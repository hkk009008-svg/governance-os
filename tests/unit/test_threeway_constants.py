"""Unit tests for threeway package-level constants (threeway/__init__.py).

Verifies the event-vocabulary invariants: the schema version, the frozenset
typing of the kind sets, the load-bearing subset relationship, the presence of
authority-fact kinds in the load-bearing set, and the exclusion of bus-carrier
kinds from the load-bearing (gate-verified) set.
"""

import threeway


def test_schema_version_is_exact_string():
    assert threeway.SCHEMA_VERSION == "threeway/1"
    assert isinstance(threeway.SCHEMA_VERSION, str)


def test_kind_sets_are_frozensets():
    assert isinstance(threeway.LOAD_BEARING_KINDS, frozenset)
    assert isinstance(threeway.THREEWAY_KINDS, frozenset)


def test_load_bearing_is_subset_of_threeway_kinds():
    assert threeway.LOAD_BEARING_KINDS <= threeway.THREEWAY_KINDS
    # Proper subset: there are carrier/lifecycle kinds in THREEWAY_KINDS that are
    # deliberately excluded from the load-bearing set.
    assert threeway.LOAD_BEARING_KINDS < threeway.THREEWAY_KINDS


def test_key_authority_facts_present_in_load_bearing():
    expected = {
        "brief",
        "candidate",
        "assignment",
        "attestation",
        "co_sign",
        "re_verify_challenge",
        "approver_roster",
        "ci_result",
        "merge_completed",
    }
    missing = expected - threeway.LOAD_BEARING_KINDS
    assert missing == set(), f"missing load-bearing authority kinds: {missing}"


def test_carrier_kinds_in_threeway_but_not_load_bearing():
    carrier_kinds = {"event_sent", "event_acknowledged", "dead_letter"}
    # Carriers ARE part of the full event vocabulary...
    assert carrier_kinds <= threeway.THREEWAY_KINDS
    # ...but their signatures are NOT gate-load-bearing.
    assert carrier_kinds.isdisjoint(threeway.LOAD_BEARING_KINDS)


def test_all_event_lifecycle_carriers_excluded_from_load_bearing():
    # The full set of event_* lifecycle + dead_letter carriers should all be
    # outside the load-bearing set (they are bus transport, not authority facts).
    lifecycle_carriers = {
        "event_sent",
        "event_acknowledged",
        "event_rejected",
        "event_timed_out",
        "event_retried",
        "dead_letter",
    }
    assert lifecycle_carriers <= threeway.THREEWAY_KINDS
    assert lifecycle_carriers.isdisjoint(threeway.LOAD_BEARING_KINDS)


def test_difference_is_exactly_the_carrier_kinds():
    # The only kinds in THREEWAY_KINDS but not LOAD_BEARING_KINDS are the
    # event_* lifecycle carriers plus dead_letter. No surprise overlap or gap.
    diff = threeway.THREEWAY_KINDS - threeway.LOAD_BEARING_KINDS
    assert diff == {
        "event_sent",
        "event_acknowledged",
        "event_rejected",
        "event_timed_out",
        "event_retried",
        "dead_letter",
    }


def test_load_bearing_kinds_are_nonempty_and_all_strings():
    assert len(threeway.LOAD_BEARING_KINDS) > 0
    assert all(isinstance(k, str) for k in threeway.LOAD_BEARING_KINDS)
    assert all(isinstance(k, str) for k in threeway.THREEWAY_KINDS)


def test_merge_completed_is_load_bearing_and_in_vocabulary():
    # merge_completed is gate-emitted for idempotency and must be verified.
    assert "merge_completed" in threeway.LOAD_BEARING_KINDS
    assert "merge_completed" in threeway.THREEWAY_KINDS
