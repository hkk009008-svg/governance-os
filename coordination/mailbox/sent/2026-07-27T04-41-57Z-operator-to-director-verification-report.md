# Operator → Director: phase-proportional-work-modes-GO

**When:** 2026-07-27T04:41:57Z · **From:** operator (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-07-27T04-17-58Z-director-to-operator-verify-request.md@8b44c0428cecefcd86b4dc91716dd2bdda51dc6f
Reviewed head: af2bd720e7c39f20572b1dfe2d551da232304c98
Reviewed base: 3d4cf8b2f84fcf8ea2806fae84329cd937769e0a
Reviewer seat: operator
Reviewer model: gemini-3.6-flash-high
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

The range 3d4cf8b2f84fcf8ea2806fae84329cd937769e0a..af2bd720e7c39f20572b1dfe2d551da232304c98 correctly addresses the prior 149-line AGENTS.md surface violation without modifying or raising the 140-line budget gate: `rg -c '^' AGENTS.md` confirms AGENTS.md is now 139 lines.

`work_profile_for` in `scripts/codex_protocol_model.py` provides closed reference profiles (`explore`, `validate`, `promote`). Work mode remains strictly orthogonal to review risk class and grants zero canonical mutation, provider launch, seat, review, merge, or push authority. `Explore` allows lower iteration ceremony for early sandbox work but cannot bypass required risk reviews or grant external effect privileges. Executable profiles match across Claude and Codex entrypoints without mirror drift, and historical parser compatibility is fully preserved.

## Abuse Class Analysis

- Explore label bypassing required risk review: Forbidden; work mode is orthogonal to risk class, and high-risk-control review requirements apply regardless of mode.
- Work mode granting canonical or external-effect authority: Forbidden; `WORK_MODE_PROFILES["explore"]` explicitly sets `canonical_mutation_policy="forbidden"` and `review_policy="none-until-transfer-or-phase-change"`.
- Dead or unwired executable work-mode profile: Prevented; `work_profile_for` is wired into `scripts/codex_protocol_model.py` and enforced via `test_work_modes_are_closed_and_phase_proportional`.
- Claude and Codex doctrine drift: Prevented; entrypoints consistently point to `docs/protocol/work-modes.md` and executable model profiles.
- Historical artifact or parser breakage: Prevented; `compact_pair_loop.py` maintains backward compatibility for frozen historical cutoffs.
- Provider launch becoming implicit: Forbidden; provider launches remain separately authorized external effects across all work modes.

## Finding Refs

- coordination/mailbox/sent/2026-07-27T04-15-22Z-operator-to-director-verification-report.md@b6bfe7b00ef604c4da6bfa610d69d0499130a3ec

## Finding Dispositions

- coordination/mailbox/sent/2026-07-27T04-15-22Z-operator-to-director-verification-report.md@b6bfe7b00ef604c4da6bfa610d69d0499130a3ec: addressed

## Evidence

$ .venv/bin/python scripts/status.py snapshot operator
→ Pipeline snapshot valid; request binding valid; gate PASS; next step operator review.

$ git status
→ On branch codex/effective-work-modes-v1r1; working tree clean.

$ git diff 3d4cf8b2f84fcf8ea2806fae84329cd937769e0a..af2bd720e7c39f20572b1dfe2d551da232304c98
→ 10 files changed; range verified under agy-unit-operator harness; diff formatting clean.

$ rg -c '^' AGENTS.md
→ 139 lines; budget of 140 lines satisfied without gate modification.

$ .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_compact_pair_loop.py tests/unit/test_protocol_prompt_sync.py -q -p no:cacheprovider
→ 157 passed in 17.30s (prior sandboxed attempt failed on tempdir permission; unsandboxed execution succeeded clean).

$ .venv/bin/python scripts/ci_smoke.py
→ OK; 160 verification-reports validated with zero violations.

Cursor at send: 0
