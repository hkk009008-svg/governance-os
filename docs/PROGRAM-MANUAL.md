# PROGRAM MANUAL - Governance OS

**Canonical expression of the user-principal's intent for Pipeline.**

Pipeline is the governance kernel. Its job is to make multi-seat AI coding work
durable, verifiable, and bounded by explicit authority. It does this with
mailbox events, capacity packets, live seat status, smoke gates, Codex/Claude
protocol skills, and route-specific verification artifacts.

evidence-ledger is the bound product target for current ledger-routed work.
Pipeline should help seats work on that target only through explicit routes; it
must not blur product truth into governance-kernel truth.

## 1. What We Build

We build an executable governance OS for AI-assisted software work. The system
turns user intent and seat-specific prompts into durable artifacts: route
mailbox events, scoped implementation packets, verify-requests,
verification-reports, handoffs, and gate evidence.

The output the user receives is not just prose. It is a repository state that
can be audited by git, tests, mailbox bodies, and route validators.

## 2. Product Goals And Non-Goals

Goals:
- Keep Pipeline as the authoritative governance kernel for Codex seat startup.
- Make every active route explicit, bounded, and verifiable.
- Preserve user-gated side-effect boundaries for push, locks, cursor consume,
  spend, pods, checkout refresh, and product generation.
- Prefer executable proof over status theater.
- Keep product-specific truth in the target product repo.

Non-goals:
- Pipeline is not the private evidence-ledger application.
- Pipeline does not silently publish, push, refresh target checkouts, or spend
  money.
- Coordinator artifacts do not replace operator GO/NITS/FAIL verification.
- Warning-only smoke output does not prove clean provenance.

## 3. How The Machine Interconnects

User or parent prompts assign a mode: readiness bridge, live seat, coordinator,
or bounded subagent. Pipeline startup tools then read durable state before any
protocol decision. `ledger_start_guard.py` enforces the Pipeline-first boundary
for ledger-routed work. `seat_status.py` reports HEAD, mailbox unread state,
peer heartbeats, and wave gate state.

Mailbox events in `coordination/mailbox/sent/` bind recipients. Capacity
packets in `coordination/capacity/packets/` define active scope. Smoke,
coordination, capacity, and doc-claim tools provide executable evidence. The
director/operator pair closes a work loop only when implementation evidence is
followed by an operator verification-report.

## 4. Operational Contract

Required inputs:
- A user or parent prompt naming the mode or seat.
- A current Pipeline checkout.
- The active route body when capacity packets are open.

Successful run output:
- For implementation: a scoped commit plus one lawful authority-bearing trigger
  for the operator.
- For verification: a GO/NITS/FAIL verification-report with command evidence.
- For coordination: a route, closeout, or no-op artifact that changes real
  ownership or preserves evidence.

Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
manual intentionally does not restate its lifecycle grammar.

Known failure modes:
- Stale route prose is trusted over newer mailbox/git evidence. Fix by
  rereading current route bodies, seat status, recent commits, and later
  reports before acting.
- Unknown broadcast receipt is treated as delivery. Fix by treating unknown as
  unproved until seat-specific evidence exists.
- Normal target checkout is treated as the route base. Fix by following the
  active route's named base or worktree first.
- A `SHA-REF BASELINE CHECK` failure is summarized as ordinary smoke noise.
  Fix by running the SHA-reference report and treating changed drift as a
  bounded cleanup or owner-decision gate.

## 5. Capability-Maximization Playbook

Use the smallest sufficient route. A good route names the owner, packet, allowed
paths, evidence commands, forbidden side effects, next recipient, and exact next
trigger.

Use subagents when they add independent signal or capacity, but keep seat
authority in the live seat. Subagents do not consume cursors, issue GO, route
coordinator work, push, claim locks, spend, or start pods.

Use tests and scripts as the evidence layer. New behavior belongs behind a
focused regression test before implementation. Gate numbers belong in committed
script output or route evidence, not ad-hoc memory.

## 6. Operating Guidance For Seats

Director seats scope and implement only inside their route. They send one
canonical committed verify-request once its structural authority fields are ready.

Operator seats independently verify only from a lawful trigger and return
GO/NITS/FAIL. They do not duplicate verification for docs-only or status-only
artifacts.

Coordinator reconciles route, lock, mailbox, capacity, and closeout state.
Coordinator must not author behavior-changing product fixes.

Coordinator and seat chains continue internally and stop only at completion, a
genuine blocker, scope expansion, or a separately user-gated effect. At a real
stop, state the blocking boundary or plain next authority without a prescribed
heading or returning seat commands to the user.
