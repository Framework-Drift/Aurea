"""
test_tcaml_wiring.py - TCAML Stage 2 (Ruling 27, §8 step 6b).

Stage 1 pinned the ORGAN in isolation. This file pins the WIRE: that the lock
is live in the pipeline, that it is ACQUIRED AND GIVEN BACK, and that the
build-stage escape hatch is gone.

Every pin is behavioral (Ruling 17), and each was hand-verified RED under the
defect it guards before landing.

THE ONE THAT MATTERS MOST
-------------------------
`test_gsr_executes_during_meta_instability_and_structural_change_does_not`
pins Ruling 30's RESOLUTION of the conflict this file used to escalate. It
asserts BOTH halves - GSR runs, structural change still does not - because the
resolution is only correct if Rule 3 survived it. Read its docstring before
changing anything near it.
"""

from __future__ import annotations

import json

import pytest

from src.aurea_core import AureaCore
from src.reflex.racm import RACM, ReasonCode, ReflexClaim, Scope, Verdict
from src.reflex.rb_system import RBSystem
from src.reflex.reflex_grid import (ReflexGrid, ReflexPriority, ReflexTrigger,
                                    SymbolicReflex)
from src.topology.tcaml import LockClass, TCAML, StaleLockRelease, Status


# =====================================================================
# THE SEAM IS CLOSED
# =====================================================================

def test_racm_always_has_a_real_tcaml_there_is_no_absent_state():
    """The build-stage default-grant branch is GONE.

    It was the one place a GLOBAL action escaped the lock model: with TCAML
    absent, GLOBAL scope proceeded ungated and the gap was merely logged. The
    branch could only be DELETED (rather than softened) because there is no
    longer an absent state to special-case - a bare RACM builds its own lock
    owner, exactly as it already builds its own RBSystem.

    RED if anyone reintroduces `if self.tcaml is None: ... return True`.
    """
    bare = RACM(rb_system=RBSystem())
    assert bare.tcaml is not None
    assert isinstance(bare.tcaml, TCAML)


def test_a_global_claim_is_actually_adjudicated_by_tcaml():
    """Not merely present - CONSULTED. A GLOBAL claim is denied when the lock
    is genuinely unavailable, which is only observable if the request really
    reaches TCAML."""
    tcaml = TCAML()
    racm = RACM(rb_system=RBSystem(), tcaml=tcaml)

    # Someone else holds the system-wide lock, and it is not RACM's to sweep.
    tcaml.lock_request("mspInstall", LockClass.STRUCTURAL, "MSSL")

    result = racm.arbitrate([_claim("GSR", 0.9, Scope.GLOBAL, ["all"],
                                lock_class=LockClass.STRUCTURAL)])

    assert result.verdict_for("GSR") is Verdict.LOCK_DENIED
    assert result.execute == []
    assert tcaml.holder == "mspInstall", "an incumbent holder must survive"


def test_aurea_core_shares_one_tcaml_with_every_requester():
    """ONE lock, or it is not a lock. Two instances would each grant happily
    while believing they were the only holder."""
    core = AureaCore()
    assert core.tcaml is core.reflex_grid.racm.tcaml
    assert core.tcaml is core.compass.tcaml


def test_the_pipeline_advances_the_tcaml_cycle():
    """Without a cycle advance the TTL bound could never be crossed and the
    force-expiry safety net would be decorative."""
    core = AureaCore()
    start = core.tcaml.cycle

    core.process_input("Truth is what survives contradiction.")
    core.process_input("And what survives is not therefore true.")

    assert core.tcaml.cycle == start + 2


# =====================================================================
# ACQUIRE / RELEASE - THE LOCK IS GIVEN BACK
# =====================================================================

