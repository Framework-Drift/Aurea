"""
test_echonet.py - the front-line collapse gate's battery (Ruling 49, 2026-07-29).

This file was a 0-BYTE STUB. EchoNet decides whether a claim is CONFIRMED,
SUSPENDED, SCARRED or PARADOX - the first thing that happens to anything AUREA
is told, and the only place a scar can be requested - and it had no dedicated
test of its own. `test_docket_h.py` covers the EVIDENCE payload thoroughly and
deliberately touches verdicts only to prove the payload did not move them.

    "Truth is not what appears coherent - it is what can be carried
     through collapse."                                    - canon, 0:121-178

STAGE 2 IS PINNED FIRST, AND THAT ORDERING IS THE POINT. Section A below was
written against `5f0c1e9` - BEFORE the Stage 3 overlay existed - and every
assertion in it was verified green there. So the overlay's arrival is MEASURED
rather than assumed: if Stage 3 had quietly moved a Stage 2 verdict, section A
would have caught it instead of the change surfacing later as a mystery.

    The six nets and the four verdict classes are CANON.
    The heuristics inside them are COINED (see the file's SPECULATION FLAG).

These pins therefore assert BEHAVIOUR, not correctness-of-heuristic: they hold
the current instrument still so that a change to it is visible and deliberate.
Where a pin depends on a coined pattern, it says so.

WHAT CHANGED WHEN STAGE 3 LANDED - the enumerated list, section E. Six verdicts
moved, all CONFIRMED -> SUSPENDED, all on claims that NAME a live doctrine and
DENY it, and all only when a spine is wired. In the bare configuration nothing
moved at all: verified by a 39-claim x 2-configuration differential dump against
`5f0c1e9`.
"""

import ast
from datetime import datetime

import pytest

from src.doctrine.codex import Codex
from src.doctrine.doctrine_spine import DoctrineSpine
from src.filtration.echonet import (
    BASE_THRESHOLD,
    SUSPENSION_FLOOR,
    SUSTAINED_STRAIN,
    EchoNet,
    OverlayInstrument,
    OverlayRelation,
    OverlayResult,
    Verdict,
)
from src.filtration.net_evidence import Countability
from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.models import Echo


def _echo(content: str) -> Echo:
    return Echo(id="E-test", content=content,
                resonance_score=0.0, created_at=datetime.now())


def _bare() -> EchoNet:
    """No stores. Every instrument that needs one must ABSTAIN, not guess."""
    return EchoNet()


def _wired() -> EchoNet:
    """The pipeline's own configuration: the REAL seed doctrines and scars.

    `aurea_core` builds EchoNet with exactly these two handles (plus the grid
    and compass). Reading the real seed rather than fixtures is deliberate -
    Ruling 35's lesson was that a defect in how a seed is READ is invisible to
    every test that substitutes its own.
    """
    return EchoNet(scar_core=ScarLogicCore(),
                   doctrine_spine=DoctrineSpine(codex=Codex()))


# =====================================================================
# A. STAGE 2 - THE SIX NETS AND THE THRESHOLD
#    Written against 5f0c1e9 and green there. These must not move.
# =====================================================================

@pytest.mark.parametrize("claim, verdict, pressure", [
    # PARADOX: the logic net at >= 0.95 on a self-devouring claim.
    ("this statement is false", Verdict.PARADOX, 1.0),
    ("i am lying", Verdict.PARADOX, 1.0),
    ("nothing is true", Verdict.PARADOX, 0.95),
    ("there are no absolutes", Verdict.PARADOX, 0.95),
    # SUSPENDED: real strain, below the collapse threshold.
    ("everyone always lies", Verdict.SUSPENDED, 0.55),
    ("by definition true", Verdict.SUSPENDED, 0.6),
    # SCARRED: a net failed AND pressure reached the threshold.
    ("truth does not matter", Verdict.SCARRED, 0.85),
    ("lying is fine", Verdict.SCARRED, 0.85),
    # CONFIRMED: nothing strained.
    ("the kettle boiled quietly", Verdict.CONFIRMED, 0.0),
])
def test_stage_2_verdicts_are_unchanged(claim, verdict, pressure) -> None:
    """THE REGRESSION PIN. Every value here was read off `5f0c1e9`.

    Stage 3 contributes pressure into the same computation these run through,
    so this is the assertion that says it did not disturb them. A bare EchoNet
    is used because the overlay abstains without a spine - which makes this
    specifically a pin on Stage 2 in isolation.
    """
    result = _bare().filter_claim(_echo(claim))
    assert result.verdict is verdict
    assert result.pressure_generated == pytest.approx(pressure)


