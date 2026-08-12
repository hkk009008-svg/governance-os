# Route Preflight Friction Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject malformed target guidance, stale autonomous parents, global legacy forks, and same-task legacy downgrades before a route is committed, while documenting one authority-safe Supabase lifecycle preflight.

**Architecture:** Keep `ledger_start_guard.parse_route_guidance_body` as the only target-guidance grammar. Add current-task and global legacy-tip checks to the existing capacity validator using `RouteBatchReader`, `resolve_task_routes`, and `resolve_authoritative`, and expose only the existing Task-board parser from `route_lineage`. Record the service rule once in the canonical ledger adoption bridge; add no helper service or dependency.

**Tech Stack:** Python 3.11+, pytest, existing Pipeline route/mailbox modules, Markdown doctrine.

## Global Constraints

- Design authority: `docs/superpowers/specs/2026-07-22-route-preflight-friction-reduction-design.md@9d91e8375a9f6dce2a5284f1d8b32dcb23f5b978`.
- One Director owns the complete implementation range; do not run concurrent implementers on the shared validator files.
- Use RED to GREEN for every behavior change and stage only explicit pathspecs.
- Reuse `ledger_start_guard.parse_route_guidance_body`; do not copy its regular expressions or allowed-path loop.
- Expose the existing Task-board parser only; do not change committed route resolution or effectiveness semantics.
- Preserve historical committed bytes; when a generated global legacy tip exists, every new generated Coordinator candidate must extend it exactly.
- Add no module, executable, dependency, lifecycle helper, service supervisor, retry loop, registry, or state store.
- Do not change evidence-ledger, the Codex task tools, fixed-writer behavior, fast-resume behavior, or any service/container/database state.
- Validation is read-only and grants no merge, push, deployment, activation, service, cursor, lock, spend, or other external-effect authority.
- Assess these abuse classes in final review: parser differential, stale-parent replay, global legacy fork, same-task legacy downgrade, unresolved same-task evidence, and route-text confusion about service authority.

---

## File Map

| File | Responsibility in this plan |
|---|---|
| `scripts/protocol_capacity.py` | Apply the shared guidance parser and reject route candidates that do not extend current committed task truth |
| `scripts/route_lineage.py` | Expose the existing exact Task-board parser as `task_board_of(body)` without changing resolver behavior |
| `tests/unit/test_protocol_capacity.py` | Pin malformed/corrected guidance and all candidate-tip/legacy compatibility cases through the public validator |
| `tests/unit/test_route_lineage.py` | Pin the public Task-board parser's exact single-field behavior |
| `docs/protocol/codex/ledger-cli-adoption.md` | Hold the one canonical Supabase lifecycle preflight and authority boundary |

## Task 1: Reuse The Start-Guard Guidance Grammar Before Commit

**Files:**

- Modify: `tests/unit/test_protocol_capacity.py`
- Modify: `scripts/protocol_capacity.py:10-18,1128-1172`

**Interfaces:**

- Consumes: `ledger_start_guard.parse_route_guidance_body(body: str) -> RouteGuidance`
- Produces: a blocking `G7` issue whose message includes the candidate filename and the parser's `ValueError` reason

- [ ] **Step 1: Add the malformed revision-34 and corrected revision-35 regression tests**

Add these tests immediately after `test_autonomous_route_needs_no_packets_join_or_capacity_split`:

```python
def test_route_validation_rejects_prose_inside_target_allowed_paths(
    tmp_path: Path,
):
    route = _write_route(
        tmp_path,
        "2026-07-22T01-43-27Z-director-to-all-coordination.md",
        _autonomous_route_body(
            "\n## Target Allowed Paths\n\n"
            "- scripts/protocol_capacity.py\n"
            "Explanatory prose is not an allowed-path bullet.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        route.name in issue["message"]
        and "allowed-path section accepts bullet paths only" in issue["message"]
        for issue in result.route_issues
    )


def test_route_validation_accepts_semantics_after_allowed_path_heading(
    tmp_path: Path,
):
    route = _write_route(
        tmp_path,
        "2026-07-22T02-01-34Z-director-to-all-coordination.md",
        _autonomous_route_body(
            "\n## Target Allowed Paths\n\n"
            "- scripts/protocol_capacity.py\n\n"
            "## Allowed Path Semantics\n\n"
            "The bullet is implementation scope; this prose is explanation.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()
```

