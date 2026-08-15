"""
test_m4_highwater.py - M4-β': THE HIGH-WATER ENVELOPE.

    **A MINT THAT DERIVES FROM SURVIVING ENTRIES REISSUES THE IDS OF THE DEAD.**

The M4-α pass STOPPED M4-β on a witnessed premise defect: the three suspension
stores are SNAPSHOTS that REMOVE entries, so the file-derived mint Ruling 69 gave
the append-only ledgers is not removal-safe here. β' is the ratified remedy -
Ruling 81's counter carried INSIDE the snapshot it numbers, which is not a cached
derivation but the record itself.

RED-FIRST, AND THIS PASS HAS A REAL ONE RATHER THAN A COLLECTION ERROR. The
load-bearing pin below (`test_a_*_reissue_*`) drives the exact witnessed case -
mint three, remove the third, mint again - against a store that at `c7de747`
mints from a wall clock. It was watched in a detached worktree there, and the
watch is reported in the pass's own record: the wall-clock mint passes the
no-reissue assertion for the WRONG REASON (microsecond spacing), which is why the
harness below ALSO asserts the ordinal shape and the high-water record. Those
halves are RED at `c7de747`.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.suspension_base import (HighWaterRegression,
                                            LEGACY_ID_FORMAT,
                                            SuspensionSystem, _legacy_ordinal)
from src.suspension.veiled_thread import VeiledThread

REPO = Path(__file__).resolve().parents[1]
SUSPENSION = REPO / "src" / "suspension"


def _payload(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# Every store, its prefix, and a `suspend` call that succeeds on it.
STORES = [
    ("csa", CSA, "CSA-", lambda s: s.suspend("volatile", pressure=0.8)),
    ("veiled", VeiledThread, "VT-", lambda s: s.suspend("unresolved", pressure=0.6)),
    ("black_sphere", BlackSphere, "BS-", lambda s: s.suspend("paradox", pressure=0.9)),
]
IDS = [row[0] for row in STORES]


# =====================================================================
# (a) THE MINT NEVER DERIVES FROM SURVIVORS - the load-bearing pin
# =====================================================================

@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_a_a_removed_id_is_never_reissued(name, cls, prefix, suspend, tmp_path):
    """THE WITNESSED CASE, DRIVEN ON ALL THREE. **RED at `c7de747`.**

    Mint three, REMOVE THE THIRD, mint again. Under a derive-from-survivors mint
    the derivation falls 3 -> 2 and the fourth mint reissues the third id - which
    is exactly what was measured on `VeiledThread.extract_emerged` and
    `CSA.emergency_purge` when M4-β was stopped.

    **THE REMOVAL USED HERE IS THE INHERITED BASE DOOR**, deliberately: it is
    callable on all three including the Black Sphere, which has no removal door
    of its own. A store that is safe only because nobody calls an inherited
    public method is one line away from the defect (Ruling 35's vacuous-guard
    class), and that is why the envelope is not conditional on the store.
    """
    store = cls(filepath=str(tmp_path / f"{name}.json"))
    minted = [suspend(store).id for _ in range(3)]
    assert minted == [f"{prefix}0001", f"{prefix}0002", f"{prefix}0003"]

    store.purge_old_entries(keep_recent=0)          # the inherited door
    assert store.entries == {}, "every entry was removed"

    after = suspend(store).id
    assert after not in minted, (
        f"{cls.__name__} REISSUED {after} after it was removed. The mint must "
        f"come from the high-water record, never from surviving entries.")
    assert after == f"{prefix}0004"


def test_a_the_veiled_thread_success_path_is_the_witnessed_one(tmp_path):
    """`extract_emerged` VERBATIM - the store's own fermentation-success path,
    and the exact call the M4-α STOP measured a reissue on.

    Content that ferments and EMERGES is removed, which is the store working.
    An id reissued at that moment would name a suspension that succeeded and a
    different one that came after it.
    """
    store = VeiledThread(filepath=str(tmp_path / "vt.json"))
    ids = [store.suspend(f"c{i}", pressure=0.6).id for i in range(3)]
    assert ids[-1] == "VT-0003"

    assert store.extract_emerged("VT-0003") == "c2"
    assert store.suspend("after the emergence", pressure=0.6).id == "VT-0004"


def test_a_the_csa_emergency_purge_path_is_the_witnessed_one(tmp_path):
    """`emergency_purge(confirm=True)` VERBATIM - the other measured case.

    It removes EVERY cascade-level entry, so at cascade pressure the whole store
    empties and a derive-from-survivors mint fell to 0 and reissued `CSA-0001`.
    """
    store = CSA(filepath=str(tmp_path / "csa.json"))
    ids = [store.suspend(f"danger {i}", pressure=0.99).id for i in range(3)]
    assert ids == ["CSA-0001", "CSA-0002", "CSA-0003"]

    assert store.emergency_purge(confirm=True) == 3
    assert store.entries == {}
    assert store.suspend("after the purge", pressure=0.99).id == "CSA-0004"


def test_a_csas_update_dormancy_is_a_removal_door_the_handoff_did_not_name(
        tmp_path):
    """THE CENSUS CORRECTION, MADE EXECUTABLE.

    The handoff counted CSA's own doors as `emergency_purge` plus the inherited
    `purge_old_entries`. The AST census found a third path that is CSA's OWN:
    `update_dormancy` auto-purges entries past `max_dormancy`. It strengthens
    the ruling rather than weakening it - one more way to lose an id - so it is
    pinned rather than merely noted.
    """
    store = CSA(filepath=str(tmp_path / "csa.json"))
    store.suspend("volatile", pressure=0.8)
    store.max_dormancy = 0                      # the next tick expires it

    assert store.update_dormancy() == ["CSA-0001"]
    assert store.entries == {}
    assert store.suspend("after the expiry", pressure=0.8).id == "CSA-0002"


def test_a_check_emergence_removes_nothing_the_other_census_correction(tmp_path):
    """The handoff listed `check_emergence` as a VT removal door. **IT IS NOT** -
    it returns a bool and deletes nothing. Pinned so the corrected census is a
    fact in the tree rather than a sentence in a commit message."""
    store = VeiledThread(filepath=str(tmp_path / "vt.json"))
    entry = store.suspend("unresolved", pressure=0.6)
    store.entries[entry.id].fermentation_cycles = 999
    store.entries[entry.id].emergence_potential = 1.0

    assert store.check_emergence(entry.id) is True
    assert entry.id in store.entries, "check_emergence removes nothing"


# =====================================================================
# (b) THE HIGH-WATER MARK IS MONOTONIC AND SURVIVES THE FILE
# =====================================================================

@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_b_the_envelope_carries_the_high_water(name, cls, prefix, suspend,
                                               tmp_path):
    """The counter rides in the SAME atomic write as the entries it numbers
    (Ruling 81's form), so the two can never disagree."""
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    for _ in range(3):
        suspend(store)

    payload = _payload(path)
    assert isinstance(payload, dict)
    assert payload["high_water"] == 3
    assert len(payload["entries"]) == 3


@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_b_the_high_water_survives_a_restart_across_a_removal(
        name, cls, prefix, suspend, tmp_path):
    """THE PROPERTY THE WHOLE RULING RESTS ON, measured across a real restart:
    a store that loses every entry still knows how many ids it has issued."""
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    for _ in range(3):
        suspend(store)
    store.purge_old_entries(keep_recent=0)
    store.save_to_file()

    assert _payload(path)["entries"] == []
    assert _payload(path)["high_water"] == 3, (
        "the record of ids ISSUED cannot be lowered by removing the entries")

    resumed = cls(filepath=str(path))
    assert resumed.high_water == 3
    assert suspend(resumed).id == f"{prefix}0004"


@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_b_a_save_may_never_write_a_lower_high_water(name, cls, prefix,
                                                     suspend, tmp_path):
    """The wrong path made UNEXECUTABLE rather than discouraged (§3).

    Nothing in the pipeline can lower a high-water mark, so this is reachable
    only by assigning to it - and it RAISES rather than repairing itself to the
    floor, because a silent `max()` would hide the one state worth knowing about.
    """
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    for _ in range(3):
        suspend(store)

    store.high_water = 1                        # the programming error
    with pytest.raises(HighWaterRegression):
        store.save_to_file()

    assert _payload(path)["high_water"] == 3, "the file is untouched by a refusal"


def test_b_the_regression_guard_is_not_in_the_structural_taxonomy():
    """Ruling 48's partition, checked rather than assumed. It is unreachable
    from `process_input` - a caller assigning to a counter is a programming
    error, not one of AUREA's guards firing (Docket N's form) - and a member
    added on speculation is a decision made without a case."""
    from src.aurea_core import STRUCTURAL_VIOLATIONS
    assert HighWaterRegression not in STRUCTURAL_VIOLATIONS


@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_b_the_high_water_only_ever_rises_across_a_long_sequence(
        name, cls, prefix, suspend, tmp_path):
    """FORCING: suspends and removals interleaved, reloading throughout, with
    the mark READ FROM THE FILE at every step. A single decrease anywhere is a
    STOP, so the pin asserts the whole sequence rather than its endpoints."""
    path = tmp_path / f"{name}.json"
    observed = []
    store = cls(filepath=str(path))
    for step in range(6):
        suspend(store)
        observed.append(_payload(path)["high_water"])
        if step % 2:
            store.purge_old_entries(keep_recent=0)
            store.save_to_file()
            observed.append(_payload(path)["high_water"])
        store = cls(filepath=str(path))          # a restart every step
        observed.append(store.high_water)

    assert observed == sorted(observed), f"high_water decreased: {observed}"
    assert observed[-1] == 6


# =====================================================================
# (c) ERA-HONEST LOAD - both shapes forever, legacy ids never parse
# =====================================================================

def test_c_a_legacy_bare_list_loads_and_starts_at_zero(tmp_path):
    """CSA/VT legacy. **A PURE-LEGACY FILE HOLDS ONLY WALL-CLOCK IDS**, which do
    not parse as ordinals - so it starts at 0, and `CSA-0001` cannot collide
    with a twenty-digit id already in it."""
    path = tmp_path / "csa.json"
    legacy_id = "CSA-20260811093000123456"
    path.write_text(json.dumps([{
        "id": legacy_id, "content": "old", "pressure_level": 0.8,
        "timestamp": "2026-08-11T09:30:00", "reason": "legacy",
        "quarantine_level": "TOXIC", "decay_score": 80.0, "dormancy_cycles": 0,
        "access_count": 0, "last_accessed": None, "linked_scars": [],
        "metadata": {}, "source": "a legacy key nothing reads",
    }]) + "\n", encoding="utf-8")

    store = CSA(filepath=str(path))
    assert legacy_id in store.entries, "the legacy record loads, whole"
    assert store.high_water == 0
    assert store.suspend("new", pressure=0.8).id == "CSA-0001"
    assert legacy_id in store.entries, "and it is still there afterwards"


def test_c_a_legacy_black_sphere_dict_without_the_key_loads_and_starts_at_zero(
        tmp_path):
    """BS legacy is a DICT MISSING `high_water`, which is treated exactly as a
    bare list is: derive once, from ids that do not parse, so 0."""
    path = tmp_path / "bs.json"
    legacy_id = "BS-20260811093000123456"
    path.write_text(json.dumps({
        "entries": [{
            "id": legacy_id, "content": "old paradox", "pressure_level": 0.9,
            "timestamp": "2026-08-11T09:30:00", "reason": "legacy",
            "orbit_stability": 1.0, "paradox_family": "self_reference",
            "gravitational_influence": 0.27, "access_count": 0,
            "last_accessed": None, "metadata": {},
        }],
        "paradox_families": {"self_reference": [legacy_id]},
    }) + "\n", encoding="utf-8")

    store = BlackSphere(filepath=str(path))
    assert legacy_id in store.entries
    assert store.paradox_families["self_reference"] == {legacy_id}
    assert store.high_water == 0
    assert store.suspend("new", pressure=0.9).id == "BS-0001"


def test_c_a_legacy_file_is_not_rewritten_by_being_read(tmp_path):
    """Ruling 68's forensic law: legacy bytes are untouched and never
    reinterpreted. Only a SAVE writes the envelope."""
    path = tmp_path / "vt.json"
    path.write_text(json.dumps([]) + "\n", encoding="utf-8")
    before = path.read_bytes()

    VeiledThread(filepath=str(path))
    assert path.read_bytes() == before, "loading rewrites nothing"


def test_c_a_hand_written_ordinal_without_an_envelope_still_derives(tmp_path):
    """The derivation is not a blanket zero - it reads what it CAN read.

    A file carrying `VT-0007` and no envelope initializes at 7, so the next mint
    is 0008 rather than 0001. This is what makes the legacy bridge honest rather
    than merely convenient.
    """
    path = tmp_path / "vt.json"
    path.write_text(json.dumps([{
        "id": "VT-0007", "content": "hand written", "pressure_level": 0.6,
        "timestamp": "2026-08-11T09:30:00", "reason": "r",
        "fermentation_cycles": 0, "emergence_potential": 0.3,
        "doctrine_candidate": False, "resonance_scores": {},
        "access_count": 0, "last_accessed": None, "linked_scars": [],
        "metadata": {},
    }]) + "\n", encoding="utf-8")

    store = VeiledThread(filepath=str(path))
    assert store.high_water == 7
    assert store.suspend("next", pressure=0.6).id == "VT-0008"


def test_c_the_legacy_ordinal_parser_refuses_exactly_the_superseded_width():
    """THE DELICATE PART, PINNED DIRECTLY.

    A wall-clock id is `PREFIX` + a digit run, so a naive `\\d+` scan reads it as
    an ordinal of twenty digits and sets a high-water mark no mint could catch.
    The rejection is keyed to the SUPERSEDED FORMAT'S OWN WIDTH, derived from
    the format string - a fact about the era being replaced, not a threshold.
    """
    from datetime import datetime
    width = len(datetime(2026, 1, 1).strftime(LEGACY_ID_FORMAT))
    assert width == 20

    assert _legacy_ordinal("CSA-" + "9" * width, "CSA-") is None
    assert _legacy_ordinal("CSA-0007", "CSA-") == 7
    assert _legacy_ordinal("CSA-" + "9" * (width - 1), "CSA-") is not None, (
        "one digit short of the superseded width is an ordinal, not a clock")
    assert _legacy_ordinal("VT-0007", "CSA-") is None, "a foreign prefix"
    assert _legacy_ordinal("CSA-00x7", "CSA-") is None, "not all digits"
    assert _legacy_ordinal(None, "CSA-") is None


@pytest.mark.parametrize("name,cls,prefix,suspend", STORES, ids=IDS)
def test_c_both_shapes_round_trip_through_a_real_restart(name, cls, prefix,
                                                         suspend, tmp_path):
    """The envelope survives save -> load -> save without drifting."""
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    suspend(store)
    first = _payload(path)

    resumed = cls(filepath=str(path))
    resumed.save_to_file()
    assert _payload(path)["high_water"] == first["high_water"]
    assert len(_payload(path)["entries"]) == len(first["entries"])


# =====================================================================
# (d) SHAPE - one definition, no second reader, no wall clock left
# =====================================================================

def test_d_no_suspension_store_mints_from_a_clock():
    """AST. The three wall-clock mints are GONE AS SHAPE, not merely unused.

    A `strftime` id in any of these files would be the defect returning; the
    scanner ignores docstrings, so the base class's record of the superseded
    FORMAT (which it must know to refuse it) is not a false positive.
    """
    offenders = []
    for path in sorted(SUSPENSION.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "strftime"):
                continue
            # The base class DERIVES the superseded width from a FIXED sample
            # date; that call reads no clock and is the era-honesty rule itself.
            reads_clock = any(
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "now"
                for inner in ast.walk(node.func.value))
            if reads_clock:
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], (
        f"a suspension store mints from a wall clock at {offenders}")


