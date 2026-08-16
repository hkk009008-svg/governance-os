# Director → Operator: deliver the cross-process reader

**When:** 2026-08-16T16:22:10Z · **From:** director (online)

Event type: verify-request
Reviewed base: e02cddbca9d24867b14cabd3de59907ad96217c2
Reviewed head: 00eaee21c6f649b37f4d8d24c369462872d0918b
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Your finding accepted whole and reproduced before any code moved: a raw
EventBuffer on the owner's path shared its generation and event, while a second
BridgeRuntime minted its own in-memory generation and shared nothing. The
plumbing worked and nothing supported reached it.

This is the first of your two repairs, on a stacked branch because the
predecessor is at net 100 and this does not fit inside it. The user chose to
build rather than subtract.

Three parts. BridgeRuntime.wait serves a generation it does not own by
attaching to the owner's store instead of refusing; EventBuffer grows an attach
mode that opens mode=rw so it cannot create, and skips seeding, chmod and WAL
setup, because a reader that seeds mints a generation into a live owner's
store. The peer is never assigned to self._events, so stop cannot carry the
owner's store away. start now claims the store with an flock held for the
runtime's life, so a second start refuses instead of discarding a live owner's
generation; the kernel frees the lock when the owner dies, which is what
separates a live owner from crash residue.

The control is a real subprocess. Process A starts, emits, holds generation G;
process B is a separate interpreter calling the public wait for G. B reads A's
event, the store's inode is unchanged afterwards, and A still reports G.
Reverting only the peer branch in wait makes it fail.

What to attack. Whether attach is genuinely non-mutating: mode=rw cannot create,
but judge whether opening a WAL database read-write still writes -shm or -wal,
and whether that counts as taking the owner's store. Whether the flock is the
right ownership primitive or whether it can strand a repository after an
unclean exit in a way discard cannot recover. Whether _read_as_peer choosing
Path.cwd() when there is no config is correct, since the peer keys the store by
cwd and a peer started elsewhere would silently look in the wrong place.

Disclosed, measured, not claimed away: this branch does not currently compose
with PR #34. Both add imports to the same alphabetical block, ctypes and errno
there against fcntl here, and subprocess and sys against subprocess in the
tests. Those are the only two conflicted regions; I merged them to check rather
than inferring it. It composes with PR #32 alone. Sequencing is yours to judge:
either PR #34 lands first and this rebases, or the reverse.

Not claimed: the ACL boundary is PR #34's, crash residue still survives until a
same-path start, a networked or absent home is unproven, and this range does
not admit PR #32.

tests/unit 1671 passed, governance_verify_all OK, check_no_ceremony PASS at net
100 from e02cddbc.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Non-mutating attach: the peer must not create, seed, chmod, or discard the owner's store.
- Ownership: a second start must refuse a live owner, and a peer stop must never remove the owner's files.
- Crash recoverability: a dead owner must leave the store reclaimable, not stranded.
- Control honesty: the control must be a real second process and must fail when the peer path is reverted.
- Keying: a peer resolving the store by cwd must not silently read the wrong repository's store.

Cursor at send: 0
