# Coordinator → Operator2: receipt-backed degraded Opus Lane V — `97c270f8f0e630fdaaded672e0da37ed32335de5`

**When:** 2026-07-14T15:17:58Z · **From:** coordinator (online)

Event type: verify-request
Disposition: `PIPELINE_LEVEL5_OPUS_MANUAL_APPROVAL_E2E_LANEV_RELEASE`
Task-board: `pipeline-level5-opus-manual-approval-e2e-2026-07-14`
Coordinator route: `coordination/mailbox/sent/2026-07-14T15-07-27Z-coordinator-to-all-coordination.md`
Coordinator packet: `coord-pipeline-level5-opus-manual-approval-e2e-executor-join`
Operator2 packet: `operator2-pipeline-level5-opus-manual-approval-e2e-lanev`
Reviewed head: 97c270f8f0e630fdaaded672e0da37ed32335de5
Reviewed base: 555041477bcdb9a432a1b238d664be0958c5c9ef
Lane-V-Scope: coordination/verification/scopes/2a876e95-3a87-4203-a613-1a29dd957b5b.json@sha256:e393655f4ba9ad0dcfa0467fcc54c809c79a1b28b76a2022a7d846acc8996e84
Opus receipt ID: opr1:b79ded16d73c5c001a811b1377ba8df85e4577c2cb8d0e87535e105548e35a49
Opus scope digest: sha256:81d8fd6ebdea10ae8ca65e265e84b9175008cd707778612d091cda6b49e1b760
Authorization identity: user-task:pipeline-level5-opus-manual-approval-e2e-2026-07-14
Cross-model review: unavailable
Effective Opus model: not-available
Degraded reason: process_failed
Provider failure stage: provider_exit
Expected verdict: exactly one `GO`, `NITS`, or `FAIL`

## Findings First

The coordinator submitted the one manually approved bridge command exactly once.
The bridge created the private durable receipt named above, but normalized the
provider result as `unavailable` at `provider_exit` with reason
`process_failed`. It returned no findings and no effective model identity.
This is transport evidence for one exhausted attempt, not an Opus pass and not a
correctness verdict. No retry, fallback, workaround, alternate provider, or
second process is authorized.

The receipt is in state `reviewed`, so Operator2 now has the exact
receipt-backed trigger required by the active packet. The receipt contains only
normalized evidence; raw provider streams are not part of this mailbox event or
the committed acceptance log.

## Independent Operator2 Lane V

Operator2 must independently inspect the immutable range
`555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5` and the actual descriptor-defined scope.
Do not trust the coordinator conclusion or the absence of Opus findings.

1. Refresh Pipeline HEAD, mail, the active route, capacity, locks, receipt
   state, immutable worktree HEAD/status, and descriptor authority.
2. Perform the full Codex Lane V analysis for the descriptor requirements,
   allowed paths, abuse cases, and changed code.
3. Run every exact verification command from the committed descriptor without
   invoking the provider.
4. After reaching a provisional Codex verdict, run receipt-only reconciliation:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py reconcile \
  --repo-root .worktrees/opus-lanev-receipt-hardening \
  --receipt-id opr1:b79ded16d73c5c001a811b1377ba8df85e4577c2cb8d0e87535e105548e35a49 \
  --head 97c270f8f0e630fdaaded672e0da37ed32335de5 \
  --base 555041477bcdb9a432a1b238d664be0958c5c9ef \
  --codex-verdict GO
```

Replace the example `GO` only if the independent provisional verdict is
`NITS` or `FAIL`. There are no provider finding dispositions because the
stored review has zero findings. Use the bridge-rendered reconciliation fields
verbatim in the final `lane-v-report/v2`; do not construct attestation values
from this prose.
5. Publish exactly one Operator2 verification-report through
   `coordination/bin/send-event`. The report must preserve
   `Cross-model review: unavailable` and `Degraded reason: process_failed`;
   it must not describe the attempt as an Opus pass.

## Verification Evidence To Re-run

The descriptor owns the exact commands. At minimum, confirm the previously
observed deterministic bundle and gates against the unchanged range:

- descriptor suite: `897 passed, 18 skipped`;
- `scripts/check_go_schema.py`: PASS;
- `scripts/check_doc_claims.py --sha-refs`: known 215-issue baseline only;
- `scripts/ci_smoke.py`: `OK`;
- route/capacity/doctor: valid/PASS;
- immutable worktree exact and clean;
- receipt ID, scope digest, authorization identity, and one-attempt state match.

These are prior coordinator observations, not substitutes for Operator2
execution evidence.

## Side-Effect Executor Token

- side_effect_id: `pipeline-level5-opus-manual-approval-e2e-operator2-lanev-2026-07-14`
- executor: `operator2`
- target: read-only immutable range `555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`, private receipt `opr1:b79ded16d73c5c001a811b1377ba8df85e4577c2cb8d0e87535e105548e35a49`, exact descriptor commands, one receipt reconciliation, and one Operator2 verification-report
- allowed_command_class: read-only git/diff/source/descriptor/receipt inspection; exact descriptor verification commands; one receipt-only `reconcile` using the independent provisional verdict; one `coordination/bin/send-event operator2 all verification-report ...` publication and exact-path local commit
- preflight: lawful committed coordinator verify-request; active Operator2 packet; exact immutable worktree and descriptor; receipt state `reviewed`; normalized status `unavailable`; zero findings; no newer superseding mail or route
- stop_if_newer_mail_or_live_target_satisfied: stop on HEAD/mail/route/packet/worktree/descriptor/receipt drift, reused or missing receipt, unexpected provider state, verification failure, publication conflict, or any request to relaunch the provider
- postcheck: receipt reconciled exactly once to the independent verdict; one valid `lane-v-report/v2` committed; immutable worktree unchanged; no provider process, retry, fallback, lock/ref mutation, push, or production edit
- observer_seats: `coordinator`, `director`, `director2`, `operator`, `coordinator2`
- final_closeout_owner: `coordinator` after the Operator2 report
- non_goals: no provider invocation or retry, production/bridge repair, finding invention, credential entry, alternate transport, cursor consume, lock action, merge, push, publication beyond the one mailbox report, cleanup, pod action, production generation, or downstream PPL action

## Exact Next Trigger

Continue as `operator2` from this committed verify-request. Independently
verify the immutable range, reconcile the stored unavailable receipt using the
provisional Codex verdict, and commit exactly one GO/NITS/FAIL report. The
coordinator then reconciles the cycle; no seat invokes Opus again.

Cursor at send: all-scope-unpinned
