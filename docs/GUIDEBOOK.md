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

The virtual environment lives in the **primary checkout only**. `.venv/` is
gitignored and does not travel, and linked worktrees deliberately carry no
duplicate — `bin/pipeline` resolves the primary checkout's interpreter from a
worktree too:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Then orient. One command is the whole startup ritual:

```bash
bin/pipeline status snapshot
```

`bin/pipeline` is the single entry point; `bin/pipeline --help` lists every
verb. It clears `GIT_INDEX_FILE` and resolves the interpreter itself, so no
`env -u GIT_INDEX_FILE .venv/bin/python …` prefix is needed anywhere below.

Reading the snapshot:

- `Git:` — commit, branch, dirty count. Confirm you are where you think.
- `Unread:` — the retired per-seat cursor counts, printed under the header
  `Unread (retired seat cursors, historical)`. A large number is normal
  history, not orientation debt; nothing obliges you to drain it. The two live
  roles, `author` and `reviewer`, are cursorless.
- `Request:` — the newest pending verify-request, if any, and its assigned
  reviewer.
- `Checkpoint:` — the newest committed campaign checkpoint (`none` when no
  campaign is open, `unavailable` when the projection cannot be read).
  Resume = this snapshot plus that checkpoint; see section 7.
- `Gate: PASS/WARN/FAIL` — FAIL names a structural blocker; WARN with
  grandfathered immutable-history advisories is the normal steady state.
- `Next:` — the one suggested next action.

Deeper diagnostics when something looks wrong:
`bin/pipeline check coordination`.

## 3. Sixty seconds of classification before you start

Three independent questions shape every task (the closed decision surfaces
live in `AGENTS.md`, `docs/protocol/work-modes.md`, and
`pipeline/codex_protocol_model.py`):

| You are about to… | Walk | Ceremony required |
|---|---|---|
| Read code, answer a question | just read | None. Reads are always free. |
| Fix docs, tests, or local behavior reversibly | section 4 | None — no seat, no mode, no mailbox event. |
| Change behavior somebody relies on | section 4, then 5 | Failing test first; non-author review of the exact range if material. |
| Touch hook policy, fixed writers, launchers, skills, CI, review machinery | section 5 | High-risk compact pair: different model family plus abuse-class analysis. |
| Publish or consume mailbox state | section 6 | Sender must be `author` or `reviewer`; publication authority. |
| Start, pause, or resume a multi-session campaign | section 7 | `explore` mode at the boundary; checkpoint events. |
| Merge, lock, consume a cursor, invoke a peer CLI, spend money | section 8 | One separate exact approval per effect, every time. |

Two rules that prevent most over-ceremony: ordinary work declares no work
mode (a mode object exists only at a campaign boundary), and no role is
needed merely because an edit exists. Roles exist only on explicit
assignment, and there are exactly two: `author` and `reviewer`.

## 4. The ordinary change walk

The default path for direct, reversible, repository-local work:

```bash
# 1. Fresh eyes on the exact state
git status --short --branch && git log --oneline -5

# 2. Inspect before editing: definitions, callers, siblings
rg -n "the_symbol_you_are_changing" pipeline/ tests/

# 3. Behavior change? Write the failing test first
coordination/bin/pipeline-python -m pytest tests/unit/test_the_area.py -q

# 4. Implement the smallest change, then focused verification, fresh
coordination/bin/pipeline-python -m pytest tests/unit/test_the_area.py -q

# 5. Inspect the exact diff before committing; stage explicit paths
git diff
git add pipeline/the_file.py tests/unit/test_the_area.py
git commit -m "fix(area): what and why"
```

Docs-only changes: run `bin/pipeline check docs` and
`bin/pipeline check placeholders` instead of pytest. Run the completion
aggregate `bin/pipeline check` only when the change touches
governance/runtime topology or an `ARCHITECTURE.md` invariant — it is not a
per-edit ritual.

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
bin/pipeline review validate compose-request --repo-root . \
  --author author --author-model <model-id> \
  --operator reviewer --risk-class material-behavior \
  --base <base-rev> --head HEAD <<< "One-paragraph outcome statement."
```

   The flag is still spelled `--operator`; its value must be `reviewer`,
   because the writer admits exactly two senders and two recipients
   (`author`, `reviewer`, plus `all` as a broadcast target). Composing with a
   retired seat name succeeds and then fails at publication, which is the
   worst place to find out.

   High-risk adds `--risk-class high-risk-control` and at least one
   `--abuse-class "…"` bullet.
3. Publish it as a `verify-request` event (section 6) and commit the staged
   event path.
4. The assigned reviewer reviews the exact committed range and independently
   verifies the requested claims.
5. The reviewer publishes one `verification-report`: GO, NITS, or FAIL,
   bound to that request and range. Authors never review their own work.
6. FAIL remediation is a new range and a new request with supersession or
   remediation binding — the old report is never rewritten.

A GO accepts the bound range and nothing else. It does not authorize merge
or any other external effect.

## 6. The mailbox

Durable coordination state is committed files under
`coordination/mailbox/sent/`, named
`<UTC-stamp>-<from>-to-<to>-<kind>.md`. The accepted kinds are the registry
`coordination/mailbox/kinds.txt`. Reading is free — open the files or use
`git log -- coordination/mailbox/sent/`.

Writing goes through fixed front doors only:

```bash
# Publish (body on stdin; stages the event, never commits — you commit it)
bin/pipeline mail send <from> <to> <kind> <subject...>

