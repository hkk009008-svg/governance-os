# Opus Lane V Receipt And Report Hardening Design

**Date:** 2026-07-13
**Status:** Approved for implementation by the user-principal on 2026-07-13;
independently challenged before approval
**Implementation base:** `555041477bcdb9a432a1b238d664be0958c5c9ef`
**Supersedes:** the caller-supplied reconciliation and prompt-only invocation
enforcement portions of the 2026-07-12 Opus designs. Their sandbox, authority,
blindness, model-identity, and reconciliation-severity rules remain in force.

## 1. Problem

Pipeline's current Opus bridge performs a carefully bounded provider call, but
the end-to-end Lane V guarantee remains forgeable and omissible:

1. `reconcile` accepts a caller-provided `--opus-review-json` document. A caller
   can construct an `unavailable` result for the expected commits and obtain a
   degraded `go_allowed=true` result without invoking `review`.
2. The bridge validates caller-declared allowed paths but does not prove that
   they cover every path changed by the reviewed range.
3. Reconciliation binds HEAD and base but not the requirements, allowed paths,
   verification commands, review profile, or authorization identity supplied
   to the provider.
4. The bridge limits one provider process per Python invocation, but distinct
   invocations can repeat the same unchanged Lane V attempt.
5. The GO-report gate does not require the cross-model fields already mandated
   by the Codex verifier and operator prompts. A report can omit the bridge and
   still pass `scripts/check_go_schema.py`.
6. Provider stdout and stderr are not size-bounded, and an early broker socket
   failure can escape constructor cleanup.
7. This managed Codex sandbox prohibits the macOS Seatbelt and AF_UNIX
   operations used by the full bridge integration suite. Pure contract tests
   pass here, but environment-dependent tests currently fail or error instead
   of reporting an explicit capability boundary.

The result is partial utilization: real calls use the intended verdict-blind
position and degraded semantics, but committed evidence cannot prove that the
required attempt happened, and `reconcile` can manufacture the same final
shape without it.

## 2. Evidence And Constraints

The 2026-07-13 audit established the baseline with these fresh commands:

```text
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ OK

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
    tests/unit/test_protocol_prompt_sync.py \
    tests/unit/test_check_go_schema.py -q
→ 64 passed

$ /usr/bin/sandbox-exec -p '(version 1) (allow default)' /usr/bin/true
→ sandbox_apply: Operation not permitted
```

The isolated design worktree repeated the project smoke and the 64-test focused
baseline at the implementation base before this specification was written.

The design must preserve these existing contracts:

- Opus runs after Codex has completed its independent Lane V analysis and
  before the final verdict, without receiving that provisional verdict.
- Opus is advisory. The operator alone issues `GO`, `NITS`, or `FAIL`.
- One unchanged Codex Lane V receives no automatic retry or substitute
  provider. A changed reviewed HEAD is a new verification, not a retry.
- `process_failed` and other genuine provider/environment failures remain
  visible degraded paths; they do not silently become a successful Opus pass.
- The standing authorization is limited to the exact Pipeline
  `codex-lane-v` profile and one bounded provider attempt.
- Raw prompts and raw provider streams do not enter Git, mailbox artifacts, or
  persistent logs.
- Historical mailbox reports remain readable without a mass rewrite.

## 3. Goals

1. Make a bridge-issued, state-backed receipt the only input to reconciliation.
2. Reserve one provider attempt before launch for each authoritative Lane V
   task and unchanged reviewed commit range in the shared runtime.
3. Bind the receipt to the entire immutable review scope, not only HEAD/base.
4. Prove that caller-declared allowed paths cover every changed path, including
   deletes and both sides of renames.
5. Make identical review and reconciliation requests idempotent while rejecting
   changed replay.
6. Validate new verification reports at their actual mailbox write boundary.
7. Preserve historical reports through an exact content-hash baseline rather
   than a date cutoff or permissive legacy parser.
8. Bound provider output and clean every partially constructed resource.
9. Separate pure contract tests from unavailable Seatbelt/socket integration
   capabilities without weakening production fail-closed behavior.
10. Preserve the current seat, mailbox, lock, commit, push, and final-verdict
    authority model.

## 4. Non-goals And Trust Boundary

This design does not attempt to:

- defend against the repository owner, root, or another process with the same
  filesystem identity deliberately editing both runtime state and reports;
- turn a local HMAC key into false cross-model or cross-principal assurance;
- make an untracked receipt a durable protocol authority source;
- commit raw Opus prompts, raw responses, stdout, or stderr;
- retry a failed, timed-out, interrupted, or uncertain provider attempt;
- generalize the bridge outside Pipeline or add another review profile;
- make hooks authoritative, because Codex hooks are advisory and bypassable;
- change the rule that a valid unavailable result may preserve a visibly
  degraded Codex verdict; or
