# Orthogonal Packet State — Derivation Slice 4 (P0.2, part A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Expose the overloaded capacity-packet `status` field by *deriving* orthogonal `work_state` and `verification_state` dimensions from the existing legacy fields — read-only, touching no packet file and not `scripts/protocol_capacity.py` — so the "a work-complete preflight is forced to sit at `blocked`" overloading becomes machine-visible without changing any live gate.

**Architecture:** A new stdlib-only module `scripts/packet_state.py` defines the `work_state` / `verification_state` vocabularies, a `work_state` transition table with an `is_valid_work_transition` validator, and pure `derive_work_state(packet_dict)` / `derive_verification_state(packet_dict)` functions that read the legacy `status` / `packet_type` / `done_evidence` / `verify_request` fields. A read-only `--report` CLI renders each wave packet's legacy status beside its derived states and flags the divergences (a `blocked` packet whose real `work_state` is `completed`). Nothing is written; no gate changes. This is **part A** of P0.2: the derivation foundation. **Part B** (accepting the new fields at parse time in `protocol_capacity.py` and remapping the G1/G5/G6 gates onto the orthogonal dimensions) is deliberately deferred — it changes the live board's validity and is gated on the workbook-refresh campaign closing (still open as of this plan: 2 active-wip packets).

**Tech Stack:** Python ≥3.11 stdlib + pytest. No new dependencies. Reads capacity-packet JSON (`coordination/capacity/packets/*.json`).

## Provenance

Implements the **safe half of roadmap Slice 4 (P0.2)** of the 2026-07-11 governance-brief audit. P0.2 verdict was **agree_with_modifications** (none refuted); the overloading is code-confirmed: a real `director-preflight` packet (`coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-director2-contract-correction-preflight.json`) sits at `status="blocked"` while carrying completion `done_evidence` — because G1 exactly-one-coverage (`protocol_capacity.py:601-624`) forces a work-complete packet to stay represented in the active cycle. Adopted modifications bound into this plan:
- First slice is a **pure derivation module** with no packet-file edits (audit first-slice framing).
- The **G1/G5/G6 gate remap** (Part B) is gated on the workbook-refresh cycle close; not in this slice.
- Reconcile `unable_to_verify` with anti-ceremony (it is a *verdict*, never a stored status): the derivation may return `unable_to_verify` only for an operator-verification packet that is completed but carries no parseable verdict — an honest "the legacy fields don't say," which is itself the argument for orthogonal fields. It is never written anywhere.
- `capacity_state` (the third dimension) needs per-seat presence data and is deferred; this slice does the two per-packet dimensions.

## Global Constraints

- Python ≥3.11 only; no 3.12+/3.13-only syntax (ADR-004). No new dependencies.
- **No live-campaign infrastructure:** do NOT modify `scripts/protocol_capacity.py`, any file under `coordination/`, `scripts/route_manifest.py`, `scripts/route_lineage.py`, `scripts/route_capability.py`, `scripts/ledger_start_guard.py`, `AGENTS.md`, `.agents/**`, `ARCHITECTURE.md`, `docs/protocol/threeway/*`. The derivation READS packet JSON but writes nothing and changes no gate.
- The `--report` CLI is a diagnostic: **exit 0 always**, no GO/PASS semantics (a report line never substitutes for executed evidence — anti-ceremony §8.6). It reads packets read-only.
- Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE`. Explicit pathspecs only; never bare `git commit`/`git add -A` — a **very active coordinator lane** holds dirty WIP and lands commits frequently. Immediately before each commit run `env -u GIT_INDEX_FILE git log --oneline -5`; if new commits touch NONE of your task's files, proceed and note the new HEAD; else report BLOCKED.
- Every commit body includes `User-principal directed immediate execution 2026-07-12 (all seats stale).` and ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push (user-gated).
- `DECISIONS.md` is append-only. Tests import bare (`import packet_state`); `pyproject.toml` sets `pythonpath = [".", "scripts"]`.
- All factual claims in commit bodies cite the producing command (R-EVIDENCE).

---

### Task 1: ADR-017 — orthogonal packet state (derivation-first; gate remap deferred)

**Files:** Modify `DECISIONS.md` (append after ADR-016).

- [ ] **Step 1: Append ADR-017** (adjust the cited line/path only if re-verification shows drift — grep the `Packet` dataclass in `protocol_capacity.py` and confirm the named live packet still shows `status:"blocked"` with `done_evidence`):

```markdown
## ADR-017: Orthogonal packet state — derive work/verification dimensions (Part A: derivation only)

