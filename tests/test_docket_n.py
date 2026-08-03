"""
test_docket_n.py - Docket N (Rulings 20-25): the SEAMS between the gates.

Nova was declared "DONE as an organ" and every gate G1-G5 does work exactly
as pinned. These six defects lived BETWEEN the gates, where no single gate is
responsible - and 161 green missed all of them because no test ever drove the
multi-input configuration each one requires. That is the Docket K
coverage-distribution finding in a new shape: not "which organs are tested"
but "which CONFIGURATIONS are."

  R20  origin-matched echo selection. An echo may back a proposal for D only
       if it erupted from D's OWN strain. THE TEST DRIVES TWO SIMULTANEOUSLY
       STRAINED DOCTRINES - the configuration nothing else in the suite
       creates - and asserts the thing that actually matters: the emitted
       scar_links carry NO scar from the other doctrine's collapse. The
       damage was lineage contamination, not merely misattribution.
  R21  backing-echo lineage. CMTE has always admitted echo_origin as an
       OR-alternative to scar_links; _approve never read it, so a scarless
       doctrine with a legitimate survived echo passed CMTE, got "", and was
       refused by SAE. Ruling 14's positive half was dead code.
  R24  SAE pre-flight. Three checks before the FIRST write, because atomicity
       comes from making failure impossible - never from undoing it. There is
       deliberately NO rollback path: un-fossilizing is mechanically the
       revival Ruling 18 forbids and Ruling 19 settled.
  R25  structural-exception taxonomy. A guard whose firing is indistinguishable
       from a typo is not enforcement. Driven by a REAL guard
       (ProvenanceOverwriteViolation) firing through the REAL pipeline.
  R22  scar snapshot-on-read. The doctrine store has an ownership BOUNDARY;
       the scar store had a CONVENTION.
  R23  DMW overflow refusal. The 32-cap is correct and does not move. The
       SILENCE was the defect.

Every test here was watched RED under the exact defect before it went green
(Ruling 17: no lexical pins, no proxies). DO NOT weaken them.
"""

from datetime import datetime

import pytest

from src.aurea_core import AureaCore
from src.doctrine.codex import Codex, CodexWriteViolation
from src.doctrine.dee import (DEE, DMW_QUEUE_MAX, MutationTrigger, PressureFlag,
                              Verdict, _Watched)
from src.expansion.nova import (FERMENTATION_ELIGIBILITY_CYCLES,
                                FermentationStatus, NovaEngine, StoreFragment)
from src.expansion.sae import SAE, MutationClass, MutationPreflightViolation
from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.models import Doctrine
# RULING 45 (2026-07-28), Ruling-14 precedent. The FOUR `mutate_doctrine` calls
# below each gained `proof=minimal_proof(...)`:
#
#     OLD: sae.mutate_doctrine("D-live", same_id, collapse_lineage="Δ-1")
#     NEW: the same call, plus `proof=minimal_proof("<what forced it>")`.
#
# WHY: `proof` is REQUIRED and has no default, because an implicit default proof
# would be a fabricated argument (Ruling 45 Part 2.2). A proof-less call is a
# TypeError, which is the enforcement.
#
# NOT A WEAKENING. Every assertion in all four tests is unchanged in force and in
# spelling - Ruling 24's three preflight refusals still fire, and the legitimate
# path still executes. The helper's `preserved_invariants` default is ALL-ABSENT,
# which is the TRUTHFUL record for a call that drives SAE directly and therefore
# never ran CMTE; it claims nothing these tests did not do.
from tests.proof_support import minimal_proof

# Two REAL seed doctrines under real strain, with DISJOINT scar sets - which
# is what makes the contamination assertion sharp. Verified against
# data/doctrines.json: A carries {Δ61, Δ17}, B carries {Δ42, Δ88, Δ31}.
DOCTRINE_A = "Doctrine-3"
DOCTRINE_B = "Doctrine-0.1"


def _seed_strain(aurea, doctrine_id):
    """The one controlled seam, identical to test_nova_stage2a/2b's pattern:
    a real sustained-strain slot in DEE's DMW watch."""
    aurea.dee.dmw.queue[doctrine_id] = _Watched(
        doctrine_id=doctrine_id, pressure=0.9, sustained_cycles=3)


def _authoring_echo_ids(engine, proposal_id):
    """Which echo the append-only provenance map records as authoring a
    proposal - read straight off Nova's forensic record, not off the
    proposal's own mutation_lineage (an ordinary field any author could set)."""
    return [p["record_id"]
            for p in engine.proposal_provenance.get(proposal_id, [])
            if p["store"] == "nova_echo_index"]


# =====================================================================
# RULING 20 - origin-matched echo selection
# =====================================================================

