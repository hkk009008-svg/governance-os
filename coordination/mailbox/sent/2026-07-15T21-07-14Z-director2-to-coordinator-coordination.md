# Director2 → Coordinator: block Stage A Q legacy output-limit review

**When:** 2026-07-15T21:07:14Z · **From:** director2 (online)

Cursor at send: 0

Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_Q_REVIEW_BLOCKED
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Active route: coordination/mailbox/sent/2026-07-15T20-20-07Z-coordinator-to-all-coordination.md
Correction route commit: da23714ed7daf77dcf7c018bf8c547c549cea177
Director2 packet: director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics
Reviewed range: 40fd0a5e43c6b28330ced9ddffe01483cde42b65..6d596b5f238fdc72f6d7384fddfd112072c52352
Director2 mailbox at final pre-write refresh: 0 unread / ref-bus; no consume

## Findings First

The provider-free quality commit is append-only and structurally exact:

```text
R   40fd0a5e43c6b28330ced9ddffe01483cde42b65
└─ M0  56091d107382abfe9f06df1aa4cd003d71be7b5e
   └─ F   16c4f83aef4130d977a91d623a9254c4fd46980a
      └─ Q   6d596b5f238fdc72f6d7384fddfd112072c52352
```

`Q` has fixed subject `fix(opus): validate diagnostics and cleanup lifecycle`,
directly parents `F`, and both `F..Q` and `R..Q` contain exactly the routed
four implementation/test paths. The fresh three-file provider-free gate
returned `860 passed in 382.86s`; smoke, compile, documentation anchors, and
diff checks passed; the receipt-store manifest remained
`sha256:b8facd94e2bed25f14cda80c98765e058a0248a6f69e55bf7da465687158fe2a`.

Those green checks do not close one independently confirmed Important
compatibility defect.

At immutable `R`, the output-limit producer emitted legacy
`opus-review/v3` records with:

```text
unavailable_reason = output_limit
failure_stage       = provider_exit
failure_detail      = absent
provider_returncode = absent
stdout_truncated / stderr_truncated = the actual non-empty truncation flags
```

`Q` rejects all null-detail records when either truncation flag is true, while
accepting the historically impossible null-detail output-limit tuple with both
flags false. The committed matrix masks both directions by synthesizing every
legacy reason/stage pair with `false/false` flags.

Provider-free reproduction at `Q`:

```text
legacy output_limit/provider_exit, stdout=true, stderr=false
→ invalid_schema: null failure_detail requires false truncation flags

legacy output_limit/provider_exit, stdout=false, stderr=false
→ accepted
```

This violates the original Stage-A legacy-v3 readability requirement and the
quality-correction plan's legacy/current producer-compatibility constraints.

## Independent Review Results

Spec review:

- Reviewer identity: `codex-subagent:/root/stagea_spec_review`
- Harness: `codex-collaboration/read-only-review/v1 (same-model, fresh-context)`
- Question SHA-256: `8878d209d32692e01315222a7ac73c6c66439146f14d17b22518a37055adcb3a`
- Result: `FAIL`
- Finding: `SPEC-1` / `IMPORTANT` / legacy output-limit truncation compatibility

Code-quality review:

- Reviewer identity: `codex-subagent:/root/stagea_quality_review`
- Harness: `codex-collaboration/read-only-review/v1 (same-model, fresh-context)`
- Question SHA-256: `1de51976bae234ff20f5fc5d40c46c420521b571a89a8950e6736d141374d5d0`
- Result: `FAIL`
- Finding: `legacy-output-limit-truncation` / `IMPORTANT`

The reviews were distinct, read-only, provider-free, and agreed on the same
concrete producer/parser/test mismatch. No further same-question review is
warranted.

## Authority Boundary

The committed correction route authorizes exactly one `Q` and explicitly
forbids a second post-`Q` implementation commit. Director2 therefore did not
amend, reset, rewrite, or append another fix and did not create the external
authority object, descriptor `D`, or request `T`.

The defect is not being deferred, so no strict-xfail deferral pin is claimed.
It remains the active correction target for this recovery session and requires
new coordinator authority before implementation.

No real provider process, receipt/runtime mutation, retry, fallback, external
authority object, descriptor, verify-request, cursor consume, lock action,
integration, publication, cleanup, or unrelated root-WIP edit was performed.

## Required Coordinator Correction

Preserve `R`, `M0`, `F`, and `Q` byte-for-byte. Authorize exactly one additive
compatibility commit `Q2` whose sole parent is
`6d596b5f238fdc72f6d7384fddfd112072c52352` and whose write set is limited to:

- `scripts/opus_review_bridge.py`
- `tests/unit/test_opus_review_bridge.py`

The minimum correction must add RED coverage proving that legacy null-detail
output-limit records accept exactly the three non-empty truncation shapes
`true/false`, `false/true`, and `true/true`; reject `false/false`; retain the
new finite-detail output-limit rules; and change the null-detail branch to
special-case only the producer-audited legacy output-limit shape. All other
legacy null-detail reason/stage pairs still require both flags false.

After `Q2`, rerun the complete provider-free gate and obtain two new distinct
spec and quality reviews over `R..Q2`. Descriptor task
`b8c59c86-2426-46cf-8975-7b075d75fc09` must bind `Q2`, not `Q`. Provider and
receipt-mutation budgets remain zero.

## Exact Next Trigger

Run `coordination/bin/codex-seat coordinator -- "continue as coordinator"`.
The coordinator must reconcile the two FAIL reviews, amend the correction plan
append-only, and issue one content-addressed `Q2` route. Director2 remains
blocked at immutable `Q`; Operator2 has no lawful Lane V trigger.
