# Reviewer → Author: desktop-app team harness exact-range review

**When:** 2026-08-27T14:51:44Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-27T14-33-49Z-author-to-reviewer-verify-request.md@d2fabcc0c67bee9476d38fd7c2a27601c555b4bc
Reviewed base: b1390a244d2368e89bb65d65a148e55bac0d8df0
Reviewed head: c1f2ac88e5b4ec1d72eee498a9090d97fdb7b55b
Reviewer seat: reviewer
Reviewer model: claude-opus-4-7
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR — Reversion controls in tests/unit/test_provider_surface_map.py cover peer/seat-launcher/cursor/consume-events/claim-lock/release-lock but do not reject a re-introduced pipeline/slope_metrics.py, pipeline/pin_reconciler.py, pipeline/seed_inventory.py, or pipeline/consume_reviewer_result.py. The CI admission gate at pipeline/ci_admission_gate.py:50-85 still requires a high-risk-control GO/NITS report on any commit touching pipeline/, so bare reintroduction cannot silently land; this is a defense-in-depth observation on the surface-map guard.

MINOR — Filesystem/SQLite guards in pipeline/status_team_store.py:68-84 and :220-224 refuse a WAL/SHM sidecar that is symlinked, hardlinked, owner-mismatched, or 0o077-permissive, and refuse a store whose recorded git_common_dir does not match the observed repo. Neither branch is exercised in the test suite. Guards are present and defensible; the reviewer confirmed them by inspection; this is a test-coverage observation, not a broken guard.

MINOR — pipeline/status_desktop.py:135-136 asserts the orientation snapshot cannot exceed 20 lines. No test locks the rendered output; growth in either helper could regress silently.

