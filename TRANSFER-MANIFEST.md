# Transfer bundle — historical generation snapshot

> This file records the bundle as generated and is not current setup or
> operating doctrine. Use `AGENTS.md`, `ARCHITECTURE.md`, and
> `docs/REPOSITORY-MANUAL.md` for current behavior. Preserve the counts and
> paths below as provenance — they describe the bundle at generation time, not
> this repository today.
>
> Indexed trees that no longer exist here: `threeway/` and
> `docs/protocol/threeway/` (the signed bus was deleted — `git ls-files
> threeway | wc -l` → 0), `.claude/hooks/` and the SessionStart/PostToolUse
> hooks (repository lifecycle hooks are absent by design), and
> `requirements-governance.txt` (now `requirements-dev.txt`). `scripts/` was
> renamed `pipeline/`, and `bin/pipeline` is now the single entry point.

This folder is a **portable, project-neutral copy of the "operating system"** that
wrapped an AI-cinema-pipeline repo: the harness config, the multi-seat governance
protocol (director / operator / coordinator), the git-native coordination layer
(mailbox + signed event bus), the CI-enforced doctrine (`governance_verify_all.py`,
`check_no_ceremony.py`), and the dual-runtime harness (`CLAUDE.md` for Claude,
`AGENTS.md` for Codex and other agentic hosts).

Everything cinema-specific — the program code, its history, and its runtime state —
was **left behind**. Everything reusable was **genericized** (cinema nouns/paths/
examples replaced with `<PROJECT>`-style placeholders) while every rule, mechanism,
and structural element was preserved verbatim.

→ **To stand this up in a new repo, follow [TRANSFER-SETUP.md](TRANSFER-SETUP.md).**

---

## What's included (186 tracked files at generation time, incl. this manifest + the setup guide)

### Tier 1 · Harness config
| Path | What it is |
|---|---|
| `.claude/settings.json` | Team-shared Claude Code config: PreToolUse git-index guard + SessionStart smoke hook *(both hooks since removed; the file now records that lifecycle hooks are absent by design)* |
| `.claude/hooks/{guard-git-index,session-smoke,update-state}.sh` | The three runtime hooks *(deleted; the directory no longer exists)* |
| `.claude/hookify.*.local.md` | 6 guard rules (block force-push, block `git add -A`, warn no-verify, warn pytest-without-venv, etc.) |
| `.claude/agents/{lane-v-verifier,money-gate-reviewer}.md` | Two reusable review-agent definitions |
| `.codex/{config.toml,agents/*.toml}` | Codex adapter: six named role deltas; no project lifecycle hooks |
| `.agents/skills/*` | Agent-agnostic protocol and seat skills |
| `.github/workflows/ci.yml`, `.github/pull_request_template.md` | CI skeleton (governance gates wired; domain steps stubbed) |
| `.env.example`, `.gitignore`, `pyproject.toml`, `requirements-governance.txt` | Slim, governance-only configs |

### Tier 2 · Protocol / governance docs
| Path | What it is |
|---|---|
| `CLAUDE.md` | Claude-specific doctrine router (process layer) |
| `AGENTS.md` | Agent-agnostic root and Codex router |
| `docs/protocol/claude/*` · `docs/protocol/agents/*` | The Rules #7–#23 governance bodies (core / director-operator / failure-modes / four-seat-extension / orchestration), in both Claude and agent-agnostic voice |
| `docs/protocol/codex/continuation.md` | Codex continuation adapter |
| `docs/protocol/threeway/*` | Signed-bus control-plane doctrine + onboarding + adoption guides *(deleted with the bus)* |
| `docs/protocol/{program-manual-guide,migration-map-claudemd-split,protocol-assembly-map,advisory-candidates}.md` | Meta-protocol guides |
| `docs/templates/{claude,agents}/*` | Subagent prompt bodies — `claude/`: implementer + reviewer; `agents/`: implementer only (an agent-agnostic reviewer has not been authored) |
| `docs/PROTOCOL-RULES-LOG.md` | Rule provenance log (codified SHAs, empirical basis, beneficiary/consent) |
| `RUNBOOK-DAILY.md` | The common daily loop *(still present; the loop is now author → reviewer, and push is no longer an authority-gated step)* |

### Tier 3 · Skills & agents (reusable subset)
`four-seat-protocol`, `seat-coordinator`, `seat-director`, `seat-operator`,
`wave-gate`, `create-regression-pin` — under both `.claude/skills/` and
`.agents/skills/`. The two
cinema skills (`ai-video-gen`, `comfyui-mastery`) were **excluded**.

