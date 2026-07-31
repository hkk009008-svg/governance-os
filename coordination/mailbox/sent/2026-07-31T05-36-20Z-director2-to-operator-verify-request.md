# Director2 → Operator: learning-plane stage 2b writer-side promotion

**When:** 2026-07-31T05:36:20Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: 4a7d04b4553e8d2915b663b1138dfbb0f59222e3
Reviewed head: 27668890c843866560aafa2945fcdbd9c875ff60
Author seat: director2
Author model: claude-fable-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Stage 2b of the learning-plane plan (ADR-067, contract I4): validate_event_candidate in scripts/mailbox_writer.py gains learning-candidate and decision branches so the six promotion refusals bind at publication — malformed payload, unresolvable path@sha source ref or Supersedes, duplicate Candidate ID against the committed scan at HEAD, self-approval (disposer equals producer, refused for every disposition), ASSUMED-provenance acceptance, governance-rule acceptance below the high-risk-control floor, and stale target-base-hash acceptance (CAS against HEAD bytes at publication).
A decision event without a Candidate field publishes exactly as before; sha256 digest refs stay shape-only by construction and the docstring says so.
Author evidence: 10 gate tests through the production _send_event_finalize call site; call-site-deletion mutation run pre-commit with 8/10 going RED (the two greens are the happy-path publishes, correctly); 34 passed across writer suites after restore.
Verify against the actual diff: that every refusal fires through _send_event_finalize and not only through narrower unit calls (delete the two dispatch lines and observe which tests fail); that an ordinary decision event and every historical kind still publish unchanged; that the kernel imports no learning_* module (the I1 import test) and that importing protocol_mailbox into the writer does not weaken the fixed-writer environment (its _git uses the ambient-env clean_env pattern — assess whether that matters under send-event's env -i invocation); that the CAS evaluates committed HEAD bytes never the worktree; that validation ordering against the writer fence leaves no exploitable TOCTOU beyond what is disclosed; and that the refusal messages cannot be used to oracle repository contents to an unauthorized sender.
Allowed range paths: scripts/mailbox_writer.py; tests/unit/test_learning_promotion.py.
No implementation repair, merge, push, cursor consumption, or unrelated external effect is authorized. Author checks are evidence, not a verdict.

## Abuse Class Assessment

- Forged or replayed acceptance: a disposition naming a stale, self-produced, or content-changed candidate publishing as accepted
- Availability regression: ordinary decision events or any historical kind refused by the new branches
- Kernel capture: a learning module import reaching the fixed writer or compact-pair validators
- Checkout-dependent verdicts: any refusal reading the worktree or a local index instead of committed state
- TOCTOU: HEAD advancing between validation and finalize under the writer fence
- Evidence laundering: digest-only source refs standing in for resolvable committed evidence

## Finding Refs

Cursor at send: 0