- add a third generic reviewer for the same unchanged scope.

The receipt protects the normal Pipeline workflow against omission, accidental
replay, caller-supplied result fabrication, concurrent duplicate launch, and
scope substitution. It is executable local evidence, not a cryptographic
attestation from an independent principal. The committed report is an auditable
summary; the private receipt is the live emission guard.

## 5. Alternatives Considered

### 5.1 Keep caller JSON and add an HMAC

Rejected. A key readable by the same local user who can invoke the CLI and edit
the state file does not establish a meaningful new principal. It adds key
lifecycle and rotation complexity while encouraging an overclaim of security.

### 5.2 Combine review and reconciliation into one long-running process

Rejected. Codex must inspect findings and gather evidence-backed dispositions
between the independent review and final reconciliation. Holding a process or
socket open across that human/model reasoning interval is fragile and does not
fit the existing CLI workflow.

### 5.3 Use a private, state-backed receipt lifecycle

Chosen. The bridge reserves the attempt before provider launch, persists only
the normalized result, and later reconciles by receipt ID. This creates the
needed lifecycle and replay checks without claiming a stronger principal than
the local runtime provides.

## 6. Architecture

### 6.1 Components

The implementation introduces a focused stdlib-only receipt module rather than
expanding the already large provider bridge further:

- `scripts/opus_review_receipts.py`
  - canonical scope and reconciliation serialization;
  - attempt-key and scope-digest computation;
  - private receipt directory validation;
  - exclusive reservation, atomic transitions, lookup, and replay rules;
  - no provider, prompt, mailbox, or verdict policy.
- `scripts/opus_review_bridge.py`
  - computes and validates immutable review inputs;
  - uses the receipt store before and after the existing one-shot provider run;
  - removes caller-supplied review JSON from `reconcile`;
  - emits normalized receipt and reconciliation metadata;
  - bounds provider output and closes partial resources.
- `scripts/check_go_schema.py`
  - retains existing GO evidence rules;
  - recognizes exact historical content hashes;
  - validates the new verification-report schema without private runtime state.
- `scripts/verification_report_gate.py`
  - derives the report mode and harness from the committed scope authority;
  - validates a complete candidate against that authority and, for Codex,
    against live reconciliation state;
  - publishes with atomic no-replace semantics while binding one report to the
    authoritative task.
- `coordination/bin/send-event`
  - invokes candidate validation after composing the complete temporary event
    and before the atomic rename into `coordination/mailbox/sent/`;
  - leaves no final event and stages nothing when validation fails.
- `scripts/ci_smoke.py`
  - runs the same historical-baseline and structural report validation over
    committed mailbox contents;
  - does not require private runtime state in CI.

Provider behavior, sandbox profiles, verifier prompts, and finding severity
semantics remain in `scripts/opus_review_bridge.py`; the receipt module does
not become a second policy implementation.

### 6.2 Runtime state location

The production default is anchored to the owner of the resolved Git common
directory, not to the current linked worktree:

```text
<git-common-dir parent>/.codex/runtime/opus-review-receipts/v1/
<git-common-dir parent>/.codex/runtime/lane-v-report-publications/v1/
```

For Pipeline and its linked worktrees, the resolved common directory is
`<primary-Pipeline-root>/.git`; all worktrees therefore share the primary
root's receipt state. The implementation adds the narrow Git ignore rule
`.codex/runtime/opus-review-receipts/` and the corresponding narrow
`lane-v-report-publications/` rule. The latter holds one-publication state for
non-Codex tasks; Codex publication remains in its Opus receipt. Tests inject a
temporary common state root through an internal constructor seam, not a
production CLI flag.

The directory is owned by the current user, mode `0700`, and must be a real
directory rather than a symlink. Receipt files are regular files, mode `0600`,
opened and replaced relative to an already validated directory descriptor. The
store rejects symlinks, non-regular files, wrong ownership, overly permissive
modes, schema drift, and identity/digest mismatches.

Each immutable commit range has one deterministic attempt key. Its receipt and
per-attempt lock filenames are derived from that key. A process acquires and
holds an exclusive `flock` on the regular mode-`0600` lock file from before
reservation until the reviewed result is durable. Reservation additionally
uses `O_CREAT|O_EXCL`, so concurrent processes cannot both launch a provider
even if one observes an incomplete receipt transition. Atomic updates use a
same-directory temporary file, `fsync`, `os.replace`, and directory `fsync`.
Locks are per attempt key, so unrelated reviewed ranges do not block one
another.

Every receipt read and every read-modify-write transition, including
reconciliation and report publication, occurs while holding the same
per-attempt lock. Each transition verifies the preceding state and monotonic
generation before replacement. Identical concurrent reconciliation converges
on one stored result; conflicting reconciliation cannot last-write-win.