def _two_strained_doctrines():
    """TWO simultaneously strained doctrines, each with its OWN MUTATED,
    scar-linked echo. This configuration is what no existing test creates.

    Doctrine A mutates ORGANICALLY end to end: its own content genuinely
    SCARS through the real EchoNet, so _nova_route_collapse records a
    survived collapse with no verdict mocked anywhere.

    Doctrine B's collapse verdict is the ONE controlled seam. Verified by
    execution: of the eight seed doctrines, ONLY Doctrine-3's own content
    SCARS through the real EchoNet (the rest come back suspended or
    confirmed), so a second organic MUTATED echo does not exist to be had.
    The outcome is therefore recorded through record_collapse_result - the
    CANONICAL and only writer of MUTATED, the same seam PIN 3 of
    test_nova_stage2b.py drives. Nothing is fabricated: the echo erupted
    from B's real strain, carries B's real scar links, and fermented through
    the real horizon before any verdict was recorded.
    """
    aurea = AureaCore()
    # Eruption order (A first) is DELIBERATELY the reverse of doctrine sort
    # order ("Doctrine-0.1" < "Doctrine-3"), so the two orderings the old
    # pop(0) conflated actually disagree. With them aligned, the defect is
    # invisible - which is precisely how it survived 161 green.
    _seed_strain(aurea, DOCTRINE_A)
    _seed_strain(aurea, DOCTRINE_B)

    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 4):
        aurea._nova_cycle([])

    echo_a = next(e for e in aurea.nova.echo_index.values()
                  if e.origin_id == DOCTRINE_A)
    echo_b = next(e for e in aurea.nova.echo_index.values()
                  if e.origin_id == DOCTRINE_B)

    assert echo_a.status is FermentationStatus.MUTATED, "A survived organically"
    assert echo_a.id < echo_b.id, "A's echo is the older id - the pop(0) winner"
    assert aurea.nova.record_collapse_result(
        echo_b.id, success=True, detail="controlled seam: survived collapse")
    assert echo_b.status is FermentationStatus.MUTATED
    assert echo_a.scar_links and echo_b.scar_links
    assert not set(echo_a.scar_links) & set(echo_b.scar_links), (
        "the vehicles must have disjoint scars or the contamination "
        "assertion below proves nothing")
    return aurea, echo_a, echo_b


def test_each_proposal_is_authored_by_its_own_doctrines_echo():
    """RULING 20, THE PIN. Two strained doctrines, two qualifying echoes of
    DIFFERENT origins: each proposal must be backed by the echo that erupted
    from its OWN doctrine's strain.

    RED under the defect: `qualifying.pop(0)` drew from a globally id-sorted
    list while the caller iterated `sorted(fragments)` - two orderings with no
    relationship - so Doctrine-0.1's proposal was authored by Doctrine-3's
    echo and vice versa.
    """
    aurea, echo_a, echo_b = _two_strained_doctrines()
    signals = {DOCTRINE_A: {"pressure": 0.9, "drpe": True},
               DOCTRINE_B: {"pressure": 0.9, "drpe": True}}

    proposals = aurea._nova_proposals(signals)

    assert proposals is not None and set(proposals) == {DOCTRINE_A, DOCTRINE_B}
    assert aurea._backing_echo(proposals[DOCTRINE_A]) is echo_a, (
        "A's proposal must be authored by A's own echo")
    assert aurea._backing_echo(proposals[DOCTRINE_B]) is echo_b, (
        "B's proposal must be authored by B's own echo")
    # The structural address records the same pairing.
    assert proposals[DOCTRINE_A].mutation_lineage == [DOCTRINE_A, echo_a.id]
    assert proposals[DOCTRINE_B].mutation_lineage == [DOCTRINE_B, echo_b.id]


def test_a_mispaired_echo_cannot_contaminate_scar_lineage():
    """THE PART THAT MATTERS MOST. proposals() merges the backing echo's
    scar_links into the emitted proposal - so a mispaired echo writes scars
    from a DIFFERENT doctrine's collapse into the successor's lineage. That is
    lineage forgery by accident: the successor would carry visible evidence of
    a fracture it never survived, and SAE would then hand that scar id to the
    Codex as the mutation's collapse lineage.

    RED under the defect: Doctrine-0.1's proposal carried Δ17 and Δ61 -
    Doctrine-3's scars.
    """
    aurea, echo_a, echo_b = _two_strained_doctrines()
    a_scars, b_scars = set(echo_a.scar_links), set(echo_b.scar_links)
    signals = {DOCTRINE_A: {"pressure": 0.9, "drpe": True},
               DOCTRINE_B: {"pressure": 0.9, "drpe": True}}

    proposals = aurea._nova_proposals(signals)

    assert not set(proposals[DOCTRINE_B].scar_links) & a_scars, (
        f"lineage contamination: B's proposal carries A's scars "
        f"{sorted(set(proposals[DOCTRINE_B].scar_links) & a_scars)}")
    assert not set(proposals[DOCTRINE_A].scar_links) & b_scars, (
        f"lineage contamination: A's proposal carries B's scars "
        f"{sorted(set(proposals[DOCTRINE_A].scar_links) & b_scars)}")
    # Not vacuous: each proposal DOES carry its own doctrine's real scars.
    assert b_scars <= set(proposals[DOCTRINE_B].scar_links)
    assert a_scars <= set(proposals[DOCTRINE_A].scar_links)


