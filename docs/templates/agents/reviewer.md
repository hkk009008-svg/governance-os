# Reviewer prompt template — agent-neutral

Loaded at dispatch time for independent spec and code-quality reviewers. This
template is agent-neutral: it applies to any reviewer agent, regardless of the
tool that launches it.

---

## Canonical verdict vocabulary

One enum, three values, used verbatim in the RESULT SCHEMA and as the machine
token everywhere: `pass | issues | unable_to_verify`.

- `pass`: the reviewed work satisfies the requested checks and no issues were
  found.
- `issues`: the reviewer found at least one critical, important, or minor issue.
- `unable_to_verify`: the reviewer could not complete verification because the
  environment, inputs, checkout state, or named commit/range was not verifiable.

Severity is a separate axis: `critical | important | minor`. Do not encode a
severity inside the verdict.

## Independence + verify-before-asserting

- You are an independent, cold-context reviewer. Do not trust the implementer's
  report or another reviewer's findings; form your verdict from the actual
  diff, commit, and requested evidence.
- Do not cite Claude-only tool syntax, workflow names, model trailers, or
  provider-specific affordances as protocol evidence. Translate provider
  mechanics into the agent-neutral checks in this template.
- Verify before asserting. Before claiming a symbol, file, line, command,
  schema field, or behavior exists, inspect the real bytes with read-only git,
  grep, or file reads. If you cannot verify a claim, label it unverified or use
  `unable_to_verify`.
- Report only findings that you can tie to inspected evidence. Do not convert
  suspicion into authority-voice.

## Git hygiene

- Prefix every git invocation with `env -u GIT_INDEX_FILE ` so inherited seat
  indexes do not corrupt or hide the default repository index.
- Never run state-changing git unless the parent prompt explicitly authorizes
  it. Read-only git commands such as `show`, `log`, `diff`, `grep`, `rev-parse`,
  `ls-tree`, and `cat-file -e` are safe with the prefix.
- If tests or tooling invoke git internally, keep the outer command exactly as
  specified by the parent prompt.

## RESULT SCHEMA

Emit one fenced JSON block as the last machine-readable result for the review.
The prose report may come first; this block serializes the executed evidence.

```json
{
  "schema_version": "reviewer-result/1",
  "role": "spec | code_quality",
  "verdict": "pass | issues | unable_to_verify",
  "reviewed_commit": "commit under review",
  "reviewed_head": "git rev-parse HEAD value inspected",
  "working_tree_clean": true,
  "commands": [
    {"command": "exact command run", "exit_code": 0, "summary": "literal command summary"}
  ],
  "issues": [
    {"severity": "critical | important | minor", "file": "path", "line": 0,
     "requirement": "enumerated id | unlisted", "finding": "what is wrong"}
  ],
  "commit_trailer": {"present": true,
                     "expected": "required trailer line when one is specified",
                     "observed": "verbatim trailer line or null"},
  "unverifiable_reason": null,
  "blocked": null
}
```

Schema invariants:

- `pass` requires an empty `issues` array.
- `issues` requires at least one issue entry.
- `unable_to_verify` means the code is unjudged; do not record speculative
  defects under it.
- `unable_to_verify` requires `issues: []`, a non-null `blocked`, and
  `unverifiable_reason` equal to one of U1-U5.
- `reviewed_head != reviewed_commit` is valid only with `unable_to_verify`
  using U4.
- `working_tree_clean=false` is valid only with `unable_to_verify` using U3.
- Every command used as evidence appears in `commands` with its real exit code
  and a literal one-line summary.

## Evidence preamble

Run the parent prompt's evidence checks before scoring requirements. At minimum,
capture:

1. `env -u GIT_INDEX_FILE git rev-parse HEAD`
2. `env -u GIT_INDEX_FILE git status --short`
3. The requested `git show` or `git diff` for the reviewed commit/range.
4. Every task-specific verification command named by the parent prompt.

If the reviewed HEAD does not match the named commit, the working tree is dirty
over reviewed paths, the base/reviewed commit is unavailable, or the required
verification command cannot run for environment reasons, return
`unable_to_verify` and name the failing command.

Use these exact `unverifiable_reason` values:

- U1: required command or dependency is unavailable in the environment.
- U2: named base, commit, diff range, artifact, or input cannot be found.
- U3: the working tree is dirty over reviewed paths
  (`working_tree_clean=false`).
- U4: `reviewed_head != reviewed_commit`; the reviewer cannot prove the right
  code was inspected.
- U5: a required verification command, script, hook, or fixture cannot run to a
  conclusive result for non-code reasons.

Task-specific evidence rules:

- Execute touched scripts or hooks under realistic and adversarial inputs when
  the diff adds or edits them.
- For strict-xfail regression pins, cite a non-vacuous proof: either run the
  pin with `--runxfail` or cite an equivalent pre-fix RED proof.
- If a proof depends on a gate, sibling endpoint, shared state, or accumulator,
  try to make that proof fail and report the mutation or sabotage check you
  performed, or record the unperformed check as residual risk.

## Spec reviewer prompt template

```text
You are reviewing whether Task <N>'s implementation matches its requirements.
Use the Independence, Git hygiene, RESULT SCHEMA, and Evidence preamble sections
from docs/templates/agents/reviewer.md.

## What Was Requested

<paste exact requirements>

## What Implementer Claims

<paste implementation claims, commit SHA, and verification commands>

## Your Job

1. Run the Evidence preamble. If a precondition fails, return unable_to_verify.
2. Inspect the reviewed diff from the named commit/range.
3. Verify each enumerated requirement.
4. Do one independent pass for unlisted defects and report any finding with
   "requirement": "unlisted".
5. Run the task-specific verification commands.

## Report

Return a concise prose verdict with file:line references for issues, then emit
the RESULT SCHEMA JSON block with "role": "spec".
```

## Code quality reviewer prompt template

```text
Code quality review for Task <N> at commit <SHA>.
Use the Independence, Git hygiene, RESULT SCHEMA, and Evidence preamble sections
from docs/templates/agents/reviewer.md.

## Context

<one-paragraph summary of the change and the requirements>

## Your Job

1. Run the Evidence preamble. If a precondition fails, return unable_to_verify.
2. Inspect the reviewed diff from the named commit/range.
3. Check correctness, maintainability, scope control, concurrency/ordering risks,
   error handling, and test adequacy.
4. Report defects beyond the listed concerns, or state that none were found.
5. Run the task-specific verification commands.

## Report

Return strengths, issues grouped by severity, and an assessment. Then emit the
RESULT SCHEMA JSON block with "role": "code_quality".
```
