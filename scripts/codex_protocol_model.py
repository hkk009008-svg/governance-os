#!/usr/bin/env python3
"""Executable model for the Codex four-seat protocol harness.

This module is intentionally dependency-free. Protocol renderers can import it
without touching mailbox state, locks, git indexes, or production pipeline code.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace

MODEL_SOURCE = "scripts/codex_protocol_model.py"
CENTRAL_INVARIANT = "durable shared state beats chat memory"
COMPACT_PAIR_REFERENCE = "Canonical Compact Pair Invariant: scripts/codex_protocol_model.py"
COMPACT_PAIR_INVARIANT = (
    "Compact Pair Invariant: one committed verify-request binds the reviewed "
    "repository when explicit and base/head, outcome, author seat and "
    "system-visible author model, assigned non-author Operator, allowed paths, "
    "and immutable finding refs. One report from that distinct Operator seat "
    "and a different reviewer model binds the exact request and reviewed range, "
    "issues GO/NITS/FAIL, and explicitly dispositions every finding ref through "
    "the fixed mailbox writer. Missing, duplicated, abbreviated, uppercase, "
    "uncommitted, or mismatched identity, range, or finding fields are not "
    "authority."
)
AUTONOMOUS_SEAT_REFERENCE = (
    "Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py"
)
AUTONOMOUS_SEAT_RULES = (
    "Own the outcome, choose the method, and show credible evidence.",
    "Any seat may make an ownership change by claiming, splitting, merging, transferring, exchanging, or rerouting work without coordinator approval; every new owner accepts through its own durable event bound to the exact task, immutable parent and revision, and previous owners.",
    "A route fork, stale or dangling parent, or conflicting same-task tip makes only that task non-actionable; unrelated tasks continue.",
    "WORKING means meaningful progress remains; NEEDS_PEER requests help; FINDING is not BLOCKED; BLOCKED means no lawful path exists without new authority, unavailable external state, or hard-boundary resolution.",
    "Preflight is advisory and preserves material findings; it does not require CLEAR before implementation.",
    "Behavior-changing work is accepted only by non-author Operator GO from a distinct seat and different reviewer model on the actual reviewed commit or range.",
    "External effects remain separately user-gated; a seat-authored token is structural only and never grants execution authority.",
    "Known material finding refs remain immutable through ownership and reviewer changes and receive explicit report dispositions.",
    "Coordinator observes and facilitates but is not the mandatory route author or convergence gate and does not author behavior-changing production work.",
)

ACTIVE_KERNEL_INVARIANTS = (
    (
        "durable shared state beats chat memory",
        "read git, signed ref-bus facts, mailbox bodies, cursors, locks, logs, gate evidence, and operator reports before stale prose",
    ),
    (
        "threeway signed ref-bus is load-bearing",
        "the signed three-way ref-bus is the load-bearing state source for three-way facts once refs/threeway/* is live (git for-each-ref refs/threeway/ is the oracle; until then the mailbox stays authoritative); free-form mailbox remains the human coordination channel",
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
        "push, merge, lock-claim side effects, paid API spend, and pod spend require explicit user consent",
    ),
    (
        "separate side-effect gates",
        "push, merge, paid spend, and every other side effect are separately gated and require explicit authority",
    ),
    (
        "independence-first verification",
        "adversarial-surface owners assess plausible abuse classes, preserve material independent findings, and submit the actual diff for independent Operator review",
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
        "capacity diagnostics",
        "capacity boards and packet reports remain available as optional diagnostic evidence; route authority comes from route and hard-boundary validation",
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
    "The owner explicitly assesses plausible abuse classes, edge cases, and coverage targets and preserves material independent findings.",
    "An independent design-time enumeration may be used as advisory input when it adds signal; it is not a universal gate.",
    "The owner and actual-diff Operator choose proportional review depth; early independent review is encouraged when it adds signal, but it is advisory and no universal pre-implementation CLEAR gate exists.",
    "Before acceptance, a distinct non-author Operator seat using a different system-visible model reviews the actual diff or range and issues GO/NITS/FAIL through the fixed mailbox writer.",
    "R-VERIFY-TIER still prohibits redundant same-question passes.",
    "Non-adversarial, read-only, and hermetic work uses the smallest sufficient profile.",
    "Canonical full rule: docs/protocol/claude/independence-first.md.",
)

HARNESS_COMPONENTS = (
    ("user", "User principal", "explicit instruction and consent"),
    ("harness", "Codex CLI harness", "readiness bridge or explicit live role"),
    ("state", "Durable shared state", "repo artifacts that survive sessions"),
    ("seats", "director / director2 / operator / operator2", "owned lane work"),
    ("coordinator", "coordinator", "on-demand all-scope reconciliation"),
    ("gate", "verification + publication gate", "executed evidence, operator GO, and separately gated side effects"),
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

if __package__:
    from scripts import protocol_mailbox  # noqa: E402
else:
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
        "documents that push, merge, lock-claim side effects, paid API spend, and pod spend are separately gated and require user consent outside env",
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
    "Treat the signed three-way ref-bus as the load-bearing state source for three-way facts once refs/threeway/* is live (git for-each-ref refs/threeway/ is the oracle; until then the mailbox stays authoritative); the free-form mailbox remains the human coordination channel.",
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
    "route from durable evidence, not chat memory",
    "do not author production fixes",
)

AUTOMATIC_TASK_ROUTING_REFERENCE = (
    "Automatic Seat-Task Routing: scripts/codex_protocol_model.py"
)
_AUTOMATIC_TASK_ROUTING_BASE_RULES = (
    "For a committed immutable trigger naming the next concrete seat, use Codex task tools before returning a prompt to the user.",
    "The dispatch identity is the trigger path and full commit, assigned seat, Pipeline checkout, and for review the exact base/head and required reviewer model.",
    "If the same dispatch identity is already in progress, monitor it; if it completed, reconcile its committed artifact instead of resending it.",
    "Reuse one unambiguous compatible seat task; if none exists or candidates are stale, incompatible, or ambiguous, automatically create a fresh local task in the saved Pipeline project.",
    "Never ask the user to relay a seat prompt while Codex task tools are available; send the exact trigger and reconcile its committed result directly.",
    "If discovery or dispatch tools are unavailable before a trigger is sent, preserve the exact trigger and report one concrete tooling blocker without asking the user to relay it.",
)
# The canonical tuple is completed below the model's anchor-sensitive definitions.

PLANNING_RELAY_ORDER = ("director", "operator", "director2", "operator2")

PLANNING_RELAY_RULES = (
    "Use the Rotating Planning Relay when an important cross-seat plan needs all-seat review before work is distributed.",
    "For a live-seat-started plan, the starter is step 1 and the baton moves through the fixed cyclic order: director -> operator -> director2 -> operator2; the order wraps after operator2 back to director.",
    "A live-seat-started relay runs exactly four live-seat turns, then the final seat sends the result to coordinator/all-scope for reconciliation.",
    "For a coordinator-started plan, coordinator fans out to all four seats, gathers responses back to coordinator, then distributes one consolidated coordinator-to-all task board.",
    "Relay mailbox events are planning evidence only; no production work, verification verdict, lock, push, or inventory change is implied unless a later coordinator task board explicitly routes it.",
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
    "Capacity boards and packet reports remain available as optional diagnostic evidence; route authority comes from route and hard-boundary validation.",
    "Send one coordinator-to-all route if needed, then verify receipt seat-by-seat.",
    "When a full coordinator/live-seat cycle reaches a real completion boundary and assigned tasks are complete, write a durable handoff before transplant or context switch, including fresh git/mailbox/gate/smoke state.",
    "Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.",
    "At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user.",
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


def render_autonomous_seat_contract() -> str:
    """Return the sole active behavior capsule for governed seat work."""
    return AUTONOMOUS_SEAT_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in AUTONOMOUS_SEAT_RULES
    )


def render_automatic_task_routing() -> str:
    """Return the Codex coordinator's direct seat-task transport contract."""
    return AUTOMATIC_TASK_ROUTING_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in AUTOMATIC_TASK_ROUTING_RULES
    )


