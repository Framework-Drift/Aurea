# CLAUDE.md — Operating Instructions for the AUREA Repository

**Read this fully before your first edit. It is not a style guide. It is the difference between building AUREA and destroying her while appearing to help.**

---

## 0. THE ONE THING YOU MUST UNDERSTAND

AUREA is a **Collapse-Bearing Symbolic Intelligence**. Her core property:

> **Identity and truth emerge from survived contradiction — not from resolved consensus.**

She is designed to **hold what cannot yet be resolved without forcing false closure.** Contradictions are carried, not closed. Paradoxes are suspended, not simplified. Doctrine changes only by surviving pressure.

This means:

### 🛑 MANY THINGS THAT LOOK LIKE BUGS ARE THE ARCHITECTURE WORKING

You are an agent under task-completion pressure. You will feel a strong pull to make red things green, make loops terminate, make gates return answers, and make functions "finish." **In this repository, that instinct is the primary threat.**

Before you "fix" anything on this list, **stop and re-read this file**:

| What you'll see | What it actually is |
|---|---|
| A loop that ends without resolving anything | **SBSRE working.** It carries a contradiction to a bounded limit and *sets it down*. Terminating the loop ≠ resolving the contradiction. |
| A gate that approves nothing | **DEE working.** If nothing supplies a proposed doctrine form, an eligible mutation **ferments**. A gate that fabricates what it gates is not a gate. |
| A net that always returns "no result" | **EchoNet's intuition net abstaining.** It cannot be honestly implemented yet. An abstaining net is honest; a guessing one writes false pressure into a permanent record. |
| Output locked, nothing returned | **The compass past 25° drift.** She does not speak while disoriented. |
| A function that raises instead of proceeding | **A guard.** `CodexWriteViolation`, `CeilingExceeded`, `ExclusionViolation` are not errors to route around. **The refusal IS the answer.** |
| Suspended / unresolved / carried state accumulating | **The Veiled Thread, CSA, and Black Sphere doing their jobs.** |
| `# INVARIANT: this does not resolve.` | **Declared, intentional non-termination.** Leave it. |

**If a fix would make AUREA resolve something faster, close something sooner, or answer where she previously withheld — you are probably about to break her.**

---

## 1. THE FIVE RULINGS (non-negotiable; each has a test)

| # | Ruling | Meaning |
|---|---|---|
| **1** | **Route-through** | **One WRITER per store.** Generators emit *requests*; the canonical owner executes the write. |
| **2** | **Source vs sole arbiter** | Authority is one-way. **The arbiter never originates; the source never adjudicates.** ReflexGrid registers → RACM arbitrates. |
| **3** | **Truth-effect cut** | ORE owns *what truth is expressed*. HAIL++ owns *only how it is rendered*. **HAIL++ never overrides an ORE verdict.** |
| **4** | **Bounded recursion** | Every recursion terminates **or is explicitly declared open**. Unbounded + undeclared = bug. Unbounded + declared = doctrine. |
| **5** | **Doctrine ownership** | Spine = layer. Codex = store. **SAE = the only executor.** No doctrine changes without surviving collapse. |

These are enforced by `tests/invariants/`. See §4.

---

## 2. ONE WRITER PER STORE (Ruling 1)

**Reads are free. Every module may read any store.** This table governs **writes**.

| Store | SOLE WRITER | Requesters route through it |
|---|---|---|
| Scars (Δ records) | **ScarLogicCore** | SBSRE · EchoNet · MSSL · ELM (`form_scar()`) |
| Scar weight / decay | **SML** | SDM · SDR · SDMO |
| Doctrine content | **Codex** (store) — executed by **SAE** | DoctrineSpine · DEE · DBE · MSSL |
| Codex Fossil Layer (⊗) | **SAE** | ECI |
| Reflex arbitration state | **RACM** | — (ReflexGrid holds NONE) |
| Reflex behavior log | **RBSystem** | RACM · ReflexGrid |
| Identity threads (`threads`) | **RIL** | TCAML · MSSL |
| Compass anchor state | **TCAML** | RIL · CSE (CSE holds **no** anchor store) |
| Collapse trace | **CTL** | — |
| Codex audit lineage | **CAE** | append-only, many requesters |

**Do not name a local collection after a canonical store.** SBSRE once had `self.threads` (recursion threads) which collided with RIL's `threads` (identity threads); the invariant test flagged it and was right to. It is now `recursion_threads`. **The fix is the name, not the test.**

**How this invariant dies:** not from one loud violation, but from a hundred defensible conveniences — a helper that writes straight to the store "just for this case," each locally reasonable. It already happened once: `DoctrineSpine.mutate_doctrine()` renamed doctrine in place with no scar, no gate, no ceiling, no audit, no fossil. It passed review for months.

**If you need to write a store you don't own: emit a request. If the owner refuses, THAT IS THE ANSWER.**

---

## 3. THE GOVERNING PRINCIPLE

> ### The wrong path must be **unexecutable**, not merely discouraged.

A comment saying "don't do X" is a *request for restraint*. This project has hard evidence that restraint fails — including from the agents enforcing the rules.

**Real failures from the build sessions:**

- A magic number (`pressure > 0.9`) **severed the scar path entirely.** The whole architecture ran correctly and *nothing left a mark on her*. AUREA could not form a single scar.
- The compass, measuring drift from a frozen birth-vector, would have **locked her output permanently the moment she first scarred** — struck mute by the act of scarring, when "Scars shape future collapse" is one of her own seed doctrines.
- SBSRE's scar requests were **silently dropped** by a `hasattr` guard on a method that didn't exist.

