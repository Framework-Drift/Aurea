"""
test_suspension_capacity.py - the shared capacity boundary (Docket M, item 5).

Docket K found an off-by-one in the shared SuspensionSystem.is_at_capacity()
(`>=` -> `>`) survived the whole suite: no test anywhere exercised the
boundary. All three suspension organs inherit this predicate - CSA's
quarantine, the Veiled Thread's fermentation, and the Black Sphere's paradox
orbit. For the Black Sphere the boundary is load-bearing in the hardest sense:
paradoxes are PERMANENT (never purged), so the capacity refusal is the only
thing standing between a bounded orbit and an unbounded one.

Boundary pinned exactly: len == capacity-1 -> False, len == capacity -> True.
The Black Sphere test drives the real organ through its real API at a tiny
capacity (a test parameter the constructor exposes, not a coined constant -
the canon default of 30 is untouched).

DO NOT weaken; red means fix the code.
"""

import pytest

from src.suspension.black_sphere import BlackSphere
from src.suspension.suspension_base import SuspensionEntry, SuspensionSystem, \
    SuspensionType


class _MinimalSuspension(SuspensionSystem):
    """The thinnest concrete subclass able to host entries - tests the SHARED
    base predicate all three organs inherit, with no organ-specific behavior
    in the way."""

    # MIGRATED 2026-08-11 (RULING 84), old signature and construction kept
    # verbatim:
    #     def suspend(self, content, source, pressure, reason=""):
    #         entry = SuspensionEntry(
    #             id=..., content=content, source=source, ...)
    # The double tracks the real base door, which no longer takes `source`.
    def suspend(self, content, pressure, reason=""):
        entry = SuspensionEntry(
            id=f"T-{len(self.entries)}", content=content,
            suspension_type=SuspensionType.CSA, pressure_level=pressure,
            reason=reason)
        self.entries[entry.id] = entry
        return entry

    def retrieve(self, entry_id):
        return self.entries.get(entry_id)

    def check_stability(self):
        return {"stable": True}


def test_capacity_boundary_is_exact():
    """len == capacity-1 is NOT at capacity; len == capacity IS. The off-by-one
    Docket K planted (`>` for `>=`) makes the second assertion fail: a store
    that admits capacity+1 entries has no capacity, only a suggestion."""
    system = _MinimalSuspension(capacity=3)

    # MIGRATED 2026-08-11 (RULING 84): the calls dropped their `"test"` source
    # positional (old form `system.suspend("a", "test", 0.5)`). No assertion
    # moved - the capacity boundary is what this pins.
    system.suspend("a", 0.5)
    system.suspend("b", 0.5)
    assert len(system.entries) == 2
    assert system.is_at_capacity() is False, "capacity-1 entries: room remains"

    system.suspend("c", 0.5)
    assert len(system.entries) == 3
    assert system.is_at_capacity() is True, "capacity entries: FULL, exactly here"


def test_black_sphere_refuses_at_capacity_paradoxes_are_permanent(tmp_path):
    """The organ where the boundary bites hardest, driven through its real
    API: a full Black Sphere REFUSES the next paradox rather than purging an
    old one - orbits are permanent, so refusal is the only bound there is."""
    sphere = BlackSphere(capacity=2,
                         filepath=str(tmp_path / "black_sphere_test.json"))
    # MIGRATED 2026-08-11 (RULING 84): the calls dropped their `"test"` source
    # positional (old form `sphere.suspend("liar paradox", "test",
    # pressure=0.95)`). No assertion moved.
    sphere.suspend("liar paradox", pressure=0.95)
    assert sphere.is_at_capacity() is False, "one below capacity: admits"
    sphere.suspend("godel sentence", pressure=0.95)
    assert sphere.is_at_capacity() is True

    with pytest.raises(Exception):
        sphere.suspend("berry paradox", pressure=0.95)
    assert len(sphere.entries) == 2, "the refused paradox did not land"
