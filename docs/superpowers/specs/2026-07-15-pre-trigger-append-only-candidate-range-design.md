# Pre-Trigger Append-Only Candidate Range Design

**Date:** 2026-07-15

**Status:** user-principal design approved; written specification awaiting review

**Scope:** Pipeline four-seat Director-to-Operator delivery before canonical Lane V trigger publication

## 1. Decision

Replace route-specific "exactly one implementation commit" constraints with a
bounded append-only candidate range before trigger publication.

A Director may append a separate review-fix commit without returning to the
coordinator only while all of these remain true:

1. no Lane V descriptor has been committed for the candidate;
2. no canonical verify-request has been published for the candidate;
3. the candidate range is linear and contains one through five total commits;
4. every changed path remains inside the packet's candidate `scope_files`;
5. the route objective, acceptance criteria, verification commands, descriptor
   identity, and side-effect policy are unchanged;
6. the correction does not modify the enforcement code for this policy; and
7. the Director re-runs the required spec review, quality review, and complete
   candidate gate against the new final head.

Once a descriptor is committed or a canonical verify-request is published,
the candidate is frozen. Any later correction requires a coordinator-mediated
replacement with a fresh descriptor identity and verify-request. The original
descriptor and request remain immutable.

This design preserves the stop-and-report behavior that exposed the Stage A
contradiction. It removes the unnecessary coordinator round-trip for an
ordinary in-envelope defect found before authority publication.

## 2. Evidence and Problem Statement

The current rules separately require:

- one commit per task and a distinct fix commit after review, without amend;
- independent review before the Director requests Lane V; and
- exact descriptor and verify-request correlation to a reviewed base and head.

Those rules are compatible with a commit range. The Stage A plan added an
extra, incompatible constraint: exactly one implementation commit. Independent
review then found an Important compatibility defect after that commit, while
the no-amend rule required the correction to be a second commit. Director2
correctly stopped instead of silently rewriting history or exceeding the
route.

Recent protocol history also contains repeated invalid-trigger, descriptor,
and authority-correction cycles. The recurring failure pattern is not that
seats stop too often; it is that route prose over-constrains candidate history
before the immutable authority boundary exists.

The concrete Stage A topology was rechecked with:

```text
$ env -u GIT_INDEX_FILE git rev-parse 56091d107382abfe9f06df1aa4cd003d71be7b5e^
40fd0a5e43c6b28330ced9ddffe01483cde42b65
$ env -u GIT_INDEX_FILE git rev-list --count 40fd0a5e43c6b28330ced9ddffe01483cde42b65..56091d107382abfe9f06df1aa4cd003d71be7b5e
1
$ env -u GIT_INDEX_FILE git diff --name-only 40fd0a5e43c6b28330ced9ddffe01483cde42b65..56091d107382abfe9f06df1aa4cd003d71be7b5e
scripts/opus_review_bridge.py
scripts/opus_review_receipts.py
tests/unit/test_opus_review_bridge.py
tests/unit/test_opus_review_receipts.py
```

`git rev-list --merges` produced no output for that range.

## 3. Goals

- Let a Director correct ordinary pre-trigger review findings without a new
  coordinator route.
- Preserve append-only audit history and exact Operator review scope.
- Keep the current maximum context size of five tightly coupled commits.
- Make the boundary executable rather than relying on natural-language route
  interpretation.
- Fail closed when scope, authority, side effects, history, or trigger state
  changes.
- Keep provider calls, receipts, locks, merge, push, and publication authority
  unchanged.

## 4. Non-Goals

- No self-correction after descriptor creation or verify-request publication.
- No amend, rebase, reset, force update, squash, history replacement, or merge
  commit inside an autonomous candidate range.
- No new Director authority over provider attempts, receipts, locks, merge,
  push, external publication, or coordinator routes.
- No replacement for Operator GO/NITS/FAIL.
- No generic candidate-tip ledger in V1.
- No claim that Git can prove the absence of a discarded local commit that was
  never named in durable evidence.
- No automatic decision that several commits are semantically tightly coupled;
  Operator judgment remains binding on that question.

## 5. Terminology

**Candidate base**

The immutable commit containing the active coordinator route event named by
the Director packet's candidate policy. A base may move forward only after
independent acceptance or a new coordinator route.

**Candidate range**

The exact `candidate_base..candidate_head` implementation range. It contains
one through five total commits, including initial implementation, review fixes,
documentation-only commits, reverts, and no-op commits.

**Candidate head**

The final implementation commit after all pre-trigger spec and quality review
findings have been resolved.

**Trigger freeze**

The boundary reached when the descriptor for the candidate is committed. From
that point onward, implementation history cannot advance under the existing
route even if the verify-request has not yet been committed.

**Canonical trigger**

The committed verify-request that exactly binds one descriptor, reviewed base,
reviewed head, and task identity. It remains the sole Lane V authority source.

## 6. Canonical Pre-Trigger Contract

V1 reuses the existing active Director capacity packet. It does not introduce
a second route-envelope artifact.

An active `director-implementation` packet that permits autonomous correction
adds one machine-readable `candidate_policy` object with these required fields:

| Field | Required value |
|---|---|
| `history` | Exact enum `append-only-until-trigger` |
| `route_event` | One committed coordinator route path under `coordination/mailbox/sent/` |
| `descriptor_task_id` | One canonical UUID reserved for the later descriptor |
| `max_commits` | Integer `5` |
| `verification_commands` | Nonempty ordered list accepted by the existing trusted-command validator |
| `governed_side_effects` | Exact enum `none` |

The validator derives the candidate base as the unique commit containing the
named route event. It does not accept a self-reported base SHA or commit count.

Existing packet fields retain their current meanings:

- `scope_files` is the exact candidate implementation path allowlist;
- `allowed_paths` additionally covers later descriptor and verify-request
  artifacts;
- `acceptance` is the route's authoritative behavioral contract;
- `row_ids`, dependencies, owner, packet type, and next recipient retain their
  current capacity semantics.

The descriptor must copy `descriptor_task_id`, candidate base, final candidate
head, `scope_files`, and `verification_commands` from the validated packet
contract. Descriptor resolution rejects any mismatch. The verify-request then
cross-binds the descriptor digest, exact base, and exact final head under the
existing trigger grammar.

The packet is authoritative before trigger publication. The descriptor and
verify-request become authoritative only after their existing structural and
content-addressed checks pass. Review notes and candidate status reports are
evidence, not authority.

## 7. Lifecycle

### 7.1 Candidate open

1. Coordinator commits the route and packet.
2. Director starts an isolated branch from the derived candidate base.
3. Director commits the initial implementation within `scope_files`.
4. Required spec and quality reviewers inspect that exact head.
5. If they find an in-envelope defect, Director adds a separate fix commit.
6. Director repeats both reviews and the complete candidate gate.
7. The process may repeat while the complete range remains linear and contains
   no more than five commits.

No descriptor or verify-request exists during this loop.

### 7.2 Candidate validation

Before descriptor creation, Director runs one candidate-range gate:

```text
protocol_capacity_board.py --wave <wave> \
  --validate-candidate <director-packet.json> \
  --candidate-head <full-sha>
```

The command is a proposed interface; its implementation belongs to the later
implementation plan.

It resolves and checks:

- the route event and derived candidate base;
- full object identity and ancestry;
- one through five commits in `base..head`;
- one-parent linear history with no merge commits;
- aggregate and per-commit changed paths, including rename endpoints and file
  modes;
- exact containment within `scope_files`;
- absence of the descriptor and canonical verify-request for the task;
- unchanged packet policy and task identity; and
- trusted verification-command syntax.

It reports facts derived from Git and committed packet bytes. It does not trust
declared `commit_count`, `changed_paths`, `within_scope`, `tests_passed`, or
`tightly_coupled` booleans.

V1 can mechanically preserve only candidate SHAs that appear in committed
route or review evidence. If a required committed artifact names an earlier
candidate head, that SHA must remain in the final linear range. V1 deliberately
does not claim to detect a discarded local tip that was never made durable.

### 7.3 Trigger freeze

After the candidate gate and both reviews pass:

1. Director snapshots the final candidate head.
2. Director creates the descriptor from the validated packet contract.
3. Immediately before committing the descriptor, Director verifies that the
   isolated branch tip still equals the validated candidate head.
4. The descriptor commit starts trigger freeze.
5. Director commits exactly one canonical verify-request after the descriptor.
6. Operator resolves the descriptor and independently verifies the exact
   frozen `base..head` range.

A partial or mismatched descriptor/request sequence confers no Lane V
authority and blocks until coordinator resolution. It does not reopen
autonomous candidate correction.

### 7.4 Post-freeze correction

After descriptor commit or canonical trigger publication, every implementation
change returns to the coordinator. A lawful replacement:

- preserves the original descriptor and request byte-for-byte;
- receives a fresh descriptor task identity and canonical verify-request;
- names the prior frozen generation it replaces;
- recomputes the state binding and exact candidate range;
- leaves Operator blocked until the replacement trigger validates; and
- grants no merge, push, provider, receipt, lock, or publication authority.

## 8. Autonomous-Correction Decision

Director may append a fix commit only when every answer in the left column is
yes.

| Gate | Autonomous correction | Coordinator reroute |
|---|---|---|
| Descriptor absent and verify-request absent | yes | either exists |
| Final range contains at most five commits | yes | sixth commit required |
| History is a strict linear fast-forward from the derived base | yes | merge, amend, rebase, reset, replacement, or missing object |
| Changed paths stay within `scope_files` | yes | any new or renamed-outside path |
| Objective and acceptance are unchanged | yes | new behavior, guarantee, or semantic objective |
| Verification commands and task identity are unchanged | yes | either changes |
| Governed-side-effect policy remains `none` | yes | any provider, receipt, lock, merge, push, or publication action is required |
| Candidate does not change this policy's validator or authority schema | yes | self-modifying enforcement |
| Evidence is sufficient to prove every mechanical gate | yes | ambiguity or incomplete history |

`tightly_coupled` remains a semantic conclusion. Director explains why the
commits form one correction sequence; Operator may still return NITS or FAIL if
the range actually contains multiple objectives.

