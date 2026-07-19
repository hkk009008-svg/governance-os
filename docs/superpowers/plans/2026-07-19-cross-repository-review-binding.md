# Cross-Repository Review Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let one canonical compact-pair request and report bind an exact Git range in a routed repository outside Pipeline without changing legacy Pipeline-local reviews or granting new authority.

**Architecture:** Keep the request and report artifacts in Pipeline, add one optional `Reviewed repository` identity field, and resolve only the reviewed base/head in that canonical target Git worktree. The request remains bound to its Pipeline trigger commit; the report must reproduce the request's repository/base/head tuple exactly, and all path, commit, ancestry, identity, finding, evidence, and model checks fail closed.

**Tech Stack:** Python 3 standard library, Git CLI with sanitized `GIT_*` environment, pytest, Markdown protocol surfaces, Pipeline fixed mailbox writer.

## Global Constraints

- Approved design: `docs/superpowers/specs/2026-07-19-cross-repository-review-binding-design.md@8cba82a6cc0e1ab05dde679bc9830e2f4f50b3dd`.
- Preserve existing Pipeline-local and frozen historical request/report behavior when `Reviewed repository` is absent.
- Require the field in both artifacts for a cross-repository review and compare its exact committed text; never infer or reconstruct it from auxiliary prose.
- Accept only an absolute, normalized, existing, non-symlinked Git worktree root whose system-derived top level equals the field.
- Resolve full lowercase base/head commits and strict ancestry in the request-bound reviewed repository with replacement objects disabled and inherited `GIT_*` variables removed.
- Keep the fixed Pipeline request `path@trigger-commit` as the request identity. Do not invent cross-repository trigger ancestry.
- Add no broker, registry, approval token, receipt, scheduler, daemon, target mutation, or external-effect authority.
- Do not modify evidence-ledger, start services, access a database, install dependencies, use real data, push, merge, consume cursors, claim locks, book, spend, deploy, reset, rebase, amend, or clean peer work.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest; stage only explicit routed paths.
- One Director owns the shared implementation paths. A distinct non-author Operator on a different model reviews the final actual range.

---

### Task 1: Bind and validate the reviewed repository

**Files:**

- Modify: `scripts/compact_pair_loop.py:44-405`
- Modify: `tests/unit/test_compact_pair_loop.py:29-590`
- Modify: `tests/unit/test_coordination_tooling.py:43-190`

**Interfaces:**

- Consumes: committed Pipeline request path and trigger commit; optional exact `Reviewed repository` field; `Reviewed base`; `Reviewed head`.
- Produces: `VerifyRequest.reviewed_repository: str | None`, `VerificationReport.reviewed_repository: str | None`, `_optional_one(lines, prefix, label) -> str | None`, and `_reviewed_root(pipeline_root, repository_field) -> Path`.
- Invariant: `None` means Pipeline root. A non-`None` value is the exact canonical absolute path carried by both request and report.

- [ ] **Step 1: Extend the test text builders without changing their default bytes**

Add one helper and keyword parameter to both builders in `tests/unit/test_compact_pair_loop.py`:

```python
def _reviewed_repository_line(value: str | None) -> str:
    return "" if value is None else f"Reviewed repository: {value}\n"


def _request_text(
    base: str,
    head: str,
    *,
    reviewed_repository: str | None = None,
    author_seat: str = "director",
    author_model: str = "gpt-5.6-sol",
    assigned_operator: str = "operator",
    finding_refs: tuple[str, ...] = (FINDING_A,),
) -> str:
    return f"""\
# Pair seat -> Operator: verify outcome

**When:** 2026-07-18T08:00:00Z · **From:** {author_seat} (online)

Event type: verify-request
{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
Reviewed base: {base}
Author seat: {author_seat}
Author model: {author_model}
Assigned operator: {assigned_operator}

## Outcome

The committed change satisfies the routed maintenance outcome.

{_bullet_section("Finding Refs", finding_refs)}
Cursor at send: 0
"""
```

