"""
Minimal test of Reflex Grid to verify implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reflex.reflex_grid import ReflexGrid

# Initialize the Reflex Grid


def main():
    grid = ReflexGrid()
    print("✓ Reflex Grid initialized")
    print(f"✓ Reflexes loaded: {list(grid.reflexes.keys())}")

    # Test ICA with medium pressure
    responses = grid.evaluate_pressure(
        source_module="test",
        pressure_type="contradiction",
        pressure_level=0.75,
        metadata={'contradiction': {'domain': 'test'}}
    )
    print(f"✓ ICA response: {responses[0].action if responses else 'none'}")

    # Test GSR with high pressure  
    responses = grid.evaluate_pressure(
        source_module="test",
        pressure_type="coherence_check",
        pressure_level=0.9,
        metadata={'coherence': 0.2}
    )
    print(f"✓ GSR response: {responses[0].action if responses else 'none'}")

    print("\nReflex Grid implementation successful!")


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
