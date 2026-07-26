"""
test_tcaml.py - TCAML Stage 1 (organ only). Ruling 27.

Every pin here is BEHAVIORAL (Ruling 17): it calls the function and asserts the
bound. No test in this file asserts that a string appears in a source file. Each
one was hand-verified RED by breaking the thing it guards before landing.

The three that matter most, and what breaks them:

  test_ttl_expires_at_exactly_five_cycles
      RED if expiry is checked before the cycle increments (fires one cycle
      late), or if it is deferred behind other housekeeping. This is
      `boundedHoldTight` from tcaml_lock_priority.qnt, as Python.

  test_instability_onset_revokes_a_held_lock
      RED if onset only blocks future requests. This is
      tcaml_lock_naive.qnt's two-step counterexample, as Python.

  test_racm_sees_tcaml_instability
      RED if Status stops being a str-Enum, or if a value drifts from
      `racm.META_UNSTABLE_STATES`. That drift would be SILENT in production:
      RACM would simply stop seeing instability.
"""

from __future__ import annotations

import pytest

from src.reflex.racm import RACM
from src.topology.tcaml import (
    DEFAULT_HEALTH,
    ELEVATED_THRESHOLD,
    RECOVERY_THRESHOLD,
    ROUTINE_THRESHOLD,
    TTL,
    LockReleaseViolation,
    Scope,
    Status,
    TCAML,
    Tier,
    TopologyDelta,
    assess_topology,
    compute_tier,
)


# =====================================================================
# RULE 1 - LOCAL REQUIRES NO CHECK
# =====================================================================

def test_local_request_is_granted_without_touching_any_state():
    """Rule 1: LOCAL needs no lock. Nothing moves, nothing is recorded.

    A LOCAL grant that mutated holder state would make every local reflex
    contend for a seat it does not occupy.
    """
    tcaml = TCAML()
    before = tcaml.lock_state()

    response = tcaml.lock_request("localAction", "LOCAL", "RACM")

    assert response.granted is True
    assert response.scope is Scope.LOCAL
    assert tcaml.lock_state() == before          # nothing moved
    assert tcaml.lock_denials == []
    assert tcaml.holder is None


def test_local_request_ignores_health_and_instability():
    """LOCAL does not consult health or status - there is no check to fail.

    Driven at a state where EVERY GLOBAL condition fails at once: unstable,
    health on the floor, and the lock already held.
    """
    tcaml = TCAML()
    tcaml.lock_request("globalHolder", "GLOBAL", "RACM")
    tcaml.set_health(0)
    tcaml.enter_meta_unstable()

    response = tcaml.lock_request("localAction", "LOCAL", "RACM")

    assert response.granted is True
    assert "Rule 1" in response.reason


# =====================================================================
# RULE 2 - THE GLOBAL GATE
# =====================================================================

def test_global_grant_at_healthy_unheld_sufficient_health():
    tcaml = TCAML()

    response = tcaml.lock_request("mspInstall", "GLOBAL", "MSSL")

    assert response.granted is True
    assert response.action_id == "mspInstall"
    assert tcaml.holder == "mspInstall"
    assert tcaml.holder_module == "MSSL"
    assert tcaml.held_since == tcaml.cycle


def test_global_denied_while_another_holder_holds_it_with_a_legible_reason():
    """Ruling 23's principle: the denial names WHICH condition failed and who
    is holding, and it lands on a durable surface. A bare False would tell the
    loser it lost without telling anyone why."""
    tcaml = TCAML()
    tcaml.lock_request("mspInstall", "GLOBAL", "MSSL")

    response = tcaml.lock_request("doctrineRemap", "GLOBAL", "SAE")

    assert response.granted is False
    assert "mspInstall" in response.reason
    assert "MSSL" in response.reason
    assert tcaml.holder == "mspInstall"          # the incumbent is untouched
    assert len(tcaml.lock_denials) == 1
    assert tcaml.lock_denials[0]["action_id"] == "doctrineRemap"
    assert tcaml.lock_denials[0]["holder"] == "mspInstall"


@pytest.mark.parametrize("enter", ["enter_meta_unstable", "enter_repair_cycle"])
def test_global_denied_when_status_is_not_healthy(enter):
    """Rule 3's blocking half. Both unstable statuses lock GLOBAL out."""
    tcaml = TCAML()
    getattr(tcaml, enter)()

    response = tcaml.lock_request("doctrineRemap", "GLOBAL", "SAE")

    assert response.granted is False
    assert "Rule 3" in response.reason
    assert tcaml.holder is None


