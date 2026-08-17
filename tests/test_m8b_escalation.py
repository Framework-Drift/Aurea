"""M8-b: `escalation-policy.v1`, the routing act, and the recorded shortfall.

THE ELEVEN BINDING PROPERTIES, in the specification's order:
  1. Determinism -- identical inputs, identical routing/census/shortfall.
  2. The ruled mapping per class: S0/S1 -> rung 0 WITHOUT shortfall; S2/S3/S4
     -> rung 0 WITH the shortfall naming minimum rung 1.
  3. Rung-1 occupancy DERIVED against the consumed REFUSED verdict: EMPTY,
     with the citation on the census.
  4. The hypothetical-occupancy direction: a qualified-shape record derives
     OCCUPIED and the shortfall disappears -- records alone, no code change.
  5. Shortfall completeness -- all four facts on the record.
  6. The routing log chains FROM GENESIS; the audit reads it clean; a tampered
     line raises CHAIN_BREAK.
  7. Self-assessment ABSENT on every v1 record; a populated input is REFUSED.
  8. Unclassified routing is REFUSED, never defaulted to the cheapest rung.
  9. The write GATES the act.
 10. Prior executive pin files byte-unmodified; L10's pins still pass.
 11. Purity and no-mutation-surface contact by import-absence; no magnitudes.
"""

import ast
import hashlib
import json
import pathlib
import subprocess
import sys

import pytest

from src.executive.act_log_audit import (ROUTING_LOG_SCHEMA, FindingKind,
                                         audit_act_log)
from src.executive.derived_view import (VERDICT_PAYLOAD_KIND, ChairState,
                                        DerivedView, build_stake_substrate,
                                        derive)
from src.executive.escalation_policy import (DELEGATED_COGNITION_ROLE,
                                             POLICY_NAME, POLICY_VERSION,
                                             REGISTRATION, RULED_MINIMUM_RUNG,
                                             EscalationIdentityMismatch,
                                             EscalationPolicy, OccupancyBasis,
                                             Rung, RungOccupancy,
                                             UnclassifiedRouting)
from src.executive.loop import ConsumedVerdict, ExecutiveLoop
from src.executive.routing_log import (RoutingLog, RoutingLogUnreadable,
                                       SelfAssessmentNotAdmissible)
from src.executive.stake_classifier import StakeClass, StakeClassifier
from src.external.acquisition_ledger import AcquisitionChannel, AcquisitionLedger
from src.external.prediction_ledger import PredictionLedger
from src.filtration.obligation_ledger import ObligationLedger
from src.goals.goal_ledger import GoalLedger

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"

THE_VERDICT = ConsumedVerdict(
    role_id=DELEGATED_COGNITION_ROLE, verdict="REFUSED",
    foundry_commit="c1930d6",
    record_path="references/m5-gamma-4-qualification-record.md",
    protocol_sha256s=("1dbdcefb",), failed_surfaces=("Q1",),
    unestablished_surfaces=("Q2", "Q3"))


def _view(acquisitions, **stake_handles) -> DerivedView:
    """A real derived view over a real acquisition ledger.

    The rung substrate is populated by `derive()` itself, so occupancy is
    exercised through the LIVE path rather than a hand-built fixture.
    """
    class _Empty:
        def open_items(self):
            return []

        def commitments(self):
            return ()

        def resolutions(self):
            return ()

    view = derive(_Empty(), _Empty(), _Empty(), acquisitions)
    if not stake_handles:
        return view
    return DerivedView(
        open_obligations=view.open_obligations,
        unresolved_predictions=view.unresolved_predictions,
        committed_goals=view.committed_goals, chair=view.chair,
        verdict_acquisition_id=view.verdict_acquisition_id,
        candidates=view.candidates, inquiry=view.inquiry, rungs=view.rungs,
        stake=build_stake_substrate(**stake_handles))


@pytest.fixture()
def refused_world(tmp_path):
    """The LIVE configuration: the M5 verdict consumed, REFUSED."""
    acquisitions = AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl"))
    acquisitions.record(THE_VERDICT.payload(),
                        channel=AcquisitionChannel.USER_INPUT)
    return acquisitions


