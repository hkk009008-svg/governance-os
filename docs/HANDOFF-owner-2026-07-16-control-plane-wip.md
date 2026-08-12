# HANDOFF owner — control-plane WIP preservation

When: 2026-07-15T22:05:27Z
Owner: director
Task-board: pipeline-recovery-owner-wip-disposition-2026-07-16
Disposition: commit-and-handoff for salvage only

## Authority

The preservation-only coordinator route is
`coordination/mailbox/sent/2026-07-15T22-02-30Z-coordinator-to-all-coordination.md`
at commit `f69e004303e97f3409b260a000ad4265b07ecefe`, blob
`9130a619b180ceae2acd518c1c679e5e918f382b`, and SHA-256
`2a9014d81c6b3c47bdb4a3de11b27e7b6518d50d6ee19b51b96fa4e535bacc3e`.
It authorized preservation of the exact parked nine-path snapshot and no
Task2U repair, verification verdict, integration, activation, publication, or
cleanup.

## Frozen Source And Preservation Head

- Original branch: `codex/control-plane-authority-foundation-2026-07-10`
- Original branch head before and after preservation:
  `6983673db60bff0d21548a90ab1db2fcbbfa377a`
- Preservation branch: `codex/recovery-control-plane-wip-2026-07-16`
- Preservation parent: `6983673db60bff0d21548a90ab1db2fcbbfa377a`
- Preservation head: `b2ff2e564445324b628c43c2072356331c17a66e`
- Preservation commit subject:
  `chore(recovery): preserve control-plane Task2U WIP`

The preservation commit changes exactly these nine paths and binds these Git
blob IDs:

| Path | Blob |
|---|---|
| `ARCHITECTURE.md` | `1a8fabc4568dba23bd3d9292def97367098a282a` |
| `scripts/bus_unread.py` | `31cf7050a798d8de6a881cc375e82421ddab07c3` |
| `scripts/consume_bus.py` | `ef05882959fbe86803e10e23d5546ab9c0ac0dc1` |
| `scripts/protocol_authority.py` | `f8a915e1fb4fd68eb0f590e0ed955558e3ecd45e` |
| `scripts/protocol_mailbox.py` | `d46eee144e5099dd69fe7de27fc37bd5c6328ae7` |
| `tests/unit/test_coordination_tooling.py` | `da8d6fb598536a99749c6ea9fc10c9cffa87c09c` |
| `tests/unit/test_protocol_authority.py` | `5c2568f32bf59de3a1b1d966dff1255fe9d07ca4` |
| `tests/unit/test_protocol_mailbox.py` | `a258a3ad710fdc917d8e09b95096e71b16e29789` |
| `tests/unit/test_threeway_activation_scripts.py` | `1f7bcead80dfb5f43aa4300fcc66b9f8b2693a1e` |

The preservation worktree is clean at the frozen head. The original branch ref
was not moved, and no amend, rebase, merge, reset, or history rewrite occurred.

## Preservation Evidence

Executed from
`.worktrees/control-plane-authority-foundation-2026-07-10`:

```text
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_authority.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_threeway_activation_scripts.py -q

97 passed in 17.83s
```

`git diff-tree --no-commit-id --name-only -r b2ff2e5...` returned exactly the
nine paths above, and `git diff b2ff2e5^ b2ff2e5 --check` printed nothing.
These are preservation checks only; they do not supersede the binding FAIL or
prove Task2U acceptance.

## Binding Historical Blockers

- Operator FAIL:
  `coordination/mailbox/sent/2026-07-10T18-33-55Z-operator-to-all-verification-report.md`
  at commit `a9244b41bd4d3a5f47dcb348507b88cb08e92158`, blob
  `72265c13c5e7362cb6434afd0e48b30e62bfb9ce`, SHA-256
  `f44e2a5f3bdcc078e7893875255125b07b7470e244afd256774a5e492da5ae5f`.
- Director contradiction:
  `coordination/mailbox/sent/2026-07-11T00-06-19Z-director-to-coordinator-coordination.md`
  at commit `d743a57b1967f644587af83dd739d2c378643343`, blob
  `a59e0fe2faddf6de628bfdee5c97f256fcbd2894`, SHA-256
  `a45fff6eb9327814b8ff7bc64cbca0c28808afc09dbcf0637e7c3bb77fe4b1b1`.

This branch is salvage input only. It is not Task2U, not GO, not a production
candidate, and must never be merged wholesale. Any later convergence work must
select and independently verify individual concepts against current main.

## Side Effects Not Taken

No provider was invoked, no receipt or cursor changed, no lock was claimed, no
remote ref was updated, and no integration, activation, publication, branch
removal, worktree removal, or cleanup occurred.

## Exact Next Trigger

After the Phase-1/2 integration plan closes with its required owner handoffs,
GO evidence, and integrated-head proof, the coordinator may route
`docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`
against this exact preservation head. Until then, retain the branch and this
handoff byte-for-byte.
