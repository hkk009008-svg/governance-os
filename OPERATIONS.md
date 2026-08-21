# OPERATIONS.md - Governance OS

Pipeline is the governance kernel: the shared coordination protocol for two
CLIs, not the private product application. evidence-ledger is the bound
product target for ledger-routed work.

For what the kernel is and where its verified facts live, see
[ARCHITECTURE.md](ARCHITECTURE.md).

## 1. Prerequisites

- A Python environment satisfying `requirements-dev.txt` at `.venv/` in the
  primary checkout. Linked worktrees do not carry their own; `bin/pipeline`
  and `coordination/bin/pipeline-python` both resolve back to the primary one.
- Both peer CLIs on `PATH`. `pipeline preflight` answers whether they are.
- A current Pipeline Git checkout. Run mutating work in a task-specific native
  Git worktree; do not export a persistent `GIT_INDEX_FILE`.
- Do not route ledger work through the user Content checkout.

## 2. Orientation And Completion Checks

```bash
pipeline status            # compact snapshot: git, mailbox, open review, gate
pipeline check             # the completion gate, at the end
```

The snapshot is the startup path. Run focused checks (`pipeline check
coordination`, `pipeline check ceremony`) while working, and the aggregate at
the completion gate for changes that touch governance/runtime topology or an
`ARCHITECTURE.md` invariant.

## 3. Working With The Other CLI

```bash
pipeline preflight                                   # can either peer run
pipeline peer ask codex  --task <id> --prompt-file <f> --dry-run
pipeline peer ask codex  --task <id> --prompt-file <f>
pipeline peer ask claude --task <id> --prompt-file <f>
pipeline peer ask agy    --task <id> --role challenge --prompt-file <f>
pipeline peer receipts --task <id>
```

`--dry-run` prints the exact argv and launches nothing — use it to show a
proposed invocation to whoever must authorize the spend. Read-only is the
default; `--write` widens exactly one flag per side. Full contract:
[docs/protocol/peer.md](docs/protocol/peer.md).

## 4. Coordination Checks

```bash
pipeline check coordination
pipeline status
```

## 5. Ledger-Routed Target Work

When a route points at the registered `evidence-ledger` target, stay in
Pipeline until the guard and active route say which base or worktree is
lawful. Inspect target state with explicit `git -C` commands:

```bash
TARGET_ROOT="$(pipeline target --target evidence-ledger --print-path)"
git -C "$TARGET_ROOT" status --short --branch
git -C "$TARGET_ROOT" log --oneline -5
```

If the route names an isolated worktree, inspect that worktree before the
normal target checkout. The normal checkout may be stale.

### 5.1 Target-Binding Registry (governance.toml, ADR-013)

Which product repos this kernel can govern is declared in `governance.toml`,
not in Python constants. Future work is onboarded by registering a table — no
code edits:

```toml
[targets.my-new-app]
repository = "hkk009008-svg/my-new-app"
path = "~/my-new-app"
route_keywords = ["my-new-app"]
```

Validate the registry with `pipeline target --check`. Select a non-default
target at role startup with `pipeline/ledger_start_guard.py --seat <seat>
--wave <wave> --target my-new-app` or the `GOVERNANCE_TARGET` environment
variable; `GOVERNANCE_TARGET_PATH` overrides the local checkout path. Missing
or unknown bindings fail closed with a corrective message.

## 6. Side-Effect Boundaries

Every external effect requires live exact authority for the executor, target,
effect, and scope. A route or role alone is never sufficient. This includes
merge, cursor consumption, lock mutation, **peer invocation**, paid API spend,
live-data mutation, target checkout refresh, and edits outside the accepted
target scope. Push is deliberately excluded — see `AGENTS.md` item 6 for why
an unenforced claim was dropped instead of restated.

## 7. Troubleshooting

| Symptom | Likely cause | Response |
|---|---|---|
| `pipeline: no Python interpreter available` | The primary checkout has no `.venv` and `python3` is absent | Create the venv per Quick Start; the shim falls back to `python3` only for `--help`. |
| Smoke fails with `SHA-REF BASELINE CHECK` | SHA-reference drift changed from the reviewed historical baseline | Run `pipeline check docs --sha-refs` and update the baseline only after a bounded cleanup or owner decision. |
| `ARCH-FRESHNESS CHECK — FAIL` | `ARCHITECTURE.md` body changed without bumping its provenance stamp | Update *Last verified against base: `<date>` @ `<sha>`* to the state you actually verified against — the base, never the landing commit. |
| `python-growth FAIL` on a branch of several commits | The local default measures `HEAD^`; CI measures the whole PR range | Re-measure the way CI does: `NO_CEREMONY_BASE=$(git merge-base main HEAD) pipeline check ceremony`. |
| `committed manifest ... resolves to 0 paths` | A frozen baseline manifest was deleted or half-renamed | Restore it. Absence is fatal by design; the pre-rename twin makes an old commit readable, never a missing manifest tolerable. |
| Guard reports a route but target checkout looks stale | Active work is in a route worktree or base | Read the route body and inspect the named worktree first. |
| `pipeline peer ask` exits 124 with no result | The peer exceeded `--timeout` | Nothing partial is recorded. Re-run with a longer timeout or a narrower prompt; the receipt says the run produced no result. |
| A peer receipt has `model_reported: null` | That peer's output carried no model field | The receipt says so in `notes`. Do not substitute the requested model — an unconfirmed model is not a confirmed one. |
| `... is not on PATH; a peer that cannot run is not a peer` | The peer CLI is missing | Install it. `pipeline preflight` reports both sides. |
