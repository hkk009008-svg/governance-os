from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]
DELETED_PROVIDER_PATHS = (
    "scripts/chatgpt_pro_consult.py",
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
    "tests/unit/test_chatgpt_pro_consult.py",
    "tests/unit/test_opus_review_bridge.py",
    "tests/unit/test_opus_review_receipts.py",
    ".agents/skills/chatgpt-pro-consultation/SKILL.md",
    "docs/protocol/codex/chatgpt-pro-consultation-acceptance.md",
    "scripts/prompts/opus_lane_v_advisory.md",
    (
        "scripts/prompts/"
        "opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json"
    ),
)
FORBIDDEN_OPERATIVE_FRAGMENTS = (
    "ChatGPT Pro",
    "Opus",
    "import chatgpt_pro_consult",
    "import opus_review_bridge",
    "import opus_review_receipts",
    "render_chatgpt_pro_consultation(",
    "chatgpt_pro_consultation_default(",
    "CROSS_MODEL_VERIFICATION_RULES",
    "render_cross_model_verification",
    "opus-review/v3",
    "opus-reconciliation/v2",
    "lane-v-report/v2",
    "--receipt-id",
    "attempt_state_uncertain",
    "standing-policy:codex-lane-v-opus-v1",
    "scripts/prompts/opus_lane_v_advisory.md",
    "one provider process attempt",
    "degraded Codex-only fallback",
)
COMPACT_PAIR_REFERENCE = (
    "Canonical Compact Pair Invariant: scripts/codex_protocol_model.py"
)
COMPACT_PAIR_SURFACES = (
    "AGENTS.md",
    "docs/protocol/codex/continuation.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
    ".agents/skills/seat-operator/verification-report-format.md",
    ".claude/skills/seat-operator/verification-report-format.md",
    ".codex/agents/lane-v-verifier.toml",
    ".claude/agents/lane-v-verifier.md",
)
COMPACT_PAIR_CORE_SURFACES = COMPACT_PAIR_SURFACES[:10]
GENERIC_AUTHORITY_STATEMENTS = (
    (
        "Mailbox decisions remain body-first: read relevant mailbox bodies before "
        "acting; live seat cursors are intentional per-seat state, and the "
        "coordinator has no cursor."
    ),
    (
        "The verifying operator must be a non-author and alone issues GO/NITS/FAIL "
        "from repository evidence."
    ),
    (
        "The coordinator may route and reconcile but not author behavior-changing "
        "production fixes."
    ),
    (
        "Push, merge, paid spend, and every other side effect are separately gated "
        "and require explicit authority."
    ),
)
DECOMMISSION_CYCLE = "provider-tools-targeted-decommission-2026-07-16"
DECISIONS_PRE_TASK5_PREFIX_BYTES = 57_646
DECISIONS_PRE_TASK5_PREFIX_SHA256 = (
    "3f09b44a053200daf337d6227c9578907137bf1d17e41f5e18e13bb7686f63de"
)
DECOMMISSION_NEGATIVE_ACCEPTANCE = frozenset(
    {
        (
            "No ChatGPT Pro, Claude, Opus, provider CLI, in-app browser, paid API, "
            "provider retry, or provider receipt action is authorized."
        ),
        (
            "Commit, push, merge, provider launch, runtime cleanup, and external "
            "publication are separate authorities; this packet authorizes no push, "
            "merge, provider call, or cleanup."
        ),
    }
)
OPERATIVE_NEGATIVE_PROVIDER_SENTENCES = DECOMMISSION_NEGATIVE_ACCEPTANCE | {
    "Verify independently from repository evidence and run no provider command.",
    "repository evidence, and run no provider command.",
}
DECOMMISSION_PROVIDER_SCOPE_PATHS = frozenset(DELETED_PROVIDER_PATHS) | {
    ".claude/skills/seat-operator/verification-report-format.md",
    ".claude/agents/lane-v-verifier.md",
    "docs/protocol/claude/independence-first.md",
    ".claude/agents/readiness-bridge.md",
}
REQUIRED_REVIEWER_TEMPLATE_HEADINGS = (
    "# Reviewer prompt template - agent-neutral",
    "## Canonical verdict vocabulary",
    "## Independence + verify-before-asserting",
    "## Git hygiene",
    "## RESULT SCHEMA",
    "## Evidence preamble",
    "## Spec reviewer prompt template",
    "## Code quality reviewer prompt template",
)


def test_decommission_plan_matches_authoritative_base_bytes() -> None:
    plan = (
        ROOT
        / "docs/superpowers/plans/2026-07-16-provider-tools-targeted-decommission.md"
    ).read_bytes()
    assert hashlib.sha256(plan).hexdigest() == (
        "0e4b4940f3d193f1d9b8c183dbfa67023583d4621210c343cb3366034b161422"
    )


def test_provider_executable_surfaces_are_deleted() -> None:
    for relative in DELETED_PROVIDER_PATHS:
        assert not (ROOT / relative).exists(), relative


def test_protocol_model_has_no_chatgpt_consultation_contract() -> None:
    source = (ROOT / "scripts/codex_protocol_model.py").read_text(encoding="utf-8")
    forbidden = (
        "render_" "chatgpt_pro_consultation",
        "chatgpt_pro_" "consultation_default",
        "validate_" "chatgpt_pro_activation_evidence",
        "chatgpt_pro_" "guard_manifest_hash",
    )
    assert all(token not in source for token in forbidden)


def _operative_paths() -> tuple[Path, ...]:
    paths = [
        ROOT / "AGENTS.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "scripts/codex_protocol_model.py",
        ROOT / "docs/protocol/claude/independence-first.md",
        *sorted((ROOT / ".agents/skills").glob("**/*")),
        *sorted((ROOT / ".codex/agents").glob("*.toml")),
        *sorted((ROOT / ".claude/agents").glob("*.md")),
        *sorted((ROOT / "docs/protocol/codex").glob("*.md")),
        *sorted((ROOT / "docs/protocol/threeway").glob("*.md")),
    ]
    text_suffixes = {".md", ".py", ".toml", ".json", ".txt"}
    return tuple(
        path
        for path in paths
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix in text_suffixes
    )


def test_provider_tools_are_absent_from_executable_and_operative_surfaces() -> None:
    for path in _operative_paths():
        assert ".codex/runtime" not in path.as_posix()
        _assert_no_forbidden_operative_fragments(path)


