# Evidence-Ledger Workbook Normalization Sidecar Design

**Status:** approved design; written specification awaiting user review

**Approved direction:** `HYBRID_LOSSLESS_FIRST` with a hash-bound Excel
sidecar and fail-closed override loader

**Governance home:** Pipeline coordinator route and acceptance contract

**Product target:** `/Users/hyungkoookkim/evidence-ledger`

**Bound refresh plan:**
`8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1`

## 1. Objective

Unblock the governed workbook refresh without guessing business facts. The
system will normalize only 12 cases proved lossless, create a local Excel
sidecar for the 68 direct cases that require owner input, and recompute the 3
dependent monthly-summary controls only after every upstream decision is
complete.

The original incoming workbook, previous canonical workbook, checklist,
canonical database, and canonical resource remain unchanged throughout
sidecar generation and validation. Scratch and canonical apply remain blocked
until a new read-only plan has zero blocking dispositions.

## 2. Approved Authority

The user approved the following authority boundary:

1. Twelve exact cases may be normalized automatically under the rules in
   Section 6.
2. The system may not infer any of the 50 missing payment months or
   automatically split any of the 14 conflicting payment-month groups.
3. The three missing-product rows and one unparseable-date row require explicit
   owner values.
4. The three monthly-summary mismatches are controls, not value sources. They
   are recomputed last and must match detail exactly.
5. Owner decisions live in a separate local `.xlsx` sidecar. Neither source
   workbook is edited or copied into a new authority surface.
6. The planner consumes canonical override JSON produced by a strict sidecar
   validator; it never consumes editable Excel cells directly at apply time.

## 3. Evidence Basis

The blocked read-only plan contains 83 quarantines:

| Class | Count | Lossless automatic coverage | Required disposition |
|---|---:|---:|---|
| Missing placement payment month | 50 | 0 | Owner month for exact group/member hash |
| Conflicting grouped payment month | 14 | 0 | Owner whole-group month or complete member partition |
| Nonnumeric derived cell | 4 | 4 | Approved deterministic rule |
| Consolidation annotation in PPL amount | 2 | 2 | Approved exact-grammar rule |
| Missing required product | 3 | 0 | Explicit owner product |
| Unparseable broadcast date | 1 | 0 | Explicit owner date |
| Stable unheaded cell | 6 | 6 | Approved opaque-preservation rule |
| Monthly-summary mismatch | 3 | 0 initially | Recompute after upstream resolution |

This yields 12 deterministic cases, 68 manual direct cases, and 3 dependent
summary gates. The proposal and decision-matrix hashes are respectively:

- `4b4f22e4da9e942cdd77e48e88e0e5ec0badfcca7db07d393125183e75c699a7`
- `90dbbfa29fe20699d3da68f1ba92adca0b633468f19567ab8cc5da390e4c0c83`

## 4. Architecture

The implementation has four isolated responsibilities:

1. **Correction model:** typed bindings, decisions, normalization audit
   entries, canonical JSON, and validation rules.
2. **Sidecar CLI:** deterministic Excel generation and strict validation into
   canonical override JSON.
3. **Normalization layer:** exact handling of the 12 approved cases plus
   application of validated owner decisions before blocker classification.
4. **Refresh planner integration:** one explicit optional override input whose
   hash and effects become part of the canonical plan.

The flow is:

```text
blocked plan + old/new workbooks + checklist
                    |
                    v
       local owner-correction sidecar.xlsx
                    |
            owner enters 68 decisions
                    |
                    v
        strict sidecar validator
                    |
                    v
       canonical ignored overrides.json
                    |
                    v
     planner + 12 exact normalization rules
                    |
                    v
    recompute 3 summaries -> zero-blocker plan
```

The Excel sidecar is an input form, not authority by itself. The validated
canonical JSON is the only planner input, and its full SHA-256 is bound into
the generated plan and later apply evidence.

## 5. Excel Sidecar Contract

### 5.1 Local artifact

The default ignored output is:

`<routed-worktree>/.superpowers/sdd/workbook-refresh.owner-corrections.xlsx`

Generation is atomic and refuses to overwrite an existing file. A completed
owner workbook is never silently regenerated. The CLI rejects symlinks,
non-regular inputs, path aliases among source and output files, and any input
with more than one hard link.

Workbook protection is an editing aid, not a security boundary. Every protected
value is independently checked by the validator.

### 5.2 Sheets

The workbook contains exactly these visible sheets plus one very-hidden
`_Bindings` sheet:

