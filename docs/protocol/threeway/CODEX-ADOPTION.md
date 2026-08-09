# Codex Adapter for Optional Threeway Adoption

Normal Codex work follows [`../codex/continuation.md`](../codex/continuation.md)
and the currently authoritative mailbox. Codex starts as a readiness bridge and
adopts a formal role only through explicit assignment.

```bash
git for-each-ref refs/threeway/
```

Until coherent refs and an explicit activation are proved, the legacy mailbox
remains authoritative for local work.

Use the native task worktree/index and one current status projection. A branch,
environment value, prompt, old event, or helper cannot create a mailbox role or
signed principal. Do not add a handoff-first startup or alternate index.

An ordinary Codex task does not create/distribute keys, mutate
`refs/threeway/*`, run cutover, act as protected merge gate, infer remote
deployment from local code, or dual-write transports. Signed identity and
runner authority are separately bound by the target.

Signed-bus, key, reducer, gate, cutover, consumer, emitter, and protected-ref
changes are high-risk control: non-author exact-range review by a different
model family plus abuse-class assessment. Review does not authorize key
mutation, activation, provider launch, cursor consumption, push, merge, spend,
or live-data mutation.

Executable sources are [`threeway/`](../../../threeway/),
[`scripts/codex_protocol_model.py`](../../../scripts/codex_protocol_model.py),
and [`scripts/compact_pair_loop.py`](../../../scripts/compact_pair_loop.py).
