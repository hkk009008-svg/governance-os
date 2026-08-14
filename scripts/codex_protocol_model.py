#!/usr/bin/env python3
"""Small executable seams shared by Codex protocol tooling."""

from __future__ import annotations

import os
import re
import subprocess
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

import protocol_mailbox


MODEL_SOURCE = "scripts/codex_protocol_model.py"
CENTRAL_INVARIANT = "durable shared state beats chat memory"


@dataclass(frozen=True)
class ReviewProfile:
    """Executable acceptance requirements for one closed risk class."""

    risk_class: str
    focused_verification: bool
    requires_non_author_review: bool
    requires_exact_range: bool
    requires_different_model: bool
    requires_abuse_class_assessment: bool
    requires_live_authorization: bool


RISK_BASED_REVIEW_PROFILES = {
    "ordinary-local": ReviewProfile(
        risk_class="ordinary-local",
        focused_verification=True,
        requires_non_author_review=False,
        requires_exact_range=False,
        requires_different_model=False,
        requires_abuse_class_assessment=False,
        requires_live_authorization=False,
    ),
    "material-behavior": ReviewProfile(
        risk_class="material-behavior",
        focused_verification=True,
        requires_non_author_review=True,
        requires_exact_range=True,
        requires_different_model=False,
        requires_abuse_class_assessment=False,
        requires_live_authorization=False,
    ),
    "high-risk-control": ReviewProfile(
        risk_class="high-risk-control",
        focused_verification=True,
        requires_non_author_review=True,
        requires_exact_range=True,
        requires_different_model=True,
        requires_abuse_class_assessment=True,
        requires_live_authorization=False,
    ),
    "external-effect": ReviewProfile(
        risk_class="external-effect",
        focused_verification=False,
        requires_non_author_review=False,
        requires_exact_range=False,
        requires_different_model=False,
        requires_abuse_class_assessment=False,
        requires_live_authorization=True,
    ),
}


def review_profile_for(risk_class: str) -> ReviewProfile:
    """Return one closed risk profile or reject an unclassified workflow."""
    try:
        return RISK_BASED_REVIEW_PROFILES[risk_class]
    except KeyError as exc:
        raise ValueError(f"unknown Codex review risk class: {risk_class}") from exc


@dataclass(frozen=True)
class WorkModeProfile:
    """Iteration and evidence contract for one closed phase of product work.

    Work mode is orthogonal to review risk. It controls how cheaply a task may
    learn, what record is proportionate, and when a candidate must cross a
    review boundary. It never grants canonical mutation or an external effect.
    """

    work_mode: str
    rerun_policy: str
    canonical_mutation_policy: str
    review_policy: str
    claim_policy: str
    record_policy: str
    requires_frozen_inputs: bool
    requires_non_author_review: bool
    requires_rollback_point: bool


WORK_MODE_PROFILES = {
    "explore": WorkModeProfile(
        work_mode="explore",
        rerun_policy="recorded-reruns-allowed",
        canonical_mutation_policy="forbidden",
        review_policy="none-until-transfer-or-phase-change",
        claim_policy="phase-transition-claims-only",
        record_policy="one-campaign-brief-plus-automatic-attempt-log",
        requires_frozen_inputs=False,
        requires_non_author_review=False,
        requires_rollback_point=False,
    ),
    "validate": WorkModeProfile(
        work_mode="validate",
        rerun_policy="frozen-input-reproduction",
        canonical_mutation_policy="forbidden",
        review_policy="one-non-author-candidate-review",
        claim_policy="load-bearing-candidate-claims",
        record_policy="frozen-report-plus-generated-manifest",
        requires_frozen_inputs=True,
        requires_non_author_review=True,
        requires_rollback_point=False,
    ),
    "promote": WorkModeProfile(
        work_mode="promote",
        rerun_policy="reviewed-candidate-only",
        canonical_mutation_policy="separately-authorized",
        review_policy="reviewed-candidate-plus-effect-authority",
        claim_policy="load-bearing-claims-plus-independent-review",
        record_policy="rollback-record-plus-approval-evidence",
        requires_frozen_inputs=True,
        requires_non_author_review=True,
        requires_rollback_point=True,
    ),
}


