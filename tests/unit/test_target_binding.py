"""Multi-target declarative binding registry (governance.toml, ADR-013).

The kernel must be able to govern more than one product repo: evidence-ledger
stays the default target (ADR-008 continuity), and future works register a new
[targets.<name>] table instead of editing Python constants.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import target_binding


def _write_config(root: Path, body: str) -> Path:
    path = root / "governance.toml"
    path.write_text(body, encoding="utf-8")
    return path


DEMO_CONFIG = """
[kernel]
repository = "example/governance-os"

[protocol.kernel]
epoch = 0
writer = "v1"

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


def _replace_kernel_mirror(root: Path, body: str | None) -> None:
    path = root / "governance.toml"
    original = path.read_text(encoding="utf-8")
    block = '[protocol.kernel]\nepoch = 0\nwriter = "v1"\n'
    replacement = "" if body is None else f"[protocol.kernel]\n{body.rstrip()}\n"
    assert block in original
    path.write_text(original.replace(block, replacement), encoding="utf-8")


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


# --- inert compact-kernel mirror -------------------------------------------


def test_load_kernel_mirror_accepts_demo_config_as_declarative_only(tmp_path):
    mirror = target_binding.load_kernel_mirror(_demo_root(tmp_path))

    assert mirror.epoch == 0
    assert mirror.writer == "v1"
    assert mirror.authority == "declarative_only"
    assert "never activation high-water mark" in mirror.provenance
    with pytest.raises(FrozenInstanceError):
        mirror.writer = "compact"


def test_repo_config_declares_inert_v1_kernel_mirror(repo_root):
    mirror = target_binding.load_kernel_mirror(repo_root)

    assert (mirror.epoch, mirror.writer) == (0, "v1")
    assert mirror.authority == "declarative_only"


def test_kernel_mirror_missing_table_fails_closed(tmp_path):
    root = _demo_root(tmp_path)
    _replace_kernel_mirror(root, None)

    with pytest.raises(target_binding.BindingError, match=r"\[protocol\.kernel\]"):
        target_binding.load_kernel_mirror(root)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('writer = "v1"', "epoch"),
        ("epoch = 0", "writer"),
        ('epoch = 0\nwriter = "v1"\nsurprise = true', "surprise"),
    ],
)
def test_kernel_mirror_requires_exact_keys(tmp_path, body, expected):
    root = _demo_root(tmp_path)
    _replace_kernel_mirror(root, body)

    with pytest.raises(target_binding.BindingError, match=expected):
        target_binding.load_kernel_mirror(root)


@pytest.mark.parametrize("epoch_literal", ["true", "-1", '"0"', "0.0"])
def test_kernel_mirror_rejects_invalid_epoch(tmp_path, epoch_literal):
    root = _demo_root(tmp_path)
    _replace_kernel_mirror(root, f'epoch = {epoch_literal}\nwriter = "v1"')

    with pytest.raises(target_binding.BindingError, match="epoch"):
        target_binding.load_kernel_mirror(root)


@pytest.mark.parametrize("writer_literal", ['"future"', "1"])
def test_kernel_mirror_rejects_invalid_writer(tmp_path, writer_literal):
    root = _demo_root(tmp_path)
    _replace_kernel_mirror(root, f"epoch = 0\nwriter = {writer_literal}")

    with pytest.raises(target_binding.BindingError, match="writer"):
        target_binding.load_kernel_mirror(root)


def test_compact_mirror_never_changes_resolved_target_binding(tmp_path):
    root = _demo_root(tmp_path)
    before = target_binding.resolve_target(root, env={})
    _replace_kernel_mirror(root, 'epoch = 0\nwriter = "compact"')

    mirror = target_binding.load_kernel_mirror(root)
    after = target_binding.resolve_target(root, env={})

    assert mirror.writer == "compact"
    assert after == before


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
    assert "epoch 0" in out
    assert "writer v1" in out
    assert "declarative only" in out


def test_check_cli_fails_closed_on_structural_error(tmp_path, capsys):
    _write_config(
        tmp_path,
        '[binding]\ndefault_target = "ghost"\n\n'
        '[targets.real]\nrepository = "x/real"\npath = "/tmp/real"\n',
    )
    rc = target_binding.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ghost" in out


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
            "--seat", "director",
            "--wave", "2",
        ]
    )

    out = capsys.readouterr().out
    demo_path = (tmp_path / "demo-app").resolve().as_posix()
    assert rc == 0
    assert f"Target repo: {demo_path}" in out
    assert f"env -u GIT_INDEX_FILE git -C {demo_path} status --short --branch" in out


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
            "--seat", "director",
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
            "--seat", "director",
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
            "--seat", "director",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 1
    assert f"Refusing `{forbidden.resolve().as_posix()}`" in out


# --- protocol_doctor integration ---------------------------------------------


def test_protocol_doctor_base_commands_include_binding_check():
    import protocol_doctor

    commands = protocol_doctor.base_commands(python_executable="PY", wave=2)
    assert ["PY", "scripts/target_binding.py", "--check"] in commands
    assert ["PY", "scripts/check_coordination.py"] in commands
    assert ["PY", "scripts/protocol_capacity_board.py", "--wave", "2"] in commands
