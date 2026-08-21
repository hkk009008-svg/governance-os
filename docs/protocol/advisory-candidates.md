# Advisory candidates — thin-evidence rules flagged for later principal review

**Status: audit-only list. NO rule status is changed by this file or by the
CLAUDE.md/AGENTS.md operative-split migration that created it.** This is a parking
list for a *separate, later* advisory-review phase in which the user-principal
decides whether any of these rules should move active → advisory (or be revised),
*with intent*. Until then every rule below remains fully active.

## What "thin evidence" means here

A codified rule whose empirical basis is N=0 (forward-looking codification —
ratified ahead of any real use) or N=1 (a single triggering instance). The
codification threshold for most rules in this repo is N=2; the rules below were
shipped under that bar deliberately (forward-looking ratification or
single-incident response) and are the natural candidates to revisit once more
data accrues.

The authoritative provenance + N-count for every rule lives in
[docs/PROTOCOL-RULES-LOG.md](../PROTOCOL-RULES-LOG.md); this file only *indexes*
the thin-evidence subset. N-counts below are quoted from each rule body's own
"Empirical basis" / "Codified SHA" line (verify against the rule body before
acting).

## Candidates (per the rule bodies' stated empirical basis)

| Rule | Stated evidence at codification | Why thin | Revisit trigger |
|---|---|---|---|
| Rule #17 — Workflow-assisted analysis lanes | N=0 ("forward-looking codification; feature unavailable in current runtime; first dogfood at v5.6") | Ratified ahead of activation; no real use yet | First real `/workflows` run (C4 retro at v5.6) — **fired + discharged 2026-06-09; delisted 2026-07-07 (see review below)** |
| Rule #18 — Doc-maintenance verifier-scoped dispatch | N=0 ("forward-looking: no dogfood result yet — graduation metrics are the first data, post-launch") | Dispatch pattern not yet exercised | First doc-maintenance dispatch; graduation metrics |
| Rule #19 — Live-presence-over-inferred-idle | N=1 (single session's RC1–RC5 + user-reported failure) | Single incident | Recurrence or a clean N=2 incident |
| Rule #20 — Shared-state-accuracy | N=1 (same session as #19: RC3 + RC4) | Single incident | Recurrence; M2 hook validation in the field |

## Out of scope for this file

- Changing any status (no active → advisory here).
- Retiring/deleting rules.
- Re-litigating the N=2 codification threshold.

Anything in those categories belongs to the dedicated advisory-review phase, driven
by the user-principal.

## Advisory review 2026-07-07 (user-principal verdicts)

Evidence for this review was gathered read-only on 2026-07-07. This clone's own
git history begins 2026-06-30 @ `18cf325`; events dated before that (e.g. the
2026-06-09 v5.6 retro cited below) are inherited documentation carried in the
transfer bundle, not activity in this clone.

| Rule | Trigger evidence at review | Verdict |
|---|---|---|
| Rule #17 | Trigger FIRED and already discharged: v5.6 dogfood retro 2026-06-09, "C4 DISCHARGED" at docs/protocol/claude/director-operator.md:1160; ~17–18 distinct `wf_*` run IDs cited at director-operator.md:1166-1170; retro verdict "net-positive and retained as-is" (director-operator.md:1192-1193). Further post-retro runs recorded at docs/PROTOCOL-RULES-LOG.md:589,729,736-737,743 and pipeline/check_coordination.py:74,222. N today ≥ 18 (was N=0). | Keep fully active; **DELISTED** from this parking list (graduated — no longer thin-evidence, N≥18) |
| Rule #18 | Trigger NOT fired: N=0 unchanged; no dated dispatch record repo-wide (every grep hit is the rule's own definition/index: director-operator.md:1215-1323, agents/director-operator.md:925-1013, advisory-candidates.md:29, program-manual-guide.md:106, migration-map-claudemd-split.md:40,109,185). Graduation metrics require N≥3 dispatches (director-operator.md:1289-1295); none logged. | Keep fully active; stays listed, trigger unchanged |
| Rule #19 | Trigger PARTIAL: no clean recurrence of the RC1–RC5 failure mode post-codification; related sibling incident "Candidate #9" (2026-06-09) at docs/PROTOCOL-RULES-LOG.md:560-594 is explicitly NOT counted toward Rule #19's N=2 per that log's own criterion (lines 576-580). N=1 unchanged. | Keep fully active; stays listed, trigger unchanged |
| Rule #20 | Trigger NOT fired: no post-codification recurrence of RC3/RC4-type shared-state failures; the M2 hook fix was validated on controlled data only (director-operator.md:1429-1433), never in the field. N=1 unchanged. | Keep fully active; stays listed, trigger unchanged |

Cross-cutting fact noted during the review: concurrent seats have never run in
this clone — coordination/presence/ holds only today's director-heartbeat.ts
(2026-07-07T01:52:26Z @ `4a74e10`); mailbox `sent/` + `archive/` hold only
`.gitkeep`. 4-seat operation was first activated today (ADR-009), so Rules
#19/#20 now begin receiving real field exposure going forward.

No rule status or HARD/SOFT tag changed in any rule body — all four verdicts
above are "keep active" (Rule #17's delisting is a parking-list correction, not
a status change to the rule itself). Because nothing moved to advisory, no
edits to docs/protocol/{claude,agents}/director-operator.md were needed. The
authorizing record for this review is DECISIONS.md ADR-011.