def work_profile_for(work_mode: str) -> WorkModeProfile:
    """Return one closed work-mode profile or reject an invented phase."""
    try:
        return WORK_MODE_PROFILES[work_mode]
    except KeyError as exc:
        raise ValueError(f"unknown Codex work mode: {work_mode}") from exc


# Harness/vendor decorations that describe where a model runs, not which model
# it is. `codex-gpt-5.6-terra` and `gpt-5.6-terra` are one model behind two
# labels; independence must not be satisfiable by the prefix alone.
MODEL_HARNESS_PREFIXES = ("codex-", "claude-code-")
_MODEL_FAMILIES_CONFIG = (
    Path(__file__).resolve().parent.parent / "config" / "model-families.toml"
)


def load_model_families(config_path: Path = _MODEL_FAMILIES_CONFIG) -> tuple[
    dict[str, str], dict[str, str], dict[str, str]
]:
    """Load the model-family registry from configuration, failing closed.

    This data feeds ``models_are_independent``, which gates high-risk-control
    review acceptance — it is a trust-granting schema input, not casual
    config. A missing, unparsable, or wrong-shaped file raises rather than
    degrading to an empty registry (an empty registry would silently make
    every independence claim fail, and a permissive default could make one
    falsely pass). Unknown model IDs remain family-``None``: free for
    ordinary work, never sufficient for a different-family claim.
    """
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(
            f"model-families configuration unavailable or unparsable: {exc}"
        ) from exc
    if payload.get("schema_version") != 1:
        raise RuntimeError("model-families schema_version must be 1")
    tables = []
    for key in ("provider_prefixes", "families", "display_aliases"):
        table = payload.get(key)
        if not isinstance(table, dict) or not table or not all(
            isinstance(name, str) and name and isinstance(value, str) and value
            for name, value in table.items()
        ):
            raise RuntimeError(
                f"model-families [{key}] must be a nonempty string→string table"
            )
        tables.append(dict(table))
    prefixes, families, aliases = tables
    known_families = set(prefixes.values())
    unknown = {family for family in families.values() if family not in known_families}
    if unknown:
        raise RuntimeError(
            f"model-families [families] names families with no provider prefix: {sorted(unknown)}"
        )
    if unmapped := {alias: model for alias, model in aliases.items() if model not in families}:
        raise RuntimeError(
            f"model-families [display_aliases] targets unknown model IDs: {sorted(unmapped)}"
        )
    return prefixes, families, aliases


