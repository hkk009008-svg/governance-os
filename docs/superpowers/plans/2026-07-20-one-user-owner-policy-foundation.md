# One-User Owner Policy Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backward-compatible single-owner policy quorum and correct the campaign-level action/eligibility defects without entering private values or activating a real policy.

**Architecture:** Preserve every existing `ppl-offer-api-v1` two-owner operation and historical record by labeling its activation/ruling quorum `two_owner_v1`. Add private quorum helpers that also recognize `single_owner_v1`; later owner-center commands will be the only public path that can create that revision. Correct both PPL and product-first evaluators so server-owned composite facts select actions while mixed denominators affect only target-level break-even.

**Tech Stack:** PostgreSQL 15 migrations and PL/pgSQL, psycopg/pytest database tests, Markdown domain/operations documentation.

## Global Constraints

- Design authority is `docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e0f4e43ce653dee37efed3cd73d90b7c5cc92779`.
- Target base is exactly `41d9f1d846d6e0928b520573094ae59846114df5` in `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`.
- Use synthetic values only. Do not read or persist real owner amounts, rates, workbooks, credentials, or managed-project data.
- Do not alter the literal ordinary PPL or selling-package read/command inventories.
- Existing two-owner rows remain valid under `two_owner_v1`; no row is updated, deleted, or reinterpreted as single-owner history.
- `single_owner_v1` requires exactly one current active owner in the deployment and one matching approval from that owner.
- This plan creates no real formula/risk body, owner approval, Gate-D record, or activation.
- Preserve server authority, append-only tables, RLS/grants, immutable receipts, and actor-scoped replay.
- No package install, network access, service lifecycle change, managed database mutation, deployment, booking, merge, publication, or external effect.
- Each task ends in a separate local commit and an actual-range non-author Operator verdict before the next task.

---

## File map

- Modify: `supabase/migrations/20260717000500_decision_policy.sql` — versioned quorum metadata and shared quorum predicates.
- Modify: `supabase/migrations/20260717000600_offer_evaluation.sql` — capability/quorum consumers and PPL evaluator facts.
- Modify: `supabase/migrations/20260718000200_selling_package_evaluation.sql` — product-first evaluator eligibility parity.
- Modify: `db/tests/test_ppl_decision_policy.py` — single-owner/legacy quorum and Gate-D negatives.
- Modify: `db/tests/test_ppl_offer_evaluation.py` — allocation, break-even, and composite action regressions.
- Modify: `db/tests/test_selling_package_evaluation.py` — product-first experimental eligibility regressions.
- Modify: `ARCHITECTURE.md`, `DECISIONS.md`, `OPERATIONS.md` — factual local implementation state and the new compatibility boundary.

### Task 1: Version the policy quorum without changing the frozen v1 operations

**Files:**
- Modify: `supabase/migrations/20260717000500_decision_policy.sql`
- Modify: `supabase/migrations/20260717000600_offer_evaluation.sql`
- Test: `db/tests/test_ppl_decision_policy.py`

**Interfaces:**
- Consumes: existing formula/risk approvals, activation events, format rulings, membership rows, and operations-only v1 commands.
- Produces: `decision._ppl_required_owner_count(text)`, `decision._ppl_activation_is_approved(bigint)`, and `decision._ppl_effective_format_status()` for every downstream policy consumer.

- [ ] **Step 1: Write the failing quorum tests.**

Add focused tests with these exact behavioral names and assertions:

```python
def test_single_owner_quorum_accepts_one_current_owner_and_one_matching_approval(db):
    # Seed exactly one active owner, one formula approval, one risk approval,
    # and an activation row labeled single_owner_v1.
    active = db.execute("select * from decision._active_ppl_policy()").fetchall()
    assert len(active) == 1


def test_single_owner_quorum_rejects_zero_or_multiple_current_owners(db):
    # Run once after revoking the only owner and once after adding OWNER2.
    assert db.execute("select count(*) from decision._active_ppl_policy()").fetchone()[0] == 0


def test_two_owner_v1_history_still_requires_two_distinct_current_approvals(db):
    # One approval is insufficient for a legacy activation; two remain valid.
    assert _active_policy_count(db, approval_count=1, quorum="two_owner_v1") == 0
    assert _active_policy_count(db, approval_count=2, quorum="two_owner_v1") == 1


def test_single_owner_manual_only_requires_one_current_owner_and_matching_digest(db):
    assert _effective_format_status(db, quorum="single_owner_v1") == "manual_only"
    _add_active_owner(db, OWNER2)
    assert _effective_format_status(db, quorum="single_owner_v1") is None
```

