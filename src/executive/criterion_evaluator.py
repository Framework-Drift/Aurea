"""M9-b: `criterion-evaluator.v1` -- line 122's clerical read, and nothing else.

Hundred-eighteenth entry (PATH v144), M9_GROUNDING.md section M9-b, on heading
line 122: *"resolution criteria fixed before outcomes exist, in operational
terms, so disposition-time interpretation approaches clerical."* This module is
the clerical part made literal: it FETCHES the censused surface's state for the
criterion's record id and COMPARES. Equal to the criterion's CONFIRMED state ->
CONFIRMED; equal to its FAILED state -> FALSIFIED; anything else -- the
surface's other closed states, an unresolvable id, a missing handle, a read
that raised -- is UNRESOLVED_AT_EVALUATION **with the reason recorded**, never
a default to either arm and never survival by inability (L6's own posture:
budget exhaustion resolves to its own state, never to survival).

PURE, ON THE STAKE CLASSIFIER'S EXACT DISCIPLINE
-------------------------------------------------------------------------------
Imports the census (DATA -- `prediction_census` imports nothing from `src/`)
and nothing else from `src/`. No ledger, no path, no `open`, no `datetime`, no
randomness. The four censused surfaces arrive as INJECTED READERS at
construction -- the resolver-injection pattern the obligation ledger and the
M9-a door already use -- so the census's excluded doctrine/scar surfaces stay
excluded STRUCTURALLY in v1: there is no key they could ride in under, and
their reopening remains a future entry's act.

THE CRITERION'S DATA DECIDES; THE EVALUATOR ONLY READS
-------------------------------------------------------------------------------
Two evaluators over one kernel agree by construction, because everything that
could vary is recorded criterion data: the surface, the record id, and which
state resolves which way. The reader contract is one callable per censused
surface key, `record_id -> state-or-None`, where the state is the owner's own
value (an Enum member is normalized through `.value`). A reader for a key
outside the census is REFUSED at construction -- an evaluator holding a
surface nobody ruled would be the invention the census exists to prevent.

WHAT AN EVALUATION IS NOT: it records nothing anywhere. Recording a decisive
outcome is the prediction ledger's `resolve()` (the existing funnel, widened
additively this slice); recording the evaluation ACT is the prediction act
log's. An UNRESOLVED_AT_EVALUATION reaches the ledger NOT AT ALL -- an
inability to evaluate is an act fact, not a prediction fact.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional

from src.external.prediction_census import CRITERION_SURFACES

__all__ = [
    "EVALUATOR_NAME", "EVALUATOR_VERSION", "REGISTRATION",
    "EvaluationOutcome", "CriterionEvaluation", "CriterionEvaluator",
    "NonOperationalCommitment", "UnruledSurfaceReader",
]

EVALUATOR_NAME = "criterion-evaluator.v1"
EVALUATOR_VERSION = "1"


class NonOperationalCommitment(Exception):
    """The commitment carries no evaluable exposure -- REFUSED BY NAME.

    NON-OPERATIONAL is an honest recorded state (M9-a: ABSENT is an answer),
    and it is precisely what M7-c's HORIZONLESS class already asks about.
    Evaluating one would mean inventing the criterion the record does not
    carry, which is the exact rewriting the prediction ledger exists to
    prevent.
    """


class UnruledSurfaceReader(Exception):
    """A reader was offered for a surface key outside the committed census."""


class EvaluationOutcome(str, Enum):
    """What one clerical read concluded. CLOSED at three.

    CONFIRMED and FALSIFIED mirror `PredictionOutcome`'s own values (pinned
    equal in tests, never imported -- this module's import set is the census
    and stdlib, and the mirror-plus-pin is the house's third option for a
    purity boundary, `standing_profile`'s own move). UNRESOLVED_AT_EVALUATION
    is this entry's member: the read happened and could not settle the
    question, which is L6's `UNRESOLVED_AT_BOUND` posture at the evaluation
    layer -- never survival, never a default.
    """

    CONFIRMED = "confirmed"
    FALSIFIED = "falsified"
    UNRESOLVED_AT_EVALUATION = "unresolved_at_evaluation"


REGISTRATION: Mapping[str, Any] = MappingProxyType({
    "identity": EVALUATOR_NAME,
    "version": EVALUATOR_VERSION,
    "kind": "deterministic_non_model_instrument",
    "contract": "registration",
    "declared_invariants": (
        "clerical: an evaluation is a read of the criterion's censused "
        "surface and an equality comparison, nothing more",
        "deterministic: the criterion's data decides; two evaluators over "
        "one kernel state agree by construction",
        "pure: no store, clock, io or randomness is reachable from this "
        "module; surfaces arrive as injected readers",
        "closed surfaces: readers are accepted for the census's four "
        "criterion surfaces only",
        "no default arm: anything but an exact match on a declared state is "
        "UNRESOLVED_AT_EVALUATION with its reason recorded",
    ),
})


@dataclass(frozen=True)
class CriterionEvaluation:
    """ONE clerical read, with everything a reader needs to re-derive it."""

    prediction_id: str
    criterion_index: int
    #: The criterion AS RECORDED on the commitment (its own as_dict).
    criterion: Mapping[str, Any]
    surface: str
    #: The state the surface showed, or None where no state could be read.
    surface_state: Optional[str]
    outcome: EvaluationOutcome
    #: Non-empty exactly when the outcome is UNRESOLVED_AT_EVALUATION.
    reason: str = ""
    evaluator_name: str = EVALUATOR_NAME
    evaluator_version: str = EVALUATOR_VERSION

    def as_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "criterion_index": self.criterion_index,
            "criterion": dict(self.criterion),
            "surface": self.surface,
            "surface_state": self.surface_state,
            "outcome": self.outcome.value,
            "reason": self.reason,
            "evaluator_name": self.evaluator_name,
            "evaluator_version": self.evaluator_version,
        }


class CriterionEvaluator:
    """The clerical evaluator. Holds readers, reads once, compares once."""

    def __init__(self,
                 surface_readers: Optional[Mapping[str, Callable[[str], Any]]]
                 = None):
        readers = dict(surface_readers or {})
        for key in readers:
            if key not in CRITERION_SURFACES:
                raise UnruledSurfaceReader(
                    f"'{key}' is not a censused criterion surface. The census "
                    f"holds {sorted(CRITERION_SURFACES)}; an evaluator holding "
                    f"a surface nobody ruled would be the invention the "
                    f"census exists to prevent, and the excluded doctrine/"
                    f"scar surfaces reopen by a future entry, not a keyword.")
        # A MISSING reader is legal and honest: evaluation against it is
        # UNRESOLVED_AT_EVALUATION with the reason recorded, never a refusal
        # at construction -- an evaluator wired for two surfaces can still
        # answer everything it can actually read.
        self._readers: Dict[str, Callable[[str], Any]] = readers

    def evaluate(self, commitment: Any, criterion_index: int
                 ) -> CriterionEvaluation:
        """Evaluate ONE recorded criterion. The unit is the criterion.

        A commitment may carry several; each evaluation is its own act, and
        aggregation across them is a judgment no entry has ruled -- so none
        happens here. The caller names the criterion by its recorded index.
        """
        if not commitment.is_operational():
            raise NonOperationalCommitment(
                f"'{commitment.prediction_id}' is NON-OPERATIONAL -- it "
                f"carries no operational criteria or no typed dependencies. "
                f"That is an honest recorded state (M9-a: ABSENT is an "
                f"answer), not an evaluable one: evaluating it would invent "
                f"the criterion the record does not carry.")
        criteria = commitment.operational_criteria
        if not 0 <= criterion_index < len(criteria):
            raise ValueError(
                f"'{commitment.prediction_id}' records "
                f"{len(criteria)} operational criteria; index "
                f"{criterion_index} names none of them. Criteria are FIXED "
                f"AT COMMIT TIME, and an evaluation may not name one that "
                f"was never committed.")
        criterion = criteria[criterion_index]

        def unresolved(state: Optional[str], reason: str) -> CriterionEvaluation:
            return CriterionEvaluation(
                prediction_id=commitment.prediction_id,
                criterion_index=criterion_index,
                criterion=criterion.as_dict(),
                surface=criterion.surface,
                surface_state=state,
                outcome=EvaluationOutcome.UNRESOLVED_AT_EVALUATION,
                reason=reason)

        reader = self._readers.get(criterion.surface)
        if reader is None:
            return unresolved(None, (
                f"no reader is held for surface '{criterion.surface}'; the "
                f"surface was not consulted, which is a different fact from "
                f"a state that did not match (the two-absences cut)"))
        try:
            state = reader(criterion.record_id)
        except Exception as failure:  # noqa: BLE001 - the read is the risk,
            # and ANY failure of it must land as inability, never as an arm.
            return unresolved(None, (
                f"the surface read raised {type(failure).__name__}: "
                f"{failure} -- an unreadable surface cannot confirm or "
                f"falsify anything"))
        state = getattr(state, "value", state)
        if state is None:
            return unresolved(None, (
                f"the surface holds no state for '{criterion.record_id}' -- "
                f"an unresolvable id settles nothing"))
        if not isinstance(state, str):
            return unresolved(None, (
                f"the surface returned {type(state).__name__}, not a state "
                f"value; comparing it would coin a reading"))

        if state == criterion.confirmed_state:
            outcome = EvaluationOutcome.CONFIRMED
        elif state == criterion.failed_state:
            outcome = EvaluationOutcome.FALSIFIED
        else:
            return unresolved(state, (
                f"the surface shows '{state}', which is neither the recorded "
                f"CONFIRMED state ('{criterion.confirmed_state}') nor the "
                f"recorded FAILED state ('{criterion.failed_state}') -- a "
                f"third state resolves nothing, and reading it as either arm "
                f"would be the default this instrument refuses"))
        return CriterionEvaluation(
            prediction_id=commitment.prediction_id,
            criterion_index=criterion_index,
            criterion=criterion.as_dict(),
            surface=criterion.surface,
            surface_state=state,
            outcome=outcome)
