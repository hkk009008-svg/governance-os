# Route Preflight Friction Reduction Design

**Status:** verbal design approved; written spec awaiting user review
**Date:** 2026-07-22
**Design base:** `9e4e18c50edf4ec783f49bf8a0f4a487aa275213`

## 1. Decision

Make three small corrections to the existing Pipeline workflow:

1. Make candidate route validation apply the same structured target-guidance
   grammar that the evidence-ledger start guard applies after commit.
2. Make candidate lineage validation prove that an autonomous continuation
   extends the current authoritative tip, and prevent a new Coordinator legacy
   route from reopening a task that already has autonomous lineage.
3. Record one evidence-ledger service-lifecycle preflight rule: inspect the
   installed Supabase CLI and exact container state before an authorized
   action, and never assume `supabase start` can partially resume stopped
   sibling services when the database is already running.

The existing missing-`wait_threads` fallback remains unchanged. It worked as
designed during Task 6: one bounded thread snapshot was followed by immutable
Git/mailbox reconciliation without redispatch.

This is the strict-minimum option selected by the user. It adds no service,
helper command, dependency, registry, state store, route format, or product
behavior.

## 2. Confirmed Defects And Evidence

### 2.1 Candidate validation and start-guard grammar disagree

`scripts/protocol_capacity.py::_validate_route_file` recognizes a route,
checks autonomous parent continuity, and checks side-effect tokens. It does
not call the pure target-guidance parser used by
`scripts/ledger_start_guard.py::parse_route_guidance_body`.

Task 6 revision 34 therefore passed capacity validation, route lineage, and
Pipeline smoke even though its `## Target Allowed Paths` section continued
with explanatory prose. The mandatory Operator2 start guard later rejected
the same committed bytes with:

```text
invalid committed route guidance: allowed-path section accepts bullet paths only
```

The formal FAIL is
`coordination/mailbox/sent/2026-07-22T01-56-46Z-operator2-to-director-verification-report.md@ed4c6c0f4b4f6e3226de3b8210ca661adef10f0e`.
Revision 35 fixed only the route text by placing `## Allowed Path Semantics`
after the bullet list and then passed both validators:
`coordination/mailbox/sent/2026-07-22T02-01-34Z-director-to-all-coordination.md@75ff28ddedb10705a32edb30a0edae9b125d14d9`.

### 2.2 Parent continuity does not prove current-tip continuity

`scripts/protocol_capacity.py::_autonomous_candidate_parent_issues` proves
that the named parent is effective, belongs to the same task, and has the
immediately preceding revision. It does not prove that the parent is the
current authoritative tip for that task.

Task 6 also demonstrated the adjacent legacy case. A new Coordinator route
was structurally valid before commit but forked the already-autonomous task
lineage after commit. No action was dispatched under that invalid route. The
route was reverted and the incumbent Director continued from its own
authoritative parent instead:

- invalid route commit: `0e250a3cbb3eb9060c544186a4b05a44b0ab39fb`;
- preserving revert: `4d759972815315a4663315feb4a3aececa318825`.

The defect is pre-commit incompleteness, not a need to change the committed
lineage resolver.

### 2.3 Supabase partial-start behavior was assumed, not established

The first Task 6 Auth/Kong route used `supabase start --exclude ...` while the
database container was already running. Supabase CLI `2.109.0` treated the
project as already running, warned about invalid exclusions, and did not start
Auth or Kong. The Director failed closed, restored the exact pre-state, and
reported the durable blocker at
`coordination/mailbox/sent/2026-07-22T00-32-24Z-director-to-coordinator-coordination.md@7b705644ffd2af161741c64c8dc31770daf2761f`.

The repository does not need a lifecycle controller. It needs one explicit
preflight rule so future routes do not infer partial-resume semantics from the
ordinary full-stack command.

## 3. Scope

### Behavior-changing surfaces

- `scripts/protocol_capacity.py`
- `scripts/route_lineage.py` only if a small public staged-candidate helper is
  required to avoid duplicating task identity or route classification
- `tests/unit/test_protocol_capacity.py`
- `tests/unit/test_route_lineage.py` only if `scripts/route_lineage.py` changes

### Instruction-only surface

- `docs/protocol/codex/ledger-cli-adoption.md`

The existing `AGENTS.md` already sends every evidence-ledger route through the
adoption bridge, so the service rule is written once at the canonical source.
It is not copied across prompts or skills.

### Explicit non-goals

- changing committed historical routes or making malformed history valid;
- changing autonomous route effectiveness, transfer, or outcome semantics;
- creating a new route schema, parser module, validator executable, lifecycle
  helper, service supervisor, or retry loop;
- modifying `ledger_start_guard` behavior or duplicating its guidance grammar;
- changing the Codex app, `wait_threads`, `read_thread`, or task-monitor rules;
- changing fixed-writer behavior or the prior fast-resume correction;
- changing evidence-ledger product bytes, Supabase configuration, containers,
  databases, dependencies, remote refs, or user data; and
- granting merge, push, deployment, activation, service, cursor, lock, spend,
  or other external-effect authority.

## 4. Candidate Route Grammar Contract

Candidate validation reuses
`ledger_start_guard.parse_route_guidance_body(body)` as the single grammar
implementation. The implementation may use a direct import or an existing
dependency-safe import pattern; it must not copy the regular expressions or
allowed-path loop into `protocol_capacity.py`.

