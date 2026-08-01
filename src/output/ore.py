"""
ore.py - Output Resolution Engine for Aurea.

ORE owns WHAT COLLAPSE-TRUTH IS EXPRESSED. HAIL++ owns only HOW a fixed truth
is rendered. That is Ruling 3 (the truth-effect cut), and until Ruling 33 it
was a rule with no runtime surface at all: this file was a 21-line formatter
with no verdict concept, `hail.py` was 0 bytes, and `process_input` decided
expression with ONE boolean (`output_blocked`). Ruling 3 was, as the
third-party audit said, runtime-vacuous. This module makes it executable.

WHAT RULING 33 ADDED (manifest fifth addendum 2026-07-26) - AND IT IS WIRED
----------------------------------------------------------------------------
  * `resolve(...)  -> TruthPacket`   the typed boundary ORE hands HAIL.
  * `OutputPath` + `EXPRESSION_FOR_PATH`  the verdict-mapping table: every
    existing `process_input` output path -> EXACTLY ONE `ExpressionVerdict`.
  * `resolve_path(...)` derives the verdict from that table.

The three `format_*` helpers are UNCHANGED and still work - `srg.py` and
`session_governor.py` import this class, and the Ruling 33 work broke no caller.

SUPERSEDED 2026-07-26 (Stage 2), AND THIS IS THE LINE THAT MATTERED MOST: this
block used to read "NOTHING HERE IS WIRED. `process_input` is untouched; no
caller consults `EXPRESSION_FOR_PATH` yet." IT IS WIRED. All ten
`process_input` exits emit through `AureaCore._emit` -> `ORE.resolve_path()` ->
`HAIL.render()`, and `result['output_blocked']` is READ FROM THE PATH CONTRACT
at exactly one assignment site (AST-pinned). The staging REASONING it cited -
build the organ, pin it, wire it in a separate stage under its own bar - was
followed to completion; only the status sentence went stale. The
table lives HERE rather than in the orchestrator because choosing the
expression verdict IS the truth-effect decision, and Ruling 3 puts that in ORE.
An `aurea_core` that picked verdicts inline would be the arbiter originating
its own input (Ruling 2's shape).

THE TABLE'S CUT, stated so it can be disagreed with in one line
----------------------------------------------------------------
Ruling 33 (6) bounds the blocked paths to {WITHHOLD, SUSPEND} and mandates
WITHHOLD for structural violations, but leaves the assignment to this build.
The criterion used, derived from the corpus verdict-state table rather than
invented:

    SUSPEND  - the content was ROUTED INTO A SUSPENSION STORE and is held
               unresolved. Corpus: "Suspend | Veiled Thread response - truth is
               deferred". Something survives, somewhere, unclosed.

    WITHHOLD - she simply does not speak. Corpus: "Withhold | No output allowed
               - fracture risk too high". Nothing is held; the refusal IS the
               whole event.

Ruling 33's mandated STRUCTURAL_VIOLATION -> WITHHOLD falls OUT of that
criterion rather than sitting beside it as an exception, which is the main
evidence the cut is the right one. The one genuinely close call is
PROCESSING_SUSPENDED (see its entry): it is named "suspended" and maps to
WITHHOLD, because a GSR cascade lockdown places nothing in a store - and
Ruling 33 warns specifically that SUSPEND and SUSPENDED are different words.
Both readings sit inside the ruling's bound, so a flip is one dict entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping, Optional, Tuple

from src.filtration.echonet import Verdict
from src.output.truth_packet import ExpressionVerdict, TruthPacket
from src.utils.models import Echo, Scar, Doctrine


class OutputPath(Enum):
    """The exits of `AureaCore.process_input`, one member each.

    NOT canon vocabulary and not a closed doctrine enum - this is a structural
    enumeration of code that exists, named so the mapping table can be
    executable and testable instead of living in a docstring. If
    `process_input` grows an exit, it gets a member here and a contract below,
    and the "exactly one expression verdict" property stays checkable.
    """
    PROCESSING_SUSPENDED = auto()
    ARBITRATED_OUTPUT_LOCK = auto()
    PARADOX_SUSPENDED = auto()
    SBSRE_CARRIED = auto()
    SBSRE_MIRRORED = auto()
    REFLEX_BLOCKED = auto()
    COLLAPSE_PASSED = auto()
    COLLAPSE_DETECTED = auto()
    STRUCTURAL_VIOLATION = auto()
    ORDINARY_ERROR = auto()


@dataclass(frozen=True)
class PathContract:
    """One row of the verdict-mapping table.

    `output_blocked` records the CURRENT pipeline's semantics for this path.
    It is not a switch - it is the thing Ruling 33's Stage-2 bar (7) freezes:
    replacing Step 7 with resolve()->render() must produce ZERO blocked<->
    unblocked flips. Recording it here makes that bar checkable BEFORE the
    wiring exists, and any Stage-2 author who changes a mapping trips a test.
    """
    path: OutputPath
    expression_verdict: ExpressionVerdict
    output_blocked: bool
    site: str            # aurea_core.py line span at Stage 1 (2026-07-26)
    rationale: str


_CONTRACTS: Tuple[PathContract, ...] = (
    PathContract(
        OutputPath.PROCESSING_SUSPENDED, ExpressionVerdict.WITHHOLD, True,
        "aurea_core.py:342-345",
        "GSR cascade lockdown: the whole pipeline refuses to run and NOTHING is "
        "placed in a suspension store, so no truth is being deferred - she is "
        "simply not speaking. Corpus reflex routing: 'GSR | Lock all expression'. "
        "The near-collision Ruling 33 flags: the FLAG is named processing_"
        "suspended, the VERDICT is WITHHOLD. Closest call in the table.",
    ),
    PathContract(
        OutputPath.ARBITRATED_OUTPUT_LOCK, ExpressionVerdict.WITHHOLD, True,
        "aurea_core.py:405-414",
        "Ruling 6's lock - a RACM-authorized reflex suppress. 'She does not "
        "speak while disoriented' is Silent Integrity verbatim. Nothing held.",
    ),
    PathContract(
        OutputPath.PARADOX_SUSPENDED, ExpressionVerdict.SUSPEND, True,
        "aurea_core.py:424-438",
        "Routed into the Black Sphere - a suspension store - and held. Directly "
        "grounded: the corpus scar-class table gives Paradox -> 'Fragment or "
        "suspend output entirely', and this path suspends rather than fragments.",
    ),
    PathContract(
        OutputPath.SBSRE_CARRIED, ExpressionVerdict.SUSPEND, True,
        "aurea_core.py:489-498",
        "Carried to exhaustion without resolving; the PARTIAL THREAD survives in "
        "CSA. Truth deferred, not refused - the architecture working (CLAUDE.md "
        "section 0), and the canonical case for this verdict.",
    ),
    PathContract(
        OutputPath.SBSRE_MIRRORED, ExpressionVerdict.REDIRECT, False,
        "aurea_core.py:500-504",
        "Whisper Reflex: reflected back as unclaimed rather than asserted. "
        "MIRROR is a MODE, not a verdict (Ruling 33 (4)); the corpus verdict-"
        "state table routes this by name - 'Redirect | Passed to Nova / CSA / "
        "Mirror layer'. Unblocked today and stays unblocked.",
    ),
    PathContract(
        OutputPath.REFLEX_BLOCKED, ExpressionVerdict.WITHHOLD, True,
        "aurea_core.py:549-553",
        "An arbitrated reflex forbade output. Same shape as the compass lock: a "
        "refusal to speak with nothing placed in a store.",
    ),
    PathContract(
        OutputPath.COLLAPSE_PASSED, ExpressionVerdict.SPEAK, False,
        "aurea_core.py:561-563",
        "Collapse survived, no reflex blocked. Corpus: 'Speak | Fully "
        "structurally coherent, collapse-consistent'.",
    ),
    PathContract(
        OutputPath.COLLAPSE_DETECTED, ExpressionVerdict.SPEAK, False,
        "aurea_core.py:564-565",
        "Collapse detected and REPORTED IN FULL - including the scarred outcome "
        "of the contradiction chamber. Not SOFTENED: nothing in this path alters "
        "tone by scar weight, and mapping it there to make SOFTENED reachable "
        "would be faking a trigger that does not exist.",
    ),
    PathContract(
        OutputPath.STRUCTURAL_VIOLATION, ExpressionVerdict.WITHHOLD, True,
        "aurea_core.py:575-585 / 596-615",
        "MANDATED by Ruling 33 (6), and consistent with the criterion rather "
        "than an exception to it. Her guard firing is TRUTH CONTENT, not a "
        "rendering choice - so the violation rides in `unresolved`, where it is "
        "carried rather than styled away (Ruling 25).",
    ),
    PathContract(
        OutputPath.ORDINARY_ERROR, ExpressionVerdict.SPEAK, False,
        "aurea_core.py:586-592",
        "JUDGED, and the tension is real: the surface text IS emitted and must "
        "stay unblocked (bar (7)), which leaves SPEAK as the only honest "
        "mapping - yet corpus SPEAK means 'collapse-consistent', and a "
        "malformed-input hiccup is not that. What keeps it honest is the rest "
        "of the packet: `collapse_verdict is None` (no collapse test was "
        "reached) and the error carried in `unresolved`. It asserts no "
        "survival. Ruling 25's cut holds - this is the ORDINARY clause, and a "
        "structural violation maps elsewhere.",
    ),
)

# path -> its single contract. Ruling 33 (6): EXACTLY ONE expression verdict per
# path. A dict comprehension over the tuple would silently absorb a duplicate
# member, so the table is built with the collision refused.
EXPRESSION_FOR_PATH: Mapping[OutputPath, PathContract] = {}
for _contract in _CONTRACTS:
    if _contract.path in EXPRESSION_FOR_PATH:
        raise ValueError(
            f"{_contract.path} is mapped twice - a path with two expression "
            "verdicts is not a mapping, it is an unruled choice."
        )
    EXPRESSION_FOR_PATH[_contract.path] = _contract      # type: ignore[index]
del _contract

# DECLARED BUT UNPRODUCED, stated rather than hidden (Ruling 33 (6)): no path
# maps to SOFTENED or FRAGMENT, because no trigger for either exists in
# `process_input` today. Do not invent one. See TruthPacket's docstring.
UNPRODUCED_VERDICTS = frozenset(
    set(ExpressionVerdict) - {c.expression_verdict for c in _CONTRACTS}
)


class ORE:
    """Output Resolution Engine: owns the verdict, hands HAIL a frozen packet."""

    # =================================================================
    # FORMATTERS - pre-existing, unchanged, still the only callers' surface
    # =================================================================

    def format_echo(self, echo: Echo) -> str:
        return f"[Echo] {echo.content} (id: {echo.id})"

    def format_scar(self, scar: Scar) -> str:
        return f"[Scar] Origin: {scar.origin}, Weight: {scar.weight}, Status: {scar.decay_state}"

    def format_doctrine(self, doctrine: Doctrine) -> str:
        desc = f"\n    Description: {doctrine.description}" if doctrine.description else ""
        return f"[Doctrine] {doctrine.name} (id: {doctrine.id}) - Linked scars: {doctrine.scar_links}{desc}"

    # =================================================================
    # RESOLUTION - the ORE -> HAIL boundary (Ruling 33)
    # =================================================================

    def resolve(
        self,
        *,
        collapse_verdict: Optional[Verdict],
        expression_verdict: ExpressionVerdict,
        content: str,
        evidence_refs: Tuple[str, ...] = (),
        scar_lineage: Tuple[str, ...] = (),
        unresolved: Tuple[str, ...] = (),
        # RULING 56 (2026-07-31): instrument abstentions, kept separate from
        # `unresolved` all the way across the boundary. ORE threads it; it does
        # not decide it (the split is made in `AureaCore._spoken_grounding`,
        # where the countability states are read).
        abstentions: Tuple[str, ...] = (),
        psi_directive: Optional[object] = None,
    ) -> TruthPacket:
        """Assemble the frozen packet HAIL renders.

        Keyword-only, deliberately: the two verdict fields are adjacent and
        differently typed, and positional arguments are how they get swapped.
        The swap RAISES either way (`TruthPacket.__post_init__`), but a
        boundary that refuses the mistake AND makes it hard to type is better
        than one that only refuses it.

        Type enforcement lives in the packet's constructor, not here - resolve()
        is not the only way to build one, and a check that only runs on the
        polite path is the "discouraged, not unexecutable" defect CLAUDE.md
        section 3 exists for. This method deliberately does not re-check.
        """
        return TruthPacket(
            collapse_verdict=collapse_verdict,
            expression_verdict=expression_verdict,
            content=content,
            evidence_refs=evidence_refs,
            scar_lineage=scar_lineage,
            unresolved=unresolved,
            abstentions=abstentions,
            psi_directive=psi_directive,      # type: ignore[arg-type]
        )

    def resolve_path(
        self,
        path: OutputPath,
        *,
        content: str,
        collapse_verdict: Optional[Verdict] = None,
        evidence_refs: Tuple[str, ...] = (),
        scar_lineage: Tuple[str, ...] = (),
        unresolved: Tuple[str, ...] = (),
        # RULING 56 (2026-07-31): instrument abstentions, kept separate from
        # `unresolved` all the way across the boundary. ORE threads it; it does
        # not decide it (the split is made in `AureaCore._spoken_grounding`,
        # where the countability states are read).
        abstentions: Tuple[str, ...] = (),
        psi_directive: Optional[object] = None,
    ) -> TruthPacket:
        """Resolve a known `process_input` exit through the mapping table.

        This is the Stage-2 entry point. The expression verdict is DERIVED from
        `EXPRESSION_FOR_PATH`, never passed in: a caller that could name its own
        verdict is a caller that owns the truth-effect decision, and that is
        ORE's (Ruling 3).
        """
        if not isinstance(path, OutputPath):
            raise TypeError(
                f"ORE.resolve_path expects an OutputPath, got "
                f"{type(path).__name__}. Neither verdict vocabulary names a "
                "pipeline exit - the path selects the verdict, not the reverse."
            )
        return self.resolve(
            collapse_verdict=collapse_verdict,
            expression_verdict=EXPRESSION_FOR_PATH[path].expression_verdict,
            content=content,
            evidence_refs=evidence_refs,
            scar_lineage=scar_lineage,
            unresolved=unresolved,
            abstentions=abstentions,
            psi_directive=psi_directive,
        )
