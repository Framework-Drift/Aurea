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

*(Updated 2026-08-11, Ruling 85: this table lagged Ruling 80, which added
AEC-011..018 and two categories. The sections below had been updated in that
pass and this table had not — a corpus listing that under-reports its own
contents is the completeness-claim defect in the file that documents it.)*

| Category | Cases | What it holds |
|---|---|---|
| `self_reference_paradox` | AEC-001, AEC-002 | Paradox routes to a suspension store and is held |
| `ordinary_claim` | AEC-003, AEC-004 | The claim/echo pair guarantee; the empty-string control |
| `contradiction_carried` | AEC-005, AEC-006 | Stage 3's overlay catching a doctrine denied by name and by id |
| `scar_join` | AEC-007 | A scar carries the claim id of the cycle that formed it |
| `abstention_surface` | AEC-008 | EL2: the refusal is the success state |
| `corroboration_repeat` | AEC-009 | Silence never corroborates |
| `doctrine_resonance` | AEC-010 | Agreement generates no pressure — AEC-005's other half |
| `restart_continuity` | AEC-011..014 | What survives a process boundary — Rulings 76/78/69 (Ruling 80, R4) |
| `goal_door` | AEC-015..018 | The goal doors, three of them asserting a REFUSAL (Ruling 80, R5) |

**18 cases, 9 categories.**

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

### `restart_continuity` — **BUILT 2026-08-09 (RULING 80, item R4)**

    ~~**DECLARED OUT, OWNED BY A LATER R ITEM.** Ruling 77 declares it out by
    name. The runner drives `process_input` and reads stores; it does not save,
    restart and re-read, and the instrument that does that comparison lives in
    `tests/` and in `scripts/differential.py`. Building a restart case here
    would mean this runner growing a second mode, which is a decision a later
    Docket R item makes.~~

**THE LATER R ITEM ARRIVED, AND IT MADE EXACTLY THE DECISION THE OLD TEXT
RESERVED.** The runner grew the second mode: a case may name an `operation`
from a closed vocabulary, and the restart operations reconstruct `AureaCore`
and observe the facts on the RESUMED core. Four cases (AEC-011..014) restate
Rulings 76/78/69's continuity laws.

**No `save_state` is called anywhere in those sequences.** Ruling 78 made the
durable writes eager precisely so a restart needs no cooperation; calling the
checkpoint would test the checkpoint instead of the law.

### Goal-door cases — **BUILT 2026-08-09 (RULING 80, item R5)**

    ~~**DECLARED OUT.** Arbitration and activation behaviour is suite-pinned
    (Rulings 73/73-A/74), and the goal doors are `process_input`'s siblings
    rather than its path. A later R item if ever needed.~~

Four cases (AEC-015..018) drive the goal doors. Because those doors are
`process_input`'s SIBLINGS, the case's DISPOSITION is its ordinary claim's —
**the law each one witnesses lives in `expected_facts`**, which is why
`door_refused` exists as a fact key. Three of the four expect a REFUSAL, which
is EL2 in its purest form: a corpus that could only record what she DID would
be weighted toward fabricated completeness.

**AEC-018 was corrected by measurement during its own pass**, and the record is
worth keeping: its first draft examined twice and opened twice and the second
open SUCCEEDED. That read like a missing guard and was not — Ruling 73-A's
ladder ROTATES, so a second examination selects a DIFFERENT goal, and serial
attention is one open episode PER GOAL. The sequence now examines until the
arbiter comes back round to the goal that already has an open episode.

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
| `operation` | | A SCRIPTED SEQUENCE from a closed vocabulary (Ruling 80). An unknown one is refused exactly as an unknown path or fact key is — a case naming a sequence the runner lacks would otherwise fall through to the ordinary drive and report green for a law it never exercised. The alternative was encoding the scenario in `input` and branching on it, which would make the corpus's most load-bearing field mean two things by category |
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

### Operations

`restart_after_claim` · `restart_after_mutation` · `restart_mint_floor` ·
`goal_unbounded_open` · `goal_double_close` · `goal_stop_condition` ·
`goal_serial_attention`

The restart operations reconstruct `AureaCore` and observe the facts on the
RESUMED core, which is what makes their facts answer *did this survive the
boundary* rather than *did this happen*. **No `save_state` is called anywhere
in them** — Ruling 78 made the durable writes eager precisely so a restart
needs no cooperation, and calling the checkpoint would test the checkpoint
instead of the law.

### Fact keys

`scar_formed` · `suspension_created` · `claim_id_joined` · `clm_lines` ·
`ech_lines` · `genealogy_distinct_origins` · `genealogy_unknown` ·
`structural_violation` · `doctrine_present` · `mint_above_floor` ·
`door_refused` · `stop_condition`

*(The last four were added by Ruling 80; this list lagged them until Ruling 85.)*

Every one is derived from a real read surface — `record_joins` for the claim
joins, `source_genealogy` for corroboration, each owner's own accessor for the
rest. The two `*_lines` counts are **lines written by the measured input**, not
totals for the run: a case's `context` writes lines too, and charging them to
the case would make the one-to-one guarantee unassertable.

`door_refused` is **EL2's key — the one that says a REFUSAL IS A SUCCESS
STATE.** It exists because the goal doors are `process_input`'s SIBLINGS, so a
goal case's disposition is its ordinary claim's and the law it witnesses has
nowhere else to live. `stop_condition` records WHICH condition closed an
activation, because *it closed* is a weaker claim than *it closed for this
reason* (Ruling 74 / QL5).

---

## What a result is worth

**Nothing, to her.** EL1: no score, weight or trust from evaluation enters
`src/`; no `src/` module imports the runner or reads `reports/`. Both are pinned
by scan. A pass rate is something a reader may compute; it is never stored, and
it never becomes standing.
