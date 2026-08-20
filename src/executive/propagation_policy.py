"""M9-b: `propagation-policy.v1` -- falsification propagates backward, whole.

Hundred-eighteenth entry (PATH v144), M9_GROUNDING.md section M9-b, on heading
line 122: *"Falsification propagates backward as obligations on the failed
dependency -- observation, causal link, assumption, scope, horizon, or main
claim."* The propagation medium is ALREADY BUILT (the grounding's MOVE TWO):
this policy is a deterministic walk over recorded typed dependencies that
SUBMITS through the obligation ledger's existing `admit()`, and the kernel
dispositions as it always has. No new store, no new admission path, no
selection judgment anywhere.

TOTAL, AND WHY TOTALITY IS THE PIN (L12)
-------------------------------------------------------------------------------
The walk covers EVERY recorded typed dependency of the falsified prediction --
all kinds, all of them, in declaration order. The heading's "on the failed
dependency" resolves at v1 to ALL recorded dependencies, because v1 records no
per-dependency failure attribution and inventing one would be a coined
judgment at the exact point pressure is being routed. A walk that skipped a
dependency would be pressure-starving in time; **the totality IS the
anti-starvation guarantee -- no selection judgment exists to be biased.**

THE KERNEL'S ANSWER PER DEPENDENCY IS THE RECORD, WHATEVER IT IS
-------------------------------------------------------------------------------
ADMITTED, a DUPLICATE rejection where an identical claim already stands, a
TARGETLESS rejection where the id resolves nowhere, a MALFORMED rejection for
a censused reference form outside the kernel's own `TargetKind` (goal,
episode, obligation -- **no TargetKind widening in this slice**; the
rejection log that answers for every unadmitted challenge is Acceptance Test
1's own language). Every answer is captured as received through the
`WalkDisposition` vocabulary (a drift-pinned mirror -- see its docstring);
none is engineered around, none coerced.

WHOLE OR NOT AT ALL -- THE ATTEMPTABILITY PREFLIGHT
-------------------------------------------------------------------------------
If any dependency's submission cannot even be ATTEMPTED -- a dead obligation
handle, or a prediction-form dependency against a ledger holding no prediction
resolver (whose `admit()` would RAISE `UncheckableTarget` mid-walk by its own
law) -- the walk REFUSES WHOLE, BEFORE the first submission. Partial pressure
silently applied is starving's twin (L12), and the probe discipline binds: a
refusal before anything begins spends nothing. An unexpected raise mid-walk
still propagates loudly -- the submissions already landed are kernel records
and the kernel's ledger is its own truth; what is missing is the walk's act,
and a loud failure is what says so.

PURE OVER INJECTED HANDLES, WRITES NOTHING ITSELF: the only write this walk
causes is the kernel's own, through the kernel's own door.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple

__all__ = [
    "POLICY_NAME", "POLICY_VERSION", "REGISTRATION", "WalkDisposition",
    "DependencySubmission", "FalsificationWalk", "PropagationPolicy",
    "WalkOnUnfalsified", "WalkNotAttemptable", "UnmappedKernelAnswer",
]

POLICY_NAME = "propagation-policy.v1"
POLICY_VERSION = "1"


class WalkOnUnfalsified(Exception):
    """The walk was invoked on a prediction that is not resolved FALSIFIED.

    Backward propagation is the CONSEQUENCE of a falsification on the record.
    Walking an unresolved or confirmed prediction would apply pressure no
    outcome licensed.
    """


class WalkNotAttemptable(Exception):
    """Some dependency's submission could not even be ATTEMPTED.

    Refused WHOLE and BEFORE the first submission (L12): a walk that
    propagated to some ancestors and not others would be partial pressure
    silently applied. Nothing was begun, so nothing needs an act record.
    """


class UnmappedKernelAnswer(Exception):
    """The kernel returned an answer this policy has no recorded member for.

    Deliberately NOT `loop.UnmappedKernelDisposition` -- sharing the type
    would make a caller's `except` catch a mismatch it never meant to handle
    (the escalation policy's own reasoning for its identity exception), and
    importing the loop here would be a cycle. Same posture, own name: the
    kernel's vocabulary moved, and recording a neighbour would put a
    disposition on a permanent record the kernel never gave.
    """


class WalkDisposition(str, Enum):
    """WHAT THE KERNEL SAID about one dependency's submission, as received.

    A MIRROR OF `inquiry_log.KernelDisposition`'s submitted answers, VALUES
    IDENTICAL, PINNED EQUAL IN TESTS AND NEVER IMPORTED -- the standing
    profile's third option for a purity boundary, forced here by a byte-frozen
    consumer census: `test_m7c_inquiry` closes the inquiry log's importer set
    at `loop.py`, and this slice's own standing constraint holds every prior
    executive pin file byte-unmodified. A duplicated vocabulary a test
    compares every run is a boundary; one nobody compares would be the drift
    hazard (Ruling 35), and the drift pin is in
    `tests/test_m9b_resolution_walk.py`.

    NO `NOT_SUBMITTED` MEMBER, AND THE ABSENCE IS THE TOTALITY LAW: a walk
    that did not submit a dependency does not exist -- it refused whole
    before submitting anything. There is no state for a skipped ancestor
    because a skipped ancestor is unrepresentable.
    """

    ADMITTED = "admitted"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_TARGETLESS = "rejected_targetless"
    REJECTED_MALFORMED = "rejected_malformed"


REGISTRATION: Mapping[str, Any] = MappingProxyType({
    "identity": POLICY_NAME,
    "version": POLICY_VERSION,
    "kind": "deterministic_non_model_instrument",
    "contract": "registration",
    "declared_invariants": (
        "total: every recorded typed dependency of the falsified prediction "
        "is submitted, all kinds, in declaration order -- no selection "
        "judgment exists",
        "deterministic: same falsified commitment over the same kernel state "
        "yields the same walk",
        "kernel-dispositioned: every submission's answer is recorded as "
        "received through the kernel's own door; none engineered around",
        "whole-or-nothing: an unattemptable submission refuses the walk "
        "before anything is submitted",
        "falsified-only: a walk on any other resolution state refuses",
    ),
})


@dataclass(frozen=True)
class DependencySubmission:
    """ONE dependency's submission and the kernel's answer, as received."""

    dependency_kind: str
    record_form: str
    record_id: str
    claim_text: str
    disposition: WalkDisposition
    obligation_id: Optional[str] = None
    rejection_reason: str = ""
    target_resolution: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "dependency_kind": self.dependency_kind,
            "record_form": self.record_form,
            "record_id": self.record_id,
            "claim_text": self.claim_text,
            "disposition": self.disposition.value,
            "obligation_id": self.obligation_id,
            "rejection_reason": self.rejection_reason,
            "target_resolution": self.target_resolution,
        }


@dataclass(frozen=True)
class FalsificationWalk:
    """ONE whole walk: the falsified prediction, the census, every answer."""

    prediction_id: str
    resolution_criterion: str
    submissions: Tuple[DependencySubmission, ...]
    policy_name: str = POLICY_NAME
    policy_version: str = POLICY_VERSION


class PropagationPolicy:
    """The backward walk. Reads two handles; the kernel does every write."""

    def __init__(self, obligations: Any = None, predictions: Any = None):
        # READ-AND-SUBMIT handles, injected (the obligation ledger's own
        # resolver-injection shape). `obligations` receives submissions
        # through ITS door; `predictions` is read for the commitment and its
        # resolution. Neither is opened, neither is written by this module.
        self.obligations = obligations
        self.predictions = predictions

    @staticmethod
    def _claim_text(prediction_id: str, resolution_criterion: str,
                    dependency: Any) -> str:
        """DERIVED, never composed as prose -- the loop's `_claim_text` rule.

        The kernel's duplicate check compares normalized claim text, so the
        text is a deterministic function of the recorded facts and nothing
        else: identical falsification-and-dependency pairs produce identical
        text by construction, and a re-walk of the same falsification draws
        the kernel's own DUPLICATE disposition rather than a second standing
        obligation.
        """
        return (f"falsified_prediction_dependency: {prediction_id} "
                f"against {resolution_criterion}; "
                f"{dependency.kind.value}: "
                f"{dependency.record_form}:{dependency.record_id}")

    @staticmethod
    def _disposition(result: Any) -> WalkDisposition:
        """Map the kernel's OWN answer onto the mirrored vocabulary.

        A TRANSLATION, NEVER A JUDGEMENT (the loop's `_disposition` rule,
        restated at this door): every branch reads a field the ledger set,
        and an unrecognised rejection kind raises rather than coercing."""
        if getattr(result, "admitted", False):
            return WalkDisposition.ADMITTED
        kind = getattr(getattr(result, "rejection_kind", None), "value", None)
        mapped = {
            "duplicate": WalkDisposition.REJECTED_DUPLICATE,
            "targetless": WalkDisposition.REJECTED_TARGETLESS,
            "malformed": WalkDisposition.REJECTED_MALFORMED,
        }.get(kind)
        if mapped is None:
            raise UnmappedKernelAnswer(
                f"the obligation ledger returned rejection kind {kind!r}, "
                f"which this walk has no recorded member for. The kernel's "
                f"vocabulary has moved; recording the nearest neighbour "
                f"would put a disposition on a permanent record that the "
                f"kernel never gave.")
        return mapped

    def walk(self, prediction_id: str) -> FalsificationWalk:
        """Propagate ONE falsification backward, whole. Returns the census.

        The caller records the walk's ACT (after these submissions, carrying
        their real dispositions); this method's only writes are the kernel's
        own, through `admit()`.
        """
        if self.predictions is None:
            raise WalkNotAttemptable(
                "no prediction handle is held, so neither the commitment nor "
                "its resolution can be read. Nothing was submitted.")
        commitment = self.predictions.commitment_for(prediction_id)
        if commitment is None:
            raise ValueError(
                f"no commitment '{prediction_id}' is recorded; there is "
                f"nothing to walk.")
        resolution = self.predictions.resolution_for(prediction_id)
        outcome = getattr(getattr(resolution, "outcome", None), "value", None)
        if outcome != "falsified":
            raise WalkOnUnfalsified(
                f"'{prediction_id}' is "
                f"{'unresolved' if resolution is None else outcome!r}, not "
                f"falsified. Backward propagation is the consequence of a "
                f"falsification on the record; nothing else licenses it.")

        dependencies = tuple(commitment.typed_dependencies)

        # THE ATTEMPTABILITY PREFLIGHT -- whole or nothing, BEFORE the first
        # submission (L12; the probe's refusal-before-begun posture).
        if self.obligations is None or not callable(
                getattr(self.obligations, "admit", None)):
            raise WalkNotAttemptable(
                f"the obligation handle is dead (no callable `admit`), so no "
                f"dependency of '{prediction_id}' can be submitted. The walk "
                f"refuses WHOLE: propagating to none beats propagating to "
                f"some.")
        if any(dep.record_form == "prediction" for dep in dependencies) and \
                getattr(self.obligations, "prediction_ledger", None) is None:
            raise WalkNotAttemptable(
                f"'{prediction_id}' records a prediction-form dependency and "
                f"the obligation ledger holds no prediction resolver -- its "
                f"own door RAISES `UncheckableTarget` on that submission by "
                f"law. Mid-walk, that raise would leave earlier ancestors "
                f"pressured and later ones not; the walk refuses WHOLE, "
                f"before anything is submitted.")

        submissions = []
        for dependency in dependencies:  # DECLARATION ORDER -- the census's
            # own order, so the walk is deterministic with nothing to sort.
            claim = self._claim_text(
                prediction_id, resolution.criterion, dependency)
            result = self.obligations.admit(
                f"{POLICY_NAME}:{prediction_id}",
                dependency.record_form,
                dependency.record_id,
                claim)
            submissions.append(DependencySubmission(
                dependency_kind=dependency.kind.value,
                record_form=dependency.record_form,
                record_id=dependency.record_id,
                claim_text=claim,
                disposition=self._disposition(result),
                obligation_id=(getattr(result, "obligation_id", "") or None),
                rejection_reason=getattr(result, "reason", ""),
                target_resolution=getattr(
                    getattr(result, "target_resolution", None), "value", ""),
            ))
        return FalsificationWalk(
            prediction_id=prediction_id,
            resolution_criterion=resolution.criterion,
            submissions=tuple(submissions))
