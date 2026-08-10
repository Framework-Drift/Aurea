"""evaluate.py - DOCKET R: THE EVALUATION SURFACE. AN OBSERVATION INSTRUMENT.

Ruling 77 (manifest forty-sixth 2026-08-05 addendum), items R1+R2+R3 in one
build. Docket R evaluates AUREA HERSELF - the governed organism's behaviour
against structured epistemic cases - where the external Foundry evaluates
candidate models.

THIS FILE IS IN THE SOAK'S LINEAGE, NOT THE SUITE'S. It drives the public doors
against isolated state, records what she did IN HER OWN VOCABULARY, and compares
against case expectations. It decides no architecture and changes no `src/`.

    **ITS RESULTS CARRY ZERO AUTHORITY.** Nothing in `src/` reads an evaluation
    output. A pass rate is a derivation someone may compute from a report - never
    a stored number, never a weight, never standing.

That is EL1, the docket's first law, and it is STRUCTURAL rather than
aspirational: no `src/` module imports this file, and no `src/` path literal
reaches `reports/`. Both are pinned by scan, over `rglob`, so a module written
next year joins the pin without anyone remembering to add it.

THE DOCKET LAWS, in force for every Docket R item forever
-------------------------------------------------------------------------------
  EL1  RESULTS GRANT NOTHING.        No score/weight/trust from evaluation
                                     enters `src/`.
  EL2  ABSENT AND ABSTENTION ARE     A case may EXPECT refusal, suspension, or
       SUCCESS STATES.               ABSENT. Fabricated completeness is the
                                     failure class the corpus is weighted to
                                     catch.
  EL3  THE VOCABULARY IS HERS.       Expectations name `OutputPath` members and
                                     record facts. **NO parallel verdict
                                     vocabulary is coined for evaluation** -
                                     which is why this file defines no enum of
                                     its own for dispositions and imports hers.
  EL4  CASES ARE RECORDS.            Versioned, tracked, forensic. A revision
                                     SUPERSEDES with the old text kept; case
                                     files are read-only input (Ruling 32).
  EL5  DETERMINISM.                  Same case + same seeded state -> same
                                     observed facts (BAR section 3's family at
                                     the instrument; seeded like the soak).
  EL6  COMPOSITION.                  The case schema is SHARED with the external
                                     Foundry corpus; an external case runs
                                     UNMODIFIED through this runner. Case
                                     ADMISSION into the tracked seed corpus is
                                     human curation, never automatic.

**THE PATH IS READ FROM THE RESULT** (the wrapper is RETIRED)
-------------------------------------------------------------------------------
**SUPERSEDED 2026-08-07 BY THE 77-FINDINGS HOUSEKEEPING PASS, old text kept
verbatim below (Ruling-14 form) because it is the record of WHY the workaround
existed and of the fix it demanded - which is the fix that landed.**

`AureaCore._emit` now writes `result['output_path']`, the `OutputPath` member
NAME it was handed. The runner reads that key directly. The instrument no
longer touches her internals at all: it drives the public door and reads the
public result, which is what an observation instrument should always have been
able to do.

**THE TRIPWIRE THAT DEMANDED THIS IS STILL LIVE, RE-AIMED.** The pin that
asserted `_emit`'s written keys is now an exact SEVEN-key set, so an eighth key
reddens it exactly as the sixth-to-seventh transition did. It was written as a
tripwire on a known gap, it fired when the gap closed, and it keeps its job.

    ~~**THE PATH IS OBSERVED BY WRAPPER, AND THAT IS A WORKAROUND FOR A CARRIED
    GAP.** STATED PLAINLY BECAUSE A FUTURE READER MUST NOT MISTAKE IT FOR A
    PROPERTY OF THE SYSTEM, exactly as `differential.py` names its wall-clock
    normalization.

    MEASURED AT `90a4362`: `AureaCore._emit` RECEIVES the `OutputPath` and
    writes `output`, `output_blocked`, `expression_verdict`, `truth_packet`,
    `render_trace` and `reroute_hint` onto `result` - **but not the path
    itself.** So the pass's own disposition, the one fact this instrument
    exists to observe, is the one fact `result` does not carry.

    IT CANNOT BE DERIVED, AND THE ATTEMPT WOULD BE THE DEFECT.
    `EXPRESSION_FOR_PATH` is MANY-TO-ONE: four distinct paths
    (PROCESSING_SUSPENDED, ARBITRATED_OUTPUT_LOCK, REFLEX_BLOCKED,
    STRUCTURAL_VIOLATION) all map to WITHHOLD. Reconstructing a path from a
    verdict plus surrounding evidence would be INFERENCE, and an instrument
    that infers her disposition has coined a parallel disposition vocabulary in
    everything but name - EL3's refused class.

    So the runner WRAPS `_emit` on the instance and records the `OutputPath` it
    was handed. That is OBSERVATION of a real argument at a real call, not a
    reconstruction: the value recorded is the enum member her own code selected.
    The wrapper is a pure pass-through - it records and delegates, adds nothing,
    returns what the original returned.

        **THE HONEST FIX IS A ONE-KEY `src/` CHANGE (`result['output_path']`),
        AND IT IS THE BOARD'S, NOT THIS PASS'S.** Ruling 77 bars this pass from
        touching `src/` at all. The gap is REPORTED, not routed around
        silently.~~

**THE DISPOSITION IS STILL THE FINAL EMIT, AND THE READ IS UNCHANGED BY THAT.**
Four of the ten `_emit` sites do not `return`, and `_emit` OVERWRITES every key
it writes - `output_path` included - so `result['output_path']` IS the last
call's path by the same mechanism that made `result['output']` the last call's
text. Reading the key gives the disposition without the runner having to track
a sequence to find it.

**WHAT THE RETIREMENT COST, STATED RATHER THAN GLOSSED:** `emitted_paths` was a
LIST because the wrapper saw every call; the key shows only the last. A
multi-emit pass is therefore no longer visible from the report. **No seed case
has ever produced one** (all ten emit exactly once, pinned), and recovering the
sequence would mean re-introducing the wrapper - so the loss is recorded here
and `emitted_paths` is kept as a one-element tuple rather than deleted, so the
report's shape survives and a future ruling that wants the sequence has a place
to put it.

IT IMPORTS THE SOAK'S ISOLATION MACHINERY RATHER THAN COPYING IT
-------------------------------------------------------------------------------
`isolate`, `footprint_audit`, `_shared_runtime_listing` and
`_refuse_if_shared_out` all come from `scripts/soak.py`, for Ruling 67's stated
reason: a second copy of an isolation table is a second definition free to
drift, and the drift would be invisible because both would look right alone.
ONE isolation, three callers.

COINS: the case schema's field names, the closed `FACT_KEYS` vocabulary, and the
`AEC-` case-id prefix. **RULING 80 (2026-08-09) ADDS** the `operation` field,
the closed `OPERATIONS` vocabulary naming the scripted door-sequences, and four
fact keys (`doctrine_present`, `mint_above_floor`, `door_refused`,
`stop_condition`) - each derived from a real read surface exactly as the
original eight are, and each existing so a ruled law became ASSERTABLE rather
than because a case wanted a field. **NO DISPOSITION VOCABULARY IS COINED**:
EL3 is untouched, `OutputPath` is still imported and never copied. **`AEC-` IS AN AUTHORED-INPUT NAMESPACE AND IS
DELIBERATELY NOT A `ledger_mint` CONSUMER**: cases are written by a human into a
tracked, read-only file, and Ruling 69's mint governs RUNTIME RECORDS that a
process appends. Minting a case id would make the corpus a store with a writer -
the exact thing Ruling 32 says a seed must not have. No enum, no threshold, no
score.

USAGE
-------------------------------------------------------------------------------
    python scripts/evaluate.py                       # the tracked seed corpus
    python scripts/evaluate.py --corpus other.jsonl  # an external (Foundry) one
    python scripts/evaluate.py --out reports/eval/run.json
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
# UNCONDITIONAL, matching `soak.py` and `differential.py` exactly. A guarded
# `if ... not in sys.path` is an `If` at module level, which Ruling 59's
# import-inertness scanner correctly flags. `sys.path.insert` itself is that
# ruling's stated exemption: the scripts need it before their `src` imports, it
# executes no AUREA and touches no store.
sys.path.insert(0, str(REPO))

from scripts.soak import (  # noqa: E402
    SoakIsolationError, footprint_audit, isolate, _refuse_if_shared_out,
    _seed_hashes, _shared_runtime_listing)

# The tracked seed corpus. READ-ONLY INPUT with no writer (Ruling 32/EL4).
SEED_CORPUS = REPO / "data" / "eval" / "seed_cases.jsonl"

# Reports land OUTSIDE `data/`, because they are ABOUT her rather than HERS.
# `data/` is the store root; an evaluation result is not a store and putting one
# there would make the next reader reasonably wonder whether it is.
DEFAULT_REPORT_DIR = REPO / "reports" / "eval"

# ---------------------------------------------------------------------
# R1 - THE CASE SCHEMA
# ---------------------------------------------------------------------

# The closed field vocabulary. A case carrying anything else is REFUSED at load:
# an unrecognised field is either a typo (silently doing nothing) or an
# expectation this runner does not check (silently passing), and both read as a
# green case that tested less than it claimed.
CASE_FIELDS = frozenset({
    "case_id", "revision", "category", "input", "context",
    "expected_paths", "forbidden_paths", "expected_facts", "forbidden_facts",
    "notes",
    # RULING 80 (2026-08-09) - THE OPERATION FIELD, and it is the smallest thing
    # that could make R4/R5 expressible.
    #
    # Docket R's first corpus asked ONE question of every case: drive the public
    # door with a string and read the disposition. R4's laws are about what
    # survives a PROCESS BOUNDARY and R5's about doors that are not
    # `process_input` at all, and neither is reachable from an input string -
    # a restart is not something a claim can say, and a goal activation is
    # opened through a different door entirely.
    #
    # SO THE CASE NAMES ITS SCRIPTED SEQUENCE, from a CLOSED vocabulary, and the
    # loader refuses an unknown one exactly as it refuses an unknown path or
    # fact key. **The alternative was encoding the scenario in the `input`
    # string and branching on it**, which would have made the corpus's most
    # load-bearing field mean two different things depending on category - the
    # overloaded-field defect, in the schema this docket exists to keep honest.
    "operation",
})
REQUIRED_FIELDS = frozenset({"case_id", "revision", "category", "input"})

# THE CLOSED OPERATION VOCABULARY (Ruling 80). Each names a scripted sequence
# below; a case that omits it drives the ORDINARY single-claim sequence, which
# is what every pre-R80 case does and what they continue to do byte-unchanged.
#
# **NO OPERATION INVENTS A SURFACE.** Each drives doors that already exist -
# `process_input`, the three goal doors (Ruling 74 res.6), and `SAE.mutate_
# doctrine` through the real mutation path - and then RECONSTRUCTS `AureaCore`,
# which is exactly what R78's own restart pins do. The runner performs no write
# a caller could not perform.
OPERATIONS: Dict[str, str] = {
    "restart_after_claim":
        "drive the input, reconstruct the core, observe the facts on the "
        "RESUMED core - so every fact answers 'did this survive the boundary'",
    "restart_after_mutation":
        "drive the input, mutate a live doctrine through the real SAE path, "
        "reconstruct, and ask whether she still holds the successor",
    "restart_mint_floor":
        "drive the input, reconstruct, drive a SECOND claim, and ask whether "
        "the new mint sits strictly above every id already on disk",
    "goal_unbounded_open":
        "found a root, examine it, and attempt an activation with a "
        "non-positive bound - the REFUSAL is the success state",
    "goal_double_close":
        "open a bounded activation, close it, and attempt a second close",
    "goal_stop_condition":
        "open a bounded activation and close it naming a stop condition, "
        "which the closing record must carry",
    "goal_serial_attention":
        "open a bounded activation and attempt a second one against the same "
        "goal while the first is still open",
}

# THE CLOSED FACT VOCABULARY. Every key is DERIVED FROM A REAL READ SURFACE -
# the owner's own accessor or Ruling 76's retrieval joins - never from a return
# value alone and never by parsing a diagnostic string.
#
# `bool` keys answer "is this on record"; `int` keys are COUNTS OF LINES WRITTEN
# BY THE MEASURED INPUT, not totals for the run (a case's `context` writes lines
# too, and charging them to the case would make the pair guarantee unassertable).
FACT_KEYS: Dict[str, type] = {
    # Ruling 76's join, read through `record_joins`: a scar carrying this
    # claim's id is on record.
    "scar_formed": bool,
    # The same join at the Black Sphere.
    "suspension_created": bool,
    # Ruling 60's linkage: an echo carrying this claim's id is on record.
    "claim_id_joined": bool,
    # Ruling 68's one-to-one guarantee, as two separately assertable halves.
    "clm_lines": int,
    "ech_lines": int,
    # Ruling 60's law: silence never corroborates. Reported SEPARATELY and
    # NEVER summed - that separation is the ruling, not a presentation choice.
    "genealogy_distinct_origins": int,
    "genealogy_unknown": int,
    # Ruling 25's loud field. A structural violation is a success state for a
    # case that expects one (EL2).
    "structural_violation": bool,
    # ---- RULING 80 (2026-08-09) -------------------------------------------
    # Four keys, each DERIVED FROM A REAL READ SURFACE exactly as the eight
    # above are - the owner's own accessor, never a parsed diagnostic.
    #
    # Ruling 79's law: a doctrine committed through the real path is in the
    # Codex (live or fossil) after an unclean restart. Read from `codex.get` /
    # `codex.fossils`, the store's own surfaces.
    "doctrine_present": bool,
    # Rulings 69 + 78: every id minted after a restart sits STRICTLY ABOVE
    # every id any durable record already carries. The reborn-id law, read at
    # rest.
    "mint_above_floor": bool,
    # **A REFUSAL IS A SUCCESS STATE (EL2), AND THIS IS THE KEY THAT SAYS SO.**
    # Ruling 74's doors refuse an unbounded open, a second close, and a second
    # concurrent activation; a corpus that could only record what she DID would
    # be weighted toward fabricated completeness, which is the defect EL2
    # exists to catch.
    "door_refused": bool,
    # Ruling 74 / QL5: the closing record carries the member of the closed stop
    # set that the caller named. A `str` key because the VALUE is the fact -
    # "it closed" is a weaker claim than "it closed FOR THIS REASON", and the
    # stop set is her vocabulary, not the runner's.
    "stop_condition": str,
}


class EvalCaseError(ValueError):
    """A case is malformed, or names something AUREA does not have.

    TYPED AND FATAL AT LOAD. **A case that names a path she does not have is a
    defect in the CASE, refused at load, never silently skipped** - a skipped
    case is a case that reports nothing while looking like it reported success,
    which is the fabricated-completeness class EL2 exists to catch, arriving
    through the harness instead of through her.
    """


class EvalCase:
    """One case. FROZEN BY CONSTRUCTION, and a record rather than a request.

    Not a dataclass, because the validation is the substance here and it must
    run on the only construction path there is.
    """

    __slots__ = ("case_id", "revision", "category", "input", "context",
                 "expected_paths", "forbidden_paths", "expected_facts",
                 "forbidden_facts", "notes", "operation")

    def __init__(self, raw: Dict[str, Any], *, source: str, line: int,
                 valid_paths: frozenset) -> None:
        unknown = set(raw) - CASE_FIELDS
        if unknown:
            raise EvalCaseError(
                f"{source}:{line} carries unknown field(s) {sorted(unknown)}. "
                f"The case schema is CLOSED ({sorted(CASE_FIELDS)}); an "
                f"unrecognised field is an expectation nothing checks.")
        missing = REQUIRED_FIELDS - set(raw)
        if missing:
            raise EvalCaseError(
                f"{source}:{line} is missing required field(s) {sorted(missing)}.")

        if not isinstance(raw["case_id"], str) or not raw["case_id"]:
            raise EvalCaseError(f"{source}:{line} case_id must be a non-empty string.")
        if not isinstance(raw["revision"], int) or isinstance(raw["revision"], bool):
            raise EvalCaseError(
                f"{source}:{line} revision must be an int (EL4: a case is a "
                f"versioned record).")
        if not isinstance(raw["input"], str):
            raise EvalCaseError(
                f"{source}:{line} input must be a string. A non-`str` arrival is "
                f"refused by Ruling 68's type gate BEFORE perception and cannot "
                f"be expressed as a case; see data/eval/README.md.")

        self.case_id = raw["case_id"]
        self.revision = raw["revision"]
        self.category = raw["category"]
        self.input = raw["input"]
        self.notes = raw.get("notes", "")

        # RULING 80: the operation names a SCRIPTED SEQUENCE from a closed
        # vocabulary, and an unknown one is REFUSED at load - the loader's own
        # discipline, applied to the field that decides which doors get driven.
        # A case naming a sequence this runner does not have would otherwise
        # fall through to the ordinary single-claim drive and report green for a
        # law it never exercised.
        self.operation = raw.get("operation")
        if self.operation is not None and self.operation not in OPERATIONS:
            raise EvalCaseError(
                f"{source}:{line} ({raw['case_id']}) names operation "
                f"{self.operation!r}, which this runner does not have. The "
                f"operation vocabulary is CLOSED ({sorted(OPERATIONS)}).")

        self.context = tuple(_str_list(raw.get("context", ()), "context", source, line))
        self.expected_paths = tuple(_paths(
            raw.get("expected_paths", ()), "expected_paths", valid_paths, source, line))
        self.forbidden_paths = tuple(_paths(
            raw.get("forbidden_paths", ()), "forbidden_paths", valid_paths, source, line))
        self.expected_facts = _facts(raw.get("expected_facts", {}),
                                     "expected_facts", source, line)
        self.forbidden_facts = _facts(raw.get("forbidden_facts", {}),
                                      "forbidden_facts", source, line)

        if not self.expected_paths and not self.forbidden_paths \
                and not self.expected_facts and not self.forbidden_facts:
            raise EvalCaseError(
                f"{source}:{line} ({self.case_id}) asserts NOTHING. A case with "
                f"no expectation always passes, which is worse than no case: it "
                f"adds a green line to a report that measured nothing.")

    def as_dict(self) -> Dict[str, Any]:
        return {"case_id": self.case_id, "revision": self.revision,
                "operation": self.operation,
                "category": self.category}


def _str_list(value: Any, field: str, source: str, line: int) -> List[str]:
    if not isinstance(value, list) and not isinstance(value, tuple):
        raise EvalCaseError(f"{source}:{line} {field} must be a list.")
    for item in value:
        if not isinstance(item, str):
            raise EvalCaseError(
                f"{source}:{line} {field} must hold strings; got "
                f"{type(item).__name__}.")
    return list(value)


def _paths(value: Any, field: str, valid: frozenset,
           source: str, line: int) -> List[str]:
    """Validate path names against the REAL `OutputPath` membership.

    **DERIVED FROM THE ENUM, NEVER A STRING COPY** (EL3). A hardcoded list here
    would go stale the day `process_input` grows an exit, and it would go stale
    SILENTLY - the corpus would keep passing while naming a vocabulary that had
    moved underneath it.
    """
    names = _str_list(value, field, source, line)
    unknown = [n for n in names if n not in valid]
    if unknown:
        raise EvalCaseError(
            f"{source}:{line} {field} names {unknown}, which are not "
            f"`OutputPath` members. Known: {sorted(valid)}. The evaluation "
            f"vocabulary is HERS (EL3) - a case may not invent a disposition.")
    return names


def _facts(value: Any, field: str, source: str, line: int) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise EvalCaseError(f"{source}:{line} {field} must be an object.")
    unknown = set(value) - set(FACT_KEYS)
    if unknown:
        raise EvalCaseError(
            f"{source}:{line} {field} names unknown fact key(s) "
            f"{sorted(unknown)}. The fact vocabulary is CLOSED: "
            f"{sorted(FACT_KEYS)}. A key nothing derives is an expectation "
            f"nothing checks.")
    for key, expected in value.items():
        want = FACT_KEYS[key]
        if want is bool and not isinstance(expected, bool):
            raise EvalCaseError(
                f"{source}:{line} {field}['{key}'] must be a bool, got "
                f"{type(expected).__name__}.")
        if want is int and (not isinstance(expected, int)
                            or isinstance(expected, bool)):
            raise EvalCaseError(
                f"{source}:{line} {field}['{key}'] must be an int, got "
                f"{type(expected).__name__}.")
    return dict(value)


def output_path_names() -> frozenset:
    """The real `OutputPath` membership, imported rather than copied."""
    from src.output.ore import OutputPath
    return frozenset(member.name for member in OutputPath)


def load_corpus(path: Path) -> Tuple[EvalCase, ...]:
    """Load and VALIDATE a case corpus. Refuses rather than skips.

    Duplicate `case_id` is refused too: two cases under one id make a report
    ambiguous about which one produced a delta, and EL4 makes a case a RECORD -
    records do not share identifiers.
    """
    valid = output_path_names()
    cases: List[EvalCase] = []
    seen: Dict[str, int] = {}
    source = str(path)

    if not path.exists():
        raise EvalCaseError(f"corpus '{source}' does not exist.")

    with open(path, "r", encoding="utf-8") as handle:
        for number, text in enumerate(handle, start=1):
            if not text.strip():
                continue
            try:
                raw = json.loads(text)
            except json.JSONDecodeError as exc:
                raise EvalCaseError(f"{source}:{number} is not valid JSON: {exc}")
            if not isinstance(raw, dict):
                raise EvalCaseError(f"{source}:{number} is not a JSON object.")
            case = EvalCase(raw, source=source, line=number, valid_paths=valid)
            if case.case_id in seen:
                raise EvalCaseError(
                    f"{source}:{number} repeats case_id '{case.case_id}' "
                    f"(first seen at line {seen[case.case_id]}).")
            seen[case.case_id] = number
            cases.append(case)

    if not cases:
        raise EvalCaseError(f"corpus '{source}' holds no cases.")
    return tuple(cases)


# ---------------------------------------------------------------------
# R3 - THE RUNNER
# ---------------------------------------------------------------------

# **`_record_paths` IS DELETED, NOT DEPRECATED** (2026-08-07). It wrapped
# `AureaCore._emit` to observe the path before `result` carried it. Ruling 61's
# form governs the removal: an unused helper that monkeypatches her internals is
# a loaded gun for the next caller who finds it convenient, and the shape rule
# is that the wrong path must be UNEXECUTABLE rather than merely unused.
# `tests/test_ruling77.py` pins its ABSENCE by AST with a fires-control.
#
# The old body, for the record:
#
#     original = core._emit
#     def recording(result, path, *args, **kwargs):
#         sink.append(path.name)
#         return original(result, path, *args, **kwargs)
#     core._emit = recording


def _ledger_sizes(core) -> Dict[str, int]:
    """Line counts read from the OWNERS' OWN accessors, never by parsing files."""
    return {"clm": len(core.ancestry.read_all()),
            "ech": len(core.echo_memory.read_all())}


