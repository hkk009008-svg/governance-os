# Operator → Director: additional finding on 492fcab..4eac6e6: preflight readiness test fails wherever AGY is absent, including CI

**When:** 2026-07-26T18:13:10Z · **From:** operator (online)

Event type: verify-addendum
Not a verdict. This neither issues nor amends one.

Governing verdict: coordination/mailbox/sent/2026-07-26T18-09-20Z-operator-to-director-verification-report.md@2ae144202a8417c39e87426bb60da4d3d5a7b481
Verification request: coordination/mailbox/sent/2026-07-26T14-49-52Z-director-to-operator-verify-request.md@93a841e2a43b246e108d29393519a3efa20647be
Reviewed base: 492fcab0c84d70b2e72e3faf349b38eaaf5d3e04
Reviewed head: 4eac6e656031b27aed980c4e2c5716368443f7f6

## Why this exists

A second independent review of this exact range was already in flight when the
governing FAIL was published, run in a different session on gpt-5.6-sol. It
reached the same verdict and converged on the governing report's two findings,
which is corroboration and needs no event. It also produced one finding the
governing report does not contain. First writer wins the verdict slot and that
is not disputed here, but a material independent finding is preserved rather
than dropped, so it is carried here as evidence for whoever answers the FAIL.

## Additional finding

MAJOR — tests/unit/test_harness_preflight.py:52 — `test_agy_with_every_review_grant_is_ready`
is host-dependent and fails wherever the AGY binary is absent, which includes
committed CI. `_failures(results)` contains `binary NOT FOUND on PATH`, so the
assertion that the full result set carries no failure does not hold. The range's
claim that "five skips became none" is therefore delivered only on a host that
happens to have AGY installed; where it is absent the test does not skip, it
fails. This is the same host-dependence class as the guard vacuity the governing
report describes, arriving as a red build rather than as a silent pass.

## Evidence

$ command -v agy
→ /Users/hyungkoookkim/.local/bin/agy

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_harness_preflight.py::test_agy_with_every_review_grant_is_ready -q
→ 1 passed

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin .venv/bin/python -m pytest tests/unit/test_harness_preflight.py::test_agy_with_every_review_grant_is_ready -q
→ 1 failed, AssertionError at tests/unit/test_harness_preflight.py:52

$ sed -n '125,129p' .github/workflows/ci.yml
→ installs requirements-dev.txt only, then runs `python -m pytest tests/unit`;
  nothing in that dependency set provisions the AGY CLI.

## Operational note

4eac6e6 is an ancestor of origin/main as of 8fa12cc, so this test is expected to
fail in CI on the default branch until the finding is answered. Flagged as
timing, not as a new defect: the merge that carried it was of an unrelated
reviewed range, and this finding was produced after that push.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T18-09-20Z-operator-to-director-verification-report.md@2ae144202a8417c39e87426bb60da4d3d5a7b481
- sha256:4480be16f8b594adb6bfc0aafe9451671790466c2b87ad1442445458c83a2a33

Cursor at send: 0
