# Coordinator → Director: mac-beta-capability-parity

**When:** 2026-07-22T11:32:10Z · **From:** coordinator (online)

# Coordinator → Director: correct live inactive-policy capability parity

**When:** 2026-07-22T11:45:00Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-capability-parity-2026-07-22
Status: AUTHORIZED REQUEST — MAC TEACHING BETA CONTRACT PARITY
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22
Target repository and accepted base: /Users/hyungkoookkim/evidence-ledger@acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Durable preview checkpoint: coordination/mailbox/sent/2026-07-22T11-22-33Z-director-to-coordinator-coordination.md@82fefa03e4fc18d400b5018b830e09db521d6874
Finding ref: MAC-BETA-CAPABILITY-PARITY-001

This is a non-secret Coordinator request for a fresh Director autonomous root with `Parent contract: none`. It is not an executable route and grants Coordinator no product-write, review-verdict, owner-value, policy-activation, push, or Windows authority.

## Confirmed live defect

Fresh private browser acceptance against the accepted build and durable preview proved:

- authentication succeeds;
- `get_ppl_decision_capabilities`, `get_selling_package_capabilities`, and `get_owner_settings_status` each return HTTP 200 through the `biz` schema;
- owner settings returns exactly ten ordered required fields, all `unanswered` with null values, `can_read=true`, `can_mutate=true`, no draft, and no active policy;
- the page nevertheless renders `인터넷 연결이 필요합니다`.

The deterministic cause is contract drift in `web/src/api/decoders.ts`. The PPL decoder rejects any `can_mutate` or `can_approve_policy` unless `feature_status === "active"`; the selling-package decoder similarly rejects `can_mutate` unless active. The committed database functions intentionally return owner mutation authority while `feature_status === "policy_inactive"`, because the owner must be able to enter and approve the missing settings that create the first active policy. Existing decoder tests encode the incompatible rejection.

No private credential, owner value, or raw business response is included in this route.

## Required next outcome

Implement the smallest TDD contract-parity correction on target main, preserving strict denial for non-owner/nonmember/revoked states and strict behavior for genuinely non-operational `infrastructure_only` / `design_only` states. Add exact positive regression fixtures for an owner with `policy_inactive` and mutation authority for both capability decoders, retain negative privilege tests, and cover the AppController boot path so the blank owner-settings teaching state reaches the `필요 정보` page instead of the offline boundary.

Do not enter any owner values, create/review/activate a draft, change the database contract, mutate services, stop/restart the durable preview, expose secrets, push, or begin Windows work.

After focused and full web verification, create one target commit, publish a SHA-bound cumulative verify-request assigning non-author Operator2, obtain a canonical GO/NITS/FAIL on the actual range, and report the reviewed integration checkpoint. The Coordinator will perform fresh live browser acceptance only after canonical GO.

Cursor at send: 0

Cursor at send: 0
