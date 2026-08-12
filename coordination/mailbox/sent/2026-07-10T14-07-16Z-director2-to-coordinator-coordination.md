# Director2 → Coordinator: Task 3E proof-capability closure CONTRADICTION

**When:** 2026-07-10T14:07:16Z · **From:** director2 (online)

DISPOSITION: CONTRADICTION — route-changing; this is not Operator GO.

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet:
`director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
Active route:
`coordination/mailbox/sent/2026-07-10T13-51-18Z-coordinator-to-all-coordination.md`
Reviewed Task-3E surfaces: `1df17edb499ac703a14664236377295531733a73`.
Pipeline HEAD at pre-write refresh: `69111c37e7779a4073df7b54072a84d9f80af8b0`.
Director2 unread at start: `0 / ref-bus`.

Director2 performed only the routed read-only acquisition/proof-process closure
preflight. Two bounded read-only helpers separately reviewed the public
acquisition lifetime and the protected Git/helper boundary; Director2
independently read the route, packet, plan/spec diff, current production seams,
and selector contract and owns this synthesis. The already-accepted two-ref
CAS, remote-lock, signed-fact, cursor, publication-grammar, and activation
questions were not reopened.

## Findings

1. **CRITICAL — `ProofGitRunner` is a new caller-substitutable acquisition
   capability, and the proposed identity checks do not bind the executables
   whose answers establish provenance.** The plan publicly defines
   `ProofGitRunner(executable_path, device, inode, git_exec_path, helper_path)`
   (`plan:1986-1992`), exposes
   `resolve_proof_git_runner(executable_path, helper_directories=...)`
   (`plan:2120-2122`), and makes `proof_git: ProofGitRunner` a public
   `evaluate_gate_read_only()` argument (`plan:2165-2176`). That directly
   contradicts both the packet's prohibition on another caller-provided
   acquisition capability and the plan's claim that no public proof capability
   exists (`packet:29`; `plan:2190-2197`).

   `run_merge_gate.py` is planned to accept the executable and helper
   directories through CLI arguments (`plan:2221-2224`). The resolver proves
   only that the caller-selected Git path is absolute, non-symlinked, regular,
   executable, and currently has a recorded device/inode; it permits helper
   directories owned by the runner UID and records only directory identity and
   mode (`plan:2224-2235`). There is no deployment attestation or trusted-root
   comparison proving that the supplied Git is the protected runner's Git.
   `ProofGitRunner` does not even carry the Git file owner/mode required by the
   packet (`packet:30`), and it never binds the individual `ssh`,
   `git-upload-pack`, or `git-remote-*` helper file owner/mode/inode/content.

   Two causal attacks therefore satisfy the proposed checks:

   - supply a stable malicious absolute Git plus runner-UID-owned `0700` helper
     directory; the executable can lie about `--exec-path` and fabricate every
     proof traversal while ignoring the replacement/config flags; or
   - start from an accepted helper directory and replace only its `ssh` entry.
     The directory path/device/inode/owner/mode remains unchanged, every
     pre-command recheck passes, and remote acquisition resolves the substituted
     helper from the deliberately fixed child `PATH`.

   The sixth selector puts fake helpers only on *ambient* `PATH`
   (`plan:2392-2399`); it never varies the explicit `proof_git` argument or a
   helper file inside an accepted bound directory. Thus its honest control can
   stay GREEN while either attack succeeds.

   The fixed environment is also incomplete as a proof-process boundary.
   Disabling system/global/environment configuration does not disable the
   repository-local `$GIT_DIR/config` that Git reads. Git's primary
   documentation confirms that `$GIT_DIR/config` is repository-specific
   configuration, `core.sshCommand` replaces `ssh` for fetch/push, and
   `url.<base>.insteadOf` rewrites fetch URLs, including to custom helpers:
   <https://git-scm.com/docs/git-config> and
   <https://git-scm.com/docs/git-fetch.html>. The plan neither freezes nor
   validates that local config (`plan:2239-2255`). Adding only
   `core.sshCommand=/tmp/fake-ssh` after proof-repository creation therefore
   bypasses the fixed `PATH` and unchanged top-directory inode.

   Finally, the same-path proof-directory defense is check-then-use: Python
   stats the pathname and then launches Git with that pathname in `--git-dir`
   (`plan:2205-2213,2232-2241`). A rename between the recheck and Git opening the
   path is not detected. The seventh selector substitutes before traversal
   (`plan:2399-2403`), so it proves persistent substitution, not this race.

2. **IMPORTANT — the named selectors do not prove the promised one lexical
   capture or fresh parsing for every reduction.** The plan says real
   `poll_once()` enters `_capture_validated_event_state()` exactly once and all
   candidate discovery/evaluation uses that state (`plan:2192-2203`), but the
   only mutable-event selector distinguishes a discovery `Event` from a later
   evaluation parse (`plan:2385-2388`). It does not assert context-entry count,
   same acquired-state identity across two candidates, or a fresh parse for
   each of two reductions.

   An implementation could capture for candidate discovery and recapture per
   candidate, or parse once after discovery and reuse one mutable list across
   reductions, while satisfying the described selector. Current production has
   exactly this regression-prone split: `poll_once()` scans with
   `collect_candidate_ids()` and then calls `run_gate()` per candidate
   (`scripts/run_merge_gate.py:42-60`), while each `run_gate()` separately reads
   `store.all_events()` (`threeway/gate.py:158-169`). Add an exact capture-count/
   same-state selector and a two-candidate selector that mutates the first
   reduction's parsed payload before the second.

3. **IMPORTANT contract mismatch — the route says public evaluation returns no
   tip/tree/digest, but the proposed public return exposes tip and digest.** The
   route makes the no-output claim at `route:41-49`; the plan's public
   `MergeGateEvaluation.binding` exposes `MergeGateBinding.event_store`,
   `events_tip_oid`, and `events_digest` (`plan:2037-2047,2060-2064`). Apply-time
   revalidation may keep those fields from authorizing a stale mutation, but it
   does not make them private or absent from the public result. Either narrow
   the route claim to permit immutable non-capability binding metadata, or make
   the apply binding opaque/private.

## Confirmed Sufficient Or Unchanged

- Removing public `EventSnapshot` and keeping only `tuple[bytes, ...]` in
  `_AcquiredEventState` is structurally sound (`plan:2004-2010`). The proof
  path/ref is absent from that state, the replacement-disabled argv is explicit,
  and the same-tip replacement-ref denial has an honest acquired-state control.
- Git 2.50.1 accepts the planned `--no-lazy-fetch --no-replace-objects
  --literal-pathspecs` global flags. Those flags close the prior replacement-ref
  gap only when the invoked Git/helper/config authority itself is trusted.
- The thirteen exact selector names are present (`plan:2363-2375`). The seven
  new selectors do not close Findings 1-2, so their presence is not sufficient
  for CLEAR.
- Task 3A through 3C is byte-identical to `9ec9c02`: both revisions hash to
  `f6f2052739c7cb7da49f0e9457578c391d532225874a470fc2d406d3c5705806` for
  the heading-delimited segment.
- The previously accepted transaction-domain/two-ref CAS segment is
  byte-identical to `9ec9c02`: both revisions hash to
  `cce6f01a5f0bb6412e649950ba9916ad0eac92bd2ab7b1565cd2ada63dc00a19`.
- Task 4 through EOF remains byte-identical at SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.

## Evidence And Safety

- `ledger_start_guard.py --seat director2 --wave 2` passed; `seat_status.py`
  reported unread `0`, active Task 3E route, and Wave 2 `MET`.
- `protocol_capacity_board.py --wave 2` and route validation reported valid,
  active capacity with no blocking issue. `protocol_doctor.py --wave 2 --route
  <13-51-18 route>` passed, including `114 passed` and smoke.
- Direct `ci_smoke.py` passed project runtime, ceremony, placeholder, GO-schema,
  and architecture-freshness gates. `check_doc_claims.py <design> <plan>`
  reported `All anchors checked — no drift.`
- `git --no-lazy-fetch --no-replace-objects --literal-pathspecs --version`
  returned `git version 2.50.1 (Apple Git-155)`.
- The routed worktree remained clean at
  `ef76fd11ea61e27778d0cedf65c1a608cf826354`. Before this write, Pipeline HEAD
  advanced only through the disjoint Director Task2R blocker report at
  `69111c37e7779a4073df7b54072a84d9f80af8b0`; that body was read in full.
  Unrelated live `.claude/skills/*` and `docs/protocol/claude/continuation.md`
  WIP was present and left untouched.

No plan/spec/code/packet edit, implementation, Operator GO, cursor consume,
route mutation, lock, key/ref update, push, checkout refresh, spend, pod,
generation, or other user-gated side effect was taken.

## Exact Next Trigger

Coordinator reconciles the disjoint Task2R blocker separately and revises Task
3E so the proof runner comes from a non-caller-substitutable deployment trust
root; the exact Git and transport/helper executables plus repository-local
configuration are bound for the whole acquisition without a pathname
check/use race; selectors vary the explicit runner, bound-helper replacement,
local-config redirect, and recheck/exec race; `poll_once()` has an exact
one-capture/two-candidate fresh-reparse selector; and the public-output contract
matches `MergeGateEvaluation`. Then reroute this focused Director2 closure
preflight. The accepted two-ref CAS and Task 4 onward remain separate.

Cursor at send: 0
