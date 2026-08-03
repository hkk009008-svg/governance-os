"""Tests for the pre-dispatch harness readiness check.

Each case encodes a failure observed on 2026-07-26 that exited 0 and produced
silence. The point of the check is that these become loud before spend, so a
test that passed while the check was blind would defeat it entirely.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import harness_preflight as preflight


def _settings(tmp_path: Path, allow: list[str]) -> Path:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"permissions": {"allow": allow}}), encoding="utf-8")
    return path


def _failures(results) -> list[str]:
    return [result.detail for result in results if not result.ok]


def _evidence_grants(root: Path | None = None) -> list[str]:
    resolved_root = (root or Path.cwd()).resolve()
    return [
        f"read_file({resolved_root})",
        *(f"command({command})" for command in preflight.AGY_EVIDENCE_COMMANDS),
    ]


def test_agy_missing_command_grants_is_not_ready(tmp_path: Path) -> None:
    """AGY auto-denies a tool it cannot prompt for and still exits 0.

    Granting scoped read_file alone got the observed run past its first denial
    and straight into a second one, so a check that stopped at file reads would
    have called a harness ready that cannot run a single evidence command.
    """
    settings = _settings(tmp_path, [f"read_file({Path.cwd().resolve()})"])

    results = preflight.check_agy(settings, scope="evidence")

    failures = _failures(results)
    assert any("missing evidence grants" in detail for detail in failures)
    assert any(command in detail for detail in failures for command in ("git diff", "pytest"))


def test_agy_evidence_scope_is_ready_without_publication_grants(tmp_path: Path) -> None:
    settings = _settings(tmp_path, _evidence_grants())

    results = preflight.check_agy(settings, scope="evidence")

    assert _failures(results) == []
    scope_results = [
        result for result in results if "capability scope" in result.detail
    ]
    assert len(scope_results) == 1
    assert "evidence selected" in scope_results[0].detail
    assert "evidence-only" in scope_results[0].detail
    assert "cannot publish" in scope_results[0].detail
    assert not any(
        "publishing commands granted" in result.detail
        or "missing publishing grants" in result.detail
        for result in results
    )


@pytest.mark.parametrize("command", preflight.AGY_EVIDENCE_COMMANDS)
def test_agy_narrower_evidence_grant_cannot_satisfy_required_command(
    tmp_path: Path, command: str,
) -> None:
    grants = _evidence_grants()
    grants.remove(f"command({command})")
    grants.append(f"command({command} --unrelated-only)")
    settings = _settings(tmp_path, grants)

    results = preflight.check_agy(settings, scope="evidence")

    failures = _failures(results)
    assert any("missing evidence grants" in detail for detail in failures)
    assert any(command in detail for detail in failures)


@pytest.mark.parametrize("command", preflight.AGY_PUBLISH_COMMANDS)
def test_agy_narrower_publish_grant_cannot_satisfy_required_command(
    tmp_path: Path, command: str,
) -> None:
    grants = [
        *_evidence_grants(),
        *(f"command({item})" for item in preflight.AGY_PUBLISH_COMMANDS),
    ]
    grants.remove(f"command({command})")
    grants.append(f"command({command} --unrelated-only)")
    settings = _settings(tmp_path, grants)

    results = preflight.check_agy(settings, scope="publishing")

    failures = _failures(results)
    assert any("missing publishing grants" in detail for detail in failures)
    assert any(command in detail for detail in failures)


@pytest.mark.parametrize(
    ("required", "grant"),
    (
        ("git diff --name-status HEAD^ HEAD --", "command(git diff)"),
        (
            ".venv/bin/python -m pytest -q tests/unit/test_harness_preflight.py",
            "command(.venv/bin/python -m pytest)",
        ),
    ),
)
def test_agy_broader_grant_token_prefix_covers_required_invocation(
    required: str, grant: str,
) -> None:
    assert preflight._command_granted(required, {grant})


@pytest.mark.parametrize(
    "grant",
    (
        "command()",
        "command(git diff",
        "command(git diff))",
        "prefix-command(git diff)",
        "command(git 'diff)",
    ),
)
def test_agy_malformed_command_grant_fails_closed(grant: str) -> None:
    assert not preflight._command_granted("git diff", {grant})


@pytest.mark.parametrize(
    ("required", "grant"),
    (
        ("git diff", "command(git dif)"),
        ("git diff", "command(git difference)"),
        ("git diff", "command(git diff-extra)"),
        ("rg", "command(r)"),
    ),
)
def test_agy_command_grants_do_not_use_string_prefixes(
    required: str, grant: str,
) -> None:
    assert not preflight._command_granted(required, {grant})


def test_agy_publishing_scope_additionally_requires_effect_commands(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path, _evidence_grants())

    results = preflight.check_agy(settings, scope="publishing")

    failures = _failures(results)
    assert any("send-event" in detail for detail in failures)
    assert any("git commit" in detail for detail in failures)


def test_agy_with_every_publishing_grant_is_capability_ready(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        [
            *_evidence_grants(),
            *(f"command({command})" for command in preflight.AGY_PUBLISH_COMMANDS),
        ],
    )

    results = preflight.check_agy(settings, scope="publishing")

    assert _failures(results) == []
    assert any("separate authority" in result.detail for result in results)


def test_agy_default_scope_remains_full_publishing_check(tmp_path: Path) -> None:
    settings = _settings(tmp_path, _evidence_grants())

    results = preflight.check_agy(settings)

    assert any("git commit" in detail for detail in _failures(results))


def test_agy_cli_passes_and_prints_explicit_scope(monkeypatch, capsys) -> None:
    selected: list[str] = []
    roots: list[Path] = []

    def check(*, scope: str, repo_root: Path):
        selected.append(scope)
        roots.append(repo_root)
        return [preflight.Result("agy", True, f"selected {scope} scope")]

    monkeypatch.setattr(preflight, "check_agy", check)
    code = preflight.main(["agy", "--agy-scope", "evidence"])

    assert code == 0
    assert selected == ["evidence"]
    assert roots == [Path.cwd().resolve()]
    assert "selected evidence scope" in capsys.readouterr().out


def test_agy_missing_read_file_is_reported_separately(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        [f"command({command})" for command in preflight.AGY_EVIDENCE_COMMANDS],
    )

    results = preflight.check_agy(settings)

    assert any("read_file NOT granted" in detail for detail in _failures(results))


def test_agy_rejects_legacy_bare_read_file_grant(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        [
            "read_file",
            *(f"command({command})" for command in preflight.AGY_EVIDENCE_COMMANDS),
        ],
    )

    results = preflight.check_agy(
        settings, scope="evidence", repo_root=tmp_path,
    )

    failures = _failures(results)
    assert any("scoped read_file" in detail for detail in failures)
    assert any(f"read_file({tmp_path.resolve()})" in detail for detail in failures)


def test_agy_read_grant_must_match_resolved_repo_root(tmp_path: Path) -> None:
    granted_root = tmp_path / "granted"
    requested_root = tmp_path / "requested"
    settings = _settings(tmp_path, _evidence_grants(granted_root))

    results = preflight.check_agy(
        settings, scope="evidence", repo_root=requested_root,
    )

    assert any("scoped read_file" in detail for detail in _failures(results))


def test_agy_absent_settings_is_not_ready(tmp_path: Path) -> None:
    results = preflight.check_agy(tmp_path / "nope.json")

    assert any("settings absent" in detail for detail in _failures(results))


def test_codex_ambient_runtime_authority_is_not_ready(tmp_path: Path) -> None:
    """A project config granting approvals-off is a launch hazard, not readiness.

    The reverted config carried approval_policy and sandbox_mode, and any Codex
    launch without explicit flags would have inherited approvals off with full
    disk access. A preflight blind to that would call the dangerous launch fine.
    """
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'personality = "friendly"\napproval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )

    results = preflight.check_codex(tmp_path)

    ambient = [r for r in results if "project config" in r.detail]
    assert ambient, "the ambient-authority check did not run"
    assert not ambient[0].ok
    assert "approval_policy" in ambient[0].detail
    assert "sandbox_mode" in ambient[0].detail


def test_codex_clean_project_config_is_ready(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'personality = "friendly"\n', encoding="utf-8"
    )

    results = preflight.check_codex(tmp_path)

    ambient = [r for r in results if "project config" in r.detail]
    assert ambient, "the ambient-authority check did not run"
    assert ambient[0].ok


def test_cursor_unregistered_seat_is_not_ready(tmp_path: Path) -> None:
    """Pointed at an unbound seat, Cursor reports itself unbound and does nothing.

    The observed run degraded to a readiness posture because --workspace was the
    main checkout rather than the seat worktree, and still exited 0.
    """
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"bindings": {}}), encoding="utf-8")

    results = preflight.check_cursor("operator", registry)

    assert any("not registered" in detail for detail in _failures(results))


def test_cursor_missing_worktree_is_not_ready(tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {"bindings": {"operator": {
                "root": str(tmp_path / "absent-worktree"),
                "branch": "cursor-seat/operator",
                "model_id": "composer-2.5",
            }}}
        ),
        encoding="utf-8",
    )

    results = preflight.check_cursor("operator", registry)

    assert any("MISSING" in detail for detail in _failures(results))


def test_main_fails_closed_when_any_check_fails(tmp_path: Path, capsys) -> None:
    """Readiness must be a nonzero exit, because every real failure returned 0."""
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'approval_policy = "never"\n', encoding="utf-8"
    )

    code = preflight.main(["codex", "--repo-root", str(tmp_path)])

    assert code == 1
    assert "NOT READY" in capsys.readouterr().out


def test_agy_scope_command_sets_do_not_conflate_evidence_with_publication() -> None:
    evidence = " ".join(preflight.AGY_EVIDENCE_COMMANDS)
    publishing = " ".join(preflight.AGY_PUBLISH_COMMANDS)

    for command in (
        "git diff",
        "git show",
        "git status",
        "git rev-parse",
        "git merge-base",
        "rg",
        ".venv/bin/python -m pytest",
    ):
        assert command in evidence
    assert "send-event" not in evidence
    assert "git commit" not in evidence
    assert "send-event" in publishing
    assert "git commit" in publishing


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _review_request_repo(
    tmp_path: Path,
    *,
    empty_range: bool = False,
    non_utf8_diff: bool = False,
    invalid_ancestry: bool = False,
) -> tuple[Path, str, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Tests")
    payload = root / "payload.txt"
    payload.write_text("base\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "base")
    base = _git(root, "rev-parse", "HEAD")
    if empty_range:
        _git(root, "commit", "-q", "--allow-empty", "-m", "empty head")
    else:
        if non_utf8_diff:
            payload.write_bytes(b"head-\xff\n")
        else:
            payload.write_text("head\n", encoding="utf-8")
        _git(root, "add", "payload.txt")
        _git(root, "commit", "-q", "-m", "head")
    head = _git(root, "rev-parse", "HEAD")
    request_base, request_head = (head, base) if invalid_ancestry else (base, head)
    path = (
        "coordination/mailbox/sent/"
        "2026-08-03T05-00-00Z-director-to-operator-verify-request.md"
    )
    target = root / path
    target.parent.mkdir(parents=True)
    target.write_text(
        "\n".join(
            (
                "# Director → Operator: packaged review",
                "",
                "**When:** 2026-08-03T05:00:00Z · **From:** director (online)",
                "",
                "Event type: verify-request",
                f"Reviewed head: {request_head}",
                f"Reviewed base: {request_base}",
                "Author seat: director",
                "Author model: gpt-5.6-sol",
                "Assigned operator: operator",
                "Risk class: material-behavior",
                "",
                "## Outcome",
                "",
                "Review the exact committed range.",
                "",
                "## Finding Refs",
                "",
                f"- sha256:{'1' * 64}",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", "request")
    trigger = _git(root, "rev-parse", "HEAD")
    return root, f"{path}@{trigger}", base, head


def test_toolless_package_binds_committed_request_and_exact_range(
    tmp_path: Path,
) -> None:
    root, request_ref, base, head = _review_request_repo(tmp_path)

    prompt = preflight.package_toolless_review(root, request_ref)

    assert request_ref in prompt
    assert f"{base}..{head}" in prompt
    assert "-base" in prompt
    assert "+head" in prompt
    assert "advisory" in prompt.casefold()


@pytest.mark.parametrize("failure", ("empty", "ancestry", "oversize", "non_utf8"))
def test_toolless_package_fails_closed_on_invalid_range_or_bytes(
    tmp_path: Path, failure: str,
) -> None:
    root, request_ref, _, _ = _review_request_repo(
        tmp_path,
        empty_range=failure == "empty",
        non_utf8_diff=failure == "non_utf8",
        invalid_ancestry=failure == "ancestry",
    )

    with pytest.raises(preflight.PreflightError):
        preflight.package_toolless_review(
            root,
            request_ref,
            max_bytes=128 if failure == "oversize" else preflight.MAX_PACKAGE_BYTES,
        )


def test_toolless_package_requires_full_request_commit(tmp_path: Path) -> None:
    root, request_ref, _, _ = _review_request_repo(tmp_path)
    path, _, commit = request_ref.rpartition("@")

    with pytest.raises(preflight.PreflightError, match="full"):
        preflight.package_toolless_review(root, f"{path}@{commit[:12]}")


@pytest.mark.parametrize(
    "stdout",
    (
        "",
        'no output produced — a tool required the "command(git rev-parse)" '
        "permission and was auto-denied.\n",
    ),
)
def test_live_probe_rejects_exit_zero_without_exact_positive_artifact(
    tmp_path: Path, stdout: str,
) -> None:
    root, _, _, _ = _review_request_repo(tmp_path)

    def runner(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout=stdout, stderr="")

    result = preflight.live_probe("agy", root, runner=runner)

    assert result.ok is False
    assert "positive artifact" in result.detail


def test_live_probe_accepts_only_exact_nonempty_head_artifact(tmp_path: Path) -> None:
    root, _, _, _ = _review_request_repo(tmp_path)
    expected = _git(root, "rev-parse", "--show-toplevel", "--short", "HEAD")

    def runner(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout=expected + "\n", stderr="")

    result = preflight.live_probe("agy", root, runner=runner)

    assert result.ok is True


def test_agy_live_probe_places_all_flags_before_print_and_sanitizes_git_env(
    tmp_path: Path, monkeypatch,
) -> None:
    root, _, _, _ = _review_request_repo(tmp_path)
    expected = _git(root, "rev-parse", "--show-toplevel", "--short", "HEAD")
    captured: dict[str, object] = {}
    monkeypatch.setenv("GIT_INDEX_FILE", "/tmp/poisoned-index")
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", "/tmp/poisoned-objects")

    def runner(argv, **kwargs):
        captured["argv"] = argv
        captured["env"] = kwargs["env"]
        return subprocess.CompletedProcess(
            argv, 0, stdout=expected + "\n", stderr="",
        )

    result = preflight.live_probe("agy", root, runner=runner)

    assert result.ok is True
    argv = captured["argv"]
    assert isinstance(argv, list)
    assert argv[-2] == "--print"
    assert "git rev-parse --show-toplevel --short HEAD" in argv[-1]
    assert "env -u" not in argv[-1]
    assert argv[argv.index("--mode") + 1] == "plan"
    assert argv[argv.index("--model") + 1] == preflight.AGY_PROBE_MODEL
    assert argv[argv.index("--effort") + 1] == "low"
    assert argv[argv.index("--add-dir") + 1] == str(root.resolve())
    assert argv.index("--add-dir") < argv.index("--print")
    assert argv.index("--disable-slash-commands") < argv.index("--print")
    assert f'Cwd set to {json.dumps(str(root.resolve()))}' in argv[-1]
    assert (
        'CommandLine set to "git rev-parse --show-toplevel --short HEAD"'
        in argv[-1]
    )
    assert "do not retry" in argv[-1]
    assert "do not request sandbox bypass" in argv[-1]
    environment = captured["env"]
    assert isinstance(environment, dict)
    assert not any(key.startswith("GIT_") for key in environment)


def test_agy_live_probe_positive_artifact_depends_on_exact_root_binding(
    tmp_path: Path,
) -> None:
    root, _, _, _ = _review_request_repo(tmp_path)
    expected = _git(root, "rev-parse", "--show-toplevel", "--short", "HEAD")

    def runner(argv, **kwargs):
        root_text = str(root.resolve())
        add_dir_bound = any(
            argv[index : index + 2] == ["--add-dir", root_text]
            for index in range(len(argv) - 1)
        )
        prompt_bound = f'Cwd set to {json.dumps(root_text)}' in argv[-1]
        stdout = expected + "\n" if add_dir_bound and prompt_bound else ""
        return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr="")

    result = preflight.live_probe("agy", root, runner=runner)

    assert result.ok is True


def test_agy_live_probe_rejects_same_head_artifact_from_wrong_root(
    tmp_path: Path,
) -> None:
    root, _, _, _ = _review_request_repo(tmp_path)
    wrong_root = tmp_path / "same-head-wrong-root"
    _git(tmp_path, "clone", "-q", str(root), str(wrong_root))
    assert _git(root, "rev-parse", "--short", "HEAD") == _git(
        wrong_root, "rev-parse", "--short", "HEAD",
    )
    wrong_artifact = _git(wrong_root, "rev-parse", "--short", "HEAD")

    def runner(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 0, stdout=wrong_artifact + "\n", stderr="",
        )

    result = preflight.live_probe("agy", root, runner=runner)

    assert result.ok is False
    assert "positive artifact" in result.detail


def test_package_cli_never_calls_live_provider(tmp_path: Path, monkeypatch, capsys) -> None:
    root, request_ref, _, _ = _review_request_repo(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("packaging must not launch a provider")

    monkeypatch.setattr(preflight, "live_probe", forbidden)
    code = preflight.main(
        [
            "agy",
            "--repo-root",
            str(root),
            "--package-request",
            request_ref,
        ]
    )

    assert code == 0
    assert request_ref in capsys.readouterr().out
