"""
aurea_repl.py - Enhanced Interactive REPL for AUREA
Improved visualization and feedback for collapse-bearing intelligence.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aurea_core import AureaCore
import json
from pathlib import Path
from datetime import datetime


class AureaREPL:
    """Interactive REPL for AUREA system with enhanced visualization."""
    
    def __init__(self):
        print("╔══════════════════════════════════════════════════════════╗")
        print("║               AUREA - Collapse-Bearing Intelligence       ║")
        print("║                    Interactive Terminal v1.0              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("Initializing systems...")
        
        self.aurea = AureaCore()
        self.running = True
        self.verbose = False  # Toggle for detailed output
        
        # Try to load previous state
        state_file = Path("data/aurea_state.json")
        if state_file.exists():
            print("Loading previous state...")
            self.aurea.load_state()
        
        print("Systems online. Type 'help' for commands.\n")
        
    def run(self):
        """Main REPL loop."""
        while self.running:
            try:
                # Show pressure indicator
                status = self.aurea.get_system_status()
                pressure = status['system_pressure']
                
                # Enhanced pressure indicator with color codes
                if pressure < 0.3:
                    indicator = "○"  # Low - stable
                    color = ""
                elif pressure < 0.6:
                    indicator = "◐"  # Medium - monitoring
                    color = ""
                elif pressure < 0.8:
                    indicator = "◑"  # High - warning
                    color = ""
                else:
                    indicator = "●"  # Critical - danger
                    color = ""
                
                # Show suspended state
                if status['suspended']:
                    indicator = "⊗"  # Suspended
                
                # Get input
                user_input = input(f"[{indicator}] aurea> ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input[1:])
                else:
                    # Process as regular input
                    self.process_input(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupt received. Use '/exit' to quit properly.")
            except Exception as e:
                print(f"Error: {e}")
    
    def process_input(self, text: str):
        """Process user input through AUREA pipeline with enhanced feedback."""
        print()  # Add spacing for clarity
        
        # Process through pipeline
        result = self.aurea.process_input(text, source="user")
        
        # Enhanced output formatting
        if self.verbose or result['pressure_generated'] > 0.3:
            self.show_processing_details(result)
        
        # Main output
        if result['output']:
            if result['output_blocked']:
                print(f"⊘ {result['output']}")
            else:
                print(f"→ {result['output']}")
        
        # System warnings
        status = self.aurea.get_system_status()
        if status['cascade_risk']:
            print("⚠️  CASCADE RISK: System approaching critical pressure")
        if status['suspended']:
            print(f"🚨 SUSPENDED: {status['suspension_reason']}")
            print("   Use '/resume' to continue")
        
        # Show active scar count if growing
        if status['active_scars'] > 10:
            print(f"📊 Active scars: {status['active_scars']} (growing)")
        
        print()  # Add spacing
    
    def show_processing_details(self, result):
        """Show detailed processing information."""
        # Pressure visualization
        pressure = result['pressure_generated']
        bar_length = int(pressure * 20)
        pressure_bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"Pressure: [{pressure_bar}] {pressure:.2f}")
        
        # Collapse dimensions
        if result['collapse_result']:
            cr = result['collapse_result']
            
            # Show which dimensions contributed
            if cr.contradictions:
                dims = []
                for c in cr.contradictions:
                    dims.append(f"{c['dimension']}({c['pressure']:.1f})")
                print(f"Collapse: {' + '.join(dims)}")
            
            # Show tags
            if cr.tags:
                print(f"Tags: [{', '.join(cr.tags)}]")
        
        # Scar formation with details
        if result['scar_formed']:
            scar = result['scar_formed']
            print(f"💠 Scar: {scar.id}")
            print(f"   Type: {scar.type}, Weight: {scar.weight:.1f}")
        
        # Reflex cascade
        if result['reflex_responses']:
            print("Reflexes:")
            for response in result['reflex_responses']:
                symbol = {
                    'suppress': '⊘',
                    'reroute': '↻',
                    'suspend': '⏸',
                    'monitor': '👁',
                    'cascade': '🌊'
                }.get(response.action, '•')
                print(f"  {symbol} {response.reflex_id}: {response.message[:50]}...")
    
    def handle_command(self, command: str):
        """Handle REPL commands."""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'help':
            self.show_help()
        elif cmd == 'status':
            self.show_status()
        elif cmd == 'scars':
            self.show_scars()
        elif cmd == 'doctrines':
            self.show_doctrines()
        elif cmd == 'reflexes':
            self.show_reflexes()
        elif cmd == 'pressure':
            self.show_pressure()
        elif cmd == 'verbose':
            self.toggle_verbose()
        elif cmd == 'test':
            self.run_test_sequence()
        elif cmd == 'save':
            self.save_state()
        elif cmd == 'load':
            self.load_state()
        elif cmd == 'resume':
            self.resume_system()
        elif cmd == 'reset':
            self.reset_system()
        elif cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
        elif cmd == 'exit' or cmd == 'quit':
            self.exit_repl()
        else:
            print(f"Unknown command: {cmd}")
    
    def show_help(self):
        """Display help information."""
        print("\n╔═══════════════════════════════════════╗")
        print("║           AUREA Commands              ║")
        print("╚═══════════════════════════════════════╝")
        print()
        print("  /help       - Show this help message")
        print("  /status     - Show system status")
        print("  /scars      - List active scars")
        print("  /doctrines  - List current doctrines")
        print("  /reflexes   - Show reflex activity")
        print("  /pressure   - Show pressure analysis")
        print("  /verbose    - Toggle detailed output")
        print("  /test       - Run test sequence")
        print("  /save       - Save current state")
        print("  /load       - Load saved state")
        print("  /resume     - Resume if suspended")
        print("  /reset      - Reset to clean state")
        print("  /clear      - Clear screen")
        print("  /exit       - Exit REPL")
        print()
        print("Pressure Indicators:")
        print("  ○ Low    ◐ Medium    ◑ High    ● Critical    ⊗ Suspended")
        print()
        print("Just type normally to send input through the pipeline.")
        print()
    
    def show_status(self):
        """Display detailed system status."""
        status = self.aurea.get_system_status()
        stats = status['statistics']
        
        print("\n╔═══════════════════════════════════════╗")
        print("║           System Status               ║")
        print("╚═══════════════════════════════════════╝")
        print()
        
        # State visualization
        if status['suspended']:
            print(f"State: 🚨 SUSPENDED")
            print(f"Reason: {status['suspension_reason']}")
        else:
            print(f"State: ✓ ACTIVE")
        
        # Pressure gauge
        pressure = status['system_pressure']
        bar_length = int(pressure * 30)
        pressure_bar = "█" * bar_length + "░" * (30 - bar_length)
        print(f"\nPressure: [{pressure_bar}] {pressure:.2%}")
        
        # Risk indicators
        print(f"Cascade Risk: {'🔴 YES' if status['cascade_risk'] else '🟢 NO'}")
        
        # Core metrics
        print(f"\nCore Systems:")
        print(f"  Active Scars: {status['active_scars']}")
        print(f"  Doctrines: {status['total_doctrines']}")
        print(f"  Reflexes Online: {status['reflex_status']['total_reflexes']}")
        
        # Activity statistics
        print(f"\nActivity Statistics:")
        print(f"  Echoes Processed: {stats['echoes_processed']}")
        print(f"  Scars Formed: {stats['scars_formed']}")
        print(f"  Reflexes Triggered: {stats['reflexes_triggered']}")
        print(f"  Outputs Suppressed: {stats['outputs_suppressed']}")
        print(f"  Cascades Prevented: {stats['cascades_prevented']}")
        print()
    
    def show_scars(self):
        """Display active scars with details."""
        scars = self.aurea.scar_core.get_active_scars()
        
        print(f"\n╔═══════════════════════════════════════╗")
        print(f"║      Active Scars ({len(scars):3d} total)         ║")
        print(f"╚═══════════════════════════════════════╝")
        print()
        
        if not scars:
            print("  No active scars")
        else:
            # Group by type
            by_type = {}
            for scar in scars:
                scar_type = scar.type or 'unknown'
                if scar_type not in by_type:
                    by_type[scar_type] = []
                by_type[scar_type].append(scar)
            
            for scar_type, type_scars in by_type.items():
                print(f"  {scar_type.upper()} ({len(type_scars)})")
                for scar in type_scars[:3]:  # Show first 3 of each type
                    weight_bar = "▰" * int(scar.weight / 20)
                    print(f"    {scar.id}: weight {scar.weight:.0f} {weight_bar}")
                if len(type_scars) > 3:
                    print(f"    ... and {len(type_scars) - 3} more")
        print()
    
    def show_doctrines(self):
        """Display current doctrines."""
        doctrines = self.aurea.doctrine_spine.doctrines
        
        print(f"\n╔═══════════════════════════════════════╗")
        print(f"║        Doctrines ({len(doctrines):2d} total)           ║")
        print(f"╚═══════════════════════════════════════╝")
        print()
        
        for doctrine in doctrines:
            seed = " 🌱" if doctrine.is_seed else ""
            print(f"  {doctrine.id}: {doctrine.name}{seed}")
            if doctrine.description:
                print(f"    \"{doctrine.description}\"")
            if doctrine.scar_links:
                print(f"    Scars: {len(doctrine.scar_links)} linked")
            if doctrine.mutation_lineage:
                print(f"    Mutations: {len(doctrine.mutation_lineage)}")
        print()
    
    def show_reflexes(self):
        """Display reflex activity."""
        status = self.aurea.reflex_grid.get_system_status()
        
        print(f"\n╔═══════════════════════════════════════╗")
        print(f"║         Reflex Activity               ║")
        print(f"╚═══════════════════════════════════════╝")
        print()
        
        for rid, state in status['reflex_states'].items():
            symbol = "🟢" if state['activations'] > 0 else "⚫"
            print(f"  {symbol} {state['name']}")
            print(f"      Priority: {state['priority']}")
            print(f"      Activations: {state['activations']}")
            if state['last_triggered']:
                # Parse and format time
                last = datetime.fromisoformat(state['last_triggered'])
                ago = (datetime.now() - last).seconds
                print(f"      Last: {ago}s ago")
        
        cascade_risk = self.aurea.reflex_grid.check_cascade_risk()
        print(f"\n  Cascade Risk Score: {cascade_risk:.2%}")
        print()
    
    def show_pressure(self):
        """Display detailed pressure analysis."""
        monitor = self.aurea.pressure_monitor
        
        print(f"\n╔═══════════════════════════════════════╗")
        print(f"║        Pressure Analysis              ║")
        print(f"╚═══════════════════════════════════════╝")
        print()
        
        current = monitor.get_system_pressure()
        
        # Pressure meter
        bar_length = int(current * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"Current: [{bar}]")
        print(f"         {current:.2f} / {monitor.cascade_threshold} (cascade threshold)")
        
        # Pressure history graph (simple ASCII)
        if monitor.pressure_history:
            print("\nRecent History:")
            recent = monitor.pressure_history[-20:]
            for event in recent[-5:]:
                level = event['level']
                bar = "▰" * int(level * 10)
                print(f"  {event['source']:12s} [{bar:10s}] {level:.2f}")
        
        print()
    
    def toggle_verbose(self):
        """Toggle verbose output mode."""
        self.verbose = not self.verbose
        print(f"Verbose mode: {'ON' if self.verbose else 'OFF'}")
    
    def run_test_sequence(self):
        """Run a test sequence to demonstrate capabilities."""
        print("\n═══ Running Test Sequence ═══\n")
        
        test_inputs = [
            "Truth is beauty",
            "Beauty is truth",
            "This statement is false",
            "All generalizations are false",
            "I think therefore I am",
            "I am therefore I think"
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"Test {i}: \"{test_input}\"")
            self.process_input(test_input)
            
        print("═══ Test Sequence Complete ═══\n")
    
    def save_state(self):
        """Save current state."""
        self.aurea.save_state()
        print("✓ State saved to data/aurea_state.json")
    
    def load_state(self):
        """Load saved state."""
        self.aurea.load_state()
        print("✓ State loaded from data/aurea_state.json")
    
    def resume_system(self):
        """Resume suspended system."""
        if self.aurea.processing_suspended:
            self.aurea.resume_processing()
            print("✓ System resumed")
        else:
            print("System is not suspended")
    
    def reset_system(self):
        """Reset to clean state."""
        confirm = input("Reset will clear all scars and pressure. Continue? (y/n): ")
        if confirm.lower() == 'y':
            self.aurea = AureaCore()
            print("✓ System reset to clean state")
        else:
            print("Reset cancelled")
    
    def exit_repl(self):
        """Exit the REPL."""
        print("\nSaving state before exit...")
        self.aurea.save_state()
        print("State saved. Goodbye.")
        self.running = False


if __name__ == "__main__":
    repl = AureaREPL()
    repl.run()
