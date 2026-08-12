# Coordination Reliability Friction Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove three recurring coordination delays without weakening authority: attribute malformed routes to the expected task during fast resume, emit a complete read-only fallback capsule, and codify safe first-attempt writer plus task-monitor fallbacks.

**Architecture:** RouteBatchReader will keep its global diagnostic strings while recording a task identity beside each malformed-route issue. The resume path will load the exact expected route first, resolve only that task, collect state once, and render the same evidence in pass or fallback form. The executable protocol model will remain the canonical source for fixed-writer launch and task-monitor behavior, with thin synchronized Codex surfaces pinned by prompt-sync tests.

**Tech Stack:** Python 3.10+, standard library dataclasses and regular expressions, Git plumbing already used by RouteBatchReader, pytest, Markdown protocol adapters. No new package.

**Approved Design:** docs/superpowers/specs/2026-07-20-coordination-reliability-friction-reduction-design.md@4729126755f03cba353c03160c1f6bea9cbec054

**Planning Route:** coordination/mailbox/sent/2026-07-20T02-38-51Z-coordinator-to-all-coordination.md@f249c288518ead29d2484e40794671eae2189954

## Global Constraints

- Execute only after a committed Director implementation route names the exact base, owner, allowed paths, assigned non-author Operator, and required reviewer model.
- One Director owns and commits the complete implementation range. Do not run concurrent implementers on these shared files.
- Use RED then GREEN for every behavior change. Record the intended failure before changing production code.
- Preserve coordination/bin/send-event and scripts/mailbox_writer.py byte-for-byte.
- Preserve the .git/protocol-kernel-writer.lock location, O_NOFOLLOW behavior, and all existing writer security checks.
- Keep legacy route aliases readable, but keep legacy routes ineligible for FAST RESUME: PASS.
- Do not rewrite historical mailbox events and do not add a registry, broker, polling journal, event framework, or dependency.
- The task-monitor change specifies Codex behavior only. Local tests must not claim to exercise the external Codex app handler.
- Fast resume, full orientation, and task monitoring grant no mailbox, cursor, lock, merge, push, spend, provider, backend, or product authority.
- Run ordinary Git and Python commands with env -u GIT_INDEX_FILE and stage explicit pathspecs only.
- A different-model, non-author Operator reviews the exact final range. Tests and smoke do not replace that verdict.

## Rollout And Rollback

- Land Tasks 1-4 as sequential local commits under one Director. No behavior-changing range is accepted until the assigned Operator GO is committed and coordinator-reconciled.
- If review finds a defect, preserve the finding and correct it in a new explicit commit; do not amend reviewed history.
- If rollback is separately authorized, revert the implementation commits newest-first. The change creates no schema, registry, service, or migration and therefore requires no data cleanup.

---

## File Responsibility Map

- **scripts/route_lineage.py** — record malformed route-shaped diagnostics with optional task attribution while preserving the existing global issues API.
- **tests/unit/test_route_lineage.py** — prove same-task and unattributed issues fail closed and unrelated issues stay globally visible without entering the task view.
- **scripts/ledger_start_guard.py** — select the exact expected task first, run existing route and target checks against that task, and render the shared evidence capsule.
- **tests/unit/test_ledger_fast_resume.py** — pin expected-task selection, issue scoping, canonical route labels, complete fallback output, and read-only behavior.
- **scripts/codex_protocol_model.py** — define canonical fixed-writer launch rules and the wait-first monitoring fallback.
- **tests/unit/test_protocol_prompt_sync.py** — pin the canonical rules, thin adapter wording, negative boundaries, and canonical route labels.
- **AGENTS.md** — expose the short project-level writer and monitoring consequences.
- **.agents/skills/four-seat-protocol/SKILL.md** — expose fixed-writer first-attempt and fast-resume capsule consequences to every named seat.
- **.agents/skills/seat-coordinator/SKILL.md** — expose wait-first snapshot fallback and no-redispatch behavior to the coordinator.
- **docs/protocol/codex/continuation.md** — document the Codex-native writer and task-tool mechanics.
- **docs/protocol/codex/ledger-cli-adoption.md** — document the canonical target-bound labels and the authority-free full-orientation capsule.

### Task 1: Attribute malformed route diagnostics without changing global lineage behavior

**Files:**

- Modify: scripts/route_lineage.py:62-113 and 497-943
- Modify: tests/unit/test_route_lineage.py:807-825

**Interfaces:**

- Consumes: route filename Path and its exact committed body string.
- Produces: RouteCandidateIssue(message: str, task_id: str | None), RouteBatchReader.issues unchanged as tuple[str, ...], and RouteBatchReader.issues_for_task(task_id: str) -> tuple[str, ...].
- Invariant: issues_for_task includes issues attributed to the requested task plus unattributable issues; it excludes only issues unambiguously attributed to a different task.

