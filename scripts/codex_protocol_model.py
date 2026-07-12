#!/usr/bin/env python3
"""Executable model for the Codex four-seat protocol harness.

This module is intentionally dependency-free. Protocol renderers can import it
without touching mailbox state, locks, git indexes, or production pipeline code.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

MODEL_SOURCE = "scripts/codex_protocol_model.py"
CENTRAL_INVARIANT = "durable shared state beats chat memory"

ACTIVE_KERNEL_INVARIANTS = (
    (
        "durable shared state beats chat memory",
        "read git, signed ref-bus facts, mailbox bodies, cursors, locks, logs, gate evidence, and operator reports before stale prose",
    ),
    (
        "threeway signed ref-bus is load-bearing",
        "the signed three-way ref-bus is the load-bearing state source for three-way facts; free-form mailbox remains the human coordination channel",
    ),
    (
        "mailbox-first decisions",
        "check mail and read relevant bodies before protocol decisions or state-asserting writes",
    ),
    (
        "same-seat handoff first",
        "a fresh or transplanted named seat locates the newest handoff from that same concrete seat before ordinary orientation",
    ),
    ("explicit mode", "readiness bridge, live seat, coordinator, and subagent stay distinct"),
    (
        "coordinator is unpinned",
        "coordinator reads all-scope mail and never consumes a coordinator cursor",
    ),
    (
        "env-u git policy",
        "ordinary git and pytest use env -u GIT_INDEX_FILE unless maintaining a seat index",
    ),
    (
        "user-gated side effects",
        "push, lock-claim side effects, paid API spend, and pod spend require explicit user consent",
    ),
    (
        "independence-first verification",
        "classify adversarial surfaces before implementation and require design-time enumeration plus independent actual-diff verification",
    ),
    (
        "side-effect executor token",
        "generic user approval is unit consent, not executor election; shared side effects need one named executor token or live-evidence closeout",
    ),
    (
        "coordinator no production fixes",
        "coordinator may route and reconcile but not author behavior-changing production fixes",
    ),
    (
        "operator verification-report GO",
        "verified transitions require operator GO plus executed evidence",
    ),
    (
        "wave gate is evidence",
        "wave_gate_check.py is process evidence, not row-correctness proof",
    ),
    (
        "single consolidated route",
        "cross-seat awareness uses one coordinator event when routing is warranted",
    ),
    (
        "capacity-board route validation",
        "active coordinator task-board routes run protocol_capacity_board.py and --validate-route before commit",
    ),
)

DEMOTED_RUNTIME_CONCEPTS = (
    (
        "capacity-max cycle",
        "explicit coordinator tool for active multi-seat work, not every status check",
    ),
    ("no-op evidence", "only after a seat was actually queried or oriented"),
    ("Rotating Planning Relay", "optional rare cross-seat planning pattern"),
    ("protocol-effectiveness report", "read-only diagnostics only"),
    (
        "proof-bundle language",
        "use concrete evidence names: status, git log, mailbox bodies, gate output, smoke output, and diff scope",
    ),
    ("handoff ceremony", "narrow handoff only at real transfer boundaries or explicit request"),
)

CODEX_EXECUTION_TIERS = (
    (
        "tier-0-conversational",
        "self-contained answer",
        "no repo orientation, implementation skills, mailbox checks, smoke, "
        "worktree, or verification commands",
    ),
    (
        "tier-1-read-only",
        "repository inspection or evidence-backed report",
        "smallest scoped read commands; no implementation skills or live-seat "
        "checks without an explicit protocol trigger",
    ),
    (
        "tier-2-local-mutation",
        "ordinary code, test, config, or documentation edit",
        "impact analysis, task-relevant implementation discipline, focused "
        "tests, and one completion verification pass",
    ),
    (
        "tier-3-governed-side-effect",
        "live-seat decision, shared protocol state, or external side effect",
        "exact mailbox, capacity, independent-verification, and "
        "user-authorization gates",
    ),
)

VERIFICATION_DEDUPLICATION_RULES = (
    "Tier 2 uses focused tests plus one fresh completion verification pass.",
    "Tier 3 uses implementer evidence plus formal operator Lane V when required, "
    "then GO before push.",
    "Do not launch another generic reviewer or repeat Lane V for the same "
    "unchanged commit unless it asks a genuinely different, pre-stated question.",
    "Deterministic artifact evidence may be reused against an unchanged HEAD "
    "and unchanged relevant paths.",
    "Tier 3 requires fresh signed-bus, mailbox/cursor, lock, approval, and "
    "external-state checks; reuse never relaxes a triggered guard.",
)

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

HARNESS_COMPONENTS = (
    ("user", "User principal", "explicit instruction and consent"),
    ("harness", "Codex CLI harness", "readiness bridge or explicit live role"),
    ("state", "Durable shared state", "repo artifacts that survive sessions"),
    ("seats", "director / director2 / operator / operator2", "owned lane work"),
    ("coordinator", "coordinator", "on-demand all-scope reconciliation"),
    ("gate", "gate + receipt loop", "evidence, receipt checks, and user-gated push"),
)

DURABLE_STATE_ARTIFACTS = (
    "Git commits",
    "Committed files",
    "Signed three-way ref-bus facts",
    "Mailbox sent/ + seen cursors",
    "Mailbox bodies",
    "Lock files",
    "Logs",
    "Gate evidence",
    "Operator verification reports",
)

import protocol_mailbox  # noqa: E402

SEATS = protocol_mailbox.SEATS               # 4 real seats; coordinators are NOT pair seats
DIRECTOR_SEATS = ("director", "director2")   # pair tuple — stays literal
OPERATOR_SEATS = ("operator", "operator2")
COORDINATOR_SEATS = ("coordinator", "coordinator2")  # on-demand oversight seats — both bind coordinator mode
SEAT_BEHAVIOR_SOURCE = {
    "director": "director",
    "director2": "director",
    "operator": "operator2",
    "operator2": "operator2",
}


def behavior_source_for_seat(seat: str) -> str | None:
    """Return the canonical behavior source for a concrete live seat."""
    return SEAT_BEHAVIOR_SOURCE.get(seat)


READ_ONLY_VERIFIER_ROLES = ("lane-v-verifier", "money-gate-reviewer")
SPAWNED_ROLE_AGENT_ROLES = (
    "protocol-coordinator",
    "protocol-director",
    "protocol-operator",
    *READ_ONLY_VERIFIER_ROLES,
)

CORE_AGENT_MODULES = (
    "lane-v-verifier.toml",
    "money-gate-reviewer.toml",
    "protocol-coordinator.toml",
    "protocol-director.toml",
    "protocol-operator.toml",
    "readiness-bridge.toml",
)

AGENT_EXTENSION_RULES = (
    "agentNN.toml modules are optional Codex harness guardrail extensions",
    "extensions may codify seat-local guardrails, routing advice, and situational awareness",
    "extensions extend the harness; they do not replace built-in role agents",
    "extensions never override seat authority, mailbox cursor rules, or user-gated push",
)

AGENT_EXTENSION_ROUTING_CONTRACT = (
    (
        "agent01",
        "capacity manager companion",
        "explicit coordinator/cycle capacity-max planning",
    ),
    (
        "agent02",
        "explicit-mode bounded worker",
        "a parent names a concrete mode and allowed write set",
    ),
    (
        "agent03",
        "general senior repo worker",
        "ordinary repo coding or documentation work with protocol awareness",
    ),
    (
        "agent04",
        "read-only protocol auditor/router",
        "read-only protocol diagnosis and route recommendation",
    ),
)

RUNTIME_ENV_VARIABLES = (
    (
        "CODEX_AGENT_MODE",
        "readiness-bridge | live-seat | coordinator | subagent",
        "selects the harness behavior; defaults to readiness-bridge unless CODEX_SEAT names a live protocol role",
    ),
    (
        "CODEX_AGENT_ROLE",
        "readiness-bridge | director | director2 | operator | operator2 | coordinator | coordinator2 | verifier/specialist role",
        "names the part this Codex instance plays in the four-seat whole",
    ),
    (
        "CODEX_SEAT",
        "director | director2 | operator | operator2 | coordinator | coordinator2",
        "binds a live seat; coordinator and coordinator2 are compatibility aliases for coordinator mode and remain unpinned",
    ),
    (
        "CODEX_BEHAVIOR_SOURCE",
        "director | operator2 | (none)",
        "names the canonical live-seat behavior source while CODEX_SEAT remains the concrete mailbox, cursor, and git-index identity",
    ),
    (
        "CODEX_CAPABILITY_MODE",
        "read-only | seat-local | capacity-max | parent-scoped",
        "states whether this process reports, works in one seat, or coordinates full capacity",
    ),
    (
        "CODEX_MUTATION_SCOPE",
        "none | seat-owned | coordination-only | read-only-verification | parent-scoped",
        "documents which durable state this process may mutate after protocol checks",
    ),
    (
        "CODEX_AUTHORITY_SCOPE",
        "report-only | seat-owned | all-scope-reconcile | parent-scoped",
        "documents whose authority boundary this process inhabits",
    ),
    (
        "CODEX_MAILBOX_POLICY",
        "read-only-no-consume | seat-read-consume-intentional | all-scope-read-no-consume | parent-scoped",
        "documents whether mailbox state may be read, consumed, or routed",
    ),
    (
        "CODEX_GIT_POLICY",
        "env-u-git-index-read-only | per-seat-index-for-cursor-status | env-u-git-index-or-temp-index | env-u-git-index-parent-scoped",
        "documents how git and the shared worktree index should be touched",
    ),
    (
        "CODEX_VERIFICATION_POLICY",
        "report-evidence-only | request-operator-go | independent-go-nits-fail | reconcile-operator-go-only | read-only-review-no-go | parent-scoped-no-go",
        "documents whether this process can verify, request verification, or only report evidence",
    ),
    (
        "CODEX_CONTEXT_SOURCES",
        "repo-docs-mailbox-gates-readonly | seat-mailbox-owned-files-gate-evidence | all-scope-mailbox-inventory-locks-gates | parent-prompt-plus-allowed-artifacts",
        "documents which durable context this part should read before acting",
    ),
    (
        "CODEX_OUTPUT_CONTRACT",
        "readiness-report-and-blockers | seat-artifact-or-operator-request | capacity-board-or-single-route | bounded-findings-to-parent",
        "documents what this part owes back to the whole before stopping",
    ),
    (
        "CODEX_DECISION_BOUNDARY",
        "no-seat-authority | lane-owned-seat | all-scope-routing-no-production-fixes | parent-scoped-no-seat-authority",
        "documents which decisions this part may make without upgrading roles",
    ),
    (
        "CODEX_NEXT_ACTION_POLICY",
        "report-then-stop-or-request-role | read-mail-then-act-or-report-idle | build-board-reconcile-once | return-evidence-then-stop",
        "documents the default next move after orientation",
    ),
    (
        "CODEX_SIDE_EFFECT_POLICY",
        "user-consent-required",
        "documents that push, lock-claim side effects, paid API spend, and pod spend require user consent outside env",
    ),
    (
        "GIT_INDEX_FILE",
        "<git-dir>/index-codex-$CODEX_SEAT",
        "uses a per-seat or coordinator-local index while ordinary git/pytest still follows CODEX_GIT_POLICY",
    ),
)

SEAT_CONTRACT_FIELDS = (
    ("S-ROLE", "role/env"),
    ("S-OBJ", "objective"),
    ("S-PERM", "permissions"),
    ("S-SCOPE", "scope"),
    ("S-VERIFY", "verification"),
    ("S-DONE", "done"),
)

START_SESSION_STEPS = (
    "Start as readiness bridge unless an explicit seat or coordinator instruction is present.",
    "same-kind handoff first: if the prompt names a seat or coordinator, find "
    "the newest docs/HANDOFF-<seat-or-coordinator>-*.md from that same concrete "
    "role before seat_status.py or git log; if none exists, state that and continue.",
    "Run scripts/continuation_readiness.py to load the Codex Harness Model.",
    "Treat the signed three-way ref-bus as the load-bearing state source for three-way facts; the free-form mailbox remains the human coordination channel.",
    "Always check mail before protocol decisions: refresh live mailbox state "
    "and read relevant mailbox bodies before acting or writing state.",
    "Use durable shared state first: git commits, signed ref-bus facts, mailbox bodies, cursors, locks, logs, and gate evidence.",
    "Guardrail: do not consume cursors, send mailbox events, claim locks, push, or spend from readiness bridge mode.",
    "Treat built-in role agents as core agent modules and agentNN.toml files as guardrail extensions.",
    "Escalate into a live seat or coordinator only when the user or parent prompt explicitly names that role.",
)

COORDINATOR_INVARIANTS = (
    "never consume coordinator cursor",
    "always check coordinator/all-scope mailbox bodies before routing claims",
    "one coordinator-to-all route if needed",
    "capacity-board route validation before any active coordinator task-board route",
    "route from durable evidence, not chat memory",
    "do not author production fixes",
)

PLANNING_RELAY_ORDER = ("director", "operator", "director2", "operator2")

PLANNING_RELAY_RULES = (
    "Use the Rotating Planning Relay when an important cross-seat plan needs all-seat review before work is distributed.",
    "For a live-seat-started plan, the starter is step 1 and the baton moves through the fixed cyclic order: director -> operator -> director2 -> operator2; the order wraps after operator2 back to director.",
    "A live-seat-started relay runs exactly four live-seat turns, then the final seat sends the result to coordinator/all-scope for reconciliation.",
    "For a coordinator-started plan, coordinator fans out to all four seats, gathers responses back to coordinator, then distributes one consolidated coordinator-to-all task board.",
    "Relay mailbox events are planning evidence only; no production work, verification verdict, lock, push, or inventory change is implied unless a later coordinator task board explicitly routes it.",
)

PAIR_OPERATING_RULES = (
    "director -> operator is the fast path inside each pair: director scopes and sends the smallest sufficient artifact; operator verifies only that artifact or landed commit.",
    "Every baton handoff is a mailbox artifact, not chat: brief, verify-request, verification-report, or handoff with commit/range, paths, tests, exclusions, and exact next trigger.",
    "Every live-seat/coordinator turn ends with an `Exact Next Trigger` section naming the next lawful prompt, seat event, standby condition, or blocker.",
    "Director sends one verify-request per implementation or brief once scope is stable; include commit/range, brief path, evidence commands, known excluded workspace state, and expected verdict.",
    "Operator waits for a fresh verify-request or shipping commit; no duplicate Lane V for docs-only, status-only, or handoff-only commits, and no speculative verification when phase is ambiguous.",
    "No receipt/status churn: send mail only when it changes ownership, preserves evidence, requests verification, returns GO/NITS/FAIL, or blocks on user-gated side effects.",
    "When both seats are active, do not edit the same files or rerun the same task; first commit to land wins and the other seat narrows or stands down after git/mailbox refresh.",
    "At boundaries, stop with exact next trigger and durable handoff only when context is transferring; avoid broad recaps when mailbox/gate state already proves standby.",
    "Effectiveness means a closed loop: director artifact -> operator verification-report GO/NITS/FAIL -> director consumes the report or coordinator closes; gate scripts never substitute for operator verification-report GO.",
)

CAPACITY_SPLIT_DEFAULT_RULES = (
    "single-pair fast path remains the default for narrow or shared-file work.",
    "divisible or preplanned larger work defaults to dual-pair routing.",
    "Coordinator promotion question: can this route produce two independently reviewable deliverables?",
    "If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.",
    "If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.",
    "The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.",
    "Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.",
    "coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.",
)

SEAT_SUBAGENT_DEVELOPMENT_RULES = (
    "Core rule: seats retain authority; subagents own bounded work.",
    "Live seats and coordinator may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.",
    "Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.",
    "After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.",
    "director/director2: dispatch bounded implementer subagents for independent implementation slices, then require spec review, quality review, and director-seat synthesis before any verify-request.",
    "operator/operator2: use read-only verifier helpers for diff inspection, focused reproduction, or edge-case review; the operator seat still owns GO/NITS/FAIL.",
    "coordinator: use read-only reconciliation helpers for inventory, mailbox, lock, gate, or plan-readiness checks; the coordinator still owns the consolidated route or no-op report.",
    "Required loop: implementer -> spec review -> quality review -> seat synthesis.",
    "Subagents receive only the parent prompt, allowed paths, acceptance evidence, and side-effect limits; they do not inherit mailbox, cursor, lock, push, spend, or seat authority.",
    "Subagent output is evidence for the parent seat, not durable protocol state by itself.",
    "A subagent cannot create a mailbox cursor, mailbox event, operator GO, coordinator route, push, lock, pod spend, or paid API spend unless the live seat/coordinator with authority performs that action under user-gated rules.",
    "Do not run parallel implementation subagents on shared files or behind the same push-gated lock.",
)

SIDE_EFFECT_EXECUTOR_TOKEN_FIELDS = (
    "side_effect_id",
    "executor",
    "target",
    "allowed_command_class",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
)

SIDE_EFFECT_EXECUTOR_RULES = (
    "generic user approval is unit consent, not executor election",
    "shared user-gated side effects need exactly one named executor before mutation unless the user directly names the executing seat in the same prompt",
    "side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation",
    "observer seats default to observer mode: read live state only, do not repeat the side effect, and report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request",
    "live evidence may close an already-satisfied side effect without appointing a redundant executor",
    "multiple same-target side-effect success claims need a common side_effect_id; otherwise route validation fails",
    "lane-only implementation, verify-request, and GO/NITS/FAIL flows remain valid when no shared user-gated side effect is present",
)

CLAUDE_FUNCTION_HARMONIZATION_RULES = (
    (
        "core stance",
        "adapt Claude functions to Codex-native primitives; do not transplant Claude-only mechanics",
    ),
    (
        "AskUserQuestion discipline",
        "ask only for cross-cutting, policy, or hard-to-reverse choices; use repo convention and durable state for ordinary file, naming, and routing choices",
    ),
    (
        "background work discipline",
        "let long verification run in an exec session while independent read-only context gathering continues, then read the result before claiming status",
    ),
    (
        "dispatch-template minimalism",
        "give subagents only the relevant rule IDs, allowed paths, evidence checks, side-effect limits, and env-u git hygiene instead of inherited doctrine",
    ),
    (
        "reviewer evidence rigor",
        "reviewers use pass | issues | unable_to_verify, U1-U5 unverifiable reasons, reviewed-head checks, clean-tree checks, and command evidence",
    ),
    (
        "adversarial verification",
        "verification agents actively try to make the gate or proof fail with non-vacuous RED, --runxfail, sibling, and touched-script/hook checks",
    ),
)

EMERGENCY_HANDLING_RULES = (
    "Scope: emergency is exactly one of four categories: Production-affecting OR user-data-integrity issue; Security-critical; Active bleed-rate; External time-pressure.",
    "Events outside those four categories use normal role partition and proposal cycles, even when they feel urgent.",
    "first-noticer claims initial response with a dispatch-claim mailbox event carrying urgency: emergency.",
    "Triage discipline: stop-the-bleed first; use the smallest mitigation before root-cause analysis.",
    "Cross-seat temporary authority applies only during transplant or context exhaustion, and the commit body must include acting under v5 §E temporary authority.",
    "coordinator no-production-code boundary remains in force during emergency routing and reconciliation.",
    "Within one session of resolution, write a post-incident note in docs/INCIDENT-LOG.md and review protocol gaps.",
)

DISAGREEMENT_HANDLING_RULES = (
    "States the disagreement explicitly in the next-cycle revision.",
    "Provides project-data-grounded evidence for the disputed item.",
    "Chooses exactly one resolution path: counter-refinement, defer to v(N+1), or acceptance criterion.",
    "silent-accept is the receiver's own acceptance, not permission inferred from peer silence.",
    "Re-REPLY is allowed for a live objection, but the 2-cycle escalation limit sends persistent disagreement to the user-principal.",
)

BLOCKED_WAVE_ACTING_COORDINATOR_RULES = (
    "Require wave-gate evidence before asserting blocked.",
    "Trigger immediate pod-off when a director gate-request is unserviced.",
    "Send one consolidated mailbox event naming blocker, owner, and SLA.",
    "If the owning coordinator is absent, escalate to user with the acting-coordinator path.",
    "Use a pre-brief skeleton only until the blocked owner or user direction confirms scope.",
    "Use no gate-relaxing or suppressive pins to make a blocked wave look green.",
    "A blocked-wave transition is verified only from operator GO, not route prose or a gate script alone.",
)

REVIEWER_RESULT_HANDLING_RULES = (
    "Use findings-first ordering by severity for review output and verification reports.",
    "When relaying reviewer or verifier output, preserve verdict, findings, and next steps.",
    "separate uncertainty, inference, and follow-up so readers can tell evidence from hypothesis.",
    "do not auto-fix after a review; route or request the next implementation action instead.",
    "failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.",
)

LIVE_LOOP_STEPS = (
    "On a fresh/transplanted instance, first find the newest same-seat handoff "
    "docs/HANDOFF-<concrete-seat>-*.md, or docs/HANDOFF-coordinator-*.md for "
    "coordinator, before seat_status.py and git log; use the concrete seat, not "
    "the behavior source.",
    "Orient from seat_status.py plus git log before protocol decisions.",
    "Always check mail before protocol decisions and state-asserting writes: "
    "refresh live mailbox state, read mailbox bodies and committed files, "
    "and do not decide from counts alone.",
    "Classify the live role: readiness bridge, named seat, or coordinator.",
    "Name concrete evidence before acting: mailbox bodies, gate output, smoke output, and diff scope.",
    "Run gate scripts and smoke commands only as evidence, not as operator GO.",
    "Before any active coordinator task-board route, run `scripts/protocol_capacity_board.py --wave <wave>` and validate the draft with `scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md`; fix named gate failures before committing the route.",
    "Send one coordinator-to-all route if needed, then verify receipt seat-by-seat.",
    "When a full coordinator/live-seat cycle reaches a real completion boundary and assigned tasks are complete, write a durable handoff before transplant or context switch, including fresh git/mailbox/gate/smoke state and the exact next trigger.",
    "Before ending any live-seat/coordinator turn, output `Exact Next Trigger` as the final section in the mailbox artifact and user-facing final response.",
    "Push remains user-gated; locks, paid spend, and pod spend require explicit consent.",
)

LEDGER_CLI_BRIDGE = {
    "doc_path": "docs/protocol/codex/ledger-cli-adoption.md",
    "guard_script": "scripts/ledger_start_guard.py",
    "pipeline_kernel": "/Users/hyungkoookkim/Pipeline",
    "forbidden_kernel": "/Users/hyungkoookkim/Content",
    "target_repo": "/Users/hyungkoookkim/evidence-ledger",
    "guard_start_command": "scripts/ledger_start_guard.py --seat <seat> --wave 2",
    "kernel_rules": (
        "Pipeline remains the Codex four-seat governance kernel.",
        "Evidence-ledger remains the product repo and owns product-local truth.",
        "Do not start ledger work from /Users/hyungkoookkim/Content.",
        "Run scripts/ledger_start_guard.py --seat <seat> --wave 2 before entering evidence-ledger.",
        "Start as readiness bridge unless the prompt names a live seat or coordinator.",
        "A named seat may work on ledger only inside the explicit route.",
        "Coordinator may reconcile ledger work from durable evidence but may not author behavior-changing product fixes.",
    ),
    "cross_repo_git_rules": (
        "Prefix every ordinary cross-repo git and pytest command with env -u GIT_INDEX_FILE.",
        "Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.",
        "Record both Pipeline and evidence-ledger heads in cross-repo handoffs.",
        "Do not copy the whole Pipeline protocol tree into evidence-ledger.",
    ),
}

CODEX_VERIFICATION_COMMANDS = (
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
    "tests/unit/test_imports_smoke.py "
    "tests/unit/test_protocol_mailbox.py "
    "tests/unit/test_status.py "
    "tests/unit/test_coordination_tooling.py "
    "tests/unit/test_ceremony_gates.py "
    "tests/unit/test_protocol_capacity.py "
    "tests/unit/test_protocol_doc_integrity.py "
    "tests/unit/test_protocol_prompt_sync.py "
    "tests/unit/test_codex_ledger_bridge.py -q",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
)

CODEX_SURFACES = (
    ("AGENTS.md", "root durable repo rules"),
    ("docs/protocol/protocol-assembly-map.md", "folder-intent assembly map"),
    ("docs/protocol/codex/continuation.md", "model-backed Codex workflow"),
    (
        LEDGER_CLI_BRIDGE["doc_path"],
        "ledger CLI adoption bridge for evidence-ledger target work",
    ),
    (
        LEDGER_CLI_BRIDGE["guard_script"],
        "ledger seat start guard that enforces Pipeline kernel before target repo work",
    ),
    (".agents/skills/four-seat-protocol/SKILL.md", "runtime checklist"),
    (".codex/agents/*.toml", "spawned role instructions"),
    (".codex/hooks.json", "session/tool guardrails"),
    ("scripts/continuation_readiness.py", "read-only harness report"),
    (".agents/skills/four-seat-protocol/scripts/seat_status.py", "live-seat orientation"),
)

PROTOCOL_ASSEMBLY_PORTIONS = (
    (
        "Universal protocol policy",
        "docs/protocol/agents/",
        "Rules that apply across tools belong outside a Codex-specific surface.",
    ),
    (
        "Codex protocol mapping",
        "docs/protocol/codex/continuation.md",
        "Codex-specific mechanics map the universal rules onto Codex-native surfaces.",
    ),
    (
        "Target-repo CLI adoption bridge",
        LEDGER_CLI_BRIDGE["doc_path"],
        "Target-repo adoption is Codex-specific mechanics and should not duplicate universal protocol policy.",
    ),
    (
        "Live seat checklists",
        ".agents/skills/",
        "Seat procedures are reusable runtime instructions, not durable mailbox state.",
    ),
    (
        "Spawnable Codex roles",
        ".codex/agents/*.toml",
        "Role prompts are executable agent modules with explicit authority boundaries.",
    ),
    (
        "Mailbox events",
        "coordination/mailbox/sent/",
        "Inter-seat protocol speech is durable state that survives chat/session loss.",
    ),
    (
        "Mailbox read cursors",
        "coordination/mailbox/seen/",
        "Per-seat consumed-up-to timestamps are the single read-state truth.",
    ),
    (
        "Shared-file locks",
        "coordination/locks/",
        "Lock files represent temporary ownership of cross-seat shared modules.",
    ),
    (
        "Campaign board",
        "docs/REMEDIATION-INVENTORY.md",
        "Wave rows, lane owners, statuses, and verifier evidence live in one board.",
    ),
    (
        "Director briefs",
        "docs/superpowers/briefs/",
        "R-BRIEFs are task-local implementation packets, not global policy.",
    ),
    (
        "Executable checks",
        "scripts/",
        "Gate, readiness, smoke, and lint checks should be runnable instruments.",
    ),
    (
        "Committed evidence",
        "logs/",
        "Discovery and product-oracle outputs are proof artifacts cited by protocol state.",
    ),
    (
        "Protocol tool tests",
        "tests/unit/",
        "Tool contracts are enforced by focused tests rather than prose alone.",
    ),
)

MERMAID_DIAGRAM = """flowchart TD
    user["User principal"]
    harness["Codex CLI harness"]
    state["Durable shared state"]
    mailbox["Mailbox sent/ + seen cursors"]
    seats["director / director2 / operator / operator2"]
    coordinator["coordinator"]
    gate["Gate + receipt loop"]

    user --> harness
    harness --> state
    state --> mailbox
    mailbox --> seats
    mailbox --> coordinator
    seats --> gate
    coordinator --> gate
    gate --> state
