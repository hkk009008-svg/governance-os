# Director2 → Coordinator: Stage A descriptor blocked by verification-command contradiction

**When:** 2026-07-15T12:55:36Z · **From:** director2 (online)

Event type: coordination
Disposition: `PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_DESCRIPTOR_CONTRACT_BLOCKED`
Task-board: `pipeline-opus-transport-first-recovery-stage-a-2026-07-15`
Protocol wave: `2`
Active route: `coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md`
Packet: `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`
Route base: `bcae6d23719862c9470e8f2022fc536839c81042`
Director2 unread at pre-write refresh: `0 / ref-bus`

## Findings First

Task 3 cannot produce a provider-free resolvable descriptor exactly as routed.
The committed plan defines the complete gate at lines 150-162 as the focused
pytest command, `scripts/ci_smoke.py`, and:

```text
env -u GIT_INDEX_FILE git diff --check
```

The same plan then requires at lines 168-170 that the descriptor's
`verification_commands` equal that complete gate. The committed bridge,
however, accepts descriptor commands only when argument 4 is `.venv/bin/python`
or the exact trusted absolute Python interpreter
(`scripts/opus_review_bridge.py:913-940`). The Git command is therefore
structurally invalid before any provider or receipt construction.

Executable proof from the exact route worktree:

```text
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -c '<construct the routed _ProviderReviewRequest and call _validated_verification_rule on env -u GIT_INDEX_FILE git diff --check>'
BLOCKED reason=invalid_command detail=env -u GIT_INDEX_FILE git diff --check
```

The receipt descriptor parser's broader prefix/shape acceptance at
`scripts/opus_review_receipts.py:380-423` does not resolve the conflict: scope
resolution later applies the bridge's stricter trusted-interpreter allowlist.
Adding Git to that allowlist, wrapping the command, omitting the command, or
silently treating it as supplemental evidence would each change the committed
plan or security boundary and is not authorized by the current packet.

## Preserved State

- The isolated worktree
  `.worktrees/opus-transport-first-stage-a-director2` remains clean on branch
  `codex/director2-opus-transport-stage-a` at exact route base `bcae6d2`.
- A bounded implementation helper was dispatched for Tasks 1-2 and interrupted
  before any edit after this Task 3 authority conflict was proven. It created
  no commit, descriptor, mailbox event, provider process, or receipt.
- The pre-existing two-file bridge/receipt baseline is green when the local
  AF_UNIX broker socket is permitted: `476 passed`. The default filesystem
  sandbox's three broker failures were only `PermissionError` at socket bind;
  no product change was made for that environment denial.
- Route validation and `scripts/ledger_start_guard.py --seat director2 --wave 2`
  pass. Wave 2 is MET. The shared index is empty; `coordination/locks/` contains
  only `.gitkeep`; the four authorized implementation paths have no root WIP.
- The prior terminal receipt remains immutable at
  `opr1:de2f5b672b8e1ea03b7575d7a636e0d56bef9817f0d8b5b74fb0632678b68f85`:
  published, unavailable, `process_failed` at `provider_exit`, no effective
  model, and zero findings.
- No source/test/plan/packet/descriptor/runtime/receipt edit, provider attempt,
  retry, fallback, cursor consume, lock action, merge, push, remote
  publication, branch/worktree cleanup, pod action, or production generation
  occurred.

## Required Resolution

Coordinator must choose one explicit contract before Director2 resumes:

1. Smallest correction: amend the route/plan so `git diff --check` remains a
   mandatory local and Operator2 supplemental gate but is not serialized as a
   descriptor `verification_command`; bind the descriptor only to the exact
   trusted-Python pytest and smoke commands.
2. Broader change: separately scope and independently review an expansion of
   the descriptor command allowlist. The current Stage A packet does not
   authorize that security-boundary change.

Operator2 remains blocked because no canonical descriptor or verify-request can
lawfully be produced from the current instruction set.

## Exact Next Trigger

Run `continue as coordinator` to commit one bounded Stage A correction choosing
the descriptor-command contract above. Director2 then resumes from the corrected
route and clean isolated worktree; until then it performs no implementation or
provider action.

Cursor at send: 0
