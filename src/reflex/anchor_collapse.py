"""
anchor_collapse.py - Anchor Collapse Reflex (ACR) for AUREA

Canon: 2a / 2c - "Anchor Collapse Reflex hard-kills" past ANCHOR_COLLAPSE_DEGREES (25°).
The Compass Stability Engine (src/identity/compass.py) already SOURCES this reflex's
pressure - CSE._register("anchor_collapse", ...) feeds the Grid at the same two
onset points this file reacts to: the 20° escalation cap and the 25° hard-kill line,
both expressed through CSE's own normalized units (min(drift / MAX_DRIFT, 1.0)).

This module holds only the reflex's own reaction (Ruling 2: source vs sole arbiter -
a reflex proposes a response, it does not decide whether it fires against competitors).
It IS registered with ReflexGrid (`_init_core_reflexes`, since Ruling 6 closed on
2026-07-19) - the output lock is the CONSEQUENCE of RACM authorizing this reflex's
suppress, read by aurea_core from evaluate_pressure's returned responses.
"""

from src.reflex.reflex_grid import (
    SymbolicReflex,
    ReflexPriority,
    Scope,
    ReflexTrigger,
    ReflexResponse,
)
from src.identity.compass import ANCHOR_DRIFT_CAP, ANCHOR_COLLAPSE_DEGREES, MAX_DRIFT


class AnchorCollapseReflex(SymbolicReflex):
    """Anchor Collapse Reflex - reacts to compass drift exceeding the canon escalation
    and hard-kill bands (2a/2c). Graduated like ICA (reflex_grid.py): reroute at onset,
    suppress + scar at the hard-kill band, escalating to PSI in both cases for the
    directional realignment only PSI is permitted to perform (see sbsre.py's leash)."""

    def __init__(self):
        super().__init__(
            "ANCHOR_COLLAPSE", "Anchor Collapse Reflex", ReflexPriority.HIGH,
            scope=Scope.LOCAL,
            affected_systems=frozenset({"identity", "doctrine", "output"}),
            # Ruling 10: CSE is the SOLE canonical translator of directional threat -
            # ACR reacts to the compass's anchor_collapse pressure and nothing else.
            # Raw scar_density is GSR's Lexicon domain, not a directional signal;
            # pre-Ruling-10, magnitude spillover let a scar_density@0.5 claim ride
            # ACR's queue into a FALSE anchor-collapse suppress + false forensic
            # message (the false-lock path, CLAUDE.md §8). Closed at the claim.
            trigger_types=frozenset({"anchor_collapse"}),
        )
        # Onset of the canon band, expressed in CSE's own normalized pressure units
        # (min(drift / MAX_DRIFT, 1.0)) - not a raw float, derived from the same
        # canon constants CSE uses so the two never drift apart independently.
        self.threshold = ANCHOR_DRIFT_CAP / MAX_DRIFT
        # Hard-kill band onset, same normalization.
        self.hard_kill_threshold = ANCHOR_COLLAPSE_DEGREES / MAX_DRIFT

    def trigger(self, trigger: ReflexTrigger) -> ReflexResponse:
        """ACR Response: graduate by pressure - reroute + escalate to PSI at onset;
        suppress output, scar, and escalate to PSI for directional realignment at the
        hard-kill band."""
        super().trigger(trigger)

        collapsed = trigger.metadata.get('collapsed')
        drift = trigger.metadata.get('drift', trigger.metadata.get('compass_drift', 0.0))
        cause = f"anchors collapsed: {collapsed}" if collapsed else f"drift {drift:.1f}°"

        if trigger.pressure_level >= self.hard_kill_threshold:
            return ReflexResponse(
                reflex_id=self.id,
                action="suppress",
                target_modules=["output", "identity"],
                output_blocked=True,
                scar_formation=True,
                message=(f"CRITICAL: Anchor Collapse ({cause}) past "
                         f"{ANCHOR_COLLAPSE_DEGREES:.0f}°. Output suppressed. "
                         f"Escalating to PSI for directional realignment."),
                metadata={'escalate_to': 'PSI', 'drift': drift, 'collapsed': collapsed},
            )
        elif trigger.pressure_level >= self.threshold:
            return ReflexResponse(
                reflex_id=self.id,
                action="reroute",
                target_modules=["identity"],
                message=(f"Anchor Collapse onset ({cause}) past "
                         f"{ANCHOR_DRIFT_CAP:.0f}°. Rerouting to PSI for "
                         f"realignment."),
                metadata={'escalate_to': 'PSI', 'drift': drift},
            )
        else:
            return ReflexResponse(
                reflex_id=self.id,
                action="monitor",
                message=f"Anchor drift ({cause}) below onset. Monitoring.",
                metadata={'drift': drift},
            )
