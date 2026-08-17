"""M8-d: the challenge surface -- a decision disputed, and re-derived.

Acceptance Test 7's challenge clause. A decision record is challenged after the
fact; the adjudicator RERUNS the pure functions over the records the decision
cites and compares. **The comparison IS the verdict** - there is no judgment
step, no reviewer, and nothing to be persuaded.

    THE CENSUS RAN FIRST AND FOUND NO DOOR. Every `challenge` / `adjudicat`
    occurrence in `src/` at `0a610c0` is PROSE - docstrings describing the law,
    not a surface implementing it. So this is the proven minimum: one challenge
    record, one adjudication act, in the Executive act-log discipline.

WHY TWO LOGS RATHER THAN ONE - decided by the instrument, not by preference
-------------------------------------------------------------------------------
A challenge and its adjudication are two appends about ONE dispute, and the
prediction ledger's commit/resolve shape would have put them in one file. **The
AUDIT decides otherwise:** `audit_act_log` checks its schema's `required_keys`
against EVERY parsed line, so a mixed-kind log would report every adjudication as
a SCHEMA_VIOLATION of the challenge schema and vice versa. One schema per log is
the instrument's shape, and bending the records to share a schema would mean
padding each with the other's fields - a worse trade than a join.

ADJUDICATION CHANGES NOTHING DOWNSTREAM
-------------------------------------------------------------------------------
**A DEFECT_SUSTAINED IS A RECORD, NOT A ROLLBACK.** The challenged decision
stands exactly as it stood; what a sustained defect obligates is a future
ruling's question, and until that ruling exists nothing reads an adjudication
back into any decision. Pinned in both no-consumer forms. This is the same
boundary utility measurement draws one slice earlier, and for the same reason: a
verdict that silently moved something would be the invisible venue decision L5
abolishes, arriving through the appeals process.

REFUSED IS NOT VINDICATION
-------------------------------------------------------------------------------
A challenge the re-derivation cannot reach - a malformed reference, unreadable
records - is REFUSED AS UNADJUDICABLE with its reason, never defaulted to UPHELD.
**Inability to adjudicate is not innocence**, and a system that reported it as
such would launder every defect it happened to be unable to check. Docket H's
two-absences cut, arriving at the appeals layer.

COINS: `DefectClass` (four), `AdjudicationVerdict` (three), the `CHL-` and `ADJ-`
prefixes. No threshold, no score, no magnitude.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.executive.act_chain import CHAIN_KEY, chain_for_next_line
from src.executive.attention_policy import AttentionPolicy
from src.executive.escalation_policy import EscalationPolicy
from src.executive.gate_one import GateOneReferent
from src.executive.stake_classifier import StakeClassifier
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "DefectClass", "AdjudicationVerdict", "ChallengeRecord",
    "AdjudicationRecord", "ChallengeLog", "AdjudicationLog",
    "ChallengeLogUnreadable", "AdjudicationLogUnreadable", "UnchallengeableRecord",
    "file_challenge", "adjudicate",
]


class DefectClass(str, Enum):
    """WHAT THE CHALLENGER ASSERTS IS WRONG. Closed at four, coined here.

    **THE SET IS WHAT DETERMINISTIC RE-DERIVATION CAN ACTUALLY ADJUDICATE**, and
    that is the whole principle behind its size: a defect class the adjudicator
    could not reach would be a promise the surface cannot keep, and a challenger
    would learn that only after filing.

    Ruling 29's law applies - one member covering two causes cannot say which
    happened - so these four name four distinct places a decision can go wrong,
    and each maps to a different leg of the re-derivation.
    """

    #: A candidate the records show was OMITTED from the census, or carried a
    #: wrong ordering key. The dispute is about what was CONSIDERED.
    CENSUS_DEFECT = "census_defect"
    #: A stake condition mis-evaluated against the records it consulted. The
    #: dispute is about what the evidence SHOWED.
    DERIVATION_DEFECT = "derivation_defect"
    #: The ruled minimum rung misapplied to the stake class. The dispute is
    #: about the LAW, not the facts.
    MAPPING_DEFECT = "mapping_defect"
    #: An occupancy basis contradicted by the acquisition records. The dispute
    #: is about whether the LADDER was read correctly.
    BASIS_DEFECT = "basis_defect"


class AdjudicationVerdict(str, Enum):
    """The comparison's outcome. Three members, and the third is SCOPED.

    For an ADJUDICABLE challenge there are exactly two: the re-derivation
    reproduces the decision, or it does not. There is no partial credit and no
    third opinion, because the adjudicator holds no opinion - it reruns pure
    functions and compares.
    """

    UPHELD = "upheld"
    DEFECT_SUSTAINED = "defect_sustained"
    #: The re-derivation could not be performed at all. NEVER a substitute for
    #: UPHELD - see the module docstring.
    REFUSED_UNADJUDICABLE = "refused_unadjudicable"


class ChallengeLogUnreadable(Exception):
    """Ruling 53's sentinel at the challenge log."""


