"""M8-c: utility measurement under L3. History that nothing reads.

**THE ENTIRE VALUE OF THIS SLICE IS WHAT IT REFUSES TO DO.** It measures what
HAPPENED to a routed episode - which rung ran, how many points of logical time
were consumed, and how the kernel disposed of it - and then it stops. Nothing
scores it, nothing compares it, and nothing anywhere reads a utility record back
into a decision.

L3'S BAR, VERBATIM IN EFFECT: **utility feeds routing ONLY under a future ruling
and NEVER touches standing.** Until that ruling exists it feeds NOTHING, and the
absence is structural rather than promised: **no module in `src/` imports this
one.** Not the policies, not the classifier, not the generator, not `derive()`,
not the kernel - and not the loop either.

    THAT LAST EXCLUSION IS A JUDGMENT CALL, AND IT IS THE STRONGER READING.
    Every other Executive act log is reachable from `ExecutiveLoop`, which is
    where governed acts live. This one is not, because the specification's
    no-consumer bar is written as "no src path imports, reads, or RECEIVES" -
    and a loop holding the handle would receive it. Measurement is a DOOR a
    caller opens with the handles it already has (the `act_log_audit` shape),
    so the tree-wide import count is ZERO rather than one. When a consumer
    ruling arrives it will decide where this rides; until then, nowhere is the
    honest answer and the pin can assert it exactly.

NOTHING EVALUATIVE IS WRITABLE, NOT MERELY DISCOURAGED
-------------------------------------------------------------------------------
The record shape has no slot for a judgment: no score, no rating, no "adequate",
no "good". **Adequacy was the ROUTING record's statement** - it said whether the
episode reached its ruled minimum rung and recorded the debt where it did not.
This record says what happened afterwards. Conflating the two would let a
measurement quietly re-open a question the routing already answered on the
record.

THE ORDINAL COST IS TWO RECORDED POINTS AND THEIR DIFFERENCE
-------------------------------------------------------------------------------
Both anchors are `SEQ-` tokens READ OFF KERNEL RECORDS, on the one monotonic
clock this tree mints logical time from. No wall clock is read anywhere in this
module (pinned by import-absence), and no unit is coined: the cost is a count of
points on a clock that already existed, not a duration in anything.

    **DIVERGENCE, WITH ITS MEASUREMENT - THE ANCHOR IS THE EPISODE, NOT THE
    ROUTING.** The specification says "between the episode's ROUTING and its
    disposition". Measured at `3e2745f`: **the routing record carries no `SEQ-`
    ordinal at all** - it mints an `RTE-` id and stamps a wall-clock
    `recorded_at`, and nothing else. Stamping one would be a routing-record
    change, which this slice's bounds forbid. So the two RECORDED ordinals that
    exist are the episode's own: the `seq` on its OPEN record and the `seq` on
    its DISPOSITION record, both minted by `EpisodeRecord._stamp` from the
    shared clock. That is arguably the better anchor anyway - the episode is the
    unit that SPANS the work, and a routing is an instant inside it - but it is
    a divergence and it is recorded as one rather than quietly substituted.

COINS: the `UTL-` prefix. No vocabulary, no threshold, no unit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.executive.act_chain import CHAIN_KEY, chain_for_next_line
from src.executive.gate_one import GateOneReferent
from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = ["UtilityRecord", "UtilityLog", "UtilityLogUnreadable",
           "UnknownRouting", "UnmeasurableEpisode", "measure_episode"]


class UtilityLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the log EXISTS and its mint cannot be derived."""


class UnknownRouting(Exception):
    """The routing reference names no recorded routing act.

    A measurement of a routing that never happened is not a weak measurement,
    it is a fabricated one - and it would sit in an append-only record citing an
    `RTE-` id nobody can resolve.
    """


class UnmeasurableEpisode(Exception):
    """The episode carries no recorded disposition, so nothing HAPPENED yet.

    **HALF-MEASURED EPISODES ARE NOT MEASURED** (Docket H: an absent fact is not
    a zero). An episode still open has consumed points that are not yet a cost,
    because the second anchor does not exist; recording it now would put a
    number on the record that the next append would falsify.
    """


