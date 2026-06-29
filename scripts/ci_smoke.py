#!/usr/bin/env python3
"""Governance smoke checks + project-runtime stub for this repo.

Two halves run in sequence:

  HALF A — Project runtime smoke (_project_smoke):
    A stub that returns 0. The new project's authors replace this with
    runtime invariants appropriate to their stack (imports succeed, singletons
    are stable, settings plumb through). See _project_smoke() below.

  HALF B — Governance gates (always active):
    These are fully portable and run unchanged in any project seeded from this
    transfer bundle:

    - Doc-anchor drift gate: check_doc_claims on ARCHITECTURE.md
      (hard-fail locally; warn in CI).
    - PROGRAM-MANUAL anchor-drift WARN (advisory; never a hard-fail).
    - Manifest drift WARN (docs/pipeline_status.toml; never a hard-fail).
    - Commit-SHA ref drift WARN (git-backed; never a hard-fail).
    - Coordination-state gate: check_coordination (FATAL hard-fails locally,
      warns in CI; ADVISORY warns everywhere).
    - Anti-ceremony gate: check_no_ceremony (hard-fail local + CI — ADR-028).
    - Reviewer-result schema validation: consume_reviewer_result smoke_check
      (schema-validation only; never re-runs pytest — ADR-032).

Usage:
    .venv/bin/python scripts/ci_smoke.py    # local
    python scripts/ci_smoke.py              # CI (after pip install)

Exit codes:
    0 — all checks pass
    1 — assertion failed (an invariant or gate broke)
   >1 — script error (import-time failure, etc.)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Bootstrap sys.path so we can import from the repo root regardless of CWD.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _project_smoke() -> int:
    """Project-runtime smoke: the governance OS's own load-bearing invariants.

    This repo's product IS the governance OS, so the runtime smoke asserts the
    OS's own code imports cleanly and its core singletons/vocabularies are stable:
      - the signed-bus package + its RFC-8785 canonicalizer import and round-trip,
      - the load-bearing kind set is a subset of the full kind vocabulary,
      - the seat roster (single source of truth) has the expected shape and the
        markdown mailbox kind registry parses from coordination/mailbox/kinds.txt.
    """
    failures: list[str] = []

    # 1. Signed-bus package imports cleanly + canonicalizer is key-order-stable.
    try:
        import threeway
        from threeway.canon import canonicalize
        from threeway import envelope, keys, reducer, gate  # noqa: F401 — import-cleanliness
        if canonicalize({"b": 1, "a": 2}) != canonicalize({"a": 2, "b": 1}):
            failures.append("canonicalize is not key-order-stable (RFC-8785 broken)")
        if not (threeway.LOAD_BEARING_KINDS <= threeway.THREEWAY_KINDS):
            failures.append("LOAD_BEARING_KINDS is not a subset of THREEWAY_KINDS")
        if "merge_completed" not in threeway.LOAD_BEARING_KINDS:
            failures.append("merge_completed missing from LOAD_BEARING_KINDS")
    except Exception as e:  # surface the real import/runtime error
        failures.append(f"threeway import/canon failed: {e!r}")

    # 2. Seat roster (single source of truth) + mailbox kind registry are stable.
    try:
        import protocol_mailbox as _pm
        if not set(_pm.SEATS) >= {"director", "director2", "operator", "operator2"}:
            failures.append(f"SEATS roster missing expected members: {_pm.SEATS!r}")
        if not set(_pm.RECEIVING_SEATS) >= set(_pm.SEATS):
            failures.append("RECEIVING_SEATS does not contain every SEAT")
        if not _pm.KNOWN_KINDS:
            failures.append("KNOWN_KINDS empty — coordination/mailbox/kinds.txt did not parse")
    except Exception as e:
        failures.append(f"protocol_mailbox roster failed: {e!r}")

    if failures:
        print("PROJECT SMOKE — governance-OS runtime invariants")
        for _f in failures:
            print(f"  ✗ {_f}")
        return 1
    print("PROJECT SMOKE — governance-OS runtime invariants ... OK")
    return 0


def main() -> int:
    # --- HALF A: project runtime smoke ---
    _result = _project_smoke()
    if _result:
        return _result

    # --- HALF B: governance gates (fully portable) ---

    # Doc-anchor drift gate (check_doc_claims on ARCHITECTURE.md).
    # Hard-fail locally; warn-only in CI.
    import check_doc_claims as _cdc

    _repo_root = Path(_REPO_ROOT)
    _drifts = _cdc.run(["ARCHITECTURE.md"], _repo_root)
    if _drifts:
        _n = len(_drifts)
        if os.environ.get("CI"):
            print(
                f"WARNING: {_n} doc-anchor drift(s) found (non-blocking in CI; "
                f"run .venv/bin/python scripts/check_doc_claims.py --fix to repair)"
            )
            for _d in _drifts:
                print(f"  [{_d.kind}] {_d.target_file}:{_d.target_line} — {_d.message}")
        else:
            print(f"\nDOC-ANCHOR DRIFT: {_n} issue(s) found in ARCHITECTURE.md")
            for _d in _drifts:
                _hint = f"  → suggested line {_d.suggested_line}" if _d.suggested_line else ""
                print(f"  [{_d.kind}] {_d.target_file}:{_d.target_line}{_hint}")
                print(f"    {_d.message}")
            print(
                "\nRun: .venv/bin/python scripts/check_doc_claims.py --fix"
            )
            return 1

    # PROGRAM-MANUAL anchor-drift WARN (never a hard-fail): the ungated manual
    # decays at code-churn rate — warn-in-smoke + fix-on-touch. The hard gate
    # above stays ARCHITECTURE.md-only by design. Advisory kinds (ambiguous_path
    # etc.) are excluded — they are exit-neutral in the CLI too.
    _manual_drifts, _ = _cdc._split_advisories(
        _cdc.run(["docs/PROGRAM-MANUAL.md"], _repo_root)
    )
    if _manual_drifts:
        _mn = len(_manual_drifts)
        print(
            f"WARNING: {_mn} doc-anchor drift(s) in docs/PROGRAM-MANUAL.md "
            f"(advisory; fix-on-touch: .venv/bin/python "
            f"scripts/check_doc_claims.py --fix docs/PROGRAM-MANUAL.md)"
        )
        for _d in _manual_drifts[:5]:
            print(f"  [{_d.kind}] {_d.target_file}:{_d.target_line} — {_d.message}")
        if _mn > 5:
            print(f"  ... and {_mn - 5} more")

    # Manifest drift WARN (never a hard-fail — manifest is not auto-fixable).
    _manifest_drifts = _cdc.check_manifest(
        _repo_root / "docs" / "pipeline_status.toml", _repo_root
    )
    if _manifest_drifts:
        _mn = len(_manifest_drifts)
        print(
            f"WARNING: {_mn} stale manifest claim(s) in docs/pipeline_status.toml"
            f" (edit the manifest):"
        )
        for _md in _manifest_drifts:
            print(f"  {_md.message}")

    # Commit-SHA ref drift WARN (git-backed; never a hard-fail — shallow clones
    # skip reachability, and SHA drift is not auto-fixable).
    _sha_drifts = _cdc.check_sha_refs(_cdc.SHA_DEFAULT_DOCS, _repo_root)
    if _sha_drifts:
        _sn = len(_sha_drifts)
        print(
            f"WARNING: {_sn} stale commit-SHA ref(s) in docs"
            f" (run .venv/bin/python scripts/check_doc_claims.py --sha-refs):"
        )
        for _sd in _sha_drifts:
            print(
                f"  [{_sd.kind}] {Path(_sd.doc_path).name}:{_sd.doc_line}"
                f" (sha: {_sd.symbol}) — {_sd.message}"
            )

    # Coordination-state gate (protocol v6.0, check_coordination).
    # FATAL (broken cursor / filename-convention violation) hard-fails locally,
    # warns in CI; ADVISORY warns everywhere; INFO (unread counts) is silent
    # here — the CLI prints it.
    import check_coordination as _cc

    _coord_issues = _cc.run(_repo_root / "coordination", docs_root=_repo_root / "docs")
    _coord_fatal = [_i for _i in _coord_issues if _i.severity == "FATAL"]
    _coord_adv = [_i for _i in _coord_issues if _i.severity == "ADVISORY"]
    for _i in _coord_adv:
        print(f"WARNING: coordination ADVISORY [{_i.kind}] {_i.path} — {_i.message}")
    if _coord_fatal:
        for _i in _coord_fatal:
            print(f"COORDINATION FATAL [{_i.kind}] {_i.path} — {_i.message}")
        if not os.environ.get("CI"):
            print("\nRun: .venv/bin/python scripts/check_coordination.py")
            return 1
        print("WARNING: coordination FATALs are non-blocking in CI")

    # ADR-028: hard-fail local/CI smoke when verification ceremony is detected.
    import check_no_ceremony as _cnc

    _ceremony_exit = _cnc.main()
    if _ceremony_exit:
        return _ceremony_exit

    # ADR-032: consume any reviewer-result/1 blocks present in the mailbox. This is the
    # SCHEMA-VALIDATION half only — it never re-runs pytest (re-running a historical
    # event's pins against today's HEAD would false-alarm; the fabrication re-run is the
    # on-demand `consume_reviewer_result.py <event>` CLI). Zero blocks (today) -> silent 0;
    # a present-but-invalid block hard-fails. Mirrors the check_no_ceremony invocation above.
    import consume_reviewer_result as _crr

    _consume_exit = _crr.smoke_check(_repo_root)
    if _consume_exit:
        return _consume_exit

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