- [ ] **Step 1: Add the failing task-attribution test**

Append this focused test beside test_batch_malformed_route_shaped_event_is_visible_to_resume:

~~~python
def test_batch_issue_task_view_keeps_same_and_unattributed_but_not_other(
    tmp_path: Path,
):
    _init_event_repo(tmp_path)
    _root_contract(tmp_path, task="expected-task")
    for timestamp, body in (
        (
            "2026-07-18T09-00-00Z",
            "Task ID: expected-task\nOutcome contract: incomplete",
        ),
        (
            "2026-07-18T10-00-00Z",
            "Task ID: unrelated-task\nOutcome contract: incomplete",
        ),
        (
            "2026-07-18T11-00-00Z",
            "Task ID: first\nTask ID: second\nOutcome contract: incomplete",
        ),
    ):
        _commit_event(
            tmp_path,
            sender="operator",
            recipient="all",
            kind="coordination",
            timestamp=timestamp,
            body=body,
        )

    with route_lineage.RouteBatchReader(tmp_path) as reader:
        routes = reader.load_task_routes("expected-task")
        global_issues = reader.issues
        expected_issues = reader.issues_for_task("expected-task")

    assert len(routes) == 1
    assert any("09-00-00" in issue for issue in expected_issues)
    assert any("11-00-00" in issue for issue in expected_issues)
    assert not any("10-00-00" in issue for issue in expected_issues)
    assert any("10-00-00" in issue for issue in global_issues)
~~~

- [ ] **Step 2: Run the new test and record RED**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py::test_batch_issue_task_view_keeps_same_and_unattributed_but_not_other -q
~~~

Expected: FAIL with AttributeError because RouteBatchReader has no issues_for_task method.

- [ ] **Step 3: Add the structured issue type and conservative task parser**

Add this type after Resolution and these helpers before RouteBatchReader:

~~~python
@dataclass(frozen=True)
class RouteCandidateIssue:
    message: str
    task_id: str | None


def _partial_route_task_id(path: Path, body: str) -> str | None:
    match = _ROUTE_NAME_RE.fullmatch(path.name)
    if match is None:
        return None
    label = (
        "Task-board"
        if match.group("sender") in {"coordinator", "coordinator2"}
        else "Task ID"
    )
    prefix = f"{label}:"
    values = [
        line[len(prefix) :].strip().strip(chr(96))
        for line in body.splitlines()
        if line.startswith(prefix)
    ]
    if len(values) != 1 or not values[0]:
        return None
    value = values[0]
    if value.casefold().startswith("none"):
        return None
    return value
~~~

This parser is deliberately weaker than route validation: it extracts only one exact task field from already-recognized route-shaped bytes and grants no route effectiveness.

- [ ] **Step 4: Record issues through one helper and expose both views**

Change self._issues to list[RouteCandidateIssue], add this method inside RouteBatchReader, and replace all three direct self._issues.append calls in _non_git_candidates and candidate_routes:

~~~python
def _record_issue(self, message: str, *, path: Path, body: str) -> None:
    self._issues.append(
        RouteCandidateIssue(
            message=message,
            task_id=_partial_route_task_id(path, body),
        )
    )
~~~

Use this exact call shape:

~~~python
self._record_issue(
    f"malformed route-shaped event: {path.name}",
    path=path,
    body=body,
)
~~~

For the non-regular-mode branch, keep its existing message and pass the same path and body. Replace the current issues property with:

~~~python
@property
def issues(self) -> tuple[str, ...]:
    return tuple(dict.fromkeys(issue.message for issue in self._issues))

def issues_for_task(self, task_id: str) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            issue.message
            for issue in self._issues
            if issue.task_id in {None, task_id}
        )
    )
~~~

- [ ] **Step 5: Run focused and full route-lineage GREEN**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py::test_batch_issue_task_view_keeps_same_and_unattributed_but_not_other tests/unit/test_route_lineage.py::test_batch_malformed_route_shaped_event_is_visible_to_resume -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q
~~~

Expected: both commands PASS; the full baseline was 39 tests before this task and must increase by the new test without losing any existing case.

- [ ] **Step 6: Commit Task 1**

~~~bash
env -u GIT_INDEX_FILE git add -- scripts/route_lineage.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(protocol): scope malformed route diagnostics"
~~~

### Task 2: Resolve fast resume from the exact expected task

**Files:**

- Modify: scripts/ledger_start_guard.py:95-149 and 726-930
- Modify: tests/unit/test_ledger_fast_resume.py:335-376 and 528-554

**Interfaces:**

- Consumes: one canonical resume_from path@full-SHA reference, selected TargetBinding, and an entered RouteBatchReader.
- Produces: _select_resume_task(...) -> tuple[LineageRoute | None, LineageRoute | None, tuple[str, ...]], where the first route is the exact expected object and the second is the current authoritative same-task object.
- Uses: RouteBatchReader.load_route_ref, load_task_routes, issues_for_task, and route_lineage.resolve_task_routes.
- Invariant: build_resume never calls target-wide resolve_latest_ledger_route.

