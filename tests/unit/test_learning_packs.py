"""Frozen retrieval packs: expected hits surface, decoys stay out (Stage 5).

Each pack under tests/learning_packs/ is a self-contained fixture repo spec.
Packs are frozen: a wrong expectation is superseded by a new pack file, never
edited in place, so retrieval regressions cannot be silenced by moving the
goalposts in the same diff that caused them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import learning_index  # noqa: E402

_PACK_DIR = _REPO_ROOT / "tests" / "learning_packs"
_PACKS = sorted(_PACK_DIR.glob("pack-*.json"))


def _build_pack_repo(tmp_path: Path, spec: dict) -> Path:
    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    for relative, content in spec["files"].items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", f"pack: {spec['name']}")
    return root


def test_at_least_one_pack_exists() -> None:
    assert _PACKS, "Stage 5 requires at least one frozen retrieval pack"


@pytest.mark.parametrize("pack_path", _PACKS, ids=lambda p: p.stem)
def test_pack_expected_hits_surface_and_decoys_stay_out(
    pack_path: Path, tmp_path: Path
) -> None:
    spec = json.loads(pack_path.read_text(encoding="utf-8"))
    root = _build_pack_repo(tmp_path, spec)
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    for query in spec["queries"]:
        rows = learning_index.query_index(
            root, query["terms"], limit=50, db_path=db
        )
        assert rows is not None, "pack index must be available after build"
        paths = {row.path for row in rows}
        missing = set(query["expect"]) - paths
        assert missing == set(), (
            f"{pack_path.name} query {query['terms']!r} missed {missing}"
        )
        leaked = set(query["decoys"]) & paths
        assert leaked == set(), (
            f"{pack_path.name} query {query['terms']!r} surfaced decoys {leaked}"
        )
