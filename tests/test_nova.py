"""
test_nova.py - Ruling 12, Stage 1: the Nova Engine v1 organ, gate by gate.

These tests pin the grounding contract (CLAUDE.md 1 row 12):
  G1  no echo without a typed, real origin - construction raises;
  G2  proposals only from MUTATED + scar-linked echoes;
  G3  every fragment of a proposal traces to a supplied store record id;
  G5  a suppressed cycle advances nothing and refuses legibly;
  and the overruled-line boundary: TIMER -> ELIGIBILITY ONLY - there is no
  code path from elapsed cycles to MUTATED. The only writer of MUTATED is
  record_collapse_result(success=True) on an ELIGIBLE echo.

No wiring is exercised here - Stage 1 has none. DO NOT weaken these tests.
They pin an architect ruling.
"""

import pytest

from src.expansion.nova import (
    FERMENTATION_ELIGIBILITY_CYCLES,
    FermentationStatus,
    NovaEcho,
    NovaEngine,
    StoreFragment,
    UngroundedEchoViolation,
    UngroundedFragmentViolation,
)
from src.utils.models import Doctrine


def _mutated_engine(scar_links=("Δ77",)):
    """Engine holding one echo taken honestly through the full lifecycle:
    erupt -> activate -> ferment to eligibility -> succeeded collapse."""
    engine = NovaEngine()
    echo = engine.erupt("scar", "Δ77", symbolic_domain="recursion",
                        scar_links=list(scar_links))
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(echo.id, success=True,
                                         detail="survived filtration")
    assert echo.status is FermentationStatus.MUTATED
    return engine, echo


def _doctrine_fragments(doctrine_id="D-001"):
    return {
        doctrine_id: [
            StoreFragment(store="doctrines", record_id=doctrine_id,
                          content="Scars shape future collapse"),
            StoreFragment(store="scars", record_id="Δ77",
                          content="recursion trap survived"),
        ],
    }


# ---------------------------------------------------------------------
# (1) G1: no origin, no echo - the refusal is the enforcement
# ---------------------------------------------------------------------

@pytest.mark.parametrize("origin_kind,origin_id", [
    ("scar", ""),                       # empty origin id
    ("scar", "   "),                    # whitespace is not a record
    ("vibes", "R-001"),                 # unknown kind - not a canon source
    ("", "R-001"),                      # no kind at all
    ("doctrine", "D-001"),              # near-miss of a canon kind
])
def test_ungrounded_echo_construction_raises(origin_kind, origin_id):
    with pytest.raises(UngroundedEchoViolation):
        NovaEcho(id="NE-XXXX", origin_kind=origin_kind, origin_id=origin_id)


def test_erupt_cannot_subtract_from_the_gate():
    """The engine's eruption path goes through the same constructor - an
    origin-less eruption raises and the index gains nothing."""
    engine = NovaEngine()
    with pytest.raises(UngroundedEchoViolation):
        engine.erupt("echonet_verdict", "")
    assert engine.echo_index == {}


def test_grounded_construction_admits_every_canon_kind():
    engine = NovaEngine()
    for kind in ("scar", "echonet_verdict", "csa_fragment",
                 "sbsre_abort", "doctrine_strain"):
        echo = engine.erupt(kind, f"{kind}-record-1")
        assert echo.status is FermentationStatus.DORMANT
    assert len(engine.echo_index) == 5


# ---------------------------------------------------------------------
# (2) the overruled line: elapsed cycles NEVER yield MUTATED
# ---------------------------------------------------------------------

def test_timer_raises_eligibility_only_never_mutated():
    """Age an echo far past the threshold. Eligible: yes. MUTATED: never.
    If this test ever fails toward MUTATED, someone implemented 5a:1113's
    literal `Timer -> Mutation` line - which is overruled. Revert them."""
    engine = NovaEngine()
    echo = engine.erupt("doctrine_strain", "D-001")

    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES * 10):
        engine.cycle(suppressed=False)

    assert echo.collapse_eligible is True
    assert echo.status is FermentationStatus.ACTIVE, (
        "elapsed time may make an echo ELIGIBLE for collapse - it may never "
        "BE the collapse")
    assert echo.collapse_attempts == [], "no attempt was fabricated by aging"