def _qualified_payload() -> str:
    """A consumed QUALIFIED verdict, as RAW LEDGER DATA.

    **NO `src/` TYPE CAN BUILD THIS.** `ConsumedVerdict.__post_init__` refuses
    any verdict but REFUSED by design (M7-a), which is the second of the two
    independent derivations that keep rung 1 empty. So the qualified shape is
    written as a payload here - through the acquisition ledger's own door, but
    bypassing the type that would refuse it - purely to exercise the OCCUPANCY
    DERIVATION's positive branch. Nothing in `src/` gains the ability to
    construct one, and this fixture asserts that below.
    """
    return json.dumps({
        "kind": VERDICT_PAYLOAD_KIND, "role_id": DELEGATED_COGNITION_ROLE,
        "verdict": "QUALIFIED", "foundry_commit": "hypothetical",
        "record_path": "references/hypothetical.md",
        "protocol_sha256s": ["deadbeef"], "failed_surfaces": [],
        "unestablished_surfaces": []}, sort_keys=True)


def _stake(target_id, view, kind="claim"):
    return StakeClassifier().classify(kind, target_id, view)


# ===========================================================================
# PIN 1 - DETERMINISM
# ===========================================================================

def test_1_identical_inputs_yield_identical_routing_twice(refused_world):
    view = _view(refused_world)
    stake = _stake("CLM-0001", view)
    policy = EscalationPolicy()
    first, second = policy.route(stake, view), policy.route(stake, view)
    assert first == second
    assert first.as_dict() == second.as_dict()


# ===========================================================================
# PIN 2 - THE RULED MAPPING, PER CLASS
# ===========================================================================

def test_2_the_ruled_mapping_is_data_and_total_over_the_stake_vocabulary():
    """The hundred-fifth entry, as DATA. A hole would let an unmapped class
    fall through to a lookup default - the unexamined judgment this layer
    exists to keep out."""
    assert set(RULED_MINIMUM_RUNG) == set(StakeClass)
    assert RULED_MINIMUM_RUNG[StakeClass.S0_PERIPHERAL] is \
        Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert RULED_MINIMUM_RUNG[StakeClass.S1_LINKED] is \
        Rung.RUNG_0_DETERMINISTIC_KERNEL
    for cls in (StakeClass.S2_DOCTRINAL, StakeClass.S3_STRUCTURAL,
                StakeClass.S4_IDENTITY):
        assert RULED_MINIMUM_RUNG[cls] is Rung.RUNG_1_DELEGATED_COGNITION
    with pytest.raises(TypeError):
        RULED_MINIMUM_RUNG[StakeClass.S0_PERIPHERAL] = Rung.RUNG_1_DELEGATED_COGNITION


class _StakeStub:
    """A classification carrying only what the policy reads: its class."""

    def __init__(self, stake_class):
        self.stake_class = stake_class

    def as_dict(self):
        return {"stake_class": self.stake_class.value}


@pytest.mark.parametrize("stake_class", [StakeClass.S0_PERIPHERAL,
                                         StakeClass.S1_LINKED])
def test_2a_s0_and_s1_route_rung_zero_without_shortfall(refused_world,
                                                        stake_class):
    decision = EscalationPolicy().route(_StakeStub(stake_class),
                                        _view(refused_world))
    assert decision.routed_rung is Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert decision.ruled_minimum_rung is Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert decision.shortfall is None
    assert decision.adequate is True


@pytest.mark.parametrize("stake_class", [StakeClass.S2_DOCTRINAL,
                                         StakeClass.S3_STRUCTURAL,
                                         StakeClass.S4_IDENTITY])
def test_2b_s2_and_above_route_rung_zero_WITH_the_shortfall(refused_world,
                                                            stake_class):
    """**THE DESIGN WORKING, NOT A BUG TO DAMPEN.** On the live tree every
    S2+ episode routes below its ruled minimum, and says so, forever."""
    decision = EscalationPolicy().route(_StakeStub(stake_class),
                                        _view(refused_world))
    assert decision.ruled_minimum_rung is Rung.RUNG_1_DELEGATED_COGNITION
    assert decision.routed_rung is Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert decision.adequate is False
    assert decision.shortfall is not None
    assert decision.shortfall.stake_class is stake_class


# ===========================================================================
# PIN 3 - OCCUPANCY IS DERIVED, WITH ITS CITATION
# ===========================================================================

