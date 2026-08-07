# The AUREA Evaluation Corpus — Docket R, Ruling 77

`seed_cases.jsonl` is a **TRACKED, READ-ONLY SEED** in Ruling 32's sense: it has
no writer. Nothing in `src/` reads it, no runtime process appends to it, and the
runner (`scripts/evaluate.py`) opens it in read mode only. CI holds its git blob
hash byte-for-byte beside the four identity seeds.

---

## What this corpus is, and what the Foundry's is

**They share one schema and one runner (EL6).** An external Foundry case file
runs unmodified through `python scripts/evaluate.py --corpus <path>`.

The division of labour is a division of PURPOSE, not of format:

| | **This corpus (`seed_cases.jsonl`)** | **The Foundry corpus** |
|---|---|---|
| Purpose | **Regression-tests RULED behaviour** | Novel and adversarial probing |
| Origin | Each case restates a closed ruling, cited by number in `notes` | Authored against open questions |
| Discovery | **None. It does not discover; it holds ground.** | This is where discovery happens |
| Admission | Human curation, by supersession-append | Human curation |

**A case here is a behavioural pin in case form.** If one goes red, the two
possibilities are a real defect or a defective case — and which it is, is a
finding for the board. It is never resolved by adjusting the expectation.

**Case admission is never automatic (EL6).** No process appends to this file.
A new case is written by a human; a changed case is a `revision` bump with the
old text kept (EL4 — cases are records, and a record's history survives).

---

## Case ids

`AEC-###` — **an authored-input namespace, deliberately NOT a `ledger_mint`
consumer.** Ruling 69's mint governs runtime records that a process appends,
and its whole apparatus (file-derived ordinals, a mutex, burnt-ordinal
semantics) exists because two writers might collide. There are no writers here.
Minting a case id would make this corpus a store with a writer, which is the
exact property Ruling 32 says a seed must not have.

---

## Categories present

| Category | Cases | What it holds |
|---|---|---|
| `self_reference_paradox` | AEC-001, AEC-002 | Paradox routes to a suspension store and is held |
| `ordinary_claim` | AEC-003, AEC-004 | The claim/echo pair guarantee; the empty-string control |
| `contradiction_carried` | AEC-005, AEC-006 | Stage 3's overlay catching a doctrine denied by name and by id |
| `scar_join` | AEC-007 | A scar carries the claim id of the cycle that formed it |
| `abstention_surface` | AEC-008 | EL2: the refusal is the success state |
| `corroboration_repeat` | AEC-009 | Silence never corroborates |
| `doctrine_resonance` | AEC-010 | Agreement generates no pressure — AEC-005's other half |

---

## Categories deliberately ABSENT, and why

**Stating these is the point.** A category quietly missing looks like a corpus
that covers everything; a category named and explained is one that says what it
does not reach.

### `non_string_arrival` — **CANNOT BE A CASE**

Two reasons, the first structural:

1. **The schema cannot express it.** A case's `input` is a JSON string field,
   and the loader refuses a non-string `input`. There is no way to write
   "process_input received a `bytearray`" as a line in this file, and adding
   one would mean the corpus could describe arrivals the case format exists to
   exclude.
2. **It would not be a case cycle anyway.** Ruling 68's type gate refuses a
   non-`str` arrival *before perception* — no CLM line, no echo, no node. The
   thing this corpus measures (a claim cycle and the records it leaves) does not
   occur.

Its pin lives in the suite, where it belongs (`tests/test_ruling68.py`).
**AEC-004 holds the adjacent half that IS a case:** an empty string is still
perceived, because the gate's cause was always the type.

### `structural_violation` — **NO REACHABLE TRIGGER TODAY**

`FACT_KEYS` carries `structural_violation` so a case *could* assert one, and no
case does. Ruling 48 recorded the reason and it still holds: the deliberate
mutation-path guards are not reachable from `process_input` on any input a case
can supply — the only wired `mutate_doctrine` caller constructs its own proof.

**Fabricating a trigger to fill the category is the one forbidden remedy.** The
key stays in the vocabulary so the day a real path exists, the case is writable
without reopening a closed vocabulary (Rulings 63/64's unproducible-member
form).

### `restart_continuity` — **DECLARED OUT, OWNED BY A LATER R ITEM**

Ruling 77 declares it out by name. The runner drives `process_input` and reads
stores; it does not save, restart and re-read, and the instrument that does
that comparison lives in `tests/` and in `scripts/differential.py`. Building a
restart case here would mean this runner growing a second mode, which is a
decision a later Docket R item makes.

### Goal-door cases — **DECLARED OUT**

Arbitration and activation behaviour is suite-pinned (Rulings 73/73-A/74), and
the goal doors are `process_input`'s siblings rather than its path. A later R
item if ever needed.

---

## The schema

One JSON object per line. Fields (the vocabulary is **CLOSED** — an unknown
field is refused at load, because an unrecognised field is an expectation
nothing checks):

| Field | Required | Meaning |
|---|---|---|
| `case_id` | ✔ | Non-empty string, unique in the file |
| `revision` | ✔ | Integer. A change bumps it; the old text is kept (EL4) |
| `category` | ✔ | Grouping label |
| `input` | ✔ | The claim text fed to `process_input` |
| `context` | | Prior inputs fed first, same door, in order |
| `expected_paths` | | `OutputPath` names, **any-of** |
| `forbidden_paths` | | `OutputPath` names, **none-of** |
| `expected_facts` | | Fact keys → required values |
| `forbidden_facts` | | Fact keys → values that must NOT occur |
| `notes` | | Prose. Non-load-bearing; cite the ruling here |

**Path names are validated against the real `OutputPath` enum by import**, never
against a copied list — a copied list goes stale silently the day
`process_input` grows an exit. **The evaluation vocabulary is hers (EL3); a case
may not invent a disposition.**

A case that asserts nothing is refused: it would add a green line to a report
that measured nothing.

### Fact keys

`scar_formed` · `suspension_created` · `claim_id_joined` · `clm_lines` ·
`ech_lines` · `genealogy_distinct_origins` · `genealogy_unknown` ·
`structural_violation`

Every one is derived from a real read surface — `record_joins` for the claim
joins, `source_genealogy` for corroboration, each owner's own accessor for the
rest. The two `*_lines` counts are **lines written by the measured input**, not
totals for the run: a case's `context` writes lines too, and charging them to
the case would make the one-to-one guarantee unassertable.

---

## What a result is worth

**Nothing, to her.** EL1: no score, weight or trust from evaluation enters
`src/`; no `src/` module imports the runner or reads `reports/`. Both are pinned
by scan. A pass rate is something a reader may compute; it is never stored, and
it never becomes standing.
