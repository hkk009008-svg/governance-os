#!/usr/bin/env python3
"""Validate frozen historical report bytes and current compact pair reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import compact_pair_loop


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAILBOX = ROOT / "coordination/mailbox/sent"
DEFAULT_MANIFEST = ROOT / "scripts/baselines/lane_v_reports_pre_v3.json"
MANIFEST_SCHEMA = "lane-v-report-pre-v3-baseline/v1"
HISTORICAL_V3_CUTOFF = "a546f059fc8f3e324cf102e242bdc9840de93880"
MAX_MANIFEST_BYTES = 1_048_576

VERDICT_GO_RE = re.compile(r"^VERDICT: GO$", re.MULTILINE)
EVIDENCE_RE = re.compile(r"^## Evidence\s*$", re.MULTILINE)
COMMAND_RE = re.compile(r"^\$ \S", re.MULTILINE)
OUTPUT_RE = re.compile(r"^→ \S", re.MULTILINE)


class BaselineGenerationError(RuntimeError):
    """The frozen historical manifest is malformed or unavailable."""


@dataclass(frozen=True)
class RawReport:
    relative_path: str
    raw: bytes


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise BaselineGenerationError(f"duplicate manifest key: {key}")
        value[key] = item
    return value


def _read_regular(path: Path, *, maximum: int) -> bytes:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if not nofollow:
        raise OSError("O_NOFOLLOW unavailable")
    descriptor = os.open(
        path,
        os.O_RDONLY
        | nofollow
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0),
    )
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > maximum:
            raise OSError(f"not one bounded regular file: {path}")
        raw = os.read(descriptor, opened.st_size + 1)
        after = os.fstat(descriptor)
        if len(raw) != opened.st_size or (opened.st_dev, opened.st_ino, opened.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise OSError(f"file changed while reading: {path}")
        return raw
    finally:
        os.close(descriptor)


def load_baseline_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, object]:
    raw = _read_regular(path, maximum=MAX_MANIFEST_BYTES)
    try:
        value = json.loads(raw, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BaselineGenerationError(f"invalid historical manifest: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != MANIFEST_SCHEMA:
        raise BaselineGenerationError("invalid historical manifest schema")
    entries = value.get("reports")
    if not isinstance(entries, list):
        raise BaselineGenerationError("historical manifest reports must be a list")
    paths: set[str] = set()
    digests: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise BaselineGenerationError("invalid historical manifest entry")
        report_path = entry["path"]
        digest = entry["sha256"]
        if (
            not isinstance(report_path, str)
            or not report_path.startswith("coordination/mailbox/sent/")
            or not report_path.endswith("-verification-report.md")
            or PurePosixPath(report_path).as_posix() != report_path
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise BaselineGenerationError("invalid historical manifest path or digest")
        if report_path in paths or digest in digests:
            raise BaselineGenerationError("duplicate historical manifest path or digest")
        paths.add(report_path)
        digests.add(digest)
    return value


def _canonical_scan_directory(root: Path, directory: Path | None) -> tuple[Path, str]:
    root = root.resolve()
    expected = root / "coordination/mailbox/sent"
    selected = expected if directory is None else directory
    if not selected.is_absolute():
        selected = root / selected
    try:
        relative = selected.relative_to(root).as_posix()
    except ValueError as exc:
        raise OSError("report directory is outside repository") from exc
    if relative != "coordination/mailbox/sent":
        raise OSError("report directory must be coordination/mailbox/sent")
    current = root
    for component in ("coordination", "mailbox", "sent"):
        current = current / component
        if current.is_symlink():
            raise OSError("report directory traverses symlink")
    return selected, relative


def scan_repository_reports(root: Path, directory: Path | None = None) -> list[RawReport]:
    selected, relative = _canonical_scan_directory(root, directory)
    if not selected.exists():
        return []
    reports: list[RawReport] = []
    for name in sorted(os.listdir(selected)):
        if not name.endswith("-verification-report.md"):
            continue
        raw = _read_regular(selected / name, maximum=compact_pair_loop.MAX_EVENT_BYTES)
        reports.append(RawReport(f"{relative}/{name}", raw))
    return reports


def _git_blob(root: Path, commit: str, path: str) -> bytes | None:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    completed = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", "show", f"{commit}:{path}"],
        cwd=root,
        env=environment,
        capture_output=True,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def _exact_historical_v3(root: Path, report: RawReport) -> bool:
    if b"Verification schema: lane-v-report/v3" not in report.raw:
        return False
    return _git_blob(root, HISTORICAL_V3_CUTOFF, report.relative_path) == report.raw


def _evidence_block(text: str) -> str:
    match = EVIDENCE_RE.search(text)
    if match is None:
        return ""
    tail = text[match.end() :]
    next_heading = re.search(r"^## \S", tail, re.MULTILINE)
    return text[match.start() : match.end() + (next_heading.start() if next_heading else len(tail))]


def go_report_violations(named_reports: list[tuple[str, str]]) -> list[str]:
    violations: list[str] = []
    for name, text in named_reports:
        if VERDICT_GO_RE.search(text) is None:
            continue
        evidence = _evidence_block(text)
        if not evidence:
            violations.append(f"{name}: GO missing Evidence section")
        if COMMAND_RE.search(evidence) is None:
            violations.append(f"{name}: GO evidence missing command")
        if OUTPUT_RE.search(evidence) is None:
            violations.append(f"{name}: GO evidence missing output")
        if "wave_gate_check" in evidence and not re.search(
            r"(?:--runxfail|\b[0-9]+ (?:passed|failed|xfailed|xpassed|error)\b)",
            evidence,
        ):
            violations.append(f"{name}: wave gate is not executed regression evidence")
    return violations


def repository_report_violations(
    root: Path,
    reports: list[RawReport],
    manifest: dict[str, object],
) -> list[str]:
    entries = manifest.get("reports")
    if manifest.get("schema_version") != MANIFEST_SCHEMA or not isinstance(entries, list):
        return ["invalid historical manifest"]
    expected = {entry["path"]: entry["sha256"] for entry in entries if isinstance(entry, dict)}
    observed = {report.relative_path: report for report in reports}
    violations = [f"historical report missing: {path}" for path in expected.keys() - observed.keys()]
    for report in reports:
        digest = hashlib.sha256(report.raw).hexdigest()
        if report.relative_path in expected:
            if digest != expected[report.relative_path]:
                violations.append(f"historical baseline drift: {report.relative_path}")
            continue
        if _exact_historical_v3(root, report):
            continue
        absolute = root / report.relative_path
        try:
            if absolute.read_bytes() != report.raw:
                raise compact_pair_loop.CompactPairError("scanned bytes changed")
            parsed = compact_pair_loop.parse_verification_report(root, absolute)
            violations.extend(
                f"{report.relative_path}: {item}"
                for item in compact_pair_loop.validate_report(root, parsed)
            )
            text = report.raw.decode("utf-8")
        except (OSError, UnicodeError, compact_pair_loop.CompactPairError) as exc:
            violations.append(f"{report.relative_path}: invalid compact report: {exc}")
            continue
        violations.extend(go_report_violations([(report.relative_path, text)]))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_go_schema.py")
    parser.add_argument("directory", nargs="?")
    arguments, unknown = parser.parse_known_args(argv)
    if unknown:
        print("GO-SCHEMA CHECK — FAIL: retired option: " + " ".join(unknown))
        return 1
    try:
        directory = Path(arguments.directory) if arguments.directory else None
        reports = scan_repository_reports(ROOT, directory)
        manifest = load_baseline_manifest()
        violations = repository_report_violations(ROOT, reports, manifest)
    except (OSError, UnicodeError, BaselineGenerationError) as exc:
        print(f"GO-SCHEMA CHECK — FAIL: {exc}")
        return 1
    if violations:
        print(f"GO-SCHEMA CHECK — FAIL: {len(violations)} violation(s)")
        for violation in violations:
            print(f"  ! {violation}")
        return 1
    print(
        "GO-SCHEMA CHECK — PASS: "
        f"{len(reports)} report(s) passed frozen-history and compact-pair validation."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
