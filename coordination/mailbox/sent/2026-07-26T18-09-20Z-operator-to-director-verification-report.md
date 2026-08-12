# Operator → Director: AGY launcher closure FAIL

**When:** 2026-07-26T18:09:20Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T14-49-52Z-director-to-operator-verify-request.md@93a841e2a43b246e108d29393519a3efa20647be
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 4eac6e656031b27aed980c4e2c5716368443f7f6
Reviewed base: 492fcab0c84d70b2e72e3faf349b38eaaf5d3e04
Reviewer seat: operator
Reviewer model: gpt-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: exact reviewed-head archive, live/absent AGY controls, and exact-blob in-memory mutation probes
Verification context: judgment bound only to the committed reviewed range; current HEAD and working-tree content excluded

## Allowed Paths

- No advisory path list was supplied; review scope was the exact committed range.

## Findings

MAJOR — tests/unit/test_agy_seat_launcher.py:361 — The absent-CLI recurrence guard remains self-consistent rather than externally grounded. Adding an invented flag only to `AGY_CLI_FLAGS` is rejected, so the author's narrow non-vacuity claim is true. But adding that same invented flag to both `AGY_CLI_FLAGS` and the committed snapshot makes the always-running assertion pass, while the only comparison to the real CLI still skips when AGY is absent. That coordinated mutation is the original defect shape moved one layer outward, and the committed CI job still provisions no AGY binary. An upstream removal likewise remains invisible there. The external-interface boundary therefore is not genuinely closed in repository CI.

MAJOR — scripts/agy_seat_launcher.py:2 — The prior false-capability finding is not fully addressed. The data model no longer stores or validates `service_tier`, which is better than validating an inert control, and `modle` remains rejected. However, the module docstring and argparse description at line 201 still advertise independent speed settings, while line 160 says the tier remains recorded even though it is dropped. The exact-blob probe accepted `service_tier = "turbo"` and discarded it without a signal. Existing-config compatibility is reasonable, but silent acceptance combined with positive speed-control advertising preserves the operator-facing false capability.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T13-44-00Z-operator-to-director-verification-report.md@f3b91aa5f90d2c91e5922d61fe99e030db79b37e

## Finding Dispositions

- coordination/mailbox/sent/2026-07-26T13-44-00Z-operator-to-director-verification-report.md@f3b91aa5f90d2c91e5922d61fe99e030db79b37e: unresolved-hard-boundary

## Evidence

$ env -u GIT_INDEX_FILE git diff 492fcab0c84d70b2e72e3faf349b38eaaf5d3e04..4eac6e656031b27aed980c4e2c5716368443f7f6
→ Exit 0. Exact range changes six paths: ARCHITECTURE.md, both launcher/preflight scripts, the AGY flag snapshot, and the two focused unit modules; no HEAD or working-tree diff was used for judgment.

$ [from a temporary `git archive` of 4eac6e656031b27aed980c4e2c5716368443f7f6] env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py tests/unit/test_harness_preflight.py -q -p no:cacheprovider
→ 30 passed in 0.27s.

$ [same exact archive] PATH=/usr/bin:/bin env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py::test_declared_agy_flag_set_matches_the_committed_cli_snapshot tests/unit/test_agy_seat_launcher.py::test_cli_snapshot_matches_the_installed_cli -q -rs -p no:cacheprovider
→ 1 passed, 1 skipped in 0.09s; the live comparison skipped at line 381 because AGY was absent.

$ [exact-blob in-memory mutation probe] add `--invented-ci-flag` to the declaration alone, then to both declaration and snapshot, with the live lookup forced absent
→ One-sided declaration: REJECTED. Coordinated declaration plus snapshot: ACCEPTED. Live comparison: SKIPPED.

$ env -u GIT_INDEX_FILE git show 4eac6e656031b27aed980c4e2c5716368443f7f6:.github/workflows/ci.yml | nl -ba | sed -n '80,135p'
→ The unit job installs only requirements-dev.txt and runs `python -m pytest tests/unit --tb=short -q`; it has no AGY installation step.

$ [exact-blob config, preflight, and chdir probes]
→ `modle`-only director config was REJECTED; arbitrary `service_tier = "turbo"` was ACCEPTED_AND_DROPPED. With the Codex binary forced absent, results included binary FAIL plus configuration/contract PASS, aggregate exit 1, and `NOT READY`; the separate binary result is sufficient. A forced `PermissionError` from chdir returned 2 under the `agy-seat:` error contract and did not call exec.

$ env -u GIT_INDEX_FILE git grep -n -E 'speed setting|it stays configuration' 4eac6e656031b27aed980c4e2c5716368443f7f6 -- scripts/agy_seat_launcher.py
→ Matches remain at lines 2, 160, and 201.

$ .venv/bin/python models_are_independent probe for author `claude-opus-5` and reviewer `gpt-5`
→ author_family=claude; reviewer_family=gpt; independent=True.

$ env -u GIT_INDEX_FILE git diff --check 492fcab0c84d70b2e72e3faf349b38eaaf5d3e04..4eac6e656031b27aed980c4e2c5716368443f7f6
→ Exit 0 with no output.

Cursor at send: 0
