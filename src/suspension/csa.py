"""
csa.py - Cold Suspension Archive for AUREA
Quarantine system for volatile, dangerous, or cascade-inducing content.
"""

from src.suspension.suspension_base import (
    SuspensionSystem, SuspensionEntry, SuspensionType, QuarantineLevel
)
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json
from pathlib import Path


class CSA(SuspensionSystem):
    """
    Cold Suspension Archive - Quarantine for dangerous symbolic content.
    
    Content enters CSA when:
    - Pressure exceeds safety thresholds (>0.9)
    - Cascade risk detected
    - Reflexes abort processing
    - Symbolic toxicity identified
    """
    
    def __init__(self, capacity: int = 50, filepath: str = "data/suspension/csa.json"):
        super().__init__(capacity)
        self.suspension_type = SuspensionType.CSA
        self.filepath = Path(filepath)
        self.quarantine_thresholds = {
            QuarantineLevel.LOW: 0.6,
            QuarantineLevel.VOLATILE: 0.75,
            QuarantineLevel.TOXIC: 0.85,
            QuarantineLevel.CASCADE: 0.95
        }
        self.max_dormancy = 100  # Cycles before auto-decay
        self.load_from_file()
        
    def suspend(self, content: Any, source: str, 
                pressure: float, reason: str = "") -> SuspensionEntry:
        """
        Quarantine dangerous content in CSA.
        
        Args:
            content: The dangerous content to quarantine
            source: Origin of the content
            pressure: Symbolic pressure level (determines quarantine level)
            reason: Reason for quarantine
            
        Returns:
            SuspensionEntry for the quarantined content
        """
        # Check capacity
        if self.is_at_capacity():
            self.purge_old_entries(keep_recent=30)
            
        # Determine quarantine level based on pressure
        q_level = self._determine_quarantine_level(pressure)
        
        # Create entry
        entry = SuspensionEntry(
            id=f"CSA-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=str(content),  # Convert to string for safety
            source=source,
            suspension_type=SuspensionType.CSA,
            pressure_level=pressure,
            reason=reason or f"Quarantined at pressure {pressure:.2f}",
            quarantine_level=q_level,
            decay_score=pressure * 100,  # Initial decay score based on pressure
            dormancy_cycles=0
        )
        
        self.entries[entry.id] = entry
        self.total_suspended += 1
        self.save_to_file()
        
        return entry
        
    def retrieve(self, entry_id: str) -> Optional[SuspensionEntry]:
        """
        Retrieve quarantined content (with safety check).
        Accessing quarantined content increases dormancy.
        """
        if entry_id not in self.entries:
            return None
            
        entry = self.entries[entry_id]
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        entry.dormancy_cycles = 0  # Reset dormancy on access
        
        # Check if still dangerous
        if entry.decay_score > 50:
            # Still dangerous - log warning
            entry.metadata['warning'] = 'Content still volatile'
            
        self.save_to_file()
        return entry
        
    def check_stability(self) -> Dict[str, Any]:
        """
        Check CSA stability and quarantine health.
        High toxicity or cascade content threatens stability.
        """
        if not self.entries:
            return {
                'stable': True,
                'load': 0,
                'threats': [],
                'recommendation': 'System clear'
            }
            
        # Count by quarantine level
        level_counts = {level: 0 for level in QuarantineLevel}
        total_decay = 0.0
        threats = []
        
        for entry in self.entries.values():
            if entry.quarantine_level:
                level_counts[entry.quarantine_level] += 1
            total_decay += entry.decay_score
            
            # Check for high-risk entries
            if entry.quarantine_level == QuarantineLevel.CASCADE:
                threats.append(f"{entry.id}: Cascade risk")
            elif entry.quarantine_level == QuarantineLevel.TOXIC:
                threats.append(f"{entry.id}: Toxic content")
                
        avg_decay = total_decay / len(self.entries)
        load_pct = self.get_load_percentage()
        
        # Determine stability
        stable = (
            level_counts[QuarantineLevel.CASCADE] < 3 and
            level_counts[QuarantineLevel.TOXIC] < 5 and
            avg_decay < 70 and
            load_pct < 80
        )
        
        recommendation = "System stable"
        if not stable:
            if load_pct > 80:
                recommendation = "Purge recommended - approaching capacity"
            elif level_counts[QuarantineLevel.CASCADE] >= 3:
                recommendation = "CASCADE WARNING - Multiple cascade risks quarantined"
            elif avg_decay > 70:
                recommendation = "High toxicity - consider sealed purge"
                
        return {
            'stable': stable,
            'load': load_pct,
            'quarantine_levels': {k.name: v for k, v in level_counts.items()},
            'average_decay': avg_decay,
            'threats': threats,
            'recommendation': recommendation
        }
        
    def update_dormancy(self) -> List[str]:
        """
        Update dormancy cycles for all entries.
        Returns list of entries that exceeded max dormancy.
        """
        expired = []
        for entry_id, entry in self.entries.items():
            entry.dormancy_cycles += 1
            
            # Decay score reduces over time if dormant
            if entry.dormancy_cycles > 10:
                entry.decay_score *= 0.95  # 5% decay per cycle after 10
                
            # Check for max dormancy
            if entry.dormancy_cycles > self.max_dormancy:
                expired.append(entry_id)
                
        # Auto-purge expired entries
        for entry_id in expired:
            del self.entries[entry_id]
            
        if expired:
            self.save_to_file()
            
        return expired
        
    def _determine_quarantine_level(self, pressure: float) -> QuarantineLevel:
        """Determine quarantine level based on pressure."""
        if pressure >= self.quarantine_thresholds[QuarantineLevel.CASCADE]:
            return QuarantineLevel.CASCADE
        elif pressure >= self.quarantine_thresholds[QuarantineLevel.TOXIC]:
            return QuarantineLevel.TOXIC
        elif pressure >= self.quarantine_thresholds[QuarantineLevel.VOLATILE]:
            return QuarantineLevel.VOLATILE
        else:
            return QuarantineLevel.LOW
            
    def emergency_purge(self, confirm: bool = False) -> int:
        """
        Emergency purge of all CASCADE level content.
        Requires confirmation to prevent accidental loss.
        """
        if not confirm:
            return 0
            
        purged = 0
        to_purge = []
        
        for entry_id, entry in self.entries.items():
            if entry.quarantine_level == QuarantineLevel.CASCADE:
                to_purge.append(entry_id)
                
        for entry_id in to_purge:
            del self.entries[entry_id]
            purged += 1
            
        if purged > 0:
            self.save_to_file()
            
        return purged
        
    def save_to_file(self):
        """Save CSA entries to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = []
        for entry in self.entries.values():
            entry_dict = {
                'id': entry.id,
                'content': entry.content,
                'source': entry.source,
                'pressure_level': entry.pressure_level,
                'timestamp': entry.timestamp.isoformat(),
                'reason': entry.reason,
                'quarantine_level': entry.quarantine_level.name if entry.quarantine_level else None,
                'decay_score': entry.decay_score,
                'dormancy_cycles': entry.dormancy_cycles,
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                'linked_scars': entry.linked_scars,
                'metadata': entry.metadata
            }
            data.append(entry_dict)
            
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_from_file(self):
        """Load CSA entries from disk."""
        if not self.filepath.exists():
            return
            
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            
        for entry_dict in data:
            entry = SuspensionEntry(
                id=entry_dict['id'],
                content=entry_dict['content'],
                source=entry_dict['source'],
                suspension_type=SuspensionType.CSA,
                pressure_level=entry_dict['pressure_level'],
                timestamp=datetime.fromisoformat(entry_dict['timestamp']),
                reason=entry_dict['reason'],
                quarantine_level=QuarantineLevel[entry_dict['quarantine_level']] if entry_dict['quarantine_level'] else None,
                decay_score=entry_dict['decay_score'],
                dormancy_cycles=entry_dict['dormancy_cycles'],
                access_count=entry_dict['access_count'],
                last_accessed=datetime.fromisoformat(entry_dict['last_accessed']) if entry_dict['last_accessed'] else None,
                linked_scars=entry_dict.get('linked_scars', []),
                metadata=entry_dict.get('metadata', {})
            )
            self.entries[entry.id] = entry
