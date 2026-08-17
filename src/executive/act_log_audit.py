"""The act-log anomaly instrument. REPORT-ONLY, in Ruling 79's discipline.

Discharges the gap M7-d measured and reported: **no instrument anywhere in the
tree caught a mutated act-log line.** A well-formed field edit round-tripped
undetected; a torn line was SILENTLY DROPPED by floor semantics; two lines edited
to share an id lowered the mint floor and set up a reissue nobody could see.

This is the read side of the answer. The write side is `act_chain` - forward
hash-chaining on every new record - because the well-formed-edit class is
uncatchable without redundancy, and no reader can conjure redundancy that the
writer never laid down.

A POSITIVE OBLIGATES A REPORT AND NOTHING ELSE
-------------------------------------------------------------------------------
No quarantine, no refusal, no repair. **REPAIR IS FORBIDDEN OUTRIGHT** and the
prohibition is pinned by driving a real tamper and asserting the log is
BYTE-UNCHANGED afterwards - Ruling 79's own pin form, because a detector that
edits what it detects is indistinguishable afterwards from the tamper it found.

Ruling 79's reasoning for refusing the alternatives applies unchanged here.
Quarantine adjudicates; refusal converts a survived corruption into an
unsurvivable one; and this instrument runs against a log whose corruption
**cannot change a single decision** (M7-d pin 7), so there is nothing to protect
the system FROM - only a reader's account of history to keep honest.

NOTHING CONSUMES THE FINDINGS
-------------------------------------------------------------------------------
No decision path reads them, and the day one is wanted that is its own ruling
(Ruling 72's no-consumer form). This matters more here than usual: the act logs
are NON-CONSTITUTIVE by design, and an integrity mechanism that made them
load-bearing would have inverted M7-d's whole result. **The instrument reads the
logs; the Executive still does not.**

A DOOR, NOT A LOOP. Every verb is externally invoked; nothing here schedules.

ERA HONESTY IS LAW
-------------------------------------------------------------------------------
Lines written before the chain existed carry no chain field and yield chain
findings NEVER. They are reported as `PRE_CHAIN` era and are
UNVERIFIABLE-BY-CHAIN, **which is a state rather than a defect**. The other three
finding kinds apply to every era, because a torn line, a bad ordinal and a
missing key are readable without any redundancy at all.

COINS: the `ActLogFinding` kind vocabulary (five members) and `LineEra`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.executive.act_chain import CHAIN_KEY, chain_over, strip_terminator

__all__ = [
    "FindingKind", "LineEra", "ActLogFinding", "ActLogReport",
    "SELECTION_LOG_SCHEMA", "INQUIRY_LOG_SCHEMA", "ROUTING_LOG_SCHEMA",
    "LogSchema", "audit_act_log",
]


class FindingKind(str, Enum):
    """WHAT IS WRONG WITH A LINE. Closed at five, coined here.

    **GAP AND DUPLICATE ARE SEPARATE MEMBERS, a deliberate divergence from the
    specification's single "ordinal anomaly".** Ruling 29's law: one type
    covering two causes cannot say which happened, and these two have opposite
    meanings. A GAP says a record that was minted is MISSING - something was
    removed, or a write was lost. A DUPLICATE says two lines wear one id, which
    is the REISSUE SETUP M7-d's census measured: it lowers the derived mint
    floor, so the next mint collides. A reader who could not tell those apart
    would not know whether to look for a lost record or a forged one.
    """

    #: Bytes that will not parse. Floor semantics still DROP the line from
    #: replay - what changes is that the drop is now REPORTED rather than silent.
    TORN_LINE = "torn_line"
    #: A missing ordinal in the minted sequence.
    ORDINAL_GAP = "ordinal_gap"
    #: Two lines wearing one id - the reissue setup.
    ORDINAL_DUPLICATE = "ordinal_duplicate"
    #: A chained-era line whose recorded chain does not match the previous
    #: line's bytes. NEVER raised for a pre-chain line.
    CHAIN_BREAK = "chain_break"
    #: A line that parses but lacks a key its own record type requires.
    SCHEMA_VIOLATION = "schema_violation"


class LineEra(str, Enum):
    """Whether a line was written before or after the chain existed.

    Carried on the report so a reader knows what the absence of chain findings
    MEANS for a given stretch of history: verified, or simply unverifiable.
    """

    PRE_CHAIN = "pre_chain"
    CHAINED = "chained"
    #: A TORN line's era cannot be known - the bytes will not parse, so nobody
    #: can say whether they once carried a chain field. Reporting such a line as
    #: PRE_CHAIN would assert it predates the chain, which is a claim this
    #: instrument has no evidence for; the whole point of the two-absences cut
    #: is not to manufacture facts about records that cannot be read.
    UNDETERMINED = "undetermined"


@dataclass(frozen=True)
class ActLogFinding:
    """ONE anomaly. Facts only - it recommends nothing and grants nothing."""

    kind: FindingKind
    #: Zero-based index of the offending line in the file, as read.
    line_number: int
    era: LineEra
    #: The recorded id where one could be parsed. `None` on a torn line, which
    #: is honest: a line that will not parse has no id to report.
    record_id: Optional[str]
    detail: str

    def as_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind.value, "line_number": self.line_number,
                "era": self.era.value, "record_id": self.record_id,
                "detail": self.detail}


@dataclass(frozen=True)
class ActLogReport:
    """What one audit found. EPHEMERAL - it is never written anywhere.

    A persisted report would be a store, and this instrument owns none: Ruling
    63's refusal of a cached projection, at a new surface.
    """

    path: str
    lines_read: int
    findings: Tuple[ActLogFinding, ...]
    #: How many lines fall in each era - the honest census of what this audit
    #: was ABLE to verify by chain, beside what it did verify.
    pre_chain_lines: int
    chained_lines: int

    @property
    def clean(self) -> bool:
        return not self.findings

    def as_dict(self) -> Dict[str, Any]:
        return {"path": self.path, "lines_read": self.lines_read,
                "pre_chain_lines": self.pre_chain_lines,
                "chained_lines": self.chained_lines,
                "clean": self.clean,
                "findings": [f.as_dict() for f in self.findings]}


@dataclass(frozen=True)
class LogSchema:
    """What a given act log's lines must carry, and how their ids are shaped."""

    kind_of_record: str
    id_field: str
    id_prefix: str
    required_keys: Tuple[str, ...]


