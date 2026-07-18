"""Unit tests for threeway.tier and threeway.policy (pure tier/policy functions).

Scope: tier_rank ordering, classify_diff (MAX across paths), effective_tier
(gate never trusts a lower claimed tier), default-policy path->tier classification
(expectations derived BY READING _DEFAULT_RULES), policy_digest determinism, and
required_ci per-tier mapping. co_sign_satisfied is intentionally out of scope
(needs EffectiveState).
"""
from __future__ import annotations

import pytest

from threeway import policy, tier
from threeway.policy import Policy, default_policy


# --- tier_rank ordering --------------------------------------------------------

def test_tier_rank_strict_ordering():
    assert tier.tier_rank("T0") < tier.tier_rank("T1") < tier.tier_rank("T2") < tier.tier_rank("T3")
    assert [tier.tier_rank(t) for t in ("T0", "T1", "T2", "T3")] == [0, 1, 2, 3]


def test_tier_rank_unknown_tier_raises_keyerror():
    with pytest.raises(KeyError):
        tier.tier_rank("T9")


# --- classify_diff: MAX tier across changed paths ------------------------------

def test_classify_diff_unmatched_path_defaults_to_t1():
    # No rule prefix matches an arbitrary source path -> default T1 (tier.py:18).
    pol = default_policy()
    assert tier.classify_diff(["threeway/reducer.py"], pol) == "T1"


def test_classify_diff_returns_max_across_paths():
    # docs/ -> T0, an unmatched path -> T1, threeway/gate.py -> T3. Max is T3.
    pol = default_policy()
    paths = ["docs/README.md", "threeway/reducer.py", "threeway/gate.py"]
    assert tier.classify_diff(paths, pol) == "T3"


def test_classify_diff_empty_paths_is_t0():
    # No changed paths -> T0 (tier.py:23-24).
    pol = default_policy()
    assert tier.classify_diff([], pol) == "T0"


def test_classify_diff_rule_order_keys_subdir_beats_coordination_prefix():
    # _DEFAULT_RULES lists "coordination/threeway/keys/" (T3) BEFORE "coordination/"
    # (T2); first match wins, so a key path under coordination resolves T3, not T2.
    pol = default_policy()
    assert tier.classify_diff(["coordination/threeway/keys/agent01.pub"], pol) == "T3"
    # A plain coordination path (not under keys/) still resolves T2.
    assert tier.classify_diff(["coordination/state.jsonl"], pol) == "T2"


# --- effective_tier: gate never trusts a LOWER claimed tier --------------------

def test_effective_tier_classification_overrides_lower_claim():
    # Claim T0 but the diff touches threeway/gate.py (T3) -> effective is T3.
    pol = default_policy()
    assert tier.effective_tier("T0", ["threeway/gate.py"], pol) == "T3"


def test_effective_tier_honors_higher_claim_than_classified():
    # Diff classifies as T0 (docs only) but the brief claimed T2 -> max keeps T2.
    pol = default_policy()
    assert tier.effective_tier("T2", ["docs/x.md"], pol) == "T2"


def test_effective_tier_equal_claim_and_classified():
    pol = default_policy()
    # docs/ classifies T0, claimed T0 -> T0.
    assert tier.effective_tier("T0", ["docs/x.md"], pol) == "T0"


# --- default-policy path->tier classification (derived from _DEFAULT_RULES) -----

def test_default_rules_classify_representative_paths():
    # Expectations read directly from policy._DEFAULT_RULES (policy.py:15-32).
    pol = default_policy()
    expected = {
        "coordination/threeway/keys/agent01.pub": "T3",
        "threeway/keys.py": "T3",
        "threeway/gate.py": "T3",
        ".github/workflows/ci.yml": "T2",
        "scripts/ci_smoke.py": "T2",
        "scripts/wave_gate_check.py": "T2",
        "scripts/check_no_ceremony.py": "T2",
        "requirements-dev.txt": "T2",
        "requirements-governance.txt": "T2",
        "pyproject.toml": "T2",
        "package-lock.json": "T2",
        "threeway/policy.py": "T2",
        "threeway/predicate.py": "T2",
        "coordination/state.jsonl": "T2",
        "docs/PROGRAM-MANUAL.md": "T0",
    }
    for path, want in expected.items():
        assert tier.classify_diff([path], pol) == want, path


def test_exact_prefix_string_match_classifies():
    # tier.py:15 matches "path == prefix" as well as startswith; the bare rule key
    # "requirements-dev.txt" should classify when passed exactly.
    pol = default_policy()
    assert tier.classify_diff(["requirements-dev.txt"], pol) == "T2"


# --- policy_digest determinism + acceptance ------------------------------------

def test_policy_digest_deterministic_for_same_rules():
    a = Policy()
    b = Policy()
    assert a.policy_digest() == b.policy_digest()
    # Stable across repeated calls on the same instance.
    assert a.policy_digest() == a.policy_digest()
    # SHA-256 hex digest shape.
    d = a.policy_digest()
    assert isinstance(d, str)
    assert len(d) == 64
    assert all(c in "0123456789abcdef" for c in d)


def test_policy_digest_changes_when_rules_change():
    base = Policy()
    altered = Policy(rules=base.rules + (("extra/", "T3"),))
    assert altered.policy_digest() != base.policy_digest()


def test_is_accepted_matches_own_digest_and_accepted_set():
    pol = default_policy()
    assert pol.is_accepted(pol.policy_digest()) is True
    assert pol.is_accepted("deadbeef") is False
    # A digest placed in accepted_digests is honored even if it isn't the own digest.
    pol2 = Policy(accepted_digests=frozenset({"feedface"}))
    assert pol2.is_accepted("feedface") is True
    assert pol2.is_accepted(pol2.policy_digest()) is True


# --- required_ci per-tier mapping ----------------------------------------------

def test_required_ci_per_tier_mapping():
    pol = default_policy()
    assert pol.required_ci("T0") == ("ci_smoke",)
    assert pol.required_ci("T1") == ("ci_smoke",)
    assert pol.required_ci("T2") == ("ci_smoke", "wave_gate")
    assert pol.required_ci("T3") == ("ci_smoke", "wave_gate")


def test_required_ci_unknown_tier_raises_keyerror():
    pol = default_policy()
    with pytest.raises(KeyError):
        pol.required_ci("T9")


def test_default_policy_uses_module_default_rules():
    pol = default_policy()
    assert pol.rules is policy._DEFAULT_RULES
