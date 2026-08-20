"""M9-c: `discriminating-candidate-generator.v1` -- the premium source, mechanical.

Hundred-nineteenth entry (PATH v145), M9_GROUNDING.md section M9-c, on L6's own
words: *"CARRIED_CONTRADICTION -- a first-class, live, GENERATIVE state that
produces discriminating-prediction candidates."* Given a carried contradiction,
this module derives CANDIDATE discriminating predictions -- statements whose
operational resolution would separate the claims -- **from recorded structure
only. Derive or decline, never invent** (the M7-c licensing law, applied to
content): a candidate exists exactly where the records themselves yield both a
drafted criterion and the typed dependencies connecting it to its source, and
everything else is a DECLINED record with its basis -- surfaced, never silent,
never padded.

THE DERIVATION, EVERY EDGE A RECORDED FACT
-------------------------------------------------------------------------------
The census behind this shape (read from the tree, not assumed):

  * A SUSPENSION ENTRY -- the carried contradiction's durable set-down --
    carries ONE claim join: `claim_id`, populated by the Black Sphere pipeline
    door (Ruling 76) and honestly None everywhere else. Its `content` is a
    FREE STRING; deriving anything from it would be semantic inference, which
    the worldmodel's own v1 surface refused by construction and this module
    refuses for the same reason.
  * The TWO-SIDED conflict the grounding's "claims A and B" names is recorded
    in the WORLD MODEL: two live propositions in MUTUAL `contradicted_by`
    reference (each naming the other -- the record declaring a conflict, not a
    stance), each side carrying its own CLAIM references.
  * `world_proposition_standing` is a censused criterion surface (M9-a), and
    the standing derivation already reads PREDICTION outcomes into a
    proposition's standing -- so a criterion over the contradicted
    proposition's standing is exactly the surface a discriminating
    prediction's own resolution moves.

So the derivation is a pure join: the suspension's origin claim A -> a live
proposition P_A supported by A -> P_A's MUTUAL contradictor P_B -> P_B's
supporting claim B. Where every edge exists, the candidate drafts:

  * CRITERION (M9-a's exact shape, built by the SAME constructor the
    commitment door validates, so an uncommittable candidate is unwritable):
    surface `world_proposition_standing` over P_A, SUPPORTED confirms claim
    A's side, UNDERCUT resolves against it -- the two states separate the
    claims by the record's own semantics.
  * TYPED DEPENDENCIES (the ruled six; this module's stated mapping): the
    SUSPENSION carries the contradiction, so it is the prediction's SCOPE;
    claim A -- the claim whose collapse produced the carried state -- is the
    MAIN_CLAIM; the opposing claim B is the ASSUMPTION the discrimination
    tests; both propositions are OBSERVATION anchors, so a falsification's
    backward walk reaches every recorded party through kernel-resolvable
    targets.
  * LICENSE, DERIVED WHERE DERIVABLE: the M7-c justification-claim join,
    verbatim semantics -- a recorded goal whose `justification_claim_ids`
    intersect {A, B}. The originating-record join cannot predate the
    prediction it would name, so it becomes derivable only after commitment
    and is the committer's context, not this derivation's. No derivable join
    is the honest `no_derivable_license` -- and **a license-less candidate is
    still a candidate** (unlike M7-c's inquiries it obligates nothing and
    pursues nothing), but its commitment will require the committer to supply
    the license, and the record says so.

TWO MIRRORS, BOTH DRIFT-PINNED IN TESTS (the standing profile's third option):
the MUTUAL-contradiction rule is applied inline here because the worldmodel
surface's no-consumer census (`test_m6_worldmodel`) is byte-frozen and this
slice holds every prior pin file byte-unmodified -- the test file compares
this module's pair derivation against `detect_inconsistencies` over the same
summaries every run. The license-basis vocabulary mirrors M7-c's values for
the same reason.

PURE: no store, no path, no `open`, no clock, no randomness. Inputs are
ALREADY-READ records (the O5 / standing-profile shape); the recording act is
the loop's; **the generator NEVER commits -- the path does not exist here.**
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

# RECORD TYPES ONLY -- Ruling 61's own migration rules this import class:
# "importing a record type is not consuming the store." The constructors ARE
# the point: a candidate's draft is valid by the commitment door's own law.
from src.external.prediction_ledger import (DependencyKind,
                                            OperationalCriterion,
                                            TypedDependency)

__all__ = [
    "GENERATOR_NAME", "GENERATOR_VERSION", "REGISTRATION",
    "CandidateLicenseBasis", "DeclineBasis", "DraftedLicense",
    "CandidatePrediction", "DeclinedContradiction", "CandidateDerivation",
    "CandidateGenerator",
]

GENERATOR_NAME = "discriminating-candidate-generator.v1"
GENERATOR_VERSION = "1"


class CandidateLicenseBasis(str, Enum):
    """HOW a candidate's licensing goal was derived, or why none could be.

    `JUSTIFICATION_CLAIM` mirrors `inquiry_generator.LicenseBasis`'s value and
    `NO_DERIVABLE_LICENSE` mirrors `DriftBasis`'s -- values identical, pinned
    equal in tests, never imported (the mirror discipline; see the module
    docstring). One vocabulary of license facts, two purity boundaries.
    """

    JUSTIFICATION_CLAIM = "justification_claim"
    NO_DERIVABLE_LICENSE = "no_derivable_license"


class DeclineBasis(str, Enum):
    """WHY a carried contradiction yielded no candidate. CLOSED, each member a
    missing RECORDED edge -- never a judgment about content."""

    #: The suspension records no claim join (`claim_id` is None -- the honest
    #: state for every entry the pipeline door did not populate).
    NO_CLAIM_JOIN = "no_claim_join"
    #: The origin claim reaches no live proposition's `supported_by`.
    CLAIM_REACHES_NO_LIVE_PROPOSITION = "claim_reaches_no_live_proposition"
    #: No live proposition supported by the claim stands in MUTUAL
    #: contradiction with another live proposition.
    NO_RECORDED_MUTUAL_CONTRADICTION = "no_recorded_mutual_contradiction"
    #: The opposing proposition records no supporting claim of its own.
    OPPOSING_SIDE_RECORDS_NO_CLAIM = "opposing_side_records_no_claim"
    #: Both sides resolve to ONE claim -- nothing to separate.
    BOTH_SIDES_ARE_ONE_CLAIM = "both_sides_are_one_claim"


REGISTRATION: Mapping[str, Any] = MappingProxyType({
    "identity": GENERATOR_NAME,
    "version": GENERATOR_VERSION,
    "kind": "deterministic_non_model_instrument",
    "contract": "registration",
    "declared_invariants": (
        "derive-or-decline: a candidate exists only where recorded structure "
        "yields both a drafted criterion and its typed dependencies; every "
        "other contradiction yields a DECLINED record with its basis",
        "deterministic: same records yield same candidates, same declines, "
        "same bases, in the same order",
        "valid-by-construction: drafted criteria and dependencies are built "
        "through the commitment door's own constructors",
        "pure: no store, clock, io or randomness is reachable; inputs are "
        "already-read records",
        "never commits: no path from this module reaches any ledger write",
    ),
})


@dataclass(frozen=True)
class DraftedLicense:
    """The licensing-goal derivation, or the honest absence of one."""

    basis: CandidateLicenseBasis
    goal_id: Optional[str] = None
    #: The claim the goal's `justification_claim_ids` shares, where derived.
    via_claim: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {"basis": self.basis.value, "goal_id": self.goal_id,
                "via_claim": self.via_claim}


@dataclass(frozen=True)
class CandidatePrediction:
    """ONE derivable discriminating prediction, with full provenance."""

    suspension_id: str
    claim_a: str
    claim_b: str
    proposition_a: str
    proposition_b: str
    #: The drafted expected result -- a deterministic function of the ids,
    #: never composed prose (the loop's `_claim_text` rule).
    statement: str
    criterion: OperationalCriterion
    typed_dependencies: Tuple[TypedDependency, ...]
    license: DraftedLicense
    generator_name: str = GENERATOR_NAME
    generator_version: str = GENERATOR_VERSION

    def __post_init__(self) -> None:
        # AN UNCOMMITTABLE CANDIDATE IS UNWRITABLE: the draft is valid by the
        # commitment door's OWN constructors, or it is not a candidate. A raw
        # dict here would be a draft that skipped the censused-surface and
        # censused-form validation and surfaced anyway -- stored hope with a
        # generator's name on it.
        if not isinstance(self.criterion, OperationalCriterion):
            raise TypeError(
                f"CandidatePrediction.criterion carries "
                f"{type(self.criterion).__name__}, not an "
                f"OperationalCriterion built by the commitment door's "
                f"constructor.")
        for dependency in self.typed_dependencies:
            if not isinstance(dependency, TypedDependency):
                raise TypeError(
                    f"typed_dependencies carries "
                    f"{type(dependency).__name__}, not a TypedDependency "
                    f"built by the commitment door's constructor.")
        if not isinstance(self.license, DraftedLicense):
            raise TypeError(
                f"CandidatePrediction.license carries "
                f"{type(self.license).__name__}, not a DraftedLicense.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "suspension_id": self.suspension_id,
            "claim_refs": [self.claim_a, self.claim_b],
            "proposition_a": self.proposition_a,
            "proposition_b": self.proposition_b,
            "statement": self.statement,
            "criterion": self.criterion.as_dict(),
            "typed_dependencies": [d.as_dict()
                                   for d in self.typed_dependencies],
            "license": self.license.as_dict(),
            "generator_name": self.generator_name,
            "generator_version": self.generator_version,
        }


@dataclass(frozen=True)
class DeclinedContradiction:
    """ONE carried contradiction that yielded no candidate, and why."""

    suspension_id: str
    basis: DeclineBasis
    detail: str
    generator_name: str = GENERATOR_NAME
    generator_version: str = GENERATOR_VERSION

    def as_dict(self) -> Dict[str, Any]:
        return {
            "suspension_id": self.suspension_id,
            "basis": self.basis.value,
            "detail": self.detail,
            "generator_name": self.generator_name,
            "generator_version": self.generator_version,
        }


@dataclass(frozen=True)
class CandidateDerivation:
    """The whole derivation over one kernel reading. The generator's output."""

    candidates: Tuple[CandidatePrediction, ...] = ()
    declined: Tuple[DeclinedContradiction, ...] = ()


