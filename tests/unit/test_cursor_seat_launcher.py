from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from types import ModuleType
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import cursor_seat_launcher as launcher


SEATS = ("director", "director2", "operator", "operator2", "coordinator")


def _write_config(path: Path, workspace: Path, *, extra: str = "") -> None:
    body = (
        "[runtime]\n"
        f'workspace = "{workspace}"\n'
        'setting_sources = ["project"]\n\n'
    )
    for seat in SEATS:
        body += f'[seats.{seat}]\nmodel = "model-{seat}"\n\n'
    path.write_text(body + extra, encoding="utf-8")


def test_config_is_exact_and_pipeline_scoped(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, tmp_path)

    config = launcher.load_config(config_path, expected_workspace=tmp_path)

    assert config.workspace == tmp_path.resolve()
    assert config.setting_sources == ("project",)
    assert tuple(config.seats) == SEATS
    assert config.seats["operator"].model == "model-operator"


@pytest.mark.parametrize(
    "mutation",
    [
        "\n[extra]\nvalue = true\n",
        "\n[seats.extra]\nmodel = 'model-extra'\n",
    ],
)
def test_config_rejects_unknown_tables(tmp_path: Path, mutation: str) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, tmp_path, extra=mutation)

    with pytest.raises(launcher.ConfigError):
        launcher.load_config(config_path, expected_workspace=tmp_path)


def test_config_rejects_foreign_workspace(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, tmp_path / "foreign")

    with pytest.raises(launcher.ConfigError, match="managed Pipeline workspace"):
        launcher.load_config(config_path, expected_workspace=tmp_path)


def test_config_rejects_relative_workspace_even_when_it_resolves_to_pipeline(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, Path("."))

    with pytest.raises(launcher.ConfigError, match="absolute"):
        launcher.load_config(config_path, expected_workspace=Path.cwd())


@pytest.mark.parametrize(
    ("seat", "mode", "behavior"),
    [
        ("director", "live-seat", "director"),
        ("director2", "live-seat", "director"),
        ("operator", "live-seat", "operator2"),
        ("operator2", "live-seat", "operator2"),
        ("coordinator", "coordinator", None),
    ],
)
def test_launch_spec_binds_exact_cursor_identity(
    tmp_path: Path, seat: str, mode: str, behavior: str | None
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, tmp_path)
    config = launcher.load_config(config_path, expected_workspace=tmp_path)

    spec = launcher.build_launch_spec(
        config,
        git_dir=tmp_path / ".git",
        seat=seat,
        trigger_ref="coordination/mailbox/sent/event.md@" + "a" * 40,
        inherited_env={"CURSOR_SEAT": "wrong", "GIT_INDEX_FILE": "/wrong"},
        operation="dispatch",
    )

    assert spec.env["CURSOR_SEAT"] == seat
    assert spec.env["CURSOR_AGENT_MODE"] == mode
    assert spec.env["CURSOR_AGENT_ROLE"] == seat
    assert spec.env.get("CURSOR_BEHAVIOR_SOURCE") == behavior
    assert spec.env["GIT_INDEX_FILE"] == str(tmp_path / ".git" / f"index-cursor-{seat}")
    assert spec.model == f"model-{seat}"