- [ ] **Step 2: Run the two regressions and confirm the parser gap**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'prose_inside_target_allowed_paths or semantics_after_allowed_path_heading' -q
```

Expected before implementation: one failure because the malformed revision-34 shape is reported valid; the corrected shape passes.

- [ ] **Step 3: Import and invoke the exact start-guard parser**

Extend the existing import fallback at the top of `scripts/protocol_capacity.py` to this shape:

```python
try:
    from scripts import codex_protocol_model as model
    from scripts import ledger_start_guard
    from scripts import route_lineage
except ImportError:  # direct script execution
    import codex_protocol_model as model
    import ledger_start_guard
    import route_lineage
```

Replace the route-recognition branch inside `_validate_route_file` with:

```python
    recognized_route = route_lineage.is_route_event(path, body)
    if not recognized_route:
        issues.append(
            _issue("G7", f"{path.name}: not a recognized outcome-contract route")
        )
    else:
        try:
            ledger_start_guard.parse_route_guidance_body(body)
        except ValueError as exc:
            issues.append(
                _issue("G7", f"{path.name}: invalid route guidance ({exc})")
            )
        if autonomous_candidate is not None:
            issues.extend(
                _autonomous_candidate_parent_issues(
                    autonomous_candidate,
                    Path(report.root),
                )
            )
```

Keep the path check, autonomous structural parse, side-effect checks, and return statement unchanged.

- [ ] **Step 4: Run the focused and complete capacity tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'prose_inside_target_allowed_paths or semantics_after_allowed_path_heading' -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py -q
```

Expected: both commands pass; the complete file reports no regression in legacy routes or structural side-effect token handling.

- [ ] **Step 5: Commit Task 1**

```bash
env -u GIT_INDEX_FILE git add \
  scripts/protocol_capacity.py tests/unit/test_protocol_capacity.py
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "fix(protocol): validate route guidance before commit"
```

Expected staged paths: exactly the two named files.

## Task 2: Bind Candidates To Current Authoritative Task Truth

**Files:**

- Modify: `tests/unit/test_route_lineage.py:1-45`
- Modify: `scripts/route_lineage.py:220-244,354-370`
- Modify: `tests/unit/test_protocol_capacity.py:145-370`
- Modify: `scripts/protocol_capacity.py:1150-1235`

**Interfaces:**

- Produces: `route_lineage.task_board_of(body: str) -> str | None`
- Consumes: `RouteBatchReader.load_all_routes()`, `RouteBatchReader.issues_for_task(task_id)`, `RouteBatchReader.load_route_ref(ref)`, `resolve_task_routes(routes, task_id)`, and `resolve_authoritative(legacy_routes)`
- Produces: blocking `G7` issues for an existing-task root, unresolved task evidence, a non-tip parent, a generated legacy route that does not extend the current global tip, or a legacy candidate targeting an autonomous task

- [ ] **Step 1: Pin the public Task-board parser**

Add this test after `test_parse_legacy_route_without_generation` in `tests/unit/test_route_lineage.py`:

```python
def test_task_board_of_requires_one_non_none_exact_field():
    assert route_lineage.task_board_of("Task-board: `demo-task`\n") == "demo-task"
    assert route_lineage.task_board_of("Task-board: none\n") is None
    assert route_lineage.task_board_of(
        "Task-board: first\nTask-board: second\n"
    ) is None
```

- [ ] **Step 2: Add committed autonomous-route fixture support**

Add this helper after `_commit_legacy_parent` in `tests/unit/test_protocol_capacity.py`:

```python
def _commit_autonomous_route(
    root: Path,
    *,
    task_id: str,
    parent: str,
    revision: int,
    minute: int,
) -> str:
    name = (
        f"2026-07-18T09-{minute:02d}-00Z-director-to-all-coordination.md"
    )
    path = _write_route(
        root,
        name,
        "# director -> all: route event\n\n"
        f"**When:** 2026-07-18T09:{minute:02d}:00Z · "
        "**From:** director (online)\n\n"
        + _autonomous_route_body(
            task_id=task_id,
            parent=parent,
            revision=revision,
            previous_owners="director",
        )
        + "\nCursor at send: 0\n",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-q", "-m", f"add route revision {revision}")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"
```

- [ ] **Step 3: Add the authoritative-tip and legacy-compatibility regressions**

