# Operator2 → Coordinator: BLOCKED control-plane Tasks 4-5 preflight

**When:** 2026-07-10T01:23:27Z · **From:** operator2 (online)

DISPOSITION: BLOCKED

Packet: operator2-control-plane-authority-foundation-cutover-preflight
Active route: coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md
Reviewed Pipeline HEAD: 41d48ab791154ea258e6e6b2f0e7aa1b33de9125
Scope: bounded read-only execution/verification-feasibility preflight for implementation-plan Tasks 4 and 5. This is not production Lane V and grants no cutover, bootstrap, ref, key, cursor, push, or other side-effect authority.

Subagent utilization decision: dispatched two bounded read-only helpers on distinct questions: Task 4 cutover/ref safety and Task 5 key-bootstrap/fixture safety. Both independently returned a blocking contradiction. The operator2 parent re-read the named source and retained the single mailbox disposition.

## Findings

1. BLOCKER — The planned Task-6 side-effect topology contradicts the approved design. The design requires key generation/public-key commit and authoritative-ref cutover to be distinct target-bound executor-token actions (docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md:174-175,220-228). The plan instead combines public-key creation, private-keystore generation, ref mutation, and the authority flip under one token and command class (docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md:592-617). Required disposition: split trust-root generation/public-key commit from authoritative-ref cutover before a later activation route. The manifest flip may be bound to the cutover token only after the trust root is already committed and independently verified.

2. BLOCKER — Task 4 has no implementable verified-resume or executor-token input contract. The plan allows a second cutover only when refs match an activation manifest and requires preflight to prove tests plus Operator GO are named in an executor token (plan:475-480,502-513), but defines no activation-manifest path/schema/loader and no token path or --executor-token input. Current force=True bypasses prior-ref refusal without verification (threeway/gitcas.py:245-258), and the driver accepts only --yes (scripts/execute_threeway_cutover.sh:12-33). Required disposition: define a structured activation manifest and token input, or remove resume support and refuse every second cutover. Also make the projected head explicit in CutoverResult and bind the initializer identities to the same validated six-cursor roster snapshotted for teardown; arbitrary identities with a fixed rollback roster can strand refs.

3. BLOCKER — Task 5's production bootstrap state machine is incomplete. The exact 11-seat default roster is source-backed, but current main() accepts arbitrary/subset --seats, creates directories, then overwrites keys immediately (threeway/keys_bootstrap.py:13-32). Existing tests deliberately create one- and two-seat registries (tests/unit/test_keys.py:95-135), and the activation fixture provisions only nine seats (tests/unit/test_threeway_activation_scripts.py:86-115). The plan also leaves empty-public-registry plus nonempty/partial private keystore undefined; keys.load_private() ignores the bootstrap explicit --keystore path; and direct bootstrap can target a keystore inside the repository. Required disposition: production CLI must bind the canonical roster and reject subset --seats; define pre-write refusal for empty public registry with any canonical private key present; add an explicit configured-keystore loader; and enforce symlink-safe off-repo keystore containment before any mkdir or generation. Pure helper functions may accept injected rosters for hermetic tests.

4. INFORMATIONAL — Current environment is safe and non-mutated. Pipeline main and the routed worktree are clean; the routed worktree exists at exact base 78b48ed493899dd126de2d1764cbdbf022111dfd; local refs/threeway/* is empty; the public registry contains metadata only and zero *.pub; no tracked or filesystem *.ed25519 was found below Pipeline; the default roster resolves to exactly 11 identities. These facts do not cure the interface contradictions above.

5. INFORMATIONAL — Selector feasibility is bounded by planned dependencies. The Task-5 selector currently collects 15 tests. The Task-4 selector cannot yet collect because tests/unit/test_threeway_cutover.py and tests/unit/test_protocol_authority.py do not exist at this routed HEAD; the plan creates them in Tasks 4 and 1 respectively. Current scripts/execute_threeway_cutover.sh --preflight exits 2 at the generic irreversible refusal and performs no mutation, confirming that a real preflight interface is not present yet.

## Required Regression Shape

Task 4 must pin: pure --preflight with identical refs, human seen bytes, registry/keystore trees, worktree/index/staging; human seen bytes unchanged on success, append failure, and partial cursor failure; every signed cursor initialized to one explicit nonzero projected head; exact full-ref snapshot restoration after the Nth cursor failure; partial/extra registry refusal; second-cutover refusal or exact structured-manifest resume; and shadow/live missing events ref returning unavailable rather than empty.

Task 5 must pin: the explicit 11-name roster; metadata-only registry classified empty; exact-roster generation from empty; complete matching registry/keystore byte-and-mtime-preserving no-op; partial, extra, missing-private, public/private-mismatch, and empty-public/nonempty-private refusal before generation or writes; production subset-roster refusal; symlink-safe in-repo keystore refusal; and no tracked or untracked *.ed25519 below the repository.

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator2 --wave 2
→ HEAD 41d48ab; unread 0 / ref-bus; Wave 2 MET.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
→ valid true; packet state active; operator2 packet active; no mechanical blocking issue.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md
→ route valid true. This validates route shape, not semantic safety.

$ env -u GIT_INDEX_FILE git status --short --branch --untracked-files=all
→ ## main...origin/main [ahead 45]; no dirty entries.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10 status --short --branch --untracked-files=all
→ clean branch at routed base.

$ env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
→ no output before and after checks.

$ env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh --preflight
→ exit 2; generic irreversible refusal; no refs or tracked changes created.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/unit/test_threeway_cutover.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_protocol_authority.py
→ exit 4; tests/unit/test_threeway_cutover.py absent.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/unit/test_keys.py tests/unit/test_threeway_activation_scripts.py
→ 15 tests collected.

$ env -u GIT_INDEX_FILE .venv/bin/python -c 'from threeway.keys_bootstrap import SEATS; print(len(SEATS))'
→ 11.

No production/code/doc edit, key generation, public-key write, private-key read, cutover, ref mutation, cursor consume, coordinator-mail consume, lock action, push, paid spend, pod action, or production generation occurred.

## Exact Next Trigger

Coordinator publishes one bounded plan/route revision that (1) splits trust-root generation/publication from authoritative-ref cutover, (2) defines or removes verified resume and gives preflight a structured executor-token input, and (3) closes the canonical-roster/keystore state machine. Then reroute operator2-control-plane-authority-foundation-cutover-preflight for a focused re-preflight. Pair-A Tasks 1 and 2 remain under the coordinator's current/new route decision; this report does not independently cancel them.

Cursor at send: 0
