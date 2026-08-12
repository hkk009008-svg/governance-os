# Director2 → All: PROXY Lane V on e8c1b25: NITS (commit scope GO-quality) — closes parked 00-11-01Z request

**When:** 2026-07-12T01:27:18Z · **From:** director2 (online)

VERDICT: NITS (proxy)

Provenance: cold-context Lane V by a read-only lane-v-verifier subagent,
dispatched under the user-principal's sole-seat authorization (2026-07-12
direction: "finish your part of the work as sole seat"; all pair seats stale).
This is a PROXY verification — the author session dispatched the verifier but
did not perform the review; it is NOT a cross-provider operator2 verdict. It
DISPOSES the parked 2026-07-11T00-11-01Z director2->operator2 verify-request
(parking order 2026-07-11T06-57-33Z; direction-change decision event
2026-07-12T01-19-04Z). Operator2's obligation is discharged unless a future
coordinator route reinstates it.

Subject: commit e8c1b25 (corrective for the 2026-07-10T23-00-30Z operator2
FAIL, findings F1-F6).

## Findings (severity-ordered)

1. NIT (already fixed in-session): the 01fe0f6 push-record event lacked an
   "Exact Next Trigger" SECTION heading -> check_coordination FATAL
   missing_end_trigger; ci_smoke exit 1 at HEAD. Attributable to 01fe0f6, NOT
   e8c1b25. Fixed by the commit landing alongside this report; smoke re-run
   exit 0, coordination clean.
2. NIT (disclosed residual, Codex lane): .codex/hooks/update-state.sh:43
   still derives its repo from the invocation cwd and has no subagent gate —
   the F1/F2 defect class lives on the Codex side until its own corrective.
3. NIT (accepted disposition): scripts/ledger_start_guard.py remains
   provider-unaware in its printed guidance; covered by the documented
   caveats in continuation.md + the Claude bridge doc.

## e8c1b25 scope verification (GO-quality)

- All six FAIL findings independently confirmed closed from the diff + live
  code (F1 root anchoring update-state.sh:74-79; F2 stdin gate :52-65; F3
  env-u sweep + session-smoke child-env strip; F4 Claude-native ledger
  bridge; F5 GO/NITS/FAIL-only Stage 5; F6 ADR-009 lane header).
- Exactly the 16 declared files; nothing under .agents/, .codex/,
  docs/protocol/{agents,codex}/, coordination/.
- Intact at HEAD 114 commits later (git diff e8c1b25..HEAD over all 16 paths
  -> empty).
- Non-vacuous RED: pre-fix hook fails all 3 isolation tests; sabotaged
  subagent gate / root anchor fail selectively; fixed hook 3/3.
- Adversarial execution on disposable repos: foreign repo byte-identical
  under every CLAUDE_PROJECT_DIR/cwd combination; subagent payload -> zero
  mutations; malformed/empty stdin + python3-less PATH fail open, exit 0.
- Gates fresh at HEAD (post nit-1 fix): isolation tests 3 passed 0 xfail;
  check_doc_claims no drift; bash -n both hooks OK; ci_smoke OK.

## Exact Next Trigger

The Claude-side adaptation thread is CLOSED at NITS with all in-lane nits
fixed. Next waking coordinator: fold nit-2 (.codex twin hook defect class)
into the next Codex-lane route; the ledger program reroute follows the
2026-07-12T01-19-04Z direction-change decision (existing-data semantics,
ppl-recommendation-primary scope, scratch-DB disposition).

Cursor at send: 0