- [ ] **Step 1: Add RED tests for selection order and issue scoping**

Replace test_live_malformed_candidate_issue_forces_full_orientation with:

~~~python
@pytest.mark.parametrize(
    ("malformed_task", "expected_classification"),
    [
        (
            "demo-fast-resume",
            ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED,
        ),
        (
            "unrelated-task",
            ledger_start_guard.ResumeClassification.FAST_RESUME_PASS,
        ),
    ],
)
def test_malformed_route_issue_is_scoped_to_expected_task(
    tmp_path,
    malformed_task,
    expected_classification,
):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    _commit_event(
        root,
        sender="operator",
        recipient="all",
        kind="coordination",
        minute=1,
        body=f"Task ID: {malformed_task}\nOutcome contract: incomplete",
    )

    result = _resume(root, route_ref)

    assert result.classification is expected_classification
    if malformed_task == "demo-fast-resume":
        assert any(
            reason.startswith("route-candidate-issue:")
            for reason in result.reasons
        )
    else:
        assert not any(
            reason.startswith("route-candidate-issue:")
            for reason in result.reasons
        )
~~~

Replace test_resume_resolves_route_once_and_guard_git_processes_are_bounded with:

~~~python
def test_resume_selects_exact_expected_task_without_target_wide_resolution(
    tmp_path, monkeypatch
):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    original_popen = subprocess.Popen
    git_processes = 0

    def forbidden(*_args, **_kwargs):
        raise AssertionError("resume called target-wide route selection")

    def counted_popen(*args, **kwargs):
        nonlocal git_processes
        command = args[0] if args else kwargs.get("args", ())
        if command and Path(command[0]).name == "git":
            git_processes += 1
        return original_popen(*args, **kwargs)

    monkeypatch.setattr(
        ledger_start_guard,
        "resolve_latest_ledger_route",
        forbidden,
    )
    monkeypatch.setattr(subprocess, "Popen", counted_popen)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    assert git_processes <= 20
~~~

- [ ] **Step 2: Run the two RED tests**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py::test_malformed_route_issue_is_scoped_to_expected_task tests/unit/test_ledger_fast_resume.py::test_resume_selects_exact_expected_task_without_target_wide_resolution -q
~~~

Expected: the unrelated malformed-task case fails because global reader issues contaminate resume, and the selection-order case fails because build_resume calls resolve_latest_ledger_route.

- [ ] **Step 3: Extract the existing target-match predicate**

Add this helper above resolve_latest_ledger_route and use it inside the existing target-wide ordinary-startup resolver:

~~~python
def _route_matches_target(
    route: route_lineage.LineageRoute,
    target: target_binding.TargetBinding,
) -> bool:
    if route.path is None or route.body is None:
        return False
    body_lower = route.body.lower()
    task_lower = (route.task_id or "").lower()
    return (
        any(keyword in task_lower for keyword in target.route_keywords)
        or any(keyword in body_lower for keyword in target.route_keywords)
        or target.path.as_posix() in route.body
    )
~~~

Do not change ordinary build_guard selection semantics beyond calling this shared predicate.

- [ ] **Step 4: Add exact expected-task selection**

Add this helper before build_resume:

~~~python
def _select_resume_task(
    *,
    root: Path,
    target: target_binding.TargetBinding,
    reader: route_lineage.RouteBatchReader,
    resume_from: str,
) -> tuple[
    route_lineage.LineageRoute | None,
    route_lineage.LineageRoute | None,
    tuple[str, ...],
]:
    reasons: list[str] = []
    if not protocol_mailbox.immutable_reference_is_canonical(resume_from):
        return (
            None,
            None,
            ("expected-route-invalid: expected a canonical path@full-commit reference",),
        )
    try:
        expected = reader.load_route_ref(resume_from)
    except (OSError, ValueError) as exc:
        return None, None, (f"expected-route-unreadable: {exc}",)
    if expected.task_id is None:
        return expected, None, ("expected-task-unavailable: route has no task identity",)
    if not _route_matches_target(expected, target):
        reasons.append(
            "expected-task-target-mismatch: route does not identify the selected target"
        )

    routes = reader.load_task_routes(expected.task_id)
    resolution = route_lineage.resolve_task_routes(routes, expected.task_id)
    reasons.extend(
        f"route-candidate-issue: {issue}"
        for issue in reader.issues_for_task(expected.task_id)
    )
    reasons.extend(f"route-state-changed: {issue}" for issue in resolution.issues)
    current = resolution.authoritative
    if current is None:
        reasons.append(
            f"route-state-changed: task {expected.task_id} has no authoritative route"
        )
    else:
        try:
            current = _actionable_route(root, current, reader=reader)
        except RouteResolutionError as exc:
            reasons.append(f"route-state-changed: {exc}")
        if current.route_ref != resume_from:
            reasons.append(
                f"expected-route-mismatch: expected {resume_from}, "
                f"current {current.route_ref or 'unavailable'}"
            )
        if current.body != expected.body:
            reasons.append(
                "expected-route-body-mismatch: exact route bodies differ"
            )
    return expected, current, tuple(dict.fromkeys(reasons))
