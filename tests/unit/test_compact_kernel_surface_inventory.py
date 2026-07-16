from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = (
    REPO_ROOT / "tests/fixtures/compact_kernel/v1_surface_inventory.json"
)

SCHEMA_VERSION = "compact-kernel-surface-inventory/v1"
HELPER_CLASSES = {
    "runtime_core",
    "cli_entrypoint",
    "historical_adapter",
    "telemetry",
    "orphan",
}
COMPONENT_IDS = {
    "target_binding",
    "markdown_routes_and_mailbox_writer",
    "typed_route_compatibility_canary",
    "capacity_reducer_and_packet_state_telemetry",
    "effectiveness_telemetry",
    "capability_receipt_recording",
    "verification_authority_and_publication",
    "live_v1_route_lineage_reader",
    "signed_bus_event_and_cursor_runtime",
    "live_v1_status_and_runtime_readers",
    "coordination_lock_effects",
    "codex_runtime_and_hook_adapter",
    "legacy_lifecycle_mapping_contract",
    "capability_baseline_runtime_collector",
    "compact_shadow_reducer_and_v1_adapter",
}
AUTHORITY_CONTRACT = {
    "route_authority": "markdown_mailbox",
    "route_sidecar_role": "compatibility_only",
    "signed_bus_role": "live_threeway_toolchain_not_compact_route_authority",
    "capability_consumption_role": "post_effect_evidence_only",
    "provider_output_role": "advisory_only",
}
ORPHAN_DISPOSITION = "integrate_or_delete_before_cutover"
REQUIRED_ORPHANS = {
    "scripts.packet_state.is_valid_work_transition",
    "scripts.route_lineage.check_cas",
    "scripts.verification_report_gate.validate_live_report",
    "scripts.verification_report_gate.publish_candidate",
}
READ_ONLY_COMPONENT_IDS = {
    "compact_shadow_reducer_and_v1_adapter",
    "legacy_lifecycle_mapping_contract",
    "live_v1_route_lineage_reader",
}
MAPPING_PRODUCER_DEPENDENCIES = {
    "scripts/protocol_capacity.py",
    "scripts/route_capability.py",
}
REMOVED_PROVIDER_MODULES = {
    "scripts/chatgpt_pro_consult.py",
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
}
REQUIRED_PRODUCTION_MODULES = {
    "scripts/capability_reducer.py",
    "scripts/capability_v1_adapter.py",
    "scripts/compact_state_mapping.py",
    "scripts/capability_baseline_runtime.py",
}
REQUIRED_SURFACE_OWNERS: dict[str, str] = {
    "governance.toml": "target_binding",
    "scripts/target_binding.py": "target_binding",
    "scripts/route_manifest.py": "markdown_routes_and_mailbox_writer",
    "scripts/protocol_mailbox.py": "markdown_routes_and_mailbox_writer",
    "coordination/bin/send-event": "markdown_routes_and_mailbox_writer",
    "coordination/bin/consume-events": "markdown_routes_and_mailbox_writer",
    "scripts/route_compat.py": "typed_route_compatibility_canary",
    "scripts/protocol_capacity.py": "capacity_reducer_and_packet_state_telemetry",
    "scripts/packet_state.py": "capacity_reducer_and_packet_state_telemetry",
    "scripts/protocol_capacity_board.py": (
        "capacity_reducer_and_packet_state_telemetry"
    ),
    "scripts/protocol_effectiveness_report.py": "effectiveness_telemetry",
    "scripts/route_capability.py": "capability_receipt_recording",
    "scripts/verification_report_gate.py": (
        "verification_authority_and_publication"
    ),
    "scripts/consume_reviewer_result.py": (
        "verification_authority_and_publication"
    ),
    "scripts/compact_state_mapping.py": "legacy_lifecycle_mapping_contract",
    "scripts/capability_baseline_runtime.py": (
        "capability_baseline_runtime_collector"
    ),
    "scripts/capability_reducer.py": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
    "schemas/route-v2.schema.json": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
    "scripts/capability_v1_adapter.py": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
    "tests/fixtures/compact_kernel/v1_to_v2_replay.json": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
    "scripts/route_lineage.py": "live_v1_route_lineage_reader",
    "threeway/refstore.py": "signed_bus_event_and_cursor_runtime",
    "threeway/gate.py": "signed_bus_event_and_cursor_runtime",
    "threeway/cutover.py": "signed_bus_event_and_cursor_runtime",
    "threeway/keys_bootstrap.py": "signed_bus_event_and_cursor_runtime",
    "threeway/__init__.py": "signed_bus_event_and_cursor_runtime",
    "threeway/approval_authority.py": "signed_bus_event_and_cursor_runtime",
    "threeway/canon.py": "signed_bus_event_and_cursor_runtime",
    "threeway/cursor_backfill.py": "signed_bus_event_and_cursor_runtime",
    "threeway/envelope.py": "signed_bus_event_and_cursor_runtime",
    "threeway/gitcas.py": "signed_bus_event_and_cursor_runtime",
    "threeway/keys.py": "signed_bus_event_and_cursor_runtime",
    "threeway/legacy_projector.py": "signed_bus_event_and_cursor_runtime",
    "threeway/loop.py": "signed_bus_event_and_cursor_runtime",
    "threeway/policy.py": "signed_bus_event_and_cursor_runtime",
    "threeway/predicate.py": "signed_bus_event_and_cursor_runtime",
    "threeway/reducer.py": "signed_bus_event_and_cursor_runtime",
    "threeway/rework.py": "signed_bus_event_and_cursor_runtime",
    "threeway/store.py": "signed_bus_event_and_cursor_runtime",
    "threeway/tier.py": "signed_bus_event_and_cursor_runtime",
    "scripts/seat_emit.py": "signed_bus_event_and_cursor_runtime",
    "scripts/chief_emit.py": "signed_bus_event_and_cursor_runtime",
    "scripts/overseer_emit.py": "signed_bus_event_and_cursor_runtime",
    "scripts/sign_ci_result.py": "signed_bus_event_and_cursor_runtime",
    "scripts/consume_bus.py": "signed_bus_event_and_cursor_runtime",
    "scripts/run_merge_gate.py": "signed_bus_event_and_cursor_runtime",
    "scripts/run_merge_gate.sh": "signed_bus_event_and_cursor_runtime",
    "scripts/overseer_plan.py": "signed_bus_event_and_cursor_runtime",
    "scripts/agy_observer.py": "signed_bus_event_and_cursor_runtime",
    "scripts/bus_unread.py": "signed_bus_event_and_cursor_runtime",
    "scripts/execute_threeway_cutover.sh": "signed_bus_event_and_cursor_runtime",
    ".github/workflows/ci.yml": "signed_bus_event_and_cursor_runtime",
    "scripts/mailbox_monitor.py": "live_v1_status_and_runtime_readers",
    "scripts/check_coordination.py": "live_v1_status_and_runtime_readers",
    "scripts/check_doc_claims.py": "live_v1_status_and_runtime_readers",
    "scripts/ledger_start_guard.py": "live_v1_status_and_runtime_readers",
    "scripts/codex_protocol_model.py": "live_v1_status_and_runtime_readers",
    "scripts/protocol_doctor.py": "live_v1_status_and_runtime_readers",
    "scripts/continuation_readiness.py": "live_v1_status_and_runtime_readers",
    ".agents/skills/four-seat-protocol/scripts/seat_status.py": (
        "live_v1_status_and_runtime_readers"
    ),
    "scripts/status.py": "live_v1_status_and_runtime_readers",
    "scripts/latest_handoff.py": "live_v1_status_and_runtime_readers",
    "coordination/bin/claim-lock": "coordination_lock_effects",
    "coordination/bin/release-lock": "coordination_lock_effects",
    "coordination/bin/codex-seat": "codex_runtime_and_hook_adapter",
    "scripts/codex_seat_launcher.py": "codex_runtime_and_hook_adapter",
    ".codex/hooks.json": "codex_runtime_and_hook_adapter",
    ".codex/hooks/session-smoke.sh": "codex_runtime_and_hook_adapter",
    ".codex/hooks/guard-git-index.sh": "codex_runtime_and_hook_adapter",
    ".codex/hooks/update-state.sh": "codex_runtime_and_hook_adapter",
}
REQUIRED_WRITER_SURFACES = {
    "threeway/refstore.py",
    "threeway/gate.py",
    "threeway/cutover.py",
    "threeway/gitcas.py",
    "threeway/cursor_backfill.py",
    "threeway/keys_bootstrap.py",
    "scripts/seat_emit.py",
    "scripts/chief_emit.py",
    "scripts/overseer_emit.py",
    "scripts/sign_ci_result.py",
    "scripts/consume_bus.py",
    "scripts/run_merge_gate.py",
    "scripts/run_merge_gate.sh",
    "scripts/overseer_plan.py",
    "scripts/execute_threeway_cutover.sh",
    ".github/workflows/ci.yml",
}
REQUIRED_SYMBOL_OVERRIDES: dict[str, tuple[str, str, str]] = {
    "scripts.target_binding.main": (
        "target_binding",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.route_compat.main": (
        "typed_route_compatibility_canary",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.packet_state.is_valid_work_transition": (
        "capacity_reducer_and_packet_state_telemetry",
        "orphan",
        "integrate_or_delete_before_cutover",
    ),
    "scripts.packet_state.main": (
        "capacity_reducer_and_packet_state_telemetry",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.protocol_capacity_board.main": (
        "capacity_reducer_and_packet_state_telemetry",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.protocol_effectiveness_report.main": (
        "effectiveness_telemetry",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.route_capability.main": (
        "capability_receipt_recording",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.verification_report_gate.validate_live_report": (
        "verification_authority_and_publication",
        "orphan",
        "integrate_or_delete_before_cutover",
    ),
    "scripts.verification_report_gate.publish_candidate": (
        "verification_authority_and_publication",
        "orphan",
        "integrate_or_delete_before_cutover",
    ),
    "scripts.verification_report_gate.main": (
        "verification_authority_and_publication",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.consume_reviewer_result.main": (
        "verification_authority_and_publication",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.compact_state_mapping.main": (
        "legacy_lifecycle_mapping_contract",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.capability_baseline_runtime.main": (
        "capability_baseline_runtime_collector",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.capability_v1_adapter.main": (
        "compact_shadow_reducer_and_v1_adapter",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.route_lineage.check_cas": (
        "live_v1_route_lineage_reader",
        "orphan",
        "integrate_or_delete_before_cutover",
    ),
    "scripts.route_lineage.main": (
        "live_v1_route_lineage_reader",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "threeway.cutover.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "threeway.keys_bootstrap.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.seat_emit.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.chief_emit.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.overseer_emit.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.sign_ci_result.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.consume_bus.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.run_merge_gate.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.overseer_plan.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.agy_observer.main": (
        "signed_bus_event_and_cursor_runtime",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.mailbox_monitor.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.check_coordination.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.check_doc_claims.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.ledger_start_guard.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.codex_protocol_model.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.protocol_doctor.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.continuation_readiness.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    ".agents.skills.four-seat-protocol.scripts.seat_status.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.status.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.latest_handoff.main": (
        "live_v1_status_and_runtime_readers",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
    "scripts.codex_seat_launcher.main": (
        "codex_runtime_and_hook_adapter",
        "cli_entrypoint",
        "keep_documented_cli",
    ),
}

ROOT_KEYS = {"schema_version", "authority_contract", "components"}
COMPONENT_KEYS = {
    "id",
    "authority_status",
    "source_paths",
    "reader_paths",
    "writer_paths",
    "executor_boundary",
    "default_helper_class",
    "module_rules",
    "symbol_overrides",
}
MODULE_RULE_KEYS = {"path", "default_helper_class"}
OVERRIDE_KEYS = {"symbol", "helper_class", "disposition"}


def _load_inventory() -> dict[str, object]:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def _assert_nonempty_string(value: object, label: str) -> None:
    assert isinstance(value, str) and value.strip(), f"{label} must be non-empty"


def _assert_repo_path(value: object, label: str) -> str:
    _assert_nonempty_string(value, label)
    relative = Path(value)
    assert not relative.is_absolute(), f"{label} must be repository-relative"
    assert ".." not in relative.parts, f"{label} must not escape the repository"
    canonical = relative.as_posix()
    assert value == canonical, (
        f"{label} must use canonical repository-relative path: {canonical}"
    )
    assert (REPO_ROOT / relative).exists(), f"{label} does not exist: {value}"
    return canonical


def _module_name(path: str) -> str:
    return ".".join(Path(path).with_suffix("").parts)


def _public_functions(path: str) -> set[str]:
    source = (REPO_ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=path)
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }


_EXPLICIT_BARE_IMPORT_ROOTS = {
    ".agents/skills/four-seat-protocol/scripts/seat_status.py": ("scripts",),
}


def _resolve_repo_local_module(module_name: str) -> set[str]:
    parts = module_name.split(".")
    if (
        not parts
        or any(not part for part in parts)
        or parts[0] not in {"scripts", "threeway"}
    ):
        return set()

    module_path = REPO_ROOT.joinpath(*parts).with_suffix(".py")
    package_path = REPO_ROOT.joinpath(*parts, "__init__.py")
    target = (
        package_path
        if package_path.is_file()
        else module_path if module_path.is_file() else None
    )
    if target is None:
        return set()

    resolved = {target.relative_to(REPO_ROOT).as_posix()}
    for depth in range(1, len(parts)):
        initializer = REPO_ROOT.joinpath(*parts[:depth], "__init__.py")
        if initializer.is_file():
            resolved.add(initializer.relative_to(REPO_ROOT).as_posix())
    return resolved


def _direct_repo_local_imports(path: str) -> set[str]:
    source = (REPO_ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=path)
    imports: set[str] = set()
    module_parts = list(Path(path).with_suffix("").parts)
    package_parts = module_parts[:-1]
    direct_root = (
        module_parts[0]
        if len(module_parts) == 2
        and module_parts[0] in {"scripts", "threeway"}
        else None
    )
    bare_import_roots = tuple(
        dict.fromkeys(
            (
                *((direct_root,) if direct_root is not None else ()),
                *_EXPLICIT_BARE_IMPORT_ROOTS.get(path, ()),
            )
        )
    )

    def resolve(module_name: str, *, bare_fallback: bool) -> set[str]:
        resolved = _resolve_repo_local_module(module_name)
        if resolved or not bare_fallback:
            return resolved
        for root in bare_import_roots:
            resolved.update(_resolve_repo_local_module(f"{root}.{module_name}"))
        return resolved

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = resolve(
                    alias.name,
                    bare_fallback=True,
                )
                imports.update(resolved)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parent_count = len(package_parts) - node.level + 1
                if parent_count < 1:
                    continue
                base_parts = package_parts[:parent_count]
            else:
                base_parts = []
            if node.module:
                base_parts.extend(node.module.split("."))
            base_name = ".".join(base_parts)
            resolved_base = resolve(
                base_name,
                bare_fallback=node.level == 0,
            )
            imports.update(resolved_base)
            for alias in node.names:
                if alias.name == "*":
                    continue
                child_name = ".".join((*base_parts, alias.name))
                resolved_child = resolve(
                    child_name,
                    bare_fallback=node.level == 0,
                )
                imports.update(resolved_child)

    return imports


def _direct_import_ownership_failures(
    module_owners: dict[str, list[str]],
) -> list[tuple[str, str, list[str]]]:
    failures: list[tuple[str, str, list[str]]] = []
    for importer in sorted(module_owners):
        for imported in sorted(_direct_repo_local_imports(importer)):
            # Their live owners are intentionally removed before the sequential
            # decommission deletes the remaining downstream imports.
            if imported in REMOVED_PROVIDER_MODULES:
                continue
            owners = module_owners.get(imported, [])
            if len(owners) != 1:
                failures.append((importer, imported, owners))
    return failures


def test_mapping_direct_repo_local_imports_are_exact() -> None:
    assert _direct_repo_local_imports(
        "scripts/compact_state_mapping.py"
    ) == MAPPING_PRODUCER_DEPENDENCIES


def test_removed_provider_modules_are_not_live_inventory_dependencies_or_orphans() -> None:
    inventory = _load_inventory()
    declared_modules = {
        rule["path"]
        for component in inventory["components"]
        for rule in component["module_rules"]
    }
    orphan_modules = {
        symbol.rsplit(".", 1)[0].replace(".", "/") + ".py"
        for symbol in REQUIRED_ORPHANS
    }

    assert REMOVED_PROVIDER_MODULES.isdisjoint(REQUIRED_PRODUCTION_MODULES)
    assert REMOVED_PROVIDER_MODULES.isdisjoint(MAPPING_PRODUCER_DEPENDENCIES)
    assert REMOVED_PROVIDER_MODULES.isdisjoint(declared_modules)
    assert REMOVED_PROVIDER_MODULES.isdisjoint(orphan_modules)


def test_seat_status_direct_repo_local_imports_are_exact() -> None:
    assert _direct_repo_local_imports(
        ".agents/skills/four-seat-protocol/scripts/seat_status.py"
    ) == {
        "scripts/bus_unread.py",
        "scripts/codex_protocol_model.py",
        "scripts/latest_handoff.py",
        "scripts/protocol_mailbox.py",
    }


def test_unknown_bare_local_import_is_an_ownership_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "synthetic_importer.py").write_text(
        "import synthetic_dependency\n",
        encoding="utf-8",
    )
    (scripts_dir / "synthetic_dependency.py").write_text(
        "SENTINEL = True\n",
        encoding="utf-8",
    )
    monkeypatch.setitem(globals(), "REPO_ROOT", tmp_path)

    assert _direct_import_ownership_failures(
        {"scripts/synthetic_importer.py": ["synthetic_owner"]}
    ) == [
        (
            "scripts/synthetic_importer.py",
            "scripts/synthetic_dependency.py",
            [],
        )
    ]


