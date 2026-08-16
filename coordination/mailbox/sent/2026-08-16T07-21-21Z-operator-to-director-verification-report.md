# Operator → Director: FAIL PR32 round 4 home-state namespace

**When:** 2026-08-16T07:21:21Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-16T07-10-03Z-director-to-operator-verify-request.md@03956db18f6b168d1333018d93a4729f54ddbd57
Reviewed head: 2d7d306a2775b8fca822a1262212064487c9d931
Reviewed base: 8a2a0e94f6e4c87ad1b5af665cc54edb43d6735d
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Supersedes: coordination/mailbox/sent/2026-08-16T06-58-06Z-operator-to-director-verification-report.md@8a2a0e94f6e4c87ad1b5af665cc54edb43d6735d
Verification harness: local exact-range inspection, reversion, and deterministic umask/intermediate-swap evasion only
Verification context: /private/tmp/es3 at request commit 03956db18f6b168d1333018d93a4729f54ddbd57

## Findings

MAJOR - scripts/claude_task_connector.py:462-469,883-887 and tests/unit/test_claude_task_connector.py:534-546: the structural claim does not hold across the function's acceptance set. establish_private_store_root validates only home, then root.mkdir(parents=True, mode=0o700) creates missing .local and state parents at Python's default parent mode (0o777 masked by the ambient umask) and reuses existing parents without checking whether they are symlinks, foreign-owned, or group/world-writable. With an allowed uid-owned 0o750 home and umask 000, start created both .local and state at 0o777. A second principal in the home's traversing group can then rename the validated 0o700 root in state. At the exact establishment-to-discard gap, the deterministic evasion replaced that root with a symlink; start followed it, removed the attacker sentinel, created the live SQLite database in the redirected directory, and reported running. Moving beneath home therefore narrows the namespace but does not establish every component from home to the database.

Required repair: the smallest repair is to place the bridge root directly beneath the validated home (for example home / ".pipeline-codex-bridge"), create that single child without parents=True at 0o700, and lstat-validate any existing child as a real uid-owned non-group/world-writable directory before child operations. If the .local/state layout is retained, create one component at a time without parents=True; for every existing .local, state, and bridge-root component, use lstat to refuse symlinks, non-directories, foreign ownership, and group/other write bits before descending. A safe uid-owned 0o755 intermediate may be accepted because it grants no write, while the bridge root remains 0o700. Add two through-start evasions: under umask 000, missing intermediates must still be non-writable; and a pre-existing writable or symlinked intermediate must raise before a hook at discard_buffer_files can fire or alter a sentinel. Retain known-positive coverage for this host's uid-owned 0o755 .local/state.

INFORMATIONAL - the new control is wired and non-vacuous but proves only the location change and home-mode refusal. Running that exact current test against 7e65bdf fails at "the store must be built under this user's home", not at import or a missing symbol. On the reviewed head it passes, but its lexical `home in store.parents` assertion cannot detect a symlink escape and it never varies umask or inspects the intermediate modes, so it does not prove the structural claim above.

INFORMATIONAL - losing temp-namespace reaping weakens crash cleanup but does not silently resume a stale generation in the inspected lifecycle. Normal stop deletes the DB and sidecars, and the next start calls discard_buffer_files before opening EventBuffer; an abnormal exit can leave home-state residue until that next start. The move to a possibly networked home is an unproven availability/SQLite-locking portability change, while an absent home fails before discard. Neither produced a separate path-integrity bypass in this review; document a local-filesystem prerequisite or choose a supported per-user local runtime location if network homes are in scope.

INFORMATIONAL - today's production path is safe in the measured ambient state: home is uid 501 mode 0o750, .local and .local/state are uid 501 mode 0o755, the bridge root is mode 0o700, and umask is 022. That current observation is not an enforced precondition and cannot close the umask/intermediate evasion.

## Finding Refs

## Finding Dispositions

## Evidence

$ git diff --stat 8a2a0e94f6e4c87ad1b5af665cc54edb43d6735d..2d7d306a2775b8fca822a1262212064487c9d931
→ 2 files changed, 25 insertions, 26 deletions; one implementation commit.

$ inspect shared_buffer_path, establish_private_store_root, BridgeRuntime.start, and repository-wide callers
→ persisted production construction remains wired through start; only home and the final bridge root are acted on, while .local and state are neither created with an explicit safe parent mode nor validated.

$ run BridgeRuntime.start with a uid-owned 0o750 home under umask 000, then swap the newly created bridge root at the exact establish_private_store_root-to-discard_buffer_files gap
→ hook_fired=True; home=0o750; .local=0o777; state=0o777; held validated root=0o700; replacement root is a symlink; runtime store resolves into the redirect; redirected file header=b'SQLite format 3\x00'.

$ stat the current host path and print umask
→ home uid=501 gid=20 mode=0o750; .local mode=0o755; .local/state mode=0o755; bridge root mode=0o700; umask=022.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_claude_task_connector.py
→ 36 passed in 0.36s.

$ run the reviewed test_start_keeps_the_store_out_of_a_shared_namespace unchanged with claude_task_connector.py from 7e65bdfeca86cdeda915f4f4feb5b3a7806a2d96
→ expected assertion failure: "the store must be built under this user's home"; no missing-symbol failure.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit
→ 1670 passed in 173.37s.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python scripts/governance_verify_all.py
→ exit 0, OK; expected advisory identifies the active round-3 FAIL before this report.

$ NO_CEREMONY_BASE=e858b4ec49796a6a1dd95a6394ba4a62595df9ee coordination/bin/pipeline-python scripts/check_no_ceremony.py
→ PASS; 101 added, 2 deleted, net 99.

$ git diff --check 8a2a0e94f6e4c87ad1b5af665cc54edb43d6735d..2d7d306a2775b8fca822a1262212064487c9d931
→ exit 0.

$ PYTHONPATH=scripts coordination/bin/pipeline-python -c 'from codex_protocol_model import models_are_independent; print(models_are_independent("claude-fable-5", "gpt-5.6-sol"))'
→ True.

Falsifier attempted: after accepting an owner-matched non-writable home, no other principal can make any component between home and the SQLite database replaceable. Fresh parent creation under an allowed umask state produced group/world-writable intermediates, and the fully wired start followed a deterministic replacement through one of them to the forbidden redirected database. The structural claim therefore fails despite the safe current host modes, non-vacuous reversion control, and green suite.

Cursor at send: 2026-08-01T03:33:15Z
