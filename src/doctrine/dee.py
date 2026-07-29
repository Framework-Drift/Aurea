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

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.doctrine.cae import CAE
from src.doctrine.mutation_proof import (
    ContentDelta, CriterionResult, DoctrineMutationProof,
)
from src.utils.continuity import LoadReport, RestorationOutcome
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

    STATE_VERSION = 1

    def __init__(self, sustain_cycles: int = SUSTAIN_CYCLES, codex: Any = None,
                 runtime_path: str = "data/runtime/dmw_queue.json"):
        self.sustain_cycles = sustain_cycles
        # READ handle only (Ruling 1: reads are free). Used at LOAD time to ask
        # whether a queued doctrine id still names a doctrine. Nova's scar_core
        # handle from Slice 1 is the precedent; DMW gains no write path here.
        self.codex = codex
        # Ruling 42 Slice 2 / Ruling 39: `__init__` DEFAULT under `data/runtime/`,
        # redirected by name in conftest. Slice 1's shape.
        self.runtime_path = Path(runtime_path)
        self.queue: Dict[str, _Watched] = {}     # one slot per doctrine; bounded
        # RULING 23 (2026-07-25): doctrines this pass DECLINED TO WATCH because the
        # bound was reached. Reset each observe() - it is this cycle's refusals,
        # handed to DEE.cycle, which routes them to the durable surface (_ferment ->
        # Veiled Thread + CAE), exactly as it already routes the expiry path.
        self.last_overflow: List[Dict[str, Any]] = []

        # Ruling 42 taxonomy (Slice 1's vocabulary, reused verbatim).
        self.load_report: Optional[LoadReport] = None
        # Slots whose doctrine the Codex no longer holds. HELD, VISIBLE,
        # REPORTED - never silently dropped, never silently re-pointed.
        self.quarantined_slots: List[Dict[str, Any]] = []
        self.persist_failures: List[Dict[str, Any]] = []

        self.load()

    # =================================================================
    # CONTINUITY (Ruling 42 Slice 2) - sustained pressure survives
    # =================================================================

    def save(self) -> None:
        """Whole-file snapshot. Ruling 32's minimal semantics VERBATIM.

        WHAT ROUND-TRIPS: `sustain_cycles` and every queue slot
        (`doctrine_id`, `pressure`, `sustained_cycles`, `idle_cycles`,
        `triggers`).

        NO CLOCK RIDES WITH THIS ONE, AND THAT IS NOT AN OMISSION. Res.3's
        coherence rule binds ABSOLUTE ordinals - TCAML's `_held_since` is one, and
        it must travel with the `_cycle` it was measured against. `sustained_cycles`
        and `idle_cycles` are pure RELATIVE counters: DMW holds no cycle number at
        all, and each counter means "how many observes in a row", which is exactly
        as true after a restart as before it. So they persist BARE, and inventing a
        clock to pair them with would be coining the ordinal the rule protects.

        REPORTED-NOT-PERSISTED: `last_overflow` - Ruling 23 refusals from the
        cycle just ended, reset at the top of every `observe()` and consumed by
        `DEE.cycle` in the same pass. A restored copy would re-route refusals that
        were already routed.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.STATE_VERSION,
            "saved_at": datetime.now().isoformat(),
            "sustain_cycles": self.sustain_cycles,
            "queue": [
                {
                    "doctrine_id": s.doctrine_id,
                    "pressure": s.pressure,
                    "sustained_cycles": s.sustained_cycles,
                    "idle_cycles": s.idle_cycles,
                    "triggers": [t.value for t in s.triggers],
                }
                for s in self.queue.values()
            ],
        }
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self) -> bool:
        """Runtime state if present, ELSE an empty queue.

        A RESTORED QUEUE OVER `DMW_QUEUE_MAX` IS A REFUSED LOAD, NEVER A
        TRUNCATION (Slice 1's RACM shape, verbatim). Truncating would discard
        real sustained pressure and report a healthy queue - and the 32-cap does
        not move, because bounded queues are how this system refuses to become an
        overload vector (Ruling 23).

        A SLOT NAMING A DOCTRINE THE CODEX NO LONGER HOLDS IS QUARANTINED - held
        out of the queue, visible on `quarantined_slots`, reported. It is not
        dropped (that discards pressure AUREA sustained) and not re-pointed
        (nothing may choose a different doctrine for it).
        """
        if not self.runtime_path.exists():
            return False

        try:
            with open(self.runtime_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"expected a JSON object, got {type(data).__name__}")
        except (OSError, ValueError) as exc:
            return self._refuse(f"unreadable watch queue: {exc!r}")

        version = data.get("version")
        if version != self.STATE_VERSION:
            return self._refuse(
                f"unknown state version {version!r} (this build writes "
                f"{self.STATE_VERSION}); the file was left untouched")

        slots = data.get("queue") or []
        if len(slots) > DMW_QUEUE_MAX:
            return self._refuse(
                f"restored queue depth {len(slots)} exceeds the bound "
                f"{DMW_QUEUE_MAX}; truncating would silently discard sustained "
                f"pressure, so the whole restore is refused")

        try:
            rebuilt = [
                _Watched(
                    doctrine_id=s["doctrine_id"],
                    pressure=float(s.get("pressure", 0.0)),
                    sustained_cycles=int(s.get("sustained_cycles", 0)),
                    idle_cycles=int(s.get("idle_cycles", 0)),
                    triggers=[MutationTrigger(t) for t in (s.get("triggers") or [])],
                )
                for s in slots
            ]
        except (KeyError, TypeError, ValueError) as exc:
            return self._refuse(f"a watch slot did not reconstruct: {exc!r}")

        held: List[Dict[str, Any]] = []
        kept: Dict[str, _Watched] = {}
        for slot in rebuilt:
            if self._doctrine_missing(slot.doctrine_id):
                held.append({
                    "doctrine_id": slot.doctrine_id,
                    "pressure": slot.pressure,
                    "sustained_cycles": slot.sustained_cycles,
                    "reason": "the Codex no longer holds this doctrine",
                })
            else:
                kept[slot.doctrine_id] = slot

        self.queue = kept
        self.sustain_cycles = int(data.get("sustain_cycles", self.sustain_cycles))
        self.quarantined_slots.extend(held)

        detail: Dict[str, Any] = {"saved_at": data.get("saved_at"),
                                  "queue_depth": len(kept)}
        if held:
            detail["quarantined"] = [h["doctrine_id"] for h in held]
        self.load_report = LoadReport(
            store="dee.dmw_queue",
            outcome=(RestorationOutcome.PARTIALLY_RESTORED if held
                     else RestorationOutcome.RESTORED),
            path=str(self.runtime_path), resumed=True, detail=detail)
        return True

    def _doctrine_missing(self, doctrine_id: str) -> bool:
        """NO CODEX MEANS NO CHECK, and that is not the same as a check that
        passed (Docket H's NOT_COUNTABLE / NONE_FOUND cut). A DMW with no handle
        to the doctrine store has run no instrument, so it quarantines nothing."""
        getter = getattr(self.codex, "get", None)
        if not callable(getter):
            return False
        return getter(doctrine_id) is None

    def _refuse(self, reason: str) -> bool:
        self.queue = {}
        self.load_report = LoadReport(
            store="dee.dmw_queue", outcome=RestorationOutcome.REFUSED,
            path=str(self.runtime_path), resumed=False, detail={"reason": reason})
        return False

    def _persist(self) -> None:
        """BEST-EFFORT save. NEVER RAISES (Ruling 11's shape). A REFUSED load
        makes this a no-op for the life of the process - "the file is left
        BYTE-UNTOUCHED" is not a statement about the instant of the refusal."""
        if self.load_report is not None \
                and self.load_report.outcome is RestorationOutcome.REFUSED:
            return
        try:
            self.save()
        except (OSError, TypeError, ValueError) as exc:
            self.persist_failures.append({
                "op": "save", "path": str(self.runtime_path), "error": repr(exc),
                "at": datetime.now().isoformat(),
            })

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

        # Ruling 42: the queue changed, so the queue is written. Sustained
        # pressure is what DMW exists to accumulate; a process that died between
        # here and a later boundary would restore counters that had already moved.
        self._persist()
        return [s for s in self.queue.values()
                if s.sustained_cycles >= self.sustain_cycles
                and s.pressure >= PRESSURE_CRITICAL]

    def release(self, doctrine_id: str) -> None:
        self.queue.pop(doctrine_id, None)
        self._persist()

    def expired(self) -> List[str]:
        return [d for d, s in self.queue.items() if s.idle_cycles >= PRESSURE_HALF_LIFE]


class CMTE:
    """Codex Mutation Trigger Engine - the final threshold between passive pressure and
    active doctrinal evolution.

    ALL FIVE criteria must pass. Not a score, not a majority - all five. CMTE exists to stop
    doctrine evolution from becoming arbitrary, aesthetic, or reactive.
    """

    # Canonical criterion name -> the FAILURE LABEL `_reject` routes on. Those
    # labels are load-bearing (`_reject` branches on `distortion_flagged` and
    # `identity_discontinuity`), so they are named here once rather than spelled
    # in two places that could drift.
    FAILURE_LABELS = {
        "collapse_threshold_reached": "collapse_threshold_not_reached",
        "scar_lineage_present": "no_scar_lineage",
        "echo_resonance_aligned": "echo_resonance_misaligned",
        "identity_continuity_maintained": "identity_discontinuity",
        "no_distortion_flags": "distortion_flagged",
    }

    def evaluate(self, doctrine: Doctrine, watched: _Watched,
                 context: Dict[str, Any]) -> Dict[str, CriterionResult]:
        """RULING 45: the five criteria AS EVALUATED - PASS, FAIL, or ABSENT.

        THE ONE SOURCE OF TRUTH. `validate()` now derives its failure list from
        this, so what the gate decided and what the proof records cannot drift.

        ABSENT IS NOT PASS, and the distinction is the whole reason this method
        exists. Criteria 3, 4 and 5 are read with `context.get(...)`, so an
        unsupplied key does not fail them - that absent-reads-as-pass semantics
        is DELIBERATE and unchanged. But recording it as PASS would claim an
        instrument ran and found the doctrine clean. No instrument ran. Docket
        H's `NONE_FOUND` / `NOT_COUNTABLE` cut, applied to a gate instead of a
        tally: two silences are not the same silence.

        Criteria 1 and 2 are never ABSENT - `watched.pressure` always exists, and
        criterion 2's two sources are both always readable, so their absence is a
        FAILURE (no visible fracture) rather than a missing instrument.
        """
        results: Dict[str, CriterionResult] = {}

        # 1. Collapse Threshold Reached - DRPE / ICA / Nova pressure above mutation level.
        results["collapse_threshold_reached"] = (
            CriterionResult.PASS if watched.pressure >= PRESSURE_CRITICAL
            else CriterionResult.FAIL)

        # 2. Scar Lineage Present - a valid collapse-linked scar or echo origin.
        #    "No belief may evolve unless the fracture that broke it can still be seen."
        results["scar_lineage_present"] = (
            CriterionResult.PASS
            if (doctrine.scar_links or context.get("echo_origin"))
            else CriterionResult.FAIL)

        # 3. Echo Resonance Alignment - the triggering echo must match the doctrine.
        #    UNSUPPLIED BY DESIGN: no honest resonance value exists in the organ
        #    (Echo Protocol IV's scores are deliberately un-coined).
        results["echo_resonance_aligned"] = self._tri_state(
            context, "echo_resonance", fails_when_true=False)

        # 4. Identity Continuity Maintained - RIL must not flag contradiction with selfhood.
        results["identity_continuity_maintained"] = self._tri_state(
            context, "ril_identity_conflict", fails_when_true=True)

        # 5. No Distortion Flags - ASIS / EchoTrace mimicry or symbolic corruption.
        results["no_distortion_flags"] = self._tri_state(
            context, "distortion_detected", fails_when_true=True)

        return results

    @staticmethod
    def _tri_state(context: Dict[str, Any], key: str,
                   fails_when_true: bool) -> CriterionResult:
        """PASS / FAIL / ABSENT for a criterion read out of `context`.

        `fails_when_true` distinguishes the two shapes already in use: criteria 4
        and 5 fail when a flag is RAISED, criterion 3 fails when alignment is
        explicitly False.
        """
        if key not in context or context[key] is None:
            return CriterionResult.ABSENT
        value = context[key]
        if fails_when_true:
            return CriterionResult.FAIL if value else CriterionResult.PASS
        return CriterionResult.FAIL if value is False else CriterionResult.PASS

    def validate(self, doctrine: Doctrine, watched: _Watched,
                 context: Dict[str, Any]) -> List[str]:
        """Returns the list of FAILED criteria. Empty list = approved.

        DERIVED from `evaluate()` since Ruling 45 - the verdict and the record of
        the verdict come from one evaluation, so they cannot disagree.
        """
        results = self.evaluate(doctrine, watched, context)
        return [self.FAILURE_LABELS[name] for name, result in results.items()
                if result is CriterionResult.FAIL]


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
        # RULING 45 - DEFAULT BY CONSTRUCTION (see `cae.py`). `aurea_core`
        # injects ONE shared instance into SAE and DEE; a bare DEE() still gets a
        # working ledger instead of a silent no-op.
        self.cae = cae or CAE()           # append-only audit
        self.ctl = ctl                    # collapse trace logger
        self.reflex_grid = reflex_grid    # GSR escalation path (§IX.3)

        self.drpas = DRPAS()
        # Ruling 42 Slice 2: DMW takes the same READ handle DEE holds, so a LOAD
        # can ask whether a queued doctrine id still names a doctrine. Reads are
        # free (Ruling 1); DMW gains no write path to the Codex.
        self.dmw = DMW(codex=codex)
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
            # Ruling 45: ONE evaluation feeds both the verdict and the proof.
            criteria = self.cmte.evaluate(doctrine, watched, ctx)
            failed = [self.cmte.FAILURE_LABELS[n] for n, r in criteria.items()
                      if r is CriterionResult.FAIL]

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

            rulings.append(self._approve(doctrine, watched, proposed, criteria))
            self.dmw.release(watched.doctrine_id)

        self.rulings.extend(rulings)
        return rulings

    # =================================================================
    # OUTCOMES
    # =================================================================

    def _approve(self, doctrine: Doctrine, watched: _Watched,
                 proposed: Doctrine,
                 criteria: Dict[str, CriterionResult]) -> EligibilityRuling:
        """All five criteria passed. Hand off to the SOLE EXECUTOR and step back.

        `criteria` is the SAME evaluation the gate decided on (Ruling 45) - it is
        threaded in rather than recomputed, so the proof records what actually
        happened rather than what a second run of the same inputs would say.
        """
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

        # RULING 45 - THE FULL LINEAGE, not the `[0]` above.
        #
        # `collapse_lineage` (singular) SURVIVES unchanged on the call and on
        # `MutationRecord`: AVT.017 refuses "" and that guard is correct and
        # untouched. But a single string was never the lineage - it was the FIRST
        # ELEMENT of it, chosen because `mutate_doctrine` took one string. The
        # proof carries BOTH criterion-2 sources in full, ordered, deduplicated:
        # the doctrine's own scars first (its lineage is its own), then the
        # proposal's (which Nova populated from the backing echo, and which
        # Ruling 20 guarantees belongs to THIS doctrine).
        scar_lineage = tuple(dict.fromkeys(
            [s for s in list(doctrine.scar_links) + list(proposed.scar_links) if s]
        ))

        proof = DoctrineMutationProof(
            contradiction_core={
                "triggers": [t.value for t in watched.triggers],
                "pressure": watched.pressure,
                "sustained_cycles": watched.sustained_cycles,
                "strain_source": "DRPAS/DMW sustained doctrine strain",
                "doctrine_id": doctrine.id,
            },
            scar_lineage=scar_lineage,
            echo_provenance=self._echo_provenance(proposed),
            content_delta=ContentDelta(
                ancestor_id=doctrine.id,
                name_before=doctrine.name,
                name_after=proposed.name,
                description_before=doctrine.description,
                description_after=proposed.description,
            ),
            preserved_invariants=criteria,
            # EMPTY IS A REAL ANSWER HERE and the field says so: CMTE approved,
            # so nothing it evaluated was left unresolved. What DEE cannot see it
            # does not claim to have resolved either - it simply has no name for.
            unresolved_residue=(),
        )

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
                proof=proof,
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

    @staticmethod
    def _echo_provenance(proposed: Doctrine) -> Optional[Dict[str, str]]:
        """The echo recorded as AUTHORING this proposal, from the proposal's own
        provenance tags. `None` where no Nova echo authored it.

        READS THE TAGS NOVA WROTE, and does not ask Nova. DEE holds no Nova
        handle and is not gaining one for a forensic field: `nova.proposals()`
        stamps `tca_tags` with `prov:{store}:{record_id}` at emission, so the
        authorship is already ON the proposal. `None` here is the ORDINARY case
        (a proposal that no echo authored) and is not a gap to fill.
        """
        for tag in getattr(proposed, "tca_tags", None) or []:
            if isinstance(tag, str) and tag.startswith("prov:nova_echo_index:"):
                return {"echo_id": tag.split(":", 2)[2],
                        "provenance_key": proposed.id}
        return None

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

    def _audit(self, event: str, target: str, detail: str) -> str:
        """3a: no doctrine may be mutated, collapsed, or discarded without a CAE entry.

        RULING 45: the `if self.cae is None or not hasattr(self.cae, "record")`
        branch is GONE, and with it the last way this method could answer the
        canon's absolute with a None. The ledger is constructed by default (see
        `__init__`), so neither the absence nor the duck-type check has anything
        left to guard.

        The `hasattr` half deserves its own epitaph: it is the same shape as the
        `hasattr(scar_core, "form_scar")` guard that SILENTLY DROPPED every
        SBSRE scar request (CLAUDE.md section 3). A capability check that
        degrades to a no-op turns a missing collaborator into a missing record.
        """
        return self.cae.record(event=event, target=target,
                               collapse_lineage=detail, epoch=0)

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