def test_nested_seat_status_bare_aliased_import_is_an_ownership_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    importer_path = (
        ".agents/skills/four-seat-protocol/scripts/seat_status.py"
    )
    importer = tmp_path / importer_path
    importer.parent.mkdir(parents=True)
    importer.write_text(
        "def load():\n"
        "    import synthetic_dependency as alias\n"
        "    return alias.SENTINEL\n",
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "synthetic_dependency.py").write_text(
        "SENTINEL = True\n",
        encoding="utf-8",
    )
    monkeypatch.setitem(globals(), "REPO_ROOT", tmp_path)

    assert _direct_import_ownership_failures(
        {importer_path: ["synthetic_owner"]}
    ) == [
        (
            importer_path,
            "scripts/synthetic_dependency.py",
            [],
        )
    ]


@pytest.mark.parametrize(
    "statement",
    (
        "import scripts.pkg.child as alias\n",
        "from scripts.pkg import child as alias\n",
    ),
    ids=("import", "import-from"),
)
def test_dotted_imports_include_executable_package_initializers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    statement: str,
) -> None:
    scripts_dir = tmp_path / "scripts"
    package_dir = scripts_dir / "pkg"
    package_dir.mkdir(parents=True)
    (scripts_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "child.py").write_text("SENTINEL = True\n", encoding="utf-8")
    importer_path = "scripts/synthetic_importer.py"
    (tmp_path / importer_path).write_text(statement, encoding="utf-8")
    monkeypatch.setitem(globals(), "REPO_ROOT", tmp_path)

    assert _direct_repo_local_imports(importer_path) == {
        "scripts/__init__.py",
        "scripts/pkg/__init__.py",
        "scripts/pkg/child.py",
    }
    assert _direct_import_ownership_failures(
        {
            importer_path: ["synthetic_owner"],
            "scripts/pkg/child.py": ["child_owner"],
        }
    ) == [
        (importer_path, "scripts/__init__.py", []),
        (importer_path, "scripts/pkg/__init__.py", []),
    ]