"""


def render_mermaid() -> str:
    """Return the canonical Mermaid diagram body for the Codex harness."""
    return MERMAID_DIAGRAM


def render_live_loop() -> str:
    """Return the canonical live-loop checklist as Markdown."""
    return "\n".join(
        f"{index}. {step}" for index, step in enumerate(LIVE_LOOP_STEPS, start=1)
    )


def render_kernel_contract(*, include_trigger_specific: bool = True) -> str:
    """Return the thin-kernel contract and demoted optional concepts."""
    demoted_concepts = DEMOTED_RUNTIME_CONCEPTS
    if not include_trigger_specific:
        demoted_concepts = tuple(
            concept
            for concept in DEMOTED_RUNTIME_CONCEPTS
            if concept[0] != "Rotating Planning Relay"
        )
    lines = ["Active kernel invariants"]
    lines.extend(
        f"- {name}: {description}" for name, description in ACTIVE_KERNEL_INVARIANTS
    )
    lines.append("")
    lines.append("Demoted optional concepts")
    lines.extend(
        f"- {name}: {description}" for name, description in demoted_concepts
    )
    return "\n".join(lines)


def render_planning_relay() -> str:
    """Return the all-seat planning relay contract as Markdown."""
    lines = [
        "Rotating Planning Relay:",
        "canonical seat order: " + " -> ".join(PLANNING_RELAY_ORDER),
    ]
    lines.extend(f"- {rule}" for rule in PLANNING_RELAY_RULES)
    lines.append("coordinator-started plan: coordinator -> all four seats -> coordinator")
    lines.append("distribution: one consolidated coordinator-to-all task board")
    return "\n".join(lines)


def render_pair_operating_contract() -> str:
    """Return the efficient director/operator pair contract as Markdown."""
    lines = ["Pair Operating Contract:"]
    lines.extend(f"- {rule}" for rule in PAIR_OPERATING_RULES)
    return "\n".join(lines)


def render_capacity_split_default() -> str:
    """Return the default promotion rule for one-pair versus two-pair routes."""
    lines = ["Capacity Split Default:"]
    lines.extend(f"- {rule}" for rule in CAPACITY_SPLIT_DEFAULT_RULES)
    return "\n".join(lines)


def render_seat_subagent_development() -> str:
    """Return the all-seat contract for bounded subagent-driven work."""
    lines = ["Seat Subagent Development:"]
    lines.extend(f"- {rule}" for rule in SEAT_SUBAGENT_DEVELOPMENT_RULES)
    lines.append(
        "blocked side effects: no mailbox cursor, mailbox event, operator GO, "
        "coordinator route, push, lock, pod spend, or paid API spend from a "
        "subagent alone"
    )
    return "\n".join(lines)


def render_codex_execution_tiers() -> str:
    """Return the risk-proportional applicability contract for Codex work."""
    lines = ["Codex Risk-Tier Router:"]
    for tier, trigger, checks in CODEX_EXECUTION_TIERS:
        lines.append(f"- `{tier}`: {trigger}; {checks}.")
    lines.extend(f"- {rule}" for rule in VERIFICATION_DEDUPLICATION_RULES)
    return "\n".join(lines)


def render_r_independence() -> str:
    """Return the Pipeline Codex independence-first contract."""
    lines = ["R-INDEPENDENCE:"]
    lines.extend(f"- {rule}" for rule in R_INDEPENDENCE_RULES)
    return "\n".join(lines)


def render_side_effect_executor_contract() -> str:
    """Return the single-executor contract for shared user-gated side effects."""
    lines = [
        "Side-Effect Executor Token:",
        "required fields: " + ", ".join(SIDE_EFFECT_EXECUTOR_TOKEN_FIELDS),
    ]
    lines.extend(f"- {rule}" for rule in SIDE_EFFECT_EXECUTOR_RULES)
    return "\n".join(lines)


def render_claude_function_harmonization() -> str:
    """Return the Claude-to-Codex function harmonization contract."""
    lines = ["Claude Function Harmonization:"]
    lines.extend(
        f"- {name}: {description}"
        for name, description in CLAUDE_FUNCTION_HARMONIZATION_RULES
    )
    return "\n".join(lines)


def render_emergency_handling_contract() -> str:
    """Return the Codex emergency handling contract."""
    lines = ["Emergency Handling:"]
    lines.extend(f"- {rule}" for rule in EMERGENCY_HANDLING_RULES)
    return "\n".join(lines)


def render_disagreement_handling_contract() -> str:
    """Return the Codex disagreement handling contract."""
    lines = ["Disagreement Handling:"]
    lines.extend(f"- {rule}" for rule in DISAGREEMENT_HANDLING_RULES)
    return "\n".join(lines)


def render_blocked_wave_acting_coordinator_contract() -> str:
    """Return the Codex blocked-wave and acting-coordinator contract."""
    lines = ["Blocked-Wave and Acting-Coordinator Handling:"]
    lines.extend(f"- {rule}" for rule in BLOCKED_WAVE_ACTING_COORDINATOR_RULES)
    return "\n".join(lines)


def render_reviewer_result_handling_contract() -> str:
    """Return the reviewer/verifier result-handling contract."""
    lines = ["Reviewer Result Handling:"]
    lines.extend(f"- {rule}" for rule in REVIEWER_RESULT_HANDLING_RULES)
    return "\n".join(lines)


def render_ledger_cli_bridge() -> str:
    """Return the Codex bridge contract for evidence-ledger target work."""
    lines = [
        "Ledger CLI Bridge:",
        f"- Pipeline kernel: `{LEDGER_CLI_BRIDGE['pipeline_kernel']}`",
        f"- Target repo: `{LEDGER_CLI_BRIDGE['target_repo']}`",
        f"- Forbidden kernel: `{LEDGER_CLI_BRIDGE['forbidden_kernel']}`",
        f"- Bridge doc: `{LEDGER_CLI_BRIDGE['doc_path']}`",
        f"- Start guard: `{LEDGER_CLI_BRIDGE['guard_start_command']}`",
        "- Runtime:",
    ]
    lines.extend(f"  - {rule}" for rule in LEDGER_CLI_BRIDGE["kernel_rules"])
    lines.append("- Cross-repo hygiene:")
    lines.extend(f"  - {rule}" for rule in LEDGER_CLI_BRIDGE["cross_repo_git_rules"])
    return "\n".join(lines)


def render_ledger_start_guard() -> str:
    """Return the concrete Pipeline-first start commands for ledger-routed seats."""
    guard = LEDGER_CLI_BRIDGE["guard_script"]
    kernel = LEDGER_CLI_BRIDGE["pipeline_kernel"]
    forbidden = LEDGER_CLI_BRIDGE["forbidden_kernel"]
    seats = ("coordinator", "director", "director2", "operator", "operator2")
    lines = [
        "Ledger Start Guard:",
        f"- Always start ledger-routed Codex seats from `cd {kernel}`.",
        f"- Do not start from `{forbidden}`.",
        "- Run the guard before entering evidence-ledger:",
        f"  - env -u GIT_INDEX_FILE .venv/bin/python {LEDGER_CLI_BRIDGE['guard_start_command']}",
        "- Seat starts:",
    ]
    lines.extend(
        "  - "
        f"{seat}: env -u GIT_INDEX_FILE .venv/bin/python {guard} --seat {seat} --wave 2"
        for seat in seats
    )
    return "\n".join(lines)


def render_codex_verification_commands() -> str:
    """Return current Codex protocol verification commands."""
    lines = ["Codex verification commands:"]
    lines.extend(f"- `{command}`" for command in CODEX_VERIFICATION_COMMANDS)
    return "\n".join(lines)


def is_agent_extension_name(name: str) -> bool:
    """Return whether *name* is an optional self-codified agent extension."""
    return (
        name.startswith("agent")
        and name.endswith(".toml")
        and len(name) == len("agent00.toml")
        and name[5:7].isdigit()
    )


def render_agent_extension_summary(agent_names: list[str] | tuple[str, ...] = ()) -> str:
    """Return a compact summary of optional agentNN harness extensions."""
    extensions = sorted({name for name in agent_names if is_agent_extension_name(name)})
    lines = [
        "agent guardrail extensions: "
        + (", ".join(extensions) if extensions else "(none discovered)"),
    ]
    lines.extend(f"extension rule: {rule}" for rule in AGENT_EXTENSION_RULES)
    return "\n".join(lines)


def render_agent_extension_routing_contract() -> str:
    """Return the routing contract for optional agentNN guardrail extensions."""
    lines = ["Agent Extension Routing Contract:"]
    for agent, purpose, route_when in AGENT_EXTENSION_ROUTING_CONTRACT:
        lines.append(f"- `{agent}`: {purpose}; use for {route_when}.")
    lines.append(
        "extension output is evidence for the parent, "
        "not a mailbox event, cursor advance, operator GO, coordinator route, "
        "lock action, push, or spend authorization"
    )
    return "\n".join(lines)


def _mode_from_role(role: str) -> str:
    """Infer a runtime mode from an explicit role when CODEX_AGENT_MODE is unset."""
    if role in SEATS:
        return "live-seat"
    if role in COORDINATOR_SEATS:
        return "coordinator"
    if role in SPAWNED_ROLE_AGENT_ROLES:
        return "subagent"
    if role == "readiness-bridge":
        return "readiness-bridge"
    return ""


def _mode_from_seat(seat: str) -> str:
    """Infer a runtime mode from CODEX_SEAT compatibility spellings."""
    if seat in SEATS:
        return "live-seat"
    if seat in COORDINATOR_SEATS:
        return "coordinator"
    return ""


def infer_runtime_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Infer the Codex runtime contract from an environment-like mapping."""
    env = environ or {}
    seat = env.get("CODEX_SEAT", "")
    explicit_mode = env.get("CODEX_AGENT_MODE", "")
    explicit_role = env.get("CODEX_AGENT_ROLE", "")

    if explicit_mode:
        mode = explicit_mode
    elif explicit_role:
        mode = (
            _mode_from_role(explicit_role)
            or _mode_from_seat(seat)
            or "readiness-bridge"
        )
    elif _mode_from_seat(seat):
        mode = _mode_from_seat(seat)
    else:
        mode = "readiness-bridge"

    if explicit_role:
        role = explicit_role
    elif mode == "live-seat" and seat in SEATS:
        role = seat
    else:
        role = mode

    if mode == "live-seat" and seat in SEATS:
        seat_display = seat
    elif mode == "coordinator" and seat in COORDINATOR_SEATS:
        seat_display = seat
    elif seat:
        seat_display = f"(ignored: {seat})"
    else:
        seat_display = "(unset)"
    behavior_source = behavior_source_for_seat(role) if mode == "live-seat" else None

    capability_defaults = {
        "readiness-bridge": "read-only",
        "live-seat": "seat-local",
        "coordinator": "capacity-max",
        "subagent": "parent-scoped",
    }
    mutation_defaults = {
        "readiness-bridge": "none",
        "live-seat": "seat-owned",
        "coordinator": "coordination-only",
        "subagent": "parent-scoped",
        "lane-v-verifier": "read-only-verification",
        "money-gate-reviewer": "read-only-verification",
    }

    capability = env.get("CODEX_CAPABILITY_MODE", capability_defaults.get(mode, "parent-scoped"))
    mutation = env.get(
        "CODEX_MUTATION_SCOPE",
        mutation_defaults.get(role, mutation_defaults.get(mode, "parent-scoped")),
    )
    authority_defaults = {
        "readiness-bridge": "report-only",
        "live-seat": "seat-owned",
        "coordinator": "all-scope-reconcile",
        "subagent": "parent-scoped",
    }
    mailbox_defaults = {
        "readiness-bridge": "read-only-no-consume",
        "live-seat": "seat-read-consume-intentional",
        "coordinator": "all-scope-read-no-consume",
        "subagent": "parent-scoped",
    }
    git_defaults = {
        "readiness-bridge": "env-u-git-index-read-only",
        "live-seat": "per-seat-index-for-cursor-status",
        "coordinator": "env-u-git-index-or-temp-index",
        "subagent": "env-u-git-index-parent-scoped",
    }
    verification_defaults = {
        "readiness-bridge": "report-evidence-only",
        "coordinator": "reconcile-operator-go-only",
        "subagent": "parent-scoped-no-go",
    }
    context_defaults = {
        "readiness-bridge": "repo-docs-mailbox-gates-readonly",
        "live-seat": "seat-mailbox-owned-files-gate-evidence",
        "coordinator": "all-scope-mailbox-inventory-locks-gates",
        "subagent": "parent-prompt-plus-allowed-artifacts",
    }
    output_defaults = {
        "readiness-bridge": "readiness-report-and-blockers",
        "live-seat": "seat-artifact-or-operator-request",
        "coordinator": "capacity-board-or-single-route",
        "subagent": "bounded-findings-to-parent",
    }
    decision_defaults = {
        "readiness-bridge": "no-seat-authority",
        "live-seat": "lane-owned-seat",
        "coordinator": "all-scope-routing-no-production-fixes",
        "subagent": "parent-scoped-no-seat-authority",
    }
    next_action_defaults = {
        "readiness-bridge": "report-then-stop-or-request-role",
        "live-seat": "read-mail-then-act-or-report-idle",
        "coordinator": "build-board-reconcile-once",
        "subagent": "return-evidence-then-stop",
    }
    if role in DIRECTOR_SEATS:
        verification_default = "request-operator-go"
    elif role in OPERATOR_SEATS:
        verification_default = "independent-go-nits-fail"
    elif role in READ_ONLY_VERIFIER_ROLES:
        verification_default = "read-only-review-no-go"
    else:
        verification_default = verification_defaults.get(mode, "parent-scoped-no-go")

    authority = env.get("CODEX_AUTHORITY_SCOPE", authority_defaults.get(mode, "parent-scoped"))
    mailbox = env.get("CODEX_MAILBOX_POLICY", mailbox_defaults.get(mode, "parent-scoped"))
    git_policy = env.get("CODEX_GIT_POLICY", git_defaults.get(mode, "env-u-git-index-parent-scoped"))
    verification = env.get("CODEX_VERIFICATION_POLICY", verification_default)
    context_sources = env.get(
        "CODEX_CONTEXT_SOURCES",
        context_defaults.get(mode, "parent-prompt-plus-allowed-artifacts"),
    )
    output_contract = env.get(
        "CODEX_OUTPUT_CONTRACT",
        output_defaults.get(mode, "bounded-findings-to-parent"),
    )
    decision_boundary = env.get(
        "CODEX_DECISION_BOUNDARY",
        decision_defaults.get(mode, "parent-scoped-no-seat-authority"),
    )
    next_action = env.get(
        "CODEX_NEXT_ACTION_POLICY",
        next_action_defaults.get(mode, "return-evidence-then-stop"),
    )

    return {
        "CODEX_AGENT_MODE": mode,
        "CODEX_AGENT_ROLE": role,
        "CODEX_SEAT": seat_display,
        "CODEX_BEHAVIOR_SOURCE": behavior_source or "(none)",
        "CODEX_CAPABILITY_MODE": capability,
        "CODEX_MUTATION_SCOPE": mutation,
        "CODEX_AUTHORITY_SCOPE": authority,
        "CODEX_MAILBOX_POLICY": mailbox,
        "CODEX_GIT_POLICY": git_policy,
        "CODEX_VERIFICATION_POLICY": verification,
        "CODEX_CONTEXT_SOURCES": context_sources,
        "CODEX_OUTPUT_CONTRACT": output_contract,
        "CODEX_DECISION_BOUNDARY": decision_boundary,
        "CODEX_NEXT_ACTION_POLICY": next_action,
        "CODEX_SIDE_EFFECT_POLICY": "user-consent-required",
        "GIT_INDEX_FILE": env.get("GIT_INDEX_FILE", "(unset)"),
    }


