# ChatGPT Local Re-prepare Task 1 Singular Lane-V Correction Design

Status: DRAFT for separate user-principal approval.

This document corrects only Task 1 of
`docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md`.
It does not modify that already approved design or plan. It is authorized for
drafting by
`coordination/mailbox/sent/2026-07-16T06-58-35Z-coordinator-to-all-coordination.md`.
This document and its companion plan grant no candidate, review, provider,
receipt, verdict, integration, publication, or cleanup authority.

## 1. Problem

The approved Task 1 asks for one binding verification report over two immutable
frozen heads:

- Codex half `Hc = 3dcff96948003d510451266b017895b42bd73c2e`;
- Claude half `Hl = 233ef8126bc75dc6a2a13adcb70810b619faa85c`.

The current `lane-v-scope/v1` contract cannot bind two reviewed heads. It
requires exactly one reviewed head, one exact reviewed base that is a strict
ancestor of that head, one descriptor-backed range, and one structurally
matching report attestation. `Hc` and `Hl` are siblings rather than an
ancestor/descendant range. Naming both only in prose would leave one frozen
range outside structural authority.

The correction must preserve the original intent: one independent review of
the combined behavior before either frozen head is integrated into `main`.

## 2. Verified frozen geometry

The following commands were executed against the drafting route at
`18601aa7c41e76c09e0c5f65ce83dfa860cafb95`:

```text
$ git show -s --format='%H%n%P' 3dcff96948003d510451266b017895b42bd73c2e
3dcff96948003d510451266b017895b42bd73c2e
560a95d70cde463913cae6fdbc355f7478c25498

$ git show -s --format='%H%n%P' 233ef8126bc75dc6a2a13adcb70810b619faa85c
233ef8126bc75dc6a2a13adcb70810b619faa85c
96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a

$ git merge-base 3dcff96948003d510451266b017895b42bd73c2e 233ef8126bc75dc6a2a13adcb70810b619faa85c
560a95d70cde463913cae6fdbc355f7478c25498

$ git diff-tree --no-commit-id --name-only -r --no-renames 3dcff96948003d510451266b017895b42bd73c2e | wc -l
16
$ git diff-tree --no-commit-id --name-only -r --no-renames 233ef8126bc75dc6a2a13adcb70810b619faa85c | wc -l
7
$ comm -12 <(git diff-tree --no-commit-id --name-only -r --no-renames 3dcff96948003d510451266b017895b42bd73c2e | LC_ALL=C sort) <(git diff-tree --no-commit-id --name-only -r --no-renames 233ef8126bc75dc6a2a13adcb70810b619faa85c | LC_ALL=C sort)
tests/unit/test_protocol_prompt_sync.py
$ { git diff-tree --no-commit-id --name-only -r --no-renames 3dcff96948003d510451266b017895b42bd73c2e; git diff-tree --no-commit-id --name-only -r --no-renames 233ef8126bc75dc6a2a13adcb70810b619faa85c; } | LC_ALL=C sort -u | wc -l
22

$ git merge-base --is-ancestor 3dcff96948003d510451266b017895b42bd73c2e 18601aa7c41e76c09e0c5f65ce83dfa860cafb95; echo $?
1
$ git merge-base --is-ancestor 233ef8126bc75dc6a2a13adcb70810b619faa85c 18601aa7c41e76c09e0c5f65ce83dfa860cafb95; echo $?
1
```

`git diff-tree --no-commit-id --name-only -r` reports 16 paths for `Hc` and
7 paths for `Hl`. Their only intersection is
`tests/unit/test_protocol_prompt_sync.py`, so the sorted union contains exactly
22 paths:

