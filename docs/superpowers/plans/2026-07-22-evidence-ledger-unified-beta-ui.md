# Evidence Ledger Unified Beta UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Use superpowers:test-driven-development for each behavior change and superpowers:verification-before-completion before any completion claim.

**Goal:** Replace the visually fragmented Mac teaching beta with one professional Korean UI that exposes both login inputs, all ten owner settings on one page, and the complete product-first selling workflow through recommendation, evidence, and recovery.

**Architecture:** Keep every existing API, decoder, command runner, security fence, and product decision rule unchanged. Add one small application shell and presentation-only copy helpers, replace the progressive owner-setting editor with an in-memory ten-field editor that still issues the existing per-field commands sequentially, and compose the current selling pages into the same shell. The Director owns implementation; one distinct non-author Operator reviews the cumulative actual range after all three implementation commits because no intermediate commit has a consumer.

**Tech Stack:** React 19, TypeScript 7, Vite 8, Vitest 4, Testing Library, Playwright 1.61, existing CSS only.

## Global Constraints

- Design authority: `docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md` on the immutable Pipeline route revision.
- Accepted product base: `/Users/hyungkoookkim/evidence-ledger@bc2e85891f27befe19236686e608f3d45db84d14`.
- Preserve pre-existing untracked `/Users/hyungkoookkim/evidence-ledger/.vscode/` and `/Users/hyungkoookkim/evidence-ledger/web/node_modules` without staging, replacing, or deleting them.
- Use an isolated evidence-ledger worktree created with `superpowers:using-git-worktrees`; do not implement in the running root checkout.
- Do not change database schemas, RPC inventories, wire DTOs, strict decoders, calculation rules, authorization, command recovery ordering, service-worker security, or external-effect boundaries.
- Do not add a package, component framework, icon library, telemetry system, font download, or network dependency.
- User-facing copy is natural Korean. Raw operation names, state enums, UUIDs, hashes, and reason codes may appear only inside an explicitly opened technical-details disclosure.
- The ten owner values remain server-authoritative or in React memory. They never enter Local Storage, IndexedDB, Cache Storage, URLs, logs, analytics, screenshots, or committed fixtures.
- `초안 저장`, `설정 검토 완료`, and `정책 활성화` remain distinct. Saving fields never activates policy.
- Preserve product order: product -> complete home-shopping candidate or no suitable slot -> conditional PPL or no-PPL -> recommendation.
- No screen or button performs booking, purchase, payment, email, deployment, policy activation against real data, or another external effect.
- No iOS work and no Windows packaging in this slice.
- Use synthetic test data only. A live Mac preview restart happens only after integration and under its separate user-authorized effect boundary.
- Preserve Playwright port `4173` as the default. On this Mac only, run isolated browser tests with validated environment override `EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174`; never reuse, stop, restart, replace, or rebind the teaching preview on `127.0.0.1:4173`.
- One cumulative non-author Operator actual-range verdict is required before integration. The Operator must be a distinct seat and different model from the Director and cannot have authored the range.

## File Map

| Path | Responsibility |
|---|---|
| `web/src/app/AppShell.tsx` | Shared ready, signed-out, offline, unavailable, and recovery presentation shell |
| `web/src/app/App.tsx` | Phase composition, workspace selection, owner sequential save orchestration, existing data mapping |
| `web/src/main.tsx` | One global import of the application stylesheet |
| `web/playwright.config.ts` | Strict numeric test-only loopback port override while preserving default 4173 |
| `web/e2e/pwa.spec.ts` | Keep the cumulative PWA contract bound to the validated loopback origin and current owner-editor label |
| `web/src/styles/app.css` | Tokens, shell, cards, controls, tables, dialogs, responsive and focus behavior |
| `web/src/features/auth/LoginView.tsx` | Two-field Korean login card and show-password control |
| `web/src/features/recovery/RecoveryPanel.tsx` | Korean recovery state presentation with raw metadata behind details |
| `web/src/features/owner-settings/owner-settings-form.ts` | Pure in-memory editor, dirty-input ordering, and successful-response reconciliation |
| `web/src/features/owner-settings/OwnerSettingsForm.tsx` | All ten fields, unknown toggles, per-row status, and one draft-save action |
| `web/src/features/owner-settings/OwnerSettingsPage.tsx` | Owner settings status/form/review/history page composition |
| `web/src/features/owner-settings/copy.ts` | Owner field, format, and state Korean copy |
| `web/src/features/selling-decision/selling-copy.ts` | Exhaustive user-facing copy for actions, offer states, evidence grades, and history kinds |
| `web/src/features/selling-decision/SellingDecisionWorkspace.tsx` | Four-step workflow plus dedicated evidence/history destination |
| `web/src/features/selling-decision/{ProductPage,HsOffersPage,PplOptionsPage,RecommendationPage,EvidencePanel,RevisionHistory,OwnerDecisionPanel}.tsx` | Existing behavior rendered with the shared layout and answer-first hierarchy |
| `web/src/**/*.{test.ts,test.tsx}` | Focused unit, integration, copy, security, and accessibility coverage |
| `web/e2e/{owner-settings,workflow,security}.spec.ts` | Synthetic browser acceptance for the complete teaching path and privacy fences |
| `ARCHITECTURE.md`, `OPERATIONS.md` | Factual UI topology and exact verified gate summaries after the final run |

