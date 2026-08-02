"""
claim_ancestry.py - RULING 58 / DOCKET O item O1: THE CLAIM-ANCESTRY RECORD.

    A claim's origin is recorded at ingress, ONCE, as fact.
    A claim whose origin cannot be recorded is not perceived.

Canon: the SPL Adapter (1:574-658) - "human input, external AI, system plugin,
LLM wrappers"; Tool Identity Sovereignty ("no external source is treated as
internal"); AVT.017 (origin trace required). The SIF spec (6b:919-1058) names
the pipeline this layer eventually serves.

WHAT THIS FIXES, AND IT IS NOT A MISSING FEATURE - IT IS A FABRICATION
-----------------------------------------------------------------------
The origin fact ALREADY EXISTED IN CODE AND WAS INVENTED. `process_input` took
`source: str = "user"` and handed that free-text default to SPL, which wrote it
into `Echo.source` - A DURABLE STORE FIELD - and `aurea_core` stamped it onto
the echo's topology node as `source:{source}`. So every claim the suite, the
soak, or any bare caller has ever processed is on record as having originated
from a human user, including the ones that did not.

That is L3's defect class - a fact stored because a field existed to hold it,
rather than because anything observed it - live at HEAD, in a store. The remedy
is not a better default. It is a vocabulary in which "nobody said" is sayable:
`UNDECLARED`, and five fields that can be ABSENT.

THE THREE STATES ARE DOCKET H'S CUT, AT THE INGRESS
-----------------------------------------------------
    PROVIDED(value)  the channel supplied it
    DECLARED_NONE    the channel said "there are none"
    ABSENT           the channel said NOTHING about it

A channel that supplied nothing and a channel that declared "none exist" are
DIFFERENT FACTS and persist differently. Flattening them is the
abstention-becomes-honest-zero defect - Docket H's founding distinction between
its two zeroes - one layer earlier: at the boundary where the claim arrives.

(The Docket H module is deliberately not named by filename here. Its consumer
pin scans source TEXT for that token, so a prose mention registers this module
as a consumer of the evidence vocabulary, which it is not - it imports nothing
from it and reads no countability state. SECOND OCCURRENCE of this
false-positive; the first was worked around the same way in Batch 51. Reported
to the architect rather than fixed here: the scan's instrument, not the prose,
is what wants changing.)

WHAT IS DELIBERATELY NOT HERE, each with its owner
----------------------------------------------------
  * SIF FILTRATION and its empirical-mode TAG TABLE (observational /
    theoretical / statistical / meta-claim / narrative-wrapped /
    authority-dependent). That table classifies claim FORM, requires content
    judgment, and is SIF's own instrument when SIF is built. It is not in O1's
    registered field list and it stays OUT.
  * ~~SOURCE GENEALOGY - O2. It will need an echo <-> claim_id linkage, and
    that SCHEMA DECISION IS O2'S. It is flagged here and deliberately not
    made.~~ SUPERSEDED 2026-08-01 BY RULING 60, kept as the record of what was
    true when written. THE DECISION WAS MADE, and THIS RECORD'S OWN STRUCTURE
    FORCED IT: the ancestry record is deep-frozen and minted BEFORE the echo
    exists (after the suspension gate, before the SPL wrap), so it cannot carry
    an echo id without mutating a frozen record or deferring the gate - both
    barred by Ruling 58 itself. So the LATER artifact references the EARLIER:
    `Echo.claim_id`, a join key and not an origin fact. The ledger still stores
    origin ONCE (L3 clean). Source genealogy itself lives in
    `src/external/source_genealogy.py` and reads these records without
    validating anything against this ledger.
  * OUTCOME ROUTING - O4.
  * TRUST SCORES - REFUSED, standing.
  * ANY STORED EPISTEMIC STANDING. The record holds origin FACTS ONLY - no
    tier, no admissibility, no reliability. L3's second half, and it is
    AST-pinned in `EntrenchmentBasis`'s shape: no such attribute is ever
    ASSIGNED on this record anywhere in `src/`. A stored standing would be a
    second writer of what the evidence already determines, and the field is the
    one people read while the facts are the one that is true.

COINS NOTHING: the id format is the house convention (Nova's / CAE's), every
enum member is recovered from canon or the docket's own registration, the
three-state vocabulary is Docket H's, and no threshold, weight or magnitude
exists anywhere in this path.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =====================================================================
# THE VOCABULARY
# =====================================================================

class OriginKind(str, Enum):
    """WHERE a claim came from. CLOSED, and EVERY MEMBER IS RECOVERED.

    The first four are the SPL Adapter's own source classes (1:574-658),
    verbatim. `MODEL_PREDICTION` is O6's registered member, included NOW so that
    O6 never has to reopen a closed enum. `UNDECLARED` is the Docket H cut
    applied to the origin fact itself.

    ADDITIONS REQUIRE A MANIFEST RULING. This is the `behavior_type` discipline
    (Ruling 7: the closed enum stays closed) applied at the docket's own
    registration - a member added to make a caller convenient is a source class
    invented rather than observed.

    A `str` Enum by the shape rule: ONE vocabulary, serialized into the ledger,
    with no collision partner anywhere in the tree.
    """

    HUMAN = "human"                      # SPL Adapter: "human input"
    EXTERNAL_AI = "external_ai"          # SPL Adapter: "external AI"
    SYSTEM_PLUGIN = "system_plugin"      # SPL Adapter: "system plugin"
    LLM_WRAPPER = "llm_wrapper"          # SPL Adapter: "LLM wrappers"
    MODEL_PREDICTION = "model_prediction"   # O6's registered member
    # THE INGRESS CHANNEL CARRIED NO DECLARATION. Not a default, not a guess,
    # and specifically NOT "human" - recording anything else here would
    # fabricate the exact fact this module exists to stop fabricating.
    UNDECLARED = "undeclared"


class FieldState(str, Enum):
    """Docket H's two-absences cut, as a persisted vocabulary."""

    PROVIDED = "provided"            # the channel supplied a value
    DECLARED_NONE = "declared_none"  # the channel said there are none
    ABSENT = "absent"                # the channel said nothing at all


