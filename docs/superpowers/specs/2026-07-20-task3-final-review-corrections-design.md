# Owner-center Task 3 final-review corrections design

**Date:** 2026-07-20
**Status:** approved direction; written-spec review pending
**Task board:** `ledger-one-user-owner-center-2026-07-20`

## Context

Owner-center Task 3 remains at target parent
`8376ed1fdca13001d2c5f1f1dd5bc452b596d04e` with exactly 17 routed paths,
an empty index, and no target commit. The corrected focused gate passed 73/73,
the complete suite passed 134/134, and typecheck, build, artifact checks,
contract hashes, scope checks, and repository smoke all passed.

The two independent final-byte reviews nevertheless found one materially
distinct generated-artifact assumption and six other Important defects. The
binding report is
`coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d`.
It supersedes green test counts as acceptance evidence: the current bytes are
preserved but are not eligible for a target commit, Operator2 review, merge,
or push.

## Review evaluation

The findings were checked against the live 17-path WIP and the pinned
Supabase Auth 2.110.7 source rather than accepted mechanically.

Accepted Important findings:

1. A compact JWT reconstructed from closed constant expressions, including an
   array of literal segments joined with `"."`, evades the raw contiguous
   artifact scan.
2. `AppController.applySession` clears the retained command before recovery,
   so the real same-page `retryable` path is unreachable even though a mock
   controller test returns it.
3. A definitive retry rejection clears the journal in the runner, while the
   controller maps every rejection to stale `unresolved` state.
4. A dynamically constructed sink such as
   `globalThis["Fun" + "ction"]` evades exact-token dynamic-code checks.
5. The Web Locks boundary covers only compare-and-persist. Retry, retirement,
   clear, and server reconciliation can race between tabs because they do not
   share one actor-scoped transaction.
6. The controller publishes signed-out state before proving the
   Session-Storage-backed Supabase session is absent and accepts late
   non-`SIGNED_OUT` callbacks during logout.
7. An ordinary source module can bypass the owner adapter by using a direct
   RPC or raw transport without importing the named owner adapter.

Two Minor findings are included because they close the same invariants with
small focused tests:

- a transport must not be able to mutate the retained command later retried
  under the same request UUID; and
- lack of Web Locks support must be explicitly proven to reject before
  persistence or transport.

The lifecycle-listener/disposal Minor is not included. The production entry
point has no remount path, while disposing on `pagehide` would conflict with
the existing back-forward-cache `pageshow` recovery path. It remains recorded
for final review and becomes blocking only if a reviewer demonstrates a
production lifecycle that reproduces stale or duplicate controllers.

The review suggestion that `e30.e30.c2ln` is necessarily a false positive is
rejected. The previously approved guard intentionally treats canonical
Base64URL object/object compact serialization as credential-like even without
a JOSE `alg` member. This is a generated-secret prohibition, not standards
validation, and the correction must not weaken it.

## Approaches considered

### Selected: bounded closure using existing primitives

Reuse the guard's existing constant-string evaluator, replace the journal's
partial lock usage with one actor-scoped transaction primitive, and correct
controller state transitions. This closes every Important finding within the
existing 17 paths and adds no dependency or framework.

### Rejected: fix only the artifact blocker and defer runtime findings

Strict regression pins could preserve the six runtime findings, but the
current Task 3 acceptance contract requires every Critical and Important
finding to be resolved before commit. This approach would remain ineligible
for Operator2 GO and merge.

### Rejected: add a general JavaScript or inter-tab orchestration framework

A full AST/data-flow analyzer, a new event-sourcing layer, or a new locking
library would introduce substantially more behavior than these findings need.
The correction covers explicit, closed abuse classes and the existing browser
state model only.

## Selected architecture

### 1. Generated-artifact semantic credential scan

The raw contiguous compact-JWT scan remains. In addition, built JavaScript is
tokenized with the already-present TypeScript scanner. The guard evaluates
only closed constant-string expressions already supported by the source
guard:

