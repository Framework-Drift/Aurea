"""
test_psi.py - Ruling 8 Stage 1: the PSI reflex face, ISOLATED (no Grid wiring yet).

PSI is built directly with a real RIL (the actual sole-writer identity store, so the
deep-snapshot guarantee under test is the real one) and a minimal scar-core stub whose
`get_scar(id)` returns the LIVE stored object.

Ruling 22 (2026-07-25) gave the real ScarLogicCore snapshot-on-read, so the stub is
now STRICTER than the owner rather than a mirror of it - and deliberately left that
way: PSI must not retain or mutate what it reads, and a stub that hands out the live
record is the surface that can actually catch it doing so. Loosening the stub to
match the owner would retire a live check.

Covers the five Stage-1 assertions:
  (a) fires on anchor_collapse with a grounded Scarline -> parked directive + graduated
      action at both canon bands;
  (b) the trigger_type gate - does NOT fire on any live foreign pressure type even at
      magnitudes that clear every threshold (sbsre_abort 1.0, cascade_warning 0.9,
      compass_disorientation 1.0, identity_fracture 0.75 - the last is PERMANENTLY
      excluded: identity_fracture was ruled DISTINCT from legacy_fracture,
      2026-07-20);
  (c) abstains on anchor_collapse with an EMPTY Scarline - no directive, no fabricated
      scar reference, no lock proposal;
  (d) hard band PROPOSES output_blocked=True but self-locks nothing - RIL's store is
      byte-identical after, and the directive holds only primitives (no live Scar);
  (e) PSI's read path cannot mutate RIL - the directive is frozen, and the snapshot
      RIL hands out is disconnected from `ril.threads`.
"""

import dataclasses

import pytest

from src.identity.psi import PSI, PSIDirective, PSI_TRIGGER_TYPES, COLLAPSE_CONSISTENT
from src.identity.ril import RIL, IdentityThread
from src.identity.compass import ANCHOR_DRIFT_CAP, ANCHOR_COLLAPSE_DEGREES, MAX_DRIFT
from src.reflex.reflex_grid import ReflexTrigger
from src.utils.models import Scar


# Canon-derived band probes (PSI's thresholds are the 20/25 deg lines in CSE's
# normalized units - see psi.py "THRESHOLDS"). ONSET sits inside the reroute band,
# HARD just past the hard-kill line - the same geometry the compass actually emits.
ONSET_PRESSURE = 22.0 / MAX_DRIFT     # past 20 deg onset, short of 25 deg hard band
HARD_PRESSURE = 26.0 / MAX_DRIFT      # past the 25 deg hard-kill line


class ScarCoreStub:
    """ScarLogicCore's read face only, held DELIBERATELY stricter than the owner:
    get_scar returns the LIVE object, which is exactly the hazard PSI's _live_weight
    documents handling. The real owner snapshots since Ruling 22; this does not, so
    a PSI that retained or mutated what it read would still be caught here."""

    def __init__(self, scars):
        self._scars = {s.id: s for s in scars}

    def get_scar(self, scar_id):
        return self._scars.get(scar_id)


def _scar(sid: str, weight: float) -> Scar:
    return Scar(id=sid, name=sid, origin="test", weight=weight)


def _trigger(trigger_type: str, level: float) -> ReflexTrigger:
    return ReflexTrigger(reflex_id="PSI", trigger_type=trigger_type,
                         pressure_level=level, source_module="test")


@pytest.fixture
def grounded():
    """A real RIL carrying two scars (first ingested seeds ORIGIN), plus the stub
    scar owner holding their live weights. Scar-002 is dominant by weight."""
    ril = RIL()
    s1 = _scar("Scar-001", 1.0)
    s2 = _scar("Scar-002", 3.0)
    ril.ingest_scar(s1)
    ril.ingest_scar(s2)
    psi = PSI(ril=ril, scar_core=ScarCoreStub([s1, s2]))
    return psi, ril


# ---------------------------------------------------------------------
# (a) fires on anchor_collapse + grounded Scarline
# ---------------------------------------------------------------------

def test_fires_on_anchor_collapse_with_grounded_scarline(grounded):
    psi, _ = grounded

    assert psi.evaluate_pressure(_trigger("anchor_collapse", ONSET_PRESSURE)) is True
    assert psi.evaluate_pressure(_trigger("anchor_collapse", HARD_PRESSURE)) is True

    onset = psi.trigger(_trigger("anchor_collapse", ONSET_PRESSURE))
    assert onset.action == "reroute"
    assert onset.output_blocked is False

    directive = onset.metadata["psi_directive"]
    assert isinstance(directive, PSIDirective)
    assert directive.scar_ref == "Scar-002", "bearing must be the heaviest live scar"
    assert directive.origin_ref == "Scar-001", "Scar-0 comes from RIL's ORIGIN thread"
    assert directive.fallback_bearing == "Scar-001"
    assert directive.tone_weight == 3.0
    assert directive.collapse_consistency == COLLAPSE_CONSISTENT
    assert onset.metadata["directive_parked"] is True, (
        "no HAIL exists - the directive must be emitted parked, not consumed")


