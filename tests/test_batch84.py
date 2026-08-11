"""
test_batch84.py - BATCH 84, RULING 84: THE SOURCE FIELD RETIRES.

    The suspension record stops carrying a manufactured origin string beside
    its honest join.

`SuspensionEntry.source` was `Echo.source`'s exact pre-Ruling-68 profile: a
free-text origin on a DURABLE record with **ZERO logic readers anywhere in
`src/`** - three serializers wrote it out, three loaders read it back, and no
code ever decided anything by it. Ruling 83 censused all seventeen of its call
sites and found NO class-(b) site, because Ruling 68's replacement (DELETION,
with origin reached through the join) was barred to that pass. This is the
ruling it waited for, and the form is Ruling 68's: **deleted as SHAPE.**

THE REPLACEMENT ALREADY EXISTED. Ruling 76 gave the record `claim_id` - a join
into the claim-ancestry ledger, populated by the pipeline door and honestly
`None` everywhere else. A demoted display string sitting beside an honest join
is not harmless: **it is the field people read while the join is the one that
is true.**

ERA HONESTY FALLS OUT BY CONSTRUCTION, WHICH IS WHY NO TOLERANT-LOAD FILTER WAS
ADDED. All three loaders read EXPLICIT keys rather than splatting the dict
(`Echo(**data)`'s shape, which is why Ruling 75 needed a filter), so a legacy
file's `source` key is simply never consulted. The bytes are never rewritten in
place, and the key never round-trips back out. Pin (b) drives that rather than
assuming it.

WHERE THE MIGRATIONS LIVE (Ruling-14 form, old text kept verbatim at each site):
`tests/test_ril.py` (the `_FakeCSA` double's captured call - STRENGTHENED to
assert the key's absence), `tests/test_ruling65.py`, `tests/test_ruling76.py`
(x5, one of them STRENGTHENED - see its docstring: the old keyword-only pin
raised on ARITY and would have passed even if `claim_id` were positional), and
`tests/test_suspension_capacity.py` (the `_MinimalSuspension` double plus its
positional calls).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.suspension.suspension_base import (
    SuspensionEntry,
    SuspensionSystem,
    SuspensionType,
)
from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"

DOOR_MODULES = {
    "src/suspension/suspension_base.py": "SuspensionSystem",
    "src/suspension/black_sphere.py": "BlackSphere",
    "src/suspension/csa.py": "CSA",
    "src/suspension/veiled_thread.py": "VeiledThread",
}


def _tree(rel: str) -> ast.Module:
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


def _pyfiles():
    for p in sorted(SRC.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        yield p


# =====================================================================
# (a) THE FIELD AND THE PARAMETER ARE GONE - BY AST, NOT BY CONVENTION
# =====================================================================

def test_a_the_suspension_entry_has_no_source_field():
    """PIN (a). The field is DELETED from the shared record.

    Driven at the TYPE, not through a door: `SuspensionEntry` is constructed
    directly in three loaders and in test doubles, so a field surviving on the
    dataclass while the doors stopped passing it would leave the manufactured
    string one keyword away from returning.
    """
    entry_class = next(
        n for n in ast.walk(_tree("src/suspension/suspension_base.py"))
        if isinstance(n, ast.ClassDef) and n.name == "SuspensionEntry")
    fields = [n.target.id for n in entry_class.body
              if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]

    assert "source" not in fields, (
        "RULING 84: `SuspensionEntry.source` is deleted as SHAPE")
    assert "claim_id" in fields, (
        "RULING 76's join is the replacement and must remain")

    with pytest.raises(TypeError):
        SuspensionEntry(id="X", content="c", source="anything",
                        suspension_type=SuspensionType.CSA, pressure_level=0.1)


@pytest.mark.parametrize("rel,cls", sorted(DOOR_MODULES.items()))
def test_a_no_suspension_door_declares_a_source_parameter(rel, cls):
    """PIN (a). The parameter is gone from ALL FOUR doors - the abstract base
    and the three organs that implement it.

    The base is included deliberately: an abstract signature that still
    declared `source` would be a standing invitation for the next
    `SuspensionSystem` subclass to reintroduce the field.
    """
    door = next(
        f for n in ast.walk(_tree(rel))
        if isinstance(n, ast.ClassDef) and n.name == cls
        for f in n.body
        if isinstance(f, ast.FunctionDef) and f.name == "suspend")
    args = door.args
    names = [a.arg for a in
             (*args.posonlyargs, *args.args, *args.kwonlyargs)]

    assert "source" not in names, (
        f"RULING 84: {cls}.suspend must not declare `source` - got {names}")


def test_a_nothing_in_src_passes_source_into_a_suspension_door():
    """PIN (a). The CALL-SITE half, tree-wide by AST.

    Deleting the parameter makes a `source=` kwarg a `TypeError`, so this is
    belt-and-braces for the KEYWORD form - but it is the only guard that
    catches a POSITIONAL reintroduction, where a caller passing an identity
    string as the second positional would now bind it silently to `pressure`.
    """
    offenders = []
    for path in _pyfiles():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "suspend"):
                continue
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            for kw in node.keywords:
                if kw.arg == "source":
                    offenders.append(f"{rel}:{node.lineno} source= kwarg")
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                offenders.append(
                    f"{rel}:{node.lineno} string as 2nd positional "
                    f"({node.args[1].value!r}) - binds to `pressure`")

    assert offenders == [], (
        "RULING 84: a suspension door was handed an origin string: " +
        "; ".join(offenders))


def test_a_the_scanner_in_the_previous_test_actually_fires():
    """PIN (a). **A GUARD NEVER OBSERVED TO FIRE IS A COMMENT.**

    Feeds the scanner both forbidden shapes and a benign control, so a future
    edit that silently stops it matching is caught here rather than by the
    guard passing forever.
    """
    def scan(text):
        found = []
        for node in ast.walk(ast.parse(text)):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "suspend"):
                continue
            for kw in node.keywords:
                if kw.arg == "source":
                    found.append("kwarg")
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                found.append("positional")
        return found

    assert scan("self.csa.suspend(content=c, source='RIL', pressure=1.0)") == ["kwarg"]
    assert scan("sphere.suspend('a paradox', 'pipeline', 0.9)") == ["positional"]
    # CONTROLS: the honest post-ruling forms, and a `source=` on a DIFFERENT
    # receiver - `record_pressure` is the pressure monitor's own vocabulary and
    # was never in this ruling's scope.
    assert scan("sphere.suspend(content=c, pressure=0.9)") == []
    assert scan("sphere.suspend('a paradox', 0.9)") == []
    assert scan("self.pressure_monitor.record_pressure(source='echonet')") == []


def test_a_nothing_in_src_reads_source_off_a_suspension_entry():
    """PIN (a). **THE CENSUS RESULT, MADE A STANDING GUARD.**

    The whole licence for this deletion was that `SuspensionEntry.source` had
    ZERO logic readers - only three serializer writes and three loader reads,
    all of which are gone. This is Ruling 68's consumer-set pin in its
    suspension spelling: it reddens on the first `entry.source` or
    `entry_dict['source']` anywhere under `src/suspension/`, which is where any
    revival would have to begin.
    """
    readers = []
    for path in sorted((SRC / "suspension").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and node.attr == "source":
                readers.append(f"{rel}:{node.lineno} .source")
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                    and node.slice.value == "source":
                readers.append(f"{rel}:{node.lineno} ['source']")

    assert readers == [], (
        "RULING 84: the suspension layer read `source` again: " +
        "; ".join(readers))


# =====================================================================
# (b) ERA HONESTY - a legacy file LOADS, and the key does not round-trip
# =====================================================================

def _legacy_black_sphere(path):
    path.write_text(json.dumps({
        "entries": [{
            "id": "BS-legacy", "content": "old paradox", "source": "pipeline",
            "pressure_level": 0.9, "timestamp": "2026-01-01T00:00:00",
            "reason": "", "orbit_stability": 1.0,
            "paradox_family": "self_reference",
            "gravitational_influence": 0.27, "access_count": 0,
            "last_accessed": None, "metadata": {}, "claim_id": "CLM-0007",
        }],
        "paradox_families": {},
    }), encoding="utf-8")


def _legacy_csa(path):
    path.write_text(json.dumps([{
        "id": "CSA-legacy", "content": "old danger", "source": "SBSRE",
        "pressure_level": 0.8, "timestamp": "2026-01-01T00:00:00",
        "reason": "", "quarantine_level": "TOXIC", "decay_score": 80.0,
        "dormancy_cycles": 0, "access_count": 0, "last_accessed": None,
        "linked_scars": [], "metadata": {},
    }]), encoding="utf-8")


def _legacy_veiled(path):
    path.write_text(json.dumps([{
        "id": "VT-legacy", "content": "old ferment", "source": "DEE",
        "pressure_level": 0.6, "timestamp": "2026-01-01T00:00:00",
        "reason": "", "fermentation_cycles": 3, "emergence_potential": 0.3,
        "doctrine_candidate": False, "resonance_scores": {},
        "access_count": 0, "last_accessed": None, "linked_scars": [],
        "metadata": {},
    }]), encoding="utf-8")


LEGACY = [
    ("black_sphere", BlackSphere, _legacy_black_sphere, "BS-legacy"),
    ("csa", CSA, _legacy_csa, "CSA-legacy"),
    ("veiled_thread", VeiledThread, _legacy_veiled, "VT-legacy"),
]


@pytest.mark.parametrize("name,cls,write_legacy,entry_id",
                         LEGACY, ids=[r[0] for r in LEGACY])
def test_b_a_legacy_file_carrying_source_loads_and_the_read_rewrites_nothing(
        name, cls, write_legacy, entry_id, tmp_path):
    """PIN (b). **ERA HONESTY, DRIVEN RATHER THAN ASSUMED.**

    A file written before this ruling carries `source`. It must LOAD - the
    entry is admitted whole - the key must be ABSENT from the reconstructed
    record, and the READ must not touch the bytes. Ruling 68's forensic law:
    the record keeps everything, the OBJECT holds the current schema.
    """
    path = tmp_path / f"{name}.json"
    write_legacy(path)
    before = path.read_bytes()

    store = cls(filepath=str(path))

    assert entry_id in store.entries, (
        "a legacy suspension file must still load")
    entry = store.entries[entry_id]
    assert not hasattr(entry, "source"), (
        "the legacy key reached the reconstructed record")
    assert path.read_bytes() == before, (
        "a READ rewrote the record - the bytes are forensic")


@pytest.mark.parametrize("name,cls,write_legacy,entry_id",
                         LEGACY, ids=[r[0] for r in LEGACY])
def test_b_the_legacy_key_does_not_round_trip_back_out(
        name, cls, write_legacy, entry_id, tmp_path):
    """PIN (b). The other half, and the one that matters: **tolerated on read,
    NEVER round-tripped back out.**

    A loader that ignored the key while the serializer still wrote it would
    leave the field alive on disk forever, regenerated from a default.
    """
    path = tmp_path / f"{name}.json"
    write_legacy(path)
    cls(filepath=str(path)).save_to_file()

    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)
    entries = payload["entries"] if isinstance(payload, dict) else payload

    assert len(entries) == 1, "the legacy entry was lost on rewrite"
    assert "source" not in entries[0], (
        "RULING 84: the retired key was written back out")


def test_b_a_legacy_black_sphere_keeps_its_ruling_76_join(tmp_path):
    """PIN (b) x (d). The deletion is SURGICAL: the legacy file above also
    carries `claim_id`, and that join must survive the same load untouched.
    Removing a field beside a join is exactly where a join gets removed by
    accident."""
    path = tmp_path / "bs.json"
    _legacy_black_sphere(path)
    store = BlackSphere(filepath=str(path))
    assert store.entries["BS-legacy"].claim_id == "CLM-0007"


# =====================================================================
# (c) A NEW FILE CARRIES NO KEY, THROUGH THE REAL DOORS
# =====================================================================

def test_c_a_new_black_sphere_file_carries_no_source_key(tmp_path):
    """PIN (c). Written through the real door, read back as raw JSON."""
    path = tmp_path / "bs.json"
    sphere = BlackSphere(filepath=str(path))
    entry = sphere.suspend(content="This sentence is false.", pressure=0.9,
                           reason="self-reference", claim_id="CLM-0001")

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "source" not in payload["entries"][0]
    assert payload["entries"][0]["claim_id"] == "CLM-0001"

    reloaded = BlackSphere(filepath=str(path))
    assert reloaded.entries[entry.id].claim_id == "CLM-0001"


def test_c_a_new_csa_file_carries_no_source_key(tmp_path):
    """PIN (c). CSA's door takes no `claim_id` today (Ruling 76 populated only
    the Black Sphere's pipeline door), so this asserts the deletion alone."""
    path = tmp_path / "csa.json"
    store = CSA(filepath=str(path))
    entry = store.suspend(content="volatile", pressure=0.8, reason="test")

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "source" not in payload[0]
    assert CSA(filepath=str(path)).entries[entry.id].content == "volatile"


