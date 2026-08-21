# Pipeline Claude router

Read `AGENTS.md` first: it is the whole contract, and it is the same contract
Codex reads. This file adds only what the Claude Code CLI does differently,
and every item here is forced by the harness rather than chosen.

## Claude-only mechanics

- Ordinary Git uses the `env -u GIT_INDEX_FILE` prefix. Python and pytest run
  through `coordination/bin/pipeline-python`, preceded by its own
  `unset GIT_INDEX_FILE` line rather than that prefix — Claude's Bash tool
  refuses `env` once a dash-prefixed token follows the variable list, so the
  prefixed form is unrunnable as soon as the command takes options.
  `bin/pipeline` needs neither: it clears the variable itself, so prefer
  `pipeline <verb>` over a raw module path.
- Claude Code discovers skills only under `.claude/skills/`; canonical bodies
  live in `.agents/skills/`. Load a skill only when the task matches its
  declared trigger.
- Keep simple work simple even inside an explicit role: fix concrete findings
  directly, use focused checks while iterating, then run one final review and
  full verification pass. Do not generalize a stale instruction into a parser
  or nested remediation cycle unless the user asked for it or the code needs it.
- When a role, mailbox, handoff, continuation, peer, or protocol decision is
  named, load `docs/protocol/claude/continuation.md` and the concrete
  `seat-*` skill. When learning-plane work is named, load
  `docs/protocol/learning/contract.md` (ADR-067).
- Work modes per `docs/protocol/work-modes.md`: ordinary work declares no
  mode; a long campaign is `explore`, a frozen candidate `validate`, a
  canonical or live mutation `promote`.
- Run `pipeline check` when work changes governance/runtime topology or relies
  on an `ARCHITECTURE.md` invariant — it is not a session-start ritual.
- Refresh scoped `git log`/`git status` before writes and gates, and diff the
  doctrine paths (`docs/protocol`, `.claude/skills`, `CLAUDE.md`,
  `AGENTS.md`) before submitting a range: an obligation can land mid-flight
  and bind in-progress work.
- Every model this harness can select is claude-family, so Claude cannot
  supply its own different-family reviewer. That counterparty is Codex,
  reached with `pipeline peer ask codex`.
- External effects (push, merge, locks, cursor consumption, peer invocation,
  paid spend) each need separate explicit authority.

## Lessons route through candidates

Finish the scoped task before extracting a lesson; then draft and, only with
the applicable publication authority, publish an evidence-backed
`learning-candidate` with truthful provider scope. There is no canonical
skill creation or edit solely because a lesson arose; promotion into a
canonical skill is a separately accepted, risk-classed Compact Pair change.
If a loaded skill conflicts with current code or a higher-priority
instruction, stop relying on it and record the conflict in the task evidence;
current code and higher-priority instructions remain controlling. Correct
canonical skill bytes only when the current accepted task authorizes that
correction and its required review completes.
