# Coordinator → All: route exact Mac loopback origin correction

**When:** 2026-07-22T08:59:52Z · **From:** coordinator (online)

Task-board: ledger-beta-mac-loopback-origin-2026-07-22
Task ID: ledger-beta-mac-loopback-origin-2026-07-22
Program board: ledger-beta-mac-activation-2026-07-22
Status: ACTIVE — EXACT LOOPBACK-ORIGIN CORRECTION, INDEPENDENT REVIEW, AND MAC PREVIEW RESUME
Route generation: 36
Supersedes route: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md
Superseded route ref: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
Expected control HEAD: abdc20936a737a539afd2919937faca936f4f6f4
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Binding blocker: coordination/mailbox/sent/2026-07-22T08-50-57Z-director-to-coordinator-coordination.md@abdc20936a737a539afd2919937faca936f4f6f4
Provisioning closeout: coordination/mailbox/sent/2026-07-22T08-41-16Z-coordinator-to-director-coordination.md@7d5b62bbbdfe0f4b6b43fc2c3bc132e08624f840
Held Director contract: coordination/mailbox/sent/2026-07-22T08-18-44Z-director-to-all-coordination.md@04b911e0e427613a313507f584b780029b2e594a
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: d66601dd843120e3989fe3099b529abaecff47db
Accepted target HEAD: d66601dd843120e3989fe3099b529abaecff47db
Correction worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-loopback-origin
Correction branch: codex/beta-mac-loopback-origin

## Coordinator disposition

The migrated local runtime and sole owner are healthy. The first exact PWA build stopped
before output because the reviewed source rejects the only live local API origin,
`http://127.0.0.1:54321`. HTTPS fails against that frozen listener. The public client key
has the required publishable shape and is not the blocker.

The blocker spans one contract implemented at three boundaries: runtime environment
validation, build-time CSP construction, and distribution CSP verification. Correct all
three together so the first successful build does not merely advance to a second known
failure. Preserve the HTTPS production contract and admit HTTP only for the one exact
canonical loopback origin required by this Mac beta.

## Outcome contract

Director creates one isolated correction commit from the accepted target head using RED
then GREEN, obtains one binding non-author Operator2 verdict on the actual range, and
integrates only a GO-bound commit by local fast-forward. After integration, Director
creates the ignored local public configuration, builds and starts the persistent loopback
preview, verifies the Korean signed-out surface, and stops at the private-login boundary.
Coordinator alone performs the private authenticated owner-flow check without recording
the credential or session. Windows packaging remains held until the user accepts the Mac
teaching run.

The existing Director remains owner; this route changes scope, not ownership. A separate
pre-implementation acceptance event is unnecessary. Director's first durable child is the
canonical verify-request after the correction commit and fresh verification exist.

## Target Allowed Paths

- web/package.json
- web/vite.config.ts
- web/src/config/env.ts
- web/src/config/env.test.ts
- web/scripts/check-pwa-dist.mjs

## Allowed Path Semantics

These five existing files are the complete tracked write set. Change `web/package.json`
only if required to pass the build mode explicitly to the existing distribution checker.
There is no dependency or lockfile change. Ignored `web/node_modules`, `web/.env.local`,
`web/dist`, and `data/local-beta` may be used only under the exact tokens below.

## Required RED and root correction

Add focused failing cases before implementation. They must prove that the current bytes
reject the exact production-build origin `http://127.0.0.1:54321` and that near misses stay
rejected. The correction must then satisfy all of these conditions:

- accept HTTP only when the raw origin is exactly `http://127.0.0.1:54321`, including in
  the production-mode bundle used by `vite preview`;
- continue to accept structurally valid HTTPS origins under the current credential,
  pathname, query, and fragment restrictions;
- reject every other HTTP host or port, including `localhost`, unported loopback, another
  loopback port, credentials, path, query, fragment, and non-loopback hosts;
- emit `connect-src 'self' http://127.0.0.1:54321 ws://127.0.0.1:54321` for the exact local
  bundle, while preserving HTTPS plus matching WSS for normal production origins;
- make the distribution checker reconstruct and compare the expected CSP from the same
  explicitly selected build mode/configuration, not derive expected truth from generated
  `dist/index.html`; and
- keep the publishable-key checks, forbidden VITE-name checks, no-source-map rule, asset
  integrity checks, service-worker checks, offline shell, and all other fail-closed PWA
  boundaries unchanged.

The earlier blocker build is valid RED evidence for the build-time boundary. The focused
runtime test must also be observed failing before the source correction, then passing.

## Side-Effect Executor Token

- effect: isolated Mac loopback-origin correction and one target commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-loopback-origin on codex/beta-mac-loopback-origin
- scope: require normal main and HEAD exactly d66601dd843120e3989fe3099b529abaecff47db with tracked/index state clean and only preserved `.vscode/`; create the named worktree and branch from that head; permit one ignored local `web/node_modules` link to the already-present `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules` only after proving the donor exists; write only the five allowed tracked paths; create exactly one correction commit with parent d66601dd843120e3989fe3099b529abaecff47db; preserve every other ref, worktree, file, local service, database row, backup, and ignored user setting

