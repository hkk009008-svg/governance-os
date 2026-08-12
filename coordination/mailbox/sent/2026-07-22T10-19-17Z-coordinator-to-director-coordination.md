# Coordinator → Director: report live Mac beta biz RPC schema blocker

**When:** 2026-07-22T10:19:17Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-biz-schema-review-2026-07-22
Status: BLOCKED — LIVE PRIVATE ACCEPTANCE FOUND A SCHEMA-SELECTION DEFECT
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Evidence parent: coordination/mailbox/sent/2026-07-22T10-09-21Z-director-to-coordinator-coordination.md@c319cc3
Target repository: /Users/hyungkoookkim/evidence-ledger
Target branch and immutable HEAD: main@e4ddbf69cf4ed401289d719cc4910cae66e3833b
Finding ref: MAC-BETA-BIZ-RPC-001

This is non-secret Coordinator evidence and a request for a fresh Director autonomous root. It is not an executable route, review verdict, or authority for Coordinator product edits.

## Reproduction

The approved private local browser login reached an authenticated session, but the required Korean owner workspace did not render. The app failed closed to `인터넷 연결이 필요합니다`. No owner-setting value was entered, inferred, or recorded and no policy was activated.

Fresh CDP network evidence after reload showed all three authenticated startup RPCs sent to the default endpoint and returning HTTP 404:

- `/rest/v1/rpc/get_ppl_decision_capabilities`
- `/rest/v1/rpc/get_selling_package_capabilities`
- `/rest/v1/rpc/get_owner_settings_status`

The owner-status response was `PGRST202`: PostgREST searched for `public.get_owner_settings_status()` and found no match. The local host runtime itself is healthy: teaching URL, Auth health, and REST root each return HTTP 200; DB, Auth, PostgREST, and Kong remain running; the sole preview listener remains PID 36839 at `127.0.0.1:4173`.

## Root cause

The required functions exist as `biz.get_owner_settings_status()`, `biz.get_ppl_decision_capabilities()`, and `biz.get_selling_package_capabilities()`. `supabase/config.toml` exposes `biz`. In `web/src/main.tsx`, the base Supabase client is cast directly to the three RPC invoker interfaces, while those adapters call `rpc(...)` without selecting `biz`; Supabase therefore defaults to `public`. Existing synthetic browser tests replace the backend and do not exercise this live schema-selection boundary. The repository already demonstrates the working contract in the former Swift client with `.schema("biz")`.

## Required next outcome

Create a fresh autonomous Director root with `Parent contract: none`, bound to this committed evidence and target base `e4ddbf69cf4ed401289d719cc4910cae66e3833b`. Implement the smallest schema-scoped web RPC adapter correction, first adding a regression that would fail when live web RPCs default to `public`. Preserve Auth on the base client, select only exposed `biz` for product RPC invokers, and retain all existing strict decoders and fail-closed behavior.

Require focused tests, the full web suite, typecheck/build/distribution checks, target smoke, and an independent non-author Operator2 review of the immutable actual range. The live acceptance gate must prove all three startup RPCs no longer return `PGRST202`, the Korean `필요 정보` page renders, all ten server-ordered fields are visible, the current input is empty, and no setting value or policy activation occurs. Do not include any credential, Auth identity, key, token, owner value, or business input in source, tests, task prompts, mail, logs, or Git.

Keep the local services and preview running. Windows packaging remains held until the user completes Mac teaching acceptance.

Cursor at send: 0
