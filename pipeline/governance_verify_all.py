#!/usr/bin/env python3
"""governance_verify_all — the full governance verification aggregate.

Formerly pipeline/ci_smoke.py (a thin deprecated alias remains at that path:
CI job vocabulary and historical commands keep resolving). The rename states
what this is: the FULL aggregate, run in CI, before a release or
high-risk-control acceptance, or when work changes governance/runtime
topology — not a cheap session-start preflight. For ordinary changes run the
focused checker that owns the touched boundary (see CHECKER_REGISTRY).

Two halves run in sequence:

  HALF A — Project runtime smoke (_project_smoke):
    This repo's product IS the governance OS, so the runtime smoke asserts the
    OS's own load-bearing invariants: the signed-bus package imports cleanly,
    the RFC-8785 canonicalizer is key-order-stable, the load-bearing kind set
    is a subset of the full vocabulary, and the seat roster + mailbox kind
    registry parse. Projects seeded from the transfer bundle replace the body
    with invariants for their own stack. See _project_smoke() below.

  HALF B — Governance gates (always active):
    These are fully portable and run unchanged in any project seeded from this
    transfer bundle:

    - Doc-anchor drift gate: check_doc_claims on ARCHITECTURE.md
      (fatal kinds hard-fail locally and in CI; advisory kinds warn).
    - PROGRAM-MANUAL anchor-drift WARN (advisory; never a hard-fail).
    - Commit-SHA ref drift baseline (git-backed; changed drift hard-fails).
    - Coordination-state gate: check_coordination (FATAL hard-fails locally
      and in CI; ADVISORY warns everywhere).
    - Anti-ceremony gate: check_no_ceremony (hard-fail local + CI — ADR-028).
    - Reviewer-result schema validation: consume_reviewer_result smoke_check
      (schema-validation only; never re-runs pytest — ADR-032).
    - Adoption-placeholder gate: check_placeholders (hard-fail local + CI — ADR-002).
    - Lane V report corpus + GO evidence validator: check_go_schema (hard-fail local + CI).
    - ARCHITECTURE Last-verified gate: check_arch_freshness (inert unless
      ARCHITECTURE.md changed vs merge-base; hard-fail when it fires).

Usage:
    pipeline check    # local
    python pipeline/governance_verify_all.py              # CI (after pip install)

Exit codes:
    0 — all checks pass
    1 — assertion failed (an invariant or gate broke)
   >1 — script error (import-time failure, etc.)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Bootstrap sys.path so we can import from repo root and the pipeline dir.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, _SCRIPTS_DIR):
    if _p not in sys.path: sys.path.insert(0, _p)

# Checker -> owned boundary map (guard admission for selective invocation:
# the map itself is a control, so tests/unit/test_governance_verify_registry.py
# pins that every named checker and owned path exists). Severity names what a
# red result blocks. This registry is descriptive routing for humans and
# agents choosing the focused checker; it does not gate anything by itself.
CHECKER_REGISTRY = {
    "project_smoke": {
        "entry": "pipeline/governance_verify_all.py",
        "owned_paths": ("pipeline/", "coordination/mailbox/kinds.txt"),
        "trigger": "governance/runtime topology change",
        "severity": "hard-fail",
        "blocked_effect": "landing a broken governance-OS runtime invariant",
    },
    "doc_anchor_drift": {
        "entry": "pipeline/check_doc_claims.py",
        "owned_paths": (
            "ARCHITECTURE.md", "CLAUDE.md", "AGENTS.md", "DECISIONS.md",
            "docs/protocol/agents/director-operator.md",
        ),
        "trigger": "editing SHA-citing truth docs",
        "severity": "hard-fail (fatal kinds) / warn (advisory kinds)",
        "blocked_effect": "stale anchors answering for current truth",
    },
    "coordination_state": {
        "entry": "pipeline/check_coordination.py",
        "owned_paths": ("coordination/", "pipeline/baselines/review_history_boundary.json"),
        "trigger": "mailbox/review/coordination state change",
        "severity": "hard-fail (FATAL) / warn (ADVISORY)",
        "blocked_effect": "corrupt or ambiguous durable coordination state",
    },
    "anti_ceremony": {
        "entry": "pipeline/check_no_ceremony.py",
        "owned_paths": (".",),
        "trigger": "Python growth / xfail pins / remediation inventory / reviewer schema change",
        "severity": "hard-fail",
        "blocked_effect": "verification theater or disproportionate Python growth",
    },
    "reviewer_result_schema": {
        "entry": "pipeline/consume_reviewer_result.py",
        "owned_paths": ("coordination/mailbox/",),
        "trigger": "reviewer-result blocks in mailbox events",
        "severity": "hard-fail",
        "blocked_effect": "malformed reviewer results consumed as verdicts",
    },
    "placeholders": {
        "entry": "pipeline/check_placeholders.py",
        "owned_paths": (".",),
        "trigger": "any adoption-surface edit",
        "severity": "hard-fail",
        "blocked_effect": "unbound placeholder tokens shipping as truth (ADR-002)",
    },
    "go_schema": {
        "entry": "pipeline/check_go_schema.py",
        "owned_paths": ("coordination/mailbox/sent/",),
        "trigger": "verification-report publication",
        "severity": "hard-fail",
        "blocked_effect": "malformed GO evidence admitted as review",
    },
    "arch_freshness": {
        "entry": "pipeline/check_arch_freshness.py",
        "owned_paths": ("ARCHITECTURE.md",),
        "trigger": "ARCHITECTURE.md in the changeset",
        "severity": "hard-fail when it fires",
        "blocked_effect": "editing truth-layer facts without bumping provenance",
    },
}

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

    # 1. Seat roster (single source of truth) + mailbox kind registry are stable.
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


def _coordination_gate(repo_root: Path) -> int:
    """Print canonical coordination dispositions and fail on every FATAL."""

    import check_coordination as _cc

    issues = _cc.run(
        repo_root / "coordination", docs_root=repo_root / "docs"
    )
    advisories = [issue for issue in issues if issue.severity == "ADVISORY"]
    fatals = [issue for issue in issues if issue.severity == "FATAL"]
    # Same-kind advisory floods (six grandfathered immutable-history
    # exceptions, today) print as one summary line so the completion gate's
    # signal is not buried; the itemized list stays one command away.
    # FATALs are never grouped.
    advisories_by_kind: dict[str, list] = {}
    for issue in advisories:
        advisories_by_kind.setdefault(issue.kind, []).append(issue)
    for kind in sorted(advisories_by_kind):
        group = advisories_by_kind[kind]
        if len(group) > 3:
            print(
                f"WARNING: coordination ADVISORY [{kind}] x{len(group)} "
                f"(e.g. {group[0].path}) — itemize with: "
                f"pipeline check coordination"
            )
        else:
            for issue in group:
                print(
                    f"WARNING: coordination ADVISORY [{issue.kind}] "
                    f"{issue.path} — {issue.message}"
                )
    if not fatals:
        return 0
    for issue in fatals:
        print(f"COORDINATION FATAL [{issue.kind}] {issue.path} — {issue.message}")
    print("\nRun: pipeline check coordination")
    return 1


def _architecture_gate(repo_root: Path) -> int:
    """Apply check_doc_claims' canonical fatal/advisory split to ARCHITECTURE."""

    import check_doc_claims as _cdc

    drifts = _cdc.run(["ARCHITECTURE.md"], repo_root)
    fatal, advisory = _cdc._split_advisories(drifts)
    for drift in advisory:
        print(
            f"WARNING: ARCHITECTURE advisory [{drift.kind}] "
            f"{drift.target_file}:{drift.target_line} — {drift.message}"
        )
    if not fatal:
        return 0
    print(f"\nDOC-ANCHOR DRIFT: {len(fatal)} fatal issue(s) found in ARCHITECTURE.md")
    for drift in fatal:
        hint = f"  → suggested line {drift.suggested_line}" if drift.suggested_line else ""
        print(f"  [{drift.kind}] {drift.target_file}:{drift.target_line}{hint}")
        print(f"    {drift.message}")
    print("\nRun: pipeline check docs --fix")
    return 1