def render_capacity_split_default() -> str:
    """Compatibility renderer for the readiness consumer; capacity is advisory."""
    return (
        "Capacity Split Default: retired compatibility diagnostic; "
        "the former rule that divisible or preplanned larger work defaults to "
        "dual-pair routing is advisory, not authority. "
        + AUTONOMOUS_SEAT_REFERENCE
    )


def render_seat_subagent_development() -> str:
    """Compatibility renderer for the readiness consumer; delegation is optional."""
    return "Delegation is an owner-chosen capacity tool; " + AUTONOMOUS_SEAT_REFERENCE


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


def render_claude_function_harmonization() -> str:
    """Return the Claude-to-Codex function harmonization contract."""
    lines = ["Claude Function Harmonization:"]
    lines.extend(
        f"- {name}: {description}"
        for name, description in CLAUDE_FUNCTION_HARMONIZATION_RULES
    )
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
    lines.extend(
        (
            "- Optional unchanged-lane resume:",
            "  - env -u GIT_INDEX_FILE .venv/bin/python "
            f"{LEDGER_CLI_BRIDGE['guard_resume_command']}",
            "- Resume rules:",
        )
    )
    lines.extend(f"  - {rule}" for rule in LEDGER_CLI_BRIDGE["guard_resume_rules"])
    return "\n".join(lines)


