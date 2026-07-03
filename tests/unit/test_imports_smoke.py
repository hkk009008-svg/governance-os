"""Import smoke: every governance package/module imports cleanly under pytest's
warnings-as-errors config, and the two pythonpath roots (repo root + scripts/)
both resolve by bare name."""
from __future__ import annotations


def test_threeway_package_imports():
    import threeway
    from threeway import canon, envelope, keys, reducer, gate, policy, tier  # noqa: F401
    assert threeway.SCHEMA_VERSION == "threeway/1"
    assert threeway.LOAD_BEARING_KINDS <= threeway.THREEWAY_KINDS


def test_scripts_modules_import_by_bare_name():
    import protocol_mailbox
    import status  # noqa: F401
    import check_no_ceremony  # noqa: F401
    import agy_observer  # noqa: F401
    import sign_ci_result  # noqa: F401
    import run_merge_gate  # noqa: F401
    import bus_unread  # noqa: F401
    import chief_emit  # noqa: F401
    import overseer_emit  # noqa: F401
    import seat_emit  # noqa: F401
    assert set(protocol_mailbox.SEATS) >= {"director", "director2", "operator", "operator2"}
