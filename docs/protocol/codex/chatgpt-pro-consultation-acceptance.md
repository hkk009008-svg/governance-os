# ChatGPT Pro consultation transport acceptance

This procedure is the hard gate for changing the consultation default from
`manual` to `auto`. It proves the guarded lifecycle and each transport class
without granting the advisory response any protocol authority.

## Safety boundary

- Use only the fixed, non-sensitive transport question below. Do not attach a
  screenshot, upload a file, quote repository content, or include secrets,
  business data, mailbox bodies, route details, credentials, or browser state.
- Keep the request, guarded packet, and response only in process or Browser
  session memory. Send request and response JSON through stdin, never shell
  arguments, environment variables, temporary files, normal logs, screenshots,
  mailbox events, or repository artifacts.
- Use a fresh ChatGPT conversation for each browser transport and one confirmed
  send per consultation ID. There is no automatic retry and no API fallback.
- Verify the visible account/session state without credential handling. On a
  signed-out, wrong-account, consent, challenge, CAPTCHA, redirect, popup, or
  ambiguous profile state, stop. Never enter credentials, never inspect cookies
  or storage, never weaken security, and never auto-navigate around the stop.
- A partial-send or uncertain delivery is a stop state. Mark the attempt failed
  and do not resend automatically.

## Prerequisites

Before transport work:

1. Confirm the relevant diff is clean apart from the planned Task 5 paths.
2. Run the focused guard and prompt-sync tests using `env -u GIT_INDEX_FILE`.
3. Confirm the platform Browser skill is available and read its current
   instructions.
4. Confirm an in-app Browser signed-in user-controlled session is visibly
   available without inspecting credentials, cookies, storage, or profiles.
5. Inspect the current Codex CLI help/configuration read-only. A bare CLI packet
   export/import is not a CLI-driven browser pass; the CLI gate is attempted
   only if the current CLI actually exposes its configured browser bridge.
6. Record content-free before snapshots for bound HEAD, refs, remotes, mailbox,
   inventory, locks, signed bus, and working-tree scope. Snapshot output must not
   contain request or response content.

## Fixed packet

Use a fresh UUIDv4 per transport and bind the current full lowercase HEAD. The
state binding is content-free (`wave`, `route_id`, and mailbox hash are null;
the relevant-path hash binds the allowed Task 5 paths). Use one short trusted
fact stating that this is a non-sensitive transport acceptance check, and no
repository excerpt.

The fixed question is:

> This is a transport acceptance test. Recommend the exact string transport-ok
> and return the full response schema requested by the guarded prompt, including
> its consultation ID and request hash.

The requested output list is exactly `recommendation`, `reasoning`,
`assumptions`, `risks`, and `questions`.

## Guard commands

Until this gate passes, the repository default is deliberately still `manual`.
For every pre-activation command that exercises an `iab` or `chrome` lifecycle,
use the explicit per-process override
`CODEX_CHATGPT_PRO_CONSULTATION=auto`; this is acceptance configuration, not an
activation change. Launch the guard without packet content in the command:

```bash
env -u GIT_INDEX_FILE CODEX_CHATGPT_PRO_CONSULTATION=auto \
  /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/chatgpt_pro_consult.py prepare \
  --state-file .codex/runtime/task5-TRANSPORT-acceptance.json
```

Write the in-memory request JSON to that process through stdin. Immediately
before the single browser send, mark `prepared -> sending` with the content-free
consultation ID and transport (`iab` or `chrome`). Only after visible confirmation
that exactly one send occurred, mark `sending -> sent`. Pass the exact in-memory
response wrapper to `accept` through stdin; it must contain the local
consultation ID, the exact response object, and the unchanged current state
binding. Confirm matching ID and request hash, then mark `received -> reconciled`.
Keep the override on `transition` and `accept` commands for the same browser
attempt. Never set it globally and never change the model default before both
real browser gates pass.

For manual relay, use transport `manual` and the same lifecycle. Export the exact
guarded packet, verify it renders identically to the guarded Browser packet for
the same input, and import the exact correlated response through stdin. Do not
substitute an unguarded question.

