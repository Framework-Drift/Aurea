"""M8-b: the routing act log -- where each episode's cognition was sent, and why.

The house append-only shape at a new prefix (Ruling 73's examination log, via
M7-b's and M7-c's): mint derived from the file under the file's lock with no
cached ordinal (Ruling 69), Ruling 53's sentinel at BOTH the mint and the read,
the write GATES the act, and Ruling 78's funnel owns the append.

**CHAINED FROM GENESIS, WHICH IS THE ONE THING THIS LOG HAS THAT ITS SIBLINGS DO
NOT.** The selection and inquiry logs were born before the chain existed, so they
carry a PRE-CHAIN era that is unverifiable-by-chain forever - era honesty, and
permanent. This log is born after it: line 0 chains over the declared genesis
constant, so **every line it will ever carry is chain-verifiable.** There is no
legacy era here and there never will be.

WHAT THE RECORD CARRIES, AND WHY EACH PART
-------------------------------------------------------------------------------
The FULL stake derivation is EMBEDDED rather than referenced. A routing record
that cited a classification living somewhere else would be checkable only by
someone who still had that somewhere else; Test 7's challenge - "what was
considered, under which policy version" - has to be answerable from the record
alone. The rung census rides for the same reason: a reader must be able to see
that the ladder was consulted and what each rung answered, not merely where the
episode landed.

**THE SHORTFALL IS A FIELD, NOT A LOG LEVEL.** When one exists it is on the
record with its four facts; when none exists the field is explicitly absent. A
warning that isn't a record would be exactly the invisible venue decision L5
abolishes.

**THE SELF-ASSESSMENT SLOT IS PRESENT AND UNPOPULATED.** Phase 8's sentence:
model self-assessment is admissible as RECORDED INPUT, never as the gate. So the
shape exists now and answers ABSENT, and `record()` REFUSES any populated value -
fail-closed, because a populated assessment with an empty ladder would be a
FABRICATED ASSESSOR: something claiming to have judged its own adequacy when
nothing occupies the rung that would have done the judging.

COINS: the `RTE-` prefix and `RoutingLogUnreadable`. The Gate-1 vocabulary is
`gate_one`'s, reused rather than redeclared.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.executive.act_chain import CHAIN_KEY, chain_for_next_line
from src.executive.escalation_policy import RoutingDecision
from src.executive.gate_one import GateOneReferent
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = ["RoutingRecord", "RoutingLog", "RoutingLogUnreadable",
           "SelfAssessmentNotAdmissible"]


class RoutingLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived.

    Never falls back to a number, and never answers an unreadable log with an
    empty read - reporting that nothing has ever been routed is a stronger and
    falser claim than "I could not look".
    """


class SelfAssessmentNotAdmissible(Exception):
    """A self-assessment was supplied while no rung above 0 is occupied.

    **FAIL-CLOSED, and the reason is not caution but arithmetic.** A
    self-assessment is an occupant's report on its own adequacy. With the ladder
    empty there is no occupant, so a populated slot would be a record of a
    judgement nobody made - a fabricated assessor. The slot exists so that the
    day an occupant arrives its assessment has somewhere ruled to go; until
    then it answers ABSENT, which is an answer.
    """


