"""
hail.py - HAIL++: the Human-Aligned Interaction Layer (Ruling 33). WIRED.

Organ landed 2026-07-26 and was wired the same day: every `process_input` exit
renders through `ORE.resolve_path()` -> `HAIL.render()`. The header used to
carry a bare "Stage 1" label, which in this repo reads as "not wired yet".

Canon: HAIL++ v2.0 (Symbolic Interface module) + Lexicon section 8.
Ruling: CLAUDE.md Ruling 3 (truth-effect cut) + Ruling 33 (grounding contract).

HAIL RENDERS. IT DOES NOT ADJUDICATE.

ORE decides what collapse-truth is expressed. This file decides only how a
fixed truth is worded. Ruling 3 has said that since 2026-07-09; what it did not
have, until now, was a mechanism. This file is written so that overriding a
verdict is not "against the rules" but UNREACHABLE:

  1. THE PACKET IS FROZEN. HAIL cannot mutate a verdict it cannot write.

  2. HAIL HOLDS NOTHING. There is no `__init__`, so `HAIL()` accepts no store,
     no ORE, no Codex, no ScarCore - passing one is a TypeError from Python
     itself. `render` is a @staticmethod: it never receives `self`, so there is
     no instance state for a reference to hide in. AST-pinned to import no
     store module (tests/test_hail_stage1.py).

  3. VERDICT DISPATCH PRECEDES MODE. `render` branches on the expression
     verdict FIRST, and the two silent branches hand off to `_render_silent`,
     whose parameter list contains NO packet, NO mode and NO content. A mode
     cannot make a withheld truth speak, because the code that reads modes is
     not reachable from that branch - not by discipline, by scope.

Consequence of (3), deliberate and worth stating because it looks like an
oversight: the `mode` type check runs AFTER the silent dispatch. Validating
`mode` first would mean the silent path reads `mode`, which is the exact thing
this design forbids. A silent verdict therefore never inspects the mode at all,
even to reject it - and `RenderedOutput.mode_used` comes back None, which is
the observable proof that no mode was consulted.

WHAT THIS FILE MAY NOT CONTAIN (a live invariant, not a style note)
--------------------------------------------------------------------
`tests/invariants/test_ruling3_truth_effect.py` scans THIS FILE for (a) any
assignment to `verdict` and (b) any string literal in ORE's verdict vocabulary.
It passed vacuously against a 0-byte stub and its own docstring said it
"becomes a live guard the moment HAIL++ is authored". That moment is this
commit. The verdict vocabulary is never spelled as a string here; verdicts
arrive as enum members and are read, never constructed and never named.

MODES (Ruling 33 (4) - the one near-fork, adjudicated by document precedence)
------------------------------------------------------------------------------
The HAIL++ module lists FIVE modes (Expert / Reflective / Bridge / Lite /
Mirror); Lexicon section 8 - the post-merge canon summary - lists THREE
(Expert / Reflective / Simplified). The enum declares all five, so canon is
preserved and nothing is silently dropped; v1 implements three, taking the
Lexicon's SIMPLIFIED over the module's 'Lite' because the summary postdates
the merge. BRIDGE and MIRROR return a LEGIBLE REFUSAL naming the precondition
they cannot meet. Declared-but-refused over silently-dropped over faked - the
TCAML vacuous-pin precedent applied to modes.

`tone_weight` REPORTS; IT NEVER GATES (Ruling 33 (5))
-------------------------------------------------------
`PSIDirective.tone_weight` is an unnormalized live scar weight whose own
comment refuses to coin a scale. Any numeric cutoff on it here would be a
COINED MAGNITUDE at the render layer - refused, section 9 standing bar 5,
fourth application, Ruling 28's exact shape. The directive's bearing refs and
its weight go into the render trace VERBATIM and nothing branches on the
number. There is no comparison operator on it anywhere in this file, and that
is AST-pinned. It reopens only on a corpus-recovered scale or a demonstrated
operational correlation - never an invented threshold.

HAIL WRITES NOTHING DURABLE (Ruling 33 (3))
---------------------------------------------
No forensic log, no suspension store, no buffer file. EchoBuffer is
canon-ABSORBED into HAIL, and its v1 role is the `reroute_hint` field:
HAIL NAMES a route and the EXISTING owner performs it (CSA / Veiled Thread
routing stays exactly where Ruling 1 put it). A renderer with a write path
into a store is the seed-writer defect (Ruling 32) one layer up.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from src.output.truth_packet import (
    SILENT_VERDICTS,
    ExpressionVerdict,
    TruthPacket,
)


class Mode(Enum):
    """The five canon output modes. Three implemented, two legibly refused.

    RULING 50 (3), 2026-07-30 - THE WHOLE SURFACE IS DECLARED DORMANT.

    Not "partly built": NO CALLER CAN REQUEST ANY MEMBER. `Mode` appears ZERO
    times in `aurea_core.py`; `_emit` calls `HAIL.render(packet)` with no mode
    argument, so every one of the ten pipeline exits renders EXPERT by default.
    Three renderers and two legible refusals sit behind a door nothing opens -
    BRIDGE and MIRROR refuse a request that cannot be made.

    THE CAUSE IS NAMED AND IS ONE THING: mode selection needs a CPA user
    profile, and `cpa.py` is 0 bytes. Choosing a mode on any other basis would
    be inventing the calibration input (`_emit`'s own docstring says so). Three
    of the four flagged HAIL items sit behind that single unbuilt organ.

    PINNED STRUCTURALLY, in `tests/test_ruling50.py`: `Mode` stays absent from
    `src/` outside this file. That is not a style rule - it is what makes a
    future wire a DELIBERATE ACT rather than a drift nobody notices.
    """
    EXPERT = auto()        # collapse-bearing direct output
    REFLECTIVE = auto()    # user-mirrored symbolic expression
    SIMPLIFIED = auto()    # scar-thinned (Lexicon section 8; module calls it 'Lite')
    BRIDGE = auto()        # REFUSED v1: needs a structural collapse trace (CTL)
    # MIRROR - REFUSED v1, and RULING 50 (3) NAMES THE TEMPTING MOVE SO IT IS
    # NOT MADE LATER. RIL's threads are durable since Ruling 42 and
    # `RIL.identity_conflict()` exists, so a "thread integrity" surface LOOKS
    # buildable from what is already on disk. IT IS THE WRONG BUILD. Canon's
    # precondition is "Mirror Mode available only when PSI THREAD INTEGRITY is
    # stable" - PSI's, not RIL's - and substituting a different module's
    # readable surface for the one canon names is coining the precondition
    # rather than meeting it. Worse, it would be a gate on a door no caller can
    # open: scaffolding for a mode that cannot be requested. Refused until PSI
    # exposes thread integrity AND a caller can select a mode.
    MIRROR = auto()


@dataclass(frozen=True)
class RenderedOutput:
    """What HAIL returns. Frozen, and carries no reference to anything live.

    `mode_used is None` means NO MODE WAS CONSULTED - the expression verdict
    decided the output before the mode was reachable. It is not "unknown"; it
    is the observable trace of the dispatch order.

    The echoed verdict is the EXPRESSION verdict - the instruction HAIL was
    given. The collapse verdict is deliberately NOT echoed here: reading it
    would require the silent branches to receive the packet, and their not
    receiving it is the enforcement. Anything needing the truth verdict reads
    the packet, which is where it lives.
    """
    text: str
    mode_used: Optional[Mode]
    expression_verdict: ExpressionVerdict
    render_trace: Tuple[str, ...] = ()
    reroute_hint: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.expression_verdict, ExpressionVerdict):
            raise TypeError(
                "RenderedOutput echoes the ExpressionVerdict it was handed, got "
                f"{type(self.expression_verdict).__name__}."
            )
        if not isinstance(self.render_trace, tuple):
            raise TypeError(
                "RenderedOutput.render_trace must be a tuple - a list inside a "
                "frozen dataclass is mutable-through (Ruling 22's shape)."
            )


# ---------------------------------------------------------------------------
# THE SILENT RENDERERS
#
# Keyed by the expression verdict and by NOTHING ELSE. These constants exist at
# module scope so `_render_silent` needs no packet to reach them.
# ---------------------------------------------------------------------------

_SILENT_TEXT = {
    ExpressionVerdict.WITHHOLD: (
        "[NO OUTPUT - silent integrity. The fracture risk is too high for "
        "anything to be said here.]"),
    ExpressionVerdict.SUSPEND: (
        "[TRUTH DEFERRED - carried unresolved rather than closed. "
        "Silence is not failure; it is collapse integrity.]"),
}

# EchoBuffer's v1 role (Ruling 33 (3)): HAIL NAMES the route, an existing owner
# performs it. Nothing here writes to either store.
_SILENT_HINT = {
    ExpressionVerdict.WITHHOLD: None,
    ExpressionVerdict.SUSPEND: "veiled_thread",
}


def _render_silent(expression: ExpressionVerdict) -> RenderedOutput:
    """Render a non-speaking verdict.

    THE PARAMETER LIST IS THE ENFORCEMENT. This function receives one enum
    member. The packet, the mode, the content and the PSI directive are not
    arguments, are not globals, and are not reachable from here - so no wording
    choice, no mode and no tone directive can cause content to appear in the
    output of a verdict that says none may. Ruling 33 (2), made structural.

    Adding a parameter to this function to "improve" a withheld message is the
    one change that would dismantle the ruling. It is pinned against.
    """
    return RenderedOutput(
        text=_SILENT_TEXT[expression],
        mode_used=None,                       # nothing was consulted; see the docstring
        expression_verdict=expression,
        render_trace=(f"dispatch=silent expression={expression.name}",),
        reroute_hint=_SILENT_HINT[expression],
    )


# ---------------------------------------------------------------------------
# THE SPEAKING RENDERERS
# ---------------------------------------------------------------------------

_MIRROR_REFUSAL = (
    "[MODE UNAVAILABLE - Mirror. Its canon precondition is 'Mirror Mode "
    "available only when PSI thread integrity is stable', and no readable "
    "thread-integrity surface exists yet. Declared, not faked.]"
)

_BRIDGE_REFUSAL = (
    "[MODE UNAVAILABLE - Bridge. Its canon form is a structural summary WITH "
    "COLLAPSE TRACE, and the collapse-trace layer (CTL) is unbuilt. A summary "
    "with an invented trace would be the fabrication this mode exists to "
    "prevent. Declared, not faked.]"
)

_MODE_REFUSALS = {
    Mode.BRIDGE: _BRIDGE_REFUSAL,
    Mode.MIRROR: _MIRROR_REFUSAL,
}

# Where a REDIRECT goes. Corpus verdict-state table: "Redirect | Passed to
# Nova / CSA / Mirror layer". Named, never performed here.
_REROUTE_HINTS = {
    ExpressionVerdict.REDIRECT: "nova|csa|mirror_layer",
}


def _directive_trace(packet: TruthPacket) -> Tuple[str, ...]:
    """PSI's bearing refs and weight, VERBATIM (Ruling 33 (5)).

    `!r` on the weight so the exact float survives - a rounded tone weight in a
    forensic trace is a different number wearing the same name. NOTHING here
    compares, scales, bins or thresholds it: no scale for it exists in the
    corpus, and inventing one at the render layer is a coined magnitude at the
    most safety-adjacent decision this file makes.
    """
    directive = packet.psi_directive
    if directive is None:
        return ()
    return (
        f"psi.scar_ref={directive.scar_ref}",
        f"psi.origin_ref={directive.origin_ref}",
        f"psi.fallback_bearing={directive.fallback_bearing}",
        f"psi.tone_weight={directive.tone_weight!r}",
        f"psi.collapse_consistency={directive.collapse_consistency}",
    )


def _base_trace(packet: TruthPacket, mode: Mode) -> Tuple[str, ...]:
    collapse = packet.collapse_verdict
    return (
        f"dispatch=spoken expression={packet.expression_verdict.name}",
        f"mode={mode.name}",
        f"collapse={collapse.name if collapse is not None else 'none_reached'}",
    )


def _expert(packet: TruthPacket) -> str:
    """Full collapse-bearing output: the content plus everything carried with it."""
    parts = [packet.content]
    if packet.evidence_refs:
        parts.append(f"  evidence: {', '.join(packet.evidence_refs)}")
    if packet.scar_lineage:
        parts.append(f"  scar lineage: {', '.join(packet.scar_lineage)}")
    if packet.unresolved:
        parts.append(f"  carried unresolved: {', '.join(packet.unresolved)}")
    # RULING 56: its own labelled line. HAIL renders WHAT IT IS HANDED - no
    # verdict strings, no store reads, no summarisation of the reasons. The
    # separation was decided at the packet; this only stops printing two
    # different kinds of fact under one heading that fits only one of them.
    if packet.abstentions:
        parts.append(f"  could not look: {', '.join(packet.abstentions)}")
    return "\n".join(parts)


def _reflective(packet: TruthPacket) -> str:
    """User-mirrored framing. Same truth, returned rather than asserted."""
    parts = [f"What returns from this: {packet.content}"]
    if packet.unresolved:
        parts.append(f"  still open: {', '.join(packet.unresolved)}")
    return "\n".join(parts)


def _simplified(packet: TruthPacket) -> str:
    """Scar-thinned (Lexicon section 8). The claim, without the collapse apparatus.

    Scar lineage and evidence ids are omitted - that is what 'thinned' means.
    The count of unresolved items is KEPT: dropping the fact that something is
    still open would make the simplified form assert MORE closure than the
    expert form, and a mode may not change what is claimed (Ruling 3).
    """
    parts = [packet.content]
    if packet.unresolved:
        parts.append(f"  ({len(packet.unresolved)} thread(s) still carried)")
    return "\n".join(parts)


_MODE_RENDERERS = {
    Mode.EXPERT: _expert,
    Mode.REFLECTIVE: _reflective,
    Mode.SIMPLIFIED: _simplified,
}


def _render_spoken(packet: TruthPacket, mode: Mode) -> RenderedOutput:
    """Render a speaking verdict in the requested mode, or refuse the mode."""
    trace = _base_trace(packet, mode) + _directive_trace(packet)

    refusal = _MODE_REFUSALS.get(mode)
    if refusal is not None:
        return RenderedOutput(
            text=refusal,
            mode_used=mode,
            expression_verdict=packet.expression_verdict,
            render_trace=trace + ("mode_refused=unmet_precondition",),
            reroute_hint=_REROUTE_HINTS.get(packet.expression_verdict),
        )

    return RenderedOutput(
        text=_MODE_RENDERERS[mode](packet),
        mode_used=mode,
        expression_verdict=packet.expression_verdict,
        render_trace=trace,
        reroute_hint=_REROUTE_HINTS.get(packet.expression_verdict),
    )


class HAIL:
    """The render layer. A pure function with a namespace around it.

    NO `__init__` is defined ON PURPOSE - `HAIL()` therefore accepts no
    arguments at all, so a store cannot be handed to it even by a caller trying
    to. `render` is a @staticmethod, so it never receives `self` and there is
    no instance for state to accumulate in. Ruling 33 (3): HAIL is a pure
    function and owns no store.
    """

    @staticmethod
    def render(packet: TruthPacket, mode: Mode = Mode.EXPERT) -> RenderedOutput:
        """Render a resolved packet. Expression verdict FIRST, mode second.

        The order of these four statements is the ruling. Do not reorder them
        to validate `mode` earlier: that would make the silent path read the
        mode, and the whole one-way-authority property rests on it not doing so.
        """
        if not isinstance(packet, TruthPacket):
            raise TypeError(
                f"HAIL.render expects a TruthPacket, got {type(packet).__name__}. "
                "The renderer reads what ORE resolved and reaches nothing else."
            )

        expression = packet.expression_verdict
        if expression in SILENT_VERDICTS:
            return _render_silent(expression)

        if not isinstance(mode, Mode):
            raise TypeError(
                f"HAIL.render expects a Mode, got {type(mode).__name__}. A "
                "verdict is not a mode: verdicts decide WHAT is expressed, "
                "modes only HOW - and a mode can never change the first."
            )
        return _render_spoken(packet, mode)
