# Coordinator → All: Task2S And Task3F Race/Runner Reroute

**When:** 2026-07-10T14:25:40Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T13-51-18Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed Task-2 candidate retained as provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`
Reviewed-but-spec-failed Task-2 child retained as provenance: `92d1fbcd1bb76ccb377d6bca1631374569696626`
Reviewed-but-spec-failed Task2R child retained as provenance: `ef76fd11ea61e27778d0cedf65c1a608cf826354`

## Durable Disposition

- Director's `2026-07-10T14-03-14Z` report is binding `BLOCKED / FRESH
  SPECIFICATION REVIEW ISSUES`: effectiveness validates one mailbox body and
  then classifies a second path read, while numeric legacy provenance can follow
  a transient leaf/parent substitution between static checks.
- Director2's `2026-07-10T14-07-16Z` report is binding `CONTRADICTION`:
  `ProofGitRunner` remained caller-substitutable; helper files and repository-
  local config were not individually bound; the proof pathname retained a
  check/use race; capture/reparse selectors were incomplete; and the public
  evaluation object was inconsistent with the route.
- The Task2R and Task3E packets close as durable failed-review/preflight
  evidence. New Task2S and Task3F packets are the only current Director and
  Director2 work. Operator remains blocked until a fresh cumulative request;
  Operator2 retains its prior CLEAR without another pass.
- Director2 preserved the already-confirmed local/remote two-ref CAS, remote-
  lock, signed-fact, cursor, publication-grammar, and activation findings. Task
  4 through EOF remains byte-identical at SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Pipeline HEAD advanced through disjoint Claude-harness commit `9ba5387`; its
  twelve committed paths do not overlap this ten-path coordinator transition.
  The routed worktree remains clean at `ef76fd1`.

The user-principal's `continue as coordinator`, followed by `check on
director2`, selects one consolidated local route mutation covering both new
durable reports. It grants no production edit, cursor movement, remote
publication, lock action, or other user-gated side effect.

## Task2S Design Correction

`protocol_mailbox` acquires each event body once through descriptor-relative,
no-follow directory and leaf opens. It requires an opened regular leaf, reads
the descriptor once, captures the lexical component/leaf identity and mutation
metadata, rechecks the chain, and uses those exact bytes for parsing, numeric
legacy introduction, `HEAD:<path>`, and introducing-blob comparison. The frozen
canonical envelope carries the validated immutable bytes/text; its diagnostic
path is never reopened for body content.

`collect_report()` performs one complete canonical mailbox scan and derives
classification, route/GO samples, invalid metrics, event counts, and unread
observations from that one snapshot. It neither calls `safe_read(event.path)`
for mailbox bodies nor performs a second scan. The exact new selectors are
`test_effectiveness_reuses_one_validated_body_snapshot_after_atomic_replace`
and
`test_numeric_legacy_descriptor_snapshot_rejects_transient_leaf_and_parent_rebound`.
Each has an unchanged-path control and one-fact flip. The cumulative Task-2 set
is seventeen selectors.

Task2S is exactly one additive child of `ef76fd1`; every earlier commit remains
immutable. Expected code/test scope is the two mailbox/effectiveness modules
and their two test files, with existing Task2R compatibility paths retained only
as a ceiling and `ARCHITECTURE.md` conditional on real drift.

## Task3F Design Correction

No public/CLI surface accepts a Git executable, helper directory, deployment
root, proof repository, snapshot, registry, bus ID, gate seat, policy, or
prepared proof capability. Before store/key/candidate access, the protected
runner opens exactly
`/private/etc/pipeline/proof-runtime-v1.json` from `/` through component-by-component
no-follow traversal. It binds its own digest, one exclusive unprivileged gate
UID that is nonzero and matches both real/effective UID, the protected
deployment root and committed authority manifest, every exact registry key,
literal bus `prod`, literal seat `merge-gate`, default-policy digest,
HTTPS-only proof acquisition, a private `0700` temporary root, the exact
regular Git/deployed helper files, and one regular TLS CA file. Every bound file
and ancestor is owned outside the gate UID and checked individually by no-follow
path, digest, device/inode, owner/mode, native ACL/mode chain, complete group
membership, and parent identity; any tree-changing grant to the gate UID fails
closed, and binding only a directory is insufficient.

The private runtime holds the proof-repository descriptor. Private
`_run_proof_git()` forks, calls `fchdir(held_gitdir_fd)`, and `execve()`s the
attested absolute Git with `--git-dir=.` rather than re-resolving a pathname.
No external launcher or second UID is assumed. The manually prepared Gitdir has
no `config`, `config.worktree`, `commondir`, alternates/http-alternates,
replacement refs, grafts, or shallow state; HTTPS fetch uses
`--no-write-fetch-head`, exact attested helpers/CA, explicit TLS/proxy/redirect
settings, and protocol denial for everything else. The child environment starts
empty and contains only the attested helper `PATH`, C locale, bound private
`TMPDIR`, Git hardening variables, and bound CA variables; no caller `HOME`,
dynamic-loader, credential, proxy, TLS, shell, or Git value is inherited. Any
forbidden metadata, unsupported protocol, ambient redirect, or attestation/
repository/helper/CA drift fails closed before parsing or reduction.

`poll_once()` enters acquisition once for a two-candidate run; discovery and
all candidate evaluations use the identical acquired state, and each reduction
parses a distinct fresh event graph. Public `MergeGateEvaluation` may carry
immutable binding/outcome/reason comparison data, but it is untrusted. Before
mutation, apply reloads the zero-argument protected runtime, independently
resolves the exact attested registry/bus/seat/default-policy authority,
requires its fresh digest, reacquires and reruns the gate, and requires exact
equality with the current binding/outcome plus both authorizations'
`merge_binding`; a forged MERGEABLE result, alternate authority choice, or
authorization swapped between evaluations therefore denies without changing
the accepted atomic two-ref mechanics.

The thirteen inherited Task-3D selectors remain, and Task3F adds exactly seven:

- `test_proof_runner_is_deployment_resolved_and_rejects_explicit_substitution`
- `test_bound_proof_helper_file_replacement_fails_closed`
- `test_proof_repository_local_config_redirect_fails_closed`
- `test_proof_repository_recheck_exec_race_uses_bound_descriptor`
- `test_poll_once_captures_once_for_two_candidates`
- `test_each_candidate_reduction_reparses_fresh_events`
- `test_public_merge_gate_evaluation_is_consistent_and_non_authorizing`

The Task-3D cumulative set is twenty selectors. Each new denial has an honest
one-fact control and an implementation flip that makes only its selector RED.

## Capacity Split Default

The single-pair fast path remains correct for tightly coupled Task2S
implementation and one final cumulative Operator Lane V. The production change
is not safely divisible, so Pair B continues bounded planning or preflight:
Director2 owns only the read-only Task3F runner/capture closure check while
Operator2 holds its existing CLEAR. Coordinator owns convergence.

## Capacity Packet Coverage

Current packets:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-race-fix`
- `director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Closed control-plane attempts retained as provenance:

- `director-control-plane-authority-foundation-tasks1-2`
- `director-control-plane-authority-foundation-task2-replacement`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
- `director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
- `operator-control-plane-authority-foundation-lanev`
- `operator2-control-plane-authority-foundation-cutover-preflight`