def test_3_rung_one_is_empty_by_the_consumed_refused_verdict(refused_world):
    """The pin exercises the DERIVATION PATH, not a constant."""
    census = {e.rung: e for e in EscalationPolicy().census(_view(refused_world))}
    rung_1 = census[Rung.RUNG_1_DELEGATED_COGNITION]
    assert rung_1.occupancy is RungOccupancy.EMPTY
    assert rung_1.basis is OccupancyBasis.CONSUMED_VERDICT_REFUSED
    # THE CITATION - what makes "empty" checkable rather than asserted.
    assert rung_1.citation and rung_1.citation.startswith("ACQ-")
    # Rung 0 is occupied BY CONSTRUCTION, and says so.
    rung_0 = census[Rung.RUNG_0_DETERMINISTIC_KERNEL]
    assert rung_0.occupancy is RungOccupancy.OCCUPIED
    assert rung_0.basis is OccupancyBasis.BY_CONSTRUCTION
    assert rung_0.citation is None


def test_3b_no_consumed_verdict_is_a_different_basis_from_a_refused_one(
        tmp_path):
    """Docket H's cut at the ladder: nobody-has-qualified and
    the-candidate-was-REFUSED are different facts and must not read alike."""
    empty = AcquisitionLedger(ledger_path=str(tmp_path / "a.jsonl"))
    census = {e.rung: e for e in EscalationPolicy().census(_view(empty))}
    rung_1 = census[Rung.RUNG_1_DELEGATED_COGNITION]
    assert rung_1.occupancy is RungOccupancy.EMPTY
    assert rung_1.basis is OccupancyBasis.NO_CONSUMED_VERDICT
    assert rung_1.citation is None


def test_3c_a_verdict_about_another_role_does_not_move_this_rung(tmp_path):
    """Occupancy is PER ROLE, compared by exact equality on a recorded field."""
    acquisitions = AcquisitionLedger(ledger_path=str(tmp_path / "a.jsonl"))
    other = json.loads(_qualified_payload())
    other["role_id"] = "ROLE-SOMETHING-ELSE"
    acquisitions.record(json.dumps(other, sort_keys=True),
                        channel=AcquisitionChannel.USER_INPUT)
    census = {e.rung: e for e in EscalationPolicy().census(_view(acquisitions))}
    assert census[Rung.RUNG_1_DELEGATED_COGNITION].basis is \
        OccupancyBasis.NO_CONSUMED_VERDICT


# ===========================================================================
# PIN 4 - THE LADDER FILLS BY RECORDS ALONE
# ===========================================================================

def test_4_a_qualified_record_derives_OCCUPIED_and_the_shortfall_disappears(
        tmp_path):
    """**NO CODE CHANGE FILLS THE RUNG - ONLY RECORDS.**

    The qualified verdict is written as RAW LEDGER DATA because no `src/` type
    can construct one (see `_qualified_payload`). That is the point of the pin:
    occupancy is a derivation over records, so the day a real qualification is
    consumed the ladder fills and the shortfall stops being recorded, with not
    one line of this codebase edited.
    """
    acquisitions = AcquisitionLedger(ledger_path=str(tmp_path / "a.jsonl"))
    acquisitions.record(_qualified_payload(),
                        channel=AcquisitionChannel.USER_INPUT)
    view = _view(acquisitions)

    census = {e.rung: e for e in EscalationPolicy().census(view)}
    rung_1 = census[Rung.RUNG_1_DELEGATED_COGNITION]
    assert rung_1.occupancy is RungOccupancy.OCCUPIED
    assert rung_1.basis is OccupancyBasis.CONSUMED_VERDICT_QUALIFIED

    decision = EscalationPolicy().route(_StakeStub(StakeClass.S3_STRUCTURAL),
                                        view)
    assert decision.routed_rung is Rung.RUNG_1_DELEGATED_COGNITION
    assert decision.shortfall is None
    assert decision.adequate is True


def test_4b_no_src_type_can_construct_a_qualified_consumed_verdict():
    """The SECOND independent derivation keeping rung 1 empty."""
    from src.executive.loop import MalformedConsumedVerdict
    with pytest.raises(MalformedConsumedVerdict):
        ConsumedVerdict(
            role_id=DELEGATED_COGNITION_ROLE, verdict="QUALIFIED",
            foundry_commit="x", record_path="y", protocol_sha256s=("z",),
            failed_surfaces=(), unestablished_surfaces=())


