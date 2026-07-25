# verification-report — outcome evidence reference

Formal review validation: `scripts/compact_pair_loop.py`. Only the
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
Reviewed repository: <absolute canonical Git worktree root; omit only for Pipeline-local review>
Reviewed head: <40-lowercase-hex>
Reviewed base: <40-lowercase-hex>
Reviewer seat: operator | operator2
Reviewer model: <system-visible model; different from Author model for high-risk-control>
Risk class: material-behavior | high-risk-control
<high-risk-control only: add `Abuse Class Assessment: bound-to-request` here>
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

For a cross-repository review, preserve the request's exact
`Reviewed repository` field; never infer it from `Verification context` or
other prose.

Preserve the request's risk class and finding references in their original
order and give each reference exactly one disposition. Include
`Abuse Class Assessment: bound-to-request` only for `high-risk-control`. GO
requires evidence, a distinct author/reviewer seat, and no
`unresolved-hard-boundary` disposition. A different system-visible model is
required for `high-risk-control`, not `material-behavior`. NITS and FAIL remain
publishable without successful evidence, but still preserve every binding.

The Operator judges the actual committed outcome and applicable hard
boundaries. Request-listed paths, commands, free-form harness names, and
context labels do not prove compliance or independence.

Findings are ordered CRITICAL, MAJOR, MINOR, INFORMATIONAL and name file:line
when applicable. Separate evidence, inference, uncertainty, and follow-up.
