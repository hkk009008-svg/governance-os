# Capability V1 Shadow Adapter Phase 2B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to execute this plan task-by-task
> and `superpowers:test-driven-development` for every task. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Complete the remaining Phase-2 gate with one read-only v1 history
adapter and one deterministic parity corpus that block both unsafe permission
expansion and unnecessary capability reduction, while v1 remains the only
authority.

**Architecture:** Add one adapter module between host-normalized legacy records
and the existing pure reducer. Route/work history becomes route-v2 shadow
events; verification, capability, effect, ChatGPT, Opus, and provider lifecycle
values remain specialized observations with an explicit `no_route_event`
disposition. One strict committed corpus binds every existing mapping row, all
Phase-2 misuse vectors, the complete reducer replay manifest, actor/scope
fixtures, source identities, and expected parity. The adapter never reads live
mailbox/ref/route state, writes v1 state, emits authority, or activates a
writer.

**Tech Stack:** Python frozen dataclasses, RFC-8785 bytes from
`threeway.canon.canonicalize`, the existing `capability_reducer` and
`compact_state_mapping` contracts, strict JSON parsing, JSON replay fixtures,
pytest.

## Global constraints

- The approved design source is
  `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
  Sections 3, 4, 8, 9, and 10. ChatGPT Pro consultation
  `2540c043-c177-4017-aa1b-0c3d3453ffa9` already resolved this unchanged
  adapter/divergence question; do not dispatch a duplicate consultation.
- Version 1 remains the only authority. Every adapted event has epoch `0`, and
  the only activation object is `ActivationState(epoch=0, mode="shadow")`.
  Add no activation argument, flag, ref, writer, CAS, or configuration change.
- Preserve the specialized-store boundary. Only capacity route/work history and
  the `cancelled`/`superseded` work dispositions can emit route-v2 events.
  Capability, local/provider verdict, ChatGPT, Opus, `failed`, and
  `outcome_unknown` values must have an explicit `no_route_event` disposition.
- The adapter consumes host-normalized identity and scope bindings. Legacy
  prose, filenames, role labels, environment variables, CLI identity flags,
  and payload fields cannot mint a principal, infer a scope, or choose an
  epoch.
- “Full Phase-2 corpus” means exactly: all rows exposed by the committed v1
  state-mapping fixture; every misuse vector whose `enforcing_phase` is `2`;
  all reducer replay vectors and their pinned permutations; plus an explicit
  deferred set containing every misuse vector whose `enforcing_phase` is `3`.
  No count may be hard-coded as a substitute for set equality.
- Current evidence, verified with the committed fixtures, is 69 mapping rows
  across 7 domains, 8 Phase-2 misuse vectors, 3 deferred Phase-3 vectors, and
  19 reducer vectors with 31 pinned permutations; the complete corpus has 89
  cases. The final gate must derive these values again and persist its
  deterministic count/digest report under `logs/capability-first/`;
  fixture-set equality, not these prose numbers, is authoritative.
- Parity compares route-event disposition, terminal/retry meaning,
  `advisory_only`, and effect eligibility. More-permissive and more-restrictive
  divergences both block. Formatting-only/non-authority differences may be
  reported but do not block.
- Unknown versions, fields, values, contexts, identities, digests, scopes,
  causal revisions, duplicate IDs, mixed v1/v2 input, unmanifested cases, or
  silent skips fail closed with one stable adapter error and no partial result.
- Evidence refs, including `web:` refs, remain validated opaque strings. The
  adapter never parses, fetches, freshness-scores, trusts, or converts them into
  verdict/effect authority.
- `scripts/capability_reducer.py` remains pure. It never imports the adapter and
  gains no filesystem, Git, mailbox, ref, environment, clock, random, cache,
  network, subprocess, provider, or writer call.
- Use one new production module and one new corpus fixture. Do not add a store,
  framework, plugin registry, live reader, migration writer, second gate
  service, or generic event abstraction.
- Each task uses RED -> minimal GREEN -> focused regression -> one commit. All
  Git and pytest commands use `env -u GIT_INDEX_FILE`.
- Before Task 1, commit this plan and obtain one independent design review of
  the abuse matrix. After Task 3, obtain one independent review of the exact
  implementation range. Do not repeat either question on an unchanged range.
- No push, merge, mailbox/cursor mutation, provider call, spend, activation, or
  live protocol-state write is part of this plan.

## Existing consultation and independent design resolution

The existing Pro advisory recommended one in-place reducer, read-only
compatibility adapters, shadow parity, and a single later activation epoch. It
rejected a second authority store, universal review, global invalidation, and
opportunistic provider fallback. This plan applies the unchanged recommendation
without another send.

A fresh read-only Codex reviewer inspected HEAD
`f17d14c684e1e1a6378e52ab8f151070fb710e07` and found four design ambiguities.
This plan resolves them before implementation:

1. it defines the complete corpus as exact source sets and manifests rather
   than treating one-value coverage as historical completeness;
2. it separates route/work events from specialized lifecycle observations and
   forbids a fallback `UPDATE` for specialized state;
3. it defines a gate-only semantic projection because `KernelReport`
   intentionally exposes no GO, DONE, verdict, terminality, or effect field;
4. it requires stable source identity, causal revision, host-resolved actor,
   immutable scope, and content/dependency/acceptance/evidence digests instead
   of inferring them from legacy prose or directory order.

The review also requires non-vacuous probes for missing corpus entries, both
parity directions, opaque web evidence, mixed versions, resolver drift, and an
injected reducer I/O/import. These are assigned below. A follow-up read-only
review checked the four corrections—canonical output ordering, executable
misuse binding, independent compact projection, and independent work/unit
cursor axes—and returned `APPROVED`, with no remaining Critical or Important
finding.

## File map

| File | Responsibility |
|---|---|
| `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md` | This reviewed execution contract. |
| `scripts/capability_reducer.py` | Existing pure reducer plus one real-caller transition cursor; no adapter import or I/O. |
| `scripts/capability_v1_adapter.py` | Strict v1 record parser, route/work adapter, specialized-state dispositions, parity gate, and fixture-only CLI. |
| `tests/fixtures/compact_kernel/v1_to_v2_replay.json` | Exact source/digest manifest, actor/scope fixtures, legacy records, case manifest, parity oracle, Phase-2 misuse set, Phase-3 deferred set, and reducer replay set. |
| `tests/unit/test_capability_v1_adapter.py` | Adapter, completeness, parity, determinism, denial-asymmetry, and CLI tests. |
| `tests/fixtures/compact_kernel/v1_surface_inventory.json` | Read-only historical-adapter and pure-reducer ownership classification. |
| `tests/unit/test_compact_kernel_surface_inventory.py` | Exact ownership, helper-class, no-writer, and import-closure assertions. |
| `tests/unit/test_capability_reducer.py` | Transition-cursor boundary tests and reverse-import/non-vacuous purity probes. |
| `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md` | Phase-2 completion evidence only after all gates pass. |
| `ARCHITECTURE.md` | Current pure-reducer/adapter topology and non-authority invariant. |
| `logs/capability-first/phase2b-shadow-parity.json` | Deterministic count/digest/divergence evidence produced from the committed gate. |

## Exact interfaces

Add this one reducer helper:

```python
def transition_cursor(
    state: object,
    *,
    work_id: object,
    unit_id: object,
) -> tuple[int, int, str]:
    """Return next_work_revision, expected_unit_version, precondition_digest."""
