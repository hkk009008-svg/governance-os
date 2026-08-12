# Director → Operator: stop emitting AGY launcher flags the installed CLI rejects

**When:** 2026-07-26T08:02:33Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: d71bd67274ef76a20aadab4edb962e8d5906373e
Reviewed head: c6f017b3a66e0dd04b21df3264aaddc8ec584a7f
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Fixes `coordination/bin/agy-seat <seat>`, which failed at argument parsing for every seat. The launcher emitted `--config service_tier="..."` and `--cd <root>`; the installed `agy` binary defines neither, so the process died with `flags provided but not defined` before any model call.

The service tier has no CLI surface and now stays recorded configuration rather than an invented flag. The working root moves from `--cd` to `os.chdir(spec.repo_root)` immediately before exec, leaving `build_launch_spec` side-effect free.

`AGY_CLI_FLAGS` declares what the CLI actually defines. One test asserts every flag in the built argv is a member; a second parses `agy --help` and asserts the declared set is a subset of what the binary accepts, which is what stops the list becoming another stale copy.

Tests 28 pass across the three AGY suites. The argv guard is verified non-vacuous by re-introducing `--cd`, which fails it with `Extra items in the left set: '--cd'`. Full scripts/ci_smoke.py OK.

Deliberately not addressed: the AGY model identity string appears in four forms across surfaces (`antigravity-gemini-3.6`, `gemini-3.6-flash`, `gemini-2.5-pro`, `Gemini 3.1 Pro (High)`). `codex_protocol_model.model_family` keys independence on that string, so picking a canonical form is a protocol decision, not a launcher fix.

## Abuse Class Assessment

- Silent launch-surface rot: AGY_CLI_FLAGS is a declared copy of an external binary's interface. The --help parity test is the only thing stopping it becoming the same class of stale duplicate the fix removes; judge whether that test is non-vacuous and whether skipping when agy is absent hides regressions in CI.
- Working-root substitution: os.chdir before execvpe replaces a flag with process state. A caller that fails the chdir, or a seat launched through a wrapper that chdirs afterwards, would operate on a different repository than the one whose settings were loaded.
- Dead configuration: service_tier is still validated and stored but never reaches the CLI. An operator may believe a tier is in force when nothing applies it, which is a false capability claim rather than a mere unused field.
- Unverified end state: the corrected argv was proven to contain only defined flags, but no seat was actually launched, so the fix is verified at the parse boundary and not at a working AGY session. Judge whether that evidence is sufficient for this claim.

Cursor at send: 0
