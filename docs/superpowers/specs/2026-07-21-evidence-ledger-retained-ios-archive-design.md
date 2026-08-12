# Evidence-Ledger Retained iOS Archive Design

**Status:** User-approved design on 2026-07-21.

## Context

The evidence-ledger repository still contains a read-only SwiftUI client and
describes it as supported, locally verified, and potentially eligible for a
future macOS CI lane. The active product is the Windows PWA, and the user has
decided that the iOS client will not be built or used.

An audit found that `biz.slot_pnl.commission_model` may be NULL while the
retained Swift model requires a non-optional `String`. That mismatch remains a
real limitation of the archived code, but it is no longer an active-product or
beta acceptance defect. Repairing it, creating simulator infrastructure, or
reviving the iOS verification lane would spend effort on an abandoned surface.

## Decision

Retain the complete `ios/` tree as unsupported archive/reference code. Do not
delete, repair, regenerate, build, test, or claim compatibility for it.

Make repository-facing truth match that boundary:

- the Windows PWA is the active client and beta surface;
- the retained iOS source is historical reference material only;
- no current schema compatibility, buildability, runtime behavior, support,
  or release assurance is promised for the archived client;
- iOS is absent from default setup, local verification, CI, beta, and release
  workflows; and
- historical iOS evidence may remain only when explicitly labeled historical
  and non-current.

This decision supersedes the executable iOS NULL-coherence portion of
`docs/superpowers/plans/2026-07-21-evidence-ledger-dormant-ios-null-coherence.md`.
That document and its route history remain immutable audit evidence; they no
longer authorize Swift, XCTest, simulator, or generated-project work.

## Target Change Boundary

The target correction may change exactly these five tracked paths:

- `README.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`
- `scripts/ci_local.sh`
- `.github/workflows/ci.yml`

Every tracked path under `ios/` is read-only. No package, lockfile, schema,
Python import, web application, generated project, service, or private-data
path may change.

## File Responsibilities

### `README.md`

State the product boundary near the opening status text. Remove iOS from the
supported-client claim, default prerequisites, quickstart, and local test
summary. Keep one concise pointer to `ios/` as unsupported archived source so
its continued presence is not mistaken for deletion or active support.

### `ARCHITECTURE.md`

Preserve factual source inventory and historical architecture descriptions,
but label the iOS subsystem and dependency entries as archived and unsupported.
State that the model may drift from the current database schema and that the
repository does not assert current decode, build, or runtime compatibility.
Remove current-verification and recurring-lane claims. Historical test results
must be explicitly dated and described as historical evidence only.

### `OPERATIONS.md`

Remove Xcode, XcodeGen, simulator, iOS configuration, iOS troubleshooting, and
iOS execution from current prerequisites, installation, default operation,
local verification, CI expectations, and release procedures. A short archive
notice may identify where the retained source lives, but it must not provide an
active build or support workflow.

### `scripts/ci_local.sh`

Run only the current database and import verification scripts. Remove the
conditional Xcode project detection, simulator destination, XCTest invocation,
and skip message.

### `.github/workflows/ci.yml`

Change comments only. Remove the future macOS/iOS job stub and any claim that
iOS merely waits for runner budget. State concisely that the archived client is
outside current CI scope. Do not add, remove, or alter an executable CI job.

## Verification Design

No Xcode, XcodeGen, simulator, Swift, or XCTest command belongs in acceptance.
The change is accepted through repository-truth and scope checks:

1. documentation anchors and references validate;
2. architecture freshness validates against target parent
   `1ad4eb2b5550af7c3941aacf08240559a9051193`;
3. evidence-ledger smoke ends in `OK`;
4. the actual target diff contains exactly the five allowed paths;
5. the actual target range contains no tracked `ios/` change;
6. the `ios/` tree still exists at the reviewed head;
7. `scripts/ci_local.sh` contains no Xcode or simulator invocation;
8. executable CI job topology is unchanged; and
9. the target worktree is clean after one scoped documentation/harness commit.

Any formatter, anchor fixer, or verification command that changes an
additional path is a stop condition. Any wording that presents iOS as current,
supported, beta-eligible, release-eligible, or merely awaiting CI budget is a
review failure.

## Governance and Sequencing

Director continues the effective autonomous contract at
`coordination/mailbox/sent/2026-07-20T20-26-28Z-director-to-all-coordination.md@f0c0459e20c2231e576b37778d0d7cac6ae44220`
with revision 2 and the revised archive outcome. The existing clean target
worktree and branch may be reused at the accepted parent.

Director authors one exact five-path target commit and publishes one canonical
actual-range verify-request. Non-author Operator2 on `gpt-5.6-terra` is the
only assigned verdict issuer. A GO makes the range eligible for separately
authorized local integration; it grants neither integration nor remote
publication.

After this archive-boundary correction is independently accepted, remediation
continues with the non-iOS parser, import/database, and CI truthfulness packets.

## Explicit Non-Goals

- Fix nullable Swift decoding or render `미정`.
- Add or modify an XCTest.
- Create, boot, shut down, or delete a simulator.
- Generate or modify an Xcode project.
- Delete or reorganize any retained iOS source.
- Promise future iOS support or revival.
- Change database, import, web, dependency, or service behavior.
- Integrate into target main or update any remote reference.