def test_denial_is_falsey_and_grant_is_truthy():
    """`LockResponse.__bool__` returns `granted`.

    `RACM._request_lock()` already reads its lock answer with `if not grant:`.
    A dataclass instance is always truthy, so without `__bool__` RACM would
    read every denial as a grant the moment Stage 2 wires this in. That is a
    fail-OPEN on the system-wide integrity lock.
    """
    tcaml = TCAML()
    assert bool(tcaml.lock_request("first", "GLOBAL", "MSSL")) is True
    assert bool(tcaml.lock_request("second", "GLOBAL", "SAE")) is False


def test_the_answer_is_to_this_call_never_a_cached_one():
    """Rule 2: synchronous, decided against live state, never memoized.

    The same (action, scope, module) triple gets a grant and then a denial as
    live state changes underneath it. A lock granted a moment before
    instability onset is not still valid.
    """
    tcaml = TCAML()
    assert tcaml.lock_request("remap", "GLOBAL", "SAE").granted is True
    tcaml.release("remap", "SAE")
    tcaml.enter_meta_unstable()

    assert tcaml.lock_request("remap", "GLOBAL", "SAE").granted is False


# =====================================================================
# TIER SELECTS A THRESHOLD - IT NEVER DENIES
# =====================================================================

def test_same_request_routine_passes_elevated_denied_at_the_same_health():
    """The tier is not a second verdict path. It is the SAME gate at a
    stricter bar - identical request, identical state, one number moved."""
    health = 50
    assert ROUTINE_THRESHOLD <= health < ELEVATED_THRESHOLD

    routine = TCAML(health=health)
    passed = routine.lock_request("remap", "GLOBAL", "SAE", tier=Tier.ROUTINE)
    assert passed.granted is True

    elevated = TCAML(health=health)
    denied = elevated.lock_request("remap", "GLOBAL", "SAE", tier=Tier.ELEVATED)
    assert denied.granted is False
    assert str(ELEVATED_THRESHOLD) in denied.reason
    assert str(health) in denied.reason

    healthier = TCAML(health=80)
    assert healthier.lock_request("remap", "GLOBAL", "SAE",
                                  tier=Tier.ELEVATED).granted is True


def test_a_structural_delta_raises_the_bar_without_denying_anything():
    """Ruling 27: Docket F's measures select a threshold, never a verdict.

    The SAME bridge-severing delta is denied at health 50 and GRANTED at
    health 80. If the measures denied on their own, the second call would fail
    too - and TCAML would have grown a second, unarbitrated authority over
    GLOBAL action.
    """
    delta = _bridge_severing_delta()

    low = TCAML(health=50)
    denied = low.lock_request("remap", "GLOBAL", "SAE", topology_delta=delta)
    assert denied.granted is False
    assert denied.tier is Tier.ELEVATED
    assert any("bridge" in r for r in low.lock_denials[0]["structural_reasons"])

    high = TCAML(health=80)
    granted = high.lock_request("remap", "GLOBAL", "SAE", topology_delta=delta)
    assert granted.granted is True
    assert granted.tier is Tier.ELEVATED


# =====================================================================
# TTL - THE PRIORITY FINDING
# =====================================================================

def test_ttl_expires_at_exactly_five_cycles_not_four_and_not_six():
    """`boundedHoldTight` (tcaml_lock_priority.qnt), as Python.

    THE BOUND IS EXACT, and the exactness is the point. `TTL = 5` alone bounds
    nothing tightly - tcaml_lock.qnt shows the hold DRIFTING +3 when expiry
    competes for scheduling instead of preempting. Two real implementations
    turn this test red:

      * expiry checked BEFORE the cycle increments  -> expires at 6
      * expiry deferred behind other housekeeping   -> expires at 6 or later
      * expiry checked at `> TTL` instead of `>= TTL` -> expires at 6

    and one turns it red the other way (`>=  TTL - 1`) -> expires at 4.
    """
    tcaml = TCAML()
    tcaml.lock_request("orphaned", "GLOBAL", "MSSL")
    assert tcaml.held_since == 0

    for _ in range(TTL - 1):
        tcaml.tick()
    assert tcaml.cycle == TTL - 1
    assert tcaml.holder == "orphaned", "expired EARLY - the bound is not TTL"

    tcaml.tick()
    assert tcaml.cycle == TTL
    assert tcaml.holder is None, "expired LATE - the hold drifted past TTL"

    assert len(tcaml.lock_expiries) == 1
    assert tcaml.lock_expiries[0]["held_cycles"] == TTL
    assert tcaml.lock_expiries[0]["action_id"] == "orphaned"


