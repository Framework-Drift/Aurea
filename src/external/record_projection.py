"""
record_projection.py - RULING 63 (Docket O item O5), CORRECTED BY RULING 64.

    A projection may not name itself after what it cannot see.

WHAT THIS PROJECTS, PLAINLY: RECORDS ABOUT CLAIMS AND PREDICTIONS.
NOT WORLD STATE.
-------------------------------------------------------------------
This module was called `world_state.py` for exactly one commit. It never held
world state and structurally cannot: `ClaimAncestryRecord` DELIBERATELY DOES
NOT STORE CLAIM CONTENT - it records WHERE a claim came from, never WHAT it
says - so a projection built from it can carry no propositions at all.

    A module named for what it structurally cannot represent is FALSE
    DOCUMENTATION IN THE STRONGEST POSITION A NAME CAN OCCUPY: every future
    reader trusts the identifier first and reads the docstring second.

THERE IS NO COMPATIBILITY SHIM AND NO ALIAS. The old name is GONE, because an
alias would preserve exactly the lie the rename exists to remove.

WHAT RULING 64 CORRECTED, AND WHY IT WAS INVISIBLE
----------------------------------------------------
Ruling 63's CODE was faithful to Ruling 63's CONTRACT. The contract never said
what a component's `detail` should carry, and the gap produced a surface that
REVERSED MEANING:

    WorldStateComponent(component_id='PRD-0001',
                        detail='The bridge will hold.',
                        annotation=TierAnnotation(tier=INFERRED, ...))

That is a FALSIFIED prediction. Its refuted expectation sat in an unlabeled
`detail` slot, tiered as something AUREA had INFERRED. A consumer reading
`detail` would have read a refuted claim as standing knowledge, and the tier
would have vouched for it.

Nothing consumed this module, so the correction is free NOW and would not have
been later. That is the whole reason it was made before a consumer existed.

THE THREE STRUCTURAL FIXES
----------------------------
  * A COMPONENT HAS NO `detail`. It carries the RECORDED FIELDS IT ACTUALLY
    HAS, each LABELED AS THE FIELD IT IS. An unlabeled slot is where meaning
    goes to be lost.
  * A CLAIM COMPONENT CARRIES NO PROPOSITION-SHAPED FIELD. The proposition is
    not in the record and may not be invented; an asserter's name in a detail
    slot is a proposition-shaped hole with a person's name in it.
  * A SETTLED PREDICTION CARRIES ITS OUTCOME POLARITY OR IT DOES NOT PROJECT.

THE CACHE IS REFUSED OUTRIGHT (Ruling 63 res.1, unchanged)
-----------------------------------------------------------
The corpus mentions world state ONCE - ELM (6a:868) ingests it as an INPUT
STREAM routed through CPA+SPL, and ELM is UNBUILT. World state is something
AUREA RECEIVES AND FILTERS, never something she KEEPS. Declaring staleness is a
DISCIPLINE; having no cache makes staleness STRUCTURALLY IMPOSSIBLE. No
module-level state, no instance cache, no memoization. AST-pinned.

IT OWNS NO STORE AND WRITES NOTHING. Inputs arrive as ALREADY-READ RECORDS; the
module never opens a file and imports neither ledger, only the record types.

THE COMPOSED SET IS CLOSED AND CHECKED, NOT DOCUMENTED. The O1 ancestry records
and the O3 commitments and resolutions, nothing else - a foreign type RAISES.
Doctrines, scars and topology are a FUTURE WIDENING RULING, because composing
them stops this being a view over external epistemics and makes it the
sovereign world-model the docket refused by name.

COINS NOTHING: no new tier member, no new vocabulary, no threshold.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from src.external.claim_ancestry import (ANCESTRY_FIELDS, ClaimAncestryRecord,
                                         OriginKind)
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

    TWO OF THE FOUR ARE STRUCTURALLY UNPRODUCIBLE TODAY, AND THAT IS NOT AN
    EMBARRASSMENT TO HIDE - IT IS THE HONEST CENSUS OF WHAT THIS ARCHITECTURE
    CAN CURRENTLY KNOW. Both members stay, because a closed vocabulary missing
    a registered member is the enum reopening later; neither may be emitted,
    and both bans are AST-pinned with their reopening conditions stated.
    """

    # ================================================================
    # UNPRODUCIBLE: AUREA HAS NO SENSOR SURFACE.
    #
    # ELM (6a:868-873) is canon's only sensor path and it is UNBUILT - there is
    # no `elm.py` in `src/`. Every record reaching this projection arrived
    # through a channel that ASSERTED, not a sensor that MEASURED, so emitting
    # OBSERVED would claim a kind of access AUREA does not have.
    #
    # REOPENING: a sensor path exists whose records are MEASUREMENTS rather
    # than assertions. Not "a source we trust more" - a different KIND of
    # access.
    # ================================================================
    OBSERVED = "observed"

    # A channel asserted it, and the record says WHICH KIND of channel.
    REPORTED = "reported"

    # ================================================================
    # UNPRODUCIBLE: AUREA HAS NO ADJUDICATION SURFACE, exactly as she has no
    # SENSOR surface. RULING 64 res.2.
    #
    # The tempting producer is a SETTLED PREDICTION - AUREA's own ledger
    # composed a commitment with a resolution, so it looks like something her
    # pipeline inferred. IT IS NOT. `PredictionLedger.resolve()` accepts a
    # CALLER-SUPPLIED outcome: the ledger evaluates no evidence, tests no
    # criterion mechanically, and the resolution record carries NO ADJUDICATION
    # PROVENANCE at all.
    #
    #     The COMPOSITION is AUREA's; the CONTENT is the caller's.
    #     COMPOSING IT IS NOT INFERRING IT.
    #
    # Labeling it INFERRED would upgrade "a caller recorded this outcome" into
    # "AUREA inferred this outcome" - the fabrication class, at the tier layer,
    # which is the layer a consumer trusts to tell it how much to trust the
    # rest.
    #
    # REOPENING: a resolution records WHO OR WHAT adjudicated it and against
    # WHICH criterion's evidence. THAT IS O4'S TERRITORY, refused-for-now in
    # Ruling 62 - so THE TWO REFUSALS INTERLOCK AND EACH NAMES THE OTHER. This
    # member becomes producible on the day O4 lands, and not before.
    # ================================================================
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


