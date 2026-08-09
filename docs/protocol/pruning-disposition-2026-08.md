# Startup-context pruning — disposition record (PR 1, 2026-08)

Method required by the audit that authorized this change: every clause
removed from an always-loaded instruction surface is dispositioned here as
**kept** (survives in compact form), **moved** (canonical home named), or
**retired** (with the reason), per the rule-maintenance clause in
`docs/protocol/work-modes.md`. Review diffs obligations, not prose.

Measured surface (bytes/words via `wc`, before at `84ed632`):

| Surface | Before | After | Loading |
|---|---|---|---|
| `AGENTS.md` | 851 w / 6,707 B | 476 w / 3,997 B | always (router) |
| `CLAUDE.md` | 1,143 w / 8,494 B | 302 w / 2,288 B | always (Claude) |
| `.cursor/rules/pipeline-os-cursor.mdc` | 269 w / 1,889 B | 191 w / 1,339 B | alwaysApply |
| `.cursor/rules/cursor-seats.mdc` | 450 w / 3,224 B | 462 w / 3,378 B | **scoped** (was alwaysApply) |
| Always-loaded total | 2,713 w / 20,314 B | 969 w / 7,624 B | −64% words |

Residual above the plan's 900-word target is pinned content:
`tests/unit/test_protocol_prompt_sync.py` and sibling gates pin ~15 exact
obligations into `AGENTS.md`/`CLAUDE.md` (kept deliberately — they are
anti-regrowth and anti-drift controls, not parity ceremony).

## AGENTS.md

| Clause (before) | Disposition |
|---|---|
| Provider entrypoint table | kept-shortened: five-line adapter index (discoverability pinned by `test_provider_routers_remain_discoverable`) |
| Codex applicability tiers 0–3 | retired: per-task tier classification was selection ceremony; review depth is carried by risk classes (`scripts/codex_protocol_model.py`), not tiers |
| "Choose product-work phase" per task | moved: `docs/protocol/work-modes.md` "Ordinary work carries no mode"; one summary line remains in the contract |
| Tier-2 pre-write refresh command block | kept-shortened: scoped refresh lives as a Claude mechanics bullet; no universal mandate |
| `ci_smoke` topology trigger | moved: `CLAUDE.md` mechanics bullet (trigger unchanged: governance/runtime topology or ARCHITECTURE invariant) |
| Project-sources table | retired: duplicate of `README.md` / `docs/REPOSITORY-MANUAL.md` discovery; no recorded failure it prevented |
| Symbol-search discipline (rg definition/writers/callers) | retired: native frontier-agent behavior; no pinned obligation |
| Engineering discipline block | kept-shortened: contract items 1–5 keep every pinned obligation (accepted exact task, failing behavior test, root cause, smallest-sufficient verification, strict xfail pin, delegation owner-chosen, tests prove only what they execute) |
| Superpowers non-dependency note | retired: the executable control is `test_active_instruction_surfaces_have_no_superpowers_invocation`, which scans surfaces; the prose added nothing |
| Governed-protocol seam list | kept-shortened: header names the three executable seams |
| Mandatory-boundaries list | kept-shortened: contract items 5–6 (review-by-risk, separate exact authority, transport ambiguity reported) |
| Review-depth policy prose | kept-shortened: contract item 5, wording aligned to the risk classes |
| Host-task-tools paragraph | moved: `docs/protocol/codex/continuation.md` already owns discovery/dispatch/waiting (PR 2 dedups further) |
| Evidence-ledger route | kept-shortened: one pointer line (pinned by `test_doc_surfaces_route_to_ledger_bridge_without_stale_selectors`); full removal is PR 2 scope with its own test retarget |
| Worktree-hygiene block | kept-shortened: contract items 2 and 7 |
| ChatGPT Pro pointer sentence | kept: pinned exactly-once by `test_chatgpt_consultation_is_an_optional_pointer_not_model_policy`; retirement is PR 2 scope (pin spans three surfaces) |

## CLAUDE.md

