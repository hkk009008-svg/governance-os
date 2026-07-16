from __future__ import annotations

import dataclasses
import errno
import hashlib
import json
import multiprocessing
import os
import stat
import subprocess
import traceback
from pathlib import Path

import pytest

import opus_review_receipts as receipts


TASK_ID = "9655cc07-e71a-4ca4-9201-5492be8bb91f"
BASE = "a" * 40
HEAD = "b" * 40
TRIGGER = "c" * 40
DESCRIPTOR_BLOB = "d" * 40
REQUIREMENT_BLOB = "e" * 40
DESCRIPTOR_DIGEST = "sha256:" + "1" * 64
REQUIREMENT_DIGEST = "sha256:" + "2" * 64
REPOSITORY_IDENTITY = "sha256:" + "3" * 64
DESCRIPTOR_PATH = f"coordination/verification/scopes/{TASK_ID}.json"
CMD_A = (
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
    "tests/unit/test_opus_review_receipts.py -q"
)
CMD_B = "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"


def _provider_prompt_mapping() -> dict[str, object]:
    return {
        "authority_path": (
            "scripts/prompts/opus_lane_v_advisory.authority."
            + "4" * 40
            + ".json"
        ),
        "authority_blob_oid": "4" * 40,
        "authority_digest": "sha256:" + "5" * 64,
        "authority_size_bytes": 512,
        "prompt_path": "scripts/prompts/opus_lane_v_advisory.md",
        "prompt_blob_oid": "6" * 40,
        "file_sha256": "sha256:" + "7" * 64,
        "file_size_bytes": 3034,
        "body_sha256": "sha256:" + "8" * 64,
        "body_size_bytes": 2917,
    }


def _descriptor_mapping() -> dict[str, object]:
    return {
        "schema_version": "lane-v-scope/v1",
        "task_id": TASK_ID,
        "question_id": "opus-lanev-receipt-hardening",
        "trigger_kind": "shipping-commit",
        "verification_mode": "codex-lane-v",
        "verification_harness": "codex:lane-v-verifier",
        "review_profile": "codex-lane-v",
        "reviewed_base": {"policy": "exact", "commit": BASE},
        "requirement_paths": ["AGENTS.md", "docs/protocol"],
        "allowed_path_roots": ["scripts", "tests/unit"],
        "verification_commands": [CMD_A, CMD_B],
    }


def _review_scope(
    *,
    commands: tuple[str, ...] = (CMD_A, CMD_B),
    allowed: tuple[str, ...] = ("scripts", "tests/unit"),
) -> receipts.ReviewScope:
    return receipts.ReviewScope(
        repository_identity=REPOSITORY_IDENTITY,
        task_id=TASK_ID,
        question_id="opus-lanev-receipt-hardening",
        trigger_kind="shipping-commit",
        trigger_identity=f"shipping-commit:{TRIGGER}",
        trigger_commit=TRIGGER,
        trigger_path=None,
        trigger_blob_id=None,
        descriptor_path=DESCRIPTOR_PATH,
        descriptor_digest=DESCRIPTOR_DIGEST,
        descriptor_blob_id=DESCRIPTOR_BLOB,
        review_profile="codex-lane-v",
        verification_mode="codex-lane-v",
        verification_harness="codex:lane-v-verifier",
        authorization_identity="user-task:receipt-hardening",
        reviewed_head=HEAD,
        requested_base=BASE,
        effective_base=BASE,
        changed_paths=(
            receipts.ChangedPath(
                "M",
                "scripts/opus_review_receipts.py",
                b"scripts/opus_review_receipts.py",
            ),
        ),
        requirements=(
            {
                "path": "AGENTS.md",
                "blob_id": REQUIREMENT_BLOB,
                "digest": REQUIREMENT_DIGEST,
            },
        ),
        allowed_path_roots=allowed,
        verification_commands=commands,
    )


def test_provider_prompt_facts_are_optional_strict_and_scope_bound() -> None:
    legacy = _review_scope()
    legacy_mapping = legacy.to_mapping()
    assert "provider_prompt" not in legacy_mapping
    assert receipts.review_scope_from_mapping(legacy_mapping) == legacy

    prompt = receipts.ProviderPromptFacts.from_mapping(
        _provider_prompt_mapping()
    )
    bound = dataclasses.replace(legacy, provider_prompt=prompt)
    bound_mapping = bound.to_mapping()

    assert bound_mapping["provider_prompt"] == _provider_prompt_mapping()
    assert receipts.review_scope_from_mapping(bound_mapping) == bound
    assert receipts.compute_attempt_key(bound) == receipts.compute_attempt_key(legacy)
    assert receipts.compute_scope_digest(bound) != receipts.compute_scope_digest(legacy)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authority_size_bytes", True),
        ("file_size_bytes", False),
        ("body_size_bytes", True),
        ("authority_blob_oid", "A" * 40),
        ("prompt_blob_oid", "6" * 39),
        ("prompt_path", "../opus_lane_v_advisory.md"),
        ("file_sha256", "7" * 64),
    ],
)
def test_provider_prompt_facts_reject_malformed_values(
    field: str, value: object
) -> None:
    mapping = _provider_prompt_mapping()
    mapping[field] = value

    with pytest.raises(
        receipts.ReceiptContractError, match="invalid_provider_prompt"
    ):
        receipts.ProviderPromptFacts.from_mapping(mapping)


def test_same_attempt_rejects_descriptor_bound_prompt_drift(tmp_path: Path) -> None:
    original_prompt = receipts.ProviderPromptFacts.from_mapping(
        _provider_prompt_mapping()
    )
    original = dataclasses.replace(
        _review_scope(), provider_prompt=original_prompt
    )
    changed_mapping = _provider_prompt_mapping()
    changed_mapping["body_sha256"] = "sha256:" + "9" * 64
    changed = dataclasses.replace(
        original,
        provider_prompt=receipts.ProviderPromptFacts.from_mapping(
            changed_mapping
        ),
    )
    store = receipts.ReceiptStore(tmp_path / "state")

    with store.lock_attempt(original, blocking=False) as attempt:
        attempt.reserve_or_load(original)
    with store.lock_attempt(changed, blocking=False) as attempt:
        with pytest.raises(
            receipts.ReceiptStateError, match="attempt_scope_conflict"
        ):
            attempt.reserve_or_load(changed)


def test_scope_descriptor_rejects_duplicate_and_unknown_fields() -> None:
    duplicate = b'{"schema_version":"lane-v-scope/v1","task_id":"a","task_id":"b"}'
    with pytest.raises(receipts.ReceiptContractError, match="duplicate_json_key"):
        receipts.strict_json_loads(duplicate)

    value = _descriptor_mapping()
    value["unexpected"] = True
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


def test_strict_json_loads_rejects_invalid_utf8_constants_and_oversize() -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_json"):
        receipts.strict_json_loads(b'"bad-\xff"')
    with pytest.raises(receipts.ReceiptContractError, match="invalid_json"):
        receipts.strict_json_loads(b'{"value":NaN}')
    with pytest.raises(receipts.ReceiptContractError, match="descriptor_too_large"):
        receipts.strict_json_loads(b" " * 65_537)


def test_scope_descriptor_normalizes_unordered_collections() -> None:
    value = _descriptor_mapping()
    value["requirement_paths"] = ["docs/protocol", "AGENTS.md", "AGENTS.md"]
    value["allowed_path_roots"] = ["tests/unit", "scripts", "scripts"]
    value["verification_commands"] = [CMD_B, CMD_A, CMD_A]

    descriptor = receipts.ScopeDescriptor.from_mapping(value)

    assert descriptor.requirement_paths == ("AGENTS.md", "docs/protocol")
    assert descriptor.allowed_path_roots == ("scripts", "tests/unit")
    assert descriptor.verification_commands == (CMD_A, CMD_B)


def test_scope_descriptor_applies_collection_limits_after_deduplication() -> None:
    value = _descriptor_mapping()
    value["requirement_paths"] = ["AGENTS.md"] * 129
    value["allowed_path_roots"] = ["scripts"] * 129
    value["verification_commands"] = [CMD_A] * 33

    descriptor = receipts.ScopeDescriptor.from_mapping(value)

    assert descriptor.requirement_paths == ("AGENTS.md",)
    assert descriptor.allowed_path_roots == ("scripts",)
    assert descriptor.verification_commands == (CMD_A,)


@pytest.mark.parametrize(
    "task_id",
    [
        "not-a-uuid",
        "9655CC07-E71A-4CA4-9201-5492BE8BB91F",
        "{9655cc07-e71a-4ca4-9201-5492be8bb91f}",
    ],
)
def test_scope_descriptor_requires_canonical_uuid(task_id: str) -> None:
    value = _descriptor_mapping()
    value["task_id"] = task_id
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


