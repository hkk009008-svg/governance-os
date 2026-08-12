# Seat End-Trigger Enforcement Design

## Purpose

Every live seat and coordinator turn must end with an explicit trigger so the
next session can resume from durable state instead of guessing from chat.

The trigger is a concise statement of the next lawful action, standby condition,
or blocking input. It must appear at the end of the seat's turn artifact and in
the seat's user-facing final response.

## Scope

Applies to Codex four-seat protocol surfaces in Pipeline:

- Live seats: `director`, `director2`, `operator`, `operator2`
- Coordinator
- Seat/coordinator mailbox artifacts that hand off status, verification,
  route, decision, or closeout state
- Seat/coordinator handoff artifacts
- Seat/coordinator user-facing final responses

Readiness-bridge reports and bounded subagent reports should include a trigger
when they transfer state, but they do not own seat authority and are not the
first executable enforcement target.

## Enforcement Rule

At the end of every live-seat/coordinator turn, output a final section named
`Exact Next Trigger`.

Accepted trigger content must name one of:

- a next prompt or seat event to wait for
- the next receiving seat and mailbox event path
- the next verification or route command
- a standby/no-op condition plus the event that would wake the seat
- an explicit blocker and who must resolve it

The trigger must be last or effectively last. Cursor metadata such as
`Cursor at send: 0` may follow it in mailbox artifacts because existing mailbox
events use that convention.

## Implementation Plan

1. Add test coverage for a protocol artifact validator that rejects live-seat or
   coordinator mailbox bodies without an end trigger.
2. Implement the validator in existing coordination/protocol tooling rather than
   introducing a new standalone convention.
3. Add docs/skill wording so seats are told to end every turn with `Exact Next
   Trigger`, not only boundary handoffs.
4. Run the focused unit tests and `scripts/ci_smoke.py`.

## Non-Goals

- Do not consume coordinator mail.
- Do not push.
- Do not change evidence-ledger product files.
- Do not require subagents to issue mailbox triggers with seat authority.
- Do not make old historical mailbox events fail normal smoke unless the
  validator is explicitly asked to check them.

## Acceptance

- A missing final trigger is caught by an automated test.
- Valid existing-style mailbox artifacts with `## Exact Next Trigger` pass.
- Four-seat protocol docs and skills tell every seat/coordinator to end turns
  with the trigger.
- This turn's final response ends with an explicit `Exact Next Trigger`.
