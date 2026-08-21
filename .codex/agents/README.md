# Codex role agents

Choose the smallest agent whose explicit role matches the task:

| Agent | Role delta |
|---|---|
| `readiness-bridge` | Read-only orientation without claiming work |
| `protocol-director` | Accepted outcome ownership and implementation |
| `protocol-operator` | Accepted implementation or non-author actual-range review |
| `protocol-coordinator` | Observation, reconciliation, and mediation |
| `lane-v-verifier` | Read-only advisory review returned to the live Operator |
| `money-gate-reviewer` | Read-only adversarial review of spend enforcement |
| `amnesiac-prober` | Reduced-context premise attack on one claim sentence |

Canonical policy lives in `pipeline/codex_protocol_model.py`; these files contain
only role-specific deltas. A generic parent-scoped subagent needs no project
agent extension and never inherits live-role or external-effect authority.
