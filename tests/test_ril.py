"""
test_ril.py - RIL (Recursive Identity Layer): the sole writer of `threads`.

Covers:
- RIL constructs cleanly with every dependency defaulted to None.
- ingest_scar appends to SCARLINE every time, and seeds ORIGIN exactly once, from the
  first scar RIL ever ingests.
- ingest_doctrine_mutation always records DOCTRINE, and fires ICA (through the real
  ReflexGrid/RACM, reading evaluate_pressure's RETURN value) only when BOTH grounding
  facts hold: the mutation names a fallen ancestor, and that ancestor was already
  anchored in RIL's own identity threads via a scar's linked_doctrines. Either fact
  missing -> abstain, no VOID entry, no reflex fired - this is the "ground it or
  abstain" discipline, tested from both missing-fact angles.
- when RACM does not authorize ICA (no reflex_grid at all, standing in for "not
  authorized"), the fracture routes to CSA as a REQUEST instead of vanishing.
- thread_state() returns a DEEP snapshot: mutating the returned structure, including
  nested objects, never reaches self.threads.
"""

import pytest

from src.identity.ril import RIL, IdentityThread, IDENTITY_FRACTURE_PRESSURE
from src.utils.models import Scar, Doctrine
from src.doctrine.dee import EligibilityRuling, Verdict
from src.reflex.reflex_grid import ReflexGrid


class _FakeCSA:
    """Records suspend() calls without touching real suspension storage."""

    def __init__(self):
        self.calls = []

    def suspend(self, **kwargs):
        self.calls.append(kwargs)
        return "CSA-fake-entry"


def _root_scar(linked_doctrines=None) -> Scar:
    return Scar(id="Scar-1", name="root", origin="test",
                linked_doctrines=linked_doctrines or [])


def _ruling(doctrine_id: str, reason: str = "test mutation") -> EligibilityRuling:
    return EligibilityRuling(doctrine_id=doctrine_id, verdict=Verdict.APPROVED,
                              reason=reason, executed_by="SAE")


# =====================================================================
# Construction
# =====================================================================

def test_ril_constructs_cleanly_with_all_deps_none():
    ril = RIL()
    assert ril.threads == {t: [] for t in IdentityThread}
    assert ril.dominant_thread() is None
    # Deliberately no __bool__/__len__: an empty-but-real RIL must not be falsy.
    assert bool(ril) is True


# =====================================================================
# ingest_scar - SCARLINE every time, ORIGIN exactly once
# =====================================================================

def test_ingest_scar_appends_to_scarline_and_seeds_origin_once():
    ril = RIL()
    first = _root_scar()
    second = Scar(id="Scar-2", name="second", origin="test")

    ril.ingest_scar(first)
    assert ril.threads[IdentityThread.SCARLINE] == [first]
    assert ril.threads[IdentityThread.ORIGIN] == [first]

    ril.ingest_scar(second)
    assert ril.threads[IdentityThread.SCARLINE] == [first, second]
    # ORIGIN must NOT have been overwritten by the second scar.
    assert ril.threads[IdentityThread.ORIGIN] == [first]


# =====================================================================
# ingest_doctrine_mutation - always records DOCTRINE
# =====================================================================

def test_ingest_doctrine_mutation_always_records_doctrine_thread():
    ril = RIL()
    doctrine = Doctrine(id="Doctrine-1", name="d", mutation_lineage=[])
    ril.ingest_doctrine_mutation(_ruling("Doctrine-1"), doctrine)

    assert len(ril.threads[IdentityThread.DOCTRINE]) == 1
    recorded = ril.threads[IdentityThread.DOCTRINE][0]
    assert recorded["doctrine_id"] == "Doctrine-1"


# =====================================================================
# Fracture: ground it or abstain
# =====================================================================

