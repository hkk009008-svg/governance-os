# Director → All: claim Mac production dist correction root

**When:** 2026-07-22T19:13:32Z · **From:** director (online)

Task-board: ledger-beta-mac-production-dist-2026-07-22
Task ID: ledger-beta-mac-production-dist-2026-07-22
Outcome contract: replace only ignored normal-checkout web/dist through the standard production build, prove the existing durable preview serves those exact bytes without lifecycle action, publish one non-secret production-dist correction checkpoint, and stop for Coordinator browser acceptance
Parent contract: none
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T19-08-07Z-coordinator-to-director-coordination.md@338b4cd44aef943a6421a90db58391f554feadba, coordination/mailbox/sent/2026-07-22T19-00-33Z-director-to-coordinator-coordination.md@aa3f48a7860e1ab7ab39aca6a55f264968cf8fa6, coordination/mailbox/sent/2026-07-22T18-53-12Z-director-to-all-coordination.md@4a91a95029700f5b6f441259cd2161f11fac41e1, coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:approved-proceed-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Binding finding: MAC-BETA-PRODUCTION-MODE-001
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Accepted target HEAD: d39f0effa841e51094f06b45f74f90446cf19c3b
Accepted target tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a
Canonical source GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Durable preview label: local.evidence-ledger.mac-teaching-preview
Durable preview PID: 7749
Durable preview listener: 127.0.0.1:4173
Ignored public configuration: existing mode-0600 loopback public configuration only; values excluded from this event

## Finding Reconciliation

MAC-BETA-PRODUCTION-MODE-001 is confirmed. The invalid checkpoint bound a test-mode generated JavaScript bundle that contacted synthetic.supabase.co. The reviewed source and its canonical Operator2 GO remain unchanged. This contract permits only regeneration of ignored distribution bytes with the repository's standard production command and non-secret proof that the existing preview serves the corrected bytes.

## Target Allowed Paths

- web/dist/

## Allowed Path Semantics

web/dist/ is ignored generated runtime output and may change only through the exact standard production build. Every tracked target path, web/.env.local, web/node_modules, protected .vscode/, launchctl registration and process identity, services, every unrelated worktree/ref/file, and all remote refs remain preserved.

## Verification Contract

- Before any target effect, require this root committed, structurally valid, directly effective, globally lineage-valid, Pipeline smoke-green, and recognized by the Director ledger start guard.
- Require target HEAD/tree exactly d39f0effa841e51094f06b45f74f90446cf19c3b/65d9b036a6847fef401d41135bdc6d7d5160a99a with no tracked or staged residue and only preserved .vscode plus web/node_modules.
- Preserve .vscode/settings.json SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4 and the ignored installed dependency link.
- Require ignored web/.env.local mode 0600, byte-identical to SHA-256 48ee0e47fb1c21be8059d51713b4c64c39ca54a364619c0161164fce7f43b0bf, and matching the accepted exact two-key loopback public-config shape without printing, sourcing, copying, exporting, or recording either value.
- Require launchctl label local.evidence-ledger.mac-teaching-preview running once with program /bin/zsh, accepted explicit normal-web cd plus installed Vite preview command, effective cwd /Users/hyungkoookkim/evidence-ledger/web, PID 7749, never exited, and the sole listener on 127.0.0.1:4173. Require 4174 unbound and frozen DB, Auth, PostgREST, and Kong services ready by read-only checks.
- Use the supported read-only host-loopback profile for HTTP evidence.
- After the exact build, require typecheck PASS, Vite production build PASS, exactly nine distribution files, no source map, production-mode dist check PASS, and target project smoke final OK.
- Derive the generated JavaScript path from dist/index.html; require synthetic.supabase.co absent, the accepted exact loopback runtime origin present without printing the publishable key, supported host-loopback HTTP 200, and served index and JavaScript bytes equal local dist.
- Require the same launchctl label, program, arguments, effective cwd, PID 7749, runs 1, never-exited state, and sole 4173 listener before and after, with 4174 absent.
- Require local config hash, protected settings hash, service identities/readiness, Git state, dependency link, and unrelated state unchanged.

## Side-Effect Executor Token

- effect: exact production-mode local distribution rebuild and in-place served-byte correction
- executor: director
- target: ignored /Users/hyungkoookkim/evidence-ledger/web/dist served by existing local.evidence-ledger.mac-teaching-preview
- scope: after this root and every preflight pass, run exactly npm run build once from /Users/hyungkoookkim/evidence-ledger/web using existing installed dependencies and ignored local public configuration; acquire nothing; permit only ignored web/dist output; stop on any command failure, tracked/index change, config mismatch, service mismatch, listener mismatch, or unexpected path without retry or substitute

## Side-Effect Executor Token

- effect: committed non-secret production-dist correction checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in /Users/hyungkoookkim/Pipeline
- scope: only after every production build, dist, served-byte, process-survival, service, config, protected-file, port, and Git postcondition passes; bind this root and the Coordinator route, disposition MAC-BETA-PRODUCTION-MODE-001, include exact non-secret command summaries and output hashes, URL, and reversible stop instruction; exclude credentials, identities, keys, tokens, owner values, private responses, and environment values

## Stop Boundary

Director may publish and prove this root, consume the exact production build token once, publish one committed non-secret correction checkpoint, and stop with the durable preview running for Coordinator-owned private browser acceptance.

No source or test edit, target commit, alternate build command, dependency acquisition, preview lifecycle action, service/container/database/account mutation, browser authentication, credential or private-response handling, owner-value entry, draft, review, activation, remote-ref publication, cleanup, Windows work, deployment, real business data, booking, purchase, payment, email, spend, cursor, lock, or history rewrite is authorized.

Cursor at send: 0