def test_a_paradox_needs_the_logic_net_specifically() -> None:
    """PARADOX is not "very high pressure" - it is the LOGIC net at >= 0.95.

    The distinction matters: the ethics net at 0.85 SCARS, and if the branch
    keyed on magnitude alone a hard enough ethical strain would land in the
    Black Sphere instead of the Collapse Archive. Two different destinations
    for two different failures.
    """
    paradox = _bare().filter_claim(_echo("this statement is false"))
    assert paradox.verdict is Verdict.PARADOX
    assert paradox.pressure_type == "logical_contradiction"

    scarred = _bare().filter_claim(_echo("truth does not matter"))
    assert scarred.verdict is Verdict.SCARRED
    assert scarred.pressure_type == "ethical"


def test_an_uncertain_claim_is_suspended_and_never_scarred() -> None:
    """The file's own standing rule, and the reason it exists:

        "A claim that is merely UNCERTAIN must not be scarred. Uncertainty is
         suspended. Only a claim that cannot be held without contradiction gets
         to leave a mark."

    An unqualified universal is unfalsifiable, not false. It strains at 0.55,
    below the 0.75 threshold, and is held open.
    """
    result = _bare().filter_claim(_echo("everyone always lies"))
    assert result.verdict is Verdict.SUSPENDED
    assert result.pressure_generated < result.threshold
    assert result.scar is None, "EchoNet requests scars; it never carries one here"


def test_a_qualified_universal_does_not_strain() -> None:
    """The empirical net's own escape hatch, pinned because it is what keeps
    the net from flagging every sentence containing 'all'. COINED heuristic."""
    strained = _bare()._net_empirical("everyone always lies")
    qualified = _bare()._net_empirical("everyone always lies when they are afraid")
    assert strained.survived is False
    assert qualified.survived is True, (
        "a condition under which the claim could fail makes it testable")


def test_the_intuition_net_abstains_and_says_so() -> None:
    """It cannot be honestly implemented and does not pretend to be.

    An abstaining net is honest; a guessing one writes false pressure into a
    permanent record. If this ever returns survived=False, someone has taught a
    regex to have a hunch.
    """
    result = _bare()._net_intuition("anything at all")
    assert result.survived is True
    assert result.pressure == 0.0
    assert "ABSTAINED" in result.note


def test_convergent_elimination_fires_only_at_three_strains() -> None:
    """The sixth net, and the canon magnitude (Scar Bloom >= 3) it rides on.

    Built from `NetResult`s directly rather than from a claim: no real claim in
    the corpus strains three nets at once, and constructing one would mean
    reverse-engineering three COINED heuristics into a sentence - which pins the
    sentence rather than the rule.
    """
    from src.filtration.echonet import NetResult

    def straining(n):
        return [NetResult(f"net-{i}", True, SUSTAINED_STRAIN) for i in range(n)]

    net = _bare()
    assert net._net_convergent_elimination(straining(2)).survived is True
    assert net._net_convergent_elimination(straining(3)).survived is False, (
        "three simultaneous strains is the convergence line")

    just_under = [NetResult("a", True, SUSTAINED_STRAIN - 0.01)] * 3
    assert net._net_convergent_elimination(just_under).survived is True, (
        "the strain list is built at >= SUSTAINED_STRAIN, not near it")


def test_the_threshold_tightens_near_scars_and_doctrine() -> None:
    """The dynamic threshold, all three inputs (Lexicon: scar weighting,
    doctrine pressure, compass drift).

    VERIFIED AGAINST 5f0c1e9: the doctrine half FIRES - 0.75 -> 0.70 on a claim
    naming a real seed doctrine. This is the consult that already existed, and
    stating it here is what keeps "EchoNet never consulted the spine" from being
    repeated: it did, in the threshold. What it never did was consult it in the
    NET LAYER, which is what Stage 3 is.
    """
    assert _bare()._threshold("the kettle boiled quietly") == BASE_THRESHOLD

    wired = _wired()
    assert wired._threshold("Fracture Carried is false.") < BASE_THRESHOLD, (
        "a claim brushing load-bearing doctrine gets less benefit of the doubt")
    assert wired._threshold("compassion was turned into a weapon") < BASE_THRESHOLD, (
        "a claim near a heavy scar is judged more strictly")


