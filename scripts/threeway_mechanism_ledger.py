#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from threeway import LOAD_BEARING_KINDS  # noqa: E402


@dataclass(frozen=True)
class MechanismRow:
    kind: str
    status: str
    emitters: tuple[str, ...]
    tests: tuple[str, ...]
    note: str


# Tests column policy: cite ONLY test files that exist (collect_mechanisms
# enforces this — the 2026-07-18 audit found six cited files that never
# existed in git history). An empty tuple renders as "(no dedicated test)".
_ROWS = {
    "brief": MechanismRow("brief", "live", ("scripts/overseer_emit.py brief",), (), "overseer-authority fact"),
    "brief_superseded": MechanismRow("brief_superseded", "live", ("scripts/overseer_emit.py brief_superseded",), (), "overseer supersession CLI"),
    "candidate": MechanismRow("candidate", "live", ("scripts/seat_emit.py coordinator candidate", "scripts/seat_emit.py coordinator2 candidate"), (), "interactive coordinator fact"),
    "candidate_aborted": MechanismRow("candidate_aborted", "live", ("scripts/seat_emit.py coordinator candidate_aborted", "scripts/seat_emit.py coordinator2 candidate_aborted"), (), "interactive coordinator abort fact"),
    "assignment": MechanismRow("assignment", "live", ("scripts/overseer_emit.py assignment",), (), "overseer assignment"),
    "attestation": MechanismRow("attestation", "live", ("scripts/seat_emit.py operator attestation", "scripts/seat_emit.py operator2 attestation"), (), "primary verifier attestation"),
    "attestation_revoked": MechanismRow("attestation_revoked", "live", ("scripts/seat_emit.py <seat> attestation_revoked", "scripts/chief_emit.py <chief> attestation_revoked", "scripts/overseer_emit.py attestation_revoked"), ("tests/unit/test_chief_emit.py",), "principal-safe revocation CLIs (chief path tested; seat/overseer paths untested)"),
    "co_sign": MechanismRow("co_sign", "live", ("scripts/seat_emit.py operator2 co_sign",), (), "dynamic mirror-verifier CLI"),
    "re_verify": MechanismRow("re_verify", "live", ("scripts/seat_emit.py operator re_verify",), (), "candidate primary-verifier challenge echo CLI"),
    "re_verify_challenge": MechanismRow("re_verify_challenge", "live", ("scripts/overseer_emit.py re_verify_challenge",), (), "overseer nonce challenge"),
    "cycle_go": MechanismRow("cycle_go", "live", ("scripts/overseer_emit.py cycle_go",), (), "overseer cycle authorization"),
    "release_requested": MechanismRow("release_requested", "live", ("scripts/seat_emit.py coordinator release_requested", "scripts/seat_emit.py coordinator2 release_requested"), (), "interactive coordinator release request"),
    "release_order": MechanismRow("release_order", "live", ("scripts/overseer_emit.py release_order",), (), "manual overseer release order"),
    "human_approval": MechanismRow("human_approval", "live", ("scripts/chief_emit.py <chief> human_approval",), ("tests/unit/test_chief_emit.py",), "rostered chief approval CLI"),
    "approver_roster": MechanismRow("approver_roster", "live", ("scripts/overseer_emit.py approver_roster",), (), "overseer roster"),
    "ci_result": MechanismRow("ci_result", "live", ("scripts/sign_ci_result.py",), ("tests/unit/test_threeway_activation_scripts.py",), "CI attestor fact"),
    "merge_completed": MechanismRow("merge_completed", "live", ("threeway/gate.py run_gate",), ("tests/unit/test_threeway_activation_scripts.py",), "merge-gate completion fact"),
}


def collect_mechanisms() -> dict[str, MechanismRow]:
    missing = set(LOAD_BEARING_KINDS) - set(_ROWS)
    extra = set(_ROWS) - set(LOAD_BEARING_KINDS)
    if missing or extra:
        raise AssertionError(f"ledger drift: missing={sorted(missing)} extra={sorted(extra)}")
    for row in _ROWS.values():
        for test in row.tests:
            if not (_REPO_ROOT / test).is_file():
                raise AssertionError(f"ledger cites a nonexistent test file: {row.kind} -> {test}")
        emitter_path = row.emitters[0].split()[0] if row.emitters else ""
        if emitter_path and not (_REPO_ROOT / emitter_path).is_file():
            raise AssertionError(f"ledger cites a nonexistent emitter: {row.kind} -> {emitter_path}")
    return dict(sorted(_ROWS.items()))


def render_markdown(rows: dict[str, MechanismRow]) -> str:
    lines = [
        "# Threeway Mechanism Ledger",
        "",
        "Generated and checked by:",
        "",
        "```bash",
        ".venv/bin/python scripts/threeway_mechanism_ledger.py --check",
        "```",
        "",
        "| Kind | Status | Runtime emitters / support | Tests | Note |",
        "|---|---|---|---|---|",
    ]
    for row in rows.values():
        emitters = "<br>".join(f"`{emitter}`" for emitter in row.emitters)
        tests = "<br>".join(f"`{test}`" for test in row.tests) or "(no dedicated test)"
        lines.append(f"| `{row.kind}` | `{row.status}` | {emitters} | {tests} | {row.note} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or check the threeway mechanism ledger.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rows = collect_mechanisms()
    text = render_markdown(rows)
    if args.check:
        expected = _REPO_ROOT / "docs/protocol/threeway/MECHANISM-LEDGER.md"
        actual = expected.read_text(encoding="utf-8") if expected.exists() else ""
        if actual != text:
            print("MECHANISM-LEDGER.md is stale; rerender with this script", file=sys.stderr)
            return 1
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
