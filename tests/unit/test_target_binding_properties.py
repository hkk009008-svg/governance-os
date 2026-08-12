"""Property tests over the ADR-013 multi-target binding resolver (ADR-018 coverage).

Total-function invariant: ``load_config`` / ``resolve_target`` /
``forbidden_roots`` / ``list_targets`` always either return well-formed output
(a ``TargetBinding`` / tuple of ``TargetBinding`` / tuple of ``Path``) or raise
the typed ``target_binding.BindingError`` — never any other exception, never an
uncaught crash — for ANY generated ``governance.toml`` content.

A Slice-6 hardening fix rides with these tests. ``_resolve_path`` previously let
a raw ``ValueError`` ('embedded null character', from a ``\\u0000`` in a TOML
basic string) or ``RuntimeError`` ('Could not determine home directory', from a
``~<unknown-user>`` path) escape ``resolve_target`` / ``forbidden_roots`` /
``list_targets`` uncaught — a total-function violation on typed-but-hostile
input. It now fails closed as ``BindingError``. The ``test_wrap_*`` regression
pins below fail against the pre-fix module and pass against the fixed one.

Non-vacuousness: the generated configs reach BOTH the success path and the
BindingError path (proved via ``event()`` tags under ``--hypothesis-show-statistics``),
and the positive control resolves to a real ``TargetBinding``.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import HealthCheck, event, given, settings, strategies as st

import target_binding

settings.register_profile(
    "ci",
    settings(
        derandomize=True,
        max_examples=200,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow,
                               HealthCheck.function_scoped_fixture],
    ),
)
settings.load_profile("ci")


# --- value strategies -------------------------------------------------------
# Tokens that repr() to clean TOML and keep a target VALID (reach the success
# path). ASCII-only, no quotes/backslash, so repr() never needs escaping.
_benign = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_.-",
    min_size=1, max_size=8,
)
# Broad fuzz: a value may be empty, contain control chars, or (through repr)
# render TOML that tomllib rejects — every such case must fail closed.
_fuzz = st.text(max_size=8)
_scalar = st.one_of(st.text(max_size=10), st.integers(), st.booleans())
_name = st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=6)
# Adversarial RAW TOML basic-string fragments that PARSE to a well-typed string
# but stress path resolution: a real null byte (basic-string U+0000 escape) and
# an unknown-user tilde prefix. These force _resolve_path down its wrap path;
# repr()-quoted strings can never reach them (repr neutralises control chars into
# literal escape text inside single-quoted TOML).
_adversarial_path = st.sampled_from(['"\\u0000"', '"a\\u0000b"', '"~nobodyxyz9/x"'])


def _p(draw, pct: int) -> bool:
    """Draw True with probability pct%, biasing the mix toward both paths."""
    return draw(st.integers(min_value=0, max_value=99)) < pct


@st.composite
def _config_text(draw) -> str:
    """Build a governance.toml body from fuzzed components — sometimes fully
    valid, sometimes missing default_target, sometimes a target missing a
    required key / carrying an unknown key / invalid route_keywords, sometimes a
    dangling default, sometimes hostile paths, sometimes junk."""
    parts: list[str] = []
    # Few targets keeps the all-targets-valid probability high enough that the
    # success path is exercised often (load_config validates EVERY target).
    names = draw(st.lists(_name, max_size=2, unique=True))

    # [binding].default_target — usually one of the declared targets (so a valid
    # config can resolve), sometimes dangling (unknown-default -> BindingError).
    if _p(draw, 88):
        if names and _p(draw, 85):
            default = draw(st.sampled_from(names))
        else:
            default = draw(_name)
        parts.append(f"[binding]\ndefault_target = {default!r}")

    for n in names:
        lines = [f"[targets.{n}]"]
        if _p(draw, 92):
            lines.append(f"repository = {(draw(_benign) if _p(draw, 85) else draw(_fuzz))!r}")
        if _p(draw, 92):
            if _p(draw, 12):
                lines.append(f"path = {draw(_adversarial_path)}")  # raw TOML fragment
            else:
                lines.append(f"path = {(draw(_benign) if _p(draw, 80) else draw(_fuzz))!r}")
        if _p(draw, 35):
            if _p(draw, 80):
                lines.append(f"route_keywords = {draw(st.lists(_benign, min_size=1, max_size=3))!r}")
            else:  # invalid: empties in the list, or a non-list scalar
                bad = draw(st.one_of(st.lists(st.text(max_size=5), max_size=3), _scalar))
                lines.append(f"route_keywords = {bad!r}")
        if _p(draw, 15):
            lines.append(f"surprise = {draw(_scalar)!r}")  # unknown key -> BindingError
        parts.append("\n".join(lines))

    if _p(draw, 40):
        if _p(draw, 20):
            frag = "[" + draw(_adversarial_path) + "]"  # hostile forbidden root
        elif _p(draw, 60):
            frag = repr(draw(st.lists(_benign, max_size=3)))
        else:  # non-list scalar or list with non-strings
            frag = repr(draw(st.one_of(st.lists(st.text(max_size=6), max_size=3), _scalar)))
        parts.append(f"[paths]\nforbidden_roots = {frag}")

    return "\n\n".join(parts)


def _write(root: Path, text: str) -> Path:
    (root / "governance.toml").write_text(text, encoding="utf-8")
    return root


# --- total-function properties ----------------------------------------------


@given(_config_text())
def test_resolve_target_is_total_returns_binding_or_bindingerror(text):
    with tempfile.TemporaryDirectory() as d:
        root = _write(Path(d), text)
        try:
            binding = target_binding.resolve_target(root, env={})
        except target_binding.BindingError:
            event("resolve_target -> BindingError")
            return  # acceptable typed refusal
        event("resolve_target -> TargetBinding")
        # success path: a well-formed binding (types, not business rules — the
        # module legitimately accepts empty required strings).
        assert isinstance(binding, target_binding.TargetBinding)
        assert isinstance(binding.path, Path)
        assert isinstance(binding.repository, str)
        assert isinstance(binding.name, str) and binding.name
        assert isinstance(binding.route_keywords, tuple) and binding.route_keywords
        assert all(isinstance(k, str) for k in binding.route_keywords)


@given(_config_text())
def test_forbidden_roots_is_total(text):
    with tempfile.TemporaryDirectory() as d:
        root = _write(Path(d), text)
        try:
            roots = target_binding.forbidden_roots(root)
        except target_binding.BindingError:
            event("forbidden_roots -> BindingError")
            return
        event("forbidden_roots -> tuple[Path]")
        assert isinstance(roots, tuple)
        assert all(isinstance(pth, Path) for pth in roots)


@given(_config_text())
def test_list_targets_is_total(text):
    with tempfile.TemporaryDirectory() as d:
        root = _write(Path(d), text)
        try:
            targets = target_binding.list_targets(root)
        except target_binding.BindingError:
            event("list_targets -> BindingError")
            return
        event("list_targets -> tuple[TargetBinding]")
        assert isinstance(targets, tuple)
        assert all(isinstance(t, target_binding.TargetBinding) for t in targets)
        assert all(isinstance(t.path, Path) for t in targets)


# --- non-vacuous positive control + missing config --------------------------


def test_positive_control_valid_config_resolves(tmp_path):
    # NON-VACUOUS control: a hand-built VALID config resolves to a TargetBinding
    # (proves the success branch is actually reachable).
    (tmp_path / "governance.toml").write_text(
        '[binding]\ndefault_target = "demo"\n\n'
        '[targets.demo]\nrepository = "x/demo"\npath = "~/demo"\nroute_keywords = ["demo"]\n',
        encoding="utf-8")
    b = target_binding.resolve_target(tmp_path, env={})
    assert isinstance(b, target_binding.TargetBinding)
    assert b.name == "demo" and b.repository == "x/demo"
    assert b.path == (Path.home() / "demo").resolve()


def test_missing_config_raises_bindingerror(tmp_path):
    with pytest.raises(target_binding.BindingError):
        target_binding.resolve_target(tmp_path / "nonexistent", env={})


# --- wrap regression pins (Slice-6 total-function fix) -----------------------
# Each config is otherwise VALID (load_config passes it) but drives _resolve_path
# to an OS-level failure that, pre-fix, escaped as a raw ValueError / RuntimeError.
# Post-fix each must fail closed as BindingError. These pins fail on the pre-fix
# module, so they are non-vacuous coverage of the wrap.

_WRAP_RESOLVE = [
    pytest.param(
        '[binding]\ndefault_target = "d"\n\n[targets.d]\nrepository = "r"\npath = "\\u0000"\n',
        id="null-byte-path",
    ),
    pytest.param(
        '[binding]\ndefault_target = "d"\n\n[targets.d]\nrepository = "r"\npath = "~nobodyxyz9/x"\n',
        id="unknown-user-tilde-path",
    ),
]


@pytest.mark.parametrize("body", _WRAP_RESOLVE)
def test_wrap_bad_path_fails_closed_in_resolve(tmp_path, body):
    (tmp_path / "governance.toml").write_text(body, encoding="utf-8")
    with pytest.raises(target_binding.BindingError):
        target_binding.resolve_target(tmp_path, env={})


def test_wrap_bad_forbidden_root_fails_closed(tmp_path):
    (tmp_path / "governance.toml").write_text(
        '[binding]\ndefault_target = "d"\n\n[targets.d]\nrepository = "r"\npath = "p"\n\n'
        '[paths]\nforbidden_roots = ["\\u0000"]\n',
        encoding="utf-8")
    with pytest.raises(target_binding.BindingError):
        target_binding.forbidden_roots(tmp_path)


def test_wrap_bad_env_path_override_fails_closed(tmp_path):
    # The GOVERNANCE_TARGET_PATH override is a second _resolve_path call site.
    (tmp_path / "governance.toml").write_text(
        '[binding]\ndefault_target = "d"\n\n[targets.d]\nrepository = "r"\npath = "p"\n',
        encoding="utf-8")
    with pytest.raises(target_binding.BindingError):
        target_binding.resolve_target(tmp_path, env={"GOVERNANCE_TARGET_PATH": "\x00"})
