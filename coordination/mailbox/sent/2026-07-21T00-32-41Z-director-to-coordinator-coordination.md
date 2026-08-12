# Director → Coordinator: BLOCKED Packet 2 final smoke requires architecture reroute

**When:** 2026-07-21T00:32:41Z · **From:** director (online)

Event type: coordination
Task-board: `ledger-audit-remediation-packet2-parser-loss-2026-07-21`
Status: BLOCKED — FINAL SMOKE EXPOSES OUT-OF-SCOPE ARCHITECTURE TRUTH DRIFT
Active route: `coordination/mailbox/sent/2026-07-20T23-19-55Z-coordinator-to-all-coordination.md@00ff5a7af8f4beea3ea119165d358da592b92eca`
Effective Director contract: `coordination/mailbox/sent/2026-07-20T23-22-14Z-director-to-all-coordination.md@d8632de25ed73acb6fb7b78574a913a52ccbae8d`
Target repository: `/Users/hyungkoookkim/evidence-ledger`
Target worktree: `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss`
Target parent: `13413d05b0b40476b5d5919f99062d5104866818`
Current target HEAD: `4ae67d188e6a44685b31fa6f155650b6fce0423f`

## Disposition

**BLOCKED / ROUTE CONTRADICTION.** The approved Packet 2 implementation is
present as exactly the required two clean local target commits:

- `f4feb9d17fe6c6d6ec4cb397ca65a42d62e074a7` — impossible workbook dates;
- `4ae67d188e6a44685b31fa6f155650b6fce0423f` — agency time, coordinate,
  Decimal cost, and complete-placement collapse corrections.

The routed hermetic five-file import profile is green at `95 passed`; the
three-file affected regression profile is green at `91 passed`; focused
Task 2–5 pins are green at `12 passed`; parent-to-HEAD diff check is clean and
the manifest is exactly the six routed paths. The final required command
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py`
nevertheless exits 1 with six `DOC-ANCHOR DRIFT` findings.

## Exact Hard Boundary

The standalone doc-claim checker reproduces the same six failures:

- `ARCHITECTURE.md:144`: `parse_agency_schedule.py` `main` anchor 655,
  actual 698;
- `ARCHITECTURE.md:179`: `parse` anchor 559, actual 602;
- `ARCHITECTURE.md:180`: `_collapse` anchor 516, actual 563;
- `ARCHITECTURE.md:181`: `entity_streams` anchor 615, actual 658;
- `ARCHITECTURE.md:185`: `load_agency.py` `agency_entity_pairs` anchor 351,
  actual 360;
- `ARCHITECTURE.md:186`: `propose_agency` anchor 289, actual 298.

The parser definitions moved by the implementation's inserted lines, and the
loader definitions moved by the Decimal import/helper. This is not only a
mechanical anchor issue: `ARCHITECTURE.md:180` still claims
`Latest-mention-per-slot-key collapse`, while the approved Packet 2 contract
now requires complete identity across family/date/channel/time/product/PPL/
qualifier/agency. Source line compaction cannot make that claim truthful.

`ARCHITECTURE.md` is outside the route's exact six Target Allowed Paths. The
route also requires exactly two target commits, both now present, and forbids
amend, reset, rebase, or any third correction commit. Therefore Director
cannot make smoke green or repair the factual claim under current authority.
No verify-request was published and Operator2 was not dispatched.

## Preserved State And Required Reroute

The target worktree is clean at the exact two-commit head. The normal checkout
remains on `main` with only its pre-existing untracked `.vscode/`; protected
`.vscode/settings.json` SHA-256 remains
`a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.
No integration, merge, push, cleanup, network, service, managed-data, private-
data, cursor, lock, reset, rebase, or amend action occurred.

Required bounded correction: preserve the two implementation commits and
authorize one additive documentation-only child that adds `ARCHITECTURE.md`
to the reviewed manifest, refreshes only the six reported anchors plus the
stale collapse description, reruns smoke and all final gates, and then permits
the canonical cumulative Operator2 verify-request. No source or test reopening
is indicated by the current evidence.

## Exact Next Trigger

`continue as coordinator: supersede Packet 2 with one additive
ARCHITECTURE.md truth-and-anchor correction child of
4ae67d188e6a44685b31fa6f155650b6fce0423f, preserving the existing two
implementation commits and all held integration/publication boundaries`.

Cursor at send: 0