def test_c_a_new_veiled_thread_file_carries_no_source_key(tmp_path):
    """PIN (c)."""
    path = tmp_path / "vt.json"
    store = VeiledThread(filepath=str(path))
    entry = store.suspend(content="unresolved", pressure=0.6, reason="test")

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "source" not in payload[0]
    assert VeiledThread(filepath=str(path)).entries[entry.id].content == "unresolved"


# =====================================================================
# (d) THE RULING 76 JOIN IS UNTOUCHED - re-asserted, never weakened
# =====================================================================

def test_d_the_pipeline_door_still_populates_the_claim_id_join():
    """PIN (d). Ruling 76's headline property, re-asserted end to end through
    the real pipeline after the field beside it was removed.

    **THIS IS THE PIN THAT WOULD CATCH THE WORST OUTCOME OF THIS RULING:** the
    call site that passed `source='pipeline'` is the same call site that passes
    `claim_id`, so a careless deletion there takes the join with it.
    """
    from src.aurea_core import AureaCore

    core = AureaCore()
    result = core.process_input("This statement is false.")
    if not core.black_sphere.entries:
        pytest.skip("this claim did not suspend into the Black Sphere")

    entry = next(iter(core.black_sphere.entries.values()))
    assert entry.claim_id == result["claim_id"]
    assert entry.claim_id == result["echo"].claim_id


def test_d_non_pipeline_suspensions_still_carry_none(tmp_path):
    """PIN (d). ABSENT is still a real answer: the tether's suspensions have no
    claim cycle behind them, and removing `source` must not tempt anything into
    synthesizing a join to replace it."""
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    assert sphere.suspend(content="tether paradox", pressure=0.9).claim_id is None

    csa = CSA(filepath=str(tmp_path / "csa.json"))
    assert csa.suspend(content="tether danger", pressure=0.7).claim_id is None

    vt = VeiledThread(filepath=str(tmp_path / "vt.json"))
    assert vt.suspend(content="tether ferment", pressure=0.5).claim_id is None


def test_d_the_base_door_contract_still_binds_its_three_organs():
    """PIN (d). All three organs remain concrete `SuspensionSystem`s after the
    abstract signature changed - i.e. the base and the implementations moved
    TOGETHER. A base whose signature drifted from its subclasses is how an
    abstract door stops meaning anything."""
    for cls in (BlackSphere, CSA, VeiledThread):
        assert issubclass(cls, SuspensionSystem)
        assert not getattr(cls.suspend, "__isabstractmethod__", False)