**Status:** Accepted (derivation module only; the gate remap is deferred)

**Context:**
The capacity-packet `status` field (ready|active|blocked|done|excepted,
`scripts/protocol_capacity.py`) overloads three orthogonal facts: what
happened to the work, whether the seat is still represented in the active
cycle, and whether the result was independently accepted. Because G1
exactly-one coverage requires every seat to own exactly one current packet
per active cycle, a work-COMPLETE packet is forced to sit at `blocked` — e.g.
the workbook-refresh director2 preflight carries completion `done_evidence`
yet status is `blocked`. `done` separately doubles as the verification
carrier for G5/G6. This damages semantic truth and blocks future automation.

**Decision:**
1. Add `scripts/packet_state.py`: the `work_state` and `verification_state`
   vocabularies, a `work_state` transition table + `is_valid_work_transition`,
   and pure `derive_work_state` / `derive_verification_state` functions that
   read the legacy `status` / `packet_type` / `done_evidence` / `verify_request`
   fields. The derivation is READ-ONLY: it writes no packet, adds no field,
   and changes no gate.
2. A `--report` CLI renders legacy status beside the derived states and flags
   divergences (a `blocked` packet whose derived `work_state` is `completed` —
   the overloading made visible). Exit 0 always; it is a diagnostic, never a
   gate.
3. `unable_to_verify` is a verdict, never a stored status; the derivation may
   return it only for a completed operator-verification packet with no
   parseable verdict, and it is never persisted.
4. Part B — accepting orthogonal fields at parse time in `protocol_capacity.py`
   and remapping G1/G5/G6 onto the new dimensions — is DEFERRED. It changes the
   live board's validity and is gated on the active workbook-refresh cycle
   closing.

**Consequences:**
- The completed-vs-blocked overloading becomes machine-visible without any
  change to live gates or packet files; the active campaign is unaffected.
- The derivation is the semantic-truth foundation Part B will wire into the
  gates once the campaign closes.
- No packet ever needs to be mislabeled to satisfy coverage once Part B lands;
  until then the legacy representation is unchanged.
```

- [ ] **Step 2: Commit** (Rule #7 pre-check first): `env -u GIT_INDEX_FILE git commit -m "docs(adr): ADR-017 orthogonal packet state (derivation-first, gate remap deferred)

User-principal directed immediate execution 2026-07-12 (all seats stale).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- DECISIONS.md`

---

### Task 2: packet_state.py — vocabularies, transition table, pure derivation

**Files:** Create `scripts/packet_state.py`; create `tests/unit/test_packet_state.py`.

**Interfaces produced:** `WORK_STATES: tuple[str,...]`; `VERIFICATION_STATES: tuple[str,...]`; `WORK_TRANSITIONS: dict[str, frozenset[str]]`; `is_valid_work_transition(src: str, dst: str) -> bool`; `derive_work_state(packet: dict) -> str`; `derive_verification_state(packet: dict) -> str`; `NON_VERIFIED_TYPES: frozenset[str]`.

- [ ] **Step 1: Write failing tests** `tests/unit/test_packet_state.py`. Cover the derivation truth table and the transition validator. The load-bearing assertions (pin the P0.2 thesis):

```python
"""Orthogonal packet-state derivation from legacy fields (ADR-017)."""
from __future__ import annotations

import packet_state


def _pkt(**overrides) -> dict:
    base = {
        "id": "p", "wave": 2, "cycle": "c", "owner": "director",
        "packet_type": "director-implementation", "status": "active",
        "done_evidence": [], "verify_request": None, "commit_range": None,
    }
    base.update(overrides)
    return base


# --- work_state derivation ---
def test_ready_derives_ready():
    assert packet_state.derive_work_state(_pkt(status="ready")) == "ready"


def test_active_derives_running():
    assert packet_state.derive_work_state(_pkt(status="active")) == "running"


def test_done_derives_completed():
    assert packet_state.derive_work_state(_pkt(status="done", done_evidence=["x"])) == "completed"