Also retain the existing tests proving the v1 `activate_ppl_policy_pair` and
`record_ppl_initial_format_ruling` commands still report one approval as
insufficient.

- [ ] **Step 2: Run the focused tests and confirm the intended RED.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_ppl_decision_policy.py \
  -k 'single_owner_quorum or two_owner_v1_history or single_owner_manual_only' -q
```

Expected: failures because quorum columns/helpers do not exist; no fixture or
connection error is an acceptable RED.

- [ ] **Step 3: Add immutable quorum metadata.**

Extend the two table definitions with exact closed values and legacy defaults:

```sql
approval_quorum text not null default 'two_owner_v1',
constraint policy_activation_quorum_check
  check (approval_quorum in ('two_owner_v1','single_owner_v1'))
```

Use the corresponding constraint name
`initial_format_quorum_check` on `decision.initial_format_rulings`. Add the new
column to inserts and snapshots explicitly; do not depend on the default in
new code. Existing v1 wrappers always insert `two_owner_v1`.

- [ ] **Step 4: Centralize quorum evaluation.**

Add these private helpers and revoke all public/authenticated execution:

```sql
create function decision._ppl_required_owner_count(p_quorum text)
returns integer language sql immutable strict
set search_path=pg_catalog,pg_temp as $$
  select case p_quorum
    when 'two_owner_v1' then 2
    when 'single_owner_v1' then 1
    else 0 end
$$;

create function decision._ppl_activation_is_approved(p_activation_id bigint)
returns boolean language sql stable security definer
set search_path=decision,app,pg_catalog,pg_temp as $$
  select coalesce((
    select decision._ppl_required_owner_count(a.approval_quorum) > 0
      and (a.approval_quorum='two_owner_v1' or
           (select count(*) from app.members m
             where m.active and m.role='owner')=1)
      and (select count(distinct x.approved_by)
             from decision.formula_approvals x
             join app.members m on m.user_id=x.approved_by
              and m.active and m.role='owner'
            where x.formula_version_id=a.formula_version_id
              and x.rule_set_sha256=a.formula_rule_set_sha256) =
          decision._ppl_required_owner_count(a.approval_quorum)
      and (select count(distinct x.approved_by)
             from decision.risk_policy_approvals x
             join app.members m on m.user_id=x.approved_by
              and m.active and m.role='owner'
            where x.risk_policy_id=a.risk_policy_id
              and x.policy_sha256=a.risk_policy_sha256) =
          decision._ppl_required_owner_count(a.approval_quorum)
    from decision.policy_pair_activation_events a
    where a.id=p_activation_id
  ),false)
$$;
```

Add `decision._ppl_effective_format_status()` with the same exact-owner-count
rule, grouping by `format_status`, `ruling_sha256`, `ruling_ref`, and
`approval_quorum`, and returning only the newest qualifying status.

- [ ] **Step 5: Replace every hard-coded quorum consumer.**

Use `rg` to enumerate all `=2`, `<>2`, and Korean two-owner messages in the
three decision/evaluation migrations. Replace only approval-quorum checks:

```text
decision._active_ppl_policy()
decision._record_ppl_manual_scenarios(jsonb,bigint,uuid)
decision.approved_policy_activation_as_of(timestamptz)
decision._seal_ppl_offer_evaluation_at(bigint,bigint,timestamptz,uuid)
biz.get_ppl_decision_capabilities()
```

`decision._active_ppl_policy()` and
`decision.approved_policy_activation_as_of(timestamptz)` filter through
`decision._ppl_activation_is_approved(a.id)`. Manual-scenario and seal
revalidation call the same helper after locking the activation and approvals.
Capabilities call `decision._ppl_effective_format_status()`.

The existing v1 activation function keeps its explicit two-owner requirement
and inserts `approval_quorum='two_owner_v1'`; it is the compatibility path, not
the new one-user path.

- [ ] **Step 6: Run quorum and security tests.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_ppl_decision_policy.py \
  db/tests/test_ppl_offer_security.py \
  db/tests/test_ppl_offer_cutoff.py -q
```

