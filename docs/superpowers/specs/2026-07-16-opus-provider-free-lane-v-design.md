# Opus Provider-Free Lane V Design

**Date:** 2026-07-16
**Owner:** dedicated Opus readiness bridge
**Bound base:** `59eb9d4a19bc200d372b6aa489df6d53a0c08d14`

## Problem

Opus Stage A intentionally permits zero provider attempts and zero receipt
mutations while Operator2 verifies the bridge repair. The public report gate,
however, currently treats every `codex-lane-v` report as receipt-backed. A
truthful provider-free report cannot satisfy the required receipt ID, scope
digest, reconciliation, model, and degraded-reason fields, so publication
fails closed.

The existing `claude-lane-v` path is also unsuitable: the verifier is Codex,
not Claude. Free-text route prose such as a provider budget of zero cannot
select a weaker publication path because it is not authenticated schema.

## Decision

Add one exact verifier tuple for committed provider-free Codex authority:

```text
verification_mode    = codex-provider-free-lane-v
verification_harness = codex:lane-v-verifier
review_profile       = codex-provider-free-lane-v
```

This mode is distinct from both existing modes:

- `codex-lane-v` remains receipt-backed and unchanged.
- `claude-lane-v` remains Claude-attributed and unchanged.
- `codex-provider-free-lane-v` is Codex-attributed, prohibits provider receipt
  state, and uses the existing task-publication transaction.

The current Stage-A descriptor is ordinary `codex-lane-v` and receives no
grandfathering. After this implementation is verified, the coordinator must
issue an append-only authority correction with a fresh provider-free
descriptor and canonical verify-request while preserving the reviewed
`R..Q2` range.

## Authority Separation

Descriptor authority and provider receipt scope must use separate verifier
allowlists.

`ScopeDescriptor.from_mapping()` may accept all three exact tuples because a
committed descriptor selects the verification contract. `ReviewScope` and
receipt reservation may accept only the existing receipt-capable
`codex-lane-v` tuple (plus any already-supported receipt semantics); the new
provider-free tuple must be rejected before a receipt or lock can be created.

This separation prevents a provider-free descriptor from becoming a
representable provider attempt. Adding the tuple to the existing shared
verifier allowlist without this split is forbidden.

## Report Contract

A provider-free report retains the complete `lane-v-report/v2` field order.
The first eight structural fields bind the committed descriptor, trigger,
reviewed range, task, and Codex harness. `Review profile` must equal
`codex-provider-free-lane-v`. Every field from `Authorization identity`
through `Degraded reason` must equal the literal `not-applicable`.

Any receipt ID, scope digest, cross-model result, model name, finding
disposition, reconciliation guard, authorization identity, or degraded reason
in provider-free mode is rejected. Conversely, ordinary `codex-lane-v` still
rejects `not-applicable` receipt fields.

Structural validation compares the report mode, harness, and profile with the
exact committed descriptor tuple. Unknown or mixed tuples fail closed.
Verify-request sender/recipient enforcement remains common across all modes.

## Publication Data Flow

Publication selects its backend from an exact mode classification:

```text
codex-lane-v
  -> ReceiptStore
  -> reconciled Opus receipt validation
  -> receipt-backed publication/resume/status

claude-lane-v | codex-provider-free-lane-v
  -> TaskPublicationStore
  -> committed authority digest validation
  -> task-backed publication/resume/status

anything else
  -> reject
```

No generic “not Codex means task publication” fallback remains. The task
authority digest binds repository identity, descriptor path and digest, trigger
identity, reviewed range, verification mode, harness, task ID, and the
authorized operator recipient; it does not include the report body. Exact
report bytes are bound later by the publication witness's candidate digest.
Provider-free publication must never call a receipt-store factory.

## Failure And Recovery

The existing `ready -> publishing -> published` task transaction, candidate
inode/digest witness, stage-zero index checks, durability barriers, resume, and
status behavior remain unchanged. A task-authority collision fails closed.

Provider-free mode creates no provider attempt, receipt, or receipt lock.
Unknown modes, mixed verifier tuples, receipt-bearing provider-free reports,
and descriptor/report mismatches fail before publication.

## Post-Integration Hosted E2E Amendment

The first hosted run after integrating `main` exposed one Opus-owned Python
3.13 compatibility defect. The repository config promotes warnings to errors,
while `_extract_review_archive()` called `TarFile.extractall()` without an
explicit filter. Python 3.13 therefore raised its archive-filter
`DeprecationWarning`. That single defect produced 36 Opus bridge failures: 35
direct warning failures and one provider result normalized to `unavailable`.

