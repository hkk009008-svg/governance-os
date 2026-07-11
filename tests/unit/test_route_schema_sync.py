"""schemas/route-v1.schema.json must never drift from the enforcing validator."""
from __future__ import annotations

import json
from pathlib import Path

import route_manifest


def _schema() -> dict:
    path = Path(__file__).resolve().parent.parent.parent / "schemas" / "route-v1.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_id_matches_module():
    assert _schema()["$id"] == route_manifest.SCHEMA_ID


def test_required_fields_match_module():
    assert tuple(_schema()["required"]) == route_manifest.REQUIRED_FIELDS


def test_properties_cover_required_plus_optional_only():
    props = set(_schema()["properties"])
    assert props == set(route_manifest.REQUIRED_FIELDS) | set(route_manifest.OPTIONAL_FIELDS)


def test_schema_rejects_unknown_fields():
    assert _schema()["additionalProperties"] is False


def test_prohibition_enum_matches_vocab():
    enum = _schema()["properties"]["prohibitions"]["items"]["enum"]
    assert set(enum) == set(route_manifest.PROHIBITION_VOCAB)


def test_token_fields_match_module():
    token = _schema()["properties"]["side_effect_token"]
    assert tuple(token["required"]) == route_manifest.SIDE_EFFECT_TOKEN_FIELDS
    assert set(token["properties"]) == set(route_manifest.SIDE_EFFECT_TOKEN_FIELDS)


def test_seat_enums_match_module():
    schema = _schema()
    assert tuple(schema["properties"]["created_by"]["enum"]) == route_manifest.KNOWN_SEATS
    assert (
        tuple(schema["properties"]["side_effect_token"]["properties"]["executor"]["enum"])
        == route_manifest.KNOWN_SEATS
    )
