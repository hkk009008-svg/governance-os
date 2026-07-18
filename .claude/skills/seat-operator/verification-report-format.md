# verification-report — outcome evidence reference

Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. Only the
assigned non-author Operator emits GO, NITS, or FAIL. The fixed mailbox writer
supplies the H1, timestamp/from envelope, and cursor footer.

```bash
coordination/bin/send-event <operator|operator2> <recipient> verification-report "<subject>" <<'EOF'
<body>
EOF
```

## Body skeleton

```markdown
Event type: verification-report
VERDICT: GO | NITS | FAIL
Verification request: coordination/mailbox/sent/<request>.md@<40-lowercase-request-commit>
Reviewed head: <40-lowercase-hex>
Reviewed base: <40-lowercase-hex>
Reviewer seat: operator | operator2
Reviewer model: <system-visible model different from Author model>
Verification harness: <optional evidence note; not authority>
Verification context: <optional evidence note; not identity proof>

## Allowed Paths

- <optional advisory request context; not compliance authority>

## Findings

<findings ordered by severity, or None.>

## Finding Refs

- <immutable-path@commit>

## Finding Dispositions

- <immutable-path@commit>: addressed | counter-evidence | ordinary-risk | unresolved-hard-boundary

## Evidence

$ <reviewer-chosen command or inspection>
→ <observed result>
```

Preserve the request's finding references in their original order and give
each exactly one disposition. GO requires evidence, a distinct author/reviewer
seat, a different system-visible model, and no `unresolved-hard-boundary`
disposition. NITS and FAIL remain publishable without successful evidence, but
they still preserve and disposition every reference.

The Operator judges the actual committed outcome and applicable hard
boundaries. Request-listed paths, commands, free-form harness names, and
context labels do not prove compliance or independence.

Findings are ordered CRITICAL, MAJOR, MINOR, INFORMATIONAL and name file:line
when applicable. Separate evidence, inference, uncertainty, and follow-up.