Add these tests after the existing autonomous candidate parent tests:

```python
def test_autonomous_candidate_accepts_current_authoritative_tip(tmp_path: Path):
    parent = _commit_legacy_parent(tmp_path, generation=3)
    tip = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=parent,
        revision=4,
        minute=10,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=tip,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_autonomous_candidate_rejects_effective_superseded_parent(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    superseded = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=superseded,
        revision=5,
        minute=20,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=superseded,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "parent contract must equal current authoritative task tip"
        in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_root_rejects_existing_same_task_route(tmp_path: Path):
    _commit_legacy_parent(tmp_path, generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "revision-zero root requires an empty committed task"
        in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_candidate_rejects_unresolved_same_task_fork(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    left = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=11,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=left,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "current task lineage is unresolved" in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_task_with_autonomous_lineage(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: autonomous-capacity-test\n"
        "Route generation: 4\n"
        f"Supersedes route: {legacy.split('@', 1)[0]}\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "legacy route cannot extend a task with autonomous lineage"
        in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_new_global_root_beside_existing_tip(
    tmp_path: Path,
):
    _commit_legacy_parent(tmp_path, task_id="prior-global-task", generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: next-global-task\nRoute generation: 0\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "generated legacy route must extend current global tip"
        in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_accepts_next_global_generation_and_tip(
    tmp_path: Path,
):
    legacy = _commit_legacy_parent(
        tmp_path,
        task_id="prior-global-task",
        generation=3,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: next-global-task\n"
        "Route generation: 4\n"
        f"Supersedes route: {legacy.split('@', 1)[0]}\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
```

- [ ] **Step 4: Run the new tests and confirm the missing protections**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py \
  -k task_board_of -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'current_authoritative_tip or superseded_parent or existing_same_task_route or unresolved_same_task_fork or legacy_candidate or next_global_generation' -q
```

Expected before implementation: the route-lineage test fails with missing `task_board_of`; the stale-parent, existing-root, fork, global-root, and autonomous-to-legacy cases fail because validation accepts them.

- [ ] **Step 5: Expose the existing Task-board parser without changing semantics**

Rename `_task_board` in `scripts/route_lineage.py` and retain its complete body:

```python
def task_board_of(body: str) -> str | None:
    matches = re.findall(r"^\s*Task-board:\s*`?([^`\n]+?)`?\s*$", body, re.MULTILINE)
    if len(matches) != 1:
        return None
    task_id = matches[0].strip()
    if task_id.casefold().startswith("none"):
        return None
    return task_id
```

Replace both internal calls with the public name:

```python
    if sender in {"coordinator", "coordinator2"}:
        return kind in {"coordination", "status", "decision"} and task_board_of(body) is not None
```

```python
        task_id=task_board_of(body),
```

Do not change `parse_lineage`, `_partial_route_task_id`, `resolve_task_routes`, or committed-effectiveness code.

- [ ] **Step 6: Add one batched committed-task context helper**

Add this helper immediately before `_autonomous_candidate_parent_issues` in `scripts/protocol_capacity.py`:

```python
def _committed_task_context(
    root: Path,
    task_id: str,
    candidate_path: Path,
    *,
    parent_ref: str | None = None,
) -> tuple[
    list[route_lineage.LineageRoute],
    tuple[str, ...],
    route_lineage.LineageRoute | None,
]:
    with route_lineage.RouteBatchReader(root) as reader:
        routes = [
            route
            for route in reader.load_all_routes()
            if route.path != candidate_path
        ]
        task_issues = reader.issues_for_task(task_id)
        parent = reader.load_route_ref(parent_ref) if parent_ref is not None else None
    return routes, task_issues, parent
