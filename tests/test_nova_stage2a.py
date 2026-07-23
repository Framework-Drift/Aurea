"""
test_nova_stage2a.py - Nova Stage 2a: Nova in the loop, ZERO mutation risk.

Stage 2 was split by RISK. 2a makes Nova live and observable while doctrine
mutation stays STRUCTURALLY IMPOSSIBLE - `proposals=None`, so SAE has no form
to execute. This file pins the gates 2b will depend on, so they are honest
BEFORE the mutation path opens:

  Docket C  echo_origin is DERIVED from real Nova state, never hardcoded True.
            A scar-less doctrine with no bearing echo now correctly FAILS
            CMTE criterion 2 ("no_scar_lineage") - the free pass is gone.
  STEP 3    Nova's suppression read is expansion-halt, NOT output_blocked
            (a render state). GSR's suspend targets ["expansion","nova"] with
            output_blocked=False - the exact case conflating the two misses.
  STEP 4    Eruption traces to a real record: doctrine strain from DEE's DMW
            watch. G1 raises on a fabricated origin, so an echo existing IS
            proof its origin was real.
  STEP 5    Compass EAST reads real Nova state (active_echoes); empty index
            reports empty, honestly.
  Boundary  proposals is STILL None at the DEE call site (guard test).

The dee-seam control pattern (seeding DMW, spying dee.cycle) follows
test_ril_pipeline_integration.py: control the one real seam a decision passes
through, run everything else real. DO NOT weaken these tests.
"""

from unittest.mock import patch

import pytest

from src.aurea_core import AureaCore
from src.doctrine.dee import CMTE, _Watched
from src.expansion.nova import FermentationStatus, NovaEngine
from src.filtration.echonet import Verdict as EchoVerdict
from src.identity.compass import Direction
from src.reflex.reflex_grid import ReflexResponse


def _aurea_with_real_scar():
    """A live AureaCore driven through the real collapse->scar path (the
    'Honesty is pointless.' input from the RIL pipeline test), so
    _evolve_doctrine has a genuine scar to signal from."""
    aurea = AureaCore()
    result = aurea.process_input("Honesty is pointless.", source="test")
    assert result["collapse_result"].verdict is EchoVerdict.SCARRED
    assert result["scar_formed"] is not None
    return aurea, result


def _spy_evolve(aurea, result):
    """Run _evolve_doctrine for real, capturing exactly what it hands DEE."""
    captured = {}

    def spy(signals=None, proposals=None, context=None):
        captured["signals"] = signals
        captured["proposals"] = proposals
        captured["context"] = context
        return []

    with patch.object(aurea.dee, "cycle", side_effect=spy):
        aurea._evolve_doctrine(result, result["collapse_result"])
    return captured


# ---------------------------------------------------------------------
# Nova is constructed and owned by the core
# ---------------------------------------------------------------------

def test_aurea_core_constructs_a_nova_engine():
    aurea = AureaCore()
    assert isinstance(aurea.nova, NovaEngine)
    assert aurea.nova.echo_index == {}, "no echoes at boot - nothing erupts yet"


# ---------------------------------------------------------------------
# PIN 1 - Docket C: echo_origin FALSE with no bearing echo, and a scar-less
#         doctrine consequently FAILS criterion 2. (The whole point.)
# ---------------------------------------------------------------------

def test_echo_origin_is_false_for_every_doctrine_when_no_echo_exists():
    """The hardcode is gone. With an empty echo index, no doctrine may claim
    an echo origin - criterion 2 falls back to requiring real scar_links."""
    aurea, result = _aurea_with_real_scar()
    captured = _spy_evolve(aurea, result)

    assert captured["context"], "context is still supplied per doctrine"
    for doctrine_id, ctx in captured["context"].items():
        assert ctx["echo_origin"] is False, (
            f"'{doctrine_id}' claims an echo origin with an EMPTY echo index "
            f"- the fabrication is back")
        assert "echo_resonance" not in ctx, (
            "no real resonance value exists in the organ - supplying one "
            "would be fabrication; absence is DEE's own semantics")


