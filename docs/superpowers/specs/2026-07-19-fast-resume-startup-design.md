# Fast-Resume Startup Design

**Date:** 2026-07-19

**Status:** User-approved design; implementation is not authorized by this
document

**Scope:** Codex Pipeline live-seat startup for an unchanged, already-routed
lane, including evidence-ledger bridge work

## 1. Problem

The current startup path protects real authority boundaries, but it performs
more work than an unchanged routed continuation needs. A local profile of
`scripts/ledger_start_guard.py` observed about 10.7 seconds and 1,137 Git
subprocesses while loading the current mailbox history. That observation is
diagnostic, not gate evidence. The dominant cost was loading and validating
hundreds of route blobs and their histories before narrowing to the relevant
task.

The guard then tells the seat to run Git log and status commands that
`seat_status.py` already renders. Models also reread global orientation
material even when the exact route, target, ownership, and restrictions have
not changed.

The optimization must reduce evidence-retrieval and repeated-reading cost. It
must not weaken route lineage, mailbox-body precedence, ownership, review
independence, or separately authorized external effects.

The unavailable local Supabase/PostgreSQL service that currently blocks the
selling-package backend lane is a separate environment and authority issue.
Fast resume does not resolve or bypass it.

## 2. Goals

1. Let a seat resume an unchanged, already-routed lane from one compact,
   freshly derived startup result.
2. Preserve the same authority decision as the full startup path.
3. Replace route-count-proportional Git subprocesses with a bounded number of
   batch reads.
4. Avoid duplicate Git log/status instructions.
5. Explain exactly why full orientation is required when fast resume cannot
   prove eligibility.
6. Keep startup read-only and free of reusable approval state.

The operational target is a startup result in under two seconds on the current
checkout and movement to the first scoped test or edit within three minutes.
Runtime is reported by a committed measurement command but is not a flaky CI
gate; deterministic equivalence and bounded-process tests are the acceptance
evidence.

## 3. Non-goals

This design does not:

- create a route, ownership, authority, cache, receipt, or event type;
- make fast resume the default for a fresh, transplanted, or ambiguous seat;
- consume a cursor or publish mailbox state;
- authorize a lock, service start, provider launch, push, merge, deployment,
  booking, spend, or any other external effect;
- make the coordinator an implementation approval gate;
- replace actual-diff review by a distinct-seat, different-model, non-author
  Operator; or
- optimize unrelated smoke, test, or product workflows.

## 4. Selected Approach

Extend the existing ledger guard with an explicit resume form:

```bash
env -u GIT_INDEX_FILE .venv/bin/python \
  scripts/ledger_start_guard.py \
  --seat <seat> \
  --wave 2 \
  --resume-from <route-path>@<full-commit>
```

The immutable reference is an expectation supplied by the running task, not an
authority claim. The guard independently resolves current committed state and
compares it with that expectation.

The ordinary command without `--resume-from` remains compatible and retains
the full startup behavior.

## 5. Eligibility Boundary

Fast resume is available only when all of these are true:

1. The prompt already names a concrete live seat or coordinator and an
   already-routed lane.
2. `--resume-from` is a canonical `path@full-commit` reference whose exact
   committed body is readable.
3. The currently effective route for the target task is that exact immutable
   route.
4. Ownership remains effective at the route's immutable parent and revision,
   including any accepted transfer or exchange lineage.
5. Pipeline and target worktree identities are readable and the target binding
   still names the expected worktree.
6. Current dirty paths are unambiguously attributable to the routed lane from
   committed route or accepted-handoff evidence. If path attribution is absent
   or ambiguous, the guard falls back instead of accepting caller-written
   scope.
7. No newer relevant mailbox event requires body-first orientation.
8. The invoking Codex adapter has classified the requested work as local
   implementation or review. When the current request involves an external
   effect, the adapter does not invoke fast resume and instead uses that
   effect's separate fresh authority path. The guard does not attempt to infer
   natural-language user intent.

A fresh or transplanted seat, a missing immutable reference, or any ambiguity
uses full orientation. Fast resume is an optimization, never an entitlement.

## 6. Components

### 6.1 Batched committed-route reader

`scripts/route_lineage.py` gains a read-only batch path that:

- enumerates committed mailbox blobs once;
- retrieves their exact contents through batched Git object access;
- filters candidate routes by target and task before expensive lineage work;
- validates the selected task's complete overlapping lineage; and
- validates the selected route's working-tree bytes against the committed
  blob before returning it.

It must preserve the existing exact-current-tree and fail-closed lineage
semantics. Narrowing occurs only after exact committed bodies are available;
filename recency alone is never authority.

The batch implementation is shared by ordinary and resume resolution where
safe, so the optimization does not create two definitions of route truth.

### 6.2 Resume evaluator

`scripts/ledger_start_guard.py` owns the new option and evaluates the approved
eligibility boundary. It returns a structured in-memory result with one of
three classifications:

- `FAST RESUME: PASS`
- `FULL ORIENTATION REQUIRED`
- `START GUARD: FAIL`

`FULL ORIENTATION REQUIRED` is not a blocker. It names the changed or
unprovable evidence and prints the ordinary startup actions. `START GUARD:
FAIL` is reserved for the existing hard failures, such as a forbidden kernel,
unresolvable effective route, or invalid target binding.

