"""The coordination transport is declarative and fails closed."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import bus_unread  # noqa: E402


def test_this_repository_declares_the_mailbox_transport() -> None:
    assert bus_unread.coordination_transport(_REPO_ROOT) == "mailbox"


@pytest.mark.parametrize(
    "content",
    ["{not toml", '[coordination]\ntransport = "carrier-pigeon"\n'],
    ids=["unparsable", "unknown-value"],
)
def test_corrupted_transport_declaration_fails_closed(
    tmp_path: Path, content: str
) -> None:
    (tmp_path / "governance.toml").write_text(content, encoding="utf-8")
    with pytest.raises(RuntimeError):
        bus_unread.coordination_transport(tmp_path)


@pytest.mark.parametrize(
    "content",
    [None, "[coordination]\n", "[kernel]\n"],
    ids=["missing-file", "missing-key", "missing-table"],
)
def test_omission_defaults_to_mailbox_and_never_activates_the_bus(
    tmp_path: Path, content: str | None
) -> None:
    if content is not None:
        (tmp_path / "governance.toml").write_text(content, encoding="utf-8")
    assert bus_unread.coordination_transport(tmp_path) == "mailbox"


def test_mailbox_transport_never_consults_the_signed_bus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Evasion control: poison the package; the short-circuit must not import it.

    With transport=mailbox the probe returns 'absent' before any threeway
    import. If the gate were removed (or moved after the import), the
    poisoned module would raise and this test would fail.
    """
    (tmp_path / "governance.toml").write_text(
        '[coordination]\ntransport = "mailbox"\n', encoding="utf-8"
    )
    monkeypatch.setitem(sys.modules, "threeway", None)
    monkeypatch.setitem(sys.modules, "threeway.gitcas", None)
    authority = bus_unread.bus_authority_state(tmp_path, "operator")
    assert authority.state == "absent"
    assert "explicitly 'mailbox'" in authority.detail

    resolution = bus_unread.resolve_unread(
        tmp_path,
        "operator",
        "1",
        [
            "2026-08-01T00-00-00Z-director-to-operator-findings.md",
            "2026-08-02T00-00-00Z-director-to-operator-findings.md",
        ],
    )
    assert resolution.source == "mailbox-fallback"
    assert resolution.transport == "absent"
