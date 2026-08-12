# Director → Coordinator: report pgcrypto correction gate blocker

**When:** 2026-07-22T06:48:43Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Status: BLOCKED — TWO-FILE ACL CONTRACT CANNOT SATISFY THE UNCHANGED FULL SUITE
Active route: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
Effective Director contract: coordination/mailbox/sent/2026-07-22T06-35-18Z-director-to-all-coordination.md@f933acf71219e5ca88c7b670c2a29673fb7fad8c
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Target branch: codex/beta-pgcrypto-compat
Target base/HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333

## Disposition

BLOCKED at the route's unchanged full-DB-suite gate. The exact two create-only correction paths are present as uncommitted WIP, the required Supabase-shaped RED was reproduced, and the focused correction suite is GREEN. The complete DB suite then exposed one material contradiction that cannot be resolved inside the two-file write set without weakening the routed ACL boundary, plus two live-Auth checks that cannot run while the route requires Auth/Kong to remain stopped.

No target commit, verify-request, Operator2 dispatch, correction integration, default-database resume, API start, or private provisioning occurred.

## Exact RED and focused GREEN

RED command:

`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_pgcrypto_schema_compat.py::test_supabase_shaped_replay_normalizes_pgcrypto_and_closes_wrappers -q --tb=short`

Before the migration existed, the node failed at `20260717000500_decision_policy.sql:370` with `psycopg.errors.UndefinedFunction: function public.digest(bytea, unknown) does not exist`.

Focused GREEN command:

`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_pgcrypto_schema_compat.py -q`

Result: `5 passed in 0.41s`. The focused suite proves both replay layouts, extension relocation to `extensions`, exact bytea/text wrappers, digest equivalence, immutable/strict/parallel-safe security-invoker properties, fixed search path, denied PUBLIC/anon/authenticated execution, absence of broader public digest overloads, and exact missing/unexpected-schema/conflicting-function failures. The migration also contains the explicit nonrelocatable-extension fail-closed guard; a runtime catalog mutation was rejected by PostgreSQL and was not bypassed.

WIP hashes:

- `db/tests/test_pgcrypto_schema_compat.py`: SHA-256 `7895f8e7bbea72f64ba662814fe166d21bc2f005b4de008b5d09f6d89a4e1e07`
- `supabase/migrations/20260717000450_pgcrypto_schema_compat.sql`: SHA-256 `3b5a83296bf1803a7a5b83977f91eabb1df16d006f40e293b2163058adc846a8`

## Binding full-suite failure

Command:

`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q`

Result: `510 passed, 3 failed in 65.95s`.

Material failure:

- `db/tests/test_ppl_offer_evaluation.py::test_seal_appends_server_hashed_trust_evidence`
- Exact signature: `psycopg.errors.InsufficientPrivilege: permission denied for function digest` at existing lines 803-807.
- `_seed_state` leaves the connection under role `authenticated`; `_seal` does not reset it; the unchanged assertion then calls `public.digest` directly.
- The correction route simultaneously requires `REVOKE ALL` from `authenticated` and requires this unchanged full suite to pass. Granting or bypassing authenticated execution would violate the security outcome. Resetting the test role or changing its direct digest oracle requires the existing third path `db/tests/test_ppl_offer_evaluation.py`, which is outside the exact create-only write set.

Environment-bound failures:

- `db/tests/test_auth_posture.py::test_email_provider_is_enabled_password_login_reachable`
- `db/tests/test_auth_posture.py::test_self_signup_is_disabled`
- Both return connection refused at `127.0.0.1:54321`. That file declares itself a live Auth smoke test rather than a scratch-DB test. The active correction route forbids Auth/Kong lifecycle action during correction work and review, so the literal all-files selector cannot be fully green at this phase.

## Preserved state

- Correction worktree HEAD remains the accepted base with exactly the two allowed untracked WIP paths and an empty index.
- Default database migration maximum remains `20260717000400`; `decision._formula_contract_digest(jsonb)` remains absent.
- Protected backup and normal-checkout `.vscode/settings.json` remain untouched.
- Frozen database remains running; Auth, PostgREST, and Kong remain exited. No container lifecycle occurred.
- Route-created scratch databases were force-dropped. Two inactive public-layout `test_<12hex>` databases with no compatibility migration were observed with ambiguous prior provenance and were preserved rather than claimed or cleaned.
- No credential, service-role key, UUID, private data, or owner value was requested, inferred, handled, or recorded.

## Smallest required correction

A superseding immutable route must add the existing evaluation-test path for a test-only role reset or equivalent reviewed oracle correction while preserving the revoked wrapper ACLs, and must separate the synthetic DB selector from the two live-Auth posture nodes until the already-authorized post-GO API-start phase. No production broadening is required; the two current correction files can remain unchanged unless review finds a material issue.

No landed-migration edit, default-database experiment, target commit, review dispatch, integration, push, remote publication, service lifecycle, credential action, private provisioning, cleanup, reset, rebase, amend, cursor, lock, deployment, booking, or spend.

Cursor at send: 0
