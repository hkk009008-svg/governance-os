# Temporary author and reviewer contract

The historical director/operator terms no longer name standing seats. Current
formal work uses two temporary responsibilities only when a risk class requires
independent review.

## Author

The `author` owns one candidate and its remediation. The author:

- states the intended outcome and allowed paths;
- prepares a focused, reviewable committed range;
- records tests actually run and known limitations;
- identifies the base and head exactly;
- does not approve authored work.

The author responsibility grants no push, merge, release, spend, live-mutation,
or destructive authority.

## Reviewer

The `reviewer` is a non-author Codex or Claude desktop-app member for that exact
range. The reviewer:

- reads the actual diff and relevant surrounding code;
- checks the claimed behavior with proportionate independent evidence;
- assesses the full request, not only author narration;
- returns GO, NITS, or FAIL with concrete findings;
- supplies different-model-family review and abuse-class analysis for
  `high-risk-control`.

The reviewer may ask Codex, Claude, or AGY for additional mapping, tests, or
challenges. Those inputs are evidence. AGY findings must be considered and
material ones explicitly dispositioned, but AGY cannot be the independent
formal reviewer or the sole accepting verdict.

## Trigger and lifetime

- `ordinary-local`: no temporary responsibility or formal review.
- `material-behavior`: author plus non-author exact-range reviewer.
- `high-risk-control`: the material contract plus different-family review and
  explicit abuse-class analysis.
- `external-effect`: exact current authority is evaluated separately; a review
  never grants the effect.

Responsibilities start only when the formal boundary is accepted for a named
range and end when its result is recorded. They do not persist into another
task, range, or effect.

## Exchange and binding

The desktop team transport carries requests, questions, findings, and replies.
Queue and acknowledgement state never constitute acceptance. The author identifies the
exact committed range in the desktop task/review context; the reviewer states
what range was actually inspected.

When a machine-validated formal artifact is required, use the existing
`bin/pipeline review validate` contract and a committed verify-request/report pair.
That validator binds repository, base, head, author, reviewer, model family,
and abuse assessment. Persist the pair through the fixed `bin/pipeline mail
send` writer only when the risk policy requires that durable artifact. This
does not turn the historical mailbox into routine transport or grant an
external effect.

Old director/director2/operator/operator2/coordinator identities remain
parseable only so committed history can be audited. Do not occupy, relaunch, or
route new work through them.
