# verification-report — compact format and severity reference

Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. Only the
assigned non-author Operator emits GO, NITS, or FAIL. `send-event` publishes all
three verdicts through the same fixed mailbox finalizer; it has no receipt,
resume, retry, or recovery path.

```bash
coordination/bin/send-event <operator|operator2> <recipient> verification-report "<subject>" <<'EOF'
<body>
EOF
```

The sender supplies only the body below. The mailbox writer supplies the H1,
timestamp/from envelope, and cursor footer.

## Body skeleton

```markdown
Event type: verification-report
VERDICT: GO | NITS | FAIL
Verification request: coordination/mailbox/sent/<canonical-verify-request>.md@<40-lowercase-request-commit>
Reviewed head: <40-lowercase-hex>
Reviewed base: <40-lowercase-hex>
Reviewer seat: operator | operator2
Reviewer model: <model identity>
Verification harness: <actual harness and method>
Verification context: <fresh non-author context>

## Allowed Paths

- <exact path or directory/>

## Evidence

$ <executed command>
→ <observed result>

## Findings

None.

## Exact Next Trigger

<next lawful owner/action or blocker>
```

GO requires command and output evidence plus a commit in the generated subject
or a `logs/` artifact. Truthful NITS and FAIL remain directly publishable even
when a command or external tool is unavailable.

Findings are ordered CRITICAL, MAJOR, MINOR, INFORMATIONAL and name file:line
when applicable. Separate evidence, inference, uncertainty, and follow-up.
