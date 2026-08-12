# Director → Coordinator: report Mac biz schema teaching preview rebound

**When:** 2026-07-22T10:59:51Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-biz-schema-integration-2026-07-22
Task ID: ledger-beta-mac-biz-schema-integration-2026-07-22
Status: TEACHING-READY — BIZ-SCHEMA CORRECTION INTEGRATED AND PREVIEW REBOUND; STOPPED AT PRIVATE BROWSER BOUNDARY
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-for-teaching-2026-07-22
Coordinator request: coordination/mailbox/sent/2026-07-22T10-49-21Z-coordinator-to-director-coordination.md@3ce963303631be5908976fc89eb30f9294e899ab
Autonomous root: coordination/mailbox/sent/2026-07-22T10-54-18Z-director-to-all-coordination.md@eb6c45785d7ba9f9db6872da8191167328e614e0
Canonical verify-request: coordination/mailbox/sent/2026-07-22T10-35-36Z-director-to-operator2-verify-request.md@59f341df26dbd4a911ead1fde0740557be2c76fb
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T10-44-44Z-operator2-to-director-verification-report.md@90438b7e5233613f0387de16c4b2058df38adc99

## Integrated Reviewed Correction

- Repository: `/Users/hyungkoookkim/evidence-ledger`
- Main and HEAD: `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`
- Reviewed parent: `e4ddbf69cf4ed401289d719cc4910cae66e3833b`
- Tree: `7e9d59a8fb68847d1149a99cb5043c781661fa8e`
- Subject: `fix(web): select biz schema for product RPCs`
- Exact paths: `web/src/main.tsx`, `web/src/api/supabase.ts`, and `web/src/api/supabase.test.ts`
- Path manifest SHA-256: `e8bdf4ae94e08f64e8f088cd310d7dccd40c8f5fdc5e2dbb0d1a5b522f76456c`
- Patch SHA-256: `136489d87ed63b01387936f924a09ecfedba181783b63e332e7d92d361a3d659`
- Result: the exact local `git merge --ff-only acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a` completed once. No merge commit or target commit was created. `origin/main` remains unchanged at `68566090b2904b86f48e42ffb5f3216856b8ac1c`; no remote ref changed.

The normal checkout has a clean index and tracked tree. Its only visible untracked paths remain the preserved ignored `.vscode/` and `web/node_modules`. The dependency symlink still resolves exactly to `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules`. Protected `.vscode/settings.json` SHA-256 remains `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`; protected backup SHA-256 remains `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`. The accepted correction worktree and every unrelated worktree/ref were preserved.

## No-Acquisition Build Evidence

- Focused schema regression: 1 file and 3/3 tests passed.
- Full web suite: 25 files and 263/263 tests passed.
- Explicit typecheck passed.
- Production build passed: Vite transformed 103 modules; the 9-file production distribution check passed.
- Target `scripts/ci_smoke.py`: `OK`.
- Generated source maps: zero.
- Built CSP: exact loopback `connect-src 'self' http://127.0.0.1:54321 ws://127.0.0.1:54321` pair passed.
- Static sensitive-literal checks: routed tracked paths and built distribution contain no service-role, private-key, or private-credential literal. The ignored local configuration remains mode `0600`, contains exactly `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`, has the exact loopback URL, and passes the public-key shape check without printing or recording its value.

No dependency, browser, image, or network acquisition occurred. The build updated only ignored normal-checkout `web/dist`; no source byte or tracked target state changed after the reviewed fast-forward.

## Rebound Teaching Preview

- Non-secret teaching URL: `http://127.0.0.1:4173/`
- Existing listener retained: exactly one Node listener, PID `36839`, at `127.0.0.1:4173`.
- Host HTTP health: `200`.
- Served `index.html` SHA-256 equals rebuilt `web/dist/index.html`: `556d27505927595cd0c1979b042187e96920516bc72f76ed9b9c494570580be4`.
- Served accepted JavaScript SHA-256 equals rebuilt `web/dist/assets/index-Bp5TnEEk.js`: `a72c3717afd784427fe5568409b2d6a878deef3ea8ff464d07d6e83bfb121bb1`.
- PID file: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.pid` (mode `0600`).
- Log file: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log` (mode `0600`).
- Reversible preview stop instruction, not executed: `kill "$(cat /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.pid)"`.

The listener never restarted and service topology did not change. Frozen runtime evidence remains:

- DB `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, image `public.ecr.aws/supabase/postgres:17.6.1.140`: running, healthy.
- Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, image `public.ecr.aws/supabase/gotrue:v2.192.0`: running, healthy; health endpoint HTTP `200`.
- PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, image `public.ecr.aws/supabase/postgrest:v14.14`: running.
- Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`, image `public.ecr.aws/supabase/kong:2.8.1`: running, healthy.

## Private Browser Boundary And Handoff

Director did not authenticate in a browser and did not click, fill, submit, or cross the private login boundary. Coordinator alone may now resume the parent-owned private browser acceptance against the rebound teaching URL: verify authenticated startup product RPCs avoid `PGRST202`, the Korean owner center and `필요 정보` workspace render, all ten server-ordered fields are visible, and current input remains empty. Coordinator must not prefill, infer, enter, or record owner values and must not activate policy; the user retains live-entry teaching control.

No private credential, Auth identity, key, token, owner-setting value, business input, or private data was requested, inferred, received, transmitted, printed, persisted, routed, or recorded. No source repair, new target commit, browser authentication, service lifecycle, database mutation, dependency/image acquisition, push/fetch/pull, policy activation, Windows work, deployment, physical installation, booking, spend, cursor, lock, cleanup, force action, or history rewrite occurred.

Director stops at this committed non-secret checkpoint. Private browser acceptance is handed back to Coordinator; Windows work remains held.

Cursor at send: 0
