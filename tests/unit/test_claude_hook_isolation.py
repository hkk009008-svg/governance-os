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
        shutil.copy2(
            ROOT / ".claude/hooks/guard-git-index.sh",
            repo / ".claude/hooks/guard-git-index.sh",
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


def _configured_guard_command(pipeline: Path) -> tuple[str, str] | None:
    settings = json.loads(
        (pipeline / ".claude/settings.json").read_text(encoding="utf-8")
    )
    for registration in settings.get("hooks", {}).get("PreToolUse", []):
        for hook in registration.get("hooks", []):
            command = hook.get("command")
            if isinstance(command, str) and "guard-git-index" in command:
                return registration.get("matcher", ""), command
    return None


def test_claude_settings_do_not_enable_codex_provider_bridge(repo_root: Path) -> None:
    settings = json.loads(
        (repo_root / ".claude/settings.json").read_text(encoding="utf-8")
    )

    assert "codex@openai-codex" not in settings.get("enabledPlugins", {})


def _seat_index(repo: Path, seat: str, *, provider: str = "claude") -> Path:
    index = repo / ".git" / f"index-{provider}-{seat}"
    _git(repo, "read-tree", f"--index-output={index}", "HEAD")
    return index


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


def _pre_tool_input(cwd: Path, tool: str, command: str = "") -> str:
    return json.dumps(
        {
            "session_id": "test-session",
            "transcript_path": str(cwd / "transcript.jsonl"),
            "cwd": str(cwd),
            "hook_event_name": "PreToolUse",
            "tool_name": tool,
            "tool_input": {"command": command} if tool == "Bash" else {},
        }
    )


def test_claude_update_state_hook_anchors_pipeline_root_across_cwd(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    target = tmp_path / "target"
    _init_repo(pipeline, install_pipeline_hook=True)
    _init_repo(target)
    command = _configured_update_state_command(pipeline)
    assert command is not None, "update-state hook no longer registered in settings.json"
    index = _seat_index(pipeline, "operator2")

    result = _run(
        ["/bin/bash", "-lc", command],
        target,
        env={
            "CLAUDE_PROJECT_DIR": str(pipeline),
            "CLAUDE_SEAT": "operator2",
            "GIT_INDEX_FILE": str(index),
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
    index = _seat_index(pipeline, "operator2")

    result = _run(
        ["/bin/bash", str(pipeline / ".claude/hooks/update-state.sh")],
        target,
        env={
            "CLAUDE_SEAT": "operator2",
            "GIT_INDEX_FILE": str(index),
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
    index = _seat_index(pipeline, "operator2")

    result = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env={
            "CLAUDE_PROJECT_DIR": str(pipeline),
            "CLAUDE_SEAT": "operator2",
            "GIT_INDEX_FILE": str(index),
        },
        stdin=_post_tool_input(pipeline, subagent=True),
    )

    assert result.returncode == 0, result.stderr
    assert not (pipeline / "coordination/presence/operator2-heartbeat.ts").exists()


def test_claude_pretool_guard_requires_exact_binding_for_write_and_edit(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    configured = _configured_guard_command(pipeline)
    assert configured is not None
    matcher, command = configured
    assert matcher == "Bash|Write|Edit"
    foreign = _seat_index(pipeline, "director", provider="codex")

    for tool in ("Write", "Edit"):
        unpinned = _run(
            ["/bin/bash", "-lc", command],
            pipeline,
            env={"CLAUDE_PROJECT_DIR": str(pipeline)},
            stdin=_pre_tool_input(pipeline, tool),
        )
        foreign_bound = _run(
            ["/bin/bash", "-lc", command],
            pipeline,
            env={
                "CLAUDE_PROJECT_DIR": str(pipeline),
                "CLAUDE_SEAT": "director",
                "GIT_INDEX_FILE": str(foreign),
            },
            stdin=_pre_tool_input(pipeline, tool),
        )
        assert unpinned.returncode != 0
        assert foreign_bound.returncode != 0


def test_claude_pretool_guard_allows_read_only_bash_but_denies_mutation_when_invalid(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    configured = _configured_guard_command(pipeline)
    assert configured is not None
    _, command = configured

    read_only = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env={"CLAUDE_PROJECT_DIR": str(pipeline)},
        stdin=_pre_tool_input(
            pipeline,
            "Bash",
            "env -u GIT_INDEX_FILE git --no-optional-locks status --short",
        ),
    )
    mutation = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env={"CLAUDE_PROJECT_DIR": str(pipeline)},
        stdin=_pre_tool_input(pipeline, "Bash", "touch forbidden.txt"),
    )

    assert read_only.returncode == 0, read_only.stderr
    assert mutation.returncode != 0


def test_claude_pretool_guard_requires_scrubbed_index_for_invalid_git_inspection(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    configured = _configured_guard_command(pipeline)
    assert configured is not None
    _, command = configured
    foreign = _seat_index(pipeline, "director", provider="codex")
    env = {
        "CLAUDE_PROJECT_DIR": str(pipeline),
        "CLAUDE_SEAT": "director",
        "GIT_INDEX_FILE": str(foreign),
    }

    inherited = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(
            pipeline, "Bash", "git --no-optional-locks status --short"
        ),
    )
    scrubbed = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(
            pipeline,
            "Bash",
            "env -u GIT_INDEX_FILE git --no-optional-locks status --short",
        ),
    )

    assert inherited.returncode != 0
    assert scrubbed.returncode == 0, scrubbed.stderr


def test_claude_pretool_guard_allows_mutation_only_for_valid_exact_binding(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    configured = _configured_guard_command(pipeline)
    assert configured is not None
    _, command = configured
    index = _seat_index(pipeline, "director")
    env = {
        "CLAUDE_PROJECT_DIR": str(pipeline),
        "CLAUDE_SEAT": "director",
        "GIT_INDEX_FILE": str(index),
    }

    write = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(pipeline, "Write"),
    )
    shell_mutation = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(pipeline, "Bash", "touch allowed.txt"),
    )
    bare_git_mutation = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(pipeline, "Bash", "git add allowed.txt"),
    )
    scrubbed_git_mutation = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env=env,
        stdin=_pre_tool_input(
            pipeline, "Bash", "env -u GIT_INDEX_FILE git add allowed.txt"
        ),
    )

    assert write.returncode == 0, write.stderr
    assert shell_mutation.returncode == 0, shell_mutation.stderr
    assert bare_git_mutation.returncode != 0
    assert scrubbed_git_mutation.returncode == 0, scrubbed_git_mutation.stderr


def test_claude_pretool_guard_rejects_corrupt_exact_path_binding(
    tmp_path: Path,
) -> None:
    pipeline = tmp_path / "pipeline"
    _init_repo(pipeline, install_pipeline_hook=True)
    configured = _configured_guard_command(pipeline)
    assert configured is not None
    _, command = configured
    index = pipeline / ".git/index-claude-director"
    index.write_bytes(b"not a git index")

    result = _run(
        ["/bin/bash", "-lc", command],
        pipeline,
        env={
            "CLAUDE_PROJECT_DIR": str(pipeline),
            "CLAUDE_SEAT": "director",
            "GIT_INDEX_FILE": str(index),
        },
        stdin=_pre_tool_input(pipeline, "Write"),
    )

    assert result.returncode != 0


def test_claude_posttool_hook_never_mutates_foreign_or_mismatched_indexes(
    tmp_path: Path,
) -> None:
    cases = (
        ("codex", "director", "director"),
        ("cursor", "director", "director"),
        ("agy", "director", "director"),
        ("claude", "operator", "director"),
    )
    for provider, index_seat, claimed_seat in cases:
        pipeline = tmp_path / f"pipeline-{provider}-{index_seat}"
        _init_repo(pipeline, install_pipeline_hook=True)
        command = _configured_update_state_command(pipeline)
        assert command is not None
        index = _seat_index(pipeline, index_seat, provider=provider)
        before = index.read_bytes()

        result = _run(
            ["/bin/bash", "-lc", command],
            pipeline,
            env={
                "CLAUDE_PROJECT_DIR": str(pipeline),
                "CLAUDE_SEAT": claimed_seat,
                "GIT_INDEX_FILE": str(index),
            },
            stdin=_post_tool_input(pipeline, subagent=False),
        )

        assert result.returncode == 0, result.stderr
        assert index.read_bytes() == before
        assert not (pipeline / "STATE.md").exists()
        assert not (
            pipeline / f"coordination/presence/{claimed_seat}-heartbeat.ts"
        ).exists()
        assert not list((pipeline / ".claude/hooks").glob(".last-index-sync-*"))