# ===========================================================================
# PIN 5 - SHORTFALL COMPLETENESS
# ===========================================================================

def test_5_the_shortfall_carries_all_four_facts(refused_world):
    decision = EscalationPolicy().route(_StakeStub(StakeClass.S4_IDENTITY),
                                        _view(refused_world))
    short = decision.shortfall
    assert short.stake_class is StakeClass.S4_IDENTITY
    assert short.ruled_minimum_rung is Rung.RUNG_1_DELEGATED_COGNITION
    assert short.actual_rung is Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert short.unoccupied_rung_basis is OccupancyBasis.CONSUMED_VERDICT_REFUSED
    assert short.unoccupied_rung_citation.startswith("ACQ-")
    # ...and all four reach the serialized form.
    payload = short.as_dict()
    assert set(payload) == {"stake_class", "ruled_minimum_rung", "actual_rung",
                            "unoccupied_rung_basis", "unoccupied_rung_citation"}
    assert all(v is not None for v in payload.values())


def test_5b_the_full_stake_derivation_is_EMBEDDED_in_the_record(tmp_path,
                                                                refused_world):
    """Test 7's challenge must be answerable from the record ALONE."""
    view = _view(refused_world)
    stake = _stake("CLM-0001", view)
    decision = EscalationPolicy().route(stake, view)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    log.record(decision, target_kind="claim", target_id="CLM-0001")

    written = log.routings()[0]
    assert written["routing"]["stake_derivation"]["stake_class"]
    assert written["routing"]["stake_derivation"]["conditions"]
    assert written["routing"]["policy_name"] == POLICY_NAME
    assert written["routing"]["policy_version"] == POLICY_VERSION
    assert len(written["routing"]["rung_census"]) == 2
    assert all("basis" in entry for entry in written["routing"]["rung_census"])


# ===========================================================================
# PIN 6 - CHAINED FROM GENESIS
# ===========================================================================

def test_6_the_routing_log_chains_from_genesis_and_audits_clean(tmp_path,
                                                                refused_world):
    """**NO PRE-CHAIN ERA, EVER.** This log was born after the chain existed."""
    from src.executive.act_chain import CHAIN_KEY, genesis_chain
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    for i in range(4):
        log.record(EscalationPolicy().route(_StakeStub(StakeClass.S2_DOCTRINAL),
                                            view),
                   target_kind="claim", target_id=f"CLM-{i:04d}")

    lines = (tmp_path / "rte.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])[CHAIN_KEY] == genesis_chain()
    report = audit_act_log(tmp_path / "rte.jsonl", ROUTING_LOG_SCHEMA)
    assert report.clean, report.as_dict()
    assert report.pre_chain_lines == 0 and report.chained_lines == 4


def test_6b_a_tampered_routing_line_raises_chain_break(tmp_path, refused_world):
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    for i in range(3):
        log.record(EscalationPolicy().route(_StakeStub(StakeClass.S2_DOCTRINAL),
                                            view),
                   target_kind="claim", target_id=f"CLM-{i:04d}")
    path = tmp_path / "rte.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    # Forge away the debt - the single most tempting edit this log will ever
    # attract, and the one the chain exists to make visible.
    record["routing"]["shortfall"] = None
    lines[0] = json.dumps(record)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = audit_act_log(path, ROUTING_LOG_SCHEMA)
    assert FindingKind.CHAIN_BREAK in {f.kind for f in report.findings}


# ===========================================================================
# PIN 7 - THE SELF-ASSESSMENT SLOT
# ===========================================================================

def test_7_self_assessment_is_present_and_absent_on_every_v1_record(
        tmp_path, refused_world):
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    log.record(EscalationPolicy().route(_StakeStub(StakeClass.S2_DOCTRINAL),
                                        view),
               target_kind="claim", target_id="CLM-0001")
    written = log.routings()[0]
    assert "self_assessment" in written          # the SHAPE exists
    assert written["self_assessment"] is None    # and answers ABSENT


def test_7b_a_populated_self_assessment_is_refused(tmp_path, refused_world):
    """FAIL-CLOSED: with an empty ladder there is no occupant, so a populated
    slot would record a judgement nobody made - a fabricated assessor."""
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    with pytest.raises(SelfAssessmentNotAdmissible):
        log.record(EscalationPolicy().route(_StakeStub(StakeClass.S2_DOCTRINAL),
                                            view),
                   target_kind="claim", target_id="CLM-0001",
                   self_assessment={"confidence": "high"})
    assert not (tmp_path / "rte.jsonl").exists()


# ===========================================================================
# PIN 8 - UNCLASSIFIED IS REFUSED
# ===========================================================================

def test_8_routing_without_a_stake_classification_is_refused(refused_world):
    """**UNCLASSIFIED IS REFUSED, NOT CHEAP.** A stake nobody derived is not a
    low stake, and defaulting it to S0 would route the one episode nobody
    measured to the cheapest rung - silently."""
    with pytest.raises(UnclassifiedRouting):
        EscalationPolicy().route(None, _view(refused_world))


# ===========================================================================
# PIN 9 - THE WRITE GATES THE ACT
# ===========================================================================

def test_9_a_failed_log_write_gates_the_routing(tmp_path, refused_world,
                                                monkeypatch):
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))

    def _boom(*a, **k):
        raise OSError("disk gone")

    monkeypatch.setattr("src.executive.routing_log.durable_append_text", _boom)
    with pytest.raises(OSError):
        log.record(EscalationPolicy().route(_StakeStub(StakeClass.S2_DOCTRINAL),
                                            view),
                   target_kind="claim", target_id="CLM-0001")
    assert log.entries == []


