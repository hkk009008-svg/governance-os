# verification-report — outcome evidence reference

Formal review validation: `pipeline/compact_pair_loop.py`. Only the assigned
non-author Codex or Claude reviewer emits GO, NITS, or FAIL. The fixed mailbox
writer supplies the H1, timestamp/from envelope, and cursor footer.

```bash
bin/pipeline mail send <codex|claude> <author-member|all> verification-report "<subject>" <<'EOF'
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
Reviewer seat: <codex|claude>
Reviewer model: <system-visible model; different family from Author model for high-risk-control>
Risk class: material-behavior | high-risk-control
<high-risk-control only: add `Abuse Class Assessment: bound-to-request` here>
<same-request re-issue: add `Supersedes: coordination/mailbox/sent/<superseded-report>.md@<its-introduction-commit>` — a seat supersedes only its own verdicts for that exact request>
<different-request remediation only: the request must contain the matching `Remediates failed report:` ref and the report must `Supersedes:` that exact active FAIL>
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
`unresolved-hard-boundary` disposition. A different system-visible model
*family* is required for `high-risk-control`, not `material-behavior`: a harness
prefix or version suffix is not a different reviewer, and
`codex_protocol_model.models_are_independent` decides the question. NITS and
FAIL remain publishable without successful evidence, but still preserve every
binding.

A different-request remediation is narrower than an ordinary re-issue. The
request's reviewed base is the failed report's `Reviewed head`, its head is a
strict descendant in that reviewed repository, and it preserves the failed
report's repository, risk class, assigned reviewer seat, and finding refs. The
new GO, NITS, or FAIL report dispositions those refs and supersedes the exact
active FAIL. Only GO or NITS clears the blocker; a superseding FAIL records the
current reviewed head and remains blocking. Missing, inactive, wrong-seat,
unrelated, and non-descendant replacements are invalid.

`Reviewer model:` is the current system-visible model in the assigned Codex or
Claude desktop app when it performs the review. There is no provider launcher
or seat-config model pin. Report the identifier the app exposes; the configured
team-member label is routing convenience and does not attest model identity.

The reviewer judges the actual committed outcome and applicable hard
boundaries. Request-listed paths, commands, free-form harness names, and
context labels do not prove compliance or independence.

Findings are ordered CRITICAL, MAJOR, MINOR, INFORMATIONAL and name file:line
when applicable. Separate evidence, inference, uncertainty, and follow-up.

A control that restores the defect proves a guard is not vacuous. It does not
prove the guard is sufficient, and the two are routinely confused. Reverting
reproduces the exact form the guard was written against, so a guard resting on a
text heuristic passes its own reversion control every time while a differently
shaped input walks through it. Attempt evasion as well: leave the guard fully in
place and try to reach the forbidden outcome by another route. Report the
attempt either way — a failed evasion is evidence, and finding none is worth
saying.

Where the question is what another program does — a flag parser, a shell, an
installed CLI — observe it running and cite the command. Inferring it from
source, help text, or an error message is a claim about behaviour supported only
by text.