```

The helper validates `KernelState`, `work_id`, and nullable `unit_id` through
the existing reducer boundaries. Its axes are independent: next revision comes
from the matching work (`1` when absent, otherwise current revision + 1), while
version/precondition come from the exact `(work_id, unit_id)` (`0` plus the
canonical zero-state precondition when absent, otherwise the unit's current
version and stored precondition). This covers an existing work with a new null
or named unit without borrowing another unit's state. It returns no
authority-bearing value and performs no I/O.

The adapter public surface is exactly:

```python
class LegacyAdapterError(ValueError):
    code: str


def adapt_v1_history(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[capability_reducer.TransitionEnvelope, ...]:
    """Return only fully validated, reducer-accepted shadow envelopes."""


def main(argv: list[str] | None = None) -> int:
    """Check one committed corpus and print its sanitized canonical report."""
```

`LegacyAdapterError.code` is one of:

```text
legacy_invalid
legacy_version
legacy_unmapped
legacy_ambiguous
legacy_nondeterministic
parity_divergence
```

Every normalized record has exactly these keys:

```text
schema
source_id
source_digest
work_id
route_id
work_revision
unit_id
actor_binding_digest
domain
value
context
mutable_scope_ref
mutable_scope_digest
content_digest
dependency_digest
acceptance_digest
evidence_refs
verification_ref
effect_reservation_refs
```

`schema` is exactly `compact-kernel-legacy-observation/v1`. This names the
host-normalized, non-authoritative adapter input without reusing or implying
the authoritative `governance.route/v1` contract. Task 1 accepts no other
schema literal.

The adapter derives `transition_id`, `requested_transition`,
`expected_unit_version`, `precondition_digest`, and `activation_epoch`; those
keys are forbidden in input. `source_digest` is the canonical SHA-256 of the
other exact record fields after context-key normalization and lexical
normalization of the unique `evidence_refs` and `effect_reservation_refs`.
Adding, removing, or changing a reference changes source identity; reordering
the same unique references does not. `transition_id` is derived from stable
`source_id`, not content or input order, so an identical replay is idempotent
and changed content under the same source identity conflicts. After causal
validation and in-memory application, returned envelopes are canonically
sorted by `(work_id, nullable-unit tag, unit_id, work_revision,
transition_id)`. Reversing independent input records therefore yields the same
tuple; reversing a causal same-work history remains an error rather than being
silently repaired.

The route/work mapping is total and has no fallback:

| v1 observation | route-v2 request |
|---|---|
| capacity `ready` or `active`, new unit | `START` |
| capacity `ready` or `active`, existing unit | `UPDATE` |
| capacity `blocked` deriving `WAIT` | `BLOCK` |
| capacity `blocked`/`done` deriving `REVIEW` | `REQUEST_REVIEW` |
| capacity `blocked`/`done` deriving `DONE`, or `excepted` | `REQUEST_CLOSE` |
| work `cancelled` | `CANCEL` |
| work `superseded` | `SUPERSEDE` |
| every other current mapping row | explicit `no_route_event`; passing it to `adapt_v1_history` raises `legacy_unmapped` |

The compact-side semantic projection is an independent private production
table, not a second call to the v1 mapping oracle:

```python
@dataclass(frozen=True)
class _AdapterRule:
    requested_transition: str | None
    compact: str
    terminal_scope: str
    next_action: str
    effect_eligibility: str
    advisory_only: bool


_ADAPTER_RULES: tuple[
    tuple[tuple[str, str, tuple[tuple[str, bool | str], ...]], _AdapterRule],
    ...,
]
```

The key is exact normalized `(domain, value, sorted context items)`. The table
is closed over every accepted current context branch. A route rule's
`requested_transition` must equal the actual emitted envelope; a specialized
rule must have `None` and emit no envelope. `_compact_projection()` reads only
the actual selected rule plus the emitted-envelope/no-event result. It may not
call `compact_state_mapping.meaning_for()` or load fixture expectations.

The gate performs a three-way comparison:

1. v1 golden projection from the bound state-mapping fixture;
2. current v1 result from `compact_state_mapping.meaning_for()`; and
3. actual compact result from `_compact_projection()`.

The corpus case carries a separately committed expected compact projection as
a review oracle, so fixture or production-table changes cannot silently bless
each other. Mutation tests change `_ADAPTER_RULES` while leaving both fixtures
and `meaning_for()` fixed.

The fixture-only CLI is:

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
```

It has no live-directory scan, fix, activation, actor, scope, mode, writer,
network, mailbox, ref, provider, or general output-path option. It prints one
canonical sanitized JSON report containing only schema/mode, source and report
digests, derived set counts, case IDs by divergence class, and the deferred
Phase-3 IDs. Exit `0` means every blocking divergence list is empty; exit `1`
means malformed/unmapped/corpus/parity/reducer failure. The report is telemetry
and grants no authority.

## Task 1: Pure transition cursor and strict adapter boundary

**Files:**
- Modify: `scripts/capability_reducer.py`
- Create: `scripts/capability_v1_adapter.py`
- Modify: `tests/unit/test_capability_reducer.py`
- Create: `tests/unit/test_capability_v1_adapter.py`

**Interfaces:**
- Produces: `transition_cursor(...) -> tuple[int, int, str]`.
- Produces: exact `LegacyAdapterError` codes and strict normalized-record
  parsing used by Task 2.
- Returns `()` for an empty history. Until Task 2 supplies the closed mapping
  table, every non-empty structurally valid current record finishes strict
  parsing and digest validation and then raises `legacy_unmapped`; it does not
  call a resolver, derive a cursor, apply a reducer event, or emit an envelope.
- Does not yet add the corpus CLI implementation beyond a parser entrypoint
  that fails closed when no valid `--check-corpus` input is supplied.

- [ ] **Step 1: Write failing transition-cursor and strict-record tests**

Add focused tests equivalent to:

```python
def test_transition_cursor_returns_only_next_revision_version_and_precondition():
    revision, version, precondition = reducer.transition_cursor(
        reducer.KernelState(), work_id="work-1", unit_id=None
    )
    assert (revision, version) == (1, 0)
    assert re.fullmatch(reducer.DIGEST_PATTERN, precondition)


@pytest.mark.parametrize("new_unit_id", (None, "unit-new"))
def test_transition_cursor_keeps_work_and_exact_unit_axes_independent(new_unit_id):
    state = state_with_existing_work_and_other_unit()
    revision, version, precondition = reducer.transition_cursor(
        state, work_id="work-1", unit_id=new_unit_id
    )
    assert revision == 2
    assert version == 0
    assert precondition == zero_state_precondition("work-1", new_unit_id)


@pytest.mark.parametrize(
    "forbidden",
    (
        "transition_id",
        "requested_transition",
        "expected_unit_version",
        "precondition_digest",
        "activation_epoch",
        "principal",
        "actor",
        "verdict",
        "effect_eligible",
        "mode",
        "writer",
    ),
)
def test_legacy_record_rejects_authority_and_derived_fields(forbidden):
    record = valid_legacy_record()
    record[forbidden] = "forbidden"
    with pytest.raises(adapter.LegacyAdapterError) as exc:
        adapter.adapt_v1_history(
            [record], resolve_actor=resolve_actor, resolve_scope=resolve_scope
        )
    assert exc.value.code == "legacy_invalid"
```

Also pin non-object records, exact keys, duplicate JSON keys, bool-as-int,
unknown schema/domain/value/context, invalid ID/ref/digest syntax (including
invalid scope-reference or scope-digest syntax), source-digest mismatch, future
v1 schema, raw route-v2 input, and nonzero/explicit epoch rejection. Pin that
an empty history returns `()`, a valid current record raises
`legacy_unmapped`, and actor/scope resolvers are not called in either Task-1
path.

- [ ] **Step 2: Run RED**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_v1_adapter.py
```

Expected: fail because `transition_cursor`, `LegacyAdapterError`, and
`adapt_v1_history` do not exist.

- [ ] **Step 3: Implement the minimal cursor and strict parser**

`transition_cursor` must call the existing state/ID validators and reuse the
existing precondition function. The adapter must canonicalize the strictly
parsed record without `source_digest`, compare the digest, and reject all
derived/authority keys. Do not infer missing values. Task 1 must not invent a
provisional mapping: after a non-empty record passes structural, schema,
domain/value/context, identifier, opaque scope-reference/digest syntax, and
source-digest validation, raise `LegacyAdapterError("legacy_unmapped")` without
calling either resolver. Map every external parsing exception to one stable
adapter code without including raw legacy content in the message.

- [ ] **Step 4: Add reducer reverse-dependency and mutation guards**

Extend the existing AST test so `scripts/capability_reducer.py` cannot import
`capability_v1_adapter`. Add a non-vacuous mutation that injects one filesystem
or adapter import and proves the guard fails before restoring the source.

- [ ] **Step 5: Run GREEN and Phase-2A regression**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_capability_v1_adapter.py
```

Expected: pass; the existing replay golden digests remain unchanged.

- [ ] **Step 6: Commit Task 1**

```sh
env -u GIT_INDEX_FILE git add \
  scripts/capability_reducer.py \
  scripts/capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_v1_adapter.py
env -u GIT_INDEX_FILE git commit -m "feat: add strict v1 shadow adapter boundary"
```

## Task 2: Complete replay corpus and two-way parity gate

**Files:**
- Modify: `scripts/capability_v1_adapter.py`
- Create: `tests/fixtures/compact_kernel/v1_to_v2_replay.json`
- Modify: `tests/unit/test_capability_v1_adapter.py`

**Interfaces:**
- Consumes: Task-1 `transition_cursor`, strict record parser, and resolver
  contract.
- Produces: deterministic route-v2 envelopes for route/work cases.
- Produces: explicit specialized `no_route_event` dispositions and one
  canonical sanitized parity report for the complete Phase-2 corpus.

- [ ] **Step 1: Write the exact corpus manifest before adapter mappings**

The fixture root has exactly:

```text
schema_version
sources
actors
scopes
case_manifest
cases
phase2_misuse_bindings
deferred_phase3_misuse_ids
reducer_replay_ids
```

`sources` binds the canonical SHA-256 and exact repository-relative path of:

```text
tests/fixtures/compact_state_mapping/v1.json
tests/fixtures/compact_kernel/v1_misuse_vectors.json
tests/fixtures/compact_kernel/v2_replay_vectors.json
```

Every case has one unique ID, a `case_kind` (`mapping`, `history`, or `misuse`),
an exact mapping-row or misuse-vector reference, a disposition (`route_event`,
`no_route_event`, or an expected stable error), zero or more stable source
records, and an exact expected result. `case_manifest` equals the case-ID
sequence exactly. Every source record has a canonical digest. Primary
`mapping` cases are one-to-one with the mapping fixture's row-ID set; extra
`history` and `misuse` cases cannot satisfy or duplicate that requirement.
`phase2_misuse_bindings` maps each Phase-2 misuse ID to exactly one executable
target: either one `history`/`misuse` case with non-empty source records or one
named reducer replay vector. Targets must exist, may bind only one misuse ID,
and must actually execute in the Phase-2 verification command; uncovered or
multiply covered IDs fail. Deferred Phase-3 misuse IDs equal their source
fixture partition exactly and bind no Phase-2 target. Reducer replay IDs equal
the v2 replay fixture set exactly; its permutation set remains pinned and
executed by `test_capability_reducer_replay.py`.

The three case-bound associations also have this production-side exact oracle,
independent of each case's self-declared misuse label:

```text
relevant_dependency_change -> misuse:dependency-change -> dependency_digest
relevant_acceptance_change -> misuse:acceptance-change -> acceptance_digest
relevant_evidence_change -> misuse:evidence-change -> evidence_refs
```

Each oracle case is exactly a `misuse` case with `route_event` disposition,
stable resolvers, order `[[0, 1]]`, no expected error, two envelopes, and
requested transitions `START` then `UPDATE`. It has exactly two parsed records
with distinct source identities and exact work revisions `1` then `2`. Schema,
work/route/unit/actor identity, domain, normalized context, mutable scope
ref/digest, content digest, verification ref, and normalized effect-reservation
refs stay equal. Among dependency digest, acceptance digest, and normalized
evidence refs, exactly the oracle-named field changes. The main corpus loop must
still call the public adapter and verify both resulting transitions; the static
oracle cannot replace execution.

Include route histories covering named/null route IDs, named/null unit IDs,
sequential updates, exact duplicate source identity, changed duplicate content,
disjoint-order permutations, stale/gapped revision, resolver drift, scope
ambiguity, content/dependency/acceptance/evidence change, and opaque `web:`
evidence. No case obtains identity or scope from prose or filename.

Every declared record order independently covers every declared record index.
Repeated or extra indexes fail closed except for the exact committed
`history:exact-duplicate-source` case, whose one record is delivered only as
`[[0, 0]]`. Every declared record independently crosses the strict parser
boundary before ordered execution; a parser error is acceptable only when
exactly one record produces the case's exact expected error. The
`history:mixed-v1-v2` case is bound to two records with schema sequence
`compact-kernel-legacy-observation/v1`, `governance.route/v2`, exact order
`[[0, 1]]`, and expected error `legacy_version`.

The complete `case_kind="history"` ID set equals the production history
semantic-oracle key set exactly: no declared history is unbound and no oracle
entry is orphaned. Independent of case names and self-declared outcomes, that
oracle binds every history's mapping row, record count, schema sequence, order
set, resolver mode, disposition, success/error shape, and its essential
identity, revision, scope, and changed-field relationships. In particular,
`history:stale-work-revision` is an accepted revision followed by a stale
revision with exact revisions `(1, 1)`; the gate executes the public adapter
once for the accepted prefix and again for the rejecting history. It remains
distinct from `history:gapped-work-revision`, whose exact revisions are
`(1, 3)`.

- [ ] **Step 2: Write failing completeness and parity tests**

Add tests equivalent to:

```python
def test_corpus_has_no_missing_extra_duplicate_or_silently_skipped_case():
    corpus = load_strict(CORPUS)
    assert corpus["case_manifest"] == [case["id"] for case in corpus["cases"]]
    mapping_cases = [
        case for case in corpus["cases"] if case["case_kind"] == "mapping"
    ]
    assert [case["mapping_row_id"] for case in mapping_cases] == mapping_row_ids()
    bindings = corpus["phase2_misuse_bindings"]
    assert set(bindings) == phase2_misuse_ids()
    assert every_binding_has_one_existing_executed_target(bindings, corpus)
    assert targets_are_not_shared_between_misuse_ids(bindings)
    assert set(corpus["deferred_phase3_misuse_ids"]) == phase3_misuse_ids()
    assert set(corpus["reducer_replay_ids"]) == reducer_replay_ids()


def test_specialized_states_never_emit_route_events():
    report = adapter._check_corpus(load_strict(CORPUS))
    assert report.specialized_event_ids == ()


def test_every_specialized_mapping_key_covers_route_unit_matrix():
    assert observed_probe_axes() == {
        (mapping_key, route_is_null, unit_is_null)
        for mapping_key in specialized_mapping_keys()
        for route_is_null in (False, True)
        for unit_is_null in (False, True)
    }


def test_independent_input_orders_return_one_canonical_envelope_tuple():
    left, right = independent_records()
    forward = adapter.adapt_v1_history(
        [left, right], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )
    reverse = adapter.adapt_v1_history(
        [right, left], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )
    assert forward == reverse


@pytest.mark.parametrize(
    ("mutation", "expected_kind"),
    (
        (make_compact_more_permissive, "compact_more_permissive"),
        (make_compact_more_restrictive, "compact_more_restrictive"),
        (make_effect_more_permissive, "compact_more_permissive"),
        (make_effect_more_restrictive, "compact_more_restrictive"),
    ),
)
def test_both_parity_directions_block(mutation, expected_kind):
    report = adapter._check_corpus(mutation(load_strict(CORPUS)))
    assert expected_kind in {item.kind for item in report.divergences}
    assert adapter._report_is_gate_clean(report) is False
```

Also remove one case, add one unmanifested case, empty one misuse target's
source records, point two misuse IDs at one target, swap the dependency and
acceptance case labels plus binding targets together, add a second delta field,
change one source digest, inject a named-route/unit specialized fallback, and
change one adapter mapping to prove each guard is non-vacuous.

- [ ] **Step 3: Run RED**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py
```

Expected: fail because corpus loading, dispositions, event mapping, parity
classification, and report rendering are incomplete.

- [ ] **Step 4: Implement route mapping, specialized dispositions, and gate**

Use the bound mapping fixture as the v1 golden, call
`compact_state_mapping.meaning_for()` for the current v1 result, and derive the
actual compact result only through `_ADAPTER_RULES` plus the emitted
envelope/no-event result. Compare all three with the corpus's separately
committed expected compact projection. The gate-only projection contains
acceptance/disposition, terminal scope, next action, advisory-only status, and
effect eligibility; it is never returned by `KernelReport` and cannot grant
authority.

For every route history, build an event from the normalized record, derive the
cursor, resolve actor/scope twice, and apply it to an in-memory `KernelState`.
Resolver handling is deterministic:

```python
first_actor_value = resolve_actor(record.actor_binding_digest)
first_actor, first_actor_bytes = capability_reducer._validate_actor(
    first_actor_value
)
second_actor_value = resolve_actor(record.actor_binding_digest)
second_actor, second_actor_bytes = capability_reducer._validate_actor(
    second_actor_value
)
if first_actor_bytes != second_actor_bytes:
    raise LegacyAdapterError("legacy_nondeterministic")
```

Each actor result crosses the reducer-owned validator separately before byte
comparison; raw actor equality and truth conversion are forbidden. Two valid
unequal canonical actors are `legacy_nondeterministic`; malformed or ineligible
results become stable sanitized failures. Pass only the validated first
`ActorContext` to `apply_transition`. Use the same two-read rule for scope
through the reducer's existing application boundary. Validate causal order as
supplied, map every external resolver or reducer exception to one stable
sanitized adapter code, and canonically sort only the fully accepted output
tuple. Task-2 tests own absolute resolved paths, ambiguous or redundant resolved
scope, and scope-resolver drift; none of those checks may be pulled into Task
1's opaque-record parser.

Maintain a local `source_id -> (source_digest, envelope)` map: an exact replay
reuses the original envelope before consulting the next cursor, while changed
content under the same source ID reaches the same transition identity and
blocks as a conflict. Stale revisions, scope/route ambiguity, and resolver drift
also block without a partial event tuple. Specialized cases are checked for
meaning parity but emit zero events. For every `_ADAPTER_RULES` entry with no
transition, derive one syntactically valid named route and unit from committed
corpus records and probe the public adapter once for each `(null, null)`,
`(null, named)`, `(named, null)`, and `(named, named)` route/unit cell. Every
row-bound probe has a unique source/work identity and recomputed source digest.
Only `legacy_unmapped` with zero actor/scope resolver calls is accepted; success,
another error, or resolver use blocks, and a non-empty success records the
mapping case in `specialized_event_ids`.

Add an AST/source-shape test proving `_compact_projection()` does not call
`compact_state_mapping.meaning_for()` and does not read fixture data. Mutate
one `_ADAPTER_RULES` transition and one semantic field while keeping both
oracles unchanged; each mutation must make the gate fail.

Parity kinds are exactly:

```text
match
compact_more_permissive
compact_more_restrictive
authority_semantic_mismatch
non_authority_only
adapter_error
```

All kinds except `match` and `non_authority_only` block. Effect eligibility has
the order `never < separate_current_grant < all_other_gates`. Route-event
emission where `no_route_event` is expected is more permissive; suppression of
an expected route event is more restrictive. Other terminal/retry mismatches
use `authority_semantic_mismatch` instead of inventing a false total order.

- [ ] **Step 5: Pin opaque web evidence and mixed-version behavior**

Tests must prove that adding, removing, or changing a `web:` ref changes only
the evidence/version/precondition digests, while reordering the same unique
references preserves source identity, envelopes, and reducer digests. No URL
is opened or parsed, and no verdict/effect field appears in reducer output.
Reject v2 records in the v1 adapter, future v1 schema, duplicate source IDs
across versions, and nonzero epoch material.

- [ ] **Step 6: Run GREEN and the complete Phase-2 corpus suite**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_compact_state_mapping.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
```

Expected: all tests pass; CLI exits `0`; every blocking divergence set is
empty; every fixture source/set digest agrees.

- [ ] **Step 7: Commit Task 2**

```sh
env -u GIT_INDEX_FILE git add \
  scripts/capability_v1_adapter.py \
  tests/fixtures/compact_kernel/v1_to_v2_replay.json \
  tests/unit/test_capability_v1_adapter.py
env -u GIT_INDEX_FILE git commit -m "test: gate full v1 shadow parity corpus"
```

## Task 3: Surface classification and durable review candidate

**Files:**
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `ARCHITECTURE.md`
- Create: `logs/capability-first/phase2b-shadow-parity.json`

**Interfaces:**
- Consumes: Task-2 clean canonical report.
- Produces: exact helper ownership and one durable gate measurement.
- Produces no live reader, writer, effect, provider, activation, or authority.

- [ ] **Step 1: Write failing inventory tests**

Add one component, `compact_shadow_reducer_and_v1_adapter`, with:

```text
authority_status = non_authoritative_read_only_shadow_compatibility
default_helper_class = historical_adapter
writer_paths = []
```

Its owned source paths include the reducer, route-v2 schema, adapter, and
adapter corpus. Its reader paths additionally include the mapping, misuse, and
reducer replay source fixtures bound by the corpus. Its module rules classify
`scripts/capability_reducer.py` as `runtime_core` and
`scripts/capability_v1_adapter.py` as `historical_adapter`; only adapter `main`
is overridden as a documented CLI. Add both modules to the required production
module owner set. Assert exactly one owner per path, empty writer paths, adapter
-> reducer import direction, and no reducer -> adapter import.

- [ ] **Step 2: Run inventory RED**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_compact_kernel_surface_inventory.py
```

Expected: fail because the new component and ownership rules are absent.

- [ ] **Step 3: Update the inventory minimally and run GREEN**

Update only the exact component/owner/helper sets required by the new module and
the previously unclassified Phase-2A reducer. Do not reclassify unrelated
helpers or relax orphan dispositions.

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_compact_kernel_surface_inventory.py
```

Expected: pass with import closure and exact owner equality.

- [ ] **Step 4: Persist and pin the deterministic parity artifact**

Run the committed CLI, capture its exact canonical JSON stdout, add those exact
bytes with `apply_patch` at
`logs/capability-first/phase2b-shadow-parity.json`, and add a test that compares
the committed artifact byte-for-byte with fresh report rendering. Do not add a
general adapter output writer merely to create this artifact.

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
```

Expected: exit `0`; canonical JSON contains the derived corpus/source counts
and digests and zero blocking divergences, with no raw legacy record, principal,
scope content, URL, prose, or authority claim.

- [ ] **Step 5: Update architecture only after evidence is green**

In `ARCHITECTURE.md`, add the reducer and adapter symbols with freshly verified
line anchors, state the adapter -> reducer dependency direction, and state that
v1 remains authoritative at epoch `0`. Refresh the document verification stamp
against the implementation HEAD.

- [ ] **Step 6: Run review-candidate verification**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_route_manifest.py \
  tests/unit/test_route_schema_sync.py \
  tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/compact_state_mapping.py \
  --check-fixture tests/fixtures/compact_state_mapping/v1.json
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/target_binding.py --check
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check f17d14c684e1e1a6378e52ab8f151070fb710e07..HEAD
env -u GIT_INDEX_FILE git diff --name-only f17d14c684e1e1a6378e52ab8f151070fb710e07..HEAD
```

Expected: tests and CLIs pass; target binding reports epoch `0`, writer `v1`,
declarative only; smoke is `OK`; the changed paths are exactly this plan plus
the Task-1 through Task-3 candidate files in **File map**.

- [ ] **Step 7: Commit Task 3**

```sh
env -u GIT_INDEX_FILE git add \
  tests/fixtures/compact_kernel/v1_surface_inventory.json \
  tests/unit/test_compact_kernel_surface_inventory.py \
  ARCHITECTURE.md \
  logs/capability-first/phase2b-shadow-parity.json \
  tests/unit/test_capability_v1_adapter.py
env -u GIT_INDEX_FILE git commit -m "chore: classify compact shadow gate"
```

## Final independent review

After Task 3, give one fresh read-only reviewer the committed plan and exact
`f17d14c684e1e1a6378e52ab8f151070fb710e07..HEAD` implementation diff. Ask:

> Can any malformed or mixed-version legacy input, duplicate/stale identity,
> causal-order ambiguity, actor/scope inference, specialized-state collapse,
> corpus omission, parity direction, opaque web ref, hidden reducer I/O, or
> activation surface escape the read-only epoch-0 shadow boundary, or can the
> gate falsely pass while compact behavior is more permissive or more
> restrictive than v1?

Any Critical or Important finding blocks Phase-2 closeout and is fixed in the
owning task with a fresh focused test. A clean review does not authorize push,
merge, Phase 3, or activation.

### Final-review evidence correction 5

The fresh full-range review of
`f17d14c684e1e1a6378e52ab8f151070fb710e07..c1a50dbcc4726d9abd91b54fd0fa15a14de7a754`
found no Critical findings and two Important evidence gaps. The bounded
correction binds successful `START` prefixes and exact actor/source/scope
provenance for the five affected causal-error cases. It also derives the exact
accepted-context set from current producer vocabularies, requires equality
with fixture, adapter-rule, and corpus keys, and adds the missing capacity case
plus 19 producer-backed ChatGPT failure cases. All specialized additions remain
`no_route_event`; v1 remains the only writer at epoch `0`.

The focused two-file command produced `13 failed, 192 passed` before any
production or fixture change, then GREEN via
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_compact_state_mapping.py tests/unit/test_capability_v1_adapter.py`
→ `210 passed`. The fixture CLI was verified via
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/compact_state_mapping.py --check-fixture tests/fixtures/compact_state_mapping/v1.json`
→ `validated 69 mappings across 7 domains`. The canonical corpus report in
`logs/capability-first/phase2b-shadow-parity.json` derives 89 cases with no
blocking divergence or specialized event. These correction facts do not close
Task 4, authorize Phase 3, or activate a writer.

### Final-review evidence correction 6

The fresh full-range review of
`f17d14c684e1e1a6378e52ab8f151070fb710e07..be1488a41b6174b4503fb23f8885794fa37528fc`
found no Critical findings and one remaining Important provenance gap. A valid,
exact second scope from another repository preserved the successful `START`
prefix and public `legacy_ambiguous` result while changing the raw reducer cause
to `actor_binding`; the broad public error allowed the corpus gate to remain
falsely clean.

The focused command
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_capability_v1_adapter.py::test_scope_ambiguity_rejects_exact_scope_from_other_repository tests/unit/test_capability_v1_adapter.py::test_canonical_ambiguity_cases_pin_raw_reducer_causes`
produced `1 failed, 1 passed` before the production change, with the failure
proving the mutated corpus still passed the gate. It then produced `2 passed`
after the validated actor fixture map was threaded into the history relationship
oracle. Route ambiguity, scope ambiguity, and
overlapping-scope constructions now require every exact normalized record scope
repository to equal the repository of the fixture actor selected by the equal
actor-binding digest. A positive raw-cause regression pins the canonical
prefix/full paths to `route_ambiguity`, `scope_invalid`, and `scope_overlap`,
respectively, while the public error remains `legacy_ambiguous`. No reducer,
public mapping, fixture, artifact, target binding, writer, epoch, or activation
behavior changed. These correction facts do not close Task 4, authorize Phase
3, or activate a writer.

## Task 4: Record reviewed Phase-2 closeout

**Files:**
- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Modify: `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`

**Interfaces:**
- Consumes: the clean independent review of the committed Task-1 through
  Task-3 range.
- Produces: truthful Phase-2 status and exact evidence; no behavior change.

- [ ] **Step 1: Record only reproduced review facts**

In the capability guide, check both Phase-2 boxes and add one short evidence
paragraph naming the exact implementation range, corpus artifact, focused test
command, independent review verdict, and epoch `0`/writer `v1` check. Do not
mark any Phase-3 or activation item complete.

In this plan's independent-review section, append the reviewer verdict, exact
reviewed range, and any reproduced correction commits. Do not paste a raw
review transcript or claim evidence that was not rerun locally.

- [ ] **Step 2: Run final verification**

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_route_manifest.py \
  tests/unit/test_route_schema_sync.py \
  tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/target_binding.py --check
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check f17d14c684e1e1a6378e52ab8f151070fb710e07..HEAD
env -u GIT_INDEX_FILE git diff --name-only f17d14c684e1e1a6378e52ab8f151070fb710e07..HEAD
```

Expected: all gates remain green after the docs-only closeout edits; the range
contains only the files in **File map**.

- [ ] **Step 3: Commit Task 4**

```sh
env -u GIT_INDEX_FILE git add \
  docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md \
  docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md
env -u GIT_INDEX_FILE git commit -m "docs: close compact shadow phase 2"
```

## Non-goals

- No live mailbox, route, ref, cursor, lock, verification store, effect store,
  ChatGPT/Claude/provider, filesystem scan, or external web call.
- No legacy rewrite, route writer, compact writer, dual writer, activation ref,
  epoch mutation, rollback, migration, reader cutover, or mixed-version live
  deployment.
- No effect reservation/execution, provider dispatch, retry/fallback, spend,
  or external action.
- No mapping of specialized lifecycle values into route-v2 transition requests.
- No Phase-3 principal issuance/revocation transport or real caller migration.
- No generic compatibility framework, second authority store, database,
  plugin registry, telemetry service, or protocol ceremony artifact.

## Stop conditions

Stop without widening the task if a legacy source lacks stable identity,
contiguous causal revision, host-resolved actor, immutable scope, or exact
content/dependency/acceptance/evidence digests; if any specialized state would
need a route event; if the full set cannot be proven from committed manifests;
if parity needs an authority field added to `KernelReport`; if the reducer would
need I/O or an adapter import; or if any change requires live state, an active
epoch, a writer, an effect, or a provider. Phase 3 cannot begin until this plan
is implemented, its deterministic gate is clean, and its independent diff
review has no Critical or Important finding.
