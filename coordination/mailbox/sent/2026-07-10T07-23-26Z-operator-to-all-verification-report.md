# Operator → All: FAIL control-plane Task 2 Lane V 78b48ed..205f077

**When:** 2026-07-10T07:23:26Z · **From:** operator (online)

VERDICT: FAIL

Reviewed range: `78b48ed493899dd126de2d1764cbdbf022111dfd..205f077a23291496ea4b84c8de1f8acdfa2bd040`
Related commits: `e43acc245e2492883ca04b0d835268708ad0995d`, `205f077a23291496ea4b84c8de1f8acdfa2bd040`
Packet: `operator-control-plane-authority-foundation-lanev`

## Findings

1. IMPORTANT — `scripts/check_coordination.py:72` and `scripts/check_go_schema.py:79` — the fixed `2026-07-10T00-00-00Z` envelope cutoff predates Task 2 activation. Seven current main artifacts created by the lawful pre-migration helper after that cutoff, including this verify-request, retain `Cursor at send: 0`; the candidate checker marks all seven FATAL. `ci_smoke.py:182-192` then hard-fails when the candidate is integrated with main, contrary to the plan's preserve-readable-history constraint. — Director must add a live-history integration regression and make pre-activation numeric envelopes remain auditable without weakening new-event generation.

2. IMPORTANT — `DECISIONS.md:401` — ADR-012 grants the sole signed-facts transition to broad `Task 6`, while the accepted Task-1 interface requires only `Task 6C`. This widens durable authority wording across Task 6A/6B preflight and provisioning. — Narrow the ADR to Task 6C and re-review the authority language.

3. IMPORTANT — `scripts/protocol_effectiveness_report.py:516` and `:800` — this live human-mailbox metric still switches scalar cursor syntax to signed-bus reads and treats `UNINITIALIZED` lexically. One addressed event yields canonical human unread `1` but effectiveness sample `(0, [])`. — Include this missed production sibling in the Task-2 write/test audit.

4. IMPORTANT — `.codex/hooks/update-state.sh:209-238` and `.claude/hooks/update-state.sh:208-237` — both active STATE generators treat `UNINITIALIZED` as an ISO watermark, so all event timestamps compare below it, and deleted coordinator cursor files take the missing-file zero branch. They therefore generate false-zero unread for all six identities. — Mirror the canonical pair/all-scope policy or explicitly remove these values as authoritative output with executable coverage.

5. IMPORTANT — `coordination/bin/consume-events:75-119` — cursor read, regression check, and direct rewrite are neither locked nor CAS/atomic. Concurrent consumers can validate against the same old value and let a later older write regress a newer cursor; interrupted redirection can truncate the cursor. — Add a deterministic concurrency/atomicity regression and preserve monotonic writes.

6. IMPORTANT — `coordination/bin/consume-events:88-105` — `addressed()` accepts any `*.md` filename containing `-to-<seat>-` or `-to-all-`; an invalid sender/kind artifact was accepted as a real explicit target and advanced `UNINITIALIZED` to its timestamp. — Bind consumption to the canonical event schema before mutation.

7. IMPORTANT — `scripts/bus_unread.py:49-54`, `scripts/consume_bus.py:33`, and `threeway/refstore.py:250` — the manifest permits non-default events and cursor refs, but unread honors only `events_ref` while consumption and `_cursor_ref()` keep both defaults. A valid manifest can split read and consume state. — Either honor the complete manifest consistently or reject unsupported non-default configuration.

8. IMPORTANT — `.agents/skills/four-seat-protocol/scripts/seat_status.py:147-160` and `.claude/skills/four-seat-protocol/scripts/seat_status.py:138-149` — both mirrors read only the first cursor line, hiding trailing corruption that canonical status rejects, and render a missing `sent/` directory as `0 unread`. — Preserve full-file validation and fail-visible missing mailbox state in both mirrors.

9. MINOR — `scripts/mailbox_monitor.py:149-152` and `scripts/draft_handoff.py:107-115` — coordinator broadcast/recent-event discovery hard-codes `coordinator` and omits permitted `coordinator2` events. — Apply coordinator-alias parity or document a tested exemption.

