# Ledger CLI Four-Seat Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Codex CLI bridge that lets Pipeline stay the four-seat governance kernel while evidence-ledger is worked as the target repo.

**Architecture:** Pipeline remains the single source for Codex seat mechanics. A new Codex bridge doc explains the cross-repo ledger launch path, `scripts/codex_protocol_model.py` exposes that bridge in executable model text, and core role prompts carry the cross-repo hygiene rule. Focused tests pin the new bridge and replace stale Codex verification selectors with tests that exist in this repo.

**Tech Stack:** Markdown docs, Python 3, pytest, TOML prompt files, existing Pipeline protocol scripts.

## Global Constraints

- Work from `/Users/hyungkoookkim/Pipeline` unless a step explicitly reads `/Users/hyungkoookkim/evidence-ledger`.
- Do not modify `/Users/hyungkoookkim/evidence-ledger` in this implementation plan. Ledger repo inspection is read-only.
- Prefix ordinary git and pytest commands with `env -u GIT_INDEX_FILE`.
- Use `apply_patch` for manual edits.
- Preserve unrelated dirty work. Use explicit pathspecs for staging and commits.
- No mailbox cursor consumption, mailbox event emission, lock claim, pod or paid API spend, remote push, or evidence-ledger product edit.
- Pipeline readiness bridge remains the default. Codex becomes a live seat only when the prompt names `director`, `director2`, `operator`, or `operator2`; coordinator only when explicitly asked to reconcile, route, gate, or operate cross-seat state.
- Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing evidence-ledger fixes.
- Cross-repo handoffs must record both Pipeline and evidence-ledger repo heads when active work spans both repos.

Current ledger checkout caveat, verified read-only:

```text
$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short
 M ARCHITECTURE.md
 M DECISIONS.md
 M import/load_agency.py
 M import/run_import.py
 M import/tests/make_agency_fixture.py
 M import/tests/test_agency_load.py
 M import/tests/test_load_agency_unit.py
```

---

## File Structure

- `tests/unit/test_codex_ledger_bridge.py`: new focused regression tests for the ledger CLI bridge, stale selector cleanup, docs, and role prompts.
- `scripts/codex_protocol_model.py`: executable Codex model gains the ledger bridge contract, current verification command rendering, and surface summary entries.
- `scripts/protocol_doctor.py`: replaces stale missing test selectors with current test selectors.
- `docs/protocol/codex/ledger-cli-adoption.md`: new bridge runbook for Codex CLI work on evidence-ledger.
- `docs/protocol/codex/continuation.md`: links the bridge and updates verification commands.
- `docs/protocol/protocol-assembly-map.md`: routes target-repo CLI bridge material and fixes stale test examples.
- `AGENTS.md`: root doc map gains the ledger bridge route.
- `.agents/skills/four-seat-protocol/SKILL.md`: runtime checklist points Codex to the bridge when ledger target work is routed.
- `.codex/agents/readiness-bridge.toml`: read-only agent learns the evidence-ledger bridge but remains non-mutating.
- `.codex/agents/protocol-director.toml`: director seats learn the ledger bridge and cross-repo hygiene.
- `.codex/agents/protocol-operator.toml`: operator seats learn the ledger bridge and read-only/default verification posture in ledger.
- `.codex/agents/protocol-coordinator.toml`: coordinator learns ledger reconciliation limits and no product-fix boundary.

---

### Task 1: Executable Model And Current Verification Selectors

**Files:**
- Create: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `scripts/protocol_doctor.py`

**Interfaces:**
- Consumes: existing `codex_protocol_model` import path exposed through `tests/conftest.py`.
- Produces:
  - `codex_protocol_model.LEDGER_CLI_BRIDGE: dict[str, object]`
  - `codex_protocol_model.CODEX_VERIFICATION_COMMANDS: tuple[str, ...]`
  - `codex_protocol_model.render_ledger_cli_bridge() -> str`
  - `codex_protocol_model.render_codex_verification_commands() -> str`

- [ ] **Step 1: Confirm the stale selector baseline**

Run:

```bash
env -u GIT_INDEX_FILE rg -n "test_codex_protocol_model|test_codex_protocol_artifacts|test_protocol_capacity_board|test_coordination_bin|test_check_coordination" docs/protocol/codex/continuation.md scripts/protocol_doctor.py docs/protocol/protocol-assembly-map.md
```

