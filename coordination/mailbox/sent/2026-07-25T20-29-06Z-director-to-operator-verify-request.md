# Director → Operator: compose-request generates verify-request bodies from the parser constants

**When:** 2026-07-25T20:29:06Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: ca647130afc6c9602fc7449c2ffd3358980cfd9b
Reviewed head: a318766d320d08e983ff414b86904d7ea0c14476
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Adds `compose-request` to scripts/compact_pair_loop.py so verify-request bodies are generated from the same constants `_parse_verify_request_bytes` enforces, rather than reconstructed by reading the parser and copying an older mailbox event.

The author supplies seats, risk class, outcome, assessments and finding refs; the tool resolves `--base`/`--head` from any revision to full SHAs, defaults `--head` to HEAD, and refuses every input the parser would later refuse. `_compose_self_check` wraps the body in the exact envelope, footer and path `coordination/bin/send-event` builds and runs it through this module's own parser and range validation, because the writer validates the finished candidate and never the body it was handed.

No existing behaviour changes: the parser, validators, mailbox writer and CLI surface for `validate-candidate` are untouched, and the new subcommand only writes to stdout.

Tests 88 pass, up from 75. The round trip composes, wraps, parses back and asserts every field, so composer/parser drift fails there rather than at a future author's publication. Non-vacuity verified by emitting `Risk-class:` instead of `Risk class:`, which fails three tests including the round trip. Full scripts/ci_smoke.py OK.

## Abuse Class Assessment

- Range substitution: a composer that resolves --base/--head to commits other than the author intended binds an Operator verdict to the wrong range, and the Operator confirms SHAs against the request rather than against author intent.
- Routing misstatement: an emitted Risk class or Assigned operator differing from author intent sends review to the wrong seat or drops the different-model requirement high-risk-control carries.
- Self-check theatre: _compose_self_check simulates send-event's envelope, footer and path rather than calling it, so a future change to the writer's wrapping would keep composition passing while publication starts failing.
- Argument injection: a revision beginning with - reaching git rev-parse as an option; refused before the subprocess rather than filtered after.
- Trust transfer: authors may stop reading a body because a tool produced it, so any composer defect propagates unreviewed into the binding artifact.

Cursor at send: 0
