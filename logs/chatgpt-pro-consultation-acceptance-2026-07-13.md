# ChatGPT Pro consultation acceptance - 2026-07-13

## Scope

- Bound HEAD: `7e09aeb94d8dec9d4db40ff92d04346cff0b303c`
- Procedure: `docs/protocol/codex/chatgpt-pro-consultation-acceptance.md`
- Default before gate: `manual`
- Raw consultation content persisted: `no`

## Results

| Test ID | Transport class | Result | Safe correlation | Lifecycle | Duplicate send | Protocol/ref/remote mutation | Failure class |
|---|---|---|---|---|---|---|---|
| T5-IAB-r1 (`cb81cec8…64dd`) | Desktop in-app | fail | pass | `prepared -> sending -> sent -> failed` | pass; one send | pass; content-free snapshots match | `malformed` |
| T5-IAB-r2 (`6d554cda…1817`) | Desktop in-app | pass | pass | `prepared -> sending -> sent -> received -> reconciled`; tab finalized | pass; one send | pass; content-free snapshots match | none |
| T5-CLI-BROWSER-r1 (`5a5a52bd…b063`) | configured CLI browser | fail | not applicable; no response/import | `prepared -> sending -> failed`; ephemeral process terminated after 5.5 minutes; tab finalization unverified | delivery uncertain; no retry | pass; content-free snapshots match; no Codex session persisted | `partial_send` |
| T5-CLI-PREFLIGHT-r2 | configured CLI non-sending diagnostic | fail | not applicable | core model healthy; Browser skill loaded; no navigation, tab, or message | no send | pass; no protected mutation | `backend_unavailable` |
| T5-CLI-MANUAL | bare CLI manual relay | pending | pending | pending | pending | pending | pending |
| T5-FAILURE-FIXTURES | fixture/disposable profile | pending | not applicable | pending | pending | pending | pending |

## Commands

- Focused tests: `163 passed`
- Full protocol tests: `249 passed`
- Project smoke: `OK`
- Persistence/security scans: `pass`
- Runtime state/lock pairs checked: `4`
- Protected hashes: `match`
- CLI-window rollout files created: `0`
- CLI-window rollout files modified: `0`

## Diagnostics

- Desktop r1 failure: `malformed`
- Desktop r1 retry: `no`
- Desktop r1 tab finalized: `yes`
- Desktop r2 result: `pass`
- Desktop r2 duplicate send: `no`
- Desktop r2 tab finalized: `yes`
- Configured CLI r1 failure: `partial_send`
- Configured CLI r1 response imported: `no`
- Configured CLI r1 retry: `no`
- Configured CLI r1 duration seconds: `330`
- Configured CLI r1 tab finalized: `unverified`
- Configured CLI preflight duration seconds: `27.7`
- Configured CLI core model: `pass`
- Configured CLI Browser skill load: `pass`
- Configured CLI backend: `iab`
- Configured CLI browser connected: `false`
- Configured CLI documentation loaded: `false`
- Configured CLI preflight navigation: `none`
- Configured CLI preflight messaging: `none`
- Configured CLI preflight failure: `backend_unavailable`

## Activation decision

- Desktop in-app gate: `pass`
- Configured CLI browser gate: `fail`
- Activation gate: `blocked`
- Shipped default: `manual`
- Bounded blocker: `backend_unavailable`
