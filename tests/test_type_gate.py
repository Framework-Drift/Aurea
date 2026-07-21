"""
test_type_gate.py - Ruling 10 (2026-07-20): type-gated reflex activation.

Base `SymbolicReflex.evaluate_pressure` is now type-membership AND magnitude. `None`
trigger_types = canon-OPEN, which only GSR may claim (2a:583's five OR'd all-domain
failsafe conditions); `ReflexGrid.add_reflex` REFUSES any other open registration
(UngatedReflexViolation) - the wrong path is unexecutable, not discouraged.

Pins, per the ruling's preservation matrix:
  (a) the false-lock chain is dead: scar_density@0.5 produces NO ACR claim, no
      arbitration, and no deferred ACR carrying a foreign payload for Ruling 9's
      queue path to later execute as a false anchor-collapse suppress;
  (b) GSR-open still catches everything loud enough: compass_disorientation@1.0
      (the ruled lock - full-path test lives in test_anchor_collapse_lock.py),
      sbsre_abort@1.0, cascade_warning@0.9;
  (c) identity_fracture@0.75 -> ICA fires (its one LIVE type, sourced by RIL);
      ACR and PSI do not;
  (d) structural guard: every registered reflex is GSR or declares a non-None
      trigger_types - enforced at registration, verified here as the belt.
"""

import pytest

from src.aurea_core import AureaCore
from src.identity.psi import PSI
from src.identity.ril import RIL
from src.reflex.reflex_grid import (
    ReflexGrid,
    ReflexPriority,
    ReflexTrigger,
    SymbolicReflex,
    UngatedReflexViolation,
)


def _grid():
    grid = ReflexGrid()
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None
    return grid


def _trigger(trigger_type, level, reflex_id="pending", source="test"):
    return ReflexTrigger(reflex_id=reflex_id, trigger_type=trigger_type,
                         pressure_level=level, source_module=source)


# ---------------------------------------------------------------------
# (a) the false-lock chain is dead at the claim
# ---------------------------------------------------------------------

def test_scar_density_produces_no_acr_claim_false_lock_chain_dead():
    """Pre-Ruling-10, ACR's magnitude-only gate claimed scar_density@0.5 (>= its
    0.222 threshold), and via Ruling 9's honest queue path a deferred ACR carrying
    that foreign payload could later execute a FALSE anchor-collapse suppress with
    a false forensic message (CLAUDE.md §8, false-lock path). Ruling 10 kills it at
    the claim: raw scar density is GSR's Lexicon domain, not a directional threat."""
    grid = _grid()

    acr = grid.reflexes["ANCHOR_COLLAPSE"]
    assert acr.evaluate_pressure(_trigger("scar_density", 0.5)) is False
    assert acr.evaluate_pressure(_trigger("scar_density", 1.0)) is False, (
        "no magnitude makes scar_density a directional threat")

    responses = grid.evaluate_pressure(
        source_module="scar_core", pressure_type="scar_density",
        pressure_level=0.5, metadata={"active_scars": 50})

    assert responses == []
    assert grid.racm.cycle == 0, "nobody claimed it - arbitration never ran"
    assert grid.racm.deferred == [], "and no deferred ACR carries a foreign payload"


# ---------------------------------------------------------------------
# (b) GSR-open still catches every loud event
# ---------------------------------------------------------------------

@pytest.mark.parametrize("trigger_type,level", [
    ("compass_disorientation", 1.0),   # the ruled lock - full path in
                                       # test_total_disorientation_locks_via_gsr_not_drift
    ("sbsre_abort", 1.0),
    ("cascade_warning", 0.9),
])
def test_gsr_open_gate_catches_loud_events(trigger_type, level):
    grid = _grid()

    responses = grid.evaluate_pressure(
        source_module="test", pressure_type=trigger_type,
        pressure_level=level, metadata={})

    ids = {r.reflex_id for r in responses}
    assert ids == {"GSR"}, (
        f"{trigger_type}@{level} is GSR's failsafe domain alone now - "
        f"got {ids or 'nothing'}")


# ---------------------------------------------------------------------
# (c) identity_fracture -> ICA, and only ICA
# ---------------------------------------------------------------------

def test_identity_fracture_fires_ica_and_only_ica():
    grid = _grid()
    grid.add_reflex(PSI(ril=RIL(), scar_core=None))   # PSI present and silent

    ica = grid.reflexes["ICA"]
    acr = grid.reflexes["ANCHOR_COLLAPSE"]
    psi = grid.reflexes["PSI"]
    fracture = _trigger("identity_fracture", 0.75)
    assert ica.evaluate_pressure(fracture) is True
    assert acr.evaluate_pressure(fracture) is False
    assert psi.evaluate_pressure(fracture) is False, (
        "ruled DISTINCT from legacy_fracture - permanent exclusion")

    responses = grid.evaluate_pressure(
        source_module="RIL", pressure_type="identity_fracture",
        pressure_level=0.75, metadata={"doctrine_id": "AVT.002"})

    assert {r.reflex_id for r in responses} == {"ICA"}
    assert responses[0].action == "reroute"          # ICA's 0.7-0.9 band


def test_ica_dormant_types_are_accepted_by_the_gate():
    """The three Lexicon-11 dormant types are declared so their emitters can arrive
    without editing ICA - same discipline as PSI's dormant pair."""
    ica = _grid().reflexes["ICA"]
    for dormant in ("internal_contradiction", "doctrine_anchor_collision",
                    "symbolic_instability"):
        assert ica.evaluate_pressure(_trigger(dormant, 0.75)) is True


# ---------------------------------------------------------------------
# (d) structural guard: GSR or gated - no third state
# ---------------------------------------------------------------------

def test_every_registered_reflex_is_gsr_or_type_gated():
    for grid in (ReflexGrid(), AureaCore().reflex_grid):
        for reflex_id, reflex in grid.reflexes.items():
            assert reflex.trigger_types is not None or reflex_id == "GSR", (
                f"{reflex_id} is registered canon-OPEN without being GSR - "
                f"Ruling 10 violation")


def test_add_reflex_refuses_non_gsr_open_registration():
    """The enforcement is the registration refusal itself - a comment saying
    'declare your types' is a request; this exception is a wall."""
    grid = ReflexGrid()
    rogue = SymbolicReflex("ROGUE", "Rogue Open Reflex", ReflexPriority.LOW)

    with pytest.raises(UngatedReflexViolation):
        grid.add_reflex(rogue)
    assert "ROGUE" not in grid.reflexes

    gated = SymbolicReflex("GATED", "Properly Gated", ReflexPriority.LOW,
                           trigger_types=frozenset({"some_pressure"}))
    grid.add_reflex(gated)
    assert "GATED" in grid.reflexes