def test_dormant_trigger_types_are_accepted_by_the_gate(grounded):
    """scarline_destabilization and legacy_fracture have no emitter today - the gate
    still accepts them so their emitters can arrive without editing PSI."""
    psi, _ = grounded
    for dormant in ("scarline_destabilization", "legacy_fracture"):
        assert dormant in PSI_TRIGGER_TYPES
        assert psi.evaluate_pressure(_trigger(dormant, HARD_PRESSURE)) is True


# ---------------------------------------------------------------------
# (b) the gate - foreign pressure types never fire PSI, at any magnitude
# ---------------------------------------------------------------------

@pytest.mark.parametrize("trigger_type,level", [
    ("sbsre_abort", 1.0),
    ("cascade_warning", 0.9),
    ("compass_disorientation", 1.0),
    ("identity_fracture", 0.75),   # ruled DISTINCT from legacy_fracture (2026-07-20):
                                   # this exclusion is permanent canon, not provisional
])
def test_gate_rejects_foreign_trigger_types_even_at_full_magnitude(
        grounded, trigger_type, level):
    psi, _ = grounded
    assert psi.evaluate_pressure(_trigger(trigger_type, level)) is False, (
        f"PSI must not fire on {trigger_type} - Ruling 8 gates activation on "
        f"trigger_type, not magnitude")


# ---------------------------------------------------------------------
# (c) abstain on empty Scarline - never fabricate a bearing
# ---------------------------------------------------------------------

def test_abstains_on_anchor_collapse_with_empty_scarline():
    psi = PSI(ril=RIL(), scar_core=ScarCoreStub([]))

    response = psi.trigger(_trigger("anchor_collapse", HARD_PRESSURE))

    assert response.action == "monitor"
    assert response.output_blocked is False
    assert "psi_directive" not in response.metadata
    assert response.metadata["grounded"] is False


def test_abstains_with_no_ril_at_all():
    """No injected RIL means no grounding is even possible - same abstention."""
    psi = PSI()
    response = psi.trigger(_trigger("anchor_collapse", HARD_PRESSURE))
    assert response.action == "monitor"
    assert response.output_blocked is False
    assert "psi_directive" not in response.metadata


# ---------------------------------------------------------------------
# (d) hard band proposes output_blocked - and self-locks nothing
# ---------------------------------------------------------------------

def test_hard_band_proposes_output_blocked_but_never_self_locks(grounded):
    psi, ril = grounded
    before = ril.thread_state()   # deep snapshot of the whole store, pre-trigger

    response = psi.trigger(_trigger("anchor_collapse", HARD_PRESSURE))

    assert response.action == "suppress"
    assert response.output_blocked is True, (
        "the hard band must PROPOSE the lock for RACM to authorize")

    # ...and that proposal is all that happened: PSI wrote nothing anywhere.
    assert ril.thread_state() == before, "PSI must not touch RIL's threads"

    # The directive carries primitives only - no live Scar rides out of the reflex.
    directive = response.metadata["psi_directive"]
    assert isinstance(directive.scar_ref, str)
    assert isinstance(directive.tone_weight, float)
    assert not isinstance(directive.origin_ref, Scar)
    for value in dataclasses.asdict(directive).values():
        assert not isinstance(value, Scar)


# ---------------------------------------------------------------------
# (e) the read path cannot reach RIL's store
# ---------------------------------------------------------------------

def test_read_path_cannot_mutate_ril_threads():
    ril = RIL()
    scar = _scar("Scar-001", 2.0)
    ril.ingest_scar(scar)
    psi = PSI(ril=ril, scar_core=None)   # no scar owner: falls back to snapshot weight

    response = psi.trigger(_trigger("anchor_collapse", HARD_PRESSURE))
    directive = response.metadata["psi_directive"]
    assert directive.tone_weight == 2.0, "snapshot-weight fallback when no scar owner"

    # The directive is frozen - it is a statement, not a channel.
    with pytest.raises(dataclasses.FrozenInstanceError):
        directive.scar_ref = "forged"

    # And the snapshot surface PSI reads through is disconnected from the store.
    snapshot = ril.thread_state(IdentityThread.SCARLINE)
    snapshot[IdentityThread.SCARLINE].clear()
    assert ril.threads[IdentityThread.SCARLINE] == [scar], (
        "mutating a thread_state snapshot must never reach ril.threads")
