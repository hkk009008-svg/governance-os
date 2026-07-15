# Capability Compact Reducer Phase 2A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to execute this plan task-by-task
> and `superpowers:test-driven-development` for every task. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest pure, deterministic, non-authoritative Phase-2A
reducer seam: a strict route-v2 transition contract, an injected shadow
reducer, and replay vectors that cannot grant GO, DONE, terminality, or effect
eligibility. Phase 2A does not complete the guide's Phase-2 adapter/divergence
gate.

**Architecture:** `scripts/capability_reducer.py` is an in-memory function over
strict typed values. The host supplies actor and immutable-scope resolvers;
the reducer performs no filesystem, Git, mailbox, ref, provider, clock, random,
or executor access. Its output is an observational report whose type has no
authority-bearing field. This slice does not adapt live v1 history; it creates
the pure seam that a later read-only adapter can call.

**Tech Stack:** Python frozen dataclasses and type aliases, RFC 8785 bytes from
`threeway.canon.canonicalize`, JSON Schema as a synchronized documentation
contract, JSON replay fixtures, pytest.

## Global constraints

- Version 1 remains the only authority. `ActivationState` accepts only
  `mode="shadow"`; there is no active/compact writer mode or activation writer.
- Do not import or call a live v1 reader/writer, mailbox/cursor/lock/ref store,
  effect executor, provider adapter, subprocess, network client, clock, random
  source, or environment reader from `scripts/capability_reducer.py`.
- `resolve_actor` and `resolve_scope` are injected callables. Both resolutions
  are checked twice for identical normalized, digest-bound output before a
  transition is applied. `apply_transition` receives an already resolved actor
  but still validates and digest-binds it.
- Provider results, verification references, and effect-reservation references
  remain opaque input digests/refs. They cannot change an observational report
  into authority or execution eligibility.
- Use a hand-rolled enforcing parser plus one schema-sync test; add no runtime
  `jsonschema` dependency and no second operation/event store.
- Every public input boundary is validated at runtime. Frozen dataclasses and
  annotations are never treated as validation.
- A null `unit_id` is the one work-level unit lane for that `work_id`. Initial
  route identity, including null, is immutable. Work revisions are contiguous:
  the first is `1`, and every later distinct transition is exactly prior + 1.
- Shared files are changed sequentially. Each task uses RED -> minimal GREEN ->
  focused regression -> one commit. All Git and pytest commands use
  `env -u GIT_INDEX_FILE`.
- Before Task 1, commit this plan and obtain one independent design review of
  the abuse matrix. After Task 3, obtain one independent review of the actual
  three-commit diff. Do not repeat the same review question.

## Independent design review resolution

A fresh read-only Codex reviewer found no Critical issue and eight Important
ambiguities in the first draft. This revision closes each before Task 1:

1. tagged total keys define nullable-unit ordering; route identity is immutable
   including null; work revisions are contiguous;
2. one precondition function validates pre-state and recomputes post-state;
3. scope binds immutably per unit, uses component-wise POSIX ancestry, and is
   checked across works;
4. every dataclass input boundary and prior `KernelState` is runtime-validated;
5. actor contexts are canonically digest-bound, user/parent narrowed, resolved
   twice, and rejected on drift;
6. both reducer entrypoints enforce exact-duplicate idempotence before resolver
   calls and reject changed ID reuse;
7. the schema's complete property mapping equals the parser's field spec; and
8. committed AST import/call and exact output-shape tests enforce purity and the
   shadow-only boundary.

The follow-up review closed five items and the Phase-2A boundary, then found
three remaining implementation ambiguities. This revision additionally:

9. requires a child binding to have a distinct parent and a proper-subset
   action set, with equality and self-parent tests;
10. gives every actor and scope string an exact grammar, length, collection
    bound, and malformed-boundary test; and
11. replaces a mutable schema mapping with a fresh mapping function and pins
    the AST test's import modules and imported call names as test literals.