## Required checks

### Desktop in-app Browser

1. Open a fresh approved ChatGPT-origin conversation.
2. Confirm the visible signed-in state without handling credentials.
3. Enter the guard-produced packet exactly once and send exactly once.
4. Wait for a complete correlated JSON response; do not capture a screenshot.
5. Accept through the guard, verify ID/hash correlation, reconcile, and finalize
   the consultation tab under the Browser skill rules.

### Configured CLI browser

Repeat the browser check from a fresh chat through the CLI-configured browser
bridge only when the current CLI exposes it. Record the exact bridge boundary.
If the bridge is unavailable or the send fails, record a bounded blocker and do
not set the default to auto. Bare CLI manual relay does not satisfy this gate.

Enabled feature flags, an installed Browser plugin, and a configured
`node_repl` MCP server prove configuration only; they do not prove that the
standalone CLI can connect to a usable browser backend. Before preparing a CLI
acceptance record or entering `sending`, run one non-sending preflight through
`codex exec --ephemeral --sandbox read-only`. It may load the Browser skill,
select the explicit `iab` backend, and load its documentation, but it must not
navigate, create a tab, send a message, or receive consultation content.
Persist no session and return only content-free diagnostic fields:
core-model status, skill-load status, backend, browser-connected,
documentation-loaded, and failure class.

```bash
env -u GIT_INDEX_FILE CODEX_CHATGPT_PRO_CONSULTATION=auto \
  codex exec --ephemeral \
  -C /Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-pro-consultation \
  --sandbox read-only --color never -
```

Only `browser-connected=true` and `documentation-loaded=true` permit the real
CLI attempt to proceed. Any false, unavailable, ambiguous, or timed-out result
records the configured CLI bridge as unavailable, keeps the default `manual`,
and stops without a send or automatic retry.

On 2026-07-13, the non-sending preflight completed in 27.7 seconds: the core
CLI/model and Browser-skill load succeeded, but the standalone CLI returned
backend `iab`, `browser-connected=false`, `documentation-loaded=false`, and
failure class `backend_unavailable`. It performed no navigation, tab creation,
or messaging. This is the exact environment boundary; the configured-CLI hard
gate is blocked even though its plugin and flags are present.

### Failure fixtures

Exercise signed-out, wrong-account, challenge, refusal, malformed HTML,
truncated JSON, and partial-send behavior only with contract fixtures or an
already-unauthenticated disposable profile. Never sign the user's session out
or provoke a challenge. Each case must stop without fabricated success,
credential entry, retry, API fallback, or protocol mutation.

### Persistence and authority

After success or failure:

1. Verify runtime metadata contains only the content-free state schema.
2. Run repository scans for transcript markers, canaries, private keys, bearer
   tokens, and response-schema content outside the sanitized acceptance log.
3. Compare content-free before/after snapshots and prove no mailbox, inventory,
   lock, signed-bus, git-ref, remote, `coordination/`, `threeway/`, or `.git/`
   mutation occurred.
4. Record only abbreviated safe IDs/hashes, bound HEAD, transport class,
   pass/fail per check, commands, and failure class in the sanitized log. Do not
   record packet, response, recommendation, reasoning, or chat URL content.

### Failed acceptance revisions

A response-schema rejection is terminal for that acceptance revision. Mark the
attempt `failed` with failure class `malformed`, finalize its browser tab, and
do not repair the response, retry the send, resume it manually, or reuse its
consultation ID, state file, guarded packet, or idempotency key. After a prompt
contract fix, increment a non-sensitive revision label in the request purpose
or trusted acceptance fact, generate a fresh UUIDv4, use a new state path, and
run `prepare` again so the revised acceptance has a distinct idempotency key.
Both real transport gates must pass on packets rendered by the fixed code.

## Stop rule

Desktop in-app and configured CLI browser acceptance are separate hard gates.
If either required gate is unavailable, ambiguous, or fails—or any safety,
correlation, lifecycle, mutation, persistence, or fixture check fails—do not set
the default to auto. Keep `manual`, record the exact bounded blocker, and make no
automatic retry.
