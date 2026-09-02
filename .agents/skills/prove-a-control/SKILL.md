---
name: prove-a-control
description: Prove that a guard, gate, or negative test would fail for the forbidden behavior and resists a plausible alternate route.
---

# Prove a control

Use two checks:

1. **Reversion:** restore the defect and confirm the control fails for the
   intended reason.
2. **Evasion:** leave the control intact and try a plausible alternate route to
   the forbidden outcome.

Also delete or bypass the real call site once. A correct guard that nothing
invokes is not enforced. Exercise the actual parser or command instead of
inferring semantics from help text or error wording.

Manufacture environmental preconditions inside the test where possible. Run
the same control in the important present/absent or main/worktree states. For a
zero result, first show the instrument detects a known-positive.

When temporarily mutating code, snapshot bytes, restore them exactly, disable
bytecode writes, and verify restoration. Prefer a throwaway repository to
mutating the reviewed checkout.

Before saying verified, retain the executed commands and observed outputs,
confirm every cited reference resolves, and state any evasion route or
environment not tested.