This uniqueness guarantee applies across linked worktrees that share the Git
common directory. Copying the repository to a new Git common directory or
altering private state is outside the trust boundary. Production prompts and
the mailbox write gate use only the derived default root.

### 6.3 Authoritative Lane V scope

The first process to run cannot define the review question. Every review is
bound to a committed `lane-v-scope/v1` descriptor under:

```text
coordination/verification/scopes/<task-id>.json
```

The strict JSON descriptor contains:

- schema version and a UUID task ID;
- one bounded `question_id` describing the pre-stated review question;
- trigger kind: `verify-request` or `shipping-commit`;
- verification mode and an exact supported harness identity;
- reviewed base policy and review profile;
- committed requirement paths;
- allowed path roots; and
- exact verification commands.

It rejects unknown fields and duplicate JSON keys. Requirement, allowed-path,
and command collections use the same canonicalization rules as the eventual
scope digest. `codex-lane-v` requires harness
`codex:lane-v-verifier` and review profile `codex-lane-v`. A non-Codex mode
must select one separately supported non-Codex harness identity in the
descriptor; report prose cannot select or change modes later.

The bridge does not accept caller-selected requirement, allowed-path, or
verification-command lists in production. It derives the descriptor pointer
from an authoritative trigger:

- a committed `verify-request` mailbox event addressed to exactly `operator`
  or `operator2`,
  whose exact `Lane-V-Scope:` field names the descriptor path and SHA-256
  digest; or
- a shipping `feat`/`fix`/`refactor` reviewed commit whose exact
  `Lane-V-Scope:` trailer names the descriptor path and digest.

For a verify request, the bridge receives the full trigger commit and event
path, reads the event and descriptor as Git blobs at that commit, validates the
mailbox envelope/kind/sender/recipient, and requires the event to name the
exact reviewed HEAD/base. For a shipping commit, it reads the trailer and
descriptor from the reviewed commit. The descriptor digest, trigger commit,
trigger path or commit trailer, and Git blob IDs enter the receipt scope. A
mutable working-tree copy is never authority. The exact committed descriptor
and verify-request bytes are supplied to Opus as immutable task requirements,
even when the later verify-request commit is not part of the reviewed snapshot.
Those requirements are represented by bounded, content-addressed Git blob
metadata (commit, normalized path, blob ID, SHA-256 digest, and size), not by a
mutable `Path` or retained raw prompt text. The isolated review repository
fetches the full trigger commit in addition to the reviewed HEAD/base,
re-verifies every bound blob there, and exposes exact `git show
<commit>:<path>` commands. Authority blobs are limited to 65,536 bytes each.

The canonical verify-request basename is
`<timestamp>-<sender>-to-<recipient>-verify-request.md`, where the recipient is
`operator` or `operator2`; the filename, H1 sender/recipient, `When` timestamp,
`From` sender, `Event type: verify-request`, reviewed commits, and scope field
must agree exactly. The filename's recipient is retained as authority for the
later verification-report sender check.

The implementation plan for a shipping change creates and commits this
descriptor before implementation; the shipping commit binds it by trailer. A
genuinely different question on the same commit range requires a distinct
pre-stated descriptor/task ID and remains subject to R-VERIFY-TIER. An arbitrary
caller task ID, descriptor not named by the trigger, altered descriptor with
the same task ID, or trigger/descriptor mismatch fails before reservation.

### 6.4 Attempt key versus scope digest

Two hashes serve different purposes:

- **Attempt key:** Pipeline repository identity, review profile, authoritative
  task ID, effective base commit, and reviewed HEAD. Authorization strings,
  command order, and path spelling cannot be varied to unlock another attempt
  for the same task and immutable range. A distinct, pre-authorized question
  receives a distinct task ID.
- **Scope digest:** a canonical JSON object containing every input actually
  exposed or authorized for the review.

The first valid invocation reserves the attempt key and records its scope
digest. A later invocation with the same attempt key and same scope digest
returns the existing state without launching a provider. A later invocation
with the same attempt key but a different scope digest fails with
`attempt_scope_conflict`; it does not create a second attempt.

The scope object contains:

- schema and bridge contract versions;
- stable Pipeline repository identity, computed from the resolved Git common
  directory after the existing Pipeline marker check so linked worktrees agree;
- authoritative task ID, question ID, trigger identity, descriptor digest, and
  Git blob IDs;
- full reviewed HEAD, requested base, and effective diff base;
- canonical changed-path entries, including status and old/new rename paths;
- each requirement path and SHA-256 of the exact committed bytes supplied to
  Opus from the reviewed snapshot;
- sorted, unique allowed path roots;
- sorted, unique verification commands after token-preserving canonicalization;
- `review_profile=codex-lane-v`; and
- resolved authorization identity.

Canonical JSON uses sorted keys, UTF-8, no insignificant whitespace, and an
explicit schema version before SHA-256 hashing. Collections whose order is not
semantic are sorted and deduplicated. The digest is rendered as
`sha256:<64 lowercase hex>`.

