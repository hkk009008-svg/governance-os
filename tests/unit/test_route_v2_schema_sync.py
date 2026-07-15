from __future__ import annotations

import json
from pathlib import Path

from scripts import capability_reducer as reducer


ROOT = Path(__file__).resolve().parents[2]


def test_schema_and_parser_contract_are_exactly_synchronized() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "route-v2.schema.json").read_text(encoding="utf-8")
    )

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == reducer.SCHEMA_ID
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert tuple(schema["required"]) == reducer.ENVELOPE_FIELDS
    assert schema["properties"] == reducer.field_schemas()

    first = reducer.field_schemas()
    second = reducer.field_schemas()
    assert first is not second
    assert first["evidence_refs"] is not second["evidence_refs"]
    assert first["evidence_refs"]["items"] is not second["evidence_refs"]["items"]

    first["evidence_refs"]["items"]["pattern"] = "mutated"
    first["requested_transition"]["enum"].append("MUTATED")
    assert reducer.field_schemas() == second
