# ChatGPT Pro Local Re-prepare — Dedicated Design (approval-gate artifact)

Status: DRAFT for user-principal approval. This document is the "dedicated
design" required by `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`
and by the Frozen ChatGPT Approval Firewall in
`coordination/mailbox/sent/2026-07-16T04-59-40Z-coordinator-to-all-coordination.md`.
Its companion implementation plan is
`docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md`.
Neither document grants review, integration, merge, publication, or push
authority by itself; the user-principal must approve both explicitly.

Author/harness: Claude (orientation-mode session, 2026-07-16). The frozen
implementation was authored by Codex seats — this design enumeration is
therefore a different-harness pass over the same change (R-INDEPENDENCE
design-time independence, ADR-019).

## 1. Problem and evidence

The consultation guard (`scripts/chatgpt_pro_consult.py`) over-blocks and
under-distinguishes:

- **False positive proven:** long benign prose, once whitespace-stripped by
  the sanitizer's compact view, fuses into an 80+ run matching the generic
  base64 pattern `[A-Za-z0-9+/]{80,}` and is rejected as "sensitive content".
  Reproduced by `test_long_benign_question_is_not_compacted_into_a_base64_token`
  on frozen head `3dcff96` (the test's question is real prose from a prior
  consultation attempt).
- **No error taxonomy:** a purely local, pre-reservation validation failure and
  a post-reservation lifecycle failure both surface as coarse errors, so a
  seat cannot tell "correct your request and prepare again" from "stop — the
  no-retry lifecycle is engaged".
- **Capability cost (runtime ledger, `.codex/runtime/chatgpt-pro-consultations.json`,
  16 records 2026-07-13..07-16):** 8 reconciled, 6 failed, 2 stale; the `iab`
  transport succeeded once in five attempts before 2026-07-16. A guard that
  additionally rejects benign questions before any attempt makes a scarce
  capability scarcer.

## 2. Design

### 2.1 Lifecycle boundary (the core rule)

Split the consultation lifecycle at `reserve_consultation()`:

- **Before reservation** — local JSON/schema/sanitizer/recursion/size checks
  run first and create no consultation record, no idempotency reservation, no
  provider contact, and no spend. A rejection here is a **correctable local
  event**: the seat may deliberately fix the request and run the complete
  preparation again. It is not a consultation attempt and not a provider
  retry.
- **From reservation onward** — the existing V1 prohibitions are unchanged:
  no changed prompts, no retries, no provider switches, no transport
  fallbacks, no workarounds; unchanged reserved work deduplicates; automatic
  provider and transport retries remain zero.

Canonical sentences (already propagated to every operative surface on the two
frozen branches, pinned by `test_chatgpt_pro_local_correction_boundary_is_surface_synced`):

> Pre-reservation local validation rejection may be corrected deliberately and
> fully prepared again; it creates no consultation attempt or provider retry.
> Once reservation or state mutation begins, changed prompts, retries,
> provider switches, transport fallbacks, and workarounds remain prohibited.

### 2.2 Error taxonomy (content-free)

- `prepare` catches only `ConsultationError` raised by `prepare_request()`
  (i.e., strictly before `reserve_consultation()`) and re-raises it as CLI
  error `local_validation_rejected` (exit 2, stderr JSON
  `{"error": "local_validation_rejected", "status": "error"}`). The payload is
  content-free: no echo of the rejected text (enforced by
  `test_cli_local_validation_rejection_is_correctable_before_reservation`,
  which asserts the secret string is absent from stderr and that no state file
  or lock is created).
- Reservation, idempotency, state, transport, delivery, and response failures
  keep their existing codes (`consultation_rejected` or coarse state errors)
  and remain ineligible for automatic retry or fallback (enforced by
  `test_cli_reservation_failure_is_not_reported_as_local_correction`).

### 2.3 Sanitizer detector split (boundary-preserving views)

`_whitespace_views(value)` yields `collapsed` (all whitespace folded to one
space) and `compact` (all whitespace removed). On frozen head `3dcff96`:

- **Named secret formats** (private-key armor, `authorization:` headers,
  `password/secret/token/api-key` assignments, `AKIA…`, `gh?_…`/`sk-…`) keep
  scanning all four views — `value`, `collapsed`, `compact`,
  `compact.lower()` — so whitespace-splitting or case games do not hide a
  recognizably named secret.
- **The generic base64 detector** becomes a separate pattern
  `(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{80,}={0,2}(?![A-Za-z0-9+/=])` and scans
  only the boundary-preserving views `(value, collapsed)`. Word boundaries
  survive the single-space collapse, so prose can no longer fuse into a fake
  token, while any genuinely contiguous 80+ base64 run is still rejected
  (five candidate shapes pinned by
  `test_contiguous_generic_base64_candidate_remains_rejected`).

