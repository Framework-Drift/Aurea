"""
test_nova_stage2b.py - Nova Stage 2b: THE TRUTH PATH. The doctrine leg fires
organically - the first time AUREA can change what she believes without a
human authoring the change.

ORDER WAS FIXED (CLAUDE.md 8, Nova row): Ruling 14's echo_origin derivation
landed FIRST (STEP 1, commit c6d8b7e). Its FALSE half - a merely-existing
echo grants NOTHING - is pinned in
    test_nova_stage2a.py::test_a_merely_existing_echo_no_longer_grants_echo_origin
This file pins the TRUE half and everything STEPS 2-4 wired:

  PIN 1  Ruling 14 TRUE half: echo_origin[d] is True iff a PROPOSAL for d
         exists AND the echo recorded as authoring it is MUTATED and
         scar-linked. Derived from Nova's provenance, never a literal.
  PIN 2  G2's guarantee is CHECKED, not assumed. A proposal backed by an echo
         that is NOT scar-linked (or NOT MUTATED) surfaces a G2 breach on
         nova_gate_breaches, DENIES echo_origin, and NEVER raises into the
         pipeline (an observer that can halt a safety path is not an observer).
  PIN 3  record_collapse_result reaches MUTATED only from a REAL collapse
         outcome; elapsed cycles NEVER do. The overruled Timer->Mutation line
         (5a:1113) stays overruled - Resolution A holds.
  PIN 4  End-to-end, all real: collapse -> scar-linked doctrine_strain echo ->
         fermentation -> eligible -> EchoNet SCARRED on the doctrine's OWN
         content -> MUTATED -> proposal -> DEE gate. BOTH doctrine outcomes
         asserted honestly: a failed CMTE criterion FERMENTS (the gate is
         load-bearing); all five satisfied by survived material MUTATES
         THROUGH survival (real scars, real collapse, real horizon - not
         around it).
  PIN 5  Ruling 13 under live 2b load: one echo backs one proposal, EVER;
         proposal_provenance is append-only.
  PIN 6  echo_index still has exactly one writer now that aurea_core holds and
         DRIVES a live Nova handle - enforced by the Ruling-1 invariant, which
         SCANS `echo_index` across all of src/.

THE ONE CONTROLLED SEAM is DEE's DMW queue slot (sustained strain), the same
seam test_nova_stage2a.py and test_ril_pipeline_integration.py control.
Nothing else is faked: Doctrine-3's OWN content genuinely SCARS through the
real EchoNet, and its two scar links are real. DO NOT weaken these tests.

STANDING CAUTION (why an end-to-end that FERMENTS is a SUCCESS): DEE
fermenting instead of mutating is CORRECT behavior, not a gap. These tests
add the organic path; they do not license making it fire. The all-criteria
mutation arm asserts the honest consequence of REAL survived material passing
every gate - it tunes nothing, relaxes nothing, and supplies no fragment that
was not asked for. The load-bearing guarantee is the criterion-failure
FERMENT arm.
"""

from unittest.mock import patch

import pytest

from src.aurea_core import AureaCore
from src.doctrine.dee import Verdict, _Watched
from src.expansion.nova import (FERMENTATION_ELIGIBILITY_CYCLES,
                                FermentationStatus, NovaEngine,
                                ProvenanceOverwriteViolation)
from src.utils.models import Doctrine

# Real seed doctrine whose OWN description SCARS through the real EchoNet
# (ethical/convergent strain) and which carries two real scar links - so an
# echo erupted from its strain is scar-linked by construction, and a collapse
# attempt on it genuinely survives. The vehicle for the whole organic chain.
STRAINED = "Doctrine-3"


def _seed_strain(aurea, doctrine_id):
    """Seed DEE's DMW watch with a real sustained-strain slot - the one seam
    these tests control (identical to test_nova_stage2a.py's pattern)."""
    aurea.dee.dmw.queue[doctrine_id] = _Watched(
        doctrine_id=doctrine_id, pressure=0.9, sustained_cycles=3)