Expected: output includes stale selectors in `docs/protocol/codex/continuation.md`, `scripts/protocol_doctor.py`, and `docs/protocol/protocol-assembly-map.md`.

- [ ] **Step 2: Write failing model and selector tests**

Create `tests/unit/test_codex_ledger_bridge.py` with this content:

```python
from __future__ import annotations

from pathlib import Path

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]
STALE_SELECTORS = (
    "tests/unit/test_codex_protocol_model.py",
    "tests/unit/test_codex_protocol_artifacts.py",
    "tests/unit/test_protocol_capacity_board.py",
    "tests/unit/test_coordination_bin.py",
    "tests/unit/test_check_coordination.py",
)
CURRENT_PROTOCOL_TESTS = (
    "tests/unit/test_imports_smoke.py",
    "tests/unit/test_protocol_mailbox.py",
    "tests/unit/test_status.py",
    "tests/unit/test_ceremony_gates.py",
    "tests/unit/test_codex_ledger_bridge.py",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ledger_bridge_contract_declares_kernel_target_and_hygiene():
    bridge = model.LEDGER_CLI_BRIDGE
    assert bridge["doc_path"] == "docs/protocol/codex/ledger-cli-adoption.md"
    assert bridge["pipeline_kernel"] == "/Users/hyungkoookkim/Pipeline"
    assert bridge["target_repo"] == "/Users/hyungkoookkim/evidence-ledger"
    assert "env -u GIT_INDEX_FILE" in "\n".join(bridge["cross_repo_git_rules"])

    rendered = model.render_ledger_cli_bridge()
    assert "/Users/hyungkoookkim/Pipeline" in rendered
    assert "/Users/hyungkoookkim/evidence-ledger" in rendered
    assert "readiness bridge" in rendered
    assert "named seat" in rendered
    assert "coordinator may reconcile" in rendered
    assert "env -u GIT_INDEX_FILE" in rendered


def test_codex_surfaces_include_ledger_bridge_doc():
    assert (
        "docs/protocol/codex/ledger-cli-adoption.md",
        "ledger CLI adoption bridge for evidence-ledger target work",
    ) in model.CODEX_SURFACES


def test_model_verification_commands_are_current():
    rendered = model.render_codex_verification_commands()
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in rendered
        assert (ROOT / selector).exists(), selector
    for selector in STALE_SELECTORS:
        assert selector not in rendered


def test_protocol_doctor_uses_current_test_selectors():
    text = _read("scripts/protocol_doctor.py")
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in text
    for selector in STALE_SELECTORS:
        assert selector not in text
```

- [ ] **Step 3: Run the tests to verify they fail**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: failure because `codex_protocol_model.LEDGER_CLI_BRIDGE` is not defined.

- [ ] **Step 4: Add the ledger bridge contract to `scripts/codex_protocol_model.py`**

Insert this block after `LIVE_LOOP_STEPS` and before `CODEX_SURFACES`:

```python
LEDGER_CLI_BRIDGE = {
    "doc_path": "docs/protocol/codex/ledger-cli-adoption.md",
    "pipeline_kernel": "/Users/hyungkoookkim/Pipeline",
    "target_repo": "/Users/hyungkoookkim/evidence-ledger",
    "kernel_rules": (
        "Pipeline remains the Codex four-seat governance kernel.",
        "Evidence-ledger remains the product repo and owns product-local truth.",
        "Start as readiness bridge unless the prompt names a live seat or coordinator.",
        "A named seat may work on ledger only inside the explicit route.",
        "Coordinator may reconcile ledger work from durable evidence but may not author behavior-changing product fixes.",
    ),
    "cross_repo_git_rules": (
        "Prefix every ordinary cross-repo git and pytest command with env -u GIT_INDEX_FILE.",
        "Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.",
        "Record both Pipeline and evidence-ledger heads in cross-repo handoffs.",
        "Do not copy the whole Pipeline protocol tree into evidence-ledger.",
    ),
}

CODEX_VERIFICATION_COMMANDS = (
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
    "tests/unit/test_imports_smoke.py "
    "tests/unit/test_protocol_mailbox.py "
    "tests/unit/test_status.py "
    "tests/unit/test_ceremony_gates.py "
    "tests/unit/test_codex_ledger_bridge.py -q",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
)
```