## 3. Abuse-case enumeration (R-INDEPENDENCE design-time artifact)

Each case is an enforced-and-tested behavior on frozen head `3dcff96`, not an
aspiration. The per-task independent review (plan Task 1) verifies the diff
against exactly this table.

| # | Abuse/edge case | Required behavior | Enforcing test (tests/unit/test_chatgpt_pro_consult.py unless noted) |
|---|---|---|---|
| E1 | Contiguous generic base64 secret (≥80 chars, with/without `+ / =` padding) | Rejected pre-reservation | `test_contiguous_generic_base64_candidate_remains_rejected` (5 shapes) |
| E2 | Benign long prose whose compacted form looks like base64 | Accepted (false positive eliminated) | `test_long_benign_question_is_not_compacted_into_a_base64_token` |
| E3 | Named-format secret split across lines / unicode lookalike (`＝`) | Rejected (compact views still scanned for named formats) | `test_split_line_secret_and_unicode_lookalike_are_rejected` |
| E4 | Rejected secret echoed back through the error channel | Content-free `local_validation_rejected`; secret absent from stderr; no state file, no lock | `test_cli_local_validation_rejection_is_correctable_before_reservation` |
| E5 | Correction loop abused as a sanitizer brute-force / reformulation automation | Policy prohibition on every operative surface: "Do not automate reformulation loops"; each rejection creates zero consultation state and zero provider contact, so no spend/attempt accrues | surface text pinned by `test_chatgpt_pro_local_correction_boundary_is_surface_synced` (tests/unit/test_protocol_prompt_sync.py, branch `3dcff96`) |
| E6 | Same consultation UUID re-prepared after local rejection | Exactly one reserved record after the corrected prepare | `test_cli_local_validation_rejection_is_correctable_before_reservation` (final assertion) |
| E7 | Content swap after reservation (changed question, same/other UUID path) | `consultation_rejected`; original reservation unchanged | `test_cli_reservation_failure_is_not_reported_as_local_correction` |
| E8 | Reclassifying a post-reservation failure as "correctable local" | Impossible by construction: only `prepare_request()` exceptions map to `local_validation_rejected`; `reserve_consultation()` runs after | code shape (`main()` try/except scope) + E7 test |
| E9 | `off` mode bypass via the new path | `off` still fails closed before any preparation | `test_cli_off_fails_without_emitting_or_persisting_prompt` |

**Accepted residual (explicit tradeoff):** an *unnamed-format* base64 blob ≥80
chars deliberately split by whitespace mid-token evades the generic detector
(both surviving views preserve the split). Compensating controls: every named
secret format still scans whitespace-stripped views (E3); rule 1 of the
Prepare procedure forbids collecting credentials/private data at the source;
the guard performs no automatic file reads; and the reviewer of record should
re-confirm this residual is acceptable. The alternative (keep scanning the
compact view generically) is the proven benign-prose false positive of §1.

## 4. Two frozen halves, one change

| Branch @ head | Content | Paths |
|---|---|---|
| `codex/chatgpt-local-reprepare-flexibility-2026-07-16` @ `3dcff96` | Guard + model + Codex-surface policy text + tests (incl. the 11-surface local-correction sync test) | 16 paths (manifest in `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`) |
| `codex/chatgpt-pro-claude-surface-wip-2026-07-16` @ `233ef81` | Claude-tree mirror: `CLAUDE.md` R-CONSULT, Claude continuation adapter, 4 Claude seat skills, Claude paths added to 3 existing consultation sync tests | 7 paths |

Both branches base cleanly inside current `main` history and touch
`tests/unit/test_protocol_prompt_sync.py` in non-overlapping regions (an
inserted test at ~line 660 vs tuple extensions at ~lines 827-930). Integrating
the Codex half without the Claude half re-opens the cross-tree drift this
campaign just closed; integrating the Claude half alone asserts policy the
canonical model does not yet render. They ship together, Codex half first, and
the local-correction sync test's surface tuple is extended with the six Claude
surfaces in the same integration change (plan Task 4).

## 5. Non-goals

- No transport change: `auto` remains `iab -> block`; `manual` remains legacy
  compatibility; no Chrome, API, or provider fallback is introduced.
- No retry-policy change after reservation; V1 zero-retry stands.
- No new consultation authority: output remains advisory-only; subagents still
  prepare-only.
- No push or publication; those remain user-gated and outside this design.
- The `.claude/skills/chatgpt-pro-consultation/` native-skill question and the
  Codex Risk-Tier Router mirroring question are deliberately out of scope
  (tracked as separate follow-up decisions).
