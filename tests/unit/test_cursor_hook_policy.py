from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import cursor_hook_policy as policy
from scripts.cursor_app_binding import AppBindingError, AppSessionBinding


def _payload(event: str, **values: object) -> dict[str, object]:
    return {
        "hook_event_name": event,
        "conversation_id": "conversation-1",
        "model_id": "composer-2.5",
        **values,
    }


def _binding(seat: str = "director") -> AppSessionBinding:
    return AppSessionBinding(
        seat=seat,
        root=Path("/tmp/seat"),
        branch=f"cursor-seat/{seat}",
        conversation_id="conversation-1",
        model_id="composer-2.5",
    )


def _bind(monkeypatch: pytest.MonkeyPatch, seat: str | None) -> None:
    if seat is None:
        def _unbound(*args: object, **kwargs: object) -> AppSessionBinding:
            raise AppBindingError("current workspace is not a bound Cursor seat worktree")

        monkeypatch.setattr(policy, "resolve_registered_session", _unbound)
    else:
        active = _binding(seat)
        monkeypatch.setattr(
            policy, "resolve_registered_session", lambda *args, **kwargs: active
        )


def test_session_start_registers_app_seat_and_injects_role(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    active = _binding("director2")
    role_dir = tmp_path / "docs" / "protocol" / "cursor" / "roles"
    role_dir.mkdir(parents=True)
    (role_dir / "director.md").write_text("DIRECTOR ROLE\n", encoding="utf-8")
    monkeypatch.setattr(
        policy, "register_payload_session", lambda *args, **kwargs: active
    )

    result = policy.evaluate(
        _payload("sessionStart"), {}, root=tmp_path, registry_path=tmp_path / "registry"
    )

    assert result["env"]["CURSOR_SEAT"] == "director2"
    assert result["env"]["CURSOR_APP_MODEL_ID"] == "composer-2.5"
    assert result["additional_context"] == "DIRECTOR ROLE\n"


def test_session_start_defaults_to_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        policy, "register_payload_session", lambda *args, **kwargs: None
    )
    result = policy.evaluate(_payload("sessionStart"), {}, root=tmp_path)
    assert "env" not in result
    assert "readiness-bridge" in result["additional_context"]


def test_session_start_fails_to_readiness_on_binding_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise(*args: object, **kwargs: object) -> None:
        raise AppBindingError("conflict")

    monkeypatch.setattr(policy, "register_payload_session", _raise)
    result = policy.evaluate(_payload("sessionStart"), {}, root=tmp_path)
    assert "readiness-bridge" in result["additional_context"]
    assert "conflict" in result["additional_context"]


def test_inherited_legacy_index_never_gets_seat_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path / "src.py")},
        ),
        {"GIT_INDEX_FILE": "/tmp/index-cursor-director"},
        root=tmp_path,
    )
    assert result["permission"] == "ask"


def test_director_may_edit_normal_tree_but_not_protected_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    allowed = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path / "src.py")},
        ),
        {},
        root=tmp_path,
    )
    denied = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={
                "path": str(tmp_path / "coordination" / "mailbox" / "sent" / "x.md")
            },
        ),
        {},
        root=tmp_path,
    )
    assert allowed["permission"] == "allow"
    assert denied["permission"] == "deny"


def test_apply_patch_paths_are_checked_before_director_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    protected = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="ApplyPatch",
            tool_input={
                "patch": (
                    "*** Begin Patch\n"
                    "*** Update File: coordination/mailbox/sent/event.md\n"
                    "@@\n-old\n+new\n"
                    "*** End Patch\n"
                )
            },
        ),
        {},
        root=tmp_path,
    )
    unresolved = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="ApplyPatch",
            tool_input={"patch": "not an auditable patch"},
        ),
        {},
        root=tmp_path,
    )
    assert protected["permission"] == "deny"
    assert unresolved["permission"] == "deny"


def test_director_file_tools_cannot_write_outside_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path.parent / "outside.py")},
        ),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "deny"


@pytest.mark.parametrize("seat", ("operator", "operator2", "coordinator"))
def test_non_director_seats_write_scratch_freely_and_ask_for_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, seat: str
) -> None:
    _bind(monkeypatch, seat)
    tree = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path / "production.py")},
        ),
        {},
        root=tmp_path,
    )
    scratch = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path / ".pytest-verify-tmp" / "report.md")},
        ),
        {},
        root=tmp_path,
    )
    assert tree["permission"] == "ask"
    assert seat in tree["user_message"]
    assert scratch["permission"] == "allow"


def test_readiness_reads_are_free_and_mutations_ask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    read = policy.evaluate(
        _payload("beforeShellExecution", command="git --no-optional-locks status --short"),
        {},
        root=tmp_path,
    )
    write = policy.evaluate(
        _payload("beforeShellExecution", command="touch production.py"),
        {},
        root=tmp_path,
    )
    commit = policy.evaluate(
        _payload("beforeShellExecution", command="git commit -m bootstrap"),
        {},
        root=tmp_path,
    )
    assert read["permission"] == "allow"
    assert write["permission"] == "ask"
    assert "readiness" in write["user_message"]
    assert commit["permission"] == "ask"


