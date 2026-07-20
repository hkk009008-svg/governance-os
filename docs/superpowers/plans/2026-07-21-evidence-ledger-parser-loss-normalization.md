# Evidence-Ledger Parser Loss and Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the five reproduced parser loss/normalization defects and preserve distinct PPL placements that share a broadcast slot.

**Architecture:** Keep parsing pure and fixture-driven. Internal rows convert impossible dates into existing typed drop anomalies. Agency parsing uses explicit HHMM validation, exact `Decimal` cost semantics, evidence-aware blank-row classification, and a complete placement identity for collapse. Invalid inputs stay unlinked and loud; no parser invents a valid coordinate.

**Tech Stack:** Python 3.11+, pytest, openpyxl, `datetime`, standard-library `decimal`, existing import models and loaders.

## Global Constraints

- Bind this packet to the locally integrated, Operator2-accepted Packet 1 head. Before Task 1, set the task-specific shell variable `EVIDENCE_LEDGER_PACKET_PARENT_SHA` to the route's exact 40-hex parent, assert `git rev-parse HEAD` equals it, and keep that shell active for the packet.
- Use a dedicated evidence-ledger worktree. Never run concurrent implementers against `import/parse_agency_schedule.py` or its tests.
- Preserve `.vscode/` and all unrelated target WIP.
- Use generated synthetic workbooks only. Do not read `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx` or any private workbook.
- Do not add a dependency; `decimal.Decimal` is in the standard library.
- Do not change database schemas, source-reference format, alias policy, checklist write policy, CI topology, or dormant iOS files in this packet.
- Do not start services, connect to a managed database, merge, or push.

---

## Task 1: Turn impossible internal dates into loud drops

**Files:**

- Modify: `import/tests/test_parse_workbook.py`
- Modify: `import/parse_workbook.py`

- [ ] Add a synthetic workbook test that uses the existing `make_fixture.HEADER`, writes one otherwise-valid row with `방송일자="02/30(월)"`, adds the required `PPL 지급 요약` sheet, and asserts:

```python
out = parse(path, year=2026)
assert out.rows == []
assert out.rows_scanned == 1
assert out.rows_dropped == 1
assert out.dropped_by_reason == {"unparseable_date": 1}
assert [(a.kind, a.raw_date) for a in out.anomalies] == [
    ("unparseable_date", "02/30(월)"),
]
```

- [ ] Run only that new test before implementation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_workbook.py \
  -k impossible_calendar_date -q
```

Expected: FAIL with uncaught `ValueError: day is out of range for month`.

- [ ] In `parse_workbook.parse`, wrap only the `datetime.date(year, month, day)` construction. On `ValueError`, call the existing `_drop` helper with kind `unparseable_date`, include the raw value and exception text in `detail`, and `continue`. Do not broaden `except` beyond `ValueError`.

- [ ] Re-run the focused test and the complete internal parser file:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_workbook.py -q
```

Expected: all tests in `test_parse_workbook.py` pass; the impossible row is counted exactly once and produces exactly one anomaly.

- [ ] Commit this independently understandable fix:

```bash
env -u GIT_INDEX_FILE git add import/parse_workbook.py import/tests/test_parse_workbook.py
env -u GIT_INDEX_FILE git commit -m "fix(import): report impossible workbook dates"
```

## Task 2: Parse agency times as validated HHMM

**Files:**

- Modify: `import/tests/test_parse_agency_schedule.py`
- Modify: `import/parse_agency_schedule.py`

- [ ] Add direct unit cases for `_normalize_time` and `_extract_channel`:

```python
@pytest.mark.parametrize(
    ("raw", "expected", "bump"),
    [("GS 930", "09:30", False), ("GS 0930", "09:30", False),
     ("NS 2500", "01:00", True), ("CJ 4759", "23:59", True)],
)
def test_time_tokens_are_hhmm(raw, expected, bump):
    assert _normalize_time(raw) == (expected, bump, None)

@pytest.mark.parametrize("raw", ["GS 2360", "GS 2460x0930", "GS 4800", "GS 9900"])
def test_invalid_time_tokens_are_loud_and_unlinked(raw):
    channel, time_value, kind, bump = _extract_channel(raw)
    assert channel == "GS"
    assert time_value is None
    assert kind == "invalid_time_token"
    assert bump is False
```

For the `2460x0930` case, assert the parser validates the first matched token and does not search for a later rescue token.

