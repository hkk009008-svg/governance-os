# CLI-exclusive overhaul — Claude CLI + Codex CLI as one unit

**Status:** in progress, started 2026-08-21.
**Owner:** user-principal directive; executed from the Claude Code CLI.
**Base:** `fec89e52` on `claude/tier2-record-ceiling-finding` (main = `86146d1f`).
`docs/superpowers/plans/` is not an authority surface; this file confers nothing.

## 0. Intent

Turn Pipeline from a multi-provider governance kernel with a desktop-app
adapter into a **CLI-exclusive repository whose only two participants are the
`claude` CLI and the `codex` CLI**, with AGY available to both as an advisory
subagent. Everything reorganises around that: one command surface, one
contract, one review binding, one durable ledger.

User decisions taken 2026-08-21 (all four asked before execution):

| Decision | Chosen |
|---|---|
| AGY authority | Advisory subagent for both sides; never a seat or verdict source |
| Non-CLI subsystems | Delete outright; git history is the archive |
| Python restructure | `scripts/` → `pipeline/`, one `pipeline` command, flat imports preserved |
| Protocol ceremony | Collapse seats to author/reviewer (highest-risk option, chosen knowingly) |

## 1. Measured baseline

Every number below is a command result, not an estimate.

| Fact | Value | Command |
|---|---|---|
| Tracked files | 1678 | `git ls-files \| wc -l` |
| Python lines | 60,728 | `git ls-files '*.py' \| xargs wc -l` |
| — `scripts/` | 26,642 | same, scoped |
| — `tests/` | 29,948 | same, scoped |
| — `threeway/` | 3,789 | same, scoped |
| — `tools/` | 349 | same, scoped |
| Mailbox events | 967 | `ls coordination/mailbox/sent \| wc -l` |
| — `coordination` chatter | 431 | filename-kind histogram |
| — `verify-request` | 244 | ditto |
| — `verification-report` | 211 | ditto |
| — all other kinds combined | 81 | ditto |
| Declared event kinds | 25 | `wc -l coordination/mailbox/kinds.txt` |
| Kinds ever used | 13 | histogram above |
| Local branches | 110 | `git branch --list \| wc -l` |
| Worktrees / prunable | 43 / 25 | `git worktree list` |
| Open PRs | 0 | `gh pr list --state open` |
| Cursor health | director 564 unread @ cursor=0; director2 424 @ 0; operator2 476 @ 0; operator 52 @ 2026-08-01 | `pipeline-python scripts/status.py snapshot` |
| Gate state at base | FAIL (0 fatal, 8 advisory, 2 failed review) | same |
| `check_coordination` latency | 0.75 s | timed run, 2026-08-21 |

### 1.1 Instrument note — the mailbox is NOT archived

`docs/protocol/learning/mailbox-archive-proposal.md` sets the activation
criterion explicitly: *not* event count, but a named live collector measured
to exceed a recorded budget. Measured at this base, `check_coordination.py`
returns in **0.75 s** over 967 events. The criterion is not met, so this
overhaul does **not** move `coordination/mailbox/sent/`. The corpus stays
where published refs already point. Recorded because the measurement
disagreed with the tidier answer.

### 1.2 Both CLIs are present, authenticated, and symmetric

    claude --version   → 2.1.238 (Claude Code)      auth: claude.ai, max
    codex --version    → codex-cli 0.147.0          auth: ChatGPT
    agy, claude-agy, codex-agy → present in ~/.local/bin

| Capability | `claude` | `codex` |
|---|---|---|
| Headless | `-p/--print` | `exec` |
| Machine-readable output | `--output-format json\|stream-json` | `--json` (JSONL) |
| Structured output schema | `--json-schema <schema>` | `--output-schema <FILE>` |
| Final message to a file | parse `.result` | `-o/--output-last-message <FILE>` |
| Model selection | `--model` | `-m/--model` |
| Working root | cwd + `--add-dir` | `-C/--cd` + `--add-dir` |
| Effect containment | `--permission-mode`, `--allowed-tools` | `-s/--sandbox` |
| Spend ceiling | `--max-budget-usd` | (none — wall-clock/timeout only) |
| Session resume | `-r/--resume <id>` | `exec resume <id>` |
| Project instructions | `CLAUDE.md` | `AGENTS.md` |

This symmetry is what makes a single peer command possible.

## 2. Target architecture

    bin/pipeline                  one entry point; resolves the venv itself
    pipeline/                     was scripts/; flat modules, uniform main(argv)
      cli.py                      verb registry and dispatch
      peer.py                     NEW — claude/codex/agy headless invocation
    coordination/
      bin/send-event              kept: hardened writer front door
      mailbox/sent/               unchanged corpus; new events use new roles
      peer/                       NEW — committed peer receipts
    docs/
      protocol/                   live CLI doctrine only
      archive/                    historical handoffs, incidents, closeouts
    AGENTS.md                     the contract, loaded natively by codex
    CLAUDE.md                     thin adapter: "read AGENTS.md" + Claude deltas

### 2.1 One command instead of an incantation

Today the shortest governed invocation is

    unset GIT_INDEX_FILE
    coordination/bin/pipeline-python scripts/status.py snapshot

— an interpreter resolver, an environment scrub, and a file path before the
verb. After:

    pipeline status

`bin/pipeline` performs the `GIT_INDEX_FILE` scrub and the primary-checkout
venv resolution that `coordination/bin/pipeline-python` does today, so no
caller has to remember either.

