# Pipeline Route Correction and Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish one superseding coordinator route that removes the false G7 classification and then fast-forward Pipeline `main` to `origin/main` exactly once.

**Architecture:** Keep the validator unchanged. A fixed-writer coordinator event preserves the accepted evidence-ledger outcome, separates negative external-effect prose onto its own physical lines, and carries one structural token electing the coordinator to publish Pipeline `main`. Publication occurs only after route, coordination, doctor, smoke, ancestry, and live-remote checks pass.

**Tech Stack:** Markdown coordination events, `coordination/bin/send-event`, Python protocol validators, Git.

## Global Constraints

- Modify no validator source or tests.
- Do not edit, merge, push, or otherwise mutate evidence-ledger.
- Preserve accepted evidence-ledger head `41d9f1d846d6e0928b520573094ae59846114df5` and the Gate B/C/D hold.
- Use the fixed mailbox writer; never edit the committed invalid route in place.
- Use one normal push to Pipeline `origin/main`; never force-push.
- Stop on remote drift, dirty scope, failed validation, failed smoke, or ambiguous push outcome.
- Do not consume cursors, claim locks, run providers, spend, reset, rebase, amend, or clean unrelated state.

---

## File Map

- Create dynamically: the fixed writer's returned `coordination/mailbox/sent/*-coordinator-to-all-coordination.md` path — the only coordination correction and the active superseding route.
- Create temporarily: `/private/tmp/pipeline-route-correction-body.md` — fixed-writer body input; never committed.
- Preserve: `coordination/mailbox/sent/2026-07-19T12-03-04Z-coordinator-to-all-coordination.md` — immutable invalid route retained as evidence.
- Preserve: `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1` — no writes or Git effects.

### Task 1: Publish and validate the superseding coordinator route

**Files:**
- Create: the fixed writer's returned `coordination/mailbox/sent/*-coordinator-to-all-coordination.md` path
- Create temporarily: `/private/tmp/pipeline-route-correction-body.md`
- Reference: `docs/superpowers/specs/2026-07-20-pipeline-route-correction-publication-design.md`
- Reference: `docs/superpowers/plans/2026-07-20-pipeline-route-correction-publication.md`

**Interfaces:**
- Consumes: active route `coordination/mailbox/sent/2026-07-19T12-03-04Z-coordinator-to-all-coordination.md@eb732bd8e2e91631143224339baeaf7b714a8145`, approved design commit `e501ca200c84ab1c283bd8311e0b74a03bc4ac10`, live remote base `cd076c50780e62dadf77ffd04cda34f60a8c56a3`, and the user's Pipeline push authorization.
- Produces: one committed route whose structural token is `(effect=git push, executor=coordinator, target=origin/main, scope=Pipeline design+plan+route publication)`.

- [ ] **Step 1: Refresh the governed state**

Run:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git ls-remote origin refs/heads/main
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 rev-parse HEAD
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 status --short --branch
```

Expected: Pipeline is clean on `main`; live `origin/main` is `cd076c50780e62dadf77ffd04cda34f60a8c56a3`; evidence-ledger is clean at `41d9f1d846d6e0928b520573094ae59846114df5`; coordinator unread count is zero.

- [ ] **Step 2: Create the exact fixed-writer body**

Use `apply_patch` to create `/private/tmp/pipeline-route-correction-body.md` with this exact body:

```markdown
Event type: coordination
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: coordinator-product-first-route-correction-publication
Status: PRODUCT-FIRST BACKEND ACCEPTED; WINDOWS TASK 5B HELD; PIPELINE PUBLICATION AUTHORIZED
Supersedes active route: coordination/mailbox/sent/2026-07-19T12-03-04Z-coordinator-to-all-coordination.md@eb732bd8e2e91631143224339baeaf7b714a8145
Design ref: docs/superpowers/specs/2026-07-20-pipeline-route-correction-publication-design.md@e501ca200c84ab1c283bd8311e0b74a03bc4ac10
Plan path: docs/superpowers/plans/2026-07-20-pipeline-route-correction-publication.md
Authorization source: user-task:pipeline-push-and-route-correction-2026-07-20
Pipeline remote base: cd076c50780e62dadf77ffd04cda34f60a8c56a3
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Accepted target head: 41d9f1d846d6e0928b520573094ae59846114df5
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Route-text correction

The superseded route combined positive acceptance prose and a negative push boundary on one physical line. The line-oriented G7 classifier therefore treated the word `push` as an untokened directive. This route preserves the outcome and places negative external-effect boundaries on their own physical lines. Validator source and tests remain unchanged.

## Preserved outcome

The product-first Selling Package backend remains accepted through Task 3 at target head `41d9f1d846d6e0928b520573094ae59846114df5`. Task 5A's strict Windows foundation and adapters remain accepted.

The evidence-ledger target remains local and unchanged.

