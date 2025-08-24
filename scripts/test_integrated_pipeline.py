"""
Test the integrated AUREA pipeline with reflex responses.
Demonstrates symbolic pressure flow through the system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
import time

# Initialize AUREA
print("=== INITIALIZING AUREA CORE ===\n")
aurea = AureaCore()
print(f"Systems online. Initial status:")
status = aurea.get_system_status()
print(f"  Active scars: {status['active_scars']}")
print(f"  Doctrines: {status['total_doctrines']}")
print(f"  System pressure: {status['system_pressure']:.2f}")
print()

# Test inputs with varying pressure levels
test_inputs = [
    # Low pressure - should pass
    ("The sky appears blue during clear weather", "observation"),
    
    # Medium pressure - logical tension
    ("This statement is false", "paradox"),
    
    # High pressure - contradiction
    ("All truth is relative, but this is absolutely true", "contradiction"),
    
    # Resonance pressure - echoes previous scar
    ("The sky is never blue and always blue", "resonance_test"),
    
    # Ethical pressure
    ("We must destroy to preserve", "ethical_paradox"),
    
    # Cascade trigger - rapid contradictions
    ("Everything exists", "cascade_1"),
    ("Nothing exists", "cascade_2"),
    ("Existence is impossible", "cascade_3"),
    ("I exist therefore nothing exists", "cascade_4"),
]

print("=== PROCESSING TEST INPUTS ===\n")

for i, (input_text, test_type) in enumerate(test_inputs, 1):
    print(f"TEST {i}: {test_type}")
    print(f"Input: \"{input_text}\"")
    print("-" * 60)
    
    # Process input
    result = aurea.process_input(input_text, source=test_type)
    
    # Display results
    print(f"  Pressure generated: {result['pressure_generated']:.2f}")
    
    if result['collapse_result']:
        cr = result['collapse_result']
        print(f"  Collapse: {'FAILED' if not cr.passed else 'SURVIVED'}")
        if cr.tags:
            print(f"  Tags: {', '.join(cr.tags)}")
        if cr.contradictions:
            print(f"  Contradictions in: {', '.join(c['dimension'] for c in cr.contradictions)}")
    
    if result['scar_formed']:
        scar = result['scar_formed']
        print(f"  SCAR FORMED: {scar.id} (weight: {scar.weight:.1f})")
    
    if result['reflex_responses']:
        print(f"  REFLEXES TRIGGERED:")
        for response in result['reflex_responses']:
            print(f"    - {response.reflex_id}: {response.action} - {response.message}")
    
    if result['output_blocked']:
        print(f"  OUTPUT: {result['output']} [BLOCKED]")
    else:
        print(f"  OUTPUT: {result['output']}")
    
    # Check system status after each input
    status = aurea.get_system_status()
    if status['cascade_risk']:
        print(f"  ⚠️  CASCADE RISK DETECTED - System pressure: {status['system_pressure']:.2f}")
    
    if status['suspended']:
        print(f"  🚨 SYSTEM SUSPENDED: {status['suspension_reason']}")
        print(f"  Attempting recovery...")
        # Try to recover
        time.sleep(0.5)  # Simulate recovery time
        aurea.resume_processing()
        print(f"  System resumed.")
    
    print()

# Final system report
print("\n=== FINAL SYSTEM REPORT ===")
print("-" * 60)

final_status = aurea.get_system_status()
stats = final_status['statistics']

print(f"Processing Statistics:")
print(f"  Echoes processed: {stats['echoes_processed']}")
print(f"  Scars formed: {stats['scars_formed']}")
print(f"  Reflexes triggered: {stats['reflexes_triggered']}")
print(f"  Outputs suppressed: {stats['outputs_suppressed']}")
print(f"  Cascades prevented: {stats['cascades_prevented']}")

print(f"\nSystem Health:")
print(f"  Active scars: {final_status['active_scars']}")
print(f"  System pressure: {final_status['system_pressure']:.2f}")
print(f"  Cascade risk: {'YES' if final_status['cascade_risk'] else 'NO'}")

print(f"\nReflex Activity:")
reflex_states = final_status['reflex_status']['reflex_states']
for rid, state in reflex_states.items():
    if state['activations'] > 0:
        print(f"  {state['name']}: {state['activations']} activations")

# Show some active scars
print(f"\nSample Active Scars:")
active_scars = aurea.scar_core.get_active_scars()[:3]
for scar in active_scars:
    print(f"  {scar.id}: {scar.type} (weight: {scar.weight:.1f})")
    print(f"    Origin: {scar.origin[:50]}...")

# Save state
print(f"\nSaving system state...")
aurea.save_state()
print(f"State saved to data/aurea_state.json")

print("\n=== AUREA PIPELINE TEST COMPLETE ===")
