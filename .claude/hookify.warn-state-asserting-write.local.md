---
name: warn-state-asserting-write
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: (docs/HANDOFF-|coordination/mailbox/sent/|DECISIONS\.md|ARCHITECTURE\.md|OPERATIONS\.md|STRATEGIC_REVIEW)
---

📌 **State-asserting / director-voice write — run the preconditions first**

You're writing a handoff, mailbox event, ADR, or truth/strategic doc. Before this lands:

- **Rule #4 (pre-Write gate):** run `git log --oneline -5` + check `coordination/mailbox/sent/` for events newer than your write-start. Use the *just-observed* HEAD in the content; if state moved during the write, add a race-ack body (Rule #5 / #7).
- **ADR-013 verification discipline:** any factual claim of the shape "N files / tests / LOC", "present in <path>", "X is unused" needs the producing command's output cited inline (`verified via $ … → result`). Scoped commands stay scoped — don't generalize a narrow run into a wide claim.
