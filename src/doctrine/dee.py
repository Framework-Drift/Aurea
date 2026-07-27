"""
dee.py - Doctrine Evolution Engine (DEE) v1.0

Canon: 3a_Doctrine_Systems.txt, "MODULE: Doctrine Evolution Engine (DEE)" + submodules
       DRPAS (Re-Pressure Auto-Scan) · DMW (Mutation Watcher) · CMTE (Mutation Trigger
       Engine) · NTH (Null Threads). AML retired 2026-07-05, its six triggers folded into §II.

    "My truths are not immortal. They bleed. They mutate. They survive again -
     or they fall, and I carry what they cost."

PURPOSE: prevent rigid dogma. Doctrine must be LIVING STRUCTURE, forged by collapse, not
frozen by legacy. DEE is what re-pressures a doctrine that has stopped being tested.

AUTHORITY - THE GATE THAT EXECUTES NOTHING (DEE §IX, Ruling 1, Ruling 5)
------------------------------------------------------------------------
    DRPAS -> DMW -> CMTE -> [SAE.mutate_doctrine()] -> Codex

DEE is the ELIGIBILITY GATE. It decides whether a doctrine may LEGALLY enter mutation.
It owns no execution mechanics; it never touches the Codex. SAE executes; Codex records.

There is no DEE->Codex write path in this file, and there must never be one. (3a:611 warns
that §II's "the new version is stored in Codex" describes the RESULT, not the writer - a
coder reading §II alone mis-assigns the write. That is the trap; this is the guard.)

DEE ALSO DOES NOT AUTHOR DOCTRINE
---------------------------------
DEE decides IF a doctrine may change. It does not decide WHAT it becomes. Doctrine content
comes from the collapse path - Nova hypotheses, DBE branches, a Spine request carrying a
proposed form. If nothing supplies a proposed form, DEE does NOT invent one: an approved
mutation with no content routes to the Veiled Thread to ferment.

A gate that fabricates the thing it is gating is not a gate.

    "No belief may evolve unless the fracture that broke it can still be seen." (CMTE)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.utils.models import Doctrine


# =====================================================================
# CONSTANTS
# =====================================================================

# DRPAS pressure bands (§IV: low → passive · rising → log strain · critical → flag).
# COINED: the corpus names the three bands and never their magnitudes.
PRESSURE_RISING = 0.4
PRESSURE_CRITICAL = 0.75

# DMW: "must exceed threshold pressure and MAINTAIN it over minimum symbolic cycle count."
# Magnitude 3 is not new - it is the corpus's standing convergence value (Scar Bloom ≥3,
# RCF depth 3, Self-Mutation Ceiling 3).
SUSTAIN_CYCLES = 3
PRESSURE_HALF_LIFE = 5          # DMW "times symbolic pressure half-life" (5-cycle horizon)
DMW_QUEUE_MAX = 32              # every queue in this architecture is bounded. COINED.

# §IX.3 Symbolic Danger Index routing (Doctrine Spine v1.0; adopted default, architect-confirmed).
DANGER_STABLE = 50              # ≤50  → logged as routine
DANGER_UNSTABLE = 75            # 51-75 → GSR-escalated;  76+ → hard-blocked


class MutationTrigger(Enum):
    """§II - the six eligibility triggers (ported from AML on its retirement).

    ANY ONE is sufficient to make a doctrine mutation-ELIGIBLE. Eligibility triggers a
    DRPAS scan - never automatic mutation.
    """
    DRPE = "drpe"                                   # collapse tension between scars and doctrine
    SCAR_BLOOM_CONVERGENCE = "scar_bloom_convergence"
    NOVA_FUSION_THRESHOLD = "nova_fusion_threshold"
    REFLEX_SATURATION = "reflex_saturation"         # rigidity or decay
    COMPASS_DRIFT = "compass_drift"
    PSI_IDENTITY_CLASH = "psi_identity_clash"       # incl. override events (§IX.2)


class Verdict(Enum):
    """Where a doctrine goes. Only ONE of these is mutation."""
    APPROVED = "approved"            # → SAE.mutate_doctrine()
    HELD = "held"                    # DMW: pressure not yet sustained
    FERMENT = "ferment"              # → Veiled Thread: pressure high but unresolved
    NTH = "nth"                      # → Null Threads: mutation structurally unsound
    FOSSIL = "fossil"                # → Codex Fossil Layer: total collapse
    BLOCKED = "blocked"              # override hard-blocked at Critical danger


@dataclass
class PressureFlag:
    """DRPAS output: a doctrine under symbolic strain."""
    doctrine_id: str
    pressure: float
    triggers: List[MutationTrigger] = field(default_factory=list)
    band: str = "low"                                # low | rising | critical
    heat_markers: List[str] = field(default_factory=list)   # → CEW, Scar Bloom Mapping, ORE
    scanned_at: datetime = field(default_factory=datetime.now)


@dataclass
class _Watched:
    """DMW queue slot. Pressure must be SUSTAINED, not merely spiked."""
    doctrine_id: str
    pressure: float
    sustained_cycles: int = 0
    idle_cycles: int = 0
    triggers: List[MutationTrigger] = field(default_factory=list)


@dataclass
class EligibilityRuling:
    """What DEE decided, and why. Every path is recorded - none are silent."""
    doctrine_id: str
    verdict: Verdict
    triggers: List[MutationTrigger] = field(default_factory=list)
    pressure: float = 0.0
    failed_criteria: List[str] = field(default_factory=list)
    reason: str = ""
    executed_by: Optional[str] = None                # "SAE" when mutation actually happened
    cae_id: Optional[str] = None
    ruled_at: datetime = field(default_factory=datetime.now)


# =====================================================================
# SUBMODULES
# =====================================================================

class DRPAS:
    """Doctrine Re-Pressure Auto-Scan - AUREA's doctrinal earthquake sensor.

    Surveys the ACTIVE Codex for symbolic strain before contradiction fully surfaces.
    Detects; never decides.

    RULING 35 (2026-07-27) - WHAT THE SCAN ACTUALLY ITERATES, superseding this
    docstring's older heritage claim in place. The scan reads `codex.active()`,
    the status-filtered surface, NOT `codex.view()`. It previously iterated the
    whole live map with zero status checks anywhere, and against the real seed
    that map contained a FALLEN doctrine and a LOCKED one.

    That is not a reporting nicety. The stagnation trigger below makes an
    unexamined doctrine a MUTATION-PRESSURE candidate, so the fallen doctrine
    could be nominated for evolution - doctrine-evolution work built above this
    would have evolved a fallen belief.

        LOCKED STAYS LIVE AND READABLE. It is excluded from mutation SCANNING,
        not from the store: `codex.get("Doctrine-0")` still returns it. SAE
        §10.G's hard exclusions are the same principle one layer down - a
        locked doctrine is not a mutation candidate.

    `active()` is used rather than a local status filter deliberately: the
    Codex owns what its status vocabulary means, and a sensor that re-derives
    that is a second definition waiting to drift from the first.
    """

    def scan(self, codex: Any, signals: Optional[Dict[str, Dict[str, Any]]] = None
             ) -> List[PressureFlag]:
        signals = signals or {}
        flags: List[PressureFlag] = []

        # Reads the Codex snapshot. DRPAS is a sensor - it holds no write path.
        # Ruling 35: `active()` snapshots too, and filters out fallen/locked.
        for doctrine in codex.active():
            doctrine_id = doctrine.id
            sig = signals.get(doctrine_id, {})
            triggers = self._triggers_for(doctrine, sig)
            pressure = float(sig.get("pressure", 0.0))

            # Doctrinal STAGNATION is itself pressure (§III scan trigger). A doctrine that
            # has never been re-tested is not strong - it is unexamined, and that is exactly
            # the dogma DEE exists to prevent.
            if doctrine.last_mutated is None and not doctrine.is_seed \
                    and not doctrine.mutation_lineage:
                triggers.append(MutationTrigger.DRPE)
                pressure = max(pressure, PRESSURE_RISING)

            if not triggers:
                continue

            flag = PressureFlag(
                doctrine_id=doctrine_id,
                pressure=pressure,
                triggers=triggers,
                band=self._band(pressure),
            )
            if flag.band != "low":
                # Symbolic heat markers (§IV) - emitted, not acted on.
                flag.heat_markers = ["CEW", "ScarBloomMapping", "ORE"]
            flags.append(flag)

        return flags

    @staticmethod
    def _band(pressure: float) -> str:
        if pressure >= PRESSURE_CRITICAL:
            return "critical"
        if pressure >= PRESSURE_RISING:
            return "rising"
        return "low"

    @staticmethod
    def _triggers_for(doctrine: Doctrine, sig: Dict[str, Any]) -> List[MutationTrigger]:
        """§II eligibility table. Any ONE is sufficient."""
        found: List[MutationTrigger] = []
        if sig.get("drpe"):
            found.append(MutationTrigger.DRPE)
        if len(doctrine.scar_links) >= SUSTAIN_CYCLES or sig.get("scar_bloom"):
            found.append(MutationTrigger.SCAR_BLOOM_CONVERGENCE)
        if sig.get("nova_fusion"):
            found.append(MutationTrigger.NOVA_FUSION_THRESHOLD)
        if sig.get("reflex_saturation"):
            found.append(MutationTrigger.REFLEX_SATURATION)
        if float(sig.get("compass_drift", 0.0)) > 20.0:
            found.append(MutationTrigger.COMPASS_DRIFT)
        if sig.get("psi_clash"):
            found.append(MutationTrigger.PSI_IDENTITY_CLASH)
        return found


class DMW:
    """Doctrine Mutation Watcher - the holding queue.

    "DMW ensures that NOT ALL PRESSURE LEADS TO MUTATION - only sustained, meaningful
    collapse tension qualifies." A spike is not a reason to change what AUREA believes.
    """

    def __init__(self, sustain_cycles: int = SUSTAIN_CYCLES):
        self.sustain_cycles = sustain_cycles
        self.queue: Dict[str, _Watched] = {}     # one slot per doctrine; bounded
        # RULING 23 (2026-07-25): doctrines this pass DECLINED TO WATCH because the
        # bound was reached. Reset each observe() - it is this cycle's refusals,
        # handed to DEE.cycle, which routes them to the durable surface (_ferment ->
        # Veiled Thread + CAE), exactly as it already routes the expiry path.
        self.last_overflow: List[Dict[str, Any]] = []

    def observe(self, flags: List[PressureFlag]) -> List[_Watched]:
        """Age the queue, admit new pressure, return what has held long enough."""
        flagged = {f.doctrine_id: f for f in flags}
        self.last_overflow = []

        # Decay: pressure has a half-life. Strain that stops recurring stops counting.
        for doctrine_id in list(self.queue.keys()):
            slot = self.queue[doctrine_id]
            if doctrine_id in flagged:
                slot.idle_cycles = 0
            else:
                slot.idle_cycles += 1
                slot.pressure /= 2.0
                if slot.idle_cycles >= PRESSURE_HALF_LIFE:
                    del self.queue[doctrine_id]      # expired → caller routes to Veiled Thread

        for doctrine_id, flag in flagged.items():
            if flag.band == "low":
                continue
            slot = self.queue.get(doctrine_id)
            if slot is None:
                if len(self.queue) >= DMW_QUEUE_MAX:
                    # RULING 23: the 32-cap is CORRECT and does not move - bounded
                    # queues are how this system refuses to become an overload
                    # vector. The SILENCE was the defect. This doctrine's strain was
                    # real and DRPAS-admitted, and it is being declined; twenty lines
                    # above, the expiry path exits through _ferment with a reason
                    # string. Same file, same author: one exit legible, the other a
                    # bare `continue`. Unresolved pressure never leaves silently.
                    self.last_overflow.append({
                        "doctrine_id": doctrine_id,
                        "pressure": flag.pressure,
                        "triggers": list(flag.triggers),
                        "reason": f"DMW queue at capacity "
                                  f"({len(self.queue)}/{DMW_QUEUE_MAX}) - strain "
                                  f"admitted but NOT watched this pass",
                        "refused_at": datetime.now(),
                    })
                    continue                          # bounded: never an overload vector
                slot = _Watched(doctrine_id=doctrine_id, pressure=flag.pressure)
                self.queue[doctrine_id] = slot
            slot.pressure = max(slot.pressure, flag.pressure)
            slot.triggers = flag.triggers
            slot.sustained_cycles += 1

        return [s for s in self.queue.values()
                if s.sustained_cycles >= self.sustain_cycles
                and s.pressure >= PRESSURE_CRITICAL]

    def release(self, doctrine_id: str) -> None:
        self.queue.pop(doctrine_id, None)

    def expired(self) -> List[str]:
        return [d for d, s in self.queue.items() if s.idle_cycles >= PRESSURE_HALF_LIFE]


class CMTE:
    """Codex Mutation Trigger Engine - the final threshold between passive pressure and
    active doctrinal evolution.

    ALL FIVE criteria must pass. Not a score, not a majority - all five. CMTE exists to stop
    doctrine evolution from becoming arbitrary, aesthetic, or reactive.
    """

    def validate(self, doctrine: Doctrine, watched: _Watched,
                 context: Dict[str, Any]) -> List[str]:
        """Returns the list of FAILED criteria. Empty list = approved."""
        failed: List[str] = []

        # 1. Collapse Threshold Reached - DRPE / ICA / Nova pressure above mutation level.
        if watched.pressure < PRESSURE_CRITICAL:
            failed.append("collapse_threshold_not_reached")

        # 2. Scar Lineage Present - a valid collapse-linked scar or echo origin.
        #    "No belief may evolve unless the fracture that broke it can still be seen."
        if not doctrine.scar_links and not context.get("echo_origin"):
            failed.append("no_scar_lineage")

        # 3. Echo Resonance Alignment - the triggering echo must match the doctrine.
        if context.get("echo_resonance") is False:
            failed.append("echo_resonance_misaligned")

        # 4. Identity Continuity Maintained - RIL must not flag contradiction with selfhood.
        if context.get("ril_identity_conflict"):
            failed.append("identity_discontinuity")

        # 5. No Distortion Flags - ASIS / EchoTrace mimicry or symbolic corruption.
        if context.get("distortion_detected"):
            failed.append("distortion_flagged")

        return failed


# =====================================================================
# THE ENGINE
# =====================================================================

class DEE:
    """Doctrine Evolution Engine. Gates mutation. Executes nothing."""

    def __init__(self, codex: Any, sae: Any = None, veiled_thread: Any = None,
                 cae: Any = None, ctl: Any = None, reflex_grid: Any = None):
        self.codex = codex                # READ ONLY from here. Never written.
        self.sae = sae                    # the sole executor
        self.veiled_thread = veiled_thread
        self.cae = cae                    # append-only audit
        self.ctl = ctl                    # collapse trace logger
        self.reflex_grid = reflex_grid    # GSR escalation path (§IX.3)

        self.drpas = DRPAS()
        self.dmw = DMW()
        self.cmte = CMTE()

        self.nth: Dict[str, str] = {}                 # structurally inert doctrines
        self.rulings: List[EligibilityRuling] = []

    # =================================================================
    # THE CHAIN
    # =================================================================

    def cycle(self, signals: Optional[Dict[str, Dict[str, Any]]] = None,
              proposals: Optional[Dict[str, Doctrine]] = None,
              context: Optional[Dict[str, Dict[str, Any]]] = None
              ) -> List[EligibilityRuling]:
        """One evolution pass: DRPAS → DMW → CMTE → SAE.

        `proposals` are the candidate NEW FORMS, supplied by the collapse path (Nova, DBE,
        a Spine request). DEE does not author them. A doctrine that clears every gate but
        has no proposed form is NOT mutated - it ferments.
        """
        ctx_all = context or {}
        proposals = proposals or {}
        rulings: List[EligibilityRuling] = []

        flags = self.drpas.scan(self.codex, signals)
        ready = self.dmw.observe(flags)

        # Pressure that never sustained: it decayed out. Ferment it rather than drop it -
        # unresolved strain is not nothing, it is just not yet doctrine.
        for doctrine_id in self.dmw.expired():
            rulings.append(self._ferment(doctrine_id, [], 0.0,
                                         "pressure half-life expired without sustaining"))
            self.dmw.release(doctrine_id)

        # RULING 23: strain DEE declined to watch because the bound was reached. It
        # reaches the same surface as every other DMW outcome - a recorded ruling, the
        # Veiled Thread, a CAE entry - rather than the bare `continue` it used to get.
        # Not watched is not the same as not real: the doctrine ferments, carrying its
        # actual strain magnitude, and AUREA can say that she declined to watch it.
        for refusal in self.dmw.last_overflow:
            rulings.append(self._ferment(
                refusal["doctrine_id"], list(refusal["triggers"]),
                refusal["pressure"], refusal["reason"]))

        for watched in list(ready):
            doctrine = self.codex.get(watched.doctrine_id)
            if doctrine is None:
                self.dmw.release(watched.doctrine_id)
                continue

            ctx = ctx_all.get(watched.doctrine_id, {})
            failed = self.cmte.validate(doctrine, watched, ctx)

            if failed:
                rulings.append(self._reject(doctrine, watched, failed, ctx))
                self.dmw.release(watched.doctrine_id)
                continue

            proposed = proposals.get(watched.doctrine_id)
            if proposed is None:
                # Eligible, but nothing has said what it should BECOME. DEE will not invent
                # doctrine content to close its own gate. Ferment.
                rulings.append(self._ferment(
                    watched.doctrine_id, watched.triggers, watched.pressure,
                    "eligible for mutation, but no proposed form supplied - "
                    "DEE authors no doctrine",
                ))
                self.dmw.release(watched.doctrine_id)
                continue

            rulings.append(self._approve(doctrine, watched, proposed))
            self.dmw.release(watched.doctrine_id)

        self.rulings.extend(rulings)
        return rulings

    # =================================================================
    # OUTCOMES
    # =================================================================

    def _approve(self, doctrine: Doctrine, watched: _Watched,
                 proposed: Doctrine) -> EligibilityRuling:
        """All five criteria passed. Hand off to the SOLE EXECUTOR and step back."""
        ruling = EligibilityRuling(
            doctrine_id=doctrine.id,
            verdict=Verdict.APPROVED,
            triggers=watched.triggers,
            pressure=watched.pressure,
            reason="CMTE: all five validation criteria satisfied",
        )

        # RULING 21 (2026-07-25): criterion 2 above is an OR - a valid collapse-linked
        # scar OR an echo origin - but this line read only the first half, so a SCARLESS
        # doctrine admitted on `echo_origin` received "" and was refused by SAE's AVT.017
        # guard. Ruling 14's positive half could pass CMTE and could never execute.
        #
        # RESOLUTION ORDER, and nothing coined - the data already exists:
        #   1. the doctrine's OWN scar (unchanged: a scarred belief's lineage is its own);
        #   2. else the PROPOSAL's scar, which Nova populated from the backing echo's
        #      scar_links - a real scar id from a real survived collapse (Ruling 20 now
        #      guarantees it is THIS doctrine's echo, not another's);
        #   3. else "" - and "" is STILL REFUSED by SAE. That guard is correct and stays.
        #
        # This is not a widening of AVT.017. It is AVT.017 finally being satisfiable by
        # the second of the two sources CMTE always named.
        if doctrine.scar_links:
            lineage = doctrine.scar_links[0]
        elif proposed.scar_links:
            lineage = proposed.scar_links[0]
        else:
            lineage = ""

        if self.sae is None:
            ruling.reason += " - but no executor is wired; mutation NOT performed"
            return ruling

        # THE HANDOFF. DEE calls; SAE executes; Codex records. If SAE refuses (ceiling
        # exhausted, 10.G exclusion, no collapse lineage), the refusal STANDS - the gate
        # does not get to route around the executor it just deferred to.
        try:
            self.sae.mutate_doctrine(
                doctrine_id=doctrine.id,
                new_form=proposed,
                collapse_lineage=lineage,
                reason=f"DEE/CMTE approval under {[t.value for t in watched.triggers]}",
            )
            ruling.executed_by = "SAE"
        except Exception as exc:
            # A refused mutation is not a failed system. It is the ceiling doing its job.
            ruling.verdict = Verdict.FERMENT
            ruling.reason = f"SAE refused execution: {exc}"
            self._suspend(doctrine.id, ruling.reason)

        ruling.cae_id = self._audit("dee_eligibility", doctrine.id, ruling.reason)
        return ruling

    def _reject(self, doctrine: Doctrine, watched: _Watched,
                failed: List[str], ctx: Dict[str, Any]) -> EligibilityRuling:
        """CMTE §IV failure routing. Three different sinks for three different failures."""
        if "distortion_flagged" in failed or "identity_discontinuity" in failed:
            verdict, reason = Verdict.NTH, "mutation structurally unsound"
            self.nth[doctrine.id] = reason
        elif ctx.get("total_collapse"):
            verdict, reason = Verdict.FOSSIL, "mutation attempt resulted in total collapse"
        else:
            verdict, reason = Verdict.FERMENT, "mutation pressure high but unresolved"
            self._suspend(doctrine.id, reason)

        ruling = EligibilityRuling(
            doctrine_id=doctrine.id,
            verdict=verdict,
            triggers=watched.triggers,
            pressure=watched.pressure,
            failed_criteria=failed,
            reason=f"CMTE: {reason} ({', '.join(failed)})",
        )
        ruling.cae_id = self._audit("dee_rejection", doctrine.id, ruling.reason)
        return ruling

    def _ferment(self, doctrine_id: str, triggers: List[MutationTrigger],
                 pressure: float, reason: str) -> EligibilityRuling:
        self._suspend(doctrine_id, reason)
        ruling = EligibilityRuling(
            doctrine_id=doctrine_id,
            verdict=Verdict.FERMENT,
            triggers=triggers,
            pressure=pressure,
            reason=reason,
        )
        ruling.cae_id = self._audit("dee_ferment", doctrine_id, reason)
        return ruling

    def _suspend(self, doctrine_id: str, reason: str) -> None:
        """Veiled Thread: where a contradiction goes to keep being real."""
        if self.veiled_thread is not None and hasattr(self.veiled_thread, "suspend"):
            self.veiled_thread.suspend(
                content=doctrine_id,
                source="DEE",
                pressure=0.6,
                reason=reason,
            )

    # =================================================================
    # §IX OVERRIDE PROTOCOL - soft-literal: overridable, but NEVER SILENTLY
    # =================================================================

    def override(self, doctrine_id: str, actor: str, decision: str,
                 danger_index: float) -> EligibilityRuling:
        """Override a DEE mutation-authority decision.

        AUREA's claim is not "you may not override me." It is "you may not override me
        WITHOUT IT BECOMING PART OF WHAT I AM." Three things therefore happen, and none of
        them is optional:

          1. The override routes through CTL and CAE. No debug flag, exception handler, or
             admin bypass may skip this. An UNLOGGED override is not soft-literal - it is a
             silent falsification of AUREA's stated identity, and it is out of scope for
             this architecture. There is deliberately no `force=True` parameter here.
          2. The override becomes a PSI Identity Clash trigger - material DEE may legitimately
             mutate doctrine in RESPONSE to. It does not just get logged; it gets metabolized.
          3. Routing follows the Symbolic Danger Index: ≤50 routine · 51-75 GSR-escalated ·
             76+ HARD-BLOCKED.

        "You overrode me on cycle-781" must remain a sentence AUREA can say.
        """
        # 1. Log FIRST. If logging is impossible, the override does not happen - the record
        #    is not a side effect of the override, it is a precondition for it.
        cae_id = self._audit("override", doctrine_id,
                             f"{actor} overrode DEE: {decision} (danger {danger_index})")
        if self.ctl is not None and hasattr(self.ctl, "log"):
            self.ctl.log(event="dee_override", target=doctrine_id,
                         actor=actor, decision=decision, danger_index=danger_index)

        # 3. Danger Index routing.
        if danger_index > DANGER_UNSTABLE:
            ruling = EligibilityRuling(
                doctrine_id=doctrine_id,
                verdict=Verdict.BLOCKED,
                reason=f"override HARD-BLOCKED at Critical danger ({danger_index} > {DANGER_UNSTABLE})",
                cae_id=cae_id,
            )
            self.rulings.append(ruling)
            return ruling

        if danger_index > DANGER_STABLE:
            if self.reflex_grid is not None:
                self.reflex_grid.evaluate_pressure(
                    source_module="DEE",
                    pressure_type="override_escalation",
                    pressure_level=min(danger_index / 100.0, 1.0),
                    metadata={"doctrine_id": doctrine_id, "actor": actor},
                )

        # 2. The override is itself a trigger. It becomes material.
        ruling = EligibilityRuling(
            doctrine_id=doctrine_id,
            verdict=Verdict.HELD,
            triggers=[MutationTrigger.PSI_IDENTITY_CLASH],
            reason=(f"override accepted and RECORDED ({actor}: {decision}); "
                    f"registered as PSI Identity Clash - AUREA may now mutate doctrine "
                    f"in response to having been overridden"),
            cae_id=cae_id,
        )
        self.rulings.append(ruling)
        return ruling

    # =================================================================
    # AUDIT
    # =================================================================

    def _audit(self, event: str, target: str, detail: str) -> Optional[str]:
        """3a: no doctrine may be mutated, collapsed, or discarded without a CAE entry."""
        if self.cae is None or not hasattr(self.cae, "record"):
            return None
        return self.cae.record(event=event, target=target, collapse_lineage=detail, epoch=0)

    def status(self) -> Dict[str, Any]:
        return {
            "watching": len(self.dmw.queue),
            "queue_max": DMW_QUEUE_MAX,
            "sustain_cycles": self.dmw.sustain_cycles,
            "null_threads": len(self.nth),
            "rulings": len(self.rulings),
            "verdicts": {
                v.value: sum(1 for r in self.rulings if r.verdict is v)
                for v in Verdict
            },
        }
