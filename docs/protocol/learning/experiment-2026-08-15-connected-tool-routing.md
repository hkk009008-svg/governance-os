# Experiment record — connected-tool skill discovery (2026-08-15)

## Claim

A fresh session asked to choose among connected tools should select
`route-connected-tools` for plugin workflows, but `four-seat-protocol` for a
formal Pipeline mailbox handoff.

## Method

The live `coordination/bin/probe-claim` provider launch was not authorized for
this change. The documented same-family fallback was used instead: an
`amnesiac-prober` received only the claim sentence, without the skill body,
diff, expected answer, or author reasoning. The frozen selection and stub
packs were also run through `tests/unit/test_skill_packs.py`.

## Result

The static pack selected `route-connected-tools` for cross-tool evidence work,
selected `four-seat-protocol` for a formal mailbox handoff, and reached the
canonical body through the Claude stub. The reduced-context probe found no
contradiction, but identified fresh-session discovery and overlap precedence
as the load-bearing unverified premise.

## Discovery path and residual risk

A fresh reader should match the natural request against the canonical
frontmatter in `.agents/skills/route-connected-tools/SKILL.md`; Claude should
first discover `.claude/skills/route-connected-tools/SKILL.md` and follow its
pointer to that canonical body. A real fresh harness may still load both
skills, choose by keyword, or omit the new project skill. The cheapest live
falsifier is to submit the exact claim in a scrubbed fresh session and record
which `SKILL.md` it reads first. Until that observation exists, discovery is
structurally checked but not operationally verified.