Expected: PASS, including legacy two-owner, single-owner, revocation, race,
RLS/grant, and as-of activation tests.

- [ ] **Step 7: Commit and request independent review.**

```bash
env -u GIT_INDEX_FILE git add -- \
  supabase/migrations/20260717000500_decision_policy.sql \
  supabase/migrations/20260717000600_offer_evaluation.sql \
  db/tests/test_ppl_decision_policy.py
env -u GIT_INDEX_FILE git commit -m "feat(policy): add versioned single-owner quorum"
```

Submit the exact parent..HEAD range to a non-author Operator. Stop on NITS/FAIL
before Task 2.

### Task 2: Correct campaign allocation and server-owned action eligibility

**Files:**
- Modify: `supabase/migrations/20260717000500_decision_policy.sql`
- Modify: `supabase/migrations/20260717000600_offer_evaluation.sql`
- Test: `db/tests/test_ppl_offer_evaluation.py`

**Interfaces:**
- Consumes: formula `package_allocation_mode`, scenarios, policy limits, choice-set `experimental_allowed`, and existing reason codes.
- Produces: private evaluator facts `needs_info_required`, `hard_skip_required`, `buy_eligible`, `test_eligible`, `negotiate_eligible`, and `always`; mixed denominators become break-even-only evidence.

- [ ] **Step 1: Add failing regressions for the two confirmed defects.**

Add tests with exact outcomes:

```python
def test_mixed_linear_rates_keep_campaign_action_and_only_hide_target_break_even(db):
    item = _seal_mixed_linear_rate_case(db)
    assert item["manual_policy_action"] in {"BUY", "TEST", "NEGOTIATE"}
    assert item["required_contribution_to_break_even"] is not None
    assert item["break_even_incremental_settled_sales"] is None
    assert item["break_even_incremental_settled_units"] is None
    assert "mixed_denominators" in item["reason_codes"]
    assert item["missing_fields"] == []


def test_unapproved_package_allocation_mode_fails_closed(db):
    item = _seal_with_formula_patch(
        db, {"package_allocation_mode": "synthetic_unapproved_mode"})
    assert item["manual_policy_action"] == "NEEDS_INFO"
    assert "missing_critical_term" in item["reason_codes"]
    assert any(field["path"] == "/formula/package_allocation_mode"
               for field in item["missing_fields"])


def test_experimental_choice_false_never_selects_test(db):
    item = _seal_with_experimental_allowed(db, False)
    assert item["manual_policy_action"] != "TEST"


def test_experimental_choice_true_selects_test_before_negotiate_when_both_eligible(db):
    item = _seal_with_experimental_allowed(db, True)
    assert item["manual_policy_action"] == "TEST"
```

- [ ] **Step 2: Run the regressions and confirm behavioral RED.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_ppl_offer_evaluation.py \
  -k 'mixed_linear_rates_keep or unapproved_package_allocation or experimental_choice' -q
```

Expected: mixed rates return `NEEDS_INFO`, the allocation mode is ignored, or
`experimental_allowed=false` can reach a TEST rule.

- [ ] **Step 3: Add the private composite fact vocabulary without widening v1.**

The evaluator facts object gains exactly these private booleans:

```text
needs_info_required
hard_skip_required
buy_eligible
test_eligible
negotiate_eligible
experimental_allowed
always
```

Do not add them to the frozen v1 `_validate_risk_body` allowlist. Task-2 tests
insert the approved synthetic risk rows directly through a test helper; the
owner-settings materializer in the dependent plan creates the production rows
from fixed server code rather than accepting arbitrary client condition codes.

- [ ] **Step 4: Consume the approved allocation mode and make denominator evidence non-blocking.**

In `_ppl_calculate_offer`:

```sql
unsupported_allocation_mode :=
  f.package_allocation_mode <> 'campaign_level_action_no_target_break_even';
