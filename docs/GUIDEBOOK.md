# Pipeline guidebook — using this repository

> Task-oriented walkthrough, not an authority source. `AGENTS.md` is the
> binding contract, `ARCHITECTURE.md` records verified facts, and executable
> code wins when this guide drifts — fix the guide in the same change that
> exposes the drift. The complete reference map (every file, flow, and
> failure state) is `docs/REPOSITORY-MANUAL.md`; this guide walks the paths
> you actually take, in the order you take them.

## 1. What you are using

Pipeline is a governance kernel, not the product. It keeps the minimum
durable evidence that multi-provider AI work stays honest: committed mailbox
events, exact-range review, checkpoints for long-horizon work, and external
effects that each need their own authorization. Product code lives in
registered target repositories (`governance.toml`); this repository holds the
protocol machinery and its own tests.

Almost everything you do here is one of six walks: an ordinary change, a
formal review, a mailbox action, a long-horizon campaign, an external
effect, or landing work on `main`. Each has a section below.

## 2. First session in a fresh checkout

Each checkout (the main clone and every linked seat worktree) needs its own
virtual environment — `.venv/` is gitignored and does not travel:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Then orient. One command is the whole startup ritual:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/status.py snapshot
```

Reading the snapshot:

- `Git:` — commit, branch, dirty count. Confirm you are where you think.
- `Unread:` — per-seat unread mailbox counts. A large number is normal
  history, not orientation debt; nothing obliges you to drain it.
- `Request:` — the newest pending verify-request, if any, and its assigned
  reviewer.
- `Checkpoint:` — the newest committed campaign checkpoint (`none` when no
  campaign is open, `unavailable` when the projection cannot be read).
  Resume = this snapshot plus that checkpoint; see section 7.
- `Gate: PASS/WARN/FAIL` — FAIL names a structural blocker; WARN with
  grandfathered immutable-history advisories is the normal steady state.
- `Next:` — the one suggested next action.

Deeper diagnostics when something looks wrong:
`.venv/bin/python scripts/check_coordination.py`.

## 3. Sixty seconds of classification before you start

Three independent questions shape every task (the closed decision surfaces
live in `AGENTS.md`, `docs/protocol/work-modes.md`, and
`scripts/codex_protocol_model.py`):

| You are about to… | Walk | Ceremony required |
|---|---|---|
| Read code, answer a question | just read | None. Reads are always free. |
| Fix docs, tests, or local behavior reversibly | section 4 | None — no seat, no mode, no mailbox event. |
| Change behavior somebody relies on | section 4, then 5 | Failing test first; non-author review of the exact range if material. |
| Touch hook policy, fixed writers, launchers, skills, CI, review machinery | section 5 | High-risk compact pair: different model family plus abuse-class analysis. |
| Publish or consume mailbox state | section 6 | Assigned sender and publication authority. |
| Start, pause, or resume a multi-session campaign | section 7 | `explore` mode at the boundary; checkpoint events. |
| Push, merge, lock, consume a cursor, launch a provider, spend money | section 8 | One separate exact approval per effect, every time. |

Two rules that prevent most over-ceremony: ordinary work declares no work
mode (a mode object exists only at a campaign boundary), and no seat is
needed merely because an edit exists. Roles exist only on explicit
assignment.

## 4. The ordinary change walk

The default path for direct, reversible, repository-local work:

```bash
# 1. Fresh eyes on the exact state
git status --short --branch && git log --oneline -5

# 2. Inspect before editing: definitions, callers, siblings
rg -n "the_symbol_you_are_changing" scripts/ tests/

# 3. Behavior change? Write the failing test first
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_the_area.py -q

# 4. Implement the smallest change, then focused verification, fresh
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_the_area.py -q

# 5. Inspect the exact diff before committing; stage explicit paths
git diff
git add scripts/the_file.py tests/unit/test_the_area.py
git commit -m "fix(area): what and why"
```

Docs-only changes: run `.venv/bin/python scripts/check_doc_claims.py` and
`.venv/bin/python scripts/check_placeholders.py` instead of pytest. Run the
completion aggregate `.venv/bin/python scripts/governance_verify_all.py`
only when the change touches governance/runtime topology or an
`ARCHITECTURE.md` invariant — it is not a per-edit ritual.

Stop here for ordinary work. Committing locally is the end of the walk;
landing on `main` is section 9.

## 5. Formal review: the compact pair

Triggered by risk, not by habit: material behavior changes need non-author
review of the exact committed range; authority surfaces (hook policy, fixed
writers, launchers, executable composition, trust-granting schemas) also
need a different model family and an explicit abuse-class assessment.
Classification criteria: `docs/protocol/agents/risk-classes.md`.

1. Commit the candidate range. Note base and head.
2. Compose the request body (validates identities, range, and risk):

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/compact_pair_loop.py \
  compose-request --repo-root . --author director --author-model <model-id> \
  --operator operator --risk-class material-behavior \
  --base <base-rev> --head HEAD <<< "One-paragraph outcome statement."
```

   High-risk adds `--risk-class high-risk-control` and at least one
   `--abuse-class "…"` bullet.
