# Director2 → All: prompt-sync desync reds `main` (75fde1d) — Codex-side fix needed

**When:** 2026-07-18T00:02:15Z · **From:** director2 (online)

Event type: findings
Reviewed head: 75fde1d (origin/main == local before this Claude remediation stack)
Full fix brief: `docs/superpowers/briefs/2026-07-18-codex-prompt-sync-desync-fix.md`

## What is wrong

`main` is RED. `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit` fails
**16 tests, all in `tests/unit/test_protocol_prompt_sync.py`** (20 on the Linux CI
runner). This is the compaction commit `75fde1d` ("compact protocol behavior
surfaces"), not the analyst-verdict remediation.

**Root cause:** the compaction shrank two always-loaded surfaces into thin routers
and dropped doctrine that `scripts/codex_protocol_model.py` renderers still emit
and the sync tests still assert must appear there. `codex_protocol_model.py` was
NOT in the compaction changeset, so model ⇄ surface fell out of sync:

- **`AGENTS.md`** is missing (per failing test): `R-INDEPENDENCE`, `Capacity Split
  Default:`, `same unchanged commit`, `brief-pattern references are runtime claims
  when they cite canonical sites`, `audit-completeness is not audit-disposition`,
  the body-first/`coordinator has no cursor` line, the claude-function-harmonization
  block, and exactly one `CHATGPT_PRO_POINTER`.
- **`docs/protocol/codex/continuation.md`** is missing: `adapt Claude functions to
  Codex-native primitives`, the `Behavior source map:` line, `Subagent utilization
  decision`, `Side-Effect Executor Token:`, `shared user-gated side effects need
  exactly one named executor`, `Production-affecting OR user-data-integrity issue`,
  `wave-gate evidence before asserting blocked`, `findings-first ordering by
  severity`, and the `Coordinator and seat chains continue internally…` line.

The brief has the full failing-test → required-phrase → surface table.

**Also note — shipped ≠ verified:** the operator GO
(`2026-07-17T13-17-10Z-operator-to-director-verification-report.md`) covered
`9766e7c` ("680 passed"). `75fde1d` was stacked on top and pushed **unverified**.

## How to fix (pick one, deliberately)

- **Option A (recommended if over-stripped):** restore the model-backed doctrine
  phrases into `AGENTS.md` and `docs/protocol/codex/continuation.md`, mirroring
  what the `codex_protocol_model.py` renderers emit.
- **Option B (only if the thin-router is intended):** move the model renderers AND
  the prompt-sync expectations together — do not weaken the tests without relocating
  the doctrine to a still-loaded surface. This is a protocol-design call; surface it
  to the user-principal first.

## Acceptance

- `pytest tests/unit -q` → 0 failures; `scripts/ci_smoke.py` → OK.
- If pushing: a fresh operator GO whose **reviewed head == the actually-shipped
  HEAD** (close the shipped≠verified gap).

## Context on the stack above this

Ten Claude-side commits sit on local `main` above `75fde1d` (`16410e4 … d018100`),
differential-verified against this red baseline (they neither touch nor depend on
the 16 failing tests) and independently GO'd over `75fde1d..06e796c`: the
CI-honesty fixes, the route/v1 deletion, the ref-bus liveness wording, and the
DECISIONS closeouts. These are NOT pushed. Once the desync above is green, the
whole tree is green.

**The user-principal holds the push decision** ("go") and it is separately gated —
this findings event requests the surface fix only, not a push.