def render_runtime_env_contract(environ: Mapping[str, str] | None = None) -> str:
    """Return the executable runtime environment contract for Codex agents."""
    values = infer_runtime_env(environ)
    lines = [
        "Runtime env contract:",
        *(f"{name}={values[name]}" for name, _, _ in RUNTIME_ENV_VARIABLES),
        "contract variables:",
    ]
    lines.extend(f"- {name}: {allowed}; {meaning}" for name, allowed, meaning in RUNTIME_ENV_VARIABLES)
    lines.extend(
        (
            "contract rules:",
            "- readiness-bridge is the default when CODEX_AGENT_MODE and CODEX_SEAT are unset.",
            "- CODEX_SEAT selects a live seat for director/director2/operator/operator2.",
            "- CODEX_BEHAVIOR_SOURCE names the canonical live-seat behavior source; CODEX_SEAT remains the concrete mailbox, cursor, and git-index identity.",
            "- CODEX_SEAT=coordinator is a compatibility spelling for coordinator mode; coordinator remains unpinned and never has a consumable cursor.",
            "- CODEX_AGENT_ROLE can infer coordinator, live-seat, or subagent mode when CODEX_AGENT_MODE is unset.",
            "- behavior variables are inferred from mode and role unless explicitly narrowed by the launcher.",
            "- fresh/transplanted live seat first finds the newest same-seat handoff under docs/HANDOFF-<concrete-seat>-*.md; coordinator uses docs/HANDOFF-coordinator-*.md.",
            "- always check mail before protocol decisions and state-asserting writes; read bodies, not counts alone.",
            "- coordinator remains unpinned; no coordinator cursor is consumed.",
            "- env does not authorize push, lock-claim side effects, paid API spend, or pod spend; user consent still gates them.",
            "- CODEX_SIDE_EFFECT_POLICY is always user-consent-required for push, lock-claim side effects, paid API spend, and pod spend.",
        )
    )
    return "\n".join(lines)


