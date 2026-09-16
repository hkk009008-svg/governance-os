# Harness analysis and improvement plan (2026-09-15)

Scope: the whole repository at `9d8d956` (main). Question asked: what limits
the three-app harness, what causes friction, what can be removed for better
context management and efficiency, and what can be added for persistent
memory, capacity, and fluid collaboration as one unit. Every finding below is
grounded in the current code or in a command executed on this checkout.
Risk class: this file is an ordinary-local plan (not an authority surface).
Nothing in it grants review, push, merge, or effect authority.

## 0. Executed baseline

| Check | Result |
|---|---|
| `bin/pipeline check` (fresh `.venv`, Linux, Python 3.11) | 264 passed in 40s; FULL CHECK PASS; 2 ADVISORY lines every run |
| `bin/pipeline check admission --base 9644a85 --head 9d8d956` | structurally admitted, 6 authority commits, 0.18s |
| `bin/pipeline status` | 0.56s; Apps `FAIL` ×3 (no `/Applications`); transport ready; `Historical unresolved FAILs: 2` |
| `bin/pipeline preflight` | exit 1: 9 FAIL / 6 PASS on any non-macOS host (handshakes all PASS) |
| `team_status`, `team_wait` from this session | work; store empty; each response carries 353 bytes of fixed prose |
| Orientation doc set (19 files) | 29,214 bytes ≈ 7,300 tokens |
| History | 227 commits in 3 weeks, 51 merges, 78 `review:` commits, 22 formal artifacts |

The harness itself is sound and worth keeping: executable policy outranks
prose, formal artifacts are append-only and bound to exact ranges, Git calls
are hermetic, the suite is fast, and the code base is small (4.6k lines
harness, 4.5k lines tests). The problems are almost all about what happens
*around* that core: cold starts, payload noise, rigid choreography, and
platform coupling. D1–D6 in `DECISIONS.md` stay intact under this plan.

## 1. Findings

### 1.1 Memory: nothing persists between sessions except Git and the mailbox

**F1. Every session pays a full cold start.** A member must read AGENTS.md,
CLAUDE.md (or its app's equivalent), README, ARCHITECTURE, OPERATIONS,
DECISIONS, and `docs/protocol/*` to orient. That set is 19 files, 29 KB,
about 7.3k tokens, and it restates the same five invariants many times:
"exact current user authority" ×8, "exact committed range" ×17, the three
tool names ×28, abuse-class ×14, append-only/retain ×11. Three
`continuation.md` files say the same thing for each app.

**F2. A fresh session cannot resume its inbox.** `team_status` reports
`pending` per member but not the member's acknowledged frontier. Measured on
a throwaway repo (120 inbound messages, 100 acknowledged in session 1):
session 2's `team_wait(after_id=0)` returned ids 1..50, all already
acknowledged, as a 36 KB page of which 43% was envelope and boilerplate.
`team_wait(after_id=100)` was accepted and returned the 20 unread messages in
one call, so the only missing piece is exposing that cursor. The rejection of
`after_id=110` shows the skip guard already works.

**F3. Team memory is per clone.** The store lives in the Git common dir
(`.git/pipeline-team/`). Linked worktrees share it; nothing else does. Every
cloud, CI, or second-machine session starts with `registered=none` (this
session did). Durable cross-clone memory therefore has to live in Git, and
today Git carries only code, docs, and the formal artifacts.

**F4. Rationale is not captured where it would persist.** The two largest
architectural commits (`ccb72b5` "reduce Pipeline to its live harness",
`e25ebc9` "reduce harness friction") have subject lines and empty bodies.
`DECISIONS.md` holds six entries. The best rationale in the repository lives
in mailbox artifacts and module docstrings, which is fine for reviewed ranges
and absent for everything else.

**F5. No working state is visible.** `team_status` shows `last_seen` and a
static capability list. Who is working on what, on which branch or worktree,
blocked on what, and what the previous session left open all have to be
re-sent as free text or are lost. `DECISIONS.md` D3 forbids required
ceremony, not a one-line self-declared focus.

### 1.2 Capacity: transport limits and payload overhead

**F6. Fixed prose is repeated in every payload.** `identity_assurance`,
`cursor_semantics`, `liveness`, and `grants_authority` add 353 bytes to each
`team_wait`/`team_status` response, and `message_view` adds 106 bytes to every
message. A 100-message page carries 10.6 KB of identical strings. The same
sentences are already in the tool descriptions and the `initialize`
instructions, so the per-payload copies are pure context cost
(`pipeline/team_messages.py:198-206,261-268`, `pipeline/team_store.py:286-290`).

**F7. `team_status` always returns the last 50 own-sent previews** (256 bytes
each, `team_messages.py:246-249`). Orientation needs the last few, not 50;
older ones are reachable by `message_id`.

**F8. Waiting is polling, and the poll is heavy.** `team_wait` blocks at most
30 s and, while waiting, reopens the SQLite connection every 50 ms with six
`lstat` calls and three PRAGMAs per iteration (`team_messages.py:136-196`,
`team_store.py:158-173`): about 600 connection opens per 30-second wait. No
member can be woken; collaboration degrades to check-ins at "natural
boundaries".

**F9. No retention.** Messages and delivery receipts accumulate forever;
`team_wait(after_id=0)` replays from the beginning of time (F2 compounds
this).

**F10. Bounded shape.** 16 KB body, `reply_to` only (no thread or topic), no
attachment or reference validation, no search. Long findings must be chunked
by hand or pushed into commits.

### 1.3 Collaboration as one unit

**F11. There is no shared channel.** By design a member never sees the other
two members' exchange (the class-5 abuse assessment protects `team_status`
from disclosing cross-member bodies). The only team-wide surface is
`recipient="all"`, and nothing summarizes it, so team state has to be
re-broadcast to be known.

