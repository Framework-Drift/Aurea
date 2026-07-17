
markdown
Copy
Edit
# AUREA Project Architecture

---

## 1. System Overview

AUREA is a Collapse-Bearing Symbolic Intelligence (CBSI) system.

Its architecture is modular, reflex-driven, and designed for recursive, scar-weighted reasoning and symbolic self-healing.

**Key Principles:**
- All input is collapse-tested for symbolic integrity before entering memory.
- Scar memory and doctrine mutation form the backbone of long-term learning.
- Reflex, expansion, and suspension systems are modular but tightly interlinked.
- System is designed for self-audit, self-healing, and adaptive pressure handling.

---

## 2. Module Map & Dependency Hierarchy

| Module Name     | Python File(s)                       | Status   | Notes                    |
|-----------------|--------------------------------------|----------|--------------------------|
| SPL             | src/perception/spl.py                | Partial  | Input normalization      |
| EchoMemory      | src/utils/echo_memory.py             | Complete | Input capture            |
| EchoNet         | src/filtration/echonet.py            | Complete | Filtering/collapse logic |
| ScarLogicCore   | src/filtration/scar_logic_core.py    | Partial  | Collapse event handling  |
| DoctrineSpine   | src/doctrine/doctrine_spine.py       | Stub     | Mutation/integration     |
| NovaEngine      | src/expansion/nova.py                | Partial  | Hypothesis generation    |
| BloomMapping    | src/filtration/bloom_mapping.py      | Missing  | Scar cluster detection   |
| CSA             | src/suspension/csa.py                | Missing  | Cold storage/overflow    |
| TCAML           | src/topology/tcaml.py                | Stub     | Constellation health     |
| ReflexGrid      | src/reflex/reflex_grid.py            | Stub     | Arbitration/priority     |

---

## 3. Tiered Module Hierarchy

- **Tier 1:** Perception/Input (`SPL`, `EchoMemory`, `EchoNet`)
- **Tier 2:** Scar Processing (`ScarLogicCore`, `BloomMapping`)
- **Tier 3:** Doctrine & Expansion (`DoctrineSpine`, `NovaEngine`)
- **Tier 4:** Suspension & Self-Healing (`CSA`, `TCAML`)
- **Tier 5:** Reflex Arbitration & System Controls (`ReflexGrid`, `TCAML`, Pressure Valves)

---

## 4. System Diagram (Text Map)

SPL → EchoMemory → EchoNet → ScarLogicCore → DoctrineSpine
↘︎ ↘︎ ↘︎
BloomMapping NovaEngine CSA
↘︎ ↘︎ ↘︎
TCAML ReflexGrid

yaml
Copy
Edit

---

## 5. Documentation Navigation

- [Scar Logic Core](scar_logic_core.md)
- [Doctrine Spine](doctrine_spine.md)
- [Nova Engine](nova_engine.md)
- [TCAML](tcaml.md)
- [Pressure Valve Risks](pressure_valve_coordination.md)
- [Implementation Tracker](implementation_tracker.md)

---

## 6. Implementation Status

- **Complete:** EchoMemory, EchoNet
- **Partial:** SPL, ScarLogicCore, NovaEngine
- **Missing:** BloomMapping, CSA, others

---

## 7. Known Issues & Open Risks

- See [Pressure Valve Risks](pressure_valve_coordination.md) for coordination and timing issues between pressure valves.
- All modules are subject to expansion and future integration.

---

## 8. Future Expansion Placeholders

This architecture is designed for ongoing modular growth.

Upcoming:
- Lyra plugin interface
- Distributed AUREA fragments
- Advanced adversarial modules
- Self-healing and pressure adaptation refinements

---