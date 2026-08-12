# Memory and skill evolution — analysis, research, staged design

Status: PLAN plus landing record. Runtime that this document specifies
is the checkpoint parser/writer, `scripts/draft_checkpoint.py`, slope
continuity/learning series, `writing-skills`, skill-use reporting, and
frozen `tests/skill_packs/`. The mailbox archive is proposed, not
executed. ADR: ADR-068 (free at plan time except same-change forward
refs in `writing-skills` and `docs/protocol/learning/skill-use.md`;
ADR-035 grep is recorded in the ADR).

## 1. Current system (measured, not recalled)

Memory is git-native, not a vector store. The learning plane (ADR-067,
`docs/protocol/learning/contract.md`) is built:

- extract (`scripts/learning_extract.py`) drafts only (O4);
- `learning-candidate` mailbox events;
- fail-closed dispositions at publication (`mailbox_writer.py` Stage 2b);
- promotion is the compact pair;
- FTS5 index (`scripts/learning_index.py`) is local-only, advisory,
  never auto-injected.

Throughput gap at plan time: two learning-candidate events ever
(2026-07-31, one superseding the other); `logs/learning/outcomes.jsonl`
had one baseline row. No durable checkpoint artifact existed.
AGENTS.md item 7 named the payload; nothing structured it.
`slope_metrics.py` listed `recovery_after_compaction` as
`not_measurable`.

Live gate at plan start: FAIL
`review_projection_unavailable: mailbox event has multiple introductions`
from PR #15 delete (`2a91d32`) / PR #16 revert (`ffa0323`) re-introducing
889 events. Unread cursors were large; unread backlog is not orientation
debt (doctrine, not a cursor fast-forward).

Skills: twelve canonical bodies under `.agents/skills/`; `.claude/`
stubs plus declared seat-family adaptations (O2). No usage telemetry,
no writing-skills skill, R-SKILL still a transfer TODO. Doc drift:
README called Stage 2b refusals advisory (false after 2b landed);
ARCHITECTURE said four stubs (disk had five, including
`isolate-a-variable`).

Contract I1–I7 still binding: no autonomous canonical writes, no
embeddings (O5), no usage-counts-as-lifecycle-evidence, extractor
scratch-only (O4), mailbox archive deferred (O3).

## 2. Research provenance (adopt / skip)

Adopted patterns, mapped onto existing seams rather than transplanted:

- Anthropic structured note-taking / MEMORY.md index → checkpoint
  statement as a typed `findings` body, not a new store.
- ACE delta updates → cadence via existing Supersedes + content hashes;
  no in-place candidate patch.
- Auto Dream as scheduled curation → not an autonomous writer; archive
  and metrics stay human/seat-triggered.
- Agent Skills eval-first authoring + writing-skills →
  `.agents/skills/writing-skills/SKILL.md` plus frozen
  `tests/skill_packs/`.
- AWM/ExpeL → `procedure` candidates from retros, via the existing
  extractor, not a new memory type.

Skipped: Mem0/Zep/Letta, embeddings, auto prompt injection,
helpful/harmful counters *binding* lifecycle, autonomous skill edits,
text-classifier guards, lifecycle hooks as orientation, per-provider
enforcement forks.

## 3. Adherence architecture (how rules are obeyed)

Writing a rule is not adherence. The layers, cheapest first:

1. **Mechanized refusal at state change.** Malformed checkpoint intent
   refuses at `mailbox_writer.py`. Byte-identical mailbox reintroduction
   is not mutation; mutated canonical review events stay fatal.
2. **Pinned prose with anti-drift tests.**
   `test_checkpoint_contract_is_pinned_across_provider_surfaces` holds
   the same phrases on AGENTS.md and all four continuation adapters.
3. **Cheapest-path tool.** `scripts/draft_checkpoint.py` (scratch-only)
   plus a required `Lessons:` field; `none-considered` always publishes
   (anti-sediment, no quota).
4. **Reduced-context probe.** Existing `probe-claim` / `amnesiac-prober`
   lane. This landing records the method when a live launch is not
   authorized (`experiment-2026-08-12-continuity-and-writing-skills.md`).
5. **Measured adherence + rule maintenance.** Slope continuity/learning
   series; skill-use rows as advisory slope. Quality of compaction
   recovery stays `not_measurable` (no resume-receipt; that would fail
   I7). Rule-maintenance footers on canonical skills name observed
   failure, cost, and re-evaluation signal (`work-modes.md`). The
   four-seat skill stays ≤60 lines and is not grown for a footer; it
   already points at `work-modes.md`.
6. **Review as last catch.** Skill-path edits hit
   `ci_admission_gate.AUTHORITY_SURFACES`. Writer/parser changes are
   high-risk-control. This change set does not self-approve and does
   not publish mailbox events.

Not used: text classifiers over agent prose, SessionStart orientation,
per-provider enforcement forks.

## 4. Staged design and landing record

| Stage | Intent | Landing |
|---|---|---|
| A | Unblock the live gate; correct doc drift | `check_coordination.py` keeps earliest introduction; byte-identical reintro is not mutation; conversational kinds with differing bytes stay projectable; Stage 2b README + stub-count drift corrected |
| B | Durable checkpoint | `findings` kind reused; parser + writer validation; `draft_checkpoint.py`; four continuation docs + AGENTS.md item 7; slope continuity coverage |
| C | Lessons routing without sediment | closeout prompts on wave-gate / seat skills; coordinator confirms, never authors; `none-considered` always legal |
| D | Skill authoring and observability | `writing-skills` + Claude stub; R-SKILL inventory; skill-use schema + reporter; rule-maintenance footers; `tests/skill_packs/` |
| E | O3 archive | proposal only (`mailbox-archive-proposal.md`); I6 fail-closed backup; activation = collector latency |
| F | Adherence probe | pinned phrases landed with B; live probe not launched; honest experiment record |

## 5. Non-goals (binding)

No new mailbox kind. No embeddings. No autonomous canonical skill
writes. No usage counts as lifecycle evidence. No cursor consumption
or fast-forward in this change. No mailbox archive execution. No
third skill tree, manifest, or materializer. No domain-graph skill.
Desktop-only: no additional provider.

## 6. Verification

Targeted: `tests/unit/test_checkpoint.py`,
`tests/unit/test_check_coordination.py`,
`tests/unit/test_protocol_prompt_sync.py`,
`tests/unit/test_slope_metrics.py`,
`tests/unit/test_learning_promotion.py`,
`tests/unit/test_learning_candidate.py`,
`tests/unit/test_learning_metrics.py`,
`tests/unit/test_skill_packs.py`.
`scripts/check_arch_freshness.py` when ARCHITECTURE.md changes.
`scripts/governance_verify_all.py` at completion.

## 7. Residual risk

- Compaction-recovery *quality* is still unmeasured.
- Live reduced-context probe of the new surfaces was not launched.
- Skill-use rows start at zero; the schema exists so the first wrap
  can append without inventing a format.
- Four-seat skill has no rule-maintenance footer (60-line pin).
- Unread cursors remain large; doctrine says that is not orientation
  debt. Fast-forward stays a user-authorized external effect.
