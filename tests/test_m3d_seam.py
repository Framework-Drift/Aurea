"""
M3-D COMMIT 1 - THE ADMISSION SEAM, THE CLOCK, AND THE GATE.

Three properties, each with its own reason to exist:

  * **ADMISSION NEVER GATES A PROTECTIVE RESPONSE.** Ruling 11's line - a
    logging failure must not disable a safety suppression - applied to the
    obligation seam. An identity fracture fires whether or not the obligation
    can be written, and the failure is RECORDED rather than lost.
  * **THE WALL CLOCK LEAVES GSR'S LOGIC PATH.** A protective reflex measured
    cascade in wall seconds, so the same sequence of events read as a cascade
    on a fast run and as calm on a slow one.
  * **THE KIND'S NAME IS ITS INTERPRETATION.** A CONFIRMED prediction cannot
    ground a "failed precommitted prediction" defeater.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.external.prediction_ledger import (
    PredictionLedger, PredictionOutcome, provided,
)
from src.filtration.episode_record import (
    DefeaterKind, EpisodeRecord, OutcomeDoesNotDefeat, PrecedenceProofFailed,
)
from src.filtration.obligation_ledger import (
    ObligationLedger, ObligationRecordType, RejectionKind, TargetKind,
    TargetResolution,
)
from src.external.claim_ancestry import ClaimAncestryLedger
from src.reflex.reflex_grid import GSR, ReflexTrigger

REPO = Path(__file__).resolve().parents[1]
CORE_SRC = REPO / "src" / "aurea_core.py"
GRID_SRC = REPO / "src" / "reflex" / "reflex_grid.py"


# =====================================================================
# A. §1.2 - TargetKind.CLAIM
# =====================================================================

def test_a_claim_is_the_fourth_member_and_the_vocabulary_is_closed():
    """PIN A1. Widened by ONE, by ruling - never by a caller's string.

    CHANGED BY A RULING, 2026-08-15 (M6-γ) - the Ruling-14 precedent, and this
    pin did EXACTLY what it exists for. Recorded verbatim:

        OLD (M3-D, 2026-08-13):
            assert {m.value for m in TargetKind} == {
                "doctrine", "scar", "suspension", "claim"}
        NEW (M6-γ):
            ... the same four PLUS "world_proposition"

    **NOTHING WAS WEAKENED - A NAME WAS ADDED TO A CLOSED SET BY A RULING**, and
    the assertion is still EXACT rather than a superset check, which is what made
    the widening arrive as a deliberate edit here instead of slipping in. The
    eighty-first manifest entry rules it: a world-model inconsistency is a
    conflict candidate routed into L4, and it is owed about the PROPOSITION that
    carries it. M6-γ's own pins live in `tests/test_m6_worldmodel.py`.
    """
    assert {m.value for m in TargetKind} == {
        "doctrine", "scar", "suspension", "claim", "world_proposition"}


def test_a_a_recorded_claim_resolves(tmp_path):
    """PIN A2. **A RECORDED CLAIM ALWAYS RESOLVES** - claims are never erased,
    which is the fossil-resolves rule's sibling."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    record = ancestry.record()
    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           ancestry_ledger=ancestry)
    result = led.admit("aurea_core.collapse", TargetKind.CLAIM,
                       record.claim_id, "the claim contradicts itself")
    assert result.admitted
    assert result.target_resolution is TargetResolution.RESOLVED


def test_a_an_unrecorded_claim_is_targetless(tmp_path):
    """PIN A3. The rejection is a RECORD, as every refused admission is."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           ancestry_ledger=ancestry)
    result = led.admit("s", TargetKind.CLAIM, "CLM-9999", "c")
    assert result.rejection_kind is RejectionKind.TARGETLESS
    assert led.read_all()[0]["record_type"] == ObligationRecordType.REJECTED.value


def test_a_no_ancestry_ledger_is_unchecked_not_targetless(tmp_path):
    """PIN A4. Docket H's cut holds for the new kind too."""
    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"))
    result = led.admit("s", TargetKind.CLAIM, "CLM-0001", "c")
    assert result.admitted
    assert result.target_resolution is TargetResolution.UNCHECKED