def load_review_admission(
    config_path: Path = _MODEL_FAMILIES_CONFIG,
) -> tuple[frozenset[str], str]:
    """Load the closed current-review families and immutable-history boundary."""

    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(
            f"model-families configuration unavailable or unparsable: {exc}"
        ) from exc
    admission = payload.get("review_admission")
    if not isinstance(admission, dict):
        raise RuntimeError("model-families [review_admission] table is required")
    active = admission.get("active_families")
    cutover = admission.get("historical_cutover")
    if (
        not isinstance(active, list)
        or not active
        or not all(isinstance(family, str) and family for family in active)
        or len(active) != len(set(active))
    ):
        raise RuntimeError(
            "model-families review_admission.active_families must be a unique "
            "nonempty string list"
        )
    prefixes = payload.get("provider_prefixes")
    if not isinstance(prefixes, dict) or not set(active) <= set(prefixes.values()):
        raise RuntimeError(
            "model-families active review families must have provider prefixes"
        )
    if not isinstance(cutover, str) or re.fullmatch(r"[0-9a-f]{40}", cutover) is None:
        raise RuntimeError(
            "model-families review_admission.historical_cutover must be one full SHA"
        )
    repository_root = config_path.resolve().parent.parent
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    try:
        exists = subprocess.run(
            [
                "/usr/bin/git",
                "--no-replace-objects",
                "-C",
                str(repository_root),
                "cat-file",
                "-e",
                f"{cutover}^{{commit}}",
            ],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
        ancestor = subprocess.run(
            [
                "/usr/bin/git",
                "--no-replace-objects",
                "-C",
                str(repository_root),
                "merge-base",
                "--is-ancestor",
                cutover,
                "HEAD",
            ],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(
            "model-families historical_cutover could not be verified against Git"
        ) from exc
    if exists.returncode != 0 or ancestor.returncode != 0:
        raise RuntimeError(
            "model-families historical_cutover must resolve to an ancestor of HEAD"
        )
    return frozenset(active), cutover


MODEL_PROVIDER_FAMILIES, MODEL_ID_REGISTRY, MODEL_DISPLAY_ALIASES = (
    load_model_families()
)
CURRENT_REVIEW_FAMILIES, CURRENT_REVIEW_FAMILY_CUTOVER = load_review_admission()


def model_family(model_id: str) -> str | None:
    """Collapse one system-visible model ID to its provider family.

    Independence is a property of the underlying model, not of the label a
    harness prints. The observed corpus pairs `gpt-5.6-sol` authors with
    `gpt-5.6-terra` reviewers; those are the same family and a plain string
    inequality accepts them. This normalizer exists so the acceptance rule can
    ask the question it actually means.

    Only the closed model-ID registry is recognized. Unknown or malformed
    labels return ``None`` so they cannot buy independence from any other
    label; adding a future model is an explicit policy update.
    """
    if not model_id or model_id != model_id.strip():
        return None
    token = MODEL_DISPLAY_ALIASES.get(model_id, model_id.casefold())
    while True:
        original = token
        for prefix in MODEL_HARNESS_PREFIXES:
            if token.startswith(prefix) and len(token) > len(prefix):
                token = token[len(prefix) :]
                break
        if token == original:
            break

    provider_family = None
    for prefix, family in MODEL_PROVIDER_FAMILIES.items():
        if token.startswith(prefix) and len(token) > len(prefix):
            provider_family = family
            token = token[len(prefix) :]
            break

    family = MODEL_ID_REGISTRY.get(token)
    if family is None:
        return None
    if provider_family is not None and provider_family != family:
        return None
    return family


def models_are_independent(author_model: str, reviewer_model: str) -> bool:
    """Return whether two system-visible model IDs are different families."""
    author_family = model_family(author_model)
    reviewer_family = model_family(reviewer_model)
    return (
        author_family is not None
        and reviewer_family is not None
        and author_family != reviewer_family
    )


def models_are_current_review_pair(author_model: str, reviewer_model: str) -> bool:
    """Return whether a pair is independent within the live two-provider policy."""

    author_family = model_family(author_model)
    reviewer_family = model_family(reviewer_model)
    return (
        author_family in CURRENT_REVIEW_FAMILIES
        and reviewer_family in CURRENT_REVIEW_FAMILIES
        and author_family != reviewer_family
    )


SEATS = protocol_mailbox.SEATS
DIRECTOR_SEATS = ("director", "director2")
OPERATOR_SEATS = ("operator", "operator2")
COORDINATOR_SEATS = ("coordinator", "coordinator2")
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
RUNTIME_MODES = ("readiness-bridge", "live-seat", "coordinator", "subagent")
RUNTIME_IDENTITY_ENV_KEYS = (
    "CODEX_AGENT_MODE",
    "CODEX_AGENT_ROLE",
    "CODEX_SEAT",
    "CODEX_BEHAVIOR_SOURCE",
)
RUNTIME_DERIVED_POLICY_ENV_KEYS = (
    "CODEX_CAPABILITY_MODE",
    "CODEX_MUTATION_SCOPE",
    "CODEX_AUTHORITY_SCOPE",
    "CODEX_MAILBOX_POLICY",
    "CODEX_GIT_POLICY",
    "CODEX_VERIFICATION_POLICY",
    "CODEX_CONTEXT_SOURCES",
    "CODEX_OUTPUT_CONTRACT",
    "CODEX_DECISION_BOUNDARY",
    "CODEX_NEXT_ACTION_POLICY",
    "CODEX_SIDE_EFFECT_POLICY",
)
RUNTIME_SCRUB_ENV_KEYS = (
    *RUNTIME_IDENTITY_ENV_KEYS,
    *RUNTIME_DERIVED_POLICY_ENV_KEYS,
    "GIT_INDEX_FILE",
)


class RuntimeIdentityError(ValueError):
    """Raised when explicit Codex identity inputs do not form one closed identity."""


_RUNTIME_ROLE_SPECS = {
    "readiness-bridge": ("readiness-bridge", None, None),
    "subagent": ("subagent", None, None),
    **{seat: ("live-seat", seat, behavior_source_for_seat(seat)) for seat in SEATS},
    **{seat: ("coordinator", seat, None) for seat in COORDINATOR_SEATS},
    **{role: ("subagent", None, None) for role in SPAWNED_ROLE_AGENT_ROLES},
}


@dataclass(frozen=True)
class RuntimeIdentity:
    """Validated process identity; policy and authority are derived elsewhere."""

    mode: str
    seat: str | None
    role: str
    behavior_source: str | None
    model: str | None = None

    def __post_init__(self) -> None:
        if self.model is not None and (
            not self.model
            or self.model.strip() != self.model
            or any(character.isspace() or ord(character) < 32 for character in self.model)
        ):
            raise RuntimeIdentityError("model must be a non-empty model name")
        expected = _RUNTIME_ROLE_SPECS.get(self.role)
        actual = (self.mode, self.seat, self.behavior_source)
        if expected is None or actual != expected:
            raise RuntimeIdentityError(
                "contradictory Codex runtime identity: "
                f"mode={self.mode!r}, seat={self.seat!r}, role={self.role!r}, "
                f"behavior_source={self.behavior_source!r}"
            )

    @classmethod
    def for_seat(cls, seat: str, *, model: str | None = None) -> RuntimeIdentity:
        """Derive one canonical live-seat or coordinator identity."""
        if seat not in (*SEATS, *COORDINATOR_SEATS):
            raise RuntimeIdentityError(f"unsupported Codex seat: {seat}")
        return cls._for_role(seat, model=model)

    @classmethod
    def _for_role(cls, role: str, *, model: str | None = None) -> RuntimeIdentity:
        try:
            mode, seat, behavior_source = _RUNTIME_ROLE_SPECS[role]
        except KeyError as exc:
            raise RuntimeIdentityError(f"unsupported Codex runtime role: {role}") from exc
        return cls(mode, seat, role, behavior_source, model)

    @classmethod
    def from_environ(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        model: str | None = None,
    ) -> RuntimeIdentity:
        """Parse only identity inputs and reject unknown or contradictory values."""
        source = environ or {}
        explicit_mode = source.get("CODEX_AGENT_MODE", "")
        explicit_role = source.get("CODEX_AGENT_ROLE", "")
        explicit_seat = source.get("CODEX_SEAT", "")
        explicit_behavior = source.get("CODEX_BEHAVIOR_SOURCE", "")
        if explicit_seat:
            identity = cls.for_seat(explicit_seat, model=model)
        elif explicit_role:
            identity = cls._for_role(explicit_role, model=model)
        elif explicit_mode in ("", "readiness-bridge", "subagent"):
            identity = cls._for_role(explicit_mode or "readiness-bridge", model=model)
        elif explicit_mode in RUNTIME_MODES:
            raise RuntimeIdentityError(
                f"{explicit_mode} mode requires a concrete matching seat or role"
            )
        else:
            raise RuntimeIdentityError(f"unsupported Codex runtime mode: {explicit_mode}")
        explicit = {
            "mode": explicit_mode,
            "role": explicit_role,
            "behavior source": explicit_behavior,
        }
        expected = {
            "mode": identity.mode,
            "role": identity.role,
            "behavior source": identity.behavior_source or "(none)",
        }
        for field, value in explicit.items():
            if value and value != expected[field]:
                raise RuntimeIdentityError(
                    f"{field} {value!r} contradicts {expected[field]!r} identity"
                )
        return identity

    def as_env(self) -> dict[str, str]:
        """Return the minimal identity environment, excluding policy authority."""
        values = {"CODEX_AGENT_MODE": self.mode, "CODEX_AGENT_ROLE": self.role}
        if self.seat is not None:
            values["CODEX_SEAT"] = self.seat
        if self.behavior_source is not None:
            values["CODEX_BEHAVIOR_SOURCE"] = self.behavior_source
        return values


CODEX_VERIFICATION_COMMANDS = (
    "coordination/bin/pipeline-python -m pytest "
    "tests/unit/test_imports_smoke.py "
    "tests/unit/test_protocol_mailbox.py "
    "tests/unit/test_status.py "
    "tests/unit/test_coordination_tooling.py "
    "tests/unit/test_ceremony_gates.py "
    "tests/unit/test_protocol_capacity.py "
    "tests/unit/test_protocol_doc_integrity.py "
    "tests/unit/test_protocol_prompt_sync.py "
    "tests/unit/test_codex_protocol_model.py "
    "tests/unit/test_model_families_config.py "
    "tests/unit/test_compact_pair_loop.py "
    "tests/unit/test_provider_surface_map.py "
    "tests/unit/test_harness_preflight.py "
    "tests/unit/test_codex_hook_lifecycle.py "
    "tests/unit/test_claude_task_connector.py "
    "tests/unit/test_codex_ledger_bridge.py -q",
    "coordination/bin/pipeline-python scripts/governance_verify_all.py",
)


def infer_runtime_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return closed identity plus policy derived solely from that identity."""
    identity = RuntimeIdentity.from_environ(environ)
    mode = identity.mode
    role = identity.role
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
        "readiness-bridge": "native-worktree-index-read-only",
        "live-seat": "native-worktree-index",
        "coordinator": "native-worktree-index",
        "subagent": "native-worktree-index-parent-scoped",
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
    return {
        "CODEX_AGENT_MODE": mode,
        "CODEX_AGENT_ROLE": role,
        "CODEX_SEAT": identity.seat or "(unset)",
        "CODEX_BEHAVIOR_SOURCE": identity.behavior_source or "(none)",
        "CODEX_CAPABILITY_MODE": capability_defaults[mode],
        "CODEX_MUTATION_SCOPE": mutation_defaults.get(role, mutation_defaults[mode]),
        "CODEX_AUTHORITY_SCOPE": authority_defaults[mode],
        "CODEX_MAILBOX_POLICY": mailbox_defaults[mode],
        "CODEX_GIT_POLICY": git_defaults[mode],
        "CODEX_VERIFICATION_POLICY": verification_default,
        "CODEX_CONTEXT_SOURCES": context_defaults[mode],
        "CODEX_OUTPUT_CONTRACT": output_defaults[mode],
        "CODEX_DECISION_BOUNDARY": decision_defaults[mode],
        "CODEX_NEXT_ACTION_POLICY": next_action_defaults[mode],
        "CODEX_SIDE_EFFECT_POLICY": "user-consent-required",
    }


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
    return "\n".join(
        (
            "Seat contract:",
            f"S-ROLE: {role_value}",
            f"S-OBJ: {objective}",
            f"S-PERM: {permissions}",
            f"S-SCOPE: {scope}",
            f"S-VERIFY: {verification}",
            f"S-DONE: {done}",
            "source order: user > git > current durable events > defaults",
            "side effects: push, merge, lock, paid API spend, and pod spend are separately gated and require user consent",
        )
    )


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
    takeover_confirmations: tuple[protocol_mailbox.TakeoverConfirmationStatement, ...] = ()


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
        and all(protocol_mailbox.immutable_reference_is_canonical(value) for value in values)
    )


def _canonical_seats(values: tuple[str, ...]) -> bool:
    return (
        isinstance(values, tuple)
        and bool(values)
        and len(values) == len(set(values))
        and all(value in protocol_mailbox.RECEIVING_SEATS for value in values)
    )


def _nonblank_tuple(values: tuple[str, ...]) -> bool:
    return isinstance(values, tuple) and bool(values) and all(_nonblank(value) for value in values)


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
    if not _nonblank(task_id) or not protocol_mailbox.immutable_reference_is_canonical(contract_ref):
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
        task_id=task_id.strip(), contract_ref=contract_ref, parent_ref=parent_ref,
        revision=revision, outcome=outcome.strip(), owners=owners,
        evidence_bar=evidence_bar, hard_boundaries=hard_boundaries,
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
    contract: OutcomeContract, change: OwnershipChange, root: os.PathLike[str] | str
) -> bool:
    proposal = change.proposal
    if proposal is None or change.takeover_evidence is not None or change.takeover_confirmations:
        return False
    try:
        committed_proposal = protocol_mailbox.load_ownership_proposal_statement(root, proposal.event.ref)
    except (OSError, ValueError):
        return False
    if committed_proposal != proposal:
        return False
    expected_outcome = change.outcome or contract.outcome
    if not (
        proposal.event.sender in contract.owners and proposal.task_id == contract.task_id
        and proposal.parent_ref == contract.contract_ref and proposal.revision == change.revision
        and proposal.previous_owners == contract.owners and proposal.proposed_owners == change.new_owners
        and proposal.outcome == expected_outcome and proposal.finding_refs == contract.finding_refs
    ):
        return False
    required_acceptors = set(change.new_owners)
    if {acceptance.event.sender for acceptance in change.acceptances} != required_acceptors:
        return False
    if len(change.acceptances) != len(required_acceptors):
        return False
    for acceptance in change.acceptances:
        try:
            committed_acceptance = protocol_mailbox.load_ownership_acceptance_statement(root, acceptance.event.ref)
        except (OSError, ValueError):
            return False
        if committed_acceptance != acceptance:
            return False
        if not (
            acceptance.event.sender in required_acceptors and acceptance.task_id == contract.task_id
            and acceptance.parent_ref == contract.contract_ref and acceptance.revision == change.revision
            and acceptance.previous_owners == contract.owners and acceptance.proposed_owners == change.new_owners
            and acceptance.proposal_ref == proposal.event.ref and acceptance.outcome == expected_outcome
            and acceptance.finding_refs == contract.finding_refs
        ):
            return False
    return True


def _abandoned_takeover_is_effective(
    contract: OutcomeContract, change: OwnershipChange, root: os.PathLike[str] | str
) -> bool:
    evidence = change.takeover_evidence
    if (
        change.proposal is not None or change.acceptances or evidence is None
        or len(change.new_owners) != 1 or change.new_owners[0] in contract.owners
        or change.outcome is not None or len(change.takeover_confirmations) != 1
    ):
        return False
    confirmation = change.takeover_confirmations[0]
    try:
        committed_evidence = protocol_mailbox.load_takeover_evidence_statement(root, evidence.event.ref)
        committed_confirmation = protocol_mailbox.load_takeover_confirmation_statement(root, confirmation.event.ref)
    except (OSError, ValueError):
        return False
    if committed_evidence != evidence or committed_confirmation != confirmation:
        return False
    claimant = change.new_owners[0]
    corroborator = confirmation.event.sender
    return bool(
        evidence.event.sender == claimant and evidence.task_id == contract.task_id
        and evidence.parent_ref == contract.contract_ref and evidence.revision == change.revision
        and evidence.finding_refs == contract.finding_refs
        and evidence.fresh_work_state.casefold() == "no fresh work"
        and evidence.lock_state.casefold() == "no active lock" and corroborator in SEATS
        and corroborator != claimant and confirmation.event.recipient == claimant
        and confirmation.task_id == contract.task_id and confirmation.parent_ref == contract.contract_ref
        and confirmation.revision == change.revision and confirmation.proposed_owner == claimant
        and confirmation.takeover_claim_ref == evidence.event.ref
        and confirmation.observed_at == evidence.observed_at
        and confirmation.finding_refs == contract.finding_refs
        and protocol_mailbox.committed_event_is_strict_ancestor(root, evidence.event, confirmation.event)
        and confirmation.event.when >= evidence.event.when and confirmation.event.when >= evidence.observed_at
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
        contract, contract_ref=successor_ref, parent_ref=contract.contract_ref,
        revision=change.revision, outcome=change.outcome or contract.outcome,
        owners=change.new_owners,
    )


def external_effect_token_is_complete(token: ExternalEffectToken) -> ExternalEffectTokenResult:
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