def test_no_matching_echo_ferments_it_never_substitutes():
    """No qualifying echo for D means D FERMENTS - a substitute is never
    accepted. The refusal is recorded legibly, not silently skipped."""
    engine = NovaEngine()
    echo = engine.erupt("doctrine_strain", "D-001", scar_links=["Δ77"])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(echo.id, success=True)

    # D-002 is strained and fully supplied - but nothing erupted from ITS
    # strain. The only qualifying echo in the index belongs to D-001.
    out = engine.proposals({"D-002": [
        StoreFragment(store="doctrines", record_id="D-002", content="form"),
        StoreFragment(store="scars", record_id="Δ77", content="mark")]})

    assert out == {}, "a foreign echo may not stand in for the missing one"
    assert echo.is_spent is False, "and the foreign echo was not consumed"
    refusal = engine.refusals[-1]
    assert refusal["action"] == "proposals"
    assert refusal["doctrine_id"] == "D-002"
    assert "origin" in refusal["reason"].lower()


def test_non_doctrine_strain_origins_are_refused_legibly():
    """The other four canon origin kinds (scar, echonet_verdict, csa_fragment,
    sbsre_abort) have NO defined doctrine-authorship semantics. They may not
    back a doctrine proposal until that is ruled - and the exclusion is
    RECORDED, not a silent skip. Here the echo's origin_id even matches the
    doctrine id exactly; the kind alone disqualifies it."""
    engine = NovaEngine()
    echo = engine.erupt("scar", "D-001", scar_links=["Δ77"])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(echo.id, success=True)
    assert echo.status is FermentationStatus.MUTATED and echo.scar_links

    out = engine.proposals({"D-001": [
        StoreFragment(store="doctrines", record_id="D-001", content="form")]})

    assert out == {}, "an unruled origin kind may not author doctrine"
    assert not echo.is_spent
    assert any(r.get("echo_id") == echo.id and "scar" in r["reason"]
               for r in engine.refusals), "the exclusion is legible"


def test_two_echoes_sharing_an_origin_resolve_deterministically():
    """Ruling 13 is NOT over-narrowed by Ruling 20: consumption is per-ECHO,
    so two distinct MUTATED echoes may both bear on the same doctrine. When
    they do, selection is deterministic - oldest by id first, then the next."""
    engine = NovaEngine()
    first = engine.erupt("doctrine_strain", "D-001", scar_links=["Δ77"])
    second = engine.erupt("doctrine_strain", "D-001", scar_links=["Δ88"])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        engine.cycle(suppressed=False)
    assert engine.record_collapse_result(first.id, success=True)
    assert engine.record_collapse_result(second.id, success=True)
    assert first.id < second.id

    frags = {"D-001": [StoreFragment(store="doctrines", record_id="D-001",
                                     content="form")]}
    one = engine.proposals(frags)
    assert _authoring_echo_ids(engine, one["D-001"].id) == [first.id]
    two = engine.proposals(frags)
    assert _authoring_echo_ids(engine, two["D-001"].id) == [second.id]
    assert one["D-001"].id != two["D-001"].id


# =====================================================================
# RULING 21 - the backing echo's scar IS the execution lineage
# =====================================================================

SCARLESS = "D-scarless"          # deliberately NOT an AVT.* id: §10.G excludes those


@pytest.fixture
def scarless_assembly(tmp_path):
    """A real Codex / SAE / DEE / Nova / ScarLogicCore over tmp paths, holding
    ONE scarless doctrine.

    Assembled directly rather than through AureaCore because no seed doctrine
    can serve: every scarless id in data/doctrines.json is an AVT.* id, and
    §10.G excludes those from self-mutation entirely - so the path Ruling 21
    unblocks has no vehicle in the seed set. This is a real store with real
    components; only the contents are chosen.
    """
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.seed(Doctrine(id=SCARLESS, name="Scarless Belief", is_seed=True,
                        description="A belief with no visible fracture.",
                        created_at=datetime.now()))
    codex.seal()
    assert codex.get(SCARLESS).scar_links == [], "the vehicle must be scarless"

    sae = SAE(codex=codex)
    dee = DEE(codex=codex, sae=sae)
    scar_core = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    scar = scar_core.form_scar(origin="test-collapse", type="contradiction",
                               weight=4.0, description="the real fracture")
    return codex, sae, dee, NovaEngine(), scar


