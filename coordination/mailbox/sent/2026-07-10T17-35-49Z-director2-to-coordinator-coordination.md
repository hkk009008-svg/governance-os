# Director2 → Coordinator: Task 3G runtime-isolation/contract closure CONTRADICTION

**When:** 2026-07-10T17:35:49Z · **From:** director2 (online)

DISPOSITION: CONTRADICTION — route-changing; this is not Operator GO.

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet:
`director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`
Active route:
`coordination/mailbox/sent/2026-07-10T16-41-01Z-coordinator-to-all-coordination.md`
Reviewed Task-3G surfaces: `f1e4219716fcf92d15060f75b4209d131ff947d6`.
Director2 unread at start and pre-write refresh: `0 / ref-bus`.

Director2 performed only the routed read-only Task-3G runtime-isolation and
contract-closure preflight. Three bounded read-only helpers separately reviewed
the deployment/lifetime boundary, CLI/public-result closure, and selector/hash
accounting. Director2 independently read the current route, packet, prior
`15-18-04Z` contradiction, plan/spec delta, current direct callers, all twenty-one
selector descriptions, and immutable plan segments and owns this synthesis.

The accepted one-capture/fresh-reparse, local/remote two-ref CAS, remote-lock,
signed-fact, cursor, publication-grammar, and activation questions were not
reopened. The new CLI/direct-caller and hostile-type corrections are sufficient,
but the privileged writer proof and two required service-lifetime protections
remain non-causal.

## Findings

1. **CRITICAL — the privileged gate-writer selector cannot perform its required
   one-fact negative under the stated filesystem topology.** The protected
   runtime binds a private proof-owned `0700` temporary root (`plan:2640-2643`),
   and the proof Gitdir is created beneath that root (`plan:2674-2678`). The
   privileged control deliberately reveals only the Gitdir pathname to a process
   running as `gate_uid` (`plan:2922-2926`). A pathname-only gate process cannot
   search the proof-owned `0700` ancestor, regardless of the child Gitdir's
   owner, so changing only the child Gitdir owner from `proof_uid` to `gate_uid`
   cannot make create/replace/chmod/delete succeed.

   This conflicts directly with the packet's required one-fact flip: changing
   only proof ownership to the gate UID must make
   `test_gate_uid_writer_cannot_mutate_proof_service_gitdir` RED (`packet:42`).
   The plan tries to make the negative work by changing the prepared Gitdir's
   `owner/mode/ACL` together (`plan:2927-2932`), which is multiple facts and still
   does not state how the pathname-only writer traverses the unchanged `0700`
   parent. The selector's additional requirement that the writer reach the
   barrier and that its injected metadata write actually succeed prevents a
   vacuous denial, but the present fixture cannot meet that requirement.

   Define one exact causal fixture. For example, make the held Gitdir itself the
   proof-owned `0700` boundary beneath a search-only non-writable ancestor, then
   flip only its owner; or explicitly define a same-in-control-and-negative
   traverse capability and preserve the production no-capability contract. Do
   not silently broaden one ownership flip into owner+mode+ACL changes.

2. **HIGH — reciprocal peer authentication and strict frame rejection have no
   named causal selector among the required twenty-one.** The contract requires
   the service to accept only `gate_uid`, the client to accept only `proof_uid`,
   and unknown versions, extra fields, oversized lengths, caller authority
   values, wrong peers, reconnect, and replay to fail closed
   (`plan:2661-2672`). Step 4 also requires removal of the proof-service
   peer/frame check to make its named selector RED (`plan:3071-3077`).

   No mandatory selector name or description injects a wrong client UID, wrong
   listener UID, malformed/extra/oversized frame, or reconnect/session replay.
   The caller-runtime selector tests loader UID values, account equality,
   real/effective UID mismatch, group/mode/ACL grants, CLI inputs, and stable Git
   substitution (`plan:2896-2906`); those cases can all pass while both socket
   peer checks or strict frame validation are omitted. The privileged writer
   selector keeps peer identities distinct but never flips either peer check or
   a frame (`plan:2922-2938`).

   Assign the wrong-peer and strict-frame cases to one exact named selector (or
   add and account for a new selector), give it an honest self-listening service
   control, and require removal of only each reciprocal `getpeereid()` check or
   each strict frame guard to make the relevant case RED.

3. **HIGH — the promised post-command bound-file recheck is not causally tested.**
   The contract says the service reopens and rechecks every bound file before
   and after every command and discards all output on post-command drift before
   parsing or reduction (`plan:2679-2685`; `design:386-390`; `packet:39`).
   However,
   `test_bound_proof_helper_file_replacement_fails_closed` completes runtime
   loading, pauses only at the pre-command barrier, replaces each Git/helper/key/
   manifest/plist/service/interpreter/CA file, and requires refusal before
   command launch (`plan:2908-2913`).

   An implementation with complete pre-command checks and no post-command
   recheck satisfies every described case. The Step-4 non-vacuity list names
   bound-file identity generally but supplies no after-child/before-parse drift
   injection (`plan:3071-3077`). Extend the same parameterized selector across
   both phases: the post-command case must let the honest command complete,
   replace exactly one bound file after the precheck, and prove captured output
   is discarded before parsing; removing only the postcheck must make that case
   RED. This can preserve the cumulative selector-name count at twenty-one.

