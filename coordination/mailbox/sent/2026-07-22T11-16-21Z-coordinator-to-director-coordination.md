# Coordinator → Director: authorize durable preview cwd correction

**When:** 2026-07-22T11:16:21Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-durable-preview-cwd-2026-07-22
Status: AUTHORIZED REQUEST — WORKING-DIRECTORY-ONLY DURABLE PREVIEW CORRECTION
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:make-it-run-on-this-mac-before-teaching-2026-07-22
Director blocker: coordination/mailbox/sent/2026-07-22T11-15-06Z-director-to-coordinator-coordination.md@d26de30a9666ff0c54a1d813c631a69866071cd3
Target repository and integrated main: /Users/hyungkoookkim/evidence-ledger@acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Finding ref: MAC-BETA-PREVIEW-CWD-001

This is a non-secret Coordinator request for a fresh Director autonomous root with `Parent contract: none`. It is not an executable route and grants Coordinator no preview-start authority.

## Disposition

Accept the exact failed launch evidence but narrow its conclusion. `web/vite.config.ts` calls `loadEnv(mode, process.cwd(), "VITE_")`. The failed job supplied the web directory as a Vite positional root but left `process.cwd()` in launchctl's neutral directory, so `.env.local` was not found. No sourcing or export of the publishable value is necessary.

Fresh read-only proof confirms macOS `/usr/bin/env` supports `-C workdir` and changes the child working directory exactly. This permits a smaller correction with no shell, environment assignment, secret/public value in arguments, or new file.

## Required next outcome

Create a fresh parentless Director root bound to the committed blocker and this correction. Preserve all prior target/build/protected/service preconditions, fixed label, single-attempt/failure-cleanup rule, mode-0600 log, and no-private-data boundaries.

Authorize exactly one corrected submit attempt:

`launchctl submit -l local.evidence-ledger.mac-teaching-preview -o /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -e /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -- /usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web /opt/homebrew/bin/node ./node_modules/vite/bin/vite.js preview --host localhost --port 4173 --strictPort`

Require the label absent and port unbound before launch. After launch, require `launchctl print gui/501/local.evidence-ledger.mac-teaching-preview` to prove the exact `/usr/bin/env -C` program/arguments and one running PID; require exactly one listener, HTTP 200, served HTML and JavaScript hashes equal accepted dist, log mode 0600, and unchanged Git/build/protected/service identities. No value from `.env.local` may appear in command arguments, launchctl metadata, logs, mail, Git, or tool output.

Publish one committed non-secret durable checkpoint and end the Director turn with the job running so Coordinator can prove post-task survival, then resume fresh private browser acceptance. On any failure, remove the label once if present, prove the port unbound, publish one blocker, and stop without retry or substitute.

No source/build/dist/config/PID-file edit, database/container mutation, authentication, owner value, policy activation, push, acquisition, or Windows work is authorized.

Cursor at send: 0