class _LockProbe(SymbolicReflex):
    """A GLOBAL reflex that records the lock state DURING its own execution."""

    def __init__(self, tcaml, blow_up: bool = False):
        # Ruling 30: STRUCTURAL is what puts a claim on the lock path. The
        # GLOBAL `scope` here is durability/breadth and is deliberately left
        # in place - the point is that the two are now independent, and only
        # `lock_class` reaches TCAML. No production reflex declares this.
        super().__init__(id="PROBE", name="Lock Probe",
                         priority=ReflexPriority.HIGH, scope=Scope.GLOBAL,
                         affected_systems=frozenset({"all"}),
                         trigger_types=frozenset({"probe"}),
                         lock_class=LockClass.STRUCTURAL)
        self._tcaml = tcaml
        self._blow_up = blow_up
        self.seen_holder = None
        self.seen_module = None

    def trigger(self, trigger: ReflexTrigger):
        self.seen_holder = self._tcaml.holder
        self.seen_module = self._tcaml.holder_module
        if self._blow_up:
            raise RuntimeError("reflex exploded mid-execution")
        return super().trigger(trigger)


def _grid_with_probe(blow_up: bool = False):
    """A Grid whose ONLY reflex is the probe.

    GSR is canon-OPEN (Ruling 10) and rank 1, so it fires on every pressure
    type and wins every GLOBAL contest - with it registered the probe would
    simply defer and never execute, which is correct arbitration and useless
    here. Isolating the probe measures the LOCK, not the priority table.
    """
    tcaml = TCAML()
    grid = ReflexGrid(tcaml=tcaml)
    grid.reflexes.clear()
    probe = _LockProbe(tcaml, blow_up=blow_up)
    grid.add_reflex(probe)
    return tcaml, grid, probe


def test_the_lock_is_held_DURING_execution_and_released_after():
    """Released before execution, TCAML would claim nothing was running while
    a GLOBAL action ran - a lock state that lies is worse than no lock."""
    tcaml, grid, probe = _grid_with_probe()

    grid.evaluate_pressure("test", "probe", 0.9)

    assert probe.seen_holder == "PROBE", "the lock was NOT held during execution"
    assert probe.seen_module == "RACM"
    assert tcaml.holder is None, "the lock was not given back"
    assert grid.racm.self_lock_sweeps == [], (
        "the natural-completion release did not run - the safety sweep "
        "cleaned up after it, which is not the same thing"
    )


def test_a_global_reflex_that_raises_still_gives_the_lock_back():
    """One crash inside a GLOBAL reflex must not block GSR - the failsafe -
    until TTL expires it. The Grid releases from a `finally`."""
    tcaml, grid, probe = _grid_with_probe(blow_up=True)

    with pytest.raises(RuntimeError, match="exploded"):
        grid.evaluate_pressure("test", "probe", 0.9)

    assert tcaml.holder is None


def test_the_orphan_path_gives_the_lock_back():
    """Ruling 9's orphan path `continue`s past a claim whose reflex left the
    registry. An earlier version of this wiring released only AFTER trigger(),
    so that path took the lock and never returned it - `finally` runs on
    `continue`, which is why the whole per-claim body sits inside it.

    DRIVEN THROUGH THE REAL GRID. An earlier version of THIS TEST hand-rolled
    a copy of the Grid's execution loop, which meant it verified the test's own
    copy of the logic and stayed green when the Grid was broken - it survived
    the exact mutation it existed to catch. A test that reimplements the thing
    it pins does not pin it.

    The configuration: GSR's threshold is 0.85 and it is canon-OPEN, so a
    high-pressure cycle makes it win and forces the GLOBAL probe to defer; a
    second cycle just below 0.85 keeps GSR out, and the queued probe - now
    deleted from the registry - wins on rank and orphans.
    """
    tcaml = TCAML()
    grid = ReflexGrid(tcaml=tcaml)

    probe = _LockProbe(tcaml)
    probe.id = "DRPE"                 # rank 3: outranks the filler below
    grid.add_reflex(probe)
    filler = SymbolicReflex(id="FILLER", name="filler",
                            priority=ReflexPriority.LOW, scope=Scope.LOCAL,
                            affected_systems=frozenset({"nothing"}),
                            trigger_types=frozenset({"probe"}))
    grid.add_reflex(filler)

    # Cycle 1: GSR (rank 1, GLOBAL, open) wins; the GLOBAL probe defers.
    grid.evaluate_pressure("test", "probe", 0.9)
    assert "DRPE" in grid.racm.deferred, "the probe did not defer"

    # It leaves the registry while queued - Ruling 9's exact scenario.
    del grid.reflexes["DRPE"]

    # Cycle 2: below GSR's 0.85, so the queued probe wins and orphans.
    grid.evaluate_pressure("test", "probe", 0.75)

    assert grid.orphaned_authorizations, "the orphan path never ran"
    assert grid.orphaned_authorizations[0]["reflex_id"] == "DRPE"
    assert tcaml.holder is None, "the orphan path leaked the GLOBAL lock"


