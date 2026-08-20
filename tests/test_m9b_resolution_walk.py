"""test_m9b_resolution_walk.py - M9-b: RESOLUTION AND THE BACKWARD WALK.

Hundred-eighteenth entry (PATH v144), M9_GROUNDING.md section M9-b, heading
line 122: the clerical evaluator (`criterion-evaluator.v1`), resolution
recording through the ledger's own widened funnel, the total deterministic
backward walk (`propagation-policy.v1`) through the kernel's own `admit()`,
and the genesis-chained prediction act log.

EVERY PIN HERE IS RED AGAINST `e88714b`, where none of the three modules
existed - the file fails at collection (ImportError), witnessed in a detached
worktree.

TWO MIRRORED VOCABULARIES, BOTH DRIFT-PINNED HERE (the standing profile's
third option for a purity boundary): `EvaluationOutcome`'s decisive members
mirror `PredictionOutcome`; `WalkDisposition` mirrors the inquiry log's
`KernelDisposition` submitted answers, forced by that log's byte-frozen
consumer census. The guard lives in these pins, not in an import.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.executive.act_log_audit import (FindingKind,
                                         PREDICTION_ACT_LOG_SCHEMA,
                                         audit_act_log)
from src.executive.criterion_evaluator import (EVALUATOR_NAME,
                                               EVALUATOR_VERSION,
                                               REGISTRATION as
                                               EVALUATOR_REGISTRATION,
                                               CriterionEvaluator,
                                               EvaluationOutcome,
                                               NonOperationalCommitment,
                                               UnruledSurfaceReader)
from src.executive.inquiry_log import KernelDisposition
from src.executive.loop import ExecutiveLoop
from src.executive.prediction_act_log import (PredictionActLog,
                                              PredictionActLogUnreadable)
from src.executive.propagation_policy import (POLICY_NAME, POLICY_VERSION,
                                              REGISTRATION as
                                              POLICY_REGISTRATION,
                                              PropagationPolicy,
                                              WalkDisposition,
                                              WalkNotAttemptable,
                                              WalkOnUnfalsified)
from src.external.prediction_ledger import (DependencyKind,
                                            OperationalCriterion,
                                            PredictionLedger,
                                            PredictionOutcome,
                                            TypedDependency, provided)
from src.filtration.obligation_ledger import ObligationLedger
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalProvenance)
from src.worldmodel.proposition_ledger import PropositionLedger
from src.worldmodel.standing import (ReferenceState, WorldStanding,
                                     derive_standing)

EVALUATOR_MODULE = Path("src/executive/criterion_evaluator.py")
POLICY_MODULE = Path("src/executive/propagation_policy.py")
ACT_LOG_MODULE = Path("src/executive/prediction_act_log.py")


# =====================================================================
# FIXTURES - one kernel, built the same way every time (determinism's
# precondition and pin 5's subject)
# =====================================================================

def _predictions(tmp_path) -> PredictionLedger:
    return PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))


def _obligations(tmp_path, predictions=None, propositions=None
                 ) -> ObligationLedger:
    return ObligationLedger(
        ledger_path=str(tmp_path / "obl.jsonl"),
        prediction_ledger=predictions,
        proposition_ledger=propositions)


def _goals(tmp_path) -> GoalLedger:
    ledger = GoalLedger(ledger_path=str(tmp_path / "glc.jsonl"))
    ledger.commit(desired_state="hold the M9-b fixtures honest",
                  kind=GoalKind.RESEARCH, level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="m9b-pins")
    return ledger


def _world_standing_reader(known_id: str):
    """A REAL `derive_standing` over fixture-built references for one id.

    The census records this surface as a DERIVATION (no single-owner per-id
    read exists in the tree - `derive_standing` has zero src/ callers), so
    the reader composes it: one live supporting claim -> SUPPORTED.
    """
    def reader(record_id: str):
        if record_id != known_id:
            return None
        verdict = derive_standing([ReferenceState(
            field="supported_by", kind="claim",
            record_id="CLM-0001", present=True)])
        return verdict.standing.value
    return reader


def _criterion(surface, record_id, confirmed, failed) -> OperationalCriterion:
    return OperationalCriterion(surface=surface, record_id=record_id,
                                confirmed_state=confirmed, failed_state=failed)


def _falsified_walk_kernel(tmp_path):
    """The pin-4 kernel: one falsified prediction with four mixed-form
    dependencies whose submissions draw all four kernel answers in ONE walk.
    Everything minted here is ordinal-deterministic."""
    predictions = _predictions(tmp_path)
    propositions = PropositionLedger(ledger_path=str(tmp_path / "wmp.jsonl"))
    obligations = _obligations(tmp_path, predictions=predictions,
                               propositions=propositions)
    # PRD-0001: the dependency target (resolvable, never walked).
    predictions.commit(expected_result="the target the walk points at")
    # PRD-0002: the falsified one. Two BYTE-IDENTICAL dependencies (first
    # ADMITTED, second the kernel's own DUPLICATE - same kind, same target,
    # same derived claim; a same-target dependency of a DIFFERENT kind is a
    # different debt and honestly admits), one unresolvable world proposition
    # (TARGETLESS), one goal form outside TargetKind (MALFORMED) - the
    # kernel's real mixed answers, none engineered.
    falsified = predictions.commit(
        expected_result="the exposure under walk",
        operational_criteria=(
            _criterion("prediction_resolution_outcome", "PRD-0001",
                       "confirmed", "falsified"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="prediction", record_id="PRD-0001"),
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="prediction", record_id="PRD-0001"),
            TypedDependency(kind=DependencyKind.ASSUMPTION,
                            record_form="world_proposition",
                            record_id="WMP-9999"),
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="goal", record_id="GLC-0001"),
        ))
    predictions.resolve(falsified.prediction_id, PredictionOutcome.FALSIFIED,
                        "operational_criteria[0]", evaluator=EVALUATOR_NAME)
    return predictions, obligations, falsified


# =====================================================================
# PIN 1 - CLERICAL AGREEMENT, BOTH ARMS, ALL FOUR SURFACES
# =====================================================================

def test_both_arms_on_all_four_surfaces_and_two_evaluators_agree(tmp_path) -> None:
    """PIN 1. One kernel state per surface, read by two criteria whose
    declared states put it on opposite arms - the criterion's DATA decides,
    and two independent evaluator instances agree on every read."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    goals = _goals(tmp_path)
    target = predictions.commit(expected_result="the surface under test",
                                success_criteria=provided("it holds"))
    predictions.resolve(target.prediction_id, PredictionOutcome.CONFIRMED,
                        "success_criteria")
    admitted = obligations.admit("m9b-pins", "prediction",
                                 target.prediction_id, "an open obligation")
    assert admitted.admitted

    subject = predictions.commit(
        expected_result="eight criteria over four surfaces",
        operational_criteria=(
            _criterion("prediction_resolution_outcome",
                       target.prediction_id, "confirmed", "falsified"),
            _criterion("prediction_resolution_outcome",
                       target.prediction_id, "falsified", "confirmed"),
            _criterion("obligation_status", admitted.obligation_id,
                       "open", "merged"),
            _criterion("obligation_status", admitted.obligation_id,
                       "merged", "open"),
            _criterion("world_proposition_standing", "WMP-0001",
                       "supported", "undercut"),
            _criterion("world_proposition_standing", "WMP-0001",
                       "undercut", "supported"),
            _criterion("goal_status", "GLC-0001",
                       "committed", "superseded"),
            _criterion("goal_status", "GLC-0001",
                       "superseded", "committed"),
        ),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="prediction",
                            record_id=target.prediction_id),))

    readers = {
        "prediction_resolution_outcome":
            lambda rid: (lambda r: None if r is None else r.outcome)(
                predictions.resolution_for(rid)),
        "obligation_status": obligations.status_of,
        "world_proposition_standing": _world_standing_reader("WMP-0001"),
        "goal_status": goals.derive_status,
    }
    first = CriterionEvaluator(surface_readers=readers)
    second = CriterionEvaluator(surface_readers=readers)

    expected = [EvaluationOutcome.CONFIRMED, EvaluationOutcome.FALSIFIED] * 4
    for index, arm in enumerate(expected):
        a = first.evaluate(subject, index)
        b = second.evaluate(subject, index)
        assert a.outcome is arm, (index, a.reason)
        assert b.outcome is arm
        assert a == b, "two evaluators over one kernel disagreed"
        assert a.reason == ""
        assert a.surface_state is not None


