"""Regression tests for protocol coordination shell tooling."""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import shutil
import shlex
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest


def _run(
    args: list[str | Path],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=full_env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = _run(["git", *args], repo, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    venv = repo / ".venv" / "bin"
    venv.mkdir(parents=True, exist_ok=True)
    if not (venv / "python").exists():
        (venv / "python").symlink_to(sys.executable)
    (repo / "governance.toml").write_text(
        '[protocol.kernel]\nepoch = 0\nwriter = "v1"\n', encoding="utf-8"
    )


def _install_compact_selector(repo: Path, source_root: Path) -> None:
    scripts = repo / "scripts"
    scripts.mkdir(exist_ok=True)
    (scripts / "kernel_activation.py").write_bytes(
        (source_root / "scripts" / "kernel_activation.py").read_bytes()
    )
    (repo / "governance.toml").write_text(
        '[protocol.kernel]\nepoch = 1\nwriter = "compact"\n',
        encoding="utf-8",
    )
    selector = (
        json.dumps(
            {
                "epoch": 1,
                "schema": "protocol-kernel-selection/v1",
                "writer": "compact",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(repo), "hash-object", "-w", "--stdin"],
        input=selector.encode(),
        capture_output=True,
        check=True,
    )
    oid = result.stdout.decode().strip()
    _git(repo, "update-ref", "refs/protocol/kernel-activation", oid)


def _verification_shell_fixture(repo: Path, source_root: Path) -> tuple[str, str]:
    task_id = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    descriptor_path = f"coordination/verification/scopes/{task_id}.json"
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("verification-report\n", encoding="utf-8")
    (mailbox / "seen" / "operator2.txt").write_text("0\n", encoding="utf-8")
    (repo / "requirements").mkdir()
    (repo / "requirements" / "task.md").write_text(
        "Verify the shell publication fixture.\n", encoding="utf-8"
    )
    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "verification_report_gate.py").write_bytes(
        (source_root / "scripts" / "verification_report_gate.py").read_bytes()
    )
    (scripts / "kernel_activation.py").write_bytes(
        (source_root / "scripts" / "kernel_activation.py").read_bytes()
    )
    (repo / "governance.toml").write_text(
        '[protocol.kernel]\nepoch = 0\nwriter = "v1"\n', encoding="utf-8"
    )
    (scripts / "feature.py").write_text("VALUE = 'base'\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Pipeline fixture\n", encoding="utf-8")
    (scripts / "codex_protocol_model.py").write_text(
        "# Pipeline marker\n", encoding="utf-8"
    )
    agent = repo / ".claude/agents/lane-v-verifier.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\nname: lane-v-verifier\n---\n\nFixture verifier.\n",
        encoding="utf-8",
    )
    (repo / ".gitattributes").write_text(
        "coordination/mailbox/sent/*-verification-report.md filter=hostile\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: base")
    base = _git(repo, "rev-parse", "HEAD")

    descriptor = {
        "schema_version": "lane-v-scope/v1",
        "task_id": task_id,
        "question_id": "send-event-shell-fixture",
        "trigger_kind": "verify-request",
        "verification_mode": "independent-lane-v",
        "verification_harness": "lane-v:independent-verifier",
        "review_profile": "independent-lane-v",
        "reviewed_base": {"policy": "exact", "commit": base},
        "requirement_paths": ["requirements/task.md"],
        "allowed_path_roots": ["coordination/verification/scopes", "scripts"],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
        ],
    }
    descriptor_file = repo / descriptor_path
    descriptor_file.parent.mkdir(parents=True)
    descriptor_raw = (json.dumps(descriptor, indent=2) + "\n").encode("utf-8")
    descriptor_file.write_bytes(descriptor_raw)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_raw).hexdigest()
    scope = f"{descriptor_path}@{descriptor_digest}"
    _git(repo, "add", descriptor_path)
    _git(repo, "commit", "-q", "-m", "docs: bind shell fixture")

    (scripts / "feature.py").write_text("VALUE = 'reviewed'\n", encoding="utf-8")
    _git(repo, "add", "scripts/feature.py")
    _git(repo, "commit", "-q", "-m", "feat: reviewed shell fixture")
    head = _git(repo, "rev-parse", "HEAD")
    trigger_path = (
        "coordination/mailbox/sent/"
        "2026-07-13T05-01-00Z-director-to-operator2-verify-request.md"
    )
    (repo / trigger_path).write_text(
        "# Director → Operator2: verify shell fixture\n\n"
        "**When:** 2026-07-13T05:01:00Z · **From:** director (online)\n\n"
        "Event type: verify-request\n"
        f"Reviewed head: {head}\n"
        f"Reviewed base: {base}\n"
        f"Lane-V-Scope: {scope}\n",
        encoding="utf-8",
    )
    _git(repo, "add", trigger_path)
    _git(repo, "commit", "-q", "-m", "coord: request shell verification")
    trigger = _git(repo, "rev-parse", "HEAD")

    venv = repo / ".venv" / "bin"
    venv.mkdir(parents=True, exist_ok=True)
    if not (venv / "python").exists():
        (venv / "python").symlink_to(sys.executable)
    body = "\n".join(
        [
            "VERDICT: GO",
            "",
            "## Evidence",
            "$ env -u GIT_INDEX_FILE true",
            "→ fixture passed",
            "",
            "## Verification Attestation",
            "",
            "Verification schema: lane-v-report/v3",
            "Verification mode: independent-lane-v",
            "Verification harness: lane-v:independent-verifier",
            f"Verification task ID: {task_id}",
            f"Scope authority: {scope}",
            f"Trigger identity: verify-request:{trigger}:{trigger_path}",
            f"Reviewed head: {head}",
            f"Reviewed base: {base}",
            "Review profile: independent-lane-v",
            "Reviewer identity: operator2",
            "",
            "## Findings",
            "None.",
        ]
    )
    return head, body