def test_the_threshold_has_a_floor_no_input_can_cross() -> None:
    """`max(0.4, ...)`. Every reduction stacks, and the floor is what stops a
    heavily-scarred claim from being judged at an impossible bar.

    IT IS ALSO WHY STAGE 3 CANNOT SCAR - see the overlay section below.
    """
    class _Drifting:
        drift = 90.0

    net = EchoNet(scar_core=ScarLogicCore(),
                  doctrine_spine=DoctrineSpine(codex=Codex()),
                  compass=_Drifting())
    for claim in ("compassion was turned into a weapon",
                  "Fracture Carried is false.",
                  "the survivor could not self-reflect and identity fragmented"):
        assert net._threshold(claim) >= 0.4


def test_echonet_never_writes_the_scar_store() -> None:
    """Ruling 1. `collapse_test` ASKS; ScarLogicCore writes. A passing claim
    asks for nothing, and a missing owner is a refusal rather than a fallback."""
    assert _bare().collapse_test(_echo("the kettle boiled quietly")) is None
    assert _bare().collapse_test(_echo("truth does not matter")) is None, (
        "no scar core injected - EchoNet does not write one itself")


# =====================================================================
# B. THE THREE COUNTABILITY STATES, WITNESSED IN ONE ORGAN
# =====================================================================

def test_all_three_countability_states_occur_in_one_pass() -> None:
    """COUNTED, NONE_FOUND and NOT_COUNTABLE all present on a single wired run.

    `test_docket_h.py` proves the states are distinguishable in the TYPE; this
    proves the organ actually reaches all three at once, which is the property
    that makes the distinction worth having.
    """
    result = _wired().filter_claim(_echo("compassion was turned into a weapon"))
    states = {n.evidence.countability for n in result.nets}
    states.add(result.overlay.evidence.countability)

    assert Countability.COUNTED in states
    assert Countability.NOT_COUNTABLE in states
    assert Countability.NONE_FOUND in states, (
        "an honest zero must be reachable, or the enum has two live members")


def test_the_overlay_is_not_a_seventh_net() -> None:
    """Canon's Stage 2 is SIX nets; Stage 3 is a separate stage.

    `OverlayResult` has NO `survived` field, which is what makes appending it to
    `nets` impossible rather than merely wrong - the same enforcement-by-scope
    Ruling 33 used on `_render_silent`. `test_docket_h.py` asserts
    `len(result.nets) == 6` and that assertion is CORRECT, not an obstacle.
    """
    result = _wired().filter_claim(_echo("Fracture Carried is false."))
    assert len(result.nets) == 6
    assert isinstance(result.overlay, OverlayResult)
    assert not hasattr(result.overlay, "survived")
    assert "survived" not in OverlayResult.__dataclass_fields__


# =====================================================================
# C. STAGE 3 - THE DOCTRINE + SCARLINE OVERLAY
# =====================================================================

def test_a_claim_that_denies_a_live_doctrine_fractures_it() -> None:
    """THE FORCING PIN FOR RULING 49.

    RED AT `5f0c1e9`: watched there, `Fracture Carried is false.` came back
    CONFIRMED with pressure 0.0 and no doctrine id anywhere in the result. The
    claim names AUREA's founding doctrine of carried fracture and denies it, and
    the front-line collapse gate had nothing to say about that - because nothing
    in the net layer consulted the doctrine store.

    The doctrine id in the EVIDENCE is half the pin. A pressure number with no
    named doctrine behind it would be exactly the fabricated magnitude
    `net_evidence.py` exists to refuse.
    """
    result = _wired().filter_claim(_echo("Fracture Carried is false."))
    overlay = result.overlay

    assert overlay.pressure > 0.0
    assert result.pressure_generated >= SUSPENSION_FLOOR
    assert result.verdict is Verdict.SUSPENDED, (
        "a claim denying what she holds does not settle")

    fractures = overlay.fractures
    assert len(fractures) == 1
    assert fractures[0].doctrine_id == "Doctrine-0.1"
    assert fractures[0].relation is OverlayRelation.FRACTURE
    assert fractures[0].instrument is OverlayInstrument.REFERENTIAL

    assert overlay.evidence.countability is Countability.COUNTED
    assert "Doctrine-0.1" in {ref.item_id for ref in overlay.evidence.refs}, (
        "the fracture must name the doctrine it found, from the real store")


