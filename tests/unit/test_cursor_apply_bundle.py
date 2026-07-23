from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import cursor_apply_bundle as bundle


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stage(root: Path, bundle_id: str, rel: str, data: bytes) -> None:
    tree = root / ".pytest-verify-tmp/cursor-bundles" / bundle_id / "tree"
    target = tree / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest = {
        "files": [{"path": rel, "sha256": _digest(data)}],
    }
    (tree.parent / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def test_dry_run_does_not_copy(tmp_path: Path) -> None:
    _stage(tmp_path, "demo", "scripts/sample.py", b"print(1)\n")
    code = bundle.apply_bundle(
        tmp_path,
        "demo",
        dry_run=True,
        environ={},
        stdin_isatty=False,
    )
    assert code == 0
    assert not (tmp_path / "scripts/sample.py").exists()


def test_apply_requires_yes_without_build_bind(tmp_path: Path) -> None:
    _stage(tmp_path, "demo", "scripts/sample.py", b"print(1)\n")
    with pytest.raises(bundle.BundleError, match="interactive"):
        bundle.apply_bundle(
            tmp_path,
            "demo",
            dry_run=False,
            environ={},
            stdin_isatty=False,
        )


def test_build_bind_skips_tty_and_copies(tmp_path: Path) -> None:
    _stage(tmp_path, "demo", "scripts/sample.py", b"print(1)\n")
    env = {
        "CURSOR_SEAT": "director",
        "CURSOR_OPERATION": "build",
        "GIT_INDEX_FILE": str(tmp_path / ".git/index-cursor-director"),
    }
    code = bundle.apply_bundle(
        tmp_path,
        "demo",
        dry_run=False,
        environ=env,
        stdin_isatty=False,
    )
    assert code == 0
    assert (tmp_path / "scripts/sample.py").read_bytes() == b"print(1)\n"


def test_rejects_forbidden_paths(tmp_path: Path) -> None:
    _stage(tmp_path, "demo", "scripts/agy_emit.py", b"x\n")
    with pytest.raises(bundle.BundleError, match="forbidden"):
        bundle.plan_copies(
            tmp_path,
            tmp_path / ".pytest-verify-tmp/cursor-bundles/demo",
            json.loads(
                (
                    tmp_path / ".pytest-verify-tmp/cursor-bundles/demo/manifest.json"
                ).read_text(encoding="utf-8")
            ),
        )


def test_rejects_junk_paths(tmp_path: Path) -> None:
    _stage(tmp_path, "demo", "scripts/__pycache__/x.pyc", b"x\n")
    with pytest.raises(bundle.BundleError, match="junk"):
        bundle.plan_copies(
            tmp_path,
            tmp_path / ".pytest-verify-tmp/cursor-bundles/demo",
            json.loads(
                (
                    tmp_path / ".pytest-verify-tmp/cursor-bundles/demo/manifest.json"
                ).read_text(encoding="utf-8")
            ),
        )