@pytest.mark.parametrize(
    ("mode", "harness", "profile"),
    [
        ("codex-lane-v", "claude:lane-v-verifier", "codex-lane-v"),
        ("codex-lane-v", "codex:lane-v-verifier", "claude-lane-v"),
        ("claude-lane-v", "codex:lane-v-verifier", "claude-lane-v"),
        ("other", "other:lane-v-verifier", "other"),
    ],
)
def test_scope_descriptor_rejects_unsupported_mode_harness_profile_pairs(
    mode: str, harness: str, profile: str
) -> None:
    value = _descriptor_mapping()
    value.update(
        verification_mode=mode,
        verification_harness=harness,
        review_profile=profile,
    )
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


def test_scope_descriptor_accepts_supported_claude_pair() -> None:
    value = _descriptor_mapping()
    value.update(
        verification_mode="claude-lane-v",
        verification_harness="claude:lane-v-verifier",
        review_profile="claude-lane-v",
    )
    descriptor = receipts.ScopeDescriptor.from_mapping(value)
    assert descriptor.verification_mode == "claude-lane-v"


def test_scope_descriptor_accepts_provider_free_codex_pair() -> None:
    value = _descriptor_mapping()
    value.update(
        verification_mode="codex-provider-free-lane-v",
        verification_harness="codex:lane-v-verifier",
        review_profile="codex-provider-free-lane-v",
    )
    descriptor = receipts.ScopeDescriptor.from_mapping(value)
    assert descriptor.verification_mode == receipts.CODEX_PROVIDER_FREE_MODE


@pytest.mark.parametrize(
    ("harness", "profile"),
    [
        ("claude:lane-v-verifier", "codex-provider-free-lane-v"),
        ("codex:lane-v-verifier", "codex-lane-v"),
        ("codex:lane-v-verifier", "claude-lane-v"),
    ],
)
def test_scope_descriptor_rejects_mixed_provider_free_pair(harness, profile):
    value = _descriptor_mapping()
    value.update(
        verification_mode="codex-provider-free-lane-v",
        verification_harness=harness,
        review_profile=profile,
    )
    with pytest.raises(receipts.ReceiptContractError):
        receipts.ScopeDescriptor.from_mapping(value)


def test_compute_attempt_key_rejects_provider_free_mode() -> None:
    scope = dataclasses.replace(
        _review_scope(),
        verification_mode="codex-provider-free-lane-v",
        review_profile="codex-provider-free-lane-v",
    )
    with pytest.raises(receipts.ReceiptContractError, match="invalid_review_scope"):
        receipts.compute_attempt_key(scope)


def test_lock_attempt_rejects_provider_free_mode_before_receipt_state(
    tmp_path: Path,
) -> None:
    scope = dataclasses.replace(
        _review_scope(),
        verification_mode="codex-provider-free-lane-v",
        review_profile="codex-provider-free-lane-v",
    )
    state_root = tmp_path / "state"
    store = receipts.ReceiptStore(state_root)

    with pytest.raises(receipts.ReceiptContractError, match="invalid_review_scope"):
        with store.lock_attempt(scope, blocking=False):
            pytest.fail("provider-free scope reached the receipt lock context")

    assert not state_root.exists()
    assert tuple(tmp_path.rglob("*.lock")) == ()
    assert tuple(tmp_path.rglob("*.json")) == ()


def test_scope_descriptor_rejects_non_string_verifier_fields() -> None:
    value = _descriptor_mapping()
    value["verification_mode"] = []
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


@pytest.mark.parametrize(
    "reviewed_base",
    [
        {"policy": "exact"},
        {"commit": BASE},
        {"policy": "exact", "commit": BASE, "extra": True},
        {"policy": "first-parent", "commit": BASE},
        {"policy": "exact", "commit": BASE.upper()},
    ],
)
def test_scope_descriptor_requires_both_exact_base_fields(
    reviewed_base: dict[str, object]
) -> None:
    value = _descriptor_mapping()
    value["reviewed_base"] = reviewed_base
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


@pytest.mark.parametrize(
    "question_id",
    ["", "-leading", "contains/slash", "contains space", "a" * 129],
)
def test_scope_descriptor_rejects_invalid_question_ids(question_id: str) -> None:
    value = _descriptor_mapping()
    value["question_id"] = question_id
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("requirement_paths", []),
        ("requirement_paths", [f"docs/{index}" for index in range(129)]),
        ("allowed_path_roots", []),
        ("allowed_path_roots", [f"allowed/{index}" for index in range(129)]),
        ("verification_commands", []),
        (
            "verification_commands",
            [
                f"env -u GIT_INDEX_FILE .venv/bin/python scripts/check_{index}.py"
                for index in range(33)
            ],
        ),
    ],
)
def test_scope_descriptor_rejects_empty_or_oversized_collections(
    field: str, value: list[str]
) -> None:
    mapping = _descriptor_mapping()
    mapping[field] = value
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize("field", ["requirement_paths", "allowed_path_roots"])
def test_scope_descriptor_rejects_path_items_over_512_utf8_bytes(field: str) -> None:
    mapping = _descriptor_mapping()
    mapping[field] = ["é" * 257]
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(mapping)


def test_scope_descriptor_rejects_command_items_over_4096_utf8_bytes() -> None:
    mapping = _descriptor_mapping()
    mapping["verification_commands"] = [
        "env -u GIT_INDEX_FILE .venv/bin/python " + "a" * 4_097
    ]
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize(
    "command",
    [
        "",
        "pytest tests/unit",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py; echo bad",
        "env -u GIT_INDEX_FILE .venv/bin/python tests/*.py",
        "env -u GIT_INDEX_FILE .venv/bin/python 'unterminated",
    ],
)
def test_scope_descriptor_rejects_invalid_command_strings(command: str) -> None:
    mapping = _descriptor_mapping()
    mapping["verification_commands"] = [command]
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(mapping)


def test_scope_reference_and_trigger_identities_are_exact() -> None:
    reference = receipts.parse_scope_reference(
        f"{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}"
    )
    assert reference == receipts.ScopeReference(DESCRIPTOR_PATH, DESCRIPTOR_DIGEST)
    assert receipts.canonical_trigger_identity("shipping-commit", TRIGGER) == (
        f"shipping-commit:{TRIGGER}"
    )
    event = "coordination/mailbox/sent/0042-director-to-operator-verification-request.md"
    assert receipts.canonical_trigger_identity(
        "verify-request", TRIGGER, event
    ) == f"verify-request:{TRIGGER}:{event}"


@pytest.mark.parametrize(
    "reference",
    [
        DESCRIPTOR_PATH,
        f"./{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}",
        f"{DESCRIPTOR_PATH}@sha256:{'A' * 64}",
        f"{DESCRIPTOR_PATH}@sha256:{'1' * 63}",
    ],
)
def test_scope_reference_rejects_decorated_or_partial_values(reference: str) -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_reference"):
        receipts.parse_scope_reference(reference)


@pytest.mark.parametrize(
    ("kind", "commit", "path"),
    [
        ("shipping-commit", TRIGGER.upper(), None),
        ("shipping-commit", TRIGGER, "event.md"),
        ("verify-request", TRIGGER, None),
        ("verify-request", TRIGGER, "./event.md"),
        ("other", TRIGGER, None),
    ],
)
def test_trigger_identity_rejects_noncanonical_inputs(
    kind: str, commit: str, path: str | None
) -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_trigger_identity"):
        receipts.canonical_trigger_identity(kind, commit, path)


def test_canonical_json_bytes_are_sorted_compact_and_utf8() -> None:
    assert receipts.canonical_json_bytes({"z": 1, "é": "✓", "a": 2}) == (
        '{"a":2,"z":1,"é":"✓"}'.encode()
    )


def test_attempt_key_ignores_scope_order_but_scope_digest_tracks_every_input() -> None:
    left = _review_scope(commands=(CMD_B, CMD_A), allowed=("scripts", "tests/unit"))
    reordered = _review_scope(
        commands=(CMD_A, CMD_B, CMD_A), allowed=("tests/unit", "scripts")
    )
    assert receipts.compute_attempt_key(left) == receipts.compute_attempt_key(reordered)
    assert receipts.compute_scope_digest(left) == receipts.compute_scope_digest(reordered)

    changed = dataclasses.replace(left, authorization_identity="user-task:other")
    assert receipts.compute_attempt_key(left) == receipts.compute_attempt_key(changed)
    assert receipts.compute_scope_digest(left) != receipts.compute_scope_digest(changed)


def test_public_review_scope_normalizer_round_trips_exact_typed_scope() -> None:
    scope = _review_scope()

    normalized = receipts.review_scope_from_mapping(scope.to_mapping())

    assert normalized == scope