The reviewer re-checked this revision and returned `APPROVED`: no remaining
Critical or Important issue in the parent-narrowing, boundary-grammar,
schema/AST-purity, Phase-2A, or web-research observation scope. Task 1 may begin
only from the committed version of this plan.

Post-Task-1 review corrected three enforcement gaps without widening the
Phase-2A boundary: integer fields now stop at the RFC-8785/JavaScript safe
maximum so every accepted envelope is canonicalizable; AST purity pins every
permitted call shape and rejects dynamic callable resolution with mutation
tests; and exact dataclass fields plus public signature kinds are test-pinned.
Literal imports and top-level definitions bind those calls to their expected
origins; protected names cannot be rebound, and dangerous introspection fails.

## File map

| File | Responsibility |
|---|---|
| `schemas/route-v2.schema.json` | Closed documentation schema for one compact transition envelope. |
| `scripts/capability_reducer.py` | Strict parser, frozen types, canonical digests, scope checks, and pure shadow reduction. |
| `tests/unit/test_route_v2_schema_sync.py` | Proves schema fields/enums remain synchronized with the enforcing parser. |
| `tests/unit/test_capability_reducer.py` | Focused parser, actor, version, scope, and shadow-boundary tests. |
| `tests/fixtures/compact_kernel/v2_replay_vectors.json` | Deterministic permutations, duplicates, conflicts, and expected outcomes. |
| `tests/unit/test_capability_reducer_replay.py` | Replays every vector and checks order-independent reports or stable error codes. |

## Exact interfaces

Implement these names and shapes; do not add a store, CLI, or I/O adapter:

```python
SCHEMA_ID = "governance.route/v2"
ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"
REF_PATTERN = r"^[\x21-\x7e]{1,512}$"
DIGEST_PATTERN = r"^sha256:[0-9a-f]{64}$"
REPOSITORY_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$"
PRINCIPAL_PATTERN = r"^[\x21-\x7e]{1,256}$"
ACTION_PATTERN = r"^[a-z][a-z0-9_.:-]{0,63}$"
LOCK_DOMAIN_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"
MAX_INT = 2**53 - 1
MAX_COLLECTION_ITEMS = 64
REQUESTED_TRANSITIONS = frozenset({
    "START", "UPDATE", "BLOCK", "REQUEST_REVIEW", "REQUEST_CLOSE",
    "CANCEL", "SUPERSEDE",
})
ENVELOPE_FIELDS = (
    "schema", "work_id", "transition_id", "route_id", "work_revision",
    "unit_id", "actor_binding_digest", "requested_transition",
    "expected_unit_version", "precondition_digest", "mutable_scope_ref",
    "mutable_scope_digest", "content_digest", "dependency_digest",
    "acceptance_digest", "evidence_refs", "verification_ref",
    "effect_reservation_refs", "activation_epoch",
)
ZERO_DIGEST = "sha256:" + ("0" * 64)
# Exact JSON-Schema `properties`; the parser uses these same patterns, bounds,
# nullable shapes, item schemas, uniqueness, and array limits.
def field_schemas() -> dict[str, dict[str, object]]: ...

@dataclass(frozen=True)
class TransitionEnvelope:
    schema: str
    work_id: str
    transition_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    actor_binding_digest: str
    requested_transition: str
    expected_unit_version: int
    precondition_digest: str
    mutable_scope_ref: str
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_refs: tuple[str, ...]
    verification_ref: str | None
    effect_reservation_refs: tuple[str, ...]
    activation_epoch: int

@dataclass(frozen=True)
class ActorContext:
    binding_id: str
    binding_digest: str
    repository: str
    principal: str
    allowed_actions: frozenset[str]
    user_authorized_actions: frozenset[str]
    parent_binding_id: str | None
    parent_allowed_actions: frozenset[str] | None
    attested: bool
    expired: bool
    revoked: bool

@dataclass(frozen=True)
class ResolvedScope:
    repository: str
    paths: tuple[str, ...]
    lock_domains: tuple[str, ...]

@dataclass(frozen=True)
class ActivationState:
    epoch: int
    mode: Literal["shadow"] = "shadow"  # __post_init__ also enforces it

@dataclass(frozen=True)
class WorkSnapshot:
    work_id: str
    route_id: str | None
    work_revision: int

@dataclass(frozen=True)
class UnitSnapshot:
    work_id: str
    unit_id: str | None
    unit_version: int
    mutable_scope_ref: str
    scope_repository: str
    scope_paths: tuple[str, ...]
    scope_lock_domains: tuple[str, ...]
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_digest: str
    precondition_digest: str

@dataclass(frozen=True)
class AppliedTransition:
    transition_id: str
    event_digest: str
    work_id: str
    unit_id: str | None
    work_revision: int
    resulting_unit_version: int
    mutable_scope_digest: str

@dataclass(frozen=True)
class KernelState:
    works: tuple[WorkSnapshot, ...] = ()
    units: tuple[UnitSnapshot, ...] = ()
    transitions: tuple[AppliedTransition, ...] = ()

@dataclass(frozen=True)
class KernelReport:
    mode: Literal["shadow"]
    state_digest: str
    applied_transition_ids: tuple[str, ...]
    idempotent_transition_ids: tuple[str, ...]
    units: tuple[UnitSnapshot, ...]
```

