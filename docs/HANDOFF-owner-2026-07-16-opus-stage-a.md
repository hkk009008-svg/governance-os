# Owner Handoff - Opus Stage A Diagnostic Range

Created: 2026-07-15T20:17:02Z
Owner: `director2`
Recovery unit: `OPUS-STAGE-A`
Source branch: `codex/director2-opus-transport-stage-a`
Source worktree: `.worktrees/opus-transport-first-stage-a-director2`

## Frozen Boundary

This handoff freezes the clean, provider-free Stage A diagnostic range without
advancing the source branch:

```text
R   40fd0a5e43c6b28330ced9ddffe01483cde42b65
└─ M0  56091d107382abfe9f06df1aa4cd003d71be7b5e
   └─ F   16c4f83aef4130d977a91d623a9254c4fd46980a
```

- `M0`: `fix(opus): expose sanitized transport failure detail`
- `F`: `fix(opus): preserve resolver ENOENT compatibility`
- `parent(M0) == R`
- `parent(F) == M0`
- Source status at freeze: clean branch
  `codex/director2-opus-transport-stage-a` at exact `F`.
- Primary `main` at the final pre-write orientation was
  `50cec4fba74fac3a7230ca3769d842e43d99045b`.

The active owner route remains
`coordination/mailbox/sent/2026-07-15T15-33-10Z-coordinator-to-all-coordination.md`.
The unresolved quality blocker is
`coordination/mailbox/sent/2026-07-15T16-49-37Z-director2-to-coordinator-coordination.md`.

## Exact Aggregate Scope And Blob Manifest

`git diff --name-only R..F` returned exactly these four paths. The blob IDs are
the full Git object IDs at `R` and `F`, respectively:

| Path | Blob at `R` | Blob at `F` |
|---|---|---|
| `scripts/opus_review_bridge.py` | `3eb3d9adf5d6573dad096cb45216ab77604e3080` | `defd7871db0c71e8b9323bdace08484cb7202273` |
| `scripts/opus_review_receipts.py` | `41f1f6e1b938c6c737cdc80cefb0b23abef72f9d` | `b55d8d549a6daeb0f7d5bbac72e4fb47879ce46d` |
| `tests/unit/test_opus_review_bridge.py` | `ed119b8e219b6b10fe19663814ec17ea349e69ae` | `5ebeeced2494647ea4e017bc55bf4788dbdb1966` |
| `tests/unit/test_opus_review_receipts.py` | `b74d44684124616ad6246fd9502d763c2ac12edd` | `9645de45fb43e70dec17a62a4a58d6baaf08f531` |

No descriptor, verify-request, integration commit, or provider-side artifact is
part of this frozen range.

## Existing Review Findings

The fresh independent spec review of `R..F` returned `pass` with zero
findings. The separate code-quality review returned `issues`: zero critical,
two important, and one minor.

1. Current-v3 diagnostics validate finite values but do not reject impossible
   semantic combinations among `unavailable_reason`, `failure_stage`,
   `failure_detail`, truncation flags, and `provider_returncode`.
2. A broker cleanup `OSError` can be labeled as broker startup failure and can
   discard a completed fake-runner result.
3. Minor: helper placement is coupled to a documentation line anchor.

The two Important findings are open. They block descriptor and Lane V
authority at `F`; this handoff does not downgrade or close them.

## Existing Provider-Free Evidence

The blocking Director2 event records the evidence already executed at `F`:

- resolver RED: `1 failed, 327 deselected` for the expected public-reason
  mismatch;
- resolver GREEN matrix: `3 passed, 325 deselected`;
- full bridge/receipt implementer suite: `513 passed`;
- provider-free quality reproductions: `2 passed in 0.30s`;
- independent spec review: `pass`, zero findings;
- independent quality review: `issues`, two Important and one minor;
- `git diff --check R..F`: no output;
- `scripts/ci_smoke.py`: `OK` after `F`.

Those results are inherited evidence from the committed blocker, not newly
rerun by this ownership-only freeze.

## Attempt And Authority Boundary

- Real Claude/Opus provider process attempts: **0**.
- Provider attempts authorized by the active Stage A packet: **0**.
- This handoff invoked no provider and performed no receipt/runtime mutation.
- Terminal receipt identity remains an inherited observation only; this
  handoff makes no new receipt claim.
- Descriptor status: absent and unauthorized at `F`.
- Operator2 verdict: absent; no lawful Lane V trigger exists.
- Integration status: not integrated.
- Publication status: not pushed.
- Locks/cursors: none claimed or consumed by this handoff.

This artifact is ownership and predecessor evidence only. It is not a GO,
descriptor, route, correctness claim, integration authority, publication
authority, or permission to rewrite `M0` or `F`.

## Exact Next Trigger

Execute
`docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md`
under a newly committed coordinator correction route that content-addresses
this handoff and authorizes exactly one append-only `Q` whose sole parent is
the frozen `F`. Provider attempts remain zero through Stage A.
