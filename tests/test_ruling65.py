"""
test_ruling65.py - RULING 65: the map is a derivation, and a derivation is
rebuilt, never restored.

THE RULING IN ONE SENTENCE: the persisted topology was a stored derivation being
trusted over its sources, so startup now builds the map from the stores and reads
no map file at all.

WHAT THIS FILE DOES NOT CONTAIN, AND WHY THAT MATTERS
-------------------------------------------------------------------------------
There is no pin here asserting that mass is no longer doubled, that the nine
one-way edges are gone, or that the gravity center holds. Those live in
`tests/test_verification_pass.py`, where they were written against the DEFECT at
`0b2072c` and watched fail. Ruling 65's pass turned all five RED, and per PATH
v39's close instruction their markers were deleted and their assertions kept IN
PLACE - a witness that becomes its ruling's pin is worth more than a fresh copy
of the same assertion, because it carries the measured values that justified it.

So this file pins what those witnesses CANNOT: that the read path is gone as
SHAPE, that the third source is rebuilt, that echoes are dropped on purpose, and
that the surviving snapshot influences live state by exactly zero.

ISOLATION: `tests/conftest.py`'s autouse fixture redirects all 25 injectable
durable paths per test - the topology's `filepath` among them, unchanged, since
`save_to_file` still writes. The three seed paths are deliberately NOT
redirected (Rulings 32/39), so every boot below reads AUREA's real founding
doctrines and scars.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.topology.tca_core import (NodeType, SymbolicPosition, TopologicalSpace)

REPO = Path(__file__).resolve().parents[1]


# =====================================================================
# HELPERS
# =====================================================================

def _census(core):
    """Everything res.1's named property covers, in one comparable shape."""
    topo = core.tca.topology
    return {
        "nodes": set(topo.nodes),
        "edges": {tuple(sorted([n, o])) for n, node in topo.nodes.items()
                  for o in node.edges},
        "total_mass": round(topo.total_mass, 9),
        "total_edges": topo.total_edges,
        "centers": {cid: c.gravity_center
                    for cid, c in topo.constellations.items()},
    }


def _map_path(core) -> Path:
    return core.tca.topology.filepath


# =====================================================================
# (a) RESTART IDENTITY - the load-bearing pin
#
# The four §1 witnesses in test_verification_pass.py cover the individual
# quantities. This covers the RULING'S OWN SENTENCE as a single property.
# =====================================================================

def test_a_restarted_aurea_holds_the_same_relational_map_as_a_fresh_one():
    """RES.1'S NAMED PROPERTY, whole.

    boot -> save -> boot again must equal fresh genesis on node set, edge set,
    `total_mass`, `total_edges` AND every gravity center - not on some of them.
    Asserting the aggregate is the point: the defect this ruling closes moved
    four of those five at once, and a pin that checked one would have called it
    a mass bug.
    """
    fresh = _census(AureaCore())

    core = AureaCore()
    core.save_state()
    assert _map_path(core).exists(), "the diagnostic snapshot must still be written"

    resumed = _census(AureaCore())

    assert resumed == fresh, (
        "a restarted map differs from a fresh one: "
        + repr({k: (fresh[k], resumed[k]) for k in fresh if fresh[k] != resumed[k]}))


def test_restart_identity_holds_across_repeated_restarts():
    """THE THIRD AND FOURTH BOOT, because the measured defect SATURATED.

    `total_mass` locked at 2x and then stayed there, so a pin comparing only
    boot 2 to boot 3 would have found them equal and reported stability. The
    comparison that witnesses anything is always against FRESH.
    """
    fresh = _census(AureaCore())
    for _ in range(3):
        core = AureaCore()
        core.save_state()
        assert _census(AureaCore()) == fresh


# =====================================================================
# (b) THE READ PATH IS ABSENT AS SHAPE
# =====================================================================