def test_blocked_without_evidence_stays_blocked():
    assert packet_state.derive_work_state(_pkt(status="blocked", done_evidence=[])) == "blocked"


def test_blocked_with_evidence_is_completed_the_overloading():
    # THE P0.2 thesis: a 'blocked' packet carrying completion evidence is work-complete.
    pkt = _pkt(status="blocked", packet_type="director-preflight",
               done_evidence=["coordination/mailbox/sent/…records CLEAR at reviewed route commit …"])
    assert packet_state.derive_work_state(pkt) == "completed"


def test_excepted_derives_completed():
    assert packet_state.derive_work_state(_pkt(status="excepted")) == "completed"


def test_unknown_status_is_queued():
    assert packet_state.derive_work_state(_pkt(status="")) == "queued"


# --- verification_state derivation ---
def test_coordinator_route_not_required():
    assert packet_state.derive_verification_state(_pkt(packet_type="coordinator-route", status="active")) == "not_required"


def test_preflight_not_required():
    assert packet_state.derive_verification_state(_pkt(packet_type="director-preflight", status="blocked", done_evidence=["x"])) == "not_required"


def test_completed_implementation_is_pending_verification():
    pkt = _pkt(packet_type="director-implementation", status="done", done_evidence=["landed"])
    assert packet_state.derive_verification_state(pkt) == "pending"


def test_operator_verification_parses_go():
    pkt = _pkt(packet_type="operator-verification", status="done",
               done_evidence=["verification-report: VERDICT GO for range abc..def"])
    assert packet_state.derive_verification_state(pkt) == "go"


def test_operator_verification_parses_fail():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["FAIL: regression"])
    assert packet_state.derive_verification_state(pkt) == "fail"


def test_operator_verification_parses_nits():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["NITS: minor doc"])
    assert packet_state.derive_verification_state(pkt) == "nits"


def test_operator_verification_completed_without_verdict_is_unable():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["did the review"])
    assert packet_state.derive_verification_state(pkt) == "unable_to_verify"


def test_go_word_boundary_not_substring():
    # 'ago' or 'going' must not match the GO verdict token.
    pkt = _pkt(packet_type="operator-verification", status="done",
               done_evidence=["a while ago the work was ongoing"])
    assert packet_state.derive_verification_state(pkt) == "unable_to_verify"


# --- transition table ---
def test_valid_transitions():
    assert packet_state.is_valid_work_transition("ready", "running")
    assert packet_state.is_valid_work_transition("running", "completed")
    assert packet_state.is_valid_work_transition("running", "blocked")
    assert packet_state.is_valid_work_transition("blocked", "running")


def test_invalid_transitions():
    assert not packet_state.is_valid_work_transition("completed", "running")
    assert not packet_state.is_valid_work_transition("superseded", "running")
    assert not packet_state.is_valid_work_transition("ready", "completed")


def test_every_transition_target_is_a_known_state():
    known = set(packet_state.WORK_STATES)
    for src, dsts in packet_state.WORK_TRANSITIONS.items():
        assert src in known
        assert dsts <= known
```

- [ ] **Step 2: Run — expect `ModuleNotFoundError: packet_state`.**

- [ ] **Step 3: Write `scripts/packet_state.py`:**

```python
#!/usr/bin/env python3
"""Orthogonal packet-state derivation from legacy capacity-packet fields (ADR-017).

The capacity-packet ``status`` field overloads work-lifecycle, seat-capacity,
and verification into one string. This module DERIVES the orthogonal
``work_state`` and ``verification_state`` dimensions from the legacy
``status`` / ``packet_type`` / ``done_evidence`` / ``verify_request`` fields.
It is READ-ONLY: it writes no packet, adds no field, and changes no gate. The
gate remap (Part B) is deferred (see ADR-017).

The load-bearing insight: a packet at ``status="blocked"`` that carries
completion ``done_evidence`` is work-COMPLETE but held at ``blocked`` to
satisfy G1 coverage — ``derive_work_state`` reports it as ``completed``, making
the overloading visible.
"""
from __future__ import annotations

import re

WORK_STATES = (
    "queued", "ready", "running", "blocked",
    "completed", "failed", "superseded", "cancelled",
)
VERIFICATION_STATES = (
    "not_required", "pending", "go", "nits", "fail", "unable_to_verify",
)

