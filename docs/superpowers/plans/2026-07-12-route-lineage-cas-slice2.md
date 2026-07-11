# Route Lineage + Compare-and-Swap — Slice 2 (P0.3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make route currency depend on a typed lineage (monotone `generation` + `parent` pointer + compare-and-swap) instead of filename-timestamp sort — while staying byte-for-byte behavior-preserving on the live campaign, whose routes carry no generation header yet.

**Architecture:** A new stdlib-only module `scripts/route_lineage.py` parses the lineage headers the route/v1 renderer already emits (`Route generation:`, `Supersedes route:`/`Supersedes active route:`, `Expected control HEAD:`) plus the parent-only form live coordinator routes use. It resolves the **authoritative route = the lineage tip** (highest-generation route that no other route supersedes) and offers a compare-and-swap check that returns a structured `stale_parent` result when a proposed route's parent isn't the current tip or its generation isn't current+1. `find_latest_ledger_route` becomes lineage-first with a legacy reverse-lex fallback that fires whenever no candidate carries a generation — so the current live route set (zero generations) resolves exactly as today. A `--check` CLI (wired into `protocol_doctor`) fails only on lineage inconsistency among generation-bearing routes; it passes trivially on the all-legacy live set.

**Tech Stack:** Python ≥3.11 stdlib + pytest. No new dependencies. Consumes Slice-1's route/v1 (ADR-014) lineage fields and `scripts/target_binding.py` (ADR-013).

## Provenance

Implements roadmap **Slice 2** of the 2026-07-11 governance-brief audit (see `docs/superpowers/plans/2026-07-11-typed-route-authority-slice1.md` roadmap table). The audit's P0.3 verdict was **agree_with_modifications** (none refuted), premises code-confirmed: the only automatic current-route resolver is reverse-lex filename sort (`scripts/ledger_start_guard.py:67`), and `Supersedes route:` prose is parsed by nothing. Adopted modifications, bound into this plan:
- Implement as git-committed lineage validation reusing local patterns; do **not** activate the dormant threeway signed bus (ADR-010).
- Demote `expected_control_head` from whole-repo HEAD equality to a parsed/reported hint (parent + generation are the hard gate).
- Lineage fields already live in the route/v1 schema (Slice 1) — this slice makes them **authoritative for selection**.
- Extend scope to resolution **and** enforcement: rewire `find_latest_ledger_route` lineage-first with legacy fallback; add a check wired into `protocol_doctor`.
- Append an ADR.

## Global Constraints