def test_expiry_is_considered_first_in_the_housekeeping_pass():
    """The SCHEDULING half of Ruling 27's bounded hold.

    tcaml_lock.qnt (expiry as one option among several): +3 slack, an
    empirical bound. tcaml_lock_priority.qnt (expiry preempts): zero slack,
    the exact bound. So the ordering IS the guarantee, and an ordering nothing
    can observe is one nobody can hold the module to - hence `last_tick_trace`.

    RED if any housekeeping step is moved above `ttl_expiry` in `tick()`.

    HONEST LIMIT, REPORTED NOT PAPERED: in Stage 1 the only other housekeeping
    step (`stability_recovery`) can never be DUE at the same time as an
    expiry, because Rule 3's revoke-on-onset makes "lock held" and "status
    unhealthy" disjoint states. So priority is currently unfalsifiable by
    real competition and is pinned by ORDER instead. It becomes load-bearing
    the moment a second concurrent-eligible GLOBAL duty exists.
    """
    tcaml = TCAML()
    tcaml.lock_request("orphaned", "GLOBAL", "MSSL")
    for _ in range(TTL - 1):
        tcaml.tick()

    trace = tcaml.tick()          # the expiring pass

    steps = [entry["step"] for entry in trace]
    assert steps[0] == "ttl_expiry", (
        f"TTL expiry must be considered FIRST; pass ran {steps}"
    )
    assert trace[0]["acted"] is True
    assert steps == list(TCAML.HOUSEKEEPING_ORDER)
    assert len(steps) > 1, "there must be other housekeeping for priority to mean anything"


def test_a_released_lock_never_expires():
    """Expiry is a safety net for an ORPHANED lock, not a timer on every one."""
    tcaml = TCAML()
    tcaml.lock_request("wellBehaved", "GLOBAL", "MSSL")
    tcaml.tick()
    tcaml.release("wellBehaved", "MSSL")

    for _ in range(TTL * 2):
        tcaml.tick()

    assert tcaml.lock_expiries == []


def test_the_seat_reopens_after_a_force_expiry():
    """A force-expiry is not a punishment - it makes the lock a BOUNDED claim.
    The next requester must be able to take the seat."""
    tcaml = TCAML()
    tcaml.lock_request("orphaned", "GLOBAL", "MSSL")
    for _ in range(TTL):
        tcaml.tick()

    assert tcaml.lock_request("nextInLine", "GLOBAL", "SAE").granted is True


# =====================================================================
# RULE 3 - ONSET REVOKES
# =====================================================================

@pytest.mark.parametrize("enter,expected", [
    ("enter_meta_unstable", Status.META_UNSTABLE),
    ("enter_repair_cycle", Status.REPAIR_CYCLE),
])
def test_instability_onset_revokes_a_held_lock(enter, expected):
    """tcaml_lock_naive.qnt's counterexample, as a Python test.

        [State 1] holder: "doctrineRemap", status: Healthy
        [State 2] holder: "doctrineRemap", status: MetaUnstable
        [violation] noGrantDuringInstability

    The weaker reading of Rule 3 - block NEW requests, leave an existing hold
    alone - fails `noGrantDuringInstability` IN TWO STEPS, because the
    dangerous GLOBAL mutation is already running. Blocking the next request
    does not help the one in flight.

    RED the moment `_enter_instability` stops clearing the holder.
    """
    tcaml = TCAML()
    tcaml.lock_request("doctrineRemap", "GLOBAL", "SAE")
    assert tcaml.holder == "doctrineRemap"

    getattr(tcaml, enter)("scar bloom cascade")

    assert tcaml.status is expected
    assert tcaml.holder is None, (
        "noGrantDuringInstability VIOLATED: a GLOBAL lock is held while TCAML "
        "is unstable - tcaml_lock_naive.qnt's two-step counterexample"
    )
    assert tcaml.held_since is None
    assert len(tcaml.lock_revocations) == 1
    assert tcaml.lock_revocations[0]["action_id"] == "doctrineRemap"
    assert tcaml.lock_revocations[0]["reason"] == "scar bloom cascade"


