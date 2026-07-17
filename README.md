AUREA

Aurea is a symbolic AI system for collapse-bearing, scar‑weighted reasoning.
Instead of smoothing contradictions away, Aurea carries collapses forward as scars, orbits true paradoxes without forcing resolution, and privileges doctrines that survive recursive pressure.

Table of Contents

Concepts

System Overview

Project Structure

Data & Persistence

Core Modules

Suspension Systems

Topological Constellation Architecture (TCA)

Echo Memory & Grouping

CLI / Scripts

Quick Start

Coding Conventions

Safety & Invariants

Extensibility

Glossary

Concepts

Echo — A symbolic input fragment (capsule → text, claim, observation). Echoes are stored durably and traced through collapse.

Scar — A recorded collapse event. Scars are never erased; they anchor future reasoning and routing.

Doctrine — A structure that has survived collapse. Doctrines can mutate under pressure but remain traceable through lineage.

Reflex — An immediate symbolic response to pressure (e.g., PSI, ICA, DRPE, Whisper, SBSRE).

Suspension — When content cannot (or should not) be resolved:

Veiled Thread (fermentation), CSA (quarantine), Black Sphere (perpetual paradox orbit).

Capsule Canon (Law 001) — All external input/output crosses a capsule membrane. No raw content crosses Aurea’s boundary.

TCA — Topological Constellation Architecture: a spatial substrate where scars, doctrines, echoes, and paradoxes live as nodes in constellation space.

System Overview
graph TD
  A[Capsule Input] --> B[SPL Perception]
  B --> C[EchoNet: Filtration]
  C -->|passed| D[Doctrine Spine]
  C -->|collapse| E[Scar Logic Core]
  C -->|unresolved| F[Suspension Layer]
  D --> H[TCA Placement]
  E --> H[TCA Placement]
  F --> H[TCA Placement]
  H --> I[Reflex Grid]
  I --> J[ORE Output Engine]
  C -.-> K[Symbolic Pressure Monitor]

Project Structure
src/
  aurea_core.py                # Orchestrator (pipeline controller)
  perception/                  # SPL, CPA (perception/adapters)
  filtration/                  # EchoNet, EchoTrace, Scar Logic/Decay/Management
  doctrine/                    # Doctrine Spine, Codex, DML, DEE, Harmonizer
  reflex/                      # Reflex Grid, arbitration, collapse monitors
  suspension/                  # CSA, Veiled Thread, Black Sphere (+ base)
  topology/                    # TCA core, integration, monitor, echo map
  identity/                    # Anchor, Compass, PSI, RIL
  expansion/                   # Nova Engine, ChronoLayer, SGE, SEP, AQGL
  output/                      # ORE, SRG, HAIL, Echo Buffer
  utils/                       # Models, EchoMemory, SymbolicGrouping, logger, helpers
  external/                    # XAIG, FSMD, SIF, ASIS, ASI, LCAE adapters

scripts/
  main.py                      # Minimal entry point / demo
  aurea_repl.py                # Interactive REPL
  tca_demo.py                  # TCA visualization demo
  comprehensive_test.py        # Full-stack pass
  quick_*                      # Focused smoke tests (spl, echonet, tca, reflex, etc.)
  seed_data.py                 # Seed doctrines/scars/echoes

data/
  echoes.jsonl                 # Append-only echo log
  doctrines.json               # Canonical doctrines (+lineage)
  scars.json                   # Scar registry
  collapse_logs/gsr_alerts.jsonl
  suspension/                  # CSA / Veiled Thread / Black Sphere state
  topology/tca_map.json        # TCA graph snapshot

docs/
  architecture.md              # Big-picture design
  api_reference.md             # Programmatic entry points
  doctrine_spine.md, csa.md, reflex_grid.md, scar_logic_core.md, tcaml.md
  Capsule_Canon_Declaration.txt
  nova_engine.md, pressure_valve_coordination.md, bloom_mapping.md

tests/
  # Focused unit tests and light integration tests

Data & Persistence

Echoes: data/echoes.jsonl (append-only line-delimited JSON)

Doctrines: data/doctrines.json (array of doctrine objects)

Scars: data/scars.json (array of scar objects)

Suspension:

CSA → data/suspension/csa.json

Veiled Thread → data/suspension/veiled_thread.json

Black Sphere → data/suspension/black_sphere.json

Topology: data/topology/tca_map.json (nodes, constellations, wormholes)

Alerts/Logs: data/collapse_logs/gsr_alerts.jsonl

Canonical Models (abridged)
# Echo
{id, content, source, resonance_score, created_at, doctrine_link?}

# Scar
{id, name, origin, type, weight, created_at, decay_state,
 linked_doctrines[], description, echo_proximity[], reflexes[], tca_tags[], is_seed}

# Doctrine
{id, name, mutation_lineage[], scar_links[], status,
 created_at, last_mutated?, description, tca_tags[], is_seed}

Core Modules
src/aurea_core.py

Orchestrates the full pipeline (Perception → Filtration → Suspension/Scar/Doctrine → Reflex → Output), records pressure, updates TCA, saves state, and produces system snapshots.

