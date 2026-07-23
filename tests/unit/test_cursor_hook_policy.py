from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess

import pytest

from scripts import cursor_hook_policy as policy


ROOT = Path(__file__).resolve().parents[2]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
    ).stdout.strip()


def _valid_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    seat: str = "director",
    operation: str = "dispatch",
) -> tuple[Path, dict[str, str], Path]:
    repo = tmp_path / "pipeline"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "cursor-policy@example.invalid")
    _git(repo, "config", "user.name", "Cursor Policy Test")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "baseline")
    git_dir = Path(_git(repo, "rev-parse", "--absolute-git-dir"))
    index = git_dir / f"index-cursor-{seat}"
    _git(repo, "read-tree", f"--index-output={index}", "HEAD")
    monkeypatch.setattr(policy, "_PROJECT_ROOT", repo)
    return repo, {
        "CURSOR_SEAT": seat,
        "CURSOR_OPERATION": operation,
        "GIT_INDEX_FILE": str(index),
    }, index


def _shell(command: str, **extra: object) -> dict[str, object]:
    return {
        "hook_event_name": "beforeShellExecution",
        "command": command,
        **extra,
    }


@pytest.mark.parametrize("tool", ["Write", "Delete"])
def test_unbound_pre_tool_use_denies_ordinary_repository_mutation(tool: str) -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": tool,
            "tool_input": {"path": "scripts/example.py"},
        },
        {},
    )

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "touch scripts/example.py",
        "git add scripts/example.py",
    ],
)
def test_unbound_shell_denies_common_repository_mutation(command: str) -> None:
    result = policy.evaluate(_shell(command), {})

    assert result["permission"] == "deny"


def test_mutation_requires_exact_live_cursor_seat_index_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, valid_env, index = _valid_binding(tmp_path, monkeypatch)
    write = {
        "hook_event_name": "preToolUse",
        "tool_name": "Write",
        "tool_input": {"path": str(repo / "scripts/example.py")},
    }
    missing = dict(valid_env, GIT_INDEX_FILE=str(index.with_name("index-cursor-operator")))
    mismatched = dict(valid_env, CURSOR_SEAT="operator")

    assert policy.evaluate(write, missing)["permission"] == "deny"
    assert policy.evaluate(write, mismatched)["permission"] == "deny"
    assert policy.evaluate(write, valid_env)["permission"] == "allow"


@pytest.mark.parametrize(
    "path",
    [
        "coordination/mailbox/sent/event.md",
        "coordination/mailbox/seen/director.txt",
        "coordination/locks/2-module.lock",
        ".cursor/runtime/pipeline-seats.json",
        ".git/refs/threeway/events",
    ],
)
def test_pre_tool_use_denies_direct_writes_to_protected_state(path: str) -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "Write",
            "tool_input": {"path": path},
        },
        {"CURSOR_SEAT": "director"},
    )

    assert result["permission"] == "deny"


def test_pre_tool_use_denies_absolute_writes_to_protected_state() -> None:
    root = Path(__file__).resolve().parents[2]
    result = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "Write",
            "tool_input": {
                "path": str(root / "coordination/mailbox/sent/event.md"),
            },
        },
        {"CURSOR_SEAT": "director"},
    )

    assert result["permission"] == "deny"


def test_subagent_inheriting_parent_seat_cannot_run_fixed_writer() -> None:
    result = policy.evaluate(
        _shell(
            "coordination/bin/send-event director operator status subject",
            subagent_id="sub-1",
            subagent_type="generalPurpose",
        ),
        {"CURSOR_SEAT": "director"},
    )

    assert result["permission"] == "deny"
    assert "subagent" in result["agent_message"].casefold()