@pytest.mark.parametrize("mutation", ["unknown", "wrong-type", "noncanonical"])
def test_public_review_scope_normalizer_rejects_malformed_stored_scope(
    mutation: str,
) -> None:
    value = _review_scope().to_mapping()
    if mutation == "unknown":
        value["unknown"] = "field"
    elif mutation == "wrong-type":
        value["reviewed_head"] = 7
    else:
        value["allowed_path_roots"] = list(reversed(value["allowed_path_roots"]))

    with pytest.raises(receipts.ReceiptContractError, match="invalid_review_scope"):
        receipts.review_scope_from_mapping(value)


def test_hashes_use_canonical_mappings_and_lowercase_rendering() -> None:
    scope = _review_scope()
    attempt_mapping = {
        "schema_version": "opus-review-attempt-key/v1",
        "repository_identity": scope.repository_identity,
        "review_profile": scope.review_profile,
        "task_id": scope.task_id,
        "effective_base": scope.effective_base,
        "reviewed_head": scope.reviewed_head,
    }
    expected_attempt = hashlib.sha256(
        json.dumps(
            attempt_mapping,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    expected_scope = hashlib.sha256(
        receipts.canonical_json_bytes(scope.to_mapping())
    ).hexdigest()

    assert receipts.compute_attempt_key(scope) == f"opr1:{expected_attempt}"
    assert receipts.compute_scope_digest(scope) == f"sha256:{expected_scope}"
    assert receipts.compute_attempt_key(scope).removeprefix("opr1:").islower()
    assert receipts.compute_scope_digest(scope).removeprefix("sha256:").islower()


@pytest.mark.parametrize(
    "bad",
    [
        "",
        ".",
        "./x",
        "x/.",
        "x/../y",
        "/x",
        "x/",
        "x//y",
        "x\\y",
        "x*",
        "x?",
        "x[0]",
    ],
)
def test_normalize_repo_path_rejects_ambiguous_authority_paths(bad: str) -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_repo_path"):
        receipts.normalize_repo_path(bad)


def test_normalize_repo_path_preserves_case_and_unicode_spelling() -> None:
    nfc = "docs/caf\u00e9.md"
    nfd = "docs/cafe\u0301.md"
    assert receipts.normalize_repo_path("Docs/Case.md") == "Docs/Case.md"
    assert receipts.normalize_repo_path(nfc) == nfc
    assert receipts.normalize_repo_path(nfd) == nfd
    assert receipts.normalize_repo_path(nfc) != receipts.normalize_repo_path(nfd)


def test_coverage_is_byte_exact_component_aware_and_covers_deletes() -> None:
    changed = receipts.parse_name_status_z(
        b"M\0scripts/foo.py\0D\0tests/old.py\0"
    )
    receipts.assert_changed_path_coverage(changed, ("scripts/foo.py", "tests"))
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(
            changed, ("scripts/foo", "tests/old")
        )


def test_invalid_utf8_changed_path_fails_closed() -> None:
    with pytest.raises(
        receipts.ReceiptContractError, match="unsupported_git_path_encoding"
    ):
        receipts.parse_name_status_z(b"A\0bad-\xff.py\0")


def test_case_colliding_changed_paths_remain_distinct() -> None:
    changed = receipts.parse_name_status_z(
        b"A\0Scripts/example.py\0A\0scripts/example.py\0"
    )
    assert [item.path for item in changed] == [
        "Scripts/example.py",
        "scripts/example.py",
    ]
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(changed, ("scripts",))
    receipts.assert_changed_path_coverage(changed, ("Scripts", "scripts"))


def test_nfc_and_nfd_changed_paths_remain_byte_distinct() -> None:
    nfc = "docs/caf\u00e9.md"
    nfd = "docs/cafe\u0301.md"
    raw = b"A\0" + nfc.encode() + b"\0A\0" + nfd.encode() + b"\0"
    changed = receipts.parse_name_status_z(raw)
    assert changed[0].path_bytes != changed[1].path_bytes
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(changed, (nfc,))
    receipts.assert_changed_path_coverage(changed, (nfc, nfd))


def test_rename_is_delete_plus_add_and_both_paths_require_coverage() -> None:
    changed = receipts.parse_name_status_z(b"D\0old/name.py\0A\0new/name.py\0")
    assert [(item.status, item.path) for item in changed] == [
        ("D", "old/name.py"),
        ("A", "new/name.py"),
    ]
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(changed, ("new",))
    receipts.assert_changed_path_coverage(changed, ("old", "new"))


def test_copy_is_represented_as_an_addition() -> None:
    changed = receipts.parse_name_status_z(b"A\0copies/new.py\0")
    assert changed == (
        receipts.ChangedPath("A", "copies/new.py", b"copies/new.py"),
    )
    receipts.assert_changed_path_coverage(changed, ("copies",))


def test_empty_diff_parses_but_fails_coverage() -> None:
    assert receipts.parse_name_status_z(b"") == ()
    with pytest.raises(receipts.ReceiptContractError, match="empty_changed_paths"):
        receipts.assert_changed_path_coverage((), ("scripts",))


@pytest.mark.parametrize(
    "raw",
    [
        b"M\0scripts/x.py",
        b"M\0",
        b"\0scripts/x.py\0",
        b"M\0\0",
        b"MM\0scripts/x.py\0",
        b"R\0old.py\0new.py\0",
        b"C\0source.py\0copy.py\0",
        b"Z\0scripts/x.py\0",
    ],
)
def test_name_status_parser_rejects_malformed_or_unsupported_records(
    raw: bytes,
) -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_name_status"):
        receipts.parse_name_status_z(raw)


def test_coverage_rejects_directory_prefix_collisions() -> None:
    changed = receipts.parse_name_status_z(b"M\0scripts/foobar/item.py\0")
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(changed, ("scripts/foo",))
    receipts.assert_changed_path_coverage(changed, ("scripts/foobar",))


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _linked_worktrees(tmp_path: Path) -> tuple[Path, Path, Path]:
    primary = tmp_path / "primary"
    first = tmp_path / "first"
    second = tmp_path / "second"
    primary.mkdir()
    _git(primary, "init", "-q")
    _git(primary, "config", "user.email", "receipt-tests@example.invalid")
    _git(primary, "config", "user.name", "Receipt Tests")
    (primary / "tracked.txt").write_text("initial\n", encoding="utf-8")
    _git(primary, "add", "tracked.txt")
    _git(primary, "commit", "-qm", "test: initialize receipt repository")
    _git(primary, "worktree", "add", "-qb", "receipt-first", str(first))
    _git(primary, "worktree", "add", "-qb", "receipt-second", str(second))
    return primary, first, second


def _receipt_paths(state_root: Path) -> tuple[Path, Path]:
    receipt_files = tuple(state_root.glob("*.json"))
    lock_files = tuple(state_root.glob("*.lock"))
    assert len(receipt_files) == 1
    assert len(lock_files) == 1
    return receipt_files[0], lock_files[0]


def _reserve_once(
    tmp_path: Path,
    *,
    stat_fn: object | None = None,
) -> tuple[object, Path]:
    state_root = tmp_path / "state"
    kwargs: dict[str, object] = {"state_root": state_root}
    if stat_fn is not None:
        kwargs["stat_fn"] = stat_fn
    store = receipts.ReceiptStore.for_repo(tmp_path, **kwargs)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        decision = attempt.reserve_or_load(_review_scope())
    return decision, state_root


def _review_mapping(
    status: str = "pass", finding_ids: tuple[str, ...] = ()
) -> dict[str, object]:
    return {
        "schema_version": "opus-review/v3",
        "status": status,
        "findings": [{"id": finding_id} for finding_id in finding_ids],
    }


def _verify_request_scope(blob_id: str = DESCRIPTOR_BLOB) -> receipts.ReviewScope:
    event_path = "coordination/mailbox/sent/0042-director-to-operator-verification-request.md"
    return dataclasses.replace(
        _review_scope(),
        trigger_kind="verify-request",
        trigger_identity=f"verify-request:{TRIGGER}:{event_path}",
        trigger_path=event_path,
        trigger_blob_id=blob_id,
    )


def _default_root_reserve_worker(
    worktree: str,
    start: object,
    losing_attempted: object,
    results: object,
) -> None:
    store: receipts.ReceiptStore | None = None
    try:
        start.wait(10)
        store = receipts.ReceiptStore.for_repo(Path(worktree))
        try:
            with store.lock_attempt(_review_scope(), blocking=False) as attempt:
                decision = attempt.reserve_or_load(_review_scope())
                if decision.action == "launch" and not losing_attempted.wait(10):
                    raise AssertionError(
                        "launch owner released before a losing attempt completed"
                    )
                results.put(("ok", decision.action, str(store.state_root)))
        except receipts.ReceiptStateError as exc:
            if exc.reason == "attempt_in_progress":
                losing_attempted.set()
            results.put(("ok", exc.reason, str(store.state_root)))
    except BaseException as exc:
        results.put(
            (
                "error",
                type(exc).__name__,
                str(exc),
                traceback.format_exc(),
                None if store is None else str(store.state_root),
                None if store is None else store.state_root.exists(),
            )
        )


def _reconciliation_input(
    *,
    finding_ids: tuple[str, ...] = (),
    verdict: str = "GO",
    evidence_suffix: str = "",
) -> dict[str, object]:
    return {
        "receipt_id": receipts.compute_attempt_key(_review_scope()),
        "scope_digest": receipts.compute_scope_digest(_review_scope()),
        "codex_verdict": verdict,
        "expected_head": HEAD,
        "expected_base": BASE,
        "dispositions": {
            finding_id: {
                "disposition": "confirmed",
                "evidence": f"evidence-{finding_id}{evidence_suffix}",
            }
            for finding_id in finding_ids
        },
    }


def _reconciliation_result(verdict: str = "GO") -> dict[str, object]:
    return {
        "schema_version": "opus-reconciliation/v2",
        "codex_verdict": verdict,
        "go_allowed": verdict == "GO",
    }


def _reconcile_worker(
    state_root: str,
    input_mapping: dict[str, object],
    result_mapping: dict[str, object],
    start: object,
    results: object,
) -> None:
    try:
        store = receipts.ReceiptStore.for_repo(
            Path(state_root).parent, state_root=state_root
        )
        start.wait()
        with store.lock_attempt(_review_scope(), blocking=True) as attempt:
            attempt.reserve_or_load(_review_scope())
            record = attempt.record_reconciliation(input_mapping, result_mapping)
            results.put(("ok", record.reconciliation["input_digest"]))
    except receipts.ReceiptStateError as exc:
        results.put(("error", exc.reason))


def _run_reconciliation_race(
    state_root: Path,
    requests: tuple[tuple[dict[str, object], dict[str, object]], ...],
) -> list[tuple[str, str]]:
    context = multiprocessing.get_context("fork")
    start = context.Event()
    results = context.Queue()
    processes = [
        context.Process(
            target=_reconcile_worker,
            args=(str(state_root), input_mapping, result_mapping, start, results),
        )
        for input_mapping, result_mapping in requests
    ]
    try:
        for process in processes:
            process.start()
        start.set()
        outcomes = [results.get(timeout=10) for _ in processes]
        for process in processes:
            process.join(timeout=10)
        assert all(process.exitcode == 0 for process in processes)
        return outcomes
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)
        results.close()
        results.join_thread()


def test_receipt_id_lookup_loads_exact_record_and_allows_reconciliation(
    tmp_path: Path,
) -> None:
    scope = _review_scope()
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(scope, blocking=False) as attempt:
        attempt.reserve_or_load(scope)
        reviewed = attempt.record_review(_review_mapping())

    with store.lock_receipt(reviewed.receipt_id, blocking=False) as attempt:
        loaded = attempt.load_existing()
        reconciled = attempt.record_reconciliation(
            _reconciliation_input(), _reconciliation_result()
        )

    assert loaded == reviewed
    assert reconciled.state == "reconciled"
    assert reconciled.generation == reviewed.generation + 1


def test_receipt_id_load_requires_active_lock(tmp_path: Path) -> None:
    scope = _review_scope()
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(scope, blocking=False) as attempt:
        record = attempt.reserve_or_load(scope).record

    unlocked = store.lock_receipt(record.receipt_id, blocking=False)
    with pytest.raises(receipts.ReceiptStateError, match="attempt_lock_required"):
        unlocked.load_existing()


@pytest.mark.parametrize(
    "receipt_id",
    [
        "sha256:" + "a" * 64,
        "opr1:" + "a" * 63,
        "opr1:" + "a" * 65,
        "opr1:" + "A" * 64,
        "opr1:" + "g" * 64,
        "opr1:" + "a" * 31 + "/" + "b" * 32,
        "opr1:" + "a" * 31 + "\\" + "b" * 32,
        "opr1:../" + "a" * 61,
    ],
)
def test_lock_receipt_rejects_malformed_id_before_state_root_io(
    tmp_path: Path, receipt_id: str
) -> None:
    state_root = tmp_path / "must-not-open"
    store = receipts.ReceiptStore(state_root)

    with pytest.raises(receipts.ReceiptContractError, match="invalid_receipt_id"):
        store.lock_receipt(receipt_id, blocking=False)

    assert not state_root.exists()


def test_receipt_id_lookup_missing_record_never_creates_receipt(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)
    missing_id = "opr1:" + "f" * 64

    with store.lock_receipt(missing_id, blocking=False) as attempt:
        with pytest.raises(receipts.ReceiptStateError, match="receipt_missing"):
            attempt.load_existing()

    assert tuple(state_root.glob("*.json")) == ()
    assert not (state_root / ("f" * 64 + ".json")).exists()


def test_receipt_id_lookup_derives_exact_names_without_directory_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    decision, state_root = _reserve_once(tmp_path)
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)

    def reject_scan(*args: object, **kwargs: object) -> object:
        raise AssertionError("receipt lookup must not scan the state directory")

    monkeypatch.setattr(receipts.os, "scandir", reject_scan)
    with store.lock_receipt(decision.record.receipt_id, blocking=False) as attempt:
        assert attempt.load_existing() == decision.record


