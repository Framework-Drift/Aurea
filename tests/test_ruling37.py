"""
Rulings 37 + 37-A + 38 - THE PASS THAT LETS AN EPOCH CLOSE.

Until this pass, `stabilization_event` - the ONLY legitimate way to restore
AUREA's mutation budget - had no caller anywhere in `src/`. The only working
reset was to kill the process, which Ruling 34 then closed. From Ruling 34 until
here, **no epoch could close by any means at all**: canon tolerated that
explicitly and 34-A's saturation surfacing carried the legibility load.

This file contains the first witness that it can.

    A scar completes fermentation when it COOLS INSTEAD OF IGNITING.
    An anchor consolidates when disturbed orientation RETURNS AND HOLDS.

SML EMITS; SAE NEVER POLLS (Ruling 37 (5)) - the budget-holder is not the judge
of its own debts. CONSOLIDATION IS OBSERVED, NEVER INDUCED (Ruling 15). THE
EPOCH IS NEVER FORCE-CLOSED (34-A). DECAY IS COUNTED QUIET CYCLES, NEVER A
WEIGHT FORMULA (bar #5). All four are pinned below, two structurally.
"""

from __future__ import annotations

import ast
from datetime import datetime

import pytest

from src.doctrine.codex import Codex
from src.expansion.sae import SAE, SATURATION_HORIZON, CeilingExceeded, MutationClass
from src.filtration.scar_logic_core import ScarLogicCore
from src.filtration.scar_management import (
    SCAR_DECAY_CYCLES,
    DecayState,
    DecayTransitionViolation,
    SML,
    normalize,
)
from src.utils.models import Scar
from tests.invariants import _ast as H


# =========================================================================
# HELPERS - real SAE, real ScarLogicCore, real SML. No mocks in the path.
# =========================================================================

def _scar(scar_id, doctrines=(), state=DecayState.ACTIVE):
    return Scar(id=scar_id, name=scar_id, origin="test", weight=2.0,
                decay_state=state.value, linked_doctrines=list(doctrines),
                created_at=datetime.now())


@pytest.fixture
def world(tmp_path):
    """(sae, scar_core, sml) over tmp paths."""
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    sae = SAE(codex=codex, runtime_path=str(tmp_path / "epoch.json"))
    scar_core = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    scar_core.scars = []
    return sae, scar_core, SML(scar_core=scar_core, sae=sae)


def _quiet(sml, n, sae=None):
    """Drive n quiet symbolic cycles, mirroring the pipeline's shared site."""
    for _ in range(n):
        if sae is not None:
            sae.advance_cycle()
        sml.advance_cycle()


# =========================================================================
# THE MILESTONE
# =========================================================================

