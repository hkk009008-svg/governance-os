# Codex R-INDEPENDENCE Default And Standing Opus Authorization

**Status:** User-approved design, 2026-07-12

## Problem

ADR-019 declares R-INDEPENDENCE to be the governance OS default for both
Claude and Codex, but the Codex harness does not yet carry the operative rule
through its executable model and role prompts. Codex can therefore reach
implementation without consistently classifying adversarial surfaces or
obtaining the required independent design-time enumeration.

ADR-020 separately requires one verdict-blind Opus review after every Codex
Lane V verification. The bridge currently treats missing task-level
authorization as `unavailable` and makes no provider call. That makes the
mandatory cross-model pass silently depend on repeated authorization even
though the user-principal has now granted standing consent for this one bounded
use.

## Goals

1. Make R-INDEPENDENCE operative by default for Pipeline Codex sessions.
2. Require Codex to classify adversarial-surface work before implementation.
3. Require independent design-time abuse/edge-case enumeration for triggered
   work and independent per-task verification before completion.
4. Give the existing post-Lane-V Opus attempt a durable, auditable standing
   authorization.
5. Keep the authorization limited to one provider attempt per Lane V bridge
   invocation, with no automatic retry or additional reviewer.
6. Preserve visible Codex-only degradation when Opus cannot run.

## Non-goals

- No standing authorization for design-time Opus calls, arbitrary Claude
  usage, other paid APIs, pods, pushes, locks, or other user-gated effects.
- No retry loop, provider failover, or third same-question review.
- No global `~/.codex` policy and no behavior change outside Pipeline.
- No change to seat, mailbox, cursor, GO, route, or push authority.
- No attempt to make credentials, network access, or sandbox support exist.

## Decision

### 1. R-INDEPENDENCE becomes a Codex harness default

The Codex executable model and role prompts will carry one canonical
R-INDEPENDENCE rule set. Before implementing a change, Codex classifies whether
it touches an adversarial surface:

- input rendered or composed into a parseable or executable context;
- authority or security-boundary enforcement;
- side-effect gating; or
- schema validation whose acceptance grants trust.

When triggered, Codex must obtain an independent design-time enumeration of
abuse cases, edge cases, and coverage targets before implementation. A
different model or harness is preferred; a same-model independent reviewer is
weaker and must be identified as such. The resulting cases become concrete,
tested acceptance criteria in a committed plan or equivalent durable artifact.

Before a triggered task is complete, an independent reviewer verifies the
actual diff against those cases. The existing Lane V plus verdict-blind Opus
pair provides the cross-model per-task verification for Codex-authored work.
R-VERIFY-TIER continues to prohibit redundant same-question passes.

The canonical full rule remains
`docs/protocol/claude/independence-first.md` for this change. Codex surfaces
link to it rather than creating a second copy that can drift.

### 2. Standing authorization is a narrow named policy

The bridge recognizes the stable authorization identity:

```text
standing-policy:codex-lane-v-opus-v1
```

It may resolve missing task-level authorization to that identity only when all
of the following are true:

1. the repository is proved to be Pipeline using the existing identity check;
2. the request declares the exact `codex-lane-v` review profile;
3. the reviewed HEAD and optional base resolve and match the requested scope;
4. all existing requirement-path, allowed-path, command, snapshot, and sandbox
   validation succeeds before provider launch.

The review profile becomes an explicit versioned field in request and result
contracts. It is not inferred from credentials, environment variables, free
text, mailbox state, or the presence of repository files.

Explicit valid `user-task:<id>` and `verify-request:<id>` sources remain
accepted for compatibility. An explicit malformed authorization source remains
an error; the standing default applies only when the source is absent.

### 3. One attempt, no retries

One bridge invocation launches at most one Opus provider process. Timeout,
missing credentials, missing Claude, network failure, sandbox failure,
effective-model mismatch, invalid JSON, invalid schema, or scope mismatch ends
that attempt. The bridge never retries automatically and never launches a
substitute provider.

Protocol prompts prohibit a second invocation for the same unchanged Lane V
verification. A further review is legal only when R-VERIFY-TIER names a
genuinely different question.

This is enforceable at two layers:

- the bridge guarantees at most one provider process per invocation; and
- the Codex protocol guarantees one invocation per unchanged Lane V task.

The bridge cannot prove global uniqueness across independently started OS
processes without adding a mutable cross-process ledger, which is outside this
design. Audit identity, reviewed commits, and prompt rules make duplicate calls
detectable without introducing that new state machine.