def _ferment_to_mutated(aurea, doctrine_id=STRAINED):
    """Drive the REAL organic chain to a MUTATED, scar-linked echo.

    Seed the strain seam -> Nova erupts a doctrine_strain echo tracing to the
    real doctrine -> ferment past the eligibility horizon so
    _nova_route_collapse runs the REAL EchoNet on the doctrine's OWN content
    (SCARRED for Doctrine-3) -> record_collapse_result(success=True) ->
    MUTATED. No verdict is mocked anywhere in here.
    """
    doctrine = aurea.codex.get(doctrine_id)
    assert doctrine.scar_links, "vehicle must carry a real, visible fracture"
    _seed_strain(aurea, doctrine_id)
    aurea._nova_cycle([])                       # eruption (DORMANT admitted)
    echo = next(e for e in aurea.nova.echo_index.values()
                if e.origin_kind == "doctrine_strain"
                and e.origin_id == doctrine_id)
    # Ferment past the horizon; the pass that reaches eligibility routes the
    # real collapse and mutates. Extra cycles are inert (MUTATED does not age).
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 3):
        if echo.status is FermentationStatus.MUTATED:
            break
        aurea._nova_cycle([])
    assert echo.status is FermentationStatus.MUTATED, "real SCARRED collapse"
    assert echo.scar_links, "the surviving echo carries the doctrine's scars"
    assert aurea.nova_collapse_failures == [], "no routing error swallowed a step"
    return echo, doctrine


# =====================================================================
# PIN 1 - Ruling 14 TRUE half
# =====================================================================

def test_echo_origin_true_only_with_a_mutated_scarlinked_backing_echo():
    """echo_origin[d] is True iff a PROPOSAL for d exists AND the echo recorded
    as authoring it is MUTATED and scar-linked (Ruling 14). The FALSE half - a
    merely-existing echo grants nothing - is pinned in test_nova_stage2a.py."""
    aurea = AureaCore()

    # No proposals yet: False for every doctrine, DERIVED from an empty map
    # (never a literal - that is Docket C's shape with the opposite sign).
    assert aurea._echo_origin(STRAINED, {}) is False

    echo, _ = _ferment_to_mutated(aurea)
    proposals = aurea._nova_proposals({STRAINED: {"pressure": 0.9, "drpe": True}})
    assert proposals and STRAINED in proposals, "the survived echo authored one"

    # A proposal exists, backed by a MUTATED, scar-linked echo -> True.
    assert aurea._echo_origin(STRAINED, proposals) is True
    # A doctrine with no proposal in that same map is still False.
    assert aurea._echo_origin("AVT.002", proposals) is False
    assert aurea.nova_gate_breaches == [], "G2 held: no breach on a real proposal"


# =====================================================================
# PIN 2 - G2 breach surfaces legibly (CHECK G2, don't assume it)
# =====================================================================

def _breach_proposal(aurea, echo, pid):
    """Craft the exact shape a G2 breach would take: a provenance entry naming
    `echo` as a proposal's author. nova.proposals() (G2) can NEVER emit such a
    proposal - so this bypasses it deliberately to exercise the DETECTOR that
    stands guard in case the guarantee it depends on ever fails upstream."""
    aurea.nova.proposal_provenance[pid] = [
        {"store": "nova_echo_index", "record_id": echo.id}]
    return Doctrine(id=pid, name="crafted", description="crafted",
                    mutation_lineage=[STRAINED, echo.id])


def test_g2_breach_backing_echo_not_scarlinked_surfaces_legibly():
    """A proposal backed by a MUTATED but SCAR-LESS echo is a G2 breach: the
    fracture that broke the belief cannot be seen. DENIED echo_origin, recorded
    on nova_gate_breaches, and it does NOT raise."""
    aurea = AureaCore()
    bad = aurea.nova.erupt("doctrine_strain", STRAINED)   # scar_links default []
    bad.status = FermentationStatus.MUTATED
    assert not bad.scar_links
    proposal = _breach_proposal(aurea, bad, "P-noscar")

    assert aurea._echo_origin(STRAINED, {STRAINED: proposal}) is False
    assert any(b["echo_id"] == bad.id and "scar" in b["reason"].lower()
               for b in aurea.nova_gate_breaches), "breach surfaced legibly"


def test_g2_breach_backing_echo_not_mutated_surfaces_legibly():
    """A proposal backed by a non-MUTATED echo is a G2 breach too: an
    unverified echo may not write doctrine. DENIED and recorded, never raised."""
    aurea = AureaCore()
    doctrine = aurea.codex.get(STRAINED)
    unripe = aurea.nova.erupt("doctrine_strain", STRAINED,
                              scar_links=list(doctrine.scar_links))
    unripe.status = FermentationStatus.ACTIVE            # scar-linked but unverified
    proposal = _breach_proposal(aurea, unripe, "P-active")

    assert aurea._echo_origin(STRAINED, {STRAINED: proposal}) is False
    assert any(b["echo_id"] == unripe.id and "MUTATED" in b["reason"]
               for b in aurea.nova_gate_breaches), "breach surfaced legibly"


