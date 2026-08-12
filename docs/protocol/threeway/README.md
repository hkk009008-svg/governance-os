# Threeway Signed-Bus Protocol

This directory documents the optional cross-provider signed-bus plane. It does
not activate the bus, allocate roles, mutate Git, or grant an external effect.
Ordinary Pipeline work uses the committed mailbox until an explicitly
authorized cutover creates a coherent signed-bus event/cursor ref set. Readers
use that coherence as the authority flip; there is no second marker.

## Read map

| Need | Source |
|---|---|
| Current deployment boundary and invariants | [`UNIFIED-OPERATING-DOCTRINE.md`](UNIFIED-OPERATING-DOCTRINE.md) |
| Opt-in activation orientation | [`ONBOARDING.md`](ONBOARDING.md) |
| Codex host delta | [`CODEX-ADOPTION.md`](CODEX-ADOPTION.md) |
| AGY host delta | [`ANTIGRAVITY-ADOPTION.md`](ANTIGRAVITY-ADOPTION.md) |
| Current topology | [`ARCHITECTURE-DIAGRAM.md`](ARCHITECTURE-DIAGRAM.md) |
| Headless advisory review constraints | [`HEADLESS-REVIEW.md`](HEADLESS-REVIEW.md) |
| Executable mechanism coverage | [`MECHANISM-LEDGER.md`](MECHANISM-LEDGER.md) |
| Historical design/review evidence | [`reviews/`](reviews/) and Git history |

Canonical adapter path: `docs/protocol/threeway/CODEX-ADOPTION.md`.

Universal role, review, and authority rules live in
[`docs/protocol/agents/`](../agents/). Provider entrypoints live in their
normal continuation documents. If prose disagrees with executable behavior,
[`threeway/`](../../../threeway/) and current Git win for runtime facts.

## Establish current state

```bash
git for-each-ref refs/threeway/
git ls-remote origin 'refs/threeway/*'   # only when remote state matters
```

Missing refs mean absent deployment. A partial or corrupt event/cursor pair is
incoherent, not an empty live bus. Source code, test refs, green tests,
preflight, or a local `activated=True` return are not protected deployment proof.

When coherent refs are absent, the legacy mailbox remains authoritative for
local work.

The repository contains the signed event envelope, CAS ref store, reducer,
tiers, gate, migration helpers, emitters, consumer, and merge-gate tooling.
Protected-main deployment additionally requires verified signer custody,
protected-ref/runner enforcement, exact activation authority, and post-action
state proof. The protected-main path is not claimed complete merely because the
local test-ref path passes.

Any supported provider may hold a formal mailbox role when explicitly
assigned. That assignment does not make it a signed principal. Signer identity,
key custody, CI attestation, merge-gate authority, provider launch, push, merge,
cursor consumption, and spend remain separately bound and authorized.