KNOWN_PROVIDER_NAMES = (
    "chatgpt",
    "claude",
    "opus",
    "gemini",
    "anthropic",
    "openai",
    "gpt",
)
AFFIRMATIVE_ACTION_TOKENS = frozenset(
    {
        "run",
        "launch",
        "send",
        "review",
        "invoke",
        "query",
        "call",
        "execute",
        "use",
        "open",
        "dispatch",
    }
)
PROVIDER_ACTION_TOKEN_RADIUS = 3
PROVIDER_MECHANISM_TOKENS = frozenset(
    {
        "advisory",
        "api",
        "cli",
        "command",
        "execution",
        "invocation",
        "process",
        "receipt",
        "retry",
    }
)
NEUTRAL_UNIFIED_TOPOLOGY_TOKENS = frozenset(
    {"codex", "claude", "antigravity", "unified", "system", "cross", "provider", "protocol"}
)


def _match_tokens(value: object) -> tuple[str, ...]:
    serialized = json.dumps(value, sort_keys=True).casefold()
    return tuple(re.findall(r"[a-z0-9]+", serialized))


NORMALIZED_OPERATIVE_NEGATIVE_PROVIDER_SENTENCES = frozenset(
    " ".join(_match_tokens(sentence))
    for sentence in OPERATIVE_NEGATIVE_PROVIDER_SENTENCES
)


def _tokens_contain_compound_name(
    tokens: tuple[str, ...],
    name: str,
    *,
    split_only: bool = False,
) -> bool:
    for start in range(len(tokens)):
        candidate = ""
        for end in range(start, len(tokens)):
            candidate += tokens[end]
            if len(candidate) > len(name) or not name.startswith(candidate):
                break
            if candidate == name:
                return not split_only or end > start
    return False


def _contains_provider_name(
    tokens: tuple[str, ...],
    names: tuple[str, ...] = KNOWN_PROVIDER_NAMES,
    *,
    split_only: bool = False,
) -> bool:
    return any(
        _tokens_contain_compound_name(tokens, name, split_only=split_only)
        for name in names
    )


def _contains_provider_reference_near_action(tokens: tuple[str, ...]) -> bool:
    for index, token in enumerate(tokens):
        if token not in AFFIRMATIVE_ACTION_TOKENS:
            continue
        start = max(0, index - PROVIDER_ACTION_TOKEN_RADIUS)
        end = index + PROVIDER_ACTION_TOKEN_RADIUS + 1
        nearby = tokens[start:end]
        if "provider" in nearby or _contains_provider_name(nearby):
            return True
    return False


def _is_neutral_unified_topology_line(line: str, token_set: set[str]) -> bool:
    return line.lstrip().startswith("|") and NEUTRAL_UNIFIED_TOPOLOGY_TOKENS.issubset(
        token_set
    )


def _operative_provider_action_sensitive(line: str) -> bool:
    tokens = _match_tokens(line)
    token_set = set(tokens)
    neutral_unified_topology = _is_neutral_unified_topology_line(line, token_set)
    if (
        _contains_provider_reference_near_action(tokens)
        and not neutral_unified_topology
    ):
        return True
    if _contains_provider_name(tokens, ("opus",)):
        return True
    if _contains_provider_name(tokens, ("chatgpt",)) and "pro" in token_set:
        return True
    if _contains_provider_name(tokens, ("anthropic",)) and "api" in token_set:
        return True
    if _contains_provider_name(tokens, ("claude", "gemini"), split_only=True):
        return True
    if "retry" in token_set and token_set & {"external", "advisory"}:
        return True
    return {"review", "receipt", "dispatch"}.issubset(token_set)


def _assert_no_forbidden_operative_fragments(path: Path) -> None:
    text = path.read_text(encoding="utf-8").casefold()
    for line_number, line in enumerate(text.splitlines(), start=1):
        statements = re.split(r"(?<=[.!?])\s+", line)
        for statement in statements:
            if (
                " ".join(_match_tokens(statement))
                in NORMALIZED_OPERATIVE_NEGATIVE_PROVIDER_SENTENCES
            ):
                continue
            for fragment in FORBIDDEN_OPERATIVE_FRAGMENTS:
                normalized_fragment = fragment.casefold()
                assert normalized_fragment not in statement, (
                    path,
                    normalized_fragment,
                )
            assert not _operative_provider_action_sensitive(statement), (
                path,
                line_number,
                line,
            )


def test_operative_provider_scan_rejects_lowercase_chatgpt_pro(tmp_path: Path) -> None:
    operative = tmp_path / "operative.md"
    operative.write_text("launch chatgpt pro for review\n", encoding="utf-8")

    with pytest.raises(AssertionError, match="chatgpt pro"):
        _assert_no_forbidden_operative_fragments(operative)