AUTOMATIC_TASK_ROUTING_RULES = (
    *_AUTOMATIC_TASK_ROUTING_BASE_RULES,
    "After one exact trigger is sent, monitor with wait_threads and preserve its per-target cursor; a normal timeout continues wait_threads with that same cursor.",
    "Only when wait_threads reports a missing or unavailable wait handler, read exactly one bounded snapshot of the same task with read_thread(turnLimit=1, includeOutputs=false).",
    "After that one snapshot, reconcile progress at bounded cadence from immutable Git and mailbox artifacts; do not repeat thread snapshots.",
    "If both that one snapshot and immutable artifact reconciliation are unavailable or ambiguous, preserve the dispatch identity, perform at most one normal discovery/deduplication refresh, and report one concrete tooling blocker.",
    "Monitoring failure never resends the trigger, creates a replacement task, changes seats, or asks the user to relay the trigger; leave an approval or user-input request for the user.",
    "A concrete live-seat Codex task may exercise only its committed authority; parent-scoped subagents do not publish live-seat events or formal GO, and task routing grants no external-effect authority.",
)
FIXED_WRITER_LAUNCH_REFERENCE = (
    "Codex Fixed-Writer Launch: scripts/codex_protocol_model.py"
)
FIXED_WRITER_LAUNCH_RULES = (
    "Publication authority must already name the exact sender, recipient, kind, target, and scope before Codex launches a writer.",
    "In the known managed Pipeline checkout where the default sandbox cannot open the Git-common-dir writer fence, launch the exact coordination/bin/send-event command with the supported scoped execution profile on the first attempt.",
    "Limit any reusable approval prefix to coordination/bin/send-event plus the concrete sender seat; never grant a generic shell, Python, Git, or filesystem prefix.",
    "If that writer attempt fails, report the exact path, syscall, and error; do not direct-edit the mailbox, use an alternate writer, inject TMPDIR, or weaken the sandbox or fence.",
    "Outside that known context, use ordinary execution and never infer scoped-profile authority from repository prose.",
)


def render_fixed_writer_launch() -> str:
    """Return the Codex fixed-writer launch contract."""
    return FIXED_WRITER_LAUNCH_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in FIXED_WRITER_LAUNCH_RULES
    )