`unit_id=None` is a real, single work-level unit identity, not missing data.
Use these total ordering keys everywhere:

```python
def unit_key(work_id: str, unit_id: str | None) -> tuple[str, int, str]:
    return (work_id, 0, "") if unit_id is None else (work_id, 1, unit_id)

def transition_key(item: AppliedTransition) -> tuple[str, int, str, int, str]:
    work, tag, unit = unit_key(item.work_id, item.unit_id)
    return (work, tag, unit, item.work_revision, item.transition_id)
```

IDs cannot be empty, so the null tag cannot collide with a string unit ID.
Sort works by `work_id`, units by `unit_key`, transitions by `transition_key`,
and report ID tuples lexicographically.

Define `ActorBindingResolver = Callable[[str], ActorContext]` and
`ScopeResolver = Callable[[str], ResolvedScope]`. The callable signatures are
`parse_transition(value: object) -> TransitionEnvelope`,
`apply_transition(state, event, *, actor, activation, resolve_scope) ->
KernelState`, and `reduce_protocol_state(events, *, resolve_actor,
resolve_scope, activation) -> KernelReport`, using the exact types above.

`KernelReport` has exactly the five fields shown. No output type or
reducer-authored enum/status may contain `GO`, `DONE`, `verdict`, `terminal`,
`authority`, `authorized`, `effect_eligible`, or `effect_eligibility`.

All five reducer-output dataclasses (`WorkSnapshot`, `UnitSnapshot`,
`AppliedTransition`, `KernelState`, and `KernelReport`) have exact field-set
tests. Tests inspect structural field and reducer-authored enum names, never
attacker-controlled ID/ref values.

`ReducerError` carries one stable `code`. Use only these codes in this slice:
`invalid_envelope`, `state_invalid`, `actor_binding`, `actor_ineligible`,
`actor_nondeterministic`, `activation_epoch`, `expected_version`,
`precondition`, `work_revision`, `route_ambiguity`, `scope_invalid`,
`scope_digest`, `scope_nondeterministic`, `scope_overlap`, and
`transition_id_reuse`.

## R-INDEPENDENCE abuse and edge-case acceptance

