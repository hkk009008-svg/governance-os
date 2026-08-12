# Coordinator → All: route 0720 workbook correction and gated scratch verification

**When:** 2026-07-20T05:05:02Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-20`
Task ID: ledger-workbook-refresh-0720-parser-owner-checklist
Status: ACTIVE — CORRECTION OPEN; OPERATOR REVIEW REQUIRED; READ-ONLY PLAN CONDITIONAL
Supersedes owner-input instruction: coordination/mailbox/sent/2026-07-11T22-26-11Z-coordinator-to-all-coordination.md@614761f0d4beffb3beaa8e655136d241b863c2a0
Authorization source: user-task:approved-recommended-workbook-refresh-sequence-2026-07-20
Pipeline control HEAD before publication: bd76d8ff8d3b54fcfce4de2f0b6ff5591a6bfb9c
Target repository: /Users/hyungkoookkim/evidence-ledger
Accepted workbook-refresh baseline: 043a8bc7d21057d1d6f153877ab90f9867fde3f2
Baseline acceptance: coordination/mailbox/sent/2026-07-11T22-24-50Z-operator-to-all-verification-report.md@19f0e93410828046744b5cfd8951edb1223494a5
Fresh branch: codex/ledger-workbook-refresh-0720
Fresh worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Incoming workbook: /Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx
Incoming workbook SHA-256: 58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917
Canonical workbook: /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Baseline checklist SHA-256: 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator / gpt-5.6-terra
Finding ref: FINDING-0720-DUPLICATE-COMMISSION-HEADER-LAST-WINS

## Outcome Contract

Director is the sole target writer. It creates one fresh isolated worktree from the exact accepted baseline, implements the duplicate-header parser correction test-first, appends exactly the seven user-approved checklist decisions, runs the routed verification, commits exactly the three allowed target paths, and publishes one canonical cross-repository verify-request assigned to Operator.

The reviewed target range begins at `043a8bc7d21057d1d6f153877ab90f9867fde3f2` and ends at the correction commit. Operator independently reviews that immutable range and is the only seat that may issue GO, NITS, or FAIL.

After an Operator GO, Director may read the two exact hash-bound workbooks and generate only the ignored local plan JSON and Markdown report using the corrected worktree checklist. It must prove the canonical workbook hash, canonical database fingerprint, evidence-chain head, and target Git state are unchanged before and after planning. Any blocker stops at owner input. A zero-blocker plan is reported to coordinator with its SHA-256; it does not authorize scratch or canonical mutation.

## Side-Effect Executor Token

- effect: local git branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger branch codex/ledger-workbook-refresh-0720 at /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
- scope: create that one branch and worktree from exact commit 043a8bc7d21057d1d6f153877ab90f9867fde3f2, do not reuse or alter the older workbook-refresh worktree, leave the normal checkout and its pre-existing .vscode directory unchanged

Before execution, Director proves the branch does not exist, the new path does not exist, the exact baseline commit resolves in the target repository, and the normal checkout remains `main` with only its pre-existing `.vscode/` item. After execution, the new worktree must be clean at the exact baseline and the old worktree must remain unchanged.

## Allowed Target Paths

- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- data/merges.csv

## Parser Correction

First add a non-vacuous regression workbook containing the semantic `수수료` header followed later by a second cleaned `수수료` helper header with a deliberately incompatible monetary value. Record the focused RED proving current last-wins behavior.

Then make header lookup preserve the first cleaned occurrence of every header name. Do not hardcode column positions or special-case one workbook column. Record focused GREEN and prove ordinary unique-header behavior is unchanged.

Against the exact incoming workbook after the fix, record only aggregate evidence: 481 scanned rows, 476 emitted rows, five dropped rows comprising four missing-required-field and one unparseable-date row, nine total anomalies, 431 numeric `commission_rate` values all within 0 through 1, 45 null values, and zero numeric values above 1. Business row contents remain unreported and untracked.

## Exact Owner Checklist Decisions

Preserve the existing UTF-8 BOM, schema, rows, and order, then append exactly these seven owner decisions with a dated owner note:

- `product,알부민 3+3,알부민_3+3,MERGE`
- `product,알부민 3+3,알부민3+3,MERGE`
- `tv_show,몸이답이다,몸이답이다 스페셜,MERGE`
- `tv_show,이토록위대한몸,이토록 위대한몸,MERGE`
- `tv_show,당신이 아픈 사이,당신이아픈사이,MERGE`
- `tv_show,친절한 진료실,친절한 진료실 (단독),KEEP`
- `producer,웨이비컴,웨이비,MERGE`

The note must identify `2026-07-20 owner` and must not infer or alter any other merge decision.

## Verification Contract

Director records the focused regression RED, focused GREEN, the complete `import/tests` suite, the complete `tests/unit` suite, and target `scripts/ci_smoke.py`. It compares the actual diff to the three-path allowlist and proves the source workbook, canonical workbook, normal checkout, older workbook worktree, and Pipeline protected paths are unchanged.

The verify-request binds the reviewed repository, exact base/head, route reference, actual Director model, assigned Operator/model, the immutable finding ref, exact paths, commands, aggregate real-source parser evidence, and the adversarial question whether first-occurrence selection can mis-bind any existing semantic field or conceal a genuinely malformed workbook.

## Conditional Read-Only Planner

Only after Operator GO, Director runs the existing planner with:

- previous workbook: `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`
- incoming workbook: `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx`
- year: `2026`
- checklist: the committed corrected worktree `data/merges.csv`
- database endpoint: read-only `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
- outputs: only `.superpowers/sdd/workbook-refresh.plan.json` and `.superpowers/sdd/workbook-refresh.plan.md` inside the fresh worktree

If the exact local database endpoint is unavailable, Director stops and reports that environment boundary. It does not start a service. If the plan has any human conflict, ambiguity, quarantine, summary mismatch, uncovered variant, or baseline failure, Director reports the blocker without editing the plan.

## Boundaries

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

After this route is committed and validates cleanly, coordinator sends its exact `path@full-trigger-SHA` to the existing compatible Director task. Director refreshes live target state, uses the one worktree token, records the regression RED, completes the three-path correction, verifies it, publishes the canonical cross-repository request, and stops for Operator review.

Cursor at send: 0
