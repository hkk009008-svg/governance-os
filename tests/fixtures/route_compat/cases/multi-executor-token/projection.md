# Coordinator → All: Multi-Executor Token Fixture

Task-board: route-compat-cycle

- coord-capacity-split-route
- director-capacity-split-chunk-a
- operator-capacity-split-chunk-a
- director2-capacity-split-work
- operator2-capacity-split-work

## Capacity Split Default

The single-pair fast path applies; the non-implementing pair holds bounded planning or preflight packets only. Coordinator owns convergence.

## Side-Effect Executor Token

- side_effect_id: publish-main-2026-07-11
- executor: director and operator
- target: origin/main
- allowed_command_class: git push
- preflight: git status plus divergence check
- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox and ls-remote
- postcheck: git ls-remote origin refs/heads/main
- observer_seats: director2, operator, operator2
- final_closeout_owner: coordinator
- non_goals: no force-push and no lock claim

Join condition: coordinator closes after both pair lanes are accounted for.

## Exact Next Trigger

Director continues Chunk A; Pair B follows the capacity split decision.
