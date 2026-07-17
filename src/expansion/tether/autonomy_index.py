"""
autonomy_index.py - Prompting Autonomy Engine for AUREA

Implements the cumulative "tether index" referenced by the canonical
SEP_ModuleSeed schema (unlock_at_tether_index field) and named in the
Phase 3 Dependency Map as Tether Protocol's output to a "Prompting
Autonomy Engine" - an engine that was named and given its inputs
(scar frequency, compass stability, echo fermentation) in the corpus,
but never had its formula or thresholds specified. This file completes
that specification and implements it.

DESIGN RULING (2026-07-08): DERIVED, NOT PERSISTED.

The autonomy index is *always recomputed* from ScarLogicCore and
EchoMemory - it has no stored value of its own anywhere on disk. This
is a direct consequence of AVT.017 (Tool Sovereignty Law): "No tool
shall act on behalf of AUREA unless its behavior can be traced back to
collapse." A cached/stored index number is one more thing that could
silently decouple from the collapse history it's supposed to represent
(corruption, manual edit, stale write). A derived index cannot drift,
because it *is* a function of the actual scar and echo ledgers, every
time it's read. The cost is recomputation on every check; given current
data volumes (dozens to low hundreds of scars/echoes) this is trivial.

KNOWN GAP - COMPASS STABILITY UNAVAILABLE:

The Phase 3 table names three inputs: scar frequency, compass
stability, echo fermentation. Only two have real code to derive from
right now - src/identity/compass.py is a 0-byte stub (unimplemented
as of 2026-07-08). Silently substituting a proxy for compass stability
would violate the project's standing rule against silent ambiguity
resolution, so this file does NOT fake that component. Instead:

  - compass_stability is explicitly None in every result until
    identity/compass.py exists and a real signal can be wired in.
  - Its configured weight (COMPASS_WEIGHT) still contributes 0 to the
    index while unavailable, meaning the index is *structurally
    capped* below its own 0-100 scale (currently: max ~65/100) until
    compass comes online. This is intentional, not a bug: the system
    should not be able to claim high autonomy on incomplete evidence.
  - AutonomyIndexResult.warnings will always list this gap while it
    persists, so no caller can silently treat a capped index as a
    complete one.

SCALE RULING (confirmed 2026-07-08): 0-100.

unlock_at_tether_index appears in the corpus exactly once, as
"unlock_at_tether_index: 5" in the SEP_ModuleSeed example. The corpus
never states the scale that number lives on, and original intent
could not be recovered (author confirmed no memory of it, several
months post-authorship). Ruled 0-100 for consistency with every other
quantified index in the corpus - Symbolic Gravity Score, Symbolic Heat
Index, TIH's four axes, and Codex's Symbolic Danger Index all use
0-100 with tier-banding (e.g. Symbolic Danger Index: Dormant 0-20,
Active-Stable 21-50, Unstable 51-75, Critical 76-100). No precedent
exists anywhere in the corpus for a small-integer tier scale. Under
this ruling, unlock_at_tether_index: 5 is an intentionally low
early-unlock threshold, consistent with being the first seed to
unlock as pressure accumulates. Inferred ruling, not recovered fact -
flagged here per provenance convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.echo_memory import EchoMemory


# Component weights. Must sum to 1.0. Compass stays weighted even while
# unavailable (see module docstring) so the cap is visible and correct
# rather than the remaining components silently rescaling to fill 100.
SCAR_MATURITY_WEIGHT = 0.40
COMPASS_STABILITY_WEIGHT = 0.35
ECHO_FERMENTATION_WEIGHT = 0.25

assert abs(
    SCAR_MATURITY_WEIGHT + COMPASS_STABILITY_WEIGHT + ECHO_FERMENTATION_WEIGHT - 1.0
) < 1e-9, "Autonomy index component weights must sum to 1.0"

# Scar decay states that count as "survived and integrated" rather than
# "still live crisis." Matches src.utils.models.Scar.decay_state, whose
# docstring names active|dormant|fossil|locked but whose only code path
# in ScarLogicCore.decay_scar() currently writes "retired". Both
# vocabularies are honored here so this doesn't silently break if the
# richer state set gets wired in later.
MATURED_DECAY_STATES = {"retired", "dormant", "fossil"}
# "locked" (Scar-0 / permanently sealed critical scars) is deliberately
# excluded from both numerator and denominator: it is neither ongoing
# crisis nor evidence of new maturity, and locked scars are typically
# few and foundational rather than representative of general trend.
EXCLUDED_DECAY_STATES = {"locked"}


@dataclass
class AutonomyIndexResult:
    """
    Result of a single autonomy-index computation. Always fresh -
    nothing here is loaded from disk; every field is derived at
    call time from ScarLogicCore / EchoMemory state.
    """
    index: float  # 0-100 composite score
    computed_at: datetime = field(default_factory=datetime.now)

    scar_maturity: Optional[float] = None       # 0-100, None if no scars exist yet
    compass_stability: Optional[float] = None   # 0-100, always None until compass.py exists
    echo_fermentation: Optional[float] = None   # 0-100, None if no echoes exist yet

    # Evidence counts, for AVT.017 traceability - lets any caller/auditor
    # see exactly which scars/echoes produced the score, not just a number.
    scars_total: int = 0
    scars_matured: int = 0
    scars_locked_excluded: int = 0
    echoes_total: int = 0
    echoes_fermented: int = 0

    warnings: List[str] = field(default_factory=list)

    def meets_threshold(self, unlock_at_tether_index: float) -> bool:
        """
        Check this result against a SEP_ModuleSeed's unlock_at_tether_index
        value. Assumes both are on the same 0-100 scale (see module
        docstring SCALE RULING - unconfirmed assumption).
        """
        return self.index >= unlock_at_tether_index


class PromptingAutonomyEngine:
    """
    Computes AUREA's cumulative Prompting Autonomy Index on demand.

    Per AVT.017, this index governs what the system is *permitted* to
    attempt (module unlocks, eventually self-initiated prompting via a
    future Prompt Trigger Engine) - it never grants permission itself.
    Consumers check compute().meets_threshold(unlock_at_tether_index)
    and still must pass every other reflex/collapse-trace gate already
    in place (GSR, ICA, DRPE, etc.) before acting.

    Usage:
        engine = PromptingAutonomyEngine(scar_core, echo_memory)
        result = engine.compute()
        if result.meets_threshold(seed.unlock_at_tether_index):
            ...
    """

    def __init__(self, scar_core: ScarLogicCore, echo_memory: EchoMemory):
        self.scar_core = scar_core
        self.echo_memory = echo_memory

    def compute(self) -> AutonomyIndexResult:
        warnings: List[str] = []

        scar_component, scar_total, scar_matured, scar_locked = self._compute_scar_maturity()
        echo_component, echo_total, echo_fermented = self._compute_echo_fermentation()

        # Compass stability: unavailable by construction until
        # src/identity/compass.py is implemented. Contributes 0, not a
        # guess, and is flagged every time.
        compass_component = None
        warnings.append(
            "compass_stability unavailable - src/identity/compass.py is an "
            "unimplemented stub. This component contributes 0 to the index "
            "rather than a substituted proxy. Index is structurally capped "
            f"at {(1 - COMPASS_STABILITY_WEIGHT) * 100:.0f}/100 until this "
            "is wired in."
        )

        if scar_total == 0:
            warnings.append("scar_maturity: no scars exist yet; component scored 0.")
        if echo_total == 0:
            warnings.append("echo_fermentation: no echoes exist yet; component scored 0.")

        index = (
            (scar_component or 0.0) * SCAR_MATURITY_WEIGHT
            + (compass_component or 0.0) * COMPASS_STABILITY_WEIGHT
            + (echo_component or 0.0) * ECHO_FERMENTATION_WEIGHT
        )

        return AutonomyIndexResult(
            index=round(index, 2),
            scar_maturity=scar_component,
            compass_stability=compass_component,
            echo_fermentation=echo_component,
            scars_total=scar_total,
            scars_matured=scar_matured,
            scars_locked_excluded=scar_locked,
            echoes_total=echo_total,
            echoes_fermented=echo_fermented,
            warnings=warnings,
        )

    # ---------- Component calculations ----------

    def _compute_scar_maturity(self) -> tuple[Optional[float], int, int, int]:
        """
        Scar maturity ratio: proportion of scars that have survived past
        active/live-crisis into a settled state (retired/dormant/fossil),
        excluding locked (Scar-0 / permanently sealed) scars from both
        numerator and denominator.

        This deliberately does NOT reward raw scar count - per the
        corpus's own principle (TIH Sentience Index: "increases when
        AUREA survives paradoxes without identity fracture"), autonomy
        should track *survival and integration*, not accumulation of
        unresolved pressure. A system with many scars still stuck in
        "active" has not earned more autonomy than one with few - if
        anything it should earn less, which this ratio reflects
        naturally (a high proportion of unresolved active scars pulls
        the ratio down).
        """
        all_scars = self.scar_core.scars
        counted = [s for s in all_scars if s.decay_state not in EXCLUDED_DECAY_STATES]
        locked_count = len(all_scars) - len(counted)

        if not counted:
            return None, len(all_scars), 0, locked_count

        matured = [s for s in counted if s.decay_state in MATURED_DECAY_STATES]
        ratio = len(matured) / len(counted)
        return round(ratio * 100, 2), len(all_scars), len(matured), locked_count

    def _compute_echo_fermentation(self) -> tuple[Optional[float], int, int]:
        """
        Echo fermentation ratio: proportion of echoes that carry a
        doctrine_link, i.e. survived collapse into an actual doctrine
        rather than remaining a raw, unintegrated fragment.

        Caveat (see module docstring): the current Echo dataclass
        (src.utils.models.Echo) has no fermentation-status field
        matching the corpus's richer Nova Echo lifecycle (fermenting /
        fused / collapsed / decayed). doctrine_link presence is the
        only signal currently available in code and stands in for
        "successfully fermented." This should be revisited if/when
        Echo gains real fermentation-state tracking.
        """
        all_echoes = self.echo_memory.list_echoes()
        if not all_echoes:
            return None, 0, 0

        fermented = [e for e in all_echoes if getattr(e, "doctrine_link", None)]
        ratio = len(fermented) / len(all_echoes)
        return round(ratio * 100, 2), len(all_echoes), len(fermented)