SELECTION_LOG_SCHEMA = LogSchema(
    kind_of_record="attention_selection", id_field="selection_id",
    id_prefix="SEL-",
    required_keys=("kind_of_record", "selection_id", "policy_name",
                   "policy_version", "outcome", "candidate_census", "gate_one"))

INQUIRY_LOG_SCHEMA = LogSchema(
    kind_of_record="inquiry_act", id_field="inquiry_id", id_prefix="INQ-",
    required_keys=("kind_of_record", "inquiry_id", "generator_name",
                   "generator_version", "discrepancy_class",
                   "source_record_ids", "partition", "derivation_depth",
                   "kernel_disposition", "gate_one"))


#: M8-b REGISTRATION - DATA ONLY, no audit-code change. The schema mechanism is
#: a frozen dataclass precisely so a new act log joins the instrument by
#: declaring its shape rather than by teaching the auditor a new special case.
#:
#: **THIS LOG IS CHAINED FROM GENESIS**, unlike its two siblings: it was born
#: after the chain existed, so it has no pre-chain era and every line it will
#: ever carry is chain-verifiable.
ROUTING_LOG_SCHEMA = LogSchema(
    kind_of_record="routing_act", id_field="routing_id", id_prefix="RTE-",
    required_keys=("kind_of_record", "routing_id", "target_kind", "target_id",
                   "routing", "gate_one", "self_assessment"))


def _ordinal(record_id: Any, prefix: str) -> Optional[int]:
    """The ordinal behind an id, or `None`. The WHOLE remainder must be digits.

    Stricter than a search, deliberately: this validates a complete recorded
    field rather than hunting an id inside arbitrary text, so `SEL-00010` can
    never read as `SEL-0001` (Ruling 64's rider, and `divergence._ordinal`'s
    own shape).
    """
    if not isinstance(record_id, str) or not record_id.startswith(prefix):
        return None
    tail = record_id[len(prefix):]
    return int(tail) if tail.isdigit() else None