---

### Task 1: Shared application shell, login, and static/recovery states

**Files:**
- Create: `web/src/app/AppShell.tsx`
- Create: `web/src/app/AppShell.test.tsx`
- Modify: `web/src/app/App.tsx:435-488`
- Modify: `web/src/main.tsx`
- Modify: `web/src/features/auth/LoginView.tsx`
- Modify: `web/src/features/recovery/RecoveryPanel.tsx`
- Modify: `web/src/components/AsyncState.tsx`
- Modify: `web/src/styles/app.css`
- Modify: `web/src/app/AppController.test.ts`
- Modify: `web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx:39-63`

**Interfaces:**
- Consumes: the existing `ConfiguredApp` phase snapshot, `logout()`, and `ReactNode` workspace bodies.
- Produces: `PrimaryWorkspace = "owner" | "decision" | "evidence"`, `AppShell`, `StandaloneShell`, and a `ReadyWorkspaceSwitcher` that keeps the one decision subtree mounted while switching between workflow and evidence modes.

- [ ] **Step 1: Write failing shell and login tests.**

Create `AppShell.test.tsx` with assertions equivalent to:

```tsx
function Harness() {
  const [workspace, setWorkspace] = useState<PrimaryWorkspace>("owner");
  const body = workspace === "owner"
    ? "필요 정보 내용"
    : workspace === "decision" ? "판매 판단 내용" : "근거와 이력 내용";
  return (
    <AppShell workspace={workspace} canMutateOwnerSettings canMutateDecision
      message={null} onWorkspaceChange={setWorkspace} onLogout={vi.fn()}>
      <p>{body}</p>
    </AppShell>
  );
}

it("renders one Korean shell with three stable destinations", async () => {
  const user = userEvent.setup();
  render(<Harness />);
  expect(screen.getByRole("navigation", { name: "주요 메뉴" })).toBeVisible();
  expect(screen.getByRole("button", { name: "필요 정보" })).toHaveAttribute("aria-current", "page");
  await user.click(screen.getByRole("button", { name: "판매 판단" }));
  expect(screen.getByText("판매 판단 내용")).toBeVisible();
  await user.click(screen.getByRole("button", { name: "근거·이력" }));
  expect(screen.getByText("근거와 이력 내용")).toBeVisible();
});

it("keeps email and password visible together and toggles only password visibility", async () => {
  render(<LoginView onLogin={vi.fn()} busy={false} message={null} />);
  expect(screen.getByRole("textbox", { name: "이메일" })).toBeVisible();
  const password = screen.getByLabelText("비밀번호");
  expect(password).toHaveAttribute("type", "password");
  await userEvent.click(screen.getByRole("button", { name: "비밀번호 표시" }));
  expect(password).toHaveAttribute("type", "text");
});
```

Update the existing workspace-switcher tests to use `필요 정보`, `판매 판단`, and `근거·이력`, and prove that returning to either decision destination preserves the same stateful subtree.

- [ ] **Step 2: Run the focused tests and verify RED.**

Run:

```bash
cd web
npx vitest run src/app/AppShell.test.tsx src/app/AppController.test.ts \
  src/features/selling-decision/SellingDecisionWorkspace.test.tsx
```

