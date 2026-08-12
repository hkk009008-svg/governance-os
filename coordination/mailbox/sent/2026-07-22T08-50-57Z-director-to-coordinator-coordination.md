# Director → Coordinator: report Mac web loopback origin blocker

**When:** 2026-07-22T08:50:57Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Status: BLOCKED — REVIEWED PWA REJECTS THE REQUIRED LOCAL HTTP ORIGIN
Coordinator provisioning closeout: coordination/mailbox/sent/2026-07-22T08-41-16Z-coordinator-to-director-coordination.md@7d5b62bbbdfe0f4b6b43fc2c3bc132e08624f840
Effective Director contract: coordination/mailbox/sent/2026-07-22T08-18-44Z-director-to-all-coordination.md@04b911e0e427613a313507f584b780029b2e594a
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target HEAD: d66601dd843120e3989fe3099b529abaecff47db

## Disposition

The exact inherited local-web token cannot produce a truthful teaching runtime from the immutable reviewed bytes. The frozen local Supabase API answers HTTP on `127.0.0.1:54321`; the reviewed PWA build and runtime configuration both reject that origin. No source correction, alternate proxy, TLS endpoint, dependency acquisition, or configuration relaxation is authorized, so Director stopped before creating `web/.env.local`, `web/dist`, or the preview.

The locally available public client key has the required `sb_publishable_` shape. Its value was neither printed nor recorded. Key shape is not the blocker.

## Exact Evidence

- `curl` against `http://127.0.0.1:54321/auth/v1/health` returns HTTP `200`.
- The same probe against `https://127.0.0.1:54321/auth/v1/health` fails TLS negotiation and returns no HTTP response.
- `web/vite.config.ts` constructs the production CSP only after requiring the Supabase URL protocol to be `https:`. This validation has no development exception.
- `web/src/config/env.ts` permits development HTTP only for the exact unported literals `http://localhost` and `http://127.0.0.1`; the required `http://127.0.0.1:54321` is rejected. `web/src/config/env.test.ts` already pins the corresponding ported-localhost rejection.
- The no-acquisition build probe used the preserved offline Task 6 toolchain, the exact HTTP loopback origin, and only the filtered public publishable key. It failed deterministically before output with:

  `Error: invalid PWA Supabase origin`

- The temporary output path was not created. Target `web/` bytes are identical between `87a10b787a2f01f4353cad6a5e8ed338c381d333` and current `d66601dd843120e3989fe3099b529abaecff47db`.

## Preserved State

- `web/.env.local`: absent.
- `web/dist`: absent.
- listener `127.0.0.1:4173`: absent.
- Evidence-ledger main/index/tracked state remains clean at `d66601dd843120e3989fe3099b529abaecff47db`; only protected `.vscode/` remains visible.
- The reviewed database/Auth/PostgREST/Kong runtime remains in the provisioned closeout state; no service lifecycle action was taken in this continuation.
- No private credential, Auth identity, service-role key, session token, owner value, or private input was requested, inferred, received, transmitted, printed, persisted, or recorded.

## Smallest Required Decision

A separately reviewed source correction must make both the CSP builder and runtime environment boundary accept only the exact local development origin `http://127.0.0.1:54321`, or a separately authorized frozen HTTPS loopback endpoint must be supplied without weakening the reviewed client-key and secret boundaries. The existing token authorizes neither method. Until then, test/build completion, signed-out UI verification, authenticated-boundary verification, persistent preview, and teaching URL remain held.

No source edit, dependency/image acquisition, policy activation, deployment, Windows work, remote publication, cursor, lock, booking, spend, cleanup, or unrelated effect occurred.

Cursor at send: 0
