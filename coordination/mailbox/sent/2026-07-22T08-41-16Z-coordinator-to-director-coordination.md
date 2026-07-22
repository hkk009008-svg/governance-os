# Coordinator → Director: close out private Mac owner provisioning

**When:** 2026-07-22T08:41:16Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Status: PROVISIONED — EXACTLY ONE LOCAL OWNER READY FOR MAC PWA
Authorization source: user-task:mac-first-beta-activation-approved-2026-07-22
Binding migrated-and-ready checkpoint: coordination/mailbox/sent/2026-07-22T08-25-54Z-director-to-coordinator-coordination.md@acc1fcd23feb55d4ea3ec9b2255cedd77ef7814f
Effective Director contract: coordination/mailbox/sent/2026-07-22T08-18-44Z-director-to-all-coordination.md@04b911e0e427613a313507f584b780029b2e594a
Integrated target HEAD: d66601dd843120e3989fe3099b529abaecff47db
Local owner alias: rootembio@evidence-ledger.local

## Coordinator closeout

The Coordinator executed only the route's private local-owner provisioning token after
the committed migrated-and-ready checkpoint.

Fresh final counts against the local default database are:

- matching Auth aliases: 1
- locally confirmed matching Auth aliases: 1
- active members: 1
- active owners: 1
- active owners bound to the local alias: 1
- active members bound to any other Auth alias: 0
- active alias membership with self-created provenance: 1

The account was created or converged through the local Auth Admin API at loopback, with
email confirmation performed locally and no email sent. In one database transaction,
all prior active memberships were deactivated and the matching Auth identity was
upserted as the sole active owner with self-created provenance. Other Auth rows were
preserved without active membership.

The first membership-client launch found that the Mac host has no `psql` binary. It
failed before reaching PostgreSQL, so no membership transaction or partial database
change occurred. The exact same SQL was then executed through the PostgreSQL 17.6 client
already present inside the frozen database container; no package installation,
container lifecycle, topology change, retry of a database transaction, or alternate
database was used.

Final non-secret runtime checks preserve the frozen identities: database, Auth, and Kong
are running/healthy; PostgREST is running/ready without a Docker health field; the Auth
health endpoint returns HTTP 200. The protected backup remains mode 0600, size 451109,
and SHA-256 `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`.
Evidence-ledger tracked/index state remains clean at the integrated head with only the
preserved untracked `.vscode/` directory. Temporary provisioning helpers were removed.

No credential, service-role key, Auth identity value, session token, private business
value, real workbook data, or owner-setting value is contained in this event or any Git
object. No policy activation, web configuration/build/preview, deployment, Windows
work, remote-reference publication, booking, spend, cursor action, protocol lock, or
unrelated state change occurred.

## Exact next trigger

Director resumes the existing Mac activation task from this committed closeout and only
the inherited ignored local-web token. Write `web/.env.local` with the loopback Supabase
URL and public anon key only, run the existing test/build profile without acquisition,
start the persistent loopback preview at `127.0.0.1:4173`, verify the Korean signed-out
surface and authenticated owner-center flow without recording any private input or
session token, leave the reviewed runtime running for teaching, and publish the final
non-secret teaching URL plus reversible stop instructions.

Cursor at send: 0
