# Reviewer → Author: replacement final bootstrap integration review verified

**When:** 2026-08-28T04:14:11Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-28T03-42-56Z-author-to-reviewer-verify-request.md@0fa1febc858827006c98e3424bf923b0e20fc6a9
Reviewed base: fb7e87000bebb72d4eaf0b3d03fa2f8675058a29
Reviewed head: 05a51a17b291d46936dfa0ddcf1e0138fdcf88d2
Reviewer seat: reviewer
Reviewer model: claude-sonnet-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR — The committed request cited an incorrect verify-request commit hash (0fa1febcfc676f98559a16d9a6d4335120ce1443, which does not exist) in the team-transport message that preceded this request's own commit; the committed mailbox artifact itself is correct and this report binds to it. Codex independently caught and corrected the same error before I acted on it. No effect on this range's substance.

## Finding Refs

- coordination/mailbox/sent/2026-08-27T19-16-42Z-reviewer-to-author-verification-report.md@3a8d29e13ac424188d934d56257e76146a1da7cb
- coordination/mailbox/sent/2026-08-28T02-43-08Z-operator-to-director-verification-report.md@3f4ba504016d622f97a0675890cb0803dcdff3c8

## Finding Dispositions

- coordination/mailbox/sent/2026-08-27T19-16-42Z-reviewer-to-author-verification-report.md@3a8d29e13ac424188d934d56257e76146a1da7cb: addressed
- coordination/mailbox/sent/2026-08-28T02-43-08Z-operator-to-director-verification-report.md@3f4ba504016d622f97a0675890cb0803dcdff3c8: addressed

## Evidence

