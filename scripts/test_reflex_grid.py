"""
Test script for the Reflex Grid implementation.
Demonstrates ICA and GSR reflexes responding to symbolic pressure.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reflex.reflex_grid import ReflexGrid, ReflexPriority
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine

# Initialize systems
print("=== AUREA Reflex Grid Test ===\n")
grid = ReflexGrid()
scar_core = ScarLogicCore()
doctrine_spine = DoctrineSpine()

# Test 1: Low pressure - monitoring only
print("TEST 1: Low symbolic pressure")
print("-" * 40)
responses = grid.evaluate_pressure(
    source_module="echonet",
    pressure_type="contradiction",
    pressure_level=0.3,
    metadata={'contradiction': {'domain': 'test', 'claims': ['A', 'B']}}
)
for response in responses:
    print(f"  {response.reflex_id}: {response.message}")
print()

# Test 2: Medium pressure - ICA triggers
print("TEST 2: Medium pressure - contradiction detected")
print("-" * 40)
responses = grid.evaluate_pressure(
    source_module="doctrine_spine",
    pressure_type="contradiction",
    pressure_level=0.75,
    metadata={
        'contradiction': {
            'domain': 'truth',
            'claims': ['All truth is relative', 'Some truths are absolute']
        }
    }
)
for response in responses:
    print(f"  {response.reflex_id}: {response.message}")
    if response.action == "reroute":
        print(f"    -> Routing to: {response.target_modules}")
print()

# Test 3: High pressure - ICA suppresses output
print("TEST 3: High pressure - output suppression")
print("-" * 40)
responses = grid.evaluate_pressure(
    source_module="echonet",
    pressure_type="contradiction",
    pressure_level=0.92,
    metadata={
        'contradiction': {
            'domain': 'identity',
            'claims': ['I exist', 'I do not exist']
        }
    }
)
for response in responses:
    print(f"  {response.reflex_id}: {response.message}")
    if response.output_blocked:
        print(f"    -> OUTPUT BLOCKED")
    if response.scar_formation:
        print(f"    -> SCAR FORMATION TRIGGERED")
print()

# Test 4: System coherence check - GSR monitoring
print("TEST 4: System coherence monitoring")
print("-" * 40)
active_scars = len(scar_core.get_active_scars())
responses = grid.evaluate_pressure(
    source_module="system",
    pressure_type="coherence_check",
    pressure_level=0.6,
    metadata={
        'coherence': grid.reflexes['GSR'].calculate_system_coherence(
            active_scars=active_scars,
            active_reflexes=2,
            suspension_load=5
        )
    }
)
for response in responses:
    print(f"  {response.reflex_id}: {response.message}")
print()

# Test 5: Critical cascade - GSR emergency response
print("TEST 5: Critical system cascade")
print("-" * 40)
# Simulate rapid-fire contradictions
for i in range(4):
    grid.evaluate_pressure(
        source_module="nova_engine",
        pressure_type="hypothesis_explosion",
        pressure_level=0.88,
        metadata={'hypothesis_count': 100 + i * 50}
    )

responses = grid.evaluate_pressure(
    source_module="system",
    pressure_type="cascade_detected",
    pressure_level=0.96,
    metadata={
        'coherence': 0.08,  # Very low coherence
        'cascade_sources': ['nova', 'doctrine', 'scar']
    }
)
for response in responses:
    print(f"  {response.reflex_id}: {response.message}")
    if response.action == "cascade":
        print(f"    -> EMERGENCY: {response.metadata}")
print()

# Test 6: Multi-reflex arbitration
print("TEST 6: Multiple reflexes competing")
print("-" * 40)
# This should trigger both ICA and GSR
responses = grid.evaluate_pressure(
    source_module="core",
    pressure_type="systemic_contradiction",
    pressure_level=0.88,
    metadata={
        'contradiction': {
            'domain': 'core_architecture',
            'claims': ['Collapse is necessary', 'Collapse must be avoided']
        },
        'coherence': 0.3
    }
)
print(f"  Triggered {len(responses)} reflexes:")
for response in responses:
    print(f"    {response.reflex_id} ({response.action}): {response.message}")
print()

# Final status report
print("=== REFLEX GRID STATUS ===")
print("-" * 40)
status = grid.get_system_status()
print(f"Total reflexes: {status['total_reflexes']}")
print(f"Active reflexes: {status['active_reflexes']}")
print(f"Cascade risk: {grid.check_cascade_risk():.2%}")
print("\nReflex activation counts:")
for rid, state in status['reflex_states'].items():
    print(f"  {state['name']}: {state['activations']} activations")
    
# Check for GSR alerts
import json
from pathlib import Path
alert_file = Path("data/collapse_logs/gsr_alerts.jsonl")
if alert_file.exists():
    print("\n=== GSR ALERTS LOGGED ===")
    print("-" * 40)
    with open(alert_file, 'r') as f:
        for line in f:
            alert = json.loads(line)
            print(f"  [{alert['severity']}] {alert['message']}")