def test_no_lock_is_ever_held_while_unstable_across_a_run():
    """`noGrantDuringInstability` as a live sweep rather than a single case:
    holder is not None IMPLIES status is HEALTHY, checked after every step."""
    tcaml = TCAML()
    script = [
        lambda: tcaml.lock_request("a", "GLOBAL", "MSSL"),
        tcaml.tick,
        tcaml.enter_meta_unstable,
        lambda: tcaml.lock_request("b", "GLOBAL", "SAE"),
        tcaml.tick,
        lambda: tcaml.set_health(RECOVERY_THRESHOLD),
        tcaml.tick,
        lambda: tcaml.lock_request("c", "GLOBAL", "SAE"),
        tcaml.enter_repair_cycle,
        tcaml.tick,
    ]
    for step in script:
        step()
        assert tcaml.holder is None or tcaml.status is Status.HEALTHY


def test_recovery_requires_the_recovery_threshold():
    """Leaving instability is not free. Below the floor she stays unstable."""
    tcaml = TCAML()
    tcaml.enter_meta_unstable()
    tcaml.set_health(RECOVERY_THRESHOLD - 1)

    tcaml.tick()
    assert tcaml.status is Status.META_UNSTABLE

    tcaml.set_health(RECOVERY_THRESHOLD)
    tcaml.tick()
    assert tcaml.status is Status.HEALTHY


def test_racm_sees_tcaml_instability():
    """The str-Enum values are an INTERFACE, not decoration.

    `RACM._meta_unstable()` reads `getattr(self.tcaml, "status", "")` and tests
    membership in `META_UNSTABLE_STATES = {"meta-unstable", "repair_cycle"}`.
    If `Status` stops subclassing `str`, or a value drifts by one character,
    RACM stops seeing instability - SILENTLY, and GLOBAL action stops being
    locked out during exactly the state Rule 3 exists for. Driven through the
    real RACM, not a mock.
    """
    tcaml = TCAML()
    racm = RACM(tcaml=tcaml)

    assert racm._meta_unstable() is False

    tcaml.enter_meta_unstable()
    assert racm._meta_unstable() is True

    tcaml.set_health(100)
    tcaml.tick()
    assert racm._meta_unstable() is False

    tcaml.enter_repair_cycle()
    assert racm._meta_unstable() is True


# =====================================================================
# RELEASE IS A GUARD, NOT A NO-OP
# =====================================================================

def test_release_by_a_non_holder_raises():
    """Ruling 25's discipline. A `return False` here would make three
    different faults - never granted, revoked underneath you, two modules
    disagreeing about ownership - all look like a successful release."""
    tcaml = TCAML()
    tcaml.lock_request("mspInstall", "GLOBAL", "MSSL")

    with pytest.raises(LockReleaseViolation):
        tcaml.release("doctrineRemap", "SAE")

    assert tcaml.holder == "mspInstall", "a refused release must not clear the lock"


def test_release_with_the_right_action_but_the_wrong_module_raises():
    """Two modules disagreeing about who owns a system-wide mutation is
    exactly the fault this guard exists for."""
    tcaml = TCAML()
    tcaml.lock_request("mspInstall", "GLOBAL", "MSSL")

    with pytest.raises(LockReleaseViolation):
        tcaml.release("mspInstall", "SAE")

    assert tcaml.holder == "mspInstall"


def test_release_when_nothing_is_held_raises():
    tcaml = TCAML()
    with pytest.raises(LockReleaseViolation) as excinfo:
        tcaml.release("phantom", "SAE")
    assert "NOBODY" in str(excinfo.value)


def test_a_revoked_holder_releasing_is_told_it_was_revoked():
    """FLAGGED, NOT DECIDED (Ruling 27, open question 1): revoke-on-instability
    interrupts an in-flight GLOBAL operation, so the interrupted operation's
    own orderly release now RAISES. That is the correct visible edge -
    swallowing it would make a revoked operation indistinguishable from a
    completed one - but the guard must at least SAY what happened, or it just
    relocates the mystery."""
    tcaml = TCAML()
    tcaml.lock_request("doctrineRemap", "GLOBAL", "SAE")
    tcaml.enter_meta_unstable()

    with pytest.raises(LockReleaseViolation) as excinfo:
        tcaml.release("doctrineRemap", "SAE")
    assert "REVOKED" in str(excinfo.value)


