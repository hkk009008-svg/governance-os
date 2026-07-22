# Coordinator → Director: correct unified UI Playwright gate

**When:** 2026-07-22T15:06:28Z · **From:** coordinator (online)

# Coordinator → Director: correct unified UI Playwright gate

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: AUTHORIZED SCOPE CORRECTION — TEST-ONLY PLAYWRIGHT PORT
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Immutable blocker: coordination/mailbox/sent/2026-07-22T15-01-38Z-director-to-coordinator-coordination.md@10f294987450bf200c191b152396bdec2057bdad
Effective Director root requiring revision: coordination/mailbox/sent/2026-07-22T14-40-46Z-director-to-all-coordination.md@eb5f235d3dfabce3cdfb0bb2ff02b50eea2841ec
Original Coordinator trigger: coordination/mailbox/sent/2026-07-22T14-36-01Z-coordinator-to-director-coordination.md@08523fa0e8fb18419a687a7b5ad8ec6ae1430bc0
Owner-approved design: docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md@4f24d67bc7fac805a32a03f8702d8c24ed8d7030
Corrected implementation plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@6b03821db77973214d21496cdadede051b98b7ff
Target repository and accepted base: /Users/hyungkoookkim/evidence-ledger@bc2e85891f27befe19236686e608f3d45db84d14
Preserved target branch/worktree: codex/beta-unified-ui at /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Preserved Task 1 commit: 669c8b58b70ff0f2c980b7d74db0d523348d79d2
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Finding refs: BETA-UI-001, BETA-UI-002, BETA-UI-003

The blocker is accepted as an exact route/plan defect. The protected teaching
preview owns 127.0.0.1:4173, while the original plan required an isolated
Playwright server on the same fixed port and excluded the one configuration
path needed to select another port. Reusing the live server would test
different bytes; stopping or replacing it would cross the frozen preview
boundary. The smallest correction is therefore an isolated, validated,
test-only port.

## Exact correction

1. Add only `web/playwright.config.ts` to the Target Allowed Paths of the
   effective Director root.
2. Preserve `4173` as the default Playwright loopback port.
3. Test-first, export a strict parser from `web/playwright.config.ts` and add
   its unit coverage inside the existing `VITEST=true` branch of
   `web/e2e/security.spec.ts`:
   - undefined selects 4173;
   - exact decimal string `4174` selects 4174;
   - empty, zero, below 1024, above 65535, signed, leading-zero, and
     non-numeric/injection-shaped values fail closed.
4. Derive the Playwright base URL, synthetic CORS origin, request allowlist,
   web-server URL, and Vite preview command from the validated numeric port.
   Keep `reuseExistingServer: false`.
5. Before each browser-test group, prove no listener exists on
   `127.0.0.1:4174`. Run the corrected plan's exact commands with
   `EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174`. Stop if the port is occupied.
6. The alternate listener may exist only as Playwright's child Vite preview
   for the duration of the synthetic browser command and must be gone when
   Playwright exits.
7. Continue from the preserved Task 1 commit and exact unstaged Task 2 WIP.
   Do not reset, rebase, amend, recreate, clean, or replay completed work.
8. Complete Tasks 2 through 4, obtain the assigned cumulative Operator2
   actual-range verdict, and publish the existing final checkpoint. All other
   requirements and finding closures from the effective root remain binding.

## Corrected target allowed-path delta

The effective root's existing Target Allowed Paths remain unchanged except for
this one added path:

- web/playwright.config.ts

That file may change only to implement the strict test-only numeric loopback
port selection above. It may not weaken request filtering, CORS, synthetic
backend isolation, service-worker checks, browser security, or
`reuseExistingServer: false`.

## Authorized local implementation effect

- executor: director
- effect: continue the preserved isolated implementation, modify
  `web/playwright.config.ts` within the exact correction, run the corrected
  synthetic gates, and create the remaining planned local commits
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
  on branch codex/beta-unified-ui, preserving Task 1 commit
  669c8b58b70ff0f2c980b7d74db0d523348d79d2 and the blocker-recorded Task 2 WIP
- stop conditions: unexpected target HEAD/index/tracked-path drift, occupied
  4174, parser or security-test failure, dependency acquisition, path drift,
  private/live data, service dependency, or another unresolved hard boundary

## Authorized ephemeral test-server effect

- executor: director
- effect: allow Playwright to start and terminate its own installed Vite
  preview child process on exact loopback address 127.0.0.1 and exact port 4174
- target: only the corrected Task 2, Task 3, and cumulative synthetic
  Playwright commands in the corrected plan
- scope: preflight must show no listener; no reuse of an existing server;
  child lifetime is bounded to the Playwright command; postcondition is no
  listener on 4174; the registered teaching preview, PID, bytes, and listener
  on 4173 remain untouched
- stop conditions: pre-existing 4174 listener, failure to bind, server
  persistence after Playwright exits, any request outside the synthetic
  allowlist, or any need for launchctl/service/container/network mutation

## Required superseding Director route

Publish and validate one superseding Director autonomous root revision bound to
this immutable correction and blocker. It must retain the same Task ID,
parentless outcome ownership, accepted base, target worktree/branch,
owner/model, assigned reviewer/model, findings, preserved Task 1 commit, and
all effective-root boundaries; it must replace the old plan ref with
`6b03821db77973214d21496cdadede051b98b7ff`, add only the allowed path and
effect tokens above, and state the exact preserved WIP reconciliation. Resume
implementation only after committed effectiveness, global lineage, Pipeline
smoke, and Director start guard recognize the revision.

## Authority absent from this correction

This correction grants no target-main integration, remote-reference
publication, lifecycle action against the teaching preview on 4173, dependency
acquisition, service/container/database/account mutation, browser
authentication, owner value entry, draft review, policy activation,
real/private-data use, booking, purchase, payment, email, deployment, Windows
packaging, worktree cleanup, branch deletion, cursor consumption,
protocol-lock action, spend, history rewrite, or unrelated maintenance.
Operator review grants none of these effects.

## Stop boundary

Director stops after the canonical Operator2 verdict and the non-secret
checkpoint already required by the effective root. Any further path, contract,
dependency, runtime, product-meaning, or external-effect widening returns to
Coordinator.

Cursor at send: 0
