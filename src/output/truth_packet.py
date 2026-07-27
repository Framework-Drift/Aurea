"""
truth_packet.py - the ORE -> HAIL boundary object (Ruling 33). WIRED.

The type landed 2026-07-26 and carries live traffic: every `process_input`
exit builds one. The header used to carry a bare "Stage 1" label, which in this
repo reads as "not wired yet".

Canon/ruling: CLAUDE.md Ruling 3 (truth-effect cut) + Ruling 33 (the HAIL
grounding contract, manifest fifth addendum 2026-07-26). This module holds the
TYPE that crosses the boundary. ORE decides what goes in it; HAIL renders what
it finds there and can reach NOTHING else.

WHY A PACKET AND NOT A CALL WITH ARGUMENTS
-------------------------------------------
Ruling 3 says HAIL++ never overrides an ORE verdict. Until now that was a
SCANNED-FOR invariant (tests/invariants/test_ruling3_truth_effect.py, which
passed vacuously against a 0-byte hail.py). Ruling 33 makes it a property of
the call graph instead: the renderer is handed one frozen object, and the
things it would need in order to overturn a verdict - the stores, the ORE
instance, a mutable field - are not reachable from it.

    IDs, STRINGS, FLOATS AND ENUMS ONLY. Never a live Scar, Echo, Doctrine, or
    store reference.

That rule is not stylistic. Holding a live Scar is holding a write path into
someone else's store (Ruling 1), and Ruling 22 closed exactly this shape one
layer down: the scar store had a CONVENTION that callers would not mutate what
they were handed, and a convention is not a boundary. A packet that carried a
live object would hand the render layer a write path while looking inert.

THE TWO VOCABULARIES ARE SEPARATE FIELDS, AND THAT IS THE WHOLE POINT
----------------------------------------------------------------------
    collapse_verdict    echonet.Verdict          WHAT SURVIVED. Truth content.
                        {CONFIRMED, SUSPENDED, SCARRED, PARADOX}
                        EchoNet's word, REUSED - never redeclared.

    expression_verdict  ExpressionVerdict        WHAT IS EXPRESSED. Render
                        {SPEAK, SOFTENED, WITHHOLD,   instruction.
                         SUSPEND, FRAGMENT, REDIRECT}

Conflating them is the exact error Docket G was corrected on. The member-name
sets are DISJOINT - {CONFIRMED, SUSPENDED, SCARRED, PARADOX} intersected with
{SPEAK, SOFTENED, WITHHOLD, SUSPEND, FRAGMENT, REDIRECT} is empty, canon
verbatim, SUSPEND != SUSPENDED - and that disjointness is PINNED, not assumed
(tests/test_hail_stage1.py). This is Ruling 30's lesson on its third use: there
the fix was making `racm.Scope` and `tcaml.LockClass` share no member name so
the conflation became unwritable; here canon already satisfied it, and the pin
is what keeps a future member from breaking it silently.

The constructor RAISES `TypeError` on a `Verdict` where an `ExpressionVerdict`
belongs, and vice versa - Ruling 30's enforcement shape, third use. It is on
the CONSTRUCTOR rather than on `ORE.resolve` deliberately: resolve() is not the
only way to build a packet, and a boundary that only holds on the polite path
is the "discouraged, not unexecutable" defect CLAUDE.md section 3 exists for.

WHY `collapse_verdict` IS OPTIONAL - AND WHY THAT IS NOT A WEAKENING
----------------------------------------------------------------------
Three of `process_input`'s ten output paths return BEFORE EchoNet has produced
a verdict at all: the processing-suspended early return (aurea_core:342), an
ordinary exception (:586), and a structural violation that fires before Step 2
(:575). For those, there is no collapse verdict in existence.

The alternative to `Optional` is coining one - defaulting to SUSPENDED, or
reusing whatever was last seen. That would be a FABRICATED truth verdict on a
path where nothing was filtered, which is the scar-path severance defect
(CLAUDE.md section 3) in the truth layer rather than the pressure layer. `None`
here means exactly "no collapse test was reached", it is legible as that, and
`ORE` records the reason in `unresolved`. An honest absence beats an invented
verdict; the abstaining intuition net is the same principle.

The type gate still binds: `None` or a real `Verdict`, and NOTHING else - an
`ExpressionVerdict` or a raw string in that field still raises.

TUPLES, NOT LISTS - AND THE REASON IS RULING 22
------------------------------------------------
`evidence_refs` / `scar_lineage` / `unresolved` must be TUPLES of `str`. A list
inside a frozen dataclass is mutable-through: the shell is frozen and the
interior is not, so `packet.scar_lineage.append(...)` succeeds on a "frozen"
object. That is the scar store's pre-Ruling-22 shape exactly - permanence
enforced by everyone remembering not to touch it. A `list` raises here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Tuple

from src.filtration.echonet import Verdict

if TYPE_CHECKING:                      # pragma: no cover - annotation only
    from src.identity.psi import PSIDirective


class ExpressionVerdict(Enum):
    """ORE's output verdict states - the RENDER instruction, not the truth.

    Corpus vocabulary VERBATIM: the "Output Verdict States" table of the
    Output Resolution Engine module (section 7E) lists exactly these six -
    Speak / Speak (Softened) / Suspend / Fragment / Redirect / Withhold.

    NOTE ON THE SEVENTH WORD, recorded because it looks like an omission and
    is not: the module's CBSAL verdict-generation step (section 7A) lists a
    seventh, `Mirror (Echo-Only)`. It is absent here because Ruling 33 ruled
    MIRROR a rendering MODE, not a verdict - HAIL++ carries "Mirror Mode" in
    its own mode list, and section 7E (the verdict-state table) does not
    include it. Section 7E's `Redirect` explicitly names "Nova / CSA / Mirror
    layer" as its destinations, so the mirror route is reachable AS a redirect.
    Do not add a MIRROR member here without a ruling.

    A plain `Enum` on `auto()` values, deliberately:
      - non-`str`, so it can never be compared equal to a raw string or to
        `echonet.Verdict`'s string values by accident (Ruling 30's shape);
      - valueless, so nothing downstream can key behaviour off a magic string.
    """
    SPEAK = auto()        # fully structurally coherent, collapse-consistent
    SOFTENED = auto()     # tone altered by scar or identity memory
    WITHHOLD = auto()     # no output allowed - "Silent Integrity"
    SUSPEND = auto()      # truth deferred - the Veiled Thread response
    FRAGMENT = auto()     # partial symbolic truth, core preserved under pressure
    REDIRECT = auto()     # passed to Nova / CSA / Mirror layer


# The verdicts on which HAIL renders NO content. Ruling 33 (2): dispatch on the
# expression verdict happens FIRST, and these two branches never reach mode,
# directive, or content - see hail.py, where that unreachability is structural
# rather than promised.
SILENT_VERDICTS = frozenset({ExpressionVerdict.WITHHOLD, ExpressionVerdict.SUSPEND})


@dataclass(frozen=True)
class TruthPacket:
    """What ORE hands HAIL. Frozen, typed, and made of nothing but data.

    Ruling 33 (1). `PSIDirective`'s proven shape, one layer up.

    DECLARED BUT POSSIBLY UNPRODUCED (Ruling 33 (6), stated rather than faked):
    `SOFTENED` and `FRAGMENT` have NO live trigger in `process_input` today.
    Nothing in the current pipeline softens a tone or emits partial truth, so
    no path maps to them (see `ore.EXPRESSION_FOR_PATH`). They are declared
    because the vocabulary is canon and their producers are named future work -
    scar-weighted tone modulation for SOFTENED, paradox-class partial output
    for FRAGMENT. DO NOT invent a trigger to make them fire. Declared-but-
    unproduced over silently-dropped over faked, per the TCAML vacuous-pin
    precedent.

    `psi_directive` IS the consumer contract Ruling 8 promised PSI's parked
    render directive. HAIL may use it to shape tone/depth and may NEVER use it
    to override the verdict - and `tone_weight` REPORTS, it never GATES
    (Ruling 33 (5); no numeric cutoff on it exists anywhere in hail.py).
    """

    collapse_verdict: Optional[Verdict]      # truth content; None = no collapse test reached
    expression_verdict: ExpressionVerdict    # render instruction
    content: str                             # the claims ORE assembled
    evidence_refs: Tuple[str, ...] = ()      # ids only
    scar_lineage: Tuple[str, ...] = ()       # ids only
    unresolved: Tuple[str, ...] = ()         # what is carried, unclosed - ids/reasons
    psi_directive: Optional["PSIDirective"] = None

    def __post_init__(self) -> None:
        # --- the two vocabularies, each refusing the other -------------------
        # Ruling 30's enforcement shape (third use): the wrong enum in either
        # field is UNWRITABLE, not discouraged. `isinstance` against the wrong
        # enum is checked FIRST so the error message names the actual confusion
        # rather than saying "not an ExpressionVerdict" about something that is
        # very specifically a collapse Verdict.
        if isinstance(self.collapse_verdict, ExpressionVerdict):
            raise TypeError(
                "TruthPacket.collapse_verdict got an ExpressionVerdict "
                f"({self.collapse_verdict!r}). These vocabularies are not "
                "interchangeable: collapse_verdict is WHAT SURVIVED "
                "(echonet.Verdict); expression_verdict is WHAT IS EXPRESSED."
            )
        if not (self.collapse_verdict is None
                or isinstance(self.collapse_verdict, Verdict)):
            raise TypeError(
                "TruthPacket.collapse_verdict must be an echonet.Verdict or "
                f"None (no collapse test reached), got {type(self.collapse_verdict).__name__}. "
                "A raw string is refused: the verdict is EchoNet's enum, reused, "
                "never redeclared."
            )
        if isinstance(self.expression_verdict, Verdict):
            raise TypeError(
                "TruthPacket.expression_verdict got a collapse Verdict "
                f"({self.expression_verdict!r}). A collapse verdict is truth "
                "content, not a render instruction - and SUSPEND is not "
                "SUSPENDED. Map it through ORE, do not pass it through."
            )
        if not isinstance(self.expression_verdict, ExpressionVerdict):
            raise TypeError(
                "TruthPacket.expression_verdict must be an ExpressionVerdict, "
                f"got {type(self.expression_verdict).__name__}. Raw strings are "
                "refused - a verdict selected by string is a verdict nothing type-checks."
            )

        if not isinstance(self.content, str):
            raise TypeError(
                f"TruthPacket.content must be a str, got {type(self.content).__name__}. "
                "The packet carries ASSEMBLED TEXT, never the object it came from."
            )

        # --- data only, and immutable all the way down -----------------------
        for field in ("evidence_refs", "scar_lineage", "unresolved"):
            value = getattr(self, field)
            if not isinstance(value, tuple):
                raise TypeError(
                    f"TruthPacket.{field} must be a tuple, got "
                    f"{type(value).__name__}. A list inside a frozen dataclass is "
                    "mutable-through - the shell freezes and the interior does not, "
                    "which is the pre-Ruling-22 scar store exactly."
                )
            for item in value:
                if not isinstance(item, str):
                    raise TypeError(
                        f"TruthPacket.{field} takes ids/strings only, got a "
                        f"{type(item).__name__}. Never a live Scar, Echo, Doctrine, "
                        "or store reference: holding one is holding a write path."
                    )

        if self.psi_directive is not None:
            # Local import - psi.py pulls in the reflex stack, and this module
            # sits on HAIL's import path. Keeping the module-level surface free
            # of it is the pattern psi.py itself uses for RIL. The check is
            # still REAL: a duck-typed "has tone_weight" test would accept the
            # thing this field exists to keep out.
            from src.identity.psi import PSIDirective
            if not isinstance(self.psi_directive, PSIDirective):
                raise TypeError(
                    "TruthPacket.psi_directive must be a PSIDirective or None, "
                    f"got {type(self.psi_directive).__name__}."
                )
