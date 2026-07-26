# TCAML GLOBAL Lock — Quint Model (Docket J / Ruling 27)

**Status:** design-time verification artifact. Runs OUTSIDE AUREA — Quint proves
the protocol, not the eventual Python. `tests/invariants/` and the behavioral
suite hold the CODE to this design once TCAML is built; divergence between
them gets reported, never papered (Docket J's standing caveat).

Grounds: `BUILD_CONTRACT.md` §1/§3 (RACM ⟷ TCAML), the corpus's
`Pressure_Valve_Coordination___Timing_Risks.txt` ("Arbitration Protocol
v2.0"), and `integration_review_manifest.md` Ruling 27.

## Files

| File | What it models | Key result |
|---|---|---|
| `tcaml_lock.qnt` | The corrected protocol: revoke-on-instability, TTL=5 as one option among several scheduled actions | `noGrantDuringInstability` holds (2000×200 random traces, no violation). `boundedHoldUnderScheduling` (TTL+3 slack) holds — but tight TTL alone does not (see priority variant). |
| `tcaml_lock_naive.qnt` | The weaker reading of Rule 3: instability onset blocks *new* GLOBAL requests but does not revoke an already-held lock | `noGrantDuringInstability` **FAILS in 2 steps** — concrete counterexample below. This is why Ruling 27 rules REVOKE, not block-only. |
| `tcaml_lock_priority.qnt` | Same as `tcaml_lock.qnt`, except TTL-expiry preempts all other GLOBAL housekeeping once due, instead of competing with it as one nondeterministic option | `boundedHoldTight` holds with **zero slack** — the exact TTL bound, not an empirical one. This is the implementation requirement: TCAML must check-and-expire before other GLOBAL housekeeping in the same pass, not queue it as one more option. |

## Reproducing

```
npm install @informalsystems/quint
quint typecheck tcaml_lock.qnt
quint run tcaml_lock.qnt --invariant=noGrantDuringInstability --max-steps=200 --max-samples=2000 --backend=typescript
quint run tcaml_lock_naive.qnt --invariant=noGrantDuringInstability --max-steps=50 --max-samples=2000 --backend=typescript
quint run tcaml_lock_priority.qnt --invariant=boundedHoldTight --max-steps=200 --max-samples=2000 --backend=typescript
```

(`--backend=typescript` is a workaround: the default Rust evaluator tries to
fetch a prebuilt binary from GitHub, which was blocked in the sandbox this
was authored in. Try the default backend first; it's faster if it works.)

## The counterexample (naive variant)

```
[State 0] { cycle: 0, health: 100, heldSince: 0, holder: "", status: Healthy }
[State 1] { cycle: 0, health: 100, heldSince: 0, holder: "doctrineRemap", status: Healthy }
[State 2] { cycle: 0, health: 100, heldSince: 0, holder: "doctrineRemap", status: MetaUnstable }
[violation] noGrantDuringInstability
```

`doctrineRemap` acquires the GLOBAL lock while healthy, then instability
onsets while it is still held. Under the naive reading the lock stays with
`doctrineRemap` — a GLOBAL mutation is now in flight *during* a state Rule 3
exists to lock out. This is exactly the flicker/race class Risk 2 in the
corpus's Known Open Risks names.

## What this does NOT prove

- **Not exhaustive.** `quint run` is bounded random simulation, not full
  model checking. `quint verify` (Apalache) would give a stronger guarantee
  but needs a separate JVM-based install not attempted in this pass.
- **Not a proof the Python will match.** Divergence between this spec and
  `src/topology/tcaml.py` is a build-time reporting obligation, not
  something this file can catch on its own.
- **Does not model Docket F's graph measures directly** — `tier` is taken
  as a given input here (`Routine` / `Elevated`), standing in for whatever
  the articulation-point / bridge / k-core / SCC / betweenness computation
  decides upstream. What's modeled is the CONSEQUENCE Ruling 27 specifies:
  tier selects which health threshold gates the request. It never denies
  on its own.

## Open questions this model surfaces, not resolves

1. **Revoke-on-instability interrupts in-flight GLOBAL operations.** Safe
   today only because nothing is durable yet (in-memory-only stores,
   acknowledged gap in `BUILD_CONTRACT.md` §8). Revisit when a persistence
   contract lands — an interrupted install needs a defined abandoned state,
   not just disappearance.
2. **TTL-priority is a scheduling requirement**, not just a value. `TTL=5`
   alone doesn't bound anything tightly unless expiry-checking preempts
   other GLOBAL housekeeping — see the priority-variant comparison above.