@dataclass(frozen=True)
class AncestryField:
    """One of O1's five fields, carrying WHICH KIND OF ANSWER it holds.

    `value` is meaningful ONLY when `state is PROVIDED`. The two other states
    carry no value by construction, which is what keeps "none exist" from
    degrading into an empty list that reads like a value.
    """

    state: FieldState
    value: Any = None

    def __post_init__(self) -> None:
        if self.state is not FieldState.PROVIDED and self.value is not None:
            raise ValueError(
                f"an ancestry field in state {self.state.value} carries no "
                f"value, got {self.value!r}. DECLARED_NONE and ABSENT are "
                f"statements ABOUT the answer, not answers.")

    def as_dict(self) -> Dict[str, Any]:
        return {"state": self.state.value, "value": _thaw(self.value)}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AncestryField":
        if not data:
            return absent()
        state = FieldState(data["state"])
        return cls(state=state,
                   value=data.get("value") if state is FieldState.PROVIDED else None)


def provided(value: Any) -> AncestryField:
    return AncestryField(state=FieldState.PROVIDED, value=value)


def declared_none() -> AncestryField:
    return AncestryField(state=FieldState.DECLARED_NONE)


def absent() -> AncestryField:
    return AncestryField(state=FieldState.ABSENT)


# O1's five registered fields, canonically named ONCE so no second spelling can
# drift from this one (Ruling 47's `CMTE_FAILURE_LABELS` shape).
ANCESTRY_FIELDS: Tuple[str, ...] = (
    "asserted_by",
    "basis",
    "replication_refs",
    "connecting_assumptions",
    "defeaters",
)


@dataclass(frozen=True)
class OriginDeclaration:
    """WHAT A CHANNEL SAYS about a claim it is handing in. The ingress input.

    Every field defaults to ABSENT, which is the honest reading of a channel
    that did not mention it. THERE IS NO DEFAULT `kind` OTHER THAN UNDECLARED:
    a channel that declares nothing gets `UNDECLARED`, not `HUMAN`.
    """

    kind: OriginKind = OriginKind.UNDECLARED
    asserted_by: AncestryField = field(default_factory=absent)
    basis: AncestryField = field(default_factory=absent)
    replication_refs: AncestryField = field(default_factory=absent)
    connecting_assumptions: AncestryField = field(default_factory=absent)
    defeaters: AncestryField = field(default_factory=absent)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, OriginKind):
            raise TypeError(
                f"OriginDeclaration.kind must be an OriginKind, got "
                f"{type(self.kind).__name__}. A raw string would let a caller "
                f"invent a source class the enum deliberately closes.")
        for name in ANCESTRY_FIELDS:
            if not isinstance(getattr(self, name), AncestryField):
                raise TypeError(
                    f"OriginDeclaration.{name} must be an AncestryField - use "
                    f"provided(...) / declared_none() / absent(). A bare value "
                    f"cannot say WHICH of the three answers it is.")


# =====================================================================
# THE RECORD
# =====================================================================

