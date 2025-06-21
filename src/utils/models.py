from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Scar:
    """
    Represents a symbolic collapse event in AUREA.
    """

    id: str
    origin: str  # e.g., doctrine or echo that triggered the scar
    weight: float
    created_at: datetime
    decay_state: str = "active"  # active | dormant | fossil | retired
    linked_doctrines: List[str] = field(default_factory=list)
    last_accessed: Optional[datetime] = None


@dataclass
class Doctrine:
    """
    Represents a doctrine (structural truth) and its mutation lineage.
    """

    id: str
    name: str
    mutation_lineage: List[str] = field(default_factory=list)
    scar_links: List[str] = field(default_factory=list)
    status: str = "active"  # active | fossil | fallen
    created_at: datetime = field(default_factory=datetime.now)
    last_mutated: Optional[datetime] = None


@dataclass
class Echo:
    """
    Represents a symbolic echo or input fragment.
    """

    id: str
    content: str
    source: str  # e.g., user/system
    resonance_score: float
    created_at: datetime
    doctrine_link: Optional[str] = None
