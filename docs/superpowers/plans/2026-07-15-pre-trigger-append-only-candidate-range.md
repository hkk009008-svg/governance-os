# Pre-Trigger Append-Only Candidate Range Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make one-to-five-commit, append-only pre-trigger review correction executable and fail closed from coordinator route through Lane V resolution.

**Architecture:** Extend the existing capacity packet with one exact `candidate_policy`, then put all Git graph, range, path, mode, evidence-preservation, and pre-freeze checks in `scripts/protocol_capacity.py`. The capacity-board CLI and the Lane V bridge call that same validator; a backward-compatible `lane-v-scope/v2` descriptor binds the validated final head while legacy `lane-v-scope/v1` descriptors keep their existing behavior.

**Tech Stack:** Python 3.14, frozen dataclasses, `argparse`, `/usr/bin/git --no-replace-objects`, strict JSON, pytest, Markdown/TOML protocol mirrors.

## Global Constraints

- The authoritative design is `docs/superpowers/specs/2026-07-15-pre-trigger-append-only-candidate-range-design.md` at commit `0e40196a1affaa21d5b7b5c4639f942e48df1d38`.
- A candidate range contains one through five total unaccepted commits, including implementation, review fixes, documentation-only commits, reverts, and no-op commits.
- The candidate base is the unique commit that adds the route event named by the committed Director packet; no caller-supplied base or commit count is accepted.
- Candidate history is a strict linear fast-forward. Merge commits, side branches, amend, rebase, reset, replacement, shallow history, grafts, and missing required candidate objects fail closed.
- Candidate changes stay inside the packet's unchanged `scope_files`; rename endpoints and per-commit transient changes are included, while symlinks, gitlinks, and existing-file mode changes are rejected.
- The packet objective, acceptance, task identity, verification commands, and governed-side-effect policy stay unchanged throughout the candidate range.
- Mechanical validity does not certify that a range is tightly coupled. The Director records one semantic correction rationale, and the independent Operator may return NITS or FAIL when the commits contain multiple objectives.
- V1 preserves candidate SHAs named by relevant committed route/review mailbox evidence; it deliberately makes no claim about a local tip that was never committed into durable evidence.
- `governed_side_effects` is exactly `none`; this work adds no provider, receipt, lock, merge, push, spend, cursor, publication, or route-mutation authority.
- The descriptor commit is the freeze boundary. Its sole parent is the validated candidate head, and the canonical verify-request commit's sole parent is the descriptor commit.
- Post-freeze implementation changes require a fresh coordinator-mediated descriptor task identity and trigger generation; old descriptor and trigger artifacts remain immutable.
- Existing `lane-v-scope/v1` descriptors and shipping-commit triggers remain accepted exactly as before. Candidate-policy enforcement is opt-in through `lane-v-scope/v2` and applies only to canonical verify-request triggers.
- The current Stage A range `40fd0a5e43c6b28330ced9ddffe01483cde42b65..56091d107382abfe9f06df1aa4cd003d71be7b5e` remains unauthorized for a second commit until the coordinator lands the separate bounded correction described under “Stage A companion action.”
- Real Claude/Opus provider attempts remain zero throughout implementation and verification of this plan.
- The coordinator owns routing and reconciliation only. A Director or bounded implementer authors production/test changes; the paired Operator owns independent GO/NITS/FAIL.
- This implementation changes the candidate validator and authority schema, so its own route must not contain `candidate_policy`. The coordinator instead authorizes exactly four planned commits plus at most one separate reviewer-fix commit under the existing one-off range-review contract; a need for a second reviewer-fix commit returns to the coordinator.
- Do not merge or push before independent Operator GO. After GO, perform the local merge, verify the merged tree, and push only under a separately authorized side-effect executor token.

---

## Stage A companion action

This is a separate coordinator-owned metadata correction, not one of the four implementation commits below. It may land before this plan is implemented.

The correction changes exactly these existing artifacts plus one newly generated coordinator-to-all mailbox event:

- `docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md`
- `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-director2-diagnostics.json`
- `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-operator2-lanev.json`
- `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-coordinator-join.json`
- the canonical event path printed by `coordination/bin/send-event coordinator all coordination "authorize additive Stage A review fix"`

The correction must preserve base `40fd0a5e43c6b28330ced9ddffe01483cde42b65`, immutable first candidate `56091d107382abfe9f06df1aa4cd003d71be7b5e`, the original four implementation/test paths, descriptor task `b8c59c86-2426-46cf-8975-7b075d75fc09`, and zero provider attempts. It authorizes exactly one additive compatibility-fix commit that keeps public reason `process_failed`, failure stage `provider_spawn`, detail `binary_missing`, and `provider_returncode = null`; renewed spec and quality reviews must pass before descriptor and verify-request creation. The companion correction does not add `candidate_policy`, because the durable validator does not exist yet.

## Execution and ownership gate

The current root worktree has peer/user WIP on several later target files, including `AGENTS.md`, `ARCHITECTURE.md`, `scripts/codex_protocol_model.py`, `docs/protocol/codex/continuation.md`, the four `.agents/skills/seat-*` mirrors, and the three `.codex/agents/protocol-*` prompts. Do not start the durable implementation until each target path is either clean or its owner has committed and handed off the exact blob.

Run this read-only check from the primary checkout immediately before routing:

```bash
env -u GIT_INDEX_FILE git status --short -- \
  AGENTS.md CLAUDE.md ARCHITECTURE.md OPERATIONS.md \
  scripts/protocol_capacity.py scripts/protocol_capacity_board.py \
  scripts/opus_review_bridge.py scripts/opus_review_receipts.py \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  docs/protocol/agents/orchestration.md \
  docs/protocol/agents/director-operator.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/claude/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-operator/verification-report-format.md \
  .claude/skills/four-seat-protocol/SKILL.md \
  .claude/skills/seat-coordinator/SKILL.md \
  .claude/skills/seat-director/SKILL.md \
  .claude/skills/seat-operator/SKILL.md \
  .claude/skills/seat-operator/verification-report-format.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .claude/agents/lane-v-verifier.md
```

Expected: no output. If any path appears, stop and obtain an owner handoff; do not overwrite, stash, or auto-fix it.

After the coordinator commits a validated implementation route, invoke `superpowers:using-git-worktrees` and create the isolated worktree from that exact route commit:

```bash
ROUTE_BASE="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
env -u GIT_INDEX_FILE git worktree add \
  .worktrees/pre-trigger-append-only-candidate-range \
  -b codex/pre-trigger-append-only-candidate-range \
  "$ROUTE_BASE"
```

Expected: one new clean worktree at the route commit. All ordinary Git and pytest commands below retain `env -u GIT_INDEX_FILE`.

The route must bind a legacy `lane-v-scope/v1` descriptor for this implementation, because the implementation range changes `scripts/protocol_capacity.py`, `scripts/protocol_capacity_board.py`, `scripts/opus_review_bridge.py`, and `scripts/opus_review_receipts.py`. Once merged, future non-self-modifying routes may opt into `candidate_policy` and `lane-v-scope/v2`.

## File structure

### Executable contract

- Modify `scripts/protocol_capacity.py`: define and parse `CandidatePolicy`; validate route contradictions; derive and validate candidate ranges; expose one API used by CLI and Lane V.
- Modify `scripts/protocol_capacity_board.py`: add the paired `--validate-candidate` and `--candidate-head` interface and render JSON/text results.
- Modify `scripts/opus_review_receipts.py`: preserve v1 descriptors and add the exact v2 descriptor field set with `reviewed_head`.
- Modify `scripts/opus_review_bridge.py`: expose the existing trusted verification-command check, resolve v2 candidate packets, call the shared range validator, and enforce head→descriptor→request topology.

### Tests

- Modify `tests/unit/test_protocol_capacity.py`: packet schema, route contradiction, Git graph/range/path/evidence checks, CLI, and abuse cases 1–7 and 10–11.
- Modify `tests/unit/test_opus_review_receipts.py`: v1 compatibility and v2 exact-schema/head tests.
- Modify `tests/unit/test_opus_review_bridge.py`: v2 candidate descriptor resolution, freeze topology, mismatch rejection, and abuse cases 8–9.
- Modify `tests/unit/test_protocol_prompt_sync.py`: exact invariant fragments across producer, consumer, and coordinator mirrors.
- Modify `tests/unit/test_protocol_doc_integrity.py`: documented CLI and descriptor-version contract.

### Protocol mirrors

- Modify `scripts/codex_protocol_model.py`: add the canonical compact invariant tuple and renderer.
- Modify `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, and `OPERATIONS.md`: root rule, sibling tool mechanics, executable truth, and CLI operation.
- Modify `docs/protocol/agents/orchestration.md`, `docs/protocol/agents/director-operator.md`, `docs/protocol/codex/continuation.md`, and `docs/protocol/claude/continuation.md`: neutral lifecycle and provider-specific execution mechanics.
- Modify the matching `.agents/skills`, `.claude/skills`, `.codex/agents`, and `.claude/agents` files listed in the ownership gate: producer, consumer, coordinator, and Lane V prompt mirrors.

## Task 1: Parse candidate policy and reject route contradictions

**Files:**

- Modify: `scripts/protocol_capacity.py:127-181, 285-339, 461-530, 588-598, 1075-1125`
- Modify: `tests/unit/test_protocol_capacity.py:10-138, 434-516`

**Interfaces:**

- Consumes: existing `Packet`, `_parse_packet`, `validate_route`, `_issue`, and route-body validation.
- Produces: `CandidatePolicy`, `Packet.candidate_policy`, exact schema validation, and route gate `G11` for append-policy contradictions.

- [ ] **Step 1: Add failing candidate-policy tests**

Add these constants and helper beside `_packet`:

```python
CANDIDATE_TASK_ID = "11111111-2222-4333-8444-555555555555"
CANDIDATE_ROUTE = (
    "coordination/mailbox/sent/"
    "2026-07-15T16-00-00Z-coordinator-to-all-coordination.md"
)
CANDIDATE_COMMANDS = (
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
    "tests/unit/test_feature.py -q",
)


def _candidate_policy(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "history": "append-only-until-trigger",
        "route_event": CANDIDATE_ROUTE,
        "descriptor_task_id": CANDIDATE_TASK_ID,
        "max_commits": 5,
        "verification_commands": list(CANDIDATE_COMMANDS),
        "governed_side_effects": "none",
    }
    value.update(changes)
    return value
```

Add these tests:

```python
def test_candidate_policy_accepts_exact_contract(tmp_path: Path) -> None:
    packet = _packet(
        owner="director",
        packet_type="director-implementation",
    ) | {
        "candidate_policy": _candidate_policy(),
        "next_recipient": "operator",
        "allowed_paths": [
            "scripts/feature.py",
            "tests/unit/test_feature.py",
            f"coordination/verification/scopes/{CANDIDATE_TASK_ID}.json",
            "coordination/mailbox/sent/*director-to-operator-verify-request.md",
        ],
        "scope_files": ["scripts/feature.py", "tests/unit/test_feature.py"],
    }
    _write_packet(tmp_path, packet)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    parsed = next(item for item in report.packets if item.id == packet["id"])
    assert parsed.candidate_policy == protocol_capacity.CandidatePolicy(
        history="append-only-until-trigger",
        route_event=CANDIDATE_ROUTE,
        descriptor_task_id=CANDIDATE_TASK_ID,
        max_commits=5,
        verification_commands=CANDIDATE_COMMANDS,
        governed_side_effects="none",
    )
    assert not any(issue["gate"] == "SCHEMA" for issue in report.issues)


