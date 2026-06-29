# OPERATIONS.md — Governance OS

> Run, configure, and troubleshoot the program.
> For *what* the program does and *why* it is shaped this way, see
> [ARCHITECTURE.md](ARCHITECTURE.md) and [DECISIONS.md](DECISIONS.md).

---

## §1 Prerequisites

<!-- List OS, runtime version, system packages, and any one-time setup steps
     required before the program can run. -->

- OS: <fill-in: e.g., macOS 13+ / Ubuntu 22.04+>
- Runtime: <fill-in: e.g., Python 3.11+>
- System packages: <fill-in: e.g., ffmpeg, git>

---

## §2 Installation

<!-- Step-by-step commands to go from a clean clone to a runnable state.
     Every command here must be copy-pasteable and verified against HEAD. -->

```bash
# 1. Clone and enter the repo
git clone <fill-in: repo URL>
cd <fill-in: repo dir>

# 2. Create and activate a virtual environment
<fill-in: e.g., python -m venv .venv && source .venv/bin/activate>

# 3. Install dependencies
<fill-in: e.g., pip install -r requirements.txt>

# 4. Copy and edit config
<fill-in: e.g., cp config.example.yaml config.yaml && $EDITOR config.yaml>
```

---

## §3 Running the Program

<!-- Show the canonical invocation(s) for the most common use cases.
     Label each with the scenario it covers. -->

```bash
# Standard run
<fill-in: e.g., python main.py --config config.yaml>

# Dry-run / preview mode (no side effects)
<fill-in: command>

# Verbose / debug output
<fill-in: command>
```

---

## §4 Configuration Reference

<!-- Describe every config key the operator is expected to set.
     Flag which keys are required vs optional and what the safe defaults are. -->

Config file: `<fill-in: path>`

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `<fill-in>` | yes/no | `<fill-in>` | <fill-in: what it controls> |
| `<fill-in>` | yes/no | `<fill-in>` | <fill-in> |

**Environment variable overrides:**

| Var | Overrides key | Notes |
|-----|--------------|-------|
| `<fill-in>` | `<fill-in>` | <fill-in> |

---

## §5 Running Tests

<!-- Canonical commands for the full test suite, a single test, and CI mode. -->

```bash
# Full suite
<fill-in: e.g., env -u GIT_INDEX_FILE .venv/bin/python -m pytest>

# Single test file
<fill-in: e.g., pytest tests/test_foo.py -v>

# CI smoke check (fast structural invariants)
<fill-in: e.g., python scripts/ci_smoke.py>
```

---

## §6 Common Workflows

<!-- Brief recipes for the tasks operators perform most often.
     Each recipe: title, 2-5 commands, expected output. -->

### <fill-in: e.g., "Add a new X">

```bash
<fill-in: commands>
```

Expected: <fill-in: what success looks like>

### <fill-in: e.g., "Rotate credentials">

```bash
<fill-in: commands>
```

Expected: <fill-in>

---

## §7 Troubleshooting

<!-- Map symptoms to causes and fixes. Prioritize failures that have actually
     occurred in production or that are non-obvious from the error message. -->

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `<fill-in: error message>` | <fill-in: cause> | <fill-in: fix> |
| <fill-in> | <fill-in> | <fill-in> |

---

## §8 Logs & Observability

<!-- Where do logs go? What log levels mean. How to find a specific run's output. -->

- Log location: `<fill-in: path or stdout>`
- Log format: <fill-in: e.g., JSON structured / plain text>
- Key log markers: `<fill-in: e.g., "GATE MET" = pipeline stage passed>`

---

## §9 Upgrading & Migrations

<!-- Steps to take when upgrading the program or its dependencies.
     Note any schema migrations, config key renames, or breaking changes. -->

<fill-in: e.g., "When upgrading from vX to vY, run: python scripts/migrate.py">

---

## §10 Security Notes

<!-- Credentials, secrets, and access controls that an operator must understand.
     Never store actual secrets here — point to where they live and how to rotate. -->

- Secrets stored in: <fill-in: e.g., `.env` (gitignored) / secrets manager>
- Rotation procedure: <fill-in>
- Least-privilege principle: <fill-in: what access the program needs and why>