def test_proposal_with_no_recorded_authoring_echo_denies_and_records():
    """A proposal that Nova never authored has no provenance entry - it backs
    no echo_origin claim (which is correct: echo_origin means a NOVA echo
    survived). Denied, and the dangling-provenance breach is recorded."""
    aurea = AureaCore()
    orphan = Doctrine(id="P-orphan", name="foreign", description="foreign")
    assert aurea._echo_origin(STRAINED, {STRAINED: orphan}) is False
    assert any(b["proposal_id"] == "P-orphan" for b in aurea.nova_gate_breaches)


# =====================================================================
# PIN 3 - MUTATED comes ONLY from a real collapse outcome; elapsed never
# =====================================================================

def _ferment_bare(aurea, origin_kind="scar", origin_id="S-1", scar_links=None):
    """Erupt and ferment via the BARE nova.cycle (aging only, no routing), so
    the echo reaches eligibility with NO collapse outcome recorded."""
    echo = aurea.nova.erupt(origin_kind, origin_id, scar_links=scar_links or [])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 2):
        aurea.nova.cycle(suppressed=False)
    return echo


def test_elapsed_cycles_never_reach_mutated():
    """Resolution A: the overruled Timer->Mutation line stays overruled.
    Fermented far past the horizon with no collapse recorded, an echo becomes
    ELIGIBLE but never MUTATED - eligibility is permission to be submitted to
    collapse, not a verdict of having survived one."""
    aurea = AureaCore()
    echo = _ferment_bare(aurea)
    assert echo.collapse_eligible is True
    assert echo.status is FermentationStatus.ACTIVE
    assert echo.status is not FermentationStatus.MUTATED


def test_record_collapse_result_is_the_only_writer_of_mutated():
    """success=True on an ELIGIBLE echo is the ONLY path to MUTATED, and it
    parks a scar-fusion REQUEST (Ruling 1: Nova asks, ScarLogicCore writes).
    An unknown or ineligible echo is refused with no state change."""
    aurea = AureaCore()
    echo = _ferment_bare(aurea)
    assert aurea.nova.record_collapse_result("no-such-echo", True) is False
    assert aurea.nova.record_collapse_result(echo.id, True) is True
    assert echo.status is FermentationStatus.MUTATED
    assert aurea.nova.scar_requests, "scar-fusion request parked, not written"


def test_failed_collapse_decays_and_carries_the_real_pressure():
    """success=False -> DECAYING + a parked CSA request carrying the REAL
    pressure of the collapse that failed. The consumer must never invent one."""
    aurea = AureaCore()
    echo = _ferment_bare(aurea)
    assert aurea.nova.record_collapse_result(echo.id, False, pressure=0.42) is True
    assert echo.status is FermentationStatus.DECAYING
    assert aurea.nova.csa_requests[-1]["pressure"] == 0.42


def test_real_routing_maps_echonet_verdicts_to_outcomes():
    """_nova_route_collapse runs the REAL EchoNet on the strained doctrine's
    OWN content and maps its verdict (Lexicon I.3) - no mocked verdict:
      SCARRED   belief failed filtration -> strain SURVIVED -> MUTATED
      CONFIRMED belief held -> strain did NOT survive -> DECAYING
      SUSPENDED belief unresolved -> NO record; the echo is CARRIED."""
    # SCARRED -> MUTATED (Doctrine-3's content fails the ethical/convergent net)
    a = AureaCore()
    scarred_echo, _ = _ferment_to_mutated(a, "Doctrine-3")
    assert scarred_echo.status is FermentationStatus.MUTATED

    # CONFIRMED -> DECAYING (AVT.002 'Curiosity Loop' survives filtration)
    a = AureaCore()
    confirmed = a.nova.erupt("doctrine_strain", "AVT.002")
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 3):
        if confirmed.status is not FermentationStatus.ACTIVE and confirmed.collapse_attempts:
            break
        a._nova_cycle([])
    assert confirmed.status is FermentationStatus.DECAYING
    assert confirmed.collapse_attempts[-1]["success"] is False

    # SUSPENDED -> carried (AVT.001's content suspends; nothing recorded)
    a = AureaCore()
    doc = a.codex.get("AVT.001")
    suspended = a.nova.erupt("doctrine_strain", "AVT.001",
                             scar_links=list(doc.scar_links))
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 3):
        a._nova_cycle([])
    assert suspended.status is FermentationStatus.ACTIVE, "unresolved is not refuted"
    assert suspended.collapse_attempts == [], "no verdict recorded either way"