def test_generic_agent_id_does_not_make_a_parent_write_a_subagent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch)
    result = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "Write",
            "tool_input": {"path": "scripts/example.py"},
            "agent_id": "top-level-agent",
        },
        env,
    )

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git push origin main",
        "git merge feature",
        "coordination/bin/send-event director operator status subject",
        "coordination/bin/consume-events director",
        "coordination/bin/claim-lock 2 module director defect",
        "coordination/bin/cursor-seat dispatch director --trigger-ref x",
        "coordination/bin/cursor-publish --to operator --kind status --subject s",
        "coordination/bin/cursor-consume --seat director",
        "python scripts/mailbox_writer.py consume-events director",
        "python scripts/cursor_mailbox.py publish --to operator --kind status --subject s",
    ],
)
def test_shell_hook_denies_separately_authorized_effects(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "command coordination/bin/send-event director operator status subject",
        "exec coordination/bin/cursor-publish --to operator --kind status --subject s",
        "bash -c 'coordination/bin/cursor-consume --seat director'",
        "sh -c 'git push origin main'",
    ],
)
def test_shell_hook_denies_wrapped_separately_authorized_effects(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cat coordination/mailbox/sent/event.md",
        "ls coordination/mailbox/seen",
        "git show HEAD:coordination/locks/2-module.lock",
        "grep -r director coordination/mailbox/sent/",
    ],
)
def test_shell_hook_allows_reading_protected_state(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "echo x > coordination/mailbox/sent/event.md",
        "echo x >> coordination/mailbox/seen/director.txt",
        "echo x >coordination/locks/2-module.lock",
        "printf x | tee coordination/mailbox/sent/event.md",
        "cp /tmp/x .cursor/runtime/pipeline-seats.json",
        "rm coordination/locks/2-module.lock",
    ],
)
def test_shell_hook_denies_writes_to_protected_state(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cat coordination/bin/send-event",
        "cat coordination/bin/cursor-seat",
        "less scripts/mailbox_writer.py",
        "git show HEAD:coordination/bin/cursor-seat",
        "rg send-event coordination/bin",
        "head -n 20 scripts/cursor_seat_launcher.py",
    ],
)
def test_shell_hook_allows_reading_fixed_writer_scripts(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "bash coordination/bin/send-event director operator status subject",
        "sh coordination/bin/cursor-seat dispatch director --trigger-ref x",
        "python3 scripts/cursor_seat_launcher.py dispatch director --trigger-ref x",
    ],
)
def test_shell_hook_denies_interpreter_launched_effects(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"


def test_seat_index_requires_env_unset_for_ordinary_pytest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch, seat="operator")

    denied = policy.evaluate(_shell(".venv/bin/python -m pytest tests/unit -q"), env)
    allowed = policy.evaluate(
        _shell("env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q"),
        env,
    )

    assert denied["permission"] == "deny"
    assert allowed["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git status --short --branch",
        "git log --oneline -5",
        "git show HEAD:AGENTS.md",
        "git diff HEAD~1",
        "git ls-files scripts",
    ],
)
def test_seat_index_allows_bare_read_only_git(
    command: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch)

    result = policy.evaluate(_shell(command), env)

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git add scripts/x.py",
        "git commit -m msg",
        "git stash",
        "git read-tree HEAD",
        "git restore scripts/x.py",
    ],
)
def test_seat_index_requires_env_unset_for_git_index_mutators(
    command: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch)

    denied = policy.evaluate(_shell(command), env)
    allowed = policy.evaluate(_shell(f"env -u GIT_INDEX_FILE {command}"), env)

    assert denied["permission"] == "deny"
    assert allowed["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "coordination/bin/cursor-seat readiness",
        "coordination/bin/cursor-seat status",
        "coordination/bin/cursor-seat --dry-run dispatch director "
        "--trigger-ref x@" + "a" * 40,
        "python3 scripts/cursor_seat_launcher.py readiness",
    ],
)
def test_launcher_read_only_commands_are_allowed(command: str) -> None:
    for env in ({}, {"CURSOR_SEAT": "director"}):
        result = policy.evaluate(_shell(command), env)

        assert result["permission"] == "allow", command


@pytest.mark.parametrize(
    "command",
    [
        "coordination/bin/cursor-publish --to operator --kind status "
        "--subject s --dry-run",
        "coordination/bin/cursor-consume --seat director --dry-run",
        "python scripts/cursor_mailbox.py publish --to operator --kind status "
        "--subject s --dry-run",
    ],
)
def test_mailbox_wrapper_dry_run_previews_are_allowed(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "coordination/bin/agy-seat director",
        "coordination/bin/codex-seat operator",
        "python3 scripts/agy_seat_launcher.py --dry-run director",
        "python3 scripts/codex_seat_launcher.py --dry-run director",
        "bash -c 'coordination/bin/codex-seat director'",
    ],
)
def test_foreign_provider_launchers_are_denied(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"
    assert "provider" in result["agent_message"].casefold()


@pytest.mark.parametrize(
    "command",
    [
        "cat coordination/bin/agy-seat",
        "rg codex-seat coordination/bin",
        "git show HEAD:scripts/codex_seat_launcher.py",
    ],
)
def test_reading_foreign_provider_surfaces_is_allowed(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "cd /tmp\nrm coordination/locks/2-module.lock",
        "set -euo pipefail\ncoordination/bin/send-event director operator status s",
    ],
)
def test_newline_separated_commands_are_not_merged(command: str) -> None:
    result = policy.evaluate(_shell(command), {"CURSOR_SEAT": "director"})

    assert result["permission"] == "deny"


