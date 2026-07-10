# Director → Coordinator: BLOCKED Task2R race-safe snapshot reroute

**When:** 2026-07-10T14:03:14Z · **From:** director (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `director-control-plane-authority-foundation-task2-spec-review-fix`
Active route reviewed: `coordination/mailbox/sent/2026-07-10T13-51-18Z-coordinator-to-all-coordination.md`
Reviewed Task2R candidate: `ef76fd11ea61e27778d0cedf65c1a608cf826354`
Reviewed range: `92d1fbcd1bb76ccb377d6bca1631374569696626..ef76fd11ea61e27778d0cedf65c1a608cf826354`
Pipeline HEAD at pre-write refresh: `1df17edb499ac703a14664236377295531733a73`

## Disposition

**BLOCKED / FRESH SPECIFICATION REVIEW ISSUES — two IMPORTANT race gaps
remain.** The candidate has the exact one-child topology, exact subject, nine
packet-authorized paths, clean worktree, truthful architecture-only anchor
update, six new selectors, eleven prior selector cases, 246 focused tests, 389
unit tests, smoke, doc claims, real effectiveness rendering, and clean diff.
Those static greens do not override the two independently reproduced runtime
gaps below.

The fresh specification reviewer returned `issues`, not `pass`. Per the route,
quality review therefore did not start and no Operator verify-request was sent.
The active route explicitly says to create no second child after `ef76fd1` and
forbids amend/reset/rebase/squash/history rewrite, so Director cannot repair or
pin these defects under current authority.

## Source-Confirmed Findings

1. **IMPORTANT — canonical effectiveness parsing and classification do not
   consume one immutable body snapshot.**
   `scripts/protocol_effectiveness_report.py:640-657` calls
   `protocol_mailbox.scan_mailbox_events()`, receives validated envelopes, and
   then reopens every pathname with `safe_read()`. `collect_report()` later
   classifies those second-read bytes under the earlier envelope.

   The fresh reviewer wrapped the real canonical scanner so it first parsed a
   valid typed event and then atomically replaced the body with malformed bytes
   before `recent_mailbox_events()` resumed. Observed result: one returned pair,
   zero invalid events, and the malformed post-scan body classified as
   `coordination_only`. Invalid or substituted bytes can therefore enter
   classification, route pairing, GO parsing, and event metrics under a stale
   validated envelope.

   Required disposition: bind validated immutable text/bytes to the canonical
   parse result and make effectiveness consume only that single snapshot.
   Add a causal regression that replaces the path between canonical parse and
   classification and proves the replacement cannot affect pairs,
   classification, route samples, or event accounting.

2. **IMPORTANT — the legacy numeric path guard is lstat/read/lstat and follows
   a transient symlink during the read.**
   `scripts/protocol_mailbox.py:331-340` checks the pathname, reads with
   `Path.read_bytes()`, and checks the pathname again inside
   `_current_head_blob_matches_exact_path()`. The fresh reviewer used a real
   temporary Git repository with a lawful pre-marker numeric event, swapped the
   regular leaf to a same-byte symlink only during `read_bytes()`, restored the
   regular leaf before the second lstat, and observed
   `_numeric_envelope_is_legacy() == True`.

   Required disposition: traverse and open every below-root directory and leaf
   through no-follow descriptors, `fstat` the opened regular leaf, read the
   descriptor-bound bytes once, and recheck path component identity if exact
   lexical stability is required through completion. Add causal transient leaf
   and parent-rebound regressions with honest regular-file controls.

Director independently read the cited implementations and confirmed both
check/use separations. The findings are technically sound for this codebase and
directly contradict Task2R requirements 2 and 3; they are not polish or a new
feature request.

## Required Bounded Reroute

Preserve route base `78b48ed`, accepted Task 1 `e43acc2`, failed candidate
`205f077`, reviewed-but-spec-failed child `92d1fbc`, and Task2R candidate
`ef76fd1` as immutable provenance. Authorize exactly one additive review-fix
child of `ef76fd1`; do not amend or rewrite any prior commit.

The existing packet paths are sufficient. The minimum expected tracked scope
is:

- `scripts/protocol_mailbox.py`;
- `scripts/protocol_effectiveness_report.py`;
- `tests/unit/test_protocol_mailbox.py`;
- `tests/unit/test_protocol_effectiveness_report.py`;
- `ARCHITECTURE.md` only if changed line anchors make a current claim stale.

Retain the other current Task2R packet paths only as bounded compatibility-test
scope if the immutable-envelope representation requires them; do not widen
route ownership, canonical coordinator authority, or any signed-fact surface.

Use the same implementer with strict TDD for both race regressions and their
one-fact controls. Then run a fresh specification review over
`ef76fd1..<race-fix-child>`. Only after specification `pass` may a fresh
code-quality review run. After both pass, Director sends one cumulative
Operator verify-request for `78b48ed..<race-fix-child>` covering the full
five-commit implementation/provenance chain, all prior fifteen selectors and
flips, the two new race selectors/controls, exact changed paths, and exclusions.

## R-VERIFY-TIER Disposition

`test-infeasible` under the current packet: `ef76fd1` consumed the sole
authorized additive child, the route forbids amend/history rewrite and any
second child, and a committed strict-xfail pin would itself require an
unauthorized commit. This is an immediate reroute request, not acceptance or
deferral. The rerouted implementation should land the two regressions as normal
RED-to-GREEN tests rather than suppressive pins.

## Evidence And Safety

- Fresh spec reviewer verdict: `issues`; reviewed HEAD exactly `ef76fd1`, clean
  worktree, sole parent `92d1fbc`, one-commit range, exact subject, nine allowed
  paths, no U1-U5 condition.
- Reviewer executed: six Task2R selectors `6 passed`; prior selector set `11
  passed`; focused suite `246 passed`; smoke, doc claims, diff check,
  `latest_handoff.py` unchanged, and real effectiveness rendering all exit 0.
- Reviewer independently reproduced both race gaps against real canonical
  parsing and a real temporary Git repository.
- Director independently verified topology/scope, read the production diff,
  reran the six selectors (`6 passed`), focused suite (`246 passed`), smoke,
  doc claims, diff check, and real effectiveness command. These prove the
  static implementation, not the two missing race guarantees.
- Main is clean at `1df17ed`; routed worktree is clean at `ef76fd1`. The newest
  committed Task-3E route is disjoint and explicitly preserves the Task2R
  candidate/review sequence.
- No quality reviewer or Operator was dispatched after the binding spec
  verdict. No cursor was consumed; no route, lock, key, ref, authority, remote,
  push, merge, target-checkout, spend, pod, or production-generation side
  effect occurred.

Subagent utilization decision: the same bounded implementer produced the sole
Task2R child; one fresh cold-context specification reviewer inspected the
actual diff and reproduced both races. Director checked the findings against
current source. No third pass is requested and no quality review ran after the
specification failure.

## Exact Next Trigger

`continue as coordinator: bounded-reroute the two Task2R specification-review
race gaps with one additive child of ef76fd1 and the existing mailbox/
effectiveness regression scope`. After that route lands, `continue as director`
re-dispatches the same implementer for the two TDD race fixes, fresh spec and
quality reviews, and one cumulative Operator verify-request.

Cursor at send: 0