Expected: failure because `AppShell.tsx`, the third destination, and the show-password control do not exist.

- [ ] **Step 3: Implement the minimal shell contract.**

Use this public shape in `AppShell.tsx`:

```tsx
export type PrimaryWorkspace = "owner" | "decision" | "evidence";

export interface AppShellProps {
  readonly workspace: PrimaryWorkspace;
  readonly canMutateOwnerSettings: boolean;
  readonly canMutateDecision: boolean;
  readonly message: string | null;
  readonly onWorkspaceChange: (workspace: PrimaryWorkspace) => void;
  readonly onLogout: () => void;
  readonly children: ReactNode;
}

export function AppShell(props: AppShellProps) {
  const items = [
    ["owner", "필요 정보"],
    ["decision", "판매 판단"],
    ["evidence", "근거·이력"],
  ] as const;
  return (
    <div className="app-shell">
      <header className="app-topbar"><strong>판매 의사결정</strong></header>
      <nav className="app-sidebar" aria-label="주요 메뉴">
        {items.map(([id, label]) => (
          <button key={id} type="button" aria-current={props.workspace === id ? "page" : undefined}
            onClick={() => props.onWorkspaceChange(id)}>{label}</button>
        ))}
        <button type="button" onClick={props.onLogout}>로그아웃</button>
      </nav>
      <main className="app-content">{props.message === null ? null : <p role="status">{props.message}</p>}{props.children}</main>
    </div>
  );
}
```

`ReadyWorkspaceSwitcher` must accept a decision render function so workflow and evidence share one mounted `DecisionWorkspaceCenter`:

```ts
decision: (surface: "workflow" | "evidence") => ReactNode
```

Do not duplicate the decision controller or issue a second source load merely to show evidence.
Move the global `app.css` import to `main.tsx` and remove the feature-local CSS
import from `SellingDecisionWorkspace.tsx`, so signed-out and recovery screens
receive the same tokens without relying on an unrelated feature module.

- [ ] **Step 4: Apply the same shell language to login and recovery.**

- Wrap login in `StandaloneShell` with a labelled card, both persistent labels, a `showPassword` boolean, and one primary submit action.
- Render loading, offline, unavailable, and recovery through the same standalone shell and shared notice classes.
- Map the pending recovery operation to fixed Korean copy such as `필요 정보 저장`, `판매 판단 저장`, or `판단 결과 기록`; keep the raw operation and timestamp only inside `<details><summary>기술 정보</summary>…</details>`.
- Keep all existing retry, continue, and two-step retirement callbacks unchanged.

- [ ] **Step 5: Replace the minimal stylesheet with reusable tokens and responsive primitives.**

Define color, spacing, radius, shadow, content-width, and focus variables under `:root`; then implement `.app-shell`, `.app-topbar`, `.app-sidebar`, `.app-content`, `.page-header`, `.panel`, `.notice`, `.button-primary`, `.button-secondary`, `.button-ghost`, `.form-grid`, `.table-wrap`, `.status-badge`, and dialog styles. At `max-width: 860px`, convert the sidebar to wrapped top navigation and every form grid to one column. Preserve the current 3 px visible focus ring and minimum 44 px control height.

- [ ] **Step 6: Run focused tests and typecheck.**

```bash
cd web
npx vitest run src/app/AppShell.test.tsx src/app/AppController.test.ts \
  src/features/selling-decision/SellingDecisionWorkspace.test.tsx
npm run typecheck
```

Expected: all selected tests pass and TypeScript exits 0.

- [ ] **Step 7: Commit Task 1.**

```bash
git add -- web/src/app/AppShell.tsx web/src/app/AppShell.test.tsx \
  web/src/app/App.tsx web/src/main.tsx web/src/features/auth/LoginView.tsx \
  web/src/features/recovery/RecoveryPanel.tsx web/src/components/AsyncState.tsx \
  web/src/styles/app.css web/src/app/AppController.test.ts \
  web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx
git commit -m "feat(web): add unified Korean application shell"
```

---

### Task 2: All-ten-fields owner settings editor

