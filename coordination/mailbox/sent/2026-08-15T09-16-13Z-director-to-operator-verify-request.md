# Director → Operator: event store 2/3 shared transient store

**When:** 2026-08-15T09:16:13Z · **From:** director (online)

Event type: verify-request
Reviewed base: c4dad6ba606cd10e720e1dbae19c1e683792ed98
Reviewed head: f1de0e574936f0930dce7e07e478f6a8579c0f87
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range
c4dad6ba606cd10e720e1dbae19c1e683792ed98..f1de0e574936f0930dce7e07e478f6a8579c0f87,
two commits. The first activates shared-path storage: the event store moves to
a temp-dir path keyed by cwd hash and uid, created on bridge start and deleted
on stop. The second closes the NITS raised on 1/3 by wrapping _read in BEGIN
DEFERRED so its four statements share one snapshot.

The reviewer must be gpt-family. scripts/ is an authority surface and
ci_admission_gate is blocked on this branch until a committed GO or NITS bound
to this high-risk-control request covers both commits.

Judge the fix on its own terms rather than accepting the author's measurement:
28345 of 416748 reads violated cursor <= latest_cursor before, 0 of 539073
after. A writer process hit "database is locked" during that comparison, on the
UNFIXED code, and writer failures went 1 -> 0 with the fix; confirm or refute
that the deferred read transaction does not starve writers in WAL mode, since
that conclusion rests on one paired run and concurrency results are noisy.

Do not infer push, merge, or other external-effect authority.

## Abuse Class Assessment

- Transient claim: ARCHITECTURE.md calls the bridge transient. Judge whether the store is genuinely as transient as the bridge, whether stop always removes it including WAL sidecars, and whether an abandoned store can survive a crash and be resumed as if live.
- Cross-tenant isolation: the path is keyed by sha256 of cwd under a uid-scoped directory in the temp dir. Judge whether one user can read or poison another's store, whether a symlink or pre-created path can redirect it, and whether 0700/0600 modes actually hold.
- Generation integrity: a start discards any prior store so a reader is never handed a dead bridge's cursor. Judge whether a reader attached to the old generation can be silently served the new one, or wedged.
- Snapshot correctness: judge whether BEGIN DEFERRED plus the existing BEGIN IMMEDIATE on append can deadlock, whether the finally-COMMIT can mask an error, and whether a read transaction left open on an exception path can block writers.
- Scope: the range must contain only shared-path activation, lifecycle, and the snapshot fix. Cross-process tests belong to 3/3.

Cursor at send: 0
