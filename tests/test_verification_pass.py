"""THE VERIFICATION PASS - executable witnesses for the external review's five
credible-unverified findings (manifest sixtieth entry, items (f) through (j)).

WHAT THIS FILE IS, AND WHAT IT IS NOT
-------------------------------------------------------------------------------
Every test here is a WITNESS OF A CONFIRMED DEFECT, not a guard of existing
behaviour - with exactly ONE exception, marked as such at the site (§5's
one-resolution guard, which is the half of finding (j) this pass REFUTED and is
therefore pinned as a real property).

RULING 65 (2026-08-02) RETIRED THE FIVE §1 WITNESSES. Their markers are DELETED
and their assertions KEPT IN PLACE, per PATH v39's close instruction - each
docstring records the exact marker it carried, verbatim, so the defect that
justified it stays legible at the site that now forbids it. They are ordinary
passing pins now and guard Ruling 65's named property: a restarted AUREA holds
the same relational map as a fresh one. FOURTEEN witnesses remain xfail, for
findings (g) through (j).

That retirement is the mechanism working exactly as designed below, on the first
ruling to reach one of these findings. The remaining witnesses are `xfail(strict=True)`.
That is the load-bearing choice:

  - The suite stays GREEN, because these record defects that are NOT this pass's
    to repair. PATH v38's mandate is MEASURE BEFORE FIXING; each of these five
    has a genuine fork that only a ruling may decide, so none was repaired here.
  - The failure output IS the finding of record (Ruling 64's standing form: a
    ruling that corrects a live surface writes the witness against the OLD code
    first, and the witness's failure output is the finding). Run with `-rx` to
    read them.
  - `strict=True` means the day a ruling lands and the defect is fixed, the
    witness XPASSes and THE SUITE GOES RED. It cannot be quietly forgotten. The
    correct response to that red is to delete the `xfail` marker and keep the
    assertion - the witness becomes the ruling's pin, in place.

NOTHING IN `src/` WAS CHANGED BY THE PASS THAT WROTE THIS FILE. These tests do
not encode a preference for any particular remedy; each asserts the property the
REVIEW claimed was violated, so that whichever remedy a ruling picks, satisfying
the assertion is evidence the finding was closed.

ISOLATION: every test runs under `tests/conftest.py`'s autouse fixture, which
redirects all 25 injectable durable paths into a per-test tmp dir. The seeds are
deliberately NOT redirected (Rulings 32/39), so these measure AUREA against her
real founding doctrines and scars - which is the whole point.
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from src.aurea_core import AureaCore


# =====================================================================
# HELPERS
# =====================================================================

def _true_mass(topo) -> float:
    return sum(n.mass for n in topo.nodes.values())


def _edge_set(topo):
    return {tuple(sorted([nid, other]))
            for nid, node in topo.nodes.items() for other in node.edges}


def _one_way_edges(topo):
    return [(nid, other) for nid, node in topo.nodes.items()
            for other in node.edges
            if other in topo.nodes and nid not in topo.nodes[other].edges]


def _restart(core) -> AureaCore:
    """Persist and construct a fresh core over the same (redirected) paths."""
    core.save_state()
    return AureaCore()


def _ledger_lines(ledger) -> list:
    path = ledger.ledger_path
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


# =====================================================================
# S1 - TCA RESTART IDEMPOTENCE  (finding (f))
#
# CONFIRMED, with a shape sharper than the review's. Mass does not inflate
# without bound: it locks at EXACTLY 2x from the first restart onward, because
# `load_from_file` recomputes `total_mass` from the loaded nodes and then
# `AureaCore.__init__` re-places every scar and doctrine through `add_node`,
# which REPLACES `self.nodes[node_id]` but increments `self.total_mass`
# unconditionally (`tca_core.py:292-293`; `Constellation.add_node`, `:163-165`).
#
# The consequential half is NOT the mass. It is that the restarted graph is a
# DIFFERENT GRAPH, and its gravity centers differ - the exact quantity Ruling 57
# was written to repair.
# =====================================================================

def test_witness_total_mass_survives_a_restart_unchanged():
    """`total_mass` must equal the sum of the masses actually present.

    Measured at `0b2072c`: 130.6 fresh -> 261.2 after one restart, and STABLE at
    261.2 thereafter (the load recomputed from nodes, then re-placement doubled
    it again). A permanent 2x overcount, not an unbounded drift.

    RETIRED 2026-08-02 BY RULING 65 - marker deleted, assertion KEPT, per PATH
    v39's close instruction. This was `@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (f): total_mass is exactly 2x the true node-mass sum after any
    restart. add_node replaces by id but increments mass unconditionally."))`.
    It now passes for TWO independent reasons, and that is deliberate: res.1
    deleted the load-then-re-add path entirely, and res.6 made replacement
    mass-correct on its own terms so the arithmetic does not depend on nobody
    re-placing a node.
    """
    core = AureaCore()
    fresh = core.tca.topology.total_mass
    assert fresh == pytest.approx(_true_mass(core.tca.topology))

    core = _restart(core)
    topo = core.tca.topology
    assert topo.total_mass == pytest.approx(_true_mass(topo)), (
        f"total_mass={topo.total_mass} but the nodes present sum to "
        f"{_true_mass(topo)}; fresh run reported {fresh}")


def test_witness_gravity_centers_survive_a_restart_unchanged():
    """THE ONE THAT BORE ON RULING 57.

    Ruling 57 res.2 made centers follow edges. It did not make the EDGE SET
    restart-invariant, so the center of her largest constellation was a function
    of whether this was a fresh run or a resumed one.

    RETIRED 2026-08-02 BY RULING 65 - marker deleted, assertion KEPT. This was
    `@pytest.mark.xfail(strict=True, reason=("CONFIRMED (f), the consequential
    half: identity_core's gravity center moves AVT.014 -> Delta-77 across a
    restart, because the restarted graph carries 9 edges the fresh graph does
    not."))`. Ruling 65 does not repair the center; it removes the divergent
    graph the center was being computed from.
    """
    core = AureaCore()
    before = {cid: c.gravity_center
              for cid, c in core.tca.topology.constellations.items()}
    core = _restart(core)
    after = {cid: c.gravity_center
             for cid, c in core.tca.topology.constellations.items()}
    assert after == before, (
        "gravity centers moved across a restart: "
        + repr({k: (before[k], after[k]) for k in before if before[k] != after[k]}))


def test_witness_the_edge_set_survives_a_restart_unchanged():
    """The restarted graph must be the fresh graph.

    The 9 additions were all `scar.linked_doctrines` back-references. On a fresh
    run `place_scar` runs before any doctrine node exists, so its reverse loop
    forms nothing (Ruling 57, KNOWN AND FLAGGED). On a restart every node was
    already loaded, so the same loop fired - and the restart silently performed
    the repair the record documents as NOT done.

    RETIRED 2026-08-02 BY RULING 65 - marker deleted, assertion KEPT. This was
    `@pytest.mark.xfail(strict=True, reason=("CONFIRMED (f): a restart adds 9
    edges - exactly the reverse-only seed links Ruling 57's own seam row records
    as forming no edge at construction."))`.

    RULING 65 res.8 IS WHAT THIS PIN NOW GUARDS, AND THE DIRECTION MATTERS: the
    rebuild reproduces the CONSTRUCTION graph exactly - 21 edges, not 40 - and
    Ruling 57's seam row STANDS UNTOUCHED. The reverse-only links still form no
    edge. This ruling does not repair them and must not silently perform half of
    that repair, which is precisely what the restart was doing.
    """
    core = AureaCore()
    before = _edge_set(core.tca.topology)
    core = _restart(core)
    after = _edge_set(core.tca.topology)
    assert after == before, (
        f"only after restart: {sorted('|'.join(p) for p in after - before)}; "
        f"only before: {sorted('|'.join(p) for p in before - after)}")


def test_witness_no_edge_is_one_way_after_a_restart():
    """THE CAUSE, not just the symptom.

    RETIRED 2026-08-02 BY RULING 65 - marker deleted, assertion KEPT. This was
    `@pytest.mark.xfail(strict=True, reason=("CONFIRMED (f), previously
    unrecorded anywhere: a restart leaves 9 ONE-WAY edges. This is the mechanism
    behind the gravity-center move."))`.

    Order of events on a restart, under the DELETED read path:
      1. every node loads, scars and doctrines alike;
      2. the scar loop re-places each scar; its reverse loop now FINDS the
         doctrine nodes and calls `create_edge`, which writes BOTH directions;
      3. the doctrine loop then re-places each doctrine, and `add_node` installs
         a FRESH node whose `edges` is empty - wiping the back-reference.

    Result: the scar holds an edge to the doctrine and the doctrine holds
    nothing back. `_recalculate_center` scores `mass * len(edges)`, so the scar
    side gains centrality the doctrine side never gains, and `identity_core`'s
    center flips from a doctrine to a scar.
    """
    core = _restart(AureaCore())
    one_way = _one_way_edges(core.tca.topology)
    assert not one_way, f"{len(one_way)} one-way edges after restart: {one_way}"


def test_witness_genesis_places_each_seed_doctrine_once(monkeypatch):
    """The duplication the review alleged on the genesis path.

    `_create_seed_doctrines` called `place_doctrine` per doctrine, and the loop
    immediately below it in `__init__` placed every doctrine in the codex -
    including the three just seeded. Reached only when the codex loads empty, so
    it was dormant in production; it was real, and it was on a live path.

    RETIRED 2026-08-02 BY RULING 65 res.5 - marker deleted, assertion KEPT. This
    was `@pytest.mark.xfail(strict=True, reason=("CONFIRMED (f), fresh-run half:
    on the genesis fallback the three seed doctrines are placed TWICE,
    overcounting mass by 15.0."))`.

    DIVERGENCE RECORDED AT THE SITE: the Ruling 65 handoff and the manifest's
    pin (a) both say the pass retires "the four TCA strict-xfail witnesses".
    FIVE were retired. This is the fifth, and it is retired by res.5 ("GENESIS
    PLACES ONCE") rather than by res.1's restart identity - the manifest's own
    pin (e) covers it in terms, so the count in (a) is the thing that was short,
    not the scope of the ruling. Reported rather than silently absorbed.
    """
    from src.doctrine.codex import Codex
    monkeypatch.setattr(Codex, "load_from_file", lambda self: None)

    calls = []
    from src.topology.tca_integration import TCAIntegration
    real = TCAIntegration.place_doctrine
    monkeypatch.setattr(
        TCAIntegration, "place_doctrine",
        lambda self, d: (calls.append(d.id), real(self, d))[1])

    core = AureaCore()
    dupes = {i for i in calls if calls.count(i) > 1}
    assert not dupes, f"placed more than once: {sorted(dupes)} (calls={calls})"
    topo = core.tca.topology
    assert topo.total_mass == pytest.approx(_true_mass(topo))


# =====================================================================
# S2 - THE ANCESTRY ORPHAN  (finding (g))
#
# CONFIRMED, and BROADER than the review's `None` case: the mint at
# `aurea_core.py:673` is deliberately outside the `try:` at :702, while SPL's
# `raw_input.strip()` (`spl.py:40`) is inside it. EVERY non-`str` input
# therefore writes a permanent CLM line, raises inside the try, degrades into
# `result['errors']`, and returns normally with no echo and no node.
#
# `""` and whitespace are NOT orphans - they are perceived and produce an echo.
# The soak's 40/40 one-to-one observation was true of what it measured; the
# property is simply not GUARANTEED for all accepted call shapes.
# =====================================================================

@pytest.mark.parametrize("bad", [None, 12345, ["a"], {"k": "v"}, object()],
                         ids=["None", "int", "list", "dict", "object"])
@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (g): a non-str input mints a permanent ancestry record for a "
    "claim that is never perceived - no echo, no node, no linkage."))
def test_witness_a_rejected_input_leaves_no_orphan_ancestry_record(bad):
    """WITNESS. A ledger line must correspond to a claim actually perceived.

    That correspondence is asserted verbatim in `aurea_core.py:667` ("keeps
    ledger lines in ONE-TO-ONE correspondence with claims actually perceived")
    and relied on in `tests/test_ruling58.py:224`. It holds for the suspension
    gate, which is what that pin covers. It does not hold here.
    """
    core = AureaCore()
    before = len(_ledger_lines(core.ancestry))
    result = core.process_input(bad)
    after = len(_ledger_lines(core.ancestry))

    if result.get("echo") is None:
        assert after == before, (
            f"no echo was built, yet {after - before} ancestry line(s) were "
            f"written (claim_id={result.get('claim_id')!r}, "
            f"errors={result.get('errors')!r})")


def test_an_empty_or_whitespace_claim_is_perceived_and_is_not_an_orphan():
    """GUARD of existing behaviour, and a deliberate CONTROL for the witness
    above: the orphan is caused by the TYPE, not by emptiness. `""` and `"  "`
    strip cleanly, build an echo, and their ledger lines are honest."""
    core = AureaCore()
    for claim in ("", "   "):
        before = len(_ledger_lines(core.ancestry))
        result = core.process_input(claim)
        assert result["echo"] is not None, f"{claim!r} built no echo"
        assert len(_ledger_lines(core.ancestry)) == before + 1


# =====================================================================
# S3 - `source="user"` STILL MANUFACTURED  (finding (h))
#
# CONFIRMED at both sites the review named: `spl.py:44` writes it into
# `Echo.source`, and `aurea_core.py:722` stamps `source:{source}` onto the
# echo's topology node. Ruling 58 DEMOTED the field and swept its readers; it
# did not stop the value being manufactured.
# =====================================================================

@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (h): a claim whose recorded origin is UNDECLARED with all five "
    "fields ABSENT simultaneously displays 'user' on the echo and the node."))
def test_witness_an_undeclared_claim_does_not_display_a_human_source():
    """WITNESS. The two surfaces must not contradict the record.

    Measured on one pass: `origin_kind='undeclared'`, `asserted_by` ABSENT -
    and `Echo.source == 'user'` with the node tagged `source:user`. The ledger
    says nobody said; the display says a human did.
    """
    core = AureaCore()
    result = core.process_input("A claim with no declared origin.")

    line = json.loads(_ledger_lines(core.ancestry)[-1])
    assert line["origin_kind"] == "undeclared"
    assert line["asserted_by"]["state"] == "absent"

    echo_source = getattr(result["echo"], "source", None)
    node = core.tca.topology.nodes.get(
        result["pass_nodes"][0] if result["pass_nodes"] else None)
    tags = sorted(node.tags) if node else []

    assert echo_source != "user", (
        f"Echo.source={echo_source!r} while the ancestry record says "
        f"UNDECLARED/ABSENT")
    assert "source:user" not in tags, f"node tags manufacture a human: {tags}"


# =====================================================================
# S4 - `default=str` ROUND-TRIP  (finding (i))
#
# CONFIRMED, identically, on all three record ledgers:
#   cae.py:262 - claim_ancestry.py:466 - prediction_ledger.py:484
#
# bytearray / set / frozenset / arbitrary objects persist as their `repr`
# STRING; an int-keyed map persists with STRING keys; NaN and Infinity persist
# as bare `NaN` / `Infinity`, which are INVALID under strict JSON (a separate
# defect in the same family - `default=str` never sees them). A tuple-keyed map
# is the one shape that raises rather than diverging.
# =====================================================================

_NONCANONICAL = {
    "bytearray": bytearray(b"abc"),
    "set": {1, 2, 3},
    "int_keyed_map": {1: "x"},
}


@pytest.mark.parametrize("name", sorted(_NONCANONICAL))
@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (i): the persisted form of a recorded field differs from its "
    "live form. An argument of record must not change shape on the way to disk."))
def test_witness_cae_round_trips_a_recorded_value_unchanged(name, tmp_path):
    """WITNESS on the audit ledger - the store whose whole purpose is that its
    records can be CITED later (3a:112)."""
    from src.doctrine.cae import CAE
    leaf = _NONCANONICAL[name]
    ledger = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    ledger.record(event="e", target="T", payload=leaf)

    live = ledger.entries[-1]["payload"]
    persisted = json.loads(
        ledger.ledger_path.read_text(encoding="utf-8").splitlines()[-1])["payload"]
    assert persisted == live and type(persisted) is type(live), (
        f"live={live!r} ({type(live).__name__}) but "
        f"persisted={persisted!r} ({type(persisted).__name__})")


@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (i), separate from default=str: NaN and Infinity are written as "
    "bare non-standard constants, so the line is not valid JSON."))
def test_witness_the_ledger_writes_strictly_valid_json(tmp_path):
    """WITNESS. A forensic log outlives the code that wrote it, so it must be
    readable by a strict parser in any language - not only by Python's `json`,
    which accepts `NaN`/`Infinity` as an extension."""
    from src.doctrine.cae import CAE
    ledger = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    ledger.record(event="e", target="T", payload=float("nan"))
    ledger.record(event="e", target="T", payload=float("inf"))

    def strict(line):
        return json.loads(line, parse_constant=_reject)

    bad = []
    for line in ledger.ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            strict(line)
        except ValueError as exc:
            bad.append(f"{line[:80]}... -> {exc}")
    assert not bad, "non-standard JSON constants written:\n" + "\n".join(bad)


def _reject(constant):
    raise ValueError(f"non-standard JSON constant {constant!r}")


@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (i), the severe consequence: one non-canonical leaf in a proof "
    "completes the mutation, is audited by CAE stringified, then permanently "
    "disables every subsequent state checkpoint."))
def test_witness_a_proof_that_passes_validation_can_be_persisted(tmp_path):
    """WITNESS - THE MOST CONSEQUENTIAL RESULT OF THE VERIFICATION PASS.

    `validate_proof` (`mutation_proof.py:266`) checks class, a non-empty
    contradiction core, and a non-empty invariant record. It does NOT check
    canonical serializability. CAE writes with `default=str`; SAE's
    `atomic_write_json` (`sae.py:1372`) does NOT pass `default`.

    So a proof carrying, say, a bytearray:
      - PASSES pre-flight;
      - the ancestor is fossilized and the successor installed;
      - a ceiling slot is spent and a permanent CAE entry is written
        (with the leaf silently stringified);
      - and THEN `_persist()` raises `TypeError`.

    The mutation record never reaches disk, so Ruling 47's reversion path has
    nothing to read - while the Codex, in memory, has already moved. And the
    failure is not transient: `sae.save()` and `AureaCore.save_state()` raise
    for the remainder of the process, so NO store is checkpointed again.
    """
    from src.doctrine.mutation_proof import (
        DoctrineMutationProof, ContentDelta, all_criteria_absent)
    from src.utils.models import Doctrine

    core = AureaCore()
    target = "Doctrine-3"
    assert target in core.codex.doctrines

    proof = DoctrineMutationProof(
        contradiction_core={"triggers": ["t"], "pressure": 1.0,
                            "evidence_blob": bytearray(b"raw")},
        scar_lineage=("Scar-0",),
        echo_provenance={},
        content_delta=ContentDelta(ancestor_id=target, name_before="a",
                                   name_after="b", description_before="x",
                                   description_after="y"),
        preserved_invariants=all_criteria_absent(),
        unresolved_residue=(),
    )
    successor = Doctrine(id=f"{target}::v2", name="b",
                         created_at=datetime.now(), description="y",
                         mutation_lineage=[target])

    core.sae.mutate_doctrine(target, successor, collapse_lineage="Scar-0",
                             proof=proof)
    core.save_state()


# =====================================================================
# S5 - LOCAL-COUNTER MINTING  (finding (j))
#
# CONFIRMED for the MINT on all three ledgers: each derives its maximum at
# construction and then increments a private `_seq`, so two live instances over
# one path both mint the same id.
#
# REFUTED for the one-resolution guarantee - see the guard at the end. That half
# of the review's claim does not hold: `resolve()` re-reads the FILE, so a
# second instance is correctly refused. (It remains racy between that read and
# the append; that is a narrower claim than "process-local", and the ruling
# should be told the difference.)
# =====================================================================

@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (j): two CAE instances over one path both mint CAE-001."))
def test_witness_cae_ids_are_unique_across_two_writers(tmp_path):
    """WITNESS on the append-only ledger whose ids are meant to be CITABLE.
    Ruling 53 closed the re-derivation hole for an UNREADABLE ledger; a second
    concurrent writer reaches the same duplicate-id outcome by another door."""
    from src.doctrine.cae import CAE
    path = str(tmp_path / "cae.jsonl")
    a, b = CAE(ledger_path=path), CAE(ledger_path=path)
    minted = [a.record(event="e", target="T"), b.record(event="e", target="T"),
              a.record(event="e", target="T"), b.record(event="e", target="T")]
    assert len(set(minted)) == len(minted), f"duplicate ids minted: {minted}"


@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (j): two ClaimAncestryLedger instances both mint CLM-0001, so "
    "Ruling 60's descent edges can point at two different claims."))
def test_witness_claim_ids_are_unique_across_two_writers(tmp_path):
    """WITNESS. A duplicated CLM id is worse than a duplicated CAE id: Ruling 60
    resolves descent by EXACT STRING EQUALITY on exactly these ids."""
    from src.external.claim_ancestry import (
        ClaimAncestryLedger, OriginDeclaration, OriginKind)
    path = str(tmp_path / "anc.jsonl")
    a, b = ClaimAncestryLedger(ledger_path=path), ClaimAncestryLedger(ledger_path=path)
    decl = OriginDeclaration(kind=OriginKind.HUMAN)
    minted = [a.record(decl).claim_id, b.record(decl).claim_id,
              a.record(decl).claim_id, b.record(decl).claim_id]
    assert len(set(minted)) == len(minted), f"duplicate ids minted: {minted}"


@pytest.mark.xfail(strict=True, reason=(
    "CONFIRMED (j): two PredictionLedger instances both mint PRD-0001."))
def test_witness_prediction_ids_are_unique_across_two_writers(tmp_path):
    """WITNESS. Two commitments sharing an id are indistinguishable to
    `resolve()`, which is the module's own stated hazard (`:178`)."""
    from src.external.prediction_ledger import PredictionLedger, provided
    path = str(tmp_path / "prd.jsonl")
    a, b = PredictionLedger(ledger_path=path), PredictionLedger(ledger_path=path)
    first = a.commit(expected_result="x", success_criteria=provided("s"))
    second = b.commit(expected_result="y", success_criteria=provided("s"))
    assert first.prediction_id != second.prediction_id, (
        f"both minted {first.prediction_id}")


def test_the_one_resolution_guarantee_holds_across_two_ledger_instances(tmp_path):
    """GUARD of existing behaviour - and the REFUTED half of finding (j).

    The review held that `resolve()`'s one-resolution guarantee is
    process-local. It is not: the guard re-reads the FILE, so a SECOND instance
    constructed over the same path correctly refuses to re-score a commitment
    the first one already resolved.

    Pinned because it is a real property that this pass verified and that a
    future change to the minting story could easily break by accident.
    """
    from src.external.prediction_ledger import (
        PredictionLedger, PredictionOutcome, provided)
    path = str(tmp_path / "prd.jsonl")
    first = PredictionLedger(ledger_path=path)
    commitment = first.commit(expected_result="the bridge will hold",
                              success_criteria=provided("it holds"))
    first.resolve(commitment.prediction_id, PredictionOutcome.CONFIRMED,
                  criterion="success_criteria")

    second = PredictionLedger(ledger_path=path)
    with pytest.raises(ValueError, match="already resolved"):
        second.resolve(commitment.prediction_id, PredictionOutcome.FALSIFIED,
                       criterion="success_criteria")

    assert len(path_lines(path)) == 2, "the refused re-score must write nothing"


def path_lines(path):
    from pathlib import Path
    return Path(path).read_text(encoding="utf-8").splitlines()