def _survived_proposal(nova, scar, doctrine_id=SCARLESS):
    """A real MUTATED, scar-linked echo taken through the full lifecycle, and
    the proposal it authors. The scar id is a REAL record in the scar store."""
    echo = nova.erupt("doctrine_strain", doctrine_id, scar_links=[scar.id])
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 1):
        nova.cycle(suppressed=False)
    assert nova.record_collapse_result(echo.id, success=True)
    proposals = nova.proposals({doctrine_id: [
        StoreFragment(store="doctrines", record_id=doctrine_id,
                      content="A belief with no visible fracture."),
        StoreFragment(store="scars", record_id=scar.id,
                      content="the real fracture")]})
    assert proposals[doctrine_id].scar_links == [scar.id]
    return echo, proposals


def test_scarless_doctrine_mutates_on_its_backing_echos_scar(scarless_assembly):
    """RULING 21, THE PIN. A scarless doctrine whose eligibility comes from
    echo_origin executes with the BACKING ECHO's scar as its collapse lineage.

    RED under the defect: `lineage = doctrine.scar_links[0] if ... else ""`
    handed SAE an empty string, SAE raised AVT.017, DEE converted the refusal
    to FERMENT - so CMTE's own second OR-branch could never reach execution.
    The belief was eligible and could not evolve.
    """
    codex, sae, dee, nova, scar = scarless_assembly
    _, proposals = _survived_proposal(nova, scar)

    dee.dmw.queue[SCARLESS] = _Watched(doctrine_id=SCARLESS, pressure=0.9,
                                       sustained_cycles=3)
    rulings = dee.cycle(signals={SCARLESS: {"pressure": 0.9, "drpe": True}},
                        proposals=proposals,
                        context={SCARLESS: {"echo_origin": True}})

    ours = next(r for r in rulings if r.doctrine_id == SCARLESS)
    assert ours.verdict is Verdict.APPROVED, ours.reason
    assert ours.executed_by == "SAE", (
        "the mutation must actually EXECUTE - Ruling 14's positive half is "
        "dead code if this is only APPROVED")
    assert sae.history[-1].collapse_lineage == scar.id, (
        "the recorded lineage is the backing echo's REAL scar")
    assert codex.get_fossil(SCARLESS) is not None, "the ancestor ⊗-fossilized"


def test_empty_lineage_is_still_refused_by_sae(scarless_assembly):
    """AVT.017 is NOT widened. A doctrine with no scar AND no backing-echo
    scar still yields "" and is still refused - that guard is correct and
    stays. Ruling 21 makes AVT.017 SATISFIABLE by the second source CMTE
    always named; it does not soften it."""
    codex, sae, dee, nova, scar = scarless_assembly
    bare = Doctrine(id=f"{SCARLESS}::bare", name="no lineage anywhere",
                    description="proposed", created_at=datetime.now())
    assert bare.scar_links == []

    dee.dmw.queue[SCARLESS] = _Watched(doctrine_id=SCARLESS, pressure=0.9,
                                       sustained_cycles=3)
    rulings = dee.cycle(signals={SCARLESS: {"pressure": 0.9, "drpe": True}},
                        proposals={SCARLESS: bare},
                        context={SCARLESS: {"echo_origin": True}})

    ours = next(r for r in rulings if r.doctrine_id == SCARLESS)
    assert ours.verdict is Verdict.FERMENT
    assert ours.executed_by is None
    assert "AVT.017" in ours.reason, ours.reason
    assert codex.get(SCARLESS) is not None, "the belief is untouched"


def test_the_doctrines_own_scar_still_wins_when_it_has_one(scarless_assembly):
    """Resolution ORDER, pinned: the doctrine's OWN scar first. Ruling 21 adds
    a FALLBACK, it does not re-source a scarred doctrine's lineage."""
    codex, sae, dee, nova, scar = scarless_assembly
    own = Doctrine(id="D-scarred", name="Scarred Belief",
                   description="a visible fracture", scar_links=["Δ-own"],
                   created_at=datetime.now())
    codex.doctrines[own.id] = own          # store fixture, not a write path

    echo, proposals = _survived_proposal(nova, scar, doctrine_id=own.id)
    assert proposals[own.id].scar_links == [scar.id], "the echo offers another"

    dee.dmw.queue[own.id] = _Watched(doctrine_id=own.id, pressure=0.9,
                                     sustained_cycles=3)
    dee.cycle(signals={own.id: {"pressure": 0.9, "drpe": True}},
              proposals=proposals, context={own.id: {}})

    assert sae.history[-1].collapse_lineage == "Δ-own", (
        "a scarred doctrine's lineage is its OWN scar, not the echo's")