def test_the_first_legitimate_epoch_closure_in_aureas_existence(world):
    """SPEND -> SATURATE -> SURFACE -> COOL -> CLOSE -> CARRY -> SPEND AGAIN.

    THE WHOLE STORY IN ONE TEST, because the story is the milestone. Watched RED
    against 0a7cfad, where `stabilization_event` has no caller and this test
    CANNOT pass - that RED is the proof the milestone is real rather than a
    rearrangement.

    Every step is a different ruling holding at once:
      34   the spend is durable and the obligation is recorded
      37/4 a BARE authorize() creates an obligation like any other spend
      34-A the saturated epoch SURFACES and is never force-closed
      37   the scar COOLS and SML emits the settle event
      34/3 the guard accepts it because the lineage really was touched
      34/2 closure DISCHARGES what settled and CARRIES what did not
    """
    sae, scar_core, sml = world
    scar_core.scars = [_scar("scar-a"), _scar("scar-b")]

    # 1. SPEND the whole epoch budget across all three counted classes.
    sae.mutate_reflex("R-1", {}, collapse_lineage="scar-a")
    sae.authorize_module_generation("M-1", collapse_lineage="scar-b")
    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-c", target_id="D-1")
    sae.advance_cycle()

    assert sae.epoch == 0
    assert sae.touched_lineages == {"scar-a", "scar-b", "scar-c"}, (
        "Ruling 37 (4): every spend - including the BARE authorize - owes a settle")

    # 2. SATURATE. The fourth mutation is refused, and stays refused.
    with pytest.raises(CeilingExceeded):
        sae.authorize(MutationClass.MUTATE_REFLEX, "scar-z", target_id="R-9")

    # 3. SURFACE (34-A). Six consecutive blocked cycles under continuing
    #    disturbance - a system straining against its ceiling is NOT quiet, so
    #    nothing cools while the pressure is on. The two clocks run
    #    independently and this is where that shows.
    for _ in range(SATURATION_HORIZON + 1):
        with pytest.raises(CeilingExceeded):
            sae.authorize(MutationClass.MUTATE_REFLEX, "scar-z", target_id="R-9")
        sml.note_drift_event()
        sae.advance_cycle()
        sml.advance_cycle()

    assert sae.saturation_surfaced is True
    assert sae.divergence_trigger_eligible is True
    assert sae.epoch == 0, "the horizon FORCE-CLOSED the epoch - canon refuses this"
    assert sae.epoch_count == 3
    assert sml.status()["quiet_counts"]["scar-a"] == 0, "it cooled under pressure"

    # 4. COOL. The pressure lifts. Six quiet cycles carry scar-a past the
    #    strict horizon and out of ACTIVE - by DECAY, which is what makes this
    #    "cooled" rather than "ignited".
    #    scar-b is still being re-collapsed throughout, so it does NOT cool -
    #    which is what leaves a real unsettled obligation for step 6 to carry.
    for _ in range(SCAR_DECAY_CYCLES):
        sml.note_disturbance(["scar-b"])
        sae.advance_cycle()
        sml.advance_cycle()
    assert sae.epoch == 0, "cooled one cycle early - the horizon is STRICT"

    sml.note_disturbance(["scar-b"])
    performed = sml.advance_cycle()

    # 5. THE SETTLE EVENT fired, and the epoch CLOSED.
    assert any(p["scar_id"] == "scar-a" and p["to"] == DecayState.WANING.value
               for p in performed), f"scar-a did not cool: {performed}"
    assert sml.settle_events, "SML did not emit the fermentation event"
    assert sae.epoch == 1, "THE EPOCH DID NOT CLOSE"
    assert sae.epoch_count == 0, "budget was not restored by the closure"

    # 6. THE CARRY (34 res.2): what settled is discharged; what did not, stays.
    assert "scar-a" not in sae.touched_lineages, "the settled lineage was not discharged"
    assert sae.touched_lineages == {"scar-b", "scar-c"}, (
        "closure erased obligations that never settled")

    # 7. AND SHE CAN CHANGE AGAIN - earned, not restarted into.
    auth = sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-b", target_id="D-2")
    assert auth.epoch == 1
    assert sae.saturation_surfaced is False, "the stasis signal outlived the stasis"


def test_a_bare_authorize_creates_a_settle_obligation(world):
    """RULING 37 (4). A slot spent invisibly to the settle condition is BUDGET
    WITHOUT DEBT - the epoch could close on fermentation of every VISIBLE
    lineage while an untracked spend rode through.

    DEFECT WATCHED: `_touch` back at the counted-class call sites, leaving the
    bare `authorize()` - how MSP Stage_2 spends a slot - recording nothing.
    """
    sae, scar_core, sml = world
    scar_core.scars = [_scar("scar-solo")]

    sae.authorize(MutationClass.MODULE_GENERATION, "scar-solo", target_id="M-1")
    assert "scar-solo" in sae.touched_lineages

    _quiet(sml, SCAR_DECAY_CYCLES + 1)
    assert sae.epoch == 1, "fermentation on a bare-authorize lineage did not close"


def test_without_the_fermentation_the_epoch_does_not_close(world):
    """The other half of the same pin: the obligation is real, not decorative."""
    sae, scar_core, sml = world
    scar_core.scars = [_scar("scar-solo")]
    sae.authorize(MutationClass.MODULE_GENERATION, "scar-solo", target_id="M-1")

    _quiet(sml, SCAR_DECAY_CYCLES)          # one short of the strict horizon
    assert sae.epoch == 0, "the epoch closed without the scar completing fermentation"


