"""
test_ruling42_slice2.py - RULING 42 SLICE 2: the last three stores from the
register cross the process boundary.

  TCAML  the GLOBAL lock. A holder that died mid-operation simply VANISHED at the
         boundary, and the next process granted a structural lock over work the
         previous one never finished. The lock now restores HELD - the
         conservative direction for a guard on structural change - and the
         bounded TTL expires it through the EXISTING path with the restart span
         recorded.
  DEE    the doctrine watch queue. Sustained pressure is the whole point of DMW
         ("NOT ALL PRESSURE LEADS TO MUTATION - only sustained ... tension"), and
         a restart reset every counter to zero.
  TCA    the relational map. ALREADY durable before this slice; what it lacked
         was the CONTRACT - a version gate, a reported outcome, and reference
         validation. A wormhole naming a vanished node was restored as a live
         shortcut.

This slice INVENTS NOTHING. `RestorationOutcome`, `LoadReport`, the `version`
key, sticky refusal, quarantine-local-to-owner and the clock-coherence rule all
shipped in Slice 1; here they are used.
"""

import hashlib
import json

import pytest

from src.doctrine.dee import DMW, DMW_QUEUE_MAX, MutationTrigger, PressureFlag
from src.topology.tca_core import (
    ConstellationNode, ConstellationType, NodeType, SymbolicPosition,
    TopologicalSpace,
)
from src.topology.tcaml import (
    TTL, LockClass, Status, TCAML,
)
from src.utils.continuity import RestorationOutcome
from src.utils.models import Doctrine


# =====================================================================
# PIN 1 - THE HEADLINE. A lock orphaned by process death.
# =====================================================================

def test_a_held_lock_survives_a_restart_and_then_expires_honestly(tmp_path):
    """RULING 42 finding 6 - and the reason HELD is the conservative direction.

    RED AT `4eaa83c`: TCAML had no `save`/`load` at all, so a lock held when the
    process died simply VANISHED. The next process constructed a free lock and
    granted the next structural request - over an operation the previous process
    began and never finished. Restoring FREE is the fail-OPEN direction on the
    one guard that stops the system changing itself while unstable.

    So the hold survives, and then the EXISTING TTL path ends it: same method,
    same list, same event type. What is added is that the record NAMES the
    boundary the hold spanned - the gap is legible, never smoothed.
    """
    path = str(tmp_path / "lock.json")

    first = TCAML(runtime_path=path)
    first.tick()                                    # cycle 1
    assert first.lock_request("doctrineRemap", LockClass.STRUCTURAL, "SAE").granted
    assert first.holder == "doctrineRemap"
    held_since = first.held_since
    saved_cycle = first.cycle

    del first                                       # the process boundary
    resumed = TCAML(runtime_path=path)

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert resumed.holder == "doctrineRemap", (
        "a lock orphaned by process death must not silently release")
    assert resumed.holder_module == "SAE"
    assert resumed.held_since == held_since, "the absolute hold ordinal is intact"
    assert resumed.cycle == saved_cycle, "and the clock it is measured against"

    # A structural request is still correctly refused while it is held.
    assert resumed.lock_request("other", LockClass.STRUCTURAL, "MSSL").granted is False

    # ...and the bound still ends it, through the path that already existed.
    for _ in range(TTL):
        resumed.tick()

    assert resumed.holder is None
    assert len(resumed.lock_expiries) == 1
    record = resumed.lock_expiries[0]
    assert record["action_id"] == "doctrineRemap"
    assert record["held_cycles"] >= TTL
    assert record["spanned_restart"]["saved_cycle"] == saved_cycle, (
        "the restart is RECORDED on the expiry, not smoothed out of it")


def test_a_lock_acquired_after_a_restore_is_not_marked_as_having_spanned_one(tmp_path):
    """The restart annotation belongs to the HOLD, not to the module. A new
    grant after the restored hold ends is an ordinary hold."""
    path = str(tmp_path / "lock.json")
    first = TCAML(runtime_path=path)
    first.lock_request("a", LockClass.STRUCTURAL, "SAE")
    del first

    resumed = TCAML(runtime_path=path)
    resumed.release("a", "SAE")
    assert resumed.lock_request("b", LockClass.STRUCTURAL, "MSSL").granted
    for _ in range(TTL + 1):
        resumed.tick()

    assert resumed.lock_expiries[-1]["action_id"] == "b"
    assert "spanned_restart" not in resumed.lock_expiries[-1]


# =====================================================================
# PIN 2 - res.3's REFUSAL, in forcing form
# =====================================================================