An independent security review traced the archive to exact local `git archive`
output and confirmed that the existing all-members-first validation must stay.
It rejects absolute paths, any `..` component, `.git` members, symlinks,
hardlinks, and special entries before extraction. The narrow repair passes the
exact `tarfile.data_filter` callable to `extractall()`. The data filter adds
destination-realpath containment and safe permission/ownership normalization;
it does not replace the stricter existing checks.

The bridge must fail closed with `ReviewContractError(reason="invalid_scope")`
before extraction if `tarfile.data_filter` is absent or not callable. Warning
suppression, `fully_trusted`, a CI Python-version change, and a broader archive
refactor are forbidden.

The repair must preserve regular-file bytes and the owner executable bit, pin
unsafe-member rejection, and execute focused coverage under Python 3.11, 3.13,
and 3.14. Hosted success is exact: the 36 Opus failures disappear while the
four unrelated unit failures remain unchanged (two ledger-path assertions and
two missing-trigger-object/smoke assertions). The CI workflow, ledger paths,
trigger objects, xfail policy, mailbox, receipts, and `main` remain untouched.

## Required Coverage

1. Accept the exact provider-free descriptor tuple.
2. Reject every mixed provider-free mode/harness/profile tuple.
3. Reject provider-free `ReviewScope` and receipt reservation before any
   receipt or lock file exists.
4. Parse the canonical provider-free report shape.
5. Reject each non-`not-applicable` provider field in provider-free mode.
6. Preserve ordinary Codex rejection of `not-applicable` receipt fields.
7. Prove free-text zero-provider prose cannot downgrade ordinary Codex mode.
8. Reject provider-free reports against ordinary Codex or Claude descriptors,
   and reject the inverse mismatches.
9. Preserve verify-request recipient enforcement for both trigger kinds.
10. Prove live validation and publication use `TaskPublicationStore` while a
    bomb `ReceiptStore` factory is never called.
11. Exercise task publication, resume, status, and authority-collision paths.
12. Prove unknown future modes never default to task publication.
13. Prove repository GO-schema validation accepts the new canonical shape.
14. Prove archive extraction receives the exact `tarfile.data_filter` callable
    and preserves regular-file bytes plus the owner executable bit.
15. Fail closed with `invalid_scope` before extraction when
    `tarfile.data_filter` is unavailable or not callable.
16. Reject absolute, `..`, `.git`, symlink, hardlink, and FIFO archive members
    without writing the destination.
17. Prove the data filter blocks a write through a pre-existing destination
    symlink and leaves the outside target unchanged.
18. Run the focused archive coverage under Python 3.11, 3.13, and 3.14, then
    confirm hosted CI removes exactly the 36 Opus failures.

## Files In Scope

- `scripts/opus_review_receipts.py`
- `scripts/opus_review_bridge.py` only for the post-integration explicit safe
  archive-filter repair
- `scripts/verification_report_gate.py`
- `tests/unit/test_opus_review_bridge.py` only for the archive-filter and
  unsafe-member coverage
- `tests/unit/test_opus_review_receipts.py`
- `tests/unit/test_verification_report_gate.py`
- `tests/unit/test_check_go_schema.py` only if repository-level shape coverage cannot
  be expressed through the existing report-gate tests
- `ARCHITECTURE.md` for the new verified publication invariant

Except for the post-integration archive-filter amendment above, no Opus
provider bridge execution behavior, prompt, sandbox, receipt lifecycle,
mailbox event, capacity packet, descriptor instance, or reviewed Stage-A code
belongs in this implementation diff.

## Non-Goals And Side-Effect Boundary

- No provider invocation or retry.
- No receipt or receipt-lock mutation.
- No mailbox write, cursor consumption, route mutation, or verification verdict.
- No Stage-A descriptor or verify-request creation by the bridge.
- No integration into `main`, force-push, publication, deployment, or merge.
  One normal push to `codex/opus-provider-free-lane-v` is authorized only after
  the append-only documentation and implementation commits are verified.
- No changes to `R..Q2` or the separate dirty control-plane work.

The bridge returns an isolated committed implementation range and verification
evidence. A live authorized seat remains responsible for normal review,
coordinator reconciliation, fresh Stage-A authority, and later integration.
