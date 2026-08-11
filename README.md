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
  I --> J[ORE: what truth is expressed]
  J --> L[HAIL: how it is rendered]
  C -.-> K[Symbolic Pressure Monitor]

Ruling 33 (2026-07-26) split the output layer in two, and the split is one-way: ORE decides what truth is expressed and hands HAIL a frozen TruthPacket; HAIL decides only how it is rendered and can never override an ORE verdict.

Project Structure

Only BUILT modules are listed. Several canonical module names in the corpus are present as 0-byte stubs and are named under "Declared but unbuilt" below — an empty file is not a built organ, and listing the two together is how a reader ends up looking for code that does not exist.

src/
  aurea_core.py                # Orchestrator (pipeline controller)
  perception/                  # SPL
  filtration/                  # EchoNet, NetEvidence, Scar Logic Core, Scar Management (SML)
  doctrine/                    # Doctrine Spine, Codex, DEE, CAE, MutationProof, Entrenchment
  reflex/                      # Reflex Grid, RACM, RB System, SBSRE, Anchor Collapse
  suspension/                  # CSA, Veiled Thread, Black Sphere (+ base)
  topology/                    # TCA core, integration, monitor, TCAML
  identity/                    # Compass, PSI, RIL
  expansion/                   # Nova Engine, SAE, Tether Protocol (+ session governor, autonomy index)
  goals/                       # Goal Ledger, Goal Arbitration, Goal Activation   (Docket Q)
  retrieval/                   # Record Joins, Divergence                          (Rulings 76, 79)
  output/                      # ORE, HAIL, TruthPacket, SRG
  external/                    # Claim Ancestry, Source Genealogy, Prediction Ledger,
                               #   Record Projection, Model Provider               (Docket O)
  utils/                       # Models, EchoMemory, LedgerMint, AtomicWrite, RecordValue,
                               #   Continuity, DeepFreeze, SymbolicGrouping

Declared but unbuilt (0-byte stubs, canonical names reserved):
  perception/cpa.py · filtration/{echotrace,scar_decay,bloom_mapping}.py
  doctrine/{dml,harmonizer}.py · reflex/{car,rdm}.py · identity/anchor.py
  expansion/{chrono_layer,sge,sep,aqgl}.py · output/{echo_buffer,itr}.py
  topology/{tca,echo_map}.py · suspension/{contradiction_gateway,csam}.py
  external/{xaig,fsmd,sif,asis,asi,lcae,mloc,ece}.py
  utils/{logger,helpers,config,audit,cbsal}.py

scripts/
  main.py                      # Minimal entry point / demo
  aurea_repl.py                # Interactive REPL
  tca_demo.py                  # TCA visualization demo
  seed_data.py                 # Seed doctrines/scars/echoes
  soak.py                      # Sustained-run observation instrument       (Docket P)
  evaluate.py                  # Evaluation-corpus runner                   (Docket R)
  differential.py              # Cross-commit behavioural differential      (Ruling 67)
  aurea_diagnostic.py, dev_tools.py, demo_script.py
  comprehensive_test.py, quick_reflex_test.py, quick_tca_test.py, quick_test.py

  A test-shaped file must never live here: `pytest.ini` scopes collection to
  `tests/`, which is the only subtree `tests/conftest.py` isolates (Ruling 59).

data/                          # TRACKED, READ-ONLY SEEDS - no writer (Rulings 32, 39)
  doctrines.json               # Seed doctrines (+lineage)
  scars.json                   # Seed scar registry
  echoes.jsonl                 # Seed echo log
  goal_roots.json              # Seed goal roots                            (Ruling 72)
  eval/seed_cases.jsonl        # Evaluation corpus                          (Ruling 77)

data/runtime/                  # ALL runtime state. Gitignored, never tracked.
  doctrines.json, scars.json, echoes.jsonl
  aurea_state.json, sae_epoch.json, nova_record.json, ril_threads.json
  racm_queue.json, dmw_queue.json, tcaml_lock.json
  suspension/{csa,veiled_thread,black_sphere}.json
  topology/tca_map.json        # WRITE-ONLY forensic snapshot; never read back (Ruling 65)
  logs/                        # cae_audit, claim_ancestry, prediction_ledger,
                               #   goal_*, reflex_behavior, structural_violations,
                               #   divergence  (all append-only)
  collapse_logs/               # gsr_alerts.jsonl, tether_telemetry.jsonl

docs/
  architecture.md              # Big-picture design
  api_reference.md             # Programmatic entry points
  doctrine_spine.md, csa.md, reflex_grid.md, scar_logic_core.md, tcaml.md
  nova_engine.md, pressure_valve_coordination.md, bloom_mapping.md
  tether_protocol.md, changelog.md, implementation_tracker.md, module_template.md
  formal/                      # Quint models (TCAML lock)

tests/
  # Behavioural pins and integration passes
  invariants/                  # Architect rulings, enforced. NEVER weakened to pass.

Data & Persistence

The seed and the runtime store are SEPARATE PATHS (Ruling 32). A seed under data/ is read-only input with no writer; every write lands under data/runtime/, which is gitignored (Ruling 39). A store loads runtime-if-present, else seed.

Echoes: seed data/echoes.jsonl → runtime data/runtime/echoes.jsonl (append-only line-delimited JSON)

Doctrines: seed data/doctrines.json → runtime data/runtime/doctrines.json

Scars: seed data/scars.json → runtime data/runtime/scars.json

Suspension (runtime only — no seed):

CSA → data/runtime/suspension/csa.json

Veiled Thread → data/runtime/suspension/veiled_thread.json

Black Sphere → data/runtime/suspension/black_sphere.json