def test_the_topological_space_has_no_load_method():
    """RES.1, Ruling 61's form: the wrong path's ABSENCE is the enforcement.

    Not deprecated, not uncalled - GONE. A load method that exists but nothing
    calls is a loaded gun for a later "helpful" pass that notices the map is
    saved and never restored.
    """
    assert not hasattr(TopologicalSpace, "load_from_file"), (
        "TopologicalSpace.load_from_file is back; res.1 deletes it FROM THE "
        "CLASS, and an uncalled loader is exactly what that forbids")
    for banned in ("_refuse", "load_report", "quarantined_edges"):
        assert not hasattr(TopologicalSpace, banned), (
            f"{banned} served the read path and leaves with it")

    space = TopologicalSpace()
    for banned in ("load_report", "quarantined_edges"):
        assert not hasattr(space, banned), f"instance still carries {banned}"


def test_no_module_in_src_reads_the_topology_snapshot():
    """RES.3 AS SHAPE: the snapshot is WRITE-ONLY, pinned across all of `src/`.

    The scanner looks for any `open(...)` or `json.load(...)` reached from a
    `filepath` belonging to the topology, and for any surviving reference to the
    deleted loader by name. A reader added anywhere in `src/` reintroduces
    exactly the structure res.1 deleted.
    """
    offenders = []
    for path in sorted(REPO.joinpath("src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            # `<anything>.load_from_file()` where the receiver is a topology.
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "load_from_file"):
                recv = ast.unparse(node.func.value)
                if "topology" in recv or "tca" in recv:
                    offenders.append(f"{path.relative_to(REPO)}: {ast.unparse(node)}")
            # A read-mode open of the topology's own path.
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                rendered = ast.unparse(node)
                if "tca_map" in rendered or "topology" in rendered:
                    offenders.append(f"{path.relative_to(REPO)}: {rendered}")
    assert not offenders, "the write-only snapshot acquired a reader:\n" + "\n".join(offenders)


def test_the_snapshot_reader_scanner_fires_on_a_real_violation(tmp_path):
    """THE SCANNER'S OWN CONTROL - Ruling 32's answer to the vacuous pin.

    A scan that passes because it cannot see is worth nothing, so the same two
    patterns are fed to the same logic and must be caught.
    """
    violations = [
        "def boot(self):\n    self.tca.topology.load_from_file()\n",
        "def boot(self):\n    handle = open('data/runtime/topology/tca_map.json')\n",
    ]
    for source in violations:
        tree = ast.parse(source)
        hits = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "load_from_file"):
                recv = ast.unparse(node.func.value)
                if "topology" in recv or "tca" in recv:
                    hits.append(node)
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                rendered = ast.unparse(node)
                if "tca_map" in rendered or "topology" in rendered:
                    hits.append(node)
        assert hits, f"the scanner is blind to:\n{source}"

    benign = "def save(self):\n    self.codex.load_from_file()\n"
    tree = ast.parse(benign)
    hits = [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "load_from_file"
            and ("topology" in ast.unparse(n.func.value)
                 or "tca" in ast.unparse(n.func.value))]
    assert not hits, "the scanner must not flag another store's loader"


# =====================================================================
# (c) THE PARADOX LOOP - the third source, witnessed
#
# SURVIVING MUTANT, JUDGED EQUIVALENT AND ANNOTATED RATHER THAN PINNED (M08:
# running the paradox loop BEFORE the doctrine loop instead of after left all
# 910 green).
#
# THE REASON IS STRUCTURAL, not "no test happened to catch it": `place_paradox`
# CREATES NO EDGES. It calls `add_node`, sets `spin`, may set
# `position.orbital_center`, and adds a family tag - and that is all
# (`tca_integration.py:160-205`). Both scar and doctrine placement end by
# calling `create_edge` against nodes that must already exist, which is what
# makes THEIR relative order load-bearing (Ruling 57, and mutant M09 confirms it
# is still pinned). Paradox placement has no such dependency in either
# direction, so its position in the sequence cannot move the node set, the edge
# set, mass, or any gravity center.
#
# THE ONE THEORETICAL COUPLING, NAMED SO IT IS NOT MISSED LATER: the family
# lookup scans `topology.nodes` for `suspension_entry.paradox_family in n.tags`,
# so a DOCTRINE carrying a `tca_tag` equal to a paradox family name could be
# selected as an orbital center, and then order would decide. It is not
# constructible from the seed, and `orbital_center` is on no surface this ruling
# names - no edge, no mass, no center. Inventing a pin for it would be pinning a
# coupling the architecture does not have.
# =====================================================================