Update `CODEX_SURFACES` so it contains this entry immediately after the Codex continuation entry:

```python
    (
        LEDGER_CLI_BRIDGE["doc_path"],
        "ledger CLI adoption bridge for evidence-ledger target work",
    ),
```

Add these functions after `render_seat_subagent_development()`:

```python
def render_ledger_cli_bridge() -> str:
    """Return the Codex bridge contract for evidence-ledger target work."""
    lines = [
        "Ledger CLI Bridge:",
        f"- Pipeline kernel: `{LEDGER_CLI_BRIDGE['pipeline_kernel']}`",
        f"- Target repo: `{LEDGER_CLI_BRIDGE['target_repo']}`",
        f"- Bridge doc: `{LEDGER_CLI_BRIDGE['doc_path']}`",
        "- Runtime:",
    ]
    lines.extend(f"  - {rule}" for rule in LEDGER_CLI_BRIDGE["kernel_rules"])
    lines.append("- Cross-repo hygiene:")
    lines.extend(f"  - {rule}" for rule in LEDGER_CLI_BRIDGE["cross_repo_git_rules"])
    return "\n".join(lines)


def render_codex_verification_commands() -> str:
    """Return current Codex protocol verification commands."""
    lines = ["Codex verification commands:"]
    lines.extend(f"- `{command}`" for command in CODEX_VERIFICATION_COMMANDS)
    return "\n".join(lines)
```

Update `render_surface_summary()` by adding this line before `"Codex surfaces:"`:

```python
        "Ledger CLI Bridge: Pipeline kernel -> evidence-ledger target via "
        + LEDGER_CLI_BRIDGE["doc_path"],
```

Update `main()` so it prints both new sections after Seat Subagent Development:

```python
    print("## Ledger CLI Bridge")
    print(render_ledger_cli_bridge())
    print()
    print("## Codex Verification Commands")
    print(render_codex_verification_commands())
    print()
```

- [ ] **Step 5: Replace stale selectors in `scripts/protocol_doctor.py`**

In the pytest command list, replace the five missing selectors with the current selectors:

```python
                "tests/unit/test_imports_smoke.py",
                "tests/unit/test_protocol_mailbox.py",
                "tests/unit/test_status.py",
                "tests/unit/test_ceremony_gates.py",
                "tests/unit/test_codex_ledger_bridge.py",
```

Keep `"-q"` as the final pytest argument.

- [ ] **Step 6: Run the focused tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: `4 passed`.

- [ ] **Step 7: Run current protocol-adjacent tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: all selected tests pass.

- [ ] **Step 8: Inspect and commit Task 1**

Run:

```bash
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git add tests/unit/test_codex_ledger_bridge.py scripts/codex_protocol_model.py scripts/protocol_doctor.py
env -u GIT_INDEX_FILE git commit -m "test(codex): pin ledger bridge model and current selectors" -- tests/unit/test_codex_ledger_bridge.py scripts/codex_protocol_model.py scripts/protocol_doctor.py
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: commit touches exactly the three Task 1 files.

---

### Task 2: Codex Bridge Docs, Skill Routing, And Assembly Map

**Files:**
- Create: `docs/protocol/codex/ledger-cli-adoption.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/protocol-assembly-map.md`
- Modify: `AGENTS.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Consumes:
  - `codex_protocol_model.LEDGER_CLI_BRIDGE`
  - `codex_protocol_model.render_ledger_cli_bridge()`
  - `codex_protocol_model.render_codex_verification_commands()`
- Produces:
  - committed bridge doc at `docs/protocol/codex/ledger-cli-adoption.md`
  - docs and skill references to that bridge
  - protocol assembly map entry for target-repo CLI adoption

- [ ] **Step 1: Extend tests for docs and stale selector cleanup**

Append these tests to `tests/unit/test_codex_ledger_bridge.py`:

