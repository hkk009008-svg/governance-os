# ChatGPT Pro consultation acceptance - 2026-07-13

## Scope

- Bound HEAD: `7e09aeb94d8dec9d4db40ff92d04346cff0b303c`
- Procedure: `docs/protocol/codex/chatgpt-pro-consultation-acceptance.md`
- Default before gate: `manual`
- Raw consultation content persisted: no

## Results

| Test ID | Transport class | Result | Safe correlation | Lifecycle | Duplicate send | Protocol/ref/remote mutation | Failure class |
|---|---|---|---|---|---|---|---|
| T5-IAB-r1 (`cb81cec8…64dd`) | Desktop in-app | fail | pass | `prepared -> sending -> sent -> failed` | pass; one send | pass; content-free snapshots match | `malformed` |
| T5-IAB-r2 (`6d554cda…1817`) | Desktop in-app | pass | pass | `prepared -> sending -> sent -> received -> reconciled`; tab finalized | pass; one send | pass; content-free snapshots match | none |
| T5-CLI-BROWSER-r1 (`5a5a52bd…b063`) | configured CLI browser | fail | not applicable; no response/import | `prepared -> sending -> failed`; ephemeral process terminated after 5.5 minutes; tab finalization unverified | delivery uncertain; no retry | pass; content-free snapshots match; no Codex session persisted | `partial_send` |
| T5-CLI-PREFLIGHT-r2 | configured CLI non-sending diagnostic | fail | not applicable | 27.7 seconds; core model healthy; Browser skill loaded; no navigation, tab, or message | no send | pass; no protected mutation | `backend_unavailable` |
| T5-CLI-MANUAL | bare CLI manual relay | pending | pending | pending | pending | pending | pending |
| T5-FAILURE-FIXTURES | fixture/disposable profile | pending | not applicable | pending | pending | pending | pending |

## Commands

- Focused tests: `124 passed`.
- Full protocol tests: `210 passed`.
- Project smoke: `OK`.
- Persistence/security scans: pass; zero secret, transcript, or runtime-content
  field hits.
- Content-free state and git snapshots: pass; four runtime state/lock pairs
  match the exact metadata schema and private-permission contract; protected
  HEAD, refs, remotes, mailbox, inventory, locks, and signed-bus hashes match.
- CLI session persistence: pass; zero rollout files were created or modified
  during the configured-CLI attempt window.
- Configured CLI non-sending diagnostic: core model and skill load passed;
  standalone `iab` backend unavailable in 27.7 seconds.

The first Desktop attempt is terminal. Its exact correlated import was rejected
by the guard because the prepared packet under-specified the response contract.
No repair or retry was attempted, and the tab was finalized. The prompt-contract
fix requires a new acceptance revision, fresh consultation ID, distinct
idempotency key, and new state path before either real gate can pass.

Desktop revision 2 used the corrected prompt contract and completed the exact
guarded lifecycle with matching correlation, one send, no duplicate, and no
content-free protocol, ref, or remote snapshot change. Its state file contains
only the approved metadata schema and has private permissions; no consultation
content is recorded here.

Configured-CLI revision 1 produced no response output and no import. Delivery
remained uncertain when the dedicated ephemeral process was terminated after
5.5 minutes, so the attempt failed closed as `partial_send`; no retry occurred
and tab finalization is unverified. No rollout/session file was created or
modified during the attempt window, and all protected content-free hashes
matched the pre-transport snapshot.

The follow-up non-sending diagnostic isolated the environment boundary without
navigating or messaging: the ephemeral core CLI/model was healthy and loaded
the Browser skill, but the standalone `iab` backend did not connect or load
documentation. Installed plugin/feature configuration is therefore not a
usable configured-CLI browser transport in this context.

## Activation decision

- Desktop in-app gate: `pass`
- Configured CLI browser gate: `fail`
- Activation gate: `blocked`
- Shipped default: `manual`
- Bounded blocker: the configured-CLI browser gate failed closed on uncertain
  delivery. The default remains `manual`; no further send is authorized by this
  attempt.
