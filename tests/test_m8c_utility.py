"""M8-c: utility measurement under L3 -- history that nothing reads.

THE SEVEN BINDING PROPERTIES:
  1. Determinism -- identical inputs, identical record, twice.
  2. The ordinal cost is two RECORDED seq points and their difference; no
     wall-clock import exists.
  3. The no-consumer bar in BOTH forms: import-absence tree-wide, and the
     no-logic-path witness -- a world with utility records derives, selects,
     generates and routes IDENTICALLY to one without.
  4. Chained from genesis; the audit reads clean; a tampered line raises
     CHAIN_BREAK.
  5. Refusals witnessed: missing routing ref, missing disposition, write failure.
  6. Prior executive pin files byte-unmodified; the kill/reconstruction pins
     pass whole -- a THIRD act log must not become constitutive.
  7. Purity of the record builder; no magnitudes beyond the two recorded
     ordinals and their difference.
"""

import ast
import hashlib
import json
import pathlib
import subprocess
import sys

import pytest

from src.executive.act_log_audit import (UTILITY_LOG_SCHEMA, FindingKind,
                                         audit_act_log)
from src.executive.escalation_policy import EscalationPolicy, Rung
from src.executive.routing_log import RoutingLog
from src.executive.stake_classifier import StakeClass
from src.executive.utility_log import (UnknownRouting, UnmeasurableEpisode,
                                       UtilityLog, UtilityLogUnreadable,
                                       measure_episode)
from src.filtration.episode_record import (EpisodeOutcome, EpisodeRecord,
                                           PressureClass)
from src.filtration.obligation_ledger import ObligationLedger, TargetKind

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"


class _StakeStub:
    def __init__(self, stake_class=StakeClass.S3_STRUCTURAL):
        self.stake_class = stake_class

    def as_dict(self):
        return {"stake_class": self.stake_class.value}


class _EmptyView:
    class rungs:
        consumed_verdicts = ()


@pytest.fixture()
def world(tmp_path):
    """A ROUTED and DISPOSED episode, built through the kernel's own doors."""
    obligations = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"))
    episodes = EpisodeRecord(log_path=str(tmp_path / "epi.jsonl"),
                             peer_paths=[str(tmp_path / "obl.jsonl")])
    routings = RoutingLog(log_path=str(tmp_path / "rte.jsonl"))
    log = UtilityLog(log_path=str(tmp_path / "utl.jsonl"))

    admitted = obligations.admit("fixture", TargetKind.DOCTRINE, "Doctrine-0",
                                 "an account is owed")
    episode_id = episodes.open_episode([admitted.obligation_id], 3)
    # Points of logical time consumed between the two anchors.
    obligations.admit("fixture", TargetKind.SCAR, "Scar-0", "work happens")
    obligations.admit("fixture", TargetKind.DOCTRINE, "Doctrine-3", "more work")
    # **K11'S FLOOR, AND THE KERNEL ENFORCED IT AGAINST MY FIRST FIXTURE.**
    # `disposition(..., SURVIVED)` REFUSES an episode carrying no
    # PRESSURE_APPLIED record - "survival requires an identifiable completed
    # pressure episode, not the absence of an objection". The fixture was wrong
    # and the kernel was right, so the pressure is applied through its own door
    # rather than the outcome being softened to one that needs none.
    episodes.record_pressure(episode_id, PressureClass.PRECOMMITTED_PREDICTION,
                             "the precommitted prediction resolved")
    episodes.disposition(episode_id, EpisodeOutcome.SURVIVED)

    decision = EscalationPolicy().route(_StakeStub(), _EmptyView())
    routing = routings.record(decision, target_kind="doctrine",
                              target_id="Doctrine-0")
    return {"tmp": tmp_path, "obligations": obligations, "episodes": episodes,
            "routings": routings, "log": log, "episode_id": episode_id,
            "routing_id": routing.routing_id}


def _measure(world, log=None):
    return measure_episode(
        world["routing_id"], world["episode_id"], routings=world["routings"],
        episodes=world["episodes"], log=log or world["log"])


# ===========================================================================
# PIN 1 - DETERMINISM
# ===========================================================================

def test_1_identical_inputs_yield_identical_records_twice(world):
    first = _measure(world)
    second = _measure(world, log=UtilityLog(log_path=str(world["tmp"] / "b.jsonl")))
    # Everything but the mint ordinal, which is per-log by construction.
    for field in ("routing_id", "rung", "disposition_id", "disposition_kind",
                  "opened_seq", "disposed_seq", "ordinal_cost", "recorded_at"):
        assert getattr(first, field) == getattr(second, field), field