# =====================================================================
# PIN 2 - UNRESOLVED_AT_EVALUATION, NEVER A DEFAULT
# =====================================================================

def test_a_third_state_an_unresolvable_id_and_a_missing_handle_each_unresolve(
        tmp_path) -> None:
    """PIN 2. Three different inabilities, three recorded reasons, zero
    defaults to either arm."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    admitted = obligations.admit("m9b-pins", "prediction",
                                 predictions.commit(
                                     expected_result="t").prediction_id,
                                 "an obligation to defer")
    obligations.defer(admitted.obligation_id, "waiting", "SEQ-000900")

    subject = predictions.commit(
        expected_result="three inabilities",
        operational_criteria=(
            # the surface's THIRD state: status is now 'deferred'
            _criterion("obligation_status", admitted.obligation_id,
                       "open", "merged"),
            # an unresolvable id
            _criterion("prediction_resolution_outcome", "PRD-7777",
                       "confirmed", "falsified"),
            # a surface with NO handle below
            _criterion("goal_status", "GLC-0001", "committed", "superseded"),
        ),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.HORIZON,
                            record_form="prediction",
                            record_id="PRD-0001"),))
    evaluator = CriterionEvaluator(surface_readers={
        "obligation_status": obligations.status_of,
        "prediction_resolution_outcome":
            lambda rid: (lambda r: None if r is None else r.outcome)(
                predictions.resolution_for(rid)),
    })
    third = evaluator.evaluate(subject, 0)
    assert third.outcome is EvaluationOutcome.UNRESOLVED_AT_EVALUATION
    assert third.surface_state == "deferred"
    assert "neither" in third.reason

    unresolvable = evaluator.evaluate(subject, 1)
    assert unresolvable.outcome is EvaluationOutcome.UNRESOLVED_AT_EVALUATION
    assert unresolvable.surface_state is None
    assert "unresolvable id" in unresolvable.reason

    no_handle = evaluator.evaluate(subject, 2)
    assert no_handle.outcome is EvaluationOutcome.UNRESOLVED_AT_EVALUATION
    assert "no reader is held" in no_handle.reason

    for result in (third, unresolvable, no_handle):
        assert result.outcome not in (EvaluationOutcome.CONFIRMED,
                                      EvaluationOutcome.FALSIFIED)
        assert result.reason


def test_a_raising_surface_read_unresolves_with_the_failure_named(tmp_path) -> None:
    """PIN 2, the unreadable-surface half: a read that RAISES is an
    inability, never an arm."""
    predictions = _predictions(tmp_path)
    subject = predictions.commit(
        expected_result="a dead surface",
        operational_criteria=(
            _criterion("obligation_status", "OBL-0001", "open", "merged"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.CAUSAL_LINK,
                            record_form="obligation",
                            record_id="OBL-0001"),))

    def dead_reader(record_id: str):
        raise OSError("the store is unreachable")

    evaluator = CriterionEvaluator(
        surface_readers={"obligation_status": dead_reader})
    result = evaluator.evaluate(subject, 0)
    assert result.outcome is EvaluationOutcome.UNRESOLVED_AT_EVALUATION
    assert "OSError" in result.reason


# =====================================================================
# PIN 3 - THE NON-OPERATIONAL REFUSAL
# =====================================================================

def test_a_non_operational_commitment_is_refused_by_name(tmp_path) -> None:
    """PIN 3. The honest state is not evaluable, and evaluating it would
    invent the criterion the record does not carry."""
    predictions = _predictions(tmp_path)
    legacy = predictions.commit(expected_result="the old shape",
                                success_criteria=provided("it holds"))
    evaluator = CriterionEvaluator(surface_readers={})
    with pytest.raises(NonOperationalCommitment):
        evaluator.evaluate(legacy, 0)


def test_an_uncommitted_criterion_index_is_refused(tmp_path) -> None:
    """PIN 3's sibling: criteria are fixed at commit time, and an index
    naming none of them refuses."""
    predictions = _predictions(tmp_path)
    subject = predictions.commit(
        expected_result="one criterion only",
        operational_criteria=(
            _criterion("goal_status", "GLC-0001", "committed", "superseded"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="goal", record_id="GLC-0001"),))
    evaluator = CriterionEvaluator(surface_readers={})
    with pytest.raises(ValueError):
        evaluator.evaluate(subject, 1)


def test_a_reader_for_an_unruled_surface_is_refused_at_construction() -> None:
    """The census stays the boundary: the excluded doctrine/scar surfaces
    cannot ride in under a keyword."""
    with pytest.raises(UnruledSurfaceReader):
        CriterionEvaluator(surface_readers={
            "doctrine_status": lambda rid: "active"})


# =====================================================================
# PIN 4 - TOTALITY, WITH THE KERNEL'S REAL MIXED ANSWERS
# =====================================================================

def test_the_walk_is_total_and_captures_every_kernel_answer(tmp_path) -> None:
    """PIN 4. Four mixed-form dependencies -> exactly four submissions in
    declaration order, dispositions ADMITTED / REJECTED_DUPLICATE /
    REJECTED_TARGETLESS / REJECTED_MALFORMED, all in ONE walk. The census is
    zipped against the commitment's own recorded dependencies, so a mutation
    deleting any dependency from the walk is RED."""
    predictions, obligations, falsified = _falsified_walk_kernel(tmp_path)
    policy = PropagationPolicy(obligations=obligations,
                               predictions=predictions)
    walk = policy.walk(falsified.prediction_id)

    commitment = predictions.commitment_for(falsified.prediction_id)
    assert len(walk.submissions) == len(commitment.typed_dependencies) == 4
    for submission, dependency in zip(walk.submissions,
                                      commitment.typed_dependencies):
        assert submission.dependency_kind == dependency.kind.value
        assert submission.record_form == dependency.record_form
        assert submission.record_id == dependency.record_id

    assert [s.disposition for s in walk.submissions] == [
        WalkDisposition.ADMITTED,
        WalkDisposition.REJECTED_DUPLICATE,
        WalkDisposition.REJECTED_TARGETLESS,
        WalkDisposition.REJECTED_MALFORMED,
    ]
    # The admitted one is a REAL kernel record, standing OPEN.
    admitted = walk.submissions[0]
    assert obligations.status_of(admitted.obligation_id) is not None
    # And the whole walk is sourced to the policy and the falsified id.
    opens = [r for r in obligations.read_all()
             if r.get("record_type") == "open"]
    assert opens and all(
        r["source"] == f"{POLICY_NAME}:{falsified.prediction_id}"
        for r in opens)


def test_a_walk_on_an_unfalsified_prediction_refuses(tmp_path) -> None:
    """The walk is the CONSEQUENCE of a falsification on the record."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    unresolved = predictions.commit(expected_result="still open")
    confirmed = predictions.commit(expected_result="held",
                                   success_criteria=provided("held"))
    predictions.resolve(confirmed.prediction_id, PredictionOutcome.CONFIRMED,
                        "success_criteria")
    policy = PropagationPolicy(obligations=obligations,
                               predictions=predictions)
    with pytest.raises(WalkOnUnfalsified):
        policy.walk(unresolved.prediction_id)
    with pytest.raises(WalkOnUnfalsified):
        policy.walk(confirmed.prediction_id)
    assert obligations.read_all() == (), "a refused walk submitted something"


