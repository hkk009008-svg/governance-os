# Independence-first verification (R-INDEPENDENCE)

**Standing default of the governance OS** (ADR-019). This document is the full
text; the operative stub lives in `CLAUDE.md` / `AGENTS.md` as **R-INDEPENDENCE**.

## The rule

**Scope: both** (every seat, Claude or Codex).

**Trigger:** designing OR implementing an **adversarial-surface** change — any
change that:
- parses, renders, or composes input into a parseable/executable context
  (a renderer, a header/config parser, a template, a serializer);
- enforces authority or a security boundary (command-class checks, path
  confinement, identity/route binding, supersession/revocation);
- gates a side effect (a consumable token/capability, a push/merge gate);
- validates a schema whose acceptance grants trust.

**Action — obtain independent verification at TWO points, not just at the end:**

1. **Design-time (before implementing).** An **independent** reviewer —
   preferably a *different model/harness* than the author (a Codex seat when
   the author is a Claude seat, or vice versa) — enumerates the abuse/edge
   cases and coverage targets the change must handle. The author folds these
   into the plan's acceptance criteria as **enforced-and-tested behaviors**
   ("consume rejects a command outside the class with reason X, proven by test
   Y"), never as aspirational guarantees ("a capability cannot act on another
   class"). The enumeration is a committed artifact.

2. **Per-task (before "done").** An **independent** reviewer verifies the actual
   diff against those enumerated cases. For an adversarial surface this SHOULD
   be **cross-model** — a same-model reviewer does not discharge it, because
   correlated blind spots make same-model review near-vacuous on exactly these
   surfaces (see "Why", below). This is stronger than the standing
   operator-GO (ADR-001): it fires *per task*, and it prefers a *different
   perspective*, not merely a different seat running the same model.

## What "independent" means here

- Strongest: a **different model/harness** (cross-model). In this repo that is
  typically a Codex `Lane-V` pass (`codex exec --sandbox read-only`) reviewing
  a Claude seat's diff, or a Claude seat reviewing a Codex seat's diff.
- Weaker: a different seat or cold-context reviewer of the same model with a genuinely adversarial prompt. For adversarial design-time enumeration this must be identified as weaker evidence; it does not replace the preferred cross-model per-task verification.
- **Not** independent: the author reviewing its own plan or implementation, even under a renamed role.

## Why (the empirical origin)

Origin: the **2026-07-12 governance-improvement retrospective**. Across six
kernel-hardening slices, a same-model author → implementer → reviewer pipeline
(all one model, in different hats) produced work that passed every internal
review — yet an independent cross-model verifier then found, on the adversarial
surfaces:

- control-character **injection** into a rendered document (twice, in two
  different renderers);
- a **compound-command bypass** (`git push && git tag`) past a prefix check;
- authority that was **computable but not enforced** at the point of use
  (a command-class field and a currency helper that nothing called);
- a **path-confinement escape** in a comparator;
- an identity/binding gap (route id not bound to its filename);
- a durability defect that **bricked** a one-time token on crash;
- **test vacuousness** — the property tests meant to catch defects did not
  reach the code they claimed to cover;
- a **total-function gap** in already-shipped code (a validator that leaked a
  raw exception on a hostile-but-typed path).

Every one had been approved by the same-model internal review. Independence
only at the *end* let a whole change's blind spots accumulate before any
different perspective saw them. Two structural lessons:

1. **You cannot review — or fuzz — your own blind spots.** The model that
   writes the validator writes the review and the test strategy with the same
   gaps, so all three miss the same cases. Only a *different* perspective
   reveals them.
2. **Fix the class, not the instance.** The injection class recurred in a new
   form (shell operators) after the newline form was fixed, because the fix
   targeted the instance. Design-time enumeration by an independent reviewer is
   how the *class* gets named before implementation.

## Relationship to existing protocol

- **Extends** ADR-001 (operator independently verifies every commit) and
  Rule #23 (cross-lane co-sign for CRITICAL cross-cutting change): this rule
  moves a slice of that independence to *design time* and prefers *cross-model*
  for adversarial surfaces.
- **Complements** R-VERIFY-TIER: that rule *caps* redundant same-question
  passes; this rule *requires* an early, genuinely-different-perspective pass
  for adversarial surfaces. They are not in tension — R-VERIFY-TIER bounds
  repetition of the *same* question; R-INDEPENDENCE demands a *new* question
  from a *new* perspective.
- Non-adversarial, read-only, or hermetic changes do **not** trigger this rule;
  the smallest sufficient profile still applies (do not spread adversarial-tier
  cost onto low-risk work).

## Evidence

- the committed design-time enumeration artifact (the independent reviewer's
  abuse/coverage list);
- the per-task independent verification report, citing the reviewer's identity
  and — for an adversarial surface — that it was cross-model.

## Mechanized enforcement and remaining follow-up

- Mechanized: `scripts/check_go_schema.py` and
  `scripts/verification_report_gate.py` require `lane-v-report/v3`,
  `independent-lane-v`, and `lane-v:independent-verifier`, with one committed
  descriptor and lawful trigger bound exactly to the reviewed range. The
  non-author operator remains the verifier and sole GO/NITS/FAIL authority.
  `TaskPublicationStore` atomically publishes the task-bound report through
  `coordination/bin/send-event`; direct mailbox writes and hooks grant no
  publication authority. Model or provider identity grants no authority.
  Exact historical reports remain readable only through the committed
  path/raw-byte digest manifest.
- Add the design-time enumeration step to the implementer/reviewer
  dispatch templates in `docs/templates/claude/`.