def _ref_ids(refs: Sequence[Any], kind_value: str) -> Tuple[str, ...]:
    """The record_ids of the refs of one kind, sorted for determinism."""
    out = []
    for ref in refs or ():
        kind = getattr(getattr(ref, "kind", None), "value", None)
        if kind == kind_value:
            out.append(str(ref.record_id))
    return tuple(sorted(out))


class CandidateGenerator:
    """The derivation. Holds nothing, reads nothing, writes nothing."""

    def derive(self,
               suspension_entries: Sequence[Any],
               proposition_summaries: Sequence[Any],
               goal_commitments: Sequence[Any] = (),
               ) -> CandidateDerivation:
        """Derive candidates and declines over ALREADY-READ records.

        `suspension_entries`: suspension records (duck: `.id`, `.claim_id`).
        `proposition_summaries`: the proposition ledger's own content-free
        summaries (`live_summaries()`), so this derivation is STRUCTURALLY
        incapable of semantic inference -- the M6 surface's own boundary.
        `goal_commitments`: the goal ledger's commitments, for the license
        join. Iteration orders are sorted throughout; the derivation is a
        function of the records alone.
        """
        summaries = {str(s.wmp_id): s for s in proposition_summaries}
        mutual_pairs = self._mutual_pairs(summaries)

        candidates: List[CandidatePrediction] = []
        declined: List[DeclinedContradiction] = []
        for entry in sorted(suspension_entries,
                            key=lambda e: str(getattr(e, "id", ""))):
            suspension_id = str(getattr(entry, "id", ""))
            claim_a = getattr(entry, "claim_id", None)
            if not claim_a:
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.NO_CLAIM_JOIN,
                    detail=("the suspension records no claim join; `claim_id` "
                            "is populated by the pipeline door and honestly "
                            "None everywhere else (Ruling 76) -- there is no "
                            "recorded claim A to discriminate for")))
                continue
            claim_a = str(claim_a)

            anchored = tuple(sorted(
                wmp_id for wmp_id, summary in summaries.items()
                if claim_a in _ref_ids(summary.supported_by, "claim")))
            if not anchored:
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.CLAIM_REACHES_NO_LIVE_PROPOSITION,
                    detail=(f"claim {claim_a} supports no live world "
                            f"proposition; a criterion needs a censused "
                            f"surface, and no record carries this claim onto "
                            f"one")))
                continue

            derived_here = False
            opposing_seen = False
            opposing_claimless: List[str] = []
            one_claim_pairs: List[str] = []
            for proposition_a in anchored:
                for proposition_b in mutual_pairs.get(proposition_a, ()):
                    opposing_seen = True
                    b_claims = _ref_ids(
                        summaries[proposition_b].supported_by, "claim")
                    if not b_claims:
                        opposing_claimless.append(proposition_b)
                        continue
                    claim_b = b_claims[0]  # sorted-first: a stated,
                    # deterministic selection among RECORDED facts, never an
                    # invention beyond them.
                    if claim_b == claim_a:
                        one_claim_pairs.append(proposition_b)
                        continue
                    candidates.append(self._draft(
                        suspension_id, claim_a, claim_b,
                        proposition_a, proposition_b, goal_commitments))
                    derived_here = True
            if derived_here:
                continue
            if opposing_claimless:
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.OPPOSING_SIDE_RECORDS_NO_CLAIM,
                    detail=(f"the mutual contradictor(s) "
                            f"{sorted(set(opposing_claimless))} record no "
                            f"supporting claim; there is no recorded claim B "
                            f"to separate from {claim_a}")))
            elif one_claim_pairs:
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.BOTH_SIDES_ARE_ONE_CLAIM,
                    detail=(f"both sides of the recorded contradiction "
                            f"resolve to {claim_a}; a discriminating "
                            f"prediction separates two claims, and the "
                            f"record holds one")))
            elif opposing_seen:
                # unreachable by construction today; kept for totality
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.NO_RECORDED_MUTUAL_CONTRADICTION,
                    detail="no derivable pairing survived the recorded edges"))
            else:
                declined.append(DeclinedContradiction(
                    suspension_id=suspension_id,
                    basis=DeclineBasis.NO_RECORDED_MUTUAL_CONTRADICTION,
                    detail=(f"no live proposition supported by {claim_a} "
                            f"stands in MUTUAL contradiction with another; "
                            f"a one-way citation is a stance, not a recorded "
                            f"conflict (the M6 surface's own rule)")))
        return CandidateDerivation(candidates=tuple(candidates),
                                   declined=tuple(declined))

    @staticmethod
    def _mutual_pairs(summaries: Mapping[str, Any]) -> Dict[str, Tuple[str, ...]]:
        """MUTUAL contradiction only -- each names the other, both live.

        A MIRROR of `contradiction_surface.detect_inconsistencies`' rule (its
        no-consumer census is byte-frozen), pinned equivalent in tests over
        the same summaries every run. Like the ruled surface, it matches on
        `record_id` alone regardless of the reference's declared kind --
        `KernelRefKind` cannot name a proposition, so the tree's own
        harnesses carry proposition-to-proposition citations under a shim
        kind, and the id-membership test against the LIVE set is the ruled
        reading.
        """
        contradicts = {
            wmp_id: {str(r.record_id) for r in (s.contradicted_by or ())}
            for wmp_id, s in summaries.items()}
        pairs: Dict[str, List[str]] = {}
        for wmp_id, targets in contradicts.items():
            for other in sorted(targets):
                if other in summaries and wmp_id in contradicts.get(other, ()):
                    pairs.setdefault(wmp_id, []).append(other)
        return {k: tuple(sorted(v)) for k, v in pairs.items()}

    @staticmethod
    def _draft(suspension_id: str, claim_a: str, claim_b: str,
               proposition_a: str, proposition_b: str,
               goal_commitments: Sequence[Any]) -> CandidatePrediction:
        """One candidate, drafted through the commitment door's constructors."""
        criterion = OperationalCriterion(
            surface="world_proposition_standing",
            record_id=proposition_a,
            confirmed_state="supported",
            failed_state="undercut")
        dependencies = (
            TypedDependency(kind=DependencyKind.SCOPE,
                            record_form="suspension",
                            record_id=suspension_id),
            TypedDependency(kind=DependencyKind.MAIN_CLAIM,
                            record_form="claim", record_id=claim_a),
            TypedDependency(kind=DependencyKind.ASSUMPTION,
                            record_form="claim", record_id=claim_b),
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="world_proposition",
                            record_id=proposition_a),
            TypedDependency(kind=DependencyKind.OBSERVATION,
                            record_form="world_proposition",
                            record_id=proposition_b),
        )
        license_draft = DraftedLicense(
            basis=CandidateLicenseBasis.NO_DERIVABLE_LICENSE)
        for goal in sorted(goal_commitments,
                           key=lambda g: str(getattr(g, "goal_id", ""))):
            justified = {str(c) for c in
                         getattr(goal, "justification_claim_ids", ()) or ()}
            shared = sorted(justified & {claim_a, claim_b})
            if shared:
                license_draft = DraftedLicense(
                    basis=CandidateLicenseBasis.JUSTIFICATION_CLAIM,
                    goal_id=str(goal.goal_id), via_claim=shared[0])
                break
        return CandidatePrediction(
            suspension_id=suspension_id,
            claim_a=claim_a, claim_b=claim_b,
            proposition_a=proposition_a, proposition_b=proposition_b,
            statement=(f"the standing of {proposition_a} under {claim_a} "
                       f"survives its recorded contradiction with "
                       f"{proposition_b} under {claim_b}"),
            criterion=criterion,
            typed_dependencies=dependencies,
            license=license_draft)
