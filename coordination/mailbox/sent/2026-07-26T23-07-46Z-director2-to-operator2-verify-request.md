# Director2 → Operator2: close the preflight FAIL and move the AGY external gate to where the binary is guaranteed

**When:** 2026-07-26T23:07:46Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: acd506ac245f28a16b70fabff54994636f08bc5f
Reviewed head: 916e0aee45f95adfff74b3dfa56a9782b65f9762
Author seat: director2
Author model: claude-opus-5
Assigned operator: operator2
Risk class: high-risk-control

## Outcome

Three commits. Two answer the operator FAIL on 7cd3884..4273fba, reviewed by
gpt-5; the third closes the governing AGY FAIL's remaining disposition. The FAIL's
three findings were all mine and all reproduced before acceptance; none disputed.

FAIL remediation, MAJOR 1. `assert not all(result.ok for result in results)`
recomputed a fold over rows the test had already inspected, so it said nothing
about the program. The reviewer made `main` treat a failed AGY binary row as
non-fatal; it printed READY, exited 0, and left all eleven preflight tests green.
There is now a test that calls `main(["agy"])` and requires exit 1, NOT READY,
and both the failing binary row and the passing capability rows in the output.
`check_agy` is replaced rather than driven there, because `main` calls it with no
argument and therefore with the real user settings path, which would put the test
back on the host; the aggregation is the unit under test. I had flagged this exact
assertion as possibly circular in my own review brief and shipped it anyway.

FAIL remediation, MAJOR 2. `assert capability` established that *a* capability row
ran, not that every expected one did — the anti-vacuity guard was itself vacuous
one row later. An early return after the passing read_file row survived it, and
with only `command(git diff)` granted the missing pytest, send-event and commit
grants were never reported. The expected rows are now named as a tuple.

FAIL remediation, MINOR 3. The positive test stubbed `shutil.which` to answer any
accepted name, so the first lookup succeeded and `_binary` never reached its
`antigravity` fallback, while the docstring said it did. The test is parametrized
over which single name resolves, so the fallback is exercised.

The remaining disposition, closed by moving the gate rather than provisioning CI.
The governing FAIL asked for a non-skipping external-interface gate in committed
CI. That is not implementable here, measured rather than assumed: `agy` is a
Mach-O arm64 executable, version 1.1.7, at ~/.local/bin/agy, and this repository
carries no pip entry, npm package, brew formula, download URL or version pin for
it. CI already runs macos-latest, so architecture was never the blocker;
distribution is. Provisioning would mean introducing a download source, which is
a supply-chain decision and not one to take inside a test fix.

So the gate moved to where the binary is guaranteed instead of hoped for.
`harness_preflight.py` runs on the host that will launch AGY and spend money; if
the binary is absent the binary row already fails and nothing is called ready, so
a passing readiness verdict now implies the parity comparison ran, and it runs
before spend rather than after a merge. Only declared-minus-defined is treated as
a defect: a CLI defining more than the launcher uses is ordinary, and the short
aliases -c, -i and -p are exactly that, while a launcher declaring a dropped flag
is a seat that never starts. Parity holds on the installed 1.1.7 — sixteen
declared flags, all defined.

`_agy_defined_flags` separates None from the empty set, because an empty parse
would mark every declared flag undefined and turn one broken invocation into a
flood of false failures. Both fail, for different stated reasons.

CI still covers the logic: the parse is driven against a captured help shape and
the comparison against a stubbed flag set. The four live-CLI tests in
tests/unit/test_agy_seat_launcher.py still skip where AGY is absent, and that is
now honest rather than a hole, because the same interface is enforced
pre-dispatch and unskippably. They are untouched by this range.

The third commit corrects a false comment found while doing this, not reported by
any review. The text above `AGY_CLI_FLAGS` claimed the emitted argv is checked
against the set and the set against `agy --help`. The second half stopped being
true when the snapshot test that performed it was deleted; the superseding parse
probe skips wherever AGY is absent. The comment now names both checks, says where
each lives, and records that the claim had outlived its mechanism.

Non-vacuity, each mutation restored from a byte snapshot with sha256 verified
equal afterward, and each failing the test written for it:

  main ignores a failed AGY binary row     -> fails  (was green)
  early return after the first grant       -> fails  (was green)
  _binary drops the antigravity fallback   -> fails  (was green)
  parity row removed                       -> 4 fail
  unreadable help reported as clean        -> fails
  parity compared in the wrong direction   -> fails
  empty parse treated as an answer         -> fails

Evidence. Preflight module 16 passed both with AGY on PATH and with ~/.local/bin
removed. Full unit suite with AGY absent 1216 passed, 4 skipped, 0 failed; with
AGY present 1228 passed. scripts/ci_smoke.py exit 0. Run against the real CLI,
`harness_preflight.py agy` reports `declared flags all defined by the installed
CLI`; with AGY absent it reports NOT READY and exits nonzero.

Carried rather than closed. The four live-CLI skips remain skips. Provisioning AGY
in CI remains open and needs a distribution channel this repository does not have;
the user was asked and chose pre-dispatch enforcement over supplying one.

## Abuse Class Assessment

- - Gate that cannot run reading as a gate that passed: the parity row is emitted only when the binary is present, and when it is absent the binary row already fails, so no path reports ready without the comparison having run. A mutation removing the parity row fails four tests, and one asserting the passing parity row is required for readiness is among them.
- Unanswered treated as agreement: `_agy_defined_flags` returns None for an unreadable or empty help text, and both None and a dropped flag produce a failing row with distinct wording. Mutations making None read clean, and making an empty parse an answer, each fail.
- Wrong comparison direction: only declared-minus-defined is a defect, and a mutation inverting it fails, so a CLI that merely defines more than the launcher uses cannot be reported as drift while a launcher declaring a dropped flag cannot pass.
- New host dependence introduced by the gate: the gate itself needs the binary, so every test of it stubs either `shutil.which` or `_agy_defined_flags`, and the whole module is verified both with AGY on PATH and with it removed. The launcher is imported by preflight, which runs both as a script with scripts/ on sys.path[0] and under the tests' pythonpath; both invocation modes are exercised.
- Import-time coupling: preflight now imports the launcher for one constant. The launcher's module level defines constants only and starts nothing, and `harness_preflight.py agy` was run directly to confirm the script path still works rather than only the imported path.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T18-13-10Z-operator-to-director-verify-addendum.md@ac54cfda45c691bedb196f2ed0dc401a83bd7897
- sha256:857fca8519dd8a0a18357f539d1215fe58348671368a89c9bf11eaeef9ee3e29

Cursor at send: 0
