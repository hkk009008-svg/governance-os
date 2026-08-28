# Guideline — Using & Maintaining `docs/PROGRAM-MANUAL.md`

*The manual is the canonical expression of the user-principal's intent for
Pipeline: what we build, goals and non-goals, how the machine interconnects,
the operational contract, and role guidance. It is a compact intent layer
(~130 lines), not a deep code reference; it was regenerated down from a
~219KB snapshot whose anchors rotted faster than they helped.*

> Truth hierarchy: **current source and `ARCHITECTURE.md` win on any factual
> conflict** (code beats docs; `ARCHITECTURE.md` is the verified-truth doc). The
> manual is the intent + operating layer on top of them.

-----

## Part 1 — Using the manual

### 1.1 Load policy

- **Pull on demand, not at session start.** Read this guide first; open the
  manual when the task actually needs user-principal intent — program-level
  orientation, capability planning, scope or non-goal questions, or manual
  maintenance.
- **Read by section.** The manual's sections are short; open what the task
  needs:

  |Need                                          |Read |
  |----------------------------------------------|-----|
  |What Pipeline is for / what we build          |§1–§2|
  |How modes, mailbox, and review interconnect   |§3   |
  |Required inputs and success outputs           |§4   |
  |Known failure modes                           |§4   |
  |Capability-maximization defaults              |§5   |
  |Per-role operating guidance                   |§6   |
- **Dispatching a subagent:** pass only the relevant section + the
  task-specific requirement — never inherited whole-doc prose.

### 1.2 Trust model (when to believe it)

- **Intent ages slowly; specifics age fast.** Trust the goals, non-goals, and
  boundaries more than any named script or path; re-grep a symbol before
  relying on it.
- **On any factual conflict, verify against current source and
  `ARCHITECTURE.md`, which win** — the manual loses.
- The manual intentionally does not restate the Compact Pair lifecycle
  grammar; `pipeline/codex_protocol_model.py` owns it.

-----

## Part 2 — Maintaining the manual

### 2.1 Hand-edit discipline

- **Add-only / localized:** correct the affected claim; don't rewrite
  surrounding prose.
- **Prefer symbol and path names over line numbers** so the edit doesn't
  immediately re-rot.
- **No semantic/behavioral claim changes without verifying against source**
  and citing the command that confirmed it (ADR-013: verification travels
  with the claim).
- **No new aspirational guarantees** ("never fails", "fully safe
  unattended"). Preserve existing caveats; the manual documents boundaries,
  it doesn't paper over them.
- Intent changes come from the user-principal; agents correct factual drift,
  they do not invent new goals.

### 2.2 Make drift fail loud

- `pipeline/check_doc_claims.py` covers `docs/PROGRAM-MANUAL.md`; the
  governance aggregate runs an advisory anchor-drift WARN on it. Run
  `bin/pipeline check docs docs/PROGRAM-MANUAL.md` after edits that touch
  anchors. That checker verifies a cited line only where a backticked symbol
  precedes the anchor; an unbound anchor is listed by `--list-unbound` and
  never gates, so a bare `path:N` still has to be read by hand.
- Treat unresolved anchors as a gate, not a report: silent staleness is the
  enemy; a noisy drift report is the fix.

### 2.3 Anti-duplication

- One home per fact. If something belongs in `ARCHITECTURE.md` (verified
  repository facts) or a continuation adapter (provider mechanics), link to
  it; don't restate it here where it can diverge.

-----

## When in doubt

The manual tells you **what the user-principal wants the system to be**;
current source and `ARCHITECTURE.md` tell you **what is true right now**. Use
the manual to align direction; verify against source before you act on a
specific number, path, or claim. If the two disagree, the source wins and the
manual needs a correction.