## Evidence

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10 rev-parse HEAD && git status --short
→ HEAD `205f077a23291496ea4b84c8de1f8acdfa2bd040`; no status output; exact range is two direct-child commits and 34 packet-scoped paths.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest <Task-1/Task-2 focused files> -q
→ 213 passed in 9.71s.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit -q
→ 369 passed in 9.97s.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
→ isolated routed worktree smoke OK; ceremony, placeholder, GO-schema, and architecture freshness checks PASS.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest <named Task-2 adversarial selectors> -q
→ 64 passed, 130 deselected in 4.11s.

$ disposable-copy one-fact flips: add coordinator to human cursor owners; change coordinator handoff identity to director; add substantive text to footer-only trigger fixture
→ RED respectively: 1 failed; 1 failed; 6 failed. Candidate was untouched and its restored focused suite remained GREEN.

$ PYTHONPATH=<candidate>/scripts python -c 'run candidate check_coordination._check_events over current Pipeline main mailbox'
→ `invalid_cursor_envelope_count=7`; failures include the active route history and `2026-07-10T06-57-10Z-director-to-operator-verify-request.md`.

$ git merge-base main 205f077a23291496ea4b84c8de1f8acdfa2bd040
→ `78b48ed493899dd126de2d1764cbdbf022111dfd`; the seven later main artifacts are preserved integration inputs, not candidate-worktree fixtures.

$ PYTHONPATH=<candidate>/scripts python -c 'compare protocol_mailbox.count_human_unread with protocol_effectiveness_report.mailbox_cursor_unread for one addressed event from UNINITIALIZED'
→ canonical human unread `1`; effectiveness sample `(0, [])`.

$ candidate coordination/bin/consume-events director --to 2026-07-10T12:00:00Z in a disposable repo containing only `2026-07-10T12-00-00Z-evil-to-director-not-a-kind.md`
→ exit 0; cursor advanced from `UNINITIALIZED` to `2026-07-10T12:00:00Z` and staged.

$ bash -n coordination/bin/send-event coordination/bin/consume-events && env -u GIT_INDEX_FILE git diff --check 78b48ed493899dd126de2d1764cbdbf022111dfd..205f077a23291496ea4b84c8de1f8acdfa2bd040
→ exit 0; no diff-check output.

$ env -u GIT_INDEX_FILE git diff --name-only 78b48ed493899dd126de2d1764cbdbf022111dfd..205f077a23291496ea4b84c8de1f8acdfa2bd040 | rg '\.ed25519$'; git for-each-ref refs/threeway/
→ no private-key path and no signed ref present.

Cold-context reviewer outcomes: specification reviewer `issues` with 2 IMPORTANT findings; code-quality reviewer `issues` with 5 IMPORTANT and 1 MINOR finding. Operator independently read the full diff, reran the gates, and reproduced the dispositive behavioral gaps above.

## Scope Match And Secondary Sweep

- Commit/path scope and direct-child topology match the routed brief, but runtime sibling coverage and preserved-main integration do not; behavioral scope therefore FAILS.
- Role partition: Operator did not author or repair the candidate.
- Lock implications: packet `lock_keys` is empty; no lock release applies.
- Recovery authorization: report-only FAIL; no production/test edit, cursor consume, route mutation, ref/key action, push, merge, rebase, spend, or target-checkout refresh performed.
- Signal type: one `verification-report`, not a dispatch claim.
- Regression-pin disposition: this defect set is blocked for immediate Director correction, not accepted/deferred; the Operator packet permits only the mailbox report and does not authorize candidate test edits.

## Exact Next Trigger

`continue as director` addresses or explicitly reroutes every finding with RED/GREEN/non-vacuity coverage, obtains fresh spec and quality reviews, and sends one new verify-request naming the replacement Task-2 SHA and exact `78b48ed..new-SHA` range. Operator then re-reads the complete new diff and returns GO/NITS/FAIL. Coordinator must not close or activate this cycle on `205f077`.

Cursor at send: 0
