# Transfer setup — stand up the governance OS in a new repo

Ordered steps to adopt this bundle. See [TRANSFER-MANIFEST.md](TRANSFER-MANIFEST.md)
for what each piece is. The bundle already **boots green** (`ci_smoke.py` → exit 0)
out of the box; these steps make it *yours*.

---

## 1. Copy into the new repo root

Copy the **tracked files only**. The bundle's working tree also holds untracked
runtime state (`.venv/`, `.superpowers/` skill scratch, `logs/`, session
artifacts) that must NOT travel — so drive the copy from `git ls-files`, not a
blind `cp -R`:

```bash
cd /path/to/this-bundle-repo
mkdir -p /path/to/new-repo
git ls-files -z | tar --null -T - -cf - | tar -xf - -C /path/to/new-repo
cd /path/to/new-repo
git init   # if not already a repo
```

**Non-empty target — clobber hazards.** Files land at the repo root, so a target
that already has a `README.md`, `.gitignore`, `CLAUDE.md`, `AGENTS.md`, or
`pyproject.toml` gets them **overwritten** by the bundle's versions. For a
non-empty target, extract to a staging directory first, diff, and merge those
by hand — in particular make sure the merged `.gitignore` still ignores
`.venv/` and `.superpowers/` (the bundle's does; yours may not).

The layout already mirrors a repo root: `.claude/`, `.codex/`, `.agents/`,
`.github/`, `coordination/`, `docs/`, `scripts/`, `threeway/`, and the root
`CLAUDE.md` / `AGENTS.md` / `ARCHITECTURE.md` / … land where the doctrine expects them.

## 2. Install the governance deps (Python ≥ 3.11)

```bash
python3 -m venv .venv    # any Python >= 3.11 (floor per DECISIONS.md ADR-004)
.venv/bin/pip install -r requirements-governance.txt   # cryptography + rfc8785
# then append your own project deps to requirements / pyproject
```

## 3. Run the smoke to confirm it boots

```bash
.venv/bin/python scripts/ci_smoke.py     # expect: ... OK  (exit 0)
```

This is also the SessionStart hook — it runs automatically at the top of every
Claude/Codex session.

## 4. Replace the global placeholders

A repo-wide find/replace gets you 90% there:

```bash
# package/import name, human name, entrypoints
grep -rl '<PROJECT>'      . --exclude-dir=.git    # then sed -i '' 's/<PROJECT>/yourpkg/g'
grep -rl '<PROJECT_NAME>' . --exclude-dir=.git
grep -rl '<entrypoint>'   . --exclude-dir=.git
```

## 5. Resolve the `TODO(<PROJECT>)` hard action items

These are the places that need *your code/doctrine*, not just a name swap:

| File | What to supply |
|---|---|
| `scripts/ci_smoke.py` (`_project_smoke()`) | your runtime smoke invariants (imports succeed, singletons stable, settings plumb through) |
| `scripts/wave_gate_check.py` | your product-oracle metric field names (two metric blocks) |
| `.github/workflows/ci.yml` | any model-weight / asset cache steps + your pytest/test job |
| `CLAUDE.md` · `AGENTS.md` (R-SKILL) | your domain-skill load triggers |
| `docs/protocol/claude/four-seat-extension.md` | the Pair-A / Pair-B domain split for your project |
| `docs/protocol/{claude,agents}/core.md` | your domain subsystem's caching behaviour example |
| `.claude/skills/seat-director/{SKILL,r-brief-template}.md` | your domain-specialist reviewer targets |
| `.claude/agents/money-gate-reviewer.md` | the phases your cost/budget precheck could miss (delete this agent if you have no budget gate) |
| `coordination/workflows/discovery-bughunt.js` | your high-risk subsystem keys/probes |

## 6. Write the truth + intent docs (skeletons provided)

The whole discipline (R-START, R-EVIDENCE, the staleness rule) leans on these. They
ship as **empty-but-structured skeletons** — fill them as the new program takes shape:

- `ARCHITECTURE.md` — the verified-truth file (topology + file:line facts + the §N
  smoke-invariants section your `_project_smoke()` implements + a `Last verified:` footer).
- `docs/PROGRAM-MANUAL.md` — the user-principal's intent (what you build + how to
  operate it to full capability).
- `OPERATIONS.md` · `README.md` · `DECISIONS.md` (append-only ADR log; ADR-001 example included).

## 7. Generate the signing trust-root (if you use the threeway signed bus)

The `threeway/` control plane verifies every load-bearing fact against Ed25519 keys.
The bundle ships **only public-key layout docs** — generate fresh keys for your deployment:

```bash
.venv/bin/python -m threeway.keys_bootstrap        # writes per-seat keypairs
# private keys live in $THREEWAY_KEYSTORE (default ~/.threeway/keys) — NEVER commit them
# commit the regenerated <seat>.pub files to coordination/threeway/keys/
```

If you don't need cryptographic merge-gating yet, you can defer this — the mailbox +
lock primitives in `coordination/bin/` work without it.

## 8. Adjust the seat roster (optional)

The default is 6 seats: `director`, `director2`, `operator`, `operator2`,
`coordinator`, `coordinator2`. To change it, edit `SEATS` / `RECEIVING_SEATS` in
`scripts/protocol_mailbox.py`, then add/remove the matching
`coordination/mailbox/seen/<seat>.txt` cursor files (seeded at `0`).

## 9. Wire the harness env (for concurrent seats)

Copy `.env.example` → `.env` and set per-seat values (`CLAUDE_SEAT`, `GIT_INDEX_FILE`,
the `CODEX_*` contract). For a single-session start you can skip this — the hooks and
smoke work without it.

---

## Acceptance check

```bash
.venv/bin/python scripts/ci_smoke.py        # OK, exit 0
.venv/bin/python scripts/check_coordination.py   # no FATALs
.venv/bin/python scripts/check_placeholders.py   # exit 0 when all skeletons are filled
```

**Non-empty target: re-baseline the allowlist first.** The scanner walks every
tracked file, so a merged repo's own pre-existing files can trip it when they
happen to contain a literal token (`<PROJECT>`, `<ref>`, `<fill-in>`, …). On the
first run in a non-empty target, add any such pre-existing paths to
`scripts/placeholder_allowlist.txt` — they are your baseline, not unfilled
skeletons — then re-run `scripts/check_placeholders.py` until the scan is clean.

**Adoption workflow for placeholders:** Filling a skeleton means removing its path
from `scripts/placeholder_allowlist.txt`. Run `scripts/check_placeholders.py` after
each removal to confirm the file no longer contains unresolved tokens. When the
allowlist is empty and the scan is clean, the repo is **fully bound** — no skeleton
placeholders remain. (The gate is enforced by CI; a non-empty allowlist with clean
scan simply means the corresponding skeletons are still unfilled.)

When `ci_smoke.py` is green **and** `_project_smoke()` asserts something real about
your code, the OS is live: every session starts under the guard hooks, the seat
protocol is loadable as skills, and the coordination + signing layers are ready when
you scale to concurrent seats.
