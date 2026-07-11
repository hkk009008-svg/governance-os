# Core Protocol - Claude Code

> Claude Code detail document loaded **on trigger**, not at session start.
> Root routers keep short stubs; this file holds the current expanded rule body.
> **Provenance (Pipeline deployment):** empirical bases, commit SHAs, ADR
> numbers, and named modules cited in the rule bodies below are origin-project
> history carried by the transfer bundle (ADR-002) — they ground each rule's
> rationale, not Pipeline file claims. Pipeline-live specifics are governed by
> `docs/protocol/claude/continuation.md`; Pipeline decisions live in
> `DECISIONS.md` (operative lanes: ADR-009).

---

# Session-start protocol (read me first)
*Router handle: `R-START` (stub in CLAUDE.md routes here).*

**Truth lives in `ARCHITECTURE.md` at the repo root.** This file (CLAUDE.md)
is the *process layer* — the impact-analysis method, multi-task orchestration, session
discipline. `ARCHITECTURE.md` is the *truth layer* — verified facts about the
pipeline, with file:line references and a project smoke block. When they disagree
about facts, `ARCHITECTURE.md` wins.

Both files drift from the actual code between sessions. Before doing any
non-trivial work, verify against current source. If a claim is stale,
**fix the relevant file in the same change** that exposes the staleness —
don't let a wrong claim survive your session.

Concrete protocol at session start (≤2 minutes):

1. Run the project smoke block — `env -u GIT_INDEX_FILE .venv/bin/python
   scripts/ci_smoke.py` (the governance-OS invariants live in its
   `_project_smoke()`; the prefix is load-bearing — the placeholder gate's
   `git ls-files` inherits the ambient index). If it fails, the doc is
   stale OR the working tree is broken — fix one or the other before
   proceeding with the user's task.
