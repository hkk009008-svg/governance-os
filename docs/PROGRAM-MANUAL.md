# PROGRAM MANUAL — Governance OS

**Canonical expression of the user-principal's intent for this program.**
This file defines *what we build* and *how the user wants it operated to full capability*.
All seats read this early and keep it true as the code evolves (same staleness discipline
as ARCHITECTURE.md). When this file and the code disagree, fix this file in the same
commit that exposes the staleness.

---

## §1 — What We Build

<!-- TODO: Replace this placeholder with a 2–4 sentence statement of the program's
     core purpose. Answer: what does this system do, for whom, and why does it
     matter? Be concrete about the end-to-end output a user receives. -->

<PROJECT> turns [INPUT] into [OUTPUT]. The user provides [X]; the program
produces [Y] with [quality bar / SLA / distinguishing characteristic].

---

## §2 — Product Goals and Non-Goals

<!-- TODO: List 3–6 bullet goals (what the program must do well) and 2–4
     explicit non-goals (what it deliberately does NOT do). Non-goals are
     as important as goals — they prevent scope creep and keep the
     architecture honest. -->

**Goals**
- [Goal 1]
- [Goal 2]
- [Goal 3]

**Non-goals**
- [Non-goal 1]
- [Non-goal 2]

---

## §3 — How the Machine Interconnects (Component Map)

<!-- TODO: Describe the top-level components, their responsibilities, and
     how data flows between them. One paragraph per major component is
     sufficient. Link to ARCHITECTURE.md for file:line-level truth.
     Keep this at the "why does this component exist" level, not the
     "what line does this function appear on" level. -->

**[Component A]** — [responsibility]; receives [input] from [source]; emits
[output] to [sink].

**[Component B]** — [responsibility]; [how it fits].

**[Component C]** — [responsibility]; [how it fits].

Data flow summary: [INPUT] → [A] → [B] → [C] → [OUTPUT].

---

## §4 — Operational Contract (Inputs, Outputs, Failure Modes)

<!-- TODO: Define the contract the program exposes to its operators.
     What inputs are required vs optional? What does a successful run
     produce? What are the known failure modes and expected remediation
     paths? This section anchors the "full capability" discussion in §5. -->

**Required inputs:** [list]

**Optional inputs / tunables:** [list]

**Success output:** [description of what a good run produces]

**Known failure modes:**
- [Failure mode 1] — [detection signal] — [remediation]
- [Failure mode 2] — [detection signal] — [remediation]

---

## §5 — Capability-Maximization Playbook

<!-- TODO: This is the most important section for seat operation. List the
     concrete levers an operator can pull to get the highest-quality /
     highest-throughput output from the program. For each lever: what it
     is, when to use it, and what tradeoff it introduces.
     Surface tradeoffs; never silently make the call for the user-principal. -->

The user-principal wants this program operated to its **full capability**.
When a decision trades against that, surface it rather than silently resolving it.

**Lever 1 — [Name]**
[What it does. When to use it. Tradeoff.]

**Lever 2 — [Name]**
[What it does. When to use it. Tradeoff.]

**Lever 3 — [Name]**
[What it does. When to use it. Tradeoff.]

<!-- Add levers as the program matures. -->

---

## §6 — Operating Guidance for Seats

<!-- TODO: Practical guidance for director and operator seats running this
     program. Cover: how to start a run, how to monitor progress, how to
     interpret gate verdicts, how to resume after an interruption, and
     any standing directives the user-principal has issued that are
     program-specific (not in CLAUDE.md). -->

**Starting a run:** [steps]

**Monitoring progress:** [where to look, what signals to watch]

**Gate verdicts:** [how to interpret GO / NITS / FAIL in this program's context]

**Resuming after interruption:** [state to check, files to inspect]

**Standing directives (program-specific):**
- [Directive 1]
- [Directive 2]

---

*Last verified: [YYYY-MM-DD] by [seat/author]. Update this line whenever a section
is re-checked against the running code.*