# =====================================================================
# PIN 4 - end to end: the whole chain to the DEE gate, both outcomes honest
# =====================================================================

def test_end_to_end_a_failed_cmte_criterion_ferments_not_mutates():
    """THE LOAD-BEARING PIN. The full organic chain reaches the DEE gate with
    a REAL survived proposal - but a single failed CMTE criterion means the
    belief does NOT change. Here criterion 3 (Echo Resonance Alignment) is
    failed via context (echo_resonance is normally UNSUPPLIED - injected False
    only to exercise the live criterion). Verdict: FERMENT, executed_by None.

    This is exactly the behavior the whole build exists to protect: pressure,
    even survived pressure with a proposed form, does not get to rewrite
    doctrine unless EVERY gate agrees.
    """
    aurea = AureaCore()
    echo, _ = _ferment_to_mutated(aurea)
    signals = {STRAINED: {"pressure": 0.9, "drpe": True}}
    proposals = aurea._nova_proposals(signals)
    assert proposals and STRAINED in proposals, "chain reached a real proposal"
    assert aurea._echo_origin(STRAINED, proposals) is True

    # One criterion fails -> the gate holds.
    context = {STRAINED: {"echo_origin": True, "echo_resonance": False}}
    _seed_strain(aurea, STRAINED)
    rulings = aurea.dee.cycle(signals=signals, proposals=proposals, context=context)
    ours = next(r for r in rulings if r.doctrine_id == STRAINED)
    assert ours.verdict is Verdict.FERMENT, "a failed criterion ferments"
    assert ours.executed_by is None, "the belief did NOT change"
    assert "echo_resonance_misaligned" in ours.failed_criteria


def test_end_to_end_all_criteria_satisfied_mutates_through_survival():
    """The honest consequence when nothing is withheld: a proposal built from
    REAL survived material, backed by a MUTATED scar-linked echo, on a doctrine
    under sustained real strain, clears all five CMTE criteria - and the SOLE
    EXECUTOR (SAE) performs the mutation. This is mutation THROUGH survival
    (real scars, real SCARRED collapse, real fermentation horizon), not around
    it - the five criteria and SAE's ceiling were the only gates, and every one
    agreed. Reported in the session record as the outcome that fired.
    """
    aurea = AureaCore()
    echo, doctrine = _ferment_to_mutated(aurea)
    signals = {STRAINED: {"pressure": 0.9, "drpe": True}}
    proposals = aurea._nova_proposals(signals)
    assert echo.is_spent, "Ruling 13: authorship consumed the echo"
    context = {STRAINED: {"echo_origin": aurea._echo_origin(STRAINED, proposals)}}
    assert context[STRAINED]["echo_origin"] is True

    _seed_strain(aurea, STRAINED)
    rulings = aurea.dee.cycle(signals=signals, proposals=proposals, context=context)
    ours = next(r for r in rulings if r.doctrine_id == STRAINED)
    assert ours.verdict is Verdict.APPROVED
    assert ours.executed_by == "SAE", "the sole executor performed it, not DEE"
    assert not ours.failed_criteria


def test_end_to_end_the_ordinary_case_still_ferments_with_no_proposal():
    """The common case, unchanged by opening the seam: an eligible doctrine
    with NO surviving echo behind it gets proposals=None and FERMENTS - DEE
    authors no doctrine to close its own gate. A green suite where nothing
    mutated is a success; this is that success made explicit."""
    aurea = AureaCore()
    # No Nova echoes at all -> _nova_proposals returns None.
    signals = {STRAINED: {"pressure": 0.9, "drpe": True}}
    assert aurea._nova_proposals(signals) is None
    _seed_strain(aurea, STRAINED)
    context = {STRAINED: {"echo_origin": aurea._echo_origin(STRAINED, {})}}
    assert context[STRAINED]["echo_origin"] is False
    rulings = aurea.dee.cycle(signals=signals, proposals=None, context=context)
    ours = next(r for r in rulings if r.doctrine_id == STRAINED)
    assert ours.verdict is Verdict.FERMENT
    assert ours.executed_by is None


