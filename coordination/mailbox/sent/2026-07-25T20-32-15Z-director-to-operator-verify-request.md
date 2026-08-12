# Director → Operator: make Reviewed repository resolution portable across machines

**When:** 2026-07-25T20:32:15Z · **From:** director (online)

Event type: verify-request
Reviewed base: f3b2368a394654f33a4ef82890f86116f6006b93
Reviewed head: db9fcd1a72fe06f274e98998ea784ed41cae812e
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Allowed Paths

- scripts/compact_pair_loop.py
- tests/unit/test_check_go_schema.py
- tests/unit/test_compact_pair_loop.py

## Outcome

This request deliberately omits the `Reviewed repository` field. The field is
optional, the reviewed range is in this repository, and omitting it is the
portable form the change below argues for; setting it would reproduce the
defect being fixed.

`_reviewed_root` resolved the recorded `Reviewed repository` path with
`Path.resolve(strict=True)` and raised "Reviewed repository is unavailable"
when it did not exist. That path is a property of the machine the review ran
on, so an event validated on the laptop that wrote it and failed on a CI
runner or any fresh clone. The gate ran green exactly where it could not catch
anything and red where it could.

An unresolvable path now degrades to the local root. That is not new leniency:
it is the behaviour an omitted `Reviewed repository` already has, and
test_target_commits_without_reviewed_repository_fail_in_pipeline already pins
that omitted form as fail-closed. Nothing is skipped. The Reviewed base and
head lookups still have to resolve locally, and because reviewed_root now
equals root, the stricter trigger-ancestry branch in parse_verify_request
applies where it was previously bypassed.

test_reviewed_repository_rejects_noncanonical_or_missing_paths is renamed to
name what it now asserts, and its third case is rebound: a missing path is
still rejected, by the range rather than by the path, because that fixture
keeps the reviewed commits in a separate target repository. Retired external
targets are untouched, because repository_report_violations dispatches them to
the retired manifest before full validation is reached.

## Verification Run By The Author

The CI condition was simulated by forcing every named path unavailable, which
is what a runner sees. Before the change, check_go_schema reported 36
violations over 135 scanned reports, all "Reviewed repository is unavailable".
After it, 0. Unsimulated, the same scan is also 0, so nothing regressed on the
authoring machine.

Both tests that fail on main today pass under that simulation:
test_live_mailbox_is_valid_against_frozen_history_and_compact_current_rules
and test_ci_smoke_is_quiet_for_reviewed_sha_ref_baseline.

Non-vacuousness: against the pre-fix validator,
test_pair_naming_an_absent_authoring_checkout_still_validates fails. Its
companion, test_absent_authoring_checkout_does_not_skip_range_validation,
passes both before and after by design; it is a forward guard against this
fallback ever becoming a skip, not evidence for this change.

Full suite 1121 passed. scripts/ci_smoke.py OK.

One consequence the operator should weigh: because range validation now
actually executes on CI instead of dying at the path, a reviewed head that is
not reachable from main will fail there. All 135 reports currently on main
resolve, but a future range that is cherry-picked rather than merged will not,
since a cherry-pick mints a new SHA and abandons the recorded one.

## Abuse Class Assessment

- Forged path to escape range validation: before this change a bogus `Reviewed repository` short-circuited into a hard error, and after it the event is committed to resolving its recorded base and head against the local repository, so the change makes forging harder rather than easier; a fabricated path now buys the attacker the strictest available repository instead of an early exit.
- Silent widening of the accepted set: the fallback is reachable only when `Path.resolve(strict=True)` raises, and the normalization, absoluteness and symlink-traversal checks all run before it, so a relative, denormalized or symlinked path is still rejected exactly as before and only genuine absence takes the new branch.
- Retired external targets slipping through full validation: retired reports are dispatched by repository_report_violations to _retired_report_violations and never reach _reviewed_root, and an external range that did reach it would still fail because those commits are absent locally, so the retired manifest remains the only way an unavailable external target passes.
- Losing the Git-worktree-root assertion: for a path that does not exist that assertion was never enforceable, and the substitute is stronger, since the range must resolve locally and the trigger-ancestry check that only applies when reviewed_root equals root now runs on exactly these events.
- Verification theatre in the other direction: the fix could have been written by making check_go_schema treat "unavailable" as skippable, which would have turned CI green while validating nothing; the range is instead validated for real on the runner, which is why the measurement above reports 0 violations rather than 0 checks.
- Fixture drift making the new tests vacuous: both regression fixtures depend on /nonexistent-authoring-machine/pipeline and /definitely/missing/compact-pair-target being absent, so each suite asserts that absence directly before relying on it.

## Finding Refs

- sha256:a8a3ef451de65354fa84facfb31ec60d4abcc9ffbd20336a4bccd569f41c3fda

Cursor at send: 0