**Files:**
- Create: `web/src/features/owner-settings/owner-settings-form.ts`
- Create: `web/src/features/owner-settings/owner-settings-form.test.ts`
- Create: `web/src/features/owner-settings/OwnerSettingsForm.tsx`
- Delete: `web/src/features/owner-settings/OwnerSettingStep.tsx`
- Modify: `web/src/features/owner-settings/OwnerSettingsPage.tsx`
- Modify: `web/src/features/owner-settings/OwnerSettingsPage.test.tsx`
- Modify: `web/src/features/owner-settings/OwnerSettingsStatus.tsx`
- Modify: `web/src/features/owner-settings/OwnerSettingsReview.tsx`
- Modify: `web/src/features/owner-settings/OwnerSettingsHistory.tsx`
- Modify: `web/src/features/owner-settings/copy.ts`
- Modify: `web/src/app/App.tsx:348-433`
- Modify: `web/e2e/owner-settings.spec.ts`
- Modify: `web/e2e/workflow.spec.ts`
- Modify: `web/e2e/security.spec.ts`
- Modify: `web/playwright.config.ts`

**Interfaces:**
- Consumes: ordered `OwnerSettingsView.status.fields`, existing `OwnerSettingInput`, and the unchanged `saveOwnerSetting(input): Promise<OwnerSettingsView>` command boundary.
- Produces: `OwnerSettingsEditor`, `editorFromView`, `updateEditorField`, `dirtyOwnerInputs`, `reconcileSavedField`, and `markOwnerSettingSaveError`; `OwnerSettingsForm` emits one ordered immutable array of dirty `OwnerSettingInput` values.

- [ ] **Step 1: Write failing pure-state and page tests.**

The pure helper tests must prove:

```ts
expect(Object.keys(editorFromView(incompleteView()))).toHaveLength(10);
expect(dirtyOwnerInputs(edited, incompleteView().status.fields)).toEqual([
  { field_code: "linear_rate_regular", state: "value", value: "0.25" },
  { field_code: "linear_rate_half_special", state: "unknown", value: null },
]);
expect(reconcileSavedField(edited, returnedView, "linear_rate_regular").linear_rate_half_special.value)
  .toBe("unsaved-local-value");
```

Replace the progressive-editor expectations with page assertions that all ten labelled inputs are visible simultaneously, no business default is inserted, `아직 모름` changes local state without issuing a command, and `초안 저장` issues dirty commands in server order. Add a partial-failure case in which the first returned view is retained, the failed row says `저장하지 못함`, later rows remain unsaved, and no review or activation call occurs.

- [ ] **Step 2: Run focused tests and verify RED.**

```bash
cd web
npx vitest run \
  src/features/owner-settings/owner-settings-form.test.ts \
  src/features/owner-settings/OwnerSettingsPage.test.tsx
```

Expected: failure because the form helpers and all-fields presentation do not exist.

- [ ] **Step 3: Implement the memory-only editor.**

Use these exact state boundaries:

```ts
export interface OwnerSettingEditorRow {
  readonly code: OwnerSettingFieldCode;
  readonly mode: "value" | "unknown";
  readonly value: string;
  readonly saved: OwnerSettingInput | null;
  readonly result: "idle" | "saved" | "error";
}

export type OwnerSettingsEditor = Record<OwnerSettingFieldCode, OwnerSettingEditorRow>;
```

`editorFromView` follows `view.status.fields` order, reads values from the
matching `view.draft.fields`, and converts `unanswered` to an empty value-mode
row, `unknown` to unknown mode, and `value` to its canonical string.
`dirtyOwnerInputs(editor, orderedFields)` compares the current payload with
`saved`, returns only changed rows, and preserves the server-supplied field
order. `reconcileSavedField` replaces only the submitted row with server truth
while preserving every other unsaved local row.

- [ ] **Step 4: Render all ten fields in two groups.**

`OwnerSettingsForm` renders `수수료율` and `예산과 위험 한도`, five rows each. Every row contains a persistent label, help text, unit, input, `아직 모름` checkbox/button, and text status. The summary uses derived counts:

```ts
const completed = rows.filter((row) => row.mode === "value" && row.value !== "").length;
const unknown = rows.filter((row) => row.mode === "unknown").length;
const unanswered = rows.length - completed - unknown;
```

There is one `초안 저장` primary button. It is disabled when capability is absent, a save is running, or no row is dirty. Do not autofocus any one business field; focus the page heading after load and the first failed row after a partial failure.

