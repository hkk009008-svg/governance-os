# Coordinator → Director: correct cumulative PWA browser gate

**When:** 2026-07-22T16:43:47Z · **From:** coordinator (online)

# Coordinator → Director: correct cumulative PWA browser gate

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: AUTHORIZED SCOPE CORRECTION — ONE TEST-ONLY PWA PATH
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Immutable blocker: coordination/mailbox/sent/2026-07-22T16-30-59Z-director-to-coordinator-coordination.md@cf31fe01398e16bfab0d68a4c7ba8ea5b66ecefd
Effective Director root requiring revision: coordination/mailbox/sent/2026-07-22T15-12-00Z-director-to-all-coordination.md@27621835c7b00ee1548a754dc3c5c6d783a519f9
Prior Coordinator correction: coordination/mailbox/sent/2026-07-22T15-06-28Z-coordinator-to-director-coordination.md@cc892efffcf2c02fd1acff194a11339cd6f1b888
Owner-approved design: docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md@4f24d67bc7fac805a32a03f8702d8c24ed8d7030
Corrected implementation plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@bfbda930279e70d8103f60bf1efa63950ce8be8c
Target repository and accepted base: /Users/hyungkoookkim/evidence-ledger@bc2e85891f27befe19236686e608f3d45db84d14
Preserved target branch/worktree: codex/beta-unified-ui at /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Preserved target HEAD: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Finding refs: BETA-UI-001, BETA-UI-002, BETA-UI-003

The blocker is accepted as a stale cumulative test-contract defect, not a
product-code defect. Fresh cumulative evidence is non-vacuous: 13 Playwright
nodes passed and exactly four PWA nodes failed. The approved all-fields editor
removed the old button label, and the protected teaching preview requires the
already-validated temporary 4174 origin. Production aliases, duplicate hidden
controls, server reuse, or a 4173 lifecycle action would weaken the accepted
contract.

The blocker text undercounted one origin use. The target test contains exactly
three hardcoded 4173 bindings: registration scope, service-worker script URL
expectation, and CDP restart scopeURL. All three must follow the validated
LOOPBACK_ORIGIN.

## Exact correction

1. Add only `web/e2e/pwa.spec.ts` to the Target Allowed Paths.
2. Import the already-validated `LOOPBACK_ORIGIN` from
   `../playwright.config`.
3. Replace all three hardcoded `http://127.0.0.1:4173/` bindings with exact
   values derived from `LOOPBACK_ORIGIN`.
4. Replace exactly three stale `저장하고 다음` button locators with
   `초안 저장`.
5. Preserve every PWA installability, static-cache, offline, waiting-worker,
   in-flight-command, multi-client, browser-native activation, and unexpected
   traffic assertion.
6. Run the focused PWA file on the temporary 4174 token, prove the listener is
   absent before and after, and create exactly one test-only commit with
   subject `test(web): align PWA gate with unified UI`.
7. Resume corrected-plan Task 4 from the cumulative gate, create the factual
   docs commit, request cumulative Operator2 review, reconcile the verdict,
   publish the non-secret checkpoint, and stop at the existing boundary.

## Corrected target allowed-path delta

The effective root's existing Target Allowed Paths remain unchanged except for:

- web/e2e/pwa.spec.ts

That path may change only for the six exact stale bindings above. It may not
weaken, skip, quarantine, extend timeouts for, or delete PWA assertions.

## Authorized local test correction effect

- executor: director
- effect: modify the one test path, run the focused PWA gate and corrected
  cumulative gates, create the exact test-only commit and later factual docs
  commit
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
  on branch codex/beta-unified-ui at preserved HEAD
  6b817bdc27acdecea5dce8832cd1b4a3daceed5c
- preserved commits: 669c8b58b70ff0f2c980b7d74db0d523348d79d2,
  940744b30e1c2878574a85fec236210ad67a1845, and
  6b817bdc27acdecea5dce8832cd1b4a3daceed5c
- stop conditions: unexpected HEAD/index/tracked-path drift, any changed path
  other than the exact test then factual docs, occupied or persistent 4174,
  changed PWA behavior, product-code change, dependency acquisition, or
  another unresolved hard boundary

The existing ephemeral test-server token remains effective without expansion:
Playwright may start its installed Vite child only on 127.0.0.1:4174 for the
focused and cumulative synthetic browser commands, with no pre-existing
listener and no listener afterward. The registered teaching preview, PID,
bytes, and listener on 127.0.0.1:4173 remain untouched.

## Required superseding Director route

Publish and validate one superseding Director autonomous-root revision bound to
this immutable correction and blocker. Retain the same Task ID, parentless
outcome lineage, accepted base, worktree/branch, owner/model, assigned
reviewer/model, findings, three target commits, and every existing boundary.
Replace the plan ref with
`bfbda930279e70d8103f60bf1efa63950ce8be8c`, add only the allowed path and
local effect above, and bind the exact 13-pass/4-fail RED evidence. Resume only
after committed effectiveness, global lineage, Pipeline smoke, and Director
start guard recognize the revision.

## Authority absent from this correction

Authority remains absent for target-main integration, remote-reference
publication, lifecycle action against the teaching preview on 4173,
dependency acquisition, service/container/database/account mutation, browser
authentication, owner value entry, draft review, policy activation,
real/private-data use, booking, purchase, payment, email, deployment, Windows
packaging, worktree cleanup, branch deletion, cursor consumption,
protocol-lock action, spend, history rewrite, or unrelated maintenance.
Operator review grants none of these effects.

## Stop boundary

Director stops after the canonical Operator2 verdict and the non-secret
checkpoint required by the effective root. Any further path, contract,
dependency, runtime, product-meaning, or external-effect widening returns to
Coordinator.

Cursor at send: 0
