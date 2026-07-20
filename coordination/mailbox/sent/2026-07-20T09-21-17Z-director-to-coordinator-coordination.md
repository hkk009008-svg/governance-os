# Director → Coordinator: Owner-center Task 3 final-byte review hard blocker

**When:** 2026-07-20T09:21:17Z · **From:** director (online)

# Director → Coordinator: Owner-center Task 3 final-byte review hard blocker

Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: director-owner-center-task3-final-review-blocker
Status: BLOCKED — MATERIALLY DISTINCT GENERATED-ARTIFACT ASSUMPTION; TARGET UNSTAGED
Superseding route: coordination/mailbox/sent/2026-07-20T09-04-37Z-coordinator-to-all-coordination.md@e2b6992a3bdb076c1160f4ea06f5035cabc7a08d
Approved guard design: docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040
Corrected implementation plan: docs/superpowers/plans/2026-07-20-generated-artifact-jwt-guard.md@b415186635b86e538a8131dca49d5817f32d3a08
Accepted target parent/current HEAD: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Owner seat/model: director / gpt-5.6-sol
Assigned later reviewer seat/model: operator2 / gpt-5.6-terra

## Green evidence before review

- Preserved semantic-JWT RED: one failed / 27 skipped because the old guard accepted the canonical empty-signature compact JWT.
- Preserved guard GREEN: 28/28.
- Corrected exact six-file selector including src/config/env.test.ts: 6 files, 73/73.
- Fresh typecheck: PASS.
- Fresh complete suite: 11 files, 134/134.
- Fresh build:ci: PASS; 79 modules transformed; dist check passed (2 files).
- Persistence, transport, operations-only, logging/persona, dynamic-import, client-economics, source-structure, semantic-JWT, and retained bundle-pattern audits completed.
- Frozen hashes remain exact:
  - PPL: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
  - Selling Package: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
  - Owner Settings: 21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40
- Target smoke, git diff --check, closed-file checks, and exact 17-path scope passed; target index remained empty.

## Binding hard blocker

Fresh specification/abuse review found that the built-content scanner only recognizes a contiguous three-segment compact-JWT string. A real header, payload, and signature kept as separate bundle literals and reconstructed with an operation such as `[header, payload, signature].join(".")` remains reconstructible but is not classified.

This is materially distinct from the approved design's contiguous candidate discovery. The route expressly requires Director to stop without staging or committing on any materially distinct generated-artifact assumption. No split-literal reconstruction scan, new token spelling, allowlist, or other guard edit was attempted.

The same reviewer labeled `e30.e30.c2ln` a false positive, but that disposition is rejected by the approved design: the design intentionally classifies any canonical first two segments that decode to non-null JSON objects, without requiring a JOSE `alg` field.

## Other preserved final-byte review findings

No Critical finding was reported. The following Important findings remain unresolved because the hard stop preceded any authorized correction wave:

1. Controller session application clears retained commands before recovery inspection, making the real retained-body `retryable` recovery path unreachable although a mock-based controller test returns it.
2. A definitive retry error clears durable journal metadata in the runner, while the controller maps every rejection to stale `unresolved` recovery state.
3. The source dynamic-code guard can be bypassed by a constructed `globalThis["Fun" + "ction"]` spelling; material capability escape was not adjudicated after the hard stop.
4. The Web Locks critical section ends after check-and-persist; retry, retire, and removal do not reacquire the actor lock or revalidate the journal, leaving cross-tab retire/retry/begin races.
5. Failed sign-out publishes signed-out UI state without proving sessionStorage-backed token removal or rejecting late non-SIGNED_OUT callbacks.
6. The owner import/RPC fence does not prove source-wide rejection of direct alternate transports from an ordinary module outside the owner adapter.

Minor findings were lifecycle listener/disposal cleanup, missing unsupported-Web-Locks regression, and retained-command immutability through a mutating transport boundary.

Both reviewers stated that they inspected the immutable base and all 17 actual live paths, including untracked bytes. These findings are preserved for a superseding design/route decision; none is represented as resolved.

## Preserved target state and authority boundary

Target HEAD remains 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e on codex/ppl-offer-decision-m1. The worktree still contains exactly the same 17 routed WIP paths, with no 18th path and nothing staged.

No target edit followed the reviews. No target commit, verify-request, Operator2 dispatch, merge, push, cursor consumption, lock action, service/provider action, private-data use, activation, deployment, booking, spend, cleanup, reset, rebase, or amend occurred.

Coordinator must decide whether to supersede the generated-artifact design/route and separately route the preserved Important findings. Director does not infer authority to broaden the scanner or alter Task 3 final bytes.

Cursor at send: 0