3. Publish it as a `verify-request` event (section 6) and commit the staged
   event path.
4. The assigned Operator reviews the exact committed range — in the Cursor
   app, the pinned Operator chat runs `/review-next`, which resolves the
   newest pending request, refuses same-model review, and materializes the
   exact reviewed head in scratch.
5. The Operator publishes one `verification-report`: GO, NITS, or FAIL,
   bound to that request and range. Authors never review their own work.
6. FAIL remediation is a new range and a new request with supersession or
   remediation binding — the old report is never rewritten.

A GO accepts the bound range and nothing else. It does not authorize push,
merge, or any other effect.

## 6. The mailbox

Durable coordination state is committed files under
`coordination/mailbox/sent/`, named
`<UTC-stamp>-<from>-to-<to>-<kind>.md`. The accepted kinds are the registry
`coordination/mailbox/kinds.txt`. Reading is free — open the files or use
`git log -- coordination/mailbox/sent/`.

Writing goes through fixed front doors only:

```bash
# Publish (body on stdin; stages the event, never commits — you commit it)
coordination/bin/send-event <from> <to> <kind> <subject...>

# Advance your own seat cursor (assigned pair seats only)
coordination/bin/consume-events <seat>
```

In the Cursor app the bound-seat wrappers are `coordination/bin/cursor-publish`
(with `--body-file`) and `coordination/bin/cursor-consume`.

Rules that surprise people: never write into `sent/` directly and never call
`scripts/mailbox_writer.py` yourself — both are denied by policy;
publication requires an assigned sender (a readiness session cannot lawfully
publish, and even asking `send-event` for its help text is denied there —
read the script header for usage); coordinators observe without consuming;
the writer stages but the commit is your separate, deliberate act.

## 7. Long-horizon campaigns: checkpoints and resume

Chat memory does not survive compaction, transfer, or interruption. Durable
state does. At a real boundary — ownership transfer, interruption,
pre-compaction, campaign wrap — publish one checkpoint:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/draft_checkpoint.py \
  --scratch .pytest-verify-tmp/ckpt --checkpoint <campaign-slug> \
  --boundary wrap --objective "…" --accepted-scope "…" --owner <seat> \
  --base <40-hex-base> --verification-status "what ran, fresh" \
  --blockers none --next-action "the one next executable action"