@pytest.mark.parametrize(
    ("case_name", "affirmative_action"),
    (
        ("chatgpt_separators", "Launch Chat-GPT Pro for review"),
        ("claude_separators", "Run C-L-A-U-D-E against the diff"),
        ("anthropic_api", "Call the Anthropic API"),
        ("query_provider", "query-provider for external feedback"),
        ("external_advisory_retry", "retry external advisory"),
        ("review_receipt", "review receipt after dispatch"),
        ("split_name_json", {"binary_parts": ["clau", "de"]}),
    ),
)
def test_operative_provider_scan_rejects_obfuscated_provider_actions(
    tmp_path: Path,
    case_name: str,
    affirmative_action: object,
) -> None:
    operative = tmp_path / f"{case_name}.md"
    text = (
        affirmative_action
        if isinstance(affirmative_action, str)
        else json.dumps(affirmative_action, sort_keys=True)
    )
    operative.write_text(f"{text}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_no_forbidden_operative_fragments(operative)


def _provider_sensitive(value: object) -> bool:
    tokens = _match_tokens(value)
    normalized = " ".join(tokens)
    phrases = (
        "in app browser",
        "paid api",
        "receipt id",
    )
    if _contains_provider_name(tokens) or any(
        phrase in normalized for phrase in phrases
    ):
        return True

    token_set = set(tokens)
    if token_set & {"receipt", "retry"}:
        return True
    if {"external", "advisory"}.issubset(token_set):
        return True

    provider_actions = AFFIRMATIVE_ACTION_TOKENS | PROVIDER_MECHANISM_TOKENS
    return "provider" in token_set and bool(token_set & provider_actions)


def _done_evidence_invokes_provider(value: object) -> bool:
    tokens = _match_tokens(value)
    token_set = set(tokens)
    normalized = " ".join(tokens)
    if _contains_provider_reference_near_action(tokens):
        return True
    if "retry" in token_set and token_set & {"external", "advisory"}:
        return True
    if token_set & AFFIRMATIVE_ACTION_TOKENS and (
        any(
            phrase in normalized
            for phrase in ("in app browser", "paid api", "receipt id")
        )
        or bool(token_set & {"receipt", "retry"})
        or {"external", "advisory"}.issubset(token_set)
        or (
            "provider" in token_set
            and bool(token_set & PROVIDER_MECHANISM_TOKENS)
        )
    ):
        return True
    return False


def _assert_launchable_packet_provider_free(path: Path, packet: dict[str, object]) -> None:
    if packet["status"] not in {"ready", "active"}:
        return
    sensitive_fields = {
        key for key, value in packet.items() if _provider_sensitive(value)
    }
    if not sensitive_fields:
        return

    assert packet["cycle"] == DECOMMISSION_CYCLE, path
    for field in sensitive_fields:
        value = packet[field]
        if field in {"allowed_paths", "scope_files"}:
            for relative in value:
                if _provider_sensitive(relative):
                    assert relative in DECOMMISSION_PROVIDER_SCOPE_PATHS, (
                        path,
                        field,
                        relative,
                    )
            continue
        if field in {"id", "cycle"}:
            assert packet["cycle"] == DECOMMISSION_CYCLE, path
            continue
        if field == "acceptance":
            for statement in value:
                if _provider_sensitive(statement):
                    assert statement in DECOMMISSION_NEGATIVE_ACCEPTANCE, (
                        path,
                        field,
                        statement,
                    )
            continue
        if field == "done_evidence":
            for statement in value:
                assert not _done_evidence_invokes_provider(statement), (
                    path,
                    field,
                    statement,
                )
            continue
        raise AssertionError((path, field, value))


def _synthetic_ready_decommission_packet() -> dict[str, object]:
    source = (
        ROOT
        / "coordination/capacity/packets/"
        "2026-07-16-provider-tools-decommission-director-implementation.json"
    )
    packet = json.loads(source.read_text(encoding="utf-8"))
    packet["status"] = "ready"
    packet["done_evidence"] = []
    return packet


def test_launchable_capacity_packets_do_not_invoke_deleted_providers() -> None:
    packet_root = ROOT / "coordination/capacity/packets"
    for path in sorted(packet_root.glob("*.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        _assert_launchable_packet_provider_free(path, packet)


def test_launchable_capacity_gate_rejects_affirmative_provider_contradiction() -> None:
    packet = _synthetic_ready_decommission_packet()
    packet["done_evidence"] = [
        "Run claude -p 'review the diff' after the provider-neutral check"
    ]

    with pytest.raises(AssertionError, match="done_evidence"):
        _assert_launchable_packet_provider_free(Path("synthetic.json"), packet)


def test_launchable_capacity_gate_rejects_command_disguised_as_scope() -> None:
    packet = _synthetic_ready_decommission_packet()
    packet["allowed_paths"].append("claude -p 'execute provider review'")

    with pytest.raises(AssertionError, match="allowed_paths"):
        _assert_launchable_packet_provider_free(Path("synthetic.json"), packet)


@pytest.mark.parametrize(
    ("field", "affirmative_action"),
    (
        ("gemini_action", "Run Gemini CLI against the candidate"),
        ("browser_action", "Open the in-app browser for review"),
        ("api_action", "Use a paid API for verification"),
        (
            "nested_action",
            {"provider": {"command": "review the candidate"}},
        ),
    ),
)
def test_launchable_capacity_gate_rejects_alternate_provider_actions(
    field: str,
    affirmative_action: object,
) -> None:
    packet = _synthetic_ready_decommission_packet()
    packet[field] = affirmative_action

    with pytest.raises(AssertionError, match=field):
        _assert_launchable_packet_provider_free(Path("synthetic.json"), packet)


@pytest.mark.parametrize(
    ("field", "affirmative_action"),
    (
        ("chatgpt_separators", "Launch Chat-GPT Pro for review"),
        ("claude_separators", "Run C-L-A-U-D-E against the diff"),
        ("anthropic_api", "Call the Anthropic API"),
        ("query_provider", "query-provider for external feedback"),
        ("external_advisory_retry", "retry external advisory"),
        ("review_receipt", "review receipt after dispatch"),
        ("split_name_json", {"binary_parts": ["clau", "de"]}),
    ),
)
def test_launchable_capacity_gate_rejects_obfuscated_provider_actions(
    field: str,
    affirmative_action: object,
) -> None:
    packet = _synthetic_ready_decommission_packet()
    packet[field] = affirmative_action

    with pytest.raises(AssertionError, match=field):
        _assert_launchable_packet_provider_free(Path("synthetic.json"), packet)


def test_launchable_capacity_gate_accepts_exact_negative_decommission_packet() -> None:
    path = (
        ROOT
        / "coordination/capacity/packets/"
        "2026-07-16-provider-tools-decommission-director-implementation.json"
    )
    packet = json.loads(path.read_text(encoding="utf-8"))

    assert DECOMMISSION_NEGATIVE_ACCEPTANCE.issubset(set(packet["acceptance"]))
    _assert_launchable_packet_provider_free(path, packet)


AFFIRMATIVE_PROVIDER_ACTION_PROBES = (
    ("claude_run", "Run Claude -p review now"),
    ("gemini_launch", "Launch Gemini CLI against the candidate"),
    ("provider_send", "Send candidate to provider for review"),
    ("provider_review", "Review with provider now"),
    ("openai_api", "Send candidate to OpenAI API"),
    ("gpt5_review", "Invoke GPT-5 for review"),
)

NEGATED_PREFIX_AFFIRMATIVE_PROVIDER_ACTION_PROBES = (
    ("claude_execute", "Do not delay; execute Claude -p now."),
    ("gpt5_invoke", "Never wait; invoke GPT-5 now."),
    ("openai_send", "Do not defer; send to OpenAI now."),
    ("anthropic_call", "Without delay, call Anthropic now."),
)


@pytest.mark.parametrize(
    ("case_name", "affirmative_action"), AFFIRMATIVE_PROVIDER_ACTION_PROBES
)
def test_operative_provider_scan_rejects_known_provider_affirmative_actions(
    tmp_path: Path,
    case_name: str,
    affirmative_action: str,
) -> None:
    operative = tmp_path / f"{case_name}.md"
    operative.write_text(f"{affirmative_action}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_no_forbidden_operative_fragments(operative)


@pytest.mark.parametrize(
    ("case_name", "affirmative_action"),
    NEGATED_PREFIX_AFFIRMATIVE_PROVIDER_ACTION_PROBES,
)
def test_operative_provider_scan_rejects_affirmative_actions_after_negated_prefixes(
    tmp_path: Path,
    case_name: str,
    affirmative_action: str,
) -> None:
    operative = tmp_path / f"{case_name}.md"
    operative.write_text(f"{affirmative_action}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_no_forbidden_operative_fragments(operative)


@pytest.mark.parametrize(
    "negative_acceptance", sorted(DECOMMISSION_NEGATIVE_ACCEPTANCE)
)
def test_operative_provider_scan_accepts_exact_negative_decommission_sentences(
    tmp_path: Path,
    negative_acceptance: str,
) -> None:
    operative = tmp_path / "negative-acceptance.md"
    operative.write_text(f"{negative_acceptance}\n", encoding="utf-8")

    _assert_no_forbidden_operative_fragments(operative)


@pytest.mark.parametrize(
    ("field", "affirmative_action"), AFFIRMATIVE_PROVIDER_ACTION_PROBES
)
def test_launchable_capacity_gate_rejects_known_provider_affirmative_actions(
    field: str,
    affirmative_action: str,
) -> None:
    packet = _synthetic_ready_decommission_packet()
    packet[field] = affirmative_action

    with pytest.raises(AssertionError, match=field):
        _assert_launchable_packet_provider_free(Path("synthetic.json"), packet)


@pytest.mark.parametrize(
    "neutral_topology",
    (
        "Claude and Gemini are provider names in this topology.",
        "OpenAI and GPT-5 are model/provider labels.",
    ),
)
def test_operative_provider_scan_allows_neutral_provider_topology(
    tmp_path: Path,
    neutral_topology: str,
) -> None:
    operative = tmp_path / "topology.md"
    operative.write_text(f"{neutral_topology}\n", encoding="utf-8")

    _assert_no_forbidden_operative_fragments(operative)


def test_threeway_dual_chief_contract_remains_provider_neutral_and_two_input() -> None:
    doctrine = _read("docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md")
    adoption = _read("docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md")
    diagram = _read("docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md")
    onboarding = _read("docs/protocol/threeway/ONBOARDING.md")

    assert (
        "| dual chief | two separately approved, human-relayed external "
        "advisory apps |"
    ) in doctrine
    assert "The dual chief comprises two separately approved" in adoption
    assert "Dual Chief<br/>Two Separately Approved External Advisory Apps" in diagram
    assert "Antigravity holds NO Layer-1 seat and is NOT the dual chief" in onboarding

    for text in (doctrine, adoption, diagram, onboarding):
        assert "Gemini Deep Think + ChatGPT Pro" not in text


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _trigger_contract_text(path: str) -> str:
    return _compact(_read(path).replace("`", ""))


VERIFY_REQUEST_TRIGGER_FRAGMENTS = (
    "one committed verify-request",
    "full reviewed base/head",
    "author seat/model",
    "assigned Operator",
    "question",
    "allowed paths",
    "commands",
)
INVALID_TRIGGER_FRAGMENTS = (
    "Missing, duplicated, abbreviated, uppercase, uncommitted, or mismatched",
    "not authority",
    "stop with a blocker",
)
TASK8_TRIGGER_FRAGMENT_CATEGORIES = (
    ("lawful verify-request production", VERIFY_REQUEST_TRIGGER_FRAGMENTS),
    ("invalid-trigger fail-closed", INVALID_TRIGGER_FRAGMENTS),
)


def test_agent_neutral_reviewer_template_exists_with_schema():
    text = _read("docs/templates/agents/reviewer.md")

    assert "schema_version" in text
    assert "reviewer-result/1" in text
    assert '"verdict": "pass | issues | unable_to_verify"' in text
    assert "env -u GIT_INDEX_FILE" in text


def test_agent_neutral_reviewer_template_keeps_required_plan_headings():
    text = _read("docs/templates/agents/reviewer.md")
    normalized = text.replace("—", "-")

    for heading in REQUIRED_REVIEWER_TEMPLATE_HEADINGS:
        assert heading in normalized


def test_codex_director_skill_uses_agent_neutral_templates():
    for path in (
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-director/r-brief-template.md",
        ".agents/skills/seat-operator/SKILL.md",
    ):
        text = _read(path)
        assert "docs/templates/agents/" in text
        assert "docs/protocol/agents/orchestration.md" in text
        assert "docs/templates/claude/implementer.md" not in text
        assert "docs/templates/claude/reviewer.md" not in text
        assert "docs/protocol/claude/orchestration.md" not in text


def test_claude_function_harmonization_is_model_backed_and_documented():
    rendered = model.render_claude_function_harmonization()

    required_phrases = (
        "Claude Function Harmonization:",
        "adapt Claude functions to Codex-native primitives",
        "do not transplant Claude-only mechanics",
        "AskUserQuestion discipline",
        "background work discipline",
        "dispatch-template minimalism",
        "reviewer evidence rigor",
        "adversarial verification",
    )
    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        text = _read(path)
        for phrase in required_phrases:
            assert phrase in text


def test_reviewer_template_adopts_claude_evidence_rigor_without_claude_mechanics():
    text = _read("docs/templates/agents/reviewer.md")

    for reason in ("U1", "U2", "U3", "U4", "U5"):
        assert reason in text
    assert "reviewed_head != reviewed_commit" in text
    assert "working_tree_clean=false" in text
    assert "--runxfail" in text
    assert "Execute touched scripts or hooks" in text
    assert "Do not cite Claude-only tool syntax" in text


def test_codex_specialist_agents_require_adversarial_proof_loop():
    for path in (
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
    ):
        text = _read(path)
        assert "Adversarial proof loop" in text
        assert "try to make the gate or proof fail" in text
        assert "unable_to_verify" in text


def test_codex_facing_prompts_name_pipeline_not_content():
    paths = [
        ".agents/skills/four-seat-protocol/SKILL.md",
        *sorted(
            str(path.relative_to(ROOT))
            for path in (ROOT / ".codex" / "agents").glob("*.toml")
        ),
    ]

    for path in paths:
        text = _read(path)
        assert "Content four-seat process" not in text
        assert "Content repo's four-seat protocol" not in text
        assert "Content repo" not in text


def test_live_seat_behavior_sources_use_director_and_operator2_defaults():
    assert model.SEAT_BEHAVIOR_SOURCE == {
        "director": "director",
        "director2": "director",
        "operator": "operator2",
        "operator2": "operator2",
    }

    expected_map = (
        "Behavior source map: `director -> director`, `director2 -> director`, "
        "`operator -> operator2`, `operator2 -> operator2`."
    )
    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        assert expected_map in _read(path)

    director_prompt = _read(".codex/agents/protocol-director.toml")
    operator_prompt = _read(".codex/agents/protocol-operator.toml")
    assert "Canonical behavior source: `director` for both `director` and `director2`" in director_prompt
    assert "Canonical behavior source: `operator2` for both `operator` and `operator2`" in operator_prompt

    threeway_adoption = _read("docs/protocol/threeway/CODEX-ADOPTION.md")
    assert "behavior source is `director`" in threeway_adoption
    assert "behavior source `operator2`" in threeway_adoption


def test_subagent_utilization_decision_is_rendered_and_documented():
    rendered = model.render_seat_subagent_development()
    assert "Subagent utilization decision" in rendered
    assert "direct/no-op because" in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
    ):
        text = _read(path)
        assert "Subagent utilization decision" in text
        assert "direct/no-op because" in text


def test_codex_execution_tiers_are_model_backed_and_surface_synced():
    expected = (
        (
            "tier-0-conversational",
            "self-contained answer",
            "no repo orientation, implementation skills, mailbox checks, "
            "smoke, worktree, or verification commands",
        ),
        (
            "tier-1-read-only",
            "repository inspection or evidence-backed report",
            "smallest scoped read commands; no implementation skills or "
            "live-seat checks without an explicit protocol trigger",
        ),
        (
            "tier-2-local-mutation",
            "ordinary code, test, config, or documentation edit",
            "impact analysis, task-relevant implementation discipline, focused "
            "tests, and one completion verification pass",
        ),
        (
            "tier-3-governed-side-effect",
            "live-seat decision, shared protocol state, or external side effect",
            "exact mailbox, capacity, independent-verification, and "
            "user-authorization gates",
        ),
    )

    assert model.CODEX_EXECUTION_TIERS == expected
    rendered = model.render_codex_execution_tiers()
    for tier in expected:
        assert all(value in rendered for value in tier)
    assert "unchanged HEAD and unchanged relevant paths" in rendered
    assert "same unchanged commit" in rendered
    assert "Deterministic artifact evidence may be reused" in rendered
    assert "Tier 3 requires fresh signed-bus, mailbox/cursor, lock, approval" in rendered
    assert "reuse never relaxes a triggered guard" in rendered

    for path in ("AGENTS.md", "docs/protocol/codex/continuation.md"):
        text = _compact(_read(path))
        for tier, _, _ in expected:
            assert tier in text
        assert "same unchanged commit" in text
        assert "Deterministic artifact evidence may be reused" in text
        assert "Tier 3 requires fresh signed-bus, mailbox/cursor, lock, approval" in text
        assert "reuse never relaxes a triggered guard" in text


def test_r_independence_is_model_backed_and_surface_synced():
    assert model.R_INDEPENDENCE_TRIGGER_SURFACES == (
        "input rendered or composed into a parseable or executable context",
        "authority or security-boundary enforcement",
        "side-effect gating",
        "schema validation whose acceptance grants trust",
    )

    rendered = model.render_r_independence()
    required = (
        "R-INDEPENDENCE",
        "standing default",
        "before implementation",
        "independent design-time enumeration",
        "abuse cases, edge cases, and coverage targets",
        "different model or harness is preferred",
        "same-model independent reviewer is weaker",
        "committed plan or equivalent durable artifact",
        "independent reviewer verifies the actual diff",
        "compact pair",
        "fixed mailbox writer",
        "R-VERIFY-TIER",
        "docs/protocol/claude/independence-first.md",
    )
    for phrase in required:
        assert phrase in rendered

    shared_surface_phrases = (
        "R-INDEPENDENCE",
        "adversarial-surface",
        "before implementation",
        "independent design-time enumeration",
        "enforced-and-tested",
        "verify the actual diff",
        "R-VERIFY-TIER",
    )
    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
    ):
        text = _compact(_read(path))
        for phrase in shared_surface_phrases:
            assert phrase in text, (path, phrase)

    assert "R-INDEPENDENCE" in model.render_start_session_inhabitance()


def test_agent_extension_routing_contract_is_model_backed():
    expected_contract = (
        (
            "agent01",
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
        ),
        (
            "agent02",
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
        ),
        (
            "agent03",
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
        ),
        (
            "agent04",
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
        ),
    )

    assert model.AGENT_EXTENSION_ROUTING_CONTRACT == expected_contract

    rendered = model.render_agent_extension_routing_contract()
    assert "Agent Extension Routing Contract:" in rendered
    for agent, purpose, route_when in expected_contract:
        assert agent in rendered
        assert purpose in rendered
        assert route_when in rendered

    assert "extension output is evidence for the parent" in rendered
    assert "not a mailbox event, cursor advance, operator GO, coordinator route, lock action, push, or spend authorization" in rendered


def test_agentnn_extensions_have_distinct_routing_prompts():
    expected = {
        "agent01": (
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
            "build all-seat awareness",
        ),
        "agent02": (
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
            "bounded protocol edits, handoffs, mailbox/cursor maintenance, or Codex agent/config edits",
        ),
        "agent03": (
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
            "defaults to readiness-bridge posture when no live role is named",
        ),
        "agent04": (
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
            "diagnose stale indexes, mailbox drift, routing gaps, gate/readiness evidence, and authority mismatches",
        ),
    }

    assert dict(
        (agent, (purpose, route_when))
        for agent, purpose, route_when in model.AGENT_EXTENSION_ROUTING_CONTRACT
    ) == {
        agent: values[:2]
        for agent, values in expected.items()
    }

    for agent, phrases in expected.items():
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in phrases:
            assert phrase in text


def test_agentnn_extensions_keep_no_seat_authority_boundary():
    required_phrases = (
        "extension, not a protocol seat",
        "cannot consume cursors, send mailbox events, issue GO, create coordinator routes, claim locks, push, start pods, or spend paid API budget",
        "authority work routes to `protocol-director`, `protocol-operator`, or `protocol-coordinator`",
        "extension output is evidence for the parent",
    )

    for agent in ("agent01", "agent02", "agent03", "agent04"):
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in required_phrases:
            assert phrase in text


def test_agent04_uses_artifact_neutral_capacity_language():
    text = _read(".codex/agents/agent04.toml")

    assert "target proof artifacts" in text
    assert "co-sign or target-proof review" in text
    assert "product-oracle status" not in text
    assert "co-sign/product-oracle review" not in text


def test_capacity_split_default_is_model_backed_and_surface_synced():
    rendered = model.render_capacity_split_default()

    required_phrases = (
        "Capacity Split Default:",
        "single-pair fast path remains the default for narrow or shared-file work",
        "divisible or preplanned larger work defaults to dual-pair routing",
        "two independently reviewable deliverables",
        "director owns Chunk A and operator verifies Chunk A",
        "director2 owns Chunk B and operator2 verifies Chunk B",
        "Pair B performs bounded planning or preflight instead of idle standby",
        "Pair B preflight packets use `director-preflight` and `operator-preflight` packet types",
        "coordinator owns convergence",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/agent01.toml",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_side_effect_executor_token_contract_is_model_backed_and_documented():
    rendered = model.render_side_effect_executor_contract()

    required_phrases = (
        "Side-Effect Executor Token:",
        "side_effect_id",
        "allowed_command_class",
        "stop_if_newer_mail_or_live_target_satisfied",
        "observer seats default to observer mode",
        "generic user approval is unit consent, not executor election",
        "live evidence may close an already-satisfied side effect",
    )
    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _read(path)
        for phrase in required_phrases:
            assert phrase in text


def test_side_effect_executor_token_detailed_contract_is_surface_synced():
    rendered = model.render_side_effect_executor_contract()
    detailed_phrases = (
        "shared user-gated side effects need exactly one named executor",
        "side effects covered: remote-ref update",
        "multiple same-target side-effect success claims need a common side_effect_id",
        "report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request",
    )
    for phrase in detailed_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _read(path)
        for phrase in detailed_phrases:
            assert phrase in text


def test_optional_codex_agent_selection_matrix_exists():
    text = _read(".codex/agents/README.md")

    for phrase in (
        "Optional Agent Selection Matrix",
        "agent01",
        "agent02",
        "agent03",
        "agent04",
        "These agents do not replace protocol-director, protocol-operator, or protocol-coordinator.",
    ):
        assert phrase in text


def test_rule_12_pattern_reference_transplant_is_surface_synced():
    required_phrases = (
        "brief-pattern references are runtime claims when they cite canonical sites",
        "verify the named symbol exists at the cited SHA",
        "verify the cited SHA exhibits the named sub-pattern",
    )

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        ".agents/skills/seat-director/SKILL.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_rule_13_disposition_transplant_is_surface_synced():
    required_phrases = (
        "audit-completeness is not audit-disposition",
        "mirror / defer / document / exempt",
        "state the disposition for each sibling",
    )

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-director/r-brief-template.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_pattern_doc_uniformity_transplant_is_surface_synced():
    required_phrases = (
        "pattern-doc uniformity pass",
        "cumulative production sites cross 20",
        "per-site detail drift",
    )

    for path in (
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
        "docs/PROTOCOL-RULES-LOG.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_emergency_and_disagreement_contracts_are_model_backed_and_synced():
    emergency_rendered = model.render_emergency_handling_contract()
    disagreement_rendered = model.render_disagreement_handling_contract()

    emergency_phrases = (
        "Production-affecting OR user-data-integrity issue",
        "Security-critical",
        "Active bleed-rate",
        "External time-pressure",
        "first-noticer claims initial response",
        "stop-the-bleed first",
        "acting under v5 §E temporary authority",
        "coordinator no-production-code boundary remains in force",
        "post-incident note",
    )
    disagreement_phrases = (
        "States the disagreement explicitly",
        "project-data-grounded evidence",
        "counter-refinement",
        "defer to v(N+1)",
        "acceptance criterion",
        "silent-accept is the receiver's own acceptance",
        "2-cycle escalation limit",
    )

    for phrase in emergency_phrases:
        assert phrase in emergency_rendered
    for phrase in disagreement_phrases:
        assert phrase in disagreement_rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _compact(_read(path))
        for phrase in (*emergency_phrases, *disagreement_phrases):
            assert phrase in text


def test_blocked_wave_and_acting_coordinator_contract_is_model_backed_and_synced():
    rendered = model.render_blocked_wave_acting_coordinator_contract()
    required_phrases = (
        "wave-gate evidence before asserting blocked",
        "immediate pod-off when a director gate-request is unserviced",
        "one consolidated mailbox event naming blocker, owner, and SLA",
        "escalate to user with the acting-coordinator path",
        "pre-brief skeleton only",
        "no gate-relaxing or suppressive pins",
        "verified only from operator GO",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_reviewer_result_handling_contract_is_model_backed_and_synced():
    rendered = model.render_reviewer_result_handling_contract()
    required_phrases = (
        "findings-first ordering by severity",
        "preserve verdict, findings, and next steps",
        "separate uncertainty, inference, and follow-up",
        "do not auto-fix after a review",
        "failed, incomplete, or unable_to_verify runs are not permission to invent substitute output",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
        "docs/templates/agents/reviewer.md",
        "docs/templates/agents/implementer.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_compact_pair_is_model_backed_and_surface_synced():
    rendered = model.render_lane_v_v3()
    required = (
        "Compact Pair Invariant",
        "one committed verify-request",
        "full reviewed base/head",
        "author seat/model",
        "assigned Operator",
        "question",
        "allowed paths",
        "commands",
        "mailbox bodies before acting",
        "live seat cursors are intentional per-seat state",
        "coordinator has no cursor",
        "non-author",
        "GO/NITS/FAIL",
        "fixed mailbox writer",
        "no descriptor, shipping-trigger alternative, task publication state, or recovery path",
        "coordinator may route and reconcile but not author behavior-changing production fixes",
        "push, merge, paid spend, and every other side effect are separately gated",
    )
    for phrase in required:
        assert phrase in rendered

    for path in COMPACT_PAIR_SURFACES:
        assert COMPACT_PAIR_REFERENCE in _compact(_read(path).replace("`", "")), path

    for path in COMPACT_PAIR_CORE_SURFACES:
        text = _compact(_read(path)).lower()
        for statement in GENERIC_AUTHORITY_STATEMENTS:
            assert statement.lower() in text, (path, statement)

    invariants = dict(model.ACTIVE_KERNEL_INVARIANTS)
    assert "merge" in invariants["user-gated side effects"]
    assert "separately gated" in invariants["separate side-effect gates"]

    source = _read("scripts/codex_protocol_model.py")
    assert "CROSS_MODEL_VERIFICATION_RULES" not in source
    assert "render_cross_model_verification" not in source

    hooks = _read(".codex/hooks.json")
    assert "verification_report_gate" not in hooks


@pytest.mark.parametrize(
    ("renderer_name", "rendered"),
    (
        ("render_runtime_env_contract", model.render_runtime_env_contract({})),
        ("render_seat_contract", model.render_seat_contract({})),
    ),
)
def test_executable_contract_renderers_separately_gate_merge(
    renderer_name: str,
    rendered: str,
) -> None:
    normalized = rendered.lower()
    assert "merge" in normalized, renderer_name
    assert "separately gated" in normalized, renderer_name
    assert "user consent" in normalized, renderer_name


def test_lane_v_trigger_producer_contract_is_surface_synced() -> None:
    producer_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "scripts/codex_protocol_model.py",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".codex/agents/protocol-director.toml",
    )

    for path in producer_paths:
        text = _trigger_contract_text(path)
        assert COMPACT_PAIR_REFERENCE in text, path


def test_lane_v_trigger_consumer_contract_is_surface_synced() -> None:
    consumer_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "scripts/codex_protocol_model.py",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    )

    for path in consumer_paths:
        text = _trigger_contract_text(path)
        assert COMPACT_PAIR_REFERENCE in text, path


def test_lane_v_trigger_renderers_include_every_task8_contract_category() -> None:
    rendered_outputs = (
        ("render_pair_operating_contract", model.render_pair_operating_contract()),
        (
            "render_lane_v_v3",
            model.render_lane_v_v3(),
        ),
    )

    for renderer_name, rendered in rendered_outputs:
        text = _compact(rendered.replace("`", ""))
        for category, fragments in TASK8_TRIGGER_FRAGMENT_CATEGORIES:
            for fragment in fragments:
                assert fragment in text, (renderer_name, category, fragment)


def test_lane_v_active_surfaces_remove_commit_only_and_prose_only_substitutes() -> None:
    rendered_pair = model.render_pair_operating_contract()
    rendered_lane_v = model.render_lane_v_v3()
    stale_model_phrases = (
        "operator verifies only that artifact or landed commit",
        "include commit/range, brief path",
        "Operator waits for a fresh verify-request or shipping commit",
        "Lane-V-Scope",
        "TaskPublicationStore",
    )
    for phrase in stale_model_phrases:
        assert phrase not in rendered_pair
        assert phrase not in rendered_lane_v

    active_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
    )
    stale_surface_phrases = (
        "send one verify-request to operator with commit/range, tests, and exclusions",
        "verify only the named verify-request or shipping commit/range",
        "Fresh verify-request naming a commit/range, scope",
        "Lane-V-Scope",
        "TaskPublicationStore",
    )
    for path in active_paths:
        text = _trigger_contract_text(path)
        for phrase in stale_surface_phrases:
            assert phrase not in text, (path, phrase)

    for path in (
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/reviewer.md",
    ):
        assert "the only sanctioned trailer" not in _read(path), path


def test_implementer_and_reviewer_templates_never_invent_trigger_authority() -> None:
    implementer_paths = (
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
    )
    reviewer_paths = (
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/reviewer.md",
    )
    for path in implementer_paths:
        text = _trigger_contract_text(path)
        assert "never invent trigger authority" in text, path

    for path in reviewer_paths:
        text = _trigger_contract_text(path)
        assert "a named commit or prose-only event is not trigger authority" in text, path
        assert "never invent trigger authority" in text, path


def test_lane_v_trigger_guidance_pins_compact_report_and_pipeline_boundary() -> None:
    report_paths = (
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    )
    for path in report_paths:
        text = _read(path)
        assert "Event type: verification-report" in text, path
        assert "Verification request:" in text, path
        assert "Reviewer seat:" in text, path
        assert "Reviewer model:" in text, path
        assert "Verification harness:" in text, path
        assert "Verification context:" in text, path
        assert "## Allowed Paths" in text, path
        assert "--receipt-id" not in text, path
        assert "provider process" not in text, path

    verifier = _trigger_contract_text(".codex/agents/lane-v-verifier.toml")
    assert COMPACT_PAIR_REFERENCE in verifier
    assert "Event type: verification-report" in verifier
    assert "--receipt-id" not in verifier

    agent_report = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_report = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_report.read_bytes() == claude_report.read_bytes()


def test_active_codex_operator_prompts_drop_descriptor_v3_contract() -> None:
    operator = _trigger_contract_text(".codex/agents/protocol-operator.toml")
    verifier_raw = _read(".codex/agents/lane-v-verifier.toml")
    verifier = _trigger_contract_text(".codex/agents/lane-v-verifier.toml")

    assert "resolve one trigger-bound committed lane-v-scope/v1 descriptor" not in operator
    assert "require the exact ordered lane-v-report/v3 block" not in operator
    assert "against the descriptor" not in verifier_raw
    assert verifier.count(COMPACT_PAIR_REFERENCE) == 1

    required = (
        "one assigned committed verify-request",
        "Verification request: canonical committed request path@full request commit",
        "Reviewed head and Reviewed base: exact full lowercase SHAs from the request",
        "assigned non-author Operator seat",
        "Reviewer model: actual model identity, different from the author model",
        "Verification harness and Verification context",
        "Allowed Paths exactly matching the request",
        "GO / NITS / FAIL",
        "coordination/bin/send-event",
    )
    for phrase in required:
        assert phrase in operator, phrase
        assert phrase in verifier, phrase


def test_task8_scope_covers_the_exact_trigger_authority_generation() -> None:
    descriptor_path = (
        "coordination/verification/scopes/"
        "2a876e95-3a87-4203-a613-1a29dd957b5b.json"
    )
    descriptor_raw = (ROOT / descriptor_path).read_bytes()
    descriptor = json.loads(descriptor_raw)
    old_digest = "74d50ded74c017c614fb6a746231e0f910ac28d247c9ad728c099f71d2aa8ffe"
    task7_digest = "c16aa28ce9211e7214ba8fb5586059515a8a59de3b37a0f853c6e13da73d5a93"
    current_digest = "e393655f4ba9ad0dcfa0467fcc54c809c79a1b28b76a2022a7d846acc8996e84"

    expected_roots = (
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator",
        ".claude/agents/lane-v-verifier.md",
        ".claude/skills/seat-director/SKILL.md",
        ".claude/skills/seat-operator",
        ".codex/agents",
        ".github/workflows/ci.yml",
        ".gitignore",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "DECISIONS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
        "coordination/bin/send-event",
        "coordination/verification/scopes",
        "docs/PROGRAM-MANUAL.md",
        "docs/PROTOCOL-RULES-LOG.md",
        "docs/protocol",
        "docs/superpowers/plans",
        "docs/superpowers/specs",
        "docs/templates/agents/implementer.md",
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/implementer.md",
        "docs/templates/claude/reviewer.md",
        "scripts",
        "tests/unit",
    )
    expected_focused_command = (
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
        "tests/unit/test_opus_review_receipts.py "
        "tests/unit/test_opus_review_bridge.py "
        "tests/unit/test_check_go_schema.py "
        "tests/unit/test_verification_report_gate.py "
        "tests/unit/test_coordination_tooling.py "
        "tests/unit/test_protocol_prompt_sync.py "
        "tests/unit/test_protocol_capacity.py "
        "tests/unit/test_protocol_doc_integrity.py -q"
    )

    assert descriptor["allowed_path_roots"] == list(expected_roots)
    assert descriptor["allowed_path_roots"] == sorted(descriptor["allowed_path_roots"])
    assert descriptor["verification_commands"][0] == expected_focused_command
    for broad_substitute in (".agents/skills", ".claude/agents", ".claude/skills", "docs"):
        assert broad_substitute not in descriptor["allowed_path_roots"]
    assert hashlib.sha256(descriptor_raw).hexdigest() == current_digest

    plan = _read(
        "docs/superpowers/plans/2026-07-13-opus-lanev-receipt-hardening.md"
    )
    design = _read(
        "docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md"
    )
    compact_plan = _compact(plan)
    compact_design = _compact(design)
    assert (
        f"Prep Task 5B and committed Task 6 remain historically bound to "
        f"`sha256:{old_digest}`" in compact_plan
    )
    assert (
        "Task 7 and the post-Task-7 test-only integration correction remain "
        f"historically bound to the amended `sha256:{task7_digest}` generation"
        in compact_plan
    )
    assert (
        f"Prep 5B and committed Task 6 remain historically bound to `{old_digest}`"
        in compact_design
    )
    assert (
        "Task 7 and its post-task test-only correction use the amended digest "
        f"`{task7_digest}`" in compact_design
    )

    task7 = plan.split("### Task 7:", 1)[1].split(
        "## Final Integration And Verification", 1
    )[0]
    correct_prior_design = (
        "docs/superpowers/specs/"
        "2026-07-12-codex-opus-cross-model-verification-design.md"
    )
    mistyped_prior_design = correct_prior_design.replace("/specs/", "/plans/")
    assert f"- Modify: `{descriptor_path}`" in task7
    assert descriptor_path in task7
    assert f"@sha256:{task7_digest}" in task7
    assert correct_prior_design in task7
    assert mistyped_prior_design not in task7

    task8 = plan.split("### Task 8:", 1)[1].split(
        "## Final Integration And Verification", 1
    )[0]
    expected_additions = (
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/agents/lane-v-verifier.md",
        ".claude/skills/seat-director/SKILL.md",
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
        "docs/PROGRAM-MANUAL.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/implementer.md",
        "docs/templates/claude/reviewer.md",
    )
    for path in expected_additions:
        assert path in task8
    assert f"@sha256:{current_digest}" in task8

    final = plan.split("## Final Integration And Verification", 1)[1]
    assert f"Expected descriptor digest: `{current_digest}`" in final
    assert f"with amended digest `{current_digest}`" in _compact(final)


def test_verification_report_format_mirrors_pin_the_compact_binding_order():
    agent_path = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_path = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_path.read_bytes() == claude_path.read_bytes()

    text = agent_path.read_text(encoding="utf-8")
    start = text.index("Event type:", text.index("## Body skeleton"))
    end = text.index("\n\n## Findings", start)
    field_lines = [
        line.split(":", 1)[0] + ":"
        for line in text[start:end].splitlines()
        if line and ":" in line and not line.startswith("## ")
    ]
    assert field_lines == [
        "Event type:",
        "VERDICT:",
        "Verification request:",
        "Reviewed head:",
        "Reviewed base:",
        "Reviewer seat:",
        "Reviewer model:",
        "Verification harness:",
        "Verification context:",
    ]


def test_provider_tool_decommission_is_current_architecture_and_append_only_decision():
    architecture = _read("ARCHITECTURE.md")
    decisions = (ROOT / "DECISIONS.md").read_bytes()

    prefix = decisions[:DECISIONS_PRE_TASK5_PREFIX_BYTES]
    assert hashlib.sha256(prefix).hexdigest() == DECISIONS_PRE_TASK5_PREFIX_SHA256
    appended = decisions[DECISIONS_PRE_TASK5_PREFIX_BYTES:].decode("utf-8")
    assert "## Targeted decommission of Opus and ChatGPT Pro tools" in appended
    assert "lane-v-report/v3" in appended
    assert "TaskPublicationStore" in appended
    assert "frozen historical" in appended
    assert ".codex/runtime" in appended
    assert "separate approval" in appended

    assert COMPACT_PAIR_REFERENCE in _compact(architecture.replace("`", ""))
    assert "TaskPublicationStore" not in architecture
    assert "R-INDEPENDENCE" in architecture
    assert "lane-v-report/v2" not in architecture


def test_cross_model_design_and_plan_match_safe_mode_system_prompt_boundary():
    for path in (
        "docs/superpowers/specs/2026-07-12-codex-opus-cross-model-verification-design.md",
        "docs/superpowers/plans/2026-07-12-codex-opus-cross-model-verification.md",
    ):
        text = _read(path)
        assert "--safe-mode" in text, path
        assert "--disable-slash-commands" in text, path
        assert "--append-system-prompt" in text, path
        assert "dynamically injects" not in text, path
