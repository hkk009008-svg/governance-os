# Pipeline Route Correction and Publication Design

**Date:** 2026-07-20  
**Status:** Approved  
**Scope:** Correct the active Pipeline coordinator route's false G7 push classification, then publish Pipeline `main` once. Evidence-ledger integration remains a separate, unexecuted recommendation.

## Context

Pipeline `main` is clean at `eb732bd8e2e91631143224339baeaf7b714a8145` and the live remote `origin/main` is `cd076c50780e62dadf77ffd04cda34f60a8c56a3`. The active route is:

`coordination/mailbox/sent/2026-07-19T12-03-04Z-coordinator-to-all-coordination.md@eb732bd8e2e91631143224339baeaf7b714a8145`

Route validation fails G7 because one physical line contains positive status prose followed by the negative sentence `No merge, push, ... is implied.` The validator is line-oriented. Since the line does not begin with `No` and contains the directive token `push`, it is classified as an untokened shared push authorization.

A diagnostic probe established the boundary:

- the current combined line produces one `remote-ref update/push` request;
- moving the negative sentence onto its own physical line produces no request;
- a positive control, `Director may push origin/main`, still produces a push request.

This is a route-text defect. Validator behavior does not change in this cycle.

## Goals

1. Publish one superseding coordinator route that preserves all accepted product-first backend findings and owner-gate holds.
2. Put every negative external-effect boundary on a separate physical line so the route validates without weakening G7.
3. Bind the requested Pipeline publication to one executor, one remote/ref, and one immutable preflight scope.
4. Validate the corrected route and Pipeline governance surfaces before publication.
5. Push Pipeline `main` to `origin/main` exactly once, then verify the live remote ref.

## Non-Goals

- No edit to `scripts/protocol_capacity.py` or its tests.
- No evidence-ledger merge, push, product edit, service action, database action, or owner-gate inference.
- No force-push, history rewrite, reset, rebase, amend, cleanup, cursor consumption, lock action, provider action, or paid spend.
- No change to Gates B, C, or D or to the Task 5B hold.

## Superseding Route

The coordinator publishes one new `coordination` event through the fixed mailbox writer. It supersedes the invalid route without editing the existing committed artifact.

The event will:

- cite the active route and its immutable commit;
- retain target head `41d9f1d846d6e0928b520573094ae59846114df5`, accepted Task 1-3 and Task 5A verdict references, contract hashes, and the Gate B/C/D hold;
- state the G7 correction explicitly;
- place the no-merge/no-push sentence on its own physical line;
- authorize no evidence-ledger effect;
- contain one structural external-effect token for the separately user-authorized Pipeline publication.

The token shape is:

- effect: `git push`
- executor: `coordinator`
- target: `origin/main`
- scope: Pipeline `main` whose new commits are limited to the approved design and superseding coordinator route, based on `eb732bd8e2e91631143224339baeaf7b714a8145`

The route will name the user instruction in this task as the authorization source. The structural token records executor election and scope; it does not replace user authorization.

## Execution Flow

1. Refresh Pipeline `HEAD`, status, mailbox, and live `origin/main`.
2. Publish the superseding route through `coordination/bin/send-event`.
3. Stage and commit only the generated coordinator route path.
4. Confirm the committed range from `eb732bd` contains only this approved design and the superseding route.
5. Run coordination validation, route validation, protocol doctor, and Pipeline smoke.
6. Re-read live `origin/main`. Stop if it differs from `cd076c50780e62dadf77ffd04cda34f60a8c56a3`, if local status is dirty, or if the remote is not an ancestor of the local publication head.
7. Push local Pipeline `main` to `origin/main` once.
8. Verify `git ls-remote origin refs/heads/main` equals the pushed local commit and recheck local status.

## Failure Handling

- If fixed-writer publication fails, preserve the exact error and do not bypass the writer.
- If the corrected route is not valid, do not push; correct only the superseding route artifact under a newly reviewed scope.
- If smoke or coordination checks fail, do not push.
- If remote `main` changes, stop and reconcile the new remote history; never force-push.
- If push fails or has ambiguous outcome, do not retry until live remote evidence establishes whether the intended commit landed.

## Evidence-Ledger Recommendation

Do not merge or push evidence-ledger in this cycle. Its accepted feature head `41d9f1d846d6e0928b520573094ae59846114df5` and `main` at `cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47` diverge by 25 feature-only commits and one main-only commit. A read-only merge-tree probe identifies overlapping changes in `ARCHITECTURE.md`, `DECISIONS.md`, and `OPERATIONS.md`.

The next evidence-ledger cycle should create an integration branch from current `main`, merge the accepted feature head, reconcile those three documentation conflicts against the actual merged code, run the complete product verification profile, and obtain independent non-author GO on the merged tree. Merge and publication remain separately authorized effects.

## Acceptance

- The superseding route is the only coordination correction.
- The active route validates cleanly with no G7 issue.
- Pipeline coordination checks, protocol doctor, and smoke pass.
- The push is a normal fast-forward update of `origin/main`; no force option is used.
- Live `origin/main` equals the final local Pipeline commit after publication.
- Evidence-ledger remains unchanged.