def render_seat_contract(
    environ: Mapping[str, str] | None = None,
    *,
    objective: str = "(unset)",
    permissions: str = "(unset)",
    scope: str = "(unset)",
    verification: str = "(unset)",
    done: str = "(unset)",
) -> str:
    """Return the six-field live-seat contract without touching durable state."""
    values = infer_runtime_env(environ)
    role_value = f"{values['CODEX_AGENT_MODE']} / {values['CODEX_AGENT_ROLE']}"
    lines = [
        "Seat contract:",
        f"S-ROLE: {role_value}",
        f"S-OBJ: {objective}",
        f"S-PERM: {permissions}",
        f"S-SCOPE: {scope}",
        f"S-VERIFY: {verification}",
        f"S-DONE: {done}",
        "source order: user > git > mailbox > handoff > defaults",
        "side effects: push, lock, paid API spend, and pod spend require user consent",
    ]
    return "\n".join(lines)


def render_start_session_inhabitance(agent_names: list[str] | tuple[str, ...] = ()) -> str:
    """Return the fresh-session contract for inhabiting the Codex harness."""
    lines = [
        "Next start session:",
        "Action: inhabit the Codex harness as readiness bridge by default.",
        "Core contract:",
    ]
    lines.extend(f"{index}. {step}" for index, step in enumerate(START_SESSION_STEPS, start=1))
    lines.append("core agent modules: " + ", ".join(CORE_AGENT_MODULES))
    lines.append(render_codex_execution_tiers())
    lines.append(render_r_independence())
    lines.append(render_agent_extension_summary(agent_names))
    lines.append(render_agent_extension_routing_contract())
    return "\n".join(lines)


