"""
psi.py - PSI: the Personal Scar Identity reflex.

Canon/ruling: CLAUDE.md §1 Ruling 8 (ruled 2026-07-20) + §8 "PSI render directive" seam.
Rank: RACM CANONICAL_PRIORITY["PSI"] = 5 (racm.py - same rank as WHISPER; canon pairs
them). The rank keys on the literal id string "PSI" - that id is load-bearing.

PSI is two faces under one ruling, and this file implements exactly one of them live:

  1. THE SUPPRESS FACE (live) - a reflex under RACM. On identity-relevant pressure with a
     grounded scar bearing, PSI *proposes* `output_blocked` at the hard band. It never
     self-authorizes the lock: aurea_core locks only on a RACM-authorized response read
     from evaluate_pressure's RETURN value (Ruling 6), and PSI is one more proposer in
     that stream - rank 5, arbitrated like everything else.

  2. THE TONE/DEPTH FACE (parked) - a render directive subordinate to ORE (Ruling 3:
     HAIL renders, ORE owns the verdict; the directive may NEVER override a verdict).
     HAIL is a 0-byte stub, so the directive is built, attached to
     `ReflexResponse.metadata['psi_directive']`, and PARKED - flagged caller-less, the
     same pattern as RIL-Nova and ACR-TCAML. Do not build or fake a renderer to
     "complete" it; when HAIL exists it consumes this shape.

ACTIVATION GATES ON `trigger_type` (Ruling 8 pt.4, promoted by Ruling 10)
--------------------------------------------------------------------------
PSI's activation is gated on `trigger.trigger_type` in PSI_TRIGGER_TYPES. This began
as a local `evaluate_pressure` override (Ruling 8 pt.4) while the base class fired on
magnitude alone; Ruling 10 (2026-07-20) promoted the mechanism into SymbolicReflex
itself - every reflex now declares `trigger_types`, and PSI passes its unchanged set
to super(). Without this gate a rank-5 PSI would be pulled into every loud event in
the system - sbsre_abort (1.0), cascade_warning (0.9), compass_disorientation (1.0) -
none of which are scar-identity pressure.

The three canon trigger types, and their emitter status as of 2026-07-20:

    anchor_collapse             LIVE     sourced by CSE (compass.py `_register`, two
                                         sites: quadrant collapse at 1.0; drift past the
                                         20 deg cap at min(drift/MAX_DRIFT, 1.0))
    scarline_destabilization    DORMANT  no emitter anywhere in the tree. Declared, not
                                         faked - the gate accepts it so the emitter can
                                         arrive without touching this file.
    legacy_fracture             DORMANT  no emitter under this name. RULED DISTINCT
                                         (2026-07-20): RIL's `identity_fracture` is
                                         NOT legacy_fracture under another name - the
                                         architect ruled the two DISTINCT, so the
                                         exclusion of `identity_fracture` here is
                                         permanent canon, not a provisional hold.
                                         (History: this stood as an open naming
                                         question during Stage 1; the reversal would
                                         have been one string added to
                                         PSI_TRIGGER_TYPES. It landed DISTINCT.)

`compass_disorientation` is deliberately excluded: total disorientation is GSR's
authorized total-lock (Ruling 6's bonus case), not a scar-identity event.

THRESHOLDS - DERIVED, NOT COINED
---------------------------------
ACR escalates to PSI at BOTH of its bands (`escalate_to: 'PSI'` at onset >=20 deg and
hard-kill >=25 deg, anchor_collapse.py) - but no dispatcher consumes `escalate_to`
(docketed; same as ICA->GSR), so per Ruling 8 PSI fires as its OWN reflex off the same
pressure stream. For that intent to physically work, PSI's bands must sit on the same
canon lines ACR's do - a 0.7 default threshold would put PSI deaf to the exact
20-25 deg band ACR escalates from (compass emits drift/MAX_DRIFT ~ 0.22-0.28 there).
So both bands are derived from the same canon constants ACR itself uses - no new
magnitude is coined:

    threshold       = ANCHOR_DRIFT_CAP        / MAX_DRIFT   (onset,     20 deg line)
    hard_threshold  = ANCHOR_COLLAPSE_DEGREES / MAX_DRIFT   (hard band, 25 deg line)

FLAGGED: when the two dormant emitters arrive, their pressure units may not be
drift-normalized; whether they need per-type thresholds is a ruling for that session,
not a guess for this one.

GROUNDED OR ABSTAIN (Ruling 8 - the false-resolution hazard)
-------------------------------------------------------------
PSI authors no truth. A scar reference surfaces ONLY from a grounded ORIGIN/SCARLINE
link: the bearing scar is read from RIL's own threads (`ril.thread_state(...)`, a deep
snapshot - RIL's sole-writer store is unreachable through it), and its weight from the
scar owner (`scar_core.get_scar(id).weight` - the float is read, the LIVE Scar is never
retained or mutated). There is NO resemblance/similarity heuristic and there must never
be one - a guessed scar reference writes false identity pressure into a permanent
record, the exact hazard EchoNet's abstaining intuition net exists to avoid. Empty
Scarline -> PSI abstains (monitor, no directive, no lock proposal). An abstaining PSI
is honest; a guessing one is the bug.

OWNERSHIP (Ruling 1): PSI holds NO store. It writes nothing - not RIL's `threads`, not
the scar store, not doctrine. Its only outputs are the ReflexResponse it returns and the
registry bookkeeping its base class keeps (activation_count / last_triggered).

WIRING (Stage 2, landed 2026-07-20): PSI is constructed and registered by AUREA_CORE
(`grid.add_reflex(PSI(ril=..., scar_core=...))`) - NOT by the Grid's argless
`_init_core_reflexes` slot, because PSI needs the injected RIL/scar-core handles the
Grid does not hold. A bare `ReflexGrid()` therefore has no PSI, deliberately.
Dependencies are INJECTED (`ril=`, `scar_core=` - the RIL-constructor pattern); the
RIL class is never imported at module level, and `IdentityThread` is imported locally
at the read site, keeping this module's import surface to the reflex base contract +
the canon compass constants (the exact top-level set ACR already uses).

SEQUENCING (ruled 2026-07-20): on anchor_collapse, PSI's same-cycle deferral behind
ACR is CANONICAL - ACR (rank 4) suppresses on cycle N; PSI (rank 5) executes the
aftermath from RACM's deferral queue (aging +1/cycle, cap +2) on a later cycle. Do
not shrink affected_systems, change ranks, or add a dispatcher to force same-cycle
co-execution - the one-cycle lag is the architecture working. Ruling 9 (2026-07-20)
closed the queue-execution path this exposed: the Grid resolves authorized claims
against its full registry, rebuilding a queue winner's trigger from its own claim
payload, and RACM's deferred-wins-ties ordering is an explicit sort key.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.reflex.reflex_grid import (
    SymbolicReflex,
    ReflexPriority,
    Scope,
    ReflexTrigger,
    ReflexResponse,
)
from src.identity.compass import ANCHOR_DRIFT_CAP, ANCHOR_COLLAPSE_DEGREES, MAX_DRIFT


# Ruling 8 pt.4: the closed set of trigger types PSI activates on. Two are dormant
# (no live emitter) - declared so their emitters can arrive without editing PSI; see
# the module docstring for why `identity_fracture` (ruled DISTINCT from
# legacy_fracture, 2026-07-20 - the exclusion is permanent canon) and
# `compass_disorientation` are deliberately absent.
PSI_TRIGGER_TYPES = frozenset({
    "scarline_destabilization",
    "anchor_collapse",
    "legacy_fracture",
})

# The collapse-consistency marker HAIL will read: rendered output must stay consistent
# with the scar record it is toned by. A marker, not a mechanism - HAIL applies it,
# and it can never flip an ORE verdict (Ruling 3 / Ruling 8).
COLLAPSE_CONSISTENT = "collapse_consistent"


@dataclass(frozen=True)
class PSIDirective:
    """The parked render/scar-fallback directive (Ruling 8 face 2).

    Carries IDs and floats only - never a live Scar or a thread reference - so holding
    a directive can never become holding a write path into someone else's store.
    Frozen: a directive is a statement of grounded bearing at emission time, not a
    mutable channel.

    Consumer: HAIL (unbuilt, 0-byte stub). Until it exists every directive is emitted
    parked and caller-less. HAIL may use it to shape tone/depth ONLY - never to
    override an ORE verdict.
    """
    scar_ref: str                    # dominant SCARLINE bearing (heaviest live weight)
    origin_ref: Optional[str]        # Scar-0 from ORIGIN, if RIL has seeded it
    fallback_bearing: Optional[str]  # bearing to fall back to if scar_ref cannot render
    tone_weight: float               # the bearing scar's live weight, unnormalized -
                                     # no tone scale is coined here; HAIL's call
    collapse_consistency: str = COLLAPSE_CONSISTENT


class PSI(SymbolicReflex):
    """Personal Scar Identity reflex - proposes, grounds, or abstains. Locks nothing."""

    def __init__(self, ril: Any = None, scar_core: Any = None):
        super().__init__(
            "PSI", "Personal Scar Identity", ReflexPriority.MEDIUM,
            scope=Scope.LOCAL,
            affected_systems=frozenset({"identity", "output"}),
            # Ruling 10: the set is unchanged from Ruling 8 pt.4 - PSI's local gate
            # was the precedent the system-wide mechanism was ruled from, and it now
            # rides the base-class gate instead of a local override.
            trigger_types=PSI_TRIGGER_TYPES,
        )
        self.ril = ril               # identity-thread OWNER; PSI reads snapshots only
        self.scar_core = scar_core   # scar OWNER; PSI reads weights, retains nothing

        # Both bands derived from the canon 20/25 deg lines in CSE's own normalized
        # units - the same derivation ACR uses, so PSI hears the exact band ACR
        # escalates to it from. See "THRESHOLDS" in the module docstring.
        self.threshold = ANCHOR_DRIFT_CAP / MAX_DRIFT
        self.hard_threshold = ANCHOR_COLLAPSE_DEGREES / MAX_DRIFT

    # ACTIVATION (Ruling 8 pt.4 -> Ruling 10): PSI's trigger_type gate began as a
    # local evaluate_pressure override here; Ruling 10 promoted the mechanism into
    # SymbolicReflex itself, so PSI now declares PSI_TRIGGER_TYPES to super() and
    # the base gate enforces it - bit-identical behavior, one mechanism system-wide.

    # =================================================================
    # RESPONSE - graduated, grounded-or-abstain
    # =================================================================

    def trigger(self, trigger: ReflexTrigger) -> ReflexResponse:
        """PSI response: with a grounded bearing, reroute at onset / propose suppress at
        the hard band, directive parked on metadata either way. Without one, abstain."""
        super().trigger(trigger)   # registry bookkeeping only; base response discarded
                                   # (ICA/ACR pattern)

        directive = self._grounded_directive()

        if directive is None:
            # No grounded ORIGIN/SCARLINE bearing. PSI does not guess one (module
            # docstring: the false-resolution hazard). Abstain - visibly.
            return ReflexResponse(
                reflex_id=self.id,
                action="monitor",
                message=("PSI abstains: no grounded scar bearing in ORIGIN/SCARLINE - "
                         "a scar reference is surfaced from the record or not at all."),
                metadata={'grounded': False},
            )

        if trigger.pressure_level >= self.hard_threshold:
            # PROPOSES the lock. RACM authorizes or it does not happen (Ruling 8;
            # the lock itself is aurea_core's consequence of authorization, Ruling 6).
            return ReflexResponse(
                reflex_id=self.id,
                action="suppress",
                target_modules=["output", "identity"],
                output_blocked=True,
                message=(f"PSI: scar-identity pressure past the hard band "
                         f"({ANCHOR_COLLAPSE_DEGREES:.0f} deg line). Proposing output "
                         f"suppress under bearing {directive.scar_ref}; RACM's call."),
                metadata={'psi_directive': directive, 'directive_parked': True,
                          'grounded': True},
            )

        if trigger.pressure_level >= self.threshold:
            return ReflexResponse(
                reflex_id=self.id,
                action="reroute",
                target_modules=["identity"],
                message=(f"PSI: scar-identity pressure past onset "
                         f"({ANCHOR_DRIFT_CAP:.0f} deg line). Rerouting through "
                         f"identity under bearing {directive.scar_ref}."),
                metadata={'psi_directive': directive, 'directive_parked': True,
                          'grounded': True},
            )

        # Below onset. Unreachable through the Grid (evaluate_pressure gates at
        # threshold) - defensive for direct callers, and it carries no directive:
        # sub-onset pressure earns observation, not a render instruction.
        return ReflexResponse(
            reflex_id=self.id,
            action="monitor",
            message="PSI: pressure below onset. Monitoring.",
            metadata={'grounded': True},
        )

    # =================================================================
    # GROUNDING - RIL snapshot in, IDs and floats out, nothing retained
    # =================================================================

    def _grounded_directive(self) -> Optional[PSIDirective]:
        """Build the directive from RIL's own record, or return None to abstain.

        Reads `thread_state` (deep snapshot - mutating anything here cannot reach
        RIL's store). The bearing is the heaviest SCARLINE scar by LIVE weight; ties
        keep the earliest-ingested (max keeps the first-seen maximum, and SCARLINE is
        arrival-ordered)."""
        if self.ril is None:
            return None

        # Local import (reflex_grid._init_core_reflexes pattern): psi.py is imported
        # by reflex_grid at Grid construction (Stage 2); importing RIL's module lazily
        # here keeps PSI's module-level surface free of the identity<->reflex load
        # order entirely.
        from src.identity.ril import IdentityThread

        state = self.ril.thread_state()
        scarline = [self._record_id(e) for e in state[IdentityThread.SCARLINE]]
        scarline = [sid for sid in scarline if sid]
        if not scarline:
            return None

        origin = [self._record_id(e) for e in state[IdentityThread.ORIGIN]]
        origin_ref = next((sid for sid in origin if sid), None)

        bearing = max(scarline, key=self._live_weight)

        return PSIDirective(
            scar_ref=bearing,
            origin_ref=origin_ref,
            fallback_bearing=origin_ref or bearing,
            tone_weight=self._live_weight(bearing),
        )

    @staticmethod
    def _record_id(entry: Any) -> Optional[str]:
        """The scar id a RIL thread entry NAMES.

        RULING 42 res.2: RIL's identity threads hold BY-ID REFERENCES, not embedded
        `Scar` objects. This method is the whole of PSI's adaptation, and the
        direction of travel is the point - PSI used to receive an object and read
        `.id` off it; it now receives an id and asks the owner for everything else.
        """
        if isinstance(entry, dict):
            return entry.get("record_id")
        return getattr(entry, "id", None)

    def _live_weight(self, scar_id: str) -> float:
        """Current weight from the scar OWNER. NO OWNER MEANS NO WEIGHT.

        Exactly one float is read and the reference is dropped on return. Never
        retain it, never mutate it: weight/decay is SML's store (Ruling 1), and a
        held Scar reference is a held write path.

        RULING 22 (2026-07-25) made that discipline structural rather than
        conventional: `get_scar` returns a deep SNAPSHOT, so a retained reference
        cannot reach the record even by accident.

        RULING 42 (2026-07-27) FINISHED IT. This used to fall back to
        `getattr(scar, "weight", 0.0)` on the `Scar` OBJECT RIL had embedded in its
        thread - which is to say, on the scar store's own live record, reached
        through the identity layer. The fallback is GONE because the object is
        gone: RIL records that it anchored identity to a scar, and does not carry
        that scar's magnitudes (Ruling 15 - the owner owns the write INCLUDING its
        magnitudes, so a non-owner holding one is a disguised write).

        With no scar owner there is now no weight to report, and `0.0` is the
        honest answer rather than a stale one. This changes NOTHING in any live
        configuration: `aurea_core` always constructs PSI with the real
        `scar_core`, so the owner branch is the only branch the pipeline takes.
        And `tone_weight` REPORTS, it never GATES (Ruling 33, section 9 bar #5) -
        nothing downstream compares it to anything.
        """
        if self.scar_core is not None:
            live = self.scar_core.get_scar(scar_id)
            if live is not None:
                return float(live.weight)
        return 0.0