# Advance a retired seat cursor (historical seats only; roles are cursorless)
bin/pipeline mail consume <seat>
```

Rules that surprise people: never write into `sent/` directly and never call
`pipeline/mailbox_writer.py` yourself — both are denied by policy;
publication requires an assigned sender, and a **new** event may only be sent
by `author` or `reviewer` and addressed to `author`, `reviewer`, or `all`
(the six retired seat names still parse, so committed history stays
readable, but they cannot be written); a new event's kind must be one of the
eight the writer admits (`decision`, `dispatch-claim`, `findings`,
`learning-candidate`, `measurement-report`, `verification-report`,
`verify-addendum`, `verify-request`) — conversation goes through peer
invocation (`docs/protocol/peer.md`) instead, which leaves a receipt rather
than an event; the writer stages but the commit is your separate, deliberate
act.

## 7. Long-horizon campaigns: checkpoints and resume

Chat memory does not survive compaction, transfer, or interruption. Durable
state does. At a real boundary — ownership transfer, interruption,
pre-compaction, campaign wrap — publish one checkpoint:

```bash
bin/pipeline checkpoint \
  --scratch .pytest-verify-tmp/ckpt --checkpoint <campaign-slug> \
  --boundary wrap --objective "…" --accepted-scope "…" --owner <role> \
  --base <40-hex-base> --verification-status "what ran, fresh" \
  --blockers none --next-action "the one next executable action"
```

`--owner` must equal the sender that will publish it, so it is `author` or
`reviewer`. The tool drafts to scratch and never publishes; review the draft,
then publish it as a `findings` event via `bin/pipeline mail send`
(section 6). A malformed checkpoint is refused at publication. The required `Lessons:` field routes
lessons toward learning-candidates; `none-considered` is always a valid
answer after actually considering it — there is no quota.

Resuming is two reads, not an archaeology dig: run the snapshot (section 2)
and open the checkpoint it names on the `Checkpoint:` line. Recalled chat
memory stays advisory; current Git and committed event bodies outrank it.

## 8. External effects

Merge, fetch/pull, lock claim/release, cursor consumption, peer invocation
(`docs/protocol/peer.md` — running the other CLI is a provider launch and
paid spend), paid spend generally, live-data mutation: each needs separate
exact authority for the executor, target, effect, and scope, at point of use.
No role, GO verdict, mode, or schema ever grants one. Transport ambiguity is
reported, never converted into success.

Push is deliberately **not** on that list — see `AGENTS.md` item 6, which
records why the obligation was dropped rather than left standing as prose the
harness never enforced.

## 9. Landing work on main

Current practice is topic branches and pull requests:

```bash
git switch -c codex/<slug>           # from the current tip
git add <explicit paths> && git commit
git push -u origin codex/<slug>
gh pr create --title "…" --body "…"
```

CI runs smoke (`governance_verify_all.py`), the full pytest matrix on
Python 3.11–3.13, a hermetic Linux job, advisory lint, and — only when the
range touches an authority surface (`AUTHORITY_SURFACES` in
`pipeline/ci_admission_gate.py`: broad prefixes including `pipeline/`,
`docs/protocol/`, the skill trees, CI itself, `AGENTS.md`, `README.md`) —
a risk-aware admission job that requires committed GO/NITS high-risk
compact-pair coverage of those commits. Documentation outside those
prefixes lands without it. Green gates prove what they executed and grant
no authority; merging is the owner's separate effect.

## 10. Memory, lessons, and skills

The learning plane is git-native and advisory
(`docs/protocol/learning/contract.md` is the contract):

- A lesson becomes a draft via `bin/pipeline learn draft` (scratch-only,
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

## 11. When something refuses

| Symptom | Meaning | Do |
|---|---|---|
| `mail send` refuses | Retired sender or recipient, frozen kind, malformed body — or no assignment | The sender and recipient must be `author`/`reviewer` (`all` may receive); check the kind against the eight in section 6 |
| Snapshot `Gate: FAIL` | Structural coordination blocker | `bin/pipeline check coordination` names it; repair before other work |
| Snapshot advisories about grandfathered history | Known immutable-history exceptions | Normal steady state; not yours to fix |
| Admission gate red on a PR | Range touches an authority-surface prefix | Attach compact-pair review coverage, or the owner decides at merge |
| A gate is green but the claim feels unproved | Gates prove only what they execute | Say what was not proved; see `probe-a-claim` skill before writing "verified" |

Deeper: the troubleshooting table in `OPERATIONS.md` and the failure-model
table in `docs/REPOSITORY-MANUAL.md`.

## 12. Which document, when

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
| Reaching the other CLI | `docs/protocol/peer.md` |
| Provider mechanics | `docs/protocol/{codex,claude}/` |
