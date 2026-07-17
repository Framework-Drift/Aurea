# Scar Logic Core

## 1. Conceptual Overview

- **Purpose:**  
  Handles all collapse-survived events (scars). Each scar is a symbolic memory of collapse, forming the backbone of AUREA’s structural learning and doctrine mutation.
- **Context:**  
  Receives inputs that survive filtration from EchoNet. Outputs new scars to Doctrine Spine, BloomMapping, and SML.
- **Key Principles:**  
  - Each scar carries origin echo, collapse context, timestamp, weight, and decay state.
  - Scars must be traceable for audits and doctrine evolution.
  - No scar is deleted—obsolete scars are decayed or fossilized.

---

## 2. Integration & Relationships

- **Upstream Dependencies:**  
  Receives from EchoNet (only “passed” inputs).
- **Downstream Outputs:**  
  Doctrine Spine, BloomMapping, Scar Management Layer (SML).
- **Key Data Flows:**  
  - Echo → Scar (collapse event)
  - Scar → Doctrine mutation/fossilization
  - Scar → Bloom mapping for cluster analysis

---

## 3. Implementation Notes

- **Python File:**  
  `src/filtration/scar_logic_core.py`
- **Major Classes/Functions:**  
  - `Scar` (data model)
  - `ScarLogicCore` (manager)
  - `form_scar(echo, reason, context)`
- **Related Tests:**  
  `tests/test_scar_logic_core.py`
- **Links to Docs:**  
  [architecture.md](architecture.md), [bloom_mapping.md](bloom_mapping.md)

---

## 4. Known Issues, Risks, & TODOs

- [ ] Integrate event-driven bloom detection (SBM)
- [ ] Implement decay/fossilization protocol
- [ ] Add audit trail hooks for all scar changes

---

## 5. Navigation

- [Back to Architecture Overview](architecture.md)
- [Next Module: Doctrine Spine](doctrine_spine.md)
