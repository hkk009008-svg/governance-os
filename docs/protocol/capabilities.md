# capability/v1 — consumable side-effect capabilities (compatibility layer)

Status: primitive-only (ADR-016). capability/v1 is generated and validated
*alongside* the live authority — it is **not yet** the live token authority. The
prose side-effect-executor token blocks and the route-time token lint
(`scripts/protocol_capacity.py`) are UNCHANGED and stay fail-closed. Do not cut
over live token authority without the follow-up ADR.

Implementation: `scripts/route_capability.py`. The hand-rolled validators there
are authoritative; the sibling JSON Schemas (`schemas/capability-v1.schema.json`,
`schemas/capability-receipt-v1.schema.json`) are documentation of the same
contract.

## What a capability is

A `governance.capability/v1` is a typed, single-use grant that binds ONE
side-effect authority to a specific route generation and a subject seat. It
carries the **authority contract of the 10-field side-effect-executor token** —

- `side_effect_id`, `allowed_command_class` (an **exact command literal**, not a
  category), `target`, `preflight`,
  `stop_if_newer_mail_or_live_target_satisfied` (the stop condition), `postcheck`,
  `observer_seats`, `final_closeout_owner`, `non_goals`

— but it is **not** a byte-verbatim superset of the token: the token's executing
seat is represented here as the enum `subject` (there is no literal `executor`
field), a new `issuer` (the granting seat) is added, and the whole is wrapped in
the capability envelope:

- `schema` — const `governance.capability/v1`.
- `capability_id` — matches `^cap-[A-Za-z0-9._-]+$`; the one-time key.
- `issuer`, `subject` — each a known seat (`director`, `director2`, `operator`,
  `operator2`, `coordinator`, `coordinator2`).
- `bound_route_id` + `bound_generation` (integer ≥ 1) — the route lineage the
  capability is bound to (Slice-2 lineage; see currency below).
- `expires_on` — exactly `{event: "packet_completed", packet_id: <non-empty>}`;
  the capability expires on packet completion.
- `state` — the lifecycle state (below).
- `extensions` — optional object for experimental data.

All 17 required fields must be present; unknown top-level fields are rejected
(`unknown authority-bearing fields rejected: …`). No string value anywhere in the
object (top-level or nested) may contain a newline or carriage return — the
injection guard, mirroring route/v1: a smuggled `\n` would otherwise let a future
Markdown projection render a second physical line a legacy per-line prose parser
reads as authority (`control characters rejected in <json-path>`).

Canonical bytes and the content hash come from `threeway.canon.canonicalize`
(RFC 8785). `capability_hash()` refuses to hash an invalid object, so an invalid
capability can never be hashed or persisted.

## Lifecycle states

`state` is one of six values (`LIFECYCLE_STATES`):

    issued → activated → consumed

plus three terminal off-ramps: `revoked`, `expired`, `failed`. The validator
accepts any of the six; it does not itself enforce transitions — consumption is
enforced by the receipt CAS (below), and currency is enforced by
`capability_is_current` (below), independent of the recorded `state`.

## One-time consumption + the receipt

Consuming a capability writes a `governance.capability-receipt/v1` — an
evidence-bearing record that the capability's single side effect was executed. A
receipt binds `capability_id` + `capability_hash` (bound by construction from the
source capability, never trusting a caller-supplied hash) and copies
`subject`/`target`, plus `result` (`ok`/`failed`), `command`, `output`.

**Non-vacuous evidence is mandatory.** A receipt that carries only a command +
its output is ceremony — it proves nothing durable. So the receipt MUST anchor to
at least one of:

- `commit` — a 7-40 char lowercase hex commit SHA, or
- `logs_ref` — a `logs/…` artifact reference.

A receipt with neither well-formed anchor is refused *before any file is written*
(`vacuous evidence rejected: …`). This mirrors the R-GATE-EVIDENCE shape
`scripts/check_go_schema.py` enforces on GO verification-reports.

**The write is an atomic one-time compare-and-swap.** The COMPLETE receipt is
written to a temp file, fsynced, then `os.link`-ed into
`<store>/<capability_id>.receipt.json`. `os.link` raises `FileExistsError` iff the
final path already exists, so exactly one consumer wins the replay race, and the
canonical path never appears with partial content (a crash or `ENOSPC` before the
link strands only a temp file that a retry ignores — the capability is never
bricked). A second consume of the same `capability_id` refuses with
`already_consumed`. Fail-closed ordering: validate the capability → (when a
route context is supplied) refuse a stale/superseded capability → refuse an
evidence command that does not match `allowed_command_class` → build + validate
the receipt (evidence non-vacuity) → only then the temp→fsync→link CAS.

**consume enforces two authority checks before it will write a receipt:**

- **(a) command-class match.** The executed evidence `command` must match the
  capability's `allowed_command_class` — the exact command literal, or a
  `<literal> …` prefix-extension (so `allowed_command_class: "git push"` permits
  `git push origin main` but rejects `git tag …`). A mismatch is refused
  `command_class_mismatch` with no receipt written — a grant for one command can
  never be spent recording a different command that ran.
