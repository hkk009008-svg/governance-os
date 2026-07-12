# Design-Time Independent Enumeration: PPL Evaluation Adversarial Surfaces

When: 2026-07-12T03:49:00Z
Coordinator: Codex
Target cycle: `ledger-ppl-recommendation-evaluation-2026-07-12`
Binding doctrine: `docs/protocol/claude/independence-first.md` (R-INDEPENDENCE)
Approved target plan SHA-256:
`25ae717f9f0256565b350d3fae9a22c557928463fcbab4950becdc9512c08018`

## Independence Statement

This is the committed design-time abuse/edge-case enumeration required before
implementation of trust-granting parsers, canonical serialization/rendering,
authority enforcement, and side-effect/path gates. It is produced from the
approved plan plus three independent Codex plan passes with distinct questions:
data architecture/replay, evaluation methodology/authority, and
integration/signature composition.

It is cross-model evidence only when the implementation author/controller is a
different harness, such as Claude. If the implementation author/controller is
Codex, this artifact does not by itself discharge R-INDEPENDENCE; that Director
must obtain a non-Codex design-time review before starting the adversarial tasks.

## Enforced-And-Tested Coverage Targets

### Task 1 — strict authority and trust-granting schema

- Reject missing and unknown keys at every nested object; no permissive
  normalization or business-policy defaults.
- Reject bool-as-int, string-coerced IDs, numeric money, nonfinite Decimal,
  naive/non-UTC time, malformed/lowercase-invalid SHA-256, duplicate manifest
  hashes, duplicate family membership, duplicate/overlapping time bands, and
  selective floors below the active floor.
- Canonicalize only explicitly unordered collections; prove input permutation
  cannot change authority bytes/hash.
- Treat a caller-computed candidate-set hash as insufficient authority. The
  whole canonical candidate universe, including enumeration metadata, costs,
  and availability records, must be named by the reviewed authority bundle.
- Mutation target: change an availability source and recompute the inner
  candidate hash; the unchanged approved authority must still reject it.

### Tasks 2 and 7 — database snapshot, canonical loader, and replay

- Fixed SQL is read-only and all snapshot/evidence/refresh queries share one
  repeatable-read transaction; a concurrent evidence write must not create a
  mixed-state snapshot.
- Select the unsuperseded result-chain head first. A later provisional head
  must not resurrect a superseded settled ancestor as outcome evidence.
- Seal every formula-relevant slot/result/placement/allocation value and bind a
  mutable-values SHA-256. Reject stale hashes, pretty/noncanonical bytes,
  unknown keys, malformed types, and timezone-invalid timestamps.
- Replay must use only sealed bytes. Mutating source commission, placement, or
  allocation rows afterward must leave replay bytes identical while a fresh
  snapshot hash changes.
- Render only whitelisted structured claims and fixed warning templates; do
  not interpolate untrusted free-form source text into parseable Markdown or
  claim causal/counterfactual outcomes.

### Tasks 3 and 4 — money math and numerical determinism

- Resolve exactly one distinct internal PPL program; aggregate multiple rows
  for the same program once; exclude zero/multiple programs; never include the
  agency lane in P&L.
- Add back historical internal allocation exactly once and subtract the
  prospective allocation exactly once.
- Set Decimal precision, quantum, and rounding from reviewed formula authority.
  Mutating ambient Decimal rounding must not change a non-divisible result.
- Compare quantized Python recomputation with the database view and fail closed
  on mismatch or missing formula inputs.
- Keep future-outcome predictive intervals and estimator uncertainty in
  distinct types and fields.

### Task 5 — fail-closed decision authority

- Reject incomplete or duplicate universes, duplicate/missing evaluation rows,
  exact cost/opportunity mismatch, future-known costs, wrong family/version,
  wrong authority hash, and unscorable material candidates.
- `HOLD` is reachable only for a complete, adequately scored, reliably
  nonpositive universe; weak/incomplete/tied evidence must abstain.
- An `approved_horizon` requires owner-approved component authority,
  authoritative enumeration before cutoff, self-consistent candidate-set hash,
  authoritative per-candidate availability/cost records, and exact membership
  of the whole universe-manifest hash in reviewed authority.
- No state can set `actionable=true`, `activation_eligible=true`, invent an
  unobserved alternative outcome, or emit an unstructured claim.

### Tasks 6 and 7 — retrospective evaluation artifacts

- Exclude same-date peers from training and label chronology
  `broadcast_order_only_not_as_known`.
- Bind snapshot, authority, source revision, formula precision/quantum/rounding,
  policy, and data-quality version into canonical evaluation bytes.
- Bind data-quality review to the exact snapshot SHA, evidence-chain head, and
  refresh-evidence ID; any one-field stale binding must reject.
- Selective-risk floors are active-or-stricter only; coverage denominator
  includes all eligible targets, including abstentions.

### Task 8 — CLI path, hash, and output side-effect fences

- Expose only `snapshot` and `evaluate`; no live/recommend/activate command.
- Resolve paths before classification. Reject repository-internal business
  input/output paths outside ignored `data/` or `.superpowers/`; cover
  traversal and symlink resolution rather than string-prefix checks.
- Validate reviewed snapshot and authority SHA-256 before writing evaluation
  output; reject noncanonical snapshot bytes.
- Open PostgreSQL with read-only, repeatable-read options and keep stdout free
  of business values.
- Every output remains local/ignored or outside the repository and includes
  `actionable=false activation_eligible=false`.

## Required Per-Task Independent Checks

For every task above that implements an adversarial surface, the committed diff
must receive an independent review against this enumeration before the task is
marked done. Cross-model review is required when author and available reviewer
would otherwise share the same model/harness. Review reports must identify the
reviewer harness and cite the exact commit/range and enforced tests.

## Exclusions

This artifact does not authorize implementation, commit, database access,
resource/workbook mutation, advice activation, push, merge, publication,
cleanup, cursor use, locks, paid spend, or any seat verdict. It records
design-time coverage targets only.

## Exact Next Trigger

The coordinator route binds this enumeration. The live Director confirms
harness independence, then folds these targets into task briefs and per-task
review prompts before implementing any named adversarial surface.