def test_a_force_expired_holder_releasing_is_told_it_expired():
    tcaml = TCAML()
    tcaml.lock_request("orphaned", "GLOBAL", "MSSL")
    for _ in range(TTL):
        tcaml.tick()

    with pytest.raises(LockReleaseViolation) as excinfo:
        tcaml.release("orphaned", "MSSL")
    assert "FORCE-EXPIRED" in str(excinfo.value)


def test_lock_release_violation_is_in_the_structural_taxonomy():
    """Ruling 25: `STRUCTURAL_VIOLATIONS` is a CLOSED, ENUMERATED tuple and a
    new guard joins it ON PURPOSE. Behavioral - it asserts the live tuple
    object, which is what `process_input`'s enumerated `except` clause uses,
    not a string in a file."""
    from src.aurea_core import STRUCTURAL_VIOLATIONS

    assert LockReleaseViolation in STRUCTURAL_VIOLATIONS
    assert not isinstance(STRUCTURAL_VIOLATIONS, list)


# =====================================================================
# RULING 22 - READS RETURN SNAPSHOTS
# =====================================================================

def test_lock_state_is_a_snapshot():
    """Mutating a read must not move the store. Lock state is the one field
    whose staleness is itself a safety property.

    The FRESH-OBJECT assertion is not ceremony. `LockState` is all scalars, so
    the mutation half of this test is nearly guaranteed by construction - it
    was the only pin in this file that no realistic defect could turn red. The
    defect that CAN happen is someone memoizing `lock_state()`, and a memoized
    snapshot would silently defeat
    `test_local_request_is_granted_without_touching_any_state`, which compares
    two `lock_state()` results with `==` to prove Rule 1 touched nothing. A
    cached object always equals itself. That test would then pass while LOCAL
    quietly mutated the lock.
    """
    tcaml = TCAML()
    tcaml.lock_request("mspInstall", "GLOBAL", "MSSL")

    snapshot = tcaml.lock_state()
    snapshot.holder = "impostor"
    snapshot.status = Status.META_UNSTABLE
    snapshot.health = 0

    assert tcaml.holder == "mspInstall"
    assert tcaml.status is Status.HEALTHY
    assert tcaml.health == DEFAULT_HEALTH

    assert tcaml.lock_state() is not tcaml.lock_state(), (
        "lock_state() must build a fresh snapshot per call - a memoized one "
        "would make the Rule 1 `==` comparison vacuously true"
    )
    assert tcaml.lock_state().holder == "mspInstall"


def test_anchor_reads_return_deep_copies():
    """Ruling 22's shape, applied to the anchor store: a caller could
    otherwise rewrite a reported drift with no owner-controlled operation, and
    the AST single-writer invariant CANNOT see it - nothing assigns to
    `tcaml.anchor_state`."""
    tcaml = TCAML()
    tcaml.anchor_feedback_update("compass", 12.5)

    one = tcaml.get_anchor("compass")
    one.last_reported_drift = 999.0
    one.realignments_requested = 42

    everything = tcaml.get_anchor_state()
    everything["compass"].last_reported_drift = -1.0
    everything["injected"] = one

    live = tcaml.get_anchor("compass")
    assert live.last_reported_drift == 12.5
    assert live.realignments_requested == 0
    assert "injected" not in tcaml.anchor_state


def test_realignment_is_a_recorded_request_with_no_effect():
    """PARKED (Ruling 15's shape). Realignment means moving an orientation
    reference and the corpus gives no magnitude for that move. The request
    accumulates legibly; the anchor's reported drift is untouched."""
    tcaml = TCAML()
    tcaml.anchor_feedback_update("compass", 22.0)
    tcaml.trigger_anchor_realignment("compass")

    assert len(tcaml.realignment_requests) == 1
    assert tcaml.realignment_requests[0]["anchor_id"] == "compass"
    assert "PARKED" in tcaml.realignment_requests[0]["state"]
    assert tcaml.get_anchor("compass").last_reported_drift == 22.0


# =====================================================================
# DOCKET F - COMPUTE_TIER
# =====================================================================