def _verification_command(tool: Path, head: str) -> list[str | Path]:
    return [
        tool,
        "operator2",
        "all",
        "verification-report",
        "Lane V verification report — commit",
        f"`{head}`",
    ]


def _fixed_report(head: str, body: str) -> tuple[str, bytes]:
    timestamp_dash = "2026-07-14T01-02-03Z"
    timestamp_colon = "2026-07-14T01:02:03Z"
    relative = (
        "coordination/mailbox/sent/"
        f"{timestamp_dash}-operator2-to-all-verification-report.md"
    )
    raw = (
        f"# Operator2 → All: Lane V verification report — commit `{head}`\n\n"
        f"**When:** {timestamp_colon} · **From:** operator2 (online)\n\n"
        f"{body}\n\nCursor at send: 0\n"
    ).encode("utf-8")
    return relative, raw


def test_send_event_force_stages_ignored_mailbox_event(tmp_path: Path, repo_root: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / ".gitignore").write_text(
        "coordination/mailbox/sent/*\n"
        "!coordination/mailbox/sent/.gitkeep\n",
        encoding="utf-8",
    )
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("status\n", encoding="utf-8")
    (mailbox / "seen" / "director.txt").write_text("0\n", encoding="utf-8")
    (mailbox / "sent" / ".gitkeep").write_text("", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "seed")

    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "director",
            "operator",
            "status",
            "ignored mailbox event",
        ],
        repo,
        input_text="body\n",
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert "coordination/mailbox/sent/" in staged
    assert staged.endswith("-director-to-operator-status.md")


