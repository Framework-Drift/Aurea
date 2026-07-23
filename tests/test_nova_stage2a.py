"""
test_nova_stage2a.py - Nova Stage 2a: Nova in the loop, ZERO mutation risk.

Two facts are pinned here, and they are the whole point of the 2a/2b split:

DOCKET C (the reason 2a exists): `aurea_core._evolve_doctrine` used to pass
`context={d: {'echo_origin': True} for d in signals}` - hardcoding, for EVERY
doctrine, the claim that a Nova echo underwrote it. CMTE criterion 2 is an OR
(`dee.py`: `if not doctrine.scar_links and not context.get("echo_origin")`),
so a doctrine with NO scar links passed the gate whose law is "No belief may
evolve unless the fracture that broke it can still be seen" - on a false
claim. Harmless only while `proposals=None`. Now `echo_origin` is DERIVED
from real Nova state: True for a doctrine only when an echo actually erupted
from that doctrine's strain. Never a literal again.

ZERO MUTATION RISK: Nova is constructed and live in AureaCore, but the
`proposals` seam stays None - nothing can mutate doctrine while no proposed
form exists (SAE needs one). The pin on `proposals is None` is the 2a
boundary; Stage 2b removes it DELIBERATELY, not by drift.

The DEE-cycle spy pattern follows test_ril_pipeline_integration.py: control
the one seam the decision passes through, run everything else real.

DO NOT weaken these tests.
"""

from unittest.mock import patch

from src.aurea_core import AureaCore
from src.expansion.nova import NovaEngine
from src.filtration.echonet import Verdict as EchoVerdict


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
# Docket C: echo_origin is DERIVED, never a literal
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


def test_echo_origin_is_true_only_for_the_strained_doctrine():
    """A real doctrine_strain echo flips echo_origin for ITS doctrine only.
    The v1 bearing rule is conservative: eruption FROM the doctrine's strain,
    nothing broader."""
    aurea, result = _aurea_with_real_scar()
    strained_id = next(iter(aurea.codex.view()))
    aurea.nova.erupt("doctrine_strain", strained_id)

    captured = _spy_evolve(aurea, result)

    assert captured["context"][strained_id]["echo_origin"] is True
    for doctrine_id, ctx in captured["context"].items():
        if doctrine_id != strained_id:
            assert ctx["echo_origin"] is False, (
                "an echo bears on the doctrine it erupted from - not on "
                "every doctrine in the codex")


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
# The 2a boundary: proposals stays None - mutation structurally impossible
# ---------------------------------------------------------------------

def test_stage_2a_passes_no_proposals_to_dee():
    """ZERO MUTATION RISK is a structural property, not a promise: with
    proposals=None, SAE has no form to execute and eligible doctrines can
    only ferment. Stage 2b removes this pin deliberately - if it goes red
    any other way, the mutation path opened by drift."""
    aurea, result = _aurea_with_real_scar()
    captured = _spy_evolve(aurea, result)
    assert captured["proposals"] is None
