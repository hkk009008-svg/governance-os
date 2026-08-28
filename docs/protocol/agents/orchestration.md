# Desktop-team orchestration

Pipeline has no standing coordinator. The user objective is controlling; the
three app members co-direct through explicit proposals, evidence, and scoped
ownership. For a concrete implementation, one member owns integration while
the other members contribute bounded work.

## Split work only when useful

Parallel work is appropriate when tasks are independently answerable or touch
nonoverlapping files. Good examples are repository mapping, independent premise
attacks, distinct platform checks, and separate implementation modules with a
clear integration owner.

Serialize work when members would edit the same file, mutate the same resource,
depend on one unresolved design choice, or compete for an exclusive external
lane. One member completes or hands off the shared write before another begins.

## Assignments

A bounded request states:

- objective and expected output;
- owned paths or read-only scope;
- relevant repository/task context;
- verification expected;
- whether the requester can continue without the answer.

Assignments are task coordination, not authority grants. A member must not
expand into push, merge, release, spend, live mutation, or destruction without
exact current user/task authority.

## Communication loop

1. Call `team_status` for current activity and pending state.
2. Send the smallest useful request with `team_send`.
3. Continue independent work when possible.
4. At a natural dependency boundary, call `team_wait` using the last handled
   cursor.
5. Inspect the content of any reply; queue, acknowledgement, and reply metadata are not
   a substantive answer.
6. Integrate through the named owner and run the combined tests once.

Use broadcast only for information all members need. Prefer one clear owner to
several overlapping directives. Do not create task boards, role rotations,
packets, or handoff chains for work that fits in the app task and Git diff.

## Capability pairing

Codex commonly anchors sustained workspace integration, Claude large-context
reasoning or independent review, and AGY fast mapping, browser/artifact work,
or adversarial challenge. These are defaults, not constraints: every member
may direct and implement.

At a formal review boundary, orchestration yields to the temporary
author/reviewer contract. AGY remains fully heard as an engineering member but
cannot be the sole independent formal verdict. When the review ends, so do the
temporary responsibilities.
