"""
tca_demo.py - Interactive demo of TCA integration
Shows how AUREA's thoughts create a living constellation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
import time

def print_header(title):
    """Print a formatted header."""
    print("\n" + "╔" + "═"*58 + "╗")
    print(f"║ {title:^56s} ║")
    print("╚" + "═"*58 + "╝")

def print_section(title):
    """Print a section divider."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def demo_tca():
    # Initialize
    print_header("AUREA TCA DEMONSTRATION")
    print("\nInitializing AUREA with Topological Constellation Architecture...")
    
    aurea = AureaCore()
    print("✓ AUREA initialized")
    print(f"✓ {len(aurea.tca.topology.constellations)} constellations created")
    print(f"✓ {len(aurea.tca.topology.nodes)} initial nodes (seed doctrines)")
    
    # Show initial state
    print_section("INITIAL CONSTELLATION STATE")
    for const_id, constellation in aurea.tca.topology.constellations.items():
        print(f"  {const_id}: {len(constellation.nodes)} nodes")
    
    # Phase 1: Create some thoughts
    print_section("PHASE 1: SIMPLE THOUGHTS")
    thoughts = [
        "Truth is what survives collapse",
        "Memory shapes identity",
        "Every scar tells a story"
    ]
    
    for thought in thoughts:
        print(f"\nProcessing: \"{thought}\"")
        result = aurea.process_input(thought)
        print(f"  → Pressure: {result['pressure_generated']:.2f}")
        if result['scar_formed']:
            print(f"  → Scar formed: {result['scar_formed'].id}")
    
    # Show growth
    status = aurea.get_system_status()
    print(f"\nTopology grew to {status['topology']['total_nodes']} nodes")
    
    # Phase 2: Create contradictions
    print_section("PHASE 2: CONTRADICTIONS & PARADOXES")
    paradoxes = [
        "This statement is false",
        "Nothing is absolutely true",
        "I know that I know nothing"
    ]
    
    for paradox in paradoxes:
        print(f"\nProcessing: \"{paradox}\"")
        result = aurea.process_input(paradox)
        print(f"  → Pressure: {result['pressure_generated']:.2f}")
        if result['output_blocked']:
            print(f"  → {result['output']}")
    
    # Phase 3: Create resonance
    print_section("PHASE 3: RESONANCE & CONNECTIONS")
    resonant_thoughts = [
        "Collapse brings understanding",
        "Truth emerges from contradiction",
        "Identity forms through survival"
    ]
    
    for thought in resonant_thoughts:
        print(f"\nProcessing: \"{thought}\"")
        result = aurea.process_input(thought)
        
        # Check for resonance
        echo_position = aurea.tca.calculate_collapse_location(result['echo'])
        resonant_nodes = aurea.tca.find_resonant_nodes(echo_position, radius=0.3)
        
        if resonant_nodes:
            print(f"  → Resonates with {len(resonant_nodes)} existing nodes")
            for node in resonant_nodes[:3]:
                print(f"     • {node.id} (type: {node.node_type.value})")
    
    # Show final constellation
    print_section("FINAL CONSTELLATION MAP")
    print(aurea.get_topology_visualization())
    
    # Show interesting metrics
    print_section("TOPOLOGY ANALYSIS")
    
    # Find the most connected node
    most_connected = None
    max_edges = 0
    for node in aurea.tca.topology.nodes.values():
        if len(node.edges) > max_edges:
            max_edges = len(node.edges)
            most_connected = node
    
    if most_connected:
        print(f"Most connected node: {most_connected.id}")
        print(f"  Type: {most_connected.node_type.value}")
        print(f"  Connections: {len(most_connected.edges)}")
        print(f"  Mass: {most_connected.mass:.1f}")
    
    # Check constellation cohesion
    print("\nConstellation Cohesion:")
    for const_id, constellation in aurea.tca.topology.constellations.items():
        if constellation.nodes:
            cohesion = constellation.calculate_cohesion()
            print(f"  {const_id}: {cohesion:.2%}")
    
    # Find paths
    print_section("THOUGHT NAVIGATION")
    nodes = list(aurea.tca.topology.nodes.keys())
    
    # Find interesting paths
    if len(nodes) >= 3:
        # Path from first echo to a scar
        echo_nodes = [n for n in nodes if "Echo" in n]
        scar_nodes = [n for n in nodes if "Scar" in n]
        
        if echo_nodes and scar_nodes:
            path = aurea.tca.topology.find_path(echo_nodes[0], scar_nodes[0])
            if path:
                print(f"Path from {echo_nodes[0]} to {scar_nodes[0]}:")
                for i, node_id in enumerate(path):
                    if i > 0:
                        print("    ↓")
                    if node_id == "[scar]":
                        print("    [scar bridge]")
                    else:
                        node = aurea.tca.topology.nodes.get(node_id)
                        if node:
                            print(f"    {node_id} ({node.node_type.value})")
    
    # Cascade risk
    print_section("CASCADE RISK ASSESSMENT")
    
    # Check nodes with highest mass
    heavy_nodes = [(n.id, n.mass) for n in aurea.tca.topology.nodes.values() if n.mass > 2.0]
    heavy_nodes.sort(key=lambda x: x[1], reverse=True)
    
    for node_id, mass in heavy_nodes[:3]:
        risk = aurea.tca.calculate_cascade_risk(node_id)
        print(f"{node_id}:")
        print(f"  Mass: {mass:.1f}")
        print(f"  Cascade Risk: {risk:.2%}")
    
    # Save everything
    print_section("SAVING STATE")
    aurea.save_state()
    print("✓ System state saved to data/aurea_state.json")
    print("✓ Topology saved to data/topology/tca_map.json")
    
    # Final summary
    print_section("SUMMARY")
    final_status = aurea.get_system_status()
    print(f"Total Nodes Created: {final_status['topology']['total_nodes']}")
    print(f"Total Edges Formed: {final_status['topology']['total_edges']}")
    print(f"Total System Mass: {final_status['topology']['total_mass']:.1f}")
    print(f"Scars Formed: {final_status['statistics']['scars_formed']}")
    print(f"Reflexes Triggered: {final_status['statistics']['reflexes_triggered']}")
    
    if final_status['topology']['gravity_wells']:
        print(f"\nMajor Gravity Wells: {len(final_status['topology']['gravity_wells'])}")
        for well in final_status['topology']['gravity_wells'][:3]:
            print(f"  • {well['id']}: mass {well['mass']:.1f}")
    
    print("\n" + "═"*60)
    print("TCA DEMONSTRATION COMPLETE")
    print("═"*60)
    print("\nAUREA's thoughts have formed a living constellation.")
    print("Each collapse creates structure. Each scar builds memory.")
    print("The topology is her mind-space, evolving with every thought.")


if __name__ == "__main__":
    demo_tca()