def _bridge_severing_delta() -> TopologyDelta:
    """Two triangles joined by a single edge. `hub->spoke` is the only thing
    holding the two regions together, and `hub`/`spoke` are the cut vertices.

        a - b            d - e
         \\ /              \\ /
         hub ----------- spoke
    """
    return TopologyDelta(
        nodes={"a", "b", "hub", "spoke", "d", "e"},
        edges={
            ("a", "b"), ("b", "hub"), ("hub", "a"),
            ("hub", "spoke"),
            ("spoke", "d"), ("d", "e"), ("e", "spoke"),
        },
        removed_edges={("hub", "spoke")},
        description="sever the only edge joining two constellations",
    )


def test_compute_tier_elevates_a_bridge_severing_delta():
    delta = _bridge_severing_delta()

    assert compute_tier(delta) is Tier.ELEVATED

    assessment = assess_topology(delta)
    assert any("bridge" in reason for reason in assessment.reasons), assessment.reasons


def test_compute_tier_leaves_an_isolated_leaf_addition_routine():
    """Adding a pendant node changes nothing structural. If this elevates,
    every ordinary growth of the constellation pays the strict bar."""
    delta = TopologyDelta(
        nodes={"a", "b", "hub", "spoke", "d", "e"},
        edges={
            ("a", "b"), ("b", "hub"), ("hub", "a"),
            ("hub", "spoke"),
            ("spoke", "d"), ("d", "e"), ("e", "spoke"),
        },
        added_nodes={"leaf"},
        added_edges={("e", "leaf")},
        description="attach one new leaf node",
    )

    assert compute_tier(delta) is Tier.ROUTINE
    assert assess_topology(delta).reasons == [
        "no structural condition met - base threshold applies"
    ]


def test_compute_tier_elevates_removal_of_an_articulation_point():
    delta = _bridge_severing_delta()
    delta.removed_edges = set()
    delta.removed_nodes = {"hub"}

    assessment = assess_topology(delta)
    assert assessment.tier is Tier.ELEVATED
    assert any("articulation point" in r for r in assessment.reasons), assessment.reasons


def test_compute_tier_elevates_a_protected_anchor_kcore_drop():
    """The anchor stays connected - it is just held by fewer mutual
    connections than before. k-core sees that; simple degree would too, but
    only k-core sees that the neighbours' mutual support went with it."""
    delta = TopologyDelta(
        nodes={"anchor", "p", "q", "r"},
        edges={
            ("anchor", "p"), ("p", "anchor"),
            ("anchor", "q"), ("q", "anchor"),
            ("anchor", "r"), ("r", "anchor"),
            ("p", "q"), ("q", "p"), ("q", "r"), ("r", "q"), ("p", "r"), ("r", "p"),
        },
        removed_nodes={"r"},
        protected_anchors={"anchor"},
        description="drop one member of the anchor's mutually-supporting core",
    )

    assessment = assess_topology(delta)
    assert assessment.tier is Tier.ELEVATED
    assert any("k-core" in r for r in assessment.reasons), assessment.reasons


def test_compute_tier_elevates_an_scc_split():
    """A three-node cycle broken open: a region of mutual symbolic
    reinforcement stops being mutually reachable."""
    delta = TopologyDelta(
        nodes={"x", "y", "z", "w"},
        edges={("x", "y"), ("y", "z"), ("z", "x"), ("z", "w"), ("w", "z")},
        removed_edges={("z", "x")},
        description="break a directed cycle",
    )

    assessment = assess_topology(delta)
    assert assessment.tier is Tier.ELEVATED
    assert any("strongly-connected" in r for r in assessment.reasons), assessment.reasons


def test_compute_tier_elevates_a_shortened_scar_to_anchor_path():
    """"Opens a new SHORT path" is stated without a length, and a length is
    what this module must not coin. So the condition is a strict DECREASE in
    the minimum scar->anchor distance - no magnitude required."""
    delta = TopologyDelta(
        nodes={"scar1", "m1", "m2", "anchor"},
        edges={("scar1", "m1"), ("m1", "m2"), ("m2", "anchor")},
        added_edges={("scar1", "anchor")},
        protected_anchors={"anchor"},
        scar_nodes={"scar1"},
        description="carve a direct scar->anchor shortcut",
    )

    assessment = assess_topology(delta)
    assert assessment.tier is Tier.ELEVATED
    assert any("scar->protected-anchor" in r for r in assessment.reasons), \
        assessment.reasons
    assert assessment.measures["min_scar_anchor_before"] == 3
    assert assessment.measures["min_scar_anchor_after"] == 1


