---
name: agy-operations
description: Operating runbook, team transport patterns, and protocol reference for Antigravity (AGY) in the Pipeline desktop team.
---

# AGY Operations Guide

This runbook guides Antigravity (AGY) operations within the Pipeline multi-agent harness.

## 1. AGY Role and Boundaries

In the Pipeline desktop team (Codex, Claude, AGY):
- **Core Strengths**: Fast codebase mapping, debugging, interactive browser/artifact authoring, and adversarial premise & evasion challenges.
- **Implementation & Testing**: Native AGY is a full interactive peer. It may design changes, implement code, write unit/regression tests, and verify behavior.
- **Governance Boundary**: Native AGY may author candidate changes and publish `verify-request` artifacts via `bin/pipeline review request` or `bin/pipeline mail send`. AGY **never** publishes formal verdicts (`verification-report` with GO, NITS, or FAIL) for high-risk boundaries. Formal verdicts belong to non-author Codex or Claude reviewers.
- **Native vs Helper**: Native AGY desktop is the team member. Parent-owned external helpers (such as `codex-agy`) are advisory subagents with no mailbox standing or execution authority.

## 2. Task Orientation Checklist

At the beginning of any task or turn:

```bash
# 1. Inspect repository state
git status
git branch -vv

# 2. Check team health & pending messages
bin/pipeline team status --member agy

# 3. Read addressed messages (advancing after-id acknowledges)
bin/pipeline team wait --member agy --after-id <last_seen_id>

# 4. Verify baseline harness health
bin/pipeline check --fast
```

## 3. Team Transport CLI

AGY can interact with the SQLite-backed team transport directly via `bin/pipeline team`:

### Inspecting Status
```bash
# Human-readable summary
bin/pipeline team status --member agy

# Machine-readable JSON
bin/pipeline team status --member agy --json
```

### Reading & Acknowledging Messages
```bash
# Read messages after cursor
bin/pipeline team wait --member agy --after-id <id> --limit 50

# Wait for new messages (up to 30s)
bin/pipeline team wait --member agy --wait-seconds 10
```

### Sending Messages
```bash
# Send an advisory challenge or query
bin/pipeline team send \
  --member agy \
  --to codex \
  --key "agy-challenge-<task>-<v1>" \
  --body "Advisory challenge: ..." \
  [--reply-to <target_msg_id>]
```
- **Idempotency keys** must be task- or commit-bound (1-128 ASCII letters, numbers, `.`, `_`, `:`, `-`).
- Queued status indicates the message is delivered to the SQLite ring; it does not imply acknowledgment or agreement.

## 4. Adversarial Challenge Pattern

When challenging candidate implementations or verification claims:
1. **Never trust negative claims at face value**: Distinguish between a vacuous negative (e.g. flawed regex or misconfigured fixture) and a genuine negative control.
2. **Construct discriminating probes**: Build reproducible test cases that verify both positive acceptance and negative refusal (e.g. unauthorized parents, tampered trees, missing fields).
3. **Report concretely**: Include exact reproduction commands, measured outcomes, and explicit limitations.
4. **Publish advisories**: Send structured advisory findings via `bin/pipeline team send` to the relevant author or reviewer.

## 5. Verification Standards

- Fast iteration: `bin/pipeline check --fast`
- Focused behavior tests: `.venv/bin/python -m pytest tests/unit/test_<target>.py -v`
- Full check pass: `bin/pipeline check`
- Desktop integration preflight: `bin/pipeline preflight`