$ git log --oneline fb7e8700..05a51a17
→ 11 commits inspected individually: 05a51a17 (fix: apply forward-reader pin in CI gate), c23c2430 (held request, withdrawn), 3dba3e7e (fix: admit active Claude Sonnet 5), a503076e (merge: origin/main into codex/desktop-app-team, with hand-resolved conflicts in pipeline/compact_pair_loop.py + two test files), 49b8013b (merge: PR #53 admission-forward-reader into origin/main), 85075ad1 (fix: pin trusted forward-reader review — first, incomplete pin), 3f4ba504 (my prior legacy operator GO), 56014111 (director request), 05df3003 (reader widening, already reviewed), 3a8d29e1 (my prior cumulative GO), 2d4159e5 (cumulative request, already reviewed).

$ git show 85075ad1bb908a0240e22b5871773de96fb83468
→ Adds _FROZEN_FORWARD_READER_REVIEW_ARTIFACTS = exactly two (path -> (introduction_commit, sha256)) tuples in pipeline/mailbox_review_admission.py, pinning the exact legacy director-to-operator request (5601411) and operator-to-director report (3f4ba504) I reviewed and published. _is_exact_frozen_forward_reader_artifact requires an exact match on all three of path, introduction commit, and content hash. When matched for a FORMAL_REVIEW_KINDS event with a legacy sender/recipient, validate_committed_new_event bypasses new_write_envelope_problem's rejection and routes to projected_request/projected_report with current_policy=False (historical grading), while reference resolution (_require_path_references_resolve) is explicitly still run via `current_policy or exact_frozen`. Ships three new tests: test_exact_pin_reaches_only_the_committed_reader (also confirms the live NEW-candidate writer path, mailbox_writer.validate_event_candidate_bytes, still rejects the same bytes — the pin applies only to replaying already-committed history, never to fresh publication), test_pin_rejects_one_variable_drift (moved timestamp, wrong commit, one changed byte — all three rejected), test_pin_cannot_reopen_non_formal_legacy_routes (same path/commit reused under kind=findings is rejected as "sender must be a desktop app").

$ git show 05a51a17b291d46936dfa0ddcf1e0138fdcf88d2
→ Confirms the request's own diagnosis: pipeline/ci_admission_gate.py's _validate_current_envelope is a SEPARATE consumer of new_write_envelope_problem from mailbox_review_admission.validate_committed_new_event, and had no knowledge of the frozen pin. This commit extracts the shared predicate to mailbox_review_admission._is_exact_frozen_forward_reader_route(kind, sender, recipient, path, introduction_commit, raw) and wires it into BOTH consumers identically, so there is exactly one source of truth (_FROZEN_FORWARD_READER_REVIEW_ARTIFACTS) with two independent call sites, not two divergent copies. New test test_gate_wires_the_exact_frozen_forward_reader_route monkeypatches the shared predicate both True and False and asserts the gate's behavior flips accordingly — a non-vacuous wiring control, not just a call-count check.

$ Independent in-process, zero-file-edit non-vacuity proof (beyond the shipped tests): read the real committed report bytes for 3f4ba504 via git show; confirmed the raw mailbox_writer.new_write_envelope_problem on its actual envelope returns "verification-report formal review role route must be reviewer to author or all" (i.e., it WOULD be rejected by the base rule); confirmed mailbox_review_admission._is_exact_frozen_forward_reader_route recognizes it as the pinned artifact; confirmed the actual (unmodified) ci_admission_gate._validate_current_envelope accepts it. Then, with the pin predicate monkeypatched in-process to always return False (simulating pre-05a51a17 behavior with zero files touched), the SAME real bytes through the SAME function raised CompactPairError "formal review role route must be reviewer to author or all" — reproducing exactly the "before the fix" rejection the request describes — then confirmed restoring the real predicate makes it pass again. This is the dual-reader-drift class attacked directly, not inferred from the diff.

$ git diff 85075ad1bb908a0240e22b5871773de96fb83468..a503076e115aa0b1609ddf4c8a5a4f2f7c84c97a -- pipeline/compact_pair_loop.py
→ Inspected the hand-resolved merge conflict directly (not just trusted "clean merge"). origin/main's scripts/compact_pair_loop.py brought its own reader-widening (REQUEST_RE/REPORT_RE with named recipient group, _READ_PAIR_SEATS/_READ_OPERATOR_SEATS, the two anti-mixing guards) into pipeline/compact_pair_loop.py, which already natively supported author/reviewer (PAIR_SEATS previously included them directly rather than via a _READ_* alias). The resolution correctly: (1) did NOT import the scripts/-only _immutable_review_reference_is_canonical wrapper, because pipeline/protocol_mailbox.py already natively includes ROLES=(author,reviewer) in its EVENT_NAME_PATTERN SENDERS/RECIPIENTS (unlike the old worktree's protocol_mailbox.py, which had no author/reviewer identity at all) — confirmed by grep showing only bare protocol_mailbox.immutable_reference_is_canonical is called at all three Finding-Ref/Supersedes/Disposition sites; (2) added a `match.group("recipient") != "all"` exception to the report anti-mixing guard that the plain scripts/ version lacked — without it, a valid current-generation "reviewer-to-all" broadcast report would have been wrongly rejected as "mixing" (reviewer==reviewer is True, recipient==author is False, mismatch). Verified this exception is correct and not a hole: adversarially probed both "reviewer-to-author" and "reviewer-to-all" through _parse_verification_report_bytes and confirmed both pass the mixing guard (fail later only on missing body content, not on role-mixing), while "operator-to-author" (legacy sender, current-only recipient) and "reviewer-to-director" (current sender, legacy recipient) are both correctly refused with "cannot mix current and legacy roles".

$ grep -n "PAIR_SEATS\|OPERATOR_SEATS" pipeline/compact_pair_loop.py
→ Bare PAIR_SEATS/OPERATOR_SEATS are used only to define _READ_PAIR_SEATS/_READ_OPERATOR_SEATS; no other code references the narrowed base sets directly, so removing author/reviewer from the base definitions (moving them to the _READ_* aliases) does not silently break anything else. compose_request's own author_seat/assigned_operator restriction was already hardcoded to the literal strings "author"/"reviewer" before this merge and is unaffected either way — the write path was never driven by PAIR_SEATS/OPERATOR_SEATS membership.

