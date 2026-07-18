# ChatGPT Pro Consultation FD-First TOCTOU Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended for this tightly coupled security change) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the filesystem-dependent pre-open inode snapshot with FD-first state and lock validation that behaves identically on Linux and macOS.

**Architecture:** Pin the Git common directory FD for each locked transaction, open fixed state and lock names relative to it with no-follow and nonblocking flags, and validate the live FD before use. Recheck the lock binding after `flock` so a replacement while waiting cannot reach state access; keep state schema, CLI, and one-send behavior unchanged.

**Tech Stack:** Python 3.13, `os`/`fcntl`/`stat`/`tempfile`, pytest, GitHub Actions Ubuntu 24.04 or a local Linux container.

## Global Constraints

- Production changes are limited to `scripts/chatgpt_pro_consult.py`.
- Test changes are limited to `tests/unit/test_chatgpt_pro_consult.py` unless an existing integration contract fails.
- Preserve `O_NOFOLLOW`, `O_NONBLOCK`, regular-file checks, exact mode `0600`, atomic state replacement, content-free errors, and terminal one-send semantics.
- Only a lock FD created by `O_CREAT|O_EXCL` may be normalized with `fchmod`; never repair an existing unsafe object.
- A same-mode object present before the first open is the current object; do not claim protection from arbitrary same-account directory control.
- The Python kernel plus canonical consultation skill must remain at most 350 lines.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest commands.
- Each stage/commit step requires the user's separate Git authority; Docker/network, mailbox publication, and push are separate effects.
- The director authors the change; a non-author operator alone issues GO/NITS/FAIL.

---

### Task 1: Pin deterministic RED and retained substitution coverage

**Files:**
- Modify: `tests/unit/test_chatgpt_pro_consult.py:274-344`

**Interfaces:**
- Consumes: `consult.reserve`, fixed `STATE_NAME`/`LOCK_NAME`, and the existing `_paths` fixture helper.
- Produces: FD-first ordering, post-open binding, and post-flock rebind acceptance tests used by Task 2.

- [ ] **Step 1: Narrow the pre-open unsafe-object cases**

Keep the two existing pre-open tests, but parameterize them only with `fifo` and
`wrong_mode`. Make their `os.open` wrappers accept `dir_fd` and identify the
target by `Path(path).name`, so they work before and after the production API
becomes directory-relative:

```python
@pytest.mark.parametrize("replacement", ("fifo", "wrong_mode"))
def test_state_unsafe_object_present_before_open_is_rejected_before_read(
    repo: Path, monkeypatch, replacement: str
):
    consult.reserve(repo, _raw(VALID))
    state_path, _ = _paths(repo)
    real_open = consult.os.open
    swapped = False

    def swap_open(
        path: object, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        nonlocal swapped
        if Path(path).name == consult.STATE_NAME and not flags & os.O_CREAT:
            assert flags & os.O_NONBLOCK
            state_path.unlink()
            if replacement == "fifo":
                os.mkfifo(state_path, 0o600)
            else:
                state_path.write_bytes(b"substituted")
                state_path.chmod(0o644)
            swapped = True
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(consult.os, "open", swap_open)
    monkeypatch.setattr(
        consult.os,
        "fdopen",
        lambda *_args, **_kwargs: pytest.fail("unsafe state was opened for read"),
    )
    with pytest.raises(consult.ConsultError, match="^state_path_invalid$"):
        consult.reserve(repo, _raw(VALID))
    assert swapped is True


@pytest.mark.parametrize("replacement", ("fifo", "wrong_mode"))
def test_lock_unsafe_object_present_before_open_is_rejected_before_flock(
    repo: Path, monkeypatch, replacement: str
):
    consult.reserve(repo, _raw(VALID))
    _, lock_path = _paths(repo)
    real_open = consult.os.open
    swapped = False

    def swap_open(
        path: object, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        nonlocal swapped
        if Path(path).name == consult.LOCK_NAME and flags & os.O_CREAT:
            assert flags & os.O_NONBLOCK
            lock_path.unlink()
            if replacement == "fifo":
                os.mkfifo(lock_path, 0o600)
            else:
                lock_path.write_bytes(b"substituted")
                lock_path.chmod(0o644)
            swapped = True
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(consult.os, "open", swap_open)
    monkeypatch.setattr(
        consult.fcntl,
        "flock",
        lambda *_args, **_kwargs: pytest.fail("unsafe lock reached flock"),
    )
    with pytest.raises(consult.ConsultError, match="^state_path_invalid$"):
        consult.reserve(repo, _raw(VALID))
    assert swapped is True
    if replacement != "fifo":
        assert lock_path.read_bytes() == b"substituted"
        assert stat.S_IMODE(lock_path.lstat().st_mode) == 0o644
```