# Allowed work_state transitions (Part-B gate validation will consume this).
WORK_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"ready", "cancelled", "superseded"}),
    "ready": frozenset({"running", "cancelled", "superseded"}),
    "running": frozenset({"blocked", "completed", "failed", "cancelled", "superseded"}),
    "blocked": frozenset({"running", "cancelled", "superseded"}),
    "completed": frozenset({"superseded"}),
    "failed": frozenset({"ready", "superseded", "cancelled"}),
    "superseded": frozenset(),
    "cancelled": frozenset(),
}

# Packet types that are not subject to independent (operator) verification.
NON_VERIFIED_TYPES = frozenset({
    "coordinator-route", "coordinator-join", "coordinator-reconcile",
    "director-brief", "director-cosign", "director-preflight",
    "operator-preflight", "operator-doc-sync", "receipt-only",
    "idle", "blocked",
})

_GO_RE = re.compile(r"\bGO\b")
_NITS_RE = re.compile(r"\bNITS\b")
_FAIL_RE = re.compile(r"\bFAIL\b")


def is_valid_work_transition(src: str, dst: str) -> bool:
    """True iff dst is a permitted work_state successor of src."""
    return dst in WORK_TRANSITIONS.get(src, frozenset())


def _has_evidence(packet: dict) -> bool:
    evidence = packet.get("done_evidence") or []
    return bool([item for item in evidence if str(item).strip()])


def derive_work_state(packet: dict) -> str:
    """Derive the work-lifecycle dimension from the legacy status field."""
    status = str(packet.get("status", "")).strip()
    if status == "ready":
        return "ready"
    if status == "active":
        return "running"
    if status == "done":
        return "completed"
    if status == "excepted":
        return "completed"
    if status == "blocked":
        # The overloading: completion evidence at blocked == work-complete, held.
        return "completed" if _has_evidence(packet) else "blocked"
    return "queued"


def derive_verification_state(packet: dict) -> str:
    """Derive whether the result has been independently accepted."""
    packet_type = str(packet.get("packet_type", "")).strip()
    evidence = " ".join(str(item) for item in (packet.get("done_evidence") or [])).upper()
    if packet_type == "operator-verification":
        if _FAIL_RE.search(evidence):
            return "fail"
        if _NITS_RE.search(evidence):
            return "nits"
        if _GO_RE.search(evidence):
            return "go"
        # Completed verification packet with no parseable verdict: honestly unknown.
        return "unable_to_verify" if derive_work_state(packet) == "completed" else "pending"
    if packet_type in NON_VERIFIED_TYPES:
        return "not_required"
    # Implementation-class packets are subject to independent verification.
    work = derive_work_state(packet)
    if work == "failed":
        return "fail"
    if work == "completed":
        return "pending"  # completed impl awaits the operator packet's verdict
    return "not_required"
