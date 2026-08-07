"""
test_batch66.py - BATCH 66: Rulings 66 + 67, the record-integrity batch.

RULING 66 - a record either holds what was presented or refuses it; there is no
third thing where it silently holds something else.
RULING 67 - an instrument that measures her audits its own footprint.

WHERE THE REST OF THIS BATCH'S PINS LIVE, AND WHY THEY ARE NOT DUPLICATED HERE:
`tests/test_verification_pass.py` carries the five collected witnesses this
batch closes. They were written against the DEFECT at `0b2072c`, they carry its
measured values, and Batch 66 migrated them in Ruling-14 form rather than
copying their assertions into a new file. Pin (d) - the load-bearing gate-order
witness - is
`test_verification_pass.py::test_the_bytearray_proof_moves_nothing_and_poisons_nothing`.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.utils.record_value import (
    CANONICAL_CONTAINER_TYPES, CANONICAL_LEAF_TYPES, NonCanonicalRecordValue,
    validate_record_value)

REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "src" / "utils" / "record_value.py"


# =====================================================================
# (b) THE VALIDATOR'S OWN PINS, AT ITS OWN HOME
#
# Ruling 63's survivor lesson as STANDING FORM: a shared helper guarded only
# through its consumers is guarded by accident. That pass shipped a hoisted
# `deep_freeze` whose dict rebuild and sequence rebuild could each be deleted
# without a single test in its own file noticing.
# =====================================================================

def test_the_admissible_set_is_declared_as_data():
    """RULING 66 res.1: the closed set is DECLARED, not described in prose.

    Pinned against the DECLARATION rather than a second hand-written copy - a
    duplicated vocabulary in the harness is the drift hazard Ruling 47
    consolidated `CMTE_FAILURE_LABELS` to close.
    """
    assert set(CANONICAL_LEAF_TYPES) == {str, bool, int, float, type(None)}
    assert set(CANONICAL_CONTAINER_TYPES) == {list, dict}


@pytest.mark.parametrize("value", [
    "text", "", True, False, None, 0, -1, 10**30, 0.0, -1.5, 3.14,
    [], {}, [1, "a", None, True], {"k": [{"deep": 1.0}]},
], ids=lambda v: f"{type(v).__name__}:{v!r}"[:40])
def test_every_admissible_shape_is_accepted(value):
    """The positive half. Without it a validator that refused EVERYTHING would
    satisfy every refusal pin in this file."""
    validate_record_value(value)


@pytest.mark.parametrize("value,label", [
    (bytearray(b"raw"), "bytearray"),
    (b"raw", "bytes"),
    ({1, 2}, "set"),
    (frozenset({1}), "frozenset"),
    ((1, 2), "tuple"),
    (object(), "object"),
    (float("nan"), "nan"),
    (float("inf"), "inf"),
    (float("-inf"), "-inf"),
])
def test_every_inadmissible_shape_is_refused(value, label):
    """The bytearray form is FIRST in this table by standing requirement (the
    fifty-eighth entry), and `tuple` is here deliberately: `json.dumps` would
    serialize it happily as an array, so nothing else in the stack would refuse
    it. A record's containers are `list` and `str`-keyed `dict`, and the
    serialized payloads this runs over have already converted (`as_dict` thaws
    Ruling 52's frozen tuples back to lists)."""
    with pytest.raises(NonCanonicalRecordValue):
        validate_record_value(value)


def test_the_refusal_carries_the_key_path_of_a_NESTED_offender():
    """RULING 66 res.1 - **A REFUSAL THAT CANNOT SAY WHERE IT REFUSED IS HALF A
    REFUSAL**, and this is the pin that makes that real.

    Witnessed AT DEPTH, through both container kinds, because a validator that
    reported only the root would be indistinguishable from one that worked on
    the flat payloads every other test here uses - and the witnessed defect hid
    ONE bytearray inside a nested proof.
    """
    payload = {"proof": {"core": {"items": [{"ok": 1}, {"blob": bytearray(b"x")}]}}}

    with pytest.raises(NonCanonicalRecordValue) as caught:
        validate_record_value(payload, path="root")

    assert caught.value.path == "root.proof.core.items[1].blob", caught.value.path
    assert caught.value.offending_type == "bytearray"
    assert "root.proof.core.items[1].blob" in str(caught.value)


def test_a_non_string_dict_key_is_refused_at_the_key():
    """The fabrication one level UP, and it was MEASURED at `0b2072c`: `{1: "x"}`
    persisted as `{"1": "x"}`, so the record claimed a string key was presented.
    Refused AT the key, and the path names it."""
    with pytest.raises(NonCanonicalRecordValue) as caught:
        validate_record_value({"outer": {1: "x"}})
    assert caught.value.path == "root.outer[1]"
    assert caught.value.offending_type == "int"


def test_a_non_finite_float_says_the_value_not_only_the_type():
    """The one case where the TYPE is admissible and the VALUE is not, so naming
    only `float` would read as a contradiction of the declared leaf set."""
    with pytest.raises(NonCanonicalRecordValue) as caught:
        validate_record_value({"f": float("nan")})
    assert "not finite" in str(caught.value)
    assert caught.value.offending_type == "float"


def test_the_validator_does_not_mutate_its_input():
    """RULING 66 res.1: PURE. Pinned after a refusal AND after a success, on a
    payload deep enough that an in-place 'helpful' conversion would show."""
    import copy
    payload = {"a": [1, {"b": ["x", bytearray(b"z")]}], "c": {"d": 2.0}}
    snapshot = copy.deepcopy(payload)

    with pytest.raises(NonCanonicalRecordValue):
        validate_record_value(payload)
    assert payload == snapshot, "the input was mutated during a refusal"
    assert type(payload["a"][1]["b"][1]) is bytearray, "a leaf was coerced"

    clean = {"a": [1, {"b": ["x"]}]}
    snapshot = copy.deepcopy(clean)
    validate_record_value(clean)
    assert clean == snapshot


def test_the_module_defines_no_coercion_path():
    """RULING 66 res.1 AS SHAPE - **REFUSAL, NEVER COERCION.**

    There is deliberately no `sanitize`/`coerce`/`to_canonical` variant that
    returns a cleaned copy. The moment one exists, a caller under deadline uses
    it and the fabrication is back - so its absence is pinned rather than
    requested. CLAUDE.md §3: the wrong path must be UNEXECUTABLE.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    forbidden = {"sanitize", "coerce", "to_canonical", "canonicalize",
                 "clean", "coerce_record_value", "sanitize_record_value"}
    assert not (defined & forbidden), (
        f"a coercion path appeared: {sorted(defined & forbidden)}")


# =====================================================================
# (c) STRUCTURAL, AST - THE WRITERS
# =====================================================================

def _writer_calls():
    """Every `json.dumps` / `json.dump` / `atomic_write_json` call in `src/`."""
    for path in sorted((REPO / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = None
            if (isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("dumps", "dump")
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "json"):
                name = f"json.{node.func.attr}"
            elif isinstance(node.func, ast.Name) and node.func.id == "atomic_write_json":
                name = "atomic_write_json"
            if name:
                rel = path.relative_to(REPO).as_posix()
                kwargs = {k.arg for k in node.keywords}
                yield rel, node.lineno, name, kwargs


# ~~EchoMemory is Ruling 66's NAMED FUTURE CONSUMER, declared OUT of this batch.
# The exemption is NOT a convenience: the batch's sweep tried removing
# `default=str` there and the suite answered at once - it is the ONE store in
# `src/` where it is LOAD-BEARING, because `add_echo` serializes `echo.__dict__`
# RAW and `created_at` arrives as a live `datetime`. Every other store converts
# through its own `_to_dict`/`.isoformat()` first. Removing it there is a real
# migration with a schema decision in it, which is the wiring ruling's to make.~~
#
#     ~~_DECLARED_OUT = {("src/utils/echo_memory.py", "json.dumps")}~~
#
# **THE EXEMPTION IS DISCHARGED 2026-08-05 BY RULING 75**, old text kept
# verbatim because it is the record of what was reserved and to whom. Batch 66
# named the wiring ruling as the one that would make the schema decision; that
# ruling landed and made it: `EchoMemory` now serializes EXPLICITLY, field by
# field, with `created_at` converted through `.isoformat()` - so `default=str`
# has nothing left to do and is GONE.
#
# **THE SET IS NOW EMPTY, AND THAT MATTERS MORE THAN THE ONE ENTRY LEAVING IT.**
# An exemption that outlives the condition it was granted for makes the scan
# TRUE BY OMISSION for that file - the completeness-claim defect, in the one
# instrument built to sweep every writer in `src/`. With the set empty the sweep
# genuinely covers all of them, which is what it always claimed to do.
_DECLARED_OUT: set = set()


def test_no_store_writer_carries_a_default_escape_hatch():
    """RULING 66 res.2 - `default=` is what turned a bytearray into a lie.

    Scanned across ALL of `src/`, not a named list: the sweep that produced this
    batch found NINE `default=str` sites the ruling never named, so a pin over
    an enumerated list would go green while the next one was added elsewhere.
    """
    offenders = [f"{rel}:{line} {name}" for rel, line, name, kwargs in _writer_calls()
                 if "default" in kwargs and (rel, name) not in _DECLARED_OUT]
    assert not offenders, (
        "a store writer can still silently stringify what it cannot hold:\n"
        + "\n".join(offenders))


def test_every_direct_json_writer_refuses_non_finite_floats():
    """RULING 66 res.2 - `allow_nan=False` at every direct write.

    NaN and Infinity are written as bare non-standard constants that no
    conforming parser in another language will read, and `default=` never sees
    them - so this is a SEPARATE half of the ruling, not a restatement of the
    one above. `atomic_write_json` callers are exempt because the funnel sets it
    (pinned below); a caller passing it explicitly would be a duplicate-keyword
    `TypeError`.
    """
    offenders = [f"{rel}:{line}" for rel, line, name, kwargs in _writer_calls()
                 if name.startswith("json.")
                 and rel != "src/utils/atomic_write.py"
                 and "allow_nan" not in kwargs
                 and (rel, name) not in _DECLARED_OUT]
    assert not offenders, (
        "a direct json writer can still emit NaN/Infinity:\n" + "\n".join(offenders))


def test_the_atomic_funnel_sets_allow_nan_false_and_it_is_not_overridable():
    """THE FUNNEL CALL, and why it was chosen over thirteen call sites.

    Thirteen disciplined call sites are thirteen chances to forget; one funnel
    is a property, and it stays true for the fourteenth caller nobody has
    written yet. `allow_nan=False` is passed BEFORE `**dump_kwargs`, so a caller
    supplying its own gets a duplicate-keyword `TypeError` - unexecutable rather
    than discouraged.
    """
    source = (REPO / "src" / "utils" / "atomic_write.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "dumps"]
    assert len(calls) == 1, "atomic_write_json must serialize in exactly one place"
    kwargs = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert kwargs.get("allow_nan") == "False", kwargs
    assert "default" not in kwargs

    # And it BINDS, not merely appears.
    from src.utils.atomic_write import atomic_write_json
    import tempfile
    target = Path(tempfile.mkdtemp()) / "x.json"
    with pytest.raises(ValueError):
        atomic_write_json(target, {"f": float("nan")})
    assert not target.exists(), "a refused payload must leave no file"


def test_the_writer_scanner_actually_sees_violations():
    """THE SCANNER'S OWN CONTROL - Ruling 32's answer to the vacuous pin.

    A scan that passes because it cannot see is worth nothing. The same
    extraction logic is fed both forbidden shapes and must flag each.
    """
    for source, missing in (
        ("import json\njson.dumps(x, default=str)\n", "default"),
        ("import json\njson.dumps(x)\n", "allow_nan"),
    ):
        tree = ast.parse(source)
        found = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "dumps"):
                kwargs = {k.arg for k in node.keywords}
                if missing == "default" and "default" in kwargs:
                    found.append(node)
                if missing == "allow_nan" and "allow_nan" not in kwargs:
                    found.append(node)
        assert found, f"the scanner is blind to a {missing} violation"


# =====================================================================
# (f) RULING 67 - THE INSTRUMENT AUDIT
# =====================================================================

def test_both_instruments_report_a_footprint_audit():
    """RULING 67: the audit result is a REQUIRED FIELD of the report schema.

    Asserted STRUCTURALLY on both instruments, because the alternative - running
    a 200-cycle soak inside the unit suite - is not a test, it is a second soak.
    """
    for rel in ("scripts/soak.py", "scripts/differential.py"):
        source = (REPO / rel).read_text(encoding="utf-8")
        assert '"footprint_audit"' in source, (
            f"{rel} does not carry the audit in its report schema")


def test_a_clean_run_reports_zero_foreign_writes(tmp_path):
    """THE POSITIVE DIRECTION, against a SENTINEL shared store.

    A file is planted in the listing that stands for shared `data/runtime/`; an
    audit that reported foreign writes for an untouched store would be useless
    noise, and one that reported none because it never looked is the defect.
    """
    from scripts.soak import footprint_audit
    listing = ["logs/claim_ancestry.jsonl", "sae_epoch.json"]
    result = footprint_audit([str(tmp_path / "a.json")], tmp_path,
                             listing, list(listing))
    assert result["performed"] is True
    assert result["pass"] is True
    assert result["foreign_writes"] == []


def test_an_audit_fails_loudly_when_the_instrument_writes_into_shared_state(tmp_path):
    """THE INCIDENT, AS A PIN. **This is the exact shape that happened:** the
    differential harness wrote 39 ancestry lines into shared `data/runtime/`
    while the audited soak refused the same contamination in the same session.

    The audit must FAIL and must NAME the file - a boolean alone would send the
    next investigation back to a manual directory diff.
    """
    from scripts.soak import footprint_audit
    before = ["sae_epoch.json"]
    after = ["sae_epoch.json", "logs/claim_ancestry.jsonl"]
    result = footprint_audit([str(tmp_path / "a.json")], tmp_path, before, after)

    assert result["pass"] is False
    assert result["foreign_writes"] == ["logs/claim_ancestry.jsonl"]


def test_a_configured_path_outside_the_run_root_fails_the_audit(tmp_path):
    """The other half of a footprint: not only what APPEARED, but whether the
    instrument was ever pointed outside its sandbox to begin with."""
    from scripts.soak import footprint_audit
    result = footprint_audit([str(REPO / "data" / "runtime" / "x.json")],
                             tmp_path, [], [])
    assert result["pass"] is False
    assert result["configured_outside_root"]


def test_the_comparison_refuses_a_report_whose_audit_is_absent_or_failing():
    """RULING 67's TEETH: audit failure FAILS the run, never silently annotates.

    A contaminated measurement compared against a clean one produces a diff that
    looks like a finding, so `compare()` refuses both shapes - the report that
    never audited, and the report that audited and failed.
    """
    from scripts.differential import compare
    from scripts.soak import SoakIsolationError

    clean = {"footprint_audit": {"performed": True, "pass": True},
             "non_topology": {"claims": []}, "topology": {}}
    no_audit = {"non_topology": {"claims": []}, "topology": {}}
    failed = {"footprint_audit": {"performed": True, "pass": False,
                                  "foreign_writes": ["logs/x.jsonl"]},
              "non_topology": {"claims": []}, "topology": {}}

    with pytest.raises(SoakIsolationError, match="no footprint audit"):
        compare(no_audit, clean)
    with pytest.raises(SoakIsolationError, match="FAILED"):
        compare(clean, failed)

    # And a clean pair compares without complaint.
    assert compare(clean, clean)["non_topology_zero_movement"] is True
