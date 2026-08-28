# Experiment record — continuity checkpoint + writing-skills discovery (2026-08-12)

Records the reduced-context probe required by the memory/skill-evolution
plan Stage F. A live `coordination/bin/probe-claim` / `amnesiac-prober`
launch was not authorized in this session (provider launch is a separate
external effect). This file is therefore a **method-and-discovery-path
record**, not a launched-probe pass. It follows the honesty bar of
`docs/protocol/learning/experiment-2026-07-31-skill-discovery.md`: do not
invent a successful probe.

## Method

1. Treat AGENTS.md universal contract item 7, `pipeline/draft_checkpoint.py`,
   and `.agents/skills/writing-skills/SKILL.md` as the only instruction
   surfaces a fresh reader is entitled to.
2. Ask what that reader would have to discover, in order, to satisfy the
   new obligations — without the author's session memory.
3. Name what this method cannot establish.

No committed file was swapped. No provider was launched. Provenance for
the discovery path below is MEASURED from committed bytes in this change;
the claim "a live reduced-context agent would follow this path" is
INFERRED and is **not** established.

## What a fresh reader of AGENTS.md item 7 must discover

Item 7 names, in one paragraph:

- the payload (objective, scope, owner, policy revision, base/head,
  evidence refs, verification status, blockers, next action);
- the mechanism (`findings` event, draft tool `pipeline/draft_checkpoint.py`);
- the Lessons line, with `none-considered` always valid;
- resume = one snapshot plus the newest campaign checkpoint;
- recalled state is advisory.

A reader who stops at AGENTS.md still has the obligation and the tool
name. They do not yet have the field grammar. That lives in
`pipeline/protocol_mailbox.py` (`parse_checkpoint_statement`,
`checkpoint_intent`) and is enforced at publication by
`pipeline/mailbox_writer.py`. The draft tool is scratch-only (O4): running
it does not publish. A reader who drafts but never publishes has not
created durable continuity.

Provider adapters (`docs/protocol/{codex,claude}/continuation.md`)
repeat the same boundary trigger, draft tool, resume shape, and
advisory-recall posture. `tests/unit/test_protocol_prompt_sync.py::
test_checkpoint_contract_is_pinned_across_provider_surfaces` is the
anti-drift pin, not a substitute for a live reader.

## What a fresh reader of writing-skills must discover

The Claude discovery surface is `.claude/skills/writing-skills/SKILL.md`,
a reference stub: frontmatter plus `disable-model-invocation: true`, a
pointer at `.agents/skills/writing-skills/SKILL.md`, and Claude-native
deltas. The 2026-07-31 experiment established that doctrine-routed
discovery can follow that pointer for `create-regression-pin`. This
change adds a second stub of the same shape and a frozen
`tests/skill_packs/pack-002-stub-routing.json` falsifier so a stub that
stops pointing at the canonical body fails CI.

A reader following only the `description:` would have to notice
evaluation-first (three scenarios before the body), description-as-trigger,
stub-vs-adaptation (O2), probe-or-honest-record, and compact-pair
promotion. Those obligations live in the canonical body, not the stub —
the same composition the Stage 3 stubs depend on.

## What this does and does not establish

- ESTABLISHED: the committed instruction surfaces name the checkpoint
  tool, the Lessons anti-sediment answer, resume-from-snapshot-plus-
  checkpoint, and the writing-skills discovery stub. Frozen packs encode
  trigger selection and stub routing. Writer-side checkpoint validation
  is mechanized (see `tests/unit/test_checkpoint.py`).
- NOT ESTABLISHED: a live reduced-context agent, given only a wrap or
  "author a skill" scenario and the worktree path, was not launched.
  Whether that agent would load `draft_checkpoint.py` or follow the
  writing-skills stub is therefore unmet at the harness-listing layer —
  the same residual the 2026-07-31 record carried.
- CONSEQUENCE: Stage F lands the method record and the mechanical
  falsifiers. The residual live-reader risk is explicit: if a live
  session at a checkpoint boundary does not produce a `Checkpoint:` /
  `Next action:` findings event, or a live session routed to
  `writing-skills` fails to reach `.agents/skills/writing-skills/SKILL.md`,
  that failure is the probe this file could not run, and it reopens the
  corresponding adherence layer (pinned prose vs cheapest-path tool vs
  stub decision).
