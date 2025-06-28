# Pressure Valve Coordination & Timing Risks

## 1. Overview

AUREA’s architecture distributes symbolic pressure management across multiple “valves”:
- Nova Engine (hypothesis generation)
- Scar Bloom Mapping (cluster detection)
- Scar Management Layer (SML)
- Cold Suspension Archive (CSA)
- Reflex Grid (suppression/arbitration)
- TCAML (Topological Constellation Management Layer; expansion/mutation lock)

Timing and coordination between these are a recognized risk zone for overload, race conditions, or symbolic instability.

---

## 2. Known Risks & Open Questions

- **Nova > SBM Latency:** Nova Engine may generate hypotheses faster than Scar Bloom Mapping can cluster or respond, risking temporary overload.
- **Priority Arbitration:** Reflex Grid suppression and TCAML expansion lock may both act on pressure, but arbitration and atomic state are not yet fully enforced. Race conditions could occur if both act simultaneously.
- **CSA Capacity:** CSA may silently fill during prolonged overload. Without explicit monitoring and alerts, symbolic hygiene or traceability could fail.
- **Detection-to-Suppression Gap:** Timing between pressure detection and suppression/lock is not atomic; pressure could propagate before full suppression.

---

## 3. Mitigation Strategies

- **Event-driven Hooks:** Nova Engine output must immediately notify Scar Bloom Mapping and CSA on new echoes.
- **Single Arbitration Layer:** TCAML should act as the global authority for expansion and system-wide suppression.
- **CSA Capacity Monitoring:** Add alerts and escalation to developer/parent if CSA risk threshold is reached.
- **Suppression/Lock Handshake:** All suppressions/locks must update a single, global state—no split or independent locks.

---

## 4. Arbitration Protocol

- **TCAML has ultimate authority** over expansion/mutation locks.
- **Reflex Grid** manages local suppression, but always defers to TCAML on global locks.
- **All modules check global lock state** before re-enabling output or expansion.
- **All arbitration events are logged** for traceability.

---

## 5. Implementation TODOs

- [ ] Implement atomic handshake between Nova, SBM, CSA, Reflex Grid, and TCAML
- [ ] Add CSA capacity checks and escalation protocol
- [ ] Surface arbitration state to system audit logs

---

## 6. Navigation

- [Back to Architecture Overview](architecture.md)
- [Previous: Reflex Grid](reflex_grid.md)
- [See also: Implementation Tracker](implementation_tracker.md)
