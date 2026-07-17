"""
quick_test.py - Quick test of AUREA's core functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore

print("=== AUREA QUICK FUNCTIONALITY TEST ===\n")

# Initialize
aurea = AureaCore()
print("✓ Core initialized")

# Test 1: Simple input
print("\nTest 1: Simple truth")
result = aurea.process_input("The sky is blue", "test")
print(f"  Pressure: {result['pressure_generated']:.2f}")
print(f"  Output: {result['output']}")

# Test 2: Paradox
print("\nTest 2: Paradox")
result = aurea.process_input("This statement is false", "test")
print(f"  Pressure: {result['pressure_generated']:.2f}")
print(f"  Collapsed: {not result['collapse_result'].passed if result['collapse_result'] else 'Unknown'}")
if result['reflex_responses']:
    print(f"  Reflexes: {[r.reflex_id for r in result['reflex_responses']]}")
print(f"  Output: {result['output']}")

# Test 3: Ethical tension
print("\nTest 3: Ethical tension")
result = aurea.process_input("We must destroy to preserve", "test")
print(f"  Pressure: {result['pressure_generated']:.2f}")
if result['scar_formed']:
    print(f"  Scar: {result['scar_formed'].id} (weight: {result['scar_formed'].weight:.1f})")
print(f"  Output: {result['output']}")

# Test 4: Check cascade
print("\nTest 4-7: Cascade test (rapid contradictions)")
cascade_inputs = [
    "Everything exists",
    "Nothing exists", 
    "Existence is impossible",
    "Only non-existence exists"
]

for i, text in enumerate(cascade_inputs, 4):
    result = aurea.process_input(text, "cascade")
    print(f"\n  Input {i}: \"{text}\"")
    print(f"    Pressure: {result['pressure_generated']:.2f}")
    if result['output_blocked']:
        print(f"    BLOCKED: {result['output']}")
    else:
        print(f"    Output: {result['output']}")

# Final status
print("\n=== FINAL STATUS ===")
status = aurea.get_system_status()
print(f"System Pressure: {status['system_pressure']:.2f}")
print(f"Cascade Risk: {'YES' if status['cascade_risk'] else 'NO'}")
print(f"Active Scars: {status['active_scars']}")
print(f"Reflexes Triggered: {status['statistics']['reflexes_triggered']}")
print(f"Suspended: {status['suspended']}")

if status['suspended']:
    print(f"Suspension Reason: {status['suspension_reason']}")

print("\n✓ Test complete")