2. Skim `ARCHITECTURE.md` §2 component topology. Spot-check:
   - `ls scripts/ coordination/ threeway/` (the governance-kernel code surface)
   - `ls coordination/capacity/packets/` (the live route's packets)
3. `git log --oneline -20` — if any commit touched a module documented in
   `ARCHITECTURE.md` since it was last edited (the `*Last verified: ...*`
   timestamp at the file footer), re-read that section against the new code.
4. **If you find a stale claim:** edit `ARCHITECTURE.md` first, in the same
   commit (or a `docs:` prep commit right before) the user's task lands.
   The user has stated this as a standing requirement.

Trust the code; update the prose when it diverges.

# Verification discipline for factual claims
*Router handle: `R-EVIDENCE` (stub in CLAUDE.md routes here).*

Codified 2026-05-24 after a director-level inventory error: STRATEGIC_REVIEW
and HANDOFF both claimed "only one unit test file" when there were 24. The
director wrote those docs from session memory of one scoped pytest run + an
anchored mental model, without ever running `ls tests/unit/`. Root cause:
session memory trusted over filesystem. See [DECISIONS.md ADR-013](../../../DECISIONS.md).

The class of error is fully preventable. These three rules close it.

## Rule 1 — No inventory claim without verification output

Any factual claim in a doc, commit message, or code comment of the shape
**"X files," "Y functions," "Z tests," "N LOC," "present in <path>,"
"absent from <path>"** requires the producing command's output captured in
the same change.

- In docs: paste the command + its output in a code block under the claim,
  OR cite it explicitly (`verified via $ ls tests/unit/ | wc -l → 24`).
- In commit messages: include the command and result in the body.
- "Just trust me" is not acceptable. Cite or don't claim.

## Rule 2 — Scoped output stays scoped

A command scoped to one path produces output about that path only.
`pytest tests/unit/foo.py` gives you `foo.py`'s test result, NOT the unit
suite's. `grep X dir/file.py` covers `file.py`, NOT `dir/`. `ls one_file`
tells you about one file.

When you want a wider claim, **re-run at the wider scope.** Do not
generalize from a narrow command. The shell never lies about what it ran;
you can lie to yourself about what it covered.

## Rule 3 — Pre-commit trip-wire for strategic docs

Before committing any strategic-review, handoff, ARCHITECTURE.md, or any
other director-voice document, the author runs the verifying commands for
every factual claim and pastes the output (or a representative snippet) in
the commit message. If a verifying command would take >30 seconds, note
it explicitly: `verified via <command> on YYYY-MM-DD`.

Cost: seconds. Cost of skipping: wrong direction for the next operator
(the 24-vs-1 test error).

## When you cannot comply

If you genuinely cannot run the verifying command (no shell, no
filesystem, no internet), state the claim as **unverified** explicitly:
> I believe X based on session memory but did not run the verifying command.

This is honest and lets the next reader treat the claim as a hypothesis,
not a fact. **Never apply director-voice authority over an unverified
factual claim.** Authority and verification travel together.

## When does this apply?

| Yes — verify before stating | No — verify not required |
|---|---|
| "There are N test files" | "Tests live under tests/unit/" (no count) |
| "X function is unused" | "X function is referenced in the imports of Y" (your immediate context) |
| "Y file is N lines" | A general qualitative claim ("this is large", "this is well-tested") |
| "Z module has no callers" | A directional claim ("this could be deleted if zero callers") |
| Any specific count, file presence, function existence | Architectural reasoning, design rationale |

The rule is: **specific factual claims = verification required.**
Qualitative directional claims = use your judgment but flag uncertainty.

## Verification tiering (R-VERIFY-TIER)
*Router handle: `R-VERIFY-TIER` (stub in CLAUDE.md). Capacity lever #3, audit `wf_6be2ee18-f4b`.*

The discipline that prevents UNDER-verification (R-EVIDENCE, Rule #9) has no companion
that prevents OVER-verification. A doc-only paragraph about an undisputed, deferred
defect drew ~25–31 adversarial agent-runs across four independent passes
(wf_73f95c8c / wf_e09bded6 / wf_5d39bbe3 / wf_ed13f2b4 — see the
R-VERIFY-TIER addendum in docs/PROTOCOL-RULES-LOG.md), producing
zero fix code. Past the second independent confirmation, more passes on the same question
add cost, not confidence.

- **(A) Convergence cap for doc-only deferred-defect notes.** Two independent seats
  confirming the same file:line claims = converged. A Rule #23 co-sign is one of the
  two. A third adversarial pass is justified ONLY when scoped to a *different* question
  (e.g. blast-radius mapping beyond the note, as `wf_5d39bbe3` legitimately was) — and
  the launching seat must state that incremental question first. Applies to
  `docs(arch)`-class deferred notes only; production code keeps Lane V / Rule #9
  per-commit verification. <!-- origin: a single doc paragraph drew ~25-31 agent-runs across 4 passes with no new question, adding cost but no confidence -->
- **(B) RED test at find-time.** When an adversarial workflow or agent-assisted
  investigation confirms a code defect that is NOT being fixed this session
  (`fix_with_brief` / `fix_deferred`), the finding seat commits a
  `pytest.mark.xfail(strict=True, reason='...')` reproducing the failure in the same
  session. If a faithful test is infeasible within budget, label the finding
  `test-infeasible` with the specific reason in the handoff. Turns
  O(agents × sessions) re-verification into O(seconds in CI).

Keep R-EVIDENCE (cite the command) and R-MEASURE (commit the instrument) distinct —
they close different gaps. R-VERIFY-TIER caps the *number* of passes; it does not
weaken any single pass.

## When you change something

Beyond the impact-analysis checks above:

- One commit per logical slice. Run the project smoke block
  (`env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`) before
  declaring a slice done.
- Don't combine concerns. A bug fix isn't a refactor isn't a feature.
- If your change touches a documented subsystem, update the relevant
  section in `ARCHITECTURE.md` in the same PR.
- **For work beyond a single slice (≥5 sub-tasks or ≥800 LOC of total
  change), don't implement in main context — orchestrate. See
  "Working a Multi-Task Plan" below.**

# Session-wrap & handoff hygiene
*Capacity lever #2 (audit `wf_6be2ee18-f4b`). Cuts stale-filename churn — 119
handoff docs had accumulated, many with verdicts baked into 100+ char names that
were false hours later.*

- **Handoff filenames carry NO reversible state.** Name = `HANDOFF-<seat>-YYYY-MM-DD[-PMn].md`
  only (seat + date + optional sequence). Verdicts, GO/NO-GO, pod/push/HEAD status,
  blast-radius — all live in the BODY, where they can be corrected without spawning a
  new file. A name like `...task4-GO-...-pod-BILLING.md` is false hours later and
  forces "STALE — trust git" caveats downstream.
- **Body is reconstructable-minus-git.** Record only: last-commit SHA, open
  carry-forwards with status, session-specific sharp edges not yet promoted to a
  standing doc, cursor position. Omit anything `git log` already proves.
- Append-only across sessions is retained (one file per seat per session) — it is the
  concurrent-write race-detection signal; do not overwrite-in-place.

# Git-tooling sharp edges (standing — stop re-deriving these in handoffs)
*Capacity lever #2. These are durable environment facts, not session observations.
Reference this section from a handoff; don't restate it.*

- **Stale per-seat / default index → phantom `MM`/deletions.** `git status` and
  `git diff --stat HEAD` read the index and can show committed files as
  modified/deleted. Ground truth: `git cat-file -e HEAD:<f>` (in HEAD?) + `test -f <f>`
  (on disk?). Reseed with `git read-tree HEAD`.
- **macOS `core.ignorecase=true` collapses case-only renames.** `git mv Foo.json foo.json`
  can become a no-op/duplicate. Verify via the object store (`git ls-tree HEAD`), or use
  `git -c core.ignorecase=false`, or `rm --cached` + `add`.
- **Partial commits need an explicit pathspec.** `git commit -m … -- <path>` builds a
  temp index from HEAD and cannot sweep a peer's staged WIP even if HEAD moved under
  you. A bare `git commit` from a shared/default index CAN sweep peers — always
  pathspec-scope (`-m` BEFORE `--`).
- **Subagent git uses `env -u GIT_INDEX_FILE`** (subagent shell state does not
  persist); main-seat commits go through the per-seat index directly — do NOT apply
  `env -u` there.
- **Deliberate seat-index maintenance under the guard hook.** `guard-git-index.sh`
  blocks any Bash command that sets `GIT_INDEX_FILE=` without an `env -u` prefix —
  including intentional seat-index ops. Compliant routes: rebuild a stale seat index
  with `env -u GIT_INDEX_FILE git read-tree --index-output=.git/index-<seat> HEAD`
  (never sets the var); read-only inspection via
  `env -u GIT_INDEX_FILE sh -c 'GIT_INDEX_FILE=… git diff --cached --stat HEAD'`.
  Seat indexes go stale whenever commits land via another index (seeded blobs then
  show as phantom `MM`) — verify staleness (`git ls-files -s` blob vs `git ls-tree
  <commit>`) before rebuilding. The exported var also FOLLOWS `cd` into other repos
  (2026-07-07: made ~/evidence-ledger look object-corrupt) — cross-repo git always
  gets the `env -u` prefix.
- **A result-caching subsystem re-run with identical inputs may return a cached
  result instead of new output** (false-fail, not a real error). Cache-bust by
  varying a seed / output-name / request parameter before concluding the
  subsystem is broken. (Origin-project lesson — no Pipeline governance-kernel
  instance recorded yet; keep the class in mind for any cached gate/tool output.)