1. `.agents/skills/chatgpt-pro-consultation/SKILL.md`
2. `.agents/skills/four-seat-protocol/SKILL.md`
3. `.agents/skills/seat-coordinator/SKILL.md`
4. `.agents/skills/seat-director/SKILL.md`
5. `.agents/skills/seat-operator/SKILL.md`
6. `.claude/skills/four-seat-protocol/SKILL.md`
7. `.claude/skills/seat-coordinator/SKILL.md`
8. `.claude/skills/seat-director/SKILL.md`
9. `.claude/skills/seat-operator/SKILL.md`
10. `.codex/agents/protocol-coordinator.toml`
11. `.codex/agents/protocol-director.toml`
12. `.codex/agents/protocol-operator.toml`
13. `.codex/agents/readiness-bridge.toml`
14. `AGENTS.md`
15. `CLAUDE.md`
16. `docs/protocol/claude/continuation.md`
17. `docs/protocol/codex/continuation.md`
18. `docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md`
19. `scripts/chatgpt_pro_consult.py`
20. `scripts/codex_protocol_model.py`
21. `tests/unit/test_chatgpt_pro_consult.py`
22. `tests/unit/test_protocol_prompt_sync.py`

Neither frozen head is an ancestor of drafting-route `main`. The candidate
construction must re-prove all of these facts after user approval; this
snapshot is design evidence, not execution authority.

## 3. Options considered

### 3.1 Selected: isolated two-merge candidate lineage

Create a review-only lineage from one route-bound base `P`. Incorporate `Hc`
and then `Hl` with two mechanical no-fast-forward merges, producing one final
candidate `C`. Review exactly `P..C`. This satisfies the one-head/one-base
schema while retaining both immutable source heads as Git parents.

This is the smallest construction that preserves all required properties.

### 3.2 Rejected: two independent Lane-V reports

One report for each frozen head would be structurally valid, but it would not
provide the single binding combined-behavior review required by approved Task
1. It would also duplicate review work and leave cross-half interaction outside
either individual range.

### 3.3 Rejected: squash or synthetic composite implementation commit

A squash would create one range, but it would discard immutable-head ancestry,
turn review composition into a new implementation artifact, and weaken the
later proof that Tasks 2 and 3 integrate the original frozen heads. No squash,
cherry-pick, rebase, patch replay, or hand-authored composite commit is allowed.

### 3.4 Rejected: shipping-commit trigger on `C`

The selected construction needs the descriptor after `C`, and `C` is a merge
commit rather than a `feat`, `fix`, or `refactor` shipping commit carrying the
descriptor trailer. The canonical trigger is therefore a committed
Director-to-Operator verify-request strictly after `C`.

## 4. Candidate topology and identities

A later coordinator execution route is commit `R`. Its first parent is the
candidate base `P`. This makes `P` mechanically derivable and ensures the two
correction documents already exist in the reviewed snapshot, while `R` remains
external route authority outside the reviewed range.

```text
                         Hc (immutable Codex half)
                        /
P ------------------- M1
                       \
                        C ---------------- D ---------------- T -------- V
                       /
             Hl (immutable Claude half)

first-parent chain: P -> M1 -> C -> D -> T -> V
merge parents:      parents(M1) = [P, Hc]
                    parents(C)  = [M1, Hl]
reviewed range:     P..C
descriptor commit: parents(D)   = [C]
request commit:    parents(T)   = [D]
report commit:     parents(V)   = [T]
```

The exact runtime identities are:

- `R`: a future coordinator route committed only after separate approval of
  both correction documents;
- `P = first_parent(R)`;
- `M1`: mechanical no-fast-forward merge of `Hc` into `P`;
- `C`: mechanical no-fast-forward merge of `Hl` into `M1`;
- `D`: descriptor-only direct child of `C`;
- `T`: verify-request-only direct child of `D`;
- `A`: later coordinator activation route, committed only after `T` exists and
  Opus Stage A is terminally clear;
- `V`: Pair-A Operator's report-only direct child of `T`, containing the one
  canonical GO/NITS/FAIL report for `P..C` after activation and review.