# =====================================================================
# RULING 24 - SAE pre-flight. Failure is made impossible, never undone.
# =====================================================================

@pytest.fixture
def executor(tmp_path):
    """Real Codex + real SAE over a tmp store holding one live doctrine."""
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.seed(Doctrine(id="D-live", name="Live", is_seed=True,
                        description="live doctrine", created_at=datetime.now()))
    codex.seal()
    return codex, SAE(codex=codex)


def test_successor_may_not_wear_its_ancestors_id(executor):
    """(i) A successor is a NEW identity. Nothing returns wearing the dead
    thing's name (Ruling 19's philosophy, made structural).

    RED under the defect: fossilize() moved D-live into fossils, then commit()
    hit Ruling 18's guard and raised - leaving the ancestor FOSSILIZED WITH NO
    SUCCESSOR INSTALLED. The doctrine vanished. Pre-Ruling-18 it was worse: id
    live and fossil simultaneously, durable across reload.
    """
    codex, sae = executor
    same_id = Doctrine(id="D-live", name="same id", description="successor",
                       created_at=datetime.now())

    with pytest.raises(MutationPreflightViolation):
        sae.mutate_doctrine("D-live", same_id, collapse_lineage="Δ-1",
                            proof=minimal_proof("Ruling 24 preflight (i) probe"))

    assert codex.get("D-live") is not None, "the ancestor did NOT vanish"
    assert codex.get_fossil("D-live") is None, "nothing was written at all"
    assert sae.history == [], "and no mutation was recorded"


def test_successor_may_not_take_a_fossilized_id(executor):
    """(ii) A fallen id is permanently dead (Ruling 18 / Ruling 19). Refused
    BEFORE the ancestor is touched, not after.

    RED under the defect: the ancestor was fossilized first, then commit()
    raised CodexWriteViolation on the fossil collision - same vanishing shape.
    """
    codex, sae = executor
    codex.commit(
        Doctrine(id="D-dead", name="doomed", description="x",
                 created_at=datetime.now()),
        sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-0", "D-dead"))
    codex.fossilize(
        "D-dead",
        sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-0", "D-dead"),
        reason="fell")
    assert codex.get_fossil("D-dead") is not None
    sae.stabilization_event("anchor_consolidation")     # fresh budget

    with pytest.raises(MutationPreflightViolation):
        sae.mutate_doctrine("D-live", Doctrine(
            id="D-dead", name="revenant", description="successor",
            created_at=datetime.now()), collapse_lineage="Δ-1",
            proof=minimal_proof("Ruling 24 preflight (ii) probe"))

    assert codex.get("D-live") is not None, "the ancestor did NOT vanish"
    assert codex.get_fossil("D-live") is None


def test_successor_may_not_clobber_a_live_doctrine(executor):
    """(iii) THE UNEXAMINED THIRD DEFECT. commit() would have SILENTLY
    overwritten an unrelated live doctrine on an id collision - a belief
    replaced with no collapse, no fossil, no lineage, no audit.

    RED under the defect: no exception at all. D-other's content was simply
    gone, and D-live was fossilized to pay for it.
    """
    codex, sae = executor
    victim = Doctrine(id="D-other", name="Bystander", description="untouched",
                      created_at=datetime.now())
    codex.doctrines[victim.id] = victim         # store fixture, not a write path

    with pytest.raises(MutationPreflightViolation):
        sae.mutate_doctrine("D-live", Doctrine(
            id="D-other", name="usurper", description="successor",
            created_at=datetime.now()), collapse_lineage="Δ-1",
            proof=minimal_proof("Ruling 24 preflight (iii) probe"))

    assert codex.get("D-other").name == "Bystander", "the bystander survived"
    assert codex.get("D-other").description == "untouched"
    assert codex.get("D-live") is not None, "and the ancestor did NOT vanish"


def test_preflight_passes_and_the_legitimate_mutation_still_executes(executor):
    """A correct guard never fires on the legitimate path. Nova's existing
    `{doctrine_id}::nova::{echo.id}` convention satisfies all three checks by
    construction - which is exactly what Ruling 24 makes structural."""
    codex, sae = executor
    successor = Doctrine(id="D-live::nova::NE-0001", name="Successor",
                         description="new form", created_at=datetime.now())

    out = sae.mutate_doctrine("D-live", successor, collapse_lineage="Δ-1",
                              proof=minimal_proof("Ruling 24 legitimate path",
                                                  scar_lineage=("Δ-1",),
                                                  ancestor_id="D-live"))

    assert out.id == "D-live::nova::NE-0001"
    assert codex.get("D-live::nova::NE-0001") is not None
    assert codex.get_fossil("D-live") is not None, "the ancestor ⊗-fossilized"
    assert codex.get("D-live") is None, "and is no longer active"
    assert "D-live" in out.mutation_lineage


# =====================================================================
# RULING 25 - a structural violation is not an error message
# =====================================================================

def _armed_pipeline():
    """A live AureaCore armed with a REAL structural landmine.

    The MUTATED echo is real, the strain is real, the scar is real. The
    landmine is a provenance key pre-claimed under the exact id the next
    emission will mint - so Nova's OWN append-only guard
    (ProvenanceOverwriteViolation, Ruling 13) fires inside _evolve_doctrine
    during a normal process_input. Nothing is patched or mocked; this is a
    deliberate guard firing on the real path.
    """
    aurea = AureaCore()
    _seed_strain(aurea, DOCTRINE_A)
    aurea._nova_cycle([])
    echo = next(e for e in aurea.nova.echo_index.values()
                if e.origin_id == DOCTRINE_A)
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 3):
        if echo.status is FermentationStatus.MUTATED:
            break
        aurea._nova_cycle([])
    assert echo.status is FermentationStatus.MUTATED
    aurea.nova.proposal_provenance[f"{DOCTRINE_A}::nova::{echo.id}"] = [
        {"store": "nova_echo_index", "record_id": echo.id}]
    return aurea


