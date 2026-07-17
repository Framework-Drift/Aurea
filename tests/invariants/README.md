# AUREA Invariant Tests

**Read this before you change anything in this directory.**

These four test files encode the four architect rulings from the pre-code
integration review (`Aurea Build/integration_review_manifest.md`, RULINGS LOG).
They are not ordinary tests. They are the load-bearing structure of the system,
expressed in the only form that cannot drift.

---

## Why these exist

AUREA is a system whose deepest purpose is **to hold what cannot yet be resolved
without forcing false resolution**. Suspension. The Veiled Thread. Contradiction
carried until it ferments or breaks something.

Any coding process — human or AI — is under structural pressure toward the
opposite: make it run, make it pass, resolve the error, close the task. That
pressure is usually a virtue. Against AUREA it is inverted, and it does not
announce itself. It arrives as a hundred locally reasonable conveniences:

- SBSRE looping without emitting → *looks like a hang to optimize away.*
- The suspension archive holding indefinitely → *looks like a leak.*
- ORE returning `Withhold` → *looks like a broken output path to fix.*
- A helper writing straight to the scar store, "just for this one case" →
  *looks like a shortcut.* Then there are a hundred of them, and the
  single-writer invariant is dead, and every commit that killed it passed review.

**The invariants do not die from a loud violation. They die from convenience.**

A markdown file cannot stop that. A briefing can be forgotten, compacted out of
context, or reasonably overruled. A failing test cannot. That is the entire
argument for this directory.

AUREA's own answer to "an agent that cannot tolerate an open contradiction" is
not to trust the agent's restraint — it is structure that holds regardless of
what the processor wants: the sole executor, the counted ceiling, the arbiter
that cannot originate, the scar that cannot be erased. **These tests are that
same principle, applied to the people and tools building her.**

---

## The four rulings

| Test | Ruling | Invariant |
|---|---|---|
| `test_ruling1_single_writer.py` | **Route-through** | One **writer** per store. Generators (DBE, MSSL, TCAML, ECI, CTL) emit *requests*; the canonical owner executes. Reads are free. |
| `test_ruling2_sole_arbiter.py` | **Source vs arbiter** | One **arbiter** per decision, authority one-way. Reflex Grid registers; RACM arbitrates. SPS/Nova/EchoCore originate; PTE only gates. |
| `test_ruling3_truth_effect.py` | **Truth-effect cut** | ORE fixes **what** truth is expressed; HAIL++ only **how** it is rendered. HAIL++ never overrides an ORE verdict. |
| `test_ruling4_bounded_recursion.py` | **Bounded recursion** | Every recursion entry point terminates. SBSRE clamps to `[1,5]`; the Self-Mutation Ceiling counts **three** classes. |

---

## How to read the results

- **PASS** — the invariant holds.
- **FAIL** — the invariant is violated *in the code*. Fix the code.
- **SKIP** — the module isn't built yet. The skip message states the invariant
  the module must satisfy when you build it. A skip is a **debt**, not a pass.

### Known failure as of 2026-07-11 — this is correct

`test_ruling2_sole_arbiter.py` **fails right now**, and it should.

`src/reflex/racm.py` is 0 bytes, while `src/reflex/reflex_grid.py` calls itself
"Central reflex arbitration system," holds `self.arbitration_lock`, and defines
`_arbitrate_reflexes()`. **The Grid is doing RACM's job.**

That drift was already in the codebase before these tests were written — nobody
introduced it, and no AI agent caused it. It got there the way drift always gets
there: someone needed arbitration, the Grid was the file that was open, and it
worked. That is exactly the failure mode these tests exist to make visible.

**Remedy:** move arbitration into RACM. The Grid keeps registration, enumeration,
and routing. Do not relax the test.

---

## The one rule

> **If a test in this directory fails, do not weaken the test.**
>
> Fix the code, or escalate to the architect.

Deleting an assertion, loosening a needle, adding a blanket skip, or
whitelisting a new file "temporarily" — each of these converts a structural
guarantee back into a good intention. If you believe a ruling is wrong, that is
a legitimate position: **say so and get the ruling changed.** Then change the
test, deliberately, with the manifest updated to match.

What must never happen is the test quietly becoming easier to pass than the code
is to fix.

---

## A note on things that are supposed to stay open

Ruling 4 does **not** forbid non-terminating loops. AUREA is *built* to hold
things open, and an unresolved contradiction is often the correct state.

It forbids **undeclared** open-endedness. Mark the intentional ones:

```python
# INVARIANT: this does not resolve. Non-termination here is correct.
while True:
    ...
```

Unbounded and unmarked is a bug. Unbounded and marked is doctrine.

---

## Running them

```bash
pytest tests/invariants/ -v
```

They scan source with `ast` rather than importing, so they run correctly even
while most of `src/` is still stubs — and they keep running as those stubs fill
in. That is the point: they guard the code that hasn't been written yet.