@pytest.mark.parametrize(
    "replacement",
    ["corrupt", "mode", "symlink", "directory", "fifo", "hardlink"],
)
def test_receipt_id_lookup_reuses_receipt_file_security_checks(
    tmp_path: Path, replacement: str
) -> None:
    decision, state_root = _reserve_once(tmp_path)
    receipt_path, _ = _receipt_paths(state_root)
    original = receipt_path.with_suffix(".original")
    if replacement == "corrupt":
        receipt_path.write_bytes(b'{"schema_version":')
        receipt_path.chmod(0o600)
    elif replacement == "mode":
        receipt_path.chmod(0o755)
    else:
        receipt_path.rename(original)
        if replacement == "symlink":
            receipt_path.symlink_to(original.name)
        elif replacement == "directory":
            receipt_path.mkdir()
        elif replacement == "hardlink":
            os.link(original, receipt_path)
        else:
            os.mkfifo(receipt_path, mode=0o600)

    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)
    with pytest.raises(receipts.ReceiptStateError):
        with store.lock_receipt(
            decision.record.receipt_id, blocking=False
        ) as attempt:
            attempt.load_existing()


def test_receipt_id_lookup_reuses_owner_check(tmp_path: Path) -> None:
    decision, state_root = _reserve_once(tmp_path)

    def wrong_owner(fd: int) -> os.stat_result:
        observed = list(os.fstat(fd))
        observed[4] = os.getuid() + 1
        return os.stat_result(observed)

    store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=state_root, stat_fn=wrong_owner
    )
    with pytest.raises(receipts.ReceiptStateError, match="receipt_file_owner"):
        with store.lock_receipt(decision.record.receipt_id, blocking=False):
            pass


def test_scope_and_receipt_id_access_contend_on_same_lock(tmp_path: Path) -> None:
    scope = _review_scope()
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")

    with store.lock_attempt(scope, blocking=False) as scope_attempt:
        record = scope_attempt.reserve_or_load(scope).record
        with pytest.raises(receipts.ReceiptStateError, match="attempt_in_progress"):
            with store.lock_receipt(record.receipt_id, blocking=False):
                pass


def test_attempt_lock_retries_one_concurrent_create_enoent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / "state"
    )
    original_open = os.open
    matching_lock_opens = 0

    def injected_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal matching_lock_opens
        if (
            isinstance(path, str)
            and path.endswith(".lock")
            and flags & os.O_CREAT
        ):
            matching_lock_opens += 1
            if matching_lock_opens == 1:
                raise FileNotFoundError(
                    errno.ENOENT,
                    "injected concurrent O_CREAT|O_NOFOLLOW race",
                    path,
                )
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(receipts.os, "open", injected_open)

    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        decision = attempt.reserve_or_load(_review_scope())

    assert decision.action == "launch"
    assert matching_lock_opens == 2