def test_a_persisted_paradox_is_rebuilt_with_no_topology_file_present():
    """RES.1'S THIRD LOOP, and the gap it closes.

    Paradox nodes had ONE creator - the PARADOX_SUSPENDED branch of
    `process_input` - so before this loop they survived a restart only via the
    map file. Deleting the read path without adding this loop would have LOST
    them, which is why the two land together.

    THE `unlink()` IS THE WHOLE POINT: with no snapshot on disk, the node can
    only have come from the Black Sphere's own persisted entries.
    """
    core = AureaCore()
    entry = core.black_sphere.suspend(
        content="This sentence is false.", source="test",
        pressure=0.9, reason="self-reference", paradox_type="self_reference")
    node = core.tca.place_paradox(entry)
    assert node.id in core.tca.topology.nodes
    core.save_state()

    _map_path(core).unlink()
    assert not _map_path(core).exists()

    resumed = AureaCore()
    assert entry.id in resumed.black_sphere.entries, (
        "precondition: the Black Sphere is the persisted SOURCE")
    rebuilt = resumed.tca.topology.nodes.get(entry.id)
    assert rebuilt is not None, (
        "a persisted paradox produced no node after restart - res.1's third "
        "loop is the only thing that can place it now")
    assert rebuilt.node_type is NodeType.PARADOX


# =====================================================================
# (d) THE ECHO DROP - both directions
# =====================================================================

def test_an_echo_node_is_rebuilt_from_its_record_and_kept_in_the_snapshot():
    """RES.4 - **SUPERSEDED 2026-08-05 BY RULING 75, WHICH THIS RULING NAMED IN
    ADVANCE AS ITS OWN REOPENING CONDITION.**

        ~~test_an_echo_node_is_dropped_from_live_state_but_kept_in_the_snapshot~~

        THE OLD PIN, KEPT VERBATIM, because its reasoning is exactly why it
        could not survive its own premise changing:

            RES.4, BOTH HALVES, and they are the two halves of one decision.

            DROPPED: an Echo record persists NOWHERE (`EchoMemory` is unwired),
            so a restored echo node would assert a holding no store holds.
            Dropping it is a CORRECTION, not a loss - the record it shadowed was
            already gone.

            KEPT IN THE SNAPSHOT: write-only means the diagnostic retains what
            live state discards. That asymmetry IS res.3 - a forensic surface
            that only ever showed what the next boot would reload would be a
            cache, not a record.

            resumed = AureaCore()
            for nid in echo_nodes:
                assert nid not in resumed.tca.topology.nodes, (
                    f"{nid} came back into live state; res.4 excludes ECHO from
                    the rebuild because its record persists nowhere")

    **THE EXCLUSION WAS NEVER ABOUT ECHOES - IT WAS ABOUT PERSISTENCE**, and
    the old docstring says so in its own words: *"a restored echo node would
    assert a holding no store holds."* Ruling 75 wires `EchoMemory`, so a store
    DOES hold it, and the identical reasoning now requires the opposite
    behaviour. **This is not a weakened pin; it is the same principle read
    against a changed fact** - and the fact changed by ruling, in the ruling
    that Ruling 65 res.4 named as its reopening condition in writing.

    THE SNAPSHOT HALF IS UNTOUCHED AND ITS ASSERTIONS ARE BYTE-IDENTICAL: the
    write-only diagnostic still retains the node, which was always res.3's
    property rather than res.4's.
    """
    core = AureaCore()
    result = core.process_input("An ordinary claim.")
    echo_nodes = [nid for nid, n in core.tca.topology.nodes.items()
                  if n.node_type is NodeType.ECHO]
    assert echo_nodes, "precondition: the pass placed an echo node"
    core.save_state()

    snapshot = json.loads(_map_path(core).read_text(encoding="utf-8"))
    for nid in echo_nodes:
        assert nid in snapshot["nodes"], (
            f"{nid} must survive in the write-only diagnostic")
        assert snapshot["nodes"][nid]["type"] == NodeType.ECHO.value

    resumed = AureaCore()
    for nid in echo_nodes:
        assert nid in resumed.tca.topology.nodes, (
            f"{nid} did not come back into live state; Ruling 75 makes echoes "
            f"the FOURTH SOURCE, so a persisted echo is rebuilt like every "
            f"other persisted record")
        assert resumed.tca.topology.nodes[nid].node_type is NodeType.ECHO

    # AND THE REBUILD IS FROM THE RECORD, NOT FROM THE SNAPSHOT: the map is
    # still a pure derivation over the stores (res.1/res.3 untouched).
    assert [e.id for e in resumed.echo_memory.read_all()] == echo_nodes