# ===========================================================================
# PIN 2 - THE ORDINAL COST
# ===========================================================================

def test_2_the_cost_is_two_recorded_seq_points_and_their_difference(world):
    record = _measure(world)
    # BOTH anchors are read off REAL kernel records.
    lines = [json.loads(x) for x in
             (world["tmp"] / "epi.jsonl").read_text(encoding="utf-8").splitlines()]
    opened = next(l for l in lines if l["record_type"] == "episode_opened")
    disposed = next(l for l in lines if l["record_type"] == "disposition")
    assert record.opened_seq == opened["opened_seq"]   # the open record's own name
    assert record.disposed_seq == disposed["seq"]

    from src.filtration.obligation_ledger import seq_ordinal
    assert record.ordinal_cost == (seq_ordinal(record.disposed_seq)
                                   - seq_ordinal(record.opened_seq))
    # Non-vacuous: real points were consumed between the anchors.
    assert record.ordinal_cost > 0


def test_2b_the_module_reads_no_clock(world):
    """No wall-clock import ANYWHERE - the cost is points, not a duration."""
    tree = ast.parse((SRC / "executive" / "utility_log.py").read_text(
        encoding="utf-8"))
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            seen.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            seen.add(node.module)
    for bad in ("datetime", "time", "calendar"):
        assert not any(n == bad or n.startswith(bad + ".") for n in seen), bad
    # ...and `recorded_at` is a PARAMETER, which is what keeps pin 1 exact.
    assert _measure(world).recorded_at == ""


def test_2c_the_disposition_id_and_kind_are_the_kernels_own(world):
    record = _measure(world)
    assert record.disposition_id == world["episode_id"]
    assert record.disposition_kind == EpisodeOutcome.SURVIVED.value
    assert record.rung == Rung.RUNG_0_DETERMINISTIC_KERNEL.value


# ===========================================================================
# PIN 3 - THE NO-CONSUMER BAR, BOTH FORMS
# ===========================================================================

def test_3_no_src_module_imports_the_utility_log_at_all():
    """**ZERO importers tree-wide** - stronger than the sibling act logs, which
    are each reachable from `ExecutiveLoop`. The specification's bar is "no src
    path imports, reads, or RECEIVES", and a loop holding the handle would
    receive it. Measurement is a DOOR, so the count is zero."""
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "utility_log.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module \
                    and "utility_log" in node.module:
                consumers.append(path.relative_to(REPO).as_posix())
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "utility_log" in alias.name:
                        consumers.append(path.relative_to(REPO).as_posix())
    assert sorted(set(consumers)) == [], consumers


def test_3b_the_loop_and_the_policies_name_nothing_utility():
    for name in ("loop.py", "derived_view.py", "attention_policy.py",
                 "inquiry_generator.py", "escalation_policy.py",
                 "stake_classifier.py"):
        source = (SRC / "executive" / name).read_text(encoding="utf-8")
        assert "utility" not in source.lower(), name


def test_3c_a_world_with_utility_records_behaves_IDENTICALLY(world):
    """**THE NO-LOGIC-PATH WITNESS** - M7-d's identity discipline applied to
    this log. Measurements are written, and every downstream derivation is
    byte-identical to the world that has none. If any decision path ever read a
    utility record, this pin would move."""
    from src.executive.derived_view import derive
    from src.executive.stake_classifier import StakeClassifier
    from src.external.acquisition_ledger import AcquisitionLedger
    from src.external.prediction_ledger import PredictionLedger
    from src.goals.goal_ledger import GoalLedger

    tmp = world["tmp"]
    acquisitions = AcquisitionLedger(ledger_path=str(tmp / "acq.jsonl"))
    predictions = PredictionLedger(ledger_path=str(tmp / "prd.jsonl"))
    goals = GoalLedger(ledger_path=str(tmp / "glc.jsonl"))

    def snapshot():
        view = derive(world["obligations"], predictions, goals, acquisitions)
        stake = StakeClassifier().classify("doctrine", "Doctrine-0", view)
        routing = EscalationPolicy().route(stake, view)
        return (view, stake.as_dict(), routing.as_dict())

    before = snapshot()
    for _ in range(3):
        _measure(world)
    assert len(world["log"].measurements()) == 3
    assert snapshot() == before


# ===========================================================================
# PIN 4 - CHAINED FROM GENESIS
# ===========================================================================

