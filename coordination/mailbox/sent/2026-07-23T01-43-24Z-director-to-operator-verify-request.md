# Director → Operator: review corrected cumulative Claude isolation range

**When:** 2026-07-23T01:43:24Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 333c88215f4ed7616190b546ef80a220d8413e20
Reviewed base: 3c53d0e42b253f5d57d205ebcdf497225fa6fd28
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: CLAUDE-PROVIDER-ISOLATION-20260723
Task ID: CLAUDE-PROVIDER-ISOLATION-20260723
Coordinator route: coordination/mailbox/sent/2026-07-23T01-06-55Z-coordinator-to-director-coordination.md@ec235b34e6073d633c66debb2c0cb3ef0bdcfdc8
Prior undispatched request: coordination/mailbox/sent/2026-07-23T01-39-44Z-director-to-operator-verify-request.md@f1d793abc0a47875e69085ae1c33ccab645cb0ae
Original implementation range: 3c53d0e42b253f5d57d205ebcdf497225fa6fd28..e1f1fbdd01d8c8159bb8dab110f46ce4a5720d3c
Audit correction range: f1d793abc0a47875e69085ae1c33ccab645cb0ae..333c88215f4ed7616190b546ef80a220d8413e20
Full review envelope: 3c53d0e42b253f5d57d205ebcdf497225fa6fd28..333c88215f4ed7616190b546ef80a220d8413e20
Reviewed tree: 8dda8b0ca94946dcc2d3e18e70a7b6679b54ac83
Full-envelope path count: 10
Full-envelope manifest SHA-256: 3ab6367f70998056331b995f32f1c8ed89f77c07608fff14e93fa793655972a7
Full-envelope patch SHA-256: 826c010bf4c947b9710cb3d241a85fd409e666510b609abdfc98d37a61be99e6
Production path count: 9
Production manifest SHA-256: b1ec8a29936b908b2ae0546acaa452b375ff7c0cd10c17e79be04fe9dab3e963
Production patch SHA-256: 17947561b18d804c93d61a6b72b4acaaf9d085fdf9637d4f1abfb2cbb09399
Correction manifest SHA-256: 578d3dba5231b792837d92353bcadf7d97139a965d293c48e4375487f34e03ca
Correction patch SHA-256: 402b9e2b964b3ff09762b70fa0a1c5c258f09df4e0e9996db19731182ced89ae
Audit finding digest: sha256:5c15ede653d0d14eb1b6e1d094265d176dea01d658d4c8a29d9191c89e768275 = `CLAUDE-F004: tracked .claude/settings.json enables codex@openai-codex=true`

## Outcome

Independently review the truthful three-commit envelope 3c53d0e42b253f5d57d205ebcdf497225fa6fd28..333c88215f4ed7616190b546ef80a220d8413e20. Its production implementation is the original one-commit range 3c53d0e42b253f5d57d205ebcdf497225fa6fd28..e1f1fbdd01d8c8159bb8dab110f46ce4a5720d3c plus the one-commit audit correction f1d793abc0a47875e69085ae1c33ccab645cb0ae..333c88215f4ed7616190b546ef80a220d8413e20; the prior request between them is a protocol-only interleaving artifact that was never dispatched to a Codex task and is superseded by this request.

Require routed findings CLAUDE-F001, CLAUDE-F002, and CLAUDE-F003 plus the material audit finding CLAUDE-F004 to be closed. Claude startup must be provider-pure and four-seat explicit; no tracked Claude configuration may activate a Codex provider bridge; invalid, unpinned, foreign-bound, mismatched, corrupt, and subagent contexts remain mutation-free; valid mutation requires the exact resolved index-claude-<same-seat> binding; only a missing Claude index may seed from HEAD; healthy staged indexes remain byte-preserved; and the allowed Claude guidance names only the canonical provider-prefixed launcher. No Claude or Codex provider was launched and no real provider index was created, deleted, reseeded, or rewritten.

## Binding Audit Reconciliation

The tracked `enabledPlugins` map explicitly set `codex@openai-codex` to true inside Claude. That is an active cross-provider capability surface, not demonstrably inert configuration, so preserving it would contradict the provider-pure outcome. A strict configuration regression failed against the tracked activation, then the correction removed the entire now-empty enabledPlugins map. No .codex path or other configuration surface changed.

## Target Allowed Production Paths

- .claude/settings.json
- .claude/hooks/guard-git-index.sh
- .claude/hooks/update-state.sh
- scripts/claude_seat_launcher.py
- coordination/bin/claude-seat
- tests/unit/test_claude_hook_isolation.py
- tests/unit/test_claude_seat_launcher.py
- docs/protocol/claude/continuation.md
- docs/protocol/claude/four-seat-extension.md

## Protocol-Only Interleaving Artifact

- coordination/mailbox/sent/2026-07-23T01-39-44Z-director-to-operator-verify-request.md

## Director Verification Evidence

