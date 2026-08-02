"""
tca_core.py - Topological Constellation Architecture Core
The spatial substrate where AUREA's symbolic reasoning occurs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
import math
import json
from pathlib import Path
from enum import Enum

from src.utils.atomic_write import atomic_write_json


class NodeType(Enum):
    """Types of nodes in the constellation."""
    SCAR = "scar"
    DOCTRINE = "doctrine"
    PARADOX = "paradox"
    ECHO = "echo"
    ANCHOR = "anchor"
    SUSPENSION = "suspension"
    VOID = "void"  # Empty space with significance


class ConstellationType(Enum):
    """Types of constellations based on dominant content."""
    IDENTITY = "identity"          # Self-defining clusters
    ETHICAL = "ethical"            # Moral reasoning regions
    LOGICAL = "logical"            # Logical reasoning regions
    EMPIRICAL = "empirical"        # Evidence-based regions
    CREATIVE = "creative"          # Nova/hypothesis regions
    SHADOW = "shadow"              # Suppressed/quarantined regions
    PARADOXICAL = "paradoxical"    # Black Sphere regions


@dataclass
class SymbolicPosition:
    """
    Position in symbolic space. Not Euclidean coordinates but
    semantic dimensions that define meaning-space.
    """
    # Primary dimensions
    semantic_vector: Dict[str, float] = field(default_factory=dict)  # Meaning dimensions
    temporal_layer: float = 0.0  # When in time (for ChronoLayer integration)
    collapse_depth: float = 0.0  # How many collapses deep
    
    # Relational position
    constellation_id: Optional[str] = None
    orbital_center: Optional[str] = None  # If orbiting something
    
    # Derived metrics
    stability: float = 1.0  # How stable this position is
    drift_velocity: Dict[str, float] = field(default_factory=dict)  # Movement in space
    
    def distance_to(self, other: 'SymbolicPosition') -> float:
        """Calculate symbolic distance to another position."""
        if not self.semantic_vector or not other.semantic_vector:
            return float('inf')
        
        # Semantic distance (cosine similarity inverted)
        common_dims = set(self.semantic_vector.keys()) & set(other.semantic_vector.keys())
        if not common_dims:
            return 1.0  # Maximum distance if no common dimensions
        
        dot_product = sum(self.semantic_vector.get(d, 0) * other.semantic_vector.get(d, 0) 
                         for d in common_dims)
        
        magnitude_self = math.sqrt(sum(v**2 for v in self.semantic_vector.values()))
        magnitude_other = math.sqrt(sum(v**2 for v in other.semantic_vector.values()))
        
        # Use small epsilon for robustness
        eps = 1e-8
        magnitude_self = max(eps, magnitude_self)
        magnitude_other = max(eps, magnitude_other)
        
        similarity = dot_product / (magnitude_self * magnitude_other)
        distance = 1.0 - similarity
        
        # Adjust for temporal distance
        temporal_distance = abs(self.temporal_layer - other.temporal_layer) * 0.1
        
        # Adjust for collapse depth difference
        collapse_distance = abs(self.collapse_depth - other.collapse_depth) * 0.2
        
        return min(distance + temporal_distance + collapse_distance, 2.0)


@dataclass
class ConstellationNode:
    """A node in the topological constellation."""
    id: str
    node_type: NodeType
    position: SymbolicPosition
    
    # Physical properties
    mass: float = 1.0  # Gravitational mass (influences others)
    charge: float = 0.0  # Positive = attracts similar, Negative = repels
    spin: float = 0.0  # Rotational dynamics (for paradoxes)
    
    # Connections
    edges: Dict[str, float] = field(default_factory=dict)  # Connected nodes and weights
    scar_bridges: List[str] = field(default_factory=list)  # Scar-carved shortcuts
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    tags: Set[str] = field(default_factory=set)
    
    def gravitational_force_on(self, other: 'ConstellationNode') -> float:
        """Calculate gravitational force this node exerts on another."""
        distance = self.position.distance_to(other.position)
        if distance == 0:
            return float('inf')  # Collision
        
        # F = G * (m1 * m2) / r^2
        G = 0.3  # Gravitational constant for symbolic space
        force = G * (self.mass * other.mass) / (distance ** 2)
        
        # Charge can modify attraction/repulsion
        if self.charge != 0 and other.charge != 0:
            # Same charge = repulsion, opposite = attraction
            charge_factor = -1 if (self.charge * other.charge > 0) else 1
            force *= (1 + abs(self.charge * other.charge) * charge_factor * 0.5)
        
        return force


@dataclass
class Constellation:
    """A cluster of related nodes forming a symbolic constellation."""
    id: str
    constellation_type: ConstellationType
    nodes: Dict[str, ConstellationNode] = field(default_factory=dict)
    
    # Constellation properties
    gravity_center: Optional[str] = None  # Node ID that anchors this constellation
    total_mass: float = 0.0
    avg_collapse_depth: float = 0.0
    
    # Boundaries
    radius: float = 1.0  # Approximate size
    membrane_strength: float = 0.5  # How strongly it maintains boundaries
    
    # Dynamics
    rotation_rate: float = 0.0  # If the constellation rotates
    expansion_rate: float = 0.0  # If growing or shrinking
    stability: float = 1.0
    
    # Connections to other constellations
    bridges: Dict[str, float] = field(default_factory=dict)  # constellation_id -> strength
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_reconfigured: Optional[datetime] = None
    
    def add_node(self, node: ConstellationNode):
        """Add a node to this constellation."""
        self.nodes[node.id] = node
        node.position.constellation_id = self.id
        self.total_mass += node.mass
        self._recalculate_center()
    
    def remove_node(self, node_id: str):
        """Remove a node from this constellation."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            self.total_mass -= node.mass
            del self.nodes[node_id]
            self._recalculate_center()
    
    def _recalculate_center(self):
        """Recalculate the gravitational center of the constellation."""
        if not self.nodes:
            self.gravity_center = None
            return
        
        # Find node with highest mass * centrality
        max_weight = 0
        center_id = None
        
        for node_id, node in self.nodes.items():
            # Centrality = mass * number of connections
            centrality = node.mass * len(node.edges)
            if centrality > max_weight:
                max_weight = centrality
                center_id = node_id
        
        self.gravity_center = center_id
        
        # Update average collapse depth
        if self.nodes:
            self.avg_collapse_depth = sum(n.position.collapse_depth for n in self.nodes.values()) / len(self.nodes)
    
    def calculate_cohesion(self) -> float:
        """Calculate how tightly bound this constellation is."""
        if len(self.nodes) < 2:
            return 1.0
        
        # Average distance between all nodes
        total_distance = 0
        comparisons = 0
        
        nodes_list = list(self.nodes.values())
        for i, node1 in enumerate(nodes_list):
            for node2 in nodes_list[i+1:]:
                total_distance += node1.position.distance_to(node2.position)
                comparisons += 1
        
        if comparisons == 0:
            return 1.0
        
        avg_distance = total_distance / comparisons
        
        # Cohesion is inverse of average distance
        cohesion = 1.0 / (1.0 + avg_distance)
        
        # Factor in gravitational binding
        if self.total_mass > 0:
            mass_factor = min(self.total_mass / 100, 1.0)  # Cap at 100 mass
            cohesion *= (1 + mass_factor * 0.5)
        
        return min(cohesion, 1.0)


