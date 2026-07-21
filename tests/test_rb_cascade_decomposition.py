"""
test_rb_cascade_decomposition.py - Ruling 7 (ruled 2026-07-19, implemented
2026-07-20): GSR's cascade decomposes in the RB log instead of dropping from it.

The defect this closes: GSR's cascade branch (pressure > 0.95 or coherence < 0.1)
emits action="cascade", which has no member in the CLOSED BehaviorType enum, and
_log_execution's ValueError guard silently returned - so a system-wide emergency
suspension left no forensic record. Post-Ruling-10 GSR is the sole responder on
three live channels (sbsre_abort, cascade_warning, escalation), so the hole was
live, not hypothetical.

The ruled shape: TRANSLATE, don't extend. cascade -> BehaviorType.SUSPEND (its
constituent behavior, system-wide), with the cascade-class fact preserved on
RBEntry.cascade_meta - a parked surface for the unbuilt CTL (RIL-Nova / ACR-TCAML
pattern). The enum stays closed; GSR's response is untouched; `monitor` and
`base_reflex` remain deliberately unlogged (non-behaviors - nothing to record).
"""

from src.reflex.rb_system import BehaviorType
from src.reflex.reflex_grid import ReflexGrid, ReflexResponse, ReflexTrigger


def _grid():
    grid = ReflexGrid()
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None
    return grid


# ---------------------------------------------------------------------
# (a) cascade decomposes: SUSPEND + all-systems + meta-flag
# ---------------------------------------------------------------------

def test_gsr_cascade_now_lands_in_the_rb_log_as_decomposed_suspend():
    """sbsre_abort@1.0 (the exact registration sbsre.py's _abort makes) drives GSR's
    cascade branch. The forensic log gains the record it was dropping."""
    grid = _grid()

    responses = grid.evaluate_pressure(
        source_module="SBSRE", pressure_type="sbsre_abort",
        pressure_level=1.0, metadata={"thread_id": "SBSRE-0001"})

    gsr = next(r for r in responses if r.reflex_id == "GSR")
    assert gsr.action == "cascade", "GSR's own response is NOT touched by Ruling 7"

    suspends = grid.rb.by_behavior(BehaviorType.SUSPEND)
    assert len(suspends) == 1, "exactly one decomposed entry for the cascade"
    entry = suspends[0]
    assert entry.reflex_triggered == "GSR"
    assert entry.affected_systems == ["all"], "system-wide, from the response itself"
    assert entry.cascade_meta is not None, "the cascade-class fact must survive"
    assert entry.cascade_meta["decomposed_from"] == "cascade"
    assert entry.cascade_meta["trigger_type"] == "sbsre_abort"
    assert entry.cascade_meta["pressure_level"] == 1.0
    assert entry.outcome["result"] == "cascade", (
        "outcome keeps the raw action - the entry is honest about what it decomposed")


# ---------------------------------------------------------------------
# (b) the ordinary suspend band stays distinguishable: meta unset
# ---------------------------------------------------------------------

def test_ordinary_gsr_suspend_carries_no_cascade_meta():
    """cascade_warning@0.9 sits in GSR's ordinary >0.85 suspend band. Same
    behavior_type in the log, but cascade_meta is None - the two suspension classes
    remain distinguishable, which is the whole reason the meta-fact exists."""
    grid = _grid()

    grid.evaluate_pressure(
        source_module="aurea_core", pressure_type="cascade_warning",
        pressure_level=0.9, metadata={})

    suspends = grid.rb.by_behavior(BehaviorType.SUSPEND)
    assert len(suspends) == 1
    entry = suspends[0]
    assert entry.reflex_triggered == "GSR"
    assert entry.cascade_meta is None, (
        "an ordinary band suspend is NOT cascade-class - the flag stays unset")
    assert entry.affected_systems == ["expansion", "nova"]
    assert entry.outcome["result"] == "suspend"


# ---------------------------------------------------------------------
# (c) the non-over-fix guard: monitor / base_reflex still do not log
# ---------------------------------------------------------------------

def test_monitor_and_base_reflex_still_produce_no_rb_entry():
    """These hit the same ValueError-return path cascade used to - and for them it
    is CORRECT: they are non-behaviors with no state change to record. Ruling 7
    translates cascade only."""
    grid = _grid()
    reflex = grid.reflexes["ICA"]
    trigger = ReflexTrigger(reflex_id="ICA", trigger_type="identity_fracture",
                            pressure_level=0.5, source_module="test")

    before = len(grid.rb.entries)
    for action in ("monitor", "base_reflex"):
        grid._log_execution(
            reflex,
            ReflexResponse(reflex_id="ICA", action=action, message="observing"),
            trigger,
        )
    assert len(grid.rb.entries) == before, (
        "observation is not behavior - the forensic log must not gain entries")


# ---------------------------------------------------------------------
# (d) local pin alongside the invariant guard: the enum stayed closed
# ---------------------------------------------------------------------

def test_cascade_is_still_not_a_behavior_type():
    """The structural invariant (test_structural_guards.py) is the law; this is the
    local echo: Ruling 7 was implemented WITHOUT extending the closed enum."""
    assert "cascade" not in {b.value for b in BehaviorType}