class ContradictoryResolutions(Exception):
    """Two resolutions for one prediction reached `project()`. RULING 64 res.5.

    `PredictionLedger.resolve()` REFUSES a second resolution - a commitment
    resolves once, and a re-score is a new prediction. But `project()` accepts
    arbitrary lists, so it must not SILENTLY WEAKEN that guarantee by keeping
    whichever resolution happened to come first.

    THE PROJECTION REPORTS WHAT THE RECORDS SAY AND REFUSES TO ADJUDICATE BY
    LIST ORDER. Choosing between two contradicting outcomes is an adjudication,
    and this module has no authority to perform one - which is the same reason
    `INFERRED` is unproducible.

    NOT in `STRUCTURAL_VIOLATIONS`: nothing in the pipeline calls this module
    (Ruling 63 res.7), so it is unreachable from `process_input` and membership
    would be a decision made on speculation. It is stated here instead, for the
    ruling that wires a consumer.
    """


@dataclass(frozen=True)
class TierAnnotation:
    """WHAT KIND OF KNOWING, AND THE RECORDED FACT THAT SAYS SO.

    RULING 45's move applied to a tier: the annotation CARRIES ITS OWN
    ARGUMENT. `basis_record` and `basis_field` name which field of which record
    produced the answer, so a reader can go and check rather than trust.

    `basis_field` IS ALWAYS A REAL FIELD OF A REAL RECORD TYPE - never prose,
    never an invented label. Pinned.

    `tier` IS `Optional` ON PURPOSE, AND THE `None` IS LOAD-BEARING TWICE OVER:
    a channel that declared nothing does not become REPORTED by default (that
    would be L3's fabrication class re-entering at the READ side after Ruling
    58 closed it at the WRITE side), and a settled prediction does not become
    anything at all, because no recorded fact determines what kind of knowing
    it is. NO FIFTH ENUM MEMBER IS COINED for the undetermined case.
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
class RecordComponent:
    """ONE part of the projection: LABELED RECORDED FIELDS, plus its tier.

    THERE IS NO `detail`, AND ITS ABSENCE IS THE FIX. Ruling 63 gave this class
    an unlabeled `detail` slot; a claim's went to the ASSERTER'S NAME and a
    prediction's to its EXPECTED RESULT - so a falsified prediction projected
    its refuted expectation as though it were a fact, with a tier vouching for
    it. AN UNLABELED SLOT IS WHERE MEANING GOES TO BE LOST.

    `fields` carries recorded values ONLY, each under the name of the field it
    came from. A reader who sees `expected_result` knows it is an EXPECTATION,
    because that is what the label says.

    DEEP-FROZEN AT CONSTRUCTION (Ruling 52), with the deepcopy: `deep_freeze`
    rebuilds the container SPINE, so a MUTABLE LEAF stays shared with whoever
    passed it in - and without the copy the projection would ALIAS its inputs,
    letting a caller edit a projection AFTER it was returned. That is a cache
    with extra steps, which is the thing res.1 refuses.
    """

    component_id: str
    fields: Mapping[str, Any]
    annotation: TierAnnotation

    def __post_init__(self) -> None:
        if not isinstance(self.annotation, TierAnnotation):
            raise TypeError(
                "RecordComponent.annotation must be a TierAnnotation - an "
                "un-annotated component would re-flatten the distinction this "
                "docket exists to preserve.")
        if not isinstance(self.fields, Mapping):
            raise TypeError(
                "RecordComponent.fields must be a Mapping of LABELED recorded "
                "fields. A bare value cannot say which field it came from, "
                "which is the defect Ruling 64 corrected.")
        object.__setattr__(self, "fields",
                           deep_freeze(copy.deepcopy(dict(self.fields))))


@dataclass(frozen=True)
class RecordProjection:
    """THE PROJECTION - a frozen value RETURNED, never a value KEPT.

    Claims and predictions are separate tuples rather than one list carrying a
    kind discriminator: THE STRUCTURE CARRIES THE DISTINCTION, so no
    component-kind enum has to be coined for it.

    THERE IS DELIBERATELY NO TALLY, NO COUNT AND NO SUMMARY FIELD. Counts of
    record are PERMITTED as tallies but not required, and a count PRESENTED BY
    THE PROJECTION is one short step from a count presented as a quality
    signal - at exactly the surface where that would feel natural and be false.
    """

    claims: Tuple[RecordComponent, ...]
    predictions: Tuple[RecordComponent, ...]

    def components(self) -> Tuple[RecordComponent, ...]:
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

    MODEL_PREDICTION -> PREDICTED, and it is also the check on O6: external
    world-model engines enter as `origin_kind=MODEL_PREDICTION` and land in the
    PREDICTED tier with NO NEW TIER MACHINERY.
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
        still a statement about an unsettled outcome.
      * RESOLVED CONFIRMED / FALSIFIED -> `None`.

    THE THIRD CASE IS A JUDGMENT CALL AND IT IS STATED, because Ruling 64 res.2
    removed the answer Ruling 63 gave without naming a replacement.

    A SETTLED PREDICTION HAS NO PRODUCIBLE TIER. It is not INFERRED - the
    outcome is caller-supplied with no adjudication provenance, and composing
    it is not inferring it (res.2). It is not REPORTED either, and that is the
    step worth stating: REPORTED is derived from a RECORDED `origin_kind`
    naming WHICH KIND of channel asserted something, and a resolution carries
    NO such field - so REPORTED would invent the attribution rather than read
    it. And it is no longer PREDICTED, because an outcome WAS recorded.

    So no recorded fact determines what kind of knowing this is, and `None` is
    what this module already says in that situation. `basis_field` still names
    `outcome`, so a reader sees WHERE the answer was sought and found absent.
    THE COMPONENT ITSELF STILL CARRIES THE FULL OUTCOME - the tier is undecided,
    the polarity is not (see `_prediction_fields`). THIS BECOMES PRODUCIBLE THE
    DAY O4 LANDS ADJUDICATION PROVENANCE - the same day `INFERRED` does, and by
    the same fact.
    """
    if resolution is None:
        return TierAnnotation(tier=KnowledgeTier.PREDICTED,
                              basis_record=commitment.prediction_id,
                              basis_field="expected_result")
    if resolution.outcome is PredictionOutcome.UNRESOLVED:
        return TierAnnotation(tier=KnowledgeTier.PREDICTED,
                              basis_record=commitment.prediction_id,
                              basis_field="outcome")
    return TierAnnotation(tier=None,
                          basis_record=commitment.prediction_id,
                          basis_field="outcome")


