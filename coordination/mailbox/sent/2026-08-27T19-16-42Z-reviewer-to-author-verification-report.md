# Reviewer → Author: cumulative desktop-team integration exact-range review

**When:** 2026-08-27T19:16:42Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-27T18-29-55Z-author-to-reviewer-verify-request.md@2d4159e51eb950100c2448ee461fdcd3c2e47948
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewed head: fb7e87000bebb72d4eaf0b3d03fa2f8675058a29
Reviewer seat: reviewer
Reviewer model: claude-opus-4-7
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR — tests/unit/test_provider_surface_map.py:20-31 pins the three exact peer paths (peer.py, peer_backends.py, peer_receipt.py) but has no wildcard glob for pipeline/peer_*.py or pipeline/*_peer.py. A renamed variant such as pipeline/peer_v2.py or pipeline/prov_peer.py would slip past the three-exact-name check. Because c1f2ac88 removed every consumer (no reader, no CLI verb, no test import) the class is UNREACHABLE regardless — this is a defense-in-depth observation on the surface-map guard, not a live route.

MINOR — Doc drift carried forward from prior reports. TRANSFER-MANIFEST.md:68, DECISIONS.md:195/196/215, and several docs/superpowers/plans/*.md still describe removed peer/seat surfaces as live. coordination/peer/{cli-exclusive-overhaul,guard-evasion,guard-v7}/*.json contain six historical receipt blobs with no live reader. No runtime effect; documentation debt.

## Finding Refs

- coordination/mailbox/sent/2026-08-21T22-12-09Z-reviewer-to-author-verification-report.md@1b37caf84372e3f5ebb4d30fe16c38f2da704e17
- coordination/mailbox/sent/2026-08-27T14-51-44Z-reviewer-to-author-verification-report.md@d84a9b3cfade5521f1dc6c85614a36f28dcf92f7
- coordination/mailbox/sent/2026-08-27T15-21-24Z-reviewer-to-author-verification-report.md@fb7e87000bebb72d4eaf0b3d03fa2f8675058a29

## Finding Dispositions

- coordination/mailbox/sent/2026-08-21T22-12-09Z-reviewer-to-author-verification-report.md@1b37caf84372e3f5ebb4d30fe16c38f2da704e17: addressed
- coordination/mailbox/sent/2026-08-27T14-51-44Z-reviewer-to-author-verification-report.md@d84a9b3cfade5521f1dc6c85614a36f28dcf92f7: addressed
- coordination/mailbox/sent/2026-08-27T15-21-24Z-reviewer-to-author-verification-report.md@fb7e87000bebb72d4eaf0b3d03fa2f8675058a29: addressed

## Evidence

$ git rev-list --count 86146d1f..fb7e8700
→ 34 commits inspected commit-by-commit rather than only the net diff. Diff shape: 325 files changed, +12796/-33426 (net -20630 Python lines).

$ Individual-commit inspection of the historical peer-remediation chain
→ First FAIL 2026-08-21T16-55-18Z@4dfb4b1c raised 8 blocking findings on the CLI-exclusive overhaul at 4c4371fd. Second FAIL 2026-08-21T22-12-09Z@1b37caf8 supersededit and identified four unresolved-hard-boundary CLASSES (F1 ignored-skill shadowing, F3 retired-event delete/reintroduction laundering, F4 symlink escape in peer result, F6 symlink+concurrency escape in peer receipts) plus new findings (argv/spend authority, EOF-whitespace NIT). Commit 2a19e4ff addressed each class in-place. Commit c1f2ac88 then removed peer.py, peer_backends.py, peer_receipt.py, all their tests, and the `pipeline peer` CLI verb — eliminating F4/F6/argv/spend at the mechanism level.

$ git ls-files pipeline/peer.py pipeline/peer_backends.py pipeline/peer_receipt.py
→ (empty). Confirmed absent at fb7e8700; also no pipeline/peer_*.py or pipeline/*_peer.py; also no coordination/bin/peer* or *-peer* shell shim. Independent subagent sweep found zero live-code references to receipt_root/receipts_dir/write_receipt/next_seq under pipeline/, coordination/bin/, .github/.

$ Codex message 7 also named a "hardlink stale-result variant" and a "receipt-directory swap window" at b1390a24 as newly discovered evasion routes on the same peer mechanism. Both are eliminated by removal at c1f2ac88 for the same reason as F4/F6: no reader, no writer, no consumer.

$ tests/unit/test_provider_surface_map.py:20-31 + :149-165
→ FORBIDDEN_RUNTIME_GLOBS names peer.py, peer_backends.py, peer_receipt.py, slope_metrics.py, pin_reconciler.py, seed_inventory.py, consume_reviewer_result.py plus cursor/seat-launcher/claude_task_connector patterns. test_runtime_absence_control_rejects_reintroduced_launch_surfaces parametrizes non-vacuous fixtures at each of those paths and asserts the assertion raises. Verified pattern-to-fixture pairing.

$ F1 skill-shadowing class — tests/unit/test_skill_packs.py:87-107
→ _skill_descriptions() enumerates _tracked(".agents/skills/*/SKILL.md"), where _tracked() runs `git ls-files -z --`, so an ignored working-tree SKILL.md cannot enter the description map at all — the F1 attack surface (globbed working tree) is structurally gone. Duplicate refusal at :98-102 raises "duplicate skill name {name!r}" rather than silently overwriting. Sibling reversion control at tests/unit/test_skill_pack_corpus.py:14-28. One residual sufficiency gap: no INJECTED-duplicate control test plants two SKILL.md with the same frontmatter name and asserts the assert fires; the tracked-only enumeration makes the assert structurally unreachable in the current corpus, so sufficiency rests on code-reading rather than an evasion control. This is a defense-in-depth note, not an F1 reopen.

