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
    "chatgpt_guard_and_browser_executor",
    "opus_reservation_and_bridge",
    "dormant_signed_bus_ref_cas_substrate",
    "legacy_lifecycle_mapping_contract",
    "capability_baseline_runtime_collector",
}
AUTHORITY_CONTRACT = {
    "route_authority": "markdown_mailbox",
    "route_sidecar_role": "compatibility_only",
    "signed_bus_role": "dormant_for_migration",
    "capability_consumption_role": "post_effect_evidence_only",
    "provider_output_role": "advisory_only",
}
ORPHAN_DISPOSITION = "integrate_or_delete_before_cutover"
REQUIRED_ORPHANS = {
    "scripts.packet_state.is_valid_work_transition",
    "scripts.route_lineage.check_cas",
    "scripts.verification_report_gate.validate_live_report",
    "scripts.verification_report_gate.publish_candidate",
    "scripts.opus_review_bridge.probe_host_capabilities",
}
READ_ONLY_COMPONENT_ID = "legacy_lifecycle_mapping_contract"
REQUIRED_PHASE1_PRODUCTION_MODULES = {
    "scripts/compact_state_mapping.py",
    "scripts/capability_baseline_runtime.py",
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
        if item["id"] == "dormant_signed_bus_ref_cas_substrate"
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


def test_phase1_production_modules_have_explicit_inventory_owners() -> None:
    declared_modules = {
        rule["path"]
        for component in _load_inventory()["components"]
        for rule in component["module_rules"]
    }

    assert REQUIRED_PHASE1_PRODUCTION_MODULES <= declared_modules


def test_mapping_contract_is_explicitly_read_only_telemetry() -> None:
    components = {
        component["id"]: component
        for component in _load_inventory()["components"]
    }
    assert READ_ONLY_COMPONENT_ID in components
    component = components[READ_ONLY_COMPONENT_ID]
    owned_paths = {
        "scripts/compact_state_mapping.py",
        "tests/fixtures/compact_state_mapping/v1.json",
        "tests/fixtures/compact_kernel/v1_misuse_vectors.json",
    }

    assert set(component["source_paths"]) == owned_paths
    assert set(component["reader_paths"]) == owned_paths
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
            if field == "writer_paths" and component_id == READ_ONLY_COMPONENT_ID:
                assert paths == [], f"{component_id}.{field} must be empty"
            else:
                assert paths, f"{component_id}.{field} is empty"
            assert len(paths) == len(set(paths)), f"{component_id}.{field} has duplicates"
            for index, path in enumerate(paths):
                _assert_repo_path(path, f"{component_id}.{field}[{index}]")

        module_rules = component["module_rules"]
        assert isinstance(module_rules, list) and module_rules
        for rule in module_rules:
            assert isinstance(rule, dict)
            assert set(rule).issubset(MODULE_RULE_KEYS)
            assert "path" in rule
            path = _assert_repo_path(rule["path"], f"{component_id}.module_rules.path")
            assert path.endswith(".py")
            if "default_helper_class" in rule:
                assert rule["default_helper_class"] in HELPER_CLASSES
                assert rule["default_helper_class"] != "orphan"

        python_sources = {
            path for path in component["source_paths"] if path.endswith(".py")
        }
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
            module_path = module_name.replace(".", "/") + ".py"
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
