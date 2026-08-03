# Headless review dispatch

How to obtain a non-author Operator review from another harness without a human
driving that harness's app. The original harness failures and invocations below
were observed against this repository on 2026-07-26. The capability scopes,
strict live probe, and tool-less package added on 2026-08-03 are enforced by
executable regression tests and the current preflight; dates are not conflated.

**Run the check, do not read this file from memory (ADR-065):**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py all --agy-scope publishing
```

`publishing` is the unchanged full default. Use `--agy-scope evidence` when the
AGY session will only inspect and test an exact range. The result states the
selected scope: evidence readiness does not mean the session can publish or
formalize a verdict, and publishing readiness still grants no authority to use
its persistent effect capabilities. The check fails closed and names the
specific remedy.

Provider launch and paid spend remain separately authorized. Readiness is not
authority: the preflight says a harness *can* act, never that it *may*.

## Why another harness

`compact_pair_loop.py` refuses a `high-risk-control` verdict whose reviewer
model shares the author's family, and `codex_protocol_model.model_family`
strips harness prefixes before comparing, so a wrapper cannot launder
independence. A Claude-authored range therefore needs a reviewer that is not
`claude`. Check before dispatching, not after:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -c "import sys; sys.path.insert(0,'scripts'); import codex_protocol_model as m; print(m.models_are_independent('claude-opus-5','<reviewer model>'))"
```

## Codex

```bash
codex exec -C /Users/hyungkoookkim/Pipeline --sandbox workspace-write -c approval_policy="never" --add-dir /Users/hyungkoookkim/Pipeline/.git "<brief>" < /dev/null
```

Pin sandbox and approval policy on the invocation, never in `.codex/config.toml`.
`test_project_codex_config_does_not_claim_runtime_permissions` asserts that the
project config carries no `approval_policy`, `sandbox_mode` or `features` key,
precisely so a checked-in file cannot silently grant a launch full disk access
with approvals off. With no policy pinned the default is `approval: on-request`,
which in a non-interactive run means an escalation nobody can answer.

`--add-dir …/.git` is what lets the reviewer commit its own report; without it
the sandbox covers only the workdir and `/tmp`.

`< /dev/null` is required, not tidiness. `codex exec` reads stdin to append a
`<stdin>` block even when the prompt is an argument, so an inherited open pipe
blocks it forever. The symptom is a process at 0% CPU that has written no
rollout log under `~/.codex/sessions/`; absence of that log is what
distinguishes "hung before startup" from "slow".

Reported model `gpt-5` / `gpt-5.6-sol`, family `gpt`. Can run evidence,
publish through `coordination/bin/send-event`, and commit its own report.

## AGY

```bash
agy --sandbox --print "<brief>"
```

**A review needs tool grants that headless mode cannot request.** `agy -p`
succeeds for a prompt that uses no tools, which is why a trivial probe passes
and a real review does not: any tool it needs is auto-denied because headless
mode has nobody to prompt. The failure is one line on stdout and exit 0 —

```
no output produced — a tool required the "read_file" permission that headless
mode cannot prompt for, so it was auto-denied.
```

— and the first such run produced no output at all. Exit status and denial text
are not interpreted as success: `--live` requires the exact nonempty output of
an actual `git rev-parse --short HEAD` probe with inherited `GIT_*` removed.

Choose the capability scope explicitly:

```bash
# Read files, inspect the exact range, and run focused tests only.
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py agy --agy-scope evidence

# Adds persistent commit and send-event capability checks; still no authority.
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py agy --agy-scope publishing
```

Evidence scope requires `read_file(<resolved repository root>)` and command
grants for `git diff`, `git show`, `git status`, `git rev-parse`, `git
merge-base`, `rg`, and `.venv/bin/python -m pytest`. The installed AGY 1.1.10
binary exposes `read_file(target)` grants, and local logs load the scoped form
while warning that bare `read_file` is invalid; the preflight requires the exact
resolved root and infers no wildcard. These settings persist into future
sessions. Do not add `command(git commit)`,
`command(coordination/bin/send-event)`, or a blanket permission skip merely to
gather evidence. Publishing scope checks the two effect commands separately,
and even a green result still requires exact commit/publication authority at
execution time.