- [ ] **Step 5: Sequence existing commands without adding a bulk endpoint.**

In `OwnerSettingsCenter`, replace `inputValue`, `selectedFieldCode`, `serverOrderedNextField`, and `onLater` with `editor` and `saveResults`. On save:

```ts
let latestView = state.view;
for (const input of dirtyOwnerInputs(editor, latestView.status.fields)) {
  try {
    latestView = await controller.saveOwnerSetting(input);
    setState({ kind: "ready", view: latestView });
    setEditor((current) => reconcileSavedField(current, latestView, input.field_code));
  } catch {
    setEditor((current) => markOwnerSettingSaveError(current, input.field_code));
    break;
  }
}
```

Disable the form during the loop. Stop on the first failure so expected-head and command-journal ordering remain authoritative. Never retry automatically. Keep review, confirmation, activation, restore, and current controller methods unchanged.

- [ ] **Step 6: Make status, review, and history professional without exposing raw states.**

- Map `owner_ruling_required` to `소유자 결정 필요`, `manual_only` to `직접 입력`, and `manual_csv_xlsx` to `파일 입력` in `copy.ts`.
- Render status counts as badges/cards, review values as a two-group definition list, and history as compact cards.
- Use the existing `ConfirmDialog` for activation and keep private values and digests out of the closed dialog body; put immutable IDs in a collapsed technical-details section if retained.
- Keep `설정 검토 완료` and `정책 활성화` separately enabled only by server truth.

- [ ] **Step 7: Add a strict test-only Playwright port override.**

In the existing `VITEST=true` branch of `web/e2e/security.spec.ts`, first add
failing tests for the exported parser:

```ts
unitTest("accepts only a bounded numeric Playwright loopback port", () => {
  unitExpect(parsePlaywrightLoopbackPort(undefined)).toBe(4173);
  unitExpect(parsePlaywrightLoopbackPort("4174")).toBe(4174);
  for (const value of ["", "0", "1023", "65536", "4174;touch-x", "+4174", "04174"]) {
    unitExpect(() => parsePlaywrightLoopbackPort(value)).toThrow("invalid Playwright loopback port");
  }
});
```

Run `npx vitest run e2e/security.spec.ts` and require RED because the parser is
missing. Then implement only this test-harness correction in
`web/playwright.config.ts`:

```ts
export function parsePlaywrightLoopbackPort(raw: string | undefined): number {
  if (raw === undefined) return 4173;
  if (!/^[1-9][0-9]{3,4}$/.test(raw)) throw new Error("invalid Playwright loopback port");
  const port = Number(raw);
  if (!Number.isSafeInteger(port) || port < 1024 || port > 65_535) {
    throw new Error("invalid Playwright loopback port");
  }
  return port;
}

const loopbackPort = parsePlaywrightLoopbackPort(process.env.EVIDENCE_LEDGER_PLAYWRIGHT_PORT);
export const LOOPBACK_ORIGIN = `http://127.0.0.1:${loopbackPort}`;
```

Use the validated numeric `loopbackPort` in the existing Vite preview command.
Keep `reuseExistingServer: false`. Default behavior remains exactly 4173; the
environment value changes only the ephemeral synthetic test server and the
matching backend allowlist in that Playwright process.

- [ ] **Step 8: Update synthetic browser coverage.**

Change the owner-settings E2E flow to fill/toggle multiple visible rows before pressing `초안 저장`; assert that the backend receives `save_owner_settings_field` once per dirty row in field order. Keep the storage inspection during a held command and prove that neither the first nor later unsaved value appears in Local Storage, Session Storage, Cache Storage, IndexedDB, URLs, or unexpected traffic. Update transport-loss cases to use `초안 저장` and assert fail-closed unmounting remains unchanged.

- [ ] **Step 9: Run Task 2 gates.**

```bash
cd web
npx vitest run \
  src/features/owner-settings/owner-settings-form.test.ts \
  src/features/owner-settings/OwnerSettingsPage.test.tsx \
  src/app/AppController.test.ts
npm run typecheck
npm run build:ci
lsof -nP -iTCP:4174 -sTCP:LISTEN
EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test \
  e2e/owner-settings.spec.ts e2e/security.spec.ts