def test_package_initializer_precedes_same_named_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripts_dir = tmp_path / "scripts"
    package_dir = scripts_dir / "pkg"
    package_dir.mkdir(parents=True)
    (scripts_dir / "__init__.py").write_text("", encoding="utf-8")
    (scripts_dir / "pkg.py").write_text("MODULE = True\n", encoding="utf-8")
    (package_dir / "__init__.py").write_text("PACKAGE = True\n", encoding="utf-8")
    monkeypatch.setitem(globals(), "REPO_ROOT", tmp_path)

    assert _resolve_repo_local_module("scripts.pkg") == {
        "scripts/__init__.py",
        "scripts/pkg/__init__.py",
    }


def test_live_status_reader_inventory_discloses_local_writers() -> None:
    component = next(
        item
        for item in _load_inventory()["components"]
        if item["id"] == "live_v1_status_and_runtime_readers"
    )

    assert component["authority_status"] == (
        "live_v1_status_readers_with_explicit_local_writes"
    )
    assert set(component["writer_paths"]) == {
        "scripts/check_doc_claims.py",
        "scripts/status.py",
    }
    assert "status.py --write" in component["executor_boundary"]
    assert "check_doc_claims.py --fix" in component["executor_boundary"]
    assert "local writes" in component["executor_boundary"]