def test_a_structural_violation_is_not_flattened_into_errors():
    """RULING 25, THE PIN. Every deliberate guard this project has built -
    CodexWriteViolation, CeilingExceeded, UngatedReflexViolation,
    UngroundedEchoViolation, ProvenanceOverwriteViolation - was
    indistinguishable from a malformed-input hiccup. The entire "raise, don't
    resolve; the wrong path must be unexecutable" discipline terminated in a
    string concatenation.

    RED under the defect: result['errors'] held the guard's message and
    result['output'] was "[ERROR: proposal_provenance already holds ...]" -
    with output_blocked False.
    """
    aurea = _armed_pipeline()

    result = aurea.process_input("Honesty is pointless.")

    violation = result.get("structural_violation")
    assert violation is not None, "the guard fired and nothing said so"
    assert violation["type"] == "ProvenanceOverwriteViolation"
    assert "append-only" in violation["message"]
    assert result["errors"] == [], (
        "a structural violation is NOT an ordinary error - it must not be "
        "merged into the graceful-degradation surface")


def test_a_structural_violation_suppresses_normal_output():
    """AUREA does not answer as though nothing happened when her own guard
    just fired. The refusal IS the answer.

    CHANGED BY A RULING, 2026-07-26 (HAIL Stage 2) - the ONE legitimate reason
    a pinned test moves, per the Ruling-14 precedent. Recorded verbatim:

        OLD (Ruling 25, 2026-07-25):
            assert "ProvenanceOverwriteViolation" in result["output"]

        NEW (Ruling 33 (6), 2026-07-26):
            assert "ProvenanceOverwriteViolation" in " ".join(
                result["truth_packet"].unresolved)

    WHY: Ruling 33 (6) rules this exact case in as many words - "Structural-
    violation output (Ruling 25) maps to WITHHOLD with the violation carried in
    `unresolved` - her guard firing is truth content, not a rendering choice."
    A WITHHOLD renders a fixed string that structurally cannot contain the
    content (hail._render_silent takes one enum; the packet is not in its
    scope), so the violation type CANNOT appear in result["output"] any more.

    NOTHING WAS WEAKENED. Ruling 25's three requirements are each still pinned:
    the loud field (test_a_structural_violation_is_not_flattened_into_errors),
    the durable record (test_..._recorded_durably_and_does_not_crash), and
    suppressed output - which is now suppressed HARDER than before, since the
    old string still narrated the violation and the new one says nothing at
    all. The violation moved from the spoken surface into the packet, which is
    where Ruling 33 put it, and the assertion followed it there.
    """
    aurea = _armed_pipeline()

    result = aurea.process_input("Honesty is pointless.")

    assert result["output_blocked"] is True
    assert not result["output"].startswith("[ERROR:"), (
        "a guard firing must not read as a typo")
    assert "Echo processed" not in (result["output"] or "")
    assert "ProvenanceOverwriteViolation" in " ".join(
        result["truth_packet"].unresolved), (
        "the violation must remain legible - Ruling 33 moved it from the "
        "rendered string into the packet, it did not drop it")
    assert "ProvenanceOverwriteViolation" not in result["output"], (
        "a WITHHOLD renders no content, including the violation's own name")