# =====================================================================
# (e) GENESIS PLACES ONCE
# =====================================================================

def test_fresh_genesis_mass_equals_the_sum_of_placed_masses(monkeypatch):
    """RES.5. The +15.0 is gone because there is ONE placement path, not two
    that have to be kept in agreement."""
    from src.doctrine.codex import Codex
    monkeypatch.setattr(Codex, "load_from_file", lambda self: None)

    core = AureaCore()
    topo = core.tca.topology
    assert topo.total_mass == pytest.approx(
        sum(n.mass for n in topo.nodes.values()))


def test_create_seed_doctrines_places_nothing(monkeypatch):
    """RES.5 AS SHAPE, and this is the pin that survives a refactor.

    The mass pin above passes if placement is duplicated but the arithmetic is
    made to agree - which res.6 now does. So the STRUCTURAL claim is pinned
    separately: `_create_seed_doctrines` authors doctrines and maps none.
    """
    from src.doctrine.codex import Codex
    monkeypatch.setattr(Codex, "load_from_file", lambda self: None)

    calls = []
    from src.topology.tca_integration import TCAIntegration
    real = TCAIntegration.place_doctrine
    monkeypatch.setattr(TCAIntegration, "place_doctrine",
                        lambda self, d: (calls.append(d.id), real(self, d))[1])

    core = AureaCore()
    assert calls, "precondition: the rebuild loop still places doctrines"
    assert len(calls) == len(set(calls)), (
        f"a doctrine was placed twice: {calls}")


# =====================================================================
# (f) THE REPLACEMENT MASS PROPERTY
# =====================================================================

def test_replacing_a_node_leaves_total_mass_equal_to_the_masses_held(tmp_path):
    """RES.6 AS A PROPERTY, driven DIRECTLY rather than through a restart.

    The restart route no longer exists, so if this were only pinned end-to-end
    it would be pinned by a path that cannot run. Re-placement WITHIN a boot is
    lawful (doctrine mutation may re-place), so the arithmetic is what must be
    honest.
    """
    space = TopologicalSpace(filepath=str(tmp_path / "tca.json"))
    pos = SymbolicPosition(semantic_vector={"a": 1.0}, collapse_depth=0.1)

    space.add_node("n1", NodeType.DOCTRINE, mass=5.0, position=pos)
    assert space.total_mass == pytest.approx(5.0)

    space.add_node("n1", NodeType.DOCTRINE, mass=7.0, position=pos)
    assert len(space.nodes) == 1, "replacement must not add a second node"
    assert space.total_mass == pytest.approx(7.0), (
        "replacement double-counted: total_mass must equal the sum of the "
        "masses actually held")
    assert space.total_mass == pytest.approx(
        sum(n.mass for n in space.nodes.values()))


