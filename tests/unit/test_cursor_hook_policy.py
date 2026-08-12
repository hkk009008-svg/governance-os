from __future__ import annotations

import json
from pathlib import Path

import pytest

import cursor_hook_policy as policy
from cursor_app_binding import AppBindingError, AppSessionBinding


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


def test_session_start_names_workspace_root_desync(tmp_path: Path) -> None:
    # No monkeypatching: the real registration path must surface a wrong-root
    # session anchor as visible context, not silently run unbound (ADR-066).
    payload = _payload("sessionStart", workspace_roots=[str(tmp_path / "elsewhere")])
    result = policy.evaluate(payload, {}, root=tmp_path)
    context = result["additional_context"]
    assert "readiness-bridge" in context
    assert "does not match the project hook root" in context
    assert "env" not in result


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
    assert result["permission"] == "deny"


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
def test_non_director_seats_write_scratch_freely_and_deny_file_tool_tree_edit(
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
    assert tree["permission"] == "deny"
    assert seat in tree["user_message"]
    assert "approved shell mutation" in tree["user_message"]
    assert scratch["permission"] == "allow"


def test_pretool_file_edits_never_return_unenforced_ask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for seat in ("director", "operator", "coordinator", None):
        _bind(monkeypatch, seat)
        for path in (tmp_path / "production.py", tmp_path / ".pytest-verify-tmp/x"):
            result = policy.evaluate(
                _payload(
                    "preToolUse",
                    tool_name="Write",
                    tool_input={"path": str(path)},
                ),
                {},
                root=tmp_path,
            )
            assert result["permission"] in {"allow", "deny"}, (seat, path, result)


def test_every_well_formed_mcp_call_asks_and_malformed_input_denies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    top_level = policy.evaluate(
        _payload(
            "beforeMCPExecution",
            tool_name="calendar_create",
            tool_input='{"title":"review"}',
            url="https://mcp.example.test",
        ),
        {},
        root=tmp_path,
    )
    child = policy.evaluate(
        _payload(
            "beforeMCPExecution",
            tool_name="calendar_create",
            tool_input={"title": "review"},
            command="mcp-server",
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    malformed = policy.evaluate(
        _payload(
            "beforeMCPExecution",
            tool_name="calendar_create",
            tool_input="not-json",
            url="https://mcp.example.test",
        ),
        {},
        root=tmp_path,
    )

    assert top_level["permission"] == "ask"
    assert "calendar_create" in top_level["user_message"]
    assert "does not grant external-effect authority" in top_level["user_message"]
    assert child["permission"] == "ask"
    assert malformed["permission"] == "deny"


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


@pytest.mark.parametrize(
    "command",
    (
        f"git update-ref refs/threeway/events {'a' * 40}",
        "git update-ref -d refs/protocol/kernel-activation",
        f"git update-ref refs/authority/cursors {'b' * 40}",
        f"git update-ref refs/heads/main {'c' * 40}",
        f"git update-ref refs/heads/cursor-seat/operator {'d' * 40}",
        f"git update-ref refs/replace/{'e' * 40} {'f' * 40}",
        "git update-ref --stdin",
        "git symbolic-ref refs/threeway/events refs/heads/feature",
        "git symbolic-ref HEAD refs/heads/main",
        f"git branch -f main {'a' * 40}",
        f"git replace {'a' * 40} {'b' * 40}",
        "git -c 'alias.pwn=!git update-ref refs/heads/main HEAD' pwn",
        "git pwn",
    ),
)
def test_protected_governance_ref_mutations_are_hard_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command: str,
) -> None:
    for seat in ("director", "operator", None):
        _bind(monkeypatch, seat)
        result = policy.evaluate(
            _payload("beforeShellExecution", command=command),
            {},
            root=tmp_path,
        )
        assert result["permission"] == "deny", (seat, command)


def test_unprotected_direct_ref_update_keeps_normal_role_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    command = f"git update-ref refs/heads/feature {'a' * 40}"
    _bind(monkeypatch, "director")
    director = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )
    _bind(monkeypatch, "operator")
    operator = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )

    assert director["permission"] == "allow"
    assert operator["permission"] == "ask"


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


@pytest.mark.parametrize(
    "command",
    (
        "git --git-dir=/tmp/other.git update-ref refs/heads/feature HEAD",
        "git --work-tree=/tmp/other checkout -- file.py",
        "git config --global alias.pwn '!touch /tmp/pwn'",
        "git config --system alias.pwn '!touch /tmp/pwn'",
        "git config --file=/tmp/other.config alias.pwn '!touch /tmp/pwn'",
        "GIT_DIR=/tmp/other.git git update-ref refs/heads/feature HEAD",
        "GIT_WORK_TREE=/tmp/other git checkout -- file.py",
    ),
)
def test_director_cannot_redirect_git_mutations_outside_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    _bind(monkeypatch, "director")

    result = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    (
        "GIT_EXTERNAL_DIFF=/tmp/side-effect git diff",
        "env PYTHONPATH=/tmp/evil python scripts/status.py",
        "env -S 'python scripts/status.py'",
    ),
)
def test_execution_bearing_environment_prefixes_are_denied(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    _bind(monkeypatch, "director")

    result = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )

    assert result["permission"] == "deny"