def test_a_resolution_never_writes_the_ancestry_ledger(tmp_path):
    """PIN A5 - THE RESOLVER IS A READ. Proved by the ledger's own BYTES.

    M3-A's `retrieve` discovery generalised: a store handed to a resolver for
    one question must not be answerable with others.
    """
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    record = ancestry.record()
    path = Path(ancestry.ledger_path)
    before = path.read_bytes()
    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           ancestry_ledger=ancestry)
    led.admit("s", TargetKind.CLAIM, record.claim_id, "c")
    led.admit("s", TargetKind.CLAIM, "CLM-9999", "c")
    assert path.read_bytes() == before


def test_a_the_three_original_kinds_are_unmoved(tmp_path):
    """PIN A6. Widening the enum moved nothing about the kinds already in it."""
    class _Codex:
        fossils = {}

        def get(self, _):
            return object()

    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           codex=_Codex())
    assert led.admit("s", TargetKind.DOCTRINE, "D", "c").admitted
    assert led.admit("s", TargetKind.SCAR, "S", "c").target_resolution \
        is TargetResolution.UNCHECKED
    assert led.admit("s", TargetKind.SUSPENSION, "X", "c").target_resolution \
        is TargetResolution.UNCHECKED


# =====================================================================
# B. §1.5 - THE FALSIFIED GATE
# =====================================================================

def _prediction(tmp_path, outcome, criterion="failure_criteria"):
    ledger = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    # All three criteria are declared at commit: the ledger refuses a
    # resolution naming one that was never committed, which is that store
    # working - so a fixture exercising an UNRESOLVED outcome must have
    # committed an unresolved criterion beforehand.
    commitment = ledger.commit(
        expected_result="the bridge holds",
        success_criteria=provided("no deflection"),
        failure_criteria=provided("visible deflection"),
        unresolved_criteria=provided("the load test never ran"))
    ledger.resolve(commitment.prediction_id, outcome, criterion=criterion)
    return ledger, commitment


def test_b_a_confirmed_prediction_cannot_ground_a_failed_defeater(tmp_path):
    """PIN B1 - THE FORCING PIN. **RED FIRST.**

    M3-B flagged this and declined to decide it; the sixty-seventh entry ruled
    it. The kind's name IS its interpretation, and a defeater citing a
    prediction that HELD is a record contradicting itself.
    """
    ledger, commitment = _prediction(tmp_path, PredictionOutcome.CONFIRMED,
                                     criterion="success_criteria")
    log = EpisodeRecord(log_path=str(tmp_path / "epi.jsonl"),
                        prediction_ledger=ledger)
    episode = log.open_episode(["OBL-0001"], 5)
    with pytest.raises(OutcomeDoesNotDefeat):
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": commitment.prediction_id})
    assert log.defeaters(episode) == (), "a refused registration wrote a record"


def test_b_a_falsified_prediction_still_registers(tmp_path):
    """PIN B2 - THE CONTROL. The gate is a CUT, not a blanket refusal."""
    ledger, commitment = _prediction(tmp_path, PredictionOutcome.FALSIFIED)
    log = EpisodeRecord(log_path=str(tmp_path / "epi.jsonl"),
                        prediction_ledger=ledger)
    episode = log.open_episode(["OBL-0001"], 5)
    log.register_defeater(episode, DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                          {"prediction_id": commitment.prediction_id})
    assert log.defeaters(episode)[0]["interpretation"]["recorded_outcome"] \
        == "falsified"


def test_b_an_unresolved_outcome_is_refused_too(tmp_path):
    """PIN B3. UNRESOLVED is a real recorded outcome and it defeats nothing."""
    ledger, commitment = _prediction(tmp_path, PredictionOutcome.UNRESOLVED,
                                     criterion="unresolved_criteria")
    log = EpisodeRecord(log_path=str(tmp_path / "epi.jsonl"),
                        prediction_ledger=ledger)
    episode = log.open_episode(["OBL-0001"], 5)
    with pytest.raises(OutcomeDoesNotDefeat):
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": commitment.prediction_id})


def test_b_the_gate_is_a_distinct_type_from_the_precedence_proof():
    """PIN B4 - RULING 29. Different CAUSES get different TYPES.

    "Precedence failed" about a perfectly well-ordered CONFIRMED prediction
    would send a caller looking for a corrupted ledger and find nothing wrong.
    """
    assert not issubclass(OutcomeDoesNotDefeat, PrecedenceProofFailed)
    assert not issubclass(PrecedenceProofFailed, OutcomeDoesNotDefeat)


