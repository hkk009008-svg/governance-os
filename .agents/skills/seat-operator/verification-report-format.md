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

Verification schema: lane-v-report/v3
Verification mode: independent-lane-v
Verification harness: lane-v:independent-verifier
Verification task ID: <canonical UUID>
Scope authority: coordination/verification/scopes/<task-id>.json@sha256:<64-hex>
Trigger identity: <shipping-commit:<sha> | verify-request:<sha>:<path>>
Reviewed head: <40-lowercase-sha>
Reviewed base: <40-lowercase-sha>
Review profile: independent-lane-v
Reviewer identity: <operator | operator2; must equal the envelope sender>

## Findings
1. <severity> — `path/file.py:line` — <what + why> — <disposition>
2. ...

## Scope-match (CRITICAL cross-cutting only)
Landed diff matches the co-signed R-BRIEF scope (defect <id>): <yes/where it drifts>.

## Exact Next Trigger
<one exact next owner/action or `none — verification loop closed`>

Cursor at send: <ISO>                                              ← footer (auto)
```

The trigger-bound descriptor supplies scope; callers do not repeat requirements,
allowed paths, or verification commands. Lane V is provider-neutral and runs no
provider command. Record the independent verifier seat in `Reviewer identity`.

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

## Worked independent Lane V fragment (real shape)

```
VERDICT: GO

## Evidence
$ grep -rn 'self\.spent_usd\s*=' --include='*.py' . | grep -v /tests/
→ exactly cost_tracker.py:224 (single chokepoint — log() delegates here)

## Verification Attestation

Verification schema: lane-v-report/v3
Verification mode: independent-lane-v
Verification harness: lane-v:independent-verifier
Verification task ID: 11111111-2222-4333-8444-555555555555
Scope authority: coordination/verification/scopes/11111111-2222-4333-8444-555555555555.json@sha256:<64-hex>
Trigger identity: shipping-commit:<40-lowercase-sha>
Reviewed head: <40-lowercase-sha>
Reviewed base: <40-lowercase-sha>
Review profile: independent-lane-v
Reviewer identity: operator

## Findings
1. INFORMATIONAL — `cost_tracker.py:224` — increment sits at the log() chokepoint;
   both log_api/log_llm delegate there → no double-count. — record only.

## Exact Next Trigger
none — verification loop closed
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