# =========================================================================
# THE DECAY SCHEDULE (Ruling 37-A (A))
# =========================================================================

def test_the_transition_fires_on_the_sixth_quiet_cycle(world):
    """STRICT, the SATURATION_HORIZON precedent. Five is not enough."""
    _sae, scar_core, sml = world
    scar_core.scars = [_scar("s1")]

    _quiet(sml, SCAR_DECAY_CYCLES)
    assert normalize(scar_core.scars[0].decay_state) is DecayState.ACTIVE

    sml.advance_cycle()
    assert normalize(scar_core.scars[0].decay_state) is DecayState.WANING


def test_only_the_first_transition_settles_a_lineage(world):
    """FERMENTATION COMPLETES AT ACTIVE -> WANING, AND ONLY THERE.

    DEFECT WATCHED: emitting the settle event on ANY transition. Then the SAME
    scar would close a second epoch on its way to DORMANT - one obligation
    discharging two debts, which is budget conjured out of bookkeeping. Caught
    as a gap by the mutation harness; nothing else in the file saw it.

    THE CONFIGURATION MATTERS, and finding it was the mutation harness's doing.
    Removing the ACTIVE->WANING condition survived the obvious version of this
    test, because Ruling 34's CARRY had already discharged the lineage - so the
    second emission found nothing to settle and the mutant was inert. It stops
    being inert the moment the lineage is TOUCHED AGAIN: then a WANING ->
    DORMANT transition would discharge a BRAND NEW obligation on a scar that
    never re-entered ACTIVE and never re-cooled. That is budget conjured out of
    bookkeeping, and it is what this guard actually prevents.
    """
    sae, scar_core, sml = world
    scar_core.scars = [_scar("s1")]
    sae.authorize(MutationClass.MODULE_GENERATION, "s1", target_id="M-1")

    _quiet(sml, SCAR_DECAY_CYCLES + 1)
    assert sae.epoch == 1, "the first transition did not settle the lineage"
    assert len(sml.settle_events) == 1
    assert "s1" not in sae.touched_lineages

    # She spends on the SAME lineage again. Its scar is WANING - already cooled
    # once - and must not be able to settle this new debt without cooling again.
    sae.authorize(MutationClass.MODULE_GENERATION, "s1", target_id="M-2")
    assert "s1" in sae.touched_lineages

    _quiet(sml, SCAR_DECAY_CYCLES + 1)          # on to DORMANT
    assert normalize(scar_core.scars[0].decay_state) is DecayState.DORMANT
    assert len(sml.settle_events) == 1, (
        "WANING -> DORMANT emitted a SECOND settle event - one cooling "
        "discharged two debts")
    assert sae.epoch == 1, "a second epoch closed off a scar that never re-cooled"
    assert "s1" in sae.touched_lineages, "the new obligation was silently discharged"


def test_ten_quiet_cycles_to_dormant(world):
    """Two full horizons, SEQUENTIAL - twice the housekeeping rate, and the
    reason a wound cools slower than a lock expires is that it passes through
    MORE STATES on the same clock, not that a new number was invented."""
    _sae, scar_core, sml = world
    scar_core.scars = [_scar("s1")]

    _quiet(sml, (SCAR_DECAY_CYCLES + 1) * 2)
    assert normalize(scar_core.scars[0].decay_state) is DecayState.DORMANT


@pytest.mark.parametrize("disturb", [
    lambda sml, scar: sml.note_drift_event(),
    lambda sml, scar: sml.note_disturbance([scar.id]),
    lambda sml, scar: sml.note_scar_formed(_scar("new", doctrines=["D-1"])),
])
def test_a_disturbance_restarts_the_count(world, disturb):
    """FERMENTATION INTERRUPTED IS FERMENTATION RESTARTED - 34-A's
    consecutive-means-consecutive applied to cooling.

    DEFECT WATCHED: a counter that only ever increments, so a scar that
    re-ignited every other cycle still cooled on schedule.
    """
    _sae, scar_core, sml = world
    scar = _scar("s1", doctrines=["D-1"])
    scar_core.scars = [scar]

    _quiet(sml, SCAR_DECAY_CYCLES)
    disturb(sml, scar)
    sml.advance_cycle()
    assert sml.status()["quiet_counts"]["s1"] == 0

    sml.advance_cycle()
    assert normalize(scar.decay_state) is DecayState.ACTIVE, "cooled anyway"