~~~

- [ ] **Step 5: Reorder build_resume around the helper**

Inside the entered RouteBatchReader:

1. Call _select_resume_task first.
2. Set route = current_route or expected_route so a failed same-task resolution can still render the exact expected route as fallback evidence.
3. Start reasons from selection_reasons.
4. Run _build_guard_from_route only when route is not None; turn its non-base errors into route-guidance-invalid reasons.
5. Parse guidance from route.body, select its worktree or the registered target path, and collect the existing Pipeline, target, and mailbox snapshots exactly once.
6. Remove the old reader.issues loop, old expected-route load, and target-wide resolve_latest_ledger_route call.
7. Set current_route_ref from current_route only; do not label an unresolved expected route as authoritative.

Keep the existing START_GUARD: FAIL path only for binding failures, forbidden roots, wrong kernel, unknown seat, and the ordinary non-resume no-active-route guard.

- [ ] **Step 6: Run Task 2 GREEN and the independent classifier corpus**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py::test_malformed_route_issue_is_scoped_to_expected_task tests/unit/test_ledger_fast_resume.py::test_resume_selects_exact_expected_task_without_target_wide_resolution -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py -q
~~~

Expected: PASS, including test_batch_and_reference_collectors_make_equal_decisions_over_shared_corpus. The pre-change baseline was 38 tests.

- [ ] **Step 7: Commit Task 2**

~~~bash
env -u GIT_INDEX_FILE git add -- scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(protocol): resolve fast resume by expected task"
~~~

### Task 3: Render one complete read-only evidence capsule and standardize new route labels

**Files:**

- Modify: scripts/ledger_start_guard.py:638-723 and build_resume result branches
- Modify: tests/unit/test_ledger_fast_resume.py:556-617 and 733-775

**Interfaces:**

- Consumes: one ResumeEvidence plus the selected TargetBinding.
- Produces: _evidence_capsule_lines(evidence, target_value) -> tuple[str, ...], reused by FAST RESUME: PASS and FULL ORIENTATION REQUIRED.
- Invariant: the renderer only formats already-collected objects; it performs no Git, mailbox, cursor, index, ref, lock, or filesystem read.

- [ ] **Step 1: Add RED coverage for the full-orientation capsule**

Add:

~~~python
def test_legacy_full_orientation_contains_complete_read_only_capsule(tmp_path):
    root, target, _route_ref, _route = _make_lane(tmp_path)
    legacy_ref = _commit_event(
        root,
        sender="coordinator",
        recipient="all",
        kind="coordination",
        minute=1,
        body=(
            "Task-board: demo-legacy-only\n"
            f"Target worktree: {target.as_posix()}\n"
            f"Accepted target HEAD: {_git(target, 'rev-parse', 'HEAD')}\n"
            "\n## Target Allowed Paths\n"
            "- tracked.txt"
        ),
    )
    before = _snapshot_bytes(root)

    result = _resume(root, legacy_ref)

    after = _snapshot_bytes(root)
    capsule = "\n".join(result.lines)
    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    for expected in (
        f"Expected route ref: {legacy_ref}",
        f"Current route ref: {legacy_ref}",
        "Route body:",
        "Task ID: demo-legacy-only",
        "Revision: (legacy)",
        "Current owners: (none)",
        "Immutable finding refs: (none)",
        "Routed outcome: (legacy route body governs)",
        "Pipeline HEAD:",
        "Pipeline branch:",
        "Pipeline dirty:",
        f"Target worktree: {target.as_posix()}",
        "Target HEAD:",
        "Target dirty:",
        "Mailbox cursor:",
        "Mailbox availability: available",
        "Unread refs: (none)",
        "Allowed paths: tracked.txt",
        "Reasons:",
        "Ordinary startup actions:",
        "External effects authorized: none by fast resume",
    ):
        assert expected in capsule
    assert after == before
~~~

- [ ] **Step 2: Make canonical labels the default test fixture and pin aliases**

Change _route_body to emit:

~~~python
allowed = (
    "\n## Target Allowed Paths\n"
    + "".join(f"- {path}\n" for path in allowed_paths)
    + allowed_section_suffix
    + "\n## Route Metadata\n"
)
~~~

Add:

~~~python
def test_legacy_route_guidance_aliases_remain_parseable(tmp_path):
    target = tmp_path / "target"
    guidance = ledger_start_guard.parse_route_guidance_body(
        f"Route worktree: {target}\n"
        f"Target reviewed head: {'a' * 40}\n"
        "\n## Allowed Paths\n"
        "- legacy/path.py\n"
    )

    assert guidance == ledger_start_guard.RouteGuidance(
        worktree=target.as_posix(),
        accepted_target_head="a" * 40,
        allowed_paths=("legacy/path.py",),
    )
~~~

- [ ] **Step 3: Run the capsule test and record RED**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py::test_legacy_full_orientation_contains_complete_read_only_capsule tests/unit/test_ledger_fast_resume.py::test_legacy_route_guidance_aliases_remain_parseable -q
~~~

Expected: the legacy-alias test passes and the capsule test fails because FULL ORIENTATION REQUIRED currently prints only reasons and startup actions.

- [ ] **Step 4: Add the shared pure renderer**

Add this renderer before _full_orientation:

~~~python
def _evidence_capsule_lines(
    evidence: ResumeEvidence,
    target_value: target_binding.TargetBinding,
) -> tuple[str, ...]:
    route = evidence.route
    target = evidence.target
    owners = (
        ", ".join(route.owners)
        if route is not None and route.owners
        else "(none)"
    )
    findings = (
        ", ".join(route.finding_refs)
        if route is not None and route.finding_refs
        else "(none)"
    )
    unread = (
        ", ".join(evidence.mailbox.unread_refs)
        if evidence.mailbox.unread_refs
        else "(none)"
    )
    allowed = (
        ", ".join(evidence.guidance.allowed_paths)
        if evidence.guidance.allowed_paths
        else "(none)"
    )
    lines = [
        f"Expected route ref: {evidence.expected_route_ref}",
        f"Current route ref: {evidence.current_route_ref or '(unavailable)'}",
    ]
    if route is not None and route.body is not None:
        lines.extend(("Route body:", route.body))
    else:
        lines.append("Route body: (unavailable)")
    lines.extend(
        (
            f"Task ID: {route.task_id if route and route.task_id else '(unavailable)'}",
            f"Revision: {route.revision if route and route.revision is not None else '(legacy)'}",
            f"Current owners: {owners}",
            f"Immutable finding refs: {findings}",
            f"Routed outcome: {route.outcome if route and route.outcome else '(legacy route body governs)'}",
            f"Pipeline HEAD: {evidence.pipeline.head or '(unavailable)'}",
            f"Pipeline branch: {evidence.pipeline.branch or '(detached)'}",
            f"Pipeline dirty: {_format_dirty(evidence.pipeline)}",
            f"Target name: {target_value.name}",
            f"Target registered repo: {target_value.repository}",
            f"Target worktree: {target.root.as_posix() if target else '(unavailable)'}",
            f"Target HEAD: {target.head if target and target.head else '(unavailable)'}",
            f"Target dirty: {_format_dirty(target) if target else '(unavailable)'}",
            f"Mailbox cursor: {evidence.mailbox.cursor or '(unavailable)'}",
            "Mailbox availability: "
            + (evidence.mailbox.unavailable_reason or "available"),
            f"Unread refs: {unread}",
            f"Route base: {evidence.guidance.base or '(none)'}",
            f"Allowed paths: {allowed}",
        )
    )
    return tuple(lines)
~~~

- [ ] **Step 5: Reuse the renderer in both classifications**

Extend _full_orientation with evidence: ResumeEvidence | None = None and
target_value: target_binding.TargetBinding | None = None. After the Reasons
block and before Ordinary startup actions, append an Orientation capsule
heading and _evidence_capsule_lines only when both values exist.

Replace the hand-built fields in _fast_capsule with:

~~~python
lines = (
    ResumeClassification.FAST_RESUME_PASS.value,
    f"Seat: {seat}",
    *_evidence_capsule_lines(evidence, target_value),
    "External effects authorized: none by fast resume",
)
~~~

When build_resume has created ResumeEvidence and evidence.reasons is nonempty, call _full_orientation with that exact evidence and target_value=target. Do not recollect snapshots inside either renderer.

- [ ] **Step 6: Run GREEN, mutation safety, and grammar coverage**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py::test_legacy_full_orientation_contains_complete_read_only_capsule tests/unit/test_ledger_fast_resume.py::test_fast_capsule_contains_exact_body_state_ownership_and_no_effect_authority tests/unit/test_ledger_fast_resume.py::test_resume_collection_mutates_no_cursor_index_ref_lock_or_worktree_byte tests/unit/test_ledger_fast_resume.py::test_legacy_route_guidance_aliases_remain_parseable tests/unit/test_ledger_fast_resume.py::test_route_guidance_is_strict_and_never_infers_path_scope_from_prose -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py -q
~~~