def test_scarless_doctrine_now_fails_criterion2_that_the_hardcode_masked():
    """The consequence that names the fix. AVT.002 is a scar-less seed. With
    the DERIVED echo_origin=False (what aurea now produces for a no-bearing
    doctrine), CMTE criterion 2 fails 'no_scar_lineage'. The old hardcoded
    True masked exactly this - so the same doctrine is shown passing under
    True and failing under False, on one real doctrine."""
    aurea = AureaCore()
    doctrine = aurea.codex.get("AVT.002")
    assert doctrine.scar_links == [], "AVT.002 is the scar-less seed"

    cmte = CMTE()
    # pressure clears criterion 1 so only criterion 2 is in question here.
    watched = _Watched(doctrine_id="AVT.002", pressure=0.9, sustained_cycles=3)

    failed_derived = cmte.validate(doctrine, watched, {"echo_origin": False})
    assert "no_scar_lineage" in failed_derived, (
        "a scar-less doctrine with no bearing echo must NOT evolve - the "
        "fracture that broke it cannot be seen")

    failed_hardcode = cmte.validate(doctrine, watched, {"echo_origin": True})
    assert "no_scar_lineage" not in failed_hardcode, (
        "this is what the old {'echo_origin': True} hardcode did for EVERY "
        "doctrine - a free pass on a false claim, harmless only while "
        "proposals=None")


# ---------------------------------------------------------------------
# PIN 2 - echo_origin TRUE only when a real echo bears on that doctrine
# ---------------------------------------------------------------------

def test_a_merely_existing_echo_no_longer_grants_echo_origin():
    """SUPERSEDES `test_echo_origin_is_true_only_for_the_strained_doctrine`
    by RULING 14 (2026-07-23). The RULING moved - the code was not made
    convenient. Reported verbatim in the session record.

    OLD PIN (Stage 2a v1 bearing rule, now wrong):
        aurea.nova.erupt("doctrine_strain", strained_id)
        assert captured["context"][strained_id]["echo_origin"] is True
      i.e. an echo that merely BEARS on d granted d eligibility.

    NEW PIN (Ruling 14): echo_origin[d] is True iff a PROPOSAL for d exists
    AND the echo recorded as authoring it is MUTATED and scar-linked. So the
    v1 trigger - an erupted doctrine_strain echo, alone - now grants NOTHING.

    WHY v1 WAS WRONG: a doctrine-strain echo of a SCAR-LESS doctrine is
    scar-less by construction, so it could never author a proposal - yet v1
    would have granted that scar-less belief eligibility to evolve, which is
    exactly the free pass criterion 2 exists to deny. A scar-less doctrine's
    own strain is not a fracture.

    The TRUE half of Ruling 14 (a real survived backing echo) is pinned in
    tests/test_nova_stage2b.py.
    """
    aurea, result = _aurea_with_real_scar()
    strained_id = next(iter(aurea.codex.view()))
    aurea.nova.erupt("doctrine_strain", strained_id)

    captured = _spy_evolve(aurea, result)

    assert captured["context"][strained_id]["echo_origin"] is False, (
        "a merely-existing echo is not a SURVIVED one (Ruling 14)")
    for doctrine_id, ctx in captured["context"].items():
        assert ctx["echo_origin"] is False


def test_non_strain_echoes_do_not_claim_doctrine_bearing():
    """A scar-origin echo does NOT set echo_origin for any doctrine - that
    inference would be a weaker re-fabrication of the same false claim.
    Broadening the bearing rule is a ruling, not an edit."""
    aurea, result = _aurea_with_real_scar()
    aurea.nova.erupt("scar", result["scar_formed"].id)

    captured = _spy_evolve(aurea, result)

    for doctrine_id, ctx in captured["context"].items():
        assert ctx["echo_origin"] is False


# ---------------------------------------------------------------------
# PIN 3 - suppression is EXPANSION-HALT, not output_blocked
# ---------------------------------------------------------------------

def _resp(action, target_modules, output_blocked):
    return ReflexResponse(reflex_id="TEST", action=action,
                          target_modules=target_modules,
                          output_blocked=output_blocked)


def test_expansion_suspension_halts_nova_even_when_output_is_not_blocked():
    """GSR's selective suspend: action='suspend', targets ['expansion','nova'],
    output_blocked=FALSE. Nova MUST defer - and a render-flag read would miss
    it entirely."""
    aurea = AureaCore()
    responses = [_resp("suspend", ["expansion", "nova"], output_blocked=False)]
    assert aurea._nova_suppressed(responses) is True

    echo = aurea.nova.erupt("scar", "S-1")
    aurea._nova_cycle(responses)
    assert echo.status is FermentationStatus.DORMANT, "no activation under halt"
    assert aurea.nova.refusals[-1]["action"] == "cycle", "deference is legible"


def test_cascade_targeting_all_halts_nova():
    aurea = AureaCore()
    responses = [_resp("cascade", ["all"], output_blocked=True)]
    assert aurea._nova_suppressed(responses) is True