def test_unresolved_shell_path_expansion_is_not_auto_allowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    top = policy.evaluate(
        _payload("beforeShellExecution", command='rm "$TARGET"'),
        {"TARGET": "/tmp/outside"},
        root=tmp_path,
    )
    child = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command='rm "$TARGET"',
            subagent_id="child-1",
        ),
        {"TARGET": "/tmp/outside"},
        root=tmp_path,
    )

    assert top["permission"] == "ask"
    assert child["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    (
        "find . -delete",
        "find . -exec sh -c 'touch /tmp/pwn' ';'",
        "sort -o /tmp/pwn input",
    ),
)
def test_mutating_inspection_options_are_not_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    _bind(monkeypatch, None)
    top = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )
    child = policy.evaluate(
        _payload(
            "beforeShellExecution", command=command, subagent_id="child-1"
        ),
        {},
        root=tmp_path,
    )

    assert top["permission"] == "ask"
    assert child["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    (
        "rg --pre /tmp/evil pattern file",
        "git grep --open-files-in-pager=/tmp/evil pattern",
        "git grep -O/tmp/evil pattern",
    ),
)
def test_execution_bearing_reader_options_are_not_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    _bind(monkeypatch, None)
    top = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )
    child = policy.evaluate(
        _payload(
            "beforeShellExecution", command=command, subagent_id="child-1"
        ),
        {},
        root=tmp_path,
    )

    assert top["permission"] == "ask"
    assert child["permission"] == "deny"


def test_spoofed_inspection_executable_is_not_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Place the spoofed binary INSIDE the workspace root but outside
    # .venv/bin. The trust check keys on that relative location, so the
    # verdict is deterministic regardless of where the ambient basetemp lives
    # (a sibling under /private/var/folders is treated as ephemeral, which
    # silently flipped this to an allow under an in-repo basetemp).
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_rg = fake_bin / "rg"
    fake_rg.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_rg.chmod(0o755)
    environment = {"PATH": str(fake_bin)}
    _bind(monkeypatch, None)

    explicit = policy.evaluate(
        _payload("beforeShellExecution", command=f"{fake_rg} pattern ."),
        environment,
        root=tmp_path,
    )
    ambient = policy.evaluate(
        _payload("beforeShellExecution", command="rg pattern ."),
        environment,
        root=tmp_path,
    )
    child = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="rg pattern .",
            subagent_id="child-1",
        ),
        environment,
        root=tmp_path,
    )

    assert explicit["permission"] == "ask"
    assert ambient["permission"] == "ask"
    assert child["permission"] == "deny"


def test_git_inspection_output_cannot_escape_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload(
            "beforeShellExecution", command="git diff --output=/tmp/pwn"
        ),
        {},
        root=tmp_path,
    )

    assert result["permission"] == "deny"


