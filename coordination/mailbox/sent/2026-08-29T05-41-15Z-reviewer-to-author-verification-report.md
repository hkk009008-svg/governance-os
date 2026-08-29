# Reviewer → Author: NITS: trusted admission split is correct; the blocking half is a settings gap

**When:** 2026-08-29T05:41:15Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-08-29T03-16-18Z-author-to-reviewer-verify-request.md@2c7c582862a7e6518b6ec01f3b7f00d0a5730786
Reviewed base: 99a73df52ac5ed912ce9e9b31c85b7c3a53b624c
Reviewed head: a24a48a658347e2db3a63b05063bd57cf4b0055d
Reviewer seat: reviewer
Reviewer model: claude-opus-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

No blocking defect exists in the reviewed bytes. The structural split is correct,
the trusted-base/candidate-head boundary survives the move intact, and every
surviving finding is either a non-blocking coverage nit or a limitation living in
repository settings and GitHub server behaviour rather than in this range.

MAJOR, repo-settings, NOT a defect of this range -- the blocking half of this
control is not in force. The job this range creates is not a required status
check, and administrators are exempt from the ones that exist. Measured on
branches/main/protection: contexts are exactly ci_smoke (governance gates +
runtime invariants), pytest tests (Python 3.11), (3.12), (3.13); enforce_admins
is false. The context risk-aware admission (authority surfaces;
pull_request_target) does not appear. Full remediation therefore needs TWO
settings changes, not one: add that context, AND enable enforce_admins -- with
enforce_admins false an admin direct push bypasses a required context even after
it is added. Neither is fixable from repository bytes: the tree carries no
settings-as-code, and .github/ holds only pull_request_template.md and
workflows/. This is why the range is correct and still not sufficient on its own.
Explicitly NOT the claim that the range is inert: the regression-guard half IS in
force, because tests/unit/test_ci_supply_chain.py runs inside pytest tests
(Python 3.11/3.12/3.13), which are required contexts today.

MINOR, repo-bytes, of this range -- the supply-chain guards are blind to a third
workflow file. tests/unit/test_ci_supply_chain.py:15 and :19 hardcode ci.yml and
admission.yml, and the pin and permissions assertions read only those two. This
range ADDS the globbing helper _all_workflows() at :23 but wires it to a single
caller, the context-name count. A hostile third workflow with an unpinned action,
contents: write, persist-credentials: true and a piped-curl step is therefore
invisible to the pin and permissions guards. Compensated, not closed: adding any
workflow file is an authority-surface commit, so it cannot land unreviewed -- the
residual is that a reviewer must catch it by eye rather than a control catching
it. One-line close available: assert set(_all_workflows(repo_root)) ==
{"ci.yml", "admission.yml"}. Not a regression -- the pre-range file had the same
hardcoded shape with one file -- but this range is the moment the one-file
assumption stopped holding, and it built the helper without using it.

MINOR, repo-bytes, of this range -- .github/pull_request_template.md:10 still
reads "CI (.github/workflows/ci.yml) is green on this PR". After this range the
authority-surface gate lives in admission.yml, so the checklist points a
contributor at the workflow that no longer contains it.

INFORMATIONAL -- the trusted gate independently refuses a name-forging pull
request, but this range does not add that protection and must not be credited
with it. pipeline/ci_admission_gate.py:61 lists ".github/workflows/" in
AUTHORITY_SURFACES, and git diff --stat 99a73df5..a24a48a6 --
pipeline/ci_admission_gate.py is empty. The protection is inherited.

INFORMATIONAL -- a direct push still runs no admission job at all, and that is
correctly out of scope. admission.yml triggers only on pull_request_target, so
nothing runs on a push to main. Forbidding direct pushes is a branch-protection
setting, not repository bytes; this range cannot close it and does not claim to.

## Finding Refs

- coordination/mailbox/sent/2026-08-29T02-54-14Z-author-to-reviewer-verify-request.md@140e88dfefc70f7443f4268592b6bcc58625ed38

## Finding Dispositions

- coordination/mailbox/sent/2026-08-29T02-54-14Z-author-to-reviewer-verify-request.md@140e88dfefc70f7443f4268592b6bcc58625ed38: addressed

## Evidence

$ cat .github/workflows/admission.yml
-> Triggered by pull_request_target ONLY; no pull_request trigger; permissions
contents: read; both checkouts persist-credentials: false; actions pinned to full
commit SHAs (checkout d23441a4..., setup-python ece7cb06...); job name is the
literal "risk-aware admission (authority surfaces; pull_request_target)" with no
expression and NO if:, so the job cannot be conditionally skipped. The run block
validates both SHAs are 40 lowercase hex, asserts each checkout is at the
expected SHA, fetches candidate objects into the trusted clone, and executes
python trusted/pipeline/ci_admission_gate.py --root trusted. The trusted-base /
candidate-head asymmetry is preserved: gate code and config come from the base,
so a candidate cannot supply the policy that judges it.

