# Codex R-INDEPENDENCE And Standing Opus Authorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make R-INDEPENDENCE the version-controlled Pipeline Codex default and authorize exactly one non-retried Opus attempt for each Pipeline Codex Lane V verification when task-level authorization is absent.

**Architecture:** Add one canonical R-INDEPENDENCE rule set to the executable Codex model and mirror it into the root/process and role surfaces. Advance the strict Opus review contract to `opus-review/v2` with a required `codex-lane-v` profile, then resolve an absent authorization source to `standing-policy:codex-lane-v-opus-v1` only after Pipeline identity, reviewed commits, immutable reviewed-HEAD scope, and command checks pass. Preserve explicit task authorization, fail closed on malformed explicit sources, keep reconciliation at v1, and retain one provider process per invocation with no retry or substitute.

**Tech Stack:** Python 3.14 standard library, `pytest`, TOML role prompts, Markdown protocol docs, Git worktrees, the existing Claude CLI bridge, and macOS Seatbelt sandboxing.

## Global Constraints

- No global `~/.codex` behavior: scope is `/Users/hyungkoookkim/Pipeline` only.
- Non-Pipeline repositories and any review profile other than `codex-lane-v`
  must fail closed before a provider call.
- Standing consent is exactly `standing-policy:codex-lane-v-opus-v1` and applies only to an absent source on the exact `codex-lane-v` review profile.
- Explicit `user-task:` and `verify-request:` sources remain valid. An explicitly supplied standing-policy value or any malformed explicit value must fail closed.
- One bridge invocation may launch at most one Opus provider process. It must not retry, fail over, or add a third same-question reviewer.
- Standing consent does not authorize design-time Opus, other Claude calls, other paid APIs, pods, pushes, locks, mailbox writes, cursor consumption, or route mutation.
- `review_profile` is required in normalized review evidence. Advance the review schema to `opus-review/v2`, reject v1 review JSON, and leave `opus-reconciliation/v1` unchanged.
- Credentials, network state, and sandbox availability are capabilities, not authorization. Their absence yields visible degraded Codex-only evidence after standing consent is recorded.
- Preserve operator GO/NITS/FAIL authority and every existing sandbox, immutable-snapshot, commit, path, command, and reconciliation guard.
- Use `/Users/hyungkoookkim/Pipeline/.venv/bin/python`; the isolated worktree has no local `.venv`.
- Prefix every Git and pytest command with `env -u GIT_INDEX_FILE`.
- Use `apply_patch` for edits, explicit pathspecs for commits, and preserve unrelated worktree state.
- Do not push. Local commits and later local integration are separate from push authorization.
- Tasks 2 and 3 share `scripts/opus_review_bridge.py` and its tests and therefore run sequentially. No parallel implementers may edit shared prompt or bridge files.
- Generic implementation spec/code-quality reviews are not extra Lane V passes. The named Lane V plus Opus pair occurs in Task 5.

---

## File Structure

### Canonical Codex behavior

- Modify `scripts/codex_protocol_model.py`: own `R_INDEPENDENCE_TRIGGER_SURFACES`, `R_INDEPENDENCE_RULES`, `render_r_independence()`, and updated cross-model authorization rules.
- Modify `AGENTS.md`: add the operative R-INDEPENDENCE stub between R-VERIFY-TIER and R-ORCH.
- Modify `docs/protocol/codex/continuation.md`: expose the same default and the bounded standing policy.
- Modify `.codex/agents/readiness-bridge.toml`: classify and route triggered work without acquiring seat authority.
- Modify `.codex/agents/protocol-director.toml`: require pre-implementation enumeration and durable tested criteria.
- Modify `.codex/agents/protocol-coordinator.toml`: refuse/reroute triggered work missing the required artifacts while retaining the no-production-fix boundary.
- Modify `.codex/agents/protocol-operator.toml`: verify the actual diff against the committed enumeration and synthesize Opus evidence.
- Modify `.codex/agents/lane-v-verifier.toml`: check classification, committed cases, actual diff, and the v2 standing-policy bridge.
- Modify `.codex/agents/money-gate-reviewer.toml`: carry the rule because paid-side-effect gates are an explicit trigger surface.
- Modify `.agents/skills/seat-operator/SKILL.md`: replace obsolete task-authorization-only Opus wording already pinned by prompt-sync tests.

### Bridge contract and runtime

- Modify `scripts/opus_review_bridge.py`: own v2 profile fields, request/result parsing, standing-source resolution, validation order, CLI input, prompt metadata, and normalized evidence.
- Modify `tests/unit/test_opus_review_bridge.py`: own contract, ordering, negative, call-count, CLI, and degradation regression coverage.

### Tests and governance truth

- Modify `tests/unit/test_protocol_prompt_sync.py`: pin canonical R-INDEPENDENCE and standing-policy wording across executable/static surfaces.
- Modify `tests/unit/test_codex_ledger_bridge.py`: prove readiness output exposes R-INDEPENDENCE.
- Modify `tests/unit/test_protocol_doc_integrity.py`: prove the completed AGENTS-sync follow-up is no longer listed as unfinished.
- Modify `tests/unit/test_check_arch_freshness.py` only if an existing assertion needs the new verified stamp shape; do not weaken freshness checks.
- Modify `docs/protocol/claude/independence-first.md`: retain canonical ownership, align the weaker same-model design-review wording, and remove only the completed AGENTS-sync follow-up.
- Modify `ARCHITECTURE.md`: record the executable rule, v2 contract, standing policy, validation order, and one-call boundary with a fresh verified stamp.
- Modify `DECISIONS.md`: append ADR-022; never edit ADR-019, ADR-020, or ADR-021 history.

## Design-Time Independent Enumeration Artifact

This plan is the committed design-time artifact required by R-INDEPENDENCE. The author is Codex. Three cold-context Codex subagents independently reviewed the approved design before implementation:

- `/root/map_bridge_plan`: bridge contract, authorization order, schema, and tests.
- `/root/map_codex_prompts`: executable model, static prompt synchronization, and readiness rendering.
- `/root/map_governance_docs`: ADR ordering, AGENTS placement, canonical-doc consistency, architecture freshness, and integration risks.

