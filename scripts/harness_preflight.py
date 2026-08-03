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
requires the exact nonempty `HEAD^..HEAD` name-status artifact because exit 0
is not evidence that anything ran.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts import compact_pair_loop
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    import compact_pair_loop  # type: ignore[no-redef]

HARNESSES = ("codex", "agy", "cursor")
AGY_SETTINGS = Path("~/.gemini/antigravity-cli/settings.json")
CURSOR_REGISTRY = Path("~/.cursor/pipeline-app-seats.json")
RUNBOOK = "docs/protocol/threeway/HEADLESS-REVIEW.md"
AGY_SCOPES = ("evidence", "publishing")
MAX_PACKAGE_BYTES = 1_048_576
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
AGY_PROBE_MODEL = "gemini-3.6-flash-low"

# What a review actually runs. AGY grants are matched against these because a
# harness that can read files but not run pytest still cannot produce evidence.
AGY_EVIDENCE_COMMANDS = (
    "git diff",
    "git show",
    "git status",
    "git rev-parse",
    "git merge-base",
    "rg",
    ".venv/bin/python -m pytest",
)
AGY_PUBLISH_COMMANDS = (
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


class PreflightError(ValueError):
    """One preflight or tool-less packaging boundary failed closed."""


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
    # Capability checks below read files, not the binary, so they run even where
    # it is absent. Returning early here is what made the equivalent launcher
    # test vacuous in CI, which installs no harness CLI at all.
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


def _command_granted(command: str, granted: set[str]) -> bool:
    exact = f"command({command})"
    prefix = f"command({command} "
    return any(entry == exact or entry.startswith(prefix) for entry in granted)


def check_agy(
    settings_path: Path = AGY_SETTINGS,
    *,
    scope: str = "publishing",
) -> list[Result]:
    """Check one explicit AGY capability scope without granting authority."""
    if scope not in AGY_SCOPES:
        raise ValueError(f"unknown AGY capability scope: {scope}")
    results: list[Result] = []
    binary = _binary("agy", "antigravity")
    results.append(
        Result("agy", bool(binary), f"binary {binary or 'NOT FOUND on PATH'}",
               "" if binary else "install the AGY CLI")
    )
    results.append(
        Result(
            "agy",
            True,
            "capability scope evidence selected — evidence-only; cannot publish "
            "or formalize a verdict"
            if scope == "evidence"
            else "capability scope publishing selected — persistent grants are "
            "capability only; execution still requires separate authority",
        )
    )
    path = settings_path.expanduser()
    if not path.is_file():
        return results + [
            Result("agy", False, f"settings absent at {path}",
                   "create it with a scoped permissions.allow list, or use the "
                   "tool-less package fallback")
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
        command
        for command in AGY_EVIDENCE_COMMANDS
        if not _command_granted(command, granted)
    ]
    results.append(
        Result(
            "agy",
            not missing,
            "evidence commands granted"
            if not missing
            else f"missing evidence grants: {', '.join(missing)}",
            "" if not missing
            else "add only the required read-only command(...) entries, or use the "
            "tool-less package fallback",
        )
    )
    if scope == "publishing":
        missing_publish = [
            command
            for command in AGY_PUBLISH_COMMANDS
            if not _command_granted(command, granted)
        ]
        results.append(
            Result(
                "agy",
                not missing_publish,
                "publishing commands granted; execution still requires separate authority"
                if not missing_publish
                else f"missing publishing grants: {', '.join(missing_publish)}",
                ""
                if not missing_publish
                else "add persistent effect grants only under separate publication and "
                "commit authority; evidence scope does not require them",
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


def _git_bytes(root: Path, *arguments: str, max_bytes: int) -> bytes:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    try:
        process = subprocess.Popen(
            ["/usr/bin/git", "--no-replace-objects", *arguments],
            cwd=root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise PreflightError(f"git {' '.join(arguments[:2])} failed: {exc}") from exc
    assert process.stdout is not None
    try:
        output = process.stdout.read(max_bytes + 1)
    finally:
        process.stdout.close()
    if len(output) > max_bytes:
        process.kill()
        process.wait()
        raise PreflightError(f"git {' '.join(arguments[:2])} output is oversized")
    returncode = process.wait()
    if returncode != 0:
        raise PreflightError(f"git {' '.join(arguments[:2])} failed")
    return output


def package_toolless_review(
    root: Path,
    request_ref: str,
    *,
    max_bytes: int = MAX_PACKAGE_BYTES,
) -> str:
    """Build one bounded, no-provider prompt from committed request and diff bytes."""
    root = root.resolve()
    path, separator, trigger = request_ref.rpartition("@")
    if not separator or not path or FULL_SHA_RE.fullmatch(trigger) is None:
        raise PreflightError("package request must be path@full lowercase commit SHA")
    if max_bytes <= 0:
        raise PreflightError("package byte limit must be positive")
    try:
        request = compact_pair_loop.parse_verify_request(root, path, trigger)
    except compact_pair_loop.CompactPairError as exc:
        raise PreflightError(f"committed request is invalid: {exc}") from exc

    reviewed_root = root
    if request.reviewed_repository is not None:
        recorded_root = Path(request.reviewed_repository)
        if recorded_root.is_dir():
            reviewed_root = recorded_root.resolve()
    request_bytes = _git_bytes(
        root, "show", f"{trigger}:{path}", max_bytes=max_bytes
    )
    diff_bytes = _git_bytes(
        reviewed_root,
        "diff",
        "--binary",
        "--no-ext-diff",
        "--no-textconv",
        request.reviewed_base,
        request.reviewed_head,
        "--",
        max_bytes=max_bytes,
    )
    if not diff_bytes.strip():
        raise PreflightError("reviewed range produced an empty diff")

    header = (
        "TOOL-LESS ADVISORY REVIEW PACKAGE\n"
        "No repository tools are available to the reviewer. Treat the committed "
        "request and verbatim diff below as ground truth; report any check that "
        "requires execution as unavailable. This package cannot publish or "
        "formalize a verdict.\n\n"
        f"Verification request: {request_ref}\n"
        f"Exact reviewed range: {request.reviewed_base}..{request.reviewed_head}\n\n"
        "--- COMMITTED VERIFY REQUEST ---\n"
    ).encode("utf-8")
    separator_bytes = b"\n--- EXACT COMMITTED RANGE DIFF ---\n"
    package = header + request_bytes + separator_bytes + diff_bytes
    if len(package) > max_bytes:
        raise PreflightError(
            f"tool-less review package exceeds {max_bytes} bytes"
        )
    try:
        return package.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PreflightError("tool-less review package is not UTF-8") from exc


def live_probe(
    harness: str,
    root: Path,
    *,
    runner=subprocess.run,
) -> Result:
    """Spend one prompt and require a positive artifact, never exit 0.

    Each silent failure mode returns success at the exit code, so the only
    trustworthy signal is the harness echoing something it could not have
    produced without running a tool.
    """
    try:
        expected = _git_bytes(
            root,
            "diff",
            "--name-status",
            "HEAD^",
            "HEAD",
            "--",
            max_bytes=65_536,
        ).decode("utf-8", errors="strict").strip()
    except (PreflightError, UnicodeDecodeError) as exc:
        return Result(harness, False, f"could not resolve probe range: {exc}")
    if not expected:
        return Result(harness, False, "probe range produced no positive artifact")

    prompt = (
        "Run exactly this command and reply with ONLY its output: "
        "env -u GIT_INDEX_FILE git diff --name-status HEAD^ HEAD --"
    )
    commands = {
        "codex": ["codex", "exec", "-C", str(root), "--sandbox", "workspace-write",
                  "-c", 'approval_policy="never"', prompt],
        "agy": [
            "agy",
            "--sandbox",
            "--print",
            "--model",
            AGY_PROBE_MODEL,
            prompt,
        ],
        "cursor": ["cursor-agent", "-p", "-f", "--trust", prompt],
    }
    try:
        completed = runner(
            commands[harness], cwd=root, capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=600, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Result(harness, False, f"probe failed to run: {exc}")
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    hit = completed.returncode == 0 and stdout.strip() == expected
    return Result(
        harness, hit,
        f"live probe {'returned exact positive artifact' if hit else 'produced no exact positive artifact'} "
        f"({'model ' + AGY_PROBE_MODEL + ', ' if harness == 'agy' else ''}"
        f"exit {completed.returncode}, stdout {len(stdout)} bytes, "
        f"stderr {len(stderr)} bytes)",
        "" if hit else f"exit code is not evidence; see {RUNBOOK}",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness_preflight.py")
    parser.add_argument("harness", choices=(*HARNESSES, "all"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--seat", default="operator")
    parser.add_argument(
        "--agy-scope",
        choices=AGY_SCOPES,
        default="publishing",
        help="explicit AGY capability scope (default: publishing, the full check)",
    )
    parser.add_argument(
        "--package-request",
        metavar="PATH@COMMIT",
        help="print one bounded tool-less AGY review package without provider launch",
    )
    parser.add_argument("--live", action="store_true",
                        help="also spend one tool-using prompt per harness")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    if args.package_request is not None:
        if args.harness != "agy" or args.live:
            parser.error("--package-request requires harness=agy and cannot use --live")
        try:
            print(package_toolless_review(root, args.package_request), end="")
        except PreflightError as exc:
            print(f"FAIL  agy     {exc}")
            return 1
        return 0
    selected = HARNESSES if args.harness == "all" else (args.harness,)
    results: list[Result] = []
    for harness in selected:
        if harness == "codex":
            results += check_codex(root)
        elif harness == "agy":
            results += check_agy(scope=args.agy_scope)
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
