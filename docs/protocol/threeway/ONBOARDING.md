# Opt-In Threeway Onboarding

Do not onboard the signed bus for ordinary Pipeline work. Use this only when
the user selected an exact target and authorized activation design.

1. Read [`README.md`](README.md) and
   [`UNIFIED-OPERATING-DOCTRINE.md`](UNIFIED-OPERATING-DOCTRINE.md).
2. Inspect the target's actual `refs/threeway/*`, mailbox, cursors, protected
   branch, CI, runners, registry, and key custody using read-only commands.
3. Name the executor, target, scope, authority source, rollback boundary, and
   exact `threeway.cutover --yes` invocation that will be the authority flip.
4. Prove shadow projection without mutating the live transport.
5. Review the exact high-risk-control range with a non-author reviewer from a
   different model family and explicit abuse-class assessment.
6. Confirm there is no dual-write interval and that every pre-flip failure
   leaves the previously authoritative transport usable.
7. Obtain separate live authorization before key mutation, cutover, cursor
   consumption, provider launch, push, protected merge, or spend.
8. Verify target post-action state directly; a local return value is not proof.

Provider mechanics:

- Codex: [`CODEX-ADOPTION.md`](CODEX-ADOPTION.md)
- AGY: [`ANTIGRAVITY-ADOPTION.md`](ANTIGRAVITY-ADOPTION.md)
- Claude: [`../claude/continuation.md`](../claude/continuation.md)
- Cursor: [`../cursor/continuation.md`](../cursor/continuation.md)

All providers start from their ordinary readiness/role adapter. Any supported
provider may hold an explicitly assigned mailbox role; none becomes a signed
principal by implication. If a deployment fact or authority is missing, stop
at capability assessment and retain the existing authority channel.