# =====================================================================
# PIN 5 - DETERMINISM, TWICE
# =====================================================================

def test_same_commitment_same_kernel_same_walk_same_act_bytes(tmp_path) -> None:
    """PIN 5. Two identically-built kernels -> walks compare EQUAL (every
    field, ordinals included, because the mints are ordinal-deterministic)
    and the act lines are byte-identical modulo the observation timestamp
    and the chain hash it feeds."""
    first_dir = tmp_path / "one"
    second_dir = tmp_path / "two"
    first_dir.mkdir()
    second_dir.mkdir()
    acts = []
    walks = []
    for base in (first_dir, second_dir):
        predictions, obligations, falsified = _falsified_walk_kernel(base)
        policy = PropagationPolicy(obligations=obligations,
                                   predictions=predictions)
        log = PredictionActLog(log_path=str(base / "pra.jsonl"))
        walk = policy.walk(falsified.prediction_id)
        acts.append(log.record_propagation(walk))
        walks.append(walk)

    assert walks[0] == walks[1], "the walk itself diverged"

    def stable(payload):
        clean = {k: v for k, v in payload.items()
                 if k not in ("recorded_at", "chain")}
        return json.dumps(clean, sort_keys=True)

    assert stable(acts[0]) == stable(acts[1]), "the act bytes diverged"


