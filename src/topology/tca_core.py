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
    
    def __init__(self, filepath: str = "data/topology/tca_map.json"):
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
        
        self.load_from_file()
    
    def add_node(self, node_id: str, node_type: NodeType, 
                 mass: float = 1.0, position: Optional[SymbolicPosition] = None,
                 constellation_id: Optional[str] = None) -> ConstellationNode:
        """Add a new node to the topological space."""
        
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
        """Create an edge between two nodes."""
        if node1_id in self.nodes and node2_id in self.nodes:
            # Guard against duplicate edges
            if node2_id not in self.nodes[node1_id].edges:
                self.nodes[node1_id].edges[node2_id] = weight
                self.nodes[node2_id].edges[node1_id] = weight
                self.total_edges += 1
    
    def create_scar_bridge(self, node1_id: str, node2_id: str):
        """Create a scar-carved shortcut between distant nodes."""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.nodes[node1_id].scar_bridges.append(node2_id)
            self.nodes[node2_id].scar_bridges.append(node1_id)
            
            # Record as wormhole
            bridge_id = f"bridge_{len(self.wormholes)}"
            self.wormholes[bridge_id] = (node1_id, node2_id)
    
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
        """Find the nearest constellation to a position."""
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
        """Save the topological map to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'nodes': {},
            'constellations': {},
            'wormholes': dict(self.wormholes),
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
        
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_from_file(self):
        """Load the topological map from disk."""
        if not self.filepath.exists():
            return
        
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        
        # Load nodes
        for node_id, node_data in data.get('nodes', {}).items():
            # Handle infinity values in collapse_depth
            collapse_depth = node_data['position']['collapse_depth']
            if isinstance(collapse_depth, str) and collapse_depth == 'inf':
                collapse_depth = 9.99  # Use large finite sentinel for paradoxes
            else:
                collapse_depth = float(collapse_depth)
            
            position = SymbolicPosition(
                semantic_vector=node_data['position']['semantic_vector'],
                temporal_layer=node_data['position']['temporal_layer'],
                collapse_depth=collapse_depth,
                constellation_id=node_data['position'].get('constellation_id')
            )
            
            node = ConstellationNode(
                id=node_id,
                node_type=NodeType(node_data['type']),
                position=position,
                mass=node_data['mass'],
                charge=node_data.get('charge', 0),
                spin=node_data.get('spin', 0),
                edges=node_data.get('edges', {}),
                scar_bridges=node_data.get('scar_bridges', []),
                tags=set(node_data.get('tags', []))
            )
            
            self.nodes[node_id] = node
            self.total_mass += node.mass
        
        # Load constellations
        for const_id, const_data in data.get('constellations', {}).items():
            constellation = Constellation(
                id=const_id,
                constellation_type=ConstellationType(const_data['type'])
            )
            
            # Add nodes to constellation
            for node_id in const_data.get('node_ids', []):
                if node_id in self.nodes:
                    constellation.add_node(self.nodes[node_id])
            
            constellation.gravity_center = const_data.get('gravity_center')
            constellation.stability = const_data.get('stability', 1.0)
            constellation.bridges = const_data.get('bridges', {})
            
            self.constellations[const_id] = constellation
        
        # Load wormholes
        self.wormholes = data.get('wormholes', {})
        
        # Recompute total_edges from loaded nodes (fixes drift)
        self.total_edges = 0
        counted_edges = set()
        for node_id, node in self.nodes.items():
            for edge_id in node.edges:
                edge_pair = tuple(sorted([node_id, edge_id]))
                if edge_pair not in counted_edges:
                    counted_edges.add(edge_pair)
                    self.total_edges += 1
        
        # Load metrics
        metrics = data.get('metrics', {})
        self.fragmentation_index = metrics.get('fragmentation_index', 0.0)
