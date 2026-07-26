# Director2 → Operator2: correct stale per-seat index claim in the AGY harness skill

**When:** 2026-07-25T18:54:06Z · **From:** director2 (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: 845f684f5f963221ae713ea6bb7f1056d71e61b1
Reviewed head: 33bcc9fcd12b698b06f247e206ca9dd62712b01d
Author seat: director2
Author model: claude-opus-5
Assigned operator: operator2
Risk class: high-risk-control

## Outcome

Two files in one commit. No other path is touched.

`.agents/skills/antigravity-harness/SKILL.md` carried a stale bullet reading
"Environment & Index Isolation: Each seat uses its dedicated
`.git/index-agy-<seat>` index and isolated process environment." That mechanism
was retired by `09d04fb` ("refactor(agy): stop binding seats to a per-seat Git
index"), and `ARCHITECTURE.md` section 5 records that no side binds a per-seat
Git index and that `index-<provider>-<seat>` is retired. The bullet is replaced
with the launcher's observed behavior: isolated process environment, native
worktree index, and `env -u GIT_INDEX_FILE` for ordinary Git and pytest.

The claim is measured, not inferred. `env -u GIT_INDEX_FILE .venv/bin/python
scripts/agy_seat_launcher.py operator --dry-run` emits an env block of exactly
`AGY_AGENT_MODE`, `AGY_AGENT_ROLE`, `AGY_BEHAVIOR_SOURCE`, and `AGY_SEAT` — no
`GIT_INDEX_FILE` and no index path.

`docs/protocol/agy/continuation.md` and the three `.agy/agents/*.toml` profiles
were checked and are already correct; neither is modified in this range.
`continuation.md` line 19 already says to use the native index of the current
worktree, and the TOML profiles already forbid index creation. A repo-wide grep
for `export GIT_INDEX_FILE=`, `index-agy-`, and `index-claude-` across
`.agents/` and `docs/protocol/agy/` returned the single SKILL.md hit.

The second file adds `test_agy_guides_never_teach_manual_index_binding` to
`tests/unit/test_agy_seat_launcher.py`, asserting that no markdown under
`.agents/skills` or `docs/protocol/agy` contains a `GIT_INDEX_FILE` export
recipe or any retired `index-<provider>-` prefix. Placement is deliberate:
`.agy/agents/*.toml` is already guarded by `test_agy_agent_surfaces.py` and the
launcher itself by
`test_launch_spec_binds_no_index_and_scrubs_inherited_git_authority`; these two
document trees were the only uncovered AGY surface, which is why the drift
landed there and nowhere else. The existing Claude guard in
`tests/unit/test_claude_seat_launcher.py` was deliberately not extended: its
name and its `index-claude-` assertion are Claude-scoped, so an AGY sibling
preserves the per-provider structure rather than blurring it.

The guard is proven non-vacuous. Replaying the pre-fix `HEAD` bytes of both
guide files into a throwaway tree and calling the new test function raised
`AssertionError: .agents/skills/antigravity-harness/SKILL.md: index-agy-`. The
guard also rejected two of the author's own intermediate drafts, once for the
literal `export GIT_INDEX_FILE=` inside a warning sentence and once for the
literal `index-agy-<seat>`; the final prose names the pattern without spelling
out an assignable recipe, and uses ARCHITECTURE.md's generic
`index-<provider>-<seat>` form. This substring strictness is intentional and is
the reviewable design choice in this range: a check that could distinguish a
recipe from a warning about a recipe would be exactly the exemption drift hides
behind.

Verification run by the author, in this worktree, against this commit:
`env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py
tests/unit/test_claude_seat_launcher.py tests/unit/test_agy_agent_surfaces.py
tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py -q`
gave 49 passed. `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
returned OK across project-smoke, ceremony (R1/R2/R3/R5/R6), placeholder,
go-schema (134 reports validated), mechanism-ledger, and arch-freshness.

Note for the reviewer: this worktree's `.codex/config.toml` is clean, so
`test_project_codex_config_does_not_claim_runtime_permissions` passes here. The
uncommitted `.codex/config.toml` dirt reported against the previous range lives
in the `/Users/hyungkoookkim/Pipeline` main checkout, is not this author's, and
was left untouched.

Carried finding, raised by the author, outside the requested scope of this range
and deliberately left unfixed so it cannot be lost. The single digest under
Finding Refs is sha256 over this exact one-line text, hashed with no trailing
newline:

coordination/README.md lines 287-322 still instruct Claude director, operator, director2, and operator2 sessions to export a per-seat GIT_INDEX_FILE pointing at .git/index-<seat> before launching claude, which is the identical session-wide rebinding hazard this range removes from the AGY harness skill and which ARCHITECTURE.md section 5 records as retired; tests/unit/test_claude_seat_launcher.py::test_claude_guides_never_teach_manual_index_binding does not cover coordination/README.md, so the Claude side keeps the same uncovered-surface gap this range closes for AGY.

## Abuse Class Assessment

- Instruction-surface reintroduction of the hazard: the corrected bullet is the only thing standing between an AGY seat and a hand-rolled per-seat index export; confirm the replacement text cannot be read as still endorsing one, and that it does not merely delete the claim while leaving the seat without positive guidance on what to do instead.
- Guard written to pass rather than to catch: a doc-content assertion is cheap to make vacuous, since a wrong glob root, a typo'd needle, or an empty file list all yield green; the non-empty `assert guides` check and the replayed-HEAD negative control are the author's answer, so re-derive both rather than trusting them and confirm the globs actually resolve to the two intended trees.
- Coverage claimed but not held: the Outcome asserts the AGY TOML profiles and the launcher are guarded elsewhere, and if either claim is wrong this range leaves a surface uncovered while reading as complete; verify test_agy_agent_surfaces.py really asserts the retired AGY index prefix is absent and that the launcher test really asserts no GIT_ key survives.
- Prose that defeats its own guard: the new assertions run against the same trees the corrected file lives in, so any future author documenting this hazard must phrase it without the literal strings; confirm this is a bounded, acceptable constraint rather than a trap that pushes the next author into weakening the assertion instead of rewording.
- Scope creep into an unreviewed surface: the carried finding names a live instance of the same hazard in coordination/README.md that is deliberately not fixed here; confirm this range does not partially touch it, and judge whether deferring it is correct or whether the two must land together.
- Model-family independence: the author is claude-opus-5, so a verdict from any Claude-family reviewer does not satisfy high-risk-control, because codex_protocol_model.models_are_independent compares families rather than labels.

## Finding Refs

- sha256:f25fe3f924694e850021c28b6aa90b00857f9391851dad645a0496a1f4b9efe2

Cursor at send: 0