```

When true, append existing reason `missing_critical_term`, add a
`missing_denominator` item at `/formula/package_allocation_mode`, and make
`needs_info_required=true`. Do not add a new wire reason code. When
`denominator_count>1`, retain reason
`mixed_denominators` but do not append a missing field and do not remove
`calculation_available`. Sales/units break-even stay null; required campaign
contribution remains `all_in`.

- [ ] **Step 5: Compute the composite facts before policy selection.**

Use these exact definitions after all primitive flags exist:

```sql
needs_info_required := not calculation_available
  or hard_unknown or unsupported_allocation_mode
  or 'invalid_vat'=any(reason_codes)
  or 'invalid_scenario'=any(reason_codes)
  or 'missing_critical_term'=any(reason_codes)
  or 'unsupported_objective'=any(reason_codes);

hard_skip_required := hard_failed
  or 'offer_expired'=any(reason_codes)
  or 'offer_withdrawn'=any(reason_codes)
  or choice_exceeded or month_exceeded or downside_exceeded;

buy_eligible := not needs_info_required and not hard_skip_required
  and p.manual_buy_allowed
  and not coalesce(o.quoted_base_amount>threshold_quote_ceiling,true);

test_eligible := not needs_info_required and not hard_skip_required
  and p.pilot_booking_allowed and c.experimental_allowed
  and p.experimental_budget_amount is not null
  and not experimental_exceeded;

negotiate_eligible := not needs_info_required and not hard_skip_required
  and threshold_quote_ceiling is not null
  and threshold_quote_ceiling>0
  and not buy_eligible;
```

Add these values, `experimental_allowed`, and `always=true` to `facts`. Change
the post-selection guards to require the matching eligibility boolean for
BUY/TEST/NEGOTIATE.

- [ ] **Step 6: Pin the approved six-row action table in a test-only policy helper.**

```json
[
  {"precedence":1,"condition_code":"needs_info_required","comparison":"is_true","threshold_source":null,"action":"NEEDS_INFO"},
  {"precedence":2,"condition_code":"hard_skip_required","comparison":"is_true","threshold_source":null,"action":"SKIP"},
  {"precedence":3,"condition_code":"buy_eligible","comparison":"is_true","threshold_source":null,"action":"BUY"},
  {"precedence":4,"condition_code":"test_eligible","comparison":"is_true","threshold_source":null,"action":"TEST"},
  {"precedence":5,"condition_code":"negotiate_eligible","comparison":"is_true","threshold_source":null,"action":"NEGOTIATE"},
  {"precedence":6,"condition_code":"always","comparison":"is_true","threshold_source":null,"action":"SKIP"}
]
```

The Python helper inserts this exact table into the private decision tables and
derives its digest independently. Do not send these new private condition codes
through the frozen v1 risk-policy command. Keep existing v1 fixtures and
targeted adversarial tables unchanged unless the test explicitly selects this
one-user policy revision.

- [ ] **Step 7: Run the complete PPL policy/evaluation profile.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_ppl_decision_policy.py \
  db/tests/test_ppl_offer_evaluation.py \
  db/tests/test_ppl_offer_cutoff.py \
  db/tests/test_ppl_offer_security.py -q
```

Expected: PASS with new mixed-rate and experimental negatives exercised.

- [ ] **Step 8: Commit and request independent review.**

```bash
env -u GIT_INDEX_FILE git add -- \
  supabase/migrations/20260717000500_decision_policy.sql \
  supabase/migrations/20260717000600_offer_evaluation.sql \
  db/tests/test_ppl_offer_evaluation.py
env -u GIT_INDEX_FILE git commit -m "fix(decision): preserve campaign action for mixed rates"
```

Submit only Task 2's parent..HEAD range. Stop before Task 3 without GO.

### Task 3: Apply eligibility parity to the product-first package evaluator

