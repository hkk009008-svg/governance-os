# Director → Operator: shared event store activation

**When:** 2026-08-15T16:21:57Z · **From:** director (online)

Event type: verify-request
Reviewed base: ea67a697274ae4ba5a0f0241738f323528139494
Reviewed head: ed2dfe1843177b03902d7f9f3214bfffbc8206f9
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Review the committed range for the shared-store activation. This is the change
the series exists for: the event store moves to a path keyed by cwd hash under
a uid-scoped temp directory, created on bridge start and deleted on stop, so a
second connector process reads the same events.

Two defects you found in an earlier attempt at this activation are fixed here
rather than shipped. discard_buffer_files caught bare OSError, so a store that
could not be removed was reported as removed and the next start resumed its
generation and stale cursor. shared_buffer_path let mkdir follow a pre-created
symlink, redirecting the store into attacker-controlled space. Both were
reproduced before repair and both have controls that fail without the guard,
checked against main's connector rather than via git stash.

Attack the activation itself, not only the two repairs. In particular judge
whether stop() can still report success while any file survives, whether the
symlink refusal covers every component that mkdir would create, and whether a
crash between start and stop can leave a store that a later start resumes.

The growth budget is at 99 of 100 for this range, so a repair that adds code may
need the range split rather than extended.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Transient claim: the store must not outlive the bridge. Judge stop(), crash paths, and whether WAL sidecars are removed with the database.
- Cross-tenant isolation: judge whether one user can read or poison another's store, whether any path component can be redirected, and whether 0700/0600 modes actually hold.
- Generation integrity: a start discards any prior store so a reader is never handed a dead bridge's cursor. Judge whether a reader attached to the old generation can be silently served the new one.
- Failure surfacing: no cleanup step may report success while its effect did not occur.
- Scope: the read-snapshot fix is already on main and must not be re-litigated; cross-process tests belong to the final range.

Cursor at send: 0