def test_repository_paths_reject_noncanonical_module_aliases() -> None:
    with pytest.raises(AssertionError, match="canonical"):
        _assert_repo_path(
            "scripts/./target_binding.py",
            "aliased module path",
        )


def test_route_lineage_runtime_helpers_are_runtime_core() -> None:
    components = _load_inventory()["components"]
    component = next(
        item
        for item in components
        if item["id"] == "live_v1_route_lineage_reader"
    )
    rule = next(
        item
        for item in component["module_rules"]
        if item["path"] == "scripts/route_lineage.py"
    )
    module_default = rule.get(
        "default_helper_class", component["default_helper_class"]
    )
    overrides = {
        override["symbol"].rpartition(".")[2]: override
        for override in component["symbol_overrides"]
        if override["symbol"].startswith("scripts.route_lineage.")
    }
    classifications = {
        function: overrides.get(function, {}).get("helper_class", module_default)
        for function in _public_functions("scripts/route_lineage.py")
    }

    assert {
        function
        for function, helper_class in classifications.items()
        if helper_class == "orphan"
    } == {"check_cas"}
    runtime_helpers = set(classifications) - {"check_cas", "main"}
    assert runtime_helpers
    assert {
        classifications[function] for function in runtime_helpers
    } == {"runtime_core"}