@dataclass(frozen=True)
class UtilityRecord:
    """What HAPPENED to one routed episode. Facts only, and no judgment.

    There is deliberately NO evaluative field. A reader who wants to know
    whether this was a good use of cognition has the routing record's adequacy
    statement and this record's facts, and must do that reasoning themselves -
    under a ruling, when one exists.
    """

    utility_id: str
    #: The routing act this measures. An `RTE-` reference, verified to resolve.
    routing_id: str
    #: The rung that actually ran, as the routing record recorded it.
    rung: str
    #: The episode, and how the kernel disposed of it.
    disposition_id: str
    disposition_kind: str
    #: THE TWO RECORDED ANCHORS, verbatim `SEQ-` tokens off kernel records.
    opened_seq: str
    disposed_seq: str
    #: Their difference. A count of points on a clock that already existed.
    ordinal_cost: int
    recorded_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind_of_record": "utility_measurement",
            "utility_id": self.utility_id,
            "routing_id": self.routing_id,
            "rung": self.rung,
            "disposition_id": self.disposition_id,
            "disposition_kind": self.disposition_kind,
            "opened_seq": self.opened_seq,
            "disposed_seq": self.disposed_seq,
            "ordinal_cost": self.ordinal_cost,
            "gate_one": {
                # A MEASUREMENT IS NOT A DISPOSITION. It applies no pressure,
                # exercises no defeater, and refuses nothing - so all three
                # referents are explicitly not-applicable. ABSENT IS AN ANSWER.
                "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
                "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
                "rejection_reason": GateOneReferent.NOT_APPLICABLE.value,
            },
            "recorded_at": self.recorded_at,
        }


