"""M7-b: the attention selection log -- what the Executive attended to, and why.

**THE RULED PRECEDENT IS THE GOAL ARBITER'S EXAMINATION LOG** (Ruling 73): an
Executive-domain selector owning ONE append-only act log was ruled acceptable
there, and this is that shape at a new prefix. CAE's / O1's / O3's / Q1's / Q2's
store discipline is copied ON PURPOSE (Ruling 72's reasoning verbatim): writing a
second subtly-different append-only store would be re-deciding settled questions
by accident.

L10 IS SATISFIED BECAUSE THIS RECORDS ACTS, NOT WORKING STATE
-------------------------------------------------------------------------------
The Executive holds no constitutive state; its working state is
`DerivedView`, recomputed from the kernel every observation. This log is the
history of what it DID, which is a different thing from what it IS.

**AND NOTHING READS IT BACK INTO A DECISION.** `derive()` never touches it, the
policy never touches it, and no module in `src/` consumes it - Ruling 72's
no-consumer form, pinned tree-wide, red the day a consumer appears, which is
exactly when that consumer needs its ruling. This is stronger here than at the
arbiter, which DOES read its own log for the least-recently-examined rung: this
policy has no recency term, so the log is genuinely write-only from the system's
point of view. That is what makes a cold-rebuilt loop select the same next item.

    THE COST IS STATED RATHER THAN HIDDEN: because nothing reads it, this log
    cannot make the policy rotate. See the persistence note on
    `attention_policy.CATEGORY_PRECEDENCE` - rotation among goals is the
    ARBITER's, by ruling.

THE WRITE GATES THE SELECTION
-------------------------------------------------------------------------------
`record()` RAISES on a failed write and the selection does not stand. This is
the acquisition ledger's and O1's reasoning, not an analogy: an act taken
without its record has lost its place in logical time, and an attention
allocation nobody can later inspect is precisely the invisible venue decision L5
abolishes. It is a DELIBERATE departure from Ruling 11's observer-never-gates
rule, on Ruling 45's stated ground - that rule protects a SUPPRESSION, and this
gates an ACT.

THE GATE-1 TRIPLE, HANDLED HONESTLY FOR A NON-DISPOSITION RECORD
-------------------------------------------------------------------------------
BUILD_CONTRACT's disposition-record adequacy names three fields: pressure class
applied, defeaters named-not-exercised, and rejection reason. **A SELECTION IS
NOT A DISPOSITION** - it allocates attention and adjudicates nothing - so two of
the three have NO REFERENT here, and they are recorded as explicitly
not-applicable rather than invented or omitted. **ABSENT IS AN ANSWER** (Docket
H's cut, Ruling 45's `CriterionResult.ABSENT`): an empty defeater list would
read as "we looked and there were none", which is a claim this record has no
standing to make, and omitting the fields would leave a reader unable to tell a
non-referent from an oversight. The rejection-reason requirement IS met, by the
per-candidate census: every non-selected candidate carries the rung that
outranked it.

COINS: the `SEL-` prefix and the `GateOneReferent` vocabulary. No threshold, no
weight, no score, and no priority field on any record.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.executive.attention_policy import (
    AttentionSelection,
    CandidateAssessment,
    SelectionBasis,
    SelectionOutcome,
)
from src.executive.derived_view import AttentionCategory
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "GateOneReferent", "AttentionSelectionRecord", "SelectionLog",
    "SelectionLogUnreadable",
]


class GateOneReferent(str, Enum):
    """How a Gate-1 adequacy field is answered by a NON-DISPOSITION record.

    Two members, and neither is a value: they say WHERE the answer is, or that
    the question does not apply. A record that silently omitted a Gate-1 field
    would be indistinguishable from one whose author forgot it.
    """

    # The field names something a selection does not do. Not zero, not empty.
    NOT_APPLICABLE = "not_applicable"
    # The requirement is met, and the per-candidate census is where it is met.
    IN_CANDIDATE_CENSUS = "in_candidate_census"


class SelectionLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived.

    Raised at the moment an id would be minted, and NEVER falling back to a
    number: two selections wearing one id are two attention allocations nobody
    can tell apart afterwards, in an append-only record where nothing can
    disambiguate them later (3a:112).

    Also raised by `selections()` on an unreadable EXISTING log. Returning `()`
    there would report that nothing has ever been attended to, which is a
    stronger and falser claim than "I could not look" - Ruling 74's finding,
    applied at drafting rather than discovered by a firing pin.
    """