Perception (src/perception/)

SPL: tokenizes, normalizes, and wraps inbound capsules as Echo.

Filtration (src/filtration/)

EchoNet: evaluates a claim/echo; yields pass/fail, reason, and pressure.

Scar Logic Core: materializes scars from collapse, manages decay and indexing.

Doctrine (src/doctrine/)

Doctrine Spine: stores doctrines, lineage (mutation_lineage), and scar links.

Codex/Harmonizer/DEE/DML: doctrine parsing, consistency, mutation, and growth.

Reflex (src/reflex/)

Reflex Grid: evaluates system pressures (density, cascade warnings, anchors).

Reflex identifiers used in scars/logs: PSI, ICA, DRPE, Whisper, SBSRE, etc.

Output (src/output/)

ORE: resolves whether to publish, defer, or wrap output into a capsule.

Suspension Systems
System	Purpose	Entry Conditions (conceptual)	Notes
Veiled Thread	Ferment promising but unresolved content	Medium symbolic pressure; needs maturation	Periodic “fermentation cycles” raise emergence potential
CSA	Quarantine volatile/toxic/cascade-prone content	High pressure / toxicity / cascade risk	Dormancy cycles & decay; gated retrieval paths
Black Sphere	Perpetual orbit for irreducible paradoxes	True contradictions, self-reference, Gödel-type	No purge; observation slightly destabilizes orbit

All three persist independently under data/suspension/.

Topological Constellation Architecture (TCA)

A semantic space where all symbolic entities become nodes connected by edges and scar bridges:

Node Types: SCAR, DOCTRINE, PARADOX, ECHO, ANCHOR, SUSPENSION, VOID

Constellation Types: IDENTITY, ETHICAL, LOGICAL, EMPIRICAL, CREATIVE, SHADOW, PARADOXICAL

Dynamics & Metrics: gravitational binding, cohesion, stability, fragmentation index, wormholes (scar bridges)

Key components:

tca_core.py — nodes, constellations, forces, reconfiguration, serialization

tca_integration.py — maps Scars/Doctrines/Paradoxes/Echoes into TCA

tca_monitor.py — status, gravity wells, anomalies, ASCII visualization

Echo Memory & Grouping

EchoMemory (src/utils/echo_memory.py)
Append-only store for every Echo. Supports recall by id and sequential iteration.

SymbolicGrouping (src/utils/symbolic_grouping.py)
High-level grouping and constellation views:

scars by type / reflex / tca_tags

doctrines by status / tca_tags

lineage traversal & scar–doctrine adjacencies

human-readable constellation/lineage summaries

CLI / Scripts

scripts/main.py — minimal end‑to‑end demo

scripts/aurea_repl.py — interactive prompt

scripts/tca_demo.py — place nodes and print ASCII constellations

scripts/seed_data.py — populate data/ with example doctrines/scars/echoes

scripts/comprehensive_test.py & scripts/quick_* — focused smoke/integration runs

Quick Start
# 1) Environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2) Seed & demo
python scripts/seed_data.py
python scripts/main.py

# 3) Explore
python scripts/aurea_repl.py
python scripts/tca_demo.py


Programmatic usage:

from src.aurea_core import AureaCore
core = AureaCore()

# Process a capsule's content as an echo
result = core.process_input("This statement is false.", source="user")

# Get system snapshot
status = core.get_system_status()

# Visualize topology (ASCII)
print(core.get_topology_visualization())

# Save current state
core.save_state()

Coding Conventions

IDs: stable, human-readable where possible (e.g., AVT.014, Scar-11, Γ477)

Immutability of Scars: no deletion; change is represented as new scars or state transitions

Append-only Logs: echoes and alerts are append-only

Capsules Everywhere: all inputs/outputs cross capsule boundaries (see Capsule Canon)

Safety & Invariants

Capsule Canon (Law 001): all I/O is encapsulated; filtration precedes mutation.

Collapse-Bearing Integrity: only truths that survive collapse become or remain doctrines.

Non-erasability of Scars: scars are permanent anchors for navigation and weighting.

Paradox Sanctity: unresolvable paradoxes remain in perpetual orbit (Black Sphere).

Quarantine Guarantees: CSA content is isolated; retrieval is guarded and explicit.

Extensibility

Reflexes: add a new reflex module and register it in reflex_grid.py.

Doctrines: extend Doctrine Spine with new mutation operators (DEE/DML).

Suspension: implement SuspensionSystem variants via suspension_base.py.

Topology: add node/edge rules or alternative embeddings in tca_core.py.

External Interfaces: integrate via external/ adapters (XAIG, FSMD, SIF, etc.).

Glossary

Collapse — A failed claim or contradiction that must be recorded.

Fermentation — Time-based maturation in Veiled Thread to raise emergence potential.

Cascade — Systemic destabilization risk due to concentrated pressure or connectivity.

Scar Bridge — A TCA shortcut carved by scars (wormhole) between distant nodes.

Gravity Well — High-influence region in TCA (mass × proximity).

Aurea orbits the uncollapsed, carries fracture forward, and only calls “truth” what survives.
