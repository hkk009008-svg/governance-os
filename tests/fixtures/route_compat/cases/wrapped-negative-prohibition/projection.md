# Coordinator → All: Wrapped Prohibition Fixture

Task-board: route-compat-cycle

- coord-capacity-split-route
- director-capacity-split-chunk-a
- operator-capacity-split-chunk-a
- director2-capacity-split-work
- operator2-capacity-split-work

## Capacity Split Default

The single-pair fast path applies; the non-implementing pair holds bounded planning or preflight packets only. Coordinator owns convergence.

## Prohibitions

No seat may execute a
push or remote-ref update in this cycle.

Join condition: coordinator closes after both pair lanes are accounted for.

## Exact Next Trigger

Director continues Chunk A; Pair B follows the capacity split decision.
