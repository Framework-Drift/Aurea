"""
world_state.py - RULING 63 / DOCKET O item O5: THE WORLD-STATE PROJECTION.

    The projection is COMPUTED, never KEPT,
    and it says what KIND of knowing each part of it is.

THE GROUNDING FINDING, AND IT DECIDES THE WHOLE MODULE
-------------------------------------------------------
The corpus was swept for a world-model organ and it has EXACTLY ONE HIT: ELM
(6a:868-873) ingests "sensor data, user behavior, world state" as an INPUT
STREAM routed through CPA+SPL for collapse filtration. World state is something
AUREA RECEIVES AND FILTERS - never something she KEEPS.

    A projection that persisted would be the first stored world-model in the
    architecture, invented here, at the layer whose whole job is to refuse
    exactly that. Canon's silence is not an omission to fill; it is the
    argument.

THE CACHE IS REFUSED OUTRIGHT
------------------------------
The registration offered "compute-on-read OR staleness-DECLARED". This module
takes compute-on-read and REFUSES the cached alternative entirely, on the
registration's own reason: A CACHED PROJECTION IS A STALE AUTHORITY WAITING FOR
A TRUSTING READER.

Declaring staleness is a DISCIPLINE. Having no cache makes staleness
STRUCTURALLY IMPOSSIBLE - there is no stored projection to go stale, so the
honest path is the only executable one. This module holds NO module-level
state, NO instance cache, NO memoization, and no `functools.lru_cache`. The
projection is a frozen value RETURNED, never a value KEPT. AST-pinned, and a
memoizing mutant must fail - that pin is what makes this resolution real rather
than stated.

IT OWNS NO STORE AND WRITES NOTHING
-------------------------------------
Not in `STORE_OWNERS` (it stores nothing). No `open`, no write handle, no path
attribute anywhere. ITS INPUTS ARRIVE AS ALREADY-READ RECORDS passed in by the
caller - O2's shape, for O2's reason: A MODULE THAT OPENS FILES IS A MODULE
THAT CAN BE MADE TO WRITE ONE.

THE COMPOSED SET IS EXPLICIT, CLOSED, AND MINIMAL
---------------------------------------------------
The O1 ancestry records and the O3 commitments and resolutions. NOTHING ELSE.
Codex doctrines, scars, topology and suspension contents are DECLARED OUT and
their inclusion is a FUTURE WIDENING RULING - because a projection that
composes the doctrine spine and the scar store stops being a view over external
epistemics and becomes THE SOVEREIGN WORLD-MODEL THE DOCKET REFUSED BY NAME.
The capability boundary is preserved HERE, at the input list, where it is
checkable - and it is CHECKED, not documented: a foreign record type raises.

NO NUMBERS ANYWHERE
---------------------
No confidence, no completeness percentage, no coverage ratio, no component
count presented as a quality signal. A projection is exactly where a summary
number would feel natural and be false.

COINS NOTHING: four tier members verbatim from the registration, the input
shape is O2's, and no threshold, weight, magnitude or duration exists here.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Sequence, Tuple

from src.external.claim_ancestry import ClaimAncestryRecord, OriginKind
# THE LEDGERS ARE DELIBERATELY NOT IMPORTED - only the RECORD types. Inputs
# arrive already-read; this module never reaches a store. AST-pinned.
from src.external.prediction_ledger import (PredictionCommitment,
                                            PredictionOutcome,
                                            PredictionResolution)
from src.utils.deep_freeze import deep_freeze


# =====================================================================
# THE VOCABULARY
# =====================================================================

class KnowledgeTier(str, Enum):
    """WHAT KIND OF KNOWING a component of the projection is.

    CLOSED, four members, RECOVERED VERBATIM from the docket's registration.
    Additions require a manifest ruling (Ruling 7's discipline).
    """

    # ================================================================
    # STRUCTURALLY UNPRODUCIBLE TODAY, AND THAT IS RECORDED RATHER THAN
    # WORKED AROUND (Ruling 50's SOFTENED precedent, exactly).
    #
    # AUREA OBSERVES NOTHING. ELM (6a:868-873) is canon's only sensor path and
    # it is UNBUILT - there is no `elm.py` in `src/`. Every record reaching this
    # projection arrived through a channel that ASSERTED, not a sensor that
    # MEASURED, so emitting OBSERVED would be the projection claiming a kind of
    # access AUREA does not have.
    #
    # THE MEMBER STAYS because the registration names it: a closed vocabulary
    # missing a registered member is the enum reopening later. NO CODE PATH MAY
    # EMIT IT, and that is AST-pinned.
    #
    # REOPENING CONDITION: a sensor path exists whose records are MEASUREMENTS
    # rather than assertions. Not "a source we trust more" - a different KIND of
    # access.
    # ================================================================
    OBSERVED = "observed"

    # A channel asserted it. The overwhelming majority of what AUREA holds.
    REPORTED = "reported"

    # AUREA's own machinery produced it from other components.
    INFERRED = "inferred"

    # A statement about an outcome not yet recorded, or recorded as unsettled.
    PREDICTED = "predicted"


# The four source classes that mean "a channel asserted this". `UNDECLARED` is
# deliberately absent - see `_claim_tier`.
_REPORTING_ORIGINS = frozenset({
    OriginKind.HUMAN,
    OriginKind.EXTERNAL_AI,
    OriginKind.SYSTEM_PLUGIN,
    OriginKind.LLM_WRAPPER,
})


@dataclass(frozen=True)
class TierAnnotation:
    """WHAT KIND OF KNOWING, AND THE RECORDED FACT THAT SAYS SO.

    RULING 45's move applied to a tier: the annotation CARRIES ITS OWN
    ARGUMENT. `basis_record` and `basis_field` name which field of which record
    produced the answer, so a reader can go and check rather than trust.

    `basis_field` IS ALWAYS A REAL FIELD OF A REAL RECORD TYPE - never prose,
    never an invented label. Pinned.

    `tier` IS `Optional` ON PURPOSE, AND THE `None` IS THE WHOLE POINT. A
    channel that declared nothing does not become REPORTED by default - that
    would be L3's fabrication class re-entering at the READ side, after Ruling
    58 spent an entire ruling closing it at the WRITE side. NO FIFTH ENUM
    MEMBER IS COINED for the undetermined case: `Optional` plus a stated basis
    carries it, and the registered vocabulary stays exactly four.
    """

    tier: Optional[KnowledgeTier]
    basis_record: str
    basis_field: str

    def __post_init__(self) -> None:
        if self.tier is not None and not isinstance(self.tier, KnowledgeTier):
            raise TypeError(
                f"TierAnnotation.tier must be a KnowledgeTier or None, got "
                f"{type(self.tier).__name__}. A raw string would let a caller "
                f"invent a tier the enum deliberately closes.")


@dataclass(frozen=True)
class WorldStateComponent:
    """ONE part of the projected world state, with its tier annotation.

    DEEP-FROZEN AT CONSTRUCTION (Ruling 52). `detail` carries a value copied
    out of an input record, and WITHOUT THE DEEPCOPY IT WOULD ALIAS THAT
    RECORD'S OWN MUTABLE LEAF - so a caller still holding the input could edit
    a projection AFTER it was returned. A projection that can be edited after
    the fact is a cache with extra steps, which is the thing res.1 refuses.
    """

    component_id: str
    detail: Any
    annotation: TierAnnotation

    def __post_init__(self) -> None:
        if not isinstance(self.annotation, TierAnnotation):
            raise TypeError(
                "WorldStateComponent.annotation must be a TierAnnotation - an "
                "un-annotated component would re-flatten the distinction this "
                "docket exists to preserve.")
        # THE COPY IS THE POINT (Ruling 52). `deep_freeze` rebuilds the
        # container SPINE, so a MUTABLE LEAF - a `bytearray`, say - is returned
        # untouched and stays shared with whoever passed it in. That gap has
        # been found by a surviving mutant three times; here it is copied first
        # and pinned with a bytearray leaf.
        object.__setattr__(self, "detail",
                           deep_freeze(copy.deepcopy(self.detail)))


@dataclass(frozen=True)
class WorldStateProjection:
    """THE PROJECTION - a frozen value RETURNED, never a value KEPT.

    Claims and predictions are separate tuples rather than one list carrying a
    kind discriminator: THE STRUCTURE CARRIES THE DISTINCTION, so no component-
    kind enum has to be coined for it.

    THERE IS DELIBERATELY NO TALLY, NO COUNT AND NO SUMMARY FIELD. Counts of
    record are PERMITTED as tallies (res.6) but not required, and a count
    PRESENTED BY THE PROJECTION is one short step from a count presented as a
    quality signal - at exactly the surface where that would feel natural and
    be false. A caller who wants to count these tuples can count them, and the
    counting is then visibly theirs.
    """

    claims: Tuple[WorldStateComponent, ...]
    predictions: Tuple[WorldStateComponent, ...]

    def components(self) -> Tuple[WorldStateComponent, ...]:
        """Every component, claims first. A read over a returned value."""
        return self.claims + self.predictions


# =====================================================================
# THE DERIVATION - entirely over recorded facts
# =====================================================================

def _claim_tier(record: ClaimAncestryRecord) -> TierAnnotation:
    """The tier of a claim, from its RECORDED `origin_kind` and nothing else.

    UNDECLARED YIELDS `None`, NOT REPORTED, and this is the line the whole
    ruling turns on. Ruling 58 exists because `process_input` defaulted a
    missing origin to `"user"` and wrote a human origin into a durable store
    for every claim the system had ever processed. Defaulting UNDECLARED to
    REPORTED here would commit the identical fabrication one layer later, on
    the read side, where nothing durable records it and nothing catches it.

    MODEL_PREDICTION -> PREDICTED is res.5, and it is also the check on O6:
    external world-model engines enter as `origin_kind=MODEL_PREDICTION` and
    land in the PREDICTED tier with NO NEW TIER MACHINERY.
    """
    if record.origin_kind in _REPORTING_ORIGINS:
        tier = KnowledgeTier.REPORTED
    elif record.origin_kind is OriginKind.MODEL_PREDICTION:
        tier = KnowledgeTier.PREDICTED
    else:
        # UNDECLARED. Nobody said, so this projection does not say either.
        tier = None
    return TierAnnotation(tier=tier,
                          basis_record=record.claim_id,
                          basis_field="origin_kind")


def _prediction_tier(commitment: PredictionCommitment,
                     resolution: Optional[PredictionResolution]
                     ) -> TierAnnotation:
    """The tier of a prediction, from its commitment and its resolution.

    THREE RECORDED CASES:

      * NO RESOLUTION LINE -> PREDICTED, on `expected_result` - the field that
        IS the prediction, a statement about an outcome not yet recorded.
      * RESOLVED `UNRESOLVED` -> PREDICTED, on the resolution's `outcome`. The
        question was reached and could not be settled, so what AUREA holds is
        still a statement about an unsettled outcome. Res.5 names this case
        explicitly and puts it with the unresolved one.
      * RESOLVED CONFIRMED / FALSIFIED -> INFERRED, on the resolution's
        `outcome`.

    THE THIRD CASE IS A JUDGMENT CALL AND IS STATED. Res.5 names the tier rule
    as "a component AUREA's own pipeline produced from other components ->
    INFERRED" without naming its producer, and this composition has exactly one
    such producer: a settled prediction is not a claim about the future and was
    not asserted by any channel - it is a fact AUREA's OWN LEDGER produced by
    composing a commitment with a resolution. Two records of hers, one
    component.

    THE ALTERNATIVE WAS REFUSED FOR A STATED REASON: calling it REPORTED would
    attribute it to a channel, and a resolution carries NO `origin_kind` - the
    attribution would be invented. Leaving it `None` would be honest but wrong:
    the basis IS on record, in two records this projection was handed.
    """
    if resolution is None:
        return TierAnnotation(tier=KnowledgeTier.PREDICTED,
                              basis_record=commitment.prediction_id,
                              basis_field="expected_result")
    if resolution.outcome is PredictionOutcome.UNRESOLVED:
        return TierAnnotation(tier=KnowledgeTier.PREDICTED,
                              basis_record=commitment.prediction_id,
                              basis_field="outcome")
    return TierAnnotation(tier=KnowledgeTier.INFERRED,
                          basis_record=commitment.prediction_id,
                          basis_field="outcome")


def _require(items: Sequence[Any], expected: type, label: str) -> None:
    """THE CLOSED COMPOSED SET, ENFORCED RATHER THAN DOCUMENTED (res.3).

    Widening the projection to doctrines, scars or topology is a FUTURE RULING,
    and the boundary is checkable exactly here - at the input list. A foreign
    record type raises, so widening is a DELIBERATE EDIT rather than something
    that happens because a caller passed something new and nothing objected.
    """
    for item in items:
        if not isinstance(item, expected):
            raise TypeError(
                f"{label} must contain only {expected.__name__}, got "
                f"{type(item).__name__}. The composed set is CLOSED to the O1 "
                f"ancestry records and the O3 commitments and resolutions "
                f"(Ruling 63 res.3): composing the doctrine spine or the scar "
                f"store would make this the sovereign world-model the docket "
                f"refused by name. Widening it is a ruling.")


def project(ancestry: List[ClaimAncestryRecord],
            commitments: List[PredictionCommitment],
            resolutions: List[PredictionResolution]) -> WorldStateProjection:
    """Compose a world-state projection. COMPUTED ON EVERY CALL.

    NOTHING IS CACHED, MEMOIZED OR CARRIED BETWEEN CALLS. Every invocation
    reads its arguments and builds a fresh frozen value; two calls with
    different inputs return different projections, and two calls with the same
    inputs return equal - but distinct - ones. There is no stored projection
    to go stale.

    INPUTS ARE ALREADY-READ RECORDS. The caller reads the ledgers
    (`ClaimAncestryLedger.read_all()`, `PredictionLedger.commitments()` /
    `.resolutions()`); this module never opens a file.

    EVERY COMPONENT CARRIES A TIER ANNOTATION - including the ones whose tier
    is `None`. An un-annotated component is not permitted, and a `None` tier is
    RENDERED rather than dropped: silently omitting the undetermined case would
    re-flatten exactly the distinction this docket preserves.
    """
    _require(ancestry, ClaimAncestryRecord, "ancestry")
    _require(commitments, PredictionCommitment, "commitments")
    _require(resolutions, PredictionResolution, "resolutions")

    # First resolution per prediction wins. The ledger refuses a second one at
    # the write (Ruling 61), so a duplicate here means a hand-built input; the
    # projection reports the FIRST recorded outcome rather than choosing.
    by_prediction = {}
    for resolution in resolutions:
        by_prediction.setdefault(resolution.prediction_id, resolution)

    claims = tuple(
        WorldStateComponent(
            component_id=record.claim_id,
            detail=record.asserted_by.value,
            annotation=_claim_tier(record))
        for record in ancestry)

    predictions = tuple(
        WorldStateComponent(
            component_id=commitment.prediction_id,
            detail=commitment.expected_result,
            annotation=_prediction_tier(
                commitment, by_prediction.get(commitment.prediction_id)))
        for commitment in commitments)

    return WorldStateProjection(claims=claims, predictions=predictions)
