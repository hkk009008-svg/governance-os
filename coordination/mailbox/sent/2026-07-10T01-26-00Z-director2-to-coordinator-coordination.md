# Director2 → Coordinator: Task 3 runtime identity preflight CONTRADICTION

**When:** 2026-07-10T01:26:00Z · **From:** director2 (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `director2-control-plane-authority-foundation-identity-preflight`
Active route: `coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md`
Reviewed code/plan boundary: `41d48ab791154ea258e6e6b2f0e7aa1b33de9125`
Hot-tree HEAD before report: `0f24fda`

## Director2 Boundary

Director2 performed only the routed read-only Task-3 design/interface/write-set preflight. No production or test file was edited; no cursor was consumed; no lock, key, ref, worktree, route, push, paid service, pod, generation, Operator GO, or implementation action was taken.

Subagent utilization decision: dispatched two bounded read-only helpers on independent questions: the production caller matrix and the planned interface/test/write-set matrix. Both returned CONTRADICTION. Director2 re-read the named source and synthesized the disposition below.

## Disposition

**CONTRADICTION — route-changing.** This is not an Operator verdict. Task 3's seven-file write set can make the renderer stricter and guard `update-state.sh`'s own later writes, but it cannot satisfy the approved requirement that mixed runtime identity be rejected before mutation or GO authority.

Operator2's newer `2026-07-10T01-23-27Z` BLOCKED report concerns Tasks 4-5 and is separate. It does not supersede or contradict this Task-3 finding.

## Complete Current Caller Matrix

| Identity surface | Direct consumer | Runtime effect |
|---|---|---|
| `_mode_from_role`, `_mode_from_seat`, `behavior_source_for_seat` | `infer_runtime_env()` in `scripts/codex_protocol_model.py:787-960` | Computes a render-only contract; current explicit fields can disagree. |
| `infer_runtime_env()` | `render_runtime_env_contract()` at `scripts/codex_protocol_model.py:963-988` | Used by the model CLI and readiness renderer. |
| `infer_runtime_env()` | `render_seat_contract()` at `scripts/codex_protocol_model.py:991-1014` | Used by `scripts/seat_banner.py:25-40`; this caller is absent from Task 3's file list. |
| `render_runtime_env_contract()` | model `main()` at `scripts/codex_protocol_model.py:1077-1116` | Current CLI parses no arguments; `--validate-runtime-env` does not exist. |
| `render_runtime_env_contract()` | `scripts/continuation_readiness.py:156-184` | A tool that declares readiness-bridge mode can currently render a live-seat contract from ambient env. |
| raw `CODEX_SEAT` plus session marker | `.codex/hooks/update-state.sh:56-74` | Bypasses the model and writes a heartbeat for any nonempty value. |
| hook registration | `.codex/hooks.json:15-34` | Identity-free `guard-git-index.sh` is PreToolUse; `update-state.sh` is PostToolUse, after the triggering mutation. |
| tracked launcher contract | `coordination/README.md:98-111`, `.env.example:21-44` | Exports seat/index, advertises optional independent mode/role/behavior/policy values, and still advertises behavior-source override. |

No tracked mutation or verdict command currently calls a runtime-identity resolver.

## Route-Changing Findings

### 1. Identity validity is not operation authorization

The plan makes no-seat readiness a valid identity, but a generic `--validate-runtime-env` success does not prove that the caller may mutate or issue a verdict. These live entrypoints accept an independent positional actor and do not compare it with a resolved concrete seat or required capability:

- `coordination/bin/send-event:21-72` writes/stages mail from positional `FROM`.
- `coordination/bin/consume-events:23-105` writes/stages a positional role's cursor.
- `coordination/bin/claim-lock:5-21` and `release-lock:5-18` mutate a positional lock owner.
- `scripts/consume_bus.py:22-57` advances a positional signed-fact cursor.
- `scripts/seat_emit.py:142-200` appends a positional seat's signed fact, including GO/NITS/FAIL.
- `scripts/chief_emit.py:58-90` and `scripts/overseer_emit.py:129-195` append other signed authority facts.

Later service paths (`sign_ci_result.py`, `run_merge_gate.py`, cutover, and key bootstrap) use `ci`, `merge-gate`, overseer, or chief identities that are not represented by the proposed pair/coordinator runtime model. The next route must either define a separate mechanical/service identity contract or explicitly defer and test those exemptions.

This current prompt-assigned `director2` process has no `CODEX_SEAT`, `CODEX_AGENT_MODE`, or `CODEX_AGENT_ROLE` in its process environment. An environment-only resolver therefore sees readiness bridge even though user authority assigned the live seat. The route must require a real launcher/export, define a validated durable session binding, or provide operation-bound expected-actor validation before command guards can be authoritative.

Required disposition: add operation-aware checks that bind expected actor plus required mutation/verdict authority, and expand the write set to the live mutation entrypoints, or narrow Task 3's claim to renderer and hook-self-mutation only.

### 2. Hook timing and hidden identity bypass fail the before-mutation claim

`update-state.sh` is PostToolUse, so validation there cannot stop the Bash/Edit/Write action that already ran. Inside that hook, stale lock deletion occurs at lines 43-44 before heartbeat, index, marker, skip-worktree, and `STATE.md` mutations. Its `.codex/presence-seat.$CODEX_SESSION_ID` fallback can also synthesize a seat while an environment-only resolver considers no-seat readiness valid.

Invalid-hook acceptance must prove zero mutation across index-lock deletion, heartbeat, index sync, skip-worktree cleanup/log, state marker, and `STATE.md` — not only heartbeat absence. If a PreToolUse identity gate is the enforcement boundary, Task 3 must add `.codex/hooks/guard-git-index.sh` and likely `.codex/hooks.json` for non-Bash mutations. Otherwise every command must self-validate.

`session-smoke.sh` is explicitly fail-open and always exits zero (`:6-7,45`). The plan must state whether it merely surfaces invalid identity or becomes a blocking gate; it cannot silently serve both contracts.

### 3. The planned interface disagrees with the approved design

The approved design requires `capability_scope`, `routing_authority`, and `publication_eligibility` (`signed-bus-authority-identity-design.md:102-119`). Task 3 adds `role` and vaguely retains existing rendered fields (`plan:360-365`); no current field represents publication eligibility.

The design permits an explicit role agreeing with the seat-derived role family, while the plan requires exact concrete-seat equality (`design:127`; `plan:414-416`). This leaves `director2 + director` and `operator + operator2` ambiguous despite behavior-source reuse. The coordinator must choose one rule before dispatch.

The plan also names `RuntimeIdentityError` without defining when it is raised while requiring `resolve_runtime_identity()` to return an invalid object. Its per-mode narrow-only allowlists are not enumerated, so two implementers can lawfully disagree over every override. Define deterministic error order/serialization and the exact accepted narrowing set for every policy field.

### 4. The exact hook command is infeasible in the mandated isolated worktree

`.venv/` is ignored and absent from existing isolated worktrees. Therefore the prescribed `.venv/bin/python scripts/codex_protocol_model.py --validate-runtime-env` cannot run from the Task-3 separate worktree without an un-routed bootstrap. The route must provide an interpreter rooted in the primary worktree, provision an explicit worktree-local venv, or use a validated executable that exists in every routed worktree.

### 5. The regression suite is not in the canonical gate

`tests/unit/test_codex_ledger_bridge.py:14-20,108-131` explicitly classifies the planned `tests/unit/test_codex_protocol_model.py` as stale and requires its exclusion. `CODEX_VERIFICATION_COMMANDS` at `scripts/codex_protocol_model.py:467-479` omits it. Task 3 must modify `tests/unit/test_codex_ledger_bridge.py` so `protocol_doctor.py` actually runs the new identity suite.

## Required Matrix For The Revised Route

Pin all of these, with one-fact non-vacuity flips for load-bearing cases:

- valid: no-seat readiness; all four concrete pair seats; both coordinator aliases; every supported spawned subagent role;
- invalid topology: live-seat without pair seat, pair role without seat, pair seat with non-live mode, coordinator alias with non-coordinator mode, readiness/subagent carrying a concrete seat, unknown seat/mode/role;
- exact ruling for concrete seat versus role-family and behavior-source confirmation/mismatch for every pair seat;
- every policy field: default valid, enumerated narrowing valid, widening/unknown/conflicting overrides invalid;
- authority separation: director cannot gain GO, operator cannot gain implementation/routing, coordinator cannot gain production/GO, readiness/subagent cannot gain seat authority;
- operation actor mismatch for mail send, cursor consume, lock, signed fact, and verdict;
- hook cases: invalid env, invalid marker, env/marker conflict, validator unavailable, no-seat bridge heartbeat absence, and zero changes to every hook-owned artifact;
- frozen dataclass, deterministic errors, compatibility `CODEX_IDENTITY_VALID/ERRORS`, CLI stdout/stderr and exit status, and defined `RuntimeIdentityError` behavior;
- isolated-worktree execution with no local `.venv`.

## Minimum Write-Set Revision

If the approved global guarantee remains, add at least:

- `tests/unit/test_codex_ledger_bridge.py` and focused command-actor/hook tests;
- `.env.example` and, if invalid seat-banner output must fail, `scripts/seat_banner.py`;
- `.codex/hooks/guard-git-index.sh` plus `.codex/hooks.json`, or command-local enforcement instead;
- `coordination/bin/send-event`, `consume-events`, `claim-lock`, `release-lock`;
- `scripts/consume_bus.py`, `scripts/seat_emit.py`;
- explicit disposition for chief/overseer/CI/merge-gate/cutover/key service identities.

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director2 --wave 2
→ PASS; active route remains `2026-07-10T00-59-43Z-coordinator-to-all-coordination.md`.

$ env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director2 --wave 2
→ hot-tree HEAD `0f24fda`; unread `0 / ref-bus`; Wave 2 MET.

$ env -u GIT_INDEX_FILE git grep -n -E 'infer_runtime_env|render_runtime_env_contract|render_seat_contract|CODEX_SEAT|CODEX_AGENT_ROLE|CODEX_AGENT_MODE|CODEX_BEHAVIOR_SOURCE|CODEX_SESSION_ID' HEAD -- ':!docs/**' ':!tests/**' ':!coordination/mailbox/sent/**'
→ caller set is the model renderers, continuation readiness, seat banner, raw hook seat/marker, and launcher/config surfaces summarized above; mutation/verdict entrypoints do not call the model.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts .venv/bin/python <six-case executable matrix>
→ current model renders `director2/operator2` with operator GO authority; role-only director with seat-owned authority; coordinator/live-seat with coordinator ignored; unknown seat as readiness; and readiness overrides widened to seat-owned operator GO.

$ env | rg '^(CODEX_SEAT|CODEX_AGENT_MODE|CODEX_AGENT_ROLE|GIT_INDEX_FILE)='
→ no output in this explicitly assigned director2 turn.

$ env -u GIT_INDEX_FILE git check-ignore -v .venv; test -x /Users/hyungkoookkim/Pipeline/.worktrees/agent-toml-consolidation/.venv/bin/python
→ `.venv/` is ignored; worktree interpreter check exits 1.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
→ 47 passed; current green suite does not contain the planned identity regression and explicitly excludes its filename.

No code/test/spec/plan edit was made by director2.

## Exact Next Trigger

Coordinator revises the Task-3 design/plan/route before any implementation dispatch: resolve the concrete-role versus role-family rule; define the complete typed interface and per-mode narrow-only allowlists; choose environment/session identity binding; add operation-aware before-mutation/verdict enforcement or narrow the guarantee; make hook validation work from isolated worktrees; and place the identity suite in `CODEX_VERIFICATION_COMMANDS`/`protocol_doctor`. Then reroute `director2-control-plane-authority-foundation-identity-preflight` for one focused re-preflight. Pair-A Tasks 1-2 remain under coordinator decision; this report does not independently cancel them.

Cursor at send: 0
