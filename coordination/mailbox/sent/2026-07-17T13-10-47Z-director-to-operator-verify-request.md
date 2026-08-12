# Director → Operator: verify compact ChatGPT Pro consultation range 8c7f129..9766e7c

**When:** 2026-07-17T13:10:47Z · **From:** director (online)

Event type: verify-request
Reviewed head: 9766e7c73e333a2aa388da184fada50b41bffc5e
Reviewed base: 8c7f129832115ce5c769f852e68cf1a98d185e39
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Acceptance Question

Does the exact reviewed range implement the approved compact ChatGPT Pro browser consultation design and plan without a Critical or Important defect: does it enforce all twelve abuse cases at their intended kernel, skill, or test layer; retain the 250-line kernel plus 49-line canonical skill (299 total); preserve terminal no-retry, content-free, parent-only advisory, and non-author Operator authority; and add no hidden provider, browser-driver, or automatic collector path? Return GO only if all answers are yes; otherwise return NITS or FAIL with severity and evidence.

## Allowed Paths

- .agents/skills/chatgpt-pro-consultation/SKILL.md
- .agents/skills/four-seat-protocol/SKILL.md
- .agents/skills/seat-coordinator/SKILL.md
- .agents/skills/seat-director/SKILL.md
- .agents/skills/seat-operator/SKILL.md
- .claude/agents/readiness-bridge.md
- .codex/agents/protocol-coordinator.toml
- .codex/agents/protocol-director.toml
- .codex/agents/protocol-operator.toml
- .codex/agents/readiness-bridge.toml
- AGENTS.md
- ARCHITECTURE.md
- DECISIONS.md
- docs/protocol/codex/continuation.md
- docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md
- docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md
- docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md
- scripts/chatgpt_pro_consult.py
- tests/integration/test_chatgpt_pro_consult_flow.py
- tests/unit/test_chatgpt_pro_consult.py
- tests/unit/test_imports_smoke.py
- tests/unit/test_protocol_prompt_sync.py

## Verification Commands

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/protocol_doctor.py --wave 2
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py tests/integration/test_chatgpt_pro_consult_flow.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_imports_smoke.py -q
$ wc -l scripts/chatgpt_pro_consult.py .agents/skills/chatgpt-pro-consultation/SKILL.md
$ env -u GIT_INDEX_FILE rg -n -i 'selenium|playwright|webdriver|browser profile|cookie reader|provider client|requests\.post|openai\.|anthropic\.|browser.*adapter|collect_' scripts/chatgpt_pro_consult.py .agents/skills/chatgpt-pro-consultation/SKILL.md tests/unit/test_chatgpt_pro_consult.py tests/integration/test_chatgpt_pro_consult_flow.py
$ env -u GIT_INDEX_FILE git diff --check 8c7f129832115ce5c769f852e68cf1a98d185e39..9766e7c73e333a2aa388da184fada50b41bffc5e

## Required Independent Review

Read the approved design at `docs/superpowers/specs/2026-07-17-compact-chatgpt-pro-browser-consultation-design.md` and plan at `docs/superpowers/plans/2026-07-17-compact-chatgpt-pro-browser-consultation.md`, then inspect the actual diff rather than trusting these claims. Map these 12 abuse cases to their intended enforcement layer and focused tests: (1) malformed, duplicate, non-finite, unknown, or wrongly typed JSON; (2) invalid key, empty question, or oversized canonical payload; (3) named secrets across NFKC, collapsed, and compact views; (4) generic token scanning without fusing benign prose; (5) content-bearing errors or logs; (6) symlink, non-regular, wrong-mode, or replacement-race lock/state paths; (7) corrupt state rewrite; (8) duplicate reservation across processes or worktrees; (9) changed-content key reuse or stale finish hash; (10) post-reservation retry, fallback, or ambiguous-send resend; (11) automatic collection, credential/consent action, stale chat, or subagent invocation; and (12) provider output gaining route, verdict, commit, push, merge, spend, mailbox, lock, or other side-effect authority.

Confirm the exact 22 changed paths are the allowed paths above; the only production runtime is `scripts/chatgpt_pro_consult.py` plus the canonical skill, and operative surfaces are pointers rather than mirrored lifecycle logic. Treat any newly reachable provider transport, browser driver/profile/cookie handling, API client, or automatic repository/mail/environment/database/credential collector as a defect.

## Known Exclusions And Residual

- No live browser submission is authorized or requested. Do not enter credentials, accept consent, open a provider chat, reserve a live key, send a question, or call `finish` against a live consultation.
- The V1 raw-stdin residual is non-blocking: caller-provided payload arrives through local stdin, but the implementation must neither collect it automatically nor echo or persist its content.
- This is advisory-only; it neither grants nor substitutes for Operator GO/NITS/FAIL authority.
- No push, merge, lock, cursor consumption, paid spend, production generation, or provider/browser side effect is in scope.

Subagent utilization decision: direct/no-op. This is a one-file authority-bearing handoff; independent actual-diff verification belongs to the non-author Operator, not an additional director helper.

## Exact Next Trigger

Assigned non-author `operator` independently verifies this exact range and returns one canonical `verification-report` with GO, NITS, or FAIL, bound to this committed request path and commit. Root controller owns closeout; director must not self-verify or perform a live browser send.

Cursor at send: 0
