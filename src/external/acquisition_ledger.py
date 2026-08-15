"""
acquisition_ledger.py - M4-alpha. THE ACQUISITION LEDGER.

    **AN ARRIVAL THAT WAS NOT RECORDED AT THE BOUNDARY IS NOT AN ARRIVAL.**

Ruling 61's law (a prediction that was not committed before its outcome is not a
prediction), Ruling 72's (a goal that was not committed before its pursuit is not
a goal) and Ruling 58's (a claim whose origin cannot be recorded is not
perceived), arriving at the thing all three presuppose: THE EXTERNAL ARRIVAL
ITSELF. Grounds heading Phase 4 - "every model exchange and tool result
permanently recorded; state transitions deterministic given prior state plus
recorded acquisitions; nondeterminism confined to acquisition points."

WHAT WAS MISSING, AND IT WAS NOT A FIELD - IT WAS THE EVENT
-------------------------------------------------------------------------------
The M4 census (grounding, tree at `86f5148`) found external arrivals entering at
exactly TWO doors - user input at `AureaCore.process_input`, and model assertions
through `model_provider.ingest_model_assertion` - and **NO ARRIVAL RECORD OF ANY
KIND**: no arrival index, no correlation id, nothing durable at the boundary.
What survived an arrival was what it BECAME - an echo, a claim, an origin
declaration - never the arrival.

That is not a gap in provenance; provenance was already first-class. It is that
**the boundary had no logical time of its own**, so "deterministic given prior
state plus recorded acquisitions" was not a testable sentence: there were no
recorded acquisitions to be given. This store is what makes Phase 4's claim
answerable, and M4-gamma's replay is the answer.

THE ORDINAL IS THE ARRIVAL INDEX - ONE CLOCK, NOT TWO FIELDS
-------------------------------------------------------------------------------
The `ACQ-` ordinal minted for a record IS that arrival's position in the
boundary's logical time. There is deliberately no second sequence field beside
it (M3-A's stores carry a `SEQ-` token because TWO stores share one clock; here
there is one store and it IS the clock), and `arrival_index` is DERIVED from the
id at read time rather than stored - L3, and Rulings 63/65's refusal of a stored
derivation, at the field where it would be most tempting.

WALL CLOCK IS RECORDED AND NEVER READ - M3-A's discipline verbatim.
`recorded_wall` is an observation, kept because a forensic record that cannot say
roughly when is worth less. No comparison, no arithmetic, no sort and no branch
anywhere in `src/` reads it, and that is AST-pinned. Ordering is by ordinal.

THE CORRELATION IS A RECORDED ID, NEVER A MINTED SECOND ONE
-------------------------------------------------------------------------------
`correlation_id` joins the halves of ONE exchange - a model request and its
response are two arrivals sharing one correlation - and it is **THE `ACQ-` ID OF
THE EXCHANGE'S FIRST ARRIVAL**, defaulting to the record's own id when it opens
the exchange. So a single arrival correlates with itself, and a two-half exchange
correlates on the half that came first.

**NOTHING IS MINTED FOR IT AND NO CLOCK IS READ.** A fresh uuid or a timestamp
would be a second identity vocabulary at the one boundary whose whole purpose is
to have exactly one, and M4-beta exists to KILL wall-clock minting rather than
add a sixth. A correlation is a function of a recorded fact.

THE JOIN TO WHAT AN ARRIVAL BECOMES POINTS ONE WAY, AND RULING 58'S OWN
STRUCTURE FORCES THE DIRECTION
-------------------------------------------------------------------------------
The grounding asks that the acquisition record the CLM "when known". It cannot,
and the reason is structural rather than an omission: **this ledger is
append-only with no update family**, and the acquisition is recorded BEFORE the
claim id exists - the arrival is what the mint is for. Writing the CLM onto the
acquisition afterwards would require exactly the update path that is forbidden.

So THE LATER ARTIFACT REFERENCES THE EARLIER: `ClaimAncestryRecord.acquisition_ref`.
This is Ruling 60's finding verbatim, one layer out - that ruling faced the
identical fork for `Echo.claim_id` and resolved it the identical way, because a
deep-frozen record minted before its successor exists cannot carry a reference to
it. **The join is still readable in BOTH directions** (`claim_for` /
`ClaimAncestryLedger.get`); what is one-way is the WRITE, and that is the whole
point of an append-only boundary record.

SECTION 4's TRIPLE, v1 - RECORDED FROM THE FIRST RECORD, CONSUMED BY NOTHING
-------------------------------------------------------------------------------
  * `integrity` - STRUCTURAL. Section 4's three clauses (chain intact, channel
    identified, record durable) are made **the write path's own properties**:
    the chain is the ordinal derived from the file at the moment of minting, the
    channel is a closed-vocabulary member on the record, and durability is
    Ruling 78's funnel. So the attestation is not a judgment this module makes
    about content - it is what its own write path structurally guarantees.
  * `method_warrant` - NONE for both current channels, recorded HONESTLY rather
    than omitted, with `warrant_conditions` empty. **NONE ADMITS WITH WARRANT
    NEAR ZERO; IT DOES NOT EXCLUDE.** Neither door has a survival history, and
    manufacturing one because a field exists to hold it is L3's fabrication
    class - the exact defect Ruling 58 spent a ruling closing one layer out.
  * `content_standing` - PROVISIONAL_UNVALIDATED, typed.

**NOTHING IN M4 CONSUMES OR PROMOTES THESE, AND THAT IS PINNED.** Standing moves
only under L12 episodes. The fields exist so the FIRST record carries them
(Phase 2's law: provenance is first-class from each store's first record, and it
CANNOT be retrofitted - a field added later is `None` for everything that came
before, forever).

Each is a closed vocabulary carrying **exactly the member the grounding names as
producible, and no other**. A second member would be a state this build can
neither produce nor recognise - coined at the one surface whose honesty the
whole boundary rests on. Widening is a governance act with a record behind it
(Ruling 7's closed-enum discipline; M3-A's "vocabularies are governed content").

VOCABULARY COLLISION CENSUS (Ruling 30's discipline, run BEFORE coining)
-------------------------------------------------------------------------------
57 enum classes / 247 distinct member names in `src/`. **ZERO class collisions**
on all four names below. ONE member name already exists elsewhere, and it is
recorded here so that nobody later derives one sense from the other - which is
precisely the defect Ruling 30 spent an entire ruling untangling for "scope":

  * `STRUCTURAL` - `tcaml.LockClass.STRUCTURAL` (an ACTION's class: does it
    CHANGE the system, and therefore must it hold the GLOBAL lock).
    `AcquisitionIntegrity.STRUCTURAL` is a different question in a different
    domain: WHAT KIND OF ATTESTATION this record carries, answered by the write
    path's own properties. **NOTHING CONVERTS BETWEEN THEM**, no code reads one
    as the other, and neither is derived from the other. Ruling 30's whole
    finding was that two senses of one word inside one call chain cost a ruling
    to untangle; these two are never in one call chain at all.

WHY `src/external/` (the location choice, stated - it is never authority)
-------------------------------------------------------------------------------
The domain row is Kernel either way. This file sits with the neighbours it
READS and is read BY: `claim_ancestry` (the CLM it joins to), `model_provider`
(one of its two doors), `source_genealogy`. Its other door is `aurea_core`,
which reaches every package. `src/filtration/` holds the collapse machinery this
store deliberately knows nothing about.

WHAT IS DELIBERATELY NOT HERE
-------------------------------------------------------------------------------
  * **NO READER IN COGNITION.** The ledger is WRITTEN at both doors and read by
    nothing that decides anything - pinned as the current fact in Ruling 72's
    form, narrowing the day a reader gets its own ruling.
  * **NO DELETE, REMOVE, CLEAR, PURGE, TRUNCATE OR UPDATE FAMILY** - AST-pinned,
    because a method named `amend` with a docstring saying "only before
    resolution" is a request for restraint, and this project has hard evidence
    restraint fails (CLAUDE.md section 3).
  * **NO STANDING PROMOTION.** This module holds no threshold, no score, no
    weight and no comparison of any of the triple's fields.
  * Tool-result acquisition is Phase 11's and has no door yet; the channel
    vocabulary is closed at two BECAUSE the census found exactly two doors, and
    a third member would assert a boundary that does not exist.

COINS: the four vocabularies above (one producible member each but for the
channel's two, every one named by the grounding), the `ACQ-` prefix, the record's
field names, and `AcquisitionLedgerUnreadable`. No threshold, no magnitude, no
score.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "AcquisitionChannel",
    "AcquisitionIntegrity",
    "MethodWarrant",
    "ContentStanding",
    "AcquisitionRecord",
    "AcquisitionLedger",
    "AcquisitionLedgerUnreadable",
]


# =====================================================================
# THE VOCABULARY - v1, GOVERNED CONTENT, closed
# =====================================================================

class AcquisitionChannel(str, Enum):
    """WHICH DOOR an arrival came through. CLOSED at the census's two doors.

    A fact about the MECHANISM that received the arrival, and deliberately NOT
    derived from `OriginKind`. The two answer different questions - `origin_kind`
    is about WHO ASSERTED, this is about WHICH DOOR - and a human pasting a
    model's output through `process_input` is honestly USER_INPUT arrival of a
    MODEL_PREDICTION assertion. **Deriving either from the other would be
    Ruling 30's defect exactly: two senses collapsed into one value.**

    A THIRD MEMBER IS A MANIFEST ACT. Tool results (Phase 11) have no door yet,
    and a member for a boundary that does not exist would assert a channel
    nothing can arrive through.
    """

    USER_INPUT = "user_input"
    MODEL_EXCHANGE = "model_exchange"


class AcquisitionIntegrity(str, Enum):
    """WHAT KIND of integrity attestation the record carries. Section 4, v1.

    STRUCTURAL is the write path's own three properties - chain intact (the
    ordinal derived from the file at the moment of minting), channel identified
    (a closed-vocabulary member on the record), record durable (Ruling 78's
    funnel). It attests nothing whatever about the CONTENT.

    See the module docstring's collision census: `tcaml.LockClass.STRUCTURAL` is
    a different word in a different domain and nothing converts between them.
    """

    STRUCTURAL = "structural"


class MethodWarrant(str, Enum):
    """The acquisition METHOD's survival history. Section 4, v1.

    NONE for both current channels, and recording it is the point: **NONE ADMITS
    WITH WARRANT NEAR ZERO; IT DOES NOT EXCLUDE.** Neither door has ever had a
    method survive anything, so any other value would be invented.
    """

    NONE = "none"


class ContentStanding(str, Enum):
    """What standing the CONTENT has at the boundary. Section 4, v1.

    Everything that arrives is PROVISIONAL_UNVALIDATED. Standing moves only
    under L12 episodes, and **nothing in M4 promotes it** - this field is written
    and never read, so that the first record carries it rather than being
    retrofitted later (Phase 2).
    """

    PROVISIONAL_UNVALIDATED = "provisional_unvalidated"


def payload_digest(payload: str) -> str:
    """The payload hash - sha256 of its UTF-8 bytes, hex.

    **BESIDE the payload, never instead of it.** Phase 4 says permanently
    RECORDED, and an acquisition ledger that stored digests could not replay
    anything; the hash is here for cheap comparison, which is what M4-gamma's
    census does with it.
    """
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AcquisitionRecord:
    """ONE external arrival, as recorded at the boundary. Frozen.

    There is no mutable interior to freeze deeply (Ruling 52's concern):
    `payload` is `str` by the write path's own type gate and the rest are
    scalars and a tuple of `str`. The type checks in `__post_init__` are what
    KEEP it that way, rather than a comment asking callers not to.
    """

    acquisition_id: str
    channel: AcquisitionChannel
    correlation_id: str
    payload: str
    payload_sha256: str
    integrity: AcquisitionIntegrity = AcquisitionIntegrity.STRUCTURAL
    method_warrant: MethodWarrant = MethodWarrant.NONE
    # Section 4's documented-conditions refs. EMPTY for both v1 channels, and
    # empty HONESTLY: a warrant of NONE has no conditions to cite.
    warrant_conditions: Tuple[str, ...] = ()
    content_standing: ContentStanding = ContentStanding.PROVISIONAL_UNVALIDATED
    # RECORDED AS OBSERVATION, NEVER READ BY LOGIC (M3-A's rule). AST-pinned.
    recorded_wall: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.payload, str):
            raise TypeError(
                f"AcquisitionRecord.payload must be str, got "
                f"{type(self.payload).__name__}. The payload is recorded WHOLE, "
                f"and a value this ledger cannot canonically hold is refused "
                f"rather than stringified into a permanent record (Ruling 66).")
        for name, enum_type in (("channel", AcquisitionChannel),
                                ("integrity", AcquisitionIntegrity),
                                ("method_warrant", MethodWarrant),
                                ("content_standing", ContentStanding)):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(
                    f"AcquisitionRecord.{name} must be a {enum_type.__name__}. "
                    f"A raw string would let a caller invent a member the enum "
                    f"deliberately closes.")
        if (not isinstance(self.warrant_conditions, tuple)
                or not all(isinstance(c, str) for c in self.warrant_conditions)):
            raise TypeError(
                "AcquisitionRecord.warrant_conditions must be a tuple of str - "
                "a list would be a mutable interior on a frozen record "
                "(Ruling 52).")

    @property
    def arrival_index(self) -> Optional[int]:
        """This arrival's position in the boundary's logical time.

        **DERIVED FROM THE ID, NEVER STORED** - the ordinal IS the arrival index
        (the grounding's own words), so a second field holding it would be a
        stored derivation free to disagree with the id it copies (L3; Rulings
        63/65). `None` for an id that does not parse, rather than 0, because an
        unparseable id is a record whose place in logical time is UNKNOWN and a
        0 would silently sort it first.
        """
        prefix = AcquisitionLedger.ID_PREFIX
        if not self.acquisition_id.startswith(prefix):
            return None
        tail = self.acquisition_id[len(prefix):]
        return int(tail) if tail.isdigit() else None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "acquisition_id": self.acquisition_id,
            "channel": self.channel.value,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "payload_sha256": self.payload_sha256,
            "integrity": self.integrity.value,
            "method_warrant": self.method_warrant.value,
            "warrant_conditions": list(self.warrant_conditions),
            "content_standing": self.content_standing.value,
            "recorded_wall": self.recorded_wall,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["AcquisitionRecord"]:
        """Rebuild from a ledger line, or `None` if the line is unreadable.

        THE CLOSED VOCABULARIES ARE ENFORCED ON THE WAY IN. A member this build
        does not know is NOT coerced and NOT defaulted - the line contributes
        nothing (floor semantics). A forensic log outlives the code that wrote
        it, and silently reading an unknown channel as a known one would put a
        fact in the reader's hands that the writer never recorded (Ruling 58's
        `from_dict`, verbatim reasoning).
        """
        try:
            return cls(
                acquisition_id=str(data["acquisition_id"]),
                channel=AcquisitionChannel(data["channel"]),
                correlation_id=str(data["correlation_id"]),
                payload=data["payload"],
                payload_sha256=str(data["payload_sha256"]),
                integrity=AcquisitionIntegrity(data["integrity"]),
                method_warrant=MethodWarrant(data["method_warrant"]),
                warrant_conditions=tuple(data.get("warrant_conditions") or ()),
                content_standing=ContentStanding(data["content_standing"]),
                recorded_wall=str(data.get("recorded_wall", "")),
            )
        except (KeyError, ValueError, TypeError):
            return None


# =====================================================================
# THE LEDGER
# =====================================================================

class AcquisitionLedgerUnreadable(Exception):
    """The ledger EXISTS and its mint cannot be derived, so the next `ACQ-`
    ordinal is UNKNOWN.

    RULING 53'S SENTINEL, WHOLE: this NEVER falls back to a number. Two arrivals
    wearing one id are two arrivals nobody can tell apart afterwards, in an
    append-only record where nothing can ever disambiguate them (3a:112) - and
    the ordinal is the boundary's CLOCK, so a reissued id is two moments of
    logical time wearing one name.

    A STRUCTURAL VIOLATION (Ruling 25's taxonomy), and here it additionally
    GATES PERCEPTION for the same reason the ancestry ledger's does: an arrival
    that cannot be recorded has lost its place at the boundary permanently.
    """


class AcquisitionLedger:
    """Append-only acquisition ledger. CAE's / O1's / O3's / Q1's / K2's shape.

    THE SHAPE IS COPIED ON PURPOSE (Ruling 72's reasoning, M3-A's verbatim):
    CAE is the append-only store this project has ruled on five times, and
    writing a second subtly-different one would be re-deciding settled questions
    by accident.
    """

    ID_PREFIX = "ACQ-"

    def __init__(self,
                 ledger_path: str = "data/runtime/logs/acquisitions.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the SAME commit as this store.
        self.ledger_path = Path(ledger_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: THERE IS NO `self._seq`. Every mint derives from the file.

    # -----------------------------------------------------------------
    # THE MINT
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `ACQ-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's helper: a RAW-TEXT scan with the anchored pattern, so an
        ordinal on a torn or unparseable line is still SEEN and never reissued.
        Ruling 53's sentinel is unchanged - `None` iff the file EXISTS and the
        read raised; a MISSING file is a legitimate `0`, because absence is a
        first run and not a fault.
        """
        return derive_max_ordinal(self.ledger_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next `ACQ-` id, or REFUSE. Caller holds the mint lock."""
        seq = self._derive_seq()
        if seq is None:
            raise AcquisitionLedgerUnreadable(
                f"the acquisition ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next {self.ID_PREFIX} ordinal is "
                f"UNKNOWN. Minting one anyway could write an id that already "
                f"names a different arrival - and that ordinal is the "
                f"boundary's clock, so it would be two moments of logical time "
                f"wearing one name.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def record(self, payload: str, *,
               channel: AcquisitionChannel,
               correlation_id: Optional[str] = None) -> AcquisitionRecord:
        """Record ONE external arrival. Mint an id, append one line, return it.

        RAISES on failure and the raise PROPAGATES - the write GATES the
        arrival, on Ruling 58's own reason rather than by analogy: **boundary
        facts cannot be reconstructed later.** An arrival taken up without its
        acquisition recorded has lost its place in the boundary's logical time
        permanently, and Phase 4's determinism claim is a claim about exactly
        that record existing.

        `correlation_id` defaults to THE RECORD'S OWN ID: a single arrival opens
        and closes its own exchange. A caller continuing an exchange passes the
        `ACQ-` id of the half that opened it.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim): a
        torn APPEND damages one line, which the floor semantics below already
        drop; a torn SNAPSHOT destroys the prior state. Routing an append-only
        log through `atomic_write` would rewrite the whole ledger per entry -
        converting the exempt failure class into the dangerous one in the name
        of fixing it.
        """
        if not isinstance(channel, AcquisitionChannel):
            raise TypeError(
                f"channel must be an AcquisitionChannel, got "
                f"{type(channel).__name__}. A raw string would let a caller "
                f"invent a door that does not exist.")
        # RULING 69 res.3 - IN-PROCESS MINT-APPEND ATOMICITY. Keyed by the
        # RESOLVED PATH and held across DERIVE -> MINT -> APPEND as one unit.
        with mint_lock(self.ledger_path):
            return self._mint_and_append(payload, channel, correlation_id)

    def _mint_and_append(self, payload: str, channel: AcquisitionChannel,
                         correlation_id: Optional[str]) -> AcquisitionRecord:
        """The locked critical section: derive, mint, validate, append.

        Split out so the lock scope is a whole method rather than an indented
        region - the boundary is then visible in the diff of any future change,
        which is what stops an append drifting out of it (Ruling 69's form).
        """
        acquisition_id = self._next_id()
        record = AcquisitionRecord(
            acquisition_id=acquisition_id,
            channel=channel,
            # THE EXCHANGE'S FIRST ARRIVAL, or itself. Nothing is minted.
            correlation_id=(correlation_id if correlation_id is not None
                            else acquisition_id),
            payload=payload,
            payload_sha256=payload_digest(payload),
            recorded_wall=datetime.now().isoformat(),
        )
        entry = record.as_dict()

        # RULING 66's WRITER GATE, BEFORE `mkdir` and BEFORE the append: a
        # refused entry leaves no file, no line and no directory it did not
        # already need. `allow_nan=False` below is the second half, and
        # `default=` is absent entirely - a non-canonical leaf REFUSES rather
        # than being silently stringified into a permanent record.
        validate_record_value(entry, path="acquisition_entry")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        # RULING 78 res.2: durable at its own write, through the funnel.
        durable_append_text(self.ledger_path,
                            json.dumps(entry, allow_nan=False) + "\n")
        self.entries.append(entry)
        return record

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> List[AcquisitionRecord]:
        """Every readable record, IN APPEND ORDER. The arrivals, as recorded.

        Reads the FILE rather than `self.entries`: the ledger spans processes
        and the in-memory mirror does not. **ERA HONESTY** - a line is returned
        as it was written, and a line that will not parse, or that carries a
        vocabulary member outside a closed enum, contributes NOTHING and is
        never coerced (floor semantics).
        """
        if not self.ledger_path.exists():
            return []
        out: List[AcquisitionRecord] = []
        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                record = AcquisitionRecord.from_dict(data)
                if record is not None:
                    out.append(record)
        return out

    def get(self, acquisition_id: str) -> Optional[AcquisitionRecord]:
        for record in self.read_all():
            if record.acquisition_id == acquisition_id:
                return record
        return None

    def correlated(self, correlation_id: str) -> Tuple[AcquisitionRecord, ...]:
        """Every arrival sharing one correlation, in append order.

        The halves of one exchange. An id join and EXACT string equality only -
        Ruling 76's retrieval law binds here as it does in `record_joins`: no
        similarity, no ranking, no content matching, ever.
        """
        return tuple(r for r in self.read_all()
                     if r.correlation_id == correlation_id)


# NOT REGISTERED IN `STORE_OWNERS`, and CAE's reason applies verbatim (the
# ancestry, prediction, goal, examination and activation ledgers all carry it):
# the Ruling-1 scanner keys on an ATTRIBUTE NAME, and this store is a FILE with
# no in-memory collection to scan - `entries` is a per-process mirror nothing
# reads back into a decision. Registering it would flag nothing and claim
# coverage that does not exist, which is the completeness-claim defect. What
# guards it instead is that `record()` is the only write path.
