# Experiment record — connected-tool skill discovery (2026-08-15)

> **Historical record of UNLANDED work — not reproducible from a clone.**
> Every artifact this record exercises is deliberately absent from the
> committed tree: `.agents/skills/route-connected-tools/`, its `.claude`
> stub, `tests/skill_packs/pack-003-connected-tool-routing.json`, and
> `pack-004-connected-tool-stub-routing.json` are all ignored by
> `.gitignore:127-137`, which explains why — committing the packs without the
> skills made a green suite unreproducible from a clone twice, both times via
> `git add -A`. This document was swept in by that same reflex. Read the
> result below as an observation someone made in a working tree that is not
> this one; do not cite it as repository evidence. Landing the work means
> committing the skills and the packs together and deleting that ignore block
> in the same change, at which point this banner comes off.

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
