"""
goal_activation.py - RULING 74 / DOCKET Q item Q3: THE ACTIVATION LAYER.

    A goal that was not committed before its pursuit is not a goal;
    an activation that was not BOUNDED before its attention is not an
    activation.

An ACTIVATION is a bounded episode of directed inquiry attention against ONE
standing commitment. It is opened ONLY from an arbiter's examination, closed
ONLY by a member of QL5's stop set, and its bound is DECLARED AT OPEN and fixed
forever - **Ruling 61's law at the attention layer.**

Q3 is MOTION: the first wire from goals into the core. It is also where
compulsion's bounds move from law to tree.

NOTHING LOOPS. EVERY VERB IS EXTERNALLY INVOKED. QUIESCENCE IS NOT FAILURE.
-------------------------------------------------------------------------------
There is no scheduler here, no timer, no background thread, no `while`, and no
internal call site anywhere in `src/` that invokes an activation verb. The core
exposes these operations as `process_input`'s SIBLINGS - **doors, opened only
from outside.** A layer that could open its own activations would be a layer
that pursues, and pursuit that starts itself is the compulsion shape QL5 exists
to refuse.

An AUREA that is running and has opened nothing is behaving correctly. Emptiness
here is not a gap to be filled by making something fire.

WHAT IT WRITES: exactly ONE store of its own, the activation log. It reads the
examination log through an INJECTED arbiter and writes nothing to it.

QL0 AS STRUCTURE - THE ENFORCEMENT IS THE IMPORT LIST (res.1)
-------------------------------------------------------------------------------
No SAE, no Codex, no RACM, no reflex grid, no expression layer, no topology, no
stochastic machinery - **and NO EchoMemory.** Not "does not call" but CANNOT:
the names are not in scope. Ruling 70's enforcement-by-scope, two dockets on.

**THE EchoMemory ABSENCE IS A SEAM VERDICT, NOT AN OVERSIGHT.** The seam check
ran BEFORE this ruling was drafted and its verdict binds this pass: NO echo
retrieval anywhere in Q3. Five live pressures sit on that store (it is canonical
and UNWIRED; its `default=str` schema decision; caller-side wall-clock Echo ids;
echoes as a fourth topology source; the `claim_id` join key as retrieval
substrate), and **an inquiry layer that reached for echoes would decide all five
by accident, in passing, at the moment they were most convenient to assume.**
The EchoMemory wiring ruling is elevated to next-after-Q3 and owns every one of
them. The absence is pinned.

    A JUDGMENT CALL ON THE RECORD: this module imports NOTHING FROM
    `goal_ledger`, though res.1 permits it. It never needs to - `focus_persistence`
    is the ARBITER's derivation over its own ledger handle, and every reference
    this layer records is IDS-ONLY (Ruling 61's `claim_refs` form). Importing
    less than permitted is strictly safer and stays inside the ruling: the
    smaller the surface, the fewer the things a later pass can reach for. If a
    future ruling gives this layer a reason to read commitments directly, that
    reading is what adds the import.

WHAT IS DELIBERATELY NOT HERE, each with its owner
-------------------------------------------------------------------------------
  * THE `INTERNAL_DRIVE` PRODUCER -> NOT BUILT, Ruling 62's conjunction form.
    See `THE DRIVE PRODUCER` below; the reopening is a CONJUNCTION.
  * ECHO RETRIEVAL as inquiry substance -> the EchoMemory wiring ruling (NEXT).
  * AUTONOMOUS SCHEDULING OR ANY LOOP -> QL5, permanent at this era.
  * WALL-CLOCK BOUNDS -> the carried timestamp-join class. Both bound kinds are
    ORDINAL-BASED, and that is a refusal rather than an omission: a time bound
    would need a clock this layer does not own and a join across two stores that
    share no ordinal, which is the gap `focus_persistence` already declares.
  * MODEL CONSULTATION -> MLOC, gated by AVT.017.
  * ADOPTION MACHINERY -> QL6, the adoption-era ruling.
  * EXTERNAL SCOPE -> Q4, blocked and registered.

COINS: `StopCondition`, `BoundKind`, and the `ACT-` prefix. Nothing else.
**Bound magnitudes are CALLER-DECLARED DATA, like criteria - not coinage.** This
module holds NO default bound and NO threshold constant of any kind, and there
is no numeric literal in the bound derivation at all.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.goals.goal_arbitration import GoalExamination
from src.utils.deep_freeze import deep_freeze as _deep_freeze
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value


# =====================================================================
# THE VOCABULARIES - both CLOSED, both COINED here, producibility DECLARED
# =====================================================================

class StopCondition(str, Enum):
    """WHY an activation closed. **QL5's closed stop set.** COINED by Ruling 74.

    An activation closes by a member of this set or it does not close. There is
    no "other", no free-text stop, and no default - a stop nobody named is a
    stop nobody can audit.

    **PRODUCIBILITY IS DECLARED PER MEMBER** (Rulings 63/64's form), because a
    closed vocabulary whose members are silently unreachable is a vocabulary
    that lies about what this system can currently do:

      BOUND_REACHED             PRODUCIBLE. `bound_met` derives it from the
                                examination record and the DECLARED bound.
      CRITERION_EVIDENCE        PRODUCIBLE. Evidence or a resolution was
                                appended to the goal ledger naming a declared
                                criterion; the close CITES it in
                                `closing_basis_ids`.
      NO_PROGRESS               PRODUCIBLE. `focus_persistence` is the
                                registered substrate. **THE TALLY STILL NEVER
                                GATES** - what fires this is the DECLARED BOUND
                                (res.4), never a module constant, and the close
                                is a RECORDED ACT by an external caller rather
                                than an automatic trigger.
      CONTRADICTION_ENCOUNTERED PRODUCIBLE AS CALLER-DECLARED. The closer
                                records that inquiry met contradiction, with
                                optional ids-only refs. This layer does not
                                detect contradiction and does not pretend to.
      AUTHORITY_DENIAL          **VACUOUS BY SUBSTRATE.** No authorization
                                surface exists that could deny anything, so
                                nothing can honestly record that one did.
                                PRESENT AS SHAPE so the vocabulary is closed
                                NOW and the substrate lifts BY RULING; the
                                public surface REFUSES a close naming it with a
                                typed `UnproducibleStopCondition`.
                                REOPENING CONDITION, NAMED: a ruled
                                authorization surface.

    The member stays rather than being omitted for Ruling 63's stated reason
    (`OBSERVED`'s precedent): a closed vocabulary missing a registered member is
    the enum reopening later, in passing, by whoever needs it.
    """

    BOUND_REACHED = "bound_reached"
    CRITERION_EVIDENCE = "criterion_evidence"
    NO_PROGRESS = "no_progress"
    CONTRADICTION_ENCOUNTERED = "contradiction_encountered"
    AUTHORITY_DENIAL = "authority_denial"          # VACUOUS BY SUBSTRATE


# The stop conditions no live close may name. Named ONCE so the refusal and its
# pin read the same list (Ruling 47's `CMTE_FAILURE_LABELS` shape, and Ruling
# 72's `UNPRODUCIBLE_KINDS` one docket up).
UNPRODUCIBLE_STOPS: Tuple[StopCondition, ...] = (
    StopCondition.AUTHORITY_DENIAL,
)


class BoundKind(str, Enum):
    """WHAT KIND of bound an activation declared. CLOSED. COINED by Ruling 74.

    **BOTH ARE ORDINAL-BASED AND WALL-CLOCK-FREE**, and there is deliberately no
    third, time-based member. A time bound would need a clock this layer does
    not own and a join between two stores that share no symbolic ordinal - the
    exact limitation `GoalArbiter.focus_persistence` already declares about
    itself. The timestamp-join class is CARRIED, not extended.

      EXAMINATION_BOUND  close is DUE after N further examinations of this goal.
      PROGRESS_BOUND     close is DUE after K consecutive examinations of this
                         goal with no progress recorded. `focus_persistence` is
                         the substrate.

    **THE MAGNITUDES ARE CALLER-DECLARED DATA, exactly like a goal's criteria.**
    This module coins no default and no constant: an activation carries the
    bound its opener declared, and nothing here has an opinion about what that
    number should be. That is what keeps §9's standing bar intact at a layer
    whose whole job is to compare a count against something.
    """

    EXAMINATION_BOUND = "examination_bound"
    PROGRESS_BOUND = "progress_bound"


class ActivationLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and cannot be read.

    Raised at the moment an id would be minted - minting from an unknown floor
    could write an `ACT-` id that already names a different activation, and an
    append-only record cannot later disambiguate two lines wearing one id, which
    here would mean two episodes of attention, with different bounds,
    indistinguishable to anyone asking what she was doing and for how long.

    **AND RAISED AT EVERY READ OF THE LOG, WHICH IS WIDER THAN THE SIBLING
    LEDGERS' VERSION OF THIS ERROR** (see `ActivationLayer.read_all`). Every
    fact this layer derives - is an episode open, is this goal already being
    attended to, which examination authorized what - comes out of this one file,
    and each of them is consulted BEFORE a mint is reached. Answering any of
    them from an empty read would be "I could not look" reported as "there is
    nothing there".
    """


class UnproducibleStopCondition(Exception):
    """A stop condition whose SUBSTRATE does not exist in this system.

    Raised when a caller asks to close an activation on a stop nothing could
    honestly have produced. Recording it anyway would put a fact in the record
    that no surface in the tree could have witnessed - L3's fabrication class,
    at the one place a bounded episode gets its reason for ending.
    """


class UnboundedActivation(Exception):
    """An activation asked for with no bound, a non-positive one, or an
    unknown kind.

    **AN UNBOUNDED ACTIVATION IS THE COMPULSION SHAPE QL5 EXISTS TO REFUSE.**
    This is not a validation nicety: a bound declared at open and fixed forever
    is the entire difference between an episode of attention and a system that
    cannot stop attending. It gets its own type because its cause is different
    in kind from a caller naming the wrong record (Ruling 29 - one type per
    cause), and because it is the refusal this whole layer is built around.
    """


# =====================================================================
# THE BOUND - validated BEFORE anything is spent, and again AT THE RECORD
# =====================================================================

def _validate_bound(bound_kind: Any, bound_magnitude: Any) -> None:
    """Refuse an unbounded, non-positive, or unknown-kind bound.

    **CALLED TWICE ON PURPOSE, AND THE SECOND IS NOT REDUNDANT.** It runs in
    `open_activation` BEFORE the mint lock is taken, so a refusal spends no
    ordinal and writes no line (Ruling 24's pre-flight boundary, and Ruling 46's
    reading of it: the wrong path must move nothing). It runs AGAIN in
    `GoalActivation.__post_init__`, so the RECORD TYPE ITSELF is unconstructible
    in an unbounded state - Ruling 46's kept backstop, with its own distinct
    contribution: the frozen record is what reaches disk and what pins read, and
    a type that can be hand-constructed unbounded is a type whose invariant
    lives only in one function's discipline.

    `bool` IS REFUSED THOUGH IT IS AN `int` SUBCLASS. `True` would silently mean
    "one further examination", which is a magnitude nobody declared.
    """
    if not isinstance(bound_kind, BoundKind):
        raise UnboundedActivation(
            f"bound_kind must be a BoundKind, got "
            f"{type(bound_kind).__name__}. An activation declares WHICH bound "
            f"it is held to; a raw value would let a caller invent a bound "
            f"class the enum deliberately closes.")
    if isinstance(bound_magnitude, bool) or not isinstance(bound_magnitude, int):
        raise UnboundedActivation(
            f"bound_magnitude must be an int, got "
            f"{type(bound_magnitude).__name__}. An activation with no declared "
            f"magnitude is an unbounded activation, which is the compulsion "
            f"shape QL5 refuses.")
    if bound_magnitude <= 0:
        raise UnboundedActivation(
            f"bound_magnitude must be positive, got {bound_magnitude}. A "
            f"non-positive bound is either already met at the moment of opening "
            f"or never met at all, and neither is a bound.")


# =====================================================================
# THE RECORDS - frozen, append-only, OPEN and CLOSE deliberately SEPARATE
# =====================================================================

def _ids(value: Any, label: str) -> Tuple[str, ...]:
    """A tuple of recorded ids. IDS-ONLY, never validated against any store.

    RULING 61'S `claim_refs` SEMANTICS VERBATIM, carried through Ruling 72: this
    layer does not open another owner's store to check that a cited record
    exists. **The join is the caller's.** A close that refused to record because
    some other file was unavailable would leave an episode of attention open
    forever over a filesystem problem.
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
class GoalActivation:
    """ONE bounded episode of attention: opened, against what, and held to what.

    **THE BOUND IS FIXED AT OPEN AND FOREVER.** There is no `extend`, no
    `rebound`, no `retarget` and no `amend` - not on this record and not on the
    layer. THE ABSENCE IS THE ENFORCEMENT and it is pinned as SHAPE. A bound
    that can be raised once it is nearly met is not a bound; it is a formality
    that documents how long attention happened to last, which is precisely the
    rewritability Ruling 61 abolished one layer up and Ruling 72 abolished at
    the commitment.

    `examination_id` IS THE AUTHORIZATION, not a decoration: an activation
    exists because a deterministic selector selected this goal, and the record
    carries the join back to that selection so the whole chain is auditable
    (Ruling 71 layer 2).
    """

    activation_id: str
    goal_id: str
    # The AUTHORIZING examination. See `ActivationLayer.open_activation` - there
    # is no path that opens on a bare goal id.
    examination_id: str
    bound_kind: BoundKind
    bound_magnitude: int
    opened_at: str = ""

    def __post_init__(self) -> None:
        _validate_bound(self.bound_kind, self.bound_magnitude)
        for name in ("activation_id", "goal_id", "examination_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"GoalActivation.{name} must be a non-empty id string. An "
                    f"activation that cannot name what it acts on, or what "
                    f"authorized it, is a record nobody can recompute.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "activation",
            "activation_id": self.activation_id,
            "goal_id": self.goal_id,
            "examination_id": self.examination_id,
            "bound_kind": self.bound_kind.value,
            "bound_magnitude": self.bound_magnitude,
            "opened_at": self.opened_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["GoalActivation"]:
        """Rebuild from a log line, or `None` if unreadable.

        A `bound_kind` outside the closed vocabulary is NOT coerced and NOT
        defaulted - the line is dropped. A forensic record outlives the code
        that wrote it, and reading an unknown bound as a known one would tell a
        later reader she was held to something she was not.
        """
        try:
            bound_kind = BoundKind(data["bound_kind"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(
                activation_id=str(data["activation_id"]),
                goal_id=str(data["goal_id"]),
                examination_id=str(data["examination_id"]),
                bound_kind=bound_kind,
                bound_magnitude=data["bound_magnitude"],
                opened_at=str(data.get("opened_at", "")),
            )
        except (KeyError, ValueError, TypeError, UnboundedActivation):
            return None


@dataclass(frozen=True)
class ActivationClose:
    """HOW an episode ended. **A SEPARATE APPEND - the open is never rewritten.**

    THE STRUCTURAL HEART, and it is Ruling 61's shape carried down one layer:
    the activation line stays byte-identical forever, so the log reads as a
    HISTORY (what was opened and under what bound, then what ended it) rather
    than a STATE (what we now say the episode was). An in-place update would be
    indistinguishable, afterwards, from having declared the right bound all
    along.

    **THIS SEPARATION IS ALSO WHAT MAKES CRASH HONESTY FREE.** Status is derived
    from the presence of a close, so an activation whose process died mid-episode
    reads as OPEN - which is exactly what it was. That is the derivation working,
    not a repair case to detect and clean up.
    """

    activation_id: str
    stop_condition: StopCondition
    # IDS-ONLY, never validated. See `_ids`.
    closing_basis_ids: Tuple[str, ...] = ()
    closed_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.stop_condition, StopCondition):
            raise TypeError(
                f"ActivationClose.stop_condition must be a StopCondition, got "
                f"{type(self.stop_condition).__name__}. QL5's stop set is "
                f"closed; a raw value would let a caller invent a way for "
                f"attention to end.")
        object.__setattr__(
            self, "closing_basis_ids",
            _deep_freeze(copy.deepcopy(
                _ids(self.closing_basis_ids, "closing_basis_ids"))))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "activation_close",
            "activation_id": self.activation_id,
            "stop_condition": self.stop_condition.value,
            "closing_basis_ids": list(self.closing_basis_ids),
            "closed_at": self.closed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["ActivationClose"]:
        try:
            stop = StopCondition(data["stop_condition"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(
                activation_id=str(data["activation_id"]),
                stop_condition=stop,
                closing_basis_ids=tuple(data.get("closing_basis_ids") or ()),
                closed_at=str(data.get("closed_at", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


ActivationEntry = Union[GoalActivation, ActivationClose]


# =====================================================================
# THE LAYER
# =====================================================================

class ActivationLayer:
    """Opens, bounds, measures and closes episodes of directed attention.

    READ-SIDE PURE with respect to every other store: it holds an injected
    arbiter and never writes to it or to the goal ledger. Its only write is its
    own append-only log.

    **THE ARBITER IS THE ONLY COLLABORATOR, AND THAT IS THE SCOPE ENFORCEMENT**
    (Ruling 70's move). Handed an `AureaCore` this layer would hold the Codex,
    the scar store and SAE and be TRUSTED not to touch them. Handed an arbiter
    it holds a way to read selections and measure focus, and nothing else.
    """

    ID_PREFIX = "ACT-"

    def __init__(self, arbiter,
                 log_path: str = "data/runtime/logs/goal_activations.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the same commit.
        self.arbiter = arbiter
        self.log_path = Path(log_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the log: the file
        # is the log. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal. Every mint derives from the
        # file under the file's lock.

    # -----------------------------------------------------------------
    # THE MINT - Ruling 69's shared helper, FOURTH consumer
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `ACT-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's whole property set inherits at a new prefix: derived at the
        moment of minting, RAW-TEXT scanned so an ordinal on a torn or
        unparseable line is still seen and never reissued, and Ruling 53's
        sentinel intact - `None` IFF the log EXISTS and the read raised, a
        MISSING log a legitimate `0`.
        """
        return derive_max_ordinal(self.log_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Callers hold `mint_lock`.

        UNDERIVED, IT RAISES rather than falling back to a number: two
        activations wearing one id are two episodes of attention nobody can tell
        apart, and the close that ends one would be ambiguous between them
        forever.
        """
        seq = self._derive_seq()
        if seq is None:
            raise ActivationLogUnreadable(
                f"the activation log at '{self.log_path}' exists and cannot be "
                f"read, so the next ACT ordinal is UNKNOWN. Minting one anyway "
                f"could write an id that already names a different episode of "
                f"attention.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module, and it targets only its own log.

        Batch 66's writer discipline: the validator runs BEFORE `mkdir` and
        BEFORE `open`, so a refused entry leaves no file and no directory;
        `allow_nan=False`; and there is NO `default=`, so a non-canonical leaf
        REFUSES rather than being silently stringified into a permanent record.

        Mode `"a"` is the only write mode in this file - which is what makes an
        open unrewritable in fact rather than by convention.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim): a
        torn APPEND damages one line, which the floor semantics already drop; a
        torn SNAPSHOT destroys the prior state.
        """
        validate_record_value(payload, path="activation_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    # -----------------------------------------------------------------
    # OPEN - authorized by an EXAMINATION, deterministically (res.5)
    # -----------------------------------------------------------------

    def open_activation(self, examination: GoalExamination,
                        bound_kind: BoundKind,
                        bound_magnitude: int) -> GoalActivation:
        """Open a bounded episode against the goal this examination selected.

        **AUTHORIZATION IS THE EXAMINATION, AND THERE IS NO OTHER DOOR**
        (res.5 - Ruling 71 layer 2 landing). This takes the arbiter's OUTPUT, a
        `GoalExamination`; there is no overload, no keyword and no helper that
        opens on a bare goal id. **The goal is READ OFF the examination**, never
        supplied alongside it, so an activation cannot name a goal the selector
        did not select. Same examination and same state yield the same outcome,
        and there is nothing to permute - the examination IS the selection.

        **EVERY REFUSAL PRECEDES THE MINT**, Ruling 24's pre-flight boundary as
        Ruling 46 read it: a refused open spends no ordinal, writes no line, and
        creates no file. In order:

          * a non-`GoalExamination` argument - the type gate IS res.5;
          * an unbounded, non-positive or unknown-kind bound
            (`UnboundedActivation`);
          * SERIAL ATTENTION - a second open for a goal whose prior activation
            is still open. **One episode at a time, per goal.** Two concurrent
            activations against one commitment would make "how long has this
            been attended, and under what bound" unanswerable, which is the one
            question the log exists to answer;
          * ONE EXAMINATION AUTHORIZES AT MOST ONE ACTIVATION. Re-using an
            examination would let one selection justify unbounded re-entry -
            the bound defeated not by raising it but by opening again.

        **THERE IS NO GUARD FOR AN `EXTERNAL_TASK` OR `CAPABILITY_ACQUISITION`
        ACTIVATION, AND THAT IS DELIBERATE** (res.5). Those kinds are
        UNPRODUCIBLE UPSTREAM (QL3, Ruling 72 - `GoalLedger._commit` refuses
        them), so no such commitment can exist to be selected, examined, or
        activated. The property is pinned over the COMPOSITION rather than
        re-enforced here: **a guard for an unreachable case is coined
        machinery**, and it would also quietly assert that this layer is the
        thing standing between her and world agency, which it is not.
        """
        if not isinstance(examination, GoalExamination):
            raise TypeError(
                f"open_activation takes a GoalExamination, got "
                f"{type(examination).__name__}. An activation is AUTHORIZED by "
                f"a recorded selection; there is no path that opens on a bare "
                f"goal id, because that path would let attention be directed by "
                f"something other than the deterministic selector.")

        _validate_bound(bound_kind, bound_magnitude)

        goal_id = examination.selected_goal_id

        standing = self.open_activation_for(goal_id)
        if standing is not None:
            raise ValueError(
                f"'{goal_id}' already has an open activation "
                f"({standing.activation_id}), so a second episode may not "
                f"begin. Attention is SERIAL per goal: two open episodes make "
                f"'how long has this been attended, and under what bound' "
                f"unanswerable. Close the standing one first.")

        existing = self.activation_for_examination(examination.examination_id)
        if existing is not None:
            raise ValueError(
                f"examination '{examination.examination_id}' already authorized "
                f"activation {existing.activation_id}. ONE EXAMINATION "
                f"AUTHORIZES AT MOST ONE ACTIVATION - re-using one would let a "
                f"single selection justify unbounded re-entry, defeating the "
                f"bound by opening again rather than by raising it.")

        with mint_lock(self.log_path):
            activation = GoalActivation(
                activation_id=self._next_id(),
                goal_id=goal_id,
                examination_id=examination.examination_id,
                bound_kind=bound_kind,
                bound_magnitude=bound_magnitude,
                opened_at=datetime.now().isoformat(),
            )
            self._append(activation.as_dict())
        return activation

    # -----------------------------------------------------------------
    # CLOSE - a SEPARATE append, by a member of the closed stop set
    # -----------------------------------------------------------------

    def close_activation(self, activation_id: str,
                         stop_condition: StopCondition,
                         closing_basis_ids: Any = ()) -> ActivationClose:
        """End an episode, naming the stop that ended it.

        THREE REFUSALS, each enforced AT THE WRITE rather than trusted at the
        read (Ruling 61 res.3's shape, whose reasons transfer intact):

          * a stop condition that is UNPRODUCIBLE
            (`UnproducibleStopCondition`) - today, AUTHORITY_DENIAL;
          * an UNKNOWN activation id - there is nothing to close;
          * a SECOND close - an episode ends ONCE, and a re-close is a second
            account of the same event with nothing to choose between them.

        **THE VOCABULARY REFUSAL IS CHECKED FIRST, AND THE ORDER IS A RULING'S
        WORTH OF REASONING IN ONE LINE** (Ruling 51's form: an engine fact
        precedes a request fact). That a stop condition has no substrate in this
        system is a permanent structural fact about the tree; that an id is
        unknown is a transient fact about one call. A caller who gets the
        structural answer learns something that will still be true tomorrow.

        **THE STOP IS NEVER DERIVED AND NEVER AUTOMATIC.** Even `BOUND_REACHED`
        is recorded because a caller looked at `bound_met` and decided to close -
        nothing here closes an episode on its own, because a layer that closed
        its own episodes would be a layer that runs.
        """
        if not isinstance(stop_condition, StopCondition):
            raise TypeError(
                f"stop_condition must be a StopCondition, got "
                f"{type(stop_condition).__name__}. QL5's stop set is closed.")

        if stop_condition in UNPRODUCIBLE_STOPS:
            raise UnproducibleStopCondition(
                f"'{stop_condition.value}' is VACUOUS BY SUBSTRATE: no "
                f"authorization surface exists in this system that could deny "
                f"anything, so nothing could honestly have produced this stop. "
                f"The member exists so that QL5's vocabulary is closed NOW and "
                f"the barrier lifts BY RULING. REOPENING CONDITION: a ruled "
                f"authorization surface.")

        activation = self.activation_for(activation_id)
        if activation is None:
            raise ValueError(
                f"no activation '{activation_id}' is recorded in this log. A "
                f"close ends an episode that was opened before it; there is "
                f"nothing here to end.")

        if self.close_for(activation_id) is not None:
            existing = self.close_for(activation_id)
            raise ValueError(
                f"'{activation_id}' is already closed on "
                f"{existing.stop_condition.value}. An episode ends ONCE; a "
                f"second close is a second account of one event, and the log "
                f"could never afterwards say which was true.")

        close = ActivationClose(
            activation_id=activation_id,
            stop_condition=stop_condition,
            closing_basis_ids=closing_basis_ids,
            closed_at=datetime.now().isoformat(),
        )
        self._append(close.as_dict())
        return close

    # -----------------------------------------------------------------
    # THE BOUND, DERIVED - it REPORTS. Nothing here acts on it.
    # -----------------------------------------------------------------

    def bound_met(self, activation: GoalActivation) -> bool:
        """Has this activation's DECLARED bound been reached?

        A PURE DERIVATION over the examination log and the activation's own
        declared bound. **NO MODULE CONSTANT PARTICIPATES** - the only magnitude
        in the comparison is `activation.bound_magnitude`, which the opener
        declared and the record carries. There is no numeric literal in this
        method or in either helper it calls.

        **IT REPORTS AND NOTHING MORE.** No caller inside `src/` consults it, no
        close follows from it automatically, and returning `True` changes
        nothing anywhere - a bound that is met is a fact an external caller may
        act on by recording a close. §9's standing bar survives at the one layer
        where crossing it would feel most natural.

        BOTH KINDS READ APPEND ORDER, NEVER A CLOCK. `examinations()` is
        documented as append-ordered and `focus_persistence` already counts back
        through it, so the two bound kinds share one ordering rather than
        introducing a second.

        **AN UNMEASURABLE BOUND REPORTS `False`, WHICH LEAVES THE EPISODE OPEN
        AND VISIBLE.** If the authorizing examination is not in the log the
        derivation cannot be made, and the conservative direction is the legible
        one: an activation that stays open is on the record and closeable by
        another stop, whereas one that reported its bound met would invite a
        close that nothing supports.
        """
        if activation.bound_kind is BoundKind.EXAMINATION_BOUND:
            return self._further_examinations(activation) >= activation.bound_magnitude
        return self._no_progress_run(activation) >= activation.bound_magnitude

    def _further_examinations(self, activation: GoalActivation) -> int:
        """How many examinations selected this goal AFTER the authorizing one.

        Counted in APPEND ORDER from the position of the authorizing
        examination. The authorizing examination itself is NOT counted - it is
        what opened the episode, not attention paid during it, and counting it
        would make a bound of N behave as N-1 for every activation ever opened.
        """
        examinations = self.arbiter.examinations()
        seen = False
        further = 0
        for examination in examinations:
            if seen and examination.selected_goal_id == activation.goal_id:
                further += 1
            if examination.examination_id == activation.examination_id:
                seen = True
        return further if seen else 0

    def _no_progress_run(self, activation: GoalActivation) -> int:
        """The consecutive-selection run for this goal, IF nothing has moved.

        `focus_persistence` is the substrate, exactly as res.3 registers it.
        **PROGRESS RESETS THE ANSWER TO ZERO** rather than merely failing the
        comparison: a goal that received evidence during its run is a goal that
        moved, and reporting a long unproductive run for it would be false.
        """
        persistence = self.arbiter.focus_persistence(activation.goal_id)
        if persistence.progress_recorded:
            return 0
        return persistence.consecutive_selections

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> Tuple[ActivationEntry, ...]:
        """Every readable entry, IN APPEND ORDER. The history, as written.

        Reads the FILE rather than `self.entries`: the log spans processes and
        the in-memory mirror does not - which is what makes the crash case
        answerable at all. A line that will not parse, that carries an unknown
        record kind, or that carries a value outside a closed vocabulary
        contributes NOTHING; it is never coerced.

        **AN UNREADABLE EXISTING LOG RAISES THE TYPED ERROR, AND THIS IS RULING
        53'S LAW GENERALIZED FROM THE MINT TO EVERY DERIVATION OVER THE SAME
        FILE.** It was found by a pin rather than by design: the shared mint
        battery asserts that every ledger refuses TYPED when its file exists and
        cannot be read, and this layer answered with a bare `OSError` - because
        `open_activation`'s guards read the log BEFORE the mint is reached, so
        the read failed a frame above the only place that knew how to name it.

        Silently returning `()` would have been far worse than the `OSError`:
        every derivation in this layer is computed from this file, so an empty
        read makes `is_open` answer TRUE, `open_activation_for` answer None, and
        the serial-attention guard wave through a second episode - **"I could
        not look" rendered as "there is nothing there", which is Docket H's
        two-absences cut at a guard.** A bare `OSError`, meanwhile, is Ruling
        25's shape: a structural refusal wearing a disk hiccup's clothes, which
        any caller's `except OSError` would swallow.

        A MISSING file stays a legitimate empty history - absence is a first
        run, not a fault - which is `derive_max_ordinal`'s own distinction,
        preserved exactly.

            **A LATENT EQUIVALENT IS REPORTED, NOT FIXED HERE:**
            `GoalArbiter.examinations()` lets an `OSError` propagate the same
            way, and its own battery row passes only because a single-commitment
            fixture returns at `SOLE_CANDIDATE` before `_context()` ever reads
            the log. With two or more candidates it would raise bare. That is
            Ruling 73's file and its own ruling's to close.
        """
        if not self.log_path.exists():
            return ()
        out: List[ActivationEntry] = []
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise ActivationLogUnreadable(
                f"the activation log at '{self.log_path}' exists and cannot be "
                f"read, so no fact about any episode of attention can be "
                f"derived from it - not whether one is open, not whether this "
                f"goal is already being attended to, and not which examination "
                f"authorized what. Answering any of those from an empty read "
                f"would report 'nothing is there' when the truth is 'I could "
                f"not look'.") from failure
        with handle:
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
                if record_kind == "activation":
                    entry = GoalActivation.from_dict(data)
                elif record_kind == "activation_close":
                    entry = ActivationClose.from_dict(data)
                else:
                    continue
                if entry is not None:
                    out.append(entry)
        return tuple(out)

    def activations(self) -> Tuple[GoalActivation, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, GoalActivation))

    def closes(self) -> Tuple[ActivationClose, ...]:
        return tuple(e for e in self.read_all()
                     if isinstance(e, ActivationClose))

    def activation_for(self, activation_id: str) -> Optional[GoalActivation]:
        for entry in self.activations():
            if entry.activation_id == activation_id:
                return entry
        return None

    def activation_for_examination(self,
                                   examination_id: str
                                   ) -> Optional[GoalActivation]:
        """The activation an examination authorized, if it authorized one."""
        for entry in self.activations():
            if entry.examination_id == examination_id:
                return entry
        return None

    def close_for(self, activation_id: str) -> Optional[ActivationClose]:
        for entry in self.closes():
            if entry.activation_id == activation_id:
                return entry
        return None

    def activations_for(self, goal_id: str) -> Tuple[GoalActivation, ...]:
        return tuple(e for e in self.activations() if e.goal_id == goal_id)

    # -----------------------------------------------------------------
    # STATUS - DERIVED, never stored (L3)
    # -----------------------------------------------------------------

    def is_open(self, activation_id: str) -> bool:
        """Is this episode still open? **DERIVED, NEVER STORED, NEVER CACHED.**

        AN ACTIVATION WITH NO CLOSE RECORD IS OPEN. That is the whole rule, and
        it is why no record carries a status field (L3, AST-pinned): a stored
        status is a second writer of what the appends already determine, and the
        field is the one people read while the facts are the one that is true -
        Ruling 63's cached-projection refusal and Ruling 65's stored-derivation
        refusal, both of which this house has already paid for.

        **CRASH HONESTY IS THIS DERIVATION WORKING, NOT A REPAIR CASE.** A
        process that dies mid-episode leaves an activation line and no close
        line, and a fresh instance reads that as OPEN - which is what it was.
        There is nothing to detect, reconcile or clean up, and any machinery
        that did so would be deciding on her behalf that an interrupted episode
        had ended.

        **THERE IS DELIBERATELY NO `ActivationStatus` ENUM** (a judgment call,
        recorded). Ruling 74 res.8 names exactly two coined vocabularies, and
        open-versus-closed is a single recorded fact rather than a vocabulary -
        `GoalStatus` earned its enum by having four members derived from
        different evidence. Coining a two-member enum for a predicate would be
        adding structure the ruling did not declare.
        """
        if self.activation_for(activation_id) is None:
            raise ValueError(
                f"no activation '{activation_id}' is recorded in this log; "
                f"there is no status to derive.")
        return self.close_for(activation_id) is None

    def open_activation_for(self, goal_id: str) -> Optional[GoalActivation]:
        """The goal's currently-open episode, if it has one.

        The serial-attention guard's own reader, and the answer to "is she
        attending to this right now". Derived from the absence of a close.
        """
        for entry in self.activations_for(goal_id):
            if self.close_for(entry.activation_id) is None:
                return entry
        return None

    def open_activations(self) -> Tuple[GoalActivation, ...]:
        """Every episode still open. Empty is the healthy resting state."""
        return tuple(e for e in self.activations()
                     if self.close_for(e.activation_id) is None)


# =====================================================================
# THE DRIVE PRODUCER - NOT BUILT (res.7), Ruling 62's conjunction form
# =====================================================================
#
# Ruling 72 recorded that `GoalProvenance.INTERNAL_DRIVE` has NO LEGITIMATE
# PRODUCER and named Q3's drive wiring as its first one. **THIS IS Q3, AND THE
# PRODUCER IS STILL NOT BUILT** - deliberately, and the reason is on the record
# rather than deferred by silence.
#
# **A DRIVE PRODUCER AT THIS ERA HAS NOTHING HONEST TO PRODUCE.** A goal's
# `desired_state` is its whole direction. Deriving one from templates over
# existing records would FABRICATE INTENTION - text that reads like something
# she wants, assembled by string composition from things she merely holds - and
# the record would be indistinguishable afterwards from a direction she actually
# formed. That is L3's fabrication class at the one field where it would matter
# most. Generative content machinery is the other candidate source and is
# UNRULED; the Foundry's future capability rulings are where it would come from.
#
# **REOPENING IS A CONJUNCTION, and neither half is optional** (Ruling 62's
# form, and the interlock is the point):
#
#     the activation layer exists   -- SATISFIED BY THIS RULING
#     AND a ruled content source exists   -- NOT SATISFIED
#
# Until both hold, an `INTERNAL_DRIVE` record appearing in the goal ledger
# remains a FINDING rather than a permitted state, exactly as Ruling 72 wrote
# it. This note is the migration target of that finding-condition.