- **(b) currency (only when a route context is supplied).** When the caller
  passes `--route-root` (CLI) / `authoritative=<LineageRoute>` (`consume()`), a
  capability bound to a superseded generation is refused `stale_capability` with
  no receipt — this is `capability_is_current` enforced at the execution point,
  not merely available. With no route context the currency check is skipped
  (backward-compatible).

### CLI

Validate a capability (strict, fail-closed):

    env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py validate --capability <path>

Consume a capability exactly once, writing an evidence receipt:

    env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py consume --capability <path> --store <dir> --result ok --command '<cmd>' --output '<out>' --commit <sha>

(`--logs-ref logs/<artifact>` may be given instead of, or in addition to,
`--commit`.)

Pass `--route-root <repo-root>` to additionally enforce currency: the CLI
resolves the authoritative route (`route_lineage.resolve_authoritative` over that
root's coordinator routes) and refuses a superseded capability (exit 4). When the
route set carries no lineage generation to check against (legacy/empty, or a
tip-less cycle), the requested check cannot be performed, so the CLI fails closed
(exit 4). Omit `--route-root` and currency is not enforced.

**Exit-code contract** — the CLI is a thin argparse shell that maps the security
logic's result to a process exit code, so a shell caller (a git-push wrapper, a CI
step) can gate a side effect on the exit code:

| Subcommand | Exit | Meaning |
|---|---|---|
| `validate` | 0 | valid |
| `validate` | 1 | invalid / unreadable / unparseable |
| `consume` | 0 | first consume (`consumed: <receipt path>`) |
| `consume` | 3 | `already_consumed` — the replay refusal |
| `consume` | 4 | `stale_capability` (bound generation superseded), or `--route-root` supplied with no lineage generation to check against — fail-closed |
| `consume` | 2 | any other refusal (invalid capability, vacuous evidence, `command_class_mismatch`, or an unreadable/unparseable file) |

Worked example (every command below runs literally; verified against the code):

    # write a valid capability to /tmp/cap-demo.json (17 required fields), then:
    $ env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py validate --capability /tmp/cap-demo.json
    capability valid: cap-demo-001                     # exit 0

    $ env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py consume \
        --capability /tmp/cap-demo.json --store /tmp/cap-store \
        --result ok --command 'git push origin main' --output 'To github.com ... main -> main' --commit 6398605
    consumed: /tmp/cap-store/cap-demo-001.receipt.json  # exit 0

    $ env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py consume \
        --capability /tmp/cap-demo.json --store /tmp/cap-store \
        --result ok --command 'git push origin main' --output 'To github.com ... main -> main' --commit 6398605
    already_consumed                                    # exit 3 (replay refused)

## Revocation-on-supersession (currency)

`capability_is_current(capability, authoritative)` reuses Slice-2 route lineage.
It returns true **only** while BOTH:

- `capability["bound_route_id"]` equals the authoritative route's `route_id`, AND
- `capability["bound_generation"]` equals that route's `lineage.generation`.

A capability bound to a superseded generation (a newer generation is now the
lineage tip) or to a different route entirely is **stale** — its authority is
revoked, independent of whether it has been consumed. Defense-in-depth: a `None`
generation on either side (an invalid capability, or a legacy no-generation route)
is treated as NOT current, so a generationless grant can never ride a legacy route
into "current." A stale capability is carried forward only if a newer route
re-binds it (route/v1 `capability_refs`, reserved `[]` in v1.0 — P0.4).

**This currency test is enforced at the execution point, not merely available.**
`consume(..., authoritative=<LineageRoute>)` — reached from the CLI via
`--route-root` — refuses a stale capability `stale_capability` before any receipt
is written. So a superseded grant is refused at consume time, exactly as ADR-016
states; without a route context supplied, currency is not enforced (the caller
opts in by providing the authoritative route).

## ADR-012 caveat — necessary, NOT sufficient

**A consumed capability never substitutes for the user push gate.** Consumption
records that the single side effect *ran* and refuses replay — that is necessary,
never sufficient. The user still authorizes the side effect itself. No capability
state grants authority the principal did not (ADR-012: push remains user-gated in
ALL cases, including emergency §E mitigation).

Concretely: the `consume` CLI **writes a receipt and refuses replay — it does NOT
execute the command.** The `--command`/`--output`/`--commit` arguments are
evidence *that the effect already happened*; the script records that evidence
atomically, it never runs the side effect. Gating a real push on the exit code is
the caller's job, downstream of the user's authorization.

## Compatibility status (ADR-016)

- The prose side-effect-executor token blocks are UNCHANGED.
- The live route-time token lint (`scripts/protocol_capacity.py`) is UNCHANGED and
  stays fail-closed.
- capability/v1 is generated + validated *alongside* the live authority; it is
  **not yet** the live token authority. Full cutover — and wiring `--executor-token`
  into the dormant `execute_threeway_cutover.sh` — is a scoped follow-up with the
  parked signed-bus plan.
