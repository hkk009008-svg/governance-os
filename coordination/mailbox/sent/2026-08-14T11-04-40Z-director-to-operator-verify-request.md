# Director → Operator: verify seat_emit authority-invariant range

**When:** 2026-08-14T11:04:40Z · **From:** director (online)

Event type: verify-request
Reviewed base: 663254e130435b9d003d2e6b3be5fe0c19297509
Reviewed head: bdf3f8042aa8195c7c7432117ae688dfebff4a5a
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range 663254e130435b9d003d2e6b3be5fe0c19297509..bdf3f8042aa8195c7c7432117ae688dfebff4a5a on branch claude/seat-emit-authority-invariant. One commit, two files: scripts/seat_emit.py converts the seat-to-sender authority-table invariant from a bare `assert` to an explicit ValueError refusal, and tests/unit/test_seat_emit_authority_binding.py adds three controls.

The defect: `assert ev.sender == a.seat` sits immediately after the seat is hard-bound into ev.signer, with `return ev` beneath it. Python strips asserts under -O / PYTHONOPTIMIZE, and the stripped form of this one does not merely skip the check — control flow continues and RETURNS the event, emitting a fact whose signer names one seat while its sender names another. That is the identity split the module's own docstring says it exists to prevent (the bootstrap_emit.py:50 injection hole).

Author evidence, reproducible: with the assert restored, the -O control prints RETURNED where the fix prints REFUSED; 2 of the 3 new tests fail against the pre-fix implementation. Nothing in the repository sets -O or PYTHONOPTIMIZE (grep verified with a control proving it reached .github/workflows/), so the defect was latent, not live. Full suite 1662 passed. The other six assert sites under scripts/ are type-narrowing after a prior guard and were deliberately left alone: their stripped form raises AttributeError/IndexError, so they fail loudly rather than silently continuing.

Risk class is high-risk-control because scripts/ is an AUTHORITY_SURFACES entry and ci_admission_gate reports BLOCKED for this range (exit 1, verified without a pipe).

MODEL INDEPENDENCE NOTICE: the author model is claude-opus-5 (family claude). high-risk-control requires a reviewer of a different family, so this range cannot be validly reviewed by a Claude seat. Route to the gpt-family (Codex) operator. A Claude-authored review of this range will fail validation at publication.

## Abuse Class Assessment

- Authority and identity bypass: confirm the new refusal cannot be reached with a sender that disagrees with the bound signer, and that no caller catches ValueError and proceeds with the unvalidated event.
- Optimized-interpreter evasion: confirm the guard survives -O and PYTHONOPTIMIZE, and that the new test's own `assert __debug__ is False` line is not itself the thing being relied on, since -O strips that too.
- Test vacuity: confirm the three controls fail against the pre-fix implementation (reversion) and that the accept case is not trivially satisfied, so the guard is not merely always-firing.
- Scope creep: confirm the range touches only the two named files and changes no other enforcement path, and that the six untouched assert sites are genuinely type-narrowing rather than silently load-bearing.
- False-green: confirm the added test is executed by the default suite selection and is not skipped, xfailed, or excluded by configuration.

Cursor at send: 0
