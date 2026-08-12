#!/usr/bin/env python3
"""Read-only hard-gated capacity scheduler for the four-seat protocol."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Any

try:
    from scripts import codex_protocol_model as model
    from scripts import ledger_start_guard
    from scripts import route_lineage
except ImportError:  # direct script execution
    import codex_protocol_model as model
    import ledger_start_guard
    import route_lineage

if __package__:
    from scripts import protocol_mailbox  # noqa: E402
else:
    import protocol_mailbox  # noqa: E402

# SEAT_ORDER = the standing capacity ACTORS the coverage gate (G1, :504) and WIP gate
# (G2, :521) require to own exactly one packet per active cycle. coordinator is a
# standing actor; coordinator2 is NOT — it is an on-demand oversight seat (Slice 2.5
# Option B: coordinator2 is an accepted-but-optional owner, decoupling "valid owner"
# from "mandatory coverage actor"). Coordinator-first ordering is load-bearing for the
# owner-iteration at :166/:504/:521. Root-derived (D1) for the 4 pair seats.
SEAT_ORDER = ("coordinator", *protocol_mailbox.SEATS)
PAIR_B_SEATS = ("director2", "operator2")
# VALID_OWNERS = the acceptance whitelist for a packet's owner / next_recipient
# (:381/:393). It DOES include coordinator2 and equals the protocol_mailbox root, so a
# coordinator2-owned or -addressed packet is accepted WITHOUT being forced into the
# per-cycle coverage requirement.
VALID_OWNERS = protocol_mailbox.RECEIVING_SEATS
PACKET_TYPES = {
    "director-implementation",
    "director-brief",
    "director-cosign",
    "director-preflight",
    "operator-verification",
    "operator-doc-sync",
    "operator-preflight",
    "coordinator-route",
    "coordinator-reconcile",
    "coordinator-join",
    "receipt-only",
    "idle",
    "blocked",
}
STATUSES = {"ready", "active", "blocked", "done", "excepted"}
ACTIVE_STATUSES = {"ready", "active"}
CURRENT_STATUSES = {"ready", "active", "blocked"}
HANDOFF_ARTIFACT_RE = re.compile(
    r"^(?:handoff(?: artifact)?\s*:\s*)?`?(docs/HANDOFF-[^/\s`]+\.md)`?$",
    re.IGNORECASE,
)
HANDOFF_REQUIRED_RE = re.compile(
    r"\b("
    r"standby|idle|no routed next work|no current work|no new [a-z -]*task|"
    r"context switch|transplant|state-transfer|state transfer|handoff|"
    r"closeout|closed cycle|cycle complete"
    r")\b",
    re.IGNORECASE,
)
_MARKDOWN_HEADING_RE = re.compile(r"(?m)^#{1,6}\s+\S")
SIDE_EFFECT_TOKEN_HEADING_RE = re.compile(
    r"(?im)^(?:#{1,6}\s*)?Side-Effect Executor Token\s*:?\s*$"
)
_DUPLICATE_TOKEN_FIELDS_KEY = "__duplicate_fields__"
SIDE_EFFECT_TOKEN_FIELD_ALIASES = {
    "effect": "effect",
    "effect kind": "effect",
    "side_effect_id": "side_effect_id",
    "side effect id": "side_effect_id",
    "executor": "executor",
    "executor seat": "executor",
    "target": "target",
    "target repo": "target",
    "target resource": "target",
    "scope": "scope",
    "bounded scope": "scope",
    "allowed_command_class": "allowed_command_class",
    "allowed command class": "allowed_command_class",
    "allowed command": "allowed_command_class",
    "preflight": "preflight",
    "stop_if_newer_mail_or_live_target_satisfied": "stop_if_newer_mail_or_live_target_satisfied",
    "stop if newer mail or live target satisfied": "stop_if_newer_mail_or_live_target_satisfied",
    "stop-if-newer-mail-or-live-target-satisfied": "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck": "postcheck",
    "post check": "postcheck",
    "observer_seats": "observer_seats",
    "observer seats": "observer_seats",
    "final_closeout_owner": "final_closeout_owner",
    "final closeout owner": "final_closeout_owner",
    "non_goals": "non_goals",
    "non goals": "non_goals",
    "non-goals": "non_goals",
}
REQUIRED_SIDE_EFFECT_TOKEN_FIELDS = (
    "effect",
    "executor",
    "target",
    "scope",
)
LEGACY_SIDE_EFFECT_TOKEN_FIELDS = (
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
SHARED_SIDE_EFFECT_PATTERNS = {
    "remote-ref update/push": r"\bremote-ref update\b|\bgit push\b|\bpush(?:es)?\b",
    "force update": r"\bforce update\b|\bforce-push\b|\bforce push\b",
    "lock action": r"\block action\b|\block claim\b|\block-claim\b|\bclaims? locks?\b|\block release\b|\block-release\b|\brelease locks?\b",
    "paid-service spend": r"\bpaid-service spend\b|\bpaid api spend\b|\bpaid-api spend\b|\bpaid service\b",
    "pod action": r"\bpod action\b|\bpod spend\b|\bstart pods?\b|\bstart a pod\b",
    "production generation": r"\bproduction generation\b",
    "target-repo checkout refresh": r"\btarget-repo checkout refresh\b|\bcheckout refresh\b|\bgit fetch\b|\bgit pull\b",
    "cursor consume": r"\bcursor consume\b|\bconsume-events?\b",
}
SIDE_EFFECT_DIRECTIVE_RE = re.compile(
    r"\b(authorizes?|authorized|allows?|grants?|executes?|execute|runs?|run|"
    r"performs?|perform|mutates?|mutate|may|can|will|shall|should|must|"
    r"push(?:es)?|claim(?:s|ing)?)\b",
    re.IGNORECASE,
)
SIDE_EFFECT_SUCCESS_RE = re.compile(r"\bside-effect success claim\s*:\s*(?P<body>.+)$", re.IGNORECASE)


@dataclass(frozen=True)
class Packet:
    id: str
    wave: int
    cycle: str
    owner: str
    packet_type: str
    row_ids: tuple[str, ...]
    allowed_paths: tuple[str, ...]
    lock_keys: tuple[str, ...]
    dependencies: tuple[str, ...]
    acceptance: tuple[str, ...]
    done_evidence: tuple[str, ...]
    handoff_artifact: str | None
    next_recipient: str | None
    status: str
    verify_request: str | None
    target_commit: str | None
    commit_range: str | None
    scope_files: tuple[str, ...]
    path: str

    @property
    def is_active_wip(self) -> bool:
        return self.status in ACTIVE_STATUSES

    @property
    def is_current(self) -> bool:
        return self.status in CURRENT_STATUSES

    @property
    def is_implementation(self) -> bool:
        return "implementation" in self.packet_type

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "wave": self.wave,
            "cycle": self.cycle,
            "owner": self.owner,
            "packet_type": self.packet_type,
            "row_ids": list(self.row_ids),
            "allowed_paths": list(self.allowed_paths),
            "lock_keys": list(self.lock_keys),
            "dependencies": list(self.dependencies),
            "acceptance": list(self.acceptance),
            "done_evidence": list(self.done_evidence),
            "handoff_artifact": self.handoff_artifact,
            "next_recipient": self.next_recipient,
            "status": self.status,
            "verify_request": self.verify_request,
            "target_commit": self.target_commit,
            "commit_range": self.commit_range,
            "scope_files": list(self.scope_files),
            "path": self.path,
        }


@dataclass(frozen=True)
class ProtocolException:
    id: str
    created_at: str
    approving_actor: str
    bypassed_gate: str
    reason: str
    scope: dict[str, tuple[str, ...]]
    expiry: dict[str, Any]
    convergence_condition: str
    status: str
    path: str

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "approving_actor": self.approving_actor,
            "bypassed_gate": self.bypassed_gate,
            "reason": self.reason,
            "scope": {key: list(value) for key, value in self.scope.items()},
            "expiry": self.expiry,
            "convergence_condition": self.convergence_condition,
            "status": self.status,
            "path": self.path,
        }


@dataclass(frozen=True)
class CapacityReport:
    root: str
    wave: int
    packets: tuple[Packet, ...]
    exceptions: tuple[ProtocolException, ...]
    issues: tuple[dict[str, Any], ...]

    @property
    def blocking_issues(self) -> list[dict[str, Any]]:
        return [issue for issue in self.issues if not issue.get("excepted_by")]

    @property
    def packet_state(self) -> str:
        if not self.packets:
            return "inactive-no-packets"
        if any(packet.is_active_wip for packet in self.packets):
            return "active"
        if any(packet.status == "blocked" for packet in self.packets):
            return "blocked"
        return "closed"

    @property
    def actor_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        active_cycles = {
            packet.cycle for packet in self.packets if packet.is_active_wip
        }
        for owner in SEAT_ORDER:
            current = _selected_actor_packets(list(self.packets), active_cycles, owner)
            rows.append(
                {
                    "owner": owner,
                    "packet_ids": [packet.id for packet in current],
                    "statuses": [packet.status for packet in current],
                    "packet_types": [packet.packet_type for packet in current],
                }
            )
        return rows

    @property
    def actor_actions(self) -> list[dict[str, Any]]:
        active_cycles = {
            packet.cycle for packet in self.packets if packet.is_active_wip
        }
        rows: list[dict[str, Any]] = []
        for owner in SEAT_ORDER:
            packets = _selected_actor_packets(list(self.packets), active_cycles, owner)
            packet = packets[0] if packets else None
            rows.append(_actor_action(owner, packet))
        return rows

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_kind": "protocol-capacity-board",
            "root": self.root,
            "wave": self.wave,
            "packet_state": self.packet_state,
            "packets": [packet.to_dict() for packet in self.packets],
            "exceptions": [exception.to_dict() for exception in self.exceptions],
            "actor_rows": self.actor_rows,
            "actor_actions": self.actor_actions,
            "issues": list(self.issues),
            "blocking_issues": self.blocking_issues,
            "valid": not self.blocking_issues,
        }


@dataclass(frozen=True)
class RouteValidation:
    route_path: str
    report: CapacityReport
    route_issues: tuple[dict[str, Any], ...]
    token_results: tuple[model.ExternalEffectTokenResult, ...]

    @property
    def blocking_issues(self) -> list[dict[str, Any]]:
        return list(self.route_issues)

    @property
    def advisories(self) -> list[dict[str, Any]]:
        return list(self.report.blocking_issues)

    @property
    def valid(self) -> bool:
        return not self.blocking_issues

    @property
    def explicit_external_user_authorization_required(self) -> bool:
        return True

    @property
    def execution_authorized(self) -> bool:
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_kind": "protocol-capacity-route-validation",
            "route_path": self.route_path,
            "valid": self.valid,
            "route_issues": list(self.route_issues),
            "blocking_issues": self.blocking_issues,
            "advisories": self.advisories,
            "structural_token_results": [
                {
                    "complete": result.complete,
                    "issues": list(result.issues),
                    "explicit_external_user_authorization_required": (
                        result.explicit_external_user_authorization_required
                    ),
                    "execution_authorized": result.execution_authorized,
                }
                for result in self.token_results
            ],
            "explicit_external_user_authorization_required": (
                self.explicit_external_user_authorization_required
            ),
            "execution_authorized": self.execution_authorized,
            "board": self.report.to_dict(),
        }


def collect_capacity_report(root: Path | str, wave: int) -> CapacityReport:
    root_path = Path(root)
    packet_issues: list[dict[str, Any]] = []
    exception_issues: list[dict[str, Any]] = []
    packets = _load_packets(root_path, wave, packet_issues)
    exceptions = _load_exceptions(root_path, exception_issues)
    issues = [*packet_issues, *exception_issues, *_validate_packets(packets, root_path)]
    issues = _apply_exceptions(issues, exceptions)
    return CapacityReport(
        root=str(root_path),
        wave=wave,
        packets=tuple(packets),
        exceptions=tuple(exceptions),
        issues=tuple(issues),
    )


def validate_route(root: Path | str, wave: int, route_path: Path | str) -> RouteValidation:
    report = collect_capacity_report(root, wave)
    path = Path(route_path)
    route_issues = _validate_route_file(path, report)
    route_issues = _apply_exceptions(route_issues, list(report.exceptions))
    blocking_route_issues = [
        issue for issue in route_issues if not issue.get("excepted_by")
    ]
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        token_results: tuple[model.ExternalEffectTokenResult, ...] = ()
    else:
        token_results = structural_external_effect_token_results(body)
    return RouteValidation(
        route_path=str(path),
        report=report,
        route_issues=tuple(blocking_route_issues),
        token_results=token_results,
    )


def require_packets(report: CapacityReport) -> CapacityReport:
    if report.packets:
        return report
    return CapacityReport(
        root=report.root,
        wave=report.wave,
        packets=report.packets,
        exceptions=report.exceptions,
        issues=(
            *report.issues,
            _issue("G9", f"no capacity packets for wave {report.wave}"),
        ),
    )


def render_capacity_board(report: CapacityReport) -> str:
    lines = [
        "# Protocol Capacity Board",
        f"wave: {report.wave}",
        f"valid: {str(not report.blocking_issues).lower()}",
        f"packet state: {report.packet_state}",
        "",
        "ACTORS",
    ]
    for row in report.actor_rows:
        packet_ids = ", ".join(row["packet_ids"]) if row["packet_ids"] else "-"
        statuses = ", ".join(row["statuses"]) if row["statuses"] else "-"
        lines.append(f"{row['owner']:<11} packets={packet_ids} status={statuses}")

    lines.extend(["", "NEXT LAWFUL ACTIONS"])
    for row in report.actor_actions:
        lines.extend(
            [
                row["owner"],
                f"  orientation: {row['orientation']}",
                f"  packet: {row['packet']}",
                f"  deps: {row['dependencies']}",
                f"  next: {row['next_action']}",
                f"  stop: {row['stop_condition']}",
            ]
        )

    lines.append("")
    if report.blocking_issues:
        lines.append("BLOCKING ISSUES")
        for issue in report.blocking_issues:
            lines.append(f"- {issue['gate']}: {issue['message']}")
    else:
        lines.append("BLOCKING ISSUES")
        lines.append("- none")

    excepted = [issue for issue in report.issues if issue.get("excepted_by")]
    if excepted:
        lines.append("")
        lines.append("EXCEPTED ISSUES")
        for issue in excepted:
            lines.append(f"- {issue['gate']}: {issue['message']} ({issue['excepted_by']})")
    return "\n".join(lines) + "\n"


def render_route_validation(result: RouteValidation) -> str:
    lines = [
        "# Protocol Capacity Route Validation",
        f"route: {result.route_path}",
        f"route valid: {str(result.valid).lower()}",
        "",
    ]
    if result.blocking_issues:
        lines.append("BLOCKING ISSUES")
        for issue in result.blocking_issues:
            lines.append(f"- {issue['gate']}: {issue['message']}")
    else:
        lines.append("BLOCKING ISSUES")
        lines.append("- none")
    lines.extend(["", "ADVISORIES"])
    if result.advisories:
        for issue in result.advisories:
            lines.append(f"- {issue['gate']}: {issue['message']}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _load_packets(root: Path, wave: int, issues: list[dict[str, Any]]) -> list[Packet]:
    packet_dir = root / "coordination/capacity/packets"
    packets: list[Packet] = []
    if not packet_dir.is_dir():
        return packets
    for path in sorted(packet_dir.glob("*.json")):
        data = _read_json(path, issues)
        if data is None:
            continue
        packet = _parse_packet(path, data, issues)
        if packet and packet.wave == wave:
            packets.append(packet)
    return packets


def _load_exceptions(root: Path, issues: list[dict[str, Any]]) -> list[ProtocolException]:
    exception_dir = root / "coordination/protocol-exceptions"
    exceptions: list[ProtocolException] = []
    if not exception_dir.is_dir():
        return exceptions
    for path in sorted(exception_dir.glob("*.json")):
        data = _read_json(path, issues)
        if data is None:
            continue
        exception = _parse_exception(path, data, issues)
        if exception:
            exceptions.append(exception)
    return exceptions


def _read_json(path: Path, issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(_issue("SCHEMA", f"{path.name}: unreadable JSON ({exc})"))
        return None
    if not isinstance(data, dict):
        issues.append(_issue("SCHEMA", f"{path.name}: top-level JSON is not an object"))
        return None
    return data


def _parse_packet(
    path: Path,
    data: dict[str, Any],
    issues: list[dict[str, Any]],
) -> Packet | None:
    required = {
        "id",
        "wave",
        "cycle",
        "owner",
        "packet_type",
        "row_ids",
        "allowed_paths",
        "lock_keys",
        "dependencies",
        "acceptance",
        "done_evidence",
        "status",
    }
    missing = sorted(required - data.keys())
    local_issues: list[str] = []
    if missing:
        local_issues.append("missing required fields: " + ", ".join(missing))
    if data.get("owner") not in VALID_OWNERS:
        local_issues.append(f"invalid owner {data.get('owner')!r}")
    if data.get("packet_type") not in PACKET_TYPES:
        local_issues.append(f"invalid packet_type {data.get('packet_type')!r}")
    if data.get("status") not in STATUSES:
        local_issues.append(f"invalid status {data.get('status')!r}")
    if not isinstance(data.get("wave"), int):
        local_issues.append("wave must be an integer")
    for field in ("row_ids", "allowed_paths", "lock_keys", "dependencies", "acceptance", "done_evidence"):
        if not _is_str_list(data.get(field)):
            local_issues.append(f"{field} must be a list of strings")
    next_recipient = data.get("next_recipient")
    if next_recipient is not None and next_recipient not in VALID_OWNERS:
        local_issues.append(f"invalid next_recipient {next_recipient!r}")
    if "scope_files" in data and not _is_str_list(data.get("scope_files")):
        local_issues.append("scope_files must be a list of strings")
    handoff_artifact = data.get("handoff_artifact")
    if handoff_artifact is not None and not isinstance(handoff_artifact, str):
        local_issues.append("handoff_artifact must be a string")
        handoff_artifact = None

    if local_issues:
        for message in local_issues:
            issues.append(_issue("SCHEMA", f"{path.name}: {message}"))
        return None

    return Packet(
        id=str(data["id"]),
        wave=int(data["wave"]),
        cycle=str(data["cycle"]),
        owner=str(data["owner"]),
        packet_type=str(data["packet_type"]),
        row_ids=tuple(data["row_ids"]),
        allowed_paths=tuple(data["allowed_paths"]),
        lock_keys=tuple(data["lock_keys"]),
        dependencies=tuple(data["dependencies"]),
        acceptance=tuple(data["acceptance"]),
        done_evidence=tuple(data["done_evidence"]),
        handoff_artifact=handoff_artifact,
        next_recipient=next_recipient,
        status=str(data["status"]),
        verify_request=_optional_str(data.get("verify_request")),
        target_commit=_optional_str(data.get("target_commit")),
        commit_range=_optional_str(data.get("commit_range")),
        scope_files=tuple(data.get("scope_files", [])),
        path=_display_path(path),
    )


def _parse_exception(
    path: Path,
    data: dict[str, Any],
    issues: list[dict[str, Any]],
) -> ProtocolException | None:
    required = {
        "id",
        "created_at",
        "approving_actor",
        "bypassed_gate",
        "reason",
        "scope",
        "expiry",
        "convergence_condition",
        "status",
    }
    missing = sorted(required - data.keys())
    local_issues: list[str] = []
    if missing:
        local_issues.append("missing required fields: " + ", ".join(missing))
    if data.get("status") not in {"active", "expired", "closed"}:
        local_issues.append(f"invalid status {data.get('status')!r}")
    if not isinstance(data.get("scope"), dict):
        local_issues.append("scope must be an object")
    if not isinstance(data.get("expiry"), dict):
        local_issues.append("expiry must be an object")

    scope: dict[str, tuple[str, ...]] = {}
    if isinstance(data.get("scope"), dict):
        for key in ("packet_ids", "row_ids", "paths"):
            value = data["scope"].get(key, [])
            if not _is_str_list(value):
                local_issues.append(f"scope.{key} must be a list of strings")
            else:
                scope[key] = tuple(value)

    if local_issues:
        for message in local_issues:
            issues.append(_issue("SCHEMA", f"{path.name}: {message}"))
        return None

    return ProtocolException(
        id=str(data["id"]),
        created_at=str(data["created_at"]),
        approving_actor=str(data["approving_actor"]),
        bypassed_gate=str(data["bypassed_gate"]),
        reason=str(data["reason"]),
        scope=scope,
        expiry=dict(data["expiry"]),
        convergence_condition=str(data["convergence_condition"]),
        status=str(data["status"]),
        path=_display_path(path),
    )


def _validate_packets(packets: list[Packet], root: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    issues.extend(_validate_coverage(packets))
    issues.extend(_validate_wip_limit(packets))
    issues.extend(_validate_pair_b_capacity_split_default(packets))
    issues.extend(_validate_path_and_lock_isolation(packets))
    issues.extend(_validate_dependencies(packets))
    issues.extend(_validate_director_done_boundary(packets))
    issues.extend(_validate_operator_verification_boundary(packets))
    issues.extend(_validate_join_gate(packets, root))
    return issues


def _validate_coverage(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    cycles = sorted({packet.cycle for packet in packets if packet.is_active_wip})
    for cycle in cycles:
        current = [packet for packet in packets if packet.cycle == cycle and packet.is_current]
        if not any(packet.is_active_wip for packet in current):
            continue
        for owner in SEAT_ORDER:
            owned = [
                packet
                for packet in packets
                if packet.cycle == cycle and packet.owner == owner and packet.is_current
            ]
            if not owned:
                owned = _fallback_done_packets(packets, {cycle}, owner)
            if len(owned) != 1:
                issues.append(
                    _issue(
                        "G1",
                        f"cycle {cycle}: {owner} has {len(owned)} current/done packets",
                        packet_ids=[packet.id for packet in owned],
                    )
                )
    return issues


def _fallback_done_packets(
    packets: list[Packet], cycles: set[str], owner: str
) -> list[Packet]:
    done = [
        packet
        for packet in packets
        if packet.owner == owner
        and packet.cycle in cycles
        and packet.status in {"done", "excepted"}
    ]
    non_idle = [packet for packet in done if packet.packet_type != "idle"]
    return non_idle or done


def _selected_actor_packets(
    packets: list[Packet], active_cycles: set[str], owner: str
) -> list[Packet]:
    current = [
        packet for packet in packets if packet.owner == owner and packet.is_current
    ]
    if not current and active_cycles:
        current = _fallback_done_packets(packets, active_cycles, owner)
    return current


def _actor_action(owner: str, packet: Packet | None) -> dict[str, Any]:
    orientation = f"python scripts/status.py snapshot {owner}"
    if packet is None:
        return {
            "owner": owner,
            "orientation": orientation,
            "packet": "-",
            "dependencies": "-",
            "next_action": "standby until a fresh coordinator route, lawful authority-bearing trigger, or user prompt assigns work",
            "stop_condition": "do not send receipt/status mail unless ownership, evidence, or blockers change",
        }

    dependencies = ", ".join(packet.dependencies) if packet.dependencies else "-"
    next_action, stop_condition = _packet_action_text(owner, packet)
    return {
        "owner": owner,
        "orientation": orientation,
        "packet": f"{packet.id} ({packet.packet_type}, {packet.status})",
        "dependencies": dependencies,
        "next_action": next_action,
        "stop_condition": stop_condition,
    }


def _packet_action_text(owner: str, packet: Packet) -> tuple[str, str]:
    if packet.status in {"done", "excepted"}:
        return (
            "no duplicate work; preserve evidence if contradicted by newer durable state",
            "standby unless new mail/user route changes ownership",
        )
    if packet.status == "blocked":
        return (
            "wait on named dependency or report the concrete blocker",
            _blocked_stop_condition(owner, packet),
        )
    if owner == "coordinator" or packet.packet_type.startswith("coordinator-"):
        return (
            "reconcile capacity/mailbox/gate state and internally continue an already-authorized Director→Operator chain",
            "return to the user only at completion, a genuine blocker, scope expansion, or a separately gated side effect; no production fix",
        )
    if packet.packet_type == "director-implementation":
        return (
            "implement the named scope inside allowed paths",
            "send one committed verify-request naming full reviewed base/head or range, outcome, author seat/model, assigned Operator, and immutable finding refs",
        )
    if packet.packet_type in {"director-brief", "director-cosign", "director-preflight"}:
        return (
            "prepare the bounded brief/co-sign/preflight artifact for the named recipient",
            "report bounded planning/preflight evidence to coordinator; no production fix or GO",
        )
    if packet.packet_type == "operator-verification":
        return (
            "verify only the assigned committed verify-request as a non-author; bind the exact request, range, and allowed paths",
            "send one directly publishable verification-report GO/NITS/FAIL through the fixed mailbox writer; no descriptor, shipping trigger, task publication state, or recovery path",
        )
    if packet.packet_type in {"operator-doc-sync", "operator-preflight"}:
        return (
            "run the bounded read-only sync/preflight checks for the packet scope",
            "report bounded preflight findings; do not duplicate Lane V or issue production GO",
        )
    if packet.packet_type == "idle":
        return (
            "standby only when the capacity split gate has no lawful preflight/planning work",
            "no receipt/status churn",
        )
    return (
        "execute the packet acceptance criteria inside the allowed scope",
        "preserve evidence and stop at the packet's named next recipient",
    )


def _blocked_stop_condition(owner: str, packet: Packet) -> str:
    if packet.packet_type in {"director-brief", "director-cosign", "director-preflight"}:
        return "report bounded planning/preflight evidence to coordinator; no production fix or GO"
    if packet.packet_type in {"operator-verification", "operator-doc-sync", "operator-preflight"}:
        return "wait for the assigned committed verify-request/dependency or report FAIL/NITS with evidence; never reconstruct missing fields"
    if owner == "coordinator":
        return "route blocker or no-op with the blocking boundary or plain next authority; no production fix"
    return "preserve blocker evidence and await the named dependency"


def _validate_wip_limit(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    cycles = sorted({packet.cycle for packet in packets})
    for cycle in cycles:
        for owner in SEAT_ORDER:
            active = [
                packet
                for packet in packets
                if packet.cycle == cycle and packet.owner == owner and packet.is_active_wip
            ]
            if len(active) > 1:
                issues.append(
                    _issue(
                        "G2",
                        f"cycle {cycle}: {owner} has {len(active)} ready/active packets",
                        packet_ids=[packet.id for packet in active],
                        row_ids=_merged(active, "row_ids"),
                        paths=_merged(active, "allowed_paths"),
                )
            )
    return issues


def _validate_pair_b_capacity_split_default(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for cycle in _active_cycles(packets):
        current = [
            packet for packet in packets if packet.cycle == cycle and packet.is_current
        ]
        idle_pair_b = [
            packet
            for packet in current
            if packet.owner in PAIR_B_SEATS and packet.packet_type == "idle"
        ]
        if idle_pair_b:
            issues.append(
                _issue(
                    "G10",
                    f"cycle {cycle}: Pair B must perform bounded planning or preflight instead of idle observer standby",
                    packet_ids=[packet.id for packet in idle_pair_b],
                    row_ids=_merged(idle_pair_b, "row_ids"),
                    paths=_merged(idle_pair_b, "allowed_paths"),
                )
            )
    return issues


def _validate_path_and_lock_isolation(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    active_impl = [
        packet for packet in packets if packet.is_active_wip and packet.is_implementation
    ]
    for idx, left in enumerate(active_impl):
        for right in active_impl[idx + 1 :]:
            if left.id == right.id:
                continue
            shared_path_pairs = _overlapping_path_pairs(
                left.allowed_paths,
                right.allowed_paths,
            )
            shared_paths = sorted(
                {path for pair in shared_path_pairs for path in pair}
            )
            shared_locks = sorted(set(left.lock_keys) & set(right.lock_keys))
            if not shared_paths and not shared_locks:
                continue
            detail = []
            if shared_path_pairs:
                detail.append(
                    "paths="
                    + ", ".join(
                        f"{left_path} <-> {right_path}"
                        for left_path, right_path in shared_path_pairs
                    )
                )
            if shared_locks:
                detail.append("locks=" + ", ".join(shared_locks))
            issues.append(
                _issue(
                    "G3",
                    f"{left.id} and {right.id} overlap " + "; ".join(detail),
                    packet_ids=[left.id, right.id],
                    row_ids=sorted(set(left.row_ids) | set(right.row_ids)),
                    paths=shared_paths,
                    lock_keys=shared_locks,
                )
            )
    return issues


def _overlapping_path_pairs(
    left_paths: tuple[str, ...],
    right_paths: tuple[str, ...],
) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for left in left_paths:
        for right in right_paths:
            if _paths_overlap(left, right):
                pairs.append((left, right))
    return pairs


def _paths_overlap(left: str, right: str) -> bool:
    left_parts = _path_parts(left)
    right_parts = _path_parts(right)
    if not left_parts or not right_parts:
        return False
    return (
        left_parts == right_parts[: len(left_parts)]
        or right_parts == left_parts[: len(right_parts)]
    )


def _path_parts(path: str) -> tuple[str, ...]:
    cleaned = path.replace("\\", "/").strip()
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.strip("/")
    if not cleaned or cleaned == ".":
        return ()
    return tuple(part for part in cleaned.split("/") if part and part != ".")


def _validate_dependencies(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    by_id = {packet.id: packet for packet in packets}
    for packet in packets:
        for dep in packet.dependencies:
            if dep not in by_id:
                issues.append(
                    _issue(
                        "G4",
                        f"{packet.id}: missing dependency {dep}",
                        packet_ids=[packet.id],
                        row_ids=list(packet.row_ids),
                    )
                )

    graph = {packet.id: list(packet.dependencies) for packet in packets}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> list[str] | None:
        if node in visiting:
            return [*stack, node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                continue
            cycle = visit(dep, stack)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node, [])
        if cycle:
            issues.append(
                _issue(
                    "G4",
                    "dependency cycle: " + " -> ".join(cycle),
                    packet_ids=cycle,
                )
            )
            break
    return issues


def _validate_director_done_boundary(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for packet in packets:
        if packet.packet_type != "director-implementation" or packet.status != "done":
            continue
        evidence = _evidence_text(packet)
        missing: list[str] = []
        if not packet.done_evidence:
            missing.append("done_evidence")
        if "verify-request" not in evidence and "verification not needed" not in evidence:
            missing.append("verify-request or verification-not-needed reason")
        if missing:
            issues.append(
                _issue(
                    "G5",
                    f"{packet.id}: missing " + ", ".join(missing),
                    packet_ids=[packet.id],
                    row_ids=list(packet.row_ids),
                    paths=list(packet.allowed_paths),
                )
            )
    return issues


def _validate_operator_verification_boundary(packets: list[Packet]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for packet in packets:
        if packet.packet_type != "operator-verification" or packet.status not in {"active", "done"}:
            continue
        missing: list[str] = []
        if not packet.verify_request:
            missing.append("verify_request")
        if not packet.target_commit and not packet.commit_range:
            missing.append("target_commit or commit_range")
        if not packet.scope_files and not packet.row_ids:
            missing.append("scope_files or row_ids")
        evidence = _evidence_text(packet)
        if packet.status == "done" and not re.search(r"\b(GO|NITS|FAIL)\b", evidence, re.IGNORECASE):
            missing.append("GO/NITS/FAIL evidence")
        if missing:
            issues.append(
                _issue(
                    "G6",
                    f"{packet.id}: missing " + ", ".join(missing),
                    packet_ids=[packet.id],
                    row_ids=list(packet.row_ids),
                    paths=list(packet.scope_files or packet.allowed_paths),
                )
            )
    return issues


def _validate_join_gate(packets: list[Packet], root: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    cycles = sorted({packet.cycle for packet in packets})
    for cycle in cycles:
        cycle_packets = [packet for packet in packets if packet.cycle == cycle]
        if not cycle_packets or not all(
            packet.status in {"done", "excepted"} for packet in cycle_packets
        ):
            continue
        joins = [packet for packet in cycle_packets if packet.packet_type == "coordinator-join"]
        if not joins:
            issues.append(
                _issue(
                    "G8",
                    f"cycle {cycle}: closed cycle missing coordinator-join packet",
                    packet_ids=[packet.id for packet in cycle_packets],
                    row_ids=_merged(cycle_packets, "row_ids"),
                )
            )
            continue
        for join in joins:
            evidence = _evidence_text(join)
            raw_evidence = _raw_evidence_text(join)
            structured_handoff = join.handoff_artifact or ""
            missing = [
                label
                for label, needle in (
                    ("capacity board evidence", "capacity board"),
                    ("smoke OK evidence", "smoke ok"),
                    ("handoff or next trigger", "next trigger"),
                )
                if needle not in evidence
            ]
            if structured_handoff:
                rel_path = _handoff_artifact_path(structured_handoff)
                if rel_path is None:
                    missing.append("handoff_artifact must cite docs/HANDOFF-*.md")
                elif not _handoff_artifact_file_exists(rel_path, root):
                    missing.append("handoff_artifact file missing")
            if (
                HANDOFF_REQUIRED_RE.search(raw_evidence)
                and not structured_handoff
                and not _has_handoff_artifact(raw_evidence, root)
            ):
                missing.append("handoff artifact")
            if missing:
                issues.append(
                    _issue(
                        "G8",
                        f"{join.id}: missing " + ", ".join(missing),
                        packet_ids=[join.id],
                        row_ids=list(join.row_ids),
                    )
                )
    return issues


def _has_handoff_artifact(evidence: str, root: Path) -> bool:
    for line in evidence.splitlines():
        rel_path = _handoff_artifact_path(line)
        if rel_path and _handoff_artifact_file_exists(rel_path, root):
            return True
    return False


def _handoff_artifact_path(value: str) -> Path | None:
    match = HANDOFF_ARTIFACT_RE.fullmatch(value.strip())
    if not match:
        return None
    rel_path = Path(match.group(1))
    if rel_path.parts[:1] != ("docs",) or len(rel_path.parts) != 2:
        return None
    name = rel_path.name
    if not (name.startswith("HANDOFF-") and name.endswith(".md")):
        return None
    return rel_path


def _handoff_artifact_file_exists(rel_path: Path, root: Path) -> bool:
    artifact = root / rel_path
    try:
        docs_dir = (root / "docs").resolve(strict=True)
        resolved_artifact = artifact.resolve(strict=True)
    except OSError:
        return False
    if resolved_artifact.parent != docs_dir:
        return False
    return artifact.is_file()


def _apply_exceptions(
    issues: list[dict[str, Any]],
    exceptions: list[ProtocolException],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for issue in issues:
        match = next(
            (
                exception
                for exception in exceptions
                if _exception_matches_issue(exception, issue)
            ),
            None,
        )
        if match:
            excepted = dict(issue)
            excepted["excepted_by"] = match.id
            out.append(excepted)
        else:
            out.append(issue)
    return out


def _validate_route_file(path: Path, report: CapacityReport) -> list[dict[str, Any]]:
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [_issue("G7", f"{path.name}: unreadable route ({exc})")]

    issues: list[dict[str, Any]] = []
    route_posix = path.as_posix()
    if not (
        route_posix.startswith("coordination/mailbox/sent/")
        or "/coordination/mailbox/sent/" in route_posix
    ):
        issues.append(
            _issue("G7", f"{path.name}: route path must be under coordination/mailbox/sent/")
        )
    try:
        autonomous_candidate = route_lineage.validate_route_candidate_structure(
            path, body
        )
    except ValueError:
        autonomous_candidate = None
    recognized_route = route_lineage.is_route_event(path, body)
    if not recognized_route:
        issues.append(
            _issue("G7", f"{path.name}: not a recognized outcome-contract route")
        )
    else:
        try:
            ledger_start_guard.parse_route_guidance_body(body)
        except ValueError as exc:
            issues.append(
                _issue("G7", f"{path.name}: invalid route guidance ({exc})")
            )
        if autonomous_candidate is not None:
            issues.extend(
                _autonomous_candidate_parent_issues(
                    autonomous_candidate,
                    Path(report.root),
                )
            )
        else:
            issues.extend(
                _legacy_candidate_lineage_issues(path, body, Path(report.root))
            )

    forbidden = _forbidden_side_effects(body)
    subagent_forbidden = [label for label in forbidden if label.startswith("subagent ")]
    if subagent_forbidden:
        issues.append(
            _issue(
                "G7",
                "forbidden side effect authorization: " + ", ".join(subagent_forbidden),
            )
        )
    issues.extend(_side_effect_executor_issues(body))
    issues.extend(_side_effect_success_claim_issues(body))
    return issues


def _committed_task_context(
    root: Path,
    task_id: str,
    candidate_path: Path,
    *,
    parent_ref: str | None = None,
) -> tuple[
    list[route_lineage.LineageRoute],
    tuple[str, ...],
    tuple[str, ...],
    route_lineage.LineageRoute | None,
]:
    normalized_candidate_path = (
        candidate_path if candidate_path.is_absolute() else root / candidate_path
    )
    with route_lineage.RouteBatchReader(root) as reader:
        routes = [
            route
            for route in reader.load_all_routes()
            if route.path != normalized_candidate_path
        ]
        task_issues = reader.issues_for_task(task_id)
        legacy_issues = reader.legacy_issues
        parent = reader.load_route_ref(parent_ref) if parent_ref is not None else None
    return routes, task_issues, legacy_issues, parent


def _autonomous_candidate_parent_issues(
    candidate: route_lineage.LineageRoute,
    root: Path,
) -> list[dict[str, Any]]:
    """Prove candidate continuity against current committed task truth."""

    task_id = candidate.task_id or ""
    try:
        routes, task_issues, _, parent = _committed_task_context(
            root,
            task_id,
            candidate.path,
            parent_ref=candidate.parent_ref,
        )
    except (OSError, UnicodeError, ValueError):
        message = (
            "parent contract is not an effective committed route"
            if candidate.parent_ref is not None
            else "current task route evidence is unreadable"
        )
        return [_issue("G7", f"{candidate.path.name}: {message}")]

    issues = [
        _issue(
            "G7",
            f"{candidate.path.name}: current task route evidence is unresolved ({message})",
        )
        for message in task_issues
    ]
    matching = [route for route in routes if route.task_id == task_id]

    if candidate.parent_ref is None:
        if candidate.revision != 0:
            issues.append(
                _issue(
                    "G7",
                    f"{candidate.path.name}: parent none requires contract revision 0",
                )
            )
        if matching:
            issues.append(
                _issue(
                    "G7",
                    f"{candidate.path.name}: revision-zero root requires an empty committed task",
                )
            )
        return issues

    assert parent is not None
    if not parent.effective:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent contract is not an effective committed route",
            )
        )
    if parent.task_id != candidate.task_id:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent Task ID does not match candidate Task ID",
            )
        )
    if parent.revision is None or candidate.revision != parent.revision + 1:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: contract revision must equal parent revision plus one",
            )
        )

    current_resolution = route_lineage.resolve_task_routes(routes, task_id)
    if (
        not current_resolution.issues
        and current_resolution.authoritative is not None
        and current_resolution.authoritative.route_ref != candidate.parent_ref
    ):
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent contract must equal current authoritative task tip",
            )
        )
        return issues

    prospective_ref = f"candidate://{candidate.path.name}"
    prospective_candidate = replace(
        candidate,
        effective=True,
        route_ref=prospective_ref,
    )
    prospective_resolution = route_lineage.resolve_task_routes(
        [*routes, prospective_candidate],
        task_id,
    )
    if (
        prospective_resolution.issues
        or prospective_resolution.authoritative is None
    ):
        detail = (
            "; ".join(prospective_resolution.issues)
            or "no authoritative route"
        )
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: current task lineage is unresolved ({detail})",
            )
        )
    elif prospective_resolution.authoritative.route_ref != prospective_ref:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent contract must equal current authoritative task tip",
            )
        )
    return issues


def _legacy_candidate_lineage_issues(
    path: Path,
    body: str,
    root: Path,
) -> list[dict[str, Any]]:
    task_id = route_lineage.task_board_of(body)
    if task_id is None:
        return []
    try:
        routes, task_issues, legacy_issues, _ = _committed_task_context(
            root,
            task_id,
            path,
        )
    except (OSError, UnicodeError, ValueError):
        return [
            _issue("G7", f"{path.name}: current task route evidence is unreadable")
        ]

    issues = [
        _issue(
            "G7",
            f"{path.name}: current task route evidence is unresolved ({message})",
        )
        for message in task_issues
    ]
    issues.extend(
        _issue(
            "G7",
            f"{path.name}: current global legacy lineage is unresolved ({message})",
        )
        for message in legacy_issues
    )
    legacy_routes = [route for route in routes if route.legacy]
    generated_legacy = [
        route
        for route in legacy_routes
        if route.lineage.generation is not None
    ]
    if generated_legacy:
        candidate_lineage = route_lineage.parse_lineage(body)
        known_ids = {route.route_id for route in legacy_routes}
        unknown_parents = sorted(
            set(candidate_lineage.parent_route_ids) - known_ids
        )
        if unknown_parents:
            issues.append(
                _issue(
                    "G7",
                    f"{path.name}: merge route declares unknown parent "
                    + ", ".join(unknown_parents),
                )
            )
        lineage_state = route_lineage.inspect_lineage(legacy_routes)
        if lineage_state.structural_issues:
            detail = "; ".join(lineage_state.structural_issues)
            issues.append(
                _issue(
                    "G7",
                    f"{path.name}: current global legacy lineage is unresolved ({detail})",
                )
            )
        elif not lineage_state.tips:
            issues.append(
                _issue(
                    "G7",
                    f"{path.name}: current global legacy lineage is unresolved (no global tip)",
                )
            )
        else:
            tip_ids = {route.route_id for route in lineage_state.tips}
            parent_ids = set(candidate_lineage.parent_route_ids)
            expected_generation = (
                max(
                    route.lineage.generation
                    for route in lineage_state.tips
                    if route.lineage.generation is not None
                )
                + 1
            )
            if len(lineage_state.tips) == 1:
                current_tip = lineage_state.tips[0]
                if (
                    parent_ids != tip_ids
                    or candidate_lineage.generation != expected_generation
                ):
                    issues.append(
                        _issue(
                            "G7",
                            f"{path.name}: generated legacy route must extend current "
                            f"global tip {current_tip.route_id} at generation "
                            f"{expected_generation}",
                        )
                    )
            else:
                if parent_ids != tip_ids:
                    issues.append(
                        _issue(
                            "G7",
                            f"{path.name}: merge parents must equal the complete current "
                            "unsuperseded tip set",
                        )
                    )
                if candidate_lineage.generation != expected_generation:
                    issues.append(
                        _issue(
                            "G7",
                            f"{path.name}: merge generation must equal max current tip "
                            "generation plus one",
                        )
                    )

            candidate = route_lineage.LineageRoute(
                route_id=route_lineage.route_id_of(path.name),
                lineage=candidate_lineage,
                task_id=task_id,
                path=path,
            )
            prospective = route_lineage.resolve_authoritative(
                [*legacy_routes, candidate]
            )
            if (
                prospective.issues
                or prospective.authoritative is None
                or prospective.authoritative.route_id != candidate.route_id
            ):
                issues.append(
                    _issue(
                        "G7",
                        f"{path.name}: merge candidate does not produce the sole global tip",
                    )
                )
    if any(
        route.task_id == task_id and not route.legacy
        for route in routes
    ):
        issues.append(
            _issue(
                "G7",
                f"{path.name}: legacy route cannot extend a task with autonomous lineage; "
                "the incumbent must publish an autonomous continuation or use durable transfer",
            )
        )
    return issues


def _active_cycles(packets: list[Packet]) -> list[str]:
    return sorted(
        {
            packet.cycle
            for packet in packets
            if packet.is_active_wip
        }
    )


def _forbidden_side_effects(body: str) -> list[str]:
    terms = {
        "push": r"\bpush\b|\bforce-push\b",
        "lock claim": r"\block claim\b|\block-claim\b|\bclaim lock\b",
        "lock release": r"\block release\b|\block-release\b|\brelease lock\b",
        "paid API spend": r"\bpaid api spend\b|\bpaid-api spend\b",
        "pod spend": r"\bpod spend\b",
        "pod start": r"\bstart pods?\b|\bstart a pod\b",
        "production generation": r"\bproduction generation\b",
    }
    subagent_terms = {
        "subagent operator GO": r"\boperator\s+go\b|\bissue\s+(?:operator\s+)?go\b",
        "subagent mailbox event": r"\bsend(?:s|ing)?-event\b|\bsend(?:s|ing)?\s+mailbox\s+events?\b|\bmailbox\s+events?\b",
        "subagent cursor consume": r"\bconsume-events?\b|\bconsume\b.*\bcursors?\b|\bcursors?\b.*\bconsume\b",
        "subagent coordinator route": r"\bcoordinator\s+routes?\b|\bcreate\b.*\broutes?\b|\broutes?\b.*\bcreate\b",
        "subagent push": r"\bpush\b|\bforce-push\b",
        "subagent lock claim": r"\block claim\b|\block-claim\b|\bclaim(?:s|ing)? locks?\b|\bclaim locks?\b",
        "subagent lock release": r"\block release\b|\block-release\b|\brelease(?:s|ing)? locks?\b|\brelease locks?\b",
        "subagent pod start": r"\bstart(?:s|ing)? pods?\b|\bpods?\b.*\bstart\b",
        "subagent spend": r"\bspend\b|\bpaid api\b|\bpaid-api\b|\bcost\b",
    }
    auth = r"\b(authorizes?|authorized|allows?|grants?)\b"
    delegation = (
        r"\b("
        r"authorizes?|authorized|allows?|grants?|may|can|will|shall|should|must|"
        r"dispatch(?:es|ed|ing)?|delegate(?:s|d|ing)?|assign(?:s|ed|ing)?|"
        r"spawn(?:s|ed|ing)?|instruct(?:s|ed|ing)?|direct(?:s|ed|ing)?"
        r")\b"
    )
    subagent = r"\bsub-?agents?\b"
    found: list[str] = []
    for line in body.splitlines():
        lowered = line.lower()
        normalized = lowered.strip().lstrip("-* ").strip()
        if normalized.startswith("no "):
            continue
        for label, pattern in terms.items():
            if re.search(auth, lowered) and re.search(pattern, lowered):
                if label not in found:
                    found.append(label)
        if re.search(auth, lowered) and re.search(subagent, lowered):
            for label, pattern in subagent_terms.items():
                if re.search(pattern, lowered) and label not in found:
                    found.append(label)
        elif (
            re.search(subagent, lowered)
            and re.search(delegation, lowered)
            and not _is_negative_subagent_boundary(normalized)
        ):
            for label, pattern in subagent_terms.items():
                if re.search(pattern, lowered) and label not in found:
                    found.append(label)
    return found


def _side_effect_executor_issues(body: str) -> list[dict[str, Any]]:
    tokens = _side_effect_executor_tokens(body)
    issues: list[dict[str, Any]] = []
    token_results = structural_external_effect_token_results(body)
    for token, result in zip(tokens, token_results, strict=True):
        for field in _duplicate_token_fields(token):
            issues.append(
                _issue(
                    "G7",
                    f"duplicate side-effect executor token field: {field}",
                )
            )
        fields = _token_shape_fields(token)
        missing = [
            field
            for field in fields
            if not token.get(field)
        ]
        if missing:
            issues.append(
                _issue(
                    "G7",
                    "incomplete side-effect executor token missing: "
                    + ", ".join(missing),
                )
            )
        if token.get("executor") and len(_executor_seats(token["executor"])) != 1:
            issues.append(
                _issue(
                    "G7",
                    "side-effect executor token must name exactly one executor",
                )
            )
        for field in result.issues:
            if field.startswith("duplicate:"):
                continue
            if field in missing:
                continue
            if field == "executor" and token.get("executor"):
                continue
            issues.append(
                _issue(
                    "G7",
                    f"side-effect executor token has invalid {field}",
                )
            )

    side_effect_requests = _shared_side_effect_requests(body)
    side_effect_labels = sorted({request["label"] for request in side_effect_requests})
    complete_tokens = [
        token
        for token, result in zip(tokens, token_results, strict=True)
        if _token_is_structurally_complete(token) and result.complete
    ]
    issues.extend(_token_group_cardinality_issues(complete_tokens))
    if side_effect_labels and not complete_tokens:
        issues.append(
            _issue(
                "G7",
                "missing side-effect executor token for shared side effect authorization: "
                + ", ".join(side_effect_labels),
            )
        )
    elif side_effect_requests:
        uncovered: list[dict[str, Any]] = []
        for request in side_effect_requests:
            covering = [
                token
                for token in complete_tokens
                if _token_covers_effect_target_scope(token, request)
            ]
            if not covering:
                uncovered.append(request)
                continue
            if len(covering) > 1:
                exact_tuples = [_token_exact_tuple(token) for token in covering]
                executors = {item[1].casefold() for item in exact_tuples}
                target = request.get("target", "")
                scope = request.get("scope", ())
                suffix = f" target={target}" if target else ""
                if scope:
                    suffix += " scope=" + ",".join(scope)
                if len(set(exact_tuples)) < len(exact_tuples):
                    message = "duplicate side-effect executor tokens cover"
                elif len(executors) > 1:
                    message = (
                        "multiple side-effect executor tokens cover"
                        " with different executors"
                    )
                else:
                    message = "multiple side-effect executor tokens cover"
                issues.append(
                    _issue(
                        "G7",
                        f"{message} {request['label']}{suffix}; exactly one is required",
                    )
                )
                continue
            if not _token_executor_matches(covering[0], request):
                uncovered.append(request)
        if uncovered:
            labels = ", ".join(
                sorted(
                    {
                        request["label"]
                        + (f" target={request['target']}" if request["target"] else "")
                        for request in uncovered
                    }
                )
            )
            issues.append(
                _issue(
                    "G7",
                    "side-effect executor token target/command mismatch for "
                    + labels,
                )
            )
    return issues


def _executor_seats(value: str) -> list[str]:
    return re.findall(
        r"\b(?:coordinator2|coordinator|director2|director|operator2|operator)\b",
        value.lower(),
    )


def _duplicate_token_fields(token: dict[str, str]) -> tuple[str, ...]:
    value = token.get(_DUPLICATE_TOKEN_FIELDS_KEY, "")
    return tuple(field for field in value.split(",") if field)


def _token_is_structurally_complete(token: dict[str, str]) -> bool:
    compact = all(token.get(field) for field in REQUIRED_SIDE_EFFECT_TOKEN_FIELDS)
    legacy = all(token.get(field) for field in LEGACY_SIDE_EFFECT_TOKEN_FIELDS)
    return compact or legacy


def _token_shape_fields(token: dict[str, str]) -> tuple[str, ...]:
    legacy_only_fields = set(LEGACY_SIDE_EFFECT_TOKEN_FIELDS) - set(
        REQUIRED_SIDE_EFFECT_TOKEN_FIELDS
    )
    if any(token.get(field) for field in legacy_only_fields):
        return LEGACY_SIDE_EFFECT_TOKEN_FIELDS
    return REQUIRED_SIDE_EFFECT_TOKEN_FIELDS


def _scope_items(token: dict[str, str]) -> tuple[str, ...]:
    compact_scope = token.get("scope", "").strip()
    if compact_scope:
        return tuple(
            item.strip()
            for item in compact_scope.split(",")
            if item.strip()
        )
    legacy_scope_fields = (
        "side_effect_id",
        "preflight",
        "stop_if_newer_mail_or_live_target_satisfied",
        "postcheck",
        "observer_seats",
        "final_closeout_owner",
        "non_goals",
    )
    return tuple(
        f"{field}:{token[field].strip()}"
        for field in legacy_scope_fields
        if token.get(field, "").strip()
    )


def _canonical_effect(token: dict[str, str]) -> str:
    return " ".join(
        (token.get("effect") or token.get("allowed_command_class", "")).split()
    ).casefold()


def _token_exact_tuple(token: dict[str, str]) -> tuple[str, str, str, tuple[str, ...]]:
    return (
        _canonical_effect(token),
        token.get("executor", "").strip(),
        token.get("target", "").strip(),
        tuple(item.strip() for item in _scope_items(token) if item.strip()),
    )


def structural_external_effect_tokens(body: str) -> tuple[model.ExternalEffectToken, ...]:
    """Parse descriptive token shapes without creating execution authority."""

    return tuple(
        model.ExternalEffectToken(
            effect=effect,
            executor=executor,
            target=target,
            scope=scope,
        )
        for effect, executor, target, scope in (
            _token_exact_tuple(token) for token in _side_effect_executor_tokens(body)
        )
    )


def structural_external_effect_token_results(
    body: str,
) -> tuple[model.ExternalEffectTokenResult, ...]:
    """Return fail-closed shape results that can never authorize execution."""

    raw_tokens = _side_effect_executor_tokens(body)
    parsed_tokens = structural_external_effect_tokens(body)
    results: list[model.ExternalEffectTokenResult] = []
    for raw, parsed in zip(raw_tokens, parsed_tokens, strict=True):
        fields = _token_shape_fields(raw)
        missing = tuple(field for field in fields if not raw.get(field))
        duplicates = tuple(
            f"duplicate:{field}" for field in _duplicate_token_fields(raw)
        )
        shape = model.external_effect_token_is_complete(parsed)
        result_issues = tuple(
            dict.fromkeys((*shape.issues, *missing, *duplicates))
        )
        results.append(
            model.ExternalEffectTokenResult(
                complete=shape.complete and not missing and not duplicates,
                issues=result_issues,
                explicit_external_user_authorization_required=True,
                execution_authorized=False,
            )
        )
    return tuple(results)


def _canonical_effect_kind(value: str) -> str:
    normalized = " ".join(value.split()).casefold()
    for label, pattern in SHARED_SIDE_EFFECT_PATTERNS.items():
        if re.fullmatch(pattern, normalized):
            return label.casefold()
    return normalized


def _canonical_scope(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(" ".join(item.split()).casefold() for item in items)


def _token_group_key(token: dict[str, str]) -> tuple[str, str, tuple[str, ...]]:
    return (
        _canonical_effect_kind(_canonical_effect(token)),
        token.get("target", "").strip().casefold(),
        _canonical_scope(_scope_items(token)),
    )


def _token_group_cardinality_issues(
    tokens: list[dict[str, str]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, tuple[str, ...]], list[dict[str, str]]] = {}
    for token in tokens:
        groups.setdefault(_token_group_key(token), []).append(token)

    issues: list[dict[str, Any]] = []
    for (effect, target, scope), group in sorted(groups.items()):
        if len(group) == 1:
            continue
        executors = {
            token.get("executor", "").strip().casefold() for token in group
        }
        suffix = f" effect={effect} target={target}"
        if scope:
            suffix += " scope=" + ",".join(scope)
        if len(executors) > 1:
            message = "multiple side-effect executor tokens define"
            suffix += " with different executors"
        else:
            message = "duplicate side-effect executor tokens define"
        issues.append(
            _issue(
                "G7",
                f"{message}{suffix}; exactly one token and executor are required",
            )
        )
    return issues


def _token_covers_effect_target_scope(
    token: dict[str, str],
    request: dict[str, Any],
) -> bool:
    if _canonical_effect_kind(_canonical_effect(token)) != request["label"].casefold():
        return False
    target = request.get("target", "").strip().casefold()
    if target and target != token.get("target", "").strip().casefold():
        return False
    scope = request.get("scope", ())
    if scope and _canonical_scope(scope) != _canonical_scope(_scope_items(token)):
        return False
    return True


def _token_executor_matches(token: dict[str, str], request: dict[str, Any]) -> bool:
    executor = request.get("executor", "").strip().casefold()
    if executor and executor != token.get("executor", "").strip().casefold():
        return False
    return True


def _side_effect_executor_tokens(body: str) -> list[dict[str, str]]:
    lines = body.splitlines()
    tokens: list[dict[str, str]] = []
    index = 0
    while index < len(lines):
        if not SIDE_EFFECT_TOKEN_HEADING_RE.match(lines[index]):
            index += 1
            continue
        token: dict[str, str] = {}
        index += 1
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if SIDE_EFFECT_TOKEN_HEADING_RE.match(line):
                break
            if stripped and _MARKDOWN_HEADING_RE.match(line):
                break
            field_match = re.match(
                r"^\s*(?:[-*]\s*)?([^:]+?)\s*:\s*(.+?)\s*$",
                line,
            )
            if field_match:
                raw_key = field_match.group(1).strip().lower().replace("-", " ")
                normalized = SIDE_EFFECT_TOKEN_FIELD_ALIASES.get(raw_key)
                if normalized:
                    if normalized in token:
                        duplicates = set(_duplicate_token_fields(token))
                        duplicates.add(normalized)
                        token[_DUPLICATE_TOKEN_FIELDS_KEY] = ",".join(
                            sorted(duplicates)
                        )
                    else:
                        token[normalized] = field_match.group(2).strip()
            index += 1
        tokens.append(token)
    return tokens


def _shared_side_effect_directives(body: str) -> list[str]:
    return sorted({request["label"] for request in _shared_side_effect_requests(body)})


def _shared_side_effect_requests(body: str) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for line in body.splitlines():
        lowered = line.lower()
        normalized = lowered.strip().lstrip("-* ").strip()
        field_match = re.match(r"^([^:]+?)\s*:\s*(.+?)\s*$", normalized)
        if field_match:
            raw_key = field_match.group(1).strip().replace("-", " ")
            if raw_key in SIDE_EFFECT_TOKEN_FIELD_ALIASES:
                continue
        if normalized.startswith("no "):
            continue
        if _is_negative_side_effect_boundary(normalized):
            continue
        if not SIDE_EFFECT_DIRECTIVE_RE.search(lowered):
            continue
        for label, pattern in SHARED_SIDE_EFFECT_PATTERNS.items():
            if not re.search(pattern, lowered):
                continue
            target = _side_effect_target(label, lowered)
            executors = _executor_seats(lowered)
            executor = executors[0] if len(executors) == 1 else ""
            scope = _side_effect_scope(lowered)
            key = (label, executor, target, scope)
            if key not in seen:
                seen.add(key)
                requests.append(
                    {
                        "label": label,
                        "executor": executor,
                        "target": target,
                        "scope": scope,
                    }
                )
    return requests


def _side_effect_scope(line: str) -> tuple[str, ...]:
    match = re.search(r"\bscope\s*=\s*(?P<scope>.+?)\s*$", line)
    if match is None:
        return ()
    return tuple(
        item.strip()
        for item in match.group("scope").split(",")
        if item.strip()
    )


def _side_effect_target(label: str, line: str) -> str:
    if label == "remote-ref update/push":
        match = re.search(r"\b(?:push(?:es)?|git push)\s+([^\s,.;)]+)", line)
        if match:
            return match.group(1).strip("`'\"").lower()
        match = re.search(r"\b(?:origin|refs/heads)/[^\s,.;)]+", line)
        if match:
            return match.group(0).strip("`'\"").lower()
    if label == "lock action":
        match = re.search(r"\b[^\s,.;)]*locks/[^\s,.;)]+", line)
        if match:
            return match.group(0).strip("`'\"").lower()
        match = re.search(r"\b[^\s,.;)]+\.lock\b", line)
        if match:
            return match.group(0).strip("`'\"").lower()
    return ""


def _is_negative_side_effect_boundary(line: str) -> bool:
    return bool(
        re.search(
            r"\b(do\s+not|does\s+not|must\s+not|may\s+not|should\s+not|"
            r"can\s+not|cannot|can't|will\s+not|shall\s+not|"
            r"not\s+allowed\s+to|unable\s+to|never|non[-_ ]goals?)\b",
            line,
        )
    )


def _side_effect_success_claim_issues(body: str) -> list[dict[str, Any]]:
    claims = _side_effect_success_claims(body)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for claim in claims:
        key = (claim.get("action", ""), claim.get("target", ""))
        if not key[0] or not key[1]:
            continue
        grouped.setdefault(key, []).append(claim)

    issues: list[dict[str, Any]] = []
    for (action, target), group in sorted(grouped.items()):
        if len(group) < 2:
            continue
        token_ids = {claim.get("side_effect_id", "") for claim in group}
        if len(token_ids) == 1 and "" not in token_ids:
            continue
        issues.append(
            _issue(
                "G7",
                "multiple side-effect success claims for "
                f"{action} target={target} without common side_effect_id",
            )
        )
    return issues


def _side_effect_success_claims(body: str) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    for line in body.splitlines():
        match = SIDE_EFFECT_SUCCESS_RE.search(line)
        if not match:
            continue
        claim_body = match.group("body").strip()
        target = _claim_value(claim_body, "target")
        token_id = _claim_value(claim_body, "side_effect_id")
        action = claim_body.split("target=", 1)[0].strip().strip(",;")
        if token_id:
            action = action.split("side_effect_id=", 1)[0].strip().strip(",;")
        claims.append(
            {
                "action": re.sub(r"\s+", " ", action.lower()),
                "target": target.lower(),
                "side_effect_id": token_id,
            }
        )
    return claims


def _claim_value(text: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}=([^\s,;]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _is_negative_subagent_boundary(line: str) -> bool:
    if re.search(r"\bno\s+sub-?agents?\b", line):
        return True
    return bool(
        re.search(
            r"\bsub-?agents?\b.*\b("
            r"do\s+not|does\s+not|must\s+not|may\s+not|should\s+not|"
            r"can\s+not|cannot|can't|will\s+not|shall\s+not|"
            r"not\s+allowed\s+to|unable\s+to|never"
            r")\b",
            line,
        )
    )


def _exception_matches_issue(exception: ProtocolException, issue: dict[str, Any]) -> bool:
    if not exception.is_active or exception.bypassed_gate != issue.get("gate"):
        return False
    scope = exception.scope
    has_scoped_issue_value = False
    for issue_key, scope_key in (
        ("packet_ids", "packet_ids"),
        ("row_ids", "row_ids"),
        ("paths", "paths"),
    ):
        issue_values = set(issue.get(issue_key) or [])
        if not issue_values:
            continue
        has_scoped_issue_value = True
        scope_values = set(scope.get(scope_key) or [])
        if not issue_values <= scope_values:
            return False
    return has_scoped_issue_value


def _issue(
    gate: str,
    message: str,
    *,
    packet_ids: list[str] | None = None,
    row_ids: list[str] | None = None,
    paths: list[str] | None = None,
    lock_keys: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "gate": gate,
        "message": message,
        "packet_ids": packet_ids or [],
        "row_ids": row_ids or [],
        "paths": paths or [],
        "lock_keys": lock_keys or [],
    }


def _is_str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _evidence_text(packet: Packet) -> str:
    return _raw_evidence_text(packet).lower()


def _raw_evidence_text(packet: Packet) -> str:
    return "\n".join(packet.done_evidence)


def _display_path(path: Path) -> str:
    return path.as_posix()


def _merged(packets: list[Packet], field: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for packet in packets:
        for value in getattr(packet, field):
            if value not in seen:
                values.append(value)
                seen.add(value)
    return values
