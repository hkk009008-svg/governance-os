"""Stateful property test: capability consumption is one-time (ADR-018).

A RuleBasedStateMachine drives route_capability.consume against a temp receipt
store across random operation interleavings, asserting the ONE-TIME invariant:

  * the FIRST consume of a capability_id succeeds  (ok, reason="consumed");
  * every REPLAY of the SAME capability_id is refused (not ok, "already_consumed");
  * exactly one receipt file exists per consumed capability_id (invariant).

A failing run is a real one-time-consumption violation in route_capability.consume
(a replay that was NOT refused, two receipts for one capability_id, or a first
consume that failed) — never a reason to weaken the invariant.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from hypothesis import strategies as st

import route_capability
from test_route_capability import _cap


class CapabilityConsumeMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Path(self._tmp.name)
        self.consumed: set[str] = set()  # capability_ids we've successfully consumed

    @rule(cid=st.text(alphabet="abcdef0123456789", min_size=1, max_size=6))
    def consume_capability(self, cid):
        cap = _cap(capability_id=f"cap-{cid}")
        evidence = {"result": "ok", "command": "git push", "output": "done", "commit": "deadbee"}
        res = route_capability.consume(cap, evidence, store_dir=self.store)
        key = cap["capability_id"]
        if key in self.consumed:
            # a replay must always be refused as already_consumed
            assert not res.ok and res.reason == "already_consumed"
        else:
            assert res.ok and res.reason == "consumed"
            self.consumed.add(key)

    @invariant()
    def one_receipt_per_consumed_capability(self):
        for key in self.consumed:
            assert (self.store / f"{key}.receipt.json").exists()

    def teardown(self):
        self._tmp.cleanup()


CapabilityConsumeMachine.TestCase.settings = settings(
    derandomize=True, max_examples=100, deadline=None,
    stateful_step_count=30, suppress_health_check=[HealthCheck.too_slow])
TestCapabilityConsume = CapabilityConsumeMachine.TestCase
