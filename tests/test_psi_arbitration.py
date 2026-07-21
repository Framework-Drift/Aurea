"""
test_psi_arbitration.py - Ruling 8 Stage 2: PSI wired and arbitrated through the REAL
Grid + RACM (no mocking of arbitration - the test_anchor_collapse_lock discipline).

SEQUENCING RULING (2026-07-20): PSI's same-cycle deferral behind ACR on anchor_collapse
is CANONICAL. ACR (rank 4) suppresses on cycle N; PSI (rank 5) executes the aftermath
from RACM's deferral queue on a later cycle (aging +1/deferred cycle, cap +2). The
one-cycle lag is the architecture working - these tests assert the deferral, they do
not work around it.

RULING 9 (2026-07-20) - THE QUEUE-EXECUTION PATH, CLOSED
---------------------------------------------------------
Stage 2 pinned a seam here: RACM authorized a queued claim's later execution, but the
Grid executed only same-cycle-triggered reflexes, so a queue winner whose reflex did
not re-trigger was authorized and silently dropped. Ruling 9 closed it: the Grid now
resolves authorized claims against the FULL registry, rebuilding the winner's trigger
from its own claim payload (its original pressure, never the current cycle's), and
Ruling 9 pt.3 canonized DEFERRED-WINS-TIES as an explicit RACM sort key (previously
emergent from _merge_with_queue insertion order + stable sort).

The formerly-pinned test is flipped below to assert the ruled behavior. One boundary
Ruling 9 did NOT move: the Grid still arbitrates only when some reflex triggers - on
a truly silent cycle the queue simply holds (aging) until the next live arbitration,
whatever pressure drives it.
"""

import pytest

from src.aurea_core import AureaCore
from src.identity.compass import MAX_DRIFT
from src.identity.psi import PSI, PSIDirective
from src.identity.ril import RIL
from src.reflex.racm import RACM, ReflexClaim, Verdict
from src.reflex.reflex_grid import ReflexGrid
from src.utils.models import Scar

HARD_PRESSURE = 26.0 / MAX_DRIFT     # past the 25 deg hard-kill line, ACR + PSI bands


def _grounded_grid(scarline=True):
    """Real Grid + real RACM + real RIL; PSI registered the aurea_core way
    (add_reflex with injected handles). GSR's file-writing alert callback is swapped
    for a no-op (the test_anchor_collapse_lock discipline) though nothing here
    reaches GSR's 0.85 threshold."""
    grid = ReflexGrid()
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None
    ril = RIL()
    if scarline:
        ril.ingest_scar(Scar(id="Scar-001", name="Scar-001", origin="test", weight=2.0))
    psi = PSI(ril=ril, scar_core=None)
    grid.add_reflex(psi)
    return grid, psi


def _emit_anchor_collapse(grid):
    return grid.evaluate_pressure(
        source_module="CSE",
        pressure_type="anchor_collapse",
        pressure_level=HARD_PRESSURE,
        metadata={"drift": 26.0},
    )


# ---------------------------------------------------------------------
# Wiring: aurea_core constructs and registers PSI with injected handles
# ---------------------------------------------------------------------

def test_aurea_core_registers_psi_with_injected_handles():
    aurea = AureaCore()
    assert "PSI" in aurea.reflex_grid.reflexes
    assert aurea.reflex_grid.reflexes["PSI"] is aurea.psi
    assert aurea.psi.ril is aurea.ril
    assert aurea.psi.scar_core is aurea.scar_core


def test_bare_grid_has_no_psi():
    """The Grid's argless slot stays commented: PSI without its handles would be a
    permanently-abstaining ghost. A bare ReflexGrid deliberately has no PSI."""
    assert "PSI" not in ReflexGrid().reflexes


# ---------------------------------------------------------------------
# Cycle 1: ACR executes, PSI defers - the canonical sequencing
# ---------------------------------------------------------------------

def test_cycle1_acr_executes_and_psi_defers():
    grid, psi = _grounded_grid()

    responses = _emit_anchor_collapse(grid)

    acr = next((r for r in responses if r.reflex_id == "ANCHOR_COLLAPSE"), None)
    assert acr is not None and acr.action == "suppress" and acr.output_blocked is True

    assert not any(r.reflex_id == "PSI" for r in responses), (
        "PSI must not co-execute with ACR - overlapping affected_systems, lower rank")
    assert psi.activation_count == 0

    result = grid.racm.last_result
    assert result.verdict_for("ANCHOR_COLLAPSE") is Verdict.EXECUTE
    assert result.verdict_for("PSI") is Verdict.DEFERRED
    assert grid.racm.is_deferred("PSI"), "PSI's claim must sit in RACM's queue"


