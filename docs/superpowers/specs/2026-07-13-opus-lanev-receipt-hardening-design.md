# Opus Lane V Receipt And Report Hardening Design

**Date:** 2026-07-13
**Status:** Approved by the user-principal on 2026-07-13 and implemented through
Task 9 in the isolated hardening branch; independent whole-branch reviews found
the active-trigger guidance gap covered by Task 8 and the duplicate shipping
authority gap covered by Task 10 below; independently challenged before
approval; amended after
`a3717e3` to bind exact index staging, explicit recovery, trusted startup, and
the real provider prompt
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
- Raw per-attempt rendered task prompts and raw provider streams do not enter
  Git, mailbox artifacts, or persistent logs. The static reviewed
  provider-instruction source is ordinary committed code and is pinned here.
- Historical mailbox reports remain readable without a mass rewrite.

Tasks 1-5A remain bound to the original descriptor. Prep 5B and committed Task
6 remain historically bound to
`74d50ded74c017c614fb6a746231e0f910ac28d247c9ad728c099f71d2aa8ffe` of
`coordination/verification/scopes/2a876e95-3a87-4203-a613-1a29dd957b5b.json`.
Task 7 and its post-task test-only correction use the amended digest
`c16aa28ce9211e7214ba8fb5586059515a8a59de3b37a0f853c6e13da73d5a93`
of that same path. Both generations retain the exact implementation base and
content-addressed provider-prompt authority; the Task 7 generation additionally
authorizes only the exact `docs/PROTOCOL-RULES-LOG.md` write, not `docs`.
Task 8 and final unchanged-HEAD Lane V use the precommitted digest
`e393655f4ba9ad0dcfa0467fcc54c809c79a1b28b76a2022a7d846acc8996e84`.
That generation adds only twelve exact active guidance roots and two focused
test modules; it does not grant broad `.agents/skills`, `.claude`,
`coordination`, `docs`, or `docs/templates` authority.

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
11. Make every active trigger producer and consumer describe the same exact
    authority structure already enforced by the bridge and publication gate.

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
  - starts with absolute privileged Bash and invokes candidate validation after
    composing the complete temporary event;
  - delegates no-replace publication and exact no-filter index staging to the
    locked Python publisher;
  - leaves no reported success and stages nothing when pre-publication
    validation fails; interrupted publication remains explicitly recoverable.
- `scripts/prompts/opus_lane_v_advisory.md`
  - is the provider-only advisory prompt loaded as an exactly pinned reviewed
    Git blob;
  - grants no seat, verdict, mailbox, lock, Git, or side-effect authority;
  - leaves the genuine Claude Lane V role file unchanged.
- `scripts/prompts/opus_lane_v_advisory.authority.<blob>.json`
  - is a descriptor-named content-addressed requirement;
  - pins the exact prompt path, blob OID, full/body digests, and sizes before
    the prompt becomes executable.
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

Every host-side Git invocation that selects committed authority, object
identity, repository identity, or a runtime-state root runs with every inherited
`GIT_*` variable removed and with `git --no-replace-objects`. The requested
repository remains the command working directory and must still pass the exact
root and Pipeline-marker checks. This prevents `GIT_DIR`, `GIT_COMMON_DIR`,
object-directory/alternate-object selectors, and replace refs from coherently
redirecting both the reviewed object graph and the receipt root. The provider
and verification sandboxes retain their separately allowlisted environments.

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

`publishing` binds one exact eight-field file/index witness while atomic
no-replace publication is in progress: planned mailbox path, candidate digest,
direct-child candidate basename, device, inode, expected Git blob OID, literal
index mode `100644`, and stage `0`. `published` retains that exact witness for
the one durable report. Every transition occurs under the per-attempt lock and
increments a checked generation; no stale writer may replace a newer state.

If a process dies after `reserved` is durable but before `reviewed`, no caller
may relaunch the provider. A low-level observer using the explicit nonblocking
attempt-lock API receives `attempt_in_progress` when the lock is held. The
public `review()` path uses the blocking attempt lock: an identical concurrent
caller waits, then returns the completed stored result or, if the owner exited
while the receipt remained `reserved`, transitions the receipt without
provider use to
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

