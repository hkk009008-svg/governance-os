# Director → Operator: review Claude provider-isolation actual range

**When:** 2026-07-23T01:39:44Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: e1f1fbdd01d8c8159bb8dab110f46ce4a5720d3c
Reviewed base: 3c53d0e42b253f5d57d205ebcdf497225fa6fd28
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: CLAUDE-PROVIDER-ISOLATION-20260723
Task ID: CLAUDE-PROVIDER-ISOLATION-20260723
Coordinator route: coordination/mailbox/sent/2026-07-23T01-06-55Z-coordinator-to-director-coordination.md@ec235b34e6073d633c66debb2c0cb3ef0bdcfdc8
Route immutable parent: 70edfd34b32dd77201bf52d58e2cb702cf77d4ad
Implementation commit: e1f1fbdd01d8c8159bb8dab110f46ce4a5720d3c
Reviewed tree: 4550612942b46503063aa353a81535973af2f5cc
Path count: 9
Path manifest SHA-256: b1ec8a29936b908b2ae0546acaa452b375ff7c0cd10c17e79be04fe9dab3e963
Patch SHA-256: 9fc4563f0a353fc19a5c06f9e48422fb44da07da2e4f26c47b792332cc43f3cf

## Outcome

Independently review the immutable one-commit actual range 3c53d0e42b253f5d57d205ebcdf497225fa6fd28..e1f1fbdd01d8c8159bb8dab110f46ce4a5720d3c against the exact corrected coordinator route. Require all three routed findings CLAUDE-F001, CLAUDE-F002, and CLAUDE-F003 to be closed: Claude startup must be provider-pure and four-seat explicit; invalid, unpinned, foreign-bound, mismatched, corrupt, and subagent contexts must remain mutation-free; valid mutation must require the exact resolved index-claude-<same-seat> binding; only a missing Claude index may seed from HEAD; healthy staged indexes remain byte-preserved; and the allowed Claude guidance must name only the canonical provider-prefixed launcher. No Claude process or real provider index was launched, created, deleted, reseeded, or rewritten.

The actual base is 3c53d0e42b253f5d57d205ebcdf497225fa6fd28 because four unrelated committed AGY lane events landed after the route commit and before the Claude implementation commit. The reviewed range itself is exactly one commit and nine routed paths; those interleavings are excluded from the review range and preserved.

## Allowed Paths

- .claude/settings.json
- .claude/hooks/guard-git-index.sh
- .claude/hooks/update-state.sh
- scripts/claude_seat_launcher.py
- coordination/bin/claude-seat
- tests/unit/test_claude_hook_isolation.py
- tests/unit/test_claude_seat_launcher.py
- docs/protocol/claude/continuation.md
- docs/protocol/claude/four-seat-extension.md

## Director Verification Evidence

- Strict RED was observed before production edits: launcher collection failed because the module was absent; hook checks failed on the Bash-only matcher, invalid mutating Bash allowance, and foreign-index PostToolUse mutation; the documentation selector failed before the canonical launcher text existed.
- The corrupt exact-path adversarial regression then failed before the guard added live Git readability validation.
- Fresh focused GREEN: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_claude_seat_launcher.py tests/unit/test_claude_hook_isolation.py` passed 17/17 after commit.
- Fresh repository smoke: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` ended OK with 104 canonical verification reports and zero schema violations.
- Shell syntax, Python compilation, scoped worktree diff checks, and exact-range `git diff --check` were silent.
- The exact range has one commit, nine paths, the bound tree/manifest/patch hashes above, and no excluded .codex, .cursor, .agy, AGENTS.md, .gitignore, protocol kernel, smoke, or prompt-sync path.

## Operator Verification

- Parse this request at its committed trigger and require the exact repository, base, head, tree, one-commit range, nine-path manifest and hashes, Director/gpt-5.6-sol author identity, Operator/gpt-5.6-terra assignment, and ordered immutable route finding reference.
- Inspect every changed byte. Confirm launcher environment construction scrubs all CODEX_, CURSOR_, AGY_, ANTIGRAVITY_, GIT_, and non-credential CLAUDE_ values before setting only the selected Claude seat/root/index binding; forwarded arguments stay literal; dry-run neither seeds nor execs.
- Independently exercise missing, healthy staged, symlink, directory, corrupt/unreadable, empty-against-HEAD, and foreign-object index cases. Require only missing to seed once, and require every existing entry to remain byte-preserved on success or failure.
- Exercise PreToolUse with unpinned, foreign-provider, mismatched-seat, corrupt exact-path, malformed/subagent, and valid exact-pair payloads. Confirm invalid Bash allows only bounded read-only commands with inherited index authority scrubbed and optional locks disabled; deny Write/Edit and all other shell mutation. Confirm a valid exact pair permits Write/Edit and ordinary shell mutation while retaining the env-u fence for Git mutators and pytest.
- Execute PostToolUse against real temporary index-codex-*, index-cursor-*, index-agy-*, mismatched index-claude-*, corrupt exact-path, and subagent cases. Require byte-identical indexes and no heartbeat, STATE, marker, index-sync, or skip-worktree effect unless the exact healthy Claude pair validates.
- Run the focused 17-test command, ci_smoke.py, and exact-range diff check. Issue GO only when no routed finding or abuse-class boundary remains unresolved; otherwise publish immutable NITS or FAIL and do not repair.

Adversarial question: can any inherited provider identity, Git variable, symlink/directory/corrupt/empty/staged index state, shell composition, malformed payload, seat mismatch, or subagent context reach Claude exec or hook mutation with authority it does not own; or can validation rewrite any pre-existing index? GO requires every answer to be no.

## Abuse-Class Dispositions

- CLAUDE-F001 inherited-index mutation: closed by exact provider/seat/path/readability validation before every PostToolUse mutation, with real temporary foreign-index byte-preservation regressions.
- CLAUDE-F002 fail-open and Write/Edit bypass: closed by Bash|Write|Edit registration, fail-closed payload/binding policy, conservative read-only shell parsing, exact-pair validation, and subagent denial.
- CLAUDE-F003 stale generic launch guidance: closed in both routed Claude guides by the canonical coordination/bin/claude-seat path and index-claude-<seat> naming.
- Foreign provider and Git environment injection: closed by prefix-wide launch scrubbing and child/internal Git environment tests.
- Existing-index replacement or staged-state loss: closed by lstat-before-Git classification, read-only validation, byte-preservation proof, and missing-only read-tree --index-output seeding.
- Provider-specific mailbox/cursor state: not introduced; the launcher and hooks alter no mailbox cursor contract.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T01-06-55Z-coordinator-to-director-coordination.md@ec235b34e6073d633c66debb2c0cb3ef0bdcfdc8

## Boundaries

This request authorizes only the assigned non-author Operator on gpt-5.6-terra to inspect the immutable Pipeline range, run the listed local synthetic checks and bounded temporary-repository probes, and publish exactly one canonical committed GO, NITS, or FAIL. It authorizes no implementation or repair, Claude/provider launch, real provider-index creation/reseed/mutation, local configuration creation, mailbox cursor consumption, lock action, unrelated WIP mutation, push, merge, cleanup, history rewrite, target-repo action, or other external effect. A later verdict grants none of those actions.

Cursor at send: 0