class AdjudicationLogUnreadable(Exception):
    """Ruling 53's sentinel at the adjudication log."""


class UnchallengeableRecord(Exception):
    """The challenged id names no recorded decision, or the class is unruled.

    Refused AT THE DOOR. A challenge against a record nobody can resolve would
    sit permanently in an append-only log accusing nothing, and an unruled
    defect class is a dispute the adjudicator has no leg to run.
    """


# ---------------------------------------------------------------------------
# THE RECORDS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChallengeRecord:
    """ONE dispute, as filed. The challenger's assertion, never a finding."""

    challenge_id: str
    challenged_record_id: str
    defect_class: DefectClass
    #: RECORDED BYTE-IDENTICAL and never interpreted - L1's discipline at the
    #: appeals layer. The adjudicator does not read this; it reruns the
    #: functions. The basis is here so a reader knows what was ALLEGED.
    challenger_basis: str
    challenger: str
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "decision_challenge",
            "challenge_id": self.challenge_id,
            "challenged_record_id": self.challenged_record_id,
            "defect_class": self.defect_class.value,
            "challenger_basis": self.challenger_basis,
            "challenger": self.challenger,
            "gate_one": {
                # A CHALLENGE IS NOT A DISPOSITION - it asserts, and the
                # adjudication decides. All three referents are absent here and
                # REAL on the adjudication, which is where the pressure is.
                "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
                "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
                "rejection_reason": GateOneReferent.NOT_APPLICABLE.value,
            },
            "recorded_at": self.recorded_at,
        }


@dataclass(frozen=True)
class AdjudicationRecord:
    """ONE adjudication: the re-derivation's comparison, field by field."""

    adjudication_id: str
    challenge_id: str
    challenged_record_id: str
    defect_class: DefectClass
    verdict: AdjudicationVerdict
    #: Every field where the recorded decision and the re-derivation differ,
    #: as (field, recorded, re-derived). EMPTY on UPHELD - and that emptiness
    #: is the whole content of an UPHELD verdict.
    divergences: Tuple[Tuple[str, str, str], ...]
    #: The re-derivation legs actually run. These ARE the Gate-1 defeaters:
    #: each is a way the decision could have been shown wrong and was not.
    legs_run: Tuple[str, ...]
    refusal_reason: Optional[str] = None
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "challenge_adjudication",
            "adjudication_id": self.adjudication_id,
            "challenge_id": self.challenge_id,
            "challenged_record_id": self.challenged_record_id,
            "defect_class": self.defect_class.value,
            "verdict": self.verdict.value,
            "divergences": [list(d) for d in self.divergences],
            "legs_run": list(self.legs_run),
            "refusal_reason": self.refusal_reason,
            "gate_one": {
                # **REAL REFERENTS, NOT NOT-APPLICABLE.** An adjudication IS a
                # disposition: the pressure applied is the defect class pressed,
                # the defeaters named are the legs the re-derivation ran, and
                # the rejection reason exists exactly when the challenge was
                # refused as unadjudicable.
                "pressure_class_applied": self.defect_class.value,
                "unexercised_defeaters": list(self.legs_run),
                "rejection_reason": (
                    self.refusal_reason if self.refusal_reason is not None
                    else GateOneReferent.NOT_APPLICABLE.value),
            },
            "recorded_at": self.recorded_at,
        }


# ---------------------------------------------------------------------------
# THE LOGS - the house shape, chained from genesis
# ---------------------------------------------------------------------------

