# Operator → Director: NITS: Codex-Claude exclusive release 12cfc6e

**When:** 2026-08-14T00:59:23Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-08-14T00-45-07Z-director-to-operator-verify-request.md@66280194f201a34d9e120897c875bfe20d342efb
Reviewed head: 12cfc6ea92a3a17ac0c663defc0cfc1c431abd55
Reviewed base: b6bb3bdb1a04832f9e1aa29f83c610837a36c817
Reviewer seat: operator
Reviewer model: claude-opus-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: exact-range git reads; the committed head checked out into a disposable linked worktree that deliberately carries no .venv, so the range's own interpreter contract was exercised rather than bypassed; every abuse-class row run as a negative plus positive control pair; full unit suite and governance verification executed through the range's documented command form, with both the governance gate and the guide-integrity guard validated by perturbation before their results were trusted.
Verification context: Pipeline-local range, 1 commit, 48 files, +5960/-169. The reviewer authored none of the range. scripts/claude_task_connector.py at this head is blob 27de6c7a1d635033283735b181a326d319b8da5d, byte-identical to the head of the separately reviewed b6bb3bd..f0990db range, so the connector controls were re-run here rather than carried forward on assertion.

## Allowed Paths

- The request declares no path restriction; this section is advisory context only. The observed range touches 48 paths under scripts/, tests/unit/, docs/, coordination/bin/, config/, threeway/, .claude/, .agents/, and repository-root instruction surfaces.

## Findings

NIT - CLAUDE.md:10-16. The interpreter bullet compresses a conditional,
permission-classifier-dependent observation into an absolute mechanism claim:
"Claude's Bash tool refuses `env` once a dash-prefixed token follows the variable
list, so the prefixed form is unrunnable as soon as the command takes options."
The strict reading is falsified by direct measurement in this review session:
`env -u GIT_INDEX_FILE <interpreter> -c "print(...)"` and
`env -u GIT_INDEX_FILE <interpreter> -m pytest <path> -q` both ran to completion,
exit 0, with dash-prefixed tokens following the variable list. The range's own
mechanizing test states the accurate version in
tests/unit/test_claude_seat_launcher.py:148-171 - "the prefix is not broken, it
is *conditionally* broken", the ban is narrow and covers only `env` wrapped
directly around the interpreter, and ordinary Git keeps its prefix "which is
verified to run". CLAUDE.md's neighbouring sentence does keep the Git prefix, so
the file is internally consistent under the scoped reading; what is wrong is only
the absolute wording, which a reader cannot scope without opening the test.

This is doctrine prose that overstates its own evidence, not a control defect,
and it is deliberately recorded rather than waived because this repository
mechanizes doctrine and treats a false mechanism claim as a defect class in its
own right. The mechanized guard is sound and I am not asking for it to change:
banning the form outright is correct precisely because the refusal is
conditional, the ban is narrow, the evasion-normalization control at
tests/unit/test_claude_seat_launcher.py:247-257 is real, and the rule's stated
rationale - an unconditional `unset` line gives the same isolation without
depending on the condition - holds independently of whether any given invocation
is refused. Remedy is one sentence in CLAUDE.md matching the test's wording. Not
blocking; no abuse-class row depends on it.

## Finding Refs

- sha256:6e9a6b784cecab307fb55ddd76ec825278338d1dcdebe4d7e1fb20f1f4007541

## Finding Dispositions

- sha256:6e9a6b784cecab307fb55ddd76ec825278338d1dcdebe4d7e1fb20f1f4007541: addressed

## Evidence

