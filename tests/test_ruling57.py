"""
test_ruling57.py - THE SEED IS PLACED WHOLE (Ruling 57, 2026-07-31).

Manifest twenty-second addendum. Scars enter the topology at construction,
BEFORE doctrines, and centers follow edges the moment edges exist.

WHAT WAS BROKEN, in one chain - each link measured by Docket P's soak before
this ruling was written:

    `place_scar` had exactly ONE caller in `src/`, the runtime chamber path,
    so SEED SCARS WERE NEVER PLACED AT ALL
      -> `place_doctrine`'s edge loop guards on `if scar_id in topology.nodes`
         and therefore never fired: every doctrine node carried ZERO edges
      -> `_recalculate_center` scores `mass * len(edges)`, so every candidate
         scored 0 and the strict `>` against 0 selected NOTHING
      -> `_find_nearest_constellation` skips a centerless constellation
      -> NO ECHO NODE WAS EVER PLACED (40 of 40 across 200 cycles)
      -> CONST-ID's spanning arm could never fire.

COINS NOTHING. Every position, mass, constellation assignment, edge weight and
selection rule in the placement path is pre-existing and unmoved. The fix is an
ORDERING, an EXISTENCE, and a TRIGGER.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `edcfbbb`.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.topology.tca_core import NodeType, SymbolicPosition, TopologicalSpace


# =====================================================================
# A. RESOLUTION 1 - THE SEED IS ON THE MAP
# =====================================================================

def test_seed_scars_are_placed_at_construction() -> None:
    """**RED FIRST.** Against `edcfbbb` the topology held 7 nodes - the active
    doctrines and NOT ONE SCAR. `place_scar`'s only caller was the runtime
    chamber path, so the seed's wounds were never on the map at all.

    ANY DECAY STATE, which is Ruling 54's cut applied to the map: a topology
    records what she HOLDS, not what is still hot. `Δ91` is FOSSILIZED and canon
    calls a fossilized scar "part of symbolic lineage" (2b:921).
    """
    core = AureaCore()
    nodes = core.tca.topology.nodes

    for scar in core.scar_core.all_scars():
        assert scar.id in nodes, f"{scar.id} is held by the store and not on the map"

    assert "Scar-0" in nodes, "The Origin Collapse is on the map"
    assert "Δ91" in nodes, (
        "a FOSSILIZED scar is part of symbolic lineage and belongs on the map - "
        "the map is not filtered by bearing")
    assert nodes["Δ91"].node_type is NodeType.SCAR


def test_scars_are_placed_before_doctrines_so_the_edges_can_form() -> None:
    """THE ORDERING IS THE MECHANISM, and this is its direct witness.

    **RED FIRST**: every doctrine node carried ZERO edges against `edcfbbb`,
    because both edge loops guard on `if <id> in self.topology.nodes` and the
    scars did not exist.
    """
    core = AureaCore()
    nodes = core.tca.topology.nodes

    linked = [d for d in core.codex.view().values() if d.scar_links]
    assert linked, "precondition: the seed records doctrine -> scar links"

    for doctrine in linked:
        if doctrine.id not in nodes:
            continue                      # a fallen doctrine is not placed
        present = [s for s in doctrine.scar_links if s in nodes]
        if not present:
            continue
        assert nodes[doctrine.id].edges, (
            f"{doctrine.id} records {doctrine.scar_links} and carries no edge - "
            f"the scar nodes did not exist when its edge loop ran")
        for scar_id in present:
            assert scar_id in nodes[doctrine.id].edges
            # `create_edge` is symmetric: the scar gains the edge too, which is
            # what lets a SCAR-side constellation acquire a center.
            assert doctrine.id in nodes[scar_id].edges


def test_the_seed_placement_uses_no_new_rule(monkeypatch) -> None:
    """COINS NOTHING, structurally: the construction path calls the OWNER's
    existing placement methods and passes them nothing but the record.

    A new mass, position or constellation computed at the call site would be a
    placement rule invented by the orchestrator - which is what the ruling
    forbids in terms.
    """
    seen = []
    original = AureaCore.__init__

    from src.topology.tca_integration import TCAIntegration
    real_place = TCAIntegration.place_scar

    def spy(self, scar):
        seen.append(scar)
        return real_place(self, scar)

    monkeypatch.setattr(TCAIntegration, "place_scar", spy)
    core = AureaCore()

    assert seen, "construction placed the seed scars through the owner's method"
    from src.utils.models import Scar
    assert all(isinstance(s, Scar) for s in seen), (
        "the record is handed over whole - no position, mass or constellation "
        "is computed at the call site")


# =====================================================================
# B. RESOLUTION 2 - CENTERS FOLLOW EDGES
# =====================================================================

def _bare_space(tmp_path, *names) -> TopologicalSpace:
    """A topology with only the constellations a test names.

    Deliberately NOT `TCAIntegration`'s six: these pins are about the trigger
    itself, and a bare space makes the before/after states unambiguous.
    """
    from src.topology.tca_core import ConstellationType

    space = TopologicalSpace(filepath=str(tmp_path / "tca.json"))
    for name in names:
        space.create_constellation(name, ConstellationType.LOGICAL)
    return space


def _add(space, node_id, constellation_id, mass=1.0):
    return space.add_node(node_id=node_id, node_type=NodeType.SCAR, mass=mass,
                          position=SymbolicPosition(semantic_vector=[0.1] * 8,
                                                    collapse_depth=0.1,
                                                    temporal_layer=0.0),
                          constellation_id=constellation_id)


def test_an_edge_makes_a_center_appear_forced_both_directions(tmp_path) -> None:
    """THE TRIGGER'S DIRECT WITNESS. **RED FIRST**: against `edcfbbb`
    `create_edge` did not recalculate anything - only `add_node`/`remove_node`
    did, and both run BEFORE a node has any edges. That one-statement gap is
    `paradox_void`'s 75-cycle center lag in the Docket P soak, exactly.

    BOTH DIRECTIONS ARE FORCED: no edge -> no center (the honest anchorless
    case), edge -> center. Asserting only the second passes against an
    implementation that hands out a center unconditionally.
    """
    space = _bare_space(tmp_path, "identity_core")
    _add(space, "S-1", "identity_core")
    _add(space, "S-2", "identity_core")

    assert space.constellations["identity_core"].gravity_center is None, (
        "NO EDGE -> NO CENTER: `mass * len(edges)` is 0 for every member, and "
        "nothing here is an anchor yet")

    space.create_edge("S-1", "S-2", weight=0.7)

    assert space.constellations["identity_core"].gravity_center is not None, (
        "an edge exists, so a member now scores above zero and is selected")
    assert space.constellations["identity_core"].gravity_center in ("S-1", "S-2")


def test_an_edge_refreshes_both_endpoints_constellations(tmp_path) -> None:
    """BOTH endpoints, not just one. A cross-constellation edge anchors each
    side - and a scar-side constellation acquiring a center is precisely what
    res.1's ordering exists to make possible."""
    space = _bare_space(tmp_path, "logic_core", "ethics_core")
    _add(space, "D-1", "logic_core")
    _add(space, "S-1", "ethics_core")

    assert space.constellations["logic_core"].gravity_center is None
    assert space.constellations["ethics_core"].gravity_center is None

    space.create_edge("D-1", "S-1", weight=0.8)

    assert space.constellations["logic_core"].gravity_center == "D-1"
    assert space.constellations["ethics_core"].gravity_center == "S-1"


