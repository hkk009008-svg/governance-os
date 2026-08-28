"""Replay desktop-era mailbox writes from committed Git history."""
from __future__ import annotations

from pathlib import Path

import compact_pair_loop
import mailbox_review_admission
import mailbox_writer
import protocol_mailbox

DESKTOP_WRITE_CUTOVER_COMMIT = "b1390a244d2368e89bb65d65a148e55bac0d8df0"


def _tree_event_entries(run_git, repo_root, commit: str, prefix: str):
    """Return event name -> committed ``(path, mode, type, oid)`` entries."""

    listed = run_git(
        repo_root, "ls-tree", "-r", "-z", commit, "--", prefix.rstrip("/")
    )
    if listed.returncode != 0:
        return None
    entries: dict[str, set[tuple[str, str, str, str]]] = {}
    for entry in listed.stdout.split(b"\0"):
        if not entry:
            continue
        meta, _, name = entry.partition(b"\t")
        fields = meta.split()
        if len(fields) < 3:
            continue
        path = name.decode("utf-8", errors="replace")
        entries.setdefault(Path(path).name, set()).add(
            (
                path,
                fields[0].decode("ascii"),
                fields[1].decode("ascii"),
                fields[2].decode("ascii"),
            )
        )
    return entries


def _changed_commits(run_git, repo_root, cutover: str, head: str, root: str):
    result = run_git(
        repo_root,
        "rev-list",
        "--reverse",
        "--topo-order",
        "--full-history",
        f"{cutover}..{head}",
        "--",
        root,
    )
    if result.returncode != 0:
        return None
    try:
        commits = result.stdout.decode("ascii", errors="strict").splitlines()
    except UnicodeDecodeError:
        return None
    if any(compact_pair_loop.SHA_RE.fullmatch(item) is None for item in commits):
        return None
    return commits


def check_post_cutover_event_admission(
    projection, issue_factory, sent_prefix, run_git, repo_root
) -> list:
    """Replay every mailbox-changing commit after the desktop cutover."""

    commits = projection.commits
    cutover = DESKTOP_WRITE_CUTOVER_COMMIT
    head = commits.head
    mailbox_root = sent_prefix.rstrip("/").rsplit("/", 1)[0]
    at_head = _tree_event_entries(run_git, repo_root, head, mailbox_root)
    if at_head is None:
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_event_admission_unavailable",
            "FATAL",
            "cannot list the mailbox at HEAD for desktop write admission",
        )]

    cutover_available = (
        commits.object_types.get(cutover) == "commit"
        and commits.is_ancestor(cutover, head)
    )
    if not cutover_available:
        identities = {*protocol_mailbox.APP_MEMBERS, *protocol_mailbox.ROLES}
        current = [
            name
            for name in at_head
            if (match := protocol_mailbox.EVENT_NAME_RE.fullmatch(name))
            and ({match.group("sender"), match.group("recipient")} & identities)
        ]
        if not current:
            return []
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_event_admission_unavailable",
            "FATAL",
            f"desktop write cutover {cutover[:8]} is unavailable while current "
            f"writer-identity events exist; first: {sorted(current)[0]}",
        )]

    at_cutover = _tree_event_entries(run_git, repo_root, cutover, mailbox_root)
    if at_cutover is None:
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_event_admission_unavailable",
            "FATAL",
            f"cannot list the mailbox at desktop write cutover {cutover[:8]}",
        )]
    history = _changed_commits(run_git, repo_root, cutover, head, mailbox_root)
    if history is None:
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_event_admission_unavailable",
            "FATAL",
            "cannot enumerate desktop-era mailbox history",
        )]

    issues: list = []
    emitted: set[tuple[str, str]] = set()
    observed: dict[str, tuple[str, str, str, str, str]] = {}

    def add(path: str, message: str) -> None:
        key = (path, message)
        if key in emitted:
            return
        emitted.add(key)
        issues.append(issue_factory(
            path.removeprefix("coordination/"),
            "post_cutover_event_admission",
            "FATAL",
            message,
        ))

    for commit in history:
        tree = _tree_event_entries(run_git, repo_root, commit, mailbox_root)
        if tree is None:
            add("coordination/mailbox/sent/", f"cannot list mailbox tree at {commit}")
            continue
        for name, entries in sorted(tree.items()):
            if protocol_mailbox.EVENT_NAME_RE.fullmatch(name) is None:
                continue
            baseline = at_cutover.get(name, set())
            signatures = {(mode, kind, blob) for _, mode, kind, blob in entries}
            if baseline:
                baseline_signatures = {
                    (mode, kind, blob) for _, mode, kind, blob in baseline
                }
                if not signatures <= baseline_signatures:
                    add(
                        sorted(entries)[0][0],
                        f"event {name} changed bytes, mode, or type from the "
                        f"desktop cutover at {commit}",
                    )
                if len(entries) > len(baseline):
                    add(sorted(entries)[0][0], f"event {name} was duplicated after the desktop cutover")
                continue
            if len(entries) != 1:
                add(sorted(entries)[0][0], f"current event name has {len(entries)} committed copies: {name}")
                continue
            path, mode, object_type, blob = next(iter(entries))
            if not path.startswith(sent_prefix):
                add(path, f"current event is outside mailbox/sent at {commit}: {path}")
                continue
            if (mode, object_type) != ("100644", "blob"):
                add(path, f"current event must be a 100644 blob, got {mode} {object_type}")
                continue
            first = observed.get(name)
            if first is not None:
                if (mode, object_type, blob) != first[1:4]:
                    add(path, f"event {name} changed after its desktop-era introduction")
                continue
            introduction = projection.introductions.get(path)
            raw = projection.introduction_events.get(path)
            if introduction is None or raw is None:
                add(path, "current sent event lacks a matching committed introduction")
                continue
            if introduction[0] != commit:
                add(path, "event was absent at the desktop cutover and cannot reuse a pre-cutover introduction; publish a new canonical event")
                continue
            if introduction[1] != blob:
                add(path, "current sent event differs from its desktop introduction")
                continue
            observed[name] = (path, mode, object_type, blob, commit)
            try:
                mailbox_review_admission.validate_committed_new_event(
                    projection, Path(repo_root), path, raw, commit
                )
            except (
                mailbox_writer.MailboxWriterError,
                compact_pair_loop.CompactPairError,
                OSError,
                UnicodeError,
                ValueError,
            ) as exc:
                add(path, f"current event fails fixed-writer admission: {exc}")

    for name, (path, mode, object_type, blob, _) in sorted(observed.items()):
        current = at_head.get(name, set())
        if (path, mode, object_type, blob) not in current:
            add(path, f"desktop-era durable event is absent or changed at HEAD: {name}")
        if len(current) != 1:
            add(path, f"desktop-era durable event has {len(current)} copies at HEAD: {name}")
    return issues
