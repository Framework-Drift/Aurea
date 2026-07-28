"""
test_ruling43.py - RULING 43: the seed's decay vocabulary loads losslessly.

    `normalize()` read `Scar-0`'s `"locked"` and `Δ91`'s `"fossil"` as ACTIVE,
    because neither literal was in the enum and the unknown-value fallback is
    "treat it as live." That enrolled THE ORIGIN COLLAPSE - weight 100, the
    heaviest record in the seed, the one every other scar is downstream of, the
    one canon protects BY NAME at 5a:1391 - in the scheduled decay machine, SIX
    QUIET CYCLES from a WANING transition that emits a settle event and restores
    mutation budget.

    THE CONSTITUTION MUST NOT COOL.

Ruling 35's exact class, scar-side: a defect in how a RECORDED STATUS IS READ,
invisible to every test that loads because the misreading WAS the fixture's
baseline, and fixed entirely on the read side. The seed is byte-identical.

WHY THE FALLBACK WAS WRONG WITHOUT BEING WRONG-HEADED (`normalize`'s own words):
"treat the unclassifiable as live" is CONSERVATIVE FOR WOUNDS and
ANTI-CONSERVATIVE FOR EXEMPTIONS. A wound read as live keeps an obligation open.
An exemption read as live enrolls the protected record in the machine it was
exempted from. The fallback survives, aimed; the seed's own words simply stopped
being unclassifiable.
"""

import json

import pytest

from src.filtration.scar_logic_core import ScarLogicCore
from src.filtration.scar_management import (
    DECAY_SEQUENCE, LIVE_STATES, SCAR_DECAY_CYCLES, SML,
    DecayState, DecayTransitionViolation, normalize,
)
from src.utils.models import Scar


# =====================================================================
# PIN 1 - THE REAL-SEED REGRESSION
# =====================================================================

def test_the_seeds_own_decay_words_load_as_themselves():
    """RULING 43 (1)+(2), against the ACTUAL tracked seed - Ruling 35's
    regression-pin precedent, and for its reason: a synthetic fixture would prove
    the mechanism on data of my own choosing, which is exactly the class of test
    that let a fallen doctrine load LIVE for months.
    """
    core = ScarLogicCore()

    assert normalize(core.get_scar("Scar-0").decay_state) is DecayState.LOCKED
    assert normalize(core.get_scar("Δ91").decay_state) is DecayState.FOSSILIZED

    # And the raw records are untouched - this is a READ-side fix.
    seed = {s["id"]: s for s in json.load(open("data/scars.json", encoding="utf-8"))}
    assert seed["Scar-0"]["decay_state"] == "locked"
    assert seed["Δ91"]["decay_state"] == "fossil"


def test_both_seed_states_sit_outside_the_decay_sequence():
    """RULING 43 (4) - `advance_cycle` needed NO CHANGE, and this proves that
    rather than assuming it. The skip it already had (`state not in
    DECAY_SEQUENCE: continue`) does the work the moment `normalize` stops lying.
    """
    assert DecayState.LOCKED not in DECAY_SEQUENCE
    assert DecayState.FOSSILIZED not in DECAY_SEQUENCE
    assert set(DECAY_SEQUENCE) == {DecayState.ACTIVE, DecayState.WANING}


# =====================================================================
# PIN 2 - THE FORCING FORM. This is the one that witnesses the hazard.
# =====================================================================

def _sml_over_the_real_seed():
    core = ScarLogicCore()
    sae = _SAEStub()
    return core, sae, SML(scar_core=core, sae=sae)


class _SAEStub:
    """Accepts every lineage, so a settle event CANNOT fail to be observed for
    the uninteresting reason that SAE refused it."""

    def __init__(self):
        self.touched_lineages = {"Scar-0", "Δ91", "Doctrine-0"}
        self.epoch = 0
        self.calls = []

    def stabilization_event(self, kind, lineage=""):
        self.calls.append((kind, lineage))
        return True


def test_thirty_quiet_cycles_move_neither_protected_record():
    """THE FORCING PIN, and without it pin 1 passes for the loading reason alone.

    RED AT `a6cc2fa`: with `"locked"` normalizing to ACTIVE, `Scar-0` entered
    `_quiet`, counted to six, and transitioned ACTIVE -> WANING - firing
    `_emit_fermentation` on a lineage SAE had touched, which RESTORES MUTATION
    BUDGET. Thirty cycles took it to DORMANT. That is the hazard, and this test
    is where it is witnessed.

    Six is the trigger (STRICT comparison, `count > SCAR_DECAY_CYCLES`), so
    thirty cycles is five clear horizons - far past any off-by-one.
    """
    core, sae, sml = _sml_over_the_real_seed()

    for _ in range(30):
        sml.advance_cycle()

    assert normalize(core.get_scar("Scar-0").decay_state) is DecayState.LOCKED
    assert normalize(core.get_scar("Δ91").decay_state) is DecayState.FOSSILIZED

    # They never even entered the counter - the skip is upstream of the count.
    assert "Scar-0" not in sml._quiet
    assert "Δ91" not in sml._quiet

    # No transition was recorded against either.
    moved = {t["scar_id"] for t in sml.transitions}
    assert "Scar-0" not in moved
    assert "Δ91" not in moved

    # And no settle event was emitted on either lineage - the consequence that
    # actually costs something, since a settle event restores mutation budget.
    settled = {lineage for _kind, lineage in sae.calls}
    assert "Scar-0" not in settled
    assert "Δ91" not in settled


