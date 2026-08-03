#!/usr/bin/env python3
"""scripts/status.py — live "where are we" snapshot of the repo/program state.

Usage
-----
  python scripts/status.py snapshot             # compact Codex orientation
  python scripts/status.py snapshot <seat>      # one assigned role
  python scripts/status.py                      # compatibility dashboard

Design constraints
------------------
* NEVER hangs or crashes. Every data source is wrapped so a slow/unreachable/
  failing source renders "(unavailable: <reason>)" and the rest still prints.
* stdlib only (urllib, subprocess, re, pathlib, datetime …).
* Pure helpers (count_unread, latest_adr, render) are fully testable.
* I/O collectors (collect_*) each return a value or "(unavailable: ...)" string.
* main(argv=None) -> int always returns 0; the dashboard reports, doesn't gate.

Repo root is resolved as the parent of this file's parent (scripts/ → repo/).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Repo root (works from any CWD)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent


# ===========================================================================
# Pure helpers — TDD'd
# ===========================================================================

# ---------------------------------------------------------------------------
# count_unread
# ---------------------------------------------------------------------------

_TS_LEN = 20  # length of "2026-05-28T20-38-34Z"

# Pattern: <ts>-<from>-to-<to>-<kind>.md
# We extract: ts (first 20 chars), to-seat (segment after "-to-")
_EVENT_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)'
    r'-\w+-to-(?P<to>\w+)-'
    r'.+\.md$'
)


def _normalize_ts(ts: str) -> str:
    """Colon→dash for ISO cursors; a scalar `seq` cursor passes through unchanged
    (it is not a wall-clock and is compared by the projection layer, not here)."""
    return ts.replace(":", "-")


def _is_iso_cursor(ts: str) -> bool:
    normalized = ts.replace(":", "-")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z", normalized) is None:
        return False
    try:
        datetime.strptime(normalized, "%Y-%m-%dT%H-%M-%SZ")
    except ValueError:
        return False
    return True


def count_unread(cursor_ts: str, event_filenames: list[str], seat: str) -> int:
    """Return the number of events addressed to *seat* whose timestamp is
    STRICTLY GREATER THAN *cursor_ts*.

    Normalization: cursor may use colons (T20:38:34Z); filenames always use
    dashes (T20-38-34Z). Both are normalized to dashes before comparison.
    Malformed filenames are silently skipped.

    This legacy helper accepts only an ISO cursor.  Scalar and malformed
    cursors raise rather than recreating the old silent ``0 unread`` failure.
    Production collectors use :func:`bus_unread.resolve_unread`.
    """
    cursor_norm = _normalize_ts(cursor_ts)
    if not _is_iso_cursor(cursor_ts):
        raise ValueError("count_unread requires one ISO mailbox cursor")
    count = 0
    for fname in event_filenames:
        m = _EVENT_RE.match(fname)
        if not m:
            continue
        event_ts = m.group("ts")   # already dashes
        event_to = m.group("to")
        # `all` is a broadcast target → addressed to every real seat (4-seat
        # protocol). _EVENT_RE's (?P<to>\w+) already matches director2/operator2.
        if event_to != seat and event_to != "all":
            continue
        if event_ts > cursor_norm:
            count += 1
    return count


# ---------------------------------------------------------------------------
# latest_adr
# ---------------------------------------------------------------------------

# Matches "## ADR-NNN" or "## ADR-NNN — " etc.; NNN must be all digits.
_ADR_RE = re.compile(
    r'^##\s+ADR-(?P<num>\d+)'   # "## ADR-017"
    r'(?:\s*[—–-]+\s*(?P<title>.+))?',  # optional " — <title>"
    re.MULTILINE,
)


def latest_adr(text: str) -> Optional[tuple[int, str]]:
    """Return (highest_adr_number, title_line) from *text*, or None if absent.

    Headings like "## ADR-NNN — <title>" or "## ADR-NNN — <title>: detail".
    Template placeholders (ADR-NNN with non-digit NNN) are ignored.
    """
    best_num: Optional[int] = None
    best_title: str = ""
    for m in _ADR_RE.finditer(text):
        num = int(m.group("num"))
        title_raw = (m.group("title") or "").strip()
        if best_num is None or num > best_num:
            best_num = num
            best_title = title_raw
    if best_num is None:
        return None
    return (best_num, best_title)


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

_STATUS_ORDER = ["live", "wired", "stubbed", "parked", "dead"]
# scripts/ is on sys.path when status.py runs (own dir as a script, or inserted
# by the importing sibling/test); protocol_mailbox imports only pathlib.
import protocol_mailbox  # noqa: E402
import bus_unread  # noqa: E402  — de-degrade: real ref-bus unread for migrated (scalar) cursors

_MAILBOX_SEATS = protocol_mailbox.RECEIVING_SEATS
_CURSOR_SEATS = protocol_mailbox.SEATS


def render_manifest(components: Optional[list]) -> list[str]:
    """Return lines for the '## Pipeline status (manifest)' section.

    *components* is the list returned by check_doc_claims.audit_manifest,
    or None/[] when no manifest exists.

    Returns a list of strings (no trailing newlines).
    """
    lines: list[str] = []
    lines.append("## Pipeline status (manifest)")

    if components is None:
        lines.append("  (no docs/pipeline_status.toml)")
        lines.append("  source:  docs/pipeline_status.toml (validated by check_doc_claims.audit_manifest)")
        return lines

    if not components:
        lines.append("  (no docs/pipeline_status.toml)")
        lines.append("  source:  docs/pipeline_status.toml (validated by check_doc_claims.audit_manifest)")
        return lines

    # Group by status in canonical order; unknown statuses go last
    grouped: dict[str, list] = {s: [] for s in _STATUS_ORDER}
    other: list = []
    for comp in components:
        status = comp.get("status", "")
        if status in grouped:
            grouped[status].append(comp)
        else:
            other.append(comp)

    for status in _STATUS_ORDER:
        for comp in grouped[status]:
            anchor = comp.get("anchor", "")
            # Split anchor for display: file_rel + symbol
            if anchor and ":" in anchor:
                file_rel, symbol = anchor.rsplit(":", 1)
            else:
                file_rel, symbol = anchor, ""

            if comp.get("valid"):
                line_num = comp.get("current_line")
                lines.append(
                    f"  ✓ {comp['id']}  ({status})  {file_rel}:{symbol} @{line_num}"
                    f"  — {comp['title']}"
                )
            else:
                problem = comp.get("problem", "unknown problem")
                lines.append(
                    f"  ✗ {comp['id']}  ({status})  {file_rel}:{symbol}"
                    f"  [BROKEN: {problem}]"
                )

    for comp in other:
        anchor = comp.get("anchor", "")
        if anchor and ":" in anchor:
            file_rel, symbol = anchor.rsplit(":", 1)
        else:
            file_rel, symbol = anchor, ""
        status = comp.get("status", "unknown")
        if comp.get("valid"):
            line_num = comp.get("current_line")
            lines.append(
                f"  ✓ {comp['id']}  ({status})  {file_rel}:{symbol} @{line_num}"
                f"  — {comp['title']}"
            )
        else:
            problem = comp.get("problem", "unknown problem")
            lines.append(
                f"  ✗ {comp['id']}  ({status})  {file_rel}:{symbol}"
                f"  [BROKEN: {problem}]"
            )

    lines.append("  source:  docs/pipeline_status.toml (validated by check_doc_claims.audit_manifest)")
    return lines


def render(data: dict) -> str:
    """Format an already-collected data dict into the report string.

    All values are pre-collected; this function is pure (no I/O).
    "(unavailable: ...)" strings are passed through verbatim.
    """
    lines: list[str] = []
    a = lines.append

    a(f"# Repo Status  |  generated {data['generated_at']}  |  derived live — do not hand-edit")
    a("")

    # --- Git ---
    a("## Git")
    a(f"  sha:     {data['git_sha']}")
    a(f"  subject: {data['git_subject']}")
    a(f"  branch:  {data['git_branch']}")
    ahead = data['git_ahead']
    behind = data['git_behind']
    a(f"  origin:  {ahead} ahead / {behind} behind origin/main")
    a(f"  dirty:   {data['git_dirty']} file(s) with uncommitted changes")
    a("  source:  git rev-parse, git log -1, git status --porcelain")
    a("")

    # --- Coordination ---
    a("## Coordination (mailbox)")
    for seat in _MAILBOX_SEATS:
        a(f"  {seat:<9} cursor={data.get(f'mailbox_{seat}_cursor', '(missing)')}  "
          f"unread={data.get(f'mailbox_{seat}_unread', '(missing)')}")
    a("  source:  coordination/mailbox/seen/*.txt + coordination/mailbox/sent/")
    a("")

    # --- Decisions ---
    a("## Decisions")
    a(f"  latest ADR: {data['latest_adr']}")
    a("  source:  DECISIONS.md  (grep ^## ADR-NNN)")
    a("")

    # --- Doc integrity ---
    a("## Doc integrity")
    a(f"  anchor-drift: {data['doc_integrity']}")
    a("  source:  scripts/check_doc_claims.py (ARCHITECTURE.md)")
    a("")

    # --- Pod ---
    a("## Infra (GPU compute pod)")
    a(f"  pod: {data['pod_status']}")
    a("  source:  .env GPU_POD_SERVER_URL → <url>/system_stats (timeout=3s)")
    a("")

    # --- Pipeline manifest ---
    manifest_components = data.get("manifest_components")
    manifest_lines = render_manifest(manifest_components)
    lines.extend(manifest_lines)
    a("")

    # --- Smoke pointer ---
    a("## Smoke test")
    a("  smoke: run `python scripts/ci_smoke.py`")
    a("  (not run inline — too heavy for a status command)")

    return "\n".join(lines) + "\n"


# ===========================================================================
# I/O collectors — each returns a value or "(unavailable: <reason>)"
# ===========================================================================

def _run_git(repo_root: Path, args: list[str], timeout: int = 5) -> str:
    """Run a git command; return stdout stripped or raise."""
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    result = subprocess.run(
        ["git"] + args,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {args[0]} failed")
    return result.stdout.strip()


def collect_git(repo_root: Path) -> dict:
    """Collect git state. Each field is a value or '(unavailable: ...)'."""

    def _get(label: str, args: list[str]):
        try:
            return _run_git(repo_root, args)
        except Exception as e:
            return f"(unavailable: {label}: {e})"

    sha = _get("sha", ["rev-parse", "--short", "HEAD"])
    subject = _get("subject", ["log", "-1", "--format=%s"])
    branch = _get("branch", ["rev-parse", "--abbrev-ref", "HEAD"])

    try:
        ahead_raw = _run_git(repo_root, ["rev-list", "--count", "origin/main..HEAD"])
        ahead = int(ahead_raw)
    except Exception as e:
        ahead = f"(unavailable: ahead: {e})"

    try:
        behind_raw = _run_git(repo_root, ["rev-list", "--count", "HEAD..origin/main"])
        behind = int(behind_raw)
    except Exception as e:
        behind = f"(unavailable: behind: {e})"

    try:
        status_out = _run_git(repo_root, ["status", "--porcelain"])
        dirty = len([l for l in status_out.splitlines() if l.strip()])
    except Exception as e:
        dirty = f"(unavailable: dirty: {e})"

    return {
        "git_sha": sha,
        "git_subject": subject,
        "git_branch": branch,
        "git_ahead": ahead,
        "git_behind": behind,
        "git_dirty": dirty,
    }


def _read_cursor(path: Path) -> str:
    """Read a cursor file; return the timestamp string or '(unavailable: ...)'."""
    try:
        return path.read_text().strip()
    except Exception as e:
        return f"(unavailable: {e})"


def collect_mailbox(repo_root: Path) -> dict:
    """Collect unread counts together with their proven authority source."""
    sent_dir = repo_root / "coordination" / "mailbox" / "sent"
    seen_dir = repo_root / "coordination" / "mailbox" / "seen"

    try:
        event_filenames = [p.name for p in sent_dir.iterdir() if p.is_file()]
    except Exception as e:
        unavail = f"(unavailable: {e})"
        return {
            f"mailbox_{seat}_{field}": unavail
            for seat in _MAILBOX_SEATS
            for field in ("unread", "cursor", "source", "transport", "detail")
        }

    data = {}
    for seat in _MAILBOX_SEATS:
        if seat not in _CURSOR_SEATS:
            data[f"mailbox_{seat}_cursor"] = "(cursorless)"
            data[f"mailbox_{seat}_unread"] = "(broadcast read-only)"
            data[f"mailbox_{seat}_source"] = "broadcast-read-only"
            data[f"mailbox_{seat}_transport"] = "none"
            data[f"mailbox_{seat}_detail"] = (
                "coordinator roles do not own or consume mailbox cursors"
            )
            continue
        cursor = _read_cursor(seen_dir / f"{seat}.txt")
        try:
            resolution = bus_unread.resolve_unread(
                repo_root, seat, cursor, event_filenames
            )
            unread = (
                resolution.count
                if resolution.count is not None
                else f"(unavailable: {resolution.detail})"
            )
            source = resolution.source
            transport = resolution.transport
            detail = resolution.detail
        except Exception as e:
            unread = f"(unavailable: {e})"
            source = "unavailable"
            transport = "incoherent"
            detail = str(e)
        data[f"mailbox_{seat}_cursor"] = cursor
        data[f"mailbox_{seat}_unread"] = unread
        data[f"mailbox_{seat}_source"] = source
        data[f"mailbox_{seat}_transport"] = transport
        data[f"mailbox_{seat}_detail"] = detail
    return data


def collect_adr(repo_root: Path) -> dict:
    """Read DECISIONS.md and extract the latest ADR."""
    try:
        text = (repo_root / "DECISIONS.md").read_text(encoding="utf-8")
        result = latest_adr(text)
        if result is None:
            return {"latest_adr": "(unavailable: no ADR headings found)"}
        num, title = result
        label = f"ADR-{num:03d}"
        if title:
            label += f" — {title}"
        return {"latest_adr": label}
    except Exception as e:
        return {"latest_adr": f"(unavailable: {e})"}


def collect_doc_integrity(repo_root: Path) -> dict:
    """Run check_doc_claims on ARCHITECTURE.md; return drift count or 'clean'."""
    try:
        # scripts/ is already on sys.path when running scripts/status.py
        scripts_dir = str(repo_root / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import check_doc_claims  # type: ignore
        drifts = check_doc_claims.run(["ARCHITECTURE.md"], repo_root)
        n = len(drifts)
        if n == 0:
            val = "clean"
        else:
            val = f"{n} drift(s) — run check_doc_claims.py --fix"
        return {"doc_integrity": val}
    except Exception as e:
        return {"doc_integrity": f"(unavailable: {e})"}


def _parse_env_key(repo_root: Path, key: str) -> Optional[str]:
    """Read KEY=VALUE from .env file. Returns value or None if absent/error."""
    env_path = repo_root / ".env"
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{key}="):
                return line[len(key) + 1:].strip().strip('"').strip("'")
    except Exception:
        pass  # .env missing or unreadable — caller falls back to env-var or None
    return None


def _probe_url(url: str, timeout: int = 3) -> str:
    """Probe <url>/system_stats; return 'UP' or 'DOWN'."""
    try:
        probe = url.rstrip("/") + "/system_stats"
        with urllib.request.urlopen(probe, timeout=timeout) as resp:
            if resp.status == 200:
                return "UP"
            return f"DOWN (HTTP {resp.status})"
    except Exception:
        return "DOWN"


def collect_pod(repo_root: Path) -> dict:
    """Probe the GPU compute pod via GPU_POD_SERVER_URL from .env."""
    url = _parse_env_key(repo_root, "GPU_POD_SERVER_URL")
    if not url:
        return {"pod_status": "(unavailable: no GPU_POD_SERVER_URL)"}
    status = _probe_url(url, timeout=3)
    return {"pod_status": status}


def collect_manifest(repo_root: Path) -> dict:
    """Load and validate docs/pipeline_status.toml via check_doc_claims.audit_manifest.

    Returns {"manifest_components": list} where list may be:
      - a list of component dicts (from audit_manifest)
      - [] when the manifest file is absent
      - None when unavailable due to an error (rendered as unavailable sentinel)
    """
    try:
        scripts_dir = str(repo_root / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import check_doc_claims  # type: ignore
        manifest_path = repo_root / "docs" / "pipeline_status.toml"
        components = check_doc_claims.audit_manifest(manifest_path, repo_root)
        # audit_manifest returns [] if file absent — pass through as-is
        return {"manifest_components": components}
    except Exception as e:
        return {"manifest_components": None}


# ===========================================================================
# Main
# ===========================================================================

def _collect_all(repo_root: Path) -> dict:
    """Collect all data sources into a single flat dict."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data: dict = {"generated_at": now}
    data.update(collect_git(repo_root))
    data.update(collect_mailbox(repo_root))
    data.update(collect_adr(repo_root))
    data.update(collect_doc_integrity(repo_root))
    data.update(collect_pod(repo_root))
    data.update(collect_manifest(repo_root))
    return data


