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
    """A channel supplied a value. RULING 64 res.7: `None` is REFUSED.

    PROVIDED MEANS A VALUE IS PRESENT. `provided(None)` is a MALFORMED FOURTH
    STATE wearing the first one's name, and it is not harmless: two records
    with `asserted_by=provided(None)` are both PROVIDED and compare EQUAL, so
    `source_genealogy.shares_recorded_asserter` reads TWO EXPLICIT NULLS AS ONE
    SHARED ASSERTER - manufacturing the corroboration collapse that module
    exists to compute honestly.

    This is Ruling 58's own three-state argument ENFORCED AT THE CONSTRUCTOR
    rather than trusted: a caller who means "there is no asserter" has
    `declared_none()`, and one who was never asked has `absent()`. Both already
    refuse to carry a value (`AncestryField.__post_init__`); this closes the
    third door.
    """
    if value is None:
        raise ValueError(
            "provided(None) is not a state. PROVIDED means a value IS "
            "present - use declared_none() for 'there are none' or absent() "
            "for 'the channel said nothing'. Two records carrying "
            "provided(None) would compare EQUAL and be read as sharing one "
            "recorded asserter.")
    # RULING 82 (2026-08-09) - THE EMPTY IDENTITY IS REFUSED, res.7's GUARD
    # EXTENDED TO ITS OTHER SPELLING.
    #
    # Ruling 70 flagged this and deliberately did not decide it: an EMPTY
    # `model_identity` was accepted, and **two such records compare EQUAL and
    # read as ONE SHARED ASSERTER** - the identical failure mode res.7 closed
    # for `None`, arriving as `""` instead. The genealogy module cannot tell
    # them apart, because at that point there is nothing to tell apart.
    #
    # A CENSUS RAN FIRST (78 `provided(` call sites tree-wide, by AST): NOT ONE
    # passes an empty or whitespace-only string, so this refuses a state nothing
    # in the tree constructs - which is the only condition under which a guard
    # like this is a closure rather than a behaviour change.
    #
    # WHITESPACE-ONLY IS THE SAME DEFECT WEARING A CHARACTER. `" "` and `"\t"`
    # are not identities either, and two of them collide exactly as two empty
    # strings do. **The value is NOT stripped and NOT normalized** - Ruling 70
    # res.7 records the declared identity BYTE-IDENTICAL, so this refuses the
    # degenerate value rather than repairing it into a different one.
    #
    # STRINGS ONLY. `provided([])` and `provided({})` are untouched: an empty
    # container is a value a channel supplied, and deciding what an empty
    # replication list MEANS is a genealogy question this guard has no standing
    # to answer. **This changes what PROVIDED accepts; it changes nothing about
    # what ABSENT or DECLARED_NONE mean.**
    if isinstance(value, str) and not value.strip():
        raise ValueError(
            "provided('') is not a state. PROVIDED means a value IS present - "
            "use declared_none() for 'there are none' or absent() for 'the "
            "channel said nothing'. Two records carrying an empty or "
            "whitespace-only value would compare EQUAL and be read as sharing "
            "one recorded asserter (Ruling 82; Ruling 64 res.7's guard in its "
            "other spelling).")
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
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.atomic_write import durable_append_text
from src.utils.record_value import validate_record_value


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
    # M4-alpha (2026-08-15) - THE JOIN TO THE ARRIVAL THAT BECAME THIS CLAIM.
    #
    # A JOIN KEY, NOT AN ORIGIN FACT - `Echo.claim_id`'s and
    # `SuspensionEntry.claim_id`'s exact class, Ruling 60's canonical key
    # extended one layer OUT rather than in. It names the `ACQ-` record written
    # at the acquisition boundary immediately before this claim was minted.
    #
    # **THE DIRECTION IS FORCED, AND BY THE SAME STRUCTURE THAT FORCED RULING
    # 60's.** The acquisition ledger is append-only with no update family, and
    # the arrival is recorded BEFORE the claim id exists - so the acquisition
    # cannot carry the CLM, and the LATER artifact references the EARLIER. That
    # is verbatim the fork Ruling 60 faced for `Echo.claim_id` and resolved the
    # same way, for the same reason.
    #
    # ERA HONESTY: `None` means the claim predates the boundary record, or was
    # minted by a caller that recorded no arrival. **There is no backfill and no
    # inference** - a legacy line simply has no such key, `from_dict` reads it as
    # `None`, and nothing synthesizes one.
    acquisition_ref: Optional[str] = None

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
                         declaration: Optional[OriginDeclaration],
                         acquisition_ref: Optional[str] = None
                         ) -> "ClaimAncestryRecord":
        """Build the record. `None` means the channel declared NOTHING.

        THE NEW SURFACE FABRICATES NOTHING: no declaration produces
        `UNDECLARED` plus five ABSENT fields, which is the truthful record of a
        caller that said nothing - and is what every existing call site does.

        `acquisition_ref` is the same shape one layer out (M4-alpha): absent
        means no arrival record was written for this claim, recorded as `None`
        rather than as an invented id.
        """
        declaration = declaration or OriginDeclaration()
        return cls(
            claim_id=claim_id,
            origin_kind=declaration.kind,
            recorded_at=datetime.now().isoformat(),
            acquisition_ref=acquisition_ref,
            **{name: getattr(declaration, name) for name in ANCESTRY_FIELDS},
        )

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "claim_id": self.claim_id,
            "origin_kind": self.origin_kind.value,
            "recorded_at": self.recorded_at,
            # M4-alpha. Written on every new line; ABSENT from every legacy one,
            # which is what `from_dict`'s `.get` reads as `None`.
            "acquisition_ref": self.acquisition_ref,
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
                # ERA HONESTY (M4-alpha): a line written before the acquisition
                # boundary existed has no such key and reads as `None`. Nothing
                # is backfilled and nothing is inferred - a claim that predates
                # the boundary has no arrival record, and saying so is the
                # honest answer (Ruling 68's forensic law).
                acquisition_ref=data.get("acquisition_ref"),
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
        # RULING 69 (2026-08-02): THERE IS NO `self._seq`.
        #
        # It was derived once HERE and then incremented in memory forever after,
        # never re-synced - a CACHED DERIVATION OF THE FILE TRUSTED OVER ITS
        # SOURCE, the structure Ruling 63 refused at the projection and Ruling 65
        # refused at the topology. Two live instances over one path minted the
        # same ordinals whenever the second derived before the first appended.
        # Every mint now derives afresh under the file's lock; see `_next_id`.

    # -----------------------------------------------------------------
    # THE MINT - continuity state (Ruling 42 res.4), sentinel per Ruling 53
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `CLM-` ordinal already ON DISK, or `None` if UNDERIVED.

        RULING 69 res.1/res.2/res.5. The body moved to
        `src.utils.ledger_mint.derive_max_ordinal` - **HOISTED, not merely
        shared**: the three ledgers' derivations differed in exactly two ways (a
        local variable name and the JSON key each parsed), and res.2 deletes the
        second BY CONSTRUCTION because the scan no longer parses JSON. What
        remained was identical modulo `ID_PREFIX`.

        RULING 53'S SENTINEL IS UNCHANGED IN SEMANTICS: `None` IFF the ledger
        EXISTS and the read raised; a MISSING ledger is a legitimate `0`. The
        typed refusal stays HERE, in `_next_id`, because the error type is this
        ruling's own vocabulary and not the helper's.

        WHAT CHANGED IS WHAT IS SCANNED. This read `json.loads(line).get(...)`,
        so an ordinal on a TORN OR UNPARSEABLE LINE WAS INVISIBLE and the next
        mint would reissue it. The helper scans RAW TEXT with the anchored
        pattern, so any id that reached disk is seen and never reissued.
        """
        return derive_max_ordinal(self.ledger_path, self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. **DERIVED AT MINT TIME (Ruling 69).**

        CALLERS MUST HOLD `mint_lock(self.ledger_path)` ACROSS derive → mint →
        append. Deriving inside the lock and appending outside it would leave
        exactly the race this ruling closes, so the lock is taken at the WRITE
        path and this method is called within it.

        ~~RE-DERIVES ONCE against an underived mint before refusing, because the
        condition this guards is characteristically TRANSIENT - the whole defect
        was a read failure at construction that had cleared by write time. A
        recovered ledger therefore resumes from its REAL maximum rather than
        refusing a mutation it is now perfectly able to audit.~~

        SUPERSEDED 2026-08-02 BY RULING 69 res.1, kept because it names the
        property that still holds. **THE RE-DERIVE IS SUBSUMED: every mint
        derives**, so a recovered ledger resumes from its real maximum BY
        CONSTRUCTION rather than by a special case that had to be remembered.
        There is no longer a cached value for a transient failure to poison.

        STILL UNDERIVED, IT RAISES. It does NOT fall back to a number: an id
        minted from an unknown floor is exactly the collision Ruling 53 closed,
        and a duplicate id in an append-only ledger is unrecoverable by
        construction (entries are never overwritten, 3a:112, so nothing can ever
        go back and disambiguate the two).
        """
        seq = self._derive_seq()
        if seq is None:
            raise AncestryLedgerUnreadable(

                f"the claim-ancestry ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next CLM ordinal is UNKNOWN. Minting "
                f"one anyway could write an id that already names a different "
                f"claim, and an append-only ledger cannot later tell the two "
                f"apart. A claim whose origin cannot be recorded is not "
                f"perceived.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"
    # -----------------------------------------------------------------
    # THE ONLY WRITE PATH
    # -----------------------------------------------------------------

    def record(self, declaration: Optional[OriginDeclaration] = None,
               *, acquisition_ref: Optional[str] = None
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
        # RULING 69 res.3 - IN-PROCESS MINT-APPEND ATOMICITY. The lock is keyed
        # by the RESOLVED PATH and held across DERIVE -> MINT -> APPEND as one
        # unit; deriving inside it and appending outside would leave exactly the
        # race this ruling closes. It answers the threat that is real under the
        # declared topology (one AUREA process per data root, res.4): two
        # instances, or two threads, inside ONE process. OS file locking is
        # DECLARED OUT with its reopening condition named in `ledger_mint.py`.
        with mint_lock(self.ledger_path):
            return self._mint_and_append(declaration, acquisition_ref)

    def _mint_and_append(self, declaration: Optional[OriginDeclaration],
                         acquisition_ref: Optional[str] = None
                         ) -> ClaimAncestryRecord:
        """The locked critical section: derive, mint, validate, append.

        Split out so the lock scope is a whole method rather than an indented
        region - the boundary is then visible in the diff of any future
        change, which is what stops an append drifting out of it.
        """
        record = ClaimAncestryRecord.from_declaration(
            self._next_id(), declaration, acquisition_ref)
        entry = record.as_dict()

        # RULING 66 (2026-08-02) - THE WRITER GATE. Refuse what this ledger
        # cannot canonically hold, BEFORE the append. A record either holds what
        # was presented or refuses it; it may not hold something else instead,
        # and this store's entries are cited later by id, so a silently
        # stringified leaf here is a permanent claim that a string was
        # presented when it was not.
        #
        # BEFORE `mkdir` AND BEFORE `open`: a refused entry leaves no file, no
        # line, and no directory it did not already need. `allow_nan=False`
        # below is the SECOND half and is not redundant - it catches NaN and
        # Infinity at the serializer boundary if a future caller ever reaches
        # this write without passing through here.
        validate_record_value(entry, path="ancestry_entry")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        # RULING 78 res.2: durable at its own write. Bytes identical -
        # the serializer, the validator above and this store's error
        # discipline are unchanged; only the fsync is new.
        durable_append_text(self.ledger_path,
                            json.dumps(entry, allow_nan=False) + "\n")
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