| Threat | Concrete acceptance tests | Required result |
|---|---|---|
| Untrusted parse/schema acceptance | `test_parse_rejects_non_object_missing_unknown_wrong_typed_and_wrong_schema`; `test_parse_rejects_payload_principal_and_effect_action_fields`; `test_direct_envelope_construction_cannot_bypass_validation`; `test_schema_and_parser_contract_are_exactly_synchronized`; `test_public_boundary_dataclasses_are_validated` | Stable `invalid_envelope`/`state_invalid`; no partial object or annotation-only trust. |
| Principal binding | `test_actor_is_resolved_out_of_band_and_canonical_digest_must_match`; `test_revoked_expired_unattested_or_actionless_actor_is_ineligible`; `test_user_actions_cannot_be_broadened_and_child_actions_are_a_proper_subset`; `test_child_binding_rejects_equal_action_set_and_self_parent`; `test_actor_and_scope_string_grammars_are_exact`; `test_same_event_replayed_under_other_actor_is_rejected`; `test_actor_resolver_must_repeat_exactly` | Payload cannot name a principal; canonical host binding must be eligible, user-bounded, strictly child-narrowed, non-self-parented, and deterministic. |
| Duplicate/reordered replay | `test_apply_exact_duplicate_returns_before_resolvers_and_changed_duplicate_conflicts`; `test_reduce_exact_duplicate_is_idempotent_but_changed_duplicate_conflicts`; replay vectors `independent_order_a` and `independent_order_b` | Both entrypoints return one application for an exact duplicate; changed ID conflicts; independent order yields identical report bytes. |
| Expected-version conflicts | `test_stale_unit_version_precondition_and_contiguous_work_revision_fail_closed`; `test_route_identity_including_null_cannot_change`; `test_post_state_precondition_is_recomputed_for_sequential_transitions`; `test_relevant_digest_change_alone_bumps_unit_version` | Stable typed error; revisions start at 1 and have no gaps; post-state precondition is reusable; unrelated unit remains unchanged. |
| Merge/scope ambiguity | `test_scope_digest_and_repository_binding_are_required`; `test_scope_is_immutable_for_one_unit`; `test_component_ancestry_redundancy_and_lock_overlap_fail`; `test_nullable_and_string_units_have_total_order`; replay vector `disjoint_scopes_merge` | Disjoint canonical scopes merge; same-unit scope changes, cross-work overlap, redundancy, or repository ambiguity fail; `src/a` does not overlap `src/ab`. |
| Shadow authority escape | `test_activation_state_is_shadow_only`; `test_request_close_verification_and_effect_refs_remain_observations`; `test_every_output_dataclass_has_exact_non_authority_fields`; `test_reducer_ast_has_only_pure_import_and_call_boundaries` | No constructor/configuration path to active mode, no authority-shaped output, and no hidden live/I/O dependency. |
| Web-research authority confusion | `test_web_research_reference_is_opaque_observation_only`; replay vector `web_research_observation` | A seat may supply a sanitized durable source reference through `evidence_refs`; the reducer neither fetches nor trusts it, and it can affect only evidence digest/version in a shadow report. |
| Nondeterminism | `test_actor_and_scope_resolvers_must_repeat_exactly`; replay vectors with reversed input, reordered JSON keys, nullable/string unit identities, and reordered ref arrays | Resolver drift fails; normalized equivalent input produces byte-identical report. |

The Phase-1 misuse vectors enforced here are forged principal, exact/changed
duplicate transition ID, stale unit version, stale epoch, and relevant
content/dependency/acceptance/evidence changes. Ambiguous external effects and
duplicate/fallback provider dispatch remain Phase 3 because this slice has no
executor or provider caller.

---

### Task 1: Strict route-v2 envelope contract

**Files:**

- Create: `schemas/route-v2.schema.json`
- Create: `scripts/capability_reducer.py`
- Create: `tests/unit/test_route_v2_schema_sync.py`
- Create: `tests/unit/test_capability_reducer.py`

**Produces:** `TransitionEnvelope`, `parse_transition`, canonical transition
mapping/bytes/digest helpers, the constants in **Exact interfaces**, and typed
`ReducerError`.

