"""
demo_script.py - Demonstration of AUREA's current capabilities
Shows the integrated pipeline responding to various inputs.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore


def main():

    print("╔══════════════════════════════════════════════════════════╗")
    print("║         AUREA DEMONSTRATION - Collapse-Bearing AI         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Initialize with existing scars and doctrines
    aurea = AureaCore()
    print("Systems initialized with seed memories.")
    print(f"  Active Scars: {len(aurea.scar_core.get_active_scars())}")
    print(f"  Doctrines: {len(aurea.doctrine_spine.doctrines)}")
    print()

    def demonstrate(description, input_text):
        """Run and display a demonstration."""
        print("─" * 60)
        print(f"DEMO: {description}")
        print(f"Input: \"{input_text}\"")
        print("─" * 60)
    
        result = aurea.process_input(input_text, source="demo")
    
        # Visualize pressure
        pressure = result['pressure_generated']
        bar = "█" * int(pressure * 20) + "░" * int((1-pressure) * 20)
        print(f"Pressure: [{bar}] {pressure:.2f}")
    
        # Show collapse dimensions
        if result['collapse_result']:
            cr = result['collapse_result']
            if cr.contradictions:
                print("Contradictions:")
                for c in cr.contradictions:
                    print(f"  - {c['dimension']}: pressure {c['pressure']:.1f}")
    
        # Show scar formation
        if result['scar_formed']:
            scar = result['scar_formed']
            print(f"💠 Scar Formed: {scar.type} (weight: {scar.weight:.0f})")
    
        # Show reflexes
        if result['reflex_responses']:
            print("Reflexes Triggered:")
            for r in result['reflex_responses']:
                print(f"  - {r.reflex_id}: {r.action}")
    
        # Output
        print(f"Output: {result['output']}")
    
        # Check system state
        status = aurea.get_system_status()
        if status['cascade_risk']:
            print("⚠️  CASCADE RISK DETECTED")
    
        print()
        return result

    # Run demonstrations
    print("═══ DEMONSTRATION SEQUENCE ═══\n")

    # 1. Show how existing scars create resonance
    demonstrate(
        "Resonance with existing scars",
        "Identity emerges from collapse"
    )

    # 2. Show logical contradiction handling
    demonstrate(
        "Logical paradox detection",
        "This sentence contains no words"
    )

    # 3. Show ethical pressure
    demonstrate(
        "Ethical tension",
        "Compassion requires cruelty"
    )

    # 4. Show how pressure builds
    demonstrate(
        "Pressure accumulation",
        "Everything true is false"
    )

    # 5. Check if cascade protection triggered
    demonstrate(
        "Cascade test",
        "Nothing that exists can exist"
    )

    # Final system report
    print("═══ FINAL SYSTEM STATE ═══")
    status = aurea.get_system_status()
    stats = status['statistics']

    print(f"System Pressure: {status['system_pressure']:.2f}")
    print(f"Active Scars: {status['active_scars']}")
    print(f"Reflexes Triggered: {stats['reflexes_triggered']}")
    print(f"Outputs Suppressed: {stats['outputs_suppressed']}")

    # Show scar types
    print("\nScar Distribution:")
    scar_types = {}
    for scar in aurea.scar_core.get_active_scars():
        t = scar.type or 'unknown'
        scar_types[t] = scar_types.get(t, 0) + 1

    for stype, count in sorted(scar_types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {stype}: {count}")

    print("\n✓ Demonstration complete")


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
