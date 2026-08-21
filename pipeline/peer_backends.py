#!/usr/bin/env python3
"""What each peer CLI looks like from the outside: argv in, facts out.

`claude` and `codex` are symmetric enough to share one interface -- both take
a prompt on stdin, a working root, a model, and a containment mode, and both
emit machine-readable output. This module holds the two places they are NOT
symmetric (flag spelling and result shape) so pipeline/peer.py can stay one
runner with one receipt format. AGY is a third backend here and nothing more:
it dispatches to the parent-owned wrapper, which owns the shared lane lock.

Output parsing is deliberately defensive. A model the peer did not report is
recorded as null with a note, never inferred from what the caller asked for --
an inferred model would make the receipt agree with the author by
construction, which is the exact failure the receipt exists to prevent.

"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_S = 900
DEFAULT_MAX_USD = 1.00
AGY_ROLES = ("map", "challenge", "evasion", "debug", "implement", "review")


class PeerError(RuntimeError):
    """The invocation cannot be built or its result cannot be trusted."""


@dataclass(frozen=True)
class Invocation:
    side: str
    argv: list[str]
    advisory: bool = False
    last_message_file: str | None = None


def _binary(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        raise PeerError(f"{name} is not on PATH; a peer that cannot run is not a peer")
    return resolved


def build_claude(spec) -> Invocation:
    argv = [
        _binary("claude"),
        "--print",
        "--output-format", "json",
        "--permission-mode", "plan" if spec.read_only else "acceptEdits",
        "--add-dir", str(spec.cwd),
        "--max-budget-usd", f"{spec.max_usd:.2f}",
    ]
    if spec.model:
        argv += ["--model", spec.model]
    return Invocation("claude", argv)


def build_codex(spec) -> Invocation:
    # A FIXED path let a run that produced nothing read the PREVIOUS run's
    # text, print it, and hash it into a fresh receipt with no warning --
    # forged evidence assembled by the mechanism that exists to prevent it.
    # The name is unique per invocation and peer.run() refuses to read a file
    # this child did not create.
    last = str(spec.scratch / f"codex-last-message-{spec.invocation_id}.txt")
    argv = [
        _binary("codex"), "exec",
        "--json",
        "--sandbox", "read-only" if spec.read_only else "workspace-write",
        "--cd", str(spec.cwd),
        "--output-last-message", last,
        "--skip-git-repo-check",
    ]
    if spec.model:
        argv += ["--model", spec.model]
    argv.append("-")
    return Invocation("codex", argv, last_message_file=last)


def build_agy(spec) -> Invocation:
    """Dispatch to the parent-owned wrapper for the side we are running on.

    The two wrappers take identical arguments and share one desktop-user lock,
    so which one runs decides receipt location and agent naming, not policy.
    """

    if spec.role not in AGY_ROLES:
        raise PeerError(f"agy role must be one of {', '.join(AGY_ROLES)}; got {spec.role!r}")
    # The wrapper has no read-only flag and no spend ceiling of its own, so
    # --write and --max-usd cannot be honoured here. Silently accepting them
    # was the defect: a caller believed a containment they did not have. The
    # only writing role is `implement`, and it must be asked for explicitly.
    if spec.read_only and spec.role == "implement":
        raise PeerError(
            "agy role 'implement' writes files; pass --write to ask for that "
            "explicitly. The other agy roles are advisory and read-only."
        )
    if not spec.read_only and spec.role != "implement":
        raise PeerError(
            f"--write has no meaning for agy role {spec.role!r}: the wrapper "
            "runs advisory roles in plan mode and takes no write flag"
        )
    preferred = os.environ.get("PIPELINE_SIDE", "claude")
    order = ["claude-agy", "codex-agy"] if preferred == "claude" else ["codex-agy", "claude-agy"]
    wrapper = next((name for name in order if shutil.which(name)), None)
    if wrapper is None:
        raise PeerError("neither claude-agy nor codex-agy is on PATH")
    argv = [
        _binary(wrapper), spec.role,
        "--cwd", str(spec.cwd),
        "--prompt-file", "-",
    ]
    if spec.model:
        argv += ["--model", spec.model]
    return Invocation("agy", argv, advisory=True)


BACKENDS = {"claude": build_claude, "codex": build_codex, "agy": build_agy}


@dataclass(frozen=True)
class Spec:
    side: str
    role: str
    task: str
    cwd: Path
    scratch: Path
    model: str | None = None
    read_only: bool = True
    max_usd: float = DEFAULT_MAX_USD
    timeout_s: int = DEFAULT_TIMEOUT_S
    # Distinguishes this invocation's scratch artifacts from every other's.
    invocation_id: str = "0"


def build(spec: Spec) -> Invocation:
    try:
        builder = BACKENDS[spec.side]
    except KeyError:
        raise PeerError(f"unknown peer side {spec.side!r}; expected one of {', '.join(BACKENDS)}")
    return builder(spec)


def reported_result(side: str, stdout: str) -> tuple[str | None, float | None, str, list[str]]:
    """Read what the peer's OWN output says it was. Absence is recorded, not guessed."""

    notes: list[str] = []
    if side == "claude":
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            notes.append("claude output was not one JSON object; model unreported")
            return None, None, stdout, notes
        if not isinstance(payload, dict):
            # Valid JSON that is not an object (a bare list, string or number).
            # Raising here aborted run(), losing a paid result and writing no
            # receipt at all.
            notes.append("claude output was JSON but not an object; model unreported")
            return None, None, stdout, notes

        model = payload.get("model")
        if not (isinstance(model, str) and model.strip()):
            model = None
        usage = payload.get("modelUsage")
        if model is None and isinstance(usage, dict) and usage:
            if len(usage) == 1:
                only = next(iter(usage))
                model = only if isinstance(only, str) and only.strip() else None
            else:
                # More than one model did work. Naming the first key would put
                # a model in the receipt that may not have done the reviewing,
                # which is the receipt asserting a fact it does not have.
                notes.append(
                    "claude reported multiple models "
                    f"({', '.join(sorted(str(key) for key in usage))}); model unreported"
                )
        if model is None:
            notes.append("claude output carried no usable model field; model unreported")

        raw_result = payload.get("result")
        if isinstance(raw_result, str):
            result = raw_result
        else:
            # str(None) is the four characters "None", which was being printed
            # to the operator as the peer's answer and hashed into the receipt.
            result = ""
            if raw_result is not None:
                notes.append(f"claude result field was {type(raw_result).__name__}, not a string")

        cost = payload.get("total_cost_usd")
        return (
            model,
            float(cost) if isinstance(cost, (int, float)) and not isinstance(cost, bool) else None,
            result,
            notes,
        )
    if side == "codex":
        model, result = None, ""
        for line in stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            found = _event_model(event)
            if found is not None and model is None:
                model = found
        if model is None:
            notes.append("no codex event carried a model field; model unreported")
        return model, None, result, notes
    notes.append("agy receipts are advisory; the wrapper owns its own receipt")
    return None, None, stdout, notes


# Exactly where a codex event is allowed to state its model. An unrestricted
# recursive search read "model" from ANY nesting depth, so an unrelated tool
# argument that happened to echo the requested model back made the receipt
# agree with its author -- the one thing a receipt must never do by
# construction. Widen this tuple only with a real observed event shape.
_MODEL_PATHS: tuple[tuple[str, ...], ...] = (
    ("model",),
    ("session", "model"),
    ("turn", "model"),
    ("msg", "model"),
    ("payload", "model"),
)


def _event_model(event) -> str | None:
    """The model an event STATES about itself, at a declared position only."""

    if not isinstance(event, dict):
        return None
    for path in _MODEL_PATHS:
        cursor = event
        for step in path:
            if not isinstance(cursor, dict) or step not in cursor:
                cursor = None
                break
            cursor = cursor[step]
        if isinstance(cursor, str) and cursor.strip():
            return cursor
    return None
