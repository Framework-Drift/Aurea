"""
aurea_core.py - Central AUREA Pipeline Controller
Orchestrates the flow: Input -> SPL -> EchoNet -> Reflexes -> Scars -> Output
"""

from src.perception.spl import SPL
from src.filtration.echonet import EchoNet, Verdict as EchoVerdict
from src.filtration.scar_logic_core import ScarLogicCore
from src.filtration.scar_management import SML
from src.doctrine.codex import Codex, CodexWriteViolation
from src.doctrine.doctrine_spine import DoctrineSpine
from src.doctrine.dee import DEE
from src.expansion.sae import (SAE, CeilingExceeded, ExclusionViolation,
                               MutationPreflightViolation)
from src.expansion.nova import (NovaEngine, FermentationStatus, StoreFragment,
                                ProvenanceOverwriteViolation,
                                UngroundedEchoViolation,
                                UngroundedFragmentViolation)
from src.reflex.reflex_grid import ReflexGrid, UngatedReflexViolation
from src.reflex.sbsre import SBSRE, LoopOutcome
from src.identity.compass import ANCHOR_DRIFT_CAP, CompassStabilityEngine
from src.identity.ril import RIL
from src.identity.psi import PSI
from src.output.hail import HAIL
from src.output.ore import EXPRESSION_FOR_PATH, ORE, OutputPath
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.suspension.black_sphere import BlackSphere
from src.topology.tca_integration import TCAIntegration
from src.topology.tcaml import TCAML, LockReleaseViolation, StaleLockRelease
from src.utils.models import Echo, Scar, Doctrine
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import json


# =====================================================================
# RULING 25 (2026-07-25) - THE STRUCTURAL EXCEPTION TAXONOMY
# =====================================================================
# A STRUCTURAL violation means a gate that was supposed to be IMPOSSIBLE to
# pass was passed. Until this tuple existed, one `except Exception` flattened
# every deliberate guard this project has built into the same string as a
# malformed-input hiccup - the entire "raise, don't resolve; the wrong path
# must be unexecutable" discipline terminating in a string concatenation. A
# guard whose firing looks like a typo is not enforcement.
#
# CLOSED AND ENUMERATED - concrete types only, deliberately NOT a shared base
# class. A base class would silently widen this set the next time someone
# subclasses it, and the whole point is that membership here is a DECISION.
# Adding a new guard to the architecture means adding it to this tuple on
# purpose. Every member below is a raise this codebase makes deliberately:
#   CodexWriteViolation          doctrine written outside the collapse path
#   CeilingExceeded              self-mutation budget spent (§10.F)
#   ExclusionViolation           §10.G target, or AVT.017 empty lineage
#   MutationPreflightViolation   successor id unwritable (Ruling 24)
#   UngatedReflexViolation       an open non-GSR reflex registered (Ruling 10)
#   UngroundedEchoViolation      echo with no traceable origin (Nova G1)
#   UngroundedFragmentViolation  proposal material tracing to nothing (G3)
#   ProvenanceOverwriteViolation forensic record rewritten (Ruling 13)
#   LockReleaseViolation         GLOBAL lock released by a NEVER-holder (R29)
#   StaleLockRelease             GLOBAL lock TCAML revoked/expired out from
#                                under a blameless holder (R29)
#
# An ORDINARY exception (malformed input, an unexpected None) may still
# degrade gracefully into `errors`. That is correct and it stays. The taxonomy
# CUTS the two apart; it does not replace one with the other.
STRUCTURAL_VIOLATIONS = (
    CodexWriteViolation,
    CeilingExceeded,
    ExclusionViolation,
    MutationPreflightViolation,
    UngatedReflexViolation,
    UngroundedEchoViolation,
    UngroundedFragmentViolation,
    ProvenanceOverwriteViolation,
    # Ruling 27 / TCAML. Joined ON PURPOSE, as this tuple's own note requires.
    # RULING 29 (2026-07-26) SPLIT what was one type into two, because they are
    # CAUSALLY OPPOSITE: `LockReleaseViolation` blames the caller (it never
    # held the lock), `StaleLockRelease` absolves it (TCAML revoked or expired
    # the lock out from under it). Flattening them was Ruling 25's own defect
    # one level down - a forensic record that cannot say whether to go fix the
    # caller or go look at what destabilised the constellation. Both are
    # concrete types and NEITHER is a base class of the other.
    LockReleaseViolation,
    StaleLockRelease,
)


class SymbolicPressureMonitor:
    """Tracks system-wide pressure and coherence metrics."""
    
    def __init__(self):
        self.pressure_history = []
        self.coherence_history = []
        self.cascade_threshold = 0.85
        
    def record_pressure(self, source: str, level: float, metadata: Dict = None):
        """Record a pressure event."""
        self.pressure_history.append({
            'timestamp': datetime.now(),
            'source': source,
            'level': level,
            'metadata': metadata or {}
        })
        
        # Keep only recent history
        if len(self.pressure_history) > 100:
            self.pressure_history.pop(0)
            
    def get_system_pressure(self) -> float:
        """Calculate current system-wide pressure."""
        if not self.pressure_history:
            return 0.0
            
        recent = [p for p in self.pressure_history[-20:]
                 if (datetime.now() - p['timestamp']).seconds < 60]
        
        if not recent:
            return 0.0
            
        return sum(p['level'] for p in recent) / len(recent)
    
    def check_cascade_risk(self) -> bool:
        """Check if system is approaching cascade."""
        return self.get_system_pressure() > self.cascade_threshold


