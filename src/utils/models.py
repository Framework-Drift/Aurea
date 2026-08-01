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
    # ~~e.g., user/system~~
    #
    # DEMOTED 2026-08-01 BY RULING 58, superseded in place with history kept.
    # THIS IS A LEGACY DISPLAY STRING. It is NOT the origin of the claim, and it
    # never honestly was: `process_input(raw_input, source="user")` handed a
    # free-text DEFAULT down to SPL, which wrote it here - into a durable store
    # field - so every claim the suite, the soak or any bare caller has ever
    # processed is on record as having originated from a human user, including
    # the ones that did not. A fact stored because a field existed to hold it.
    #
    # THE SINGLE AUTHORITATIVE ORIGIN SURFACE IS THE CLAIM-ANCESTRY LEDGER
    # (`src/external/claim_ancestry.py`), which records origin ONCE, at ingress,
    # with a closed source vocabulary and an honest UNDECLARED for a channel
    # that said nothing. Read origin from there.
    #
    # THE `"user"` DEFAULT IS UNTOUCHED THIS PASS, deliberately: those bytes are
    # already in persisted stores and rewriting them is not Ruling 58's remit.
    # A sweep of `src/` at that ruling found ZERO readers of this field - the
    # only consumer anywhere is a display line in `scripts/aurea_diagnostic.py`
    # - so the demotion changes no behaviour. Do not add a reader.
    source: str
    resonance_score: float
    created_at: datetime
    doctrine_link: Optional[str] = None
    # RULING 60 (2026-08-01) / DOCKET O item O2 - THE ECHO <-> CLAIM LINKAGE.
    #
    # A JOIN KEY, NOT AN ORIGIN FACT. It points at the claim-ancestry ledger
    # line minted for this claim at ingress; the LEDGER still stores origin
    # ONCE (L3 clean). This is identity linkage - the same reference class as
    # scar lineage - and it points BACKWARD IN TIME, as references should.
    #
    # THE DIRECTION IS FORCED BY RULING 58'S OWN STRUCTURE, not chosen for
    # convenience: the ancestry record is deep-frozen and minted BEFORE the echo
    # exists (after the suspension gate, before the SPL wrap), so the RECORD
    # cannot carry an echo id without mutating a frozen record or deferring the
    # gate - both barred by 58 itself. The LATER artifact references the
    # EARLIER one. A third linkage store was REFUSED: it would duplicate one
    # Optional field with a new owner, a new sentinel and a new path.
    #
    # NEVER SYNTHESIZED. It is the actual minted id or None. `None` honestly
    # means "no ancestry record backs this echo" - a legacy persisted echo that
    # predates the ledger, or an echo built outside `process_input` (SPL called
    # standalone, or an internal probe, which is not a perceived claim). Every
    # echo through `process_input` carries it, because the mint GATES
    # PERCEPTION: the id exists before any echo can.
    claim_id: Optional[str] = None