# RULING 52's freeze/thaw pair. HOISTED TO `src/utils/deep_freeze.py` BY
# RULING 63 (2026-08-01) - one behaviour, one definition. The two copies
# that lived here and in the sibling module were verified BYTE-IDENTICAL by
# AST (docstrings stripped) before the hoist, so nothing was reconciled or
# chosen between. The LOCAL NAMES ARE PRESERVED so every call site and every
# AST pin naming `_deep_freeze` is unchanged.
from src.utils.deep_freeze import deep_freeze as _deep_freeze  # noqa: E402
from src.utils.deep_freeze import thaw as _thaw  # noqa: E402


@dataclass(frozen=True)
class ClaimAncestryRecord:
    """The origin of ONE claim, as recorded at ingress. AN ARGUMENT OF RECORD.

    DEEP-FROZEN AT CONSTRUCTION (Ruling 52). `frozen=True` alone would freeze
    the shell and leave a `PROVIDED` field's value - which may be a dict or a
    list a channel handed in - writable through a retained reference. This
    record is consulted precisely when the question is what was true at ingress,
    so a value editable afterwards is not a record of ingress.
    """

    claim_id: str
    origin_kind: OriginKind
    asserted_by: AncestryField = field(default_factory=absent)
    basis: AncestryField = field(default_factory=absent)
    replication_refs: AncestryField = field(default_factory=absent)
    connecting_assumptions: AncestryField = field(default_factory=absent)
    defeaters: AncestryField = field(default_factory=absent)
    recorded_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.origin_kind, OriginKind):
            raise TypeError(
                f"ClaimAncestryRecord.origin_kind must be an OriginKind, got "
                f"{type(self.origin_kind).__name__}.")
        for name in ANCESTRY_FIELDS:
            item = getattr(self, name)
            if not isinstance(item, AncestryField):
                raise TypeError(
                    f"ClaimAncestryRecord.{name} must be an AncestryField.")
            # Ruling 52: a fresh deep copy, then a recursive read-only rebuild.
            # The copy is what defeats a caller's retained reference.
            object.__setattr__(
                self, name,
                AncestryField(state=item.state,
                              value=_deep_freeze(copy.deepcopy(item.value))))

    @classmethod
    def from_declaration(cls, claim_id: str,
                         declaration: Optional[OriginDeclaration]
                         ) -> "ClaimAncestryRecord":
        """Build the record. `None` means the channel declared NOTHING.

        THE NEW SURFACE FABRICATES NOTHING: no declaration produces
        `UNDECLARED` plus five ABSENT fields, which is the truthful record of a
        caller that said nothing - and is what every existing call site does.
        """
        declaration = declaration or OriginDeclaration()
        return cls(
            claim_id=claim_id,
            origin_kind=declaration.kind,
            recorded_at=datetime.now().isoformat(),
            **{name: getattr(declaration, name) for name in ANCESTRY_FIELDS},
        )

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "claim_id": self.claim_id,
            "origin_kind": self.origin_kind.value,
            "recorded_at": self.recorded_at,
        }
        for name in ANCESTRY_FIELDS:
            payload[name] = getattr(self, name).as_dict()
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["ClaimAncestryRecord"]:
        """Rebuild from a ledger line, or `None` if the line is unreadable.

        THE CLOSED ENUM IS ENFORCED ON THE WAY IN. An `origin_kind` this build
        does not know is NOT coerced to a member and NOT defaulted to
        `UNDECLARED` - the line is dropped by the caller's floor semantics. A
        forensic log outlives the code that wrote it, and silently reading an
        unknown source class as a known one is worse than not reading it: it
        would put a fact in the reader's hands that the writer never recorded.
        """
        try:
            kind = OriginKind(data["origin_kind"])
        except (KeyError, ValueError, TypeError):
            return None
        try:
            return cls(
                claim_id=str(data["claim_id"]),
                origin_kind=kind,
                recorded_at=str(data.get("recorded_at", "")),
                **{name: AncestryField.from_dict(data.get(name))
                   for name in ANCESTRY_FIELDS},
            )
        except (KeyError, ValueError, TypeError):
            return None


# =====================================================================
# THE LEDGER
# =====================================================================

class AncestryLedgerUnreadable(Exception):
    """RULING 58 / RULING 53's sentinel: the ledger EXISTS and its mint cannot
    be derived.

    Raised at the moment an id would be minted, after ONE re-derivation attempt.
    Minting from an unknown floor would write a `CLM-` id that may already name
    a different claim, and an append-only ledger cannot later disambiguate two
    records wearing one id.

    A STRUCTURAL VIOLATION (Ruling 25's taxonomy). It propagates rather than
    fermenting - and here it also GATES PERCEPTION: a claim whose origin cannot
    be recorded is not perceived.
    """


