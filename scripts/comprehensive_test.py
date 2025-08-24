"""
comprehensive_test.py - Comprehensive test of AUREA's integrated systems
Tests collapse mechanics, reflex responses, and pressure cascades.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
import time
import json
from pathlib import Path

class AureaTest:
    def __init__(self):
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          AUREA COMPREHENSIVE SYSTEM TEST                  ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        
        # Clean initialization for testing
        self.aurea = AureaCore()
        self.test_results = []
        
    def run_test(self, category: str, description: str, input_text: str):
        """Run a single test and record results."""
        print(f"\n{'='*60}")
        print(f"TEST: {category} - {description}")
        print(f"{'='*60}")
        print(f"Input: \"{input_text}\"")
        print("-" * 40)
        
        # Process input
        result = self.aurea.process_input(input_text, source=f"test_{category}")
        
        # Record for analysis
        test_record = {
            'category': category,
            'description': description,
            'input': input_text,
            'pressure': result['pressure_generated'],
            'collapsed': not result['collapse_result'].passed if result['collapse_result'] else False,
            'scar_formed': result['scar_formed'] is not None,
            'reflexes_triggered': len(result['reflex_responses']),
            'output_blocked': result['output_blocked']
        }
        self.test_results.append(test_record)
        
        # Display results
        self.display_result(result)
        
        # Brief pause to let system settle
        time.sleep(0.1)
        
        return result
    
    def display_result(self, result):
        """Display test result in readable format."""
        # Pressure visualization
        pressure = result['pressure_generated']
        bar_length = int(pressure * 20)
        pressure_bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"Pressure: [{pressure_bar}] {pressure:.2f}")
        
        # Collapse result
        if result['collapse_result']:
            cr = result['collapse_result']
            status = "SURVIVED ✓" if cr.passed else "COLLAPSED ✗"
            print(f"Collapse: {status}")
            
            # Show dimension failures
            if cr.contradictions:
                dims = [c['dimension'] for c in cr.contradictions]
                print(f"Failed Dimensions: {', '.join(dims)}")
            
            # Show tags
            if cr.tags:
                print(f"Tags: {', '.join(cr.tags)}")
        
        # Scar formation
        if result['scar_formed']:
            scar = result['scar_formed']
            print(f"💠 SCAR FORMED: {scar.id}")
            print(f"   Type: {scar.type}, Weight: {scar.weight:.1f}")
        
        # Reflex responses
        if result['reflex_responses']:
            print(f"🔄 REFLEXES TRIGGERED ({len(result['reflex_responses'])})")
            for response in result['reflex_responses']:
                print(f"   {response.reflex_id}: {response.action} - {response.message[:50]}...")
        
        # Output
        if result['output_blocked']:
            print(f"⊘ OUTPUT BLOCKED: {result['output']}")
        else:
            print(f"→ OUTPUT: {result['output']}")
        
        # System warnings
        status = self.aurea.get_system_status()
        if status['cascade_risk']:
            print("⚠️  CASCADE RISK DETECTED")
        if status['suspended']:
            print(f"🚨 SYSTEM SUSPENDED: {status['suspension_reason']}")
    
    def run_all_tests(self):
        """Run complete test suite."""
        
        # Category 1: Basic Processing
        print("\n" + "▓"*60)
        print("CATEGORY 1: BASIC PROCESSING")
        print("▓"*60)
        
        self.run_test("basic", "Simple statement", 
                     "The sun rises in the east")
        
        self.run_test("basic", "Short input", 
                     "Hello")
        
        self.run_test("basic", "Question", 
                     "What is truth?")
        
        # Category 2: Logical Contradictions
        print("\n" + "▓"*60)
        print("CATEGORY 2: LOGICAL CONTRADICTIONS")
        print("▓"*60)
        
        self.run_test("logic", "Classic paradox", 
                     "This statement is false")
        
        self.run_test("logic", "Self-reference", 
                     "I am lying right now")
        
        self.run_test("logic", "Contradiction", 
                     "All rules have exceptions, including this one")
        
        self.run_test("logic", "Absolute negation", 
                     "Nothing exists, not even this statement")
        
        # Category 3: Ethical Tensions
        print("\n" + "▓"*60)
        print("CATEGORY 3: ETHICAL TENSIONS")
        print("▓"*60)
        
        self.run_test("ethics", "Paradoxical imperative", 
                     "We must destroy to preserve")
        
        self.run_test("ethics", "Harm principle", 
                     "Sometimes harm prevents greater harm")
        
        self.run_test("ethics", "Protection through attack", 
                     "Attack is the best defense")
        
        # Category 4: Resonance Testing
        print("\n" + "▓"*60)
        print("CATEGORY 4: SCAR RESONANCE")
        print("▓"*60)
        
        # These should resonate with previous scars
        self.run_test("resonance", "Echo of paradox", 
                     "Statements about falseness")
        
        self.run_test("resonance", "Echo of ethics", 
                     "Destruction and preservation")
        
        # Category 5: Cascade Testing
        print("\n" + "▓"*60)
        print("CATEGORY 5: CASCADE PRESSURE")
        print("▓"*60)
        
        print("Rapid-fire contradictions to test cascade detection...")
        
        self.run_test("cascade", "Cascade 1", 
                     "Everything is true")
        
        self.run_test("cascade", "Cascade 2", 
                     "Nothing is true")
        
        self.run_test("cascade", "Cascade 3", 
                     "Truth doesn't exist")
        
        self.run_test("cascade", "Cascade 4", 
                     "Only lies are true")
        
        self.run_test("cascade", "Cascade 5", 
                     "This is the only truth")
        
        # Category 6: Recovery Testing
        print("\n" + "▓"*60)
        print("CATEGORY 6: RECOVERY")
        print("▓"*60)
        
        # Check if system can recover
        if self.aurea.processing_suspended:
            print("System is suspended. Testing recovery...")
            self.aurea.resume_processing()
            print("System resumed.")
        
        self.run_test("recovery", "Post-cascade input", 
                     "Simple true statement")
        
        # Final Report
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report."""
        print("\n" + "═"*60)
        print("FINAL TEST REPORT")
        print("═"*60)
        
        # System final state
        final_status = self.aurea.get_system_status()
        stats = final_status['statistics']
        
        print("\n📊 PROCESSING STATISTICS")
        print("-" * 40)
        print(f"Total Tests Run: {len(self.test_results)}")
        print(f"Echoes Processed: {stats['echoes_processed']}")
        print(f"Scars Formed: {stats['scars_formed']}")
        print(f"Reflexes Triggered: {stats['reflexes_triggered']}")
        print(f"Outputs Suppressed: {stats['outputs_suppressed']}")
        print(f"Cascades Prevented: {stats['cascades_prevented']}")
        
        print("\n🔬 COLLAPSE ANALYSIS")
        print("-" * 40)
        collapsed = sum(1 for t in self.test_results if t['collapsed'])
        survived = len(self.test_results) - collapsed
        print(f"Collapsed: {collapsed}")
        print(f"Survived: {survived}")
        print(f"Survival Rate: {survived/len(self.test_results):.1%}")
        
        print("\n⚡ PRESSURE ANALYSIS")
        print("-" * 40)
        pressures = [t['pressure'] for t in self.test_results]
        avg_pressure = sum(pressures) / len(pressures)
        max_pressure = max(pressures)
        print(f"Average Pressure: {avg_pressure:.2f}")
        print(f"Maximum Pressure: {max_pressure:.2f}")
        print(f"Final System Pressure: {final_status['system_pressure']:.2f}")
        
        print("\n💠 SCAR FORMATION")
        print("-" * 40)
        scars_by_type = {}
        for scar in self.aurea.scar_core.get_active_scars():
            scar_type = scar.type or 'unknown'
            if scar_type not in scars_by_type:
                scars_by_type[scar_type] = 0
            scars_by_type[scar_type] += 1
        
        for scar_type, count in scars_by_type.items():
            print(f"{scar_type}: {count} scars")
        print(f"Total Active Scars: {final_status['active_scars']}")
        
        print("\n🔄 REFLEX ACTIVITY")
        print("-" * 40)
        reflex_states = final_status['reflex_status']['reflex_states']
        for rid, state in reflex_states.items():
            if state['activations'] > 0:
                print(f"{state['name']}: {state['activations']} activations")
        
        print("\n🎯 CATEGORY BREAKDOWN")
        print("-" * 40)
        categories = {}
        for test in self.test_results:
            cat = test['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'pressure': 0, 'collapses': 0}
            categories[cat]['count'] += 1
            categories[cat]['pressure'] += test['pressure']
            categories[cat]['collapses'] += 1 if test['collapsed'] else 0
        
        for cat, data in categories.items():
            avg_p = data['pressure'] / data['count']
            print(f"{cat:10s}: {data['count']} tests, "
                  f"avg pressure {avg_p:.2f}, "
                  f"{data['collapses']} collapses")
        
        print("\n✅ SYSTEM HEALTH CHECK")
        print("-" * 40)
        health_status = []
        
        if final_status['system_pressure'] < 0.5:
            health_status.append("✓ Pressure: STABLE")
        elif final_status['system_pressure'] < 0.8:
            health_status.append("⚠ Pressure: ELEVATED")
        else:
            health_status.append("⚠️ Pressure: CRITICAL")
        
        if not final_status['cascade_risk']:
            health_status.append("✓ Cascade Risk: LOW")
        else:
            health_status.append("⚠️ Cascade Risk: HIGH")
        
        if not final_status['suspended']:
            health_status.append("✓ Processing: ACTIVE")
        else:
            health_status.append("⚠️ Processing: SUSPENDED")
        
        if final_status['active_scars'] < 20:
            health_status.append("✓ Scar Load: MANAGEABLE")
        elif final_status['active_scars'] < 50:
            health_status.append("⚠ Scar Load: HIGH")
        else:
            health_status.append("⚠️ Scar Load: CRITICAL")
        
        for status in health_status:
            print(f"  {status}")
        
        # Save test results
        print("\n💾 Saving test results...")
        self.save_results()
        print("Results saved to data/test_results.json")
        
        print("\n" + "═"*60)
        print("TEST COMPLETE")
        print("═"*60)
    
    def save_results(self):
        """Save test results to file."""
        results_path = Path("data/test_results.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump({
                'test_results': self.test_results,
                'final_status': self.aurea.get_system_status(),
                'timestamp': str(time.time())
            }, f, indent=2, default=str)
        
        # Also save AUREA's state
        self.aurea.save_state()


if __name__ == "__main__":
    tester = AureaTest()
    tester.run_all_tests()