def _claim_fields(record: ClaimAncestryRecord) -> Dict[str, Any]:
    """The recorded fields a claim component carries. RULING 64 res.3.

    `origin_kind`, and the five ancestry fields' STATES - never their VALUES.

    THE STATES AND NOT THE VALUES, DELIBERATELY. `asserted_by`'s value is a
    person or an organisation; putting it on a component makes a
    proposition-shaped hole with a name in it, which is precisely the defect
    this ruling corrects. The STATE (`provided` / `declared_none` / `absent`)
    is the epistemically meaningful fact here - it says whether the channel
    ANSWERED - and it cannot be misread as the claim's substance.

    THE PROPOSITION IS SIMPLY NOT AVAILABLE, and that is by design elsewhere:
    `ClaimAncestryRecord` records WHERE a claim came from and never WHAT it
    says. A projection may not invent what its inputs deliberately omit.
    """
    fields: Dict[str, Any] = {"origin_kind": record.origin_kind.value}
    for name in ANCESTRY_FIELDS:
        fields[name] = getattr(record, name).state.value
    return fields


def _prediction_fields(commitment: PredictionCommitment,
                       resolution: Optional[PredictionResolution]
                       ) -> Dict[str, Any]:
    """The recorded fields a prediction component carries. RULING 64 res.4.

    A SETTLED COMPONENT CARRIES ITS OUTCOME POLARITY OR IT DOES NOT PROJECT.
    `expected_result` is present but LABELED AS AN EXPECTATION, and `outcome`
    sits beside it carrying what was actually recorded - so a FALSIFIED
    prediction projects that its expected result was recorded as NOT surviving
    its committed criterion, and NEVER projects that expectation as standing
    knowledge.

    `outcome` IS PRESENT AND `None` WHEN NOTHING WAS RECORDED, rather than
    absent from the mapping. A missing key reads as an oversight; an explicit
    `None` is this module's own established idiom for "no recorded fact
    determines this" (see `TierAnnotation.tier`), and it MARKS the component
    unresolved rather than leaving a reader to notice a gap.

    BOTH REFS: a settled component names BOTH records it was composed from; an
    unresolved one names the one that exists. `criterion` appears only when a
    resolution named one, because criteria are fixed at commit time and a
    criterion is only MET by an actual resolution (Ruling 61).
    """
    fields: Dict[str, Any] = {
        "expected_result": commitment.expected_result,
        "commitment_ref": commitment.prediction_id,
        "claim_refs": commitment.claim_refs,
    }
    if resolution is None:
        fields["outcome"] = None
        return fields
    fields["outcome"] = resolution.outcome.value
    fields["criterion"] = resolution.criterion
    fields["resolution_ref"] = resolution.prediction_id
    return fields


