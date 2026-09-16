#!/usr/bin/env python3
"""Risk classes and model-family checks for formal review."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


MODEL_HARNESS_PREFIXES = ("codex-", "claude-code-")
MODEL_FAMILIES_CONFIG = (
    Path(__file__).resolve().parent.parent / "config/model-families.toml"
)
MEMBER_MODEL_FAMILIES = {"codex": "gpt", "claude": "claude", "agy": "gemini"}


@dataclass(frozen=True)
class ReviewProfile:
    risk_class: str
    focused_verification: bool
    requires_non_author_review: bool
    requires_exact_range: bool
    requires_different_model: bool
    requires_abuse_class_assessment: bool
    requires_live_authorization: bool


RISK_BASED_REVIEW_PROFILES = {
    "ordinary-local": ReviewProfile(
        "ordinary-local", True, False, False, False, False, False
    ),
    "material-behavior": ReviewProfile(
        "material-behavior", True, True, True, False, False, False
    ),
    "high-risk-control": ReviewProfile(
        "high-risk-control", True, True, True, True, True, False
    ),
    "external-effect": ReviewProfile(
        "external-effect", False, False, False, False, False, True
    ),
}


def review_profile_for(risk_class: str) -> ReviewProfile:
    try:
        return RISK_BASED_REVIEW_PROFILES[risk_class]
    except KeyError as exc:
        raise ValueError(f"unknown review risk class: {risk_class}") from exc


def _load_config(config_path: Path) -> dict[str, object]:
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"model-family configuration unavailable: {exc}") from exc
    if payload.get("schema_version") != 1:
        raise RuntimeError("model-families schema_version must be 1")
    return payload


def load_model_families(
    config_path: Path = MODEL_FAMILIES_CONFIG,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    payload = _load_config(config_path)
    tables: list[dict[str, str]] = []
    for key in ("provider_prefixes", "families", "display_aliases"):
        value = payload.get(key)
        if not isinstance(value, dict) or not value or not all(
            isinstance(name, str)
            and name
            and isinstance(family, str)
            and family
            for name, family in value.items()
        ):
            raise RuntimeError(f"model-families [{key}] must be a nonempty string table")
        tables.append(dict(value))
    prefixes, families, aliases = tables
    known_families = set(prefixes.values())
    if unknown := set(families.values()) - known_families:
        raise RuntimeError(f"model IDs use unknown families: {sorted(unknown)}")
    if unknown_aliases := set(aliases.values()) - set(families):
        raise RuntimeError(
            f"display aliases target unknown model IDs: {sorted(unknown_aliases)}"
        )
    return prefixes, families, aliases


def load_family_prefixes(config_path: Path = MODEL_FAMILIES_CONFIG) -> dict[str, str]:
    """Name prefixes that admit an unregistered point release as an author."""
    payload = _load_config(config_path)
    prefixes = payload.get("provider_prefixes")
    value = payload.get("family_prefixes")
    if not isinstance(prefixes, dict) or not isinstance(value, dict) or not value:
        raise RuntimeError("model-families [family_prefixes] must be a nonempty table")
    known = set(prefixes.values())
    for prefix, family in value.items():
        if (
            not isinstance(prefix, str) or len(prefix) < 2 or not prefix.endswith("-")
            or prefix != prefix.casefold() or family not in known
        ):
            raise RuntimeError(
                "model-families [family_prefixes] entries must map a lowercase "
                "'<name>-' prefix to a known family"
            )
    return dict(value)


def load_review_admission(
    config_path: Path = MODEL_FAMILIES_CONFIG,
) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    payload = _load_config(config_path)
    admission = payload.get("review_admission")
    families = payload.get("families")
    prefixes = payload.get("provider_prefixes")
    if not isinstance(admission, dict) or not isinstance(families, dict) or not isinstance(prefixes, dict):
        raise RuntimeError("model-families review tables are required")

    def unique_strings(key: str) -> frozenset[str]:
        value = admission.get(key)
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item for item in value)
            or len(value) != len(set(value))
        ):
            raise RuntimeError(f"review_admission.{key} must be a unique nonempty list")
        return frozenset(value)

    active_families = unique_strings("active_families")
    authors = unique_strings("active_author_models")
    reviewers = unique_strings("active_reviewer_models")
    if not active_families <= set(prefixes.values()):
        raise RuntimeError("active review families must have provider prefixes")
    if not authors <= set(families):
        raise RuntimeError("active author models must be registered model IDs")
    if not reviewers <= authors:
        raise RuntimeError("active reviewer models must also be active authors")
    if {families[model] for model in reviewers} != set(active_families):
        raise RuntimeError("reviewer models must cover exactly the active families")
    return active_families, authors, reviewers


MODEL_PROVIDER_FAMILIES, MODEL_ID_REGISTRY, MODEL_DISPLAY_ALIASES = (
    load_model_families()
)
MODEL_FAMILY_PREFIXES = load_family_prefixes()
CURRENT_REVIEW_FAMILIES, CURRENT_AUTHOR_MODEL_IDS, CURRENT_REVIEWER_MODEL_IDS = (
    load_review_admission()
)
# Families that have at least one active author; an unregistered point release
# of one of them may author. Reviewers are always exact IDs.
CURRENT_AUTHOR_FAMILIES = frozenset(
    MODEL_ID_REGISTRY[model] for model in CURRENT_AUTHOR_MODEL_IDS
)


def _normalize(model_id: str) -> tuple[str, str | None] | None:
    """Return (token, provider family or None) after alias and prefix stripping."""
    if not model_id or model_id != model_id.strip():
        return None
    token = MODEL_DISPLAY_ALIASES.get(model_id, model_id.casefold())
    changed = True
    while changed:
        changed = False
        for prefix in MODEL_HARNESS_PREFIXES:
            if token.startswith(prefix) and len(token) > len(prefix):
                token = token[len(prefix) :]
                changed = True
                break
    provider_family = None
    for prefix, family in MODEL_PROVIDER_FAMILIES.items():
        if token.startswith(prefix) and len(token) > len(prefix):
            provider_family = family
            token = token[len(prefix) :]
            break
    return token, provider_family


def _model_record(model_id: str) -> tuple[str, str] | None:
    """Exact registry record, or None for unknown, malformed, or conflicting IDs."""
    normalized = _normalize(model_id)
    if normalized is None:
        return None
    token, provider_family = normalized
    family = MODEL_ID_REGISTRY.get(token)
    if family is None or (provider_family is not None and provider_family != family):
        return None
    return token, family


def _prefix_family(model_id: str) -> str | None:
    """Family of an unregistered ID by name prefix; None when registered or unknown.

    Registered tokens are refused here as well as by the exact-record check
    in the callers, so a retired registry entry stays retired even if one of
    the two guards were bypassed. Author admission is the only consumer that
    grants anything, and an author grants nothing: repository bytes could
    always name any admitted ID, so exact author matching only ever caught
    typos and new releases.
    """
    normalized = _normalize(model_id)
    if normalized is None:
        return None
    token, provider_family = normalized
    if token in MODEL_ID_REGISTRY:
        return None
    for prefix, family in MODEL_FAMILY_PREFIXES.items():
        if token.startswith(prefix) and len(token) > len(prefix):
            if provider_family is not None and provider_family != family:
                return None
            return family
    return None


def model_family(model_id: str) -> str | None:
    record = _model_record(model_id)
    return record[1] if record else _prefix_family(model_id)


def model_family_matches_member(model_id: str, member: str) -> bool:
    return model_family(model_id) == MEMBER_MODEL_FAMILIES.get(member)


def models_are_independent(author_model: str, reviewer_model: str) -> bool:
    author = model_family(author_model)
    reviewer = model_family(reviewer_model)
    return author is not None and reviewer is not None and author != reviewer


def model_is_current_author(model_id: str) -> bool:
    record = _model_record(model_id)
    if record:
        return record[0] in CURRENT_AUTHOR_MODEL_IDS
    return _prefix_family(model_id) in CURRENT_AUTHOR_FAMILIES


def model_is_current_reviewer(model_id: str) -> bool:
    record = _model_record(model_id)
    return bool(record and record[0] in CURRENT_REVIEWER_MODEL_IDS)


def models_are_current_review_pair(author_model: str, reviewer_model: str) -> bool:
    reviewer = _model_record(reviewer_model)
    author_family = model_family(author_model)
    return bool(
        reviewer
        and author_family is not None
        and model_is_current_author(author_model)
        and reviewer[0] in CURRENT_REVIEWER_MODEL_IDS
        and reviewer[1] in CURRENT_REVIEW_FAMILIES
        and author_family != reviewer[1]
    )