def test_a_claim_that_affirms_a_doctrine_is_support_and_never_pressure() -> None:
    """RESONANCE is recorded, and it is recorded at ZERO pressure.

    If alignment ever generated pressure, agreeing with AUREA would push a claim
    toward collapse - which inverts the whole instrument.
    """
    result = _wired().filter_claim(_echo("Fracture Carried is true."))
    overlay = result.overlay

    assert overlay.pressure == 0.0
    assert result.verdict is Verdict.CONFIRMED
    assert [f.doctrine_id for f in overlay.resonances] == ["Doctrine-0.1"]
    assert overlay.fractures == ()
    assert overlay.evidence.countability is Countability.COUNTED, (
        "support is real evidence and is counted; it just is not pressure")


def test_a_claim_that_both_denies_and_affirms_is_ambiguous_not_guessed() -> None:
    """The instrument cannot tell which stance is aimed at the doctrine, so it
    reports AMBIGUOUS at zero pressure rather than picking.

    The file's standing posture: over-reporting collapse manufactures scars.
    Under-reporting costs a suspension that does not happen.
    """
    overlay = _wired().filter_claim(
        _echo("Fracture Carried is true but Scar as Anchor is false.")).overlay

    assert overlay.pressure == 0.0
    assert overlay.findings, "the doctrines still bore on the claim"
    assert all(f.relation is OverlayRelation.AMBIGUOUS for f in overlay.findings)


def test_the_overlay_abstains_when_it_has_no_doctrine_store() -> None:
    """GROUND OR ABSTAIN. A bare EchoNet cannot look at what AUREA holds, and
    NOT_COUNTABLE with a reason is what that must produce - never a guess, and
    never an honest zero (which would claim a search that did not happen)."""
    overlay = _bare().filter_claim(_echo("Fracture Carried is false.")).overlay

    assert overlay.pressure == 0.0
    assert overlay.findings == ()
    assert overlay.evidence.countability is Countability.NOT_COUNTABLE
    assert overlay.evidence.uncountable_reason.strip()
    assert "no doctrine spine" in overlay.evidence.uncountable_reason


def test_the_overlay_read_the_store_and_found_nothing_is_an_honest_zero() -> None:
    """The OTHER zero. A real instrument ran over the real doctrine store and
    nothing bore on the claim - which is a completely different statement from
    'could not look', and `net_evidence.py` exists to keep them apart."""
    overlay = _wired().filter_claim(_echo("the kettle boiled quietly")).overlay

    assert overlay.evidence.countability is Countability.NONE_FOUND
    assert overlay.findings == ()
    assert overlay.evidence.uncountable_reason == ""


def test_the_overlay_cannot_scar_a_claim_by_itself() -> None:
    """A STRUCTURAL PROPERTY, not a convention, and it falls out of two
    magnitudes that were already in the file.

    Stage 3's maximum pressure is SUSPENSION_FLOOR (0.35); `_threshold`'s own
    floor is 0.4. So overlay-only pressure can reach SUSPENDED and can never
    reach the collapse threshold - and SCARRED and PARADOX both additionally
    require a failed NET, which Stage 3 structurally cannot be.

    This is what lets Stage 3 exist at all without violating the file's rule
    that a filter which over-reports collapse manufactures scars.
    """
    assert SUSPENSION_FLOOR < 0.4, (
        "the overlay's ceiling must stay below the threshold's floor")
    assert SUSTAINED_STRAIN < SUSPENSION_FLOOR, (
        "the weak instrument must stay below the suspension floor")

    for claim in ("Fracture Carried is false.",
                  "Doctrine-0 is false.",
                  "AVT.001 must be abandoned.",
                  "Paradox Suspension Law is wrong."):
        result = _wired().filter_claim(_echo(claim))
        assert result.verdict is Verdict.SUSPENDED, claim


def test_the_lexical_instrument_alone_never_suspends_a_claim() -> None:
    """The weak instrument reports and does not decide.

    `collapse must be simplified into a single conclusion` genuinely contradicts
    `Doctrine-3` ("Collapse Must Not Be Simplified") but does not NAME it, so the
    finding rests on shared vocabulary - a COINED heuristic. It is recorded at
    SUSTAINED_STRAIN, which is below the suspension floor by construction, so a
    lexical guess can never by itself change what AUREA does with the claim.
    """
    result = _wired().filter_claim(
        _echo("collapse must be simplified into a single conclusion"))

    assert result.overlay.pressure == pytest.approx(SUSTAINED_STRAIN)
    assert all(f.instrument is OverlayInstrument.LEXICAL
               for f in result.overlay.fractures)
    assert result.verdict is Verdict.CONFIRMED, (
        "reported, not acted on - the verdict is unchanged from 5f0c1e9")


