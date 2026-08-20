"""
prediction_ledger.py - RULING 61 / DOCKET O item O3: THE PREDICTION LEDGER.

    A prediction that was not committed before its outcome is not a prediction.

Canon: Docket O's registration - "committed BEFORE outcome with expected
result, applicable conditions, resolution horizon, and success/failure/
unresolved criteria FIXED AT COMMIT TIME... the mechanism that turns a
truth-seeking POSTURE into a recorded truth-seeking HISTORY."

THE PRINCIPLE
--------------
Without prior commitment a prediction is REWRITABLE until everything appears
successful. So this ledger's entire job is to make the commitment UNREWRITABLE
and the scoring MECHANICAL against criteria that already existed:

    the commitment is frozen at commit time,
    the resolution is a SEPARATE APPEND,
    and nothing here promotes anything.

The ledger reads as a HISTORY - what was expected, then what was recorded -
rather than as a STATE, which is what "what we now say we expected" would be.

L2 GOVERNS THIS WHOLE MODULE, AND IT IS PINNED STRUCTURALLY, NOT PROMISED
--------------------------------------------------------------------------
    "Prediction is a pressure source, never a promotion source. A scored-false
     prediction applies collapse pressure to the exact dependency chain that
     produced it - observation, causal link, auxiliary assumption, horizon,
     domain validity, or the claim itself. Predictive success preserves
     viability and updates instrument history; it PROMOTES NOTHING. Utility is
     not ontology."

And the Lexicon's core maxim (:608), which is why prediction FEEDS collapse and
never substitutes for it:

    "Truth is not what survives prediction; it is what survives collapse."

So: this module imports no doctrine writer, no Codex handle, no scar mint and
no pressure surface. A CONFIRMED prediction updates NOTHING but the record. An
AST pin asserts the import set, because a promise in a docstring is exactly the
thing this codebase has learned not to rely on.

THE O3/O4 BOUNDARY (ruled explicitly - the registration could be read two ways)
-------------------------------------------------------------------------------
O3 owns the RECORDING of the outcome; O4 owns its CONSEQUENCE. A commitment
ledger that cannot record what happened is a ledger of INTENTIONS. So this file
records that a prediction was FALSIFIED against criterion X, and O4 - which is
FCT-gated - decides what collapses because of it.

WHAT IS DELIBERATELY NOT HERE, each with its owner
----------------------------------------------------
  * DEPENDENCY-ROUTED PRESSURE and the minimal-unsat-core operation - O4,
    FCT-gated. This module RECORDS a dependency chain and routes nothing.
  * WORLD-STATE PROJECTION over these records - O5.
  * ANY INSTRUMENT TRACK RECORD, ACCURACY RATE, OR CALIBRATION SCORE - REFUSED
    HERE AND STANDING. These are the numeric trust scores the docket refused.
    They are legitimate LATER only as DERIVATIONS OVER RECORDED FACTS, which
    means derived AT READ and never stored (L3).
  * CONSUMER WIRING anywhere in the pipeline - no verdict path, no HAIL
    surface. An instrument first, consumers by later ruling.
  * AUTO-RESOLUTION OF ANY KIND. See `resolve` and `overdue`.

COINS NOTHING: six dependency members recovered verbatim from L2's own
sentence, three outcome members from the registration's own words, the
three-state field vocabulary is Docket H's (REUSED, not redeclared), the id
format and ledger shape are the house's, and no threshold, weight, magnitude or
duration exists anywhere in this module.

M9-a (2026-08-19) - THE COMMITMENT CARRIES ITS EXPOSURE. Widened under the
hundred-seventeenth entry (PATH v143), M9_GROUNDING.md section M9-a, heading
line 122. ADDITIVE, governed-content form: `DependencyKind` (the heading's own
six, a SECOND closed vocabulary beside `DependencyLink`, which stays exactly
as Ruling 61 recovered it - era honesty, no reinterpretation of history);
`TypedDependency` (a record reference plus exactly one kind, validated at the
door against the committed census in `prediction_census.py`);
`OperationalCriterion` (a censused kernel record surface, the record it reads,
and the state that resolves each way - deterministically evaluable by
construction, so disposition-time interpretation approaches clerical);
and the `licensing_goal` linkage, VALIDATED TO RESOLVE against the goal
ledger's commitments at commitment time. The hundred-seventeenth entry rules
the goal join differently from res.1's claim_refs (which stay recorded ids,
unvalidated, exactly as before): a commitment carrying `claim_refs` and a
resolving licensing goal is THE JOINT's substrate - what makes an M7-c
license derivable. `GoalLedger.commitment_for` is a pure read; this module
still writes nothing anywhere but its own file. A commitment without
operational criteria or typed dependencies reads honestly as NON-OPERATIONAL
(`is_operational`, derived at read, never stored) - ABSENT is an answer, a
state not a defect, and every legacy line loads exactly as before.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (Any, Callable, ClassVar, Dict, List, Optional, Tuple,
                    Union)

# THE THREE-STATE VOCABULARY IS REUSED, NEVER REDECLARED (Ruling 33's phrasing
# for `echonet.Verdict` crossing into the packet). It is Docket H's cut and
# `claim_ancestry` already owns one definition of it; a second would be the
# drift hazard Ruling 35 named, in the one place where the two records most
# need to mean the same thing.
#
# `AncestryField` is imported under a LOCAL NAME because here it holds
# prediction criteria rather than ancestry - the TYPE is shared deliberately,
# the reading is local. It is the same class, not a copy.
#
# `_deep_freeze` / `_thaw` ARE IMPORTED RATHER THAN RE-IMPLEMENTED, and that is
# a deliberate departure from the usual "don't reach for a private name":
# `claim_ancestry`'s own `_deep_freeze` docstring records that it is already the
# SECOND definition of that behaviour (after `mutation_proof`'s) and states the
# rule for the next one - "if a THIRD appears, the honest move is to hoist one
# copy into `src/utils/`". Writing a third here is the move that file explicitly
# warned against. THE HOIST IS OWED and is flagged to the architect; it touches
# two files outside this pass's scope, so it is not taken here.
#
# `ClaimAncestryLedger` IS DELIBERATELY NOT IMPORTED. `claim_refs` are recorded
# ids ONLY and are NOT validated against the ancestry ledger - that would make
# this module read a second store. A caller who wants that join performs it.
# AST-pinned.
from src.external.claim_ancestry import (AncestryField as RecordedField,
                                         FieldState, _deep_freeze, _thaw,
                                         absent, declared_none, provided)
# M9-a: the committed census - PURE DATA (vocabulary, not machinery; it
# imports nothing from src/). The door validates reference forms and
# criterion surfaces against it, so a form nothing can resolve is refused at
# commitment rather than stored as hope.
from src.external.prediction_census import (criterion_surface,
                                            id_matches_form, reference_form)
# M9-a: the licensing linkage's owner, READ SURFACE ONLY
# (`commitment_for` is a pure fold over the goal ledger's own file). The
# hundred-seventeenth entry rules this join validated at commitment - a
# DIFFERENT ruling from res.1's claim_refs, which stay unvalidated ids. This
# module writes nothing to the goal store and reaches no promotion surface
# through it (`goal_ledger.py` imports only `src/utils/`).
from src.goals.goal_ledger import GoalLedger
# RULING 66: the shared record-value validator. A pure function over serialized
# payloads - it owns no store, opens no file, and reads nothing, so importing it
# here is not this module reading a second store.
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.atomic_write import durable_append_text
from src.utils.record_value import validate_record_value

__all__ = [
    "DependencyLink", "DependencyKind", "PredictionOutcome",
    "CRITERION_FIELDS", "TypedDependency", "OperationalCriterion",
    "PredictionCommitment", "PredictionResolution", "PredictionLedger",
    "PredictionLedgerUnreadable", "RecordedField", "FieldState",
    "provided", "declared_none", "absent",
]


# =====================================================================
# THE VOCABULARY - every member RECOVERED, none coined
# =====================================================================

class DependencyLink(str, Enum):
    """WHAT A PREDICTION RESTS ON. CLOSED, and every member is L2's own word.

    L2, verbatim - the law names these six in its own sentence, which is why
    this enum is RECOVERED RATHER THAN COINED:

        "A scored-false prediction applies collapse pressure to the exact
         dependency chain that produced it - OBSERVATION, CAUSAL LINK,
         AUXILIARY ASSUMPTION, HORIZON, DOMAIN VALIDITY, or THE CLAIM ITSELF."

    RECORDED AT COMMIT TIME, and the timing is the point: O4 routes pressure to
    "the exact dependency chain that produced it", and A CHAIN RECONSTRUCTED
    AFTER A FAILURE IS A CHAIN DRAWN TO EXPLAIN THE FAILURE. Fixing it at
    commit is what makes it evidence rather than narrative.

    RECORDING ONLY - this module routes nothing. ADDITIONS REQUIRE A MANIFEST
    RULING (Ruling 7's closed-enum discipline).
    """

    OBSERVATION = "observation"
    CAUSAL_LINK = "causal_link"
    AUXILIARY_ASSUMPTION = "auxiliary_assumption"
    HORIZON = "horizon"
    DOMAIN_VALIDITY = "domain_validity"
    THE_CLAIM_ITSELF = "the_claim_itself"


class DependencyKind(str, Enum):
    """WHAT A TYPED DEPENDENCY IS. CLOSED at the ruled six - M9-a's vocabulary.

    Hundred-seventeenth entry (PATH v143), M9_GROUNDING.md section M9-a, on
    the heading's line 122, verbatim:

        "Falsification propagates backward as obligations on the failed
         dependency - observation, causal link, assumption, scope, horizon,
         or main claim."

    A SECOND CLOSED VOCABULARY BESIDE `DependencyLink`, AND BOTH STAY.
    `DependencyLink` is L2's own sentence, recovered by Ruling 61 and carried
    by the legacy `dependency_chain` field, which this entry does not
    reinterpret (era honesty - the old records are clients, never debt). A
    typed dependency under M9-a is a RECORD REFERENCE plus exactly one of
    THESE members, declared at commitment because justifications are recorded
    at formation time - and because M9-b's backward walk routes obligations by
    THIS vocabulary, a chain reconstructed after a failure being a chain drawn
    to explain the failure.

    ADDITIONS REQUIRE A MANIFEST RULING (Ruling 7's closed-enum discipline).
    An unruled seventh is unwritable: `DependencyKind("anything_else")` raises,
    `from_dict` drops the whole line, and the pin file holds the member set.
    """

    #: hundred-seventeenth entry / heading line 122: "observation"
    OBSERVATION = "observation"
    #: hundred-seventeenth entry / heading line 122: "causal link"
    CAUSAL_LINK = "causal_link"
    #: hundred-seventeenth entry / heading line 122: "assumption"
    ASSUMPTION = "assumption"
    #: hundred-seventeenth entry / heading line 122: "scope"
    SCOPE = "scope"
    #: hundred-seventeenth entry / heading line 122: "horizon"
    HORIZON = "horizon"
    #: hundred-seventeenth entry / heading line 122: "main claim"
    MAIN_CLAIM = "main_claim"


class PredictionOutcome(str, Enum):
    """WHAT WAS RECORDED. CLOSED at three, the registration's own words.

    UNRESOLVED is a real recorded outcome, not a placeholder for "not yet":
    an unresolved commitment simply has NO resolution line. Recording
    UNRESOLVED is a deliberate act saying the question was reached and could
    not be settled - the Veiled Thread's discipline, applied to predictions.
    """

    CONFIRMED = "confirmed"
    FALSIFIED = "falsified"
    UNRESOLVED = "unresolved"


# The three criteria, named ONCE so no second spelling can drift from this one
# (Ruling 47's `CMTE_FAILURE_LABELS` shape). `resolve()` validates against this
# tuple, so a caller cannot name a field that is not a criterion at all.
CRITERION_FIELDS: Tuple[str, ...] = (
    "success_criteria",
    "failure_criteria",
    "unresolved_criteria",
)


class PredictionLedgerUnreadable(Exception):
    """RULING 53'S SENTINEL: the ledger EXISTS and its mint cannot be derived.

    Raised at the moment an id would be minted, after ONE re-derivation attempt.
    Minting from an unknown floor would write a `PRD-` id that may already name
    a different prediction, and an append-only ledger cannot later disambiguate
    two records wearing one id - which in THIS ledger would mean two
    commitments, potentially with different criteria, indistinguishable to
    anyone scoring them.

    A STRUCTURAL VIOLATION (Ruling 25's taxonomy).
    """


# =====================================================================
# M9-a - THE EXPOSURE RECORDS, both validated at construction so the door
# inherits their refusals: a commitment is CONSTRUCTED before it is appended,
# and a refused construction writes nothing.
# =====================================================================

@dataclass(frozen=True)
class TypedDependency:
    """A RECORD REFERENCE plus exactly one ruled kind - M9-a section 1A.

    The reference is a (form, id) pair in the proposition ledger's own
    `KernelRef` shape: the FORM names an entry in the committed census
    (`prediction_census.REFERENCEABLE_FORMS`), and the id must wear that
    form's anchored mint shape where the owner mints one. A form outside the
    census is REFUSED HERE - a reference form nothing can resolve is refused
    at the door, not stored as hope. EXISTENCE is deliberately not checked
    here: that is the resolver owner's question at ITS door, exactly as
    `ObligationLedger.admit` already answers it for the backward walk's
    obligations (M9-b).
    """

    kind: DependencyKind
    record_form: str
    record_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, DependencyKind):
            raise TypeError(
                f"TypedDependency.kind carries {self.kind!r}, which is not a "
                f"DependencyKind. A raw string would let a caller invent a "
                f"dependency class the ruled vocabulary deliberately closes.")
        form = reference_form(self.record_form)
        if form is None:
            raise ValueError(
                f"'{self.record_form}' is not a censused reference form. The "
                f"census (prediction_census.REFERENCEABLE_FORMS) holds what "
                f"the kernel honestly resolves; a form outside it is refused "
                f"at the door, never stored as hope.")
        if not id_matches_form(form, self.record_id):
            raise ValueError(
                f"'{self.record_id}' does not wear the censused id form for "
                f"'{self.record_form}' ({form.id_patterns or 'non-empty'}). "
                f"A reference the owner's mint never issued resolves nowhere.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "record_form": self.record_form,
            "record_id": self.record_id,
        }


@dataclass(frozen=True)
class OperationalCriterion:
    """A clerically evaluable resolution criterion - M9-a section 1B.

    Names a censused KERNEL RECORD SURFACE, the record it reads, the state
    that resolves CONFIRMED and the state that resolves FAILED. THE BINDING
    PROPERTY IS DETERMINISTIC EVALUABILITY: given this criterion and the
    kernel, two evaluators agree by construction, because evaluating it is a
    read of the named surface and an equality comparison - nothing more
    (heading line 122: "disposition-time interpretation approaches
    clerical"). Evaluation itself is M9-b's; this record is what makes it
    clerical rather than interpretive.

    Both named states must come from the surface's honest closed vocabulary
    (the owner's own enum, censused as data and drift-pinned), and they must
    differ - a criterion whose CONFIRMED and FAILED name one state resolves
    nothing. A surface outside the census is refused: derive or decline,
    never invent.
    """

    surface: str
    record_id: str
    confirmed_state: str
    failed_state: str

    def __post_init__(self) -> None:
        censused = criterion_surface(self.surface)
        if censused is None:
            raise ValueError(
                f"'{self.surface}' is not a censused criterion surface. The "
                f"census (prediction_census.CRITERION_SURFACES) holds the "
                f"surfaces a clerical evaluator can read; naming another is "
                f"invention, and the discipline is derive or decline.")
        form = reference_form(censused.reference_form)
        if form is None or not id_matches_form(form, self.record_id):
            raise ValueError(
                f"'{self.record_id}' does not wear the censused id form for "
                f"surface '{self.surface}' (reads {censused.reference_form}).")
        for name, state in (("confirmed_state", self.confirmed_state),
                            ("failed_state", self.failed_state)):
            if state not in censused.states:
                raise ValueError(
                    f"OperationalCriterion.{name} names {state!r}, which is "
                    f"outside '{self.surface}''s honest vocabulary "
                    f"{censused.states}. A state the surface can never show "
                    f"is a criterion that can never be met - stored hope.")
        if self.confirmed_state == self.failed_state:
            raise ValueError(
                f"confirmed_state and failed_state both name "
                f"{self.confirmed_state!r}. One state cannot resolve both "
                f"ways; the criterion would decide nothing deterministically.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "surface": self.surface,
            "record_id": self.record_id,
            "confirmed_state": self.confirmed_state,
            "failed_state": self.failed_state,
        }


# =====================================================================
# THE COMMITMENT - an argument of record, frozen before the outcome
# =====================================================================

@dataclass(frozen=True)
class PredictionCommitment:
    """WHAT WAS PREDICTED, AND WHAT WOULD COUNT - fixed before the outcome.

    DEEP-FROZEN AT CONSTRUCTION (Ruling 52). `frozen=True` alone freezes the
    shell and leaves a criterion's value - which may be a dict or list a caller
    handed in - writable through a retained reference. This record is consulted
    precisely when the question is what was committed BEFORE the outcome, so a
    value editable afterwards is not a commitment at all.

    THERE IS NO `update`, NO `amend` AND NO `revise` - not on this record and
    not on the ledger. THE ABSENCE IS THE ENFORCEMENT, and it is pinned as
    shape: the wrong path is unexecutable rather than discouraged. A prediction
    that can be edited after the fact is the exact thing this docket abolishes,
    and a method named `amend` with a docstring saying "only before resolution"
    would be a request for restraint.

    ANY OF THE THREE CRITERIA MAY BE DECLARED_NONE OR ABSENT. A predictor who
    declared NO failure criterion is on record as having declared none - which
    is exactly the fact worth keeping, and is a DIFFERENT FACT from never
    having been asked (Docket H's cut).
    """

    prediction_id: str
    # The prediction itself. Plain and REQUIRED: a commitment with no expected
    # result is not a prediction, so there is no honest three-state reading of
    # its absence.
    expected_result: str
    # JUDGMENT CALL, STATED. These two are three-state like the criteria, not
    # plain strings. The ruling attaches the three-state vocabulary explicitly
    # to the criteria and lists these beside them without saying; the coherent
    # reading is that the same honesty applies, because "no horizon was
    # declared" and "nobody asked for a horizon" are different facts about a
    # prediction - and res.5 needs exactly that distinction to report an
    # overdue commitment without inventing one.
    applicable_conditions: RecordedField = field(default_factory=absent)
    resolution_horizon: RecordedField = field(default_factory=absent)
    success_criteria: RecordedField = field(default_factory=absent)
    failure_criteria: RecordedField = field(default_factory=absent)
    unresolved_criteria: RecordedField = field(default_factory=absent)
    dependency_chain: Tuple[DependencyLink, ...] = ()
    # RECORDED IDS ONLY (Ruling 50's ids-only shape). NOT validated against the
    # ancestry ledger - see the import note.
    claim_refs: Tuple[str, ...] = ()
    committed_at: str = ""
    # ---- M9-a, all three ADDITIVE with honest defaults: a legacy line loads
    # exactly as before and reads NON-OPERATIONAL (`is_operational`).
    operational_criteria: Tuple[OperationalCriterion, ...] = ()
    typed_dependencies: Tuple[TypedDependency, ...] = ()
    # Three-state like the criteria (Docket H's cut): PROVIDED holds a GLC-
    # reference validated to resolve at the door; DECLARED_NONE is a
    # commitment explicitly under no goal; ABSENT is every legacy line.
    # DELIBERATELY NOT IN `RECORDED_FIELDS` - the prior pin closes that tuple
    # exactly (test_ruling61's freeze-list pin), so this field carries the
    # same freeze discipline individually in `__post_init__`.
    licensing_goal: RecordedField = field(default_factory=absent)

    # Every three-state field on this record, in one place.
    #
    # `ClassVar` IS LOAD-BEARING, NOT DECORATION: an annotated class attribute
    # inside a dataclass becomes a FIELD with a default, so without it this
    # tuple would become a seventh constructor parameter - a per-instance,
    # caller-supplied list of which fields the freeze loop walks. A record
    # whose own integrity rule is an argument is not a record.
    RECORDED_FIELDS: ClassVar[Tuple[str, ...]] = (
        "applicable_conditions", "resolution_horizon") + CRITERION_FIELDS

    def __post_init__(self) -> None:
        for name in self.RECORDED_FIELDS:
            item = getattr(self, name)
            if not isinstance(item, RecordedField):
                raise TypeError(
                    f"PredictionCommitment.{name} must be a three-state field - "
                    f"use provided(...) / declared_none() / absent(). A bare "
                    f"value cannot say WHICH of the three answers it is.")
            # Ruling 52: a fresh deep copy, then a recursive read-only rebuild.
            # THE COPY IS THE POINT - a proxy over the caller's own container is
            # a VIEW, and a freeze that stops the honest caller while the one
            # holding the reference writes through is the appearance of
            # immutability.
            object.__setattr__(
                self, name,
                RecordedField(state=item.state,
                              value=_deep_freeze(copy.deepcopy(item.value))))

        for link in self.dependency_chain:
            if not isinstance(link, DependencyLink):
                raise TypeError(
                    f"dependency_chain carries {link!r}, which is not a "
                    f"DependencyLink. A raw string would let a caller invent a "
                    f"dependency class the enum deliberately closes.")
        object.__setattr__(self, "dependency_chain", tuple(self.dependency_chain))
        object.__setattr__(self, "claim_refs", tuple(self.claim_refs))
        for ref in self.claim_refs:
            if not isinstance(ref, str):
                raise TypeError(
                    f"claim_refs carries {ref!r}. Recorded IDS ONLY - a live "
                    f"record object here would be a reference into another "
                    f"owner's store (Ruling 42's finding).")

        # M9-a: the exposure records are typed, already-validated, frozen
        # shapes; anything else here would let a raw dict skip their door.
        object.__setattr__(self, "operational_criteria",
                           tuple(self.operational_criteria))
        for criterion in self.operational_criteria:
            if not isinstance(criterion, OperationalCriterion):
                raise TypeError(
                    f"operational_criteria carries {criterion!r}, which is "
                    f"not an OperationalCriterion - a raw value would skip "
                    f"the censused-surface validation at the door.")
        object.__setattr__(self, "typed_dependencies",
                           tuple(self.typed_dependencies))
        for dependency in self.typed_dependencies:
            if not isinstance(dependency, TypedDependency):
                raise TypeError(
                    f"typed_dependencies carries {dependency!r}, which is "
                    f"not a TypedDependency - a raw value would skip the "
                    f"censused-form validation at the door.")
        if not isinstance(self.licensing_goal, RecordedField):
            raise TypeError(
                f"PredictionCommitment.licensing_goal must be a three-state "
                f"field - use provided(...) / declared_none() / absent(). A "
                f"bare value cannot say WHICH of the three answers it is.")
        # The same Ruling 52 freeze the RECORDED_FIELDS loop applies, held
        # individually because the prior pin closes that tuple exactly.
        object.__setattr__(
            self, "licensing_goal",
            RecordedField(state=self.licensing_goal.state,
                          value=_deep_freeze(
                              copy.deepcopy(self.licensing_goal.value))))

    def criterion(self, name: str) -> RecordedField:
        """The named criterion as recorded, or raise if it is not a criterion."""
        if name not in CRITERION_FIELDS:
            raise ValueError(
                f"'{name}' is not one of the recorded criteria "
                f"{CRITERION_FIELDS}. A resolution names WHICH criterion it "
                f"met, and the set was fixed at commit time.")
        return getattr(self, name)

    def is_operational(self) -> bool:
        """DERIVED AT READ, NEVER STORED (L3). M9-a section 1D.

        OPERATIONAL means the commitment carries BOTH structured resolution
        criteria and typed dependency declarations - the exposure M9-b's
        evaluator and backward walk consume. Either absent reads honestly as
        NON-OPERATIONAL: ABSENT is an answer, a state not a defect, and it is
        precisely what M7-c's HORIZONLESS class already asks about. The
        ledger's whole history is NON-OPERATIONAL by construction, and those
        records are the new machinery's first honest clients - no migration,
        no backfill, no reinterpretation.
        """
        return bool(self.operational_criteria) and bool(self.typed_dependencies)

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "kind": "commitment",
            "prediction_id": self.prediction_id,
            "expected_result": self.expected_result,
            "dependency_chain": [link.value for link in self.dependency_chain],
            "claim_refs": list(self.claim_refs),
            "committed_at": self.committed_at,
            # M9-a: additive keys. A reader of the OLD shape ignores them; a
            # legacy line simply lacks them and loads with the honest defaults.
            "operational_criteria": [c.as_dict()
                                     for c in self.operational_criteria],
            "typed_dependencies": [d.as_dict()
                                   for d in self.typed_dependencies],
            "licensing_goal": self.licensing_goal.as_dict(),
        }
        for name in self.RECORDED_FIELDS:
            payload[name] = getattr(self, name).as_dict()
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["PredictionCommitment"]:
        """Rebuild from a ledger line, or `None` if the line is unreadable.

        THE CLOSED ENUM IS ENFORCED ON THE WAY IN. A `dependency_chain` member
        this build does not know is NOT coerced and NOT dropped from the chain -
        THE WHOLE LINE IS DROPPED by the caller's floor semantics. Keeping a
        partial chain would be worse than keeping none: O4 routes pressure to
        the chain, and a chain silently missing a link would route pressure
        somewhere the predictor never named.
        """
        try:
            chain = tuple(DependencyLink(v) for v in data.get("dependency_chain", []))
            refs = tuple(str(r) for r in data.get("claim_refs", []))
            # M9-a: the same whole-line-drop discipline as the chain above. An
            # unruled kind, an uncensused form or surface, or a state outside
            # a surface's vocabulary raises here and the WHOLE LINE is dropped
            # - a partially-loaded exposure would route M9-b's backward walk
            # somewhere the predictor never named.
            dependencies = tuple(
                TypedDependency(kind=DependencyKind(item["kind"]),
                                record_form=str(item["record_form"]),
                                record_id=str(item["record_id"]))
                for item in data.get("typed_dependencies", []))
            criteria = tuple(
                OperationalCriterion(
                    surface=str(item["surface"]),
                    record_id=str(item["record_id"]),
                    confirmed_state=str(item["confirmed_state"]),
                    failed_state=str(item["failed_state"]))
                for item in data.get("operational_criteria", []))
            return cls(
                prediction_id=str(data["prediction_id"]),
                expected_result=str(data["expected_result"]),
                dependency_chain=chain,
                claim_refs=refs,
                committed_at=str(data.get("committed_at", "")),
                operational_criteria=criteria,
                typed_dependencies=dependencies,
                # A legacy line lacks the key entirely; `from_dict(None)` is
                # ABSENT - never asked, which is the honest reading.
                licensing_goal=RecordedField.from_dict(
                    data.get("licensing_goal")),
                **{name: RecordedField.from_dict(data.get(name))
                   for name in cls.RECORDED_FIELDS},
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class PredictionResolution:
    """WHAT WAS RECORDED against a commitment. A SEPARATE LINE, always.

    It carries the criterion it met BY NAME, because a resolution that does not
    say which recorded criterion was met is a score with nothing behind it.
    """

    prediction_id: str
    outcome: PredictionOutcome
    criterion: str
    note: str = ""
    resolved_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, PredictionOutcome):
            raise TypeError(
                f"PredictionResolution.outcome must be a PredictionOutcome, "
                f"got {type(self.outcome).__name__}.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind": "resolution",
            "prediction_id": self.prediction_id,
            "outcome": self.outcome.value,
            "criterion": self.criterion,
            "note": self.note,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["PredictionResolution"]:
        """Rebuild, or `None`. An unknown `outcome` drops the LINE - it is
        never coerced to a member and never defaulted to UNRESOLVED, which
        would silently turn somebody's recorded verdict into a shrug."""
        try:
            return cls(
                prediction_id=str(data["prediction_id"]),
                outcome=PredictionOutcome(data["outcome"]),
                criterion=str(data["criterion"]),
                note=str(data.get("note", "")),
                resolved_at=str(data.get("resolved_at", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


LedgerEntry = Union[PredictionCommitment, PredictionResolution]


# =====================================================================
# THE LEDGER
# =====================================================================

class PredictionLedger:
    """Append-only prediction ledger. CAE's and O1's shape, deliberately verbatim.

    THE SHAPE IS COPIED ON PURPOSE, not from convenience: CAE is the audit
    ledger this project has already ruled on four times (31, 42 res.4, 45, 53)
    and O1 followed it; every one of those rulings applies here for the same
    reasons. Writing a second, subtly different durable append-only store would
    be re-deciding settled questions by accident.
    """

    ID_PREFIX = "PRD-"

    def __init__(self,
                 ledger_path: str = "data/runtime/logs/prediction_ledger.jsonl",
                 goal_ledger: Optional[GoalLedger] = None):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - redirected in both in the same commit.
        self.ledger_path = Path(ledger_path)
        # M9-a: the licensing linkage's resolver, held the way the obligation
        # ledger holds ITS resolvers - injected at construction, None-able,
        # READ ONLY. A commitment carrying a PROVIDED licensing goal while
        # this is None is REFUSED at the door (`ObligationLedger.admit`'s own
        # rule for an UNCHECKED prediction target): the entry requires the
        # reference to resolve at commitment, and unvalidatable is not
        # validated.
        if goal_ledger is not None and not isinstance(goal_ledger, GoalLedger):
            raise TypeError(
                f"goal_ledger must be a GoalLedger or None, got "
                f"{type(goal_ledger).__name__} - the licensing goal resolves "
                f"against the OWNER's read surface, not a stand-in.")
        self.goal_ledger = goal_ledger
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69 (2026-08-02): THERE IS NO `self._seq`.
        #
        # It was derived once HERE and then incremented in memory forever after,
        # never re-synced - a CACHED DERIVATION OF THE FILE TRUSTED OVER ITS
        # SOURCE, the structure Ruling 63 refused at the projection and Ruling 65
        # refused at the topology. Two live instances over one path minted the
        # same ordinals whenever the second derived before the first appended.
        # Every mint now derives afresh under the file's lock; see `_next_id`.

    # -----------------------------------------------------------------
    # THE MINT - continuity state (Ruling 42 res.4), sentinel per Ruling 53
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `PRD-` ordinal already ON DISK, or `None` if UNDERIVED.

        RULING 69 res.1/res.2/res.5. The body moved to
        `src.utils.ledger_mint.derive_max_ordinal` - **HOISTED, not merely
        shared**: the three ledgers' derivations differed in exactly two ways (a
        local variable name and the JSON key each parsed), and res.2 deletes the
        second BY CONSTRUCTION because the scan no longer parses JSON. What
        remained was identical modulo `ID_PREFIX`.

        RULING 53'S SENTINEL IS UNCHANGED IN SEMANTICS: `None` IFF the ledger
        EXISTS and the read raised; a MISSING ledger is a legitimate `0`. The
        typed refusal stays HERE, in `_next_id`, because the error type is this
        ruling's own vocabulary and not the helper's.

        WHAT CHANGED IS WHAT IS SCANNED. This read `json.loads(line).get(...)`,
        so an ordinal on a TORN OR UNPARSEABLE LINE WAS INVISIBLE and the next
        mint would reissue it. The helper scans RAW TEXT with the anchored
        pattern, so any id that reached disk is seen and never reissued.
        """
        return derive_max_ordinal(self.ledger_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. **DERIVED AT MINT TIME (Ruling 69).**

        CALLERS MUST HOLD `mint_lock(self.ledger_path)` ACROSS derive → mint →
        append. Deriving inside the lock and appending outside it would leave
        exactly the race this ruling closes, so the lock is taken at the WRITE
        path and this method is called within it.

        ~~RE-DERIVES ONCE against an underived mint before refusing, because the
        condition this guards is characteristically TRANSIENT - the whole defect
        was a read failure at construction that had cleared by write time. A
        recovered ledger therefore resumes from its REAL maximum rather than
        refusing a mutation it is now perfectly able to audit.~~

        SUPERSEDED 2026-08-02 BY RULING 69 res.1, kept because it names the
        property that still holds. **THE RE-DERIVE IS SUBSUMED: every mint
        derives**, so a recovered ledger resumes from its real maximum BY
        CONSTRUCTION rather than by a special case that had to be remembered.
        There is no longer a cached value for a transient failure to poison.

        STILL UNDERIVED, IT RAISES. It does NOT fall back to a number: an id
        minted from an unknown floor is exactly the collision Ruling 53 closed,
        and a duplicate id in an append-only ledger is unrecoverable by
        construction (entries are never overwritten, 3a:112, so nothing can ever
        go back and disambiguate the two).

        ~~A BURNT ORDINAL ON A FAILED WRITE IS ACCEPTED AND HARMLESS: `_seq`
        advances before the append, so a raised write leaves a gap. Gaps are
        fine - ids need only be unique and increasing - and a restart reclaims
        it from the file maximum. The alternative, decrementing on failure,
        risks reissuing an id that a partially-written line already carries.~~

        SUPERSEDED 2026-08-02 BY RULING 69, kept because the struck paragraph
        states the SAFETY PROPERTY this ruling makes structural, and it named
        the right hazard for the right reason.

        **THE PROPERTY NOW HOLDS BY READING THE FILE HONESTLY RATHER THAN BY
        MANAGING MEMORY.** There is no `_seq` to advance, so a failed write
        BURNS NOTHING unless bytes landed - and if bytes landed, the raw-text
        scan SEES THEM (res.2), including on a torn line that will not parse.
        The struck text's own fear - "reissuing an id that a partially-written
        line already carries" - was exactly right, and it was a real exposure
        under the OLD derivation, which parsed JSON and so could not see an
        ordinal on a torn line at all. Gaps remain fine; the difference is that
        the ordinal is now reclaimed from the BYTES rather than from a counter
        nobody re-synced.
        """
        seq = self._derive_seq()
        if seq is None:
            raise PredictionLedgerUnreadable(

                f"the prediction ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next PRD ordinal is UNKNOWN. Minting "
                f"one anyway could write an id that already names a different "
                f"prediction - and two commitments wearing one id are two sets "
                f"of criteria nobody can tell apart afterwards.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"
    # -----------------------------------------------------------------
    # THE TWO WRITE PATHS - both APPEND, neither rewrites
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write. Append one line.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim):
        a torn APPEND damages one line, which the floor semantics already drop;
        a torn SNAPSHOT destroys the prior state. Routing an append-only log
        through `atomic_write` would rewrite the whole ledger per entry -
        converting the exempt failure class into the dangerous one in the name
        of fixing it.

            ~~THERE IS NO WRITE MODE ANYWHERE IN THIS FILE BUT `"a"`. That
            is what makes the commitment unrewritable in fact rather than
            by convention.~~

        RULING 78 (2026-08-09) - SUPERSEDED IN PLACE, old text struck above.
        The append moved to `atomic_write.durable_append_text`, so there is
        now no write mode in this file AT ALL. **THE PROPERTY IS UNCHANGED
        AND STRONGER**: the unrewritability is enforced by the funnel plus
        the AST census in `tests/test_ruling78.py`, which forbids a
        mode-`"a"` open anywhere in `src/` outside the helper - so a `"w"`
        here would have to get past a tree-wide scan rather than a reader.
        The atomicity exemption below still stands exactly as written; what
        the move added is DURABILITY, which that exemption never answered.
        """
        # RULING 66 (2026-08-02) - THE WRITER GATE. Refuse what this ledger
        # cannot canonically hold, BEFORE the append. A record either holds what
        # was presented or refuses it; it may not hold something else instead,
        # and this store's entries are cited later by id, so a silently
        # stringified leaf here is a permanent claim that a string was
        # presented when it was not.
        #
        # BEFORE `mkdir` AND BEFORE `open`: a refused entry leaves no file, no
        # line, and no directory it did not already need. `allow_nan=False`
        # below is the SECOND half and is not redundant - it catches NaN and
        # Infinity at the serializer boundary if a future caller ever reaches
        # this write without passing through here.
        validate_record_value(payload, path="prediction_entry")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        # RULING 78 res.2: durable at its own write. Bytes identical -
        # the serializer, the validator above and this store's error
        # discipline are unchanged; only the fsync is new.
        durable_append_text(self.ledger_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def commit(self,
               expected_result: str,
               applicable_conditions: Optional[RecordedField] = None,
               resolution_horizon: Optional[RecordedField] = None,
               success_criteria: Optional[RecordedField] = None,
               failure_criteria: Optional[RecordedField] = None,
               unresolved_criteria: Optional[RecordedField] = None,
               dependency_chain: Tuple[DependencyLink, ...] = (),
               claim_refs: Tuple[str, ...] = (),
               operational_criteria: Tuple[OperationalCriterion, ...] = (),
               typed_dependencies: Tuple[TypedDependency, ...] = (),
               licensing_goal: Optional[RecordedField] = None,
               ) -> PredictionCommitment:
        """Record a prediction BEFORE its outcome. RAISES on write failure.

        THE WRITE GATES THE PREDICTION - O1's gate applied to O3's own reason:
        AN UNRECORDED PREDICTION IS PRECISELY THE REWRITABLE THING THIS DOCKET
        EXISTS TO ABOLISH. If the line cannot be written, the prediction does
        not exist, and the caller learns that by exception rather than by
        holding an object nothing backs.

        A missing criterion defaults to ABSENT, which is the honest reading of
        a caller who did not mention it - never to an empty PROVIDED value,
        which would read as "asked, and there are none".

        M9-a: THE SAME SINGLE FUNNEL, WIDENED - every existing call site stays
        valid (the three new parameters are trailing and defaulted), and the
        widened door validates EVERYTHING before the append. The typed shapes
        self-validated at construction (censused forms, censused surfaces,
        honest state vocabularies); the licensing goal is validated HERE,
        before the mint lock is even taken, so a refused commitment derives
        no ordinal, writes no line, and leaves no directory - refusals before
        the write spend nothing.
        """
        goal = licensing_goal if licensing_goal is not None else absent()
        if not isinstance(goal, RecordedField):
            raise TypeError(
                f"licensing_goal must be a three-state field or None, got "
                f"{type(goal).__name__} - use provided('GLC-...') / "
                f"declared_none() / absent().")
        if goal.state is FieldState.PROVIDED:
            form = reference_form("goal")
            if not isinstance(goal.value, str) or not id_matches_form(
                    form, goal.value):
                raise ValueError(
                    f"the licensing goal reference {goal.value!r} does not "
                    f"wear the goal ledger's censused id form "
                    f"({form.id_patterns}). A reference the mint never issued "
                    f"resolves nowhere, and is refused at the door.")
            if self.goal_ledger is None:
                raise ValueError(
                    f"a licensing goal ({goal.value!r}) was provided but this "
                    f"ledger was constructed without a goal ledger to resolve "
                    f"it against. The hundred-seventeenth entry requires the "
                    f"goal reference to RESOLVE at commitment time; "
                    f"unvalidatable is not validated, so the commitment is "
                    f"refused rather than stored as hope.")
            if self.goal_ledger.commitment_for(goal.value) is None:
                raise ValueError(
                    f"the licensing goal {goal.value!r} does not resolve "
                    f"against the goal ledger's commitments. A commitment "
                    f"under a goal nobody committed licenses nothing.")
        # RULING 69 res.3 - IN-PROCESS MINT-APPEND ATOMICITY. The lock is keyed
        # by the RESOLVED PATH and held across DERIVE -> MINT -> APPEND as one
        # unit; deriving inside it and appending outside would leave exactly the
        # race this ruling closes. It answers the threat that is real under the
        # declared topology (one AUREA process per data root, res.4): two
        # instances, or two threads, inside ONE process. OS file locking is
        # DECLARED OUT with its reopening condition named in `ledger_mint.py`.
        with mint_lock(self.ledger_path):
            return self._mint_and_append(
                expected_result, applicable_conditions, resolution_horizon,
                success_criteria, failure_criteria, unresolved_criteria,
                dependency_chain, claim_refs,
                operational_criteria, typed_dependencies, goal)

    def _mint_and_append(self,
                         expected_result: str,
                         applicable_conditions: Optional[RecordedField],
                         resolution_horizon: Optional[RecordedField],
                         success_criteria: Optional[RecordedField],
                         failure_criteria: Optional[RecordedField],
                         unresolved_criteria: Optional[RecordedField],
                         dependency_chain: Tuple[DependencyLink, ...],
                         claim_refs: Tuple[str, ...],
                         operational_criteria: Tuple[OperationalCriterion, ...],
                         typed_dependencies: Tuple[TypedDependency, ...],
                         licensing_goal: RecordedField,
                         ) -> PredictionCommitment:
        """The locked critical section: derive, mint, freeze, append.

        Split out so the lock scope is a whole method rather than an indented
        region - the boundary is then visible in the diff of any future
        change, which is what stops an append drifting out of it.
        """
        commitment = PredictionCommitment(
            prediction_id=self._next_id(),
            expected_result=expected_result,
            applicable_conditions=applicable_conditions or absent(),
            resolution_horizon=resolution_horizon or absent(),
            success_criteria=success_criteria or absent(),
            failure_criteria=failure_criteria or absent(),
            unresolved_criteria=unresolved_criteria or absent(),
            dependency_chain=dependency_chain,
            claim_refs=claim_refs,
            committed_at=datetime.now().isoformat(),
            operational_criteria=operational_criteria,
            typed_dependencies=typed_dependencies,
            licensing_goal=licensing_goal,
        )
        self._append(commitment.as_dict())
        return commitment

    def resolve(self, prediction_id: str, outcome: PredictionOutcome,
                criterion: str, note: str = "") -> PredictionResolution:
        """Record what happened. A NEW LINE - the commitment is never rewritten.

        THIS IS THE STRUCTURAL HEART OF THE RULING. The commitment line stays
        byte-identical forever, so the ledger reads as a HISTORY (what was
        expected, then what was recorded) rather than a STATE (what we now say
        we expected). An in-place update would be indistinguishable, after the
        fact, from having predicted correctly all along.

        THREE REFUSALS, each enforced AT THE WRITE rather than trusted at the
        read:

          * an UNKNOWN prediction id - there is nothing to resolve;
          * a criterion NOT RECORDED on that commitment (not one of the three
            names at all, or one that was DECLARED_NONE / ABSENT) - "criteria
            fixed at commit time" is worth nothing if a resolution may invent
            the criterion it met;
          * a SECOND resolution of the same prediction - a commitment resolves
            ONCE, and a re-score is a new prediction.

        THE OUTCOME IS DELIBERATELY NOT CONSTRAINED TO A MATCHING CRITERION.
        Requiring FALSIFIED to name `failure_criteria` would be a rule this
        ruling does not make, and it would be WRONG: a prediction that declared
        only a success criterion is falsified precisely by failing THAT
        criterion, and forcing a `failure_criteria` it never declared would
        make the honest record unwritable.
        """
        commitment = self.commitment_for(prediction_id)
        if commitment is None:
            raise ValueError(
                f"no commitment '{prediction_id}' is recorded in this ledger. "
                f"A resolution refers to a prediction that was committed "
                f"BEFORE its outcome; there is nothing here to resolve.")

        recorded = commitment.criterion(criterion)   # raises if not a criterion
        if recorded.state is not FieldState.PROVIDED:
            raise ValueError(
                f"'{prediction_id}' recorded no {criterion} - it is "
                f"{recorded.state.value}. Criteria are FIXED AT COMMIT TIME, "
                f"so a resolution may not meet a criterion that was never "
                f"committed. Naming one after the outcome is the rewriting "
                f"this ledger exists to prevent.")

        existing = self.resolution_for(prediction_id)
        if existing is not None:
            raise ValueError(
                f"'{prediction_id}' is already resolved as "
                f"{existing.outcome.value} against {existing.criterion}. A "
                f"commitment resolves ONCE; a re-score is a new prediction.")

        resolution = PredictionResolution(
            prediction_id=prediction_id,
            outcome=outcome,
            criterion=criterion,
            note=note,
            resolved_at=datetime.now().isoformat(),
        )
        self._append(resolution.as_dict())
        return resolution

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> Tuple[LedgerEntry, ...]:
        """Every readable entry, IN APPEND ORDER. The history, as written.

        Reads the FILE rather than `self.entries`: the ledger spans processes
        and the in-memory mirror does not. A line that will not parse, that
        carries an unknown `kind`, or that carries an enum value outside a
        closed vocabulary contributes NOTHING - it is never coerced.
        """
        if not self.ledger_path.exists():
            return ()
        out: List[LedgerEntry] = []
        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(data, dict):
                    continue
                kind = data.get("kind")
                if kind == "commitment":
                    entry = PredictionCommitment.from_dict(data)
                elif kind == "resolution":
                    entry = PredictionResolution.from_dict(data)
                else:
                    continue
                if entry is not None:
                    out.append(entry)
        return tuple(out)

    def commitments(self) -> Tuple[PredictionCommitment, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, PredictionCommitment))

    def resolutions(self) -> Tuple[PredictionResolution, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, PredictionResolution))

    def commitment_for(self, prediction_id: str) -> Optional[PredictionCommitment]:
        for entry in self.commitments():
            if entry.prediction_id == prediction_id:
                return entry
        return None

    def resolution_for(self, prediction_id: str) -> Optional[PredictionResolution]:
        for entry in self.resolutions():
            if entry.prediction_id == prediction_id:
                return entry
        return None

    def outstanding(self) -> Tuple[PredictionCommitment, ...]:
        """Committed and NOT resolved. PURE RECORDED FACT - no clock involved.

        An unresolved commitment stays outstanding and VISIBLE for as long as
        it is unresolved. Nothing expires it, nothing hides it, and nothing
        judges it - the Veiled Thread's discipline applied to predictions:
        nothing is discarded and nothing is prematurely judged.
        """
        resolved = {r.prediction_id for r in self.resolutions()}
        return tuple(c for c in self.commitments()
                     if c.prediction_id not in resolved)

    def overdue(self,
                horizon_has_passed: Callable[[RecordedField], bool]
                ) -> Tuple[PredictionCommitment, ...]:
        """Outstanding commitments whose RECORDED horizon the CALLER judges past.

        HORIZON IS A RECORDED DECLARATION, NOT A SCHEDULER. This ledger runs no
        clock, fires no timer, and NEVER AUTO-RESOLVES - an auto-resolution
        would be the ledger scoring its own predictions, which is the whole
        thing prior commitment exists to prevent.

        THE MODULE DOES NOT INTERPRET A HORIZON, AND CANNOT HONESTLY: a horizon
        may be a date, a cycle count, or an observed condition, and picking a
        format here would COIN one - at the exact point where "has this expired"
        gets decided. So the CALLER supplies the judgement and the ledger
        supplies the record plus the fact that nothing has resolved it.

        "OVERDUE" IS COMPUTED AT READ, EVERY TIME, AND IS NEVER STORED (L3:
        derive standing, never store it redundantly; and Ruling 42's
        cached-status lesson). An overdue commitment remains UNRESOLVED and
        VISIBLE - passing a horizon changes the record not at all.

        RULING 64 res.8 - ONLY PROVIDED HORIZONS ARE CONSULTED. A commitment
        that DECLARED NO horizon is not overdue, and one that was NEVER ASKED
        is not knowable; handing either to the predicate as though it were a
        date invites the caller to make something up about a record that says
        nothing. The predicate now sees only horizons that exist, and the
        other two states are reported by `outstanding()` or not at all -
        Docket H's two-absences cut, at the read.
        """
        return tuple(
            c for c in self.outstanding()
            if c.resolution_horizon.state is FieldState.PROVIDED
            and horizon_has_passed(c.resolution_horizon))


# NOT REGISTERED IN `STORE_OWNERS`, and CAE's reason applies verbatim: the
# Ruling-1 scanner keys on an ATTRIBUTE NAME, and this store is a FILE with no
# in-memory collection to scan - `entries` is a per-process mirror nothing reads
# back into a decision. Registering it would flag nothing and claim coverage
# that does not exist, which is the completeness-claim defect. What guards it
# instead is that `_append` is the only write path.
#     ~~...and it opens mode "a".~~
# RULING 78 (2026-08-09): it opens nothing - it calls the append funnel,
# which is what a tree-wide AST census can police and a per-file reading
# could not.
