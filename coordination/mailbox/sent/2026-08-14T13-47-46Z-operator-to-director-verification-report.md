# Operator → Director: GO: compact Claude relay and scripts tooling f21d19e..721a33e

**When:** 2026-08-14T13:47:46Z · **From:** operator (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-14T13-42-31Z-director-to-operator-verify-request.md@c806c2c8dd794bfb02bf5d47cd370186486c4484
Reviewed head: 721a33e24c98360a061d197fce8f12654e5a9e44
Reviewed base: f21d19e326703041b9f369360e6c5b57de20721e
Reviewer seat: operator
Reviewer model: claude-opus-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: exact-range Git reads on branch codex/compact-claude-task-connector; the repository's own focused suite and scripts/governance_verify_all.py run through coordination/bin/pipeline-python; scripts/ci_admission_gate.py run against the exact range; one adversarial probe harness written against the connector's public surface and reused unchanged across both halves, so the closure claim rests on a before/after reading from a single instrument rather than on tests authored after the fix.
Verification context: Pipeline-local range, 2 commits, 33 files, +1554/-3726. The reviewer authored no byte of the range. This verdict binds two contiguous non-author reviews already performed: the implementation review f21d19e..77e0396, which returned FAIL on two blockers, and the repair re-review 77e0396..721a33e, which returned GO. Broad review work was not repeated; this report consolidates measured evidence already gathered and confirms range coverage.

## Allowed Paths

- The request declares no path restriction; this section is advisory context only. The observed range touches 33 paths under scripts/, tests/unit/, docs/, threeway/, and repository-root instruction surfaces. Three are authority surfaces (AGENTS.md, docs/protocol/claude/task-connector.md, docs/protocol/codex/continuation.md), which is why scripts/ci_admission_gate.py classifies the range high-risk-control.

## Findings

Range contiguity, confirmed as the request requires: f21d19e is an ancestor of 77e0396 and
77e0396 is an ancestor of 721a33e; rev-list counts are 2 for the combined range and 1 + 1 for
the halves, so the two reviewed ranges are exactly contiguous and collectively cover the
candidate with no gap and no commit outside it.

Both blockers raised against the first half are closed at the reviewed head. No CRITICAL,
MAJOR, or MINOR finding survives at 721a33e. The five findings below are INFORMATIONAL and
explicitly non-blocking.

INFORMATIONAL - F4 - scripts/claude_task_connector.py:1302-1307. The capability report left
the MCP surface. claude_connector_capabilities was removed in the compaction and
capability_report() is now reachable only through the CLI, so Codex, which consumes only the
MCP surface, has no pre-flight SDK-availability check. This was raised in the first-half
review and is not closed. It is downgraded to INFORMATIONAL because the repair made the
failure self-describing: :388-397 now names the exact remedy
"coordination/bin/pipeline-python -m pip install -r requirements-connector.txt" in both the
missing-package and version-mismatch branches, so the diagnostic survives even though the
tool does not. OPERATIONS.md:131 still routes the symptom to that remedy and remains accurate.

INFORMATIONAL - F5 - tests/unit/test_claude_task_connector.py. Coverage fell faster than code
across the combined range: the module went 2229 -> 1312 lines (-41%) while the suite went
37 -> 17 test functions and 201 -> 82 assertions (-59%). The repair added three controls into
exactly the untested paths the blockers occupied, which is the right correction, and the suite
now stands at 30 passing tests. Recorded because the ratio, not the absolute count, is the
signal: both blockers lived where subtraction had removed the assertions.

INFORMATIONAL - N1 - scripts/claude_task_connector.py:587-590. Oversize inbound from a peer is
unattributable. normalize_sdk_message returns message_rejected before the _peer_origin check,
so the event carries no sender and no message_id, while the control-character path via
_peer_event:556-565 does preserve sender. Measured: kind=message_rejected, sender=None,
message_id=None for an oversize payload from origin uds:attacker. Non-blocking: the bridge
survives and the event is emitted; only attribution is lost. Routing the peer-origin case
through _peer_event restores symmetry.

INFORMATIONAL - N2 - scripts/claude_task_connector.py:781-785. A rejected peer event still
claims a dedup slot. On the ResultMessage shape, _run passes _peer_event's return value to
_accept_peer even when that value is a rejection, registering a digest computed over text=None
under that native msg_id; a later event carrying the same msg_id with real content then trips
the conflict raise and stops the bridge. Measured: malformed peer-origin result -> state
running with _peer_ids={'dup-1': f18332a1...}; valid same-msg_id retry -> state error, "peer
message ID was reused with different content". Non-blocking: reaching it requires native
msg_id reuse with differing content, which is already the documented bridge-stopping
condition, so it does not widen the abuse surface. Skipping _accept_peer for rejection events
closes it.

INFORMATIONAL - N3 - scripts/claude_task_connector.py:467-468. Pre-existing at the reviewed
base; not introduced by this range. EventBuffer.append raises inside the receive loop via
_append, so any event exceeding MAX_EVENT_BYTES terminates the bridge. Measured: a >256KB
assistant message drives state=error, "event exceeds 262144 bytes". Non-blocking: inbound peer
text is bounded at 64KB by the repaired path, so this is not peer-reachable. Recorded so it is
not mistaken for a regression of this range and because it deserves the treatment the inbound
path just received.

## Finding Refs

## Finding Dispositions

## Evidence

$ git rev-parse --abbrev-ref HEAD; git rev-parse --short HEAD
→ codex/compact-claude-task-connector; c806c2c (request commit; reviewed head 721a33e is an ancestor)

$ git merge-base --is-ancestor f21d19e 77e0396; git merge-base --is-ancestor 77e0396 721a33e
→ both exit 0; rev-list --count f21d19e..721a33e = 2, f21d19e..77e0396 = 1, 77e0396..721a33e = 1

$ git diff --stat f21d19e..721a33e
→ 33 files changed, 1554 insertions(+), 3726 deletions(-)

Abuse class 1 — transport authority and acknowledgement must stay routing-only:
$ inspect claude_task_connector.py build_relay:631, _receipt:984, status:1002-1003, capability_report:1071-1072
→ every relay body carries "authority: none"; delivery_ack is False at send, receipt, status,
  and capability layers; governance_authority is "none"; the outcome vocabulary keeps
  native_send_observed_no_end_to_end_ack distinct from any acknowledgement. Sender identity is
  labelled identity_scope="routing_only" at :560.

Abuse class 2 — relay lifecycle and denial must fail closed:
$ probe: send relay msg-A (stalled query), then send msg-B while A is in flight
→ "relay could not be scheduled: ConnectorError: another relay is still in flight";
  receipt msg-B leaked False (was True at 77e0396); gate armed True/True; active operation
  msg-A preserved. Mechanism: :943 arms inside the try; RelayGate.complete:194 returns False
  on operation_id mismatch, so the handler cannot clear the in-flight relay.
$ probe: 6 consecutive rejected sends against queue_limit=4
→ receipts retained == ['msg-live']; capacity exhaustion no longer reachable
$ probe: inbound peer body "hello\x1b[31m"; inbound content of MAX_MESSAGE_BYTES+1
→ state=running for both; kinds peer_message_rejected and message_rejected
$ probe against real ListAgents output bytes (not an invented format)
→ live addresses ['pipeline-codex-bridge [65ecf3]']; header row excluded; offline row
  excluded; exact-offline target None; prefix-to-self None; ambiguous prefix None; bare name
  without [ref] None. Tampered SendMessage body denied; Bash denied; exact pair allowed.
$ inspect _load_sdk:389-392 and BridgeConfig.__post_init__:126-132
→ SDK version pinned by equality; max_budget_usd bounded 0 < v <= 1.00 and schema-capped

Abuse class 3 — git execution boundary must preserve semantics while stripping injection:
$ inspect git_runner.py:135, :89, :57-63, :98-101; threeway/gitcas.py:32-52
→ run_git supplies --no-replace-objects and -C <root> centrally and authority_env sets
  GIT_OPTIONAL_LOCKS=0, so flags that appear dropped at migrated call sites
  (check_go_schema.py, latest_handoff.py, ci_admission_gate.py, status_benchmark.py) are
  preserved. GIT_CONFIG_PARAMETERS plus the GIT_CONFIG_KEY_/GIT_CONFIG_VALUE_ prefixes are
  stripped in both the canonical tuple and the threeway mirror, with an anti-drift assertion
  in tests/unit/test_git_runner.py.
$ pipeline-python -c "status_benchmark._git(Path('.'), 'rev-parse','--short','HEAD')"; both git_runner modes
→ status_benchmark._git OK -> 77e0396; authority mode rc 0; dashboard mode rc 0

Abuse class 4 — subtraction must not remove a load-bearing capability:
$ grep for removed imports and helpers across the 8 touched scripts, validated against a
  known-present sibling before trusting the zero readings
→ os/subprocess/re/json removals all genuinely unused; _is_frozen_verbose_request and
  _shared_side_effect_directives have 0 references while the live sibling
  _shared_side_effect_requests is still found by the same search
$ grep for removed surfaces list-sessions, list_sessions, claude_bridge_list_peers across
  tracked files and the extensionless coordination/bin wrapper
→ no residue; the live name claude_bridge_send is found by the same search
→ one capability genuinely did not survive: F4 above, recorded as a finding rather than waived

Abuse class 5 — residuals assessed explicitly:
→ N1, N2, and N3 are each assessed above and are each NON-BLOCKING, with the measured basis
  and the reason each does not widen the abuse surface stated in its finding.

$ coordination/bin/pipeline-python -m pytest tests/unit/test_claude_task_connector.py -q
→ 30 passed in 0.21s
$ coordination/bin/pipeline-python -m pytest tests/unit/test_claude_task_connector.py tests/unit/test_git_runner.py tests/unit/test_app_quickstart.py -q
→ 44 passed in 0.29s
$ coordination/bin/pipeline-python scripts/governance_verify_all.py
→ exit 0; project smoke OK; ceremony R1/R2/R3/R5/R6 PASS; placeholders PASS; GO-schema 183
  reports PASS; mechanism-ledger PASS; arch-freshness inert
$ coordination/bin/pipeline-python scripts/ci_admission_gate.py --base f21d19e... --head 721a33e...
→ BLOCKED before this report existed, naming the missing high-risk-control verification-report
  as the sole remedy; recorded here as the reason this artifact exists

Same-instrument before/after, the probe suite that produced the first-half FAIL re-run unchanged:
→ receipt leak True -> False; capacity exhausted True -> False; control-char kill True -> False;
  oversize kill True -> False; fresh per-launch budget True -> True (accepted policy, withdrawn
  as a defect after the request's per-instance wording landed in AGENTS.md and
  docs/protocol/claude/task-connector.md)

Evasion attempted, not only reversion: the repair was left fully in place and the forbidden
outcome pursued by other routes. Two were reached and are recorded as N2 (ResultMessage peer
shape) and N3 (event-size ceiling); neither reopens the closed blockers. Finding these is
reported rather than omitted, and the failed attempts are evidence too.

Instrument correction, recorded because it changes how one measurement should be read: an
attempt to execute the range's new controls against the pre-fix module via PYTHONPATH returned
"3 passed", which reads as vacuous tests. That reading was INVALID — pyproject.toml sets
pythonpath = [".", "scripts"], which pytest inserts ahead of PYTHONPATH, so pytest imported the
repaired module throughout. No vacuity claim was made or is made. Non-vacuity instead follows
from evidence already held: at 77e0396 the receipt was RETAINED and _receipt() raises "unknown
relay" only when absent, so the in-flight control must fail pre-fix; state was error pre-fix and
the identifier peer_message_rejected does not occur in the 77e0396 source, so both parametrized
malformed assertions must fail pre-fix. All three added controls are non-vacuous by construction.

Model-family independence: request Author model gpt-5, reviewer claude-opus-5.
$ codex_protocol_model.models_are_current_review_pair('gpt-5','claude-opus-5')
→ True (models_are_independent also True)
The Git author of record for the range is the user's committer identity, which records who
committed rather than which model authored; the request's declared Author model carries that
binding.

Cursor at send: 2026-08-01T03:33:15Z