@pytest.mark.parametrize(
    "change",
    (
        {"history": "rewrite-until-trigger"},
        {"route_event": "docs/not-mail.md"},
        {"descriptor_task_id": "not-a-uuid"},
        {"max_commits": 4},
        {"max_commits": True},
        {"verification_commands": []},
        {"governed_side_effects": "provider"},
        {"unexpected": "field"},
    ),
)
def test_candidate_policy_rejects_noncanonical_contract(
    tmp_path: Path, change: dict[str, object]
) -> None:
    packet = _packet(
        owner="director",
        packet_type="director-implementation",
    ) | {
        "candidate_policy": _candidate_policy(**change),
        "scope_files": ["scripts/feature.py"],
    }
    _write_packet(tmp_path, packet)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    assert packet["id"] not in {item.id for item in report.packets}
    assert any(issue["gate"] == "SCHEMA" for issue in report.issues)


def test_route_rejects_append_policy_with_exact_one_shipping_commit(
    tmp_path: Path,
) -> None:
    _write_capacity_split_cycle(tmp_path)
    director = _packet(
        packet_id="director-capacity-split-chunk-a",
        owner="director",
        packet_type="director-implementation",
        cycle="capacity-split-cycle",
    ) | {
        "candidate_policy": _candidate_policy(),
        "next_recipient": "operator",
        "allowed_paths": [
            "scripts/feature.py",
            f"coordination/verification/scopes/{CANDIDATE_TASK_ID}.json",
            "coordination/mailbox/sent/*director-to-operator-verify-request.md",
        ],
        "scope_files": ["scripts/feature.py"],
        "acceptance": ["Stop after one shipping commit."],
    }
    _write_packet(tmp_path, director)
    route = _write_route(
        tmp_path,
        Path(CANDIDATE_ROUTE).name,
        _capacity_split_route_body(
            "## Capacity Split Default\n\n"
            "- single-pair fast path remains the default for narrow or shared-file work.\n"
            "- Pair B performs bounded planning or preflight.\n"
            "- Stop after exactly one implementation commit.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        issue["gate"] == "G11" and "exact-one" in issue["message"]
        for issue in result.route_issues
    )
```

- [ ] **Step 2: Run the focused tests and confirm failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'candidate_policy or exact_one_shipping_commit' -q
```

Expected: FAIL because `CandidatePolicy` and `Packet.candidate_policy` do not exist and route validation has no `G11` gate.

- [ ] **Step 3: Implement the exact policy schema**

Add these definitions above `Packet`:

```python
import uuid


CANDIDATE_POLICY_FIELDS = frozenset(
    {
        "history",
        "route_event",
        "descriptor_task_id",
        "max_commits",
        "verification_commands",
        "governed_side_effects",
    }
)
CANDIDATE_HISTORY = "append-only-until-trigger"
CANDIDATE_MAX_COMMITS = 5
CANDIDATE_GOVERNED_SIDE_EFFECTS = "none"
EXACT_ONE_CANDIDATE_RE = re.compile(
    r"\b(?:exactly\s+one|one)\s+"
    r"(?:(?:shipping|implementation|diagnostic|diagnostics|review-fix|review fix)\s+){1,3}"
    r"commit\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CandidatePolicy:
    history: str
    route_event: str
    descriptor_task_id: str
    max_commits: int
    verification_commands: tuple[str, ...]
    governed_side_effects: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "history": self.history,
            "route_event": self.route_event,
            "descriptor_task_id": self.descriptor_task_id,
            "max_commits": self.max_commits,
            "verification_commands": list(self.verification_commands),
            "governed_side_effects": self.governed_side_effects,
        }
```

Add `candidate_policy: CandidatePolicy | None` to `Packet`, serialize it from `Packet.to_dict`, and parse it with this helper:

```python
def _parse_candidate_policy(value: object) -> tuple[CandidatePolicy | None, list[str]]:
    if value is None:
        return None, []
    if not isinstance(value, dict) or set(value) != CANDIDATE_POLICY_FIELDS:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        return None, [
            "candidate_policy fields must be "
            f"{sorted(CANDIDATE_POLICY_FIELDS)!r}, got {actual!r}"
        ]
    issues: list[str] = []
    route_event = value["route_event"]
    task_id = value["descriptor_task_id"]
    commands = value["verification_commands"]
    if value["history"] != CANDIDATE_HISTORY:
        issues.append(f"candidate_policy.history must be {CANDIDATE_HISTORY!r}")
    if (
        not isinstance(route_event, str)
        or not route_event.startswith("coordination/mailbox/sent/")
        or "\\" in route_event
        or any(part in {"", ".", ".."} for part in route_event.split("/"))
        or Path(route_event).name != route_event.removeprefix(
            "coordination/mailbox/sent/"
        )
        or not route_event.endswith("-coordinator-to-all-coordination.md")
    ):
        issues.append("candidate_policy.route_event must be one canonical coordinator-to-all sent event")
    try:
        parsed_task = uuid.UUID(task_id) if isinstance(task_id, str) else None
    except ValueError:
        parsed_task = None
    if parsed_task is None or str(parsed_task) != task_id:
        issues.append("candidate_policy.descriptor_task_id must be canonical UUID text")
    if type(value["max_commits"]) is not int or value["max_commits"] != 5:
        issues.append("candidate_policy.max_commits must equal 5")
    if (
        not isinstance(commands, list)
        or not commands
        or len(commands) > 32
        or not all(isinstance(command, str) and command for command in commands)
        or len(set(commands)) != len(commands)
    ):
        issues.append("candidate_policy.verification_commands must contain 1-32 unique strings")
    if value["governed_side_effects"] != CANDIDATE_GOVERNED_SIDE_EFFECTS:
        issues.append("candidate_policy.governed_side_effects must be 'none'")
    if issues:
        return None, issues
    return CandidatePolicy(
        history=str(value["history"]),
        route_event=str(route_event),
        descriptor_task_id=str(task_id),
        max_commits=5,
        verification_commands=tuple(commands),
        governed_side_effects="none",
    ), []
```

In `_parse_packet`, add this block after validating `scope_files` and `next_recipient`, then pass `candidate_policy` to `Packet`:

```python
candidate_policy, candidate_issues = _parse_candidate_policy(
    data.get("candidate_policy")
)
local_issues.extend(candidate_issues)
scope_files = tuple(data.get("scope_files", []))
if candidate_policy is not None:
    if data.get("packet_type") != "director-implementation":
        local_issues.append(
            "candidate_policy is allowed only on director-implementation packets"
        )
    if not scope_files:
        local_issues.append("candidate_policy requires nonempty scope_files")
    allowed_paths = tuple(data.get("allowed_paths", []))
    for scope_file in scope_files:
        if not any(
            scope_file == allowed.rstrip("/")
            or scope_file.startswith(allowed.rstrip("/") + "/")
            for allowed in allowed_paths
            if not any(character in allowed for character in "*?[]")
        ):
            local_issues.append(
                f"candidate scope file is not covered by allowed_paths: {scope_file}"
            )
    descriptor_path = (
        "coordination/verification/scopes/"
        f"{candidate_policy.descriptor_task_id}.json"
    )
    if descriptor_path not in allowed_paths:
        local_issues.append(
            "candidate descriptor path must be present in allowed_paths"
        )
    verify_path = (
        "coordination/mailbox/sent/*"
        f"{data.get('owner')}-to-{next_recipient}-verify-request.md"
    )
    if verify_path not in allowed_paths:
        local_issues.append(
            "candidate verify-request glob must be present in allowed_paths"
        )
```

Append each parser message as `SCHEMA`. Serialize the optional policy from `Packet.to_dict()` without changing legacy packet output other than the new `candidate_policy: null` field.

Add this route check and call it from `_validate_route_file` after `_capacity_split_route_issues`:

```python
def _candidate_route_issues(
    body: str, path: Path, report: CapacityReport
) -> list[dict[str, Any]]:
    try:
        route = path.resolve().relative_to(Path(report.root).resolve()).as_posix()
    except ValueError:
        route = path.as_posix()
    issues: list[dict[str, Any]] = []
    for packet in report.packets:
        policy = packet.candidate_policy
        if policy is None or not packet.is_current or policy.route_event != route:
            continue
        conflict_text = "\n".join((*packet.acceptance, body))
        if EXACT_ONE_CANDIDATE_RE.search(conflict_text):
            issues.append(
                _issue(
                    "G11",
                    f"{packet.id}: append-only candidate policy conflicts with exact-one implementation history",
                    packet_ids=[packet.id],
                )
            )
    return issues
```

- [ ] **Step 4: Run focused and existing capacity tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py -q
```

Expected: all tests pass; packets without `candidate_policy` retain their current behavior.

- [ ] **Step 5: Commit Task 1**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/protocol_capacity.py tests/unit/test_protocol_capacity.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m \
  "feat(protocol): parse append-only candidate policy"
```

Expected: one commit changing only the two named paths.

## Task 2: Derive and validate candidate ranges from Git

**Files:**

- Modify: `scripts/protocol_capacity.py:1-15, 285-416, 1538-1579`
- Modify: `scripts/protocol_capacity_board.py:16-55`
- Modify: `tests/unit/test_protocol_capacity.py`

**Interfaces:**

- Consumes: `CandidatePolicy`, `Packet`, and `_parse_packet` from Task 1; a callback with signature `Callable[[Path, tuple[str, ...]], None]` for trusted command validation.
- Produces: `CandidateRangeValidation`, `validate_candidate(...)`, `validate_candidate_for_task(...)`, text/JSON renderers, and the CLI pair `--validate-candidate` plus `--candidate-head`.

- [ ] **Step 1: Add a real-Git candidate fixture and valid-range test**

Add imports `os`, `subprocess`, and `dataclass` to the test file, then add:

```python
@dataclass(frozen=True)
class _CandidateFixture:
    root: Path
    packet_path: str
    base: str
    heads: tuple[str, ...]


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", *args],
        cwd=root,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def _candidate_repo(
    root: Path,
    *,
    commit_count: int = 2,
    extra_scope: tuple[str, ...] = (),
) -> _CandidateFixture:
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Candidate Fixture")
    _git(root, "config", "user.email", "candidate@example.invalid")
    _git(root, "config", "core.filemode", "true")
    (root / "scripts").mkdir()
    (root / "tests/unit").mkdir(parents=True)
    (root / "scripts/feature.py").write_text("VALUE = 0\n", encoding="utf-8")
    (root / "tests/unit/test_feature.py").write_text(
        "def test_feature():\n    assert True\n", encoding="utf-8"
    )
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: seed")

    route = root / CANDIDATE_ROUTE
    route.parent.mkdir(parents=True)
    route.write_text(
        "# Coordinator → All: candidate route\n\n"
        "Event type: coordination\n"
        "Task-board: cycle-a\n"
        "Packet: director-candidate\n"
        "Candidate history: append-only-until-trigger\n",
        encoding="utf-8",
    )
    packet_path = (
        "coordination/capacity/packets/"
        "2026-07-15-candidate-director.json"
    )
    packet_file = root / packet_path
    packet_file.parent.mkdir(parents=True)
    packet = _packet(
        packet_id="director-candidate",
        owner="director",
        packet_type="director-implementation",
    ) | {
        "candidate_policy": _candidate_policy(),
        "next_recipient": "operator",
        "allowed_paths": [
            "scripts/feature.py",
            "tests/unit/test_feature.py",
            *extra_scope,
            f"coordination/verification/scopes/{CANDIDATE_TASK_ID}.json",
            "coordination/mailbox/sent/*director-to-operator-verify-request.md",
        ],
        "scope_files": [
            "scripts/feature.py",
            "tests/unit/test_feature.py",
            *extra_scope,
        ],
    }
    packet_file.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    _git(root, "add", CANDIDATE_ROUTE, packet_path)
    _git(root, "commit", "-q", "-m", "coord: route candidate")
    base = _git(root, "rev-parse", "HEAD")

    heads: list[str] = []
    for index in range(1, commit_count + 1):
        (root / "scripts/feature.py").write_text(
            f"VALUE = {index}\n", encoding="utf-8"
        )
        _git(root, "add", "scripts/feature.py")
        _git(root, "commit", "-q", "-m", f"fix: candidate {index}")
        heads.append(_git(root, "rev-parse", "HEAD"))
    return _CandidateFixture(root, packet_path, base, tuple(heads))


def _accept_candidate_commands(root: Path, commands: tuple[str, ...]) -> None:
    assert root.is_dir()
    assert commands == CANDIDATE_COMMANDS


def test_candidate_range_accepts_initial_commit_and_review_fix(
    tmp_path: Path,
) -> None:
    fixture = _candidate_repo(tmp_path / "repo", commit_count=2)

    result = protocol_capacity.validate_candidate(
        fixture.root,
        2,
        fixture.packet_path,
        fixture.heads[-1],
        command_validator=_accept_candidate_commands,
    )

    assert result.valid
    assert result.candidate_base == fixture.base
    assert result.candidate_head == fixture.heads[-1]
    assert result.commit_ids == fixture.heads
    assert result.changed_paths == ("scripts/feature.py",)
```

- [ ] **Step 2: Add the non-vacuous graph, path, evidence, and self-modification tests**

For each test, first call `validate_candidate` on the valid fixture and assert `valid`; mutate only the named dimension; then call it again and assert the specified gate:

```python
@pytest.mark.parametrize(
    ("case", "expected_gate"),
    (
        ("six-commits", "CANDIDATE_COUNT"),
        ("merge", "CANDIDATE_GRAPH"),
        ("forbidden-path", "CANDIDATE_PATH"),
        ("rename-outside", "CANDIDATE_PATH"),
        ("symlink", "CANDIDATE_MODE"),
        ("gitlink", "CANDIDATE_MODE"),
        ("mode-change", "CANDIDATE_MODE"),
        ("self-modifying-validator", "CANDIDATE_SELF_MODIFICATION"),
    ),
)
def test_candidate_range_rejects_one_mutated_dimension(
    tmp_path: Path, case: str, expected_gate: str
) -> None:
    extra_scope = {
        "symlink": ("scripts/link.py",),
        "gitlink": ("scripts/gitlink",),
        "self-modifying-validator": ("scripts/protocol_capacity.py",),
    }.get(case, ())
    fixture = _candidate_repo(
        tmp_path / case, commit_count=2, extra_scope=extra_scope
    )
    valid = protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, fixture.heads[-1],
        command_validator=_accept_candidate_commands,
    )
    assert valid.valid

    mutated_head = _mutate_candidate_fixture(fixture, case)
    rejected = protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, mutated_head,
        command_validator=_accept_candidate_commands,
    )

    assert not rejected.valid
    assert any(issue["gate"] == expected_gate for issue in rejected.issues)
```

Add this helper, which performs exactly one mutation after the valid assertion:

```python
def _mutate_candidate_fixture(
    fixture: _CandidateFixture, case: str
) -> str:
    root = fixture.root
    if case == "six-commits":
        for index in range(3, 7):
            (root / "scripts/feature.py").write_text(
                f"VALUE = {index}\n", encoding="utf-8"
            )
            _git(root, "add", "scripts/feature.py")
            _git(root, "commit", "-q", "-m", f"fix: candidate {index}")
    elif case == "merge":
        _git(root, "switch", "-q", "-c", "candidate-side", fixture.heads[0])
        (root / "tests/unit/test_feature.py").write_text(
            "def test_feature():\n    assert 1 + 1 == 2\n", encoding="utf-8"
        )
        _git(root, "add", "tests/unit/test_feature.py")
        _git(root, "commit", "-q", "-m", "test: side candidate")
        _git(root, "switch", "-q", "-")
        _git(root, "merge", "-q", "--no-ff", "candidate-side", "-m", "merge candidate side")
    elif case == "forbidden-path":
        (root / "outside.txt").write_text("outside\n", encoding="utf-8")
        _git(root, "add", "outside.txt")
        _git(root, "commit", "-q", "-m", "fix: outside path")
    elif case == "rename-outside":
        _git(root, "mv", "scripts/feature.py", "outside.py")
        _git(root, "commit", "-q", "-m", "refactor: rename outside scope")
    elif case == "symlink":
        (root / "scripts/link.py").symlink_to("feature.py")
        _git(root, "add", "scripts/link.py")
        _git(root, "commit", "-q", "-m", "fix: add symlink")
    elif case == "gitlink":
        current = _git(root, "rev-parse", "HEAD")
        _git(
            root,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{current},scripts/gitlink",
        )
        _git(root, "commit", "-q", "-m", "fix: add gitlink")
    elif case == "mode-change":
        (root / "scripts/feature.py").chmod(0o755)
        _git(root, "add", "scripts/feature.py")
        _git(root, "commit", "-q", "-m", "fix: change mode")
    elif case == "self-modifying-validator":
        (root / "scripts/protocol_capacity.py").write_text(
            "# candidate self-modification\n", encoding="utf-8"
        )
        _git(root, "add", "scripts/protocol_capacity.py")
        _git(root, "commit", "-q", "-m", "fix: alter candidate validator")
    else:
        raise AssertionError(case)
    return _git(root, "rev-parse", "HEAD")
```

The mutations prove these exact conditions:

- `six-commits`: append four regular commits to the existing two-commit range.
- `merge`: branch from the first candidate, commit an allowed-path change, return to the second candidate, and merge with `--no-ff`.
- `forbidden-path`: add and commit `outside.txt`.
- `rename-outside`: rename the allowed `scripts/feature.py` endpoint to forbidden `outside.py`.
- `symlink`: create `scripts/link.py -> feature.py`, include it in the packet scope at the base, and commit it.
- `gitlink`: run `git update-index --add --cacheinfo 160000,<current-head>,scripts/gitlink` in a fixture whose base packet includes `scripts/gitlink`, then commit.
- `mode-change`: `chmod 0755 scripts/feature.py`, add, and commit.
- `self-modifying-validator`: add `scripts/protocol_capacity.py` to the base packet scope, then change and commit that path; the protected-path gate must reject even though the path is allowlisted.

Add two dedicated evidence tests:

```python
def test_candidate_range_rejects_amended_head_named_by_committed_evidence(
    tmp_path: Path,
) -> None:
    fixture = _candidate_repo(tmp_path / "repo", commit_count=1)
    original = fixture.heads[0]
    evidence_branch = _git(fixture.root, "branch", "evidence", original)
    assert evidence_branch == ""
    evidence_path = (
        "coordination/mailbox/sent/"
        "2026-07-15T16-05-00Z-director-to-coordinator-coordination.md"
    )
    evidence_file = fixture.root / evidence_path
    evidence_file.write_text(
        "Task-board: cycle-a\n"
        "Packet: director-candidate\n"
        f"Reviewed head: {original}\n",
        encoding="utf-8",
    )
    _git(fixture.root, "add", evidence_path)
    _git(fixture.root, "commit", "-q", "-m", "coord: preserve candidate evidence")
    _git(fixture.root, "branch", "-f", "evidence", "HEAD")
    _git(fixture.root, "reset", "-q", "--hard", fixture.base)
    (fixture.root / "scripts/feature.py").write_text("VALUE = 99\n", encoding="utf-8")
    _git(fixture.root, "add", "scripts/feature.py")
    _git(fixture.root, "commit", "-q", "-m", "fix: replacement candidate")
    replacement = _git(fixture.root, "rev-parse", "HEAD")

    result = protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, replacement,
        command_validator=_accept_candidate_commands,
    )

    assert not result.valid
    assert any(issue["gate"] == "CANDIDATE_EVIDENCE" for issue in result.issues)


def test_candidate_range_rejects_sliding_base_to_unaccepted_intermediate(
    tmp_path: Path,
) -> None:
    fixture = _candidate_repo(tmp_path / "repo", commit_count=5)
    assert protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, fixture.heads[-1],
        command_validator=_accept_candidate_commands,
    ).valid
    second_route = (
        "coordination/mailbox/sent/"
        "2026-07-15T16-10-00Z-coordinator-to-all-coordination.md"
    )
    _rewrite_candidate_packet_route(
        fixture.root, fixture.packet_path, second_route
    )
    _git(fixture.root, "add", fixture.packet_path, second_route)
    _git(fixture.root, "commit", "-q", "-m", "coord: attempt sliding base")
    (fixture.root / "scripts/feature.py").write_text("VALUE = 6\n", encoding="utf-8")
    _git(fixture.root, "add", "scripts/feature.py")
    _git(fixture.root, "commit", "-q", "-m", "fix: hidden sixth commit")
    head = _git(fixture.root, "rev-parse", "HEAD")

    result = protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, head,
        command_validator=_accept_candidate_commands,
    )

    assert not result.valid
    assert any(
        issue["gate"] in {"CANDIDATE_PACKET", "CANDIDATE_EVIDENCE"}
        for issue in result.issues
    )
```

Add the concrete route-rewrite helper:

```python
def _rewrite_candidate_packet_route(
    root: Path, packet_path: str, second_route: str
) -> None:
    route_file = root / second_route
    route_file.parent.mkdir(parents=True, exist_ok=True)
    route_file.write_text(
        "# Coordinator → All: attempted sliding route\n\n"
        "Event type: coordination\n"
        "Task-board: cycle-a\n"
        "Packet: director-candidate\n",
        encoding="utf-8",
    )
    packet_file = root / packet_path
    packet = json.loads(packet_file.read_text(encoding="utf-8"))
    packet["candidate_policy"]["route_event"] = second_route
    packet_file.write_text(
        json.dumps(packet, indent=2) + "\n", encoding="utf-8"
    )
```

This proves the validator does not accept a later route as a sliding reviewed base.

Add one parameterized packet-drift test:

```python
@pytest.mark.parametrize(
    "field",
    ("acceptance", "verification_commands", "descriptor_task_id", "governed_side_effects"),
)
def test_candidate_range_rejects_packet_contract_drift(
    tmp_path: Path, field: str
) -> None:
    fixture = _candidate_repo(tmp_path / field, commit_count=2)
    assert protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, fixture.heads[-1],
        command_validator=_accept_candidate_commands,
    ).valid
    packet_file = fixture.root / fixture.packet_path
    packet = json.loads(packet_file.read_text(encoding="utf-8"))
    if field == "acceptance":
        packet["acceptance"].append("A second semantic objective.")
    elif field == "verification_commands":
        packet["candidate_policy"][field] = list(reversed(CANDIDATE_COMMANDS))
    elif field == "descriptor_task_id":
        packet["candidate_policy"][field] = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    else:
        packet["candidate_policy"][field] = "provider"
    packet_file.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    _git(fixture.root, "add", fixture.packet_path)
    _git(fixture.root, "commit", "-q", "-m", f"coord: drift {field}")
    head = _git(fixture.root, "rev-parse", "HEAD")

    result = protocol_capacity.validate_candidate(
        fixture.root, 2, fixture.packet_path, head,
        command_validator=_accept_candidate_commands,
    )

    assert not result.valid
    assert any(
        issue["gate"] in {"CANDIDATE_PACKET", "CANDIDATE_PATH", "SCHEMA"}
        for issue in result.issues
    )
```

This proves a changed objective, command contract, task identity, or side-effect policy cannot create an autonomous correction.

- [ ] **Step 3: Run the new tests and confirm failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'candidate_range' -q
```

Expected: FAIL because `validate_candidate`, range result types, Git derivation, and mutation helpers are not implemented.

- [ ] **Step 4: Implement the candidate result and secure Git launcher**

Add imports `os`, `subprocess`, `PurePosixPath`, and `Callable`. Add these definitions after `RouteValidation`:

```python
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CANDIDATE_PROTECTED_PATHS = frozenset(
    {
        "scripts/protocol_capacity.py",
        "scripts/protocol_capacity_board.py",
        "scripts/opus_review_bridge.py",
        "scripts/opus_review_receipts.py",
    }
)
VerificationCommandValidator = Callable[[Path, tuple[str, ...]], None]


@dataclass(frozen=True)
class CandidateRangeValidation:
    root: str
    wave: int
    packet_path: str
    packet: Packet | None
    candidate_base: str | None
    candidate_head: str
    commit_ids: tuple[str, ...]
    changed_paths: tuple[str, ...]
    issues: tuple[dict[str, Any], ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_kind": "protocol-candidate-range-validation",
            "valid": self.valid,
            "wave": self.wave,
            "packet_path": self.packet_path,
            "packet": self.packet.to_dict() if self.packet is not None else None,
            "candidate_base": self.candidate_base,
            "candidate_head": self.candidate_head,
            "commit_ids": list(self.commit_ids),
            "commit_count": len(self.commit_ids),
            "changed_paths": list(self.changed_paths),
            "issues": list(self.issues),
        }


def _git_process(
    root: Path, *args: str, text: bool = True
) -> subprocess.CompletedProcess[Any]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    return subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", *args],
        cwd=root,
        env=environment,
        capture_output=True,
        text=text,
        check=False,
    )
