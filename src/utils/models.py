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
    # RULING 76 (2026-08-05) - THE RECORD CARRIES ITS ORIGIN.
    #
    # A JOIN KEY, NOT AN ORIGIN FACT - `Echo.claim_id`'s exact class, and
    # Ruling 60's canonical key extended to the second record that a claim
    # cycle produces. It points at the claim-ancestry ledger line minted for the
    # claim whose collapse formed this scar; the LEDGER still stores origin ONCE
    # (L3 clean).
    #
    # **WHY IT HAD TO EXIST: THE ECHO->SCAR EDGE WAS RUNTIME HISTORY NOTHING
    # COULD DERIVE.** Ruling 75 measured both event edges vanishing at restart
    # and reported it rather than repairing it, because rebuilding NODES is not
    # rebuilding EDGES and no record carried the join. This is that join. With
    # it the edge becomes a DERIVATION over records, which is how everything
    # else in this house is rebuilt.
    #
    # SET AT CREATION, never by post-hoc mutation, and NEVER SYNTHESIZED.
    # `None` honestly means "no ancestry record backs this scar" - a legacy scar
    # written before this ruling, a seed scar that predates every claim, or one
    # formed outside `process_input`. **There is no backfill and no inference:**
    # matching a legacy scar to a claim by content would be the lexical-
    # similarity defect class, and manufacturing a join is exactly the
    # fabrication Rulings 58 and 70 spent themselves closing.
    claim_id: Optional[str] = None
    # RULING 76 res.2 - THE FORMATION PRESSURE, AS A FACT OF RECORD.
    #
    # The RAW `collapse_result.pressure_generated` at the moment this scar
    # formed. `weight` above is a DERIVATION of it (`min(pressure * 2.0, 5.0)`)
    # and is UNCHANGED - the two coexist, and neither rewrites the other
    # (Ruling 63's recorded-basis form: a derived value and the fact it came
    # from are different records of different things).
    #
    # **THE CLAMP IS WHY THIS FIELD IS NECESSARY RATHER THAN REDUNDANT.** Weight
    # saturates at 5.0, so every collapse at pressure >= 2.5 stores the SAME
    # weight and the raw pressure is UNRECOVERABLE from it. The echo->scar edge
    # is created at that raw pressure, so without this fact the edge cannot be
    # re-derived at all for a saturated scar - and "derive it from weight" would
    # silently invent a different graph.
    #
    # Legacy scars carry `None`, honestly, and derive no edge.
    origin_pressure: Optional[float] = None

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
    # ~~e.g., user/system~~  ~~source: str~~
    #
    # DEMOTED 2026-08-01 BY RULING 58; **DELETED 2026-08-02 BY RULING 68.**
    # Superseded in place, history kept, because Ruling 58's reasoning is the
    # record of why the field could not simply stay.
    #
    # IT WAS A LEGACY DISPLAY STRING AND IT WAS NEVER HONESTLY AN ORIGIN:
    # `process_input(raw_input, source="user")` handed a free-text DEFAULT down
    # to SPL, which wrote it here - into a durable store field - so every claim
    # the suite, the soak or any bare caller ever processed was on record as
    # having originated from a human user, including the ones that did not. A
    # fact stored because a field existed to hold it.
    #
    # RULING 58 DEMOTED IT AND SWEPT ITS READERS, and deferred the `"user"`
    # default as "not this ruling's remit". **DEMOTION IS DISCIPLINE, AND THE
    # MANUFACTURE CONTINUED UNDERNEATH IT:** one pass could carry
    # `origin_kind=undeclared` with all five ancestry fields ABSENT while
    # simultaneously reporting `source == 'user'` here and tagging its topology
    # node `source:user`. Ruling 68 is the ruling 58 deferred to, and it deletes
    # the parameter, this field, and the tag together - Ruling 61's form:
    # deletion, not deprecation, because an unread legacy field is a loaded gun
    # for the next caller who defaults it.
    #
    # THE SINGLE AUTHORITATIVE ORIGIN SURFACE IS THE CLAIM-ANCESTRY LEDGER
    # (`src/external/claim_ancestry.py`), which records origin ONCE, at ingress,
    # with a closed source vocabulary and an honest UNDECLARED for a channel
    # that said nothing. Reach it from `claim_id`, below.
    #
    # LEGACY BYTES ARE UNTOUCHED: every `"source": "user"` already written into a
    # store stays exactly where it is. Forensic record - no migration, and no
    # reader-side reinterpretation of what a stored value used to mean.
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