# =====================================================================
# PIN 3 - an operator cannot retire The Origin Collapse
# =====================================================================

def test_manual_retire_refuses_the_origin_collapse():
    """RULING 43 (3), the FROM direction, reached through Ruling 40's operator
    path. `manual_retire` is the one surface that jumps a scar straight to
    DORMANT, and the one record no operator gets to finish is the one every
    other scar is downstream of."""
    core, _sae, sml = _sml_over_the_real_seed()

    with pytest.raises(DecayTransitionViolation) as exc:
        sml.manual_retire("Scar-0")

    assert "Origin Collapse" in str(exc.value)
    assert normalize(core.get_scar("Scar-0").decay_state) is DecayState.LOCKED, (
        "the record must be untouched - the refusal precedes the write")


def test_no_transition_may_move_a_locked_scar_by_any_route():
    """The refusal is on the STATE, not on the method that asked. Every
    destination is refused, so a caller cannot find an unguarded door."""
    _core, _sae, sml = _sml_over_the_real_seed()

    for destination in (DecayState.ACTIVE, DecayState.WANING, DecayState.DORMANT):
        with pytest.raises(DecayTransitionViolation):
            sml.transition("Scar-0", destination)


def test_nothing_may_lock_a_scar_at_runtime():
    """RULING 43 (3), the TO direction - a DIFFERENT refusal with a DIFFERENT
    reason (Ruling 29: one message covering two causes is a defect).

    Locking is not something that happens to a scar at runtime; it is what the
    SEED declares about a record AUREA was founded on. Were this permitted, any
    caller could lock any scar and thereby remove it from the settle machinery
    forever - a silent way to withhold the pressure that closes an epoch.
    """
    core = ScarLogicCore()
    core.scars = [Scar(id="S-1", name="s", origin="t", decay_state="active")]
    sml = SML(scar_core=core)

    with pytest.raises(DecayTransitionViolation) as exc:
        sml.transition("S-1", DecayState.LOCKED)

    assert "runtime" in str(exc.value).lower()
    assert normalize(core.scars[0].decay_state) is DecayState.ACTIVE


# =====================================================================
# PIN 4 - the fabricated-settlement guard
# =====================================================================

def test_a_fossilized_scar_never_emits_a_settle_event():
    """A settle event restores mutation budget. A record that arrived ALREADY
    fossilized has not just now cooled - it cooled before AUREA ever ran - so
    letting it settle would credit her budget for a cooling that is not an event
    in her runtime (Ruling 36's reasoning about seed fossils, applied to decay).
    """
    core, sae, sml = _sml_over_the_real_seed()

    for _ in range(30):
        sml.advance_cycle()

    assert all(lineage != "Δ91" for _kind, lineage in sae.calls)
    assert not any(t["scar_id"] == "Δ91" for t in sml.transitions)


def test_only_a_scar_leaving_ACTIVE_settles_anything():
    """CASE PIN ADDED AFTER A SURVIVING MUTANT (M15: dropping the `was is ACTIVE`
    half of the settle condition left all 521 tests green).

    THE QUESTION THE SURVIVOR GOT: what execution path would have to run for this
    to matter? One where something transitions a NON-ACTIVE scar TO WANING. No
    caller in `src/` does that today - `DECAY_SEQUENCE` sends WANING to DORMANT,
    and `manual_retire` goes straight to DORMANT - so the guard was correct and
    entirely unwitnessed.

    IT IS NOT AN EQUIVALENT MUTANT, and that is why this pin exists rather than a
    note. The guard is what makes "cooled" distinguishable from every other route
    into WANING (Ruling 37 (1)). The day a re-ignition or revival path lands, the
    mutated form would FABRICATE a settle event and restore mutation budget for a
    cooling that never happened - pin 4's hazard, arriving through a different
    door.

    The refusal is deliberately NOT widened here: whether `DORMANT -> WANING`
    should be refused outright is a ruling nobody has made, and inventing one
    would be the over-reach this pass is otherwise at pains to avoid. What is
    pinned is the SETTLE CONDITION, which is already ruled.
    """
    core = ScarLogicCore()
    core.scars = [Scar(id="S-cold", name="s", origin="t", decay_state="dormant")]
    sae = _SAEStub()
    sae.touched_lineages = {"S-cold"}
    sml = SML(scar_core=core, sae=sae)

    sml.transition("S-cold", DecayState.WANING)

    assert sae.calls == [], (
        "a scar that did not leave ACTIVE has not cooled, and must not settle")
    assert sml.transitions[-1]["settled_lineages"] == []


