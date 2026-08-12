# Threeway Signed-Bus Doctrine

This doctrine applies only when an exact target is explicitly adopting the
signed bus. It does not duplicate universal role policy or activate itself.

## Deployment boundary

```bash
git for-each-ref refs/threeway/
```

Inspect local and, when relevant, remote ref state. Until the target proves a
coherent event/cursor ref set, complete signer registry and private-key custody,
protected-runner isolation, protected-ref enforcement, and one recorded
authorized cutover, the prior mailbox remains authoritative.

In the ordinary local state, the legacy mailbox remains authoritative for local
work.

Missing, partial, corrupt, or mismatched refs are explicit transport failure.
Never infer deployment from source code or turn ambiguity into zero unread.

## Invariants

1. **One authority channel.** Migration is read-only shadow projection followed
   by one explicitly authorized cutover. Its coherent event/cursor refs are the
   flip consumed by readers; there is no dual write or second marker.
2. **Principal-scoped facts.** An emitter signs only facts owned by its bound
   principal. A role label, fixture key, or helper cannot widen authority.
3. **Verify before reduce.** Signatures, IDs, ordering, supersession,
   revocation, candidate identity, and tier evidence are checked before use.
4. **Recompute the exact merge.** The gate does not trust a claimed integration
   object and does not execute candidate code.
5. **Isolate protected effects.** Candidate-running environments do not hold
   signer or merge-gate credentials.
6. **Conflicts abort.** Textual or semantic conflicts become a new candidate;
   the gate does not silently repair them.
7. **No authority leakage.** Signed readiness does not grant provider launch,
   push, merge outside the protected runner, cursor consumption, spend, or
   live-data mutation.
8. **Transactional activation.** Any append, cursor, or legacy-backfill failure
   restores each successful CAS chain to its actual predecessor and does not
   return `activated=True`.

Exact event kinds, canonicalization, signatures, state reduction, tiers, CAS,
and merge predicates live in [`threeway/`](../../../threeway/).
Codex deployment deltas live at
`docs/protocol/threeway/CODEX-ADOPTION.md`.

## Provider posture

Codex, Claude, Cursor, and AGY may hold formal mailbox roles only after explicit
assignment through their normal adapters. Native helpers stay parent-scoped.
Mailbox role identity and signed principal identity are separate facts: a
target binds each signer, key, and runner explicitly.

No provider or helper implicitly becomes overseer, CI attestor, chief, signer,
or merge gate. Communication and structural dispatch do not launch a provider.

## Activation

Activation is a governed external effect. Bind and verify:

- target repository, protected ref, and prior authority source;
- exact event/cursor refs and canonical legacy projection;
- complete signer roster, private-key custody, CI, and merge-gate runners;
- abort/recovery behavior before the flip;
- executor, target, scope, and live authorization;
- direct post-action proof.

`threeway.cutover --yes` is the local authority flip because no separate marker
is consulted by readers. It requires separate live authorization before the
invocation. Its return is not a protected-main deployment receipt; verify refs,
registry binding, runners, and protected enforcement directly afterward.

## Review

Signed schemas, key handling, reducers, gates, cutover, consumers, emitters,
credential boundaries, and protected-ref controls are `high-risk-control`.
They require non-author exact-range review by a different model family and
explicit abuse-class assessment. Review never authorizes activation or another
effect.