def test_racm_never_enters_a_new_cycle_still_holding_the_last_ones_lock():
    """`arbitrate()` ACQUIRES; the natural-completion release happens in the
    GRID, after arbitrate returned. That split means the release depends on a
    DIFFERENT object behaving - a convention, not a boundary (Ruling 22's
    standing lesson).

    Calling `arbitrate()` directly - every direct-RACM test does - leaked the
    lock, so the NEXT cycle's GSR came back LOCK_DENIED. The Global Integrity
    Lock, disarmed by bookkeeping. The sweep makes the leak UNEXECUTABLE
    rather than fixed only where it is currently known, and records it.
    """
    tcaml = TCAML()
    racm = RACM(rb_system=RBSystem(), tcaml=tcaml)
    claim = _claim("GSR", 0.9, Scope.GLOBAL, ["all"],
                   lock_class=LockClass.STRUCTURAL)

    first = racm.arbitrate([claim])
    assert first.verdict_for("GSR") is Verdict.EXECUTE
    assert tcaml.holder == "GSR"          # nobody released it

    second = racm.arbitrate([claim])
    assert second.verdict_for("GSR") is Verdict.EXECUTE, (
        "a leaked lock disarmed GSR on the following cycle"
    )
    assert racm.self_lock_sweeps, "the sweep must RECORD, never silently tidy"
    assert racm.self_lock_sweeps[0]["action_id"] == "GSR"


def test_the_sweep_never_touches_another_modules_lock():
    """NARROWLY SCOPED: only a lock whose holder_module is 'RACM'. A genuine
    multi-cycle holder - an MSP install spanning cycles, exactly what the TTL
    bound exists for - holds under its own module id. Broadening this check
    would turn a leak-guard into a lock-breaker."""
    tcaml = TCAML()
    racm = RACM(rb_system=RBSystem(), tcaml=tcaml)
    tcaml.lock_request("mspInstall", LockClass.STRUCTURAL, "MSSL")

    racm.arbitrate([_claim("ICA", 0.9, Scope.LOCAL, ["identity"])])

    assert tcaml.holder == "mspInstall"
    assert racm.self_lock_sweeps == []


def test_a_stale_release_is_recorded_not_raised_through_the_finally():
    """Ruling 29 + Ruling 11's principle, at their intersection.

    The Grid releases from a `finally`, and an exception raised inside a
    `finally` REPLACES the exception already in flight. So `release_lock`
    catches `StaleLockRelease` and records it: THE OBSERVER NEVER GATES THE
    OBSERVED. It is REROUTED to a surface that cannot eat a real outcome, not
    swallowed - and it stays loud there.
    """
    tcaml = TCAML()
    racm = RACM(rb_system=RBSystem(), tcaml=tcaml)
    tcaml.lock_request("GSR", LockClass.STRUCTURAL, "RACM")
    tcaml.enter_meta_unstable("cascade")      # revokes RACM's hold

    racm.release_lock("GSR")                  # must NOT raise

    assert len(racm.stale_lock_releases) == 1
    assert "REVOKED" in racm.stale_lock_releases[0]["detail"]

    # ...but the exception type itself is still real and still structural.
    tcaml2 = TCAML()
    tcaml2.lock_request("x", LockClass.STRUCTURAL, "RACM")
    tcaml2.enter_repair_cycle()
    with pytest.raises(StaleLockRelease):
        tcaml2.release("x", "RACM")


# =====================================================================
# CSE -> TCAML: THE REALIGNMENT REQUESTS FINALLY REACH AN OWNER
# =====================================================================