# =====================================================================
# PIN 5 - THE EXEMPTION IS AIMED, NOT SPRAYED
# =====================================================================

def test_every_other_seed_scar_still_cools_on_schedule():
    """REGRESSION. The whole risk of a fix like this is that it over-reaches and
    quietly exempts more than it was aimed at. Every seed scar written `"active"`
    must still normalize ACTIVE and still reach WANING on the sixth quiet cycle.
    """
    core, _sae, sml = _sml_over_the_real_seed()
    ordinary = [s.id for s in core.scars
                if normalize(s.decay_state) is DecayState.ACTIVE]

    assert len(ordinary) == 9, "9 of the 11 seed scars are ordinary live wounds"
    assert "Scar-0" not in ordinary and "Δ91" not in ordinary

    for _ in range(SCAR_DECAY_CYCLES + 1):
        sml.advance_cycle()

    for sid in ordinary:
        assert normalize(core.get_scar(sid).decay_state) is DecayState.WANING, (
            f"{sid} is an ordinary wound and must still cool on schedule")


def test_unknown_junk_still_reads_as_active():
    """RULING 43 (5) - THE FALLBACK SURVIVES, AIMED. Ruling 37's conservative
    direction is unchanged for values nobody wrote on purpose; what changed is
    that the seed's own words are no longer among them."""
    assert normalize("garbled-nonsense") is DecayState.ACTIVE
    assert normalize(None) is DecayState.ACTIVE
    assert normalize("") is DecayState.ACTIVE


# =====================================================================
# THE LOAD-BEARING CONSEQUENCE - Ruling 37's standing requirement
# =====================================================================

def test_the_live_filter_keeps_the_constitution_and_releases_the_fossil():
    """RULING 37 LEFT A STANDING REQUIREMENT ABOUT THIS EXACT SET, and it is why
    this test exists: a decay-vocabulary migration must not SILENTLY change which
    scars `get_active_scars()` returns. Three consumers depend on it - EchoNet's
    resonance net, EchoNet's dynamic threshold, and the compass SOUTH anchor.

    A bare `is ACTIVE` filter would have dropped BOTH records the moment
    `normalize` stopped mis-reading them - `Scar-0` (weight 100) and `Δ91`
    (weight 99), 199 of 835 SOUTH bearing mass, gone as a SIDE EFFECT of a fix
    aimed at the decay schedule. So the two are treated differently, each with a
    cited authority:

      * `Scar-0` is LOCKED and STAYS LIVE. Ruling 35 already ruled what `locked`
        means in this codebase - live and readable, excluded from the CHANGE
        machinery only. It resonates and carries bearing exactly as before.
      * `Δ91` is FOSSILIZED and LEAVES. That is the one intended behavioral
        change of this pass, recorded as a DECISION ON THE RECORD in the same
        form Ruling 37 recorded WANING's departure: a fossil has matured out of
        live crisis, `autonomy_index` has grouped `"fossil"` with
        `"retired"`/`"dormant"` since before SML existed, and Ruling 37 pinned
        the principle in terms - "cooling is exactly what 'stops exerting live
        resonance' means."
    """
    assert LIVE_STATES == frozenset({DecayState.ACTIVE, DecayState.LOCKED})

    active = {s.id for s in ScarLogicCore().get_active_scars()}

    assert "Scar-0" in active, (
        "The Origin Collapse must not leave her resonance substrate as a side "
        "effect of being protected from the decay schedule")
    assert "Δ91" not in active, (
        "a fossil has matured out of live crisis - the one intended change")
    assert len(active) == 10


def test_the_constitution_still_carries_its_full_bearing_weight():
    """The consequence that would have been hardest to notice and worst to have:
    the compass SOUTH anchor is "the high-weight scars that define who she is",
    and `Scar-0` is the heaviest record she has."""
    from src.identity.compass import SCAR_BEARING_WEIGHT

    active = ScarLogicCore().get_active_scars()
    bearing = {s.id: float(s.weight) for s in active
               if float(s.weight) >= SCAR_BEARING_WEIGHT}

    assert bearing.get("Scar-0") == 100.0
    assert sum(bearing.values()) == 736.0, (
        "835 before this pass; the 99 that left is Δ91 and ONLY Δ91")