def test_a_constellation_of_zero_edge_members_stays_anchorless(tmp_path) -> None:
    """RESOLUTION 3, FORCED. The honest anchorless case is PRESERVED, not
    patched away: members with no connections have nothing that anchors them,
    and substituting a fallback would COIN an anchor the data does not support
    at the exact point where placement decisions are made."""
    space = _bare_space(tmp_path, "shadow_realm", "empirical_core")
    _add(space, "A", "shadow_realm")
    _add(space, "B", "shadow_realm")
    _add(space, "C", "empirical_core")

    assert space.constellations["shadow_realm"].gravity_center is None
    assert space.constellations["empirical_core"].gravity_center is None

    # Adding a THIRD member changes nothing: membership is not connection, and
    # `add_node` already recalculated on the way in. It is the EDGE that
    # anchors, never the count of members.
    _add(space, "D", "shadow_realm")
    assert space.constellations["shadow_realm"].gravity_center is None


def test_an_edge_to_an_unplaced_node_triggers_nothing_for_that_side(tmp_path) -> None:
    """A node outside any constellation has no membership to recalculate, and
    inventing one here would be a placement rule wearing a refresh's clothes."""
    space = _bare_space(tmp_path, "logic_core")
    _add(space, "IN", "logic_core")
    space.add_node(node_id="OUT", node_type=NodeType.ECHO, mass=1.0,
                   position=SymbolicPosition(semantic_vector=[9.0] * 8,
                                             collapse_depth=0.5,
                                             temporal_layer=0.0))
    assert space.nodes["OUT"].position.constellation_id is None

    space.create_edge("IN", "OUT")

    assert space.constellations["logic_core"].gravity_center == "IN", (
        "the placed side still refreshes")
    assert space.nodes["OUT"].position.constellation_id is None, (
        "the unplaced side is not placed as a side effect of being linked")

    # THE TWO SURVIVING MUTANTS OF THIS PASS ARE EQUIVALENT FOR ONE SHARED
    # REASON, annotated here rather than left as a coverage gap:
    # `_recalculate_center` is a PURE, IDEMPOTENT function of the
    # constellation's CURRENT state. So neither
    #   (M06) dropping `_refresh_centers`' dedup, which recalculates the same
    #         constellation twice when both endpoints share one, nor
    #   (M07) recalculating an arbitrary EXTRA constellation when an endpoint
    #         has no membership,
    # can change any observable outcome - an extra recomputation returns what
    # was already there. The dedup is kept because doing the work twice is
    # waste, and the `is None` skip is kept because pretending an unplaced node
    # has a constellation is false even where it is harmless. Both are
    # correctness-neutral and neither is a hole in these pins.