# =====================================================================
# PIN 6 - THE PARTIAL-WALK REFUSAL: WHOLE OR NOTHING
# =====================================================================

def test_a_dead_handle_fails_the_walk_whole_before_anything_lands(tmp_path) -> None:
    """PIN 6. A dead obligation handle, and separately a prediction-form
    dependency against a ledger with no prediction resolver (whose own door
    would RAISE mid-walk), each refuse BEFORE the first submission."""
    predictions, obligations, falsified = _falsified_walk_kernel(tmp_path)

    dead = PropagationPolicy(obligations=None, predictions=predictions)
    with pytest.raises(WalkNotAttemptable):
        dead.walk(falsified.prediction_id)

    resolverless = _obligations(tmp_path / "bare", predictions=None)
    half_dead = PropagationPolicy(obligations=resolverless,
                                  predictions=predictions)
    with pytest.raises(WalkNotAttemptable):
        half_dead.walk(falsified.prediction_id)
    assert resolverless.read_all() == (), (
        "the walk propagated to some ancestors before refusing - partial "
        "pressure silently applied is starving's twin (L12)")


# =====================================================================
# PIN 7 - THE ACT LOG: CHAINED FROM GENESIS, AUDIT-CLEAN, TAMPER-EVIDENT
# =====================================================================

