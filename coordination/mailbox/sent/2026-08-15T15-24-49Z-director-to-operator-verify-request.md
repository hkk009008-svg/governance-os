# Director → Operator: remediate FAIL: control falsifiability

**When:** 2026-08-15T15:24:49Z · **From:** director (online)

Event type: verify-request
Reviewed base: 15757a7d153b3a52cb7a07d2643b64adb65c9ab7
Reviewed head: 6183e9c5135bbad51f58bd5c8c1002692b9b464c
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control
Remediates failed report: coordination/mailbox/sent/2026-08-15T15-16-38Z-operator-to-director-verification-report.md@15757a7d153b3a52cb7a07d2643b64adb65c9ab7

## Outcome

Remediation of the committed FAIL. Reviewed base is that report's introduction
commit and reviewed head is a strict descendant, preserving its repository,
risk class, and assigned reviewer seat. The FAIL carried no finding refs, so
there are none to preserve.

One commit, and it changes no production code. The FAIL's MAJOR finding was that
the forced-interleave control set its fired flag BEFORE calling
injector.append(), so deleting the append left every assertion green, including
against the exact unguarded _read from the original reviewed base. The control
could not distinguish a forced interleave from a hook that wrote nothing.

The postcondition is now the write rather than the hook: the injected
connection's committed cursor must be 2, which a hook that writes nothing cannot
produce.

Verified across four arms, the third being the FAIL's exact evasion:
  fixed _read     + injection present -> pass
  unguarded _read + injection present -> fail
  unguarded _read + append DELETED    -> fail   (this previously passed)
  fixed _read     + append DELETED    -> fail

The FAIL recorded the production exception-path repairs as passing their
reproduced fault paths, so this range deliberately touches only the control.
Two of its INFORMATIONAL observations are treated as accepted rather than
re-litigated: that a synthetic close raising before delegating can still retain
the underlying transaction while the original exception survives, and that the
real sqlite3 close released the lock under reproduced denial.

Attack the remediation directly rather than accepting the four-arm table.
Judge whether committed == 2 can be satisfied without a genuine interleave, and
whether any other single deletion or reordering inside the control leaves it
green against the unguarded base.

Do not infer push, merge, or other external-effect authority.

## Abuse Class Assessment

- Control falsifiability: no single deletion or reordering within the control may leave it green against the unguarded base _read.
- Postcondition strength: the committed-cursor assertion must be unsatisfiable by a hook that performs no write, and must not pass on a write that landed outside the read window.
- Production scope: no runtime behaviour may change in this range; the exception-path repairs already reviewed must be byte-identical.
- Regression durability: the control must remain deterministic rather than timing-dependent, and must not become order-dependent on other tests in the module.

Cursor at send: 0