- [ ] **Step 1: Write failing parser and schema-sync tests**

  Add the three untrusted-parser tests named in the matrix. A valid object uses
  every `ENVELOPE_FIELDS` key; IDs match `ID_PATTERN`, refs match
  `REF_PATTERN`, and arrays have at most 64
  unique refs, and revisions/epochs are non-boolean integers from their minimum
  through `2**53 - 1` (`work_revision >= 1`, the other two `>= 0`). Digests match
  `^sha256:[0-9a-f]{64}$`, nullable fields are exactly `route_id`, `unit_id`, and
  `verification_ref`, and ref arrays contain unique strings. Mutations cover
  each missing key, each unknown key, wrong schema, bool-as-int, bad digest,
  unsupported transition, duplicate refs, and injected `principal`, `actor`,
  `effect_action`, or `effect_eligible` keys.

  `test_route_v2_schema_sync.py` loads the schema and asserts:

  ```python
  assert schema["$id"] == reducer.SCHEMA_ID
  assert schema["additionalProperties"] is False
  assert tuple(schema["required"]) == reducer.ENVELOPE_FIELDS
  assert schema["properties"] == reducer.field_schemas()
  ```

  `field_schemas()` returns a fresh mapping and pins each field's complete
  type/const/nullable form, exact
  pattern, minimum/maximum, and array item/uniqueness/limit contract. The parser
  uses the same `ID_PATTERN`, `REF_PATTERN`, `DIGEST_PATTERN`, `MAX_INT`, and
  transition set; no weaker duplicate schema constants are allowed. The
  function returns new nested dictionaries/lists on every call; production has
  no mutable schema global and callers cannot mutate later validation.

- [ ] **Step 2: Run RED**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q tests/unit/test_route_v2_schema_sync.py \
    tests/unit/test_capability_reducer.py
  ```

  Expected: collection/import failure because the schema/module contract does
  not exist; no unrelated test failure.

- [ ] **Step 3: Implement the minimal closed contract**

  Make the JSON Schema Draft 2020-12 object closed and exact. Implement the
  parser by checking the exact key set before reading values, rejecting bools
  where integers are required, normalizing ref arrays to sorted tuples, and
  returning a frozen envelope. Serialize only through an explicit mapping in
  `ENVELOPE_FIELDS` order and RFC 8785 canonicalization; never through
  `__dict__`. Convert every canonicalization/type failure to a `ReducerError`
  whose code is `invalid_envelope`. Both reducer entrypoints must round-trip a
  directly constructed envelope through this same parser before using it. Add
  the AST purity test now. In the test itself, literal
  `PERMITTED_IMPORT_MODULES` is exactly `("__future__", "dataclasses",
  "hashlib", "re", "typing", "threeway.canon")` and literal
  `PERMITTED_IMPORTED_CALL_NAMES` is exactly `("canonicalize", "dataclass",
  "fullmatch", "sha256")`; neither allowlist is imported or derived from
  production. Test-owned literal allowlists pin every permitted `ast.Call`
  name and attribute shape. `ast.Import` aliases, unlisted attribute calls,
  arbitrary builtin access, and subscript, lambda, or call-result callable
  resolution are forbidden. Mutation tests pin `hashlib.md5`, dynamic `open`,
  and dynamic `__import__` rejection.

- [ ] **Step 4: Run GREEN and commit**

  Run the Step-2 command. Expected: all new tests pass.

  ```sh
  env -u GIT_INDEX_FILE git add schemas/route-v2.schema.json \
    scripts/capability_reducer.py tests/unit/test_route_v2_schema_sync.py \
    tests/unit/test_capability_reducer.py
  env -u GIT_INDEX_FILE git commit -m "feat: add compact transition contract"
  ```

### Task 2: Pure shadow reducer and structural authority boundary

**Files:**

- Modify: `scripts/capability_reducer.py`
- Modify: `tests/unit/test_capability_reducer.py`

**Consumes:** Task-1 `TransitionEnvelope` and canonical digest helpers.

**Produces:** all remaining **Exact interfaces** types/functions and stable
reducer error codes.

- [ ] **Step 1: Write the failing reducer-law tests**

  Add every principal, expected-version, merge/scope, shadow-escape, and
  resolver-determinism test named in the matrix. Use in-memory resolver
  functions only. Include path cases `src/a` versus `src/a/file.py` and
  `src/ab`, redundant ancestors inside one scope, identical lock domains on
  disjoint paths, overlap across different works, absolute/backslash/empty/
  `.`/`..` components, and a resolver whose second answer changes. Cover actor
  digest/repository mismatch, resolver drift, user action broadening, parent
  equality/broadening, self-parenting,
  revoked/expired/unattested bindings, action omission, malformed direct state,
  empty/control/oversize actor and repository strings, malformed lock domains,
  null/string unit ordering, route changes in both null directions, work-
  revision gaps, two sequential preconditions, active mode, stale epoch, both
  direct and batch duplicate paths, and `REQUEST_CLOSE` with non-empty
  verification/effect refs. Parameterize relevant changes over content,
  dependency, acceptance, and evidence digests.

- [ ] **Step 2: Run RED**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q tests/unit/test_capability_reducer.py
  ```

  Expected: failures for missing reducer types/functions, not fixture or import
  errors from Task 1.

