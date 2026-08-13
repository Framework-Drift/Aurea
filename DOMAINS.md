# DOMAINS.md — where the work lives

**This is a NAVIGATION document, not an authority surface.**

`Aurea Build/BUILD_CONTRACT.md` remains the ruling record; `CLAUDE.md` remains the
operating instruction. Nothing here rules anything, closes anything, or grants
anything. It is a map: it says which domain a concept belongs to and which heading
section owns it, so that a name reserved in the corpus can be found again.

Created by **M1 — THE SCAFFOLD SWEEP** (2026-08-13), which deleted thirty-two
zero-byte module files and one empty package. Those files owned no store, no
authority, no transformation and no invariant; they were reserved names wearing a
module's shape. **Every name below remains recoverable from git history and from the
corpus.** Deletion is strike-and-keep at the tree level: the names were never lost,
only the empty files that impersonated them.

---

## The six domains

| Domain | One line |
|---|---|
| **Kernel** | The collapse core — perception, filtration, scars, doctrine, reflex arbitration, suspension. What survives contradiction and what it costs her to hold it. |
| **World Model** | What she holds about the world and where it came from — claim ancestry, source genealogy, predictions, record projection, topology. |
| **Executive** | What she is trying to do and what she is allowed to spend on it — goals, arbitration, activation, delegation, scheduling. |
| **Capability Plane** | Typed ingress and typed egress — how external material becomes a claim, and how an authorized action reaches the world through the Action Gateway. |
| **Foundry** | The external evaluation surface — candidate models measured against structured cases, with no authority over her. |
| **Builder** | The instruments that build and measure her — soak, differential, evaluation runner, invariant suite. They observe; they never grant. |

---

## Registered concepts (11) — reserved, with a destination

These names have somewhere to go. The file is gone; the concept is assigned.

| Concept | Domain | Destination |
|---|---|---|
| `cpa` | Capability Plane | Ingress, under heading §4's type system — **Pivot-P5 / M7** |
| `echotrace` | Capability Plane | Ingress, under heading §4's type system — **Pivot-P5 / M7** |
| `mloc` | Executive | Delegation and scheduler — **Phases 7–9** |
| `lcae` | Executive | Delegation and scheduler — **Phases 7–9** |
| `sif` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `xaig` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `ece` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `fsmd` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `asi` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `asis` | Capability Plane | Capability Plane + Action Gateway — **Phases 5, 11** |
| `scar_decay` | Kernel | The standing-derivation function — L7's decision-time compressions, **Phase 3** |

> `scar_decay`'s *scheduled* half already exists and is live: SML owns the decay state
> machine (Rulings 37, 40, 43). What the destination above reserves is the
> decision-time derivation, not a second writer of `decay_state`.

---

## Retired names (21)

Reserved in the corpus, never built, and carrying no destination in the current
heading. They are retired — **not forbidden**. A later ruling may recover any of
them; git history and the corpus both hold them intact.

`dml` · `harmonizer` · `aqgl` · `chrono_layer` · `sep` · `sge` · `bloom_mapping` ·
`anchor` · `echo_buffer` · `itr` · `car` · `rdm` · `contradiction_gateway` · `csam` ·
`echo_map` · `tca` · `audit` · `cbsal` · `config` · `helpers` · `logger`

**Two entries carry a qualification, so this map does not misdescribe the tree:**

- **`echo_buffer` — the NAME is retired; the FILE was NOT deleted.**
  `src/output/echo_buffer.py` survives at 0 bytes. `tests/invariants/test_ruling3_truth_effect.py`
  names it as a string in `RENDERER_PATHS`, so it is a live invariant fixture: both
  Ruling 3 tests guard `(hail.py, echo_buffer.py)` and skip a path that does not exist.
  Deleting the file would have narrowed that invariant from two renderers to one
  **silently, with nothing turning red.** M1 stopped on it and reported it rather than
  improvising. Retiring the name is a separate decision from disarming the guard, and
  only the first is M1's.
- **`tca` — retired as a MODULE NAME only.** The Topological Constellation Architecture
  is built and live in `src/topology/tca_core.py`, `tca_integration.py`, `tca_monitor.py`
  and `tcaml.py`. What retired is the empty `src/topology/tca.py` placeholder.

The package `src/perception/adapters/` was deleted with its 0-byte `__init__.py`.

---

## The reflex family — HELD / RE-DERIVE

`racm` · `reflex_grid` · `sbsre` · `rb_system` · `anchor_collapse`

**Disposition HELD / RE-DERIVE per Corrigendum C3, pending the M3 grounding.**
These are built, live, and load-bearing; they are named here only so that their
disposition is legible beside the swept names and is not mistaken for either a
domain assignment or a retirement. **M1 did not touch them.**