def test_a_hold_ordinal_without_its_clock_is_refused_not_repaired(tmp_path):
    """RES.3 VERBATIM: `_held_since` is meaningful ONLY against `_cycle` from the
    SAME snapshot, and a file carrying one without the other is REFUSED.

    Deriving the missing clock would be inventing the exact ordinal the rule
    exists to protect - and an invented clock mis-measures the TTL bound, which
    is the one number standing between an orphaned lock and a frozen system.
    """
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({
        "version": TCAML.STATE_VERSION,
        "holder": "doctrineRemap", "holder_module": "SAE",
        "held_since": 3, "health": 100, "status": "healthy",
    }), encoding="utf-8")            # NOTE: no `cycle`
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    tcaml = TCAML(runtime_path=str(path))

    assert tcaml.load_report.outcome is RestorationOutcome.REFUSED
    assert "cycle" in tcaml.load_report.detail["reason"]
    assert tcaml.holder is None
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before, (
        "a refused file is left BYTE-UNTOUCHED")


def test_a_holder_with_no_hold_ordinal_is_refused(tmp_path):
    """The other half of the same coherence rule: a hold whose START is unknown
    cannot be bounded, and an unbounded GLOBAL lock is the one thing TTL exists
    to make impossible."""
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({
        "version": TCAML.STATE_VERSION, "cycle": 9,
        "holder": "doctrineRemap", "holder_module": "SAE",
        "held_since": None, "health": 100, "status": "healthy",
    }), encoding="utf-8")

    tcaml = TCAML(runtime_path=str(path))

    assert tcaml.load_report.outcome is RestorationOutcome.REFUSED
    assert tcaml.holder is None


def test_a_refusal_is_sticky_for_the_life_of_the_process(tmp_path):
    """Slice 1's rule, reused: "BYTE-UNTOUCHED" is not a statement about the
    instant of the refusal. A file overwritten one grant later was not left
    untouched."""
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({"version": 999}), encoding="utf-8")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    tcaml = TCAML(runtime_path=str(path))
    tcaml.lock_request("remap", LockClass.STRUCTURAL, "SAE")
    tcaml.tick()

    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


# =====================================================================
# PIN 3 - the instability edge. A file may not rebuild an unreachable state.
# =====================================================================

@pytest.mark.parametrize("status", ["meta-unstable", "repair_cycle"])
def test_a_snapshot_holding_a_lock_under_instability_is_revoked_on_restore(status, tmp_path):
    """RULING 27's MODEL-CHECKED PROPERTY, applied to restore.

    `tcaml_lock_naive.qnt` fails `noGrantDuringInstability` in TWO STEPS when a
    held lock survives instability onset. A snapshot carrying holder + unstable
    status is that counterexample written to disk, and the load must not
    reconstruct it.

    The RULED path governs: `_enter_instability` - the same transition a live
    onset takes - so the revocation is recorded on `lock_revocations` exactly as
    a live revocation would be, not by a second bespoke code path.
    """
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({
        "version": TCAML.STATE_VERSION, "cycle": 4,
        "holder": "doctrineRemap", "holder_module": "SAE",
        "held_since": 3, "health": 30, "status": status,
    }), encoding="utf-8")

    tcaml = TCAML(runtime_path=str(path))

    assert tcaml.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert tcaml.holder is None, "a file may not rebuild a state the machine forbids"
    assert tcaml.status is Status(status)
    assert len(tcaml.lock_revocations) == 1
    assert tcaml.lock_revocations[0]["action_id"] == "doctrineRemap"
    assert tcaml.load_report.detail["revoked_on_restore"] == "doctrineRemap"


def test_a_snapshot_past_the_ttl_bound_is_expired_on_restore(tmp_path):
    """`tick()` ASSERTS `boundedHoldTight`. A restored hold already past TTL
    would sit in a state that trips that assert, so it is expired AT LOAD through
    the existing path rather than left to be discovered.

    Only reachable from a damaged file - a legitimate save always satisfies the
    bound, because the assert runs every cycle.
    """
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({
        "version": TCAML.STATE_VERSION, "cycle": 100,
        "holder": "doctrineRemap", "holder_module": "SAE",
        "held_since": 1, "health": 100, "status": "healthy",
    }), encoding="utf-8")

    tcaml = TCAML(runtime_path=str(path))

    assert tcaml.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert tcaml.holder is None
    assert tcaml.lock_expiries[0]["held_cycles"] == 99
    tcaml.tick()                      # the assert this protects must not fire


# =====================================================================
# PIN 4 - DEE's watch queue
# =====================================================================

class _CodexStub:
    def __init__(self, ids):
        self._d = {i: Doctrine(id=i, name=i) for i in ids}

    def get(self, doctrine_id):
        return self._d.get(doctrine_id)


