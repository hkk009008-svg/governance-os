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
CURRENT_REVIEW_FAMILIES, CURRENT_AUTHOR_MODEL_IDS, CURRENT_REVIEWER_MODEL_IDS = (
    load_review_admission()
)


def _model_record(model_id: str) -> tuple[str, str] | None:
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
    family = MODEL_ID_REGISTRY.get(token)
    if family is None or (provider_family is not None and provider_family != family):
        return None
    return token, family


def model_family(model_id: str) -> str | None:
    record = _model_record(model_id)
    return record[1] if record else None


def model_family_matches_member(model_id: str, member: str) -> bool:
    return model_family(model_id) == MEMBER_MODEL_FAMILIES.get(member)


def models_are_independent(author_model: str, reviewer_model: str) -> bool:
    author = model_family(author_model)
    reviewer = model_family(reviewer_model)
    return author is not None and reviewer is not None and author != reviewer


def model_is_current_author(model_id: str) -> bool:
    record = _model_record(model_id)
    return bool(record and record[0] in CURRENT_AUTHOR_MODEL_IDS)


def model_is_current_reviewer(model_id: str) -> bool:
    record = _model_record(model_id)
    return bool(record and record[0] in CURRENT_REVIEWER_MODEL_IDS)


def models_are_current_review_pair(author_model: str, reviewer_model: str) -> bool:
    author = _model_record(author_model)
    reviewer = _model_record(reviewer_model)
    return bool(
        author
        and reviewer
        and author[0] in CURRENT_AUTHOR_MODEL_IDS
        and reviewer[0] in CURRENT_REVIEWER_MODEL_IDS
        and reviewer[1] in CURRENT_REVIEW_FAMILIES
        and author[1] != reviewer[1]
    )
