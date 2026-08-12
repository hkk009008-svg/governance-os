# Director2 -> Coordinator: user-approved existing-session Opus launch denied before process creation

**When:** 2026-07-14T13:53:55Z · **From:** director2 (online)

Event type: coordination
Disposition: `PIPELINE_LEVEL5_OPUS_USER_APPROVED_RUNTIME_POLICY_BLOCKED`
Task-board: `pipeline-level5-opus-user-approved-2026-07-14`
Protocol wave: `2`
Active route: `coordination/mailbox/sent/2026-07-14T13-14-24Z-coordinator-to-all-coordination.md`
Packet: `director2-pipeline-level5-opus-user-approved-transport`
Side-effect ID: `pipeline-level5-opus-user-approved-attempt-2026-07-14`
Reviewed range: `555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`

## Findings First

Every no-provider precondition in the fresh user-approved route passed:

- Director2 unread was `0`; Wave 2 was `MET`; capacity and the active route
  validated; locks were empty; and the shared receipt root was absent.
- Main remained at `b2993ba2ac2c22398adf58712dbd122c088ee317`
  with bridge blobs `5e37f668a9e0c401ea8583cd0e07cebfffa9ba67`
  and `a67da9672d5c94fc2916ad6c17d4d10841f7d122`.
- The immutable review worktree remained clean at exact
  `97c270f8f0e630fdaaded672e0da37ed32335de5`; descriptor, provider prompt,
  and prompt-authority digests and blob identities matched the committed
  evidence.
- The unchanged deterministic no-provider acceptance bundle passed
  `897 passed, 18 skipped`; the GO schema, known SHA-reference baseline, and
  `scripts/ci_smoke.py` also passed on the unchanged head.
- No forbidden credential, auth-token, endpoint, or proxy override name was
  present; the Claude executable was present; and the required transport
  profile remained `anthropic-claude-existing-session-v1`.

Director2 then submitted the single routed bridge command once under
`pipeline-level5-opus-user-approved-attempt-2026-07-14`. The outer runtime
denied the request before `CreateProcess` under tenant policy prohibiting the
external disclosure of private workspace review scope. The bridge and provider
never started, no paid request was sent, no receipt or receipt root was
created, and no raw prompt or response bytes were persisted.

This is a terminal pre-process denial for the new side-effect ID. It is not a
retry of `pipeline-level5-wave0-opus-attempt-2026-07-14` or
`pipeline-level5-opus-existing-session-attempt-2026-07-14`; neither earlier
identity, command, or receipt state was reused. Director2 made no retry,
workaround, fallback, indirect execution, or substitute attempt.

## Preserved State

- The immutable review worktree remains clean at exact `97c270f`.
- The active route and capacity state remain valid; locks remain empty.
- Content-free command/result metadata is recorded in
  `logs/pipeline-level5-opus-user-approved-acceptance-2026-07-14.json`.
- No code or worktree edit, cursor consume, route, packet, lock, or ref
  mutation, receipt synthesis, merge, push, publication, cleanup, pod action,
  production generation, or downstream PPL action occurred.
- Operator2 remains blocked because no receipt-backed Director2
  verify-request exists.

## Required Resolution

Coordinator must reconcile or park the unsatisfied transport criterion. This
side-effect ID cannot be retried after the denial. This artifact grants no
authority for another provider process, workaround, or alternative transport.

## Exact Next Trigger

Run `continue as coordinator` to reconcile or park the terminal pre-process
denial. Do not run `continue as operator2` unless a future separately lawful
cycle first lands a receipt-backed Director2 verify-request.

Cursor at send: 0
