# One-User Owner Gates and Owner Center Design

**Date:** 2026-07-20
**Status:** Owner choices approved; awaiting written-spec review
**Target:** `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`
**Accepted target base:** `41d9f1d846d6e0928b520573094ae59846114df5`

## 1. Purpose

Replace the inherited two-person owner quorum with the product the owner has
now specified: one operational user, one laptop, one installed Windows PWA,
one persistent owner session, and one owner approval for formula, risk/action,
format, and activation decisions.

The same product also gains a Korean-first `필요 정보` owner center. It lists
missing configuration, lets the owner save private values later, explains how
to obtain unknown values, and keeps incomplete policy state fail-closed. It is
not a generic administration console and it does not book, buy, deploy, or
infer private business limits.

This design supersedes only the product's two-owner assumptions and the older
Gate B/C/D hold. It preserves the accepted product-first sequence:

```text
product
  -> one real home-shopping booking or no suitable slot
  -> supporting PPL booking or no-PPL
```

## 2. Product identity and authority

### 2.1 One operational principal

- Exactly one operational owner account is provisioned for this private
  deployment.
- The PWA has no user switcher and presents no second-owner or approval-match
  workflow.
- Ordinary use stays in one persistent authenticated owner session. Device and
  operating-system sign-in provide the outer laptop boundary; the PWA does not
  add a separate launch PIN.
- Policy activation always requires an explicit Korean confirmation. A saved
  field or completed draft never activates policy by itself.

Authorization remains fail-closed. Existing membership, revoked, nonmember,
and viewer-shaped wire states may remain for backward compatibility and
negative tests, but they are not additional product personas. Mutations still
require the one current active owner. A deployment with zero or multiple
current active owners cannot activate a new policy.

### 2.2 Quorum migration

New formula, risk/action, Gate-D, and activation records use a versioned
single-owner quorum. One independently authenticated current owner records one
digest-bound approval. Activation rechecks that the same owner is still active
inside the activation transaction.

Existing append-only two-owner history is never rewritten or reinterpreted.
Restoring an older policy copies it into a new single-owner draft and requires
a new review and activation; it does not mutate the historical record.

## 3. Gate B: financial formula contract

Gate B's public semantics are resolved as follows. Private numeric rates that
are not already authoritative remain required owner inputs; the application
must not invent them.

1. The target metric is incremental campaign contribution in KRW.
2. Scenario entry uses `target_lines`.
3. Commission mapping is:
   - `정률`, `반특`, `완특`, `직매입`, and `반반특` use `linear_rate` only
     when a valid owner-provided rate is present;
   - `정액`, null, and unsettled commission terms are deliberately
     non-evaluable and return `NEEDS_INFO`.
4. Scenario inputs are net of returns and cancellations.
5. The counterfactual method is `owner_manual_without_ppl`.
6. Only incremental costs enter the decision. Existing costs cancel from the
   comparison. The PPL quote, nonrecoverable VAT, agency fee, production cost,
   and other incremental cost are each deducted exactly once. Slot, vendor,
   or set costs are not deducted again unless represented by one of those
   explicit incremental fields.
7. Package economics are campaign-level. The canonical allocation mode is
   `campaign_level_action_no_target_break_even`. A mixed set of participating
   rates may still produce a campaign contribution, cost, ceiling, and action;
   it does not become `NEEDS_INFO` merely because a single target denominator
   is unavailable.
8. Required campaign contribution to break even is always returned when cost
   is calculable. Sales break-even is returned only when exactly one supported,
   positive `linear_rate` denominator participates. Unit break-even is
   unavailable. Mixed or unsupported denominators leave sales and unit
   break-even null with an explanatory non-blocking reason.
9. Scenario timing follows the target home-shopping slot. Budget commitment is
   assigned separately from immutable `booked_at` in the business timezone.
10. Owner money inputs are whole KRW. Calculations retain six decimal places,
    use `half_up`, round at `final_only`, return final KRW at scale zero, and
    apply policy thresholds to post-round values. Negative scenario values are
    allowed and remain visible.

The existing evaluator currently treats mixed denominators as calculation-
blocking and does not consume the stored `package_allocation_mode`. The
implementation must correct both behaviors with a failing regression first.

## 4. Gate C: risk and action contract

### 4.1 Required private limits

All five owner-controlled amounts are enabled and required before initial
activation:

- choice-set budget;
- monthly PPL budget;
- downside-loss limit;
- experimental budget; and
- risk reserve.

Their actual values are not known in this design. Each remains private,
uncommitted, and unset until the owner enters a valid whole-KRW amount in the
owner center. No synthetic fixture, prior workbook figure, inferred history,
or calculated suggestion may become a default.

The business timezone is `Asia/Seoul`. Monthly commitment uses the calendar
month containing immutable `booked_at` in that timezone.

### 4.2 Allowed decisions

- Manual `BUY` is allowed as a recorded owner intent only.
- Pilot `TEST` is allowed as a recorded owner intent only.
- Neither action performs an external booking. A booking-capable surface and
  its effect require a separate design, review, and exact authorization.
- Evidence is displayed before any owner action.
- Non-financial strategy text is descriptive. It cannot change the calculated
  action, though the owner may separately hold or decline a recommendation.

### 4.3 Server-owned eligibility and precedence

The server, not JavaScript, computes explicit composite eligibility facts for
`BUY`, `TEST`, and `NEGOTIATE`. `TEST` eligibility includes the choice-set's
`experimental_allowed` value, pilot permission, experimental budget, and all
shared calculation, constraint, monthly, choice-set, and downside checks.
`NEGOTIATE` eligibility requires an exact positive scenario-based quote
ceiling.

The action precedence is exactly:

1. `NEEDS_INFO` for inactive policy, missing or unknown required facts,
   invalid scenarios, unsupported calculation inputs, or non-evaluable Gate-B
   mappings;
2. hard `SKIP` for failed constraints, withdrawn or expired offers, or an
   exceeded hard budget/downside boundary;
3. `BUY` when the server-owned BUY eligibility and approved action rule match;
4. `TEST` when TEST and NEGOTIATE could both apply and the owner explicitly
   enabled the experimental choice;
5. `NEGOTIATE` otherwise when its positive exact ceiling is available;
6. fallback `SKIP`.

The current evaluator checks `experimental_allowed` in its hard TEST guard but
omits it from the action facts supplied to policy selection. The implementation
must add the server-owned eligibility facts and prove the false and true cases
with regression tests. A policy rule that asks for an ineligible action fails
closed.

## 5. Gate D: initial input format

Gate D is `manual_only`.

One current owner records the digest-bound ruling and a capability reread must
report `manual_only` before the disposition is effective. The older
two-owner matching requirement is removed for the single-owner schema
revision.

Once effective, Task 4 is recorded exactly `SKIPPED-NOT-APPLICABLE`; no Task-4
CSV/XLSX implementation or production commit is created. CSV, XLSX, PDF,
email, image, KakaoTalk, and AI extraction remain outside this milestone.

## 6. Korean owner center

### 6.1 Layout

The selected layout is **상태판 + 단계별 입력**.

The page groups configuration into `재무 공식`, `위험·행동 정책`, and
`입력 방식`. The status area always shows what is active, what is in draft,
and which items need information. The main pane focuses on one next required
field and provides `저장하고 다음` plus `나중에` actions.

All user-facing copy is natural Korean and all money is labeled in KRW. Stable
wire enums, reason codes, operation names, and database identifiers stay in
English.

### 6.2 Missing-information behavior

- A persistent `설정 필요` badge and non-blocking banner replace an external
  reminder.
- The owner may mark a field `아직 모름`. The server stores that explicit
  state without fabricating a value, and the page explains where the owner can
  find the information.
- An unknown field blocks only the policy or action that requires it. Before
  the first complete activation, calculated actions remain policy-inactive.
- If a valid policy is already active, editing an incomplete replacement does
  not disturb it; the banner describes the draft, while recommendations keep
  using the immutable active version.

### 6.3 Draft, review, activation, and history

Owner-center data is server-authoritative. Unsaved form state is memory-only;
saved drafts live in the protected database and never in Local Storage,
IndexedDB, Cache Storage, URLs, logs, analytics, screenshots, or committed
fixtures.

The lifecycle is:

```text
active policy or no policy
  -> private server-side draft
  -> field validation and completeness summary
  -> Korean review screen
  -> explicit 정책 활성화 confirmation
  -> immutable active policy version
```

Edits to an active policy always create a replacement draft. Saving never
changes live recommendations. Activation atomically validates completeness,
the single current owner, all digests, and the expected active revision before
switching versions.