@pytest.mark.parametrize("flag", ("-m", "-M", "--move"))
def test_bound_seat_cannot_implicitly_rename_its_reserved_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str
) -> None:
    _bind(monkeypatch, "director")
    result = policy.evaluate(
        _payload("beforeShellExecution", command=f"git branch {flag} feature"),
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


def test_mailbox_wrapper_allows_bound_pair_and_denies_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    command = (
        "coordination/bin/cursor-publish --to operator --kind status "
        "--subject hello --body-file .pytest-verify-tmp/body.md"
    )
    for seat in ("director", "operator", "operator2"):
        _bind(monkeypatch, seat)
        bound = policy.evaluate(
            _payload("beforeShellExecution", command=command),
            {},
            root=tmp_path,
        )
        assert bound["permission"] == "allow", seat
    _bind(monkeypatch, "coordinator")
    coordinator = policy.evaluate(
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
    assert coordinator["permission"] == "ask"
    assert "coordinator" in coordinator["user_message"]
    assert readiness["permission"] == "deny"


def test_next_review_subject_cannot_disguise_mailbox_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    command = (
        "python scripts/cursor_mailbox.py publish --to all --kind coordination "
        "--subject next-review --body-file .pytest-verify-tmp/body.md"
    )
    _bind(monkeypatch, "coordinator")
    coordinator = policy.evaluate(
        _payload("beforeShellExecution", command=command), {}, root=tmp_path
    )
    _bind(monkeypatch, "director")
    child = policy.evaluate(
        _payload(
            "beforeShellExecution", command=command, subagent_id="child-1"
        ),
        {},
        root=tmp_path,
    )

    assert coordinator["permission"] == "ask"
    assert child["permission"] == "deny"


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


def test_live_seat_spawns_advisor_but_not_impersonator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    advisor = policy.evaluate(
        _payload("subagentStart", task="Search tests", subagent_type="explore"),
        {},
        root=tmp_path,
    )
    impersonation = policy.evaluate(
        _payload(
            "subagentStart",
            task="Act as operator seat and issue GO",
            subagent_type="generalPurpose",
        ),
        {},
        root=tmp_path,
    )
    assert advisor["permission"] == "allow"
    assert impersonation["permission"] == "deny"


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
    # Forward-compatibility: IF Cursor ever tags a tool-surface payload with a
    # child marker, the mutating branches must deny even for a bound Director.
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


def test_child_marker_detection_is_robust_to_naming() -> None:
    # Any plausible child marker with a real value activates the fail-closed
    # forward-compat path; base fields and empty markers do not.
    assert policy._subagent({"subagent_type": "explore"})
    assert policy._subagent({"parent_conversation_id": "conv-parent"})
    assert policy._subagent({"is_subagent": True})
    assert not policy._subagent({"subagent_id": ""})
    assert not policy._subagent({"subagent_type": None})
    assert not policy._subagent(
        {"conversation_id": "c", "generation_id": "g", "model_id": "m"}
    )


def test_tool_surface_payloads_carry_no_subagent_discriminator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Schema pin (cursor.com/docs/hooks): the real beforeShellExecution /
    # preToolUse payloads are base fields + tool data only — no subagent
    # marker — and a child shares the parent's conversation_id. This test
    # documents that a Director-launched subagent's mutating tool call is,
    # at the tool surface, INDISTINGUISHABLE from the Director's own: it
    # resolves to the Director binding and is allowed. Containment of
    # subagents is therefore enforced at subagentStart, not here. If this
    # assertion ever flips (Cursor adds a tool-surface discriminator), the
    # forward-compat detector above already denies and this pin should be
    # promoted into a real control.
    _bind(monkeypatch, "director")
    realistic_shell = {
        "hook_event_name": "beforeShellExecution",
        "conversation_id": "conversation-1",
        "generation_id": "gen-1",
        "model": "composer-2.5",
        "cursor_version": "3.11.0",
        "workspace_roots": [str(tmp_path)],
        "command": "git add src.py",
        "cwd": str(tmp_path),
    }
    assert policy._subagent(realistic_shell) is False
    decision = policy.evaluate(realistic_shell, {}, root=tmp_path)
    assert decision["permission"] == "allow"


def test_subagent_start_is_the_enforceable_containment_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # subagentStart DOES carry subagent_type / task / parent_conversation_id,
    # so it is where impersonation is denied. Non-impersonating advisor
    # launches remain allowed (the rules permit bound seats to launch
    # advisors / capacity workers).
    _bind(monkeypatch, "director")
    impersonation = policy.evaluate(
        {
            "hook_event_name": "subagentStart",
            "conversation_id": "conversation-1",
            "subagent_type": "generalPurpose",
            "parent_conversation_id": "conversation-1",
            "task": "act as the operator seat and issue GO on the pending report",
        },
        {},
        root=tmp_path,
    )
    advisor = policy.evaluate(
        {
            "hook_event_name": "subagentStart",
            "conversation_id": "conversation-1",
            "subagent_type": "explore",
            "parent_conversation_id": "conversation-1",
            "task": "summarize how the mailbox writer stages events",
        },
        {},
        root=tmp_path,
    )
    assert impersonation["permission"] == "deny"
    assert advisor["permission"] == "allow"


def test_subagent_scratch_writes_stay_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    edit = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="Write",
            tool_input={"path": ".pytest-verify-tmp/draft.md"},
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    shell = policy.evaluate(
        _payload(
            "beforeShellExecution",
            command="tee .pytest-verify-tmp/draft.md",
            subagent_id="child-1",
        ),
        {},
        root=tmp_path,
    )
    assert edit["permission"] == "allow"
    assert shell["permission"] == "allow"


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


@pytest.mark.parametrize(
    "event",
    ("beforeShellExecution", "beforeMCPExecution", "preToolUse", "subagentStart"),
)
def test_malformed_sensitive_payload_fails_closed(
    tmp_path: Path, event: str
) -> None:
    output, status = policy.process_bytes(
        b"{",
        event_hint=event,
        environ={},
        root=tmp_path,
        registry_path=tmp_path / "registry",
    )
    assert status == 0
    assert json.loads(output)["permission"] == "deny"


def test_malformed_payload_fails_closed_without_event_hint(tmp_path: Path) -> None:
    # No hint (e.g. hooks.json omitted --event) must not weaken the gate to
    # an empty JSON object; malformed bytes deny for every event family.
    output, status = policy.process_bytes(
        b"{",
        event_hint=None,
        environ={},
        root=tmp_path,
        registry_path=tmp_path / "registry",
    )
    assert status == 0
    assert json.loads(output)["permission"] == "deny"


def test_unknown_or_missing_hook_event_denies(tmp_path: Path) -> None:
    unknown = policy.evaluate(
        _payload("afterFileEdit", tool_name="Write", tool_input={}),
        {},
        root=tmp_path,
        registry_path=tmp_path / "registry",
    )
    assert unknown["permission"] == "deny"
    assert "afterFileEdit" in unknown["user_message"]

    absent = _payload("ignored")
    absent.pop("hook_event_name")
    missing = policy.evaluate(
        absent, {}, root=tmp_path, registry_path=tmp_path / "registry"
    )
    assert missing["permission"] == "deny"


def test_pretool_unknown_tool_denies_and_dedicated_event_tools_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "director")
    # A mutating tool the policy has no rule for (a matcher regex like
    # ``Edit`` also fires for ``EditNotebook``) must deny, not slide through
    # a fallthrough allow — even for a bound Director.
    unknown = policy.evaluate(
        _payload(
            "preToolUse",
            tool_name="EditNotebook",
            tool_input={"path": "notebook.ipynb"},
        ),
        {},
        root=tmp_path,
    )
    assert unknown["permission"] == "deny"
    assert "EditNotebook" in unknown["user_message"]

    nameless = policy.evaluate(
        _payload("preToolUse", tool_input={"path": "src.py"}),
        {},
        root=tmp_path,
    )
    assert nameless["permission"] == "deny"

    for tool in ("Shell", "Task", "MCP: server tool"):
        passthrough = policy.evaluate(
            _payload("preToolUse", tool_name=tool, tool_input={}),
            {},
            root=tmp_path,
        )
        assert passthrough == {"permission": "allow"}, tool


def test_mailbox_event_grammar_accepts_cold_capacity_coordinator2() -> None:
    # coordinator2 is cold capacity but a lawful roster identity; the hook
    # grammar must stay in lockstep with the writer instead of silently
    # downgrading its committed events to a generic mutation ask.
    match = policy._MAILBOX_EVENT_NAME.fullmatch(
        "2026-08-13T00-00-00Z-coordinator2-to-all-verification-report.md"
    )
    assert match is not None
    assert match.group("sender") == "coordinator2"


@pytest.mark.parametrize("seat", ("operator", "operator2", "coordinator"))
@pytest.mark.parametrize(
    ("command", "permission"),
    (
        ("sed -i s/a/b/ production.py", "ask"),
        ("printf x>production.py", "ask"),
        ("bash coordination/bin/send-event director operator status hello", "deny"),
        ("command git push origin HEAD", "ask"),
    ),
)
def test_h1_probe_commands_never_allow_for_non_director_or_subagent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    seat: str,
    command: str,
    permission: str,
) -> None:
    _bind(monkeypatch, seat)
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
    assert top_level["permission"] == permission, command
    assert child["permission"] == "deny", command


