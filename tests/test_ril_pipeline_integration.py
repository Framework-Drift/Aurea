"""
test_ril_pipeline_integration.py - RIL Stage 2: the identity terminus wired into the real
pipeline (aurea_core.py). Asserts the loop closes: collapse -> scar -> RIL (Scarline/
Origin), and doctrine mutation -> RIL (Doctrine), against the SAME live AureaCore instance
- its real EchoNet, SBSRE, ScarLogicCore, Codex, DEE, SAE, and RIL, not stand-ins.

WHY THE DOCTRINE LEG DOES NOT ROUTE THROUGH `process_input` ALONE
-------------------------------------------------------------------
`aurea_core._evolve_doctrine` always calls `self.dee.cycle(..., proposals=None, ...)`
(CLAUDE.md Sec 8: Nova, the doctrine-content author, is unbuilt). With no proposed form
ever supplied, DEE can only FERMENT an eligible doctrine, never APPROVE one - so
`ruling.executed_by == 'SAE'` is, by design, unreachable through `process_input` today.
That is correct behavior, not a gap (dee.py's own docstring says the same). The RIL
doctrine-handoff wiring this test covers is therefore the same kind of "ready, not yet
reachable" code as the pre-existing `stats['doctrines_mutated']` counter it sits beside.

To exercise that wiring for real without inventing a Nova, this test controls the one
seam DEE's decision passes through - `aurea.dee.cycle` - exactly as
test_anchor_collapse_lock.py controls compass's `_north`/`_south`/`_drift` seam to reach a
specific state. Everything downstream of that seam (`aurea._evolve_doctrine`'s own code,
`aurea.codex.get`, `aurea.ril.ingest_doctrine_mutation`) runs unmodified and real.
"""

from unittest.mock import patch

from src.aurea_core import AureaCore
from src.filtration.echonet import Verdict as EchoVerdict
from src.doctrine.dee import EligibilityRuling, Verdict as DEEVerdict
from src.identity.ril import IdentityThread


def test_collapse_to_scar_to_doctrine_populates_ril_identity_threads():
    aurea = AureaCore()

    # ---- COLLAPSE -> SCAR -> RIL (Scarline / Origin) ----
    # "Honesty is pointless." clears the ethics net at pressure 0.85 (>= BASE_THRESHOLD
    # 0.75) without tripping the logic net's paradox path (worst.net != logical_
    # contradiction), so EchoNet returns Verdict.SCARRED. _echonet_resolver reads that
    # verdict as "irreconcilable" on SBSRE's first cycle, so the contradiction chamber
    # collapses immediately (LoopOutcome.COLLAPSE) and requests a scar - the real,
    # un-mocked pipeline path, not a shortcut to one.
    result = aurea.process_input("Honesty is pointless.", source="test")

    assert result["collapse_result"].verdict is EchoVerdict.SCARRED
    scar = result["scar_formed"]
    assert scar is not None, "expected the contradiction chamber to collapse and form a scar"

    # UPDATED 2026-07-27 (Ruling 42 res.2 + res.3). Ruling-14 precedent,
    # old/new verbatim:
    #
    #     OLD: assert aurea.ril.threads[SCARLINE] == [scar]
    #          assert aurea.ril.threads[ORIGIN]   == [scar], (
    #              "first scar RIL ever ingests must seed ORIGIN exactly once")
    #     NEW: SCARLINE compared by record id; ORIGIN asserted to be the
    #          CONSTITUTIONAL seed record `Scar-0`, with provenance.
    #
    # WHY, and the second half is a RULING and not a shape change:
    #   res.2 - threads hold by-ID references, not embedded `Scar` objects.
    #   res.3 - ORIGIN IS CONSTITUTIONAL. In a live pipeline the scar owner is
    #     present, so RIL resolves ORIGIN from the seed record tagged `origin`
    #     BEFORE any runtime scar exists. The first runtime scar therefore no
    #     longer claims ORIGIN - which is the entire point of the ruling. The
    #     old assertion documented the defect: her birth identity was whatever
    #     she happened to collapse on first after a restart.
    #
    # NOT A WEAKENING. The written-once guarantee is asserted MORE strongly
    # here than before: ORIGIN is pinned to a specific, tracked, constitutional
    # record rather than to "whatever arrived first", and the run-to-run
    # variability the old assertion tolerated is now a red test.
    assert [e["record_id"] for e in aurea.ril.threads[IdentityThread.SCARLINE]] == [scar.id]

    origin = aurea.ril.threads[IdentityThread.ORIGIN]
    assert [e["record_id"] for e in origin] == ["Scar-0"], (
        "ORIGIN is CONSTITUTIONAL (Ruling 42 res.3) - the seed record tagged "
        "`origin`, not the first scar that happened to arrive")
    assert origin[0]["provenance"] == "constitutional"

    # ---- DOCTRINE MUTATION -> RIL (Doctrine) ----
    # See module docstring: DEE's decision is controlled here because nothing in the live
    # pipeline authors a `proposals` entry yet (Nova is unbuilt) - the real gap this
    # patches around, not a convenience shortcut around a reachable path.
    fake_ruling = EligibilityRuling(
        doctrine_id="AVT.002",
        verdict=DEEVerdict.APPROVED,
        executed_by="SAE",
        reason="test-forced approval - see module docstring",
    )
    with patch.object(aurea.dee, "cycle", return_value=[fake_ruling]):
        report = aurea._evolve_doctrine(result, result["collapse_result"])

    assert report["mutated"] == 1

    doctrine_thread = aurea.ril.threads[IdentityThread.DOCTRINE]
    assert len(doctrine_thread) == 1
    assert doctrine_thread[0]["doctrine_id"] == "AVT.002"
    assert doctrine_thread[0]["verdict"] is DEEVerdict.APPROVED

    # AVT.002 is a seed doctrine with no mutation_lineage, so RIL correctly finds no
    # fallen ancestor to ground a fracture in and abstains - VOID stays empty. This is
    # the "ground it or abstain" discipline the module docstring documents, not a miss.
    assert aurea.ril.threads[IdentityThread.VOID] == []