def test_linked_worktrees_race_default_root_and_one_scope_reservation(
    tmp_path: Path,
) -> None:
    primary, first, second = _linked_worktrees(tmp_path)
    expected = primary / ".codex/runtime/opus-review-receipts/v1"
    first_local = first / ".codex/runtime/opus-review-receipts/v1"
    second_local = second / ".codex/runtime/opus-review-receipts/v1"
    assert not expected.exists()
    context = multiprocessing.get_context("fork")
    start = context.Barrier(2)
    losing_attempted = context.Event()
    results = context.Queue()
    processes = [
        context.Process(
            target=_default_root_reserve_worker,
            args=(str(worktree), start, losing_attempted, results),
        )
        for worktree in (first, second)
    ]
    try:
        for process in processes:
            process.start()
        outcomes = [results.get(timeout=15) for _ in processes]
        for process in processes:
            process.join(timeout=15)
        assert all(process.exitcode == 0 for process in processes)
    finally:
        losing_attempted.set()
        for process in processes:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)
        results.close()
        results.join_thread()

    errors = [outcome for outcome in outcomes if outcome[0] != "ok"]
    assert not errors, "\n".join(
        f"state_root={outcome[4]!r} exists={outcome[5]!r}\n{outcome[3]}"
        for outcome in errors
    )
    assert {outcome[1] for outcome in outcomes} == {
        "launch",
        "attempt_in_progress",
    }
    assert {Path(outcome[2]) for outcome in outcomes} == {expected}
    assert stat.S_IMODE(expected.stat().st_mode) == 0o700
    assert not first_local.exists()
    assert not second_local.exists()


@pytest.mark.parametrize("selector", ("GIT_DIR", "GIT_COMMON_DIR"))
def test_receipt_store_ignores_ambient_repository_root_selector(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selector: str,
) -> None:
    target = tmp_path / "target"
    foreign = tmp_path / "foreign"
    target.mkdir()
    foreign.mkdir()
    _git(target, "init", "-q")
    _git(foreign, "init", "-q")
    monkeypatch.setenv(selector, str(foreign / ".git"))

    store = receipts.ReceiptStore.for_repo(target)

    expected = target / ".codex/runtime/opus-review-receipts/v1"
    foreign_runtime = foreign / ".codex/runtime/opus-review-receipts/v1"
    assert store.state_root == expected
    assert expected.is_dir()
    assert not foreign_runtime.exists()


def test_receipt_store_git_launcher_strips_every_git_environment_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    real_run = subprocess.run
    launches: list[tuple[list[str], dict[str, object]]] = []

    def launch_spy(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[object]:
        launches.append((argv, kwargs))
        return real_run(argv, **kwargs)

    monkeypatch.setenv("GIT_FUTURE_RECEIPT_SELECTOR", "attacker-controlled")
    monkeypatch.setattr(receipts.subprocess, "run", launch_spy)

    store = receipts.ReceiptStore.for_repo(repo)

    assert store.state_root == repo / ".codex/runtime/opus-review-receipts/v1"
    assert len(launches) == 1
    argv, kwargs = launches[0]
    assert argv[:3] == [
        "/usr/bin/git",
        "--no-replace-objects",
        "--literal-pathspecs",
    ]
    assert Path(kwargs["cwd"]) == repo
    environment = kwargs["env"]
    assert isinstance(environment, dict)
    assert set(environment) == {
        "PATH",
        "LANG",
        "LC_ALL",
        "HOME",
        "XDG_CONFIG_HOME",
    }
    assert environment["PATH"] == "/usr/bin:/bin"
    assert environment["LANG"] == environment["LC_ALL"] == "C"
    assert not any(key.startswith("GIT_") for key in environment)


def test_initial_reservation_is_durable_and_private(tmp_path: Path) -> None:
    decision, state_root = _reserve_once(tmp_path)
    receipt_path, lock_path = _receipt_paths(state_root)

    assert decision.action == "launch"
    assert decision.record.state == "reserved"
    assert decision.record.generation == 1
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600


def test_receipt_store_rejects_wrong_owner_from_injected_stat_boundary(
    tmp_path: Path,
) -> None:
    _reserve_once(tmp_path)

    def wrong_owner(fd: int) -> os.stat_result:
        observed = list(os.fstat(fd))
        observed[4] = os.getuid() + 1
        return os.stat_result(observed)

    store = receipts.ReceiptStore.for_repo(
        tmp_path,
        state_root=tmp_path / "state",
        stat_fn=wrong_owner,
    )
    with pytest.raises(receipts.ReceiptStateError, match="receipt_file_owner"):
        with store.lock_attempt(_review_scope(), blocking=False) as attempt:
            attempt.reserve_or_load(_review_scope())


@pytest.mark.parametrize(
    "replacement",
    ["mode", "symlink", "directory", "fifo", "hardlink"],
)
def test_receipt_store_rejects_unsafe_receipt_file_metadata(
    tmp_path: Path, replacement: str
) -> None:
    _reserve_once(tmp_path)
    receipt_path, _ = _receipt_paths(tmp_path / "state")
    original = receipt_path.with_suffix(".original")
    if replacement == "mode":
        receipt_path.chmod(0o755)
    else:
        receipt_path.rename(original)
        if replacement == "symlink":
            receipt_path.symlink_to(original.name)
        elif replacement == "directory":
            receipt_path.mkdir()
        elif replacement == "hardlink":
            os.link(original, receipt_path)
        else:
            os.mkfifo(receipt_path, mode=0o600)

    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with pytest.raises(receipts.ReceiptStateError):
        with store.lock_attempt(_review_scope(), blocking=False) as attempt:
            attempt.reserve_or_load(_review_scope())


@pytest.mark.parametrize(
    "corruption",
    ["truncated", "duplicate", "attempt_key", "scope_digest", "generation"],
)
def test_receipt_store_rejects_corrupt_or_rolled_back_receipts(
    tmp_path: Path, corruption: str
) -> None:
    _reserve_once(tmp_path)
    receipt_path, _ = _receipt_paths(tmp_path / "state")
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    if corruption == "truncated":
        raw = b'{"schema_version":'
    elif corruption == "duplicate":
        raw = b'{"attempt_key":"first","attempt_key":"second"}'
    else:
        if corruption == "attempt_key":
            payload["attempt_key"] = "opr1:" + "f" * 64
        elif corruption == "scope_digest":
            payload["scope_digest"] = "sha256:" + "f" * 64
        else:
            payload["generation"] = 0
        raw = receipts.canonical_json_bytes(payload)
    receipt_path.write_bytes(raw)
    receipt_path.chmod(0o600)

    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with pytest.raises(receipts.ReceiptStateError):
        with store.lock_attempt(_review_scope(), blocking=False) as attempt:
            attempt.reserve_or_load(_review_scope())


def test_reviewed_reservation_returns_and_abandoned_reservation_degrades(
    tmp_path: Path,
) -> None:
    reviewed_root = tmp_path / "reviewed"
    reviewed_store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=reviewed_root
    )
    with reviewed_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        first = attempt.reserve_or_load(_review_scope())
        reviewed = attempt.record_review(_review_mapping())

    with reviewed_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        identical = attempt.reserve_or_load(_review_scope())

    abandoned_root = tmp_path / "abandoned"
    abandoned_store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=abandoned_root
    )
    with abandoned_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        abandoned_first = attempt.reserve_or_load(_review_scope())
    with abandoned_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        abandoned = attempt.reserve_or_load(_review_scope())

    assert first.action == "launch"
    assert reviewed.state == "reviewed"
    assert reviewed.generation == 2
    assert identical.action == "return"
    assert abandoned_first.action == "launch"
    assert abandoned.action == "degrade_uncertain"


def test_reordered_duplicate_scope_collections_are_idempotent(tmp_path: Path) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    original = _review_scope(commands=(CMD_B, CMD_A), allowed=("scripts", "tests/unit"))
    reordered = _review_scope(
        commands=(CMD_A, CMD_B, CMD_A),
        allowed=("tests/unit", "scripts", "scripts"),
    )
    with store.lock_attempt(original, blocking=False) as attempt:
        attempt.reserve_or_load(original)
        attempt.record_review(_review_mapping())
    with store.lock_attempt(reordered, blocking=False) as attempt:
        repeated = attempt.reserve_or_load(reordered)
    assert repeated.action == "return"


@pytest.mark.parametrize(
    "changed_field",
    [
        "requirement_digest",
        "authorization",
        "command_tokenization",
        "trigger_blob",
        "descriptor_digest",
        "allowed_roots",
    ],
)
def test_same_attempt_key_rejects_any_changed_scope_input(
    tmp_path: Path, changed_field: str
) -> None:
    original = _verify_request_scope() if changed_field == "trigger_blob" else _review_scope()
    if changed_field == "requirement_digest":
        changed = dataclasses.replace(
            original,
            requirements=(
                {
                    "path": "AGENTS.md",
                    "blob_id": REQUIREMENT_BLOB,
                    "digest": "sha256:" + "4" * 64,
                },
            ),
        )
    elif changed_field == "authorization":
        changed = dataclasses.replace(
            original, authorization_identity="user-task:changed"
        )
    elif changed_field == "command_tokenization":
        changed = dataclasses.replace(
            original,
            verification_commands=(CMD_A.replace("env -u", "env  -u"), CMD_B),
        )
    elif changed_field == "trigger_blob":
        changed = dataclasses.replace(original, trigger_blob_id="f" * 40)
    elif changed_field == "descriptor_digest":
        changed = dataclasses.replace(
            original, descriptor_digest="sha256:" + "5" * 64
        )
    else:
        changed = dataclasses.replace(original, allowed_path_roots=("scripts",))

    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(original, blocking=False) as attempt:
        attempt.reserve_or_load(original)
        attempt.record_review(_review_mapping())
    with store.lock_attempt(changed, blocking=False) as attempt:
        with pytest.raises(receipts.ReceiptStateError, match="attempt_scope_conflict"):
            attempt.reserve_or_load(changed)