def collect_orientation_snapshot(
    repo_root: Path, seat: str | None = None
) -> dict:
    """Collect the small executable orientation surface used by Codex."""

    if seat is not None and seat not in _MAILBOX_SEATS:
        raise ValueError(f"unknown mailbox seat: {seat}")
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git = collect_git(repo_root)
    mailbox = collect_mailbox(repo_root)
    selected = (seat,) if seat is not None else _CURSOR_SEATS
    unread = {
        role: {
            "cursor": mailbox[f"mailbox_{role}_cursor"],
            "count": mailbox[f"mailbox_{role}_unread"],
            "source": mailbox[f"mailbox_{role}_source"],
            "transport": mailbox[f"mailbox_{role}_transport"],
            "detail": mailbox[f"mailbox_{role}_detail"],
        }
        for role in selected
    }

    # Local import avoids making the status helper/checker module dependency
    # recursive at import time.
    import check_coordination  # type: ignore

    review_state = check_coordination.inspect_verify_review_state(repo_root)
    requests = list(review_state.pending)
    failed_reviews = list(review_state.failed)
    if seat in {"operator", "operator2"}:
        requests = [
            request for request in requests
            if request.assigned_operator == seat
        ]
    current = max(requests, key=lambda request: request.path, default=None)
    failed = max(
        failed_reviews, key=lambda review: review.report_path, default=None
    )
    issues = check_coordination.run(
        repo_root / "coordination",
        docs_root=repo_root / "docs",
        review_state=review_state,
    )
    fatals = [issue for issue in issues if issue.severity == "FATAL"]
    advisories = [issue for issue in issues if issue.severity == "ADVISORY"]

    blocker = None
    if fatals:
        blocker = f"{fatals[0].kind}: {fatals[0].message}"
    elif current is not None and not current.valid:
        blocker = (
            f"invalid current request for {current.assigned_operator}: "
            f"{current.problem}"
        )
    elif failed is not None:
        blocker = (
            f"failed review for {failed.assigned_operator}: "
            f"{failed.report_path}@{failed.report_commit}"
        )

    if blocker is not None:
        if fatals or (current is not None and not current.valid):
            next_action = "repair the blocker before implementation or review"
        elif failed is not None:
            next_action = (
                f"remediate failed review for {failed.request_path}@"
                f"{failed.request_commit}"
            )
    elif current is not None:
        next_action = (
            f"{current.assigned_operator} reviews the exact committed request"
        )
    else:
        next_action = "continue routed local work; publish a request when review is needed"

    current_data = None
    if current is not None:
        current_data = {
            "path": current.path,
            "commit": current.commit,
            "assigned_operator": current.assigned_operator,
            "valid": current.valid,
            "grandfathered": current.grandfathered,
            "problem": current.problem,
        }
    failed_data = None
    if failed is not None:
        failed_data = {
            "request_path": failed.request_path,
            "request_commit": failed.request_commit,
            "report_path": failed.report_path,
            "report_commit": failed.report_commit,
            "assigned_operator": failed.assigned_operator,
        }
    gate_status = (
        "FAIL" if fatals or failed_reviews else ("WARN" if advisories else "PASS")
    )
    return {
        "generated_at": now,
        "git": {
            "sha": git["git_sha"],
            "branch": git["git_branch"],
            "dirty": git["git_dirty"],
        },
        "unread": unread,
        "current_request": current_data,
        "failed_review": failed_data,
        "gate": {
            "status": gate_status,
            "fatal": len(fatals),
            "advisory": len(advisories),
            "failed_review": len(failed_reviews),
        },
        "blocker": blocker,
        "next_action": next_action,
    }


