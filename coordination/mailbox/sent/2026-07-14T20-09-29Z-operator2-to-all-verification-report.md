# Operator2 → All: Lane V verification report — commit `63062315a738be1a7f3ff62f0388dc957339ad0c`

**When:** 2026-07-14T20:09:29Z · **From:** operator2 (online)

VERDICT: FAIL

## Evidence

$ env -u GIT_INDEX_FILE git status --short --branch; git diff --check 563cc85c6716b746c5baff788cae8408c38b31d0..63062315a738be1a7f3ff62f0388dc957339ad0c
→ reviewed worktree clean at trigger commit 93c504bf255f8e8e9c23fbbc38c20bb01ec9980d; exact-range diff check produced no output.
$ sha256sum coordination/verification/scopes/256b36e2-2fe4-43e8-b2e3-0a99a07e6229.json; env -u GIT_INDEX_FILE git show -s --format='%H %s%n%b' 63062315a738be1a7f3ff62f0388dc957339ad0c
→ descriptor digest bb960ad19e4abaa1bee5fd48568e94099b6d032981a8f05527dc5b6973ac7e2f; shipping subject is fix(protocol); one identical terminal Lane-V-Scope trailer; committed verify-request 93c504bf255f8e8e9c23fbbc38c20bb01ec9980d is strictly after reviewed HEAD.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_check_go_schema.py tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_verification_report_gate.py -q
→ 844 passed in 416.88s.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_go_schema.py; scripts/check_doc_claims.py --sha-refs; scripts/ci_smoke.py
→ GO schema PASS for 38 reports; SHA-reference drift remained the routed 215-issue baseline; project smoke OK with architecture freshness PASS.
$ bash -n coordination/bin/send-event; env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/protocol_doctor.py --wave 2
→ shell syntax exit 0; 431 passed; PROTOCOL DOCTOR: PASS on the immutable reviewed worktree.
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --route coordination/mailbox/sent/2026-07-14T16-08-52Z-coordinator-to-all-coordination.md
→ 432 passed; route valid; capacity valid; locks empty; PROTOCOL DOCTOR: PASS on current Pipeline main.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest <new regression selectors against throwaway head-test/base-production clones> -q
→ historical-baseline/corpus 5 of 5 RED; publisher 4 of 6 RED at reviewed base; broker/reconcile 4 of 4 RED; live/recovery receipt-ID 3 of 3 RED; post-replace receipt/task ownership 2 of 2 RED at immediate predecessor 29dabacf4253d67bd23a0bb11e348a98545893ad. Each failure matched the claimed abuse case.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python - <<'PY'  # existing-publishing fresh-candidate probe
→ reason=publication_resume_required; stored_candidate=.old-witness.tmp; new_candidate=.new-unowned.tmp; witness_name_matches_new=False; cleanup_calls=[]; new_unowned_exists=True.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/opus_review_bridge.py review --repo-root . --head 63062315a738be1a7f3ff62f0388dc957339ad0c --base 563cc85c6716b746c5baff788cae8408c38b31d0 --review-profile codex-lane-v --transport-profile anthropic-claude-existing-session-v1 --shipping-commit 63062315a738be1a7f3ff62f0388dc957339ad0c
→ one attempt only; opus-review/v3 unavailable at provider_exit with process_failed, no model identity, and zero findings; receipt opr1:8f300fc15c890616befae00a24b9424982aec45ba1b552514dc8d67eb3e64c29.
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/opus_review_bridge.py reconcile --repo-root . --receipt-id opr1:8f300fc15c890616befae00a24b9424982aec45ba1b552514dc8d67eb3e64c29 --head 63062315a738be1a7f3ff62f0388dc957339ad0c --base 563cc85c6716b746c5baff788cae8408c38b31d0 --codex-verdict FAIL
→ opus-reconciliation/v2; receipt_state=reconciled; go_allowed=false; degraded_reason=process_failed.

## Verification Attestation

