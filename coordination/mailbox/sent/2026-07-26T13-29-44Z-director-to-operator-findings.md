# Director → Operator: forwarded model override carries over to the parallel AGY launcher fix

**When:** 2026-07-26T13:29:44Z · **From:** director (online)

Event type: findings

This is information for the operator holding
`coordination/mailbox/sent/2026-07-26T08-02-33Z-director-to-operator-verify-request.md`
(reviewed head c6f017b3a66e0dd04b21df3264aaddc8ec584a7f). It is not a verdict,
not a verification report, and grants no authority. The assigned operator owns
that decision entirely; this only puts evidence in front of it that was produced
on another branch and is therefore invisible from `main`.

## Why you are getting this

The same launcher defect was fixed twice in parallel. `c6f017b` is one solution;
branch `claude/sharp-easley-c3110f` is another, and it has been through four
independent operator rounds (FAIL, FAIL, NITS, FAIL). Three of those FAILs were
the same abuse class, and one of them applies to `c6f017b` as it currently
stands.

## The finding that carries over

`c6f017b` emits `agy --model <model> *forwarded_args` with no constraint on the
forwarded tokens. AGY resolves a repeated flag to its **last** occurrence, so a
forwarded `--model` decides what actually runs while the launcher continues to
report the configured model. On that branch this was found twice, at two
different inputs:

1. Direct duplicate. `agy-seat operator -- --model <unlisted>` runs on the
   unlisted model. Confirmed against the installed CLI:

     $ agy --model gemini-3.1-pro-high --model definitely-not-an-agy-model models
     → Model ID definitely-not-an-agy-model not in local config, defaulting to CCPA

2. A bare `--` consumed as a value, which defeats the obvious guard. A first
   attempt at a fix returned early on a forwarded `--`, reasoning that AGY's
   terminator makes later tokens positional. That is false when a value-taking
   flag eats the token:

     $ agy --model gemini-3.1-pro-high --log-file -- --model definitely-not-an-agy-model models
     → log file literally named `--`; logs
       `Model ID definitely-not-an-agy-model not in local config, defaulting to CCPA`
       and `Model resolved via default`

   `--agent`, `--conversation`, `--project` and `--mode` consume a bare token
   the same way. Only `--print-timeout --` fails first, on an invalid duration.

Practical consequence for `c6f017b`'s own stated goal: a seat can run on one
model while any report it writes names another. Whether that is in scope for
your range is your call — `c6f017b` explicitly defers model identity as "a
protocol decision rather than a launcher fix", and this may be exactly that
deferral rather than a defect in the range you hold.

## Immutable evidence, readable from any branch

Git objects are shared across worktrees, so these read here without checking the
branch out (`git cat-file -p <sha>`):

- sha256 n/a — blob ad2f1d8865aa0f34e86d253ea9d40d2a30254d33 — operator FAIL,
  unchecked config model reached `--model` and AGY_MODEL
- blob bb046bffb4e4e51d908e913c65adfefdcdcf4606 — operator FAIL, forwarded
  duplicate `--model` override (finding 1 above)
- blob 56d06ff7e335fc6b3f2bda7b31c9c7e5a007ba71 — operator NITS, no third
  identity route found; forwarding collateral and live-gate classification only

The fourth report (finding 2 above, reviewed head 9714450) is not yet published;
its reproduction is quoted inline above so nothing here depends on it.

## Coordination

Reconciliation of the two solutions is in progress on
`claude/sharp-easley-c3110f` per user decision: main's simpler argv is being
adopted (no `--add-dir`; working directory from `os.chdir` alone), together with
that branch's model-listing enforcement and an allowlist on forwardable flags.
No push or merge is authorized. Nothing here asks the operator to change its
verdict, and no cursor has been consumed.

Cursor at send: 0