- [ ] **Step 2: Add FD-first ordering RED tests**

```python
@pytest.mark.parametrize("path_index", (0, 1), ids=("state", "lock"))
def test_state_and_lock_are_opened_before_path_metadata(
    repo: Path, monkeypatch, path_index: int
):
    consult.reserve(repo, _raw(VALID))
    target = _paths(repo)[path_index]
    target_name = (consult.STATE_NAME, consult.LOCK_NAME)[path_index]
    real_open = consult.os.open
    real_lstat = Path.lstat
    target_opened = False

    def track_open(
        path: object, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        nonlocal target_opened
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path).name == target_name:
            target_opened = True
        return fd

    def reject_preopen_lstat(path: Path):
        if path == target and not target_opened:
            pytest.fail("target path metadata inspected before open")
        return real_lstat(path)

    monkeypatch.setattr(consult.os, "open", track_open)
    monkeypatch.setattr(Path, "lstat", reject_preopen_lstat)
    assert consult.reserve(repo, _raw(VALID))["created"] is False
```

- [ ] **Step 3: Add retained post-open same-mode binding coverage**

```python
@pytest.mark.parametrize("path_index", (0, 1), ids=("state", "lock"))
def test_same_mode_replacement_after_open_is_rejected_before_use(
    repo: Path, monkeypatch, path_index: int
):
    consult.reserve(repo, _raw(VALID))
    target = _paths(repo)[path_index]
    target_name = (consult.STATE_NAME, consult.LOCK_NAME)[path_index]
    real_open = consult.os.open
    swapped = False

    def swap_after_open(
        path: object, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        nonlocal swapped
        if dir_fd is None:
            fd = real_open(path, flags, mode)
        else:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if Path(path).name == target_name and not swapped:
            target.unlink()
            target.write_bytes(b"substituted")
            target.chmod(0o600)
            swapped = True
        return fd

    monkeypatch.setattr(consult.os, "open", swap_after_open)
    if path_index == 0:
        monkeypatch.setattr(
            consult.os,
            "fdopen",
            lambda *_args, **_kwargs: pytest.fail("replacement reached state read"),
        )
    else:
        monkeypatch.setattr(
            consult.fcntl,
            "flock",
            lambda *_args, **_kwargs: pytest.fail("replacement reached flock"),
        )
    with pytest.raises(consult.ConsultError, match="^state_path_invalid$"):
        consult.reserve(repo, _raw(VALID))
    assert swapped is True
```

- [ ] **Step 4: Add post-flock rebind RED coverage**

```python
def test_lock_replacement_while_waiting_is_rejected_before_state_read(
    repo: Path, monkeypatch
):
    consult.reserve(repo, _raw(VALID))
    _, lock_path = _paths(repo)
    real_flock = consult.fcntl.flock
    swapped = False

    def swap_before_return(fd: int, operation: int) -> None:
        nonlocal swapped
        real_flock(fd, operation)
        lock_path.unlink()
        lock_path.write_bytes(b"substituted")
        lock_path.chmod(0o600)
        swapped = True

    monkeypatch.setattr(consult.fcntl, "flock", swap_before_return)
    monkeypatch.setattr(
        consult,
        "_read",
        lambda *_args: pytest.fail("state read after lock replacement"),
    )
    with pytest.raises(consult.ConsultError, match="^state_path_invalid$"):
        consult.reserve(repo, _raw(VALID))
    assert swapped is True
```

- [ ] **Step 5: Keep the write-failure probe compatible with dirfd replacement**

Update the existing monkeypatch in `test_finish_write_failure_leaves_reserved_terminal`
so it accepts the production call's keyword-only directory arguments while
preserving the same simulated `OSError`:

```python
def fail_replace(
    source: object,
    destination: object,
    *,
    src_dir_fd: int | None = None,
    dst_dir_fd: int | None = None,
) -> None:
    raise OSError("simulated write failure")
```

- [ ] **Step 6: Run the focused tests and confirm non-vacuous RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py -k 'unsafe_object_present or opened_before_path_metadata or same_mode_replacement_after_open or replacement_while_waiting' -q
```

Expected: the FIFO, wrong-mode, and retained post-open cases pass; both
`opened_before_path_metadata` cases fail because `_fixed` calls `lstat` first;
the post-flock case fails because current `_locked` reaches the `_read` sentinel.

- [ ] **Step 7: Stop for test-only commit authority**

After approval, stage only `tests/unit/test_chatgpt_pro_consult.py`, inspect
`git diff --cached --name-status`, and commit with:

```bash
env -u GIT_INDEX_FILE git commit -m "test(consult): pin fd-first TOCTOU boundaries"
```

### Task 2: Implement FD-first open, binding, and post-flock validation

**Files:**
- Modify: `scripts/chatgpt_pro_consult.py:91-222`
- Test: `tests/unit/test_chatgpt_pro_consult.py`

**Interfaces:**
- Consumes: Task 1's ordering and substitution tests.
- Produces: `_bound(fd: int, common_fd: int, name: str) -> bool`, `_read(common_fd: int)`, `_write(common: Path, common_fd: int, state)`, and `_locked(common: Path, action)` with two-argument actions.

- [ ] **Step 1: Replace pre-open snapshots with directory-relative helpers**

Replace `_fixed` and the old `_bound` with:

```python
def _named(common_fd: int, name: str):
    return os.stat(name, dir_fd=common_fd, follow_symlinks=False)