@dataclass(frozen=True)
class AttentionSelectionRecord:
    """ONE recorded act of attention: who was considered, who won, what decided.

    Frozen and append-only. A selection record is the history of an event that
    happened; editing one would make the Executive's own account of its
    attention rewritable, which is the defect QL1 abolishes one layer up.

    IT CARRIES NO AUTHORITY. Selecting a record for attention is not acting on
    it, not resolving it, and not adopting anything.
    """

    selection_id: str
    policy_name: str
    policy_version: str
    outcome: SelectionOutcome
    selected_record_id: Optional[str]
    selected_category: Optional[AttentionCategory]
    deciding_basis: Optional[SelectionBasis]
    census: Tuple[CandidateAssessment, ...]
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "attention_selection",
            "selection_id": self.selection_id,
            # THE POLICY THAT RAN, BY NAME AND VERSION. L5: a record that did
            # not say which chooser chose would leave the chooser invisible
            # even though the choice was written down.
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "outcome": self.outcome.value,
            "selected_record_id": self.selected_record_id,
            "selected_category": (None if self.selected_category is None
                                  else self.selected_category.value),
            "deciding_basis": (None if self.deciding_basis is None
                               else self.deciding_basis.value),
            "candidate_census": [c.as_dict() for c in self.census],
            # THE GATE-1 TRIPLE. See the module docstring: two have no referent
            # for a selection and say so; the third is met by the census.
            "gate_one": {
                "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
                "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
                "rejection_reason": GateOneReferent.IN_CANDIDATE_CENSUS.value,
            },
            "recorded_at": self.recorded_at,
        }


class SelectionLog:
    """Append-only log of attention selections. Its ONLY write is its own file."""

    ID_PREFIX = "SEL-"

    def __init__(self,
                 log_path: str = "data/runtime/logs/attention_selections.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the SAME COMMIT as the store.
        self.log_path = Path(log_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the log: the file
        # is the log. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal. Every mint derives from the
        # file, under the file's lock, across derive -> mint -> append.

    # -----------------------------------------------------------------
    # THE MINT - Ruling 69's shared helper at a new prefix
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `SEL-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's whole property set inherits: derived at the moment of
        minting, RAW-TEXT scanned so an ordinal on a torn line is still seen and
        never reissued, and Ruling 53's sentinel intact - `None` IFF the log
        EXISTS and the read raised, a MISSING log a legitimate `0`.
        """
        return derive_max_ordinal(self.log_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Callers hold `mint_lock`."""
        seq = self._derive_seq()
        if seq is None:
            raise SelectionLogUnreadable(
                f"the selection log at '{self.log_path}' exists and cannot be "
                f"read, so the next {self.ID_PREFIX} ordinal is UNKNOWN. "
                f"Minting one anyway could write an id that already names a "
                f"different attention allocation.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module, and it targets only its own log.

        Batch 66's writer discipline: the validator runs BEFORE `mkdir` and
        BEFORE the append, so a refused entry leaves no file and no directory it
        did not already need; `allow_nan=False`; and there is NO `default=`, so
        a non-canonical leaf REFUSES rather than being silently stringified into
        a permanent record (Ruling 66 - REFUSAL, NEVER COERCION).

        There is no write mode in this file at all: Ruling 78's funnel owns the
        append and the tree-wide AST census forbids a mode-`"a"` open outside
        it, so durability is inherited rather than re-argued.
        """
        validate_record_value(payload, path="attention_selection_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    # -----------------------------------------------------------------
    # THE DOOR - externally invoked, zero internal callers
    # -----------------------------------------------------------------

    def record(self, selection: AttentionSelection, policy_name: str,
               policy_version: str) -> AttentionSelectionRecord:
        """Record ONE act of attention - including an act that found nothing.

        **A `NOTHING_ATTENDABLE` SELECTION IS RECORDED, NOT SKIPPED.** That the
        Executive looked and found a quiet kernel is a fact about the run, and a
        log that only contained selections would make quiet indistinguishable
        from not having run at all.

        RAISES on a failed write, and the caller must not continue: see the
        module docstring. The exception propagates unchanged - this module never
        converts a write failure into a returned value.
        """
        with mint_lock(self.log_path):
            record = AttentionSelectionRecord(
                selection_id=self._next_id(),
                policy_name=policy_name,
                policy_version=policy_version,
                outcome=selection.outcome,
                selected_record_id=selection.selected_record_id,
                selected_category=selection.selected_category,
                deciding_basis=selection.deciding_basis,
                census=selection.census,
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC. Ordering here
                # is by `SEL-` ordinal, exactly as the obligation ledger orders
                # by `SEQ-` rather than by its `created_wall`.
                recorded_at=datetime.now().isoformat(),
            )
            self._append(record.as_dict())
        return record

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def selections(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable selection line, IN APPEND ORDER. FORENSIC ONLY.

        Returns raw dicts rather than rebuilt records, deliberately: nothing in
        `src/` consumes this, so a rebuild path would be machinery for a
        consumer that does not exist and must not quietly acquire one. A reader
        that wants typed records is a new consumer and needs its ruling.

        Reads the FILE rather than `self.entries`: the log spans processes and
        the in-memory mirror does not. **ERA HONESTY** - a line is returned AS
        IT WAS WRITTEN; nothing is backfilled or defaulted. A line that will not
        parse contributes nothing and is never coerced (floor semantics).

        AN UNREADABLE EXISTING LOG RAISES TYPED; a MISSING one is a legitimate
        empty history, because absence is a first run and not a fault.
        """
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise SelectionLogUnreadable(
                f"the selection log at '{self.log_path}' exists and cannot be "
                f"read, so no fact about any attention allocation can be "
                f"derived from it. Answering from an empty read would report "
                f"that nothing has ever been attended to.") from failure
        out: List[Dict[str, Any]] = []
        with handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                if (isinstance(data, dict)
                        and data.get("kind_of_record") == "attention_selection"):
                    out.append(data)
        return tuple(out)