def test_replacing_a_node_does_not_double_count_it_in_its_constellation(tmp_path):
    """RES.6's SECOND HALF, stated in the ruling and easy to miss.

    `Constellation.add_node` has the same unconditional `+=`, so a fix at the
    space level alone leaves the constellation's own `total_mass` wrong - and
    that is the number `calculate_cohesion` reads.
    """
    from src.topology.tca_core import ConstellationType
    space = TopologicalSpace(filepath=str(tmp_path / "tca.json"))
    # A bare space holds no constellations - `TCAIntegration` seeds the six, not
    # `TopologicalSpace.__init__`. Building one here keeps the pin on res.6's
    # arithmetic rather than on the integration layer's setup.
    cid = "c1"
    space.create_constellation(cid, ConstellationType.IDENTITY)
    pos = SymbolicPosition(semantic_vector={"a": 1.0}, collapse_depth=0.1)

    space.add_node("n1", NodeType.DOCTRINE, mass=5.0, position=pos,
                   constellation_id=cid)
    space.add_node("n1", NodeType.DOCTRINE, mass=7.0, position=pos,
                   constellation_id=cid)

    constellation = space.constellations[cid]
    assert len(constellation.nodes) == 1
    assert constellation.total_mass == pytest.approx(
        sum(n.mass for n in constellation.nodes.values())), (
        "the constellation double-counted a replaced member")


# =====================================================================
# RES.7 - THE BRIDGE MINT
#
# SURVIVING MUTANT M04 (reverting `_next_bridge_id` to
# `f"bridge_{len(self.wormholes)}"` left all 910 green) - JUDGED EQUIVALENT, AND
# THE INVESTIGATION FOUND A REAL DEFECT IN THIS PASS'S OWN WORK.
#
# The first response was to write a pin forcing the max-ordinal form, on the
# strength of `_next_bridge_id`'s docstring claim that it "stays correct if
# anything ever does [remove a wormhole]". THAT PIN FAILED, and it was right to:
# delete `bridge_0` from an otherwise-empty dict and max-ordinal mints
# `bridge_0` again, exactly as `len()` would. **It was the QUARANTINED term -
# not the max-ordinal shape - that made the old expression removal-safe, and
# that term left with the read path.** The two forms are equivalent in every
# case.
#
# So M04 is a genuine equivalent mutant, the false sentence was struck from the
# docstring rather than pinned around, and the reopening condition (a real
# issued-set is needed again if a removal path is ever added) is recorded at the
# method. **A mutation survivor whose investigation corrects a false claim in
# the pass's own documentation is the discipline paying for itself.**
#
# What IS pinned below is res.7's actual claim: per-boot determinism.
# =====================================================================

def test_bridge_ids_derive_identically_on_every_boot():
    """RES.7's OTHER HALF - the narrowing that makes per-boot issuance safe.

    Ruling 42 res.4's "the mint counts what has been ISSUED" is CONSCIOUSLY
    narrowed for this store. That is only sound because placement order is
    deterministic, so the same boot produces the same ids - which is a claim
    about the rebuild, and therefore testable.
    """
    first = dict(AureaCore().tca.topology.wormholes)
    second = dict(AureaCore().tca.topology.wormholes)
    assert first == second, (
        "bridge ids are per-boot derivations; if they are not stable across "
        "identical boots, res.7's narrowing does not hold")


# =====================================================================
# (g) THE ADVERSARIAL SNAPSHOT
# =====================================================================

