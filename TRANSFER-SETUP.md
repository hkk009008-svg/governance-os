# Transfer setup — historical generation snapshot

> This setup recipe describes the original transfer bundle and is not a current
> installation path. It is kept as provenance; do not follow it. Several steps
> below name files and modules this repository no longer contains, and they are
> marked inline. Use `AGENTS.md`, `ARCHITECTURE.md`, and
> `docs/REPOSITORY-MANUAL.md` for the current repository, and `bin/pipeline`
> for every command.

Ordered steps to adopt this bundle. See [TRANSFER-MANIFEST.md](TRANSFER-MANIFEST.md)
for what each piece is. The bundle already **boots green** (`governance_verify_all.py` → exit 0)
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
`.github/`, `coordination/`, `docs/`, `pipeline/`, `threeway/`, and the root
`CLAUDE.md` / `AGENTS.md` / `ARCHITECTURE.md` / … land where the doctrine expects them.
*(Historical: the signed-bus `threeway/` tree is gone —
`git ls-files threeway | wc -l` → 0. `scripts/` was later renamed `pipeline/`.)*

## 2. Install the governance deps (Python ≥ 3.11)

```bash
python3 -m venv .venv    # any Python >= 3.11 (floor per DECISIONS.md ADR-004)
.venv/bin/pip install -r requirements-governance.txt   # cryptography + rfc8785
# then append your own project deps to requirements / pyproject
```

*(Historical: `requirements-governance.txt` no longer exists — the current
dependency file is `requirements-dev.txt`, and the venv lives in the primary
checkout only.)*

## 3. Run the smoke to confirm it boots

```bash
.venv/bin/python pipeline/governance_verify_all.py     # expect: ... OK  (exit 0)
```

*(Current form: `bin/pipeline check`. There is no SessionStart hook and no
other repository lifecycle hook — an earlier revision of this step claimed the
smoke ran automatically at the top of every session, which the current contract
forbids: see `.claude/settings.json`, "Repository lifecycle hooks are absent by
design", and `ARCHITECTURE.md` section 5.)*

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
| `pipeline/governance_verify_all.py` (`_project_smoke()`) | your runtime smoke invariants (imports succeed, singletons stable, settings plumb through) |
| `pipeline/wave_gate_check.py` | your product-oracle metric field names (two metric blocks) |
| `.github/workflows/ci.yml` | any model-weight / asset cache steps + your pytest/test job |
| `CLAUDE.md` · `AGENTS.md` (R-SKILL) | your domain-skill load triggers |
| `docs/protocol/{claude,agents}/core.md` | your domain subsystem's caching behaviour example *(historical: only `docs/protocol/agents/core.md` survives; the Claude-side copy is gone)* |
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

**Historical only — this step is unrunnable.** The dormant signed bus was
deleted: `threeway/`, `docs/protocol/threeway/`, and `coordination/threeway/`
carry no tracked files, and `python -m threeway.keys_bootstrap` exits 1 with
"No module named threeway.keys_bootstrap". The mailbox and lock primitives in
`coordination/bin/` were always independent of it and still work. The original
step read:

```bash
python -m threeway.keys_bootstrap                  # writes per-seat keypairs
# private keys live in $THREEWAY_KEYSTORE (default ~/.threeway/keys) — NEVER commit them
# commit the regenerated <seat>.pub files to coordination/threeway/keys/
```

## 8. Adjust the seat roster (optional)

The default receiving roster has four pair seats plus two cursorless
coordinator aliases. To change it, edit `SEATS` / `RECEIVING_SEATS` in
`pipeline/protocol_mailbox.py`. Create read cursors only for identities that
can lawfully consume events. *(Current: `protocol_mailbox.ROLES` is
`('author', 'reviewer')` and only those two may send or receive a new event;
the six seat names above remain readable in committed history and are
cursorless or retired.)*

## 9. Configure concurrent runtimes

Use each provider's launcher. Codex validates one closed identity and uses the
selected task worktree's native Git index; do not create per-seat
`GIT_INDEX_FILE` state or rely on repository lifecycle hooks. Provider-specific
environment values describe identity only and never grant task or side-effect
authority.

---

## Acceptance check

```bash
bin/pipeline check                # OK, exit 0  (pipeline/governance_verify_all.py)
bin/pipeline check coordination   # no FATALs
bin/pipeline check placeholders   # exit 0 when all skeletons are filled
```

**Non-empty target: re-baseline the allowlist first.** The scanner walks every
tracked file, so a merged repo's own pre-existing files can trip it when they
happen to contain a literal token (`<PROJECT>`, `<ref>`, `<fill-in>`, …). On the
first run in a non-empty target, add any such pre-existing paths to
`pipeline/placeholder_allowlist.txt` — they are your baseline, not unfilled
skeletons — then re-run `pipeline check placeholders` until the scan is clean.

**Adoption workflow for placeholders:** Filling a skeleton means removing its path
from `pipeline/placeholder_allowlist.txt`. Run `pipeline check placeholders`
after each removal to confirm the file no longer contains unresolved tokens. When the
allowlist is empty and the scan is clean, the repo is **fully bound** — no skeleton
placeholders remain. (The gate is enforced by CI; a non-empty allowlist with clean
scan simply means the corresponding skeletons are still unfilled.)

When `governance_verify_all.py` is green **and** `_project_smoke()` asserts something real
about your code, the kernel is locally testable. That does not prove the signed
bus, protected merge gate, provider identity, or any external effect is live;
verify those in their actual deployment before claiming them.