The gate holds the task's publication lock and records the complete
`publishing` witness: path, candidate digest/name/device/inode, and expected
stage-0 Git object ID/mode/stage. It creates the final report with
same-directory atomic hard-link/no-replace semantics, durably completes the
file and directory fsync sequence, writes the captured bytes as an exact Git
blob with `hash-object -w --no-filters --stdin`, stages only the canonical final
path with `update-index --cacheinfo`, and revalidates the stage-0 entry, object
bytes, and final witness. Only then does it record `published` while retaining
that exact eight-field witness. `published` therefore attests both the durable
final and the exact index binding observed under the lock. A Codex publication
is an additional receipt transition; a non-Codex task uses an equivalent
private publication record keyed by its authoritative task ID. Exactly one
canonical report and creation witness may publish per task. A repeated or
altered fresh publication is rejected. For verification reports, the current
shell-level check-then-`mv` and later `git add` sequence is replaced by this
single publisher; no preliminary existence check or clean-filtered staging is
treated as publication authority.

The non-Codex record schema is `lane-v-task-publication/v1` and contains exactly
the canonical task UUID, an authority digest, state, generation, and the same
eight publication fields: path, candidate digest/name/device/inode, and
`index_blob_oid`/`index_mode`/`index_stage`. The authority digest covers
repository identity, task ID, mode, harness, descriptor path/digest, trigger
identity, reviewed HEAD/base, and the authorized operator recipient. `ready`
has an odd generation at least 1 and all eight publication fields null;
`publishing` has an even generation at least 2 and the exact path, digest,
direct-child candidate basename, non-boolean non-negative device, non-boolean
positive inode, full Git object ID, literal mode `100644`, and non-boolean stage
zero present; `published` has an odd generation at least 3 and retains that
exact witness. The Codex receipt publication mapping carries the same fields.
Initial validated reservation creates `ready` generation 1. Every begin, fresh
pre-link exact-witness cancellation, both-names-absent recovery clear, or
exact-witness finish increments generation. Unknown fields, illegal
type/parity/nullability, changed authority, malformed private state, mismatched
recovery, or a pre-existing index entry for a fresh report path fails without
rewriting the record. `published` is illegal until the file witness, blob
bytes, and exact stage-0 facts have all been revalidated.

Codex live validation occurs under the receipt lock and decodes the stored
review and reconciliation through the bridge's public normalization functions;
raw receipt mappings are never treated as report authority. It additionally
matches the receipt's repository identity and stored commits to the current
provider-neutral structural authority. The receipt transition methods may be
internally idempotent for crash recovery, but the public publisher rejects an
entry state of `published`, including an identical replay. Only an entry state
of `publishing` may recover. Candidate-only recovery verifies the witnessed
bytes/inode, recreates the no-replace final link, and continues. Final-only
recovery validates and fsyncs that witnessed inode. Final-plus-candidate
recovery requires both names to be the same witnessed inode and exact bytes,
then removes only the verified candidate name after the final is durable. In
all three cases recovery idempotently writes or verifies the expected blob,
converges only the exact stage-0 index entry, revalidates the final witness,
blob bytes, and index tuple, and only then calls `finish_publication` with the
stored eight-field witness. A fresh `os.link` collision is not recovery even if
the existing bytes match; it fails and cannot be mistaken for a link created
by an interrupted publisher. Because that pre-link destination is not the
witnessed inode created by this invocation, an exact witness-plus-generation
cancellation returns the fresh attempt to `reconciled|ready`; this narrow
fresh-`EEXIST` transition is distinct from the interrupted-recovery clear below.

Candidate and final names are direct children of one held, descriptor-relative
`coordination/mailbox/sent` directory. The candidate is opened once with
`O_NOFOLLOW`, required to be a regular current-uid mode-`0600` single-link
file, and its device/inode, metadata, bytes, and digest are retained. The name is
revalidated against that inode immediately before a basename-only hard link.
The caller-supplied candidate path itself must be absolute, lexically canonical,
and name that exact held parent; parent/alias components or the same basename in
another directory are rejected rather than reduced to `.name`.
The final must be the same inode and digest through its own no-follow descriptor.
After exact candidate validation the publisher fsyncs the held file descriptor.
After linking it validates and fsyncs the same final inode, fsyncs the directory,
writes the captured bytes with absolute system Git as an unfiltered object,
stages only the canonical path with `update-index --cacheinfo`, and parses one
NUL-delimited stage-0 index entry without shell command substitution. The
object bytes, index mode/OID/stage/path, and reopened final witness must all
match. It then removes the temporary candidate, fsyncs the directory again,
reopens the final, requires link count 1 and the same digest, fsyncs that
descriptor, checks index durability, and only then records `published`. A
failure before that transition preserves the witnessed `publishing` state for
explicit recovery and never reports success. A durable `published` transition
can therefore never precede file-data, mailbox-name, and exact-index
validation.

