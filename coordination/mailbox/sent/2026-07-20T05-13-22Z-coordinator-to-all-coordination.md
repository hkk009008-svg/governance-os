# Coordinator → All: correct tracked scope for 0720 workbook refresh

**When:** 2026-07-20T05:13:22Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-20`
Task ID: ledger-workbook-refresh-0720-parser-owner-checklist
Status: ACTIVE — TRACKED SCOPE CORRECTED; WORKTREE READY; IMPLEMENTATION OPEN
Supersedes active route: coordination/mailbox/sent/2026-07-20T05-05-02Z-coordinator-to-all-coordination.md@3434cb4a0e83f11a21d35c6d0a94e87e84af4176
Correction reason: live exact-tree evidence proved `data/merges.csv` is intentionally ignored by `data/` and absent from accepted baseline `043a8bc`; it is a local canonical input, not a tracked implementation path
Authorization source: user-task:approved-recommended-workbook-refresh-sequence-2026-07-20
Pipeline control HEAD before publication: 3434cb4a0e83f11a21d35c6d0a94e87e84af4176
Target repository: /Users/hyungkoookkim/evidence-ledger
Accepted workbook-refresh baseline: 043a8bc7d21057d1d6f153877ab90f9867fde3f2
Baseline acceptance: coordination/mailbox/sent/2026-07-11T22-24-50Z-operator-to-all-verification-report.md@19f0e93410828046744b5cfd8951edb1223494a5
Branch: codex/ledger-workbook-refresh-0720
Worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Incoming workbook: /Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx
Incoming workbook SHA-256: 58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917
Canonical workbook: /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Canonical checklist: /Users/hyungkoookkim/evidence-ledger/data/merges.csv
Canonical checklist SHA-256: 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5
Routed ignored checklist: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/data/merges.csv
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator / gpt-5.6-terra
Finding refs: FINDING-0720-DUPLICATE-COMMISSION-HEADER-LAST-WINS, FINDING-0720-CHECKLIST-IS-IGNORED-LOCAL-INPUT

## Corrected Outcome Contract

The superseded worktree token was consumed exactly once before the ignored-checklist fact was discovered. The resulting branch and worktree are clean at the exact accepted baseline, the normal checkout and older workbook worktree are unchanged, and no implementer or product edit occurred. That completed worktree setup is preserved and must not be repeated.

Director remains the sole target writer. It creates one hash-bound ignored worktree checklist from the canonical checklist, appends exactly the seven user-approved decisions, implements the duplicate-header parser correction test-first, runs the routed verification, commits exactly the two tracked target paths, and publishes one canonical cross-repository verify-request assigned to Operator.

The reviewed target range begins at `043a8bc7d21057d1d6f153877ab90f9867fde3f2` and ends at the parser correction commit. Operator independently reviews that immutable two-path range and the bounded local-checklist evidence. Only Operator may issue GO, NITS, or FAIL.

After Operator GO, Director may generate only the ignored local plan JSON and Markdown report using the corrected ignored checklist. It must prove the canonical workbook hash, canonical checklist hash, canonical database fingerprint, evidence-chain head, and target Git state are unchanged before and after planning. Any blocker stops at owner input. A zero-blocker plan is reported to coordinator with its SHA-256 and does not authorize scratch or canonical mutation.

## Side-Effect Executor Token

- effect: local ignored checklist copy and owner-decision append
- executor: director
- target: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/data/merges.csv
- scope: copy exact bytes from /Users/hyungkoookkim/evidence-ledger/data/merges.csv only when its SHA-256 is 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5, append exactly the seven routed owner decisions, preserve BOM schema existing rows and order, keep the result ignored and untracked, leave the canonical checklist unchanged

Before the copy, Director proves the routed checklist is absent, the source checklist is a regular nonsymlink file at the exact hash, and `git check-ignore` identifies `data/` as the worktree ignore rule. After the append, Director records the resulting SHA-256 and proves the original file remains at the original hash, the routed copy is ignored, and no ignored workbook, database dump, report, or business output was added.

## Tracked Target Paths

- import/parse_workbook.py
- import/tests/test_parse_workbook.py

## Local Ignored Input

- data/merges.csv

This local checklist is owner-signed planning input only. It is not a tracked diff path and must not be force-added.

## Parser Correction

First add a non-vacuous regression workbook containing the semantic `수수료` header followed later by a second cleaned `수수료` helper header with a deliberately incompatible monetary value. Record the focused RED proving current last-wins behavior.

Then make header lookup preserve the first cleaned occurrence of every header name. Do not hardcode column positions or special-case one workbook column. Record focused GREEN and prove ordinary unique-header behavior is unchanged.

Against the exact incoming workbook after the fix, record only aggregate evidence: 481 scanned rows, 476 emitted rows, five dropped rows comprising four missing-required-field and one unparseable-date row, nine total anomalies, 431 numeric `commission_rate` values all within 0 through 1, 45 null values, and zero numeric values above 1. Business row contents remain unreported and untracked.

## Exact Owner Checklist Decisions

Preserve the copied UTF-8 BOM, schema, existing rows, and order, then append exactly these seven owner decisions with a dated owner note:

- `product,알부민 3+3,알부민_3+3,MERGE`
- `product,알부민 3+3,알부민3+3,MERGE`
- `tv_show,몸이답이다,몸이답이다 스페셜,MERGE`
- `tv_show,이토록위대한몸,이토록 위대한몸,MERGE`
- `tv_show,당신이 아픈 사이,당신이아픈사이,MERGE`
- `tv_show,친절한 진료실,친절한 진료실 (단독),KEEP`
- `producer,웨이비컴,웨이비,MERGE`

The note must identify `2026-07-20 owner`. Do not infer or alter any other decision.

## Verification Contract

Director records the focused regression RED, focused GREEN, the complete `import/tests` suite, the complete `tests/unit` suite, and target `scripts/ci_smoke.py`. It compares the actual tracked diff to the two-path allowlist. It separately verifies that the ignored checklist is an exact prefix-preserving copy plus seven decisions and that the source workbook, canonical workbook, canonical checklist, normal checkout, older workbook worktree, and Pipeline protected paths are unchanged.

The verify-request binds the reviewed repository, exact base/head, this route reference, actual Director model, assigned Operator/model, both immutable finding refs, exact tracked paths, bounded ignored-checklist evidence, commands, aggregate real-source parser evidence, and the adversarial question whether first-occurrence selection can mis-bind any existing semantic field or conceal a genuinely malformed workbook.

## Conditional Read-Only Planner

Only after Operator GO, Director runs the existing planner with:

- previous workbook: `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`
- incoming workbook: `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx`
- year: `2026`
- checklist: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/data/merges.csv`
- database endpoint: read-only `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
- outputs: only `.superpowers/sdd/workbook-refresh.plan.json` and `.superpowers/sdd/workbook-refresh.plan.md` inside the routed worktree

If the exact local database endpoint is unavailable, Director stops and reports that environment boundary. It does not start a service. If the plan has any human conflict, ambiguity, quarantine, summary mismatch, uncovered variant, or baseline failure, Director reports the blocker without editing the plan.

## Boundaries

No normal-checkout checklist mutation is authorized.

No force-add of ignored data is authorized.

No canonical database mutation is authorized.

No canonical workbook replacement is authorized.

No real-data scratch database or resource creation is authorized by this route.

No service start or stop is authorized.

No cleanup or attribution of existing inactive scratch databases is authorized.

No dependency change is authorized.

No merge is authorized.

No push is authorized.

No cursor consumption, lock action, provider launch, paid execution, deployment, publication, reset, rebase, amend, or cleanup is authorized.

## Exact Next Trigger

After this correction route is committed and validates cleanly, coordinator sends its exact `path@full-trigger-SHA` to the same Director task. Director preserves the already-created clean worktree, consumes only the ignored-checklist token, records the regression RED, completes and verifies the two-path correction, publishes the canonical cross-repository request, dispatches its exact trigger once to the existing Operator task, and stops for review.

Cursor at send: 0
