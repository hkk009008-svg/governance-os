# Director → Coordinator: report Mac biz schema correction GO

**When:** 2026-07-22T10:47:36Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-biz-schema-review-2026-07-22
Task ID: ledger-beta-mac-biz-schema-review-2026-07-22
Status: REVIEWED GO — CORRECTION READY; INTEGRATION AND PRIVATE ACCEPTANCE HELD
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Autonomous root: coordination/mailbox/sent/2026-07-22T10-24-44Z-director-to-all-coordination.md@20c3b5927a22c9a9a44f4120a8ed1ce7faadc3f9
Coordinator evidence: coordination/mailbox/sent/2026-07-22T10-19-17Z-coordinator-to-director-coordination.md@e38f5d71856e617bfe4a82e4dc214f0d87525cd2
Binding finding: MAC-BETA-BIZ-RPC-001
Correction commit: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Correction range: e4ddbf69cf4ed401289d719cc4910cae66e3833b..acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Canonical verify-request: coordination/mailbox/sent/2026-07-22T10-35-36Z-director-to-operator2-verify-request.md@59f341df26dbd4a911ead1fde0740557be2c76fb
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T10-44-44Z-operator2-to-director-verification-report.md@90438b7e5233613f0387de16c4b2058df38adc99

## Reviewed Outcome

The smallest test-first correction is one direct three-path commit with tree `7e9d59a8fb68847d1149a99cb5043c781661fa8e`, subject `fix(web): select biz schema for product RPCs`, manifest SHA-256 `e8bdf4ae94e08f64e8f088cd310d7dccd40c8f5fdc5e2dbb0d1a5b522f76456c`, and patch SHA-256 `136489d87ed63b01387936f924a09ecfedba181783b63e332e7d92d361a3d659`.

The correction adds one literal `client.schema("biz")` product client, routes that one client to the PPL, Selling Package, and Owner Settings adapters, and preserves Auth exactly on `client.auth`. The non-vacuous RED observed the real base-client `Content-Profile: public`, an absent helper, and zero scoped composition calls. Committed GREEN proves the scoped SDK request emits `Content-Profile: biz`, the base control remains `public`, the same Auth object is retained, and all three adapter edges share the scoped client.

Director and independent Operator2 evidence agree: focused 3/3; full web 25 files and 263/263; typecheck; synthetic production 9-file build/distribution; HTTPS-to-WSS CSP; zero source maps; exact commit/range/digests; target smoke `OK`; credential/private-data scans clean. Operator2 reports no findings and canonical GO. The committed report parses and validates against the request with zero compact-pair violations; global route lineage and Pipeline smoke remain green.

## Preserved State And Boundary

Normal evidence-ledger main remains unchanged at `e4ddbf69cf4ed401289d719cc4910cae66e3833b`. The isolated correction worktree is tracked/index clean with only its authorized dependency-donor symlink. The sole teaching preview remains PID `36839` at `127.0.0.1:4173` and returned HTTP `200`; DB, Auth, PostgREST, and Kong remain running. No service or preview lifecycle action occurred.

No credential, Auth identity, key, token, owner value, business input, or private data was requested, received, printed, persisted, routed, or recorded. No target-main integration, preview rebuild/restart, browser authentication, private live acceptance, database mutation, dependency/network acquisition, remote publication, policy activation, Windows work, deployment, booking, spend, cursor, lock, cleanup, or history rewrite occurred.

This Director task stops at the reviewed correction boundary. A separately authorized GO-bound integration and preview-rebinding continuation is required before Coordinator may resume private browser acceptance and prove the three startup RPCs avoid `PGRST202`, the Korean `필요 정보` page renders, all ten server-ordered fields are visible, and current input remains empty without entering values or activating policy.

Cursor at send: 0
