---
name: create-regression-pin
description: Add a strict xfail for a confirmed defect that is deliberately deferred, and prove the pin fails for that defect.
---

# Create a regression pin

Use this only when a confirmed defect will remain unfixed in the current task.
Prefer fixing an in-scope defect over pinning it.

Write a test for the correct post-fix behavior and mark it
`pytest.mark.xfail(strict=True, reason="<defect>: <reason>")`. Match the
assertion to the intended fix: if the fix should return safely, assert that
return; if it should block, assert the block.

Prove the pin is useful:

1. Run the test with `--runxfail`; it must fail because of the defect, not setup.
2. Run it normally; it must report xfailed, never xpassed or skipped.
3. Record the test path and the one-line reason in the task result.

If the behavior cannot be exercised without unavailable hardware, paid access,
or nondeterministic external state, record `test-infeasible` and the reason.
