# Abandoned Takeover Outcome Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an abandoned-owner takeover from becoming authoritative when its successor route changes the parent outcome.

**Architecture:** Keep `scripts/codex_protocol_model.py` as the sole policy authority. The route-lineage adapter will expose the candidate-versus-parent outcome delta to the existing `OwnershipChange` guard, so unchanged takeovers remain valid and changed-outcome takeovers fail closed.

**Tech Stack:** Python 3, frozen dataclasses, pytest, Git-backed committed mailbox fixtures.

## Global Constraints

- Binding design: `docs/superpowers/specs/2026-07-21-abandoned-takeover-outcome-integrity-design.md@a1655ec77163e486af2f6a546ce266d6e20cc3e5`.
- Binding finding: `audit-5-abandoned-takeover-outcome-integrity`, preserved by the design reference above.
- Modify only `scripts/route_lineage.py` and `tests/unit/test_route_lineage.py` in the implementation range.
- Do not change `scripts/codex_protocol_model.py`; its existing abandoned-takeover guard is canonical and already correct.
- Add no mailbox, envelope, route-body, ownership schema, fallback, exception type, dependency, configuration, or refactor.
- An unchanged abandoned takeover remains effective; an outcome-changing abandoned takeover is ineffective and leaves the task without an authoritative successor.
- Use TDD: capture the current wrong authority result as RED before changing production code.
- The Coordinator does not implement this behavior change. A routed Director owns the implementation and exact range.
- A distinct non-author Operator seat using a different model must review the actual implementation range and disposition the binding finding.
- No merge, push, cursor consumption, lock action, provider launch, paid spend, or other external effect is authorized.

---

### Task 1: Preserve the parent outcome across abandoned takeovers

**Files:**
- Modify: `tests/unit/test_route_lineage.py:287-310`
- Modify: `tests/unit/test_route_lineage.py:650-711`
- Modify: `scripts/route_lineage.py:473-493`
- Test: `tests/unit/test_route_lineage.py`
- Regression support: `tests/unit/test_autonomous_seat_contract.py`

**Interfaces:**
- Consumes: `route_lineage.RouteBatchReader.load_task_routes(task_id)`, `route_lineage.resolve_task_routes(routes, task_id)`, `codex_protocol_model.OwnershipChange.outcome`, and the existing `_abandoned_takeover_is_effective()` policy.
- Produces: no new public API; the `dispatch-claim` adapter supplies `str | None` outcome delta semantics identical to the normal proposal adapter.

- [ ] **Step 1: Make the committed-route fixture express an explicit outcome**

Replace `_autonomous_body` in `tests/unit/test_route_lineage.py` with this backward-compatible helper. Existing callers retain the current outcome through the default argument.

```python
def _autonomous_body(
    *,
    task: str,
    parent: str = "(none)",
    revision: int = 0,
    previous: str = "(none)",
    owners: str = "director",
    proposal: str = "self-candidate",
    acceptances: str = "self-candidate",
    findings: str = "(none)",
    outcome: str = "deliver tested route behavior",
) -> str:
    return "\n".join(
        (
            f"Task ID: {task}",
            f"Outcome contract: {outcome}",
            f"Parent contract: {parent}",
            f"Contract revision: {revision}",
            f"Previous owners: {previous}",
            f"Owners: {owners}",
            f"Proposal ref: {proposal}",
            f"Acceptance refs: {acceptances}",
            f"Finding refs: {findings}",
        )
    )
```

- [ ] **Step 2: Replace the existing takeover test with positive and negative cases**

Replace `test_batch_takeover_uses_exact_statement_and_ancestry_proof` with this parametrized test. It keeps the existing valid-takeover assertion and adds the outcome-changing regression without duplicating the committed evidence setup.

