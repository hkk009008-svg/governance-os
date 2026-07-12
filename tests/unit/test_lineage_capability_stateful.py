"""Cross-subsystem stateful test: capability revocation follows route supersession
(ADR-015 lineage x ADR-016 capabilities; executes ADR-018).

A RuleBasedStateMachine grows a route lineage by supersession and issues
capabilities bound to specific (route_id, generation) pairs, then interleaves
consumes. It asserts the CROSS-SUBSYSTEM invariant: a capability is current — and
``consume(authoritative=tip)`` succeeds — ONLY while its ``bound_route_id`` /
``bound_generation`` equal the authoritative lineage tip; a capability bound to a
superseded generation is stale (``capability_is_current`` False; ``consume``
refuses ``stale_capability`` and writes NO new receipt).

NON-CIRCULAR ORACLE: the model's own expectation of currency (``_is_current``) is
re-derived from the raw ``bound_route_id`` / ``bound_generation`` fields — it does
NOT call the system-under-test ``capability_is_current``. So a mutant
``capability_is_current`` (e.g. always-True) fails BOTH the ``currency_matches_tip``
invariant (SUT vs oracle) AND the stale-consume assertion (consume, which uses the
mutated function internally, no longer refuses a stale grant the oracle flags).

A failing run is a real cross-subsystem invariant violation in route_lineage or
route_capability — never a reason to weaken the invariant.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import HealthCheck, event, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

import route_capability
import route_lineage
from test_route_capability import _cap


def _lineage_route(route_id: str, generation: int, parent: str | None) -> route_lineage.LineageRoute:
    return route_lineage.LineageRoute(route_id, route_lineage.RouteLineage(generation, parent, None))


def _evidence():
    # command matches BOTH allowed_command_class "git push" and target "origin/main".
    return {"result": "ok", "command": "git push origin main", "output": "done", "commit": "deadbee"}


def _is_current(cap: dict, tip: route_lineage.LineageRoute) -> bool:
    """Independent oracle: currency re-derived from raw fields, NOT from the SUT.

    Mirrors the ADR-015 x ADR-016 contract without calling
    ``route_capability.capability_is_current`` — so it can adjudicate that
    function (and consume's use of it) rather than tautologically agreeing.
    """
    return (
        cap["bound_route_id"] == tip.route_id
        and cap["bound_generation"] == tip.lineage.generation
    )


class LineageCapabilityMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Path(self._tmp.name)
        # start with a generation-1 tip
        self.routes = [_lineage_route("route-1", 1, None)]
        self.next_gen = 2
        # capabilities: list of full capability dicts (bound gen is in each dict)
        self.caps: list[dict] = []
        # capability_ids that have been successfully consumed (a real receipt exists)
        self.consumed_ids: set[str] = set()

    def _tip(self) -> route_lineage.LineageRoute:
        res = route_lineage.resolve_authoritative(self.routes)
        assert res.mode == "lineage" and res.winner is not None
        return next(r for r in self.routes if r.route_id == res.winner)

    # A single supersession per step keeps the lineage linear (one unambiguous
    # tip). Hypothesis exercises this rule often enough that the lineage reliably
    # grows past generation 1 (~1200 calls/run), making the stale path (a cap
    # bound below the tip) non-vacuous.
    @rule()
    def supersede_route(self):
        tip = self._tip()
        rid = f"route-{self.next_gen}"
        self.routes.append(_lineage_route(rid, self.next_gen, tip.route_id))
        self.next_gen += 1
        event("supersede_route")

    @rule(at_tip=st.booleans())
    def issue_capability(self, at_tip):
        tip = self._tip()
        # Bind either to the current tip (current) or, once the lineage has grown,
        # to the original generation-1 route (immediately stale). Both feed the
        # stale path: an at-tip cap goes stale the next time supersede fires.
        gen = tip.lineage.generation
        rid = tip.route_id
        if not at_tip and self.next_gen > 3:
            gen = 1
            rid = "route-1"
            event("issue_capability@stale_gen1")
        else:
            event("issue_capability@tip")
        cap = _cap(capability_id=f"cap-{len(self.caps)}", bound_route_id=rid, bound_generation=gen)
        self.caps.append(cap)

    @rule(idx=st.integers(min_value=0, max_value=50))
    def consume_random_capability(self, idx):
        if not self.caps:
            event("consume:noop_no_caps")
            return
        cap = self.caps[idx % len(self.caps)]
        cid = cap["capability_id"]
        tip = self._tip()
        # Oracle-decided expectation (independent of the SUT), and the pre-consume
        # receipt state. Compute BOTH before calling consume so the assertions are
        # not contaminated by consume's own write.
        current = _is_current(cap, tip)
        already = cid in self.consumed_ids
        receipt = self.store / f"{cid}.receipt.json"
        receipt_existed = receipt.exists()

        res = route_capability.consume(cap, _evidence(), store_dir=self.store, authoritative=tip)

        if not current:
            # Stale: refused fail-closed. consume's stale check precedes its
            # already_consumed check, so a previously-consumed-then-superseded
            # cap also refuses stale here. NO NEW receipt is written: the receipt
            # exists now iff it already existed (from an earlier current consume).
            assert not res.ok and res.reason.startswith("stale_capability")
            assert receipt.exists() == receipt_existed
            event("consume:stale_refused")
        elif already:
            # Current but already consumed -> replay refusal, receipt unchanged.
            assert not res.ok and res.reason == "already_consumed"
            assert receipt.exists()
            event("consume:already_consumed")
        else:
            # Current, first consume -> success, exactly one receipt now exists.
            assert res.ok and res.reason == "consumed"
            assert receipt.exists()
            self.consumed_ids.add(cid)
            event("consume:fresh_ok")

    @invariant()
    def currency_matches_tip(self):
        tip = self._tip()
        for cap in self.caps:
            expected = _is_current(cap, tip)
            assert route_capability.capability_is_current(cap, tip) == expected

    def teardown(self):
        self._tmp.cleanup()


LineageCapabilityMachine.TestCase.settings = settings(
    derandomize=True, max_examples=100, deadline=None, stateful_step_count=40,
    suppress_health_check=[HealthCheck.too_slow])
TestLineageCapability = LineageCapabilityMachine.TestCase
