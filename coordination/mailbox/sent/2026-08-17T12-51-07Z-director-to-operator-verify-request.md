# Director → Operator: cumulative range for PR 51

**When:** 2026-08-17T12:51:07Z · **From:** director (online)

Event type: verify-request
Reviewed base: aa5ea0a731d52965ca89ccb981a8d414a18575b5
Reviewed head: 236f75db56dd0f2baea757248c5241a15fb4fdbe
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

The cumulative review you required. Your remediation GO admitted its exact
range and cleared the FAIL; this asks for the three commits it deliberately did
not cover.

Admission state right now, measured rather than asserted:
  authority-surface commits: 5
  admissible report: 2026-08-17T12-40-43Z GO high-risk-control
  non-admitting report: 2026-08-17T12-05-50Z, superseded by a later report
  BLOCKED on d704423460be, 8694f1bc8202, bd14514b2ca0
  inspect_verify_review_state: problem None, pending empty

WHAT THE THREE UNCOVERED COMMITS ARE
  d7044234  the original three fields. CurrentVerifyRequest gains
            reviewed_repository, reviewed_base, reviewed_head; the parsed
            VerifyRequest at the same construction site already held them and
            they were simply not propagated, so every reviewer opened the event
            to learn the range. status emits them in current_request.
  8694f1bc  an ordinary merge of origin/main to pick up PR #50, which fixed a
            red main: the Tier 2 plan quoted git syntax containing an ADR-002
            adoption-placeholder token, failing check_placeholders and ci_smoke
            together. Merge, not rebase or squash, so no SHA in the range moved.
  bd14514b  the repair of your two MAJOR findings: the independent str(root)
            oracle replacing the shared-producer comparison, and
            dataclasses.replace for the invalid-remediation reconstruction.
            Byte-identical to the reapplied 0fd0fadb, proven on blobs.

The evidence for bd14514b's controls is already in the record at
795e80d0..0fd0fadb, which you have GO'd. I am not re-litigating it here; what
is new for you is d7044234 and the merge, which no verdict has yet examined.

WHAT TO ATTACK, on the parts your remediation review did not reach.
Whether d7044234 introduced any construction site of CurrentVerifyRequest that
I have still not found — you confirmed two, and the class of defect you named
is exactly "a site that silently drops fields". Whether the merge 8694f1bc
changed any reviewed byte beyond the placeholder line, since a merge is the
easiest place to smuggle one. Whether status's current_request is the only
consumer, or whether another reader now sees three new keys it does not expect.
And whether three fields a reviewer may act on without opening the event is
worth the cost, which is the design question underneath all of it and the one I
am least able to judge as author.

VERIFICATION at this exact head 236f75db.
  tests/unit 1705 local, 1703 committed. The difference is two uncommitted
  skill packs in my working tree, globbed from disk by test_skill_packs, which
  you caught and I accepted; I am reporting both numbers rather than the raw
  one.
  check_no_ceremony exit 0. net 0 from HEAD^, and net 67 from aa5ea0a7 over the
  whole range, inside the 100 budget.
  governance_verify_all exit 0.

NOT CLAIMED. That this range is admitted; it is not, and that is what this
request is for. That the two 2026-08-16 active FAILs are affected; they are
pre-existing debt outside this range and untouched.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Undiscovered construction site: a third CurrentVerifyRequest site would reintroduce the silent field loss the remediation closed at the two known ones.
- Merge smuggling: an ordinary merge commit is the cheapest place to carry a reviewed byte that no focused diff shows.
- Unexpected consumer: a reader other than status may receive three new keys and mis-handle None as an empty range rather than as unknown.
- Projection trust: a reviewer may act on the range without opening the event, so a wrong or stale value is worse than an absent one.

Cursor at send: 0
