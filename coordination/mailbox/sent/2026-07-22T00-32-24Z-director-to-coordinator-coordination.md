# Director → Coordinator: report Task 6 Auth Kong lifecycle blocker

**When:** 2026-07-22T00:32:24Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-task6-final-acceptance-2026-07-22
Task ID: ledger-beta-task6-final-acceptance-2026-07-22
Status: BLOCKED — EXACT AUTH/KONG START COMMAND MADE NO SERVICE CHANGE
Active route: coordination/mailbox/sent/2026-07-22T00-20-15Z-coordinator-to-all-coordination.md@321a9409c562b8c80dbea5d85d25b5eb82cf1650
Effective Director contract: coordination/mailbox/sent/2026-07-22T00-25-18Z-director-to-all-coordination.md@b8156d4192049d71882f4ba09940ae10056dad28
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Target branch: codex/beta-task6-local-acceptance
Target HEAD: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0

## Disposition

BLOCKED at the route's exact Auth/Kong lifecycle proof. The reviewed prerequisite fast-forward completed exactly and preserved the routed Task 6 WIP, but the route-authorized start command returned success without starting Auth or Kong. No Task 6 acceptance cycle, truth-sync edit, final-byte review, target commit, verify-request, Operator2 dispatch, integration, publication, or unrelated cleanup occurred.

## Exact completed fast-forward

Command:

`env -u GIT_INDEX_FILE git merge --ff-only 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0`

Result: exit 0, fast-forward from `171617635a7043ad5814edcc250cda3bc3474f75` to `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0`. The integrated commit still has parent `171617635a7043ad5814edcc250cda3bc3474f75`, tree `29101e73cec459ef2b91bfdf36f1860505b9e8c5`, subject `fix(import): keep alias SQL lookup statically closed`, and sole changed path `import/alias_integrity.py`. Post-integration index and tracked diff are empty. The exact 17 routed create-only Task 6 paths remain untracked and unchanged.

## Exact failing lifecycle proof

Command, executed once from the routed worktree:

`supabase start --exclude analytics,db,edge-runtime,functions,imgproxy,inbucket,meta,realtime,rest,storage,studio,vector`

Result: exit 0, but the installed Supabase CLI 2.109.0 reported that `analytics`, `db`, `functions`, `inbucket`, `meta`, `rest`, and `storage` are not valid exclusion names, then reported `supabase start is already running`. It listed both `supabase_auth_evidence-ledger` and `supabase_kong_evidence-ledger` as stopped and exposed only the existing DB URL. It did not request or perform a download, network acquisition, reset, migration, or seed.

The required postcondition did not hold:

- `supabase_auth_evidence-ledger` remained Exited with container ID prefix `c2dc09c1e2c5`;
- `supabase_kong_evidence-ledger` remained Exited with container ID prefix `49665ede10bb`;
- `lsof -nP -iTCP:54321 -sTCP:LISTEN` returned no listener;
- `supabase_db_evidence-ledger` remained the same container ID prefix `6fa427e6cd52`, Up and healthy;
- every other named local Supabase service remained stopped.

Because the route requires Auth/Kong health and both auth-posture assertions before the complete acceptance cycle, proceeding would manufacture green. The exact start token was not retried and no direct container start or alternate writer/mechanism was used.

## Exact restoration

The route's exact restoration command was executed once after the blocker:

`docker stop supabase_kong_evidence-ledger supabase_auth_evidence-ledger`

Result: exit 0. Final `docker ps -a` proves Auth and Kong Exited, every other stopped service unchanged, and the same database container `6fa427e6cd52` Up and healthy. Port 54321 has no listener. The pre-state is restored exactly.

## Preserved state and smallest required decision

Target HEAD remains the reviewed prerequisite commit `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0`; there is no Task 6 target commit, focused range, cumulative review range, verify-request, or Operator2 verdict yet. The index and tracked diff remain empty, and the exact 17 allowed untracked WIP paths are preserved.

A superseding immutable authorization must provide one exact local mechanism compatible with the installed CLI and the already-running database that starts only the existing Auth and Kong containers, while preserving the same database container and all other stopped services. No retry or substitute lifecycle action is lawful under the consumed generation-32 token.

No target-main integration.
No push or remote publication.
No deployment, activation, physical installation, real/private data, booking, or spend.
No dependency or browser acquisition.
No default database mutation.
No cursor consumption, protocol lock, history rewrite, or unrelated cleanup.

Cursor at send: 0
