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

No wiring is exercised IN THIS FILE - it pins the organ in isolation, and that
is its scope, not a claim about Nova. (This line used to read "Stage 1 has
none"; Nova has been wired since 2026-07-24 - see `test_nova_stage2a.py` and
`test_nova_stage2b.py`.) DO NOT weaken these tests.
They pin an architect ruling.

RULING 20 (2026-07-25) MOVED THE FIXTURE, NOT THE ASSERTIONS. An echo may now
back a proposal for doctrine D only if it erupted from D's OWN strain
(`origin_kind == "doctrine_strain"` and `origin_id == D`). The two lifecycle
helpers below used to erupt a SCAR-origin echo and then propose for "D-001" -
a pairing Ruling 20 refuses outright, and refuses correctly: `Δ77` is a scar
id, not a doctrine address, so that echo never had authorship standing over
D-001 in the first place. The helpers now erupt from D-001's strain. Every
assertion in this file is unchanged and every one still binds; only the
echo's ORIGIN moved, because the RULING moved. Recorded here for the same
reason Ruling 14's supersession was recorded in test_nova_stage2b.py: a
changed pinned test must say which ruling changed it.

The one assertion edit is in test_emitted_proposal_is_fully_provenance_mapped,
where a hardcoded `("scar", echo.origin_id)` became
`(echo.origin_kind, echo.origin_id)` - derived from the echo instead of
restating a literal, which is strictly stronger.
"""

import copy

import pytest

from src.expansion.nova import (
    FERMENTATION_ELIGIBILITY_CYCLES,
    FermentationStatus,
    NovaEcho,
    NovaEngine,
    ProvenanceOverwriteViolation,
    StoreFragment,
    UngroundedEchoViolation,
    UngroundedFragmentViolation,
)
from src.utils.models import Doctrine


def _mutated_engine(scar_links=("Δ77",)):
    """Engine holding one echo taken honestly through the full lifecycle:
    erupt -> activate -> ferment to eligibility -> succeeded collapse.

    Ruling 20: the echo erupts from D-001's OWN strain, which is what gives
    it standing to author for D-001 below. It still carries the real scar Δ77
    as its fracture."""
    engine = NovaEngine()
    echo = engine.erupt("doctrine_strain", "D-001", symbolic_domain="recursion",
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
                                 (echo.origin_kind, echo.origin_id)}

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


# =====================================================================
# Ruling 13 (2026-07-22): an echo is SPENT when it authors
# =====================================================================

def _mutate_second_echo(engine, origin_id="D-001", scar_links=("Δ88",)):
    """Take a second echo honestly through the lifecycle on a live engine.

    Ruling 20: same doctrine origin as the first echo (that is the point of
    R13-5 - consumption is per-ECHO), but DIFFERENT survived material (Δ88
    rather than Δ77)."""
    echo = engine.erupt("doctrine_strain", origin_id, scar_links=list(scar_links))
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(echo.id, success=True)
    return echo


# ---------------------------------------------------------------------
# (R13-1) one echo, one proposal, EVER
# ---------------------------------------------------------------------

def test_one_echo_one_proposal_ever():
    """The same call that emitted once emits nothing the second time - the
    echo is spent, and the unbacked doctrine is refused legibly."""
    engine, echo = _mutated_engine()
    fragments = _doctrine_fragments("D-001")

    first = engine.proposals(fragments)
    assert set(first) == {"D-001"}
    assert echo.spent_on == first["D-001"].id
    assert echo.spent_at is not None
    assert echo.is_spent

    second = engine.proposals(fragments)
    assert second == {}, "a spent echo may never back another proposal"
    refusal = engine.refusals[-1]
    assert refusal["action"] == "proposals"
    assert refusal["doctrine_id"] == "D-001"


# ---------------------------------------------------------------------
# (R13-2) the first emission's provenance survives VERBATIM
# ---------------------------------------------------------------------

def test_first_provenance_survives_verbatim_across_subsequent_calls():
    engine, echo = _mutated_engine()
    first = engine.proposals(_doctrine_fragments("D-001"))
    proposal_id = first["D-001"].id
    original = copy.deepcopy(engine.proposal_provenance[proposal_id])

    # Subsequent activity: refused re-emission, a second echo authoring for
    # the same doctrine, more fermentation.
    engine.proposals(_doctrine_fragments("D-001"))
    _mutate_second_echo(engine)
    engine.proposals(_doctrine_fragments("D-001"))

    assert engine.proposal_provenance[proposal_id] == original, (
        "the exact map, byte for byte - a forensic record is never rewritten")


# ---------------------------------------------------------------------
# (R13-3) append-only: an existing key RAISES
# ---------------------------------------------------------------------

def test_provenance_overwrite_raises():
    engine, _ = _mutated_engine()
    out = engine.proposals(_doctrine_fragments("D-001"))
    proposal_id = out["D-001"].id

    with pytest.raises(ProvenanceOverwriteViolation):
        engine._append_provenance(proposal_id, [{"store": "scars",
                                                 "record_id": "Δ99"}])
    # The raise protected the record - nothing changed.
    assert engine.proposal_provenance[proposal_id] != [
        {"store": "scars", "record_id": "Δ99"}]


# ---------------------------------------------------------------------
# (R13-4) the closed-enum pin: exactly the four canon members
# ---------------------------------------------------------------------

def test_fermentation_status_has_exactly_the_four_canon_members():
    """Consumption is a FIELD, not a status. If a fifth member (SPENT,
    CONSUMED, ...) ever appears here, someone re-made the Ruling-7 mistake
    in Nova's enum. The enum is canon-closed (5a:1118-1123)."""
    assert {s.value for s in FermentationStatus} == {
        "dormant", "active", "decaying", "mutated"}


# ---------------------------------------------------------------------
# (R13-5) the anti-over-narrow pin: consumption is per-ECHO
# ---------------------------------------------------------------------

def test_second_distinct_echo_backs_a_proposal_for_the_same_doctrine():
    """MUST STAY GREEN. Different survived material legitimately bears on
    the same belief - spending echo A must not bar echo B from proposing
    for the same strained doctrine. Each proposal gates independently at
    DEE. If this fails, consumption was over-narrowed to per-doctrine."""
    engine, first_echo = _mutated_engine()
    first = engine.proposals(_doctrine_fragments("D-001"))
    assert set(first) == {"D-001"}

    second_echo = _mutate_second_echo(engine)
    second = engine.proposals(_doctrine_fragments("D-001"))

    assert set(second) == {"D-001"}, (
        "a distinct MUTATED echo still proposes for the same doctrine")
    assert second["D-001"].id != first["D-001"].id
    assert second_echo.spent_on == second["D-001"].id
    assert first_echo.spent_on == first["D-001"].id, "first echo untouched"
    # Both forensic records coexist - append-only means both survive.
    assert first["D-001"].id in engine.proposal_provenance
    assert second["D-001"].id in engine.proposal_provenance


# ---------------------------------------------------------------------
# (R13-6) consumption is not deletion: the spent record is CARRIED
# ---------------------------------------------------------------------

def test_spent_echo_remains_in_index_with_status_mutated():
    engine, echo = _mutated_engine()
    engine.proposals(_doctrine_fragments("D-001"))

    assert echo.is_spent
    assert echo.id in engine.echo_index, "consumption is not deletion"
    assert engine.echo_index[echo.id] is echo
    assert echo.status is FermentationStatus.MUTATED, (
        "spent is a fact about authorship - the fermentation state it "
        "earned by surviving collapse is not revoked")
