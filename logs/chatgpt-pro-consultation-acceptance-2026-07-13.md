# ChatGPT Pro consultation acceptance - 2026-07-13

## Scope

- Bound HEAD: `c96b5427a93b32858664d4ac00b5362032b1c96c`
- Guard commit: `c96b5427a93b32858664d4ac00b5362032b1c96c`
- Guard relevant paths hash: `388c45d2d1993f357baace7f24fdbb99edf4d68c3a71bfb772464f44e0af1f3c`
- Procedure: `docs/protocol/codex/chatgpt-pro-consultation-acceptance.md`
- Default before gate: `manual`
- Raw consultation content persisted: `no`

## Results

| Test ID | Transport class | Result | Safe correlation | Lifecycle | Duplicate send | Protocol/ref/remote mutation | Failure class |
|---|---|---|---|---|---|---|---|
| T5-IAB-r1 (`cb81cec8…64dd`) | Desktop in-app | fail | pass | `prepared -> sending -> sent -> failed` | pass; one send | pass; content-free snapshots match | `malformed` |
| T5-IAB-r2 (`6d554cda…1817`) | Desktop in-app | pass | pass | `prepared -> sending -> sent -> received -> reconciled`; tab finalized | pass; one send | pass; content-free snapshots match | none |
| T5-IAB-r3 (`182b94d3…087c`) | Desktop in-app | pass | pass | `prepared -> sending -> sent -> received -> reconciled`; tab finalized | pass; one send | pass; content-free snapshots match | none |
| T5-CLI-BROWSER-r1 (`5a5a52bd…b063`) | configured CLI browser | fail | not applicable; no response/import | `prepared -> sending -> failed`; ephemeral process terminated after 5.5 minutes; tab finalization unverified | delivery uncertain; no retry | pass; content-free snapshots match; no Codex session persisted | `partial_send` |
| T5-CLI-PREFLIGHT-r2 | configured CLI non-sending diagnostic | fail | not applicable | core model healthy; Browser skill loaded; no navigation, tab, or message | no send | pass; no protected mutation | `backend_unavailable` |
| T5-CLI-MANUAL-r2 (`801d4038…c37e`) | bare CLI manual relay | pass | pass | `prepared -> sending -> sent -> received -> reconciled`; manual relay finalized | pass; one relay | pass; content-free snapshots match | none |
| T5-FAILURE-FIXTURES-r1 | fixture/disposable profile | pass | not applicable | seven-case fixture matrix failed closed; fixtures finalized | pass; no retry or fallback | pass; content-free snapshots match | none |

## Commands

- Focused tests: `226 passed`
- Full protocol tests: `312 passed`
- Project smoke: `OK`
- Persistence/security scans: `pass`
- Runtime state/lock pairs checked: `6`
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
- Desktop r3 result: `pass`
- Desktop r3 state file: `.codex/runtime/task5-iab-r3-acceptance.json`
- Desktop r3 request hash: `9f551ed6…57b2b5`
- Desktop r3 idempotency key: `faec7aba…2f98e25`
- Desktop r3 binding hash: `f8f0eaef…ebe107f`
- Desktop r3 correlation: `pass`
- Desktop r3 transport sends: `1`
- Desktop r3 transport resend: `no`
- Desktop r3 interrupted local accept: `1`
- Desktop r3 state after interrupted accept: `sent`
- Desktop r3 response imports: `1`
- Desktop r3 final state: `reconciled`
- Desktop r3 tab finalized: `yes`
- Bare CLI manual r2 result: `pass`
- Bare CLI manual r2 state file: `.codex/runtime/task5-manual-r2-acceptance.json`
- Bare CLI manual r2 request hash: `c2dee748…451918`
- Bare CLI manual r2 idempotency key: `a3ed85e4…77fd5b`
- Bare CLI manual r2 binding hash: `f8f0eaef…ebe107f`
- Bare CLI manual r2 prompt parity: `pass`
- Bare CLI manual r2 correlation: `pass`
- Bare CLI manual r2 relays: `1`
- Bare CLI manual r2 response imports: `1`
- Bare CLI manual r2 final state: `reconciled`
- Failure-fixture result: `pass`
- Failure-fixture cases: `signed-out,wrong-account,challenge,refusal,html,truncated-json,partial-send`
- Failure-fixture pre-send stops: `signed-out,wrong-account,challenge`
- Failure-fixture partial-send start: `sending`
- Failure-fixture retry or fallback: `none`
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
- Bare CLI manual gate: `pass`
- Failure-fixture gate: `pass`
- Activation gate: `blocked`
- Shipped default: `manual`
- Bounded blocker: `backend_unavailable`
