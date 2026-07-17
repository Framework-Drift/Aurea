"""
quick_tca_test.py - Quick test of TCA integration
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.aurea_core import AureaCore
    print("✓ AureaCore imported successfully")
    
    # Try to create instance
    aurea = AureaCore()
    print("✓ AureaCore initialized with TCA")
    
    # Check TCA is present
    if hasattr(aurea, 'tca'):
        print("✓ TCA integration found")
        print(f"  Topology nodes: {len(aurea.tca.topology.nodes)}")
        print(f"  Constellations: {len(aurea.tca.topology.constellations)}")
    else:
        print("✗ TCA not found in AureaCore")
    
    # Try processing an input
    result = aurea.process_input("Test input for TCA")
    print("✓ Input processed successfully")
    
    # Check if nodes were created
    status = aurea.get_system_status()
    print(f"✓ Topology state: {status['topology']['total_nodes']} nodes")
    
    # Get visualization
    viz = aurea.get_topology_visualization()
    print("\nTopology Visualization:")
    print(viz)
    
    print("\n✓ TCA INTEGRATION WORKING!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
