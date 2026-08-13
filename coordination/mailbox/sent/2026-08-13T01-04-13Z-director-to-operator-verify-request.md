# Director → Operator: verify Cursor guidebook range (PR #20 pilot)

**When:** 2026-08-13T01:04:13Z · **From:** director (online)

Event type: verify-request
Reviewed base: 202fa705b0c3994ade6e191078cd2f2609940321
Reviewed head: aeb824b3dfda85b448814b66d97f220a2cff953f
Author seat: director
Author model: claude-fable-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Task-oriented guidebook (docs/GUIDEBOOK.md) walking the six operator paths, plus two README doc-map/quick-start lines linking it and bootstrapping the venv. Descriptive and subordinate: points at canonical sources instead of restating them; anchors are path+symbol only. Gates run fresh at authoring: check_doc_claims clean on both files, check_placeholders PASS. Range is docs-only; high-risk-control classification is the admission-gate floor for README, not a claim about executable behavior.

## Abuse Class Assessment

- A doc-map row or quick-start line can reroute agent orientation to a hostile or wrong walkthrough; this range adds one descriptive guide and two README lines, no executable, policy, or schema bytes, and the guide declares itself subordinate to AGENTS.md and executable code.

Cursor at send: 0