### 6.5 Complete changed-path coverage

Before reservation, the bridge computes changed paths from Git using the
effective base and reviewed HEAD as bytes with NUL-delimited name-status
output, `--no-renames`, no external diff, and no textconv. Disabling heuristic
rename/copy detection makes the result independent of Git config: a rename is
deterministically a delete plus an add, and a copy changes only its added path.

Path comparison is byte-exact, component-aware, and case-sensitive. It does no
NFC/NFD or case normalization. Authority-descriptor paths must be valid UTF-8
POSIX relative paths and encode losslessly to the compared bytes; a changed Git
path containing invalid UTF-8 fails closed as unsupported scope. A normalized
allow entry covers either the exact path or descendants beneath that path. No
glob magic, absolute path, backslash, leading/trailing slash, `.` or `..`
component, empty component, or NUL is accepted.

Coverage rules are:

- additions and modifications require the resulting path to be covered;
- deletions require the deleted path to be covered;
- a rename's delete and add paths are both covered, while a copy's added path
  is covered;
- an empty changed-path set fails as an invalid Lane V scope; and
- extra allowed roots are permitted because requirements and shared evidence
  may legitimately sit outside the changed set.

Requirement existence and content are read from the immutable reviewed
snapshot, not from mutable working-tree bytes. Missing-at-HEAD requirements
fail before reservation.

### 6.6 Receipt lifecycle

Each receipt uses `opus-review-receipt/v1` and these states:

```text
reserved -> reviewed -> reconciled -> publishing -> published
```

`reserved` is persisted before broker construction, sandbox probing, or
provider launch. It records the deterministic receipt ID, attempt key, full
scope object, scope digest, sanitized timestamps, and no review result.

`reviewed` adds exactly one normalized `opus-review/v3` result. It may be
`pass`, `issues`, or `unavailable`. It records a sanitized failure stage and
truncation flags when relevant, but never raw prompt text, raw response text,
stdout, or stderr.

`reconciled` adds one `opus-reconciliation/v2` input digest and result. The
digest binds:

- receipt ID and scope digest;
- Codex verdict;
- every finding disposition and its evidence digest; and
- expected reviewed HEAD/base.

An identical reconciliation request returns the stored result. Any changed
verdict, disposition, evidence, expected commit, or receipt scope fails with
`reconciliation_replay_conflict`.

`publishing` binds one planned mailbox path and candidate digest while the
atomic no-replace publication is in progress. `published` records the one
durable report path and digest. Every transition occurs under the per-attempt
lock and increments a checked generation; no stale writer may replace a newer
state.

If a process dies after `reserved` is durable but before `reviewed`, no caller
may relaunch the provider. A second process that cannot acquire the attempt
lock returns `attempt_in_progress`. If the next identical `review` invocation
acquires the lock after the owner has exited and finds the receipt still
`reserved`, it transitions the receipt without provider use to
`reviewed/unavailable` with
`unavailable_reason=attempt_state_uncertain`. Reconciliation may then preserve
only a visibly degraded Codex verdict. Wall-clock age is not used to decide
liveness. There is no reset or retry CLI.

The receipt ID is deterministic from the attempt key and version. It is an
identifier, not a bearer secret.

Receipt-only reconciliation locates state through the store, never by scanning
or opening the runtime directory in the bridge. `ReceiptStore.lock_receipt()`
accepts only the canonical `opr1:<64 lowercase hex>` identifier, maps it to the
one exact descriptor-relative receipt and lock name, and `load_existing()`
fails closed without creating a receipt when that exact record is absent. The
same metadata, ownership, no-follow, and exclusive-lock checks used by
scope-derived review access therefore remain authoritative during
reconciliation.

### 6.7 CLI contracts

`review` accepts the repository, reviewed HEAD/base, exact review profile and
authorization, plus either a committed verify-request trigger or the reviewed
shipping commit trigger. It derives requirements, allowed paths, verification
commands, task identity, and harness mode from the trigger-bound scope
descriptor. The former production CLI path that accepted those lists directly
is removed; internal constructors remain injectable for pure tests.

On success it prints `opus-review/v3` plus:

```json
{
  "receipt_id": "opr1:<attempt-key-digest>",
  "scope_digest": "sha256:<scope-digest>",
  "receipt_state": "reviewed"
}
```

The result is returned from the private receipt on an exact idempotent repeat;
the provider is not called again. If reconciliation already occurred, the
returned `receipt_state` is instead `reconciled`.

`reconcile` changes incompatibly. It accepts:

```text
--receipt-id <id>
--repo-root <Pipeline root>
--head <full sha>
--base <full sha, when originally explicit>
--codex-verdict GO|NITS|FAIL
--disposition ID=value
--evidence ID=value
```