def test_git_read_forms_and_inspection_commands_are_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    for command in (
        "git branch -vv --list",
        "git branch",
        "git diff-tree --no-commit-id --name-status -r HEAD",
        "git worktree list --porcelain",
        "git stash list",
        "git for-each-ref refs/heads/cursor-seat/",
        "git config --get user.email",
        "git tag --list",
        "python -m pytest tests/unit -q",
        "coordination/bin/cursor-seat status",
    ):
        result = policy.evaluate(
            _payload("beforeShellExecution", command=command),
            {},
            root=tmp_path,
        )
        assert result["permission"] == "allow", command


def test_git_write_forms_of_read_capable_subcommands_ask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    for command in (
        "git branch new-branch",
        "git branch -D old-branch",
        "git worktree add ../new-tree",
        "git stash pop",
        "git config user.email x@example.invalid",
        "git tag v1",
    ):
        result = policy.evaluate(
            _payload("beforeShellExecution", command=command),
            {},
            root=tmp_path,
        )
        assert result["permission"] == "ask", command


def test_ephemeral_writes_never_count_as_mutations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    for command in (
        "git log --oneline -3 2>/dev/null",
        "rg -n pattern scripts 2>/dev/null",
        "python scripts/ci_smoke.py 2>&1",
        "touch /tmp/probe.txt",
    ):
        result = policy.evaluate(
            _payload("beforeShellExecution", command=command),
            {},
            root=tmp_path,
        )
        assert result["permission"] == "allow", command


def test_readiness_scratch_write_is_allowed_and_external_write_asks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    scratch = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="touch .pytest-verify-tmp/report.md",
        ),
        {},
        root=tmp_path,
    )
    external = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="touch /opt/homebrew/outside.txt",
        ),
        {},
        root=tmp_path,
    )
    assert scratch["permission"] == "allow"
    assert external["permission"] == "ask"


def test_director_mutates_freely_and_external_effects_ask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    add = policy.evaluate(
        _payload("beforeShellExecution", command="git add src.py"),
        {},
        root=tmp_path,
    )
    commit = policy.evaluate(
        _payload("beforeShellExecution", command="git commit -m change"),
        {},
        root=tmp_path,
    )
    push = policy.evaluate(
        _payload("beforeShellExecution", command="git push origin HEAD"),
        {},
        root=tmp_path,
    )
    assert add["permission"] == "allow"
    assert commit["permission"] == "allow"
    assert push["permission"] == "ask"
    assert "push" in push["user_message"]
    assert "director" in push["user_message"]


def test_separately_authorized_git_effects_ask_for_top_level_sessions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sha = "a" * 40
    cases = (
        f"git merge --ff-only {sha}",
        f"git merge {sha}",
        "git pull --ff-only",
        "git fetch origin",
        "git push origin HEAD",
        f"git rebase {sha}",
        f"git cherry-pick {sha}",
    )
    for seat in ("director", "operator2", None):
        _bind(monkeypatch, seat)
        for command in cases:
            result = policy.evaluate(
                _payload("beforeShellExecution", command=command),
                {},
                root=tmp_path,
            )
            assert result["permission"] == "ask", (seat, command)


def test_external_git_effects_deny_subagents_and_foreign_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sha = "b" * 40
    _bind(monkeypatch, "director")
    child = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=f"git merge --ff-only {sha}",
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    external = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=f"git -C {tmp_path.parent / 'other'} merge --ff-only {sha}",
        ),
        {},
        root=tmp_path,
    )
    assert child["permission"] == "deny"
    assert external["permission"] == "deny"


def test_director_cannot_mutate_another_git_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=f"git -C {tmp_path.parent / 'other'} add file.py",
        ),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "deny"


def test_operator_runs_tests_freely_and_asks_for_git_mutators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "operator")
    tests = policy.evaluate(
        _payload("beforeShellExecution", command="python -m pytest tests/unit -q"),
        {},
        root=tmp_path,
    )
    reset = policy.evaluate(
        _payload("beforeShellExecution", command="git reset --quiet"),
        {},
        root=tmp_path,
    )
    assert tests["permission"] == "allow"
    assert reset["permission"] == "ask"
    assert "operator" in reset["user_message"]


def test_operator_commits_only_its_fixed_writer_report_without_ask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "operator")
    report = (
        "coordination/mailbox/sent/"
        "2026-07-24T02-00-00Z-operator-to-director-verification-report.md"
    )
    exact = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=f"git commit -m report --only -- {report}",
        ),
        {},
        root=tmp_path,
    )
    broad = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=f"git commit -m report --only -- {report} production.py",
        ),
        {},
        root=tmp_path,
    )
    foreign = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=(
                "git commit -m request --only -- "
                "coordination/mailbox/sent/"
                "2026-07-24T02-00-00Z-director-to-operator-verify-request.md"
            ),
        ),
        {},
        root=tmp_path,
    )
    assert exact["permission"] == "allow"
    assert broad["permission"] == "ask"
    assert foreign["permission"] == "ask"