def _raw_lines(path: Path) -> List[bytes]:
    """Every line's RAW BYTES, in file order, blank segments dropped.

    Split exactly as `act_chain.last_line_bytes` splits, because the two must
    agree about what "the previous line" is or the verification would be
    checking a different thing than the writer chained.
    """
    if not path.exists():
        return []
    data = path.read_bytes()
    if not data:
        return []
    stripped = [strip_terminator(line) for line in data.split(b"\n")]
    return [line for line in stripped if line != b""]


def audit_act_log(path: Any, schema: LogSchema) -> ActLogReport:
    """Read one act log and report every anomaly. WRITES NOTHING.

    A door, externally invoked. It opens the file for READING and nothing else -
    there is no write mode, no `mkdir`, and no repair verb anywhere in this
    module.
    """
    path = Path(path)
    raw = _raw_lines(path)
    findings: List[ActLogFinding] = []
    pre_chain = chained = 0
    previous_ordinal: Optional[int] = None
    seen_ordinals: Dict[int, int] = {}

    for index, line in enumerate(raw):
        try:
            record = json.loads(line.decode("utf-8"))
            if not isinstance(record, dict):
                raise ValueError("not an object")
        except (ValueError, UnicodeDecodeError) as failure:
            # REPORTED-AND-DROPPED. The line is still excluded from replay by
            # the logs' own floor semantics - what this changes is that the
            # exclusion stops being silent.
            findings.append(ActLogFinding(
                kind=FindingKind.TORN_LINE, line_number=index,
                era=LineEra.UNDETERMINED, record_id=None,
                detail=f"line will not parse and is excluded from replay: "
                       f"{failure}"))
            # NOT counted in either era census: an unreadable line belongs to
            # neither, and adding it to one would inflate a count a reader uses
            # to judge how much of the history is chain-verifiable.
            continue

        era = LineEra.CHAINED if CHAIN_KEY in record else LineEra.PRE_CHAIN
        if era is LineEra.CHAINED:
            chained += 1
        else:
            pre_chain += 1
        record_id = record.get(schema.id_field)

        missing = [key for key in schema.required_keys if key not in record]
        if missing:
            findings.append(ActLogFinding(
                kind=FindingKind.SCHEMA_VIOLATION, line_number=index, era=era,
                record_id=record_id if isinstance(record_id, str) else None,
                detail=f"missing required key(s): {', '.join(sorted(missing))}"))

        # ---- THE CHAIN. Chained era ONLY - era honesty is law. ----
        if era is LineEra.CHAINED:
            expected = chain_over(raw[index - 1] if index > 0 else None)
            recorded = record.get(CHAIN_KEY)
            if recorded != expected:
                findings.append(ActLogFinding(
                    kind=FindingKind.CHAIN_BREAK, line_number=index, era=era,
                    record_id=record_id if isinstance(record_id, str) else None,
                    detail="recorded chain does not match the previous line's "
                           "bytes: the previous line, this line's chain field, "
                           "or both have been altered since it was written"))

        # ---- THE ORDINAL SEQUENCE. Every era - no redundancy needed. ----
        ordinal = _ordinal(record_id, schema.id_prefix)
        if ordinal is not None:
            if ordinal in seen_ordinals:
                findings.append(ActLogFinding(
                    kind=FindingKind.ORDINAL_DUPLICATE, line_number=index,
                    era=era, record_id=record_id,
                    detail=f"id already used at line "
                           f"{seen_ordinals[ordinal]}; two lines wearing one "
                           f"id lower the derived mint floor and set up a "
                           f"reissue"))
            elif previous_ordinal is not None and ordinal > previous_ordinal + 1:
                findings.append(ActLogFinding(
                    kind=FindingKind.ORDINAL_GAP, line_number=index, era=era,
                    record_id=record_id,
                    detail=f"ordinal jumps from {previous_ordinal} to "
                           f"{ordinal}; a minted record is missing"))
            seen_ordinals.setdefault(ordinal, index)
            previous_ordinal = max(previous_ordinal or 0, ordinal)

    return ActLogReport(path=str(path), lines_read=len(raw),
                        findings=tuple(findings), pre_chain_lines=pre_chain,
                        chained_lines=chained)