def test_distinct_authoritative_task_id_creates_distinct_receipt(
    tmp_path: Path,
) -> None:
    second_scope = dataclasses.replace(
        _review_scope(),
        task_id="11111111-1111-4111-8111-111111111111",
        question_id="second-lawful-question",
    )
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        first = attempt.reserve_or_load(_review_scope())
    with store.lock_attempt(second_scope, blocking=False) as attempt:
        second = attempt.reserve_or_load(second_scope)
    assert first.action == second.action == "launch"
    assert first.record.receipt_id != second.record.receipt_id
    assert len(tuple((tmp_path / "state").glob("*.json"))) == 2


def test_pre_reservation_failure_leaves_no_receipt(tmp_path: Path) -> None:
    invalid = dataclasses.replace(
        _review_scope(), authorization_identity="contains whitespace"
    )
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(invalid, blocking=False) as attempt:
        with pytest.raises(receipts.ReceiptContractError, match="invalid_review_scope"):
            attempt.reserve_or_load(invalid)
    assert tuple((tmp_path / "state").glob("*.json")) == ()


def test_atomic_review_replacement_failure_preserves_reservation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())

        def fail_replace(*args: object, **kwargs: object) -> None:
            raise OSError("injected replacement failure")

        monkeypatch.setattr(receipts.os, "replace", fail_replace)
        with pytest.raises(receipts.ReceiptStateError, match="receipt_replace_failed"):
            attempt.record_review(_review_mapping())

    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        recovered = attempt.reserve_or_load(_review_scope())
    assert recovered.action == "degrade_uncertain"
    assert tuple((tmp_path / "state").glob("*.tmp-*")) == ()


def test_reconciliation_is_canonical_idempotent_and_bound_to_result(
    tmp_path: Path,
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    input_mapping = _reconciliation_input()
    result_mapping = _reconciliation_result()
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping())
        first = attempt.record_reconciliation(input_mapping, result_mapping)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        reservation = attempt.reserve_or_load(_review_scope())
        identical = attempt.record_reconciliation(
            dict(reversed(tuple(input_mapping.items()))),
            dict(reversed(tuple(result_mapping.items()))),
        )
        with pytest.raises(
            receipts.ReceiptStateError, match="reconciliation_replay_conflict"
        ):
            attempt.record_reconciliation(
                {**input_mapping, "codex_verdict": "NITS"},
                result_mapping,
            )

    expected_digest = "sha256:" + hashlib.sha256(
        receipts.canonical_json_bytes(input_mapping)
    ).hexdigest()
    assert first.state == "reconciled"
    assert first.generation == 3
    assert first.reconciliation == {
        "input": input_mapping,
        "input_digest": expected_digest,
        "result": result_mapping,
    }
    assert reservation.action == "return"
    assert identical == first


@pytest.mark.parametrize("status", ["pass", "unavailable"])
def test_pass_and_unavailable_reconciliation_reject_dispositions(
    tmp_path: Path, status: str
) -> None:
    store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / status
    )
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping(status))
        with pytest.raises(receipts.ReceiptStateError, match="unexpected_dispositions"):
            attempt.record_reconciliation(
                _reconciliation_input(finding_ids=("OPUS-1",)),
                _reconciliation_result(),
            )


@pytest.mark.parametrize(
    "actual_ids", [("OPUS-1",), ("OPUS-1", "OPUS-2", "OPUS-3")]
)
def test_issue_reconciliation_requires_exact_finding_id_set(
    tmp_path: Path, actual_ids: tuple[str, ...]
) -> None:
    store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / "-".join(actual_ids)
    )
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping("issues", ("OPUS-1", "OPUS-2")))
        with pytest.raises(
            receipts.ReceiptStateError, match="finding_disposition_mismatch"
        ):
            attempt.record_reconciliation(
                _reconciliation_input(finding_ids=actual_ids),
                _reconciliation_result(),
            )


def test_issue_reconciliation_accepts_exact_finding_id_set(tmp_path: Path) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping("issues", ("OPUS-2", "OPUS-1")))
        reconciled = attempt.record_reconciliation(
            _reconciliation_input(finding_ids=("OPUS-1", "OPUS-2")),
            _reconciliation_result(),
        )
    assert reconciled.state == "reconciled"


def test_reconciliation_detects_generation_change_under_lock(tmp_path: Path) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping())
        receipt_path, _ = _receipt_paths(tmp_path / "state")
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["generation"] = 4
        receipt_path.write_bytes(receipts.canonical_json_bytes(payload))
        with pytest.raises(
            receipts.ReceiptStateError, match="receipt_generation_conflict"
        ):
            attempt.record_reconciliation(
                _reconciliation_input(), _reconciliation_result()
            )


def test_simultaneous_identical_reconciliation_converges(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping())
    request = (_reconciliation_input(), _reconciliation_result())
    outcomes = _run_reconciliation_race(state_root, (request, request))
    assert [status for status, _ in outcomes] == ["ok", "ok"]
    assert outcomes[0][1] == outcomes[1][1]


def test_simultaneous_conflicting_reconciliation_has_one_winner(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping())
    outcomes = _run_reconciliation_race(
        state_root,
        (
            (_reconciliation_input(), _reconciliation_result()),
            (
                _reconciliation_input(verdict="NITS"),
                _reconciliation_result("NITS"),
            ),
        ),
    )
    assert sorted(status for status, _ in outcomes) == ["error", "ok"]
    assert ("error", "reconciliation_replay_conflict") in outcomes


def _prepare_reconciled(store: object) -> None:
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.record_review(_review_mapping())
        attempt.record_reconciliation(
            _reconciliation_input(), _reconciliation_result()
        )


def _real_publication_witness(
    tmp_path: Path, *, name: str = ".candidate.tmp", raw: bytes = b"report\n"
) -> tuple[str, str, str, int, int, Path]:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    candidate = sent / name
    candidate.write_bytes(raw)
    candidate.chmod(0o600)
    observed = candidate.stat()
    path = (
        "coordination/mailbox/sent/"
        "2026-07-13T05-00-00Z-operator-to-all-verification-report.md"
    )
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    return path, digest, name, observed.st_dev, observed.st_ino, candidate


_INDEX_BLOB_OID = "a" * 40
_INDEX_MODE = "100644"
_INDEX_STAGE = 0
_LIFECYCLE_PUBLICATION_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-13T05-00-00Z-operator-to-all-verification-report.md"
)
_LIFECYCLE_PUBLICATION_DIGEST = "sha256:" + "b" * 64
_LIFECYCLE_PUBLICATION_NAME = ".candidate"
_LIFECYCLE_PUBLICATION_DEVICE = 17
_LIFECYCLE_PUBLICATION_INODE = 23
_LIFECYCLE_STATES = (
    "reserved",
    "reviewed",
    "reconciled",
    "publishing",
    "published",
)
_LIFECYCLE_OPERATIONS = (
    "record_review",
    "record_reconciliation",
    "begin_publication",
    "finish_publication",
    "cancel_publication",
    "recover_publication",
)
_LIFECYCLE_ORACLE = {
    ("reserved", "record_review"): "to:reviewed",
    ("reserved", "record_reconciliation"): "invalid",
    ("reserved", "begin_publication"): "invalid",
    ("reserved", "finish_publication"): "invalid",
    ("reserved", "cancel_publication"): "invalid",
    ("reserved", "recover_publication"): "invalid",
    ("reviewed", "record_review"): "invalid",
    ("reviewed", "record_reconciliation"): "to:reconciled",
    ("reviewed", "begin_publication"): "invalid",
    ("reviewed", "finish_publication"): "invalid",
    ("reviewed", "cancel_publication"): "invalid",
    ("reviewed", "recover_publication"): "invalid",
    ("reconciled", "record_review"): "invalid",
    ("reconciled", "record_reconciliation"): "replay",
    ("reconciled", "begin_publication"): "to:publishing",
    ("reconciled", "finish_publication"): "invalid",
    ("reconciled", "cancel_publication"): "invalid",
    ("reconciled", "recover_publication"): "invalid",
    ("publishing", "record_review"): "invalid",
    ("publishing", "record_reconciliation"): "replay",
    ("publishing", "begin_publication"): "replay",
    ("publishing", "finish_publication"): "to:published",
    ("publishing", "cancel_publication"): "to:reconciled",
    ("publishing", "recover_publication"): "finalize",
    ("published", "record_review"): "invalid",
    ("published", "record_reconciliation"): "replay",
    ("published", "begin_publication"): "replay",
    ("published", "finish_publication"): "replay",
    ("published", "cancel_publication"): "invalid",
    ("published", "recover_publication"): "invalid",
}
_CHANGED_VALID_REPLAY_CASES = (
    ("reconciled", "record_reconciliation", "reconciliation_replay_conflict"),
    ("publishing", "record_reconciliation", "reconciliation_replay_conflict"),
    ("published", "record_reconciliation", "reconciliation_replay_conflict"),
    ("publishing", "begin_publication", "publication_replay_conflict"),
    ("published", "begin_publication", "publication_replay_conflict"),
    ("publishing", "finish_publication", "publication_replay_conflict"),
    ("published", "finish_publication", "publication_replay_conflict"),
    ("publishing", "cancel_publication", "publication_replay_conflict"),
    ("publishing", "recover_publication", "publication_replay_conflict"),
)