class _ActLog:
    """Shared append-only mechanics. Subclasses declare prefix and error type.

    The four prior act logs each spell this out in full; a fifth and sixth
    verbatim copy would be five and six definitions of one discipline, free to
    drift. What is NOT shared is the RECORD - each log's shape is its own.
    """

    ID_PREFIX = ""
    UNREADABLE: type = Exception
    KIND = ""

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: there is no cached ordinal.

    def _next_id(self) -> str:
        seq = derive_max_ordinal(self.log_path, self.ID_PREFIX)
        if seq is None:
            raise self.UNREADABLE(
                f"the log at '{self.log_path}' exists and cannot be read, so "
                f"the next {self.ID_PREFIX} ordinal is UNKNOWN. Minting one "
                f"anyway could write an id that already names a different "
                f"record.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        payload = dict(payload)
        payload[CHAIN_KEY] = chain_for_next_line(self.log_path)
        validate_record_value(payload, path=self.KIND)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def _read(self) -> Tuple[Dict[str, Any], ...]:
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise self.UNREADABLE(
                f"the log at '{self.log_path}' exists and cannot be read, so "
                f"no fact about any record in it can be derived. Answering "
                f"from an empty read would report that nothing was ever "
                f"filed.") from failure
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
                if isinstance(data, dict) and data.get("kind_of_record") == self.KIND:
                    out.append(data)
        return tuple(out)


class ChallengeLog(_ActLog):
    ID_PREFIX = "CHL-"
    UNREADABLE = ChallengeLogUnreadable
    KIND = "decision_challenge"

    def __init__(self, log_path: str = "data/runtime/logs/challenges.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/`,
        # registered in both isolation tables in the SAME COMMIT.
        super().__init__(log_path)

    def challenges(self) -> Tuple[Dict[str, Any], ...]:
        return self._read()


class AdjudicationLog(_ActLog):
    ID_PREFIX = "ADJ-"
    UNREADABLE = AdjudicationLogUnreadable
    KIND = "challenge_adjudication"

    def __init__(self, log_path: str = "data/runtime/logs/adjudications.jsonl"):
        super().__init__(log_path)

    def adjudications(self) -> Tuple[Dict[str, Any], ...]:
        return self._read()


# ---------------------------------------------------------------------------
# THE DOORS
# ---------------------------------------------------------------------------

def _find(records: Any, field: str, value: str) -> Optional[Dict[str, Any]]:
    return next((r for r in records if r.get(field) == value), None)


def file_challenge(challenged_record_id: str, defect_class: Any,
                   challenger_basis: str, challenger: str, *,
                   log: ChallengeLog, routings: Any = None,
                   selections: Any = None,
                   recorded_at: str = "") -> ChallengeRecord:
    """File ONE challenge. REFUSES at the door, before anything is written.

    The challenged id must resolve to a REAL recorded decision - a routing
    (`RTE-`) or a selection (`SEL-`) - and the defect class must be one of the
    four ruled members. Neither is defaulted: a challenge nobody can resolve
    accuses nothing, permanently.
    """
    if not isinstance(defect_class, DefectClass):
        try:
            defect_class = DefectClass(defect_class)
        except ValueError as failure:
            raise UnchallengeableRecord(
                f"{defect_class!r} is not a ruled defect class. The four "
                f"members are what deterministic re-derivation can adjudicate; "
                f"a fifth is a manifest decision, not a caller's string."
            ) from failure

    found = None
    if challenged_record_id.startswith("RTE-") and routings is not None:
        found = _find(routings.routings(), "routing_id", challenged_record_id)
    elif challenged_record_id.startswith("SEL-") and selections is not None:
        found = _find(selections.selections(), "selection_id",
                      challenged_record_id)
    if found is None:
        raise UnchallengeableRecord(
            f"'{challenged_record_id}' names no recorded decision this door can "
            f"resolve. A challenge against a record nobody can find would sit "
            f"in an append-only log accusing nothing.")

    with mint_lock(log.log_path):
        record = ChallengeRecord(
            challenge_id=log._next_id(),
            challenged_record_id=challenged_record_id,
            defect_class=defect_class, challenger_basis=challenger_basis,
            challenger=challenger, recorded_at=recorded_at)
        log._append(record.as_dict())
    return record


def _diff(recorded: Any, rederived: Any, prefix: str = "") -> List[Tuple[str, str, str]]:
    """Field-by-field divergence between two serialized decisions.

    Recursive over dicts so the divergence NAMES THE FIELD rather than reporting
    that two large objects differ - a verdict a reader cannot act on is half a
    verdict.
    """
    out: List[Tuple[str, str, str]] = []
    if isinstance(recorded, dict) and isinstance(rederived, dict):
        for key in sorted(set(recorded) | set(rederived)):
            out.extend(_diff(recorded.get(key), rederived.get(key),
                             f"{prefix}.{key}" if prefix else key))
        return out
    if recorded != rederived:
        # `allow_nan=False` HERE TOO - Batch 66's tree-wide writer sweep
        # caught this pair, and it was right to: a divergence is serialized
        # into a permanent adjudication record, so a non-finite float would be
        # stringified into the one document that says what went wrong. Ruling
        # 66's law is REFUSAL, NEVER COERCION, and it binds every direct writer
        # rather than only the ones that felt like stores.
        out.append((prefix, json.dumps(recorded, sort_keys=True, allow_nan=False),
                    json.dumps(rederived, sort_keys=True, allow_nan=False)))
    return out


#: The re-derivation legs, per challenged record kind. DECLARED DATA: these are
#: the Gate-1 defeaters an adjudication names, so they must be the legs actually
#: run rather than a description of them.
ROUTING_LEGS: Tuple[str, ...] = (
    "stake_reclassification", "rung_census", "mapping_application")
SELECTION_LEGS: Tuple[str, ...] = ("candidate_census", "ladder_application")


def adjudicate(challenge_id: str, *, challenges: ChallengeLog,
               adjudications: AdjudicationLog, rebuild_view: Callable[[], Any],
               routings: Any = None, selections: Any = None,
               recorded_at: str = "") -> AdjudicationRecord:
    """RERUN the pure functions and compare. The comparison IS the verdict.

    `rebuild_view` is a caller-supplied zero-argument reconstruction of the
    derived view from the kernel stores. It is a CALLABLE rather than a set of
    handles so this module holds no store: the adjudicator reruns policies, and
    a module that could reach a store could be talked into writing one.
    """
    filed = _find(challenges.challenges(), "challenge_id", challenge_id)
    if filed is None:
        raise UnchallengeableRecord(
            f"'{challenge_id}' names no filed challenge.")

    challenged_id = filed["challenged_record_id"]
    defect = DefectClass(filed["defect_class"])
    is_routing = challenged_id.startswith("RTE-")
    legs = ROUTING_LEGS if is_routing else SELECTION_LEGS

    def _refuse(reason: str) -> AdjudicationRecord:
        return _write(AdjudicationRecord(
            adjudication_id="", challenge_id=challenge_id,
            challenged_record_id=challenged_id, defect_class=defect,
            verdict=AdjudicationVerdict.REFUSED_UNADJUDICABLE,
            divergences=(), legs_run=(), refusal_reason=reason,
            recorded_at=recorded_at))

    def _write(record: AdjudicationRecord) -> AdjudicationRecord:
        with mint_lock(adjudications.log_path):
            stamped = AdjudicationRecord(
                adjudication_id=adjudications._next_id(),
                challenge_id=record.challenge_id,
                challenged_record_id=record.challenged_record_id,
                defect_class=record.defect_class, verdict=record.verdict,
                divergences=record.divergences, legs_run=record.legs_run,
                refusal_reason=record.refusal_reason,
                recorded_at=record.recorded_at)
            adjudications._append(stamped.as_dict())
        return stamped

    try:
        source = (routings.routings() if is_routing
                  else selections.selections())
    except Exception as failure:                       # unreadable records
        return _refuse(f"the cited records cannot be read: {failure}")

    field = "routing_id" if is_routing else "selection_id"
    challenged = _find(source, field, challenged_id)
    if challenged is None:
        return _refuse(
            f"'{challenged_id}' is no longer resolvable in the decision "
            f"records, so the re-derivation has nothing to compare against. "
            f"THIS IS NOT VINDICATION - inability to adjudicate is not "
            f"innocence.")

    try:
        view = rebuild_view()
        if is_routing:
            stake = StakeClassifier().classify(
                challenged["target_kind"], challenged["target_id"], view)
            rederived = EscalationPolicy().route(stake, view).as_dict()
            recorded = challenged["routing"]
        else:
            selection = AttentionPolicy().select(view)
            rederived = {
                "outcome": selection.outcome.value,
                "selected_record_id": selection.selected_record_id,
                "selected_category": (None if selection.selected_category is None
                                      else selection.selected_category.value),
                "deciding_basis": (None if selection.deciding_basis is None
                                   else selection.deciding_basis.value),
                "candidate_census": [c.as_dict() for c in selection.census],
            }
            recorded = {key: challenged.get(key) for key in rederived}
    except Exception as failure:
        return _refuse(f"the re-derivation could not be performed: {failure}")

    divergences = tuple(_diff(recorded, rederived))
    return _write(AdjudicationRecord(
        adjudication_id="", challenge_id=challenge_id,
        challenged_record_id=challenged_id, defect_class=defect,
        verdict=(AdjudicationVerdict.UPHELD if not divergences
                 else AdjudicationVerdict.DEFECT_SUSTAINED),
        divergences=divergences, legs_run=legs, recorded_at=recorded_at))
