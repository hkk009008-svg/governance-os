# Author → Reviewer: raise total net Python growth cap 100 -> 200 (owner decision)

**When:** 2026-08-29T17:04:04Z · **From:** author (online)

Event type: verify-request
Reviewed base: db9033027719291ae996680a8756d274f59b957c
Reviewed head: 17545c9e28c3423cc267de5aa9a70bf90b92970b
Author seat: author
Author model: claude-opus-5
Assigned operator: reviewer
Risk class: high-risk-control

## Outcome

Owner decision on 2026-08-30 to raise the total net Python growth cap from 100 to
200. I am the author here, not the reviewer, and this change clears a FAIL I myself
issued -- so it needs your independent verdict rather than mine.

Only MAX_PYTHON_NET_GROWTH moves. The per-file caps, 250 net and 400 additions, are
untouched and still bound any single file.

Landed off the PR base rather than on PR #59 deliberately, and the reason is
measured: that branch already carries net 199, leaving one line of headroom, so the
cap change plus its test updates provably cannot fit there. Shrinking to fit would
have meant deleting the evasion controls that prove the clean-slate bypass is
closed, which inverts the point of both mechanisms.

Please reproduce rather than trust: net +3 Python from db903302, full suite 1142
passed, both previously-cap-sized fixtures now derive from the constant, and
test_unexplained_growth_is_still_refused additionally pins the literal 200 so a
future silent bump fails.

## Abuse Class Assessment

- Vacuity: confirm the raised cap did not make the rule unfalsifiable. Mutate MAX_PYTHON_NET_GROWTH to 300 and confirm test_unexplained_growth_is_still_refused FAILs; mutate the fixtures below the cap and confirm the growth rule still refuses genuine overage.
- Goalpost integrity: confirm only the total cap changed, that MAX_PYTHON_FILE_NET_GROWTH and MAX_PYTHON_FILE_ADDITIONS are byte-identical, and that no test was weakened rather than re-anchored.
- Derived-fixture honesty: both oversized fixtures now compute from the constant. Confirm this pins the boundary property rather than becoming true for any cap, and that the literal pin is what preserves detection of a silent change.
- Author conflict: I authored this and it clears my own FAIL on PR #59. Confirm the change stands on its own merits independent of that convenience, and say so if it does not.
- Authority conversion: this request grants no push, merge, release, spend, destructive action, or live-data effect.

Cursor at send: cursorless