**F12. Path ownership is prose.** AGENTS.md says "assign one owner to shared
paths"; nothing records or shows the assignment.

**F13. Formal review couples both apps to one branch in lockstep.** The
request must be the only change in a commit whose single parent is Reviewed
head; the report must be the only change directly after the request
(`compact_pair_loop.py:339-351,711-730`). Any interleaved commit breaks the
pair; a revision after review needs a fresh exact-range pair; a squash merge
discards coverage because only a byte-clean merge commit inherits it
(`ci_admission_gate.py:356-386`). Publishing is a four-step manual dance
(compose from stdin, `mail send`, commit with explicit pathspec, push) with
no single command that refuses at the wrong HEAD.

**F14. Model admission churns and can deadlock.** `config/model-families.toml`
changed 14 times in three weeks (top-15 churn) because admission is exact
string match. Executed: a current point-release ID of an admitted family, the
one serving this session, resolves to `family=None, author=False,
reviewer=False`. Because `compose_request` refuses an unadmitted author model,
a session on such a model cannot even author the request that would add it;
the other app must do it, and the change is high-risk-control.

**F15. Review ceremony has no middle gear for harness code.** All of
`pipeline/` plus README, ARCHITECTURE, OPERATIONS, and `docs/protocol/` are
authority surfaces (`ci_admission_gate.py:60-107`). A rendering tweak in
`status_desktop.py` or a wording fix in OPERATIONS.md needs a different-family
high-risk-control review with abuse-class bullets. History shows the cost:
78 of 227 commits are review choreography.

### 1.4 Orientation cost and platform coupling

**F16. `status` re-proves 22 immutable artifacts every time.** Measured: 243
subprocesses per `status`, 239 of them in `inspect_verify_review_state`
(introduction commit, two `show`s, `diff-tree`, `rev-parse`, ancestry, per
artifact). 0.5 s today and linear in artifact count: each review adds two
files and about 20 subprocesses to every future `status` and `check`.

**F17. Readiness is macOS-desktop-only, but CI and cloud are not.**
`check_apps` reads `/Applications/*.app/Contents/Info.plist`;
`native_app_readiness` reads `~/Library/Application Support` and `~/.gemini`.
On this host `preflight` exits 1 with 9 FAILs and `status` prints `Apps:
codex=FAIL claude=FAIL agy=FAIL` even though the transport is fully ready.
About 660 test lines (15% of the suite) cover desktop discovery. CI runs all
four jobs on `macos-latest` although the suite passes on Linux (264 passed
here); macOS minutes are billed at roughly ten times the Linux rate.

**F18. Two historical FAILs are permanent noise.** Both reference requests
that never landed (`2026-08-29`, `2026-09-02T05-41`). They print as two
long ADVISORY lines in every `check` and a line in every `status`. Retiring
one needs a remediation whose base equals the failed head on a dead branch,
published by the same reviewer; the commits exist but the ranges are
unreachable in practice. They already do not block admission
(`ci_admission_gate.py:456-470` only bites when failed commits are in range).

