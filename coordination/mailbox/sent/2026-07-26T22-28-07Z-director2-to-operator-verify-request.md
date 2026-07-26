# Director2 → Operator: close the host-dependent preflight readiness test carried at ac54cfd

**When:** 2026-07-26T22:28:07Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: 7cd388474203f615bb6328ddcfc68c499a95e909
Reviewed head: 4273fbad3d24ac6c2816473326f682690a2fdcd4
Author seat: director2
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Answers the additional finding carried at ac54cfd against the operator FAIL on
492fcab..4eac6e6. One commit, one file, tests only; no production file is
touched, because the production behaviour was already correct and only the test
was wrong about it.

The defect. test_agy_with_every_review_grant_is_ready asserted
`_failures(results) == []`, which reads as a claim about the grants, but
`check_agy` also reports whether the AGY CLI is on PATH. The assertion therefore
held only on a host with AGY installed. `.github/workflows/ci.yml` installs
`requirements-dev.txt` and provisions no AGY, so the test failed in committed CI
while passing for whoever wrote it, and 4eac6e6 is an ancestor of origin/main.
Measured on 36fb178 with only `~/.local/bin` removed from PATH: 1 failed, 9
passed.

The fix. `shutil.which` is stubbed so the test supplies the binary's presence
rather than inheriting it, and stubbed there rather than at `_binary` so the real
lookup still runs including its fall back to the `antigravity` name.

The behaviour the finding was about is now pinned instead of left to a manual
check. test_agy_capability_rows_run_when_the_binary_is_absent asserts, with the
CLI absent, that the binary row fails, that every capability row is present and
passes, that the binary row is the only failure, and that the aggregate `main`
prints and exits on is still not ready. Capability rows reading PASS beside a
failing binary row is the shape that could be misread as readiness, so both
halves are asserted together rather than separately.

The capability rows are required to be present, not merely non-failing.
Asserting only that the binary row is the sole failure would hold equally if
`check_agy` returned early and ran no capability check at all — which is the
early return removed to close the previous round's finding, so it is the
regression most worth catching.

Evidence, all with `env -u GIT_INDEX_FILE`. The preflight module passes 11/11
both with AGY on PATH and with `~/.local/bin` removed. The full unit suite with
AGY absent is 1211 passed, 4 skipped, 0 failed after rebase onto 7cd3884; the
same command on 36fb178 reported 1 failed. Full suite with AGY present 1223
passed; scripts/ci_smoke.py exit 0.

Non-vacuity, each mutation restored from a byte snapshot with sha256 verified
equal afterward: restoring the early return when the binary is absent fails with
"no capability row ran, so this proves nothing about them"; making the binary row
never fail also fails. Both die for the reason they exist.

Not addressed, and deliberately so. The four live-CLI skips in
tests/unit/test_agy_seat_launcher.py are untouched and still skip where AGY is
absent. That is the governing FAIL's remaining disposition — a non-skipping
external gate in committed CI — and it is a CI-provisioning decision with real
cost rather than a test fix. It is carried, not claimed closed.

Risk class is kept at high-risk-control rather than dropped to
material-behavior. This change alone touches no authority surface and would not
have required that class on its own, but it answers one finding of a
high-risk-control review, and the binding is preserved rather than weakened
because a narrower task would have allowed less.

## Abuse Class Assessment

- - Stub above the logic under test: `shutil.which` is stubbed rather than `_binary`, so the name fallback to `antigravity` still executes. Stubbing `_binary` would have replaced the very lookup whose behaviour the binary row reports, which is the layer confusion an earlier round in this repository shipped.
- Sole-failure assertion as a vacuity hole: asserting the binary row is the only failure would also hold if no capability row ran at all, so their presence is asserted separately. Restoring the early return is measured to fail on exactly that assertion.
- Readiness misread from capability rows: capability rows now PASS beside a failing binary row by design, so the test pins the aggregate as not-ready in the same breath, and a mutation making the binary row never fail is measured to fail.
- Host state leaking back in: the test no longer reads PATH at all for this decision, and the claim is checked in both directions — AGY present and AGY removed from PATH — so a green result cannot be a property of the machine it ran on.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T18-13-10Z-operator-to-director-verify-addendum.md@ac54cfda45c691bedb196f2ed0dc401a83bd7897
- sha256:4956083165ee8f2a2d86e0ba911ed12135bb451c14a589bd61906de8a95564fd

Cursor at send: 0
