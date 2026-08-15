"""
proposition_ledger.py - M6-α. THE WORLD MODEL's FIRST MEMBER.

    **A PROPOSITION CITING EVIDENCE THAT DOES NOT EXIST IS MANUFACTURING TRUTH
    AT ONE REMOVE.**

Grounds heading Phase 6 and the World Model domain paragraph: "a persistent
typed representation of what she thinks is happening outside herself... World
propositions never manufacture truth: they reference kernel epistemic records
and derive standing from the kernel."

WHAT THIS IS NOT, AND THE HISTORY THAT BINDS IT TWICE
-------------------------------------------------------------------------------
`record_projection.py` was named `world_state.py` for exactly one commit, and
Rulings 63/64 ruled this territory before it was built:

  * **(R63/64, NAME HONESTY)** that module projects RECORDS ABOUT CLAIMS AND
    PREDICTIONS and structurally cannot carry propositions - so a module named
    for what it cannot represent is false documentation in the strongest
    position a name can occupy. This file is named for what it holds:
    PROPOSITIONS, each carrying `asserted_content` - *what the proposition
    CLAIMS*, never *what is known*.
  * **(R64, THE REVERSED MEANING)** an unlabeled content slot let a FALSIFIED
    prediction's refuted expectation read as standing knowledge, with a tier
    vouching for it. That defect is made UNBUILDABLE here rather than reviewed
    for: **no public read door returns content without the derived standing
    beside it** (see `PropositionView`), and the door the contradiction surface
    reads carries NO CONTENT AT ALL.

THE REFERENCE DISCIPLINE IS A WRITE LAW
-------------------------------------------------------------------------------
`supported_by` / `contradicted_by` / `predicted_by` are kernel record
references RESOLVED AT WRITE against the real read surfaces. An id that does not
resolve is REFUSED TYPED, because the domain's own paragraph forbids
manufacturing truth and a citation to a record that does not exist is exactly
that, one level of indirection away. Id-equality joins only (Ruling 76): no
similarity, no ranking, no content matching, ever.

**REFERENCES ARE TYPED PAIRS, NOT BARE IDS, AND THE CENSUS IS WHY.** Scars are
`Δ17` / `Scar-0`, doctrines are `Doctrine-0` / `AVT.001` - there is no prefix
grammar that separates them, so a bare id would have to be resolved by TRYING
every store until one hit. That is guessing, and an id living in two stores
would resolve ambiguously. The caller names the store; the ledger checks it.

TWO REFUSALS, BECAUSE THERE ARE TWO CAUSES (Ruling 29's law)
-------------------------------------------------------------------------------
  * `UnresolvedReference` - the ledger LOOKED and the record is not there.
  * `UnverifiableReference` - no resolver for that kind was supplied, so the
    ledger COULD NOT LOOK.

One type covering both would be Ruling 25's defect one level down. The second
exists because a write law that can be skipped by simply not injecting a
resolver is the "discouraged, not unexecutable" shape (CLAUDE.md section 3):
**a ledger that cannot see a kind may not admit a reference to one.** It never
asserts non-existence it did not test, and it never admits a resolution it did
not perform - M3-A's `UNCHECKED` reasoning, resolved at the door instead of
recorded on the record, because here the reference is the thing being admitted.

UNGROUNDED IS A REAL STATE, ADMITTED AND RECORDED
-------------------------------------------------------------------------------
A proposition with ZERO references admits, and its standing derives to nothing
with the reason named. Refusing it would push callers to fabricate references
to get a write through - L3's fabrication class arriving at the write door, and
the ABSENT-is-a-real-answer law (Rulings 58/70) applied one domain over.

SUPERSESSION, NEVER MUTATION - AND THE CURRENT WORLD IS A DERIVATION
-------------------------------------------------------------------------------
A proposition updates by a SUCCESSOR carrying `supersedes`, resolved at write
against this ledger's own records. **The live set is computed by folding the
stream, never stored** - L3, and Rulings 63/65's refusal of a stored derivation,
at the field where a "current world snapshot" would be most tempting and most
wrong: a stored snapshot is a stale authority waiting for a trusting reader.

STANDING IS NOT STORED AND THIS MODULE DOES NOT OWN IT
-------------------------------------------------------------------------------
No standing value is ever written here. What is stored is REFERENCES; what is
read is STANDING; the gap between them is where the honesty lives, because a
reference whose record has MOVED since the proposition was written derives at
its CURRENT state - which is the entire point of deriving (M6-β).

`PropositionView.standing` is deliberately untyped by this module: the
derivation owns that vocabulary, and this ledger's only law is that the two
travel together.

VOCABULARY COLLISION CENSUS (Ruling 30's discipline, run BEFORE coining)
-------------------------------------------------------------------------------
61 enum classes / 251 distinct member names in `src/`. **ZERO class collisions.**
Four member names exist elsewhere and are recorded so nobody later derives one
sense from another:

  * `UNKNOWN` - `source_genealogy.GenealogyVerdict.UNKNOWN` (Ruling 60: the
    record cannot certify the world). `PropositionKind.UNKNOWN` is a KIND OF
    PROPOSITION from the heading's own list. Different question, different
    domain, nothing converts.
  * `CLAIM` / `SCAR` / `DOCTRINE` - `obligation_ledger.TargetKind` (what an
    obligation is owed ABOUT), `tca_core.NodeType` (topology), `ril.IdentityThread`.
    `KernelRefKind` names WHICH KERNEL STORE an id lives in. **It is NOT derived
    from `TargetKind` and must not be**, for the reason M3-A gives about its own
    mirroring of `NodeType`: a vocabulary change in one would silently move what
    the other can express.

WRITERS, v1 - HONEST
-------------------------------------------------------------------------------
Every door is externally invoked and **NOTHING IN `src/` WRITES A PROPOSITION**,
pinned in Ruling 72's no-consumer form. The Executive wires proposition-writing
at M7; perception-side auto-extraction is ruled NOWHERE and this module does not
pretend otherwise.

COINS: `PropositionKind` (the heading's nine, recovered not invented),
`KernelRefKind`, the `WMP-` prefix, the record's field names, and the two
refusal types. No threshold, no magnitude, no score.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "PropositionKind",
    "KernelRefKind",
    "KernelRef",
    "PropositionRecord",
    "PropositionSummary",
    "PropositionView",
    "PropositionLedger",
    "PropositionLedgerUnreadable",
    "UnresolvedReference",
    "UnverifiableReference",
]


# =====================================================================
# THE VOCABULARY - v1, GOVERNED CONTENT, closed
# =====================================================================

class PropositionKind(str, Enum):
    """WHAT KIND of thing a proposition asserts. **THE HEADING'S OWN NINE**,
    verbatim and in its order - recovered, not invented.

    GOVERNED CONTENT: widened only by a manifest entry (Ruling 7's closed-enum
    discipline). A member added to make a caller convenient is a category of
    world-fact invented rather than observed.
    """

    ENTITY = "entity"
    EVENT = "event"
    STATE = "state"
    RELATION = "relation"
    CAUSAL_HYPOTHESIS = "causal_hypothesis"
    CONSTRAINT = "constraint"
    UNKNOWN = "unknown"
    CONTRADICTION = "contradiction"
    TEMPORAL_INTERVAL = "temporal_interval"


class KernelRefKind(str, Enum):
    """WHICH KERNEL STORE a referenced id lives in. Closed at six.

    NOT DERIVED FROM `TargetKind`, deliberately - see the census in the module
    docstring. These name the stores a proposition may cite; that one names what
    an obligation may be owed about, and the two moving together would be an
    accident rather than a decision.
    """

    CLAIM = "claim"              # CLM- : the claim-ancestry ledger
    SCAR = "scar"                # the scar store
    DOCTRINE = "doctrine"        # the Codex (live or fossil)
    EPISODE = "episode"          # EPI- : the episode record
    OBLIGATION = "obligation"    # OBL- : the obligation ledger
    PREDICTION = "prediction"    # PRD- : the prediction ledger


@dataclass(frozen=True)
class KernelRef:
    """One reference from a proposition into the kernel. A TYPED PAIR.

    The caller names the store; the ledger checks the id against it. Bare ids
    would have to be resolved by trying every store until one hit, which is
    guessing (see the module docstring).
    """

    kind: KernelRefKind
    record_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, KernelRefKind):
            raise TypeError(
                f"KernelRef.kind must be a KernelRefKind, got "
                f"{type(self.kind).__name__}. A raw string would let a caller "
                f"cite a store this ledger does not know how to check.")
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise TypeError(
                "KernelRef.record_id must be a non-empty str - an id join is "
                "EXACT string equality (Ruling 76), and an empty id joins "
                "nothing while looking like a citation.")

    def as_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind.value, "record_id": self.record_id}

    @classmethod
    def from_dict(cls, data: Any) -> Optional["KernelRef"]:
        if not isinstance(data, dict):
            return None
        try:
            return cls(kind=KernelRefKind(data["kind"]),
                       record_id=str(data["record_id"]))
        except (KeyError, ValueError, TypeError):
            return None


REFERENCE_FIELDS: Tuple[str, ...] = (
    "supported_by", "contradicted_by", "predicted_by")


class PropositionLedgerUnreadable(Exception):
    """The ledger EXISTS and its mint cannot be derived (Ruling 53's sentinel).

    NEVER falls back to a number: two propositions wearing one id are two
    world-claims nobody can tell apart afterwards, in an append-only record
    where nothing can ever disambiguate them (3a:112).
    """


class UnresolvedReference(Exception):
    """The ledger LOOKED for a referenced record and it is not there.

    The write law: a proposition citing evidence that does not exist is
    manufacturing truth at one remove.
    """


class UnverifiableReference(Exception):
    """No resolver for that kind was supplied, so the ledger COULD NOT LOOK.

    **A DIFFERENT CAUSE FROM `UnresolvedReference`, AND THEREFORE A DIFFERENT
    TYPE** (Ruling 29). This one blames nothing about the reference: it says the
    ledger was built unable to check that store, and admitting the reference
    anyway would claim a resolution it never performed while refusing it as
    UNRESOLVED would assert a non-existence it never tested (M3-A's `UNCHECKED`
    distinction, at the door rather than on the record).
    """


# =====================================================================
# THE RECORDS
# =====================================================================

@dataclass(frozen=True)
class PropositionRecord:
    """ONE proposition, as written. Frozen.

    `asserted_content` IS NAMED FOR WHAT IT IS: what this proposition CLAIMS,
    not what is known. R64's lesson made a field name.
    """

    wmp_id: str
    kind: PropositionKind
    asserted_content: str
    supported_by: Tuple[KernelRef, ...] = ()
    contradicted_by: Tuple[KernelRef, ...] = ()
    predicted_by: Tuple[KernelRef, ...] = ()
    supersedes: Optional[str] = None
    # EVENT-TIME references, recorded AS DECLARED and deliberately NOT resolved:
    # they may name any recorded ordinal space (`ACQ-`, `SEQ-`, ...), and
    # deciding which spaces bind here is a future ruling. **They are not wall
    # clock** - that is `recorded_wall`, below, which no logic reads.
    interval_start: Optional[str] = None
    interval_end: Optional[str] = None
    # RECORDED AS OBSERVATION, NEVER READ BY LOGIC (M3-A's rule). AST-pinned.
    recorded_wall: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.kind, PropositionKind):
            raise TypeError(
                f"PropositionRecord.kind must be a PropositionKind, got "
                f"{type(self.kind).__name__}.")
        if not isinstance(self.asserted_content, str):
            raise TypeError(
                f"PropositionRecord.asserted_content must be str, got "
                f"{type(self.asserted_content).__name__}.")
        for name in REFERENCE_FIELDS:
            value = getattr(self, name)
            if (not isinstance(value, tuple)
                    or not all(isinstance(r, KernelRef) for r in value)):
                raise TypeError(
                    f"PropositionRecord.{name} must be a tuple of KernelRef - "
                    f"a list would be a mutable interior on a frozen record "
                    f"(Ruling 52), and a bare id cannot say which store it "
                    f"lives in.")

    @property
    def references(self) -> Tuple[KernelRef, ...]:
        """Every kernel reference, across all three fields. A DERIVATION."""
        return tuple(ref for name in REFERENCE_FIELDS
                     for ref in getattr(self, name))

    @property
    def ungrounded(self) -> bool:
        """Zero references. A REAL STATE, admitted and recorded honestly."""
        return not self.references

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "wmp_id": self.wmp_id,
            "kind": self.kind.value,
            "asserted_content": self.asserted_content,
            "supersedes": self.supersedes,
            "interval_start": self.interval_start,
            "interval_end": self.interval_end,
            "recorded_wall": self.recorded_wall,
        }
        for name in REFERENCE_FIELDS:
            payload[name] = [ref.as_dict() for ref in getattr(self, name)]
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["PropositionRecord"]:
        """Rebuild from a ledger line, or `None` if unreadable.

        THE CLOSED VOCABULARIES ARE ENFORCED ON THE WAY IN. A kind this build
        does not know is NOT coerced and NOT defaulted - the line contributes
        nothing (floor semantics). A forensic log outlives the code that wrote
        it, and reading an unknown proposition kind as a known one would put a
        fact in the reader's hands the writer never recorded (Ruling 58's
        `from_dict`, verbatim reasoning).
        """
        try:
            refs = {}
            for name in REFERENCE_FIELDS:
                raw = data.get(name) or []
                rebuilt = [KernelRef.from_dict(item) for item in raw]
                if any(r is None for r in rebuilt):
                    return None
                refs[name] = tuple(rebuilt)
            return cls(
                wmp_id=str(data["wmp_id"]),
                kind=PropositionKind(data["kind"]),
                asserted_content=str(data["asserted_content"]),
                supersedes=data.get("supersedes"),
                interval_start=data.get("interval_start"),
                interval_end=data.get("interval_end"),
                recorded_wall=str(data.get("recorded_wall", "")),
                **refs,
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass(frozen=True)
class PropositionSummary:
    """A proposition's STRUCTURAL facts, **WITH NO CONTENT**.

    **THIS IS ENFORCEMENT BY SCOPE, NOT BY DISCIPLINE** (Ruling 33's move). The
    contradiction surface reads this shape, and because it carries no
    `asserted_content` the surface is STRUCTURALLY INCAPABLE of inferring a
    semantic contradiction from text. v1's record-honest floor is not a promise
    anyone must keep - it is the only thing the surface can see.
    """

    wmp_id: str
    kind: PropositionKind
    supported_by: Tuple[KernelRef, ...] = ()
    contradicted_by: Tuple[KernelRef, ...] = ()
    predicted_by: Tuple[KernelRef, ...] = ()
    supersedes: Optional[str] = None


@dataclass(frozen=True)
class PropositionView:
    """A proposition's CONTENT AND ITS STANDING, together. Frozen.

    **THE ONLY SHAPE A PUBLIC READ DOOR RETURNS `asserted_content` IN**, which
    is R64's law made schema: the reversed-meaning defect (refuted content read
    as standing knowledge) is unbuildable here rather than reviewed for.

    `standing` IS DELIBERATELY UNTYPED BY THIS MODULE. The derivation owns that
    vocabulary (M6-β); this ledger's law is only that the two travel together,
    and typing it here would make the ledger the author of a standing it must
    never store.
    """

    record: PropositionRecord
    standing: Any

    @property
    def wmp_id(self) -> str:
        return self.record.wmp_id

    @property
    def asserted_content(self) -> str:
        return self.record.asserted_content


# =====================================================================
# THE LEDGER
# =====================================================================

class PropositionLedger:
    """Append-only proposition ledger. The M3-A discipline, verbatim.

    THE SHAPE IS COPIED ON PURPOSE (Ruling 72's reasoning, seven consumers
    deep now): CAE is the append-only store this project has ruled on five
    times, and writing a second subtly-different one would be re-deciding
    settled questions by accident.
    """

    ID_PREFIX = "WMP-"

    def __init__(
        self,
        ledger_path: str = "data/runtime/worldmodel/propositions.jsonl",
        ancestry_ledger: Any = None,
        scar_core: Any = None,
        codex: Any = None,
        episode_record: Any = None,
        obligation_ledger: Any = None,
        prediction_ledger: Any = None,
    ):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the SAME commit as this store.
        self.ledger_path = Path(ledger_path)
        # READ-ONLY RESOLVER HANDLES. Every one was censused before wiring (see
        # the module docstring): all six read surfaces open mode "r" or fold in
        # memory, none mints, stamps or writes. `retrieve` is barred here for
        # the reason M3-A bars it - on the suspension systems it mutates the
        # entry and calls `save_to_file()`, so it is not a read.
        # **NAMED TO AVOID THE CANONICAL STORE NAMES, AND THE RULING-1
        # INVARIANT IS WHY.** The first draft called these `claims`, `scars`,
        # `episodes`, `obligations`, `predictions` - and `self.scars = scars`
        # tripped the single-writer scanner, which flags `<anything>.scars = ...`
        # outside `scar_logic_core.py`. It was RIGHT to: CLAUDE.md section 2
        # says do not name a local collection after a canonical store, and THE
        # FIX IS THE NAME, NOT THE TEST. These are M3-A's own handle names,
        # already proven safe by the obligation ledger.
        self.ancestry_ledger = ancestry_ledger
        self.scar_core = scar_core
        self.codex = codex
        self.episode_record = episode_record
        self.obligation_ledger = obligation_ledger
        self.prediction_ledger = prediction_ledger
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: THERE IS NO `self._seq`. Every mint derives from the file.

    # -----------------------------------------------------------------
    # THE MINT
    # -----------------------------------------------------------------

    def _next_id(self) -> str:
        """Mint the next `WMP-` id, or REFUSE. Caller holds the mint lock."""
        seq = derive_max_ordinal(self.ledger_path, self.ID_PREFIX)
        if seq is None:
            raise PropositionLedgerUnreadable(
                f"the proposition ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next {self.ID_PREFIX} ordinal is "
                f"UNKNOWN. Minting one anyway could write an id that already "
                f"names a different proposition - and propositions supersede "
                f"each other BY ID, so a collision would make the world's own "
                f"history unreadable.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE REFERENCE DISCIPLINE - RESOLVED AT WRITE
    # -----------------------------------------------------------------

    def _resolver_for(self, kind: KernelRefKind):
        return {
            KernelRefKind.CLAIM: self.ancestry_ledger,
            KernelRefKind.SCAR: self.scar_core,
            KernelRefKind.DOCTRINE: self.codex,
            KernelRefKind.EPISODE: self.episode_record,
            KernelRefKind.OBLIGATION: self.obligation_ledger,
            KernelRefKind.PREDICTION: self.prediction_ledger,
        }[kind]

    def _exists(self, ref: KernelRef) -> bool:
        """Does this kernel record exist? A READ, on each owner's own surface.

        Each call below was censused as READ-ONLY before being wired. Doctrines
        consult the FOSSIL MAP too, because a proposition may legitimately cite
        a doctrine that has fallen - M3-A's fossil-resolves rule, and refusing
        it would make the world model unable to reference her own history.
        """
        resolver = self._resolver_for(ref.kind)
        if ref.kind is KernelRefKind.CLAIM:
            return resolver.get(ref.record_id) is not None
        if ref.kind is KernelRefKind.SCAR:
            # Ruling 22: `get_scar` returns a DEEP COPY, so this cannot hand the
            # ledger a live record to mutate even by accident.
            return resolver.get_scar(ref.record_id) is not None
        if ref.kind is KernelRefKind.DOCTRINE:
            if resolver.get(ref.record_id) is not None:
                return True
            return ref.record_id in getattr(resolver, "fossils", {})
        if ref.kind is KernelRefKind.PREDICTION:
            return resolver.commitment_for(ref.record_id) is not None
        # EPISODE and OBLIGATION: an id-equality membership test over the
        # store's own append-order read. **A RECORDED EPISODE OR OBLIGATION
        # ALWAYS RESOLVES** - neither store erases, so membership is the whole
        # question (M3-A's claim-resolves rule, same reasoning).
        key = {KernelRefKind.EPISODE: "episode_id",
               KernelRefKind.OBLIGATION: "obligation_id"}[ref.kind]
        return any(entry.get(key) == ref.record_id
                   for entry in resolver.read_all())

    def _check_references(self, refs: Sequence[KernelRef]) -> None:
        """THE WRITE LAW. Every reference resolves, or the write REFUSES."""
        for ref in refs:
            # THE TYPE CHECK COMES FIRST. `PropositionRecord.__post_init__`
            # enforces it too, but that runs AFTER resolution - so without this
            # a bare id raised `AttributeError` from inside the resolver lookup
            # instead of refusing cleanly. Found by this module's own pin.
            if not isinstance(ref, KernelRef):
                raise TypeError(
                    f"a reference must be a KernelRef, got "
                    f"{type(ref).__name__}. A bare id cannot say which kernel "
                    f"store it lives in, and this ledger resolves by store "
                    f"rather than by guessing.")
            if self._resolver_for(ref.kind) is None:
                raise UnverifiableReference(
                    f"this ledger was built with no {ref.kind.value} resolver, "
                    f"so it cannot check '{ref.record_id}'. A reference it "
                    f"cannot verify is not admitted: asserting the record is "
                    f"absent would claim a test it never ran, and admitting it "
                    f"would claim a resolution it never performed.")
            if not self._exists(ref):
                raise UnresolvedReference(
                    f"no {ref.kind.value} record '{ref.record_id}' resolves "
                    f"against the kernel. A proposition citing evidence that "
                    f"does not exist is manufacturing truth at one remove, "
                    f"which is what the World Model domain forbids by name.")

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def record(self, kind: PropositionKind, asserted_content: str, *,
               supported_by: Sequence[KernelRef] = (),
               contradicted_by: Sequence[KernelRef] = (),
               predicted_by: Sequence[KernelRef] = (),
               supersedes: Optional[str] = None,
               interval_start: Optional[str] = None,
               interval_end: Optional[str] = None) -> PropositionRecord:
        """Record ONE proposition. Mint, append, return it. RAISES on refusal.

        **EVERY REFERENCE IS RESOLVED BEFORE ANYTHING IS MINTED OR WRITTEN** -
        Ruling 24/46's pre-flight boundary, so a refused proposition spends no
        ordinal and leaves no line.

        A proposition with NO references admits: UNGROUNDED is a real state, and
        refusing it would push callers to fabricate citations to get a write
        through.

        DELIBERATELY NOT ATOMIC (Rider R3's exemption, CAE's reason verbatim):
        a torn APPEND damages one line, which floor semantics already drop, and
        M4-δ's column-zero law keeps it from taking the next record with it.
        """
        if not isinstance(kind, PropositionKind):
            raise TypeError(
                f"kind must be a PropositionKind, got {type(kind).__name__}. A "
                f"raw string would let a caller invent a category of world-fact "
                f"the enum deliberately closes.")

        supported = tuple(supported_by)
        contradicted = tuple(contradicted_by)
        predicted = tuple(predicted_by)

        # PRE-FLIGHT, BEFORE THE MINT. Every reference, then the supersession.
        self._check_references(supported + contradicted + predicted)
        if supersedes is not None and self._get_record(supersedes) is None:
            raise UnresolvedReference(
                f"no proposition '{supersedes}' resolves in this ledger, so "
                f"nothing can supersede it. Supersession is how the world "
                f"model updates, and a successor to a record that was never "
                f"written would leave the live set claiming a history it does "
                f"not have.")

        with mint_lock(self.ledger_path):
            record = PropositionRecord(
                wmp_id=self._next_id(),
                kind=kind,
                asserted_content=asserted_content,
                supported_by=supported,
                contradicted_by=contradicted,
                predicted_by=predicted,
                supersedes=supersedes,
                interval_start=interval_start,
                interval_end=interval_end,
                recorded_wall=datetime.now().isoformat(),
            )
            entry = record.as_dict()
            # RULING 66's WRITER GATE, BEFORE `mkdir` and BEFORE the append.
            validate_record_value(entry, path="proposition_entry")
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            # RULING 78 res.2 + M4-δ: durable at its own write, through the
            # funnel, beginning at column 0.
            durable_append_text(self.ledger_path,
                                json.dumps(entry, allow_nan=False) + "\n")
            self.entries.append(entry)
        return record

    # -----------------------------------------------------------------
    # READS
    # -----------------------------------------------------------------
    #
    # **NO PUBLIC READ DOOR RETURNS `asserted_content` WITHOUT STANDING.** The
    # doors that carry content take a `derive` callable and return
    # `PropositionView`; the door the contradiction surface uses returns
    # `PropositionSummary`, which has no content at all.

    def _records(self) -> Tuple[PropositionRecord, ...]:
        """Every readable record, IN APPEND ORDER. PRIVATE, deliberately.

        This is the raw stream, content included, and it is not a public door:
        the module's own folds need it, and handing it out would be exactly the
        bare-text read R64's law forbids.

        ERA HONESTY - a line is returned as written; one that will not parse, or
        that carries a vocabulary member outside a closed enum, contributes
        NOTHING and is never coerced (floor semantics).
        """
        if not self.ledger_path.exists():
            return ()
        out: List[PropositionRecord] = []
        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                record = PropositionRecord.from_dict(data)
                if record is not None:
                    out.append(record)
        return tuple(out)

    def _get_record(self, wmp_id: str) -> Optional[PropositionRecord]:
        """The raw record by id. PRIVATE, and it was PUBLIC for one draft.

        **THIS FILE'S OWN PIN CAUGHT IT.** A public `get_record` returns a
        `PropositionRecord`, which carries `asserted_content` - a bare-text read,
        and precisely the hole R64's law exists to close. It is needed for
        SUPERSESSION resolution and for `resolves()`, both of which want identity
        rather than content, so it stays and stops being a door.
        """
        for record in self._records():
            if record.wmp_id == wmp_id:
                return record
        return None

    def resolves(self, wmp_id: str) -> bool:
        """Does this proposition exist? The TargetKind resolver's read.

        **A RECORDED PROPOSITION ALWAYS RESOLVES** - this ledger never erases,
        so membership is the whole question (M3-A's claim-resolves rule). No
        content crosses this boundary.
        """
        return self._get_record(wmp_id) is not None

    def _superseded_ids(self) -> frozenset:
        return frozenset(r.supersedes for r in self._records()
                         if r.supersedes is not None)

    def summaries(self) -> Tuple[PropositionSummary, ...]:
        """Every proposition's STRUCTURAL facts. **NO CONTENT.**"""
        return tuple(
            PropositionSummary(
                wmp_id=r.wmp_id, kind=r.kind, supported_by=r.supported_by,
                contradicted_by=r.contradicted_by, predicted_by=r.predicted_by,
                supersedes=r.supersedes)
            for r in self._records())

    def live_summaries(self) -> Tuple[PropositionSummary, ...]:
        """The LIVE set's structural facts. **NO CONTENT.**

        THE CURRENT WORLD IS A DERIVATION: a fold over the stream, never a
        stored snapshot (L3; Rulings 63/65). Live = not superseded by any later
        record.
        """
        superseded = self._superseded_ids()
        return tuple(s for s in self.summaries() if s.wmp_id not in superseded)

    def propositions(self, derive: Callable[[PropositionRecord], Any]
                     ) -> Tuple[PropositionView, ...]:
        """Every proposition, CONTENT AND STANDING TOGETHER.

        `derive` is REQUIRED and has no default. That is the enforcement: there
        is no way to ask this ledger for content and not be handed the standing
        beside it, so R64's reversed-meaning defect is unbuildable rather than
        reviewed for.
        """
        return tuple(PropositionView(record=r, standing=derive(r))
                     for r in self._records())

    def live(self, derive: Callable[[PropositionRecord], Any]
             ) -> Tuple[PropositionView, ...]:
        """The live set, content and standing together."""
        superseded = self._superseded_ids()
        return tuple(v for v in self.propositions(derive)
                     if v.wmp_id not in superseded)

    def get(self, wmp_id: str, derive: Callable[[PropositionRecord], Any]
            ) -> Optional[PropositionView]:
        record = self._get_record(wmp_id)
        return None if record is None else PropositionView(
            record=record, standing=derive(record))


# NOT REGISTERED IN `STORE_OWNERS`, AND THE CONDITION FOR REGISTERING IT IS NOT
# MET - stated rather than assumed, because M6's handoff reserved the row.
#
# The premise it reserved on is TRUE: `record()` is the one writer of the
# world's propositions. What is missing is a SCANNABLE UNIQUE ATTRIBUTE. The
# Ruling-1 invariant flags `<anything>.<name> = ...` across `src/`, so a row
# needs a name that names ONE store - and this ledger's only in-memory
# collection is `entries`, which THREE suspension stores already assign to
# (`self.entries[entry.id] = entry`, measured by AST). Registering it would flag
# correct code, which is Ruling 1's own warning and the precedent the invariant
# file records for `history`: "the honest move is to register the name that IS
# unique."
#
# There is no such name here for the same reason the eight sibling ledgers carry
# CAE's note: **the FILE is the store.** `entries` is a per-process mirror
# nothing reads back into a decision, so a row would police a shadow and claim
# coverage that does not exist - the completeness-claim defect. What guards this
# store instead is that `record()` is the only write path, pinned.
