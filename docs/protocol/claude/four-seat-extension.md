# Four-seat coordination — protocol extension

**Status:** TOOLING LANDED 2026-06-13 (user-authorized "proceed now") ·
operator-authored per user directive ("scale 2→4 seats for speed"). The
backward-compatible tooling cutover (§8) is **applied + verified** — `ci_smoke`
green; coverage lives in `tests/unit/test_check_coordination.py` +
`tests/unit/test_coordination_tooling.py` (the originally cited
test_four_seat_coordination.py was not transplanted). `director2`
/`operator2` went LIVE at the 2026-06-13T08:50Z cutover (historical
snapshot — read liveness from heartbeats, not this line). **Lanes:** the
origin-project badge "FINAL (PRINCIPAL-CONFIRMED 2026-06-13)" is transfer-bundle
history; the operative lane record for THIS Pipeline deployment is
`DECISIONS.md` **ADR-009** (PRINCIPAL-CONFIRMED 2026-07-07): Pair A =
coordination layer, Pair B = verification & signing layer. The angle-bracket
lane slots below stay unbound by ADR-009's explicit instruction (adopter
fill-ins, ADR-002). Status: **ACCEPTED.**

**Principle: additive + backward-compatible.** No existing seat is renamed. The
two current seats keep their exact identifiers, indexes, cursors, presence files,
and launch. The change is purely additive — two new seats plus a wider event
vocabulary. Every intermediate state of the cutover keeps `ci_smoke` green so the
live `director` session is never broken.

---

## 1. Seat model

Canonical seat IDs become a 4-set: **`director`, `director2`, `operator`,
`operator2`** — where `director`/`operator` ARE seat-1 (unchanged). A `coordinator` broadcast role also exists for cross-seat signaling. Two **pairs**:

| Pair | Director | Operator | Lane (adopter slot — operative record: ADR-009) |
|------|----------|----------|------|
| **A** | `director`  | `operator`  | **<domain-lane-A>** — <!-- TODO(<PROJECT>): list the Pair-A domain modules, subsystems, and data-integrity concerns for this project. --> |
| **B** | `director2` | `operator2` | **<domain-lane-B>** — <!-- TODO(<PROJECT>): list the Pair-B domain modules, subsystems, external-API clients, and main orchestrator paths for this project. --> |

(Adopter fill-ins per ADR-002 — deliberately unbound. For THIS deployment read
the lanes from `DECISIONS.md` ADR-009: Pair A = coordination layer, Pair B =
verification & signing layer; per-route capacity packets refine scope within
those lanes.)

**Shared seams** (modules that touch both lanes):
owner = whoever's specific change-lane the edit is in, with a `-to-all-` heads-up
first per Rule #23.

The director↔operator relationship (strategy/briefs vs independent verification)
is **unchanged within each pair** — we duplicate the proven two-seat unit, we do
not invent a new role. "Two seats of one team" becomes "four seats / two pairs of
one team"; user is still principal; **git is still the tiebreaker** (first commit
to land wins) at any boundary.

## 2. Launch (provider-pure canonical path)

```bash
# Any four-seat Claude session (new terminal, SAME shared tree)
cd /Users/hyungkoookkim/Pipeline
coordination/bin/claude-seat <director|director2|operator|operator2> -- <claude-args>
```

The launcher scrubs inherited foreign-provider and Git authority, replaces stale
Claude contract identity with the selected seat, and binds exactly
`.git/index-claude-<seat>`. Existing regular indexes are validated and
preserved, including staged work. Symlinks, directories, malformed/unreadable
indexes, and an empty index against non-empty `HEAD` fail closed. Only a truly
missing index is seeded. `--dry-run` neither seeds nor starts Claude.

Manual `CLAUDE_SEAT` / `GIT_INDEX_FILE` export recipes are not a supported
launch path because they can inherit or cross-bind another provider's index.

## 3. Presence / heartbeat / index — exact binding required

`.claude/hooks/update-state.sh` is seat-generic only after it validates the
provider-pure binding:
- `_stamp_presence()` stamps `coordination/presence/${CLAUDE_SEAT}-heartbeat.ts`
  for *any* seat → `director2`/`operator2` auto-stamp on launch.