## Execution Flow

1. Codex classifies the proposed change under R-INDEPENDENCE.
2. If triggered, an independent reviewer enumerates design-time abuse and
   coverage cases; Codex folds them into durable acceptance criteria.
3. Implementation proceeds under the normal task discipline.
4. Codex completes its primary Lane V analysis without exposing its verdict to
   Opus.
5. Codex invokes `opus_review_bridge.py review` with profile
   `codex-lane-v`, reviewed commits, requirements, allowed paths, and exact
   verification commands.
6. The bridge validates repository identity and scope, then records either the
   explicit task authorization or
   `standing-policy:codex-lane-v-opus-v1`.
7. The bridge attempts exactly one sandboxed Opus process.
8. Codex reconciles the normalized result. Opus findings may tighten the final
   verdict but cannot silently weaken it.
9. The verification report records the review profile, authorization identity,
   effective model, finding dispositions, reconciliation result, and degraded
   reason when applicable.

## Failure Behavior

- Non-Pipeline repository or non-`codex-lane-v` profile: fail closed; standing
  authorization is unavailable and no provider runs.
- Invalid explicit authorization: fail closed; do not replace it with standing
  consent.
- Provider or environment unavailable: emit normalized `unavailable` evidence
  with the specific reason and preserve a visibly degraded Codex verdict.
- Opus returns issues: reconcile every finding and tighten GO/NITS/FAIL using
  the existing severity rules.
- Result scope or commit mismatch: reject stale, replayed, or invented review
  evidence.

Credentials and environment state are capabilities, not authorization. The
standing policy supplies consent only; all existing sandbox and identity
controls remain mandatory.

## Implementation Surfaces

- `AGENTS.md`: add the operative R-INDEPENDENCE stub while preserving unrelated
  concurrent edits.
- `scripts/codex_protocol_model.py`: add canonical rule data and render it into
  Codex readiness/role guidance.
- `.codex/agents/*.toml`: synchronize the relevant director, operator,
  verifier, coordinator, and readiness behavior.
- `docs/protocol/codex/continuation.md`: document classification, two review
  points, and the narrow standing policy.
- `scripts/opus_review_bridge.py`: add the review profile and standing-policy
  resolution after identity/scope validation.
- `tests/unit/test_opus_review_bridge.py`: pin authorization, call-count,
  profile, degradation, and compatibility behavior.
- `tests/unit/test_protocol_prompt_sync.py` and related model tests: pin
  R-INDEPENDENCE and authorization wording across generated and static prompts.
- `DECISIONS.md`: append a new ADR; do not rewrite ADR-019 or ADR-020 history.
- `ARCHITECTURE.md`: update the runtime invariant and freshness stamp if the
  implementation changes documented behavior.

## Test Strategy

Implementation follows test-driven development.

1. Add prompt/model tests that fail because Codex does not yet carry the
   operative R-INDEPENDENCE default.
2. Add bridge tests that fail because an absent authorization source currently
   produces `authorization_missing` for a valid Pipeline Lane V request.
3. Add negative tests for non-Pipeline identity, missing/wrong review profile,
   malformed explicit authorization, and scope mismatch; every case proves the
   provider runner was not called.
4. Add a call-count test proving one invocation makes at most one provider
   attempt and never retries failures.
5. Add contract tests proving results record the review profile and exact
   standing-policy identity.
6. Preserve tests for explicit task authorization and all normalized
   unavailable reasons.
7. Run focused bridge and prompt/model suites, the full unit suite, SHA baseline
   classification, `git diff --check`, and `scripts/ci_smoke.py`.
8. Run one live Opus smoke through the `codex-lane-v` standing policy when the
   provider environment is available. This standing consent authorizes that
   single attempt without another user prompt. Report unavailable environment
   evidence rather than retrying.

## Acceptance Criteria

- Every relevant Pipeline Codex prompt states the R-INDEPENDENCE trigger and
  both required review points.
- The executable model is the test-pinned source for the shared Codex wording.
- A valid Pipeline `codex-lane-v` request with no task-level authorization
  records `standing-policy:codex-lane-v-opus-v1` and attempts Opus once.
- The standing policy cannot authorize another review profile or repository.
- Explicit malformed authorization never falls back to standing consent.
- One bridge invocation never retries or launches more than one provider
  process.
- Final reports expose authorization identity and degraded status.
- No other user-gated side-effect policy is relaxed.
- Focused tests, full unit tests, SHA baseline, diff checks, and project smoke
  pass on the completed implementation.