class ClaimAncestryLedger:
    """Append-only claim-ancestry ledger. CAE's shape, deliberately verbatim.

    THE SHAPE IS COPIED ON PURPOSE, not from convenience: CAE is the audit
    ledger this project has already ruled on four times (31, 42 res.4, 45, 53),
    and every one of those rulings applies here for the same reasons. Writing a
    second, subtly different durable append-only store would be re-deciding
    settled questions by accident.
    """

    ID_PREFIX = "CLM-"

    def __init__(self, ledger_path: str = "data/runtime/logs/claim_ancestry.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - redirected in both in the same commit.
        self.ledger_path = Path(ledger_path)
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        self._seq = self._derive_seq()

    # -----------------------------------------------------------------
    # THE MINT - continuity state (Ruling 42 res.4), sentinel per Ruling 53
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `CLM-` ordinal already in the ledger, or `None`.

        RULING 53 WHOLE: `None` IFF the ledger EXISTS and the read raised. A
        MISSING ledger is a legitimate `0`, because absence is a first run and
        not a fault - and answering an unreadable file with `0` is a claim about
        content the code never saw.

        PER-LINE FLOOR SEMANTICS for anything that will not parse: a forensic
        log outlives the code that wrote it, and a build that refuses to start
        because it met a line it does not understand has turned an append-only
        record into a liability. An unreadable FILE and an unparseable LINE are
        different failures and get different answers.
        """
        if not self.ledger_path.exists():
            return 0
        highest = 0
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry_id = json.loads(line).get("claim_id", "")
                    except ValueError:
                        continue
                    if isinstance(entry_id, str) and entry_id.startswith(self.ID_PREFIX):
                        tail = entry_id[len(self.ID_PREFIX):]
                        if tail.isdigit():
                            highest = max(highest, int(tail))
        except OSError:
            return None
        return highest

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Ruling 53's shape exactly."""
        if self._seq is None:
            self._seq = self._derive_seq()
        if self._seq is None:
            raise AncestryLedgerUnreadable(
                f"the claim-ancestry ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next CLM ordinal is UNKNOWN. Minting "
                f"one anyway could write an id that already names a different "
                f"claim, and an append-only ledger cannot later tell the two "
                f"apart. A claim whose origin cannot be recorded is not "
                f"perceived.")
        self._seq += 1
        # `{n:04d}` matches the house convention and GROWS NATURALLY past 9999 -
        # `CLM-10000` is what the format produces, not an overflow.
        return f"{self.ID_PREFIX}{self._seq:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE PATH
    # -----------------------------------------------------------------

    def record(self, declaration: Optional[OriginDeclaration] = None
               ) -> ClaimAncestryRecord:
        """Mint an id, append ONE line, return the record. RAISES on failure.

        THE WRITE GATES PERCEPTION, and that is the ruling's fourth resolution.
        CAE's precedent is the auditor gating the change, and `dee.py` states it
        in terms: "if logging is impossible, the override does not happen." Here
        the reason is L3's own - ORIGIN FACTS CANNOT BE RECONSTRUCTED LATER. A
        claim perceived without its origin recorded has lost that origin
        PERMANENTLY, so the record is the legitimacy and not a receipt.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim): a
        torn APPEND damages one line, which the floor semantics above already
        drop; a torn SNAPSHOT destroys the prior state. Routing an append-only
        log through `atomic_write` would rewrite the whole ledger per entry -
        converting the exempt failure class into the dangerous one in the name
        of fixing it.
        """
        record = ClaimAncestryRecord.from_declaration(self._next_id(), declaration)
        entry = record.as_dict()

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")
        self.entries.append(entry)
        return record

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> List[ClaimAncestryRecord]:
        """Every readable record, in append order. A forensic read.

        Reads the FILE rather than `self.entries`: the ledger spans processes
        and the in-memory mirror does not. A line that will not parse, or that
        carries an `origin_kind` outside the closed enum, contributes NOTHING -
        it is never coerced into a member.
        """
        if not self.ledger_path.exists():
            return []
        out: List[ClaimAncestryRecord] = []
        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                record = ClaimAncestryRecord.from_dict(data)
                if record is not None:
                    out.append(record)
        return out

    def get(self, claim_id: str) -> Optional[ClaimAncestryRecord]:
        for record in self.read_all():
            if record.claim_id == claim_id:
                return record
        return None


# NOT REGISTERED IN `STORE_OWNERS`, and CAE's reason applies verbatim: the
# Ruling-1 scanner keys on an ATTRIBUTE NAME, and this store is a FILE with no
# in-memory collection to scan - `entries` is a per-process mirror nothing reads
# back into a decision. Registering it would flag nothing and claim coverage
# that does not exist, which is the completeness-claim defect. What guards it
# instead is that `record()` is the only write path.