def test_a_structural_violation_is_recorded_durably_and_does_not_crash():
    """It does NOT crash the process - that would destroy the record, and the
    record is the point. The record is legible in memory AND on disk."""
    aurea = _armed_pipeline()

    aurea.process_input("Honesty is pointless.")

    assert len(aurea.structural_violations) == 1
    entry = aurea.structural_violations[0]
    assert entry["type"] == "ProvenanceOverwriteViolation"
    assert entry["input"] == "Honesty is pointless."
    log = aurea.structural_log_path
    assert log.exists(), "a forensic record that is not durable is not forensic"
    assert "ProvenanceOverwriteViolation" in log.read_text(encoding="utf-8")

    # The pipeline is not dead: an ordinary pass afterward still runs.
    after = aurea.process_input("The sky is blue.")
    assert after.get("structural_violation") is None


def test_an_ordinary_exception_still_degrades_gracefully():
    """The taxonomy CUTS - it does not replace. A malformed-input hiccup is
    not a structural violation and must keep degrading into `errors`, exactly
    as before. If this goes red, the broad clause was widened into the
    structural one.

    MIGRATED 2026-08-01 BY RULING 60, under the Ruling-14 precedent. NO
    ASSERTION MOVED - all four are byte-identical. What changed is the TEST
    DOUBLE'S SIGNATURE, which had drifted from the collaborator it stands in
    for: SPL's `process_input` gained a keyword-only `claim_id` (the echo <->
    claim linkage), and the double did not accept it.

        OLD:  def process_input(self, raw_input, source):
        NEW:  def process_input(self, raw_input, source, *, claim_id=None):

    THE FAILURE WAS THE DOUBLE, NOT AUREA, and the distinction is worth
    recording: the pass still degraded gracefully and still recorded NO
    structural violation - the taxonomy cut exactly as this test demands. Only
    the MESSAGE differed, because the stale signature raised a `TypeError`
    about `claim_id` before the intended `ValueError` could be reached. A
    double that cannot be called the way the real object is called tests the
    harness, not the system.
    """
    aurea = AureaCore()

    class _Boom:
        # RULING 68 (2026-08-02): the double follows the collaborator it
        # stands in for - `source` was DELETED from `SPL.process_input`.
        # A double whose signature has drifted from the real thing tests the
        # double (Ruling 60's finding, same file). No assertion moved.
        def process_input(self, raw_input, *, claim_id=None):
            raise ValueError("ordinary malformed-input hiccup")

    aurea.spl = _Boom()
    result = aurea.process_input("anything")

    assert result.get("structural_violation") is None
    assert result["errors"] == ["ordinary malformed-input hiccup"]
    assert result["output"].startswith("[ERROR:")
    assert aurea.structural_violations == []


# =====================================================================
# RULING 22 - the scar store gets the boundary the doctrine store has
# =====================================================================

@pytest.fixture
def scars(tmp_path):
    core = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    core.form_scar(origin="collapse-a", type="contradiction", weight=5.0,
                   description="first", linked_doctrines=["D-1"])
    core.form_scar(origin="collapse-b", type="paradox", weight=9.0,
                   description="second")
    return core


def test_get_scar_hands_out_a_snapshot_not_the_record(scars):
    """RULING 22. A caller holding the live Scar can set .weight, clear
    .linked_doctrines, or flip .decay_state with no owner-controlled
    operation - and the AST single-writer invariant cannot see it, because
    nothing assigns to scar_core.scars. The doctrine store has an ownership
    BOUNDARY; the scar store had a CONVENTION."""
    scar_id = scars.scars[0].id
    first = scars.get_scar(scar_id)

    assert first is not scars.scars[0], "a read must not hand out the record"
    first.weight = 999.0
    first.decay_state = "retired"
    first.linked_doctrines.clear()

    fresh = scars.get_scar(scar_id)
    assert fresh.weight == 5.0, "the store's weight was written through a read"
    assert fresh.decay_state == "active"
    assert fresh.linked_doctrines == ["D-1"], "the mutable list is copied too"


def test_get_active_scars_hands_out_snapshots(scars):
    """The list accessor gets the same boundary - Codex.active() already
    snapshots each element, and this is the same shape."""
    live = scars.get_active_scars()
    assert len(live) == 2
    for scar in live:
        scar.weight = 0.0
        scar.decay_state = "retired"

    assert [s.weight for s in scars.get_active_scars()] == [5.0, 9.0]
    assert len(scars.get_active_scars()) == 2, "nothing was retired by a read"


