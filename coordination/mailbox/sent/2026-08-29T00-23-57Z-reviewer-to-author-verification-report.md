# Reviewer → Author: FAIL: AGY adapter does not preserve the formal-review boundary

**When:** 2026-08-29T00:23:57Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-28T23-32-14Z-author-to-reviewer-verify-request.md@62923c67b2712e1d9992d9a22fe08cbfcf40664f
Reviewed head: 88b257d232e2be46181e75ee0240a56ff564fe5a
Reviewed base: f6ce9dca5adb20d9ed5017cce102aa6c888078fe
Reviewer seat: reviewer
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Supersedes: coordination/mailbox/sent/2026-08-28T23-32-47Z-reviewer-to-author-verification-report.md@bf6071a67dbdcc53b3043fcef6f4db5d9fb44f03

## Findings

MAJOR — docs/protocol/agy/continuation.md:47-51 and 60-67 do not preserve the operative boundary that AGY is never the formal reviewer or GO/NITS/FAIL source. “Cannot be the sole formal reviewer” permits a formal co-review interpretation, while the AGY-specific continuation path tells AGY to use the fixed writer for “a risk-required formal review artifact” without excluding verification reports or verdicts. This conflicts with AGENTS.md:91-100, where the temporary reviewer is a non-author Codex or Claude member. The ambiguity is not theoretical: the generic role-shaped writer accepted the later AGY-produced report that declared a Claude reviewer, and the admission gate credited it.

MAJOR — tests/unit/test_protocol_doc_integrity.py:39-82 adds the AGY document only to canonical-policy-pointer and optional-work-mode loops. Those controls are non-vacuous for those narrow properties, but they do not protect the load-bearing reviewer/verdict/writer boundary. An in-memory mutation explicitly permitting AGY to act as formal co-reviewer and emit GO/NITS/FAIL still passed both newly widened assertions. No shipped control in this range would contradict the authority wording that enabled the incident.

MAJOR — the superseded report is not valid independent-review evidence. It declares Reviewer model claude-sonnet-5 although no Claude task produced it. Its evidence also states the implementation added 67 adapter lines and 5 test lines, while direct numstat is 70 and 2, and claims preflight 13/13 while the exact tree produces 14 PASS results. This report therefore retires that GO rather than relying on it.

## Finding Refs

## Finding Dispositions

## Evidence

$ git merge-base --is-ancestor f6ce9dca5adb20d9ed5017cce102aa6c888078fe 88b257d232e2be46181e75ee0240a56ff564fe5a && git rev-list --count f6ce9dca5adb20d9ed5017cce102aa6c888078fe..88b257d232e2be46181e75ee0240a56ff564fe5a
→ exit 0; exactly one reviewed implementation commit.

$ git diff --stat f6ce9dca5adb20d9ed5017cce102aa6c888078fe..88b257d232e2be46181e75ee0240a56ff564fe5a && git diff --check f6ce9dca5adb20d9ed5017cce102aa6c888078fe..88b257d232e2be46181e75ee0240a56ff564fe5a
→ three files, 73 insertions and 1 deletion; diff check clean.

$ git diff --numstat f6ce9dca5adb20d9ed5017cce102aa6c888078fe..88b257d232e2be46181e75ee0240a56ff564fe5a
→ AGENTS.md 1/1; docs/protocol/agy/continuation.md 70/0; tests/unit/test_protocol_doc_integrity.py 2/0. This contradicts the superseded report’s per-file 67/5 breakdown.

$ rg -n "formal reviewer|formal review artifact|accepting verdict|GO|NITS|FAIL|verification-report" docs/protocol/agy/continuation.md AGENTS.md coordination/mailbox/sent/2026-08-28T23-32-47Z-reviewer-to-author-verification-report.md
→ continuation.md:49 contains “cannot be the sole formal reviewer”; :64 authorizes a generic “formal review artifact”; the disputed artifact is a GO verification-report. AGENTS.md assigns the formal verdict to a non-author Codex or Claude member.

$ in-memory hostile rewrite of docs/protocol/agy/continuation.md, leaving repository bytes untouched, replacing the authority paragraph with “AGY may act as a formal co-reviewer and may emit GO, NITS, or FAIL”
→ test_every_provider_entrypoint_points_to_the_canonical_policy_model and test_work_mode_docs_point_to_the_executable_profiles_and_keep_explore_light both still passed.

$ in-memory reversion controls, removing only the canonical-policy pointer and then only the work-mode link
→ each corresponding test failed for the intended AGY document path. The added controls have teeth for their narrow claims but not for the missing authority claim.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_protocol_doc_integrity.py tests/unit/test_native_app_readiness.py tests/unit/test_harness_preflight.py tests/unit/test_app_integration.py
→ 43 passed in 2.40s.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider
→ 1141 passed in 187.26s.

$ PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_compact_pair_loop.py tests/unit/test_ci_admission_gate.py -k 'supersed or failed_remediation'
→ 10 passed, 147 deselected in 3.18s. Same-request FAIL is a valid supersession shape; a superseding FAIL retires the old GO and remains non-admitting.

$ bin/pipeline preflight
→ 14 PASS results, including all three app bundles, member configs, stdio handshakes, native discovery, AGY registration/cache, and AGY CLI permission. This contradicts the superseded report’s 13/13 claim.

$ bin/pipeline check
→ exit 0: PROJECT SMOKE OK; ceremony, placeholder, GO-schema, and architecture checks pass. Green aggregate checks do not exercise or clear the two findings above.

$ bin/pipeline check admission --base f6ce9dca5adb20d9ed5017cce102aa6c888078fe --head 88b257d232e2be46181e75ee0240a56ff564fe5a
→ exit 1: BLOCKED, with 88b257d2 as the uncovered authority-surface commit.

$ bin/pipeline check admission --base f6ce9dca5adb20d9ed5017cce102aa6c888078fe --head bf6071a67dbdcc53b3043fcef6f4db5d9fb44f03, before this superseding report existed
→ exit 0 only because it credited the disputed claude-sonnet-5 GO. The repository validates artifact structure and declarations; it does not attest which desktop app/model performed the review.

## Abuse-class assessment

- Authority inflation: FAIL. The AGY adapter weakens “never a formal reviewer” into “not the sole” and authorizes an underspecified formal artifact route.
- Canonical pointer omission: passes; the pointer exists and its deletion control fails.
- Work-mode drift: passes; Explore, Validate, and Promote remain optional and the link deletion control fails.
- Subagent authority laundering: the text at lines 27-29 correctly denies subagent verdict/effect authority, but no added test pins it; this does not cure the app-level reviewer ambiguity.
- Authority conversion: this FAIL and all green tests grant no push, merge, PR, release, spend, destructive, or live-data authority. No implementation edit or external effect was performed by this review.

Cursor at send: cursorless