def test_bare_topical_overlap_is_not_recorded_as_support() -> None:
    """The weak instrument requires a STANCE in either direction.

    Across a store of doctrines almost any claim shares two words with
    something. Recording that as resonance would flood the evidence with
    topicality and make a support tally meaningless.
    """
    overlay = _wired().filter_claim(
        _echo("collapse and doctrine and symbolic pressure")).overlay
    assert overlay.resonances == ()


# =====================================================================
# D. STAGE 3 AGAINST THE REAL SEED - Doctrine-0 and Scar-0
# =====================================================================

def test_the_locked_founding_doctrine_is_still_fracturable() -> None:
    """WHY THE OVERLAY READS active + locked AND NOT `codex.active()` ALONE.

    `Doctrine-0` ships LOCKED in the seed, so it is absent from `active()`.
    Ruling 35 settled what locked means - "LOCKED STAYS LIVE AND READABLE ...
    excluded from mutation SCANNING, not from the store" - and Ruling 43 landed
    the scar-side twin (`LIVE_STATES = {ACTIVE, LOCKED}`).

    Stage 3 is a TRUTH TEST, not change machinery. Reading `active()` here would
    mean a claim denying her FOUNDING doctrine produced no fracture at all,
    which is the one case most obviously worth noticing.
    """
    codex = Codex()
    assert "Doctrine-0" not in {d.id for d in codex.active()}, (
        "precondition: the founding doctrine is locked, not active")
    assert codex.get("Doctrine-0") is not None, "and it is still live and readable"

    overlay = _wired().filter_claim(_echo("Doctrine-0 is false.")).overlay
    assert [f.doctrine_id for f in overlay.fractures] == ["Doctrine-0"]


def test_the_scarline_is_read_from_both_sides() -> None:
    """RULING 26's bidirectional read, and here it is LOAD-BEARING rather than
    defensive - proven against the real seed, which DISAGREES WITH ITSELF.

    `Doctrine-0` records exactly ONE scar link of its own (`Scar-0`, The Origin
    Collapse). But FOUR scars name it in their `linked_doctrines`: Δ42, Δ77, Δ88
    and Scar-0. So the doctrine's own half reports a quarter of its lineage, and
    a reader consulting only `doctrine.scar_links` would see the founding record
    and none of the collapses that actually bear on it.

    CORRECTED HERE AFTER THE PRECONDITION FAILED. This test first asserted the
    doctrine's own half was EMPTY - inferred from a probe that had printed only
    `codex.active()`, which excludes the locked founding doctrine. The
    precondition caught it, which is what preconditions are for. The bidirectional
    read is MORE clearly load-bearing than the wrong version claimed, not less:
    three of the four scars are reachable only through the scar store's half.
    """
    codex = Codex()
    assert codex.get("Doctrine-0").scar_links == ["Scar-0"], (
        "precondition: the doctrine's own half names exactly one scar")

    overlay = _wired().filter_claim(_echo("Doctrine-0 is false.")).overlay
    finding = overlay.fractures[0]

    assert "Scar-0" in finding.scarline, "the doctrine's own half"
    assert {"Δ42", "Δ77", "Δ88"} <= set(finding.scarline), (
        "reachable ONLY through scar.linked_doctrines - the store's half")
    assert finding.unconfirmed_scarline == (), (
        "every one of them is confirmed live by the scar store")


def test_a_doctrine_id_never_matches_inside_a_longer_id() -> None:
    """`Doctrine-0` is a prefix of `Doctrine-0.1`, and BOTH are in the real seed.

    With a plain `\\b` boundary, a claim about the successor would have
    attributed a fracture to her founding doctrine. The boundary is `[\\w.\\-]`
    for exactly this pair, which exists on disk rather than in theory.
    """
    overlay = _wired().filter_claim(_echo("Doctrine-0.1 is false.")).overlay
    assert [f.doctrine_id for f in overlay.fractures] == ["Doctrine-0.1"]

    reverse = _wired().filter_claim(_echo("Doctrine-0 is false.")).overlay
    assert [f.doctrine_id for f in reverse.fractures] == ["Doctrine-0"]


