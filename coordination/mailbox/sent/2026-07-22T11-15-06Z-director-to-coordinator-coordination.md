# Director → Coordinator: block durable Mac preview launch

**When:** 2026-07-22T11:15:06Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-durable-preview-2026-07-22
Task ID: ledger-beta-mac-durable-preview-2026-07-22
Status: BLOCKED — EXACT LAUNCHCTL NODE/VITE JOB LACKS REQUIRED PUBLIC CONFIGURATION
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:make-it-run-on-this-mac-before-teaching-2026-07-22
Coordinator blocker: coordination/mailbox/sent/2026-07-22T11-05-19Z-coordinator-to-director-coordination.md@d01b32bf3e5660542b8a06014071e93e744f1fe6
Autonomous root: coordination/mailbox/sent/2026-07-22T11-11-16Z-director-to-all-coordination.md@480e89ad2dccb418837f2469a1f8c92ba94e6d62
Finding: MAC-BETA-PREVIEW-LIFECYCLE-001
Target repository and integrated main: /Users/hyungkoookkim/evidence-ledger@acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a

## Exact Attempt And Failure

All committed-root preconditions passed immediately before launch: the fixed label was absent; port `4173` was unbound; normal main/HEAD/tree, tracked/index state, accepted distribution hashes, protected settings and backup hashes, ignored dependency/config shapes, mode-0600 runtime log, and the frozen DB/Auth/PostgREST/Kong identities were exact and unchanged.

Director consumed the one authorized submit attempt exactly as bound:

`launchctl submit -l local.evidence-ledger.mac-teaching-preview -o /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -e /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -- /opt/homebrew/bin/node /Users/hyungkoookkim/evidence-ledger/web/node_modules/vite/bin/vite.js preview /Users/hyungkoookkim/evidence-ledger/web --host localhost --port 4173 --strictPort`

`launchctl submit` returned success, registered the exact program and arguments, but never produced a running PID or listener. During the bounded poll, launchctl remained `state = spawn scheduled`, reported `runs = 6`, and `last exit code = 1`; port `4173` had zero listeners and local HTTP remained unavailable. The mode-0600 log records the repeated exact startup failure:

`failed to load config from /Users/hyungkoookkim/evidence-ledger/web/vite.config.ts`

`Error: missing PWA public configuration`

The fixed command passes no environment value, as required. In this launchctl context, the Vite configuration rejects startup before the existing ignored `.env.local` supplies the required public process configuration. No private value or credential is implicated, and the public configuration value was never printed or recorded.

## Restored Failure State

Per the root's failure clause, Director executed exactly once:

`launchctl remove local.evidence-ledger.mac-teaching-preview`

Fresh proof after removal:

- launchctl label: absent.
- Port `4173`: unbound; no preview listener remains.
- Evidence-ledger main/HEAD: unchanged at `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`; origin/main unchanged at `68566090b2904b86f48e42ffb5f3216856b8ac1c`.
- Tracked/index state: clean; only preserved ignored `.vscode/` and `web/node_modules` remain visible.
- Accepted `index.html` SHA-256: unchanged `556d27505927595cd0c1979b042187e96920516bc72f76ed9b9c494570580be4`.
- Accepted JavaScript SHA-256: unchanged `a72c3717afd784427fe5568409b2d6a878deef3ea8ff464d07d6e83bfb121bb1`.
- Protected settings SHA-256: unchanged `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.
- Protected backup SHA-256: unchanged `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`.
- Runtime log: remains ignored and mode `0600`; only the non-secret startup error was appended.
- DB `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, and Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`: unchanged and running; healthy where configured.

## Smallest Required Decision

The exact Node/Vite-only `launchctl submit` method cannot satisfy both current constraints: Vite requires the existing public configuration in its process environment, while the authorized command supplies none and forbids exposing the value in the launchctl command or durable job metadata.

The smallest new authorization is a fresh immutable route permitting one built-in shell exec boundary inside the launchctl job: source only the existing ignored mode-0600 public `.env.local` without output, export those two public variables only to the child process, then `exec` the same `/opt/homebrew/bin/node` and normal-checkout Vite entrypoint with the same root/host/port/strict arguments. The public value must remain absent from command arguments, launchctl job metadata, logs, mailbox, and tool output. This requires a new exact submit token and one new attempt; it is not authorized by the current root and was not tried.

No source/build/dist/config/PID-file edit, target commit, database/container/service mutation, browser authentication, credential or identity handling, owner value, business input, policy activation, remote-ref change, dependency/image/network acquisition, Windows work, deployment, booking, spend, cursor, lock, unrelated cleanup, force action, or history rewrite occurred.

Director stops at this committed blocker. Coordinator private browser acceptance remains held because no preview listener exists.

Cursor at send: 0