### 2.2 Seats collapse to author and reviewer

Six seat names (`director`, `director2`, `operator`, `operator2`,
`coordinator`, `coordinator2`) become two roles — **author** and
**reviewer** — carried alongside the **side** that ran (`claude`, `codex`).

The review binding gets *stronger*, not weaker. Today
`compact_pair_loop.validate_report` checks a **declared** seat name and a
**declared** model ID; ARCHITECTURE §9 already concedes "a configured model
name is runtime evidence, not cryptographic provider attestation". Under the
new model the reviewer's side and model come from the peer CLI's own JSON
output, captured in a committed receipt. Declared identity becomes observed
identity. It is still not attestation — a local receipt is forgeable by
whoever can write the file — but it is evidence the author did not simply
type.

The six legacy names stay valid **for historical events only**, at a named
cutover commit. New events accept `author` and `reviewer` only.

### 2.3 Cursors are deleted, not repaired

Three of four cursors read 0 while reporting 400+ unread; the fourth has not
moved since 2026-08-01. A mutable per-seat pointer that drifts to zero is a
worse instrument than no instrument, because it reads *reassuring* when
broken. Replace "unread" (mutable state) with "open" (derived): unanswered
verify-requests and failed reports, computed from the ledger every time.
This removes `coordination/mailbox/seen/`, `consume-events`, `bus_unread.py`,
`consume_bus.py`, and `mailbox_monitor.py`.

## 3. The joint mechanism — `pipeline peer`

The current cross-app mechanism is a persistent Agent-SDK peer
(`pipeline-codex-bridge`) started over MCP and addressed with Claude Desktop's
native `ListAgents`/`SendMessage`. It is desktop-bound, costs a per-instance
budget, and — by its own documentation — **"reports no delivery ack"**.

Replacement: **one-shot headless invocation of the other CLI, with a receipt.**

    pipeline peer ask codex  --task <id> --prompt-file P [--role reviewer]
    pipeline peer ask claude --task <id> --prompt-file P [--model opus]
    pipeline peer ask agy    --task <id> --prompt-file P --role challenge
    pipeline peer review --base B --head H --to codex
    pipeline peer receipts --task <id>

Each call writes `coordination/peer/<task>/<seq>-<side>.json`:

    {"task": "...", "seq": 1, "side": "codex", "role": "reviewer",
     "model_requested": "...", "model_reported": "...",
     "argv_sha256": "...", "prompt_sha256": "...", "result_sha256": "...",
     "exit": 0, "started": "...", "duration_s": 93, "cost_usd": null}

Why this is better than the bridge, point by point:

1. **Delivery is acknowledged.** The child's exit code and captured stdout
   *are* the ack the bridge never had. "Submitted but delivery unknown" — a
   row in today's OPERATIONS troubleshooting table — stops being reachable.
2. **One process, one budget, terminates.** No long-lived peer to leak, no
   duplicate-bridge failure mode, no registration-lag ambiguity.
3. **The model is observed.** `model_reported` comes from the CLI's own JSON,
   not from the author's prose.
4. **Symmetric and direction-free.** The same verb runs from either terminal;
   `claude` and `codex` are two backends of one interface.
5. **AGY is a third backend, not a third authority.** `--side agy` dispatches
   to the existing `claude-agy`/`codex-agy` wrappers (identical signatures,
   shared `~/.codex/agy-desktop-user-inflight.lock`, so the lane still
   serialises). Receipts record it as advisory; no verdict path accepts it.

## 4. Staged execution

Each stage is a separately reviewable range. Ordering is chosen so that every
stage leaves the tree green.

| # | Stage | Shape |
|---|---|---|
| 1 | Subtract non-CLI surfaces | delete-only; large negative line count |
| 2 | `scripts/` → `pipeline/` + `bin/pipeline` | renames + one new module |
| 3 | `pipeline peer` | new module + tests |
| 4 | Seat collapse + kind reduction + cursor removal | behaviour change, highest risk |
| 5 | Doctrine consolidation | AGENTS.md contract, CLAUDE.md adapter, docs/archive |
| 6 | Repo hygiene | prune worktrees and merged branches |
| 7 | Verification + Codex review | full suite, gates, different-family review |

## 5. Landing constraints, stated up front

- **Growth budget.** `check_no_ceremony` hard-fails at 100 net Python lines
  per range and 80 per pre-existing file. Stages 1, 2, 4 and 6 are
  deletion- and rename-dominated and pass comfortably. Stage 3 introduces a
  new file, which is exempt from the per-file cap but not the aggregate, so
  `pipeline/peer.py` plus its dispatch must land inside 100 net lines or as
  its own sequential range. The ceiling is not amended for this work: the
  finding at `fec89e52` records why a mechanism that excepts itself proves
  nothing.
- **Admission gate.** `scripts/ci_admission_gate.py` blocks any range touching
  an authority surface without a committed GO/NITS report bound to a
  `high-risk-control` request. This overhaul touches nearly every listed
  surface, so **Codex must review it** — and the only different-family
  reviewer available is Codex. Stage 7 is not optional.
- **External effects.** Push, merge, and provider launch each need separate
  live authority. Peer invocation is a provider launch.

## 6. Verification

    pipeline check                      # governance_verify_all aggregate
    python -m pytest tests -q           # full suite, both before and after
    pipeline peer review --base <base> --head HEAD --to codex

Report failures with their output; name skips as skips.