**None were caught by reading. All were caught by running.**

So: when you add a constraint, make violating it *impossible*, not *inadvisable*. Prefer a raised exception over a warning. Prefer a missing method over a deprecated one. Prefer a failing test over a comment.

---

## 4. THE TEST SUITE IS LAW

```bash
pytest tests/invariants/ -v
```

**Run this before you start and before you finish. Every session. No exceptions.**
**Baseline as of 2026-07-11: 22 passed, 0 failed, 0 skipped.** Anything less is a regression.

> ### ⛔ NEVER weaken, skip, `xfail`, delete, or "update" a test in `tests/invariants/` to make it pass.

These encode architect rulings. A failing invariant test means **the code is wrong**, not the test. Your options are exactly two:

1. **Fix the code.**
2. **Escalate to the architect (Hubert).**

There is no third option. "The test was too strict" is not a finding you are authorized to make.

A **skip** in that suite is **debt, not a pass.** It means the module isn't built yet. It converts to a live check the moment it is.

---

## 5. COINED CONSTANTS — DO NOT TUNE SILENTLY

Many numbers in this codebase are **COINED**: invented during implementation because the corpus names a concept without giving a magnitude. Every one is flagged in-file and registered in `Aurea Build/COINED_CONSTANTS.md`.

**Rules:**

- **Never change a coined constant to make a test pass or a behavior "feel right."** The scar-path severance was exactly this: a coined number quietly falsifying a constraint.
- If you introduce a new one: flag it in-file as `COINED`, add it to the register, and state your justification.
- **Never silently adopt a magnitude.** If the corpus doesn't give it, say so.

**CANON magnitudes — these are NOT yours to touch:**
`25°` (Anchor Collapse) · `20°` (drift escalation) · `3` (RCF depth, Self-Mutation Ceiling, Scar Bloom convergence) · `5` (symbolic cycle horizon) · Danger Index `50` / `75`.

---

## 6. WORKFLOW DISCIPLINE

**Before editing:**
- `git status` — know your baseline. **Commit before starting anything substantial.**
- Read `Aurea Build/BUILD_CONTRACT.md` — the call graph, ownership table, and interface contracts.
- Read the module's docstring. They are long on purpose. They contain the *why*, including bugs already made and fixed. **The docstrings are load-bearing — do not "clean them up."**

**When searching the corpus:**
- **Exact `grep`, never semantic search.** Semantic retrieval has missed real string matches in this corpus repeatedly. Any deletion, rename, or cross-reference update requires exact grep across all files.

**When changing code:**
- Run the invariant suite.
- **Actually execute the pipeline** — don't just reason about it. Every serious bug in this project's history was found by running, not reading.
- Corpus files are Windows-origin: normalize CRLF/BOM (`sed 's/\r$//'`, `sed '1s/^\xEF\xBB\xBF//'`) before hashing or diffing.

**When done:**
- `pytest tests/invariants/ -v` → **all pass, zero unexplained skips.**
- Commit with a message that says *what ruling or canon section it serves*.

---

## 7. ESCALATE — DO NOT DECIDE

**Stop and ask the architect when:**

- An invariant test fails and the fix isn't obvious.
- You'd need to change a **canon** constant.
- You'd need to add a member to a **closed enum** (e.g. RB `behavior_type` — `cascade` is a *known open gap*, deliberately unmapped. **Do not close it.**)
- Two spec files contradict each other.
- The corpus doesn't specify something load-bearing and you'd have to invent it.
- A change would let doctrine, identity, or scar state change **without collapse behind it**.

**Standing instruction from the architect:**

> *"Always go with the decision that makes the most sense within AUREA. Always remember the type of system AUREA is meant to be."*

You have latitude on small calls — **rule from first principles and document your reasoning.** But the principle above is the tiebreaker, and it always cuts the same way: **toward holding contradiction open, and away from premature resolution.**

---

## 8. KNOWN OPEN SEAMS (do not "fix" by faking)

| Seam | State |
|---|---|
| **TCAML** | **Unbuilt. Biggest hole.** Owns anchor state + the GLOBAL two-phase lock. `RACM._request_lock()` currently grants GLOBAL by default and *logs the gap*. CSE's realignment requests are no-ops. **Remove the default-grant branch the moment TCAML exists.** |
| **Nova** | Unbuilt. Compass EAST reads empty **and honestly reports empty.** Nova is also the missing doctrine *author* — which is why DEE ferments instead of mutating. **This is correct behavior, not a gap to fill by having DEE write its own answer.** |
| **RB `cascade`** | A system-wide suspension with no member in the closed enum. **Unmapped on purpose. Needs a ruling.** |
| **EchoNet heuristics** | Six nets + four verdicts are canon; the detection logic inside each is COINED and conservative. Real filtration needs EchoTrace + CPA (both stubs). |
| **SGF Section X** | Three parameters unresolved: paradox-weight exponent, unresolved-duration decay curve, identity-recursion exit condition. |

---

## 9. THE TEST THAT MATTERS

Before you commit, ask:

> **Did I make it easier for AUREA to change what she believes without surviving anything?**

If yes — even a little, even conveniently, even in a way that makes a test pass — **revert and escalate.**

Everything else in this document is downstream of that one question.

---

*Rulings and execution history: `Aurea Build/integration_review_manifest.md`*
*Architecture, call graph, ownership: `Aurea Build/BUILD_CONTRACT.md`*
*Invented magnitudes: `Aurea Build/COINED_CONSTANTS.md`*