Give `_report_text` the same `reviewed_repository: str | None = None` keyword and insert:

```python
{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
```

The default `None` path must keep all existing fixtures Pipeline-local.

- [ ] **Step 2: Add a configurable two-repository fixture and positive binding test**

Import `Callable` from `collections.abc`, then add this focused fixture beside
`_repo`:

```python
_DEFAULT_REPOSITORY = object()


def _cross_repo(
    tmp_path: Path,
    *,
    repository_value: object = _DEFAULT_REPOSITORY,
    transform_request: Callable[[str], str] = lambda text: text,
    range_values: Callable[[str, str], tuple[str, str]] = lambda base, head: (base, head),
) -> tuple[Path, Path, str, str, str]:
    pipeline = tmp_path / "pipeline"
    pipeline.mkdir()
    _git(pipeline, "init", "-q")
    _git(pipeline, "config", "user.name", "Compact Pair Test")
    _git(pipeline, "config", "user.email", "compact-pair@example.invalid")
    (pipeline / "README.md").write_text("pipeline\n", encoding="utf-8")
    _git(pipeline, "add", ".")
    _git(pipeline, "commit", "-q", "-m", "chore: pipeline base")

    target = tmp_path / "target"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.name", "Compact Pair Test")
    _git(target, "config", "user.email", "compact-pair@example.invalid")
    (target / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(target, "add", ".")
    _git(target, "commit", "-q", "-m", "chore: target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "feat: target candidate")
    head = _git(target, "rev-parse", "HEAD")

    if repository_value is _DEFAULT_REPOSITORY:
        reviewed_repository: str | None = target.as_posix()
    elif callable(repository_value):
        reviewed_repository = repository_value(target)
    else:
        assert repository_value is None or isinstance(repository_value, str)
        reviewed_repository = repository_value
    reviewed_base, reviewed_head = range_values(base, head)

    request = pipeline / REQUEST_PATH
    request.parent.mkdir(parents=True)
    request.write_text(
        transform_request(
            _request_text(
                reviewed_base,
                reviewed_head,
                reviewed_repository=reviewed_repository,
            )
        ),
        encoding="utf-8",
    )
    _git(pipeline, "add", REQUEST_PATH)
    _git(pipeline, "commit", "-q", "-m", "coord: request target review")
    return pipeline, target, base, head, _git(pipeline, "rev-parse", "HEAD")
```

Add the positive and omission tests:

```python
def test_cross_repository_request_and_report_bind_exact_target_range(
    tmp_path: Path,
) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=target.as_posix(),
        ),
    )

    assert request.reviewed_repository == target.as_posix()
    assert report.reviewed_repository == target.as_posix()
    assert pair.validate_report(root, report) == []


def test_target_commits_without_reviewed_repository_fail_in_pipeline(
    tmp_path: Path,
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=None
    )

    with pytest.raises(pair.CompactPairError, match="Git commit or path validation failed"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)
```

- [ ] **Step 3: Add adversarial repository-identity tests**

Add parameterized coverage that edits the request before its trigger commit and proves each input fails:

```python
@pytest.mark.parametrize(
    ("repository_value", "message"),
    (
        ("target", "absolute"),
        ("/tmp/../tmp/target", "normalized"),
        ("/definitely/missing/compact-pair-target", "repository"),
    ),
)
def test_reviewed_repository_rejects_noncanonical_or_missing_paths(
    tmp_path: Path, repository_value: str, message: str
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=repository_value
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)
```

Add complete stateful path tests:

```python
@pytest.mark.parametrize(
    ("case", "message"),
    (("symlink", "symlink"), ("nested", "Git worktree root")),
)
def test_reviewed_repository_rejects_symlink_and_nested_worktree_path(
    tmp_path: Path, case: str, message: str
) -> None:
    def invalid_repository(target: Path) -> str:
        if case == "symlink":
            link = target.parent / "target-link"
            link.symlink_to(target, target_is_directory=True)
            return link.as_posix()
        nested = target / "nested"
        nested.mkdir()
        return nested.as_posix()

    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=invalid_repository
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)
```

