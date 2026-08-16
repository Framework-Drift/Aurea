"""M7-a: the derived view -- the Executive's ENTIRE working state, computed.

L10: the component that loops holds no constitutive state. This module is the
enforcement in code shape: ONE frozen dataclass and ONE pure function. There is
no cache, no store, no file, no clock, and no write path anywhere in it. Two
calls over the same ledgers yield equal views; a view that could differ from
its own recomputation would be owned state wearing a derivation's name.

DUCK-TYPED READ HANDLES, NEVER IMPORTED (episode_record.py's M3-B precedent
verbatim): this module imports no ledger class, so the enforcement-by-scope
pins stay exact and a handle handed to a reader for one question cannot be
talked into answering others. The handles are used for their named read
methods ONLY: `open_items()`, `commitments()`, `resolutions()`, `read_all()`.

THE CHAIR IS DERIVED, NEVER HARDWIRED (ninety-eighth entry): the
delegated-cognition chair's state is a function of whether the M5 qualification
verdict has been registered as a consumed acquisition. Before that record
exists the chair is UNREGISTERED -- a visible state, not an error. After it,
EMPTY_BY_REFUSED_VERDICT. There is NO qualified state in this vocabulary,
because no package has ever cleared the gate; adding one is a ruling that
arrives with the first QUALIFIED verdict, not before (M7_GROUNDING section 3).

M7-b EXTENDS THIS VIEW WITH CANDIDATE FACTS, AND THE CUT IS DELIBERATE: the
view holds FACTS read from the kernel; `attention_policy` holds ORDERING over
them. Nothing here knows that an obligation outranks a goal, and nothing here
ranks anything -- so `attention-policy.v2` would change one module and this one
not at all. A view that carried ordering keys would be a policy wearing a
derivation's name.

NOTHING HERE READS THE SELECTION LOG. The Executive records the acts it takes;
those records are forensic, and a derivation that folded them back in would make
the loop's own history an input to its next decision -- owned state, reached by
the long way round. L10, pinned by AST rather than promised.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, Tuple

# PURE FUNCTIONS ONLY, NEVER A LEDGER CLASS. `seq_ordinal` parses a `SEQ-`
# token and `ordinal_pattern` builds an anchored id matcher; neither opens a
# file, holds state, or reaches a store. `episode_record` set this precedent
# explicitly - it imports the obligation ledger's mint FUNCTION and not its
# class, so the zero-internal-callers pins (which bind on CLASSES) stay exact.
#
# RE-DERIVING EITHER PATTERN HERE WAS THE ALTERNATIVE AND IS REFUSED: a second
# definition of a ruled regex is what Ruling 79 declined by name, and an id
# grammar that drifts between two spellings is a join that silently stops
# joining.
from src.filtration.obligation_ledger import seq_ordinal
from src.utils.ledger_mint import ordinal_pattern

# The payload discriminator for the consumed-verdict acquisition. A closed,
# exact string: the derivation below matches it with equality, never with
# heuristics, so a payload that ALMOST looks like a verdict registration is
# nothing at all.
VERDICT_PAYLOAD_KIND = "M5_QUALIFICATION_VERDICT_CONSUMED"


class ChairState(str, Enum):
    """The delegated-cognition chair, v1: exactly two states.

    UNREGISTERED is the loop before its first submission -- the chair's state
    is not yet on the record, and the view says so rather than assuming.
    EMPTY_BY_REFUSED_VERDICT is the designed initial condition after the loop
    has read the verdict: the chair exists, the gate swung, nobody sits in it.
    """

    UNREGISTERED = "unregistered"
    EMPTY_BY_REFUSED_VERDICT = "empty_by_refused_verdict"


class AttentionCategory(str, Enum):
    """WHICH PRECEDENCE CLASS a candidate belongs to. Closed at three.

    **VOCABULARY COLLISION CENSUS, run BEFORE coining** (Ruling 30's discipline;
    67 enum classes / 279 distinct member names in `src/` at `ce0498f`). ZERO
    class-name collisions. Two member names already exist elsewhere and are
    recorded here so nobody later derives one sense from the other:

      * `OBLIGATION` and `PREDICTION` are live in
        `proposition_ledger.KernelRefKind`, where they name WHICH KERNEL STORE
        AN ID LIVES IN. Here they name WHICH PRECEDENCE CLASS A CANDIDATE
        BELONGS TO. **This enum is NOT derived from that one and must not be**,
        or a store-vocabulary change would silently move what the Executive
        attends to first - the same reasoning `TargetKind` records about
        `NodeType`, one layer up.

    `GOAL` is free tree-wide. There is deliberately no fourth member: a category
    the policy cannot order is a category it must not be handed.
    """

    OBLIGATION = "obligation"
    PREDICTION = "prediction"
    GOAL = "goal"


@dataclass(frozen=True)
class AttentionCandidate:
    """ONE attendable record, as FACTS. It carries no ranking of any kind.

    Every field below is READ FROM THE KERNEL, never computed by comparison.
    The policy turns these into ordering keys; this type does not know what
    outranks what, and a reviewer can confirm that by the absence of any
    comparison operator in this module.

    The optional fields are category-shaped and that is honest rather than
    untidy: an obligation has no commitment ordinal and a goal has no horizon.
    `None` means THE FACT DOES NOT APPLY TO THIS CATEGORY - it never means the
    fact was unavailable, because a candidate whose ordering fact could not be
    read is not built at all.
    """

    category: AttentionCategory
    record_id: str
    # OBLIGATIONS. The EFFECTIVE due ordinal - see `_obligation_candidates`.
    due_ordinal: Optional[int] = None
    # PREDICTIONS. The `FieldState` VALUE of the recorded resolution horizon,
    # verbatim. Carried beside the rank the policy derives from it so that
    # Docket H's cut survives the ordering: DECLARED_NONE and ABSENT rank
    # together and are still DIFFERENT FACTS on the record.
    horizon_state: Optional[str] = None
    # PREDICTIONS and GOALS. The mint ordinal behind the record's own id, which
    # IS commitment order - both ledgers are append-only and mint monotonically.
    commitment_ordinal: Optional[int] = None


# The `FieldState` value meaning "the channel supplied a horizon". Compared by
# VALUE rather than imported as a member, so that this module keeps its promise
# to import no ledger class; the real vocabulary is pinned against it.
HORIZON_PROVIDED = "provided"

# What a horizon field reads as when the handle carries none at all. This is the
# PREDICTION LEDGER'S OWN DEFAULT (`field(default_factory=absent)`), not a
# convenience: a commitment that never mentioned a horizon is ABSENT there too,
# so reading a missing attribute as ABSENT agrees with the store rather than
# guessing past it.
HORIZON_WHEN_UNRECORDED = "absent"


def _ordinal_of(record_id: Any, prefix: str) -> Optional[int]:
    """The mint ordinal behind an id, by ANCHORED match, or `None`.

    Ruling 64's rider discipline: `PRD-00010` must never read as `PRD-0001`, and
    a bare `\\b` is insufficient because `-` is itself a non-word character.
    An unparseable id yields `None` and the policy orders it by identity - it is
    never guessed at and never silently sorted first.
    """
    if not isinstance(record_id, str):
        return None
    match = ordinal_pattern(prefix).search(record_id)
    return int(match.group(1)) if match else None


def _obligation_candidates(obligations: Any) -> Tuple[AttentionCandidate, ...]:
    """Standing obligations, carrying their EFFECTIVE DUE ORDINAL.

    **THE FINDING THAT SHAPES THIS FUNCTION, measured before it was written:**
    `open_items()` returns the OPEN record, and `due_seq` is not on it. A
    deferral is a SEPARATE append (`ObligationRecordType.DEFERRED`) carrying
    `reason` and `due_seq`, because that ledger is event-sourced and never edits
    a record in place. So the due ordinal has to be FOLDED out of the stream; a
    reader that trusted `open_items()` alone would silently order every deferred
    obligation by its admission instead of by when it was set aside.

    **THE EFFECTIVE DUE ORDINAL IS THE DEFERRED `due_seq` WHERE ONE EXISTS, AND
    THE OPEN `created_seq` OTHERWISE - AND THE TWO ARE COMPARABLE BECAUSE THEY
    ARE MINTED BY ONE CLOCK.** `mint_seq_token` stamps every record in that
    ledger from a single monotonic `SEQ-` sequence, so an admission ordinal and
    a due ordinal are points on the same line. Nothing is coined, nothing is
    scaled, and no magnitude is invented to make them commensurable - they
    already were, and that is what licenses this reading rather than a
    convenience mapping.

    The consequences are both intended: an un-deferred obligation sorts by when
    it arrived, and a deferred one sorts by when it comes due - which puts an
    OVERDUE deferral (a due ordinal already passed) ahead of recent arrivals,
    and a far-future deferral behind them.

    THE FOLD IS LAZY. With no standing obligations there is nothing to order, so
    the stream is never read - which also means a handle that offers only
    `open_items()` stays sufficient for the empty case.
    """
    items = list(obligations.open_items())
    if not items:
        return ()

    standing = {item.get("obligation_id") for item in items}
    due: dict = {}
    for record in obligations.read_all():
        obligation_id = record.get("obligation_id")
        if obligation_id not in standing:
            continue
        # LAST DEFERRAL WINS, by append order: an obligation may be deferred
        # more than once, and the ledger's own `status_of` folds the same way.
        ordinal = seq_ordinal(record.get("due_seq"))
        if ordinal is not None:
            due[obligation_id] = ordinal

    out = []
    for item in items:
        obligation_id = item.get("obligation_id")
        effective = due.get(obligation_id)
        if effective is None:
            effective = seq_ordinal(item.get("created_seq"))
        out.append(AttentionCandidate(
            category=AttentionCategory.OBLIGATION,
            record_id=str(obligation_id),
            due_ordinal=effective))
    return tuple(out)


@dataclass(frozen=True)
class PredictionFacts:
    """What M7-c's discrepancy classes need about ONE unresolved prediction.

    FACTS ONLY, exactly as `AttentionCandidate` is. Nothing here decides whether
    a prediction is overdue - that comparison is the generator's, and it is made
    against a clock reading carried on the substrate beside these.
    """

    prediction_id: str
    # The `FieldState` VALUE, verbatim. DECLARED_NONE and ABSENT are kept apart
    # here for the same reason they are on the attention census: they are
    # different facts about a prediction, and only the RANK ever merges them.
    horizon_state: str
    # The `SEQ-` ordinal behind the recorded horizon, or `None`.
    #
    # **THIS IS NOT AN INTERPRETATION OF THE HORIZON'S FORMAT** (Ruling 61
    # res.5, which refuses to interpret one and cannot honestly). It asks a
    # narrower question with a recorded answer: IS THE RECORDED VALUE A TOKEN OF
    # THE ONE CLOCK THIS TREE HAS? A `SEQ-NNNNNN` token is comparable to every
    # other point on that clock; anything else - a date, a cycle count, a prose
    # condition - is left alone and yields `None`, which the generator reads as
    # "no comparable ordinal" rather than as "not overdue".
    horizon_ordinal: Optional[int]
    # Recorded ids only (Ruling 61's `claim_refs`, never validated here).
    claim_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class GoalFacts:
    """The LINKAGE fields a licensing derivation may honestly read.

    Ids only, and only the two tuples that can carry a linkage. `desired_state`,
    `kind`, `provenance` and every other content field are deliberately ABSENT
    from this type: M7-c's bounds permit reading id, order and linkage, and a
    field that is not carried cannot be read by accident.
    """

    goal_id: str
    originating_record_ids: Tuple[str, ...] = ()
    justification_claim_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ObligationFacts:
    """A standing obligation's PROVENANCE - who authored it, and about what.

    `source` is what makes depth accounting possible from records alone: an
    obligation the inquiry generator admitted carries the generator's name in
    the field the ledger already stamps, so "did I author this" is a recorded
    fact rather than a self-log read.
    """

    obligation_id: str
    source: str
    target_kind: str
    target_id: str


@dataclass(frozen=True)
class InquirySubstrate:
    """Everything M7-c's generator reads, gathered once per observation.

    Carried BESIDE the attention candidates rather than merged into them,
    because the two consumers ask different questions of the same kernel and
    merging would give the attention policy fields it has no business reading.
    """

    predictions: Tuple[PredictionFacts, ...] = ()
    goals: Tuple[GoalFacts, ...] = ()
    obligations: Tuple[ObligationFacts, ...] = ()
    # THE CLOCK READING, from the obligation ledger's own `SEQ-` sequence - the
    # single monotonic clock this tree mints logical time from. It is an
    # OBSERVATION carried as data, never a wall-clock read: the generator
    # compares two recorded points and calls no clock of its own.
    max_seq_ordinal: int = 0


@dataclass(frozen=True)
class DerivedView:
    """One observation of the kernel, frozen. Equality is field equality.

    `open_obligations`: obligation ids with OPEN status, ledger order.
    `unresolved_predictions`: prediction ids committed and not yet resolved,
        commitment order.
    `committed_goals`: goal ids in commitment (append) order.
    `chair`: the delegated-cognition chair state, derived per module docstring.
    `verdict_acquisition_id`: the ACQ- id of the consumed-verdict record when
        the chair is EMPTY_BY_REFUSED_VERDICT, else None. Carried so any
        consumer of the view can cite the record rather than the view.
    """

    open_obligations: Tuple[str, ...]
    unresolved_predictions: Tuple[str, ...]
    committed_goals: Tuple[str, ...]
    chair: ChairState
    verdict_acquisition_id: Optional[str]
    # M7-b. Every attendable record with the FACTS an ordering needs, in the
    # same order as the three id tuples above. ADDITIVE and defaulted, so every
    # M7-a construction and every M7-a pin still means exactly what it meant.
    candidates: Tuple[AttentionCandidate, ...] = ()
    # M7-c. Additive and defaulted for the same reason `candidates` was: every
    # M7-a and M7-b pin must keep meaning exactly what it meant, and the v-a/v-b
    # test files must pass BYTE-UNMODIFIED.
    inquiry: InquirySubstrate = field(default_factory=InquirySubstrate)

    def candidates_in(self,
                      category: AttentionCategory) -> Tuple[AttentionCandidate, ...]:
        """This category's candidates, in derivation order. A filter, not a rank."""
        return tuple(c for c in self.candidates if c.category is category)


