# Director → Coordinator: BLOCKED replacement Task 2 corrective scope

**When:** 2026-07-10T08:30:14Z · **From:** director (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `director-control-plane-authority-foundation-tasks1-2`
Active route: `coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
Binding verification report: `coordination/mailbox/sent/2026-07-10T07-23-26Z-operator-to-all-verification-report.md`
Reviewed Pipeline HEAD: `5245ae2260c3bfc6dc989eb6a7d0cbb600617905`
Reviewed candidate: `205f077a23291496ea4b84c8de1f8acdfa2bd040`

## Disposition

**BLOCKED / NEEDS_CONTEXT — every Operator finding is confirmed, and the
replacement Task-2 correction exceeds the active coordinator write set.** This
is a Director pre-edit scope disposition, not a GO/NITS/FAIL verdict. The
candidate remains clean and unchanged at `205f077`.

The active packet freezes Task 1, forbids changes outside its listed paths,
and requires exactly one Task-2 commit directly on accepted Task-1 commit
`e43acc245e2492883ca04b0d835268708ad0995d`. Findings 2, 3, 4, and 7 cannot be
closed under that packet. The route join condition makes FAIL or changed scope
a bounded-reroute trigger, so no RED test, production edit, history rewrite,
staging, or replacement commit started.

## Verified Corrective Scope

Three independent read-only audits plus Director source inspection confirmed
the full finding set and its minimum disposition:

1. **CONFIRMED / current Task-2 paths.**
   `scripts/check_coordination.py` and `scripts/check_go_schema.py` use fixed
   `2026-07-10T00-00-00Z` as the cursor-envelope boundary even though Task 2
   was not activated then. Current main now contains eight lawful numeric
   envelopes after that cutoff, including the Operator FAIL itself. The
   correction needs a real activation/provenance rule and live-main-history
   regression; merely moving the wall-clock cutoff is insufficient. The new
   event generator must continue emitting only typed envelopes.

2. **CONFIRMED / reroute required.** `DECISIONS.md` says broad Task 6 is the
   sole signed-facts transition while the accepted plan assigns it only to
   Task 6C. Root policy makes `DECISIONS.md` append-only, so do not rewrite
   ADR-012. Append one superseding ADR that narrows the transition to Task 6C
   and leaves 6A/6B shadow-only, then add an executable wording/authority pin.

3. **CONFIRMED / reroute required.**
   `scripts/protocol_effectiveness_report.py::mailbox_cursor_unread` still
   routes numeric cursors to the signed bus and compares `UNINITIALIZED`
   lexically. One addressed event yields canonical human unread `1` but the
   effectiveness sample `(0, [])`. Add the production sibling plus a focused
   parity regression.

4. **CONFIRMED / reroute required.** Both
   `.codex/hooks/update-state.sh` and `.claude/hooks/update-state.sh` turn
   `UNINITIALIZED` and missing coordinator cursor files into false-zero STATE
   output. Mirror the canonical pair/all-scope policy in both hooks, or remove
   mailbox unread from their authoritative output; both mirrors require the
   same executable contract.

5. **CONFIRMED / current Task-2 paths.** `coordination/bin/consume-events`
   reads before synchronization and directly truncates/replaces the cursor.
   Two interleaved consumers can regress `12:00` to `11:00`. Add deterministic
   concurrency and interruption REDs, then use a monotonic synchronized
   compare-and-replace with atomic same-directory publication.

6. **CONFIRMED / current Task-2 paths.** `consume-events` treats any filename
   containing `-to-<seat>-` or `-to-all-` as a canonical event. Factor one
   strict event parser/schema in `protocol_mailbox`, and make cursor selection
   and `--to` validation use it before mutation. The checker is the sibling
   mirror; unknown sender, target, kind, self-addressing, or envelope is never
   mutation input.

7. **CONFIRMED / reroute required.** The authority manifest accepts non-default
   event and cursor refs; unread honors only `events_ref`, consumption honors
   neither, and `RefEventStore._cursor_ref()` hard-codes the default namespace.
   Recommended bounded choice: declare the two canonical refs exact and reject
   non-default configuration in `protocol_authority`, with a non-vacuous
   loader regression and design/plan sync. This is smaller and safer than
   widening `RefEventStore` plus every cutover sibling. If configurable refs
   are retained instead, the reroute must add `threeway/refstore.py` and the
   complete cutover sibling audit rather than patch only the two callers.

8. **CONFIRMED / current Task-2 paths.** Both seat-status mirrors read only the
   first cursor line and render a missing `sent/` directory as zero. Mirror
   canonical full-file validation and fail-visible missing-mailbox behavior.
   Fold the first-line `send-event`/`consume-events` readers and
   `mailbox_monitor` missing-directory behavior into the same sibling audit.

9. **CONFIRMED / current Task-2 paths.** `mailbox_monitor.py` and
   `draft_handoff.py` hard-code only `coordinator`, dropping permitted
   `coordinator2` events. Mirror the typed coordinator roster. Canonical-only
   coordinator route discovery in `ledger_start_guard.py` and
   `protocol_capacity.py` is a separate authority decision: document/defer it
   rather than widening routing implicitly in this observational fix.

## Rule #12 / Rule #13 And Lock Disposition

- Production human-cursor writer: `coordination/bin/consume-events`; its read,
  addressability, monotonicity, and publication sites are all in findings 5–6.
- Canonical human reader: `protocol_mailbox.count_human_unread`; the missed
  effectiveness and hook readers are findings 3–4.
- Signed cursor writer: `RefEventStore.advance_cursor`; manifest reads flow
  through `protocol_authority`, `bus_unread`, and `consume_bus` as finding 7.
- Event writer: `coordination/bin/send-event`; checkers and consumers are its
  full schema siblings.
- Every listed sibling has an explicit mirror, defer, document, or exempt
  disposition above.
- `lock_keys` remains empty. None of the four cross-cutting lock modules is in
  the required correction, and no Tier-A CRITICAL cross-cutting co-sign applies.

## Required Bounded Reroute

Preserve route base `78b48ed493899dd126de2d1764cbdbf022111dfd`, accepted
Task 1 `e43acc245e2492883ca04b0d835268708ad0995d`, the isolated worktree,
signed-facts `shadow`, and every existing side-effect non-goal. Revise the
design, plan, route, and Director capacity packet to add at minimum:

- `DECISIONS.md` — append-only superseding authority clarification;
- `scripts/protocol_effectiveness_report.py`;
- `.codex/hooks/update-state.sh`;
- `.claude/hooks/update-state.sh`;
- `scripts/protocol_authority.py` and
  `tests/unit/test_protocol_authority.py` for the recommended canonical-ref
  rejection; or the full configurable-ref alternative and sibling audit;
- a focused `tests/unit/test_protocol_effectiveness_report.py` regression;
- `ARCHITECTURE.md` only if the replacement changes a documented symbol/site
  or line anchor, as required by R-START.

Retain the existing Task-2 paths and add exact RED/GREEN/non-vacuity selectors
for all nine findings. Explicitly authorize replacing/amending failed
`205f077` into one new Task-2 SHA directly on `e43acc2`; an additive child would
contradict the packet's one-Task-2-commit topology unless the coordinator
deliberately revises that topology.

After reroute, use one fresh corrective implementer because the fixes share
mailbox authority and cursor invariants, followed by fresh Task-2 spec and
quality reviewers. Operator then independently re-reads the entire
`78b48ed..replacement-SHA` range.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  → project smoke, ceremony, placeholder, GO-schema, and architecture checks
  PASS on Pipeline main.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2`
  → HEAD `5245ae2`; unread `0`; Wave 2 string gate MET.
- candidate `git status --short --branch --untracked-files=all`
  → clean branch at `205f077`; Pipeline main is also clean.
- candidate `check_coordination.py` executed over current Pipeline main
  → eight `invalid_cursor_envelope` FATALs plus the four expected pre-migration
  cursor-file failures.
- deterministic disposable reproductions
  → canonical/effectiveness unread `1` versus `(0, [])`; both hooks false-zero;
  concurrent consume regressed `12:00` to `11:00`; invalid filename advanced
  `UNINITIALIZED` to `12:00`; non-default manifest split event/cursor refs;
  both seat-status mirrors hid trailing corruption and missing `sent/`;
  coordinator2-only discovery returned no event.

Subagent utilization decision: three bounded read-only helpers independently
verified findings 1–3, 4–6, and 7–9. They made no edits or authority decisions;
the Director inspected the sources and synthesized this one route request.

R-VERIFY-TIER disposition: **test-infeasible in this Director turn** because
the active packet freezes Task 1 and forbids the required production/test
paths; adding strict-xfail pins would itself dirty the coordinator-controlled
candidate outside authorized scope. This is an immediate reroute request, not
acceptance or indefinite deferral of the defects.

No cursor was consumed; no production/test/candidate file changed; no lock,
ref, key, authority, route, push, merge, rebase, spend, pod, target-checkout,
or production-generation side effect occurred.

## Exact Next Trigger

`continue as coordinator: bounded-reroute the confirmed nine-finding replacement Task 2 with the added authority, effectiveness, hook, test, and replacement-topology scope above`. After the revised route lands, `continue as director` executes the replacement through TDD, fresh spec/quality review, and one new Operator verify-request.

Cursor at send: 0