def _open_error(common_fd: int, name: str, exc: OSError):
    try:
        metadata = _named(common_fd, name)
    except OSError:
        raise ConsultError("io_failed") from exc
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o600:
        raise ConsultError("state_path_invalid") from exc
    raise ConsultError("io_failed") from exc


def _bound(fd: int, common_fd: int, name: str) -> bool:
    opened = os.fstat(fd)
    try:
        current = _named(common_fd, name)
    except FileNotFoundError:
        return False
    identity = opened.st_dev, opened.st_ino
    return (
        stat.S_ISREG(opened.st_mode)
        and stat.S_IMODE(opened.st_mode) == 0o600
        and identity == (current.st_dev, current.st_ino)
    )
```

- [ ] **Step 2: Open and read state FD-first**

Replace `_read` with:

```python
def _read(common_fd: int) -> dict[str, dict[str, str]]:
    fd = -1
    try:
        try:
            fd = os.open(
                STATE_NAME,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=common_fd,
            )
        except FileNotFoundError:
            return {}
        except OSError as exc:
            _open_error(common_fd, STATE_NAME, exc)
        if not _bound(fd, common_fd, STATE_NAME):
            raise ConsultError("state_path_invalid")
        stream = os.fdopen(fd, "rb")
        fd = -1
        with stream:
            value = _loads(stream.read())
    except ConsultError as exc:
        if exc.code == "invalid_json":
            raise ConsultError("state_corrupt") from exc
        raise
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    finally:
        if fd >= 0:
            os.close(fd)
    if not isinstance(value, dict):
        raise ConsultError("state_corrupt")
    for key, record in value.items():
        if not isinstance(key, str) or not KEY_RE.fullmatch(key):
            raise ConsultError("state_corrupt")
        if not isinstance(record, dict) or set(record) != {"hash", "status"}:
            raise ConsultError("state_corrupt")
        request_hash, status_value = record.get("hash"), record.get("status")
        if not isinstance(request_hash, str) or not HASH_RE.fullmatch(request_hash):
            raise ConsultError("state_corrupt")
        if not isinstance(status_value, str) or status_value not in TERMINAL:
            raise ConsultError("state_corrupt")
    return value
```

- [ ] **Step 3: Create or open the lock without repairing unsafe existing objects**

Add:

```python
def _open_lock(common_fd: int) -> int:
    fd = -1
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        try:
            fd = os.open(
                LOCK_NAME,
                flags | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=common_fd,
            )
            os.fchmod(fd, 0o600)
        except FileExistsError:
            fd = os.open(LOCK_NAME, flags, dir_fd=common_fd)
        if not _bound(fd, common_fd, LOCK_NAME):
            raise ConsultError("state_path_invalid")
        return fd
    except ConsultError:
        if fd >= 0:
            os.close(fd)
        raise
    except OSError as exc:
        if fd >= 0:
            os.close(fd)
        _open_error(common_fd, LOCK_NAME, exc)