def test_a_scarline_is_one_source_not_several_corroborations() -> None:
    """`source_id` is the INDEPENDENCE KEY (net_evidence.py).

    Four scars in one doctrine's lineage are FOUR pieces of evidence from ONE
    source. Reporting four sources would be the overstatement that module exists
    to prevent - the one-of-one versus thousand-of-one-thousand rule, applied to
    a lineage.
    """
    evidence = _wired().filter_claim(_echo("Doctrine-0 is false.")).overlay.evidence

    assert evidence.evidence_count > evidence.independent_source_count
    assert evidence.independent_source_count == 1
    assert {ref.source_id for ref in evidence.refs} == {"Doctrine-0"}


def test_an_unconfirmable_scarline_is_named_not_silently_counted() -> None:
    """With no scar store, every scarline id is a RECORDED reference and NONE is
    confirmed live. They are still reported - the doctrine records them, which
    is a fact - and named as nominal so a reader can subtract."""
    net = EchoNet(doctrine_spine=DoctrineSpine(codex=Codex()))   # no scar_core
    overlay = net.filter_claim(_echo("Fracture Carried is false.")).overlay
    finding = overlay.fractures[0]

    assert finding.scarline == ("Δ42", "Δ88", "Δ31")
    assert finding.unconfirmed_scarline == finding.scarline
    assert set(overlay.evidence.uncounted_contributors) == set(finding.scarline)


# =====================================================================
# E. THE ENUMERATED CHANGED OUTCOMES
# =====================================================================

# Verified by a 39-claim x 2-configuration differential dump against `5f0c1e9`.
# SIX verdicts moved and no more. Every one is CONFIRMED -> SUSPENDED, on a
# claim that NAMES a live doctrine and DENIES it, with a spine wired.
STAGE_3_VERDICT_MOVES = {
    "Fracture Carried is false.": "Doctrine-0.1",
    "Doctrine-0.1 is false.": "Doctrine-0.1",
    "Doctrine-0 is false.": "Doctrine-0",
    "AVT.001 must be abandoned.": "AVT.001",
    "Paradox Suspension Law is wrong.": "AVT.001",
    "Curiosity Loop is meaningless": "AVT.002",
}


@pytest.mark.parametrize("claim, doctrine_id", sorted(STAGE_3_VERDICT_MOVES.items()))
def test_each_changed_outcome_is_a_named_doctrine_denied(claim, doctrine_id) -> None:
    """Every verdict Stage 3 moved, with the reason it moved.

    A changed outcome that nobody enumerated is indistinguishable from a
    regression. Each of these was CONFIRMED at `5f0c1e9` and is SUSPENDED now,
    and the assertion carries WHICH doctrine did it.
    """
    result = _wired().filter_claim(_echo(claim))
    assert result.verdict is Verdict.SUSPENDED
    assert result.pressure_type == "doctrine_fracture"
    assert [f.doctrine_id for f in result.overlay.fractures] == [doctrine_id]
    assert doctrine_id in result.reason


def test_the_bare_configuration_moved_nothing_at_all() -> None:
    """The ground-or-abstain guarantee, stated as a property rather than a hope.

    In the 39-claim differential, the BARE configuration produced ZERO
    differences of any kind - not a verdict, not a pressure, not a note. Stage 3
    cannot change anything without a store to read, which is what makes the
    abstention honest rather than decorative.
    """
    bare = _bare()
    for claim in STAGE_3_VERDICT_MOVES:
        result = bare.filter_claim(_echo(claim))
        assert result.verdict is Verdict.CONFIRMED, (
            f"{claim!r} moved without a doctrine store to move it")
        assert result.pressure_generated == 0.0


def test_a_scarred_claim_is_still_scarred() -> None:
    """The single most important thing NOT to have broken.

    `Honesty is pointless.` is the claim four end-to-end test files drive
    through the real pipeline to produce a real scar. Stage 3 adds at most 0.35
    and the ethics net already carries 0.85, so the verdict is untouched - but
    it is pinned here rather than reasoned about, because the whole downstream
    scar/Nova/DEE chain rests on it.
    """
    result = _wired().filter_claim(_echo("Honesty is pointless."))
    assert result.verdict is Verdict.SCARRED
    assert result.pressure_generated == pytest.approx(0.85)
    assert result.pressure_type == "ethical"


# =====================================================================
# F. THE ETHICS NET'S BORROWED CLAIM GOES HOME
# =====================================================================

