# Aurea API Reference

---

## Models (`src/utils/models.py`)

### Scar
```python
@dataclass
class Scar:
    id: str
    origin: str
    weight: float
    created_at: datetime
    decay_state: str = "active"
    linked_doctrines: List[str] = field(default_factory=list)
    last_accessed: Optional[datetime] = None

@dataclass
class Doctrine:
    id: str
    name: str
    mutation_lineage: List[str] = field(default_factory=list)
    scar_links: List[str] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    last_mutated: Optional[datetime] = None

@dataclass
class Echo:
    id: str
    content: str
    source: str
    resonance_score: float
    created_at: datetime
    doctrine_link: Optional[str] = None

class SPL:
    def process_input(self, raw_input: str) -> Echo:
        """Normalize and classify input, returning an Echo object."""

    def classify_intent(self, echo: Echo) -> str:
        """Classify the intent of the input (question, claim, command, etc.)."""

class EchoNet:
    def filter_claim(self, echo: Echo) -> bool:
        """Filter an Echo for collapse-resistance, return True if it passes."""

    def collapse_test(self, echo: Echo) -> Scar:
        """Attempt to collapse an echo. Returns a Scar if successful."""

class ScarLogicCore:
    def add_scar(self, scar: Scar) -> None:
        """Add a scar to the system."""
    
    def decay_scar(self, scar_id: str) -> None:
        """Decay or retire a scar by ID."""

    def get_active_scars(self) -> List[Scar]:
        """Return all active scars."""

class DoctrineSpine:
    def add_doctrine(self, doctrine: Doctrine) -> None:
        """Add a new doctrine."""

    def mutate_doctrine(self, doctrine_id: str, new_data: dict) -> None:
        """Mutate an existing doctrine."""

    def get_doctrine(self, doctrine_id: str) -> Doctrine:
        """Fetch a doctrine by ID."""

class RACM:
    def resolve_reflex_priority(self, reflex_chain: List[str], ...) -> Optional[str]:
        """Resolve which reflex takes priority in a symbolic conflict."""

    def detect_reflex_deadlock(self, reflex_chain: List[str]) -> bool:
        """Detect deadlocks between simultaneous reflexes."""

    def log_reflex_override(self, reflex: str, cause: str, cae_id: Optional[str] = None) -> None:
        """Log an override event for auditing."""

