# OPERATIONS.md - Governance OS

Pipeline is the governance kernel. It runs the shared coordination protocol,
not the private product application. `evidence-ledger` is the bound product
target for ledger-routed work; Pipeline owns the seat mechanics, mailbox
state, capacity board, protocol smoke checks, and cross-provider adoption docs.

For what the kernel is and where its verified facts live, see
[ARCHITECTURE.md](ARCHITECTURE.md). ARCHITECTURE.md records verified
governance-kernel truth.

## 1. Prerequisites

- Python virtual environment at `.venv/`.
- Git checkout at `/Users/hyungkoookkim/Pipeline`.
- Use `env -u GIT_INDEX_FILE` for normal git, pytest, and Python commands.
- Do not route ledger work through `/Users/hyungkoookkim/Content`.

## 2. Basic Health Checks

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git status --short --branch
```

Expected:
- `scripts/ci_smoke.py` exits `0`.
- The reviewed historical commit-SHA baseline stays quiet in smoke; changed
  SHA-ref drift hard-fails.
- `git status --short --branch` shows only changes you intentionally made.

## 3. Live Seat Startup

For a live Codex seat, run the Pipeline guard first, then seat status:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
```

Replace `director` with `director2`, `operator`, `operator2`, or `coordinator`
only when the user or parent prompt names that seat. Read the active route body
reported by the guard before entering any target repo.

## 4. Coordination Checks

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/mailbox_monitor.py --once
```

`mailbox_monitor.py` is read-only. Unknown coordinator broadcast receipt means
receipt is unproved, not delivered.

## 5. Ledger-Routed Target Work

When a route points at `/Users/hyungkoookkim/evidence-ledger`, stay in Pipeline
until the guard and active route say which base or worktree is lawful. Inspect
target state with explicit `git -C` commands:

```bash
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short --branch
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log --oneline -5
```

If the route names an isolated worktree, inspect that worktree before the normal
target checkout. The normal checkout may be stale.

### 5.1 Target-Binding Registry (governance.toml, ADR-013)

Which product repos this kernel can govern is declared in `governance.toml`,
not in Python constants. `evidence-ledger` is the default target; registered
additional targets include `foulplay` (`~/FoulPlay`, Cursor bridge at
`docs/protocol/cursor/foulplay-adoption.md`). A future work is onboarded by
registering a new table — no code edits:

```toml
[targets.my-new-app]
repository = "hkk009008-svg/my-new-app"
path = "~/my-new-app"
route_keywords = ["my-new-app"]   # words a coordinator route uses to name this work
```

Validate the registry (also runs inside `protocol_doctor.py`):

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
```

Select a non-default target at seat startup with
`scripts/ledger_start_guard.py --seat <seat> --wave <wave> --target my-new-app`
or the `GOVERNANCE_TARGET` environment variable; `GOVERNANCE_TARGET_PATH`
overrides the local checkout path of the selected target. Missing or unknown
bindings fail closed with a corrective message. Coordinator routes for the new
target must mention one of its `route_keywords` (or its path) so the start
guard resolves them.

## 6. Side-Effect Boundaries

The following require explicit user authorization or a valid routed executor:
- push or force-push;
- cursor consumption;
- lock action;
- paid API spend;
- pod spend;
- target checkout refresh;
- product-target edits outside the active route.

## 7. Troubleshooting

| Symptom | Likely cause | Response |
|---|---|---|
| Smoke fails with `SHA-REF BASELINE CHECK` | SHA-reference drift changed from the reviewed historical baseline | Run `scripts/check_doc_claims.py --sha-refs` and update the baseline only after a bounded cleanup or owner decision. |
| Guard reports a route but target checkout looks stale | Active work is in a route worktree or base | Read the route body and inspect the named worktree before using normal target checkout. |
| Mailbox monitor shows unknown receipt | Cursor or ref-bus state cannot prove receipt | Treat delivery as unproved until a seat-specific status or mailbox body proves it. |
| Capacity board reports active packets | A route is open | Work only inside the packet scope and send the next required mailbox artifact. |