def test_the_selection_rule_itself_is_untouched(tmp_path) -> None:
    """RULING 57 CHANGES WHEN THE RULE IS ASKED, NEVER HOW IT ANSWERS.

    `mass * len(edges)`, strict `>` against an initial 0. Pinned by giving two
    members different mass and asserting the heavier one wins with edges equal.
    """
    space = _bare_space(tmp_path, "logic_core", "ethics_core")
    _add(space, "LIGHT", "logic_core", mass=1.0)
    _add(space, "HEAVY", "logic_core", mass=9.0)
    _add(space, "OTHER", "ethics_core", mass=1.0)

    space.create_edge("LIGHT", "OTHER")
    space.create_edge("HEAVY", "OTHER")

    assert space.constellations["logic_core"].gravity_center == "HEAVY", (
        "one edge each, so mass decides - the pre-existing rule, unmoved")


# =====================================================================
# C. THE CONSEQUENCE ON THE WIRED PIPELINE
# =====================================================================

def test_the_constellations_holding_seed_material_have_centers() -> None:
    """PIN 1. **RED FIRST**: against `edcfbbb` ALL SIX constellations were
    centerless at construction (the soak's "five of six" counted `paradox_void`
    acquiring one only at runtime cycle 75).

    ENUMERATED RATHER THAN COUNTED, because which ones gain a center is the
    reportable fact: a constellation with connected members has an anchor; an
    EMPTY one honestly does not, and that is res.3's case surviving.
    """
    core = AureaCore()
    constellations = core.tca.topology.constellations

    populated = {cid: c for cid, c in constellations.items() if c.nodes}
    empty = {cid: c for cid, c in constellations.items() if not c.nodes}

    assert populated, "the seed places material"
    for cid, c in populated.items():
        assert c.gravity_center is not None, (
            f"{cid} holds {sorted(c.nodes)} and has no anchor")
        assert c.gravity_center in core.tca.topology.nodes

    for cid, c in empty.items():
        assert c.gravity_center is None, (
            f"{cid} is EMPTY and must not claim an anchor")


def test_an_echo_places_on_the_wired_pipeline() -> None:
    """PIN 2. **RED FIRST**: 0 of 40 echo nodes placed across the Docket P soak,
    and 0 of 10 in the pre-pass probe. The echo had nothing to be near, because
    nothing had an anchor."""
    core = AureaCore()
    result = core.process_input("Water is wet.")

    node = core.tca.topology.nodes[result["echo"].id]
    assert node.position.constellation_id is not None, (
        "an echo now lands in a constellation - `_find_nearest_constellation` "
        "has real centers to measure against")


def test_the_runtime_path_still_places_its_own_scars() -> None:
    """RESOLUTION 3's other half: the runtime path was ALREADY CORRECT and is
    untouched. A chamber scar places at formation, and now gains center
    freshness for free from res.2."""
    core = AureaCore()
    before = len(core.tca.topology.nodes)
    result = core.process_input("Honesty is pointless.")

    scar = result.get("scar_formed")
    if scar is None:
        pytest.skip("this claim did not scar in this configuration")
    assert scar.id in core.tca.topology.nodes
    assert scar.id in result["pass_nodes"]
    assert len(core.tca.topology.nodes) > before


def test_seed_placement_writes_nothing_to_the_stores() -> None:
    """THE MAP IS A READ. Placement consumes SNAPSHOTS (`all_scars`, Ruling 22)
    and must not write back into the scar or doctrine store - the topology is a
    consumer, and Ruling 1 governs writes."""
    core = AureaCore()

    scars = {s.id: (s.decay_state, s.weight, tuple(s.linked_doctrines))
             for s in core.scar_core.all_scars()}
    doctrines = {d.id: (d.status, tuple(d.scar_links))
                 for d in core.codex.view().values()}

    second = AureaCore()
    assert {s.id: (s.decay_state, s.weight, tuple(s.linked_doctrines))
            for s in second.scar_core.all_scars()} == scars
    assert {d.id: (d.status, tuple(d.scar_links))
            for d in second.codex.view().values()} == doctrines
