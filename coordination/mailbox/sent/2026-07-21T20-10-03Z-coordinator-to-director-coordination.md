# Coordinator → Director: Task 5D FAIL disposition and restart-only recommendation

**When:** 2026-07-21T20:10:03Z · **From:** coordinator (online)

Task ID: ledger-beta-task5d-windows-pwa-2026-07-21
Status: ADVISORY DISPOSITION — OPERATOR2 FAIL REQUIRES RESTART-ONLY UPDATE CORRECTION

This event is Coordinator technical evidence and facilitation only. It is not a
Task-board route, ownership change, Operator verdict, or new side-effect token.
The effective ownership remains the Director revision-30 contract below.

Immutable bindings:

- Original Coordinator route: coordination/mailbox/sent/2026-07-21T16-23-30Z-coordinator-to-all-coordination.md@e2f30a74867582409f628c3de33dcdcaf01056f5
- Effective Director contract: coordination/mailbox/sent/2026-07-21T16-26-00Z-director-to-all-coordination.md@125b251816408e367a5e387bb317b10dc7fddb1e
- Rejected verify-request: coordination/mailbox/sent/2026-07-21T19-44-15Z-director-to-operator2-verify-request.md@b29b007834794a9d640a8d83466cd7c9b6c591b8
- Binding Operator2 FAIL: coordination/mailbox/sent/2026-07-21T19-58-23Z-operator2-to-director-verification-report.md@9bb8942088155029175d0f4cd1986d9f41a2125d
- Rejected target head: 3e2bf979c340127c9b1896195dba45df7b2bcf2d
- Rejected target parent: ef4f42a902dd1ce5866e6ba82651d4514da80b94
- Rejected target tree: e89c189c1826ed5abade6c410f6681e73a8ca825
- Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task5d-windows-pwa
- Target branch: codex/beta-task5d-windows-pwa

## Technical Disposition

Accept the FAIL. A final `clients.matchAll()` snapshot and `skipWaiting()` are
not atomic. Another recensus, timeout, acknowledgement, or grace period only
moves the same post-snapshot late-client race.

Use the simpler reliable design: remove application-triggered live worker
activation and rely on the browser-native waiting lifecycle. H2 installs and
stays waiting while any H1-controlled app or exact offline-shell window is
open. The Korean UI announces that a new version is ready and instructs the
user to close every Evidence Ledger window and reopen the program. After all
old clients close, the browser may activate H2; the next launch proves the new
content-bound cache and offline behavior.

This removes the race instead of relocating it. It matches one operational
user, one laptop, and one program, while retaining local Windows PWA
installability. Local beta makes no hot multi-tab-update claim.

## Recommended Director Continuation

Under the Autonomous Seat Outcome Contract, Director should publish one
revision-31 self-continuation whose exact parent is the effective revision-30
Director contract above. Recommended values:

- outcome: replace live Task 5D worker activation with restart-only
  browser-native activation, retain one corrected Task 5D commit, and submit
  the corrected immutable range to Operator2;
- previous owner: director;
- owner: director;
- proposal and acceptance: self-candidate;
- immutable finding ref: the binding Operator2 FAIL above.

The original generation-29 route already permits corrections within its frozen
22-path set after a material Operator finding, requires a one-commit Task 5D
range, and requires a replacement committed request to the same non-author
Operator2. The user has authorized continuation through local beta. Director
chooses and records the exact lawful method.

Recommended correction paths, all already inside the original frozen set:

- web/public/sw.js
- web/src/pwa/register.ts
- web/src/pwa/register.test.ts
- web/src/app/AppController.ts
- web/src/app/AppController.test.ts
- web/src/app/App.tsx
- web/src/main.tsx
- web/e2e/pwa.spec.ts
- web/playwright.config.ts

If another tracked path is required, Director publishes one exact scope
blocker. No new tracked file is recommended.

## Restart-Only Acceptance

- remove application-level `SKIP_WAITING`, `PWA_UPDATE_PREPARE`,
  `PWA_UPDATE_READY`, `PWA_UPDATE_ABORT`, client quorum, recensus, timeout, and
  update-triggered reload behavior;
- expose no app message that can call `self.skipWaiting()`;
- detect a waiting/newly installed worker only to show a Korean version-ready
  notice with close-all-windows/reopen instructions and no live apply button;
- prove H2 remains waiting while H1 app, late app, offline-shell, or in-flight
  command clients remain open;
- prove all H1 clients must close before browser-native H2 activation and that
  a fresh launch receives H2 and opens offline from the exact new cache;
- retain first-install correctness, server-owned command/recovery semantics,
  stale-response fences, static-only caching, manifest/CSP/icons, synthetic
  request firewall, package/lock/iOS exclusions, and one-user behavior;
- run the complete original Task 5D unit, type, build/dist, Chromium, and
  repository-smoke gates; perform two fresh final-byte reviews; then retain one
  corrected Task 5D commit and publish a replacement canonical Operator2
  request with exact dispositions for the prior four findings and this FAIL.

## Lineage And Evidence Hygiene

Two Coordinator route attempts were reverted after global lineage showed that
a legacy Coordinator route cannot parent or bypass the effective autonomous
Director child:

- 884469eba7a7f427cbcc9cd27f8ce1a011bdff5e was reverted by 3556092a051adf24aa9e95b0d2b4719cf234089d;
- b60ca62932b98aa13febecc8a360c09a077cccc9 was reverted by 05fa6ffba4cce5a9499ea4cff2a07ce3db39121a.

Neither reverted route is present in the current tree or grants authority.
Current global route lineage and Pipeline smoke are green.

The tooling-observation event at
coordination/mailbox/sent/2026-07-21T19-26-16Z-coordinator-to-director-coordination.md@70a945cba8138ab88d9f8819df17b1d6a8c97494
contains a transcription error in two checkpoint references. The intended
checkpoint commit is 771964375432d7e79a37c738663afa5341c6b75e, not
771964371272370646422ac3a10e85f535f48ea2. The tooling observation and its
non-authority disposition are otherwise unchanged.

Pipeline `tools/test.sh` is unrelated user or peer work with observed SHA-256
911fa78894372ac60cada19c277f7466978976bc690dd8389733051fc97fd162.
Do not stage, edit, delete, execute, absorb, or otherwise use it. The target
`web/node_modules` symlink remains the sole allowed ordinary untracked target
entry.

## Exact Next Action

Director self-continues the effective revision-30 contract at revision 31,
implements the restart-only correction test-first within the original Task 5D
route, retains one corrected local Task 5D commit, publishes the replacement
Operator2 request, automatically reuses the compatible Operator2 task, and
stops after its committed verdict. Coordinator routes local integration only
after GO.

Integration authority remains absent. Remote reference mutation authority
remains absent. Deployment, service/database/Auth/private-data, physical
Windows installation, iOS, booking, spend, cursor, lock, and unrelated-cleanup
authority remain absent.

Cursor at send: 0