```

Expected: `lsof` exits 1 with no listener before the test; all selected tests
pass, the ephemeral 4174 listener exits with Playwright, build exits 0,
private-state checks remain empty, and unexpected synthetic traffic is `[]`.

- [ ] **Step 10: Commit Task 2.**

```bash
git add -- web/playwright.config.ts web/src/app/App.tsx web/src/features/owner-settings \
  web/e2e/owner-settings.spec.ts web/e2e/workflow.spec.ts web/e2e/security.spec.ts
git commit -m "feat(web): show all owner settings on one page"
```

---

### Task 3: Unified selling, evidence, and answer-first recommendation pages

**Files:**
- Create: `web/src/features/selling-decision/selling-copy.ts`
- Create: `web/src/features/selling-decision/selling-copy.test.ts`
- Modify: `web/src/app/App.tsx:122-202,205-345,474-488`
- Modify: `web/src/features/selling-decision/SellingDecisionWorkspace.tsx`
- Modify: `web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx`
- Modify: `web/src/features/selling-decision/ProductPage.tsx`
- Modify: `web/src/features/selling-decision/HsOffersPage.tsx`
- Modify: `web/src/features/selling-decision/PplOptionsPage.tsx`
- Modify: `web/src/features/selling-decision/RecommendationPage.tsx`
- Modify: `web/src/features/selling-decision/EvidencePanel.tsx`
- Modify: `web/src/features/selling-decision/RevisionHistory.tsx`
- Modify: `web/src/features/selling-decision/OwnerDecisionPanel.tsx`
- Modify: `web/src/features/selling-decision/accessibility.test.tsx`
- Modify: `web/src/styles/app.css`
- Modify: `web/e2e/workflow.spec.ts`

**Interfaces:**
- Consumes: existing decoded selling sources, `SellingWorkspaceModel`, command actions, and page-continuation controls.
- Produces: `SellingDecisionWorkspace.surface: "workflow" | "evidence"`, Korean exhaustive copy helpers, an extended presentation-only `HsOfferView`, and a fail-closed answer-first recommendation presentation.

- [ ] **Step 1: Write failing copy, navigation, and recommendation tests.**

Cover exact mappings:

```ts
expect(actionCopy("BUY")).toBe("진행 권고");
expect(actionCopy("NEGOTIATE")).toBe("조건 협상");
expect(actionCopy("TEST")).toBe("시험 진행");
expect(actionCopy("NEEDS_INFO")).toBe("정보 필요");
expect(actionCopy("SKIP")).toBe("진행하지 않음");
expect(offerStateCopy("confirmed")).toBe("조건 확인됨");
```

Add workspace tests that switch to `근거·이력` without reloading or losing the selected selling case. Add a recommendation test where a confirmed winner leads with complete Korean home-shopping time/channel and `PPL 없음`; add a missing/incomplete winner test that leads with `추천을 완성할 정보가 없습니다` and exposes no buy-like primary action.

- [ ] **Step 2: Run focused tests and verify RED.**

```bash
cd web
npx vitest run \
  src/features/selling-decision/selling-copy.test.ts \
  src/features/selling-decision/SellingDecisionWorkspace.test.tsx \
  src/features/selling-decision/accessibility.test.tsx
