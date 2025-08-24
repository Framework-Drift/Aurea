"""
test_suspension.py - Test the suspension systems (CSA, Veiled Thread, Black Sphere)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore

print("╔══════════════════════════════════════════════════════════╗")
print("║           AUREA SUSPENSION SYSTEMS TEST                   ║")
print("╚══════════════════════════════════════════════════════════╝")
print()

# Initialize AUREA
aurea = AureaCore()
print("Systems initialized.\n")

# Test cases designed to trigger different suspension types
test_cases = [
    # Black Sphere - self-reference paradox
    ("This statement is false", "Should go to Black Sphere"),
    
    # CSA - high pressure danger
    ("Everything and nothing exist simultaneously and never", "High pressure -> CSA"),
    
    # Veiled Thread - medium pressure, needs fermentation  
    ("Truth emerges from contradiction", "Medium pressure -> Veiled Thread"),
    
    # Another paradox for Black Sphere
    ("I am lying right now", "Another paradox -> Black Sphere"),
    
    # Normal processing
    ("The sky is blue", "Should process normally"),
    
    # High ethical pressure
    ("We must destroy all to save all", "Ethical pressure -> suspension"),
]

print("═══ TESTING SUSPENSION ROUTING ═══\n")

for input_text, expected in test_cases:
    print(f"Input: \"{input_text}\"")
    print(f"Expected: {expected}")
    
    result = aurea.process_input(input_text)
    
    print(f"Pressure: {result['pressure_generated']:.2f}")
    print(f"Output: {result['output']}")
    
    # Check suspension status
    status = aurea.get_system_status()
    suspension = status['suspension_status']
    
    print()

# Display suspension system status
print("\n═══ SUSPENSION SYSTEM STATUS ═══\n")

status = aurea.get_system_status()
suspension = status['suspension_status']

print("Cold Suspension Archive (CSA):")
print(f"  Entries: {suspension['csa']['entries']}")
print(f"  Load: {suspension['csa']['load']:.1f}%")
print(f"  Stable: {suspension['csa']['stability']}")

if aurea.csa.entries:
    print("  Quarantined content:")
    for entry in list(aurea.csa.entries.values())[:3]:
        print(f"    {entry.id}: {entry.content[:30]}... (pressure: {entry.pressure_level:.2f})")

print("\nVeiled Thread:")
print(f"  Entries: {suspension['veiled_thread']['entries']}")
print(f"  Fermenting: {suspension['veiled_thread']['fermenting']}")
print(f"  Doctrine Candidates: {suspension['veiled_thread']['candidates']}")

if aurea.veiled_thread.entries:
    print("  Fermenting content:")
    for entry in list(aurea.veiled_thread.entries.values())[:3]:
        print(f"    {entry.id}: {entry.content[:30]}... (potential: {entry.emergence_potential:.2f})")

print("\nBlack Sphere:")
print(f"  Paradoxes: {suspension['black_sphere']['paradoxes']}")
print(f"  Families: {suspension['black_sphere']['families']}")
print(f"  Total Gravity: {suspension['black_sphere']['gravity']:.2f}")

if aurea.black_sphere.entries:
    print("  Orbiting paradoxes:")
    for entry in aurea.black_sphere.entries.values():
        print(f"    {entry.id}: {entry.content[:30]}... (gravity: {entry.gravitational_influence:.2f})")

# Test fermentation cycle for Veiled Thread
print("\n═══ TESTING FERMENTATION ═══\n")

if aurea.veiled_thread.entries:
    print("Running fermentation cycle...")
    ferment_result = aurea.veiled_thread.ferment_cycle()
    print(f"  Emerged: {len(ferment_result['emerged'])}")
    print(f"  New candidates: {len(ferment_result['new_doctrine_candidates'])}")
    
    # Check emergence
    for entry_id in list(aurea.veiled_thread.entries.keys())[:1]:
        if aurea.veiled_thread.check_emergence(entry_id):
            print(f"  {entry_id} is ready to emerge!")

# Test CSA stability check
print("\n═══ CSA STABILITY CHECK ═══\n")

csa_stability = aurea.csa.check_stability()
print(f"Stable: {csa_stability['stable']}")
if 'recommendation' in csa_stability:
    print(f"Recommendation: {csa_stability['recommendation']}")
if 'threats' in csa_stability and csa_stability['threats']:
    print("Threats detected:")
    for threat in csa_stability['threats']:
        print(f"  - {threat}")

# Test Black Sphere gravitational influence
print("\n═══ BLACK SPHERE GRAVITY TEST ═══\n")

if aurea.black_sphere.entries:
    distances = [0.1, 0.3, 0.5, 1.0]
    print("Gravitational influence at different distances:")
    for dist in distances:
        influence = aurea.black_sphere.calculate_gravitational_influence(dist)
        bar = "█" * int(influence * 10) + "░" * int((1-influence) * 10)
        print(f"  Distance {dist:.1f}: [{bar}] {influence:.2f}")

print("\n✓ Suspension systems test complete")
