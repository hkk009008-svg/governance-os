---
name: writing-skills
description: "Author, revise, or promote a repository skill from observed procedure — evaluation-first (three scenarios before the body), description-as-trigger, stub-vs-adaptation (O2), reduced-context probe before landing, and compact-pair promotion. Use when writing a new skill, changing a canonical SKILL.md, closing a skill TODO, or promoting a procedure candidate into .agents/skills/."
---

# Writing skills

Canonical skill authoring for this repository. There is no autonomous
skill write: a lesson becomes a `learning-candidate`; promotion into
`.agents/skills/` is a separately accepted compact-pair change (contract
I3). Usage counts never bind lifecycle (ADR-067 rejection, reaffirmed).

Codex has no skill-level equivalent of Claude's `disable-model-invocation`;
use this as procedural guidance in the active session, not as a delegation
trigger for a separate model run.

## When

- A repeated procedure is about to become a skill, or an existing skill
  failed in use and needs a revision.
- A transfer-bundle skill TODO is being closed with this repo's real
  inventory (do not invent a domain skill that does not exist).
- A Claude discovery surface is being added or changed.

Do not load this skill to *follow* another skill; load it to *author* one.

## Evaluation first — three scenarios before the body

Write the evaluation pack before the skill body. A skill whose trigger
cannot distinguish itself from decoys is a discovery failure wearing a
filename.

1. Name three natural-language scenarios a fresh session would actually
   type. One must be the happy path; one a near-miss decoy; one a
   stub-routing case if the skill will have a `.claude` stub.
2. Add them under `tests/skill_packs/` as a new `pack-*.json`. Packs are
   frozen: a wrong expectation is superseded by a new pack file, never
   edited in place (`tests/learning_packs/` discipline).
3. Confirm the expected skill's `description:` is the trigger — distinctive
   phrases from the scenarios must appear there, and must not all appear
   in the named decoys.
4. Only then write the body.

## Body constraints

- Keep the body short enough to load on demand. Prefer under 500 lines;
  one level of references, not a tree. The four-seat skill is separately
  pinned at ≤60 lines — do not grow it to fit a footer.
- Frontmatter `name` matches the directory. `description` is the discovery
  surface on every provider; it is not a summary of the body.
- Canonical body lives in `.agents/skills/<name>/SKILL.md`.
- Claude discovery is a **reference stub** (ADR-067 Stage 3) unless the
  pair is a declared provider-native adaptation (O2: the five seat-family
  skills). A stub keeps frontmatter plus `disable-model-invocation: true`,
  points at the canonical path, and names only Claude-native deltas
  (`env -u GIT_INDEX_FILE`, `.venv/bin/python`).
- Do not add a third skill tree, a materializer, or a manifest.

## Probe before landing

A new or revised instruction surface is not landed on author-context
alone. Run the existing reduced-context lane:

```
coordination/bin/probe-claim "<one-sentence claim the skill must survive>"
```

That is a real provider launch and stays separately authorized. The
same-family fallback (`amnesiac-prober`, ONLY the claim sentence) is
weaker by design. Never include the diff, the body, or your reasoning
in the probe prompt — context is contamination (`probe-a-claim`).

If a live probe cannot be launched, record the method, the discovery
path a fresh reader of the description would have to follow, and the
residual risk, as
`docs/protocol/learning/experiment-2026-07-31-skill-discovery.md` did.
Do not invent a passing probe.

The standing stub-routing falsifier: if a live session routed to a
stubbed skill fails to reach the canonical `.agents` body, revert the
stub and reopen ADR-067 Stage 3b/3c. `tests/skill_packs/` encodes that
falsifier for committed stubs.

## Promotion and revision

1. Draft a `learning-candidate` (`pipeline/learning_extract.py`, scratch
   only) whose Target is the canonical skill path. Category `procedure`
   unless the change is a `governance-rule`.
2. Publish only with publication authority. Disposition and promotion
   are the compact pair at the change's risk class (skill-path edits
   are authority surfaces).
3. Revise on observed failure, not on usage counts. A `skill-use` row
   in `logs/learning/outcomes.jsonl` (schema:
   `docs/protocol/learning/skill-use.md`) is advisory slope evidence.
   Helped/hindered/neutral totals never accept, decline, expire, or
   edit a skill.
4. Supersede; do not patch a candidate in place.

## Closeout

At wrap, append one `skill-use` row if this skill (or the skill just
authored) was loaded, or skip with a one-line reason. Then consider a
checkpoint `Lessons:` line (`pipeline/draft_checkpoint.py`);
`none-considered` remains valid.

## Rule maintenance

Observed failure: skills authored from recall, with triggers that do not
select, and stubs that do not reach the canonical body (2026-07-31
skill-discovery experiment; R-SKILL left as a transfer TODO).
Mode/risk: ordinary local authoring; promotion is material-behavior or
high-risk-control when the skill is an authority surface.
Cost: one evaluation pack, one probe-or-honest-record, one compact pair.
Owner: learning plane (ADR-067 / ADR-068).
Re-evaluate: if two consecutive skill landings skip the pack or the
probe-or-record, or if a live stub-routing failure fires the falsifier.
