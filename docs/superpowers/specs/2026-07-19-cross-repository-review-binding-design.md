# Cross-Repository Review Binding Design

**Date:** 2026-07-19

**Status:** Approach A approved by the user; written specification pending user review

## Purpose

Allow the existing compact Director-to-Operator review pair to bind an exact
Git range in a routed target repository such as `evidence-ledger`, while
preserving current Pipeline-local reviews and every separate authority
boundary.

This is a resolver correction, not a new review system. It adds no broker,
registry, approval token, receipt, scheduler, or external-effect authority.

## Problem

The canonical parser currently resolves `Reviewed base` and `Reviewed head`
only in the Pipeline repository. The Task 5A request therefore put the real
`evidence-ledger` range in auxiliary prose while its canonical fields named a
Pipeline range. Operator2 correctly issued FAIL because a report could bind
only the Pipeline range or misrepresent the target review.

The binding defect is recorded by:

- `coordination/mailbox/sent/2026-07-19T06-39-39Z-operator2-to-all-verification-report.md@1ebadf84a4730f70116634f0f994550d6d604063`; and
- `coordination/mailbox/sent/2026-07-19T06-46-07Z-director2-to-all-coordination.md@ff6ea7bcc481215d21255c1e187327ef007e5ce6`.

The target implementation range remains
`16d1e4dfd204bc1344be93cffa20f99ca1a16b43..6782538190675fec9dbda0ea90e6b302377138a2`.
No implementation defect is inferred from the request-binding failure.

## Decision

Add one optional canonical field to both current verify-requests and
verification reports:

```text
Reviewed repository: /absolute/canonical/git/worktree/root
```

The immutable reviewed-artifact identity becomes the committed tuple:

```text
(reviewed repository, reviewed base, reviewed head)
```

For a new cross-repository review, `Reviewed repository` is required in the
request and report. When the field is absent, the reviewed repository remains
the Pipeline root, preserving existing Pipeline-local and frozen historical
artifacts without rewriting them.

The report must reproduce the request's repository field exactly. It cannot
add, omit, or substitute the field, base, or head.

## Alternatives Rejected

- Importing target Git objects into Pipeline would contaminate and couple the
  governance repository merely to make its local resolver see another
  repository's commits.
- Replacing the reviewed Git range with a generated digest manifest would add
  a second range format and weaken the existing actual-diff review semantics.

Both alternatives add machinery without improving the authority boundary.

## Canonical Repository Resolution

The parser continues to read the verify-request from its exact committed
Pipeline `path@trigger-commit`. It resolves only the reviewed range in the
selected repository.

For an explicit `Reviewed repository`, the resolver must:

1. require exactly one nonblank, absolute, normalized path;
2. reject trailing whitespace, duplicate or malformed headers, relative
   paths, lexical aliases, and any symlinked path component;
3. require a bounded existing directory whose system-derived Git top level is
   exactly that path;
4. run Git with inherited `GIT_*` variables removed and replacement objects
   disabled;
5. resolve both full lowercase SHAs as commits in that repository; and
6. require `Reviewed base` to be a strict ancestor of `Reviewed head` there.

The existing rule that the Pipeline request-trigger commit must add exactly
the canonical request path remains unchanged. For a Pipeline-local review,
the existing rule that the trigger is strictly after the reviewed head also
remains. A cross-repository trigger cannot have Git ancestry with the target
head, so the committed request artifact—not invented cross-repository
ancestry—provides the temporal binding.

If another repository contains the same full commit objects, the reviewed
content and range are identical; the committed canonical path still selects
the intended resolver. A path replacement that does not contain the bound
objects fails closed.

## Report Validation

Report parsing and validation must:

- parse the optional field with the same duplicate-header defenses as other
  identity fields;
- load the request only from its committed Pipeline reference;
- derive the authoritative reviewed repository from that request;
- require the report repository field, base, and head to match the request
  exactly;
- re-resolve the range and ancestry in the request-bound repository; and
- retain all existing author/reviewer, different-model, finding-disposition,
  evidence, and GO restrictions.

The report's field never chooses a different resolver independently. A
mismatch is a validation failure, not a prompt to reconstruct intent.

## Compatibility

- Existing Pipeline-local requests and reports without the new field continue
  to resolve against Pipeline.
- Frozen historical compatibility remains byte-bound and unchanged.
- The malformed Task 5A request and its FAIL remain truthful historical
  evidence; they are not edited or reinterpreted.
- After the correction receives non-author Operator GO, Director2 issues one
  replacement Task 5A request with the target repository and range in the
  canonical fields.

## Failure Handling

The validator fails closed for:

- a blank, duplicate, malformed, relative, non-normalized, or symlinked
  repository field;
- a path that is missing, not a directory, not a Git worktree root, or whose
  system-derived top level differs;
- an unavailable or non-commit base/head;
- a non-ancestor or equal base/head;
- a report repository field that differs from the request, including an
  explicit/omitted mismatch; or
- any existing identity, model, finding, evidence, or request-binding failure.

Errors identify the rejected boundary without copying sensitive repository
contents into mailbox events.

## Canonical Surfaces

The smallest expected implementation surface is:

- `scripts/compact_pair_loop.py` for parsing, repository resolution, and
  validation;
- `tests/unit/test_compact_pair_loop.py` for same-repository compatibility and
  adversarial cross-repository cases;
- `tests/unit/test_coordination_tooling.py` only if the fixed report writer
  needs an end-to-end cross-repository candidate test;
- `scripts/codex_protocol_model.py` plus its focused prompt-sync test to state
  that the reviewed repository is part of the range identity when present;
  and
- `ARCHITECTURE.md` only for factual smoke-anchor updates caused by moved
  definitions.

Implementation may narrow this set when tests show a surface is unnecessary.
It must not widen into mailbox transport, task routing, authority schemas, or
target-product code.

## Verification

Test-first implementation must prove:

1. an unchanged Pipeline-local request/report still validates;
2. a cross-repository request/report validates the exact target base/head;
3. the same target SHAs fail when resolved only in Pipeline;
4. repository omission/addition/substitution between request and report
   fails;
5. duplicate, blank, malformed, relative, alias, symlink, non-repository, and
   unavailable-repository inputs fail;
6. missing commits, equal endpoints, reversed ancestry, and merge-base errors
   fail closed;
7. report identity, model independence, findings, and GO evidence remain
   enforced; and
8. the fixed writer, GO-schema scan, placeholder check, and Pipeline smoke
   remain green.

Behavior-changing acceptance requires a committed actual-range review by a
non-author Operator seat on a different model.

## Authority Boundaries

The new field is structural evidence only. It does not authorize reading a
repository that the route did not place in scope, target writes, implementation
or repair, service or database access, dependency installation, real-data use,
push, merge, deployment, cursor consumption, lock action, booking, spend, or
any other external effect.

The coordinator routes the correction but does not author its behavior-changing
implementation.

## Acceptance

The correction is accepted when a fixed-writer request can canonically bind
the exact `evidence-ledger` Task 5A repository/base/head tuple, an assigned
non-author Operator can publish a report bound to the same tuple, adversarial
repository substitutions fail closed, legacy Pipeline reviews still validate,
and no new authority or ceremony layer is introduced.