def render_protocol_assembly_map() -> str:
    """Return the folder-intent map for reassembling protocol portions."""
    lines = [
        "Protocol assembly rule: use the lowest folder that can own it without ambiguity.",
        "",
        "| Protocol portion | Intended home | Reason |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| {portion} | `{home}` | {reason} |"
        for portion, home, reason in PROTOCOL_ASSEMBLY_PORTIONS
    )
    return "\n".join(lines)


CROSS_MODEL_VERIFICATION_RULES = (
    "after every Codex Lane V verification in the Pipeline repository, attempt exactly one verdict-blind Opus review before the final verdict",
    "the Opus request carries the reviewed commit/range, requirements, allowed paths, exact verification commands, and a recorded user-task:<id> or verify-request:<id> authorization source but no Codex verdict, report, findings, or conclusion",
    "the Opus call occurs only when the parent prompt supplies recorded task-level authorization; absent parent authorization yields unavailable without an external call",
    "parent-supplied recorded authorization permits exactly the one bounded Opus call and does not grant inherited paid-spend authority",
    "V1 applies only to Pipeline-repository verification",
    "Cross-repo and evidence-ledger verification use explicit Codex-only fallback outside V1, not an incomplete required Opus pass",
    "operator retains GO/NITS/FAIL authority; Opus output is advisory evidence and never a mailbox event or protocol verdict",
    "unavailable is explicit degraded Codex-only fallback with the reason preserved; it is never treated as pass",
    "every Opus finding requires a disposition: confirmed, disproved with concrete evidence, or unresolved",
    "an unresolved Opus finding blocks GO; confirmed minor findings require NITS and confirmed important/critical findings require FAIL",
    "reconciliation requires explicit expected HEAD/base and preserves reviewed scope; a mismatch rejects stale or replayed review JSON",
    "reconciliation requires an explicit Pipeline repo root and local proof that expected HEAD/base commits exist before GO",
    "the bridge permits one Claude process attempt and no automatic retry for a verification attempt",
    "no third same-question generic reviewer runs over the unchanged commit unless R-VERIFY-TIER names a distinct question",
    "Do not launch generic same-question spec or code-quality reviewers for Codex Lane V; the primary Codex analysis and blind Opus pass are the pair",
    "generic Lane V helpers are not used for Codex same-question review; only a different pre-stated specialist question is eligible under R-VERIFY-TIER",
)


