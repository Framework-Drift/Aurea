"""
aurea_core.py - Central AUREA Pipeline Controller
Orchestrates the flow: Input -> SPL -> EchoNet -> Reflexes -> Scars -> Output
"""

from src.perception.spl import SPL
from src.filtration.echonet import EchoNet, Verdict as EchoVerdict
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.codex import Codex
from src.doctrine.doctrine_spine import DoctrineSpine
from src.doctrine.dee import DEE
from src.expansion.sae import SAE
from src.expansion.nova import NovaEngine
from src.reflex.reflex_grid import ReflexGrid
from src.reflex.sbsre import SBSRE, LoopOutcome
from src.identity.compass import CompassStabilityEngine
from src.identity.ril import RIL
from src.identity.psi import PSI
from src.output.ore import ORE
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.suspension.black_sphere import BlackSphere
from src.topology.tca_integration import TCAIntegration
from src.utils.models import Echo, Scar, Doctrine
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import json


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
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize AUREA core systems.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize core modules
        self.spl = SPL()
        self.scar_core = ScarLogicCore()

        # Doctrine layer (Ruling 5): Codex owns the store, SAE is the sole executor,
        # the Spine is structure + requests. Nothing else may write doctrine.
        self.codex = Codex()
        self.sae = SAE(codex=self.codex)
        self.doctrine_spine = DoctrineSpine(codex=self.codex)

        self.reflex_grid = ReflexGrid()
        self.ore = ORE()
        
        # Initialize suspension systems
        self.csa = CSA()
        self.veiled_thread = VeiledThread()
        self.black_sphere = BlackSphere()
        
        # Initialize Topological Constellation Architecture
        self.tca = TCAIntegration()

        # Nova (Ruling 12, Stage 2a): the doctrine AUTHOR, now constructed and
        # owned here. Sole writer of `echo_index` (G4, scanned by the Ruling-1
        # invariant); everything else it wants is a REQUEST list or a return
        # value. ZERO MUTATION RISK in 2a: the `proposals` seam below stays
        # None, so nothing Nova holds can reach SAE - doctrine mutation remains
        # structurally impossible until 2b opens that path. Compass EAST reads
        # this engine live (below), and it cycles once per pipeline pass
        # (see _nova_cycle).
        self.nova = NovaEngine()

        # ---- THE COLLAPSE SPINE ----------------------------------------------
        # CSE: orientation. Holds NO anchor store - it derives N/S/E/W from the modules that
        # already own them (Codex · Scar Core · Nova · Black Sphere), so the compass cannot
        # disagree with reality. A compass that lies is worse than no compass.
        self.compass = CompassStabilityEngine(
            codex=self.codex,
            scar_core=self.scar_core,
            black_sphere=self.black_sphere,
            nova=self.nova,                # Stage 2a: EAST reads real Nova state - active_echoes()
            tcaml=None,                    # unbuilt: realignment requests are no-ops for now
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
            'errors': []
        }
        
        # Check if processing is suspended
        if self.processing_suspended:
            result['output_blocked'] = True
            result['output'] = f"[SUSPENDED: {self.suspension_reason}]"
            return result
        
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
            arbitrated_lock = next(
                (r for r in reading.reflex_responses if r.output_blocked), None)
            if arbitrated_lock is not None:
                result['output'] = (
                    f"[OUTPUT LOCKED by {arbitrated_lock.reflex_id} - compass drift "
                    f"{reading.drift:.1f}°, RACM-authorized suppress. She does not speak "
                    f"while disoriented.]")
                result['output_blocked'] = True
                self.stats['outputs_suppressed'] += 1
                return result

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
                    result['output'] = f"[PARADOX SUSPENDED in Black Sphere: {bs_entry.id}]"
                    result['output_blocked'] = True
                    return result

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
                    result['output'] = (
                        f"[CARRIED {thread.cycles_run} cycles, unresolved - "
                        f"partial thread held in CSA: {entry_id}]")
                    result['output_blocked'] = True
                    return result

                elif thread.outcome is LoopOutcome.MIRROR:
                    # Whisper Reflex: speaking this would be symbolic betrayal. Reflect it back
                    # as unclaimed rather than assert something AUREA has not earned.
                    result['output'] = f"[MIRRORED - unclaimed contradiction: {echo.content}]"
                    return result
            
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

            # Step 5a.5: NOVA (Stage 2a). Cycle Nova ONCE here, AFTER all reflex
            # arbitration this pass (compass-read Step 2.5 + GSR cascade Step 4 +
            # scar-density Step 5 have all appended their RACM-authorized returns
            # to result['reflex_responses']) and BEFORE _evolve_doctrine (so the
            # echo state Docket C reads is current). Ferment + erupt; never
            # proposes - proposals stays None in _evolve_doctrine (2a boundary).
            self._nova_cycle(result['reflex_responses'])

            # Step 5b: DOCTRINE EVOLUTION. A new scar is pressure on everything it touches.
            # DEE gates; SAE executes; the Codex records. This orchestrator does none of those.
            result['doctrine'] = self._evolve_doctrine(result, collapse_result)
            
            # Step 6: Check reflex responses for output blocking
            for response in result['reflex_responses']:
                if response.output_blocked:
                    result['output_blocked'] = True
                    result['output'] = f"[BLOCKED by {response.reflex_id}]"
                    self.stats['outputs_suppressed'] += 1
                    
                if response.action == 'cascade':
                    # System-wide suspension
                    self.processing_suspended = True
                    self.suspension_reason = response.message
                    
            # Step 7: Generate output if not blocked
            if not result['output_blocked']:
                if collapse_result.passed:
                    result['output'] = f"Echo processed: {echo.content}"
                else:
                    result['output'] = f"Collapse detected: {collapse_result.reason}"
                    
                # Add pressure indicator
                if collapse_result.pressure_generated > 0.5:
                    result['output'] += f" [Pressure: {collapse_result.pressure_generated:.2f}]"
            
            # Step 8: Update statistics
            if result['reflex_responses']:
                self.stats['reflexes_triggered'] += len(result['reflex_responses'])
                
        except Exception as e:
            result['errors'].append(str(e))
            result['output'] = f"[ERROR: {str(e)}]"
            
        return result
    
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
        """Nova Stage 2a: one fermentation-and-eruption pass, ZERO mutation risk.

        Nova ferments its echoes and may erupt new ones; it NEVER proposes here
        (proposals stays None in _evolve_doctrine). G5 first: if expansion is
        under an authorized suspension this cycle, cycle() records its own
        refusal and advances nothing, and we skip eruption too - deference is
        total, not cosmetic.
        """
        suppressed = self._nova_suppressed(reflex_responses)
        self.nova.cycle(suppressed=suppressed, source='aurea_core')
        if suppressed:
            return
        self._nova_erupt_from_doctrine_strain()

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
        (all built and available) are ALSO NOT-YET-WIRED sources - Stage 2a
        wires exactly one, honestly, per the contract.
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

    def _evolve_doctrine(self, result: Dict[str, Any], collapse_result) -> Dict[str, Any]:
        """Run one DEE evolution pass. The orchestrator gates nothing and writes nothing.

        A fresh scar is pressure on every doctrine it touches. DEE scans, holds, validates;
        SAE executes; the Codex records. AureaCore's only job here is to hand DEE the
        pressure signals and report what it decided.

        NOTE: no `proposals` are passed - BY STAGE DESIGN (Nova Stage 2a). Nova is
        constructed and its echo state is real, but its proposals seam stays unwired:
        `proposals=None` keeps doctrine mutation structurally impossible (SAE needs a
        proposed form) until Stage 2b deliberately opens that path. DBE remains unbuilt.
        Eligible doctrines FERMENT rather than mutate - correct behavior, not a gap to
        paper over: AUREA does not get to invent what she becomes just because pressure
        demands that she become something.
        """
        report: Dict[str, Any] = {'rulings': [], 'mutated': 0, 'fermenting': 0}

        scar = result.get('scar_formed')
        if scar is None:
            return report

        # Pressure signals: which doctrines does this scar bear on?
        signals: Dict[str, Dict[str, Any]] = {}
        pressure = float(getattr(collapse_result, 'pressure_generated', 0.0))
        for doctrine in self.codex.view().values():
            touched = bool(set(doctrine.scar_links) & {scar.id}) or \
                      bool(set(scar.linked_doctrines or []) & {doctrine.id})
            signals[doctrine.id] = {
                'pressure': pressure if touched else pressure * 0.5,
                'drpe': touched,
                'scar_bloom': len(doctrine.scar_links) >= 3,
            }

        # Docket C (Stage 2a, 2026-07-23): `echo_origin` is DERIVED from real
        # Nova state, never a literal. The old hardcode ({'echo_origin': True}
        # for every doctrine) claimed, falsely, that a Nova echo underwrote
        # every doctrine - and CMTE criterion 2 is an OR, so a doctrine with
        # NO scar links passed the gate whose law is "No belief may evolve
        # unless the fracture that broke it can still be seen." Harmless only
        # while proposals=None; a lie the moment 2b opens the seam.
        #
        # v1 BEARING RULE (conservative by design - broadening is a ruling,
        # not an edit): an echo bears on a doctrine iff it ERUPTED FROM that
        # doctrine's strain (origin_kind == "doctrine_strain", origin_id ==
        # the doctrine id). Scar-link overlap is deliberately NOT inferred -
        # that would be a weaker re-fabrication of the same false claim.
        #
        # `echo_resonance` is NOT supplied: no real resonance value exists in
        # the organ (Echo Protocol IV's scores are deliberately un-coined),
        # and criterion 3's absent-reads-as-pass semantics stay DEE's own.
        context: Dict[str, Dict[str, Any]] = {}
        for doctrine_id in signals:
            context[doctrine_id] = {
                'echo_origin': any(
                    e.origin_kind == "doctrine_strain"
                    and e.origin_id == doctrine_id
                    for e in self.nova.echo_index.values()
                ),
            }

        rulings = self.dee.cycle(signals=signals, proposals=None,
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
        
    def save_state(self, filepath: str = "data/aurea_state.json"):
        """Save current system state to disk."""
        state_path = Path(filepath)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'system_status': self.get_system_status(),
            'suspension_state': {
                'suspended': self.processing_suspended,
                'reason': self.suspension_reason
            }
        }
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
            
        # Also save modules
        self.scar_core.save_to_file()
        self.codex.save_to_file()
        self.tca.topology.save_to_file()
        
    def load_state(self, filepath: str = "data/aurea_state.json"):
        """Load system state from disk."""
        state_path = Path(filepath)
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
                self.stats = state.get('statistics', self.stats)
                suspension = state.get('suspension_state', {})
                self.processing_suspended = suspension.get('suspended', False)
                self.suspension_reason = suspension.get('reason', '')
