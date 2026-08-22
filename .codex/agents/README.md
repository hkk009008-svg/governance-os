# Codex role prompts

Nothing here loads automatically: the Codex CLI resolves
`$CODEX_HOME/config.toml`, never this repository's `.codex/config.toml`, and
that user config declares no `[agents]` table. These are prompts a Codex
invocation is pointed at explicitly. Pick the smallest role that matches:

| Prompt | Role delta |
|---|---|
| `readiness-bridge` | Read-only orientation without claiming work |
| `protocol-director` | Legacy name for the **author** role: owns and submits a range |
| `protocol-operator` | Legacy name for the **reviewer** role: binds one committed request |
| `protocol-coordinator` | Retired identity: no live role, no cursor, publishes nothing |
| `lane-v-verifier` | Read-only advisory review returned to the assigned reviewer |
| `money-gate-reviewer` | Read-only adversarial review of spend enforcement |
| `amnesiac-prober` | Reduced-context premise attack on one claim sentence |

Mailbox identities collapsed to `author` and `reviewer`; the six seat names
still parse for committed history but cannot send a new event. The three
`protocol-*` file names survive only because the runtime role table in
`pipeline/codex_protocol_model.py` and the catalog tests still bind them.

Canonical policy lives in `pipeline/codex_protocol_model.py`; these files contain
only role-specific deltas. A generic parent-scoped subagent needs no project
agent extension and never inherits live-role or external-effect authority.
