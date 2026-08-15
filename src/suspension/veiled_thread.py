"""
veiled_thread.py - Veiled Thread suspension system for AUREA
Fermentation chamber for valuable but unresolved symbolic content.
"""

from src.suspension.suspension_base import (
    SuspensionSystem, SuspensionEntry, SuspensionType
)
from typing import Any, Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path

from src.utils.atomic_write import atomic_write_json


class VeiledThread(SuspensionSystem):
    """
    Veiled Thread - Fermentation chamber for promising but unresolved content.
    
    Content enters Veiled Thread when:
    - Medium pressure (0.5-0.8) without clear resolution
    - Promising insights that need development
    - Cross-domain paradoxes that might resolve with time
    - Resonant content lacking structural support
    """

    # M4-beta' (2026-08-15): the mint's prefix, unchanged from the wall-clock
    # era. **TWO REMOVAL DOORS OF ITS OWN** - `extract_emerged` and
    # `_purge_low_potential_entries` - plus the inherited `purge_old_entries`.
    # (`check_emergence` is NOT one: it returns a bool and removes nothing.)
    ID_PREFIX = "VT-"

    def __init__(self, capacity: int = 100, filepath: str = "data/runtime/suspension/veiled_thread.json"):
        super().__init__(capacity)
        self.suspension_type = SuspensionType.VEILED
        self.filepath = Path(filepath)
        self.fermentation_threshold = 10  # Cycles before checking emergence
        self.resonance_threshold = 0.7    # Resonance level for emergence
        self.doctrine_potential_threshold = 0.8  # When content becomes doctrine candidate
        self.load_from_file()
        
    def suspend(self, content: Any,
                pressure: float, reason: str = "") -> SuspensionEntry:
        """
        Suspend content in Veiled Thread for fermentation.

        RULING 84 (2026-08-11): the `source` parameter is DELETED. Its two
        callers passed `DEE` and `tether` - real module identities, and still a
        display string no logic read.

        Args:
            content: The unresolved content to ferment
            pressure: Symbolic pressure level
            reason: Reason for suspension
            
        Returns:
            SuspensionEntry for the veiled content
        """
        # Check capacity
        if self.is_at_capacity():
            # Purge entries with low emergence potential
            self._purge_low_potential_entries()
            
        # Create entry
        #
        # M4-beta': MINTED from the high-water mark. **THIS STORE IS THE ONE
        # THE STOP WAS WITNESSED ON**: `extract_emerged` is the Veiled Thread's
        # own success path - content ferments and emerges - and it removes the
        # entry, so a mint derived from survivors reissued the id of something
        # that had just succeeded. The purge two lines above does it too.
        entry = SuspensionEntry(
            id=self._mint_id(),
            content=content,
            suspension_type=SuspensionType.VEILED,
            pressure_level=pressure,
            reason=reason or f"Suspended for fermentation at pressure {pressure:.2f}",
            fermentation_cycles=0,
            emergence_potential=pressure * 0.5,  # Initial potential based on pressure
            doctrine_candidate=False
        )
        
        self.entries[entry.id] = entry
        self.total_suspended += 1
        self.save_to_file()
        
        return entry
        
    def retrieve(self, entry_id: str) -> Optional[SuspensionEntry]:
        """
        Retrieve veiled content for inspection or retry.
        """
        if entry_id not in self.entries:
            return None
            
        entry = self.entries[entry_id]
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        self.save_to_file()
        return entry
        
    def check_stability(self) -> Dict[str, Any]:
        """
        Check Veiled Thread stability and fermentation health.
        """
        if not self.entries:
            return {
                'stable': True,
                'load': 0,
                'fermenting': 0,
                'ready_for_emergence': [],
                'doctrine_candidates': []
            }
            
        fermenting = 0
        ready_for_emergence = []
        doctrine_candidates = []
        total_potential = 0.0
        
        for entry in self.entries.values():
            # Count actively fermenting
            if entry.fermentation_cycles < self.fermentation_threshold:
                fermenting += 1
                
            # Check emergence readiness
            if self.check_emergence(entry.id):
                ready_for_emergence.append(entry.id)
                
            # Check doctrine candidacy
            if entry.doctrine_candidate:
                doctrine_candidates.append(entry.id)
                
            total_potential += entry.emergence_potential
            
        avg_potential = total_potential / len(self.entries) if self.entries else 0
        load_pct = self.get_load_percentage()
        
        # Stable if not overloaded and fermentation is progressing
        stable = load_pct < 90 and avg_potential > 0.3
        
        return {
            'stable': stable,
            'load': load_pct,
            'fermenting': fermenting,
            'ready_for_emergence': ready_for_emergence,
            'doctrine_candidates': doctrine_candidates,
            'average_potential': avg_potential
        }
        
    def ferment_cycle(self) -> Dict[str, Any]:
        """
        Run a fermentation cycle on all veiled content.
        Updates fermentation progress and emergence potential.
        
        Returns:
            Dict with fermentation results
        """
        emerged = []
        candidates = []
        
        for entry in self.entries.values():
            # Increment fermentation
            entry.fermentation_cycles += 1
            
            # Increase emergence potential over time (slow maturation)
            if entry.fermentation_cycles > 5:
                entry.emergence_potential = min(
                    entry.emergence_potential * 1.05,  # 5% increase per cycle
                    1.0
                )
                
            # Check for doctrine candidacy
            if entry.emergence_potential > self.doctrine_potential_threshold:
                if not entry.doctrine_candidate:
                    entry.doctrine_candidate = True
                    candidates.append(entry.id)
                    
            # Check if ready to emerge
            if self.check_emergence(entry.id):
                emerged.append(entry.id)
                
        self.save_to_file()
        
        return {
            'cycles_run': 1,
            'emerged': emerged,
            'new_doctrine_candidates': candidates,
            'total_fermenting': len(self.entries)
        }
        
    def check_emergence(self, entry_id: str) -> bool:
        """
        Check if veiled content is ready to emerge (retry collapse).
        
        Emergence conditions:
        - Sufficient fermentation cycles
        - High emergence potential
        - System pressure is low (safe to retry)
        - Resonance with new scars
        """
        if entry_id not in self.entries:
            return False
            
        entry = self.entries[entry_id]
        
        # Check fermentation time
        if entry.fermentation_cycles < self.fermentation_threshold:
            return False
            
        # Check emergence potential
        if entry.emergence_potential < self.resonance_threshold:
            return False
            
        # Additional checks would involve:
        # - Current system pressure (from pressure monitor)
        # - New scar formation that might enable resolution
        # - Doctrine mutations that change context
        
        return True
        
    def extract_emerged(self, entry_id: str) -> Optional[Any]:
        """
        Extract emerged content for retry in main pipeline.
        Removes from suspension.
        """
        if entry_id not in self.entries:
            return None
            
        entry = self.entries[entry_id]
        content = entry.content
        
        # Remove from suspension
        del self.entries[entry_id]
        self.save_to_file()
        
        return content
        
    def update_resonance(self, entry_id: str, scar_id: str, resonance: float):
        """
        Update resonance scores based on new scar formation.
        High resonance with new scars increases emergence potential.
        """
        if entry_id not in self.entries:
            return
            
        entry = self.entries[entry_id]
        entry.resonance_scores[scar_id] = resonance
        
        # Update emergence potential based on resonance
        if resonance > 0.7:
            entry.emergence_potential = min(
                entry.emergence_potential * (1 + resonance * 0.1),
                1.0
            )
            entry.linked_scars.append(scar_id)
            
        self.save_to_file()
        
    def _purge_low_potential_entries(self, threshold: float = 0.2) -> int:
        """
        Purge entries with low emergence potential.
        Used when approaching capacity.
        """
        to_purge = []
        
        for entry_id, entry in self.entries.items():
            # Old entries with low potential
            if (entry.fermentation_cycles > 50 and 
                entry.emergence_potential < threshold):
                to_purge.append(entry_id)
                
        purged = 0
        for entry_id in to_purge:
            del self.entries[entry_id]
            purged += 1
            
        if purged > 0:
            self.save_to_file()
            
        return purged
        
    def get_doctrine_candidates(self) -> List[SuspensionEntry]:
        """Get all entries that are doctrine candidates."""
        return [e for e in self.entries.values() if e.doctrine_candidate]
        
    def save_to_file(self):
        """Save Veiled Thread entries to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = []
        for entry in self.entries.values():
            entry_dict = {
                'id': entry.id,
                'content': str(entry.content),  # Convert to string for JSON
                # RULING 84: `'source': entry.source` STOOD HERE.
                'pressure_level': entry.pressure_level,
                'timestamp': entry.timestamp.isoformat(),
                'reason': entry.reason,
                'fermentation_cycles': entry.fermentation_cycles,
                'emergence_potential': entry.emergence_potential,
                'doctrine_candidate': entry.doctrine_candidate,
                'resonance_scores': entry.resonance_scores,
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                'linked_scars': entry.linked_scars,
                'metadata': entry.metadata
            }
            data.append(entry_dict)
            
        # Rider R3 (2026-07-29): ATOMIC. A whole-file rebuild per save (see
        # `black_sphere.save_to_file`). The Veiled Thread is "where a
        # contradiction goes to keep being real"; a torn write ends that.
        #
        # M4-beta' (2026-08-15) - THE ENVELOPE. **THE SCHEMA CHANGE, DECLARED**:
        # a BARE JSON LIST becomes `{"high_water": N, "entries": [...]}`. The
        # counter rides in the same atomic write as the entries it numbers, so
        # an emergence that removes an entry cannot take the record of its id
        # with it.
        atomic_write_json(self.filepath, self._envelope(data), indent=2)

    def load_from_file(self):
        """Load Veiled Thread entries from disk.

        M4-beta': BOTH SHAPES LOAD FOREVER - see `_absorb_envelope`. A legacy
        file's wall-clock ids do not parse as ordinals, so it starts at 0 and
        `VT-0001` cannot collide with a twenty-digit id already in it.
        """
        if not self.filepath.exists():
            return

        with open(self.filepath, 'r') as f:
            data = json.load(f)

        for entry_dict in self._absorb_envelope(data):
            entry = SuspensionEntry(
                id=entry_dict['id'],
                content=entry_dict['content'],
                # RULING 84: `source=entry_dict['source']` STOOD HERE. Explicit
                # key reads mean a legacy key is never consulted.
                suspension_type=SuspensionType.VEILED,
                pressure_level=entry_dict['pressure_level'],
                timestamp=datetime.fromisoformat(entry_dict['timestamp']),
                reason=entry_dict['reason'],
                fermentation_cycles=entry_dict['fermentation_cycles'],
                emergence_potential=entry_dict['emergence_potential'],
                doctrine_candidate=entry_dict['doctrine_candidate'],
                resonance_scores=entry_dict.get('resonance_scores', {}),
                access_count=entry_dict.get('access_count', 0),
                last_accessed=datetime.fromisoformat(entry_dict['last_accessed']) if entry_dict.get('last_accessed') else None,
                linked_scars=entry_dict.get('linked_scars', []),
                metadata=entry_dict.get('metadata', {})
            )
            self.entries[entry.id] = entry