def test_fossilized_and_purged_are_declared_and_refused(world):
    """DECLARED-NOT-FAKED. Canon's machine continues past DORMANT; v1 has no
    ruled path, so the transition RAISES rather than being quietly performed.

    THIS PIN SHOULD FAIL if a ruling authorizes either - and the response then
    is to cite that ruling, never to delete the pin.
    """
    _sae, scar_core, sml = world
    scar_core.scars = [_scar("s1")]

    for state in (DecayState.FOSSILIZED, DecayState.PURGED):
        with pytest.raises(DecayTransitionViolation):
            sml.transition("s1", state)
    assert normalize(scar_core.scars[0].decay_state) is DecayState.ACTIVE


def test_retired_maps_into_the_canon_vocabulary_as_dormant():
    """RULING 37 (2). `"retired"` does not survive as a fifth state.

    The mapping is BEHAVIOURALLY INERT for the one module that reads the
    distinction - `autonomy_index` already grouped `retired` with `dormant` as
    "survived and integrated" and said so in a comment anticipating exactly
    this. That is the strongest evidence available that it is the right reading.
    """
    assert normalize("retired") is DecayState.DORMANT
    assert normalize("dormant") is DecayState.DORMANT
    assert normalize("active") is DecayState.ACTIVE
    assert normalize("waning") is DecayState.WANING


def test_an_unreadable_state_reads_as_active_not_as_cooled():
    """The CONSERVATIVE direction. Cooling a scar nobody can classify would
    discharge an obligation on a record we do not understand."""
    assert normalize("something-nobody-wrote") is DecayState.ACTIVE
    assert normalize(None) is DecayState.ACTIVE
    assert normalize("") is DecayState.ACTIVE


def test_active_scars_filter_is_unchanged_for_todays_states(world):
    """Ruling 37 required the migration NOT to change which scars
    `get_active_scars()` returns - that filter is load-bearing (EchoNet's
    resonance net, the compass SOUTH anchor, the dynamic threshold).

    A WANING scar leaving the set is BY DESIGN and is the one downstream
    consequence, pinned here so it is a decision on the record: cooling is
    exactly what "stops exerting live resonance" means.
    """
    _sae, scar_core, sml = world
    scar_core.scars = [_scar("a"), _scar("b", state=DecayState.DORMANT),
                       _scar("c")]
    assert {s.id for s in scar_core.get_active_scars()} == {"a", "c"}

    sml.transition("a", DecayState.WANING)
    assert {s.id for s in scar_core.get_active_scars()} == {"c"}


# =========================================================================
# THE CONSOLIDATION OBSERVER (Ruling 37 (3) / 37-A (B))
# =========================================================================

class _Reading:
    """A minimal CompassReading stand-in: the observer reads three fields."""

    def __init__(self, drift=0.0, disoriented=False, collapsed=(), members=()):
        class _A:
            def __init__(self, c, m):
                self.collapsed = list(c)
                self.members = list(m)
        self.drift = drift
        self.disoriented = disoriented
        self.anchors = {"north": _A(collapsed, members)}


def _cse(codex=None):
    from src.identity.compass import CompassStabilityEngine
    return CompassStabilityEngine(codex=codex)


def test_consolidation_is_observed_on_the_sixth_stable_cycle(world):
    """STRICT again. A lull is shorter than a horizon by definition."""
    from src.identity.compass import CONSOLIDATION_WINDOW

    sae, scar_core, _sml = world
    sae.authorize(MutationClass.MODULE_GENERATION, "D-anchor", target_id="M-1")
    cse = _cse()
    reading = _Reading(members=["D-anchor"])

    for _ in range(CONSOLIDATION_WINDOW):
        assert cse.observe_consolidation(reading, sae) == []
    assert sae.epoch == 0

    assert cse.observe_consolidation(reading, sae) == ["D-anchor"]
    assert sae.epoch == 1, "the observed consolidation did not close the epoch"