**F19. Stale and duplicate surfaces.** `docs/protocol/peer.md` promises
"marker metadata" that no response contains and says its filename "is
retained for links". `.env.example` states that nothing loads it.
`coordination/bin/pipeline-python` duplicates `bin/pipeline`'s interpreter
resolution and is referenced nowhere. `tests/unit/formal_review_support.py`
and `tests/unit/team_test_support.py` each define their own `git()` and repo
initializer. `.claude/skills/*` are four one-line pointer stubs to
`.agents/skills/*` (necessary because each app discovers its own directory,
but they cost four files of context).

## 2. Remove (context management and efficiency)

| Id | Remove | Effect | Addresses |
|---|---|---|---|
| R1 | `identity_assurance`, `cursor_semantics`, `liveness` from every payload and `identity_assurance` from `message_view`; keep one top-level `grants_authority:false` (preflight checks it) | ≈43% smaller `team_wait` pages; 353 → ~25 bytes per response | F6 |
| R2 | Default `sent` previews 50 → 10 (add `sent_limit` ≤ 50) | ~16 KB less per orientation call in a busy session | F7 |
| R3 | Historical FAIL advisories from default `status` and `check` text; keep in `--json` and a new `--verbose` | 2 lines less on every run; no trust change | F18 |
| R4 | `docs/protocol/{claude,codex,agy}/continuation.md`, `independence-first.md`, and `peer.md` (fold the two unique sentences into AGENTS.md and ARCHITECTURE.md); trim README/ARCHITECTURE/DECISIONS overlap | Orientation set 29 KB → ≤ 12 KB; one place per invariant | F1, F19 |
| R5 | `.env.example`, `coordination/bin/pipeline-python` | Two dead files | F19 |
| R6 | Desktop-bundle and native-discovery checks from the default `preflight` and from `status` on non-darwin hosts (move behind `preflight --desktop`, on by default only on darwin) | `preflight` and `status` become truthful in CI/cloud | F17 |
| R7 | `macos-latest` from the pytest matrix (ubuntu for 3.11–3.13; one macOS job keeps `check --fast` + `preflight --desktop` coverage) | ~4× cheaper CI, faster queue | F17 |
| R8 | Duplicate git/repo helpers in the two test support modules (one `tests/unit/support.py`) | Less test scaffolding to read | F19 |

## 3. Implement (memory, capacity, capability)

Tier 1 needs no new tool or schema. Tier 2 changes the store schema and one
tool signature. Tier 3 is optional and gated on Tier 2 proving insufficient.

### Tier 1: no new surfaces