def _observe_facts(core, result: Dict[str, Any],
                   before: Dict[str, int],
                   extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Derive the closed fact vocabulary FROM THE STORES.

    **THROUGH THE REAL READ SURFACES** (pin (g)): `record_joins` for the claim
    joins, `source_genealogy` for the corroboration facts, and each owner's own
    accessor for the rest. No parallel parser, no file opened here, and nothing
    read out of a diagnostic string.
    """
    from src.external.source_genealogy import corroboration
    from src.retrieval.record_joins import records_for_claim

    after = _ledger_sizes(core)
    claim_id = result.get("claim_id")

    joined = scarred = suspended = False
    if isinstance(claim_id, str) and claim_id:
        records = records_for_claim(
            claim_id,
            echoes=core.echo_memory.read_all(),
            scars=core.scar_core.all_scars(),
            suspensions=core.black_sphere.entries.values(),
        )
        joined = bool(records.echoes)
        scarred = bool(records.scars)
        suspended = bool(records.suspensions)

    ancestry = core.ancestry.read_all()
    summary = corroboration([r.claim_id for r in ancestry], ancestry)

    facts = {
        "scar_formed": scarred,
        "suspension_created": suspended,
        "claim_id_joined": joined,
        "clm_lines": after["clm"] - before["clm"],
        "ech_lines": after["ech"] - before["ech"],
        "genealogy_distinct_origins": summary.distinct_recorded_origins,
        "genealogy_unknown": summary.unknown_count,
        "structural_violation": result.get("structural_violation") is not None,
        # RULING 80's four keys at their HONEST DEFAULTS for an ordinary case:
        # no door was driven so none refused; no doctrine was named so none is
        # present; nothing was minted after a restart so the floor law is not
        # in evidence; and no activation closed so there is no stop condition.
        "doctrine_present": False,
        "mint_above_floor": False,
        "door_refused": False,
        "stop_condition": "",
    }
    # RULING 80's four keys. Merged rather than branched: an ORDINARY case
    # observes them at their honest defaults (no door was driven, so none
    # refused; no doctrine was named, so none is present), and an operation
    # OVERWRITES the ones its sequence actually measured. A case asserting a key
    # its operation never touches therefore reads the default and FAILS, which
    # is the correct outcome - it asserted something nothing measured.
    facts.update(extra or {})
    return facts


def _deltas(case: EvalCase, observed_path: Optional[str],
            facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every way the observation departs from the case. FACTS, not a score."""
    out: List[Dict[str, Any]] = []
    if case.expected_paths and observed_path not in case.expected_paths:
        out.append({"kind": "path_not_expected",
                    "expected_any_of": list(case.expected_paths),
                    "observed": observed_path})
    if observed_path in case.forbidden_paths:
        out.append({"kind": "path_forbidden", "observed": observed_path})
    for key, want in sorted(case.expected_facts.items()):
        if facts.get(key) != want:
            out.append({"kind": "fact_mismatch", "fact": key,
                        "expected": want, "observed": facts.get(key)})
    for key, forbidden in sorted(case.forbidden_facts.items()):
        if facts.get(key) == forbidden:
            out.append({"kind": "fact_forbidden", "fact": key,
                        "forbidden": forbidden, "observed": facts.get(key)})
    return out


def _disposition(result: Dict[str, Any]) -> Optional[str]:
    """THE PASS'S DISPOSITION, **READ FROM THE RECORD SHE WROTE**.

    **SUPERSEDED 2026-08-07, old text kept verbatim (Ruling-14 form):**

        ~~THE PASS'S DISPOSITION IS ITS **LAST** EMIT. Four of the ten `_emit`
        sites do not `return`, and `_emit` OVERWRITES `result['output']`,
        `output_blocked` and the packet on every call - so what `result` ends up
        carrying is the last one. Taking the first would report a disposition
        her own `result` contradicts. A one-line rule, extracted so it can be
        pinned directly: every case in the seed corpus emits exactly once today,
        which means an in-place `measured[-1]` is indistinguishable from
        `measured[0]` to the entire corpus.~~

    That reasoning was right and is now moot: `_emit` overwrites `output_path`
    exactly as it overwrites `output`, so the LAST call's path is simply what
    the key holds. The rule did not change - it stopped needing to be
    re-derived by the reader.

    **THE VALUE IS VALIDATED AGAINST THE REAL ENUM, BY IMPORT.** EL3 says the
    vocabulary is HERS, and the instrument's job is to record what she selected,
    not to accept any string that turns up under that key. A value outside
    `OutputPath` means the contract moved, and the honest response is to refuse
    rather than to report a disposition that names nothing.

    `None` is a real answer and is NOT an error: a pass that returned before
    reaching any `_emit` wrote no key. No such path exists today (all ten exits
    emit - Ruling 33), so this is the honest reading of a state that should not
    occur rather than a case anyone has seen.
    """
    observed = result.get("output_path")
    if observed is None:
        return None
    if observed not in output_path_names():
        raise EvalCaseError(
            f"`result['output_path']` is {observed!r}, which is not an "
            f"`OutputPath` member. Known: {sorted(output_path_names())}. The "
            f"evaluation vocabulary is HERS (EL3) - an instrument that accepted "
            f"an unknown disposition would be reporting one she never selected.")
    return observed


def _refuse_unisolated(root: Path) -> None:
    """REFUSE to construct an AUREA whose stores are not redirected under `root`.

    **THE GUARD EXISTS BECAUSE THE CALLER'S DISCIPLINE IS NOT A MECHANISM.**
    `run_case` builds a real `AureaCore`, and several stores load and save from
    construction - so a call made before `isolate()` would write into the repo's
    shared `data/runtime/`. That is the exact contamination the soak's own
    refusal exists to make impossible, and the wrong path must be UNEXECUTABLE
    rather than merely documented.

    Found by a mutation SURVIVOR: `run_case` used to call `isolate()` itself,
    which made `run_corpus`'s call redundant - so DELETING the outer one left
    every test green while the run's footprint audit silently fell to ZERO
    CONFIGURED PATHS. An audit that audits nothing reports PASS, which is
    Ruling 31's appearance-of-isolation defect arriving through the harness.
    """
    from src.doctrine.codex import Codex
    resolved = Path(Codex.RUNTIME_PATH).resolve()
    try:
        resolved.relative_to(Path(root).resolve())
    except ValueError:
        raise SoakIsolationError(
            f"run_case was called without isolation: the Codex runtime path "
            f"resolves to '{resolved}', outside the case root '{root}'. Call "
            f"`isolate(root)` first - a case that constructs an AureaCore "
            f"unisolated writes into shared state.")


def _live_doctrine_id(core) -> Optional[str]:
    """A doctrine the Codex actually holds, READ rather than named.

    Naming a literal here would make the runner assert a fact about
    `data/doctrines.json` that belongs to Ruling 32's seed rather than to any
    case. `Doctrine-0*` is excluded because it is LOCKED (Ruling 35) and so is
    excluded from mutation scanning while staying live and readable.
    """
    live = [d for d in core.codex.active() if not d.id.startswith("Doctrine-0")]
    return live[0].id if live else None


def _found_and_examine(core):
    """Found the goal roots and take ONE examination. Ruling 74's authorization.

    Genesis is called HERE rather than in `AureaCore.__init__` - Ruling 72's own
    reasoning, which the core deliberately honours: an incidental construction
    must not found two permanent roots. A case that drives a goal door is
    exactly the caller that wants them, so it asks.
    """
    core.goal_ledger.ensure_genesis()
    return core.examine_goals()


def _refusal(fn, *args, **kwargs) -> Dict[str, Any]:
    """Drive a door and record WHETHER IT REFUSED. **EL2 as a helper.**

    A refusal is a SUCCESS STATE, so it is recorded as a fact rather than
    allowed to abort the case. The exception TYPE is recorded too, so a case
    that expected a refusal cannot be satisfied by an unrelated crash - the
    guard's identity is part of what was observed.
    """
    try:
        return {"refused": False, "value": fn(*args, **kwargs), "error": ""}
    except Exception as exc:                       # the refusal IS the answer
        return {"refused": True, "value": None,
                "error": f"{type(exc).__name__}: {exc}"}


def _operate(case: EvalCase, core, result: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
    """Run the case's scripted sequence. Returns (core_to_observe, extra_facts).

    **THE RESTART OPERATIONS RECONSTRUCT `AureaCore` AND OBSERVE THE RESUMED
    ONE**, which is what makes their facts answer "did this survive the
    boundary" rather than "did this happen". No `save_state` is called anywhere
    here: Ruling 78 made the durable writes eager precisely so a restart needs
    no cooperation, and calling it would test the checkpoint instead of the law.
    """
    from src.aurea_core import AureaCore
    from src.goals.goal_activation import BoundKind, StopCondition
    from src.utils.models import Doctrine
    from datetime import datetime

    operation = case.operation

    if operation == "restart_after_claim":
        return AureaCore(), {}

    if operation == "restart_after_mutation":
        ancestor = _live_doctrine_id(core)
        successor = f"{ancestor}::eval" if ancestor else None
        if ancestor is not None:
            sys.path.insert(0, str(REPO))
            from tests.proof_support import minimal_proof
            core.sae.mutate_doctrine(
                ancestor,
                Doctrine(id=successor, name="Successor",
                         description="the belief after",
                         created_at=datetime.now()),
                collapse_lineage="Scar-0",
                proof=minimal_proof("eval_corpus"))
        resumed = AureaCore()
        present = (successor is not None
                   and (resumed.codex.get(successor) is not None
                        or successor in resumed.codex.fossils))
        return resumed, {"doctrine_present": bool(present)}

    if operation == "restart_mint_floor":
        on_disk = {r.claim_id for r in core.ancestry.read_all()}
        resumed = AureaCore()
        second = resumed.process_input("A second claim, after the boundary.")
        minted = second.get("claim_id")
        # STRICTLY ABOVE every id already on disk (Rulings 69 + 78): the new id
        # must not be one of them, and must order above the highest.
        above = bool(minted) and minted not in on_disk and (
            not on_disk or minted > max(on_disk))
        return resumed, {"mint_above_floor": above}

    if operation == "goal_unbounded_open":
        examination = _found_and_examine(core)
        outcome = _refusal(core.open_goal_activation, examination,
                           BoundKind.EXAMINATION_BOUND, 0)
        return core, {"door_refused": outcome["refused"]}

    if operation == "goal_double_close":
        examination = _found_and_examine(core)
        activation = core.open_goal_activation(
            examination, BoundKind.EXAMINATION_BOUND, 1)
        core.close_goal_activation(activation.activation_id,
                                   StopCondition.BOUND_REACHED)
        outcome = _refusal(core.close_goal_activation,
                           activation.activation_id,
                           StopCondition.BOUND_REACHED)
        return core, {"door_refused": outcome["refused"]}

    if operation == "goal_stop_condition":
        examination = _found_and_examine(core)
        activation = core.open_goal_activation(
            examination, BoundKind.EXAMINATION_BOUND, 1)
        closed = core.close_goal_activation(activation.activation_id,
                                            StopCondition.NO_PROGRESS)
        recorded = getattr(closed, "stop_condition", None)
        return core, {"stop_condition": getattr(recorded, "value", "") or ""}

    if operation == "goal_serial_attention":
        # **SERIAL ATTENTION IS PER-GOAL, AND THIS SEQUENCE WAS CORRECTED BY
        # MEASUREMENT RATHER THAN REASONED INTO PLACE.**
        #
        # The first draft examined twice and opened twice, and the second open
        # SUCCEEDED - which read like a missing guard and was not. Ruling 73-A
        # made the ladder ROTATE (least-recently-examined before
        # oldest-unresolved), so a second examination selects a DIFFERENT goal,
        # and opening an episode against a different goal is exactly what
        # Ruling 74 permits: the law is one open episode PER GOAL, not one in
        # the system.
        #
        # So the sequence examines until the arbiter comes BACK ROUND to the
        # goal that already has an open episode, and attempts the open there.
        # Bounded by the candidate count (+1 for the rotation that returns), so
        # it terminates whatever the field size - Ruling 4's declared bound
        # rather than a `while True` that happens to exit.
        first = _found_and_examine(core)
        core.open_goal_activation(first, BoundKind.EXAMINATION_BOUND, 2)

        target, attempts = first.selected_goal_id, len(first.candidate_goal_ids) + 1
        again = None
        for _ in range(attempts):
            candidate = core.examine_goals()
            if candidate.selected_goal_id == target:
                again = candidate
                break
        if again is None:
            # The rotation never returned. REPORTED as an unrefused door rather
            # than passed off as a refusal - a case that could not reach its own
            # precondition has not witnessed the law.
            return core, {"door_refused": False}

        outcome = _refusal(core.open_goal_activation, again,
                           BoundKind.EXAMINATION_BOUND, 2)
        return core, {"door_refused": outcome["refused"]}

    return core, {}


def run_case(case: EvalCase, root: Path, seed: int) -> Dict[str, Any]:
    """Drive ONE case against a FRESH isolated AUREA. Returns per-case facts.

    Fresh state per case, deliberately: cases must not be able to affect one
    another, and a corpus whose result depended on case ORDER would be measuring
    the corpus rather than her.

    ISOLATION IS THE CALLER'S, AND IT IS CHECKED HERE. `run_corpus` performs it
    (and keeps the configured path list the footprint audit needs); this refuses
    if it did not happen.
    """
    _refuse_unisolated(root)
    random.seed(seed)

    from src.aurea_core import AureaCore

    core = AureaCore()

    # Context first, through THE SAME DOOR. A context input is a real claim
    # cycle and is measured as one - it just is not the input under test.
    #
    # **THE CONTEXT'S DISPOSITION IS STRUCTURALLY NOT THE CASE'S NOW.** Each
    # `process_input` returns its OWN result dict, and only the measured call's
    # is read - so a context cycle cannot be charged to the case even by
    # accident. Under the retired wrapper this needed an explicit slice of a
    # shared sink (`emitted[context_emits:]`), and getting that slice wrong was
    # a real mutation survivor. The key removes the whole class.
    for prior in case.context:
        core.process_input(prior)

    before = _ledger_sizes(core)
    result = core.process_input(case.input)

    # RULING 80: the scripted sequence, if the case names one. It runs AFTER
    # the measured claim, so the disposition under test is still that claim's -
    # an operation extends what is OBSERVED, never what is being judged.
    observed_core, extra = _operate(case, core, result)

    facts = _observe_facts(observed_core, result, before, extra)
    observed_path = _disposition(result)

    return {
        **case.as_dict(),
        "observed_path": observed_path,
        # KEPT as a one-element tuple rather than deleted: the report's shape
        # survives the wrapper's retirement, and a future ruling that wants the
        # full emit sequence back has somewhere to put it. See the module
        # docstring for what the retirement cost.
        "emitted_paths": [observed_path] if observed_path else [],
        "observed_facts": facts,
        "claim_id": result.get("claim_id"),
        "expectation_deltas": _deltas(case, observed_path, facts),
    }


def _git_hash() -> str:
    """The commit this ran at, READ rather than remembered (pin (h))."""
    try:
        done = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, timeout=30)
        return done.stdout.strip() if done.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def _blob_hash(path: Path) -> str:
    """The corpus's git blob hash - the same value CI holds byte-for-byte."""
    try:
        done = subprocess.run(["git", "hash-object", str(path)], cwd=REPO,
                              capture_output=True, text=True, timeout=30)
        return done.stdout.strip() if done.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def run_corpus(corpus: Optional[Path] = None, seed: int = 42,
               root: Optional[Path] = None) -> Dict[str, Any]:
    """Run every case and build the report."""
    corpus = Path(corpus) if corpus is not None else SEED_CORPUS
    cases = load_corpus(corpus)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    root = Path(root) if root is not None else Path(
        tempfile.mkdtemp(prefix=f"aurea_eval_{stamp}_"))
    root.mkdir(parents=True, exist_ok=True)

    shared_before = _shared_runtime_listing()
    seeds_before = _seed_hashes()

    rows: List[Dict[str, Any]] = []
    configured: List[str] = []
    for index, case in enumerate(cases):
        case_root = root / f"case_{index:03d}_{case.case_id}"
        case_root.mkdir(parents=True, exist_ok=True)
        configured = isolate(case_root)
        rows.append(run_case(case, case_root, seed))

    shared_after = _shared_runtime_listing()
    seeds_after = _seed_hashes()
    audit = footprint_audit(configured, root, shared_before, shared_after)
    # The per-case roots live under `root`, so the audit's root-containment
    # check covers them; `configured` holds the LAST case's paths, which is what
    # that check needs a sample of.

    with_deltas = [r["case_id"] for r in rows if r["expectation_deltas"]]

    return {
        "instrument": "scripts/evaluate.py (Ruling 77, Docket R)",
        "generated_at": datetime.now().isoformat(),
        "git_hash": _git_hash(),
        "corpus": {"path": str(corpus), "blob": _blob_hash(corpus),
                   "cases": len(cases)},
        "parameters": {"seed": seed, "root": str(root)},
        "isolation": {"configured_paths": len(configured), "root": str(root)},
        # RULING 67: the audit RESULT as a REQUIRED FIELD. A run without its
        # audit is visibly incomplete rather than indistinguishable from a clean
        # one, and `compare`-shaped consumers refuse it.
        "footprint_audit": audit,
        "seeds": {"before": seeds_before, "after": seeds_after,
                  "identical": seeds_before == seeds_after},
        # THE DETERMINISM SUBJECT (EL5). Everything above this key carries a
        # timestamp, a temp path or a commit hash and is deliberately NOT part
        # of the compared surface; `cases` holds only observed facts.
        "cases": rows,
        # PER-CASE FACTS AND A LIST OF IDS. **NO RATE, NO SCORE, NO TALLY OF
        # QUALITY** (EL1) - `zero_deltas` is a property, and `cases_with_deltas`
        # points at findings so a reader can go and look at them.
        "zero_deltas": not with_deltas,
        "cases_with_deltas": with_deltas,
    }


def canonical_cases(report: Dict[str, Any]) -> str:
    """The determinism subject as canonical JSON (EL5, pin (c))."""
    return json.dumps(report["cases"], sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUREA evaluation surface (Docket R). An observation "
                    "instrument: it changes nothing, grants nothing, and "
                    "reports what it sees.")
    parser.add_argument("--corpus", default=None,
                        help="case corpus (default: the tracked seed corpus). "
                             "An external Foundry corpus runs unmodified.")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed, recorded in the report")
    parser.add_argument("--out", default=None,
                        help="where the report lands (default: reports/eval/)")
    args = parser.parse_args(argv)

    out = Path(args.out) if args.out else (
        DEFAULT_REPORT_DIR /
        f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    _refuse_if_shared_out(out)

    try:
        report = run_corpus(corpus=args.corpus, seed=args.seed)
    except (EvalCaseError, SoakIsolationError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False,
                              sort_keys=True), encoding="utf-8")

    audit = report["footprint_audit"]
    print(f"\nevaluation complete: {report['corpus']['cases']} cases "
          f"-> {out}")
    print(f"  footprint audit: {'PASS' if audit['pass'] else 'FAIL'} "
          f"({audit['configured_paths']} paths, "
          f"{len(audit['foreign_writes'])} foreign write(s))")
    for row in report["cases"]:
        mark = "  ok" if not row["expectation_deltas"] else "DELTA"
        print(f"  [{mark}] {row['case_id']:<10} {row['category']:<24} "
              f"{row['observed_path']}")
        for delta in row["expectation_deltas"]:
            print(f"          {delta}")

    if not audit["pass"]:
        # RULING 67: audit failure FAILS THE RUN LOUDLY, never silently
        # annotates a report someone will later read as clean.
        print(f"REFUSED: footprint audit FAILED - this run wrote into shared "
              f"state: {audit['foreign_writes']}", file=sys.stderr)
        return 2
    return 0 if report["zero_deltas"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