def _lifecycle_review() -> dict[str, object]:
    return _review_mapping("issues", ("OPUS-1",))


def _lifecycle_reconciliation_input(
    *, changed: bool = False
) -> dict[str, object]:
    return _reconciliation_input(
        finding_ids=("OPUS-1",),
        verdict="NITS",
        evidence_suffix="-changed" if changed else "",
    )


def _lifecycle_reconciliation_result() -> dict[str, object]:
    return _reconciliation_result("NITS")


def _lifecycle_publication_arguments(
    *, changed: bool = False
) -> tuple[str, str, str, int, int, str, str, int]:
    return (
        _LIFECYCLE_PUBLICATION_PATH,
        (
            "sha256:" + "c" * 64
            if changed
            else _LIFECYCLE_PUBLICATION_DIGEST
        ),
        _LIFECYCLE_PUBLICATION_NAME,
        _LIFECYCLE_PUBLICATION_DEVICE,
        _LIFECYCLE_PUBLICATION_INODE,
        _INDEX_BLOB_OID,
        _INDEX_MODE,
        _INDEX_STAGE,
    )


def _advance_attempt_to_lifecycle_state(
    attempt: receipts.LockedAttempt,
    state: str,
) -> receipts.ReceiptRecord:
    current = attempt.reserve_or_load(_review_scope()).record
    if state == "reserved":
        return current
    current = attempt.record_review(_lifecycle_review())
    if state == "reviewed":
        return current
    current = attempt.record_reconciliation(
        _lifecycle_reconciliation_input(),
        _lifecycle_reconciliation_result(),
    )
    if state == "reconciled":
        return current
    current = attempt.begin_publication(*_lifecycle_publication_arguments())
    if state == "publishing":
        return current
    current = attempt.finish_publication(*_lifecycle_publication_arguments())
    assert state == "published"
    return current


def _invoke_lifecycle_operation(
    attempt: receipts.LockedAttempt,
    operation: str,
    *,
    generation: int,
    changed: bool = False,
) -> receipts.ReceiptRecord | str:
    if operation == "record_review":
        return attempt.record_review(_lifecycle_review())
    if operation == "record_reconciliation":
        return attempt.record_reconciliation(
            _lifecycle_reconciliation_input(changed=changed),
            _lifecycle_reconciliation_result(),
        )
    if operation == "begin_publication":
        return attempt.begin_publication(
            *_lifecycle_publication_arguments(changed=changed)
        )
    if operation == "finish_publication":
        return attempt.finish_publication(
            *_lifecycle_publication_arguments(changed=changed)
        )
    if operation == "cancel_publication":
        return attempt.cancel_publication(
            *_lifecycle_publication_arguments(changed=changed),
            generation,
        )
    if operation == "recover_publication":
        return attempt.recover_publication(
            _LIFECYCLE_PUBLICATION_PATH,
            (
                "sha256:" + "c" * 64
                if changed
                else _LIFECYCLE_PUBLICATION_DIGEST
            ),
            _LIFECYCLE_PUBLICATION_DEVICE,
            _LIFECYCLE_PUBLICATION_INODE,
        )
    raise AssertionError(f"unknown lifecycle operation {operation!r}")


def test_publication_transitions_retain_full_creation_witness(
    tmp_path: Path,
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    _prepare_reconciled(store)
    path, digest, name, device, inode, candidate = _real_publication_witness(tmp_path)
    final = tmp_path / path
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        publishing = attempt.begin_publication(
            path,
            digest,
            name,
            device,
            inode,
            _INDEX_BLOB_OID,
            _INDEX_MODE,
            _INDEX_STAGE,
        )
        repeated_begin = attempt.begin_publication(
            path,
            digest,
            name,
            device,
            inode,
            _INDEX_BLOB_OID,
            _INDEX_MODE,
            _INDEX_STAGE,
        )
        with pytest.raises(
            receipts.ReceiptStateError, match="publication_replay_conflict"
        ):
            attempt.begin_publication(
                path.replace("05-00-00Z", "05-00-01Z"),
                digest,
                name,
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
            )
        os.link(candidate, final)
        final_stat = final.stat()
        assert (final_stat.st_dev, final_stat.st_ino) == (device, inode)
        published = attempt.finish_publication(
            path,
            digest,
            name,
            device,
            inode,
            _INDEX_BLOB_OID,
            _INDEX_MODE,
            _INDEX_STAGE,
        )
        repeated_finish = attempt.finish_publication(
            path,
            digest,
            name,
            device,
            inode,
            _INDEX_BLOB_OID,
            _INDEX_MODE,
            _INDEX_STAGE,
        )
        with pytest.raises(
            receipts.ReceiptStateError, match="publication_replay_conflict"
        ):
            attempt.finish_publication(
                path,
                "sha256:" + "7" * 64,
                name,
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
            )
    assert publishing.state == "publishing"
    assert publishing.generation == 4
    assert publishing.publication == {
        "path": path,
        "candidate_digest": digest,
        "candidate_name": name,
        "candidate_device": device,
        "candidate_inode": inode,
        "index_blob_oid": _INDEX_BLOB_OID,
        "index_mode": _INDEX_MODE,
        "index_stage": _INDEX_STAGE,
    }
    assert repeated_begin == publishing
    assert published.state == "published"
    assert published.generation == 5
    assert repeated_finish == published


def test_publication_recovery_handles_absent_exact_and_mismatch(
    tmp_path: Path,
) -> None:
    path, digest, name, device, inode, candidate = _real_publication_witness(tmp_path)

    absent_store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / "absent"
    )
    _prepare_reconciled(absent_store)
    with absent_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
        assert attempt.recover_publication(path, None, None, None) == "clear"
        restarted = attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
    assert restarted.state == "publishing"
    assert restarted.generation == 6

    exact_store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / "exact"
    )
    _prepare_reconciled(exact_store)
    with exact_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
        final = tmp_path / path
        os.link(candidate, final)
        final_stat = final.stat()
        assert attempt.recover_publication(
            path, digest, final_stat.st_dev, final_stat.st_ino
        ) == "finalize"
        finalized = attempt.finish_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
    assert finalized.state == "published"
    final.unlink()

    mismatch_store = receipts.ReceiptStore.for_repo(
        tmp_path, state_root=tmp_path / "mismatch"
    )
    _prepare_reconciled(mismatch_store)
    with mismatch_store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
        with pytest.raises(
            receipts.ReceiptStateError, match="publication_replay_conflict"
        ):
            attempt.recover_publication(
                path, "sha256:" + "a" * 64, device, inode
            )


def test_publication_cancel_requires_exact_tuple_and_generation(tmp_path: Path) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    _prepare_reconciled(store)
    path, digest, name, device, inode, _ = _real_publication_witness(tmp_path)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        publishing = attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
        for changed in (
            (
                path.replace("05-00-00Z", "05-00-01Z"),
                digest,
                name,
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation,
            ),
            (
                path,
                digest,
                name + ".other",
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation,
            ),
            (
                path,
                digest,
                name,
                device + 1,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation,
            ),
            (
                path,
                digest,
                name,
                device,
                inode + 1,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation,
            ),
            (
                path,
                digest,
                name,
                device,
                inode,
                "b" * 40,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation,
            ),
            (
                path,
                digest,
                name,
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
                publishing.generation + 1,
            ),
        ):
            with pytest.raises(
                receipts.ReceiptStateError, match="publication_replay_conflict"
            ):
                attempt.cancel_publication(*changed)
        cancelled = attempt.cancel_publication(
            path,
            digest,
            name,
            device,
            inode,
            _INDEX_BLOB_OID,
            _INDEX_MODE,
            _INDEX_STAGE,
            publishing.generation,
        )
    assert cancelled.state == "reconciled"
    assert cancelled.generation == 5
    assert cancelled.publication is None