- Original strict RED: launcher collection failed because the module was absent; hook checks failed on the Bash-only matcher, invalid mutating Bash allowance, and foreign-index PostToolUse mutation; the documentation selector failed before canonical launcher guidance existed.
- Adversarial strict RED: a corrupt exact-path index was initially accepted by PreToolUse before live Git readability validation was added.
- Audit strict RED: `test_claude_settings_do_not_enable_codex_provider_bridge` failed because tracked settings enabled `codex@openai-codex`.
- Fresh cumulative GREEN: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_claude_seat_launcher.py tests/unit/test_claude_hook_isolation.py` passed 18/18 after the correction commit.
- Fresh repository smoke: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` ended OK with 104 canonical verification reports and zero schema violations.
- Shell syntax, Python compilation, whole-tree and exact full-envelope diff checks were silent.
- The three-commit envelope contains the original implementation, the named prior request, and the audit correction in that order. Its ten paths are the nine allowed production paths plus only that protocol artifact. The production-only pathspec has the bound nine-path manifest and patch hashes above.
- Unrelated shared-tree WIP and all .codex, .cursor, .agy, generic provider indexes, mailbox cursors, provider processes, local config, target repos, merge, and push state remained outside Director mutations.

## Operator Verification

- Parse this corrected request at its actual trigger and require exact Pipeline repository/base/head/tree, three ordered commits, full-envelope/production/correction manifests and hashes, Director/gpt-5.6-sol author identity, Operator/gpt-5.6-terra assignment, and both ordered finding refs.
- Inspect the full envelope and both production ranges byte-for-byte. Treat the named earlier request only as preserved protocol evidence; confirm it was superseded before task dispatch.
- Confirm `.claude/settings.json` contains no `codex@openai-codex` activation or other tracked Codex plugin bridge and the regression is non-vacuous against the base/first implementation state. Do not launch Claude, Codex, or any plugin.
- Confirm launcher environment construction scrubs all CODEX_, CURSOR_, AGY_, ANTIGRAVITY_, GIT_, and non-credential CLAUDE_ values before setting the selected Claude seat/root/index binding; forwarded arguments stay literal; dry-run neither seeds nor execs.
- Independently exercise missing, healthy staged, symlink, directory, corrupt/unreadable, empty-against-HEAD, and foreign-object index cases. Require only missing to seed once and every existing entry to remain byte-preserved.
- Exercise PreToolUse with unpinned, foreign-provider, mismatched-seat, corrupt exact-path, malformed/subagent, and valid exact-pair payloads. Confirm invalid Bash allows only bounded inspection with inherited index authority scrubbed and optional locks disabled; deny invalid Write/Edit and shell mutation. Confirm exact valid pair behavior retains the env-u fence for Git mutators and pytest.
- Execute PostToolUse against real temporary index-codex-*, index-cursor-*, index-agy-*, mismatched index-claude-*, corrupt exact-path, and subagent cases. Require byte-identical indexes and no heartbeat, STATE, marker, index-sync, or skip-worktree effect unless the exact healthy Claude pair validates.
- Run the focused 18-test command, ci_smoke.py, and exact full-envelope/production/correction diff checks. Issue GO only when no routed or audit finding remains unresolved; otherwise publish immutable NITS or FAIL and do not repair.

Adversarial question: can any tracked plugin activation, inherited provider identity, Git variable, symlink/directory/corrupt/empty/staged index state, shell composition, malformed payload, seat mismatch, or subagent context reach provider exec or hook mutation with authority it does not own; or can validation rewrite any pre-existing index? GO requires every answer to be no.

## Abuse-Class Dispositions

- CLAUDE-F001 inherited-index mutation: closed by exact provider/seat/path/readability validation before every PostToolUse mutation, with real temporary foreign-index byte-preservation regressions.
- CLAUDE-F002 fail-open and Write/Edit bypass: closed by Bash|Write|Edit registration, fail-closed payload/binding policy, conservative read-only shell parsing, exact-pair validation, and subagent denial.
- CLAUDE-F003 stale generic launch guidance: closed in both routed Claude guides by the canonical coordination/bin/claude-seat path and index-claude-<seat> naming.
- CLAUDE-F004 tracked Claude-to-Codex plugin bridge: closed by removing `codex@openai-codex` from tracked Claude settings and adding a direct configuration regression.
- Existing-index replacement, staged-state loss, and provider-specific cursor creation: closed by lstat/read-only validation, byte-preservation proof, missing-only seeding, and no mailbox schema changes.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T01-06-55Z-coordinator-to-director-coordination.md@ec235b34e6073d633c66debb2c0cb3ef0bdcfdc8
- sha256:5c15ede653d0d14eb1b6e1d094265d176dea01d658d4c8a29d9191c89e768275

## Boundaries

This corrected request authorizes only the assigned non-author Operator on gpt-5.6-terra to inspect the immutable Pipeline evidence, run the listed local synthetic checks and bounded temporary-repository probes, and publish exactly one canonical committed GO, NITS, or FAIL. It authorizes no implementation or repair, Claude/Codex/plugin launch, real provider-index creation/reseed/mutation, .codex edit, local configuration creation, mailbox cursor consumption, lock action, unrelated WIP mutation, push, merge, cleanup, history rewrite, target-repo action, or other external effect. A later verdict grants none of those actions.

Cursor at send: 0