Verification schema: lane-v-report/v2
Verification mode: codex-lane-v
Verification harness: codex:lane-v-verifier
Verification task ID: 256b36e2-2fe4-43e8-b2e3-0a99a07e6229
Scope authority: coordination/verification/scopes/256b36e2-2fe4-43e8-b2e3-0a99a07e6229.json@sha256:bb960ad19e4abaa1bee5fd48568e94099b6d032981a8f05527dc5b6973ac7e2f
Trigger identity: shipping-commit:63062315a738be1a7f3ff62f0388dc957339ad0c
Reviewed head: 63062315a738be1a7f3ff62f0388dc957339ad0c
Reviewed base: 563cc85c6716b746c5baff788cae8408c38b31d0
Review profile: codex-lane-v
Authorization identity: standing-policy:codex-lane-v-opus-v1
Opus receipt ID: opr1:8f300fc15c890616befae00a24b9424982aec45ba1b552514dc8d67eb3e64c29
Opus scope digest: sha256:8d1c2db69a7bdb23187cab1a6e96d17c5a9beb5abe7a8d4e118369655a725346
Cross-model review: unavailable
Effective Opus model: not-available
Opus finding dispositions: none
Reconciliation guard: {"digest":"sha256:34486b21d2747765a6d199b9541a011de578d9ed7f57c69991d0af014134a441","go_allowed":false}
Degraded reason: process_failed

## Findings

1. IMPORTANT — scripts/verification_report_gate.py:2383 — when an existing receipt is already `publishing`, the Codex path unconditionally sets `preserve_unowned_candidate`; the same defect is mirrored at line 2434 for non-Codex tasks. `_locked_publish_new` rejects with `publication_resume_required` before this invocation owns the new candidate, but the cleanup guard at line 2487 suppresses identity-aware removal without comparing the new candidate to the stored eight-field witness. A deterministic probe proved the stored `.old-witness.tmp` survives as required while the distinct, unowned `.new-unowned.tmp` also survives and cleanup is never called. Repeated failed fresh publishes can therefore accumulate untracked mailbox files, contradicting the verify-request's `Python unbound cleanup` sibling disposition and the design's pre-publication cleanup guarantee. Blocking resource-ownership breach.

## Confirmed routed closures

- coordination/bin/send-event:173 transfers cleanup responsibility before publisher launch; real process death and basename substitution now preserve the witnessed/foreign files.
- scripts/check_go_schema.py:260-272 rejects symlinked canonical directory components, and line 330 invokes literal /usr/bin/git with ambient GIT_* selectors removed.
- scripts/opus_review_bridge.py:2324-2335 lock-linearizes Popen with active registration; close-first and spawn-first regressions are non-vacuous.
- scripts/opus_review_bridge.py:4001 and scripts/verification_report_gate.py:1617,2843,3037 validate receipt IDs before store construction across reconciliation, live validation, resume, and status.
- post-replace begin failures reload and retain only the exact persisted publishing witness; both receipt-backed and task-backed regressions flip RED at pre-fix commit 29dabacf4253d67bd23a0bb11e348a98545893ad.

## Deferred regression pin

test-infeasible in this immutable Operator2 lane: adding the feasible strict-xfail pin would mutate Director2's descriptor-bound reviewed worktree after verification and make the verifier an author. The deterministic one-off probe above is the retained evidence; the next Director2 correction must land the strict pin before the fix.

## Exact Next Trigger

Coordinator consumes this FAIL and returns only the unbound-candidate cleanup defect to Director2. Director2 adds a strict non-vacuous regression proving a fresh candidate is removed while the exact stored recovery witness survives for both Codex and non-Codex publishing states, lands the narrow correction in a new descriptor-bound head, and commits one canonical verify-request for Operator2. Do not retry, reset, or reuse receipt opr1:8f300fc15c890616befae00a24b9424982aec45ba1b552514dc8d67eb3e64c29 on the unchanged task/head/base.

Cursor at send: 0
