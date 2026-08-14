"""
episode_record.py - M3-A slice A, kernels K3 and K11. THE EPISODE RECORD.

**AN EPISODE THAT WAS NOT BOUNDED BEFORE ITS PRESSURE IS NOT AN EPISODE**, and
**NOTHING SURVIVES WITHOUT AN IDENTIFIABLE COMPLETED PRESSURE EPISODE** (K11).
Ruling 74's law at the layer below attention: the bound is DECLARED AT OPEN and
FIXED FOREVER, and the terminal state is honest about whether the episode ran
out of room before it ran out of doubt.

WHAT THIS STORES AND WHAT IT DOES NOT
-------------------------------------------------------------------------------
It records what an episode DID. It runs nothing: no loop, no scheduler, no
internal caller anywhere in `src/`. Every door is externally invoked - the
Q-family's pattern (Rulings 72/73/74) - and this module imports nothing it could
command. **It cannot mint a scar, write a doctrine, or touch the Codex**, and the
absence of those imports is the enforcement rather than a promise (Ruling 70's
enforcement-by-scope).

**A DISPOSITION SETTLES THE RECORD, NOT THE WORLD.** `SURVIVED` on an episode
promotes nothing: no doctrine changes, no scar forms, no pressure is released.
What survives collapse is still decided where it has always been decided.

THE COUNTING RULE - THE LOAD-BEARING PIECE
-------------------------------------------------------------------------------
When an episode's APPLIED-PRESSURE COUNT HAS REACHED ITS BOUND, the legal
outcomes are exactly `UNRESOLVED_AT_BOUND`, `SUSPENDED` and
`CARRIED_CONTRADICTION`. **`SURVIVED` IS UNPRODUCIBLE THERE**, and so are
`REVISED` and `COLLAPSED`: an episode that used every pressure it declared and
still wants to claim a conclusion is claiming one the bound says it did not
reach. The refusal names `UNRESOLVED_AT_BOUND` in its message, because the
honest terminal state is the one the caller is being asked to use instead.

**"REACHED" IS `>=`, NOT `>`, AND THE CHOICE IS STATED RATHER THAN LEFT TO BE
READ OFF THE OPERATOR.** The bound is the number of pressures the episode
declared it would apply. Having applied that many, it has no further pressure to
apply, so a conclusion drawn at that moment is drawn with nothing left to test
it. Ruling 34-A made the opposite choice for the saturation horizon and said so
explicitly for the same reason - the comparison is a decision, and a decision
that lives only in an operator is one nobody can find later.

This is the mechanism that makes **"ran out of room" DISTINGUISHABLE FROM
"withstood testing."** Without it both end as SURVIVED and the record cannot
tell them apart afterwards, which is the one thing an episode record exists to
prevent.

PRESSURE DEBT IS PERMANENT (K11)
-------------------------------------------------------------------------------
Every entry in `unexercised_defeaters` becomes its own `PRESSURE_DEBT` record.
It is never netted off, never discharged by a later disposition, and never
summarised into a count. A defeater somebody NOTICED and did not exercise is a
standing fact about how much testing a claim actually received, and Ruling 23's
law binds: unresolved pressure never leaves silently.

`adequacy` IS RECORDED AND NEVER COMPARED
-------------------------------------------------------------------------------
It is a STRING - a declaration about how adequate the pressure was - and no
comparison, arithmetic, threshold or branch anywhere in this module reads it.
A NUMERIC adequacy would be a coined magnitude at the exact point survival is
decided, which is §9 standing bar #5's target and this codebase has refused it
nine times (Rulings 28, 33, 45, 50, 60, 63, 73, 74 among them). **It REPORTS;
it never GATES.** AST-pinned.

LOGICAL TIME
-------------------------------------------------------------------------------
`mint_seq_token` is imported from `obligation_ledger` - THE FUNCTION, not the
class - so the two stores share ONE clock implementation and the
zero-internal-callers pin (which binds on the CLASSES) stays exact. Wall clock
is recorded as observation and **never read by any logic path**, AST-pinned;
ordering is by `SEQ-` ordinal, always.

VOCABULARY COLLISION CENSUS
-------------------------------------------------------------------------------
Run tree-wide before coining - see `obligation_ledger`'s docstring for the full
table. The one that matters most here: **`EpisodeOutcome.SUSPENDED` is NOT
`echonet.Verdict.SUSPENDED`.** That one is a COLLAPSE verdict about a claim;
this one is a DISPOSITION about an episode. Ruling 33 pinned SUSPEND/SUSPENDED
disjointness at the ORE/HAIL boundary for exactly this reason, and nothing here
converts between the two vocabularies.

VOCABULARIES ARE GOVERNED CONTENT, NOT KERNEL. The closed sets below are v1;
they evolve through episodes, not through edits. v1 exists so the first record
is typed rather than free text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.filtration.obligation_ledger import SEQ_PREFIX, mint_seq_token
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "EpisodeRecordType",
    "ShapingActKind",
    "PressureClass",
    "EpisodeOutcome",
    "DefeaterKind",
    "REQUIRED_INTERPRETATION_FIELDS",
    "LEGAL_OUTCOMES_AT_BOUND",
    "EpisodeRecord",
    "EpisodeLogUnreadable",
    "UnboundedEpisode",
    "ClosedVocabularyViolation",
    "IllegalOutcomeAtBound",
    "SurvivalWithoutPressure",
    "EpisodeAlreadyDisposed",
    "UnknownEpisode",
    "MalformedInterpretation",
    "PrecedenceProofFailed",
    "UnknownDefeater",
]


# =====================================================================
# TYPED REFUSALS - Ruling 29: different CAUSES get different TYPES
# =====================================================================

class EpisodeLogUnreadable(Exception):
    """The log exists and cannot be read, so the next ordinal is UNKNOWN.

    Ruling 53's sentinel. Never falls back to a number.
    """


class UnboundedEpisode(Exception):
    """An episode opened without a positive integer bound.

    An unbounded episode of pressure is one that can always apply one more test
    and therefore never has to say it ran out - which is the whole thing the
    bound exists to make impossible.
    """


class ClosedVocabularyViolation(Exception):
    """A value outside a closed v1 vocabulary.

    ONE TYPE FOR THREE SURFACES, and that is Ruling 29 applied rather than
    ignored: the CAUSE is identical at all three (a member that is not in a
    closed set), and only the vocabulary differs - which the message names.
    Ruling 29 forbids one type covering two different CAUSES, not one type
    covering one cause at several sites.
    """


class IllegalOutcomeAtBound(Exception):
    """A conclusion claimed by an episode that had reached its bound.

    Distinct from `SurvivalWithoutPressure` on purpose: this one means the
    episode ran out of room, the other means it never applied any pressure at
    all. One type for both would make a spent episode indistinguishable from an
    untested one - Ruling 29's defect exactly.
    """


class SurvivalWithoutPressure(Exception):
    """SURVIVED claimed on an episode with no PRESSURE_APPLIED record (K11)."""


class EpisodeAlreadyDisposed(Exception):
    """A second disposition. The first one settled the record permanently."""


class UnknownEpisode(Exception):
    """No EPISODE_OPENED record for this id in this log."""


class MalformedInterpretation(Exception):
    """A defeater registered without the fields its KIND requires.

    Distinct from `ClosedVocabularyViolation` on purpose (Ruling 29): that one
    means the KIND is not a member, this one means the kind is fine and its
    INTERPRETATION is incomplete. One type for both would make "you named a
    defeater class that does not exist" indistinguishable from "you named a
    real one and did not say what it means."
    """


class PrecedenceProofFailed(Exception):
    """The prediction's criteria do not PREDATE its outcome on the record.

    A defeater built on a prediction whose criteria cannot be shown to precede
    its outcome is a defeater built on a prediction that may have been written
    to fit what happened - which is the exact thing Ruling 61 exists to make
    unwritable, arriving one layer up as an unprovable citation.
    """


class UnknownDefeater(Exception):
    """A `defeater_ref` naming no DEFEATER_REGISTERED record on this episode."""


# =====================================================================
# VOCABULARY - v1, GOVERNED CONTENT
# =====================================================================

class EpisodeRecordType(str, Enum):
    EPISODE_OPENED = "episode_opened"
    SHAPING_ACT = "shaping_act"
    PRESSURE_APPLIED = "pressure_applied"
    PRESSURE_DEBT = "pressure_debt"
    DEFEATER_REGISTERED = "defeater_registered"
    DISPOSITION = "disposition"


class ShapingActKind(str, Enum):
    """K3: the ONLY way episode-shaping enters the record.

    An act that shaped what the episode considered, but is not itself pressure.
    """
    CLASSIFICATION = "classification"
    DECOMPOSITION = "decomposition"
    CONTEXT_ASSEMBLY = "context_assembly"
    ADMISSION = "admission"
    ATTENTION = "attention"
    ESCALATION = "escalation"
    PRESSURE_SELECTION = "pressure_selection"


class PressureClass(str, Enum):
    """What KIND of test was applied. Classes, never scores."""
    MODEL_ADVERSARIAL = "model_adversarial"
    PRECOMMITTED_PREDICTION = "precommitted_prediction"
    PRIMARY_SOURCE = "primary_source"
    REPRODUCED_COUNTEREXAMPLE = "reproduced_counterexample"
    FORMAL_DERIVATION = "formal_derivation"


class EpisodeOutcome(str, Enum):
    """How an episode ended. `SUSPENDED` here is a DISPOSITION, not a verdict."""
    SURVIVED = "survived"
    REVISED = "revised"
    SUSPENDED = "suspended"
    COLLAPSED = "collapsed"
    UNRESOLVED_AT_BOUND = "unresolved_at_bound"
    CARRIED_CONTRADICTION = "carried_contradiction"


class DefeaterKind(str, Enum):
    """M3-B: WHAT KIND OF THING DEFEATS A CLAIM. Closed v1, governed content.

    **INTERPRETATION IS FIXED AT REGISTRATION**, which is this vocabulary's
    whole point. A defeater whose meaning is settled after the outcome is
    known is a defeater shaped to the outcome - Ruling 61's law (a prediction
    that was not committed before its outcome is not a prediction) applied to
    the thing that does the defeating.
    """
    FAILED_PRECOMMITTED_PREDICTION = "failed_precommitted_prediction"
    REPRODUCED_COUNTEREXAMPLE = "reproduced_counterexample"
    PRIMARY_SOURCE_CONTRADICTION = "primary_source_contradiction"
    DEMONSTRATED_INCOMPATIBILITY = "demonstrated_incompatibility"


# WHAT EACH KIND MUST SAY ABOUT ITSELF, validated AT REGISTRATION - before any
# outcome exists to shape it. A key that is PRESENT but null records ABSENT
# honestly (Ruling 58's three states); a key that is MISSING is malformed,
# because "nobody was asked" and "asked and there is none" are different facts.
REQUIRED_INTERPRETATION_FIELDS = {
    DefeaterKind.FAILED_PRECOMMITTED_PREDICTION: ("prediction_id",),
    DefeaterKind.REPRODUCED_COUNTEREXAMPLE: ("reproduction_recipe",
                                             "observed_result"),
    DefeaterKind.PRIMARY_SOURCE_CONTRADICTION: ("source_ref", "fetch_record"),
    DefeaterKind.DEMONSTRATED_INCOMPATIBILITY: ("derivation_text",
                                                "standing_refs"),
}

# Fields that must carry a real non-empty string, not merely be addressed. The
# rest may be explicitly null and are recorded as absent.
#
# `fetch_record` IS DELIBERATELY NOT HERE - BOOTSTRAP-SHAPED, era honesty
# FORWARD. The M4 acquisition boundary will populate it from real acquisition
# records; until that exists a registration carries what exists and **absent
# stays absent**. Requiring it now would force every pre-M4 caller to invent an
# acquisition record, which is the fabrication class this house has closed
# twice (Rulings 58 and 70).
SUBSTANTIVE_INTERPRETATION_FIELDS = {
    DefeaterKind.FAILED_PRECOMMITTED_PREDICTION: ("prediction_id",),
    DefeaterKind.REPRODUCED_COUNTEREXAMPLE: ("reproduction_recipe",
                                             "observed_result"),
    DefeaterKind.PRIMARY_SOURCE_CONTRADICTION: ("source_ref",),
    DefeaterKind.DEMONSTRATED_INCOMPATIBILITY: ("derivation_text",),
}

# DEMONSTRATED_INCOMPATIBILITY names EXACTLY TWO standings - an incompatibility
# is a relation between two things, and one or three of them is not one.
INCOMPATIBILITY_STANDING_COUNT = 2


# THE COUNTING RULE'S LEGAL SET. At bound, these three and nothing else.
LEGAL_OUTCOMES_AT_BOUND: frozenset = frozenset({
    EpisodeOutcome.UNRESOLVED_AT_BOUND,
    EpisodeOutcome.SUSPENDED,
    EpisodeOutcome.CARRIED_CONTRADICTION,
})


def _ids(value: Any, label: str) -> Tuple[str, ...]:
    """Recorded id references, ids ONLY. The house `_ids` shape.

    A live object crossing this boundary would be a write path into another
    owner's store that the Ruling 1 scanner structurally cannot see - the exact
    hazard Ruling 42 closed for RIL's identity threads.
    """
    if isinstance(value, str):
        raise TypeError(
            f"{label} must be a sequence of id strings, not one string - a bare "
            f"string would silently record each CHARACTER as an id.")
    out: List[str] = []
    for item in value or ():
        if not isinstance(item, str):
            raise TypeError(
                f"{label} takes recorded ID STRINGS only; got {type(item).__name__}.")
        out.append(item)
    return tuple(out)


class EpisodeRecord:
    """Append-only episode log. One file, typed records, never rewritten."""

    ID_PREFIX = "EPI-"
    DEFEATER_PREFIX = "DEF-"

    def __init__(
        self,
        log_path: str = "data/runtime/episodes/episodes.jsonl",
        peer_paths: Optional[Sequence[str]] = None,
        prediction_ledger: Any = None,
    ):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/`.
        self.log_path = Path(log_path)
        self.peer_paths: Tuple[Path, ...] = tuple(
            Path(p) for p in (peer_paths or ()))
        # M3-B: a READ-ONLY handle, DUCK-TYPED AND NEVER IMPORTED. Not importing
        # `PredictionLedger` keeps this module's import set stdlib + utils + the
        # shared clock, so the enforcement-by-scope pins stay exact - and the
        # handle is used for `read_all` ONLY. **`commit` and `resolve` are
        # AST-forbidden here**, the same guard M3-A put on `retrieve` after
        # finding it was not a read: a store handed to a reader for one question
        # is a store it can be talked into answering others with.
        self.prediction_ledger = prediction_ledger
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: THERE IS NO `self._seq`.

    # -----------------------------------------------------------------
    # MINT + WRITE
    # -----------------------------------------------------------------

    def _clock_paths(self) -> Tuple[Path, ...]:
        return (self.log_path,) + self.peer_paths

    def _next_id(self) -> str:
        seq = derive_max_ordinal(self.log_path, self.ID_PREFIX)
        if seq is None:
            raise EpisodeLogUnreadable(
                f"the episode log at '{self.log_path}' exists and cannot be "
                f"read, so the next {self.ID_PREFIX} ordinal is UNKNOWN. Two "
                f"episodes wearing one id are two pressure histories nobody can "
                f"tell apart afterwards.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write. Ruling 66's gate before `mkdir`, Ruling 78's funnel."""
        validate_record_value(payload, path="episode_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def _stamp(self, record_type: EpisodeRecordType, episode_id: str,
               extra: Dict[str, Any]) -> str:
        with mint_lock(self.log_path):
            seq = mint_seq_token(self._clock_paths())
            payload = {
                "record_type": record_type.value,
                "episode_id": episode_id,
                "seq": seq,
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC. AST-pinned.
                "wall": datetime.now().isoformat(),
            }
            payload.update(extra)
            self._append(payload)
        return seq

    # -----------------------------------------------------------------
    # THE DOORS
    # -----------------------------------------------------------------

    def open_episode(self, obligation_ids: Any, bound: Any) -> str:
        """Open a bounded episode. THE BOUND IS FIXED HERE, FOREVER.

        There is no `amend_bound`, `extend`, `rebound` or `reopen` anywhere in
        this module, and the ABSENCE is the enforcement - a method named
        `extend_bound` with a docstring saying "only before disposition" is a
        request for restraint (CLAUDE.md §3). AST-pinned.

        `obligation_ids` are RECORDED REFERENCES and are deliberately NOT
        validated against the obligation ledger - Ruling 61's `claim_refs`
        verbatim. A store that refused to record a real episode because another
        file was unavailable would be a worse record, and the join is the
        caller's.
        """
        refs = _ids(obligation_ids, "obligation_ids")
        # `bool` is an `int` in Python and `True` would pass as bound 1 - a
        # silent, plausible bound nobody declared.
        if isinstance(bound, bool) or not isinstance(bound, int) or bound < 1:
            raise UnboundedEpisode(
                f"an episode needs a POSITIVE INTEGER bound declared at open; "
                f"got {bound!r}. An episode that can always apply one more "
                f"pressure never has to report that it ran out.")
        with mint_lock(self.log_path):
            episode_id = self._next_id()
            seq = mint_seq_token(self._clock_paths())
            self._append({
                "record_type": EpisodeRecordType.EPISODE_OPENED.value,
                "episode_id": episode_id,
                "opened_seq": seq,
                "wall": datetime.now().isoformat(),
                "obligation_ids": list(refs),
                "bound": bound,
            })
        return episode_id

    def record_shaping_act(self, episode_id: str, act_kind: Any,
                           actor: Any, content: Any) -> str:
        """K3: the ONLY way episode-shaping enters the record."""
        self._require_open(episode_id)
        kind = self._member(ShapingActKind, act_kind, "act_kind")
        return self._stamp(
            EpisodeRecordType.SHAPING_ACT, episode_id,
            {"act_kind": kind.value, "actor": actor, "content": content})

    def record_pressure(self, episode_id: str, pressure_class: Any,
                        adequacy: Any,
                        unexercised_defeaters: Any = ()) -> str:
        """Record one applied pressure, and its DEBT.

        Each unexercised defeater becomes its own permanent `PRESSURE_DEBT`
        record (K11). They are never netted off and never summarised.
        """
        self._require_open(episode_id)
        pclass = self._member(PressureClass, pressure_class, "pressure_class")
        if not isinstance(adequacy, str) or not adequacy.strip():
            raise ClosedVocabularyViolation(
                f"`adequacy` is a recorded DECLARATION and must be a non-empty "
                f"string; got {adequacy!r}. It is never compared - a numeric "
                f"adequacy would be a coined magnitude at the point survival is "
                f"decided (§9 standing bar #5).")
        defeaters = _ids(unexercised_defeaters, "unexercised_defeaters")
        seq = self._stamp(
            EpisodeRecordType.PRESSURE_APPLIED, episode_id,
            {"pressure_class": pclass.value, "adequacy": adequacy})
        for defeater in defeaters:
            self._stamp(EpisodeRecordType.PRESSURE_DEBT, episode_id,
                        {"defeater": defeater, "incurred_by": pclass.value})
        return seq

    def register_defeater(self, episode_id: str, kind: Any,
                          interpretation: Any) -> str:
        """M3-B: register a TYPED defeater, INTERPRETED AT REGISTRATION.

        **A DEFEATER ALONE OBLIGATES NOTHING.** Registration writes its own
        record and does nothing else: no disposition, no status change, no
        write anywhere else. Cognition PRESSURES and evidence DISPOSES, and
        both are acts on the record - so a registered defeater becomes a
        disposition only when the disposition door is invoked with it.

        THE INTERPRETATION IS FIXED HERE AND HAS NO AMEND SURFACE. Every field
        the kind requires is validated PRESENT before any outcome exists to
        shape it - which is the whole reason the validation lives at
        registration rather than at disposition.
        """
        self._require_open(episode_id)
        defeater_kind = self._member(DefeaterKind, kind, "defeater kind")
        if not isinstance(interpretation, dict):
            raise MalformedInterpretation(
                f"a {defeater_kind.value} defeater's interpretation must be a "
                f"mapping of its required fields; got "
                f"{type(interpretation).__name__}.")

        recorded = dict(interpretation)
        required = REQUIRED_INTERPRETATION_FIELDS[defeater_kind]
        missing = [name for name in required if name not in recorded]
        if missing:
            raise MalformedInterpretation(
                f"a {defeater_kind.value} defeater requires "
                f"{list(required)}; missing {missing}. A key that is PRESENT "
                f"but null records ABSENT honestly - a key that is MISSING "
                f"means nobody was asked, and those are different facts.")

        for name in SUBSTANTIVE_INTERPRETATION_FIELDS[defeater_kind]:
            value = recorded.get(name)
            if not isinstance(value, str) or not value.strip():
                raise MalformedInterpretation(
                    f"a {defeater_kind.value} defeater's `{name}` must be a "
                    f"non-empty string; got {value!r}.")

        if defeater_kind is DefeaterKind.DEMONSTRATED_INCOMPATIBILITY:
            refs = _ids(recorded.get("standing_refs"), "standing_refs")
            if len(set(refs)) != INCOMPATIBILITY_STANDING_COUNT:
                raise MalformedInterpretation(
                    f"a demonstrated incompatibility names EXACTLY "
                    f"{INCOMPATIBILITY_STANDING_COUNT} DISTINCT standings - an "
                    f"incompatibility is a relation between two things, and one "
                    f"or three of them is not one; got {list(refs)}.")
            recorded["standing_refs"] = list(refs)

        if defeater_kind is DefeaterKind.FAILED_PRECOMMITTED_PREDICTION:
            recorded.update(self._precommitment_proof(recorded["prediction_id"]))

        with mint_lock(self.log_path):
            seq = derive_max_ordinal(self.log_path, self.DEFEATER_PREFIX)
            if seq is None:
                raise EpisodeLogUnreadable(
                    f"the episode log at '{self.log_path}' exists and cannot be "
                    f"read, so the next {self.DEFEATER_PREFIX} ordinal is "
                    f"UNKNOWN.")
            defeater_id = f"{self.DEFEATER_PREFIX}{seq + 1:04d}"
            clock = mint_seq_token(self._clock_paths())
            self._append({
                "record_type": EpisodeRecordType.DEFEATER_REGISTERED.value,
                "episode_id": episode_id,
                "defeater_id": defeater_id,
                "seq": clock,
                "wall": datetime.now().isoformat(),
                "defeater_kind": defeater_kind.value,
                "interpretation": recorded,
            })
        return defeater_id

    def _precommitment_proof(self, prediction_id: Any) -> Dict[str, Any]:
        """THE PRECEDENCE PROOF - the premium evidence engine earning its keep.

        **THE PREDICTION LEDGER RECORDS NO ORDINAL, AND THE PROOF IS BUILT ON
        WHAT IT DOES RECORD.** A `PredictionCommitment` carries `prediction_id`
        and a wall-clock `committed_at`; a `PredictionResolution` carries a
        REFERENCE plus a wall-clock `resolved_at`. There is no logical-time
        field on either - the `SEQ-` clock is this slice's, on obligations and
        episodes, and it was never stamped on a `PRD-` record.

        So precedence is read from **APPEND ORDER**, which is the ledger's own
        recorded fact and the structural heart of Ruling 61: the resolution is a
        SEPARATE APPEND and the commitment line was written before it, so the
        file reads as a history rather than a state. **The wall clock is NOT
        used**, and not merely as a preference - M3-A pinned that no logic path
        reads a clock, and a proof of precedence resting on `resolved_at` would
        be a timestamp join in the one place that must not have one.

        Ruling 61 already makes the ordinary path unwritable in the wrong order
        (`resolve` refuses an unknown id). This proves it from the RECORD rather
        than trusting it from the writer, because the file outlives the code
        that wrote it and a hand-edited or torn ledger can carry anything.
        """
        if self.prediction_ledger is None:
            raise MalformedInterpretation(
                f"a failed_precommitted_prediction defeater cites "
                f"'{prediction_id}', and no prediction ledger was supplied to "
                f"resolve it against. An unresolvable citation is not evidence; "
                f"supply the ledger or register a different kind of defeater.")

        commitment_index: Optional[int] = None
        resolution_index: Optional[int] = None
        outcome: Any = None
        criterion: Any = None
        commitment: Any = None
        # DUCK-TYPED on purpose (see `__init__`): a resolution carries an
        # `outcome`, a commitment carries an `expected_result`.
        for index, entry in enumerate(self.prediction_ledger.read_all()):
            if getattr(entry, "prediction_id", None) != prediction_id:
                continue
            if hasattr(entry, "outcome"):
                if resolution_index is None:
                    resolution_index = index
                    outcome = getattr(entry.outcome, "value", entry.outcome)
                    criterion = entry.criterion
            elif commitment_index is None:
                commitment_index = index
                commitment = entry

        if commitment_index is None:
            raise MalformedInterpretation(
                f"no commitment '{prediction_id}' is recorded in the supplied "
                f"prediction ledger. A defeater cannot cite a prediction that "
                f"was never made.")
        if resolution_index is None:
            raise PrecedenceProofFailed(
                f"'{prediction_id}' carries NO resolution, so there is no "
                f"outcome for its criteria to predate. An unresolved prediction "
                f"has not failed - it has not been settled.")
        if commitment_index >= resolution_index:
            raise PrecedenceProofFailed(
                f"'{prediction_id}' has its resolution at append position "
                f"{resolution_index} and its commitment at {commitment_index}, "
                f"so the criteria DO NOT PREDATE the outcome on the record. "
                f"Criteria written after the result they judge are criteria "
                f"shaped to it, and this defeater cannot rest on them.")

        # COPIED VERBATIM FROM THE LEDGER RECORD, not restated by the caller.
        # The resolution names WHICH criterion it met; the value copied is the
        # one fixed at COMMIT time, which is the fact worth carrying.
        criteria_field = commitment.criterion(criterion)
        return {
            "resolution_criteria": {"criterion": criterion,
                                    "recorded": criteria_field.as_dict()},
            "recorded_outcome": outcome,
            "precedence_proof": {"commitment_index": commitment_index,
                                 "resolution_index": resolution_index,
                                 "basis": "prediction_ledger_append_order"},
        }

    def defeaters(self, episode_id: str) -> Tuple[Dict[str, Any], ...]:
        """Every defeater registered on this episode, in append order."""
        return tuple(record for record in self.read_all()
                     if record.get("episode_id") == episode_id
                     and record.get("record_type")
                     == EpisodeRecordType.DEFEATER_REGISTERED.value)

    def disposition(self, episode_id: str, outcome: Any,
                    defeater_ref: Optional[str] = None) -> str:
        """Settle the episode. ONE per episode, ever.

        THE ORDER OF THE CHECKS IS PART OF THE RULE. Existence, then
        already-disposed, then the vocabulary, then the counting rule, then
        K11's floor - so a caller is told the FIRST thing wrong with the
        request rather than an incidental one.
        """
        opened = self._require_open(episode_id)
        if self._disposition_of(episode_id) is not None:
            raise EpisodeAlreadyDisposed(
                f"'{episode_id}' already carries a disposition. An episode is "
                f"settled once; a re-score afterwards is a new episode, and "
                f"rewriting this one would let the record be revised until it "
                f"read the way somebody wanted.")
        result = self._member(EpisodeOutcome, outcome, "outcome")

        bound = opened.get("bound")
        applied = self.applied_pressure_count(episode_id)
        if isinstance(bound, int) and applied >= bound:
            if result not in LEGAL_OUTCOMES_AT_BOUND:
                raise IllegalOutcomeAtBound(
                    f"'{episode_id}' has applied {applied} of its declared "
                    f"bound {bound}, so it has no pressure left to apply and "
                    f"'{result.value}' is unproducible. The honest terminal "
                    f"states here are "
                    f"'{EpisodeOutcome.UNRESOLVED_AT_BOUND.value}', "
                    f"'{EpisodeOutcome.SUSPENDED.value}' and "
                    f"'{EpisodeOutcome.CARRIED_CONTRADICTION.value}'. Running "
                    f"out of room is not the same as withstanding testing, and "
                    f"this record must be able to tell them apart later.")

        # M3-B: a cited defeater must RESOLVE, and to THIS episode's own
        # register. A dangling citation on a permanent disposition is worse
        # than no citation, because the record reads as though the reasoning
        # was grounded and nothing can afterwards say what it pointed at.
        if defeater_ref is not None:
            known = {record.get("defeater_id")
                     for record in self.defeaters(episode_id)}
            if defeater_ref not in known:
                raise UnknownDefeater(
                    f"'{defeater_ref}' is not a defeater registered on "
                    f"'{episode_id}'. Registered here: {sorted(k for k in known if k)}. "
                    f"A disposition may cite only a defeater whose "
                    f"interpretation was fixed on this episode before it.")

        if result is EpisodeOutcome.SURVIVED and applied == 0:
            raise SurvivalWithoutPressure(
                f"'{episode_id}' carries no PRESSURE_APPLIED record, so nothing "
                f"survived anything (K11). Survival requires an identifiable "
                f"completed pressure episode, not the absence of an objection.")

        return self._stamp(
            EpisodeRecordType.DISPOSITION, episode_id,
            {"outcome": result.value, "defeater_ref": defeater_ref})

    # -----------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _member(vocabulary: Any, value: Any, label: str) -> Any:
        """Coerce into a closed v1 vocabulary, or REFUSE. Never a default."""
        try:
            return vocabulary(value.value if isinstance(value, vocabulary) else value)
        except (ValueError, AttributeError):
            raise ClosedVocabularyViolation(
                f"'{value!r}' is not a member of the closed v1 {label} "
                f"vocabulary {sorted(m.value for m in vocabulary)}. The "
                f"vocabulary is GOVERNED CONTENT: it evolves through an episode "
                f"with a record behind it, never through a caller passing a new "
                f"string.") from None

    def _require_open(self, episode_id: str) -> Dict[str, Any]:
        for record in self.read_all():
            if (record.get("episode_id") == episode_id
                    and record.get("record_type")
                    == EpisodeRecordType.EPISODE_OPENED.value):
                return record
        raise UnknownEpisode(
            f"no episode '{episode_id}' was opened in this log. An act cannot "
            f"belong to an episode that was never bounded.")

    def _disposition_of(self, episode_id: str) -> Optional[Dict[str, Any]]:
        for record in self.read_all():
            if (record.get("episode_id") == episode_id
                    and record.get("record_type")
                    == EpisodeRecordType.DISPOSITION.value):
                return record
        return None

    def applied_pressure_count(self, episode_id: str) -> int:
        """How many pressures this episode APPLIED. Derived, never stored.

        Counts `PRESSURE_APPLIED` only. A `PRESSURE_DEBT` is a pressure that was
        NOT exercised, and counting it here would let noticing a defeater
        consume the same budget as testing one.
        """
        return sum(1 for record in self.read_all()
                   if record.get("episode_id") == episode_id
                   and record.get("record_type")
                   == EpisodeRecordType.PRESSURE_APPLIED.value)

    def pressure_debts(self, episode_id: str) -> Tuple[Dict[str, Any], ...]:
        """Every unexercised defeater on record. Permanent; never discharged."""
        return tuple(record for record in self.read_all()
                     if record.get("episode_id") == episode_id
                     and record.get("record_type")
                     == EpisodeRecordType.PRESSURE_DEBT.value)

    def read_all(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable line, IN APPEND ORDER, AS WRITTEN.

        ERA HONESTY: a field a later schema added is simply absent from an older
        line. Nothing is backfilled, defaulted, or dropped for missing it
        (Ruling 68's forensic law). An unparseable line contributes nothing.
        """
        if not self.log_path.exists():
            return ()
        out: List[Dict[str, Any]] = []
        with open(self.log_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                if isinstance(data, dict) and "episode_id" in data:
                    out.append(data)
        return tuple(out)
