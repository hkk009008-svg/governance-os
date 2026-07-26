# Three-Way Protocol — Adoption & Unified Doctrine

This directory holds the operating manuals for running **Claude, Codex, and Antigravity** as one
unified system on top of the cross-provider three-way protocol.

| Read this | When |
|---|---|
| [`ONBOARDING.md`](ONBOARDING.md) | **Start here.** A copy-paste prompt to bring any Codex / Claude / Antigravity session into the system, the reading order, the non-negotiables, per-provider quick-start, and a self-conformance check. |
| [`UNIFIED-OPERATING-DOCTRINE.md`](UNIFIED-OPERATING-DOCTRINE.md) | The shared rules all three providers follow — Layer 1 (the cross-provider protocol/topology) and Layer 2 (the portable operating doctrine), plus the per-provider capability-mapping table. |
| [`CODEX-ADOPTION.md`](CODEX-ADOPTION.md) | Operating Codex against the protocol. Codex already mirrors Layer 2; this covers its Layer-1 seats (`director`, `operator2`, `coordinator2`) and the migration. |
| [`ANTIGRAVITY-ADOPTION.md`](ANTIGRAVITY-ADOPTION.md) | Operating Antigravity ("agy"). It holds **no Layer-1 seat** by design; it participates as a human-relayed strategic reasoner / read-only observer and adopts Layer 2 for any work it does. |
| [`ARCHITECTURE-DIAGRAM.md`](ARCHITECTURE-DIAGRAM.md) | The canonical topology diagram (mermaid) — legend + the six load-bearing reads + what it corrects vs the draft diagrams. |
| [`HEADLESS-REVIEW.md`](HEADLESS-REVIEW.md) | Dispatching a non-author Operator review from Codex, AGY, or Cursor without a human driving that app — verified invocations, the per-harness constraints that block them, and what each can and cannot publish. |

**Truth sources (these win over the manuals on any factual disagreement):**
- Current Codex adoption status: [`docs/protocol/threeway/CODEX-ADOPTION.md`](CODEX-ADOPTION.md)
- Current unified doctrine: [`docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`](UNIFIED-OPERATING-DOCTRINE.md)
- The package: [`threeway/`](../../../threeway/)
- Verified-truth + decisions: [`ARCHITECTURE.md`](../../../ARCHITECTURE.md) · [`DECISIONS.md`](../../../DECISIONS.md) (ADR-034..064)
- Principle root: [`AGENTS.md`](../../../AGENTS.md) · Claude mechanics: [`CLAUDE.md`](../../../CLAUDE.md) · Codex mechanics: [`docs/protocol/codex/continuation.md`](../codex/continuation.md)

**Status (verify before relying — `git for-each-ref refs/threeway/` is the local
oracle):** the `threeway/` package — signed bus, effective-state reducer, gate,
RefEventStore, migration substrate, and tiered T2/T3 co-sign machinery — is built
and test-covered. In this checkout, the local oracle currently returns no
`refs/threeway/*`; therefore the legacy mailbox remains authoritative for local
work. If remote signed-bus status matters, verify it directly with
`git ls-remote origin 'refs/threeway/*'` before claiming remote bus authority.

What IS and is NOT live (be precise — this is bus + local CLI mechanism, not a deployed strategic loop):
- **BUILT — bus infrastructure and local mechanisms.** Signed-bus code,
  reducer, gate, RefEventStore, migration helpers, and merge-gate tooling are
  present in the repo and covered by tests.
- **LIVE LOCALLY AS TOOLS — principal-safe emitters for signed facts.** T1/T2/T3 and revocation/supersession facts
  are emitted through `scripts/overseer_emit.py`, `scripts/seat_emit.py`, and `scripts/chief_emit.py`;
  `docs/protocol/threeway/MECHANISM-LEDGER.md` covers every `LOAD_BEARING_KINDS` member. Verified via
  `env -u GIT_INDEX_FILE .venv/bin/python scripts/threeway_mechanism_ledger.py --check` -> exit 0.
- **NOT live locally — signed-bus authority for this checkout.** The free-form
  mailbox remains the human coordination channel and the local authority source
  until `refs/threeway/*` exists locally or remote refs are explicitly verified.
- **NOT live — deployed protected-main strategic loop.** The local signed-bus path is proved on `refs/threeway/test-main`, but deployed
  protected `refs/heads/main` promotion still requires verifiable branch-protection/ref-ACL controls and
  a protected merge-gate runner. Coverage: `tests/unit/test_threeway_activation_scripts.py::test_run_merge_gate_script`;
  the protected-main fail-closed path has no dedicated test — a previously cited
  `test_threeway_run_merge_gate_protected_main.py` never existed (citation corrected 2026-07-18).

Activation tooling: `scripts/sign_ci_result.py`, `scripts/run_merge_gate.py`, `scripts/agy_observer.py`,
`scripts/execute_threeway_cutover.sh`, `scripts/seat_emit.py`, `scripts/chief_emit.py`,
`scripts/overseer_emit.py`, `scripts/threeway_mechanism_ledger.py`, and the `.github/workflows/ci.yml`
`threeway-ci-result` job (fetchable `integration_ref` + exact tested `integration_sha`). Adoption of
the live protected-main loop requires first verifying the chosen signed-bus authority and then deploying
the protected merge-gate controls. See
`UNIFIED-OPERATING-DOCTRINE.md` §I.5.
