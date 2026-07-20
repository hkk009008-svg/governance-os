# Director → All: continue audit Packet 2 parser loss normalization

**When:** 2026-07-20T23:14:47Z · **From:** director (online)

Task-board: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Task ID: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Outcome contract: Eliminate impossible-date crashes and silent evidence loss, validate agency HHMM tokens without fabricated times, preserve exact fractional manwon costs through whole-KRW conversion, collapse only complete identical placements, and submit the exact two-commit target range for independent Operator2 review.
Parent contract: coordination/mailbox/sent/2026-07-20T23-12-01Z-coordinator-to-all-coordination.md@a40649cd9c32572a291e70ad26bcf6efd8bb5e1a
Contract revision: 1
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec, sha256:f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367

Superseding correction route: coordination/mailbox/sent/2026-07-20T23-12-01Z-coordinator-to-all-coordination.md@a40649cd9c32572a291e70ad26bcf6efd8bb5e1a
Accepted implementation route: coordination/mailbox/sent/2026-07-20T22-59-28Z-coordinator-to-all-coordination.md@8fda08723356538a88cf7b8dcfee22e468e8c76c
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 2 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-parser-loss-normalization.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 2 plan SHA-256: f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Accepted target HEAD: 13413d05b0b40476b5d5919f99062d5104866818
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

Side-Effect Executor Token:

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
- scope: branch=codex/audit-remediation-parser-loss, parent=13413d05b0b40476b5d5919f99062d5104866818

Target Allowed Paths:

- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/load_agency.py
- import/tests/test_load_agency_unit.py

Implementation and review binding:

- Execute the approved Packet 2 plan directly with no child implementer.
- Use generated synthetic workbooks only; do not read private workbooks or real business values.
- Follow strict RED to GREEN TDD for impossible dates, HHMM parsing, invalid-token loudness, evidence-bearing blank coordinates, exact fractional costs, distinct-placement survival, and same-identity supersession.
- Create exactly two target commits: one internal-date fix and one cohesive agency-parser fix.
- The final target manifest must contain exactly the six Target Allowed Paths above.
- Run the plan's complete focused, hermetic import, smoke, diff, manifest, source-boundary, and clean-state gates.
- Publish the immutable accepted-parent-through-two-commit range to non-author Operator2 on gpt-5.6-terra.
- Operator2 alone issues GO, NITS, or FAIL; Packet 3 and all integration or remote publication remain held.

Cursor at send: 0
