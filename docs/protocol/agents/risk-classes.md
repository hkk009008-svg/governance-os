# Risk classes

Classify changed behavior, not diff size. Use the lowest truthful class.
Executable profiles live in `pipeline/codex_protocol_model.py`.

## `ordinary-local`

Reversible local work that does not materially change runtime behavior or a
trust boundary. Use focused verification and exact diff inspection. No formal
artifact is required.

## `material-behavior`

A meaningful behavior, integration, data-model, or user-visible change. In
addition to normal verification, a non-author Codex or Claude reviewer inspects
the exact committed range and issues GO, NITS, or FAIL.

## `high-risk-control`

A change to authority, security, privacy, executable composition, identity,
side-effect gates, formal admission, or another trust-granting schema. It needs
the material review, a different model family, and explicit abuse/evasion
analysis.

AGY may author, investigate, test, and challenge every class. Its material
findings must be considered, but it does not issue the formal verdict.

## `external-effect`

Push, merge, release, paid spend, live-data mutation, and destructive actions.
These require exact current user authority for executor, target, effect, and
scope. Code review does not authorize execution.