Expected: PASS. FULL ORIENTATION REQUIRED remains exit zero and never prints BLOCKED.

- [ ] **Step 7: Commit Task 3**

~~~bash
env -u GIT_INDEX_FILE git add -- scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): emit full orientation evidence capsule"
~~~

### Task 4: Pin fixed-writer launch and task-monitor fallback in the executable model

**Files:**

- Modify: scripts/codex_protocol_model.py:386-397 and 653-657
- Modify: tests/unit/test_protocol_prompt_sync.py:315-405
- Modify: AGENTS.md:87-123
- Modify: .agents/skills/four-seat-protocol/SKILL.md:17-44
- Modify: .agents/skills/seat-coordinator/SKILL.md:21-47
- Modify: docs/protocol/codex/continuation.md:22-93
- Modify: docs/protocol/codex/ledger-cli-adoption.md:45-75

**Interfaces:**

- Produces: FIXED_WRITER_LAUNCH_REFERENCE, FIXED_WRITER_LAUNCH_RULES, render_fixed_writer_launch(), and an expanded AUTOMATIC_TASK_ROUTING_RULES tuple.
- Adapter contract: each synced surface cites the canonical model once and states only Codex mechanics and authority consequences.
- Invariant: a missing wait handler changes observation transport only; it never creates a second dispatch identity.

- [ ] **Step 1: Add RED model and adapter tests**

Add these constants beside the existing surface lists:

~~~python
FIXED_WRITER_LAUNCH_REFERENCE = (
    "Codex Fixed-Writer Launch: scripts/codex_protocol_model.py"
)
FIXED_WRITER_LAUNCH_SURFACES = (
    "AGENTS.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    "docs/protocol/codex/continuation.md",
)
~~~

Add:

~~~python
def test_fixed_writer_launch_model_is_scoped_and_fail_closed() -> None:
    rendered = _compact(model.render_fixed_writer_launch())

    assert model.FIXED_WRITER_LAUNCH_RULES == (
        "Publication authority must already name the exact sender, recipient, kind, target, and scope before Codex launches a writer.",
        "In the known managed Pipeline checkout where the default sandbox cannot open the Git-common-dir writer fence, launch the exact coordination/bin/send-event command with the supported scoped execution profile on the first attempt.",
        "Limit any reusable approval prefix to coordination/bin/send-event plus the concrete sender seat; never grant a generic shell, Python, Git, or filesystem prefix.",
        "If that writer attempt fails, report the exact path, syscall, and error; do not direct-edit the mailbox, use an alternate writer, inject TMPDIR, or weaken the sandbox or fence.",
        "Outside that known context, use ordinary execution and never infer scoped-profile authority from repository prose.",
    )
    for phrase in (
        "authority must already",
        "first attempt",
        "concrete sender seat",
        "exact path, syscall, and error",
        "do not direct-edit",
        "ordinary execution",
    ):
        assert phrase.casefold() in rendered.casefold()


def test_fixed_writer_launch_adapters_are_thin_and_synced() -> None:
    required = (
        "already-authorized exact fixed-writer action",
        "known managed Pipeline checkout",
        "supported scoped execution profile on the first attempt",
        "no alternate writer",
        "grants no publication authority",
        "outside that known context, use ordinary execution",
    )
    for path in FIXED_WRITER_LAUNCH_SURFACES:
        text = _compact(_read(path).replace(chr(96), ""))
        assert text.count(FIXED_WRITER_LAUNCH_REFERENCE) == 1, path
        for phrase in required:
            assert phrase.casefold() in text.casefold(), (path, phrase)
~~~

Update the automatic-routing tests to require these exact mechanics:

~~~python
for phrase in (
    "wait_threads",
    "per-target cursor",
    "missing or unavailable wait handler",
    "read_thread(turnLimit=1, includeOutputs=false)",
    "bounded cadence",
    "latest turn or message identity",
    "at most one discovery",
    "never redispatch",
    "approval or user-input request",
):
    assert phrase.casefold() in rendered.casefold(), phrase
~~~

Also make the adapter test require wait-first, bounded read-only snapshot, preserved dispatch identity, and no redispatch.

- [ ] **Step 2: Run prompt-sync RED**

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -k "fixed_writer_launch or automatic_task_routing" -q
~~~

Expected: FAIL because render_fixed_writer_launch and the new canonical rules do not exist.

- [ ] **Step 3: Add canonical fixed-writer rules and renderer**

Add to scripts/codex_protocol_model.py:

