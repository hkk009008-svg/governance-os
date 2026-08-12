# Generated-artifact JWT guard design

**Date:** 2026-07-20
**Status:** approved design, pending implementation route
**Task board:** `ledger-one-user-owner-center-2026-07-20`

## Context

Owner-center Task 3 is preserved at target parent
`8376ed1fdca13001d2c5f1f1dd5bc452b596d04e` with exactly 17 routed paths and
nothing staged. Its focused tests pass 72/72, the full suite passes 133/133,
and typecheck passes. The build reaches `check:dist`, where the current
JWT-shaped regular expression falsely classifies these ordinary minified
property chains as credentials:

- `dependencies.commandRunner.retryConfirmedAbsent`
- `dependencies.commandRunner.retireConfirmedAbsent`

The immutable blocker report is
`coordination/mailbox/sent/2026-07-20T08-28-48Z-director-to-coordinator-coordination.md@cf210120b7b544829ec4ece7e63f87980b4f2e31`.

## Decision

Generated artifacts will continue to be checked for embedded JWTs, but a
three-segment dotted string is only a candidate. The guard will classify a
candidate as a JWT only when:

1. the first two segments are canonical unpadded Base64URL values whose decoded
   bytes re-encode to the same segment;
2. both segments decode successfully as UTF-8 JSON; and
3. both decoded values are non-null JSON objects rather than arrays or scalar
   values.

The signature segment may be populated or empty so an unsecured compact JWT
cannot evade the guard. A semantic JWT match remains a hard failure.

This is credential-format validation, not signature verification. The guard's
purpose is to prove that no JWT credential is embedded in the generated
artifact, not to establish whether a token is trusted.

## Boundary

Generated-output checks retain responsibility for content that can be
meaningfully identified after bundling:

- semantic compact JWTs;
- `sb_secret_` credentials;
- private-key banners;
- real-data paths and `.xlsx` references;
- source maps; and
- operations-only RPC names.

Application-behavior restrictions remain structural source checks. In
particular, raw-HTML use, owner-adapter import edges, persistence/network sinks,
dynamic code, and literal RPC inventories are not inferred from arbitrary
minified substrings.

No generated filename, hash, byte offset, property name, occurrence count,
React version, or current bundle is allowlisted.

## Implementation scope

The correction may edit only the two already-routed target files:

- `web/scripts/check-pwa-dist.mjs`
- `web/src/api/owner-settings-api.test.ts`

It adds no dependency and opens no new target path. The existing 17-path Task
3 WIP remains preserved. The smallest testable semantic-JWT helper may be
exported from the guard module.

## Test contract

Before implementation, the existing guard test records a non-vacuous RED that
proves:

- the two observed property chains are allowed;
- ordinary long dotted identifiers are allowed;
- realistic signed JWT compact serialization is rejected;
- a compact JWT with an empty signature is rejected;
- invalid Base64URL, non-JSON, scalar JSON, and array JSON candidates are not
  classified as JWTs; and
- the existing secret-prefix, private-key, real-data-path, and workbook
  prohibitions still fail closed.

After the focused guard turns green, Director reruns every Task 3 focused and
full gate, typecheck, `build:ci`, source and bundle scans, frozen contract
hashes, target smoke, `git diff --check`, and the exact allowed-path audit.
Both independent final-byte reviews are then repeated. All Critical and
Important findings must be resolved before the single authorized local target
commit and immutable Operator2 verify-request.

## Failure handling

Malformed candidate decoding is treated as “not a JWT” and does not suppress
the other generated-content checks. Any real semantic JWT, retained secret or
private-data pattern, new target path, or failing Task 3 gate stops the route.
Operator2 remains the only seat that may issue the actual-range verdict.

## Exclusions

This design does not authorize dependency changes, service lifecycle, managed
database or Auth work, real/private values, policy activation, booking, spend,
merge, push, deployment, cursor consumption, lock actions, cleanup, reset,
rebase, amend, or Task 4 UI work.