```python
REQUIRED_LEDGER_DOC_PHRASES = (
    "Pipeline remains the Codex four-seat governance kernel.",
    "/Users/hyungkoookkim/evidence-ledger",
    "env -u GIT_INDEX_FILE",
    "Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.",
    "Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.",
    "Cross-repo handoffs record both repo heads.",
)
DOC_SURFACES = (
    "docs/protocol/codex/ledger-cli-adoption.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/protocol-assembly-map.md",
    "AGENTS.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
)


def test_ledger_bridge_doc_exists_and_names_required_boundaries():
    text = _read("docs/protocol/codex/ledger-cli-adoption.md")
    for phrase in REQUIRED_LEDGER_DOC_PHRASES:
        assert phrase in text


def test_doc_surfaces_route_to_ledger_bridge_without_stale_selectors():
    for path in DOC_SURFACES:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        for selector in STALE_SELECTORS:
            assert selector not in text


def test_protocol_assembly_renderer_includes_target_repo_bridge():
    rendered = model.render_protocol_assembly_map()
    assert "Target-repo CLI adoption bridge" in rendered
    assert "docs/protocol/codex/ledger-cli-adoption.md" in rendered
```

- [ ] **Step 2: Run the docs tests to verify they fail**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: failure because `docs/protocol/codex/ledger-cli-adoption.md` does not exist and the assembly renderer lacks the target-repo bridge entry.

- [ ] **Step 3: Create `docs/protocol/codex/ledger-cli-adoption.md`**

Create the file with this content:

```markdown
# Ledger CLI Adoption Bridge

This bridge is for Codex CLI sessions working on
`/Users/hyungkoookkim/evidence-ledger` while Pipeline remains the governance
kernel.

Pipeline remains the Codex four-seat governance kernel. Evidence-ledger remains
the product repo and owns product-local truth.

Use this bridge only when the user or parent prompt routes work to
`/Users/hyungkoookkim/evidence-ledger`.

## Authority Boundary

- Readiness bridge: may inspect and report. It must not mutate evidence-ledger.
- Named live seat: may work on evidence-ledger only inside the explicit route.
- Coordinator: may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.
- Subagent: receives only the parent prompt, allowed paths, acceptance evidence,
  forbidden side effects, and git hygiene. It does not inherit mailbox, cursor,
  GO, route, lock, push, or spend authority.

## Start From Pipeline

Readiness bridge:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

Named live seat:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Coordinator:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Read relevant Pipeline mailbox bodies before protocol decisions. Counts alone
are not enough.

## Enter Evidence-Ledger

Before product edits, inspect the target repo from a clean command environment:

```bash
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log --oneline -5
```

Read evidence-ledger CLAUDE.md and AGENTS.md before product edits. If those
files disagree with Pipeline, user instructions win first; evidence-ledger
controls product behavior, and Pipeline controls Codex seat mechanics.

## Cross-Repo Git Hygiene

- Prefix every ordinary cross-repo git and pytest command with `env -u GIT_INDEX_FILE`.
- Do not let a Pipeline seat index follow `cd` into evidence-ledger.
- Do not stage or commit evidence-ledger files from a Pipeline seat index.
- Use explicit pathspecs for any parent-authorized staging or commit.
- Preserve unrelated evidence-ledger dirty work.

## Handoffs

Cross-repo handoffs record both repo heads.

Use this minimum body when active work spans both repos:

```text
Pipeline HEAD: paste output from `env -u GIT_INDEX_FILE git log -1 --oneline`
Evidence-ledger HEAD: paste output from `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log -1 --oneline`
Pipeline status: paste output from `env -u GIT_INDEX_FILE git status --short`, or write `clean`
Evidence-ledger status: paste output from `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short`, or write `clean`
Seat: write one of `director`, `director2`, `operator`, `operator2`, or `coordinator`
Authority used: write one of `readiness report`, `live-seat route`, `operator verification`, or `coordinator reconciliation`
Evidence run: paste commands and results
Side effects not taken: push, lock, cursor consume, mailbox event, spend
Exact next trigger: paste the next prompt or seat event
```

Replace every field value with concrete command output or one of the listed
values before committing a real handoff. Do not commit this example body as-is.

## Verification

Use current Pipeline protocol checks:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Use evidence-ledger's own verification commands for product changes after
reading that repo's local docs.
```

- [ ] **Step 4: Add the bridge to the Codex adapter**

In `docs/protocol/codex/continuation.md`, add this section after the opening paragraphs and before `## Runtime modes`:

```markdown
## Ledger CLI Adoption Bridge

For work routed to `/Users/hyungkoookkim/evidence-ledger`, use
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
Pipeline remains the Codex four-seat governance kernel; evidence-ledger owns
product-local truth. Cross-repo git and pytest commands use
`env -u GIT_INDEX_FILE` so Pipeline seat indexes do not leak into ledger work.
```

