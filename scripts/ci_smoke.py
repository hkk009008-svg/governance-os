#!/usr/bin/env python3
"""Deprecated alias for scripts/governance_verify_all.py (the full aggregate).

Kept so historical commands, the CI job vocabulary ("ci_smoke" in
threeway/policy.py required_ci), and muscle memory keep resolving. New
invocations should call scripts/governance_verify_all.py; ordinary changes
should run the focused checker that owns the touched boundary instead
(see CHECKER_REGISTRY there).
"""
from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _path in (_REPO_ROOT, _SCRIPTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

if __package__:
    from scripts.governance_verify_all import main  # noqa: E402,F401
else:
    from governance_verify_all import main  # noqa: E402,F401

if __name__ == "__main__":
    raise SystemExit(main())