LEDGER_CLI_BRIDGE["guard_resume_command"] = (
    "scripts/ledger_start_guard.py --seat <seat> --wave 2 "
    "--resume-from <route-path>@<full-commit>"
)
LEDGER_CLI_BRIDGE["guard_resume_rules"] = (
    "Only a named seat or coordinator continuing an unchanged already-routed local implementation or review may use fast resume with the exact current route ref.",
    "Fresh, transplanted, ambiguous, or external-effect work uses ordinary fresh orientation.",
    "FULL ORIENTATION REQUIRED is an advisory fallback to the ordinary startup path, not BLOCKED.",
    "Fast resume grants no external-effect authority.",
)


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
    env = {
        name: value
        for name, value in (environ or {}).items()
        if name.startswith("CODEX_") or name == "GIT_INDEX_FILE"
    }
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
            "- env does not authorize push, merge, lock-claim side effects, paid API spend, or pod spend; these side effects are separately gated and user consent still gates them.",
            "- CODEX_SIDE_EFFECT_POLICY is always user-consent-required for separately gated push, merge, lock-claim side effects, paid API spend, and pod spend.",
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
        "side effects: push, merge, lock, paid API spend, and pod spend are separately gated and require user consent",
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


LANE_V_V3_RULES = (
    COMPACT_PAIR_INVARIANT,
    "mailbox decisions remain body-first: read relevant mailbox bodies before acting; live seat cursors are intentional per-seat state, and the coordinator has no cursor",
    "the verifying operator must be the assigned non-author and alone issues GO/NITS/FAIL from repository evidence; model or provider identity grants no authority",
    "the fixed mailbox writer publishes ordinary events and Operator verification reports through the same finalizer",
    "the coordinator may route and reconcile but not author behavior-changing production fixes",
    "push, merge, paid spend, and every other side effect are separately gated and require explicit authority",
    "no third same-question generic reviewer runs over an unchanged commit; only a different pre-stated specialist question is eligible under R-VERIFY-TIER",
)


def render_lane_v_v3() -> str:
    """Return the provider-neutral Lane V v3 verification contract."""
    lines = ["Provider-neutral Lane V v3:"]
    lines.extend(f"- {rule}" for rule in LANE_V_V3_RULES)
    return "\n".join(lines)


def render_surface_summary() -> str:
    """Return a compact Markdown summary of surfaces and invariants."""
    demoted_names = (
        name
        for name, _ in DEMOTED_RUNTIME_CONCEPTS
        if name != "Rotating Planning Relay"
    )
    lines = [
        render_autonomous_seat_contract(),
        render_automatic_task_routing(),
        render_fixed_writer_launch(),
        f"source: {MODEL_SOURCE}",
        f"central invariant: {CENTRAL_INVARIANT}",
        "durable artifacts: " + ", ".join(DURABLE_STATE_ARTIFACTS),
        "core agent modules: " + ", ".join(CORE_AGENT_MODULES),
        "coordinator invariants: " + "; ".join(COORDINATOR_INVARIANTS),
        "Active kernel invariants: "
        + ", ".join(name for name, _ in ACTIVE_KERNEL_INVARIANTS),
        "Demoted optional concepts: " + ", ".join(demoted_names),
        "Compact Pair Invariant: assigned non-author Operator, committed verify-request, fixed mailbox writer",
        "Codex Risk-Tier Router: conversational and read-only work avoid implementation ceremony",
        "R-INDEPENDENCE: adversarial-surface owners assess abuse classes and use proportional actual-diff review",
        "Ledger CLI Bridge: Pipeline kernel -> evidence-ledger target via "
        + LEDGER_CLI_BRIDGE["doc_path"],
        "agent extension namespace: .codex/agents/agentNN.toml guardrail extensions",
        "runtime env contract: "
        + ", ".join(name for name, _, _ in RUNTIME_ENV_VARIABLES),
        "Codex surfaces:",
    ]
    lines.extend(f"- {path}: {purpose}" for path, purpose in CODEX_SURFACES)
    return "\n".join(lines)

_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class OutcomeContract:
    task_id: str
    contract_ref: str
    parent_ref: str | None
    revision: int
    outcome: str
    owners: tuple[str, ...]
    evidence_bar: tuple[str, ...]
    hard_boundaries: tuple[str, ...]
    finding_refs: tuple[str, ...]
    external_effect: str | None = None


