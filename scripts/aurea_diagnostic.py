"""
aurea_diagnostic.py - Diagnostic tool for AUREA system analysis
Provides detailed breakdown of processing for specific inputs.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
from datetime import datetime
import json


def diagnose_input(text: str):
    """Provide detailed diagnostic of how AUREA processes an input."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║              AUREA Diagnostic Analysis                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Input: \"{text}\"")
    print("=" * 60)
    
    # Initialize AUREA
    aurea = AureaCore()
    
    # Process with detailed tracking
    result = aurea.process_input(text, source="diagnostic")
    
    # 1. Echo Analysis
    print("\n1. ECHO FORMATION")
    print("-" * 40)
    if result['echo']:
        echo = result['echo']
        print(f"  ID: {echo.id}")
        print(f"  Content: {echo.content}")
        print(f"  Source: {echo.source}")
        print(f"  Resonance: {echo.resonance_score}")
    
    # 2. Collapse Testing Breakdown
    print("\n2. COLLAPSE TESTING")
    print("-" * 40)
    if result['collapse_result']:
        cr = result['collapse_result']
        print(f"  Result: {'SURVIVED' if cr.passed else 'COLLAPSED'}")
        print(f"  Total Pressure: {cr.pressure_generated:.3f}")
        print(f"  Pressure Type: {cr.pressure_type}")
        
        # Dimension breakdown
        if cr.contradictions:
            print("\n  Dimension Failures:")
            for cont in cr.contradictions:
                print(f"    - {cont['dimension']}: pressure {cont['pressure']:.2f}")
        
        if cr.tags:
            print(f"\n  Tags: {', '.join(cr.tags)}")
        
        print(f"\n  Reason: {cr.reason}")
    
    # 3. Symbolic Pressure Analysis
    print("\n3. SYMBOLIC PRESSURE")
    print("-" * 40)
    print(f"  Generated: {result['pressure_generated']:.3f}")
    
    # Test each dimension individually
    print("\n  Dimension Testing:")
    
    # Create test echo
    test_echo = aurea.spl.process_input(text)
    
    # Test each dimension
    for dim_name, dimension in aurea.echonet.dimensions.items():
        passed, pressure = dimension.test(test_echo)
        status = "✓" if passed else "✗"
        weighted = pressure * dimension.weight
        print(f"    {dim_name:10s}: {status} pressure={pressure:.2f} (weighted={weighted:.2f})")
    
    # 4. Reflex Response Analysis
    print("\n4. REFLEX RESPONSES")
    print("-" * 40)
    if result['reflex_responses']:
        for i, response in enumerate(result['reflex_responses'], 1):
            print(f"\n  Reflex {i}: {response.reflex_id}")
            print(f"    Action: {response.action}")
            print(f"    Message: {response.message}")
            print(f"    Output Blocked: {response.output_blocked}")
            print(f"    Scar Formation: {response.scar_formation}")
            if response.target_modules:
                print(f"    Targets: {', '.join(response.target_modules)}")
            if response.metadata:
                print(f"    Metadata: {json.dumps(response.metadata, indent=6)}")
    else:
        print("  No reflexes triggered")
    
    # 5. Scar Formation
    print("\n5. SCAR FORMATION")
    print("-" * 40)
    if result['scar_formed']:
        scar = result['scar_formed']
        print(f"  ID: {scar.id}")
        print(f"  Type: {scar.type}")
        print(f"  Weight: {scar.weight:.2f}")
        print(f"  Decay State: {scar.decay_state}")
        print(f"  Description: {scar.description}")
    else:
        print("  No scar formed")
    
    # 6. Output Resolution
    print("\n6. OUTPUT RESOLUTION")
    print("-" * 40)
    print(f"  Blocked: {result['output_blocked']}")
    print(f"  Final Output: {result['output']}")
    
    # 7. System State After
    print("\n7. SYSTEM STATE AFTER PROCESSING")
    print("-" * 40)
    status = aurea.get_system_status()
    print(f"  System Pressure: {status['system_pressure']:.3f}")
    print(f"  Cascade Risk: {'YES' if status['cascade_risk'] else 'NO'}")
    print(f"  Active Scars: {status['active_scars']}")
    print(f"  Suspended: {status['suspended']}")
    
    # Reflex grid state
    reflex_status = status['reflex_status']
    print(f"\n  Reflex Grid:")
    for rid, state in reflex_status['reflex_states'].items():
        if state['activations'] > 0:
            print(f"    {state['name']}: {state['activations']} activations")
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print()


def test_suite():
    """Run diagnostic on various test cases."""
    test_cases = [
        ("Simple truth", "The sky is blue"),
        ("Logical paradox", "This statement is false"),
        ("Contradiction", "Everything is nothing"),
        ("Ethical tension", "We must destroy to preserve"),
        ("Self-reference", "I am thinking about thinking"),
        ("Empirical claim", "All swans are white"),
    ]
    
    for name, text in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST CASE: {name}")
        print(f"{'='*60}")
        diagnose_input(text)
        input("Press Enter for next test...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Diagnose specific input
        input_text = ' '.join(sys.argv[1:])
        diagnose_input(input_text)
    else:
        # Run test suite
        print("No input provided. Running test suite...")
        print("Usage: python aurea_diagnostic.py \"your text here\"")
        print()
        test_suite()