`P` is runtime-bound rather than a prose placeholder: the execution plan
derives it from `R^`, verifies it is full lowercase 40-hex, and requires the
body of `R` to repeat that exact value once as `Candidate base`.

## 5. Candidate construction contract

The future route may authorize one candidate branch and one isolated worktree.
The shared root remains on `main`.

Construction is valid only if:

1. `R` is the newest mailbox route and the current `main` HEAD;
2. `P = R^` contains both correction documents and both previously approved
   ChatGPT documents;
3. the two frozen refs still equal `Hc` and `Hl` exactly;
4. neither frozen head is already an ancestor of `P`;
5. the candidate branch and worktree do not already exist;
6. locks and the shared index are empty;
7. both no-fast-forward merges complete without conflicts;
8. no manual edit, `git add`, restore, checkout, or generation occurs between
   merge start and merge commit; Git's own staging of the merge result is
   expected;
9. parent order is exactly `[P,Hc]` then `[M1,Hl]`;
10. both frozen heads are ancestors of `C`;
11. state-free `git merge-tree --write-tree --no-messages` precomputes an
    expected tree before each merge, and `M1^{tree}` / `C^{tree}` equal those
    expected tree OIDs after the mechanical commits;
12. `git diff --name-status -z --no-renames P..C` equals the normalized frozen
    union exactly, not merely its path names;
13. `git diff --check P..C` is clean and the candidate worktree is clean.

A merge-tree preflight conflict stops before `git merge` starts, so there is no
merge state to abort. A conflict reported by an actual `git merge --no-commit`
requires `git merge --abort` and then the same bounded contradiction artifact.
Neither path permits resolution, rerere, checkout, restore, or edits to the
conflicted paths. Any path or parent mismatch is candidate contamination and
has the same stop outcome.

## 6. Singular descriptor and trigger

The descriptor identity is fixed now so later execution cannot silently choose
a new review question:

- task ID: `f1e1ad5f-cb1b-4650-93ad-bf8701069f32`;
- descriptor path:
  `coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json`;
- question ID: `chatgpt-local-reprepare-task1-singular-lanev`;
- trigger kind: `verify-request`;
- verification mode/profile: `codex-lane-v`;
- verification harness: `codex:lane-v-verifier`;
- exact reviewed base: runtime-bound `P`;
- allowed path roots: the 22 exact paths in §2;
- verification commands: the two focused unit-test files together;
- requirement paths: the approved design and plan, this correction design and
  plan, the frozen Codex owner handoff, the drafting coordinator route, and the
  one content-addressed Opus prompt-authority object.

`D` directly parents `C` and changes only the descriptor path. `T` directly
parents `D`, changes only one canonical sent-mailbox verify-request, and binds
exactly one of each:

- `Event type: verify-request`;
- `Reviewed head: C`;
- `Reviewed base: P`;
- exact descriptor path and SHA-256 digest;
- `Hc` and `Hl` as provenance-only source heads;
- provider attempts authorized: zero;
- receipt mutations authorized: zero;
- a terminal `Exact Next Trigger` directing Operator to wait for `A`.

The source heads never appear as additional reviewed heads or bases in `T` or
`V`. They are provenance only. The report attestation is structurally bound to
`C/P` and the exact `T` identity.

After `T`, Director runs only the provider-free
`resolve_authoritative_scope()` path, then the state-free
`resolve_provider_authoritative_scope()` path to bind the content-addressed
provider prompt. From the provider-resolved scope it derives the exact attempt
key and scope digest with `compute_attempt_key()` and `compute_scope_digest()`,
then separately proves prospective receipt/lock absence. Despite its name, the
provider resolver launches no provider and creates no receipt or reservation.
It must not call `review()`, instantiate a receipt store in a way that creates
its directory, or call a receipt-store lock method. Receipt/lock absence is
checked against the mechanically derived common-dir path with read-only
filesystem tests.

## 7. Provider boundary and activation

`T` alone does not authorize a provider attempt. Its terminal trigger requires
a later coordinator activation `A`. `A` may exist only when:

1. Opus Stage A has a terminal durable closeout and no longer owns Operator2;
2. `P`, `C`, `D`, `T`, the descriptor digest, request blob, provider-resolved
   scope digest, prompt-authority facts, candidate branch, and worktree are
   unchanged;
3. the prospective attempt receipt and lock are absent;
4. no prior provider attempt exists for the exact attempt key;
5. Pair-A Operator is the named executor;
6. the route carries a complete Side-Effect Executor Token bound to the exact
   `opus_review_bridge.py review` command for `T/C/P`;
7. the token authorizes at most one provider process and zero retries,
   fallbacks, substitutes, or credential entry.

The review command omits `--authorization-source`; after all structural checks,
the bridge resolves the absent source to
`standing-policy:codex-lane-v-opus-v1`. The side-effect token authorizes the
one execution; it does not forge or replace the bridge's authorization
identity.

Operator first performs verdict-blind primary Codex Lane V analysis, then runs
the one Opus attempt without sharing its provisional verdict or findings. Every
Opus finding is reconciled. The bridge remains advisory and Operator retains
GO/NITS/FAIL authority. The activation token authorizes exactly one canonical
verification-report publication, one report-only local commit `V` with parent
`T`, and that single candidate-ref advance; it authorizes no other edit or ref
mutation.

Provider unavailability is recorded visibly and never retried. A schema-valid
degraded reconciliation does not discharge approved Task 1's different-harness
review requirement, even if its guard says `go_allowed=true`. Unavailability,
uncertain or partial delivery, an unreconciled receipt, or failed correlation
therefore blocks integration. Proceeding would require a separate explicit
user exception naming an alternate non-author harness; no retry or transport
substitution is inferred.

## 8. Failure and abuse-case table

| Case | Detection | Required result |
|---|---|---|
| Conflict | merge-tree returns nonzero/non-tree, or an actual no-fast-forward merge reports an unmerged path | stop before merge, or abort the active merge; no hand resolution; one bounded contradiction artifact |
| Path drift | source union or `P..C` differs from the exact 22 paths | stop; no descriptor or trigger |
| Parent drift | any parent list differs from `[P,Hc]` or `[M1,Hl]` | stop; candidate is contaminated |
| Base drift | `P` is not `R^`, lacks required docs, or contains either frozen head | stop before branch/worktree creation |
| Frozen-ref drift | either branch ref differs from its fixed full SHA | stop; do not substitute a descendant or equivalent tree |
| Candidate contamination | dirty candidate, extra commit/path, hooks mutate files, or shared root is touched | stop; preserve evidence; no descriptor |
| Descriptor drift | schema, task ID, base, requirements, paths, or commands differ | stop before `D` |
| Stale trigger | `T` is not a strict descendant of `C`, or fields/digest/blob disagree | stop; Operator does not reconstruct authority |
| Premature activation | Stage A not terminally clear or `A` lacks exact executor token | no Operator action and no provider attempt |
| Provider unavailable | bridge returns normalized unavailable evidence | no retry/fallback; integration blocked absent a separate user-authorized non-author harness |
| Uncertain delivery | send state or delivery cannot be proven | mark failed when safe; no retry/fallback; integration blocked |
| Receipt already exists | prospective receipt/lock is present before authorized first attempt | stop; do not delete, reset, resume, or overwrite |
| Receipt changes during review | receipt identity/state no longer matches exact attempt | stop; no invented attestation or second attempt |
| Finding conflict | confirmed blocking or unresolved relevant Opus finding | NITS/FAIL according to severity; no integration |
| Integration substitution | later task proposes merging `M1`, `C`, `D`, `T`, or `V` | reject; Tasks 2/3 merge only `Hc` then `Hl` |

## 9. Verification and report contract

Before descriptor creation, Director runs at `C`:

```bash
(
  cd /Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_chatgpt_pro_consult.py \
    tests/unit/test_protocol_prompt_sync.py -q
)
```

