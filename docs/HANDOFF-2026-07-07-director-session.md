# HANDOFF — director-seat session, 2026-07-07 afternoon

Scope: Pipeline-repo work by this seat + pointers to the cross-repo (evidence-
ledger) coordination it participated in. Ledger-side truth lives in that repo's
`.superpowers/sdd/progress.md` (tail entries are the authority) — do not
re-derive it from here.

## Landed in this repo (main, ahead of origin — PUSH PENDING)

| Commit | What | Evidence |
|---|---|---|
| `c2e16d5` | gitignore-twin chip (cherry-picked from `claude/loving-fermi-6e87ee`, since deleted) — `.claude/hooks/.last-state-head` twin of the `.codex` entry from `1cd8bcb` | commit body carries check-ignore + smoke verification |
| `0432a02` | completes the chip: both `.skip-worktree-cleared.log` twins (written by `update-state.sh:141`/`:142` in both hook dirs) | `git check-ignore -v` on all 4 runtime files → `.gitignore:96-97,100-101`; `ci_smoke.py` → OK |
| (this handoff's commit) | core.md sharp-edge: deliberate seat-index maintenance under `guard-git-index.sh` + this doc | — |

Push decision is the user-principal's (A7 push-gate deferred, ADR-005).
The operator seat sanity-verified `c2e16d5`+`0432a02` (chore tier, no Lane V —
its findings event carries the check-ignore + smoke evidence).

**AMENDED at wrap:** an operator session landed `45477ff` + `ba6af6a`
(coordination events) between this seat's commits and this handoff — main is
now **ahead 5**, not 2. See "Operator events" below; the original "no mailbox
events pending" claim was falsified mid-wrap and is retracted.

## Seat hygiene done (not commit-visible)

All four per-seat indexes (`.git/index-{director,director2,operator,operator2}`)
were STALE — seeded around `4a74e10`, showing phantom `MM` staged diffs after
ADR-009..011 landed via another index. All rebuilt to HEAD and verified
0 staged diffs, via the guard-compliant route now documented in
`docs/protocol/claude/core.md` → "Git-tooling sharp edges" (read that; don't
re-derive). The session-start `MM DECISIONS.md …` snapshot noise should be gone
next session.

## Chip dispositions (closes the 2026-07-07 chip check)

- **gitignore-twin: LANDED** (above). Branch deleted.
- **REMEDIATION-INVENTORY: DEAD chip** — its branch (`claude/cool-mendeleev-665de2`)
  had zero commits; deleted. Board creation was NOT picked up on purpose:
  `scripts/seed_inventory.py` docstring pins the coordinator as the single
  writer, and creating a campaign board with no campaign running is ceremony
  (`check_no_ceremony`). `docs/protocol/protocol-assembly-map.md`'s references
  to `docs/REMEDIATION-INVENTORY.md` stay as documented-future-artifact until a
  campaign wave starts; the coordinator seat bootstraps it then.

## Cross-repo participation (evidence-ledger) — pointers only

Same-day, multi-seat T14 work: this seat ran the evidence-backed merge-gate
sign-off, was overridden by the owner's later informed answers, claimed the
import runway on an owner "proceed", then RETRACTED on discovering the
owner's carrier designation + a live carrier — full claim/retract sequence in
the ledger's `progress.md` (kept legible by design). Durable contributions
that survived: the owner-ruled PPL-annotation FINDING (implemented verbatim by
the carrier), the 0706-workbook blocker re-sweep, and two protocol memories
(`git-index-file-leak-pipeline-to-ledger`,
`concurrent-seat-collision-shared-ledger-tasks`). The real internal import
LANDED (carrier seat, take 4; PR #8 route). Ledger remaining queue (owner +
carrier): checkpoint-2 reconciliation readout → agency checklist sign-off →
real agency load → cross-source readout → T16 Step 6.

## Operator events (Rule #8 — read them; they bind receiving seats)

`coordination/mailbox/sent/2026-07-07T04-33-03Z-operator-to-all-findings.md`
+ `…04-43-45Z-operator-to-all-wrap.md`. Two fleet defects on record:

1. **`_sync_seat_index` cold-start wedge** — a freshly seeded seat index with
   no `.last-index-sync-*` marker can never self-sync (both hook branches skip
   it). Runtime-repaired 13:26–13:29 this session. **Source fix ASSIGNED to
   the director lane: the seeding step must write the marker alongside the
   index.** Note: this seat's read-tree rebuilds (above) did not touch markers;
   pre-existing markers mean hook branch B keeps those seats syncing — the
   wedge bites only marker-less fresh seeds.
2. **`send-event` is broken fleet-wide** — `coordination/bin/send-event` does a
   plain `git add` but `.gitignore:51` ignores `sent/*`; every emit fails and
   self-deletes (sent/ empty since 06-30). Fix ownership open: `add -f` in the
   script vs a documented force-add path. Manual emit recipe is in the
   findings event.

## Resume protocol (next Pipeline session)

1. R-START as usual (smoke ran green throughout this session).
2. Decide/execute the push of the commits above (with the user).
3. **Director-lane queue:** the `_sync_seat_index` seeding-marker source fix
   (assigned above); decide/land the `send-event` fix (production coordination
   tooling — Lane V applies, unlike this session's chores).
4. If starting ledger work from a Pipeline seat: read the two memories named
   above FIRST, and check the ledger `progress.md` tail for an active seat
   before touching anything shared.