# ---------------------------------------------------------------------
# Cycle 2, transient collapse: the queue-won claim EXECUTES (Ruling 9) -
# the formerly-pinned seam, flipped to the ruled behavior
# ---------------------------------------------------------------------

def test_foreign_pressure_no_longer_drives_the_queue_psi_claim_holds():
    """[Ruling 10 correction, 2026-07-20] This test previously asserted that a
    scar_density@0.5 cycle surfaced the queued PSI claim - which only worked because
    magnitude spillover let ACR claim scar_density and drive an arbitration (the
    false-lock seam Ruling 10 closed at the claim). Ruled behavior: scar_density@0.5
    is NOBODY'S claim (ACR is {anchor_collapse}-gated; GSR's open gate needs 0.85),
    so no arbitration runs at all and PSI's queued claim simply HOLDS - deferred,
    honest, not executed and not dropped. The Ruling-9 queue-execution machinery
    itself stays adversarially pinned in
    test_queue_win_executes_against_its_original_trigger_ica below."""
    grid, psi = _grounded_grid()
    _emit_anchor_collapse(grid)                       # cycle 1: PSI -> queue
    assert grid.racm.is_deferred("PSI")
    assert psi.activation_count == 0
    cycle_before = grid.racm.cycle

    responses = grid.evaluate_pressure(
        source_module="scar_core", pressure_type="scar_density",
        pressure_level=0.5, metadata={"active_scars": 50})

    assert responses == []
    assert grid.racm.cycle == cycle_before, (
        "no reflex claims scar_density@0.5 post-gate - no arbitration may even run")
    assert grid.racm.is_deferred("PSI"), "the queued claim holds; it does not vanish"
    assert psi.activation_count == 0, (
        "and PSI must NOT execute on the back of a foreign pressure type")


def test_queue_win_executes_against_its_original_trigger_ica():
    """[Ruling 10 re-target, 2026-07-20] The Ruling-9 adversarial pin: a queue winner
    executes via full-registry resolution against a trigger REBUILT from its own
    claim, never the current cycle's pressure. Previously demonstrated with PSI
    riding a scar_density spillover cycle; post-gate, rank geometry makes a transient
    PSI queue-win unreachable (see the report/module docstring), so the same
    machinery is pinned with ICA: deferred behind GSR on identity_fracture@0.86
    (both claim it - ICA in-set, GSR open), aged ICA (rank 2-1=1) then wins a cycle
    driven by anchor_collapse@0.25, a type ICA does NOT accept - proving it executed
    from the queue against its reconstructed identity_fracture trigger."""
    grid = ReflexGrid()
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None

    grid.evaluate_pressure(
        source_module="RIL", pressure_type="identity_fracture",
        pressure_level=0.86, metadata={"doctrine_id": "AVT.002"})
    assert grid.racm.last_result.verdict_for("GSR") is Verdict.EXECUTE
    assert grid.racm.last_result.verdict_for("ICA") is Verdict.DEFERRED
    assert grid.racm.is_deferred("ICA")

    ica = grid.reflexes["ICA"]
    received = []
    original_trigger = ica.trigger
    ica.trigger = lambda t: (received.append(t), original_trigger(t))[1]

    responses = grid.evaluate_pressure(
        source_module="CSE", pressure_type="anchor_collapse",
        pressure_level=0.25, metadata={"drift": 22.5})

    assert grid.racm.last_result.verdict_for("ICA") is Verdict.EXECUTE
    assert grid.racm.last_result.verdict_for("ANCHOR_COLLAPSE") is Verdict.DEFERRED

    assert len(received) == 1, "ICA executes exactly once, from the queue"
    got = received[0]
    assert got.trigger_type == "identity_fracture", (
        "the reconstructed trigger must carry the claim's own type - ICA cannot even "
        "CLAIM this cycle's anchor_collapse, so receiving it would be a false event")
    assert got.pressure_level == pytest.approx(0.86)
    assert got.source_module == "RIL"
    assert got.metadata.get("doctrine_id") == "AVT.002", "original claim metadata rides"

    ica_response = next(r for r in responses if r.reflex_id == "ICA")
    assert ica_response.action == "reroute", "0.86 is ICA's reroute band - its OWN band"