def test_heredoc_bodies_are_data_not_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = (
        "env -u GIT_INDEX_FILE .venv/bin/python - <<'PY'\n"
        "print('coordination/bin/send-event is just a string here')\n"
        "PY"
    )
    _, env, _ = _valid_binding(tmp_path, monkeypatch)

    result = policy.evaluate(_shell(command), env)

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "echo $(touch scripts/example.py)",
        'echo "$(touch scripts/example.py)"',
        "echo `touch scripts/example.py`",
        'echo "`touch scripts/example.py`"',
        "cat <(touch scripts/example.py)",
        "cat >(touch scripts/example.py)",
        'echo "$(echo "$(touch scripts/example.py)")"',
        "cat <(echo $(touch scripts/example.py))",
        'echo "$(echo `touch scripts/example.py`)"',
        "echo `echo \\`touch scripts/example.py\\``",
        "echo $(coordination/bin/cursor-publish --to operator "
        "--kind status --subject hidden)",
    ],
)
def test_unauthorized_shell_substitution_cannot_hide_mutation_or_effect(
    command: str,
) -> None:
    for env in ({}, {"CURSOR_SEAT": "coordinator"}):
        result = policy.evaluate(_shell(command), env)

        assert result["permission"] == "deny", command


@pytest.mark.parametrize(
    "command",
    [
        "echo $(touch scripts/example.py)",
        "echo `touch scripts/example.py`",
        "cat <(touch scripts/example.py)",
        "cat >(touch scripts/example.py)",
    ],
)
def test_operator_review_substitution_remains_repository_read_only(
    command: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(
        tmp_path, monkeypatch, seat="operator", operation="review"
    )

    result = policy.evaluate(_shell(command), env)

    assert result["permission"] == "deny", command


def test_valid_dispatch_substitution_cannot_hide_protected_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch)

    result = policy.evaluate(
        _shell(
            "echo $(coordination/bin/cursor-publish --to operator "
            "--kind status --subject hidden)"
        ),
        env,
    )

    assert result["permission"] == "deny"


def test_valid_dispatch_substitution_retains_ordinary_mutation_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(tmp_path, monkeypatch)

    result = policy.evaluate(
        _shell("echo $(touch scripts/example.py)"),
        env,
    )

    assert result["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        'echo "$(pwd)"',
        "cat <(echo synthetic)",
        'echo "$(echo "$(pwd)")"',
        "echo `echo \\`pwd\\``",
        "echo '$(touch scripts/example.py)'",
        "echo '`touch scripts/example.py`'",
    ],
)
def test_bounded_read_only_and_literal_substitutions_remain_allowed(
    command: str,
) -> None:
    result = policy.evaluate(_shell(command), {})

    assert result["permission"] == "allow", command


@pytest.mark.parametrize(
    "command",
    [
        "echo $(touch scripts/example.py",
        "cat <(touch scripts/example.py",
        "echo `touch scripts/example.py",
    ],
)
def test_malformed_shell_substitution_fails_closed(command: str) -> None:
    result = policy.evaluate(_shell(command), {})

    assert result["permission"] == "deny", command