# =====================================================================
# C. §1.4 - THE EVENT-TIME FIX
# =====================================================================

def _gsr_trigger(cycle, pressure=0.5):
    return ReflexTrigger(reflex_id="GSR", trigger_type="cascade",
                         pressure_level=pressure, source_module="test",
                         metadata={"cycle": cycle})


def test_c_cascade_is_measured_in_cycles_not_seconds():
    """PIN C1. Four events inside the 5-cycle window is a cascade."""
    gsr = GSR()
    for cycle in range(4):
        gsr.cascade_events.append({"cycle": cycle, "pressure": 0.9})
    assert gsr.detect_cascade(_gsr_trigger(4)) is True


def test_c_events_outside_the_window_do_not_count():
    """PIN C2. The same four events, now old, are not a cascade."""
    gsr = GSR()
    for cycle in range(4):
        gsr.cascade_events.append({"cycle": cycle, "pressure": 0.9})
    assert gsr.detect_cascade(_gsr_trigger(100)) is False


def test_c_the_window_is_five_cycles_and_the_limit_is_three():
    """PIN C3. 5 is the corpus's standard horizon, RECOVERED not coined; the
    event limit of 3 is PRE-EXISTING and UNMOVED."""
    assert GSR.CASCADE_WINDOW_CYCLES == 5
    assert GSR.CASCADE_EVENT_LIMIT == 3
    gsr = GSR()
    for cycle in (0, 1, 2, 3):
        gsr.cascade_events.append({"cycle": cycle, "pressure": 0.9})
    # cycle 4: all four are within 5 -> cascade. cycle 5: event 0 falls out.
    assert gsr.detect_cascade(_gsr_trigger(4)) is True
    assert gsr.detect_cascade(_gsr_trigger(5)) is False


def test_c_no_wall_clock_in_the_detection_path():
    """PIN C4 - THE PROPERTY. `detect_cascade` reads no clock at all.

    A suspended AUREA (Rider R2 - a mind that is not running does not age its
    wounds) aged out of cascade state while doing nothing whatsoever.
    """
    for node in ast.walk(ast.parse(GRID_SRC.read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef) and node.name == "detect_cascade":
            for sub in ast.walk(node):
                assert not (isinstance(sub, ast.Attribute)
                            and sub.attr in ("now", "utcnow")), (
                    "detect_cascade reads a wall clock")
                assert not (isinstance(sub, ast.Name)
                            and sub.id == "datetime"), (
                    "detect_cascade names datetime")
            return
    raise AssertionError("detect_cascade not found")


def test_c_an_unplaceable_event_is_not_counted():
    """PIN C5. An event with no recorded cycle cannot be placed in the window.

    Admitting it "just in case" would let an unplaceable event push the system
    into a total output block.
    """
    gsr = GSR()
    for _ in range(9):
        gsr.cascade_events.append({"cycle": None, "pressure": 0.9})
    assert gsr.detect_cascade(_gsr_trigger(3)) is False
    # ... and a trigger with no cycle detects nothing rather than everything.
    assert gsr.detect_cascade(ReflexTrigger(
        reflex_id="GSR", trigger_type="cascade", pressure_level=0.9,
        source_module="t", metadata={})) is False


def test_c_the_grid_stamps_the_cycle_onto_every_trigger():
    """PIN C6. The stamp is what makes the window measurable at all."""
    from src.reflex.reflex_grid import ReflexGrid
    grid = ReflexGrid()
    grid.racm.cycle = 7
    grid.evaluate_pressure(source_module="test", pressure_type="scar_density",
                           pressure_level=0.1)
    assert grid.active_triggers[-1].metadata["cycle"] == 7


def test_c_a_caller_supplied_cycle_is_not_overwritten():
    """PIN C7. `setdefault`: the stamp fills a gap, never overrides a source
    that knows better."""
    from src.reflex.reflex_grid import ReflexGrid
    grid = ReflexGrid()
    grid.racm.cycle = 7
    grid.evaluate_pressure(source_module="test", pressure_type="scar_density",
                           pressure_level=0.1, metadata={"cycle": 2})
    assert grid.active_triggers[-1].metadata["cycle"] == 2


# =====================================================================
# D. §1.3 - THE ADMISSION SEAM
# =====================================================================

class _Exploding:
    """A ledger whose door always fails. The seam must not care."""

    def admit(self, **kwargs):
        raise OSError("disk is gone")


def test_d_ril_admits_the_fracture(tmp_path):
    """PIN D1. The obligation exists, targeting the fractured doctrine."""
    from src.identity.ril import RIL
    from src.utils.models import Doctrine

    class _Codex:
        fossils = {}

        def get(self, _):
            return object()

    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           codex=_Codex())
    ril = RIL(obligation_ledger=led)
    doctrine = Doctrine(id="D-1", name="n", description="d")

    class _Ruling:
        reason = "ancestor fell"

    ril._fire_ica(doctrine, "D-0", _Ruling())
    items = led.open_items()
    assert len(items) == 1
    assert items[0]["target_id"] == "D-1"
    assert items[0]["target_kind"] == TargetKind.DOCTRINE.value
    assert items[0]["source"] == "RIL"
    assert "D-0" in items[0]["claim_text"]