This is a **same-model independent review**, explicitly weaker than a cross-model design review. The user limited standing Opus consent to the post-Lane-V call, so no design-time paid call is authorized. The reviewers enumerated these cases, all of which must become enforced tests or explicit protocol assertions:

1. A caller must not explicitly forge `standing-policy:codex-lane-v-opus-v1`; only the bridge may resolve it from an absent source.
2. Missing authorization must not resolve before Git-worktree identity, Pipeline markers, reviewed commit existence, ancestry/trusted-prompt selection, reviewed-HEAD requirement existence, allowed paths, and verification commands are proved.
3. A non-Pipeline repo, wrong review profile, nonexistent commit, missing reviewed-HEAD requirement, invalid command, or scope mismatch must make zero provider calls.
4. A malformed explicit authorization must fail closed and must never fall back to standing consent.
5. Valid explicit `user-task:` and `verify-request:` sources must survive unchanged.
6. Adding required `review_profile` to the strict result shape requires `opus-review/v2`; v1 JSON must be rejected instead of receiving an inferred profile.
7. The provider structured-output schema, Python parser, normalized result, CLI, prompt, and reconciliation input must agree on `review_profile=codex-lane-v`.
8. Unavailable results after authorization resolution must retain both the review profile and standing authorization identity rather than reverting to `missing`.
9. One invocation must make at most one provider-process attempt. Timeout, authentication, sandbox, invalid output, model mismatch, or process failure must not retry or substitute another model.
10. Cross-process uniqueness is governed and auditable by commit/profile/source evidence; this change must not add a mutable global call ledger.
11. Readiness may classify and route R-INDEPENDENCE work but must not perform seat-authority actions.
12. Director, coordinator, operator, Lane V, and money-gate prompts must apply role-specific actions without weakening the shared trigger and two review points.
13. The general paid-spend gate remains intact; only the named post-Lane-V policy is a standing explicit consent exception.
14. Historical ADR-019/020 and old v1 design/plan documents remain unchanged; ADR-022 records the new decision and v2 transition.

---

### Task 1: Make R-INDEPENDENCE The Executable Codex Default

**Files:**
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `AGENTS.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `.codex/agents/readiness-bridge.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.codex/agents/money-gate-reviewer.toml`

**Interfaces:**
- Produces: `R_INDEPENDENCE_TRIGGER_SURFACES: tuple[str, ...]`.
- Produces: `R_INDEPENDENCE_RULES: tuple[str, ...]`.
- Produces: `render_r_independence() -> str`.
- Consumes later: Task 3 updates `CROSS_MODEL_VERIFICATION_RULES` without changing these names.

- [ ] **Step 1: Write the failing model/surface tests**

Add this test to `tests/unit/test_protocol_prompt_sync.py`:

```python
def test_r_independence_is_model_backed_and_surface_synced():
    assert model.R_INDEPENDENCE_TRIGGER_SURFACES == (
        "input rendered or composed into a parseable or executable context",
        "authority or security-boundary enforcement",
        "side-effect gating",
        "schema validation whose acceptance grants trust",
    )

    rendered = model.render_r_independence()
    required = (
        "R-INDEPENDENCE",
        "standing default",
        "before implementation",
        "independent design-time enumeration",
        "abuse cases, edge cases, and coverage targets",
        "different model or harness is preferred",
        "same-model independent reviewer is weaker",
        "committed plan or equivalent durable artifact",
        "independent reviewer verifies the actual diff",
        "Lane V plus verdict-blind Opus",
        "R-VERIFY-TIER",
        "docs/protocol/claude/independence-first.md",
    )
    for phrase in required:
        assert phrase in rendered

    shared_surface_phrases = (
        "R-INDEPENDENCE",
        "adversarial-surface",
        "before implementation",
        "independent design-time enumeration",
        "enforced-and-tested",
        "verify the actual diff",
        "R-VERIFY-TIER",
    )
    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
    ):
        text = _compact(_read(path))
        for phrase in shared_surface_phrases:
            assert phrase in text, (path, phrase)

    assert "R-INDEPENDENCE" in model.render_start_session_inhabitance()
```

Extend `test_readiness_render_codex_surfaces_ledger_bridge()` in `tests/unit/test_codex_ledger_bridge.py`:

```python
    assert "R-INDEPENDENCE:" in rendered
    assert "independent design-time enumeration" in rendered
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py::test_r_independence_is_model_backed_and_surface_synced \
  tests/unit/test_codex_ledger_bridge.py::test_readiness_render_codex_surfaces_ledger_bridge -q
```

Expected: FAIL because `R_INDEPENDENCE_TRIGGER_SURFACES` and `render_r_independence()` do not exist.

- [ ] **Step 3: Add the canonical executable model**

Add near the existing risk-tier contract in `scripts/codex_protocol_model.py`:

```python
R_INDEPENDENCE_TRIGGER_SURFACES = (
    "input rendered or composed into a parseable or executable context",
    "authority or security-boundary enforcement",
    "side-effect gating",
    "schema validation whose acceptance grants trust",
)

R_INDEPENDENCE_RULES = (
    "R-INDEPENDENCE is the standing default for Pipeline Codex work.",
    "Before implementation, classify whether the change touches an adversarial-surface: "
    + "; ".join(R_INDEPENDENCE_TRIGGER_SURFACES)
    + ".",
    "Triggered work requires an independent design-time enumeration of abuse cases, edge cases, and coverage targets before implementation.",
    "A different model or harness is preferred; a same-model independent reviewer is weaker and must be identified as such.",
    "Fold the enumeration into enforced-and-tested acceptance criteria in a committed plan or equivalent durable artifact.",
    "Before completion, an independent reviewer verifies the actual diff against the committed cases.",
    "For Codex-authored adversarial work, Lane V plus verdict-blind Opus supplies the per-task cross-model pair.",
    "R-VERIFY-TIER still prohibits redundant same-question passes; it does not remove the earlier new-perspective review.",
    "Non-adversarial, read-only, and hermetic work uses the smallest sufficient profile.",
    "Canonical full rule: docs/protocol/claude/independence-first.md.",
)