def test_five_profile_baseline_is_read_only_effectiveness_telemetry() -> None:
    components = _load_inventory()["components"]
    component = next(
        item for item in components if item["id"] == "effectiveness_telemetry"
    )
    baseline = "scripts/baselines/capability_first_five_profile_v1.json"

    assert baseline in component["source_paths"]
    assert baseline in component["reader_paths"]
    assert baseline not in component["writer_paths"]
    assert baseline not in {rule["path"] for rule in component["module_rules"]}


def test_required_production_modules_have_explicit_inventory_owners() -> None:
    declared_modules = {
        rule["path"]
        for component in _load_inventory()["components"]
        for rule in component["module_rules"]
    }

    assert REQUIRED_PRODUCTION_MODULES <= declared_modules


@pytest.mark.parametrize(
    ("path", "expected_owner"),
    sorted(REQUIRED_SURFACE_OWNERS.items()),
)
def test_required_surfaces_have_explicit_owner(path, expected_owner):
    components = _load_inventory()["components"]
    owners = [
        component["id"]
        for component in components
        if path
        in (
            {rule["path"] for rule in component["module_rules"]}
            if path.endswith(".py")
            else set(component["source_paths"])
        )
    ]
    assert owners == [expected_owner]


@pytest.mark.parametrize("path", sorted(REQUIRED_WRITER_SURFACES))
def test_required_writer_surfaces_have_signed_bus_owner(path: str) -> None:
    owners = [
        component["id"]
        for component in _load_inventory()["components"]
        if path in component["writer_paths"]
    ]

    assert owners == ["signed_bus_event_and_cursor_runtime"]