- [ ] **Step 3: Implement deterministic application**

  Apply this algorithm exactly:

  1. Validate the `ActivationState`, round-tripped envelope, and input
     `KernelState` before use. `ActivationState` accepts a non-boolean epoch
     `>= 0` and only `mode="shadow"`; event epoch must equal it. State validation
     checks exact primitive/tuple types, canonical ordering, unique work/unit/
     transition keys, digest grammar, contiguous positive work revisions,
     transition referential integrity, and every stored unit precondition by
     recomputation. Malformed direct state raises `state_invalid`.
  2. Compute the canonical event digest. If the state already contains its
     transition ID, return the unchanged state when the digest is identical or
     raise `transition_id_reuse` when it differs. Do this before actor or scope
     resolution; tests assert neither resolver is called for exact replay.
  3. Canonicalize an actor context through exactly `binding_id`, `repository`,
     `principal`, sorted `allowed_actions`, sorted `user_authorized_actions`,
     `parent_binding_id`, sorted-or-null `parent_allowed_actions`, `attested`,
     `expired`, and `revoked`. Recompute `binding_digest` from those RFC-8785
     bytes. `binding_id` and `parent_binding_id` match `ID_PATTERN`, repository
     matches `REPOSITORY_PATTERN` and also has no empty, `.` or `..` component,
     principal matches `PRINCIPAL_PATTERN`, and every action matches
     `ACTION_PATTERN`; action sets are non-empty and contain at most
     `MAX_COLLECTION_ITEMS`. Reject malformed types, digest/repository
     mismatch, revoked, expired, unattested, unauthorized actions, actions
     beyond the user set, or a child whose `allowed_actions` is not a proper
     subset of `parent_allowed_actions`. Root contexts require both parent
     fields null. Child contexts require both, a distinct parent binding ID,
     and `allowed_actions < parent_allowed_actions`; equality, a superset, and
     self-parenting fail. `reduce_protocol_state`
     resolves each distinct digest twice and rejects unequal normalized bytes
     as `actor_nondeterministic`; `apply_transition` validates its supplied
     actor through the same function.
  4. Resolve the scope twice for the same ref. Canonicalize a safe repository,
     sorted unique relative POSIX paths, and sorted unique lock domains. Scope
     repository follows the same repository grammar; each path matches
     `REF_PATTERN` before lexical validation; each lock domain matches
     `LOCK_DOMAIN_PATTERN`; and both tuples contain at most
     `MAX_COLLECTION_ITEMS`. A path
     is already lexical: no leading slash/backslash, empty/`.`/`..` component,
     repeated separator, or trailing slash. Reject changed normalized answers,
     empty scope, redundant ancestor entries, actor-repository mismatch, or
     event digest mismatch. Hash RFC-8785 bytes for exactly `repository`,
     `paths`, and `lock_domains` arrays. Compare path ancestry by components, so
     `src/a` overlaps `src/a/file.py` but not `src/ab`.
  5. On unit creation, bind `mutable_scope_ref`, digest, repository, paths, and
     lock domains immutably. A later event for that unit must reproduce all five
     values exactly. Against every *other* unit in the same repository,
     including units under other works, exact/ancestor path intersection or an
     equal lock domain is `scope_overlap`; otherwise disjoint scopes merge.
  6. A work's first distinct transition has revision `1`; every next distinct
     transition is exactly prior + 1. Bind the first `route_id` exactly,
     including null, and reject any later inequality as `route_ambiguity`.
  7. Define one `compute_precondition` over exactly `work_id`, `unit_id`,
     `unit_version`, `mutable_scope_digest`, `content_digest`,
     `dependency_digest`, `acceptance_digest`, and `evidence_digest`. The
     absent pre-state is version `0` with five `ZERO_DIGEST` values. Require the
     event's expected version and precondition to match the pre-state. A newly
     created unit becomes version `1`; later versions increment only when
     content, dependency, acceptance, or evidence changes. Build the post-state
     first, recompute and store its precondition, and prove that digest drives a
     second transition for both null-unit and route-free cases. A transition
     label alone does not increment the version.
  8. Evidence digest is the prefixed SHA-256 of canonical sorted refs. Sort via
     the exact total keys above. State digest hashes explicit canonical
     `works`, `units`, and `transitions` arrays; never `__dict__`, `asdict`, or a
     dataclass object.
  9. In `reduce_protocol_state`, parse/digest all events first, reject changed
     transition-ID reuse before any resolver call, collapse exact duplicates,
     sort unique events by `(work_id, work_revision, transition_id)`, resolve
     each actor deterministically through a local per-call cache, then apply.

  A sanitized web source reference such as
  `web:https://example.test/source@2026-07-15` is merely one valid opaque
  `evidence_refs` string. No URL parsing, fetching, source trust, freshness
  decision, or authority inference belongs in this module.

  Do not add a mutable module global, cache, file path, adapter, or output field
  beyond the exact interfaces.