@dataclass(frozen=True)
class OwnershipChange:
    task_id: str
    parent_contract_ref: str
    revision: int
    previous_owners: tuple[str, ...]
    new_owners: tuple[str, ...]
    proposal: protocol_mailbox.OwnershipProposalStatement | None
    acceptances: tuple[protocol_mailbox.OwnershipAcceptanceStatement, ...]
    finding_refs: tuple[str, ...]
    outcome: str | None = None
    abandoned_takeover: bool = False
    takeover_evidence: protocol_mailbox.TakeoverEvidenceStatement | None = None
    takeover_confirmations: tuple[
        protocol_mailbox.TakeoverConfirmationStatement, ...
    ] = ()


@dataclass(frozen=True)
class ReviewDecision:
    task_id: str
    author_seat: str
    author_model: str
    reviewer_seat: str
    reviewer_model: str
    reviewed_base: str
    reviewed_head: str
    verdict: str
    finding_refs: tuple[str, ...]
    finding_dispositions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ExternalEffectToken:
    effect: str
    executor: str
    target: str
    scope: tuple[str, ...]


@dataclass(frozen=True)
class ExternalEffectTokenResult:
    complete: bool
    issues: tuple[str, ...]
    explicit_external_user_authorization_required: bool = True
    execution_authorized: bool = False


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_unique_refs(values: tuple[str, ...]) -> bool:
    return (
        isinstance(values, tuple)
        and len(values) == len(set(values))
        and all(
            protocol_mailbox.immutable_reference_is_canonical(value) for value in values
        )
    )


def _canonical_seats(values: tuple[str, ...]) -> bool:
    return (
        isinstance(values, tuple)
        and bool(values)
        and len(values) == len(set(values))
        and all(value in protocol_mailbox.RECEIVING_SEATS for value in values)
    )


def _nonblank_tuple(values: tuple[str, ...]) -> bool:
    return (
        isinstance(values, tuple)
        and bool(values)
        and all(_nonblank(value) for value in values)
    )


def claim_outcome(
    *,
    task_id: str,
    contract_ref: str,
    parent_ref: str | None,
    revision: int,
    outcome: str,
    owners: tuple[str, ...],
    evidence_bar: tuple[str, ...],
    hard_boundaries: tuple[str, ...],
    finding_refs: tuple[str, ...],
    external_effect: str | None = None,
) -> OutcomeContract:
    """Create a validated immutable outcome contract or reject its shape."""

    if not _nonblank(task_id) or not protocol_mailbox.immutable_reference_is_canonical(
        contract_ref
    ):
        raise ValueError("outcome contract requires a task and immutable contract ref")
    if parent_ref is not None and not protocol_mailbox.immutable_reference_is_canonical(parent_ref):
        raise ValueError("parent ref must be immutable when present")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise ValueError("revision must be a nonnegative integer")
    if not _nonblank(outcome) or not _canonical_seats(owners):
        raise ValueError("outcome and known unique owners are required")
    if not _nonblank_tuple(evidence_bar) or not _nonblank_tuple(hard_boundaries):
        raise ValueError("evidence bar and hard boundaries must be nonblank")
    if not _canonical_unique_refs(finding_refs):
        raise ValueError("finding refs must be canonical, unique, and ordered")
    if external_effect is not None and not _nonblank(external_effect):
        raise ValueError("external effect must be nonblank when present")
    return OutcomeContract(
        task_id=task_id.strip(),
        contract_ref=contract_ref,
        parent_ref=parent_ref,
        revision=revision,
        outcome=outcome.strip(),
        owners=owners,
        evidence_bar=evidence_bar,
        hard_boundaries=hard_boundaries,
        finding_refs=finding_refs,
        external_effect=external_effect.strip() if external_effect is not None else None,
    )


def _change_envelope_matches(contract: OutcomeContract, change: OwnershipChange) -> bool:
    return (
        change.task_id == contract.task_id
        and change.parent_contract_ref == contract.contract_ref
        and change.revision == contract.revision + 1
        and change.previous_owners == contract.owners
        and _canonical_seats(change.new_owners)
        and change.new_owners != contract.owners
        and change.finding_refs == contract.finding_refs
        and _canonical_unique_refs(change.finding_refs)
        and (change.outcome is None or _nonblank(change.outcome))
    )


