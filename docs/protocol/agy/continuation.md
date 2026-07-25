# AGY (Antigravity) Continuation Adapter & Native Subagent Mesh

This adapter defines the AGY (Antigravity) protocol integration in Pipeline. AGY operates as a first-class autonomous provider running natively in direct autonomous posture, leveraging a native subagent & artifact mesh architecture while fully preserving Pipeline's seating and verification doctrines.

## Operating Posture

### Direct Autonomous Posture (Default)

`coordination/bin/agy-seat <seat>` launches directly into autonomous execution for the specified seat (`director`, `operator`, `coordinator`, `director2`, `operator2`). Direct autonomous posture is the default behavior — no advisory flags or mandatory `--mode single-model-autonomous` parameters are required.

### Advisory Inspection Mode (Optional)

`coordination/bin/agy-seat --dry-run <profile>` emits the resolved seat configuration, model profile, and isolated `.git/index-agy-<profile>` path for read-only inspection without executing the provider process. Advisory inspection mode does not claim a shared Pipeline seat, mailbox, cursor, or lock.

## AGY Native Subagent & Artifact Mesh Architecture

AGY replaces legacy disk-bound Markdown mailbox file polling with native subagent orchestration and structured artifact management:

### 1. Native Subagent Mesh (`define_subagent` / `invoke_subagent`)
Seats orchestrate tasks programmatically by defining specialized subagents (`define_subagent`) and invoking them (`invoke_subagent`). Subagents are tiered by model capability:
- **`flash_lite`**: Fast search (`rg`), file reading, directory listing, and log inspection.
- **`flash`**: Codebase orientation, multi-file research, and documentation analysis.
- **`pro` / `inherit`**: Deep logic implementation, complex refactoring, and independent verifier analysis.

### 2. Structured Artifact Mesh (`implementation_plan.md`, `walkthrough.md`)
Subagents exchange structured work products via standard artifacts in their designated workspace directory (`.agents/<agent_folder>/`):
- **`implementation_plan.md`**: Formulated during design phase for architectural or multi-file initiatives (>50 LOC or material ambiguity). Contains problem description, evidence chain, target file diffs/snippets, and verification plan.
- **`walkthrough.md`**: Formulated upon completion. Details actual changes made, test outputs, verification command results, and handoff evidence.

## Seating Doctrine & Event Emission

- **Seating Independence & Non-Author Verification**: The core Pipeline invariant **impl ≠ verifier** applies to AGY native subagents and seats. Candidate code authored by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`).
- **Event Emission**: When milestone transitions or inter-provider updates require mailbox or signed-bus records, events are emitted programmatically via `coordination/bin/send-event` or `scripts/agy_emit.py`:
  ```bash
  coordination/bin/send-event <sender> <recipient> <kind> <subject...> < body.md
  ```

## AGY Launcher Mechanics

`coordination/bin/agy-seat` is backed by `scripts/agy_seat_launcher.py` and uses the AGY protocol adapter `scripts/agy_protocol_model.py`. It establishes clean environment isolation for each seat:
- Sanitizes environment variables (removes inherited `CLAUDE_*`, `CURSOR_*`, `CODEX_*`, `ANTIGRAVITY_*`, and `GIT_*` authority).
- Sets controlled variables: `AGY_SEAT`, `AGY_AGENT_MODE=autonomous`, `AGY_AGENT_ROLE`, `AGY_GIT_INDEX_FILE`, and `GIT_INDEX_FILE` (`.git/index-agy-<seat>`).
- Loads local seat profiles from `~/.agy/pipeline-seat-launcher.toml`:

```toml
[seats.director]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.director2]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.operator]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.operator2]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.coordinator]
model = "gemini-2.5-flash"
service_tier = "fast"
```
