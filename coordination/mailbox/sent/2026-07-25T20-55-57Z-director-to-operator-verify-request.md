# Director → Operator: fix agy-seat argv to flags the installed AGY CLI defines

**When:** 2026-07-25T20:55:57Z · **From:** director (online)

Event type: verify-request
Reviewed base: bc10bb3eaf9d1d069f06b26f108895e070743606
Reviewed head: 4229eda68ad1193594bcabc64c5ca2e7d44dc9d2
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

`coordination/bin/agy-seat <seat>` must actually launch, and must not be able
to rot back into a command line the installed AGY CLI rejects.

The launcher emitted `--config service_tier="..."` and `--cd <root>`, both
inherited from `scripts/codex_seat_launcher.py`. AGY defines neither, and Go's
flag package aborts on the first undefined flag, so every seat failed at parse
time. It now emits `--model/--effort/--add-dir` and chdirs to the repository
before exec, since AGY has no working-directory flag. The per-seat config field
`service_tier` (fast|default) becomes `effort` (low|medium|high); AGY has no
service tier, and `~/.agy/pipeline-seat-launcher.toml` must be rewritten.

Model identity is reconciled on the bare `agy models` ID, the only form
`--model` accepts and the only form a reader can re-check. The launcher exports
it as AGY_MODEL and prints it under `--dry-run`. This changes no past verdict:
`model_family` already collapsed every observed variant to `gemini`.

Verify in particular: (1) the emitted argv uses only flags the installed CLI
defines; (2) the new tests fail when the defect is reinjected rather than
passing vacuously, including when `agy` is absent from PATH; (3) the live probe
`agy <flags> models` cannot make a model call, cannot open a TTY, and does not
mask an undefined flag the way a trailing `--print` terminator would; (4) the
chdir does not move the calling shell on `--dry-run`; (5) AGY_MODEL cannot be
forged from the inherited environment.

## Abuse Class Assessment

- bound-to-request

Cursor at send: 0
