"""
tca_monitor.py - Monitoring and visualization for Topological Constellation Architecture
Provides insights into AUREA's symbolic topology.
"""

from src.topology.tca_core import TopologicalSpace, NodeType, ConstellationType
from src.topology.tca_integration import TCAIntegration
from typing import Dict, List, Any, Optional
import math


class TCAMonitor:
    """
    Monitor and analyze the topological space.
    Provides health metrics, visualization data, and diagnostics.
    """
    
    def __init__(self, topology: TopologicalSpace, integration: Optional[TCAIntegration] = None):
        self.topology = topology
        self.integration = integration or TCAIntegration(topology)
    
    def get_topology_status(self) -> Dict[str, Any]:
        """Get comprehensive topology status."""
        
        # Count nodes by type
        node_counts = {node_type: 0 for node_type in NodeType}
        for node in self.topology.nodes.values():
            node_counts[node.node_type] += 1
        
        # Constellation health
        constellation_status = {}
        for const_id, constellation in self.topology.constellations.items():
            constellation_status[const_id] = {
                'type': constellation.constellation_type.value,
                'nodes': len(constellation.nodes),
                'mass': constellation.total_mass,
                'cohesion': constellation.calculate_cohesion(),
                'stability': constellation.stability,
                'center': constellation.gravity_center
            }
        
        # Find high-gravity regions
        gravity_wells = self._find_gravity_wells()
        
        # Calculate fragmentation
        fragmentation = self._calculate_fragmentation()
        
        # Find isolated nodes
        isolated = self._find_isolated_nodes()
        
        return {
            'total_nodes': len(self.topology.nodes),
            'node_distribution': {k.value: v for k, v in node_counts.items()},
            'total_mass': self.topology.total_mass,
            'constellations': constellation_status,
            'gravity_wells': gravity_wells,
            'wormholes': len(self.topology.wormholes),
            'fragmentation_index': fragmentation,
            'isolated_nodes': len(isolated),
            'edge_density': self._calculate_edge_density(),
            'bridge_density': self._calculate_bridge_density(),
            'average_constellation_stability': self._average_constellation_stability()
        }
    
    def get_constellation_report(self, constellation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report on a specific constellation."""
        if constellation_id not in self.topology.constellations:
            return None
        
        constellation = self.topology.constellations[constellation_id]
        
        # Node breakdown
        node_types = {}
        total_edge_degree = 0  # Sum of degrees (counts each edge twice)
        unique_edges = set()
        scar_bridges = 0
        
        for node in constellation.nodes.values():
            # Count types
            if node.node_type not in node_types:
                node_types[node.node_type] = 0
            node_types[node.node_type] += 1
            
            # Count connections
            total_edge_degree += len(node.edges)  # This is degree sum
            
            # Track unique edges
            for edge_id in node.edges:
                edge_pair = tuple(sorted([node.id, edge_id]))
                unique_edges.add(edge_pair)
            
            scar_bridges += len(node.scar_bridges)
        
        # Find most connected node
        if constellation.nodes:
            hub_node = max(constellation.nodes.values(), 
                          key=lambda n: len(n.edges) + len(n.scar_bridges))
            hub_id = hub_node.id
        else:
            hub_id = None
        
        return {
            'id': constellation_id,
            'type': constellation.constellation_type.value,
            'total_nodes': len(constellation.nodes),
            'node_types': {k.value: v for k, v in node_types.items()},
            'total_mass': constellation.total_mass,
            'average_collapse_depth': constellation.avg_collapse_depth,
            'cohesion': constellation.calculate_cohesion(),
            'stability': constellation.stability,
            'gravity_center': constellation.gravity_center,
            'hub_node': hub_id,
            'total_edge_degree': total_edge_degree,  # Sum of all degrees
            'unique_edges': len(unique_edges),  # Actual number of edges
            'scar_bridges': scar_bridges,
            'bridge_connections': list(constellation.bridges.keys()),
            'radius': constellation.radius,
            'rotation_rate': constellation.rotation_rate,
            'expansion_rate': constellation.expansion_rate
        }
    
    def find_thought_path(self, from_concept: str, to_concept: str) -> Dict[str, Any]:
        """
        Analyze the path between two concepts.
        Shows how AUREA would navigate from one thought to another.
        """
        # Find nodes matching concepts
        from_nodes = self._find_nodes_by_concept(from_concept)
        to_nodes = self._find_nodes_by_concept(to_concept)
        
        if not from_nodes or not to_nodes:
            return {
                'found': False,
                'reason': 'Concepts not found in topology'
            }
        
        # Use closest matching nodes
        from_id = from_nodes[0]
        to_id = to_nodes[0]
        
        # Find path
        path = self.topology.find_path(from_id, to_id)
        
        if not path:
            return {
                'found': False,
                'from': from_id,
                'to': to_id,
                'reason': 'No path exists'
            }
        
        # Analyze path
        path_analysis = []
        total_distance = 0.0
        scar_bridges_used = path.count("[scar]")
        
        # Get real nodes only (no placeholders)
        real_nodes = [p for p in path if p != "[scar]"]
        
        for i, node_id in enumerate(real_nodes):
            node = self.topology.nodes.get(node_id)
            if node:
                step = {
                    'node_id': node_id,
                    'type': node.node_type.value,
                    'constellation': node.position.constellation_id,
                    'mass': node.mass
                }
                
                # Calculate distance to next real node
                if i < len(real_nodes) - 1:
                    next_node = self.topology.nodes.get(real_nodes[i+1])
                    if next_node:
                        distance = node.position.distance_to(next_node.position)
                        step['distance_to_next'] = distance
                        total_distance += distance
                
                path_analysis.append(step)
        
        return {
            'found': True,
            'from': from_id,
            'to': to_id,
            'path_length': len([p for p in path if p != "[scar]"]),
            'total_distance': total_distance,
            'scar_bridges_used': scar_bridges_used,
            'path': path_analysis
        }
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in the topology."""
        anomalies = []
        
        # Check for orphaned nodes
        for node_id, node in self.topology.nodes.items():
            if not node.edges and not node.scar_bridges:
                anomalies.append({
                    'type': 'orphaned_node',
                    'node_id': node_id,
                    'severity': 'medium',
                    'description': f"Node {node_id} has no connections"
                })
        
        # Check for unstable constellations
        for const_id, constellation in self.topology.constellations.items():
            if constellation.stability < 0.3:
                anomalies.append({
                    'type': 'unstable_constellation',
                    'constellation_id': const_id,
                    'severity': 'high',
                    'stability': constellation.stability,
                    'description': f"Constellation {const_id} is fragmenting"
                })
        
        # Check for extreme gravity wells
        gravity_wells = self._find_gravity_wells()
        for well in gravity_wells:
            if well['field_strength'] > 50.0:  # Use field_strength, not mass_strength
                anomalies.append({
                    'type': 'extreme_gravity',
                    'node_id': well['node_id'],
                    'severity': 'high',
                    'field_strength': well['field_strength'],
                    'mass_strength': well['mass_strength'],
                    'description': f"Extreme gravitational influence at {well['node_id']}"
                })
        
        # Check for paradox clustering
        paradox_nodes = [n for n in self.topology.nodes.values() 
                        if n.node_type == NodeType.PARADOX]
        if len(paradox_nodes) > 5:
            # Check if they're clustering
            paradox_constellation = None
            for node in paradox_nodes:
                if node.position.constellation_id == "paradox_void":
                    paradox_constellation = self.topology.constellations.get("paradox_void")
                    break
            
            if paradox_constellation and paradox_constellation.total_mass > 30:
                anomalies.append({
                    'type': 'paradox_cascade_risk',
                    'severity': 'critical',
                    'paradox_count': len(paradox_nodes),
                    'total_mass': paradox_constellation.total_mass,
                    'description': "Paradox clustering approaching critical mass"
                })
        
        return anomalies
    
    def _project_to_2d(self, semantic_vector: Dict[str, float]) -> tuple:
        """Project semantic vector to 2D coordinates deterministically."""
        if not semantic_vector:
            return 0.0, 0.0
        
        # Choose top-2 dimensions by absolute weight for determinism
        dims = sorted(semantic_vector.items(), key=lambda kv: abs(kv[1]), reverse=True)
        x = dims[0][1] if dims else 0.0
        y = dims[1][1] if len(dims) > 1 else 0.0
        return x, y
    
    def visualize_ascii(self, width: int = 60, height: int = 20) -> str:
        """
        Create a simple ASCII visualization of the topology.
        """
        # Create grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Map nodes to grid positions
        for node in self.topology.nodes.values():
            # Get primary semantic dimension for positioning
            if node.position.semantic_vector:
                # Project to 2D deterministically
                x_raw, y_raw = self._project_to_2d(node.position.semantic_vector)
                x = int((x_raw + 1) * width / 2)
                y = int((y_raw + 1) * height / 2)
            else:
                x = width // 2
                y = height // 2
            
            # Clamp to grid
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            
            # Choose symbol based on node type
            symbol = {
                NodeType.SCAR: '◊',
                NodeType.DOCTRINE: '□',
                NodeType.PARADOX: '◎',
                NodeType.ECHO: '·',
                NodeType.ANCHOR: '▲',
                NodeType.SUSPENSION: '○',
                NodeType.VOID: '×'
            }.get(node.node_type, '?')
            
            # Place on grid
            # Handle collision - combine symbols if needed
            if grid[y][x] != ' ':
                grid[y][x] = '*'  # Multiple nodes at same position
            else:
                grid[y][x] = symbol
        
        # Add constellation boundaries (simplified)
        for constellation in self.topology.constellations.values():
            if constellation.gravity_center and constellation.gravity_center in self.topology.nodes:
                center = self.topology.nodes[constellation.gravity_center]
                if center.position.semantic_vector:
                    dims = list(center.position.semantic_vector.items())
                    if dims:
                        cx = int((dims[0][1] + 1) * width / 2)
                        cy = int((dims[1][1] + 1) * height / 2) if len(dims) > 1 else height // 2
                        
                        # Draw constellation marker
                        cx = max(1, min(width - 2, cx))
                        cy = max(1, min(height - 2, cy))
                        
                        # Mark constellation boundaries
                        if grid[cy][cx] == ' ':
                            grid[cy][cx] = '+'
        
        # Convert to string
        lines = [''.join(row) for row in grid]
        
        # Add legend
        legend = [
            "",
            "Legend:",
            "  ◊ Scar      □ Doctrine   ◎ Paradox",
            "  · Echo      ▲ Anchor     ○ Suspension",
            "  × Void      + Constellation Center"
        ]
        
        return '\n'.join(lines + legend)
    
    def _find_gravity_wells(self) -> List[Dict[str, Any]]:
        """Find the strongest gravity wells in the topology."""
        wells = []
        
        for node_id, node in self.topology.nodes.items():
            if node.mass > 5.0:  # Significant mass
                # Calculate actual field strength at this node
                field_strength = 0.0
                for other_id, other in self.topology.nodes.items():
                    if other_id != node_id:
                        distance = node.position.distance_to(other.position)
                        if distance > 0:
                            field_strength += other.mass / (distance ** 2)
                
                wells.append({
                    'node_id': node_id,
                    'type': node.node_type.value,
                    'mass_strength': node.mass,
                    'field_strength': field_strength,
                    'constellation': node.position.constellation_id
                })
        
        # Sort by field strength (actual gravitational influence)
        wells.sort(key=lambda w: w['field_strength'], reverse=True)
        
        return wells[:5]  # Top 5 gravity wells
    
    def _calculate_fragmentation(self) -> float:
        """Calculate how fragmented the topology is."""
        if len(self.topology.nodes) < 2:
            return 0.0
        
        # Count connected components
        visited = set()
        components = 0
        
        for node_id in self.topology.nodes:
            if node_id not in visited:
                # BFS to find component
                component = set()
                queue = [node_id]
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    component.add(current)
                    
                    # Add neighbors
                    if current in self.topology.nodes:
                        node = self.topology.nodes[current]
                        queue.extend(node.edges.keys())
                        queue.extend(node.scar_bridges)
                
                if component:
                    components += 1
        
        # Fragmentation = (components - 1) / (nodes - 1)
        # 0 = fully connected, 1 = fully fragmented
        fragmentation = (components - 1) / (len(self.topology.nodes) - 1)
        
        return min(fragmentation, 1.0)
    
    def _find_isolated_nodes(self) -> List[str]:
        """Find nodes with no connections."""
        isolated = []
        
        for node_id, node in self.topology.nodes.items():
            if not node.edges and not node.scar_bridges:
                isolated.append(node_id)
        
        return isolated
    
    def _calculate_edge_density(self) -> float:
        """Calculate edge density (actual edges / possible edges)."""
        n = len(self.topology.nodes)
        if n < 2:
            return 0.0
        
        possible_edges = n * (n - 1) / 2
        actual_edges = self.topology.total_edges
        
        # Also count scar bridges
        scar_bridges = sum(len(node.scar_bridges) for node in self.topology.nodes.values()) // 2
        
        total_connections = actual_edges + scar_bridges
        
        return total_connections / possible_edges if possible_edges > 0 else 0.0
    
    def _calculate_bridge_density(self) -> float:
        """Calculate scar bridge density as separate metric."""
        n = len(self.topology.nodes)
        if n < 2:
            return 0.0
        
        possible_edges = n * (n - 1) / 2
        scar_bridges = sum(len(node.scar_bridges) for node in self.topology.nodes.values()) // 2
        
        return scar_bridges / possible_edges if possible_edges > 0 else 0.0
    
    def _average_constellation_stability(self) -> float:
        """Calculate average stability across all constellations."""
        if not self.topology.constellations:
            return 1.0
        
        total_stability = sum(c.stability for c in self.topology.constellations.values())
        return total_stability / len(self.topology.constellations)
    
    def _find_nodes_by_concept(self, concept: str) -> List[str]:
        """Find nodes related to a concept."""
        concept_lower = concept.lower()
        matches = []
        
        for node_id, node in self.topology.nodes.items():
            # Check tags
            if any(concept_lower in tag.lower() for tag in node.tags):
                matches.append(node_id)
                continue
            
            # Check semantic vector
            for dim in node.position.semantic_vector:
                if concept_lower in dim.lower():
                    matches.append(node_id)
                    break
        
        return matches