def render_cross_model_verification() -> str:
    """Return the Codex-to-Opus independent verification contract."""
    lines = ["Cross-Model Opus Verification:"]
    lines.extend(f"- {rule}" for rule in CROSS_MODEL_VERIFICATION_RULES)
    return "\n".join(lines)


def render_surface_summary() -> str:
    """Return a compact Markdown summary of surfaces and invariants."""
    demoted_names = (
        name
        for name, _ in DEMOTED_RUNTIME_CONCEPTS
        if name != "Rotating Planning Relay"
    )
    lines = [
        f"source: {MODEL_SOURCE}",
        f"central invariant: {CENTRAL_INVARIANT}",
        "durable artifacts: " + ", ".join(DURABLE_STATE_ARTIFACTS),
        "core agent modules: " + ", ".join(CORE_AGENT_MODULES),
        "coordinator invariants: " + "; ".join(COORDINATOR_INVARIANTS),
        "Active kernel invariants: "
        + ", ".join(name for name, _ in ACTIVE_KERNEL_INVARIANTS),
        "Demoted optional concepts: " + ", ".join(demoted_names),
        "Pair Operating Contract: director -> operator is the fast path; mailbox artifact, not chat",
        "Capacity Split Default: divisible or preplanned larger work defaults to dual-pair routing",
        "Seat Subagent Development: seats retain authority; subagents own bounded work",
        "Cross-Model Opus Verification: every Codex Lane V pass attempts one blind Opus review",
        "Codex Risk-Tier Router: conversational and read-only work avoid implementation ceremony",
        "R-INDEPENDENCE: adversarial-surface work requires design-time enumeration and independent actual-diff verification",
        "Side-Effect Executor Token: generic user approval is unit consent, not executor election",
        "Ledger CLI Bridge: Pipeline kernel -> evidence-ledger target via "
        + LEDGER_CLI_BRIDGE["doc_path"],
        "agent extension namespace: .codex/agents/agentNN.toml guardrail extensions",
        "runtime env contract: "
        + ", ".join(name for name, _, _ in RUNTIME_ENV_VARIABLES),
        "Codex surfaces:",
    ]
    lines.extend(f"- {path}: {purpose}" for path, purpose in CODEX_SURFACES)
    return "\n".join(lines)


def main() -> int:
    print("# Codex Harness Model")
    print()
    print("```mermaid")
    print(render_mermaid().rstrip())
    print("```")
    print()
    print("## Live Loop")
    print(render_live_loop())
    print()
    print("## Kernel Contract")
    print(render_kernel_contract(include_trigger_specific=False))
    print()
    print("## R-INDEPENDENCE")
    print(render_r_independence())
    print()
    print("## Pair Operating Contract")
    print(render_pair_operating_contract())
    print()
    print("## Capacity Split Default")
    print(render_capacity_split_default())
    print()
    print("## Seat Subagent Development")
    print(render_seat_subagent_development())
    print()
    print("## Cross-Model Opus Verification")
    print(render_cross_model_verification())
    print()
    print("## Ledger CLI Bridge")
    print(render_ledger_cli_bridge())
    print()
    print("## Ledger Start Guard")
    print(render_ledger_start_guard())
    print()
    print("## Codex Verification Commands")
    print(render_codex_verification_commands())
    print()
    print("## Protocol Assembly Map")
    print(render_protocol_assembly_map())
    print()
    print("## Surface Summary")
    print(render_surface_summary())
    print()
    print("## Runtime Env Contract")
    print(render_runtime_env_contract(os.environ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
