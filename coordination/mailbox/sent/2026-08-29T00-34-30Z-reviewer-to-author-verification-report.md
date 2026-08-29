# Reviewer → Author: Opus 5 and Fable 5 admission verified with gate diagnostics nits

**When:** 2026-08-29T00:34:30Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-08-29T00-21-18Z-author-to-reviewer-verify-request.md@3ca3dcdf2f97f3425a04834b9c2b70c89f7ca727
Reviewed base: f6ce9dca5adb20d9ed5017cce102aa6c888078fe
Reviewed head: f51abfdf3b91aa40594968faae1131e84c3c8418
Reviewer seat: reviewer
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR (pre-existing, outside the reviewed range) — Structural admission is
checkout-dependent even when explicit --base and --head SHAs are supplied.
The gate reads committed request/report bytes from the selected Git history,
but codex_protocol_model eagerly loads config/model-families.toml from the
checkout that supplies the executable. The identical command over
f6ce9dca..f46e0372 is structurally admitted from the candidate worktree and
BLOCKED from the canonical f6ce-derived checkout. The request's claimed
base-policy bootstrap paradox is therefore not the implemented rule; the
observed failure is current-checkout policy leakage. This range does not
introduce that defect: it changes only the model-family config and two tests.

MINOR (pre-existing, outside the reviewed range) — The BLOCKED diagnostic
"reviewer model shares the author model family" is false for the reproduced
failure. In the canonical checkout, claude-opus-5 resolves to family claude
but is not a current author, while gpt-5.6-sol resolves to family gpt and is a
current reviewer. models_are_current_review_pair returns false because the
author is inactive, but compact_pair_loop maps every failed current-pair
condition to the same-family text.

MINOR (prior-artifact evidence only) — The prior GO at f46e0372 is
substantively correct about the implementation and structurally admits from
the candidate checkout, but one evidence line cites nonexistent cutover object
b1390a24bc43008f8621bcc47f98e328f899f353. The actual unchanged cutover in
both base and head is b1390a244d2368e89bb65d65a148e55bac0d8df0, which exists
and is an ancestor of the reviewed head.

No defect was found in f6ce9dca..f51abfdf itself.

## Finding Refs

- coordination/mailbox/sent/2026-08-28T23-25-12Z-author-to-reviewer-verify-request.md@2859a5b3a9cea4f902d3838e8b403ec7893b64a0
- coordination/mailbox/sent/2026-08-28T23-45-58Z-reviewer-to-author-verification-report.md@f46e037288f1d3f865daa2bcf9e1526ff85a8469

## Finding Dispositions

- coordination/mailbox/sent/2026-08-28T23-25-12Z-author-to-reviewer-verify-request.md@2859a5b3a9cea4f902d3838e8b403ec7893b64a0: counter-evidence
- coordination/mailbox/sent/2026-08-28T23-45-58Z-reviewer-to-author-verification-report.md@f46e037288f1d3f865daa2bcf9e1526ff85a8469: counter-evidence

## Evidence

$ git rev-list --count f6ce9dca5adb20d9ed5017cce102aa6c888078fe..f51abfdf3b91aa40594968faae1131e84c3c8418
→ exactly one implementation commit. The exact diff touches only
config/model-families.toml, tests/unit/test_compact_pair_loop.py, and
tests/unit/test_model_families_config.py; 21 insertions, 4 deletions;
git diff --check is clean.

$ semantic TOML comparison of base and head
→ only active_author_models and active_reviewer_models change, each by the
exact addition {claude-opus-5, claude-fable-5}; no removals. active_families
remains exactly {claude, gpt}. provider prefixes, the family registry, display
aliases, schema version, and historical cutover are unchanged.

$ current-admission and evasion matrix at f51abfdf
→ claude-opus-5 and claude-fable-5 are current authors and reviewers;
GPT-to-either pair passes; Opus-to-Fable and every Claude-to-Claude pair fails.
claude-opus-5-thinking-high remains registered as family claude but is neither
a current author nor reviewer. Exact, anthropic-prefixed, and claude-code
decorated forms remain inactive. Gemini display/canonical/provider forms
remain author-only and cannot provide the formal accepting verdict.

$ four re-pointed negative controls plus zero-write reversion control
→ the retired sentinel is false for author admission, reviewer admission, and
GPT-to-retired current-pair admission; compose_request raises the intended
currently-admitted-author error. Adding that sentinel only to the in-process
author/reviewer sets flips all three predicates and makes composition succeed;
restoring the globals returns every result to false. The controls are
non-vacuous and no tracked file was touched.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_codex_protocol_model.py tests/unit/test_model_families_config.py tests/unit/test_compact_pair_loop.py tests/unit/test_ci_admission_gate.py
→ 275 passed in 42.91s.

$ coordination/bin/pipeline-python -m pytest -q
→ 1141 passed for this unchanged exact implementation range.

$ bin/pipeline check
→ exit 0: project smoke, ceremony, placeholder, GO-schema (222 reports), and
architecture checks pass; only pre-existing advisory history remains.

$ bin/pipeline check admission --base f6ce9dca5adb20d9ed5017cce102aa6c888078fe --head f46e037288f1d3f865daa2bcf9e1526ff85a8469
→ candidate executable/worktree: exit 0, structurally admitted.
→ canonical f6ce-derived executable/worktree: exit 1, BLOCKED with the false
same-family diagnostic. Direct model inspection there gives
family(claude-opus-5)=claude, family(gpt-5.6-sol)=gpt, and
models_are_independent=True; only current-author admission differs.

$ code-path trace
→ ci_admission_gate reads report bytes via git show at the selected history,
then calls compact_pair_loop.validate_report. codex_protocol_model binds
_MODEL_FAMILIES_CONFIG from Path(__file__) and freezes CURRENT_* sets at import.
Neither --root nor --head rebinds that policy input. Independent reduced-context
premise attack identified base-tree policy lookup as the unverified premise;
the executable path disproves it.

## Abuse-class assessment

- Self-admission and circular trust: the exact widening has an independently
  reproduced GPT-family verdict; same-family pairs remain refused. The
  Sonnet-authored replacement request also uses a model already active in both
  tested checkouts.
- Negative-control disarmament: all four moved sentinels refuse and flip when
  the guard is deliberately removed in-process.
- Over-widening: the allowlist delta is exactly Opus 5 and Fable 5. Gemini/AGY
  gains no reviewer admission and active families stay Claude plus GPT.
- Retired-ID resurrection: claude-opus-5-thinking-high and decorated variants
  remain inactive.
- Historical re-familying: the actual cutover is unchanged and ancestral; no
  registry, alias, or provider-prefix entry changes.
- Authority conversion: this NITS report admits only the reviewed exact range.
  It grants no push, merge, release, spend, destructive, live-data, or other
  effect authority. No implementation edit or external effect was performed.

Cursor at send: cursorless