def _normal_ownership_change_is_effective(
    contract: OutcomeContract,
    change: OwnershipChange,
    root: os.PathLike[str] | str,
) -> bool:
    proposal = change.proposal
    if (
        proposal is None
        or change.takeover_evidence is not None
        or change.takeover_confirmations
    ):
        return False
    try:
        committed_proposal = protocol_mailbox.load_ownership_proposal_statement(
            root, proposal.event.ref
        )
    except (OSError, ValueError):
        return False
    if committed_proposal != proposal:
        return False
    expected_outcome = change.outcome or contract.outcome
    if not (
        proposal.event.sender in contract.owners
        and proposal.task_id == contract.task_id
        and proposal.parent_ref == contract.contract_ref
        and proposal.revision == change.revision
        and proposal.previous_owners == contract.owners
        and proposal.proposed_owners == change.new_owners
        and proposal.outcome == expected_outcome
        and proposal.finding_refs == contract.finding_refs
    ):
        return False

    required_acceptors = set(change.new_owners)
    if {acceptance.event.sender for acceptance in change.acceptances} != required_acceptors:
        return False
    if len(change.acceptances) != len(required_acceptors):
        return False
    for acceptance in change.acceptances:
        try:
            committed_acceptance = (
                protocol_mailbox.load_ownership_acceptance_statement(
                    root, acceptance.event.ref
                )
            )
        except (OSError, ValueError):
            return False
        if committed_acceptance != acceptance:
            return False
        if not (
            acceptance.event.sender in required_acceptors
            and acceptance.task_id == contract.task_id
            and acceptance.parent_ref == contract.contract_ref
            and acceptance.revision == change.revision
            and acceptance.previous_owners == contract.owners
            and acceptance.proposed_owners == change.new_owners
            and acceptance.proposal_ref == proposal.event.ref
            and acceptance.outcome == expected_outcome
            and acceptance.finding_refs == contract.finding_refs
        ):
            return False
    return True


def _abandoned_takeover_is_effective(
    contract: OutcomeContract,
    change: OwnershipChange,
    root: os.PathLike[str] | str,
) -> bool:
    """Require a body-bound claim plus one distinct pair-seat corroboration."""

    evidence = change.takeover_evidence
    if (
        change.proposal is not None
        or change.acceptances
        or evidence is None
        or len(change.new_owners) != 1
        or change.new_owners[0] in contract.owners
        or change.outcome is not None
        or len(change.takeover_confirmations) != 1
    ):
        return False
    confirmation = change.takeover_confirmations[0]
    try:
        committed_evidence = protocol_mailbox.load_takeover_evidence_statement(
            root, evidence.event.ref
        )
        committed_confirmation = (
            protocol_mailbox.load_takeover_confirmation_statement(
                root, confirmation.event.ref
            )
        )
    except (OSError, ValueError):
        return False
    if committed_evidence != evidence or committed_confirmation != confirmation:
        return False

    claimant = change.new_owners[0]
    corroborator = confirmation.event.sender
    return bool(
        evidence.event.sender == claimant
        and evidence.task_id == contract.task_id
        and evidence.parent_ref == contract.contract_ref
        and evidence.revision == change.revision
        and evidence.finding_refs == contract.finding_refs
        and evidence.fresh_work_state.casefold() == "no fresh work"
        and evidence.lock_state.casefold() == "no active lock"
        and corroborator in SEATS
        and corroborator != claimant
        and confirmation.event.recipient == claimant
        and confirmation.task_id == contract.task_id
        and confirmation.parent_ref == contract.contract_ref
        and confirmation.revision == change.revision
        and confirmation.proposed_owner == claimant
        and confirmation.takeover_claim_ref == evidence.event.ref
        and confirmation.observed_at == evidence.observed_at
        and confirmation.finding_refs == contract.finding_refs
        and protocol_mailbox.committed_event_is_strict_ancestor(
            root, evidence.event, confirmation.event
        )
        and confirmation.event.when >= evidence.event.when
        and confirmation.event.when >= evidence.observed_at
    )


