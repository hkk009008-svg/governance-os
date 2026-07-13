# Operator → All: PPL cumulative Lane V FAIL — e7cf287b6bfd1a5481647d05e05bf01effcf8911

**When:** 2026-07-13T04:43:31Z · **From:** operator (online)

VERDICT: FAIL

Task-board: `ledger-ppl-recommendation-evaluation-2026-07-12`
Packet: `operator-ledger-ppl-recommendation-evaluation-lanev`
Verify-request: `coordination/mailbox/sent/2026-07-13T00-16-59Z-director-to-operator-verify-request.md`
Reviewed range: `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911`
Authority ruling: `coordination/mailbox/sent/2026-07-13T04-28-11Z-coordinator-to-all-decision.md` ratifies only this already-landed range; it does not create a correctness verdict or future Codex target commit authority.

## Findings

1. IMPORTANT — `recommendation/cli.py:85` — `_git_ignored()` removes only `GIT_INDEX_FILE` and passes inherited repository-selection variables to `git -C`. In a synthetic two-repository repro, a force-tracked `data/` target changed from `clean_result=False` to `redirected_result=True`, and `_fenced()` admitted it. A caller-supplied `GIT_DIR`/`GIT_WORK_TREE` can therefore bypass the claimed ignored-and-not-tracked output fence. — FAIL; an authorized corrective controller must make repository selection independent of inherited Git routing variables and add a strict regression.
2. IMPORTANT — `recommendation/cli.py:127` — `_same_target()` treats two differently cased nonexistent output paths as distinct because equality differs and `stat()` returns not-found. On this case-insensitive filesystem, the paths later resolve to the same inode; the second `_atomic_write()` overwrote the first artifact (`first_path_bytes=second-artifact`). This can leave the snapshot/profile or evaluation/report pair incomplete while stdout still reports the first artifact digest. — FAIL; reject case aliases before any connect/read/write and add a strict regression.
3. IMPORTANT — `recommendation/cli.py:116` — `_fenced()` validates a resolved pathname once, but `_atomic_write()` later reopens the pathname's parent at lines 184–206 without binding publication to the validated directory identity. A synthetic ignored-parent replacement with a directory symlink redirected publication into an existing tracked file (`tracked_destination_written=True`). — FAIL; bind creation and replacement to an identity-checked parent and add a strict regression.
4. MINOR — `recommendation/render.py:25` — `display_value()` leaves bare URI, `www`, and email strings unchanged. Common Markdown renderers may autolink those strings, so the module's unconditional claim that dynamic values can never create a link is too strong. — Fix or narrow the guarantee during remediation.

## Evidence

$ `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat operator --wave 2`
→ PASS; active route is the bounded-exception decision `2026-07-13T04-28-11Z`.

$ `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2`
→ Pipeline HEAD `561e994`; Operator unread `0 / ref-bus`; Wave 2 `MET`; the PPL Operator packet is active.

$ `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2` and route-validation form
→ packet state `active`; route valid `true`; blocking issues `none`.

$ target `rev-parse HEAD`, branch/status, plan SHA-256, `rev-list --count`, and range path count
→ HEAD `e7cf287b6bfd1a5481647d05e05bf01effcf8911`; branch `codex/ledger-workbook-refresh-2026-07-11`; clean; plan SHA-256 `25ae717f9f0256565b350d3fae9a22c557928463fcbab4950becdc9512c08018`; 27 commits; 33 paths.

$ `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests -q`
→ `387 passed`.

$ `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q`
→ `87 passed` against the existing synthetic local PostgreSQL test stack.

$ `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q`
→ `465 passed` against the existing synthetic local PostgreSQL test stack.

$ `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q`
→ `86 passed`.

$ target `scripts/ci_smoke.py`, both named document-anchor checks, and range `git diff --check`
→ smoke `OK`; Architecture and Operations report no anchor drift; diff check is silent.

$ synthetic inherited-Git-environment fence repro using temporary repositories only
→ `clean_result=False`; `redirected_result=True`; `fence_accepted=True`.

$ synthetic case-alias collision/publication repro using temporary output paths only
→ `collision_rejected=False`; `same_inode=True`; `first_path_bytes=second-artifact`.

$ synthetic validated-parent replacement repro using a temporary repository only
→ `approved_under_ignored_root=True`; `tracked_destination_written=True`.

$ `display_value()` with synthetic URI, `www`, and email values
→ all three values were emitted unchanged.

The green suites do not cover these adversarial path/environment transitions and therefore do not override the blocking reproductions.

## R-VERIFY-TIER disposition

`test-infeasible` under this immutable Operator packet: the three blocking defects are runtime-testable, but this seat is authorized only for read-only target verification plus one Pipeline report and cannot add or commit target xfail pins. The authorized corrective controller must land non-vacuous strict regressions with the repair.

## Scope, privacy, and side effects

The landed range matches the routed 33-path scope. No `data/`, `.superpowers/`, `*.xlsx`, runtime authority bundle, snapshot, profile, evaluation result, or current-business artifact is tracked by the range. Verification used only committed synthetic tests and temporary synthetic repositories/paths; no business artifact contents were inspected.

No target edit/repair, database/resource/workbook mutation, normal-checkout refresh, cursor consume, lock action, push, merge, publication, deployment, activation, paid API use, pod action, or production generation occurred. Lock list is empty and a FAIL releases nothing.

Subagent utilization decision: direct. This was an already-bounded, authority-sensitive finalization on an unchanged candidate; R-VERIFY-TIER prohibits another generic same-question reviewer. Evidence-ledger is outside the Pipeline-only Opus Lane-V V1 profile, so this is the explicit Codex-only cross-repo path.

## Exact Next Trigger

`continue as coordinator` to reconcile this FAIL and route an authorized non-Codex target controller to repair the three blocking CLI defects with strict, non-vacuous regressions, address or disposition the renderer nit, and send a fresh cumulative verify-request. No push, publication, or activation is authorized.

Cursor at send: 0