- string and no-substitution template literals;
- parentheses;
- literal `+` concatenation;
- templates whose substitutions are themselves closed constant strings; and
- literal arrays using `.join()` with a closed constant separator.

Each reconstructed string is passed to the same canonical Base64URL, fatal
UTF-8, non-null JSON-object/object classifier. A populated or empty signature
continues to fail closed. Identifier resolution, alias tracking, arbitrary
calls, control flow, general data flow, bundle-specific allowlists, and new
parser dependencies remain out of scope.

Required positives include contiguous, `+`, template, and array-join forms.
Required negatives retain the two real command-runner property chains,
malformed encodings, non-JSON values, scalar/array JSON values, and ordinary
dotted code. All existing `sb_secret_`, private-key, real-data-path, `.xlsx`,
source-map, and operations-only checks remain independent and active.

### 2. Source-wide code and transport fences

The existing closed constant-string evaluator also resolves computed property
names for the finite forbidden names `eval`, `Function`, and `rpc`. All
production source files fail on direct or constant-composed dynamic-code
sinks. Direct raw transport primitives (`fetch`, `XMLHttpRequest`, and
`sendBeacon`) are forbidden in production application source.

Literal or constant-composed RPC invocation is permitted only in the three
reviewed API adapters:

- `web/src/api/ppl-api.ts`;
- `web/src/api/selling-package-api.ts`; and
- `web/src/api/owner-settings-api.ts`.

The existing exact owner RPC inventory and sole composition-root import in
`web/src/main.tsx` remain mandatory. This is a structural source fence for the
current application, not a claim to solve arbitrary malicious JavaScript.

### 3. Actor-scoped pending-command transaction

`PendingJournal` exposes one asynchronous actor-scoped transaction method.
The Web Lock is acquired before reading or changing that actor's pending
metadata and remains held until the callback finishes. The transaction offers
only exact operations to read the current metadata, begin when empty, and
remove a matching request UUID.

Every state-changing command path uses that transaction:

1. initial execution checks empty, persists metadata, retains the canonical
   in-memory command, sends, and classifies the result while holding the actor
   lock;
2. recovery re-reads the exact metadata, queries the matching result, and
   clears or records the local recovery disposition under the same lock;
3. retry revalidates both journal UUID and retained body, sends a fresh clone,
   and clears only on success or definitive rejection under the same lock; and
4. retirement revalidates the exact body-lost journal entry and Korean
   confirmation before removing it under the same lock.

The runner must not reacquire the same lock from inside a transaction. Journal
mutation is performed through the current transaction object. If Web Locks
are unavailable, acquisition fails before storage mutation or network
transport. Read-only display may inspect actor-scoped metadata outside a
transaction, but it grants no mutation authority.

The retained command is a canonical structured clone. Each transport attempt
receives a new structured clone, so adapter mutation cannot change later
retry bytes under the original request UUID.

### 4. Recovery and session state transitions

Sensitive business/owner DTO clearing and retained-command clearing become
separate controller operations.

- Sensitive DTOs clear before every authentication or availability
  transition.
- Retained commands clear on actual sign-out, actor change, offline or
  transport loss, authentication failure, and controller disposal.
- Retained commands survive only a same-actor, same-page session application
  or recovery revalidation, allowing a real confirmed-absent command to
  become `retryable`.
- A new page process has no retained body; persisted metadata therefore still
  becomes `body_lost` and still requires the fixed two-step Korean retirement.

`retryConfirmedAbsent` returns a terminal disposition for both successful
application and definitive expected rejection. Both terminal outcomes clear
the exact journal entry and cause capability/session revalidation.
`unresolved` is reserved for an ambiguous outcome whose exact journal entry
still exists. The controller must never display recovery for metadata that the
runner has already removed.

### 5. Logout proof and callback fence

Logout immediately clears sensitive and retained in-memory state, disables
all mutation, advances the authentication epoch, and enables a logout fence.
While fenced, non-`SIGNED_OUT` authentication callbacks cannot apply a
session.