class AureaCore:
    """
    Central orchestrator for AUREA's collapse-bearing intelligence.
    Manages the complete pipeline from input to output.
    """

    # Ruling 25: the durable record of every structural violation. Resolved at
    # construction (the RBSystem.DEFAULT_LOG_PATH shape) so the suite can
    # REDIRECT it into tmp - there is deliberately no injectable no-op sink,
    # because a forensic log you can silently disable is not a forensic log.
    STRUCTURAL_LOG_PATH = "data/runtime/logs/structural_violations.jsonl"

    # Ruling 34 res.7: was a method-parameter default on save_state/load_state -
    # the ONE path shape `conftest.py` cannot reach, and it pointed outside
    # `data/runtime/`. A class attribute is reachable, and the target is now
    # runtime state rather than a stray untracked file at the repo root.
    STATE_PATH = "data/runtime/aurea_state.json"

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize AUREA core systems.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Ruling 25: the legible in-memory surface, its durable sink, and the
        # sink's own failure surface. Empty in a healthy system - a non-empty
        # `structural_violations` means one of AUREA's guards fired, which is
        # never routine and never an ordinary error.
        self.structural_violations: List[Dict[str, Any]] = []
        self.structural_log_path = Path(self.STRUCTURAL_LOG_PATH)
        self.structural_log_failures: List[Dict[str, Any]] = []

        # Initialize core modules
        self.spl = SPL()
        self.scar_core = ScarLogicCore()

        # Doctrine layer (Ruling 5): Codex owns the store, SAE is the sole executor,
        # the Spine is structure + requests. Nothing else may write doctrine.
        self.codex = Codex()
        self.doctrine_spine = DoctrineSpine(codex=self.codex)

        # TCAML (Ruling 27, Stage 2 - 2026-07-26): the topology layer's anchor
        # and lock owner, constructed HERE and threaded to every requester, so
        # the whole pipeline shares ONE lock. Built BEFORE the Grid because the
        # Grid hands it straight to RACM, which no longer has an "absent TCAML"
        # path to fall back on - the build-stage default-grant branch is gone.
        # Requesters, none of which hold lock or anchor state:
        #   RACM (via the Grid)  - GLOBAL two-phase lock, per claim
        #   CSE                  - anchor_feedback_update / realignment
        self.tcaml = TCAML()

        self.reflex_grid = ReflexGrid(tcaml=self.tcaml)

        # SAE (Ruling 5: the sole executor of self-mutation). Constructed AFTER
        # the Grid, and the ordering is load-bearing rather than cosmetic:
        # Ruling 34-A routes SAE's anti-deadlock surfacing through RACM, which
        # owns the route to the reflex behavior log (Ruling 1), and RACM does
        # not exist until the Grid builds it. The same shape as TCAML above -
        # build the owner first, then hand it to the requester.
        #
        # SAE RESUMES ITS EPOCH FROM DISK AT CONSTRUCTION (Ruling 34). A restart
        # no longer restores mutation budget: the ceiling, the unsettled
        # lineages and the stasis clock all cross the process boundary.
        self.sae = SAE(codex=self.codex, racm=self.reflex_grid.racm)

        # SML (Ruling 37): the DECAY OWNER, and the sender that finally makes an
        # epoch closeable. Constructed after SAE because it EMITS to it - SML
        # calls `stabilization_event`; SAE never polls SML, because the
        # budget-holder must not be the judge of its own debts (Ruling 37 (5)).
        self.sml = SML(scar_core=self.scar_core, sae=self.sae)

        self.ore = ORE()
        # Ruling 33 Stage 2. ORE resolves the verdict; HAIL renders it. HAIL is
        # a PURE FUNCTION - it takes no arguments here because it holds nothing
        # (no store, no ORE, no core). If you ever find yourself passing it a
        # reference, the ruling has already been broken.
        self.hail = HAIL()

        # Initialize suspension systems
        self.csa = CSA()
        self.veiled_thread = VeiledThread()
        self.black_sphere = BlackSphere()
        
        # Initialize Topological Constellation Architecture
        self.tca = TCAIntegration()

        # Nova (Ruling 12): the doctrine AUTHOR, constructed and owned here.
        # Sole writer of `echo_index` (G4, scanned by the Ruling-1 invariant);
        # everything else it wants is a REQUEST list or a return value.
        #
        # SUPERSEDED 2026-07-24 (Stage 2b): this comment used to say "ZERO
        # MUTATION RISK in 2a: the `proposals` seam below stays None, so
        # nothing Nova holds can reach SAE". THE SEAM IS WIRED - see
        # `_nova_proposals` and `_evolve_doctrine`. Doctrine mutation is now
        # STRUCTURALLY POSSIBLE, gated by DEE's five CMTE criteria and SAE's
        # Self-Mutation Ceiling rather than by an unconnected argument. (The
        # rest of the superseded sentence, verbatim: "doctrine mutation remains
        # structurally impossible until 2b opens that path.")
        #
        # Compass EAST reads this engine live (below), and it cycles once per
        # pipeline pass (see _nova_cycle).
        self.nova = NovaEngine()
        # Ruling 14: G2's guarantee is CHECKED here, not assumed. A proposal
        # whose backing echo is not MUTATED-and-scar-linked is a G2 BREACH -
        # it lands on this legible surface and denies echo_origin. It never
        # raises into the pipeline: an observer that can halt a safety path
        # is not an observer (Ruling 11's principle). Empty in a healthy system.
        self.nova_gate_breaches: List[Dict[str, Any]] = []
        # Stage 2b: collapse-routing / request-consumer errors land here and
        # are swallowed. The observer never gates the observed (Ruling 11) -
        # a filtration hiccup must not be able to halt the pipeline.
        self.nova_collapse_failures: List[Dict[str, Any]] = []

        # ---- THE COLLAPSE SPINE ----------------------------------------------
        # CSE: orientation. Holds NO anchor store - it derives N/S/E/W from the modules that
        # already own them (Codex · Scar Core · Nova · Black Sphere), so the compass cannot
        # disagree with reality. A compass that lies is worse than no compass.
        self.compass = CompassStabilityEngine(
            codex=self.codex,
            scar_core=self.scar_core,
            black_sphere=self.black_sphere,
            nova=self.nova,                # Stage 2a: EAST reads real Nova state - active_echoes()
            tcaml=self.tcaml,              # Stage 2: realignment requests reach a real owner
            reflex_grid=self.reflex_grid,
        )
        # SBSRE: the contradiction chamber. Bounded by Ruling 4's clamp; carries what
        # cannot yet be resolved instead of forcing a verdict.
        self.sbsre = SBSRE(
            reflex_grid=self.reflex_grid,
            csa=self.csa,
            scar_core=self.scar_core,          # SBSRE REQUESTS scars; the Core writes them
            resolver=self._echonet_resolver,   # coherence detection is EchoNet's job, not SBSRE's
        )
        # DEE: the eligibility gate. Decides IF doctrine may change; SAE decides nothing
        # about eligibility and DEE executes nothing about content.
        self.dee = DEE(
            codex=self.codex,
            sae=self.sae,
            veiled_thread=self.veiled_thread,
            reflex_grid=self.reflex_grid,
        )
        # RIL: the identity terminus. Accumulates the five identity threads from what
        # survives collapse (Ruling 1: RIL is the SOLE WRITER of `threads`). RIL only
        # reads Codex/ScarLogicCore/BlackSphere/CSA; it sources ICA through ReflexGrid
        # exactly as compass sources ANCHOR_COLLAPSE, and never arbitrates or locks.
        self.ril = RIL(
            codex=self.codex,
            scar_core=self.scar_core,
            black_sphere=self.black_sphere,
            csa=self.csa,
            reflex_grid=self.reflex_grid,
        )
        # PSI (Ruling 8): the Personal Scar Identity reflex. Registered HERE, not in
        # the Grid's argless _init_core_reflexes slot, because PSI needs the injected
        # RIL and scar-core handles the Grid does not hold. Registration is housing
        # only (Ruling 2) - rank comes from RACM's table ("PSI" -> 5), arbitration
        # stays RACM's, and PSI's output_blocked locks solely through the existing
        # reflex-agnostic Ruling-6 gate above. No PSI-specific consumer path exists:
        # its render directive stays parked until HAIL is built.
        self.psi = PSI(ril=self.ril, scar_core=self.scar_core)
        self.reflex_grid.add_reflex(self.psi)
        # ----------------------------------------------------------------------

        # Initialize EchoNet with connections
        self.echonet = EchoNet(
            scar_core=self.scar_core,
            doctrine_spine=self.doctrine_spine,
            reflex_grid=self.reflex_grid,
            compass=self.compass          # collapse thresholds tighten as orientation degrades
        )
        
        # Pressure monitoring
        self.pressure_monitor = SymbolicPressureMonitor()
        
        # Processing state
        self.processing_suspended = False
        self.suspension_reason = ""
        
        # Statistics
        self.stats = {
            'echoes_processed': 0,
            'scars_formed': 0,
            'reflexes_triggered': 0,
            'outputs_suppressed': 0,
            'cascades_prevented': 0,
            'contradictions_carried': 0,   # SBSRE threads run
            'doctrines_mutated': 0,        # DEE approvals executed by SAE
            'doctrines_fermenting': 0,     # eligible but unresolved - held open, not forced
            'structural_violations': 0,    # Ruling 25 - her own guards firing
        }
        
        # Initialize with seed doctrine if none exist
        if not self.codex.doctrines:
            self._create_seed_doctrines()
        self.codex.seal()   # genesis closed: from here, only collapse writes doctrine
        
        # Map existing doctrines to topological space
        for doctrine in self.codex.doctrines.values():
            self.tca.place_doctrine(doctrine)
    
    def _create_seed_doctrines(self):
        """Create foundational doctrines.

        The ONLY doctrine writes that did not survive collapse - because nothing had
        yet collapsed. `Codex.seal()` closes this window permanently.
        """
        seed_doctrines = [
            ("AVT.001", "Truth survives collapse"),
            ("AVT.002", "Scars shape future collapse"),
            ("AVT.003", "Contradiction without resolution is suspension"),
        ]
        
        for doc_id, name in seed_doctrines:
            doctrine = Doctrine(
                id=doc_id,
                name=name,
                created_at=datetime.now(),
                is_seed=True,
                description="Foundational doctrine"
            )
            self.codex.seed(doctrine)
            # Map to topological space
            self.tca.place_doctrine(doctrine)
    
    def process_input(self, raw_input: str, source: str = "user") -> Dict[str, Any]:
        """
        Process input through the complete AUREA pipeline.
        
        Args:
            raw_input: Raw text input
            source: Source identifier
            
        Returns:
            Dictionary containing processing results
        """
        result = {
            'input': raw_input,
            'echo': None,
            'collapse_result': None,
            'scar_formed': None,
            'reflex_responses': [],
            'output': None,
            'output_blocked': False,
            'pressure_generated': 0.0,
            'errors': [],
            # Ruling 33 Stage 2. `output` is now RENDERED, not concatenated, and
            # `output_blocked` is READ FROM THE PATH CONTRACT rather than set at
            # each site. These four carry what the render surface no longer can:
            # `truth_packet` holds everything ORE resolved (including the exact
            # string the pre-wiring pipeline would have printed, as `content`),
            # so nothing that used to be visible is lost - it moved from a
            # string into typed fields.
            'expression_verdict': None,
            'truth_packet': None,
            'render_trace': (),
            'reroute_hint': None,
        }

        # Check if processing is suspended
        if self.processing_suspended:
            return self._emit(
                result, OutputPath.PROCESSING_SUSPENDED,
                content=f"[SUSPENDED: {self.suspension_reason}]",
                unresolved=(f"processing_suspended: {self.suspension_reason}",),
            )

        # TCAML cycle advance (Ruling 27, Stage 2). One pipeline pass = one
        # TCAML cycle. Run FIRST, before anything can request a lock, for the
        # same reason expiry is checked first INSIDE tick(): a lock orphaned by
        # a previous pass must get its chance to expire before this pass's
        # GLOBAL requests are adjudicated against it. Ticking afterwards would
        # make the TTL bound one pass looser than the model states.
        #
        # This is also the ONLY thing that makes TTL reachable at all - without
        # a cycle advance the bound could never be crossed and the force-expiry
        # safety net would be decorative.
        self.tcaml.tick()

        # SAE symbolic-cycle advance (Ruling 34-A). Deliberately the SAME site as
        # tcaml.tick(): one pipeline pass is one symbolic cycle, and driving both
        # from one place is what stops the two clocks drifting apart. It closes
        # the accounting for the cycle just ended - a cycle in which every
        # mutation attempt was refused by a saturated epoch increments the stasis
        # count; a cycle in which one executed resets it.
        self.sae.advance_cycle()

        # SML symbolic-cycle advance (Ruling 37). THE SAME SITE, deliberately:
        # one pipeline pass is one symbolic cycle, and driving TCAML, SAE and
        # SML from a single place is what stops three clocks drifting apart.
        # This is the call that can close an epoch - a scar that has been quiet
        # for a full canon horizon cools out of ACTIVE, and if its lineage is
        # one SAE touched, SML emits the fermentation settle event.
        self.sml.advance_cycle()

        try:
            # Step 1: Perception layer
            echo = self.spl.process_input(raw_input, source)
            result['echo'] = echo
            self.stats['echoes_processed'] += 1
            
            # Step 1.5: Map echo to topological space
            echo_position = self.tca.calculate_collapse_location(echo)
            from src.topology.tca_core import NodeType
            echo_node = self.tca.topology.add_node(
                node_id=echo.id,
                node_type=NodeType.ECHO,
                position=echo_position,
                mass=1.0
            )
            echo_node.tags.add(f"source:{source}")
            
            # Step 2: Collapse testing with pressure generation
            collapse_result = self.echonet.filter_claim(echo)
            result['collapse_result'] = collapse_result
            result['pressure_generated'] = collapse_result.pressure_generated
            
            # Record pressure
            self.pressure_monitor.record_pressure(
                source='echonet',
                level=collapse_result.pressure_generated,
                metadata={'echo_id': echo.id}
            )
            
            # Step 2.5: ORIENTATION. Read the compass BEFORE deciding how long to carry a
            # contradiction - the leash length depends on whether she still knows which way
            # is up. Ruling 6: the output lock is the CONSEQUENCE of RACM authorizing a
            # reflex's suppress (keyed on ANCHOR_COLLAPSE, but any RACM-authorized
            # output_blocked locks) - never compass's own drift-past-line flag.
            reading = self.compass.read()
            result['compass'] = {
                'drift': round(reading.drift, 2),
                'stability': round(reading.stability, 3),
                'drift_past_lock_line': reading.drift_past_lock_line,
                'escalations': reading.escalations,
            }
            # reading.reflex_responses is the direct return of evaluate_pressure at compass's
            # own registration sites this read - never reflex_grid.last_arbitration, which is
            # a shared field, stale across cycles and clobbered same-cycle by the later
            # GSR/scar_density calls below (Steps 4-5).
            result['reflex_responses'].extend(reading.reflex_responses)

            # Ruling 37: the two compass-sourced halves of the settle contract.
            #
            # (a) DRIFT IS A DISTURBANCE. Past the canon cap the cycle is not
            #     quiet for ANY scar - drift is a system-wide reading, so there
            #     is no honest way to scope it. Delayed cooling holds the epoch
            #     closed, which is the side to err on.
            # (b) CONSOLIDATION IS OBSERVED, NEVER INDUCED (Ruling 15). CSE
            #     reports that stability returned and HELD; it steers nothing.
            if reading.drift > ANCHOR_DRIFT_CAP:
                self.sml.note_drift_event()
            result['consolidations'] = self.compass.observe_consolidation(
                reading, self.sae)

            arbitrated_lock = next(
                (r for r in reading.reflex_responses if r.output_blocked), None)
            if arbitrated_lock is not None:
                self.stats['outputs_suppressed'] += 1
                return self._emit(
                    result, OutputPath.ARBITRATED_OUTPUT_LOCK,
                    content=(
                        f"[OUTPUT LOCKED by {arbitrated_lock.reflex_id} - compass drift "
                        f"{reading.drift:.1f}°, RACM-authorized suppress. She does not speak "
                        f"while disoriented.]"),
                    collapse_verdict=collapse_result.verdict if collapse_result else None,
                    evidence_refs=(echo.id,),
                    unresolved=(f"output_lock:{arbitrated_lock.reflex_id}",
                                f"compass_drift:{reading.drift:.1f}"),
                )

            # Step 3: PARADOX leaves the pipeline entirely. It is not a contradiction to be
            # carried - it is one that CANNOT be carried. The Black Sphere is where AUREA keeps
            # what she cannot hold, without pretending to have resolved it.
            if collapse_result and not collapse_result.passed:
                # Routed on EchoNet's VERDICT, not on string-matching the input. The old code
                # looked for the literal phrases 'this statement' / 'i am lying', so any other
                # self-devouring claim ('nothing is true') was fed to the recursion chamber to
                # be ground on - when the chamber can never resolve it either.
                if collapse_result.verdict is EchoVerdict.PARADOX:
                    bs_entry = self.black_sphere.suspend(
                        content=echo.content,
                        source='pipeline',
                        pressure=collapse_result.pressure_generated,
                        reason=collapse_result.reason or 'Self-reference paradox',
                        paradox_type='self_reference'
                    )
                    # Map paradox to topological space
                    paradox_node = self.tca.place_paradox(bs_entry)
                    # Create edge from echo to paradox
                    self.tca.topology.create_edge(echo.id, bs_entry.id, weight=1.0)
                    return self._emit(
                        result, OutputPath.PARADOX_SUSPENDED,
                        content=f"[PARADOX SUSPENDED in Black Sphere: {bs_entry.id}]",
                        collapse_verdict=collapse_result.verdict,
                        evidence_refs=(echo.id,),
                        unresolved=(bs_entry.id,),
                    )

                # Step 3b: THE CONTRADICTION CHAMBER (SBSRE).
                #
                # Everything else that failed collapse testing is now CARRIED rather than
                # sorted straight into a bin by a pressure threshold. The old code decided a
                # contradiction's fate by a single number, in one pass. This carries it - for
                # as many cycles as Ruling 4's clamp allows, and not one more.
                #
                # This is the difference between a system that PROCESSES contradiction and one
                # that BEARS it.
                self._current_collapse = collapse_result
                thread = self.sbsre.process(
                    echo.content,
                    scar_weight=min(collapse_result.pressure_generated * 2.0, 5.0),
                    # REAL compass reading (CSE). This replaces a fabricated proxy
                    # (`1 - system_pressure`) that was a different quantity wearing the
                    # compass's name, and which silently drove every loop limit to the floor.
                    # Drift SHORTENS the leash: a system that does not know which way is up
                    # does not get more cycles to grind on a contradiction.
                    compass_stability=reading.stability,
                    reflex_load=1.0 + len(self.reflex_grid.racm.deferred),
                    compass_drift=reading.drift,
                    context={'echo_id': echo.id,
                             'collapse_pressure': collapse_result.pressure_generated},
                )
                self.stats['contradictions_carried'] += 1
                result['sbsre'] = {
                    'thread_id': thread.id,
                    'loop_limit': thread.loop_limit,
                    'cycles_carried': thread.cycles_run,
                    'outcome': thread.outcome.value,
                    'reason': thread.reason,
                    'exhausted': thread.exhausted,
                }

                # --- What the chamber decided ---
                if thread.outcome is LoopOutcome.COLLAPSE:
                    # The contradiction was PROVEN not to resolve. That is not a failure.
                    # That is a scar. SBSRE requested it; Scar Logic Core wrote it.
                    scar = self.scar_core.get_scar(thread.scar_id) if thread.scar_id else None
                    if scar is not None:
                        result['scar_formed'] = scar
                        self.stats['scars_formed'] += 1
                        # Ruling 37: a NEW scar on a lineage is a DISTURBANCE -
                        # the cycle is not quiet for anything that scar touches,
                        # and every affected count restarts. Fermentation
                        # interrupted is fermentation restarted.
                        self.sml.note_scar_formed(scar)
                        self.tca.place_scar(scar)
                        self.tca.topology.create_edge(
                            echo.id, scar.id, weight=collapse_result.pressure_generated)
                        # RIL: identity terminus. Every scar that survives to formation
                        # is what the identity threads accumulate (Scarline/Origin).
                        self.ril.ingest_scar(scar)

                elif thread.outcome in (LoopOutcome.ABORT, LoopOutcome.ROUTE):
                    # Carried to exhaustion without resolving. SBSRE has already stored the
                    # PARTIAL THREAD in CSA - the unfinished shape of the contradiction is
                    # what survives, and it is not discarded just because it did not close.
                    entry_id = getattr(thread.csa_entry, 'id', None)
                    return self._emit(
                        result, OutputPath.SBSRE_CARRIED,
                        content=(
                            f"[CARRIED {thread.cycles_run} cycles, unresolved - "
                            f"partial thread held in CSA: {entry_id}]"),
                        collapse_verdict=collapse_result.verdict,
                        evidence_refs=(echo.id, thread.id),
                        unresolved=tuple(x for x in (entry_id,) if x),
                    )

                elif thread.outcome is LoopOutcome.MIRROR:
                    # Whisper Reflex: speaking this would be symbolic betrayal. Reflect it back
                    # as unclaimed rather than assert something AUREA has not earned.
                    #
                    # UNREACHABLE TODAY, and deliberately left that way: MIRROR
                    # requires ctx["symbolic_betrayal"] (sbsre.py:290) and the
                    # context dict built above never sets it. Nothing in the
                    # tree emits that flag. The path is WIRED so it is correct
                    # the day a betrayal detector arrives; inventing a trigger
                    # for it here would be faking the condition, not building
                    # the consumer. Verified unreachable by dump, 2026-07-26.
                    return self._emit(
                        result, OutputPath.SBSRE_MIRRORED,
                        content=f"[MIRRORED - unclaimed contradiction: {echo.content}]",
                        collapse_verdict=collapse_result.verdict,
                    )
            
            # Step 4: Check for cascade risk
            if self.pressure_monitor.check_cascade_risk():
                # Trigger GSR for cascade prevention
                gsr_responses = self.reflex_grid.evaluate_pressure(
                    source_module='aurea_core',
                    pressure_type='cascade_warning',
                    pressure_level=0.9,
                    metadata={
                        'system_pressure': self.pressure_monitor.get_system_pressure(),
                        'echo_id': echo.id
                    }
                )
                result['reflex_responses'].extend(gsr_responses)
                self.stats['cascades_prevented'] += 1
            
            # Step 5: Scar pressure -> reflexes.  (Scar FORMATION now happens in the
            # contradiction chamber above: a scar is what a carried contradiction leaves
            # behind when it will not resolve - not an automatic byproduct of a failed filter.)
            if result['scar_formed'] is not None:
                active_scars = len(self.scar_core.get_active_scars())
                if active_scars > 50:
                    # High scar density triggers reflexes
                    density_responses = self.reflex_grid.evaluate_pressure(
                        source_module='scar_core',
                        pressure_type='scar_density',
                        pressure_level=min(active_scars / 100, 1.0),
                        metadata={'active_scars': active_scars}
                    )
                    result['reflex_responses'].extend(density_responses)

            # Step 5a.5: NOVA. Cycle Nova ONCE here, AFTER all reflex
            # arbitration this pass (compass-read Step 2.5 + GSR cascade Step 4 +
            # scar-density Step 5 have all appended their RACM-authorized returns
            # to result['reflex_responses']) and BEFORE _evolve_doctrine (so the
            # echo state Docket C reads is current). Ferment + erupt only -
            # THIS step never proposes. (Superseded 2026-07-24: the rest of
            # this line used to read "proposals stays None in _evolve_doctrine
            # (2a boundary)". It does not; `_evolve_doctrine` passes
            # `_nova_proposals(signals)`. What remains true is the SCOPE of
            # this step - proposals are emitted there, not here.)
            self._nova_cycle(result['reflex_responses'])

            # Step 5b: DOCTRINE EVOLUTION. A new scar is pressure on everything it touches.
            # DEE gates; SAE executes; the Codex records. This orchestrator does none of those.
            result['doctrine'] = self._evolve_doctrine(result, collapse_result)
            
            # Step 6: Check reflex responses for output blocking.
            #
            # The loop's side effects are UNCHANGED (one `outputs_suppressed`
            # per blocking response; cascade still suspends). What moved is the
            # emission: it now happens ONCE, after the loop, through the same
            # contract every other exit uses. LAST blocking response wins,
            # exactly as the pre-wiring loop's overwrite did.
            blocking = None
            for response in result['reflex_responses']:
                if response.output_blocked:
                    blocking = response
                    self.stats['outputs_suppressed'] += 1

                if response.action == 'cascade':
                    # System-wide suspension
                    self.processing_suspended = True
                    self.suspension_reason = response.message

            if blocking is not None:
                self._emit(
                    result, OutputPath.REFLEX_BLOCKED,
                    content=f"[BLOCKED by {blocking.reflex_id}]",
                    collapse_verdict=collapse_result.verdict if collapse_result else None,
                    evidence_refs=(echo.id,),
                    unresolved=(f"blocked_by:{blocking.reflex_id}",),
                )

            # Step 7: Generate output if not blocked.
            #
            # RULING 33 STAGE 2: this was the placeholder Step 7 the ruling
            # named - two f-strings gated by one boolean, with no verdict
            # concept anywhere. The TEXT is unchanged (it is now the packet's
            # `content`); what is new is that ORE decides the expression verdict
            # and HAIL renders it, so Ruling 3's truth-effect cut finally has a
            # runtime surface instead of being a scanned-for invariant.
            #
            # The speaking packets carry CONTENT ONLY - no evidence_refs, no
            # scar_lineage. That is deliberate for this stage: EXPERT mode
            # appends a line per populated field, so filling them would change
            # the spoken surface, and enriching what she says is a separate
            # decision from rewiring how she says it. The fields are there the
            # day someone rules on the surface.
            if not result['output_blocked']:
                if collapse_result.passed:
                    path = OutputPath.COLLAPSE_PASSED
                    content = f"Echo processed: {echo.content}"
                else:
                    path = OutputPath.COLLAPSE_DETECTED
                    content = f"Collapse detected: {collapse_result.reason}"

                # Add pressure indicator
                if collapse_result.pressure_generated > 0.5:
                    content += f" [Pressure: {collapse_result.pressure_generated:.2f}]"

                self._emit(result, path, content=content,
                           collapse_verdict=collapse_result.verdict)


            # Step 8: Update statistics
            if result['reflex_responses']:
                self.stats['reflexes_triggered'] += len(result['reflex_responses'])
                
        except STRUCTURAL_VIOLATIONS as violation:
            # RULING 25: one of AUREA's OWN guards fired. This is not an error
            # to report and speak past - it means a path the architecture makes
            # unexecutable was executed anyway. It gets its own loud field (NOT
            # merged into `errors`), suppressed output (she does not answer as
            # though nothing happened when her own guard just fired), and a
            # durable record. It does NOT crash the process: that would destroy
            # the record, and the record is the point. Fail toward legible
            # refusal - never toward silent corruption, never toward a fluent
            # answer.
            self._record_structural_violation(result, violation, raw_input, source)
        except Exception as e:
            # ORDINARY failure: malformed input, an unexpected None. Graceful
            # degradation is correct here and is unchanged. Ordered AFTER the
            # structural clause on purpose - widening this one back over the
            # other is the regression Ruling 25 exists to prevent.
            result['errors'].append(str(e))
            self._emit(
                result, OutputPath.ORDINARY_ERROR,
                content=f"[ERROR: {str(e)}]",
                # If EchoNet ran before the failure its verdict is real and is
                # reported; if it did not, None is the honest answer and NOT a
                # placeholder. Coining a verdict for a path where nothing was
                # filtered is fabricating truth content (Ruling 33 (1)).
                collapse_verdict=getattr(result.get('collapse_result'), 'verdict', None),
            )

        return result

    # =================================================================
    # RULING 33 STAGE 2 - the ONE way this pipeline produces output
    # =================================================================

    def _emit(self, result: Dict[str, Any], path: OutputPath, content: str, *,
              collapse_verdict: Any = None,
              evidence_refs: tuple = (),
              scar_lineage: tuple = (),
              unresolved: tuple = ()) -> Dict[str, Any]:
        """Resolve this exit through ORE, render it through HAIL, record both.

        EVERY output path in `process_input` goes through here. That is the
        point: before Ruling 33 the expression decision was ten scattered
        f-strings and ten scattered `output_blocked = True` assignments, and
        nothing checked that the two agreed. Now the PATH CONTRACT
        (`EXPRESSION_FOR_PATH`) is the single source of both, so a verdict and
        a blocked flag CANNOT disagree - there is only one of them.

        `output_blocked` is read from the contract, NEVER passed in. A caller
        that could set it independently would be the scattered-booleans defect
        with an extra step.

        THE MODE IS NOT SELECTABLE HERE, deliberately. HAIL's default is EXPERT
        (full collapse-bearing output). Choosing a mode per pass needs a CPA
        user profile, which does not exist; picking one on any other basis
        would be inventing the calibration input. v1 renders one way.

        WHAT THE SILENT VERDICTS DO TO THE SURFACE, stated because it is the
        biggest observable change of this stage: WITHHOLD and SUSPEND render a
        FIXED string that contains none of `content`. The diagnostics that used
        to be inside the output string (the Black Sphere id, the CSA entry, the
        blocking reflex, the violation type) are still here - in
        `result['truth_packet']`, whose `content` field holds the pre-wiring
        string verbatim and whose `unresolved` holds the ids. Nothing was lost;
        it stopped being SPOKEN. That is the ruling working, not a regression.
        """
        packet = self.ore.resolve_path(
            path,
            content=content,
            collapse_verdict=collapse_verdict,
            evidence_refs=evidence_refs,
            scar_lineage=scar_lineage,
            unresolved=unresolved,
            # Ruling 8's promise landing: PSI's directive stops being
            # caller-less. It is read from the ACCUMULATED, RACM-AUTHORIZED
            # responses of this pass - never from a reflex object, never from
            # last_arbitration (shared, stale across cycles).
            psi_directive=self._psi_directive(result['reflex_responses']),
        )
        rendered = self.hail.render(packet)

        result['output'] = rendered.text
        result['output_blocked'] = EXPRESSION_FOR_PATH[path].output_blocked
        result['expression_verdict'] = packet.expression_verdict
        result['truth_packet'] = packet
        result['render_trace'] = rendered.render_trace
        result['reroute_hint'] = rendered.reroute_hint
        return result

    @staticmethod
    def _psi_directive(responses: List[Any]) -> Any:
        """The first grounded PSI directive among this pass's responses, or None.

        PSI is the only emitter today and emits at most one per pass, so FIRST
        is unambiguous. If a second emitter ever appears, first-wins stays
        DETERMINISTIC - and merging two directives would be a tone decision
        nobody has ruled, so it is not done here.

        PSI abstains rather than guessing a bearing (Ruling 8), so `None` here
        means "no grounded scar bearing existed", not "nobody looked".
        """
        for response in responses:
            directive = (getattr(response, 'metadata', None) or {}).get('psi_directive')
            if directive is not None:
                return directive
        return None

    def _record_structural_violation(self, result: Dict[str, Any],
                                     violation: BaseException,
                                     raw_input: str, source: str) -> None:
        """Ruling 25: the loud field, the suppressed output, the durable record."""
        entry = {
            'type': type(violation).__name__,
            'message': str(violation),
            'input': raw_input,
            'source': source,
            'timestamp': datetime.now().isoformat(),
        }
        result['structural_violation'] = entry
        # RULING 33 (6), verbatim: structural-violation output maps to WITHHOLD
        # "with the violation carried in `unresolved` - her guard firing is
        # truth content, not a rendering choice." So the violation now rides in
        # the PACKET rather than in the spoken string. Ruling 25 is untouched
        # and its three requirements all still hold: the loud field above,
        # suppressed output (WITHHOLD suppresses harder than the old string
        # did), and the durable record below.
        self._emit(
            result, OutputPath.STRUCTURAL_VIOLATION,
            content=(
                f"[STRUCTURAL VIOLATION - {entry['type']}: {entry['message']} "
                f"AUREA does not answer past her own guard.]"),
            collapse_verdict=getattr(result.get('collapse_result'), 'verdict', None),
            unresolved=(f"{entry['type']}: {entry['message']}",),
        )
        self.stats['outputs_suppressed'] += 1
        self.stats['structural_violations'] += 1
        self.structural_violations.append(entry)
        self._flush_structural_violation(entry)

    def _flush_structural_violation(self, entry: Dict[str, Any]) -> None:
        """Best-effort durable append. NEVER raises (Ruling 11's principle,
        third application): a logging failure must not be able to convert a
        legible refusal into a crash. A failed write lands on
        `structural_log_failures` and the in-memory record still stands."""
        try:
            self.structural_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.structural_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as exc:
            self.structural_log_failures.append({
                'error': f"{type(exc).__name__}: {exc}",
                'entry_type': entry.get('type'),
                'timestamp': datetime.now().isoformat(),
            })
    
    def _echonet_resolver(self, contradiction, cycle):
        """SBSRE's coherence check. Delegated to EchoNet's VERDICT - never guessed.

        SBSRE must not decide for itself whether a contradiction has resolved; that is
        EchoNet's job, and a recursion engine that scores its own homework will always find
        a reason to stop looping. So this reads the verdict and nothing else:

            CONFIRMED  -> "emerge"          coherence found under pressure
            SCARRED    -> "irreconcilable"  EchoNet has already proven it collapses. It scars.
            SUSPENDED  -> None              NOT YET. Keep carrying it.

        `None` is the important return. It means the contradiction is still open, and the
        loop keeps holding it - for exactly as many cycles as Ruling 4's clamp allows, and
        no more. Ambiguity is carried, not rounded off.

        HISTORY (do not repeat): an earlier draft used `pressure > 0.9` as the collapse
        condition. That number was mine, not the corpus's - and it silently made the COLLAPSE
        outcome UNREACHABLE, because the only claims that clear 0.9 are paradoxes, and
        paradoxes are diverted to the Black Sphere before they ever reach this chamber.
        AUREA could not form a scar. The whole architecture ran, and nothing left a mark on
        her. The verdict is authoritative precisely so that no invented threshold can quietly
        sever the scar path again.
        """
        collapse = getattr(self, '_current_collapse', None)
        if collapse is None:
            return None
        if collapse.verdict is EchoVerdict.CONFIRMED:
            return "emerge"
        if collapse.verdict is EchoVerdict.SCARRED:
            return "irreconcilable"
        return None    # SUSPENDED: unresolved is not the same as refuted. Carry it.

    def _nova_cycle(self, reflex_responses: List[Any]) -> None:
        """One fermentation-and-eruption pass. Nova proposes NOTHING in here.

        Nova ferments its echoes and may erupt new ones; it NEVER proposes AT
        THIS STEP - and that is a statement about this method's scope, verified
        against the call graph: `_nova_cycle` calls `nova.cycle()` and the
        eruption helper, and never `nova.proposals()`. Emission happens in
        `_evolve_doctrine`, via `_nova_proposals`.

        SUPERSEDED 2026-07-24 (Stage 2b): the parenthetical here used to read
        "(proposals stays None in _evolve_doctrine)". That is FALSE now - the
        seam is wired and doctrine mutation is structurally possible. The
        method's own guarantee is unchanged; only the claim about its
        neighbour was stale.

        G5 first: if expansion is
        under an authorized suspension this cycle, cycle() records its own
        refusal and advances nothing, and we skip eruption too - deference is
        total, not cosmetic.
        """
        suppressed = self._nova_suppressed(reflex_responses)
        eligible = self.nova.cycle(suppressed=suppressed, source='aurea_core')
        if suppressed:
            return
        self._nova_erupt_from_doctrine_strain()
        self._nova_route_collapse(eligible)
        self._nova_consume_requests()

    def _nova_suppressed(self, reflex_responses: List[Any]) -> bool:
        """G5 suppression read (STEP 3) - the honest one, NOT output_blocked.

        `output_blocked` means "she does not speak" - a RENDER state. Nova's
        deference is about EXPANSION being halted. Different conditions;
        conflating them is the convenient-flag error. GSR's high-pressure
        suspend targets ["expansion","nova"] with output_blocked=FALSE - the
        exact case a render-flag read would miss.

        Honest surface: a RACM-AUTHORIZED response this cycle whose effect is a
        suspension AND whose target_modules name nova / expansion / all.
        `reflex_responses` is result['reflex_responses'] - the accumulated
        DIRECT returns of evaluate_pressure (compass-read + GSR + scar-density),
        every entry already RACM-authorized by construction (the Grid returns
        only what RACM executed, Ruling 9). NEVER last_arbitration (shared,
        stale, clobbered same-cycle - the same discipline the Ruling-6 gate
        keeps). "cascade" is GSR's system-wide SUSPEND decomposition (Ruling 7,
        target ["all"]); "suspend" is its selective halt (target
        ["expansion","nova"]).
        """
        halt_targets = {"nova", "expansion", "all"}
        for r in reflex_responses:
            if getattr(r, 'action', None) in ("suspend", "cascade") \
                    and halt_targets & set(getattr(r, 'target_modules', []) or []):
                return True
        return False

    def _nova_erupt_from_doctrine_strain(self) -> None:
        """STEP 4 eruption - ONE wired source: doctrine strain from DEE's watch.

        DEE's DMW queue (`self.dee.dmw.queue`) holds one slot per doctrine under
        SUSTAINED, DEE-admitted strain, persisting across cycles. Each key is a
        real Codex doctrine id; the slot is a real strain record - so an echo
        erupted from it traces to something survived (G1: origin_kind
        "doctrine_strain", origin_id the doctrine id; the constructor raises on
        a bad one - no fabricated id here). scar_links come from the doctrine's
        OWN real scar links, nothing invented.

        Minimal dedup: at most one live echo per strained doctrine (checked
        against the index by origin) - a doctrine strained for N cycles yields
        one echo, not N. The full Nova Echo Crosscheck (5a:82) is NOT-YET-WIRED.
        EchoNet filtration residue, CSA fragments, and scar-conflict eruption
        (all built and available) are ALSO NOT-YET-WIRED sources - re-verified
        2026-07-27 and still accurate: exactly ONE eruption source is wired,
        honestly, per the contract. (Nova's collapse ROUTING was wired at
        Stage 2b; that is a different seam - it reports outcomes, it does not
        erupt echoes.)
        """
        existing = {(e.origin_kind, e.origin_id)
                    for e in self.nova.echo_index.values()}
        for doctrine_id in list(self.dee.dmw.queue):
            if ("doctrine_strain", doctrine_id) in existing:
                continue
            doctrine = self.codex.get(doctrine_id)
            if doctrine is None:
                continue                      # released/expired mid-cycle; nothing real to trace
            self.nova.erupt(
                origin_kind="doctrine_strain",
                origin_id=doctrine_id,
                scar_links=list(doctrine.scar_links),
            )

    def _nova_route_collapse(self, eligible_ids: List[str]) -> None:
        """STEP 2 (Stage 2b): route REAL collapse outcomes into
        record_collapse_result - the ONLY writer of MUTATED.

        Echo Protocol III.4: "Echo is run through EchoNet for filtration."
        An eligible echo names a STRAIN on a doctrine, so the collapse attempt
        puts that strain to the test by filtering the strained doctrine's OWN
        stated content (real Codex material) through EchoNet - the canonical
        filtration path. No resolver is invented, and `filter_claim` is pure:
        it writes nothing and mints no scars (scar formation is EchoNet's
        separate opt-in `collapse_test`, deliberately NOT called here - a
        probe that manufactured permanent records would be worse than none).

        Verdict -> outcome, on canon's own meanings (Lexicon I.3):
          SCARRED   "collapsed -> Collapse Archive" - the belief FAILED
                    filtration, so its fracture is real and visible: the
                    strain SURVIVED -> success=True -> MUTATED.
          CONFIRMED "survived collapse" - the belief still holds, so the
                    strain did NOT survive -> success=False -> DECAYING +
                    the parked CSA request, carrying the real pressure.
          SUSPENDED "unresolved -> Veiled Thread. NOT a failure."
          PARADOX   "cannot be held at all -> Black Sphere"
                    -> NO record either way. Unresolved is not refuted; the
                    echo is CARRIED and may face collapse again. Recording
                    these as failure would resolve by fiat what has not
                    resolved - the one thing this system exists not to do.

        A routing error is recorded and swallowed: the observer never gates
        the observed (Ruling 11's principle).
        """
        for echo_id in eligible_ids:
            try:
                echo = self.nova.echo_index.get(echo_id)
                if echo is None or echo.origin_kind != "doctrine_strain":
                    # v1 holds filtration material only for doctrine strain -
                    # the other origin kinds are NOT-YET-ROUTED, not assumed.
                    continue
                doctrine = self.codex.get(echo.origin_id)
                content = (doctrine.description or doctrine.name) if doctrine else ""
                if not content:
                    continue                   # nothing real to filter; no fabricated probe
                probe = Echo(
                    id=f"nova-collapse-{echo.id}",
                    content=content,
                    source="nova",
                    # Inert: EchoNet's verdict is content-driven and never
                    # reads this field (SPL sets the same documented
                    # placeholder). No magnitude enters the truth path here.
                    resonance_score=1.0,
                    created_at=datetime.now(),
                    doctrine_link=doctrine.id,
                )
                outcome = self.echonet.filter_claim(probe)
                if outcome.verdict is EchoVerdict.SCARRED:
                    self.nova.record_collapse_result(
                        echo.id, success=True,
                        detail=f"EchoNet SCARRED on {doctrine.id}: {outcome.reason}")
                elif outcome.verdict is EchoVerdict.CONFIRMED:
                    self.nova.record_collapse_result(
                        echo.id, success=False,
                        detail=f"EchoNet CONFIRMED {doctrine.id} - strain did not survive",
                        pressure=outcome.pressure_generated)
                # SUSPENDED / PARADOX: deliberately no record. Carried.
            except Exception as exc:
                self.nova_collapse_failures.append({
                    'echo_id': echo_id,
                    'error': f"{type(exc).__name__}: {exc}",
                    'timestamp': datetime.now().isoformat(),
                })

    def _nova_consume_requests(self) -> None:
        """STEP 4 (Stage 2b): consumers for Nova's parked request lists.

        Ruling 1: Nova never writes another module's store - it asks, and the
        OWNER executes. csa_requests -> CSA (wired here).

        scar_requests -> ScarLogicCore: RE-PARKED, not forced. `form_scar`
        needs a `weight`, and scar weight/decay is SML's store, not Nova's
        (Ruling 1 ownership table) - Nova supplying one would write into a
        domain it does not own. Worse, minting a NEW scar for every mutated
        echo would MANUFACTURE permanent records, and "scar fused" (5a:1123)
        plausibly means fusing into the scars the echo ALREADY links, which
        the corpus does not specify. Escalated in the session report rather
        than guessed. The requests accumulate legibly on `nova.scar_requests`
        until that is ruled.
        """
        while self.nova.csa_requests:
            request = self.nova.csa_requests.pop(0)
            try:
                echo = self.nova.echo_index.get(request.get('echo_id'))
                pressure = request.get('pressure')
                self.csa.suspend(
                    content={
                        'echo_id': request.get('echo_id'),
                        'origin_kind': getattr(echo, 'origin_kind', None),
                        'origin_id': getattr(echo, 'origin_id', None),
                        'status': getattr(getattr(echo, 'status', None), 'value', None),
                    },
                    source='nova',
                    # The real pressure of the collapse that failed. Absent =
                    # unrecorded -> 0.0, the lowest quarantine: the
                    # uninformative case is the conservative case, and a
                    # consumer must never invent a magnitude.
                    pressure=float(pressure) if pressure is not None else 0.0,
                    reason=request.get('reason', ''),
                )
            except Exception as exc:
                self.nova_collapse_failures.append({
                    'echo_id': request.get('echo_id'),
                    'error': f"CSA consume failed: {type(exc).__name__}: {exc}",
                    'timestamp': datetime.now().isoformat(),
                })

    def _nova_proposals(self, signals: Dict[str, Dict[str, Any]]
                        ) -> Optional[Dict[str, Doctrine]]:
        """STEP 3 (Stage 2b): THE SEAM. Nova's proposals for DEE's gate.

        Returns None when nothing has survived to propose - which is the
        common case and the CORRECT one: DEE then ferments eligible doctrines
        rather than mutating them, exactly as before this stage. Opening this
        path does not license making it fire.

        G3: every fragment is store-traceable, and the strained doctrine's OWN
        record is REQUIRED (Nova refuses the proposal otherwise). Material
        comes from the Codex doctrine and the real scars the echo links -
        nothing authored here, no generative model anywhere near it.
        """
        qualifying = [e for e in self.nova.echo_index.values()
                      if e.status is FermentationStatus.MUTATED
                      and e.scar_links and not e.is_spent]
        if not qualifying:
            return None

        fragments: Dict[str, List[StoreFragment]] = {}
        for echo in qualifying:
            if echo.origin_kind != "doctrine_strain":
                continue          # only a doctrine-strain echo names its target doctrine
            doctrine_id = echo.origin_id
            if doctrine_id not in signals or doctrine_id in fragments:
                continue
            doctrine = self.codex.get(doctrine_id)
            if doctrine is None:
                continue
            frags = [StoreFragment(
                store="doctrines", record_id=doctrine_id,
                content=doctrine.description or doctrine.name)]
            for scar_id in echo.scar_links:
                scar = self.scar_core.get_scar(scar_id)
                if scar is not None:
                    frags.append(StoreFragment(
                        store="scars", record_id=scar_id,
                        content=scar.description or scar.name))
            fragments[doctrine_id] = frags

        if not fragments:
            return None
        return self.nova.proposals(fragments) or None

    def _backing_echo(self, proposal: Doctrine):
        """The echo RECORDED AS AUTHORING this proposal, or None.

        Source: Nova's `proposal_provenance` - the APPEND-ONLY forensic record
        of authorship (Ruling 13), guarded by ProvenanceOverwriteViolation.
        Chosen over the proposal's own `mutation_lineage` because that is an
        ordinary dataclass field any future author (DBE, a Spine request)
        could set, whereas provenance is Nova's protected record of what
        actually went into the emission. A proposal authored by something
        other than Nova has no entry here, so it backs no echo_origin claim -
        which is correct: echo_origin means a NOVA echo survived.
        """
        for entry in self.nova.proposal_provenance.get(proposal.id, []):
            if entry.get("store") == "nova_echo_index":
                return self.nova.echo_index.get(entry.get("record_id"))
        return None

    def _echo_origin(self, doctrine_id: str, proposals: Dict[str, Doctrine]) -> bool:
        """RULING 14: True iff a PROPOSAL for `doctrine_id` exists AND the echo
        recorded as authoring it is MUTATED and scar-linked.

        This is the gate that decides whether a SCAR-LESS belief may evolve
        (CMTE criterion 2 is an OR, so echo_origin is load-bearing only there).
        It therefore demands a SURVIVED echo, not merely an existing one.

        G2's guarantee is CHECKED, not assumed. Nova's proposals() is supposed
        to emit only MUTATED + scar-linked echoes; if a proposal ever reaches
        here backed by an echo that is neither, that is a G2 BREACH. It is
        recorded legibly on `nova_gate_breaches` and DENIES echo_origin - it
        never raises, because this observer must not be able to halt the
        pipeline it observes (Ruling 11's principle).
        """
        proposal = proposals.get(doctrine_id)
        if proposal is None:
            return False

        echo = self._backing_echo(proposal)
        if echo is None:
            self._record_gate_breach(
                doctrine_id, proposal.id, None,
                "proposal has no recorded authoring echo - dangling provenance")
            return False
        if echo.status is not FermentationStatus.MUTATED:
            self._record_gate_breach(
                doctrine_id, proposal.id, echo.id,
                f"G2 breach: backing echo is {echo.status.value}, not MUTATED "
                f"- an unverified echo may not write doctrine")
            return False
        if not echo.scar_links:
            self._record_gate_breach(
                doctrine_id, proposal.id, echo.id,
                "G2 breach: backing echo carries no scar linkage - the "
                "fracture that broke this belief cannot be seen")
            return False
        return True

    def _record_gate_breach(self, doctrine_id: str, proposal_id: str,
                            echo_id: Optional[str], reason: str) -> None:
        """Legible surface for a Ruling-14/G2 breach. Never raises."""
        self.nova_gate_breaches.append({
            'doctrine_id': doctrine_id,
            'proposal_id': proposal_id,
            'echo_id': echo_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
        })

    def _evolve_doctrine(self, result: Dict[str, Any], collapse_result) -> Dict[str, Any]:
        """Run one DEE evolution pass. The orchestrator gates nothing and writes nothing.

        A fresh scar is pressure on every doctrine it touches. DEE scans, holds, validates;
        SAE executes; the Codex records. AureaCore's only job here is to hand DEE the
        pressure signals and report what it decided.

        NOTE (Stage 2b, corrects the Stage-2a note this superseded): `proposals`
        IS passed below, via `_nova_proposals(signals)` - the seam commented
        inline at "THE SEAM. This is the line that makes doctrine mutation
        possible." Doctrine mutation is no longer structurally impossible.
        What stands between pressure and a changed belief now is DEE's five
        CMTE criteria and SAE's Self-Mutation Ceiling - not the absence of a
        proposal. An eligible doctrine with no qualifying Nova proposal, or
        one that fails any CMTE criterion, still FERMENTS rather than
        mutating - that remains correct behavior, not a gap: AUREA does not
        get to invent what she becomes just because pressure demands that
        she become something.
        """
        report: Dict[str, Any] = {'rulings': [], 'mutated': 0, 'fermenting': 0}

        scar = result.get('scar_formed')
        if scar is None:
            return report

        # Pressure signals: which doctrines does this scar bear on?
        signals: Dict[str, Dict[str, Any]] = {}
        pressure = float(getattr(collapse_result, 'pressure_generated', 0.0))
        # RULING 38 (2026-07-27): `active()`, NOT `view()`. The Ruling 35
        # principle applied to its last unreviewed consumer - the Codex owns
        # what LIVE-AND-MUTABLE means, and a builder that admits locked ids is a
        # second definition of eligibility drifting from the first.
        #
        # This closes the WASTE (dead signal entries for a locked doctrine that
        # DRPAS, scanning `active()`, never looked up) and - the part that
        # matters - the GATE: `_nova_proposals` uses `doctrine_id not in
        # signals` as a membership check, so a locked doctrine can no longer
        # ENTER the proposal path, INDEPENDENT of whether DRPAS upstream ever
        # flags it. Defence in depth is the point, not the dead entry: the
        # defect between two gates is nobody's defect until it is everybody's
        # incident.
        for doctrine in self.codex.active():
            touched = bool(set(doctrine.scar_links) & {scar.id}) or \
                      bool(set(scar.linked_doctrines or []) & {doctrine.id})
            signals[doctrine.id] = {
                'pressure': pressure if touched else pressure * 0.5,
                'drpe': touched,
                'scar_bloom': len(doctrine.scar_links) >= 3,
            }

        # Docket C (Stage 2a): `echo_origin` is DERIVED from real Nova state,
        # never a literal - in EITHER direction. The original hardcode
        # ({'echo_origin': True} for every doctrine) claimed falsely that a
        # Nova echo underwrote every doctrine; a hardcoded False would be the
        # same shape with the opposite sign, honest only until proposals
        # arrive. It is computed, every pass, from what actually exists.
        #
        # RULING 14 (2026-07-23) supersedes Stage 2a's v1 bearing rule.
        # `echo_origin[d]` is True iff a PROPOSAL for d exists AND the echo
        # recorded as authoring it is MUTATED and scar-linked. NOT "an echo
        # bears on d": a doctrine-strain echo of a scar-less doctrine is
        # scar-less by construction, so it could never author a proposal -
        # yet the v1 rule would have granted eligibility for one. And a
        # scar-less doctrine's own strain is not a fracture.
        #
        # `echo_resonance` is NOT supplied: no real resonance value exists in
        # the organ (Echo Protocol IV's scores are deliberately un-coined),
        # and criterion 3's absent-reads-as-pass semantics stay DEE's own.
        # STAGE 2b STEP 3 - THE SEAM. This is the line that makes doctrine
        # mutation possible: from here, DEE's five CMTE criteria and SAE's
        # Self-Mutation Ceiling are the only things between pressure and a
        # changed belief. No sixth gate was added; none of the five removed.
        # `_nova_proposals` returns None when nothing has survived to propose,
        # so the ordinary case is unchanged: eligible doctrines FERMENT.
        proposals = self._nova_proposals(signals)
        proposal_map = proposals or {}
        context: Dict[str, Dict[str, Any]] = {
            doctrine_id: {'echo_origin': self._echo_origin(doctrine_id, proposal_map)}
            for doctrine_id in signals
        }

        rulings = self.dee.cycle(signals=signals, proposals=proposals,
                                 context=context)

        for ruling in rulings:
            report['rulings'].append({
                'doctrine': ruling.doctrine_id,
                'verdict': ruling.verdict.value,
                'reason': ruling.reason,
            })
            if ruling.executed_by == 'SAE':
                report['mutated'] += 1
                self.stats['doctrines_mutated'] += 1
                # RIL: identity terminus. Record the mutation on DOCTRINE; RIL grounds
                # or abstains on whether it fractures identity (module docstring).
                doctrine = self.codex.get(ruling.doctrine_id)
                if doctrine is not None:
                    self.ril.ingest_doctrine_mutation(ruling, doctrine)
            elif ruling.verdict.value == 'ferment':
                report['fermenting'] += 1
                self.stats['doctrines_fermenting'] += 1

        return report

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        # Calculate TCA metrics
        tca_metrics = {
            'total_nodes': len(self.tca.topology.nodes),
            'total_edges': self.tca.topology.total_edges,
            'constellations': len(self.tca.topology.constellations),
            'total_mass': self.tca.topology.total_mass,
            'fragmentation': self.tca.topology.fragmentation_index
        }
        
        # Find gravity wells
        gravity_wells = []
        for node_id, node in self.tca.topology.nodes.items():
            if node.mass > 5.0:
                gravity_wells.append({
                    'id': node_id,
                    'type': node.node_type.value,
                    'mass': node.mass,
                    'edges': len(node.edges)
                })
        gravity_wells.sort(key=lambda x: x['mass'], reverse=True)
        tca_metrics['gravity_wells'] = gravity_wells[:5]  # Top 5
        
        return {
            'suspended': self.processing_suspended,
            'suspension_reason': self.suspension_reason,
            'system_pressure': self.pressure_monitor.get_system_pressure(),
            'cascade_risk': self.pressure_monitor.check_cascade_risk(),
            'active_scars': len(self.scar_core.get_active_scars()),
            'total_doctrines': len(self.codex),
            'fossil_doctrines': len(self.codex.fossils),
            'self_mutation': self.sae.status(),
            'compass': self.compass.status(),
            'contradiction_chamber': self.sbsre.status(),
            'doctrine_evolution': self.dee.status(),
            'reflex_status': self.reflex_grid.get_system_status(),
            'suspension_status': {
                'csa': {
                    'entries': len(self.csa.entries),
                    'load': self.csa.get_load_percentage(),
                    'stability': self.csa.check_stability()['stable']
                },
                'veiled_thread': {
                    'entries': len(self.veiled_thread.entries),
                    'fermenting': len([e for e in self.veiled_thread.entries.values() 
                                      if e.fermentation_cycles < 10]),
                    'candidates': len(self.veiled_thread.get_doctrine_candidates())
                },
                'black_sphere': {
                    'paradoxes': len(self.black_sphere.entries),
                    'families': len(self.black_sphere.paradox_families),
                    'gravity': sum(e.gravitational_influence for e in self.black_sphere.entries.values())
                }
            },
            'topology': tca_metrics,
            'statistics': self.stats
        }
    
    def resume_processing(self):
        """Resume processing after suspension."""
        self.processing_suspended = False
        self.suspension_reason = ""
    
    def get_topology_visualization(self) -> str:
        """Get ASCII visualization of the topological space."""
        lines = []
        lines.append("\n" + "="*60)
        lines.append("TOPOLOGICAL CONSTELLATION MAP")
        lines.append("="*60)
        
        # Node counts by type
        node_types = {}
        for node in self.tca.topology.nodes.values():
            node_type = node.node_type.value
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        lines.append("\nNODE DISTRIBUTION:")
        for node_type, count in sorted(node_types.items()):
            lines.append(f"  {node_type:10s}: {count:3d} nodes")
        
        # Constellation status
        lines.append("\nCONSTELLATIONS:")
        for const_id, constellation in self.tca.topology.constellations.items():
            cohesion = constellation.calculate_cohesion()
            lines.append(f"  {const_id:15s}: {len(constellation.nodes):3d} nodes, cohesion {cohesion:.2f}")
        
        # Top gravity wells
        lines.append("\nMAJOR GRAVITY WELLS:")
        wells = [(n.id, n.mass) for n in self.tca.topology.nodes.values() if n.mass > 3.0]
        wells.sort(key=lambda x: x[1], reverse=True)
        for node_id, mass in wells[:5]:
            lines.append(f"  {node_id[:20]:20s}: mass {mass:.1f}")
        
        # System metrics
        lines.append("\nSYSTEM METRICS:")
        lines.append(f"  Total Mass:     {self.tca.topology.total_mass:.1f}")
        lines.append(f"  Total Edges:    {self.tca.topology.total_edges}")
        lines.append(f"  Fragmentation:  {self.tca.topology.fragmentation_index:.2f}")
        
        # Wormholes (scar bridges)
        if self.tca.topology.wormholes:
            lines.append(f"\nWORMHOLES: {len(self.tca.topology.wormholes)} scar bridges active")
        
        lines.append("="*60)
        return "\n".join(lines)
        
    def save_state(self, filepath: Optional[str] = None):
        """Save current system state to disk.

        RULING 34 res.7 - THE PATH IS NO LONGER A METHOD-PARAMETER DEFAULT.
        It was `filepath: str = "data/aurea_state.json"`, which is reachable by
        NEITHER of `tests/conftest.py`'s two mechanisms: it is not a class
        attribute and not an `__init__` default. That is Ruling 31's
        unreachable-by-construction defect in its THIRD location - the shape
        Ruling 31's sweep was never specified on - and its target sat OUTSIDE
        `data/runtime/`, so a real run left an untracked file in the tree: the
        exact pre-Ruling-31 condition. `STATE_PATH` is a class attribute,
        resolved at WRITE time, redirected by the fixture, and pointed under
        `data/runtime/`. The parameter survives as the EXPLICIT override, the
        same way Ruling 32 kept `filepath=` on the stores.

        RULING 34 res.8 - THE save/load ASYMMETRY IS CLOSED. `system_status` (a
        RENDERED REPORT STRING from `get_system_status()`) was written into the
        data file and never read back: Docket L's stale-status-line shape in its
        worst possible location, guaranteed to go stale against the data beside
        it with nothing ever reading it to notice. DROPPED, not moved.

        WHAT ROUND-TRIPS NOW, exhaustively: `statistics` and `suspension_state`
        are written and read. `timestamp` and `version` are written and NOT read
        back - they are metadata ABOUT the file rather than state, which is a
        different thing from a rendered view of state that pretends to be data.
        """
        state_path = Path(filepath or self.STATE_PATH)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            'version': 1,
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'suspension_state': {
                'suspended': self.processing_suspended,
                'reason': self.suspension_reason
            }
        }

        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)

        # Also save modules. SAE joins them (Ruling 34): its epoch state is
        # ALREADY durable at every mutation, so this is a consistency snapshot
        # rather than the mechanism - if this were the only save point, a process
        # kill would still restore her budget.
        self.scar_core.save_to_file()
        self.codex.save_to_file()
        self.tca.topology.save_to_file()
        self.sae.save()

    def load_state(self, filepath: Optional[str] = None):
        """Load system state from disk. Symmetrical with `save_state` (res.8)."""
        state_path = Path(filepath or self.STATE_PATH)
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
                self.stats = state.get('statistics', self.stats)
                suspension = state.get('suspension_state', {})
                self.processing_suspended = suspension.get('suspended', False)
                self.suspension_reason = suspension.get('reason', '')