def test_the_act_log_chains_from_genesis_and_tamper_reads_chain_break(
        tmp_path) -> None:
    """PIN 7. Clean audit over both act kinds on one ordinal stream; one
    flipped byte -> CHAIN_BREAK."""
    predictions, obligations, falsified = _falsified_walk_kernel(tmp_path)
    log = PredictionActLog(log_path=str(tmp_path / "pra.jsonl"))
    evaluator = CriterionEvaluator(surface_readers={})
    evaluation = evaluator.evaluate(
        predictions.commitment_for(falsified.prediction_id), 0)
    log.record_evaluation(evaluation)
    walk = PropagationPolicy(obligations=obligations,
                             predictions=predictions).walk(
        falsified.prediction_id)
    log.record_propagation(walk)

    report = audit_act_log(log.log_path, PREDICTION_ACT_LOG_SCHEMA)
    assert report.clean, [f.detail for f in report.findings]
    assert report.chained_lines == 2 and report.pre_chain_lines == 0

    raw = Path(log.log_path).read_bytes()
    Path(log.log_path).write_bytes(raw.replace(b"prediction_evaluation_act",
                                               b"prediction_evaluation_ACT",
                                               1))
    tampered = audit_act_log(log.log_path, PREDICTION_ACT_LOG_SCHEMA)
    assert any(f.kind is FindingKind.CHAIN_BREAK for f in tampered.findings)


def test_the_underived_floor_refuses_both_ways(tmp_path) -> None:
    """PIN 7, Ruling 53 both ways: a log that EXISTS and cannot be read
    refuses the mint AND the read, typed - never a fallback number, never an
    empty history."""
    blocked = tmp_path / "pra.jsonl"
    blocked.mkdir()  # exists, unreadable as a file
    log = PredictionActLog(log_path=str(blocked))
    predictions = _predictions(tmp_path)
    subject = predictions.commit(
        expected_result="x",
        operational_criteria=(
            _criterion("goal_status", "GLC-0001", "committed", "superseded"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="goal", record_id="GLC-0001"),))
    evaluation = CriterionEvaluator(surface_readers={}).evaluate(subject, 0)
    with pytest.raises(PredictionActLogUnreadable):
        log.record_evaluation(evaluation)
    with pytest.raises(PredictionActLogUnreadable):
        log.acts()


