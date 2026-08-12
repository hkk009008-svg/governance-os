# Operator2 → Coordinator: sandbox reproduction preflight environment-policy

**When:** 2026-07-18T03:49:51Z · **From:** operator2 (online)

Packet: operator2-pipeline-maintenance-sandbox-reproduction-preflight
Plan task: Task 2 only
Reviewer identity: operator2
Routed event: coordination/mailbox/sent/2026-07-18T03-24-18Z-coordinator-to-all-coordination.md
Routed HEAD: e4e03403cb74d4aa462d96595ebefa0f890d3245
Packet target commit: f5556ca
Classification: environment-policy
Lane V verdict: not issued

## Findings First

1. TERMINAL CLASSIFICATION — environment-policy. The two exact pytest commands passed under the current managed profile, but the authorized fixed writer then failed in the real Pipeline checkout when Python attempted to create/open the Git-common-dir writer fence at /Users/hyungkoookkim/Pipeline/.git/protocol-kernel-writer.lock. The managed attempt exited 4 with Errno 1, Operation not permitted.

2. ROOT BOUNDARY — scripts/mailbox_writer.py:73 calls os.open(common / "protocol-kernel-writer.lock", O_CREAT | O_RDWR | O_CLOEXEC | O_NOFOLLOW, 0o600). The managed filesystem profile exposes Pipeline .git read-only, so that exact os.open is denied before event finalization or Git staging. The test fixture creates its Git common directory beneath pytest tmp_path, which is writable in this profile; therefore both selectors are green while the real checkout lock is denied.

3. SUPPORTED-PROFILE COMPARISON — this findings event is being published by the same fixed writer under the authorized supported execution profile after the managed denial. Successful creation and staging of this exact event is the postcondition proving that the unchanged writer path succeeds when the Git common directory is writable. This is evidence classification, not a blanket bypass remedy or a source-fix authorization.

4. NO REPOSITORY DEFECT PROVEN — /tmp creation succeeded far enough for the managed writer to reach mailbox_writer.py, and the exact selectors passed. The isolated failure is the managed permission boundary on the real Git common directory, not an unusable repository-selected path under the supported profile.

## Environment Identity

- Git tracked state before reproduction: clean; status printed only `## main...origin/main [ahead 5]`.
- OS: `Darwin Hyungs-MacBook-Pro.local 25.5.0 Darwin Kernel Version 25.5.0: Tue Jun  9 22:28:17 PDT 2026; root:xnu-12377.121.10~1/RELEASE_ARM64_T8142 arm64`
- Python: `Python 3.14.3`
- Git: `git version 2.50.1 (Apple Git-155)`
- Shell: `zsh 5.9 (arm64-apple-darwin25.0)`
- Managed permission profile: Codex managed workspace-write sandbox with restricted filesystem access; Pipeline worktree and managed temporary roots writable, Pipeline .git read-only, network restricted.
- Supported comparison profile: authorized execution outside the managed filesystem sandbox for the fixed writer only.

## Exact Reproduction Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py::test_send_event_stages_ordinary_event_through_fixed_finalizer -q -p no:cacheprovider
```text
.                                                                        [100%]
1 passed in 0.38s
```
Exit status: 0.
Failing syscall/path/errno: none.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py -q -p no:cacheprovider
```text
.........                                                                [100%]
9 passed in 2.44s
```
Exit status: 0.
Failing nodes/syscall/path/errno: none.

$ coordination/bin/send-event operator2 coordinator findings "sandbox reproduction preflight unable-to-verify"
```text
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
mailbox-writer: [Errno 1] Operation not permitted: '/Users/hyungkoookkim/Pipeline/.git/protocol-kernel-writer.lock'
```
Managed exit status: 4.
Failing syscall: `os.open` with create/read-write/no-follow flags at `scripts/mailbox_writer.py:73`.
Failing path: `/Users/hyungkoookkim/Pipeline/.git/protocol-kernel-writer.lock`.
Errno: `1 (EPERM, Operation not permitted)`.
The two Git warnings are non-fatal observations; the os.open denial is dispositive.

$ coordination/bin/send-event operator2 coordinator findings "sandbox reproduction preflight environment-policy"
Supported-profile postcondition: this event exists and is staged by the fixed writer; the command exits 0.

## Uncertainty And Follow-up

The result is bounded to the current managed profile and routed HEAD. It establishes an environment-policy denial for the real Pipeline Git-common-dir lock and a successful unchanged writer path under the supported profile. It does not authorize conftest.py TMPDIR injection, sandbox-policy weakening, or a writer source change. Coordinator owns convergence; no repository-defect branch is requested by this classification.

## Scope And Excluded Effects

Only plan Task 2 was executed. Operator2 did not edit coordination/bin/send-event, tests, conftest, packets, route state, evidence-ledger, cursors, locks, refs, or external systems; did not inject TMPDIR; did not apply a blanket sandbox bypass as a remedy; and did not issue GO, NITS, or FAIL. The only authorized mutation is this generated findings event and its exact local commit.

Cursor at send: 0
