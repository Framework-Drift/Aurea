"""
test_tca_integration.py - Test TCA integration with AUREA core
Verifies that topological mapping is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
import time

def test_tca_integration():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          TCA INTEGRATION TEST                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Initialize AUREA with TCA
    aurea = AureaCore()
    
    # Check initial topology state
    print("Initial Topology State:")
    print("-" * 40)
    status = aurea.get_system_status()
    print(f"Total Nodes: {status['topology']['total_nodes']}")
    print(f"Total Edges: {status['topology']['total_edges']}")
    print(f"Constellations: {status['topology']['constellations']}")
    print(f"Total Mass: {status['topology']['total_mass']:.1f}")
    print()
    
    # Test inputs to create topological structure
    test_inputs = [
        ("Simple truth", "A fact about the world"),
        ("Paradox", "This statement is false"),
        ("Ethical claim", "We must protect the vulnerable"),
        ("Identity statement", "I am a collapse-bearing system"),
        ("Contradiction", "Everything is true and nothing is true"),
        ("Resonance test", "Truth survives collapse"),
        ("Another paradox", "I am lying right now"),
        ("Structural claim", "Systems must evolve or decay")
    ]
    
    print("Processing Test Inputs:")
    print("=" * 60)
    
    for category, input_text in test_inputs:
        print(f"\n[{category}]: \"{input_text}\"")
        result = aurea.process_input(input_text, source=f"test_{category}")
        
        # Show result
        print(f"  Pressure: {result['pressure_generated']:.2f}")
        if result['collapse_result']:
            print(f"  Collapsed: {not result['collapse_result'].passed}")
        if result['scar_formed']:
            print(f"  Scar: {result['scar_formed'].id}")
        if result['output_blocked']:
            print(f"  Output: {result['output']}")
        
        time.sleep(0.1)  # Small delay
    
    print("\n" + "=" * 60)
    print("FINAL TOPOLOGY STATE:")
    print("=" * 60)
    
    # Show final topology
    print(aurea.get_topology_visualization())
    
    # Show detailed metrics
    final_status = aurea.get_system_status()
    print("\nDETAILED METRICS:")
    print("-" * 40)
    print(f"Nodes Created: {final_status['topology']['total_nodes']}")
    print(f"Edges Formed: {final_status['topology']['total_edges']}")
    print(f"System Mass: {final_status['topology']['total_mass']:.1f}")
    
    # Show gravity wells
    if final_status['topology']['gravity_wells']:
        print("\nGravity Wells Formed:")
        for well in final_status['topology']['gravity_wells']:
            print(f"  {well['id']}: mass {well['mass']:.1f}, {well['edges']} connections")
    
    # Test navigation
    print("\n" + "=" * 60)
    print("TESTING NAVIGATION:")
    print("=" * 60)
    
    # Try to find a path between nodes
    nodes = list(aurea.tca.topology.nodes.keys())
    if len(nodes) >= 2:
        start = nodes[0]
        end = nodes[-1]
        path = aurea.tca.topology.find_path(start, end)
        if path:
            print(f"Path from {start} to {end}:")
            print(" -> ".join(path))
        else:
            print(f"No path found from {start} to {end}")
    
    # Test cascade risk calculation
    print("\n" + "=" * 60)
    print("CASCADE RISK ANALYSIS:")
    print("=" * 60)
    
    for node_id in nodes[:3]:  # Check first 3 nodes
        risk = aurea.tca.calculate_cascade_risk(node_id)
        print(f"{node_id}: cascade risk {risk:.2%}")
    
    # Save state
    print("\n" + "=" * 60)
    print("Saving topology state...")
    aurea.save_state()
    print("State saved to data/aurea_state.json")
    print("Topology saved to data/topology/tca_map.json")
    
    print("\n" + "=" * 60)
    print("TCA INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_tca_integration()