The controller then calls Supabase local sign-out and performs a fresh
`getSession` read. Supabase Auth 2.110.7 reads the configured storage key in
`getSession`; therefore `error === null` and `session === null`, or an actual
`SIGNED_OUT` callback emitted after `_removeSession`, is the required local
absence proof.

Only that proof publishes normal signed-out state. If sign-out or the proof
read leaves a session, returns an error, or throws, the controller remains in
a fixed Korean unavailable state with mutation disabled and the logout fence
intact. A later callback cannot silently restore the old session. An explicit
new password login starts a new authentication epoch and is the only in-page
action that may lower the fence.

## Files and scope

No new target path opens. Corrections remain inside the existing 17-path Task
3 write set. The expected correction files are:

- `web/scripts/check-pwa-dist.mjs`;
- `web/src/api/owner-settings-api.test.ts`;
- `web/src/app/AppController.ts`;
- `web/src/app/AppController.test.ts`;
- `web/src/features/recovery/command-runner.ts`;
- `web/src/features/recovery/command-runner.test.ts`;
- `web/src/features/recovery/pending-journal.ts`;
- `web/src/features/recovery/pending-journal.test.ts`.

The remaining routed files are preserved as part of the combined Task 3 range
but do not change merely to satisfy a path count. No new edit to
`web/src/main.tsx` is planned by this correction. `web/src/config/env.test.ts`
remains read-only verification input, and `web/src/test/synthetic-wire.ts`
remains closed and unchanged. A correction that requires another target path
or a new `main.tsx` behavior change stops for a revised design and route.

## Test and review contract

Each accepted finding receives a focused non-vacuous failing regression before
its implementation changes. The implementation proceeds finding by finding;
the branch retains one combined target commit only after every gate is green.

Focused acceptance must prove:

- semantic JWT rejection for contiguous, concatenated, templated, and joined
  constant forms, including an empty signature;
- preservation of credential-like object/object classification and every
  non-JWT artifact prohibition;
- rejection of direct and constant-composed dynamic-code/RPC bypasses and raw
  alternate transports from ordinary source;
- real-controller same-actor recovery reaches `retryable`, while actor change
  and terminal transitions destroy the retained body;
- definitive retry rejection clears recovery state, while ambiguous retry
  keeps the exact pending record and becomes `unresolved`;
- execute/recover/retry/retire/begin races serialize under one actor lock and
  cannot admit a replacement UUID while an old mutation is active;
- unsupported Web Locks reject before persistence and transport;
- transport mutation does not alter the retained retry command;
- failed or indeterminate logout never exposes normal signed-out state, and a
  late session callback cannot lower the logout fence; and
- storage-backed session absence or `SIGNED_OUT` permits normal signed-out
  state and later explicit login.

The implementation plan must enumerate every added or replaced test and bind
the resulting exact focused-test count before execution. The superseding route
must repeat that count, and any runtime mismatch is a stop condition. After
focused GREEN, Director also reruns typecheck, the complete suite, `build:ci`,
all source and artifact abuse scans, frozen contract hashes, target smoke,
`git diff --check`, exact 17-path scope, empty pre-commit index, and closed-file
checks.

Two fresh independent final-byte reviews must inspect all 17 live paths. Every
Critical and Important finding is resolved test-first or causes another
truthful stop. Minor findings receive explicit dispositions. Only then may
Director create the one local combined target commit and canonical immutable
verify-request assigned to Operator2.

## Completion and integration boundary

Operator2 remains the only seat that may issue GO, NITS, or FAIL on the actual
target range. User authorization selects a local merge as the later tidy
action, but it becomes executable only through a separate exact route binding
the verified source SHA, destination branch, executor, and clean-state checks.
No push is selected.

This design authorizes no dependency change, service or managed Auth action,
real/private value, policy activation, booking, spend, deployment, cursor
consumption, protocol lock action, cleanup, reset, rebase, amend, target-main
update, merge, or push by itself.
