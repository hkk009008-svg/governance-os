# Skill-use outcome rows — advisory schema

> Appended by seats at wrap to `logs/learning/outcomes.jsonl`.
> Reported by `pipeline/learning_metrics.py`. Advisory under contract I1/I2:
> these counts bind no lifecycle decision and grant no authority. The
> reporter writes nothing. Wiring any total here into accept / decline /
> expire / edit / prune is a contract change and reviews as one (I7).

## Failure this record addresses

Skill load was invisible. A skill could sit unused, or fail in use, with
no durable slope — so revision happened from recall, and usage-count
proposals (rejected by ADR-067) had nothing honest to cite instead.

## Row shape

One JSON object per line. Required keys:

| Key | Type | Closed set / shape |
|---|---|---|
| `ts` | string | UTC `YYYY-MM-DDTHH:MM:SSZ` |
| `event` | string | `skill-use` |
| `skill` | string | Directory name under `.agents/skills/` |
| `task_ref` | string | Immutable `<sent-path>@<40-hex>`, or `none` |
| `outcome` | string | `helped` \| `hindered` \| `neutral` |
| `evidence_ref` | string | `<path>@<40-hex>`, `sha256:<64-hex>`, or `none` |
| `seat` | string | Envelope identity that loaded the skill (`author`, `reviewer`, or a legacy seat name in older rows), or `none` |

Optional: `note` (one line, no authority claim).

Example (not a live measurement):

```json
{"ts": "2026-08-12T22:00:00Z", "event": "skill-use", "skill": "create-regression-pin", "task_ref": "none", "outcome": "helped", "evidence_ref": "none", "seat": "reviewer", "note": "pin authored; --runxfail went red"}
```

Non-`skill-use` events in the same file (the Stage 5 baseline row) are
other outcome types; the reporter ignores them for these counters.

## Who writes, who reads

- **The live role** appends at wrap when a named skill was loaded, or skips
  with a one-line reason in the checkpoint `Lessons:` line. There is no
  quota and no penalty for `none`.
- **`pipeline/learning_metrics.py`** reports `skill_use_rows` split by
  outcome, plus per-skill totals. Malformed `skill-use` lines are counted
  as `skill_use_malformed` and never coerced into helped/hindered/neutral.
- **`pipeline/mailbox_writer.py`**, **`pipeline/compact_pair_loop.py`**,
  **`pipeline/learning_extract.py`**, **`pipeline/learning_index.py`**, and
  **`pipeline/protocol_mailbox.py`** must not read this file or these
  counters. That absence is the recorded rejection of
  usage-counts-as-lifecycle-evidence.

## Interpretation

Helped/hindered/neutral is the seat's wrap judgment, not a measurement.
A high helped count can mean the skill is useful or that seats only log
successes. Treat the slope as a pointer: hindered rows with an
`evidence_ref` are the input to a `procedure` candidate, not a vote to
edit the skill in place.

## Rule maintenance

1. Observed failure: skill load and failure had no durable record, so
   revision and the rejected usage-count proposals had no honest substrate.
2. Mode/risk: advisory in every mode; appending a row is ordinary local
   logging and grants nothing.
3. Operating cost: one JSONL line at wrap, plus a read-only reporter pass.
4. Owner: learning plane (ADR-067 / ADR-068).
5. Re-evaluate: after the first hindered rows are cited by a disposed
   `learning-candidate`, or if two consecutive review cycles find the
   counters unused, keep, adjust, or retire per `docs/protocol/work-modes.md`.