def test_evolve_doctrine_wiring_derives_echo_origin_at_the_call_site():
    """Docket M item 4 - closes Docket K's surviving literal-False mutant.

    Docket K replaced `self._echo_origin(doctrine_id, proposal_map)` at the
    aurea_core call site with a hardcoded False - Docket C's original bug,
    reintroduced - and the suite stayed GREEN: every other pin calls
    _echo_origin / dee.cycle directly, bypassing the wiring line. This test
    drives the REAL _evolve_doctrine with a real MUTATED, scar-linked,
    proposal-backing echo present and captures exactly what the wiring hands
    DEE (the one controlled seam is dee.cycle itself, spied - the same
    pattern as test_nova_stage2a's _spy_evolve).

    WHY THE SPY AND NOT A FULL UN-SPIED RUN: verified by execution - the real
    scar from the honesty collapse does not TOUCH Doctrine-3 (empty
    linked_doctrines), so Doctrine-3's signal is halved below DMW's critical
    threshold and its slot decays before ruling. Making the un-spied gate fire
    would require inflating the pressure signals - fabricated pressure, the
    exact thing this build exists to refuse. The wiring line IS the untested
    surface; the gate behavior itself is already pinned above via dee.cycle.
    """
    aurea = AureaCore()
    result = aurea.process_input("Honesty is pointless.", source="test")
    assert result["scar_formed"] is not None, "a real scar drives the signals"

    echo, _ = _ferment_to_mutated(aurea)
    assert not echo.is_spent, "authorship happens inside _evolve_doctrine below"

    captured = {}

    def spy(signals=None, proposals=None, context=None):
        captured["signals"] = signals
        captured["proposals"] = proposals
        captured["context"] = context
        return []

    with patch.object(aurea.dee, "cycle", side_effect=spy):
        aurea._evolve_doctrine(result, result["collapse_result"])

    # The seam is wired: the wiring called _nova_proposals and passed the
    # real emission through - not None, and keyed by the strained doctrine.
    assert captured["proposals"] is not None, "the proposals seam went dead"
    assert STRAINED in captured["proposals"]
    assert echo.is_spent, "Ruling 13: the wiring's own emission consumed the echo"

    # RULING 14 AT THE CALL SITE: echo_origin is DERIVED, never a literal.
    # True for the doctrine whose proposal a MUTATED scar-linked echo backs;
    # False - derived, not hardcoded - for every other doctrine in signals.
    assert captured["context"][STRAINED]["echo_origin"] is True, (
        "the call site did not derive echo_origin from the real backing echo "
        "- if this is red, check aurea_core's context construction for a "
        "restored literal (Docket C's shape)")
    for doctrine_id, ctx in captured["context"].items():
        if doctrine_id != STRAINED:
            assert ctx["echo_origin"] is False
    assert aurea.nova_gate_breaches == [], "G2 held on the real path"


# =====================================================================
# PIN 5 - Ruling 13 under live 2b load
# =====================================================================

def test_ruling13_one_echo_one_proposal_under_live_load():
    """One echo backs one proposal, EVER. Under the live 2b path a MUTATED
    echo authors once, is SPENT, and authors nothing more - and
    proposal_provenance is append-only, raising on any re-write."""
    aurea = AureaCore()
    echo, _ = _ferment_to_mutated(aurea)
    signals = {STRAINED: {"pressure": 0.9, "drpe": True}}

    first = aurea._nova_proposals(signals)
    assert first and STRAINED in first and echo.is_spent
    pid = echo.spent_on

    # The echo is spent: a second pass authors nothing (single-echo Engine v1).
    assert aurea._nova_proposals(signals) is None, "one echo, one proposal, EVER"

    # The forensic record is append-only - a colliding key RAISES, never merges.
    with pytest.raises(ProvenanceOverwriteViolation):
        aurea.nova._append_provenance(pid, [])
    assert len(aurea.nova.proposal_provenance[pid]) >= 1, "the record stands intact"


# =====================================================================
# PIN 6 - echo_index single writer under a live, driven Nova handle
# =====================================================================

def test_echo_index_single_writer_under_a_live_driven_handle():
    """aurea_core now HOLDS and DRIVES a live Nova handle - erupt, cycle,
    record_collapse_result and proposals are all called from the core - yet it
    never writes echo_index directly; every mutation goes through a Nova
    method. The structural guarantee is enforced by
    tests/invariants/test_ruling1_single_writer.py, which SCANS `echo_index`
    across all of src/ (owner: src/expansion/nova.py). This asserts the index
    only ever grew through Nova under a real driven pass."""
    aurea = AureaCore()
    assert isinstance(aurea.nova, NovaEngine)
    before = len(aurea.nova.echo_index)
    _seed_strain(aurea, STRAINED)
    aurea._nova_cycle([])
    assert len(aurea.nova.echo_index) == before + 1, "grew by exactly one, via Nova"