| Clause (before) | Disposition |
|---|---|
| Mandatory session-start smoke + git log + status | retired as ritual: measured cost was context (dozens of WARN lines per session), not the 3.5 s runtime; the topology-change trigger is kept as a mechanics bullet |
| Program-manual reading order | retired: task-specific; the manual remains discoverable |
| Pre-edit symbol-search block | retired: native behavior (same row as AGENTS.md) |
| Verification-profile + xfail lines | kept: `AGENTS.md` contract items 1 and 3 |
| "Work mode before ceremony" section | moved: `docs/protocol/work-modes.md`; router keeps a one-line mode summary (pinned words explore/validate/promote remain) |
| Skills-default section ("check `.claude/skills/` before starting") | kept-shortened: "load a skill only when the task matches its declared trigger" — the audited proposal's exact replacement |
| Skill-conflict handling | kept: Lessons section (pinned phrases intact) |
| Lesson→candidate routing | kept-shortened: Lessons section carries all ten pinned obligations (ADR-066/067 anti-sediment controls) |
| 6.5 h field-trial narrative | moved: preserved below under "Field evidence (relocated)"; candidate for a future ADR. Loading the anecdote on every task reproduced the effect it documents |
| Formation gate for claims (full loop + commands) | moved: canonical body is `.agents/skills/probe-a-claim/SKILL.md` (already the stated source of truth); `AGENTS.md` item 5 keeps the risk hook |
| Proportional independence section | kept-shortened: `AGENTS.md` item 5; full rationale remains `docs/protocol/claude/independence-first.md` |
| Autonomous seat contract + Compact Pair invariant text | moved: `.agents/skills/four-seat-protocol/SKILL.md` and `docs/protocol/claude/continuation.md` own these; router keeps the load trigger |
| Delegation/orchestration pointer | kept-shortened: `AGENTS.md` item 4 |
| Evidence-ledger startup route + guard command | moved: `docs/protocol/claude/ledger-cli-adoption.md` owns the procedure; router pointer removed (Claude reaches it via `AGENTS.md`) |
| Shared-tree hygiene block | kept-shortened: mechanics bullet keeps the doctrine-diff practice; the evasion-control story moved below |
| External-effects list | kept: mechanics bullet + `AGENTS.md` item 6 |

## .cursor/rules/pipeline-os-cursor.mdc (alwaysApply)

| Clause (before) | Disposition |
|---|---|
| Fresh smoke/history/status inspection mandate | retired as ritual (same rationale as CLAUDE.md) |
| Readiness/seat/approval topology recap | kept-shortened: "no formal seat unless registered", hook-approval expectations |
| Hook approval + native-file-edit denial behavior | kept and made explicit (new): "the hook may deny native file edits or convert governed mutations into one approval — expected, not an error." Empirical basis: 2026-08-09 session had file-edit tools denied in readiness posture and completed the work via the sanctioned shell path |
| Standing-pair topology, five-seat warning | moved: `.cursor/rules/cursor-seats.mdc` (scoped) and `docs/protocol/cursor/continuation.md` already carry it |
| `GIT_INDEX_FILE` prohibition | kept: baseline bullet |
| Symbol-search + "tests prove only what they execute" | retired here: not Cursor-specific governance; the tests-prove line lives in `AGENTS.md` item 5 |
| Push/merge/lock/spend separate approvals | kept-shortened |
| "Cursor workflow truth lives under..." pointer | kept-shortened: final bullet |

## .cursor/rules/cursor-seats.mdc

Body unchanged in PR 1. Loading changed from `alwaysApply: true` to scoped
(`alwaysApply: false` + description + globs over `coordination/**`,
`.cursor/runtime/**`, `.cursor/hooks/**`, `scripts/cursor_*.py`): ordinary
Cursor sessions no longer carry seat doctrine; seat/mailbox/coordination work
still loads it. Content dedup is PR 2 scope.

## docs/protocol/work-modes.md

Added "Ordinary work carries no mode": ordinary reversible repository-local
work declares nothing; a mode object exists only at its boundary (campaign →
Explore record, frozen candidate → Validate, canonical/live mutation →
Promote). "Start in explore" reworded to "Begin an Explore record when a
campaign starts" so Explore is the implicit absence of a higher boundary,
not a mandatory declaration. All pinned phrases (`one campaign brief`,
`No formal review inside Explore`, `Provider launch remains separately
authorized`, `work_profile_for`) unchanged.

## Test retargets (same change, by design)

| Test | Change | Reason |
|---|---|---|
| `test_cursor_surface_sync.py::test_scoped_rule_declares_binding_and_advisor_subagents` | `alwaysApply: true` pin → `alwaysApply: false` + `globs:` presence | The pin froze the loading decision this reviewed change inverts; the binding/advisor content pins are unchanged |
| `docs/protocol/learning/contract.md` I5 citation | `AGENTS.md:110-118` → `AGENTS.md` Universal contract item 5 | line-number anchor into a rewritten file; obligation text unchanged |

No other test was modified: the full suite (1,901 tests) and
`scripts/ci_smoke.py` pass against the rewritten surfaces because every other
pinned obligation was kept in compact form.

## Field evidence (relocated from CLAUDE.md)

Instruction prose is executable on models and is the least-gated surface in
this repository. The first field trial measured it: a 6.5 h transcript with
zero tool invocations yet unprompted hash-citations and a handoff doc —
doctrine text shaped the worker's habits while the reviewed tools sat unused.
When the goal is behavior change, change the prose surface first, and give a
changed instruction surface at least a reduced-context probe of its central
claim, because its only other test is a field trial someone pays for.

Shared-tree lesson (relocated from CLAUDE.md): diff the doctrine paths before
submitting a range, not only the code — an obligation can land mid-flight and
bind in-progress work; one did (the evasion-control requirement) and killed a
mechanism built hours earlier. The practice survives as a CLAUDE.md mechanics
bullet; this paragraph is the originating story.
