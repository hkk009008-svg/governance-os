# Risk classes — classification criteria

The executable profiles (review requirements per class) live in
`scripts/codex_protocol_model.py` `RISK_BASED_REVIEW_PROFILES`; this document
owns the membership question the profiles deliberately do not answer: which
changes belong to which class. The author declares the class on the
verify-request and the assigned Operator's risk-class judgment is the
governance floor (ADR-067 I5). When in doubt between two classes, take the
higher one.

## ordinary-local

Reversible, repository-local work whose failure is contained by the tree it
edits: implementation details behind stable contracts, test-only changes,
documentation that binds nothing, behavior-preserving refactors. Focused
fresh verification; no formal request/report pair.

## material-behavior

A change is material when it crosses a load-bearing boundary:

- a public or cross-component contract (API, schema, event shape, CLI);
- persistence semantics or stored-data migration;
- an accepted scientific or business conclusion;
- externally visible or hard-to-reverse behavior;
- repository-wide execution architecture (CI topology, test harness);
- an instruction surface (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`,
  skills, continuation docs): prose is executable on models — the 2026-07
  field trial measured doctrine text shaping a 6.5 h session whose reviewed
  tools sat unused — so editing it changes behavior by the same standard as
  code.

Acceptance needs non-author review of the exact committed range.

## high-risk-control

Everything material, plus the change constructs or gates trust: authority or
identity resolution, security enforcement, side-effect gating, money or
resource enforcement, executable composition (hooks, launchers, fixed
writers), trust-granting schema validation, or the review/admission machinery
itself. Acceptance needs distinct non-author, different-model actual-diff
review plus an explicit abuse-class assessment.

## external-effect

Push, merge, lock, cursor consumption, provider launch, paid spend, and
live-data mutation. Not a review depth: live human authorization for the
exact executor, target, effect, and scope — regardless of model capability
or any green gate.

The path-prefix list in `scripts/ci_admission_gate.py` (`AUTHORITY_SURFACES`)
is the conservative executable approximation of the high-risk boundary at the
integration gate; extending or narrowing it is itself an authority-surface
change and reviews as one.
