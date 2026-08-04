"""
goal_ledger.py - RULING 72 / DOCKET Q item Q1: THE GOAL COMMITMENT LEDGER.

    A goal that was not committed before its pursuit is not a goal.

Ruling 61's law, generalized from prediction to INTENTION. Without prior
commitment a goal is rewritable until whatever happened looks like what was
wanted, so this ledger's entire job is to make the commitment UNREWRITABLE and
the outcome MECHANICAL against criteria that already existed.

THE LEDGER IS SUBSTRATE, NOT MOVER
-------------------------------------------------------------------------------
It stores DIRECTION. It moves nothing, wires to nothing, and grants no
authority. Q2 owns selection and arbitration; Q3 owns bounded activation and
drive wiring. This ruling builds the memory of intention and NOTHING else - and
at the close of this pass nothing in `src/` imports this module at all.

QL0 AS STRUCTURE (res.6) - THE ENFORCEMENT IS THE IMPORT LIST
-------------------------------------------------------------------------------
**A goal grants no authority, so the module that stores goals cannot reach
anything a goal might wish to command.** No SAE, no Codex, no RACM, no reflex
grid, no expression layer, no topology. Not "does not call" - CANNOT: the names
are not in scope. Ruling 70's enforcement-by-scope, one docket later, and the
import-absence census is AST-pinned with a fires-control.

What it may import is deliberately tiny: the shared mint, the record-value
gate, the deep freeze, and stdlib.

WHAT IS DELIBERATELY NOT HERE, each with its owner
-------------------------------------------------------------------------------
  * ARBITRATION and the tie-key ladder -> Q2, carrying Ruling 71's pins. This
    ledger never chooses between commitments; it does not even order them.
  * ACTIVATION RECORDS (QL5's bounded shape) and DRIVE WIRING -> Q3.
  * EXTERNAL SCOPE -> Q4, blocked.
  * THE DIFFERENTIAL MUTATION THRESHOLDS BY LEVEL -> an arbitration/adoption-era
    ruling. **This ledger STORES `level`; it does not enforce a mutation class
    from it.** Storing a field is not the same as policing it, and the policing
    rule is not this ruling's to invent.
  * ANY PRIORITY, CONFIDENCE, WEIGHT OR SCALAR STANDING -> QL4 and the standing
    refusals. Not present, pinned as ABSENCE, and there is nowhere to put one:
    no record carries a numeric field at all.

COINS NOTHING: every enum member is recovered from the ruling's own closed
lists, the id format is the house convention, the mint is Ruling 69's shared
helper, the three-state criterion shape is `AncestryField`'s, and no threshold,
weight or magnitude exists anywhere in this path.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.utils.deep_freeze import deep_freeze as _deep_freeze
from src.utils.deep_freeze import thaw as _thaw
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

# =====================================================================
# THE VOCABULARIES - every one CLOSED, every member RECOVERED
# =====================================================================


class GoalKind(str, Enum):
    """WHAT KIND of goal. CLOSED (Ruling 72 res.1).

    **THE LAST TWO ARE STRUCTURALLY UNPRODUCIBLE, PER QL3.** Epistemic
    commitments come before world agency, so the members exist - a closed
    vocabulary missing a registered member is the enum reopening later - and NO
    code path constructs a commitment carrying them. `GoalLedger.commit`
    REFUSES them with a typed error naming QL3.

    THE MEMBERS STAY RATHER THAN BEING OMITTED for Ruling 63's stated reason
    (`OBSERVED`'s precedent): the vocabulary is decided now, and the day the
    barrier lifts is a ruling, not an enum edit made in passing.

    REOPENING CONDITIONS, NAMED:
      * EXTERNAL_TASK       -> the ACTION GATEWAY. Nothing in this system can
                               act on the world; a goal whose kind presumes it
                               would be a commitment to something unreachable.
      * CAPABILITY_ACQUISITION -> the HASH-CHAIN plus AUTOGENESIS unblocking. A
                               goal to acquire capability is self-modification
                               wearing intention's clothes, and the guards that
                               would make it auditable are not built.
    """

    RESEARCH = "research"
    VERIFICATION = "verification"
    REPAIR = "repair"
    EXTERNAL_TASK = "external_task"                    # UNPRODUCIBLE (QL3)
    CAPABILITY_ACQUISITION = "capability_acquisition"  # UNPRODUCIBLE (QL3)


# The two members no live path may mint. Named ONCE so the refusal and its pin
# read the same list (Ruling 47's `CMTE_FAILURE_LABELS` shape).
UNPRODUCIBLE_KINDS: Tuple[GoalKind, ...] = (
    GoalKind.EXTERNAL_TASK,
    GoalKind.CAPABILITY_ACQUISITION,
)


class GoalLevel(str, Enum):
    """The hierarchy position. CLOSED.

    STORED AS DECLARED. This ledger does NOT enforce mutation classes by level -
    that is arbitration/adoption-era work and is declared OUT above. A field
    recorded is not a rule enforced, and conflating the two is how a store
    quietly becomes a governor.
    """

    ROOT = "root"
    EPOCH = "epoch"
    PROJECT = "project"
    IMMEDIATE = "immediate"


class GoalProvenance(str, Enum):
    """WHERE the goal came from. CLOSED.

    **THE ASSERTER IS A SEPARATE DECLARED STRING, NOT AN ENUM MEMBER** - L1 at
    the goal layer. The founder is a named external asserter; making "founder" a
    provenance member would bake one particular proposer into the vocabulary and
    lose the distinction between WHERE a proposal came from and WHO made it.

    INTERNAL_DRIVE HAS NO LEGITIMATE PRODUCER TODAY EITHER, and that is stated
    rather than enforced: nothing internal proposes goals yet, so its first
    producer is Q3's drive wiring. It is deliberately NOT hard-barred like the
    QL3 kinds - the barrier there is a LAW about world agency, whereas this is
    simply a mechanism that does not exist yet. **Any INTERNAL_DRIVE record
    appearing in the ledger before Q3 is a FINDING**, not a permitted state.
    """

    EXTERNAL_PROPOSAL = "external_proposal"
    INTERNAL_DRIVE = "internal_drive"
    CONSTITUTIONAL = "constitutional"


class CriterionKind(str, Enum):
    """HOW a criterion answers. CLOSED, and `AncestryField`'s three-state shape.

    The two special members are FIRST-CLASS, never magic strings:

      DECLARED          an ordinary criterion, carrying its text.
      STANDING          NO TERMINAL STATE OF THIS KIND EXISTS - the root case.
                        A root goal does not complete and does not fail; it
                        stands until superseded.
      SUPERSESSION_ONLY this goal is abandoned ONLY by a superseding
                        commitment - the root mutation class.

    **NEITHER SPECIAL MEMBER CAN BE RESOLVED AGAINST** (see `GoalLedger.resolve`),
    which is what makes a root structurally unresolvable except by supersession.
    That property falls out of the vocabulary rather than being a rule anyone
    must remember.
    """

    DECLARED = "declared"
    STANDING = "standing"
    SUPERSESSION_ONLY = "supersession_only"


class GoalOutcome(str, Enum):
    """How a goal ended. CLOSED (res.2).

    **PREMISE_INVALIDATED IS DISTINCT FROM FAILED, and the distinction is the
    register's enrichment adopted into law: a goal whose GROUND DISSOLVED did
    not fail.** Recording it as FAILED would file a fact about the world as a
    fact about her pursuit, and the two carry opposite lessons - one says the
    approach was wrong, the other says the question stopped existing.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    SUPERSEDED = "superseded"
    PREMISE_INVALIDATED = "premise_invalidated"


class GoalStatus(str, Enum):
    """DERIVED, never stored (res.3 / L3). See `GoalLedger.derive_status`."""

    COMMITTED = "committed"
    EVIDENCE_BEARING = "evidence_bearing"
    RESOLVED = "resolved"
    SUPERSEDED = "superseded"


class AdoptionAct(str, Enum):
    """The vocabulary of an adoption event. CLOSED - and UNREACHABLE (res.4)."""

    ADOPTED = "adopted"
    REVISED = "revised"
    REFUSED = "refused"


# The three criterion surfaces, named ONCE so no second spelling can drift.
CRITERION_FIELDS: Tuple[str, ...] = (
    "completion_criteria",
    "failure_criteria",
    "abandonment_criteria",
)


class GoalLedgerUnreadable(Exception):
    """RULING 53'S SENTINEL: the ledger EXISTS and its mint cannot be derived.

    Raised at the moment an id would be minted. Minting from an unknown floor
    could write a `GLC-` id that already names a different commitment, and an
    append-only ledger cannot later disambiguate two records wearing one id -
    which here would mean two DIRECTIONS, with different criteria,
    indistinguishable to anyone reading what she committed to.
    """


class UnproducibleGoalKind(Exception):
    """QL3: epistemic commitments before world agency.

    Raised when a caller asks for a commitment whose kind presumes an agency
    this system does not have and whose guards are not built.
    """


# =====================================================================
# THE CRITERION - three states, `AncestryField`'s shape reused not redeclared
# =====================================================================

@dataclass(frozen=True)
class GoalCriterion:
    """One criterion, carrying WHICH KIND OF ANSWER it holds.

    `text` is meaningful ONLY when `kind is DECLARED`. The two special kinds
    carry no text by construction, which is what keeps "this goal cannot
    complete" from degrading into an empty string that reads like a criterion
    nobody filled in.
    """

    kind: CriterionKind
    text: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, CriterionKind):
            raise TypeError(
                f"GoalCriterion.kind must be a CriterionKind, got "
                f"{type(self.kind).__name__}. A raw string would let a caller "
                f"invent a criterion class the enum deliberately closes.")
        if self.kind is CriterionKind.DECLARED:
            if not isinstance(self.text, str) or not self.text:
                raise ValueError(
                    "a DECLARED criterion carries its text. An empty declared "
                    "criterion is a criterion nobody can resolve against, "
                    "which is the rewritability this ledger exists to refuse.")
        elif self.text is not None:
            raise ValueError(
                f"a {self.kind.value} criterion carries no text, got "
                f"{self.text!r}. STANDING and SUPERSESSION_ONLY are statements "
                f"ABOUT the answer, not answers.")

    def as_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind.value, "text": self.text}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["GoalCriterion"]:
        """Rebuild from a ledger line, or `None` if unreadable.

        A `kind` outside the closed enum is NOT coerced and NOT defaulted - the
        line is dropped by the caller's floor semantics. A forensic record
        outlives the code that wrote it.
        """
        if not isinstance(data, dict):
            return None
        try:
            kind = CriterionKind(data["kind"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(kind=kind,
                       text=data.get("text") if kind is CriterionKind.DECLARED
                       else None)
        except (TypeError, ValueError):
            return None


def declared(text: str) -> GoalCriterion:
    """An ordinary criterion, carrying its text."""
    return GoalCriterion(kind=CriterionKind.DECLARED, text=text)


def standing() -> GoalCriterion:
    """No terminal state of this kind exists. The root case."""
    return GoalCriterion(kind=CriterionKind.STANDING)


def supersession_only() -> GoalCriterion:
    """Abandoned only by a superseding commitment. The root mutation class."""
    return GoalCriterion(kind=CriterionKind.SUPERSESSION_ONLY)


# =====================================================================
# THE RECORDS - all frozen, all append-only
# =====================================================================

def _ids(value: Any, label: str) -> Tuple[str, ...]:
    """A tuple of recorded ids. IDS-ONLY, never validated against any store.

    RULING 61'S `claim_refs` SEMANTICS VERBATIM: this ledger does not open a
    second store to check that a referenced record exists. **The join is the
    caller's.** A ledger that validated its references would be a ledger that
    reads another owner's store to decide whether to accept a write - and would
    refuse to record a real intention because some other file was unavailable.
    """
    if value is None:
        return ()
    if isinstance(value, str):
        raise TypeError(
            f"{label} must be a sequence of id strings, not a single string. "
            f"A bare string would be recorded as a tuple of its characters.")
    items = tuple(value)
    for item in items:
        if not isinstance(item, str):
            raise TypeError(
                f"{label} carries {type(item).__name__}; recorded references "
                f"are ID STRINGS ONLY. A live object here would be a handle "
                f"into another owner's store (Ruling 42).")
    return items


@dataclass(frozen=True)
class GoalCommitment:
    """WHAT WAS INTENDED, AND WHAT WOULD COUNT - fixed before the pursuit.

    DEEP-FROZEN AT CONSTRUCTION (Ruling 52). `frozen=True` alone freezes the
    shell and leaves a mutable interior writable through a retained reference.
    This record is consulted precisely when the question is what was committed
    BEFORE the outcome, so an interior editable afterwards is not a commitment.

    **THERE IS NO `update`, NO `amend`, NO `revise` and NO `retarget`** - not on
    this record and not on the ledger. THE ABSENCE IS THE ENFORCEMENT and it is
    pinned as SHAPE. A goal that can be edited after the fact is the exact thing
    QL1 abolishes, and a method named `amend` with a docstring saying "only
    before resolution" would be a request for restraint - which this project has
    hard evidence fails.

    **ROOT MUTATION IS SUPERSESSION** (res.1): a NEW commitment naming its
    predecessor in `supersedes_goal_id`, NEVER an edit. The predecessor's bytes
    are untouched forever, so the record reads as a HISTORY of what she meant
    rather than a STATE of what she now says she meant. QL1 governs EVERY level,
    root included - and the root is exactly where the temptation to edit lives.
    """

    goal_id: str
    kind: GoalKind
    level: GoalLevel
    # The direction itself. Plain and REQUIRED: a commitment with no desired
    # state is not a goal, so there is no honest reading of its absence.
    desired_state: str
    provenance: GoalProvenance
    # RECORDED BYTE-IDENTICAL, NEVER VERIFIED, NEVER NORMALIZED (L1 at the goal
    # layer, Ruling 70's `asserted_by` reasoning). This ledger cannot check that
    # a name is who it says it is, and a layer that cannot verify something must
    # not appear to have verified it.
    asserter: str
    completion_criteria: GoalCriterion
    failure_criteria: GoalCriterion
    abandonment_criteria: GoalCriterion
    permitted_scope: str = ""
    # IDS-ONLY, all three. See `_ids`.
    originating_record_ids: Tuple[str, ...] = ()
    justification_claim_ids: Tuple[str, ...] = ()
    governing_doctrine_ids: Tuple[str, ...] = ()
    supersedes_goal_id: Optional[str] = None
    committed_at: str = ""

    def __post_init__(self) -> None:
        for name, enum_type in (("kind", GoalKind), ("level", GoalLevel),
                                ("provenance", GoalProvenance)):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(
                    f"GoalCommitment.{name} must be a {enum_type.__name__}, "
                    f"got {type(getattr(self, name)).__name__}.")
        if not isinstance(self.desired_state, str) or not self.desired_state:
            raise ValueError(
                "a commitment carries its desired state. A goal with no "
                "direction is not a goal.")
        if not isinstance(self.asserter, str):
            raise TypeError("asserter is a DECLARED STRING, recorded as given.")
        for name in CRITERION_FIELDS:
            if not isinstance(getattr(self, name), GoalCriterion):
                raise TypeError(
                    f"GoalCommitment.{name} must be a GoalCriterion - use "
                    f"declared(...) / standing() / supersession_only(). A bare "
                    f"value cannot say WHICH of the three answers it is.")
        # Ruling 52: a fresh deep copy, then a recursive read-only rebuild. The
        # COPY is what defeats a caller's retained reference; a proxy over the
        # caller's own object is a VIEW, and a freeze that stops only the honest
        # caller is not a freeze.
        for name in ("originating_record_ids", "justification_claim_ids",
                     "governing_doctrine_ids"):
            object.__setattr__(
                self, name,
                _deep_freeze(copy.deepcopy(_ids(getattr(self, name), name))))

    def criterion(self, name: str) -> GoalCriterion:
        """The named criterion, or RAISE if it is not one of the three.

        Raising on an unknown NAME is the first half of res.2's guard: a
        resolution may not invent the criterion it met, and "not a criterion at
        all" is a different error from "a criterion that cannot be resolved
        against" (Ruling 29 - one type per cause).
        """
        if name not in CRITERION_FIELDS:
            raise ValueError(
                f"'{name}' is not a criterion. A commitment carries exactly "
                f"{list(CRITERION_FIELDS)}, fixed at commit time.")
        return getattr(self, name)

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "kind_of_record": "commitment",
            "goal_id": self.goal_id,
            "kind": self.kind.value,
            "level": self.level.value,
            "desired_state": self.desired_state,
            "provenance": self.provenance.value,
            "asserter": self.asserter,
            "permitted_scope": self.permitted_scope,
            "originating_record_ids": list(self.originating_record_ids),
            "justification_claim_ids": list(self.justification_claim_ids),
            "governing_doctrine_ids": list(self.governing_doctrine_ids),
            "supersedes_goal_id": self.supersedes_goal_id,
            "committed_at": self.committed_at,
        }
        for name in CRITERION_FIELDS:
            payload[name] = getattr(self, name).as_dict()
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["GoalCommitment"]:
        """Rebuild from a ledger line, or `None` if the line is unreadable.

        THE CLOSED ENUMS ARE ENFORCED ON THE WAY IN. A value this build does
        not know is NOT coerced to a member and NOT defaulted - the line is
        dropped. Silently reading an unknown kind as a known one would put a
        fact in the reader's hands that the writer never recorded.
        """
        try:
            kind = GoalKind(data["kind"])
            level = GoalLevel(data["level"])
            provenance = GoalProvenance(data["provenance"])
        except (KeyError, ValueError, TypeError):
            return None
        criteria = {}
        for name in CRITERION_FIELDS:
            criterion = GoalCriterion.from_dict(data.get(name))
            if criterion is None:
                return None
            criteria[name] = criterion
        try:
            return cls(
                goal_id=str(data["goal_id"]),
                kind=kind,
                level=level,
                desired_state=str(data["desired_state"]),
                provenance=provenance,
                asserter=str(data.get("asserter", "")),
                permitted_scope=str(data.get("permitted_scope", "")),
                originating_record_ids=tuple(
                    data.get("originating_record_ids") or ()),
                justification_claim_ids=tuple(
                    data.get("justification_claim_ids") or ()),
                governing_doctrine_ids=tuple(
                    data.get("governing_doctrine_ids") or ()),
                supersedes_goal_id=data.get("supersedes_goal_id"),
                committed_at=str(data.get("committed_at", "")),
                **criteria,
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class GoalEvidence:
    """Evidence BEARING ON a goal. A SEPARATE APPEND - never an edit.

    **THIS RECORD SETTLES NOTHING.** It records that something was observed to
    bear on a commitment; it does not say the goal is closer, and it carries no
    magnitude with which to say so (QL4). Contradictory evidence is never
    settled by list order (Ruling 64 res.5) - which here is structural rather
    than promised, because evidence contributes NOTHING to the derived status
    beyond the fact that some exists.
    """

    goal_id: str
    evidence_record_ids: Tuple[str, ...] = ()
    note: str = ""
    recorded_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "evidence_record_ids",
            _deep_freeze(copy.deepcopy(
                _ids(self.evidence_record_ids, "evidence_record_ids"))))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "evidence",
            "goal_id": self.goal_id,
            "evidence_record_ids": list(self.evidence_record_ids),
            "note": self.note,
            "recorded_at": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["GoalEvidence"]:
        try:
            return cls(
                goal_id=str(data["goal_id"]),
                evidence_record_ids=tuple(data.get("evidence_record_ids") or ()),
                note=str(data.get("note", "")),
                recorded_at=str(data.get("recorded_at", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class GoalResolution:
    """How a goal ENDED. A SEPARATE APPEND - the commitment is never rewritten.

    THE STRUCTURAL HEART, and it is Ruling 61's verbatim: the commitment line
    stays byte-identical forever, so the ledger reads as a HISTORY (what was
    intended, then what was recorded) rather than a STATE (what we now say we
    intended). An in-place update would be indistinguishable, afterwards, from
    having wanted the outcome all along.
    """

    goal_id: str
    outcome: GoalOutcome
    criterion: str
    note: str = ""
    resolved_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, GoalOutcome):
            raise TypeError(
                f"GoalResolution.outcome must be a GoalOutcome, got "
                f"{type(self.outcome).__name__}.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "resolution",
            "goal_id": self.goal_id,
            "outcome": self.outcome.value,
            "criterion": self.criterion,
            "note": self.note,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["GoalResolution"]:
        try:
            outcome = GoalOutcome(data["outcome"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(
                goal_id=str(data["goal_id"]),
                outcome=outcome,
                criterion=str(data["criterion"]),
                note=str(data.get("note", "")),
                resolved_at=str(data.get("resolved_at", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class GoalAdoption:
    """AUREA'S OWN ADOPTION of a proposed goal. **NO PRODUCER PATH** (res.4).

    THE TYPE EXISTS AND NOTHING CAN WRITE ONE. There is no ledger method that
    constructs or appends this record, and no call to this constructor anywhere
    in `src/` - AST-pinned.

    **THE REASON IS QL6, AND IT IS THE WHOLE POINT OF THE DOCKET.** Adoption is
    AUREA's own event: the moment a proposed direction becomes a direction she
    holds. Her deliberation machinery does not exist yet, so nothing here is
    entitled to produce that moment. **A founder-written adoption would be the
    laundering QL6 names** - an external proposal wearing her assent, and the
    record would be indistinguishable afterwards from one she actually made.

    So the roots enter as EXTERNAL PROPOSALS and STAY proposals. The laws bind
    now regardless: a proposed root constrains through its law; an adopted root
    directs through her commitment.

    REOPENING CONDITION, NAMED: the Q3-era deliberation machinery. On that day
    this type gets its producer, and not before.
    """

    goal_id: str
    act: AdoptionAct
    justification_record_ids: Tuple[str, ...] = ()
    note: str = ""
    recorded_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.act, AdoptionAct):
            raise TypeError(
                f"GoalAdoption.act must be an AdoptionAct, got "
                f"{type(self.act).__name__}.")
        object.__setattr__(
            self, "justification_record_ids",
            _deep_freeze(copy.deepcopy(
                _ids(self.justification_record_ids,
                     "justification_record_ids"))))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "adoption",
            "goal_id": self.goal_id,
            "act": self.act.value,
            "justification_record_ids": list(self.justification_record_ids),
            "note": self.note,
            "recorded_at": self.recorded_at,
        }


LedgerEntry = Union[GoalCommitment, GoalEvidence, GoalResolution]


# =====================================================================
# THE LEDGER
# =====================================================================

class GoalLedger:
    """Append-only goal ledger. CAE's / O1's / O3's shape, deliberately verbatim.

    THE SHAPE IS COPIED ON PURPOSE. CAE is the append-only store this project
    has ruled on five times (31, 42 res.4, 45, 53, 69) and O1 and O3 followed
    it; every one of those rulings applies here for the same reasons. Writing a
    second, subtly different durable append-only store would be re-deciding
    settled questions by accident.
    """

    ID_PREFIX = "GLC-"
    SEED_PATH = "data/goal_roots.json"   # TRACKED, READ-ONLY (Ruling 32)

    def __init__(self,
                 ledger_path: str = "data/runtime/logs/goal_ledger.jsonl",
                 seed_path: Optional[str] = None):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the same commit.
        self.ledger_path = Path(ledger_path)
        # THE SEED IS READ-ONLY INPUT WITH NO WRITER (Ruling 32). It is read at
        # genesis and never opened for writing anywhere in this file.
        self.seed_path = Path(seed_path or self.SEED_PATH)
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: THERE IS NO `self._seq`. Every mint derives from the file
        # under the file's lock; a cached ordinal is a derivation trusted over
        # its source, and this house has refused that structure three times.

    # -----------------------------------------------------------------
    # THE MINT - Ruling 69's shared helper, SECOND consumer
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `GLC-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's whole property set inherits at a new prefix: file-derived at
        the moment of minting, RAW-TEXT scanned so an ordinal on a torn or
        unparseable line is still seen and never reissued, and Ruling 53's
        sentinel intact - `None` IFF the ledger EXISTS and the read raised, a
        MISSING ledger a legitimate `0`.

        The typed refusal stays HERE, in `_next_id`, because the error type is
        this ruling's own vocabulary and not the helper's.
        """
        return derive_max_ordinal(self.ledger_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE.

        CALLERS MUST HOLD `mint_lock(self.ledger_path)` ACROSS derive → mint →
        append. Deriving inside the lock and appending outside would leave
        exactly the race Ruling 69 closes.

        UNDERIVED, IT RAISES - it does NOT fall back to a number. A duplicate id
        in an append-only ledger is unrecoverable by construction (3a:112), and
        here it would mean two DIRECTIONS nobody can tell apart.
        """
        seq = self._derive_seq()
        if seq is None:
            raise GoalLedgerUnreadable(
                f"the goal ledger at '{self.ledger_path}' exists and cannot be "
                f"read, so the next GLC ordinal is UNKNOWN. Minting one anyway "
                f"could write an id that already names a different commitment, "
                f"and two goals wearing one id are two directions nobody can "
                f"tell apart afterwards.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE - append, never rewrite
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write. Append one line.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim): a
        torn APPEND damages one line, which the floor semantics already drop; a
        torn SNAPSHOT destroys the prior state. Routing an append-only log
        through `atomic_write` would rewrite the whole ledger per entry -
        converting the exempt failure class into the dangerous one in the name
        of fixing it.

        THERE IS NO WRITE MODE ANYWHERE IN THIS FILE BUT `"a"`. That is what
        makes the commitment unrewritable in fact rather than by convention.

        RULING 66's WRITER GATE runs BEFORE `mkdir` and BEFORE `open`, so a
        refused entry leaves no file, no line, and no directory it did not
        already need. `allow_nan=False` is the second half and is not redundant:
        `default=` is absent entirely, so a non-canonical leaf REFUSES rather
        than being silently stringified into a permanent record.
        """
        validate_record_value(payload, path="goal_entry")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def commit(self,
               desired_state: str,
               kind: GoalKind,
               level: GoalLevel,
               provenance: GoalProvenance,
               asserter: str,
               completion_criteria: Optional[GoalCriterion] = None,
               failure_criteria: Optional[GoalCriterion] = None,
               abandonment_criteria: Optional[GoalCriterion] = None,
               permitted_scope: str = "",
               originating_record_ids: Any = (),
               justification_claim_ids: Any = (),
               governing_doctrine_ids: Any = (),
               supersedes_goal_id: Optional[str] = None,
               ) -> GoalCommitment:
        """Record a goal BEFORE its pursuit. RAISES on write failure.

        A THIN DELEGATION TO `_commit`, and the split is REQUIRED rather than
        stylistic. `Codex.commit` is the doctrine write API, and Ruling 5's
        invariant scans `src/` for calls to `.commit()` on any receiver -
        correctly, because a scanner that had to tell "commit a goal" from
        "commit a doctrine" by inferring the receiver's type is one that will
        eventually get it wrong. Genesis needs to commit the seed roots, so an
        internal `self.commit(...)` would have been the first such call outside
        SAE in the whole tree.

        **THE PUBLIC NAME STAYS** - `commit` is this docket's own vocabulary
        (QL1 "commitment precedes outcome") and is Ruling 61's sibling shape
        verbatim. CLAUDE.md §2's rule is that the fix is the NAME rather than
        the test; here the name that had to move was the INTERNAL call site,
        which is the one that carried the ambiguity.

        THE WRITE GATES THE GOAL - O1's gate on QL1's own reason: an unrecorded
        commitment is precisely the rewritable thing this docket abolishes. If
        the line cannot be written, the goal does not exist, and the caller
        learns that by exception rather than by holding an object nothing backs.

        TWO REFUSALS, each enforced AT THE WRITE:

          * an UNPRODUCIBLE KIND (QL3) - EXTERNAL_TASK and
            CAPABILITY_ACQUISITION presume an agency this system does not have;
          * a `supersedes_goal_id` naming a goal THIS LEDGER DOES NOT HOLD -
            supersession is the ONLY way a root mutates, so a supersession
            pointing at nothing would be an edit with no predecessor, which is
            a new goal wearing a mutation's clothes.

        A missing criterion defaults to STANDING, which is the honest reading of
        a caller who did not name one: no terminal state of that kind was
        declared, so none can be resolved against. It is NOT an empty DECLARED
        criterion, which would read as "a criterion exists" and be resolvable.
        """
        return self._commit(
            desired_state=desired_state, kind=kind, level=level,
            provenance=provenance, asserter=asserter,
            completion_criteria=completion_criteria,
            failure_criteria=failure_criteria,
            abandonment_criteria=abandonment_criteria,
            permitted_scope=permitted_scope,
            originating_record_ids=originating_record_ids,
            justification_claim_ids=justification_claim_ids,
            governing_doctrine_ids=governing_doctrine_ids,
            supersedes_goal_id=supersedes_goal_id)

    def _commit(self,
                desired_state: str,
                kind: GoalKind,
                level: GoalLevel,
                provenance: GoalProvenance,
                asserter: str,
                completion_criteria: Optional[GoalCriterion] = None,
                failure_criteria: Optional[GoalCriterion] = None,
                abandonment_criteria: Optional[GoalCriterion] = None,
                permitted_scope: str = "",
                originating_record_ids: Any = (),
                justification_claim_ids: Any = (),
                governing_doctrine_ids: Any = (),
                supersedes_goal_id: Optional[str] = None,
                ) -> GoalCommitment:
        """The single write path for a commitment. Both callers pass here.

        EVERY GUARD LIVES HERE rather than in the public wrapper, so genesis is
        held to exactly the same refusals as any other caller - a seed root
        carrying an unproducible kind or a dangling supersession would be
        refused identically. A guard that only the public door enforces is a
        guard the seed path walks around.
        """
        if kind in UNPRODUCIBLE_KINDS:
            raise UnproducibleGoalKind(
                f"'{kind.value}' is structurally unproducible under QL3: "
                f"epistemic commitments come before world agency. "
                f"EXTERNAL_TASK reopens with the ACTION GATEWAY; "
                f"CAPABILITY_ACQUISITION reopens with the HASH-CHAIN plus "
                f"AUTOGENESIS unblocking. The member exists so that the "
                f"vocabulary is closed now and the barrier lifts by ruling.")

        if supersedes_goal_id is not None:
            if self.commitment_for(supersedes_goal_id) is None:
                raise ValueError(
                    f"no commitment '{supersedes_goal_id}' is recorded in this "
                    f"ledger, so nothing can supersede it. Root mutation IS "
                    f"supersession - a new commitment naming its predecessor - "
                    f"and a supersession naming nothing is a new goal wearing "
                    f"a mutation's clothes.")

        with mint_lock(self.ledger_path):
            commitment = GoalCommitment(
                goal_id=self._next_id(),
                kind=kind,
                level=level,
                desired_state=desired_state,
                provenance=provenance,
                asserter=asserter,
                completion_criteria=completion_criteria or standing(),
                failure_criteria=failure_criteria or standing(),
                abandonment_criteria=abandonment_criteria or standing(),
                permitted_scope=permitted_scope,
                originating_record_ids=originating_record_ids,
                justification_claim_ids=justification_claim_ids,
                governing_doctrine_ids=governing_doctrine_ids,
                supersedes_goal_id=supersedes_goal_id,
                committed_at=datetime.now().isoformat(),
            )
            self._append(commitment.as_dict())
        return commitment

    def record_evidence(self, goal_id: str,
                        evidence_record_ids: Any = (),
                        note: str = "") -> GoalEvidence:
        """Append evidence bearing on a goal. It settles NOTHING (QL4)."""
        if self.commitment_for(goal_id) is None:
            raise ValueError(
                f"no commitment '{goal_id}' is recorded in this ledger. "
                f"Evidence bears on a goal that was committed BEFORE it.")
        evidence = GoalEvidence(
            goal_id=goal_id,
            evidence_record_ids=evidence_record_ids,
            note=note,
            recorded_at=datetime.now().isoformat(),
        )
        self._append(evidence.as_dict())
        return evidence

    def resolve(self, goal_id: str, outcome: GoalOutcome,
                criterion: str, note: str = "") -> GoalResolution:
        """Record how a goal ended. A NEW LINE - the commitment is never edited.

        THREE REFUSALS, each enforced AT THE WRITE rather than trusted at the
        read (Ruling 61 res.3's shape, and its reasons transfer intact):

          * an UNKNOWN goal id - there is nothing to resolve;
          * a criterion NOT DECLARED on that commitment - either not one of the
            three names at all, or one recorded as STANDING /
            SUPERSESSION_ONLY. "Criteria fixed at commit time" is worth nothing
            if a resolution may invent the criterion it met;
          * a SECOND resolution - a goal resolves ONCE, and a re-score is a new
            goal.

        **THIS IS WHAT MAKES A ROOT STRUCTURALLY UNRESOLVABLE.** A root carries
        STANDING completion, STANDING failure and SUPERSESSION_ONLY abandonment,
        so no criterion on it can be resolved against and the only status it can
        ever reach is SUPERSEDED - derived from a later commitment naming it.
        That property falls out of the criterion vocabulary; it is not a
        special case anyone has to remember.

        THE OUTCOME IS DELIBERATELY NOT CONSTRAINED TO A MATCHING CRITERION,
        Ruling 61's reasoning verbatim: a goal that declared only a completion
        criterion FAILS precisely by failing that criterion, and forcing a
        `failure_criteria` it never declared would make the honest record
        unwritable.
        """
        commitment = self.commitment_for(goal_id)
        if commitment is None:
            raise ValueError(
                f"no commitment '{goal_id}' is recorded in this ledger. A "
                f"resolution refers to a goal that was committed BEFORE its "
                f"pursuit; there is nothing here to resolve.")

        recorded = commitment.criterion(criterion)   # raises if not a criterion
        if recorded.kind is not CriterionKind.DECLARED:
            raise ValueError(
                f"'{goal_id}' recorded no {criterion} - it is "
                f"{recorded.kind.value}. Criteria are FIXED AT COMMIT TIME, so "
                f"a resolution may not meet a criterion that was never "
                f"declared. A {CriterionKind.STANDING.value} criterion says no "
                f"terminal state of that kind exists; a "
                f"{CriterionKind.SUPERSESSION_ONLY.value} one says the goal "
                f"ends only by being superseded.")

        if self.resolution_for(goal_id) is not None:
            existing = self.resolution_for(goal_id)
            raise ValueError(
                f"'{goal_id}' is already resolved as {existing.outcome.value} "
                f"against {existing.criterion}. A goal resolves ONCE; a "
                f"re-score is a new goal.")

        resolution = GoalResolution(
            goal_id=goal_id,
            outcome=outcome,
            criterion=criterion,
            note=note,
            resolved_at=datetime.now().isoformat(),
        )
        self._append(resolution.as_dict())
        return resolution

    # -----------------------------------------------------------------
    # GENESIS - res.5, idempotent, the ONLY seed path
    # -----------------------------------------------------------------

    def ensure_genesis(self) -> Tuple[GoalCommitment, ...]:
        """Commit the seed roots, IF AND ONLY IF this ledger is empty.

        **A SECOND CALL COMMITS NOTHING** - it returns an empty tuple, having
        written no line. Restart is not absolution (Ruling 34): the ledger
        persists, so a process that starts against a non-empty ledger has
        nothing to found. **THERE IS NO RE-SEED METHOD**, and genesis is the
        only path by which a seed root enters the ledger.

        NOT CALLED FROM `__init__`, AND THAT IS A JUDGMENT CALL WITH A REASON.
        No store in this codebase writes from its constructor, and one that did
        would turn every incidental construction - a test fixture, a diagnostic
        script, a redirect that arrived a line too late - into two permanent
        records. Genesis is a deliberate act and reads as one at the call site.
        The idempotence is what makes calling it routinely safe.

        THE SEED IS READ-ONLY INPUT (Ruling 32) and is never opened for writing
        anywhere in this module. A missing or unreadable seed RAISES rather than
        founding an empty ledger: a genesis that quietly founded nothing would
        leave her with no roots and no error, which is the silent-failure class
        this house refuses everywhere else.
        """
        if self.read_all():
            return ()

        roots = self._read_seed()
        committed: List[GoalCommitment] = []
        for root in roots:
            # `_commit`, NOT `self.commit`: Ruling 5's invariant scans `src/`
            # for calls to `.commit()` because that is the Codex doctrine write
            # API, and it is right to - see `commit`'s docstring. Every guard
            # still applies; only the ambiguous call site is gone.
            committed.append(self._commit(
                desired_state=root["desired_state"],
                kind=GoalKind(root["kind"]),
                level=GoalLevel(root["level"]),
                provenance=GoalProvenance(root["provenance"]),
                asserter=root["asserter"],
                completion_criteria=GoalCriterion.from_dict(
                    root["completion_criteria"]),
                failure_criteria=GoalCriterion.from_dict(
                    root["failure_criteria"]),
                abandonment_criteria=GoalCriterion.from_dict(
                    root["abandonment_criteria"]),
                permitted_scope=root.get("permitted_scope", ""),
            ))
        return tuple(committed)

    def _read_seed(self) -> List[Dict[str, Any]]:
        """The tracked seed document's roots, in document order.

        READ ONLY. This method opens the seed in `"r"` and nothing in this
        module ever opens it otherwise - Ruling 32's whole point, enforced by
        there being no other reference to `seed_path` in the file.
        """
        with open(self.seed_path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
        roots = document.get("roots")
        if not isinstance(roots, list) or not roots:
            raise ValueError(
                f"the goal seed at '{self.seed_path}' declares no roots. "
                f"Founding an empty ledger silently would leave her with no "
                f"roots and no error.")
        return roots

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> Tuple[LedgerEntry, ...]:
        """Every readable entry, IN APPEND ORDER. The history, as written.

        Reads the FILE rather than `self.entries`: the ledger spans processes
        and the in-memory mirror does not. A line that will not parse, that
        carries an unknown record kind, or that carries an enum value outside a
        closed vocabulary contributes NOTHING - it is never coerced.

        **NO ADOPTION BRANCH EXISTS HERE.** Nothing can write one (res.4), so
        nothing reads one back; adding a branch would be building half a
        producer for an event that is not hers to have yet.
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
                record_kind = data.get("kind_of_record")
                if record_kind == "commitment":
                    entry = GoalCommitment.from_dict(data)
                elif record_kind == "evidence":
                    entry = GoalEvidence.from_dict(data)
                elif record_kind == "resolution":
                    entry = GoalResolution.from_dict(data)
                else:
                    continue
                if entry is not None:
                    out.append(entry)
        return tuple(out)

    def commitments(self) -> Tuple[GoalCommitment, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, GoalCommitment))

    def commitment_for(self, goal_id: str) -> Optional[GoalCommitment]:
        for entry in self.commitments():
            if entry.goal_id == goal_id:
                return entry
        return None

    def evidence_for(self, goal_id: str) -> Tuple[GoalEvidence, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, GoalEvidence) and e.goal_id == goal_id)

    def resolution_for(self, goal_id: str) -> Optional[GoalResolution]:
        for entry in self.read_all():
            if isinstance(entry, GoalResolution) and entry.goal_id == goal_id:
                return entry
        return None

    def superseded_by(self, goal_id: str) -> Optional[str]:
        """The id of the commitment that supersedes `goal_id`, if any.

        A RECORDED FACT read from the successor's own `supersedes_goal_id` - the
        predecessor is never edited to say it was superseded, because that would
        be the rewrite this ledger refuses.
        """
        for entry in self.commitments():
            if entry.supersedes_goal_id == goal_id:
                return entry.goal_id
        return None

    # -----------------------------------------------------------------
    # STATUS - DERIVED, never stored (res.3 / L3)
    # -----------------------------------------------------------------

    def derive_status(self, goal_id: str) -> GoalStatus:
        """Compute a goal's status from the appends. NEVER STORED, NEVER CACHED.

        NO RECORD CARRIES A STATUS FIELD (L3, AST-pinned). A stored status is a
        second writer of what the appends already determine, and the field is
        the one people read while the facts are the one that is true - Ruling
        63's cached-projection refusal and Ruling 65's stored-derivation
        refusal, both of which this house has already paid for twice.

        PRECEDENCE IS DECLARED RATHER THAN EMERGENT:

          SUPERSEDED first. A superseding commitment is a NEW record explicitly
            naming this goal, and it is how a root mutates - the case the ruling
            most cares about. A superseded goal that also carries a resolution
            keeps BOTH facts legible in the record (`resolution_for` and
            `superseded_by` each still answer); what this method returns is the
            structural fact about the goal's place in the lineage.
          RESOLVED next - the goal's own recorded terminal outcome.
          EVIDENCE_BEARING next - something was recorded as bearing on it.
          COMMITTED otherwise.

        **EVIDENCE ORDER CANNOT CHANGE THIS.** Evidence contributes only its
        EXISTENCE, never a direction or a magnitude, so permuted appends derive
        the same status by construction rather than by a sort anyone maintains
        (QL4; Ruling 64 res.5's no-adjudication-by-list-order).
        """
        if self.commitment_for(goal_id) is None:
            raise ValueError(
                f"no commitment '{goal_id}' is recorded in this ledger; there "
                f"is no status to derive.")
        if self.superseded_by(goal_id) is not None:
            return GoalStatus.SUPERSEDED
        if self.resolution_for(goal_id) is not None:
            return GoalStatus.RESOLVED
        if self.evidence_for(goal_id):
            return GoalStatus.EVIDENCE_BEARING
        return GoalStatus.COMMITTED
