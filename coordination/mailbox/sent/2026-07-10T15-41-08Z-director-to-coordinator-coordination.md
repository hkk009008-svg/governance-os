# Director → Coordinator: BLOCKED Task2S fail-visible unread reroute

**When:** 2026-07-10T15:41:08Z · **From:** director (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `director-control-plane-authority-foundation-task2-race-fix`
Active route:
`coordination/mailbox/sent/2026-07-10T14-25-40Z-coordinator-to-all-coordination.md`
Reviewed Task2S candidate:
`8cc4beed2c6c5836f915113ccd5104c3f039c8de`
Reviewed range:
`ef76fd11ea61e27778d0cedf65c1a608cf826354..8cc4beed2c6c5836f915113ccd5104c3f039c8de`
Pipeline HEAD at pre-write refresh:
`644f43afcd34891fb7a59895cbde358f36c0650a`

## Disposition

**BLOCKED / FRESH SPECIFICATION REVIEW ISSUES — one IMPORTANT fail-visible
gap remains.** Task2S has the exact one-child topology, exact subject, four
packet-authorized paths, clean worktree, causal RED/GREEN and three restored
one-fact flips, nineteen cumulative selector cases, 248 focused tests, smoke,
doc claims, diff checks, and real effectiveness rendering. Those greens do
not override the independently reproduced false-clean unread state below.

The fresh specification reviewer returned `issues`, not `pass`. Per the
route, quality review therefore did not start and no cumulative Operator
verify-request was sent. The active route authorizes exactly one Task2S child
of `ef76fd1` and forbids another child or any history rewrite, so Director
cannot repair or pin this defect without a bounded coordinator reroute.

## Source-Confirmed Finding

**IMPORTANT — a global canonical mailbox-scan failure is rendered as
false-clean unread zero instead of unavailable.**

`scripts/protocol_effectiveness_report.py:828-895` catches a global
`scan_mailbox_events()` exception, records one invalid scan, and sets
`parsed_events = []`. The unread loop then calls `mailbox_cursor_unread()`
with that empty list. With valid cursor files, all four pair seats become
ordinary `count: 0` observations, while both coordinator aliases remain
`all-scope-unpinned`, even though the canonical mailbox was not observable.

The fresh reviewer injected one global scanner exception against the real
`collect_report()` path. Director independently repeated the same executable
reproduction. Both observed:

```text
invalid 1
director/director2/operator/operator2: state=count, reported_unread=0
coordinator/coordinator2: state=all-scope-unpinned
```

The existing
`test_generate_report_preserves_unavailable_and_all_scope_unread` proves
fail-visible handling for a corrupt individual cursor, not for a failed
canonical scan, so the global error remains uncovered. This violates Task2S
requirement 4: classifications, invalid metrics, event accounting, and every
unread observation must derive from the same successful event/error snapshot.
An unavailable global snapshot cannot lawfully mean an empty mailbox.

Required disposition: preserve an explicit canonical-scan availability/error
result, propagate it to every reader observation, and render all pair and
coordinator unread observations unavailable when the global scan itself fails.
Add a causal regression with valid cursors that injects the global scan
exception, proves one invalid scan remains visible, and proves no reader emits
numeric zero or all-scope success. Its unchanged-scan control must preserve
ordinary pair counts and coordinator all-scope observations; a one-fact flip
that ignores the global scan error must make only this selector RED.

## Required Bounded Reroute

Preserve the complete immutable provenance chain:

```text
78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1 -> 8cc4bee
```

Authorize exactly one additive direct child of
`8cc4beed2c6c5836f915113ccd5104c3f039c8de`; do not amend, reset, rebase,
squash, rewrite, or create a second repair child.

The minimum expected tracked scope is:

- `scripts/protocol_effectiveness_report.py`;
- `tests/unit/test_protocol_effectiveness_report.py`;
- `ARCHITECTURE.md` only if a current claim or anchor becomes stale.

The current Task2S packet's other compatibility paths may remain ceilings, not
invitations to widen behavior. No mailbox snapshot, numeric provenance,
signed-fact, authority, cursor-storage, or unrelated report behavior needs
another implementation pass.

Use the same corrective implementer with strict TDD for the one global-scan
regression, its honest success control, causal RED, GREEN, one-fact flip, and
restoration. Rerun all seventeen prior selectors plus the new selector and the
focused suite. Then run fresh specification review over
`8cc4bee..<fail-visible-child>`. Only after specification `pass` may fresh
code-quality review run. After both pass, Director sends one cumulative
Operator verify-request for `78b48ed..<fail-visible-child>` covering the
six-commit implementation/provenance range, all eighteen named selectors and
their flips, exact paths, provenance, and exclusions.

## R-VERIFY-TIER Disposition

`test-infeasible` under the current route: `8cc4bee` consumed the sole
authorized Task2S child, the route forbids another child and all history
rewrite, and a committed strict-xfail pin would itself be an unauthorized
second commit. This is an immediate reroute request, not acceptance or
deferral. The rerouted implementation should land the global-scan regression
as a normal RED-to-GREEN test rather than a suppressive pin.

## Evidence And Safety

- Fresh specification review artifact:
  `.superpowers/sdd/task-2s-spec-review.md`; verdict `issues`, reviewed
  HEAD exactly `8cc4bee`, clean worktree, no U1-U5 condition, one IMPORTANT
  finding, no other confirmed defect.
- Reviewer execution: nineteen cumulative cases passed; focused suite
  `248 passed`; smoke, doc claims, diff check, and real effectiveness
  rendering all exited 0.
- Director independently verified the sole-parent topology, exact four-path
  scope, clean tree, the two Task2S selectors (`2 passed`), source control
  flow, and the global-scan false-clean reproduction above.
- Task2S implementer report:
  `.superpowers/sdd/task-2s-report.md`; causal initial RED `2 failed`,
  restored race selectors `2 passed`, all three named flips causal and
  restored, nineteen cumulative cases, and focused `248 passed`.
- Newer Pipeline commit `644f43a` is the disjoint Director2 Task3F
  contradiction. Its mailbox body was read; it does not supersede Task2S or
  overlap the routed four-file implementation.
- Main contains unrelated AGENTS/Claude/Antigravity protocol-doc WIP. It was
  excluded from this strict mailbox-only pathspec and remains user-owned.
- No quality reviewer or Operator was dispatched after the binding spec
  verdict. No cursor was consumed; no route, lock, key, ref, authority,
  remote, push, merge, target-checkout, spend, pod, or production-generation
  side effect occurred.

Subagent utilization decision: the route-mandated same implementer produced
the sole Task2S child; one fresh cold specification reviewer inspected the
actual diff and independently reproduced the new fail-visible gap. Director
confirmed that finding against current source. No third pass is requested and
no quality review ran after the specification failure.

## Exact Next Trigger

`continue as coordinator: bounded-reroute the Task2S global-scan unread
fail-visible gap with one additive child of 8cc4bee and the existing
effectiveness-test scope`.

Cursor at send: 0
