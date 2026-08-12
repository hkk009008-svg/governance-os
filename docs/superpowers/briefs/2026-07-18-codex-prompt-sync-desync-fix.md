# Brief (for the Codex side): fix the prompt-sync desync that reds `main`

**Author:** Claude session (orientation mode — this is a draft brief for the Codex
director/operator pair to adopt, not a mailbox event and not a seat instruction).
**Date:** 2026-07-18
**Priority:** P0 — `main` is red; blocks the push of an otherwise-green stack.

## Problem

At `origin/main == 75fde1d` ("docs(codex): compact protocol behavior surfaces"),
`env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit` fails **16 tests, all
in `tests/unit/test_protocol_prompt_sync.py`** (20 on the Linux CI runner: the 16
below + 2 now-fixed bridge tests + 2 Linux fault-injection). This is a fresh
regression from the compaction, not from the analyst-verdict remediation.

**Shipped ≠ verified.** The operator GO in
`coordination/mailbox/sent/2026-07-17T13-17-10Z-operator-to-director-verification-report.md`
covered `9766e7c` ("680 passed"). The compaction commit `75fde1d` was stacked on
top of the GO'd commit and pushed **unverified** (`git diff 9766e7c 75fde1d` = the
compaction alone). So the shipped HEAD was never green.

## Root cause

The compaction shrank two always-loaded surfaces into thin routers, dropping
doctrine that `scripts/codex_protocol_model.py` renderers still emit and the
prompt-sync tests still assert must appear on those surfaces:

- **`AGENTS.md`** → now `"# Pipeline agent guide … keeps only rule… Cross-provider
  ownership and synchronization rules live in protocol-assembly-map.md"`.
- **`docs/protocol/codex/continuation.md`** → now `"# Codex continuation adapter …
  translates Pipeline doctrine into Codex-native runtime actions …"`.

The model (`codex_protocol_model.py`) was **not** in the compaction changeset, so
model ⇄ surface fell out of sync.

## Exact restore list (failing test → required phrase → surface)

`AGENTS.md` is missing:
| test (test_protocol_prompt_sync.py) | required phrase |
|---|---|
| `test_claude_function_harmonization…` (:122) | (claude-function harmonization block) |
| `test_r_independence…` (:453) | `R-INDEPENDENCE` (+ the shared_surface_phrases block: `adversarial-surface`, `enforced-and-tested`, `R-VERIFY-TIER`) |
| `test_capacity_split_default…` (:588) | `Capacity Split Default:` |
| `test_codex_execution_tiers…` (:399) | `same unchanged commit` |
| `test_rule_12_pattern_reference_transplant…` (:679) | `brief-pattern references are runtime claims when they cite canonical sites` |
| `test_rule_13_disposition_transplant…` (:699) | `audit-completeness is not audit-disposition` |
| `test_compact_pair…` (:852) | `Mailbox decisions remain body-first: read relevant mailbox bodies before acting; live seat cursors are intentional per-seat state, and the coordinator has no cursor.` |
| `test_compact_chatgpt_tool…` | `CHATGPT_PRO_POINTER` (exactly one occurrence) |

`docs/protocol/codex/continuation.md` is missing:
| test | required phrase |
|---|---|
| `test_claude_function_harmonization…` (:270) | `adapt Claude functions to Codex-native primitives` |
| `test_live_seat_behavior_sources…` (:328) | `Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.` |
| `test_subagent_utilization…` (:353) | `Subagent utilization decision` |
| `test_side_effect_executor_token…` (:618) | `Side-Effect Executor Token:` |
| `test_side_effect_executor_token_detailed…` (:644) | `shared user-gated side effects need exactly one named executor` |
| `test_reviewer_result_handling…` (:763) | `Production-affecting OR user-data-integrity issue` |
| `test_blocked_wave_and_acting_coordinator…` (:789) | `wave-gate evidence before asserting blocked` |
| `test_emergency_and_disagreement…` (:819) | `findings-first ordering by severity` |
| `test_active_surfaces_continue…` (:1095) | `Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.` |

(Read each test for its full `required`/`shared_surface_phrases` tuple — some
assert several phrases per surface; the table lists the first that trips.)

## Two ways to green — pick one, deliberately

**Option A — restore the doctrine to the compacted surfaces (recommended if the
compaction over-stripped).** Put the model-backed phrases back into `AGENTS.md`
and `docs/protocol/codex/continuation.md`. The authoritative source text is what
the `codex_protocol_model.py` renderers emit — mirror those. This keeps the
always-loaded router carrying the doctrine inline, which is what the sync tests
encode as the invariant.

**Option B — ratify the thin-router intent (only if AGENTS.md is *meant* to be a
pointer).** If the compaction deliberately moved doctrine out of `AGENTS.md`/
`codex/continuation.md` into pointed-to docs, then the **model renderers and the
prompt-sync expectations must change together**: drop those surfaces from the
tests' path lists (or point the assertions at the new home). Do NOT weaken the
tests without moving the doctrine somewhere still-loaded — that would delete a
real cross-surface-sync guarantee. This is a protocol-design decision; surface it
to the user-principal before choosing it.

This is a Codex-lane call because it is the Codex executable model + Codex-owned
surfaces. The Claude side is already in sync (no `.claude` surface appears in any
failing test's path list — verified).

## Acceptance

- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q` → 0 failures
  (the 16 gone; no new).
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` → OK.
- If pushing: a fresh operator GO whose **reviewed head == the actually-shipped
  HEAD** (close the shipped≠verified gap that produced this).

## What's already staged on top (do not redo)

Nine Claude-side commits sit on local `main` above `75fde1d`
(`16410e4 … 5c3d4f6`), differential-verified against this red baseline (they
neither touch nor depend on the 16 failing tests) and independently GO'd
(`75fde1d..06e796c`): the CI-honesty fixes (bridge env-independence, the backwards
`--runxfail`/R4 removal, PR-template + assembly-map drift), the route/v1 deletion,
the ref-bus liveness wording, and the DECISIONS closeouts. Once this desync is
fixed, the whole tree greens and is push-ready (push is user-gated).