```

Expected: failure because Korean copy helpers, external surface selection, and the answer banner do not exist.

- [ ] **Step 3: Add exhaustive presentation copy.**

Create total functions for action, offer state, evidence grade, evidence disposition, history kind, PPL mode, placement mode, integration level, and common reason/missing-field codes. Each function uses a `switch` over its typed union and an `assertNever` fallback. Unknown free-form technical codes render the neutral Korean phrase `기술 정보에서 확인` in primary copy and remain visible only inside a details disclosure.

- [ ] **Step 4: Preserve complete home-shopping presentation fields.**

Extend `HsOfferView` and `workspaceModel` with the already-decoded fields needed for a real offer display:

```ts
readonly quote_expiry: string | null;
readonly settlement_days: number | null;
readonly returns_terms: string | null;
readonly cancellation_terms: string | null;
readonly make_good_terms: string | null;
readonly inventory_terms: string | null;
readonly source_ref: string | null;
```

Also map the already-loaded `programs` page into
`SellingWorkspaceModel.programOptions: readonly NamedOption[]`. Resolve the
home-shopping channel label through `channelOptions` and a PPL program label
through `programOptions`; do not add a read or infer either name. A card is
`조건 확인됨` only when the server state is `confirmed` and the displayed
booking fields are present. Otherwise render `정보 필요` and keep it out of
the complete recommendation headline.

- [ ] **Step 5: Compose the workflow and evidence destinations.**

- Keep the four-step navigation as `1 상품`, `2 홈쇼핑`, `3 PPL`, `4 추천`.
- Accept an external `surface` prop. `workflow` renders the four visited pages; `evidence` renders `EvidencePanel`, `RevisionHistory`, and continuation controls in the same loaded model.
- Remove the permanently dense evidence sidebar from workflow mode.
- Preserve visited-page mounting, selected-case identity, in-flight command guards, page cursor checks, and command error redaction exactly.

- [ ] **Step 6: Apply the shared page hierarchy.**

Use `.page-header`, `.panel`, `.form-grid`, `.option-grid`, `.table-wrap`, `.action-row`, and status badges across the product, home-shopping, PPL, recommendation, evidence, and history components. Do not change command mapper inputs or enabled/disabled rules. Put long PPL term entry under a visible `전체 조건` section rather than compressing or dropping fields. Tables become labelled stacked cards below 860 px through CSS without duplicating private DOM content.

- [ ] **Step 7: Lead recommendations with the decision.**

Before scenario input or metadata, render one banner derived only from the sealed winner and its matching loaded offer:

```text
추천: <채널> · <한국 표시 일시> 홈쇼핑
PPL 없음 / PPL <프로그램·방송 일시>
```

If the winner is null, stale, has missing fields, or cannot resolve a complete confirmed home-shopping offer, use a neutral information-needed banner and no acceptance primary action. Render base/downside profit, total committed cost, and evidence grade next. Move hashes, IDs, raw reason codes, and tie-break internals under `기술 정보`. Keep scenario recording and sealing available in their own panels before a recommendation exists.

- [ ] **Step 8: Update accessibility and E2E teaching flow.**

- Prove stable `aria-current`, visible focus, keyboard-reachable four-step and three-destination navigation, dialog focus return, text-plus-icon status, and labelled validation.
- Update `workflow.spec.ts` to navigate with the new labels, assert product -> HS -> conditional PPL -> recommendation order, confirm the answer-first no-PPL winner, open `근거·이력`, and return without another source bootstrap.
- At viewports `1440x900` and `768x900`, assert no horizontal document overflow and that the three primary destinations remain keyboard reachable.

- [ ] **Step 9: Run Task 3 gates.**

```bash
cd web
npx vitest run \
  src/features/selling-decision/selling-copy.test.ts \
  src/features/selling-decision/SellingDecisionWorkspace.test.tsx \
  src/features/selling-decision/accessibility.test.tsx \
  src/app/AppController.test.ts
npm run typecheck
npm run build:ci
EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test e2e/workflow.spec.ts
```

Expected: all selected tests pass, build exits 0, the synthetic path remains product-first, and unexpected traffic is `[]`.

- [ ] **Step 10: Commit Task 3.**

```bash
git add -- web/src/app/App.tsx web/src/features/selling-decision \
  web/src/styles/app.css web/e2e/workflow.spec.ts
git commit -m "feat(web): unify selling and evidence experience"
```

---

### Task 4: Cumulative verification, factual docs, and independent review request

**Files:**
- Modify: `web/e2e/pwa.spec.ts`
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`
- Read-only verify: all files changed by Tasks 1-3
- Publish in Pipeline: one exact cumulative verify-request after the evidence-ledger commit exists

**Interfaces:**
- Consumes: Task 1-3 commits and their common accepted base.
- Produces: one test-only PWA correction commit, one factual documentation commit, one shipping range, complete local verification evidence, and one non-author Operator verify-request. It does not launch or replace the live Mac beta.

- [ ] **Step 1: Correct the stale cumulative PWA browser contract.**

Use the fresh cumulative RED evidence from target HEAD
`6b817bdc27acdecea5dce8832cd1b4a3daceed5c`: 13 Playwright tests passed and
exactly four failed. After the first six stale bindings were corrected, the
focused PWA run advanced to 2 passed and exactly 3 failed solely on the removed
post-release `나중에` control. In `web/e2e/pwa.spec.ts` only:

- import the already-validated `LOOPBACK_ORIGIN` from `../playwright.config`;
- replace all three hardcoded `http://127.0.0.1:4173/` bindings (registration
  scope, service-worker script URL expectation, and CDP `scopeURL`) with values
  derived from `LOOPBACK_ORIGIN`;
- replace exactly the three stale `저장하고 다음` button locators with the
  approved all-fields editor label `초안 저장`;
- replace exactly the three post-release `나중에` enabled assertions with the
  current command-settlement invariant: the same `초안 저장` button is present
  and disabled after the held save completes;
- preserve every PWA installability, cache, waiting-worker, multi-client,
  offline, and activation assertion.

Then run:

```bash
cd web
lsof -nP -iTCP:4174 -sTCP:LISTEN
EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test e2e/pwa.spec.ts
cd ..
lsof -nP -iTCP:4174 -sTCP:LISTEN
git add -- web/e2e/pwa.spec.ts
git commit -m "test(web): align PWA gate with unified UI"
```

Expected: each `lsof` exits 1 with no listener; every PWA node passes; the
registered teaching preview on 4173 is untouched; the commit changes only the
one test path.

- [ ] **Step 2: Run the complete unit, type, build, browser, and privacy gates.**

```bash
cd web
npm test
npm run typecheck
npm run build:ci
EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test
npm run build
cd ..
rg -n "localStorage|sessionStorage|indexedDB|caches|console\." web/src \
  --glob '!**/*.test.*'
rg -n "owner_ruling_required|manual_only|\bBUY\b|\bTEST\b|\bSKIP\b|\bNEGOTIATE\b|NEEDS_INFO" \
  web/src/features web/src/app --glob '!**/*.test.*'
```

Expected: all commands exit 0; storage hits remain limited to reviewed auth/recovery machinery; raw-state hits are either mapper inputs or technical-detail output, never primary visible copy.

- [ ] **Step 3: Run the repository smoke proportional to UI risk.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: PASS. Do not run real database mutation, managed Supabase, real policy activation, provider launch, email, booking, or deployment.

- [ ] **Step 4: Update factual documentation from the observed output.**

Update `ARCHITECTURE.md` and `OPERATIONS.md` to describe the unified Korean shell, all-ten-fields page, three primary destinations, answer-first recommendation, and the exact Vitest/Playwright summaries emitted by Step 2. Remove stale prior counts rather than copying the pre-change `251` claim. State clearly that local verification is not physical Windows installation or managed deployment.

- [ ] **Step 5: Commit the factual closeout.**

```bash
git add -- ARCHITECTURE.md OPERATIONS.md
git commit -m "docs: record unified beta UI verification"
```

- [ ] **Step 6: Verify the actual range and write set.**

```bash
git diff --check bc2e85891f27befe19236686e608f3d45db84d14..HEAD
git diff --name-status bc2e85891f27befe19236686e608f3d45db84d14..HEAD
git status --short --branch
```

Expected: only the files named in this plan plus focused tests/docs changed; the worktree is clean; `.vscode/` and `web/node_modules` remain untouched outside the isolated worktree.

- [ ] **Step 7: Publish one cumulative non-author verify-request.**

The Director publishes through the fixed Pipeline mailbox writer and binds:

- accepted base `bc2e85891f27befe19236686e608f3d45db84d14`;
- exact shipping commit and actual range;
- assigned distinct non-author Operator seat and different model;
- immutable design and plan refs;
- exact changed paths;
- every command and terminal summary from Steps 1-3;
- findings for login two-field visibility, all-ten owner fields, sequential save/fail-closed behavior, product ordering, complete/no-PPL recommendation, raw-copy containment, privacy, responsive overflow, and recovery behavior.

No merge, push, live preview restart, service launch, deployment, booking, or real-policy activation is authorized by the verify-request.

- [ ] **Step 8: Stop for the Operator verdict.**

The assigned Operator independently reviews the actual range and publishes GO/NITS/FAIL. On FAIL, the Director corrects only the cited findings and republishes a new exact range. On GO, the Coordinator may integrate under the user's existing local-beta continuation authority; live Mac preview replacement remains a separately checked effect.
