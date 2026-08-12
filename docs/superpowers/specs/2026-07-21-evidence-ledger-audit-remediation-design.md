# Evidence-Ledger Audit Remediation Design

**Date:** 2026-07-21
**Status:** User-approved design; implementation not started
**Coordinator role:** non-production design and routing only
**Target repository:** `/Users/hyungkoookkim/evidence-ledger`
**First target parent:** `1ad4eb2b5550af7c3941aacf08240559a9051193`
**Remote tracking state at design time:** local `main` is 34 commits ahead of
`origin/main@cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47`

## Purpose

Correct the confirmed audit defects without treating unbound hypotheses as
implementation authority. Preserve the dormant iOS source, prevent parser and
import data loss, make import identity and owner decisions fail closed, and
strengthen CI evidence without adding frameworks or unrelated architecture.

The implementation is split into four sequential packets. Each packet starts
from the previously accepted integrated target head, carries its own TDD cycle,
and requires an immutable verify-request plus non-author Operator2 GO before
local integration.

## Chosen Approach

Use four independently reviewable packets:

1. dormant iOS NULL coherence;
2. parser loss and normalization;
3. import and database invariants;
4. CI and gate truthfulness.

Two broader waves would reduce route count but mix Swift, Python, database,
and CI failure modes. One combined patch would make review, rollback, and
finding attribution unnecessarily difficult. The four-packet design is the
smallest structure that keeps each trust boundary independently testable.

## Global Constraints

- Preserve `/Users/hyungkoookkim/evidence-ledger/.vscode/` byte-for-byte and
  untracked.
- Do not delete the iOS tree.
- Use only synthetic fixtures; do not use the private workbook or live business
  values.
- Do not install dependencies or introduce an agent, event-sourcing, retry,
  telemetry, or other framework.
- Do not start services, access a managed database, activate policy, book,
  spend, deploy, merge, push, consume a cursor, or claim a protocol lock unless
  the exact external effect receives separate user authority.
- Preserve existing database rows. No migration or rewrite of historical
  `source_ref` values is part of this work.
- Conditional audit claims, including merged-cell package behavior and current
  production activation impact, remain out of scope until separately bound to
  executable evidence.

## Packet 1: Dormant iOS NULL Coherence

The iOS source is retained for reference or future revival, but it is not an
active product, beta surface, recurring release target, or required beta gate.
This packet performs one bounded coherence correction before the tree is
treated as dormant:

- decode `commission_model` as optional;
- expose one Korean display value that renders NULL as `미정`;
- use that display value in both list and detail surfaces;
- add one NULL decoding/rendering fixture while retaining known-value coverage;
- state in the repository's product/architecture guidance that iOS is dormant
  and excluded from active beta claims and recurring release verification.

No broader Swift refactor, UI improvement, dependency change, or renewed iOS
product work is permitted. The focused NULL test is required for this packet;
future packets do not inherit a recurring iOS gate.

## Packet 2: Parser Loss and Normalization

### Internal date parsing

An impossible calendar date such as `02/30` must not raise an uncaught
`ValueError`. It becomes a typed, source-referenced `unparseable_date` anomaly,
is included in scan/drop accounting, and is excluded from materialized rows.

### Agency time parsing

Three- and four-digit tokens are interpreted as `HHMM`:

- `930` becomes `09:30`;
- `2500` becomes `01:00` with a next-day bump;
- a token with an invalid minute or an unsupported hour never becomes a
  fabricated time. It remains unlinked and produces a loud anomaly.

### Evidence-bearing blank coordinates

A row with neither date nor broadcast/channel is quiet only when the row is
genuinely empty. If it carries cost, PPL, product, company, agency, or issue
evidence, the parser emits a typed anomaly containing the source reference and
available evidence. The row cannot acquire a slot key and is not materialized,
but it never disappears silently.

### Exact fractional cost

Agency cost is parsed as an exact decimal amount in 만원 and converted to an
integer KRW amount without truncation. For example, `437.5만원` becomes
`4,375,000원`. Values that cannot represent a whole KRW amount fail loudly;
binary floating-point rounding is not an accepted conversion mechanism.

### Placement identity and supersession

Collapse identity consists of:

1. family;
2. air date;
3. normalized channel;
4. normalized start time;
5. per-row product identity;
6. PPL show;
7. PPL qualifier;
8. producer/agency identity.

Cost and free-text issue notes are not identity fields. A newer row supersedes
an older row only when this complete identity matches. Distinct PPL shows or
producers sharing one broadcast slot both survive. This is the user's explicit
owner ruling for the remediation.