Replace the `## Verification Commands` code block with:

```markdown
```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
.venv/bin/python scripts/wave_gate_check.py 2
```
```

- [ ] **Step 5: Add the bridge to the protocol assembly map**

In `docs/protocol/protocol-assembly-map.md`, add this row after the Codex protocol mapping row:

```markdown
| Target-repo CLI adoption bridge | `docs/protocol/codex/ledger-cli-adoption.md` | Evidence-ledger CLI bridge | Target-repo adoption is Codex-specific mechanics and should not duplicate universal protocol policy. |
```

Update the Protocol tool tests example row to use current examples:

```markdown
| Protocol tool tests | `tests/unit/` | `test_protocol_mailbox.py`, `test_codex_ledger_bridge.py` | Tool contracts should be enforced by tests so prose drift is caught. |
```

Add this line to the quick routing check:

```text
Target-repo Codex bridge?   -> docs/protocol/codex/ledger-cli-adoption.md
```

- [ ] **Step 6: Add the bridge to AGENTS.md**

In the repo doc map table in `AGENTS.md`, add this row after the Codex continuation row:

```markdown
| Work on evidence-ledger from Codex CLI as a four-seat unit | [docs/protocol/codex/ledger-cli-adoption.md](docs/protocol/codex/ledger-cli-adoption.md) |
```

- [ ] **Step 7: Add the bridge to the four-seat skill**

In `.agents/skills/four-seat-protocol/SKILL.md`, add this section before `## Related files`:

```markdown
## Ledger CLI bridge

When the parent prompt routes Codex work to `/Users/hyungkoookkim/evidence-ledger`, read `docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.

- Pipeline remains the Codex four-seat governance kernel.
- Evidence-ledger owns product-local truth.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.
- Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.
```

Also add this bullet to the related files list:

```markdown
- Ledger CLI bridge: `docs/protocol/codex/ledger-cli-adoption.md`
```

- [ ] **Step 8: Add target-repo bridge to `scripts/codex_protocol_model.py` assembly portions**

In `PROTOCOL_ASSEMBLY_PORTIONS`, add this tuple after the Codex protocol mapping tuple:

```python
    (
        "Target-repo CLI adoption bridge",
        LEDGER_CLI_BRIDGE["doc_path"],
        "Target-repo adoption is Codex-specific mechanics and should not duplicate universal protocol policy.",
    ),
```

- [ ] **Step 9: Run the focused docs tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: all tests in `test_codex_ledger_bridge.py` pass.

- [ ] **Step 10: Run current protocol-adjacent tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: all selected tests pass.

- [ ] **Step 11: Inspect and commit Task 2**

Run:

```bash
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git add docs/protocol/codex/ledger-cli-adoption.md docs/protocol/codex/continuation.md docs/protocol/protocol-assembly-map.md AGENTS.md .agents/skills/four-seat-protocol/SKILL.md scripts/codex_protocol_model.py tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git commit -m "docs(codex): add ledger CLI adoption bridge" -- docs/protocol/codex/ledger-cli-adoption.md docs/protocol/codex/continuation.md docs/protocol/protocol-assembly-map.md AGENTS.md .agents/skills/four-seat-protocol/SKILL.md scripts/codex_protocol_model.py tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: commit touches exactly the seven Task 2 files.

---

### Task 3: Core Codex Role Prompts And Final Verification

**Files:**
- Modify: `.codex/agents/readiness-bridge.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Consumes: bridge doc from Task 2.
- Produces: core role prompts that point to the bridge and preserve cross-repo authority boundaries.

- [ ] **Step 1: Extend tests for core role prompts**

Append these tests to `tests/unit/test_codex_ledger_bridge.py`:

```python
CORE_CODEX_ROLE_PROMPTS = (
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
)


def test_core_codex_role_prompts_reference_ledger_bridge_and_hygiene():
    for path in CORE_CODEX_ROLE_PROMPTS:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        assert "/Users/hyungkoookkim/evidence-ledger" in text
        assert "env -u GIT_INDEX_FILE" in text
        assert "Pipeline remains the Codex four-seat governance kernel" in text
        assert "evidence-ledger owns product-local truth" in text