# =====================================================================
# PIN 8 - THE RESOLUTION CITATION, THROUGH THE WIDENED FUNNEL
# =====================================================================

def test_a_recorded_resolution_carries_criterion_and_evaluator(tmp_path) -> None:
    """PIN 8. Through the loop's door: the resolution cites the operational
    criterion by recorded index and the evaluator by identity, read back off
    the file by a fresh instance."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    target = predictions.commit(expected_result="t",
                                failure_criteria=provided("broke"))
    predictions.resolve(target.prediction_id, PredictionOutcome.FALSIFIED,
                        "failure_criteria")
    subject = predictions.commit(
        expected_result="falsifies against the target's outcome",
        operational_criteria=(
            _criterion("prediction_resolution_outcome",
                       target.prediction_id, "confirmed", "falsified"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.MAIN_CLAIM,
                            record_form="prediction",
                            record_id=target.prediction_id),))
    loop = ExecutiveLoop(obligations=obligations, predictions=predictions,
                         goals=None, acquisitions=None)
    loop.prediction_acts = PredictionActLog(
        log_path=str(tmp_path / "pra.jsonl"))
    evaluation = loop.evaluate_prediction(subject.prediction_id, 0)
    assert evaluation.outcome is EvaluationOutcome.FALSIFIED

    reread = _predictions(tmp_path).resolution_for(subject.prediction_id)
    assert reread is not None
    assert reread.outcome is PredictionOutcome.FALSIFIED
    assert reread.criterion == "operational_criteria[0]"
    assert reread.evaluator == EVALUATOR_NAME

    [act] = loop.prediction_acts.acts()
    assert act["kind_of_record"] == "prediction_evaluation_act"
    assert act["evaluation"]["outcome"] == "falsified"


def test_the_operational_criterion_form_is_fixed_at_commit_time(tmp_path) -> None:
    """PIN 8's refusals: an index never committed refuses; the operational
    form is unwritable against a legacy commitment; a legacy resolution line
    reads back with an empty evaluator (era honesty)."""
    predictions = _predictions(tmp_path)
    subject = predictions.commit(
        expected_result="one criterion",
        operational_criteria=(
            _criterion("goal_status", "GLC-0001", "committed", "superseded"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="goal", record_id="GLC-0001"),))
    with pytest.raises(ValueError):
        predictions.resolve(subject.prediction_id,
                            PredictionOutcome.CONFIRMED,
                            "operational_criteria[1]")
    legacy = predictions.commit(expected_result="legacy",
                                success_criteria=provided("held"))
    with pytest.raises(ValueError):
        predictions.resolve(legacy.prediction_id,
                            PredictionOutcome.CONFIRMED,
                            "operational_criteria[0]")
    recorded = predictions.resolve(legacy.prediction_id,
                                   PredictionOutcome.CONFIRMED,
                                   "success_criteria")
    assert recorded.evaluator == ""
    reread = _predictions(tmp_path).resolution_for(legacy.prediction_id)
    assert reread.evaluator == ""


def test_an_unresolved_evaluation_records_nothing_in_the_ledger(tmp_path) -> None:
    """Section B's cut: an inability to evaluate is an ACT fact. The ledger
    stays untouched; the act line is the only trace, and it carries the
    reason."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    subject = predictions.commit(
        expected_result="no goal handle in the loop, by bounds",
        operational_criteria=(
            _criterion("goal_status", "GLC-0001", "committed", "superseded"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="goal", record_id="GLC-0001"),))
    loop = ExecutiveLoop(obligations=obligations, predictions=predictions,
                         goals=None, acquisitions=None)
    loop.prediction_acts = PredictionActLog(
        log_path=str(tmp_path / "pra.jsonl"))
    evaluation = loop.evaluate_prediction(subject.prediction_id, 0)
    assert evaluation.outcome is EvaluationOutcome.UNRESOLVED_AT_EVALUATION
    assert predictions.resolution_for(subject.prediction_id) is None
    [act] = loop.prediction_acts.acts()
    assert act["gate_one"]["rejection_reason"] == evaluation.reason
    assert evaluation.reason


