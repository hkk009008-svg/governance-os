from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(
    args: list[str | Path],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.pop("GIT_INDEX_FILE", None)
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=full_env,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str) -> str:
    result = _run(["git", *args], repo)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(repo: Path, *, install_pipeline_hook: bool = False) -> None:
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".claude/hooks").mkdir(parents=True)
    (repo / "coordination/mailbox/sent").mkdir(parents=True)
    (repo / "coordination/mailbox/seen").mkdir()
    (repo / "coordination/presence").mkdir()
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    if install_pipeline_hook:
        shutil.copy2(ROOT / ".claude/settings.json", repo / ".claude/settings.json")
        shutil.copy2(
            ROOT / ".claude/hooks/update-state.sh",
            repo / ".claude/hooks/update-state.sh",
        )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")


def _configured_update_state_command(pipeline: Path) -> str | None:
    settings = json.loads(
        (pipeline / ".claude/settings.json").read_text(encoding="utf-8")
    )
    for registration in settings.get("hooks", {}).get("PostToolUse", []):
        for hook in registration.get("hooks", []):
            command = hook.get("command")
            if isinstance(command, str) and "update-state" in command:
                return command
    return None


def _post_tool_input(cwd: Path, *, subagent: bool) -> str:
    payload: dict[str, object] = {
        "session_id": "test-session",
        "transcript_path": str(cwd / "transcript.jsonl"),
        "cwd": str(cwd),
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "true"},
        "tool_response": {"stdout": "", "stderr": "", "interrupted": False},
    }
    if subagent:
        payload.update(
            {
                "agent_id": "agent-test",
                "agent_type": "readiness-bridge",
            }
        )
    return json.dumps(payload)


def test_claude_update_state_hook_anchors_pipeline_root_across_cwd(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    target = tmp_path / "target"
    _init_repo(pipeline, install_pipeline_hook=True)
    _init_repo(target)
    command = _configured_update_state_command(pipeline)
    assert command is not None, "update-state hook no longer registered in settings.json"

    result = _run(
        ["/bin/bash", "-lc", command],
        target,
        env={
            "CLAUDE_PROJECT_DIR": str(pipeline),
            "CLAUDE_SEAT": "operator2",
            "CLAUDE_CODE_SESSION_ID": "main-test",
        },
        stdin=_post_tool_input(target, subagent=False),
    )

    assert result.returncode == 0, result.stderr
    assert (pipeline / "coordination/presence/operator2-heartbeat.ts").is_file()
    assert not (target / "coordination/presence/operator2-heartbeat.ts").exists()
    assert (pipeline / "STATE.md").is_file()
    assert not (target / "STATE.md").exists()


def test_claude_update_state_hook_script_location_fallback_anchors_owner(
    tmp_path: Path,
) -> None:
    """Direct invocation with CLAUDE_PROJECT_DIR unset anchors to the script's
    own repo (BASH_SOURCE fallback), never the foreign invocation cwd."""
    pipeline = tmp_path / "pipeline"
    target = tmp_path / "target"
    _init_repo(pipeline, install_pipeline_hook=True)
    _init_repo(target)

    result = _run(
        ["/bin/bash", str(pipeline / ".claude/hooks/update-state.sh")],
        target,
        env={
            "CLAUDE_SEAT": "operator2",
            "CLAUDE_CODE_SESSION_ID": "fallback-test",
        },
        stdin=_post_tool_input(target, subagent=False),
    )

    assert result.returncode == 0, result.stderr
    assert (pipeline / "coordination/presence/operator2-heartbeat.ts").is_file()
    assert not (target / "coordination/presence/operator2-heartbeat.ts").exists()
    assert (pipeline / "STATE.md").is_file()
    assert not (target / "STATE.md").exists()


def test_claude_update_state_hook_skips_subagent_seat_mutations(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    command = _configured_update_state_command(pipeline)
    assert command is not None, "update-state hook no longer registered in settings.json"

    result = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env={
            "CLAUDE_PROJECT_DIR": str(pipeline),
            "CLAUDE_SEAT": "operator2",
            "CLAUDE_CODE_SESSION_ID": "parent-test",
        },
        stdin=_post_tool_input(pipeline, subagent=True),
    )

    assert result.returncode == 0, result.stderr
    assert not (pipeline / "coordination/presence/operator2-heartbeat.ts").exists()
