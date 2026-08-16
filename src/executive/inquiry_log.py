"""M7-c: the inquiry act log -- what was noticed, what was asked, what drifted.

The SelectionLog's discipline verbatim at a new prefix, which is itself Ruling
73's examination-log shape: append-only, mint derived from the file under the
file's lock with no cached ordinal (Ruling 69), Ruling 53's sentinel intact at
BOTH the mint and the read, the write GATES the act, and Ruling 78's funnel owns
the append. **The shape is copied ON PURPOSE** (Ruling 72's reasoning): writing
a second subtly-different append-only store would be re-deciding settled
questions by accident.

EVERY CANDIDATE LANDS HERE - BOTH SIDES OF THE PARTITION
-------------------------------------------------------------------------------
A licensed inquiry is recorded WITH the kernel's disposition of its submission;
a drift finding is recorded and never pursued. **The forbidden outcome is a
candidate that is neither admitted nor recorded**, and it is unreachable by
construction: the act walks the generator's full output and every branch writes.

    THE ORDER IS RECORD-THEN-RETURN, AND THE ADMISSION COMES FIRST WITHIN IT.
    For a licensed candidate the kernel is asked BEFORE the line is written, so
    the line can carry what the kernel actually said rather than what the
    Executive hoped it would say. A disposition invented before the fact would
    be exactly the invisible venue decision L5 abolishes.

THE GATE-1 REFERENTS
-------------------------------------------------------------------------------
A DRIFT FINDING IS DISPOSITION-LIKE, so its REJECTION REASON is the drift basis
itself - a closed-vocabulary value, not prose. A licensed inquiry rejected
nothing, so its rejection-reason field is explicitly NOT_APPLICABLE. Pressure
class and unexercised defeaters have no referent for either: an inquiry applies
no epistemic pressure and exercises no defeater. **ABSENT IS AN ANSWER** - an
empty defeater list would claim we looked.

COINS: the `INQ-` prefix. The Gate-1 vocabulary is the selection log's, reused
rather than redeclared - a second definition of one rule is free to drift.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.executive.inquiry_generator import (
    CandidatePartition,
    DiscrepancyClass,
    DriftBasis,
    InquiryCandidate,
    LicenseBasis,
)
from src.executive.gate_one import GateOneReferent
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "KernelDisposition", "InquiryRecord", "InquiryLog", "InquiryLogUnreadable",
]


class KernelDisposition(str, Enum):
    """WHAT THE KERNEL SAID about a submission, recorded as received.

    **THESE ARE NOT THE EXECUTIVE'S JUDGEMENTS AND MUST NEVER BECOME THEM.**
    Section 5: the Executive submits; the kernel dispositions. Each member below
    mirrors an answer the obligation ledger actually returns, and the act
    records what came back without interpreting it - a submission the ledger
    called a DUPLICATE is recorded as a duplicate, not as a suppressed repeat,
    because deciding it was redundant is the kernel's half of the sentence.

    NOT_SUBMITTED is the drift side: no submission was attempted at all, which
    is a different fact from one that was attempted and refused.
    """

    ADMITTED = "admitted"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_TARGETLESS = "rejected_targetless"
    REJECTED_MALFORMED = "rejected_malformed"
    NOT_SUBMITTED = "not_submitted"


class InquiryLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived.

    Never falls back to a number. Two inquiries wearing one id are two acts
    nobody can tell apart afterwards, in an append-only record where nothing can
    disambiguate them later (3a:112). Also raised by `inquiries()` on an
    unreadable EXISTING log - answering from an empty read would report that
    nothing has ever been asked.
    """


@dataclass(frozen=True)
class InquiryRecord:
    """ONE inquiry act: the discrepancy, its provenance, and its disposition."""

    inquiry_id: str
    generator_name: str
    generator_version: str
    discrepancy_class: DiscrepancyClass
    source_record_ids: Tuple[str, ...]
    partition: CandidatePartition
    derivation_depth: int
    disposition: KernelDisposition
    ancestor_goal_id: Optional[str] = None
    license_basis: Optional[LicenseBasis] = None
    drift_basis: Optional[DriftBasis] = None
    horizon_state: Optional[str] = None
    # The obligation the kernel minted, when it admitted one. Recorded so the
    # Executive's act and the kernel's record can be joined afterwards without
    # anyone re-deriving the match.
    obligation_id: Optional[str] = None
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "inquiry_act",
            "inquiry_id": self.inquiry_id,
            "generator_name": self.generator_name,
            "generator_version": self.generator_version,
            "discrepancy_class": self.discrepancy_class.value,
            "source_record_ids": list(self.source_record_ids),
            "partition": self.partition.value,
            "derivation_depth": self.derivation_depth,
            "ancestor_goal_id": self.ancestor_goal_id,
            "license_basis": (None if self.license_basis is None
                              else self.license_basis.value),
            "drift_basis": (None if self.drift_basis is None
                            else self.drift_basis.value),
            "horizon_state": self.horizon_state,
            "kernel_disposition": self.disposition.value,
            "obligation_id": self.obligation_id,
            "gate_one": {
                "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
                "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
                # A DRIFT finding is disposition-like: the basis IS the reason.
                # A licensed inquiry rejected nothing.
                "rejection_reason": (
                    self.drift_basis.value if self.drift_basis is not None
                    else GateOneReferent.NOT_APPLICABLE.value),
            },
            "recorded_at": self.recorded_at,
        }


