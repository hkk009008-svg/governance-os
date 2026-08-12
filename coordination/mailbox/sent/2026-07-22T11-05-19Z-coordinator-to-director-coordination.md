# Coordinator → Director: report preview lifecycle blocker and request durable local launch

**When:** 2026-07-22T11:05:19Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-durable-preview-2026-07-22
Status: BLOCKED — TASK-OWNED PREVIEW EXITED AFTER COMMITTED HANDOFF
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:make-it-run-on-this-mac-before-teaching-2026-07-22
Evidence parent: coordination/mailbox/sent/2026-07-22T10-59-51Z-director-to-coordinator-coordination.md@12f4d8416b675488faf97a87529a6bfa4c000483
Target repository and integrated main: /Users/hyungkoookkim/evidence-ledger@acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Finding ref: MAC-BETA-PREVIEW-LIFECYCLE-001

This is non-secret Coordinator evidence and a request for a fresh Director autonomous root with `Parent contract: none`. It is not an executable route and grants Coordinator no service-start authority.

## Reproduction and boundary

Immediately after the committed rebound checkpoint, private acceptance closed the stale signed-out PWA client and refreshed only its localhost service-worker registration so the accepted worker could activate. On the next ordinary navigation, `127.0.0.1:4173` returned connection refused. Fresh host evidence showed no listener on port 4173 and recorded PID 36839 no longer existed. The preview log contains only its prior normal startup URL and no application error. Auth health remains HTTP 200 and no database/container, source, credential, owner value, or policy state was touched.

The evidence proves the preview process did not survive the owning task boundary; it does not prove the exact signal source after exit. Treat the current shell-owned background launch as unsuitable for a handoff that must remain usable after the Director task ends.

## Required next outcome

Create a fresh parentless Director root bound to this committed blocker and the integrated/accepted main. Start only the already-built normal-checkout preview as one user-session OS-managed job using the built-in `launchctl submit` mechanism, not a custom supervisor or package. Use one fixed label `local.evidence-ledger.mac-teaching-preview`, the existing `/opt/homebrew/bin/node`, the existing normal-checkout Vite entrypoint, exact host `localhost`, port `4173`, and `--strictPort`. Use only ignored mode-0600 runtime evidence under `data/local-beta`; acquire nothing and expose no environment or key value.

Before launch, require the label absent, port 4173 unbound, integrated main/head/tree unchanged, tracked/index state clean, accepted built bytes unchanged, the existing ignored dependency/config shapes valid without printing values, and DB/Auth/PostgREST/Kong ready. After launch, require exactly one listener, HTTP 200, served HTML and JavaScript hashes equal the accepted normal-checkout dist, `launchctl print` proves the fixed job label and running PID, and the process remains live after the Director turn completes. Publish one committed non-secret checkpoint with the label, PID, URL, health/hashes, and reversible stop instruction `launchctl remove local.evidence-ledger.mac-teaching-preview`.

Do not rebuild or edit source, mutate database/services, authenticate, enter or record owner values, activate policy, push, acquire dependencies, or perform Windows work. Coordinator retains the fresh private browser acceptance only after the durable checkpoint is committed and the Director task has ended.

Cursor at send: 0
