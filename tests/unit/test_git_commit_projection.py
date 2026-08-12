from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import compact_pair_loop
import git_commit_projection as projection_module


def _git(root: Path, *arguments: str, input_text: str | None = None) -> str:
    return subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", *arguments],
        cwd=root,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
        env={
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "HOME": "/var/empty",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        },
    ).stdout.strip()


def _repo(path: Path) -> tuple[Path, str]:
    path.mkdir()
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "projection@example.invalid")
    _git(path, "config", "user.name", "Projection Test")
    (path / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(path, "add", "tracked.txt")
    _git(path, "commit", "-q", "-m", "base")
    return path, _git(path, "rev-parse", "HEAD")


def _commit(root: Path, message: str, content: str) -> str:
    (root / "tracked.txt").write_text(content, encoding="utf-8")
    _git(root, "add", "tracked.txt")
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def test_projection_matches_git_for_merge_unrelated_and_object_shapes(
    tmp_path: Path,
) -> None:
    root, base = _repo(tmp_path / "repo")
    _git(root, "checkout", "-q", "-b", "side")
    (root / "side.txt").write_text("side\n", encoding="utf-8")
    _git(root, "add", "side.txt")
    _git(root, "commit", "-q", "-m", "side")
    side = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "-q", "main")
    main = _commit(root, "main", "main\n")
    _git(root, "merge", "-q", "--no-ff", "-m", "merge", "side")
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    unrelated = _git(root, "commit-tree", tree, input_text="unrelated\n")
    blob = _git(root, "hash-object", "-w", "--stdin", input_text="blob\n")
    missing = "f" * 40

    projection = projection_module.CommitGraphProjection.build(
        root, {base, side, main, head, unrelated, blob, missing}
    )

    assert projection.head == head
    assert projection.require_commit(head, "head") == head
    assert projection.is_ancestor(base, head)
    assert projection.is_ancestor(side, head)
    assert projection.is_ancestor(main, head)
    assert not projection.is_ancestor(unrelated, head)
    assert base in projection.ancestors_of("HEAD")
    for invalid in (missing, blob, head[:12], head.upper(), f"g{head[1:]}"):
        with pytest.raises(projection_module.CommitGraphProjectionError):
            projection.require_commit(invalid, "candidate")


def test_projection_scrubs_hostile_git_environment_and_replace_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base = _repo(tmp_path / "repo")
    head = _commit(root, "head", "head\n")
    replacement = _git(
        root,
        "commit-tree",
        _git(root, "rev-parse", "HEAD^{tree}"),
        input_text="replacement without parent\n",
    )
    subprocess.run(
        ["/usr/bin/git", "replace", head, replacement],
        cwd=root,
        check=True,
        capture_output=True,
    )
    for name, value in {
        "GIT_DIR": "/missing/git-dir",
        "GIT_WORK_TREE": "/missing/work-tree",
        "GIT_OBJECT_DIRECTORY": "/missing/objects",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
        "GIT_CONFIG_VALUE_0": "999",
        "LC_ALL": "hostile_LOCALE",
    }.items():
        monkeypatch.setenv(name, value)

    projection = projection_module.CommitGraphProjection.build(root, {base, head})

    assert projection.head == head
    assert projection.is_ancestor(base, head)


def test_projection_detects_head_change_and_is_not_reused(tmp_path: Path) -> None:
    root, base = _repo(tmp_path / "repo")
    first = projection_module.CommitGraphProjection.build(root, {base})
    changed = _commit(root, "changed", "changed\n")

    with pytest.raises(
        projection_module.CommitGraphProjectionError,
        match="identity changed",
    ):
        first.assert_current()

    second = projection_module.CommitGraphProjection.build(root, {base, changed})
    assert second.head == changed
    assert second.head != first.head


def test_cross_repository_candidate_can_use_explicit_git_fallback(
    tmp_path: Path,
) -> None:
    first_root, first_head = _repo(tmp_path / "first")
    second_root, second_head = _repo(tmp_path / "second")
    projection = projection_module.CommitGraphProjection.build(
        first_root, {first_head}
    )

    assert compact_pair_loop._full_commit(
        second_root,
        second_head,
        "candidate",
        commit_projection=projection,
        allow_git_fallback=True,
    ) == second_head
    with pytest.raises(compact_pair_loop.CompactPairError, match="cannot use"):
        compact_pair_loop._full_commit(
            second_root,
            second_head,
            "committed candidate",
            commit_projection=projection,
            allow_git_fallback=False,
        )


def _completed(
    arguments: tuple[str, ...],
    stdout: bytes,
    *,
    returncode: int = 0,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(arguments, returncode, stdout, b"")


def _fake_root(tmp_path: Path) -> tuple[Path, Path, str, str]:
    root = tmp_path / "fake"
    git_dir = root / ".git"
    git_dir.mkdir(parents=True)
    return root, git_dir, "a" * 40, "b" * 40


@pytest.mark.parametrize(
    ("batch_output", "graph_output", "message"),
    [
        (b"a" * 40 + b" commit\n", b"", "batch is truncated"),
        (
            b"a" * 40 + b" commit\n" + b"b" * 40 + b" commit\n",
            b"a" * 40 + b"\n" + b"b" * 40 + b" " + b"c" * 40 + b"\n",
            "omits a referenced parent",
        ),
        (
            b"a" * 40 + b" commit\n" + b"b" * 40 + b" commit\n",
            b"not-a-commit\n",
            "graph is malformed",
        ),
    ],
)
def test_projection_rejects_truncated_or_malformed_git_output(
    tmp_path: Path,
    batch_output: bytes,
    graph_output: bytes,
    message: str,
) -> None:
    root, git_dir, candidate, head = _fake_root(tmp_path)
    identity = f"{root}\n{git_dir}\n{head}\n".encode()

    def runner(_root, arguments, *, input_bytes=None):
        del input_bytes
        if arguments[0] == "rev-parse":
            return _completed(arguments, identity)
        if arguments[0] == "cat-file":
            return _completed(arguments, batch_output)
        if arguments[0] == "rev-list":
            return _completed(arguments, graph_output)
        raise AssertionError(arguments)

    with pytest.raises(projection_module.CommitGraphProjectionError, match=message):
        projection_module.CommitGraphProjection.build(
            root, {candidate}, runner=runner
        )


def test_projection_rejects_graph_output_over_byte_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, git_dir, candidate, head = _fake_root(tmp_path)
    identity = f"{root}\n{git_dir}\n{head}\n".encode()
    batch = (
        f"{candidate} commit\n{head} commit\n".encode()
    )

    def runner(_root, arguments, *, input_bytes=None):
        del input_bytes
        outputs = {
            "rev-parse": identity,
            "cat-file": batch,
            "rev-list": f"{head}\n{candidate}\n".encode(),
        }
        return _completed(arguments, outputs[arguments[0]])

    monkeypatch.setattr(projection_module, "MAX_GRAPH_BYTES", 10)
    with pytest.raises(projection_module.CommitGraphProjectionError, match="exceeds 10 bytes"):
        projection_module.CommitGraphProjection.build(
            root, {candidate}, runner=runner
        )
