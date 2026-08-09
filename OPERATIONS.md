# OPERATIONS.md - Governance OS

Pipeline is the governance kernel. It runs the shared coordination protocol,
not the private product application. `evidence-ledger` is the bound product
target for ledger-routed work; Pipeline owns the seat mechanics, mailbox
state, capacity board, protocol smoke checks, and cross-provider adoption docs.

For what the kernel is and where its verified facts live, see
[ARCHITECTURE.md](ARCHITECTURE.md). ARCHITECTURE.md records verified
governance-kernel truth.

## 1. Prerequisites

- An activated Python environment satisfying `requirements-dev.txt`.
- A current Pipeline Git checkout.
- Run mutating Codex work in a task-specific native Git worktree. Do not export
  a persistent per-seat `GIT_INDEX_FILE`.
- Do not route ledger work through the user Content checkout.

## 2. Orientation And Completion Checks

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
python scripts/status.py snapshot
```

The compact snapshot is the startup path. Run focused checks while working and
run `python scripts/ci_smoke.py` at the completion gate for changes
that touch governance/runtime topology or an `ARCHITECTURE.md` invariant.

## 3. Live Seat Startup

For governed Codex work, request the concrete role in the compact snapshot:

```bash
python scripts/status.py snapshot director
```

Replace `director` with `director2`, `operator`, `operator2`, or `coordinator`
only when the user or parent prompt names that role. Use
`ledger_start_guard.py --seat <seat> --wave 2` in addition only when the task is
ledger-routed.

## 4. Coordination Checks

```bash
python scripts/check_coordination.py
python scripts/status.py snapshot
```

Use the capacity board only for an active campaign or an explicit diagnostic
question. It is not a startup or route-authority requirement.

## 5. Ledger-Routed Target Work

When a route points at the registered `evidence-ledger` target, stay in Pipeline
until the guard and active route say which base or worktree is lawful. Inspect
target state with explicit `git -C` commands:

```bash
TARGET_ROOT="$(python scripts/target_binding.py --target evidence-ledger --print-path)"
git -C "$TARGET_ROOT" status --short --branch
git -C "$TARGET_ROOT" log --oneline -5
```

If the route names an isolated worktree, inspect that worktree before the normal
target checkout. The normal checkout may be stale.

### 5.1 Target-Binding Registry (governance.toml, ADR-013)

Which product repos this kernel can govern is declared in `governance.toml`,
not in Python constants. `evidence-ledger` is the default target. Future work
is onboarded by registering a new table — no code edits:

```toml
[targets.my-new-app]
repository = "hkk009008-svg/my-new-app"
path = "~/my-new-app"
route_keywords = ["my-new-app"]   # words a coordinator route uses to name this work
```

Validate the registry (also runs inside `protocol_doctor.py`):

```bash
python scripts/target_binding.py --check
```

Select a non-default target at seat startup with
`scripts/ledger_start_guard.py --seat <seat> --wave <wave> --target my-new-app`
or the `GOVERNANCE_TARGET` environment variable; `GOVERNANCE_TARGET_PATH`
overrides the local checkout path of the selected target. Missing or unknown
bindings fail closed with a corrective message. Coordinator routes for the new
target must mention one of its `route_keywords` (or its path) so the start
guard resolves them.

## 6. Side-Effect Boundaries

Every external effect requires live exact authority for the executor, target,
effect, and scope. A route or role alone is never sufficient. This includes
push/force-push, merge, cursor consumption, lock mutation, provider launch,
paid API or pod spend, live-data mutation, target checkout refresh, and edits
outside the accepted target scope. See `AGENTS.md` for the canonical boundary.

## 7. Troubleshooting

| Symptom | Likely cause | Response |
|---|---|---|
| Smoke fails with `SHA-REF BASELINE CHECK` | SHA-reference drift changed from the reviewed historical baseline | Run `scripts/check_doc_claims.py --sha-refs` and update the baseline only after a bounded cleanup or owner decision. |
| Guard reports a route but target checkout looks stale | Active work is in a route worktree or base | Read the route body and inspect the named worktree before using normal target checkout. |
| Mailbox monitor shows unknown receipt | Cursor or ref-bus state cannot prove receipt | Treat delivery as unproved until a seat-specific status or mailbox body proves it. |
| Capacity board reports active packets | A route is open | Work only inside the packet scope and send the next required mailbox artifact. |