def test_eligibility_needs_the_full_horizon():
    engine = NovaEngine()
    echo = engine.erupt("scar", "Δ77")
    # First cycle only activates (DORMANT -> ACTIVE); aging starts after.
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES):
        engine.cycle(suppressed=False)
    assert echo.fermentation_cycles == FERMENTATION_ELIGIBILITY_CYCLES - 1
    assert echo.collapse_eligible is False
    engine.cycle(suppressed=False)
    assert echo.collapse_eligible is True


# ---------------------------------------------------------------------
# (3) MUTATED has exactly one writer: a succeeded collapse on an ELIGIBLE echo
# ---------------------------------------------------------------------

def test_succeeded_collapse_on_eligible_echo_mutates():
    engine, echo = _mutated_engine()
    assert echo.collapse_attempts[-1]["success"] is True
    assert len(engine.scar_requests) == 1, (
        "scar fusion is a parked REQUEST to ScarLogicCore (G4), not a write")
    assert engine.scar_requests[0]["echo_id"] == echo.id


def test_failed_collapse_decays_and_parks_a_csa_request():
    engine = NovaEngine()
    echo = engine.erupt("csa_fragment", "CSA-009")
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(echo.id, success=False)
    assert echo.status is FermentationStatus.DECAYING
    assert len(engine.csa_requests) == 1
    assert engine.csa_requests[0]["echo_id"] == echo.id


def test_collapse_result_on_ineligible_echo_is_refused_state_unchanged():
    """A fresh echo has not fermented through its horizon - it has not earned
    a collapse verdict in EITHER direction. Refused, legibly, no mutation."""
    engine = NovaEngine()
    echo = engine.erupt("sbsre_abort", "SBSRE-0001")

    assert engine.record_collapse_result(echo.id, success=True) is False
    assert echo.status is FermentationStatus.DORMANT, "state unchanged"
    assert echo.collapse_attempts == []
    assert engine.scar_requests == []
    refusal = engine.refusals[-1]
    assert refusal["action"] == "record_collapse_result"
    assert "not collapse-eligible" in refusal["reason"]


def test_collapse_result_on_unknown_echo_is_refused():
    engine = NovaEngine()
    assert engine.record_collapse_result("NE-9999", success=True) is False
    assert engine.refusals[-1]["reason"] == "no such echo in the Nova Echo Index"


# ---------------------------------------------------------------------
# (4) G2: the emission gate - MUTATED and scar-linked, nothing less
# ---------------------------------------------------------------------

def test_no_proposals_from_active_decaying_or_unattempted_echoes():
    engine = NovaEngine()
    active = engine.erupt("scar", "Δ10", scar_links=["Δ10"])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES * 2):
        engine.cycle(suppressed=False)   # eligible, but never attempted
    decayed = engine.erupt("csa_fragment", "CSA-001", scar_links=["Δ11"])
    decayed.status = FermentationStatus.DECAYING

    assert active.collapse_eligible is True
    assert engine.proposals(_doctrine_fragments()) == {}, (
        "eligibility is not mutation; decay is not mutation - no doctrine "
        "may be proposed from either")
    assert engine.refusals[-1]["action"] == "proposals"


def test_no_proposals_from_a_mutated_echo_without_scar_linkage():
    """MUTATED alone does not clear G2 - 'Unverified Echoes may not write
    doctrine' means unverified BY SCAR: no scar linkage, no proposal."""
    engine, echo = _mutated_engine(scar_links=())
    assert echo.status is FermentationStatus.MUTATED
    assert echo.scar_links == []

    assert engine.proposals(_doctrine_fragments()) == {}
    assert "no MUTATED, scar-linked echo" in engine.refusals[-1]["reason"]


def test_proposal_refused_without_the_strained_doctrines_own_material():
    """Recombination requires the material being recombined: fragments that
    omit the target doctrine's own record yield no proposal."""
    engine, _ = _mutated_engine()
    only_scar = {"D-001": [StoreFragment(store="scars", record_id="Δ77",
                                         content="residue")]}
    assert engine.proposals(only_scar) == {}
    assert "strained doctrine itself" in engine.refusals[-1]["reason"]


