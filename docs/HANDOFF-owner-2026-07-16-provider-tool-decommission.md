# Owner Handoff: Provider Tool Targeted Decommission

## Supersedes

- `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md`
- `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`

## Active Ownership

- Coordinator: route retirement, capacity, activation, and closeout metadata only.
- Director: Tasks 2-3.
- Director2: Tasks 4-5 after Director completes.
- Operator2: Task 6 bounded quality preflight; no repair.
- Operator: Task 7 provider-neutral Lane V; no repair.

## Preservation Boundary

Historical Git, mailbox, plan, specification, log, descriptor, packet, handoff, and ignored local runtime evidence remains unchanged.

## Prohibited Actions

No provider invocation, browser send, paid API, retry, fallback, receipt mutation, runtime cleanup, push, or merge.

## Exact Next Trigger

Director starts Task 2 only after the coordinator route commit passes the wave-2 capacity validator.