class TopologicalSpace:
    """
    The complete topological space where AUREA's reasoning occurs.
    This is the substrate for all symbolic thought.
    """
    
    STATE_VERSION = 1

    def __init__(self, filepath: str = "data/runtime/topology/tca_map.json"):
        self.filepath = Path(filepath)
        
        # All nodes in the space
        self.nodes: Dict[str, ConstellationNode] = {}
        
        # Constellations (clusters of nodes)
        self.constellations: Dict[str, Constellation] = {}
        
        # Special regions
        self.void_zones: List[SymbolicPosition] = []  # Areas of emptiness
        self.wormholes: Dict[str, Tuple[str, str]] = {}  # Shortcuts between distant nodes
        self.event_horizons: Set[str] = set()  # Constellation IDs that are black holes
        
        # Global properties
        self.total_mass = 0.0
        self.expansion_rate = 0.0
        self.highest_gravity_point: Optional[str] = None
        
        # Metrics
        self.fragmentation_index = 0.0  # How disconnected the space is
        self.total_edges = 0

        self.persist_failures: List[Dict[str, Any]] = []

        # RULING 65 (2026-08-02) - THE MAP IS A DERIVATION, AND A DERIVATION IS
        # REBUILT, NEVER RESTORED.
        #
        # THERE IS NO `self.load_from_file()` HERE, AND THERE IS NO
        # `load_from_file` ON THIS CLASS. That is res.1, and its absence is
        # SHAPE (Ruling 61's form), not an omission: a load method that exists
        # but is uncalled is a loaded gun for a later "helpful" pass.
        #
        # WHAT THE READ PATH COST, MEASURED (sixty-second entry, verbatim): the
        # space loaded every persisted node, then `AureaCore.__init__` re-placed
        # every scar and doctrine on top. `add_node` REPLACED by id but
        # incremented mass unconditionally, so `total_mass` locked at exactly 2x
        # from the first restart (130.6 -> 261.2). Scar re-placement's reverse
        # loop then found doctrine nodes that only exist after a load, minting
        # nine edges a fresh boot does not have; the doctrine loop re-placed
        # those doctrines with fresh empty-edge nodes, wiping the back-references
        # and leaving all nine ONE-WAY. Centrality is `mass * len(edges)`, so
        # `identity_core`'s gravity center moved AVT.014 -> Delta-77, and
        # `total_edges` read 40 against a true 21.
        #
        # NONE OF THAT IS FIXED. The path that produces it does not exist.
        #
        # WHY DELETION IS THE RIGHT INSTRUMENT AND A REPAIR WAS NOT: this map is
        # a PURE DERIVATION over three persisted stores (scars, doctrines,
        # Black Sphere paradoxes) plus in-process echoes. There is no
        # runtime-only node whose referent survives a restart - an echo's record
        # persists NOWHERE, so a persisted echo node asserts a holding no store
        # holds. A derivation kept as a source is exactly what Ruling 63 res.1
        # refused one layer up ("a cached projection is a stale authority
        # waiting for a trusting reader") - and here the trusting reader was
        # already identified and already paying.
        #
        # `load_report` and `quarantined_edges` LEFT WITH THE READ PATH THEY
        # SERVED (res.1/res.2). Ruling 42 Slice 2's restoration contract -
        # version gate, reported outcome, refusal, reference validation - was a
        # CORRECT contract applied to a store that should never have been one,
        # and it is SUPERSEDED FOR THIS STORE ONLY. It stands, unweakened, for
        # every actual store. Nothing is read, so nothing can be refused, so
        # sticky refusal has no meaning here either.
        #
        # `save_to_file` SURVIVES, WRITE-ONLY (res.3) - see its docstring.

    def add_node(self, node_id: str, node_type: NodeType, 
                 mass: float = 1.0, position: Optional[SymbolicPosition] = None,
                 constellation_id: Optional[str] = None) -> ConstellationNode:
        """Add a new node to the topological space.

        RULING 65 res.6 (2026-08-02) - REPLACEMENT IS MASS-CORRECT.

        THE PROPERTY, which is what is ruled and pinned: after `add_node` on an
        id this space already holds, `total_mass` equals the sum of the masses
        of the nodes actually held. How that is achieved is an implementation
        choice; that it holds is not.

        The old body wrote `self.nodes[node_id] = node` (a REPLACE) and then
        `self.total_mass += mass` (an unconditional ADD), so a replacement
        counted its mass twice while the node count did not move. Under the
        deleted read path that produced a permanent 2x overcount at every
        restart; the rebuild removes that caller, but the arithmetic was wrong
        on its own terms and is corrected here rather than left to depend on
        nobody re-placing a node.

        RE-PLACEMENT WITHIN A BOOT IS NOT RULED ILLEGITIMATE - doctrine mutation
        may lawfully re-place a node - so the ARITHMETIC is made honest rather
        than the OPERATION refused. Constellation membership is part of the same
        property: a replaced node must not be double-counted in its
        constellation's `total_mass` either, which is why the outgoing node is
        removed from whatever constellation held it before the new one is filed.
        """

        # Create position if not provided
        if position is None:
            position = self._find_optimal_position(node_type)

        # Create node
        node = ConstellationNode(
            id=node_id,
            node_type=node_type,
            position=position,
            mass=mass
        )

        # res.6: discharge the outgoing node before filing the new one, at BOTH
        # levels. `Constellation.remove_node` already decrements its own
        # `total_mass` and re-selects its center, so routing through it keeps one
        # owner for that arithmetic instead of a second copy here.
        previous = self.nodes.get(node_id)
        if previous is not None:
            self.total_mass -= previous.mass
            for constellation in self.constellations.values():
                if node_id in constellation.nodes:
                    constellation.remove_node(node_id)

        # Add to space
        self.nodes[node_id] = node
        self.total_mass += mass

        # Add to constellation if specified
        if constellation_id and constellation_id in self.constellations:
            self.constellations[constellation_id].add_node(node)
        elif not constellation_id:
            # Find nearest constellation
            nearest = self._find_nearest_constellation(position)
            if nearest:
                self.constellations[nearest].add_node(node)
        
        return node
    
    def create_edge(self, node1_id: str, node2_id: str, weight: float = 1.0):
        """Create an edge between two nodes.

        RULING 57 res.2 (2026-07-31) - CENTERS FOLLOW EDGES.

        A constellation's gravity center is selected by `mass * len(edges)`, and
        until this ruling that selection ran ONLY from `add_node` / `remove_node`
        - i.e. at MEMBERSHIP time, which for every node is BEFORE its edges
        exist. So a center was computed from a graph in which nothing was
        connected yet and then never revisited.

        That is the structural half of Ruling 57, and without it res.1's
        scars-first ordering is not enough: the scar nodes' own recalculation
        would still have run at add time, pre-edge, leaving their constellations
        centerless. It is also `paradox_void`'s 75-cycle lag in the Docket P
        soak, exactly - the Black Sphere node acquired its edge one statement
        after being added, and nothing recomputed until the NEXT node arrived.

        CANON ENDORSES CENTERS THAT MOVE, BY NAME: constellations "anchor
        identity to NEW gravity centers" (0_Core:92). A center that is computed
        once and frozen is not the thing canon describes.

        THE SELECTION RULE ITSELF IS UNTOUCHED - the strict `>` against an
        initial `max_weight = 0` in `_recalculate_center` is the tree's own
        declared rule and this ruling coins nothing. What changes is WHEN it is
        asked, never HOW it answers.

        A node outside any constellation triggers nothing for its side: there is
        no membership to recalculate, and inventing one here would be a
        placement rule wearing a refresh's clothes.
        """
        if node1_id in self.nodes and node2_id in self.nodes:
            # Guard against duplicate edges
            if node2_id not in self.nodes[node1_id].edges:
                self.nodes[node1_id].edges[node2_id] = weight
                self.nodes[node2_id].edges[node1_id] = weight
                self.total_edges += 1
                self._refresh_centers(node1_id, node2_id)

    def _refresh_centers(self, *node_ids: str) -> None:
        """Re-select the gravity center of each given node's constellation.

        RULING 57 res.2. Deduplicated, because both endpoints of an edge are
        very often in the SAME constellation and recalculating it twice is
        wasted work with no different answer.
        """
        seen = set()
        for node_id in node_ids:
            node = self.nodes.get(node_id)
            constellation_id = getattr(node.position, "constellation_id", None) \
                if node is not None else None
            if constellation_id is None or constellation_id in seen:
                continue
            seen.add(constellation_id)
            constellation = self.constellations.get(constellation_id)
            if constellation is not None:
                constellation._recalculate_center()
    
    def create_scar_bridge(self, node1_id: str, node2_id: str):
        """Create a scar-carved shortcut between distant nodes."""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.nodes[node1_id].scar_bridges.append(node2_id)
            self.nodes[node2_id].scar_bridges.append(node1_id)
            
            # Record as wormhole
            self.wormholes[self._next_bridge_id()] = (node1_id, node2_id)

    def _next_bridge_id(self) -> str:
        """MAX ORDINAL + 1 over the ids this space currently holds.

        RULING 42 res.4 ORIGINALLY - "the mint counts what has been ISSUED, not
        what is currently present" - derived over live AND QUARANTINED ids,
        because quarantine held a dangling wormhole OUT of `self.wormholes` and
        so was a removal in every sense `len()` cared about.

        RULING 65 res.7 (2026-08-02) - CONSCIOUSLY NARROWED FOR THIS STORE, and
        recorded here so the narrowing is a RULING rather than a drift.

        Quarantine is gone with the read path (res.1), so there is no longer any
        set of ids that were issued and are not present: nothing removes a
        wormhole, and a wormhole is only ever minted by
        `_create_identity_bridges` inside `place_scar`. BRIDGE IDS ARE THEREFORE
        PER-BOOT DERIVATIONS. Issuance restarts each boot and derives IDENTICALLY
        each boot, because placement order is deterministic (scar-store order,
        then dict insertion order), and nothing outside the write-only snapshot
        references a bridge id.

        THE MAX-ORDINAL FORM IS KEPT, AND IT IS NOT A REMOVAL GUARANTEE. An
        earlier draft of this docstring claimed it "stays correct if anything
        ever does [remove]", and A MUTATION TEST PROVED THAT FALSE: with the
        quarantine term gone, max-ordinal over LIVE ids and
        `len(self.wormholes)` are EQUIVALENT IN EVERY CASE, including after a
        removal - delete `bridge_0` from an otherwise empty dict and both mint
        `bridge_0` again. It was the QUARANTINED term, not the max-ordinal
        shape, that made the old expression removal-safe, and that term left
        with the read path.

        So this form is kept for legibility (it says "the next unused ordinal"
        rather than "the count"), NOT for a safety property it does not have.
        The correction is recorded rather than quietly fixed because a false
        justification in a docstring is worse than none: the next reader would
        have trusted it.

        IF A REMOVAL PATH IS EVER ADDED, THIS MINT NEEDS A REAL ISSUED-SET AGAIN
        - that is the reopening condition, and res.7's per-boot narrowing is
        only sound while nothing removes. An unparseable id contributes nothing
        rather than raising - this is a floor.
        """
        highest = -1
        for bridge_id in self.wormholes:
            if isinstance(bridge_id, str) and bridge_id.startswith("bridge_"):
                tail = bridge_id[len("bridge_"):]
                if tail.isdigit():
                    highest = max(highest, int(tail))
        return f"bridge_{highest + 1}"
    
    def create_constellation(self, constellation_id: str, 
                           constellation_type: ConstellationType,
                           node_ids: List[str] = None) -> Constellation:
        """Create a new constellation."""
        constellation = Constellation(
            id=constellation_id,
            constellation_type=constellation_type
        )
        
        # Add initial nodes if provided
        if node_ids:
            for node_id in node_ids:
                if node_id in self.nodes:
                    constellation.add_node(self.nodes[node_id])
        
        self.constellations[constellation_id] = constellation
        return constellation
    
    def find_path(self, start_id: str, end_id: str, 
                  use_scar_bridges: bool = True) -> Optional[List[str]]:
        """
        Find a path through topological space from start to end.
        Uses gravitational gradients and scar bridges.
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        # Simple pathfinding for now (can be enhanced with A* later)
        visited = set()
        queue = [(start_id, [start_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return path
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            current = self.nodes[current_id]
            
            # Check direct edges
            for neighbor_id in current.edges:
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))
            
            # Check scar bridges if allowed
            if use_scar_bridges:
                for bridge_id in current.scar_bridges:
                    if bridge_id not in visited:
                        queue.append((bridge_id, path + ["[scar]", bridge_id]))
        
        return None
    
    def calculate_field_at_position(self, position: SymbolicPosition) -> Dict[str, float]:
        """Calculate the gravitational and other fields at a position."""
        total_gravity = 0.0
        gravity_vector = {}
        
        for node in self.nodes.values():
            distance = position.distance_to(node.position)
            if distance > 0:
                force = node.mass / (distance ** 2)
                total_gravity += force
                
                # Track which semantic dimensions are pulled
                for dim in node.position.semantic_vector:
                    if dim not in gravity_vector:
                        gravity_vector[dim] = 0
                    gravity_vector[dim] += force * node.position.semantic_vector[dim]
        
        return {
            'total_gravity': total_gravity,
            'gravity_vector': gravity_vector,
            'nearest_mass': self._find_nearest_node(position)
        }
    
    def _find_optimal_position(self, node_type: NodeType) -> SymbolicPosition:
        """Find an optimal position for a new node based on type."""
        import random
        
        semantic_vector = {}
        
        if node_type == NodeType.SCAR:
            semantic_vector['trauma'] = 0.7
            semantic_vector['memory'] = 0.8
        elif node_type == NodeType.DOCTRINE:
            semantic_vector['truth'] = 0.9
            semantic_vector['structure'] = 0.7
        elif node_type == NodeType.PARADOX:
            semantic_vector['contradiction'] = 1.0
            semantic_vector['recursion'] = 0.8
        else:
            semantic_vector['neutral'] = 0.5
        
        # Add small random jitter to prevent stacking
        for k in semantic_vector:
            semantic_vector[k] += random.uniform(-0.02, 0.02)
        
        return SymbolicPosition(semantic_vector=semantic_vector)
    
    def _find_nearest_constellation(self, position: SymbolicPosition) -> Optional[str]:
        """Find the nearest constellation to a position.

        RULING 57 res.3 (2026-07-31) - THE CENTERLESS SKIP IS DECLARED, NOT
        PATCHED, and it stays exactly as it is.

        The `if constellation.gravity_center` test below reads like a defect
        once you know it was the last link in the chain that left every echo
        node unplaced (Docket P: 40 of 40). It is not one. A constellation whose
        members all carry zero edges HONESTLY HAS NO ANCHOR YET - there is no
        node in it that anything else is attached to, so there is nothing for a
        position to be "near". Skipping it reports that; substituting a fallback
        (the first member, the heaviest member, the centroid) would COIN an
        anchor the data does not support, at the exact point where placement
        decisions are made.

        What Ruling 57 changed is the INPUT to this test, never the test:
        res.1 gives the seed's scars nodes to be linked to, and res.2 makes the
        center follow the edge. A constellation that has real connected members
        now has a real center, and this skip stops firing for it - because the
        condition it reports is no longer true, which is the correct way for a
        guard to fall silent.
        """
        min_distance = float('inf')
        nearest_id = None

        for const_id, constellation in self.constellations.items():
            # Distance to constellation center
            if constellation.gravity_center and constellation.gravity_center in self.nodes:
                center = self.nodes[constellation.gravity_center]
                distance = position.distance_to(center.position)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_id = const_id
        
        return nearest_id if min_distance < 2.0 else None  # Threshold for "near"
    
    def _find_nearest_node(self, position: SymbolicPosition) -> Optional[str]:
        """Find the nearest node to a position."""
        min_distance = float('inf')
        nearest_id = None
        
        for node_id, node in self.nodes.items():
            distance = position.distance_to(node.position)
            if distance < min_distance:
                min_distance = distance
                nearest_id = node_id
        
        return nearest_id
    
    def reconfigure(self):
        """
        Reconfigure the entire topology based on gravitational forces.
        This is how the space evolves over time.
        """
        # Calculate forces on each node
        forces = {}
        
        for node_id, node in self.nodes.items():
            total_force = {}  # Use only semantic dimensions, not x/y/z
            
            for other_id, other in self.nodes.items():
                if node_id != other_id:
                    force = node.gravitational_force_on(other)
                    distance = node.position.distance_to(other.position)
                    
                    if distance > 0:
                        # Apply force in direction of other node
                        for dim in other.position.semantic_vector:
                            if dim not in total_force:
                                total_force[dim] = 0
                            direction = other.position.semantic_vector[dim] - node.position.semantic_vector.get(dim, 0)
                            total_force[dim] += force * direction / distance
            
            forces[node_id] = total_force
        
        # Apply forces to update positions (simplified)
        damping = 0.1  # Prevent oscillation
        
        for node_id, force in forces.items():
            node = self.nodes[node_id]
            
            for dim, f in force.items():
                if dim not in node.position.semantic_vector:
                    node.position.semantic_vector[dim] = 0
                
                # Update position based on force
                node.position.semantic_vector[dim] += f * damping
                
                # Update drift velocity with decay
                node.position.drift_velocity[dim] = node.position.drift_velocity.get(dim, 0.0) * 0.8 + f * damping
                
                # Clamp to reasonable range
                node.position.semantic_vector[dim] = max(-1.0, min(1.0, node.position.semantic_vector[dim]))
        
        # Recalculate constellation boundaries
        for constellation in self.constellations.values():
            constellation._recalculate_center()
            constellation.stability = constellation.calculate_cohesion()
    
    def save_to_file(self):
        """Write the topological map to disk as a DIAGNOSTIC SNAPSHOT.

        RULING 65 res.3 (2026-08-02) - THIS FILE IS WRITE-ONLY. NOTHING READS IT.

        It is kept, deliberately, on the forensic-record principle: this is the
        surface that caught the restart-drift defect class, and it stays to catch
        the next one. It is for EXTERNAL readers - a human, a diff, a debugging
        session - and for no code path in `src/`, which is AST-pinned.

        THE PROPERTY THAT MAKES "WRITE-ONLY" REAL RATHER THAN A PROMISE: a boot's
        live state is influenced by this file's bytes ZERO. An adversarial or
        fabricated snapshot and an absent snapshot produce identical live state,
        and that is pinned (res.3), not asserted here.

        BECAUSE NOTHING IS READ, NOTHING CAN BE REFUSED. Slice 1's sticky-refusal
        branch stood here and is gone with the read path it protected: it existed
        so that a file AUREA declined to trust was not overwritten one bridge
        later, and there is no longer any act of trusting it to decline.

        The `version` key STAYS. Its Slice 2 counterpart no longer enforces it,
        but an external reader still needs to know which build's shape it is
        holding, and a snapshot that cannot say is worth less to the next
        investigation. Wormholes are still written as PAIRS; JSON has no tuple,
        and nothing re-tuples them on the way back in because there is no way
        back in.
        """
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'version': self.STATE_VERSION,
            'nodes': {},
            'constellations': {},
            'wormholes': {k: list(v) for k, v in self.wormholes.items()},
            'metrics': {
                'total_mass': self.total_mass,
                'total_edges': self.total_edges,
                'fragmentation_index': self.fragmentation_index
            }
        }
        
        # Serialize nodes
        for node_id, node in self.nodes.items():
            data['nodes'][node_id] = {
                'type': node.node_type.value,
                'mass': node.mass,
                'charge': node.charge,
                'spin': node.spin,
                'position': {
                    'semantic_vector': node.position.semantic_vector,
                    'temporal_layer': node.position.temporal_layer,
                    'collapse_depth': node.position.collapse_depth,
                    'constellation_id': node.position.constellation_id
                },
                'edges': node.edges,
                'scar_bridges': node.scar_bridges,
                'tags': list(node.tags)
            }
        
        # Serialize constellations
        for const_id, constellation in self.constellations.items():
            data['constellations'][const_id] = {
                'type': constellation.constellation_type.value,
                'node_ids': list(constellation.nodes.keys()),
                'gravity_center': constellation.gravity_center,
                'total_mass': constellation.total_mass,
                'stability': constellation.stability,
                'bridges': constellation.bridges
            }
        
        # Rider R3 (2026-07-29): ATOMIC. `json.dumps` output is ASCII
        # (`ensure_ascii` defaults True), so naming utf-8 here where the old call
        # took the platform default is byte-for-byte the same file.
        atomic_write_json(self.filepath, data, indent=2)
