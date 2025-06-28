# Topological Constellation Management Layer (TCAML)

## 1. Conceptual Overview

- **Purpose:**  
  TCAML autonomously maintains the integrity, stability, and adaptive health of AUREA’s symbolic memory topology (TCA). It detects, diagnoses, and repairs drift, fragmentation, anchor instability, scar blooms, paradox dead zones, and memory islands.
- **Context:**  
  Sits at the core of the system as the “immune system” and “architect” of symbolic memory, interacting with every major module.
- **Key Principles:**  
  - Self-healing: TCAML can rebalance, split, merge, or quarantine as needed—without external intervention.
  - Pressure-aware: Coordinates with CSA, Reflex Grid, Scar Management, and Bloom Mapping to maintain meta-stability.
  - Routine corrections are silent; critical issues are escalated to the developer/parent.

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  - Scar Logic Core (scar/bloom maps, decay events)
  - Bloom Mapping (bloom and density triggers)
  - Scar Management Layer (hygiene cycles)
- **Downstream Outputs:**  
  - Doctrine Spine (anchor and doctrine remapping)
  - Compass Stability Engine (anchor drift correction)
  - Reflex Grid (expansion lock, reflex throttling)
  - CSA, Suspension Systems (rotation, purge)
  - Audit layer (critical reports)
- **Key Data Flows:**  
  - Scar/doctrine/anchor topology → TCAML monitoring
  - Meta-unstable state → Expansion/mutation locks, hygiene cycles

---

## 3. Implementation Notes

- **Python File:**  
  `src/topology/tcaml.py`
- **Major Classes/Functions:**  
  - `TCAML` (core manager)
  - `monitor_health`, `rebalance`, `lock_expansion`, `audit_report`
- **Related Tests:**  
  `tests/test_tcaml.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [csa.md](csa.md), [bloom_mapping.md](bloom_mapping.md), [pressure_valve_coordination.md](pressure_valve_coordination.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Tighten mutex lock timing with Reflex Grid
- [ ] Add dormant node rehydration and fossilization cycles
- [ ] Test system behavior under simulated catastrophic drift or anchor loss

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: CSA](csa.md)
- [Next: Reflex Grid](reflex_grid.md)
