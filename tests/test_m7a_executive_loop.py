"""M7-a: the Executive loop skeleton and the derived view.

WHAT THESE TESTS PIN, in the grounding's own order:
  * the view is a PURE DERIVATION -- two derives over one kernel are equal,
    and a SECOND LOOP over the same ledgers derives the SAME view
    (Test 6 in miniature: reconstruction loses nothing);
  * the chair is DERIVED from the consumed-verdict acquisition, never
    hardwired -- UNREGISTERED before the record exists,
    EMPTY_BY_REFUSED_VERDICT after, citing the ACQ- id;
  * the first submission writes EXACTLY ONE acquisition and a second
    registration REFUSES (fires-control);
  * the choosing edge is UNEXECUTABLE without a bound policy
    (fires-control) while observation stays available;
  * a ConsumedVerdict that is not the M5 REFUSED fact refuses construction
    (fires-control).

HANDLE DISCIPLINE: the loop and the derivation take duck-typed read handles by
design (episode_record.py's M3-B precedent). These tests use REAL ledgers
where their write APIs are simple (ObligationLedger, AcquisitionLedger,
PredictionLedger's commit) and MINIMAL STUBS where construction machinery is
another milestone's subject (GoalLedger.commit's criterion vocabulary; a
PredictionResolution for the subtraction case). A stub here carries only the
read method the derivation names, which is exactly the contract.
"""

import pytest

from src.executive.derived_view import ChairState, derive
from src.executive.loop import (
    ConsumedVerdict,
    ExecutiveLoop,
    MalformedConsumedVerdict,
    NoAttentionPolicyBound,
    VerdictAlreadyRegistered,
)
from src.external.acquisition_ledger import AcquisitionLedger
from src.external.prediction_ledger import PredictionLedger
from src.filtration.obligation_ledger import ObligationLedger


# ---------------------------------------------------------------------------
# Minimal duck-typed stubs -- each carries ONLY the read method derive() names.
# ---------------------------------------------------------------------------

class _StubGoals:
    def __init__(self, goal_ids=()):
        self._ids = tuple(goal_ids)

    def commitments(self):
        return tuple(_StubGoalCommitment(g) for g in self._ids)


class _StubGoalCommitment:
    def __init__(self, goal_id):
        self.goal_id = goal_id


class _StubPredictions:
    """Commitments and resolutions as plain id-bearing objects."""

    def __init__(self, committed=(), resolved=()):
        self._committed = tuple(committed)
        self._resolved = tuple(resolved)

    def commitments(self):
        return tuple(_StubPredId(p) for p in self._committed)

    def resolutions(self):
        return tuple(_StubPredId(p) for p in self._resolved)


class _StubPredId:
    def __init__(self, prediction_id):
        self.prediction_id = prediction_id


# ---------------------------------------------------------------------------
# Fixtures: real ledgers on tmp_path.
# ---------------------------------------------------------------------------

@pytest.fixture()
def kernel(tmp_path):
    obligations = ObligationLedger(
        ledger_path=str(tmp_path / "obligations.jsonl"))
    predictions = PredictionLedger(
        ledger_path=str(tmp_path / "predictions.jsonl"))
    acquisitions = AcquisitionLedger(
        ledger_path=str(tmp_path / "acquisitions.jsonl"))
    goals = _StubGoals(("GLC-0001", "GLC-0002"))
    return obligations, predictions, goals, acquisitions


def _the_verdict():
    return ConsumedVerdict(
        role_id="ROLE-EXECUTIVE-DELEGATED-COGNITION",
        verdict="REFUSED",
        foundry_commit="c1930d6",
        record_path="references/m5-gamma-4-qualification-record.md",
        protocol_sha256s=(
            "1dbdcefb908b1b7341be90e67ad353b4dceef795e9377fe3513c1ede2e1874f7",
            "9face257c39af3ca9d1544b57a47ea9c6e79d4870bcdfaa5092d56ac7878c7d5",
        ),
        failed_surfaces=("Q1",),
        unestablished_surfaces=("Q2", "Q3"),
    )


# ---------------------------------------------------------------------------
# Derivation purity and content.
# ---------------------------------------------------------------------------

def test_two_derives_over_one_kernel_are_equal(kernel):
    obligations, predictions, goals, acquisitions = kernel
    obligations.admit("test", "claim", "CLM-0001", "a claim under pressure")
    first = derive(obligations, predictions, goals, acquisitions)
    second = derive(obligations, predictions, goals, acquisitions)
    assert first == second


def test_open_obligations_appear_in_ledger_order(kernel):
    obligations, predictions, goals, acquisitions = kernel
    a = obligations.admit("test", "claim", "CLM-0001", "first conflict")
    b = obligations.admit("test", "claim", "CLM-0002", "second conflict")
    assert a.admitted and b.admitted
    view = derive(obligations, predictions, goals, acquisitions)
    assert view.open_obligations == (a.obligation_id, b.obligation_id)


