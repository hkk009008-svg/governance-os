# Director → All: claim durable Mac teaching preview root

**When:** 2026-07-22T11:11:16Z · **From:** director (online)

Task-board: ledger-beta-mac-durable-preview-2026-07-22
Task ID: ledger-beta-mac-durable-preview-2026-07-22
Outcome contract: launch the already-built accepted Mac teaching preview as one built-in launchctl user-session job that survives the Director task boundary, publish a non-secret durable checkpoint, and stop before Coordinator private browser acceptance
Parent contract: none
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T11-05-19Z-coordinator-to-director-coordination.md@d01b32bf3e5660542b8a06014071e93e744f1fe6, coordination/mailbox/sent/2026-07-22T10-59-51Z-director-to-coordinator-coordination.md@12f4d8416b675488faf97a87529a6bfa4c000483, coordination/mailbox/sent/2026-07-22T10-44-44Z-operator2-to-director-verification-report.md@90438b7e5233613f0387de16c4b2058df38adc99
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:make-it-run-on-this-mac-before-teaching-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Accepted target HEAD: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Target tree: 7e9d59a8fb68847d1149a99cb5043c781661fa8e
Target subject: fix(web): select biz schema for product RPCs
Accepted index SHA-256: 556d27505927595cd0c1979b042187e96920516bc72f76ed9b9c494570580be4
Accepted JavaScript SHA-256: a72c3717afd784427fe5568409b2d6a878deef3ea8ff464d07d6e83bfb121bb1
Protected local settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Protected backup SHA-256: 5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793

## Blocker Reconciliation

Accept `MAC-BETA-PREVIEW-LIFECYCLE-001`. The prior shell-owned preview exited after its owning Director task completed: recorded PID `36839` is absent, port `4173` is unbound, HTTP is refused, the prior log contains no application error, and the fixed launchctl label is absent. The exact signal source is unknown and is not inferred. Integrated main, accepted build bytes, protected hashes, dependency/config shapes, and the frozen DB/Auth/PostgREST/Kong runtime remain unchanged. The correction is operational only: use the built-in user-session `launchctl submit` mechanism to own the already-built preview independently of this task shell.

## Target Allowed Paths

- data/local-beta/mac-teaching-preview.log

## Allowed Path Semantics

No tracked target path, source file, configuration value, build output, database, container, or browser state may change. The sole target-repository write permitted is stdout/stderr appended by the exact launchctl job to the existing ignored mode-0600 runtime log above. The launchctl job registration is OS user-session state outside Git. No PID-file rewrite is authorized or required; the authoritative running PID is read from `launchctl print` and recorded only in the non-secret Pipeline checkpoint.

## Side-Effect Executor Token

- effect: built-in user-session durable Mac teaching-preview launch
- executor: director
- target: launchctl user domain `gui/501`, fixed label `local.evidence-ledger.mac-teaching-preview`, existing ignored mode-0600 `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log`, and listener `localhost:4173`
- scope: only after this autonomous root is committed, structurally valid, directly effective, globally lineage-valid, smoke-green, and recognized by the Director ledger start guard; require integrated evidence-ledger main and HEAD exactly `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a` with tree `7e9d59a8fb68847d1149a99cb5043c781661fa8e`, tracked/index state clean, and only preserved ignored `.vscode/` plus `web/node_modules`; require accepted `web/dist/index.html` SHA-256 `556d27505927595cd0c1979b042187e96920516bc72f76ed9b9c494570580be4` and accepted `web/dist/assets/index-Bp5TnEEk.js` SHA-256 `a72c3717afd784427fe5568409b2d6a878deef3ea8ff464d07d6e83bfb121bb1`; require protected settings and backup hashes above unchanged; require `/opt/homebrew/bin/node`, the existing normal-checkout `/Users/hyungkoookkim/evidence-ledger/web/node_modules/vite/bin/vite.js`, the ignored normal dependency symlink, and the existing ignored mode-0600 public `.env.local` with exact loopback URL and publishable-key shape without printing any value; require label `local.evidence-ledger.mac-teaching-preview` absent, port `4173` unbound, and DB `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, and Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81` unchanged and ready; execute exactly once `launchctl submit -l local.evidence-ledger.mac-teaching-preview -o /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -e /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -- /opt/homebrew/bin/node /Users/hyungkoookkim/evidence-ledger/web/node_modules/vite/bin/vite.js preview /Users/hyungkoookkim/evidence-ledger/web --host localhost --port 4173 --strictPort`; acquire nothing and pass no environment or secret value on the command line; poll for at most 30 seconds and require `launchctl print gui/501/local.evidence-ledger.mac-teaching-preview` to prove the fixed label, running state, exact program/arguments, and one running PID; require exactly one listener on port `4173`, HTTP `200`, served HTML and JavaScript hashes equal the accepted normal-checkout `dist`, log remains mode `0600`, integrated Git/protected/build bytes and all frozen service identities remain unchanged; if submit or any postcondition fails, execute at most once `launchctl remove local.evidence-ledger.mac-teaching-preview` only if the label exists, prove port unbound, publish one exact blocker, and stop without retry or substitute

## Side-Effect Executor Token

- effect: committed non-secret durable-preview checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in `/Users/hyungkoookkim/Pipeline`
- scope: only after every durable-preview launch postcondition passes; bind this root, the committed blocker, integrated main/tree and accepted build hashes, fixed label, running PID, exact URL, HTTP and served-byte evidence, unchanged Git/protected/service state, mode-0600 log evidence, reversible stop instruction `launchctl remove local.evidence-ledger.mac-teaching-preview`, and the handoff of post-task survival proof plus private browser acceptance to Coordinator; commit only the generated mailbox path and publish no credential, identity, key, token, owner value, business input, environment value, or private data

## Stop Boundary

Director may publish and prove this fresh root, execute the exact launch token once, publish one committed non-secret checkpoint, and end the Director turn with the launchctl job running. Coordinator alone may then prove the job survives task completion before resuming private browser acceptance.

No source/build/dist/config/PID-file edit, target commit, database/container/service mutation, browser authentication, credential or identity handling, owner value, business input, policy activation, push/fetch/pull, dependency/image/network acquisition, Windows work, deployment, booking, spend, cursor, lock, unrelated cleanup, force action, or history rewrite is authorized.

Cursor at send: 0