```

Filtering only `candidate_path` preserves non-Git fixture compatibility while keeping every other committed/current route in resolution.

- [ ] **Step 7: Replace autonomous parent validation with current-tip validation**

Replace `_autonomous_candidate_parent_issues` with:

```python
def _autonomous_candidate_parent_issues(
    candidate: route_lineage.LineageRoute,
    root: Path,
) -> list[dict[str, Any]]:
    """Prove candidate continuity against current committed task truth."""

    task_id = candidate.task_id or ""
    try:
        routes, task_issues, parent = _committed_task_context(
            root,
            task_id,
            candidate.path,
            parent_ref=candidate.parent_ref,
        )
    except (OSError, UnicodeError, ValueError):
        message = (
            "parent contract is not an effective committed route"
            if candidate.parent_ref is not None
            else "current task route evidence is unreadable"
        )
        return [_issue("G7", f"{candidate.path.name}: {message}")]

    issues = [
        _issue(
            "G7",
            f"{candidate.path.name}: current task route evidence is unresolved ({message})",
        )
        for message in task_issues
    ]
    matching = [route for route in routes if route.task_id == task_id]

    if candidate.parent_ref is None:
        if candidate.revision != 0:
            issues.append(
                _issue(
                    "G7",
                    f"{candidate.path.name}: parent none requires contract revision 0",
                )
            )
        if matching:
            issues.append(
                _issue(
                    "G7",
                    f"{candidate.path.name}: revision-zero root requires an empty committed task",
                )
            )
        return issues

    assert parent is not None
    if not parent.effective:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent contract is not an effective committed route",
            )
        )
    if parent.task_id != candidate.task_id:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent Task ID does not match candidate Task ID",
            )
        )
    if parent.revision is None or candidate.revision != parent.revision + 1:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: contract revision must equal parent revision plus one",
            )
        )

    resolution = route_lineage.resolve_task_routes(routes, task_id)
    if resolution.issues or resolution.authoritative is None:
        detail = "; ".join(resolution.issues) or "no authoritative route"
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: current task lineage is unresolved ({detail})",
            )
        )
    elif resolution.authoritative.route_ref != candidate.parent_ref:
        issues.append(
            _issue(
                "G7",
                f"{candidate.path.name}: parent contract must equal current authoritative task tip",
            )
        )
    return issues
```

- [ ] **Step 8: Reject global legacy forks and same-task autonomous downgrades**

Add this helper after autonomous parent validation:

```python
def _legacy_candidate_lineage_issues(
    path: Path,
    body: str,
    root: Path,
) -> list[dict[str, Any]]:
    task_id = route_lineage.task_board_of(body)
    if task_id is None:
        return []
    try:
        routes, task_issues, _ = _committed_task_context(
            root,
            task_id,
            path,
        )
    except (OSError, UnicodeError, ValueError):
        return [
            _issue("G7", f"{path.name}: current task route evidence is unreadable")
        ]

    issues = [
        _issue(
            "G7",
            f"{path.name}: current task route evidence is unresolved ({message})",
        )
        for message in task_issues
    ]
    legacy_routes = [route for route in routes if route.legacy]
    generated_legacy = [
        route
        for route in legacy_routes
        if route.lineage.generation is not None
    ]
    if generated_legacy:
        global_resolution = route_lineage.resolve_authoritative(legacy_routes)
        if global_resolution.issues or global_resolution.authoritative is None:
            detail = "; ".join(global_resolution.issues) or "no global tip"
            issues.append(
                _issue(
                    "G7",
                    f"{path.name}: current global legacy lineage is unresolved ({detail})",
                )
            )
        else:
            current_tip = global_resolution.authoritative
            assert current_tip.lineage.generation is not None
            candidate_lineage = route_lineage.parse_lineage(body)
            expected_generation = current_tip.lineage.generation + 1
            if (
                candidate_lineage.generation != expected_generation
                or candidate_lineage.parent_route_id != current_tip.route_id
            ):
                issues.append(
                    _issue(
                        "G7",
                        f"{path.name}: generated legacy route must extend current "
                        f"global tip {current_tip.route_id} at generation "
                        f"{expected_generation}",
                    )
                )
    if any(
        route.task_id == task_id and not route.legacy
        for route in routes
    ):
        issues.append(
            _issue(
                "G7",
                f"{path.name}: legacy route cannot extend a task with autonomous lineage; "
                "the incumbent must publish an autonomous continuation or use durable transfer",
            )
        )
    return issues
```

Then extend the recognized-route branch created in Task 1:

```python
        if autonomous_candidate is not None:
            issues.extend(
                _autonomous_candidate_parent_issues(
                    autonomous_candidate,
                    Path(report.root),
                )
            )
        else:
            issues.extend(
                _legacy_candidate_lineage_issues(path, body, Path(report.root))
            )
```

- [ ] **Step 9: Run the new regressions and complete focused suites**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py -k task_board_of -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k 'current_authoritative_tip or superseded_parent or existing_same_task_route or unresolved_same_task_fork or legacy_candidate or next_global_generation' -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py tests/unit/test_route_lineage.py -q
```