### Parser tests

Hermetic synthetic tests cover impossible dates, three- and four-digit times,
invalid minutes/hours, evidence-bearing blank coordinates, exact fractional
cost conversion, two identities sharing one slot, and same-identity latest
mention supersession.

## Packet 3: Import and Database Invariants

### Immutable source identity

New internal-import source references include the full workbook SHA-256,
sheet, and row. Two workbook versions can no longer collide at a yearless
`방송스케줄!rN` identity. Reconciliation queries the exact source reference
emitted for the current import. Existing rows are neither rewritten nor
backfilled.

### Alias conflict detection

Before entity materialization, the loader compares every proposed alias with
the existing database mapping:

- absent alias: insert the approved mapping;
- same alias and same entity: accept as idempotent;
- same alias and different entity: abort the complete import with both the
  existing and proposed identities in the error evidence.

`ON CONFLICT DO NOTHING` must not conceal a contradictory owner decision, and
the loader must not silently remap an existing alias.

### Negative cost

A negative agency cost becomes a typed parser anomaly and a pre-database import
blocker. It must not reach a nonnegative database constraint after partial
work. No refund/credit semantics are inferred by this remediation.

### Checklist preservation

Checklist proposal uses exclusive creation. If the requested path exists, the
command stops without changing any byte. The operator chooses a new path;
there is no automatic overwrite flag for an owner-signed checklist.

### Transaction boundary and tests

All preflight failures occur before materialized database writes. Once writes
begin, the existing one-transaction rollback contract remains authoritative.
Hermetic tests cover source identity across workbook versions, alias absent /
same / contradictory mappings, negative-cost preflight, and checklist byte
preservation. Database integration tests may run only against a separately
authorized synthetic local stack.

## Packet 4: CI and Gate Truthfulness

- Add `import/tests/test_checklist_coverage_unit.py` to the hermetic import CI
  lane and update the lane's count/description.
- Replace R4's free-text `--runxfail` substring witness with a fixed executable
  regression-pin runner.
- Require CI to invoke that runner through one exact, non-comment, single-line
  `run:` command. R4 validates this structural invocation and the runner's
  executable pytest command; comments alone cannot satisfy it.
- Add negative tests proving comments, step names, and unrelated strings do not
  satisfy R4.
- Leave the architecture-freshness mechanism unchanged. It is active and
  passing against the current unpublished range; documentation must state that
  evidence truthfully rather than change code to manufacture gate activity.

This packet runs the ceremony tests, the exact workflow checks, the newly
included checklist test, and project smoke.

## Data and Error Flow

Input parsing produces normalized values plus typed anomalies. Evidence-bearing
rows may be rejected or left unlinked, but they are never silently discarded.
Pre-database validation then checks exact cost semantics, complete checklist
coverage, immutable source identity, and negative-cost policy. Transactional
validation checks existing alias truth before any conflicting entity mapping
can be materialized. Reports and append-only evidence continue to record the
complete accepted warning/anomaly sets under the existing import contract.

No layer converts an unknown or invalid value into an invented valid value.
Recoverable uncertainty is displayed or reported in Korean (`미정` or a typed
warning); structurally unsafe input blocks the import with source provenance.

## Review and Integration

For each packet:

1. Director binds ownership to the exact accepted evidence-ledger parent and
   uses a dedicated isolated target worktree.
2. Director writes failing regression tests before the smallest implementation.
3. Director runs the packet-specific focused suite and the applicable broader
   hermetic/smoke profile.
4. Director commits one independently reviewable target range and publishes an
   immutable verify-request naming all finding references.
5. Non-author Operator2 on a different model reviews the actual range and
   issues GO, NITS, or FAIL.
6. Only a GO range becomes eligible for separately authorized local
   integration. The next packet binds to that accepted integrated head.

Route publication, implementation, verification, local integration, and remote
publication remain separate events. This design authorizes none of them by
itself.

## Completion Criteria

The remediation is complete only when all four packets have independently
accepted ranges and the integrated target state proves:

- dormant iOS NULL decoding is coherent and clearly non-product;
- all five reproduced parser loss/normalization cases are closed by tests;
- distinct placements on one slot survive while true same-identity updates
  supersede deterministically;
- new imports use immutable source identity;
- contradictory aliases and negative costs fail before materialized writes;
- existing checklists cannot be overwritten by proposal;
- checklist coverage executes in CI;
- R4 cannot be satisfied by comments; and
- no real/private data or unauthorized external effect was used.