def render_r_independence() -> str:
    """Return the Pipeline Codex independence-first contract."""
    lines = ["R-INDEPENDENCE:"]
    lines.extend(f"- {rule}" for rule in R_INDEPENDENCE_RULES)
    return "\n".join(lines)
```

Add one summary entry to `ACTIVE_KERNEL_INVARIANTS`:

```python
    (
        "independence-first verification",
        "classify adversarial surfaces before implementation and require design-time enumeration plus independent actual-diff verification",
    ),
```

Wire the renderer into `render_start_session_inhabitance()` immediately after `render_codex_execution_tiers()`:

```python
    lines.append(render_codex_execution_tiers())
    lines.append(render_r_independence())
```

Add this compact line to `render_surface_summary()`:

```python
        "R-INDEPENDENCE: adversarial-surface work requires design-time enumeration and independent actual-diff verification",
```

Print the full section from `main()` after `## Kernel Contract`:

```python
    print("## R-INDEPENDENCE")
    print(render_r_independence())
    print()
```

- [ ] **Step 4: Add the operative root and Codex continuation text**

Insert this block in `AGENTS.md` between R-VERIFY-TIER and R-ORCH, and add the same semantic block near the risk-tier section in `docs/protocol/codex/continuation.md`:

```markdown
# Independence-first verification (R-INDEPENDENCE)
Scope: both.
Trigger: before designing or implementing, classify whether the change touches an adversarial-surface: input rendered or composed into a parseable or executable context; authority or security-boundary enforcement; side-effect gating; or schema validation whose acceptance grants trust.
Action: triggered work requires an independent design-time enumeration of abuse cases, edge cases, and coverage targets before implementation. A different model or harness is preferred; a same-model independent reviewer is weaker and must be identified. Fold the result into enforced-and-tested acceptance criteria in a committed plan or equivalent durable artifact. Before completion, an independent reviewer must verify the actual diff against those cases. For Codex-authored adversarial work, Lane V plus verdict-blind Opus supplies the per-task cross-model pair.
Deduplication: R-VERIFY-TIER still prohibits redundant same-question passes. Non-adversarial, read-only, and hermetic work uses the smallest sufficient profile.
Evidence: the committed design-time enumeration artifact and the independent verification report naming the reviewer and harness.
Details: `docs/protocol/claude/independence-first.md` (ADR-019).
```

Use Markdown `## R-INDEPENDENCE` rather than an H1 in the continuation adapter.

- [ ] **Step 5: Synchronize the six core Codex prompts**

Add this shared block to each named `.codex/agents/*.toml` developer prompt:

```text
R-INDEPENDENCE:
- R-INDEPENDENCE is the standing default for adversarial-surface work.
- Before implementation, classify input-to-parser/executable composition, authority or security-boundary enforcement, side-effect gating, and trust-granting schema validation.
- Triggered work requires an independent design-time enumeration of abuse cases, edge cases, and coverage targets before implementation.
- A different model or harness is preferred; a same-model independent reviewer is weaker and must be identified.
- Fold the result into enforced-and-tested acceptance criteria in a committed plan or equivalent durable artifact.
- Before completion, an independent reviewer must verify the actual diff against the committed cases.
- R-VERIFY-TIER still forbids redundant same-question passes.
```

Add exactly one role-specific line after that shared block:

```text
readiness-bridge: Classify and route only; readiness authority does not perform the review or implementation.
protocol-director: Obtain the enumeration, commit the tested criteria, and include it in the verify-request.
protocol-coordinator: Refuse or reroute triggered implementation lacking the enumeration or final independent verification; do not author the fix.
protocol-operator: Verify the actual diff against the committed enumeration before final synthesis.
lane-v-verifier: Check the classification, enumeration artifact, enforced cases, and actual diff.
money-gate-reviewer: Treat paid-side-effect gates as an adversarial surface and verify the actual diff against the committed cases.
```

Do not add seat authority to readiness, coordinator, or read-only verifier prompts.

- [ ] **Step 6: Run focused tests and verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_codex_ledger_bridge.py -q
```

Expected: PASS.

- [ ] **Step 7: Review the scoped diff and commit Task 1**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_codex_ledger_bridge.py \
  scripts/codex_protocol_model.py \
  AGENTS.md \
  docs/protocol/codex/continuation.md \
  .codex/agents/readiness-bridge.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .codex/agents/money-gate-reviewer.toml
env -u GIT_INDEX_FILE git add -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_codex_ledger_bridge.py \
  scripts/codex_protocol_model.py \
  AGENTS.md \
  docs/protocol/codex/continuation.md \
  .codex/agents/readiness-bridge.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .codex/agents/money-gate-reviewer.toml
env -u GIT_INDEX_FILE git commit -m "feat(protocol): make R-INDEPENDENCE the Codex default" -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_codex_ledger_bridge.py \
  scripts/codex_protocol_model.py \
  AGENTS.md \
  docs/protocol/codex/continuation.md \
  .codex/agents/readiness-bridge.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .codex/agents/money-gate-reviewer.toml
```

Expected: one Task 1 commit containing only the listed files.

---

### Task 2: Introduce The Explicit `opus-review/v2` Profile Contract

**Files:**
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `scripts/opus_review_bridge.py`

**Interfaces:**
- Produces: `CODEX_LANE_V_REVIEW_PROFILE = "codex-lane-v"`.
- Produces: `STANDING_CODEX_LANE_V_AUTHORIZATION = "standing-policy:codex-lane-v-opus-v1"`.
- Produces: `ReviewRequest.review_profile: str`.
- Produces: `OpusReview.review_profile: str` serialized under `opus-review/v2`.
- Preserves: `RECONCILIATION_SCHEMA_VERSION = "opus-reconciliation/v1"`.
- Consumes later: Task 3 resolves absent authorization after full scope validation.

- [ ] **Step 1: Write the failing v2 contract tests**

Update `_structured_payload()` so the desired provider output is explicit:

```python
def _structured_payload(
    *,
    status: str = "pass",
    findings: list[dict[str, object]] | None = None,
    reviewed_head: str = HEAD,
    reviewed_base: str | None = BASE,
) -> dict[str, object]:
    return {
        "schema_version": "opus-review/v2",
        "review_profile": "codex-lane-v",
        "reviewed_head": reviewed_head,
        "reviewed_base": reviewed_base,
        "status": status,
        "findings": [] if findings is None else findings,
    }
```

Add these tests:

```python
def test_opus_review_v2_round_trip_preserves_codex_lane_v_profile() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    payload = review.to_dict()
    assert payload["schema_version"] == "opus-review/v2"
    assert payload["review_profile"] == "codex-lane-v"
    assert bridge.OpusReview.from_dict(payload) == review


def test_opus_review_from_dict_rejects_v1_without_profile() -> None:
    payload = _normalized_pass_payload()
    payload["schema_version"] = "opus-review/v1"
    payload.pop("review_profile", None)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema"


def test_parse_structured_review_rejects_wrong_profile() -> None:
    payload = _structured_payload()
    payload["review_profile"] = "money-gate"

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.parse_structured_review(
            payload,
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile="codex-lane-v",
            effective_model="claude-opus-4-7",
            authorization_source="user-task:verification-1",
        )

    assert excinfo.value.reason == "invalid_schema"
```

Change the CLI test name to `test_review_cli_requires_and_emits_review_profile`, pass `--review-profile codex-lane-v`, assert `request.review_profile`, and assert both v2/profile output fields.

Add `review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE` to both direct `ReviewRequest(...)` fixtures, every `OpusReview.unavailable(...)` test construction, and every `parse_structured_review(...)` call. Use this audit after editing:

```bash
rg -n "ReviewRequest\(|OpusReview\.unavailable\(|parse_structured_review\(" tests/unit/test_opus_review_bridge.py
```

Every displayed construction must supply the explicit profile or receive it from `_structured_payload()` plus `expected_profile`.

- [ ] **Step 2: Run the v2 tests and verify RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py::test_opus_review_v2_round_trip_preserves_codex_lane_v_profile \
  tests/unit/test_opus_review_bridge.py::test_opus_review_from_dict_rejects_v1_without_profile \
  tests/unit/test_opus_review_bridge.py::test_parse_structured_review_rejects_wrong_profile \
  tests/unit/test_opus_review_bridge.py::test_review_cli_requires_and_emits_review_profile -q
```

Expected: FAIL because v2/profile fields and CLI input do not exist.

- [ ] **Step 3: Add constants and strict fields**

At the top of `scripts/opus_review_bridge.py`, use:

```python
SCHEMA_VERSION = "opus-review/v2"
RECONCILIATION_SCHEMA_VERSION = "opus-reconciliation/v1"
CODEX_LANE_V_REVIEW_PROFILE = "codex-lane-v"
STANDING_CODEX_LANE_V_AUTHORIZATION = (
    "standing-policy:codex-lane-v-opus-v1"
)
```

Add `review_profile` to `_REVIEW_FIELDS` and `_STRUCTURED_REVIEW_FIELDS`.

In `OPUS_OUTPUT_SCHEMA`, add:

```python
        "review_profile": {"const": CODEX_LANE_V_REVIEW_PROFILE},
```

and include `review_profile` in its `required` list.

- [ ] **Step 4: Thread the explicit profile through request/result contracts**

Change the dataclasses to include required fields:

```python
@dataclass(frozen=True)
class ReviewRequest:
    repo_root: Path
    reviewed_head: str
    reviewed_base: str | None
    requirement_paths: tuple[Path, ...]
    allowed_paths: tuple[str, ...]
    verification_commands: tuple[str, ...]
    review_profile: str
    authorization_source: str
    max_turns: int = DEFAULT_MAX_TURNS
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class OpusReview:
    reviewed_head: str
    reviewed_base: str | None
    review_profile: str
    effective_model: str | None
    status: str
    findings: tuple[Finding, ...]
    authorization_source: str
    unavailable_reason: str | None
```

Add these validators near the authorization helpers:

```python
def _validated_review_profile(value: str) -> str:
    profile = value.strip()
    if profile != CODEX_LANE_V_REVIEW_PROFILE:
        raise ReviewContractError(
            "invalid_profile",
            f"review_profile must be {CODEX_LANE_V_REVIEW_PROFILE!r}",
        )
    return profile


def _schema_review_profile(value: object) -> str:
    try:
        return _validated_review_profile(_required_string(value, "review_profile"))
    except ReviewContractError as exc:
        raise ReviewContractError(
            "invalid_schema", f"invalid review_profile: {value!r}"
        ) from exc
```

Call `_validated_review_profile(request.review_profile)` from
`_validate_request_shape()` before path and command iteration.

Thread `review_profile` through:

- `OpusReview.unavailable()` parameters and returned object;
- `OpusReview.from_dict()` exact-field parsing;
- `OpusReview.to_dict()`;
- `parse_structured_review(..., expected_profile: str, ...)` and its scope check;
- `_unavailable()`;
- every call to `parse_structured_review()`.

Use this exact check inside `parse_structured_review()` before status parsing:

```python
    review_profile = _schema_review_profile(payload.get("review_profile"))
    if review_profile != _validated_review_profile(expected_profile):
        raise ReviewContractError(
            "reviewed_scope_mismatch",
            f"expected profile {expected_profile}, got {review_profile}",
        )
```

Use `review_profile=_schema_review_profile(value.get("review_profile"))` when parsing normalized v2 JSON.

- [ ] **Step 5: Add CLI and prompt metadata**

Add the required CLI option:

```python
    review_parser.add_argument(
        "--review-profile",
        choices=(CODEX_LANE_V_REVIEW_PROFILE,),
        required=True,
    )
```

Pass it into `ReviewRequest`:

```python
        review_profile=args.review_profile,
```

Add this line to `build_review_prompt()` immediately before authorization:

```python
            f"Review profile: {_validated_review_profile(request.review_profile)}",