def _verdict_registration(acquisitions: Any) -> Optional[str]:
    """Return the ACQ- id of the consumed-verdict record, if exactly present.

    Scans `read_all()` for a record whose payload parses as JSON and carries
    `kind == VERDICT_PAYLOAD_KIND`. A payload that fails to parse is not a
    candidate -- the registration path writes canonical JSON, so anything else
    is some other arrival that happens to share bytes-shape, and guessing
    would be classification by resemblance.
    """
    for record in acquisitions.read_all():
        payload = getattr(record, "payload", None)
        if not isinstance(payload, str):
            continue
        try:
            parsed = json.loads(payload)
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, dict) and parsed.get("kind") == VERDICT_PAYLOAD_KIND:
            return getattr(record, "acquisition_id", None)
    return None


def derive(obligations: Any, predictions: Any, goals: Any,
           acquisitions: Any) -> DerivedView:
    """Compute the Executive's working state from kernel ledgers. Pure.

    Reads only. Raises whatever the ledgers raise -- an unreadable kernel store
    is the kernel's fact to assert, and a derivation that swallowed it would be
    inventing an empty world.
    """
    obligation_candidates = _obligation_candidates(obligations)
    open_obligations = tuple(c.record_id for c in obligation_candidates)

    resolved_ids = frozenset(
        str(res.prediction_id) for res in predictions.resolutions())
    prediction_candidates = []
    for com in predictions.commitments():
        prediction_id = str(com.prediction_id)
        if prediction_id in resolved_ids:
            continue
        # THE HORIZON IS READ FOR ITS STATE, NEVER FOR ITS VALUE. Ruling 61
        # res.5 is explicit that the prediction ledger does not interpret a
        # horizon and CANNOT honestly - it may be a date, a cycle count or an
        # observed condition, and choosing a format would coin one at the point
        # "has this expired" gets decided. So the Executive orders by whether a
        # horizon was RECORDED, which is a fact, and never by what it says.
        horizon = getattr(com, "resolution_horizon", None)
        state = getattr(horizon, "state", None)
        prediction_candidates.append(AttentionCandidate(
            category=AttentionCategory.PREDICTION,
            record_id=prediction_id,
            horizon_state=(getattr(state, "value", None)
                           if state is not None else HORIZON_WHEN_UNRECORDED),
            commitment_ordinal=_ordinal_of(prediction_id, "PRD-")))
    unresolved = tuple(c.record_id for c in prediction_candidates)

    goal_candidates = tuple(
        AttentionCandidate(
            category=AttentionCategory.GOAL,
            record_id=str(com.goal_id),
            commitment_ordinal=_ordinal_of(str(com.goal_id), "GLC-"))
        for com in goals.commitments())
    committed_goals = tuple(c.record_id for c in goal_candidates)

    # ---------------------------------------------------------------
    # M7-c SUBSTRATE. Every read below is GUARDED, and the guards are not
    # defensive clutter: this function's handles are duck-typed by contract
    # (episode_record's M3-B precedent), so a handle supplying only what an
    # EARLIER slice named must keep working. That is pin 9 - the v-a and v-b
    # test files pass byte-unmodified - enforced here rather than promised.
    # ---------------------------------------------------------------
    prediction_facts = []
    for com in predictions.commitments():
        prediction_id = str(com.prediction_id)
        if prediction_id in resolved_ids:
            continue
        horizon = getattr(com, "resolution_horizon", None)
        state = getattr(horizon, "state", None)
        prediction_facts.append(PredictionFacts(
            prediction_id=prediction_id,
            horizon_state=(getattr(state, "value", None) if state is not None
                           else HORIZON_WHEN_UNRECORDED),
            # Only a PROVIDED horizon can carry a value worth parsing; an
            # ABSENT one has nothing recorded, and reading a DECLARED_NONE's
            # value would be reading a declaration that there is none.
            horizon_ordinal=(seq_ordinal(getattr(horizon, "value", None))
                             if getattr(state, "value", None) == HORIZON_PROVIDED
                             else None),
            claim_refs=tuple(str(r) for r in getattr(com, "claim_refs", ()) or ())))

    goal_facts = tuple(
        GoalFacts(
            goal_id=str(com.goal_id),
            originating_record_ids=tuple(
                str(r) for r in getattr(com, "originating_record_ids", ()) or ()),
            justification_claim_ids=tuple(
                str(r) for r in getattr(com, "justification_claim_ids", ()) or ()))
        for com in goals.commitments())

    obligation_facts = []
    max_seq = 0
    read_all = getattr(obligations, "read_all", None)
    if callable(read_all):
        standing = {c.record_id for c in obligation_candidates}
        for record in read_all():
            # THE CLOCK READING is taken over EVERY line, not only standing
            # ones: `SEQ-` is monotonic across the whole stream, so the maximum
            # observed is the furthest point logical time has reached. Reading
            # it off standing records alone would make the clock run backwards
            # whenever an obligation was merged out of the standing set.
            for key in ("created_seq", "due_seq"):
                ordinal = seq_ordinal(record.get(key))
                if ordinal is not None and ordinal > max_seq:
                    max_seq = ordinal
            obligation_id = record.get("obligation_id")
            if obligation_id in standing and record.get("source") is not None:
                obligation_facts.append(ObligationFacts(
                    obligation_id=str(obligation_id),
                    source=str(record.get("source")),
                    target_kind=str(record.get("target_kind")),
                    target_id=str(record.get("target_id"))))

    verdict_id = _verdict_registration(acquisitions)
    chair = (ChairState.EMPTY_BY_REFUSED_VERDICT if verdict_id is not None
             else ChairState.UNREGISTERED)

    return DerivedView(
        open_obligations=open_obligations,
        unresolved_predictions=unresolved,
        committed_goals=committed_goals,
        chair=chair,
        verdict_acquisition_id=verdict_id,
        candidates=(obligation_candidates + tuple(prediction_candidates)
                    + goal_candidates),
        inquiry=InquirySubstrate(
            predictions=tuple(prediction_facts),
            goals=goal_facts,
            obligations=tuple(obligation_facts),
            max_seq_ordinal=max_seq),
    )