```

- [ ] **Step 4: Reuse the pinned directory FD for atomic state replacement**

Change `_write` to accept `common_fd`, replace the destination relative to that
FD, and fsync the already-open directory:

```python
def _write(common: Path, common_fd: int, state: dict[str, dict[str, str]]) -> None:
    payload = json.dumps(
        state, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"
    fd, temporary = -1, ""
    try:
        fd, temporary = tempfile.mkstemp(prefix=".chatgpt-pro-consult.", dir=common)
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(payload):
            count = os.write(fd, payload[offset:])
            if not count:
                raise OSError("short write")
            offset += count
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(temporary, STATE_NAME, dst_dir_fd=common_fd)
        temporary = ""
        os.fsync(common_fd)
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
        if temporary:
            try:
                os.unlink(temporary)
            except OSError:
                pass
```

- [ ] **Step 5: Pin the directory, rebind after flock, and pass it to actions**

Replace `_locked` and update the two nested `apply` functions:

```python
def _locked(common: Path, action):
    common_fd = lock_fd = -1
    try:
        common_fd = os.open(
            common, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        lock_fd = _open_lock(common_fd)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if not _bound(lock_fd, common_fd, LOCK_NAME):
            raise ConsultError("state_path_invalid")
        return action(_read(common_fd), common_fd)
    except ConsultError:
        raise
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    finally:
        if lock_fd >= 0:
            os.close(lock_fd)
        if common_fd >= 0:
            os.close(common_fd)
```

Update `reserve` and `finish` to pass the pinned directory FD without changing
their transition or result contracts:

```python
def reserve(repo_root: Path | str, raw_payload: bytes) -> dict[str, object]:
    key, request_hash = _normalize(raw_payload)
    common = _common(repo_root)
    def apply(state, common_fd):
        existing = state.get(key)
        if existing:
            if existing["hash"] != request_hash:
                raise ConsultError("key_conflict")
            return {"ok": True, "key": key, "hash": request_hash, "status": existing["status"], "created": False}
        state[key] = {"hash": request_hash, "status": "reserved"}
        _write(common, common_fd, state)
        return {"ok": True, "key": key, "hash": request_hash, "status": "reserved", "created": True}
    return _locked(common, apply)


def finish(repo_root: Path | str, key: str, request_hash: str, status: str) -> dict[str, object]:
    if not isinstance(key, str) or not KEY_RE.fullmatch(key):
        raise ConsultError("invalid_key")
    if (not isinstance(request_hash, str) or not HASH_RE.fullmatch(request_hash)
            or not isinstance(status, str) or status not in {"sent", "failed"}):
        raise ConsultError("finish_rejected")
    common = _common(repo_root)
    def apply(state, common_fd):
        existing = state.get(key)
        if not existing or existing["hash"] != request_hash or existing["status"] != "reserved":
            raise ConsultError("finish_rejected")
        state[key] = {"hash": request_hash, "status": status}
        _write(common, common_fd, state)
        return {"ok": True, "key": key, "hash": request_hash, "status": status}
    return _locked(common, apply)
```

- [ ] **Step 6: Run the focused test file**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py -q
```

Expected: all tests pass, including both ordering cases and the post-flock RED
case from Task 1.

- [ ] **Step 7: Check the compact package budget**

Run:

```bash
wc -l scripts/chatgpt_pro_consult.py .agents/skills/chatgpt-pro-consultation/SKILL.md
```

Expected: combined total at most 350 lines.

- [ ] **Step 8: Stop for implementation commit authority**

After approval, stage only the production and unit-test paths, inspect the
cached diff and name-status, and commit with:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(consult): validate state and lock fd-first"
```

### Task 3: Run complete local and Linux verification

**Files:**
- Verify: `scripts/chatgpt_pro_consult.py`
- Verify: `tests/unit/test_chatgpt_pro_consult.py`
- Verify unchanged contracts: `tests/integration/test_chatgpt_pro_consult_flow.py`
- Verify unchanged prompts: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**
- Consumes: Task 2's committed production/test range.
- Produces: exact macOS and Linux evidence for the later operator verify-request.

- [ ] **Step 1: Run focused cross-surface contracts**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/integration/test_chatgpt_pro_consult_flow.py tests/unit/test_protocol_prompt_sync.py -q
```

Expected: all selected tests pass and neither excluded path needs a change.

- [ ] **Step 2: Run the full local unit suite**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit --tb=short -q
```

Expected: zero failures.

- [ ] **Step 3: Run project smoke and diff checks**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: smoke ends `OK`, diff check is silent, and status contains no
unexpected path.

- [ ] **Step 4: Stop for Docker/network authority, then run Linux read-only**

After approval, run the full unit suite in a disposable Python 3.13 Linux
container with the repository mounted read-only:

```bash
docker run --rm --mount type=bind,src=/Users/hyungkoookkim/Pipeline,dst=/work,readonly --workdir /work python:3.13-slim sh -lc 'apt-get update && apt-get install -y git && git config --global --add safe.directory /work && python -m venv /tmp/venv && /tmp/venv/bin/pip install -r requirements-dev.txt && HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis PYTHONDONTWRITEBYTECODE=1 /tmp/venv/bin/python -m pytest -p no:cacheprovider tests/unit --tb=short -q'
```

Expected: zero failures on Linux. If Docker or dependency download is
unavailable, stop; do not substitute macOS evidence for Linux proof.

- [ ] **Step 5: Refresh protocol state and stop at the verify-request gate**

Run the director seat status, recent Git history, scoped status/diff, and read
every mailbox body newer than the original finding. Do not send a mailbox event
until the user separately authorizes the director as the named side-effect
executor. The later verify-request must bind the actual base/head, author
director, assigned non-author operator, allowed paths, this R-BRIEF, exact test
commands, Linux evidence, and exclusions.
