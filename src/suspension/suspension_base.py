"""
suspension_base.py - Base classes for AUREA's suspension systems
Foundation for CSA, Veiled Thread, and Black Sphere.

M4-beta' (2026-08-15) - THE HIGH-WATER ENVELOPE
-------------------------------------------------------------------------------
**A MINT THAT DERIVES FROM SURVIVING ENTRIES REISSUES THE IDS OF THE DEAD.**

M4-beta proposed moving the three wall-clock ids (`CSA-`/`BS-`/`VT-`) to the
file-derived ordinal mint that Ruling 69 gave the append-only ledgers, and the
M4-alpha pass STOPPED it on a witnessed premise defect: **these are SNAPSHOT
stores that REMOVE entries**, so a max-over-the-live-file derivation DROPS when
one is purged. Measured then, and pinned now: after
`VeiledThread.extract_emerged('VT-0003')` - the store's own fermentation-success
path - the derivation falls 3 -> 2 and the next mint reissues `VT-0003`.

That is barred by the laws the STOP cited, each of which speaks to exactly this:
Ruling 69 (*"any id that reached disk is seen and never reissued... given a
choice between burning an ordinal and forging one, burn it"*), Ruling 42 res.4
(the mint derives over live **AND** removed ids), and Ruling 65's own stated
reopening condition (*"if a removal path is ever added the mint needs a real
issued-set again"*).

**RULING 81 ALREADY RATIFIED THE REMEDY FOR A SNAPSHOT STORE**, and this is it,
verbatim: a counter carried INSIDE the snapshot it numbers is not a cached
derivation - IT IS THE RECORD. It rides in the same atomic write as the entries,
persists at the moment of minting, and is floor-validated at load. The
distinction from the `_seq` counters Ruling 69 deleted is structural rather than
one of degree: those were derived once from a file and then trusted over it
forever; this one is written to the file every time it moves.

WHY THE ENVELOPE IS ON ALL THREE, INCLUDING THE ONE THAT CANNOT PURGE
-------------------------------------------------------------------------------
The census (2026-08-15, by AST) found the removal doors are:

    suspension_base   purge_old_entries                                    (1)
    csa               emergency_purge, update_dormancy                     (2)
    veiled_thread     extract_emerged, _purge_low_potential_entries        (2)
    black_sphere      - none of its own -                                  (0)

**AND `purge_old_entries` IS INHERITED, SO IT IS CALLABLE ON ALL THREE**, the
Black Sphere included - zero callers today, which is precisely the shape that
rots. Safe-by-current-callers is not safe; the envelope goes on all three, and
for the Black Sphere that is one key on a dict it already writes.

    TWO CORRECTIONS TO THE HANDOFF'S CENSUS, ON THE RECORD, neither of which
    changes the design (the envelope goes on all three either way):
      * CSA's own doors are `emergency_purge` AND **`update_dormancy`** - the
        auto-purge of entries past `max_dormancy`, which the handoff did not
        name. It counted the inherited base door as CSA's second.
      * VT has TWO own doors, not three: **`check_emergence` REMOVES NOTHING**
        (it returns a bool). `extract_emerged` and
        `_purge_low_potential_entries` are the real ones.
    So the tree holds MORE removal paths than the handoff counted on CSA and
    FEWER on VT, and the un-named one strengthens the ruling's own case.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

from src.utils.ledger_mint import mint_lock

# THE SUPERSEDED ID FORMAT, KEPT BECAUSE ERA HONESTY IS ABOUT KNOWING IT.
#
# Every id these three stores minted before this ruling was
# `{PREFIX}-{datetime.now().strftime(LEGACY_ID_FORMAT)}`. The width is DERIVED
# from the format rather than asserted, so it cannot drift from the thing it
# describes: 4+2+2+2+2+2+6 = 20 digits, for every year this system can express.
LEGACY_ID_FORMAT = "%Y%m%d%H%M%S%f"
_LEGACY_ID_DIGITS = len(datetime(2026, 1, 1).strftime(LEGACY_ID_FORMAT))


class HighWaterRegression(Exception):
    """A save would have written a `high_water` BELOW the one it loaded.

    The wrong path made UNEXECUTABLE rather than merely discouraged (CLAUDE.md
    section 3). Nothing in the pipeline can lower a high-water mark - the
    counter is incremented at mint and read nowhere else - so this can only be
    reached by a caller assigning to it directly, which is a programming error
    rather than one of AUREA's guards firing.

    **DELIBERATELY NOT IN `STRUCTURAL_VIOLATIONS`** (Ruling 48's partition, and
    Docket N's form): it is unreachable from `process_input`, and a member added
    on speculation is a decision made without a case. If a path ever lowers a
    high-water mark, that is when membership gets ruled on.
    """


def _legacy_ordinal(entry_id: Any, prefix: str) -> Optional[int]:
    """The ordinal behind `{prefix}NNNN`, or `None` if this is not one.

    **A PURE-LEGACY WALL-CLOCK ID MUST NEVER PARSE**, and that is the whole
    delicacy of this function. `CSA-20260815083435413404` is `CSA-` followed by
    a digit run, so a naive `\\d+` scan would read it as an ordinal of twenty
    digits and set the high-water mark to a number no mint could ever catch -
    turning the index into nonsense while looking like it worked.

    So a digit run of EXACTLY the superseded format's width is rejected. That is
    a FACT ABOUT THE FORMAT THIS RULING SUPERSEDES, derived from the format
    string itself, and not a coined threshold: it stops being a rejection the
    day an honest ordinal reaches twenty digits, which is 10^19 suspensions.

    Everything else parses, so a file hand-written with `CSA-0007` and no
    envelope still initializes at 7 rather than at 0.
    """
    if not isinstance(entry_id, str):
        return None
    match = re.fullmatch(re.escape(prefix) + r"(\d+)", entry_id)
    if match is None or len(match.group(1)) == _LEGACY_ID_DIGITS:
        return None
    return int(match.group(1))


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
    
    # M4-beta': the id prefix each store mints under. Set by every subclass; the
    # base has none, because the base suspends nothing.
    ID_PREFIX: Optional[str] = None

    def __init__(self, capacity: int = 100):
        self.entries: Dict[str, SuspensionEntry] = {}
        self.capacity = capacity
        self.suspension_type: SuspensionType = None
        self.total_suspended = 0
        self.last_purge: Optional[datetime] = None
        # M4-beta' - THE HIGH-WATER MARK. Monotonic, incremented at MINT, and
        # persisted in the SAME atomic write as the entries it numbers.
        #
        # **IT IS NOT A CACHED DERIVATION OF THE FILE** (Ruling 81's whole
        # distinction): the `_seq` counters Ruling 69 deleted were derived once
        # and then trusted over their source forever, while this is written back
        # every time it moves. What it must NEVER be re-derived from is the
        # SURVIVING entries - that is the reissue defect this ruling exists to
        # close, and the derivation below runs only for a file that predates the
        # envelope entirely.
        self.high_water: int = 0
        # THE FLOOR: the highest mark this store has ever READ FROM A FILE or
        # COMMITTED TO ONE. A save may never write below it.
        #
        # **IT ADVANCES ON SAVE AS WELL AS ON LOAD, AND THAT IS THE STRONGER
        # READING TAKEN DELIBERATELY.** A floor fixed at load time would catch a
        # regression below the value this process STARTED with and wave through
        # one below the value it has since WRITTEN - so a store that saved 3 and
        # then saved 1 would record the second silently. The property worth
        # having is that the mark never decreases across any save / load /
        # removal sequence, and only a floor that tracks writes can say that.
        self._high_water_floor: int = 0

    # -----------------------------------------------------------------
    # M4-beta' - THE MINT AND THE ENVELOPE
    # -----------------------------------------------------------------

    def _mint_id(self) -> str:
        """The next id for this store. **NEVER derived from surviving entries.**

        Held under the shared `mint_lock` keyed by this store's RESOLVED FILE
        PATH (Ruling 69 res.3's discipline): the thing being protected is one
        file's increment-and-write sequence, and two instances over one path
        must take the same lock.

        `{PREFIX}{n:04d}` matches the house ordinal shape, and it GROWS PAST
        9999 rather than wrapping - CAE's rule, and the reason the width is a
        minimum rather than a cap.
        """
        if not self.ID_PREFIX:
            raise NotImplementedError(
                f"{type(self).__name__} mints ids but declares no ID_PREFIX. A "
                f"store without a prefix cannot mint an id that is unambiguous "
                f"about which store issued it.")
        with mint_lock(self.filepath):
            self.high_water += 1
            return f"{self.ID_PREFIX}{self.high_water:04d}"

    def _absorb_envelope(self, data: Any) -> List[Dict[str, Any]]:
        """Read a snapshot of EITHER shape and return its entry dicts.

        **BOTH SHAPES LOAD FOREVER; ONLY SAVES WRITE THE ENVELOPE.** A legacy
        file is never rewritten in place and never reinterpreted (Ruling 68's
        forensic law) - it is simply read by a loader that knows both eras.

            envelope  {"high_water": N, "entries": [...], ...}   -> N is READ
            bare list [...]                                      -> DERIVED once
            dict, no high_water (legacy Black Sphere)             -> DERIVED once

        THE DERIVATION IS A ONE-TIME LEGACY BRIDGE AND NOTHING ELSE. It runs
        only for a file written before the envelope existed, and such a file
        holds only wall-clock ids, which `_legacy_ordinal` refuses - so the
        honest answer for a pure-legacy file is 0, and a fresh mint of
        `{PREFIX}0001` cannot collide with a twenty-digit id.

        **A FILE THAT CARRIES THE ENVELOPE NEVER RE-DERIVES**, which is the
        property the whole ruling rests on: once ids have been issued, the
        record of how many says so, and no amount of purging can lower it.
        """
        if isinstance(data, dict):
            entries = data.get("entries", [])
            recorded = data.get("high_water")
            if isinstance(recorded, int) and not isinstance(recorded, bool):
                self.high_water = self._high_water_floor = max(recorded, 0)
                return entries if isinstance(entries, list) else []
        else:
            entries = data if isinstance(data, list) else []

        entries = entries if isinstance(entries, list) else []
        derived = 0
        for entry_dict in entries:
            if not isinstance(entry_dict, dict):
                continue
            ordinal = _legacy_ordinal(entry_dict.get("id"), self.ID_PREFIX or "")
            if ordinal is not None:
                derived = max(derived, ordinal)
        self.high_water = self._high_water_floor = derived
        return entries

    def _envelope(self, entries: List[Dict[str, Any]],
                  **extra: Any) -> Dict[str, Any]:
        """Wrap this store's serialized entries with its high-water mark.

        THE GUARD IS HERE, AT THE WRITE, because this is the only place a
        regression could reach disk. A save that would record FEWER ids issued
        than the file already records is the reissue defect arriving through
        the back door, so it RAISES rather than repairing itself to the floor -
        a silent `max()` here would hide the very state worth knowing about.
        """
        if self.high_water < self._high_water_floor:
            raise HighWaterRegression(
                f"{type(self).__name__} would save high_water="
                f"{self.high_water} over a file recording "
                f"{self._high_water_floor}. A high-water mark is monotonic by "
                f"construction - it is incremented at mint and read nowhere "
                f"else - so lowering one means an id already issued could be "
                f"minted again, which is the defect the envelope exists to "
                f"close.")
        # The floor advances to what is about to be written. If the write then
        # fails, the floor is merely ahead of the file, which refuses nothing a
        # later honest save would want to do.
        self._high_water_floor = self.high_water
        return {"high_water": self.high_water, "entries": entries, **extra}

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
