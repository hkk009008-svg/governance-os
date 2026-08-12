from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

import cursor_app_binding as binding


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _repo_with_worktree(tmp_path: Path, seat: str = "director") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "seed")
    worktree = tmp_path / seat
    _git(repo, "worktree", "add", "-q", "-b", f"cursor-seat/{seat}", str(worktree))
    return repo, worktree


def test_parse_seat_branch_accepts_only_reserved_known_seats() -> None:
    assert binding.parse_seat_branch("main") is None
    assert binding.parse_seat_branch("cursor-seat/director2") == "director2"
    with pytest.raises(binding.AppBindingError, match="unknown seat"):
        binding.parse_seat_branch("cursor-seat/auditor")


def test_resolve_worktree_requires_linked_worktree(tmp_path: Path) -> None:
    repo, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)

    assert identity is not None
    assert identity.seat == "director"
    assert identity.root == worktree.resolve()
    assert identity.git_dir != identity.common_dir

    _git(repo, "switch", "-q", "-c", "cursor-seat/operator")
    with pytest.raises(binding.AppBindingError, match="linked worktree"):
        binding.resolve_worktree_seat(repo)


def test_ordinary_branch_is_readiness_not_a_seat(tmp_path: Path) -> None:
    repo, _ = _repo_with_worktree(tmp_path)
    assert binding.resolve_worktree_seat(repo) is None


