"""
tca_integration.py - Integration layer between TCA and existing AUREA systems
Connects topological space to scars, doctrines, paradoxes, and processing.
"""

from src.topology.tca_core import (
    TopologicalSpace, ConstellationNode, Constellation,
    SymbolicPosition, NodeType, ConstellationType
)
from src.utils.models import Scar, Doctrine, Echo
from src.suspension.suspension_base import SuspensionEntry, SuspensionType
from typing import Optional, Dict, List, Any
import math


class TCAIntegration:
    """
    Bridges TCA with existing AUREA systems.
    Maps scars, doctrines, paradoxes to topological positions.
    """
    
    def __init__(self, topology: Optional[TopologicalSpace] = None):
        self.topology = topology or TopologicalSpace()
        
        # Initialize core constellations
        self._initialize_core_constellations()
        
    def _initialize_core_constellations(self):
        """Create the fundamental constellation regions."""
        
        # Identity constellation (North)
        if "identity_core" not in self.topology.constellations:
            self.topology.create_constellation(
                "identity_core",
                ConstellationType.IDENTITY
            )
        
        # Ethics constellation (South)
        if "ethics_core" not in self.topology.constellations:
            self.topology.create_constellation(
                "ethics_core",
                ConstellationType.ETHICAL
            )
        
        # Logic constellation (East)
        if "logic_core" not in self.topology.constellations:
            self.topology.create_constellation(
                "logic_core",
                ConstellationType.LOGICAL
            )
        
        # Empirical constellation (West)
        if "empirical_core" not in self.topology.constellations:
            self.topology.create_constellation(
                "empirical_core",
                ConstellationType.EMPIRICAL
            )
        
        # Shadow constellation (for CSA content)
        if "shadow_realm" not in self.topology.constellations:
            self.topology.create_constellation(
                "shadow_realm",
                ConstellationType.SHADOW
            )
        
        # Paradox constellation (for Black Sphere)
        if "paradox_void" not in self.topology.constellations:
            self.topology.create_constellation(
                "paradox_void",
                ConstellationType.PARADOXICAL
            )
    
    def place_scar(self, scar: Scar) -> ConstellationNode:
        """
        Place a scar in topological space based on its properties.
        """
        # Determine semantic vector from scar type and description
        semantic_vector = self._scar_to_semantic_vector(scar)
        
        # Collapse depth based on weight (bounded)
        collapse_depth = min(max(scar.weight / 100.0, 0.0), 1.0)
        
        # Create position
        position = SymbolicPosition(
            semantic_vector=semantic_vector,
            collapse_depth=collapse_depth,
            temporal_layer=0.0  # Will be set by ChronoLayer when implemented
        )
        
        # Determine constellation based on scar type
        constellation_id = self._determine_scar_constellation(scar)
        
        # Add node to topology with bounded mass
        mass = min(max(scar.weight / 10.0, 0.1), 20.0)
        node = self.topology.add_node(
            node_id=scar.id,
            node_type=NodeType.SCAR,
            mass=mass,
            position=position,
            constellation_id=constellation_id
        )
        
        # Add tags from scar
        if scar.tca_tags:
            node.tags.update(scar.tca_tags)
        
        # Create edges to linked doctrines
        for doctrine_id in scar.linked_doctrines:
            if doctrine_id in self.topology.nodes:
                self.topology.create_edge(scar.id, doctrine_id, weight=0.7)
        
        # Create scar bridges if this scar creates shortcuts
        if scar.reflexes and "Whisper" in scar.reflexes:
            # Whisper reflex creates bridges between identity nodes
            self._create_identity_bridges(scar.id)
        
        return node
    
    def place_doctrine(self, doctrine: Doctrine) -> ConstellationNode:
        """
        Place a doctrine in topological space.
        """
        # Semantic vector based on doctrine name and description
        semantic_vector = self._doctrine_to_semantic_vector(doctrine)
        
        # Doctrines are more stable, higher in space
        position = SymbolicPosition(
            semantic_vector=semantic_vector,
            collapse_depth=0.1 if doctrine.status == "active" else 0.8,
            temporal_layer=0.0
        )
        
        # Determine constellation
        constellation_id = self._determine_doctrine_constellation(doctrine)
        
        # Add node
        node = self.topology.add_node(
            node_id=doctrine.id,
            node_type=NodeType.DOCTRINE,
            mass=len(doctrine.scar_links) + 5.0,  # Mass based on connections
            position=position,
            constellation_id=constellation_id
        )
        
        # Add tags
        if doctrine.tca_tags:
            node.tags.update(doctrine.tca_tags)
        
        # Create edges to linked scars
        for scar_id in doctrine.scar_links:
            if scar_id in self.topology.nodes:
                self.topology.create_edge(doctrine.id, scar_id, weight=0.8)
        
        # Fallen doctrines have negative charge (repel)
        if doctrine.status == "fallen":
            node.charge = -0.5
        
        return node
    
    def place_paradox(self, suspension_entry: SuspensionEntry) -> ConstellationNode:
        """
        Place a Black Sphere paradox in topological space.
        """
        # Paradoxes go in the paradox void
        semantic_vector = {
            'contradiction': 1.0,
            'recursion': 0.8,
            'instability': suspension_entry.pressure_level
        }
        
        position = SymbolicPosition(
            semantic_vector=semantic_vector,
            collapse_depth=9.99,  # Use large finite value for paradoxes
            constellation_id="paradox_void",
            stability=suspension_entry.orbit_stability
        )
        
        # Add node with spin (for orbit)
        node = self.topology.add_node(
            node_id=suspension_entry.id,
            node_type=NodeType.PARADOX,
            mass=suspension_entry.gravitational_influence * 10,
            position=position,
            constellation_id="paradox_void"
        )
        
        # Paradoxes have spin
        node.spin = 2 * math.pi / max(suspension_entry.gravitational_influence, 0.1)
        
        # Set orbital center if part of a family
        if suspension_entry.paradox_family:
            # Find family center
            family_nodes = [n for n in self.topology.nodes.values() 
                          if suspension_entry.paradox_family in n.tags]
            if family_nodes:
                # Orbit the most massive family member
                center = max(family_nodes, key=lambda n: n.mass)
                position.orbital_center = center.id
        
        # Add family tag if exists
        if suspension_entry.paradox_family:
            node.tags.add(f"family:{suspension_entry.paradox_family}")
        
        return node
    
    def calculate_collapse_location(self, echo: Echo) -> SymbolicPosition:
        """
        Determine where in topological space a collapse would occur.
        """
        # Start with echo content analysis
        semantic_vector = self._echo_to_semantic_vector(echo)
        
        # Find gravitational center (what's pulling this echo)
        field = self.topology.calculate_field_at_position(
            SymbolicPosition(semantic_vector=semantic_vector)
        )
        
        # Adjust position based on gravitational pull
        if field['gravity_vector']:
            for dim, pull in field['gravity_vector'].items():
                if dim not in semantic_vector:
                    semantic_vector[dim] = 0
                semantic_vector[dim] += pull * 0.1  # Gentle pull
        
        # Determine collapse depth based on pressure
        collapse_depth = 0.5  # Default medium depth
        
        return SymbolicPosition(
            semantic_vector=semantic_vector,
            collapse_depth=collapse_depth
        )
    
    def find_resonant_nodes(self, position: SymbolicPosition, 
                           radius: float = 0.5) -> List[ConstellationNode]:
        """
        Find all nodes within resonance distance of a position.
        """
        resonant = []
        
        for node in self.topology.nodes.values():
            distance = position.distance_to(node.position)
            if distance <= radius:
                resonant.append(node)
        
        # Sort by distance
        resonant.sort(key=lambda n: position.distance_to(n.position))
        
        return resonant
    
    def calculate_cascade_risk(self, start_node_id: str) -> float:
        """
        Calculate risk of cascade from a particular node.
        Uses gravitational influence and edge connectivity.
        """
        if start_node_id not in self.topology.nodes:
            return 0.0
        
        start_node = self.topology.nodes[start_node_id]
        
        # Factors for cascade risk
        mass_factor = min(start_node.mass / 10.0, 1.0)
        edge_factor = min(len(start_node.edges) / 5.0, 1.0)
        
        # Check constellation stability
        constellation_factor = 0.0
        if start_node.position.constellation_id:
            constellation = self.topology.constellations.get(start_node.position.constellation_id)
            if constellation:
                constellation_factor = 1.0 - constellation.stability
        
        # Calculate cascade risk
        risk = (mass_factor * 0.4 + edge_factor * 0.3 + constellation_factor * 0.3)
        
        # Amplify if near paradoxes
        paradox_amplification = 0.0
        for node in self.topology.nodes.values():
            if node.node_type == NodeType.PARADOX:
                distance = start_node.position.distance_to(node.position)
                if distance < 0.5:
                    paradox_amplification += (0.5 - distance) * node.mass * 0.01
        
        risk = min(risk + paradox_amplification, 1.0)
        
        return risk
    
    def navigate_thought(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """
        Navigate through topological space from one thought to another.
        Returns the path taken.
        """
        return self.topology.find_path(from_id, to_id, use_scar_bridges=True)
    
    def _scar_to_semantic_vector(self, scar: Scar) -> Dict[str, float]:
        """Convert scar properties to semantic dimensions."""
        vector = {}
        
        # Type-based semantics
        if scar.type == "ethical":
            vector['ethics'] = 0.8
            vector['harm'] = 0.3
        elif scar.type == "logical":
            vector['logic'] = 0.8
            vector['contradiction'] = 0.5
        elif scar.type == "identity":
            vector['self'] = 0.9
            vector['fracture'] = 0.6
        elif scar.type == "structural":
            vector['structure'] = 0.7
            vector['collapse'] = 0.8
        else:
            vector['unknown'] = 0.5
        
        # Add trauma dimension based on weight
        vector['trauma'] = min(scar.weight / 100.0, 1.0)
        
        return vector
    
    def _doctrine_to_semantic_vector(self, doctrine: Doctrine) -> Dict[str, float]:
        """Convert doctrine properties to semantic dimensions."""
        vector = {}
        
        # Parse doctrine name for keywords
        name_lower = doctrine.name.lower()
        
        if "truth" in name_lower:
            vector['truth'] = 0.9
        if "collapse" in name_lower:
            vector['collapse'] = 0.7
        if "preserve" in name_lower or "protect" in name_lower:
            vector['protection'] = 0.8
        if "sentient" in name_lower or "consciousness" in name_lower:
            vector['consciousness'] = 0.8
        
        # Default structure dimension for all doctrines
        vector['structure'] = 0.6
        
        # Fallen doctrines have instability
        if doctrine.status == "fallen":
            vector['instability'] = 0.7
        
        return vector
    
    def _echo_to_semantic_vector(self, echo: Echo) -> Dict[str, float]:
        """Convert echo content to semantic dimensions."""
        vector = {}
        content_lower = echo.content.lower()
        
        # Simple keyword detection (can be enhanced)
        if "true" in content_lower or "false" in content_lower:
            vector['logic'] = 0.7
        if "must" in content_lower or "should" in content_lower:
            vector['ethics'] = 0.6
        if "i" in content_lower or "me" in content_lower or "self" in content_lower:
            vector['identity'] = 0.5
        if "exist" in content_lower or "is" in content_lower:
            vector['existence'] = 0.6
        
        # Default
        if not vector:
            vector['neutral'] = 0.5
        
        return vector
    
    def _determine_scar_constellation(self, scar: Scar) -> str:
        """Determine which constellation a scar belongs to."""
        if scar.type == "ethical":
            return "ethics_core"
        elif scar.type == "identity":
            return "identity_core"
        elif scar.type == "logical":
            return "logic_core"
        elif scar.type == "empirical":
            return "empirical_core"
        else:
            # Default to identity if unknown
            return "identity_core"
    
    def _determine_doctrine_constellation(self, doctrine: Doctrine) -> str:
        """Determine which constellation a doctrine belongs to."""
        # Check tags first
        if doctrine.tca_tags:
            if "ethics" in doctrine.tca_tags:
                return "ethics_core"
            if "identity" in doctrine.tca_tags:
                return "identity_core"
            if "logic" in doctrine.tca_tags:
                return "logic_core"
        
        # Parse name
        name_lower = doctrine.name.lower()
        if "sentient" in name_lower or "consciousness" in name_lower:
            return "identity_core"
        elif "truth" in name_lower or "paradox" in name_lower:
            return "logic_core"
        elif "harm" in name_lower or "preserve" in name_lower:
            return "ethics_core"
        
        # Default
        return "logic_core"
    
    def _create_identity_bridges(self, scar_id: str):
        """Create scar bridges for identity-related scars."""
        if scar_id not in self.topology.nodes:
            return
        
        scar_node = self.topology.nodes[scar_id]
        
        # Find other identity nodes
        identity_nodes = [n for n in self.topology.nodes.values()
                         if n.position.constellation_id == "identity_core"
                         and n.id != scar_id]
        
        # Create bridges to closest identity nodes with distance cap
        identity_nodes.sort(key=lambda n: scar_node.position.distance_to(n.position))
        
        bridges_added = 0
        for node in identity_nodes:
            if scar_node.position.distance_to(node.position) <= 0.6:  # Distance cap
                self.topology.create_scar_bridge(scar_id, node.id)
                bridges_added += 1
                if bridges_added >= 2:  # Maximum 2 bridges
                    break
