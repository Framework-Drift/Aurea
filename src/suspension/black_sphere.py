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

from src.utils.atomic_write import atomic_write_json


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

    # M4-beta' (2026-08-15): the mint's prefix, unchanged from the wall-clock
    # era.
    #
    # **THIS STORE HAS NO REMOVAL DOOR OF ITS OWN - AND IT GETS THE ENVELOPE
    # ANYWAY.** Paradoxes are permanent and `suspend` REFUSES at capacity
    # rather than purging, so a derive-from-survivors mint would be safe here
    # today. It would be safe only BY CURRENT CALLERS: `purge_old_entries` is
    # inherited from `SuspensionSystem` and is callable on this class right
    # now. Safe-by-current-callers is exactly the class that rots (Ruling 35's
    # vacuous guard; Ruling 32's "nothing prevented it but that no test happened
    # to do it"), and a store whose correctness rests on nobody calling an
    # inherited public method is one line away from the defect. Uniformity
    # removes the contingency, and here it costs one key on a dict this store
    # already writes.
    ID_PREFIX = "BS-"

    def __init__(self, capacity: int = 30, filepath: str = "data/runtime/suspension/black_sphere.json"):
        super().__init__(capacity)
        self.suspension_type = SuspensionType.BLACK_SPHERE
        self.filepath = Path(filepath)
        self.paradox_families: Dict[str, Set[str]] = {}  # Group related paradoxes
        self.gravitational_range = 0.3  # How far influence extends
        self.load_from_file()
        
    def suspend(self, content: Any,
                pressure: float, reason: str = "",
                paradox_type: str = "unknown", *,
                claim_id: Optional[str] = None) -> SuspensionEntry:
        """
        Suspend paradox in Black Sphere for perpetual orbit.

        RULING 84 (2026-08-11): the `source` parameter is DELETED. This door
        carried the one literal Ruling 83 classified as report-only
        (`source='pipeline'` at `aurea_core`) - true but vaguer than its
        siblings' module identities, and beside `claim_id` it was the field a
        reader would reach for while the join was the one that was true.

        Args:
            content: The paradoxical content
            pressure: Symbolic pressure (usually very high for paradoxes)
            reason: Reason for suspension
            paradox_type: Type of paradox (self-reference, gödel, etc.)
            claim_id: RULING 76 - the minted claim-ancestry id for the claim
                whose collapse produced this paradox, KEYWORD-ONLY (mirroring
                Ruling 58's `origin` and 60's `claim_id`). **THE JOIN THAT MAKES
                THE ECHO->PARADOX EDGE DERIVABLE**: before this ruling `suspend`
                received no id of any kind, so the edge written at suspension
                time was runtime history nothing could rebuild - Ruling 75
                measured `paradox_void` losing its center at every restart and
                reported it rather than repairing it.

                KEYWORD-ONLY so the two existing callers are unaffected and a
                future one cannot bind it positionally into `reason`.
                `None` is the honest default: the tether's suspensions
                (`session_governor`) have no claim cycle behind them and must
                not appear to. **Never synthesized, never backfilled.**

        Returns:
            SuspensionEntry for the orbiting paradox
        """
        # Black Sphere has strict capacity - paradoxes are heavy
        if self.is_at_capacity():
            # Cannot purge paradoxes - they're permanent
            # Must refuse new entries
            raise Exception(f"Black Sphere at capacity ({self.capacity}). Cannot suspend more paradoxes.")
            
        # Create entry
        #
        # M4-beta': MINTED from the high-water mark. A paradox node's id reaches
        # the topology (`place_paradox`) and `result['pass_nodes']`, so it is a
        # referent other records point at - which is why uniqueness here has to
        # be a property of the record rather than of the clock's resolution.
        entry = SuspensionEntry(
            id=self._mint_id(),
            content=str(content),  # Convert to string for safety
            suspension_type=SuspensionType.BLACK_SPHERE,
            pressure_level=pressure,
            reason=reason or f"Irreducible paradox at pressure {pressure:.2f}",
            orbit_stability=1.0,  # Perfect stability initially
            paradox_family=paradox_type,
            gravitational_influence=pressure * 0.3,  # Influence based on pressure
            claim_id=claim_id,      # Ruling 76: a fact of origin, recorded once
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
        
        # M4-beta': the entry list is built here and WRAPPED by `_envelope`
        # below, which adds `high_water` and carries `paradox_families` through
        # unchanged. For this store the schema change is ONE KEY on a dict it
        # already wrote - CSA's and VT's bare lists are the ones that change
        # shape.
        data = []

        for entry in self.entries.values():
            entry_dict = {
                'id': entry.id,
                'content': entry.content,
                # RULING 84: `'source': entry.source` STOOD HERE. The key is no
                # longer written; a legacy file that carries it is read without
                # it and never rewritten with it.
                'pressure_level': entry.pressure_level,
                'timestamp': entry.timestamp.isoformat(),
                'reason': entry.reason,
                'orbit_stability': entry.orbit_stability,
                'paradox_family': entry.paradox_family,
                'gravitational_influence': entry.gravitational_influence,
                'access_count': entry.access_count,
                'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                'metadata': entry.metadata,
                # RULING 76: the JOIN must SURVIVE THE FILE, or it is not a
                # join. This serializer writes an EXPLICIT field list, so a new
                # field is invisible to it until named here - and the first
                # measurement of this ruling caught exactly that: the scar edge
                # reformed at restart and the paradox edge did not, because
                # `claim_id` was being dropped at this boundary while the scar
                # store carried it through.
                'claim_id': entry.claim_id,
            }
            data.append(entry_dict)


        # Rider R3 (2026-07-29): ATOMIC. This method REBUILDS the whole file from
        # `self.entries` on every save, so mode "w" put every contradiction she
        # has ever set down at risk to record one more. The Black Sphere is where
        # she puts what she cannot hold - §10.G names it as outside her own
        # revision - and it was the least atomic write in the tree.
        atomic_write_json(
            self.filepath,
            self._envelope(
                data,
                paradox_families={k: list(v)
                                  for k, v in self.paradox_families.items()}),
            indent=2)

    def load_from_file(self):
        """Load Black Sphere entries from disk.

        M4-beta': a legacy file is a dict WITHOUT `high_water`, which
        `_absorb_envelope` treats exactly as it treats a bare list - derive
        once, from ids that (being wall-clock) do not parse, so 0. Both shapes
        load forever and neither is rewritten in place.
        """
        if not self.filepath.exists():
            return

        with open(self.filepath, 'r') as f:
            data = json.load(f)

        # Load entries
        for entry_dict in self._absorb_envelope(data):
            entry = SuspensionEntry(
                id=entry_dict['id'],
                content=entry_dict['content'],
                # RULING 84: `source=entry_dict['source']` STOOD HERE. This
                # loader reads EXPLICIT keys, so deleting the read is the whole
                # of era honesty - a legacy key is simply never consulted.
                suspension_type=SuspensionType.BLACK_SPHERE,
                pressure_level=entry_dict['pressure_level'],
                timestamp=datetime.fromisoformat(entry_dict['timestamp']),
                reason=entry_dict['reason'],
                orbit_stability=entry_dict['orbit_stability'],
                paradox_family=entry_dict.get('paradox_family'),
                gravitational_influence=entry_dict['gravitational_influence'],
                access_count=entry_dict.get('access_count', 0),
                last_accessed=datetime.fromisoformat(entry_dict['last_accessed']) if entry_dict.get('last_accessed') else None,
                metadata=entry_dict.get('metadata', {}),
                # RULING 76, read with Ruling 75's TOLERANT form: `.get` so a
                # legacy entry written before this ruling loads clean and
                # carries `None`. Its bytes are untouched, it derives no edge,
                # and nothing is inferred to fill the gap - ABSENT is a real
                # answer (Rulings 58/70).
                claim_id=entry_dict.get('claim_id'),
            )
            self.entries[entry.id] = entry
            
        # Load families
        self.paradox_families = {
            k: set(v) for k, v in data.get('paradox_families', {}).items()
        }
