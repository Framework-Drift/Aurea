"""
aurea_core.py - Central AUREA Pipeline Controller
Orchestrates the flow: Input -> SPL -> EchoNet -> Reflexes -> Scars -> Output
"""

from src.perception.spl import SPL
from src.filtration.echonet import EchoNet
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine
from src.reflex.reflex_grid import ReflexGrid
from src.output.ore import ORE
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.suspension.black_sphere import BlackSphere
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
        self.doctrine_spine = DoctrineSpine()
        self.reflex_grid = ReflexGrid()
        self.ore = ORE()
        
        # Initialize suspension systems
        self.csa = CSA()
        self.veiled_thread = VeiledThread()
        self.black_sphere = BlackSphere()
        
        # Initialize EchoNet with connections
        self.echonet = EchoNet(
            scar_core=self.scar_core,
            doctrine_spine=self.doctrine_spine,
            reflex_grid=self.reflex_grid
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
            'cascades_prevented': 0
        }
        
        # Initialize with seed doctrine if none exist
        if not self.doctrine_spine.doctrines:
            self._create_seed_doctrines()
    
    def _create_seed_doctrines(self):
        """Create foundational doctrines."""
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
            self.doctrine_spine.add_doctrine(doctrine)
    
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
            
            # Step 3: Handle suspension routing based on collapse type
            if collapse_result and not collapse_result.passed:
                # Route to suspension based on pressure and type
                if collapse_result.pressure_type == 'logical_contradiction' and collapse_result.pressure_generated > 0.9:
                    # Self-reference paradox -> Black Sphere
                    if 'this statement' in raw_input.lower() or 'i am lying' in raw_input.lower():
                        bs_entry = self.black_sphere.suspend(
                            content=echo.content,
                            source='pipeline',
                            pressure=collapse_result.pressure_generated,
                            reason='Self-reference paradox',
                            paradox_type='self_reference'
                        )
                        result['output'] = f"[PARADOX SUSPENDED in Black Sphere: {bs_entry.id}]"
                        result['output_blocked'] = True
                        return result
                elif collapse_result.pressure_generated > 0.9:
                    # Very high pressure -> CSA quarantine
                    csa_entry = self.csa.suspend(
                        content=echo.content,
                        source='pipeline',
                        pressure=collapse_result.pressure_generated,
                        reason=collapse_result.reason
                    )
                    result['output'] = f"[QUARANTINED in CSA: {csa_entry.id}]"
                    result['output_blocked'] = True
                    return result
                elif 0.5 < collapse_result.pressure_generated < 0.8:
                    # Medium pressure -> Veiled Thread for fermentation
                    vt_entry = self.veiled_thread.suspend(
                        content=echo.content,
                        source='pipeline',
                        pressure=collapse_result.pressure_generated,
                        reason='Needs fermentation'
                    )
                    result['output'] = f"[SUSPENDED in Veiled Thread: {vt_entry.id}]"
            
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
            
            # Step 5: Handle collapse and scar formation
            if not collapse_result.passed:
                # Form scar from collapse
                scar = collapse_result.scar or self.echonet.collapse_test(echo)
                self.scar_core.add_scar(scar)
                result['scar_formed'] = scar
                self.stats['scars_formed'] += 1
                
                # Check if scar density is getting dangerous
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'suspended': self.processing_suspended,
            'suspension_reason': self.suspension_reason,
            'system_pressure': self.pressure_monitor.get_system_pressure(),
            'cascade_risk': self.pressure_monitor.check_cascade_risk(),
            'active_scars': len(self.scar_core.get_active_scars()),
            'total_doctrines': len(self.doctrine_spine.doctrines),
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
            'statistics': self.stats
        }
    
    def resume_processing(self):
        """Resume processing after suspension."""
        self.processing_suspended = False
        self.suspension_reason = ""
        
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
        self.doctrine_spine.save_to_file()
        
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
