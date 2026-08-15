"""
test_m4_chaos_gamma.py - M4-γ: THE REPLAY AND THE CHAOS FAMILY.

Heading Phase 4 - *"state transitions deterministic given prior state plus
recorded acquisitions; nondeterminism confined to acquisition points"* - and
item 13.5's interrupt-at-an-acquisition-point.

**THE CLAIM IS ONLY TESTABLE BECAUSE OF THE TWO PASSES UNDER IT.** M4-α made the
acquisitions recorded facts; M4-β' removed the last wall-clock id mints, so two
runs of one tree no longer differ by construction. Before either, a replay could
not have been identical for reasons that said nothing about determinism.

RED-FIRST: at `c7de747` the replay comparison is unwritable (no instrument) AND
unmeetable (three id spaces minted from a clock, so a second run of the same
claims produced a different census). The second half was WATCHED in a detached
worktree there and is reported in the pass's own record.

A CHAOS CASE THAT CANNOT FAIL PROVES NOTHING (Ruling 35), so every class below
carries a FIRES CONTROL that drives the failure and observes the assertion catch
it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.replay import ReplayAuditFailure, census, compare, verify
from src.aurea_core import AureaCore
from src.external.acquisition_ledger import (AcquisitionChannel,
                                             AcquisitionLedger)
from src.external.claim_ancestry import ClaimAncestryLedger
from src.external.model_provider import ingest_model_assertion
from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread

IDENTITY = "openai/gpt-9/2026-01-15"

# A small claim set that exercises several exits (collapse, paradox, carry).
CLAIMS = [
    "Fracture Carried is false.",
    "this statement is false",
    "Honesty is pointless.",
    "It is raining and it is not raining.",
    "Doctrine-0 is true.",
]


def _payload(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# =====================================================================
# (a) REPLAY - the milestone's claim
# =====================================================================

def test_a_a_recorded_run_replays_to_an_identical_census():
    """**THE HEADLINE.** Drive a run, replay it FROM ITS OWN ACQUISITION LEDGER,
    compare end-state censuses.

    NOTHING IS EXCLUDED FROM THE COMPARISON AND NO WALL FIELD IS NORMALIZED -
    the census is clock-free by construction, which is what M4-β' made possible.
    A `modulo the declared record-side wall fields` allowance was expected here
    and turned out to be unnecessary; the exactness is the finding.
    """
    report = verify()

    assert report["arrivals"]["recorded"] == report["arrivals"]["replayed"]
    assert report["comparison"]["identical"], (
        f"the replay diverged: {report['comparison']['moved']}")
    assert report["comparison"]["fields_compared"] > 10, (
        "a comparison over almost nothing is identical for the wrong reason")


def test_a_the_replay_reads_the_ledger_and_nothing_else():
    """The arrivals come from the RECORD. A replay seeded from the original
    claim list would prove only that the harness kept a copy."""
    report = verify(claims=CLAIMS)
    assert report["arrivals"]["replayed"] == len(CLAIMS)
    assert report["comparison"]["identical"]
    # The replayed run rebuilt the same acquisition ledger from the same
    # arrivals - ids included, because the ordinal is a function of order.
    original = report["census"]["acquisitions"]
    replayed = report["replayed_census"]["acquisitions"]
    assert original == replayed
    assert original["last_id"] == f"ACQ-{len(CLAIMS):04d}"


def test_a_the_comparison_fires_when_the_censuses_differ():
    """FIRES CONTROL for class (a). `compare` must REPORT a difference, or the
    identical verdict above is satisfied by a comparator that never looks."""
    verdict = compare({"scars": 3, "echoes": 5}, {"scars": 4, "echoes": 5})
    assert verdict["identical"] is False
    assert verdict["moved"] == {"scars": {"original": 3, "replayed": 4}}


def test_a_the_replay_report_carries_a_passing_audit_for_both_halves():
    """RULING 67: the audit RESULT is a REQUIRED FIELD, and a replay has TWO
    runs to answer for - the recorded one and the replayed one."""
    report = verify(claims=CLAIMS)
    for key in ("footprint_audit", "replay_footprint_audit"):
        audit = report[key]
        assert audit["performed"] is True
        assert audit["pass"] is True
        assert audit["foreign_writes"] == []
        assert audit["configured_paths"] == 33   # M6-α: 32 -> 33, the ruled movement


def test_a_an_audit_failure_is_loud_and_typed():
    """FIRES CONTROL for the audit. A failing audit must FAIL THE RUN, never
    annotate a report that then gets compared against a clean one."""
    assert issubclass(ReplayAuditFailure, Exception)
    import scripts.replay as replay_mod
    source = Path(replay_mod.__file__).read_text(encoding="utf-8")
    assert "raise ReplayAuditFailure(" in source
    assert 'if not audit["pass"]:' in source


# =====================================================================
# (b) AN UNCLEAN RESTART ON A SUSPENSION STORE - 13.5 + the new invariant
# =====================================================================

@pytest.mark.parametrize("name,cls,prefix,suspend", [
    ("csa", CSA, "CSA-", lambda s: s.suspend("volatile", pressure=0.8)),
    ("veiled", VeiledThread, "VT-", lambda s: s.suspend("unresolved", pressure=0.6)),
    ("bs", BlackSphere, "BS-", lambda s: s.suspend("paradox", pressure=0.9)),
], ids=["csa", "veiled", "bs"])
def test_b_an_unclean_restart_mid_sequence_keeps_the_high_water(
        name, cls, prefix, suspend, tmp_path):
    """13.5's interrupt, aimed at the store M4-β' changed.

    **NO `save_to_file` IS CALLED BY THIS TEST** - the store persists at its own
    write, so the restart needs no cooperation. The process dies mid-sequence and
    the resumed one must still know how many ids were issued, or the very next
    mint reissues a live one.
    """
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    for _ in range(3):
        suspend(store)

    del store                                     # the unclean death
    resumed = cls(filepath=str(path))

    assert resumed.high_water == 3
    assert len(resumed.entries) == 3
    assert suspend(resumed).id == f"{prefix}0004"


@pytest.mark.parametrize("name,cls,prefix,suspend", [
    ("csa", CSA, "CSA-", lambda s: s.suspend("volatile", pressure=0.8)),
    ("veiled", VeiledThread, "VT-", lambda s: s.suspend("unresolved", pressure=0.6)),
    ("bs", BlackSphere, "BS-", lambda s: s.suspend("paradox", pressure=0.9)),
], ids=["csa", "veiled", "bs"])
def test_b_a_restart_that_loses_every_entry_still_keeps_the_mark(
        name, cls, prefix, suspend, tmp_path):
    """THE HARD CASE: the interrupt lands right after a removal, so the resumed
    store holds NOTHING and must still refuse to reissue.

    This is the witnessed defect's exact shape crossing a process boundary -
    the one place a derive-from-survivors mint looks most reasonable and is most
    wrong.
    """
    path = tmp_path / f"{name}.json"
    store = cls(filepath=str(path))
    minted = [suspend(store).id for _ in range(3)]
    store.purge_old_entries(keep_recent=0)
    store.save_to_file()
    del store

    resumed = cls(filepath=str(path))
    assert resumed.entries == {}
    assert resumed.high_water == 3
    after = suspend(resumed).id
    assert after not in minted and after == f"{prefix}0004"


def test_b_the_divergence_detector_reads_clean_across_the_interrupt(tmp_path):
    """13.5's own sentence, driven through the REAL pipeline.

    The detector runs at every `AureaCore` construction (Ruling 79, AST-pinned
    to `__init__`'s last act), so the resumed core has already run it. A finding
    here would mean it had started reporting survivable crash residue.
    """
    acq = tmp_path / "acquisitions.jsonl"
    clm = tmp_path / "claim_ancestry.jsonl"

    first = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq)),
                      ancestry=ClaimAncestryLedger(ledger_path=str(clm)))
    for claim in CLAIMS:
        first.process_input(claim)
    assert first.divergence_findings == []

    # THE INTERRUPT, at an acquisition point: a half-written arrival, then death.
    with open(acq, "a", encoding="utf-8") as handle:
        handle.write('{"acquisition_id": "ACQ-0006", "channel": "user_i')
    del first

    resumed = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq)),
                        ancestry=ClaimAncestryLedger(ledger_path=str(clm)))
    assert resumed.divergence_findings == [], (
        f"the detector reported {resumed.divergence_findings} across an unclean "
        f"restart. Crash residue is survivable and already adjudicated by "
        f"Ruling 78's ordering law.")
    assert resumed.divergence_log_failures == []

    # ...AND THE BOUNDARY'S CLOCK STILL REFUSES TO REISSUE THE TORN ORDINAL.
    # `ACQ-0006`'s bytes reached disk, so its ordinal is BURNED (Ruling 69
    # res.2's raw-text scan) and the next mint is 0007.
    result = resumed.process_input("after the crash")
    claim = resumed.ancestry.get(result["claim_id"])
    assert claim.acquisition_ref == "ACQ-0007"

    # CHANGED BY A RULING, 2026-08-15 (M4-δ) - the Ruling-14 precedent, and this
    # pin's own message is what asked for the change:
    #
    #     OLD (M4-γ):
    #         assert resumed.acquisitions.read_all()[-1].acquisition_id
    #                == "ACQ-0005"
    #         ... "if this now reads ACQ-0007 the torn-append seam has been
    #             ruled on - update this pin and its twin, citing it"
    #     NEW (M4-δ):
    #         ... == "ACQ-0007"
    #
    # **THE WORKAROUND'S REASON IS GONE.** γ read the CLAIM rather than the
    # ledger's last line because a torn append swallowed the record that
    # followed it; δ's column-zero law opens a new line for that record, so the
    # LEDGER can be read directly again. The claim assertion above stays - it is
    # now a second, independent view of the same fact rather than a substitute
    # for one that could not be taken.
    assert resumed.acquisitions.read_all()[-1].acquisition_id == "ACQ-0007", (
        "M4-δ: the post-tear record survives as its own line, so the ledger's "
        "last line IS the record just written")

    # AND THE TORN FRAGMENT IS STILL REFUSED - the boundary was repaired, the
    # record never was.
    assert resumed.acquisitions.get("ACQ-0006") is None


def test_b_the_restart_assertions_fire_when_the_mark_is_lost(tmp_path):
    """FIRES CONTROL for class (b). A store whose envelope is stripped from the
    file must FAIL the resumed-mark assertion - otherwise these pass for a store
    that never recorded anything."""
    path = tmp_path / "vt.json"
    store = VeiledThread(filepath=str(path))
    for _ in range(3):
        store.suspend("u", pressure=0.6)

    stripped = _payload(path)["entries"]              # the envelope, removed
    path.write_text(json.dumps(stripped), encoding="utf-8")

    resumed = VeiledThread(filepath=str(path))
    assert resumed.high_water == 3, (
        "sanity: these ARE ordinal ids, so the legacy derivation reads them")

    # ...and with the entries gone too, the mark is genuinely unrecoverable -
    # which is precisely why the envelope, and not the entries, is the record.
    path.write_text(json.dumps([]), encoding="utf-8")
    empty = VeiledThread(filepath=str(path))
    assert empty.high_water == 0, (
        "the FIRES control: strip the envelope AND the entries and the mark is "
        "lost - the assertions above are not vacuous")


# =====================================================================
# (c) THE CORRELATION JOIN, BOTH DIRECTIONS
# =====================================================================

def test_c_the_exchange_halves_join_on_one_correlation(tmp_path):
    """A model REQUEST and its RESPONSE are two arrivals sharing one
    correlation - and the correlation is a RECORDED ID, never a minted second
    one (it is the `ACQ-` id of the half that opened the exchange)."""
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))

    request = core.acquisitions.record(
        "Will the bridge hold?", channel=AcquisitionChannel.MODEL_EXCHANGE)
    ingest_model_assertion(core.process_input, "The bridge will hold.",
                           IDENTITY, correlation_id=request.acquisition_id)

    halves = core.acquisitions.correlated(request.acquisition_id)
    assert [h.acquisition_id for h in halves] == ["ACQ-0001", "ACQ-0002"]
    assert [h.payload for h in halves] == ["Will the bridge hold?",
                                           "The bridge will hold."]
    assert {h.channel for h in halves} == {AcquisitionChannel.MODEL_EXCHANGE}
    assert halves[0].correlation_id == halves[0].acquisition_id, (
        "the opening half correlates with itself")


def test_c_the_acq_clm_join_resolves_in_both_directions(tmp_path):
    """The WRITE points one way (Ruling 60's forced direction); the READ
    resolves both, which is what makes the one-way write sufficient."""
    core = AureaCore(
        acquisitions=AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl")),
        ancestry=ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl")))
    for claim in CLAIMS:
        core.process_input(claim)

    claims = core.ancestry.read_all()
    assert len(claims) == len(CLAIMS)
    for index, claim in enumerate(claims, start=1):
        # forward: claim -> arrival
        assert claim.acquisition_ref == f"ACQ-{index:04d}"
        arrival = core.acquisitions.get(claim.acquisition_ref)
        assert arrival is not None and arrival.payload == CLAIMS[index - 1]
        # back: arrival -> claim
        back = [c.claim_id for c in claims
                if c.acquisition_ref == arrival.acquisition_id]
        assert back == [claim.claim_id]


def test_c_an_unrelated_correlation_returns_nothing(tmp_path):
    """FIRES CONTROL for class (c). `correlated` must DISCRIMINATE - an id join
    that returned everything would satisfy the joins above."""
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))
    core.process_input("one arrival")

    assert core.acquisitions.correlated("ACQ-9999") == ()
    assert len(core.acquisitions.correlated("ACQ-0001")) == 1


# =====================================================================
# (d) THE INSTRUMENT'S OWN SHAPE
# =====================================================================

def test_d_the_instrument_grants_nothing_and_owns_nothing():
    """Docket R's EL1 in this instrument's shape: no `src/` module imports it,
    and it holds no store of its own."""
    import ast
    repo = Path(__file__).resolve().parents[1]
    offenders = []
    for path in sorted((repo / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            if any("replay" in n for n in names):
                offenders.append(f"{path.relative_to(repo).as_posix()}:{node.lineno}")
    assert offenders == [], f"a src/ module imports the replay instrument: {offenders}"

    import scripts.replay as replay_mod
    source = Path(replay_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    writes = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr in {"save_to_file", "save_state", "record"}]
    assert writes == [], f"the instrument writes a store at {writes}"


def test_d_the_isolation_and_the_audit_are_imported_not_copied():
    """ONE implementation, four callers (Ruling 67). A second copy would be a
    second definition free to drift, invisibly, because both would look right
    alone."""
    import ast
    import scripts.replay as replay_mod
    tree = ast.parse(Path(replay_mod.__file__).read_text(encoding="utf-8"))

    imported = {n.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and (node.module or "").endswith("soak")
                for n in node.names}
    assert {"isolate", "footprint_audit"} <= imported

    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert not ({"isolate", "footprint_audit"} & defined), (
        "the instrument redefines the isolation it should be importing")


def test_d_the_ancestry_limitation_is_declared_not_papered_over():
    """The one thing a replay CANNOT reconstruct, stated in the instrument.

    An acquisition records the ARRIVAL; the ancestry DECLARATION is the claim's
    record and is minted after it. A replay therefore re-drives every arrival
    faithfully and replays a declared origin as UNDECLARED - which is the two
    records being about different things, not a defect of either. It is pinned
    so nobody later reads an identical census as proof that declarations
    round-trip.
    """
    import scripts.replay as replay_mod
    source = Path(replay_mod.__file__).read_text(encoding="utf-8")
    # Matched on the PHRASE rather than a whole sentence: this repo has been
    # bitten eight times by a scanner that broke on a word of surrounding
    # markup, and a pin that fails when someone bolds a sentence is a pin that
    # gets deleted rather than read.
    assert "ancestry DECLARATION" in source
    assert "UNDECLARED" in source

    # ...and the limitation is REAL, measured rather than asserted.
    from src.external.claim_ancestry import OriginKind
    report = verify(claims=["a claim with no declaration"])
    assert report["comparison"]["identical"], (
        "an arrival that declared nothing replays exactly")
    assert OriginKind.UNDECLARED is OriginKind("undeclared")


def test_d_the_census_covers_every_surface_the_two_passes_added():
    """**FOUND BY A SURVIVING MUTANT**, and it is the comparator gap in its
    other spelling.

    Dropping a surface from the census leaves the replay comparison IDENTICAL -
    both sides lose it together - so "identical" is equally satisfied by a
    census that measures less and less. The M4-α slate found the same shape in a
    comparator that never reported; here it is a census that never looks.

    THE KEY SET IS PINNED EXACTLY rather than as a subset: a surface added
    silently is as much a drift as one removed, and this is the one place that
    can be seen.
    """
    core = AureaCore()
    core.process_input("a claim, so the census has something to describe")
    keys = set(census(core))

    assert keys == {
        "acquisitions",            # M4-α: the boundary record
        "suspensions",             # M4-β': the high-water envelope
        "decay", "lineage", "placement",
        "echoes", "claims", "scars",
        "doctrines", "fossils",
        "topology_nodes", "topology_edges",
        "epoch", "structural_violations", "divergence_findings",
    }

    # ...and the two M4 surfaces carry REAL structure, not empty placeholders.
    snapshot = census(core)
    assert snapshot["acquisitions"]["lines"] == 1
    assert set(snapshot["suspensions"]) == {"csa", "veiled_thread",
                                            "black_sphere"}
    for store in snapshot["suspensions"].values():
        assert "high_water" in store and "entries" in store