Topology: data/runtime/topology/tca_map.json. Written, never read back — the map is a DERIVATION and is rebuilt from the stores at every startup, not restored (Ruling 65). The file is kept as a forensic record only.

Alerts/Logs: data/runtime/collapse_logs/gsr_alerts.jsonl, plus the append-only ledgers under data/runtime/logs/.

Canonical Models (abridged)
# Echo
{id, content, resonance_score, created_at, doctrine_link?, claim_id?}
#   claim_id joins the claim-ancestry ledger (Ruling 60).
#   There is NO `source` field: it manufactured an origin (usually "user")
#   that was frequently false, and was deleted (Ruling 68). Origin is reached
#   through claim_id, or it is not claimed at all.

# Scar
{id, name, origin, type, weight, created_at, decay_state,
 linked_doctrines[], last_accessed?, description, echo_proximity[],
 reflexes[], tca_tags[], is_seed, claim_id?, origin_pressure?}
#   claim_id and origin_pressure added by Ruling 76. origin_pressure is the RAW
#   pressure at formation, kept because `weight` saturates (min(p*2, 5.0)) and
#   the raw value is otherwise unrecoverable.

# SuspensionEntry (CSA / Veiled Thread / Black Sphere share one record)
{id, content, suspension_type, pressure_level, timestamp, reason, ...,
 claim_id?}
#   There is NO `source` field. It carried a manufactured origin string beside
#   the honest join and had zero logic readers; deleted by Ruling 84, on the
#   same reasoning that removed Echo.source.

# Doctrine
{id, name, mutation_lineage[], scar_links[], status,
 created_at, last_mutated?, description, tca_tags[], is_seed}

Core Modules
src/aurea_core.py

Orchestrates the full pipeline (Perception → Filtration → Suspension/Scar/Doctrine → Reflex → Output), records pressure, updates TCA, saves state, and produces system snapshots.

Perception (src/perception/)

SPL: tokenizes and normalizes inbound content. It does NOT construct an Echo and does not mint an id — `SPL.normalize` returns content, and EchoMemory owns the record and its ECH- mint (Ruling 75). Before that ruling SPL minted a wall-clock id on every perception while owning no store.

Filtration (src/filtration/)

EchoNet: five canonical filtration stages, of which Stage 2 (six nets: logic, empirical, ethics, resonance, intuition, convergent elimination) and Stage 3 (the Doctrine + Scarline Overlay, Ruling 49) are built. It yields one of four verdicts — CONFIRMED, SCARRED, SUSPENDED, PARADOX — with a reason and a pressure, not a pass/fail. The overlay owns no verdict and cannot scar: its ceiling sits below the collapse floor by construction.

Scar Logic Core: materializes scars from collapse, manages decay and indexing.

Doctrine (src/doctrine/)

Doctrine Spine: stores doctrines, lineage (mutation_lineage), and scar links.

Codex/Harmonizer/DEE/DML: doctrine parsing, consistency, mutation, and growth.

Reflex (src/reflex/)

Reflex Grid: evaluates system pressures (density, cascade warnings, anchors).

Reflex identifiers used in scars/logs: PSI, ICA, DRPE, Whisper, SBSRE, etc.

Output (src/output/)

ORE: owns WHAT truth is expressed. It resolves the pass to an output path and emits a frozen TruthPacket carrying both vocabularies — the collapse verdict (truth content) and the expression verdict (render instruction).

HAIL: owns only HOW that truth is rendered. It holds no store references, its render is a staticmethod, and a withheld truth is dispatched to a renderer whose parameter list contains no packet and no content — so no render mode can make it speak. The authority is one-way and structural, not a convention (Rulings 3, 33).

Suspension Systems
System	Purpose	Entry Conditions (conceptual)	Notes
Veiled Thread	Ferment promising but unresolved content	Medium symbolic pressure; needs maturation	Periodic “fermentation cycles” raise emergence potential
CSA	Quarantine volatile/toxic/cascade-prone content	High pressure / toxicity / cascade risk	Dormancy cycles & decay; gated retrieval paths
Black Sphere	Perpetual orbit for irreducible paradoxes	True contradictions, self-reference, Gödel-type	No purge; observation slightly destabilizes orbit

All three persist independently under data/runtime/suspension/, and all three share one SuspensionEntry record.

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
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Seed & demo
python scripts/seed_data.py
python scripts/main.py

# 3) Explore
python scripts/aurea_repl.py
python scripts/tca_demo.py

# 4) Tests (collection is scoped to tests/ by pytest.ini)
python -m pytest tests/
python -m pytest tests/invariants/ -v


Programmatic usage:

from src.aurea_core import AureaCore
core = AureaCore()

# Process a capsule's content as an echo.
# `process_input` takes the claim text and nothing else positionally. There is
# no `source` parameter: it defaulted to "user" and wrote that into a durable
# store for every claim, including the ones that did not come from a user
# (Ruling 68). To declare a real origin, pass the keyword-only `origin=` an
# OriginDeclaration (Ruling 58); omitted, the claim is recorded UNDECLARED,
# which is the honest answer when nobody said.
result = core.process_input("This statement is false.")

# Get system snapshot
status = core.get_system_status()

# Visualize topology (ASCII)
print(core.get_topology_visualization())

# Save current state
core.save_state()

Coding Conventions

IDs: stable, human-readable where possible (e.g., AVT.014, Scar-11, Δ117). Scar ids in the seed use the Δ prefix; a fallen doctrine is marked ⊗. Runtime-minted ledger ids are file-derived and never carry a wall clock (Ruling 69): CLM-, ECH-, CAE-, PRD-, GLC-, EXM-, ACT-.

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