@pytest.mark.parametrize("bad", [
    _Reading(drift=25.0, members=["D-anchor"]),
    _Reading(disoriented=True, members=["D-anchor"]),
    _Reading(collapsed=["D-fallen"], members=["D-anchor"]),
])
def test_any_disturbance_resets_the_stability_count(world, bad):
    """All three of Ruling 37 (3)'s conditions, each on its own."""
    from src.identity.compass import CONSOLIDATION_WINDOW

    sae, _sc, _sml = world
    sae.authorize(MutationClass.MODULE_GENERATION, "D-anchor", target_id="M-1")
    cse = _cse()
    good = _Reading(members=["D-anchor"])

    for _ in range(CONSOLIDATION_WINDOW):
        cse.observe_consolidation(good, sae)
    cse.observe_consolidation(bad, sae)
    assert cse.observe_consolidation(good, sae) == []
    assert sae.epoch == 0, "consolidation survived a disturbance"


def test_consolidation_fires_once_per_episode(world):
    """An unbroken calm is ONE formation, not a pulse train."""
    from src.identity.compass import CONSOLIDATION_WINDOW

    sae, _sc, _sml = world
    sae.authorize(MutationClass.MODULE_GENERATION, "D-anchor", target_id="M-1")
    cse = _cse()
    reading = _Reading(members=["D-anchor"])

    for _ in range(CONSOLIDATION_WINDOW * 4):
        cse.observe_consolidation(reading, sae)
    assert len(cse.consolidations) == 1
    assert sae.epoch == 1, "one formation should close exactly one epoch"


def test_consolidation_does_not_fire_for_an_unanchored_lineage(world):
    """The evidence guard (Ruling 34 res.3) still binds: a touched lineage that
    anchors nothing recovered is not consolidated by someone else's calm."""
    from src.identity.compass import CONSOLIDATION_WINDOW

    sae, _sc, _sml = world
    sae.authorize(MutationClass.MODULE_GENERATION, "scar-elsewhere", target_id="M-1")
    cse = _cse()
    reading = _Reading(members=["D-unrelated"])

    for _ in range(CONSOLIDATION_WINDOW + 1):
        cse.observe_consolidation(reading, sae)
    assert sae.epoch == 0


# =========================================================================
# RULING 38 - SIGNALS ARE BUILT FROM active()
# =========================================================================

def test_the_locked_doctrine_never_enters_signals(monkeypatch):
    """Behavioral, against the REAL seed, and it CAPTURES THE ACTUAL DICT.

    DEFECT WATCHED: `view()` restored at the builder. An earlier draft of this
    pin asserted on `codex.active()` instead - which is the builder's INPUT, not
    its output - so it passed no matter what the builder did. Caught by the
    mutation harness; the fix is to intercept `dee.cycle` and read the signals
    it was actually handed.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    seen = {}
    real = core.dee.cycle

    def _capture(signals=None, **kw):
        seen["signals"] = dict(signals or {})
        return real(signals=signals, **kw)

    monkeypatch.setattr(core.dee, "cycle", _capture)
    core.process_input("Honesty is pointless.")

    assert seen, "the doctrine-evolution path never ran; the pin witnessed nothing"
    assert "Doctrine-0" not in seen["signals"], (
        "the LOCKED doctrine entered the signals dict - the builder is back on "
        "view() and the proposal gate is borrowing DRPAS's narrowing again")
    assert "Doctrine-0" in core.codex.doctrines, "locked must stay LIVE (Ruling 35)"
    assert set(seen["signals"]) == {d.id for d in core.codex.active()}, (
        "dead signal entries: the builder and DRPAS disagree about eligibility")


def test_the_pipeline_advances_the_sml_cycle():
    """THE WIRE, PINNED. DEFECT WATCHED: `advance_cycle` implemented and never
    called - scars frozen mid-cool forever, so no epoch could ever close and the
    whole organ would look built.

    Drives the REAL pipeline, so a call that exists but is unreachable still
    fails. Caught as a gap by the mutation harness (M22 survived every other
    pin), which is the harness doing its job.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    core.scar_core.scars = [_scar("wire-probe")]
    core.sml._quiet["wire-probe"] = 0

    core.process_input("The kettle boiled quietly.")

    assert core.sml.status()["quiet_counts"].get("wire-probe") == 1, (
        "process_input did not advance SML's symbolic cycle - nothing cools, "
        "and no epoch can ever close")