`--opus-review-json` is removed and rejected by argument parsing. The public CLI
has no alternate JSON/file/stdin result-import path. Reconciliation loads the
normalized review only from the matching receipt, verifies the current
repository and commit binding, applies the existing severity rules, persists
the result, and emits a ready-to-copy report-field block.

Internal `OpusReview.from_dict` parsing remains available only for validating
provider output and receipt reads. It is not a reconciliation trust boundary.

### 6.8 Report schema and write gate

New verification reports use `lane-v-report/v2`. Every new report contains one
exact `## Verification Attestation` section. The section contains each
canonical field exactly once, in the generated order; duplicate sections,
duplicate fields, unknown fields, decorated field names, continuation lines,
and values outside their field-specific bounds are rejected. Free-form prose
elsewhere in the report cannot satisfy or override the section.

The physical grammar is exact: the heading is followed by one blank framing
line and then the 17 consecutive field lines. After the final field, the report
either ends or has one blank line followed by the next exact level-two heading.
A blank, continuation, prose line, subheading, extra field, carriage return, or
NUL cannot terminate or escape the section. Raw UTF-8 line and section byte
limits are applied before value/JSON parsing.

Every new report declares:

```text
Verification schema: lane-v-report/v2
Verification mode: codex-lane-v | <supported non-Codex mode>
Verification harness: <exact identity from the scope authority>
Verification task ID: <UUID from the scope authority>
Scope authority: <path>@sha256:<descriptor digest>
Trigger identity: <shipping commit or committed verify-request identity>
Reviewed head: <full lowercase sha>
Reviewed base: <full lowercase sha | none>
```

A `codex-lane-v` report additionally carries the exact bridge-generated fields:

```text
Review profile: codex-lane-v
Authorization identity: <standing policy or explicit task identity>
Opus receipt ID: <receipt id>
Opus scope digest: sha256:<64 lowercase hex>
Cross-model review: pass | issues | unavailable
Effective Opus model: <verified model id | not-available>
Opus finding dispositions: <none or canonical bounded JSON object>
Reconciliation guard: <canonical JSON with go_allowed and digest>
Degraded reason: <none or exact enumerated reason>
```

The bridge renders these fields from stored reconciliation state; callers do
not construct them independently. The dispositions value is either `none` or a
canonical JSON object keyed by the existing bounded finding-ID grammar. Each
value contains exactly `disposition`, `evidence`, and `evidence_digest`; the
digest is `none` for an empty value or `sha256:<64 lowercase hex>` over the
exact UTF-8 Codex disposition evidence. This is Codex-authored proof, not raw
provider prose. The guard value is canonical JSON containing exactly
`go_allowed` and `digest`. The existing `## Evidence` section still carries the
executed command/output proof required for GO. The entire attestation section
has a fixed byte cap so finding-count, evidence, or line-length expansion cannot
become a report parser resource attack.

For `codex-lane-v`, `Verification harness` is exactly
`codex:lane-v-verifier`. For a supported non-Codex mode, every Opus-specific
line is still present with the literal value `not-applicable`, including review
profile, authorization, receipt ID, scope digest, cross-model status, effective
model, finding dispositions, reconciliation guard, and degraded reason. Mode,
harness, task, scope authority, and trigger are loaded from and checked against
the committed descriptor and trigger; they are not trusted from caller prose.

At `send-event`, a completed temporary `verification-report` is validated
before publication. Structural and scope-authority validation apply to every
new report. A Codex report additionally loads the matching receipt. Live
validation proves:

- the filename and envelope sender are `operator` or `operator2` and agree;
- there is exactly one undecorated `VERDICT: GO|NITS|FAIL` line;
- report mode, harness, task ID, trigger, HEAD/base, and scope authority equal
  the committed trigger and descriptor;
- for Codex, profile, authorization, receipt ID, and scope digest match;
- review status, effective model, degraded reason, and all dispositions match;
- the reconciliation digest and exact stored Codex verdict match; and
- the full SHA in the report H1 equals `Reviewed head`.

For Codex GO, `go_allowed` must be true. Codex NITS/FAIL require false and must
equal the stored reconciliation verdict; NITS cannot substitute for FAIL or
vice versa.

The gate holds the task's publication lock, records a `publishing` path and
candidate digest, creates the final report with same-directory atomic
hard-link/no-replace semantics, `fsync`s the directory, then records
`published`. A Codex publication is an additional receipt transition; a
non-Codex task uses an equivalent private publication record keyed by its
authoritative task ID. Exactly one canonical report path+digest may publish per
task. A repeated or altered publication is rejected. For verification reports,
the current shell-level check-then-`mv` sequence is replaced by this single
publisher; no preliminary existence check is treated as publication authority.