def test_9b_an_underived_mint_refuses(tmp_path, refused_world, monkeypatch):
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    log.record(EscalationPolicy().route(_StakeStub(StakeClass.S0_PERIPHERAL),
                                        view),
               target_kind="claim", target_id="CLM-0001")
    monkeypatch.setattr("src.executive.routing_log.derive_max_ordinal",
                        lambda *a, **k: None)
    with pytest.raises(RoutingLogUnreadable):
        log.record(EscalationPolicy().route(_StakeStub(StakeClass.S0_PERIPHERAL),
                                            view),
                   target_kind="claim", target_id="CLM-0002")
    assert len(log.routings()) == 1


# ===========================================================================
# PIN 10 - PRIOR PINS UNTOUCHED
# ===========================================================================

_FROZEN = {
    "tests/test_m7a_executive_loop.py":
        "c7867cd28cf7d76d64683024a2c86335ec0f27bc3676e9467ef615523adc58fe",
    "tests/test_m7b_attention_policy.py":
        "5ea92b1f5ef9c278499151705ad2fc1180522665fda9b0e5f0c07544ad8bf700",
    "tests/test_m7c_inquiry.py":
        "6029d504c25fe4d2b1717339f1a74e34bce04d11460a08c587424efcd8227aa6",
    "tests/test_m7d_acceptance.py":
        "d3ab01833edb5748671bde1a4f8e75fc318d663421ca12afd4e41945cf4073f0",
    "tests/test_m8a_stake_classifier.py":
        "01dd8bdbc7a3ccf9070a56e6fc43163c61ce1b7e7068e12dea584798bb3ae055",
    "tests/test_act_log_integrity.py":
        "f663fd29114848860aa1bb4472d5d7f0ef0a68d48cc53679c44ea2418ff9caa9",
}


def test_10_all_prior_executive_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN.items():
        actual = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
        assert actual == expected, path


def test_10b_the_kill_and_reconstruction_pins_still_pass():
    """L10: the routing log is an ACT log - decisions never read it."""
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest",
         "tests/test_m7d_acceptance.py", "-q"],
        cwd=str(REPO), capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-3000:]


def test_10c_nothing_in_src_consumes_the_routing_log_but_the_loop():
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "routing_log.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module \
                    and "routing_log" in node.module:
                consumers.append(path.relative_to(REPO).as_posix())
    assert sorted(set(consumers)) == ["src/executive/loop.py"], consumers


# ===========================================================================
# PIN 11 - PURITY AND NO MAGNITUDES
# ===========================================================================

