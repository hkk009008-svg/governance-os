"""The checker registry is a control: its map must name real things."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import governance_verify_all  # noqa: E402


def test_registry_entries_and_owned_paths_exist() -> None:
    registry = governance_verify_all.CHECKER_REGISTRY
    assert registry, "registry must not be empty"
    for name, entry in registry.items():
        assert (_REPO_ROOT / entry["entry"]).is_file(), (name, entry["entry"])
        assert entry["owned_paths"], name
        for owned in entry["owned_paths"]:
            assert (_REPO_ROOT / owned).exists(), (name, owned)
        for field in ("trigger", "severity", "blocked_effect"):
            assert entry[field].strip(), (name, field)


def test_registry_covers_every_rendered_gate() -> None:
    """A gate that prints in the aggregate must be routable by the registry.

    Keyed on the aggregate's own output vocabulary so adding a gate without a
    registry row fails here rather than silently widening the unmapped set.
    """
    source = (_REPO_ROOT / "scripts/governance_verify_all.py").read_text(
        encoding="utf-8"
    )
    rendered_gates = {
        "PLACEHOLDER CHECK": "placeholders",
        "GO-SCHEMA CHECK": "go_schema",
        "ARCH-FRESHNESS CHECK": "arch_freshness",
        "PROJECT SMOKE": "project_smoke",
    }
    for marker, registry_key in rendered_gates.items():
        assert marker in source, marker
        assert registry_key in governance_verify_all.CHECKER_REGISTRY, registry_key


def test_no_deprecated_alias_survives() -> None:
    """The ci_smoke alias is gone; one aggregate has one name."""
    import importlib.util

    assert importlib.util.find_spec("ci_smoke") is None