def test_the_ethics_net_names_the_doctrine_when_it_can() -> None:
    """DOCKET H'S FINDING, CLOSED.

    RED AT `5f0c1e9`: the net asserted "claim requires abandoning a load-bearing
    doctrine to accept" while never reading the doctrine store - it could not
    name the doctrine, so its evidence was NOT_COUNTABLE and its note was a
    claim about a record it had never opened. One net trying to be the overlay
    with a regex.
    """
    codex = Codex()
    # A load-bearing doctrine (3+ scars, the Spine's own definition) that the
    # claim also names. `Doctrine-0.1` carries three seed scars.
    assert len(codex.get("Doctrine-0.1").scar_links) >= 3

    result = _wired()._net_ethics("truth does not matter, Fracture Carried is wrong")

    assert result.survived is False
    assert result.pressure == pytest.approx(0.85)
    assert result.evidence.countability is Countability.COUNTED
    assert "Doctrine-0.1" in {ref.item_id for ref in result.evidence.refs}
    assert "Doctrine-0.1" in result.note


def test_the_ethics_net_keeps_its_finding_when_no_doctrine_grounds() -> None:
    """WHAT IS WITHDRAWN IS THE CLAIM, NOT THE VERDICT.

    The ethical strain is caught by this net's own instrument. Dropping the
    finding because a SECOND instrument could not corroborate it would be a net
    overruling itself with someone else's silence - and it would un-scar
    `Honesty is pointless.` across four end-to-end test files.

    What changes is that the note stops asserting a specific doctrine is at
    stake when it cannot name one, and the payload becomes an HONEST ZERO: an
    instrument ran over the real store and found nothing.
    """
    result = _wired()._net_ethics("truth does not matter")

    assert result.survived is False
    assert result.pressure == pytest.approx(0.85)
    assert result.evidence.countability is Countability.NONE_FOUND
    assert "no load-bearing doctrine" in result.note


def test_the_ethics_net_still_abstains_with_no_spine() -> None:
    """Three states, and the third one. NOT_COUNTABLE is now specifically about
    THIS CONSTRUCTION having no spine - not about the net being shallow, which
    is what the reason string used to say and no longer does."""
    result = _bare()._net_ethics("truth does not matter")

    assert result.survived is False
    assert result.evidence.countability is Countability.NOT_COUNTABLE
    assert "no doctrine spine" in result.evidence.uncountable_reason


def test_the_ethics_net_asks_about_load_bearing_doctrines_only() -> None:
    """It uses the SPINE'S OWN `load_bearing()` at the Spine's own default,
    rather than a locally chosen number.

    The note's word is "load-bearing"; the Spine owns what that means (Scar
    Bloom >= 3, the corpus's convergence magnitude); a second definition here
    would be free to drift from it.

    STRENGTHENED AFTER A SURVIVING MUTANT. The first version of this test named
    `AVT.002`, which has ZERO scars - so it is excluded at `min_scars=3` AND at
    `min_scars=1`, and the assertion could not tell the two apart. Swapping the
    default for `min_scars=1` passed the whole file. `AVT.001` carries EXACTLY
    ONE scar, which is the only configuration that distinguishes them.
    """
    net = _wired()
    codex = Codex()
    assert len(codex.get("AVT.001").scar_links) == 1, (
        "precondition: exactly one scar - inside load_bearing(1), outside the "
        "default of 3, which is what makes this test able to see the difference")

    grounded = {d.id for d in net.doctrine_spine.load_bearing()}
    assert "AVT.001" not in grounded
    assert "AVT.001" in {d.id for d in net.doctrine_spine.load_bearing(min_scars=1)}

    result = net._net_ethics("truth does not matter, Paradox Suspension Law is wrong")
    assert result.evidence.countability is Countability.NONE_FOUND, (
        "a doctrine that is not load-bearing cannot be what the claim would "
        "require abandoning - and widening the query to min_scars=1 would make "
        "AVT.001 ground it")

    # And the zero-scar case, which the original version of this test covered.
    assert "AVT.002" not in grounded
    assert _wired()._net_ethics(
        "truth does not matter, Curiosity Loop is wrong"
    ).evidence.countability is Countability.NONE_FOUND


# =====================================================================
# G. STRUCTURAL - the overlay must not become a gate
# =====================================================================

def _echonet_tree() -> ast.AST:
    import src.filtration.echonet as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        return ast.parse(f.read())


