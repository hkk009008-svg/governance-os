"""Import smoke: every governance module imports cleanly under pytest's
warnings-as-errors config, and the two pythonpath roots (repo root + scripts/)
both resolve by bare name."""
from __future__ import annotations


def test_scripts_modules_import_by_bare_name():
    import protocol_mailbox
    import status  # noqa: F401
    import check_no_ceremony  # noqa: F401
    import bus_unread  # noqa: F401
    import harness_preflight  # noqa: F401
    import compact_pair_loop  # noqa: F401
    import codex_protocol_model  # noqa: F401
    assert set(protocol_mailbox.SEATS) >= {"director", "director2", "operator", "operator2"}