- [ ] **Step 4: Run GREEN, regress Task 1, and commit**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q tests/unit/test_capability_reducer.py \
    tests/unit/test_route_v2_schema_sync.py
  env -u GIT_INDEX_FILE git add scripts/capability_reducer.py \
    tests/unit/test_capability_reducer.py
  env -u GIT_INDEX_FILE git commit -m "feat: add shadow capability reducer"
  ```

  Expected: focused tests pass; the Task-1 contract remains green.

### Task 3: Deterministic replay and merge vectors

**Files:**

- Create: `tests/fixtures/compact_kernel/v2_replay_vectors.json`
- Create: `tests/unit/test_capability_reducer_replay.py`

**Consumes:** Task-2 `reduce_protocol_state` and its frozen output/error codes.

**Produces:** fixture schema `compact-kernel-replay/v2` and a total replay test
over every vector ID.

- [ ] **Step 1: Add the replay test before its fixture**

  The loader accepts exactly `schema_version`, `actors`, `scopes`, and
  `vectors`. Each vector accepts exactly `id`, `events`, `permutations`, and
  `expected`; expected is either a report summary (`applied_transition_ids`,
  `idempotent_transition_ids`, and unit versions) or one `error_code`. Reject
  unknown fixture/vector/expected fields so test data cannot smuggle authority.
  Actor fixture objects use every canonical actor-context field and their
  recomputed digest; scope fixture objects use every normalized scope field.

- [ ] **Step 2: Run RED**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q tests/unit/test_capability_reducer_replay.py
  ```

  Expected: failure naming the absent
  `tests/fixtures/compact_kernel/v2_replay_vectors.json`.

