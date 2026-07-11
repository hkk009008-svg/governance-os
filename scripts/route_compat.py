#!/usr/bin/env python3
"""Legacy-vs-structured route verdict comparator (ADR-014, R-MEASURE instrument).

Runs the committed fixture corpus through BOTH the legacy prose validator
(protocol_capacity.validate_route) and the structured route/v1 validator, and
writes a machine-readable report. Exit 0 iff every case matches expected.json.
Divergences are pre-triaged in expected.json: legacy-formatting-false-positive
(the defect class route/v1 removes) and narrative-directive-outside-manifest
(free prose the legacy lint still governs during compatibility).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import protocol_capacity  # noqa: E402
import route_manifest  # noqa: E402

WAVE = 2
NARRATIVE = (("Durable Disposition", "Generated projection for route-compat fixtures."),)
SENT_RELDIR = Path("coordination/mailbox/sent")


def _case_projection(case_dir: Path, route: dict, root: Path, relpath: str | None) -> Path:
    """Materialize the case's projection under root; return its path."""
    hand_written = case_dir / "projection.md"
    if relpath is not None:
        destination = root / relpath
    else:
        destination = root / SENT_RELDIR / f"{route['route_id']}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if hand_written.exists():
        destination.write_text(hand_written.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        body = route_manifest.render_markdown(
            route, title="Coordinator → All: Route Compat Fixture", narrative=NARRATIVE
        )
        destination.write_text(body, encoding="utf-8")
        destination.with_suffix(".route.json").write_bytes(
            route_manifest.canonical_route_bytes(route)
        )
    return destination


def _structured_verdict(route: dict, projection: Path, root: Path) -> tuple[bool, list[str]]:
    issues = route_manifest.validate_route_object(route)
    relative = projection.resolve().as_posix()
    if f"/{SENT_RELDIR.as_posix()}/" not in relative:
        issues = [*issues, "route projection must live under coordination/mailbox/sent/"]
    return (not issues), issues


def run_corpus(fixtures_dir: Path) -> dict:
    expected = json.loads((fixtures_dir / "expected.json").read_text(encoding="utf-8"))
    cases = []
    for name in sorted(expected):
        spec = expected[name]
        case_dir = fixtures_dir / "cases" / name
        route = json.loads((case_dir / "route.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet_dir = root / "coordination" / "capacity" / "packets"
            packet_dir.mkdir(parents=True)
            for packet_file in sorted((fixtures_dir / "packets").glob("*.json")):
                shutil.copy(packet_file, packet_dir / packet_file.name)
            projection = _case_projection(case_dir, route, root, spec.get("route_relpath"))
            legacy = protocol_capacity.validate_route(root, WAVE, projection)
            structured_valid, structured_issues = _structured_verdict(
                route, projection, root
            )
        # A rendered pair must also round-trip; hand-written prose has no pair.
        if not (case_dir / "projection.md").exists() and spec.get("route_relpath") is None:
            with tempfile.TemporaryDirectory() as tmp:
                sent = Path(tmp) / SENT_RELDIR
                sent.mkdir(parents=True)
                md_path, _ = route_manifest.write_route_pair(
                    sent, route, title="round-trip", narrative=NARRATIVE
                )
                assert route_manifest.read_manifest(md_path) == route
        case = {
            "name": name,
            "legacy_valid": legacy.valid,
            "legacy_gates": sorted(
                {issue.get("gate", "?") for issue in legacy.blocking_issues}
            ),
            "structured_valid": structured_valid,
            "structured_issues": structured_issues,
            "divergence": spec["divergence"],
            "matches_expectation": (
                legacy.valid == spec["legacy_valid"]
                and structured_valid == spec["structured_valid"]
            ),
        }
        cases.append(case)
    return {
        "schema": "governance.route-compat-report/1",
        "fixtures": str(fixtures_dir),
        "cases": cases,
        "all_match": all(case["matches_expectation"] for case in cases),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=Path("tests/fixtures/route_compat"))
    parser.add_argument("--out", type=Path, help="Write the JSON report here (logs/ artifact).")
    args = parser.parse_args(argv)
    report = run_corpus(args.fixtures)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if report["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