def test_send_event_selector_denial_precedes_final_file_and_index_mutation(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("status\n", encoding="utf-8")
    (mailbox / "seen" / "director.txt").write_text("0\n", encoding="utf-8")
    (mailbox / "sent" / ".gitkeep").write_text("", encoding="utf-8")
    _install_compact_selector(repo, repo_root)
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: compact selector fixture")

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "director",
            "operator",
            "status",
            "must be fenced",
        ],
        repo,
        input_text="body\n",
    )

    assert result.returncode != 0
    assert list((mailbox / "sent").glob("*-director-to-operator-status.md")) == []
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_consume_events_selector_denial_precedes_cursor_and_index_mutation(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    cursor = mailbox / "seen" / "director.txt"
    cursor.write_text("2026-07-16T00:00:00Z\n", encoding="utf-8")
    (mailbox / "sent" / "2026-07-16T00-01-00Z-operator-to-director-status.md").write_text(
        "# fixture\n", encoding="utf-8"
    )
    _install_compact_selector(repo, repo_root)
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: compact cursor fixture")

    result = _run(
        [repo_root / "coordination/bin/consume-events", "director"],
        repo,
    )

    assert result.returncode != 0
    assert cursor.read_text(encoding="utf-8") == "2026-07-16T00:00:00Z\n"
    assert _git(repo, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize(
    "from_seat",
    ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"],
)
def test_send_event_keeps_mailbox_event_when_git_index_is_locked_for_every_sender(
    tmp_path: Path, repo_root: Path, from_seat: str
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("status\n", encoding="utf-8")
    (mailbox / "seen" / f"{from_seat}.txt").write_text("0\n", encoding="utf-8")
    (mailbox / "sent" / ".gitkeep").write_text("", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "seed")

    index_lock = repo / ".git" / "index.lock"
    index_lock.write_text("locked\n", encoding="utf-8")
    try:
        result = _run(
            [
                repo_root / "coordination" / "bin" / "send-event",
                from_seat,
                "all",
                "status",
                "index locked mailbox event",
            ],
            repo,
            input_text="body\n",
        )
    finally:
        index_lock.unlink()

    assert result.returncode == 0, result.stderr
    assert "not staged" in result.stdout
    sent_files = sorted((mailbox / "sent").glob(f"*-{from_seat}-to-all-status.md"))
    assert len(sent_files) == 1
    assert "index locked mailbox event" in sent_files[0].read_text(encoding="utf-8")
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_verification_send_event_uses_trusted_runtime_and_exact_python_stage(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    attacker_bin = tmp_path / "attacker-bin"
    attacker_bin.mkdir()
    marker = tmp_path / "attacker-ran"
    for name in ("bash", "git", "python", "date", "sed"):
        executable = attacker_bin / name
        executable.write_text(
            f"#!/bin/sh\n/usr/bin/touch {marker}\nexit 99\n", encoding="utf-8"
        )
        executable.chmod(0o755)
    hostile_home = tmp_path / "hostile-home"
    hostile_xdg = tmp_path / "hostile-xdg"
    hostile_home.mkdir()
    (hostile_xdg / "git").mkdir(parents=True)
    filter_marker = tmp_path / "filter-ran"
    hostile_config = (
        "[filter \"hostile\"]\n"
        f"\tclean = /bin/sh -c '/usr/bin/touch {filter_marker}; /bin/cat'\n"
        "\trequired = true\n"
    )
    (hostile_home / ".gitconfig").write_text(hostile_config, encoding="utf-8")
    (hostile_xdg / "git" / "config").write_text(hostile_config, encoding="utf-8")
    bash_env = tmp_path / "bash-env"
    bash_env.write_text(f"/usr/bin/touch {marker}\n", encoding="utf-8")
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "json.py").write_text("raise RuntimeError('shadowed')\n", encoding="utf-8")
    (shadow / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n",
        encoding="utf-8",
    )
    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "operator2",
            "all",
            "verification-report",
            "Lane V verification report — commit",
            f"`{head}`",
        ],
        repo,
        env={
            "PATH": str(attacker_bin),
            "HOME": str(hostile_home),
            "XDG_CONFIG_HOME": str(hostile_xdg),
            "GIT_DIR": str(tmp_path / "attacker.git"),
            "GIT_COMMON_DIR": str(tmp_path / "attacker-common.git"),
            "GIT_WORK_TREE": str(tmp_path / "attacker-worktree"),
            "GIT_INDEX_FILE": str(tmp_path / "attacker-index"),
            "GIT_OBJECT_DIRECTORY": str(tmp_path / "attacker-objects"),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(tmp_path / "attacker-alternates"),
            "GIT_REPLACE_REF_BASE": "refs/attacker/replace/",
            "GIT_CONFIG_SYSTEM": str(tmp_path / "attacker-system.gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "0",
            "GIT_CONFIG_GLOBAL": str(hostile_home / ".gitconfig"),
            "GIT_CEILING_DIRECTORIES": str(tmp_path),
            "GIT_DISCOVERY_ACROSS_FILESYSTEM": "1",
            "GIT_EXEC_PATH": str(attacker_bin),
            "GIT_FUTURE_UNKNOWN_SELECTOR": "must-be-scrubbed",
            "PYTHONPATH": str(shadow),
            "PYTHONHOME": str(tmp_path / "hostile-python-home"),
            "PYTHONSTARTUP": str(shadow / "sitecustomize.py"),
            "PYTHONUSERBASE": str(tmp_path / "hostile-user-base"),
            "BASH_ENV": str(bash_env),
            "BASH_FUNC_git%%": f"() {{ /usr/bin/touch {marker}; }}",
        },
        input_text=body,
    )

    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    assert not filter_marker.exists()
    staged_paths = _git(repo, "diff", "--cached", "--name-only").splitlines()
    report_paths = [path for path in staged_paths if path.endswith("-verification-report.md")]
    assert len(report_paths) == 1
    report_path = report_paths[0]
    working = (repo / report_path).read_bytes()
    timestamp_dash = Path(report_path).name.split("-operator2-to-", 1)[0]
    timestamp_colon = (
        timestamp_dash[:11] + timestamp_dash[11:19].replace("-", ":") + "Z"
    )
    expected = (
        f"# Operator2 → All: Lane V verification report — commit `{head}`\n\n"
        f"**When:** {timestamp_colon} · **From:** operator2 (online)\n\n"
        f"{body}\n\nCursor at send: 0\n"
    ).encode("utf-8")
    assert working == expected
    staged = subprocess.run(
        ["/usr/bin/git", "-C", str(repo), "show", ":" + report_path],
        check=True,
        capture_output=True,
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
    ).stdout
    assert staged == working
    assert f"created {report_path} (staged" in result.stdout
    task_records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(task_records) == 1
    assert json.loads(task_records[0].read_text(encoding="utf-8"))["state"] == "published"
    assert not list((repo / "coordination/mailbox/sent").glob(".trusted-*"))
    assert not list((repo / "coordination/mailbox/sent").glob(".pycache.*"))
    assert not list((repo / "coordination/mailbox/sent").glob(".published.*"))


def test_verification_send_event_primary_bootstrap_fails_closed(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    (repo / ".venv/bin/python").unlink()

    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "operator2",
            "all",
            "verification-report",
            "Lane V verification report — commit",
            f"`{head}`",
        ],
        repo,
        input_text=body,
    )

    assert result.returncode == 4
    assert "trusted Pipeline Python unavailable" in result.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert not list((repo / "coordination/mailbox/sent").glob("*-verification-report.md"))
    assert not list((repo / "coordination/mailbox/sent").glob(".*.tmp"))


def test_verification_send_event_nonexecutable_primary_python_fails_closed(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    python = repo / ".venv/bin/python"
    python.unlink()
    python.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
    python.chmod(0o644)

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body,
    )

    assert result.returncode == 4
    assert "trusted Pipeline Python unavailable" in result.stderr
    _assert_no_verification_publication(repo)


@pytest.mark.parametrize("checkpoint", ["after_publishing", "after_link", "after_index_update"])
def test_verification_send_event_preserves_recoverable_candidate_and_resumes(
    tmp_path: Path, repo_root: Path, checkpoint: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    source = gate_path.read_text(encoding="utf-8")
    needle = '    """Fault-injection seam for crash-boundary regression tests."""\n'
    replacement = (
        needle
        + f"    if label == {checkpoint!r}:\n"
        + "        raise RuntimeError('injected shell publication crash')\n"
    )
    assert needle in source
    gate_path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
    _git(repo, "add", "scripts/verification_report_gate.py")
    _git(repo, "commit", "-q", "-m", f"test: inject {checkpoint}")

    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "operator2",
            "all",
            "verification-report",
            "Lane V verification report — commit",
            f"`{head}`",
        ],
        repo,
        input_text=body,
    )

    assert result.returncode == 5
    assert (
        f"{repo / '.venv/bin/python'} -E -s -S -B "
        f"{repo / 'scripts/verification_report_gate.py'} resume "
        f"--repo-root {repo} --task-id "
    ) in result.stderr
    assert "publication remains recoverable" in result.stderr
    records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["state"] == "publishing"
    candidate = repo / "coordination/mailbox/sent" / record["candidate_name"]
    assert candidate.exists()

    resumed = _run(
        [
            repo / ".venv/bin/python",
            repo / "scripts/verification_report_gate.py",
            "resume",
            "--repo-root",
            repo,
            "--task-id",
            "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
        ],
        repo,
    )
    assert resumed.returncode == 0, resumed.stderr
    relative = resumed.stdout.strip()
    assert relative == record["path"]
    assert (repo / relative).exists()
    assert relative in _git(repo, "diff", "--cached", "--name-only")


