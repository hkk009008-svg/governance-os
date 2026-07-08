# Final review fix report

## 1) All-seat wave visibility

RED evidence:

`env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_seat_status_all.py -q`

Failed exactly where the regression lived:

```text
assert out.count("── wave gate — wave 2 ") == 1
E       AssertionError: assert 0 == 1
```

GREEN evidence:

- Added `wave_gate(root, args.wave)` to the `--all` path in `.agents/skills/four-seat-protocol/scripts/seat_status.py`.
- Extended `tests/unit/test_seat_status_all.py` to assert the wave-gate section renders once, alongside the capacity board.
- Re-ran the test command and it passed: `2 passed in 0.03s`.

Observed output after the fix:

```text
── wave gate — wave 2 ────────────────────────────────────────
Wave 2 gate: MET  counts={}
→ exit 0 (MET)

── capacity board — wave 2 ───────────────────────────────────
```

## 2) Mailbox monitor row spacing

Before:

`scripts/mailbox_monitor.py` rendered seat rows with `f"{seat:<11}unread=..."`, which collapsed the coordinator row into `coordinatorunread=0`.

After:

`f"{seat:<14}unread=..."` now leaves a readable gap. The focused assertion in `tests/unit/test_governance_hardening.py` now expects:

```text
coordinator   unread=
```

Observed output after the fix:

```text
coordinator   unread=0 latest=- cursor=0 source=ref-bus receipt=unknown heartbeat=n/a age=n/a
```

## Verification

- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_seat_status_all.py -q`
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_governance_hardening.py -q`
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py --all --wave 2 --commits 1`
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/mailbox_monitor.py --once --wave 2`
- `env -u GIT_INDEX_FILE git diff --check -- .agents/skills/four-seat-protocol/scripts/seat_status.py tests/unit/test_seat_status_all.py scripts/mailbox_monitor.py tests/unit/test_governance_hardening.py`