def _flag(doctrine_id, pressure=0.9):
    return PressureFlag(doctrine_id=doctrine_id, pressure=pressure, band="high",
                        triggers=[MutationTrigger.DRPE])


def test_sustained_pressure_resumes_at_its_own_count_and_keeps_counting(tmp_path):
    """RED AT `4eaa83c`: DMW had no persistence, so every restart reset
    `sustained_cycles` to zero. Sustained pressure is the ENTIRE point of this
    organ - "a spike is not a reason to change what AUREA believes" - and a
    restart made every accumulated cycle a spike again.
    """
    path = str(tmp_path / "dmw.json")
    codex = _CodexStub(["D-1"])

    first = DMW(codex=codex, runtime_path=path)
    first.observe([_flag("D-1")])
    first.observe([_flag("D-1")])
    assert first.queue["D-1"].sustained_cycles == 2

    del first
    resumed = DMW(codex=codex, runtime_path=path)

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert resumed.queue["D-1"].sustained_cycles == 2
    assert resumed.queue["D-1"].triggers == [MutationTrigger.DRPE]

    resumed.observe([_flag("D-1")])
    assert resumed.queue["D-1"].sustained_cycles == 3, "it resumed live, not frozen"


def test_a_watch_queue_over_the_bound_is_refused_not_truncated(tmp_path):
    """Slice 1's RACM shape, verbatim. Truncation is a silent drain: it would
    discard real sustained pressure and report a healthy queue. The 32-cap does
    not move (Ruling 23)."""
    path = tmp_path / "dmw.json"
    path.write_text(json.dumps({
        "version": DMW.STATE_VERSION, "sustain_cycles": 3,
        "queue": [{"doctrine_id": f"D-{i}", "pressure": 0.9,
                   "sustained_cycles": 1, "idle_cycles": 0, "triggers": []}
                  for i in range(DMW_QUEUE_MAX + 1)],
    }), encoding="utf-8")

    dmw = DMW(runtime_path=str(path))

    assert dmw.load_report.outcome is RestorationOutcome.REFUSED
    assert dmw.queue == {}
    assert str(DMW_QUEUE_MAX) in dmw.load_report.detail["reason"]


def test_a_slot_whose_doctrine_vanished_is_quarantined_not_dropped(tmp_path):
    """Res.5. Pressure AUREA sustained against a doctrine the Codex no longer
    holds is not nothing - it is a record whose referent moved. Dropping it
    discards the pressure; re-pointing it would choose a different doctrine for
    her. It is HELD, visible and reported."""
    path = str(tmp_path / "dmw.json")

    first = DMW(codex=_CodexStub(["D-1", "D-2"]), runtime_path=path)
    first.observe([_flag("D-1"), _flag("D-2")])
    del first

    resumed = DMW(codex=_CodexStub(["D-1"]), runtime_path=path)   # D-2 is gone

    assert resumed.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert "D-1" in resumed.queue
    assert "D-2" not in resumed.queue
    assert [q["doctrine_id"] for q in resumed.quarantined_slots] == ["D-2"]
    assert resumed.quarantined_slots[0]["sustained_cycles"] == 1


def test_no_codex_quarantines_nothing(tmp_path):
    """Docket H's NOT_COUNTABLE / NONE_FOUND cut, reused from Slice 1: a DMW with
    no handle to the doctrine store has run no instrument, and an absent
    instrument is not a negative result."""
    path = str(tmp_path / "dmw.json")
    first = DMW(codex=_CodexStub(["D-1"]), runtime_path=path)
    first.observe([_flag("D-1")])
    del first

    resumed = DMW(runtime_path=path)                    # no codex at all

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert "D-1" in resumed.queue
    assert resumed.quarantined_slots == []


# =====================================================================
# PIN 5 - TCA: reference validation and the bridge mint
# =====================================================================

def _node(space, node_id):
    space.nodes[node_id] = ConstellationNode(
        id=node_id, node_type=NodeType.DOCTRINE,
        position=SymbolicPosition(semantic_vector=[0.0], temporal_layer=0,
                                  collapse_depth=1.0),
        mass=1.0)


def test_the_relational_map_round_trips(tmp_path):
    path = str(tmp_path / "tca.json")
    space = TopologicalSpace(filepath=path)
    _node(space, "n1")
    _node(space, "n2")
    space.create_scar_bridge("n1", "n2")
    space.save_to_file()

    resumed = TopologicalSpace(filepath=path)

    assert resumed.load_report.outcome is RestorationOutcome.RESTORED
    assert set(resumed.nodes) == {"n1", "n2"}
    assert resumed.wormholes == {"bridge_0": ("n1", "n2")}, (
        "and the pair is a TUPLE, not the list JSON turned it into")