- Python ≥3.11 only; no 3.12+/3.13-only syntax (ADR-004). No new dependencies.
- **Behavior preservation is the headline constraint:** on any route set where no candidate carries a `Route generation:` header (the entire live campaign today), `find_latest_ledger_route` MUST return exactly what today's reverse-lex sort returns. The pre-existing `tests/unit/test_codex_ledger_bridge.py` guard tests must pass UNMODIFIED.
- Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE`. Explicit pathspecs only (`git commit -m "..." -- <paths>`); never bare `git commit`/`git add -A` — a **very active coordinator lane** holds dirty WIP and lands commits frequently. Immediately before each commit run `env -u GIT_INDEX_FILE git log --oneline -5`; if new commits touch NONE of your task's files, proceed and note the new HEAD; if they touch your files, report BLOCKED.
- Every commit body includes `User-principal directed immediate execution 2026-07-12 (all seats stale).` and ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push (user-gated).
- Do not touch: `scripts/protocol_capacity.py`, `scripts/route_manifest.py`, `scripts/route_compat.py` (Slice-1 frozen), `ARCHITECTURE.md` (parked-worktree dirty), `AGENTS.md`, `.agents/**`, `docs/protocol/threeway/*`, `coordination/**`.
- `DECISIONS.md` is append-only. Tests import bare (`import route_lineage`); `pyproject.toml` sets `pythonpath = [".", "scripts"]`.
- All factual claims in commit bodies cite the producing command (R-EVIDENCE).

---

### Task 1: ADR-015 — route lineage authority (generation + parent + CAS)

**Files:** Modify `DECISIONS.md` (append after ADR-014).

- [ ] **Step 1: Append ADR-015** (adjust the two cited line numbers only if re-verification shows drift — grep `find_latest_ledger_route` in `scripts/ledger_start_guard.py` and the `Route generation:` emit in `scripts/route_manifest.py`):

```markdown
## ADR-015: Route currency from typed lineage (generation + parent + compare-and-swap)

**Status:** Accepted

**Context:**
The only automatic current-route resolver is reverse-lexicographic filename
sort (`scripts/ledger_start_guard.py` `find_latest_ledger_route`), so a
transient filesystem observation or a stale writer whose artifact name sorts
later could appear authoritative. `Supersedes route:` / `Supersedes active
route:` parent pointers exist in live coordinator routes but are parsed by no
code. Slice 1 (ADR-014) added `generation` / `parent_route_id` /
`expected_control_head` to route/v1 and its renderer emits them, but nothing
consumes them for selection.

**Decision:**
1. Add `scripts/route_lineage.py`: parse the lineage headers (`Route
   generation:`, `Supersedes route:` and its `Supersedes active route:`
   alias, backtick-optional; `Expected control HEAD:`), resolve the
   authoritative route as the lineage TIP (highest-generation route no other
   route supersedes), and offer a compare-and-swap check returning a
   structured `stale_parent` result when a proposed route's parent is not the
   current tip or its generation is not current+1.
2. Rewire `find_latest_ledger_route` lineage-first with a legacy fallback:
   when no candidate route carries a generation header, resolution is
   byte-identical to the prior reverse-lex behavior. The live campaign (zero
   generation headers) is unaffected.
3. `expected_control_head` is parsed and reported, not gated on whole-repo
   HEAD equality (audit modification) — parent + generation are the hard gate.
4. A `route_lineage.py --check` CLI, wired into `scripts/protocol_doctor.py`,
   fails only on lineage inconsistency among generation-bearing routes (a
   fork — two tips at the same generation — or a cycle). It passes on the
   all-legacy live set.
5. This does not activate the dormant signed bus (ADR-010); lineage lives in
   the git-committed mailbox route bodies.

**Consequences:**
- Two concurrent coordinators cannot both become authoritative once routes
  carry generations: a fork is detected (structured issue) and CAS rejects
  the stale writer with a `stale_parent` result to rebase.
- Route ancestry is auditable from parent pointers; resolution is
  deterministic and independent of filename timestamp for
  generation-bearing routes.
- No behavior change for legacy routes; the pre-existing start-guard tests
  pass unmodified.
```

- [ ] **Step 2: Commit** (Rule #7 pre-check first): `env -u GIT_INDEX_FILE git commit -m "docs(adr): ADR-015 route lineage authority (generation + parent + CAS)\n\nUser-principal directed immediate execution 2026-07-12 (all seats stale).\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- DECISIONS.md`

---

### Task 2: lineage parsing (headers → RouteLineage)

**Files:** Create `scripts/route_lineage.py`; create `tests/unit/test_route_lineage.py`.

**Interfaces produced:** `route_id_of(path_or_name: str) -> str`; `RouteLineage` (frozen dataclass: `generation: int|None`, `parent_route_id: str|None`, `expected_control_head: str|None`); `parse_lineage(body: str) -> RouteLineage`; the regexes `_GENERATION_RE`, `_SUPERSEDES_RE`, `_CONTROL_HEAD_RE`.

- [ ] **Step 1: Write failing tests** `tests/unit/test_route_lineage.py`:

```python
"""Route lineage parsing, resolution, and compare-and-swap (ADR-015)."""
from __future__ import annotations

import route_lineage


def test_route_id_of_strips_path_and_md_suffix():
    assert route_lineage.route_id_of(
        "coordination/mailbox/sent/2026-07-11T09-42-22Z-coordinator-to-all-coordination.md"
    ) == "2026-07-11T09-42-22Z-coordinator-to-all-coordination"
    assert route_lineage.route_id_of("  `foo.md`  ".strip("` ")) == "foo"


def test_parse_generation_and_parent_backtick_and_plain():
    backtick = (
        "Task-board: x\n"
        "Supersedes active route: `coordination/mailbox/sent/2026-07-10T22-47-55Z-coordinator-to-all-coordination.md`\n"
        "Route generation: 7\n"
    )
    plain = (
        "Task-board: x\n"
        "Supersedes route: coordination/mailbox/sent/2026-07-11T07-38-30Z-coordinator-to-all-coordination.md\n"
        "Route generation: 12\n"
        "Expected control HEAD: 808bda9\n"
    )
    a = route_lineage.parse_lineage(backtick)
    assert a.generation == 7
    assert a.parent_route_id == "2026-07-10T22-47-55Z-coordinator-to-all-coordination"
    assert a.expected_control_head is None
    b = route_lineage.parse_lineage(plain)
    assert b.generation == 12
    assert b.parent_route_id == "2026-07-11T07-38-30Z-coordinator-to-all-coordination"
    assert b.expected_control_head == "808bda9"


def test_parse_legacy_route_without_generation():
    body = "Task-board: x\nSupersedes route: coordination/mailbox/sent/foo.md\n"
    parsed = route_lineage.parse_lineage(body)
    assert parsed.generation is None
    assert parsed.parent_route_id == "foo"


def test_parse_first_generation_no_parent():
    parsed = route_lineage.parse_lineage("Task-board: x\nRoute generation: 1\n")
    assert parsed.generation == 1
    assert parsed.parent_route_id is None


def test_control_head_lowercased():
    parsed = route_lineage.parse_lineage("Expected control HEAD: 808BDA9\n")
    assert parsed.expected_control_head == "808bda9"
```

- [ ] **Step 2: Run — expect `ModuleNotFoundError: route_lineage`.**

- [ ] **Step 3: Write `scripts/route_lineage.py`:**

```python
#!/usr/bin/env python3
"""Route lineage: generation + parent + compare-and-swap authority (ADR-015).

Route currency stops depending on filename timestamp sort. A route carries a
monotone ``Route generation:`` and a ``Supersedes route:`` parent pointer (both
already emitted by route/v1 render_markdown; the parent form is used by live
coordinator routes). The authoritative route is the lineage TIP: the
highest-generation route that no other route supersedes. A proposed route is
accepted only when its parent is the current tip and its generation is
current+1 (compare-and-swap); otherwise a structured stale_parent result is
returned. Legacy routes without a generation header fall back to the previous
reverse-lexicographic filename resolution, so the live campaign is unaffected.
This does not activate the dormant signed bus (ADR-010).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent

_GENERATION_RE = re.compile(
    r"^\s*Route generation:\s*(?P<value>\d+)\s*$", re.IGNORECASE | re.MULTILINE
)
_SUPERSEDES_RE = re.compile(
    r"^\s*Supersedes(?: active)? route:\s*`?(?P<value>[^`\n]+?)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_CONTROL_HEAD_RE = re.compile(
    r"^\s*(?:Expected control HEAD|Control HEAD):\s*`?(?P<value>[0-9a-fA-F]{7,40})`?\s*$",
    re.MULTILINE,
)


def route_id_of(path_or_name: str) -> str:
    """Normalize a route reference (path or filename) to its bare stem."""
    name = Path(path_or_name.strip()).name
    if name.endswith(".md"):
        name = name[:-3]
    return name


@dataclass(frozen=True)
class RouteLineage:
    generation: int | None
    parent_route_id: str | None
    expected_control_head: str | None


def parse_lineage(body: str) -> RouteLineage:
    gen_match = _GENERATION_RE.search(body)
    sup_match = _SUPERSEDES_RE.search(body)
    head_match = _CONTROL_HEAD_RE.search(body)
    return RouteLineage(
        generation=int(gen_match.group("value")) if gen_match else None,
        parent_route_id=route_id_of(sup_match.group("value")) if sup_match else None,
        expected_control_head=head_match.group("value").lower() if head_match else None,
    )
```

- [ ] **Step 4: Run tests — expect all pass. Commit** `-- scripts/route_lineage.py tests/unit/test_route_lineage.py`.

---

### Task 3: authoritative-tip resolution + compare-and-swap

**Files:** Modify `scripts/route_lineage.py` (append); modify `tests/unit/test_route_lineage.py` (append).

**Interfaces produced:** `LineageRoute` (frozen: `route_id: str`, `lineage: RouteLineage`); `Resolution` (frozen: `winner: str|None`, `mode: str` in {`"lineage"`,`"legacy"`,`"empty"`}, `issues: tuple[str, ...]`); `resolve_authoritative(routes: list[LineageRoute]) -> Resolution`; `CasResult` (frozen: `ok: bool`, `reason: str`); `check_cas(current: LineageRoute, proposed: LineageRoute) -> CasResult`.

- [ ] **Step 1: Append failing tests to `tests/unit/test_route_lineage.py`:**

```python
def _lr(route_id, generation=None, parent=None):
    return route_lineage.LineageRoute(
        route_id, route_lineage.RouteLineage(generation, parent, None)
    )


def test_resolve_empty():
    assert route_lineage.resolve_authoritative([]).mode == "empty"


def test_resolve_legacy_when_no_generation():
    res = route_lineage.resolve_authoritative([_lr("a"), _lr("b")])
    assert res.mode == "legacy" and res.winner is None


def test_resolve_lineage_tip_is_unsuperseded_highest_generation():
    routes = [
        _lr("r1", generation=1, parent=None),
        _lr("r2", generation=2, parent="r1"),
        _lr("r3", generation=3, parent="r2"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode == "lineage" and res.winner == "r3" and res.issues == ()


def test_resolve_detects_forked_lineage_two_tips_same_generation():
    routes = [
        _lr("r1", generation=1, parent=None),
        _lr("r2a", generation=2, parent="r1"),
        _lr("r2b", generation=2, parent="r1"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode == "lineage"
    assert res.winner is not None  # still deterministic
    assert any("forked lineage" in issue for issue in res.issues)


def test_resolve_detects_cycle_no_tip():
    routes = [
        _lr("r1", generation=2, parent="r2"),
        _lr("r2", generation=1, parent="r1"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.winner is None
    assert any("no tip" in issue for issue in res.issues)


def test_resolve_is_deterministic_regardless_of_input_order():
    a = [_lr("r1", 1, None), _lr("r2", 2, "r1")]
    b = list(reversed(a))
    assert (
        route_lineage.resolve_authoritative(a).winner
        == route_lineage.resolve_authoritative(b).winner
        == "r2"
    )


def test_cas_accepts_parent_tip_and_next_generation():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r3", generation=3, parent="r2")
    assert route_lineage.check_cas(current, proposed).ok


def test_cas_rejects_wrong_parent_with_stale_parent():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r3", generation=3, parent="r1")  # stale: parent is not the tip
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "stale_parent" in result.reason


def test_cas_rejects_non_incremented_generation():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r9", generation=9, parent="r2")
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "stale_parent" in result.reason
```

- [ ] **Step 2: Run — expect failures (`AttributeError: ... 'LineageRoute'`).**

- [ ] **Step 3: Append to `scripts/route_lineage.py`:**

```python
@dataclass(frozen=True)
class LineageRoute:
    route_id: str
    lineage: RouteLineage


@dataclass(frozen=True)
class Resolution:
    winner: str | None
    mode: str  # "lineage" | "legacy" | "empty"
    issues: tuple[str, ...] = field(default_factory=tuple)


def resolve_authoritative(routes: list[LineageRoute]) -> Resolution:
    """Pick the authoritative route. Lineage-first; caller does legacy fallback.

    Lineage resolution fires only when at least one route carries a
    generation. The tip is a generation-bearing route no other route
    supersedes; the winner is the highest-generation tip (ties broken by
    route_id for determinism), and a same-generation multi-tip fork or a
    tip-less cycle is reported as a structured issue.
    """
    if not routes:
        return Resolution(winner=None, mode="empty")
    gen_routes = [r for r in routes if r.lineage.generation is not None]
    if not gen_routes:
        return Resolution(winner=None, mode="legacy")
    superseded = {
        r.lineage.parent_route_id for r in routes if r.lineage.parent_route_id
    }
    tips = [r for r in gen_routes if r.route_id not in superseded]
    if not tips:
        return Resolution(
            winner=None,
            mode="lineage",
            issues=("lineage has no tip (cycle or every generation superseded)",),
        )
    tips.sort(key=lambda r: (r.lineage.generation, r.route_id), reverse=True)
    top_generation = tips[0].lineage.generation
    top_tips = [r for r in tips if r.lineage.generation == top_generation]
    issues: tuple[str, ...] = ()
    if len(top_tips) > 1:
        issues = (
            f"forked lineage: multiple tips at generation {top_generation}: "
            + ", ".join(sorted(r.route_id for r in top_tips)),
        )
    return Resolution(winner=tips[0].route_id, mode="lineage", issues=issues)


@dataclass(frozen=True)
class CasResult:
    ok: bool
    reason: str = ""


def check_cas(current: LineageRoute, proposed: LineageRoute) -> CasResult:
    """Accept proposed as the next authoritative route only under compare-and-swap.

    parent must equal the current tip AND generation must be current + 1.
    Any mismatch is a structured stale_parent refusal (the writer must rebase).
    """
    if proposed.lineage.parent_route_id != current.route_id:
        return CasResult(
            ok=False,
            reason=(
                f"stale_parent: proposed parent {proposed.lineage.parent_route_id!r} "
                f"is not the current tip {current.route_id!r}"
            ),
        )
    if current.lineage.generation is None or proposed.lineage.generation is None:
        return CasResult(
            ok=False, reason="stale_parent: missing generation on current or proposed"
        )
    if proposed.lineage.generation != current.lineage.generation + 1:
        return CasResult(
            ok=False,
            reason=(
                f"stale_parent: proposed generation {proposed.lineage.generation} "
                f"is not current {current.lineage.generation} + 1"
            ),
        )
    return CasResult(ok=True)
```

- [ ] **Step 4: Run tests — expect all pass. Commit** `-- scripts/route_lineage.py tests/unit/test_route_lineage.py`.

---

### Task 4: lineage-first resolution in the guard + `--check` CLI wired into protocol_doctor

**Files:** Modify `scripts/ledger_start_guard.py` (`find_latest_ledger_route`, add `import route_lineage`); modify `scripts/route_lineage.py` (append `load_routes` + `main`); modify `scripts/protocol_doctor.py` (`base_commands`); modify `tests/unit/test_route_lineage.py` (append); modify `tests/unit/test_target_binding.py` (append one doctor-wiring assertion) — OR add to `test_route_lineage.py` (choose the latter to avoid touching the binding test file; put the doctor assertion in `test_route_lineage.py`).

**Interfaces produced:** `load_routes(root: Path) -> list[LineageRoute]` (reads every `*coordinator-to-all*.md` under `root/coordination/mailbox/sent/`, parsing lineage); `main(argv) -> int` (the `--check` CLI). `find_latest_ledger_route` keeps its exact signature and legacy return value.

- [ ] **Step 1: Append failing tests to `tests/unit/test_route_lineage.py`:**

```python
import json
from pathlib import Path


def _write_route(root: Path, name: str, body: str) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / name
    path.write_text(body, encoding="utf-8")
    return path


def test_find_latest_is_lineage_tip_when_generations_present(tmp_path):
    import ledger_start_guard

    # older filename carries the HIGHER generation -> lineage must beat filename sort
    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-a\nThis routes ledger work.\nRoute generation: 3\n"
        "Supersedes route: coordination/mailbox/sent/2026-07-12T09-00-00Z-coordinator-to-all-coordination.md\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\nRoute generation: 2\n",
    )
    result = ledger_start_guard.find_latest_ledger_route(tmp_path)
    assert result is not None
    assert result.name == "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md"


def test_find_latest_falls_back_to_reverse_lex_without_generation(tmp_path):
    import ledger_start_guard

    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-a\nThis routes ledger work.\n",
    )
    newest = _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\n",
    )
    result = ledger_start_guard.find_latest_ledger_route(tmp_path)
    assert result == newest  # identical to prior reverse-lex behavior


def test_check_cli_passes_on_legacy_route_set(tmp_path, capsys):
    _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\n",
    )
    rc = route_lineage.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0 and "legacy" in out.lower()


def test_check_cli_fails_on_forked_lineage(tmp_path, capsys):
    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: a\nRoute generation: 1\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T02-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: b\nRoute generation: 2\n"
        "Supersedes route: 2026-07-12T01-00-00Z-coordinator-to-all-coordination.md\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T03-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: c\nRoute generation: 2\n"
        "Supersedes route: 2026-07-12T01-00-00Z-coordinator-to-all-coordination.md\n",
    )
    rc = route_lineage.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1 and "forked lineage" in out


def test_protocol_doctor_base_commands_include_lineage_check():
    import protocol_doctor

    commands = protocol_doctor.base_commands(python_executable="PY", wave=2)
    assert ["PY", "scripts/route_lineage.py", "--check"] in commands
```

- [ ] **Step 2: Run — expect failures (`AttributeError`/missing `main`).**

- [ ] **Step 3: Append `load_routes` + `main` to `scripts/route_lineage.py`:**

```python
def load_routes(root: Path) -> list[LineageRoute]:
    """Parse lineage for every coordinator-to-all route under root's mailbox."""
    sent = root / "coordination" / "mailbox" / "sent"
    routes: list[LineageRoute] = []
    if not sent.exists():
        return routes
    for path in sorted(sent.glob("*coordinator-to-all*.md")):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        routes.append(LineageRoute(route_id_of(path.name), parse_lineage(body)))
    return routes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate coordinator route lineage consistency (read-only).",
    )
    parser.add_argument("--root", default=str(_REPO_ROOT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="report the authoritative route and fail on lineage inconsistency",
    )
    args = parser.parse_args(argv)

    resolution = resolve_authoritative(load_routes(Path(args.root)))
    if resolution.mode == "legacy":
        print("ROUTE LINEAGE — legacy route set (no generations); resolution by filename.")
        return 0
    if resolution.mode == "empty":
        print("ROUTE LINEAGE — no coordinator routes found.")
        return 0
    print(f"ROUTE LINEAGE — authoritative route: {resolution.winner}")
    for issue in resolution.issues:
        print(f"- {issue}")
    return 1 if resolution.issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rewire `find_latest_ledger_route` in `scripts/ledger_start_guard.py`.** Add `import route_lineage` beside the existing `import target_binding`. Replace the function body's tail so it collects the target-matching candidates first, then resolves lineage-first with the legacy fallback:

```python
def find_latest_ledger_route(
    root: Path, target: target_binding.TargetBinding | None = None
) -> Path | None:
    """Return the authoritative coordinator-to-all route for target work.

    Lineage-first (ADR-015): when candidate routes carry a Route generation
    header, return the lineage tip; otherwise fall back to reverse-lex
    filename order (byte-identical to the prior behavior).
    """
    if target is None:
        target = target_binding.resolve_target()
    sent = root / "coordination" / "mailbox" / "sent"
    if not sent.exists():
        return None
    candidates: list[Path] = []
    for path in sorted(sent.glob("*coordinator-to-all*.md"), reverse=True):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body_lower = body.lower()
        if "Task-board:" in body and (
            any(keyword in body_lower for keyword in target.route_keywords)
            or target.path.as_posix() in body
        ):
            candidates.append(path)
    if not candidates:
        return None
    lineage_routes = [
        route_lineage.LineageRoute(
            route_lineage.route_id_of(path.name),
            route_lineage.parse_lineage(path.read_text(encoding="utf-8", errors="replace")),
        )
        for path in candidates
    ]
    resolution = route_lineage.resolve_authoritative(lineage_routes)
    if resolution.mode == "lineage" and resolution.winner is not None:
        for path in candidates:
            if route_lineage.route_id_of(path.name) == resolution.winner:
                return path
    return candidates[0]  # legacy fallback: reverse-lex newest
```

- [ ] **Step 5: Wire the check into `scripts/protocol_doctor.py` `base_commands`** — add `[python_executable, "scripts/route_lineage.py", "--check"]` immediately after the `target_binding.py --check` entry.

- [ ] **Step 6: Run the full guard + lineage + doctor tests, then the whole suite.** Confirm `tests/unit/test_codex_ledger_bridge.py` passes UNMODIFIED (behavior preservation). Confirm `env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --check` exits 0 on the live repo (all-legacy set) and `scripts/protocol_doctor.py --wave 2` still PASSES. Commit `-- scripts/route_lineage.py scripts/ledger_start_guard.py scripts/protocol_doctor.py tests/unit/test_route_lineage.py`.

---

### Task 5: doc note + final full-gate verification

**Files:** Modify `docs/protocol/route-v1.md` (append a lineage section).

- [ ] **Step 1: Append to `docs/protocol/route-v1.md`:**

```markdown
## Route lineage and currency (ADR-015)

Route currency no longer depends on filename timestamp. A route carries
`Route generation: N` and (unless it is generation 1) `Supersedes route:
<parent>` — both emitted by the route/v1 renderer. The authoritative route is
the lineage TIP: the highest-generation route that no other route supersedes.

- Resolve / audit the current authoritative route:

      env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --check

  It reports the authoritative route id, exits non-zero on a fork (two tips at
  one generation) or a cycle, and prints `legacy route set` when no route
  carries a generation (the resolver then falls back to filename order).

- A new route may supersede the current tip only under compare-and-swap: its
  `Supersedes route:` must name the current tip and its generation must be
  the tip's generation + 1. `route_lineage.check_cas` returns a structured
  `stale_parent` refusal otherwise — the stale writer rebases its delta onto
  the new tip rather than overwriting it.

Legacy routes without a generation header keep the prior reverse-lexicographic
behavior, so the live campaign is unaffected until routes adopt generations.
```

- [ ] **Step 2: Final gates (paste outputs into the commit body — R-EVIDENCE):**

```
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expect: suite green (prior total + ~24 new lineage tests, 0 failures, the 1 pre-existing xfail unchanged); smoke OK; lineage-check exit 0 (legacy live set); doctor PASS; diff-stat shows only this plan's files.

- [ ] **Step 3: Commit** `-- docs/protocol/route-v1.md`. Independent verification (Codex Lane-V) is dispatched by the controller after this task; NO push regardless.

---

## Acceptance criteria (P0.3, from the brief as modified by the audit)

1. Route resolution is deterministic — `resolve_authoritative` is order-independent (test) and filename-independent for generation-bearing routes.
2. Two concurrent route writers cannot both become authoritative — a same-generation fork is detected (structured issue) and `check_cas` rejects the stale writer.
3. A stale route cannot reactivate superseded authority — CAS requires parent == current tip.
4. Concurrent-writer tests produce one winner and one structured stale result (`stale_parent`).
5. Route ancestry is auditable from the parsed parent pointers (`--check`).
6. A transient filesystem observation cannot change authority for generation-bearing routes (lineage tip, not filename sort).
7. **Behavior preservation:** the all-legacy live set resolves exactly as before; pre-existing start-guard tests pass unmodified.

## Rollback

Additive except two behavior-preserving edits (`find_latest_ledger_route` rewire, one `base_commands` line). Revert the slice's commits; the legacy fallback path means no live route/packet migration to unwind.
