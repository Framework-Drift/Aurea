"""
test_ruling76.py - RULING 76: THE RECORD CARRIES ITS ORIGIN, AND THE EDGE IS A
DERIVATION.

    Ruling 75 forbade IMPROVISING the event edges. Ruling 76 does not
    improvise them: it adds the missing JOINS at the creation sites so they
    become derivations over records.

Items 7 + 9 and the edge-rebuild question are ONE decision. When this closes,
Ruling 65's restart-identity law is back to FULL SCOPE - nodes AND edges.

WHERE THE REST OF THIS RULING'S PINS LIVE:
`tests/test_ruling75.py` carries the two finding pins this ruling turns green -
`test_h_the_paradox_void_center_survives_restart` and
`test_h_the_event_edges_are_rebuilt_from_recorded_joins`. They were written
against the measured defect, they demanded that a later pass come and say why,
and they were migrated in place with their old text kept verbatim. **A witness
that becomes its ruling's pin is worth more than a fresh copy of the same
assertion.**
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.filtration.scar_logic_core import ScarLogicCore
from src.retrieval.record_joins import (ClaimRecords, claim_of_scar,
                                        claim_of_suspension, claims_present,
                                        records_for_claim)
from src.suspension.black_sphere import BlackSphere
from src.suspension.suspension_base import SuspensionEntry, SuspensionType
from src.topology.tca_core import NodeType
from src.utils.models import Scar

REPO = Path(__file__).resolve().parents[1]
RETRIEVAL = "src/retrieval/record_joins.py"


def _tree(rel):
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


# =====================================================================
# (a) THE CENSUS - four sites, two classes
# =====================================================================

def _create_edge_sites():
    """Every `create_edge` CALL SITE in `src/`, tagged by its enclosing scope.

    RGLOB rather than a module list (Ruling 70's instrument lesson): the census
    must cover the module nobody has written yet, or it reports a completeness
    that lapses the moment someone adds a file.

    TAGGED BY SCOPE, because scope IS the classification: a call inside
    `AureaCore.__init__` is a REBUILD DERIVATION; one inside `process_input` is
    a LIVE EVENT site; one in `tca_integration` is PLACEMENT-DERIVED.
    """
    found = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        owners = {}
        for func in ast.walk(tree):
            if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(func):
                    owners.setdefault(id(inner), func.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (getattr(node.func, "attr", None)
                        or getattr(node.func, "id", None))
                if name == "create_edge":
                    found.append((path.relative_to(REPO).as_posix(),
                                  owners.get(id(node), "<module>"),
                                  node.lineno))
    return found


def test_a_the_edge_census_holds_three_classes_and_no_fourth():
    """PIN (a). **THE CENSUS THIS RULING OPENED WITH, PINNED - AND CORRECTED BY
    ITS OWN FIRST RUN.**

    The opening census found FOUR sites in TWO classes. This pin's first draft
    asserted `len(sites) == 4` and went red, correctly: **Ruling 76 ADDS two
    sites** - the fifth-phase derivations - so the post-ruling tree holds six in
    THREE classes. Pinning the pre-ruling count would have measured the tree
    this ruling replaced.

      PLACEMENT-DERIVED (`tca_integration`, 2) - scar->doctrine and
        doctrine->scar, from `linked_doctrines` / `scar_links`. These have
        ALWAYS reformed at rebuild and are UNTOUCHED by Ruling 76.
      LIVE EVENT (`process_input`, 2) - echo->paradox at suspension, echo->scar
        at formation. **Untouched too**: live behaviour is unchanged, and these
        remain the authority the derivations must EQUAL.
      REBUILD DERIVATION (`__init__`, 2) - Ruling 76's fifth phase, one per
        event class.

    **A SEVENTH SITE, OR A SITE IN A FOURTH SCOPE, IS A STOP** - it would be an
    edge class nobody has classified, and this ruling's derivation would
    silently not cover it.
    """
    sites = _create_edge_sites()
    by_scope = {}
    for rel, scope, line in sites:
        by_scope.setdefault((rel, scope), []).append(line)

    assert sorted(by_scope) == [
        ("src/aurea_core.py", "__init__"),
        ("src/aurea_core.py", "process_input"),
        ("src/topology/tca_integration.py", "place_doctrine"),
        ("src/topology/tca_integration.py", "place_scar"),
    ], f"the edge census moved: {sorted(by_scope)}"

    assert len(by_scope[("src/aurea_core.py", "process_input")]) == 2, (
        "the LIVE EVENT class changed - these are the authority the rebuild "
        "derivations must equal")
    assert len(by_scope[("src/aurea_core.py", "__init__")]) == 2, (
        "the REBUILD DERIVATION class changed - one per event class")
    assert len(sites) == 6, f"the edge census moved: {sites}"


def test_a_the_census_instrument_actually_fires():
    """The scanner's own control - Ruling 32's answer to the vacuous pin."""
    found = [n for n in ast.walk(ast.parse(
        "def f(self):\n    self.topology.create_edge('a', 'b', weight=1.0)\n"))
        if isinstance(n, ast.Call)
        and getattr(n.func, "attr", None) == "create_edge"]
    assert len(found) == 1


# =====================================================================
# (b) THE JOIN IS POPULATED AT BOTH CREATION SITES
# =====================================================================

def test_b_a_scar_formed_by_a_claim_carries_that_claims_id():
    """PIN (b) / res.1. Driven through the REAL pipeline, not constructed."""
    core = AureaCore()
    result = core.process_input("Honesty is pointless.")
    scar = result.get("scar_formed")
    if scar is None:
        pytest.skip("this claim did not reach scar formation")

    assert scar.claim_id == result["claim_id"], (
        "the scar does not carry the claim cycle's id")
    assert scar.claim_id is not None
    assert scar.claim_id == result["echo"].claim_id, (
        "the scar and its echo must name the SAME ancestry record")


def test_b_a_suspension_from_a_claim_carries_that_claims_id():
    """PIN (b) / res.1. The Black Sphere half, through the real pipeline."""
    core = AureaCore()
    result = core.process_input("This statement is false.")
    if not core.black_sphere.entries:
        pytest.skip("this claim did not suspend into the Black Sphere")

    entry = next(iter(core.black_sphere.entries.values()))
    assert entry.claim_id == result["claim_id"]
    assert entry.claim_id == result["echo"].claim_id


def test_b_the_claim_id_survives_the_black_sphere_file(tmp_path):
    """PIN (b). **THE JOIN MUST SURVIVE THE FILE OR IT IS NOT A JOIN**, and this
    is the defect the ruling's first measurement caught.

    `BlackSphere.save_to_file` writes an EXPLICIT field list, so a new field is
    invisible to it until named there. The scar store serializes `__dict__` and
    carried the join for free; the Black Sphere silently dropped it, and the
    symptom was the paradox edge failing to rebuild while the scar edge
    succeeded.
    """
    path = tmp_path / "bs.json"
    sphere = BlackSphere(filepath=str(path))
    entry = sphere.suspend(content="a paradox", source="pipeline",
                           pressure=0.9, claim_id="CLM-0042")
    assert entry.claim_id == "CLM-0042"

    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["entries"][0]["claim_id"] == "CLM-0042", (
        "the join was dropped at the serializer")

    reloaded = BlackSphere(filepath=str(path))
    assert reloaded.entries[entry.id].claim_id == "CLM-0042", (
        "the join was dropped at the loader")


def test_b_the_claim_id_is_keyword_only_on_suspend(tmp_path):
    """PIN (i) / res.1. Keyword-only, so the two existing callers are
    unaffected and a future one cannot bind it positionally into `reason`."""
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    with pytest.raises(TypeError):
        sphere.suspend("content", "source", 0.9, "reason", "type", "CLM-0001")


def test_b_non_pipeline_suspensions_carry_none(tmp_path):
    """PIN (i) / res.1. **ABSENT IS A REAL ANSWER.** The tether's suspensions
    have no claim cycle behind them and must not appear to."""
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    entry = sphere.suspend(content="tether paradox", source="tether",
                           pressure=0.9)
    assert entry.claim_id is None


# =====================================================================
# (c) LEGACY HONESTY - no backfill, no inference, no edge
# =====================================================================

def test_c_a_legacy_scar_carries_none_and_derives_no_edge(tmp_path):
    """PIN (c) / res.1. A scar written before this ruling loads clean, carries
    `None`, and **fabricates nothing**. No content matching, no inference."""
    path = tmp_path / "scars.json"
    legacy = [{
        "id": "Scar-legacy", "name": "old", "origin": "pre-ruling",
        "type": "contradiction", "weight": 3.0,
        "created_at": "2026-01-01 00:00:00", "decay_state": "active",
        "linked_doctrines": [], "last_accessed": None, "description": "",
        "echo_proximity": [], "reflexes": [], "tca_tags": [], "is_seed": False,
    }]
    path.write_text(json.dumps(legacy), encoding="utf-8")
    before = path.read_bytes()

    core = ScarLogicCore(filepath=str(path))
    scar = core.get_scar("Scar-legacy")
    assert scar is not None, "a legacy scar must still load"
    assert scar.claim_id is None
    assert scar.origin_pressure is None
    assert path.read_bytes() == before, "a READ rewrote the record"


def test_c_a_legacy_suspension_carries_none(tmp_path):
    """PIN (c) / res.1. The suspension half, tolerant-load form (Ruling 75)."""
    path = tmp_path / "bs.json"
    path.write_text(json.dumps({
        "entries": [{
            "id": "BS-legacy", "content": "old paradox", "source": "pipeline",
            "pressure_level": 0.9, "timestamp": "2026-01-01T00:00:00",
            "reason": "", "orbit_stability": 1.0,
            "paradox_family": "self_reference",
            "gravitational_influence": 0.27, "access_count": 0,
            "last_accessed": None, "metadata": {},
        }],
        "paradox_families": {},
    }), encoding="utf-8")
    before = path.read_bytes()

    sphere = BlackSphere(filepath=str(path))
    assert sphere.entries["BS-legacy"].claim_id is None
    assert path.read_bytes() == before


def test_c_a_record_missing_either_fact_derives_no_edge():
    """PIN (c) / res.3. **STATED RATHER THAN REPAIRED.**

    A scar with a `claim_id` but no `origin_pressure` derives NOTHING - the
    live site writes the edge at the raw pressure, and inventing a weight would
    build a different graph than the one that happened.
    """
    core = AureaCore()
    result = core.process_input("Honesty is pointless.")
    scar = result.get("scar_formed")
    if scar is None:
        pytest.skip("this claim did not reach scar formation")

    # Strip ONE of the two facts on the persisted record, then restart.
    live = core.scar_core._find(scar.id)
    live.origin_pressure = None
    core.save_state()

    resumed = AureaCore()
    edges = {(n, e) for n, v in resumed.tca.topology.nodes.items()
             for e in v.edges}
    assert not any(scar.id in pair for pair in edges), (
        "an edge was derived for a scar missing its origin_pressure - the "
        "weight was invented")


# =====================================================================
# (d) origin_pressure IS THE RAW FACT BESIDE THE CLAMPED DERIVATION
# =====================================================================

def test_d_origin_pressure_is_raw_and_weight_stays_clamped():
    """PIN (d) / res.2. **THE CLAMP IS WHY THE FACT IS NECESSARY.**

    `weight = min(pressure * 2.0, 5.0)`, so every collapse at pressure >= 2.5
    stores the SAME weight and the raw pressure is UNRECOVERABLE from it. The
    echo->scar edge is created at the RAW pressure, so without this fact a
    saturated scar's edge could not be re-derived at all.

    Both are asserted on ONE formation: the derivation and the fact it came
    from coexist, and neither rewrites the other (Ruling 63's recorded-basis
    form).
    """
    core = AureaCore()
    result = core.process_input("Honesty is pointless.")
    scar = result.get("scar_formed")
    if scar is None:
        pytest.skip("this claim did not reach scar formation")

    raw = result["collapse_result"].pressure_generated
    assert scar.origin_pressure == raw, "origin_pressure is not the RAW value"
    assert scar.weight == pytest.approx(min(raw * 2.0, 5.0)), (
        "`weight` changed - it is a pre-existing derivation and stays one")


def test_d_the_clamp_ambiguity_is_real_and_documented():
    """PIN (d). The clamp genuinely destroys information - measured, so the
    justification for `origin_pressure` is a fact rather than an argument."""
    for pressure in (2.5, 3.0, 10.0):
        assert min(pressure * 2.0, 5.0) == 5.0
    # Three different collapses, one stored weight: weight cannot recover them.
    assert len({min(p * 2.0, 5.0) for p in (2.5, 3.0, 10.0)}) == 1


def test_d_origin_pressure_survives_the_scar_file(tmp_path):
    """PIN (d). Both new fields round-trip through the scar store."""
    core = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    core.form_scar(origin="test", weight=5.0, claim_id="CLM-0009",
                   origin_pressure=3.75)
    core.save_to_file()

    reloaded = ScarLogicCore(filepath=str(tmp_path / "scars.json"))
    scar = next(s for s in reloaded.all_scars() if s.claim_id == "CLM-0009")
    assert scar.origin_pressure == 3.75
    assert scar.weight == 5.0, "the clamped weight and the raw fact coexist"


# =====================================================================
# (e) THE FIFTH PHASE - derived edges EQUAL the live sites'
# =====================================================================

def test_e_derived_edges_are_identical_to_the_live_sites():
    """PIN (e) / res.3. **THE EQUALITY PIN - endpoints AND weights.**

    Approximation would not do: the derivation must produce the SAME graph the
    live sites produced, or a restarted AUREA holds a different map than the one
    she had - which is the very defect Ruling 65 exists to prevent.
    """
    core = AureaCore()
    for claim in ("This statement is false.", "Honesty is pointless."):
        core.process_input(claim)
    core.save_state()

    def event_edges(topo):
        echoes = {n for n, v in topo.nodes.items()
                  if v.node_type is NodeType.ECHO}
        out = {}
        for node_id, node in topo.nodes.items():
            for other in node.edges:
                if node_id in echoes or other in echoes:
                    weight = node.edge_weights.get(other) if hasattr(
                        node, "edge_weights") else None
                    out[(node_id, other)] = weight
        return out

    live = event_edges(core.tca.topology)
    if not live:
        pytest.skip("this claim set produced no event edge")

    rebuilt = event_edges(AureaCore().tca.topology)
    assert set(live) <= set(rebuilt), (
        f"missing derived edges: {sorted(set(live) - set(rebuilt))}")
    for pair, weight in live.items():
        assert rebuilt[pair] == weight, (
            f"derived weight differs at {pair}: live={weight} "
            f"rebuilt={rebuilt[pair]}")


def test_e_the_fifth_phase_runs_after_every_placement():
    """PIN (e) / res.3. Order: scars -> doctrines -> paradoxes -> echoes ->
    EVENT EDGES. An edge needs BOTH endpoints placed."""
    core_class = next(n for n in ast.walk(_tree("src/aurea_core.py"))
                      if isinstance(n, ast.ClassDef) and n.name == "AureaCore")
    init = next(n for n in core_class.body
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")

    placements, edges = [], []
    for node in ast.walk(init):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("place_scar", "place_doctrine",
                                  "place_paradox", "place_echo"):
                placements.append((node.lineno, node.func.attr))
            elif node.func.attr == "create_edge":
                edges.append(node.lineno)

    assert [n for _, n in sorted(placements)] == [
        "place_scar", "place_doctrine", "place_paradox", "place_echo"]
    assert edges, "the fifth phase creates no edges at all"
    assert min(edges) > max(line for line, _ in placements), (
        "an event edge is derived before every node is placed")


def test_e_the_derivation_invents_no_weight():
    """PIN (e) / res.3. The paradox weight is the live site's literal 1.0; the
    scar weight is READ FROM THE RECORD. Nothing else is computed."""
    core_class = next(n for n in ast.walk(_tree("src/aurea_core.py"))
                      if isinstance(n, ast.ClassDef) and n.name == "AureaCore")
    init = next(n for n in core_class.body
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    for node in ast.walk(init):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "create_edge"):
            weight = next((k.value for k in node.keywords if k.arg == "weight"),
                          None)
            assert weight is not None, "an edge is derived with no stated weight"
            rendered = ast.unparse(weight)
            assert rendered in ("1.0", "scar.origin_pressure"), (
                f"a derived edge weight is computed rather than recorded: "
                f"{rendered}")


# =====================================================================
# (g) FULL-SCOPE RESTART IDENTITY - Ruling 65's law restored
# =====================================================================

def test_g_a_restarted_map_is_identical_including_event_edges():
    """PIN (g) / res.4. **RULING 65'S LAW RETURNS TO FULL SCOPE - NODES AND
    EDGES.**

    That ruling's named property was "a restarted AUREA holds the SAME
    relational map as a fresh one", and Ruling 75 measured it holding for nodes
    and failing for the two event edges. This is the whole map.
    """
    core = AureaCore()
    for claim in ("This statement is false.", "Honesty is pointless.",
                  "A is not A."):
        core.process_input(claim)
    core.save_state()

    def census(topo):
        return {
            "nodes": sorted(topo.nodes),
            "edges": sorted((n, e) for n, v in topo.nodes.items()
                            for e in v.edges),
            "centers": {c: v.gravity_center
                        for c, v in topo.constellations.items()},
            "total_mass": round(topo.total_mass, 4),
        }

    live = census(core.tca.topology)
    resumed = census(AureaCore().tca.topology)
    assert resumed == live, (
        "the restarted map differs from the live one:\n"
        f"  nodes lost   : {sorted(set(live['nodes']) - set(resumed['nodes']))}\n"
        f"  edges lost   : {sorted(set(live['edges']) - set(resumed['edges']))}\n"
        f"  centers moved: "
        f"{ {k: (v, resumed['centers'].get(k)) for k, v in live['centers'].items() if resumed['centers'].get(k) != v} }")


# =====================================================================
# (h) RETRIEVAL - id joins only, scoreless
# =====================================================================

def test_h_retrieval_joins_are_correct_on_real_records():
    """PIN (h) / res.5. The same joins read the other way."""
    core = AureaCore()
    for claim in ("This statement is false.", "Honesty is pointless."):
        core.process_input(claim)
    core.save_state()

    echoes = core.echo_memory.read_all()
    scars = core.scar_core.all_scars()
    suspensions = list(core.black_sphere.entries.values())

    for echo in echoes:
        found = records_for_claim(echo.claim_id, echoes=echoes, scars=scars,
                                  suspensions=suspensions)
        assert [e.id for e in found.echoes] == [echo.id], (
            "the echo join is not one-to-one (Ruling 75's guarantee)")
        for scar in found.scars:
            assert claim_of_scar(scar) == echo.claim_id
        for entry in found.suspensions:
            assert claim_of_suspension(entry) == echo.claim_id

    assert claims_present(echoes) == [e.claim_id for e in echoes]


def test_h_retrieval_is_exact_equality_never_a_prefix():
    """PIN (h) / res.5. Ruling 60 res.3's lesson: `CLM-0001` must never graze
    `CLM-00010`."""
    near = [Scar(id="S1", name="n", origin="o", claim_id="CLM-00010"),
            Scar(id="S2", name="n", origin="o", claim_id="CLM-0001"),
            Scar(id="S3", name="n", origin="o", claim_id=None)]
    found = records_for_claim("CLM-0001", scars=near)
    assert [s.id for s in found.scars] == ["S2"]


def test_h_an_unknown_claim_returns_empty_and_that_is_legitimate():
    found = records_for_claim("CLM-9999", echoes=(), scars=(), suspensions=())
    assert found.is_empty
    assert found.echoes == () and found.scars == () and found.suspensions == ()
    with pytest.raises(ValueError):
        records_for_claim("")


def test_h_absent_joins_contribute_nothing():
    """PIN (h) / res.5. A record with `None` is ABSENT - never a prompt to
    guess, and never counted among the ids that WERE recorded."""
    records = [Scar(id="S1", name="n", origin="o", claim_id=None),
               Scar(id="S2", name="n", origin="o", claim_id="CLM-0001"),
               Scar(id="S3", name="n", origin="o", claim_id=None)]
    assert claims_present(records) == ["CLM-0001"]
    assert claim_of_scar(records[0]) is None
    entry = SuspensionEntry(id="BS-x", content="c", source="tether",
                            suspension_type=SuspensionType.BLACK_SPHERE,
                            pressure_level=0.5)
    assert claim_of_suspension(entry) is None


def test_h_retrieval_carries_no_score_rank_or_similarity():
    """PIN (h) / res.5. **QL4's absence, and the BARs' permanent one.**

    Content-similarity retrieval is FOREVER outside the truth path: a
    similarity ranker decides which evidence a later stage ever sees, which is
    a selection effect entering by the side door (Ruling 71's finding, binding
    identically here).
    """
    source = (REPO / RETRIEVAL).read_text(encoding="utf-8")
    tree = _tree(RETRIEVAL)

    defined = {n.name.lower() for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for word in ("score", "rank", "similar", "distance", "embed", "vector",
                 "relevance", "top_k", "nearest", "match_content"):
        assert not any(word in name for name in defined), (
            f"a `{word}` surface appeared in the retrieval module")

    for record in (ClaimRecords,):
        for field_name in record.__dataclass_fields__:
            assert not any(w in field_name.lower()
                           for w in ("score", "rank", "weight", "confidence",
                                     "relevance", "similarity")), field_name

    # NO NUMERIC LITERAL IS COMPARED ANYWHERE - there is no cutoff to coin.
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left] + list(node.comparators)
            assert not [o for o in operands
                        if isinstance(o, ast.Constant)
                        and isinstance(o.value, (int, float))
                        and not isinstance(o.value, bool)], (
                f"a numeric comparison at line {node.lineno}: "
                f"`{ast.unparse(node)}`")


def test_h_the_retrieval_module_owns_no_store_and_grants_nothing():
    """PIN (h) / res.5. Ruling 63's shape (records arrive already-read) and
    Ruling 70's enforcement-by-scope."""
    tree = _tree(RETRIEVAL)
    calls = {getattr(n.func, "id", None) or getattr(n.func, "attr", None)
             for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for forbidden in ("open", "read_text", "write_text", "mkdir", "dumps",
                      "load", "save_to_file"):
        assert forbidden not in calls, f"the retrieval module calls {forbidden}"

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.update(node.module.split("."))
    for forbidden in ("sae", "codex", "racm", "reflex", "hail", "ore",
                      "echonet", "goals", "json", "pathlib", "os",
                      "numpy", "random"):
        assert forbidden not in imported, (
            f"the retrieval module imports {forbidden}")


def test_h_no_consumer_in_src_reads_the_retrieval_module():
    """res.5. It is CAPABILITY, not wiring - nothing consumes it this pass, and
    this pin reddens the day something does, which is exactly when that wiring
    needs its own ruling."""
    #
    # ~~if "record_joins" in node.module or "retrieval" in node.module.split("."):~~
    #
    # MIGRATED 2026-08-09 (Ruling 79), old text kept verbatim above, and the
    # ASSERTION IS UNCHANGED - `record_joins` still has no consumer in `src/`.
    #
    # WHAT MOVED IS THE SCAN'S AIM, WHICH WAS BROADER THAN ITS OWN SUBJECT. The
    # second clause flagged an import from the retrieval PACKAGE, while this
    # test's name, docstring and failure message all speak of the retrieval
    # MODULE. That was a distinction without a difference for exactly as long as
    # `record_joins.py` was the package's only member; Ruling 79 adds
    # `divergence.py` beside it, and `aurea_core` imports THAT - so the old form
    # reddened for a module this pin was never written about.
    #
    # **IT IS NARROWED WITHOUT BEING WEAKENED.** The package clause existed to
    # catch `from src.retrieval import record_joins`, where the module string
    # names only the package - so that form is still caught, now by checking the
    # imported NAMES rather than by flagging the package wholesale. A consumer
    # of `record_joins` in either spelling still reddens this, which is the day
    # that wiring needs its own ruling.
    consumers = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "record_joins.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported = {alias.name for alias in node.names}
                if ("record_joins" in node.module
                        or ("retrieval" in node.module.split(".")
                            and "record_joins" in imported)):
                    consumers.append(path.relative_to(REPO).as_posix())
    assert consumers == [], f"the retrieval module acquired a consumer: {consumers}"


# =====================================================================
# (j) COINS NOTHING NUMERIC; (k) CENSUS REGRESSION
# =====================================================================

def test_j_this_ruling_added_no_enum_member():
    """PIN (j) / res.7. **COINS: two optional record fields and nothing else.**"""
    found = {}
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.ClassDef):
                continue
            if not any("Enum" in ast.unparse(b) for b in node.bases):
                continue
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            found.setdefault(target.id, []).append(
                                f"{path.relative_to(REPO).as_posix()}:{node.name}")
    assert len(found) > 100, f"census implausibly small: {len(found)}"
    assert not any("record_joins.py" in owner
                   for owners in found.values() for owner in owners)


def test_j_the_new_fields_are_optional_and_default_to_none():
    """PIN (j). Both fields default to `None` on every record type, so every
    pre-existing construction site is untouched and honest."""
    scar = Scar(id="S", name="n", origin="o")
    assert scar.claim_id is None and scar.origin_pressure is None

    entry = SuspensionEntry(id="E", content="c", source="s",
                            suspension_type=SuspensionType.BLACK_SPHERE,
                            pressure_level=0.0)
    assert entry.claim_id is None
