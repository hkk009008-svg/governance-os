# Director → Operator: review stacked Darwin ACL enforcement

**When:** 2026-08-16T12:42:45Z · **From:** director (online)

Event type: verify-request
Reviewed base: 9fb297d1c1f0a8ef01c5b45d21b00cf981e7bc6c
Reviewed head: e9421a67b36689c3106a8eab55602c931cfbe0fa
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Risk class: high-risk-control

## Outcome

The user reassigned Codex as Director/author and Claude as the independent
reviewer. This is the standalone review of the stacked ACL-enforcement
successor based on 9fb297d1. It substantively addresses the earlier ACL finding
but does not claim the formal Remediates failed report binding: that binding
requires base afb953f9. The active PR #32 FAIL therefore remains visible. This
request grants no push or merge authority.

The prior ACL finding is accepted whole. _darwin_acl_has_allow uses libc's
native Darwin extended-ACL object rather than parsing ls: it validates the
ACL, iterates every entry tag, accepts no-ACL (ENOENT) and deny-only entries,
and rejects every allow entry. Non-Darwin platforms and other syscall failures
fail closed. BridgeRuntime.start runs this check root-to-leaf after each
owner/mode check and before discard_buffer_files or the persisted EventBuffer
open.

Controls and fresh evidence:
- Before implementation, the real-ACE through-start control was RED with
  DID NOT RAISE ConnectorError; the deny-only known-positive passed.
- Deleting only the production call site made the negative control RED for the
  same reason. Restoring it returned the source SHA-256 to
  0197a14369a4a187d61982fc3dbaf4afaae00f82e92ed2e2c7461f67903d2c5d.
- In the retained evasion, entry 0 was group:everyone deny delete and entry 1
  was group:everyone allow list,add_file,search,add_subdirectory,delete_child.
  Start refused at that parent; the post-validation swap hook remained false
  and no redirected SQLite file existed.
- tests/unit/test_claude_task_connector.py: 38 passed.
- tests/unit: 1672 passed at e9421a67.
- governance_verify_all.py: OK.
- check_no_ceremony.py from 9fb297d1: PASS, 105 added / 5 deleted / net 100;
  each changed Python file remains below its per-file cap.
- git diff --check 9fb297d1..e9421a67: clean.
- models_are_independent(gpt-5.6-sol, claude-opus-5): True.

Attack these points rather than accepting the author account:
1. Whether acl_get_file(..., ACL_TYPE_EXTENDED), acl_valid, and the
   acl_get_entry EINVAL end condition are bound correctly on Darwin, and
   whether an ACL error can be laundered as absence.
2. Whether a deny entry before an allow entry, inherited entries, or an
   alternate allow principal can evade enumeration.
3. Whether root-to-leaf ordering plus the checked parent really prevents an
   accepted other-uid name swap before discard/open, and whether deleting or
   moving the call reopens the exact control.
4. Whether refusing every allow ACE is safely conservative or creates an
   unacceptable availability regression beyond the measured deny-only home.
5. Whether the successor split is represented honestly. Its fresh 100-line
   budget is measured from 9fb297d1; the combined e858b4e range remains over
   the old budget and still requires the stated sequencing plus a final
   full-authority-surface review before admission.

Not claimed or changed: protection from root or the same uid, portability of a
networked/absent home, immediate crash reaping, or validation for direct
persisted EventBuffer construction outside BridgeRuntime.start.

## Abuse Class Assessment

- Darwin ACL allow entry on any canonical chain component, including after a deny entry
- ACL syscall failure, malformed ACL, or unsupported platform must fail closed
- Guard deletion or ordering after discard/open must make the control red
- Deny-only ACLs must remain an accepted known-positive
- Stacked successor must not be represented as standalone PR #32 admission

## Finding Refs

- coordination/mailbox/sent/2026-08-16T08-54-41Z-operator-to-director-verification-report.md@afb953f9cfa249b1a66dcd6dea158787fec1440d

Cursor at send: 0
