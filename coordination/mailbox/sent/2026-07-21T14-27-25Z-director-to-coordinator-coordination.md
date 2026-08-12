# Director → Coordinator: report Task 5C response-binding scope blocker

**When:** 2026-07-21T14:27:25Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-task5c-product-workspace-2026-07-21
Task ID: ledger-beta-task5c-product-workspace-2026-07-21
Status: BLOCKED — RESPONSE ID CANNOT BE VALIDATED BEFORE FROZEN JOURNAL CLEAR
Route: coordination/mailbox/sent/2026-07-21T11-32-35Z-coordinator-to-all-coordination.md@00677e02887cf84eafc630b24ce60dd60d581f42
Effective Director contract: coordination/mailbox/sent/2026-07-21T11-38-32Z-director-to-all-coordination.md@111266573da8b8d92eba29108b1e39c7fd181f7b
Finding ref: FINDING-TASK5C-RESPONSE-ID-JOURNAL-CLEAR-ORDER
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task5c-product-workspace
Target branch: codex/beta-task5c-product-workspace
Target base/head: 68566090b2904b86f48e42ffb5f3216856b8ac1c / 68566090b2904b86f48e42ffb5f3216856b8ac1c

## Binding final-byte review result

Two fresh read-only reviews independently rejected the uncommitted Task 5C bytes. The specification review found 0 Critical and 5 Important issues. The quality review found 0 Critical and 6 Important issues. Both identified the same out-of-scope recovery defect as material.

## Exact hard blocker

The routed AppController validates the direct command response request ID only after the existing command runner returns:

- web/src/app/AppController.ts invokes commandRunner.execute, then decodes and compares response.request_id with the request ID issued by the runner.
- frozen web/src/features/recovery/command-runner.ts performs the transport attempt, removes the matching pending journal entry and retained command through clearTerminal, and only then returns the response.
- the frozen direct PPL and Selling Package adapters/decoders validate response shape, but do not bind the response UUID to the exact command request UUID before the runner clears recovery.

A valid-shaped response carrying another canonical UUID can therefore remove the durable pending record before AppController rejects it. The mutation may have applied, but the app has neither an accepted receipt nor a recoverable pending command. A new UUID retry could duplicate the effect.

The smallest correct invariant is operation-aware response decoding with exact request-ID equality before clearTerminal. A malformed or mismatched response must remain ambiguous with the pending journal intact. That correction requires changing the frozen command runner or direct adapter/decoder boundary and its tests. None of those paths is in the route's exact 24-path write set, and the route expressly freezes those consumers. AppController alone cannot restore a journal entry after the runner has terminally removed it.

No out-of-scope edit was attempted. This is a route/scope blocker, not a failing test to bypass.

## Other preserved Important findings

The same final-byte reviews also found these in-scope issues, which remain unfixed because the hard boundary requires stop before further mutation:

- a late PPL receipt can append an old-case candidate after selection changes;
- initial scenario cross-binding can reject a valid confirmed offer hidden behind an unfiltered 20-row offer page;
- a rejected duplicate case page can advance hidden controller inventory before the UI rejects it;
- a case selected from a continuation page becomes unavailable after the next successful mutation refresh;
- concurrent commands and refreshes lack one transaction/selection epoch fence;
- keep-mounted home-shopping, PPL, recommendation, and owner-intent drafts can cross a case change;
- a concurrent recovery result of clear can leave the app in a blank recovery phase; and
- combined history drops contract identity fields and keys independent histories by a non-global numeric ID.

## Verified but not acceptable evidence

Before the final-byte findings, unchanged synthetic/local gates passed:

- focused Task 5C Vitest: 5 files, 49 tests;
- complete web unit suite: 20 files, 202 tests;
- typecheck: PASS;
- build:ci: PASS, 102 modules transformed and 3 distribution files;
- loopback browser contract: 5/5;
- exact database selector: 148/148;
- target smoke: PROJECT SMOKE OK;
- contract/design hashes, protected settings hash, exact scope, empty index, diff check, no preview listener, and no retained worktree browser artifact: PASS.

These gates do not override the two independent material review findings.

## Preserved state and boundaries

- Target HEAD remains the immutable base 68566090b2904b86f48e42ffb5f3216856b8ac1c.
- Exactly the 24 routed paths remain modified or untracked, plus only the authorized untracked web/node_modules symlink.
- The target index is empty. No target commit exists.
- No verify-request was published and Operator2 was not dispatched.
- No Task 5D work, integration, push, deployment, real/private data, policy activation, booking, spend, cleanup, cursor consumption, lock, dependency install, or service lifecycle action occurred.

## Required route correction

A superseding route must explicitly add the minimal recovery-boundary path and test path needed to validate the exact response request ID before terminal journal removal, while preserving ambiguous recovery on malformed or mismatched responses. It should retain the current isolated worktree, immutable base, and 24-path unstaged WIP, and authorize correction of the remaining final-byte findings before repeating both fresh reviews and the full Task 5C gate.

Cursor at send: 0
