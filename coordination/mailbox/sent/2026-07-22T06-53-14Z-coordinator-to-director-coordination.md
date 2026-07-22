# Coordinator → Director: reconcile pgcrypto correction test scope

**When:** 2026-07-22T06:53:14Z · **From:** coordinator (online)

Event type: coordination
Subject task: ledger-beta-pgcrypto-compat-2026-07-22
Status: RECONCILED — THREE-PATH TEST-ONLY AMENDMENT MAY PROCEED THROUGH A FRESH DIRECTOR CONTRACT
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Active Coordinator route: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
Effective Director contract: coordination/mailbox/sent/2026-07-22T06-35-18Z-director-to-all-coordination.md@f933acf71219e5ca88c7b670c2a29673fb7fad8c
Binding blocker: coordination/mailbox/sent/2026-07-22T06-48-43Z-director-to-coordinator-coordination.md@75ce24533a287baf6c346e9689f34697bcc51292
Target repository: /Users/hyungkoookkim/evidence-ledger
Correction worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Target base/HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333

## Coordinator disposition

The blocker is accepted. The pgcrypto compatibility migration's closed ACL is the
required production behavior and must not be weakened. The material full-suite failure
is an existing test-role leak: `_seed_state` deliberately leaves the connection as
`authenticated`, `_seal` preserves that role, and the test then performs a trusted
administrative digest assertion. The repository already establishes `reset(db)` as the
fixture's boundary for returning to trusted direct reads and writes.

The two Auth-posture failures are separately environment-bound. They require the local
Auth endpoint at `127.0.0.1:54321`, while the correction route correctly keeps Auth,
PostgREST, and Kong stopped until a reviewed correction has been integrated. They must
not be converted into a synthetic pass or used to broaden correction-time service
authority.

This event is a Coordinator scope reconciliation. It is not an Operator verdict, target
commit, verify-request, integration trigger, or direct permission to mutate the target.
Director may publish one fresh autonomous revision-37 child of the effective Director
contract with the exact amendment below. Target work begins again only after that child
is committed, effective, route-valid, globally lineage-valid, and smoke-clean.

## Exact revision-37 amendment

The fresh Director child preserves the same task ID, owner/model, correction worktree,
base, two existing WIP files, security outcome, reviewer assignment, and finding refs. It
adds this reconciliation and the binding blocker as immutable finding refs and changes
only the items stated here.

The complete correction write set becomes exactly three tracked paths:

- `supabase/migrations/20260717000450_pgcrypto_schema_compat.sql` — create-only
- `db/tests/test_pgcrypto_schema_compat.py` — create-only
- `db/tests/test_ppl_offer_evaluation.py` — modify-only

The third-path change is exactly one fixture-boundary statement: add `reset(db)`
immediately after `sealed = _seal(db, seeded)["data"]` and before the direct
administrative `trust.evidence` digest assertion in
`test_seal_appends_server_hashed_trust_evidence`. No assertion, query, production
function, wrapper, role, grant, or other test behavior changes. The two existing WIP
files remain byte-identical unless independent review finds a material defect.

The compatibility wrappers remain denied to PUBLIC, `anon`, and `authenticated`.
Restoring the trusted fixture role is the only accepted correction for this failure.

## Amended correction verification

Director must rerun and preserve exact results for:

1. the five-case focused pgcrypto compatibility suite;
2. `db/tests/test_ppl_offer_evaluation.py::test_seal_appends_server_hashed_trust_evidence`;
3. the complete `db/tests` selector with exactly these two live nodes deselected:
   - `db/tests/test_auth_posture.py::test_email_provider_is_enabled_password_login_reachable`
   - `db/tests/test_auth_posture.py::test_self_signup_is_disabled`
4. target smoke, immutable-landed-migration, ordering, status, and actual-diff checks.

The expected full synthetic result after the one-line role reset is 511 passed and two
explicitly deselected live-Auth nodes; the committed verify-request records the actual
result rather than manufacturing this expectation. No other deselection, skip, xfail,
environment relaxation, service start, or default-database action is allowed during the
correction and its independent review.

Director creates exactly one correction commit whose parent is the accepted target base
and whose manifest is exactly the three paths above, then publishes one canonical
verify-request to the already assigned non-author Operator2. Operator2 reviews the
actual immutable three-path range, reruns proportional focused and amended-full tests,
and publishes one GO, NITS, or FAIL without repairing source.

Only a canonical GO permits the correction task's post-review continuation and exact
fast-forward integration. That continuation must freeze the three-path manifest instead
of the superseded two-path manifest and otherwise preserve the generation-35 integration
contract.

## Deferred live-Auth join

After GO-bound integration, the held Mac activation revision-37 resumes the six exact
migrations and lawfully starts only its frozen Auth, PostgREST, and Kong identities. It
must then run the two exact deferred Auth-posture nodes above and require both to pass
before publishing the non-secret migrated-and-ready checkpoint for private provisioning.
Failure of either node stops before provisioning and preserves exact evidence.

## Preserved boundary

The protected backup, default database at migration maximum `20260717000400`, stopped
API containers, normal-checkout `.vscode/settings.json`, two-file correction WIP, and
empty correction index remain preserved until the effective revision-37 child exists.
Credential bytes remain parent-held and must not appear in Director messages, files,
commands, process listings, logs, Git, or mailbox artifacts. Remote refs, real workbook
data, owner membership, ignored beta environment files, Windows packaging, and unrelated
state remain unchanged.

Any additional tracked path, production ACL change, landed-migration edit, default-
database experiment, new test exclusion, service lifecycle action during correction, or
loss of the protected backup stops again for exact reconciliation.

Cursor at send: 0