~~~python
FIXED_WRITER_LAUNCH_REFERENCE = (
    "Codex Fixed-Writer Launch: scripts/codex_protocol_model.py"
)
FIXED_WRITER_LAUNCH_RULES = (
    "Publication authority must already name the exact sender, recipient, kind, target, and scope before Codex launches a writer.",
    "In the known managed Pipeline checkout where the default sandbox cannot open the Git-common-dir writer fence, launch the exact coordination/bin/send-event command with the supported scoped execution profile on the first attempt.",
    "Limit any reusable approval prefix to coordination/bin/send-event plus the concrete sender seat; never grant a generic shell, Python, Git, or filesystem prefix.",
    "If that writer attempt fails, report the exact path, syscall, and error; do not direct-edit the mailbox, use an alternate writer, inject TMPDIR, or weaken the sandbox or fence.",
    "Outside that known context, use ordinary execution and never infer scoped-profile authority from repository prose.",
)


def render_fixed_writer_launch() -> str:
    """Return the Codex fixed-writer launch contract."""
    return FIXED_WRITER_LAUNCH_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in FIXED_WRITER_LAUNCH_RULES
    )
~~~

Add render_fixed_writer_launch() to render_surface_summary immediately after
render_automatic_task_routing(), so the ordinary executable model output
exposes the canonical rule. Extend the RED test with:

~~~python
assert FIXED_WRITER_LAUNCH_REFERENCE in model.render_surface_summary()
~~~

- [ ] **Step 4: Expand automatic monitoring rules without adding runtime state**

Replace AUTOMATIC_TASK_ROUTING_RULES with this exact tuple and make the
existing exact-tuple test match it:

~~~python
AUTOMATIC_TASK_ROUTING_RULES = (
    "For a committed immutable trigger naming the next concrete seat, use Codex task tools before returning a prompt to the user.",
    "The dispatch identity is the trigger path and full commit, assigned seat, Pipeline checkout, and for review the exact base/head and required reviewer model.",
    "If the same dispatch identity is already in progress, monitor it; if it completed, reconcile its committed artifact instead of resending it.",
    "Reuse one unambiguous compatible seat task; if none exists or candidates are stale, incompatible, or ambiguous, automatically create a fresh local task in the saved Pipeline project.",
    "Never ask the user to relay a seat prompt while Codex task tools are available; send the exact trigger and reconcile its committed result directly.",
    "If discovery or dispatch tools are unavailable before a trigger is sent, preserve the exact trigger and report one concrete tooling blocker without asking the user to relay it.",
    "After one exact trigger is sent, monitor with wait_threads and preserve its per-target cursor.",
    "Only when wait_threads reports a missing or unavailable wait handler, read the same thread with read_thread(turnLimit=1, includeOutputs=false).",
    "Snapshot monitoring uses bounded cadence, compares the cursor and latest turn or message identity, and reports only changes.",
    "If both monitoring transports fail, preserve the dispatch identity and perform at most one normal discovery/deduplication refresh; unavailable or ambiguous state becomes one concrete tooling blocker.",
    "Monitoring failure never resends the trigger, creates a replacement task, or changes seats; leave an approval or user-input request for the user.",
    "A concrete live-seat Codex task may exercise only its committed authority; parent-scoped subagents do not publish live-seat events or formal GO, and task routing grants no external-effect authority.",
)
~~~

Do not add a persistent task registry or local polling journal.

- [ ] **Step 5: Synchronize the thin adapter capsules**

Insert this exact fixed-writer capsule once in AGENTS.md, four-seat-protocol, and continuation:

~~~text
Codex Fixed-Writer Launch: scripts/codex_protocol_model.py
For an already-authorized exact fixed-writer action in the known managed
Pipeline checkout, use the supported scoped execution profile on the first
attempt. Scope any reusable prefix to coordination/bin/send-event plus the
sender seat. This grants no publication authority; on failure report the exact
writer error, use no alternate writer, and do not weaken the sandbox or fence.
Outside that known context, use ordinary execution and infer no authority from
this guidance.
~~~

Extend the Automatic Seat-Task Routing capsule once in AGENTS.md, seat-coordinator, and continuation:

~~~text
After one exact trigger, monitor with wait_threads and its per-target cursor.
Only a missing or unavailable wait handler permits a bounded read-only
read_thread(turnLimit=1, includeOutputs=false) snapshot of the same task.
Deduplicate by cursor and latest turn or message identity. If both transports
fail, preserve the dispatch identity, perform at most one discovery refresh,
and report ambiguity as one tooling blocker. Monitoring failure never
redispatches, replaces the task, or changes seats.
Leave an approval or user-input request for the user.
~~~

Extend the fast-resume paragraphs in AGENTS.md, four-seat-protocol, continuation, and ledger-cli-adoption with one sentence:

~~~text
When fast resume falls back after collecting route and state evidence, full
orientation includes that read-only orientation capsule without a second
collection pass or any new authority.
~~~

Add this canonical grammar only to ledger-cli-adoption:

~~~text
New target-bound routes use Target worktree, Accepted target HEAD, and
## Target Allowed Paths. The parser retains historical aliases only for
committed compatibility.
~~~