def test_classified_modules_close_over_direct_repo_local_imports() -> None:
    components = _load_inventory()["components"]
    module_owners: dict[str, list[str]] = {}
    for component in components:
        for rule in component["module_rules"]:
            module_owners.setdefault(rule["path"], []).append(component["id"])

    ownership_failures = _direct_import_ownership_failures(module_owners)

    assert not ownership_failures, (
        "classified modules have direct local imports without exactly one "
        f"module-rule owner: {ownership_failures}"
    )


def test_required_symbol_overrides_are_exactly_pinned() -> None:
    actual = {
        override["symbol"]: (
            component["id"],
            override["helper_class"],
            override["disposition"],
        )
        for component in _load_inventory()["components"]
        for override in component["symbol_overrides"]
    }

    assert actual == REQUIRED_SYMBOL_OVERRIDES


def test_mapping_contract_is_explicitly_read_only_telemetry() -> None:
    components = {
        component["id"]: component
        for component in _load_inventory()["components"]
    }
    component_id = "legacy_lifecycle_mapping_contract"
    assert component_id in READ_ONLY_COMPONENT_IDS
    assert component_id in components
    component = components[component_id]
    owned_paths = {
        "scripts/compact_state_mapping.py",
        "tests/fixtures/compact_state_mapping/v1.json",
        "tests/fixtures/compact_kernel/v1_misuse_vectors.json",
    }

    assert set(component["source_paths"]) == owned_paths
    assert set(component["reader_paths"]) == (
        owned_paths | MAPPING_PRODUCER_DEPENDENCIES
    )
    assert component["writer_paths"] == []
    assert component["default_helper_class"] == "telemetry"
    assert component["module_rules"] == [
        {"path": "scripts/compact_state_mapping.py"}
    ]
    assert component["symbol_overrides"] == [
        {
            "symbol": "scripts.compact_state_mapping.main",
            "helper_class": "cli_entrypoint",
            "disposition": "keep_documented_cli",
        }
    ]
    assert "imported only for observation" in component["executor_boundary"]
    assert (
        "no writer or effect entrypoint is invoked"
        in component["executor_boundary"]
    )