def test_readiness_and_coordinator_prompts_keep_mutation_boundaries():
    readiness = _read(".codex/agents/readiness-bridge.toml")
    coordinator = _read(".codex/agents/protocol-coordinator.toml")
    assert "A readiness bridge must not mutate evidence-ledger." in readiness
    assert "Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes." in coordinator
```

- [ ] **Step 2: Run the prompt tests to verify they fail**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: failure because core role prompts do not yet mention the ledger bridge.

- [ ] **Step 3: Update readiness bridge prompt**

In `.codex/agents/readiness-bridge.toml`, add this block after the `Harness inhabitance:` block:

```text
Ledger CLI bridge:
- For work routed to `/Users/hyungkoookkim/evidence-ledger`, read
  `docs/protocol/codex/ledger-cli-adoption.md` before inspecting the target repo.
- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger owns product-local truth.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- A readiness bridge must not mutate evidence-ledger.
```

- [ ] **Step 4: Update director prompt**

In `.codex/agents/protocol-director.toml`, add this block after the `Authority boundary:` block:

```text
Ledger CLI bridge:
- For work routed to `/Users/hyungkoookkim/evidence-ledger`, read
  `docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger owns product-local truth.
- Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- Record both Pipeline and evidence-ledger heads in cross-repo handoffs.
```

- [ ] **Step 5: Update operator prompt**

In `.codex/agents/protocol-operator.toml`, add this block after the `Authority boundary:` block:

```text
Ledger CLI bridge:
- For verification routed to `/Users/hyungkoookkim/evidence-ledger`, read
  `docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger owns product-local truth.
- Read evidence-ledger CLAUDE.md and AGENTS.md before product verification.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- Record both Pipeline and evidence-ledger heads in cross-repo verification reports or handoffs.
```

- [ ] **Step 6: Update coordinator prompt**

In `.codex/agents/protocol-coordinator.toml`, add this block after the `Authority boundary:` block:

```text
Ledger CLI bridge:
- For reconciliation involving `/Users/hyungkoookkim/evidence-ledger`, read
  `docs/protocol/codex/ledger-cli-adoption.md` before inspecting the target repo.
- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger owns product-local truth.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- Cross-repo handoffs record both Pipeline and evidence-ledger heads.
- Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.
```

- [ ] **Step 7: Run focused prompt tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q
```

Expected: all tests in `test_codex_ledger_bridge.py` pass.

- [ ] **Step 8: Run full selected verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py --skip-ceremony
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected:

- pytest exits 0;
- continuation readiness exits 0 and includes `Ledger CLI Bridge` in the Codex Harness Model section;
- `ci_smoke.py` exits 0. Existing stale commit-SHA warnings may still print, but no new stale selector warnings should be introduced by this plan.

- [ ] **Step 9: Inspect and commit Task 3**

Run:

```bash
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git add .codex/agents/readiness-bridge.toml .codex/agents/protocol-director.toml .codex/agents/protocol-operator.toml .codex/agents/protocol-coordinator.toml tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git commit -m "docs(codex): teach role agents ledger CLI bridge" -- .codex/agents/readiness-bridge.toml .codex/agents/protocol-director.toml .codex/agents/protocol-operator.toml .codex/agents/protocol-coordinator.toml tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: commit touches exactly the five Task 3 files.

---

## Final Verification

After all three tasks are committed, run:

```bash
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py --skip-ceremony
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected:

- Pipeline working tree is clean except any pre-existing unrelated user work.
- Latest commits are the three task commits.
- selected pytest exits 0.
- continuation readiness exits 0 and names the ledger bridge.
- smoke exits 0.
- no push has been attempted.
- evidence-ledger remains unmodified by this implementation.

## Execution Notes

- Use one commit per task.
- If another seat advances `HEAD` before a task commit, rerun `env -u GIT_INDEX_FILE git log --oneline -5` and `env -u GIT_INDEX_FILE git status --short` before staging.
- If an implementation step reveals a new stale factual claim, update the relevant doc in the same task commit and cite the command output.
- Do not run `scripts/protocol_doctor.py` as the final proof in this repo state. The script includes broader Wave checks that can fail when no active remediation inventory exists; this plan pins the stale-selector cleanup through focused tests and `ci_smoke.py`.