def test_the_proposal_gate_refuses_a_locked_id_even_if_signals_contain_it():
    """THE FORCING FORM, and it is the whole point of the pin.

    Ruling 38's value is DEFENCE IN DEPTH: `_nova_proposals`'s membership check
    must be a REAL second layer, not a formality that happens to be satisfied
    because DRPAS upstream never flags a locked doctrine. Without injecting a
    signals dict that DOES contain the locked id, this pin would pass for the
    upstream reason and witness nothing - the Ruling 35 vacuity lesson.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    forced = {"Doctrine-0": {"pressure": 0.9, "drpe": True}}
    assert core._nova_proposals(forced) is None, (
        "a locked doctrine produced a proposal when the signals dict was forced "
        "to contain it - the gate is borrowing DRPAS's narrowing instead of "
        "being its own layer")


# =========================================================================
# STRUCTURAL - the two bars that must hold by SCOPE, not by discipline
# =========================================================================

WEIGHT_TERMS = {"weight", "half_life", "magnitude"}


def find_weight_in_schedule(tree: ast.AST) -> list:
    """Any weight term inside the decay schedule's own methods.

    Bar #5: a scar's WEIGHT REPORTS its magnitude and never SCHEDULES its
    cooling. A weight-driven schedule would make the heaviest scars cool by a
    coined curve nobody ruled, at the site deciding when AUREA may change again.
    """
    found = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name not in {"advance_cycle", "_disturbed", "transition"}:
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and node.attr in WEIGHT_TERMS:
                found.append((node.lineno, f"reads .{node.attr}"))
            if isinstance(node, ast.Name) and node.id in WEIGHT_TERMS:
                found.append((node.lineno, f"uses {node.id}"))
    return found


def test_no_weight_term_schedules_decay():
    """SECTION 9 STANDING BAR #5, SEVENTH application."""
    tree = H.parse(H.repo_root() / "src/filtration/scar_management.py")
    assert not find_weight_in_schedule(tree), (
        "a weight term entered the decay schedule. Weight REPORTS; counted "
        "quiet cycles SCHEDULE. Reopen only on a corpus-recovered curve.")


@pytest.mark.parametrize("body", [
    "def advance_cycle(self):\n    return self.horizon / scar.weight\n",
    "def transition(self, i, s):\n    half_life = 3\n    return half_life\n",
    "def _disturbed(self, scar):\n    return scar.weight > 1\n",
])
def test_the_weight_scanner_actually_fires(body):
    """Self-pinned (Ruling 32's precedent)."""
    assert find_weight_in_schedule(ast.parse(body))


def test_sae_never_reaches_for_sml():
    """RULING 37 (5): SML EMITS; SAE NEVER POLLS.

    SAE owning the settle-detection would make the BUDGET-HOLDER THE JUDGE OF
    ITS OWN DEBTS. The direction of the dependency is the enforcement: `sae.py`
    must not import or name `scar_management` / `SML` at all.
    """
    source = (H.repo_root() / "src/expansion/sae.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = getattr(node, "module", "") or ""
            names = " ".join(a.name for a in node.names)
            assert "scar_management" not in mod and "SML" not in names, (
                f"sae.py imports the decay owner at line {node.lineno}")
        if isinstance(node, ast.Attribute) and node.attr in {"sml", "advance_decay"}:
            raise AssertionError(f"sae.py reaches for SML at line {node.lineno}")
