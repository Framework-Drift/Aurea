from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Scar:
    """
    Represents a symbolic collapse event in AUREA.
    """

    id: str
    name: str                     # Canonical title or short label
    origin: str                   # Collapse cause, event, or doctrine root
    type: str = ""                # Symbolic type/category ("ethical", etc.)
    weight: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    # Canon decay vocabulary (Lexicon section 3), owned and typed by
    # `scar_management.DecayState` since Ruling 37:
    #     active -> waning -> dormant   (v1)
    #     fossilized | purged           (DECLARED, no v1 path)
    # Stored as the member's string VALUE so persisted records stay plain JSON.
    # This comment previously read "active | dormant | fossil | locked", which
    # named neither the canon sequence nor anything the code wrote.
    decay_state: str = "active"
    linked_doctrines: List[str] = field(default_factory=list)
    last_accessed: Optional[datetime] = None
    description: str = ""         # Human-readable meaning
    echo_proximity: List[str] = field(default_factory=list)
    reflexes: List[str] = field(default_factory=list)
    tca_tags: List[str] = field(default_factory=list)
    is_seed: bool = False

@dataclass
class Doctrine:
    """
    Represents a doctrine (structural truth) and its mutation lineage.
    """

    id: str
    name: str
    mutation_lineage: List[str] = field(default_factory=list)
    scar_links: List[str] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    last_mutated: Optional[datetime] = None
    description: str = ""
    tca_tags: List[str] = field(default_factory=list)
    is_seed: bool = False

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