- `_sync_seat_index()` / `_clear_skip_worktree()` key off `$GIT_INDEX_FILE` →
  `index-claude-director2`/`index-claude-operator2` are maintained automatically.

An unpinned, mismatched, foreign-provider, unreadable, or subagent context
performs none of those mutations and does not write `STATE.md` or hook markers.
The PreToolUse guard applies the same binding to Bash, Write, and Edit: invalid
contexts may inspect through a conservative read-only shell subset but cannot
mutate.

The ONLY hook touch was **cosmetic** and has since landed: the STATE.md
unread report lists all six seats (`.claude/hooks/update-state.sh`
`_unread_for`, ref-bus-aware). Not load-bearing — each seat recomputes
live via `seat_status.py`.

## 4. Mailbox addressing — point-to-point **+ a broadcast target**

Any seat may address any other seat directly (`<from>-to-<to>-<kind>.md`). A new
pseudo-target **`all`** lets a seat announce to everyone (lane claims, "I'm
online", cutover notices) without sending N copies. `all` is a valid `to` only —
never a `from`, never a real cursor/seen file.

**The seat vocabulary lives in FOUR code spots — they MUST change together**
(2026-06-13 cutover record, kept as history: the LIVE registry is now
`scripts/protocol_mailbox.py` `SEATS`/`RECEIVING_SEATS`/`KNOWN_KINDS` — six
seats incl. `coordinator2` since Slice 2.5)**:**

| File | What changes |
|------|--------------|
| `coordination/bin/send-event` | `FROM` enum → `director\|director2\|operator\|operator2\|coordinator`; `TO` enum → same **+ `all`** |
| `coordination/bin/consume-events` | `ROLE` enum → 4 seats + coordinator; `addressed()` grep → `-to-(${ROLE}\|all)-` |
| `scripts/check_coordination.py` | `ROLES` → 5-tuple; `_EVENT_NAME_RE` `frm`→5 roles, `to`→5 roles **+ `all`**; orphan check `m.group("to") in (role, "all")` (line 116) |
| `scripts/status.py` | `_EVENT_RE` `to`→5 roles + `all`; `count_unread` line 81 → `if event_to != seat and event_to != "all": continue` |

(`all` is NOT added to `ROLES` — there is no `seen/all.txt`; it is only a `to`
target that every real seat counts as addressed-to-it.)

## 5. Cursors

(2026-06-13 cutover record — live cursors are now scalar-seq per Slice 2.5;
see `docs/protocol/claude/continuation.md` for the current consume paths.)

Create two new watermark files, seeded with a safe past timestamp so the linter's
`cursor_missing` (FATAL) and `cursor_orphan` (ADVISORY) both pass for a seat with
zero events yet (`addressed` is empty → orphan check is skipped):

```
coordination/mailbox/seen/director2.txt   <- 2026-06-13T00:00:00Z
coordination/mailbox/seen/operator2.txt   <- 2026-06-13T00:00:00Z
```

## 6. Work partitioning (the actual speed lever)

- **Pair lanes (adopter slots — the operative record is ADR-009).** Pair A =
  **<domain-lane-A>**; Pair B = **<domain-lane-B>**; in Pipeline: Pair A =
  coordination layer, Pair B = verification & signing layer (`DECISIONS.md`
  ADR-009). Each pair's director briefs, its operator
  independently verifies — the current loop, run twice in parallel. Disjoint by
  construction; shared seams handled per Rule #23.
- **Tiebreaker unchanged.** `git log --oneline -3` before acting on a shared
  task; first commit to land wins. With four seats the provider-prefixed
  `.git/index-claude-<seat>`
  already isolates staging; commits serialize on git's ref lock.
- **Lane discipline (NEW Rule).** A seat does substantive work only in its lane.
  Cross-lane edits require a `-to-all-` heads-up first (or a direct dispatch-claim
  to the owning pair). Pathspec-scoped commits remain load-bearing.
- **Architectural decisions (NEW Rule).** A lane-local ADR is owned by that
  lane's director. A **cross-cutting / cross-lane ADR needs BOTH directors'
  sign-off** (a `director-to-director2` proposal + `proposal-reply` ack), or
  escalate to the user. Prevents two directors landing conflicting architecture.
- **Co-sign tiers (Lever #7, audit `wf_6be2ee18-f4b`).** The cross-director
  co-sign is **tiered** so an awareness heads-up does not serialize behind a full
  session. Classifier: *would the co-signer's own verification change which files /
  sites the implementation touches?*
  - **Tier A — implementation-scope-determining** (yes): the co-signing director
    MUST run an independent verification (e.g. a downstream consumer audit the
    brief's caller-grep can't see — a landscape co-sign can catch regressions in
    adjacent subsystems this way) and land a mailbox `verification-report`
    **before dispatch**. This is fulfillable **async** via a workflow + mailbox
    report — NO session restart required; it just must precede the implementer
    dispatch.
  - **Tier B — awareness-only** (no): a `-to-all-` or direct heads-up with a
    **48h proceed-if-no-objection** default (already the de-facto practice — e.g.
    a sibling-fix ACK can round-trip in <10 min).
  When unsure which tier, treat it as Tier A (the safe default).

## 7. Rules deltas (docs/protocol/claude/director-operator.md)

Most of #7–#22 scale unchanged (they are per-seat). Touch points:
- Framing: "two seats" → "four seats / two pairs"; user still principal.
- Rule #8 (mailbox binds receiving seat): now per-seat across 4 + `all` events
  bind every seat.
- Rules #19/#20 (presence): four presence + four heartbeat files.
- **NEW Rule #23 — lane ownership** (§6 lane discipline + cross-director ADR).

## 8. Cutover sequence (safe-ordered — keeps ci_smoke green at every step)

The working tree is SHARED, so each edit is live for the peer the instant it is
written. Order the cutover so no intermediate state can FATAL the peer's smoke:

1. **Create the two `seen/*.txt` cursors** (harmless — unreferenced until ROLES
   widens).
2. **Widen the four vocabulary spots together** (send-event, consume-events,
   check_coordination, status.py) + the cosmetic hook unread.
3. **Regression coverage** — carried by `tests/unit/test_check_coordination.py`
   + `tests/unit/test_coordination_tooling.py` (a `director2→operator2` event +
   an `all` broadcast lint clean, `count_unread` counts `all` for every seat,
   `consume-events operator2` advances). The originally cited
   `test_four_seat_coordination.py` was never created (see header note).
4. **Run `scripts/ci_smoke.py`** → must stay green (it runs check_coordination).
   Round-trip a real `director2→operator2` test event through send/consume.
5. **README launch stanzas + this doc** flipped to ACCEPTED.
6. **Commit** the whole cutover via explicit pathspec, one commit.

## 9. Rollback

`git revert` the cutover commit. Backward-compatibility means the 2-seat world is
untouched by the extension, so a rollback is clean and the live `director`/
`operator` seats are unaffected either way.

## 10. Coordinator — on-demand policy (Lever #8, audit `wf_6be2ee18-f4b`)

The `coordinator` is a 5th, read-only, cross-pair oversight pseudo-seat — **NOT a
standing concurrent seat**. Standing-concurrent operation consumes the working
seats' attention and duplicates findings already queued; the value is the
cross-pair view, not the constant presence. (This is the on-demand framing of the
`coordinator` broadcast role mentioned in §1.)

- **Trigger.** Spawn on demand at a **multi-pair-wrap boundary** (both pairs
  wrapped the same day) when the user or a director wants a cross-pair audit — the
  high-collision regime where cross-pair stale-state accumulates fastest.
- **Posture.** UNPINNED: no `CLAUDE_SEAT`, no `GIT_INDEX_FILE`. Read-only by
  default; owns no lane (Rule #23-inert).
- **Output.** Land findings as a **single** findings/doc commit (or one mailbox
  event) — not a stream of per-finding events. The send-only `coordinator` mailbox
  vocab (`fd334d3`) stays valid for this but is used sparingly.
- **Commits** only under explicit user direction, via a seeded
  `.git/index-claude-coordinator` + pathspec partial commit; push stays USER-gated.