```

At this task, preserve the existing task-level authorization requirement; Task 3 changes only the absent-source behavior after the v2 profile contract is green.

- [ ] **Step 6: Run the full bridge test file and verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py -q
```

Expected: PASS, with explicit task authorization still used by existing successful-review fixtures.

- [ ] **Step 7: Confirm no stale runtime v1/profile omissions and commit Task 2**

Run:

```bash
rg -n 'opus-review/v1' scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
rg -n "ReviewRequest\(|OpusReview\.unavailable\(|parse_structured_review\(" \
  scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
```

Expected: the first command finds only the deliberate v1 rejection test; every relevant constructor/call is profile-aware; diff check is clean.

Commit:

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git commit -m "feat(verify): add explicit Opus Lane-V review profile" -- \
  scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
```

---

### Task 3: Resolve Narrow Standing Authorization After Immutable Scope Proof

**Files:**
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `scripts/opus_review_bridge.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.agents/skills/seat-operator/SKILL.md`

**Interfaces:**
- Produces: `_resolved_authorization_source(request: ReviewRequest) -> str`.
- Preserves: `_validated_authorization_source()` accepts only explicit `user-task:` and `verify-request:` sources.
- Produces normalized v2 results carrying `review_profile` and resolved authorization identity for pass, issues, and unavailable.
- Preserves: one provider runner call per `review()` invocation and no retries.

- [ ] **Step 1: Replace the obsolete missing-authorization tests with standing-policy RED tests**

Replace the old no-call missing-authorization test with:

```python
def test_missing_authorization_uses_standing_policy_and_invokes_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request(tmp_path, authorization="")
    calls = 0
    monkeypatch.setattr(
        bridge,
        "_resolve_claude_executable",
        lambda environment: Path(sys.executable),
    )

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)

    assert calls == 1
    assert result.status == "pass"
    assert result.review_profile == "codex-lane-v"
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )
```

Replace the whitespace test with:

```python
def test_whitespace_authorization_uses_standing_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request(tmp_path, authorization=" \t ")
    calls = 0
    monkeypatch.setattr(
        bridge,
        "_resolve_claude_executable",
        lambda environment: Path(sys.executable),
    )

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)
    assert calls == 1
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )
```

Add these negative/preservation tests:

```python
def test_standing_authorization_requires_exact_review_profile(
    tmp_path: Path,
) -> None:
    request = replace(
        _request(tmp_path, authorization=""),
        review_profile="money-gate",
    )
    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run for a wrong profile")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_profile"
    assert calls == 0


@pytest.mark.parametrize(
    "authorization",
    ["user-task:verification-1", "verify-request:route-22"],
)
def test_explicit_authorization_sources_are_preserved(
    tmp_path: Path, authorization: str
) -> None:
    request = _request(tmp_path, authorization=authorization)

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)
    assert result.authorization_source == authorization


def test_explicit_standing_policy_source_is_rejected(
    tmp_path: Path,
) -> None:
    request = _request(
        tmp_path,
        authorization="standing-policy:codex-lane-v-opus-v1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request)

    assert excinfo.value.reason == "invalid_authorization"


def test_standing_authorization_requires_requirement_at_reviewed_head(
    tmp_path: Path,
) -> None:
    request = _committed_request(tmp_path)
    late_requirement = tmp_path / "late-requirement.md"
    late_requirement.write_text("mutable only\n", encoding="utf-8")
    request = replace(
        request,
        requirement_paths=(late_requirement,),
        authorization_source="",
    )
    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run before snapshot scope proof")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"
    assert calls == 0
```

Rename the existing missing-authorization commit and Pipeline-identity tests to
`test_standing_authorization_requires_existing_reviewed_commits` and
`test_standing_authorization_requires_pipeline_identity`. Keep their blank
source, pass a counting forbidden runner to `review()`, and assert the count is
zero after the existing `invalid_scope` / `not_pipeline_repo` assertions.
Likewise set a blank source in the existing invalid-command and explicit-base
scope tests; their forbidden runners already prove the provider is not called.

Extend `test_review_normalizes_timeout_without_retry` with a blank authorization request and:

```python
    assert result.review_profile == "codex-lane-v"
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )
```

- [ ] **Step 2: Update prompt-sync tests for the new standing policy**

In `test_cross_model_opus_verification_is_model_backed_and_surface_synced()`, replace obsolete parent-authorization assertions with:

```python
        "review profile codex-lane-v",
        "standing-policy:codex-lane-v-opus-v1",
        "only when the authorization source is absent",
        "malformed explicit authorization never falls back",
        "one provider process attempt and no automatic retry",
        "one invocation per unchanged Lane V verification",
        "does not authorize design-time Opus or any other paid call",
        "opus-review/v2",
```

Add these exact report fields:

```python
        "Review profile:",
        "Authorization identity:",
```

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py::test_missing_authorization_uses_standing_policy_and_invokes_once \
  tests/unit/test_opus_review_bridge.py::test_standing_authorization_requires_exact_review_profile \
  tests/unit/test_opus_review_bridge.py::test_explicit_standing_policy_source_is_rejected \
  tests/unit/test_opus_review_bridge.py::test_review_normalizes_timeout_without_retry \
  tests/unit/test_protocol_prompt_sync.py::test_cross_model_opus_verification_is_model_backed_and_surface_synced -q
```

Expected: FAIL because missing authorization still returns `authorization_missing` and protocol surfaces still require parent task authorization.

- [ ] **Step 4: Separate explicit-source validation from normalized-result validation**

Keep `_AUTHORIZATION_RE` unchanged so it accepts only explicit task/verify-request sources. Keep `_validated_authorization_source()` as the caller-input validator.

Replace `_schema_authorization_source()` with:

```python
def _schema_authorization_source(value: str) -> str:
    source = value.strip()
    if source == STANDING_CODEX_LANE_V_AUTHORIZATION:
        return source
    try:
        return _validated_authorization_source(source)
    except ReviewContractError as exc:
        raise ReviewContractError(
            "invalid_schema", f"invalid authorization_source: {value!r}"
        ) from exc
```

