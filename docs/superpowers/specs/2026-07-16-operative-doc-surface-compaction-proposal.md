# Proposal: Operative-Doc Surface Compaction (capability-first Phase-3 scope addendum)

Status: ADVISORY PROPOSAL. Authored by a Claude orientation-mode session on
2026-07-16 at the user-principal's request. It grants no scope by itself: the
coordinator routes it, and it enters the capability-first campaign
(`docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`) only
with explicit user-principal approval. No file outside this proposal is
modified by landing it.

## Problem (measured, 2026-07-16)

Every cross-cutting protocol rule is hand-copied onto every operative surface
and held together by phrase-matching tests:

- The two ChatGPT-Pro local-correction sentences required **18 hand-edited
  sites**: 11 Codex/agent-neutral surfaces (AGENTS.md, the Codex continuation
  adapter, 5 `.agents/skills/`, 4 `.codex/agents/` TOMLs), 6 Claude surfaces
  (CLAUDE.md, the Claude continuation adapter, 4 `.claude/skills/`), plus the
  canonical rules tuple in `scripts/codex_protocol_model.py`.
- The consultation contract shipped Codex-side on 2026-07-13 (`5e81c03`) but
  the Claude tree carried **none of it** until 2026-07-16 — three days of
  silent cross-tree drift — because the sync tests
  (`tests/unit/test_protocol_prompt_sync.py`) enumerated only Codex surfaces.
  Drift is caught exactly where a human remembered to enumerate a surface, and
  nowhere else.
- Closing that one gap consumed two agent sessions on 2026-07-16 (one Codex,
  one Claude working in parallel), produced a shared-root WIP collision, a
  coordinator hold event (`2026-07-16T04:59:40Z`), and two preservation
  branches — pure coordination cost for what is semantically a **single
  sentence pair with one authority**.
- Of the ~170 commits on `main` ahead of origin (2026-07-12..07-16), roughly
  100 are coordination, verification-routing, or docs — the overhead the
  capability-first charter exists to reduce. Hand-mirrored operative docs are
  a standing generator of exactly this overhead.

## Proposal

Extend the pattern the repo already trusts — `codex_protocol_model.py` renders
canonical text and tests pin surfaces to the rendering — from *phrase
matching* to *fragment generation*:

1. **One canonical fragment source.** Each shared contract block (consultation
   contract, Lane-V trigger grammar, emergency handling, disagreement
   protocol, shared guardrails, side-effect token fields, capacity split)
   lives exactly once, as a named fragment in the executable model (or a
   `docs/protocol/fragments/` tree the model loads).
2. **Rendered surfaces between markers.** Each operative surface embeds its
   contract blocks between explicit begin/end markers; a committed renderer
   (`scripts/render_protocol_surfaces.py`, new) regenerates the marked regions
   from the fragments plus a per-surface adaptation map (harness name, skill
   pointer, role tail — the only legitimately divergent parts, made explicit
   as data instead of hand-prose).
3. **Byte-pin sync tests.** `test_protocol_prompt_sync.py` collapses from
   ~1,700 lines of phrase tuples to one property: for every registered
   surface, the marked region byte-equals the renderer's output. New surfaces
   register in one table; an unregistered surface containing a fragment marker
   fails the test.
4. **Change protocol.** A policy change edits one fragment + runs the renderer
   + commits fragments, renderer output, and surfaces together — one commit,
   one review, zero drift-window. The per-surface adaptation map is the only
   place harness divergence can appear, so review attention concentrates
   there.

## Why Phase 3

Phase 3 of the compact-kernel campaign (control-plane convergence: triggered
boundaries + real callers) is where v1 surfaces get re-bound to the compact
kernel. Doing surface compaction there means the re-binding is done once,
against generated surfaces, instead of re-mirroring N hand-copies during the
migration and re-introducing the drift class the shadow-parity work just
closed. It also directly serves the charter sentence: "no ceremony that lacks
a demonstrated safety or correctness purpose" — 17-site hand-mirroring is
ceremony; the safety purpose (identical contract everywhere) is delivered
cheaper by generation.

## Non-goals and constraints

- **No authority change.** Fragments carry the same text the surfaces carry
  today; v1 remains authoritative; nothing about seat authority, verdicts, or
  side-effect gating changes.
- **Harness-specific adaptations stay explicit** (Claude vs Codex commands,
  skill pointers, subagent boundaries) — as declared adaptation data, never
  silently normalized away.
- **Incremental adoption:** start with the consultation contract (the block
  with the freshest drift evidence and the cleanest 17-surface inventory),
  prove the renderer + byte-pin loop, then migrate the other shared blocks
  one per slice with normal R-BRIEF/Lane-V discipline.
- **R-INDEPENDENCE applies:** the renderer composes text into operative
  context; its design review enumerates injection/escaping/marker-collision
  cases before implementation.

## Requested decision

Add "operative-doc surface compaction" to the capability-first Phase-3 scope
(one design slice + incremental migration slices), or reject with reason. On
approval, the coordinator routes a design R-BRIEF per the four-seat protocol;
this proposal then serves as the problem-statement input to that brief, not as
its design.
