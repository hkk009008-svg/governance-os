from __future__ import annotations

import check_coordination as coordination
from formal_review_support import (
    add_report,
    add_request,
    commit,
    event,
    init_repo,
    report_body,
    request_body,
)


def test_empty_current_mailbox_is_clean(tmp_path) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    state = coordination.inspect_verify_review_state(root)
    assert state.pending == ()
    assert state.failed == ()
    assert coordination.run(root / "coordination") == []


def test_unknown_current_mailbox_entry_is_fatal(tmp_path) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    extra = root / "coordination/mailbox/sent/note.txt"
    extra.write_text("not a formal artifact\n", encoding="utf-8")
    state = coordination.inspect_verify_review_state(root)
    assert "unsupported current mailbox entry" in state.problem


def test_committed_request_is_pending_until_report(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, _ = add_request(root, base, head)
    state = coordination.inspect_verify_review_state(root)
    assert [item.path for item in state.pending] == [request_path]
    assert state.pending[0].reviewed_head == head


def test_go_closes_pending_request(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, head)
    add_report(root, request_path, request_commit)
    state = coordination.inspect_verify_review_state(root)
    assert state.pending == () and state.failed == () and state.problem is None


def test_report_commit_cannot_hide_another_change(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, head)
    report_path, text = event(
        "2026-09-02T10-01-00Z",
        "claude",
        "codex",
        "verification-report",
        report_body(request_path, request_commit),
    )
    commit(root, {report_path: text, "extra.txt": "hidden\n"}, "mixed report")
    state = coordination.inspect_verify_review_state(root)
    assert "only change" in state.problem


def test_fail_is_an_explicit_blocker(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, head)
    report_path, _ = add_report(root, request_path, request_commit, verdict="FAIL")
    state = coordination.inspect_verify_review_state(root)
    assert state.pending == ()
    assert state.failed[0].report_path == report_path
    assert coordination.run(root / "coordination")[0].kind == "failed_review"


def test_exact_remediation_supersedes_fail(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    first_head = commit(root, {"pipeline/control.py": "bad\n"}, "candidate")
    request1, request1_commit = add_request(root, base, first_head)
    fail_path, fail_commit = add_report(root, request1, request1_commit, verdict="FAIL")
    second_head = commit(root, {"pipeline/control.py": "fixed\n"}, "fix")
    request2, request2_commit = add_request(
        root, first_head, second_head, stamp="2026-09-02T10-02-00Z"
    )
    add_report(
        root,
        request2,
        request2_commit,
        stamp="2026-09-02T10-03-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )
    state = coordination.inspect_verify_review_state(root)
    assert state.pending == () and state.failed == () and state.problem is None


def test_modified_published_request_is_fatal(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, _ = add_request(root, base, head)
    (root / request_path).write_text("changed\n", encoding="utf-8")
    state = coordination.inspect_verify_review_state(root)
    assert not state.pending[0].valid
    assert "differs from committed HEAD" in str(state.pending[0].problem)
    assert coordination.run(root / "coordination")[0].severity == "FATAL"


def test_uncommitted_request_is_visible_and_invalid(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    path, text = event(
        "2026-09-02T10-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, head),
    )
    (root / path).write_text(text, encoding="utf-8")
    state = coordination.inspect_verify_review_state(root)
    assert state.pending[0].problem == "request is not committed"