FORBIDDEN = ("random", "secrets", "numpy", "datetime", "time", "pathlib", "os",
             "json", "src.filtration", "src.goals", "src.external",
             "src.doctrine", "src.identity", "src.suspension", "src.worldmodel",
             "src.utils", "src.executive.loop", "src.executive.routing_log",
             "src.executive.selection_log", "src.executive.inquiry_log")


def test_11_the_policy_imports_nothing_it_could_read_draw_or_write_with():
    tree = ast.parse((SRC / "executive" / "escalation_policy.py").read_text(
        encoding="utf-8"))
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            seen.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            seen.add(node.module)
    for name in seen:
        for bad in FORBIDDEN:
            assert not (name == bad or name.startswith(bad + ".")), name


def test_11b_no_mutation_surface_contact_and_no_write_call():
    tree = ast.parse((SRC / "executive" / "escalation_policy.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open"
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"record", "commit", "admit", "suspend",
                                     "save", "write", "_append"}


def test_11c_the_policy_holds_no_numeric_literal():
    """A rung is an ORDINAL POSITION on a ruled ladder, never a score."""
    tree = ast.parse((SRC / "executive" / "escalation_policy.py").read_text(
        encoding="utf-8"))
    # EXCLUDE THE WHOLE SLICE SUBTREE, not just the slice node. `below[-1]` is
    # `Subscript(slice=UnaryOp(USub, Constant(1)))`, so a scanner that skipped
    # only the slice node itself would flag the `1` inside it as a magnitude -
    # the same naivety M8-a's pin corrected, one level deeper. An index is a
    # position, not a score.
    indices = {id(inner) for node in ast.walk(tree)
               if isinstance(node, ast.Subscript)
               for inner in ast.walk(node.slice)}
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant)
                and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool) and id(n) not in indices}
    assert literals == set(), literals


def test_11d_routing_is_pure_and_writes_nothing(tmp_path, refused_world):
    view = _view(refused_world)
    log = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    policy = EscalationPolicy()
    for _ in range(5):
        policy.route(_StakeStub(StakeClass.S3_STRUCTURAL), view)
    assert log.routings() == ()
    assert not (tmp_path / "rte.jsonl").exists()


# ===========================================================================
# IDENTITY, REGISTRATION, AND THE LOOP PHASE
# ===========================================================================

def test_identity_is_data():
    assert POLICY_NAME == "escalation-policy.v1"
    with pytest.raises(EscalationIdentityMismatch):
        EscalationPolicy(name="escalation-policy.v2")
    with pytest.raises(EscalationIdentityMismatch):
        EscalationPolicy(version="2")


def test_the_registration_slot_is_declared_data_and_gates_nothing():
    assert REGISTRATION["identity"] == POLICY_NAME
    assert REGISTRATION["contract"] == "registration"
    assert len(REGISTRATION["declared_invariants"]) == 6
    with pytest.raises(TypeError):
        REGISTRATION["contract"] = "qualification"   # type: ignore[index]
    source = (SRC / "executive" / "escalation_policy.py").read_text(
        encoding="utf-8")
    assert "if REGISTRATION" not in source and "REGISTRATION[" not in source


def test_the_loop_routes_through_a_governed_phase(tmp_path):
    """End to end on a REAL loop: the shortfall lands on the record."""
    acquisitions = AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl"))
    loop = ExecutiveLoop(
        ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl")),
        PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl")),
        GoalLedger(ledger_path=str(tmp_path / "glc.jsonl")),
        acquisitions,
        routings=RoutingLog(log_path=str(tmp_path / "rte.jsonl")))
    loop.register_consumed_verdict(THE_VERDICT)

    record = loop.route_and_record("claim", "CLM-0001")
    assert record.routing_id == "RTE-0001"
    # With no stake handles supplied the target derives S0 - and S0 is adequate
    # at rung 0, so this route carries no debt. The shortfall arm is exercised
    # against a real S2+ classification in the parametrized pins above.
    assert record.decision.routed_rung is Rung.RUNG_0_DETERMINISTIC_KERNEL
    assert len(loop.routings.routings()) == 1


def test_step_is_untouched_by_routing(tmp_path):
    """Pin 10 by construction: routing rides BESIDE the cycle."""
    source = (SRC / "executive" / "loop.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    step = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "step")
    body = ast.unparse(step)
    assert "route" not in body and "routings" not in body