def test_4_the_utility_log_chains_from_genesis_and_audits_clean(world):
    from src.executive.act_chain import CHAIN_KEY, genesis_chain
    for _ in range(3):
        _measure(world)
    path = world["tmp"] / "utl.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])[CHAIN_KEY] == genesis_chain()
    report = audit_act_log(path, UTILITY_LOG_SCHEMA)
    assert report.clean, report.as_dict()
    assert report.pre_chain_lines == 0 and report.chained_lines == 3


def test_4b_a_tampered_utility_line_raises_chain_break(world):
    for _ in range(3):
        _measure(world)
    path = world["tmp"] / "utl.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    # Forge the cost down - the edit this log will most attract.
    record["ordinal_cost"] = 0
    lines[0] = json.dumps(record)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report = audit_act_log(path, UTILITY_LOG_SCHEMA)
    assert FindingKind.CHAIN_BREAK in {f.kind for f in report.findings}


# ===========================================================================
# PIN 5 - THE REFUSALS
# ===========================================================================

def test_5_an_unknown_routing_reference_is_refused(world):
    with pytest.raises(UnknownRouting):
        measure_episode("RTE-9999", world["episode_id"],
                        routings=world["routings"], episodes=world["episodes"],
                        log=world["log"])
    assert world["log"].measurements() == ()


def test_5b_an_undisposed_episode_is_refused(world):
    """HALF-MEASURED EPISODES ARE NOT MEASURED. An episode still open has
    consumed points that are not yet a cost - the second anchor does not
    exist, and an absent fact is not a zero."""
    open_only = world["episodes"].open_episode(["OBL-0001"], 3)
    with pytest.raises(UnmeasurableEpisode):
        measure_episode(world["routing_id"], open_only,
                        routings=world["routings"], episodes=world["episodes"],
                        log=world["log"])
    assert world["log"].measurements() == ()


def test_5c_an_unknown_episode_is_refused(world):
    with pytest.raises(UnmeasurableEpisode):
        measure_episode(world["routing_id"], "EPI-9999",
                        routings=world["routings"], episodes=world["episodes"],
                        log=world["log"])


def test_5f_the_two_refusals_are_DISTINGUISHABLE_not_interchangeable(world,
                                                                     tmp_path):
    """**FOUND BY TWO SURVIVING MUTANTS, AND THE FINDING IS THE POINT.**

    `measure_episode` carries two guards that both raise `UnmeasurableEpisode`:
    one for a missing RECORD (the episode is not complete) and one for a missing
    ANCHOR (a record exists but carries no `SEQ-` token). Deleting either left
    every pin green, because the other caught the same fixture and the pins only
    asserted the exception TYPE. **A guard masked by its neighbour is a guard
    nothing measures** - Ruling 29's law arriving through the test rather than
    the code.

    They stay ONE exception type, deliberately: both say "this episode cannot be
    measured", which is one fact about one subject, and splitting it would coin
    a vocabulary for the caller's benefit that the caller cannot act on
    differently. What changes is that each guard's MESSAGE names its own case,
    and this pin holds them apart.
    """
    # (a) MISSING RECORD - the episode is open, never disposed.
    open_only = world["episodes"].open_episode(["OBL-0001"], 3)
    with pytest.raises(UnmeasurableEpisode) as missing_record:
        measure_episode(world["routing_id"], open_only,
                        routings=world["routings"], episodes=world["episodes"],
                        log=world["log"])
    assert "disposed=False" in str(missing_record.value)

    # (b) MISSING ANCHOR - both records exist, neither carries a `SEQ-` token.
    # A legacy-shaped episode log, which is a real possibility under era
    # honesty: a record written before the clock was stamped on it.
    legacy = tmp_path / "legacy_epi.jsonl"
    legacy.write_text("\n".join(json.dumps(line) for line in [
        {"record_type": "episode_opened", "episode_id": "EPI-0001"},
        {"record_type": "disposition", "episode_id": "EPI-0001",
         "outcome": "survived"}]) + "\n", encoding="utf-8")

    class _LegacyEpisodes:
        def read_all(self):
            return tuple(json.loads(x) for x in
                         legacy.read_text(encoding="utf-8").splitlines())

    with pytest.raises(UnmeasurableEpisode) as missing_anchor:
        measure_episode(world["routing_id"], "EPI-0001",
                        routings=world["routings"], episodes=_LegacyEpisodes(),
                        log=world["log"])
    assert "no recorded anchor" in str(missing_anchor.value)
    # ...and the two messages are genuinely different.
    assert str(missing_record.value) != str(missing_anchor.value)
    assert world["log"].measurements() == ()