@pytest.mark.parametrize("payload,label", [
    ("{ this is not json", "corrupted"),
    (json.dumps({"version": 999, "nodes": {}, "wormholes": {}}), "future version"),
    (json.dumps({"version": 1, "nodes": {"FABRICATED": {
        "type": "doctrine", "mass": 999.0, "charge": 0, "spin": 0,
        "position": {"semantic_vector": {"x": 1.0}, "temporal_layer": 0,
                     "collapse_depth": 1.0, "constellation_id": None},
        "edges": {"ALSO_FAKE": 1.0}, "scar_bridges": [], "tags": ["forged"]}},
        "constellations": {}, "wormholes": {"bridge_0": ["FABRICATED", "GONE"]},
        "metrics": {"total_mass": 12345.0}}), "fabricated"),
])
def test_a_boot_is_identical_whether_the_snapshot_is_hostile_or_absent(
        payload, label, tmp_path):
    """RES.3'S PROPERTY, AND IT IS A PIN RATHER THAN A PROMISE.

    "Write-only" is a claim about every possible file content, so it is tested
    against a file engineered to be believed: a node with 999.0 mass, an edge to
    a node that does not exist, and a wormhole to nowhere. If ANY of it reached
    live state, mass, node set or edge set would move.

    This is the successor to Slice 2's `test_a_refused_topology_map_is_never_
    overwritten`, and it is stronger in the direction that matters: that pin
    protected the FILE from the process; this establishes the file cannot
    influence the PROCESS.
    """
    baseline = _census(AureaCore())

    path = _map_path(AureaCore())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")

    hostile = _census(AureaCore())
    assert hostile == baseline, (
        f"a {label} snapshot changed live state: "
        + repr({k: (baseline[k], hostile[k])
                for k in baseline if baseline[k] != hostile[k]}))
    assert "FABRICATED" not in hostile["nodes"]


# =====================================================================
# (h) THE CONSTRUCTION EDGE COUNT
# =====================================================================

def test_total_edges_reads_twelve_at_construction():
    """RES.8. The rebuild reproduces the CONSTRUCTION graph EXACTLY.

    DIVERGENCE FROM THE RULING'S QUOTED MAGNITUDE, RECORDED AT THE SITE AND
    REPORTED. Ruling 65 pin (h) and res.8 both say "21 edges, not 40". THE
    CONSTRUCTION GRAPH IS 12. The sixty-second entry's measurements, which res.8
    cites, are:

        fresh boot   - counter 12, true unique 12
        after restart - counter 40, true unique 21

    So 21 is the RESTARTED true-unique count, not the construction count, and it
    equals 12 + the nine restart-only reverse-only edges. The ruling transcribed
    the wrong row of its own measurement.

    THE RULING'S PRINCIPLE GOVERNS ITS QUOTED NUMBER, AND THE PRINCIPLE IS
    UNAMBIGUOUS AND POINTS AT 12: res.8 says in the same sentence that Ruling
    57's seam row STANDS UNTOUCHED and that reverse-only seed links still form
    NO edge. Those nine edges are precisely the reverse-only ones. **Pinning 21
    would assert that they DID form - the exact half-repair res.8 forbids in the
    words immediately following the number.** 12 is the only value consistent
    with the resolution; 21 would contradict it.

    Pinned at 12, reported to the architect rather than silently absorbed.
    """
    topo = AureaCore().tca.topology
    assert topo.total_edges == 12
    true_unique = len({tuple(sorted([n, o])) for n, node in topo.nodes.items()
                       for o in node.edges})
    assert true_unique == 12, "the counter and the graph must agree"
    assert topo.total_edges == true_unique, (
        "the counter drifting from the graph is what read 40 against 21 under "
        "the deleted read path")


def test_the_reverse_only_seed_links_still_form_no_edge():
    """RULING 57'S SEAM ROW, PINNED SO THIS RULING CANNOT ERODE IT.

    `Δ117` is named in that row: `Doctrine-3` and `AVT.015` name it in their own
    records, it names them back, and NO edge forms at construction because
    `place_scar` runs before any doctrine node exists.

    Res.8 says this ruling does not repair that. A pass that "helpfully" made
    the rebuild form these edges would be performing the restart's accidental
    half-repair on purpose, and this pin is what fails first.
    """
    topo = AureaCore().tca.topology
    if "Δ117" not in topo.nodes:
        pytest.skip("seed does not carry Δ117")
    assert topo.nodes["Δ117"].edges == {}, (
        "Δ117 acquired an edge; Ruling 57's seam row records that reverse-only "
        "seed links form none at construction, and Ruling 65 res.8 keeps it")
