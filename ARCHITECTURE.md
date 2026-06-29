# ARCHITECTURE.md — <PROJECT_NAME>

> **Truth lives here; CLAUDE.md is the process layer.**
> All load-bearing facts about this codebase — file:line references, module
> responsibilities, invariants — are recorded in this file. When CLAUDE.md and
> this file disagree about a fact, this file wins. Fix staleness in the same
> commit that exposes it.

*Last verified: <date> @ <sha>*

---

## §1 Purpose

<!-- One-paragraph statement of what the program does and what problem it solves. -->
<fill-in: one-paragraph summary of <PROJECT>'s purpose>

---

## §2 Topology

<!-- Describe the top-level component graph: entry points, major subsystems, and
     how data/control flows between them. Use a brief ASCII or bullet graph.
     Every component named here must have a §N section below. -->
<fill-in: component graph or bullet list — e.g., entry-point → subsystem-A → subsystem-B>

**Entry point(s):**
- `<fill-in: path/to/main.py>` — <fill-in: one-line role>

**Key directories:**
| Path | Role |
|------|------|
| `<fill-in>` | <fill-in> |
| `<fill-in>` | <fill-in> |
| `<fill-in>` | <fill-in> |

---

## §3 Module Map

<!-- List every load-bearing module with its file path and the ONE function/class
     that is its public contract. Format: `symbol (file:line)` — this exact
     pattern is what scripts/ci_smoke.py's _project_smoke() gate checks. -->

| Symbol | File:line | Role |
|--------|-----------|------|
| `<fill-in: ClassName>` | `<fill-in: path/to/file.py:N>` | <fill-in: one-line role> |
| `<fill-in: function_name>` | `<fill-in: path/to/file.py:N>` | <fill-in: one-line role> |

---

## §4 Subsystem — <fill-in: SubsystemA>

<!-- One section per top-level subsystem. State the invariant the subsystem owns,
     its public interface, and any sharp edges a caller must know. -->

**Invariant:** <fill-in: what must always be true about this subsystem>

**Public interface:**
- `<fill-in: symbol> (<file:line>)` — <fill-in: one-line description>

**Sharp edges / known traps:**
- <fill-in: e.g., "Not thread-safe; callers must hold X lock">

---

## §5 Subsystem — <fill-in: SubsystemB>

**Invariant:** <fill-in>

**Public interface:**
- `<fill-in: symbol> (<file:line>)` — <fill-in>

**Sharp edges / known traps:**
- <fill-in>

---

## §6 Data Model

<!-- Describe the primary data structures / schemas / DB tables that flow through
     the program. Note the canonical write site for each field — type declarations
     are NOT write evidence (per Rule #12). -->

**Primary schema / struct: `<fill-in>`**
- `<field>` — written at `<file:line>`; <fill-in: semantics>
- `<field>` — written at `<file:line>`; <fill-in: semantics>

---

## §7 Configuration

<!-- Where does config live? What are the must-know keys? What breaks silently
     if a key is absent or wrong? -->

Config file(s): `<fill-in: path>`

| Key | Default | Effect if wrong |
|-----|---------|-----------------|
| `<fill-in>` | `<fill-in>` | <fill-in> |

---

## §8 External Dependencies

<!-- List third-party services, APIs, or binaries the program requires at runtime.
     Note the version pin or minimum version and what breaks if missing. -->

| Dependency | Version | Required for |
|------------|---------|--------------|
| `<fill-in>` | `<fill-in>` | <fill-in> |

---

## §9 Error Handling & Failure Modes

<!-- Document the failure modes that are non-obvious or have caused bugs.
     For each: what triggers it, what the symptom is, and the fix or mitigation. -->

| Failure mode | Trigger | Symptom | Mitigation |
|--------------|---------|---------|------------|
| <fill-in> | <fill-in> | <fill-in> | <fill-in> |

---

## §10 Performance & Scaling Notes

<!-- Record any measured (not estimated) throughput limits, memory ceilings, or
     O(N) cliffs. Label estimates explicitly. All numbers must be backed by a
     committed script per R-MEASURE. -->

- <fill-in: "X operation is O(N) in Y; measured limit = Z at commit <sha>">

---

## §11 Decision Log (ADR index)

<!-- Point to DECISIONS.md for the full ADR log; list only the ADRs that directly
     constrain code in this file (so a reader knows which ADRs are load-bearing). -->

Full ADR log: [DECISIONS.md](DECISIONS.md)

Load-bearing ADRs for this codebase:
- **ADR-001** — <fill-in: one-line summary; constraint it imposes>

---

## §N Smoke Invariants

<!-- This section is the contract for scripts/ci_smoke.py's _project_smoke()
     function. List each invariant as a checkable assertion: symbol present at
     file:line, import succeeds, config key exists, etc.
     The smoke script MUST verify every claim listed here and fail fast if any
     assertion breaks. -->

The following invariants are checked by `scripts/ci_smoke.py` → `_project_smoke()`:

1. `<fill-in: symbol> (<file:line>)` exists and is importable.
2. `<fill-in: config key>` is present in `<fill-in: config path>`.
3. <fill-in: any other fast-checkable structural invariant>

**Adding a new invariant:** add it here AND add the matching assertion in
`_project_smoke()` in the same commit. Never let this list drift from the script.

---

*Last verified: <YYYY-MM-DD> @ <git-sha>*