def test_a_first_ever_scar_to_anchor_path_counts_as_a_shortening():
    """`inf -> finite` is a decrease. A fracture that could not reach an
    anchor at all and now can is the strongest form of this condition, and an
    implementation comparing raw floats without handling `inf` would miss it
    entirely."""
    delta = TopologyDelta(
        nodes={"scar1", "anchor"},
        edges=set(),
        added_edges={("scar1", "anchor")},
        protected_anchors={"anchor"},
        scar_nodes={"scar1"},
    )

    assessment = assess_topology(delta)
    assert assessment.tier is Tier.ELEVATED
    assert any("none -> 1" in r for r in assessment.reasons), assessment.reasons


def test_no_delta_means_the_base_bar_not_the_strict_one():
    """No structural evidence means no elevation. Defaulting to ELEVATED would
    be inventing pressure no measure found (Nova's G1 failure mode)."""
    assert compute_tier(None) is Tier.ROUTINE

    tcaml = TCAML(health=ROUTINE_THRESHOLD)
    assert tcaml.lock_request("remap", "GLOBAL", "SAE").granted is True


def test_an_explicit_tier_overrides_the_derived_one_and_the_disagreement_is_recorded():
    """A caller may know something the delta does not encode. The derived
    assessment is still recorded on the denial, so the disagreement is
    visible rather than lost."""
    delta = _bridge_severing_delta()
    tcaml = TCAML(health=50)

    response = tcaml.lock_request("remap", "GLOBAL", "SAE",
                                  topology_delta=delta, tier=Tier.ROUTINE)

    assert response.granted is True
    assert response.tier is Tier.ROUTINE

    tcaml.release("remap", "SAE")
    tcaml.set_health(10)
    tcaml.lock_request("remap2", "GLOBAL", "SAE",
                       topology_delta=delta, tier=Tier.ROUTINE)
    assert any("bridge" in r
               for r in tcaml.lock_denials[0]["structural_reasons"])


def test_assessment_reasons_are_a_list_not_a_score():
    """Standing bar 5: no scoring function. Measures combine by boolean OR
    over NAMED conditions, each individually legible. A single number cannot
    say WHICH structure is at risk, and 'which' is the whole content of a
    topological assessment."""
    delta = _bridge_severing_delta()
    delta.removed_nodes = {"hub"}
    delta.protected_anchors = {"spoke"}

    assessment = assess_topology(delta)

    assert isinstance(assessment.reasons, list)
    assert len(assessment.reasons) >= 2, assessment.reasons
    assert all(isinstance(r, str) and r for r in assessment.reasons)
    assert not any(isinstance(v, float) and 0.0 < v < 1.0
                   for v in vars(assessment).values())


# =====================================================================
# HEALTH IS A FIELD, NOT A FORMULA
# =====================================================================

def test_health_defaults_to_full_and_is_clamped_to_the_index_range():
    tcaml = TCAML()
    assert tcaml.health == DEFAULT_HEALTH == 100

    tcaml.set_health(-40)
    assert tcaml.health == 0
    tcaml.set_health(500)
    assert tcaml.health == 100


def test_health_rejects_a_non_finite_value():
    tcaml = TCAML()
    with pytest.raises(ValueError):
        tcaml.set_health(float("nan"))
    with pytest.raises(ValueError):
        tcaml.set_health(float("inf"))


def test_nothing_in_tcaml_moves_health_on_its_own():
    """The Constellation Health Index has NO combination rule in the corpus.
    If a future pass invents one, this goes red - which is the point. The five
    named inputs (anchor drift, scar bloom density, fragmentation, dead-zone
    index, meta-stability) have no ruled way to combine, and a weighted
    average here would be a coined magnitude at the most safety-critical site
    in the organ."""
    tcaml = TCAML(health=60)

    tcaml.lock_request("remap", "GLOBAL", "SAE")
    tcaml.tick()
    tcaml.anchor_feedback_update("compass", 24.9)
    tcaml.trigger_anchor_realignment("compass")
    tcaml.enter_meta_unstable()
    tcaml.tick()
    tcaml.lock_request("blocked", "GLOBAL", "SAE")

    assert tcaml.health == 60