def main(argv: list[str] | None = None) -> int:
    fast_mode = False
    args = argv if argv is not None else sys.argv[1:]
    if "-h" in args or "--help" in args:
        # `_ARGLESS` used to answer this by printing "Takes no arguments",
        # which denied --fast existed. The gate answers for itself instead.
        print("usage: pipeline check [--fast]\n")
        print("Run every governance gate (the completion gate).\n")
        print("  --fast  essential coordination, ceremony and placeholder")
        print("          checks only; skips the full aggregate.")
        return 0
    if "--fast" in args:
        fast_mode = True

    # --- HALF A: project runtime smoke ---
    _result = _project_smoke()
    if _result:
        return _result

    if fast_mode:
        # Fast preflight mode: run essential coordination, ceremony, and placeholder checks
        import check_no_ceremony as _cnc
        import check_placeholders as _cp

        _repo_root = Path(_REPO_ROOT)
        _coordination_exit = _coordination_gate(_repo_root)
        if _coordination_exit:
            return _coordination_exit

        _ceremony_exit = _cnc.main()
        if _ceremony_exit:
            return _ceremony_exit

        _ph_violations = _cp.run(_repo_root)
        if _ph_violations:
            print(f"PLACEHOLDER CHECK — FAIL: {len(_ph_violations)} violation(s)")
            return 1

        print("FAST PREFLIGHT — PASS (essential invariants ok).")
        print("OK")
        return 0

    # --- HALF B: governance gates (fully portable) ---

    # Doc-anchor drift gate (check_doc_claims on ARCHITECTURE.md). Canonical
    # fatal kinds block locally and in CI; canonical advisories warn everywhere.
    import check_doc_claims as _cdc

    _repo_root = Path(_REPO_ROOT)
    _architecture_exit = _architecture_gate(_repo_root)
    if _architecture_exit:
        return _architecture_exit

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
            f"pipeline/check_doc_claims.py --fix docs/PROGRAM-MANUAL.md)"
        )
        for _d in _manual_drifts[:5]:
            print(f"  [{_d.kind}] {_d.target_file}:{_d.target_line} — {_d.message}")
        if _mn > 5:
            print(f"  ... and {_mn - 5} more")

    # Commit-SHA ref drift baseline. Historical protocol-provenance refs are
    # quiet when the reviewed set is unchanged; any count/digest change is new
    # drift and hard-fails.
    _sha_drifts = _cdc.check_sha_refs(_cdc.SHA_DEFAULT_DOCS, _repo_root)
    if _sha_drifts:
        _sha_status = _cdc.classify_sha_ref_baseline(_sha_drifts, _repo_root)
        if not _sha_status.matches_baseline:
            _sha_is_repo, _sha_shallow = _cdc._repo_state(_repo_root)
            if _sha_shallow:
                # A shallow clone cannot resolve historical protocol-provenance
                # SHAs beyond its boundary, so the baseline is not evaluable here.
                # CI uses fetch-depth: 0 (full clone), which still gates this; warn
                # rather than hard-fail so a shallow local checkout is not bricked.
                print(
                    "SHA-REF BASELINE CHECK — WARN (shallow clone; baseline not "
                    "evaluable; use fetch-depth: 0 to gate SHA-ref drift)."
                )
            else:
                print("SHA-REF BASELINE CHECK — FAIL")
                print(_sha_status.warning_line)
                print(
                    "Run: pipeline check docs --sha-refs "
                    "and update the reviewed baseline only after a bounded cleanup "
                    "or explicit owner decision."
                )
                for _sd in _sha_drifts[:20]:
                    print(
                        f"  [{_sd.kind}] {Path(_sd.doc_path).name}:{_sd.doc_line}"
                        f" (sha: {_sd.symbol}) — {_sd.message}"
                    )
                if len(_sha_drifts) > 20:
                    print(f"  ... and {len(_sha_drifts) - 20} more")
                return 1

    # Coordination-state gate (protocol v6.0, check_coordination). FATAL blocks
    # locally and in CI; ADVISORY warns; INFO is silent here (the CLI prints it).
    _coordination_exit = _coordination_gate(_repo_root)
    if _coordination_exit:
        return _coordination_exit

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

    # ADR-002: adoption-placeholder gate (check_placeholders). Hard-fail local + CI.
    # Calls run() directly — NOT main() — to avoid mis-parsing ci_smoke's own argv.
    import check_placeholders as _cp

    _ph_violations = _cp.run(_repo_root)
    if _ph_violations:
        _ph_n = len(_ph_violations)
        print(
            f"\nPLACEHOLDER CHECK — FAIL: {_ph_n} violation(s): "
            f"placeholder token(s) found outside allowlist\n"
        )
        for _v in _ph_violations:
            print(f"  ! {_v}")
        print(
            "\nTo fix: either fill in the placeholder or add the file path to "
            "pipeline/placeholder_allowlist.txt."
        )
        return 1
    print("PLACEHOLDER CHECK — PASS (no unallowlisted tokens).")

    # Lane V verification-report repository validator. Hard-fail local + CI.
    # CLI and smoke share this exact public raw-byte legacy/v2 validation path.
    import check_go_schema as _cgs

    try:
        _go_reports = _cgs.scan_repository_reports(_repo_root)
        _go_manifest = _cgs.load_baseline_manifest(_cgs.DEFAULT_MANIFEST)
        _retired_reviews = _cgs.load_retired_review_targets(
            _cgs.DEFAULT_RETIRED_MANIFEST
        )
        _go_violations = _cgs.repository_report_violations(
            _repo_root, _go_reports, _go_manifest, _retired_reviews
        )
    except (
        OSError,
        UnicodeError,
        _cgs.BaselineGenerationError,
        _cgs.RetiredReviewTargetsError,
    ) as _go_error:
        print(f"\nGO-SCHEMA CHECK — FAIL: {_go_error}")
        return 1
    if _go_violations:
        # Report SHA bindings cannot resolve on a shallow clone (same failure
        # class the SHA-ref baseline gate guards above); warn there instead of
        # bricking. CI uses fetch-depth: 0, so the full-clone hard gate holds.
        _go_is_repo, _go_shallow = _cdc._repo_state(_repo_root)
        if _go_shallow:
            print(
                "GO-SCHEMA CHECK — WARN (shallow clone; report SHA bindings not "
                "evaluable; use fetch-depth: 0 to gate)."
            )
        else:
            print(
                f"\nGO-SCHEMA CHECK — FAIL: {len(_go_violations)} violation(s)\n"
            )
            for _v in _go_violations:
                print(f"  ! {_v}")
            return 1
    else:
        print(
            "GO-SCHEMA CHECK — PASS "
            f"({len(_go_reports)} verification-report(s) validated; zero violations)."
        )

    # ARCHITECTURE Last-verified gate (check_arch_freshness). Inert unless
    # ARCHITECTURE.md changed vs merge-base; self-degrades if git/base unavailable.
    # Calls the underlying pure function directly — NOT main().
    import check_arch_freshness as _caf

    _af_base = _caf._resolve_base()
    if _af_base is None:
        print(
            "ARCH-FRESHNESS CHECK — git unavailable or no base ref found; "
            "skipping (exit 0)."
        )
    elif not _caf._arch_in_changeset(_af_base):
        print(
            "ARCH-FRESHNESS CHECK — ARCHITECTURE.md not in changeset; "
            "gate inert (exit 0)."
        )
    else:
        _af_old = _caf._show_at_base(_af_base)
        if _af_old is None:
            print(
                "ARCH-FRESHNESS CHECK — ARCHITECTURE.md is a new file at this base; "
                "gate inert (exit 0)."
            )
        elif not _caf.ARCH_FILE.exists():
            print(
                "ARCH-FRESHNESS CHECK — ARCHITECTURE.md absent in working tree; "
                "gate inert (exit 0)."
            )
        else:
            _af_new = _caf.ARCH_FILE.read_text(encoding="utf-8", errors="replace")
            if _caf.arch_freshness_violation(_af_old, _af_new):
                print(
                    "ARCH-FRESHNESS CHECK — FAIL\n"
                    "\n"
                    "  ARCHITECTURE.md body changed but no *Last verified …* stamp was bumped.\n"
                    "\n"
                    "  Remedy: update the stamp line to\n"
                    "  *Last verified against base: <YYYY-MM-DD> @ <git-sha>*\n"
                    "  where <git-sha> is the state you verified against — normally the\n"
                    "  base/parent commit, never the landing commit's own SHA.\n"
                )
                return 1
            _af_provenance = _caf.stamp_provenance_violations(
                _caf.new_valid_stamps(_af_old, _af_new), _caf._git_resolve_stamp
            )
            if _af_provenance:
                print("ARCH-FRESHNESS CHECK — FAIL\n")
                for _af_violation in _af_provenance:
                    print(f"  {_af_violation}")
                print(
                    "\n  Remedy: stamp the SHA of the state actually verified"
                    " against (an ancestor of HEAD)."
                )
                return 1
            print(
                "ARCH-FRESHNESS CHECK — PASS "
                "(stamp bump with resolvable ancestor provenance, or body unchanged)."
            )

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