@pytest.mark.parametrize(
    "candidate_name",
    ["bad\\name", "bad*name", "bad?name", "bad[name", "bad\nname", "x" * 256],
)
def test_publication_witness_rejects_noncanonical_candidate_basename(
    tmp_path: Path, candidate_name: str
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    _prepare_reconciled(store)
    path, digest, _, device, inode, _ = _real_publication_witness(tmp_path)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        with pytest.raises(receipts.ReceiptStateError, match="invalid_publication"):
            attempt.begin_publication(
                path,
                digest,
                candidate_name,
                device,
                inode,
                _INDEX_BLOB_OID,
                _INDEX_MODE,
                _INDEX_STAGE,
            )


@pytest.mark.parametrize(
    "corruption",
    [
        "unknown-key",
        "missing-key",
        "bool-device",
        "negative-device",
        "bool-inode",
        "zero-inode",
        "nested-name",
        "bad-index-oid",
        "bad-index-mode",
        "bool-index-stage",
        "nonzero-index-stage",
        "odd-publishing-generation",
    ],
)
def test_receipt_rejects_malformed_publication_witness_and_parity(
    tmp_path: Path, corruption: str
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    _prepare_reconciled(store)
    path, digest, name, device, inode, _ = _real_publication_witness(tmp_path)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        attempt.begin_publication(
            path, digest, name, device, inode, _INDEX_BLOB_OID, _INDEX_MODE, _INDEX_STAGE
        )
    receipt_file, _ = _receipt_paths(store.state_root)
    value = json.loads(receipt_file.read_text(encoding="utf-8"))
    publication = value["publication"]
    assert isinstance(publication, dict)
    if corruption == "unknown-key":
        publication["extra"] = "x"
    elif corruption == "missing-key":
        publication.pop("candidate_inode")
    elif corruption == "bool-device":
        publication["candidate_device"] = True
    elif corruption == "negative-device":
        publication["candidate_device"] = -1
    elif corruption == "bool-inode":
        publication["candidate_inode"] = False
    elif corruption == "zero-inode":
        publication["candidate_inode"] = 0
    elif corruption == "nested-name":
        publication["candidate_name"] = "nested/candidate"
    elif corruption == "bad-index-oid":
        publication["index_blob_oid"] = "A" * 40
    elif corruption == "bad-index-mode":
        publication["index_mode"] = "100755"
    elif corruption == "bool-index-stage":
        publication["index_stage"] = False
    elif corruption == "nonzero-index-stage":
        publication["index_stage"] = 1
    else:
        value["generation"] = 5
    receipt_file.write_bytes(receipts.canonical_json_bytes(value))

    with store.lock_receipt(receipts.compute_attempt_key(_review_scope())) as attempt:
        with pytest.raises(receipts.ReceiptStateError):
            attempt.load_existing()


def test_locked_attempt_lifecycle_matches_independent_thirty_cell_oracle(
    tmp_path: Path,
) -> None:
    expected_case_keys = {
        (state, operation)
        for state in _LIFECYCLE_STATES
        for operation in _LIFECYCLE_OPERATIONS
    }
    assert len(expected_case_keys) == 30
    assert set(_LIFECYCLE_ORACLE) == expected_case_keys

    for state, operation in sorted(expected_case_keys):
        state_root = tmp_path / f"{state}-{operation}"
        store = receipts.ReceiptStore.for_repo(
            tmp_path, state_root=state_root
        )
        with store.lock_attempt(_review_scope(), blocking=False) as attempt:
            before = _advance_attempt_to_lifecycle_state(attempt, state)
            receipt_path, _ = _receipt_paths(state_root)
            before_bytes = receipt_path.read_bytes()
            before_inode = receipt_path.stat().st_ino
            expectation = _LIFECYCLE_ORACLE[(state, operation)]

            if expectation == "invalid":
                with pytest.raises(receipts.ReceiptStateError) as excinfo:
                    _invoke_lifecycle_operation(
                        attempt,
                        operation,
                        generation=before.generation,
                    )
                assert excinfo.value.reason == "invalid_receipt_transition"
                expected_state = state
                expected_generation = before.generation
            else:
                result = _invoke_lifecycle_operation(
                    attempt,
                    operation,
                    generation=before.generation,
                )
                if expectation == "replay":
                    assert result == before
                    expected_state = state
                    expected_generation = before.generation
                elif expectation == "finalize":
                    assert result == "finalize"
                    expected_state = state
                    expected_generation = before.generation
                else:
                    assert expectation.startswith("to:")
                    expected_state = expectation.removeprefix("to:")
                    expected_generation = before.generation + 1
                    assert isinstance(result, receipts.ReceiptRecord)
                    assert result.state == expected_state
                    assert result.generation == expected_generation

            if expectation in {"invalid", "replay", "finalize"}:
                assert receipt_path.read_bytes() == before_bytes
                assert receipt_path.stat().st_ino == before_inode

        with store.lock_attempt(_review_scope(), blocking=False) as attempt:
            persisted = attempt.load_existing()
        assert persisted.state == expected_state
        assert persisted.generation == expected_generation


@pytest.mark.parametrize(
    ("state", "operation", "reason"),
    _CHANGED_VALID_REPLAY_CASES,
)
def test_changed_valid_lifecycle_replays_raise_exact_conflict(
    tmp_path: Path,
    state: str,
    operation: str,
    reason: str,
) -> None:
    assert set(_CHANGED_VALID_REPLAY_CASES) == {
        (
            "reconciled",
            "record_reconciliation",
            "reconciliation_replay_conflict",
        ),
        (
            "publishing",
            "record_reconciliation",
            "reconciliation_replay_conflict",
        ),
        (
            "published",
            "record_reconciliation",
            "reconciliation_replay_conflict",
        ),
        ("publishing", "begin_publication", "publication_replay_conflict"),
        ("published", "begin_publication", "publication_replay_conflict"),
        ("publishing", "finish_publication", "publication_replay_conflict"),
        ("published", "finish_publication", "publication_replay_conflict"),
        ("publishing", "cancel_publication", "publication_replay_conflict"),
        ("publishing", "recover_publication", "publication_replay_conflict"),
    }
    state_root = tmp_path / f"{state}-{operation}"
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=state_root)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        before = _advance_attempt_to_lifecycle_state(attempt, state)
        receipt_path, _ = _receipt_paths(state_root)
        before_bytes = receipt_path.read_bytes()
        before_inode = receipt_path.stat().st_ino
        with pytest.raises(receipts.ReceiptStateError) as excinfo:
            _invoke_lifecycle_operation(
                attempt,
                operation,
                generation=before.generation,
                changed=True,
            )
        assert excinfo.value.reason == reason
        assert receipt_path.read_bytes() == before_bytes
        assert receipt_path.stat().st_ino == before_inode


def test_receipt_store_accepts_normalized_review_larger_than_descriptor_limit(
    tmp_path: Path,
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    review = {**_review_mapping(), "bounded_detail": "x" * 70_000}
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        attempt.reserve_or_load(_review_scope())
        stored = attempt.record_review(review)
    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        repeated = attempt.reserve_or_load(_review_scope())
    assert stored.review == review
    assert repeated.action == "return"
    assert repeated.record.review == review


def test_complete_receipt_limit_rejects_review_before_replacement(
    tmp_path: Path,
) -> None:
    store = receipts.ReceiptStore.for_repo(tmp_path, state_root=tmp_path / "state")
    review = {**_review_mapping(), "bounded_detail": ""}
    empty_review_size = len(receipts.canonical_json_bytes(review))
    review["bounded_detail"] = "x" * (
        receipts._RECEIPT_MAX_BYTES - empty_review_size
    )
    assert len(receipts.canonical_json_bytes(review)) == receipts._RECEIPT_MAX_BYTES

    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        reservation = attempt.reserve_or_load(_review_scope())
        receipt_path, _ = _receipt_paths(tmp_path / "state")
        reserved_bytes = receipt_path.read_bytes()
        with pytest.raises(receipts.ReceiptStateError) as captured:
            attempt.record_review(review)
        assert captured.value.reason == "receipt_too_large"
        assert receipt_path.read_bytes() == reserved_bytes

    with store.lock_attempt(_review_scope(), blocking=False) as attempt:
        recovered = attempt.reserve_or_load(_review_scope())
    assert reservation.action == "launch"
    assert recovered.action == "degrade_uncertain"
    assert recovered.record.state == "reserved"
