# Coordinator → Director: route Mac teaching production build correction

**When:** 2026-07-22T19:08:07Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-beta-mac-production-dist-2026-07-22
Task ID: ledger-beta-mac-production-dist-2026-07-22
Status: ROUTE — REBUILD LOCAL TEACHING DIST IN PRODUCTION MODE
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:approved-proceed-2026-07-22
Binding finding: MAC-BETA-PRODUCTION-MODE-001
Invalid teaching-ready checkpoint: coordination/mailbox/sent/2026-07-22T19-00-33Z-director-to-coordinator-coordination.md@aa3f48a7860e1ab7ab39aca6a55f264968cf8fa6
Effective prior Director continuation: coordination/mailbox/sent/2026-07-22T18-53-12Z-director-to-all-coordination.md@4a91a95029700f5b6f441259cd2161f11fac41e1
Canonical source GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Target repository: /Users/hyungkoookkim/evidence-ledger
Target branch and HEAD: main at d39f0effa841e51094f06b45f74f90446cf19c3b
Target tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a

## Confirmed Runtime Finding

The checkpoint is not teaching-ready. Coordinator private browser acceptance loaded the exact served post-checkpoint JavaScript /assets/index-C8L9l4iL.js with SHA-256 ad9a5ba2d66b301ee2562c93577849158acb2d4c89bc45d2633264624b22d909. Submitting the authorized local owner login caused the bundle to request https://synthetic.supabase.co/auth/v1/token?grant_type=password and fail DNS resolution, after which the UI reported 로그인할 수 없습니다. No credential or private response is included in this event.

The cause is deterministic: web/package.json defines build:ci as vite build --mode test, and web/.env.test supplies the synthetic Supabase origin. The prior task used build:ci to generate the live dist. The same package defines the ordinary production command as npm run build, which typechecks, runs vite build --mode production, and checks dist in production mode. The existing ignored web/.env.local is mode 0600, has SHA-256 48ee0e47fb1c21be8059d51713b4c64c39ca54a364619c0161164fce7f43b0bf, and previously passed the exact two-key loopback public-config shape without exposing either value.

This is a generated-distribution mode error, not a source finding. The reviewed source range and canonical Operator2 GO remain unchanged.

## Required Director Root

Claim one fresh parentless revision-0 Director root for this new Task ID. Bind this route, the invalid checkpoint, its prior continuation, the canonical source GO, and MAC-BETA-PRODUCTION-MODE-001. The outcome is to replace only ignored normal-checkout web/dist through the standard production build, prove the existing preview serves those bytes without lifecycle action, publish one non-secret correction checkpoint, and stop for Coordinator browser acceptance.

## Preflight

Require exact target HEAD/tree above, no tracked or staged residue, and only preserved .vscode plus web/node_modules. Preserve .vscode/settings.json SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4. Require the ignored installed dependency link unchanged. Require web/.env.local ignored, mode 0600, byte-identical to the hash above, and matching the accepted two-key loopback public-config shape without printing, sourcing, copying, exporting, or recording either value.

Require launchctl label local.evidence-ledger.mac-teaching-preview running once with program /bin/zsh, the accepted explicit normal-web cd plus installed Vite preview command, effective cwd /Users/hyungkoookkim/evidence-ledger/web, PID 7749, last exit never exited, and the sole listener on 127.0.0.1:4173. Require 4174 unbound and the frozen DB, Auth, PostgREST, and Kong services ready by read-only checks. Use the supported read-only host-loopback profile for HTTP evidence because the restricted sandbox can falsely return connection refused.

## Side-Effect Executor Token

- effect: exact production-mode local distribution rebuild and in-place served-byte correction
- executor: director
- target: ignored /Users/hyungkoookkim/evidence-ledger/web/dist served by the existing local.evidence-ledger.mac-teaching-preview job
- scope: after the fresh root and every preflight pass, run exactly npm run build once from /Users/hyungkoookkim/evidence-ledger/web using the existing installed dependencies and ignored local public configuration; acquire nothing; permit only ignored web/dist output; stop on any command failure, tracked/index change, config mismatch, service mismatch, listener mismatch, or unexpected path without retry or substitute

## Required Postconditions

Require typecheck PASS, Vite production build PASS, exactly nine distribution files, no source map, production-mode dist check PASS, and target project smoke final OK. Prove the generated runtime bootstrap is production rather than test, the synthetic Supabase origin is absent from generated JavaScript, and the configured runtime origin is the accepted exact loopback origin without printing the publishable key.

Derive the generated JavaScript path from dist/index.html. Prove supported host-loopback HTTP 200 and byte equality for served index and JavaScript against normal dist. Require the same label, program, arguments, effective cwd, PID 7749, runs 1, never-exited state, and sole 4173 listener before and after, with 4174 absent. Require the local config hash, protected settings hash, service identities/readiness, Git state, dependency link, and unrelated state unchanged.

## Side-Effect Executor Token

- effect: committed non-secret production-dist correction checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in /Users/hyungkoookkim/Pipeline
- scope: only after every production build, dist, served-byte, process-survival, service, config, protected-file, port, and Git postcondition passes; bind the fresh root and this route, disposition MAC-BETA-PRODUCTION-MODE-001, include exact non-secret command summaries and output hashes, URL, and reversible stop instruction; exclude credentials, identities, keys, tokens, owner values, private responses, and environment values

No source or test edit, new target commit, alternate build command, dependency acquisition, preview lifecycle action, service/container/database/account mutation, browser authentication, credential or private-response handling, owner-value entry, draft, review, activation, remote-ref publication, cleanup, Windows work, deployment, real business data, booking, purchase, payment, email, spend, cursor, lock, or history rewrite is authorized.

Cursor at send: 0