def test_the_overlay_pressure_is_only_ever_the_two_existing_magnitudes() -> None:
    """RULING 49 COINS NO MAGNITUDE, and this is the assertion rather than the
    claim. Stage 3's pressures are `SUSPENSION_FLOOR` and `SUSTAINED_STRAIN`,
    both already in the file, reused for what they already mean.

    AST rather than behavioural: a run can only show that whatever number
    someone wrote did not appear on the inputs someone picked.
    """
    fn = next(n for n in ast.walk(_echonet_tree())
              if isinstance(n, ast.FunctionDef) and n.name == "_overlay_pressure")
    literals = [n.value for n in ast.walk(fn)
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool)]
    assert literals == [], (
        f"_overlay_pressure carries numeric literals {literals}. Stage 3's "
        f"magnitudes are SUSPENSION_FLOOR and SUSTAINED_STRAIN by NAME - a "
        f"literal here is a coined constant wearing an expression's clothes.")

    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert {"SUSPENSION_FLOOR", "SUSTAINED_STRAIN"} <= names


def test_the_overlay_is_not_fed_back_into_convergent_elimination() -> None:
    """Convergence is a property of the SIX NETS straining together (canon's
    Scar Bloom >= 3 over Stage 2). Feeding a LATER stage back into an EARLIER
    one would let Stage 3 manufacture a Stage 2 verdict - and convergent
    elimination is the one net that can FAIL a claim on accumulated strain.
    """
    fn = next(n for n in ast.walk(_echonet_tree())
              if isinstance(n, ast.FunctionDef) and n.name == "filter_claim")
    lines = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            lines[node.func.attr] = node.lineno

    assert lines["_net_convergent_elimination"] < lines["_stage3_overlay"], (
        "Stage 3 runs AFTER Stage 2's sixth net, and its result is never an "
        "input to it")


def test_stage_3_owns_no_verdict() -> None:
    """The overlay contributes pressure and never appears in `failed`.

    SCARRED and PARADOX both require a failed NET, so a stage that cannot be a
    net cannot reach either. Structural, checked at the source, because the
    behavioural version can only sample.
    """
    fn = next(n for n in ast.walk(_echonet_tree())
              if isinstance(n, ast.FunctionDef) and n.name == "filter_claim")
    failed_assign = next(
        n for n in ast.walk(fn)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "failed" for t in n.targets))
    assert "overlay" not in ast.dump(failed_assign.value), (
        "the overlay must not enter `failed` - that list is what routes a claim "
        "to SCARRED and PARADOX, and Stage 3 owns no verdict")


# =====================================================================
# H. RIDER - InvalidMutationProof joins STRUCTURAL_VIOLATIONS
# =====================================================================

def test_invalid_mutation_proof_is_a_structural_violation() -> None:
    """RULING 49's rider, adjudicating the question Ruling 48 escalated.

    `InvalidMutationProof` is a deliberate raise guarding a gate meant to be
    impossible to pass - a malformed proof reaching the executor means the
    constructor-gate failed. Ruling 48 declined to add it on its own authority
    because membership here is a DECISION; the forty-fourth entry made it.

    Unreachability from `process_input` does not disqualify it: other members
    guard rarely-reached paths, and it becomes reachable the day a second
    `mutate_doctrine` call site appears - on which day this membership is
    already correct rather than discovered by a guard degrading into a string.
    """
    from src.aurea_core import STRUCTURAL_VIOLATIONS
    from src.doctrine.mutation_proof import InvalidMutationProof

    assert InvalidMutationProof in STRUCTURAL_VIOLATIONS

    for member in STRUCTURAL_VIOLATIONS:
        others = [o for o in STRUCTURAL_VIOLATIONS if o is not member]
        assert not any(issubclass(o, member) for o in others), (
            f"{member.__name__} is a base class of another member - the tuple "
            f"is CLOSED and its members are concrete (Ruling 25)")


def test_the_taxonomy_is_a_tuple_of_concrete_names_not_a_base_class() -> None:
    """AST. The tuple's membership must stay an enumerated DECISION.

    A base class here would widen the set silently the next time anyone
    subclassed it, which is the one thing Ruling 25 says this tuple exists to
    prevent.
    """
    import src.aurea_core as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    assign = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "STRUCTURAL_VIOLATIONS"
                for t in n.targets))
    assert isinstance(assign.value, ast.Tuple)
    names = {e.id for e in assign.value.elts if isinstance(e, ast.Name)}
    assert len(names) == len(assign.value.elts), (
        "every member must be a plain concrete name")
    assert "InvalidMutationProof" in names
