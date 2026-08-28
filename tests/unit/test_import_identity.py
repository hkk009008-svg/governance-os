"""Flat imports are the one convention for pipeline/ modules.

With both the repository root and pipeline/ on sys.path, ``import X`` and
``from pipeline import X`` load two distinct module objects for the same
file. Exception classes then differ by identity — an ``AppBindingError``
raised by the flat copy is not caught by an ``except`` clause holding the
package copy — and monkeypatches land on only one of the twins. ``pipeline/``
carries no ``__init__.py``, so the package form resolves as an implicit
namespace package and succeeds silently; only this scan makes it a failure.

The pattern tracks the directory name. When ``scripts/`` became
``pipeline/`` the old pattern kept passing while guarding a directory that no
longer existed — a control that cannot fail proves nothing.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_PACKAGE_FORM = re.compile(r"^\s*(?:from pipeline[.\s]|import pipeline\b)", re.MULTILINE)


def test_no_package_form_imports_of_pipeline_modules() -> None:
    offenders: list[str] = []
    for base in ("pipeline", "tests"):
        for path in sorted((ROOT / base).rglob("*.py")):
            if _PACKAGE_FORM.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_the_scan_would_catch_a_real_package_import(tmp_path: Path) -> None:
    """Reversion control: the pattern must actually match the form it forbids."""

    for forbidden in (
        "from pipeline import status\n",
        "from pipeline.status import main\n",
        "import pipeline.status\n",
        "    import pipeline\n",
    ):
        assert _PACKAGE_FORM.search(forbidden), forbidden
    for allowed in ("import status\n", "from status import main\n", "import pipelines\n"):
        assert not _PACKAGE_FORM.search(allowed), allowed