```python
@pytest.mark.parametrize(
    ("outcome", "expected_owner"),
    (
        ("deliver tested route behavior", ("operator",)),
        ("silently changed takeover outcome", None),
    ),
)
def test_batch_takeover_preserves_parent_outcome(
    tmp_path: Path,
    outcome: str,
    expected_owner: tuple[str, ...] | None,
):
    _init_event_repo(tmp_path)
    _, parent_ref = _root_contract(tmp_path, task="takeover-task")
    _, evidence_ref = _commit_event(
        tmp_path,
        sender="operator",
        recipient="all",
        kind="dispatch-claim",
        timestamp="2026-07-18T10-00-00Z",
        body="\n".join(
            (
                "Task ID: takeover-task",
                f"Parent contract: {parent_ref}",
                "Contract revision: 1",
                "Observed at: 2026-07-18T10:00:00Z",
                "Fresh work state: no fresh work",
                "Lock state: no active lock",
                "Finding refs: (none)",
            )
        ),
    )
    _, confirmation_ref = _commit_event(
        tmp_path,
        sender="operator2",
        recipient="operator",
        kind="acknowledgement",
        timestamp="2026-07-18T10-01-00Z",
        body="\n".join(
            (
                "Task ID: takeover-task",
                f"Parent contract: {parent_ref}",
                "Contract revision: 1",
                "Proposed owner: operator",
                f"Takeover claim ref: {evidence_ref}",
                "Observed at: 2026-07-18T10:00:00Z",
                "Finding refs: (none)",
            )
        ),
    )
    _commit_event(
        tmp_path,
        sender="operator",
        recipient="all",
        kind="coordination",
        timestamp="2026-07-18T10-02-00Z",
        body=_autonomous_body(
            task="takeover-task",
            parent=parent_ref,
            revision=1,
            previous="director",
            owners="operator",
            proposal=evidence_ref,
            acceptances=confirmation_ref,
            outcome=outcome,
        ),
    )

    with route_lineage.RouteBatchReader(tmp_path) as reader:
        routes = reader.load_task_routes("takeover-task")

    resolution = route_lineage.resolve_task_routes(routes, "takeover-task")
    if expected_owner is not None:
        assert resolution.authoritative is not None
        assert resolution.authoritative.owners == expected_owner
        assert resolution.issues == ()
    else:
        assert resolution.authoritative is None
        assert resolution.winner is None
        assert any(
            "ownership evidence is ineffective" in issue
            for issue in resolution.issues
        )
```

- [ ] **Step 3: Run the new selector and confirm RED against the current adapter**

Run from the Pipeline root:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py::test_batch_takeover_preserves_parent_outcome -q
```

Expected: `1 failed, 1 passed`. The changed-outcome case must fail specifically because `resolution.authoritative` is the Operator successor instead of `None`. A fixture parse failure, missing committed reference, or unrelated exception is not acceptable RED evidence.

- [ ] **Step 4: Expose the outcome delta to the canonical model**

In the `proposal_event.kind == "dispatch-claim"` branch of `_validate_committed_autonomous`, add the outcome field to the existing `OwnershipChange` constructor immediately after `finding_refs`:

```python
            finding_refs=candidate.finding_refs,
            outcome=(candidate.outcome if candidate.outcome != parent.outcome else None),
            abandoned_takeover=True,
```

Do not add a separate precheck. The existing canonical model must decide effectiveness.

- [ ] **Step 5: Run the new selector and confirm GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py::test_batch_takeover_preserves_parent_outcome -q
```

Expected: `2 passed`. The unchanged case remains authoritative and the changed-outcome case reports ineffective ownership evidence with no authoritative successor.

- [ ] **Step 6: Run the complete focused protocol verification**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py \
  tests/unit/test_autonomous_seat_contract.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: the pytest command reports `74 passed`; Pipeline smoke exits zero with every check passing.

- [ ] **Step 7: Verify scope and create one implementation commit**

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git diff -- scripts/route_lineage.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git add -- scripts/route_lineage.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "fix(protocol): preserve abandoned takeover outcome"
```

Expected staged manifest before commit:

```text
M	scripts/route_lineage.py
M	tests/unit/test_route_lineage.py
```

Do not stage the design, plan, mailbox artifacts, or unrelated peer work into the implementation commit.

- [ ] **Step 8: Prepare the immutable independent-review handoff**

Run:

```bash
env -u GIT_INDEX_FILE git show --format=fuller --name-status --stat -1
env -u GIT_INDEX_FILE git status --short --branch
```

The Director's verification request must bind:

- the actual implementation base and head;
- author seat and system-visible model;
- one assigned non-author Operator seat using a different model;
- design finding reference `docs/superpowers/specs/2026-07-21-abandoned-takeover-outcome-integrity-design.md@a1655ec77163e486af2f6a546ce266d6e20cc3e5`;
- RED evidence from Step 3 and GREEN evidence from Steps 5 and 6; and
- the exact two-file implementation manifest.

The Operator independently chooses sufficient evidence and issues GO, NITS, or FAIL on the actual range. This plan grants no merge or push authority.
