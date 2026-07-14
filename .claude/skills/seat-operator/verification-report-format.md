# verification-report — format & severity reference

Read this when you are about to emit a `verification-report` and want the
field structure and severity vocabulary in front of you. The report is the
operator's load-bearing artifact: it is the *only* thing that moves a fix to
`verified` (guarantee #3), so its shape and evidence matter as much as the
verdict.

## Emit it as an artifact, never as chat (Rule #19)

A binding signal is a mailbox file, not a sentence in the conversation. Generate
it with the existing tool so the envelope/cursor are correct:

```bash
coordination/bin/send-event <from> <to> verification-report "<subject line>" <<'EOF'
<body — see skeleton below>
EOF
```

`send-event` writes the H1 header, the `**When:** … · **From:** …` envelope,
and the `Cursor at send:` footer automatically. For a `verification-report`,
the kind is carried by `…-<from>-to-<to>-verification-report.md`; the separate
verify-request trigger contract below additionally requires its exact in-body
`Event type: verify-request` authority field.

## Lane V trigger authority

A verify-request trigger is a canonical committed sent-mailbox event strictly
after the reviewed HEAD with exactly one `Event type: verify-request`, one
`Reviewed head: <40-lowercase-hex>`, one
`Reviewed base: <40-lowercase-hex>`, and one
`Lane-V-Scope: coordination/verification/scopes/<uuid>.json@sha256:<64-lowercase-hex>`
whose values agree with the committed descriptor and canonical
filename/envelope. A shipping trigger commit equals the reviewed HEAD, its
subject begins `feat`, `fix`, or `refactor`, and exactly one identical descriptor
reference in the terminal Git trailer block supplies its `Lane-V-Scope`.
Missing, duplicated, abbreviated, uppercase, misplaced, uncommitted, stale, or
mismatched authority is not a trigger: stop with a blocker, do not reconstruct
missing fields, and do not fall back to the other trigger kind.

## Body skeleton

```
# <From> → <To>: Lane V verification report — commit `<40-lowercase-sha>`
**When:** <ISO> · **From:** <seat> (online)                       ← envelope (auto)

VERDICT: GO                                                        ← exact: GO / NITS / FAIL

## Evidence            ← R-EVIDENCE: the command AND its output, not a claim
$ <command you ran>
→ <result>

## Verification Attestation

Verification schema: lane-v-report/v2
Verification mode: <codex-lane-v | claude-lane-v>
Verification harness: <codex:lane-v-verifier | claude:lane-v-verifier>
Verification task ID: <canonical UUID>
Scope authority: coordination/verification/scopes/<task-id>.json@sha256:<64-hex>
Trigger identity: <shipping-commit:<sha> | verify-request:<sha>:<path>>
Reviewed head: <40-lowercase-sha>
Reviewed base: <40-lowercase-sha>
Review profile: <codex-lane-v | not-applicable>
Authorization identity: <stored identity | not-applicable>
Opus receipt ID: <opr1:64-hex | not-applicable>
Opus scope digest: <sha256:64-hex | not-applicable>
Cross-model review: <pass | issues | unavailable | not-applicable>
Effective Opus model: <stored model | unavailable | not-applicable>
Opus finding dispositions: <exact reconcile field | not-applicable>
Reconciliation guard: <exact reconcile field | not-applicable>
Degraded reason: <exact reconcile field | not-applicable>

## Findings
1. <severity> — `path/file.py:line` — <what + why> — <disposition>
2. ...

## Scope-match (CRITICAL cross-cutting only)
Landed diff matches the co-signed R-BRIEF scope (defect <id>): <yes/where it drifts>.

## Exact Next Trigger
<one exact next owner/action or `none — verification loop closed`>

Cursor at send: <ISO>                                              ← footer (auto)
```

For Codex Lane V, obtain the nine Opus/reconciliation lines from the bridge's
stored receipt. The trigger-bound descriptor supplies scope; callers do not
repeat requirements, allowed paths, or verification commands:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py review \
  --repo-root . --head "$HEAD" --base "$BASE" --review-profile codex-lane-v \
  --transport-profile anthropic-claude-existing-session-v1 \
  --shipping-commit "$HEAD"
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py review \
  --repo-root . --head "$HEAD" --base "$BASE" --review-profile codex-lane-v \
  --transport-profile anthropic-claude-existing-session-v1 \
  --verify-request-commit "$TRIGGER_COMMIT" \
  --verify-request-path "$TRIGGER_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py reconcile \
  --repo-root . --receipt-id "$RECEIPT_ID" --head "$HEAD" --base "$BASE" \
  --codex-verdict GO
```

Finding dispositions and evidence remain repeated `--disposition ID=value`
and `--evidence ID=value` flags. Copy the returned `report_fields` values
exactly. For non-Codex Lane V, use `not-applicable` for every attestation line
from `Review profile` through `Degraded reason`; never invent an Opus receipt.

## Verdict vocabulary

| Verdict | Meaning | What it triggers |
|---|---|---|
| **GO** | Diff read, independently verified, ships. | Coordinator may set `verified`; on a cross-cutting row, delete the lock in **this same commit** (§6b). |
| **NITS** | Cosmetic concerns only — but "cosmetic" is a *claim about scope*. | Fixer addresses; you **re-read the nit-fix diff** (`git show <sha>` yourself) before upgrading NITS→GO. Never self-upgrade on the fixer's word. |
| **FAIL** | Blocking defect, scope drift vs the co-signed brief, or guarantee breach. | Fix stays unverified; lock retained. After **3 consecutive FAILs** the holder releases (anti-hostage). |

## Finding-severity vocabulary (Rule #15 disposition advisory)

| Severity | Disposition guidance |
|---|---|
| **CRITICAL** | Standalone fix preferred — do not fold into unrelated work. |
| **IMPORTANT** | Fix this cycle; fold-in acceptable if tightly scoped. |
| **MINOR** | Fold-in or advisory. |
| **INFORMATIONAL** | No-action acceptable; record for awareness. |

## Worked Codex fragment (real shape)

```
VERDICT: GO

## Evidence
$ grep -rn 'self\.spent_usd\s*=' --include='*.py' . | grep -v /tests/
→ exactly cost_tracker.py:224 (single chokepoint — log() delegates here)

## Verification Attestation

Verification schema: lane-v-report/v2
Verification mode: codex-lane-v
Verification harness: codex:lane-v-verifier
Verification task ID: 11111111-2222-4333-8444-555555555555
Scope authority: coordination/verification/scopes/11111111-2222-4333-8444-555555555555.json@sha256:<64-hex>
Trigger identity: shipping-commit:<40-lowercase-sha>
Reviewed head: <40-lowercase-sha>
Reviewed base: <40-lowercase-sha>
Review profile: codex-lane-v
Authorization identity: standing-policy:codex-lane-v-opus-v1
Opus receipt ID: opr1:<64-hex>
Opus scope digest: sha256:<64-hex>
Cross-model review: pass
Effective Opus model: claude-opus-4-7
Opus finding dispositions: none
Reconciliation guard: {"digest":"sha256:<64-hex>","go_allowed":true}
Degraded reason: none

## Findings
1. INFORMATIONAL — `cost_tracker.py:224` — increment sits at the log() chokepoint;
   both log_api/log_llm delegate there → no double-count. — record only.

## Exact Next Trigger
none — verification loop closed
```

## Worked non-Codex attestation block

```
## Verification Attestation

Verification schema: lane-v-report/v2
Verification mode: claude-lane-v
Verification harness: claude:lane-v-verifier
Verification task ID: 11111111-2222-4333-8444-555555555555
Scope authority: coordination/verification/scopes/11111111-2222-4333-8444-555555555555.json@sha256:<64-hex>
Trigger identity: shipping-commit:<40-lowercase-sha>
Reviewed head: <40-lowercase-sha>
Reviewed base: <40-lowercase-sha>
Review profile: not-applicable
Authorization identity: not-applicable
Opus receipt ID: not-applicable
Opus scope digest: not-applicable
Cross-model review: not-applicable
Effective Opus model: not-applicable
Opus finding dispositions: not-applicable
Reconciliation guard: not-applicable
Degraded reason: not-applicable
```

## Three reminders that ride every report

- **Verdict-ahead-of-report (Rule #21):** if a peer is blocked on a *billed*
  resource (pod running), send the dispositive **GO/NO-GO as its own event
  first**; the full evidence report follows. Don't let billing burn while you
  prose-write.
- **Lock atomicity (§6b):** on GO for a cross-cutting row, `git rm` the lock and
  stage this report (`send-event`), then commit **both in one explicit-pathspec
  commit** — `release-lock` makes a *separate* unlock commit and does NOT satisfy
  "same commit as GO."
- **Correct event kind:** a post-implementation hand-off is `verification-report`
  (a status signal), never `dispatch-claim` (a *pre*-implementation intent signal).
