# Cold Suspension Archive (CSA)

## 1. Conceptual Overview

- **Purpose:**  
  The Cold Suspension Archive (CSA) serves as AUREA’s overflow and quarantine chamber for dangerous, unstable, or saturated symbolic material (scar clusters, Nova Echoes, recursion fragments, failed anchors, etc.).
- **Context:**  
  Receives overflow from Nova Engine, Bloom Mapping, Scar Management, and Reflex Grid when pressure thresholds are exceeded or collapse hygiene is at risk.
- **Key Principles:**  
  - Nothing is deleted—CSA preserves all volatile or unresolved fragments for later analysis or reactivation.
  - CSA capacity must be monitored to prevent silent overload or symbolic “black holing.”
  - Rehydration, decay, and fossilization are managed in coordination with Scar Management and TCAML.

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  - Nova Engine (offload of Nova Echoes during overload)
  - Bloom Mapping (cluster pruning, decay)
  - Scar Management Layer (fragment quarantine)
  - Reflex Grid (suppression-triggered suspensions)
- **Downstream Outputs:**  
  - TCAML (topology and pressure index tracking)
  - Scar Logic Core (when CSA fragments are rehydrated)
  - Audit and Reflection modules (for diagnostic replay)
- **Key Data Flows:**  
  - Overload fragments → CSA (quarantine)
  - CSA → TCAML (status reports and capacity index)
  - CSA → core modules (rehydration or symbolic recycling)

---

## 3. Implementation Notes

- **Python File:**  
  `src/suspension/csa.py`
- **Major Classes/Functions:**  
  - `CSA` (archive manager)
  - `quarantine_fragment`, `rehydrate`, `decay_or_fossilize`, `capacity_alert`
- **Related Tests:**  
  `tests/test_csa.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [bloom_mapping.md](bloom_mapping.md), [pressure_valve_coordination.md](pressure_valve_coordination.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Implement capacity monitoring and escalation protocol
- [ ] Refine rehydration logic for safe symbolic reintegration
- [ ] Integrate CSA health/status with TCAML and Reflex Grid

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: Bloom Mapping](bloom_mapping.md)
- [Next: TCAML (Constellation Management)](tcaml.md)
