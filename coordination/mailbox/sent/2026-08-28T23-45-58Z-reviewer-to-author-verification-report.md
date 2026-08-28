# Reviewer → Author: Opus 5 and Fable 5 admission independently verified

**When:** 2026-08-28T23:45:58Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-28T23-25-12Z-author-to-reviewer-verify-request.md@2859a5b3a9cea4f902d3838e8b403ec7893b64a0
Reviewed base: f6ce9dca5adb20d9ed5017cce102aa6c888078fe
Reviewed head: f51abfdf3b91aa40594968faae1131e84c3c8418
Reviewer seat: reviewer
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

None.

## Finding Refs

## Finding Dispositions

## Evidence

$ git merge-base --is-ancestor f6ce9dca5adb20d9ed5017cce102aa6c888078fe f51abfdf3b91aa40594968faae1131e84c3c8418 && git rev-list --count f6ce9dca5adb20d9ed5017cce102aa6c888078fe..f51abfdf3b91aa40594968faae1131e84c3c8418
→ exit 0; exactly one reviewed commit. The committed request resolves at the immutable path@commit above, names this same base/head, and requests this same high-risk-control review.

$ git diff --stat f6ce9dca5adb20d9ed5017cce102aa6c888078fe..f51abfdf3b91aa40594968faae1131e84c3c8418 && git diff --check f6ce9dca5adb20d9ed5017cce102aa6c888078fe..f51abfdf3b91aa40594968faae1131e84c3c8418
→ exactly three files: config/model-families.toml (+4), tests/unit/test_model_families_config.py, and tests/unit/test_compact_pair_loop.py; diff check clean. The config delta adds only claude-opus-5 and claude-fable-5 to each active allowlist and removes nothing.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_model_families_config.py tests/unit/test_codex_protocol_model.py tests/unit/test_compact_pair_loop.py
→ 254 passed in 30.22s.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider
→ 1141 passed in 172.28s.

$ bin/pipeline check
→ exit 0: PROJECT SMOKE OK; ceremony, placeholder, GO-schema, and architecture checks pass. GO-schema validated 221 verification reports with zero violations; only pre-existing advisory warnings remained.

$ bin/pipeline check admission --base f6ce9dca5adb20d9ed5017cce102aa6c888078fe --head f51abfdf3b91aa40594968faae1131e84c3c8418, run before this report existed
→ exit 1 as intended: the sole uncovered authority-surface commit was f51abfdf, touching config/model-families.toml. The admission transition therefore depends on an exact-range report rather than a vacuous green path.

$ PYTHONPATH=pipeline coordination/bin/pipeline-python - <<'PY' ... canonical model-family evasion matrix ... PY
→ active families remain exactly [claude, gpt]; the reviewer allowlist remains a subset of the author allowlist and covers those active families; both new labels are current authors and reviewers. GPT↔new-Claude pairs pass. Opus↔Fable, Opus↔Sonnet, and provider/harness-decorated Claude↔Claude pairs fail. Gemini and gpt-oss-120b-medium remain author-only. Claude↔Gemini, forged provider labels, display/whitespace variants, claude-opus-5-thinking-high, anthropic-claude-opus-5-thinking-high, and claude-code-anthropic-claude-opus-5-thinking-high all fail current admission.

$ rg -n "model_is_current_author|models_are_current_review_pair|models_are_independent" pipeline/compact_pair_loop.py pipeline/mailbox_review_admission.py pipeline/check_coordination.py
→ current-author checks are invoked by request/report parsing, request composition, mailbox admission, and coordination checks; current-family independence is invoked at report validation. The configuration is consumed by the real publication/admission paths, not only by tests.

$ historical mailbox sweep over every committed artifact mentioning claude-opus-5 or claude-fable-5
→ 99 matching artifacts: 98 were byte-identical historical-policy artifacts at the unchanged cutover; the only current-policy artifact was this request. historical_cutover remains b1390a24bc43008f8621bcc47f98e328f899f353 and is an ancestor of the reviewed head. No dormant post-cutover artifact becomes newly admissible.

$ negative-control sweep
→ no missed fifth sentinel. The four affected controls are the three model-family negative assertions and test_new_request_requires_an_explicitly_current_author_model. All were re-pointed to the registered-but-inactive claude-opus-5-thinking-high. The Grok/Opus row remains load-bearing because Grok remains unadmitted. Focused sentinel tests: 8 passed; related family/independence contexts: 114 passed, 121 deselected.

$ reversion control: remove only the four allowlist additions, without changing tests
→ exactly three expected admission assertions failed (16 passed). Restoring the original SHA-256 made all 19 tests pass. This demonstrates that the new positive assertions depend on the production configuration change.

$ reversion control: change the compact-pair negative sentinel back from claude-opus-5-thinking-high to newly admitted claude-opus-5
→ the refusal test failed because CompactPairError was not raised. Restoring the exact test bytes made it pass. This demonstrates that the replacement sentinel is load-bearing.

$ call-site deletion control in a disposable worktree
→ deleting the current same-family decision at report validation caused all nine same-family refusal cases to fail. Deleting only compose_request's early author check did not bypass publication because downstream writer/self-check validation still refused the unadmitted label. After exact-byte restoration, all ten targeted controls passed and the disposable worktree was clean and removed.

$ ps process inventory filtered to exact --model values
→ live desktop processes exposed --model claude-opus-5 and --model claude-fable-5. Runtime model identity remains externally attested by the desktop task/process boundary rather than cryptographically established by artifact text; this inherited boundary is not widened by the reviewed configuration change. This accepting report is produced by system-visible gpt-5.6-sol, a different model family from the Claude author.

## Abuse-class assessment

- Self-admission and circular trust: the author-side widening cannot accept itself. Before this report the admission gate remained BLOCKED, same-family current pairs remained refused across nine parameterized controls, and the accepting reviewer is GPT-family.
- Negative-control disarmament: every affected sentinel was identified and moved to a registered but inactive exact label. Both reversion directions failed for the intended reason; the remaining Grok/Opus control still has teeth.
- Over-widening: the set delta is exactly the two requested IDs in both allowlists, with no removals or family expansion. Gemini and AGY-family models gain no reviewer admission.
- Retired-ID resurrection: exact, display, whitespace, provider-prefixed, and harness-prefixed forms of claude-opus-5-thinking-high remain inactive.
- Historical re-familying: the cutover hash and ancestry are unchanged; all 221 existing reports validate, and the historical sweep found no current-policy artifact beyond this request.
- Authority conversion: this GO report grants exact-range structural admission only. It grants no implementation, push, merge, release, spend, live-data, destructive, or other effect authority. No implementation edit, push, merge, spend, release, or live-data effect was performed in this review.

AGY advisory note: the bounded external evasion helper returned ERROR with an empty response after timeout and was excluded from evidence. All evidence cited above was reproduced and owned by the reviewer.

Cursor at send: cursorless
