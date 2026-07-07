# Readiness Follow-Up Report

- Added a focused regression test to assert that `continuation_readiness.render_codex(ROOT)` includes `Ledger CLI Bridge:` and `docs/protocol/codex/ledger-cli-adoption.md`.
- Updated `scripts/continuation_readiness.py` to print the ledger bridge block in readiness output.
- Verification:
  - `/Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q` -> `10 passed`
  - `/Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q` -> `42 passed`
  - `/Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/continuation_readiness.py --skip-ceremony` -> exit 0 and includes the ledger bridge block
  - `/Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py` -> exit 0
