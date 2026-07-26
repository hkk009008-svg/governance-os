#!/usr/bin/env python3
"""Check whether a review harness can actually do work before dispatching it.

Every harness failure observed on 2026-07-26 exited 0 and produced silence or a
usage dump: Codex blocked forever reading stdin, Cursor degraded to an unbound
readiness posture in the wrong workspace, AGY auto-denied a tool permission it
could not prompt for. None of them said "I did nothing" in a way a caller could
branch on. Protocol failures behave the opposite way — the mailbox writer, the
compact-pair validator and the placeholder gate all refuse loudly and name the
defect — so the expensive knowledge in this repository is the invocation half,
and prose lost it twice in one session.

Each check reads live state instead of restating it: Cursor's verdicts come from
`cursor_hook_policy.py` itself, AGY's grants from the CLI's own settings file,
and Codex's ambient authority from the project config the launch would inherit.
A copy of an external interface rots exactly the way the launcher flags did.

`--live` additionally spends one trivial tool-using prompt per harness and
requires a positive artifact — the repository HEAD echoed back — because exit 0
is not evidence that anything ran.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HARNESSES = ("codex", "agy", "cursor")
AGY_SETTINGS = Path("~/.gemini/antigravity-cli/settings.json")
CURSOR_REGISTRY = Path("~/.cursor/pipeline-app-seats.json")
RUNBOOK = "docs/protocol/threeway/HEADLESS-REVIEW.md"

# What a review actually runs. AGY grants are matched against these because a
# harness that can read files but not run pytest still cannot produce evidence.
REVIEW_COMMANDS = (
    "git diff",
    ".venv/bin/python -m pytest",
    "coordination/bin/send-event",
    "git commit",
)
# Ambient runtime authority a Codex launch would inherit from the project
# config. `tests/unit/test_protocol_prompt_sync.py` forbids these keys so a
# checked-in file cannot grant approvals-off with full disk access; a preflight
# that ignored them would call a dangerous launch ready.
CODEX_AMBIENT_KEYS = ("approval_policy", "sandbox_mode", "features")


@dataclass(frozen=True)
class Result:
    harness: str
    ok: bool
    detail: str
    remedy: str = ""


def _binary(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def check_codex(root: Path) -> list[Result]:
    """Codex is ready when the binary exists and no ambient authority is implied."""
    results: list[Result] = []
    binary = _binary("codex")
    results.append(
        Result("codex", bool(binary), f"binary {binary or 'NOT FOUND on PATH'}",
               "" if binary else "install the Codex CLI")
    )
    if not binary:
        return results

    config = root / ".codex/config.toml"
    ambient: list[str] = []
    if config.is_file():
        text = config.read_text(encoding="utf-8")
        ambient = [key for key in CODEX_AMBIENT_KEYS if f"{key}" in text]
    results.append(
        Result(
            "codex",
            not ambient,
            "project config implies no ambient runtime authority"
            if not ambient
            else f"project config carries {', '.join(ambient)}",
            "" if not ambient
            else "remove these from .codex/config.toml and pin them per invocation; "
                 "a checked-in file must not grant approvals-off or full disk access",
        )
    )
    # The stdin trap cannot be detected without running: `codex exec` reads
    # stdin for a <stdin> block even with a prompt argument, so an inherited
    # open pipe blocks before any session log is written. It is structural, so
    # it is asserted as a contract rather than probed.
    results.append(
        Result("codex", True,
               "invocation contract: < /dev/null, --sandbox, -c approval_policy, --add-dir .git",
               "")
    )
    return results


def check_agy(settings_path: Path = AGY_SETTINGS) -> list[Result]:
    """AGY is ready when its own settings grant the tools a review needs."""
    results: list[Result] = []
    binary = _binary("agy", "antigravity")
    results.append(
        Result("agy", bool(binary), f"binary {binary or 'NOT FOUND on PATH'}",
               "" if binary else "install the AGY CLI")
    )
    if not binary:
        return results

    path = settings_path.expanduser()
    if not path.is_file():
        return results + [
            Result("agy", False, f"settings absent at {path}",
                   "create it with a permissions.allow list, or pass "
                   "--dangerously-skip-permissions per invocation")
        ]
    try:
        allow = json.loads(path.read_text(encoding="utf-8"))["permissions"]["allow"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return results + [
            Result("agy", False, f"settings unreadable: {exc}",
                   "repair permissions.allow in the settings file")
        ]

    granted = {str(entry) for entry in allow}
    reads = "read_file" in granted
    results.append(
        Result("agy", reads, "read_file granted" if reads else "read_file NOT granted",
               "" if reads else 'add "read_file" to permissions.allow')
    )
    missing = [
        command for command in REVIEW_COMMANDS
        if not any(entry.startswith(f"command({command}") for entry in granted)
    ]
    results.append(
        Result(
            "agy",
            not missing,
            "review commands granted" if not missing
            else f"missing grants: {', '.join(missing)}",
            "" if not missing
            else "add command(...) entries for these, or dispatch a harness that "
                 "does not need a persistent grant",
        )
    )
    return results


def check_cursor(seat: str, registry_path: Path = CURSOR_REGISTRY) -> list[Result]:
    """Cursor is ready when the seat binds and its policy allows evidence commands."""
    results: list[Result] = []
    binary = _binary("cursor-agent")
    results.append(
        Result("cursor", bool(binary), f"binary {binary or 'NOT FOUND on PATH'}",
               "" if binary else "install the Cursor agent CLI")
    )
    if not binary:
        return results

    path = registry_path.expanduser()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))["bindings"][seat]
        seat_root = Path(str(record["root"]))
        model = str(record["model_id"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return results + [
            Result("cursor", False, f"seat {seat} not registered: {exc}",
                   "open the seat once in the Cursor app so sessionStart registers it")
        ]

    exists = seat_root.is_dir()
    results.append(
        Result("cursor", exists,
               f"seat worktree {seat_root} {'present' if exists else 'MISSING'}",
               "" if exists else f"create the {seat} worktree; --workspace must be the "
                                 "seat worktree, not the main checkout")
    )
    # A Claude-authored range needs a non-claude reviewer, and the Cursor
    # default is a Claude model. Report the pin so the caller sees it.
    results.append(
        Result("cursor", True, f"registered model {model} — pin --model explicitly", "")
    )
    if not exists:
        return results

    verdicts = _cursor_policy(seat_root)
    if verdicts is None:
        return results + [
            Result("cursor", False, "could not query cursor_hook_policy.py",
                   "run from the Pipeline root so scripts/ is importable")
        ]
    blocked = [command for command, verdict in verdicts.items() if verdict != "allow"]
    results.append(
        Result(
            "cursor",
            not blocked,
            "policy allows evidence commands" if not blocked
            else "; ".join(f"{command}={verdicts[command]}" for command in blocked),
            "" if not blocked
            else "Cursor can gather evidence but cannot publish a verdict headlessly; "
                 f"see {RUNBOOK}",
        )
    )
    return results


def _cursor_policy(seat_root: Path) -> dict[str, str] | None:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import cursor_hook_policy  # noqa: PLC0415
    except ImportError:
        return None
    environ = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
               "HOME": os.environ.get("HOME", "")}
    verdicts: dict[str, str] = {}
    for command in ("env -u GIT_INDEX_FILE git diff HEAD~1..HEAD",
                    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q"):
        payload = {
            "hook_event_name": "beforeShellExecution",
            "command": command,
            "cwd": str(seat_root),
            "workspace_roots": [str(seat_root)],
        }
        try:
            output, _ = cursor_hook_policy.process_bytes(
                json.dumps(payload).encode(),
                event_hint="beforeShellExecution",
                environ=environ,
                root=seat_root,
            )
            verdicts[command.split()[3]] = json.loads(output).get("permission", "unknown")
        except Exception:  # noqa: BLE001 - a failed query is a failed check
            return None
    return verdicts


def live_probe(harness: str, root: Path) -> Result:
    """Spend one prompt and require a positive artifact, never exit 0.

    Each silent failure mode returns success at the exit code, so the only
    trustworthy signal is the harness echoing something it could not have
    produced without running a tool.
    """
    expected = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=root,
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if not expected:
        return Result(harness, False, "could not resolve HEAD for the probe")

    prompt = (
        "Run exactly this command and reply with ONLY its output: "
        "env -u GIT_INDEX_FILE git rev-parse --short HEAD"
    )
    commands = {
        "codex": ["codex", "exec", "-C", str(root), "--sandbox", "workspace-write",
                  "-c", 'approval_policy="never"', prompt],
        "agy": ["agy", "--sandbox", "--print", prompt],
        "cursor": ["cursor-agent", "-p", "-f", "--trust", prompt],
    }
    try:
        completed = subprocess.run(
            commands[harness], cwd=root, capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=600, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Result(harness, False, f"probe failed to run: {exc}")
    body = completed.stdout + completed.stderr
    hit = expected in body
    return Result(
        harness, hit,
        f"live probe {'echoed HEAD' if hit else 'produced no HEAD'} "
        f"(exit {completed.returncode}, {len(body)} bytes)",
        "" if hit else f"exit code is not evidence; see {RUNBOOK}",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness_preflight.py")
    parser.add_argument("harness", choices=(*HARNESSES, "all"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--seat", default="operator")
    parser.add_argument("--live", action="store_true",
                        help="also spend one tool-using prompt per harness")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    selected = HARNESSES if args.harness == "all" else (args.harness,)
    results: list[Result] = []
    for harness in selected:
        if harness == "codex":
            results += check_codex(root)
        elif harness == "agy":
            results += check_agy()
        else:
            results += check_cursor(args.seat)
        if args.live:
            results.append(live_probe(harness, root))

    failed = False
    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        failed = failed or not result.ok
        print(f"{mark}  {result.harness:7} {result.detail}")
        if result.remedy:
            print(f"      -> {result.remedy}")
    print("READY" if not failed else "NOT READY — dispatching now would fail silently")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