def test_register_latest_conversation_wins_for_same_worktree(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "home" / "registry.json"

    binding.register_session(
        identity,
        conversation_id="conversation-a",
        model_id="composer-2.5",
        registry_path=registry,
    )
    latest = binding.register_session(
        identity,
        conversation_id="conversation-b",
        model_id="gpt-5.6-sol",
        registry_path=registry,
    )

    assert latest.conversation_id == "conversation-b"
    resolved = binding.resolve_registered_session(
        worktree, {}, registry_path=registry
    )
    assert resolved == latest
    assert stat_mode(registry) == 0o600


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def test_registered_session_resolves_from_worktree_and_registry_alone(
    tmp_path: Path,
) -> None:
    _, worktree = _repo_with_worktree(tmp_path, "operator2")
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "registry.json"
    active = binding.register_session(
        identity,
        conversation_id="operator2-chat",
        model_id="claude-sonnet-5",
        registry_path=registry,
    )

    resolved = binding.resolve_registered_session(
        worktree, {}, registry_path=registry
    )

    assert resolved == active
    assert resolved.conversation_id == "operator2-chat"
    assert resolved.model_id == "claude-sonnet-5"


def test_unregistered_seat_worktree_cannot_resolve_session(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    with pytest.raises(binding.AppBindingError, match="no registered"):
        binding.resolve_registered_session(
            worktree, {}, registry_path=tmp_path / "registry.json"
        )


def test_readiness_checkout_cannot_resolve_session(tmp_path: Path) -> None:
    repo, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "registry.json"
    binding.register_session(
        identity,
        conversation_id="director-chat",
        model_id="composer-2.5",
        registry_path=registry,
    )
    with pytest.raises(binding.AppBindingError, match="not a bound Cursor seat"):
        binding.resolve_registered_session(repo, {}, registry_path=registry)


def test_environment_cross_check_rejects_disagreeing_values(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "registry.json"
    binding.register_session(
        identity,
        conversation_id="conversation-b",
        model_id="gpt-5.6-sol",
        registry_path=registry,
    )

    with pytest.raises(binding.AppBindingError, match="disagrees"):
        binding.resolve_registered_session(
            worktree,
            {"CURSOR_APP_CONVERSATION_ID": "conversation-a"},
            registry_path=registry,
        )
    with pytest.raises(binding.AppBindingError, match="disagrees"):
        binding.resolve_registered_session(
            worktree,
            {"CURSOR_APP_MODEL_ID": "composer-2.5"},
            registry_path=registry,
        )


def test_payload_identity_must_match_registry_even_with_matching_env(
    tmp_path: Path,
) -> None:
    _, worktree = _repo_with_worktree(tmp_path, "operator2")
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "registry.json"
    binding.register_session(
        identity,
        conversation_id="operator2-chat",
        model_id="claude-sonnet-5",
        registry_path=registry,
    )
    env = {
        "CURSOR_APP_CONVERSATION_ID": "operator2-chat",
        "CURSOR_APP_MODEL_ID": "claude-sonnet-5",
    }

    matched = binding.resolve_registered_session(
        worktree,
        env,
        registry_path=registry,
        payload={
            "conversation_id": "operator2-chat",
            "model_id": "claude-sonnet-5",
        },
    )
    assert matched.conversation_id == "operator2-chat"

    with pytest.raises(binding.AppBindingError, match="payload conversation_id"):
        binding.resolve_registered_session(
            worktree,
            env,
            registry_path=registry,
            payload={
                "conversation_id": "spoofed-chat",
                "model_id": "claude-sonnet-5",
            },
        )
    with pytest.raises(binding.AppBindingError, match="payload model_id"):
        binding.resolve_registered_session(
            worktree,
            env,
            registry_path=registry,
            payload={
                "conversation_id": "operator2-chat",
                "model_id": "composer-2.5",
            },
        )
    with pytest.raises(binding.AppBindingError, match="payload conversation_id"):
        binding.resolve_registered_session(
            worktree,
            env,
            registry_path=registry,
            payload={"conversation_id": "", "model_id": "claude-sonnet-5"},
        )


def test_registry_rejects_same_seat_in_two_live_worktrees(tmp_path: Path) -> None:
    _, first = _repo_with_worktree(tmp_path)
    second = tmp_path / "director-copy"
    second.mkdir()
    first_identity = binding.resolve_worktree_seat(first)
    assert first_identity is not None
    second_identity = binding.WorktreeSeat(
        seat="director",
        root=second.resolve(),
        branch="cursor-seat/director",
        git_dir=tmp_path / "git-dir-two",
        common_dir=first_identity.common_dir,
    )
    registry = tmp_path / "registry.json"

    binding.register_session(
        first_identity,
        conversation_id="first",
        model_id="composer-2.5",
        registry_path=registry,
    )
    with pytest.raises(binding.AppBindingError, match="another live worktree"):
        binding.register_session(
            second_identity,
            conversation_id="second",
            model_id="composer-2.5",
            registry_path=registry,
        )


def test_registry_rejects_one_conversation_for_two_seats(tmp_path: Path) -> None:
    repo, director = _repo_with_worktree(tmp_path)
    operator = tmp_path / "operator"
    _git(
        repo,
        "worktree",
        "add",
        "-q",
        "-b",
        "cursor-seat/operator",
        str(operator),
    )
    director_identity = binding.resolve_worktree_seat(director)
    operator_identity = binding.resolve_worktree_seat(operator)
    assert director_identity is not None and operator_identity is not None
    registry = tmp_path / "registry.json"
    binding.register_session(
        director_identity,
        conversation_id="shared-chat",
        model_id="composer-2.5",
        registry_path=registry,
    )
    with pytest.raises(binding.AppBindingError, match="cannot bind"):
        binding.register_session(
            operator_identity,
            conversation_id="shared-chat",
            model_id="gpt-5.6-sol",
            registry_path=registry,
        )


def test_registry_replaces_stale_non_worktree_path(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    stale = tmp_path / "stale-directory"
    stale.mkdir()
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "version": 1,
                "bindings": {
                    "director": {
                        "root": str(stale),
                        "branch": "cursor-seat/director",
                        "conversation_id": "old",
                        "model_id": "old",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    active = binding.register_session(
        identity,
        conversation_id="new",
        model_id="composer-2.5",
        registry_path=registry,
    )
    assert active.root == worktree.resolve()


def test_payload_registration_rejects_wrong_or_multiple_workspace_roots(
    tmp_path: Path,
) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    registry = tmp_path / "registry.json"
    payload = {
        "conversation_id": "director-chat",
        "model_id": "composer-2.5",
        "workspace_roots": [str(worktree)],
    }
    active = binding.register_payload_session(
        worktree,
        payload,
        registry_path=registry,
    )
    assert active is not None
    for roots in (
        [str(tmp_path / "wrong")],
        [str(worktree), str(tmp_path / "other")],
    ):
        with pytest.raises(binding.AppBindingError, match="workspace root"):
            binding.register_payload_session(
                worktree,
                {**payload, "workspace_roots": roots},
                registry_path=registry,
            )


def test_background_session_cannot_register_durable_seat(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    with pytest.raises(binding.AppBindingError, match="background"):
        binding.register_payload_session(
            worktree,
            {
                "conversation_id": "background-chat",
                "model_id": "composer-2.5",
                "workspace_roots": [str(worktree)],
                "is_background_agent": True,
            },
            registry_path=tmp_path / "registry.json",
        )


def test_registered_session_rejects_legacy_index(tmp_path: Path) -> None:
    _, worktree = _repo_with_worktree(tmp_path)
    identity = binding.resolve_worktree_seat(worktree)
    assert identity is not None
    registry = tmp_path / "registry.json"
    active = binding.register_session(
        identity,
        conversation_id="director-chat",
        model_id="composer-2.5",
        registry_path=registry,
    )
    environ = binding.session_environment(active)
    environ["GIT_INDEX_FILE"] = "/tmp/index-cursor-director"

    with pytest.raises(binding.AppBindingError, match="must not use"):
        binding.resolve_registered_session(
            worktree, environ, registry_path=registry
        )


def test_malformed_registry_fails_closed(tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"version": 99, "bindings": {}}), encoding="utf-8")
    with pytest.raises(binding.AppBindingError, match="unsupported schema"):
        binding.load_registry(registry)


def test_session_environment_contains_app_identity() -> None:
    active = binding.AppSessionBinding(
        seat="operator2",
        root=Path("/tmp/operator2"),
        branch="cursor-seat/operator2",
        conversation_id="conversation-2",
        model_id="gpt-5.6-sol",
    )
    environ = binding.session_environment(active)
    assert environ == {
        "CURSOR_SEAT": "operator2",
        "CURSOR_AGENT_MODE": "live-seat",
        "CURSOR_AGENT_ROLE": "operator2",
        "CURSOR_BEHAVIOR_SOURCE": "operator2",
        "CURSOR_APP_CONVERSATION_ID": "conversation-2",
        "CURSOR_APP_MODEL_ID": "gpt-5.6-sol",
    }