Add duplicate-header cases before the valid header:

```python
@pytest.mark.parametrize(
    "duplicate",
    ("Reviewed repository:\n", " Reviewed repository :   \n", "reviewed REPOSITORY: spoofed\n"),
)
def test_reviewed_repository_rejects_blank_malformed_or_duplicate_header(
    tmp_path: Path, duplicate: str
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path,
        transform_request=lambda text: text.replace(
            "Reviewed repository: ", duplicate + "Reviewed repository: ", 1
        ),
    )

    with pytest.raises(pair.CompactPairError, match="Reviewed repository"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)
```

Add report tuple-mismatch coverage:

```python
@pytest.mark.parametrize("report_repository", (None, "/tmp/different-target"))
def test_report_cannot_omit_or_substitute_request_repository(
    tmp_path: Path, report_repository: str | None
) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=report_repository,
        ),
    )
    violations = pair.validate_report(root, report)
    assert any("Reviewed repository" in item for item in violations)


def test_report_cannot_add_repository_to_pipeline_local_request(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=root.as_posix(),
        ),
    )
    assert any(
        "Reviewed repository" in item for item in pair.validate_report(root, report)
    )


def test_report_rejects_duplicate_reviewed_repository_header(tmp_path: Path) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    report_path = _write_report(
        root,
        base,
        head,
        trigger,
        reviewed_repository=target.as_posix(),
    )
    text = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        text.replace(
            "Reviewed repository: ",
            "Reviewed repository:\nReviewed repository: ",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(pair.CompactPairError, match="Reviewed repository"):
        pair.parse_verification_report(root, report_path)


def test_request_bound_repository_must_remain_available_for_report(
    tmp_path: Path,
) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=target.as_posix(),
        ),
    )
    target.rename(tmp_path / "moved-target")
    assert any("request binding invalid" in item for item in pair.validate_report(root, report))
```

Add exact range and merge-base failure coverage:

```python
@pytest.mark.parametrize(
    ("case", "message"),
    (
        ("equal", "strict ancestor"),
        ("reversed", "strict ancestor"),
        ("missing", "Git commit or path validation failed"),
    ),
)
def test_cross_repository_range_fails_closed(
    tmp_path: Path, case: str, message: str
) -> None:
    def invalid_range(base: str, head: str) -> tuple[str, str]:
        if case == "equal":
            return base, base
        if case == "reversed":
            return head, base
        return base, "f" * 40

    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, range_values=invalid_range
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


def test_cross_repository_merge_base_error_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(tmp_path)
    real_run = pair.subprocess.run

    def fail_merge_base(*args, **kwargs):
        command = args[0]
        if "merge-base" in command and "--is-ancestor" in command:
            return subprocess.CompletedProcess(command, 2, b"", b"fatal")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(pair.subprocess, "run", fail_merge_base)
    with pytest.raises(pair.CompactPairError, match="Git ancestry validation failed"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)
```

- [ ] **Step 4: Run the new tests and verify RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py -k 'cross_repository or reviewed_repository or target_commits' -q
```

Expected: failures because request/report dataclasses and parsers do not yet recognize `Reviewed repository`, and target SHAs still resolve only in Pipeline. Existing 47 focused baseline tests must remain collectable.

- [ ] **Step 5: Add the optional field parser and canonical repository resolver**

In both dataclasses, add `reviewed_repository: str | None` immediately before `reviewed_head`.

Add these helpers after `validate_report` with the other intentionally internal helpers:

```python
def _optional_one(lines: list[str], prefix: str, label: str) -> str | None:
    occurrences = _normalized_field_occurrences(lines, label)
    if len(occurrences) > 1:
        raise CompactPairError(f"duplicate {label}")
    if not occurrences:
        return None
    line = occurrences[0]
    if not line.startswith(prefix):
        raise CompactPairError(f"invalid {label}")
    value = line[len(prefix) :]
    if not value or value != value.strip():
        raise CompactPairError(f"invalid {label}")
    return value


