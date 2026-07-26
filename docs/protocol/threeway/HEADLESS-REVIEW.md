# Headless review dispatch

How to obtain a non-author Operator review from another harness without a human
driving that harness's app. Every command here was executed against this
repository on 2026-07-26; the constraints are observed behaviour, not inference.

**Run the check, do not read this file from memory (ADR-065):**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py all
```

It fails closed and names the specific remedy. This page is the remediation
reference it points at, not the thing you are expected to remember — every
harness failure below exits 0 and produces silence, and this file was already
wrong twice within hours of being written.

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

— and the first such run produced no output at all. Grant what a review needs
in `~/.gemini/antigravity-cli/settings.json` under `permissions.allow`:
`read_file`, plus a `command(...)` entry per command it must run. The preflight
checks these against that file directly.

Note what each grant costs. `read_file` is an observation grant;
`command(git commit)` and `command(coordination/bin/send-event)` are *authority*
grants that outlive the task and apply to every later AGY session, unlike the
per-run limits in a prompt. `--dangerously-skip-permissions` grants everything
at once and should be a deliberate choice, not a shortcut past a denial.

Flags must precede the prompt: it is a Go flag parser, which stops at the first
positional and then reports `flags provided but not defined` for anything after
it. That error text is also the fastest way to check whether a flag exists,
because it happens at parse time and costs no model call.

Reported model `Gemini 3.1 Pro (High)`, family `gemini`. Seat launch is
`coordination/bin/agy-seat <seat>`; it emitted two undefined flags until
`c6f017b`.

Settled 2026-07-26: AGY may hold Layer-1 seats in both modes, superseding the
Mode-1 exclusion in `ANTIGRAVITY-ADOPTION.md` §1. That section records what the
exclusion protected — both audit CRITICALs lived on AGY's CLI write path — and
what seating it in Mode 1 accepts, so an AGY verdict now rests on the same
fail-closed publication validation as every other provider rather than on
provider exclusion. The GO at `5ad43ed` stands.

Its model identity also appears in four forms — `antigravity-gemini-3.6`,
`gemini-3.6-flash`, `gemini-2.5-pro`, `Gemini 3.1 Pro (High)` — and
independence keys on that string.

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
