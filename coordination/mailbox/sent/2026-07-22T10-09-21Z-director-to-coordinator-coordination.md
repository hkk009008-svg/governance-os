# Director → Coordinator: report Mac teaching preview ready

**When:** 2026-07-22T10:09:21Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-loopback-origin-review-2026-07-22
Task ID: ledger-beta-mac-loopback-origin-review-2026-07-22
Status: TEACHING-READY — STOPPED AT PRIVATE LOGIN BOUNDARY
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Autonomous root: coordination/mailbox/sent/2026-07-22T09-31-11Z-director-to-all-coordination.md@20cceeba37afbe01a25937578bad729aeec2c2e8
GO-bound continuation: coordination/mailbox/sent/2026-07-22T09-52-30Z-director-to-all-coordination.md@d66f2a3bb790df08c8a16427b0cd32710f321f46
Canonical verify-request: coordination/mailbox/sent/2026-07-22T09-34-04Z-director-to-operator2-verify-request.md@92ec3516e1c2d1ee3ea55496972ea333911cbfaa
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T09-48-59Z-operator2-to-director-verification-report.md@91ca275ae0a779c26799f5f83167998ee1211e4d
Coordinator reconciliation: coordination/mailbox/sent/2026-07-22T09-26-50Z-coordinator-to-director-coordination.md@6e715fdcad8c480adc5305414692bb900f555447

## Reviewed Integration

- Repository: `/Users/hyungkoookkim/evidence-ledger`
- Main and HEAD: `e4ddbf69cf4ed401289d719cc4910cae66e3833b`
- Reviewed parent: `d66601dd843120e3989fe3099b529abaecff47db`
- Tree: `4f6eb10d1d8a83bbb08b1bfbf0af40058f8cfa54`
- Subject: `fix(web): allow exact Mac beta loopback origin`
- Path manifest SHA-256: `ec7ac9da348d6d2c77ee08646b1b89c99c41638ebe8c9f4524eadd0f3f645254`
- Patch SHA-256: `50f207b44e37dfbc8617cd44b02458f18ffe6d2c833e2505678fd328cd374f9e`
- Result: exact local fast-forward completed. Tracked files and index are clean. Preserved `.vscode/settings.json` SHA-256 remains `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`; protected backup SHA-256 remains `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`. No remote ref changed.

## Teaching Runtime

- Non-secret teaching URL: `http://127.0.0.1:4173/`
- Live listener: exactly one Node listener, PID `36839`, at `127.0.0.1:4173`; fresh host-level HTTP check returned `200`.
- PID file: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.pid` (mode `0600`)
- Log file: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log` (mode `0600`)
- Reversible preview stop instruction, not executed: `kill "$(cat /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.pid)"`
- Ignored dependency link: `/Users/hyungkoookkim/evidence-ledger/web/node_modules` resolves exactly to `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules`.
- Ignored local public configuration contains exactly `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`; its URL is `http://127.0.0.1:54321`, its key has the public publishable-key shape, its mode is `0600`, and the key value was never printed or recorded.

The unchanged no-acquisition profile passed: `npm test` ran 24 files and 260/260 tests; `npm run build` passed typecheck, production build, and the 9-file distribution check. The built CSP is exactly `connect-src 'self' http://127.0.0.1:54321 ws://127.0.0.1:54321`; generated source maps are absent; target smoke is `OK`.

The frozen local runtime remains ready without lifecycle change:

- DB `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, image `public.ecr.aws/supabase/postgres:17.6.1.140`: running, healthy.
- Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, image `public.ecr.aws/supabase/gotrue:v2.192.0`: running, healthy; health endpoint HTTP `200`.
- PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, image `public.ecr.aws/supabase/postgrest:v14.14`: running.
- Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`, image `public.ecr.aws/supabase/kong:2.8.1`: running, healthy.
- Aggregate-only database proof: exactly one active local owner. No identity was read or recorded.

## Browser Boundary

Fresh local browser evidence at the teaching URL shows title `판매 의사결정`, heading `소유자 로그인`, one `이메일` field, one `비밀번호` field, one enabled `로그인` submit button, one form, no update banner, and zero console errors. The browser tab is preserved for Coordinator handoff. Director did not click, fill, submit, authenticate, or cross the private login boundary.

Coordinator alone may now use the parent-held credential solely through that local browser UI to verify successful sign-in, the Korean owner-center and `필요 정보` workspace, sole-owner role, and the complete server-ordered financial and risk input list. No owner-setting value may be prefilled, inferred, entered, or recorded, and policy must not be activated. The preview remains running so the user can enter the actual numbers live during teaching.

## Private And Operational Boundaries

No private credential, Auth identity, service-role key, session token, owner-setting value, or business input was requested, inferred, received, transmitted, printed, persisted, or recorded. The earlier wrong relative log path launched no preview; the first detached preview did not persist and left no listener. The final sole live listener is PID `36839` above. No source edit, target commit, service lifecycle change, dependency or image acquisition, default/managed database mutation, real/private data action, policy activation, deployment, physical installation, Windows work, remote publication, provider contact, booking, spend, cursor, lock, cleanup, force action, or history rewrite occurred.

Director stops here at the committed non-secret teaching-ready checkpoint. Coordinator private browser acceptance is the only next authorized action.

Cursor at send: 0
