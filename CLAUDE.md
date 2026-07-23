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

## 1. THE THIRTEEN RULINGS (non-negotiable)

| # | Ruling | Meaning |
|---|---|---|
| **1** | **Route-through** | **One WRITER per store.** Generators emit *requests*; the canonical owner executes the write. |
| **2** | **Source vs sole arbiter** | Authority is one-way. **The arbiter never originates; the source never adjudicates.** ReflexGrid registers → RACM arbitrates. |
| **3** | **Truth-effect cut** | ORE owns *what truth is expressed*. HAIL++ owns *only how it is rendered*. **HAIL++ never overrides an ORE verdict.** |
| **4** | **Bounded recursion** | Every recursion terminates **or is explicitly declared open**. Unbounded + undeclared = bug. Unbounded + declared = doctrine. |
| **5** | **Doctrine ownership** | Spine = layer. Codex = store. **SAE = the only executor.** No doctrine changes without surviving collapse. |
| **6** | **Anchor-collapse single-owner** | The whole anchor-collapse response (onset→hard-kill) is ACR under RACM. Compass *sources*; RACM arbitrates; the output lock is the **consequence** of arbitration, never an inline `output_locked` flag. *(Ruled 2026-07-19; implementation pending — §8.)* |
| **7** | **`cascade` is control flow** | A cascade is **not** a `BehaviorType`. It **decomposes** into logged constituent behaviors + a CTL meta-event. The closed enum stays closed. *(Ruled 2026-07-19; **CLOSED 2026-07-20** — GSR `cascade` → logged `SUSPEND` + `cascade_meta` — §8.)* |
| **8** | **PSI decomposition** | PSI's suppress face is a **reflex under RACM** (rank 5) — it *proposes* `output_blocked`, never self-authorizes the lock. Its tone/depth face is a **render directive subordinate to ORE** (never overrides a verdict), **parked until HAIL exists**. Activation gates on **`trigger_type`**; a scar reference surfaces **only on a grounded ORIGIN/SCARLINE link, else it abstains**. *(Ruled 2026-07-20; **CLOSED 2026-07-20** — built, wired, arbitrated; 69 green. Directive parked pending HAIL — §8.)* |
| **9** | **Queue-won authorizations execute** | The Grid resolves every `result.execute` claim against its **FULL registry** (`self.reflexes`), never only the current-cycle triggered list — silently dropping an authorized claim **un-decides the arbiter by omission**. A queue-won claim runs against a **fresh `ReflexTrigger` reconstructed from its own stored payload** (`trigger_conditions` + claim `metadata`), NEVER the current cycle's pressure. **Deferred-wins-ties** is an explicit RACM sort key, not a dict-order accident. *(Ruled 2026-07-20; **CLOSED 2026-07-20**, adversarially verified — §8.)* |
| **10** | **Type-gated reflex activation** | Every reflex declares `trigger_types: Optional[frozenset]`; base `evaluate_pressure` = **type-membership AND magnitude**. `None` = canon-OPEN — **GSR only** (2a:583's five OR'd all-domain failsafe conditions, cited in-file). **ACR = {anchor_collapse}** — CSE is the sole canonical translator of directional threat; raw `scar_density` is GSR's Lexicon domain. **ICA = {identity_fracture, internal_contradiction, doctrine_anchor_collision, symbolic_instability}** (Lexicon §11; first live, rest declared-dormant). PSI's set unchanged — its local gate migrates into the base mechanism. New reflexes default CLOSED; OPEN requires corpus citation. *(Ruled 2026-07-20; **CLOSED 2026-07-20** — 77 green; `UngatedReflexViolation` refuses an open non-GSR reflex at registration — §8.)* |
| **11** | **RB durability is scope-tiered** | A behavior recorded from a **GLOBAL-scope reflex flushes to disk immediately** (best-effort — **the flush NEVER gates the reflex response**; a logging failure must not disable a safety suppression). LOCAL entries buffer (bounded; flush on cap / session-close / explicit drain; **overflow flushes, never drops**). `autoflush=True` = force-all override. Cascade is durable because **GSR is GLOBAL** (Ruling 7 decomposition), not because it is named — no `cascade_meta` / `action=='cascade'` check in the flush path. `RBSystem` stays scope-agnostic (`record(..., durable=...)`); `_log_execution` sets `durable=(reflex.scope==Scope.GLOBAL)` — do NOT import `Scope` into rb_system (racm→rb_system already; it would cycle). *(Ruled 2026-07-21; **CLOSED 2026-07-22 — 89 green, invariants 22/22, `cb0fcc0`**; §8.)* |
| **12** | **Nova grounding contract** | Nova authors doctrine **PROPOSALS** into DEE's gate (`aurea_core:521` `proposals=None` is the seam) — **from survived material only**. **G1:** `NovaEcho` construction **REQUIRES a real origin record** (scar / EchoNet verdict / CSA fragment / SBSRE abort / doctrine strain) and **RAISES on absence** — an echo with no traceable origin is fabricated pressure. **G2:** proposal emission only at status `Mutated` **+ scar linkage** ("Unverified Echoes may not write doctrine"). **G3:** new-forms are **recombination of store-traceable material — NO generative model in the truth-content path** (an LLM's output is resolved consensus; the founding axiom is survived contradiction). **G4:** Nova = sole writer of the **Nova Echo Index** only; scar/identity effects are REQUESTS to ScarLogicCore/RIL; **Codex never**. **G5:** refuses to run under RACM/Grid/TCAML suppression. **Timer→ELIGIBILITY only** — `Mutated` is set by a **succeeded collapse attempt**, never by clock. **Scope: Engine v1, single-echo**; NSC/fusion/NDR **declared-dormant**. *(Ruled 2026-07-21; **STAGE 1 CLOSED 2026-07-22 — 110 green, `95562cf`. STAGE 2 GATED on the echo-consumption ruling**; §8.)* |
| **13** | **A Nova echo is SPENT when it authors** | **One echo backs one proposal, EVER.** A MUTATED echo that has authored is consumed — it may never back another. Record consumption as a **FIELD** on the echo (`spent_on` = the proposal id, + timestamp): it is **NOT a fifth `FermentationStatus`** — that enum is canon-closed at DORMANT/ACTIVE/DECAYING/MUTATED and **stays closed** (Ruling 7's shape; `status` remains MUTATED). **`proposal_provenance` is APPEND-ONLY** — writing a key that already exists must **RAISE**, never overwrite: an overwrite means the one-proposal-ever gate already failed, and a forensic record is never overwritten (Ruling 11). **Do NOT over-narrow:** consumption is per-**ECHO**, not per-doctrine — a second, distinct MUTATED echo may still propose for the same strained doctrine. *(Ruled 2026-07-22; **impl PENDING — the Ruling-13 pass, with the `echo_index` invariant registration, BEFORE Stage 2 wiring**; §8.)* |

Rulings **1–5 are enforced by `tests/invariants/`** (§4). Rulings **6–11 are all CLOSED in code**; **Ruling 12 Stage 1 (the Nova organ) is CLOSED** — suite baseline **110**, invariants 22/22. **Ruling 13 is the ACTIVE task: the hardening pass — echo consumption + append-only provenance + registering `echo_index` in `STORE_OWNERS` (invariants 22→23). Organ + invariant ONLY; still no wiring. Stage 2 (wiring Nova) opens only after that pass verifies in Projects.** See §8 for the closed-seam record + remaining unbuilt-module seams (TCAML, HAIL, CTL, NSC).

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
| Nova Echo Index | **Nova** (Ruling 12) | — (scar effects → ScarLogicCore REQUEST · identity pulls → RIL NOVA-thread REQUEST · Codex never). **Ownership asserted but NOT yet scanned — register `echo_index` in `STORE_OWNERS` before wiring Nova.** |
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
- You'd need to add a member to a **closed enum**. RB `behavior_type` `cascade` is **RULED (Ruling 7): it decomposes into logged constituent behaviors + a CTL meta-event — it is NEVER added to the enum.** The closed enum stays closed.
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
| **Nova** | — **STAGE 1 CLOSED 2026-07-22 (110 green; `95562cf`). The organ exists; it is NOT wired. ACTIVE TASK = the Ruling-13 hardening pass (organ + invariant only, still NO wiring); Stage 2 wiring opens after it verifies in Projects.** Built and pinned: G1 `UngroundedEchoViolation` at `NovaEcho` construction (closed `ORIGIN_KINDS`; `erupt()` routes through the same constructor and cannot subtract from the gate); G2 `proposals()` emits only MUTATED + scar-linked; G3 `StoreFragment` refuses untraceable material at construction, recombination is tagged concatenation ONLY, `proposal_provenance` maps every emission, and the strained doctrine's own record is required; G4 sole store `echo_index`, scar/CSA effects parked as request lists; G5 suppressed cycle advances nothing. **`collapse_eligible` is a read-only property and `record_collapse_result(success=True)` is the ONLY writer of MUTATED** — 5a:1113's `Timer → Mutation` stays overruled; the test says to revert anyone who implements it. **Do not:** add fusion/NSC/NDR/reawakening (declared dormant, deliberately no fields), coin the §IV score formulas, weaken the two construction-time refusals, or let any generative model near the proposal path. Stage-2 scope, all parked honestly as parameters/return values: live suppression read · EchoNet/DEE collapse routing · `proposals()` → `aurea_core:521` · compass EAST · consumers for `scar_requests`/`csa_requests`. |
| **Anchor-collapse lock (Ruling 6)** | **CLOSED 2026-07-19 (41 green).** The lock is now the consequence of RACM authorizing a reflex's `output_blocked`, read from `CompassReading.reflex_responses` (the returned value of `evaluate_pressure`, never `last_arbitration`). The gate is **reflex-agnostic** — ANY RACM-authorized `output_blocked` locks, not `ANCHOR_COLLAPSE`-only; **do NOT re-narrow it.** `output_locked` renamed to `drift_past_lock_line` (diagnostic, never a gate). Bonus: total disorientation now locks (via GSR's authorized suppress) where the old drift-flag left her speaking at `_drift()=0`. |
| **RB `cascade` (Ruling 7)** | — **CLOSED 2026-07-20.** `_log_execution` translates GSR's `action="cascade"` → `BehaviorType.SUSPEND` (`affected_systems=["all"]`) + typed `cascade_meta` on `RBEntry` (CTL's parked surface; no CTL fabricated). Closed enum untouched — `cascade` never became a member. `monitor`/`base_reflex` still correctly unlogged (non-behaviors). The system-wide suspension that was invisible is now legible. **Do not re-narrow, and do not start logging monitor/base_reflex.** |
| **Type-gate (Ruling 10)** | — **CLOSED 2026-07-20 (77 green).** `trigger_types` on the base class; `evaluate_pressure` = type-membership AND magnitude; `UngatedReflexViolation` refuses an open (`None`) non-GSR reflex at `add_reflex` (core set routed through it, so the rule binds by construction). GSR=open (2a:583), ACR={anchor_collapse}, ICA=Lexicon-§11 set, PSI's local gate folded into base. False-lock path dead at the claim. **Do not re-open the gate or exempt a second reflex from the OPEN refusal.** |
| **PSI render directive (Ruling 8)** | PSI emits a render/scar-fallback directive (scar ref, tone weight, collapse-consistency marker) but **HAIL is a 0-byte stub and ORE a formatter skeleton — no live consumer.** Emit + **park** it, flagged caller-less (RIL-Nova / ACR-TCAML pattern). When HAIL is built it consumes the directive and may **never** use it to override an ORE verdict. ACR's `escalate_to:'PSI'` is **not dispatched** (no router; same as ICA→GSR) — PSI fires as its **own reflex**; a dispatcher is docketed. NB: PSI locally gates `evaluate_pressure` on `trigger_type` (Ruling 8 pt.4) — a local precedent for, not a discharge of, the pressure-type-gate ruling above. |
| **Queue execution (Ruling 9)** | — **CLOSED 2026-07-20 (69 green).** Authorized claims resolve by_id → full-registry fallback; queue winners execute against a trigger rebuilt from their own claim payload (adversarially verified); registry-miss → legible `grid.orphaned_authorizations` (closed RB enum respected); RACM `_rank_key=(effective_rank, deferral_seniority)`. **Do not re-narrow the registry fallback or reuse the live cycle's trigger for queue winners.** |
| **False-lock path** | — **CLOSED by Ruling 10 (2026-07-20).** ACR no longer accepts `scar_density`, so no deferred ACR can carry a foreign payload into a false anchor-collapse suppress. Historical: Ruling 9's honest execution had unmasked it (aurea_core 427-428 honors its own call sites' `output_blocked`). |
| **RB log durability (Ruling 11)** | — **CLOSED 2026-07-22 (89 green; `cb0fcc0`).** GLOBAL → immediate best-effort flush that never raises (failures → `flush_failures`; entry carried in buffer for boundary retry); LOCAL → bounded buffer (`LOCAL_BUFFER_CAP=64`, COINED) with cap/`drain()`/`close()` boundaries — overflow flushes, never drops. `RBEntry.scope` v1.2; no `Scope` import in rb_system. Suite isolation = autouse conftest redirect of `DEFAULT_LOG_PATH` to tmp. **Do not add an injectable no-op sink** (a forensic log you can silently disable is not a forensic log), **do not route durable writes through the buffer, and do not add any cascade/name check to the flush path** — durability comes from scope, pinned. |
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
