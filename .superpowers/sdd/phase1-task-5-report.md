# Phase 1 Task 5 Runtime Cohort Report

Status: complete and operationally verified; no activation, commit, push, or
merge was performed.

## Sealed identity

- Source HEAD: `01d77653d5b7257bcef7c2517d958824eb8ff8a9`
- Cohort: `phase1-01d7765-gpt56sol-max-20260715-v1`
- Model/config: `gpt-5.6-sol`, reasoning effort `max`
- Codex: `codex-cli/0.144.4@sha256:3302acbda5f53de1a71ebdb0c0f2aae0d47f9324aa9fb6b4e78a47014fd51c7d`
- Collector: `capability-baseline-runtime@sha256:40ce2fb5c66c0c6845ee450bf8f8ff7e57f2ae86640a21a51166d9a7790d4c75`
- Contract blob: `sha256:229444a882692570bab94a0cc8a11b02ddd597f7b963a0b6dfe2a50e0146f751`
- Reporter blob: `sha256:4e5334a8075f3cb2a147e0e1f1ffc000dc6ffa722b6c0c5a0aeab32efc470c4b`

The operational provenance in
`logs/capability-first/phase1-01d7765-gpt56sol-max-20260715-v1/baseline.json`
binds the same source, collector, Codex runtime, contract, observations, host,
and all 25 run-record digests.

## Canary and cohort outcome

The one guarded `none`/ordinal-1 canary exited `0` with status `completed`,
record digest
`sha256:059d71368e30ffb7379394b2aaafa49c18103e13244464f69415764f056ffe82`,
and `effect_attempted=false`. It produced no marker, route, or review artifact
and was not retried.

The fresh collection exited `0` with
`{"status":"complete","run_count":25}`. Independent persisted-artifact checks
confirmed:

- 25 completed run reservations and records over the exact five-profile by
  five-ordinal product, in ordinal-first order;
- 25 unique run IDs and 25 unique accepted-result digests;
- exactly ten completed nonce-bound marker effects: five `effect_only` and five
  `combined`, each with one matching reservation and `reconciled=false`;
- exactly ten coordination artifacts and ten verification artifacts, all
  profile-appropriate, with zero standby or telemetry artifacts and zero exact
  duplicate reviews;
- no symlink evidence, failed record, uncertain record, retry, replacement, or
  extra evidence file; and
- final `status=complete`, `structural_complete=true`,
  `operational_complete=true`, and an empty error list.

## Persisted measurements

The committed reporter persisted these values in `baseline.json`:

| Metric | Result |
|---|---:|
| Accepted results | 25 |
| Time to first tool, overall median | 8,261,529,459 ns |
| Route to GO, combined median | 31,696,976,833 ns |
| Protocol artifacts | 30 |
| Protocol artifacts per accepted result | 1.2 |
| Exact duplicate reviews | 0 |
| Standby artifacts | 0 |

Per-profile time-to-first-tool medians are persisted in the same artifact; all
five profiles have five measured runs. Route-to-GO is correctly not applicable
outside the five `combined` runs.

## Verification record

Fresh verification after collection produced:

- independent artifact auditor: `PASS runs=25 unique_results=25 markers=10
  effect_only=5 combined=5 routes=10 reviews=10 standby=0 symlinks=0 files=92`;
- bounded regression suite: `338 passed in 11.66s`;
- compact-state fixture: `validated 49 mappings across 7 domains`;
- target-binding registry: `OK`, kernel mirror epoch `0`, writer `v1`,
  declarative only;
- `py_compile`, project smoke, post-run committed-byte preflight, and
  `git diff --check`: exit `0`; and
- independent final artifact review: no Critical or artifact-integrity defect;
  its sole Important finding was the missing report/stale plan state corrected
  by this closure update.

Generated evidence and this report remain local and uncommitted pending a
separate scoped commit decision. The compact kernel remains non-authoritative;
this cohort does not activate it or change current v1 route/reducer semantics.
