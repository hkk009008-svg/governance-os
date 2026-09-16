# Current architecture decisions

Only decisions that still shape the executable harness. History is in Git.

- **D1 Native desktop apps are the team.** Codex, Claude, and AGY are the
  three members. No provider is launched from the shell; native subagents
  inherit their parent app's scope and no separate authority.
- **D2 Routine communication is local and uncommitted.** The three MCP tools
  use a repository-scoped SQLite store under the Git common directory. Git is
  not a chat bus. Queued, acknowledged, replied, and substantive are separate
  facts; none grants authority.
- **D3 Work is direct and proportional.** Focused tests, exact diff
  inspection, one final pass. No required roles, modes, packets, or planning
  ceremonies.
- **D4 Formal review is one pair of artifacts.** One exact-range
  `verify-request` and one bound `verification-report` from a non-author
  Codex or Claude member; high-risk controls need a different model family and
  abuse-class analysis. The fixed writer accepts no other kind.
- **D5 Authority-surface admission is executable.** The gate discovers
  authority commits independently of the review files and admits only exact
  high-risk GO/NITS coverage; active FAILs block until superseded. Runtime
  identity stays an external task fact.
- **D6 Review never grants an external effect.** Push, merge, release, spend,
  destructive operations, and live-data mutation need exact current user
  authority.
- **D7 Working memory is local; rationale is committed.** Focus and handoff
  notes live in the local store, never in Git. Durable rationale lives in
  commit bodies, in this file, and in formal artifacts.