When user-owned settings may not be changed, package an already committed
request and its exact range without launching a provider:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py agy \
  --package-request 'coordination/mailbox/sent/<request>.md@<full-commit-sha>'
```

The helper validates the full request commit, strict range ancestry, sanitized
Git environment, disabled replacement refs, nonempty UTF-8 diff, and fixed byte
limit. It prints a prompt only and spends nothing. The resulting tool-less
analysis is advisory until a separately authorized actor relays and publishes
it through the canonical Compact Pair path; the package itself cannot create a
formal verdict.

Flags must precede the prompt: it is a Go flag parser, which stops at the first
positional and then reports `flags provided but not defined` for anything after
it. That error text is also the fastest way to check whether a flag exists,
because it happens at parse time and costs no model call.

The low-cost live probe puts every flag before its final `--print <prompt>` and
pins sandboxed plan mode, `gemini-3.6-flash-low`, and low effort. AGY 1.1.10 has
no working-directory flag: the probe passes the exact repository through
`--add-dir`, requires the command tool to use that same absolute `Cwd`, and
forbids a retry or sandbox bypass. The command remains `git rev-parse --short
HEAD`, so the scoped `command(git rev-parse)` grant covers what actually runs.
This is a capability probe, not the identity of any later review. A formal
review records the exact model ID its actual launch selected. Seat launch is
`coordination/bin/agy-seat <seat>`; it emitted two undefined flags until
`c6f017b`.

Settled 2026-07-26: AGY may hold Layer-1 seats in both modes, superseding the
Mode-1 exclusion in `ANTIGRAVITY-ADOPTION.md` §1. That section records what the
exclusion protected — both audit CRITICALs lived on AGY's CLI write path — and
what seating it in Mode 1 accepts, so an AGY verdict now rests on the same
fail-closed publication validation as every other provider rather than on
provider exclusion. The GO at `5ad43ed` stands.

Model-family independence uses the closed registry in
`scripts/codex_protocol_model.py`; harness decorations do not create a new
family, and an unregistered invented model ID buys no independence.

## Cursor

```bash
cursor-agent -p -f --model composer-2.5 --trust --workspace /Users/hyungkoookkim/Pipeline-cursor-seats/operator "<brief>"
```

All four flags carry weight:

- `--workspace` must be the *seat worktree*. Seat identity resolves from the
  worktree's reserved branch plus the registry at
  `~/.cursor/pipeline-app-seats.json`. Pointed at the main tree it degrades to
  readiness-bridge and reports itself unbound.
- `--model` must be pinned. The default is Claude Sonnet 5, which shares the
  family of a Claude author and fails the independence rule.
- `--trust` — print mode refuses an untrusted directory outright.
- `-f` disables cursor-agent's own client-side prompting. `.cursor/hooks.json`
  still governs, because `-f` allows "unless explicitly denied" and this
  repository's denials are explicit.

Observed policy for a bound operator seat, queried directly from
`scripts/cursor_hook_policy.py` rather than inferred from the agent's own
account of itself:

| verdict | commands |
| --- | --- |
| allow | `git log`, `git diff`, `git status`, `pytest`, `ci_smoke.py` |
| ask | `git commit`, `git push` |
| deny | `send-event`, `cursor-publish` |

So Cursor can produce review evidence headlessly but **cannot publish a
verdict** headlessly. That is the design: it is the only side with an in-app
approval surface, and publication is what that surface exists to gate.

## Briefing rules that earned their place

- **Name the committed range, and say not to review HEAD.** Concurrent sessions
  commit while a review runs; a reviewer pointed at "the code" will judge a mix
  of authors and bind a verdict to it.
- **Ask it to falsify your test-quality claims, not accept them.** "91 tests
  pass" is cheap; "disabling this line fails exactly this test" is checkable.
- **State residual risk in the abuse assessment, not the outcome.** A limitation
  written as a question gets investigated; written as a conclusion it gets
  inherited.
- **Do not trust an agent's report of its own permissions.** A Cursor run
  claimed a worktree was absent that existed, and a command blocked that policy
  allows. Query the policy.
