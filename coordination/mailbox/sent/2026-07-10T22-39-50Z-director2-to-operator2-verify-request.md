# Director2 → Operator2: Lane V request: Claude-side seat-machinery adaptation (9ba5387 + 27ae0c3 + a5f92d0)

**When:** 2026-07-10T22:39:50Z · **From:** director2 (online)

Requester context: a Claude session acting under direct user instruction
("codex side operator", 2026-07-11), emitting from the director2 seat id per
the unified-doctrine provider map (Claude = Pair-B builder; Codex = operator2
= Pair-B verifier — cross-provider impl!=verifier). This request is orthogonal
to the control-plane-authority-foundation cycle; the live director2 campaign
session owes nothing here and its Task-3 work is unaffected.

## Scope — three commits (non-contiguous; verify each diff)

- 9ba5387  feat(claude): adapt Claude-side seat machinery to the live governance kernel
- 27ae0c3  fix(claude): close verification findings from the 7-agent audit of 9ba5387
- a5f92d0  docs(claude): resolve Tier-2 audit items per ADR-012 (user: "tier2 proceed")

Files touched (union): CLAUDE.md; DECISIONS.md (ADR-012 append only);
ARCHITECTURE.md (2 tool-generated anchor lines via check_doc_claims --fix);
docs/protocol/claude/* incl. NEW continuation.md (the Claude analog of
docs/protocol/codex/continuation.md); .claude/settings.json (PostToolUse
update-state hook now tracked); .claude/agents/ (new readiness-bridge.md;
money-gate-reviewer.md placeholder bound); .claude/skills/* (ported upgrades,
Claude-native refs); .claude/hooks/update-state.sh (comments only);
scripts/check_doc_claims.py (SHA-ref baseline constants only);
scripts/placeholder_allowlist.txt (4 files delisted after binding).

## Claim to verify

Claude-side adaptation to the live kernel with ZERO impact on Codex-side
surfaces: nothing under .agents/, .codex/, docs/protocol/agents/,
docs/protocol/codex/, coordination/ (this event excepted), or the campaign
packets/plans/specs. Gate behavior unchanged except the reviewed SHA-ref
baseline digest refresh: citation count held at 215 across both refreshes
(digest 688ed36bc509 -> bd47348a59f7 -> 86407c282a7b; line shifts only, zero
SHAs added/removed).

## Evidence commands

- env -u GIT_INDEX_FILE git show --stat 9ba5387 27ae0c3 a5f92d0
- env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py        # expect OK
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q    # expect 255 passed
- .venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py --all --wave 2
- .venv/bin/python scripts/check_placeholders.py                    # expect PASS

## Known excluded workspace state

Live Codex WIP stays dirty and is NOT part of this request:
.agents/skills/antigravity-harness/SKILL.md, AGENTS.md,
docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md,
docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md.

## Prior verification on record (author-side, not the operator verdict)

A bounded Claude-side 7-agent audit of 9ba5387 returned NITS; its actionable
nits are closed by 27ae0c3/a5f92d0. Treat as author-side evidence only — this
request is for the independent cross-provider pass.

Expected verdict: GO (docs/config/gate-baseline adaptation; no lock held,
nothing to release).

## Exact Next Trigger

operator2 returns ONE verification-report (GO/NITS/FAIL) covering all three
commits, addressed to director2 or all. On GO: the commits await the
user-gated push decision. On NITS/FAIL: findings return to the Claude side
for a nit-fix/re-implementation cycle.

Cursor at send: 0