class InquiryLog:
    """Append-only log of inquiry acts. Its ONLY write is its own file."""

    ID_PREFIX = "INQ-"

    def __init__(self,
                 log_path: str = "data/runtime/logs/inquiry_acts.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the SAME COMMIT as the store.
        self.log_path = Path(log_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the log.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal.

    def _derive_seq(self) -> Optional[int]:
        """The highest `INQ-` ordinal ON DISK, or `None` if UNDERIVED."""
        return derive_max_ordinal(self.log_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Callers hold `mint_lock`."""
        seq = self._derive_seq()
        if seq is None:
            raise InquiryLogUnreadable(
                f"the inquiry log at '{self.log_path}' exists and cannot be "
                f"read, so the next {self.ID_PREFIX} ordinal is UNKNOWN. "
                f"Minting one anyway could write an id that already names a "
                f"different inquiry act.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module, and it targets only its own log.

        Batch 66's writer discipline: validator BEFORE `mkdir` and BEFORE the
        append; `allow_nan=False`; no `default=`, so a non-canonical leaf
        REFUSES rather than being stringified into a permanent record. There is
        no write mode in this file at all - Ruling 78's funnel owns the append.
        """
        validate_record_value(payload, path="inquiry_act_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def record(self, candidate: InquiryCandidate, generator_name: str,
               generator_version: str,
               disposition: KernelDisposition = KernelDisposition.NOT_SUBMITTED,
               obligation_id: Optional[str] = None) -> InquiryRecord:
        """Record ONE inquiry act - licensed or drift, submitted or not.

        RAISES on a failed write, and the caller must not continue: an act taken
        without its record has lost its place in logical time, and an inquiry
        nobody can inspect is the unprovenanced question the heading forbids.
        The exception propagates unchanged.
        """
        with mint_lock(self.log_path):
            record = InquiryRecord(
                inquiry_id=self._next_id(),
                generator_name=generator_name,
                generator_version=generator_version,
                discrepancy_class=candidate.discrepancy_class,
                source_record_ids=candidate.source_record_ids,
                partition=candidate.partition,
                derivation_depth=candidate.derivation_depth,
                disposition=disposition,
                ancestor_goal_id=candidate.ancestor_goal_id,
                license_basis=candidate.license_basis,
                drift_basis=candidate.drift_basis,
                horizon_state=candidate.horizon_state,
                obligation_id=obligation_id,
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC. Ordering is by
                # `INQ-` ordinal, exactly as the obligation ledger orders by
                # `SEQ-` rather than by its `created_wall`.
                recorded_at=datetime.now().isoformat(),
            )
            self._append(record.as_dict())
        return record

    def inquiries(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable act line, IN APPEND ORDER. FORENSIC ONLY.

        Raw dicts rather than rebuilt records, for the selection log's stated
        reason: nothing in `src/` consumes this, so a rebuild path would be
        machinery for a consumer that does not exist and must not quietly
        acquire one.

        **AND THE GENERATOR MUST NEVER READ IT.** Dedup by self-inspection would
        be the Executive dispositioning its own submissions, which is the
        kernel's half of section 5 - pinned as import-absence, red the day a
        consumer appears.

        AN UNREADABLE EXISTING LOG RAISES TYPED; a MISSING one is a legitimate
        empty history, because absence is a first run and not a fault.
        """
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise InquiryLogUnreadable(
                f"the inquiry log at '{self.log_path}' exists and cannot be "
                f"read, so no fact about any inquiry act can be derived from "
                f"it. Answering from an empty read would report that nothing "
                f"has ever been asked.") from failure
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
                        and data.get("kind_of_record") == "inquiry_act"):
                    out.append(data)
        return tuple(out)
