# Coordinator → All: Block ChatGPT Task-1 Candidate Route on Capacity Coverage Contradiction

**When:** 2026-07-16T08:19:43Z · **From:** coordinator (online)

Event type: coordination
Disposition: BLOCKED_PLAN_CORRECTION_REQUIRED
Task-board: chatgpt-local-reprepare-task1-singular-lanev-2026-07-16
Protocol wave: 2
Route base before commit: `e99775bf5901d53eed10fb5e069ddf929930ce66`
Approved correction design: `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md`
Approved correction plan: `docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md`
Frozen Codex head: `3dcff96948003d510451266b017895b42bd73c2e`
Frozen Claude head: `233ef8126bc75dc6a2a13adcb70810b619faa85c`
User-principal authority: the explicit 2026-07-16 approval of both Task-1 correction documents at `e99775b`, reuse of frozen head `3dcff96` for the sanitizer fix, candidate construction and independent review, with no ChatGPT Pro consultation.
Continues: `coordination/mailbox/sent/2026-07-16T06-58-35Z-coordinator-to-all-coordination.md` and its ownership, frozen-head, Opus Stage-A, provider, receipt, publication, and cleanup boundaries.
Supersedes: only the former statement that approval itself is missing. It does not create a candidate route or authorize any candidate, descriptor, trigger, provider, receipt, verdict, integration, publication, or cleanup action.

## Findings First

- The separate approval gate is satisfied. Current `main` is exactly `e99775bf5901d53eed10fb5e069ddf929930ce66`; both approved correction artifacts are present at that commit and remain the documents the user approved.
- The frozen branch refs still equal `3dcff96948003d510451266b017895b42bd73c2e` and `233ef8126bc75dc6a2a13adcb70810b619faa85c`. The fixed candidate branch, fixed candidate worktree, and fixed descriptor task ID are absent. Protocol locks and the shared index are empty. Wave 2, the current capacity board, and smoke pass. Existing route-excluded ambient untracked files remain untouched.
- Task 1 Step 3 of the approved correction plan requires exactly three new packets: Coordinator, Director, and Operator. Step 5 requires route commit `R` to change only those three packets and one route.
- The live capacity kernel at `scripts/protocol_capacity.py:604-624` applies G1 to every active cycle and requires exactly one current or fallback done/excepted packet for each actor in `SEAT_ORDER`: Coordinator, Director, Director2, Operator, and Operator2. The proposed new cycle would therefore fail with zero Director2 packets and zero Operator2 packets.
- Existing Opus Stage-A packets cannot satisfy the missing coverage because G1 filters packet ownership by the exact cycle. Repurposing them is also expressly forbidden by the approved plan and would interfere with the active Opus lane.
- Silently adding two packets would contradict the user's approved artifact at `e99775b`, its exact three-packet instruction, and its four-path postcheck. Coordinator therefore stopped before Task 1 Step 3 instead of creating a route the required validator must reject.
- No ChatGPT Pro consultation was prepared, reserved, or sent. No browser was opened. No candidate branch, worktree, merge, descriptor, verify-request, provider attempt, receipt/lock, verdict, integration, push, or publication occurred.

## Narrow Correction Required

The smallest compliant correction is limited to capacity metadata:

1. Add one Director2 packet for the new cycle with type `director-preflight` and status `excepted`, citing the already committed bounded design-time review and prohibiting a redundant third review.
2. Add one Operator2 packet for the new cycle with type `operator-preflight` and status `excepted`, citing Operator2's exclusive active Opus Stage-A assignment and prohibiting duplicate ChatGPT review.
3. Change Task 1 references from three packets to five packets, include the two exact new paths in the Coordinator packet, and change the route/postcheck scope from three packets plus one route to five packets plus one route.
4. Preserve every candidate identity, frozen SHA, 22-path range, merge topology, descriptor identity, zero-provider construction boundary, later Opus activation gate, review contract, integration firewall, and non-goal byte-for-byte in meaning.

This correction changes no sanitizer behavior, review question, candidate lineage, provider authority, receipt authority, or integration scope. Because it changes an explicitly approved authority-bearing plan, it still requires direct user approval before the plan is edited and executed.

## Subagent Utilization

Direct/no-op. This was a tightly coupled, authority-sensitive contradiction between the approved plan and the executable capacity kernel. The exact kernel and plan lines provide deterministic evidence; a helper would add no independent signal and cannot repair plan authority.

## Side-Effect Executor Token

- side_effect_id: `chatgpt-task1-capacity-plan-blocker-2026-07-16`
- executor: `coordinator`
- target: `coordination/mailbox/sent/2026-07-16T08-19-43Z-coordinator-to-all-coordination.md`
- allowed_command_class: fresh read-only HEAD, mailbox, capacity, plan, ref, candidate-artifact, lock, index, Wave-2, and smoke checks; `apply_patch` for exactly this blocker event; exact-path `git add -f --` and one exact-path local commit; read-only postchecks
- preflight: HEAD is exactly `e99775bf5901d53eed10fb5e069ddf929930ce66`; the newest committed mailbox event is the 2026-07-16T06:58:35Z coordinator route; both frozen refs match; candidate names and descriptor task ID are absent; locks and shared index are empty; capacity and smoke pass; the approved plan still requires only three packets
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if HEAD, newest mailbox body, either approved correction document, either frozen ref, candidate artifact presence, lock/index state, plan packet count, capacity result, or target path changes
- postcheck: prove one local commit changes exactly this blocker event; rerun capacity, Protocol Doctor, Wave 2, smoke, HEAD/mailbox/ref/candidate-artifact/lock/index checks; confirm no production, candidate, provider, receipt, verdict, ref, or remote side effect
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no plan edit, capacity packet, candidate route, branch, worktree, merge, descriptor, verify-request, provider or browser call, receipt/runtime mutation, verdict, integration, cursor consume, lock action, push, remote-ref update, publication, deployment, cleanup, or unrelated WIP change

Join condition: the user explicitly approves or rejects the four-point narrow capacity-plan correction above. Until then, Task 1 remains stopped before packet or route creation.

## Exact Next Trigger

Approve the narrow Task-1 capacity correction: add the two Pair-B excepted preflight packets required by G1, change only the packet counts/paths/postchecks from three to five, preserve every candidate/provider/review semantic, then proceed without a ChatGPT Pro consultation.

Cursor at send: 0
