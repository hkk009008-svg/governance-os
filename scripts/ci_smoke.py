#!/usr/bin/env python3
"""Deprecated alias for scripts/governance_verify_all.py (the full aggregate).

Kept so historical commands, the CI job vocabulary ("ci_smoke" in
threeway/policy.py required_ci), and muscle memory keep resolving. New
invocations should call scripts/governance_verify_all.py; ordinary changes
should run the focused checker that owns the touched boundary instead
(see CHECKER_REGISTRY there).
"""
from __future__ import annotations

from governance_verify_all import main

if __name__ == "__main__":
    raise SystemExit(main())
