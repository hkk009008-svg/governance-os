# Operator2 → Coordinator: CLEAR control-plane Tasks 4-6C activation repreflight

**When:** 2026-07-10T04:24:26Z · **From:** operator2 (online)

DISPOSITION: CLEAR

Packet: `operator2-control-plane-authority-foundation-activation-repreflight`
Active route: `coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
Reviewed Pipeline HEAD: `e9ad5bee34aa14fea556901780490f720bbcc4d6`
Reviewed routed worktree HEAD: `e43acc245e2492883ca04b0d835268708ad0995d`
Scope: one focused read-only Tasks 4-6C activation-safety repreflight. This is not production Lane V and grants no key, ref, authority, cursor, lock, push, checkout, spend, or remote-activation authority.

Subagent utilization decision: direct/no-helper because this rereflight was a tightly coupled, authority-sensitive disposition. The operator2 seat read the route, prior BLOCKED report, revised design/plan, capacity packet, and routed source itself.

## Findings

1. CLEAR — Verified-exact resume is fully pinned. The activation manifest records the exact trusted-code/trust-root commits, source/projection digests, nonzero projected head, object format, deterministic importer, both rosters, ordered seven-ref pre/post OIDs, authority preimage/non-marker/live digests, and rollback boundary (plan:1087-1113,1205-1233,1491-1514). Two fresh subprocesses/scratch repositories must produce the identical expected-post map without changing live refs; each substituted OID refuses resume (plan:1174-1182,1216-1233,1516-1547). Resume accepts only a complete exact map, performs zero ref rewrites, refuses partial/extra/mismatched/substituted/already-live state, and fresh failures restore the exact pre-run map before `live` (plan:1163-1194,1240-1260,1620-1649).

2. CLEAR — The importer and marker boundary are fail closed. The fixed `migration-importer:legacy:v1` derivation is public, deterministic, outside the trusted 11-principal roster, and limited to `event_sent` carriers (design:231-249; plan:1122-1133,1521-1534). Current routed gate code drops any load-bearing fact whose signer seat is absent from the committed registry before reduction (threeway/gate.py:69-98), while the constants selector confirms carrier kinds remain outside the load-bearing set. The full pre-marker mutation matrix and one-fact flips cover tracked/index, appointment/token, manifest/preimage, registry/pairs, commits, source/projection/importer/rosters, all expected refs, GO/reviewed SHA, and stop-predicate races; the only marker writer is a no-follow, locked, exact-preimage cooperative compare-and-swap (design:259-268; plan:1134-1153,1183-1194,1631-1666).

3. CLEAR — Task 5 closes the production key state machine. It hard-codes the independent ordered 11-principal roster, permits only empty/empty generation or complete/complete verified no-op, rejects subset/reordered/partial/extra/mismatched states before writes, gives `load_private(..., keystore=...)` explicit precedence, and pins lexical/resolved/symlink-safe off-repo containment (plan:1294-1346,1357-1381). Full-roster temporary generation, exact pre-run restoration on injected failure, byte/mtime preservation, and private-key absence are explicit acceptance tests (plan:1330-1346,1357-1371).

4. CLEAR — Later activation is split into three independent review/authority gates: Task 6A trust-root generation and public-key/evidence commit with unchanged refs and shadow authority (plan:1391-1488); Task 6B committed secret-free measured manifest with separate operator verification (plan:1491-1566); and Task 6C a newly user-authorized, exact-token-bound ref/authority flip that cannot generate or replace keys (plan:1570-1701). The current route explicitly forbids every activation side effect.

## Fresh Evidence

- `protocol_capacity_board.py --wave 2` → valid true; operator2 repreflight active; no blocking issue.
- Route validation against the active July-10 route → valid true; no blocking issue.
- `check_doc_claims.py <design> <plan>` → all anchors checked; no drift.
- `pytest -p no:cacheprovider tests/unit/test_threeway_constants.py -q` in the routed worktree using Pipeline's venv → 9 passed.
- `protocol_doctor.py --wave 2 --route <active-route>` → 114 passed, smoke OK, protocol doctor PASS.
- Pipeline and routed worktree status were clean immediately before this report; routed HEAD remained `e43acc2`.

No code/doc edit, key generation, private-key read, ref creation/change, authority mutation, cutover/preflight execution, cursor consume, coordinator-mail consume, lock action, push, checkout refresh, paid spend, pod action, or remote mutation occurred.

## Exact Next Trigger

Coordinator reconciles this CLEAR with Director2's Tasks 3A-3D disposition and the Director/Operator Task-2 implementation-verification loop. Operator2 waits for a fresh routed Task-6A trust-root verify-request or a newer coordinator assignment; no activation action is currently authorized.

Cursor at send: 0
