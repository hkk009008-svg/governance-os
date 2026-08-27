# Optional Codex task specialists

The Codex desktop app reads this project's `.codex/config.toml`; that file
connects the shared team transport. These profiles are narrower optional
subagents, not standing seats or alternate communication channels. Pick one
only when its specialization helps:

| Prompt | Role delta |
|---|---|
| `readiness-bridge` | Read-only orientation without claiming work |
| `protocol-director` | Advisory author assistant; the parent app retains responsibility |
| `protocol-operator` | Advisory review assistant; the assigned app retains the verdict |
| `lane-v-verifier` | Read-only advisory review returned to the assigned reviewer |
| `money-gate-reviewer` | Read-only adversarial review of spend enforcement |
| `amnesiac-prober` | Reduced-context premise attack on one claim sentence |

Canonical policy lives in `pipeline/codex_protocol_model.py`; these files contain
only role-specific deltas. Every native subagent is an assistant to its parent
app: it cannot publish a formal artifact or verdict and never inherits
external-effect authority. Team messages coordinate work but do not turn a
specialist's output into a verdict.