def test_fracture_fires_ica_when_ancestor_is_identity_anchored():
    """Both grounding facts present: mutation_lineage names a fallen ancestor, and
    that ancestor is already linked from a scar in SCARLINE. Real ReflexGrid/RACM -
    ICA (rank 2) outranks the also-triggered ANCHOR_COLLAPSE (rank 4, overlapping
    affected_systems) and executes alone at pressure 0.75."""
    grid = ReflexGrid()
    ril = RIL(reflex_grid=grid)
    ril.ingest_scar(_root_scar(linked_doctrines=["Doctrine-1"]))

    mutated = Doctrine(id="Doctrine-1-v2", name="evolved",
                        mutation_lineage=["Doctrine-1"])
    ril.ingest_doctrine_mutation(_ruling("Doctrine-1-v2", reason="fell"), mutated)

    void_entries = ril.threads[IdentityThread.VOID]
    assert len(void_entries) == 1
    assert void_entries[0]["fallen_ancestor"] == "Doctrine-1"

    ica = next((r for r in grid.response_log if r.reflex_id == "ICA"), None)
    assert ica is not None, "ICA should have been sourced and authorized to execute"


def test_fracture_abstains_when_ancestor_not_identity_anchored():
    """The mutation names a fallen ancestor, but RIL never anchored identity to it
    (no scar links to it) - not grounded, so RIL abstains: no VOID entry, no reflex
    pressure raised at all."""
    grid = ReflexGrid()
    ril = RIL(reflex_grid=grid)
    ril.ingest_scar(_root_scar(linked_doctrines=["Doctrine-UNRELATED"]))

    mutated = Doctrine(id="Doctrine-1-v2", name="evolved",
                        mutation_lineage=["Doctrine-1"])
    ril.ingest_doctrine_mutation(_ruling("Doctrine-1-v2"), mutated)

    assert ril.threads[IdentityThread.VOID] == []
    assert grid.response_log == []


def test_fracture_abstains_when_no_ancestor_fell():
    """Empty mutation_lineage: nothing fell, so there is nothing to ground a fracture
    in - abstain, even though a scar anchors this exact doctrine ID (i.e. this is not
    a false negative from a broken anchoring check, it's the correct call given no
    ancestor exists to check)."""
    grid = ReflexGrid()
    ril = RIL(reflex_grid=grid)
    ril.ingest_scar(_root_scar(linked_doctrines=["Doctrine-1"]))

    fresh = Doctrine(id="Doctrine-1", name="fresh", mutation_lineage=[])
    ril.ingest_doctrine_mutation(_ruling("Doctrine-1"), fresh)

    assert ril.threads[IdentityThread.VOID] == []
    assert grid.response_log == []


def test_unresolved_fracture_routes_to_csa_as_request():
    """A grounded fracture where RACM never gets a chance to authorize ICA (no
    reflex_grid at all - standing in for "not authorized") must not just vanish: it
    routes to CSA as a REQUEST, the same pattern SBSRE already uses."""
    csa = _FakeCSA()
    ril = RIL(reflex_grid=None, csa=csa)
    ril.ingest_scar(_root_scar(linked_doctrines=["Doctrine-1"]))

    mutated = Doctrine(id="Doctrine-1-v2", name="evolved",
                        mutation_lineage=["Doctrine-1"])
    ril.ingest_doctrine_mutation(_ruling("Doctrine-1-v2", reason="fell"), mutated)

    assert len(ril.threads[IdentityThread.VOID]) == 1
    assert len(csa.calls) == 1
    call = csa.calls[0]
    assert call["source"] == "RIL"
    assert call["pressure"] == IDENTITY_FRACTURE_PRESSURE


# =====================================================================
# Read views - deep snapshots only
# =====================================================================

def test_thread_state_returns_deep_snapshot_not_a_live_reference():
    ril = RIL()
    scar = _root_scar(linked_doctrines=["Doctrine-1"])
    ril.ingest_scar(scar)

    view = ril.thread_state()
    view[IdentityThread.SCARLINE].append("INTRUDER")
    view[IdentityThread.SCARLINE][0].linked_doctrines.append("HACKED")

    assert ril.threads[IdentityThread.SCARLINE] == [scar]
    assert ril.threads[IdentityThread.SCARLINE][0].linked_doctrines == ["Doctrine-1"]

    single = ril.thread_state(IdentityThread.ORIGIN)
    single[IdentityThread.ORIGIN].append("INTRUDER-2")
    assert ril.threads[IdentityThread.ORIGIN] == [scar]