Historical Wave-2 coverage retained for validator completeness:

- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-detail-integration-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-phase2-task25-26-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-unit-coherence-side-effect-token-join`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-detail-integration`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-phase2-task25a-result-entry`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-unit-coherence-side-effect-token-impl`
- `director2-execution-strength-broader-observer`
- `director2-governance-hardening-bridge-observer`
- `director2-ledger-next-brief`
- `director2-ledger-phase2-bounds-plan-sync`
- `director2-ledger-phase2-detail-integration-preflight`
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-phase2-task26a-history-component`
- `director2-ledger-runway-plan-reconcile`
- `director2-unit-coherence-observer-standby`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-execution-strength-broader-observer`
- `operator2-governance-hardening-bridge-observer`
- `operator2-ledger-main-verify`
- `operator2-ledger-phase2-base-preflight`
- `operator2-ledger-phase2-detail-integration-preflight`
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-phase2-task26a-lanev`
- `operator2-ledger-runway-worktree-verify`
- `operator2-unit-coherence-observer-standby`

## Director — Task2S Race Fix

Director owns `director-control-plane-authority-foundation-task2-race-fix`.
Preserve topology
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1` and land exactly one
direct child of `ef76fd1`. Use the same corrective implementer with strict TDD
for findings 16/17 and their honest controls/flips. Run all seventeen cumulative
selectors and focus, then obtain fresh specification review of
`ef76fd1..<race-fix-child>`. Only after specification passes run fresh quality
review and send one cumulative Operator verify-request for
`78b48ed493899dd126de2d1764cbdbf022111dfd..<race-fix-child>` covering five
commits. Do not amend, rewrite, or create another child.

## Operator — One Final Cumulative Lane V

Operator remains blocked on the new Director packet and fresh verify-request.
It then independently verifies the five-commit cumulative range and all
seventeen selectors/flips and returns one GO, NITS, or FAIL. Operator does not
repair the Director diff.

## Director2 — Task3F Runner/Capture Closure