# ---------------------------------------------------------------------
# Sustained pressure: the loop closes through the Grid - PSI executes
# with its directive by cycle 3 at the latest (aging; actually cycle 2)
# ---------------------------------------------------------------------

def test_sustained_pressure_psi_executes_by_cycle3_with_directive():
    grid, psi = _grounded_grid()

    psi_response = None
    executed_on_cycle = None
    for cycle in (1, 2, 3):
        responses = _emit_anchor_collapse(grid)
        psi_response = next((r for r in responses if r.reflex_id == "PSI"), None)
        if psi_response is not None:
            executed_on_cycle = cycle
            break

    assert psi_response is not None, "sustained pressure must surface PSI via aging"
    assert executed_on_cycle <= 3, "aging (+1/cycle, cap +2) bounds the wait"
    assert executed_on_cycle >= 2, "cycle 1 belongs to ACR - the ruled sequencing"

    # The executed aftermath carries the parked directive, grounded in Scarline.
    directive = psi_response.metadata["psi_directive"]
    assert isinstance(directive, PSIDirective)
    assert directive.scar_ref == "Scar-001"
    assert psi_response.metadata["directive_parked"] is True

    # At the hard band PSI PROPOSES the lock; RACM authorized it (it executed), so
    # a caller applying the reflex-agnostic Ruling-6 gate would lock on this.
    assert psi_response.action == "suppress"
    assert psi_response.output_blocked is True

    # And the cycle PSI won, ACR was the one deferred - contention, not co-execution.
    result = grid.racm.last_result
    assert result.verdict_for("PSI") is Verdict.EXECUTE
    assert result.verdict_for("ANCHOR_COLLAPSE") is Verdict.DEFERRED


# ---------------------------------------------------------------------
# Tie-break pin: aged-PSI(4) vs fresh-ACR(4) -> the DEFERRED claim wins,
# by ruled key (Ruling 9 pt.3), not by merge insertion order
# ---------------------------------------------------------------------

def test_tie_break_deferred_claim_wins_by_ruled_key():
    """Cycle 1 defers PSI behind ACR. Cycle 2: aging lifts PSI to effective rank 4,
    tying fresh ACR's base 4 - and the explicit secondary key (deferral seniority,
    Ruling 9 pt.3 canonized 2026-07-20) hands the tie to the deferred claim. Asserted
    straight against RACM with fresh claims passed ACR-first, so no Grid ordering or
    dict-insertion accident can be what passes this."""
    racm = RACM()

    def claims():
        return [
            ReflexClaim(reflex_id="ANCHOR_COLLAPSE", pressure_level=HARD_PRESSURE,
                        affected_systems=frozenset({"identity", "doctrine", "output"}),
                        source_module="CSE"),
            ReflexClaim(reflex_id="PSI", pressure_level=HARD_PRESSURE,
                        affected_systems=frozenset({"identity", "output"}),
                        source_module="CSE"),
        ]

    r1 = racm.arbitrate(claims())
    assert r1.verdict_for("ANCHOR_COLLAPSE") is Verdict.EXECUTE
    assert r1.verdict_for("PSI") is Verdict.DEFERRED

    r2 = racm.arbitrate(claims())
    assert r2.verdict_for("PSI") is Verdict.EXECUTE, (
        "at equal effective rank the deferred claim must win - ruled, not emergent")
    assert r2.verdict_for("ANCHOR_COLLAPSE") is Verdict.DEFERRED


# ---------------------------------------------------------------------
# Abstain through the spine: empty Scarline -> PSI monitors, no directive,
# no lock proposal, output flows
# ---------------------------------------------------------------------

def test_abstain_through_the_spine_with_empty_scarline():
    grid, psi = _grounded_grid(scarline=False)

    psi_response = None
    for _ in (1, 2, 3):
        responses = _emit_anchor_collapse(grid)
        psi_response = next((r for r in responses if r.reflex_id == "PSI"), None)
        if psi_response is not None:
            break

    assert psi_response is not None, "PSI still wins its arbitration cycle - "  \
        "grounding is checked at trigger time, not at claim time"
    assert psi_response.action == "monitor"
    assert psi_response.output_blocked is False
    assert "psi_directive" not in psi_response.metadata, (
        "no grounded bearing -> no directive, never a fabricated one")

    # Output flows: nothing in PSI's executed cycle proposed a lock.
    assert not any(r.output_blocked for r in responses)
