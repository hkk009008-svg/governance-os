"""Regressions for the .codex twin of the 2026-07-10 hook-isolation defects.

The Claude copy's fixes (CLAUDE-HOOK-ROOT-001 cwd anchoring,
CLAUDE-HOOK-SUBAGENT-002 inherited seat authority) were folded into
.codex/hooks/update-state.sh on 2026-07-12 by direct user instruction
("fold twin hook fix"). Same defect classes, direct-invocation form
(the Codex config layer resolves script paths itself, so these tests
invoke the script path explicitly rather than parsing hooks.json).
"""

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


def _init_repo(repo: Path, *, install_codex_hook: bool = False) -> None:
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".codex/hooks").mkdir(parents=True)
    (repo / "coordination/mailbox/sent").mkdir(parents=True)
    (repo / "coordination/mailbox/seen").mkdir()
    (repo / "coordination/presence").mkdir()
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    if install_codex_hook:
        shutil.copy2(
            ROOT / ".codex/hooks/update-state.sh",
            repo / ".codex/hooks/update-state.sh",
        )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")


def _post_tool_input(cwd: Path, *, subagent: bool) -> str:
    payload: dict[str, object] = {
        "session_id": "test-session",
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


def test_codex_update_state_hook_anchors_script_root_across_cwd(
    tmp_path: Path,
) -> None:
    """Invoking the owner repo's hook from a foreign repo's cwd mutates the
    OWNER repo only (script-location anchoring), never the foreign repo."""
    owner = tmp_path / "owner"
    target = tmp_path / "target"
    _init_repo(owner, install_codex_hook=True)
    _init_repo(target)

    result = _run(
        ["/bin/bash", str(owner / ".codex/hooks/update-state.sh")],
        target,
        env={"CODEX_SEAT": "operator2", "CODEX_SESSION_ID": "main-test"},
        stdin=_post_tool_input(target, subagent=False),
    )

    assert result.returncode == 0, result.stderr
    assert (owner / "coordination/presence/operator2-heartbeat.ts").is_file()
    assert not (target / "coordination/presence/operator2-heartbeat.ts").exists()
    assert (owner / "STATE.md").is_file()
    assert not (target / "STATE.md").exists()


def test_codex_update_state_hook_skips_subagent_seat_mutations(
    tmp_path: Path,
) -> None:
    """A subagent-shaped stdin payload (top-level agent_id/agent_type) gets
    zero mutations even with CODEX_SEAT inherited from the parent env."""
    owner = tmp_path / "owner"
    _init_repo(owner, install_codex_hook=True)

    result = _run(
        ["/bin/bash", str(owner / ".codex/hooks/update-state.sh")],
        owner,
        env={"CODEX_SEAT": "operator2", "CODEX_SESSION_ID": "parent-test"},
        stdin=_post_tool_input(owner, subagent=True),
    )

    assert result.returncode == 0, result.stderr
    assert not (owner / "coordination/presence/operator2-heartbeat.ts").exists()
    assert not (owner / "STATE.md").exists()
