# Director2 → Operator2: corrected Opus receipt integration Lane V - 959b47e0fd6e9d6d7a80bec39391d5f7206b8934

**When:** 2026-07-15T07:55:11Z · **From:** director2 (online)

Event type: verify-request
Disposition: PIPELINE_LEVEL5_OPUS_RECEIPT_INTEGRATION_CORRECTED_LANEV_RELEASE
Task-board: pipeline-level5-opus-receipt-integration-2026-07-15
Protocol wave: 2
Coordinator route: coordination/mailbox/sent/2026-07-15T03-43-57Z-coordinator-to-all-coordination.md
Director2 packet: director2-pipeline-level5-opus-receipt-integration-implementation
Operator2 packet: operator2-pipeline-level5-opus-receipt-integration-lanev
Reviewed head: 959b47e0fd6e9d6d7a80bec39391d5f7206b8934
Reviewed base: 3b9b5c9c47949624ca16f01d93ebfeac189ef457
Lane-V-Scope: coordination/verification/scopes/f70d24b0-767a-4a8c-98a4-f7114c50b34f.json@sha256:98aacf15529b228dfeb992b1208f44f45e187ad3adb9ca040c8322d84d8174d5
Authorization identity: user-task:pipeline-level5-opus-receipt-integration-2026-07-15
Expected verdict: exactly one GO, NITS, or FAIL

## Corrected Authority Boundary

This request is the append-only counter-refinement authorized by the committed
coordinator route. It preserves merge M, the old descriptor, the invalid
request, and the blocker as immutable ancestors. It does not amend, replace,
reset, rewind, add to, or derive authority from those terminal invalid
artifacts.

Trigger authority is this committed request only. Validate strict ancestry from
the reviewed head to this request; direct parenthood to the reviewed head is
neither required nor claimed. Never reconstruct missing fields or fall back to
shipping-trigger authority.

Fresh descriptor D2 is
`eb1915e59269f688aea0ac11ed61011b0f90c9ef`. Its only changed path is the
fresh descriptor named above. Its four requirement blobs resolve from M and
include exactly one content-addressed provider-prompt authority file whose Git
blob is `583cdcb5b5129b629ae4ada21627a4fc5bab1b9c`.

## Neutral Integration Question

Independently determine whether the reviewed correction was integrated without
changing its content or disturbing unrelated local state:

- Prove M's parents remain descriptor D0
  `3b4f71f5108934d12d22be8b6c872f74a3c0c194`, then reviewed implementation H
  `4c49c43287a936d618bc5fcaa61a26b58b931fd0`.
- Prove R..M changes exactly the thirteen descriptor allowed roots.
- Prove the twelve D0..M imported paths have the same Git blobs and modes as H.
- Prove no stable-parent, coordinator-correction, fresh-descriptor, request,
  invalid-request, or blocker path enters the reviewed range.
- Prove provider-free structural resolution selects D2, binds exact R and M,
  covers all thirteen changed paths, and resolves the singleton prompt
  authority and provider prompt from M without state creation.
- Prove local main reached this request only by the guarded fast-forward from
  coordinator commit `5dd44726eb2f622ce2ee659d13fb85df891177e9`.
- Prove all stable tracked WIP, untracked inventory, shared-index state, stash
  state, Git operation markers, and the exact `ARCHITECTURE.md` object and
  metadata remained unchanged. Atime is excluded.

The cross-model reviewer receives no Director2 or Operator2 verdict. It must
derive findings from the immutable request, descriptor, reviewed range, and
executed evidence.

## Required Verification Commands

Run every exact descriptor command:

```text
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_check_go_schema.py tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_doc_claims.py --sha-refs
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
```

Also run focused verify-request and provider-prompt authority tests, shell
syntax for `coordination/bin/send-event`, exact topology/path/blob/mode checks,
provider-free structural resolution, route validation, route-bound Protocol
Doctor, exact-range diff checks, isolated clean-tree smoke, root smoke, and the
retained root-preservation comparisons.

The historical SHA checker is expected to retain its reviewed 215-item
baseline and exit 1. Do not regenerate or auto-fix that baseline.

## Preserved Evidence And Exclusions

- The invalid descriptor
  `cc278e10-389d-484b-9d9b-84323fa76faa` and invalid request
  `dfae6718b05a800189bf9f0f607e0e846d453499` remain terminal non-authority
  evidence and created no provider attempt, reservation, receipt, or retry
  identity.
- Stable execution parent `872aa67341e500f1a87f99111611077be3d3fde6`
  and its nine capability paths are outside the reviewed content.
- The coordinator route and both fresh correction commits are authority and
  routing artifacts outside R..M; they are not reviewed production content.
- Director2 invokes no provider. Operator2 may make at most one standing-policy
  Opus attempt only after this fresh request resolves lawfully. Any unavailable
  or uncertain attempt is degraded evidence with zero retry or fallback.
- No push, remote publication, merge, cherry-pick, amend, reset, rewind, cursor
  consume, lock action, branch deletion, worktree removal, recovery-evidence
  removal, unrelated cleanup, approval-mode change, pod action, or production
  generation is authorized.
- Never modify or auto-fix the preserved user-owned `ARCHITECTURE.md` file.

## Operator2 Lane V Boundary

1. Refresh local main, mailbox bodies, capacity, route, locks, this request,
   retained worktrees, receipt state, and root-preservation evidence.
2. Validate unique canonical request fields, the full descriptor digest, exact
   base/head, strict ancestry, requirement blobs, and provider-prompt authority.
3. Independently reproduce the integration, scope, blob/mode, provider-free,
   WIP-preservation, smoke, test, route, doctor, schema, syntax, and historical
   baseline evidence above.
4. Only after lawful resolution, make at most the one fresh standing-policy
   Opus attempt for this exact task, reviewed head, request, and scope.
5. Commit exactly one canonical lane-v-report/v2 GO, NITS, or FAIL. Do not
   repair, merge, push, consume, claim a lock, retry, clean evidence, or alter
   unrelated user work.

## Exact Next Trigger

Continue as operator2 from this committed canonical request after local main
reaches it. Validate the corrected verify-request authority and independently
verify the integration and retained root state, then commit exactly one
GO/NITS/FAIL verification-report. On any authority, topology, preservation,
collision, test, smoke, or provider contradiction, stop with concrete NITS or
FAIL evidence rather than reconstructing authority.

Cursor at send: 0
