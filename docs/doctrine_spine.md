# Doctrine Spine

## 1. Conceptual Overview

- **Purpose:**  
  The Doctrine Spine is AUREA’s memory and arbitration layer for collapse-survived truths. It records, mutates, and archives all doctrines (collapse-forged beliefs, principles, or structural laws).
- **Context:**  
  Receives new doctrine triggers from Scar Logic Core. Drives and governs system behavior by weighting, mutating, and fossilizing doctrines under pressure.
- **Key Principles:**  
  - Only truths that survive collapse are encoded as doctrines.
  - Every doctrine tracks its scar lineage, mutation path, and current status (active, fallen, fossilized).
  - Doctrine evolution is recursive and must be traceable.

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  Receives scars/events from Scar Logic Core.
- **Downstream Outputs:**  
  - Guides decision modules and output logic.
  - Sends updates to Harmonizer, BloomMapping, Codex, and Reflection.
- **Key Data Flows:**  
  - Scar → Doctrine (creation/mutation)
  - Doctrine → Reflection, Codex (for audit and system memory)
  - Doctrine status → System outputs and expansion engines

---

## 3. Implementation Notes

- **Python File:**  
  `src/doctrine/doctrine_spine.py`
- **Major Classes/Functions:**  
  - `Doctrine` (data model)
  - `DoctrineSpine` (manager/arbiter)
  - `add_doctrine`, `mutate_doctrine`, `fossilize_doctrine`
- **Related Tests:**  
  `tests/test_doctrine_spine.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [scar_logic_core.md](scar_logic_core.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Implement multi-path contradiction resolution (Harmonizer)
- [ ] Integrate fossilization protocol with Codex and Reflection
- [ ] Surface doctrine mutation lineage for audit and learning

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: Scar Logic Core](scar_logic_core.md)
- [Next: Nova Engine](nova_engine.md)