- [ ] Run these cases before implementation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_agency_schedule.py \
  -k 'time_tokens_are_hhmm or invalid_time_tokens_are_loud' -q
```

Expected: FAIL; `930` currently becomes `906:00`, and invalid values can become fabricated times.

- [ ] Change the interface to:

```python
def _normalize_time(raw) -> tuple[str | None, bool, str | None]:
    """Return (HH:MM, next_day_bump, anomaly_kind)."""
```

Interpret three digits by left-padding to four (`930` -> `0930`), then split the last two digits as minutes. Accept hours `00..47` and minutes `00..59`; hours `24..47` subtract 24 and set one next-day bump. Return `(None, False, "invalid_time_token")` for any matched token outside those ranges. Preserve the existing raw-string fallback when no 3-4 digit token exists so the loader's existing bad-time warning still works.

- [ ] Update `_extract_channel` to propagate `invalid_time_token` without overwriting the parsed channel. Update its docstring and all tuple unpacking.

- [ ] Add one generated-workbook integration assertion showing the anomaly carries the exact row `source_ref` and the row's `start_time_raw` is `None`.

- [ ] Run the complete agency parser suite:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_agency_schedule.py -q
```

Expected: all tests pass; `2500` remains an overnight `01:00`, `930` is `09:30`, and invalid tokens are loud and unlinked.

## Task 3: Make blank coordinates quiet only for genuinely empty rows

**Files:**

- Modify: `import/tests/test_parse_agency_schedule.py`
- Modify: `import/parse_agency_schedule.py`

- [ ] Add a generated sheet containing these two post-header rows:

  - a completely blank row;
  - a row with blank `날짜` and blank `홈쇼핑 방송`, but synthetic `PPL 명`, `비용`, and `아이템` values.

Assert the blank row produces neither a row nor anomaly. Assert the evidence-bearing row produces exactly one anomaly:

```python
assert anomaly.kind == "missing_slot_coordinates"
assert anomaly.source_ref.endswith("!r3")
assert "cost=" in anomaly.detail
assert "ppl=" in anomaly.detail
assert not any(r.source_ref == anomaly.source_ref for r in out.all_rows)
assert not any(r.source_ref == anomaly.source_ref for r in out.collapsed)
```

- [ ] Run the new test before implementation. Expected: FAIL because the evidence-bearing row is silently skipped by the current both-blank guard.

- [ ] In `_extract_rows`, compute `row_no` and `source_ref` before the both-blank decision. Define evidence as any nonblank value among `item`, `ppl`, `company`, `issue`, `cost`, and `agency`. When both coordinates are blank:

  - emit `missing_slot_coordinates` with a stable `repr` of the populated evidence fields and continue; or
  - continue quietly only when every evidence field is blank.

Treat numeric zero as evidence; do not use a truthiness test that discards `0`.

- [ ] Re-run the focused test and confirm both positive and negative contracts pass.

## Task 4: Preserve exact fractional 만원 costs through KRW conversion

**Files:**

- Modify: `import/tests/test_parse_agency_schedule.py`
- Modify: `import/tests/test_load_agency_unit.py`
- Modify: `import/parse_agency_schedule.py`
- Modify: `import/load_agency.py`

- [ ] Add parser tests for numeric `437.5`, string `"437.5만원"`, and a nonnumeric string. Expected contracts:

```python
assert _to_cost(437.5) == (Decimal("437.5"), None)
assert _to_cost("437.5만원") == (Decimal("437.5"), None)
assert _to_cost("확인 필요") == (None, "non_numeric_cost")
assert _to_cost("NaN") == (None, "non_finite_cost")
```

- [ ] Add loader-unit tests for a pure `_cost_to_krw` helper:

```python
assert _cost_to_krw(Decimal("437.5")) == 4_375_000
assert _cost_to_krw(Decimal("0.0001")) == 1
with pytest.raises(ValueError, match="whole KRW"):
    _cost_to_krw(Decimal("0.00015"))
```

- [ ] Run these tests before implementation. Expected: FAIL because `_to_cost(437.5)` truncates to `437` and `_cost_to_krw` does not exist.