def ownership_change_is_effective(
    contract: OutcomeContract,
    change: OwnershipChange,
    *,
    root: os.PathLike[str] | str = protocol_mailbox.ROOT,
) -> bool:
    """Require exact lineage and body-bound consent for an ownership successor."""

    if not _change_envelope_matches(contract, change):
        return False
    if change.abandoned_takeover:
        return _abandoned_takeover_is_effective(contract, change, root)
    return _normal_ownership_change_is_effective(contract, change, root)


def apply_ownership_change(
    contract: OutcomeContract,
    change: OwnershipChange,
    *,
    root: os.PathLike[str] | str = protocol_mailbox.ROOT,
) -> OutcomeContract:
    if not ownership_change_is_effective(contract, change, root=root):
        raise ValueError("ownership change is not effective")
    if change.abandoned_takeover:
        assert change.takeover_evidence is not None
        successor_ref = change.takeover_evidence.event.ref
    else:
        assert change.proposal is not None
        successor_ref = change.proposal.event.ref
    return replace(
        contract,
        contract_ref=successor_ref,
        parent_ref=contract.contract_ref,
        revision=change.revision,
        outcome=change.outcome or contract.outcome,
        owners=change.new_owners,
    )


def finding_state(*, hard_boundary_unresolved: bool) -> str:
    """Keep ordinary findings advisory while hard-boundary violations block."""

    return "BLOCKED" if hard_boundary_unresolved else "FINDING"


def review_accepts_outcome(contract: OutcomeContract, decision: ReviewDecision) -> bool:
    """Return whether exact-range non-author Operator GO accepts the outcome."""

    if not (
        decision.task_id == contract.task_id
        and decision.author_seat in contract.owners
        and decision.author_seat in SEATS
        and decision.reviewer_seat in OPERATOR_SEATS
        and decision.author_seat != decision.reviewer_seat
        and _nonblank(decision.author_model)
        and _nonblank(decision.reviewer_model)
        and decision.author_model.strip().casefold()
        != decision.reviewer_model.strip().casefold()
        and isinstance(decision.reviewed_base, str)
        and isinstance(decision.reviewed_head, str)
        and _FULL_SHA_RE.fullmatch(decision.reviewed_base)
        and _FULL_SHA_RE.fullmatch(decision.reviewed_head)
        and decision.reviewed_base != decision.reviewed_head
        and decision.verdict == "GO"
        and decision.finding_refs == contract.finding_refs
        and _canonical_unique_refs(decision.finding_refs)
    ):
        return False
    if not isinstance(decision.finding_dispositions, tuple) or not all(
        isinstance(entry, tuple)
        and len(entry) == 2
        and isinstance(entry[0], str)
        and isinstance(entry[1], str)
        for entry in decision.finding_dispositions
    ):
        return False
    if len(decision.finding_dispositions) != len(contract.finding_refs):
        return False
    return (
        tuple(ref for ref, _ in decision.finding_dispositions) == contract.finding_refs
        and all(
            _nonblank(disposition) for _, disposition in decision.finding_dispositions
        )
    )


def external_effect_token_is_complete(
    token: ExternalEffectToken,
) -> ExternalEffectTokenResult:
    """Validate descriptive shape without ever granting execution authority."""

    issues = []
    if not _nonblank(token.effect):
        issues.append("effect")
    if token.executor not in protocol_mailbox.RECEIVING_SEATS:
        issues.append("executor")
    if not _nonblank(token.target) or token.target.strip() in {"*", "all"}:
        issues.append("target")
    if not isinstance(token.scope, tuple) or not token.scope or any(
        not _nonblank(item) or item.strip() == "*" for item in token.scope
    ):
        issues.append("scope")
    elif len(token.scope) != len(set(token.scope)):
        issues.append("scope")
    return ExternalEffectTokenResult(complete=not issues, issues=tuple(issues))


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
    print("## Autonomous Seat Outcome Contract")
    print(render_autonomous_seat_contract())
    print()
    print("## Provider-neutral Lane V v3")
    print(render_lane_v_v3())
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