INFORMATIONAL — Doc drift. TRANSFER-MANIFEST.md:68, DECISIONS.md:195/196/215, and several docs/superpowers/plans/*.md still describe removed surfaces (claim-lock, release-lock, consume_reviewer_result, slope_metrics, pin_reconciler) as live. No runtime effect; they read as re-implementation recipes.

## Finding Refs

## Finding Dispositions

## Evidence

$ coordination/bin/pipeline-python -m pytest -q
→ 1119 passed in 183.62s (exit 0). One more than the request's 1118; delta is not a regression.

$ bin/pipeline preflight
→ 14 rows, all PASS: apps codex/claude/agy (ChatGPT.app 26.820.60940, Claude.app 1.37937.3, Antigravity.app 2.11.0); project configs codex/claude/agy; stdio initialize 2025-06-18 handshakes for codex/claude/agy each listed all three tools and executed team_status as member=<self>; Codex native discovery enabled member=codex; Claude native discovery connected member=claude; Antigravity workspace registration; Antigravity native cache matches exact plugin tools; AGY CLI allows mcp(pipeline-team/*).

$ bin/pipeline check --fast
→ PROJECT SMOKE — desktop team and governance invariants OK. CEREMONY CHECK PASS on all five rules (xfail-strictness 0 violations, invisible-green clean, gate-executes-pins executed the strict-xfail controls, utv-not-row-status clean, python-growth net 0). FAST PREFLIGHT PASS.

$ bin/pipeline check admission
→ Range 86146d1f..d2fabcc0 correctly BLOCKED — c1f2ac88 has no admitting review yet at inspection time, so the guard actively refuses the range this report closes. Earlier 2026-08-21T22-12-09Z reviewer-to-author-verification-report is properly counted as verdict FAIL does not admit; the 2026-08-21T16-55-18Z report is counted as superseded. Gate behavior is non-vacuous.

$ mcp__pipeline-team__team_status (live in this Claude Opus 4.7 session)
→ member=claude; three-member roster codex/claude/agy with capability strings; store="/Users/hyungkoookkim/Pipeline/.git/pipeline-team/messages.sqlite3"; grants_authority=false. Resolves the request's "UNKNOWN live tool availability" limitation for this desktop model session.

$ mcp__pipeline-team__team_wait after_id=0 then after_id=1
→ Retrieved Codex message id 1 (idempotency_key review-d2fabcc0-c1f2ac88), advanced acknowledged_through to 1, replied via team_send with idempotency_key review-c1f2ac88-accepted (message id 2, state=queued). Live desktop MCP round trip completed before this review.

$ Independent inspection of pipeline/team.py, team_store.py, team_messages.py, team_mcp.py, native_app_readiness.py, harness_preflight.py, codex_protocol_model.py, mailbox_admission.py, mailbox_review_admission.py, mailbox_writer.py, compact_pair_loop.py, ci_admission_gate.py, status.py, status_desktop.py, status_team_store.py, check_no_ceremony.py, .mcp.json, .codex/config.toml, .claude/settings.json, .agents/plugins/pipeline-team/{plugin.json,mcp_config.json}, config/model-families.toml, coordination/bin/send-event
→ every abuse class the request names has a structural defense.

$ Identity/model spoofing — codex_protocol_model.models_are_independent + CURRENT_AUTHOR_MODEL_IDS/CURRENT_REVIEWER_MODEL_IDS derived from config/model-families.toml enforce cross-family review for high-risk-control; gpt-5.6-sol resolves to family "gpt", claude-opus-4-7 resolves to family "claude"; historical_cutover b1390a24 pins the boundary at this range's base.

$ Extra/malformed/stale MCP — harness_preflight._validate_member_config refuses any config with extra keys, wrong transport, non-'.' cwd, env overrides, or a command that is not this repo's bin/pipeline; .claude/settings.json is asserted to enable exactly ['pipeline-team'] with no enableAllProjectMcpServers; the AGY plugin manifest and config are locked to name pipeline-team with the exact member=agy args.

$ Retired-role/direct-Git admission bypass — pipeline/mailbox_admission.py:64-206 replays every mailbox-changing commit after the desktop cutover b1390a24 through mailbox_review_admission.validate_committed_new_event, emitting FATAL issues if any post-cutover event fails the fixed-writer admission or renames an existing durable event. The desktop cutover matches this range's Reviewed base.

$ Filesystem/SQLite/WAL races — team_store._repository_identity/_secure_store/_validate_store_path enforce owner-only, symlink-refusing, single-hardlink checks with re-validation around every connection; _initialize_once binds git_common_dir into the metadata table and refuses cross-repo stores. status_team_store copies the WAL+main pair to a scratch snapshot with bounded retries and queries only the snapshot in read-only immutable mode.

$ JSON-safe IDs/idempotency/lifecycle/invalid MCP params — MAX_MESSAGE_ID = (1<<53)-1 is enforced by SQL CHECK plus a TRIGGER that raises 'message id exceeds JSON-safe range'; team_messages._validate_key/_validate_body/_validate_read close every input bound; team_mcp.McpServer.dispatch enforces the initialize→notifications/initialized→ready lifecycle and refuses tools/call before ready; the serve loop discards oversized lines before parsing so a JSON-shaped tail cannot execute.

$ Discovery-mode mutation — team._DiscoveryTeam raises TeamError on every operation when PIPELINE_TEAM_DISCOVERY_ONLY=1; native_app_readiness.check_native_discovery sets that env var when calling `codex mcp get` and `claude mcp get`, so read-only discovery cannot create or mutate the shared SQLite store.

$ git -C . show d2fabcc0c67bee9476d38fd7c2a27601c555b4bc:coordination/mailbox/sent/2026-08-27T14-33-49Z-author-to-reviewer-verify-request.md
→ Event type: verify-request, Reviewed base b1390a244d2368e89bb65d65a148e55bac0d8df0, Reviewed head c1f2ac88e5b4ec1d72eee498a9090d97fdb7b55b, Author seat author, Author model gpt-5.6-sol, Assigned operator reviewer, Risk class high-risk-control, nonempty ## Abuse Class Assessment — the exact bindings this report attests to.

$ AGY advisory receipt SHA-256 83adace686d0013f32871e9745eb89ccf9544ddf42ad533e3781c28c3d4b93a6
→ Considered as advisory only per AGENTS.md and the four-seat-protocol adapter; AGY cannot supply the accepting formal verdict; this Claude-family reviewer is the accepting seat.

$ git -C . diff --stat b1390a244d2368e89bb65d65a148e55bac0d8df0..c1f2ac88e5b4ec1d72eee498a9090d97fdb7b55b | tail -1
→ 177 files changed, 9548 insertions(+), 13151 deletions(-)

Cursor at send: cursorless