def test_launch_spec_replaces_ambient_provider_and_git_contracts(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, tmp_path)
    config = launcher.load_config(config_path, expected_workspace=tmp_path)
    index = tmp_path / ".git" / "index-cursor-director"

    spec = launcher.build_launch_spec(
        config,
        git_dir=tmp_path / ".git",
        seat="director",
        trigger_ref="coordination/mailbox/sent/event.md@" + "a" * 40,
        inherited_env={
            "CURSOR_SEAT": "operator",
            "CURSOR_MUTATION_SCOPE": "unbounded",
            "CURSOR_GIT_INDEX_FILE": "/foreign/index",
            "CURSOR_UNKNOWN_FUTURE_FIELD": "stale",
            "CURSOR_API_KEY": "cursor_test_key",
            "CURSOR_PROJECT_DIR": "/repo",
            "CODEX_SEAT": "operator",
            "CODEX_AGENT_MODE": "live-seat",
            "GIT_INDEX_FILE": "/foreign/index",
            "GIT_DIR": "/foreign/git",
            "GIT_WORK_TREE": "/foreign/tree",
        },
        operation="dispatch",
    )

    assert not any(key.startswith("CODEX_") for key in spec.env)
    assert "CURSOR_UNKNOWN_FUTURE_FIELD" not in spec.env
    assert spec.env["CURSOR_MUTATION_SCOPE"] == "seat-owned"
    assert spec.env["CURSOR_GIT_INDEX_FILE"] == str(index)
    assert spec.env["CURSOR_API_KEY"] == "cursor_test_key"
    assert spec.env["CURSOR_PROJECT_DIR"] == str(tmp_path)
    assert spec.env["GIT_INDEX_FILE"] == str(index)
    assert "GIT_DIR" not in spec.env
    assert "GIT_WORK_TREE" not in spec.env


def test_seat_environment_clears_ambient_provider_and_git_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CURSOR_MUTATION_SCOPE", "unbounded")
    monkeypatch.setenv("CODEX_SEAT", "operator")
    monkeypatch.setenv("GIT_DIR", "/foreign/git")

    with launcher._seat_environment(
        {
            "CURSOR_SEAT": "director",
            "GIT_INDEX_FILE": "/repo/.git/index-cursor-director",
        }
    ):
        assert os.environ["CURSOR_SEAT"] == "director"
        assert "CURSOR_MUTATION_SCOPE" not in os.environ
        assert "CODEX_SEAT" not in os.environ
        assert "GIT_DIR" not in os.environ

    assert os.environ["CURSOR_MUTATION_SCOPE"] == "unbounded"
    assert os.environ["CODEX_SEAT"] == "operator"
    assert os.environ["GIT_DIR"] == "/foreign/git"


def test_dispatch_key_is_stable_and_trigger_sensitive() -> None:
    first = launcher.dispatch_key("director", "path@" + "a" * 40, 2)
    second = launcher.dispatch_key("director", "path@" + "a" * 40, 2)
    changed = launcher.dispatch_key("director", "path@" + "b" * 40, 2)

    assert first == second
    assert first != changed
    assert len(first) == 64


def test_registry_write_is_atomic_private_and_prompt_free(tmp_path: Path) -> None:
    path = tmp_path / "runtime" / "pipeline-seats.json"
    registry = launcher.empty_registry(tmp_path)
    registry["seats"]["director"] = {
        "agent_id": "agent-director",
        "model": "model-director",
        "last_run_id": "run-1",
    }

    launcher.save_registry(path, registry)

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert launcher.load_registry(path, tmp_path) == registry
    assert "prompt" not in path.read_text(encoding="utf-8").casefold()
    assert not list(path.parent.glob(".*.tmp"))


def test_registry_rejects_foreign_workspace(tmp_path: Path) -> None:
    path = tmp_path / "pipeline-seats.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workspace": str(tmp_path / "foreign"),
                "seats": {},
                "dispatches": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(launcher.RegistryError, match="workspace"):
        launcher.load_registry(path, tmp_path)


def test_registry_rejects_prompt_content_on_load(tmp_path: Path) -> None:
    path = tmp_path / "pipeline-seats.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workspace": str(tmp_path),
                "seats": {"director": {"prompt": "sensitive"}},
                "dispatches": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(launcher.RegistryError, match="prompt"):
        launcher.load_registry(path, tmp_path)


