"""The review-history boundary manifest is the single fail-closed source."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import check_coordination  # noqa: E402


def test_manifest_is_the_loaded_boundary() -> None:
    """Migration equality: loaded constants equal the manifest bytes."""
    payload = json.loads(
        (_REPO_ROOT / "pipeline/baselines/review_history_boundary.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["schema_version"] == 1
    assert (
        check_coordination._REVIEW_STATE_CUTOVER_PATH
        == payload["review_state_cutover"]["path"]
    )
    assert (
        check_coordination._REVIEW_STATE_CUTOVER_COMMIT
        == payload["review_state_cutover"]["commit"]
    )
    assert (
        check_coordination._ACTIVE_FAILURE_CUTOVER_COMMIT
        == payload["active_failure_cutover_commit"]
    )
    assert (
        check_coordination._LEARNING_HISTORY_CUTOVER_COMMIT
        == payload["learning_history_cutover_commit"]
    )
    assert check_coordination._BASELINE_ACTIVE_FAILURE_REPORTS == frozenset(
        payload["baseline_active_failure_reports"]
    )
    assert check_coordination._PRE_CUTOVER_INVALID_REQUESTS == {
        tuple(ref.rsplit("@", 1)): digest
        for ref, digest in payload["pre_cutover_invalid_requests"].items()
    }
    # The frozen exception manifest it names must exist and stay distinct.
    # The manifest declares itself one-way ("never edit in place"), so its
    # reference still carries the pre-rename scripts/ prefix; the projection
    # normalizes that reference rather than rewriting frozen provenance.
    frozen = _REPO_ROOT / check_coordination._normalize_archive_name(
        payload["frozen_exception_manifest"]
    )
    assert frozen.is_file()
    assert frozen.name != "review_history_boundary.json"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda p: p.unlink(),
        lambda p: p.write_text("{not json", encoding="utf-8"),
        lambda p: p.write_text(json.dumps({"schema_version": 2}), encoding="utf-8"),
        lambda p: p.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "review_state_cutover": {"path": "elsewhere.md", "commit": "zz"},
                }
            ),
            encoding="utf-8",
        ),
    ],
    ids=["missing", "unparsable", "wrong-version", "malformed-shape"],
)
def test_loader_fails_closed(tmp_path: Path, mutate) -> None:
    manifest = tmp_path / "review_history_boundary.json"
    manifest.write_text(
        (_REPO_ROOT / "pipeline/baselines/review_history_boundary.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    mutate(manifest)
    with pytest.raises(RuntimeError):
        check_coordination.load_review_history_boundary(manifest)


def test_boundary_shas_live_only_in_baselines_not_in_adapter_prose() -> None:
    """The continuation adapter points at the manifest instead of pasting SHAs."""
    adapter = (_REPO_ROOT / "docs/protocol/codex/continuation.md").read_text(
        encoding="utf-8"
    )
    for sha in (
        "61786501e26f7e1bac92efbdcd4ff0ea468a7bbb",
        "8d05a76489b8609634e1635ebfad12792abc8119",
        "e0fbefdb56af03b8c04b6df58245f7533a3d83c0",
    ):
        assert sha not in adapter
    assert "pipeline/baselines/review_history_boundary.json" in adapter
