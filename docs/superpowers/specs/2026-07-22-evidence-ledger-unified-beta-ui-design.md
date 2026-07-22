# Evidence Ledger Unified Beta UI Design

**Date:** 2026-07-22

**Status:** Approved by owner

**Target:** `/Users/hyungkoookkim/evidence-ledger@bc2e85891f27befe19236686e608f3d45db84d14`

**Selected direction:** A — `차분한 업무도구`

## 1. Purpose

Make the Mac teaching beta look and behave like one coherent Korean business
application. The change covers every user-facing page, not only the owner
settings page. It keeps the product boundary unchanged:

```text
상품 선택
  -> 실제 홈쇼핑 예약안 또는 진행하지 않음
  -> 조건부 실제 PPL 예약안 또는 PPL 없음
  -> 근거가 붙은 최종 추천
```

This design supersedes the one-field-at-a-time owner-center layout in
`2026-07-20-one-user-owner-gates-and-owner-center-design.md` section 6.1. It
does not change the ten-field contract, calculation rules, authorization,
draft/review/activation separation, or external-effect boundaries.

## 2. Design language

The selected direction is a calm work tool rather than a dense executive
dashboard or a wizard that hides the rest of the work.

- One application shell: compact top bar, stable left navigation on wide
  screens, and a single-column navigation treatment on narrow screens.
- One visual system: warm neutral background, white content cards, restrained
  navy/green accents, 8 px spacing rhythm, consistent radii, borders, shadows,
  typography, and focus rings.
- Natural Korean is shown to the user. Internal enum values such as
  `owner_ruling_required` never appear as primary copy.
- Status is communicated with both Korean text and color; color alone is never
  required to understand a result.
- The primary action is visually unique. Save, review, activate, negotiate,
  hold, and logout are not styled as equivalent actions.
- Missing values remain visibly unknown; the UI never invents defaults or
  displays unknown money as zero.

## 3. Information architecture

The stable navigation has three primary destinations:

1. `필요 정보` — owner settings, review, activation, and history.
2. `판매 판단` — product, home-shopping offers, conditional PPL, and result.
3. `근거·이력` — evidence, decision revisions, and recovery status.

The selling workflow keeps a visible four-step indicator:

```text
1 상품 -> 2 홈쇼핑 -> 3 PPL -> 4 추천
```

PPL remains downstream of a home-shopping candidate. `PPL 없음` is always a
real comparison option, not an error or incomplete state.

## 4. Complete page set

### 4.1 Login

- Centered owner-login card with product name, short local-beta explanation,
  email field, password field, show-password control, and one `로그인` action.
- Both required inputs are visible at once and have persistent labels.
- Authentication failures appear next to the form in Korean without revealing
  whether a particular account exists.

### 4.2 Required information

- Show all ten owner-controlled inputs on one page, grouped into
  `수수료율` and `예산과 위험 한도`.
- Each row supports a validated value or explicit `아직 모름` state.
- Show unit, short explanation, field-level error, and saved/unsaved state
  beside the field.
- A sticky summary shows completed, unknown, and unanswered counts.
- `초안 저장` saves the complete edited page as the existing sequence of
  server-authoritative field commands; partial success is reported per field.
- Saving never activates a policy.

### 4.3 Settings review and activation

- Summarize all ten fields without exposing internal codes.
- Keep `초안 저장`, `설정 검토 완료`, and `정책 활성화` as three visibly
  separate stages.
- Activation remains unavailable until the server reports readiness and a
  current review digest.
- The final confirmation explains that recommendations will begin using the
  new policy; it does not imply any booking or payment.

### 4.4 Product and selling setup

- Product is selected first.
- Show selling price, cost, available quantity, decision name, and decision
  deadline in one structured form.
- Keep current draft state visible while moving between selling steps.

### 4.5 Home-shopping offers

- Present candidates in a comparable table/card layout.
- A complete candidate exposes channel, date, start time, price/commission,
  cancellation terms, and evidence status.
- Incomplete candidates are retained but clearly marked `정보 필요` and cannot
  masquerade as bookable recommendations.
- `진행하지 않음` remains available when no suitable slot exists.