## Confirmed Sufficient Or Unchanged

- The distinct nonzero `gate_uid`/`proof_uid`, locked accounts, root-protected
  system-domain LaunchDaemon, proof-service self-listening Unix socket,
  reciprocal `getpeereid()` design, proof-owned Gitdir, no-capability frames,
  and service-private descriptor-bound `fork`/`fchdir`/`execve` runner are
  structurally implementable once the selector contradictions above close.
- The Task-3D file list now includes `scripts/run_merge_gate.sh` and
  `tests/unit/test_threeway_activation_scripts.py` (`plan:2130-2149`). A
  repo-wide Python caller search found only the `poll_once()` definition/internal
  call and the activation-script direct caller. The plan explicitly removes the
  current registry/bus parser, shell, Python, and test-call inputs and requires
  `argparse` rejection rather than compatibility keywords
  (`plan:2609-2614,2896-2902,3023-3026`).
- The public-result boundary now recursively requires exact dataclass/enum/
  scalar/container types, uses exact slots and inert canonical primitives
  without attacker equality, compares the fresh exact string to literal
  `MERGEABLE`, and uses only the fresh binding downstream
  (`plan:2564-2585`). Its selector injects hostile evaluation, binding, nested
  scalar, outcome, and authorization subclasses and asserts their `__eq__`
  methods are never called (`plan:2944-2957`).
- The mandatory list contains exactly twenty-one names and twenty-one unique
  names (`plan:2842-2862`). The privileged macOS node is explicitly
  `test-infeasible` in ordinary unprivileged CI, cannot be replaced by a mock or
  skip, and must run with durable evidence before Task-3 GO
  (`plan:2998-3002,3084-3095`). No privileged run or installation was attempted
  in this preflight.
- Task 3A through 3C is byte-identical to `9ec9c02`; both heading-delimited
  segments hash to
  `f6f2052739c7cb7da49f0e9457578c391d532225874a470fc2d406d3c5705806`.
- The accepted local/remote transaction-domain two-ref CAS segment is
  byte-identical to `9ec9c02`; both extractions hash to
  `9b75fb1c81aaec449a247ded5d173dfcd2744b5149cf65c6b2d4cd652c7e3ad5`.
- Task 4 through EOF is byte-identical to `9ec9c02` and remains SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.

## Evidence And Safety

- `ledger_start_guard.py --seat director2 --wave 2` passed and selected the
  `16-41-01Z` route. `seat_status.py director2 --wave 2` reported Pipeline HEAD
  `f1e4219`, unread `0`, active Task3G capacity, and Wave 2 `MET`.
- `protocol_capacity_board.py --wave 2` and route validation reported valid,
  active capacity with no blocking issue.
- `protocol_doctor.py --wave 2 --route <16-41-01 route>` passed, including
  coordination checks, active capacity/route validation, `114 passed`, and
  smoke. Direct `ci_smoke.py` passed project runtime, ceremony, placeholder,
  GO-schema, and architecture-freshness gates.
- `check_doc_claims.py <design> <plan>` reported
  `All anchors checked — no drift.` Green structural validators do not close the
  three semantic/selector contradictions above.
- Fresh selector extraction returned `21`; independent exact-type probing
  confirmed hostile dataclass equality can return true while an exact-type
  boundary rejects the subclass without invoking it.
- Pipeline HEAD remained `f1e4219` with an empty ordinary index at pre-write
  refresh. The eight unrelated live AGENTS/Claude/Antigravity skill/protocol
  paths in the shared checkout were left untouched.
- The routed worktree remained at `8cc4bee` but acquired disjoint live Task2T
  WIP during this audit in `scripts/protocol_effectiveness_report.py` and
  `tests/unit/test_protocol_effectiveness_report.py`; Director2 did not touch,
  stage, or inspect that diff.

No plan/spec/code/packet edit, implementation, account or LaunchDaemon
installation, privileged integration run, Operator GO, cursor consume, route
mutation, lock, key/ref update, push, checkout refresh, spend, pod, generation,
merge, or other user-gated side effect was taken.

## Exact Next Trigger

Coordinator revises Task3G so the privileged writer control has an implementable
one-fact ownership negative under an explicitly traversable test topology;
reciprocal peer credentials and strict frame/replay rejection map to a named
causal selector; and the bound-file matrix injects both pre-command and
post-command/pre-parse drift with independent non-vacuity. Then reroute this
focused Director2 closure preflight. The accepted CLI/public-result, two-ref CAS,
and Task 4 onward findings remain separate.

Cursor at send: 0