**I1. Resume cursor in `team_status`.** Add `acknowledged_through` (the
member's `cursor_frontiers` value) and `next_unread_id` to the caller's own
row. A fresh session then calls `team_wait(after_id=acknowledged_through)`
once. Addresses F2, F9 (partly).

**I2. `bin/pipeline orient`.** One read-only command that prints, in under
40 lines: Git sha/branch/dirty, the caller's own focus and handoff (I4), each
member's focus, pending counts plus resume cursor, pending formal requests,
the subjects of the last three formal artifacts, and the `check --fast`
verdict. Its output replaces reading the 19-file doc set at task start; the
docs become reference material. Addresses F1, F5.

**I3. Cheaper waiting.** Hold one read connection for the duration of a
`team_wait`, poll `PRAGMA data_version` every 200 ms instead of reopening and
re-validating the store every 50 ms, re-validate the path only when
`data_version` changes. Same semantics, about 25× fewer opens. Addresses F8.

**I5. Review ergonomics without weakening the pair.**
`bin/pipeline review publish` = compose (Outcome from `--outcome-file` or
stdin) → validate → `mail send` → `git commit -- <path>`, refusing unless HEAD
is exactly Reviewed head. `bin/pipeline review accept` does the same for the
reviewer, refusing unless HEAD is exactly the request commit.
`bin/pipeline review land-check --base --head` verifies the byte-clean merge
inheritance rule locally before a human merges. Document "never squash-merge
a reviewed range" in OPERATIONS.md. No push is ever performed by these
commands. Addresses F13.

**I6. Doc budget test.** One test that the orientation set (AGENTS.md,
CLAUDE.md, README.md, ARCHITECTURE.md, OPERATIONS.md, DECISIONS.md,
`docs/protocol/**`) totals ≤ 12,000 bytes and names no retired identifier
(`seat`, `marker`, `capacity packet`, `RUNBOOK`). Total bytes, not per-file
line counts (the per-file budget that produced the 2026-08-29 FAIL was the
wrong instrument). Addresses F1, F19.

**I7. Commit and PR bodies carry rationale.** AGENTS.md gets one line: a
merge or authority-surface commit states why in its body; the PR template
already asks for verification and review links. Cheapest durable memory the
repository has. Addresses F4.

### Tier 2: store-level working memory

**I4. Focus and handoff per member, in the local store.** Add
`members.focus` (≤ 512 bytes) and `members.handoff` (≤ 2 KB) columns.
`team_status(focus=..., handoff=...)` sets the caller's own values;
`team_status` returns every member's `focus` and the caller's own `handoff`.
Convention, not ceremony: `focus` is one line ("implementing I3 on
codex/wait-poll; owns pipeline/team_messages.py"), `handoff` is what the next
session of the same member needs ("DONE: …; OPEN: …; NEXT: …"). Uncommitted,
per clone, visible to all three apps, never authority. Path ownership (F12)
is declared in `focus` and shown by `orient`; enforcement stays out of scope.
Addresses F3 (within a machine), F5, F11, F12.

**I8. Model admission split.** Keep `families` exact for *reviewer*
admission (the trust-granting side) and let *author* admission accept any
model whose family resolves through `provider_prefixes`/`families` prefix
matching. Authors grant nothing; the reviewer's different family and
admission stay strict. Removes the self-add deadlock and most registry churn.
Addresses F14.

**I9. Narrow the authority surface list.** Split `pipeline/` in
`AUTHORITY_SURFACES` into trust-granting modules (`compact_pair_loop`,
`ci_admission_gate`, `mailbox_writer`, `codex_protocol_model`,
`protocol_mailbox`, `git_runner`, `team_store`, `team_messages`, `team_mcp`,
`team`, `cli`, `governance_verify_all`, `check_coordination`) and
observational modules (`status*`, `harness_preflight`,
`native_app_readiness`), and drop README.md, ARCHITECTURE.md, and
OPERATIONS.md from the list (AGENTS.md, CLAUDE.md, skills, and
`docs/protocol/` stay because agents execute them as instructions).
Observational modules and reference docs then need material-behavior review,
not high-risk-control. Addresses F15.

**I10. `status` caching for the dashboard only.** Cache
`inspect_verify_review_state` results in `.git/pipeline-team/status-cache.json`
keyed by (HEAD sha, artifact path, blob sha, introduction commit); the gate
(`ci_admission_gate`) and `check` keep re-proving from Git. Bounds `status`
to a handful of subprocesses. Addresses F16.

### Tier 3: only if Tier 2 proves insufficient

**I11. Task rows.** `tasks(id, title, branch, owner, state, updated_at)` in
the store, listed by `orient`, referenced from messages as `task:<id>`.
**I12. Store archival.** `bin/pipeline team compact --before <date>` moves
acknowledged messages to `messages-archive.sqlite3`.
**I13. Reference validation in chat.** Optional `path@commit` resolution in
`team_send`, reusing `_require_path_references_resolve`.
**I14. Committed `STATE.md`.** A single ≤ 2 KB overwritten file for
cross-clone memory. Trade-off: it conflicts on every parallel branch, which
is why Tier 2 keeps memory in the store and Git keeps rationale in commit
bodies.

## 4. Plan

Each phase is one exact-range review pair when its class requires it. Phases
are ordered so that each one shrinks the context cost of the next. Owner
routing hints follow AGENTS.md; a high-risk-control reviewer must be from a
different model family than the author.

| Phase | Content | Files | Risk class | Evidence to produce |
|---|---|---|---|---|
| 0 | This plan | `docs/plans/` | ordinary-local | none required |
| 1 | R1, R2, I1, I3 (implemented on this branch; awaiting its exact-range review) | `pipeline/team_messages.py`, `team_store.py`, `team_mcp.py`, `team.py`, `tests/unit/test_team_messages.py`, `test_team_mcp.py`, orientation lines in `AGENTS.md`, `OPERATIONS.md`, `docs/protocol/peer.md` | high-risk-control (transport) | byte counts before/after on the 120-message probe; cursor experiment re-run showing one call to unread; reversion of the skip guard still fails its test; class-5 probe (no cross-member body in status) unchanged |
| 2 | R3, I2, I4, I10 (implemented on this branch; I4 moved here because `orient` reads focus and handoff) | `pipeline/status*.py`, `governance_verify_all.py`, new `pipeline/orient.py`, `cli.py`, `team_store.py`, `team_messages.py`, `team_mcp.py`, `tests/conftest.py`, `tests/unit/test_status*.py`, `test_team_*.py`, new `test_orient.py`, `OPERATIONS.md` | high-risk-control until I9 lands (then material-behavior) | subprocess count ≤ 30 per warm `status`; `orient` output ≤ 40 lines; cache misses on HEAD change and worktree tampering (reversion test); advisories present in `--json`/`--verbose`; notes columns migrate in place |
| 3 | R4, R5, R8, I6, I7 | `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `OPERATIONS.md`, `docs/protocol/`, `.env.example`, `coordination/bin/`, `tests/unit/` | high-risk-control (`docs/protocol/`, top-level docs, `coordination/bin/`) | budget test red on the old set, green on the new; grep shows each invariant stated once; no test references removed helpers |
| 4 | R6, R7 | `pipeline/harness_preflight.py`, `native_app_readiness.py`, `status_desktop.py`, `.github/workflows/ci.yml`, `tests/unit/test_ci_supply_chain.py` | high-risk-control (workflows) | `preflight` exit 0 on Linux with transport checks; `--desktop` still fails without apps; CI green on ubuntu 3.11–3.13 and the single macOS job; pins unchanged |
| 5 | I4, I5, I8, I9 | `pipeline/team_store.py`, `team_messages.py`, `team_mcp.py`, `compact_pair_loop.py`, `mailbox_writer.py`, `codex_protocol_model.py`, `ci_admission_gate.py`, `config/model-families.toml`, `OPERATIONS.md` | high-risk-control (schema, admission, authority list) | `review publish` refuses at wrong HEAD (negative test); `land-check` rejects a squash landing and accepts a byte-clean merge; author-by-prefix admits a point release while reviewer-by-prefix is refused (evasion test); narrowed surface list still catches every trust-granting module (reversion: remove one, gate goes red) |
| 6 | I11–I14 | store, `orient`, `team_send` | high-risk-control | only opened after two weeks of Phase 5 use show a concrete gap; each item its own range |

Sequencing rules:

1. Land Phase 1 before Phase 2 so `orient` is built on the trimmed payloads.
2. Land Phase 3 before Phase 5 so the review-ergonomics docs go into the
   consolidated OPERATIONS.md once.
3. Phase 4 is independent of 1–3 and can run in parallel on a separate
   worktree (file-disjoint).
4. I8 and I9 change what the gate admits; publish each as its own request so
   a FAIL on one does not hold the other.
5. Every phase ends with `bin/pipeline check` and, for phases 1, 2, 5, the
   probes named in the evidence column re-run against the new head.

## 5. Acceptance metrics

| Metric | Now | Target |
|---|---|---|
| Orientation doc set | 29,214 bytes / 19 files | ≤ 12,000 bytes / ≤ 8 files |
| Tool calls for a fresh session to reach unread mail | 2 or more (pages of ≤100) | 1 (Phase 1: done) |
| `team_wait` 50-message page overhead (400-byte bodies) | 42.7% | 35.0% after Phase 1 (measured); the rest is ids, route, timestamps, receipts |
| `team_status` default payload after 36 own 4 KB sends | 23,029 bytes | 6,123 bytes after Phase 1 (measured) |
| Subprocesses per `status` review state | 243 (linear in artifacts) | 3 warm / 242 cold after Phase 2 (measured); `check` and the gate unchanged |
| SQLite opens per 2 s empty `team_wait` | 42 | 3 after Phase 1 (measured) |
| `preflight` on a Linux/CI host | exit 1, 9 FAIL | exit 0 (transport); `--desktop` opt-in |
| CI runner minutes per run | 4 macOS jobs | 1 macOS + 3 ubuntu |
| Historical FAIL lines in default output | 2 per `check`, 1 per `status` | 0 (kept in `--json`/`--verbose`) |
| Model registry edits needed for an author point release | 1 high-risk review | 0 |
| Review publish steps (author) | 4 commands | 1 (`review publish`) |

## 6. Constraints honored

- No lifecycle hooks, no provider launched from a shell, no app run as
  another app's child (D1; pinned by `test_*_hook_*`).
- Transport state, focus, handoff, and task rows never grant authority (D2,
  D6); every new field is documented as observational.
- Formal artifacts stay append-only and exact-range; I5 only automates the
  commands that already exist and refuses at the wrong HEAD (D4, D5).
- Reviewer admission stays exact-match and different-family (I8 relaxes
  authors only).
- Nothing here authorizes push, merge, release, spend, destructive action, or
  live-data mutation; each phase's landing needs exact current user authority.
