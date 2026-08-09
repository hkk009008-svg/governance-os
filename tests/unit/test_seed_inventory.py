from __future__ import annotations

from pathlib import Path

import pytest

import seed_inventory


def test_malformed_test_file_fails_inventory_instead_of_disappearing(
    tmp_path: Path,
) -> None:
    test_file = tmp_path / "test_broken.py"
    test_file.write_text("def broken(:\n", encoding="utf-8")

    with pytest.raises(seed_inventory.InventoryParseError, match="test_broken.py"):
        seed_inventory.find_xfail_pins(tmp_path)


@pytest.mark.parametrize(
    "mark",
    (
        "pytest.mark.xfail(reason=reason, strict=True)",
        "pytest.mark.xfail(reason='known', strict=strict_mode)",
    ),
)
def test_dynamic_xfail_metadata_fails_closed(tmp_path: Path, mark: str) -> None:
    test_file = tmp_path / "test_dynamic.py"
    test_file.write_text(
        "import pytest\nreason = 'dynamic'\nstrict_mode = True\n"
        f"@{mark}\ndef test_case():\n    pass\n",
        encoding="utf-8",
    )

    with pytest.raises(seed_inventory.InventoryParseError, match="literal"):
        seed_inventory.find_xfail_pins(tmp_path)


def test_dynamic_xfail_kwargs_fail_closed(tmp_path: Path) -> None:
    test_file = tmp_path / "test_dynamic_kwargs.py"
    test_file.write_text(
        "import pytest\n"
        "opts = {'reason': 'dynamic', 'strict': True}\n"
        "@pytest.mark.xfail(**opts)\n"
        "def test_case():\n"
        "    pass\n",
        encoding="utf-8",
    )

    with pytest.raises(seed_inventory.InventoryParseError, match=r"dynamic \*\*kwargs"):
        seed_inventory.find_xfail_pins(tmp_path)
