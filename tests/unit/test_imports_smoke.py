def test_live_runtime_modules_import_cleanly() -> None:
    import check_coordination  # noqa: F401
    import ci_admission_gate  # noqa: F401
    import compact_pair_loop  # noqa: F401
    import harness_preflight  # noqa: F401
    import mailbox_writer  # noqa: F401
    import protocol_mailbox
    import status  # noqa: F401
    import team  # noqa: F401

    assert protocol_mailbox.APP_MEMBERS == ("codex", "claude", "agy")