def test_output_block_for_unrelated_reasons_does_NOT_halt_nova():
    """An ICA suppress blocking OUTPUT (targets output/doctrine) is a render
    state - 'she does not speak'. Expansion is not halted. Nova cycles."""
    aurea = AureaCore()
    responses = [_resp("suppress", ["output", "doctrine"], output_blocked=True)]
    assert aurea._nova_suppressed(responses) is False, (
        "render-block is not expansion-halt - conflating them is the "
        "convenient-flag error")

    echo = aurea.nova.erupt("scar", "S-1")
    aurea._nova_cycle(responses)
    assert echo.status is FermentationStatus.ACTIVE, (
        "output blocked, but expansion free - Nova ferments normally")


def test_no_responses_means_no_suppression():
    aurea = AureaCore()
    assert aurea._nova_suppressed([]) is False


# ---------------------------------------------------------------------
# PIN 4 - a real system event erupts an echo with a traceable origin
# ---------------------------------------------------------------------

def test_doctrine_strain_from_dmw_watch_erupts_a_traceable_echo():
    """DEE's DMW queue holds real Codex doctrines under sustained strain.
    Seeding a real slot (a real doctrine id) and cycling Nova erupts a
    doctrine_strain echo whose origin traces to that doctrine - and whose
    scar_links are the doctrine's OWN, nothing invented. G1 would have raised
    on a fabricated origin, so the echo's existence proves the trace."""
    aurea = AureaCore()
    doctrine = aurea.codex.get("AVT.001")
    assert doctrine is not None and doctrine.scar_links, "real, scar-linked"
    aurea.dee.dmw.queue["AVT.001"] = _Watched(doctrine_id="AVT.001",
                                              pressure=0.8, sustained_cycles=3)

    aurea._nova_cycle([])   # unsuppressed

    echoes = [e for e in aurea.nova.echo_index.values()
              if e.origin_kind == "doctrine_strain" and e.origin_id == "AVT.001"]
    assert len(echoes) == 1, "the watched doctrine erupted exactly one echo"
    assert echoes[0].scar_links == doctrine.scar_links, "real scar links, carried"


def test_doctrine_strain_eruption_dedups_per_doctrine():
    """A doctrine strained across many cycles yields ONE echo, not one per
    cycle - minimal dedup (full Nova Echo Crosscheck is not-yet-wired)."""
    aurea = AureaCore()
    aurea.dee.dmw.queue["AVT.001"] = _Watched(doctrine_id="AVT.001",
                                              pressure=0.8, sustained_cycles=3)
    aurea._nova_cycle([])
    aurea._nova_cycle([])
    aurea._nova_cycle([])

    strain = [e for e in aurea.nova.echo_index.values()
              if e.origin_id == "AVT.001"]
    assert len(strain) == 1, "one echo per strained doctrine, not one per cycle"


# ---------------------------------------------------------------------
# PIN 5 - compass EAST reads real Nova state; empty reports empty
# ---------------------------------------------------------------------

def test_compass_east_empty_index_reports_empty():
    aurea = AureaCore()
    east = aurea.compass.read().anchors[Direction.EAST]
    assert east.mass == 0.0, "no echoes - EAST is honestly empty, not faked"
    assert east.members == []


def test_compass_east_reflects_active_nova_echoes():
    """An ACTIVE (pulling) echo shows up in EAST: mass counts it (uniform 1.0,
    no coined heat), members names it. DORMANT echoes do not pull yet."""
    aurea = AureaCore()
    echo = aurea.nova.erupt("scar", "S-1")

    # DORMANT: awaiting context, not yet pulling.
    east_dormant = aurea.compass.read().anchors[Direction.EAST]
    assert east_dormant.mass == 0.0, "a dormant echo does not pull"

    # One unsuppressed cycle activates it -> now it pulls.
    aurea.nova.cycle(suppressed=False)
    assert echo.status is FermentationStatus.ACTIVE
    east_active = aurea.compass.read().anchors[Direction.EAST]
    assert east_active.mass == 1.0, "one active echo, weighted 1.0 (count, not heat)"
    assert echo.id in east_active.members


def test_active_echoes_accessor_returns_active_only():
    aurea = AureaCore()
    dormant = aurea.nova.erupt("scar", "S-1")
    assert aurea.nova.active_echoes() == [], "dormant is not pulling"
    aurea.nova.cycle(suppressed=False)
    assert aurea.nova.active_echoes() == [dormant]


# ---------------------------------------------------------------------
# PIN 6 - the 2a boundary: proposals stays None (mutation impossible)
# ---------------------------------------------------------------------

def test_stage_2a_passes_no_proposals_to_dee():
    """ZERO MUTATION RISK is a structural property, not a promise: with
    proposals=None, SAE has no form to execute and eligible doctrines can
    only ferment. Stage 2b removes this pin deliberately - if it goes red
    any other way, the mutation path opened by drift."""
    aurea, result = _aurea_with_real_scar()
    captured = _spy_evolve(aurea, result)
    assert captured["proposals"] is None
