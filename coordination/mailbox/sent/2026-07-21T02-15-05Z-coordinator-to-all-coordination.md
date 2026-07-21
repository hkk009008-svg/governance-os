# Coordinator → All: authorize Packet 2 local integration and cleanup

**When:** 2026-07-21T02:15:05Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet2-integration-2026-07-21
Task ID: ledger-audit-remediation-packet2-integration-2026-07-21
Status: ACTIVE — LOCAL FAST-FORWARD AND EXACT PACKET CLEANUP
Route generation: 9
Supersedes route: coordination/mailbox/sent/2026-07-21T01-21-34Z-coordinator-to-all-coordination.md
Expected control HEAD: ed019815b23be296d77836e88f07f0e8fae40faf
Superseded route ref: coordination/mailbox/sent/2026-07-21T01-21-34Z-coordinator-to-all-coordination.md@3de4c3adfe4e21bd89518224e8bb063f9605856b
Authorization source: user-task:authorized-packet2-local-integration-2026-07-21; user-task:clean-up-packet2-branch-2026-07-21
Accepted Packet 2 GO: coordination/mailbox/sent/2026-07-21T01-15-02Z-operator2-to-all-verification-report.md@7b16985e74201fe572e32c132f2678c498aa5c65
Executor/model: director / existing compatible Codex task
Target base: 13413d05b0b40476b5d5919f99062d5104866818
Target worktree: /Users/hyungkoookkim/evidence-ledger
Accepted target HEAD: 538c9dab07e93ada190ef318ec06dc225ec54b3b

## Outcome Contract

Execute the user-authorized local fast-forward of evidence-ledger `main` from
`13413d05b0b40476b5d5919f99062d5104866818` to the independently accepted
Packet 2 head `538c9dab07e93ada190ef318ec06dc225ec54b3b`, prove the integrated state,
then remove only the Packet 2 isolated worktree and its local feature branch.

This route creates no product edit, conflict resolution, replacement commit,
remote-reference publication, dependency change, service/data access, private
workbook access, cursor mutation, protocol-lock action, deployment, booking,
or spend.

## Director Autonomous Contract Revision 10

Before entering evidence-ledger, Director publishes exactly one fresh
director-to-all coordination event through the fixed writer and commits only
that event. It uses:

- Task ID: ledger-audit-remediation-packet2-integration-2026-07-21
- Outcome contract: Execute and verify the exact authorized Packet 2 local fast-forward and exact Packet 2 branch/worktree cleanup, then report the immutable pre/post evidence.
- Parent contract: this committed generation-9 Coordinator route's exact path at its full commit SHA
- Contract revision: 10
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the full immutable refs of this route and the accepted Packet 2 GO

Director proves the contract effective and global route lineage valid, then
runs the ordinary ledger start guard from Pipeline before touching the target.
The contract grants no effect beyond the two tokens below.

## Side-Effect Executor Token

- effect: local git fast-forward integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: from=13413d05b0b40476b5d5919f99062d5104866818, to=538c9dab07e93ada190ef318ec06dc225ec54b3b, method=git-merge-ff-only, preserve=.vscode/settings.json@sha256:a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4

## Side-Effect Executor Token

- effect: exact local feature worktree and branch cleanup
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss:refs/heads/codex/audit-remediation-parser-loss
- scope: after-main=538c9dab07e93ada190ef318ec06dc225ec54b3b, remove-one-worktree=/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss, delete-one-local-branch=codex/audit-remediation-parser-loss, preserve-all-other-worktrees-and-branches

## Exact Preflight

Director stops without mutation unless all of the following are true at one
fresh observation:

- Pipeline contains this exact committed route and its effective revision-10
  Director child; route validation, global lineage, and ledger start guard pass.
- Normal evidence-ledger checkout is on local `main` at exactly
  `13413d05b0b40476b5d5919f99062d5104866818`.
- Its only status entry is the pre-existing untracked `.vscode/` directory,
  and `.vscode/settings.json` hashes to
  `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.
- The Packet 2 worktree is clean on
  `codex/audit-remediation-parser-loss` at exactly
  `538c9dab07e93ada190ef318ec06dc225ec54b3b`.
- The accepted base is an ancestor of the accepted head; the range is exactly
  four commits and exactly these seven paths: `ARCHITECTURE.md`,
  `import/load_agency.py`, `import/parse_agency_schedule.py`,
  `import/parse_workbook.py`, `import/tests/test_load_agency_unit.py`,
  `import/tests/test_parse_agency_schedule.py`, and
  `import/tests/test_parse_workbook.py`.
- The accepted Operator2 GO still binds exactly that repository, base, head,
  and range.

No fetch, pull, checkout replacement, autostash, reset, rebase, amend,
cherry-pick, conflict resolution, or unrelated staging is permitted.

## Exact Execution And Verification

Director performs one ordinary local `git merge --ff-only` of the exact
accepted head into the already-checked-out normal `main`. It then verifies in
the normal checkout:

- local `main` and `HEAD` equal
  `538c9dab07e93ada190ef318ec06dc225ec54b3b`;
- the old base remains an ancestor and the integrated range remains four
  commits with the same seven paths;
- `.vscode/settings.json` retains the exact protected hash and `.vscode/`
  remains the only status entry;
- `git diff --check` for the exact range succeeds;
- the accepted 96-test Packet 2 command passes without skip, xfail, or failure;
- `scripts/check_doc_claims.py ARCHITECTURE.md` succeeds; and
- target `scripts/ci_smoke.py` ends OK.

Only after every merged-state check passes, Director removes the exact Packet
2 worktree with `git worktree remove` and deletes only local branch
`codex/audit-remediation-parser-loss` with non-force `git branch -d`.
Director does not run broad worktree pruning because unrelated historical
registrations are outside this cleanup scope.

Final checks require local `main` and `HEAD` still equal the accepted head,
the protected settings hash is unchanged, the Packet 2 worktree path is absent,
the Packet 2 local branch is absent, and every other worktree and branch is
preserved.

## Completion Evidence

After success, Director publishes exactly one ordinary director-to-all
coordination event through the fixed writer with subject
`report Packet 2 local integration and cleanup`. It contains the exact route
ref, pre/post target heads, protected settings hash, test counts, documentation
and smoke results, removed worktree/branch names, preserved boundaries, and
states that remote publication did not occur. The event contains no
`Task-board` field and therefore is evidence, not a successor route. Director
commits only that event in Pipeline and returns its immutable ref to
Coordinator.

If any preflight, fast-forward, verification, or cleanup check fails, Director
stops, preserves all recoverable state, publishes one truthful blocker instead
of a success report, and performs no fallback or broader cleanup.

## Frozen Boundaries

Remote-reference publication authority: none.
Other branch/worktree cleanup authority: none.
Product-edit and new-commit authority in evidence-ledger: none.
Network, dependency, service, managed-data, private-data, provider, deployment,
booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Force deletion, reset, rebase, amend, squash, revert, and conflict-resolution
authority: none.

## Exact Next Trigger

Director reads this committed generation-9 route, publishes and proves its
revision-10 autonomous contract, runs the exact preflight, executes the two
tokens in order, publishes the single completion-evidence event, and stops.
Coordinator then independently reconciles Pipeline lineage plus the local
target head, protected settings hash, exact cleanup scope, and fresh merged-tree
verification. No remote action follows without a new explicit authorization.

Cursor at send: 0