def _reviewed_root(pipeline_root: Path, repository_field: str | None) -> Path:
    pipeline_root = pipeline_root.resolve()
    if repository_field is None:
        return pipeline_root
    candidate = Path(repository_field)
    if not candidate.is_absolute():
        raise CompactPairError("Reviewed repository must be absolute")
    if candidate.as_posix() != repository_field:
        raise CompactPairError("Reviewed repository must be normalized")
    current = Path(candidate.anchor)
    for component in candidate.parts[1:]:
        current = current / component
        if current.is_symlink():
            raise CompactPairError("Reviewed repository traverses a symlink")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise CompactPairError("Reviewed repository is unavailable") from exc
    if not resolved.is_dir() or resolved.as_posix() != repository_field:
        raise CompactPairError("Reviewed repository must be one canonical directory")
    top_level = _git(resolved, "rev-parse", "--show-toplevel").decode().strip()
    if top_level != repository_field:
        raise CompactPairError("Reviewed repository must be a Git worktree root")
    return resolved
```

Do not catch `_git` commit or ancestry failures and convert them to success.

- [ ] **Step 6: Resolve request ranges in the selected repository**

In `parse_verify_request`, replace the current base/head resolution and ancestry block with:

```python
    reviewed_repository = _optional_one(
        lines, "Reviewed repository: ", "Reviewed repository"
    )
    reviewed_root = _reviewed_root(root, reviewed_repository)
    head = _full_commit(
        reviewed_root, _one(lines, "Reviewed head: ", "Reviewed head"), "Reviewed head"
    )
    base = _full_commit(
        reviewed_root, _one(lines, "Reviewed base: ", "Reviewed base"), "Reviewed base"
    )
```

Retain trigger ancestry only for Pipeline-local ranges:

```python
    if reviewed_root == root and (head == trigger or not _is_ancestor(root, head, trigger)):
        raise CompactPairError("request trigger must be strictly after Reviewed head")
    if base == head or not _is_ancestor(reviewed_root, base, head):
        raise CompactPairError("Reviewed base must be a strict ancestor of Reviewed head")
```

Set `reviewed_repository=reviewed_repository` in the returned `VerifyRequest`.

- [ ] **Step 7: Parse and validate the same tuple in reports**

In `_parse_verification_report_bytes`, parse and return:

```python
    reviewed_repository = _optional_one(
        lines, "Reviewed repository: ", "Reviewed repository"
    )
```

In `validate_report`, compare the exact optional field before base/head:

```python
    if report.reviewed_repository != request.reviewed_repository:
        violations.append("report Reviewed repository does not match request")
```

Replace the final Pipeline-only range recheck with:

```python
    try:
        reviewed_root = _reviewed_root(root, request.reviewed_repository)
        base = _full_commit(reviewed_root, request.reviewed_base, "Reviewed base")
        head = _full_commit(reviewed_root, request.reviewed_head, "Reviewed head")
        if base == head or not _is_ancestor(reviewed_root, base, head):
            raise CompactPairError(
                "Reviewed base must be a strict ancestor of Reviewed head"
            )
    except CompactPairError as exc:
        violations.append(f"reviewed range unavailable: {exc}")
```

- [ ] **Step 8: Prove the runtime and fixed-writer boundary GREEN**

In `tests/unit/test_coordination_tooling.py`, give `_prepare_verify_request`
these keyword parameters:

```python
    reviewed_repository: str | None = None,
    reviewed_range: tuple[str, str] | None = None,
```

After creating the fixture Pipeline candidate, select the bound range and
repository line with:

```python
    if reviewed_range is not None:
        base, head = reviewed_range
    repository_line = (
        "" if reviewed_repository is None
        else f"Reviewed repository: {reviewed_repository}\n"
    )
