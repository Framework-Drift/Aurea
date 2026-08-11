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
    # RULING 84 (2026-08-11) - THE SOURCE FIELD RETIRES.
    #
    # `source: str` STOOD HERE and is DELETED AS SHAPE, Ruling 68's form.
    #
    # It was `Echo.source`'s exact pre-Ruling-68 profile: a manufactured origin
    # string on a durable record, with ZERO logic readers anywhere in `src/` -
    # three serializers wrote it out, three loaders read it back, and nothing
    # ever decided anything by it. Ruling 83's census classified all seventeen
    # of its call sites and found NO class-(b) site, because the replacement
    # Ruling 68 used - deletion, with origin reached through the join - was
    # barred to that pass. **THIS IS THE RULING IT WAITED FOR.**
    #
    # THE REPLACEMENT ALREADY EXISTS AND IS UNTOUCHED: `claim_id` below is the
    # record's real origin, a join into the claim-ancestry ledger, populated by
    # the pipeline door and honestly `None` everywhere else. A demoted display
    # string sitting beside an honest join is not harmless - it is the field
    # people read while the join is the one that is true.
    #
    # **ERA HONESTY FALLS OUT BY CONSTRUCTION, and that is why no tolerant-load
    # filter was added:** all three loaders read EXPLICIT keys rather than
    # splatting the dict (`Echo(**data)`'s shape, which needed Ruling 75's
    # filter), so a legacy file's `source` key is simply never read. The bytes
    # are never rewritten in place and the key never round-trips back out.
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
    # RULING 76 (2026-08-05) - THE RECORD CARRIES ITS ORIGIN.
    #
    # A JOIN KEY, NOT AN ORIGIN FACT - `Echo.claim_id` and `Scar.claim_id`'s
    # exact class, Ruling 60's canonical key extended to the third record a
    # claim cycle can produce. It points at the claim-ancestry ledger line
    # minted at ingress; the LEDGER still stores origin ONCE (L3 clean).
    #
    # **WHY: THE ECHO->PARADOX EDGE WAS RUNTIME HISTORY NOTHING COULD DERIVE.**
    # Ruling 75 measured `paradox_void` losing its gravity center at every
    # restart and reported it rather than repairing it - a paradox node's only
    # edge is written at suspension time, and `suspend(...)` received content,
    # source, pressure, reason and paradox_type with **NO id join of any kind**.
    # Content-matching would have been the lexical-similarity defect class and
    # was refused. This is the join instead.
    #
    # **ON THE SHARED ENTRY, NOT THE BLACK SPHERE'S OWN, BECAUSE THE RECORD IS
    # SHARED.** CSA, the Veiled Thread and the Black Sphere all suspend into
    # this one dataclass. Only the Black Sphere's pipeline door populates it in
    # this ruling; every other suspension carries `None`, honestly, and that is
    # not a gap - a tether suspension and a DEE fermentation have no claim cycle
    # behind them. Whether CSA's own pipeline suspensions should carry it is a
    # question this ruling does not answer, because nothing derives an edge from
    # them.
    #
    # SET AT CREATION, never by post-hoc mutation, and NEVER SYNTHESIZED. No
    # backfill: a legacy entry carries `None` and derives no edge.
    claim_id: Optional[str] = None


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
    def suspend(self, content: Any,
                pressure: float, reason: str = "") -> SuspensionEntry:
        """Suspend content with given parameters.

        RULING 84: the `source` parameter is GONE from this door and from the
        three that implement it. A suspension's origin is `claim_id` where a
        claim cycle produced it, and nothing where one did not.
        """
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
