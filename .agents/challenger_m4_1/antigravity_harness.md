# Antigravity Protocol Harness & Native Subagent Mesh

This skill is the Antigravity-specific runtime harness for Pipeline. AGY operates natively in direct autonomous posture, executing seated roles (`director`, `operator`, `coordinator`, `director2`, `operator2`) and leveraging native subagent orchestration and structured artifact mesh conventions.

## Operating Posture & Seating Roles

- **Direct Autonomous Mode (Default)**: AGY operates natively in direct autonomous mode by default. Seat launchers (`coordination/bin/agy-seat <seat>`) execute directly without requiring mandatory advisory posture flags.
- **Seated Role Occupancy**: AGY natively occupies Pipeline seats (`director`, `operator`, `coordinator`, `director2`, `operator2`) under unified operating doctrine.

## Operating Doctrine (Layer-2) Bindings & Native Mesh Rules

When performing substantive work, adhere to the unified operating doctrine bound to AGY primitives:

- **Evidence & Verification**: Follow R-EVIDENCE (cite exact command output), R-MEASURE (commit test instruments), and R-VERIFY-TIER (cap over-verification, strict xfail pins for deferred defects).
- **Subagent Model Tiering**: Select native subagent models based on task requirements:
  - `flash_lite`: Directory listing, `rg` searching, file reading, and log extraction (fastest).
  - `flash`: Multi-file research, codebase orientation, and doc inspection.
  - `pro` / `inherit`: Complex reasoning, heavy refactoring, and independent verifier analysis.
- **Native Subagent Mesh (`define_subagent` / `invoke_subagent`)**: Delegate sub-tasks dynamically using `define_subagent` and `invoke_subagent`. Avoid spinning external OS chat processes or polling disk mailbox files for internal task coordination.
- **Structured Artifact Mesh**:
  - **`implementation_plan.md`**: Formulate for multi-file/architectural initiatives (>50 lines or material ambiguity). Skip for routine single-file edits or minor fixes.
  - **`walkthrough.md`**: Formulate upon completion to summarize executed changes, test logs, and verification proof.
  - Save artifacts in designated working directories (`.agents/<agent_folder>/`). Legacy `brain/<conversation-id>/` paths are deprecated.
- **Seating Doctrine & Non-Author Verification**:
  - **impl ≠ verifier**: Candidate code authored by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`).
- **Programmatic Event Emission**: Use `scripts/agy_emit.py --to <seat> --kind <kind> --subject <subj> --body <body>` or `coordination/bin/send-event` to emit schema-compliant events programmatically when milestone records are required.
- **Environment & Index Isolation**: Each seat uses its dedicated `.git/index-agy-<seat>` index and isolated process environment.
- **Background Tasks**: Use `schedule` and `manage_task` tools for background command and timer execution.
- **User Delegation**: Use `ask_question` rather than deciding policy or cross-cutting changes on your own.
- **Smoke Tests**: Run `scripts/ci_smoke.py --fast` for session-start preflight verification; run full `scripts/ci_smoke.py` before final verification.

## Hard Boundaries & User Consent

- **User-Gated Side Effects**: Pushing to `main`, merging candidates, locking resources, or initiating paid spend MUST receive explicit user consent (`ask_question`).
- **No Self-Approval**: Candidate code built by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`). Verifiers must strictly evaluate candidates using reproducible test runs and record actual terminal evidence in verification reports.
