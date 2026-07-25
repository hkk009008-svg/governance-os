# AGY Protocol Modernization — R2 Guidance & Skill Analysis (`analysis_r2.md`)

**Explorer**: Explorer 2 (Milestone 1)  
**Date**: 2026-07-25  
**Target Files Analyzed**:
- `docs/protocol/agy/continuation.md`
- `.agents/skills/antigravity-harness/SKILL.md`

---

## 1. Executive Summary

This report provides a comprehensive analysis of the existing AGY (Antigravity) protocol documentation (`docs/protocol/agy/continuation.md`) and harness skill (`.agents/skills/antigravity-harness/SKILL.md`) as part of **Milestone 1 (R2 Analysis)**.

The current documentation and skill reflect a legacy design pattern characterized by:
1. Mandatory advisory/read-only default posture and launch blockers (`--mode single-model-autonomous` required, `--dry-run` restrictions).
2. Disk-bound Markdown mailbox file polling and legacy file tree structures (`brain/<conversation-id>/`).
3. Outdated process-isolation assumptions (spinning up separate chat processes for every seat rather than leveraging native subagents).

To achieve the R2 requirements of AGY Protocol Modernization, this document formulates the **AGY Native Subagent & Artifact Mesh Architecture**, which transitions AGY to:
- Direct first-class autonomous posture by default.
- Programmatic native subagent orchestration via `define_subagent` and `invoke_subagent`.
- Standardized structured artifacts (`implementation_plan.md`, `walkthrough.md`) stored in scoped `.agents/` working directories instead of disk mailbox file polling.
- Full preservation of Pipeline's core seating doctrine (distinct non-author verifier, impl ≠ verifier), signed-bus event compatibility, and user-gated side effects.

---

## 2. Catalog of Legacy References

### 2.1 Analysis of `docs/protocol/agy/continuation.md`

| Section / Lines | Legacy Reference / Content | Issue / Incompatibility with Modernized Posture |
|-----------------|----------------------------|------------------------------------------------|
| Lines 5 | `"AGY is advisory/read-only by default."` | States advisory/read-only posture is default, creating ambiguity for direct autonomous execution. |
| Lines 9–16 (`Default: advisory readiness`) | `coordination/bin/agy-seat --dry-run <profile>` emits a read-only identity... `"Advisory mode never launches the AGY provider."` | Frames advisory `--dry-run` as default posture, blocking direct launcher execution. |
| Lines 19–26 (`Explicit exception: independent single-model unit`) | `coordination/bin/agy-seat --mode single-model-autonomous <profile>` is the *only launchable AGY mode*. | Restricts launcher to require `--mode single-model-autonomous` flag as an explicit exception. |
| Lines 27–32 (`Read-only startup`) | Advisory AGY session inspects repo state read-only without claiming a seat. | Overly emphasizes read-only posture instead of native direct seat execution. |
| Lines 33–41 (`Fixed-writer syntax`) | `coordination/bin/send-event ... < body.md` | Focuses on file-based stdin piping (`body.md`) for event creation. |
| Lines 76–78 | `"It must not borrow the Pipeline shared mailbox, cursor, lock, or seat identity."` | Outdated restriction framing AGY as isolated from Pipeline seating. |
| Lines 80–90 (`Independent Seat Chat Launchers`) | `"seats ... are independent protocol roles executed in separate dedicated chat processes rather than internal subagents"` & `"Seats communicate exclusively through committed mailbox events emitted via coordination/bin/send-event or scripts/agy_emit.py."` | Directly contradicts native subagent mesh architecture (`define_subagent` / `invoke_subagent`) and disk-free artifact passing. |

### 2.2 Analysis of `.agents/skills/antigravity-harness/SKILL.md`

