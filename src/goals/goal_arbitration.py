"""
goal_arbitration.py - RULING 73 / DOCKET Q item Q2: GOAL ARBITRATION.

    The selector selects and records. It closes nothing, grants nothing,
    and draws nothing.

Given the goal ledger's standing commitments, this module deterministically
selects which ONE receives inquiry attention, and records the examination.

THREE THINGS IT IS NOT, each enforced rather than promised
-------------------------------------------------------------------------------
  * IT NEVER CLOSES A COMMITMENT. Closure is RESOLUTION, a goal-ledger append.
    This module contains no call to `resolve`, `record_evidence`, `commit`,
    `_commit` or `ensure_genesis` on any receiver, and defines no method named
    `commit` - **Ruling 72's lesson applied IN ADVANCE rather than discovered by
    a firing invariant.** Ruling 5's scanner refuses receiver inference, and it
    is right to; a selector that could close a goal would be able to declare its
    own work finished.
  * IT GRANTS NOTHING (QL0). Selection is attention, not authority. Nothing here
    authorizes an action, and the import list makes the machinery an authority
    would need unreachable.
  * IT DRAWS NOTHING (Ruling 71). Selection is DETERMINISTIC: identical state
    yields an identical selection, and the selection is invariant under the
    order candidates arrive in. No `random`, no `secrets`, no sampling anywhere -
    **a stochastic selector biases what the system can come to know, invisibly**,
    which is the class BAR §3 exists to bar and Ruling 71 extended to goals.

WHAT IT WRITES: exactly one store of its own, the examination log. It reads the
goal ledger through an INJECTED instance and writes nothing to it.

    THE INJECTION SHAPE IS A JUDGMENT CALL, AND THE ALTERNATIVE IS NAMED. The
    ruling says "an injected instance"; a NARROWED read surface would be
    stronger in Ruling 70's sense (the arbiter would hold no write methods at
    all rather than being scanned for not calling them). It was not built,
    because inventing an adapter type the ruling did not name would be coining
    structure, and res.2 supplies its own enforcement for exactly this hazard.
    Reopening: a ruling that names a read-surface protocol for the ledger.

THE LADDER IS RULING 71'S, APPLIED AS WRITTEN - INCLUDING WHERE IT HAS NO FLOOR
-------------------------------------------------------------------------------
Two of the five rungs have NO SUBSTRATE in the Q1 records: `GoalCommitment`
carries no dependency field and no review-horizon field. **A ladder ruled over
fields that do not exist must either tie through honestly or be silently
rewritten, and this module does the first.** The vacuous rungs are PRESENT as
shape - Rulings 63/64's unproducible-member form applied to a sort key: the
vocabulary is closed now and the substrate lifts by ruling, rather than the
ladder quietly becoming a different ladder than the one that was ruled.

~~**REPORTED DIVERGENCE - READ THIS BEFORE CHANGING A RUNG.** Rung 2 keys on the
GLC ordinal, which is UNIQUE per commitment, so with two or more candidates it
always yields a unique leader. Rungs 3, 4 and 5 are therefore UNREACHABLE
today - not vacuous-by-substrate like rungs 1 and 3, but unreachable by rung 2's
totality. This is measured, not argued (see `tests/test_ruling73.py`), and it is
reported to the board rather than repaired here: repairing it means deciding
what "oldest unresolved" keys on, which is a semantic decision this pass does
not own. **The consequence is that a standing goal is selected persistently
rather than in rotation** - which is precisely the condition `focus_persistence`
below exists to measure, and which QL5's `no-progress` stop condition is the
registered consumer of.~~

**SUPERSEDED 2026-08-03 BY RULING 73-A, kept above VERBATIM as the record of
what was measured and of the order that produced it.** The struck paragraph is
history, not an error to delete: it is the finding that forced this rider, and
the strict-xfail witness it left behind is what MEASURED the correction rather
than asserting it.

    THE OLD ORDER, recorded so the change is legible:
        UNMET_DEPENDENCY -> OLDEST_UNRESOLVED -> REVIEW_HORIZON
        -> LEAST_RECENTLY_EXAMINED -> STABLE_IDENTIFIER

**RULING 73-A: THE LADDER REORDERS. `LEAST_RECENTLY_EXAMINED` MOVES AHEAD OF
`OLDEST_UNRESOLVED`.** The board ruled the fork NOT GENUINE: with two
STRUCTURALLY UNRESOLVABLE roots, persistent focus starves RG-2 permanently, and
it does so **on MINT ORDER - adjudication by list order, the exact class
Ruling 64 res.5 refused.** Three pieces of intent converge against it: pin (f)
ruled alternation, the liveness derivation exists to surface sustained focus
WITHOUT progress, and two unresolvable roots make persistence permanent rather
than temporary.

**RECENCY ROTATION IS THE WORKING ALLOCATOR** among standing commitments;
**OLDEST_UNRESOLVED IS THE DETERMINISTIC BREAKER** among equally-recently-
examined candidates - including the all-never-examined GENESIS case, where it
decides the FIRST selection. So the recorded bases are now honest: the genesis
selection records OLDEST_UNRESOLVED, and every rotation afterwards records
LEAST_RECENTLY_EXAMINED.

`DecidingBasis`'s MEMBER SET IS UNCHANGED - only `LADDER`'s order moved.

**THE VACUOUS RUNGS KEEP THEIR REGISTERED RELATIVE ORDER, AND THEIR POSITIONS
CARRY A STATED CONDITION:** each future field ruling (the dependency field; the
review-horizon field) RE-CONFIRMS OR MOVES ITS OWN RUNG when the substrate
arrives. A rung that ties through today has never been tested in competition,
so its position is provisional in a way a deciding rung's is not.

**RUNG 4 IS TOTAL BY CONSTRUCTION, SO RUNG 5 IS A DECLARED BACKSTOP** -
unreachable while GLC ordinals parse and remain unique. Its remedy class
DIFFERS from the vacuous rungs': they await a missing FIELD, while rung 5
guards a future ID MALFORMATION. It is pinned as DECLARED-UNREACHABLE and is
never falsely pinned as deciding cases.

DECLARED OUT, each owned
-------------------------------------------------------------------------------
  * DRIVE WIRING and ACTIVATION RECORDS -> Q3 (QL5's shape). Nothing in `src/`
    consumes this module, and the no-consumer pin reddens the day one does.
  * AUTHORIZATION determinism pins -> Ruling 71 layer 2, landing with Q3.
  * LEVEL-BASED PRECEDENCE CLASSES -> a future arbitration ruling. The ladder is
    LEVEL-BLIND today: the ledger stores `level` and does not police it
    (Ruling 72), and this module does not read it.
  * THE DEPENDENCY FIELD and THE REVIEW-HORIZON FIELD -> each its own ruling,
    named at the vacuous rungs below.
  * ADOPTION-GATED CANDIDACY -> the adoption-era ruling; see `candidates`.
  * CONSEQUENCE MODELLING of any kind -> SAE owns simulation. No simulation
    machinery exists here and its absence is pinned.

COINS: the `DecidingBasis` vocabulary and the `EXM-` prefix. Nothing else - no
threshold, no weight, no score, and no priority field on any record (QL4).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from src.goals.goal_ledger import GoalCommitment, GoalStatus
from src.utils.ledger_mint import derive_max_ordinal, mint_lock, ordinal_pattern
from src.utils.record_value import validate_record_value


class DecidingBasis(str, Enum):
    """WHY this candidate and not another. CLOSED, and COINED by Ruling 73.

    **THE RECORDED BASIS BESIDE A DERIVED OUTPUT** - Ruling 63's own form. The
    selection is recomputable from the records, and the basis says which rung
    made it unique, so a reader learns not merely what was chosen but what
    decided it.

    THERE IS NO PER-CANDIDATE VERDICT VOCABULARY, deliberately. A non-selected
    candidate's standing is DERIVABLE from the same records, and storing it
    would be storing a derivation (L3, fourth application at this layer).

    **THE WORD `DEFER` APPEARS NOWHERE IN THIS MODULE, AND THAT IS A RULING.**
    Docket Q's registration described the capability as "focus, hold, or defer",
    and a tree-wide census found `DEFERRED` live in `racm.Verdict` with
    `_defer` / `is_deferred` / `deferred_cycles` throughout `racm.py`. That
    vocabulary is RACM's. The registration's "defer" sense here is simply
    EXCLUSION AT A RUNG, which the basis already reports.

    FOCUS is the selection itself. HOLD is re-selection of the same commitment
    across consecutive examinations - DERIVABLE by comparing records, never
    stored.
    """

    # Only one candidate stood; the ladder never ran.
    SOLE_CANDIDATE = "sole_candidate"
    # Ruling 71's five rungs, in the order it declared them.
    UNMET_DEPENDENCY = "unmet_dependency"
    OLDEST_UNRESOLVED = "oldest_unresolved"
    REVIEW_HORIZON = "review_horizon"
    LEAST_RECENTLY_EXAMINED = "least_recently_examined"
    STABLE_IDENTIFIER = "stable_identifier"


# =====================================================================
# THE RECORDS
# =====================================================================

@dataclass(frozen=True)
class GoalExamination:
    """ONE examination: who was considered, who was selected, and what decided.

    Frozen and append-only. An examination is a record of an event that
    happened; editing one would make the selector's own history rewritable,
    which is the defect QL1 abolishes one layer up.

    IT CARRIES NO OUTCOME AND NO AUTHORITY. Selecting a goal for attention is
    not pursuing it, not adopting it, and not resolving it.
    """

    examination_id: str
    selected_goal_id: str
    # The FULL candidate set at selection time, ids only, in the order the
    # ladder considered them (which is deterministic - see `_ordered`).
    candidate_goal_ids: Tuple[str, ...]
    deciding_basis: DecidingBasis
    recorded_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.deciding_basis, DecidingBasis):
            raise TypeError(
                f"GoalExamination.deciding_basis must be a DecidingBasis, got "
                f"{type(self.deciding_basis).__name__}.")
        if not isinstance(self.selected_goal_id, str) or not self.selected_goal_id:
            raise ValueError(
                "an examination records the goal it selected; there is no "
                "examination without a selection.")
        for item in self.candidate_goal_ids:
            if not isinstance(item, str):
                raise TypeError(
                    "candidate_goal_ids carries ID STRINGS ONLY - a live "
                    "commitment object here would be a handle into another "
                    "owner's store (Ruling 42).")
        if self.selected_goal_id not in self.candidate_goal_ids:
            raise ValueError(
                f"'{self.selected_goal_id}' is not among the recorded "
                f"candidates. A selection that is not in its own candidate set "
                f"is a record nobody can recompute.")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "examination",
            "examination_id": self.examination_id,
            "selected_goal_id": self.selected_goal_id,
            "candidate_goal_ids": list(self.candidate_goal_ids),
            "deciding_basis": self.deciding_basis.value,
            "recorded_at": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["GoalExamination"]:
        """Rebuild from a log line, or `None` if unreadable.

        A `deciding_basis` outside the closed vocabulary is NOT coerced and NOT
        defaulted - the line is dropped. A forensic record outlives the code
        that wrote it, and reading an unknown basis as a known one would put a
        fact in the reader's hands that the writer never recorded.
        """
        try:
            basis = DecidingBasis(data["deciding_basis"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(
                examination_id=str(data["examination_id"]),
                selected_goal_id=str(data["selected_goal_id"]),
                candidate_goal_ids=tuple(data.get("candidate_goal_ids") or ()),
                deciding_basis=basis,
                recorded_at=str(data.get("recorded_at", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class FocusPersistence:
    """THE LIVENESS MEASUREMENT - register item 17, the Q2 half.

    **A GENUINE TALLY, WITH NO THRESHOLD, NO GATE AND NO VERDICT.** A count
    reports; it never gates (§9 standing bar #5). Nothing in this module
    compares either field to anything, and the count-never-gates scan holds it.

    ENFORCEMENT IS Q3'S, through QL5's closed stop set - whose `no-progress` and
    `authority denial` members are already the registered consumers of exactly
    this derivation. Building the enforcement here would be this module
    deciding what to do about its own starved focus, which is the selector
    grading its own work.
    """

    goal_id: str
    # How many examinations, counting back from the most recent, selected this
    # goal without interruption.
    consecutive_selections: int
    # Whether ANY evidence or resolution was appended for this goal since the
    # first examination of that consecutive run.
    progress_recorded: bool


# =====================================================================
# THE LADDER - Ruling 71's declared tie-key order, as DECLARED DATA
# =====================================================================
#
# Each rung maps a candidate to a sort key. Lower sorts first. A rung NARROWS
# the field to those sharing the minimum key; the first rung that leaves exactly
# one candidate is the recorded basis.


def _rung_unmet_dependency(commitment: GoalCommitment,
                           context: "_LadderContext") -> Any:
    """RUNG 1 (unmoved by Ruling 73-A) - VACUOUS BY SUBSTRATE, present as SHAPE.

    **NO DEPENDENCY FIELD EXISTS ON ANY RECORD**, so this rung TIES ALL
    CANDIDATES - deterministically, which is what makes tying honest rather than
    arbitrary. It is not deleted, because Ruling 71 declared a five-rung ladder
    and a four-rung implementation would be a different ladder wearing the
    ruled one's name.

    REOPENING CONDITION: a ruled dependency field on `GoalCommitment`. On that
    day this body reads it and the rung starts discriminating. **THAT RULING
    ALSO RE-CONFIRMS OR MOVES THIS RUNG'S POSITION** (Ruling 73-A) - a rung
    that has only ever tied through has never been tested in competition.
    """
    return 0


def _rung_oldest_unresolved(commitment: GoalCommitment,
                            context: "_LadderContext") -> Any:
    """RUNG 4 (Ruling 73-A; was rung 2) - the GLC ordinal, ascending.
    File-derived and wall-clock-free.

    Parsed with Ruling 64's ANCHORED-PATTERN discipline rather than by slicing:
    `GLC-00010` must not read as `GLC-0001`, and a bare `\\b` is insufficient
    because `-` is itself a non-word character.

    **THE DETERMINISTIC BREAKER among equally-recently-examined candidates.**
    Its most important case is GENESIS: every candidate is never-examined, so
    rung 3 ties them all and this rung decides the FIRST selection.

    **THIS RUNG IS TOTAL, AND THAT IS NOW LOAD-BEARING RATHER THAN A DEFECT.**
    GLC ordinals are unique per commitment, so this always yields a unique
    leader - which is exactly what makes rung 5 a DECLARED BACKSTOP rather than
    a rung that decides cases. At rung 2 that totality made the ladder's whole
    tail unreachable; at rung 4 it is the guarantee that the ladder terminates.
    """
    return context.ordinal_of(commitment.goal_id)


def _rung_review_horizon(commitment: GoalCommitment,
                         context: "_LadderContext") -> Any:
    """RUNG 2 (Ruling 73-A; was rung 3) - VACUOUS BY SUBSTRATE, as rung 1.

    **NO REVIEW-HORIZON FIELD EXISTS.** Ties all candidates.

    REOPENING CONDITION: a ruled horizon field, adjacent to Ruling 61's horizon
    vocabulary - which deliberately refuses to interpret a horizon's FORMAT
    (a date, a cycle count, an observed condition), so the field's arrival has
    to decide that too. **THAT RULING ALSO RE-CONFIRMS OR MOVES THIS RUNG'S
    POSITION** (Ruling 73-A): a rung that has only ever tied through has never
    been tested in competition, so where it sits is provisional in a way a
    deciding rung's position is not.
    """
    return 0


def _rung_least_recently_examined(commitment: GoalCommitment,
                                  context: "_LadderContext") -> Any:
    """RUNG 3 (Ruling 73-A; was rung 4) - the goal's most recent EXM ordinal,
    ascending. **THE WORKING ALLOCATOR.**

    **A NEVER-EXAMINED GOAL SORTS FIRST**, because the least recently examined
    thing is the thing never examined. Wall-clock-free by construction: it
    compares mint ordinals, not timestamps.

    This is the rung that ROTATES attention among standing commitments, and
    Ruling 73-A moved it here for that reason: behind `OLDEST_UNRESOLVED` it
    was unreachable, and the consequence was permanent starvation of every
    commitment but the lowest-minted one - **starvation decided by MINT ORDER,
    which is adjudication by list order** (Ruling 64 res.5's refused class).

    It TIES at genesis, when every candidate is never-examined; rung 4 then
    breaks that tie deterministically.
    """
    return context.last_examination_ordinal.get(commitment.goal_id, -1)


def _rung_stable_identifier(commitment: GoalCommitment,
                            context: "_LadderContext") -> Any:
    """RUNG 5 (unmoved) - the GLC id string, ascending. **A DECLARED BACKSTOP.**

    Ids are unique, so this rung can never tie. It is what guarantees the ladder
    always selects rather than failing to decide - a selector that could return
    "no decision" would hand the question back to whoever called it, which is
    where nondeterminism gets in.

    **DECLARED UNREACHABLE, AND PINNED AS SUCH RATHER THAN AS A DECIDER**
    (Ruling 73-A). Rung 4 is TOTAL while GLC ordinals parse and remain unique,
    so nothing reaches here today. **Its remedy class DIFFERS from the vacuous
    rungs':** they await a missing FIELD, while this one guards a future ID
    MALFORMATION - an id `ordinal_of` cannot parse sorts to a shared sentinel,
    and if two such ids ever tied at rung 4 this rung would order them. Pinning
    it as a decider would mean constructing an id the mint cannot produce, so
    the pin asserts UNREACHABILITY instead of faking a case.
    """
    return commitment.goal_id


# RULING 73-A (2026-08-03): LEAST_RECENTLY_EXAMINED MOVED AHEAD OF
# OLDEST_UNRESOLVED. See the module docstring for the ruling and the old order.
# The two vacuous rungs keep their registered relative order.
LADDER: Tuple[Tuple[DecidingBasis, Callable[..., Any]], ...] = (
    (DecidingBasis.UNMET_DEPENDENCY, _rung_unmet_dependency),
    (DecidingBasis.REVIEW_HORIZON, _rung_review_horizon),
    (DecidingBasis.LEAST_RECENTLY_EXAMINED, _rung_least_recently_examined),
    (DecidingBasis.OLDEST_UNRESOLVED, _rung_oldest_unresolved),
    (DecidingBasis.STABLE_IDENTIFIER, _rung_stable_identifier),
)

# The derived statuses that make a commitment a candidate. Named ONCE so no
# second spelling can drift (Ruling 47's `CMTE_FAILURE_LABELS` shape).
CANDIDATE_STATUSES: Tuple[GoalStatus, ...] = (
    GoalStatus.COMMITTED,
    GoalStatus.EVIDENCE_BEARING,
)


@dataclass(frozen=True)
class _LadderContext:
    """Everything the rungs read, computed once per selection.

    Frozen and passed explicitly rather than reached through `self`, so a rung
    cannot quietly acquire a new input: whatever a rung reads is visible in this
    type.
    """

    goal_prefix: str
    last_examination_ordinal: Mapping[str, int]

    def ordinal_of(self, goal_id: str) -> int:
        """The GLC ordinal, by anchored match. An unparseable id sorts LAST.

        An id this module cannot parse is not guessed at and not crashed on: it
        loses every ordinal comparison and falls through to the stable-identifier
        backstop, which can always order it.
        """
        match = ordinal_pattern(self.goal_prefix).search(goal_id)
        return int(match.group(1)) if match else _UNPARSEABLE_ORDINAL


# Larger than any ordinal a ledger will mint in practice; an unparseable id
# sorts after every parseable one rather than before it.
_UNPARSEABLE_ORDINAL = 2 ** 62


@dataclass(frozen=True)
class Selection:
    """The pure result of running the ladder. RECOMPUTABLE, never stored."""

    selected_goal_id: str
    candidate_goal_ids: Tuple[str, ...]
    deciding_basis: DecidingBasis


class ExaminationLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived.

    Raised at the moment an id would be minted. Minting from an unknown floor
    could write an `EXM-` id that already names a different examination, and an
    append-only record cannot later disambiguate two lines wearing one id.
    """


class GoalArbiter:
    """Selects one standing commitment for attention, and records the choice.

    READ-SIDE PURE with respect to the goal ledger: it holds an injected ledger
    and never writes to it. Its only write is its own append-only log.
    """

    ID_PREFIX = "EXM-"

    def __init__(self, ledger,
                 log_path: str = "data/runtime/logs/goal_examinations.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the same commit.
        self.ledger = ledger
        self.log_path = Path(log_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the log: the file
        # is the log. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal. Every mint derives from the
        # file under the file's lock.

    # -----------------------------------------------------------------
    # THE MINT - Ruling 69's shared helper, THIRD consumer
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `EXM-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's whole property set inherits at a new prefix: derived at the
        moment of minting, RAW-TEXT scanned so an ordinal on a torn line is
        still seen and never reissued, and Ruling 53's sentinel intact - `None`
        IFF the log EXISTS and the read raised, a MISSING log a legitimate `0`.
        """
        return derive_max_ordinal(self.log_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Callers hold `mint_lock`.

        UNDERIVED, IT RAISES rather than falling back to a number: two
        examinations wearing one id are two selection histories nobody can tell
        apart, and the log is the only evidence that a selection was ever made.
        """
        seq = self._derive_seq()
        if seq is None:
            raise ExaminationLogUnreadable(
                f"the examination log at '{self.log_path}' exists and cannot "
                f"be read, so the next EXM ordinal is UNKNOWN. Minting one "
                f"anyway could write an id that already names a different "
                f"examination.")
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

        Mode `"a"` is the only write mode in this file.
        """
        validate_record_value(payload, path="examination_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    # -----------------------------------------------------------------
    # CANDIDACY - by DERIVATION, never by a stored flag
    # -----------------------------------------------------------------

    def candidates(self) -> Tuple[GoalCommitment, ...]:
        """The standing commitments, in GLC-id order.

        CANDIDACY IS DERIVED: a commitment stands iff `derive_status` puts it in
        `CANDIDATE_STATUSES`. Superseded and resolved commitments leave the set
        BY DERIVATION - no stored flag is read, and none exists to read
        (Ruling 72 res.4 / L3).

        **ADOPTION DOES NOT GATE CANDIDACY TODAY, AND THAT IS A RULING RATHER
        THAN AN OVERSIGHT.** Examination is neither pursuit nor adoption, and
        arbitration grants nothing (QL0). Gating on an adoption event that no
        machinery can produce (Ruling 72 res.6 - `GoalAdoption` has no producer
        path) would ship a selector with a structurally EMPTY domain: a vacuous
        build that passes its tests by never selecting anything.
        REOPENING CONDITION: whether adoption gates candidacy is the
        adoption-era ruling's to decide, once deliberation machinery exists.

        THE FILTER IS LEVEL-BLIND. The ledger stores `level` and does not police
        it (Ruling 72), and this module does not read it; level-based precedence
        classes are a future arbitration ruling.

        Returned in a DETERMINISTIC order so that nothing downstream depends on
        the ledger's file order (which is stable, but relying on it would make
        the guarantee accidental rather than stated).
        """
        standing = [c for c in self.ledger.commitments()
                    if self.ledger.derive_status(c.goal_id) in CANDIDATE_STATUSES]
        return tuple(sorted(standing, key=lambda c: c.goal_id))

    # -----------------------------------------------------------------
    # SELECTION - pure, deterministic, permutation-invariant
    # -----------------------------------------------------------------

    def _context(self) -> _LadderContext:
        last: Dict[str, int] = {}
        pattern = ordinal_pattern(self.ID_PREFIX)
        for examination in self.examinations():
            match = pattern.search(examination.examination_id)
            if match is None:
                continue
            ordinal = int(match.group(1))
            goal_id = examination.selected_goal_id
            if ordinal > last.get(goal_id, -1):
                last[goal_id] = ordinal
        return _LadderContext(
            goal_prefix=getattr(self.ledger, "ID_PREFIX", "GLC-"),
            last_examination_ordinal=last)

    def select(self) -> Optional[Selection]:
        """Run the ladder. PURE - it reads, decides, and writes NOTHING.

        Separated from `examine` deliberately: a selection that can be computed
        without recording one is a selection anyone can audit, and it is what
        makes the determinism pins measurable without accumulating log lines.

        **PERMUTATION-INVARIANT BY CONSTRUCTION** (Ruling 71): the candidate set
        is sorted before the ladder runs, and every rung's key is a function of
        the candidate alone, so input order cannot reach the outcome.

        Returns `None` when nothing stands - a legitimate state, not an error:
        every goal may be resolved or superseded.
        """
        candidates = self.candidates()
        if not candidates:
            return None

        ids = tuple(c.goal_id for c in candidates)
        if len(candidates) == 1:
            return Selection(selected_goal_id=candidates[0].goal_id,
                             candidate_goal_ids=ids,
                             deciding_basis=DecidingBasis.SOLE_CANDIDATE)

        context = self._context()
        remaining = list(candidates)
        for basis, rung in LADDER:
            keyed = [(rung(c, context), c) for c in remaining]
            best = min(k for k, _ in keyed)
            remaining = [c for k, c in keyed if k == best]
            if len(remaining) == 1:
                return Selection(selected_goal_id=remaining[0].goal_id,
                                 candidate_goal_ids=ids,
                                 deciding_basis=basis)

        # UNREACHABLE: rung 5 keys on unique ids and cannot tie. Raising rather
        # than picking is deliberate - if the backstop ever stops being a total
        # order, the right answer is a loud failure, not a quiet choice.
        raise RuntimeError(
            "the ladder exhausted every rung without selecting; the "
            "stable-identifier backstop is no longer a total order.")

    def examine(self) -> GoalExamination:
        """Select and RECORD. The one operation that writes.

        RAISES when nothing stands: an examination record carries a selected
        goal, so there is no honest examination of an empty field. The caller
        learns it by exception rather than holding a record of a choice that
        was never made.
        """
        with mint_lock(self.log_path):
            # RULING 75 res.7 - THE SELECTION MOVED INSIDE THE HOLD.
            #
            # `select()` used to run OUTSIDE this lock, so two concurrent
            # `examine()` calls could each compute a selection before either
            # appended - and both would select the SAME goal, because neither
            # could see the other's examination yet. Reported as an observation
            # at Ruling 74 (its mutex fixture had to deal pre-recorded
            # examinations to keep measuring the ACT mint rather than this
            # race); closed here, in its own file, as the ordered housekeeping.
            #
            # **DERIVE THROUGH APPEND UNDER ONE HOLD** is Ruling 69's own
            # discipline: the selection IS a derivation over this log, exactly
            # as the ordinal is, so it belongs inside the same hold rather than
            # beside it. `select()` stays PURE and publicly callable - what
            # moved is where `examine` calls it, not what it does.
            selection = self.select()
            if selection is None:
                raise ValueError(
                    "no commitment stands: every goal in the ledger is "
                    "resolved, superseded, or the ledger is empty. There is "
                    "nothing to examine, and an examination record carries a "
                    "selection.")

            examination = GoalExamination(
                examination_id=self._next_id(),
                selected_goal_id=selection.selected_goal_id,
                candidate_goal_ids=selection.candidate_goal_ids,
                deciding_basis=selection.deciding_basis,
                recorded_at=datetime.now().isoformat(),
            )
            self._append(examination.as_dict())
        return examination

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def examinations(self) -> Tuple[GoalExamination, ...]:
        """Every readable examination, IN APPEND ORDER.

        Reads the FILE rather than `self.entries`: the log spans processes and
        the in-memory mirror does not. A line that will not parse, or that
        carries a basis outside the closed vocabulary, contributes NOTHING.

        **AN UNREADABLE EXISTING LOG RAISES TYPED** - Ruling 75 res.7, the
        ordered housekeeping, applying Ruling 74's own finding to the file that
        finding was reported against. The activation layer hit this first: its
        guards read the log BEFORE the mint, so an unreadable log surfaced a
        bare `OSError` one frame above the only place that knew how to name it.
        **This method had the identical latent shape**, and its inherited
        battery row passed only because a single-commitment fixture returns at
        `SOLE_CANDIDATE` before `_context()` ever reads the log - with two or
        more candidates it raised bare.

        Returning `()` would be worse than the `OSError`: an unreadable log
        would read as "no goal has ever been examined", which makes every
        never-examined rung tie and silently re-decides the ladder.

        A MISSING log stays a legitimate empty history - absence is a first run,
        not a fault, which is `derive_max_ordinal`'s own distinction.
        """
        if not self.log_path.exists():
            return ()
        out: List[GoalExamination] = []
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise ExaminationLogUnreadable(
                f"the examination log at '{self.log_path}' exists and cannot "
                f"be read, so no fact about any selection can be derived from "
                f"it - not which goal was last examined, not how long one has "
                f"held focus. Answering from an empty read would report that "
                f"nothing has ever been examined.") from failure
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
                if data.get("kind_of_record") != "examination":
                    continue
                entry = GoalExamination.from_dict(data)
                if entry is not None:
                    out.append(entry)
        return tuple(out)

    def examinations_for(self, goal_id: str) -> Tuple[GoalExamination, ...]:
        return tuple(e for e in self.examinations()
                     if e.selected_goal_id == goal_id)

    # -----------------------------------------------------------------
    # LIVENESS - the MEASUREMENT (res.7). It reports; it never gates.
    # -----------------------------------------------------------------

    def focus_persistence(self, goal_id: str) -> FocusPersistence:
        """How long this goal has held focus, and whether anything moved.

        Counts back from the MOST RECENT examination while the selection is
        still this goal, then asks the ledger whether any evidence or
        resolution for it was appended since that run began.

        **NO THRESHOLD, NO GATE, NO VERDICT.** This returns two facts. What to
        DO about a goal that has held focus without progress is Q3's, through
        QL5's closed stop set, whose `no-progress` member is the registered
        consumer of exactly this derivation.

        THE JOIN IS BY RECORDED TIMESTAMP, AND THE LIMITATION IS STATED. The two
        stores carry no shared symbolic ordinal - the goal ledger mints `GLC-`
        and this log mints `EXM-`, and neither orders against the other - so
        "since the run began" is answered by comparing ISO-8601 `recorded_at`
        strings, which are lexicographically ordered and written by one process
        clock. This is the same systemic gap the carried Echo wall-clock item
        names. REOPENING: a shared symbolic ordinal across durable stores would
        make this exact rather than clock-dependent.
        """
        examinations = self.examinations()

        run: List[GoalExamination] = []
        for examination in reversed(examinations):
            if examination.selected_goal_id != goal_id:
                break
            run.append(examination)

        if not run:
            return FocusPersistence(goal_id=goal_id,
                                    consecutive_selections=0,
                                    progress_recorded=False)

        run_started_at = run[-1].recorded_at
        progress = False

        for evidence in self.ledger.evidence_for(goal_id):
            if evidence.recorded_at >= run_started_at:
                progress = True
        resolution = self.ledger.resolution_for(goal_id)
        if resolution is not None and resolution.resolved_at >= run_started_at:
            progress = True

        return FocusPersistence(goal_id=goal_id,
                                consecutive_selections=len(run),
                                progress_recorded=progress)