After a candidate is recognized as a route event, capacity validation calls
that parser. A `ValueError` becomes a blocking `G7` route issue containing the
route filename and the parser's reason. Validation remains read-only.

The structured contract remains:

- `Target worktree`, when present, is absolute and contains no traversal or
  wildcard;
- `Accepted target HEAD`, when present, is a full lowercase SHA;
- at most one `## Allowed Paths` or `## Target Allowed Paths` heading exists;
- every nonblank line under that heading, up to the next Markdown heading, is
  one safe repository-relative bullet path; and
- duplicate, absolute, traversing, wildcard, or malformed paths fail closed.

All guidance fields remain optional so a new candidate with no target-guidance
section retains existing behavior. Historical committed routes are not
revalidated or rewritten by this pre-commit check. The corrected revision-35
shape remains valid.

## 5. Candidate Lineage Contract

### Autonomous candidates

After structural parsing, candidate validation resolves the committed routes
for the candidate's exact Task ID using the existing `RouteBatchReader` and
`resolve_task_routes` behavior.

- A revision-zero candidate with no parent is accepted only when no committed
  route already exists for that task.
- A candidate with a parent must retain the existing effective-parent,
  same-task, and consecutive-revision checks.
- The exact parent ref must also equal the current conflict-free authoritative
  tip for that task.
- If the committed same-task lineage is unresolved, ineffective, or forked,
  the candidate fails `G7`; candidate validation does not choose a winner.

This check observes current committed state plus the staged candidate. It does
not claim the candidate is effective before commit.

### Coordinator legacy candidates

A newly validated Coordinator/Coordinator2 legacy route remains accepted when
its Task-board has only legacy history or no history. If that exact Task-board
already has any committed autonomous route, the candidate fails `G7` with an
actionable message directing the incumbent owner to publish an autonomous
continuation or use the existing durable transfer protocol.

This preserves legacy-only compatibility while preventing a legacy route from
becoming a competing base after a task has crossed into autonomous lineage.

## 6. Evidence-Ledger Service Preflight Rule

Add one short rule to the canonical ledger adoption bridge:

1. Before an authorized local Supabase lifecycle action, inspect
   `supabase --version` and the exact existing project container/service state.
2. If the database is already running while required siblings are stopped, do
   not infer that `supabase start` or `--exclude` will partially resume those
   siblings.
3. Stop and report the observed state unless a separate route or user grant
   authorizes an exact existing-container action with frozen identities and a
   restoration contract.

The rule is advisory preflight plus an authority boundary. It does not execute
a service action, prescribe a universal Docker workaround, or authorize
network, acquisition, configuration, restart, or cleanup.

## 7. Error Handling

| Condition | Result |
|---|---|
| Malformed target-guidance section | Blocking `G7` before commit |
| Candidate parent is effective but not the current task tip | Blocking `G7` before commit |
| Existing same-task lineage is unresolved or forked | Blocking `G7`; no inferred winner |
| Revision-zero root targets an existing task | Blocking `G7` |
| Legacy candidate targets an autonomous task | Blocking `G7`; use autonomous continuation/transfer |
| Legacy-only route chain | Existing compatibility retained |
| DB already running and sibling-service behavior is uncertain | Stop, report exact state, seek exact authority if action is needed |
| `wait_threads` handler unavailable | Existing one-snapshot/artifact fallback; no code change |

Every failure is read-only and preserves the route bytes, Git index, refs,
mailbox, cursors, locks, services, and product state.

## 8. Verification Contract

Implementation follows RED to GREEN and adds focused regression cases for:

- the revision-34 malformed allowed-path section failing candidate validation;
- the revision-35 corrected shape passing candidate validation;
- an autonomous candidate extending the exact authoritative tip passing;
- an autonomous candidate extending an effective but superseded parent failing;
- a revision-zero root for an existing task failing;
- an unresolved same-task lineage failing without choosing a winner;
- a Coordinator legacy candidate for an autonomous task failing; and
- a new or legacy-only Coordinator Task-board retaining compatibility.

The smallest required verification profile is:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q  # only when that module changes
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

The owner also runs the live capacity validator against a temporary candidate
body matching both Task 6 regression shapes. A distinct, different-model,
non-author Operator reviews the actual committed implementation range and
alone issues GO, NITS, or FAIL.

## 9. Ownership, Rollout, And Resume Point

One Director owns the implementation and canonical doctrine edit. No
concurrent implementer edits the shared validator files. A non-author Operator
reviews the final exact range.

The change is backward compatible for legacy-only tasks and additive for new
candidate validation. Rollback is one separately authorized local revert; no
migration, service cleanup, or data repair is required.

The beta-activation checkpoint remains paused and unchanged while this
friction slice is implemented and reviewed. After Operator GO and Coordinator
reconciliation, work resumes from the already-established state:

- Task 6 local acceptance commit
  `87a10b787a2f01f4353cad6a5e8ed338c381d333` has canonical GO;
- it remains two fast-forwardable commits ahead of evidence-ledger `main`; and
- integration, managed deployment/Auth, one-owner provisioning, required-info
  entry, and physical Windows Edge acceptance remain the next separately
  governed beta actions.