# ---------------------------------------------------------------------
# (5) G3: every piece of an emitted proposal traces to a store record
# ---------------------------------------------------------------------

def test_untraceable_fragment_is_refused_at_construction():
    for store, record_id in (("", "R-1"), ("scars", ""), ("  ", "R-1"),
                             ("scars", "   ")):
        with pytest.raises(UngroundedFragmentViolation):
            StoreFragment(store=store, record_id=record_id, content="text")


def test_emitted_proposal_is_fully_provenance_mapped():
    """The happy path, end to end - and every piece of it traceable."""
    engine, echo = _mutated_engine()
    fragments = _doctrine_fragments("D-001")

    out = engine.proposals(fragments)

    assert set(out) == {"D-001"}, "keyed by the strained doctrine's id"
    proposal = out["D-001"]
    assert isinstance(proposal, Doctrine), (
        "the models.py Doctrine - no parallel doctrine shape")

    # The provenance map exists and covers: every supplied fragment, the
    # echo itself, and the echo's origin record. Nothing else.
    prov = engine.proposal_provenance[proposal.id]
    supplied = {(f.store, f.record_id) for f in fragments["D-001"]}
    mapped = {(p["store"], p["record_id"]) for p in prov}
    assert mapped == supplied | {("nova_echo_index", echo.id),
                                 ("scar", echo.origin_id)}

    # Every content piece of the new form carries its inline [store:id] tag.
    for piece in proposal.description.split(" + "):
        store, _, rest = piece.partition(":")
        assert store.startswith("[") and "]" in rest, (
            f"untagged piece in proposal content: {piece!r}")
        assert (store.lstrip("["), rest.split("]")[0]) in supplied, (
            f"piece traces to nothing supplied: {piece!r}")

    # Structural fields trace too.
    assert proposal.mutation_lineage == ["D-001", echo.id]
    assert "Δ77" in proposal.scar_links
    assert proposal.status == "proposed", "a proposal is not yet doctrine"
    assert f"prov:nova_echo_index:{echo.id}" in proposal.tca_tags


def test_single_echo_engine_backs_at_most_one_proposal_per_echo():
    """Engine v1 is single-echo by ruling: one mutated echo cannot fan out
    across every strained doctrine offered."""
    engine, _ = _mutated_engine()
    fragments = {}
    for did in ("D-001", "D-002"):
        fragments[did] = [
            StoreFragment(store="doctrines", record_id=did, content="form"),
            StoreFragment(store="scars", record_id="Δ77", content="mark"),
        ]
    out = engine.proposals(fragments)
    assert len(out) == 1, "one qualifying echo -> one proposal"
    assert engine.refusals[-1]["action"] == "proposals", (
        "the unbacked doctrine is refused legibly, not silently skipped")


# ---------------------------------------------------------------------
# (6) G5: a suppressed cycle advances NOTHING and refuses legibly
# ---------------------------------------------------------------------

def test_suppressed_cycle_advances_nothing_and_records_refusal():
    engine = NovaEngine()
    dormant = engine.erupt("scar", "Δ20")
    aging = engine.erupt("scar", "Δ21")
    engine.cycle(suppressed=False)          # aging: DORMANT -> ACTIVE
    cycles_before = aging.fermentation_cycles
    dormant.status = FermentationStatus.DORMANT  # hold one back at DORMANT

    result = engine.cycle(suppressed=True, source="RACM")

    assert result == []
    assert dormant.status is FermentationStatus.DORMANT, "no activation"
    assert aging.fermentation_cycles == cycles_before, "no aging"
    refusal = engine.refusals[-1]
    assert refusal["action"] == "cycle"
    assert refusal["source"] == "RACM"
    assert "suppression" in refusal["reason"]


def test_suppression_does_not_kill_the_engine_afterward():
    """Refusal is per-cycle, not a latch: the next unsuppressed cycle runs."""
    engine = NovaEngine()
    echo = engine.erupt("scar", "Δ22")
    engine.cycle(suppressed=True)
    engine.cycle(suppressed=False)
    assert echo.status is FermentationStatus.ACTIVE