In `OpusReview.unavailable()`, retain the special
`authorization_missing -> "missing"` branch, but change the other branch to:

```python
        else:
            source = _schema_authorization_source(source)
```

This is required so timeout, sandbox, provider, and schema degradation can
record the bridge-generated standing identity while explicit caller input is
still validated by `_validated_authorization_source()` before resolution.

Add:

```python
def _resolved_authorization_source(request: ReviewRequest) -> str:
    _validated_review_profile(request.review_profile)
    source = request.authorization_source.strip()
    if source:
        return _validated_authorization_source(source)
    return STANDING_CODEX_LANE_V_AUTHORIZATION
```

This split is load-bearing: callers cannot explicitly submit the standing identity, while normalized bridge output can record it.

- [ ] **Step 5: Reorder `review()` so standing consent follows immutable scope proof**

Replace the early missing-authorization return and reorder the function around the snapshot as follows:

```python
    request = _canonical_review_request(request)
    _validate_request_shape(request)
    _pipeline_root(source)
    _require_commit(source, request.reviewed_head, "reviewed_head")
    if request.reviewed_base is not None:
        _require_commit(source, request.reviewed_base, "reviewed_base")

    trusted_revision = _trusted_prompt_revision(source, request)
    trusted_agent_prompt = _load_agent_prompt_at_revision(
        source, trusted_revision
    )
    if request.authorization_source.strip():
        _validated_authorization_source(request.authorization_source)

    with _immutable_review_snapshot(request) as snapshot:
        snapshot_request = _snapshot_request(request, snapshot)
        _validate_request(snapshot_request)
        authorization_source = _resolved_authorization_source(request)
        request = replace(
            request,
            authorization_source=authorization_source,
        )
        snapshot_request = replace(
            snapshot_request,
            authorization_source=authorization_source,
        )

        child_env = build_claude_environment()
        claude_executable = _resolve_claude_executable(child_env)
        if claude_executable is None:
            return _unavailable(request, "claude_not_found")
```

Move the existing `try` block beginning with
`with _sandbox_runtime(source, snapshot) as sandbox:` through the final
structured-result parse immediately after the shown Claude-executable check.
Retain those statements byte-for-byte except for indentation and the resolved
`request` / `snapshot_request` variables.

Ensure `_unavailable()` passes both:

```python
        review_profile=request.review_profile,
        authorization_source=request.authorization_source,
```

Update `build_review_prompt()` to call `_resolved_authorization_source(request)` after `_validate_request(request)` so direct prompt construction follows the same fail-closed validation order.

- [ ] **Step 6: Update canonical cross-model wording and report fields**

Replace the obsolete authorization lines in `CROSS_MODEL_VERIFICATION_RULES` with exact rules equivalent to:

```python
    "the request declares review profile codex-lane-v and normalized evidence uses opus-review/v2",
    "after Pipeline identity, reviewed commits, and immutable scope validation, missing authorization resolves to standing-policy:codex-lane-v-opus-v1 only when the authorization source is absent",
    "valid explicit user-task:<id> and verify-request:<id> sources remain accepted; malformed explicit authorization never falls back",
    "the standing policy permits exactly one provider process attempt and no automatic retry, with one invocation per unchanged Lane V verification",
    "standing consent does not authorize design-time Opus or any other paid call",
```

Mirror these rules in:

- `docs/protocol/codex/continuation.md`;
- `.codex/agents/protocol-operator.toml`;
- `.codex/agents/lane-v-verifier.toml`; and
- `.agents/skills/seat-operator/SKILL.md`.

Add these report lines to both operator prompts:

```text
- Review profile: codex-lane-v
- Authorization identity: standing-policy / explicit task source
```

- [ ] **Step 7: Run bridge and prompt tests and verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: PASS. Existing timeout test still proves one call and no retry.

- [ ] **Step 8: Inspect call order and commit Task 3**

Run:

```bash
rg -n "authorization_missing|_resolved_authorization_source|_immutable_review_snapshot|_validate_request\(snapshot_request\)|runner or _run_process_group" scripts/opus_review_bridge.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/opus_review_bridge.py \
  tests/unit/test_opus_review_bridge.py \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/protocol/codex/continuation.md \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .agents/skills/seat-operator/SKILL.md
```

Expected: snapshot validation precedes standing resolution; the provider runner appears once in the function; diff check is clean.

Commit:

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/opus_review_bridge.py \
  tests/unit/test_opus_review_bridge.py \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/protocol/codex/continuation.md \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .agents/skills/seat-operator/SKILL.md
env -u GIT_INDEX_FILE git commit -m "feat(verify): authorize one standing Lane-V Opus attempt" -- \
  scripts/opus_review_bridge.py \
  tests/unit/test_opus_review_bridge.py \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/protocol/codex/continuation.md \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .agents/skills/seat-operator/SKILL.md
```

---

### Task 4: Record ADR-022 And Synchronize Governance Truth

**Files:**
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`
- Modify: `docs/protocol/claude/independence-first.md`
- Modify: `ARCHITECTURE.md`
- Modify: `DECISIONS.md`

**Interfaces:**
- Consumes: Task 1 `render_r_independence()` and Task 3 standing-policy/v2 behavior.
- Produces: append-only ADR-022 and current architecture truth.
- Preserves: historical ADR-019/020/021 text and historical v1 design/plan files.

- [ ] **Step 1: Write failing governance-truth tests**

Extend `test_cross_model_opus_bridge_is_mapped_in_architecture_and_decisions()`:

```python
    assert "## ADR-022: Make Codex R-INDEPENDENCE operative and authorize one standing Lane-V Opus attempt" in decisions
    assert "standing-policy:codex-lane-v-opus-v1" in architecture
    assert "opus-review/v2" in architecture
    assert "R-INDEPENDENCE" in architecture
    assert "one provider process" in architecture
```

Add to `tests/unit/test_protocol_doc_integrity.py`:

```python
def test_independence_first_doc_no_longer_lists_agents_sync_as_unfinished():
    text = (ROOT / "docs/protocol/claude/independence-first.md").read_text(
        encoding="utf-8"
    )
    assert "Sync the operative stub into `AGENTS.md`" not in text
    assert "Mechanize the cross-model requirement" in text
    assert "dispatch templates" in text
```

Use the module's existing `ROOT` constant rather than adding a second root.

- [ ] **Step 2: Run governance tests and verify RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py::test_cross_model_opus_bridge_is_mapped_in_architecture_and_decisions \
  tests/unit/test_protocol_doc_integrity.py::test_independence_first_doc_no_longer_lists_agents_sync_as_unfinished -q
```

Expected: FAIL because ADR-022 and the current architecture/canonical-doc updates do not exist.

- [ ] **Step 3: Align the canonical independence document without duplicating it**

In `docs/protocol/claude/independence-first.md`, preserve the prohibition on author self-review but replace the same-model bullet under “What independent means” with:

```markdown
- Weaker: a different seat or cold-context reviewer of the same model with a genuinely adversarial prompt. For adversarial design-time enumeration this must be identified as weaker evidence; it does not replace the preferred cross-model per-task verification.
- **Not** independent: the author reviewing its own plan or implementation, even under a renamed role.
```

Remove only this completed follow-up:

```markdown
- Sync the operative stub into `AGENTS.md` (the Codex twin) once it is not
  mid-edit by a peer lane, per the CLAUDE/AGENTS operative-split map.
```

Retain the `check_go_schema.py` and dispatch-template follow-ups.

- [ ] **Step 4: Append ADR-022 exactly once**

Append this decision after ADR-021 in `DECISIONS.md`:

```markdown
## ADR-022: Make Codex R-INDEPENDENCE operative and authorize one standing Lane-V Opus attempt

**Status:** Accepted (user-approved design, 2026-07-12)

**Context:**
ADR-019 made independence-first verification standing doctrine but left the Codex operative stub and executable role surfaces unfinished. ADR-020 required one blind Opus pass after Codex Lane V, yet its task-level authorization rule made that required pass degrade whenever a parent prompt omitted repeated consent. The user-principal directed that R-INDEPENDENCE become the Pipeline Codex default and granted standing consent for only the existing bounded post-Lane-V Opus attempt.

**Decision:**
Pipeline Codex classifies the four ADR-019 adversarial surfaces before implementation. Triggered work requires a committed independent design-time abuse/edge/coverage enumeration and independent actual-diff verification before completion. The Codex executable model and core role prompts carry that default. For the exact `codex-lane-v` review profile, after Pipeline identity, reviewed commits, immutable reviewed-HEAD scope, and command validation, an absent authorization source resolves to `standing-policy:codex-lane-v-opus-v1`. Explicit `user-task:` and `verify-request:` sources remain valid; malformed or explicitly forged standing sources fail closed. The normalized review schema advances to `opus-review/v2` with a required profile; v1 review JSON is rejected rather than inferred, while `opus-reconciliation/v1` remains unchanged. One invocation launches at most one provider process and never retries or substitutes another reviewer. Protocol rules allow one invocation per unchanged Lane V verification. Operator authority and every other paid-spend or side-effect gate remain unchanged.

**Consequences:**
- This extends ADR-019 and supersedes only ADR-020's task-authorization, v1-contract, and separately-authorized-live-smoke details for the named Pipeline Lane V profile.
- Unavailable credentials, network, sandbox, provider, or valid output remain visible degraded Codex-only evidence after standing authorization is recorded.
- The bridge enforces one provider process per invocation. Cross-process uniqueness remains auditable from profile, authorization identity, and reviewed commits rather than adding a mutable global call ledger.
- Standing consent does not authorize design-time Opus or any unrelated paid operation.
```

- [ ] **Step 5: Update `ARCHITECTURE.md` against the landed implementation**

Run these read-only commands first:

```bash
env -u GIT_INDEX_FILE git rev-parse --short HEAD
rg -n "def render_r_independence|def _resolved_authorization_source|def review" \
  scripts/codex_protocol_model.py scripts/opus_review_bridge.py
```

Set the `*Last verified:*` stamp to `2026-07-12 @` followed by the exact short SHA printed above. Add module-map rows for `render_r_independence` and `_resolved_authorization_source` using the exact line numbers printed by `rg`.

Replace the general paid-spend sentence with wording that retains the gate and names the sole standing exception:

```markdown
- Pushes, lock actions, cursor consumption, pod spend, target checkout refresh,
  production generation, and paid API spend require explicit authorization or
  a valid routed executor. The sole standing paid-call exception is
  `standing-policy:codex-lane-v-opus-v1`, limited to one post-Lane-V Opus
  attempt under the exact Pipeline `codex-lane-v` profile.
```

Extend the Lane V invariant with these verified facts:

```markdown
The Codex model applies R-INDEPENDENCE before implementation: it classifies the four adversarial surfaces, requires a durable independent design-time enumeration for triggered work, and requires independent actual-diff verification before completion. Lane V requests declare `codex-lane-v`. After Pipeline identity, commits, immutable reviewed-HEAD scope, and command validation, an absent task source resolves to `standing-policy:codex-lane-v-opus-v1`; malformed explicit sources never fall back. Normalized evidence is `opus-review/v2` and records the profile and authorization identity. One invocation launches at most one provider process and never retries. Unavailability remains visibly degraded and the operator retains GO/NITS/FAIL authority.
```

- [ ] **Step 6: Run focused docs/tests and verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_check_arch_freshness.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
```

Expected: tests PASS and smoke ends `OK`.

- [ ] **Step 7: Confirm append-only scope and commit Task 4**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  docs/protocol/claude/independence-first.md \
  ARCHITECTURE.md DECISIONS.md
env -u GIT_INDEX_FILE git diff -- DECISIONS.md
```

Expected: ADR-022 is appended after ADR-021; ADR-019/020/021 have no removed or changed lines.

Commit:

```bash
env -u GIT_INDEX_FILE git add -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  docs/protocol/claude/independence-first.md \
  ARCHITECTURE.md DECISIONS.md
