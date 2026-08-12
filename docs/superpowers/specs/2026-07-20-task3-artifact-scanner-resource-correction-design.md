# Task 3 artifact-scanner resource correction design

**Date:** 2026-07-20
**Status:** approved direction; written-spec review pending
**Task board:** `owner-center-task3-final-review-corrections-2026-07-20`

## Context

Owner-center Task 3 remains at target parent
`8376ed1fdca13001d2c5f1f1dd5bc452b596d04e` with exactly 17 routed WIP
paths and an empty index. The accepted Task 3 correction route is
`coordination/mailbox/sent/2026-07-20T10-09-22Z-coordinator-to-all-coordination.md@43fa4eb603025986cc01d4deb3e2997e51a84d2c`,
and the Director's effective autonomous continuation is
`coordination/mailbox/sent/2026-07-20T10-24-01Z-director-to-all-coordination.md@2cbb8d8ec2eb87c19b3d1a7bc3abf3714e0a7caa`.

Task 1 followed the approved RED/GREEN order. The three named regressions were
non-vacuously RED, and the corrected owner guard then passed 28/28. The real
`build:ci` gate nevertheless failed during `check:dist`: the Vite build
completed, but whole-bundle constant-root enumeration exhausted about 4.8 GB
of heap and aborted with exit 134. Tasks 2 through 4 did not start. The binding
blocker report is
`coordination/mailbox/sent/2026-07-20T10-36-43Z-director-to-coordinator-coordination.md@7543b34f10e80490f302d1085e16cd6c5019b0f7`.

The current two Task 1 correction files remain unstaged. The other nine
protected WIP paths and both closed files retain their accepted hashes. No
target commit, verify-request, Operator2 verdict, merge, or push exists.

## Root cause

The failure is not caused by the semantic-JWT classifier or by the size of a
legitimate reconstructed value. It is a tokenizer progress defect.

`scanSource` uses the TypeScript lexical scanner without parser context. A
parser normally decides when `/` begins a regular-expression literal and
invokes the scanner's slash rescan. The standalone lexical loop cannot make
that decision. A regular expression containing a backtick therefore causes
later backticks to be paired as template delimiters incorrectly. On the real
bundle, the scanner eventually reaches byte 356,573 and repeatedly emits a
zero-length `PrivateIdentifier` token at `#`. The token cursor never advances,
so the new whole-bundle root collection grows until Node exhausts the heap.

Increasing the heap, allowlisting the generated filename or byte offset,
assuming today's bundle layout, or merely converting the root array to a
generator would conceal the symptom without fixing tokenizer non-progress or
the security blind spot. Those responses are rejected.

## Approaches considered

### Selected: forward-only closed constant recognizer

Replace whole-input TypeScript tokenization for constant reconstruction with a
small recognizer for the already-approved closed constant grammar. The outer
cursor advances on every iteration, candidate parsing is memoized by input
offset, reconstructed values are streamed to their consumers, and an
over-budget construction fails closed. This preserves the intended
concatenation, template, and array-join coverage without a dependency or a
general JavaScript parser.

### Rejected: semantic-segment prefilter before the existing scanner

A prefilter for two directly decodable Base64URL object segments would make
the current bundle fast, but it would silently miss a segment assembled from
smaller constant fragments. It would also retain the scanner's parser-context
failure for source-wide computed-name checks.

### Rejected: add a JavaScript parser dependency

A full parser could provide context-correct regular-expression and template
tokenization, but it would add package, lockfile, integration, and maintenance
surface for a finite constant grammar already owned by the guard. The current
route forbids dependency and lockfile changes, and this correction does not
justify reopening that boundary.

## Selected architecture

### 1. One closed grammar, independent of whole-program tokenization

The correction provides one internal forward-only recognizer for these forms:

- single-quoted and double-quoted string literals;
- no-substitution template literals;
- parentheses around another closed expression;
- literal `+` concatenation;
- template literals whose substitutions are themselves closed expressions;
  and
- literal arrays whose elements are closed expressions followed by
  `.join()` with a closed constant separator.

The recognizer does not resolve identifiers, aliases, arbitrary calls,
property reads, control flow, data flow, or runtime values. It is not a
general JavaScript lexer or parser. A syntax form outside the closed grammar
does not produce a reconstructed value.

The recognizer attempts a candidate at every input position capable of
starting a closed expression. A failed attempt never moves the outer cursor
past later input. This matters when a quote or backtick belongs to a comment
or regular expression: a conservative false candidate may be inspected, but
it cannot desynchronize the rest of the source or hide a later real
construction.

Literal escape decoding must follow JavaScript string/template semantics for
the supported literal forms. Malformed or unterminated candidates produce no
value and cannot stall the outer cursor.

### 2. Explicit progress and resource invariants

Every outer recognition step consumes at least one UTF-16 code unit. Every
inner recognition result records an end offset strictly greater than its
start. Results are memoized by production and start offset so the same nested
expression is not reparsed for each parent candidate. The implementation uses
an explicit work stack rather than recursive call depth proportional to the
artifact. Its possible memo/work states are bounded by the fixed closed
productions multiplied by `source.length + 1`; exceeding that derived bound is
a hard guard failure.

Reconstructed values are yielded to the caller one at a time rather than
retained in a root array. The semantic-JWT consumer stops on the first match.
The finite-name consumer stops after it has established the applicable
forbidden name.