$ F3 retired-event delete/reintroduction class — pipeline/mailbox_admission.py:104-158
→ check_post_cutover_event_admission reads the ACTUAL desktop-write-cutover tree via _tree_event_entries at cutover b1390a244d2368e89bb65d65a148e55bac0d8df0 (line 104), not projection.introductions. For each post-cutover commit that touched the mailbox, if the event existed at cutover the current signatures must be a subset of the cutover baseline; byte/mode/type mismatch emits FATAL "event {name} changed bytes, mode, or type from the desktop cutover at {commit}". If absent at cutover, introduction[0] != commit emits FATAL "event was absent at the desktop cutover and cannot reuse a pre-cutover introduction". Additional projection-layer gate at pipeline/check_coordination.py:775-791 and :943-946 refuses the projection with "mailbox event was reintroduced with different bytes". Non-vacuous controls: tests/unit/test_desktop_write_admission.py:115-125 test_restored_boundary_blob_does_not_hide_mutation reproduces mutation-then-byte-identical-restore; tests/unit/test_desktop_write_admission.py:98-104 test_pre_cutover_introduction_cannot_be_reused reproduces the strict-writer variant; tests/unit/test_reintroduction_doctrine.py:107-134 test_changed_reintroduction_is_refused_by_every_consumer reproduces the projection-layer variant and asserts projection is None with "reintroduced with different bytes".

$ Direct-Git event injection — mailbox_admission.py replays every mailbox-changing commit after b1390a24 through validate_committed_new_event, which applies mailbox_writer's fixed-writer envelope and payload policy against the committed bytes. A raw git-add of a hand-crafted event with retired-role sender/recipient produces a post_cutover_event_admission FATAL rather than admitting silently.

$ coordination/bin/pipeline-python -m pytest -q
→ 1133 passed in 171.70s (exit 0). Matches the author's evidence claim exactly.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_provider_surface_map.py tests/unit/test_mailbox_new_write_allowlist.py tests/unit/test_mailbox_review_admission.py tests/unit/test_desktop_write_admission.py tests/unit/test_desktop_direct_git_guards.py tests/unit/test_ci_admission_gate.py
→ 102 passed in 10.47s — focused admission and abuse-class suites.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_skill_packs.py tests/unit/test_mailbox_writer.py tests/unit/test_check_coordination.py
→ 111 passed in 31.51s — focused F1 + writer + coordination suites. F3 delete/reintroduce and F1 duplicate-name controls both in that pass.

