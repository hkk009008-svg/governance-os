#!/usr/bin/env bash
# SessionStart: R-START §15 smoke tripwire. Runs scripts/ci_smoke.py and reports
# PASS/FAIL as session context so a stale ARCHITECTURE.md / broken tree is caught
# before any non-trivial work.
#
# FAIL-OPEN: always exits 0 — NEVER blocks a session from starting. The 180s
# bound is enforced inside Python's subprocess.run(timeout=...) so it is portable
# (no dependency on GNU `timeout`/`gtimeout`, which macOS does not ship) and
# cannot leave the session hanging. Any large model weights expected cached locally
# should be pre-downloaded; a cold download would be bounded by the timeout.
set -uo pipefail

# Derive the repo root from this script's own location (.codex/hooks/ -> root),
# independent of cwd or machine. Fail-open if unresolvable.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)" || exit 0
[ -n "$ROOT" ] && cd "$ROOT" 2>/dev/null || exit 0

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "⚠️  §15 smoke SKIPPED — project venv missing at .venv/bin/python."
  echo "    Bootstrap with: /opt/homebrew/bin/python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 0
fi

# Reuse a passing smoke result only when both HEAD and the smoke-relevant
# working content are unchanged. The helper includes tracked/staged changes and
# untracked file bytes, and deliberately ignores ambient seat-index selection.
CACHE_FILE="$ROOT/.codex/hooks/.last-smoke-pass"
CACHE_KEY="$("$PY" - 2>/dev/null <<'PYKEY'
import hashlib
import os
import subprocess
from pathlib import Path

env = os.environ.copy()
env.pop("GIT_INDEX_FILE", None)


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    ).stdout


# `git diff` intentionally trusts skip-worktree/assume-unchanged bits. Smoke
# reads working-tree bytes, so caching under either flag could hide a real
# change. An empty key below means "run smoke, do not reuse or write cache."
for entry in git("ls-files", "-v", "-z").split(b"\0"):
    tag = entry[:1]
    if tag and (tag == b"S" or tag in b"abcdefghijklmnopqrstuvwxyz"):
        raise SystemExit(3)

digest = hashlib.sha256()
digest.update(git("rev-parse", "HEAD"))
for ref in ("main", "origin/main"):
    try:
        ref_value = git("rev-parse", "--verify", f"{ref}^{{commit}}")
    except subprocess.CalledProcessError:
        ref_value = b"missing\n"
    digest.update(ref.encode("ascii") + b"\0" + ref_value)
digest.update(git("diff", "--binary", "HEAD", "--"))
untracked = git("ls-files", "--others", "--exclude-standard", "--")
for relative in sorted(untracked.decode("utf-8", errors="surrogateescape").splitlines()):
    path = Path(relative)
    if path.is_symlink():
        kind = b"symlink\0"
        content = os.readlink(path).encode("utf-8", errors="surrogateescape")
    elif path.is_file():
        kind = b"file\0"
        content = path.read_bytes()
    else:
        continue
    digest.update(relative.encode("utf-8", errors="surrogateescape"))
    digest.update(b"\0")
    digest.update(kind)
    digest.update(content)
    digest.update(b"\0")
print(digest.hexdigest())
PYKEY
)" || CACHE_KEY=""

if [ -n "$CACHE_KEY" ] && [ -f "$CACHE_FILE" ] \
   && [ "$(tr -d '[:space:]' < "$CACHE_FILE")" = "$CACHE_KEY" ]; then
  exit 0
fi

# Run the smoke under a hard 180s bound enforced by Python itself.
if out="$("$PY" - "$PY" 2>&1 <<'PYWRAP'
import os, subprocess, sys
env = os.environ.copy()
env.pop("GIT_INDEX_FILE", None)
try:
    r = subprocess.run(
        [sys.argv[1], "scripts/ci_smoke.py"], timeout=180, env=env
    )
    sys.exit(r.returncode)
except subprocess.TimeoutExpired:
    sys.stderr.write("ci_smoke.py exceeded 180s — aborted\n")
    sys.exit(124)
except Exception as exc:
    sys.stderr.write("session-smoke wrapper error: %s\n" % exc)
    sys.exit(125)
PYWRAP
)"; then
  if [ -n "$CACHE_KEY" ]; then
    printf '%s\n' "$CACHE_KEY" > "${CACHE_FILE}.tmp.$$" \
      && mv -f "${CACHE_FILE}.tmp.$$" "$CACHE_FILE"
  fi
else
  echo "⚠️  §15 smoke FAILED or timed out — ARCHITECTURE.md may be stale OR the working tree is broken."
  echo "    Fix one before non-trivial work (R-START). Tail:"
  echo "$out" | tail -6 | sed 's/^/      /'
fi
exit 0