def test_cse_drift_feedback_reaches_tcaml():
    """`anchor_feedback_update` / `trigger_anchor_realignment` have been
    no-ops since CSE was built - the calls existed behind `hasattr` guards
    with nothing on the other side."""
    core = AureaCore()

    core.compass._realign(22.0)

    anchor = core.tcaml.get_anchor("compass")
    assert anchor is not None, "CSE's feedback did not reach the anchor owner"
    assert anchor.last_reported_drift == 22.0
    assert anchor.realignments_requested == 1
    assert core.tcaml.realignment_requests[0]["anchor_id"] == "compass"
    assert "PARKED" in core.tcaml.realignment_requests[0]["state"]


def test_below_the_drift_cap_cse_reports_but_does_not_ask_for_realignment():
    """ANCHOR_DRIFT_CAP = 20.0 stays OWNED BY CSE (Ruling 1): CSE decides when
    to ASK, TCAML executes. A second copy of that threshold inside TCAML would
    be a second owner of the same decision.

    RED if TCAML ever grows its own drift cap and starts deciding this.
    """
    core = AureaCore()

    core.compass._realign(5.0)

    anchor = core.tcaml.get_anchor("compass")
    assert anchor.reports == 1                 # measured and reported
    assert anchor.realignments_requested == 0  # but nothing was asked for
    assert core.tcaml.realignment_requests == []


def test_tcaml_defines_no_drift_cap_of_its_own():
    """The Ruling-1 half of the above, checked at the module surface."""
    import src.topology.tcaml as tcaml_mod

    caps = [n for n in dir(tcaml_mod)
            if "DRIFT" in n.upper() or "ANCHOR_CAP" in n.upper()]
    assert caps == [], f"TCAML must not own a drift threshold; found {caps}"


# =====================================================================
# OBSERVABILITY SLIVER - ADDITIVE ONLY
# =====================================================================

def test_non_executed_claims_carry_a_structured_reason():
    """Structured rejection reasons: reason code, blocking claims, failed
    conditions. Previously a deferred claim carried only the prose string
    'lost same-cycle contention' - true, and useless to a query."""
    racm = RACM(rb_system=RBSystem())
    result = racm.arbitrate([
        _claim("GSR", 0.9, Scope.GLOBAL, ["all"]),
        _claim("ICA", 0.8, Scope.LOCAL, ["identity"]),
    ])

    winner = next(d for d in result.decisions if d.reflex_id == "GSR")
    loser = next(d for d in result.decisions if d.reflex_id == "ICA")

    assert winner.verdict is Verdict.EXECUTE
    assert winner.reason_code is ReasonCode.WON_PRIORITY

    assert loser.verdict is Verdict.DEFERRED
    assert loser.reason_code is ReasonCode.LOST_CONTENTION
    assert loser.blocking_claims == ["GSR"], "must name WHO stood in the way"
    assert any("did not win" in c for c in loser.failed_conditions)


def test_the_sliver_changed_no_verdict_and_no_prose():
    """OBSERVABILITY ONLY - zero arbitration change (§8 step 6b, §9).

    The full nine-scenario verdict dump was captured before and after and is
    byte-identical; this pins the invariant that makes that true - the sliver
    is PARALLEL to the existing prose, never a replacement for it, and the
    existing `reason` strings are untouched.
    """
    racm = RACM(rb_system=RBSystem())
    result = racm.arbitrate([
        _claim("GSR", 0.9, Scope.GLOBAL, ["all"]),
        _claim("ICA", 0.8, Scope.LOCAL, ["identity"]),
    ])

    winner = next(d for d in result.decisions if d.reflex_id == "GSR")
    loser = next(d for d in result.decisions if d.reflex_id == "ICA")
    assert winner.reason == "highest priority"
    assert loser.reason == "lost same-cycle contention"


def test_a_reason_code_never_reaches_the_rank_key():
    """A typed-preference algebra over RACM is REJECTED (§9). ReasonCodes are
    described, never compared: two claims whose only difference is the code
    they will END UP with must rank identically."""
    racm = RACM(rb_system=RBSystem())
    a = _claim("ICA", 0.8, Scope.LOCAL, ["x"])
    b = _claim("ICA", 0.8, Scope.LOCAL, ["y"])
    assert racm._rank_key(a) == racm._rank_key(b)


