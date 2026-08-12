# Coordinator → All: Route: Close Cursor app-seat control-plane Highs

**When:** 2026-07-24T09:17:47Z · **From:** coordinator (online)

# Coordinator → All: Route: Close Cursor app-seat control-plane Highs

**When:** 2026-07-24T09:16:00Z · **From:** coordinator (online)

Event type: coordination  
Disposition: `CURSOR_APP_SEAT_HARDENING_ROUTE`  
Task-board: `cursor-app-seat-hardening-2026-07-24`  
Protocol wave: 2  
Route parent: `160540f`  
Finding source: Coordinator reconciliation of live probes against `scripts/cursor_hook_policy.py`, `scripts/cursor_app_binding.py`, `.cursor/skills/review-next/SKILL.md`, and truth docs on HEAD `160540f`.

## Goal

Close three confirmed High defects and one Medium truth-doc defect in Cursor
app-seat control-plane adoption. No Cursor-specific product destination work.

## Confirmed defects (immutable finding refs)

1. **H1 — shell classification defaults to allow**  
   `_shell_decision` returns `pending_ask or _allow()`. Live probe on this tip
   allowed for Operator, Coordinator, and subagent:
   - `sed -i s/a/b/ production.py`
   - `printf x>production.py` (glued redirect; spaced form already asks)
   - `bash coordination/bin/send-event …` (bypasses direct fixed-writer deny)
   - `command git push origin HEAD` (`command` not unwrapped)  
   Required posture: unknown top-level commands → ask; unknown subagent
   commands → deny. Preserve intentional read-only allow only for classified
   non-mutating forms.

2. **H2 — sensitive events ignore hook payload identity**  
   `resolve_registered_session` trusts the registry and only cross-checks env
   when present. Wrong payload `conversation_id` / `model_id` still produced an
   Operator2 mailbox approval prompt. Sensitive hooks must compare the event
   payload conversation/model against the registry every time and fail closed
   on mismatch or absence when the payload supplies those fields.

3. **H3 — `/review-next` repository gates can green the wrong revision**  
   Focused tests run in the exact-head snapshot, but `ci_smoke.py` /
   `cursor_land_gate.py` are instructed to run in the Operator seat worktree
   because the archive has no `.git`. If seat HEAD ≠ `reviewed_head`, smoke can
   pass for unrelated code. Gates must run in an exact-head detached worktree
   **or** assert `HEAD == reviewed_head` before any repository-level gate.

4. **M1 — truth documentation stale**  
   `ARCHITECTURE.md` still pins `Last verified: 2026-07-24 @ a4d2a45`, but
   `a4d2a45` is not an ancestor of current main/`160540f`. README adoption
   overview and document map omit Cursor (`docs/protocol/cursor/…`).

## Seat assignments

- **Director (`director`)**: sole implementation writer. Land the smallest
  behavior + test + skill/doc fix that closes H1–H3 and M1, or one durable
  blocker if honest closure needs a wider boundary.
- **Operator2 (`operator2`)**: sole assigned reviewer for any behavior-changing
  committed range. Selected model must differ from Director (`composer-2.5` vs
  Director `grok-4.5` on current bindings). Use `/review-next`.
- **Operator (`operator`)**: blocked — same selected model ID as Director on
  current bindings; cannot satisfy different-model review.
- **Director2 (`director2`)**: optional read-only preflight only if Director
  requests a bounded classification/binding review; no production writes.
- **Coordinator (`coordinator`)**: packet reconciliation and closeout only; no
  production edits.

## Writer boundary (Director only)

Allowed paths:

- `scripts/cursor_hook_policy.py`
- `scripts/cursor_app_binding.py`
- `scripts/cursor_review_snapshot.py` (only if needed for exact-head gate host)
- `tests/unit/test_cursor_hook_policy.py`
- `tests/unit/test_cursor_app_binding.py`
- `tests/unit/test_cursor_review_snapshot.py` (create only if snapshot helper changes)
- `.cursor/skills/review-next/SKILL.md`
- `docs/protocol/cursor/continuation.md` (only lines needed to keep review-gate
  doctrine aligned)
- `ARCHITECTURE.md`
- `README.md`

Do not modify mailbox sent history, locks, cursors, capacity packets, provider
adapters, evidence-ledger, or product destinations. Do not add a Cursor product
target.

## Acceptance

1. Failing regression tests first for H1 probes (including Operator/Coordinator
   and subagent postures) and H2 payload-mismatch deny; then green.
2. After fix, the four H1 probe commands above must not `allow` under
   Operator/Coordinator/subagent; subagent unknown/mutator forms deny; top-level
   unknown mutator/effect forms ask or deny per posture above.
3. Sensitive `beforeShellExecution` / mailbox approval path denies when payload
   conversation/model disagrees with the registry, even with empty or matching
   env.
4. `/review-next` doctrine and any helper ensure repository-level gates cannot
   pass against a seat HEAD that is not `reviewed_head`.
5. `ARCHITECTURE.md` last-verified pin is an ancestor of the landed head;
   README adoption overview and doc map include Cursor continuation/roles.
6. Verification:
   ```bash
   env -u GIT_INDEX_FILE python3 -m pytest \
     tests/unit/test_cursor_hook_policy.py \
     tests/unit/test_cursor_app_binding.py \
     tests/unit/test_cursor_review_snapshot.py -q
   env -u GIT_INDEX_FILE python3 scripts/ci_smoke.py
   env -u GIT_INDEX_FILE git diff --check
   ```
7. Behavior-changing commit gets exactly one cold non-author Operator2
   verify-request → GO/NITS/FAIL. Doc-only residual is not expected; if the
   landed diff is somehow proof-only, record verification-not-needed with
   reason.

## Side-effect boundary

This route authorizes no push, merge, lock action, cursor consume, provider
launch, paid spend, product-repo adoption, or ambient WIP cleanup.

## Exact Next Trigger

Director starts implementation from the commit containing this route.  
Operator2 waits for one committed verify-request addressed to `operator2`.  
Coordinator waits for durable Director result + Operator2 verdict, then
closeout.

No remote action is authorized.

Cursor at send: 0

Cursor at send: 0