Publication recovery clears the interrupted reservation back to
`reconciled|ready` only when both the stored final and candidate names are
absent, the exact index entry is absent, the held directory is fsynced, and all
three facts remain true immediately before the checked transition. A surviving
valid candidate is therefore recovery input, never discardable evidence. Any
mismatched candidate or final path, digest, device, inode, blob, or index entry
fails closed. Validation failure before `publishing` leaves no new final event
and the shell trap removes only its unbound temporary file. A link,
object-write, index-stage, or final-revalidation failure after `publishing`
remains a non-successful, explicitly recoverable record. The operator does not
stage manually and does not emit another report.

Recovery may finalize the persisted path from an earlier second. The publisher
therefore emits exactly that canonical repository-relative path on stdout only
after the final and exact stage-0 index blob both validate. `send-event`
validates that returned path but performs no second staging operation. Empty,
multiline, absolute, traversing, wrong-directory, or wrong-suffix output fails
closed; diagnostics use stderr and failure emits no stdout.

Recovery is explicit through `resume --repo-root ROOT (--receipt-id ID |
--task-id UUID)` and read-only inspection through the analogous `status`
command. Neither accepts caller-supplied path, digest, object ID, or witness.
`resume` accepts only stored `publishing`, reacquires the same lock, validates
the stored final/candidate witness, converges a missing or already-correct exact
index entry, and then completes. Public `publish` still rejects `published`.
`status` emits canonical single-line sanitized JSON containing only state,
stored path, file-witness match, index OID, and staged-blob match. Output loss
after `published` is resolved by `status`, never another publication.

`send-event` resolves the trusted Python from the resolved Git common
directory's Pipeline root and fails closed if that interpreter is unavailable.
It also requires the common-directory parent to be the matching primary
Pipeline checkout. It captures that checkout's literal full HEAD once, requires
the gate plus receipt/bridge imports to be regular Git blobs at that commit, and
materializes exactly those three blobs into a newly-created mode-`0700` code
directory. Python executes that copy, never a mutable primary or linked-worktree
pathname. Until the captured primary HEAD contains the publication gate,
verification-report emission fails closed. Bare,
separate-git-dir-without-primary, root-mismatch, missing/non-blob module,
unavailable interpreter, import, or missing-CLI cases create and stage nothing.
The trusted Python runs from that three-file code directory with an allowlisted
environment, `-E -s -S -B`, and a new secure empty `-X pycache_prefix`
directory, so caller `PYTHON*`, user/system `sitecustomize`, untracked shadow
modules, adjacent cached bytecode, primary-path TOCTOU, and linked-worktree
module paths cannot replace the captured modules. Root-selection Git uses the
absolute system Git, all `GIT_*` values removed, and `--no-replace-objects`.
Other event kinds are unchanged.

The shell begins with `#!/bin/bash -p`, establishes the system PATH before any
external command, initializes cleanup variables before installing its trap,
and uses a partial-initialization-safe trap. Hostile `PATH`, `BASH_ENV`,
exported functions, HOME/XDG config, attributes, and clean filters cannot alter
the selected runtime or staged bytes. Live activation remains fail-closed until
an explicitly authorized executor fast-forwards a clean, unchanged primary
checkout to the landed Task 7 head and revalidates the required blob modes and
OIDs. That shared-checkout activation is a separate user-gated side effect, not
part of Tasks 6-7 or coordinator handoff.

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
replacement uses same-directory fsync/replace/fsync durability. Replacement is
serialized by one secure stable lock under the sanitized Git common directory,
acquired before resolving the immutable HEAD snapshot and held through target
replacement and directory fsync. Locking the replaceable manifest inode is not
sufficient.

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

### 6.11 Provider-only advisory prompt