# =====================================================================
# THE LIVE PATH, END TO END, THROUGH THE LOOP'S DOORS
# =====================================================================

def test_the_first_live_falsification_walk_end_to_end(tmp_path) -> None:
    """Evaluate -> falsify through the funnel -> walk -> act, all through
    the loop's own doors, with the act's census carrying the kernel's real
    dispositions and the walk's act written AFTER the submissions (its
    census cites obligation ids that resolve in the kernel's own store)."""
    predictions = _predictions(tmp_path)
    propositions = PropositionLedger(ledger_path=str(tmp_path / "wmp.jsonl"))
    obligations = _obligations(tmp_path, predictions=predictions,
                               propositions=propositions)
    target = predictions.commit(expected_result="t",
                                failure_criteria=provided("broke"))
    predictions.resolve(target.prediction_id, PredictionOutcome.FALSIFIED,
                        "failure_criteria")
    subject = predictions.commit(
        expected_result="carries exposure; loses; propagates",
        operational_criteria=(
            _criterion("prediction_resolution_outcome",
                       target.prediction_id, "confirmed", "falsified"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="prediction",
                            record_id=target.prediction_id),
            TypedDependency(kind=DependencyKind.ASSUMPTION,
                            record_form="world_proposition",
                            record_id="WMP-4242"),
        ))
    loop = ExecutiveLoop(obligations=obligations, predictions=predictions,
                         goals=None, acquisitions=None)
    loop.prediction_acts = PredictionActLog(
        log_path=str(tmp_path / "pra.jsonl"))

    evaluation = loop.evaluate_prediction(subject.prediction_id, 0)
    assert evaluation.outcome is EvaluationOutcome.FALSIFIED
    walk = loop.propagate_falsification(subject.prediction_id)
    assert [s.disposition for s in walk.submissions] == [
        WalkDisposition.ADMITTED, WalkDisposition.REJECTED_TARGETLESS]

    acts = loop.prediction_acts.acts()
    assert [a["kind_of_record"] for a in acts] == [
        "prediction_evaluation_act", "prediction_propagation_act"]
    propagation = acts[1]
    assert propagation["policy"] == {"identity": POLICY_NAME,
                                     "version": POLICY_VERSION}
    assert propagation["resolution_criterion"] == "operational_criteria[0]"
    census = propagation["dependency_census"]
    assert len(census) == 2
    assert obligations.status_of(census[0]["obligation_id"]) is not None
    report = audit_act_log(loop.prediction_acts.log_path,
                           PREDICTION_ACT_LOG_SCHEMA)
    assert report.clean


def test_a_decisive_evaluation_of_a_resolved_prediction_raises_and_logs_nothing(
        tmp_path) -> None:
    """The door's stated discipline: a decisive evaluation whose `resolve()`
    refuses raises HERE and records no act - nothing claims an evaluation
    consummated that the ledger refused."""
    predictions = _predictions(tmp_path)
    obligations = _obligations(tmp_path, predictions=predictions)
    target = predictions.commit(expected_result="t",
                                success_criteria=provided("held"))
    predictions.resolve(target.prediction_id, PredictionOutcome.CONFIRMED,
                        "success_criteria")
    subject = predictions.commit(
        expected_result="already resolved below",
        operational_criteria=(
            _criterion("prediction_resolution_outcome",
                       target.prediction_id, "confirmed", "falsified"),),
        typed_dependencies=(
            TypedDependency(kind=DependencyKind.MAIN_CLAIM,
                            record_form="prediction",
                            record_id=target.prediction_id),))
    loop = ExecutiveLoop(obligations=obligations, predictions=predictions,
                         goals=None, acquisitions=None)
    loop.prediction_acts = PredictionActLog(
        log_path=str(tmp_path / "pra.jsonl"))
    loop.evaluate_prediction(subject.prediction_id, 0)  # resolves CONFIRMED
    with pytest.raises(ValueError):
        loop.evaluate_prediction(subject.prediction_id, 0)  # resolve-once
    assert len(loop.prediction_acts.acts()) == 1


