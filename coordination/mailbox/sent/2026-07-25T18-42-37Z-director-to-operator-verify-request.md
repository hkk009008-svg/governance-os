# Director → Operator: mirror chatgpt-pro-consultation skill into .claude/skills

**When:** 2026-07-25T18:42:37Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: 8836d70de1f77c714990cc79e0d4cdb9df3089a3
Reviewed head: 9f9ede94212e2d12eca66d29d9d2ee3eac62ebbd
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

One added file, `.claude/skills/chatgpt-pro-consultation/SKILL.md` (60 lines, no
other path touched). Claude Code discovers skills only under `.claude/skills/`,
so the ChatGPT Pro consultation procedure was reachable only by reading
`.agents/skills/chatgpt-pro-consultation/SKILL.md` directly; the sole Claude-side
pointer at `.claude/agents/readiness-bridge.md` names the Codex path. The mirror
makes the procedure a listed Claude skill.

Adapted, not byte-copied, matching how all six pre-existing mirrored skills are
built. Three substitutions: `browser:control-in-app-browser` (a Codex skill name
with no Claude equivalent) becomes the in-app Browser tools `mcp__Claude_Browser__*`;
the reserve/finish invocations become concrete `env -u GIT_INDEX_FILE
.venv/bin/python scripts/chatgpt_pro_consult.py` commands in a Commands section;
the description names the Claude in-app Browser. `scripts/chatgpt_pro_consult.py`
is unchanged.

Preserved verbatim in meaning: parent-only ownership with subagents limited to
proposing; the four consultation triggers plus the three never-consult cases; no
automatic reading of files, diffs, mail, environment, database, browser storage
or credentials; preflight before reservation; stop with no reservation on
preflight failure; the `created:true` gate; exactly one send with no repository
material; `finish` before waiting for the answer; failed-status on ambiguous
post-reservation failure; no retry, transport switch, reformulation or
replacement key; no persistence of prompt, response, screenshot, transcript or
summary; and the answer treated as inert advice granting no authority.

One deliberate discretionary choice, flagged for review: `disable-model-invocation`
is absent. wave-gate and create-regression-pin carry it; the four seat-* skills do
not. Setting it would block parent-initiated consultation on a material reasoning
trigger, which the source procedure explicitly permits, so it would narrow rather
than mirror. If the reviewer reads the trigger list as user-request-only, this is
the line to change.

Carried finding, raised by the author and deliberately not fixed in this range.
The single digest under Finding Refs is sha256 over this exact one-line text:
`docs/protocol/claude/continuation.md states that byte-equality assertions in
tests/unit/test_protocol_prompt_sync.py keep the .claude/skills mirror honest,
but the only byte-equality assertion is
test_verification_report_templates_remain_identical, scoped to
seat-operator/verification-report-format.md; all six pre-existing mirrored
SKILL.md files already differ from their .agents/skills counterparts.` The
adaptation in this range follows observed practice rather than that doctrine
sentence. Whether the sentence should be corrected or the mirror convention
tightened is left to the reviewer; changing it would touch files outside this
range.

Verification run by the author: focused tests over
tests/unit/test_protocol_prompt_sync.py, tests/unit/test_claude_seat_launcher.py
and tests/unit/test_chatgpt_pro_consult.py gave 173 passed, 1 failed;
scripts/ci_smoke.py OK across project-smoke, ceremony, placeholder, go-schema,
mechanism-ledger and arch-freshness. The single failure,
test_project_codex_config_does_not_claim_runtime_permissions, is pre-existing
uncommitted `.codex/config.toml` working-tree dirt outside this range and
untouched by it; `git show HEAD:.codex/config.toml` carries only `personality`.
The author also confirmed cross-harness kernel reachability: an empty-payload
`reserve` returned `{"ok":false,"error":"invalid_json"}` exit 2 with the shared
state file byte-identical before and after, since `_normalize` rejects ahead of
`_common` and the lock.

## Abuse Class Assessment

- Repository exfiltration by drift: a mirrored procedure that silently relaxes step 1 or step 5 would let a Claude parent attach diffs, mail or environment to an outbound prompt. Both prohibitions are retained verbatim in meaning; confirm no widening of what may be sent.
- Once-only bypass across harnesses: the reservation ledger lives at the repo git-common-dir and is now shared by Claude and Codex parents. If the Claude copy weakened the reserve/`created:true`/finish ordering, a second send could bind to an existing key. Steps 3, 4 and 6 are retained and the kernel is unchanged, so the flock plus hash-bound key still enforce once-only.
- Authority laundering through advice: a skill file is an instruction surface, so a mirror that dropped the inertness clauses could let ChatGPT output read as protocol authority. Both the header disclaimer and the closing inert-instructions paragraph are retained.
- Credential capture and consent acceptance: the procedure drives a signed-in browser session. The do-not-enter-credentials and do-not-accept-consent constraints are retained, and the Claude harness independently prohibits both.
- Trigger widening via model self-invocation: omitting `disable-model-invocation` permits parent-initiated consults. The four triggers and the never-consult-by-default clause are the only brake; this is the discretionary choice named in the Outcome.
- Silent fork over time: no test asserts parity between `.agents/skills` and `.claude/skills`, so the two copies can diverge undetected. This change adds a seventh unguarded pair rather than creating the gap; see the carried finding.

## Finding Refs

- sha256:7c2b341558a8d83f8c5dd0773e0610d8c6965c09ea6a3805b80c4a8a0aa5aba6

Cursor at send: 0