**Files:**
- Modify: `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- Test: `db/tests/test_selling_package_evaluation.py`

**Interfaces:**
- Consumes: the Task-2 composite fact vocabulary and current package candidate choice-set revision.
- Produces: identical server-owned BUY/TEST/NEGOTIATE eligibility semantics for the actual product-first recommendation path.

- [ ] **Step 1: Add failing product-first tests.**

Create paired synthetic cases where every fact is identical except
`experimental_allowed`:

```python
def test_package_test_requires_explicit_experimental_choice(db):
    disabled = _seal_package(db, experimental_allowed=False)
    enabled = _seal_package(db, experimental_allowed=True)
    assert disabled["manual_policy_action"] != "TEST"
    assert enabled["manual_policy_action"] == "TEST"


def test_no_ppl_candidate_is_never_test_eligible(db):
    no_ppl = _sealed_no_ppl_candidate(db)
    assert no_ppl["manual_policy_action"] != "TEST"
```

- [ ] **Step 2: Run and confirm the TEST-eligibility RED.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_selling_package_evaluation.py \
  -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q
```

- [ ] **Step 3: Add product-first composite facts and guards.**

Set `experimental_allowed` to the linked PPL choice-set value for `ppl`
candidates and false for `no_ppl`. Build the same six composite booleans as
Task 2 from the package candidate's primitive flags. Supply them to
`decision._ppl_select_action` and require `buy_eligible`, `test_eligible`, or
`negotiate_eligible` in the respective hard guard.

Do not calculate action in the web client and do not alter ranking/tie-break
fields except through the corrected server action.

- [ ] **Step 4: Run product-first and cumulative tests.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_selling_package_domain.py \
  db/tests/test_selling_package_evaluation.py \
  db/tests/test_selling_package_api.py \
  db/tests/test_selling_package_security.py \
  db/tests/test_ppl_offer_evaluation.py -q
```

Expected: PASS; excluded missing scenarios, no-PPL generation, rank/winner,
evidence, and stable-read behavior remain unchanged.

- [ ] **Step 5: Commit and request independent review.**

```bash
env -u GIT_INDEX_FILE git add -- \
  supabase/migrations/20260718000200_selling_package_evaluation.sql \
  db/tests/test_selling_package_evaluation.py
env -u GIT_INDEX_FILE git commit -m "fix(package): bind server action eligibility"
```

### Task 4: Reconcile factual documentation and run the foundation gate

**Files:**
- Modify: `ARCHITECTURE.md`
- Modify: `DECISIONS.md`
- Modify: `OPERATIONS.md`

**Interfaces:**
- Consumes: the three independently accepted task commits.
- Produces: factual single-owner compatibility and evaluator documentation; no runtime policy or private values.

- [ ] **Step 1: Update factual docs from command-backed source inventory.**

Append one ADR recording `single_owner_v1` as an additive quorum revision,
legacy `two_owner_v1` preservation, the fixed six-row action precedence, and
the no-activation boundary. Update topology/operations only where the actual
commits changed functions, tests, or commands. Keep real values absent.

- [ ] **Step 2: Run source-boundary and full local verification.**

```bash
env -u GIT_INDEX_FILE rg -n "<>2|\)=2|두 명" \
  supabase/migrations/20260717000500_decision_policy.sql \
  supabase/migrations/20260717000600_offer_evaluation.sql
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_ppl_decision_policy.py \
  db/tests/test_ppl_offer_evaluation.py \
  db/tests/test_ppl_offer_cutoff.py \
  db/tests/test_ppl_offer_security.py \
  db/tests/test_selling_package_domain.py \
  db/tests/test_selling_package_evaluation.py \
  db/tests/test_selling_package_api.py \
  db/tests/test_selling_package_security.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check 41d9f1d846d6e0928b520573094ae59846114df5..HEAD
```

Expected: only the intentionally preserved v1 wrapper contains a two-owner
check; all tests and smoke pass; diff-check emits no output.

- [ ] **Step 3: Commit documentation and request cumulative review.**

```bash
env -u GIT_INDEX_FILE git add -- ARCHITECTURE.md DECISIONS.md OPERATIONS.md
env -u GIT_INDEX_FILE git commit -m "docs(policy): record one-user policy foundation"
```

Director submits the exact `41d9f1d..HEAD` range to a non-author Operator on a
different model. GO accepts local implementation only. It does not authorize
owner-center API work, private input, Gate-D recording, activation, integration,
or any external effect.