The current bridge actually loads `.claude/agents/lane-v-verifier.md` from the
trusted reviewed base, strips its YAML frontmatter, and passes the Markdown body
as `--append-system-prompt`; `.codex/agents/lane-v-verifier.toml` is not a
provider input. Because that shared Claude file is also a genuine Claude Lane V
role and lies outside the original descriptor's allowed roots, it is not
repurposed. The amended scope descriptor instead names a prompt-authority
requirement whose own expected Git blob OID appears in its filename. That
content-addressed JSON precommits the exact path, Git blob OID, full-file/body
SHA-256 digests, and byte sizes for
`scripts/prompts/opus_lane_v_advisory.md`. An inert prep commit then adds those
exact bytes; a later commit validates the authority-requirement blob, loads the
named prompt Git blob from the literal reviewed commit, and rejects it unless
every earlier fact matches. The reviewed commit cannot select different
instruction bytes. There is no HEAD-drift, WIP, mirror, frontmatter-body, or
linked-worktree fallback.

The exact target body is committed verbatim in the implementation plan's
approved post-`a3717e3` amendment. It identifies the model as a read-only
advisory evidence reviewer, not a seat or decision-maker, and expressly denies
GO/NITS/FAIL, mailbox, route, lock, staging, commit, push, and side-effect
authority. It returns only the caller's `pass|issues` evidence schema.

Before reservation, `ReviewScope` binds the descriptor/trigger authority, the
content-addressed authority-requirement blob, prompt path, Git blob OID,
full-file SHA-256/size, and extracted-body SHA-256/size. Those fields enter the
scope digest and receipt. The already-loaded exact body is passed to the
provider; it is not reloaded after reservation and raw prompt text is never
persisted in receipt/runtime state or provider-output logs. Same-attempt prompt
drift is `attempt_scope_conflict`, not another launch. A real-Git rendered regression
captures the provider argv and proves the descriptor-bound body is exactly the
`--append-system-prompt` value while the blind generated task prompt remains a
separate `-p` value.

### 6.12 Authority-bearing trigger production

The bridge and report gate already consume two exact trigger forms. Active
producer and consumer guidance must now expose that same contract rather than
describing a looser commit-only or prose-only approximation.

A verify-request trigger is a canonical committed sent-mailbox event strictly
after the reviewed HEAD. It contains exactly one `Event type: verify-request`,
one full lowercase forty-hex `Reviewed head`, one full lowercase forty-hex
`Reviewed base`, and one canonical
`Lane-V-Scope: coordination/verification/scopes/<uuid>.json@sha256:<64
lowercase hex>` field. The event fields agree with the committed descriptor and
the canonical filename/envelope.

A shipping trigger is lawful only when its commit equals the reviewed HEAD,
its subject begins `feat`, `fix`, or `refactor`, and exactly one identical
descriptor reference appears in the terminal Git trailer block. A descriptor
reference in the body, an arbitrary landed commit, or a trigger commit distinct
from reviewed HEAD grants no authority.

Missing, duplicated, abbreviated, uppercase, misplaced, uncommitted, stale, or
mismatched authority means no lawful trigger exists. The operator stops with a
blocker and never reconstructs fields or falls back to the other trigger kind.
Implementers may emit the shipping trailer only under explicit parent commit
authority with the exact descriptor reference supplied; implementers and
reviewers never invent it.

This descriptor and trigger grammar remains Pipeline-only. Evidence-ledger or
other cross-repository verification returns to the coordinator for a separate
evidence-ledger-aware bridge route; no seat fabricates Pipeline descriptor
authority to bridge the repository boundary.

## 7. Data Flow