If publication recovery finds the named final path with the expected digest,
it finalizes `published`; if the path is absent, it clears the interrupted
publication reservation before accepting one new candidate; a mismatched path
or digest fails closed. Validation or publication failure leaves no new final
event and the shell trap removes the temporary file. A Git staging failure
after successful publication preserves the validated final event and its
publication binding, matching current `send-event` recovery semantics; the
operator stages that exact path manually rather than emitting another report.

`send-event` resolves the trusted Python from the resolved Git common
directory's Pipeline root and fails closed if that interpreter is unavailable.
Other event kinds are unchanged.

### 6.9 Historical report compatibility

A committed `scripts/baselines/lane_v_report_v1.json` manifest records the
repository-relative path and SHA-256 content digest of every historical
verification report that predates
`lane-v-report/v2`. It records exact artifacts, not a timestamp cutoff.

During a repository scan:

- an exact path+digest baseline match is accepted under the historical schema;
- a new report must satisfy v2;
- a modified historical report no longer matches and must be migrated to v2 or
  accompanied by an explicit, reviewed baseline update; and
- deleted historical reports are surfaced as baseline drift rather than
  silently reducing the evidence set.

The manifest contains no report prose or business data. CI and
`scripts/ci_smoke.py` validate it without access to private receipt state.
Consequently CI proves committed structure and immutable legacy accounting,
while the live `send-event` boundary proves the local receipt match.

Initial manifest generation enumerates only NUL-delimited Git-tracked `HEAD`
paths and hashes their raw blobs; it never grandfathers ignored or mutable
working-tree files. Normal validation separately enumerates current filesystem
reports, reads each once as raw bytes, and therefore detects untracked new
reports. Explicit replacement may update digests only for the already-reviewed
manifest path set; it cannot add later reports, remove missing history, or
change paths. Initial publication is atomic no-clobber, while an explicit valid
replacement uses same-directory fsync/replace/fsync durability.

### 6.10 Provider output and resource safety

Provider stdout and stderr are drained concurrently so the child cannot block
on a full pipe. Each stream retains at most a fixed production cap in memory;
additional bytes are drained and discarded while setting a truncation flag.
No unbounded temporary output file is created or decoded. Truncated output
cannot be parsed as a successful review and becomes a sanitized
`unavailable` result.

The durable failure record uses enumerated stages such as `broker_start`,
`sandbox_probe`, `provider_spawn`, `provider_timeout`, `provider_exit`,
`response_parse`, `contract_validation`, and `model_validation`. A failure to
write the final receipt cannot truthfully record its own stage; the CLI reports
only the sanitized `receipt_write` reason and leaves the durable reservation
for uncertain-attempt recovery. Neither form records command arguments,
environment values, raw stderr, or provider text.

`_VerificationBroker.__init__` owns cleanup from the instant the listener
socket is allocated. Any bind, listen, permission, thread-start, or later
constructor failure closes the listener, stops any started thread, and removes
the socket path before re-raising. Normal context-manager cleanup remains
idempotent.

## 7. Data Flow

```text
Codex completes verdict-blind Lane V analysis
  -> review resolves the committed trigger and authoritative scope descriptor
  -> review validates Pipeline, commits, requirements, commands, and coverage
  -> bridge canonicalizes scope and reserves the immutable attempt key
  -> bridge performs zero or one sandboxed Opus provider launch
  -> bridge persists normalized pass/issues/unavailable evidence as reviewed
  -> Codex investigates every finding and supplies dispositions
  -> reconcile loads only the receipt and stores one bound reconciliation
  -> bridge renders the report-field block
  -> send-event validates and no-clobber-publishes one bound candidate
  -> operator emits GO/NITS/FAIL; CI preserves structural and legacy evidence
```

The provider reads no mailbox state. The review subcommand may read only the
exact committed verify-request blob named as its trigger; it does not inspect
live cursors, consume mail, or write mailbox state. Only the operator-owned
`send-event` step creates the durable verification report.

## 8. Error Semantics

Errors divide into three classes:

1. **Pre-reservation contract failure:** wrong repository/profile, invalid
   commits, invalid/unbound scope authority or trigger, incomplete changed-path
   coverage, missing committed requirements, invalid commands, or malformed
   explicit authorization. No receipt and no provider attempt are created.
2. **Reserved attempt unavailable:** broker, sandbox, provider, timeout,
   output-bound, parse, schema, scope-return, or model-identity failure. The
   receipt becomes `reviewed/unavailable`; no retry occurs.
3. **Integrity/replay failure:** receipt corruption, scope conflict, stale
   commit mismatch, altered reconciliation, report mismatch, or historical
   baseline drift. The operation fails closed and cannot emit GO.

If the final receipt update itself fails after a provider may have launched,
the durable `reserved` record remains. Recovery follows
`attempt_state_uncertain`; it never launches another provider.

## 9. Adversarial-Surface Enumeration

