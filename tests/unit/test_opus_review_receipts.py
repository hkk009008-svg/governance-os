from __future__ import annotations

import dataclasses
import hashlib
import json

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