# =====================================================================
# RULING 30 - THE CONFLICT IS RESOLVED, AND NEITHER SIDE BENT
# =====================================================================

def test_gsr_executes_during_meta_instability_and_structural_change_does_not():
    """RULING 30 (2026-07-26) RESOLVED THE CONFLICT THIS TEST USED TO PIN.

    It changes WITH the ruling, exactly as its own docstring promised.

    OLD (Stage 2, `3c2a1a3`) - `test_gsr_is_locked_out_during_meta_instability_ESCALATION`:
        *** THIS PINS A CONFLICT BETWEEN TWO RULED BEHAVIORS. NOT A RESOLUTION. ***
        ... RACM exempts GSR from suppression, and then TCAML denies it the
        GLOBAL lock two steps later. GSR IS DISARMED DURING INSTABILITY - by
        the lock, not by the arbiter. ...
            assert responses == [], "GSR did not execute - it was locked out"
            assert grid.last_arbitration.verdict_for("GSR") is Verdict.LOCK_DENIED

    NEW: the conflict DISSOLVED at the classification layer. It was never a
    contest between two authorities - it was one axis wearing another's
    vocabulary. GSR's action is SUPPRESSION, which is not expansion, mutation,
    registration, topology change or a doctrine-spine write, so it is
    NON_STRUCTURAL and never reaches Rule 3 at all. Breadth was doing the
    talking; structure decides.

    BOTH HALVES ARE ASSERTED HERE, and the test is worthless without the
    second one - the resolution is only correct if Rule 3 is still intact:
      1. GSR EXECUTES during META_UNSTABLE (RACM's coined exemption survives,
         and nothing lock-denies a suppression).
      2. A STRUCTURAL request in the SAME state is still DENIED - no actor
         exemption entered Rule 3, and `noGrantDuringInstability` still holds.

    Both wrong fixes stay wrong permanently: do NOT exempt an actor from Rule 3
    (breaks the model-checked property), and do NOT delete RACM's exemption
    (disarms the failsafe by another route).
    """
    tcaml = TCAML()
    grid = ReflexGrid(tcaml=tcaml)
    tcaml.enter_meta_unstable("scar bloom cascade")

    # 1. Suppression is never lock-gated, however wide it reaches.
    responses = grid.evaluate_pressure("test", "scar_density", 0.99)

    assert [r.reflex_id for r in responses] == ["GSR"], (
        "GSR must execute during instability - it is the reflex that exists "
        "FOR instability"
    )
    assert grid.last_arbitration.verdict_for("GSR") is Verdict.EXECUTE
    assert tcaml.status is Status.META_UNSTABLE

    # 2. ...and Rule 3 is untouched: structural change is still locked out.
    structural = tcaml.lock_request("doctrineRemap", LockClass.STRUCTURAL, "SAE")
    assert structural.granted is False
    assert "Rule 3" in structural.reason
    assert tcaml.holder is None


def test_a_suppressive_reflex_never_reaches_the_lock_at_all():
    """The mechanism behind the resolution: no reflex claim requests the lock.

    Not "requests it and is granted" - never asks. A healthy TCAML would grant
    GSR anyway, so a test that only checked the verdict could not tell the two
    apart. The holder never moving, and no lock record existing, is what
    distinguishes them.
    """
    tcaml = TCAML()
    grid = ReflexGrid(tcaml=tcaml)

    grid.evaluate_pressure("test", "scar_density", 0.99)

    assert grid.last_arbitration.verdict_for("GSR") is Verdict.EXECUTE
    assert tcaml.lock_denials == []
    assert tcaml.holder is None
    lock_entries = [e for e in grid.rb.entries if "LOCK" in str(e.behavior_type)]
    assert lock_entries == [], (
        f"a suppressive reflex still transacted with the lock: {lock_entries}"
    )


