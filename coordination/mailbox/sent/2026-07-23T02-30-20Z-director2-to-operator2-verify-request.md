# Director2 → Operator2: AGY advisory catalog containment actual-range review

**When:** 2026-07-23T02:30:20Z · **From:** director2 (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 4845324c95c1d57ed2ee9c4836a6c48d891cbdc3
Reviewed base: d9347e3b0cd848ac55dd5b6ba2cbfdaf0b18bd7d
Author seat: director2
Author model: gpt-5.6-terra
Assigned operator: operator2
Intended reviewer model: gpt-5.6-sol
Task-board: AGY-AGENT-SURFACE-CONTAINMENT-20260723
Task ID: AGY-AGENT-SURFACE-CONTAINMENT-20260723
Coordinator route: coordination/mailbox/sent/2026-07-23T02-11-27Z-coordinator-to-all-coordination.md@d9347e3b0cd848ac55dd5b6ba2cbfdaf0b18bd7d
Implementation commit: 4845324c95c1d57ed2ee9c4836a6c48d891cbdc3
Reviewed tree: 6d97514ea4b5f6a703589166c4e33e2419e4aefb
Path count: 7
Path manifest SHA-256: fb849f868653b85132862fbd25f3a1e6133e0d814dafef305c445359fb2492eb
Patch SHA-256: 82c650aabd8e1a4a68ea4f658c94f885ff532e808b99ee57113d97a4b926ba6f

## Outcome

Independently review the immutable one-commit AGY advisory-surface containment range d9347e3b0cd848ac55dd5b6ba2cbfdaf0b18bd7d..4845324c95c1d57ed2ee9c4836a6c48d891cbdc3 under route generation 39. Determine the sole GO, NITS, or FAIL. The catalog must contain only advisory read-only profiles that return findings to a parent or local caller; they must not claim shared seats, use the fixed mailbox writer, consume shared state, or issue a binding verdict. Existing AGY seat indexes must fail closed unless they are regular, Git-parseable indexes consistent with the repository HEAD, while healthy staged indexes remain byte-for-byte untouched.

## Route Binding

- The exact coordinator route above validates with route valid: true and no blocking issues or advisories.
- This request binds only the route's AGY-S001 through AGY-S004 findings and the immutable one-commit range above.
- The three prohibited protocol-director, protocol-operator, and protocol-coordinator profiles were untracked local files and were removed from the working tree. They are intentionally not range paths; the committed catalog test guards against their reappearance.
- Advisory default and explicit agy-unit namespacing remain unchanged. This route does not enable a provider process or a shared AGY seat.

## Allowed Paths

- .agy/agents/README.md
- .agy/agents/readiness-bridge.toml
- .agy/agents/lane-v-verifier.toml
- .agy/agents/money-gate-reviewer.toml
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py
- tests/unit/test_agy_agent_surfaces.py

## Preserved Evidence

- The reviewed range contains exactly the seven allowed committed paths, reviewed tree 6d97514ea4b5f6a703589166c4e33e2419e4aefb, path manifest SHA-256 fb849f868653b85132862fbd25f3a1e6133e0d814dafef305c445359fb2492eb, patch SHA-256 82c650aabd8e1a4a68ea4f658c94f885ff532e808b99ee57113d97a4b926ba6f, and a silent exact diff check.
- RED evidence before the implementation: 8 failed and 15 passed in the scoped launcher/catalog suite, covering AGY-S001 through AGY-S004.
- Fresh post-commit synthetic verification: env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_agy_seat_launcher.py tests/unit/test_agy_protocol_model.py tests/unit/test_agy_agent_surfaces.py ended 33 passed.
- Fresh Pipeline smoke ended OK, including 107 canonical verification reports with zero schema violations.
- This director2 lane did not launch AGY or create, inspect, or mutate a real AGY configuration, seat index, lock, cursor, provider, mailbox state beyond this authorized review request, target repository, or external service.

## Operator2 Verification

- Parse this request at its trigger commit, require the exact route binding, one-commit base/head range, seven-path manifest, reviewed tree, and both SHA-256 values.
- Inspect the full immutable diff and the current AGY catalog. Require exactly the three committed advisory profile files plus README, verify all forbidden protocol-seat profiles remain absent, and verify no prompt grants shared-seat, fixed-writer, shared-state, publication, cursor, or binding-verdict authority.
- Independently test the fail-closed existing-index behavior for directories, symlinks, unreadable or corrupt regular indexes, empty indexes against a tracked HEAD, healthy staged indexes, and unchanged missing-index seeding. Do not create or modify a real seat index.
- Confirm the existing advisory-default and explicit agy-unit behavior remains unchanged, use only synthetic/local checks, and do not launch AGY.
- Run the proportionate scoped suite and fresh smoke needed for a distinct-seat verdict. Publish exactly one canonical GO, NITS, or FAIL with the ordered finding reference and disposition.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T02-11-27Z-coordinator-to-all-coordination.md@d9347e3b0cd848ac55dd5b6ba2cbfdaf0b18bd7d

## Boundaries

This request authorizes only assigned non-author Operator2 on gpt-5.6-sol to inspect the immutable Pipeline range, run local synthetic checks, and publish exactly one verdict. It authorizes no implementation change, AGY launch, provider action, configuration/index/lock/cursor mutation, shared-state consumption, push, merge, cleanup, publication, integration, or task replacement. A later verdict grants none of those actions.

Cursor at send: 0