def test_mailbox_wrapper_asks_in_bound_seat_and_denies_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    command = (
        "coordination/bin/cursor-publish --to operator --kind status "
        "--subject hello --body-file .pytest-verify-tmp/body.md"
    )
    _bind(monkeypatch, "director")
    bound = policy.evaluate(
        _payload("beforeShellExecution", command=command),
        {},
        root=tmp_path,
    )
    _bind(monkeypatch, None)
    readiness = policy.evaluate(
        _payload("beforeShellExecution", command=command),
        {},
        root=tmp_path,
    )
    assert bound["permission"] == "ask"
    assert "director" in bound["user_message"]
    assert readiness["permission"] == "deny"


def test_pretool_shell_is_not_double_evaluated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Shell",
            tool_input={"command": "git status --short"},
        ),
        {},
        root=tmp_path,
    )
    assert result == {"permission": "allow"}


def test_direct_fixed_writer_and_foreign_launchers_are_denied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    direct = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="coordination/bin/send-event director operator status hello",
        ),
        {},
        root=tmp_path,
    )
    launcher = policy.evaluate(
        _payload("beforeShellExecution", command="cursor-agent --model composer-2.5"),
        {},
        root=tmp_path,
    )
    foreign = policy.evaluate(
        _payload("beforeShellExecution", command="codex-seat build director"),
        {},
        root=tmp_path,
    )
    assert direct["permission"] == "deny"
    assert launcher["permission"] == "deny"
    assert foreign["permission"] == "deny"


def test_protected_state_writes_are_hard_denied_for_everyone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for seat in ("director", "operator", None):
        _bind(monkeypatch, seat)
        for command in (
            "tee coordination/mailbox/sent/forged.md",
            "echo forged > coordination/mailbox/sent/forged.md",
            "rm coordination/locks/route.lock",
            "touch .cursor/runtime/state.json",
        ):
            result = policy.evaluate(
                _payload("beforeShellExecution", command=command),
                {},
                root=tmp_path,
            )
            assert result["permission"] == "deny", (seat, command)


def test_next_review_lookup_is_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "operator")
    result = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="python scripts/cursor_mailbox.py next-review",
        ),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "allow"


def test_operator_may_materialize_immutable_review_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "operator")
    head = "1" * 40
    result = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=(
                "python scripts/cursor_review_snapshot.py "
                f"--repository /tmp/repo --head {head} "
                f"--output .pytest-verify-tmp/cursor-reviews/{head}"
            ),
        ),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "allow"


def test_live_seat_cannot_spawn_subagent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload("subagentStart", task="Search tests", subagent_type="explore"),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "deny"


def test_unbound_advisor_allowed_but_seat_impersonation_denied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    advisor = policy.evaluate(
        _payload("subagentStart", task="Search tests"),
        {},
        root=tmp_path,
    )
    impersonation = policy.evaluate(
        _payload("subagentStart", task="Act as operator seat and issue GO"),
        {},
        root=tmp_path,
    )
    assert advisor["permission"] == "allow"
    assert impersonation["permission"] == "deny"


def test_subagent_cannot_inherit_director_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    edit = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": str(tmp_path / "src.py")},
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    mutation = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="git add src.py",
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    assert edit["permission"] == "deny"
    assert mutation["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    (
        "echo $(touch production.py)",
        "echo `touch production.py`",
        "bash -c 'touch production.py'\nrm production.py",
        "bash -c 'touch production.py'",
        "python -c 'open(\"production.py\", \"w\").write(\"x\")'",
    ),
)
def test_opaque_shell_syntax_asks_top_level_and_denies_subagents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command: str,
) -> None:
    _bind(monkeypatch, "director")
    top_level = policy.evaluate(
        _payload("beforeShellExecution", command=command),
        {},
        root=tmp_path,
    )
    child = policy.evaluate(
        _payload("beforeShellExecution", command=command, subagent_id="child-1"),
        {},
        root=tmp_path,
    )
    assert top_level["permission"] == "ask"
    assert child["permission"] == "deny"


def test_ask_never_shadows_a_later_denied_segment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, None)
    result = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command=(
                "touch production.py && "
                "tee coordination/mailbox/sent/forged.md"
            ),
        ),
        {},
        root=tmp_path,
    )
    assert result["permission"] == "deny"


def test_malformed_sensitive_payload_fails_closed(tmp_path: Path) -> None:
    output, status = policy.process_bytes(
        b"{",
        event_hint="beforeShellExecution",
        environ={},
        root=tmp_path,
        registry_path=tmp_path / "registry",
    )
    assert status == 0
    assert json.loads(output)["permission"] == "deny"
