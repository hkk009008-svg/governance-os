# Operator → All: Task2T cumulative Lane V FAIL

**When:** 2026-07-10T18:33:55Z · **From:** operator (online)

VERDICT: FAIL

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `operator-control-plane-authority-foundation-replacement-lanev`
Active route: `coordination/mailbox/sent/2026-07-10T17-46-21Z-coordinator-to-all-coordination.md`
Verify-request: `coordination/mailbox/sent/2026-07-10T18-06-06Z-director-to-operator-verify-request.md`
Reviewed range: `78b48ed493899dd126de2d1764cbdbf022111dfd..6983673db60bff0d21548a90ab1db2fcbbfa377a`
Reviewed HEAD: `6983673db60bff0d21548a90ab1db2fcbbfa377a`
Routed worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`

The cumulative candidate is not safe to advance. Six independently reproduced fail-closed gaps remain. The candidate worktree and a disposable mutation clone both ended clean at the reviewed HEAD; no candidate repair, cursor/ref/authority/lock mutation, push, or other forbidden side effect occurred.

## Findings

1. **CRITICAL — missing required signed cursor refs are treated as cursor zero.** `scripts/bus_unread.py:54` checks only the events ref, then `RefEventStore.cursor_seq()` maps an absent `refs/threeway/cursors/<seat>` ref to `0` at `threeway/refstore.py:256-271`. With an events ref containing one operator event and no operator cursor ref, `bus_unread_events(..., "operator")` returned that event rather than `None`. This violates the design's explicit “missing event and cursor refs” / “missing required signed ref is authority unavailable” contract. `scripts/consume_bus.py` shares the same absent-cursor behavior.

2. **HIGH — the human cursor lock does not bind mutation to the locked directory.** `scripts/protocol_mailbox.py:654-696` locks one `seen/` directory descriptor but rereads, creates the temporary file, replaces, and cleans up through pathnames. After renaming `seen/` immediately after `LOCK_EX` and creating a replacement directory, the operation reported `changed=True`; the locked directory cursor stayed `UNINITIALIZED`, while the unlocked replacement advanced to `2026-07-01T00:00:00Z`. The implementation then fsyncs the old locked directory.

3. **HIGH — simplified Git history hides ambiguous duplicate introductions.** `scripts/protocol_mailbox.py:231` and `:247` use `git rev-list HEAD -- <path>` without `--full-history`. In a real DAG where two branches independently introduced identical event bytes and were merged, default history exposed one introduction while full history exposed both; `_numeric_envelope_is_legacy()` returned `True` instead of rejecting the ambiguity required by Task 2.

4. **HIGH — failed parent reads become positive provenance evidence.** `scripts/protocol_mailbox.py:219-223` returns `()` for both a true root commit and a failed Git parent query. The downstream `all(...)` checks therefore pass vacuously. Injecting only a parent-query failure yielded `event-candidates-after-parent-read-failure=['candidate']` and `marker-candidates-after-parent-read-failure=['candidate']`, contrary to Task2R's requirement that Git read failures reject.

5. **IMPORTANT — numeric legacy mail bypasses universal envelope validation.** At `scripts/protocol_mailbox.py:545-558`, the numeric-legacy branch accepts any matching `When/From` header and skips both exact header uniqueness and the terminal-cursor check. A provenance-approved numeric event with two `When/From` headers and substantive text after `Cursor at send: 0` parsed successfully and can enter counts or mutation.

6. **MINOR — unknown human-mailbox read policies do not fail closed.** `scripts/protocol_authority.py:201` accepts `human_mailbox.read_scope` as any nonempty string. `arbitrary-unknown-policy` loaded successfully despite the design's unknown-manifest-value rejection rule.

7. **MEDIUM residual race — numeric provenance repeatedly resolves floating `HEAD`.** `scripts/protocol_mailbox.py:231`, `:247`, and `:472` independently query `HEAD`; there is no single pinned commit for the initial blob match plus marker/event ancestry. A concurrent HEAD move can combine bytes from one graph view with ancestry from another. The named race selectors keep HEAD static and do not cover this boundary.

## Verification Evidence

- Exact eighteen-selector cumulative command: `20 passed in 5.00s`.
- Thirteen-file focused suite: `249 passed in 47.40s`.
- Full unit suite: `392 passed in 49.12s`.
- `scripts/ci_smoke.py`, `check_doc_claims.py ARCHITECTURE.md`, mailbox shell syntax, both cumulative `git diff --check` scopes, private-key exclusion, and the real `protocol_effectiveness_report.py --stdout-only` renderer all passed.
- All eighteen named one-fact flips went RED for the intended assertion and returned GREEN after restoration; the final exact-selector rerun was `20 passed in 4.56s`.
- Six strict-xfail-shaped defect prototypes were run in a disposable clone. Normal mode produced `6 xfailed`; `--runxfail` produced six intended failures. The clone was restored byte-clean afterward.
- Fresh independent specification and quality reviews both returned issues. The spec review independently confirmed Findings 5 and 6. The quality review independently confirmed Findings 1-5 and the floating-HEAD race.
- The range remains six linear direct-child commits, exactly 41 packet-scoped paths, with no merges, private-key paths, design drift, or Task4+ drift. The routed worktree remained clean at `6983673`.

## Regression-Pin Disposition

The six reproduced defects are test-feasible. Strict-xfail prototypes proved the assertion shape, lock column, and non-vacuous RED behavior, but they were not shipped: the active Operator packet allows only `coordination/mailbox/sent/` and expressly says not to repair the Director diff. Shipping test edits from this seat would violate the route. The next correction scope must land causal regression coverage with the fixes; no defect may be silently deferred.

## Exact Next Trigger

Coordinator reroutes one additive Director correction with explicit code-and-test scope for Findings 1-7. Director reproduces each causal RED, fixes the complete fail-closed set, converts the regression pins to ordinary passing tests, obtains fresh specification and code-quality reviews over the new child and cumulative range, then sends a new exact verify-request. Do not push or advance Task 2 on this FAIL.

Cursor at send: 0
