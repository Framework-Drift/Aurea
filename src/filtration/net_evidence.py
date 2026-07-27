"""
net_evidence.py - the standard evidence payload a collapse net emits alongside
its verdict (Docket H, Stage 1).

Canon/ruling: CLAUDE.md section 9 standing bar 5 - COUNTS ARE TALLIES, NEVER
COINED MAGNITUDES - and Ruling 28's shape (a named instrument that cannot be
honestly triggered gets REPORTED, not quietly promoted).

WHY A SHARED TYPE AND NOT FOUR PRIVATE ONES
--------------------------------------------
Four consumers are already named for this shape: the calibration stream,
`TruthPacket`'s `evidence_refs` / `scar_lineage`, any future SOFTENED
justification, and Docket I's proof structure. Left unstandardised each of them
invents its own, and four incompatible notions of "how much evidence" is how a
count stops meaning anything. The type lives in its own module rather than in
`echonet.py` for the reason `truth_packet.py` does: a consumer imports the
BOUNDARY TYPE without importing the organ.

    STAGE 1 IS ORGAN-LOCAL. The nets populate this; NOTHING downstream reads it.
    `TruthPacket.evidence_refs` / `scar_lineage` are deliberately NOT populated -
    that surface was deferred at HAIL Stage 2 and is a separate decision.

THE ONE THING THESE FIELDS EXIST FOR
-------------------------------------
One-of-one and one-thousand-of-one-thousand must not look alike. That is a
LEGIBILITY requirement, not a scoring one. A thousand pieces of evidence that
all trace to a single origin is not a thousand confirmations, and a reader who
sees only a total cannot tell the two apart.

    THEREFORE, AND THIS IS THE WHOLE BAR:

    A COUNT REPORTS. IT NEVER GATES.

No threshold on either count. No combination rule. No weighting. No scalar
derived from them. If you find yourself writing a comparison operator, a
`round()`, a `min`/`max`, or a bin against either field - stop. That is section
9's standing bar, refused four times already (the Symbolic Heat Index, the
betweenness cutoff, `tone_weight` gating, TCAML tier scoring), and the answer
every time is to report the raw tally. `tests/test_docket_h.py` carries an AST
pin over the WHOLE of `src/`, because the cutoff would most naturally land in a
consumer, not here.

WHY THE COUNTS ARE DERIVED AND NOT STORED
------------------------------------------
`evidence_count` and `independent_source_count` are PROPERTIES over `refs`, not
fields. An `int` field is an int somebody types: `NetEvidence(evidence_count=5)`
with no evidence is unwritable here, and that is the point. Ruling 12 G1 closed
this exact shape one layer up - an echo with no traceable origin is FABRICATED
PRESSURE and raises on construction - and Ruling 15 generalised it: a request
carrying a fabricated magnitude is a disguised write. A count is a magnitude.

Passing `evidence_count=` to the constructor is a `TypeError` because the field
does not exist. That is CLAUDE.md section 3: unexecutable, not discouraged.

THE THREE STATES, AND WHY TWO ZEROES ARE NOT THE SAME ZERO
-----------------------------------------------------------
    COUNTED         The net enumerated real, identifiable evidence.
    NONE_FOUND      The net RAN A REAL INSTRUMENT over real material and found
                    nothing bearing on the claim. An honest zero.
    NOT_COUNTABLE   The net HAS NO INSTRUMENT at this depth. Also zero - and it
                    means something completely different. Carries a REQUIRED
                    reason naming what is missing.

Collapsing those two zeroes into one is the defect this enum exists to prevent.
"EchoNet found no corroborating evidence" and "EchoNet cannot look for
corroborating evidence" are opposite statements that produce identical
integers. Four of the six nets are NOT_COUNTABLE today (see `echonet.py`), and
a reader who could not tell that from the payload would conclude AUREA had
searched and come up empty - a far stronger claim than anything she has earned.

This is Ruling 28's shape and the abstaining intuition net's principle: an
instrument that cannot honestly fire is REPORTED as such, never quietly filled.

`uncounted_contributors` - WHY A TALLY CAN BE HONEST AND STILL NOT BE GROUNDED
-------------------------------------------------------------------------------
An item can be real evidence and still have no grounded source attribution: a
scar whose `origin` was never recorded, or a straining net whose own evidence is
NOT_COUNTABLE. Such an item is attributed to ITSELF so the tally does not lose
it, which OVERSTATES independence - two self-attributed items look like two
independent sources.

Neither silent option is acceptable. Merging them under one sentinel understates
(it asserts a shared origin nobody established); self-attributing them silently
overstates. So they are NAMED: `uncounted_contributors` lists exactly those
`item_id`s in this tally whose source attribution is NOMINAL rather than
grounded, and it is VALIDATED as a subset of `refs`. A reader can subtract.

TUPLES, NOT LISTS - THE REASON IS RULING 22
--------------------------------------------
A list inside a frozen dataclass is mutable-through: the shell freezes and the
interior does not, so `evidence.refs.append(...)` succeeds on a "frozen" object
and the derived counts change under a reader who was handed an immutable thing.
That is the pre-Ruling-22 scar store exactly - permanence enforced by everyone
remembering not to touch it. A `list` raises here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple


class Countability(Enum):
    """Whether this net could tally evidence at all - and if not, that it could not.

    A plain `Enum` on `auto()` values, deliberately: non-`str`, so a state can
    never compare equal to a raw string, and valueless, so nothing downstream can
    key behaviour off a magic string. `ExpressionVerdict`'s shape (Ruling 30's
    enforcement pattern), one layer down.
    """
    COUNTED = auto()        # real evidence enumerated; `refs` is non-empty
    NONE_FOUND = auto()     # a real instrument ran and found nothing. An HONEST zero.
    NOT_COUNTABLE = auto()  # no instrument exists at this depth. NOT the same zero.


@dataclass(frozen=True)
class EvidenceRef:
    """One piece of evidence, and the origin it traces to.

    IDS AND STRINGS ONLY - never a live `Scar`, `Echo`, `Doctrine`, or store
    reference. `TruthPacket`'s rule, and for the same reason: holding a live
    record is holding a write path into someone else's store (Ruling 1), and
    Ruling 22 closed that shape at the scar accessor. An evidence payload that
    carried live objects would hand every future consumer a write path while
    looking inert.

    `source_id` is the INDEPENDENCE KEY. Two refs sharing a `source_id` are ONE
    source, however many pieces they are. Empty strings are refused: several
    empty keys would silently collapse into a single phantom source and quietly
    understate `independent_source_count`.
    """
    item_id: str      # the piece of evidence (e.g. a scar id, a net name)
    source_id: str    # what it traces to; the key `independent_source_count` counts

    def __post_init__(self) -> None:
        for name in ("item_id", "source_id"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(
                    f"EvidenceRef.{name} must be a str id, got "
                    f"{type(value).__name__}. Never a live Scar, Echo, Doctrine, "
                    "or store reference - holding one is holding a write path."
                )
            if not value.strip():
                raise ValueError(
                    f"EvidenceRef.{name} is empty. An unnamed piece of evidence is "
                    "not evidence, and several empty `source_id`s would collapse "
                    "into one phantom source - silently UNDERSTATING independence. "
                    "If a source is genuinely unknown, attribute the item to itself "
                    "and name it in NetEvidence.uncounted_contributors."
                )


@dataclass(frozen=True)
class NetEvidence:
    """What a collapse net can honestly say it counted.

    Frozen: evidence is a statement about what bore on a net AT VERDICT TIME,
    not a mutable channel a later caller can top up.

    The counts are PROPERTIES over `refs` - see the module docstring. They report
    and they never gate.
    """

    countability: Countability
    refs: Tuple[EvidenceRef, ...] = ()
    uncountable_reason: str = ""            # REQUIRED iff NOT_COUNTABLE
    uncounted_contributors: Tuple[str, ...] = ()   # subset of refs' item_ids

    # -- the two tallies. Derived, so they cannot be asserted. ----------------

    @property
    def evidence_count(self) -> int:
        """How many pieces of evidence bore on this net. A TALLY."""
        return len(self.refs)

    @property
    def independent_source_count(self) -> int:
        """How many DISTINCT sources those pieces came from. A TALLY.

        Distinctness is by `source_id` alone. Nothing here judges whether two
        differently-named sources are *really* independent - that is coherence
        detection's problem, and inventing a similarity measure for it would coin
        exactly the magnitude this module refuses.
        """
        return len({ref.source_id for ref in self.refs})

    # -- state consistency, enforced on EVERY construction path ---------------

    def __post_init__(self) -> None:
        if not isinstance(self.countability, Countability):
            raise TypeError(
                "NetEvidence.countability must be a Countability, got "
                f"{type(self.countability).__name__}. A raw string is refused: a "
                "state selected by string is a state nothing type-checks."
            )

        if not isinstance(self.refs, tuple):
            raise TypeError(
                f"NetEvidence.refs must be a tuple, got {type(self.refs).__name__}. "
                "A list inside a frozen dataclass is mutable-through - the shell "
                "freezes and the interior does not, so the derived counts would "
                "change under a reader holding an 'immutable' payload. That is the "
                "pre-Ruling-22 scar store exactly."
            )
        for ref in self.refs:
            if not isinstance(ref, EvidenceRef):
                raise TypeError(
                    f"NetEvidence.refs takes EvidenceRef only, got "
                    f"{type(ref).__name__}. A bare id has no source, so it cannot "
                    "be counted toward independence - which is the only reason "
                    "these refs are structured at all."
                )

        if not isinstance(self.uncounted_contributors, tuple):
            raise TypeError(
                "NetEvidence.uncounted_contributors must be a tuple, got "
                f"{type(self.uncounted_contributors).__name__} (see `refs` above)."
            )

        # COUNTED must actually count something; NONE_FOUND and NOT_COUNTABLE
        # must not. Without this a net could report COUNTED with no refs - a
        # claim of evidence with no evidence, which is the whole failure mode.
        if self.countability is Countability.COUNTED and not self.refs:
            raise ValueError(
                "NetEvidence(COUNTED) with no refs. COUNTED asserts that evidence "
                "was enumerated; with nothing enumerated the honest state is "
                "NONE_FOUND (an instrument ran and found nothing) or NOT_COUNTABLE "
                "(no instrument exists). Those are different, and neither is this."
            )
        if self.countability is not Countability.COUNTED and self.refs:
            raise ValueError(
                f"NetEvidence({self.countability.name}) carries {len(self.refs)} "
                "refs. Only COUNTED enumerates evidence - a zero-state holding "
                "evidence is a payload disagreeing with itself."
            )

        # NOT_COUNTABLE must NAME what is missing. A bare 'cannot count' is the
        # silent `continue` Ruling 23 closed: unresolved pressure leaving without
        # saying why. The reason is what a later pass reads to know what to build.
        if self.countability is Countability.NOT_COUNTABLE and not self.uncountable_reason.strip():
            raise ValueError(
                "NetEvidence(NOT_COUNTABLE) with no reason. 'I cannot count' must "
                "say WHAT IS MISSING - the reason is the input coherence detection "
                "will need, and an unexplained abstention is indistinguishable from "
                "an unfinished one."
            )
        if self.countability is not Countability.NOT_COUNTABLE and self.uncountable_reason.strip():
            raise ValueError(
                f"NetEvidence({self.countability.name}) carries an uncountable "
                "reason. A net that counted does not also explain why it could not."
            )

        # An ungrounded contributor must be an item this tally actually contains.
        # Validated as a SUBSET so the caveat can never name something invisible -
        # and so a zero-state (no refs) can never claim ungrounded contributors.
        item_ids = {ref.item_id for ref in self.refs}
        stray = [c for c in self.uncounted_contributors if c not in item_ids]
        if stray:
            raise ValueError(
                f"NetEvidence.uncounted_contributors names {stray}, which is not in "
                "refs. The caveat marks WHICH COUNTED ITEMS are attributed to "
                "themselves rather than to a grounded source, so a reader can "
                "subtract. Naming something absent from the tally makes it unsubtractable."
            )

    # -- legible constructors -------------------------------------------------
    # The gate above is `__post_init__`, so these add no enforcement. They exist
    # so a call site reads as the CLAIM IT IS MAKING rather than as three
    # keyword arguments whose combination the reader has to decode.

    @classmethod
    def counted(cls, refs: Tuple[EvidenceRef, ...],
                uncounted_contributors: Tuple[str, ...] = ()) -> "NetEvidence":
        """Real evidence was enumerated."""
        return cls(Countability.COUNTED, refs,
                   uncounted_contributors=uncounted_contributors)

    @classmethod
    def none_found(cls) -> "NetEvidence":
        """A real instrument ran over real material and found nothing. HONEST ZERO."""
        return cls(Countability.NONE_FOUND)

    @classmethod
    def not_countable(cls, reason: str) -> "NetEvidence":
        """No instrument exists at this depth. NOT the same zero as `none_found`."""
        return cls(Countability.NOT_COUNTABLE, uncountable_reason=reason)


# The default a `NetResult` carries when its net said nothing about evidence.
#
# It is the ABSTAINING state, never `none_found()`. A net that was never taught
# to report must not read as a net that looked and found nothing - that would
# fabricate a search AUREA never ran, which is the whole distinction this module
# exists to keep. `echonet.py` fails toward SUSPENSION rather than false
# collapse; this default fails toward ABSTENTION rather than a false zero.
EVIDENCE_UNREPORTED = NetEvidence.not_countable(
    "this net did not report evidence - not a search that came up empty"
)