This change touches parseable provider output, authorization, side-effect
gating, and a schema whose acceptance grants GO trust. R-INDEPENDENCE therefore
applies. The following cases are mandatory acceptance targets.

### 9.1 Result fabrication and replay

- caller supplies fabricated pass, issues, or unavailable JSON;
- caller uses the removed v2 JSON CLI through stdin, a file, or an unknown flag;
- receipt ID exists but belongs to another HEAD/base or repository;
- identical reconcile request repeats;
- two processes submit identical reconciliation concurrently;
- two processes submit conflicting reconciliation concurrently;
- verdict changes after reconciliation;
- one disposition, evidence string, or expected commit changes on replay;
- a pass/unavailable receipt receives dispositions;
- issue IDs are missing, duplicated, added, malformed, or reordered;
- stale receipt is used after HEAD changes; and
- a private receipt file is truncated, schema-mutated, symlinked, replaced by a
  special file, wrong-owner, or mode-widened.

### 9.2 Attempt uniqueness and crash boundaries

- two processes reserve the same attempt concurrently;
- two linked worktrees race the same authoritative task and commit range;
- a second invocation uses reordered or duplicate paths/commands;
- a second invocation changes requirements, authorization, allowed paths, or
  commands for the same authoritative task and commit range;
- a caller invents a task ID, selects a descriptor not bound by its trigger, or
  changes a descriptor while retaining its task ID;
- two lawful, pre-stated task IDs ask genuinely different questions on one
  commit range without colliding;
- crash occurs before reservation, after reservation but before launch, during
  provider execution, after provider exit, or during final atomic replacement;
- a live reservation is mistaken for abandoned;
- an abandoned reservation is retried rather than degraded; and
- a changed HEAD correctly receives a new attempt key.

### 9.3 Scope completeness and canonicalization

- changed file omitted from allowed roots;
- deletion omitted because the path no longer exists at HEAD;
- only one delete/add side of a rename covered, or a copied addition omitted;
- directory prefix collision such as `scripts/foo` versus `scripts/foobar`;
- case-colliding paths and distinct NFC/NFD spellings remain distinct;
- invalid-UTF-8 changed path fails closed;
- absolute path, `./`, `.`, `..`, backslash, glob magic, empty component, or
  leading/trailing slash;
- requirement exists in the working tree but not at reviewed HEAD;
- mutable working-tree requirement bytes differ from `HEAD:path` while the
  digest remains derived from the Git blob;
- changing reviewed HEAD changes a changed requirement's digest;
- empty diff or non-ancestor base;
- abbreviated, uppercase, missing, or moving commit reference;
- command whitespace/quoting variations create a second attempt; and
- authorization/profile variation attempts to unlock a retry.

### 9.4 Provider and resource behavior

- stdout or stderr exceeds the cap independently or simultaneously;
- provider exits while reader threads are draining;
- timeout kills the full process group and joins drainers;
- malformed, oversized, non-UTF-8, or trailing provider output;
- returned review names a non-Opus model or mismatched scope;
- socket allocation succeeds but bind/listen/thread start fails;
- cleanup is called twice; and
- Seatbelt, AF_UNIX, Claude CLI, credentials, or network capability is absent.

### 9.5 Report and mailbox enforcement

- new GO omits verification mode or receipt fields;
- duplicate attestation sections/fields or lookalike fields in free-form prose;
- oversized or non-canonical disposition/guard JSON;
- Codex Lane V report claims a nonexistent, reserved, unmatched, or
  unreconciled receipt;
- GO claims `go_allowed=false` or NITS/FAIL claims `go_allowed=true`;
- report verdict differs from the exact stored Codex verdict, including
  NITS/FAIL substitution;
- sender is not operator/operator2 or filename and envelope sender disagree;
- report alters status, model, dispositions, degraded reason, or digest;
- unavailable result omits its exact degraded reason;
- report self-declares a mode, harness, task, or descriptor different from its
  committed scope authority;
- a non-Codex report omits its separately authorized harness identity or uses
  Codex-only values;
- historical report body changes while its filename stays fixed;
- new report tries to inherit legacy status by timestamp or filename shape;
- candidate validation fails after the temp file is written;
- two paths attempt to publish from one reconciliation/task;
- no-replace publication races a same-second collision;
- crash occurs before/after the `publishing` transition or atomic link;
- recovery sees absent, exact, or mismatched final content; and
- Git staging fails after a validated final event is published.

A fresh independent reviewer must challenge this enumeration before the design
commit. Before completion, an independent actual-diff review must verify that
the implemented tests cover these cases. A same-model subagent is acceptable
for design review only when explicitly identified as weaker; the required
post-Lane-V Opus attempt remains the distinct-model implementation review when
the provider is available.

## 10. Test Strategy

Implementation follows test-driven development. Each behavior begins with a
failing test or mutation probe.

### 10.1 Pure receipt and contract tests