def _require(items: Sequence[Any], expected: type, label: str) -> None:
    """THE CLOSED COMPOSED SET, ENFORCED RATHER THAN DOCUMENTED (Ruling 63).

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


def _index_resolutions(resolutions: Sequence[PredictionResolution]
                       ) -> Dict[str, PredictionResolution]:
    """One resolution per prediction, or REFUSE. RULING 64 res.5.

    The previous form was `setdefault`, which kept whichever resolution came
    FIRST and dropped the other silently - so a CONFIRMED and a FALSIFIED
    record of the same prediction produced a projection asserting one of them,
    chosen by list order.
    """
    indexed: Dict[str, PredictionResolution] = {}
    for resolution in resolutions:
        existing = indexed.get(resolution.prediction_id)
        if existing is not None:
            raise ContradictoryResolutions(
                f"'{resolution.prediction_id}' was handed TWO resolutions: "
                f"{existing.outcome.value} against {existing.criterion}, and "
                f"{resolution.outcome.value} against {resolution.criterion}. "
                f"A commitment resolves ONCE (Ruling 61), and this projection "
                f"will not decide which of two contradicting records is the "
                f"real one by taking whichever came first in a list - that is "
                f"an adjudication, and this module has no authority to make "
                f"one.")
        indexed[resolution.prediction_id] = resolution
    return indexed


def project(ancestry: List[ClaimAncestryRecord],
            commitments: List[PredictionCommitment],
            resolutions: List[PredictionResolution]) -> RecordProjection:
    """Compose a projection over records. COMPUTED ON EVERY CALL.

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
    re-flatten exactly the distinction this docket preserves, and would do it
    invisibly, since a shorter list looks like a smaller world rather than a
    hidden one.
    """
    _require(ancestry, ClaimAncestryRecord, "ancestry")
    _require(commitments, PredictionCommitment, "commitments")
    _require(resolutions, PredictionResolution, "resolutions")

    by_prediction = _index_resolutions(resolutions)

    claims = tuple(
        RecordComponent(component_id=record.claim_id,
                        fields=_claim_fields(record),
                        annotation=_claim_tier(record))
        for record in ancestry)

    predictions = tuple(
        RecordComponent(
            component_id=commitment.prediction_id,
            fields=_prediction_fields(
                commitment, by_prediction.get(commitment.prediction_id)),
            annotation=_prediction_tier(
                commitment, by_prediction.get(commitment.prediction_id)))
        for commitment in commitments)

    return RecordProjection(claims=claims, predictions=predictions)