- [ ] **Step 6: Complete prompt-sync assertions and run GREEN**

Add a test that checks the canonical grammar in ledger-cli-adoption and verifies that every FAST_RESUME_ADAPTER_SURFACES entry contains read-only orientation capsule. Preserve the existing negative checks against duplicated internal reason tokens.

Run:

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py -q
~~~

Expected: both commands PASS. The prompt-sync baseline was 38 tests and must
increase by the new fixed-writer and grammar tests.

- [ ] **Step 7: Commit Task 4**

~~~bash
env -u GIT_INDEX_FILE git add -- scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py AGENTS.md .agents/skills/four-seat-protocol/SKILL.md .agents/skills/seat-coordinator/SKILL.md docs/protocol/codex/continuation.md docs/protocol/codex/ledger-cli-adoption.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): codify writer and task-monitor fallbacks"
~~~

### Task 5: Verify the integrated range and request independent review

**Files:**

- Verify: every path in the File Responsibility Map.
- Confirm unchanged: coordination/bin/send-event, scripts/mailbox_writer.py, pyproject.toml, uv.lock, and every product repository.
- Publish only under the future implementation route: one committed verify-request through coordination/bin/send-event.

**Interfaces:**

- Consumes: implementation_base, defined as the exact full parent SHA in the committed Director implementation route; reviewed_head, defined as the final full SHA after Tasks 1-4; and verify_request_path, defined as the exact generated filename printed by the fixed writer.
- Produces: one canonical verify-request binding implementation_base..reviewed_head, the Director author seat/model, assigned non-author Operator and model requirement, exact allowed paths, finding refs, and commands below.

- [ ] **Step 1: Run every focused suite from a clean command environment**

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_mailbox_writer.py -q
~~~

Expected: all five commands PASS with zero failures.

- [ ] **Step 2: Run governance smoke**

~~~bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
~~~

Expected: PROJECT SMOKE OK, ceremony check PASS, placeholder check PASS, GO-schema check PASS, mechanism-ledger check PASS, and final OK.

- [ ] **Step 3: Audit the exact range and abuse classes**

Run git diff --check over implementation_base..reviewed_head, list the exact changed paths, and verify the two protected writer files plus dependency manifests have no diff. Inspect the range against these questions:

- Can a malformed route attributed to the expected task still pass?
- Can an unattributable malformed route pass?
- Can a malformed route attributed only to another task change the expected-task classification?
- Can a historical or forked same-task route become authoritative?
- Can the capsule trigger a second collection or mutation?
- Can writer guidance grant authority, generic escalation, direct mailbox editing, an alternate writer, TMPDIR injection, or fence weakening?
- Can wait-handler failure cause a second trigger, replacement task, seat change, or user relay?
- Do all new target-bound docs name Target worktree, Accepted target HEAD, and Target Allowed Paths while legacy aliases still parse?

Expected: only the eleven implementation paths in the File Responsibility Map changed; every answer is no except that historical aliases remain readable and same-task or unattributable defects deliberately force full orientation.

- [ ] **Step 4: Refresh shared-tree and route gates**

~~~bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py --git-root .
~~~

Also validate the then-current committed implementation route with scripts/protocol_capacity_board.py --wave 2 --validate-route and its exact mailbox path.

Expected: no unrelated dirty or staged paths, coordination clean apart from informational unread counts, and route valid true with no blockers.

- [ ] **Step 5: Publish and commit the canonical verify-request**

Use the fixed coordination/bin/send-event writer under the exact authority and supported profile in the implementation route. Bind:

- Reviewed base: implementation_base.
- Reviewed head: reviewed_head.
- Outcome: the three accepted reliability corrections.
- Author: the routed Director seat and its actual model.
- Assigned reviewer: the routed non-author Operator seat and required different model.
- Allowed paths: exactly the File Responsibility Map.
- Finding refs: every preserved immutable finding or none.
- Verification commands: the six commands from Steps 1-2.
- Adversarial question: whether unrelated malformed history, writer escalation wording, or monitoring failure can bypass task scoping, authority, or dispatch deduplication.

Read back the generated event and validate its exact fields. Copy the writer's exact generated filename into the task-specific shell variable verify_request_path; do not use a directory path, wildcard, or reconstructed timestamp. Stage only that generated path, then commit with:

~~~bash
env -u GIT_INDEX_FILE git commit -m "review(operator): request coordination reliability verification" -- "$verify_request_path"
~~~

Do not push, merge, consume a cursor, launch a provider, or issue a verdict.

- [ ] **Step 6: Stop for the assigned Operator**

Route the committed verify-request to the assigned different-model Operator through the automatic seat-task mechanism. The Operator independently chooses sufficient evidence and alone issues GO, NITS, or FAIL against implementation_base..reviewed_head. Coordinator reconciliation happens only after that committed verdict.