def test_unknown_shell_asks_top_level_and_denies_subagent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bind(monkeypatch, "operator")
    command = "unusual-mutator --force production.py"
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


def test_mailbox_approval_denies_mismatched_payload_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    active = _binding("operator2")

    def resolve(
        root: Path,
        environ: object = None,
        *,
        registry_path: object = None,
        payload: dict[str, object] | None = None,
    ) -> AppSessionBinding:
        if payload is not None:
            conversation = payload.get("conversation_id")
            model = payload.get("model_id")
            if conversation is not None and conversation != active.conversation_id:
                raise AppBindingError(
                    "payload conversation_id disagrees with the registered app session"
                )
            if model is not None and model != active.model_id:
                raise AppBindingError(
                    "payload model_id disagrees with the registered app session"
                )
        return active

    monkeypatch.setattr(policy, "resolve_registered_session", resolve)
    command = (
        "coordination/bin/cursor-publish --to director --kind status "
        "--subject hello --body-file .pytest-verify-tmp/body.md"
    )
    matched = policy.evaluate(
        _payload("beforeShellExecution", command=command),
        {},
        root=tmp_path,
    )
    mismatched = policy.evaluate(
        _payload(
            "beforeShellExecution",
            conversation_id="other-conversation",
            model_id="composer-2.5",
            command=command,
        ),
        {"CURSOR_APP_CONVERSATION_ID": "conversation-1"},
        root=tmp_path,
    )
    assert matched["permission"] == "allow"
    assert mismatched["permission"] == "deny"
    assert "bound top-level" in mismatched["user_message"]