def test_d_the_clock_scanner_actually_fires():
    """A guard never observed to fire is a comment (Docket P's rule)."""
    fed = ast.parse("id = f\"CSA-{datetime.now().strftime('%Y%m%d')}\"")
    hits = [n for n in ast.walk(fed)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "strftime"
            and any(isinstance(i, ast.Call) and isinstance(i.func, ast.Attribute)
                    and i.func.attr == "now" for i in ast.walk(n.func.value))]
    assert hits, "the scanner's own shape no longer matches the defect"


def test_d_the_envelope_has_exactly_one_definition():
    """One mint, one absorber, one guard, on the BASE - so three stores cannot
    drift from each other. A second definition would be free to disagree, and
    invisibly, because each would look right alone (Ruling 67's reason)."""
    tree = ast.parse((SUSPENSION / "suspension_base.py").read_text(
        encoding="utf-8"))
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert {"_mint_id", "_absorb_envelope", "_envelope"} <= defined

    for name in ("csa.py", "veiled_thread.py", "black_sphere.py"):
        sub = ast.parse((SUSPENSION / name).read_text(encoding="utf-8"))
        local = {n.name for n in ast.walk(sub) if isinstance(n, ast.FunctionDef)}
        assert not ({"_mint_id", "_absorb_envelope", "_envelope"} & local), (
            f"{name} redefines the envelope machinery")