The descriptor binds the path-equivalent `.venv/bin/python` command because
the review bridge installs the trusted Pipeline virtualenv at `.venv` inside
its immutable snapshot before executing descriptor commands.

`ci_smoke.py` is deliberately not a Task 1 candidate command. `Hc` moves
`scripts/codex_protocol_model.py` anchors while the approved integration plan
defers `ARCHITECTURE.md` coherence to its later Task 5. Running smoke against
the exact 22-path candidate would therefore fail for the expected anchor drift;
adding `ARCHITECTURE.md` would contaminate the reviewed range. Smoke returns as
a required gate after the original coherence task on integrated `main`.

The drafting evidence is deterministic: `ARCHITECTURE.md` pins
`LEDGER_CLI_BRIDGE`, `render_r_independence`, and `render_ledger_start_guard`
at lines 547, 773, and 857, while `git show Hc:scripts/codex_protocol_model.py |
rg -n` locates those same symbols at lines 549, 775, and 859. The frozen change
adds two net lines at the earlier consultation-rule block; `ARCHITECTURE.md` is
not one of the 22 frozen paths.

Operator independently reruns the path-equivalent worktree command, requires
the bridge to execute the descriptor's exact snapshot command, and validates
the complete topology, 22-path manifest, all cases in §8, the accepted
whitespace-split unnamed-base64 residual from the approved design, and exact
receipt/provider evidence.

`V` changes only its canonical verification-report path and contains exactly
one `Reviewed head: C` and one `Reviewed base: P` in its attestation. `Hc` and
`Hl` may be cited only in a provenance subsection. A GO is the only result that
unlocks the original plan's Task 2; NITS or FAIL returns to coordinator without
edits by Operator.

## 10. Integration firewall

Candidate history exists only to make pre-integration review structurally
singular. It is not a shipping candidate and must never be merged, cherry-picked,
rebased, fast-forwarded, or pushed into `main`.

After a binding GO for `P..C`, the original approved plan resumes at Task 2:

1. merge immutable `Hc` into `main`;
2. merge immutable `Hl` into `main`;
3. perform the original coherence work and post-merge verification.

Before that reuse, all 22 path modes and blobs on integration `main` must equal
their values at `P`. The two integration merge parent lists must then be
`[preMain,Hc]` and `[I1,Hl]`; `Hc` and `Hl` must be ancestors of the resulting
`I2`; `M1`, `C`, `D`, `T`, and `V` must not be ancestors of `I2`; and the
resulting 22 path modes/blobs must equal `C`. Any mismatch invalidates reuse and
requires a new routed question. The candidate itself never becomes integration
input.

## 11. Consultation and independence record

The pre-plan authority-boundary trigger normally qualifies for ChatGPT Pro
advice. The user-principal explicitly prohibited provider attempts and receipts
for this drafting turn, so no consultation record was prepared, reserved, or
sent. Consultation status: `prohibited by current task scope; zero attempts`.

R-INDEPENDENCE is instead satisfied at design time by one bounded, read-only
same-model adversarial reviewer plus local source/schema inspection. This is a
weaker harness than a different model and is identified as such. The actual
diff review remains Pair-A Operator plus one verdict-blind Opus attempt under
the later exact token.

## 12. Approval and non-goals

Separate explicit user approval of both this document and
`docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md`
is required before any candidate ref, branch, worktree, merge, descriptor,
verify-request, provider attempt, receipt action, or verdict.

This design does not authorize edits to the approved design/plan, production
code, frozen branches, compact work, Opus Stage A, mailbox cursors, locks,
remote refs, publication, deployment, or cleanup.

## Exact Next Trigger

The coordinator refreshes this committed design/plan pair and returns them to
the user-principal for separate explicit approval. Until that approval and a
new execution route exist, every candidate, trigger, provider, receipt, and
verdict action remains prohibited.