### 4.6 Conditional PPL options

- Open only after a home-shopping candidate exists or the user explicitly
  reviews the no-PPL comparison.
- Compare `PPL 없음` with real PPL candidates using supplier, program, air
  date/time, total incremental cost, rights, tax, cancellation, and evidence.
- An incomplete PPL candidate may be saved as a draft but cannot be named as a
  real booking recommendation.

### 4.7 Recommendation

- Lead with one plain-Korean answer: the complete home-shopping booking or no
  suitable slot, followed by the supporting PPL booking or no-PPL.
- Show key economics and evidence grade immediately below the answer.
- Separate `수락 의향 기록`, `협상`, `건너뛰기`, and `근거 보기`.
- These actions record intent only; they do not book, buy, pay, deploy, or send
  anything externally.

### 4.8 Evidence and history

- Distinguish evidence included in the recommendation from expired, excluded,
  or missing evidence.
- Show source, effective time, and decision revision in a readable table.
- Preserve immutable history while keeping private numeric values out of
  general activity copy.

### 4.9 Offline and recovery

- Use the same application shell and components as ordinary pages.
- State whether the user is offline, a command outcome is being recovered, or
  reauthentication is required.
- Never display success until the server response is bound to the submitted
  request and the pending journal is safely cleared.
- Offer one safe next action and preserve fail-closed behavior.

## 5. Shared states and responsive behavior

Every page uses the same loading skeleton, empty state, inline validation,
error banner, success notice, confirmation dialog, status badge, and button
hierarchy. Raw exceptions, operation names, UUIDs, and wire codes stay behind
an optional technical-details disclosure.

The Mac teaching layout targets laptop widths first. At narrower widths, the
sidebar becomes a compact top navigation, tables become labeled cards, and
forms become one column. No core action or status may require horizontal
scrolling. Keyboard order follows the visual order, focus is always visible,
and dialogs return focus to their invoking control.

## 6. Data and security boundaries

- Reuse the existing typed APIs, decoders, command runner, and recovery model.
- Do not place private owner values or command bodies in Local Storage,
  IndexedDB, Cache Storage, URLs, analytics, logs, screenshots, or fixtures.
- Keep server state authoritative. UI aggregation of the ten settings changes
  presentation and command sequencing only; it does not introduce a bulk
  bypass around per-field validation, revision binding, review, or activation.
- No new dependency or UI framework is required. Extend the current React and
  CSS implementation with small shared components.

## 7. Implementation shape

The implementation should be one reviewed UI slice with three internal parts:

1. Shared shell and design tokens in the existing app/style layer.
2. Login and owner-settings composition, including all-ten-fields presentation.
3. Selling, evidence, and recovery pages migrated to the shared components.

The slice may refactor presentation components, but it must not change domain
calculations, database schemas, RPC inventories, authorization, or booking
effects. Behavior-changing work belongs to a Director and requires a distinct,
non-author Operator review of the actual range before integration.

## 8. Acceptance criteria

- All nine page states above render through the same application shell.
- Login visibly contains both email and password fields.
- Required information visibly contains all ten fields on one page.
- Korean user copy contains no primary raw wire-state labels.
- Product -> home-shopping -> conditional PPL -> recommendation ordering is
  preserved in navigation and tests.
- Missing data, offline state, auth failure, and ambiguous command recovery are
  visually distinct and fail closed.
- Saving owner information cannot activate policy; activation remains an
  explicit reviewed command.
- No recommendation names an incomplete home-shopping or PPL booking as real.
- Existing authorization, strict-decoder, recovery, PWA, and business-workflow
  tests remain green; focused UI tests cover the changed page behavior.
- A manual Mac acceptance pass checks laptop and narrow-window layouts, Korean
  copy, keyboard navigation, visible focus, and the teaching flow.

## 9. Explicit non-goals

- No iOS work.
- No Windows packaging in this slice.
- No generic analytics dashboard or chatbot.
- No external booking, payment, email, deployment, or real-policy activation.
- No invented business values and no automatic filling of the ten owner fields.
- No new component framework, telemetry stack, or design-system service.