def test_5d_a_failed_write_gates_the_act(world, monkeypatch):
    monkeypatch.setattr("src.executive.utility_log.durable_append_text",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("gone")))
    with pytest.raises(OSError):
        _measure(world)
    assert world["log"].entries == []


def test_5e_an_underived_mint_refuses(world, monkeypatch):
    _measure(world)
    monkeypatch.setattr("src.executive.utility_log.derive_max_ordinal",
                        lambda *a, **k: None)
    with pytest.raises(UtilityLogUnreadable):
        _measure(world)
    assert len(world["log"].measurements()) == 1


# ===========================================================================
# PIN 6 - PRIOR PINS UNTOUCHED
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
    "tests/test_m8b_escalation.py":
        "dbabe9e752c83e83444fd74f2656588ad0773ce0d6c2d33a392d3bf621bcc8a4",
}


def test_6_all_prior_executive_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN.items():
        actual = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
        assert actual == expected, path


def test_6b_a_third_act_log_did_not_become_constitutive():
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest",
         "tests/test_m7d_acceptance.py", "-q"],
        cwd=str(REPO), capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-3000:]


# ===========================================================================
# PIN 7 - PURITY AND NO MAGNITUDES
# ===========================================================================

def test_7_nothing_evaluative_is_writable(world):
    """The shape has NO slot for judgment, so judgment is UNWRITABLE.

    Adequacy was the ROUTING record's statement; this record says what
    happened. Conflating them would let a measurement quietly re-open a
    question the routing already answered on the record.
    """
    written = _measure(world)
    payload = written.as_dict()
    for banned in ("score", "rating", "adequate", "adequacy", "good", "quality",
                   "value", "utility_score", "efficiency", "verdict"):
        assert banned not in payload, banned
    source = (SRC / "executive" / "utility_log.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    fields = {n.target.id for n in ast.walk(tree)
              if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
    for banned in ("score", "rating", "adequate", "quality", "verdict"):
        assert banned not in fields


def test_7b_the_only_numeric_work_is_the_difference_of_two_ordinals():
    tree = ast.parse((SRC / "executive" / "utility_log.py").read_text(
        encoding="utf-8"))
    indices = {id(inner) for node in ast.walk(tree)
               if isinstance(node, ast.Subscript)
               for inner in ast.walk(node.slice)}
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant)
                and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool) and id(n) not in indices}
    # THE MINT STEP IS DECLARED, NOT ABSORBED. `seq + 1` is the increment every
    # house act log uses to mint its next ordinal; it selects no behaviour from
    # a range and is identical in all four logs. Naming it here keeps the bound
    # tight instead of widening the literal set to swallow it.
    assert literals == {1}, literals
    # STRING CONCATENATION IS NOT ARITHMETIC. The `+ "\\n"` in `_append` is the
    # line terminator every house log writes; excluding it by its string operand
    # keeps this pin about NUMBERS, which is what the bar is about.
    numeric = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp)
               and not any(isinstance(side, ast.Constant)
                           and isinstance(side.value, str)
                           for side in (n.left, n.right))]
    kinds = sorted(type(o.op).__name__ for o in numeric)
    assert kinds == ["Add", "Sub"], kinds   # the mint step, and the cost


def test_7c_the_module_writes_only_its_own_log():
    tree = ast.parse((SRC / "executive" / "utility_log.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"admit", "commit", "suspend", "form_scar",
                                     "disposition", "open_episode",
                                     "save_to_file", "resolve"}


def test_7d_the_cost_is_a_count_of_points_never_a_duration(world):
    """No unit is coined: the anchors are tokens on a clock that already
    existed, and the difference is a count of its points."""
    record = _measure(world)
    assert record.opened_seq.startswith("SEQ-")
    assert record.disposed_seq.startswith("SEQ-")
    assert isinstance(record.ordinal_cost, int)


def test_the_gate_one_referents_are_all_not_applicable(world):
    """A MEASUREMENT IS NOT A DISPOSITION - it applies no pressure, exercises
    no defeater, and refuses nothing."""
    written = world["log"].measurements() if world["log"].measurements() else None
    _measure(world)
    gate = world["log"].measurements()[0]["gate_one"]
    assert set(gate.values()) == {"not_applicable"}
    assert set(gate) == {"pressure_class_applied", "unexercised_defeaters",
                         "rejection_reason"}