def test_d_a_failing_admission_never_gates_the_fracture(tmp_path):
    """PIN D2 - THE LOAD-BEARING HALF. Ruling 11's line.

    A protective response must fire even when its record cannot be written.
    The failure is RECORDED, which is what makes it not a silent loss.
    """
    from src.identity.ril import RIL
    from src.utils.models import Doctrine

    fired = []

    class _Grid:
        def evaluate_pressure(self, **kwargs):
            fired.append(kwargs)
            return ["response"]

    ril = RIL(reflex_grid=_Grid(), obligation_ledger=_Exploding())

    class _Ruling:
        reason = "r"

    responses = ril._fire_ica(Doctrine(id="D-1", name="n", description="d"),
                              "D-0", _Ruling())
    assert responses == ["response"], "the admission failure GATED the reflex"
    assert len(fired) == 1
    assert len(ril.admission_failures) == 1
    assert "OSError" in ril.admission_failures[0]["error"]


def test_d_a_bare_ril_admits_nothing(tmp_path):
    """PIN D3. `None` is the honest default - incidental construction writes
    no obligation."""
    from src.identity.ril import RIL
    from src.utils.models import Doctrine

    class _Ruling:
        reason = "r"

    ril = RIL()
    assert ril.obligation_ledger is None
    ril._fire_ica(Doctrine(id="D-1", name="n", description="d"), "D-0", _Ruling())
    assert ril.admission_failures == []


def test_d_racm_admits_one_obligation_per_unsettled_lineage(tmp_path):
    """PIN D4. A saturated epoch is one owed thing PER LINEAGE, not one total.

    Collapsing them would lose exactly the fact the epoch is saturated ABOUT.
    """
    from src.reflex.racm import RACM

    class _Codex:
        fossils = {}

        def get(self, _):
            return object()

    led = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                           codex=_Codex())
    racm = RACM(runtime_path=str(tmp_path / "q.json"), obligation_ledger=led)
    racm.rb.DEFAULT_LOG_PATH = str(tmp_path / "rb.jsonl")
    racm.record_saturation_pressure(epoch=2, blocked_cycles=6, horizon=5,
                                    unsettled_lineages=["D-1", "D-2", "D-3"])
    assert sorted(i["target_id"] for i in led.open_items()) == ["D-1", "D-2", "D-3"]
    assert all(i["source"] == "SAE" for i in led.open_items())


def test_d_the_rb_record_is_written_before_the_admission(tmp_path):
    """PIN D5 - ADDITIVE. The forensic entry exists whatever the seam does."""
    from src.reflex.racm import RACM
    racm = RACM(runtime_path=str(tmp_path / "q.json"),
                obligation_ledger=_Exploding())
    entry_id = racm.record_saturation_pressure(
        epoch=1, blocked_cycles=6, horizon=5, unsettled_lineages=["D-1"])
    assert entry_id, "the RB entry did not survive a failing admission"
    assert len(racm.admission_failures) == 1


def test_d_the_seam_enters_only_through_admit():
    """PIN D6. No seam site writes the ledger by any other door."""
    for rel in ("src/identity/ril.py", "src/reflex/racm.py"):
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                target = getattr(node.func, "value", None)
                attr = getattr(node.func, "attr", None)
                if (isinstance(target, ast.Attribute)
                        and target.attr == "obligation_ledger"):
                    assert attr == "admit", (
                        f"{rel}:{node.lineno} calls `{attr}` on the obligation "
                        f"ledger - admissions enter ONLY through `admit`")


