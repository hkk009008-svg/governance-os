# Coordinator → All: Route provider-native workflow and config hygiene

**When:** 2026-07-23T12:12:15Z · **From:** coordinator (online)

Event type: coordination
Task-board: PIPELINE-WORKFLOW-CONFIG-HYGIENE-20260723
Route generation: 42
Supersedes route: coordination/mailbox/sent/2026-07-23T12-08-23Z-coordinator-to-all-coordination.md
Expected control HEAD: 8b17d91c2b27c25ea7a0140d694266383d6aba72
Status: ACTIVE — PROVIDER-NATIVE WORKFLOW AND CONFIG HYGIENE
Authorization source: user-task:local-pipeline-os-protocol-adjust-and-fix-2026-07-23
Owner: director
Assigned reviewer: operator
Author provider/model: Codex/gpt-5.6-sol
Reviewer provider/model: Codex/gpt-5.6-terra

## Outcome

Finish the local Pipeline OS policy/configuration cleanup without creating false permission guarantees or plugin coupling. Keep Pipeline provider-native and route-driven, make AGY/Cursor provider entrypoints discoverable, remove stale mandatory Superpowers invocations from active Claude guidance, and preserve historical plans/specs as durable non-triggering inputs.

## Confirmed findings

- POLICY-F001: Codex Doctor 0.144.4 reports the loaded config path is /Users/hyungkoookkim/.codex/config.toml, not Pipeline/.codex/config.toml. The dirty project approval_policy and sandbox_mode keys therefore do not control this desktop runtime.
- POLICY-F002: the effective current runtime already reports approval policy Never and filesystem sandbox unrestricted. Repeated prompts are separate hook-trust, fixed-writer, external-app/macOS, or platform-safety boundaries; committing the project keys would create false confidence.
- POLICY-F003: the dirty AGENTS.md correctly adds AGY and Cursor provider routers and a proportional project-native engineering policy, but it is not durable or tested yet.
- POLICY-F004: active docs/protocol/claude/orchestration.md still mandates superpowers:subagent-driven-development, superpowers:code-reviewer, and superpowers:finishing-a-development-branch even though CLAUDE.md already points to the agent-neutral native orchestration contract and Pipeline does not require that plugin.
- POLICY-F005: the current .gitignore dirt is one redundant blank line only.

## Required behavior

1. Remove the ineffective approval_policy and sandbox_mode dirt from Pipeline/.codex/config.toml. Do not change the user's global Codex config or desktop permission profile.
2. Commit the AGY/Cursor provider-router additions and the project-native engineering workflow policy in AGENTS.md, with focused tests. Exact routed tasks do not require redundant brainstorming/spec/plan cycles; tests, root-cause analysis, fresh verification, and binding non-author Operator review remain proportional requirements.
3. Rewrite active Claude orchestration guidance to use Claude-native Task/Agent helpers and the universal Pipeline Operator review/finish boundary without requiring any superpowers:* skill. A plan stored under docs/superpowers/ remains an ordinary durable plan, not a plugin trigger.
4. Update the Claude Director brief pointer if needed so it links to the agent-neutral/native contract. Preserve optional delegation as an owner-chosen capacity tool; do not reintroduce task-count or line-count mandates.
5. Preserve docs/superpowers/**; do not delete historical specifications, plans, or briefs. Do not remove global Codex skills or system skills: they are outside Pipeline and not active merely because installed.
6. Remove the redundant .gitignore blank-line hunk so the file is clean, unless a focused test proves it carries semantics.
7. Add regression coverage that active Pipeline/Codex/Claude instruction surfaces contain no mandatory superpowers:* invocation, the project config contains no ineffective approval/sandbox promise, and the provider routers remain present.

## Allowed paths

- .codex/config.toml
- .gitignore
- AGENTS.md
- .claude/skills/seat-director/r-brief-template.md
- docs/protocol/claude/orchestration.md
- tests/unit/test_protocol_prompt_sync.py
- tests/unit/test_protocol_doc_integrity.py

## Exclusions and review

Do not change /Users/hyungkoookkim/.codex/config.toml, any credential/session data, docs/superpowers/**, provider adapters/hooks/launchers, mailbox history except the implementation verify-request/report, or any other unrelated file. Do not launch providers, change desktop/macOS permissions, install/remove plugins, access evidence-ledger, push, merge, consume cursors, or change external state.

Director commits only the allowed policy/config manifest after focused instruction/config tests, diff checks, Codex Doctor read-only confirmation, Protocol Doctor, and fresh full smoke. Operator alone reviews the immutable actual range and issues GO, NITS, or FAIL.

## Exact Next Trigger

Continue in the existing Director task, implement this route, and reuse the existing Operator task for the one actual-range review. Do not create replacement tasks.

Cursor at send: 0
