# Peer invocation — how the two CLIs work as one unit

Pipeline has exactly two participants: the `claude` CLI and the `codex` CLI.
Neither is a service the other talks to. Each is a program the other can run.

## The mechanism

    pipeline peer ask <claude|codex|agy> --task <id> --prompt-file <f> [options]
    pipeline peer receipts [--task <id>]

One verb, three backends, one receipt format. The direction is whichever
terminal you are sitting in: from a Claude session you `ask codex`, from a
Codex session you `ask claude`, and the machinery is identical because the two
CLIs are symmetric where it matters.

| Capability | `claude` | `codex` |
|---|---|---|
| Headless | `--print` | `exec` |
| Machine-readable output | `--output-format json` | `--json` (JSONL) |
| Prompt | stdin | stdin (`-`) |
| Working root | `--add-dir` | `--cd` |
| Containment | `--permission-mode` | `--sandbox` |
| Spend ceiling | `--max-budget-usd` | none — bounded by `--timeout` |
| Final message | `.result` in the JSON | `--output-last-message <file>` |

`pipeline/peer_backends.py` owns the two places they are *not* symmetric.
`pipeline/peer.py` owns the runner, the receipt, and the verb.

## Why this replaces the bridge

The previous mechanism was a persistent Agent-SDK peer (`pipeline-codex-bridge`)
started over MCP and addressed through Claude Desktop's cross-session plane.
Its own contract said it "reports no delivery ack", and `OPERATIONS.md` carried
a troubleshooting row for exactly that: *relay is submitted but delivery is
unknown*. That row is now unreachable.

1. **Delivery is acknowledged.** The child's exit code and captured output are
   the acknowledgement. A peer that did not run cannot look like one that did.
2. **One process, one budget, terminates.** No long-lived peer to leak, no
   duplicate-bridge failure mode, no registration-lag ambiguity.
3. **The model is observed, not declared.** `model_reported` comes from the
   peer's own output. Where the peer reports nothing, the receipt records
   `null` and says so — it is never back-filled from the `--model` request.
   A receipt that echoed the request would agree with its author by
   construction, which is the one thing it must not do.
4. **No host assumption.** Two terminals, any machine, no desktop app.

A receipt is evidence, not attestation: whoever can write the file can forge
it. It is strictly better than prose the author typed, and strictly weaker
than a signature. Do not describe it as proof of who reviewed.

## AGY is a backend, not a side

`pipeline peer ask agy --role <map|challenge|evasion|debug|implement|review>`
dispatches to the parent-owned `~/.local/bin/claude-agy` or `codex-agy`
wrapper — whichever matches `PIPELINE_SIDE` (default `claude`). Those wrappers
take the shared `~/.codex/agy-desktop-user-inflight.lock`, so the lane still
serialises no matter which side calls it.

AGY is **advisory in both directions**. Its receipts carry `"advisory": true`.
It is never a seat, never a mailbox participant, never a reviewer, and never a
GO/NITS/FAIL source. `config/model-families.toml` keeps
`active_families = ["claude", "gpt"]`, so a gemini-family opinion cannot
satisfy the different-family requirement that `compact_pair_loop.py` validates
at publication. Promoting AGY to a verdict-bearing side would be a
trust-granting schema change with its own high-risk-control review.

## Authority

Running a peer is a **provider launch and paid spend**. Per `AGENTS.md` that
needs live, exact authority for the executor, target, effect, and scope — the
command does not grant it, and neither does a task id.

The command prints the exact argv to stderr before launching. `--dry-run`
prints it and exits without launching, which is the right way to show a
proposed invocation to whoever must authorize it.

Bounds that are enforced rather than advised:

- `--task` is required, so every launch is attributable to a work unit.
- `--max-usd` defaults to `1.00` and maps to `claude --max-budget-usd`.
- `--timeout` defaults to 900s; exceeding it records exit 124 with no result,
  never a partial answer presented as a whole one.
- Read-only is the default. For `claude` and `codex`, `--write` widens exactly
  one flag — `--permission-mode` and `--sandbox` respectively. The AGY wrapper
  has no read-only flag and no ceiling of its own, so `--write` cannot widen
  anything there: `peer_backends.build_agy` refuses `--write` for every
  advisory role and requires it for `implement`, the one role that writes.
  Accepting it silently was a caller believing in containment it did not have.

## Receipts

`coordination/peer/<task>/<seq>-<side>.json`, schema `peer-receipt/1`:

    {
      "schema": "peer-receipt/1",
      "task": "...", "side": "codex", "role": "reviewer",
      "advisory": false,
      "started": "...", "duration_s": 93.4, "exit_code": 0,
      "argv_sha256": "...", "argv_binary": "/path/to/codex",
      "prompt_sha256": "...", "result_sha256": "...",
      "model_reported": "gpt-5-codex", "cost_usd": null,
      "notes": []
    }

The file name is `<seq>-<side>.json` with `seq` zero-padded to four digits and
taken from one past the highest already present, never from a count.

`notes` is where the mechanism admits what it does not know: an unparseable
result, a missing model field, a peer's stderr, a timeout. An empty `notes`
with a `null` model is not possible — absence is always narrated.

## Verification

`tests/unit/test_peer.py` covers argv construction for all three backends,
fail-closed on a missing binary, the closed AGY role set, output parsing for
both result shapes, receipt sequencing and hashing, timeout handling, and the
control that a receipt never reports the requested model.
`tests/unit/test_peer_review_findings.py` holds the review-driven controls,
including `test_an_absent_model_is_always_narrated`, which is what keeps the
"absence is always narrated" sentence above from being prose: a claude payload
with no model and no `modelUsage` returned an empty `notes` until that test
existed. Nothing in either suite launches a provider: `shutil.which` is
monkeypatched and `run()` takes an injected runner.

That means the argv this repository *builds* is verified, and the shape of
what a real `claude` or `codex` *emits* is parsed defensively but not
confirmed against a live run. One authorized round trip per side would settle
it; until then the parsers' behaviour on absence — record `null`, add a note —
is what keeps an unconfirmed shape from becoming a false fact.