## 9. Five-Commit Rule

The cap is five total unaccepted commits, not five fix commits. It aligns with
the existing small-range Operator review ceiling and avoids a second threshold.

The base cannot slide to an unaccepted intermediate commit to keep the visible
range below the cap. Only a commit covered by binding independent acceptance
and coordinator closeout can become a later candidate base without a new
design decision.

When a sixth commit would be required, the coordinator chooses one of two
paths:

- replan or decompose the work into independently reviewable objectives; or
- issue an explicit larger-range route with a distinct verification design.

The coordinator may not merely reset the count while preserving the same
unaccepted objective.

## 10. Enforcement Surfaces

The later implementation plan should update only the surfaces needed to make
the rule executable:

- `scripts/protocol_capacity.py`: parse and validate `candidate_policy`;
- `scripts/protocol_capacity_board.py`: expose the candidate-range gate;
- the Lane V descriptor/trigger resolver: re-run the same derived range and
  packet checks so a skipped Director preflight cannot create authority;
- `scripts/codex_protocol_model.py`: render the invariant for Codex roles;
- agent-neutral orchestration and director/operator docs;
- Claude and Codex seat skills and role prompts that mirror the invariant; and
- focused capacity, descriptor, trigger, and prompt-sync tests.

The reusable range logic should have one implementation in the protocol
library. The CLI preflight and trigger resolver call that implementation rather
than maintaining parallel validators.

The implementation plan must first reconcile the active overlapping user/peer
WIP on protocol skills, prompts, and tests. This design document does not claim
or overwrite those files.

## 11. Abuse and Regression Cases

At minimum, tests must cover:

1. one initial commit followed by one in-scope review-fix commit is accepted;
2. the same range is rejected if the route still says exactly one commit;
3. six total unaccepted commits are rejected;
4. a merge commit or nonlinear side branch is rejected;
5. an amended or replaced candidate head named by required committed evidence
   is rejected;
6. a forbidden path, rename endpoint, symlink, gitlink, or mode change is
   rejected;
7. changing acceptance, verification commands, descriptor identity, or
   side-effect policy forces coordinator rerouting;
8. creating the descriptor and then appending an implementation commit is
   rejected;
9. using an old trigger against a newer descendant head is rejected;
10. sliding the base to an unaccepted intermediate commit is rejected;
11. changing the candidate-range validator or its authority schema under the
    autonomous policy is rejected; and
12. the current Stage A topology—base `40fd0a5`, immutable implementation
    `56091d1`, and exactly one additive review fix in the original four-path
    scope—passes once its bounded coordinator correction is committed.

Each negative test must be non-vacuous: first prove the corresponding valid
case passes, then mutate only the prohibited dimension and prove rejection.

## 12. Current Stage A Application

This specification does not retroactively authorize Director2. The active
Stage A plan and packet still require one shipping commit.

The smallest current correction remains a coordinator-owned metadata route
that:

- preserves `56091d1` without amend or rewrite;
- authorizes exactly one additive resolver-compatibility fix commit;
- keeps reviewed base `40fd0a5` and binds the descriptor to the corrected final
  head;
- keeps the exact original four implementation/test paths;
- leaves provider attempts at zero; and
- routes the final range to Operator2 only after renewed spec and quality
  reviews pass.

That bounded correction may proceed before the general protocol enhancement,
but it must be explicit because the current committed route has not yet adopted
this policy.

## 13. Independent Challenge and Consultation

This design changes an authority boundary and therefore requires independent
challenge.

- A bounded same-model read-only helper audited the concrete Stage A topology
  at `406cee8`. It confirmed that an append-only correction can preserve base
  `40fd0a5`, immutable candidate `56091d1`, the original four-path scope, zero
  provider attempts, and later Operator2 authority. This is useful but weaker
  than cross-model review.
- Guarded manual ChatGPT Pro consultation
  `67d59d80-9331-425f-8eab-b70012734ee6` was delivered once against the exact
  bound state. Its response failed the local import contract and the record is
  terminal `failed/malformed`. No response content or recommendation is
  adopted, summarized, retried, or treated as evidence.
- Before implementation completion, an independent Operator must verify the
  actual diff against Section 11. A later valid cross-model challenge may ask a
  genuinely different question, but this failed consultation is not retried.

## 14. Acceptance Criteria

The design is implemented only when:

- pre-trigger in-envelope review fixes no longer require a coordinator route;
- exact-one-commit plus separate-review-fix contradictions fail route
  validation before dispatch;
- candidate base, range, count, ancestry, merges, paths, and final head are
  derived rather than trusted from prose;
- the same range validator runs before descriptor creation and again during
  trigger resolution;
- descriptor creation freezes autonomous correction;
- every post-freeze change requires a fresh coordinator-mediated descriptor and
  verify-request;
- five means five total unaccepted commits and the base cannot slide;
- all abuse cases in Section 11 are enforced by tests;
- protocol mirrors remain synchronized; and
- no new merge, push, provider, receipt, lock, spend, or publication authority
  is introduced.
