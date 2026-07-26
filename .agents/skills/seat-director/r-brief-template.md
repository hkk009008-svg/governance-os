# R-BRIEF template — what a dispatch-ready brief contains

Read this when you are about to author an R-BRIEF (the brief that gates a fix —
read by the co-signer on a CRITICAL cross-cutting row, and by the implementer if
you dispatch). The brief is where **evidence is produced**, not where intentions
are stated: a named symbol without its grep-output is a *type-level claim*, not a
*runtime claim* (Rule #12), and a new guard without a sibling audit is a blind
spot (Rule #13). Fill every slot or say why it's N/A — an empty slot is the
defect that ships.

## Fill-in skeleton

```
# R-BRIEF: <defect-id> — <one-line what+why>

PRIORITY: CRITICAL | MAJOR | MEDIUM        LANE: A (<domain-A>) | B (<domain-B>)
CROSS-CUTTING: yes/no   (auto_approve.py · <PROJECT>/context.py · core.py · <entrypoint>.py)
  → if yes: LOCK held? <claim-lock output, exit 0=WON>   CO-SIGN: Tier-A/B? (CRITICAL x-cut ⇒ Tier-A BEFORE DISPATCH)

## The defect (file:line + observable symptom)
<where it is, what goes wrong at runtime, and the failure the user/gate sees>

## Rule #12 — grep-the-writes (the symbol is WRITTEN at runtime, not just declared)
TARGET SYMBOL: <field / dict-key / mutator / write-path the new code targets>
$ <grep that proves the production WRITE site>     # e.g. grep -rn "self.spent_usd\s*=" --include='*.py' .
→ <paste the matching file:line output>            # type-declaration is NOT write-evidence
  (mixed-shape symbol — typed attr AND raw-dict? grep BOTH surfaces.)

## Rule #13 — symmetric / sibling audit (what existing sites should mirror, or are missing)
SHARED FENCE/FLAG/STATE: <e.g. the budget gate · screening_approved · a shared lock>
$ <grep the siblings on the same fence>
→ Audited <sites>; audit-completeness is not audit-disposition; state the disposition for each sibling as mirror / defer / document / exempt.

## Full-shape pattern reference (brief-pattern = implicit spec)
MIRROR: <existing helper/endpoint at file:line> — its FULL shape:
  signature · route/pid-scope · error handling · lock guards · return contract.
  If this cites a canonical site/SHA, brief-pattern references are runtime claims when they cite canonical sites:
  verify the named symbol exists at the cited SHA and verify the cited SHA exhibits the named sub-pattern.
  (R-PID: a project-scoped endpoint takes <pid> EXPLICITLY — never scan list_projects().)
  If the named helper doesn't exist or the wording is ambiguous → say so HERE, before dispatch.

## The fix (what changes, bounded)
<the intended change + the ~LoC delta + the files touched — scope the implementer must not exceed>

## Verification the operator/CI will run
<the test/pin that must flip, the command + expected result; for a deferred defect, the strict-xfail pin>
REVERSION CONTROL: <restore the defect → which pins fail, and that they fail for the right reason>
EVASION CONTROL: <guard left intact → the closest you got to the forbidden outcome anyway, or why no route exists>
```

## "Verified" bar — the brief is not dispatch-ready until

- **Rule #12 slot has real grep OUTPUT** under the target symbol — not "I'll grep later," not the type declaration. Without it, label the symbol *type-level claim* explicitly so the implementer knows.
- **Rule #13 slot names the siblings actually checked** and states fold-or-defer for each under-defended one; audit-completeness is not audit-disposition, so state the disposition for each sibling as mirror / defer / document / exempt.
- **Cross-cutting?** Name the overlap and preserve peer work. Claim a lock only
  when the user or active route separately authorizes that exact lock action.
  High-risk control work receives the required actual-range review; there is no
  universal pre-implementation review ceremony.
- **Pattern refs are full-shape**, not just a function name. For canonical sites, verify the named symbol exists at the cited SHA and verify the cited SHA exhibits the named sub-pattern.
- **Both controls are present** when the change adds a guard. Reversion proves the pin is not vacuous; evasion proves the guard is sufficient. Only the second can expose a guard that pattern-matches text where it should observe behaviour, because reverting always hands it the shape it already recognizes.

## Dispatch decision (after the brief is verified-complete)

| Situation | Do |
|---|---|
| Small, tightly-coupled change | Implement directly and apply the risk-based verification profile. |
| Independent work where parallel evidence or capacity helps | Delegate bounded, non-overlapping ownership; never run concurrent writers on shared files. |
| Dispatching an implementer | Use the relevant parts of `docs/templates/agents/implementer.md`, bind its allowed paths, and use the selected native worktree index. |

**Name the right specialist reviewer** when the lane has one — these are real dispatch targets:
- **Money / cost-gate fix** (the cost/budget gate accumulator, per-item veto, budget pre-check) → the **`money-gate-reviewer`** agent (hunts gate-source-mismatch + silent-gate-degradation).
- **Post-commit independent verification** is your operator's job, who dispatches the **`lane-v-verifier`** agent (you do NOT verify your own pair's fix).
- **Domain-specific subsystem or pipeline-design content** → load the matching `<domain-skill>` BEFORE authoring or judging the code (R-SKILL).
<!-- TODO(<PROJECT>): add project-specific specialist reviewer targets here -->

## Worked fragment (Rule #12 slot done right)

```
## Rule #12 — grep-the-writes
# Example: the cost/budget gate reads a single accumulator field
TARGET SYMBOL: BudgetTracker.spent_usd (the gate reads only this accumulator)
$ grep -rn "self\.spent_usd\s*=\|self\.spent_usd\s*+=" --include='*.py' . | grep -v /tests/
→ budget_tracker.py:227  self.spent_usd: float = 0.0
  budget_tracker.py:306  self.spent_usd += cost_usd     # the ONE write chokepoint (log() delegates here)
  ⇒ runtime-written confirmed; the gate's single source of truth is this line, not the type hint.
# Replace with the actual symbol + grep for your project's cost/budget gate or other write target.
```