env -u GIT_INDEX_FILE git commit -m "docs(adr): enact Codex independence and standing Opus consent" -- \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  docs/protocol/claude/independence-first.md \
  ARCHITECTURE.md DECISIONS.md
```

---

### Task 5: Full Verification, Independent Lane V, And One Live Opus Attempt

**Files:**
- Verify only: all files changed since the branch point.
- No file mutation unless a real finding requires returning to the owning implementation task.

**Interfaces:**
- Consumes: all Task 1–4 commits.
- Produces: fresh local verification evidence and exactly one standing-authorized Opus result for the current unchanged HEAD.

- [ ] **Step 1: Hot-refresh branch and changed-scope evidence**

Run:

```bash
env -u GIT_INDEX_FILE git log --oneline -8
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git merge-base main HEAD
env -u GIT_INDEX_FILE git diff --name-only "$(env -u GIT_INDEX_FILE git merge-base main HEAD)"..HEAD
```

Expected: the worktree is clean and the changed paths match this plan. If `main` advanced into an overlapping path, merge/rebase it before verification and rerun the relevant focused tests.

- [ ] **Step 2: Run the full deterministic verification set**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_check_arch_freshness.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -c '
from pathlib import Path
from scripts import check_doc_claims as c
root = Path.cwd()
status = c.classify_sha_ref_baseline(c.check_sha_refs(c.SHA_DEFAULT_DOCS, root), root)
print(status.warning_line)
print(f"matches_baseline={status.matches_baseline} count={status.count} new_or_changed={status.new_or_changed_count}")
raise SystemExit(0 if status.matches_baseline else 1)
'
env -u GIT_INDEX_FILE git diff --check "$(env -u GIT_INDEX_FILE git merge-base main HEAD)"..HEAD
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
```

Expected: focused and full suites PASS; SHA baseline reports `matches_baseline=True` and `new_or_changed=0`; diff check exits 0; smoke ends `OK`.

- [ ] **Step 3: Perform the primary read-only Codex Lane V review**

Use a fresh read-only Lane V reviewer against the exact branch-point-to-HEAD range. The reviewer must verify:

- every design-time enumeration case in this plan;
- all strict schema fields and v1 rejection;
- authorization resolution order against the immutable reviewed-HEAD snapshot;
- explicit-standing-source rejection;
- zero calls on invalid repo/profile/scope/authorization;
- one call and no retry on provider failure;
- static/executable prompt synchronization;
- ADR append-only history and architecture truth.

Record the provisional Codex verdict internally. Do not pass that verdict, report, findings, or conclusion to Opus.

- [ ] **Step 4: Run exactly one live standing-authorized Opus review for this HEAD**

Run this command once. Do not add `--authorization-source`:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/opus_review_bridge.py review \
  --repo-root . \
  --review-profile codex-lane-v \
  --head "$(env -u GIT_INDEX_FILE git rev-parse HEAD)" \
  --base "$(env -u GIT_INDEX_FILE git merge-base main HEAD)" \
  --requirement docs/superpowers/specs/2026-07-12-codex-r-independence-standing-opus-authorization-design.md \
  --requirement docs/superpowers/plans/2026-07-12-codex-r-independence-standing-opus-authorization.md \
  --allow-path docs/superpowers/specs/2026-07-12-codex-r-independence-standing-opus-authorization-design.md \
  --allow-path docs/superpowers/plans/2026-07-12-codex-r-independence-standing-opus-authorization.md \
  --allow-path AGENTS.md \
  --allow-path ARCHITECTURE.md \
  --allow-path DECISIONS.md \
  --allow-path scripts/codex_protocol_model.py \
  --allow-path scripts/opus_review_bridge.py \
  --allow-path docs/protocol/codex/continuation.md \
  --allow-path docs/protocol/claude/independence-first.md \
  --allow-path .agents/skills/seat-operator/SKILL.md \
  --allow-path .codex/agents/readiness-bridge.toml \
  --allow-path .codex/agents/protocol-director.toml \
  --allow-path .codex/agents/protocol-coordinator.toml \
  --allow-path .codex/agents/protocol-operator.toml \
  --allow-path .codex/agents/lane-v-verifier.toml \
  --allow-path .codex/agents/money-gate-reviewer.toml \
  --allow-path tests/unit/test_opus_review_bridge.py \
  --allow-path tests/unit/test_protocol_prompt_sync.py \
  --allow-path tests/unit/test_codex_ledger_bridge.py \
  --allow-path tests/unit/test_protocol_doc_integrity.py \
  --allow-path tests/unit/test_check_arch_freshness.py \
  --verification-command "env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_bridge.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_check_arch_freshness.py -q" \
  --verification-command "env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py"
```

Expected normalized output:

```json
{
  "schema_version": "opus-review/v2",
  "review_profile": "codex-lane-v",
  "authorization_source": "standing-policy:codex-lane-v-opus-v1",
  "status": "pass | issues | unavailable"
}
```

Interpret the full strict object, not only this abbreviated field view.

- [ ] **Step 5: Reconcile without retrying the unchanged review**

- If status is `pass`, reconcile with the provisional Codex verdict and zero findings.
- If status is `issues`, disposition every finding as confirmed, evidence-backed disproved, or unresolved. Confirmed important/critical or any unresolved finding blocks GO; confirmed minor requires NITS.
- If status is `unavailable`, record the exact reason and `degraded_cross_model_review=true`; do not retry or launch a substitute reviewer.
- If a confirmed finding causes a code change, return to the owning task, create a new commit, rerun deterministic verification, then run a new Lane V plus one Opus attempt for the **new HEAD**. That is a new verification, not a retry of the unchanged review.

- [ ] **Step 6: Final scope/status evidence**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -8
env -u GIT_INDEX_FILE git diff --stat "$(env -u GIT_INDEX_FILE git merge-base main HEAD)"..HEAD
env -u GIT_INDEX_FILE git diff --check "$(env -u GIT_INDEX_FILE git merge-base main HEAD)"..HEAD
```

Expected: clean feature worktree, coherent task commits, scoped diff, and no whitespace errors. Do not push.