```

- [ ] **Step 5: Implement one reusable range validator**

Implement these private helpers in `scripts/protocol_capacity.py`:

```python
_RAW_CHANGE_RE = re.compile(
    rb"^:([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([A-Z][0-9]*)$"
)
_EVIDENCE_SHA_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")


def _duplicate_checked_packet_object(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate key: {key}")
        value[key] = item
    return value


def _committed_packet(
    root: Path, revision: str, packet_path: str
) -> tuple[Packet | None, bytes | None, list[dict[str, Any]]]:
    shown = _git_process(root, "show", f"{revision}:{packet_path}", text=False)
    if shown.returncode != 0 or not isinstance(shown.stdout, bytes):
        return None, None, [
            _issue("CANDIDATE_PACKET", f"committed packet is missing at {revision}")
        ]
    raw = shown.stdout
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_duplicate_checked_packet_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError(f"invalid constant: {item}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return None, raw, [
            _issue("CANDIDATE_PACKET", f"committed packet is invalid JSON: {exc}")
        ]
    if not isinstance(value, dict):
        return None, raw, [
            _issue("CANDIDATE_PACKET", "committed packet is not an object")
        ]
    parse_issues: list[dict[str, Any]] = []
    packet = _parse_packet(Path(packet_path), value, parse_issues)
    return packet, raw, parse_issues


def _git_blob_oid(root: Path, revision: str, path: str) -> str | None:
    resolved = _git_process(root, "rev-parse", f"{revision}:{path}")
    value = resolved.stdout.strip() if resolved.returncode == 0 else ""
    return value if FULL_SHA_RE.fullmatch(value) else None


def _history_completeness_issues(root: Path) -> list[dict[str, Any]]:
    shallow = _git_process(root, "rev-parse", "--is-shallow-repository")
    issues: list[dict[str, Any]] = []
    if shallow.returncode != 0 or shallow.stdout.strip() != "false":
        issues.append(_issue("CANDIDATE_GRAPH", "candidate history is shallow or unreadable"))
    graft_path = _git_process(root, "rev-parse", "--git-path", "info/grafts")
    if graft_path.returncode != 0:
        issues.append(_issue("CANDIDATE_GRAPH", "could not resolve Git graft path"))
    else:
        path = Path(graft_path.stdout.strip())
        if not path.is_absolute():
            path = root / path
        try:
            grafted = path.is_file() and bool(path.read_bytes().strip())
        except OSError:
            grafted = True
        if grafted:
            issues.append(_issue("CANDIDATE_GRAPH", "Git graft history is not accepted"))
    return issues


def _derive_candidate_base(
    root: Path, head: str, route_event: str
) -> tuple[str | None, list[dict[str, Any]]]:
    result = _git_process(
        root,
        "log",
        "--format=%H",
        "--diff-filter=A",
        "--reverse",
        head,
        "--",
        route_event,
    )
    additions = tuple(line for line in result.stdout.splitlines() if line)
    if result.returncode != 0 or len(additions) != 1:
        return None, [
            _issue(
                "CANDIDATE_BASE",
                "route event must have one addition commit reachable from candidate head",
            )
        ]
    base = additions[0]
    base_blob = _git_blob_oid(root, base, route_event)
    head_blob = _git_blob_oid(root, head, route_event)
    if base_blob is None or head_blob is None or base_blob != head_blob:
        return None, [
            _issue("CANDIDATE_BASE", "route event changed after candidate-base publication")
        ]
    return base, []


def _candidate_route_binding_issues(
    root: Path, base: str, packet: Packet
) -> list[dict[str, Any]]:
    policy = packet.candidate_policy
    assert policy is not None
    shown = _git_process(root, "show", f"{base}:{policy.route_event}")
    if shown.returncode != 0:
        return [_issue("CANDIDATE_BASE", "could not read committed candidate route")]
    issues: list[dict[str, Any]] = []
    if f"Task-board: {packet.cycle}" not in shown.stdout or packet.id not in shown.stdout:
        issues.append(
            _issue("CANDIDATE_BASE", "candidate route does not bind packet cycle and id")
        )
    if EXACT_ONE_CANDIDATE_RE.search("\n".join((*packet.acceptance, shown.stdout))):
        issues.append(
            _issue("CANDIDATE_CONTRACT", "candidate route retains an exact-one implementation clause")
        )
    return issues


def _linear_candidate_commits(
    root: Path, base: str, head: str, maximum: int
) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    ancestor = _git_process(root, "merge-base", "--is-ancestor", base, head)
    if ancestor.returncode != 0:
        return (), [
            _issue("CANDIDATE_GRAPH", "candidate base is not an ancestor of candidate head")
        ]
    listed = _git_process(root, "rev-list", "--reverse", f"{base}..{head}")
    commits = tuple(line for line in listed.stdout.splitlines() if line)
    issues: list[dict[str, Any]] = []
    if listed.returncode != 0:
        issues.append(_issue("CANDIDATE_GRAPH", "could not enumerate candidate range"))
        return (), issues
    if not 1 <= len(commits) <= maximum:
        issues.append(
            _issue(
                "CANDIDATE_COUNT",
                f"candidate range contains {len(commits)} commits; expected 1-{maximum}",
            )
        )
    expected_parent = base
    for commit in commits:
        parents = _git_process(root, "rev-list", "--parents", "-n", "1", commit)
        fields = parents.stdout.split()
        if (
            parents.returncode != 0
            or len(fields) != 2
            or fields[0] != commit
            or fields[1] != expected_parent
        ):
            issues.append(
                _issue(
                    "CANDIDATE_GRAPH",
                    f"candidate commit is not a one-parent linear append: {commit}",
                )
            )
        expected_parent = commit
    return commits, issues


def _path_in_candidate_scope(path: str, roots: tuple[str, ...]) -> bool:
    return any(
        path == root.rstrip("/") or path.startswith(root.rstrip("/") + "/")
        for root in roots
    )


def _raw_commit_changes(
    root: Path, parent: str, commit: str
) -> tuple[tuple[tuple[str, str, str, str], ...], list[dict[str, Any]]]:
    result = _git_process(
        root,
        "diff-tree",
        "--no-commit-id",
        "-r",
        "--raw",
        "-z",
        "--no-renames",
        parent,
        commit,
        "--",
        text=False,
    )
    if result.returncode != 0 or not isinstance(result.stdout, bytes):
        return (), [_issue("CANDIDATE_PATH", f"could not read changes for {commit}")]
    chunks = result.stdout.split(b"\0")
    if chunks and chunks[-1] == b"":
        chunks.pop()
    if len(chunks) % 2:
        return (), [_issue("CANDIDATE_PATH", f"malformed raw diff for {commit}")]
    changes: list[tuple[str, str, str, str]] = []
    issues: list[dict[str, Any]] = []
    for index in range(0, len(chunks), 2):
        metadata = _RAW_CHANGE_RE.fullmatch(chunks[index])
        try:
            path = chunks[index + 1].decode("utf-8")
        except UnicodeDecodeError:
            metadata = None
            path = "<non-utf8>"
        if metadata is None:
            issues.append(_issue("CANDIDATE_PATH", f"malformed raw change at {commit}"))
            continue
        old_mode, new_mode, _old_oid, _new_oid, status = metadata.groups()
        changes.append(
            (
                status.decode("ascii"),
                path,
                old_mode.decode("ascii"),
                new_mode.decode("ascii"),
            )
        )
    return tuple(changes), issues


def _candidate_changes(
    root: Path, base: str, commits: tuple[str, ...], scope_files: tuple[str, ...]
) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    if (
        not scope_files
        or len(set(scope_files)) != len(scope_files)
        or any(
            not path
            or path.startswith("/")
            or path.endswith("/")
            or "\\" in path
            or any(part in {"", ".", ".."} for part in path.split("/"))
            or any(character in path for character in "*?[]")
            for path in scope_files
        )
    ):
        return (), [_issue("CANDIDATE_PACKET", "scope_files is not an exact path allowlist")]
    paths: set[str] = set()
    parent = base
    for commit in commits:
        changes, change_issues = _raw_commit_changes(root, parent, commit)
        issues.extend(change_issues)
        for _status, path, old_mode, new_mode in changes:
            paths.add(path)
            if not _path_in_candidate_scope(path, scope_files):
                issues.append(
                    _issue("CANDIDATE_PATH", f"candidate path is outside scope_files: {path}", paths=[path])
                )
            if path in CANDIDATE_PROTECTED_PATHS:
                issues.append(
                    _issue(
                        "CANDIDATE_SELF_MODIFICATION",
                        f"candidate changes its own enforcement surface: {path}",
                        paths=[path],
                    )
                )
            if old_mode in {"120000", "160000"} or new_mode in {"120000", "160000"}:
                issues.append(
                    _issue("CANDIDATE_MODE", f"symlink or gitlink is not accepted: {path}", paths=[path])
                )
            if (
                old_mode != "000000"
                and new_mode != "000000"
                and old_mode != new_mode
            ):
                issues.append(
                    _issue("CANDIDATE_MODE", f"existing-file mode changed: {path}", paths=[path])
                )
        parent = commit
    return tuple(sorted(paths)), issues


def _candidate_evidence_issues(
    root: Path, packet: Packet, base: str, commits: tuple[str, ...]
) -> list[dict[str, Any]]:
    policy = packet.candidate_policy
    assert policy is not None
    markers = (packet.id, packet.cycle, policy.descriptor_task_id)
    evidence_commits: set[str] = set()
    for marker in markers:
        result = _git_process(
            root,
            "log",
            "--all",
            "--format=%H",
            "-G",
            re.escape(marker),
            "--",
            "coordination/mailbox/sent",
        )
        if result.returncode != 0:
            return [_issue("CANDIDATE_EVIDENCE", "could not inspect committed candidate evidence")]
        evidence_commits.update(result.stdout.splitlines())
    named: set[str] = set()
    for evidence_commit in evidence_commits:
        changed = _git_process(
            root,
            "diff-tree",
            "--no-commit-id",
            "-r",
            "--name-only",
            "-z",
            evidence_commit,
            "--",
            "coordination/mailbox/sent",
            text=False,
        )
        if changed.returncode != 0 or not isinstance(changed.stdout, bytes):
            return [_issue("CANDIDATE_EVIDENCE", "could not read candidate evidence paths")]
        for encoded in filter(None, changed.stdout.split(b"\0")):
            try:
                path = encoded.decode("utf-8")
            except UnicodeDecodeError:
                continue
            shown = _git_process(root, "show", f"{evidence_commit}:{path}")
            if shown.returncode != 0 or not any(marker in shown.stdout for marker in markers):
                continue
            named.update(_EVIDENCE_SHA_RE.findall(shown.stdout))
    allowed = {base, *commits}
    issues: list[dict[str, Any]] = []
    for revision in sorted(named):
        exists = _git_process(root, "cat-file", "-e", f"{revision}^{{commit}}")
        if exists.returncode != 0:
            continue
        descends = _git_process(root, "merge-base", "--is-ancestor", base, revision)
        if descends.returncode == 0 and revision not in allowed:
            issues.append(
                _issue(
                    "CANDIDATE_EVIDENCE",
                    f"committed evidence names a candidate omitted from the final range: {revision}",
                )
            )
    return issues


def _pre_freeze_issues(
    root: Path, head: str, policy: CandidatePolicy
) -> list[dict[str, Any]]:
    descriptor_path = (
        "coordination/verification/scopes/"
        f"{policy.descriptor_task_id}.json"
    )
    descriptor = _git_process(root, "cat-file", "-e", f"{head}:{descriptor_path}")
    issues: list[dict[str, Any]] = []
    if descriptor.returncode == 0:
        issues.append(_issue("CANDIDATE_FROZEN", "candidate descriptor already exists at candidate head"))
    listed = _git_process(
        root,
        "ls-tree",
        "-r",
        "--name-only",
        "-z",
        head,
        "--",
        "coordination/mailbox/sent",
        text=False,
    )
    if listed.returncode != 0 or not isinstance(listed.stdout, bytes):
        return [*issues, _issue("CANDIDATE_FROZEN", "could not inspect candidate mailbox tree")]
    for encoded in filter(None, listed.stdout.split(b"\0")):
        try:
            path = encoded.decode("utf-8")
        except UnicodeDecodeError:
            continue
        shown = _git_process(root, "show", f"{head}:{path}")
        if (
            shown.returncode == 0
            and "Event type: verify-request" in shown.stdout
            and f"Lane-V-Scope: {descriptor_path}@sha256:" in shown.stdout
        ):
            issues.append(_issue("CANDIDATE_FROZEN", f"candidate verify-request already exists: {path}"))
    return issues
```

Use `/usr/bin/git --no-replace-objects` for every Git read. Reject `rev-parse --is-shallow-repository == true`, a nonempty `info/grafts`, any non-full input SHA, a missing object, route or packet blob drift between base and head, a packet whose `wave` differs, and a command-validator exception. Parse raw diffs with UTF-8 strict decoding; `--no-renames` makes both rename endpoints visible. Reject modes `120000` and `160000`, any existing-path `old_mode != new_mode`, and every changed path outside `scope_files`. Reject a protected path even when it is allowlisted.

Add the public entrypoint:

```python
def validate_candidate(
    root: Path | str,
    wave: int,
    packet_path: Path | str,
    candidate_head: str,
    *,
    command_validator: VerificationCommandValidator,
) -> CandidateRangeValidation:
    root_path = Path(root).resolve()
    packet_posix = Path(packet_path).as_posix()
    issues: list[dict[str, Any]] = []
    packet: Packet | None = None
    base: str | None = None
    commits: tuple[str, ...] = ()
    changed_paths: tuple[str, ...] = ()
    if FULL_SHA_RE.fullmatch(candidate_head) is None:
        issues.append(_issue("CANDIDATE_HEAD", "candidate head must be one lowercase full SHA"))
    if not (
        packet_posix.startswith("coordination/capacity/packets/")
        and PurePosixPath(packet_posix).name.endswith(".json")
        and ".." not in PurePosixPath(packet_posix).parts
    ):
        issues.append(_issue("CANDIDATE_PACKET", "packet path must be one canonical capacity-packet JSON path"))
    if issues:
        return CandidateRangeValidation(
            str(root_path), wave, packet_posix, None, None,
            candidate_head, (), (), tuple(issues)
        )
    issues.extend(_history_completeness_issues(root_path))
    packet, packet_raw, packet_issues = _committed_packet(
        root_path, candidate_head, packet_posix
    )
    issues.extend(packet_issues)
    if packet is not None:
        policy = packet.candidate_policy
        if packet.wave != wave:
            issues.append(_issue("CANDIDATE_PACKET", "packet wave does not agree"))
        if packet.packet_type != "director-implementation" or policy is None:
            issues.append(_issue("CANDIDATE_PACKET", "packet does not authorize append-only candidate history"))
        if policy is not None:
            try:
                command_validator(root_path, policy.verification_commands)
            except Exception as exc:
                issues.append(_issue("CANDIDATE_COMMAND", f"verification command rejected: {exc}"))
            base, base_issues = _derive_candidate_base(
                root_path, candidate_head, policy.route_event
            )
            issues.extend(base_issues)
            if base is not None:
                issues.extend(_candidate_route_binding_issues(root_path, base, packet))
                base_packet, base_raw, base_packet_issues = _committed_packet(
                    root_path, base, packet_posix
                )
                issues.extend(base_packet_issues)
                if base_packet is None or base_raw != packet_raw:
                    issues.append(_issue("CANDIDATE_PACKET", "candidate packet changed after route publication"))
                commits, graph_issues = _linear_candidate_commits(
                    root_path, base, candidate_head, policy.max_commits
                )
                issues.extend(graph_issues)
                changed_paths, change_issues = _candidate_changes(
                    root_path, base, commits, packet.scope_files
                )
                issues.extend(change_issues)
                issues.extend(_candidate_evidence_issues(root_path, packet, base, commits))
                issues.extend(_pre_freeze_issues(root_path, candidate_head, policy))
    return CandidateRangeValidation(
        str(root_path), wave, packet_posix, packet, base,
        candidate_head, commits, changed_paths, tuple(issues)
    )
```

Add the task-identity entrypoint used by Lane V:

```python
def validate_candidate_for_task(
    root: Path | str,
    candidate_head: str,
    descriptor_task_id: str,
    *,
    command_validator: VerificationCommandValidator,
) -> CandidateRangeValidation:
    root_path = Path(root).resolve()
    listed = _git_process(
        root_path,
        "ls-tree",
        "-r",
        "--name-only",
        "-z",
        candidate_head,
        "--",
        "coordination/capacity/packets",
        text=False,
    )
    matches: list[Packet] = []
    if listed.returncode == 0 and isinstance(listed.stdout, bytes):
        for encoded in filter(None, listed.stdout.split(b"\0")):
            try:
                packet_path = encoded.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if not packet_path.endswith(".json"):
                continue
            shown = _git_process(
                root_path, "show", f"{candidate_head}:{packet_path}", text=False
            )
            if (
                shown.returncode != 0
                or not isinstance(shown.stdout, bytes)
                or descriptor_task_id.encode("utf-8") not in shown.stdout
            ):
                continue
            packet, _raw, _issues = _committed_packet(
                root_path, candidate_head, packet_path
            )
            if (
                packet is not None
                and packet.candidate_policy is not None
                and packet.candidate_policy.descriptor_task_id == descriptor_task_id
            ):
                matches.append(packet)
    if len(matches) != 1:
        return CandidateRangeValidation(
            root=str(root_path),
            wave=0,
            packet_path="",
            packet=None,
            candidate_base=None,
            candidate_head=candidate_head,
            commit_ids=(),
            changed_paths=(),
            issues=(
                _issue(
                    "CANDIDATE_PACKET",
                    f"descriptor task matches {len(matches)} candidate packets; expected one",
                ),
            ),
        )
    packet = matches[0]
    return validate_candidate(
        root_path,
        packet.wave,
        packet.path,
        candidate_head,
        command_validator=command_validator,
    )
```

- [ ] **Step 6: Add the candidate CLI without a second validator**

In `scripts/protocol_capacity_board.py`, add:

```python
parser.add_argument(
    "--validate-candidate",
    default=None,
    help="committed director capacity-packet JSON to validate",
)
parser.add_argument(
    "--candidate-head",
    default=None,
    help="lowercase full candidate HEAD; required with --validate-candidate",
)
```

Reject `--validate-route` together with `--validate-candidate`, and reject either candidate argument without the other via `parser.error`. Lazily import `opus_review_bridge` only inside the candidate branch, then call:

```python
result = protocol_capacity.validate_candidate(
    Path(args.root),
    args.wave,
    Path(args.validate_candidate),
    args.candidate_head,
    command_validator=opus_review_bridge.validate_verification_commands,
)
```

Render JSON with `result.to_dict()`. Add this text renderer to `protocol_capacity.py` and exit zero only when `result.valid`:

```python
def render_candidate_validation(result: CandidateRangeValidation) -> str:
    lines = [
        "# Protocol Candidate Range Validation",
        f"packet: {result.packet_path}",
        f"candidate valid: {str(result.valid).lower()}",
        f"candidate base: {result.candidate_base or '-'}",
        f"candidate head: {result.candidate_head}",
        f"commit count: {len(result.commit_ids)}",
        "commits: " + (", ".join(result.commit_ids) or "-"),
        "changed paths: " + (", ".join(result.changed_paths) or "-"),
        "",
        "BLOCKING ISSUES",
    ]
    if result.issues:
        lines.extend(
            f"- {issue['gate']}: {issue['message']}" for issue in result.issues
        )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
```

Import `protocol_capacity_board` and add this CLI test:

```python
def test_candidate_cli_reports_derived_range_and_rejects_abbreviated_head(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = _candidate_repo(tmp_path / "repo", commit_count=2)
    valid_exit = protocol_capacity_board.main(
        [
            "--root", str(fixture.root),
            "--wave", "2",
            "--validate-candidate", fixture.packet_path,
            "--candidate-head", fixture.heads[-1],
            "--json",
        ]
    )
    valid = json.loads(capsys.readouterr().out)

    assert valid_exit == 0
    assert valid["candidate_base"] == fixture.base
    assert valid["commit_count"] == 2

    invalid_exit = protocol_capacity_board.main(
        [
            "--root", str(fixture.root),
            "--wave", "2",
            "--validate-candidate", fixture.packet_path,
            "--candidate-head", fixture.heads[-1][:12],
            "--json",
        ]
    )
    invalid = json.loads(capsys.readouterr().out)

    assert invalid_exit == 1
    assert any(issue["gate"] == "CANDIDATE_HEAD" for issue in invalid["issues"])
```

- [ ] **Step 7: Run Task 2 tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
  --wave 2 --json >/tmp/pre-trigger-capacity-board.json
```

Expected: all capacity tests pass; the existing board command exits zero and emits valid JSON without requiring a candidate policy on legacy packets.

- [ ] **Step 8: Commit Task 2**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/protocol_capacity.py \
  scripts/protocol_capacity_board.py \
  tests/unit/test_protocol_capacity.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m \
  "feat(protocol): validate append-only candidate ranges"
```

Expected: one commit changing only the three named paths.

## Task 3: Bind the candidate contract into Lane V

**Files:**

- Modify: `scripts/opus_review_receipts.py:20-80, 665-729`
- Modify: `scripts/opus_review_bridge.py:876-943, 1001-1033, 1538-1707`
- Modify: `tests/unit/test_opus_review_receipts.py:55-370`
- Modify: `tests/unit/test_opus_review_bridge.py:1168-1735`

**Interfaces:**

- Consumes: `protocol_capacity.validate_candidate_for_task` and `CandidateRangeValidation` from Task 2.
- Produces: `CANDIDATE_SCOPE_DESCRIPTOR_SCHEMA_VERSION`, `ScopeDescriptor.schema_version`, `ScopeDescriptor.reviewed_head`, public `validate_verification_commands`, and v2 resolver enforcement.

- [ ] **Step 1: Add v1 compatibility and v2 descriptor tests**

Keep `_descriptor_mapping()` as the v1 fixture. Add:

```python
def _candidate_descriptor_mapping() -> dict[str, object]:
    return _descriptor_mapping() | {
        "schema_version": "lane-v-scope/v2",
        "trigger_kind": "verify-request",
        "reviewed_head": "c" * 40,
    }


def test_scope_descriptor_v1_remains_backward_compatible() -> None:
    descriptor = receipts.ScopeDescriptor.from_mapping(_descriptor_mapping())

    assert descriptor.schema_version == "lane-v-scope/v1"
    assert descriptor.reviewed_head is None


def test_candidate_scope_descriptor_binds_exact_reviewed_head() -> None:
    descriptor = receipts.ScopeDescriptor.from_mapping(
        _candidate_descriptor_mapping()
    )

    assert descriptor.schema_version == "lane-v-scope/v2"
    assert descriptor.reviewed_head == "c" * 40
    assert descriptor.trigger_kind == "verify-request"


@pytest.mark.parametrize(
    "mutation",
    (
        {"reviewed_head": None},
        {"reviewed_head": "c" * 12},
        {"trigger_kind": "shipping-commit"},
        {"unexpected": "field"},
    ),
)
def test_candidate_scope_descriptor_rejects_invalid_contract(
    mutation: dict[str, object],
) -> None:
    value = _candidate_descriptor_mapping()
    value.update(mutation)

    with pytest.raises(
        receipts.ReceiptContractError, match="invalid_scope_descriptor"
    ):
        receipts.ScopeDescriptor.from_mapping(value)
```

- [ ] **Step 2: Run descriptor tests and confirm failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  -k 'candidate_scope_descriptor or v1_remains_backward' -q
```

Expected: FAIL because v2 is unsupported and the dataclass has no schema/head fields.

- [ ] **Step 3: Implement backward-compatible descriptor parsing**

Keep `SCOPE_SCHEMA_VERSION = "lane-v-scope/v1"` for existing review-scope serialization. Add:

```python
CANDIDATE_SCOPE_DESCRIPTOR_SCHEMA_VERSION = "lane-v-scope/v2"
_CANDIDATE_DESCRIPTOR_FIELDS = frozenset({*_DESCRIPTOR_FIELDS, "reviewed_head"})
```

Add this v2-only command helper:

```python
def _ordered_commands(value: object, *, reason: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ReceiptContractError(reason, "verification_commands must be an array")
    commands = tuple(_validated_command(item, reason=reason) for item in value)
    if (
        not 1 <= len(commands) <= _COMMAND_COLLECTION_MAX_ITEMS
        or len(set(commands)) != len(commands)
    ):
        raise ReceiptContractError(
            reason,
            "verification_commands must contain 1-32 unique items",
        )
    return commands
```

Add `schema_version: str` and `reviewed_head: str | None` to `ScopeDescriptor`. In `from_mapping`, select the exact field set from `mapping["schema_version"]`: v1 uses `_DESCRIPTOR_FIELDS`, keeps `_normalized_commands`, and yields `reviewed_head=None`; v2 uses `_CANDIDATE_DESCRIPTOR_FIELDS`, requires `trigger_kind == "verify-request"`, parses `reviewed_head` through `_full_sha`, and uses `_ordered_commands`. Every other version, missing field, extra field, duplicate v2 command, or invalid command remains `invalid_scope_descriptor`. Do not change `ReviewScope.to_mapping()` or existing receipt digests.

- [ ] **Step 4: Add a v2 authority fixture and resolver tests**

In `tests/unit/test_opus_review_bridge.py`, add `_candidate_authority_fixture`. It must build this exact topology in a temporary Pipeline fixture:

```text
seed -> R(route + candidate packet) -> C1 -> C2 -> D(v2 descriptor only) -> T(verify-request only)
```

The packet uses task ID `AUTHORITY_TASK_ID`, route path `coordination/mailbox/sent/2026-07-15T16-20-00Z-coordinator-to-all-coordination.md`, scope `scripts/feature.py` and `tests/unit/test_feature.py`, `max_commits=5`, the existing trusted pytest command, and governed side effects `none`. Descriptor v2 binds `reviewed_base=R`, `reviewed_head=C2`, allowed roots equal packet scope, and verification commands equal packet commands. Implement the helper by reusing the file's `_git`, `_hash_git_blob`, `_AuthorityFixture`, `PROMPT_PATH`, and `PROMPT_AUTHORITY_PREFIX` utilities; the body must perform these concrete writes and commits:

```python
def _candidate_authority_fixture(
    root: Path, *, mutation: str | None = None
) -> _AuthorityFixture:
    root.mkdir()
    (root / "AGENTS.md").write_text("# Pipeline fixture\n", encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts/codex_protocol_model.py").write_text(
        "# Pipeline marker\n", encoding="utf-8"
    )
    (root / "scripts/feature.py").write_text("VALUE = 0\n", encoding="utf-8")
    (root / "tests/unit").mkdir(parents=True)
    (root / "tests/unit/test_feature.py").write_text(
        "def test_feature():\n    assert True\n", encoding="utf-8"
    )
    (root / "requirements").mkdir()
    (root / "requirements/task.md").write_text(
        "Review the candidate range.\n", encoding="utf-8"
    )
    verifier = root / ".claude/agents/lane-v-verifier.md"
    verifier.parent.mkdir(parents=True)
    verifier.write_text(
        "---\nname: lane-v-verifier\n---\n\nPinned verifier.\n",
        encoding="utf-8",
    )
    prompt = b"---\nname: candidate-advisory\n---\n\nReview candidate evidence.\n"
    prompt_file = root / PROMPT_PATH
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_bytes(prompt)

    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Candidate Authority")
    _git(root, "config", "user.email", "candidate-authority@example.invalid")
    prompt_oid = _hash_git_blob(root, prompt)
    prompt_body = bridge._agent_prompt_from_content(prompt.decode("utf-8")).encode()
    authority = {
        "schema_version": "opus-provider-prompt-authority/v1",
        "prompt_path": PROMPT_PATH,
        "prompt_blob_oid": prompt_oid,
        "file_sha256": "sha256:" + hashlib.sha256(prompt).hexdigest(),
        "file_size_bytes": len(prompt),
        "body_sha256": "sha256:" + hashlib.sha256(prompt_body).hexdigest(),
        "body_size_bytes": len(prompt_body),
    }
    authority_raw = (json.dumps(authority, indent=2, sort_keys=True) + "\n").encode()
    authority_oid = _hash_git_blob(root, authority_raw)
    authority_path = f"{PROMPT_AUTHORITY_PREFIX}{authority_oid}.json"
    authority_file = root / authority_path
    authority_file.write_bytes(authority_raw)
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: seed candidate authority")

    route_path = (
        "coordination/mailbox/sent/"
        "2026-07-15T16-20-00Z-coordinator-to-all-coordination.md"
    )
    route = root / route_path
    route.parent.mkdir(parents=True)
    route.write_text(
        "# Coordinator → All: candidate route\n\n"
        "Event type: coordination\n"
        "Task-board: candidate-authority\n"
        "Packet: director-candidate-authority\n",
        encoding="utf-8",
    )
    packet_task_id = (
        "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
        if mutation == "descriptor-task"
        else AUTHORITY_TASK_ID
    )
    command = (
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
        "tests/unit/test_feature.py -q"
    )
    packet_path = (
        "coordination/capacity/packets/"
        "2026-07-15-candidate-authority-director.json"
    )
    packet_file = root / packet_path
    packet_file.parent.mkdir(parents=True)
    packet_file.write_text(
        json.dumps(
            {
                "id": "director-candidate-authority",
                "wave": 2,
                "cycle": "candidate-authority",
                "owner": "director",
                "packet_type": "director-implementation",
                "row_ids": ["candidate-authority"],
                "allowed_paths": [
                    "scripts/feature.py",
                    "tests/unit/test_feature.py",
                    f"coordination/verification/scopes/{AUTHORITY_TASK_ID}.json",
                    "coordination/mailbox/sent/*director-to-operator-verify-request.md",
                ],
                "lock_keys": [],
                "dependencies": [],
                "acceptance": ["Preserve one candidate objective."],
                "done_evidence": [],
                "handoff_artifact": None,
                "next_recipient": "operator",
                "status": "active",
                "verify_request": None,
                "target_commit": None,
                "commit_range": None,
                "scope_files": ["scripts/feature.py", "tests/unit/test_feature.py"],
                "candidate_policy": {
                    "history": "append-only-until-trigger",
                    "route_event": route_path,
                    "descriptor_task_id": packet_task_id,
                    "max_commits": 5,
                    "verification_commands": [command],
                    "governed_side_effects": "none",
                },
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    _git(root, "add", route_path, packet_path)
    _git(root, "commit", "-q", "-m", "coord: route candidate authority")
    base = _git(root, "rev-parse", "HEAD")

    (root / "scripts/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(root, "commit", "-q", "-m", "feat: candidate implementation")
    (root / "tests/unit/test_feature.py").write_text(
        "def test_feature():\n    assert 1 + 1 == 2\n", encoding="utf-8"
    )
    _git(root, "add", "tests/unit/test_feature.py")
    _git(root, "commit", "-q", "-m", "fix: candidate review fix")
    head = _git(root, "rev-parse", "HEAD")

    if mutation == "descriptor-not-child-of-head":
        (root / "requirements/interstitial.md").write_text(
            "interstitial\n", encoding="utf-8"
        )
        _git(root, "add", "requirements/interstitial.md")
        _git(root, "commit", "-q", "-m", "docs: interstitial before descriptor")

    descriptor_path = (
        "coordination/verification/scopes/"
        f"{AUTHORITY_TASK_ID}.json"
    )
    descriptor_head = "f" * 40 if mutation == "descriptor-head" else head
    descriptor_base = (
        _git(root, "rev-parse", f"{base}^")
        if mutation == "descriptor-base"
        else base
    )
    descriptor_paths = (
        ["scripts/feature.py"]
        if mutation == "descriptor-paths"
        else ["scripts/feature.py", "tests/unit/test_feature.py"]
    )
    descriptor_commands = (
        ["env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"]
        if mutation == "descriptor-commands"
        else [command]
    )
    descriptor = {
        "schema_version": "lane-v-scope/v2",
        "task_id": AUTHORITY_TASK_ID,
        "question_id": "candidate-authority",
        "trigger_kind": "verify-request",
        "verification_mode": "codex-lane-v",
        "verification_harness": "codex:lane-v-verifier",
        "review_profile": "codex-lane-v",
        "reviewed_base": {"policy": "exact", "commit": descriptor_base},
        "reviewed_head": descriptor_head,
        "requirement_paths": ["requirements/task.md", authority_path],
        "allowed_path_roots": descriptor_paths,
        "verification_commands": descriptor_commands,
    }
    descriptor_file = root / descriptor_path
    descriptor_file.parent.mkdir(parents=True)
    descriptor_raw = (json.dumps(descriptor, indent=2) + "\n").encode()
    descriptor_file.write_bytes(descriptor_raw)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_raw).hexdigest()
    _git(root, "add", descriptor_path)
    _git(root, "commit", "-q", "-m", "coord: bind candidate descriptor")
    descriptor_commit = _git(root, "rev-parse", "HEAD")

    if mutation in {"request-not-child-of-descriptor", "implementation-after-descriptor"}:
        path = (
            root / "scripts/feature.py"
            if mutation == "implementation-after-descriptor"
            else root / "requirements/interstitial.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("post-freeze mutation\n", encoding="utf-8")
        relative = path.relative_to(root).as_posix()
        _git(root, "add", relative)
        _git(root, "commit", "-q", "-m", "fix: post-freeze mutation")

    event_path = (
        "coordination/mailbox/sent/"
        "2026-07-15T16-21-00Z-director-to-operator-verify-request.md"
    )
    event = root / event_path
    event.write_text(
        "# Director → Operator: candidate review\n\n"
        "**When:** 2026-07-15T16:21:00Z · **From:** director (online)\n\n"
        "Event type: verify-request\n"
        f"Reviewed head: {head}\n"
        f"Reviewed base: {base}\n"
        f"Lane-V-Scope: {descriptor_path}@{descriptor_digest}\n",
        encoding="utf-8",
    )
    _git(root, "add", event_path)
    _git(root, "commit", "-q", "-m", "coord: request candidate verification")
    trigger_commit = _git(root, "rev-parse", "HEAD")
    requested_head = head
    if mutation == "old-trigger-new-head":
        (root / "scripts/feature.py").write_text("VALUE = 3\n", encoding="utf-8")
        _git(root, "add", "scripts/feature.py")
        _git(root, "commit", "-q", "-m", "fix: descendant after old trigger")
        requested_head = _git(root, "rev-parse", "HEAD")

    return _AuthorityFixture(
        root=root,
        request=bridge.ReviewRequest(
            repo_root=root,
            reviewed_head=requested_head,
            reviewed_base=base,
            review_profile="codex-lane-v",
            authorization_source="",
            trigger_kind="verify-request",
            trigger_commit=trigger_commit,
            trigger_path=event_path,
        ),
        base=base,
        head=head,
        descriptor_commit=descriptor_commit,
        trigger_commit=trigger_commit,
        descriptor_path=descriptor_path,
        descriptor_digest=descriptor_digest,
        event_path=event_path,
    )
```

Add these tests:

```python
def test_candidate_v2_trigger_revalidates_packet_range_before_lane_v(
    tmp_path: Path,
) -> None:
    fixture = _candidate_authority_fixture(tmp_path / "repo")

    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)

    assert resolved.authority.schema_version == "lane-v-scope/v2"
    assert resolved.authority.reviewed_head == fixture.head
    assert resolved.scope.effective_base == fixture.base
    assert resolved.scope.reviewed_head == fixture.head


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        ("descriptor-head", "reviewed_scope_mismatch"),
        ("descriptor-base", "reviewed_scope_mismatch"),
        ("descriptor-task", "candidate_range_invalid"),
        ("descriptor-paths", "candidate_contract_mismatch"),
        ("descriptor-commands", "candidate_contract_mismatch"),
        ("descriptor-not-child-of-head", "candidate_freeze_invalid"),
        ("request-not-child-of-descriptor", "candidate_freeze_invalid"),
        ("implementation-after-descriptor", "candidate_freeze_invalid"),
        ("old-trigger-new-head", "invalid_verify_request"),
    ),
)
def test_candidate_v2_trigger_rejects_one_mutated_binding(
    tmp_path: Path, mutation: str, reason: str
) -> None:
    lawful = _candidate_authority_fixture(tmp_path / f"{mutation}-lawful")
    bridge.resolve_provider_authoritative_scope(lawful.request)
    fixture = _candidate_authority_fixture(
        tmp_path / mutation, mutation=mutation
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_provider_authoritative_scope(fixture.request)

    assert excinfo.value.reason == reason
```

The lawful resolution at the start of every parameterized case makes abuse cases 8 and 9 non-vacuous.

- [ ] **Step 5: Run bridge tests and confirm failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  -k 'candidate_v2_trigger' -q
```

Expected: FAIL because the bridge neither recognizes v2 nor calls the candidate validator.

- [ ] **Step 6: Expose the existing trusted-command validator**

Refactor `_validate_pytest_arguments` and `_validated_verification_rule` to accept `repo_root: Path` instead of the whole provider request. Add:

```python
def validate_verification_commands(
    repo_root: Path | str, commands: tuple[str, ...]
) -> None:
    root = Path(repo_root).resolve()
    if not commands:
        raise ReviewContractError(
            "invalid_scope", "at least one verification command is required"
        )
    for command in commands:
        _validated_verification_rule(root, command)
```

Update `_validate_request_shape` to call this public function. Do not widen `_NO_ARGUMENT_VERIFIER_SCRIPTS`, `_FIXED_ARGUMENT_VERIFIER_SCRIPTS`, interpreter rules, pytest target rules, or forbidden shell syntax.

- [ ] **Step 7: Re-run the shared candidate validator during v2 resolution**

Import `protocol_capacity` in `scripts/opus_review_bridge.py`. After descriptor parsing and before provider-request construction, add:

```python
if authority.schema_version == receipts.CANDIDATE_SCOPE_DESCRIPTOR_SCHEMA_VERSION:
    if authority.reviewed_head != request.reviewed_head:
        raise ReviewContractError(
            "reviewed_scope_mismatch",
            "candidate descriptor reviewed head does not agree",
        )
    candidate = protocol_capacity.validate_candidate_for_task(
        root,
        request.reviewed_head,
        authority.task_id,
        command_validator=validate_verification_commands,
    )
    if not candidate.valid or candidate.packet is None:
        details = "; ".join(
            f"{issue['gate']}: {issue['message']}" for issue in candidate.issues
        )
        raise ReviewContractError("candidate_range_invalid", details)
    packet = candidate.packet
    policy = packet.candidate_policy
    assert policy is not None
    if (
        candidate.candidate_base != authority.base_commit
        or candidate.candidate_head != authority.reviewed_head
        or tuple(sorted(packet.scope_files)) != authority.allowed_path_roots
        or policy.descriptor_task_id != authority.task_id
        or policy.verification_commands != authority.verification_commands
        or policy.governed_side_effects != "none"
    ):
        raise ReviewContractError(
            "candidate_contract_mismatch",
            "descriptor does not copy the validated candidate contract",
        )
    _require_candidate_freeze_topology(
        root=root,
        candidate_head=request.reviewed_head,
        descriptor_path=reference.descriptor_path,
        trigger_commit=request.trigger_commit,
    )
```

Implement `_require_candidate_freeze_topology` by deriving the unique descriptor-add commit reachable from the trigger. Require its sole parent to equal `candidate_head`, and require the trigger's sole parent to equal the descriptor commit. Reject all other topology with reason `candidate_freeze_invalid`. The candidate validator reads the packet and absence of descriptor/request from `candidate_head`, so the descriptor and trigger never pollute the reviewed range.

- [ ] **Step 8: Run receipt, bridge, and legacy trigger suites**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_protocol_capacity.py -q
```

Expected: all tests pass; all existing v1 shipping and verify-request fixtures remain green; no provider function or receipt store is constructed by the candidate resolver tests.

- [ ] **Step 9: Commit Task 3**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/opus_review_receipts.py \
  scripts/opus_review_bridge.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m \
  "feat(opus): bind candidate ranges into Lane V"
```

Expected: one commit changing only the four named paths.

## Task 4: Synchronize protocol mirrors and prove the whole contract

**Files:**

- Modify: `scripts/codex_protocol_model.py:399-415, 737-742, 1188-1208, 1211-1241`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`
- Modify: `docs/protocol/agents/orchestration.md`
- Modify: `docs/protocol/agents/director-operator.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/claude/continuation.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/four-seat-protocol/SKILL.md`
- Modify: `.claude/skills/seat-coordinator/SKILL.md`
- Modify: `.claude/skills/seat-director/SKILL.md`
- Modify: `.claude/skills/seat-operator/SKILL.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.claude/agents/lane-v-verifier.md`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`

**Interfaces:**

- Consumes: executable CLI and v2 resolver contract from Tasks 1–3.
- Produces: `PRE_TRIGGER_CANDIDATE_RANGE_RULES`, `render_pre_trigger_candidate_range()`, synchronized producer/consumer/coordinator guidance, and full abuse-case evidence.

- [ ] **Step 1: Add failing mirror tests**

In `tests/unit/test_protocol_prompt_sync.py`, add:

```python
CANDIDATE_RANGE_FRAGMENTS = (
    "append-only-until-trigger",
    "one through five total unaccepted commits",
    "strict linear fast-forward",
    "descriptor commit freezes",
    "fresh coordinator-mediated descriptor",
    "no provider, receipt, lock, merge, push, or publication authority",
)


@pytest.mark.parametrize(
    "path",
    (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/agents/orchestration.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/skills/four-seat-protocol/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".codex/agents/protocol-director.toml",
    ),
)
def test_candidate_range_producer_contract_is_surface_synced(path: str) -> None:
    text = _compact(_read(path).replace("`", ""))
    for fragment in CANDIDATE_RANGE_FRAGMENTS:
        assert fragment in text, (path, fragment)


@pytest.mark.parametrize(
    "path",
    (
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-operator/verification-report-format.md",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
    ),
)
def test_candidate_range_consumer_contract_is_surface_synced(path: str) -> None:
    text = _compact(_read(path).replace("`", ""))
    assert "lane-v-scope/v1" in text
    assert "lane-v-scope/v2" in text
    assert "re-runs the candidate-range validator" in text
    assert "descriptor commit freezes" in text


@pytest.mark.parametrize(
    "path",
    (
        ".agents/skills/seat-coordinator/SKILL.md",
        ".claude/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-coordinator.toml",
    ),
)
def test_candidate_range_coordinator_reroute_contract_is_surface_synced(
    path: str,
) -> None:
    text = _compact(_read(path).replace("`", ""))
    assert "sixth unaccepted commit" in text
    assert "post-freeze correction" in text
    assert "fresh coordinator-mediated descriptor" in text
```

In `tests/unit/test_protocol_doc_integrity.py`, add assertions that `OPERATIONS.md` contains both candidate CLI flags, `ARCHITECTURE.md` names the single validator reuse and both descriptor versions, and no normative mirror says an append-policy route requires exactly one implementation commit.

- [ ] **Step 2: Run mirror tests and confirm failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  -k 'candidate_range' -q
```

Expected: FAIL because the compact model and mirrors do not yet contain the approved invariant.

- [ ] **Step 3: Add the compact model source of truth**

Add this tuple after `PAIR_OPERATING_RULES`:

```python
PRE_TRIGGER_CANDIDATE_RANGE_RULES = (
    "An active director-implementation packet may opt into append-only-until-trigger only through one exact candidate_policy.",
    "The candidate range is one through five total unaccepted commits from the unique route-event commit to the final candidate head.",
    "History is a strict linear fast-forward; every commit stays inside unchanged scope_files, acceptance, task identity, verification commands, and governed side effects none.",
    "Spec and quality review fixes are separate commits before authority publication; an exact-one implementation clause conflicts with this policy and blocks the route.",
    "The Director runs protocol_capacity_board.py --validate-candidate with the exact full candidate head before descriptor creation.",
    "The descriptor commit freezes autonomous correction, its parent is the validated head, and the verify-request is its direct child.",
    "Lane V accepts legacy lane-v-scope/v1 unchanged; lane-v-scope/v2 re-runs the candidate-range validator and cross-checks base, head, task, paths, and commands.",
    "A sixth unaccepted commit, scope or semantic expansion, rewritten history, self-modifying enforcement, incomplete evidence, or any post-freeze correction returns to the coordinator for a fresh coordinator-mediated descriptor and trigger.",
    "Mechanical gates do not decide tightly coupled semantics; the Director explains one correction objective and the independent Operator may reject a multi-objective range.",
    "V1 preserves candidate SHAs named in relevant committed mailbox evidence and does not claim to detect a discarded tip that was never durable.",
    "This policy grants no provider, receipt, lock, merge, push, or publication authority.",
)


def render_pre_trigger_candidate_range() -> str:
    lines = ["Pre-Trigger Append-Only Candidate Range:"]
    lines.extend(f"- {rule}" for rule in PRE_TRIGGER_CANDIDATE_RANGE_RULES)
    return "\n".join(lines)
```

Include the renderer in the pair contract and surface summary. Update `CROSS_MODEL_VERIFICATION_RULES` to say the resolver accepts legacy v1 plus candidate-bound v2, while preserving every existing one-shot Opus and Operator-authority rule.

- [ ] **Step 4: Apply the exact rule to producer mirrors**

Add a compact “Pre-Trigger Append-Only Candidate Range” section to every producer path listed in Step 1. Use the nine model rules verbatim or provider-native wording that preserves every required fragment. Director mechanics must include:

```bash
env -u GIT_INDEX_FILE .venv/bin/python \
  scripts/protocol_capacity_board.py --wave 2 \
  --validate-candidate coordination/capacity/packets/2026-07-15-candidate-director.json \
  --candidate-head "$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
```

State that the illustrative packet path must be replaced by the active committed Director packet selected by the coordinator route. The command is read-only and creates no descriptor, trigger, receipt, provider attempt, merge, or push.

- [ ] **Step 5: Apply the exact rule to consumer and coordinator mirrors**

Operator/Lane V mirrors must state:

- v1 remains the legacy exact descriptor contract;
- v2 requires a committed candidate packet and re-runs the candidate-range validator before any receipt or provider construction;
- the reviewed head is the descriptor's bound head, not a moving branch;
- descriptor commit freezes the range;
- any mismatch or post-freeze implementation commit is FAIL/blocker, never reconstructed authority.

Coordinator mirrors must state:

- a sixth unaccepted commit, semantic expansion, scope/command/task change, rewritten history, self-modification, incomplete evidence, or post-freeze correction requires a fresh route;
- the coordinator cannot slide the base to an unaccepted intermediate commit;
- replacement preserves old descriptor/request bytes and uses a fresh task identity;
- no provider, receipt, lock, merge, push, or publication authority follows from candidate correction.

Update `ARCHITECTURE.md` with current source line references after code lands, not the pre-plan line numbers. Update its `*Last verified:*` footer to the final implementation commit. Add the CLI to `OPERATIONS.md` and describe the zero-side-effect read-only result and exit status.

- [ ] **Step 6: Run all focused protocol tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all focused tests pass; smoke reports `OK`; `git diff --check` has no output; no provider process, receipt, runtime state, mailbox event, lock, merge, or remote ref is created.

- [ ] **Step 7: Prove all twelve abuse cases are covered**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py \
  -k 'candidate or append_policy or scope_descriptor_v1' -q
```

Expected coverage mapping:

1. two-commit implementation plus review fix: `test_candidate_range_accepts_initial_commit_and_review_fix`;
2. exact-one contradiction: `test_route_rejects_append_policy_with_exact_one_shipping_commit`;
3. sixth commit: `six-commits` mutation;
4. merge/nonlinear history: `merge` mutation;
5. amended evidence-named head: `test_candidate_range_rejects_amended_head_named_by_committed_evidence`;
6. forbidden path, rename endpoint, symlink, gitlink, and mode: candidate mutation matrix plus a dedicated allowed-to-forbidden rename test;
7. acceptance, commands, task, or side-effect drift: policy schema tests and v2 binding matrix;
8. descriptor then implementation append: `implementation-after-descriptor`;
9. old trigger against new head: `old-trigger-new-head`;
10. sliding base: `test_candidate_range_rejects_sliding_base_to_unaccepted_intermediate`;
11. self-modifying validator/schema: `self-modifying-validator` plus a bridge-path protected mutation;
12. Stage A topology: the separate coordinator correction, Director2 additive fix, and Operator2 report must record base `40fd0a5e43c6b28330ced9ddffe01483cde42b65`, preserved `56091d107382abfe9f06df1aa4cd003d71be7b5e`, exactly one additive fix, the original four-path aggregate diff, and zero provider attempts.

Every negative unit test first proves its lawful fixture passes, then mutates only the prohibited dimension.

- [ ] **Step 8: Commit Task 4**

Stage only the exact paths listed for Task 4, inspect the staged scope, and commit:

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/codex_protocol_model.py \
  AGENTS.md CLAUDE.md ARCHITECTURE.md OPERATIONS.md \
  docs/protocol/agents/orchestration.md \
  docs/protocol/agents/director-operator.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/claude/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-operator/verification-report-format.md \
  .claude/skills/four-seat-protocol/SKILL.md \
  .claude/skills/seat-coordinator/SKILL.md \
  .claude/skills/seat-director/SKILL.md \
  .claude/skills/seat-operator/SKILL.md \
  .claude/skills/seat-operator/verification-report-format.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/lane-v-verifier.toml \
  .claude/agents/lane-v-verifier.md \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m \
  "docs(protocol): codify pre-trigger candidate ranges"
```

Expected: the fourth implementation-range commit contains only compact-model, protocol-doc, skill/prompt mirror, and mirror-test changes. It contains no capacity, bridge, receipt, provider, mailbox, packet, lock, merge, or push mutation.

## Independent verification and integration

After the four implementation commits exist, the Director re-runs the complete Task 4 gate and dispatches fresh spec and code-quality reviewers against the exact route base through final head. Review questions must explicitly cover all twelve abuse cases, v1 backward compatibility, no provider attempt, no side-effect authority, and the descriptor freeze topology. This self-modifying implementation route uses the coordinator-authorized four-commit range plus at most one separate reviewer-fix commit; a need for another commit returns to the coordinator.

The Director then creates one legacy `lane-v-scope/v1` descriptor and one canonical verify-request under this active self-modifying route. The paired Operator independently verifies the exact frozen range and returns one committed GO/NITS/FAIL. A valid later cross-model review may address the actual diff as a new verification question; the failed manual ChatGPT Pro consultation `67d59d80-9331-425f-8eab-b70012734ee6` is terminal and is not retried or reused.

Only after Operator GO:

1. the designated integrator performs the local merge;
2. the merged tree re-runs the five focused test files, `scripts/ci_smoke.py`, and `git diff --check`;
3. the coordinator confirms the merged object IDs equal the approved range and no post-GO edits exist; and
4. a separately named executor may push the explicitly named remote/ref under a fresh side-effect executor token.

Any NITS/FAIL, newer relevant mail, changed target blob, failed test, descriptor/trigger mismatch, provider attempt, receipt mutation, dirty target path, merge conflict, or post-GO edit stops before merge or push.