| Section / Lines | Legacy Reference / Content | Issue / Incompatibility with Modernized Posture |
|-----------------|----------------------------|------------------------------------------------|
| Line 3 | `"Use this skill when operating as Antigravity within the three-way signed-bus protocol or legacy mailbox four-seat campaign."` | References legacy mailbox campaign framing. |
| Line 8 | `"As an Antigravity session, you hold no Layer-1 seat on the write, verify, integrate, or bus-write paths."` | Legacy restriction precluding AGY from occupying seats directly. |
| Lines 11–12 | Roles split into `"Multi-Model Three-Way Protocol (Observer / Relay)"` and `"Single-Model Autonomous Unit"` using legacy mailbox protocol. | Legacy dual-mode split requiring explicit single-model autonomous mode flag. |
| Lines 23–24 | `"- **Seat Launchers (Default Behavior):** Seats operate as separate chat instances launched via coordination/bin/agy-seat --mode single-model-autonomous <seat>."` | Enforces external chat process spinning and mandatory `--mode single-model-autonomous`. |
| Line 25 | `"- **Mailbox Emission:** Use scripts/agy_emit.py --to <seat> ... for 1-step schema-compliant event creation..."` | Assumes disk-bound mailbox polling loops between seats. |
| Line 26 | `"- **Reporting:** Use markdown artifacts in brain/<conversation-id>/ for structured output."` | Refers to deprecated `brain/<conversation-id>/` directory instead of standard `.agents/<agent>/` workspace artifacts (`implementation_plan.md`, `walkthrough.md`). |
| Lines 38–40 | `"When operating in Single-Model Autonomous Unit mode: ... You are authorized to assume mailbox seats..."` | Frames seat occupancy as a conditional exception mode. |

---

## 3. AGY Native Subagent & Artifact Mesh Architecture

To replace the legacy polling and advisory restrictions while maintaining complete compatibility with Pipeline seating and verification doctrines, the modernization establishes four architectural pillars:

```
+-----------------------------------------------------------------------------------+
|                        AGY Native Subagent & Artifact Mesh                        |
+-----------------------------------------------------------------------------------+
| 1. Direct Autonomous Posture                                                      |
|    - Default execution mode for coordination/bin/agy-seat <seat>                  |
|    - No mandatory --mode single-model-autonomous or --dry-run flags               |
+-----------------------------------------------------------------------------------+
| 2. Native Subagent Mesh (define_subagent / invoke_subagent)                      |
|    - Model Tiering: flash_lite (search/read), flash (research), pro (impl/verify) |
|    - Dynamic typed sub-task delegation without disk mailbox polling               |
+-----------------------------------------------------------------------------------+
| 3. Structured Artifact Mesh                                                       |
|    - implementation_plan.md: Architecture, scope, evidence chain, target diffs   |
|    - walkthrough.md: Executed changes, verification commands, test logs           |
|    - Standardized locations in .agents/<agent_folder>/                            |
+-----------------------------------------------------------------------------------+
| 4. Seating & Protocol Compatibility                                               |
|    - Preserves impl != verifier rule (distinct non-author verifier subagent/seat) |
|    - Programmatic event emission via scripts/agy_emit.py / send-event             |
|    - Strict adherence to R-EVIDENCE, R-MEASURE, R-VERIFY-TIER, user-gated effects |
+-----------------------------------------------------------------------------------+
```

### Pillar 1: Direct Autonomous Posture
- AGY seat launchers (`coordination/bin/agy-seat <seat>`) run natively in autonomous mode without requiring `--mode single-model-autonomous`.
- Advisory `--dry-run` posture is optional for quick environment/profile inspection, never a mandatory launch blocker.
- AGY agents directly fulfill Pipeline roles (`director`, `operator`, `coordinator`, `director2`, `operator2`).

### Pillar 2: Native Subagent Mesh Architecture (`define_subagent` / `invoke_subagent`)
- Rather than launching independent OS chat processes that poll disk mailbox files, AGY agents utilize native subagents.
- Subagents are defined using `define_subagent` with appropriate capabilities and model tiering:
  - **`flash_lite`**: Fast directory listings, grep searches (`rg`), log viewing, and file reads.
  - **`flash`**: Multi-file research, codebase orientation, and documentation analysis.
  - **`pro` / `inherit`**: Deep reasoning, complex refactoring, and independent verifier analysis.
- Sub-tasks are dispatched via `invoke_subagent`. In-memory context passing replaces file polling.

### Pillar 3: Structured Artifact Mesh (`implementation_plan.md` & `walkthrough.md`)
- File-based mailbox polling loops are replaced by structured artifacts created in designated agent working directories (`.agents/<agent_folder>/`):
  - **`implementation_plan.md`**: Required for non-trivial initiatives (>50 LOC or material ambiguity). Documents problem statement, evidence chain, proposed code changes (file paths, line numbers), and verification strategy.
  - **`walkthrough.md`**: Produced upon task completion. Summarizes executed changes, test results, verification command outputs, and verification proof for handoffs.
- Deprecated `brain/<conversation-id>/` paths are superseded by explicit `.agents/` workspace paths.