### 6.3 Compact status composition

The guard reuses read-only status functions from
`.agents/skills/four-seat-protocol/scripts/seat_status.py` rather than asking
the model to rerun Git log and status. Any small refactor exposes data-returning
helpers while preserving the current command's output and no-mutation
behavior.

### 6.4 Thin instruction adapters

Codex continuation and ledger-bridge instructions describe when the optional
resume command is eligible and make full orientation the explicit fallback.
They do not copy the authority policy or add another checklist. Existing hard
invariants remain in `scripts/codex_protocol_model.py`.

## 7. Data Flow

For an eligible invocation:

1. Parse the concrete seat and canonical immutable route reference.
2. Resolve the registered target from the existing binding registry.
3. Batch-read current committed route bodies.
4. Resolve and validate the effective task lineage.
5. Load the exact expected route body and compare identities.
6. Refresh Pipeline HEAD/status, target worktree HEAD/status, unread state, and
   effective ownership.
7. Check whether dirty paths are attributable from committed evidence.
8. Render one capsule containing:
   - seat and work state;
   - exact route reference and exact committed route body;
   - target repo, worktree, and HEAD;
   - current dirty paths;
   - current ownership;
   - relevant unread state;
   - side effects not authorized by the route; and
   - the routed next outcome.
9. Return `FAST RESUME: PASS` and let the seat proceed directly to its scoped
   test, edit, or review.

The capsule is stdout derived from current state. It is not written to disk,
signed as authority, or reusable after state changes.

## 8. Fallback and Error Handling

The evaluator returns `FULL ORIENTATION REQUIRED` with an exact reason when it
finds any of the following:

- newer, conflicting, or ineffective route lineage;
- expected-route mismatch;
- target binding or worktree mismatch;
- ownership change or ambiguity;
- newer relevant mailbox state;
- dirty paths outside or unprovable against the attributed lane;
- malformed or unreadable Git output;
- inability to prove exact committed/worktree byte equality.

Fallback prints only the evidence that needs refreshing plus the existing full
startup command. It does not manufacture a `BLOCKED` result.

Existing hard-boundary violations remain fail-closed. Performance errors,
unsupported repository layouts, and unavailable batch plumbing fall back to
the existing correct path rather than weakening validation.

An external-effect request never enters the resume evaluator under the Codex
adapter. If a caller nevertheless runs the command, a fast-resume result still
states that it grants no effect authority, and the effect must stop at its
separate fresh gate.

## 9. Authority and Security Invariants

The implementation must preserve these properties:

1. Current committed repository and mailbox evidence outranks stale prose.
2. Relevant mailbox decisions remain body-first.
3. Caller input cannot invent ownership, allowed paths, authorization, or
   replay protection.
4. Fast resume never consumes or advances a seat cursor.
5. Coordinator remains read-only for behavior-changing product work.
6. Authors cannot approve their own behavior-changing changes.
7. External effects retain exact, fresh, separately scoped authorization.
8. Route and handoff references remain canonical full immutable references.
9. Any inability to prove equivalence chooses full orientation.

## 10. Verification

Focused tests cover:

- unchanged valid route produces `FAST RESUME: PASS`;
- a fresh or omitted resume reference uses ordinary startup;
- route replacement, fork, malformed lineage, or changed committed bytes
  rejects fast resume;
- changed target HEAD, binding, or worktree requires full orientation;
- effective ownership transfer or exchange requires full orientation;
- relevant unread mailbox state requires body-first orientation;
- attributable in-lane WIP is surfaced without mutation;
- unattributed or overlapping dirty paths require full orientation;
- Codex prompt-sync tests require external-effect requests to bypass fast
  resume, and every resume result states that it grants no effect authority;
- Git/batch failures fall back or fail closed according to the existing
  boundary;
- cursor, mailbox, lock, index, and worktree bytes remain unchanged;
- full and fast evaluators return the same authority decision over a shared
  corpus of route, ownership, mailbox, target, and dirty-state cases; and
- Git process count stays bounded independently of mailbox route count.

A committed benchmark instrument reports elapsed time and Git process count
for the current checkout. Its report is evidence for the optimization but
elapsed wall-clock time is not a CI verdict.

Because this touches route parsing and authority-sensitive startup decisions,
the implementation receives independent actual-diff review from a distinct
Operator seat on a different model before acceptance.

## 11. Compatibility and Rollout

The existing startup command remains unchanged. `--resume-from` is opt-in and
initially documented only for already-routed unchanged continuations. Any
unsupported or ambiguous case falls back to the current full path.

No migration, cache cleanup, event rewrite, or target-repo change is required.
The first implementation should remain within the existing route reader,
guard, status helper, thin Codex docs, and focused tests. Broader startup or
hook refactoring is outside scope.

## 12. Success Criteria

The change succeeds when:

1. An unchanged routed continuation reaches one fresh capsule without repeated
   manual orientation commands.
2. Authority decisions are differential-test equivalent to the full path.
3. Git process count is bounded rather than proportional to historical route
   count.
4. The current checkout benchmark reports the intended sub-two-second startup
   target, without making timing a flaky CI gate.
5. Every ambiguity or changed authority fact falls back with an actionable
   reason.
6. No new protocol entity, cache, or authority-granting structure exists.
