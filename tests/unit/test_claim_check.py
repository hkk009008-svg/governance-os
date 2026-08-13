"""Tests for the formation-time claim discipline engine.

The grammar's tether to reality is the nine-claims fixture: every entry is a
claim actually made in the 2026-07-26/27 session, paired with the premise whose
omission produced the measured failure. The grammar exists to hand an author
that premise without recall, so the one test that matters is that it does — and
the negative control beside it is what keeps that test honest, because a
classifier that assigned every premise to every claim would pass the fixture
while teaching nothing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import claim_check


# (claim as made, premise that would have named the miss)
NINE_MEASURED_FAILURES = (
    # Round 1: held only in the author's checkout; failed in every worktree.
    (
        "Measured, not assumed: this control is verified and passes in every checkout",
        "environment-of-record",
    ),
    # Rounds 2-3: the form list was an enumeration; :/ then :x then ://x won.
    (
        "The guard refuses every pathspec magic form; coverage is complete",
        "space-generated",
    ),
    # Round 4: trackedness of the path stood in for the committed rule bytes.
    (
        "The provenance check cites the committed rule; the reference anchors it",
        "is-the-named-document",
    ),
    # The comment that outlived its mechanism: no instrument existed any more.
    (
        "The emitted argv is checked against this set and verified against provider --help",
        "instrument-cited",
    ),
    # The preflight gate nothing on the dispatch path invoked.
    (
        "The parity gate is enforced pre-dispatch on every launch",
        "invoked-on-path",
    ),
    # The readiness assertion that recomputed all(rows) beside the rows.
    (
        "main is verified not ready when any row fails",
        "instrument-independent",
    ),
    # Three fabricated references, each forty well-formed hex characters.
    (
        "finding ref sha256:857f... and the report @2ae144202a8417c39e87426bb60da4d3d5a7b481 anchor the FAIL",
        "resolves",
    ),
    # The regex over help text deciding what a Go parser accepts.
    (
        "defined_cli_flags returns the flags the installed CLI defines and accepts",
        "authority-asked",
    ),
    # The dry-run believed free that executed a prompt.
    (
        "the probe costs nothing extra and cannot spend during dry-run",
        "behavior-observed",
    ),
)


@pytest.mark.parametrize("claim,missed", NINE_MEASURED_FAILURES)
def test_grammar_hands_the_author_the_premise_that_was_actually_missed(
    claim: str, missed: str
) -> None:
    keys = [premise.key for _, premise in claim_check.premises_for(claim)]
    assert missed in keys, (claim, keys)


def test_a_neutral_claim_gets_only_the_generic_premises() -> None:
    """The negative control that keeps the fixture above honest.

    A classifier that matched every shape on every sentence would satisfy all
    nine fixture rows while discriminating nothing — the exact combined-assert
    vacuity this repository keeps re-finding. So a sentence with no claim
    vocabulary must classify to nothing and receive only the generic premises.
    """
    claim = "the refactor moves two helpers into a shared module"
    assert claim_check.classify(claim) == []
    keys = [premise.key for _, premise in claim_check.premises_for(claim)]
    assert keys == [premise.key for premise in claim_check.GENERIC_PREMISES]


def test_every_claim_carries_the_embarrassing_command_premise() -> None:
    """Every miss in the source session was one command from detection."""
    for claim, _ in NINE_MEASURED_FAILURES:
        keys = [premise.key for _, premise in claim_check.premises_for(claim)]
        assert "embarrassing-command-run" in keys, claim


def test_probe_prompt_carries_the_claim_and_no_working_context() -> None:
    """Amnesia is the probe's entire value, so leakage is the defect to pin.

    The prompt must contain the claim and the fixed instructions — never the
    cwd, environment, or anything else that would let the reader inherit the
    author's context.
    """
    claim = "the gate is enforced on every launch"
    prompt = claim_check.build_probe_prompt(claim)

    assert claim in prompt
    assert "amnesiac" in prompt
    import os

    assert os.getcwd() not in prompt
    assert "GIT_INDEX_FILE" not in prompt


def test_record_writes_assumed_rows_for_unsupplied_premises(tmp_path: Path) -> None:
    """The blank cell exists by construction, not by diligence.

    An unstated premise is invisible; an ASSUMED row is refusable. `record`
    therefore fills every grammar premise the author did not cite, so the
    ledger shows what was skipped rather than only what was done.
    """
    ledger = tmp_path / "ledger.jsonl"
    entry = claim_check.record_entry(
        {
            "claim": "the sweep is verified on every launch",
            "premises": [
                {"key": "instrument-cited", "status": "MEASURED", "cite": "$ pytest -q → 36 passed"}
            ],
            "kills_attempted": ["deleted the call site; test failed"],
        },
        ledger,
    )

    statuses = {row["key"]: row["status"] for row in entry["premises"]}
    assert statuses["instrument-cited"] == "MEASURED"
    assert statuses["invoked-on-path"] == "ASSUMED"
    written = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert written["claim"] == entry["claim"]


def test_audit_flags_weak_premises_and_unkilled_claims(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    claim_check.record_entry(
        {
            "claim": "the gate is enforced on every launch",
            "premises": [
                {"key": "invoked-on-path", "status": "REMEMBERED", "cite": "I am fairly sure"}
            ],
        },
        ledger,
    )

    problems = claim_check.audit_ledger(ledger)

    assert any("REMEMBERED" in problem for problem in problems)
    assert any("ASSUMED" in problem for problem in problems)
    assert any("NO-KILL" in problem for problem in problems)


def test_audit_passes_a_fully_cited_killed_claim(tmp_path: Path) -> None:
    """The positive control: a clean entry must not be flagged.

    Without this, an audit that flagged everything would satisfy the test
    above while making the ledger unusable.
    """
    ledger = tmp_path / "ledger.jsonl"
    claim = "the refactor moves two helpers into a shared module"
    claim_check.record_entry(
        {
            "claim": claim,
            "premises": [
                {"key": "falsifier-named", "status": "MEASURED", "cite": "$ pytest → red on revert"},
                {"key": "embarrassing-command-run", "status": "MEASURED", "cite": "$ grep -rn helper → 2 sites"},
            ],
            "kills_attempted": ["reverted the move; suite failed"],
        },
        ledger,
    )

    assert claim_check.audit_ledger(ledger) == []


def _throwaway_repo(tmp_path: Path) -> Path:
    """A repository built for the test, never the checkout under review."""
    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    (root / "notes.md").write_text("plain start\n", encoding="utf-8")
    git("add", "notes.md")
    git("commit", "-q", "-m", "base")
    return root


def test_sweep_flags_uncited_overclaims_and_spares_cited_ones(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    # Citations bind on the same line only — proximity never bound a citation
    # to a claim, and an unrelated `$ echo` two lines below once suppressed a
    # finding. The uncited line here sits right beside cited ones to pin that
    # neighbours spare nothing.
    (root / "notes.md").write_text(
        "plain start\n"
        "the module is verified — per `pytest tests/unit -q`\n"
        "an unrelated middle line\n"
        "another unrelated middle line\n"
        "the gate is always enforced here\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "notes.md"],
        cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "claims"],
        cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )

    findings = claim_check.sweep_range(root, "HEAD~1", "HEAD")

    assert len(findings) == 1, findings
    assert "always" in findings[0] or "enforced" in findings[0]
    assert "verified" not in findings[0]


def test_sweep_reports_a_broken_range_instead_of_a_clean_answer(tmp_path: Path) -> None:
    """An unanswerable diff is not a diff with no findings."""
    root = _throwaway_repo(tmp_path)

    with pytest.raises(RuntimeError):
        claim_check.sweep_range(root, "HEAD~9", "HEAD")


def test_lottery_samples_only_recorded_claims(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    for text in ("claim one is measured", "claim two is enforced on every run"):
        claim_check.record_entry({"claim": text}, ledger)

    sampled = claim_check.lottery(ledger, 5)

    assert len(sampled) == 2
    assert set(sampled) == {"claim one is measured", "claim two is enforced on every run"}


# --- round-2 controls, from the operator FAIL on c34c7af..1be2808 ---------------

# Real prose, both directions. The reviewer defeated the fixture by replacing a
# shape trigger with `\b(is|this)\b` — every fixture row still passed, because
# nothing constrained what a trigger must NOT match. These sentences are the
# constraint: the positives are claims from this repository's own idiom that
# MUST classify, the negatives are ordinary prose that MUST NOT. A degenerate
# trigger now fails here instead of surviving everything.
SHAPE_POSITIVES = (
    # One sentence per trigger family, or deleting a family survives the corpus:
    # dropping \benforc\w+\b stayed green once because every enforced positive
    # reached the shape through a synonym.
    ("the validator enforces the schema at publication", "enforced"),
    ("the guard rejects unsafe paths", "enforced"),
    ("the hook prevents two directors from binding", "enforced"),
    ("the writer hard-denies direct mailbox edits", "enforced"),
    ("36 tests passed on the reviewed range", "measured"),
    ("the fix is verified by the suite", "measured"),
    ("the report is anchored at sha256:0f2a", "reference"),
    ("the sweep covers every form and coverage is complete", "complete"),
    ("the launcher never spends during dry-run", "absence"),
    ("the CLI parses --model as its own flag", "semantics"),
)
NEUTRAL_PROSE = (
    "complete the unification of the two templates",
    "the free-form mailbox body carries prose",
    "wrap the output in a code block",
    "this is the config the seat loads",
    "read the file and move on to the next one",
)


@pytest.mark.parametrize("sentence,shape", SHAPE_POSITIVES)
def test_repository_idiom_claims_classify_to_their_shape(sentence: str, shape: str) -> None:
    assert shape in claim_check.classify(sentence), (sentence, claim_check.classify(sentence))


@pytest.mark.parametrize("sentence", NEUTRAL_PROSE)
def test_ordinary_repository_prose_classifies_to_nothing(sentence: str) -> None:
    assert claim_check.classify(sentence) == [], (sentence, claim_check.classify(sentence))


def test_probe_subprocess_starts_pointerless(monkeypatch, tmp_path: Path) -> None:
    """The claimed property, pinned at the subprocess boundary it lives at.

    The first shipped probe claimed a context-free reader while launching it in
    the author's cwd with the author's environment — the prompt was clean and
    the process sat inside the repository. Amnesia is a property of the launch,
    so the launch is what gets asserted: an empty working directory that is not
    ours, and an environment with no PWD, no GIT_*, nothing but PATH/HOME/TERM.
    """
    seen: dict = {}

    def recorder(argv, **kwargs):
        seen.update(kwargs)
        seen["argv"] = argv
        seen["cwd_contents"] = list(Path(kwargs["cwd"]).iterdir())
        return subprocess.CompletedProcess(argv, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(claim_check.subprocess, "run", recorder)
    monkeypatch.setattr(claim_check.shutil, "which", lambda _name: "/probe/bin/codex")

    code = claim_check._run_probe("the gate is enforced on every launch", 5)

    assert code == 0
    cwd = Path(seen["cwd"])
    assert cwd != Path.cwd()
    assert seen["cwd_contents"] == []
    environment = seen["env"]
    assert set(environment) <= {"PATH", "HOME", "TERM"}
    assert "PWD" not in environment
    assert not any(key.startswith("GIT_") for key in environment)


def test_record_refuses_the_laundering_shapes(tmp_path: Path) -> None:
    """Each rejection is a way absent evidence once audited clean.

    Duplicate keys were last-wins, a MEASURED status accepted an empty
    citation, an unknown key rode along unexamined, and a blank kill string
    counted as an attempt. Every one is a strong-looking entry with nothing
    inside, which is worse than a weak entry because audit believed it.
    """
    ledger = tmp_path / "ledger.jsonl"
    base = {"claim": "the gate is enforced on every launch"}

    for premises, kills, why in (
        ([{"key": "invoked-on-path", "status": "MEASURED", "cite": "a"},
          {"key": "invoked-on-path", "status": "ASSUMED", "cite": ""}], ["mutated; test failed"], "duplicate"),
        ([{"key": "invoked-on-path", "status": "MEASURED", "cite": ""}], ["mutated; test failed"], "empty citation"),
        ([{"key": "invoked-on-path", "status": "MEASURED",
           "cite": "trust me; this is obvious"}], ["mutated; test failed"], "prose citation"),
        ([{"key": "invoked-on-path", "status": "MEASURED",
           "cite": "$ grep -n caller → main:12"}], ["thought about it"], "vacuous kill"),
        ([{"key": "not-a-premise", "status": "MEASURED", "cite": "a"}], ["mutated; test failed"], "unknown key"),
        ([], [""], "blank kill"),
    ):
        with pytest.raises(ValueError):
            claim_check.record_entry(
                {**base, "premises": premises, "kills_attempted": kills}, ledger
            )
    assert not ledger.exists(), why


def test_audit_reconstructs_instead_of_trusting_the_entry(tmp_path: Path) -> None:
    """A hand-written ledger line with zero premises once audited clean.

    audit now rederives the claim's required premises and flags every missing
    row, every strong status with an empty citation, and kills that are only
    blank strings — the entry is checked against the grammar, not against
    itself.
    """
    ledger = tmp_path / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps(
            {
                "claim": "the gate is enforced on every launch",
                "premises": [
                    {"key": "invoked-on-path", "status": "MEASURED", "cite": ""}
                ],
                "kills_attempted": ["", "  "],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    problems = claim_check.audit_ledger(ledger)

    assert any("[PROSE-CITE] invoked-on-path" in problem for problem in problems)
    assert any("[MISSING] mechanism-correct" in problem for problem in problems)
    assert any("[NO-KILL]" in problem for problem in problems)


def test_sweep_scopes_to_where_claims_live(tmp_path: Path) -> None:
    """Mention is not use: the 73-flag noise came from sweeping code literals.

    Prose files are swept whole-line; code and extensionless files only on
    comment lines; data files not at all. And the citation must share the
    claim's line — an unrelated `$ echo` two lines below once suppressed a
    finding, so that exact shape is pinned as still-flagged.
    """
    root = _throwaway_repo(tmp_path)
    (root / "fixture_test.py").write_text(
        'CLAIM = "the gate is always enforced here"\n'
        "# this comment is guaranteed uncited prose\n",
        encoding="utf-8",
    )
    (root / "probe-tool").write_text(
        "#!/bin/bash\n# this wrapper always launches the reader\necho run\n",
        encoding="utf-8",
    )
    (root / "ledger.jsonl").write_text(
        '{"status": "MEASURED", "note": "always"}\n', encoding="utf-8"
    )
    (root / "notes.md").write_text(
        "plain start\n"
        "the claim here is never checked\n"
        "\n"
        "$ echo unrelated evidence two lines away\n",
        encoding="utf-8",
    )
    environment = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True, env=environment)
    subprocess.run(["git", "commit", "-q", "-m", "claims"], cwd=root, check=True, capture_output=True, env=environment)

    findings = claim_check.sweep_range(root, "HEAD~1", "HEAD")
    joined = "\n".join(findings)

    assert "always enforced here" not in joined, "string literal is mention, not use"
    assert "ledger.jsonl" not in joined, "data files carry no claims"
    assert any("fixture_test.py" in f and "guaranteed" in f for f in findings)
    assert any("probe-tool" in f and "always" in f for f in findings)
    assert any("never checked" in f for f in findings), "same-line rule: distant $ echo suppresses nothing"


def test_record_accepts_the_flag_form(tmp_path: Path, monkeypatch, capsys) -> None:
    """The stdin-JSON form was clunky enough to skip under pressure.

    Pressure is when recording matters, so the flag form exists; it must build
    the same entry the JSON form does, blank cells included.
    """
    ledger = tmp_path / "ledger.jsonl"
    code = claim_check.main(
        [
            "record", "--ledger", str(ledger),
            "--claim", "the gate is enforced on every launch",
            "--premise", "invoked-on-path", "MEASURED", "$ grep -n caller → main:12",
            "--kill", "deleted the call site; test failed",
        ]
    )

    assert code == 0
    entry = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    statuses = {row["key"]: row["status"] for row in entry["premises"]}
    assert statuses["invoked-on-path"] == "MEASURED"
    assert statuses["mechanism-correct"] == "ASSUMED"
    assert "ASSUMED" in capsys.readouterr().out


# --- round-3 controls, from the second operator FAIL -----------------------------

def test_every_trigger_alternative_carries_an_exclusive_witness() -> None:
    """Coverage derived from the grammar's own table, not remembered beside it.

    Round two measured 37 of 46 hand-listed trigger alternatives deletable with
    every test green — each shape was reachable through a synonym, so no single
    deletion moved any assertion. Alternatives now carry their witness in the
    source table, and this test holds both directions for every one of them:
    the witness classifies to its shape, and removing exactly its alternative
    stops it classifying. An alternative that cannot satisfy this cannot exist,
    which is the rule that deleted bare `means`, `no-op`, and the redundant
    costs/spends-nothing forms.
    """
    import re as _re

    for shape in claim_check.SHAPES:
        assert shape.alternatives, shape.name
        for fragment, witness in shape.alternatives:
            assert shape.name in claim_check.classify(witness), (shape.name, witness)
            others = [f for f, _ in shape.alternatives if f is not fragment]
            reduced = _re.compile("|".join(others) or r"(?!x)x", _re.IGNORECASE)
            assert not reduced.search(witness), (
                shape.name, fragment, witness,
                "witness is reachable without its alternative, so deleting the "
                "alternative would survive",
            )


def test_probe_argv_skips_the_lanes_user_config(monkeypatch, tmp_path: Path) -> None:
    """The lane's own config carried repository paths; the probe must not load it.

    Round two showed HOME and the resolved binary remain pointers, and the
    inherited user config pointed straight at this repository's projects and
    hooks. The flag that skips it is part of the launch contract, so it is
    pinned beside the cwd/env boundary.
    """
    seen: dict = {}

    def recorder(argv, **kwargs):
        seen["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(claim_check.subprocess, "run", recorder)
    monkeypatch.setattr(claim_check.shutil, "which", lambda _name: "/probe/bin/codex")

    assert claim_check._run_probe("the gate is enforced on every launch", 5) == 0
    assert "--ignore-user-config" in seen["argv"]


def test_sweep_ignores_hash_inside_python_strings_and_reads_toml_prose(
    tmp_path: Path,
) -> None:
    """The two scope defects round two measured, pinned in both directions.

    A `#` inside a Python string was treated as a comment start, reintroducing
    the literal noise the scoping exists to remove; and TOML was binned as data
    while this repository's agent TOMLs carry claim-bearing instructions.
    """
    root = _throwaway_repo(tmp_path)
    (root / "module.py").write_text(
        'MESSAGE = "always include a # marker in output"\n'
        "# a full-line comment that is never cited\n",
        encoding="utf-8",
    )
    (root / "agent.toml").write_text(
        'instructions = "this agent always verifies the range"\n', encoding="utf-8"
    )
    environment = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True, env=environment)
    subprocess.run(["git", "commit", "-q", "-m", "claims"], cwd=root, check=True, capture_output=True, env=environment)

    findings = claim_check.sweep_range(root, "HEAD~1", "HEAD")
    joined = "\n".join(findings)

    assert "always include a #" not in joined, "a # inside a string is not a comment"
    assert any("module.py" in f and "never" in f for f in findings)
    assert any("agent.toml" in f and "always" in f for f in findings)


# The independent anchor for the grammar's alternative set. Witnesses moved into
# the source table so coverage is derived — which made deleting a
# (fragment, witness) pair silent again, since the witness vanishes with the
# alternative it was pinning. This copy is the anchor the source cannot take
# with it: an alternative deleted or added in scripts/claim_check.py without a
# matching, deliberate edit here is a red test, not a quiet narrowing. That is
# the same two-file-change rule the nine-failure fixture already applies to
# premises.
EXPECTED_ALTERNATIVES = {
    'enforced': (
        '\\bblocks\\b',
        '\\bden(?:y|ies)\\b',
        '\\benforc\\w+\\b',
        '\\bevery (launch|call|run|dispatch|path)\\b',
        '\\bgate[sd]?\\b',
        '\\bprevents?\\b',
        '\\brefus\\w+\\b',
        '\\brejects?\\b',
        '\\brequir\\w+ on\\b',
    ),
    'measured': (
        '\\bconfirm\\w+\\b',
        '\\bgreen\\b',
        '\\bmeasur\\w+\\b',
        '\\bnon-vacuous\\b',
        '\\bpass(?:es|ed)\\b',
        '\\bproves?\\b',
        '\\btest(?:ed|s)?\\b',
        '\\bverif\\w+\\b',
    ),
    'reference': (
        '@[0-9a-f]{7,40}\\b',
        '\\banchors?\\b',
        '\\bcite[sd]?\\b',
        '\\bfinding ref\\b',
        '\\bprovenance\\b',
        '\\bsha256:',
    ),
    'complete': (
        '\\ball (?:cases|forms|paths)\\b',
        '\\bcomplete(?:ly)?\\b(?!\\s+the\\b)',
        '\\bcovers? (?:all|every)\\b',
        '\\bexhaustive\\w*\\b',
        '\\bno other\\b',
        '\\bonly way\\b',
    ),
    'absence': (
        '\\bcannot\\b',
        '\\bfor free\\b',
        '\\bimpossible\\b',
        '\\bnever\\b',
        '\\bno \\w+ (?:exists|calls|reaches|remains)\\b',
        '\\bnothing\\b',
    ),
    'semantics': (
        '\\baccepts?\\b',
        '\\bconsumes?\\b',
        '\\bdefines?\\b',
        '\\binterprets?\\b',
        '\\bparses?\\b',
        '\\bresolves? to\\b',
        '\\btreats?\\b',
    ),
}


def test_the_alternative_table_matches_the_independent_anchor() -> None:
    actual = {
        shape.name: tuple(sorted(fragment for fragment, _ in shape.alternatives))
        for shape in claim_check.SHAPES
    }
    assert actual == EXPECTED_ALTERNATIVES
