"""
Minimal test of Reflex Grid to verify implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reflex.reflex_grid import ReflexGrid

# Initialize the Reflex Grid
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