$ bin/pipeline preflight
→ 14/14 PASS. Codex, Claude, AGY apps installed and identified; three project MCP configs bind exactly member=codex/claude/agy; stdio initialize 2025-06-18 handshakes for all three; native discovery for Codex/Claude; Antigravity workspace registration; native tool cache matches exact plugin tools; AGY CLI allows mcp(pipeline-team/*).

$ bin/pipeline check --fast
→ PROJECT SMOKE OK; CEREMONY CHECK PASS (all five rules: xfail-strictness 0 violations, invisible-green clean, gate-executes-pins non-vacuous, utv-not-row-status clean, python-growth net 0 from HEAD^); FAST PREFLIGHT PASS.

$ bin/pipeline check admission --base 86146d1f --head fb7e8700
→ Range currently BLOCKED — 20 authority-surface commits, 16 uncovered pre-b1390a24 commits plus my two prior GO reports covering the b1390a24..fb7e8700 remainder. My new GO on 86146d1f..fb7e8700 closes those 16 commits.

$ bin/pipeline check admission --base b1390a24 --head fb7e8700
→ 4 authority-surface commits, RESULT: structurally admitted (my two prior GO reports already cover this subrange).

$ bin/pipeline check admission --base 86146d1f --head b1390a24
→ 16 authority-surface commits, RESULT: BLOCKED — this is the older Claude-authored epoch this cumulative review closes. The prior 2026-08-21T22-12-09Z FAIL is correctly non-admitting, and the earlier 2026-08-21T16-55-18Z is correctly superseded.

$ git diff --check 86146d1f..fb7e8700
→ clean. Reproduces the author's clean-diff claim.

$ coordination/bin/pipeline-python -m compileall -q pipeline/
→ clean.

$ config/model-families.toml
→ claude-opus-4-7 in active_author_models AND active_reviewer_models; gpt-5.6-sol in both; historical_cutover=b1390a244d2368e89bb65d65a148e55bac0d8df0 matches DESKTOP_WRITE_CUTOVER_COMMIT. Cross-family: claude != gpt.

$ bin/pipeline review validate on the request candidate itself
→ compact-pair validation passed. Request grammar is structurally correct.

$ Independent inspection of the six declared abuse-class families.

$ Class 1 — Removed peer/provider paths must not survive under aliases or reintroduction — ABSENT confirmed at fb7e8700 by direct path check plus grep sweep for aliased imports; no receipt-root/next-seq/write-receipt/codex-last-message reference under pipeline/, coordination/bin/, .github/; no CLI dispatch; no tests import a peer symbol. Reintroduction guarded by exact-name FORBIDDEN glob and non-vacuous fixture, though a renamed variant is not covered (MINOR above).

$ Class 2 — Desktop-team transport must preserve repository and filesystem identity — pipeline/team_store.py:41-141 refuses group/world-writable common dir; requires owner-only store directory; refuses symlinks, hardlinks, foreign uid on both main and -wal/-shm sidecars; re-validates the file identity around every connection; binds git_common_dir into metadata and refuses cross-repo stores. status_team_store.py:68-84 mirrors those checks on the observation path and never touches the shared store (copies main+WAL to scratch, queries read-only immutable). tests/unit/test_team_security.py and tests/unit/test_status_team_store.py attack these with real symlinks, hardlinks, monkeypatched foreign uid, and raw SQLite UPDATE of git_common_dir.

$ Class 3 — Message and MCP semantics must resist identity and lifecycle confusion — team_messages.py enforces sender-scoped idempotency, refuses duplicate keys with changed content, rejects reply_to that is not addressed to sender, validates JSON-safe id range through SQL CHECK plus TRIGGER, refuses oversized bodies and control bytes. team_mcp.py enforces initialize→notifications/initialized→ready lifecycle and refuses tools/call before ready; the serve loop discards oversized request lines before parsing. team_status/team_wait/team_send responses all include grants_authority=false, and the "queued" state is not "acknowledged" — the response text explicitly says so.

$ Class 4 — Native app configuration and discovery must bind exactly Codex, Claude, and AGY — preflight passes and .mcp.json, .claude/settings.json, .codex/config.toml, .agents/plugins/pipeline-team/{plugin.json,mcp_config.json} all narrow to exactly the pipeline-team server; enableAllProjectMcpServers is refused; extra config keys are refused; PIPELINE_TEAM_DISCOVERY_ONLY=1 maps to _DiscoveryTeam which raises on every operation so discovery cannot create the store.

$ Class 5 — Review and admission must resist laundering — every authority-surface commit was inspected individually (34 commits, notable ones at ac0ac341 subtract non-CLI surface, f7f1c2ad one command surface, 4c4371fd two review roles, d2fe72b1 peer machinery introduced, 782cb724+2a19e4ff remediation, c1f2ac88 desktop cutover with peer removal). mailbox_writer.NEW_WRITE_SENDERS+NEW_WRITE_RECIPIENTS refuse retired-role writes at compose time; validate_committed_new_event refuses them at admission time; author-model must be currently admitted; abuse-class assessment must be bound-to-request for high-risk-control; ci_admission_gate.resolve_range now prefers origin/main (my prior review addressed the 67ed9ae6 mistake that flipped this); check_no_ceremony._committed_range_violations measures the committed range too, not only the working tree.

$ Class 6 — Communication grants no push/merge/release/spend/destructive/live-data authority — team messages carry explicit grants_authority=false; the SQLite messages table has no authority column; effect authority per AGENTS.md and pipeline/codex_protocol_model.py requires exact current user/task authority per effect. This report is one message; it does not push, merge, spend, mutate live data, or launch a provider.

$ Class 7 — Capability removal must not defeat the requested team — bin/pipeline preflight demonstrates each of the three desktop apps handshakes as its configured member label and can call team_status live. mcp__pipeline-team__team_status from this Claude Opus 4.7 desktop session confirms the three-member roster is registered and reachable. AGY appears in team status with its capability strings and is fully heard through the same transport, but AGY cannot supply a formal accepting verdict per .agents/skills/four-seat-protocol/SKILL.md — this is enforced at the compact_pair_loop parser: reviewer_model must be currently admitted, and AGY/Gemini is not in active_reviewer_models.

$ FAIL report 2026-08-21T22-12-09Z@1b37caf8 disposition = addressed. F1 skill-shadowing: closed at tests/unit/test_skill_packs.py:84-100. F3 retired-event delete/reintroduce: closed at pipeline/mailbox_admission.py:143-184 with reproducing test at test_check_coordination.py:1683. F4 symlink escape in peer result: eliminated by removal of pipeline/peer.py at c1f2ac88. F6 symlink+concurrency in receipt: eliminated by removal of pipeline/peer_receipt.py at c1f2ac88. Argv/spend authority: eliminated by removal of pipeline/peer.py at c1f2ac88. Hardlink stale-result and receipt-directory swap variants (Codex message 7): eliminated by removal at c1f2ac88. F2/F5/F7/F8 (previously addressed by the initial remediation) remain addressed. The two earlier NITs on EOF whitespace are resolved: git diff --check 86146d1f..fb7e8700 exit 0.

$ First-GO report 2026-08-27T14-51-44Z@d84a9b3c disposition = addressed. Its three MINOR findings (test_provider_surface_map reversion gap, status_team_store sidecar test gap, status_desktop 20-line pin gap) are all closed by commits e26de454+97400d8d within this cumulative range, as attested in the second-GO report and re-verified here.

$ Second-GO report 2026-08-27T15-21-24Z@fb7e8700 disposition = addressed. Its INFORMATIONAL doc-drift finding is carried forward here as MINOR; the substantive fixes are inside this cumulative range.

$ mcp__pipeline-team__team_status (live in this Claude Opus 4.7 session)
→ member=claude, three-member roster codex/claude/agy with capability strings, store=/Users/hyungkoookkim/Pipeline/.git/pipeline-team/messages.sqlite3, grants_authority=false. Team round trip: team_wait after_id=5 read messages 6/7/8, team_wait after_id=8 acknowledged the cursor through 8, team_send reply_to=8 idempotency_key=review-2d4159e5-accepted queued as id 9.

$ AGY receipt SHA-256 83adace686d0013f32871e9745eb89ccf9544ddf42ad533e3781c28c3d4b93a6 considered as advisory only; AGY does not supply the accepting formal verdict; this cross-family Claude reviewer is the accepting seat.

Cursor at send: cursorless
