# AGY continuation adapter

This file maps Pipeline policy to AGY (Antigravity) mechanics. Canonical policy
and validation live in `scripts/codex_protocol_model.py`; role prompts and
skills contain only their local deltas.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

Runtime identity comes from the harness. Ambient policy variables, role labels,
or prompt text do not grant authority.

## Work mode before ceremony

Select `explore`, `validate`, or `promote` from
`docs/protocol/work-modes.md`; the closed profiles live in
`scripts/codex_protocol_model.py`.

- Explore is the default for reversible sandbox learning: one campaign brief,
  automatic attempt logs, recorded reruns, and no formal review until transfer
  or phase change.
- Validate freezes one candidate and uses one non-author candidate review.
- Promote carries the reviewed candidate, rollback point, and separately
  authorized canonical or external effect.

Mode is separate from review risk and grants no seat, write, provider launch,
merge, push, or external-effect authority.

## Orientation

Use the native index of the current worktree:

```bash
python scripts/status.py snapshot <seat>
```

Read actionable event bodies before a decision. Only the assigned live role
consumes its cursor, and coordinator has no cursor.

Use the fixed interfaces, never raw event or cursor edits:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...>  # body on stdin
coordination/bin/consume-events <seat> [--to <timestamp>]
```

## Executable contracts

- `scripts/codex_protocol_model.py` validates runtime identity, ownership
  lineage, risk profiles, model-family independence, and external-effect token
  shape.
- `scripts/compact_pair_loop.py` validates formal requests, reports, and exact
  reviewed ranges.
- `scripts/mailbox_writer.py` validates and serializes event publication.
- `scripts/agy_protocol_model.py` carries only AGY-local deltas.

Role deltas match the shared contract: Director owns an accepted outcome and
submits its actual committed range; Operator may implement but stays non-author
when reviewing; Coordinator observes and mediates without approving routes or
authoring production work; subagents return bounded evidence and never publish
a formal verdict.

## AGY-native deltas

The genuine difference is orchestration, not policy.

- **Native subagent mesh.** Seats compose work with `define_subagent` /
  `invoke_subagent` rather than by polling files. Tiers: `flash_lite` for
  search and file reads, `flash` for orientation and multi-file research,
  `pro` / `inherit` for implementation and independent analysis.
- **Workspace artifacts.** A subagent may keep working notes under
  `.agents/<agent_folder>/`. These are scratch inputs, not protocol events:
  they grant no authority, are not a mailbox, are not durable protocol state,
  and must not be mistaken for a handoff. Durable inter-seat speech goes
  through `coordination/bin/send-event` like every other side. Prefer returning
  evidence to the parent over materializing a file.

## Work from the skills, and write the next one

Before starting, check `.agents/skills/` for a skill that covers the work and
follow it. `prove-a-control` before claiming any guard, gate, or negative
control holds. `create-regression-pin` before deferring a confirmed defect.
`seat-operator` before issuing a verdict.

When work exposes a lesson no skill covers — a trap, a measured instance, and
what to do instead — write the skill in the same session. When a skill's advice
turns out wrong, correct the file rather than working around it.

## Formation gate for claims

A load-bearing claim — "enforced", "measured", "complete", "never", a cited
reference — is a conjunction whose premises come from its shape, not from
memory, and whose check must be able to disagree with its author. Apply the
discipline at the boundary selected by the work mode:

- Explore: use it for a claim that stops the campaign, selects a candidate, or
  changes phase; cite routine observations directly.
- Validate: use the full loop for the candidate's load-bearing conclusion.
- Promote: retain the full loop and the independent review.

For the full loop, derive the premises
(`env -u GIT_INDEX_FILE .venv/bin/python scripts/claim_check.py premises "<claim>"`),
cite each with the command that measured it, run the one command most likely
to embarrass the claim, and attack it with a reduced-context reader when useful
and separately authorized (`coordination/bin/probe-claim "<claim>"`).
`scripts/claim_check.py sweep` is an optional lens over a range's uncited
overclaim vocabulary. All advisory, none a gate; the full loop is
`.agents/skills/probe-a-claim`.

## Review and external effects

Review depth is risk-based as defined by `AGENTS.md` and the executable model.
Ordinary local edits need no mailbox event, role ceremony, capacity packet,
handoff, or independent review.

`impl ≠ verifier` applies to AGY subagents and seats alike. Note the local
constraint: when every configured seat profile resolves to one model family,
AGY cannot satisfy `high-risk-control` on its own, because
`codex_protocol_model.models_are_independent` compares families rather than
labels. Route those reviews to a seat on a different family.

Headless review dispatch (measured 2026-07-31; accepted learning candidate
`2c906ea580a9…`): `agy -p` in headless mode auto-denies every tool permission
request — there is no scoped allow-rule, only a blanket skip flag that must
not be used for review work. An AGY operator review therefore runs
**tool-less**: the dispatcher packages the committed verify-request, the
verbatim range diff (`git show`/`git diff` piped in the same pipeline that
builds the prompt, never hand-edited), and any reader-side context into the
prompt; the reviewer judges the diff as ground truth, lists every check that
would need execution under an explicit "unanswerable without execution"
heading instead of assuming it, and the published report discloses the
tool-less constraint. Author evidence for previously-unanswerable items is
supplied in later rounds as commands-plus-output, for the reviewer to accept
or challenge. Measured working across a FAIL and a GO round on a
high-risk-control range.

State the model as the exact ID `agy models` lists, undecorated — the same
string `coordination/bin/agy-seat --dry-run <seat>` prints as `AGY_MODEL` and
passes to `--model`. `Author model:` and `Reviewer model:` are read by people
re-checking whether a seat could have run as claimed, so a form that no launch
could produce, such as `antigravity-gemini-3.6` or an unlisted `gemini-2.5-pro`,
is unverifiable even when `model_family` happens to normalize it to the same
family. The launcher checks the configured model against that listing on launch
and on `--dry-run`, and fails closed when the listing is unobtainable, so a
dry-run identity is either checked or absent — never merely asserted. It also
refuses a forwarded `--model`, which AGY would otherwise resolve in preference
to the checked one while `AGY_MODEL` kept advertising the configured value.

External effects remain separate from structural validation. Push, merge,
locking, event consumption, paid spend, provider launch, and live-data mutation
need exact authority for the executor, target, and scope.