No evidence-ledger merge, push, deployment, managed-service mutation, real-data use, booking, spend, policy activation, owner ruling, Task 4 transition, or Task 5B mutation is authorized by this event.

Gate B/C still requires matching decisions from two distinct current active owners for the complete formula and risk/action policy packets. Gate D still requires matching `manual_only` or `manual_csv_xlsx` decisions plus an effective capability reread. Task 5B remains held until the required Task-3B policy state and terminal Gate-D branch are independently evidenced.

## Side-Effect Executor Token

- effect: git push
- executor: coordinator
- target: origin/main
- scope: Pipeline main publication from cd076c50780e62dadf77ffd04cda34f60a8c56a3 through the committed design, plan, and this superseding route only

After all local gates pass and live `origin/main` still equals `cd076c50780e62dadf77ffd04cda34f60a8c56a3`, coordinator may push `origin/main` exactly once. Stop on dirty scope, remote drift, failed ancestry, failed validation, failed smoke, denial, timeout, or ambiguous outcome. No force-push, retry-before-live-reconciliation, merge, reset, rebase, amend, cleanup, cursor consumption, lock action, provider action, or spend is authorized.
```

Expected: the temporary body contains the exact immutable design ref and no unresolved template tokens.

- [ ] **Step 3: Publish through the fixed writer**

Run:

```bash
coordination/bin/send-event coordinator all coordination "correct G7 boundary and authorize one Pipeline publication" < /private/tmp/pipeline-route-correction-body.md
```

Expected: `created coordination/mailbox/sent/` followed by one timestamped `-coordinator-to-all-coordination.md` path and the staged commit instruction, or the documented unstaged form with the same single final path. Stop on writer or lock failure; do not bypass the writer.

- [ ] **Step 4: Resolve and inspect the generated route path**

Run:

```bash
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: exactly one staged added path ending in `-coordinator-to-all-coordination.md`; no other worktree changes. Record that exact path as the task-specific `ROUTE_PATH`. Read the complete generated file and confirm that the design ref is a full commit, the negative evidence-ledger boundary begins its own physical line, and the token names only coordinator plus `origin/main`.

- [ ] **Step 5: Validate the candidate route before commit**

Run these commands after setting the task-specific variable to the exact generated path from Step 4:

```bash
ROUTE_PATH=$(env -u GIT_INDEX_FILE git diff --cached --name-only -- 'coordination/mailbox/sent/*-coordinator-to-all-coordination.md')
test -n "$ROUTE_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route "$ROUTE_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE git diff --cached --check
```

Expected: `ROUTE_PATH` resolves to the single staged fixed-writer path, route validation reports `route valid: true`, coordination reports `OK`, and diff-check emits no output.

- [ ] **Step 6: Commit only the route**

Run in the same shell session with the validated `ROUTE_PATH`:

```bash
env -u GIT_INDEX_FILE git commit "$ROUTE_PATH" -m "coord(pipeline): correct route and bind publication"
```

Expected: one commit containing only the generated route.

- [ ] **Step 7: Run the full local publication gate**

Run in the same shell session with the committed `ROUTE_PATH`:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route "$ROUTE_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --route "$ROUTE_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check eb732bd8e2e91631143224339baeaf7b714a8145..HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: route valid, doctor PASS, coordination `OK`, smoke `OK`, no diff-check output, and a clean Pipeline worktree.

### Task 2: Publish Pipeline main and prove the remote result

**Files:**
- Modify remotely: `origin/main` in `https://github.com/hkk009008-svg/governance-os.git`
- Preserve: all evidence-ledger refs and files

**Interfaces:**
- Consumes: the committed valid route and its one coordinator executor token.
- Produces: live Pipeline `origin/main` equal to the final local Pipeline `HEAD`.

- [ ] **Step 1: Revalidate live remote and ancestry immediately before push**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git ls-remote origin refs/heads/main
env -u GIT_INDEX_FILE git merge-base --is-ancestor cd076c50780e62dadf77ffd04cda34f60a8c56a3 HEAD
env -u GIT_INDEX_FILE git rev-list --left-right --count HEAD...origin/main
```

Expected: clean local worktree; live remote exactly `cd076c50780e62dadf77ffd04cda34f60a8c56a3`; ancestry exits zero; local is ahead and zero behind. Stop if any expectation differs.

- [ ] **Step 2: Push once**

Run:

```bash
env -u GIT_INDEX_FILE git push origin main
```

Expected: a normal fast-forward update of `refs/heads/main`. Do not retry an error or ambiguous result before Step 3 establishes live state.

- [ ] **Step 3: Verify live publication and target preservation**

Run:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git ls-remote origin refs/heads/main
env -u GIT_INDEX_FILE git rev-list --left-right --count HEAD...origin/main
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 rev-parse HEAD
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 status --short --branch
```

Expected: local `HEAD` and live `origin/main` are identical; divergence is `0 0`; Pipeline is clean; evidence-ledger remains clean at `41d9f1d846d6e0928b520573094ae59846114df5`.
