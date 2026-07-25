"""
test_gsr_queue_exemption.py - GSR is NEVER queued (Docket M, item 5).

Docket K found that deleting "GSR" from racm's NEVER_QUEUED frozenset survived
the whole suite - the queue-exemption policy (2b Overflow & Deferral, policy 6)
existed only as data with no behavioral witness. Why it matters: GSR is the
all-domain failsafe. A failsafe sitting in a deferral queue is a failsafe that
fires five cycles after the emergency, against conditions that no longer exist
- and Ruling 9 makes queued winners execute against their ORIGINAL trigger, so
a queued GSR would eventually fire a stale global suspension into a healthy
system. GSR preempts or it is suppressed THIS cycle; it never waits.

The scenario is real arbitration, no mocks: a failed-Nova-lineage-boosted ICA
(canon modifier +2 -> effective rank 0) legitimately outranks GSR (rank 1).
The losing GSR must be SUPPRESSED - legible, this-cycle - and must NOT enter
the deferral queue, while an ordinary losing reflex in the same cycle DOES
defer (the contrast that proves the exemption is GSR's, not everyone's).

DO NOT weaken; red means fix the code.
"""

from src.reflex.racm import RACM, NEVER_QUEUED, ReflexClaim, Scope, Verdict


def _claims():
    return [
        ReflexClaim(reflex_id="ICA", pressure_level=0.9, scope=Scope.LOCAL,
                    affected_systems=frozenset({"output", "doctrine", "suspension"}),
                    failed_nova_lineage=True),   # canon +2 -> effective rank 0
        ReflexClaim(reflex_id="GSR", pressure_level=0.9, scope=Scope.GLOBAL,
                    affected_systems=frozenset({"all"})),
        ReflexClaim(reflex_id="ANCHOR_COLLAPSE", pressure_level=0.9,
                    scope=Scope.LOCAL,
                    affected_systems=frozenset({"output", "compass"})),
    ]


def test_gsr_is_registered_queue_exempt():
    """The policy datum itself (2b policy 6): GSR preempts; RLB throttles the
    queue. Removing either from this set is a ruling, not an edit."""
    assert "GSR" in NEVER_QUEUED
    assert "RLB" in NEVER_QUEUED


def test_losing_gsr_is_suppressed_this_cycle_never_deferred():
    """When GSR legitimately loses arbitration it is SUPPRESSED - a legible,
    this-cycle verdict - and never enters the deferral queue."""
    racm = RACM()
    result = racm.arbitrate(_claims())

    assert result.verdict_for("ICA") is Verdict.EXECUTE, "the boosted claim won"
    assert result.verdict_for("GSR") is Verdict.SUPPRESSED, (
        "a losing GSR must be suppressed THIS cycle - a queued failsafe is a "
        "stale global suspension waiting to fire")
    assert racm.is_deferred("GSR") is False
    assert "GSR" not in racm.deferred


def test_ordinary_losing_reflex_defers_in_the_same_cycle():
    """The contrast that makes the exemption visible: ANCHOR_COLLAPSE, losing
    the very same cycle, DOES enter the queue. The queue works; GSR is exempt
    from it - not the other way around."""
    racm = RACM()
    result = racm.arbitrate(_claims())

    assert result.verdict_for("ANCHOR_COLLAPSE") is Verdict.DEFERRED
    assert racm.is_deferred("ANCHOR_COLLAPSE") is True
    assert racm.deferred == ["ANCHOR_COLLAPSE"], (
        "exactly one reflex queued - and it is not GSR")