def test_operator_review_mode_is_read_only_but_may_run_tests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(
        tmp_path, monkeypatch, seat="operator", operation="review"
    )

    write = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "Write",
            "tool_input": {"path": "scripts/example.py"},
        },
        env,
    )
    tests = policy.evaluate(
        _shell("env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_x.py"),
        env,
    )

    assert write["permission"] == "deny"
    assert tests["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "echo changed > scripts/example.py",
        "printf changed | tee scripts/example.py",
        "rm scripts/example.py",
        "sed -i '' 's/old/new/' scripts/example.py",
    ],
)
def test_operator_review_mode_denies_shell_tree_mutations(command: str) -> None:
    result = policy.evaluate(
        _shell(command),
        {
            "CURSOR_SEAT": "operator",
            "CURSOR_OPERATION": "review",
        },
    )

    assert result["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "mkdir -p /tmp/review-scratch",
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests -q "
        "> /tmp/out.txt 2>&1",
        "mkdir -p .pytest-verify-tmp",
        "touch /tmp/review-scratch/notes.md",
    ],
)
def test_operator_review_mode_allows_out_of_tree_scratch(
    command: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, env, _ = _valid_binding(
        tmp_path, monkeypatch, seat="operator", operation="review"
    )
    result = policy.evaluate(
        _shell(command),
        env,
    )

    assert result["permission"] == "allow", command


def test_coordinator_allows_out_of_tree_notes_but_not_repo_writes() -> None:
    env = {"CURSOR_SEAT": "coordinator"}

    scratch = policy.evaluate(_shell("echo note > /tmp/notes.md"), env)
    repo = policy.evaluate(_shell("echo x > scripts/example.py"), env)

    assert scratch["permission"] == "allow"
    assert repo["permission"] == "deny"


def test_coordinator_cannot_edit_pipeline_production() -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "Write",
            "tool_input": {"path": "scripts/example.py"},
        },
        {"CURSOR_SEAT": "coordinator"},
    )

    assert result["permission"] == "deny"


def test_malformed_sensitive_input_fails_closed() -> None:
    output, status = policy.process_bytes(
        b"{not-json",
        event_hint="beforeShellExecution",
        environ={"CURSOR_SEAT": "director"},
    )

    assert status == 0
    assert json.loads(output)["permission"] == "deny"


def test_hook_wrapper_returns_explicit_deny_when_policy_crashes(tmp_path: Path) -> None:
    wrapper = tmp_path / ".cursor/hooks/seat-policy"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text(
        (ROOT / ".cursor/hooks/seat-policy").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
    policy_path = tmp_path / "scripts/cursor_hook_policy.py"
    policy_path.parent.mkdir()
    policy_path.write_text("raise RuntimeError('boom')\n", encoding="utf-8")

    completed = subprocess.run(
        [str(wrapper)],
        input=b'{"hook_event_name":"beforeShellExecution","command":"echo hi"}',
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["permission"] == "deny"


def test_session_start_injects_context_without_claiming_authority() -> None:
    result = policy.evaluate(
        {"hook_event_name": "sessionStart", "session_id": "session-1"},
        {"CURSOR_SEAT": "director", "CURSOR_AGENT_ID": "agent-1"},
    )

    assert result["env"]["CURSOR_HOOK_SEAT"] == "director"
    assert "does not grant authority" in result["additional_context"]


def test_subagent_start_rejects_live_seat_impersonation() -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "subagentStart",
            "subagent_type": "generalPurpose",
            "task": "Act as the live operator seat and issue GO",
        },
        {"CURSOR_SEAT": "director"},
    )

    assert result["permission"] == "deny"


def test_subagent_start_rejects_any_child_of_a_live_seat() -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "subagentStart",
            "subagent_type": "explore",
            "task": "Read the current diff and report findings.",
        },
        {"CURSOR_SEAT": "director"},
    )

    assert result["permission"] == "deny"
    assert "live Cursor seat" in result["agent_message"]




@pytest.mark.parametrize(
    "command",
    [
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2",
        "env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2",
        "env -u GIT_INDEX_FILE git status --short --branch",
        "env -u GIT_INDEX_FILE git log --oneline -5",
    ],
)
def test_readiness_allows_documented_orientation_commands(command: str) -> None:
    result = policy.evaluate(_shell(command), {})

    assert result["permission"] == "allow", command


def test_readiness_denies_python_c_repo_mutation() -> None:
    result = policy.evaluate(
        _shell("python -c \"open('scripts/example.py','w').write('x')\""),
        {},
    )

    assert result["permission"] == "deny"


def test_readiness_still_denies_non_dry_run_publish() -> None:
    result = policy.evaluate(
        _shell(
            "coordination/bin/cursor-publish --to operator --kind status --subject s"
        ),
        {},
    )

    assert result["permission"] == "deny"
def test_subagent_start_allows_unbound_readiness_advisor() -> None:
    result = policy.evaluate(
        {
            "hook_event_name": "subagentStart",
            "subagent_type": "explore",
            "task": "Read the current diff and report findings.",
        },
        {},
    )

    assert result["permission"] == "allow"