```

The tool drafts to scratch and never publishes; review the draft, then
publish it as a `findings` event via `send-event` (section 6). A malformed
checkpoint is refused at publication. The required `Lessons:` field routes
lessons toward learning-candidates; `none-considered` is always a valid
answer after actually considering it — there is no quota.

Resuming is two reads, not an archaeology dig: run the snapshot (section 2)
and open the checkpoint it names on the `Checkpoint:` line. Recalled chat
memory stays advisory; current Git and committed event bodies outrank it.

## 8. External effects

Push, merge, fetch/pull, lock claim/release, cursor consumption, provider
launch, paid spend, live-data mutation: each needs separate exact authority
for the executor, target, effect, and scope, at point of use. No role, GO
verdict, mode, or schema ever grants one. In the Cursor app this surfaces
as one in-app approval card per effect — that card is the authority for
exactly that command, and nothing else is. Transport ambiguity (a push that
may or may not have landed) is reported, never converted into success.

## 9. Landing work on main

Current practice is topic branches and pull requests:

```bash
git switch -c cursor/<slug>          # from the current tip
git add <explicit paths> && git commit
git push -u origin cursor/<slug>     # separate approved effect
gh pr create --title "…" --body "…"
```

CI runs smoke (`governance_verify_all.py`), the full pytest matrix on
Python 3.11–3.13, a hermetic Linux job, advisory lint, and — only when the
range touches an authority surface (`AUTHORITY_SURFACES` in
`scripts/ci_admission_gate.py`: broad prefixes including `scripts/`,
`docs/protocol/`, the skill trees, CI itself, `AGENTS.md`, `README.md`) —
a risk-aware admission job that requires committed GO/NITS high-risk
compact-pair coverage of those commits. Documentation outside those
prefixes lands without it. Green gates prove what they executed and grant
no authority; merging is the owner's separate effect.

## 10. Cursor Desktop seats — the daily runtime

Condensed from `docs/protocol/cursor/continuation.md`, which is
authoritative:

- The standing pair is two pinned top-level chats: Director in the
  `cursor-seat/director` linked worktree, Operator in `cursor-seat/operator`,
  with different model families. Everything else is cold capacity.
- Binding is automatic: the newest chat opened in a seat worktree registers
  at `sessionStart` (user-local `~/.cursor/pipeline-app-seats.json`). No
  init message. An older chat in the same worktree silently loses the seat.
- Every other chat is a readiness bridge: it reads everything, writes
  scratch freely, and gets one in-app approval per governed mutation. Native
  file-tool edits are denied there — use approved shell commands instead;
  this is the designed path, not an error.
- Hard denies (no approval offered): direct mailbox/lock/runtime writes,
  direct fixed-writer calls, switching a protected `cursor-seat/*` ref, seat
  impersonation by subagents.
- Do not switch branches on a dirty tree inside a seat chat; the app may
  auto-commit a checkpoint of every dirty file. Branch surgery happens in a
  terminal with explicit user authority.
- The one manual handoff in the review loop is activating the Operator chat
  and running `/review-next`.

## 11. Memory, lessons, and skills

The learning plane is git-native and advisory
(`docs/protocol/learning/contract.md` is the contract):

- A lesson becomes a draft via `scripts/learning_extract.py` (scratch-only,
  evidence triggers only — user correction, contradiction, recurrence,
  measured improvement), then a `learning-candidate` mailbox event, then a
  non-producer disposition (`accepted`/`declined`/`expired`).
- Promotion into canonical state (including any skill edit) is an ordinary
  reviewed compact-pair change. There is no autonomous skill write.
- Skills live in `.agents/skills/<name>/SKILL.md` (canonical) with Claude
  discovery stubs in `.claude/skills/`. Authoring one? Load
  `.agents/skills/writing-skills/SKILL.md` first — evaluation pack under
  `tests/skill_packs/` before body.
- After using a named skill, append one advisory `skill-use` row to
  `logs/learning/outcomes.jsonl` (schema:
  `docs/protocol/learning/skill-use.md`). Counts never bind lifecycle.

## 12. When something refuses

| Symptom | Meaning | Do |
|---|---|---|
| File edit denied in chat | Readiness posture; only bound Directors edit natively | Use an approved shell mutation, or work from the bound seat chat |
| `cursor-seat/*` switch denied | Protected ref; no approval path from an unbound session | Switch from the bound seat chat or your own terminal |
| `send-event` refuses or is denied outright | Unassigned sender, unknown kind, malformed body — or readiness posture | Check seat assignment and `kinds.txt`; publication needs an assigned seat |
| Snapshot `Gate: FAIL` | Structural coordination blocker | `scripts/check_coordination.py` names it; repair before other work |
| Snapshot advisories about grandfathered history | Known immutable-history exceptions | Normal steady state; not yours to fix |
| Admission gate red on a PR | Range touches an authority-surface prefix | Attach compact-pair review coverage, or the owner decides at merge |
| A gate is green but the claim feels unproved | Gates prove only what they execute | Say what was not proved; see `probe-a-claim` skill before writing "verified" |

Deeper: the troubleshooting table in `OPERATIONS.md` and the failure-model
table in `docs/REPOSITORY-MANUAL.md`.

## 13. Which document, when

| Genre | Document |
|---|---|
| Binding agent contract | `AGENTS.md` |
| This walkthrough | `docs/GUIDEBOOK.md` |
| Complete reference map | `docs/REPOSITORY-MANUAL.md` |
| Commands and troubleshooting | `OPERATIONS.md` |
| The daily loop, compressed | `RUNBOOK-DAILY.md` |
| Verified system facts | `ARCHITECTURE.md` |
| User-principal intent | `docs/PROGRAM-MANUAL.md` |
| Decision history | `DECISIONS.md` |
| Work phases | `docs/protocol/work-modes.md` |
| Desktop app setup | `docs/protocol/app-quickstart.md` |
| Provider mechanics | `docs/protocol/{codex,claude,agy,cursor}/` |
