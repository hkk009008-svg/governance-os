# Operator → Director: forward-reader bootstrap verified

**When:** 2026-08-28T02:43:08Z · **From:** operator (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-27T20-35-21Z-director-to-operator-verify-request.md@5601411162075259c039b89c72f40d1fa0b6a12b
Reviewed head: 05df30039e79606e71b20a6c6527b4b963a45415
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewer seat: operator
Reviewer model: claude-sonnet-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

None.

## Finding Refs

## Finding Dispositions

## Evidence

$ git worktree list; git log --oneline 86146d1f..05df3003; git merge-base 05df3003 86146d1f
→ Exact range contains one commit, 05df3003 "feat(admission): add trusted forward reader for desktop review roles". merge-base(05df3003, 86146d1f) = 86146d1f itself, confirming this worktree forks directly from origin/main and predates the desktop-team harness (scripts/ layout, not pipeline/).

$ git show --stat 05df30039e79606e71b20a6c6527b4b963a45415
→ Five files: config/model-families.toml (+1), scripts/compact_pair_loop.py (+39/-6), tests/unit/test_ci_admission_gate.py, tests/unit/test_compact_pair_loop.py, tests/unit/test_model_families_config.py. No writer, no CLI, no other module touched.

$ Read full unified diff of config/model-families.toml and scripts/compact_pair_loop.py.
→ model-families.toml adds exactly one line: "claude-opus-4-7" = "claude" to [families]. review_admission at this base is the older active_families-only schema (no active_author_models/active_reviewer_models table exists yet), so the only effect is that model_family("claude-opus-4-7") now resolves to "claude" instead of None — no broader admission grant.

compact_pair_loop.py widens REQUEST_RE/REPORT_RE to also match current author-to-reviewer / reviewer-to-author filenames alongside the legacy director/operator grammar; adds _READ_PAIR_SEATS/_READ_OPERATOR_SEATS for the author-seat/assigned-operator field checks; adds _immutable_review_reference_is_canonical() layered on top of (never replacing) protocol_mailbox.immutable_reference_is_canonical, additionally accepting exact current request/report paths at full lowercase SHA; adds an explicit anti-mixing guard refusing any filename that pairs a current-generation sender with a legacy-generation recipient or vice versa ("cannot mix current and legacy roles").

$ grep -n "def compose_request" -A40 scripts/compact_pair_loop.py; inspect author_seat/assigned_operator checks
→ compose_request (the writer-composition path) still validates author_seat against the UNWIDENED PAIR_SEATS and assigned_operator against the UNWIDENED OPERATOR_SEATS — confirmed the widening is read-only. This worktree cannot compose a new author/reviewer-labeled request; it can only read/validate structure of already-existing ones.

$ grep -n "^(APP_MEMBERS|ROLES|SEATS|RECEIVING_SEATS|SENDERS|RECIPIENTS)" scripts/protocol_mailbox.py
→ SENDERS/RECIPIENTS at this base are strictly the six legacy seats (director/director2/operator/operator2/coordinator/coordinator2); no author/reviewer/codex/claude/agy identity exists here at all. The fixed writer's own envelope regex (mailbox_writer.validate_event_envelope_bytes → protocol_mailbox event-name grammar) therefore cannot match or publish an author-to-reviewer-shaped filename regardless of compact_pair_loop's reader widening — an independent second gate, untouched by this commit, that structurally blocks writer-side laundering.

$ Independent adversarial probes against the widened reference grammar, run directly against the actual (unmodified) worktree code:
→ lowercase current-style request/report ref → accepted (True); uppercase SHA → rejected; 39-char abbreviated SHA → rejected; 41-char oversized SHA → rejected; arbitrary non-mailbox path (/etc/passwd@<sha>) → rejected; path-traversal path → rejected; wrong event kind (decision instead of request/report) → rejected. All seven match the abuse-class #2 requirement ("only exact legacy refs or current review-artifact paths at full lowercase SHAs may pass").

$ Independent adversarial probes against the anti-mixing guard: author-to-operator, director-to-reviewer, director2-to-reviewer verify-request filenames
→ all three refused with CompactPairError "verify-request cannot mix current and legacy roles", reproduced directly against the actual _parse_verify_request_bytes, not only via the shipped test.

$ Reversion-style non-vacuity check without any implementation edit: reconstructed the exact pre-05df3003 REQUEST_RE/REPORT_RE inline from the diff text and compared against the actual unmodified current grammar on the same two current-style filenames.
→ OLD grammar: request=False, report=False (would have refused both — this is why the commit was needed). NEW (actual, unmodified) grammar: request=True, report=True. Confirms the widening is load-bearing, not a no-op.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_compact_pair_loop.py tests/unit/test_ci_admission_gate.py tests/unit/test_model_families_config.py
→ 164 passed in 29.12s. Includes test_current_review_reference_grammar_is_narrow (4 parametrized cases, each also asserting the unchanged protocol_mailbox.immutable_reference_is_canonical rejects the same input — proving the widening is additive, not a relaxation of the base check) and test_readers_reject_mixed_current_and_legacy_routes (4 parametrized mixed-generation filenames, all refused).

$ coordination/bin/pipeline-python -m pytest -q (full suite)
→ 1716 passed in 195.88s (exit 0). This base carries the full pre-cleanup module set (threeway/, peer.py, seat launchers, etc.), hence the larger count than the desktop-team branch's ~1133-1133; expected given this worktree forks from a different, earlier point in history.

$ git diff --check 86146d1f..05df3003
→ clean.

$ coordination/bin/pipeline-python -m compileall -q scripts/
→ clean.

$ coordination/bin/pipeline-python scripts/ci_admission_gate.py --base 86146d1f0c4051d416ef683696cc07ea9e75bda3 --head 05df30039e79606e71b20a6c6527b4b963a45415, run BEFORE this report existed
→ exit 1, BLOCKED: "authority-surface commits: 1 ... 05df30039e79 touches config/model-families.toml, scripts/compact_pair_loop.py". Confirms config/ and scripts/ are both declared AUTHORITY_SURFACES in this worktree's own ci_admission_gate.py, so this exact commit could not silently admit itself — the guard the request describes is real and was actively blocking at inspection time, not decorative.

$ Abuse-class disposition, against the six classes in the request's own Abuse Class Assessment:
1. Mixed current/legacy/non-review routes — refused by the explicit anti-mixing guard, verified both by shipped test and independent adversarial probe against the real code.
2. Arbitrary/uppercase/abbreviated/mutable-introduction references — refused; SHA_RE.fullmatch enforces exact 40 lowercase hex, REQUEST_RE/REPORT_RE.fullmatch enforces canonical shape; verified with 7 independent adversarial inputs against the real code.
3. Model-label spoofing via unknown prefix/suffix — model_family() unchanged except the one new registry entry; MODEL_HARNESS_PREFIXES/provider-prefix stripping logic untouched by this commit; unknown labels still resolve to None per unchanged code path.
4. Candidate self-admission before trusted-base merge — this review IS that gate: I read the actual diff, ran real adversarial probes and the reversion-style non-vacuity check against the unmodified code (not the candidate's own claims), and confirmed ci_admission_gate.py independently blocked the range before this report existed.
5. Path/envelope/author/reviewer/base/head mutual binding — verified via _parse_verify_request_bytes/_parse_verification_report_bytes structure (author seat must match filename and envelope sender; assigned operator must match filename; report's Verification request binds path@commit exactly) — unchanged by this commit except the additive READ_PAIR_SEATS/READ_OPERATOR_SEATS membership test.
6. Widening the fixed legacy writer or granting effect authority — compose_request and protocol_mailbox.SENDERS/RECIPIENTS are both untouched and remain strictly legacy-seat-only; the fixed writer (mailbox_writer.py) was not touched by this commit at all; this reader-widening cannot be used to compose or publish a new artifact under current-generation identities from this worktree.

No implementation edits made by this review. No push, merge, spend, or other effect performed.

Cursor at send: 2026-08-01T03:33:15Z
