# Targeted Web Research Default Design

Date: 2026-07-15
Status: approved design, awaiting written-spec review
Owner: user-principal; coordinator records and routes implementation

## Purpose

Make public, read-only web research a default capability for every live seat
when the task genuinely depends on information that cannot be established
reliably from the current workspace. Preserve the repository's existing
authority, verification, secrecy, provider-attempt, and side-effect boundaries.

This rule is named `R-WEB-RESEARCH`.

## Scope

The rule applies to readiness bridges, `director`, `director2`, `operator`,
`operator2`, and `coordinator`. A seat may delegate bounded source gathering to
a helper, but the parent seat retains synthesis and every protocol decision.

Agent-agnostic clients receive the rule from `AGENTS.md`. Claude- and
Codex-specific active instruction surfaces mirror the compact invariant so a
seat does not depend on loading a detail document before recognizing the
research trigger.

## Trigger

A seat proactively searches the public web when a material part of its task
depends on one or more of the following:

- current or temporally unstable information;
- external documentation, standards, release notes, issues, papers, datasets,
  laws, schedules, prices, recommendations, or product behavior;
- a niche or uncertain fact whose unsupported recall could change the result;
- direct quotation, links, or precise source attribution; or
- an external artifact named by the user but not supplied in the workspace.

An explicit user request to search or verify online always triggers the rule.

Web research is not required for stable facts already established by supplied
content, current repository source, or deterministic local commands. Pure
transformation tasks and trivial local questions remain local-first.

## Research Behavior

When triggered, the seat:

1. Searches without waiting for a separate browsing instruction.
2. Prefers official and primary sources for technical and consequential
   claims. It uses secondary sources only when they add necessary context or
   when no adequate primary source exists.
3. Checks dates and version applicability for time-sensitive material.
4. Places links close to the claims they support and distinguishes sourced
   facts from the seat's inference.
5. Cross-checks a consequential claim when one source is ambiguous,
   self-interested, stale, or insufficient.
6. Returns to local source and executable evidence before making a
   repository-specific conclusion.

Current repository code, committed protocol artifacts, mailbox bodies, and
executed verification remain authoritative for local state. Internet material
may reveal a hypothesis or implementation pattern, but it cannot override
current local evidence.

## Availability and Failure Handling

If public web access is unavailable or a source cannot be verified, the seat
labels the material claim unverified and identifies the missing evidence. It
continues when the uncertainty is non-blocking. It stops and asks for direction
when the unavailable fact would materially change scope, security, authority,
cost, or an irreversible decision.

A failed search does not authorize a provider substitution, repeated paid
attempt, credential workflow, or fabricated citation.

## Security and Side-Effect Boundary

The user's standing instruction authorizes public, read-only web search when
the trigger above fires. It does not authorize:

- entering credentials, completing login, solving a challenge, or inspecting
  cookies, tokens, browser storage, or private session state;
- uploading repository files, prompts, mailbox bodies, business data, or
  other non-public content;
- downloading and executing software or opening an installer;
- sending forms, messages, comments, votes, purchases, or other external
  mutations;
- paid API use, ChatGPT Pro consultation, Claude or Opus invocation, or any
  other provider/model attempt; or
- a retry, fallback, or transport-profile change prohibited by an active
  route.

Those actions retain their existing explicit authority and attempt rules.
Authenticated browsing is outside this default and requires a separately
authorized workflow.

## Protocol Authority Boundary

Web research is evidence, not authority. It grants no mailbox consumption,
route mutation, lock, GO/NITS/FAIL, merge, push, publication, spend, or
production-change permission. It cannot replace local tests, a lawful Lane V
trigger, Operator verification, state binding, or a terminal receipt.

For seat-specific use:

- Directors may use research to strengthen briefs, designs, compatibility
  checks, and external-pattern comparisons, then verify local applicability.
- Operators may use research for a distinct external specification or known-
  behavior question, but it cannot substitute for independent inspection and
  execution against the reviewed commit.
- The coordinator may use research before synthesis or routing, while current
  mailbox, capacity, lock, and Git state remain decisive.

Ordinary web research is not a generic third reviewer and does not relax
`R-VERIFY-TIER`.

## Codification Surfaces

Implementation uses the canonical-plus-active-mirrors approach:

- agent-agnostic root and detail: `AGENTS.md` and
  `docs/protocol/agents/core.md`;
- Claude router and live-seat surfaces: `CLAUDE.md`,
  `docs/protocol/claude/continuation.md`, and the Claude seat skills;
- Codex router and live-seat surfaces:
  `docs/protocol/codex/continuation.md`,
  `.agents/skills/four-seat-protocol/SKILL.md`, the Codex seat skills, and the
  built-in Codex role prompts;
- provenance: append the user-principal decision to
  `docs/PROTOCOL-RULES-LOG.md`; and
- enforcement: extend `tests/unit/test_protocol_prompt_sync.py` with a compact
  invariant that fails when an active seat surface loses the trigger or its
  authority boundary.

Antigravity and other agent-agnostic runtimes inherit the rule through
`AGENTS.md`; platform-specific duplication is added only where an active
harness otherwise omits the root instruction.

## Compatibility

`R-WEB-RESEARCH` is separate from ChatGPT Pro advisory consultation and Opus
verification. It changes neither consultation transport nor provider-attempt
accounting. Searching public documentation or an open-source repository is not
a model review. Invoking a model, using an authenticated account, or sending a
prompt remains governed by the existing consultation or Opus route.

The rule also preserves the risk-tier router: browsing for an answer is
read-only research, while any resulting repository mutation or external action
is classified and authorized separately.

## Implementation Sequencing

The active workspace currently contains unrelated peer work on several target
instruction and prompt-sync files. The implementation must not overwrite,
stage, or absorb that work. The coordinator will route one tightly coupled
single-pair change after the overlapping work has a clean owner boundary. The
implementing seat refreshes Git and mailbox state immediately before editing
and commits only the reviewed target paths.

The active Opus transport-first recovery route remains unchanged by this
design.

## Verification

The implementation plan must include:

- a prompt-sync test proving every active seat surface contains the targeted
  trigger, public-read-only boundary, local-source precedence, and no-authority
  rule;
- focused execution of `tests/unit/test_protocol_prompt_sync.py`;
- the repository smoke test;
- a repository-wide search showing no active seat surface carries a
  contradictory always-search or never-search instruction;
- exact-path diff inspection and `git diff --check`; and
- independent Operator verification before integration or publication.

No real web search, authenticated browser action, consultation, provider call,
merge, or push is required to test the textual policy itself.

## Acceptance Criteria

The change is complete only when:

1. Every live seat recognizes the targeted trigger without requiring the user
   to repeat "search the internet."
2. Stable local and repository questions remain local-first and do not incur
   compulsory browsing.
3. Technical research prefers official or primary sources, cites material
   claims, and labels inference or unavailable evidence.
4. Public web research remains read-only and cannot silently cross into login,
   disclosure, execution, payment, provider, or mutation behavior.
5. Research cannot grant or replace protocol authority or executable
   verification.
6. Prompt synchronization tests and repository smoke pass on the exact
   reviewed diff.
7. Existing peer work and the active Opus recovery route remain intact.

## Non-Goals

- Forcing a web search for every non-trivial task.
- Building a search proxy, cache, crawler, citation database, or generic
  research framework.
- Enforcing search through runtime telemetry or blocking local tasks when the
  web is unnecessary.
- Expanding authenticated-browser, ChatGPT Pro, Claude, Opus, paid-service,
  merge, push, or publication authority.
