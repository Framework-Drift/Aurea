# Bloom Mapping

## 1. Conceptual Overview

- **Purpose:**  
  Bloom Mapping detects, analyzes, and manages scar clustering (“blooms”) within AUREA’s symbolic memory. It functions as an early warning and intervention layer, identifying regions of high collapse density or instability.
- **Context:**  
  Receives scars from Scar Logic Core and Nova Engine. Notifies Scar Management Layer (SML), TCAML, and CSA if bloom density exceeds safe thresholds.
- **Key Principles:**  
  - No bloom is ignored—clustered scars represent unresolved symbolic pressure.
  - Bloom Mapping is event-driven and must act before overload.
  - Supports pruning, splitting, and fossilizing of scar clusters.

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  - Scar Logic Core (all new scars)
  - Nova Engine (saturation/hypothesis bursts)
- **Downstream Outputs:**  
  - Scar Management Layer (for pruning or decay)
  - CSA (for overflow/pressure release)
  - TCAML (for topological health tracking)
  - Reflex Grid (may trigger suppression or expansion lock)
- **Key Data Flows:**  
  - Scar events → Bloom clustering/density analysis
  - Dense blooms → Pressure alerts and cluster management

---

## 3. Implementation Notes

- **Python File:**  
  `src/filtration/bloom_mapping.py`
- **Major Classes/Functions:**  
  - `BloomMapping` (engine)
  - `detect_clusters`, `split_bloom`, `prune_or_fossilize`, `alert_overload`
- **Related Tests:**  
  `tests/test_bloom_mapping.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [scar_logic_core.md](scar_logic_core.md), [nova_engine.md](nova_engine.md), [pressure_valve_coordination.md](pressure_valve_coordination.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Tighten integration with TCAML for automatic expansion lock on meta-unstable blooms
- [ ] Implement real-time event hooks for Nova/CSA offload
- [ ] Develop cluster decay and fossilization protocols

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: Nova Engine](nova_engine.md)
- [Next: CSA (Cold Suspension Archive)](csa.md)