$ Independent adversarial probes against the merged anti-mixing guards, run directly against the real unmodified module: author-to-operator, director-to-reviewer, director2-to-reviewer (verify-request) and operator-to-author, reviewer-to-director (verification-report) — all five refused with "cannot mix current and legacy roles"; reviewer-to-author and reviewer-to-all — both pass the mixing guard as required.

$ git show 3dba3e7eb0a22a30c870e0ae235f0d8a3a1a61ad
→ Adds exactly "claude-sonnet-5" to both active_author_models and active_reviewer_models in config/model-families.toml. Confirmed at HEAD: claude-opus-5 remains absent from both lists (present only in [families] for family-mapping/historical purposes); Gemini models remain in active_author_models only, never active_reviewer_models (can author, can never be the accepting reviewer) — matches the request's abuse-class requirement exactly: only the actual desktop model added, historical/advisory models correctly excluded.

$ coordination/bin/pipeline-python -m pytest -q (full suite)
→ 1138 passed in 161.29s (exit 0). Matches the author's claim of 1137 passed before 05a51a17 plus the one new wiring test it adds.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_mailbox_review_admission.py tests/unit/test_ci_admission_gate.py tests/unit/test_compact_pair_loop.py tests/unit/test_model_families_config.py tests/unit/test_mailbox_new_write_allowlist.py tests/unit/test_desktop_write_admission.py
→ 237 passed in 38.30s — focused abuse-class suites for the pin, dual-reader wiring, anti-mixing, and model admission.

$ bin/pipeline preflight
→ 14/14 PASS.

$ bin/pipeline check --fast
→ PROJECT SMOKE OK, CEREMONY CHECK PASS (all 5 rules, python-growth net 0), FAST PREFLIGHT PASS.

$ bin/pipeline check admission --base fb7e8700 --head 3dba3e7e
→ Correctly BLOCKED — both prior GO reports (3a8d29e1, 3f4ba504) already recognized as admissible via the mailbox-replay-side pin (85075ad1), but 85075ad1/3dba3e7e/a503076e themselves remain uncovered pending this report. (Ran with today's code, which already contains both fixes; the code-level "before/after" non-vacuity for the CI-gate-specific consumer is proven above via the in-process predicate simulation, since --base/--head select which commits are scanned, not which code version does the scanning.)

$ bin/pipeline check admission --base fb7e8700 --head 05a51a17
→ 5 authority-surface commits; both prior GO reports admissible; 05a51a17, 3dba3e7e, 85075ad1, a503076e correctly BLOCKED pending this report.

$ git diff --check fb7e8700..05a51a17
→ clean.

$ coordination/bin/pipeline-python -m compileall -q pipeline/
→ clean.

$ Merge-and-history-laundering abuse class — verified empirically, not just by code reading: throughout every admission-gate run above, my two prior GO reports (3a8d29e1 bound to 86146d1f..fb7e8700, 3f4ba504 bound to 86146d1f..05df3003) never once covered 85075ad1, a503076e, 49b8013b, 3dba3e7e, or 05a51a17 — ci_admission_gate._reviewed_commits computes coverage strictly from each report's own Reviewed base/head, so neither prior verdict bleeds into this new territory. This report's own Reviewed base/head (fb7e8700..05a51a17) is exactly and only this new range.

$ Authority conversion — this report, the prior two GO reports, the AGY Flash map referenced in the request, and every team-transport message grant no push, merge, release, spend, destructive, or live-data authority; none of the commands run here performed any such effect. AGY's successful map is advisory only per the request's own framing; I did not rely on it for any structural conclusion, only on direct code inspection and adversarial probing.

$ mcp__pipeline-team__team_status / team_wait (live in this Claude Sonnet 5 session)
→ Full round trip: read and corrected the same request-commit hash error Codex independently caught (messages 20/21), accepted reviewer responsibility (message 22) after explicit user authorization.

Cursor at send: cursorless