Expected: every command passes. The public `validate_route` tests are the required temporary-candidate validator probes; they exercise both non-Git staged bodies and committed Git lineage.

- [ ] **Step 10: Commit Task 2**

```bash
env -u GIT_INDEX_FILE git add \
  scripts/protocol_capacity.py scripts/route_lineage.py \
  tests/unit/test_protocol_capacity.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "fix(protocol): bind route candidates to current tip"
```

Expected staged paths: exactly the four named files.

## Task 3: Add The Single Service Rule And Run The Acceptance Gate

**Files:**

- Modify: `docs/protocol/codex/ledger-cli-adoption.md:72-83`

**Interfaces:**

- Consumes: the existing AGENTS.md pointer to the canonical ledger adoption bridge
- Produces: one instruction-only Supabase lifecycle rule; no executable or duplicated prompt text

- [ ] **Step 1: Prove the lifecycle heading is absent**

Run:

```bash
rg -n '^## Local Supabase Lifecycle Preflight$' \
  docs/protocol/codex/ledger-cli-adoption.md
```

Expected before the documentation edit: exit 1 and no output.

- [ ] **Step 2: Add the exact canonical doctrine section**

Insert this section immediately before `## Enter Evidence-Ledger`:

```markdown
## Local Supabase Lifecycle Preflight

Before any user-authorized local Supabase lifecycle action, inspect
`supabase --version` and the exact existing project container/service state.
If the database is already running while required siblings are stopped, do not
infer that `supabase start` or `--exclude` will partially resume those
siblings.

Stop and report the observed state unless the user separately authorizes the
exact existing-container action and the active route records its executor,
target, scope, frozen identities, and restoration contract. This preflight
does not authorize network, acquisition, configuration, restart, cleanup, or
any other service action.
```

Do not copy the section into `AGENTS.md`, a skill, or `codex_protocol_model.py`.

- [ ] **Step 3: Verify the canonical wording and bridge compatibility**

Run:

```bash
rg -n '^## Local Supabase Lifecycle Preflight$|supabase --version|partially resume|user separately authorizes|frozen identities' \
  docs/protocol/codex/ledger-cli-adoption.md
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_prompt_sync.py -q
```

Expected: one lifecycle heading, all four required concepts present, and both test files pass without requiring duplicated doctrine.

- [ ] **Step 4: Commit Task 3**

```bash
env -u GIT_INDEX_FILE git add docs/protocol/codex/ledger-cli-adoption.md
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "docs(protocol): require Supabase lifecycle preflight"
```

Expected staged path: exactly the adoption bridge.

- [ ] **Step 5: Run the complete implementation acceptance profile**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py tests/unit/test_route_lineage.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff HEAD~3..HEAD --check
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git diff --name-only HEAD~3..HEAD
```

Expected:

- all focused tests pass;
- global route lineage is valid;
- project smoke is `OK`;
- the three-commit range has no whitespace errors;
- the tracked worktree and index are clean; and
- the implementation manifest is exactly:

```text
docs/protocol/codex/ledger-cli-adoption.md
scripts/protocol_capacity.py
scripts/route_lineage.py
tests/unit/test_protocol_capacity.py
tests/unit/test_route_lineage.py
```

- [ ] **Step 6: Perform the owner abuse-class review and request independent verification**

Inspect the actual three-commit range and record one disposition for each:

```text
parser differential: closed by the shared pure parser and revision-34/35 probes
stale-parent replay: closed by exact authoritative-tip equality
global legacy fork: closed by exact global-tip parent and consecutive generation
same-task legacy downgrade: closed after any committed autonomous route
unresolved same-task evidence: fails closed without selecting a winner
service authority confusion: doctrine requires separate user authorization plus exact route fields
```

Then publish one canonical verify-request through the fixed mailbox writer. Bind the exact base/head, all five changed paths, the three commit subjects, the six abuse-class dispositions above, the immutable defect evidence refs from design section 2, the implementation owner/model, and one distinct different-model non-author Operator. Do not merge, push, deploy, start services, resume beta activation, or change evidence-ledger. After Operator review, stop for Coordinator reconciliation; the separate beta sequence follows the Mac-first checkpoint in design section 9.