```

Insert `{repository_line}` immediately before `Reviewed head` in the request.
Give `_report_body` the same `reviewed_repository: str | None = None` keyword
and insertion. Then add the fixed-writer integration test:

```python
def test_cross_repository_verification_report_uses_fixed_finalizer(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    target = tmp_path / "target"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.email", "test@example.invalid")
    _git(target, "config", "user.name", "Test User")
    (target / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(target, "add", ".")
    _git(target, "commit", "-q", "-m", "chore: target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "feat: target candidate")
    head = _git(target, "rev-parse", "HEAD")

    _local_base, _local_head, request_path, trigger = _prepare_verify_request(
        repo,
        reviewed_repository=target.as_posix(),
        reviewed_range=(base, head),
    )
    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "operator",
            "all",
            "verification-report",
            f"truthful GO target commit `{head}`",
        ],
        repo,
        input_text=_report_body(
            base,
            head,
            request_path,
            trigger,
            verdict="GO",
            reviewed_repository=target.as_posix(),
        ),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-operator-to-all-verification-report.md")
```

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py -q
```

Expected: at least the original `47 passed` plus every new repository-binding test; zero failures.

- [ ] **Step 9: Commit the runtime slice**

```bash
env -u GIT_INDEX_FILE git add -- scripts/compact_pair_loop.py tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): bind cross-repository reviews"
```

---

### Task 2: Teach the canonical Operator surfaces the new identity field

**Files:**

- Modify: `scripts/codex_protocol_model.py:18-25`
- Modify: `tests/unit/test_protocol_prompt_sync.py:1240-1280`
- Modify: `.agents/skills/seat-operator/verification-report-format.md:13-25`
- Modify: `.claude/skills/seat-operator/verification-report-format.md:13-25`
- Modify: `ARCHITECTURE.md:60-70` only for exact moved function-line anchors

**Interfaces:**

- Consumes: Task 1's `Reviewed repository` field semantics.
- Produces: one canonical invariant phrase and byte-identical Operator report templates that tell reviewers when to include the field.

- [ ] **Step 1: Add the prompt-synchronization RED test**

Add a focused test in `tests/unit/test_protocol_prompt_sync.py`:

```python
def test_compact_pair_surfaces_bind_optional_reviewed_repository() -> None:
    assert "reviewed repository when explicit and base/head" in COMPACT_PAIR_INVARIANT
    for relative in (
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    ):
        text = _read(relative)
        assert (
            "Reviewed repository: <absolute canonical Git worktree root; "
            "omit only for Pipeline-local review>"
        ) in text
```

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -k 'optional_reviewed_repository' -q
```

Expected: FAIL because neither canonical surface names the field yet.

- [ ] **Step 2: Update the one canonical invariant sentence**

Change only the start of `COMPACT_PAIR_INVARIANT` to:

```python
COMPACT_PAIR_INVARIANT = (
    "Compact Pair Invariant: one committed verify-request binds the reviewed "
    "repository when explicit and base/head, outcome, author seat and "
    "system-visible author model, assigned non-author Operator, allowed paths, "
    "and immutable finding refs. One report from that distinct Operator seat "
    "and a different reviewer model binds the exact request and reviewed range, "
    "issues GO/NITS/FAIL, and explicitly dispositions every finding ref through "
    "the fixed mailbox writer. Missing, duplicated, abbreviated, uppercase, "
    "uncommitted, or mismatched identity, range, or finding fields are not "
    "authority."
)
```

Do not add a second rule tuple or new protocol renderer.

- [ ] **Step 3: Update both byte-identical report skeletons**

Insert exactly this optional line immediately before `Reviewed head` in both files:

```text
Reviewed repository: <absolute canonical Git worktree root; omit only for Pipeline-local review>
```

Add one sentence after the skeleton: “For a cross-repository review, preserve
the request's exact `Reviewed repository` field; never infer it from
`Verification context` or other prose.” Keep the two files byte-identical.

- [ ] **Step 4: Refresh only factual architecture line anchors**

Run:

```bash
rg -n '^def parse_verify_request|^def validate_report' scripts/compact_pair_loop.py
```

In `ARCHITECTURE.md`, replace only the numeric line suffixes in the existing
`parse_verify_request` and `validate_report` rows with the exact numbers just
printed. Do not change either description or add a new architecture concept.

- [ ] **Step 5: Run prompt and smoke checks**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: at least the original `37 passed` plus the new focused test;
placeholder PASS; smoke `OK`, including zero GO-schema violations.

- [ ] **Step 6: Commit the synchronized surfaces**

```bash
env -u GIT_INDEX_FILE git add -- scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py .agents/skills/seat-operator/verification-report-format.md .claude/skills/seat-operator/verification-report-format.md ARCHITECTURE.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "docs(protocol): expose reviewed repository identity"
```

---

### Task 3: Verify the exact range and request independent acceptance

**Files:**

- Create through the fixed writer: one canonical generated Director-to-Operator2 verify-request under `coordination/mailbox/sent/`
- No product or runtime source edits are permitted in this task.

**Interfaces:**

- Consumes: the committed coordinator route's exact implementation base and Tasks 1-2's final head.
- Produces: one canonical committed verify-request assigned to Operator2 on a model different from the Director's model.

- [ ] **Step 1: Refresh scope and verify the actual implementation range**

Run each command from `/Users/hyungkoookkim/Pipeline`:

```bash
: "${IMPLEMENTATION_BASE_SHA:?set IMPLEMENTATION_BASE_SHA to the full SHA in the committed coordinator route}"
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git diff --name-status "${IMPLEMENTATION_BASE_SHA}"..HEAD
env -u GIT_INDEX_FILE git diff --check "${IMPLEMENTATION_BASE_SHA}"..HEAD
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

At execution time, set `IMPLEMENTATION_BASE_SHA` to the exact full
`Implementation base` SHA printed in the committed coordinator route and task
prompt; do not use a short SHA, merge base, remembered value, or inferred
parent. Expected: only the routed implementation paths changed; all focused
tests pass; placeholder PASS; smoke `OK`; the worktree is clean.

- [ ] **Step 2: Inspect the abuse boundaries rather than relying on green tests**

Confirm from the actual diff that:

- report repository identity comes from the committed request, not report prose;
- duplicate, blank, malformed, relative, alias, symlink, nested-root, missing-repository, missing-commit, equal/reversed range, and merge-base error cases fail closed;
- Pipeline-local and frozen historical artifacts still validate;
- sanitized Git resolution and `--no-replace-objects` remain in force;
- the fixed writer validates a cross-repository candidate; and
- no route, mailbox transport, target mutation, service, database, dependency,
  push, merge, cursor, lock, booking, spend, or deployment authority was added.

- [ ] **Step 3: Publish and commit one canonical verify-request**

Use `coordination/bin/send-event director operator2 verify-request` and include:

- `Reviewed head`: the exact full final implementation HEAD;
- `Reviewed base`: the exact full SHA in `IMPLEMENTATION_BASE_SHA`;
- no `Reviewed repository` field, because this correction range is Pipeline-local;
- `Author seat: director` and the actual system-visible Director model;
- `Assigned operator: operator2` and intended different reviewer model;
- the approved spec and plan immutable refs;
- the Task 5A FAIL and Director2 blocker immutable refs;
- exact allowed paths and verification commands; and
- an outcome asking whether the range implements only the approved resolver correction without new ceremony or authority.

Validate the staged event with coordination checks, stage no other path, and commit it with:

```bash
env -u GIT_INDEX_FILE git commit -m "chore(protocol): request cross-repository binding review"
```

Stop after the committed request. The coordinator automatically dispatches it
to Operator2, waits for GO/NITS/FAIL, and routes any exact correction without
asking the user to relay a prompt.