def test_d_every_store_declares_a_distinct_prefix():
    """A store without a prefix cannot mint an id that says which store issued
    it; two stores sharing one could mint the same id."""
    prefixes = [cls.ID_PREFIX for _, cls, _, _ in STORES]
    assert prefixes == ["CSA-", "VT-", "BS-"]
    assert len(set(prefixes)) == 3
    assert SuspensionSystem.ID_PREFIX is None, "the base suspends nothing"


def test_d_a_store_without_a_prefix_refuses_to_mint():
    """The refusal is typed and named rather than a silent `None-0001`."""
    class Prefixless(SuspensionSystem):
        def suspend(self, content, pressure, reason=""): ...
        def retrieve(self, entry_id): ...
        def check_stability(self): ...

    store = Prefixless()
    store.filepath = Path("unused.json")
    with pytest.raises(NotImplementedError):
        store._mint_id()


def test_d_the_three_snapshot_files_have_no_reader_outside_their_own_loaders():
    """A.3's STOP condition, standing rather than a one-time census.

    The loaders are the ONLY readers of the file shape. A second reader would
    have to know both eras too, and would be free to learn one of them wrong.
    """
    readers = []
    for path in sorted((REPO / "src").rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"load", "loads"}
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "json"):
                continue
            if rel.startswith("src/suspension/"):
                owner = next((n.name for n in ast.walk(tree)
                              if isinstance(n, ast.FunctionDef)
                              and n.lineno <= node.lineno
                              and node.lineno <= (n.end_lineno or n.lineno)),
                             None)
                if owner == "load_from_file":
                    continue
                readers.append(f"{rel}:{node.lineno} in {owner}")
    assert readers == [], (
        f"a second reader of a suspension snapshot at {readers}")