### Tier 4 · Coordination tooling + control plane
| Path | What it is |
|---|---|
| `coordination/bin/{claim-lock,release-lock,send-event,consume-events}` | The git-native cross-cutting lock + mailbox event primitives |
| `coordination/README.md`, `coordination/mailbox/kinds.txt` | Coordination mechanics + the mailbox-kind schema |
| `coordination/presence/{SEAT.md.template,README.md}` | Per-seat presence-file template (originals were runtime state) |
| `coordination/mailbox/seen/*.txt` | Compatibility read cursors for the four pair seats; coordinators are cursorless |
| `coordination/workflows/discovery-bughunt.js` | A reusable discovery-bughunt coordination workflow |
| `threeway/*.py` (20 modules) | The Ed25519-signed event-bus control plane (envelope, canon, gate, reducer, refstore, keys, …) *(deleted; no tracked files remain)* |
| `pipeline/*.py` + `*.sh` (37 files) + `placeholder_allowlist.txt` | Governance scripts: `governance_verify_all` (alias `ci_smoke`), `check_{coordination,doc_claims,no_ceremony}`, the three fail-closed adoption gates `check_{placeholders,go_schema,arch_freshness}` (+ their allowlist), `wave_gate_check`, the `*_emit`/`consume_bus`/`run_merge_gate` bus tools, `draft_handoff`, `protocol_*`, etc. *(this tree was `scripts/` at generation time; the bus tools, `ci_smoke`, and the handoff drafters have since been deleted)* |
| `tests/` (`conftest.py` + 22 unit modules) | The pytest regression suite — gate scripts, threeway control plane (canon/envelope/keys/reducer), mailbox protocol, activation scripts, and protocol doc-integrity checks |

---

## What was deliberately excluded

- **The program** — all cinema code (`cinema/`, `*_native.py`, `phase_c_*.py`,
  `quality_max.py`, `lip_sync.py`, `cost_tracker.py`, the `*.json` ComfyUI workflows,
  the `*.swift` files).
- **Program history** — ~300 `HANDOFF-*` / `BRIEF-*` / `AUDIT-*` docs, `docs/archive/`,
  the 135 KB cinema `ARCHITECTURE.md`, the 239 KB cinema `DECISIONS.md`, etc.
  (replaced here with empty-but-structured skeletons).
- **Runtime state** — 780 mailbox `sent/` payloads, the per-seat `seen` cursors and
  presence files, capacity packets, the signed-bus event blobs. *(This
  repository has since accumulated its own committed event history; the
  exclusion describes the bundle, not the store here.)*
- **Domain scripts** — all `pipeline/_*` measurement/probe scripts, `setup_runpod.sh`,
  `run_max_harness.py`, the cinema-measurement tooling.
- **Build/env & session runtime state** — `node_modules/`, `.venv/`,
  `.superpowers/` (gitignored skill-runtime scratch), `logs/`, `projects/`,
  `data/`, `__pycache__/`, secrets (`.env`, `client_secrets.json`, `token.pickle`).

---

## How it was genericized (B2) + verification evidence

**Method:** copy the reusable surface verbatim, then for the 34 files that carried
cinema references, replace cinema **nouns / paths / examples** with placeholders
(`<PROJECT>`, `<entrypoint>`, `<domain-skill>`, `TODO(<PROJECT>)`) while preserving
every rule and mechanism. `governance_verify_all.py` was surgically split: the cinema runtime-
invariant half became a `_project_smoke()` stub; the portable governance-gate half
(doc-anchor drift, coordination state, anti-ceremony, reviewer-result schema) stayed
intact. Five truth/intent skeletons (`ARCHITECTURE.md`, `docs/PROGRAM-MANUAL.md`,
`OPERATIONS.md`, `DECISIONS.md`, `README.md`) were authored fresh.

*Re-baselined 2026-07-03:* the counts below are the generation-time (B2) record.
Since then, governance-hardening Track A grew the bundle 164 → **186** tracked
files (the `tests/` suite, the `check_{placeholders,go_schema,arch_freshness}`
gates + `placeholder_allowlist.txt`, `RUNBOOK-DAILY.md`), and `_project_smoke()`
is **no longer a stub** — it asserts the governance OS's own runtime invariants
(filled in commit `0708c59`; see `pipeline/governance_verify_all.py`).

**Verified at generation time (commands + results):**
- Zero residual cinema tokens — `grep -rIlE '<35-token cinema regex>' .` → **0 / 162 files**.
- Python compiles — `ast.parse` over all `.py` → **53 / 53 OK, 0 failures**.
- Shell valid — `bash -n` over hooks + `bin/` → **0 failures**.
- **Governance OS boots turn-key** — `python pipeline/governance_verify_all.py` → `OK`, **exit 0**
  (the `_project_smoke()` stub runs, the doc-anchor gate passes on the skeleton
  `ARCHITECTURE.md`, the coordination gate passes on the seeded cursors, and the
  anti-ceremony gate passes all five checks — R1–R3, R5–R6; R4 was removed with
  the suite-wide `--runxfail` step).

---

## Placeholder convention

| Placeholder | Replace with |
|---|---|
| `<PROJECT>` | your python package / import name |
| `<PROJECT_NAME>` / "the program" | the human-readable program name |
| `<entrypoint>.py` | your main orchestrator module(s) |
| `<domain-skill>` | your project's domain skill name(s) |
| `<domain-lane-A>` / `<domain-lane-B>` | the two seat-pair domains |
| `TODO(<PROJECT>)` | a hard action item — code/doctrine you must supply (see SETUP) |
| `<ref>` / `<fill-in>` | a citation or section to fill when you author the doc |