```

- [ ] **Step 4: Run tests — expect all pass. Commit** `-- scripts/packet_state.py tests/unit/test_packet_state.py`.

---

### Task 3: read-only `--report` CLI (overloading made visible)

**Files:** Modify `scripts/packet_state.py` (append `load_packets` + `build_report` + `main`); modify `tests/unit/test_packet_state.py` (append).

**Interfaces produced:** `load_packets(root: Path, wave: int) -> list[dict]` (globs `coordination/capacity/packets/*.json`, filters by `wave`, tolerant of unreadable/unparseable files); `build_report(packets: list[dict]) -> dict` (per-packet: id, cycle, legacy status, work_state, verification_state, `overloaded: bool` where a `blocked` legacy status derives `completed`); `main(argv) -> int` (prints the report; **exit 0 always**).

- [ ] **Step 1: Write failing tests** (write packet JSONs to a tmp `coordination/capacity/packets/`, then):

```python
import json
from pathlib import Path


def _write_pkt(root: Path, pkt: dict) -> None:
    d = root / "coordination" / "capacity" / "packets"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{pkt['id']}.json").write_text(json.dumps(pkt), encoding="utf-8")


def test_build_report_flags_blocked_completed_overloading(tmp_path):
    _write_pkt(tmp_path, _pkt(id="held", wave=2, status="blocked",
                              packet_type="director-preflight", done_evidence=["CLEAR at route commit abc"]))
    _write_pkt(tmp_path, _pkt(id="run", wave=2, status="active"))
    packets = packet_state.load_packets(tmp_path, 2)
    report = packet_state.build_report(packets)
    rows = {r["id"]: r for r in report["packets"]}
    assert rows["held"]["legacy_status"] == "blocked"
    assert rows["held"]["work_state"] == "completed"
    assert rows["held"]["overloaded"] is True
    assert rows["run"]["overloaded"] is False


def test_load_packets_filters_by_wave(tmp_path):
    _write_pkt(tmp_path, _pkt(id="w2", wave=2, status="active"))
    _write_pkt(tmp_path, _pkt(id="w9", wave=9, status="active"))
    ids = {p["id"] for p in packet_state.load_packets(tmp_path, 2)}
    assert ids == {"w2"}


def test_load_packets_tolerates_bad_json(tmp_path):
    d = tmp_path / "coordination" / "capacity" / "packets"
    d.mkdir(parents=True)
    (d / "broken.json").write_text("{not json", encoding="utf-8")
    _write_pkt(tmp_path, _pkt(id="ok", wave=2, status="active"))
    ids = {p["id"] for p in packet_state.load_packets(tmp_path, 2)}
    assert ids == {"ok"}


def test_cli_report_exits_zero_always(tmp_path, capsys):
    _write_pkt(tmp_path, _pkt(id="held", wave=2, status="blocked", done_evidence=["x"]))
    rc = packet_state.main(["--root", str(tmp_path), "--wave", "2"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "held" in out and "completed" in out
```

- [ ] **Step 2: RED, then append `load_packets` + `build_report` + `main`** (argparse `--root` default repo root, `--wave` default 2; print a readable table; `main` returns 0 unconditionally). **GREEN.** Confirm on the live repo: `env -u GIT_INDEX_FILE .venv/bin/python scripts/packet_state.py --wave 2` exits 0 and shows the real workbook-refresh preflight as `blocked → completed (overloaded)`. **Commit** `-- scripts/packet_state.py tests/unit/test_packet_state.py`.

---

### Task 4: doc + final full-gate verification

**Files:** Create `docs/protocol/packet-state.md`.

- [ ] **Step 1: Write `docs/protocol/packet-state.md`** — the two derived dimensions and their vocabularies; the transition table; the derivation rules (especially `blocked + done_evidence → completed`, the overloading); how to run the read-only report; and the explicit note that this is Part A (derivation only) with the gate remap (Part B) deferred until the workbook-refresh campaign closes. Show the exact command and verify it runs literally. State that the report is a diagnostic (exit 0 always), never a gate.

- [ ] **Step 2: Final gates (paste outputs into the commit body — R-EVIDENCE):**

```
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/packet_state.py --wave 2
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expect: suite green (prior total + the new packet-state tests, 0 failures, 1 pre-existing xfail unchanged); smoke OK; report exit 0 and shows at least one `overloaded` packet from the live set; diff-stat shows only this slice's files.

- [ ] **Step 3: Commit** `-- docs/protocol/packet-state.md`. Independent verification (Codex Lane-V) is dispatched by the controller after this task; NO push regardless.

---

## Acceptance criteria (P0.2 Part A, from the brief as modified by the audit)

1. `work_state` and `verification_state` are derivable purely from legacy fields — pure functions, no I/O, no mutation.
2. The completed-vs-blocked overloading is made visible — a `blocked` packet with completion evidence derives `work_state="completed"` and is flagged `overloaded` (proven against the real workbook-refresh preflight).
3. A `work_state` transition table exists with a validator; every transition target is a known state; forbidden edges (e.g. `completed→running`) return False.
4. `unable_to_verify` is returned only for a completed operator-verification packet with no parseable verdict, and is never persisted.
5. No live-campaign file touched; no gate changed; the report is exit-0-always and never substitutes for evidence.
6. Verdict tokens (GO/NITS/FAIL) are matched on word boundaries, not substrings (`ago`/`going` do not match GO).

## Rollback

All new files (module, one doc, tests) plus one append-only ADR. Revert the slice's commits; nothing live changed, no migration to unwind. Part B (the gate remap) remains a separate future slice gated on campaign close.