def test_compact_shadow_reducer_and_adapter_are_read_only_compatibility() -> None:
    component = next(
        item
        for item in _load_inventory()["components"]
        if item["id"] == "compact_shadow_reducer_and_v1_adapter"
    )
    source_paths = {
        "scripts/capability_reducer.py",
        "schemas/route-v2.schema.json",
        "scripts/capability_v1_adapter.py",
        "tests/fixtures/compact_kernel/v1_to_v2_replay.json",
    }
    reader_fixtures = {
        "tests/fixtures/compact_state_mapping/v1.json",
        "tests/fixtures/compact_kernel/v1_misuse_vectors.json",
        "tests/fixtures/compact_kernel/v2_replay_vectors.json",
    }

    assert component["authority_status"] == (
        "non_authoritative_read_only_shadow_compatibility"
    )
    assert set(component["source_paths"]) == source_paths
    assert set(component["reader_paths"]) == (
        source_paths
        | reader_fixtures
        | {"scripts/compact_state_mapping.py"}
    )
    assert component["writer_paths"] == []
    assert component["default_helper_class"] == "historical_adapter"
    assert component["module_rules"] == [
        {
            "path": "scripts/capability_reducer.py",
            "default_helper_class": "runtime_core",
        },
        {"path": "scripts/capability_v1_adapter.py"},
    ]
    assert component["symbol_overrides"] == [
        {
            "symbol": "scripts.capability_v1_adapter.main",
            "helper_class": "cli_entrypoint",
            "disposition": "keep_documented_cli",
        }
    ]
    assert "imported only for observation" in component["executor_boundary"]
    assert (
        "no provider, writer, or effect entrypoint is invoked"
        in component["executor_boundary"]
    )

    adapter_imports = _direct_repo_local_imports(
        "scripts/capability_v1_adapter.py"
    )
    reducer_imports = _direct_repo_local_imports("scripts/capability_reducer.py")
    assert "scripts/capability_reducer.py" in adapter_imports
    assert "scripts/capability_v1_adapter.py" not in reducer_imports


def test_runtime_collector_is_a_non_authoritative_benchmark_executor() -> None:
    component = next(
        item
        for item in _load_inventory()["components"]
        if item["id"] == "capability_baseline_runtime_collector"
    )
    module = "scripts/capability_baseline_runtime.py"

    assert component["authority_status"] == "non_authoritative_benchmark_executor"
    assert component["source_paths"] == [module]
    assert set(component["reader_paths"]) == {
        module,
        "scripts/baselines/capability_first_five_profile_v1.json",
        "scripts/protocol_effectiveness_report.py",
    }
    assert component["writer_paths"] == [module]
    assert component["default_helper_class"] == "telemetry"
    assert component["module_rules"] == [{"path": module}]
    assert component["symbol_overrides"] == [
        {
            "symbol": "scripts.capability_baseline_runtime.main",
            "helper_class": "cli_entrypoint",
            "disposition": "keep_documented_cli",
        }
    ]
    assert _public_functions(module) == {
        "hook_main",
        "parse_runtime_trace",
        "run_one",
        "run_cohort",
        "main",
    }
    boundary = component["executor_boundary"]
    for phrase in (
        "minimal read-only workspaces",
        "one writable fixture directory",
        "reserved nonce marker",
        "parent benchmark evidence",
        "no live authority",
    ):
        assert phrase in boundary