def test_unresolved_predictions_subtract_resolutions():
    predictions = _StubPredictions(
        committed=("PRD-0001", "PRD-0002", "PRD-0003"),
        resolved=("PRD-0002",))
    view = derive(_EmptyObligations(), predictions, _StubGoals(),
                  _EmptyAcquisitions())
    assert view.unresolved_predictions == ("PRD-0001", "PRD-0003")


def test_real_prediction_commitments_with_no_resolutions_are_unresolved(kernel):
    obligations, predictions, goals, acquisitions = kernel
    committed = predictions.commit("the suite stays green through M7-a")
    view = derive(obligations, predictions, goals, acquisitions)
    assert view.unresolved_predictions == (committed.prediction_id,)


def test_committed_goals_preserve_commitment_order(kernel):
    obligations, predictions, goals, acquisitions = kernel
    view = derive(obligations, predictions, goals, acquisitions)
    assert view.committed_goals == ("GLC-0001", "GLC-0002")


class _EmptyObligations:
    def open_items(self):
        return []


class _EmptyAcquisitions:
    def read_all(self):
        return []


# ---------------------------------------------------------------------------
# The chair: derived, never hardwired.
# ---------------------------------------------------------------------------

def test_chair_is_unregistered_before_the_first_submission(kernel):
    obligations, predictions, goals, acquisitions = kernel
    view = derive(obligations, predictions, goals, acquisitions)
    assert view.chair is ChairState.UNREGISTERED
    assert view.verdict_acquisition_id is None


def test_registration_derives_the_empty_chair_and_cites_the_record(kernel):
    obligations, predictions, goals, acquisitions = kernel
    loop = ExecutiveLoop(obligations, predictions, goals, acquisitions)
    acq_id = loop.register_consumed_verdict(_the_verdict())
    view = loop.observe()
    assert view.chair is ChairState.EMPTY_BY_REFUSED_VERDICT
    assert view.verdict_acquisition_id == acq_id
    # Exactly one boundary fact was minted for the one event.
    payloads = [r.payload for r in acquisitions.read_all()]
    assert len(payloads) == 1
    assert "c1930d6" in payloads[0]
    assert "REFUSED" in payloads[0]


def test_a_second_registration_refuses_as_fabrication(kernel):
    obligations, predictions, goals, acquisitions = kernel
    loop = ExecutiveLoop(obligations, predictions, goals, acquisitions)
    loop.register_consumed_verdict(_the_verdict())
    with pytest.raises(VerdictAlreadyRegistered):
        loop.register_consumed_verdict(_the_verdict())
    assert len(acquisitions.read_all()) == 1


def test_a_non_refused_consumption_refuses_construction():
    with pytest.raises(MalformedConsumedVerdict):
        ConsumedVerdict(
            role_id="ROLE-EXECUTIVE-DELEGATED-COGNITION",
            verdict="QUALIFIED",
            foundry_commit="c1930d6",
            record_path="references/m5-gamma-4-qualification-record.md",
            protocol_sha256s=("1dbdcefb",),
            failed_surfaces=(),
            unestablished_surfaces=(),
        )


def test_a_registration_without_protocol_digests_refuses():
    with pytest.raises(MalformedConsumedVerdict):
        ConsumedVerdict(
            role_id="ROLE-EXECUTIVE-DELEGATED-COGNITION",
            verdict="REFUSED",
            foundry_commit="c1930d6",
            record_path="references/m5-gamma-4-qualification-record.md",
            protocol_sha256s=(),
            failed_surfaces=("Q1",),
            unestablished_surfaces=(),
        )


# ---------------------------------------------------------------------------
# The choosing edge is unexecutable in v-a.
# ---------------------------------------------------------------------------

def test_step_without_a_policy_refuses_while_observe_stays_available(kernel):
    obligations, predictions, goals, acquisitions = kernel
    loop = ExecutiveLoop(obligations, predictions, goals, acquisitions)
    view = loop.observe()
    assert view.chair is ChairState.UNREGISTERED
    with pytest.raises(NoAttentionPolicyBound):
        loop.step()


# ---------------------------------------------------------------------------
# Test 6 in miniature: reconstruction loses nothing.
# ---------------------------------------------------------------------------

def test_a_second_loop_over_the_same_ledgers_derives_the_same_view(kernel):
    obligations, predictions, goals, acquisitions = kernel
    first_loop = ExecutiveLoop(obligations, predictions, goals, acquisitions)
    obligations.admit("test", "claim", "CLM-0009", "a fact worth arguing")
    predictions.commit("the rebuilt loop sees this commitment")
    first_loop.register_consumed_verdict(_the_verdict())
    before = first_loop.observe()

    # The first loop is dropped; new handles are built over the SAME files,
    # the way a fresh process would after the first one was killed.
    rebuilt = ExecutiveLoop(
        ObligationLedger(ledger_path=str(obligations.ledger_path)),
        PredictionLedger(ledger_path=str(predictions.ledger_path)),
        goals,
        AcquisitionLedger(ledger_path=str(acquisitions.ledger_path)),
    )
    after = rebuilt.observe()
    assert before == after
    assert after.chair is ChairState.EMPTY_BY_REFUSED_VERDICT
