"""Flat imports are the one convention for scripts/ modules.

With both the repository root and scripts/ on sys.path, ``import X`` and
``from scripts import X`` load two distinct module objects for the same
file. Exception classes then differ by identity — an ``AppBindingError``
raised by the flat copy is not caught by an ``except`` clause holding the
package copy — and monkeypatches land on only one of the twins. The
convention is flat everywhere (modules and tests); this scan makes the
package form a CI failure instead of a latent identity bug.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_PACKAGE_FORM = re.compile(r"^\s*(?:from scripts[.\s]|import scripts\b)", re.MULTILINE)


def test_no_package_form_imports_of_scripts_modules() -> None:
    offenders: list[str] = []
    for base in ("scripts", "tests"):
        for path in sorted((ROOT / base).rglob("*.py")):
            if _PACKAGE_FORM.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