def render_orientation_snapshot(snapshot: dict) -> str:
    """Render the compact snapshot in at most twenty human-readable lines."""

    git = snapshot["git"]
    lines = [
        f"Pipeline snapshot {snapshot['generated_at']}",
        f"Git: {git['sha']} branch={git['branch']} dirty={git['dirty']}",
        "Unread:",
    ]
    for role, unread in snapshot["unread"].items():
        lines.append(
            f"  {role}: {unread['count']} via {unread['source']} "
            f"(cursor={unread['cursor']}, transport={unread['transport']})"
        )
    current = snapshot.get("current_request")
    if current is None:
        lines.append("Request: none")
    else:
        commit = current.get("commit") or "uncommitted"
        state = "valid" if current.get("valid") else "INVALID"
        lines.append(
            f"Request: {current['path']}@{commit} "
            f"assigned={current['assigned_operator']} {state}"
        )
    failed = snapshot.get("failed_review")
    if failed is not None:
        lines.append(
            f"Failed review: {failed['report_path']}@{failed['report_commit']} "
            f"request={failed['request_path']}@{failed['request_commit']}"
        )
    gate = snapshot["gate"]
    lines.append(
        f"Gate: {gate['status']} ({gate['fatal']} fatal, "
        f"{gate['advisory']} advisory, "
        f"{gate.get('failed_review', 0)} failed review)"
    )
    lines.append(f"Blocker: {snapshot.get('blocker') or 'none'}")
    lines.append(f"Next: {snapshot['next_action']}")
    if len(lines) > 20:
        raise ValueError("orientation snapshot exceeded the 20-line contract")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print a live status snapshot of the repo.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="optional subcommand: 'mailbox-unread' (print one seat's live unread count)",
    )
    parser.add_argument(
        "seat",
        nargs="?",
        default=None,
        help="seat for 'mailbox-unread': director | director2 | operator | operator2",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Also write the report to STATUS.md at the repo root.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="For 'snapshot', emit the machine-readable object.",
    )
    args = parser.parse_args(argv)

    repo_root = _REPO_ROOT
    # Focused subcommand: print just one seat's LIVE unread count and exit.
    # Reuses the canonical count_unread (via collect_mailbox) — one source of
    # truth, no second copy of the logic — and skips the heavy dashboard (no
    # GPU pod probe / doc reads). This is the instrument Rule #20.1
    # live-recompute should call instead of a hand-rolled `ls|awk` (which has
    # two proven sharp edges: full-filename-vs-bare-prefix over-count, and
    # field-split capturing trailing text).
    if args.command == "mailbox-unread":
        if args.seat not in _CURSOR_SEATS:
            parser.error(
                "mailbox-unread requires a seat: "
                "director | director2 | operator | operator2"
            )
        print(collect_mailbox(repo_root)[f"mailbox_{args.seat}_unread"])
        return 0
    if args.command == "snapshot":
        if args.seat is not None and args.seat not in _MAILBOX_SEATS:
            parser.error(
                "snapshot seat must be one of: " + " | ".join(_MAILBOX_SEATS)
            )
        snapshot = collect_orientation_snapshot(repo_root, args.seat)
        if args.json:
            print(json.dumps(snapshot, sort_keys=True))
        else:
            print(render_orientation_snapshot(snapshot), end="")
        return 0
    if args.command is not None:
        parser.error(f"unknown command: {args.command!r}")

    data = _collect_all(repo_root)
    report = render(data)

    print(report, end="")

    if args.write:
        out_path = repo_root / "STATUS.md"
        out_path.write_text(report, encoding="utf-8")
        print("(wrote STATUS.md)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