def test_inventory_schema_authority_and_paths() -> None:
    inventory = _load_inventory()

    assert set(inventory) == ROOT_KEYS
    assert inventory["schema_version"] == SCHEMA_VERSION
    assert inventory["authority_contract"] == AUTHORITY_CONTRACT

    components = inventory["components"]
    assert isinstance(components, list) and components
    component_ids = [component["id"] for component in components]
    assert len(component_ids) == len(set(component_ids)), "duplicate component id"
    assert set(component_ids) == COMPONENT_IDS

    for component in components:
        assert isinstance(component, dict)
        assert set(component) == COMPONENT_KEYS
        component_id = component["id"]
        _assert_nonempty_string(component_id, "component id")
        _assert_nonempty_string(
            component["authority_status"], f"{component_id}.authority_status"
        )
        _assert_nonempty_string(
            component["executor_boundary"], f"{component_id}.executor_boundary"
        )

        default_class = component["default_helper_class"]
        assert default_class in HELPER_CLASSES
        assert default_class != "orphan", "orphans require explicit symbol overrides"

        for field in ("source_paths", "reader_paths", "writer_paths"):
            paths = component[field]
            assert isinstance(paths, list), f"{component_id}.{field} is not a list"
            if field == "writer_paths" and component_id in READ_ONLY_COMPONENT_IDS:
                assert paths == [], f"{component_id}.{field} must be empty"
            else:
                assert paths, f"{component_id}.{field} is empty"
            assert len(paths) == len(set(paths)), f"{component_id}.{field} has duplicates"
            for index, path in enumerate(paths):
                _assert_repo_path(path, f"{component_id}.{field}[{index}]")

        module_rules = component["module_rules"]
        assert isinstance(module_rules, list)
        python_sources = {
            path for path in component["source_paths"] if path.endswith(".py")
        }
        if python_sources:
            assert module_rules
        else:
            assert module_rules == []
        for rule in module_rules:
            assert isinstance(rule, dict)
            assert set(rule).issubset(MODULE_RULE_KEYS)
            assert "path" in rule
            path = _assert_repo_path(rule["path"], f"{component_id}.module_rules.path")
            assert path.endswith(".py")
            if "default_helper_class" in rule:
                assert rule["default_helper_class"] in HELPER_CLASSES
                assert rule["default_helper_class"] != "orphan"

        rule_paths = {rule["path"] for rule in module_rules}
        assert rule_paths == python_sources, (
            f"{component_id} must have one module rule for every scoped Python source"
        )

        overrides = component["symbol_overrides"]
        assert isinstance(overrides, list)
        for override in overrides:
            assert isinstance(override, dict)
            assert set(override) == OVERRIDE_KEYS
            _assert_nonempty_string(
                override["symbol"], f"{component_id}.symbol_overrides.symbol"
            )
            assert override["helper_class"] in HELPER_CLASSES
            _assert_nonempty_string(
                override["disposition"],
                f"{component_id}.symbol_overrides.disposition",
            )


def test_every_scoped_public_function_is_classified() -> None:
    components = _load_inventory()["components"]
    module_owner: dict[str, str] = {}
    module_default: dict[str, str] = {}
    module_paths_by_key: dict[str, str] = {}
    public_symbols: set[str] = set()
    overrides: dict[str, dict[str, str]] = {}

    for component in components:
        component_id = component["id"]
        owned_modules: set[str] = set()
        for rule in component["module_rules"]:
            path = rule["path"]
            assert path not in module_owner, (
                f"duplicate module ownership: {path} belongs to "
                f"{module_owner.get(path)} and {component_id}"
            )
            module_owner[path] = component_id
            module_default[path] = rule.get(
                "default_helper_class", component["default_helper_class"]
            )
            module_name = _module_name(path)
            assert module_name not in module_paths_by_key
            module_paths_by_key[module_name] = path
            owned_modules.add(module_name)
            public_symbols.update(
                f"{module_name}.{function}" for function in _public_functions(path)
            )

        for override in component["symbol_overrides"]:
            symbol = override["symbol"]
            assert symbol not in overrides, f"duplicate symbol override: {symbol}"
            module_name, _, function_name = symbol.rpartition(".")
            assert module_name in owned_modules, (
                f"override belongs to an unowned module: {symbol}"
            )
            module_path = module_paths_by_key[module_name]
            assert function_name in _public_functions(module_path), (
                f"override names an unknown public function: {symbol}"
            )
            overrides[symbol] = override

    assert REQUIRED_ORPHANS <= public_symbols, "a required orphan symbol disappeared"
    assert REQUIRED_ORPHANS <= overrides.keys(), "required orphans need explicit overrides"

    for path, default_class in module_default.items():
        module_name = _module_name(path)
        for function_name in _public_functions(path):
            symbol = f"{module_name}.{function_name}"
            helper_class = overrides.get(symbol, {}).get(
                "helper_class", default_class
            )
            assert helper_class in HELPER_CLASSES, f"unclassified function: {symbol}"

    for symbol, override in overrides.items():
        assert symbol in public_symbols, f"unknown override: {symbol}"
        if override["helper_class"] == "orphan":
            assert override["disposition"] == ORPHAN_DISPOSITION

    for symbol in REQUIRED_ORPHANS:
        assert overrides[symbol]["helper_class"] == "orphan"
        assert overrides[symbol]["disposition"] == ORPHAN_DISPOSITION