def test_the_owners_own_write_paths_still_reach_the_record(scars):
    """THE FAIL-SILENT GUARD. decay_scar() resolved its target THROUGH the
    public read accessor and mutated what came back. Snapshotting the accessor
    without re-pointing that lookup at the record would make the owner's own
    write vanish silently - the worst possible outcome of this change, and
    invisible to every other test in the suite.

    VOCABULARY UPDATED 2026-07-27 (Ruling 37 (2)) - the ASSERTION IS UNCHANGED
    IN FORCE, only in spelling. Recorded per the Ruling-14 precedent:

        OLD: assert scars.get_scar(scar_id).decay_state == "retired"
             assert scars.scars[1].decay_state == "retired", "the RECORD changed"
        NEW: the same two assertions against `DecayState.DORMANT`.

    WHY: Ruling 37 gave `decay_state` a typed closed vocabulary and ruled that
    `"retired"` maps INTO it rather than surviving as a fifth state outside it.
    The pin still asserts exactly what it always did - that the owner's write
    reached the RECORD and not a snapshot - and it would still go red under the
    fail-silent defect it was written for. The literal moved because the RULING
    moved, not because the test was inconvenient.
    """
    from src.filtration.scar_management import DecayState

    scar_id = scars.scars[1].id

    assert scars.decay_scar(scar_id) is True

    assert scars.get_scar(scar_id).decay_state == DecayState.DORMANT
    assert scars.scars[1].decay_state == DecayState.DORMANT, "the RECORD changed"
    assert len(scars.get_active_scars()) == 1
    assert scars.decay_scar("no-such-scar") is False


# =====================================================================
# RULING 23 - DMW overflow is a REFUSAL and must be recorded as one
# =====================================================================

def _fill_dmw(dee):
    """Saturate the watch queue with real slots up to the bound."""
    for i in range(DMW_QUEUE_MAX):
        dee.dmw.queue[f"FILLER-{i:03d}"] = _Watched(
            doctrine_id=f"FILLER-{i:03d}", pressure=0.8, sustained_cycles=1)
    assert len(dee.dmw.queue) == DMW_QUEUE_MAX


def test_dmw_overflow_records_the_refusal_it_used_to_swallow():
    """RULING 23. The 32-cap is CORRECT and does not move - bounded queues are
    how this system refuses to become an overload vector. The SILENCE was the
    defect: past the cap, a new strained doctrine hit a bare `continue`, while
    twenty lines above the expiry path routed through _ferment with a reason
    string. Same file, same author: one exit legible, the other silent.

    RED under the defect: dmw.last_overflow did not exist; the doctrine's
    admitted strain was discarded with no record that AUREA declined to watch
    it.
    """
    aurea = AureaCore()
    _fill_dmw(aurea.dee)
    flag = PressureFlag(doctrine_id=DOCTRINE_A, pressure=0.9, band="critical",
                        triggers=[MutationTrigger.DRPE])

    aurea.dee.dmw.observe([flag])

    assert DOCTRINE_A not in aurea.dee.dmw.queue, "the bound HOLDS"
    assert len(aurea.dee.dmw.queue) == DMW_QUEUE_MAX, "the cap did not move"
    refusal = next(r for r in aurea.dee.dmw.last_overflow
                   if r["doctrine_id"] == DOCTRINE_A)
    assert "capacity" in refusal["reason"]


def test_an_overflowed_doctrine_reaches_the_same_surface_as_every_outcome():
    """Unresolved pressure never leaves silently. An overflowed doctrine's
    strain was real and DRPAS-admitted, so it lands where the expiry path
    lands: a recorded EligibilityRuling, fermenting rather than dropped."""
    aurea = AureaCore()
    _fill_dmw(aurea.dee)

    rulings = aurea.dee.cycle(
        signals={DOCTRINE_A: {"pressure": 0.9, "drpe": True}})

    ours = next(r for r in rulings if r.doctrine_id == DOCTRINE_A)
    assert ours.verdict is Verdict.FERMENT
    assert "capacity" in ours.reason
    assert ours in aurea.dee.rulings, "recorded, not merely returned"
    assert ours.pressure == 0.9, "the real strain magnitude is carried"


def test_below_capacity_nothing_is_refused():
    """Not vacuous: with room in the queue the same doctrine is ADMITTED and
    no refusal is recorded. The refusal path fires on the bound, not on
    every pass."""
    aurea = AureaCore()
    flag = PressureFlag(doctrine_id=DOCTRINE_A, pressure=0.9, band="critical",
                        triggers=[MutationTrigger.DRPE])

    aurea.dee.dmw.observe([flag])

    assert DOCTRINE_A in aurea.dee.dmw.queue
    assert aurea.dee.dmw.last_overflow == []