```text
Codex completes verdict-blind Lane V analysis
  -> review resolves the committed trigger and authoritative scope descriptor
  -> review validates Pipeline, commits, requirements, commands, coverage,
     and the descriptor-bound advisory prompt blob
  -> bridge canonicalizes scope and reserves the immutable attempt key
  -> bridge performs zero or one sandboxed Opus provider launch
  -> bridge persists normalized pass/issues/unavailable evidence as reviewed
  -> Codex investigates every finding and supplies dispositions
  -> reconcile loads only the receipt and stores one bound reconciliation
  -> bridge renders the report-field block
  -> send-event invokes one locked transaction that validates, no-clobber
     publishes, exact-stages, and revalidates one bound candidate
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
- authority-requirement blob, prompt path/blob, full-file digest/size, or
  extracted-body digest/size changes for the same attempt key;
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
- command whitespace/quoting variations create a second attempt;
- authorization/profile variation attempts to unlock a retry;
- inherited `GIT_DIR`, `GIT_COMMON_DIR`, object/alternate-object directories,
  or replace refs attempt to substitute committed authority or receipt roots;
  and
- the requested repository root is valid while a foreign object graph is made
  visible only through ambient Git selectors.

### 9.4 Provider and resource behavior

- stdout or stderr exceeds the cap independently or simultaneously;
- provider exits while reader threads are draining;
- timeout kills the full process group and joins drainers;
- malformed, oversized, non-UTF-8, or trailing provider output;
- returned review names a non-Opus model or mismatched scope;
- the reviewed path, mutable WIP, old Claude path, Codex mirror, or YAML
  frontmatter attempts to replace the descriptor-bound provider body;
- the loaded body claims seat, verdict, mailbox, route, lock, Git, or
  side-effect authority;
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
- an identical public invocation enters after the task is already `published`;
- a fresh exact-byte destination collision is mistaken for crash recovery;
- a publisher crashes after `publishing` but before linking while an unrelated
  exact-byte destination already exists;
- recovery finds the final and a surviving stored candidate hard link, or a
  different file has replaced that candidate basename;
- cancellation receives a stale generation or changed planned tuple;
- no-replace publication races a same-second collision;
- crash occurs before/after the `publishing` transition or atomic link;
- crash occurs before/after object write, index update, stage verification,
  final revalidation, `published`, or stdout emission;
- recovery sees absent, exact, or mismatched final content;
- recovery finds a missing, exact, foreign, clean-filtered, wrong-mode,
  wrong-stage, or wrong-object index entry;
- recovery finalizes an older cross-second path while the shell attempts a
  second staging operation;
- candidate/final symlink, FIFO, directory, mode, link-count, inode-swap, or
  post-link digest mutation;
- candidate CLI path is non-canonical, outside the held directory, or aliases a
  same-named in-directory file;
- file-data fsync fails before link, after link, or during recovery;
- candidate-absent recovery directory fsync fails before the published
  transition;
- primary-root interpreter, gate, import, or common-directory trust is missing
  while an untrusted linked-worktree substitute exists;
- caller `PYTHONPATH`, `sitecustomize`, or adjacent malicious cached bytecode
  attempts to replace the trusted gate/import path;
- hostile PATH-selected Bash, `BASH_ENV`, exported functions, HOME/XDG Git
  config, attributes, clean/smudge filters, or dynamic-loader variables alter
  startup, object bytes, or index selection;
- `ls-tree -z` or `ls-files --stage -z` is parsed through NUL-stripping shell
  command substitution;
- index staging fails while state is `publishing`; and
- primary-checkout activation is attempted without a clean unchanged head,
  fast-forward ancestry, and separate executor authority.

### 9.6 Trigger-production and operator-start authority

- verify-request omits or duplicates event type, reviewed HEAD, reviewed base,
  or descriptor reference;
- verify-request uses an abbreviated or uppercase SHA, a non-canonical scope
  path/digest, a mismatched task ID, or fields inconsistent with its
  filename/envelope;
- event is uncommitted, stale, not strictly after reviewed HEAD, or points to a
  different base/head than the committed descriptor;
- shipping trigger is not the reviewed HEAD, has a non-shipping subject, omits
  or duplicates the descriptor reference, or places it in the commit body
  rather than the terminal trailer block;
- director, implementer, reviewer, capacity action, continuation, or operator
  guidance accepts a named commit or body-free prose as sufficient authority;
- an implementer invents a descriptor reference without explicit parent commit
  authority;
- an operator reconstructs missing fields or silently falls back between
  verify-request and shipping trigger forms;
- Codex-only tests pass while the Claude structural mode lacks either trigger
  form, or vice versa;
- historical reports, handoffs, or plans are treated as fresh trigger
  authority; and
- a cross-repository or evidence-ledger review fabricates Pipeline descriptor
  authority instead of returning to the coordinator's separate bridge route.

### 9.7 Final actual-diff review corrections

The first independent final actual-diff review stopped before provider spend
and identified three remaining adversarial gaps. They are mandatory acceptance
targets for the final implementation head:

- every host-side Git authority read executes the trusted absolute
  `/usr/bin/git`, retains `--no-replace-objects`, and strips every ambient
  `GIT_*` selector; an attacker-controlled `PATH` containing a `git` shim must
  neither select the executable nor observe an invocation;
- two processes starting in two real linked worktrees concurrently derive and
  initialize an initially absent default receipt root and reserve the same
  authoritative scope, without a test-injected `state_root`; a barrier is
  immediately before `ReceiptStore.for_repo`, and the `launch` owner retains
  its lock until the losing nonblocking attempt completes. Both stores resolve
  the primary-root runtime directory, neither worktree-local root is created,
  and the only results are one `launch` and one `attempt_in_progress`;
- crash coverage calls production `review()` and interrupts four distinct
  seams: after real `reserve_or_load` returns `launch` but before provider
  entry, inside the entered provider callable, after the real
  `_validated_provider_result` returns but before persistence, and at the
  actual `receipts.os.replace` call immediately before replacement. Fsynced
  traces from the wrappers, exact child exit codes, the generation-1 reserved
  record, and the pre-replace orphan temporary file are boundary evidence. A
  later exact review degrades to persisted `reviewed/unavailable` receipt
  recovery without entering the provider, and an exact replay stays inert; and
- lifecycle coverage uses the following independent 30-cell oracle for the
  six concrete `LockedAttempt` methods. `invalid` means exact
  `invalid_receipt_transition`; `exact replay` means no write or generation
  change.

| Entry state | `record_review` | `record_reconciliation` | `begin_publication` | `finish_publication` | `cancel_publication` | `recover_publication` |
|---|---|---|---|---|---|---|
| `reserved` | to `reviewed` | invalid | invalid | invalid | invalid | invalid |
| `reviewed` | invalid | to `reconciled` | invalid | invalid | invalid | invalid |
| `reconciled` | invalid | exact replay | to `publishing` | invalid | invalid | invalid |
| `publishing` | invalid | exact replay | exact replay | to `published` | to `reconciled` | `finalize` unchanged or `clear` to `reconciled` |
| `published` | invalid | exact replay | exact replay | exact replay | invalid | invalid |

Changed valid inputs are a separate oracle: reconciliation changes from
`reconciled`, `publishing`, or `published` raise
`reconciliation_replay_conflict`; publication witness changes for begin from
`publishing`/`published`, finish from `publishing`/`published`, cancel from
`publishing`, or recover from `publishing` raise
`publication_replay_conflict`. They do not count as illegal-state cells.

Tests must prove each correction non-vacuously: restoring bare `git`, deriving
state beneath a linked worktree, collapsing crash fixtures to one raise site,
deleting a matrix cell, or permitting one forbidden state/operation edge must
cause a focused failure.
The independent reviewer that found these gaps was a same-model harness; the
final receipt-backed Opus review remains the distinct-model challenge and is
not invoked until these regressions and a new Codex actual-diff review are
green on one unchanged head.

A fresh independent reviewer must challenge this enumeration before the design
commit. Before completion, an independent actual-diff review must verify that
the implemented tests cover these cases. A same-model subagent is acceptable
for design review only when explicitly identified as weaker; the required
post-Lane-V Opus attempt remains the distinct-model implementation review when
the provider is available.

### 9.8 Global uniqueness of shipping scope authority

The next fresh actual-diff review stopped before provider reservation and
identified an ambiguity shared by the bridge and report gate. Both consumers
validated one `Lane-V-Scope:` inside the terminal trailer paragraph but did not
reject an additional canonical `Lane-V-Scope: ` line in an earlier commit-body
paragraph.

A shipping commit is lawful only when its complete decoded message contains
exactly one canonical line beginning `Lane-V-Scope: `. That same sole line must
also be the one exact reference in the terminal Git trailer block, and its
value must continue to match the reviewed descriptor/report authority. A
body-plus-trailer pair is invalid even when both values are identical. The
bridge and report gate must enforce the same rule; paired regressions exercise
the real resolvers, the report gate covers both structural modes, and one
lawful terminal-only positive control proves the correction is not vacuous.

The minimum repair adds the global count beside the existing terminal parser.
It does not introduce a new shared parsing abstraction or alter provider,
receipt, reconciliation, or publication semantics. The one provider attempt
remains unopened until this correction, its task review, the repeated local
verification bundle, and a new whole-branch actual-diff review are green on one
unchanged head.

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
- trusted prompt metadata sensitivity, stored scope binding, and
  same-attempt prompt-drift conflict;
- ambient Git-selector and replace-ref rejection for both authority reads and
  receipt-root derivation;
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
  recovery for final-only, candidate-only, final-plus-candidate, both-absent,
  and mismatched witnesses;
- exact task-publication schema/generation/authority conflicts and public
  published-replay rejection;
- synchronized producer/consumer guidance for both trigger forms and both
  Codex/Claude structural modes, including non-vacuous malformed-to-lawful
  fixture flips;
- capacity-board text, implementer commit conditions, reviewer preflight, and
  exact narrow descriptor-root/digest pins;
- descriptor-relative candidate/final identity, persisted basename/inode
  recovery, exact index OID/mode/stage witness, exact cancellation,
  file/directory/index fsync ordering, and collision rollback;
- object write, exact no-filter stage, NUL-delimited index parsing, exact
  file/blob/index revalidation before finish, explicit resume/status, and every
  post-link crash boundary;
- publisher-returned cross-second path staging plus strict stdout validation;
- absolute privileged-Bash startup and primary-root interpreter/script trust
  with no PATH, startup-file, exported-function, or linked-worktree fallback;
- `send-event` leaves no final event and stages nothing on failure;
- successful candidate validation preserves the envelope; stage failure leaves
  explicit recoverable `publishing` and never reports success; and
- `ci_smoke` needs no private receipt store.

### 10.3 Resource tests

- deterministic constructor cleanup by injecting bind/listen/thread failures;
- bounded concurrent stdout/stderr drains and truncation classification;
- process-group cleanup on timeout and reader failure;
- pure sandbox profile generation and capability-probe classification; and
- descriptor-bound provider prompt metadata and exact rendered argv separation
  from the blind `-p` task prompt.

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

Rollout order for the remaining work is:

1. commit this docs-only amendment without staging paused Task 6 WIP;
2. seed the inert provider-only advisory prompt in an independently reviewed
   prep commit so it exists at the next trusted base;
3. complete and independently review Task 6's file-plus-index transaction and
   recovery paths;
4. complete Task 7's prompt binding, loader switch, rendered regression,
   doctrine, and docs, then independently review its actual diff;
5. after whole-branch review, complete Task 8's active trigger-producer and
   consumer synchronization under its precommitted narrow descriptor;
6. run focused, full, smoke, baseline, doc, and whole-branch checks;
7. perform independent actual-diff review against Section 9, correct any
   blocking finding under a committed amendment, and repeat the review; make
   the one authorized receipt-backed advisory Opus attempt only after PASS and
   only when the capability guard succeeds, preserving an exact degraded reason
   without retry otherwise;
8. return a durable handoff to the coordinator for the separately routed
   evidence-ledger-aware bridge work; and
9. only under separate explicit executor authority, fast-forward and revalidate
   a clean unchanged primary checkout to activate the live `send-event` path.

No mailbox event, live route, cursor, lock, push, or external publication is
part of implementation without its separately triggered authority.

## 12. Consultation And Design Provenance

The pre-plan touches authority, parseable output, schema trust, and a mailbox
side-effect gate, so a guarded ChatGPT Pro consultation was prepared under
consultation ID `1351461e-3d8c-4b25-b1e7-ed5657483d91`. Its first local
execution stopped before sending because sandboxed permission enforcement
could not complete the protected-runtime `fchmod`; this was not a policy or
packet rejection. The corrected scoped runtime invocation succeeded and the
consultation was reconciled. It was not retried after reconciliation.

The reconciled result remained advisory and granted no protocol, verdict,
mailbox, lock, Git, or side-effect authority. No raw consultation prompt or
response is recorded here. The selected amendments rest on sanitized advisory
input, the local implementation audit, the existing Opus contracts, the
user-principal's explicit directions, and the independent adversarial review
required before implementation resumes.

A fresh same-model reviewer challenged the draft independently. This is
explicitly weaker than a distinct-model review. It identified shared-worktree
state, authoritative first-writer scope, self-declared non-Codex bypass, exact
verdict/sender binding, concurrent reconciliation, byte-level Git paths,
publication replay/no-clobber, and infeasible fixture language as material
gaps. Sections 6, 9, and 10 incorporate each correction. After those changes,
the reviewer judged the adversarial enumeration sufficient for design-time use;
the implementation still requires a fresh actual-diff review and the one
authorized Opus attempt when the host can run it.