- canonical scope digest stability and sensitivity;
- authoritative trigger/descriptor parsing, binding, and mutation rejection;
- full byte-exact changed-path coverage for add/modify/delete/rename/copy,
  case/NFC/NFD variants, and invalid UTF-8;
- exclusive concurrent reservation across two linked worktrees and same-scope
  idempotency;
- changed-scope conflict for the same attempt key;
- distinct authorized task IDs for different questions on one range;
- every legal and illegal lifecycle transition;
- abandoned-lock reservation degradation without provider invocation;
- exact and concurrent reconciliation replay plus changed replay rejection;
- secure path, mode, symlink, and malformed-state rejection, with ownership
  supplied through an injected `stat` boundary where the host cannot create a
  foreign-owned fixture;
- legacy caller JSON rejection; and
- unchanged severity/disposition rules loaded from receipt state.

### 10.2 Report tests

- exact historical baseline acceptance and drift detection;
- v2 Codex and non-Codex positive fixtures;
- every missing/mismatched field;
- exact descriptor-derived mode/harness/task/trigger and verdict binding;
- live receipt/report comparison;
- one-publication binding, atomic no-replace races, and interrupted-publication
  recovery for absent/exact/mismatched final state;
- `send-event` leaves no final event and stages nothing on failure;
- successful candidate validation preserves the envelope; staging failure
  preserves the one validated final event for manual staging; and
- `ci_smoke` needs no private receipt store.

### 10.3 Resource tests

- deterministic constructor cleanup by injecting bind/listen/thread failures;
- bounded concurrent stdout/stderr drains and truncation classification;
- process-group cleanup on timeout and reader failure; and
- pure sandbox profile generation and capability-probe classification.

Tests that exercise actual Seatbelt, AF_UNIX, or Claude execution run only when
a shared capability probe proves those facilities are usable. A skip names the
missing host capability. Pure validation, receipt, schema, command, prompt,
cleanup-injection, and output-bound tests always run and may not be hidden by
the integration skip.

### 10.4 Completion verification

The implementation plan will name focused commands after impact analysis. The
minimum completion pass includes:

```text
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_prompt_sync.py -q

env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

The full unit suite follows if focused tests pass. A live Opus attempt is made
once only when the production capability probe succeeds; unavailable evidence
is reported without retry when the environment cannot support it.

## 11. Documentation And Rollout

Implementation updates:

- `ARCHITECTURE.md` with the receipt lifecycle, complete-scope invariant,
  report write gate, output bounds, and current verification date;
- `DECISIONS.md` with an append-only ADR that records the trust boundary and
  the intentional `--opus-review-json` incompatibility;
- `docs/protocol/codex/continuation.md`, Codex role prompts, and the operator
  skill with the receipt CLI and report fields;
- `.gitignore`, `docs/protocol/protocol-assembly-map.md`, and the new
  `coordination/verification/scopes/` artifact contract;
- the prior Opus design docs with a short supersession pointer rather than
  rewriting their historical decisions; and
- the report-format source used by operator prompts, if impact analysis shows
  one canonical source exists.

Rollout order is:

1. land receipt and report tests with the implementation;
2. generate and verify the exact historical-report baseline at that commit;
3. switch bridge reconciliation to receipt-only;
4. switch prompts and docs to the new CLI and fields;
5. activate `send-event` candidate validation;
6. run focused, full, smoke, baseline, and doc checks;
7. perform independent actual-diff review against Section 9; and
8. attempt the one authorized post-Lane-V Opus review if the host capability
   exists, otherwise preserve the exact degraded reason.

No mailbox event, live route, cursor, lock, push, or external publication is
part of implementation without its separately triggered authority.

## 12. Consultation And Design Provenance

The pre-plan touches authority, parseable output, schema trust, and a mailbox
side-effect gate, so a guarded ChatGPT Pro consultation was prepared under
consultation ID `1351461e-3d8c-4b25-b1e7-ed5657483d91`. The guard rejected the
preparation before any prompt left the machine. The no-retry rule was obeyed;
there was no imported advice and therefore no design change attributed to the
consultation.

The selected design instead rests on the local implementation audit, the
existing Opus contracts, the user-principal's explicit approval to remove the
caller-JSON compatibility path, and the independent adversarial review required
before this document is committed.

A fresh same-model reviewer challenged the draft independently. This is
explicitly weaker than a distinct-model review. It identified shared-worktree
state, authoritative first-writer scope, self-declared non-Codex bypass, exact
verdict/sender binding, concurrent reconciliation, byte-level Git paths,
publication replay/no-clobber, and infeasible fixture language as material
gaps. Sections 6, 9, and 10 incorporate each correction. After those changes,
the reviewer judged the adversarial enumeration sufficient for design-time use;
the implementation still requires a fresh actual-diff review and the one
authorized Opus attempt when the host can run it.
