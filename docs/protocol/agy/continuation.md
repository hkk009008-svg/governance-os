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
python scripts/agy_observer.py --snapshot  # compact status plus labelled RAW bus view
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
- `scripts/agy_seat_launcher.py` preserves ordinary process state and the
  explicit `AGY_API_KEY` credential, while dropping ambient provider, Git, and
  other `AGY_*` identity or project state. Its live model listing fails closed
  on an error or on a successful response containing no model IDs.
- `scripts/agy_observer.py --snapshot` combines two clearly labelled read-only
  views: the compact authority-aware status snapshot and the raw, unverified
  threeway event-bus summary.
- `scripts/agy_emit.py --dispatch` retains its historical CLI spelling but only
  prints a follow-up launch hint. It never executes that command or proves a
  seat was dispatched.

Role deltas match the shared contract: Director owns an accepted outcome and
submits its actual committed range; Operator may implement but stays non-author
when reviewing; Coordinator observes and mediates without approving routes or
authoring production work; subagents return bounded evidence and never publish
a formal verdict.

## AGY-native deltas

The genuine difference is orchestration, not policy.

- **Native helpers.** An assigned parent may delegate bounded work with
  `define_subagent` / `invoke_subagent` rather than polling files. These
  helpers are parent-scoped, not formal seats: they return evidence locally
  and cannot author a verdict, publish an event, consume a cursor, or inherit
  the parent's authority. Tiers select cost/capability, not protocol standing.
- **Workspace artifacts.** A subagent may keep working notes under
  `.agents/<agent_folder>/`. These are scratch inputs, not protocol events:
  they grant no authority, are not a mailbox, are not durable protocol state,
  and must not be mistaken for a handoff. Durable inter-seat speech goes
  through `coordination/bin/send-event` like every other side. Prefer returning
  evidence to the parent over materializing a file.
- **Native browser and consultation.** The in-app browser is free for research
  and testing at the session's discretion. Optional ChatGPT Pro consultation is
  parent-owned and advisory: follow
  `.agents/skills/chatgpt-pro-consultation/SKILL.md`; it grants no protocol or
  side-effect authority.

## Work from skills; route new lessons through candidates

Before starting, check `.agents/skills/` for a skill that covers the work and
follow it. `prove-a-control` before claiming any guard, gate, or negative
control holds. `create-regression-pin` before deferring a confirmed defect.
`seat-operator` before issuing a verdict.

Current code and higher-priority instructions remain controlling. If a loaded
skill conflicts with either, stop relying on it and record the conflict in the
task evidence; do not silently work around it. Correct canonical skill bytes
only when the current accepted task authorizes that correction and its required
review completes.

Finish the scoped task before extracting a lesson. Then draft and, only with the
applicable publication authority, publish an evidence-backed
`learning-candidate` with truthful provider scope. There is no canonical skill
creation or edit solely because a lesson arose. Promotion into a canonical
skill is a separately accepted, risk-classed Compact Pair change; the candidate
is evidence for that later decision, not authority to make it.

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
labels. The current local AGY seat configuration is all Gemini; that is a local
configuration fact, not a claim that the installed `agy models` catalog can
never offer another recognized family. Route reviews according to the exact
configured IDs and the executable fail-conservative family result.

Headless review dispatch has two explicit capability scopes. Run
`scripts/harness_preflight.py agy --agy-scope evidence` for read-only exact-range
inspection: it requires `read_file(<resolved repository root>)`, Git
diff/show/status/rev-parse/merge-base, `rg`, and focused pytest grants. Bare
`read_file` is not a valid AGY 1.1.10 grant. Run `--agy-scope publishing` only
when the session is separately intended and authorized to commit and publish;
it adds `git commit` and `coordination/bin/send-event` capability checks.
Publishing is the unchanged full default, so an omitted scope never silently
weakens the old gate. Either result measures capability only, never authority.

AGY settings grants persist into future sessions. Do not add commit,
send-event, or a blanket permission skip merely to gather review evidence. In
headless mode a missing grant may return exit 0 with denial text or no output,
so the live probe requires the exact nonempty artifact from a real read-only
`git rev-parse --show-toplevel --short HEAD` command: the exact two-line root and
HEAD artifact prevents another checkout at the same commit from satisfying the
probe. The canonical form is `<resolved-root>\n<short-head>\n`; leading or
trailing whitespace is a failure. It sanitizes inherited `GIT_*`, pins plan mode,
`gemini-3.6-flash-low`, and low effort. AGY has no working-directory flag, so
the launch binds the exact repository through `--add-dir` and the prompt
requires that same absolute path as the command tool's `Cwd`, with no retry or
sandbox bypass. Every flag precedes the final `--print <prompt>`. When settings
cannot be changed, use
`scripts/harness_preflight.py agy --package-request <path>@<full-sha>` to emit a
bounded tool-less prompt from the committed request and verbatim exact-range
diff. Packaging launches no provider. Its analysis remains advisory until
separately relayed and published through the canonical exact-authority path;
the package itself cannot formalize a verdict. Full commands and grant lists
are in `docs/protocol/threeway/HEADLESS-REVIEW.md`.

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
