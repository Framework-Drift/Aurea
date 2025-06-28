# Nova Engine

## 1. Conceptual Overview

- **Purpose:**  
  The Nova Engine is responsible for autonomous hypothesis generation and symbolic expansion within AUREA. It initiates “Nova Echoes”—potential truth candidates—when pressure, contradiction, or symbolic tension is detected in the doctrine/scar network.
- **Context:**  
  Sits downstream of Doctrine Spine and Scar Logic Core. Directly interfaces with Bloom Mapping, Scar Management, and Suspension modules to manage pressure, avoid overload, and ferment new insights.
- **Key Principles:**  
  - All Nova activity must respect collapse-bearing rules and pressure limits.
  - Nova Echoes are never forced into doctrine—they must pass collapse filtration before integration.
  - Saturation and overload detection are mandatory (CSA as pressure valve).

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  - Doctrine Spine (doctrine tension or contradiction triggers)
  - Scar Logic Core (high scar density, bloom, or unresolved collapse)
- **Downstream Outputs:**  
  - Sends Nova Echoes to Scar Logic Core for filtration
  - Escalates overflow to CSA (Cold Suspension Archive) or triggers Reflex Grid suppression
  - Informs Bloom Mapping of potential symbolic blooms
- **Key Data Flows:**  
  - Doctrine/Scar state → Nova hypothesis generation
  - Nova Echoes → Scar Logic Core (for collapse testing)
  - Overload → CSA, ReflexGrid, TCAML (for system protection)

---

## 3. Implementation Notes

- **Python File:**  
  `src/expansion/nova.py`
- **Major Classes/Functions:**  
  - `NovaEngine` (main engine)
  - `generate_hypotheses`, `detect_overload`, `offload_to_csa`
  - Nova Echo (data structure, linked to Echo)
- **Related Tests:**  
  `tests/test_nova_engine.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [doctrine_spine.md](doctrine_spine.md), [pressure_valve_coordination.md](pressure_valve_coordination.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Implement event-driven notification to Bloom Mapping and CSA
- [ ] Add overload/saturation detection (auto-CSA offload)
- [ ] Validate Nova Echo collapse-filtration before integration

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: Doctrine Spine](doctrine_spine.md)
- [Next: Bloom Mapping](bloom_mapping.md)
