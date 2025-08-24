"""
suspension_base.py - Base classes for AUREA's suspension systems
Foundation for CSA, Veiled Thread, and Black Sphere.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class SuspensionType(Enum):
    """Types of suspension in AUREA."""
    CSA = "cold_suspension"          # Quarantine for dangerous content
    VEILED = "veiled_thread"          # Fermentation for valuable but unresolved
    BLACK_SPHERE = "black_sphere"     # Perpetual orbit for true paradoxes
    

class QuarantineLevel(Enum):
    """Danger levels for CSA quarantine."""
    LOW = 1        # Monitored but stable
    VOLATILE = 2   # Actively dangerous
    TOXIC = 3      # Corrupting influence
    CASCADE = 4    # Cascade-inducing


@dataclass
class SuspensionEntry:
    """
    Represents suspended content in AUREA's symbolic memory.
    Can be quarantined (CSA), fermenting (Veiled), or orbiting (Black Sphere).
    """
    id: str
    content: Any  # Can be Echo, partial doctrine, paradox, etc.
    source: str
    suspension_type: SuspensionType
    pressure_level: float
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    
    # CSA-specific
    quarantine_level: Optional[QuarantineLevel] = None
    decay_score: float = 0.0
    dormancy_cycles: int = 0
    
    # Veiled Thread-specific
    fermentation_cycles: int = 0
    resonance_scores: Dict[str, float] = field(default_factory=dict)
    emergence_potential: float = 0.0
    doctrine_candidate: bool = False
    
    # Black Sphere-specific
    orbit_stability: float = 1.0
    paradox_family: Optional[str] = None
    gravitational_influence: float = 0.0
    
    # Tracking
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    linked_scars: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SuspensionSystem(ABC):
    """
    Abstract base class for suspension systems.
    Provides interface for CSA, Veiled Thread, and Black Sphere.
    """
    
    def __init__(self, capacity: int = 100):
        self.entries: Dict[str, SuspensionEntry] = {}
        self.capacity = capacity
        self.suspension_type: SuspensionType = None
        self.total_suspended = 0
        self.last_purge: Optional[datetime] = None
        
    @abstractmethod
    def suspend(self, content: Any, source: str, 
                pressure: float, reason: str = "") -> SuspensionEntry:
        """Suspend content with given parameters."""
        pass
        
    @abstractmethod
    def retrieve(self, entry_id: str) -> Optional[SuspensionEntry]:
        """Retrieve suspended content by ID."""
        pass
        
    @abstractmethod
    def check_stability(self) -> Dict[str, Any]:
        """Check overall stability of suspension system."""
        pass
        
    def is_at_capacity(self) -> bool:
        """Check if suspension system is at capacity."""
        return len(self.entries) >= self.capacity
        
    def get_load_percentage(self) -> float:
        """Get current load as percentage of capacity."""
        return (len(self.entries) / self.capacity) * 100
        
    def list_entries(self, limit: int = 10) -> List[SuspensionEntry]:
        """List suspended entries (most recent first)."""
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_entries[:limit]
        
    def purge_old_entries(self, keep_recent: int = 50) -> int:
        """
        Purge oldest entries if over capacity.
        Returns number of entries purged.
        """
        if len(self.entries) <= keep_recent:
            return 0
            
        # Sort by timestamp (oldest first)
        sorted_ids = sorted(
            self.entries.keys(),
            key=lambda x: self.entries[x].timestamp
        )
        
        # Purge oldest
        to_purge = len(self.entries) - keep_recent
        purged = 0
        
        for entry_id in sorted_ids[:to_purge]:
            del self.entries[entry_id]
            purged += 1
            
        self.last_purge = datetime.now()
        return purged
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get suspension system statistics."""
        return {
            'type': self.suspension_type.value if self.suspension_type else 'unknown',
            'total_entries': len(self.entries),
            'capacity': self.capacity,
            'load_percentage': self.get_load_percentage(),
            'total_suspended_lifetime': self.total_suspended,
            'last_purge': self.last_purge.isoformat() if self.last_purge else None
        }
