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
    last = str(spec.scratch / "codex-last-message.txt")
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
        model = payload.get("model")
        if model is None and isinstance(payload.get("modelUsage"), dict):
            model = next(iter(payload["modelUsage"]), None)
        cost = payload.get("total_cost_usd")
        return model, (float(cost) if isinstance(cost, (int, float)) else None), str(payload.get("result", "")), notes
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
            found = _find_key(event, "model")
            if isinstance(found, str) and model is None:
                model = found
        if model is None:
            notes.append("no codex event carried a model field; model unreported")
        return model, None, result, notes
    notes.append("agy receipts are advisory; the wrapper owns its own receipt")
    return None, None, stdout, notes


def _find_key(payload, key: str):
    if isinstance(payload, dict):
        if key in payload and isinstance(payload[key], str):
            return payload[key]
        for value in payload.values():
            found = _find_key(value, key)
            if found is not None:
                return found
    return None
