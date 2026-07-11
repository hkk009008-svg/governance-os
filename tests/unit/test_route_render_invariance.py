"""Prose formatting must never change route authority (ADR-014).

Mutations run on the RENDERED projection only — the sidecar object is the
authority, so every benign mutant must (a) leave read_manifest output
byte-identical and (b) still satisfy the legacy validator. A mutation that
destroys the hash pin must fail CLOSED (RouteManifestError), never silently.
"""
from __future__ import annotations

import re
from pathlib import Path

import protocol_capacity
import pytest

import route_manifest
from test_route_manifest import _route
from test_route_render import NARRATIVE, _write_packets


def _pair(tmp_path: Path) -> Path:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    md_path, _ = route_manifest.write_route_pair(
        sent, _route(), title="Coordinator → All: Invariance Fixture", narrative=NARRATIVE
    )
    return md_path


def _swap_bullets(body: str) -> str:
    return re.sub(r"(?m)^- ", "* ", body)


def _deepen_headings(body: str) -> str:
    return re.sub(r"(?m)^## ", "### ", body)


def _pad_blank_lines(body: str) -> str:
    return body.replace("\n\n", "\n\n\n")


def _add_trailing_whitespace(body: str) -> str:
    return "\n".join(line + "  " if line else line for line in body.splitlines()) + "\n"


BENIGN_MUTATIONS = [
    ("bullet-style", _swap_bullets),
    ("heading-depth", _deepen_headings),
    ("blank-padding", _pad_blank_lines),
    ("trailing-whitespace", _add_trailing_whitespace),
]


@pytest.mark.parametrize("name,mutate", BENIGN_MUTATIONS)
def test_benign_mutation_never_changes_authority(tmp_path, name, mutate):
    md_path = _pair(tmp_path)
    original = route_manifest.read_manifest(md_path)
    md_path.write_text(mutate(md_path.read_text(encoding="utf-8")), encoding="utf-8")
    assert route_manifest.read_manifest(md_path) == original


@pytest.mark.parametrize("name,mutate", BENIGN_MUTATIONS)
def test_benign_mutation_keeps_legacy_verdict(tmp_path, name, mutate):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path)
    md_path.write_text(mutate(md_path.read_text(encoding="utf-8")), encoding="utf-8")
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, (name, result.to_dict())


def test_narrative_variants_share_one_hash(tmp_path):
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    md_a, _ = route_manifest.write_route_pair(
        sent, _route(), title="A", narrative=(("Note", "one line"),)
    )
    hash_a = route_manifest.HASH_LINE_RE.search(md_a.read_text(encoding="utf-8"))
    md_a.unlink()
    md_b, _ = route_manifest.write_route_pair(
        sent, _route(), title="A", narrative=(("Note", "a\nvery\nwrapped\nparagraph"),)
    )
    hash_b = route_manifest.HASH_LINE_RE.search(md_b.read_text(encoding="utf-8"))
    assert hash_a.group("digest") == hash_b.group("digest")


def test_destroyed_hash_pin_fails_closed(tmp_path):
    md_path = _pair(tmp_path)
    body = md_path.read_text(encoding="utf-8")
    md_path.write_text(
        route_manifest.HASH_LINE_RE.sub("route_hash: (redacted)", body), encoding="utf-8"
    )
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Legacy per-line negation defect (protocol_capacity.py:1396-1448): a "
        "prohibition wrapped across lines is misread as a side-effect request. "
        "Not fixed in the prose parser by design — route/v1 typed prohibitions "
        "are the fix (ADR-014). Pinned per R-VERIFY-TIER; an XPASS means the "
        "legacy parser changed and this pin plus the route-compat expected.json "
        "row must be revisited together."
    ),
)
def test_legacy_validator_should_tolerate_wrapped_prohibition(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path)
    body = md_path.read_text(encoding="utf-8")
    wrapped = body.replace(
        "- No push or remote-ref update by any seat in this cycle.",
        "- No seat may execute a\n  push or remote-ref update in this cycle.",
    )
    assert wrapped != body
    md_path.write_text(wrapped, encoding="utf-8")
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()