class UtilityLog:
    """Append-only log of utility measurements. Its ONLY write is its own file.

    CHAINED FROM GENESIS: born after the chain existed, so it has no pre-chain
    era and every line it will ever carry is chain-verifiable.
    """

    ID_PREFIX = "UTL-"

    def __init__(self,
                 log_path: str = "data/runtime/logs/utility_measurements.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/`,
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
            raise UtilityLogUnreadable(
                f"the utility log at '{self.log_path}' exists and cannot be "
                f"read, so the next {self.ID_PREFIX} ordinal is UNKNOWN. "
                f"Minting one anyway could write an id that already names a "
                f"different measurement.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write in this module. Batch 66's writer discipline."""
        payload = dict(payload)
        payload[CHAIN_KEY] = chain_for_next_line(self.log_path)
        validate_record_value(payload, path="utility_measurement_entry")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.log_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    def record(self, record: UtilityRecord) -> UtilityRecord:
        """Append ONE measurement. RAISES on a failed write.

        Takes an already-built record rather than raw parts: `measure_episode`
        is the only thing that builds one, and it builds it by READING kernel
        records - so there is no door here through which an unverified
        measurement can enter.
        """
        with mint_lock(self.log_path):
            stamped = UtilityRecord(
                utility_id=self._next_id(), routing_id=record.routing_id,
                rung=record.rung, disposition_id=record.disposition_id,
                disposition_kind=record.disposition_kind,
                opened_seq=record.opened_seq, disposed_seq=record.disposed_seq,
                ordinal_cost=record.ordinal_cost,
                recorded_at=record.recorded_at)
            self._append(stamped.as_dict())
        return stamped

    def measurements(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable measurement line, IN APPEND ORDER. FORENSIC ONLY.

        **NOTHING IN `src/` CALLS THIS.** It exists for a reader of history, and
        the day a decision path wants it, that is its own ruling.
        """
        if not self.log_path.exists():
            return ()
        try:
            handle = open(self.log_path, "r", encoding="utf-8")
        except OSError as failure:
            raise UtilityLogUnreadable(
                f"the utility log at '{self.log_path}' exists and cannot be "
                f"read, so no fact about any measurement can be derived from "
                f"it. Answering from an empty read would report that nothing "
                f"has ever been measured.") from failure
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
                        and data.get("kind_of_record") == "utility_measurement"):
                    out.append(data)
        return tuple(out)


# =====================================================================
# THE MEASUREMENT ACT - a door, reading records only
# =====================================================================

#: THE EPISODE RECORD SPELLS ITS ANCHOR TWO WAYS, MEASURED NOT ASSUMED. The
#: OPEN record carries `opened_seq`; every later record carries `seq`. The first
#: draft read `seq` on both and was REFUSED by this module's own missing-anchor
#: guard - which is the guard working: a cost with no recorded anchor is not
#: computed from something else. Both names are tried, in this order, and
#: neither is invented.
_SEQ_FIELDS: Tuple[str, ...] = ("seq", "opened_seq")


def _seq_of(record: Optional[Dict[str, Any]]) -> Optional[str]:
    for field in _SEQ_FIELDS:
        token = (record or {}).get(field)
        if isinstance(token, str):
            return token
    return None


def measure_episode(routing_id: str, episode_id: str, *, routings: Any,
                    episodes: Any, log: UtilityLog,
                    recorded_at: str = "") -> UtilityRecord:
    """Measure ONE completed episode and record it. READS, then appends once.

    Both references are VERIFIED against records before anything is built:
      * `routing_id` must resolve to a recorded routing act, or `UnknownRouting`;
      * `episode_id` must carry BOTH an open record and a recorded disposition,
        or `UnmeasurableEpisode`.

    Neither is defaulted and neither is guessed. An unverifiable reference in an
    append-only record is worse than no record, because nothing afterwards can
    tell it from a true one.

    **`recorded_at` IS A PARAMETER, NOT A CLOCK READ.** This module imports no
    time source at all (pinned), so the observation timestamp - which every
    house record carries and none reads - is supplied by the caller or left
    empty. That keeps the whole measurement path deterministic, which is what
    lets pin 1 compare two runs byte for byte.
    """
    routing = next((r for r in routings.routings()
                    if r.get("routing_id") == routing_id), None)
    if routing is None:
        raise UnknownRouting(
            f"'{routing_id}' names no recorded routing act. A measurement of a "
            f"routing that never happened would cite an id nobody can resolve.")

    opened = None
    disposed = None
    for line in episodes.read_all():
        if line.get("episode_id") != episode_id:
            continue
        # THE RECORD-TYPE STRINGS ARE THE EPISODE RECORD'S OWN, and the first
        # draft got the open one wrong (`"opened"` rather than
        # `"episode_opened"`) - which the refusal caught immediately, because a
        # missing anchor is refused rather than defaulted. Compared as VALUES
        # rather than imported as members, so this module keeps its promise to
        # import no kernel class; the real vocabulary is pinned against them.
        if line.get("record_type") == "episode_opened":
            opened = line
        elif line.get("record_type") == "disposition":
            disposed = line

    if opened is None or disposed is None:
        raise UnmeasurableEpisode(
            f"'{episode_id}' is not a completed episode: "
            f"opened={opened is not None}, disposed={disposed is not None}. "
            f"Half-measured episodes are not measured - an episode still open "
            f"has consumed points that are not yet a cost, because the second "
            f"anchor does not exist.")

    opened_seq, disposed_seq = _seq_of(opened), _seq_of(disposed)
    if opened_seq is None or disposed_seq is None:
        raise UnmeasurableEpisode(
            f"'{episode_id}' carries a record without a `SEQ-` token, so the "
            f"ordinal cost has no recorded anchor. It is not inferred from "
            f"anything else.")

    from src.filtration.obligation_ledger import seq_ordinal
    start, end = seq_ordinal(opened_seq), seq_ordinal(disposed_seq)
    if start is None or end is None:
        raise UnmeasurableEpisode(
            f"'{episode_id}' carries an unparseable `SEQ-` token; the cost is "
            f"a difference of two recorded ordinals or it is nothing.")

    return log.record(UtilityRecord(
        utility_id="",                       # minted by the log, under its lock
        routing_id=routing_id,
        rung=str(routing.get("routing", {}).get("routed_rung", "")),
        disposition_id=episode_id,
        disposition_kind=str(disposed.get("outcome", "")),
        opened_seq=opened_seq, disposed_seq=disposed_seq,
        ordinal_cost=end - start, recorded_at=recorded_at))