def test_ensure_seat_index_seeds_only_when_missing(tmp_path: Path) -> None:
    index = tmp_path / ".git" / "index-cursor-director"
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "read-tree" in argv:
            index.parent.mkdir()
            index.write_text("seed", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "ls-files" in argv:
            return subprocess.CompletedProcess(argv, 0, "100644 blob deadbeef\tfile\0", "")
        if "status" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        raise AssertionError(argv)

    launcher.ensure_seat_index(tmp_path, index, runner=fake_run)
    launcher.ensure_seat_index(tmp_path, index, runner=fake_run)

    assert len(calls) == 3
    assert calls[0][-3:] == ["read-tree", f"--index-output={index}", "HEAD"]
    assert "ls-files" in calls[1]
    assert "status" in calls[2]


def test_ensure_seat_index_rejects_existing_empty_index_when_head_has_files(
    tmp_path: Path,
) -> None:
    index = tmp_path / ".git" / "index-cursor-director"
    index.parent.mkdir()
    index.write_text("placeholder", encoding="utf-8")

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if "ls-files" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "ls-tree" in argv:
            return subprocess.CompletedProcess(argv, 0, "scripts/example.py\0", "")
        raise AssertionError(argv)

    with pytest.raises(launcher.LaunchError, match="empty"):
        launcher.ensure_seat_index(tmp_path, index, runner=fake_run)


@pytest.mark.parametrize("entry_kind", ["dangling-symlink", "directory"])
def test_ensure_seat_index_rejects_non_regular_entries_without_git_or_mutation(
    tmp_path: Path,
    entry_kind: str,
) -> None:
    index = tmp_path / ".git" / "index-cursor-director"
    index.parent.mkdir()
    target = tmp_path / "must-not-be-created"
    if entry_kind == "dangling-symlink":
        index.symlink_to(target)
    else:
        index.mkdir()
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    with pytest.raises(launcher.LaunchError, match="regular file"):
        launcher.ensure_seat_index(tmp_path, index, runner=fake_run)

    if entry_kind == "dangling-symlink":
        assert index.is_symlink()
        assert not target.exists()
    else:
        assert index.is_dir()
    assert calls == []


def test_ensure_seat_index_preserves_healthy_staged_index_byte_for_byte(
    tmp_path: Path,
) -> None:
    index = tmp_path / ".git" / "index-cursor-operator"
    index.parent.mkdir()
    index.write_bytes(b"preserve-staged-index")
    before = index.read_bytes()
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "ls-files" in argv:
            return subprocess.CompletedProcess(
                argv, 0, "100644 deadbeef 0\ttracked.txt\0", ""
            )
        if "status" in argv:
            return subprocess.CompletedProcess(argv, 0, "M  tracked.txt\n", "")
        raise AssertionError(argv)

    launcher.ensure_seat_index(tmp_path, index, runner=fake_run)

    assert index.read_bytes() == before
    assert not any("read-tree" in call for call in calls)


def test_review_binding_requires_assignment_and_different_model() -> None:
    request = SimpleNamespace(assigned_operator="operator", author_model="author-model")

    launcher.validate_review_binding(request, "operator", "reviewer-model")
    with pytest.raises(launcher.LaunchError, match="assigned"):
        launcher.validate_review_binding(request, "operator2", "reviewer-model")
    with pytest.raises(launcher.LaunchError, match="different model"):
        launcher.validate_review_binding(request, "operator", "AUTHOR-MODEL")


def test_real_provider_launch_requires_tty_confirmation() -> None:
    with pytest.raises(launcher.LaunchError, match="interactive"):
        launcher.confirm_provider_launch(
            seat="director",
            model="model-director",
            workspace=Path("/repo"),
            trigger_ref="path@" + "a" * 40,
            stdin_isatty=False,
            input_fn=lambda _: "yes",
        )

    assert launcher.confirm_provider_launch(
        seat="director",
        model="model-director",
        workspace=Path("/repo"),
        trigger_ref="path@" + "a" * 40,
        stdin_isatty=True,
        input_fn=lambda _: "yes",
    )


def test_sdk_checkpoints_agent_and_run_identity_before_wait(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    checkpoints: list[tuple[str, str]] = []

    class FakeResult:
        status = "finished"
        model = SimpleNamespace(id="model-director")
        result = "done"

    class FakeRun:
        id = "run-1"

        def wait(self) -> FakeResult:
            assert checkpoints == [("agent", "agent-1"), ("run", "run-1")]
            return FakeResult()

    class FakeAgent:
        agent_id = "agent-1"
        create_key: str | None = None
        send_key: str | None = None

        @classmethod
        def create(cls, **kwargs: object) -> "FakeAgent":
            cls.create_key = kwargs.get("idempotency_key")  # type: ignore[assignment]
            return cls()

        @classmethod
        def resume(cls, *_: object) -> "FakeAgent":
            raise AssertionError("first dispatch must create an agent")

        def __enter__(self) -> "FakeAgent":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def send(self, _: str, *, idempotency_key: str | None = None) -> FakeRun:
            type(self).send_key = idempotency_key
            return FakeRun()

    class FakeAgentOptions:
        def __init__(self, **_: object) -> None:
            pass

    class FakeLocalAgentOptions:
        def __init__(self, **_: object) -> None:
            pass

    sdk = ModuleType("cursor_sdk")
    sdk.Agent = FakeAgent  # type: ignore[attr-defined]
    sdk.AgentOptions = FakeAgentOptions  # type: ignore[attr-defined]
    sdk.LocalAgentOptions = FakeLocalAgentOptions  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cursor_sdk", sdk)

    spec = launcher.LaunchSpec(
        seat="director",
        operation="dispatch",
        model="model-director",
        trigger_ref="path@" + "a" * 40,
        workspace=tmp_path,
        setting_sources=("project",),
        env={},
        index_path=tmp_path / ".git/index-cursor-director",
    )
    registry = launcher.empty_registry(tmp_path)

    run_id, status, combined = launcher._run_sdk(
        spec,
        "trigger",
        registry,
        dispatch_key="dispatch-key",
        on_agent_bound=lambda agent_id: checkpoints.append(("agent", agent_id)),
        on_run_started=lambda started_run_id: checkpoints.append(("run", started_run_id)),
    )

    assert (run_id, status, combined) == ("run-1", "finished", "model-director\0done")
    assert FakeAgent.create_key == "dispatch-key"
    assert FakeAgent.send_key == "dispatch-key"


def test_role_prompt_is_required_before_provider_launch(tmp_path: Path) -> None:
    with pytest.raises(launcher.LaunchError, match="role prompt"):
        launcher._role_prompt(tmp_path, "director")


def test_outbox_run_id_cannot_escape_the_seat_directory(tmp_path: Path) -> None:
    path = launcher._write_outbox(
        tmp_path,
        "director",
        "../../../../escaped",
        "result",
        "model-director",
    )

    expected_parent = tmp_path / ".cursor/runtime/outbox/director"
    assert path.parent.resolve() == expected_parent.resolve()
    assert path.is_file()
    assert not (tmp_path / "escaped.json").exists()


def test_dry_run_does_not_create_runtime_or_index(
    tmp_path: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = tmp_path / "seats.toml"
    _write_config(config, repo_root)
    runtime = repo_root / ".cursor/runtime"
    before = set(runtime.iterdir()) if runtime.exists() else set()
    git_dir = Path(
        subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
            check=True,
            capture_output=True,
            text=True,
            env={key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"},
        ).stdout.strip()
    )
    index = git_dir / "index-cursor-director"
    index_before = index.stat().st_mtime_ns if index.exists() else None

    rc = launcher.main(
        [
            "--config",
            str(config),
            "--dry-run",
            "dispatch",
            "director",
            "--trigger-ref",
            "coordination/mailbox/sent/event.md@" + "a" * 40,
        ]
    )

    assert rc == 0
    assert '"seat": "director"' in capsys.readouterr().out
    after = set(runtime.iterdir()) if runtime.exists() else set()
    assert after == before
    assert (index.stat().st_mtime_ns if index.exists() else None) == index_before
