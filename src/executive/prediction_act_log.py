"""M9-b: the prediction act log -- every evaluation, every walk, chained.

Hundred-eighteenth entry (PATH v144), M9_GROUNDING.md section M9-b: *"Every
propagation is an act record in the house discipline (chained log, census of
dependencies walked, the kernel's disposition per obligation)."*

The house append-only shape at a new prefix (the routing log's, via the
Q-family's): mint derived from the file under the file's lock with no cached
ordinal (Ruling 69), Ruling 53's sentinel at BOTH the mint and the read, the
write GATES the act, Ruling 78's funnel owns the append, and -- born after the
chain -- **every line it will ever carry is chain-verifiable from genesis.**

ONE LOG, TWO ACT KINDS, ONE ORDINAL STREAM
-------------------------------------------------------------------------------
An EVALUATION act records one clerical read (the criterion as recorded, the
surface state actually read, the outcome, and the reason where UNRESOLVED --
an inability to evaluate is an ACT fact, not a prediction fact, and this line
is its only trace). A PROPAGATION act records one whole walk: the falsified
prediction, the FULL dependency census with each submission's kernel
disposition as received, and the policy identity. They share the `PRA-`
ordinal stream and the schema's required core; the audit registration is data
(`act_log_audit.PREDICTION_ACT_LOG_SCHEMA`), and the audit never repairs.

THE WALK'S ACT WRITES AFTER THE SUBMISSIONS -- CRASH HONESTY, STATED
-------------------------------------------------------------------------------
The act carries the submissions' REAL dispositions, so it cannot precede them.
A crash between the submissions and this append leaves admissions without
their walk record -- and that is the honest state: **the kernel's ledger is
its own truth, and this log records the WALK, not the admissions.** A reader
reconstructing that gap finds every obligation in the kernel's own store,
sourced `propagation-policy.v1:PRD-...`, which is exactly where a kernel fact
belongs. A log-write failure fails the act LOUDLY (the raise propagates); it
never unwinds a kernel record, because nothing anywhere unwinds a kernel
record.

Gate-1 referents ride per house precedent: these acts adjudicate nothing and
apply no epistemic pressure themselves (the walk SUBMITS; the kernel
dispositions), so the referent fields answer NOT_APPLICABLE -- except where
the answer lives elsewhere on the record itself: an UNRESOLVED evaluation's
reason IS its rejection answer, and a walk's rejections live in the
dependency census (`IN_CANDIDATE_CENSUS`, the referent that says WHERE).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.executive.act_chain import CHAIN_KEY, chain_for_next_line
from src.executive.criterion_evaluator import (CriterionEvaluation,
                                               EvaluationOutcome)
from src.executive.gate_one import GateOneReferent
from src.executive.propagation_policy import FalsificationWalk
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = ["PredictionActLog", "PredictionActLogUnreadable"]


class PredictionActLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived.

    Never falls back to a number, and never answers an unreadable log with an
    empty read -- reporting that nothing was ever evaluated or walked is a
    stronger and falser claim than "I could not look".
    """


class PredictionActLog:
    """Append-only log of prediction acts. Its ONLY write is its own file."""

    ID_PREFIX = "PRA-"

    def __init__(self,
                 log_path: str = "data/runtime/logs/prediction_acts.jsonl"):
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
            raise PredictionActLogUnreadable(
                f"the prediction act log at '{self.log_path}' exists and "
                f"cannot be read, so the next {self.ID_PREFIX} ordinal is "
                f"UNKNOWN. Minting one anyway could write an id that already "
                f"names a different act.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module. Chained from genesis."""
        payload = dict(payload)
        payload[CHAIN_KEY] = chain_for_next_line(self.log_path)
        validate_record_value(payload, path="prediction_act_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def record_evaluation(self, evaluation: CriterionEvaluation
                          ) -> Dict[str, Any]:
        """Record ONE clerical evaluation. RAISES on a failed write.

        Recorded for EVERY evaluation outcome: a decisive one's resolution
        lives in the prediction ledger (its own truth), and an UNRESOLVED
        one's ONLY trace is this line -- the inability is an act fact.
        """
        if not isinstance(evaluation, CriterionEvaluation):
            raise TypeError(
                f"record_evaluation takes a CriterionEvaluation, got "
                f"{type(evaluation).__name__} -- a raw payload would skip "
                f"the evaluator's own vocabulary.")
        unresolved = (evaluation.outcome
                      is EvaluationOutcome.UNRESOLVED_AT_EVALUATION)
        with mint_lock(self.log_path):
            payload = {
                "kind_of_record": "prediction_evaluation_act",
                "act_id": self._next_id(),
                "prediction_id": evaluation.prediction_id,
                "evaluation": evaluation.as_dict(),
                "gate_one": {
                    "pressure_class_applied":
                        GateOneReferent.NOT_APPLICABLE.value,
                    "unexercised_defeaters":
                        GateOneReferent.NOT_APPLICABLE.value,
                    # An UNRESOLVED evaluation's reason IS the answer to what
                    # was refused; a decisive one refused nothing.
                    "rejection_reason": (
                        evaluation.reason if unresolved
                        else GateOneReferent.NOT_APPLICABLE.value),
                },
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC.
                "recorded_at": datetime.now().isoformat(),
            }
            self._append(payload)
        return payload

    def record_propagation(self, walk: FalsificationWalk) -> Dict[str, Any]:
        """Record ONE whole walk, AFTER its submissions, with their real
        dispositions. RAISES on a failed write -- loudly, and the submissions
        stand as kernel records regardless (see the module docstring)."""
        if not isinstance(walk, FalsificationWalk):
            raise TypeError(
                f"record_propagation takes a FalsificationWalk, got "
                f"{type(walk).__name__} -- a raw payload would skip the "
                f"policy's own census.")
        with mint_lock(self.log_path):
            payload = {
                "kind_of_record": "prediction_propagation_act",
                "act_id": self._next_id(),
                "prediction_id": walk.prediction_id,
                "policy": {"identity": walk.policy_name,
                           "version": walk.policy_version},
                "resolution_criterion": walk.resolution_criterion,
                "dependency_census": [s.as_dict() for s in walk.submissions],
                "gate_one": {
                    "pressure_class_applied":
                        GateOneReferent.NOT_APPLICABLE.value,
                    "unexercised_defeaters":
                        GateOneReferent.NOT_APPLICABLE.value,
                    # Per-dependency rejections live ON this record, in the
                    # census -- the referent that says WHERE.
                    "rejection_reason":
                        GateOneReferent.IN_CANDIDATE_CENSUS.value,
                },
                "recorded_at": datetime.now().isoformat(),
            }
            self._append(payload)
        return payload

    def acts(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable act line, IN APPEND ORDER. FORENSIC ONLY.

        AN UNREADABLE EXISTING LOG RAISES TYPED; a MISSING one is a
        legitimate empty history.
        """
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise PredictionActLogUnreadable(
                f"the prediction act log at '{self.log_path}' exists and "
                f"cannot be read, so no fact about any act can be derived "
                f"from it.") from failure
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
                        and data.get("kind_of_record") in (
                            "prediction_evaluation_act",
                            "prediction_propagation_act")):
                    out.append(data)
        return tuple(out)
