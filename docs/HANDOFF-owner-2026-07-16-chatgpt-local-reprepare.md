# HANDOFF owner — ChatGPT local reprepare preservation

When: 2026-07-16
Owner: director
Disposition: commit-and-handoff

## Frozen Source And Preservation Head

- Source branch: `main`
- Source base: `560a95d70cde463913cae6fdbc355f7478c25498`
- Preservation branch: `codex/chatgpt-local-reprepare-flexibility-2026-07-16`
- Preservation head: `3dcff96948003d510451266b017895b42bd73c2e`
- Preservation commit subject: `fix(consult): preserve local reprepare correction`

The preservation commit changes exactly these sixteen paths and binds these Git
blob IDs:

| Path | Blob |
|---|---|
| `.agents/skills/chatgpt-pro-consultation/SKILL.md` | `2503fe1f40823a28241c14dd9bacc823be9396ab` |
| `.agents/skills/four-seat-protocol/SKILL.md` | `e6fd7b7e256e1acc3b315ad5240b41dffff500ea` |
| `.agents/skills/seat-coordinator/SKILL.md` | `8ee9d8efb252131483ab4c0d2603b7ad80e965bf` |
| `.agents/skills/seat-director/SKILL.md` | `e9f185f45225516ff233c6aa96b475563d9e649a` |
| `.agents/skills/seat-operator/SKILL.md` | `d52fe922ba76af8c9d7d090b48f147773ad80b9e` |
| `.codex/agents/protocol-coordinator.toml` | `b0b0572169de6b3d7161d2486de891fe8c7c1f82` |
| `.codex/agents/protocol-director.toml` | `8fa5bab7a61e6ec78ff99928256dbfc96a68c79e` |
| `.codex/agents/protocol-operator.toml` | `85322bf14f1ef39cbc6d85b8d2efd566379207df` |
| `.codex/agents/readiness-bridge.toml` | `d8075fff3fc64f1b4d74bbc8ed4aa31de818ffb5` |
| `AGENTS.md` | `ed7ed3757e04130c2c55aef0415b02b1b59d07dd` |
| `docs/protocol/codex/continuation.md` | `af8a148f02bba8ecda8d80334ae0dcf233bb454b` |
| `docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md` | `dca17eb8d94cee51fa78353d655a40da3599aaf8` |
| `scripts/chatgpt_pro_consult.py` | `fa8b9d92ba79ddcbf83f843a43d79ef8bd962abe` |
| `scripts/codex_protocol_model.py` | `8e2b3bd96860ce41844301769349d750a3b5eca6` |
| `tests/unit/test_chatgpt_pro_consult.py` | `f0f349b9cdb15eb75da9b8c80ec89a1108a34968` |
| `tests/unit/test_protocol_prompt_sync.py` | `bf726b6ee82ff6f99946b9387f35758bba0e963f` |

## Preservation Evidence

Executed from the preservation branch:

```text
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py -q

309 passed in 5.03s
```

```text
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py

PROJECT SMOKE — governance-OS runtime invariants ... OK
RESULT: no ceremony detected — every relied-on green is backed by execution.
PLACEHOLDER CHECK — PASS (no unallowlisted tokens).
GO-SCHEMA CHECK — PASS (41 verification-report(s) validated; zero violations).
ARCH-FRESHNESS CHECK — PASS (stamp bump detected or body unchanged).
OK
```

These checks are preservation evidence only. They do not approve the branch for
shipping or grant integration authority.

## Authority And Exclusions

- Integration authority: none
- Provider attempts: zero
- Push authority: none
- No receipt or runtime state was mutated.
- No lock or mailbox cursor was changed.
- The untracked 2026-07-15 plan is preserved context, not sufficient shipping
  authority.
- This preservation branch is not an accepted implementation branch and is not
  a merge or publication candidate without a later lawful route.

## Exact Next Trigger

User approval of a dedicated design and compliant implementation plan, followed
by a routed independent review of the frozen commit.
