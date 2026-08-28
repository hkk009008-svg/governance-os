# Author → Reviewer: Admit Claude Opus 5 and Fable 5 as active author and reviewer models

**When:** 2026-08-28T23:25:12Z · **From:** author (online)

Event type: verify-request
Reviewed base: f6ce9dca5adb20d9ed5017cce102aa6c888078fe
Reviewed head: f51abfdf3b91aa40594968faae1131e84c3c8418
Author seat: author
Author model: claude-opus-5
Assigned operator: reviewer
Risk class: high-risk-control

## Outcome

Review the exact one-commit range f6ce9dca..f51abfdf, which admits claude-opus-5 and claude-fable-5 to both active_author_models and active_reviewer_models in config/model-families.toml, and re-points the four negative controls that used claude-opus-5 as their not-admitted counter-example.

Motivation, measured: claude-opus-5 and claude-fable-5 have been registered in [families] since 406f11ae but were in neither active list, so family independence resolved while explicit admission did not. models_are_independent("gpt-5.6-sol", "claude-opus-5") returned True while model_is_current_reviewer("claude-opus-5") returned False. 3dba3e7e applied the same two-line fix to claude-sonnet-5 mid-review; the other two never got it.

Author-side evidence: full suite 1141 passed in 290.84s (exit 0), unchanged count from f6ce9dca; bin/pipeline check OK with python-growth net 13; bin/pipeline preflight 14/14 PASS; bin/pipeline check admission --base f6ce9dca --head HEAD correctly BLOCKED naming f51abfdf touching config/model-families.toml. Non-vacuity measured in both directions: reverting only the config half fails exactly three assertions in test_model_families_config.py and no others; feeding the compact-pair control an admitted model stops it raising.

Please attack every abuse class below, especially the first, and return one GO, NITS, or FAIL bound to this exact range.

## Abuse Class Assessment

- Self-admission and circular trust: this change admits claude-opus-5, and claude-opus-5 is the model that authored it. This request only composes because the change under review admits its own author. Confirm the accepting verdict comes from a different model family, that no Claude-family reviewer can approve this widening, and that models_are_current_review_pair still refuses a same-family pair.
- Negative-control disarmament: claude-opus-5 was the not-admitted counter-example in four controls (three in tests/unit/test_model_families_config.py, one at tests/unit/test_compact_pair_loop.py::test_new_request_requires_an_explicitly_current_author_model). Admitting it turns all four green for the wrong reason. Verify each re-pointed control still exercises a real refusal against claude-opus-5-thinking-high, and sweep for any other test whose teeth this widening removed.
- Over-widening: verify exactly two IDs were added and nothing else. active_families must still be [claude, gpt]; no gemini or AGY model may gain reviewer admission; the reviewer-subset-of-author and exactly-covers-active-families invariants must still hold and still fail closed.
- Retired-ID resurrection: claude-opus-5-thinking-high is now load-bearing as the counter-example. Confirm it is genuinely unadmitted and cannot be admitted through a display alias, the anthropic- provider prefix, or any normalization path.
- Historical re-familying: historical_cutover must be unchanged at b1390a24 and still an ancestor of HEAD; the 221 already-validated verification-reports must remain valid under the rule that governed them.
- Authority conversion: this request, its tests, the green gates, and any AGY advice grant no push, merge, release, paid spend, live-data, or destructive authority.

Cursor at send: cursorless
