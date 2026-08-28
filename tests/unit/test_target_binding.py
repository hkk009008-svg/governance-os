"""Multi-target declarative binding registry (governance.toml, ADR-013).

The kernel must be able to govern more than one product repo: evidence-ledger
stays the default target (ADR-008 continuity), and future works register a new
[targets.<name>] table instead of editing Python constants.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

import route_lineage
import target_binding


def _write_config(root: Path, body: str) -> Path:
    path = root / "governance.toml"
    path.write_text(body, encoding="utf-8")
    return path


DEMO_CONFIG = """
[kernel]
repository = "example/governance-os"

[binding]
default_target = "demo-app"

[targets.demo-app]
repository = "example/demo-app"
path = "{demo_path}"
route_keywords = ["demo"]
description = "a future work governed from this kernel"

[targets.beta-app]
repository = "example/beta-app"
path = "{beta_path}"

[paths]
forbidden_roots = ["{forbidden}"]
"""


def _demo_root(tmp_path: Path) -> Path:
    _write_config(
        tmp_path,
        DEMO_CONFIG.format(
            demo_path=(tmp_path / "demo-app").as_posix(),
            beta_path=(tmp_path / "beta-app").as_posix(),
            forbidden=(tmp_path / "Forbidden").as_posix(),
        ),
    )
    return tmp_path


# --- registry loading -------------------------------------------------------


def test_list_targets_registers_every_table(tmp_path):
    root = _demo_root(tmp_path)
    names = [target.name for target in target_binding.list_targets(root)]
    assert names == ["demo-app", "beta-app"]


def test_missing_config_fails_closed(tmp_path):
    with pytest.raises(target_binding.BindingError) as excinfo:
        target_binding.resolve_target(tmp_path, env={})
    assert "governance.toml" in str(excinfo.value)


def test_default_target_missing_from_registry_fails_closed(tmp_path):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "ghost"\n\n'
        '[targets.real]\nrepository = "x/real"\npath = "/tmp/real"\n',
    )
    with pytest.raises(target_binding.BindingError) as excinfo:
        target_binding.resolve_target(tmp_path, env={})
    assert "ghost" in str(excinfo.value)


def test_target_missing_required_key_fails_closed(tmp_path):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "demo"\n\n'
        '[targets.demo]\nrepository = "x/demo"\n',
    )
    with pytest.raises(target_binding.BindingError) as excinfo:
        target_binding.resolve_target(tmp_path, env={})
    assert "path" in str(excinfo.value)


def test_unknown_target_key_fails_closed(tmp_path):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "demo"\n\n'
        '[targets.demo]\nrepository = "x/demo"\npath = "/tmp/demo"\nsurprise = 1\n',
    )
    with pytest.raises(target_binding.BindingError) as excinfo:
        target_binding.resolve_target(tmp_path, env={})
    assert "surprise" in str(excinfo.value)


# --- resolution order -------------------------------------------------------


def test_resolve_default_target(tmp_path):
    root = _demo_root(tmp_path)
    binding = target_binding.resolve_target(root, env={})
    assert binding.name == "demo-app"
    assert binding.repository == "example/demo-app"
    assert binding.path == (tmp_path / "demo-app").resolve()
    assert binding.route_keywords == ("demo",)


def test_resolve_by_explicit_name(tmp_path):
    root = _demo_root(tmp_path)
    binding = target_binding.resolve_target(root, name="beta-app", env={})
    assert binding.name == "beta-app"
    assert binding.path == (tmp_path / "beta-app").resolve()


def test_env_var_selects_target(tmp_path):
    root = _demo_root(tmp_path)
    binding = target_binding.resolve_target(root, env={"GOVERNANCE_TARGET": "beta-app"})
    assert binding.name == "beta-app"


def test_explicit_name_beats_env(tmp_path):
    root = _demo_root(tmp_path)
    binding = target_binding.resolve_target(
        root, name="demo-app", env={"GOVERNANCE_TARGET": "beta-app"}
    )
    assert binding.name == "demo-app"


def test_env_path_overrides_selected_target_path(tmp_path):
    root = _demo_root(tmp_path)
    override = tmp_path / "elsewhere"
    binding = target_binding.resolve_target(
        root, env={"GOVERNANCE_TARGET_PATH": str(override)}
    )
    assert binding.path == override.resolve()
    assert "GOVERNANCE_TARGET_PATH" in binding.source


def test_unknown_target_fails_closed_and_lists_known(tmp_path):
    root = _demo_root(tmp_path)
    with pytest.raises(target_binding.BindingError) as excinfo:
        target_binding.resolve_target(root, name="ghost", env={})
    message = str(excinfo.value)
    assert "ghost" in message
    assert "demo-app" in message and "beta-app" in message


def test_route_keywords_default_to_target_name(tmp_path):
    root = _demo_root(tmp_path)
    binding = target_binding.resolve_target(root, name="beta-app", env={})
    assert binding.route_keywords == ("beta-app",)


def test_forbidden_roots_parse_and_resolve(tmp_path):
    root = _demo_root(tmp_path)
    roots = target_binding.forbidden_roots(root)
    assert roots == ((tmp_path / "Forbidden").resolve(),)


def test_tilde_paths_expand_to_home(tmp_path):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "demo"\n\n'
        '[targets.demo]\nrepository = "x/demo"\npath = "~/demo-checkout"\n',
    )
    binding = target_binding.resolve_target(tmp_path, env={})
    assert binding.path == (Path.home() / "demo-checkout").resolve()


# --- the committed repo registry (ADR-008 continuity) -----------------------


def test_repo_config_keeps_evidence_ledger_as_default(repo_root):
    binding = target_binding.resolve_target(repo_root, env={})
    assert binding.name == "evidence-ledger"
    assert binding.repository == "hkk009008-svg/evidence-ledger"
    assert binding.path == (Path.home() / "evidence-ledger").resolve()
    assert "ledger" in binding.route_keywords


def test_repo_config_forbids_content_kernel(repo_root):
    assert (Path.home() / "Content").resolve() in target_binding.forbidden_roots(repo_root)


# --- check CLI ---------------------------------------------------------------


def test_check_cli_reports_all_targets(tmp_path, capsys):
    root = _demo_root(tmp_path)
    rc = target_binding.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "demo-app" in out and "beta-app" in out
    assert "default" in out.lower()


def test_check_cli_fails_closed_on_structural_error(tmp_path, capsys):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "ghost"\n\n'
        '[targets.real]\nrepository = "x/real"\npath = "/tmp/real"\n',
    )
    rc = target_binding.main(["--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.out == ""
    assert "ghost" in captured.err


def test_print_path_cli_resolves_explicit_target_to_stdout_only(tmp_path, capsys):
    root = _demo_root(tmp_path)
    rc = target_binding.main(
        ["--root", str(root), "--target", "beta-app", "--print-path"]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == f"{(tmp_path / 'beta-app').resolve()}\n"
    assert captured.err == ""


def test_print_path_cli_uses_default_and_path_override(tmp_path, capsys, monkeypatch):
    root = _demo_root(tmp_path)
    override = tmp_path / "override"
    monkeypatch.delenv("GOVERNANCE_TARGET", raising=False)
    monkeypatch.setenv("GOVERNANCE_TARGET_PATH", str(override))
    rc = target_binding.main(["--root", str(root), "--print-path"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == f"{override.resolve()}\n"
    assert captured.err == ""


def test_print_path_cli_errors_go_to_stderr(tmp_path, capsys):
    root = _demo_root(tmp_path)
    rc = target_binding.main(
        ["--root", str(root), "--target", "ghost", "--print-path"]
    )
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.out == ""
    assert "unknown target `ghost`" in captured.err


def test_print_path_cli_honors_target_name_environment(tmp_path, capsys, monkeypatch):
    root = _demo_root(tmp_path)
    monkeypatch.setenv("GOVERNANCE_TARGET", "beta-app")
    rc = target_binding.main(["--root", str(root), "--print-path"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == f"{(tmp_path / 'beta-app').resolve()}\n"
    assert captured.err == ""


def test_target_without_print_path_fails_argument_validation(tmp_path):
    root = _demo_root(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        target_binding.main(["--root", str(root), "--target", "beta-app"])
    assert excinfo.value.code == 2


def test_print_path_and_check_are_mutually_exclusive(tmp_path):
    root = _demo_root(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        target_binding.main(["--root", str(root), "--check", "--print-path"])
    assert excinfo.value.code == 2


# --- start-guard integration: future works start here ------------------------


def _route_body(task_board: str, keyword: str) -> str:
    return (
        f"# Coordinator -> All: {keyword} phase0 route\n\n"
        f"Task-board: {task_board}\n"
        f"This cycle routes {keyword} work.\n"
    )


def test_guard_routes_future_target_from_registry(tmp_path, capsys):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    (sent / "2026-07-11T21-00-00Z-coordinator-to-all-coordination.md").write_text(
        _route_body("demo-app-phase0", "demo"), encoding="utf-8"
    )

    rc = ledger_start_guard.main(
        [
            "--root", str(root),
            "--kernel", str(root),
            "--binding-root", str(root),
            "--seat", "author",
            "--wave", "2",
        ]
    )

    out = capsys.readouterr().out
    demo_path = (tmp_path / "demo-app").resolve().as_posix()
    assert rc == 0
    assert f"Target repo: {demo_path}" in out
    assert f"git -C {demo_path} status --short --branch" in out
    assert "env -u GIT_INDEX_FILE" not in out


def test_guard_selects_named_target_over_default(tmp_path, capsys):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    (sent / "2026-07-11T21-05-00Z-coordinator-to-all-coordination.md").write_text(
        _route_body("beta-app-phase0", "beta-app"), encoding="utf-8"
    )

    rc = ledger_start_guard.main(
        [
            "--root", str(root),
            "--kernel", str(root),
            "--binding-root", str(root),
            "--target", "beta-app",
            "--seat", "author",
            "--wave", "2",
        ]
    )

    out = capsys.readouterr().out
    beta_path = (tmp_path / "beta-app").resolve().as_posix()
    assert rc == 0
    assert f"Target repo: {beta_path}" in out


def test_guard_fails_closed_on_unknown_target(tmp_path, capsys):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    rc = ledger_start_guard.main(
        [
            "--root", str(root),
            "--kernel", str(root),
            "--binding-root", str(root),
            "--target", "ghost",
            "--seat", "author",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 1
    assert "ghost" in out


def test_guard_refuses_configured_forbidden_root(tmp_path, capsys):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    forbidden = tmp_path / "Forbidden"
    forbidden.mkdir()

    rc = ledger_start_guard.main(
        [
            "--root", str(forbidden),
            "--kernel", str(root),
            "--binding-root", str(root),
            "--seat", "author",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 1
    assert f"Refusing `{forbidden.resolve().as_posix()}`" in out


# --- protocol_doctor integration ---------------------------------------------


def test_protocol_doctor_base_commands_include_binding_check():
    import protocol_doctor

    commands = protocol_doctor.base_commands(python_executable="PY", wave=2)
    assert ["PY", "pipeline/target_binding.py", "--check"] in commands
    assert ["PY", "pipeline/check_coordination.py"] in commands
    assert ["PY", "pipeline/route_lineage.py", "--check"] in commands


# --- autonomous route conflict enforcement ----------------------------------


def _write_legacy_lineage_route(
    root: Path,
    *,
    timestamp: str,
    task: str,
    keyword: str,
    generation: int,
    parent: str | None = None,
) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / f"{timestamp}-coordinator-to-all-coordination.md"
    parent_line = f"Supersedes route: {parent}\n" if parent else ""
    path.write_text(
        f"Task-board: {task}\nThis routes {keyword} work.\n"
        f"Route generation: {generation}\n{parent_line}",
        encoding="utf-8",
    )
    return path


def test_find_latest_target_route_rejects_same_task_fork(tmp_path):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    parent = _write_legacy_lineage_route(
        root,
        timestamp="2026-07-18T10-00-00Z",
        task="demo-route",
        keyword="demo",
        generation=1,
    )
    parent_ref = parent.name
    _write_legacy_lineage_route(
        root,
        timestamp="2026-07-18T10-01-00Z",
        task="demo-route",
        keyword="demo",
        generation=2,
        parent=parent_ref,
    )
    _write_legacy_lineage_route(
        root,
        timestamp="2026-07-18T10-02-00Z",
        task="demo-route",
        keyword="demo",
        generation=2,
        parent=parent_ref,
    )
    target = target_binding.resolve_target(root, env={})

    with pytest.raises(ledger_start_guard.RouteResolutionError, match="demo-route"):
        ledger_start_guard.find_latest_ledger_route(root, target)


def test_resolve_latest_target_route_returns_the_selected_live_object(tmp_path):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    expected = _write_legacy_lineage_route(
        root,
        timestamp="2026-07-18T10-00-00Z",
        task="demo-route",
        keyword="demo",
        generation=1,
    )
    target = target_binding.resolve_target(root, env={})

    route = ledger_start_guard.resolve_latest_ledger_route(root, target)

    assert route is not None
    assert route.path == expected
    assert route.body == expected.read_text(encoding="utf-8")


def test_build_guard_reports_selected_task_lineage_failure(tmp_path):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    _write_legacy_lineage_route(
        root,
        timestamp="2026-07-18T10-00-00Z",
        task="demo-route",
        keyword="demo",
        generation=3,
        parent="missing-route.md",
    )

    result = ledger_start_guard.build_guard(
        seat="author",
        root=root,
        kernel=root,
        binding_root=root,
    )

    assert not result.ok
    assert any("demo-route" in error for error in result.errors)
    assert any("dangling parent" in error for error in result.errors)


def _route_git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def _init_committed_demo_root(root: Path) -> None:
    _route_git(root, "init", "-q")
    _route_git(root, "config", "user.name", "Guard Test")
    _route_git(root, "config", "user.email", "guard@example.test")
    _route_git(root, "add", "--", "governance.toml")
    _route_git(root, "commit", "-q", "-m", "governance")


def _commit_autonomous_demo_route(
    root: Path,
    *,
    task: str = "demo-route",
    owners: str = "director",
) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / "2026-07-18T11-00-00Z-director-to-all-coordination.md"
    path.write_text(
        "# director -> all: autonomous route\n\n"
        "**When:** 2026-07-18T11:00:00Z · **From:** director (online)\n\n"
        f"Task ID: {task}\n"
        "Outcome contract: deliver demo behavior\n"
        "Parent contract: (none)\n"
        "Contract revision: 0\n"
        "Previous owners: (none)\n"
        f"Owners: {owners}\n"
        "Proposal ref: self-candidate\n"
        "Acceptance refs: self-candidate\n"
        "Finding refs: (none)\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    rel = path.relative_to(root).as_posix()
    _route_git(root, "add", "--", rel)
    _route_git(root, "commit", "-q", "-m", "autonomous route")
    return path


def test_find_latest_route_rejects_worktree_replacement_after_validation(tmp_path):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    _init_committed_demo_root(root)
    path = _commit_autonomous_demo_route(root)
    loaded = route_lineage.load_routes(root)
    assert loaded[0].effective
    path.write_text(path.read_text(encoding="utf-8").replace("demo-route", "demo-evil"), encoding="utf-8")
    target = target_binding.resolve_target(root, env={})

    with pytest.raises(ledger_start_guard.RouteResolutionError, match="working tree"):
        ledger_start_guard.find_latest_ledger_route(root, target)

    result = ledger_start_guard.build_guard(
        seat="author", root=root, kernel=root, binding_root=root
    )
    assert not result.ok
    assert any("working tree" in error for error in result.errors)


def test_guard_delete_readd_same_filename_never_uses_old_valid_blob(tmp_path):
    import ledger_start_guard

    root = _demo_root(tmp_path)
    _init_committed_demo_root(root)
    path = _commit_autonomous_demo_route(root)
    rel = path.relative_to(root).as_posix()
    original_commit = _route_git(root, "rev-parse", "HEAD")
    _route_git(root, "rm", "-q", "--", rel)
    _route_git(root, "commit", "-q", "-m", "delete route")
    _commit_autonomous_demo_route(root, owners="operator")
    readd_commit = _route_git(root, "rev-parse", "HEAD")
    assert readd_commit != original_commit
    target = target_binding.resolve_target(root, env={})

    with pytest.raises(ledger_start_guard.RouteResolutionError, match="ineffective"):
        ledger_start_guard.find_latest_ledger_route(root, target)

    result = ledger_start_guard.build_guard(
        seat="author", root=root, kernel=root, binding_root=root
    )
    assert not result.ok
    assert any("ineffective" in error for error in result.errors)