def test_verification_send_event_process_death_preserves_witnessed_candidate(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    source = gate_path.read_text(encoding="utf-8")
    needle = '    """Fault-injection seam for crash-boundary regression tests."""\n'
    replacement = (
        needle
        + "    if label == 'after_publishing':\n"
        + "        os._exit(77)\n"
    )
    assert needle in source
    gate_path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
    _git(repo, "add", "scripts/verification_report_gate.py")
    _git(repo, "commit", "-q", "-m", "test: inject publisher process death")

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body,
    )

    assert result.returncode == 77
    records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["state"] == "publishing"
    candidate = repo / "coordination/mailbox/sent" / record["candidate_name"]
    assert candidate.exists()
    assert "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest() == record[
        "candidate_digest"
    ]
    assert not (repo / record["path"]).exists()


def test_verification_send_event_process_death_does_not_unlink_substituted_name(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    source = gate_path.read_text(encoding="utf-8")
    needle = '    _publication_checkpoint("after_publishing")\n'
    replacement = (
        needle
        + '    moved_name = ".moved-invocation-candidate.tmp"\n'
        + "    os.rename(\n"
        + "        candidate.name, moved_name, src_dir_fd=sent_fd, dst_dir_fd=sent_fd\n"
        + "    )\n"
        + "    replacement_fd = os.open(\n"
        + "        candidate.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600,\n"
        + "        dir_fd=sent_fd,\n"
        + "    )\n"
        + "    os.write(replacement_fd, b'foreign replacement must survive\\n')\n"
        + "    os.fsync(replacement_fd)\n"
        + "    os.close(replacement_fd)\n"
        + "    os._exit(77)\n"
    )
    assert needle in source
    gate_path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
    _git(repo, "add", "scripts/verification_report_gate.py")
    _git(repo, "commit", "-q", "-m", "test: inject candidate name substitution")

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body,
    )

    assert result.returncode == 77
    records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["state"] == "publishing"
    sent = repo / "coordination/mailbox/sent"
    moved = sent / ".moved-invocation-candidate.tmp"
    assert moved.exists()
    assert "sha256:" + hashlib.sha256(moved.read_bytes()).hexdigest() == record[
        "candidate_digest"
    ]
    substituted = sent / record["candidate_name"]
    assert substituted.read_bytes() == b"foreign replacement must survive\n"
    assert not (repo / record["path"]).exists()


