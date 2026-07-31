"""Stage 2 gate tests for the learning-candidate lifecycle (ADR-067).

Refusal tests here exercise READ-SIDE parsers: until the Stage 2b
writer-side branch lands in scripts/mailbox_writer.py these refusals are
advisory — a nonconforming event still publishes durably (contract I4). The
tests pin the parser contract, not a publication gate.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import protocol_mailbox  # noqa: E402


_SOURCE_REF = (
    "coordination/mailbox/sent/"
    "2026-07-30T01-02-03Z-director2-to-operator-verify-request.md@" + "c" * 40
)


def _candidate_fields(**overrides: str | None) -> dict[str, str | None]:
    fields: dict[str, str | None] = {
        "Category": "procedure",
        "Scope": "repository",
        "Statement": "Run the doctrine diff before every range submit.",
        "Proposed content hash": None,
        "Target": None,
        "Target base hash": None,
        "Source refs": _SOURCE_REF,
        "Evidence provenance": "MEASURED",
        "Applicability": "any range submitted for compact-pair review",
        "Exclusions": "scratch worktrees never submitted",
        "Risk class": "material-behavior",
        "Supersedes": None,
        "Producer seat": "director2",
        "Producer model": "claude-fable-5",
    }
    fields.update(overrides)
    return fields


def _event_text(fields: dict[str, str | None], *, candidate_id: str | None = None) -> str:
    body_id = (
        candidate_id
        if candidate_id is not None
        else protocol_mailbox.compute_learning_candidate_id(fields)
    )
    lines = [
        "# Director2 → Operator: candidate",
        "",
        "**When:** 2026-07-30T02-03-04Z · **From:** director2 (online)".replace(
            "02-03-04", "02:03:04"
        ),
        "",
        f"Candidate ID: {body_id}",
    ]
    for label, value in fields.items():
        if value is not None:
            lines.append(f"{label}: {value}")
    lines.append("")
    lines.append("Cursor at send: 0")
    return "\n".join(lines) + "\n"


def _event(fields: dict[str, str | None], *, candidate_id: str | None = None,
           kind: str = "learning-candidate") -> protocol_mailbox.CommittedEventRef:
    path = f"coordination/mailbox/sent/2026-07-30T02-03-04Z-director2-to-operator-{kind}.md"
    return protocol_mailbox.parse_committed_event_text(
        f"{path}@{'d' * 40}", _event_text(fields, candidate_id=candidate_id)
    )


def test_kernel_validators_import_no_learning_module() -> None:
    """Contract I1: the two validation kernels import no learning_* module."""

    for kernel in ("scripts/mailbox_writer.py", "scripts/compact_pair_loop.py"):
        tree = ast.parse((_REPO_ROOT / kernel).read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                # `from scripts import learning_x` binds learning_x: the
                # alias names carry the module, not node.module (round-one
                # FAIL: recording only node.module let exactly that form
                # evade the control).
                for alias in node.names:
                    imported.append(alias.name)
                    if node.module:
                        imported.append(f"{node.module}.{alias.name}")
        offenders = [
            name
            for name in imported
            if any(part.startswith("learning_") for part in name.split("."))
        ]
        assert offenders == [], f"{kernel} imports learning modules: {offenders}"


def test_i1_collector_catches_the_package_style_import(tmp_path: Path) -> None:
    """The collector itself is exercised against the form that evaded it."""

    probe = tmp_path / "kernel_probe.py"
    probe.write_text("from scripts import learning_index\n", encoding="utf-8")
    tree = ast.parse(probe.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.append(alias.name)
                if node.module:
                    imported.append(f"{node.module}.{alias.name}")
    offenders = [
        name
        for name in imported
        if any(part.startswith("learning_") for part in name.split("."))
    ]
    assert offenders, "the package-style learning import must be caught"


def test_registry_has_learning_candidate_and_not_memory_candidate() -> None:
    """The kind swap landed in one commit: new kind in, retired kind out."""

    kinds = (_REPO_ROOT / "coordination/mailbox/kinds.txt").read_text(
        encoding="utf-8"
    ).split()
    assert "learning-candidate" in kinds
    assert "memory-candidate" not in kinds


def test_candidate_round_trip() -> None:
    fields = _candidate_fields()
    statement = protocol_mailbox.parse_learning_candidate_statement(_event(fields))
    assert statement.category == "procedure"
    assert statement.scope == "repository"
    assert statement.source_refs == (_SOURCE_REF,)
    assert statement.evidence_provenance == "MEASURED"
    assert statement.risk_class == "material-behavior"
    assert statement.producer_seat == "director2"
    assert statement.supersedes is None
    assert statement.candidate_id == protocol_mailbox.compute_learning_candidate_id(
        fields
    )


def test_candidate_id_must_match_normalized_payload() -> None:
    with pytest.raises(ValueError, match="normalized payload"):
        protocol_mailbox.parse_learning_candidate_statement(
            _event(_candidate_fields(), candidate_id="e" * 64)
        )


def test_target_requires_base_hash_and_vice_versa() -> None:
    with pytest.raises(ValueError, match="present together"):
        protocol_mailbox.parse_learning_candidate_statement(
            _event(_candidate_fields(Target="docs/protocol/learning/contract.md"))
        )
    statement = protocol_mailbox.parse_learning_candidate_statement(
        _event(
            _candidate_fields(
                **{
                    "Target": "docs/protocol/learning/contract.md",
                    "Target base hash": "sha256:" + "a" * 64,
                }
            )
        )
    )
    assert statement.target_base_hash == "sha256:" + "a" * 64


def test_closed_vocabularies_are_enforced() -> None:
    for overrides, message in (
        ({"Category": "vibe"}, "closed learning categories"),
        ({"Scope": "global"}, "Scope must be"),
        ({"Evidence provenance": "GUESSED"}, "claim_check ladder"),
        ({"Risk class": "casual"}, "closed set"),
        ({"Producer seat": "coordinator"}, "pair seat"),
    ):
        with pytest.raises(ValueError, match=message):
            protocol_mailbox.parse_learning_candidate_statement(
                _event(_candidate_fields(**overrides))
            )


def test_assumed_provenance_parses_but_is_marked() -> None:
    # ASSUMED is a legal recorded blank cell; refusing its ACCEPTANCE is a
    # Stage 2b disposition rule, not a parse error (contract §3).
    statement = protocol_mailbox.parse_learning_candidate_statement(
        _event(_candidate_fields(**{"Evidence provenance": "ASSUMED"}))
    )
    assert statement.evidence_provenance == "ASSUMED"


def test_supersedes_must_name_a_learning_candidate_event() -> None:
    good = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "b" * 40
    )
    statement = protocol_mailbox.parse_learning_candidate_statement(
        _event(_candidate_fields(Supersedes=good))
    )
    assert statement.supersedes == good
    with pytest.raises(ValueError, match="learning-candidate event"):
        protocol_mailbox.parse_learning_candidate_statement(
            _event(_candidate_fields(Supersedes=_SOURCE_REF))
        )


def test_disposition_round_trip_and_kind_guard() -> None:
    candidate_ref = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "b" * 40
    )
    path = (
        "coordination/mailbox/sent/"
        "2026-07-30T03-04-05Z-director-to-all-decision.md"
    )
    text = (
        "# Director → All: dispose candidate\n\n"
        "**When:** 2026-07-30T03:04:05Z · **From:** director (online)\n\n"
        f"Candidate: {candidate_ref}\n"
        "Disposition: declined\n\n"
        "Cursor at send: 0\n"
    )
    event = protocol_mailbox.parse_committed_event_text(f"{path}@{'a' * 40}", text)
    statement = protocol_mailbox.parse_learning_disposition_statement(event)
    assert statement.disposition == "declined"
    assert statement.candidate_ref == candidate_ref
    assert statement.disposer_seat == "director"
    with pytest.raises(ValueError, match="committed 'decision'"):
        protocol_mailbox.parse_learning_disposition_statement(
            _event(_candidate_fields())
        )


def test_dedup_scan_reads_committed_events_at_the_pinned_commit(
    tmp_path: Path,
) -> None:
    """Dedup derives from committed sent/ events, never the local index."""

    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        ).stdout.decode("utf-8")

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    fields = _candidate_fields()
    name = "2026-07-30T02-03-04Z-director2-to-operator-learning-candidate.md"
    (sent / name).write_text(_event_text(fields), encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "candidate")
    ids = protocol_mailbox.committed_learning_candidate_ids(root, "HEAD")
    expected_id = protocol_mailbox.compute_learning_candidate_id(fields)
    assert ids == {expected_id: f"coordination/mailbox/sent/{name}"}
    # An uncommitted (worktree-only) candidate must NOT appear in the scan.
    other = "2026-07-30T09-09-09Z-operator-to-director-learning-candidate.md"
    (sent / other).write_text(
        _event_text(_candidate_fields(Statement="uncommitted lesson")),
        encoding="utf-8",
    )
    assert protocol_mailbox.committed_learning_candidate_ids(root, "HEAD") == {
        expected_id: f"coordination/mailbox/sent/{name}"
    }


def test_send_event_wrapper_refuses_non_pair_learning_candidate_sender(
    tmp_path: Path,
) -> None:
    """The wrapper-side sender gate refuses, and nothing is written.

    Advisory strength only (bypassable by hand-authoring, contract I4). Runs
    against a repository built for the test — never this checkout — so a
    reverted gate publishes into a throwaway mailbox, not the reviewed one
    (round-one FAIL: the earlier form ran against the live checkout).
    """

    import sys as _sys

    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    venv = root / ".venv" / "bin"
    venv.mkdir(parents=True)
    (venv / "python").symlink_to(_sys.executable)
    mailbox = root / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("learning-candidate\n", encoding="utf-8")
    (mailbox / "seen" / "coordinator.txt").write_text("0\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "fixture")

    result = subprocess.run(
        [str(_REPO_ROOT / "coordination/bin/send-event"),
         "coordinator", "all", "learning-candidate", "probe"],
        input=b"Candidate ID: probe\n",
        capture_output=True,
        cwd=root,
    )
    assert result.returncode == 2
    assert b"only pair seats may publish learning-candidate" in result.stderr
    assert list((mailbox / "sent").iterdir()) == [], "refusal must write nothing"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    ).stdout
    assert status == b"", "refusal must stage nothing"


def test_producer_seat_must_match_envelope_sender() -> None:
    """A self-declared producer differing from the sender is refused at parse."""

    with pytest.raises(ValueError, match="match the envelope sender"):
        protocol_mailbox.parse_learning_candidate_statement(
            _event(_candidate_fields(**{"Producer seat": "operator"}))
        )


def test_dedup_scan_collapses_duplicate_ids_to_the_first_path(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    fields = _candidate_fields()
    first = "2026-07-30T02-03-04Z-director2-to-operator-learning-candidate.md"
    second = "2026-07-30T09-09-09Z-director2-to-operator-learning-candidate.md"
    (sent / first).write_text(_event_text(fields), encoding="utf-8")
    (sent / second).write_text(
        _event_text(fields).replace("02:03:04", "09:09:09"), encoding="utf-8"
    )
    git("add", "-A")
    git("commit", "-q", "-m", "duplicate republish")
    ids = protocol_mailbox.committed_learning_candidate_ids(root, "HEAD")
    expected_id = protocol_mailbox.compute_learning_candidate_id(fields)
    assert ids == {expected_id: f"coordination/mailbox/sent/{first}"}


def test_parsers_work_under_package_style_import(tmp_path: Path) -> None:
    """`from scripts import protocol_mailbox` with only the repo root on
    sys.path must still parse a candidate (round-one FAIL: the flat-only lazy
    imports raised ModuleNotFoundError in that shape)."""

    script = tmp_path / "probe.py"
    script.write_text(
        "import sys\n"
        "sys.path = [p for p in sys.path"
        " if not p.rstrip('/').endswith('scripts')]\n"
        f"sys.path.insert(0, {str(_REPO_ROOT)!r})\n"
        "from scripts import protocol_mailbox\n"
        "fields = {\n"
        "    'Category': 'procedure', 'Scope': 'repository',\n"
        "    'Statement': 's', 'Source refs': "
        f"{_SOURCE_REF!r},\n"
        "    'Evidence provenance': 'MEASURED', 'Applicability': 'a',\n"
        "    'Exclusions': 'e', 'Risk class': 'material-behavior',\n"
        "    'Producer seat': 'director2', 'Producer model': 'm',\n"
        "}\n"
        "cid = protocol_mailbox.compute_learning_candidate_id(fields)\n"
        "lines = [f'Candidate ID: {cid}'] + "
        "[f'{k}: {v}' for k, v in fields.items()]\n"
        "text = ('# Director2 → Operator: c\\n\\n'\n"
        "        '**When:** 2026-07-30T02:03:04Z · **From:** director2 (online)\\n\\n'\n"
        "        + '\\n'.join(lines) + '\\n\\nCursor at send: 0\\n')\n"
        "path = ('coordination/mailbox/sent/'\n"
        "        '2026-07-30T02-03-04Z-director2-to-operator-learning-candidate.md')\n"
        "event = protocol_mailbox.parse_committed_event_text(path + '@' + 'd'*40, text)\n"
        "statement = protocol_mailbox.parse_learning_candidate_statement(event)\n"
        "print('OK', statement.candidate_id == cid)\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-P", str(script)],
        capture_output=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr.decode()
    assert b"OK True" in result.stdout
