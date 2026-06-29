# DECISIONS — Architecture Decision Record Log

This file is the append-only ADR log for Governance OS. Each entry records an
architectural or governance decision at the moment it was made, together with
the context that made it necessary and the consequences (positive and negative)
accepted at that time. **Append-only — never edit prior entries.** If a
decision is superseded, add a new entry that references the old one by number
and explains what changed and why; leave the original entry exactly as written.

---

## ADR Template

```
## ADR-NNN: <Short imperative title>

**Status:** Proposed | Accepted | Superseded by ADR-NNN

**Context:**
[1–3 sentences: what situation, constraint, or problem forced a decision?]

**Decision:**
[1–3 sentences: what was decided, stated unambiguously.]

**Consequences:**
- [Positive consequence]
- [Negative consequence / accepted tradeoff]
- [Follow-on work created, if any]
```

---

## ADR-001: Adopt the 4-seat governance operating system

**Status:** Accepted

**Context:**
As Governance OS grows, uncoordinated parallel edits and unverified claims have
caused repeated integration failures. A lightweight governance model is needed
that enforces independent verification without slowing routine work.

**Decision:**
Governance OS operates with a 4-seat model (two director seats, two operator seats
per pair). Director seats author briefs and make strategy calls; operator seats
independently verify every commit before it is considered landed. No commit is
treated as complete until the responsible operator seat issues a GO report.

**Consequences:**
- Defects are caught by a second set of eyes before they compound.
- Every cross-cutting change requires a co-sign, adding latency to large refactors.
- Seat discipline (mailbox protocol, presence files, lock claims) must be kept
  current; letting it drift negates the benefit.

---

<!-- Append new ADR entries below this line. Do not edit entries above. -->

## ADR-002: Gate adoption placeholders in CI (fail-closed allowlist)

**Status:** Accepted

**Context:**
The governance OS ships as a transfer bundle with skeleton docs that deliberately
contain adoption-placeholder tokens (`<PROJECT>`, `<fill-in>`, etc.). These
placeholders can be read by agents as if they were real doctrine, and a half-bound
repo (some skeletons filled, some not) currently passes the green smoke check —
there is no gate that catches un-replaced placeholders.

**Decision:**
Add an allowlist-based fail-closed placeholder scan (`scripts/check_placeholders.py`
+ `scripts/placeholder_allowlist.txt`). The script fails (exit 1) when any
placeholder token appears in a non-allowlisted file. The initial baseline allowlist
is generated empirically from the live repo (every file currently containing a token
is allowlisted). As adopters fill skeletons, they remove paths from the allowlist;
an empty allowlist with a clean scan is the definition of "fully bound." The gate is
wired into CI smoke in task A-WIRE.

**Consequences:**
- A half-bound repo will fail CI rather than silently passing green.
- Filling a skeleton now requires a mechanical step: remove its path from the
  allowlist, confirm the scan is still clean, then commit.
- An empty allowlist + clean scan is a machine-checkable definition of "fully bound."

---

## ADR-003: Make GO-evidence and ARCHITECTURE-freshness machine-checkable

**Status:** Accepted

**Context:**
High-value soft rules (GO reports must carry real evidence; ARCHITECTURE facts must
be re-verified when changed) were prose-only, enforced by the same class of agent
they govern ("the enforcer is the enforced"). Agents could issue a GO citing only
`wave_gate_check` (which reads an inventory string, not a test execution) or edit
`ARCHITECTURE.md` without bumping its `*Last verified:*` stamp — leaving stale
provenance on the truth layer — with no mechanical backstop.

**Decision:**
Promote them to fail-closed scripts: `scripts/check_go_schema.py` (task A2 — a GO
verification-report must carry verdict + command/output + SHA; a GO citing only
`wave_gate_check` fails) and `scripts/check_arch_freshness.py` (task A3 — editing
`ARCHITECTURE.md` without bumping its `*Last verified:*` stamp fails). Both are
wired into smoke/CI in task A-WIRE.

**Consequences:**
- GO reports and ARCHITECTURE edits now have teeth in CI; ceremony-only evidence
  is blocked at the gate rather than caught (if at all) in post-hoc review.
- Adopters must bump the `*Last verified:*` stamp on every substantive ARCHITECTURE.md
  edit — a small but non-zero friction increase for truthful updates.
- Verify-then-push machine-checkability remains deferred (see ADR-005 / task A7).