## Side-Effect Executor Token

- effect: synthetic web correction verification
- executor: director
- target: the correction worktree's web test and build outputs
- scope: use only the preserved dependency donor and synthetic publishable values; run the focused RED/GREEN environment tests, complete Vitest suite, typecheck, ordinary synthetic HTTPS `build:ci`, and exact-loopback production build plus distribution check; inspect the exact local CSP and require no source map; dependency installation, package acquisition, private credential handling, local Auth mutation, service lifecycle change, and real business data are outside this token

## Side-Effect Executor Token

- effect: independent Mac loopback-origin correction review
- executor: operator2
- target: the exact one-commit correction range from d66601dd843120e3989fe3099b529abaecff47db in /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-loopback-origin
- scope: inspect the immutable five-path maximum diff and independently challenge raw-string and URL canonicalization variants, alternate loopback ports and hosts, credentials, path/query/fragment injection, HTTP-to-WS and HTTPS-to-WSS CSP pairing, build-mode selection, distribution-check independence, key/forbidden-name boundaries, source maps, and unchanged PWA integrity checks; run sufficient focused and full synthetic tests; publish exactly one canonical GO, NITS, or FAIL; source repair, target-main integration, private input, default-database mutation, service lifecycle change, and remote-reference publication are outside this token

## Post-GO exact continuation

Only after a committed canonical Operator2 GO, Director publishes and commits one
continuation that freezes the exact correction commit, its parent/tree/subject/path
manifest, canonical verify-request and GO refs, target-main precondition, preserved
settings hash, and the two post-GO tokens below. A material finding is fixed test-first
inside the same five-path maximum and receives a fresh exact verify-request.

## Side-Effect Executor Token

- effect: exact GO-bound local loopback correction integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: only under the committed post-GO continuation; require main and HEAD exactly d66601dd843120e3989fe3099b529abaecff47db and the reviewed correction head to descend directly with exactly one commit and no path outside the allowed set; require the binding Operator2 GO; execute one fast-forward-only local integration to that frozen head; require tracked/index state clean, preserved `.vscode/settings.json` unchanged, and no other ref, worktree, remote reference, or file changed

## Side-Effect Executor Token

- effect: exact local Mac PWA build and persistent preview start
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/web/.env.local, web/dist, data/local-beta, and listener 127.0.0.1:4173
- scope: only after GO-bound integration; require the frozen database/Auth/PostgREST/Kong set still running and ready, Auth health HTTP 200, exactly one active local owner, and the protected backup unchanged; write the ignored config with only `VITE_SUPABASE_URL=http://127.0.0.1:54321` and the local public publishable key without printing its value; run the reviewed no-acquisition production build and distribution check; start exactly one persistent preview at 127.0.0.1:4173 with non-secret PID/log evidence under ignored data/local-beta; verify the Korean signed-out surface and that the login request path is reachable; leave the preview and frozen runtime running on success; if build or preview verification fails, stop only a preview process started by this token and publish one exact blocker without changing service state

## Side-Effect Executor Token

- effect: private local authenticated owner-flow acceptance
- executor: coordinator
- target: the teaching preview at http://127.0.0.1:4173 and the already-provisioned local owner alias
- scope: only after Director's committed teaching-ready checkpoint; use the parent-held credential solely through the local browser UI; do not place it in a command, file, mailbox event, Git object, log, task prompt, or tool output; verify successful sign-in, Korean owner-center reachability, sole-owner role, and sign-out without entering real workbook values, owner settings, bookings, policy activation, or other business data; retain only non-secret pass/fail evidence and leave the preview running for the user's teaching session

## Verification and review contract

Director's canonical verify-request binds the target repository/worktree, exact base and
head, one-commit path manifest, RED evidence, focused and full Vitest results, typecheck,
synthetic HTTPS build, exact-loopback production build and CSP, diff checks, owner/model,
assigned Operator2/model, and immutable blocker/route refs. Dispatch it once to the
existing compatible Operator2 task and reconcile only its committed report.

A required correction outside the five tracked paths, any broader HTTP allowance, any
dependency change, or any need to alter the frozen local service topology stops for
Coordinator reconciliation. Target-main integration and preview start wait for GO.

## Stop boundary

Source work is limited to the exact five-path correction and its isolated commit.
The frozen local database, account membership, containers, protected backup, and private
credential remain untouched during implementation and review. Remote-reference
publication, real workbook import, owner-value entry, policy activation, deployment,
Windows work, provider contact, booking, spend, cursor action, protocol-lock action,
history rewrite, and unrelated cleanup are excluded from this route.

## Exact next trigger

Director reads this committed generation-38 route, implements the five-path-maximum
correction RED-to-GREEN in the named isolated worktree, commits it once, publishes the
canonical verify-request, and dispatches it once to the existing Operator2 task. After a
canonical GO only, Director freezes and performs the exact local integration and preview
tokens, then stops at a committed non-secret teaching-ready checkpoint for Coordinator's
private browser acceptance.

Cursor at send: 0

Cursor at send: 0