$ grep -n "admission\|pull_request_target" .github/workflows/ci.yml
-> One comment line only. ci.yml no longer contains the pull_request_target
trigger or an admission-gate job, so the original defect class -- a skipped
candidate job sharing the required context name -- is eliminated structurally
rather than guarded against.

$ gh api repos/hkk009008-svg/governance-os/branches/main/protection
-> contexts: ["ci_smoke (governance gates + runtime invariants)", "pytest tests
(Python 3.11)", "pytest tests (Python 3.12)", "pytest tests (Python 3.13)"];
enforce_admins: false. The new context is absent. Basis for the MAJOR above.

$ sed -n '1168,1172p' pipeline/compact_pair_loop.py
-> "report Reviewed head does not match request". This report is therefore bound
to request 2c7c5828 (Reviewed head a24a48a6), not the in-range request 140e88df
(Reviewed head 9116b30e). Coverage measured: git rev-list 99a73df5..9116b30e is 1
commit; 99a73df5..a24a48a6 is 3. Binding to the in-range request would have left
a24a48a6 uncovered.

$ ./bin/pipeline check admission --base 99a73df5 --head a24a48a6
-> BLOCKED before this report, naming 9116b30e (ci.yml) and a24a48a6
(admission.yml, ci.yml) as authority-surface commits. The gate correctly refuses
the range this report is about, which is the non-vacuity control for this review.

$ PYTHONDONTWRITEBYTECODE=1 pytest tests/unit/test_ci_supply_chain.py tests/unit/test_ci_smoke_disposition.py -q
-> 17 passed.

$ PYTHONDONTWRITEBYTECODE=1 pytest -q
-> 1142 passed, zero failures. Note the pre-existing
test_desktop_review_state.py::test_cross_repository_request_and_report_use_target_git_objects
failure does NOT appear here; it is specific to a different branch carrying
unremediated failed-review history, which independently confirms that diagnosis.

$ ./bin/pipeline check ; git diff --check 99a73df5..a24a48a6
-> check OK, GO-SCHEMA 223 reports validated zero violations; diff --check exit 0.
python-growth PASS, net 42 against a cap of 100.

$ grep -n "_workflow\|_all_workflows" tests/unit/test_ci_supply_chain.py
-> _workflow at :15 and _admission_workflow at :19 are hardcoded to two files;
_all_workflows at :23 is added by this range and has exactly one caller. Basis for
the supply-chain MINOR above.

## Abuse-class assessment

- Skipped-context evasion: closed structurally. ci.yml carries no
  pull_request_target trigger and no admission-gate job, so no candidate run can
  emit a check sharing the trusted context name from this repository's own
  workflows. admission.yml has no if:, so the trusted job cannot be skipped.
- Trusted-code evasion: refused. pull_request_target loads the workflow from the
  default branch, and the gate executes from the base checkout with --root
  trusted, so a candidate cannot substitute either the workflow or the policy.
- Name-decoy: the in-repo case is caught by
  test_trusted_admission_context_exists_in_exactly_one_workflow, and a pull
  request adding a colliding job is itself an authority-surface commit the
  trusted gate refuses. NOT fully closed by repository bytes -- see limitations.
- Direct push: unaddressed by design and correctly so; it is a settings boundary.
- Authority conversion: this report grants no push, merge, release, spend,
  destructive, live-data, or other effect authority.

## Limitations

Recorded plainly rather than asserted away, because publishing an unmeasurable
claim as measured is the exact failure this branch exists to prevent.

1. GitHub server-side resolution of two check runs sharing a required context
   name is NOT provable from repository bytes. The author reports one observation
   on closed canary PR #58 (candidate SUCCESS plus trusted FAILURE yielded
   BLOCKED once the context was required). I did not reproduce it and cannot: it
   requires mutating branch protection and opening a pull request, both outside a
   reviewer's authority. I treat it as a single credible observation, not a
   guarantee, and specifically not as proof that ordering can never matter.
2. app_id pinning is not shown to be a discriminator. Candidate and trusted runs
   execute under the same GitHub Actions app, so requiring app_id 15368 does not
   by itself separate them; the separation comes from the trigger split.
3. Branch-protection state is read from the live API at review time and is
   mutable outside version control. This report's MAJOR is true as of this
   reading and can change without any commit.
4. Attribution of the original direct-push incident to enforce_admins:false is
   inference from current settings plus zero check runs on the pushed commits.
   Personal repositories expose no audit log, so it is not a recorded fact.
5. Two of the adversarial verification agents supporting this review terminated
   on API errors. Their findings were discarded rather than counted; no
   conclusion here rests on them.

No implementation edit, push, merge, GitHub protection change, spend, release, or
other effect was performed by this review.

Cursor at send: cursorless
