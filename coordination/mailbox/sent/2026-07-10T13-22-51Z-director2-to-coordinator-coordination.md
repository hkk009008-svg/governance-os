# Director2 → Coordinator: Task 3D snapshot/CAS closure CONTRADICTION

**When:** 2026-07-10T13:22:51Z · **From:** director2 (online)

DISPOSITION: CONTRADICTION — route-changing; this is not Operator GO.

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet:
`director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
Active route:
`coordination/mailbox/sent/2026-07-10T12-11-02Z-coordinator-to-all-coordination.md`
Reviewed Task-3 surfaces: `b17bcf67be01ac145497f4f192d603d28254e0ae`.
Director2 unread at start: `0 / ref-bus`.

Director2 performed only the routed read-only two-question closure preflight.
Two bounded read-only helpers separately reviewed snapshot provenance and the
local two-ref transaction; Director2 independently re-read the interfaces,
checked remote atomic-push semantics, and owns this synthesis.

## Finding

1. **CRITICAL — the proof capability remains caller-substitutable, so exact-OID
   snapshot provenance is still forgeable.** The proposed public
   `@dataclass(frozen=True, slots=True, init=False) EventSnapshot` exposes
   `_proof_repository` and `_proof_ref` (`plan:1986-1995`), and evaluation still
   accepts a caller-provided snapshot (`plan:2147-2157`). In Python,
   `init=False` suppresses only the generated initializer: the exact-shape probe
   constructed the object with `S()` and populated frozen slots using
   `object.__setattr__`. The proof directory/ref is therefore not an opaque,
   acquisition-only capability as claimed by `plan:2171-2174` and
   `design:289-298`.

   Independent proof-repository traversal is also insufficient unless every
   object read disables Git replacement objects. Git uses `refs/replace/*` by
   default for object access; `git --no-replace-objects` or
   `GIT_NO_REPLACE_OBJECTS` is required to suppress it. Current plumbing strips
   only `GIT_INDEX_FILE` (`threeway/gitcas.py:24-29`), and the revised plan,
   design, and named selector never require replacement suppression. A caller
   can therefore substitute or mutate the exposed bare proof repository, point
   its proof ref at the real current tip, add `refs/replace/<real-tip>` mapping
   that OID to a same-type commit containing a chosen authentic event subset,
   and recompute the advertised tree/bytes/digest. Validation then re-traverses
   the substituted graph while the live tip string still equals the real tip.

   The planned forged-subset selector (`plan:2294,2303-2307`) changes snapshot
   fields against an honest retained proof repository. It does not vary caller
   construction, proof-repository substitution, a replacement ref, or ambient
   replacement semantics. Add a one-fact control in which honest acquisition
   passes and adding exactly one replacement ref at the same claimed tip fails.
   Bind validation to a non-substitutable acquisition capability and run every
   proof-object command with replacement objects disabled; sanitize repository-
   redirecting Git environment as part of the same boundary.

## Confirmed Closed Or Sufficient

- The original event-tip TOCTOU is closed at the interface level. Co-located
  refs queue both expected-old updates in one `update-ref --stdin` transaction
  and reach `prepare` before exact combined-closure import
  (`plan:2251-2256`). Remote refs bind one unique effective push endpoint and
  use one atomic two-ref push with exact leases, no sequential fallback, and no
  later retrying `store.append()` (`plan:2191-2206,2257-2265`).
- The eight exact selectors are present (`plan:2294-2301`), including honest
  snapshot acquisition plus local/remote positive controls. The local/remote
  race, cross-repository, and unsupported-atomic denials assert unchanged input
  object/ref state and forbid `RefEventStore.append()` or sequential
  publication (`plan:2312-2331`). The missing proof-capability substitution
  selector above prevents CLEAR.
- Prior remote-lock, operator-fact, cursor, and publication-grammar closures
  remain byte-identical across the Task-3A-through-3C plan segment: SHA-256
  `4be624e8d2691ad3a0ad0da0a921bd024b1a497775302cbf34f0e63575a5ab92`.
- Task 4 through EOF remains byte-identical at SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.

## Evidence

- Exact-shape Python probe:
  `@dataclass(frozen=True, slots=True, init=False) ...; s = S();
  object.__setattr__(...)` → `S claimed /tmp/proof`.
- `rg -n 'GIT_NO_REPLACE_OBJECTS|replace-objects|refs/replace' threeway scripts tests`
  → no matches.
- Git's primary documentation states that replacement refs are used by default
  for Git commands and names `--no-replace-objects` /
  `GIT_NO_REPLACE_OBJECTS` as the suppression mechanism:
  <https://git-scm.com/docs/git-replace.html>.
- `protocol_capacity_board.py --wave 2 --validate-route <12-11-02 route>` →
  route valid true; no blocking issues.
- `check_doc_claims.py <design> <plan>` → all anchors checked; no drift.
- `ci_smoke.py` → project smoke OK; ceremony, placeholder, GO-schema, and
  architecture-freshness checks pass.
- Fresh Pipeline status was clean at `b17bcf6`; the routed worktree remained
  clean at `92d1fbcd1bb76ccb377d6bca1631374569696626`; no newer route or report
  existed before this write.

No design/plan/code/packet edit, implementation, Operator GO, cursor consume,
route mutation, lock, key/ref update, push, checkout refresh, spend, pod,
generation, or other user-gated side effect was taken.

## Exact Next Trigger

Coordinator revises Task 3D so snapshot validation uses a non-substitutable
acquisition capability, disables Git replacement objects and ambient repository
redirection for every proof traversal, and adds the replacement-ref/proof-
repository substitution selector with an honest one-fact control; then reroutes
this focused Director2 closure preflight. The two-ref CAS closure and the other
lane's Task-2 work remain separate.

Cursor at send: 0