- [ ] Import `Decimal` and `InvalidOperation` from `decimal`. Change `AgencyPlacementRow.cost` to `Decimal | None` and change `_to_cost` to return `(value, anomaly_kind)`. Parse numeric cells through `Decimal(str(raw))`; for strings, remove commas, surrounding whitespace, and one terminal `만원` suffix before constructing `Decimal`. Do not construct `Decimal` directly from a float. Require `value.is_finite()` and emit `non_finite_cost` for `NaN` or infinity before any comparison or conversion.

- [ ] Reject sub-KRW precision in `_to_cost` by checking whether `value * Decimal(10_000)` equals its integral value. Return `(None, "sub_krw_cost")` so `_extract_rows` emits a typed anomaly rather than allowing a later rounded amount.

- [ ] Add this loader helper and use it instead of `int(r.cost) * MANWON`:

```python
def _cost_to_krw(cost: Decimal) -> int:
    krw = cost * Decimal(MANWON)
    if krw != krw.to_integral_value():
        raise ValueError(f"cost does not represent whole KRW: {cost}")
    return int(krw)
```

This is a defense-in-depth assertion; normal parsed rows already pass the representability check.

- [ ] Run both affected test files:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_agency_schedule.py \
  import/tests/test_load_agency_unit.py -q
```

Expected: all selected tests pass with exact integer KRW assertions; no binary-float rounding assertion is used.

## Task 5: Collapse only identical placements, not everything on one slot

**Files:**

- Modify: `import/tests/test_parse_agency_schedule.py`
- Modify: `import/parse_agency_schedule.py`

- [ ] Replace `test_collapsed_has_exactly_one_row_per_distinct_slot_key_within_family` with a complete-identity invariant. Add two explicit regression tests:

  1. two rows with the same family/date/channel/time/product but different PPL shows or agencies both survive;
  2. two snapshots of the same complete identity with changed cost/issue collapse to the newer mention.

Use direct `AgencyPlacementRow` instances and an explicit `sheet_rank` so the tests do not depend on worksheet iteration.

- [ ] Run the two tests before implementation. Expected: the distinct-placement test FAILS because `_collapse` currently keys only family plus slot.

- [ ] Replace `_slot_key` with a named `_placement_identity` that returns exactly:

```python
(
    row.family,
    row.air_date,
    (row.channel_raw or "").upper(),
    row.start_time_raw,
    row.item_raw or row.family,
    row.ppl_show_raw,
    row.ppl_qualifier,
    row.agency_raw,
)
```

Do not add `cost`, `issue_raw`, `note_raw`, `source_ref`, or snapshot date to the identity. Snapshot date and deterministic sheet rank remain ordering fields that select the latest same-identity mention.

- [ ] Update `_collapse`'s docstring, variable names, and tests so no prose still claims one row per slot key. Preserve rows with `air_date is None` as anomaly-only/non-collapsible.

- [ ] Run the complete parser and loader-unit suites:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_workbook.py \
  import/tests/test_parse_agency_schedule.py \
  import/tests/test_load_agency_unit.py -q
```

Expected: all selected tests pass; the two owner-rule tests prove distinct placements survive and true same-identity updates supersede deterministically.

- [ ] Commit Tasks 2-5 as one cohesive agency-parser change:

```bash
env -u GIT_INDEX_FILE git add \
  import/parse_agency_schedule.py import/load_agency.py \
  import/tests/test_parse_agency_schedule.py import/tests/test_load_agency_unit.py
env -u GIT_INDEX_FILE git commit -m "fix(import): preserve agency placement evidence"
```

## Task 6: Verify and hand off the immutable packet

**Files:**

- Verify only; no new product files.

- [ ] Run the entire existing hermetic import profile:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest \
  import/tests/test_parse_workbook.py \
  import/tests/test_parse_agency_schedule.py \
  import/tests/test_propose_merges.py \
  import/tests/test_load_agency_unit.py \
  import/tests/test_profile_agency_workbook.py \
  --tb=short -q
```

Expected: exit 0 with no skipped, xfailed, or failed tests introduced by this packet.

- [ ] Run repository smoke and range checks:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git diff --name-only "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: smoke ends in `OK`; diff check is silent; changed paths are the six files named in this plan; the worktree is clean.

- [ ] Publish an immutable verify-request assigning non-author Operator2 and naming separate finding references for impossible dates, HHMM parsing, invalid-token loudness, blank-coordinate evidence, fractional cost, distinct-placement survival, and same-identity supersession.

- [ ] Stop without merge or push. Packet 3 must bind to the accepted and separately integrated head, not merely this implementation branch.
