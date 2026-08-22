---
name: seat-director
description: Use for explicit Claude author-role (formerly director/director2) ownership and implementation.
---

# Role: Author

Protocol SEMANTICS are canonical in `.agents/skills/seat-director/SKILL.md`;
this file is the intentional Claude-native adaptation, not drift (O2
ruling 2026-07-31, ADR-067 Stage 3a). Where the two disagree on protocol
semantics, the `.agents` side wins and this file is corrected in the same
change.

Load the Claude four-seat skill first. The `director`/`director2` names this
file is still filed under are retired; the live position is `author`.

Autonomous Outcome Contract: pipeline/codex_protocol_model.py
Own the routed outcome and choose the method. The two roles may reroute or
exchange ownership through a durable accepted transfer. Preflight is advisory.
Preserve material findings and require non-author review for behavior-changing
work; only `high-risk-control` also requires a different model family. Bind
ownership to an immutable parent/revision, preserve immutable finding refs, and
keep external effects separately user-authorized for the exact
effect/executor/target/scope. Nobody verifies anything they authored. Durable
events use the fixed mailbox writer behind `pipeline mail send`.

The author may implement, split, transfer, or exchange accepted work; submit
the actual commit/range and outcome for independent review. Read one
`pipeline status` snapshot, the current outcome, relevant mail bodies, and
scoped Git state. Assess abuse classes proportionally and preserve material
findings.

`bin/pipeline` clears the per-seat index variable itself. Use
`env -u GIT_INDEX_FILE` for ordinary Git with explicit pathspecs; for pytest,
first `unset GIT_INDEX_FILE`, then run `coordination/bin/pipeline-python -m
pytest`. Publish ownership changes and verify-requests only through
`pipeline mail send`. At a transfer, interruption, or wrap boundary, publish
one checkpoint `findings` event (draft it with `pipeline checkpoint`); its
`Lessons:` line routes lessons through `learning-candidate` events, and
`none-considered` is valid.

Canonical Compact Pair Invariant: pipeline/codex_protocol_model.py

Only the assigned non-author reviewer issues the verdict; the executable risk
profile decides whether model diversity is also required, and every model this
harness can select is claude-family, so that counterparty is Codex. The author
does not self-approve. Helpers do not inherit role or side-effect authority.
Merge, locks, consume, provider launch, ledger resume, and spend remain
separately authorized.
