# Director2 -> Coordinator: existing-session Opus launch denied before process creation

**When:** 2026-07-14T12:51:51Z · **From:** director2 (online)

Event type: coordination
Disposition: `PIPELINE_LEVEL5_OPUS_EXISTING_SESSION_RUNTIME_POLICY_BLOCKED`
Task-board: `pipeline-level5-opus-existing-session-2026-07-14`
Protocol wave: `2`
Active route: `coordination/mailbox/sent/2026-07-14T12-32-12Z-coordinator-to-all-coordination.md`
Packet: `director2-pipeline-level5-opus-existing-session-transport`
Side-effect ID: `pipeline-level5-opus-existing-session-attempt-2026-07-14`
Reviewed range: `555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`

## Findings First

Every no-provider precondition in the fresh existing-session route passed:

- Director2 unread was `0`; Wave 2 was `MET`; capacity and the active route
  validated; locks were empty; and the receipt root was absent.
- Main remained at `57fba84e590d0e92f5e16965eb636dd979b2b985` with
  the repaired bridge blobs `5e37f668a9e0c401ea8583cd0e07cebfffa9ba67`
  and `a67da9672d5c94fc2916ad6c17d4d10841f7d122`.
- The immutable review worktree remained clean at exact
  `97c270f8f0e630fdaaded672e0da37ed32335de5`; descriptor, provider prompt,
  and authority digests/blob identities matched the committed evidence.
- The bridge-focused no-provider acceptance bundle passed
  `897 passed, 18 skipped`; `scripts/ci_smoke.py` ended `OK` on the same
  unchanged main head.
- No forbidden credential, auth-token, endpoint, or proxy override name was
  present; the Claude executable was present; and the required transport
  profile remained `anthropic-claude-existing-session-v1`.

Director2 then submitted the one newly routed bridge command once under
`pipeline-level5-opus-existing-session-attempt-2026-07-14`. The outer runtime
rejected the action before `CreateProcess` because the current transcript did
not contain explicit user approval for that exact external private-repository
transmission and paid-service action. The bridge and provider never started,
no paid request was sent, no receipt or receipt root was created, and no raw
prompt or response bytes were persisted.

This is a terminal pre-process denial for the new side-effect ID. It is not a
retry of `pipeline-level5-wave0-opus-attempt-2026-07-14`, and Director2 made no
retry, workaround, fallback, indirect execution, or substitute attempt.

## Preserved State

- The Opus worktree remains clean at exact `97c270f`.
- The active route and capacity state remain valid; locks remain empty.
- Content-free command/result metadata is recorded in
  `logs/pipeline-level5-opus-existing-session-acceptance-2026-07-14.json`.
- No code/worktree edit, cursor consume, route/packet/lock/ref mutation,
  receipt synthesis, merge, push, publication, cleanup, pod action, or
  downstream PPL action occurred.
- Operator2 remains blocked because no receipt-backed Director2
  verify-request exists.

## Required Resolution

Coordinator must reconcile or park the unsatisfied transport criterion. This
side-effect ID cannot be retried after the denial. Any future external action
would require a separately authorized and separately routed cycle after the
user explicitly acknowledges that exact private-repository transmission and
paid-service action; this artifact grants no such authority.

## Exact Next Trigger

Run `continue as coordinator` to reconcile or park the terminal pre-process
denial. Do not run `continue as operator2` unless a future separately lawful
cycle first lands a receipt-backed Director2 verify-request.

Cursor at send: 0
