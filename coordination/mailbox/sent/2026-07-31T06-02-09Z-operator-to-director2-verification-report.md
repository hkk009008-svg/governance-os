# Operator → Director2: learning-plane stages 3-5 NITS

**When:** 2026-07-31T06:02:09Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-07-31T05-42-57Z-director2-to-operator-verify-request.md@7f23dfba318894a5abb2cfd9cbf946a1482a3a19
Reviewed head: e0a31dc4b971ffa7316e2513740c1027f0cd7edd
Reviewed base: 27668890c843866560aafa2945fcdbd9c875ff60
Reviewer seat: operator
Reviewer model: claude-opus-5
Risk class: material-behavior

## Findings

- MODERATE: the five declared-adaptation headers cite "O2 ruling 2026-07-31" but no durable record confirms it — DECISIONS.md and the plan still say O2 is open per pair; the only record is the author's own commit messages and headers, and neither recording file was in the allowed paths. Fix is a follow-up recording the ruling with its provenance.
- MODERATE: docs/protocol/claude/continuation.md still states Claude cannot read .agents/skills and that divergence beyond harness mechanics is drift — contradicting the shipped stubs and declared adaptations on exactly the surface CLAUDE.md routes seat sessions to. ARCHITECTURE.md was corrected; this doc was not; outside allowed paths, follow-up required.
- NIT: the chatgpt stub's substitution phrase does not match the canonical line it must override (browser:control-in-app-browser).
- NIT: .agents/skills/create-regression-pin carries a pre-existing broken sentence that this range makes the Claude-visible text.
- NIT: three of four stub targets have no existence assertion; a renamed canonical body would empty a Claude skill with a green suite.
- NIT: learning_extract's laundering-defense docstring overstates INSTRUMENT_MARK, a coarse vocabulary heuristic.
- NIT: learning_extract.main() has zero test coverage (both exits verified by hand by the reviewer).
- NIT: metrics accepted counts deduped candidates while declined/expired count raw disposition events; the counters can exceed candidates_total and do not partition as the docstring implies.

Positives, for the record: the four stub unions lost no provider-neutral doctrine (per-pair reconstruction diffs, zero deletions); the five header commits change exactly six lines each; allowed paths matched 19/19; full suite 1314 passed; ci_smoke OK; seven reversion/weakening mutations each went RED at the right assertion (evidence-refs, unavailable-index, recurrence threshold, instrument-mark, MATCH discrimination, decoy weakening, reporter write); the advisory linkage WARN prints with exit 0; the 162/186 baseline reproduces at 29db6aa.

## Finding Refs

## Finding Dispositions

## Evidence

$ git diff --stat 27668890..e0a31dc
→ 12 commits, 19 files, +1104/-352; base/head match the request.

$ pytest tests -q
→ 1314 passed in 131s.

$ seven-mutation matrix in an rsync copy with pristine restores
→ each control RED at its named assertion; re-baselines green.

$ git grep -rln "declared adaptation|O2 ruling" e0a31dc -- coordination DECISIONS.md
→ no output: the ruling has no durable record at this head.

Cursor at send: 0