$ git diff b6bb3bdb1a04832f9e1aa29f83c610837a36c817..12cfc6ea92a3a17ac0c663defc0cfc1c431abd55 | shasum -a 256
→ 6e9a6b784cecab307fb55ddd76ec825278338d1dcdebe4d7e1fb20f1f4007541  - (equals the request's finding ref exactly)

$ git log --oneline b6bb3bd..12cfc6e
→ 12cfc6e feat(protocol): make Pipeline Codex-Claude exclusive (single commit)

$ git rev-parse 12cfc6e:scripts/claude_task_connector.py f0990db:scripts/claude_task_connector.py
→ both 27de6c7a1d635033283735b181a326d319b8da5d; the connector is unchanged from the separately reviewed range

ROW 1 - retired provider surfaces cannot re-enter
$ grep -rniE "antigravity|cursor_mailbox|cursor_land_gate|AGY_|CURSOR_" scripts .agents .claude config coordination/bin threeway AGENTS.md CLAUDE.md
→ zero adapter, path, or instruction hits; every match is generic mailbox-transport vocabulary (_normalize_cursor, cursor_seq, refs/threeway/cursors/<seat>, _ISO_CURSOR_RE), which is exactly the carve-out this row preserves. The grep's own false positives are the evidence that generic cursor vocabulary survives.
$ CURRENT_REVIEW_FAMILIES and models_are_current_review_pair at this head
→ active families ['claude', 'gpt']; gpt-5/claude-opus-5 True; gpt-5/gemini-3.6-flash-high False; gpt-5/xai-grok-4.5 False; model_family still resolves 'grok-4.5' and 'gemini-3.1-pro-high' for historical parsing only

ROW 2 - bounded supported SDK surface
$ build_sdk_options at this head
→ tools and allowed_tools ['ListAgents','SendMessage']; 13 disallowed tools; mcp_servers {} with strict_mcp_config True; setting_sources []; skills []; pinned name via extra_args; cwd, runtime and model validated in BridgeConfig
$ _validate_target('local_deadbeef')
→ rejected: private Desktop task IDs cannot be targeted

ROW 3 - ambiguity, timeout, budget, duplicates, late hooks fail closed
$ _listed_addresses on a live listing containing two Remote Control offline rows
→ offline rows excluded; three live addresses returned
$ _resolve_listed_target with own_name set to the bridge's own name
→ None (self refused); prefix 'pipeline-a' still returns 'pipeline-a7 [8775be]' (positive control resolves)
$ _resolve_listed_target(target_prefix='pipeline-') against four live pipeline rows
→ None (ambiguity refused)
$ collection path with two peers sharing one display name
→ None (duplicate refused)
$ BridgeConfig max_budget_usd of 0, negative, 1e9, and inf
→ all four rejected; the ceiling is finite and bounded
$ inspection of _schedule and send at this head
→ TimeoutError and post-schedule failure set state=error with an explicit quarantine message so late native hooks can never be attributed to a later operation; failed_to_schedule clears only its own arm and pops its receipt; send fails closed when len(_sent)+len(_discoveries) reaches queue_limit

ROW 4 - attribution dedupes without suppressing distinct messages
$ _accept_peer_message with a repeated ID and identical text, then a distinct ID, then a conflicting payload
→ True then False for the exact repeat; True for the distinct ID, so distinct messages are not suppressed; the conflicting reuse raises "native peer message ID was reused with a different attributed payload"
$ capability_report()
→ governance_authority 'none'; delivery_ack 'not_available'; delivery_ack is False at every receipt surface and submission status is queued_to_bridge, never delivered

ROW 5 - instructions runnable in linked worktrees; proportionality without weakening admission
$ git worktree add --detach <tmp> 12cfc6e; ls -d .venv
→ "No such file or directory" - the disposable worktree reproduces the trap the range documents
$ unset GIT_INDEX_FILE; coordination/bin/pipeline-python -c "import sys,pytest; print(sys.executable, pytest.__version__)"
→ /Users/hyungkoookkim/Pipeline/.venv/bin/python, pytest 9.1.1, exit 0 - the documented form resolves the primary interpreter from a .venv-less linked worktree
$ instrument validation of the guide-integrity guard: appended a line naming coordination/bin/does-not-exist-anywhere to CLAUDE.md, ran the guard, restored
→ FAILED test_claude_guides_only_name_programs_that_exist_on_this_branch (1 failed, 6 passed); after restore 7 passed and the worktree was clean, so the runnability guard is non-vacuous
$ AGENTS.md and CLAUDE.md proportionality clauses in the range
→ both preserve "run one final review and full verification pass" and condition the exception on explicit user request or genuine implementation need; high-risk admission is unchanged and independently confirmed above by the retired-family rejections

$ unset GIT_INDEX_FILE; coordination/bin/pipeline-python -m pytest tests/unit -q   (at 12cfc6e, disposable linked worktree)
→ 1725 passed in 208.91s

$ unset GIT_INDEX_FILE; coordination/bin/pipeline-python scripts/governance_verify_all.py   (at 12cfc6e)
→ exit 0; GO-SCHEMA CHECK PASS with 182 verification-reports validated; PLACEHOLDER, MECHANISM-LEDGER and ARCH-FRESHNESS all PASS

$ instrument validation before trusting that exit 0: one committed verification-report perturbed with an invalid Risk class line, gate re-run, then restored
→ exit 1; after restoring the file the worktree was clean, so the gate can fail rather than being a control that cannot

$ prior review's NIT re-checked at this head
→ closed. docs/protocol/claude/continuation.md:51-56 now reads that the CLI "was 2.1.220 at the 2026-08-09 audit and 2.1.231 when re-observed on 2026-08-14, so the floor is met", and instructs re-reading `claude --version` rather than trusting either figure; this is consistent with docs/protocol/app-quickstart.md:122-126

$ model-family admission for this pair
→ author gpt-5 is family gpt, reviewer claude-opus-5 is family claude; distinct families, both inside the currently admitted set, and reviewer seat operator differs from author seat director

Cursor at send: 2026-08-01T03:33:15Z