def test_nothing_is_structural_unless_it_declares_itself():
    """The safe default is the whole safety property.

    A hand-built `ReflexClaim` - what a future direct caller writes - must not
    reach the lock by omission. If the dataclass default were STRUCTURAL,
    every claim that simply did not mention `lock_class` would start
    contending for the system-wide lock, silently, and Ruling 30 would have
    been undone by a field initializer.
    """
    claim = ReflexClaim(reflex_id="ANY", pressure_level=0.9, scope=Scope.GLOBAL)
    assert claim.lock_class is LockClass.NON_STRUCTURAL

    tcaml = TCAML()
    racm = RACM(rb_system=RBSystem(), tcaml=tcaml)
    racm.arbitrate([claim])
    assert tcaml.holder is None, "a claim became structural by omission"


def test_a_durability_scope_cannot_be_passed_as_a_lock_class():
    """RULING 30's type boundary. The conflation must be UNWRITABLE, not
    discouraged - a comment saying "don't pass the wrong scope" is the defect
    this ruling exists to kill.

    `racm.Scope` and the raw strings it used to be converted to are both
    refused. Before Ruling 30 `claim.scope.value` typechecked here, read
    correctly, and locked the wrong axis.
    """
    tcaml = TCAML()

    with pytest.raises(TypeError, match="LockClass"):
        tcaml.lock_request("x", Scope.GLOBAL, "RACM")
    with pytest.raises(TypeError, match="LockClass"):
        tcaml.lock_request("x", "GLOBAL", "RACM")
    with pytest.raises(TypeError, match="LockClass"):
        tcaml.lock_request("x", Scope.LOCAL, "RACM")

    assert tcaml.holder is None


def test_the_two_scope_concepts_share_no_member_names():
    """Separated BY NAME as well as by type. If `LockClass` had kept
    GLOBAL/LOCAL, the types would differ but every reader would still have to
    hold two meanings for one word - which is how the conflation survived
    review in the first place."""
    assert {m.name for m in LockClass} == {"STRUCTURAL", "NON_STRUCTURAL"}
    assert {m.name for m in Scope} == {"LOCAL", "GLOBAL"}
    assert not ({m.name for m in LockClass} & {m.name for m in Scope})


def test_ruling_11_durability_still_reads_the_reflex_scope(tmp_path):
    """The durability read is UNTOUCHED (Ruling 11).

    `_log_execution` sets `durable=(reflex.scope == Scope.GLOBAL)`. GSR is
    GLOBAL-scope, so its entry flushes to disk IMMEDIATELY - and GSR is also
    NON_STRUCTURAL, so it takes no lock. Those two facts now come from two
    different fields, which is the entire point of Ruling 30; if separating
    them had re-keyed durability onto `lock_class`, GSR would silently become
    a buffered LOCAL entry and a system-wide safety suppression would sit
    unwritten until some later flush boundary.

    ASSERTS THE FLUSH, NOT A RECORDED STRING. An earlier version of this test
    checked `entry.scope == "GLOBAL"` - which is the scope RB was TOLD, not
    the durability DECISION, so it stayed green when durability was re-keyed.
    Ruling 11's guarantee is "on disk now"; that is what gets asserted.
    """
    log = tmp_path / "rb.jsonl"
    grid = ReflexGrid(rb_system=RBSystem(log_path=str(log)), tcaml=TCAML())

    grid.evaluate_pressure("test", "scar_density", 0.99)

    assert log.exists(), "GSR's GLOBAL-scope entry was not flushed immediately"
    on_disk = [json.loads(line) for line in log.read_text().splitlines() if line]
    assert [e["reflex_triggered"] for e in on_disk] == ["GSR"]


def _claim(rid, level, scope=Scope.LOCAL, systems=(),
           lock_class=LockClass.NON_STRUCTURAL):
    """Ruling 30: `scope` (durability/breadth) and `lock_class` (the ACTION's
    structural class) are SEPARATE knobs here on purpose. Production sets the
    latter NON_STRUCTURAL for every reflex; tests that exercise the lock
    lifecycle declare STRUCTURAL explicitly, the way MSP install will."""
    return ReflexClaim(
        reflex_id=rid, pressure_level=level, scope=scope, lock_class=lock_class,
        affected_systems=frozenset(systems), source_module="test",
        trigger_conditions={"pressure_type": "t", "pressure_level": level},
    )