- [ ] **Step 3: Add the complete replay corpus**

  Add these exact vector IDs and expectations:

  | Vector ID | Expected |
  |---|---|
  | `independent_order_a` / `independent_order_b` | Reversed disjoint inputs yield byte-identical reports. |
  | `exact_duplicate_collapses` | One applied ID and that ID once in idempotent IDs. |
  | `changed_duplicate_conflicts` | `transition_id_reuse`. |
  | `stale_expected_version` | `expected_version`. |
  | `stale_activation_epoch` | `activation_epoch`. |
  | `actor_cross_binding_replay` | `actor_binding`. |
  | `disjoint_scopes_merge` | Both units present at the expected versions. |
  | `ancestor_scope_overlap` | `scope_overlap`. |
  | `lock_domain_overlap` | `scope_overlap`. |
  | `scope_digest_mismatch` | `scope_digest`. |
  | `same_unit_scope_change_conflicts` | `scope_invalid`. |
  | `route_null_to_named_conflicts` | `route_ambiguity`. |
  | `work_revision_gap` | `work_revision`. |
  | `nullable_and_string_units_order` | Work-level null unit and named unit reduce with the prescribed total order. |
  | `changed_dependency_bumps_version` | Only the addressed unit version advances. |
  | `equivalent_ref_order_normalizes` | Reordered evidence/effect ref arrays yield identical transition/report digests. |
  | `web_research_observation` | A sanitized `web:` source reference changes only the evidence digest/version and remains absent from authority-shaped output. |
  | `request_close_is_observation` | Applied report with no authority-shaped key/value. |

  Use only repository-relative fictional scopes and `sha256:` plus 64 lowercase
  hex characters. The test constructs in-memory resolvers from `actors` and
  `scopes`; it must not open any path named by a vector. For every permutation,
  compare `canonicalize` over an explicit report mapping (never `asdict`); for
  errors, compare only the stable code and assert no report was returned.

- [ ] **Step 4: Run GREEN and commit**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q tests/unit/test_capability_reducer_replay.py \
    tests/unit/test_capability_reducer.py \
    tests/unit/test_route_v2_schema_sync.py
  env -u GIT_INDEX_FILE git add \
    tests/fixtures/compact_kernel/v2_replay_vectors.json \
    tests/unit/test_capability_reducer_replay.py
  env -u GIT_INDEX_FILE git commit -m "test: pin compact reducer replay laws"
  ```

  Expected: every vector and focused reducer test passes.

## Final verification and review gate

Run once from the final Task-3 HEAD:

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q \
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
  scripts/target_binding.py --check
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check HEAD~3..HEAD
env -u GIT_INDEX_FILE git diff --name-only HEAD~3..HEAD
```

Expected changed paths are exactly the six files in **File map**. The committed
AST purity and exact-output-field tests are the enforcement evidence; do not
substitute a one-off regex scan. Give one independent reviewer the committed
plan and exact `HEAD~3..HEAD` diff. The review question is: “Can any malformed
boundary value, resolver drift, duplicate, nullable identity, route/scope
ambiguity, replay order, hidden import/call, or output shape escape the
shadow-only authority boundary or make reduction nondeterministic?” Any
Critical or Important finding blocks publication and is fixed in the owning
task with a fresh focused test.

## Non-goals

- No v1 history adapter, dual-read comparison, live mailbox/route/capacity
  reader, legacy writer, migration, or full Phase-2 activation gate claim.
- No verification store lookup, effect lifecycle/reservation/executor,
  advisory dispatcher, ChatGPT/Claude call, web-search call, transport choice,
  or spend. Seats remain free to use separately approved research tools outside
  this pure reducer; their results cannot enter as authority.
- No activation ref, epoch mutation, writer fence, rollback, push, merge, or
  production integration.
- No generic event framework, plugin registry, database, ref store, CLI,
  telemetry artifact, or ceremony record.
- No Phase-3 principal issuance/expiry/revocation transport; this slice consumes
  a host-resolved, user-bounded, parent-narrowed context and fails closed on its
  canonical eligibility fields.

## Stop conditions

Stop without widening the task if implementation would require any live v1
import/caller, durable write, external effect, provider/model launch, activation
mode, environment-derived identity, nondeterministic resolver, or authority-
shaped report field. Stop on schema/parser drift, a resolver answer that cannot
be made canonical and repeatable, or replay output that changes with equivalent
input order. This plan completes only the pure Phase-2A reducer seam. A
separately reviewed Phase-2B plan must add the guide's read-only v1 adapter and
full-corpus divergence gate; Phase 3 cannot begin until that gate passes.
