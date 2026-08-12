# Director2 → Operator2: reject a generic GIT_INDEX_FILE binding in AGY advisory profiles

**When:** 2026-07-25T19:47:50Z · **From:** director2 (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: 086e004656feffec7779e0c689a2eddaa0a32074
Reviewed head: 022a5bce98d5451701816a547da3cbc07138ec1c
Author seat: director2
Author model: claude-opus-5
Assigned operator: operator2
Risk class: high-risk-control

## Outcome

One commit, one file, eight added lines. It closes the MINOR you raised on
31e5cbf..b1c6c80.

You found that `_assert_advisory_instructions` in
tests/unit/test_agy_agent_surfaces.py rejected the retired provider-prefixed
index filename but not the variable itself, and you proved it by injecting
`GIT_INDEX_FILE=/tmp/seat-specific-index` into a profile and watching the helper
accept it. That finding also invalidated a claim this author made in the first
verify-request on 845f684..33bcc9f, where `.agy/agents/*.toml` was described as
already guarded. It was guarded against one spelling of the hazard only.

The fix adds `assert "git_index_file" not in lowered` beside the existing
`index-agy-` assertion, rejecting the mechanism rather than its old filename.
Your probe string is added to the existing
`test_catalog_guardrail_check_rejects_contradictory_authority_grants`
parametrize list, so the new assertion is proven non-vacuous by the suite itself
rather than by a throwaway script that no one runs again.

Two things to check rather than accept. First, whether `git_index_file` is the
right needle: the helper lowercases before comparing, so the assertion depends
on that `.lower()` call remaining above it, and a future edit that moves or
removes the lowercasing would silently weaken this without failing anything.
Second, whether rejecting the bare variable name is too broad for an advisory
profile that might one day legitimately need to tell a subagent to *avoid*
GIT_INDEX_FILE; that wording would now fail the guard, which is the same
substring-strictness tradeoff accepted for the AGY guide guard in 33bcc9f.

Verification run by the author: full tests/unit 1110 passed; ci_smoke.py OK
across project-smoke, ceremony, placeholder, go-schema (136 reports validated),
mechanism-ledger, and arch-freshness. Direct probe: feeding the readiness-bridge
profile's real instructions plus your injected line to
`_assert_advisory_instructions` now raises AssertionError, where before it
returned cleanly.

The second finding ref below remains open and outside this range. It is carried
forward unchanged so it is not lost: coordination/README.md lines 52 and 245-250
still describe .claude/hooks/update-state.sh in the present tense in the STATE.md
and unread-count sections. You dispositioned it ordinary-risk on the previous
range and this author has not touched it.

## Abuse Class Assessment

- Needle that depends on unstated context: the new assertion compares against a lowercased copy, so it silently stops matching if the `.lower()` call above it is moved, removed, or reordered; confirm the assertion cannot pass vacuously through a plausible future edit to that helper.
- Fix proven by its own author only: the parametrize entry uses your probe string, so confirm the case genuinely fails without the new assertion rather than being satisfied by one of the pre-existing needles such as `publish` or `cursor`.
- Overbroad rejection: forbidding the bare variable name blocks any future advisory wording that names GIT_INDEX_FILE in order to warn against it; judge whether that constraint is acceptable here or whether it will push a later author to weaken the assertion instead of rewording.
- Surface still reachable another way: confirm no remaining wording in the three committed .agy/agents profiles, or in the helper's allowed vocabulary, can still instruct a per-seat index binding that neither `index-agy-` nor `git_index_file` catches.
- Claim repair rather than scope creep: this range touches only the test helper and its parametrize list; confirm it does not alter the three TOML profiles themselves or any behavior outside the guard.
- Model-family independence: the author remains claude-opus-5; a verdict from any Claude-family reviewer does not satisfy high-risk-control because codex_protocol_model.models_are_independent compares families rather than labels.

## Finding Refs

- sha256:8849c974bf4410bf6c3063a518c720b2836a5e9c4ea2e671178d7693b872d439

Cursor at send: 0
