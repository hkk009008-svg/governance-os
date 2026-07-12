# Orthogonal packet state (derivation) — `scripts/packet_state.py`

The capacity-packet `status` field (`ready|active|blocked|done|excepted`, defined
in `scripts/protocol_capacity.py`) overloads three orthogonal facts into one
string: **what happened to the work**, **whether the seat is still represented in
the active cycle** (G1 exactly-one coverage), and **whether the result was
independently accepted** (G5/G6). `scripts/packet_state.py` DERIVES two of those
facts back out as separate dimensions — `work_state` and `verification_state` —
purely from the legacy `status` / `packet_type` / `done_evidence` fields.

This module is **READ-ONLY**: it writes no packet, adds no field, and changes no
gate. It is the derivation foundation described in **ADR-017**. This slice is
**Part A** (derivation only); the gate remap is **Part B**, deferred — see
[Part A / Part B](#part-a--part-b) below.

## The two derived dimensions

### `work_state` — the work-lifecycle dimension

Vocabulary (`WORK_STATES`, `scripts/packet_state.py:23`):

```
queued | ready | running | blocked | completed | failed | superseded | cancelled
```

`derive_work_state(packet)` (`scripts/packet_state.py:66`) maps the legacy
`status` string:

| legacy `status` | derived `work_state` | condition |
|---|---|---|
| `ready`    | `ready`     | — |
| `active`   | `running`   | — |
| `done`     | `completed` | — |
| `excepted` | `completed` | — |
| `blocked`  | `completed` | **has completion `done_evidence`** (the overloading) |
| `blocked`  | `blocked`   | no completion evidence |
| anything else (incl. empty/unknown) | `queued` | fallback |

Note: the derivation currently emits only five of the eight vocabulary states —
`{queued, ready, running, blocked, completed}`. `failed`, `superseded`, and
`cancelled` have no legacy-`status` source today; they are reserved in the
vocabulary and the transition table for Part B (parse-time orthogonal fields).

### `verification_state` — the independent-acceptance dimension

Vocabulary (`VERIFICATION_STATES`, `scripts/packet_state.py:27`):

```
not_required | pending | go | nits | fail | unable_to_verify
```

`derive_verification_state(packet)` (`scripts/packet_state.py:83`):

1. **`packet_type == "operator-verification"`** — parse the verdict out of the
   packet's `done_evidence` (joined, upper-cased). Tokens are matched on **word
   boundaries** (`\bGO\b`, `\bNITS\b`, `\bFAIL\b`), so `AGO` / `GOING` /
   `FAILED` do NOT match. Precedence is **FAIL > NITS > GO** (FAIL dominates —
   it is tested first). If no token parses:
   - `unable_to_verify` if the packet's derived `work_state == "completed"` (a
     finished verification packet with no readable verdict — honestly unknown);
   - otherwise `pending`.
2. **`packet_type` in `NON_VERIFIED_TYPES`** (`scripts/packet_state.py:44` —
   `coordinator-route`, `coordinator-join`, `coordinator-reconcile`,
   `director-brief`, `director-cosign`, `director-preflight`,
   `operator-preflight`, `operator-doc-sync`, `receipt-only`, `idle`, `blocked`)
   → `not_required` (these types are not subject to independent verification).
3. **Otherwise** (implementation-class packet):
   - `work_state == "failed"` → `fail` (unreachable under the current derivation,
     since `derive_work_state` never emits `failed` — reserved for Part B);
   - `work_state == "completed"` → `pending` (a completed implementation awaits
     the operator packet's verdict);
   - otherwise → `not_required`.

`unable_to_verify` is a **verdict, never a stored status**: the derivation is the
only thing that ever produces it, and only in case (1) above. It is never
persisted to any packet.

## `work_state` transition table

`WORK_TRANSITIONS` (`scripts/packet_state.py:32`) defines the allowed successors;
`is_valid_work_transition(src, dst)` (`scripts/packet_state.py:56`) returns
`True` iff `dst` is a permitted successor of `src` (and `False` for any unknown
`src`).

| from `src` | allowed `dst` |
|---|---|
| `queued`     | `ready`, `cancelled`, `superseded` |
| `ready`      | `running`, `cancelled`, `superseded` |
| `running`    | `blocked`, `completed`, `failed`, `cancelled`, `superseded` |
| `blocked`    | `running`, `cancelled`, `superseded` |
| `completed`  | `superseded` |
| `failed`     | `ready`, `superseded`, `cancelled` |
| `superseded` | *(none — terminal)* |
| `cancelled`  | *(none — terminal)* |

Every transition target is a member of `WORK_STATES`; forbidden edges (e.g.
`completed → running`, `superseded → anything`) return `False`. Part B's gate
validation will consume this table; Part A only exposes it.

## The load-bearing rule: `blocked` + completion evidence → `completed`

This is the ADR-017 thesis made machine-visible. G1 exactly-one coverage requires
every seat to own exactly one current packet per active cycle, so a packet whose
work is genuinely **complete** is forced to sit at `status="blocked"` to stay
represented in the cycle — the `status` string cannot say "done AND still holding
the slot." `derive_work_state` reports such a packet as `completed`, and the
`--report` CLI flags it `OVERLOADED` (`overloaded` is `True` exactly when
`legacy_status == "blocked"` and derived `work_state == "completed"`,
`scripts/packet_state.py:152`).

A `blocked` packet carrying no completion `done_evidence` stays `blocked` — it is
genuinely held, not overloaded.

## Running the read-only report

```
env -u GIT_INDEX_FILE .venv/bin/python scripts/packet_state.py --wave 2
```

Flags: `--root` (repo root containing `coordination/capacity/packets/`, defaults
to the repo root) and `--wave` (capacity wave, default `2`). The report globs
`coordination/capacity/packets/*.json`, keeps packets whose `wave` matches, and
is tolerant of unreadable/unparseable files (they are skipped, never raised).

Each row shows the legacy `status` beside the two derived dimensions, plus an
`OVERLOADED` marker:

```
id  cycle  legacy_status  work_state  verification_state  overloaded
--  -----  -------------  ----------  ------------------  ----------
...
director2-ledger-workbook-refresh-contract-correction-preflight  ...  blocked  completed  not_required  OVERLOADED
...
N packet(s); M overloaded (blocked -> completed).
```

**The report exits `0` ALWAYS.** It is a diagnostic view, never a gate: it must
not fail a pipeline, and a report line **never substitutes for executed
evidence** (anti-ceremony — a diagnostic printout is not a verdict). If you need
a GO/NITS/FAIL decision, that still comes from an operator verification packet,
not from this report.

## Part A / Part B

This slice is **Part A: derivation only.** It adds the pure derivation module and
the read-only report. It touches no live-campaign file, changes no gate, and
mutates no packet. Rolling it back is deleting new files and reverting one
append-only ADR — nothing live changes.

**Part B is DEFERRED.** Part B accepts the orthogonal fields at parse time in
`scripts/protocol_capacity.py` and remaps the G1/G5/G6 gates onto the new
`work_state` / `verification_state` dimensions. That changes the live board's
validity, so it is gated on the active **workbook-refresh campaign** closing.
Until Part B lands, the legacy `status` representation is unchanged and the
derivation is observation-only.

---

*See also:* `DECISIONS.md` → ADR-017 (rationale, consequences);
`scripts/packet_state.py` (the module); the slice plan at
`docs/superpowers/plans/2026-07-12-packet-state-derivation-slice4.md`.
