#!/usr/bin/env python3
"""Formation-time claim discipline: premises from shape, probes from amnesia.

Nine defects in one session (2026-07-26/27) shared a single mechanism: a claim
was verified on the property its author was thinking about, while the property
the claim actually rested on went unstated and unchecked. "The gate is enforced
pre-dispatch" — the check was correct and nothing called it. "Measured, not
assumed" — measured only in the checkout the author sat in. "This ref anchors
the report" — well-formed, resolving to nothing. Each miss was one command from
detection, and a reviewer holding no context caught all nine, because it never
made the assumption.

Two consequences drive this module's design:

The premises of a claim must come from somewhere the author cannot forget. A
recalled checklist inherits the author's blind spot — the skipped premise is
always the one that felt settled while writing. So premises are derived from the
claim's *grammatical shape*: "enforced on every X" carries fixed premises
regardless of who writes it, and the author's job shrinks from remembering to
classifying.

The check of a claim must be able to disagree with its author. A sentence
cannot contradict the person who wrote it; a command's exit code can, and a
reader given only the claim text can. So this module builds amnesiac probes —
prompts carrying the claim and nothing else — and demands citations that are
commands, not prose.

Scope, honestly. `premises` names what must be true; it does not check it.
`sweep` flags overclaim *vocabulary*, which is a property of prose and is
pattern-matched as prose — it judges no code and models no parser. `probe`
builds and optionally runs one cross-family question; the answer is advisory.
`record`/`audit` are self-reported bookkeeping whose value is that an
unverified premise becomes a visible ASSUMED row instead of an absent thought.
Everything here is an instrument for the author, upstream of the compact-pair
gates, and substitutes for none of them.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER = Path("logs/claims/ledger.jsonl")

# Evidence provenance, weakest-last. A premise resting on the last three is a
# blank cell wearing a label: REMEMBERED and INFERRED were the status of every
# missed premise in the nine measured failures, and ASSUMED is what `record`
# writes for a grammar premise the author supplied nothing for.
PROVENANCE = ("MEASURED", "RELAYED", "REMEMBERED", "INFERRED", "ASSUMED")
STRONG_PROVENANCE = frozenset({"MEASURED", "RELAYED"})


@dataclass(frozen=True)
class Premise:
    key: str
    question: str


@dataclass(frozen=True)
class Shape:
    name: str
    trigger: re.Pattern
    premises: tuple[Premise, ...]


# The grammar. Each shape's premises are the ones whose omission produced a
# measured failure; the docstring of tests/unit/test_claim_check.py maps each
# of the nine to the premise that would have named it. Editing a shape means
# re-running that fixture — it is the grammar's tether to what actually
# happened, and a grammar that drifts from it is a checklist again.
SHAPES: tuple[Shape, ...] = (
    Shape(
        "enforced",
        re.compile(
            r"\benforc\w+\b|\bgate[sd]?\b|\bon every\b|\bevery (launch|call|run|dispatch|path)\b"
            r"|\brefus\w+\b|\brejects?\b|\bprevents?\b|\bden(?:y|ies)\b|\brequir\w+ on\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "mechanism-correct",
                "The check does what it claims on inputs it receives; cite the unit evidence.",
            ),
            Premise(
                "invoked-on-path",
                "Name the caller on the enforced path and cite the grep or trace showing the call site.",
            ),
            Premise(
                "only-route",
                "List every other route to the same effect and why each passes through the check.",
            ),
            Premise(
                "real-arguments-arrive",
                "Show the real arguments reach the check — a stub that throws on anything proves wiring for nothing.",
            ),
            Premise(
                "deletion-mutation",
                "Delete the call site, not the callee; cite the test that fails.",
            ),
        ),
    ),
    Shape(
        "measured",
        re.compile(
            r"\bmeasur\w+\b|\bverif\w+\b|\btest(?:ed|s)?\b|\bpass(?:es|ed)\b|\bgreen\b"
            r"|\bconfirm\w+\b|\bproves?\b|\bnon-vacuous\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "instrument-cited",
                "Name the command that measured it and paste its real output; a measurement with no instrument is a memory.",
            ),
            Premise(
                "environment-of-record",
                "Show it holds where the suite actually runs, not only where you ran it — the other checkout, the CI PATH, the linked worktree.",
            ),
            Premise(
                "fails-when-false",
                "Restore the defect and cite the failure, failing for the right reason rather than erroring a line earlier.",
            ),
            Premise(
                "instrument-independent",
                "Show the instrument is not a restatement of the artifact under test — recomputing all(rows) beside the rows measures nothing.",
            ),
        ),
    ),
    Shape(
        "reference",
        re.compile(
            r"@[0-9a-f]{7,40}\b|\bsha256:|\bprovenance\b|\bcite[sd]?\b|\bfinding ref\b|\banchors?\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "resolves",
                "Run `git cat-file -e <commit>:<path>` (or equivalent) and cite the exit code; forty hex characters satisfy every shape check.",
            ),
            Premise(
                "is-the-named-document",
                "Open what it resolves to and cite its first lines; a ref that resolves to a different document is forged provenance, not weak provenance.",
            ),
            Premise(
                "immutable-shape",
                "Confirm the ref form is immutable (full SHA / digest), not a moving name like a branch or HEAD.",
            ),
        ),
    ),
    Shape(
        "complete",
        re.compile(
            r"\bcomplete(?:ly)?\b(?!\s+the\b)|\bcovers? (?:all|every)\b|\bexhaustive\w*\b"
            r"|\ball (?:cases|forms|paths)\b|\bno other\b|\bonly way\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "property-stated",
                "State the property the coverage approximates; a list without a property is the thing a narrowing survives.",
            ),
            Premise(
                "space-generated",
                "Generate the case space from the grammar of the domain, not from the cases you remember — three rounds each found a form the previous list omitted.",
            ),
            Premise(
                "termination-reason",
                "Say where the enumeration stops and why that is safe (reachability, grammar), because no finite sweep excludes a carve-out aimed at what it does not generate.",
            ),
            Premise(
                "evasion-attempted",
                "With the guard fully intact, try to reach the forbidden outcome anyway; cite the attempt or state that no route was found.",
            ),
        ),
    ),
    Shape(
        "absence",
        re.compile(
            r"\bnever\b|\bnothing\b|\bcannot\b|\bimpossible\b|\bno \w+ (?:exists|calls|reaches|remains)\b"
            r"|\bcosts? nothing\b|\bfor free\b|\bno-op\b|\bspends? nothing\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "search-cited",
                "Name the command that looked and paste what it found; an absence claim without a search is a hope.",
            ),
            Premise(
                "space-bounded",
                "State what space the search covered — the absence holds only there, and saying so is the claim's honest size.",
            ),
            Premise(
                "behavior-observed",
                "For 'cannot' / 'costs nothing': observe the behavior once rather than inferring it — a dry-run believed free executed a prompt.",
            ),
        ),
    ),
    Shape(
        "semantics",
        re.compile(
            r"\bparses?\b|\bdefines?\b|\baccepts?\b|\binterprets?\b|\bmeans\b|\btreats?\b"
            r"|\bconsumes?\b|\bresolves? to\b",
            re.IGNORECASE,
        ),
        (
            Premise(
                "authority-asked",
                "Invoke the semantic authority itself — the parser, shell, or CLI — on a real input and cite its exit code or behavior, never a pattern over its text.",
            ),
            Premise(
                "divergent-input-tried",
                "Try one input where surface text and semantics diverge (`--log-file --`, a help line starting with a flag name); text heuristics die there.",
            ),
        ),
    ),
)

GENERIC_PREMISES: tuple[Premise, ...] = (
    Premise(
        "falsifier-named",
        "State the single observation that would prove this claim false; a claim with no falsifier is a mood.",
    ),
    Premise(
        "embarrassing-command-run",
        "Run the one command most likely to embarrass the claim and cite its output — every miss in the source session was one command away.",
    ),
)

AMNESIAC_PROMPT = """You are an amnesiac reader. You receive ONE claim and nothing else — no code,
no history, no author intent. Do not ask for context; the absence of context is
your advantage.

