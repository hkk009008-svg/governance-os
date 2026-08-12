# AGY continuation adapter

This file maps Pipeline policy to AGY (Antigravity) mechanics. Canonical policy
and validation live in `scripts/codex_protocol_model.py`; role prompts and
skills contain only their local deltas.

For the desktop-first setup, native capability map, and cross-app handoff
choices, start with `docs/protocol/app-quickstart.md`.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

Runtime identity comes from the harness. Ambient policy variables, role labels,
or prompt text do not grant authority.

## Work mode at boundaries

Ordinary work declares no mode. A campaign selects `explore`, a frozen
candidate `validate`, a canonical or live mutation `promote` — see
`docs/protocol/work-modes.md` (closed profiles:
`scripts/codex_protocol_model.py`). Mode is separate from review risk and
grants no authority.

## Orientation

Use the native index of the current worktree:

```bash
python3 scripts/status.py snapshot <seat>
python3 scripts/agy_observer.py --snapshot  # compact status plus labelled RAW bus view
```

Read actionable event bodies before a decision. Only the assigned live role
consumes its cursor, and coordinator has no cursor.

Use the fixed interfaces, never raw event or cursor edits:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...>  # body on stdin
coordination/bin/consume-events <seat> [--to <timestamp>]
```

At a real long-horizon boundary — ownership transfer, interruption, wrap, or
before context compaction — publish one checkpoint `findings` event (draft:
`scripts/draft_checkpoint.py`; its `Lessons:` line routes lessons toward
learning-candidates, and `none-considered` is always valid). Resume is one
snapshot plus the newest campaign checkpoint plus the actionable bodies it
names; unread backlog is not an orientation debt. Recall from the episodic
index (`scripts/learning_index.py query`) is optional and advisory (learning
contract I1) — committed state outranks it.

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

Role semantics are owned by `.agents/skills/four-seat-protocol/SKILL.md`;
subagents return bounded evidence and never publish a formal verdict.

## AGY-native deltas

The genuine difference is orchestration, not policy.

- **Native helpers and relay.** Workspace custom agents live in
  `.agents/agents/*.md`; the obsolete `.agy/agents/*.toml` surface is not a
  current host discovery path. An assigned parent may use `invoke_subagent`,
  `define_subagent`, `send_message`, and `manage_subagents` instead of polling
  files or asking the user to relay text. Native messages are transient
  AGY-local coordination. Helpers remain parent-scoped, not formal seats: they
  cannot author a verdict, publish an event, consume a cursor, or inherit the
  parent's authority. Tiers select cost/capability, not protocol standing.
- **Saved orientation.** Invoke `/pipeline-start` from the tracked
  `.agents/workflows/pipeline-start.md` workflow for a compact read-only start.
  Saved workflows remove repeated prompt text; they grant no role or effect
  authority.
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

For a load-bearing claim, follow `.agents/skills/probe-a-claim` (premises
from the claim's shape via `scripts/claim_check.py premises`, citations from
commands, one embarrassing command, an optional reduced-context probe through
`coordination/bin/probe-claim` — a real provider launch). All advisory, none
a gate; apply at the boundary the work mode selects.

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