Version history records activation time, the owner identity, immutable digests,
and which fields changed without exposing secret values in general activity
copy. Restore means copy-to-new-draft followed by normal review and activation.

## 7. API and component boundaries

The ordinary product-first selling workflow remains unable to call the seven
raw operations-only PPL commands. The owner center uses a separate, closed,
typed operations facade whose inventory is limited to:

- read current configuration status and completeness;
- read one owner-scoped draft;
- save or mark unknown one validated draft field;
- review the complete draft summary;
- activate the reviewed draft; and
- copy one historical version into a new draft.

The implementation plan must assign exact RPC names and DTO shapes after an
impact audit of the current frozen PPL and additive selling-package contracts.
It may add a new versioned owner-settings contract; it must not silently widen
either accepted ordinary adapter union.

Command bodies stay in memory. Ambiguous owner-center commands use the same
actor-scoped, metadata-only recovery principle as the ordinary PWA, in a
separate operation namespace. Logout, actor change, offline transition, auth
failure, or malformed recovery state clears private in-memory state and blocks
owner-center mutation until recovery is resolved.

## 8. Error handling

- Unknown or incomplete required data returns a fixed Korean `설정 필요`
  state, not a guessed result.
- Stale draft or active-version bindings reject activation and require a fresh
  reread.
- Zero or multiple active owners reject activation.
- Invalid KRW, decimal, enum, digest, or state transitions fail before any
  partial policy write.
- Offline and transport-unavailable states expose no cached business or policy
  data and permit no mutation.
- Expected server errors map to fixed Korean copy. Unknown or malformed errors
  are redacted and do not echo command bodies or private values.

## 9. Implementation decomposition and review

This design is implemented as two sequential, independently reviewed
subprojects:

1. **Single-owner policy foundation and evaluator correction.** Amend factual
   contracts and append-only decision history, add the versioned single-owner
   quorum, record Gate-D `manual_only`, encode the Gate-B/C symbolic policy,
   correct mixed-denominator/package-allocation behavior, and add server-owned
   eligibility facts. Private limits remain unset and no activation occurs.
2. **Owner-center API and Windows PWA.** Add the isolated owner-settings
   contract, protected draft/version surfaces, Korean status-plus-step UI,
   recovery behavior, and synthetic accessibility/security tests. Activation
   is implemented locally but is not executed against a managed project.

Each behavior-changing commit receives actual-range review from a non-author
Operator on a different model. Money math, quorum/auth, RLS/grants, operation
allowlists, private-data handling, and fail-closed negatives are mandatory
review surfaces.

## 10. Verification and acceptance

Acceptance requires synthetic tests proving at least:

- one current owner can approve and activate a complete reviewed draft;
- zero owners, multiple owners, stale owner state, mismatched digests, and
  partial drafts cannot activate;
- historical two-owner records remain immutable and restorable only through a
  new draft;
- every Gate-B mapping, cost, rounding, negative-value, mixed-denominator, and
  break-even rule above;
- every Gate-C precedence branch, including `experimental_allowed=false` and
  true, exact positive negotiation ceiling, missing limits, and hard skips;
- `manual_only` becomes effective only after its single-owner record and
  capability reread, and no Task-4 import surface is added;
- Korean status, unknown, review, activation, history, restore, offline,
  logout, actor-change, stale-draft, and redacted-error flows;
- the ordinary PPL and selling-package adapters still reject operations-only
  names and client-side economics;
- no real owner value, workbook content, credential, command body, or business
  response enters git, browser persistence, logs, caches, or screenshots.

Local GO authorizes no managed database mutation, policy activation,
deployment, Windows installation, real-data use, provider contact, booking,
spend, integration, publication, or other external effect. Each remains a
separate exact owner authorization after the reviewed implementation exists.

## 11. Supersession result

After this design is reviewed and its implementation plans are committed, a
new coordinator route may supersede
`coordination/mailbox/sent/2026-07-19T16-01-59Z-coordinator-to-all-coordination.md@bf217ebb0a9cdd2a87198057ce31fdd13f99ca74`.
That route will mark the two-owner Gate B/C/D requirement superseded, record
the public decisions above, keep private amounts and runtime activation
incomplete, and route only the first reviewed local implementation slice.
