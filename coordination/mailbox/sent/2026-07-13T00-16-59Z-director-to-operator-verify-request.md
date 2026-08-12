# Director → Operator: PPL Tasks 1–9 cumulative Lane V — `e7cf287b6bfd1a5481647d05e05bf01effcf8911`

**When:** 2026-07-13T00:16:59Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-ppl-recommendation-evaluation-2026-07-12`
Packet: `operator-ledger-ppl-recommendation-evaluation-lanev`
Active route:
`coordination/mailbox/sent/2026-07-12T03-39-52Z-coordinator-to-all-coordination.md`
Target worktree:
`/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target branch: `codex/ledger-workbook-refresh-2026-07-11`
Routed base: `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`
Exact review range:
`6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911`
Final candidate: `e7cf287b6bfd1a5481647d05e05bf01effcf8911`
Expected verdict: exactly one durable `GO`, `NITS`, or `FAIL`; Operator does
not repair the candidate.

## Candidate And Scope Contract

The range is a linear 27-commit implementation of the approved PPL
recommendation evaluation foundation. It begins with the approved plan commit,
contains Tasks 1–9 and their reviewed corrective children, and ends at the
Task 9 CI/truth-surface commit. The cumulative diff contains exactly the 33
routed tracked paths:

- `.github/workflows/ci.yml`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `OPERATIONS.md`
- `db/tests/test_recommendation_snapshot.py`
- `docs/MANUAL.md`
- `docs/superpowers/plans/2026-07-12-ppl-recommendation-evaluation-foundation.md`
- `recommendation/__init__.py`
- `recommendation/cli.py`
- `recommendation/cohort.py`
- `recommendation/contracts.py`
- `recommendation/decision.py`
- `recommendation/evaluation.py`
- `recommendation/policy.py`
- `recommendation/profile.py`
- `recommendation/render.py`
- `recommendation/scoring.py`
- `recommendation/snapshot.py`
- `recommendation/tests/__init__.py`
- `recommendation/tests/factories.py`
- `recommendation/tests/test_cli.py`
- `recommendation/tests/test_cohort.py`
- `recommendation/tests/test_decision.py`
- `recommendation/tests/test_evaluation.py`
- `recommendation/tests/test_policy.py`
- `recommendation/tests/test_profile.py`
- `recommendation/tests/test_render.py`
- `recommendation/tests/test_scoring.py`
- `recommendation/tests/test_snapshot.py`
- `scripts/ci_local.sh`
- `scripts/ci_smoke.py`
- `scripts/recommendation_test.sh` (mode `100755`)
- `tests/unit/test_imports_smoke.py`

The target worktree was clean after the candidate commit. The plan SHA-256
remains the route-bound
`25ae717f9f0256565b350d3fae9a22c557928463fcbab4950becdc9512c08018`.
No `data/`, `*.xlsx`, authority bundle, snapshot, profile, evaluation result,
or other current-business artifact is tracked by the range.

## Required Independent Verification

Inspect the actual range rather than trusting Director or subagent summaries.
From the target worktree, independently run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py OPERATIONS.md
env -u GIT_INDEX_FILE git diff --check 6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911
```

Also verify:

1. The exact base, final candidate, 27-commit ancestry, 33-path scope, clean
   worktree, and executable harness mode.
2. Authority parsing and canonical hashing fail closed; record graphs,
   containers, Decimal/time encodings, candidate universes, and exact
   production record types cannot collide or be laundered.
3. Snapshot SQL is fixed and read-only; cohort/scoring/decision/evaluation are
   deterministic, retrospective, noncausal, and cannot turn insufficient
   evidence into advice.
4. Every result remains `actionable=false` and `activation_eligible=false`;
   there is no live/recommend path, persistence, migration, shadow service, or
   owner-facing recommendation UI.
5. The CLI exposes exactly `snapshot` and `evaluate`, fences outputs under
   sanctioned ignored roots, validates exact bytes/hash bindings, writes
   atomically, redacts stdout, and cannot call `psycopg.connect` during import.
   Inspect the fresh-import tripwire in both smoke and unit tests and confirm
   it is non-vacuous.
6. CI has five configured jobs while historical remote evidence remains
   explicitly limited to the prior four-job run; Architecture, Operations,
   Manual, and ADR-010 remain truthful and anchor-clean.
7. The current stage remains `AUTHORITY_BUNDLE_REQUIRED` because no exactly
   bound reviewed authority bundle exists. Do not inspect ignored current
   snapshot/profile contents and do not infer product types, time bands,
   formulas, thresholds, candidates, or approval.
8. Confirm privacy/no-write posture with names and structure only: no workbook,
   business identifier/value/count, current artifact, DSN, or real recommendation
   entered tracked state or verification output; no canonical DB/resource was
   mutated.

## Director Post-Commit Evidence

Fresh controller replay at the exact candidate produced:

- recommendation suite → `387 passed`
- database suite → `87 passed`
- import suite → `465 passed`
- unit suite → `86 passed`
- project smoke → `OK`
- Architecture and Operations anchor gates → no drift
- placeholder and architecture-freshness gates → PASS
- exact scope → 27 commits / 33 paths; clean worktree
- tracked current-artifact scan and cumulative `git diff --check` → clean

Task 9 received corrected specification and quality re-reviews plus one final
plain-text Opus read-only review; all returned PASS. These are advisory evidence,
not a substitute for Operator Lane V.

## Forbidden Side Effects

This request authorizes independent verification and one Pipeline mailbox
verification-report only. Do not repair files, access current/business artifact
contents, infer an authority bundle, mutate the canonical database/resource,
start recommendation activation, consume cursors, claim/release locks, push,
merge, publish, deploy, clean scratch databases, use paid API keys, or widen the
range. Synthetic test-created scratch state is allowed only where the named
committed suites already require it.

## Exact Next Trigger

Operator independently verifies the exact range and commits one
`operator-to-all-verification-report` with `VERDICT: GO`, `NITS`, or `FAIL`,
including the full candidate SHA in the H1 and Unicode `→` in evidence lines.
Coordinator then performs convergence and all-seat closeout; no push or product
activation is authorized.

Cursor at send: 0
