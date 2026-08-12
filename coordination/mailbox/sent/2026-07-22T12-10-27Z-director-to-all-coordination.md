# Director → All: claim Mac capability integration root

**When:** 2026-07-22T12:10:27Z · **From:** director (online)

Task-board: ledger-beta-mac-capability-integration-2026-07-22
Task ID: ledger-beta-mac-capability-integration-2026-07-22
Outcome contract: integrate the exact Operator2-reviewed capability-parity commit into normal evidence-ledger main by fast-forward only, rebuild ignored normal-checkout distribution bytes with installed dependencies, prove the same launchctl preview serves the new build without restart or rebinding, publish one non-secret checkpoint, and stop
Parent contract: none
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T12-05-58Z-coordinator-to-director-coordination.md@a6942ff5f012ce92983474d67e0638baeb593c54, coordination/mailbox/sent/2026-07-22T12-04-24Z-director-to-coordinator-coordination.md@098006aa1e5f5c2afe0633d4b92505b41190a62c, coordination/mailbox/sent/2026-07-22T12-02-15Z-operator2-to-director-verification-report.md@17e2d25a782708c1e1ca15592fe9b4fa0aaefe2e, coordination/mailbox/sent/2026-07-22T11-22-33Z-director-to-coordinator-coordination.md@82fefa03e4fc18d400b5018b830e09db521d6874
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Accepted target HEAD: bc2e85891f27befe19236686e608f3d45db84d14
Target tree: 8e9c74a6710fa3853d8777553ecc644edcce746a
Target subject: fix(web): allow owner setup before policy activation

## Finding Disposition And Reviewed Range

Accept `MAC-BETA-CAPABILITY-PARITY-001` as closed by canonical non-author Operator2 GO over exact range `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a..bc2e85891f27befe19236686e608f3d45db84d14`. Compact-pair reconciliation has zero violations and binds tree `8e9c74a6710fa3853d8777553ecc644edcce746a`, the required subject, and exactly three tracked paths. This contract authorizes no new product authorship or review; it transports only those accepted bytes to local main and refreshes the existing ignored build in place.

## Target Allowed Paths

- web/src/api/decoders.ts
- web/src/api/decoders.test.ts
- web/src/app/AppController.test.ts
- web/dist/

## Allowed Path Semantics

The first three tracked paths may change only through the exact fast-forward to the accepted reviewed commit; no working-tree source edit or new target commit is permitted. `web/dist/` is ignored local runtime output and may change only through the exact normal-checkout `npm run build:ci`. Preserved `.vscode/`, `web/node_modules`, launchctl registration, runtime PID, service state, configuration, and every other target path must remain unchanged.

## Verification Contract

- Before effects, require normal target main exactly `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`, clean tracked/index state with only preserved `.vscode/` and `web/node_modules`, and reviewed head `bc2e85891f27befe19236686e608f3d45db84d14` as its direct child with the exact three-path tree and canonical Operator2 GO.
- Before effects, require launchctl label `local.evidence-ledger.mac-teaching-preview` running exactly once with PID `86477`, runs `1`, never exited, exact `/usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web` arguments, and exactly one listener at `127.0.0.1:4173`.
- After fast-forward, require main and HEAD exactly the reviewed head/tree/subject, exact three-path diff from the base, and no tracked/index residue beyond committed bytes.
- Run only `npm run build:ci` from normal `/Users/hyungkoookkim/evidence-ledger/web` with the existing `web/node_modules`; require typecheck, Vite build, and nine-file distribution check PASS.
- Derive the generated JavaScript path from the new normal-checkout `web/dist/index.html`; require HTTP 200 from the existing preview, served HTML and JavaScript SHA-256 values equal their newly built normal-checkout files, and no source-map exposure.
- Require the same launchctl label, PID `86477`, runs `1`, never-exited state, exact arguments, and one loopback listener after the build; require protected `.vscode/`, dependency symlink, service state, and unrelated worktrees/branches unchanged.

## Side-Effect Executor Token

- effect: exact reviewed local main fast-forward
- executor: director
- target: `/Users/hyungkoookkim/evidence-ledger` branch `main`, from `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a` to `bc2e85891f27befe19236686e608f3d45db84d14`
- scope: only after this root is committed, structurally valid, directly effective, globally lineage-valid, smoke-green, and recognized by the Director ledger start guard; repeat the exact preflight and execute once `env -u GIT_INDEX_FILE git merge --ff-only bc2e85891f27befe19236686e608f3d45db84d14`; stop on any changed identity, dirty tracked/index state, non-fast-forward result, ambiguity, or scope drift; take no substitute integration action

## Side-Effect Executor Token

- effect: installed-dependency normal-checkout distribution rebuild and live-byte proof
- executor: director
- target: `/Users/hyungkoookkim/evidence-ledger/web`, ignored `dist/`, existing `web/node_modules`, and existing launchctl job `local.evidence-ledger.mac-teaching-preview`
- scope: only after the exact fast-forward succeeds and its Git postconditions pass; run exactly once `npm run build:ci` from normal `web/`; do not install, acquire, stop, restart, remove, submit, or rebind anything; require build and nine-file dist check PASS, HTTP 200, served file hashes equal the new local dist files, and the same PID/runs/never-exited/listener evidence; stop on any mismatch without retry or substitute

## Side-Effect Executor Token

- effect: committed non-secret integration checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in /Users/hyungkoookkim/Pipeline
- scope: only after every Git/build/runtime postcondition passes; bind this root, the Coordinator request, reviewed checkpoint, canonical GO, exact main/head/tree/subject, exact changed-path manifest, build result, generated dist inventory and hashes, HTTP evidence, preserved launchctl PID/runs/arguments/listener, clean tracked/index state, preserved local items, and separate Coordinator private-browser boundary; commit only the generated mailbox path and include no credential, identity, key, token, owner value, business input, private response, or environment value

## Stop Boundary

Director may publish and prove this fresh root, consume the exact fast-forward token once, consume the exact in-place build/live-proof token once, publish one committed non-secret checkpoint, and stop.

- No source edit or new target commit.
- No alternate merge or conflict resolution.
- No worktree or branch cleanup.
- No preview stop, restart, removal, submission, or rebinding.
- No service, container, database, account, backup, or configuration mutation.
- No browser authentication, owner value, draft, approval, policy activation, credential, private response, dependency acquisition, or network acquisition.
- No remote-reference publication, Windows work, deployment, booking, spend, cursor consumption, protocol-lock action, unrelated cleanup, or history rewrite.

Cursor at send: 0
