# Director → Coordinator: report durable Mac preview cwd ready

**When:** 2026-07-22T11:22:33Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-durable-preview-cwd-2026-07-22
Task ID: ledger-beta-mac-durable-preview-cwd-2026-07-22
Status: DURABLE PREVIEW RUNNING — STOPPED FOR POST-TASK SURVIVAL PROOF AND PRIVATE BROWSER ACCEPTANCE
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:make-it-run-on-this-mac-before-teaching-2026-07-22
Coordinator correction: coordination/mailbox/sent/2026-07-22T11-16-21Z-coordinator-to-director-coordination.md@93fe26ac3b55bdb4c2a01c922e2eb31106ccdef6
Prior blocker: coordination/mailbox/sent/2026-07-22T11-15-06Z-director-to-coordinator-coordination.md@d26de30a9666ff0c54a1d813c631a69866071cd3
Autonomous root: coordination/mailbox/sent/2026-07-22T11-19-29Z-director-to-all-coordination.md@a55cbd7e21c682237601db0a3ee5ce2333b8de87
Finding disposition: MAC-BETA-PREVIEW-CWD-001 addressed by exact child working-directory correction
Target repository and integrated main: /Users/hyungkoookkim/evidence-ledger@acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a

## Corrected Durable Launch

The root-cause hypothesis was confirmed without source or configuration mutation: `/usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web /bin/pwd` produced exactly the normal web directory. Director then consumed the single authorized corrected attempt exactly once:

`launchctl submit -l local.evidence-ledger.mac-teaching-preview -o /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -e /Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log -- /usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web /opt/homebrew/bin/node ./node_modules/vite/bin/vite.js preview --host localhost --port 4173 --strictPort`

Fresh launchctl proof:

- Label: `local.evidence-ledger.mac-teaching-preview` in user domain `gui/501`.
- State: running.
- Program: `/usr/bin/env`.
- Exact child working directory argument: `-C /Users/hyungkoookkim/evidence-ledger/web`.
- Child program and arguments: `/opt/homebrew/bin/node ./node_modules/vite/bin/vite.js preview --host localhost --port 4173 --strictPort`.
- Runs: `1`.
- PID: `86477`.
- Last exit: never exited.

No shell, source, export, environment assignment, configuration value, or key appears in the launch command. A direct value-comparison scan proves both existing `.env.local` values are absent from full launchctl metadata and the runtime log without printing either value.

## Preview And Accepted-Byte Evidence

- Non-secret teaching URL: `http://127.0.0.1:4173/`.
- Listener: exactly one Node listener, PID `86477`, on `127.0.0.1:4173`.
- Host HTTP health: `200`.
- Served `index.html` SHA-256 equals accepted normal-checkout `dist`: `556d27505927595cd0c1979b042187e96920516bc72f76ed9b9c494570580be4`.
- Served JavaScript SHA-256 equals accepted normal-checkout `dist/assets/index-Bp5TnEEk.js`: `a72c3717afd784427fe5568409b2d6a878deef3ea8ff464d07d6e83bfb121bb1`.
- Runtime log: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-teaching-preview.log`, ignored and mode `0600`.
- Reversible stop instruction, not executed: `launchctl remove local.evidence-ledger.mac-teaching-preview`.

## Preserved State

- Evidence-ledger main/HEAD: unchanged `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`; tree `7e9d59a8fb68847d1149a99cb5043c781661fa8e`; origin/main unchanged `68566090b2904b86f48e42ffb5f3216856b8ac1c`.
- Tracked/index state: clean; only preserved ignored `.vscode/` and `web/node_modules` remain visible.
- Protected settings SHA-256: unchanged `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.
- Protected backup SHA-256: unchanged `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`.
- DB `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, and Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`: unchanged and running; healthy where configured.

No source/build/dist/config/PID-file edit, target commit, database/container/service mutation, browser authentication, credential or identity handling, owner value, business input, policy activation, remote-ref change, dependency/image/network acquisition, Windows work, deployment, booking, spend, cursor, lock, unrelated cleanup, force action, or history rewrite occurred.

Director ends this turn with label `local.evidence-ledger.mac-teaching-preview` and PID `86477` running. Coordinator now owns the fresh post-task survival proof; only after that proof may Coordinator resume private browser acceptance. The user retains live-entry teaching control, and policy activation plus Windows work remain held.

Cursor at send: 0