# =====================================================================
# E. §1.1 - COMPOSITION IS NOT INVOCATION
# =====================================================================

def test_e_the_core_composes_both_stores():
    """PIN E1. One of each, held as members, resolvers wired."""
    from src.aurea_core import AureaCore
    core = AureaCore()
    assert core.obligations is not None and core.episodes is not None
    assert core.obligations.codex is core.codex
    assert core.obligations.scar_core is core.scar_core
    assert core.obligations.ancestry_ledger is core.ancestry
    assert len(core.obligations.suspension_systems) == 3


def test_e_the_two_stores_share_one_clock():
    """PIN E2. M3-A left the coordinator unbuilt and named this as where it
    lands: wired as a PAIR, the logical clock is genuinely shared."""
    from src.aurea_core import AureaCore
    core = AureaCore()
    assert Path(core.episodes.log_path) in tuple(core.obligations.peer_paths)
    assert Path(core.obligations.ledger_path) in tuple(core.episodes.peer_paths)


def test_e_construction_alone_writes_no_obligation_and_no_episode(tmp_path):
    """PIN E3 - COMPOSITION ONLY. Invariant 27's needle: admission is neither
    arbitration nor execution, and building a core is not admitting anything."""
    from src.aurea_core import AureaCore
    core = AureaCore()
    assert core.obligations.read_all() == ()
    assert core.episodes.read_all() == ()


def test_e_the_core_holds_no_scheduler_for_either_store():
    """PIN E4. No loop, no timer, no internal caller of a store's doors."""
    tree = ast.parse(CORE_SRC.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            attr = getattr(node.func, "attr", None)
            target = getattr(node.func, "value", None)
            if attr in ("open_episode", "record_pressure", "disposition") and \
                    isinstance(target, ast.Attribute) and target.attr == "episodes":
                # Commit 2 introduces the ruled episode path; before it, none
                # exist. Either way there is no LOOP driving them: this pin
                # asserts they are never called from a `while` body.
                parents = [n for n in ast.walk(tree)
                           if isinstance(n, ast.While) and node in ast.walk(n)]
                assert parents == [], (
                    f"an episode door is driven from a `while` loop at line "
                    f"{node.lineno} - the substrate never runs itself")


# =====================================================================
# F. GAPS FOUND BY THE MUTATION SLATE (M3-D follow-up)
# =====================================================================

def test_f_an_unplaceable_trigger_is_refused_before_the_arithmetic():
    """PIN F1 - FOUND BY SURVIVOR C1-09, and it was a REAL GAP.

    C5 above drives a no-cycle trigger against events that ALSO carry no cycle,
    so the per-event `isinstance` filter empties the list and the function
    returns False for a reason unrelated to the guard under test. Deleting the
    guard therefore survived. The configuration that separates them is a
    no-cycle TRIGGER against events that DO carry cycles - where the missing
    guard makes `None - int` raise `TypeError` inside a protective reflex.
    """
    gsr = GSR()
    for cycle in range(4):
        gsr.cascade_events.append({"cycle": cycle, "pressure": 0.9})
    unplaceable = ReflexTrigger(reflex_id="GSR", trigger_type="cascade",
                                pressure_level=0.9, source_module="t",
                                metadata={})
    assert gsr.detect_cascade(unplaceable) is False, (
        "an unplaceable trigger must report NO detectable cascade - and it "
        "must not raise inside a protective reflex to do it")


def test_f_the_surviving_status_surface_reports_the_clamp():
    """PIN F2 - FOUND BY SURVIVOR R-03. The retirement narrowed `status()` to
    the one thing still true; nothing asserted it still says anything."""
    from src.reflex.sbsre import BASELINE, CEILING, FLOOR, SBSRE
    status = SBSRE().status()
    assert status == {"clamp": {"baseline": BASELINE, "floor": FLOOR,
                                "ceiling": CEILING}}
    for gone in ("threads_run", "suppressed_patterns", "outcomes"):
        assert gone not in status, (
            f"`{gone}` came back - its backing state is deleted, so it could "
            f"only report a permanent zero about machinery that no longer runs")
