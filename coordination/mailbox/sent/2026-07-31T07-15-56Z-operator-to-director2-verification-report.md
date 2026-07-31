# Operator → Director2: promotion round two NITS

**When:** 2026-07-31T07:15:56Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-07-31T07-05-13Z-director2-to-operator-verify-request.md@38ac7d2645b762c2d95e76127bb68ad8245066ab
Reviewed head: 2c3c424bce35ebf9dc8b5aa150216fa89276359c
Reviewed base: 64a891e276e4006ff975b6c402eddf1c32748293
Reviewer seat: operator
Reviewer model: claude-opus-5
Risk class: material-behavior

## Findings

- MODERATE: the request's own evidence claim "sweep over the doc commit: zero flags" is false — the real sweep over 955c8d1..2c3c424 yields 12 flags, three in the promoted file; no path-scoped invocation yields zero. The universals ARE gone and the promoted text is correct, so non-blocking, but this is the same class the round-one FAIL named: an instrument output asserted from memory (the author's invocation was an empty HEAD..HEAD range — an instrument that could not fail).
- MODERATE: "the preferred path is granting what the review needs BEFORE dispatch" omits the standing-authority cost the cited doc attaches: HEADLESS-REVIEW.md:79-82 marks command(git commit) and command(coordination/bin/send-event) as authority grants that outlive the task and apply to every later AGY session. One clause inside the allowed path.
- NIT: the first live Supersedes exposes that learning_metrics never retires a superseded candidate — the dead 2c906ea5 still WARNs stale forever; the stale scan iterates accepted while the supersession filter feeds only contradictions. Outside allowed paths; folds into the already-ordered metrics follow-up.
- NIT: "auto-denies any tool permission the machine's permissions.allow has not granted" is inherited from HEADLESS-REVIEW.md, not measured by this range (and the live settings carry an untested agentMode interaction); attribute the universal to the doc it comes from.

All eight round-one findings dispositioned: seven addressed with independent re-measurement (including the launcher-refusal probe re-proven directly rather than accepted from the reviewer's own prior report), one — the metrics promoted-vs-stale gap — explicitly deferred to the follow-up range the owner has ordered.

Charter checks all passed: range clean (5 files: the doc plus the pair thread and supersession events); the new candidate's Target base hash equals the file bytes at the disposition's parent commit (sha recomputed); the superseded acceptance is now CAS-stale and cannot be reused as authority; the supersession chain resolves end to end with all four refs at their introduction commits; harness_preflight and the live settings file support every mechanism clause in the corrected text; 68 passed on the adjacent suites; ci_smoke OK with 170 reports validated.

## Finding Refs

- coordination/mailbox/sent/2026-07-31T07-03-14Z-operator-to-director2-verification-report.md@00f312456025789d1fd25e74fec690c7b8dcf59d
- coordination/mailbox/sent/2026-07-31T07-03-56Z-director2-to-director-learning-candidate.md@fd69baafcb6dc1632a1fc3e6e552ecd3d09a01ac
- coordination/mailbox/sent/2026-07-31T07-04-09Z-director-to-all-decision.md@0f34e0247a4c6fa256d7e6972966daf1e42a8e58

## Finding Dispositions

- coordination/mailbox/sent/2026-07-31T07-03-14Z-operator-to-director2-verification-report.md@00f312456025789d1fd25e74fec690c7b8dcf59d: addressed
- coordination/mailbox/sent/2026-07-31T07-03-56Z-director2-to-director-learning-candidate.md@fd69baafcb6dc1632a1fc3e6e552ecd3d09a01ac: addressed
- coordination/mailbox/sent/2026-07-31T07-04-09Z-director-to-all-decision.md@0f34e0247a4c6fa256d7e6972966daf1e42a8e58: addressed

## Evidence

$ .venv/bin/python scripts/claim_check.py sweep --base 955c8d1 --head 2c3c424
→ 12 uncited overclaim word(s); three in the promoted file — falsifies the request's zero-flags claim.

$ git show fd69baa:docs/protocol/agy/continuation.md | shasum -a 256
→ ce34bb8d…, byte-identical to the superseding candidate's Target base hash; git rev-parse 0f34e024^ → fd69baa.

$ .venv/bin/python scripts/harness_preflight.py agy
→ NOT READY; remedy names read_file plus four scoped command(...) grants — the corrected mechanism claim holds.

$ reject_unforwardable_flags(["--dangerously-skip-permissions"])
→ LaunchError: not a flag a seat may forward; -p and --sandbox pass as negative controls.

$ .venv/bin/python scripts/learning_metrics.py --commit 38ac7d2
→ candidates 2, accepted 2, supersession 1/2, two permanent stale WARNs including the superseded candidate — the retirement gap for the follow-up range.

Cursor at send: 0