Claim: {claim}

Answer in at most 10 lines:
1. Every premise that must be true for this claim to hold.
2. The single premise the author is MOST likely to have left unverified.
3. The one cheapest command or observation that would most embarrass the claim.
"""

OVERCLAIM_WORDS = re.compile(
    r"\b(enforced?|guarantee[sd]?|always|never|every|cannot|impossible"
    r"|complete(?:ly)?|verified|measured|exhaustive(?:ly)?|no way)\b",
    re.IGNORECASE,
)
# A citation marker is prose pointing at an instrument: "per `cmd`", a "$ cmd"
# line, or an observed-output arrow. This is a vocabulary heuristic about
# prose, applied to prose — the one domain where pattern-matching text is the
# honest tool, because the subject matter *is* the text.
CITATION_MARK = re.compile(r"per `|→|\$ |exit [0-9]|sha256:")


def classify(claim: str) -> list[str]:
    return [shape.name for shape in SHAPES if shape.trigger.search(claim)]


def premises_for(claim: str) -> list[tuple[str, Premise]]:
    rows: list[tuple[str, Premise]] = []
    seen: set[str] = set()
    names = classify(claim)
    for shape in SHAPES:
        if shape.name not in names:
            continue
        for premise in shape.premises:
            if premise.key not in seen:
                seen.add(premise.key)
                rows.append((shape.name, premise))
    for premise in GENERIC_PREMISES:
        if premise.key not in seen:
            seen.add(premise.key)
            rows.append(("generic", premise))
    return rows


def _print_premises(claim: str) -> None:
    names = classify(claim) or ["generic"]
    print(f"claim: {claim}")
    print(f"shape: {', '.join(names)}")
    print()
    for shape_name, premise in premises_for(claim):
        print(f"  [{shape_name}] {premise.key}")
        print(f"      {premise.question}")


def build_probe_prompt(claim: str) -> str:
    return AMNESIAC_PROMPT.format(claim=claim.strip())


def _run_probe(claim: str, timeout: int) -> int:
    """Launch the reader from an empty directory with repo pointers scrubbed.

    The first shipped version claimed a context-free reader while launching it
    in the author's cwd with the author's environment — the child sat inside
    the repository whose absence was the claimed property. Now it starts in an
    empty scratch directory with an environment reduced to PATH, HOME and TERM:
    no PWD, no GIT_*, no session variables, nothing that hands it the repo.

    Stated as what it is: pointer scrubbing, not access denial. HOME survives
    because the CLI's credentials live there, and a read-only sandbox could
    still roam the disk if it guessed a path. The enforced property is that
    nothing in cwd or env points anywhere, and the test pins exactly that
    subprocess boundary.
    """
    prompt = build_probe_prompt(claim)
    codex = shutil.which("codex")
    if codex is None:
        print(
            "probe: codex CLI not found; run the printed prompt through any "
            "reader given only the claim",
            file=sys.stderr,
        )
        print(prompt)
        return 2
    scratch = Path(tempfile.mkdtemp(prefix="amnesiac-probe-"))
    environment = {
        "PATH": "/usr/bin:/bin",
        "HOME": os.environ.get("HOME", str(scratch)),
        "TERM": os.environ.get("TERM", "dumb"),
    }
    try:
        completed = subprocess.run(
            [codex, "exec", "-s", "read-only", "--skip-git-repo-check", "-"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
            cwd=scratch,
        )
    except subprocess.SubprocessError as exc:
        print(f"probe: could not run codex: {exc}", file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    sys.stdout.write(completed.stdout)
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
    return completed.returncode


def record_entry(payload: dict, ledger: Path) -> dict:
    """Normalize one claim entry and append it to the ledger.

    Any grammar premise the author supplied nothing for is written as ASSUMED —
    the blank cell exists by construction rather than by diligence. That row is
    the whole point of the ledger: an unstated premise is invisible, an ASSUMED
    row is something `audit` can refuse.
    """
    claim = str(payload.get("claim", "")).strip()
    if not claim:
        raise ValueError("entry needs a nonempty 'claim'")
    expected_keys = {premise.key for _, premise in premises_for(claim)}
    supplied: dict[str, dict] = {}
    for item in payload.get("premises", ()):
        key = str(item.get("key"))
        if key in supplied:
            raise ValueError(f"duplicate premise key {key!r}; last-wins is how evidence launders")
        if key not in expected_keys:
            raise ValueError(f"unknown premise key {key!r} for this claim's shape")
        supplied[key] = item
    kills = [str(kill) for kill in payload.get("kills_attempted", ())]
    if any(not kill.strip() for kill in kills):
        raise ValueError("a blank kill entry counts a kill that was not attempted")
    rows = []
    for _, premise in premises_for(claim):
        item = supplied.get(premise.key)
        if item is None:
            rows.append({"key": premise.key, "status": "ASSUMED", "cite": ""})
            continue
        status = str(item.get("status", "ASSUMED")).upper()
        if status not in PROVENANCE:
            raise ValueError(
                f"premise {premise.key!r} has unknown status {status!r}; "
                f"use one of {', '.join(PROVENANCE)}"
            )
        if status in STRONG_PROVENANCE and not str(item.get("cite", "")).strip():
            raise ValueError(
                f"premise {premise.key!r} is {status} with an empty citation; "
                "a strong status without an instrument is a memory wearing a label"
            )
        rows.append(
            {
                "key": premise.key,
                "status": status,
                "cite": str(item.get("cite", "")),
            }
        )
    entry = {
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim": claim,
        "shapes": classify(claim) or ["generic"],
        "premises": rows,
        "kills_attempted": kills,
    }
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def audit_ledger(ledger: Path) -> list[str]:
    """Every way a recorded claim is weaker than it reads, one line each."""
    if not ledger.is_file():
        return []
    problems: list[str] = []
    for line_number, line in enumerate(
        ledger.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        entry = json.loads(line)
        claim = entry.get("claim", "")[:70]
        # Reconstruct what the claim requires rather than trusting what the
        # entry brought: a hand-written line with zero premises audited clean
        # once, which is absent evidence laundered into a good report.
        expected = {premise.key for _, premise in premises_for(entry.get("claim", ""))}
        seen_keys: list[str] = []
        for premise in entry.get("premises", ()):
            key = premise.get("key")
            seen_keys.append(key)
            status = premise.get("status")
            if status not in STRONG_PROVENANCE:
                problems.append(
                    f"{ledger}:{line_number}: [{status}] {key} — {claim}"
                )
            elif not str(premise.get("cite", "")).strip():
                problems.append(
                    f"{ledger}:{line_number}: [UNCITED-STRONG] {key} — {claim}"
                )
        for missing in sorted(expected - set(seen_keys)):
            problems.append(
                f"{ledger}:{line_number}: [MISSING] {missing} — {claim}"
            )
        if len(seen_keys) != len(set(seen_keys)):
            problems.append(
                f"{ledger}:{line_number}: [DUPLICATE-KEY] — {claim}"
            )
        kills = [str(kill).strip() for kill in entry.get("kills_attempted", ())]
        if not any(kills):
            problems.append(
                f"{ledger}:{line_number}: [NO-KILL] nothing tried to falsify — {claim}"
            )
    return problems


_DATA_SUFFIXES = frozenset({".json", ".jsonl", ".toml", ".lock", ".txt"})
_PROSE_SUFFIXES = frozenset({".md", ".rst"})


def _claim_bearing_text(file_name: str, line: str) -> str | None:
    """The part of an added line where a published claim could live, or None.

    Mention is not use: overclaim vocabulary inside a code string literal or a
    data file is somebody talking *about* claims, and sweeping it produced 73
    flags of noise on the kit's own first range. Prose files carry claims on
    any line; code carries them in comments; data carries none.
    """
    suffix = Path(file_name).suffix
    if suffix in _DATA_SUFFIXES:
        return None
    if suffix in _PROSE_SUFFIXES:
        return line
    comment = line.find("#")
    if comment == -1:
        return None
    return line[comment:]


def sweep_range(root: Path, base: str, head: str) -> list[str]:
    """Overclaim vocabulary in added lines with no citation marker nearby.

    Vocabulary only, and said plainly: this flags words, judges nothing, and a
    finding means "a strong word appeared with no instrument in sight", not
    "the sentence is false". Its value is where it points, not what it proves.
    Measured on its own first range: 73 flags, dominated by fixture strings —
    an optional lens, not a publication step.

    Scope follows the cause of the noise, not the file list of the moment. The
    sweep's target is published prose claims; its first run returned 73 flags
    dominated by *mentions* — vocabulary inside code string literals and test
    fixtures — which are not claims and had no reason to be in scope. So: prose
    files are swept whole-line; code and extensionless files only on comment
    lines (the wrapper's claims live there); data files (.json/.jsonl/.toml/
    .lock) are excluded, because data carries no claims. Docstring prose in code
    is therefore missed here — that failure class is prove-a-control's beat.
    The citation must sit on the same line: proximity never bound a citation to
    a claim, and an unrelated `$ echo` two lines down once satisfied the check.
    """
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    completed = subprocess.run(
        ["git", "--no-replace-objects", "diff", f"{base}..{head}"],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git diff failed: {completed.stderr.strip() or completed.returncode}"
        )
    findings: list[str] = []
    current_file = "?"
    added: list[tuple[str, str]] = []
    for raw in completed.stdout.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw[6:]
        elif raw.startswith("+") and not raw.startswith("+++"):
            added.append((current_file, raw[1:]))
    for file_name, line in added:
        scoped = _claim_bearing_text(file_name, line)
        if scoped is None:
            continue
        match = OVERCLAIM_WORDS.search(scoped)
        if not match:
            continue
        if CITATION_MARK.search(scoped):
            continue
        findings.append(f"{file_name}: {match.group(0)!r} uncited near: {scoped.strip()[:90]}")
    return findings


def lottery(ledger: Path, count: int) -> list[str]:
    if not ledger.is_file():
        return []
    claims = [
        json.loads(line)["claim"]
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return random.sample(claims, min(count, len(claims)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="claim_check.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("premises", help="derive a claim's premises from its shape")
    p.add_argument("claim")

    p = sub.add_parser("probe", help="build (and with --execute run) an amnesiac probe")
    p.add_argument("claim")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--timeout", type=int, default=180)

    p = sub.add_parser(
        "record",
        help="append one claim entry (flags, or JSON on stdin when no --claim)",
    )
    p.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    p.add_argument("--claim")
    p.add_argument(
        "--premise", nargs=3, action="append", metavar=("KEY", "STATUS", "CITE"),
        default=[],
    )
    p.add_argument("--kill", action="append", default=[])

    p = sub.add_parser("audit", help="list ASSUMED/weak premises and unkilled claims")
    p.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)

    p = sub.add_parser("sweep", help="flag uncited overclaim vocabulary in a diff range")
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--repo-root", type=Path, default=Path.cwd())

    p = sub.add_parser("lottery", help="sample recorded claims for a fresh probe")
    p.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    p.add_argument("--count", type=int, default=3)

    args = parser.parse_args(argv)

    if args.command == "premises":
        _print_premises(args.claim)
        return 0
    if args.command == "probe":
        if args.execute:
            return _run_probe(args.claim, args.timeout)
        print(build_probe_prompt(args.claim))
        return 0
    if args.command == "record":
        try:
            if args.claim:
                payload = {
                    "claim": args.claim,
                    "premises": [
                        {"key": key, "status": status, "cite": cite}
                        for key, status, cite in args.premise
                    ],
                    "kills_attempted": args.kill,
                }
            else:
                payload = json.loads(sys.stdin.read())
            entry = record_entry(payload, args.ledger)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"record: {exc}", file=sys.stderr)
            return 2
        assumed = [row["key"] for row in entry["premises"] if row["status"] == "ASSUMED"]
        print(f"recorded: {entry['claim'][:70]}")
        if assumed:
            print(f"ASSUMED (blank cells): {', '.join(assumed)}")
        return 0
    if args.command == "audit":
        problems = audit_ledger(args.ledger)
        for problem in problems:
            print(problem)
        print(f"{len(problems)} weak premise(s)/unkilled claim(s)")
        return 1 if problems else 0
    if args.command == "sweep":
        try:
            findings = sweep_range(args.repo_root, args.base, args.head)
        except RuntimeError as exc:
            print(f"sweep: {exc}", file=sys.stderr)
            return 2
        for finding in findings:
            print(finding)
        print(f"{len(findings)} uncited overclaim word(s) — vocabulary flags, not verdicts")
        return 1 if findings else 0
    if args.command == "lottery":
        for claim in lottery(args.ledger, args.count):
            print(f'probe: .venv/bin/python scripts/claim_check.py probe --execute "{claim}"')
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