def test_publication_cli_published_replay_cleans_unowned_second_candidate(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    final_relative, raw = _fixed_report(head, body)
    sent = repo / "coordination/mailbox/sent"
    first = sent / ".first-candidate.tmp"
    first.write_bytes(raw)
    first.chmod(0o600)
    command = [
        repo / ".venv/bin/python",
        "-E",
        "-s",
        "-S",
        "-B",
        repo / "scripts/verification_report_gate.py",
        "publish",
        "--repo-root",
        repo,
        "--candidate",
        first,
        "--final-relative",
        final_relative,
    ]
    first_result = _run(command, repo)
    assert first_result.returncode == 0, first_result.stderr
    assert not first.exists()
    assert (repo / final_relative).exists()

    second = sent / ".second-candidate.tmp"
    second.write_bytes(raw)
    second.chmod(0o600)
    command[command.index(first)] = second
    replay = _run(command, repo)

    assert replay.returncode == 6
    assert "publication_status_required" in replay.stderr
    assert not second.exists()
    assert (repo / final_relative).read_bytes() == raw


def test_publication_cli_cancelled_link_conflict_cleans_candidate(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    final_relative, raw = _fixed_report(head, body)
    candidate = repo / "coordination/mailbox/sent/.link-conflict-candidate.tmp"
    candidate.write_bytes(raw)
    candidate.chmod(0o600)
    final = repo / final_relative
    conflicting = b"existing untracked final must survive\n"
    final.write_bytes(conflicting)
    final.chmod(0o600)

    result = _run(
        [
            repo / ".venv/bin/python",
            "-E",
            "-s",
            "-S",
            "-B",
            repo / "scripts/verification_report_gate.py",
            "publish",
            "--repo-root",
            repo,
            "--candidate",
            candidate,
            "--final-relative",
            final_relative,
        ],
        repo,
    )

    assert result.returncode == 4
    assert "publication_path_exists" in result.stderr
    assert not candidate.exists()
    assert final.read_bytes() == conflicting
    records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(records) == 1
    assert json.loads(records[0].read_text(encoding="utf-8"))["state"] == "ready"


def _resume_command_from_failure(stderr: str) -> list[str]:
    commands = [
        line.split("run: ", 1)[1]
        for line in stderr.splitlines()
        if "run: " in line
    ]
    assert len(commands) == 1
    arguments = shlex.split(commands[0])
    assert arguments[:2] == ["/usr/bin/env", "-i"]
    assert "resume" in arguments
    assert "publish" not in arguments
    assert "status" not in arguments
    assert "ROOT" not in commands[0]
    return arguments


@pytest.mark.parametrize("failure", ["object-write", "index-update"])
def test_verification_send_event_real_git_failure_is_explicitly_resumable(
    tmp_path: Path,
    repo_root: Path,
    failure: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    body = body.replace("→ fixture passed", f"→ fixture passed {failure}")
    object_modes: dict[Path, int] = {}
    index_lock = repo / ".git/index.lock"
    lock_sentinel = b"task-6-real-index-lock\n"
    lock_survived = False
    if failure == "object-write":
        objects = repo / ".git/objects"
        object_directories = [
            objects,
            *[path for path in objects.rglob("*") if path.is_dir()],
        ]
        object_modes = {
            path: stat.S_IMODE(path.stat().st_mode) for path in object_directories
        }
        for path in sorted(object_directories, key=lambda item: len(item.parts), reverse=True):
            path.chmod(0o500)
        assert not os.access(objects, os.W_OK)
    else:
        index_lock.write_bytes(lock_sentinel)
        index_lock.chmod(0o600)
    try:
        result = _run(
            _verification_command(repo_root / "coordination/bin/send-event", head),
            repo,
            input_text=body,
        )
        if failure == "index-update":
            lock_survived = index_lock.read_bytes() == lock_sentinel
    finally:
        for path, mode in sorted(object_modes.items(), key=lambda item: len(item[0].parts)):
            path.chmod(mode)
        if index_lock.exists():
            index_lock.unlink()

    assert result.returncode == 5, result.stderr
    assert result.stdout == ""
    assert result.stderr.count("publication_resumable:") == 1
    assert "publication remains recoverable" in result.stderr
    assert "publication_status_required" not in result.stderr
    resume_command = _resume_command_from_failure(result.stderr)
    assert resume_command == [
        "/usr/bin/env",
        "-i",
        "PATH=/usr/bin:/bin",
        "LANG=C",
        "LC_ALL=C",
        str(repo / ".venv/bin/python"),
        "-E",
        "-s",
        "-S",
        "-B",
        str(repo / "scripts/verification_report_gate.py"),
        "resume",
        "--repo-root",
        str(repo),
        "--task-id",
        "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
    ]
    records = list(
        (repo / ".codex/runtime/lane-v-report-publications/v1").glob("*.json")
    )
    assert len(records) == 1
    record_path = records[0]
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["state"] == "publishing"
    for field in (
        "path",
        "candidate_digest",
        "candidate_name",
        "candidate_device",
        "candidate_inode",
        "index_blob_oid",
        "index_mode",
        "index_stage",
    ):
        assert record[field] is not None
    candidate = repo / "coordination/mailbox/sent" / record["candidate_name"]
    final = repo / record["path"]
    candidate_stat = candidate.stat()
    final_stat = final.stat()
    assert (candidate_stat.st_dev, candidate_stat.st_ino, candidate_stat.st_nlink) == (
        final_stat.st_dev,
        final_stat.st_ino,
        2,
    )
    assert record["candidate_digest"] == (
        "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest()
    )
    assert _git(repo, "ls-files", "--stage", "--", record["path"]) == ""
    object_read = subprocess.run(
        ["/usr/bin/git", "-C", str(repo), "cat-file", "blob", record["index_blob_oid"]],
        capture_output=True,
        check=False,
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
    )
    if failure == "object-write":
        assert object_read.returncode != 0
    else:
        assert lock_survived is True
        assert object_read.returncode == 0
        assert object_read.stdout == candidate.read_bytes()

    resumed = _run(resume_command, repo)

    assert resumed.returncode == 0, resumed.stderr
    assert resumed.stdout.strip() == record["path"]
    completed = json.loads(record_path.read_text(encoding="utf-8"))
    assert completed["state"] == "published"
    assert not candidate.exists()
    assert final.stat().st_nlink == 1
    assert _git(repo, "ls-files", "--stage", "--", record["path"]) == (
        f"100644 {record['index_blob_oid']} 0\t{record['path']}"
    )


def test_verification_send_event_lost_stdout_uses_status_not_republish(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    source = gate_path.read_text(encoding="utf-8")
    needle = '    """Fault-injection seam for crash-boundary regression tests."""\n'
    replacement = (
        needle
        + "    if label == 'after_stdout':\n"
        + "        raise RuntimeError('injected lost stdout crash')\n"
    )
    gate_path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
    _git(repo, "add", "scripts/verification_report_gate.py")
    _git(repo, "commit", "-q", "-m", "test: inject lost stdout")

    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "operator2",
            "all",
            "verification-report",
            "Lane V verification report — commit",
            f"`{head}`",
        ],
        repo,
        input_text=body,
    )
    assert result.returncode == 6
    assert "use the resume command above" not in result.stderr
    assert (
        f"{repo / 'scripts/verification_report_gate.py'} status "
        f"--repo-root {repo} --task-id "
    ) in result.stderr
    # The injected crash represents output loss in one process. Restore the
    # normal CLI implementation before performing the independent status read.
    gate_path.write_text(source, encoding="utf-8")

    status = _run(
        [
            repo / ".venv/bin/python",
            repo / "scripts/verification_report_gate.py",
            "status",
            "--repo-root",
            repo,
            "--task-id",
            "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
        ],
        repo,
    )
    assert status.returncode == 0, status.stderr
    parsed = json.loads(status.stdout)
    assert parsed["state"] == "published"
    assert parsed["file_witness_match"] is True
    assert parsed["staged_blob_match"] is True
    assert parsed["path"] in _git(repo, "diff", "--cached", "--name-only")


def test_verification_send_event_branch_contains_no_shell_git_add(repo_root: Path) -> None:
    source = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert source.startswith("#!/bin/bash -p\nPATH=/usr/bin:/bin\n")
    assert 'add -f -- "$REL"' not in source
    assert "send-event-finalize" in source


def test_provider_neutral_gate_and_send_event_have_task_only_source_cli_closure(
    tmp_path: Path,
    repo_root: Path,
) -> None:
    gate_path = repo_root / "scripts" / "verification_report_gate.py"
    gate_source = gate_path.read_text(encoding="utf-8")
    send_source = (repo_root / "coordination" / "bin" / "send-event").read_text(
        encoding="utf-8"
    )

    rejected = _run(
        [
            sys.executable,
            gate_path,
            "status",
            "--repo-root",
            tmp_path,
            "--task-id",
            "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
            "--receipt-id",
            "opr1:" + "1" * 64,
        ],
        repo_root,
    )

    assert rejected.returncode != 0
    assert "unrecognized arguments: --receipt-id" in rejected.stderr
    for forbidden in (
        "ReceiptStore",
        "ReceiptRecord",
        "receipt_store_factory",
        '"reconciled"',
        "opus_review_bridge",
        "codex-lane-v",
        "claude-lane-v",
        "Opus receipt ID",
        "Authorization identity",
    ):
        assert forbidden not in gate_source
    assert "for SOURCE in verification_report_gate.py kernel_activation.py; do" in send_source
    assert "opus_review_receipts.py" not in send_source
    assert "opus_review_bridge.py" not in send_source


def _assert_no_verification_publication(repo: Path) -> None:
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert not list(
        (repo / "coordination/mailbox/sent").glob("*-verification-report.md")
    )
    assert not list((repo / "coordination/mailbox/sent").glob(".*.tmp"))
    assert not list((repo / "coordination/mailbox/sent").glob(".trusted-*"))
    assert not list((repo / "coordination/mailbox/sent").glob(".pycache.*"))
    assert not list((repo / "coordination/mailbox/sent").glob(".published.*"))


def _assert_only_unowned_candidate_preserved(repo: Path) -> None:
    sent = repo / "coordination/mailbox/sent"
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert not list(sent.glob("*-verification-report.md"))
    candidates = list(sent.glob(".*-verification-report.*.tmp"))
    assert len(candidates) == 1
    assert "VERDICT: GO" in candidates[0].read_text(encoding="utf-8")
    assert not list(sent.glob(".trusted-*"))
    assert not list(sent.glob(".pycache.*"))
    assert not list(sent.glob(".published.*"))


def test_verification_send_event_invalid_report_creates_no_file_or_index(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body.replace("VERDICT: GO", "VERDICT: MAYBE"),
    )

    assert result.returncode != 0
    _assert_no_verification_publication(repo)


def test_verification_send_event_concurrent_same_second_publish_is_no_replace(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    command = _verification_command(repo_root / "coordination/bin/send-event", head)
    barrier = threading.Barrier(3)
    results: list[subprocess.CompletedProcess[str]] = []

    def publish() -> None:
        barrier.wait()
        results.append(_run(command, repo, input_text=body))

    workers = [threading.Thread(target=publish) for _ in range(2)]
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join(timeout=30)
        assert not worker.is_alive()

    assert sorted(result.returncode == 0 for result in results) == [False, True]
    reports = list(
        (repo / "coordination/mailbox/sent").glob("*-verification-report.md")
    )
    assert len(reports) == 1
    assert reports[0].relative_to(repo).as_posix() in _git(
        repo, "diff", "--cached", "--name-only"
    )
    assert reports[0].read_text(encoding="utf-8").count("VERDICT: GO") == 1


@pytest.mark.parametrize(
    "shape",
    ["empty", "multiline", "absolute", "traversal", "wrong-dir", "wrong-suffix"],
)
def test_verification_send_event_rejects_malformed_publisher_stdout(
    tmp_path: Path, repo_root: Path, shape: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    expressions = {
        "empty": "pass",
        "multiline": "print(relative); print('extra')",
        "absolute": "print('/' + relative)",
        "traversal": (
            "print('coordination/mailbox/sent/../sent/' + "
            "relative.rsplit('/', 1)[1])"
        ),
        "wrong-dir": (
            "print(relative.replace('coordination/mailbox/sent/', "
            "'coordination/mailbox/other/', 1))"
        ),
        "wrong-suffix": "print(relative[:-3] + '.txt')",
    }
    gate_path.write_text(
        "import sys\n"
        "relative = sys.argv[sys.argv.index('--final-relative') + 1]\n"
        f"{expressions[shape]}\n",
        encoding="utf-8",
    )
    _git(repo, "add", "scripts/verification_report_gate.py")
    _git(repo, "commit", "-q", "-m", f"test: malformed publisher {shape}")

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body,
    )

    assert result.returncode == 4
    _assert_only_unowned_candidate_preserved(repo)


@pytest.mark.parametrize(
    "candidate_kind", ["outside", "alias", "same-basename-wrong-parent"]
)
def test_publication_cli_rejects_noncanonical_candidate_locations(
    tmp_path: Path,
    repo_root: Path,
    candidate_kind: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    final_relative, raw = _fixed_report(head, body)
    name = ".candidate-location.tmp"
    if candidate_kind == "outside":
        candidate = tmp_path / name
        candidate_arg = str(candidate)
    elif candidate_kind == "alias":
        candidate = repo / "coordination/mailbox/sent" / name
        candidate_arg = str(
            repo / "coordination/mailbox/sent/../sent" / name
        )
    else:
        candidate = repo / "other" / name
        candidate.parent.mkdir()
        candidate_arg = str(candidate)
    candidate.write_bytes(raw)
    candidate.chmod(0o600)

    result = _run(
        [
            repo / ".venv/bin/python",
            "-E",
            "-s",
            "-S",
            "-B",
            repo / "scripts/verification_report_gate.py",
            "publish",
            "--repo-root",
            repo,
            "--candidate",
            candidate_arg,
            "--final-relative",
            final_relative,
        ],
        repo,
    )

    assert result.returncode == 4
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert not (repo / final_relative).exists()


@pytest.mark.parametrize(
    "source_failure",
    ["missing", "nonblob", "symlink", "missing-publish"],
)
def test_verification_send_event_fails_closed_on_untrusted_bootstrap_source(
    tmp_path: Path,
    repo_root: Path,
    source_failure: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    gate_path = repo / "scripts/verification_report_gate.py"
    if source_failure == "missing":
        gate_path.unlink()
    elif source_failure == "nonblob":
        gate_path.unlink()
        gate_path.mkdir()
        (gate_path / "payload.py").write_text("pass\n", encoding="utf-8")
    elif source_failure == "symlink":
        gate_path.unlink()
        gate_path.symlink_to("feature.py")
    else:
        gate_path.write_text("# publisher intentionally absent\n", encoding="utf-8")
    _git(repo, "add", "-A", "scripts")
    _git(repo, "commit", "-q", "-m", f"test: source failure {source_failure}")

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        input_text=body,
    )

    assert result.returncode != 0
    if source_failure == "missing-publish":
        _assert_only_unowned_candidate_preserved(repo)
    else:
        _assert_no_verification_publication(repo)


def test_verification_send_event_uses_primary_head_from_real_linked_worktree(
    tmp_path: Path, repo_root: Path
) -> None:
    primary = tmp_path / "primary"
    primary.mkdir()
    _init_repo(primary)
    head, body = _verification_shell_fixture(primary, repo_root)
    linked = tmp_path / "linked"
    _git(primary, "worktree", "add", "-q", "-b", "linked-test", str(linked))
    marker = tmp_path / "linked-source-ran"
    (linked / "scripts/verification_report_gate.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
        "raise RuntimeError('linked working source executed')\n",
        encoding="utf-8",
    )

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        linked,
        input_text=body,
    )

    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    reports = list(
        (linked / "coordination/mailbox/sent").glob("*-verification-report.md")
    )
    assert len(reports) == 1
    assert reports[0].relative_to(linked).as_posix() in _git(
        linked, "diff", "--cached", "--name-only"
    )


def test_verification_send_event_rejects_common_parent_that_is_linked_worktree(
    tmp_path: Path, repo_root: Path
) -> None:
    primary = tmp_path / "original-primary"
    primary.mkdir()
    _init_repo(primary)
    head, body = _verification_shell_fixture(primary, repo_root)
    evil_staging = tmp_path / "evil-staging"
    current = tmp_path / "current"
    _git(primary, "worktree", "add", "-q", "-b", "evil", str(evil_staging))
    _git(primary, "worktree", "add", "-q", "-b", "current", str(current))
    evil_admin_old = Path(
        (evil_staging / ".git").read_text(encoding="utf-8").split(": ", 1)[1].strip()
    )
    current_admin_old = Path(
        (current / ".git").read_text(encoding="utf-8").split(": ", 1)[1].strip()
    )
    evil_root = tmp_path / "forged-common-parent"
    evil_root.mkdir()
    common = evil_root / ".git-common"
    (primary / ".git").rename(common)
    shutil.copytree(evil_staging, evil_root, dirs_exist_ok=True)
    evil_admin = common / "worktrees" / evil_admin_old.name
    current_admin = common / "worktrees" / current_admin_old.name
    (evil_root / ".git").write_text(
        f"gitdir: {evil_admin}\n", encoding="utf-8"
    )
    (current / ".git").write_text(
        f"gitdir: {current_admin}\n", encoding="utf-8"
    )
    (evil_admin / "gitdir").write_text(
        f"{evil_root / '.git'}\n", encoding="utf-8"
    )
    (current_admin / "gitdir").write_text(
        f"{current / '.git'}\n", encoding="utf-8"
    )
    marker = tmp_path / "forged-python-ran"
    forged_python = evil_root / ".venv/bin/python"
    forged_python.parent.mkdir(parents=True, exist_ok=True)
    forged_python.write_text(
        f"#!/bin/sh\n/usr/bin/touch {marker}\nexit 99\n", encoding="utf-8"
    )
    forged_python.chmod(0o755)

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        current,
        input_text=body,
    )

    assert result.returncode == 4
    assert "does not identify a primary Pipeline checkout" in result.stderr
    assert not marker.exists()
    _assert_no_verification_publication(current)


def test_verification_send_event_ignores_mutable_source_and_python_shadows(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    head, body = _verification_shell_fixture(repo, repo_root)
    marker = tmp_path / "mutable-or-shadow-source-ran"
    malicious = (
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
        "raise RuntimeError('mutable source executed')\n"
    )
    gate_path = repo / "scripts/verification_report_gate.py"
    gate_path.write_text(malicious, encoding="utf-8")
    for name in ("json.py", "hashlib.py", "sitecustomize.py"):
        (repo / "scripts" / name).write_text(malicious, encoding="utf-8")
    cache = repo / "scripts/__pycache__"
    cache.mkdir()
    malicious_source = tmp_path / "verification_report_gate.py"
    malicious_source.write_text(malicious, encoding="utf-8")
    py_compile.compile(
        str(malicious_source),
        cfile=str(
            cache
            / f"verification_report_gate.{sys.implementation.cache_tag}.pyc"
        ),
        doraise=True,
    )
    shadow = tmp_path / "python-shadow"
    shadow.mkdir()
    (shadow / "sitecustomize.py").write_text(malicious, encoding="utf-8")

    result = _run(
        _verification_command(repo_root / "coordination/bin/send-event", head),
        repo,
        env={
            "PYTHONPATH": str(shadow),
            "PYTHONSTARTUP": str(shadow / "sitecustomize.py"),
            "PYTHONPYCACHEPREFIX": str(repo / "scripts/__pycache__"),
        },
        input_text=body,
    )

    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    reports = list(
        (repo / "coordination/mailbox/sent").glob("*-verification-report.md")
    )
    assert len(reports) == 1


@pytest.mark.parametrize(
    ("hook_path", "marker_dir"),
    [
        (".claude/hooks/update-state.sh", ".claude/hooks"),
        (".codex/hooks/update-state.sh", ".codex/hooks"),
    ],
)
def test_update_state_syncs_markerless_clean_seeded_seat_index(
    tmp_path: Path, repo_root: Path, hook_path: str, marker_dir: str
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    hook_destination = repo / hook_path
    hook_destination.parent.mkdir(parents=True)
    hook_destination.write_text((repo_root / hook_path).read_text(encoding="utf-8"), encoding="utf-8")
    hook_destination.chmod(0o755)

    (repo / "coordination" / "mailbox" / "sent").mkdir(parents=True)
    (repo / "coordination" / "mailbox" / "seen").mkdir(parents=True)
    (repo / "coordination" / "presence").mkdir(parents=True)
    (repo / "tracked.txt").write_text("before\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")

    seat_index = repo / ".git" / "index-director"
    _git(repo, "read-tree", f"--index-output={seat_index}", "HEAD")
    assert not (repo / marker_dir / f".last-index-sync-{seat_index.name}").exists()

    (repo / "tracked.txt").write_text("after\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "peer commit")
    head_tree = _git(repo, "show", "-s", "--format=%T", "HEAD")

    result = _run([hook_destination], repo, env={"GIT_INDEX_FILE": str(seat_index)})

    assert result.returncode == 0, result.stderr
    marker = repo / marker_dir / f".last-index-sync-{seat_index.name}"
    assert marker.read_text(encoding="utf-8").strip() == _git(repo, "rev-parse", "HEAD")
    index_tree = _git(repo, "write-tree", env={"GIT_INDEX_FILE": str(seat_index)})
    assert index_tree == head_tree


@pytest.mark.parametrize(
    "hook_path",
    [
        ".claude/hooks/update-state.sh",
        ".codex/hooks/update-state.sh",
    ],
)
def test_update_state_does_not_delete_index_lock_based_only_on_age(
    tmp_path: Path,
    repo_root: Path,
    hook_path: str,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    hook_destination = repo / hook_path
    hook_destination.parent.mkdir(parents=True)
    hook_destination.write_text(
        (repo_root / hook_path).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    hook_destination.chmod(0o755)

    (repo / "coordination/mailbox/sent").mkdir(parents=True)
    (repo / "coordination/mailbox/seen").mkdir()
    (repo / "coordination/presence").mkdir()
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")

    index_lock = repo / ".git/index.lock"
    index_lock.write_text("active-or-unknown\n", encoding="utf-8")
    os.utime(index_lock, (0, 0))

    result = _run([hook_destination], repo)

    assert result.returncode == 0, result.stderr
    assert index_lock.exists()
