# Abandoned Takeover Outcome Integrity Design

**Date:** 2026-07-21

**Status:** User-approved design; implementation not yet routed

**Finding ID:** `audit-5-abandoned-takeover-outcome-integrity`

**Scope:** Preserve an existing outcome across abandoned-owner takeovers by
restoring parity between the route-lineage adapter and the canonical protocol
model.

## Problem

An abandoned-owner takeover may currently become authoritative while changing
the parent contract's outcome. This violates the autonomous outcome contract:
a takeover may replace an inactive owner, but it may not silently redefine the
result being owned.

The defect is live on clean Pipeline `HEAD` `fa0f941`. A focused reproduction
created a valid abandoned takeover whose successor route changed the outcome.
Route resolution accepted the successor as authoritative and returned the
changed outcome without a lineage issue.

No message or route is lost. The integrity failure occurs while adapting a
committed takeover route into the canonical ownership model.

## Root Cause

`scripts/codex_protocol_model.py` already enforces the intended policy.
`_abandoned_takeover_is_effective()` rejects an abandoned takeover whenever
`OwnershipChange.outcome` is not `None`.

`scripts/route_lineage.py` constructs `OwnershipChange` in two branches:

- A normal proposal passes the candidate outcome when it differs from the
  parent outcome.
- An abandoned takeover, represented by a `dispatch-claim`, omits the outcome
  field entirely.

The omission converts a real outcome change into the default `None` before the
model guard runs. The model therefore sees an unchanged outcome and accepts
the takeover.

## Chosen Design

Restore adapter parity in the abandoned-takeover branch. When constructing its
`OwnershipChange`, pass the same outcome delta used by the normal proposal
branch:

- equal candidate and parent outcomes map to `None`;
- a different candidate outcome maps to that changed value.

The existing canonical model remains the sole policy authority. With the real
delta present, its current guard rejects the outcome-changing takeover. An
unchanged abandoned takeover continues to work exactly as it does today.

This is preferable to adding a second route-lineage precheck, which would
duplicate policy and create another drift point. Expanding takeover schemas to
authorize outcome changes is also excluded because that would change protocol
semantics rather than repair the adapter defect.

## Code and Test Scope

Only these implementation paths may change:

1. `scripts/route_lineage.py`
   - Supply the candidate-versus-parent outcome delta when constructing an
     abandoned-takeover `OwnershipChange`.
2. `tests/unit/test_route_lineage.py`
   - Add a regression case that reproduces the currently accepted changed
     outcome.
   - Preserve or strengthen the existing positive case proving an unchanged
     abandoned takeover remains authoritative.

The regression must be non-vacuous: before the implementation correction, the
changed-outcome case must fail because the takeover becomes authoritative;
afterward, that successor must be ineffective and must not replace the parent
contract's outcome.

## Resolution Flow

1. Route lineage loads the parent outcome and successor candidate outcome.
2. It computes whether the candidate outcome differs from the parent.
3. It supplies that delta to the canonical `OwnershipChange` model.
4. The model accepts an unchanged abandoned takeover or rejects a changed one.
5. Route resolution excludes an ineffective changed-outcome successor from
   authoritative ownership.

No new exception type, fallback, recovery path, or user-facing route format is
introduced. Existing ineffective-lineage handling remains responsible for the
rejected successor.

## Verification

The implementing Director must use test-driven development: first commit or
demonstrate the failing regression against the current behavior, then make the
minimal adapter correction.

Required verification is:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py \
  tests/unit/test_autonomous_seat_contract.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

The actual behavior-changing commit or range requires review by a non-author
Operator seat using a different model. The review must bind this finding by the
committed design path and commit and confirm both the positive and negative
takeover cases.

## Non-Goals

- No change to `scripts/codex_protocol_model.py` policy.
- No mailbox, envelope, route-body, or ownership schema change.
- No authorization for outcome-changing takeovers.
- No refactor of normal proposals, transfers, exchanges, or fork resolution.
- No remediation of other audit findings in this route.
- No merge, push, cursor consumption, lock action, provider launch, paid spend,
  or other external effect.

## Acceptance

- The changed-outcome regression fails on the pre-fix behavior and passes with
  the correction.
- An unchanged abandoned takeover remains effective.
- An outcome-changing abandoned takeover cannot become the authoritative
  successor.
- The focused protocol tests and Pipeline smoke pass.
- The implementation diff is limited to the two scoped files.
- A distinct non-author Operator issues the binding verdict on the actual
  implementation range before any integration decision.