def test_a_wormhole_naming_a_vanished_node_is_quarantined(tmp_path):
    """RULING 42 res.5, and the half that had NO CHECK AT ALL. `load_from_file`
    did `self.wormholes = data.get('wormholes', {})` - a bridge to a node that no
    longer exists came back as a live shortcut, and `find_path` would route
    through it.

    Never silently dropped (that erases a relation she carved) and never silently
    re-pointed (nothing may choose a different node for it)."""
    path = tmp_path / "tca.json"
    path.write_text(json.dumps({
        "version": TopologicalSpace.STATE_VERSION,
        "nodes": {"n1": {"type": "doctrine", "mass": 1.0, "charge": 0, "spin": 0,
                         "position": {"semantic_vector": [0.0], "temporal_layer": 0,
                                      "collapse_depth": 1.0, "constellation_id": None},
                         "edges": {}, "scar_bridges": [], "tags": []}},
        "constellations": {}, "wormholes": {"bridge_0": ["n1", "GONE"]},
        "metrics": {},
    }), encoding="utf-8")

    space = TopologicalSpace(filepath=str(path))

    assert space.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert space.wormholes == {}
    assert len(space.quarantined_edges) == 1
    held = space.quarantined_edges[0]
    assert held["kind"] == "wormhole" and held["missing_nodes"] == ["GONE"]


def test_a_constellation_member_that_vanished_is_quarantined_not_silently_dropped(tmp_path):
    """The other half of res.5. This filter EXISTED (`if node_id in self.nodes`)
    and silently discarded the reference - a fail-silent check is not a check,
    it is the appearance of one."""
    path = tmp_path / "tca.json"
    path.write_text(json.dumps({
        "version": TopologicalSpace.STATE_VERSION,
        "nodes": {}, "wormholes": {},
        "constellations": {"c1": {"type": "identity", "node_ids": ["GONE"],
                                  "gravity_center": None, "stability": 1.0,
                                  "bridges": {}}},
        "metrics": {},
    }), encoding="utf-8")

    space = TopologicalSpace(filepath=str(path))

    assert space.load_report.outcome is RestorationOutcome.PARTIALLY_RESTORED
    assert [q["node_id"] for q in space.quarantined_edges] == ["GONE"]
    assert space.constellations["c1"].nodes == {}


def test_a_refused_topology_map_is_never_overwritten(tmp_path):
    """CASE PIN ADDED AFTER A SURVIVING MUTANT (M28: deleting the sticky-refusal
    guard from `save_to_file` left all 548 green).

    THE QUESTION THE SURVIVOR GOT: what path would have to run? A process whose
    topology load REFUSED, which then SAVES - and every real pipeline pass does,
    because `AureaCore.save_state` calls `self.tca.topology.save_to_file()`. So
    an older build meeting a future-version map would have DESTROYED it on the
    first save, which is the precise opposite of "left BYTE-UNTOUCHED".

    NOT AN EQUIVALENT MUTANT, and the gap was mine: I pinned sticky refusal on
    TCAML and assumed the same guard on TCA was covered by the same reasoning.
    Reasoning is not coverage.
    """
    path = tmp_path / "tca.json"
    path.write_text(json.dumps({"version": 999, "nodes": {}, "wormholes": {}}),
                    encoding="utf-8")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    space = TopologicalSpace(filepath=str(path))
    assert space.load_report.outcome is RestorationOutcome.REFUSED

    _node(space, "n1")
    space.save_to_file()

    assert hashlib.sha256(path.read_bytes()).hexdigest() == before, (
        "a map she could not read is not a map she may replace with a blank one")