- `Instructions`
- `Missing_Months`
- `Conflicting_Groups`
- `Missing_Fields`
- `Auto_Resolved`
- `Summary_Gates`

`Instructions` explains the permitted edits, color coding, required approval
fields, and the stop condition for incomplete rows.

`_Bindings` contains the schema version, target commit, plan hash, old/new
workbook hashes, checklist hash, database fingerprint, evidence-chain head,
per-class fact-set hashes, generation timestamp, and a canonical hash of all
protected row data. The validator recomputes every value from supplied source
artifacts; merely unhiding or editing the sheet cannot create authority.

### 5.3 Missing_Months

There is one owner row per exact missing-month group. Protected columns include
group hash, member fact IDs, source references, member count, and local-only
business context. Editable columns are:

- `approved_month` in `YYYY-MM` format;
- `approved_by` as a nonblank owner identity;
- `approval_date` as an ISO date;
- `owner_note`, optional.

One decision covers the complete bound member set. A changed, missing, added,
or duplicated member invalidates the row.

### 5.4 Conflicting_Groups

There is one protected row per group member so an owner can express a complete
partition. Editable columns are:

- `subgroup_id`, either one shared ID for the whole group or stable owner IDs
  for explicit partitions;
- `approved_month` in `YYYY-MM` format;
- `amount_owner`, `YES` or `NO`;
- `approved_by`;
- `approval_date`;
- `owner_note`, optional.

Every bound member must appear exactly once. Each subgroup must have one month
and exactly one amount owner. Divergent months, uncovered members, duplicated
members, or zero/multiple amount owners are blocking.

### 5.5 Missing_Fields

This sheet contains the three missing-product cases and one unparseable-date
case. Protected columns include issue kind, fact ID, source reference, raw
context hashes, and local-only neighboring context. Editable columns are:

- `approved_product` for product cases;
- `approved_broadcast_date` in `YYYY-MM-DD` format for the date case;
- `approved_by`;
- `approval_date`;
- `owner_note`, optional.

The unused value column must remain blank. Formulas are forbidden in all
editable cells.

### 5.6 Audit-only sheets

`Auto_Resolved` lists the 12 deterministic cases, rule code, fact ID, reason,
and effect. It has no editable business fields.

`Summary_Gates` lists the three affected months and their protected fact IDs.
It shows `PENDING_UPSTREAM_RESOLUTION` until the planner recomputes detail. The
sidecar cannot provide a balancing value or override a mismatch.

## 6. Approved Deterministic Rules

### 6.1 Nonnumeric derived cells

Only anomalies in `종합달성률`, `전환률`, or `영업이익` qualify. The parser
preserves the emitted source row, sets the affected derived value to
`null/not_comparable`, and records a nonblocking normalization audit entry.
The rule cannot alter any source amount, write action, or database-derived
direction. Any other field or changed anomaly shape remains quarantined.

### 6.2 PPL consolidation annotations

Only the exact approved `M/D LABEL 합` grammar qualifies. The annotation must
resolve to exactly one emitted row in the same placement group with a numeric
amount. The annotation row retains its allocation relationship, binds the
referenced fact ID, and creates no second placement amount. An absent,
non-unique, different-group, or nonnumeric reference remains quarantined.

### 6.3 Stable unheaded cells

The six approved cells qualify only while source reference, blank column `AG`,
and value hash exactly match both workbooks and the column remains outside all
parser inputs. They are preserved as opaque normalization audit entries and
never enter database fields, evidence amounts, reconciliation totals, or
direction metrics. A new, moved, removed, headed, or changed cell remains
quarantined.

## 7. Canonical Override JSON

The validator writes:

`<routed-worktree>/.superpowers/sdd/workbook-refresh.owner-corrections.json`

The JSON uses a versioned schema and canonical key/order encoding. It contains:

- the complete `_Bindings` projection;
- sidecar SHA-256;
- one typed decision for each of the 68 manual direct cases;
- normalized group/member hashes and approval metadata;
- decision-set SHA-256;
- no formulas or cached spreadsheet calculations.

Validation requires exact completeness: 68 accepted decisions, no unknown
fact IDs, no duplicates, and no partial group. The JSON is written atomically
only after all validation succeeds. Failed validation leaves no usable output.

## 8. Planner Integration

The read-only planner gains one optional argument:

`--normalization-overrides <canonical-json-path>`

Without the argument, current behavior is unchanged and all 83 cases remain
blocking. With the argument, the planner:

1. validates schema and all source/plan/database/evidence bindings;
2. applies the 12 deterministic rules to the exact bound fact sets;
3. applies owner decisions only to their exact fact IDs and member sets;
4. regenerates component facts and action classifications;
5. recomputes the three monthly summaries last;
6. records normalization and owner-decision audit entries in the plan;
7. includes the override JSON hash in canonical plan bytes.

The planner never edits either workbook. Summary values cannot create detail,
allocate residuals, or repair a mismatch. If any upstream case remains
unresolved or a summary remains unequal, the plan is blocking.

The applier accepts no new sidecar argument. It receives only the canonical
plan, whose hash already binds the validated override JSON and normalization
audit.

## 9. Fail-Closed Behavior

Generation or validation stops on:

- stale target, plan, workbook, checklist, database, evidence, class, group,
  member, protected-row, or sidecar hash;
- missing sheets, changed headers, hidden data rows, extra nonempty rows, or
  formulas in editable cells;
- blank approval fields or malformed dates/months;
- unknown, missing, duplicated, or multiply assigned facts;
- incomplete or overlapping partitions;
- subgroup month disagreement or zero/multiple amount owners;
- deterministic cases outside their exact allowlist, grammar, or stability
  proof;
- any remaining monthly-summary mismatch after recomputation.

Errors identify sheet, row, protected fact hash, and rule code without copying
business values into tracked logs or mailbox events.

## 10. Testing And Review

### 10.1 Synthetic tests

Tests build synthetic workbooks and sidecars with `openpyxl` and prove:

- deterministic workbook bytes or a documented canonical content model;
- exact sheets, headers, protections, data validations, frozen panes, and
  editable-cell allowlist;
- round-trip generation, owner completion, validation, canonical JSON, and
  planner integration;
- rejection of missing decisions, formulas, invalid dates/months, duplicates,
  incomplete partitions, multiple amount owners, and every binding mutation;
- no source workbook modification;
- no duplicated amount for consolidation annotations;
- no business effect from derived or unheaded-cell normalizations;
- unchanged planner output when no override argument is supplied.

Each of the 12 deterministic cases has a non-vacuous mutation test that changes
one load-bearing predicate and restores quarantine.

### 10.2 Governed real-data gates

After implementation, review, and synthetic tests:

1. Generate the ignored real correction workbook from the bound blocked plan.
2. Prove it inventories exactly 68 manual cases and 12 audit-only automatic
   cases without changing canonical fingerprints.
3. Stop for owner completion of the 68 editable decisions.
4. Validate the completed sidecar into canonical ignored JSON.
5. Rerun the planner read-only and require zero blocking dispositions.
6. Require exact equality for all three summary controls.
7. Reprove unchanged canonical database/resource fingerprints and clean git.
8. Only then request a new Task 7 scratch executor token and cumulative
   Operator verification.

No seat may fill owner fields by heuristic or treat spreadsheet protection as
approval.

## 11. Privacy And Publication

The sidecar, override JSON, regenerated plans, and reports are ignored local
artifacts. They may contain the business context needed for an owner decision.
Tracked code, specs, tests, docs, mailbox events, and review reports contain
only synthetic fixtures, hashes, reason classes, and counts.

No workbook, correction sheet, override JSON, report, dump, credential, or
business value may enter git. Push, merge, remote publication, deployment,
paid services, and remote database mutation remain out of scope.

## 12. Acceptance Criteria

The design is satisfied only when:

1. The source and canonical workbook hashes are unchanged by generation and
   validation.
2. Exactly 12 bound cases normalize automatically and any predicate mutation
   restores quarantine.
3. The generated sidecar inventories exactly 68 manual direct cases and the
   validator refuses incomplete owner input.
4. Completed owner decisions produce one canonical, hash-bound override JSON
   with complete group coverage.
5. The regenerated plan has zero blocking dispositions and three exact summary
   controls.
6. The plan records normalization/owner-decision audit entries and binds the
   override hash.
7. Scratch and canonical execution remain impossible before all preceding
   gates pass.
8. All tracked artifacts remain free of real workbook contents and business
   values.

## 13. Explicit Non-Goals

- Editing, annotating, or copying the incoming workbook into a new authority
  surface.
- Inferring payment month from broadcast date, row order, summary totals,
  majority/first value, previous workbook, or database placement.
- Automatically partitioning conflicting groups.
- Using monthly summaries to create or balance detail.
- Allowing the apply command to read editable Excel.
- Proceeding with partial owner decisions or unresolved quarantines.
- Refactoring unrelated parser, planner, database, resource, or reporting code.