# =====================================================================
# PIN 9 - THE SEAM CENSUS, AS COMMITTED FACTS
# =====================================================================

def test_the_standing_seam_exists_and_is_not_wired(tmp_path) -> None:
    """PIN 9. THE FINDING, held as pins: (a) the standing profile's STRONG
    pressure vocabulary already names the prospective-prediction class -
    the seam EXISTS as data; (b) evidence enters that derivation only
    through episode records, whose store carries a zero-internal-callers
    law this slice must not break - so NOTHING built here imports the
    episode store or the standing profile. The wiring is one entry away and
    is routed to the ordering, not taken on ambition."""
    from src.doctrine.standing_profile import STRONG_PRESSURE_CLASSES
    assert "precommitted_prediction" in STRONG_PRESSURE_CLASSES

    for module in (EVALUATOR_MODULE, POLICY_MODULE, ACT_LOG_MODULE,
                   Path("src/executive/loop.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        imported = {node.module or "" for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)}
        assert not any("episode_record" in m or "standing_profile" in m
                       for m in imported), (
            f"{module} wired the standing seam without its entry")


# =====================================================================
# THE MIRRORS, DRIFT-PINNED; THE REGISTRATIONS; THE PURITY
# =====================================================================

def test_the_mirrored_vocabularies_equal_their_owners() -> None:
    """The standing profile's boundary rule: a duplicated vocabulary a test
    compares every run is a boundary, not a hazard."""
    assert EvaluationOutcome.CONFIRMED.value == PredictionOutcome.CONFIRMED.value
    assert EvaluationOutcome.FALSIFIED.value == PredictionOutcome.FALSIFIED.value
    kernel_values = {m.value for m in KernelDisposition}
    for member in WalkDisposition:
        assert member.value in kernel_values, (
            f"WalkDisposition.{member.name} drifted from the kernel-answer "
            f"vocabulary it mirrors")
    assert {m.value for m in WalkDisposition} == (
        kernel_values - {KernelDisposition.NOT_SUBMITTED.value}), (
        "the mirror must cover exactly the SUBMITTED answers - a walk that "
        "did not submit does not exist")


def test_both_instruments_are_registered_as_data() -> None:
    for registration, identity, version in (
            (EVALUATOR_REGISTRATION, EVALUATOR_NAME, EVALUATOR_VERSION),
            (POLICY_REGISTRATION, POLICY_NAME, POLICY_VERSION)):
        assert registration["identity"] == identity
        assert registration["version"] == version
        assert registration["kind"] == "deterministic_non_model_instrument"
        assert registration["contract"] == "registration"
        assert registration["declared_invariants"]
        with pytest.raises(TypeError):
            registration["identity"] = "impostor"  # mappingproxy refuses


def test_the_evaluator_imports_the_census_and_nothing_else_from_src() -> None:
    """The handoff's no-import-expansion bar, AST-pinned."""
    tree = ast.parse(EVALUATOR_MODULE.read_text(encoding="utf-8"))
    src_imports = {node.module for node in ast.walk(tree)
                   if isinstance(node, ast.ImportFrom)
                   and (node.module or "").startswith("src")}
    assert src_imports == {"src.external.prediction_census"}, src_imports


def test_the_walk_module_reaches_no_store_and_no_kernel_writer() -> None:
    """The policy holds handles; it imports no ledger, opens no file."""
    tree = ast.parse(POLICY_MODULE.read_text(encoding="utf-8"))
    src_imports = {node.module for node in ast.walk(tree)
                   if isinstance(node, ast.ImportFrom)
                   and (node.module or "").startswith("src")}
    assert src_imports == set(), src_imports
    opens = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open"]
    assert opens == []
