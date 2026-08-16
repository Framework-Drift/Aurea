"""M7-c: `inquiry-generator.v1` -- endogenous inquiry, scoped and depth-bounded.

Heading Phase 7: *the loop generates subordinate questions... under existing
goals, with provenance and depth accounting.* Every clause of that sentence is a
constraint this module enforces rather than describes -- SUBORDINATE (a citation
to an ancestor goal, derived from records), PROVENANCE (the source records ride
on every candidate), DEPTH ACCOUNTING (live from the first commit, not deferred
to the day recursion becomes possible).

PURE, ON THE ATTENTION POLICY'S EXACT DISCIPLINE
-------------------------------------------------------------------------------
Imports the derived view and NOTHING else from `src/`. No ledger, no path, no
`open`, no `datetime`, no `random`. It examines ONE observation and returns a
deterministic candidate set; it submits nothing, records nothing, and has no
side effect of any kind. The submitting/recording act is the loop's, which is
the select/record split for a third time (arbiter, attention policy, here).

THE PARTITION IS TOTAL, AND THAT IS THE POINT
-------------------------------------------------------------------------------
Every candidate is EITHER a LICENSED INQUIRY or a DRIFT FINDING. **A candidate
that is neither admitted nor recorded is the one forbidden outcome** -- the
grounding's "surfaced, never silently pursued" has a mirror clause that matters
just as much: never silently DROPPED either. Ruling 23's law (unresolved
pressure never leaves silently) at the Executive's own front door.

WHAT v1 DOES NOT DO, AND WHY
-------------------------------------------------------------------------------
  * **CLAIM-VS-CLAIM INCONSISTENCY IS OUT.** "Why are A and B inconsistent" is
    the kernel's own conflict machinery, and obligations already ARE that
    record. v1 duplicating it would put a second author on the kernel's page.
  * **IT NEVER DEDUPLICATES.** Re-deriving the same overdue prediction on the
    next cycle submits again, and the LEDGER's duplicate disposition is the
    answer, recorded as received. A generator that suppressed its own repeats
    would be the Executive dispositioning, which is the kernel's half of
    section 5 -- and it would have to read its own log to do it, which is the
    class the selection log's no-consumer pin closed one slice ago.
  * **IT CREATES NO GOALS.** Sovereign goal creation is barred by name. An
    unlicensable candidate becomes a finding; it does NOT get a maintenance
    goal invented to license it, which would be the generator authorising its
    own scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Tuple

from src.executive.derived_view import (
    DerivedView,
    GoalFacts,
    PredictionFacts,
)

__all__ = [
    "GENERATOR_NAME", "GENERATOR_VERSION", "MAX_DERIVATION_DEPTH",
    "DiscrepancyClass", "DriftBasis", "LicenseBasis", "CandidatePartition",
    "InquiryCandidate", "InquiryGenerator", "GeneratorIdentityMismatch",
]


# IDENTITY IS DATA, NOT CONVENTION - the attention policy's rule, verbatim.
GENERATOR_NAME = "inquiry-generator.v1"
GENERATOR_VERSION = "1"

# **DEPTH IS A COUNT OF DERIVATION HOPS, AND IT IS NOT A COINED MAGNITUDE.**
# v1 generates at depth 1 - candidates whose source records are kernel-native.
# The ceiling is 1 because v1 is the first generation there has ever been, so
# any second hop is by definition an inquiry about this module's own output.
# Raising it is a ruling, not a tuning knob: the number does not select a
# behaviour from a range, it names which hop is the first recursive one.
MAX_DERIVATION_DEPTH = 1


class GeneratorIdentityMismatch(Exception):
    """Construction named an identity this module does not carry.

    A record citing a generator that never ran is worse than no record, because
    it cannot be told from a true one.
    """


class DiscrepancyClass(str, Enum):
    """WHAT was noticed. CLOSED at two for v1, and both are threshold-free.

    Both come from the prediction ledger and both are the grounding's own
    example ("when does P resolve"). Neither carries a window, a grace period,
    or any coined magnitude.
    """

    # An unresolved prediction whose PROVIDED horizon ordinal lies behind the
    # furthest point logical time has reached. A comparison of two RECORDED
    # points on one clock - nothing else.
    OVERDUE_UNRESOLVED = "overdue_unresolved"
    # An unresolved prediction that records no horizon at all. The inquiry IS
    # the missing fact. Detected by `FieldState`, never by value.
    HORIZONLESS_COMMITMENT = "horizonless_commitment"


class CandidatePartition(str, Enum):
    """Which side of the scope guard a candidate fell on. Exhaustive at two."""

    LICENSED = "licensed"
    DRIFT = "drift"


class DriftBasis(str, Enum):
    """WHY a candidate is a finding rather than an inquiry. CLOSED at two.

    A drift finding is DURABLY RECORDED AND NEVER PURSUED. These are the only
    two ways v1 can fail to license, and each names a different bar: one is
    about SCOPE, the other about RECURSION.
    """

    # No ancestor goal linkage is derivable from the records. **The limiting
    # case of scope drift**: an inquiry nothing she has committed to can be
    # shown to subordinate to.
    NO_DERIVABLE_LICENSE = "no_derivable_license"
    # The source discrepancy traces to an obligation this generator authored -
    # an inquiry about an inquiry. The recursion door, closed the day the
    # recursion became possible rather than the day it became a problem.
    DEPTH_CEILING = "depth_ceiling"


class LicenseBasis(str, Enum):
    """WHICH recorded join licensed a candidate. Both read ids-only fields.

    Recorded beside the goal id so a reader learns not merely THAT the inquiry
    was subordinate but HOW that was established - Ruling 63's recorded-basis
    form, and the same reason the attention selection carries its deciding rung.
    """

    # `goal.originating_record_ids` names the prediction directly.
    ORIGINATING_RECORD = "originating_record"
    # `goal.justification_claim_ids` and `prediction.claim_refs` share a claim.
    JUSTIFICATION_CLAIM = "justification_claim"


@dataclass(frozen=True)
class InquiryCandidate:
    """ONE noticed discrepancy, PARTITIONED. Frozen; the generator's whole output.

    Carries its own provenance: the records it was derived FROM, the goal it
    subordinates TO (or the basis on which it could not), and the depth at
    which it was derived. A candidate that could not say where it came from
    would be exactly the unprovenanced question the heading forbids.
    """

    discrepancy_class: DiscrepancyClass
    # The records the discrepancy was observed ON. Ids only.
    source_record_ids: Tuple[str, ...]
    partition: CandidatePartition
    derivation_depth: int
    # LICENSED only. The ancestor goal and the join that established it.
    ancestor_goal_id: Optional[str] = None
    license_basis: Optional[LicenseBasis] = None
    # DRIFT only.
    drift_basis: Optional[DriftBasis] = None
    # Carried onto the record so DECLARED_NONE and ABSENT stay distinct facts
    # even where a class merges them (Docket H's cut, third surface).
    horizon_state: Optional[str] = None

    def __post_init__(self) -> None:
        if self.partition is CandidatePartition.LICENSED:
            if not self.ancestor_goal_id or self.license_basis is None:
                raise ValueError(
                    "a LICENSED inquiry cites an ancestor goal AND the join "
                    "that established it; a licence nobody can recompute is "
                    "not a licence.")
            if self.drift_basis is not None:
                raise ValueError(
                    "a LICENSED inquiry carries no drift basis - the partition "
                    "is exclusive, and a candidate on both sides is a record "
                    "that contradicts itself.")
        else:
            if self.drift_basis is None:
                raise ValueError(
                    "a DRIFT finding records WHY it drifted; a finding with no "
                    "basis is the silent drop this partition exists to "
                    "prevent.")
            if self.ancestor_goal_id is not None:
                raise ValueError(
                    "a DRIFT finding cites no ancestor goal - if one were "
                    "derivable it would not be drift.")


class InquiryGenerator:
    """`inquiry-generator.v1`. Deterministic, pure, and named in data."""

    def __init__(self, name: str = GENERATOR_NAME,
                 version: str = GENERATOR_VERSION):
        if name != GENERATOR_NAME or version != GENERATOR_VERSION:
            raise GeneratorIdentityMismatch(
                f"this module implements {GENERATOR_NAME!r} version "
                f"{GENERATOR_VERSION!r}; construction named {name!r} version "
                f"{version!r}.")
        self.name = GENERATOR_NAME
        self.version = GENERATOR_VERSION

    # -----------------------------------------------------------------
    # LICENSING - derived from records, never assumed, never synthesized
    # -----------------------------------------------------------------

    @staticmethod
    def _license(prediction: PredictionFacts,
                 goals: Tuple[GoalFacts, ...]
                 ) -> Optional[Tuple[str, LicenseBasis]]:
        """The ancestor goal for this prediction, or `None`.

        TWO JOINS, BOTH ON RECORDED IDS-ONLY FIELDS, both by EXACT STRING
        EQUALITY (Ruling 60's discipline - no normalization, no prefix grazing,
        no semantic matching, which would be inference wearing a record's
        clothes).

        DIRECT is preferred over VIA-CLAIM when both hold: naming the prediction
        itself is a stronger statement of subordination than sharing a claim
        with it. Ties inside a basis break by lowest goal id - deterministic,
        and never by content.

        **RETURNS `None` RATHER THAN INVENTING ANYTHING.** No maintenance goal
        is synthesized, no root is assumed, and no "closest" goal is guessed:
        the caller turns `None` into a NO_DERIVABLE_LICENSE finding, which is
        the ruled limiting case of scope drift.
        """
        direct = sorted(g.goal_id for g in goals
                        if prediction.prediction_id in g.originating_record_ids)
        if direct:
            return direct[0], LicenseBasis.ORIGINATING_RECORD
        refs = frozenset(prediction.claim_refs)
        via_claim = sorted(g.goal_id for g in goals
                           if refs & frozenset(g.justification_claim_ids))
        if via_claim:
            return via_claim[0], LicenseBasis.JUSTIFICATION_CLAIM
        return None

    # -----------------------------------------------------------------
    # DEPTH - a recorded fact, never a self-log read
    # -----------------------------------------------------------------

    @staticmethod
    def _depth(prediction: PredictionFacts, view: DerivedView) -> int:
        """1 for a kernel-native source; 2 when it traces to our own inquiry.

        **THE TRACE IS A RECORDED REFERENCE, AND THAT IS WHAT MAKES THIS
        HONEST.** A prediction committed while working an inquiry may cite that
        inquiry's obligation id among its recorded refs. If any such reference
        names a standing obligation whose `source` is THIS GENERATOR, then a
        discrepancy observed on that prediction is an inquiry about an inquiry.

        **THIS IS NOT DEDUPLICATION AND MUST NOT BECOME IT.** The question is
        never "have I already asked about this prediction" - that is the
        kernel's duplicate disposition, and answering it here would need a
        self-log read. The question is "did my own output produce the record I
        am now noticing a discrepancy on", which is a different relation and is
        answered entirely from the obligation ledger's own `source` field.
        """
        authored = {o.obligation_id for o in view.inquiry.obligations
                    if o.source == GENERATOR_NAME}
        return 2 if authored & frozenset(prediction.claim_refs) else 1

    # -----------------------------------------------------------------
    # GENERATION - pure, deterministic, order-stable
    # -----------------------------------------------------------------

    def generate(self, view: DerivedView) -> Tuple[InquiryCandidate, ...]:
        """Every candidate this observation supports, PARTITIONED. Pure.

        Deterministic and order-stable: predictions are walked in the substrate's
        own derivation order and the two classes are tested in declaration
        order, so an identical kernel yields an identical set AND an identical
        partition.
        """
        goals = view.inquiry.goals
        clock = view.inquiry.max_seq_ordinal
        out: List[InquiryCandidate] = []

        for prediction in view.inquiry.predictions:
            for discrepancy in self._classes_for(prediction, clock):
                out.append(self._partition(prediction, discrepancy, goals, view))
        return tuple(out)

    @staticmethod
    def _classes_for(prediction: PredictionFacts,
                     clock: int) -> Tuple[DiscrepancyClass, ...]:
        """Which discrepancies this prediction exhibits. Threshold-free.

        The two are MUTUALLY EXCLUSIVE by construction rather than by rule: a
        horizon that yields a comparable ordinal is PROVIDED, and a horizonless
        commitment has no ordinal to compare.
        """
        if prediction.horizon_ordinal is not None:
            # STRICT. A horizon standing exactly AT the furthest observed point
            # has been REACHED, not PASSED - and the repo's every scheduled
            # comparison (Rulings 34-A, 37, 43) fires on the step beyond, never
            # on the step itself.
            if prediction.horizon_ordinal < clock:
                return (DiscrepancyClass.OVERDUE_UNRESOLVED,)
            return ()
        if prediction.horizon_state != "provided":
            return (DiscrepancyClass.HORIZONLESS_COMMITMENT,)
        # A PROVIDED horizon whose recorded form yields no comparable ordinal.
        # **THIS CLASS YIELDS NOTHING, DELIBERATELY** - the prediction is not
        # horizonless (one was declared) and it cannot be shown overdue (nothing
        # comparable was recorded). Inventing a reading of the value here is
        # exactly what Ruling 61 res.5 refuses.
        return ()

    def _partition(self, prediction: PredictionFacts,
                   discrepancy: DiscrepancyClass,
                   goals: Tuple[GoalFacts, ...],
                   view: DerivedView) -> InquiryCandidate:
        """Licensed, or drift-with-a-basis. Total, exclusive, never a third thing.

        **DEPTH IS TESTED BEFORE LICENSING, and the precedence is deliberate.**
        A depth-2 candidate must not be pursued even when a licence IS
        derivable: the recursion bar is structural and the scope bar is
        contextual, so a candidate that fails the structural one never reaches
        the question of whose goal it would serve.
        """
        common = dict(
            discrepancy_class=discrepancy,
            source_record_ids=(prediction.prediction_id,),
            horizon_state=prediction.horizon_state,
        )
        depth = self._depth(prediction, view)
        if depth > MAX_DERIVATION_DEPTH:
            return InquiryCandidate(
                partition=CandidatePartition.DRIFT,
                derivation_depth=depth,
                drift_basis=DriftBasis.DEPTH_CEILING, **common)

        licence = self._license(prediction, goals)
        if licence is None:
            return InquiryCandidate(
                partition=CandidatePartition.DRIFT,
                derivation_depth=depth,
                drift_basis=DriftBasis.NO_DERIVABLE_LICENSE, **common)

        goal_id, basis = licence
        return InquiryCandidate(
            partition=CandidatePartition.LICENSED,
            derivation_depth=depth,
            ancestor_goal_id=goal_id,
            license_basis=basis, **common)