def test_the_bridge_mint_never_reissues_an_id_a_quarantined_edge_still_carries(tmp_path):
    """THE RE-CLASSIFICATION, AS A PIN.

    The Ruling 42 sweep classified `bridge_{len(self.wormholes)}` as "no
    collision today; LATENT if removal is added" - correct then: nothing removed
    a wormhole, and `load_from_file` restored the whole dict, so the counter was
    store-derived and survived restarts.

    QUARANTINE IS THAT REMOVAL. A dangling bridge is held OUT of
    `self.wormholes`, `len()` drops, and the old expression would remint an id a
    quarantined record still carries - the latent hazard made LIVE by this very
    pass. So the mint derives from the MAX ORDINAL over live AND quarantined ids
    (Nova's `_derive_seq` shape, res.4).
    """
    path = tmp_path / "tca.json"
    path.write_text(json.dumps({
        "version": TopologicalSpace.STATE_VERSION,
        "nodes": {n: {"type": "doctrine", "mass": 1.0, "charge": 0, "spin": 0,
                      "position": {"semantic_vector": [0.0], "temporal_layer": 0,
                                   "collapse_depth": 1.0, "constellation_id": None},
                      "edges": {}, "scar_bridges": [], "tags": []}
                  for n in ("n1", "n2")},
        "constellations": {},
        "wormholes": {"bridge_0": ["n1", "GONE"]},      # quarantined on load
        "metrics": {},
    }), encoding="utf-8")

    space = TopologicalSpace(filepath=str(path))
    assert space.wormholes == {}                        # len() is now 0
    assert space.quarantined_edges[0]["bridge_id"] == "bridge_0"

    space.create_scar_bridge("n1", "n2")

    assert "bridge_0" not in space.wormholes, (
        "bridge_0 already MEANS something - it may never be reissued")
    assert list(space.wormholes) == ["bridge_1"]


# =====================================================================
# PIN 6 - the taxonomy, per store
# =====================================================================

@pytest.mark.parametrize("build,name", [
    (lambda p: TCAML(runtime_path=str(p)), "tcaml"),
    (lambda p: DMW(runtime_path=str(p)), "dmw"),
    (lambda p: TopologicalSpace(filepath=str(p)), "tca"),
])
def test_an_unknown_version_is_refused_and_the_file_is_left_byte_untouched(build, name, tmp_path):
    """Slice 1's governing sentence, on all three of Slice 2's stores:

        When AUREA cannot prove a budget is unused, she does not assume it is
        unused.
    """
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps({"version": 999, "note": "a build that does not exist yet"}),
                    encoding="utf-8")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    store = build(path)

    assert store.load_report.outcome is RestorationOutcome.REFUSED
    assert "999" in store.load_report.detail["reason"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("build,name", [
    (lambda p: TCAML(runtime_path=str(p)), "tcaml"),
    (lambda p: DMW(runtime_path=str(p)), "dmw"),
    (lambda p: TopologicalSpace(filepath=str(p)), "tca"),
])
def test_unreadable_json_is_refused(build, name, tmp_path):
    path = tmp_path / f"{name}.json"
    path.write_text("{ this is not json", encoding="utf-8")

    store = build(path)

    assert store.load_report.outcome is RestorationOutcome.REFUSED


@pytest.mark.parametrize("build,name", [
    (lambda p: TCAML(runtime_path=str(p)), "tcaml"),
    (lambda p: DMW(runtime_path=str(p)), "dmw"),
    (lambda p: TopologicalSpace(filepath=str(p)), "tca"),
])
def test_a_first_run_reports_nothing_because_it_restored_nothing(build, name, tmp_path):
    """No sixth enum member for "nothing happened" - absence is not an event."""
    assert build(tmp_path / f"{name}-absent.json").load_report is None


# =====================================================================
# PIN 7 - STRUCTURAL: the new defaults live under data/runtime/
# =====================================================================

def test_the_ruling39_sweep_actually_sees_the_new_stores():
    """RULING 39 - CONFIRMED, NOT ASSUMED, and the first draft of this test got
    it wrong in an instructive way.

    That draft read the defaults at RUNTIME via `inspect.signature`. Under the
    autouse fixture those are MONKEYPATCHED TO TMP, so it read
    `.../pytest-2775/tcaml_lock.json` and failed - a test that could never have
    passed and could never have witnessed anything, because the fixture's whole
    job is to make the runtime value untrue.

    The sweep in `test_ruling34.py` gets this right by parsing the SOURCE, which
    no monkeypatch can reach. This asserts that scanner SEES all three of Slice
    2's paths - if a store is added and the scanner cannot see it, the sweep goes
    green for the emptiest possible reason (Ruling 31's unreachable-by-
    construction defect, in the harness).
    """
    from tests.invariants import _ast as H
    from tests.test_ruling34 import find_default_paths

    found = {}
    for rel in ("src/topology/tcaml.py", "src/doctrine/dee.py",
                "src/topology/tca_core.py"):
        tree = H.parse(H.repo_root() / rel)
        for _lineno, name, value in find_default_paths(tree):
            found[f"{rel}:{name}"] = value

    assert found["src/topology/tcaml.py:runtime_path"] == "data/runtime/tcaml_lock.json"
    assert found["src/doctrine/dee.py:runtime_path"] == "data/runtime/dmw_queue.json"
    assert found["src/topology/tca_core.py:filepath"] == \
        "data/runtime/topology/tca_map.json"