### Pillar 4: Seating & Protocol Compatibility
- **Seating Isolation & Non-Author Verification**: The fundamental Pipeline invariant **impl ≠ verifier** remains mandatory. An implementer subagent/seat (`director`) must submit its work to a distinct verifier subagent/seat (`operator`).
- **Signed-Bus & Mailbox Emission**: When inter-provider or pipeline milestone events must be recorded, `coordination/bin/send-event` or `scripts/agy_emit.py` are executed programmatically without disk polling loops.
- **Verification Discipline**: All work adheres to R-EVIDENCE (cite command output), R-MEASURE (commit test instruments), R-VERIFY-TIER (strict xfail pins for deferred defects), and user consent rules for external side-effects (push, merge, paid spend).

---

## 4. Proposed Refactored Documentation Content

### 4.1 Proposed Refactored `docs/protocol/agy/continuation.md`

```markdown
# AGY (Antigravity) Continuation Adapter & Native Subagent Mesh

This adapter defines the AGY (Antigravity) protocol integration in Pipeline. AGY operates as a first-class autonomous provider running natively in direct autonomous mode, using a native subagent & artifact mesh architecture while fully maintaining Pipeline's seating and verification doctrines.

## Operating Posture

### Direct Autonomous Posture (Default)

`coordination/bin/agy-seat <profile>` launches directly into autonomous execution for the specified seat (`director`, `operator`, `coordinator`, `director2`, `operator2`). No advisory posture flags or `--mode single-model-autonomous` parameters are required.

### Advisory Inspection Mode (Optional)

`coordination/bin/agy-seat --dry-run <profile>` emits the resolved seat configuration, model profile, and isolated `.git/index-agy-<profile>` path for read-only inspection without launching the provider process.

## AGY Native Subagent & Artifact Mesh Architecture

AGY replaces legacy disk-bound Markdown mailbox file polling with native subagent orchestration and structured artifact management:

### 1. Native Subagent Mesh (`define_subagent` / `invoke_subagent`)
Seats orchestrate complex tasks by defining specialized subagents (`define_subagent`) and invoking them (`invoke_subagent`). Subagents are tiered by model capability:
- **`flash_lite`**: Fast search (`rg`), file reading, directory listing, and log inspection.
- **`flash`**: Codebase orientation, multi-file analysis, and doc exploration.
- **`pro` / `inherit`**: Deep logic implementation, complex refactoring, and independent verifier analysis.

### 2. Structured Artifact Mesh (`implementation_plan.md`, `walkthrough.md`)
Subagents exchange structured work products via standard artifacts in their working directory (`.agents/<agent_folder>/`):
- **`implementation_plan.md`**: Formulated during design phase for architectural or multi-file initiatives (>50 LOC or material ambiguity). Contains problem description, evidence chain, target file diffs/snippets, and verification plan.
- **`walkthrough.md`**: Formulated upon completion. Details actual changes made, test outputs, verification command results, and handoff evidence.

## Seating Doctrine & Event Emission

- **Seating Independence**: The core Pipeline invariant **impl ≠ verifier** applies to AGY native subagents and seats. Implementation subagents (`director`) must be verified by distinct verifier subagents (`operator`).
- **Event Emission**: When milestone transitions or inter-provider updates require mailbox/bus records, events are emitted programmatically via `coordination/bin/send-event` or `scripts/agy_emit.py`:
  ```bash
  coordination/bin/send-event <sender> <recipient> <kind> <subject...> < body.md
  ```

## AGY Launcher Mechanics

`coordination/bin/agy-seat` is backed by `scripts/agy_seat_launcher.py` and `scripts/agy_protocol_model.py`. It establishes clean environment isolation for each seat:
- Sanitizes environment variables (removes inherited `CLAUDE_*`, `CURSOR_*`, `CODEX_*`, `ANTIGRAVITY_*`, `GIT_*`).
- Sets controlled variables: `AGY_SEAT`, `AGY_AGENT_MODE=autonomous`, `AGY_AGENT_ROLE`, `AGY_GIT_INDEX_FILE`, and `GIT_INDEX_FILE` (`.git/index-agy-<seat>`).
- Loads local seat profiles from `~/.agy/pipeline-seat-launcher.toml`.
```

---

### 4.2 Proposed Refactored `.agents/skills/antigravity-harness/SKILL.md`