Before concatenating or joining, the recognizer checks the resulting length.
A value whose reconstruction would exceed the inspected source's input
length, or a nesting pattern that cannot be evaluated within the derived
recognizer-state bound, is a deterministic hard guard failure rather than an
allocation attempt or a silent safe result. This is a denial-of-service safety
boundary, not an allowlist: no credential-like value is accepted because it
is large.

No `NODE_OPTIONS` heap increase, generated-asset size exemption, timeout-based
pass, filename/hash/offset allowlist, or current-bundle occurrence count is
permitted.

### 3. Generated-artifact credential classification

The raw contiguous compact-JWT scan remains the first artifact check. Each
value produced by the closed recognizer is then passed to the same semantic
classifier already accepted for Task 3:

1. the first two segments must be canonical unpadded Base64URL;
2. both must decode through fatal UTF-8 as JSON; and
3. both decoded values must be non-null objects rather than arrays or scalar
   values.

The signature may be populated or empty. `e30.e30.c2ln` remains
credential-like. Contiguous, literal-concatenated, closed-template, and
literal-array-join forms must all fail closed. Ordinary dotted code,
malformed encodings, non-JSON values, and scalar/array JSON values remain
allowed by this classifier while all independent secret, private-key,
real-data-path, workbook, source-map, and operations-only prohibitions remain
active.

### 4. Source-wide finite-name safety

The same recognizer supplies constant-composed names to the existing finite
source-safety policy:

- `eval` and `Function` are forbidden in every production source;
- `fetch`, `XMLHttpRequest`, and `sendBeacon` are forbidden in every
  production source; and
- `rpc` is allowed only in the three exact reviewed API adapters.

Direct exact identifier spellings are checked with a forward-only identifier
boundary pass, not by tokenizing the whole source as JavaScript. Matching a
forbidden spelling conservatively inside an unusual lexical context may fail
closed; it may never cause the scan to skip subsequent input. Constant values
from the closed recognizer catch computed spellings such as
`"Fun" + "ction"` and `"r" + "pc"`.

The existing owner-adapter RPC inventory and import-edge checks remain
separate structural checks. Their scanner loop gains a deterministic
non-progress failure so malformed or context-desynchronized input cannot hang
or be represented as a successful audit. This correction does not broaden
their accepted grammar or add identifier/data-flow inference.

## Files and scope

The resource correction changes only the two already-authorized Task 1 files:

- `web/scripts/check-pwa-dist.mjs`;
- `web/src/api/owner-settings-api.test.ts`.

No new target path, package, lockfile, configuration, build flag, dependency,
framework, or generated fixture is permitted. The exact target remains the
same 17-path WIP at parent
`8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`. Tasks 2 through 4 resume only
after Task 1 satisfies its focused guard and real `build:ci` gate.

## Test contract

The implementation remains test-first and preserves the owner guard file's
exact 28-test count by extending existing cases rather than adding a new
Vitest case.

The Task 1 regression must prove:

- a regular-expression literal containing a backtick before a later constant
  construction neither hangs nor hides that construction;
- the real reconstructed `Function`, direct RPC/raw transport, concatenated
  JWT, closed-template JWT, literal-array-join JWT, populated-signature JWT,
  empty-signature JWT, and `e30.e30.c2ln` cases fail closed;
- a safe minified fixture with many literals and regex/template punctuation
  completes deterministically without a heap override;
- the two real command-runner property chains and every existing negative JWT
  fixture remain allowed;
- malformed and unterminated constant candidates cannot stall recognition;
  and
- every pre-existing source, import, RPC inventory, secret, private-key,
  real-data, workbook, source-map, and operations-only assertion retains its
  prior result.

After focused 28/28, Director must run `build:ci` with `NODE_OPTIONS` unset.
The actual 474.52 kB-class minified bundle must complete the distribution
check under Node's ordinary heap. Passing only a synthetic fixture is
insufficient.

The remaining corrected Task 3 plan then resumes its already-bound acceptance
contract: exactly 79/79 focused tests and 140/140 complete tests, typecheck,
`build:ci`, source/artifact audits, three frozen contract hashes, target smoke,
`git diff --check`, exactly 17 target paths, empty pre-commit index, protected
WIP hashes, and both closed-file hashes.

Two fresh final-byte reviews still inspect all 17 live paths and every binding
finding. Any unresolved Critical or Important finding, resource failure,
unexpected test-count change, ninth correction file, eighteenth target path,
or weakened credential/source policy causes another truthful stop.

## Failure and recovery behavior

The recognizer must distinguish three outcomes:

- no supported constant at an offset: advance and continue;
- a supported constant value: classify it and continue or fail on a policy
  match; and
- a resource/progress invariant violation: stop `check:dist` with a stable
  guard error.

An exception, malformed candidate, or budget violation cannot be converted to
"not a JWT" for the whole artifact. Existing malformed Base64URL/JSON
candidates may remain ordinary non-JWT strings only after the recognizer has
successfully produced their exact constant value.

## Completion and authority boundary

This design corrects only the Task 1 algorithm/resource blocker. It does not
alter the accepted resolutions for the pending-journal transaction,
same-actor retained retry, terminal retry classification, logout fence, or
the two included Minor findings. After a corrected plan and superseding route,
Director remains the sole implementation owner and must preserve one combined
target commit. Operator2 remains the only actual-range verdict issuer.

The user's selected tidy action remains a later local merge only after
Operator2 GO and a separate exact merge route. This design grants no merge,
push, target-main update, cursor consumption, lock action, service lifecycle,
managed database/Auth action, private-data access, policy activation, booking,
spend, deployment, cleanup, reset, rebase, or amend authority.