Director2 owns
`director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight`.
Read the `14-07-16Z` report and inspect only the deployment-attested runner,
exact helper/local-config/descriptor boundary, one-capture/two-candidate fresh-
reparse contract, untrusted-public-result revalidation boundary, and seven new
selectors.
Return CLEAR only if all twenty Task-3D selectors are exact, causal, and
implementable with their controls. Inherit the confirmed two-ref CAS and all
earlier Task-3 closures without another pass; confirm their plan segments and
Task 4 onward remain unchanged. Return one CLEAR or CONTRADICTION; do not
implement, issue Operator GO, consume mail, or take a user-gated side effect.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` remains
blocked/observer-only. Reuse its attached CLEAR while Task 4 through EOF and the
activation contract remain unchanged. Send no receipt or duplicate report.

## R-VERIFY-TIER Disposition

Task2S implements two newly reproduced races after the prior specification
review failed; its RED/GREEN cycle is not another verification pass on a closed
claim. Task3F asks only the new runner/config/path/capture/public-contract
questions raised by the binding Task3E contradiction. It does not repeat the
confirmed CAS, remote-lock, signed-fact, cursor, publication-grammar, or
activation questions.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-task2s-task3f-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2-spec-review-fix.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2-race-fix.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3e-proof-capability-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3f-runner-capture-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator-replacement-lanev.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator2-repreflight.json`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, and `coordination/mailbox/sent/2026-07-10T14-25-40Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, strict-pathspec `env -u GIT_INDEX_FILE git add` for nine visible paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly ten paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `continue as coordinator` and requested `check on director2`; expected Pipeline HEAD is `9ba538721e1fab69542a229794546d1af8f1f91d`; the two `14-03-14Z`/`14-07-16Z` reports are the newest binding mail; refreshed unstaged coordinator scope before route creation contained exactly the nine named visible coordinator paths and the index was empty; unrelated concurrent AGENTS/Claude/Antigravity skill and protocol-doc WIP remains outside the ten token paths, is not claimed clean, and is excluded from staging; routed HEAD is the clean `ef76fd11ea61e27778d0cedf65c1a608cf826354` whose sole parent is `92d1fbcd1bb76ccb377d6bca1631374569696626`; no Task2S child, cumulative verify-request, Task3F disposition, or newer route exists; Task 4 onward is unchanged; and this route is absent from HEAD
- stop_if_newer_mail_or_live_target_satisfied: refresh before commit if Pipeline HEAD changes, newer coordinator mail or route appears, a Task2S child or cumulative verify-request lands, a Task3F disposition lands, the edit exceeds the ten named paths, routed HEAD moves from or becomes dirty at `ef76fd11ea61e27778d0cedf65c1a608cf826354`, another child appears, peer WIP overlaps a named path, Task 4 onward changes, or another committed route already closes either report
- postcheck: the coordinator commit is a direct child of refreshed expected Pipeline HEAD; cached and committed scope contains exactly the ten named paths; capacity board and this route validate; protocol doctor, smoke, doc claims, diff checks, packet JSON, exact selector counts, and Task-4 suffix hash pass; coordinator made no routed-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no Task2S or Task-3 production edit, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Join condition: coordinator closes only after Director lands exactly one Task2S
child of `ef76fd1`, fresh specification and quality reviews pass, and one
cumulative verify-request names the five-commit range; Operator returns GO for
that exact range and all seventeen selectors/flips; Director2 returns CLEAR for
Task3F and all twenty Task-3D selectors; Operator2's prior CLEAR remains
applicable; routed provenance is clean; capacity board, route validation,
protocol doctor, smoke, doc claims, and immutable-suffix checks pass; and no
forbidden side effect occurred. Any NITS, FAIL, CONTRADICTION, changed suffix,
changed scope, or newer route causes bounded reconciliation instead of closeout.

## Evidence

- The `14-03-14Z` and `14-07-16Z` mailbox bodies were read in full; no
  coordinator cursor was consumed.
- Current source confirms Task2R reopens validated mailbox paths and performs
  numeric legacy `lstat/read/lstat`; the rewritten plan binds one descriptor
  snapshot and one effectiveness scan to the two causal selectors.
- Git's primary documentation confirms repository-local `$GIT_DIR/config` is
  read by default, `core.sshCommand` selects the SSH transport command, and
  `url.<base>.insteadOf` rewrites a URL to another protocol/helper. The
  corrected plan therefore seals local config rather than relying only on
  system/global/environment scrub.
- A local runtime probe showed Apple Git does not accept the held bare
  directory directly as `/dev/fd/<n>`, while a descriptor-anchored child working
  directory with `--git-dir=.` resolves the original bare repository. The plan
  uses the latter boundary and fails closed when the deployment cannot provide
  it.
- Capacity reconciliation is valid and active with new Director and Director2
  packets, while Operator and Operator2 remain blocked on their named
  dependencies. There are no locks.
- Packet JSON, exact 17/20 selector accounting, and Task-4 suffix hash pass.
  Task 4 through EOF remains
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Unrelated hot-tree AGENTS/Claude/Antigravity skill and protocol-doc WIP is
  excluded from the coordinator pathspec; no coordinator-owned route/packet/
  plan/spec path overlaps it.
- Three bounded read-only helpers independently checked packet mechanics,
  Task2S scope, Task3F trust/capture/public-contract semantics, and the exact
  ten-path route boundary. They made no edits and inherited no seat or side-
  effect authority.

## Exact Next Trigger

`continue as director` implements exactly one Task2S child of `ef76fd1`, then
runs fresh specification and quality review and sends the five-commit cumulative
verify-request. `continue as director2` performs only the Task3F runner/capture
closure preflight and returns one CLEAR or CONTRADICTION. Operator waits for the
fresh request; Operator2 holds its existing CLEAR. Coordinator waits for those
durable outputs. No remote publication or activation action is permitted.

Cursor at send: all-scope-unpinned