```markdown
---
name: antigravity-harness
description: Use this skill when operating as Antigravity within Pipeline. Defines Layer-2 operating doctrine bindings, native subagent mesh (define_subagent/invoke_subagent), and artifact-driven execution (implementation_plan.md, walkthrough.md).
---

# Antigravity Protocol Harness & Native Subagent Mesh

This skill defines the AGY (Antigravity) runtime harness for Pipeline. AGY operates natively in direct autonomous posture, executing seated roles (`director`, `operator`, `coordinator`, `director2`, `operator2`) and leveraging native subagents and structured artifacts.

## Operating Posture & Seat Execution

- **Direct Autonomous Mode**: AGY operates natively in direct autonomous mode by default. Seat launchers (`coordination/bin/agy-seat <seat>`) execute directly without mandatory advisory flags.
- **Role Occupancy**: AGY natively occupies Pipeline seats (`director`, `operator`, `coordinator`, `director2`, `operator2`) under the unified operating doctrine.

## Operating Doctrine (Layer-2) Bindings & Native Mesh Rules

When performing substantive work, adhere to the full unified operating doctrine bound to AGY primitives:

1. **Evidence & Verification**: Follow R-EVIDENCE (cite exact commands and outputs), R-MEASURE (commit test instruments), and R-VERIFY-TIER (cap over-verification, strict xfail pins for deferred defects).
2. **Subagent Model Tiering**:
   - `flash_lite`: Directory listing, `rg` searching, file reading, log extraction (fastest).
   - `flash`: Multi-file research, codebase orientation, doc inspection.
   - `pro` / `inherit`: Complex reasoning, heavy refactoring, independent verifier analysis.
3. **Native Subagent Mesh (`define_subagent` / `invoke_subagent`)**:
   - Delegate sub-tasks dynamically using `define_subagent` and `invoke_subagent`.
   - Avoid spinning external OS chat processes or polling disk mailbox files for internal task coordination.
4. **Structured Artifact Mesh**:
   - **`implementation_plan.md`**: Formulate for multi-file/architectural initiatives (>50 lines or material ambiguity). Skip for routine single-file edits or minor fixes.
   - **`walkthrough.md`**: Formulate upon completion to summarize changes, test logs, and verification proof.
   - Save artifacts in scoped working directories (`.agents/<agent_folder>/`). Legacy `brain/<conversation-id>/` paths are deprecated.
5. **Seating Doctrine & Non-Author Verification**:
   - **impl ≠ verifier**: Candidate code authored by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`).
6. **Programmatic Event Emission**:
   - Use `scripts/agy_emit.py --to <seat> --kind <kind> --subject <subj> --body <body>` or `coordination/bin/send-event` to emit schema-compliant events programmatically when milestone records are required.
7. **Environment & Index Isolation**:
   - Each seat uses its dedicated `.git/index-agy-<seat>` index and isolated process environment.
8. **Preflight & Verification Smoke Tests**:
   - Run `scripts/ci_smoke.py --fast` for quick session-start preflight check; run full `scripts/ci_smoke.py` before final verification.

## User Consent & Hard Boundaries

- **User-Gated Side Effects**: Pushing to `main`, merging candidates, locking resources, or initiating paid spend MUST receive explicit user consent (`ask_question`).
- **No Self-Approval**: Verifiers must strictly evaluate candidates using reproducible test runs and paste actual terminal evidence into verification reports.
```

---

## 5. Implementation Roadmap for Milestone 3 (M3)

When Milestone 3 (Documentation & Harness Skill Update) is executed by the designated Implementer agent, the following steps should be taken:

1. **Update `docs/protocol/agy/continuation.md`**:
   - Replace legacy advisory/read-only framing and `--mode single-model-autonomous` requirements with direct autonomous posture.
   - Insert the Native Subagent Mesh (`define_subagent`/`invoke_subagent`) and Structured Artifact Mesh (`implementation_plan.md`, `walkthrough.md`) sections.
   - Clarify seat launcher mechanics and environment isolation.

2. **Update `.agents/skills/antigravity-harness/SKILL.md`**:
   - Update frontmatter description.
   - Streamline operating doctrine rules to reference native subagent tiering, artifact mesh paths in `.agents/`, and programmatic event emission.
   - Remove legacy mailbox polling and `brain/` directory references.

3. **Validation & Verification**:
   - Re-read both updated files to verify formatting, clarity, and consistency with `scripts/agy_protocol_model.py` and `scripts/agy_seat_launcher.py`.
   - Run `.venv/bin/python scripts/ci_smoke.py --fast` to confirm documentation updates do not break any automated doc integrity checks.
