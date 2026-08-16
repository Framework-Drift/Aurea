"""M7-b: `attention-policy.v1` -- the named, versioned, deterministic chooser.

Heading Phase 7's ordering, verbatim, as CATEGORY PRECEDENCE: obligations, then
unresolved predictions, then committed goals. The heading's section 5 forbids an
unexamined judgment at the top of the stack, and this module is the examined one
made legible: every rung is declared data, every key is read off a record, and
the whole decision is recomputable from the kernel by anyone holding the same
ledgers.

PURE, AND THE PURITY IS STRUCTURAL RATHER THAN PROMISED
-------------------------------------------------------------------------------
This module imports the DERIVED VIEW and nothing else from `src/`. No ledger, no
path, no `open`, no `datetime`, no `random`, no `secrets` - Ruling 71 as
import-absence, which is the arbiter's own pin set and the reason it is quotable
rather than argued. **A stochastic selector biases what the system can come to
know, invisibly**, and a selector that could read a store could be given a
different answer by a store that changed underneath it. Neither is reachable
from here.

`select()` takes a `DerivedView` and returns an `AttentionSelection`. It writes
nothing, records nothing, and has no side effect of any kind - which is what
lets the determinism and reconstruction pins be measured without accumulating a
single log line, exactly as `GoalArbiter.select` is separated from `examine`.

THE VIEW HOLDS FACTS; THIS MODULE HOLDS ORDERING
-------------------------------------------------------------------------------
`derived_view` reads the kernel and knows nothing about precedence; this module
ranks and reads no store. That cut is what makes `attention-policy.v2` a
one-module change, and it is why the ordering keys are computed HERE from facts
rather than carried on the candidate: a fact that arrived pre-ranked would make
the view a policy under another name.

NO WEIGHTS, NO SCORES, NO MAGNITUDES - §9 STANDING BAR #5
-------------------------------------------------------------------------------
Every key below is either an ORDINAL READ OFF A RECORD (a mint sequence, a
logical-time token) or a MEMBERSHIP RANK over a closed vocabulary. Nothing is
scaled, combined, weighted or summed. **A numeric priority would be a coined
magnitude at the exact point the heading forbids an unexamined judgment** - and
it would be the most natural-looking wrong move in this file, because "urgency"
feels like a number and is not one anybody recovered from the corpus.

WHAT THIS POLICY DELIBERATELY DOES NOT DO
-------------------------------------------------------------------------------
  * IT NEVER CONSULTS OR DUPLICATES THE GOAL ARBITER. Ruling 73's ladder orders
    WITHIN goals; this orders ACROSS categories. `goal_arbitration` is not
    imported, not read, and not modified, and that is pinned - two selectors
    quietly sharing a rung would make one ruling's change move the other's
    behaviour invisibly.
  * IT READS NO GOAL CONTENT beyond id and order - no `level`, no kind, no
    provenance. `level` is stored and not policed (Ruling 72), and reading it
    here would be this module inventing the level-precedence classes a future
    arbitration ruling owns.
  * IT NEVER READS THE SELECTION LOG. The policy is a function of the kernel,
    so a cold-rebuilt loop selects the same next item - Test 6 in miniature,
    extended to v-b. **A recency rung is therefore UNBUILDABLE here without
    breaking that property**, and that is a design fact rather than an
    oversight; see the persistence note on `CATEGORY_PRECEDENCE`.

FORK 8.1 IS PRESENT AND UNRESOLVED, BY CONSTRUCTION
-------------------------------------------------------------------------------
The heading requires Executive policies to be "named, versioned objects with
Foundry contracts". A deterministic non-model instrument is exactly the open
fork-8.1 question, so `FOUNDRY_CONTRACT` is PRESENT AS DECLARED DATA and
EXPLICITLY UNEVALUATED. The slot exists so the fork's ruling has somewhere to
land; nothing here evaluates it, and no code path reads it into a decision.
Filling it in would resolve the fork by construction, which this slice must not
do.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from src.executive.derived_view import (
    HORIZON_PROVIDED,
    AttentionCandidate,
    AttentionCategory,
    DerivedView,
)

__all__ = [
    "POLICY_NAME", "POLICY_VERSION", "FOUNDRY_CONTRACT",
    "SelectionBasis", "SelectionOutcome", "CATEGORY_PRECEDENCE",
    "WITHIN_CATEGORY_LADDER", "CandidateAssessment", "AttentionSelection",
    "AttentionPolicy", "PolicyIdentityMismatch",
]


# =====================================================================
# IDENTITY - DATA, NEVER CONVENTION
# =====================================================================

# The name the heading requires, exactly. Not derived, not formatted, not
# assembled from parts: a name assembled at runtime is a name that can differ
# between two processes that both believe they ran the same policy.
POLICY_NAME = "attention-policy.v1"

# CARRIED SEPARATELY even though the name ends in `v1`. The name is an
# IDENTIFIER and the version is a FACT ABOUT THE INSTRUMENT, and collapsing
# them would mean a `v2` could only ever be a different name - never a
# comparable successor of the same instrument.
POLICY_VERSION = "1"


FOUNDRY_CONTRACT: Mapping[str, Any] = MappingProxyType({
    # PRESENT AND UNEVALUATED. See the module docstring: the slot's existence is
    # the requirement; filling it would decide fork 8.1 by construction.
    "fork": "8.1",
    "status": "DEFERRED",
    "question": (
        "whether a deterministic, non-model Executive instrument requires "
        "Foundry evaluation, or whether the Foundry contract binds only "
        "learned/generative capabilities"
    ),
    "evaluated": False,
    # No verdict, no commit, no record path. A citation here would be a claim
    # that an evaluation happened.
    "evaluation_record": None,
})


class PolicyIdentityMismatch(Exception):
    """Construction named an identity this module does not carry.

    Identity is DATA: a caller that believes it is constructing
    `attention-policy.v2` must not silently receive v1's ordering under v2's
    name, because the selection record would then cite a policy that never ran.
    """


# =====================================================================
# THE VOCABULARY - censused before coining (Ruling 30)
# =====================================================================

class SelectionOutcome(str, Enum):
    """Whether anything was attendable at all.

    **NOTHING_ATTENDABLE IS A REAL OUTCOME, NOT AN ERROR.** A kernel with no
    standing obligation, no unresolved prediction and no committed goal is a
    quiet kernel, and quiet is a state the Executive is allowed to be in. A loop
    that raised here would treat an empty world as a failure and would leave no
    record that it looked - which is the one thing the log exists to prevent.
    """

    SELECTED = "selected"
    NOTHING_ATTENDABLE = "nothing_attendable"


class SelectionBasis(str, Enum):
    """WHICH KEY made the selected candidate unique. CLOSED, and COINED here.

    The recorded basis beside a derived output - Ruling 63's form, and
    `DecidingBasis`'s shape one domain over. **It is a SEPARATE VOCABULARY from
    `goal_arbitration.DecidingBasis` on purpose**: that one answers "which rung
    of Ruling 73's within-goals ladder decided", this one answers "which key of
    the across-category ordering decided". Sharing a type would let one ruling's
    edit move the other selector's recorded meaning. `SOLE_CANDIDATE` is live in
    that enum and is deliberately NOT reused here - see `CATEGORY_PRECEDENCE`.
    """

    # The winning category held exactly one candidate, so precedence alone
    # decided and no within-category key ever ran. **Deliberately not spelled
    # `SOLE_CANDIDATE`**: that word is `DecidingBasis`'s, and it means sole
    # among GOALS. This means sole within the winning CATEGORY, which is a
    # different claim about a different field.
    CATEGORY_PRECEDENCE = "category_precedence"
    # Obligations: the effective due ordinal.
    DUE_ORDINAL = "due_ordinal"
    # Predictions: whether a resolution horizon was RECORDED (never its value).
    HORIZON_STANDING = "horizon_standing"
    # Predictions and goals: the mint ordinal behind the record's own id.
    COMMITMENT_ORDER = "commitment_order"
    # The backstop. Ids are unique, so this rung can never tie.
    RECORD_IDENTITY = "record_identity"


# ---------------------------------------------------------------------
# CATEGORY PRECEDENCE - the heading's order, as DECLARED DATA
# ---------------------------------------------------------------------
#
# **PERSISTENCE IS THE INTENDED CONSEQUENCE, AND IT IS NOT RULING 73-A's
# STARVATION.** With no recency term, a category's leader stays the leader until
# the kernel changes - which is exactly what pin 7 requires (a cold-rebuilt loop
# selects the same next item) and what makes the ordering auditable at all.
# Obligations and predictions DRAIN: an obligation leaves the standing set when
# it is merged or an episode opens against it, and a prediction leaves when it
# resolves. So this is a work queue that empties, not a rotation among permanent
# items.
#
# **THE GOAL CATEGORY IS THE HONEST EXCEPTION AND IS REPORTED RATHER THAN
# PATCHED.** Ruling 72 res.5 makes a ROOT structurally unresolvable - it can
# only be superseded - so with obligations and predictions empty, this policy
# names the same lowest-ordinal goal every cycle. That is the shape Ruling 73-A
# reordered a ladder to escape. It is NOT repaired here for two reasons, both
# binding: the handoff rules that within-goals ordering is the ARBITER's and is
# not to be duplicated or consulted here, and any recency term would require
# reading the selection log into the decision, which pin 8 forbids outright.
# The composition - this policy naming the GOAL category, the arbiter rotating
# WITHIN it - is the architecture that resolves it, and wiring that composition
# is a later slice's with its own ruling.
CATEGORY_PRECEDENCE: Tuple[AttentionCategory, ...] = (
    AttentionCategory.OBLIGATION,
    AttentionCategory.PREDICTION,
    AttentionCategory.GOAL,
)


# Larger than any ordinal a ledger will mint in practice. A record whose
# ordinal cannot be parsed sorts AFTER every parseable one and falls through to
# the identity backstop, which can always order it. `goal_arbitration` sorts an
# unparseable id the same way and for the same reason: never guessed at, never
# silently first.
_UNORDERED = 2 ** 62


def _key_due_ordinal(candidate: AttentionCandidate) -> Any:
    """OBLIGATIONS, rung 1 - the effective due ordinal, ascending.

    Derived in `derived_view._obligation_candidates`: a deferral's `due_seq`
    where one was appended, the admission `created_seq` otherwise, both minted
    from the obligation ledger's ONE monotonic `SEQ-` clock, which is what makes
    them comparable without coining anything.
    """
    return _UNORDERED if candidate.due_ordinal is None else candidate.due_ordinal


def _key_horizon_standing(candidate: AttentionCandidate) -> Any:
    """PREDICTIONS, rung 1 - a RECORDED horizon orders first. A MEMBERSHIP RANK.

    **THE VALUE IS NEVER READ, ONLY THE STATE.** Ruling 61 res.5 is explicit
    that a horizon may be a date, a cycle count or an observed condition, and
    that picking a format coins a magnitude at the point expiry is decided. So
    this asks only whether the predictor RECORDED one.

    **DECLARED_NONE AND ABSENT RANK TOGETHER, AND THEY REMAIN DIFFERENT FACTS.**
    Docket H's cut is not flattened by this rank - the candidate carries the
    `FieldState` value verbatim and the census records it, so a reader still
    sees "the predictor declared no horizon" and "nobody asked" as the distinct
    things they are. Ordering them against each other would need a reason no
    ruling supplies, so they tie and the next rung decides.
    """
    return 0 if candidate.horizon_state == HORIZON_PROVIDED else 1


def _key_commitment_order(candidate: AttentionCandidate) -> Any:
    """PREDICTIONS and GOALS - the mint ordinal behind the id, ascending.

    Commitment order IS append order: both ledgers are append-only and mint
    monotonically from their own files, so the ordinal is the commitment
    sequence rather than a proxy for it.
    """
    return (_UNORDERED if candidate.commitment_ordinal is None
            else candidate.commitment_ordinal)


def _key_record_identity(candidate: AttentionCandidate) -> Any:
    """EVERY CATEGORY, last rung - the record id, ascending. THE BACKSTOP.

    Ids are unique within a ledger, so this rung cannot tie and the ladder
    always selects. **A selector that could return "no decision" would hand the
    question back to its caller, which is where nondeterminism gets in.**

    Ties break by IDENTITY and never by content: comparing claim text, goal
    descriptions or expected results would be a judgment about meaning at the
    point attention is allocated - a selection effect entering by the side door,
    which is Ruling 71's finding and binds identically here.
    """
    return candidate.record_id


_Rung = Tuple[SelectionBasis, Callable[[AttentionCandidate], Any]]

# Each category's within-category ladder, as DECLARED DATA. A rung narrows the
# field to those sharing the minimum key; the first rung leaving exactly one
# candidate is the recorded basis.
WITHIN_CATEGORY_LADDER: Mapping[AttentionCategory, Tuple[_Rung, ...]] = \
    MappingProxyType({
        AttentionCategory.OBLIGATION: (
            (SelectionBasis.DUE_ORDINAL, _key_due_ordinal),
            (SelectionBasis.RECORD_IDENTITY, _key_record_identity),
        ),
        AttentionCategory.PREDICTION: (
            (SelectionBasis.HORIZON_STANDING, _key_horizon_standing),
            (SelectionBasis.COMMITMENT_ORDER, _key_commitment_order),
            (SelectionBasis.RECORD_IDENTITY, _key_record_identity),
        ),
        AttentionCategory.GOAL: (
            (SelectionBasis.COMMITMENT_ORDER, _key_commitment_order),
            (SelectionBasis.RECORD_IDENTITY, _key_record_identity),
        ),
    })


# =====================================================================
# THE RESULT - pure, recomputable, never stored by this module
# =====================================================================

@dataclass(frozen=True)
class CandidateAssessment:
    """ONE candidate's place in the ordering, with the reason it is there.

    **THIS TYPE IS WHY A NON-SELECTION'S REASON IS ON THE RECORD RATHER THAN
    ONLY IN THE POLICY.** L5's no-invisible-chooser law is satisfied by writing
    down what happened to every candidate, not by promising the policy could be
    rerun: a reader a year from now has the ledgers and the log, and the log
    must answer without re-executing anything.
    """

    category: AttentionCategory
    record_id: str
    # The ordering key actually used, in the category ladder's rung order.
    ordering_key: Tuple[Any, ...]
    # What each position of `ordering_key` means. Parallel, same length.
    key_names: Tuple[str, ...]
    # The rung at which this candidate stopped being a contender, or `None` for
    # the selected one. A candidate in a losing CATEGORY carries
    # `CATEGORY_PRECEDENCE` - it never entered a within-category ladder at all.
    outranked_at: Optional[SelectionBasis]
    selected: bool
    # The `FieldState` value the horizon rank compresses, for predictions.
    # Carried so Docket H's cut survives onto the permanent record.
    horizon_state: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "record_id": self.record_id,
            "ordering_key": list(self.ordering_key),
            "key_names": list(self.key_names),
            "outranked_at": (None if self.outranked_at is None
                             else self.outranked_at.value),
            "selected": self.selected,
            "horizon_state": self.horizon_state,
        }


@dataclass(frozen=True)
class AttentionSelection:
    """The pure result of running the policy. RECOMPUTABLE, never stored here.

    Named `AttentionSelection` rather than `Selection` because
    `goal_arbitration.Selection` is live - the census caught it, and two types
    called `Selection` in one tree is how a reader ends up believing one
    selector's guarantees about the other's output.
    """

    outcome: SelectionOutcome
    selected_category: Optional[AttentionCategory]
    selected_record_id: Optional[str]
    deciding_basis: Optional[SelectionBasis]
    census: Tuple[CandidateAssessment, ...]

    def __post_init__(self) -> None:
        if self.outcome is SelectionOutcome.NOTHING_ATTENDABLE:
            if self.selected_record_id is not None or self.census:
                raise ValueError(
                    "NOTHING_ATTENDABLE means no candidate stood; a record id "
                    "or a non-empty census contradicts the outcome it is "
                    "recorded beside.")
            return
        if not self.selected_record_id:
            raise ValueError(
                "a SELECTED outcome carries the record it selected; there is "
                "no selection without a selected id.")
        if self.selected_record_id not in {c.record_id for c in self.census}:
            raise ValueError(
                f"'{self.selected_record_id}' is not in its own census. A "
                f"selection absent from the candidate set it was drawn from is "
                f"a record nobody can check.")


# =====================================================================
# THE POLICY
# =====================================================================

class AttentionPolicy:
    """`attention-policy.v1`. Deterministic, pure, and named in data.

    Holds NO handles and NO state. It is constructed rather than being a bare
    function so that its identity and its Foundry-contract slot travel with it
    to the record, which is what "a named, versioned object" means.
    """

    def __init__(self, name: str = POLICY_NAME, version: str = POLICY_VERSION):
        # IDENTITY IS DATA, NOT CONVENTION. A caller may state what it believes
        # it is constructing, and a disagreement REFUSES rather than being
        # quietly resolved in this module's favour.
        if name != POLICY_NAME or version != POLICY_VERSION:
            raise PolicyIdentityMismatch(
                f"this module implements {POLICY_NAME!r} version "
                f"{POLICY_VERSION!r}; construction named {name!r} version "
                f"{version!r}. A record citing a policy that never ran is worse "
                f"than no record, because it cannot be told from a true one.")
        self.name = POLICY_NAME
        self.version = POLICY_VERSION
        self.foundry_contract = FOUNDRY_CONTRACT

    # -----------------------------------------------------------------
    # SELECTION - pure, deterministic, permutation-invariant
    # -----------------------------------------------------------------

    @staticmethod
    def _assessment(candidate: AttentionCandidate,
                    outranked_at: Optional[SelectionBasis],
                    selected: bool) -> CandidateAssessment:
        ladder = WITHIN_CATEGORY_LADDER[candidate.category]
        return CandidateAssessment(
            category=candidate.category,
            record_id=candidate.record_id,
            ordering_key=tuple(rung(candidate) for _, rung in ladder),
            key_names=tuple(basis.value for basis, _ in ladder),
            outranked_at=outranked_at,
            selected=selected,
            horizon_state=candidate.horizon_state,
        )

    def select(self, view: DerivedView) -> AttentionSelection:
        """Choose the ONE record that receives attention. Reads; writes nothing.

        **PERMUTATION-INVARIANT BY CONSTRUCTION** (Ruling 71): every rung's key
        is a function of the candidate alone, and the final rung is a total
        order on unique ids, so the outcome cannot depend on the order the
        candidates arrived in.
        """
        by_category = {
            category: view.candidates_in(category)
            for category in CATEGORY_PRECEDENCE
        }

        winning: Optional[AttentionCategory] = None
        for category in CATEGORY_PRECEDENCE:
            if by_category[category]:
                winning = category
                break

        if winning is None:
            # THE HONEST EMPTY. Recorded by the caller, never raised.
            return AttentionSelection(
                outcome=SelectionOutcome.NOTHING_ATTENDABLE,
                selected_category=None,
                selected_record_id=None,
                deciding_basis=None,
                census=())

        contenders = list(by_category[winning])
        # Every candidate in a LOSING category is outranked by precedence alone
        # and never enters a ladder. Recorded, so the census is complete.
        assessments: List[CandidateAssessment] = [
            self._assessment(c, SelectionBasis.CATEGORY_PRECEDENCE, False)
            for category in CATEGORY_PRECEDENCE if category is not winning
            for c in by_category[category]
        ]

        if len(contenders) == 1:
            basis = SelectionBasis.CATEGORY_PRECEDENCE
        else:
            basis = None
            for rung_basis, rung in WITHIN_CATEGORY_LADDER[winning]:
                keyed = [(rung(c), c) for c in contenders]
                best = min(key for key, _ in keyed)
                survivors = [c for key, c in keyed if key == best]
                for key, candidate in keyed:
                    if key != best:
                        assessments.append(
                            self._assessment(candidate, rung_basis, False))
                contenders = survivors
                if len(contenders) == 1:
                    basis = rung_basis
                    break
            if basis is None:
                # UNREACHABLE: the identity rung keys on unique ids and cannot
                # tie. Raising rather than picking is deliberate - if the
                # backstop stops being a total order the right answer is a loud
                # failure, not a quiet choice.
                raise RuntimeError(
                    "the within-category ladder exhausted every rung without "
                    "selecting; the record-identity backstop is no longer a "
                    "total order.")

        selected = contenders[0]
        assessments.append(self._assessment(selected, None, True))
        return AttentionSelection(
            outcome=SelectionOutcome.SELECTED,
            selected_category=winning,
            selected_record_id=selected.record_id,
            deciding_basis=basis,
            census=tuple(assessments))
