"""
black_sphere.py - Black Sphere paradox suspension for AUREA
Perpetual orbit system for irreducible paradoxes.
"""

from src.suspension.suspension_base import (
    SuspensionSystem, SuspensionEntry, SuspensionType
)
from typing import Any, Optional, Dict, List, Set
from datetime import datetime
import json
from pathlib import Path
import math


class BlackSphere(SuspensionSystem):
    """
    Black Sphere - Perpetual orbit for true paradoxes.
    
    Content enters Black Sphere when:
    - Self-reference paradoxes detected
    - Irreducible contradictions identified
    - Gödel-type incompleteness encountered
    - Mutually exclusive truths that both survive collapse
    
    Unlike CSA or Veiled Thread, Black Sphere content NEVER resolves.
    It orbits perpetually, exerting gravitational influence on nearby processing.
    """
    
    def __init__(self, capacity: int = 30, filepath: str = "data/suspension/black_sphere.json"):
        super().__init__(capacity)
        self.suspension_type = SuspensionType.BLACK_SPHERE
        self.filepath = Path(filepath)
        self.paradox_families: Dict[str, Set[str]] = {}  # Group related paradoxes
        self.gravitational_range = 0.3  # How far influence extends
        self.load_from_file()
        
    def suspend(self, content: Any, source: str, 
                pressure: float, reason: str = "",
                paradox_type: str = "unknown") -> SuspensionEntry:
        """
        Suspend paradox in Black Sphere for perpetual orbit.
        
        Args:
            content: The paradoxical content
            source: Origin of the paradox
            pressure: Symbolic pressure (usually very high for paradoxes)
            reason: Reason for suspension
            paradox_type: Type of paradox (self-reference, gödel, etc.)
            
        Returns:
            SuspensionEntry for the orbiting paradox
        """
        # Black Sphere has strict capacity - paradoxes are heavy
        if self.is_at_capacity():
            # Cannot purge paradoxes - they're permanent
            # Must refuse new entries
            raise Exception(f"Black Sphere at capacity ({self.capacity}). Cannot suspend more paradoxes.")
            
        # Create entry
        entry = SuspensionEntry(
            id=f"BS-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=str(content),  # Convert to string for safety
            source=source,
            suspension_type=SuspensionType.BLACK_SPHERE,
            pressure_level=pressure,
            reason=reason or f"Irreducible paradox at pressure {pressure:.2f}",
            orbit_stability=1.0,  # Perfect stability initially
            paradox_family=paradox_type,
            gravitational_influence=pressure * 0.3  # Influence based on pressure
        )
        
        # Add to paradox family
        if paradox_type not in self.paradox_families:
            self.paradox_families[paradox_type] = set()
        self.paradox_families[paradox_type].add(entry.id)
        
        self.entries[entry.id] = entry
        self.total_suspended += 1
        self.save_to_file()
        
        return entry
        
    def retrieve(self, entry_id: str) -> Optional[SuspensionEntry]:
        """
        Observe orbiting paradox (cannot extract - only observe).
        Observation slightly destabilizes orbit.
        """
        if entry_id not in self.entries:
            return None
            
        entry = self.entries[entry_id]
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        # Observation destabilizes orbit slightly
        entry.orbit_stability *= 0.99
        
        self.save_to_file()
        return entry
        
    def check_stability(self) -> Dict[str, Any]:
        """
        Check Black Sphere stability.
        Too many paradoxes or unstable orbits threaten the system.
        """
        if not self.entries:
            return {
                'stable': True,
                'load': 0,
                'paradox_families': {},
                'gravitational_field': 0.0,
                'unstable_orbits': []
            }
            
        total_gravity = 0.0
        unstable_orbits = []
        family_counts = {}
        
        for entry in self.entries.values():
            # Sum gravitational influence
            total_gravity += entry.gravitational_influence
            
            # Check orbit stability
            if entry.orbit_stability < 0.5:
                unstable_orbits.append(entry.id)
                
            # Count families
            if entry.paradox_family:
                family_counts[entry.paradox_family] = family_counts.get(entry.paradox_family, 0) + 1
                
        load_pct = self.get_load_percentage()
        
        # Black Sphere becomes unstable if:
        # - Too full (>80% capacity)
        # - Total gravity too high (>10.0)
        # - Multiple unstable orbits
        stable = (
            load_pct < 80 and
            total_gravity < 10.0 and
            len(unstable_orbits) < 3
        )
        
        warning = None
        if not stable:
            if load_pct >= 80:
                warning = "Black Sphere approaching capacity - new paradoxes may destabilize"
            elif total_gravity >= 10.0:
                warning = "Gravitational field dangerously strong - affecting all processing"
            elif len(unstable_orbits) >= 3:
                warning = "Multiple unstable orbits - cascade risk"
                
        return {
            'stable': stable,
            'load': load_pct,
            'paradox_families': family_counts,
            'gravitational_field': total_gravity,
            'unstable_orbits': unstable_orbits,
            'warning': warning
        }
        
    def calculate_gravitational_influence(self, distance: float) -> float:
        """
        Calculate total gravitational influence at a given symbolic distance.
        Used to determine how paradoxes affect nearby processing.
        
        Args:
            distance: Symbolic distance (0.0 = at paradox, 1.0 = far away)
            
        Returns:
            Total gravitational influence (0.0 to 1.0)
        """
        if not self.entries:
            return 0.0
            
        total_influence = 0.0
        
        for entry in self.entries.values():
            # Gravitational falloff with distance
            if distance < self.gravitational_range:
                # Inverse square law
                influence = entry.gravitational_influence / (1 + distance ** 2)
                total_influence += influence
                
        # Cap at 1.0 (maximum distortion)
        return min(total_influence, 1.0)
        
    def get_nearby_paradoxes(self, content: str, threshold: float = 0.5) -> List[str]:
        """
        Find paradoxes that might be related to given content.
        Used to detect paradox families and resonance.
        
        Args:
            content: Content to check
            threshold: Similarity threshold
            
        Returns:
            List of paradox IDs that might be related
        """
        nearby = []
        content_words = set(content.lower().split())
        
        for entry_id, entry in self.entries.items():
            # Simple word overlap check (could be more sophisticated)
            paradox_words = set(entry.content.lower().split())
            overlap = len(content_words & paradox_words)
            
            if overlap / max(len(content_words), 1) > threshold:
                nearby.append(entry_id)
                
        return nearby
        
    def stabilize_orbits(self) -> int:
        """
        Attempt to stabilize all orbits.
        Returns number of orbits stabilized.
        """
        stabilized = 0
        
        for entry in self.entries.values():
            if entry.orbit_stability < 0.8:
                # Gradual stabilization
                entry.orbit_stability = min(entry.orbit_stability * 1.1, 1.0)
                stabilized += 1
                
        if stabilized > 0:
            self.save_to_file()
            
        return stabilized
        
    def get_paradox_families(self) -> Dict[str, List[str]]:
        """Get all paradox families and their members."""
        families = {}
        for family, members in self.paradox_families.items():
            families[family] = list(members)
        return families
        
    def calculate_family_resonance(self, family: str) -> float:
        """
        Calculate resonance strength of a paradox family.
        Larger families have stronger collective influence.
        """
        if family not in self.paradox_families:
            return 0.0
            
        members = self.paradox_families[family]
        if not members:
            return 0.0
            
        # Sum gravitational influence of family members
        total_influence = 0.0
        for entry_id in members:
            if entry_id in self.entries:
                total_influence += self.entries[entry_id].gravitational_influence
                
        # Apply family bonus (paradoxes reinforce each other)
        family_bonus = math.log(len(members) + 1) * 0.2
        
        return min(total_influence * (1 + family_bonus), 1.0)
        
    def save_to_file(self):
        """Save Black Sphere entries to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'entries': [],
            'paradox_families': {k: list(v) for k, v in self.paradox_families.items()}
        }
        
        for entry in self.entries.values():
            entry_dict = {
                'id': entry.id,
                'content': entry.content,
                'source': entry.source,
                'pressure_level': entry.pressure_level,
                'timestamp': entry.timestamp.isoformat(),
                'reason': entry.reason,
                'orbit_stability': entry.orbit_stability,
                'paradox_family': entry.paradox_family,
                'gravitational_influence': entry.gravitational_influence,
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                'metadata': entry.metadata
            }
            data['entries'].append(entry_dict)
            
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_from_file(self):
        """Load Black Sphere entries from disk."""
        if not self.filepath.exists():
            return
            
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            
        # Load entries
        for entry_dict in data.get('entries', []):
            entry = SuspensionEntry(
                id=entry_dict['id'],
                content=entry_dict['content'],
                source=entry_dict['source'],
                suspension_type=SuspensionType.BLACK_SPHERE,
                pressure_level=entry_dict['pressure_level'],
                timestamp=datetime.fromisoformat(entry_dict['timestamp']),
                reason=entry_dict['reason'],
                orbit_stability=entry_dict['orbit_stability'],
                paradox_family=entry_dict.get('paradox_family'),
                gravitational_influence=entry_dict['gravitational_influence'],
                access_count=entry_dict.get('access_count', 0),
                last_accessed=datetime.fromisoformat(entry_dict['last_accessed']) if entry_dict.get('last_accessed') else None,
                metadata=entry_dict.get('metadata', {})
            )
            self.entries[entry.id] = entry
            
        # Load families
        self.paradox_families = {
            k: set(v) for k, v in data.get('paradox_families', {}).items()
        }