@dataclass(frozen=True)
class RoutingRecord:
    """ONE routing act. Frozen, append-only, and self-contained by design."""

    routing_id: str
    target_kind: str
    target_id: str
    #: The attention selection this routing answers, where one is known. Ids
    #: only - the join, never an embedded record (Ruling 42).
    selection_id: Optional[str]
    decision: RoutingDecision
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        payload = {
            "kind_of_record": "routing_act",
            "routing_id": self.routing_id,
            "target_kind": self.target_kind,
            "target_id": self.target_id,
            "selection_id": self.selection_id,
            # THE POLICY THAT RAN, and the FULL derivation it ran on.
            "routing": self.decision.as_dict(),
            "gate_one": {
                # A routing allocates cognition; it adjudicates nothing and
                # applies no epistemic pressure. ABSENT IS AN ANSWER.
                "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
                "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
                # A SHORTFALL IS THE REJECTION REASON WHERE ONE EXISTS: the
                # ruled minimum rung was not available, and the record says on
                # what basis. Where the routing was adequate, nothing was
                # refused.
                "rejection_reason": (
                    self.decision.shortfall.unoccupied_rung_basis.value
                    if self.decision.shortfall is not None
                    else GateOneReferent.NOT_APPLICABLE.value),
            },
            # PHASE 8'S SLOT. Present, unpopulated, and refused if supplied.
            "self_assessment": None,
            "recorded_at": self.recorded_at,
        }
        return payload


class RoutingLog:
    """Append-only log of routing acts. Its ONLY write is its own file."""

    ID_PREFIX = "RTE-"

    def __init__(self,
                 log_path: str = "data/runtime/logs/routing_acts.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # registered in `tests/conftest.py` and `scripts/soak.py` in the SAME
        # COMMIT as the store.
        self.log_path = Path(log_path)
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal.

    def _derive_seq(self) -> Optional[int]:
        return derive_max_ordinal(self.log_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        seq = self._derive_seq()
        if seq is None:
            raise RoutingLogUnreadable(
                f"the routing log at '{self.log_path}' exists and cannot be "
                f"read, so the next {self.ID_PREFIX} ordinal is UNKNOWN. "
                f"Minting one anyway could write an id that already names a "
                f"different routing act.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module. Batch 66's writer discipline.

        Validator BEFORE `mkdir` and BEFORE the append; `allow_nan=False`; no
        `default=`. **CHAINED FROM GENESIS** - this log has no pre-chain era, so
        line 0 chains over the declared genesis constant and every line it ever
        carries is verifiable.
        """
        payload = dict(payload)
        payload[CHAIN_KEY] = chain_for_next_line(self.log_path)
        validate_record_value(payload, path="routing_act_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def record(self, decision: RoutingDecision, target_kind: str,
               target_id: str, selection_id: Optional[str] = None,
               self_assessment: Any = None) -> RoutingRecord:
        """Record ONE routing act - adequate or short. RAISES on a failed write.

        `self_assessment` exists to be REFUSED in v1. It is a parameter rather
        than an absence so that the shape is visible and the refusal is
        explicit: a caller who has one learns immediately that the ladder cannot
        receive it yet, instead of discovering later that it was silently
        dropped.
        """
        if self_assessment is not None:
            raise SelfAssessmentNotAdmissible(
                "a self-assessment was supplied, but no rung above the "
                "deterministic kernel is occupied. With an empty ladder there "
                "is no occupant to have made the assessment, so recording one "
                "would be recording a judgement nobody made. The slot stays "
                "ABSENT until an occupant exists.")
        with mint_lock(self.log_path):
            record = RoutingRecord(
                routing_id=self._next_id(), target_kind=target_kind,
                target_id=target_id, selection_id=selection_id,
                decision=decision,
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC.
                recorded_at=datetime.now().isoformat())
            self._append(record.as_dict())
        return record

    def routings(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable routing line, IN APPEND ORDER. FORENSIC ONLY.

        Raw dicts, for the siblings' stated reason: nothing in `src/` consumes
        this, so a rebuild path would be machinery for a consumer that does not
        exist and must not quietly acquire one.

        AN UNREADABLE EXISTING LOG RAISES TYPED; a MISSING one is a legitimate
        empty history.
        """
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise RoutingLogUnreadable(
                f"the routing log at '{self.log_path}' exists and cannot be "
                f"read, so no fact about any routing act can be derived from "
                f"it. Answering from an empty read would report that nothing "
                f"has ever been routed.") from failure
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
                        and data.get("kind_of_record") == "routing_act"):
                    out.append(data)
        return tuple(out)
