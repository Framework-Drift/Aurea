"""
quick_tca_test.py - Quick test of TCA integration
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():

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


# RULING 59 res.3 (2026-08-01) - IMPORT-INERTNESS.
#
# The body above used to run at MODULE level, so merely IMPORTING this
# file executed AUREA against real default store paths. That is the root
# cause of the contamination incident this ruling closes: a bare `pytest`
# collected `scripts/`, and collection alone wrote twelve files into
# shared `data/runtime/`.
#
# Nothing about the CLI changed - not one statement was added, removed or
# reordered. The body was indented into `main()` and is called here.
if __name__ == "__main__":
    main()
