#!/usr/bin/env python3
"""Run the small set of checks that protect Pipeline's supported surface."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for item in (str(ROOT), str(ROOT / "pipeline")):
    if item not in sys.path:
        sys.path.insert(0, item)

def _project_smoke() -> int:
    failures: list[str] = []
    try:
        import team
        if tuple(team.MEMBERS) != ("codex", "claude", "agy"):
            failures.append(f"unexpected team members: {team.MEMBERS!r}")
        if set(team.RECIPIENTS) != {*team.MEMBERS, "all"}:
            failures.append(f"unexpected recipients: {team.RECIPIENTS!r}")
    except Exception as exc:
        failures.append(f"team import failed: {exc}")
    try:
        import harness_preflight
        failures.extend(
            result.detail
            for result in harness_preflight.check_team_configs(ROOT)
            if not result.ok
        )
    except Exception as exc:
        failures.append(f"desktop config check failed: {exc}")
    try:
        import codex_protocol_model
        if codex_protocol_model.CURRENT_REVIEW_FAMILIES != frozenset({"claude", "gpt"}):
            failures.append("formal review families must remain claude and gpt")
    except Exception as exc:
        failures.append(f"review policy import failed: {exc}")
    if failures:
        print("PROJECT SMOKE — FAIL")
        for failure in failures:
            print(f"  ! {failure}")
        return 1
    print("PROJECT SMOKE — OK")
    return 0


def _coordination_check() -> int:
    import check_coordination
    issues = check_coordination.run(ROOT / "coordination")
    fatal = [item for item in issues if item.severity == "FATAL"]
    for item in fatal:
        print(f"COORDINATION FATAL [{item.kind}] {item.path} — {item.message}")
    if fatal:
        return 1
    print("COORDINATION — OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(arg in {"-h", "--help"} for arg in args):
        print("usage: bin/pipeline check [--fast]")
        return 0
    unknown = [arg for arg in args if arg != "--fast"]
    if unknown:
        print("unknown option: " + " ".join(unknown), file=sys.stderr)
        return 2
    if _project_smoke() or _coordination_check():
        return 1
    if "--fast" in args:
        print("FAST CHECK — PASS")
        return 0
    sys.stdout.flush()
    environment = os.environ.copy()
    environment.pop("GIT_INDEX_FILE", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    if result.returncode:
        return result.returncode
    print("FULL CHECK — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
