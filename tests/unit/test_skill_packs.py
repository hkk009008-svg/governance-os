"""Frozen skill-selection packs: expected skill wins; decoys lose; stubs route.

Each pack under tests/skill_packs/ is a frozen evaluation case. Packs are
grown, never edited in place — a wrong expectation is superseded by a new
pack file, so a description change cannot silence a selection regression in
the same diff that caused it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PACK_DIR = _REPO_ROOT / "tests" / "skill_packs"
_PACKS = sorted(_PACK_DIR.glob("pack-*.json"))
_SKILLS_DIR = _REPO_ROOT / ".agents" / "skills"
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FRONTMATTER_RE = re.compile(
    r"^---\n(?P<body>.*?)\n---\s*", re.DOTALL
)


def _tokens(text: str) -> set[str]:
    return {token for token in _TOKEN_RE.findall(text.casefold()) if len(token) >= 4}


def _frontmatter_field(text: str, field: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    assert match, "SKILL.md must start with YAML frontmatter"
    block = match.group("body")
    key = f"{field}:"
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith(key):
            value = stripped[len(key) :].strip()
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            return value
    raise AssertionError(f"frontmatter missing {field}:")


def _skill_descriptions() -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for skill_md in sorted(_SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        name = _frontmatter_field(text, "name").strip('"')
        descriptions[name] = _frontmatter_field(text, "description")
    return descriptions


def _score(description: str, trigger: str) -> int:
    return len(_tokens(description) & _tokens(trigger))


def test_at_least_one_pack_exists() -> None:
    assert _PACKS, "skill evaluation requires at least one frozen pack"


@pytest.mark.parametrize("pack_path", _PACKS, ids=lambda p: p.stem)
def test_pack_schema_and_frozen_kind(pack_path: Path) -> None:
    spec = json.loads(pack_path.read_text(encoding="utf-8"))
    assert spec["name"]
    assert spec["kind"] in {"selection", "stub-routing"}
    assert spec["cases"], f"{pack_path.name} has no cases"
    assert "never edited in place" in spec["comment"]


def test_selection_trigger_picks_expected_skill_over_decoys() -> None:
    descriptions = _skill_descriptions()
    for pack_path in _PACKS:
        spec = json.loads(pack_path.read_text(encoding="utf-8"))
        if spec["kind"] != "selection":
            continue
        for case in spec["cases"]:
            expect = case["expect"]
            trigger = case["trigger"]
            assert expect in descriptions, f"{case['id']}: missing skill {expect}"
            expected_score = _score(descriptions[expect], trigger)
            assert expected_score > 0, (
                f"{case['id']}: expected skill {expect} shares no 4+ char "
                f"tokens with trigger {trigger!r}"
            )
            for decoy in case["decoys"]:
                assert decoy in descriptions, f"{case['id']}: missing decoy {decoy}"
                decoy_score = _score(descriptions[decoy], trigger)
                assert expected_score > decoy_score, (
                    f"{case['id']}: decoy {decoy} scored {decoy_score} >= "
                    f"expected {expect} scored {expected_score} on {trigger!r}"
                )


def test_stub_routing_falsifier_reaches_canonical_body() -> None:
    """ADR-067: a committed Claude stub must point at a live .agents body."""

    descriptions = _skill_descriptions()
    seen = 0
    for pack_path in _PACKS:
        spec = json.loads(pack_path.read_text(encoding="utf-8"))
        if spec["kind"] != "stub-routing":
            continue
        for case in spec["cases"]:
            seen += 1
            skill = case["skill"]
            canonical = _REPO_ROOT / case["expect_canonical"]
            stub = _REPO_ROOT / case["expect_stub"]
            assert canonical.is_file(), f"{case['id']}: missing {canonical}"
            assert stub.is_file(), f"{case['id']}: missing {stub}"
            stub_text = stub.read_text(encoding="utf-8")
            assert "canonical body of this skill is" in stub_text.casefold(), (
                f"{case['id']}: stub is not a reference pointer"
            )
            assert case["expect_canonical"] in stub_text, (
                f"{case['id']}: stub does not name {case['expect_canonical']}"
            )
            # disable-model-invocation is the usual Claude stub marker;
            # chatgpt-pro-consultation is a reference stub without it.
            assert skill in descriptions, case["id"]
            assert _score(descriptions[skill], case["trigger"]) > 0, (
                f"{case['id']}: canonical description does not share tokens "
                f"with trigger {case['trigger']!r}"
            )
    assert seen >= 6, "the ADR-067 stub-routing falsifier must cover every stub"


def test_usage_counts_are_not_consumed_by_lifecycle_kernels() -> None:
    """Recorded rejection of usage-counts-as-lifecycle-evidence."""

    needles = ("skill-use", "skill_use", "skill_use_helped")
    for relative in (
        "scripts/mailbox_writer.py",
        "scripts/compact_pair_loop.py",
        "scripts/learning_extract.py",
        "scripts/learning_index.py",
        "scripts/protocol_mailbox.py",
    ):
        text = (_REPO_ROOT / relative).read_text(encoding="utf-8")
        for needle in needles:
            assert needle not in text, f"{relative} consumes {needle}"


def test_r_skill_names_this_repo_inventory() -> None:
    """R-SKILL lists real skills; the transfer TODO slot is closed here."""

    text = (_REPO_ROOT / "docs" / "PROTOCOL-RULES-LOG.md").read_text(
        encoding="utf-8"
    )
    assert "writing-skills" in text
    assert "add this project's domain-skill triggers" not in text
    assert "There is no domain-graph skill in this repository." in text