def test_d_the_mint_holds_the_files_lock_across_increment_and_return():
    """STRUCTURAL, and the instrument is chosen deliberately (Ruling 17).

    **FOUND BY A SURVIVING MUTANT**: dropping `mint_lock` is invisible
    single-threaded, so every behavioural pin above stays green while two
    instances over one path can interleave their increments. This is the exact
    gap Ruling 73's pass found at its own mint and closed the same way - the
    property IS a lexical scope, and a threaded probe could pass by luck.
    """
    tree = ast.parse((SUSPENSION / "suspension_base.py").read_text(
        encoding="utf-8"))
    mint = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_mint_id")

    held = [n for n in ast.walk(mint) if isinstance(n, ast.With)
            and any(isinstance(item.context_expr, ast.Call)
                    and getattr(item.context_expr.func, "id", None) == "mint_lock"
                    for item in n.items)]
    assert len(held) == 1, "`_mint_id` must take the file's mint lock exactly once"

    # ...AND THE INCREMENT AND THE RETURN ARE BOTH INSIDE IT. Deriving inside
    # the lock and returning outside would leave exactly the race it closes.
    body = held[0]
    assert any(isinstance(n, ast.AugAssign) for n in ast.walk(body)), (
        "the increment must be INSIDE the lock")
    assert any(isinstance(n, ast.Return) for n in ast.walk(body)), (
        "the mint must return from INSIDE the lock")


def test_d_the_black_sphere_families_survive_the_envelope(tmp_path):
    """**FOUND BY A SURVIVING MUTANT** - a real gap, and a real risk of this
    ruling's own schema change.

    The Black Sphere's save now routes its entry list through `_envelope`, which
    carries `paradox_families` as an extra key. Nothing asserted that it ARRIVES:
    dropping it left every pin green while paradox families vanished at the next
    restart, taking the store's only grouping with them.
    """
    path = tmp_path / "bs.json"
    store = BlackSphere(filepath=str(path))
    first = store.suspend("this statement is false", pressure=0.9,
                          paradox_type="self_reference")
    second = store.suspend("A and not A", pressure=0.9,
                           paradox_type="contradiction")

    payload = _payload(path)
    assert payload["paradox_families"] == {
        "self_reference": [first.id], "contradiction": [second.id]}

    resumed = BlackSphere(filepath=str(path))
    assert resumed.paradox_families == {
        "self_reference": {first.id}, "contradiction": {second.id}}
    assert resumed.high_water == 2, "and the mark rode in the same file"
