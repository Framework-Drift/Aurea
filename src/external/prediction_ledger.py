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

__all__ = [
    "DependencyLink", "PredictionOutcome", "CRITERION_FIELDS",
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

    def criterion(self, name: str) -> RecordedField:
        """The named criterion as recorded, or raise if it is not a criterion."""
        if name not in CRITERION_FIELDS:
            raise ValueError(
                f"'{name}' is not one of the recorded criteria "
                f"{CRITERION_FIELDS}. A resolution names WHICH criterion it "
                f"met, and the set was fixed at commit time.")
        return getattr(self, name)

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "kind": "commitment",
            "prediction_id": self.prediction_id,
            "expected_result": self.expected_result,
            "dependency_chain": [link.value for link in self.dependency_chain],
            "claim_refs": list(self.claim_refs),
            "committed_at": self.committed_at,
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
            return cls(
                prediction_id=str(data["prediction_id"]),
                expected_result=str(data["expected_result"]),
                dependency_chain=chain,
                claim_refs=refs,
                committed_at=str(data.get("committed_at", "")),
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
                 ledger_path: str = "data/runtime/logs/prediction_ledger.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - redirected in both in the same commit.
        self.ledger_path = Path(ledger_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        self._seq = self._derive_seq()

    # -----------------------------------------------------------------
    # THE MINT - continuity state (Ruling 42 res.4), sentinel per Ruling 53
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `PRD-` ordinal already in the ledger, or `None`.

        RULING 53 WHOLE: `None` IFF the ledger EXISTS and the read raised. A
        MISSING ledger is a legitimate `0`, because absence is a first run and
        not a fault - and answering an unreadable file with `0` is a claim
        about content the code never saw.

        PER-LINE FLOOR SEMANTICS for anything that will not parse: an
        unreadable FILE and an unparseable LINE are different failures and get
        different answers. Resolution lines carry the same `prediction_id` key
        and cannot raise the maximum, so scanning every line is both simpler
        and exactly as correct as filtering by kind.
        """
        if not self.ledger_path.exists():
            return 0
        highest = 0
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry_id = json.loads(line).get("prediction_id", "")
                    except ValueError:
                        continue
                    if isinstance(entry_id, str) and entry_id.startswith(self.ID_PREFIX):
                        tail = entry_id[len(self.ID_PREFIX):]
                        if tail.isdigit():
                            highest = max(highest, int(tail))
        except OSError:
            return None
        return highest

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Ruling 53's shape exactly.

        A BURNT ORDINAL ON A FAILED WRITE IS ACCEPTED AND HARMLESS: `_seq`
        advances before the append, so a raised write leaves a gap. Gaps are
        fine - ids need only be unique and increasing - and a restart reclaims
        it from the file maximum. The alternative, decrementing on failure,
        risks reissuing an id that a partially-written line already carries.
        """
        if self._seq is None:
            self._seq = self._derive_seq()
        if self._seq is None:
            raise PredictionLedgerUnreadable(
                f"the prediction ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next PRD ordinal is UNKNOWN. Minting "
                f"one anyway could write an id that already names a different "
                f"prediction - and two commitments wearing one id are two sets "
                f"of criteria nobody can tell apart afterwards.")
        self._seq += 1
        # `{n:04d}` matches the house convention and GROWS NATURALLY past 9999.
        return f"{self.ID_PREFIX}{self._seq:04d}"

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

        THERE IS NO WRITE MODE ANYWHERE IN THIS FILE BUT `"a"`. That is what
        makes the commitment unrewritable in fact rather than by convention.
        """
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
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
# instead is that `_append` is the only write path and it opens mode "a".
