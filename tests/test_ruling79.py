"""
test_ruling79.py - RULING 79: THE CROSS-STORE DIVERGENCE DETECTOR.

    The disagreement is reported in her own vocabulary, and the report
    obligates nothing.

Registered by Ruling 78 res.4.iii. Every store passed its own integrity check;
the disagreement was BETWEEN them, and nothing in the tree could see it.

WHY THE FOUR WITNESSES MANUFACTURE THEIR STATES THROUGH REAL STORES
-------------------------------------------------------------------------------
The pure module is testable with hand-built dicts, and it is tested that way
too - but a detector pinned ONLY on hand-built dicts proves that a function
compares numbers, not that AUREA can see her own disagreement. Each of the four
kinds is therefore driven END TO END: a real mutation or a real claim cycle
through a live core, then a surgical edit to ONE durable file that removes the
counterpart a crash would have taken, then a fresh construction.

**EACH EDIT IS CHOSEN TO PRODUCE EXACTLY ONE KIND**, and that is harder than it
looks - the naive edits overlap (deleting a CLM line both orphans the join AND
lowers the floor beneath the id citing it). Where an edit would produce two
findings honestly, a different edit was chosen rather than a looser assertion,
and each witness asserts the EXACT set of kinds it expects.
"""

from __future__ import annotations

import ast
import json
from datetime import datetime
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.retrieval.divergence import (DivergenceFinding, DivergenceKind,
                                      detect_divergence)
from src.utils.models import Doctrine
from tests.proof_support import minimal_proof

REPO = Path(__file__).resolve().parents[1]
DIVERGENCE = "src/retrieval/divergence.py"


def _tree(rel: str) -> ast.Module:
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


def _src_files():
    return [p for p in sorted(REPO.joinpath("src").rglob("*.py"))
            if "__pycache__" not in p.parts]


def _mutate(core) -> str:
    """One real mutation through the real path. Returns the ancestor id."""
    ancestor = [d for d in core.codex.active()
                if not d.id.startswith("Doctrine-0")][0].id
    core.sae.mutate_doctrine(
        ancestor,
        Doctrine(id=f"{ancestor}::r79", name="Successor",
                 description="the belief after", created_at=datetime.now()),
        collapse_lineage="Scar-0", proof=minimal_proof("test_ruling79"))
    return ancestor


def _rewrite_epoch_state(core, edit):
    """Apply `edit` to the durable SAE state. The crash, performed surgically."""
    path = Path(core.sae.runtime_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    edit(payload)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _kinds(core):
    return {f["kind"] for f in core.divergence_findings}


def _of_kind(core, kind: DivergenceKind):
    return [f for f in core.divergence_findings if f["kind"] == kind.value]


# =====================================================================
# (a) THE MODULE IS PURE
# =====================================================================

def test_a_the_detector_is_stdlib_only_and_imports_no_store():
    """PIN (a) / res.1. `record_joins`' own pin form, and for its reason.

    **THIS IS WHAT MAKES "NEVER WRITES TO ANY STORE IT READS" STRUCTURAL RATHER
    THAN PROMISED.** A module that cannot reach a store cannot be talked into
    repairing one, and repair is the remedy this ruling forbids outright.

    It is also why `ledger_mint.ordinal_pattern` is not imported even though it
    solves the ordinal problem exactly: that module opens files.
    """
    imported = set()
    for node in ast.walk(_tree(DIVERGENCE)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert "src" not in imported, (
        f"the detector acquired a project import: {sorted(imported)}. It takes "
        f"ALREADY-READ records; a module that can reach a store can be made to "
        f"write one.")
    assert imported <= {"__future__", "dataclasses", "enum", "types", "typing"}, (
        f"the detector acquired a non-stdlib import: {sorted(imported)}")


def test_a_the_detector_opens_nothing_and_holds_no_path():
    """PIN (a), the other half - purity is about CALLS as well as imports."""
    source = (REPO / DIVERGENCE).read_text(encoding="utf-8")
    for node in ast.walk(_tree(DIVERGENCE)):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in {"open", "read_text", "write_text", "mkdir",
                                "unlink", "durable_append_text",
                                "atomic_write_text", "atomic_write_json"}, (
                f"the detector performs filesystem work: {name}")
    assert "Path(" not in source, "the detector holds a path"


# =====================================================================
# (b) REPORT-ONLY, AS STRUCTURE
# =====================================================================

def test_b_no_src_module_reads_the_divergence_log():
    """PIN (b) / res.4. **A FINDING GRANTS NOTHING AND GATES NOTHING.**

    EL1's law arriving at a second instrument, and pinned the same way: the
    wrong path is unexecutable rather than discouraged. The log is written and
    never read, so no decision anywhere in `src/` can come to depend on what a
    previous crash happened to leave behind.

    Scanned tree-wide rather than in `aurea_core` alone, so the module nobody
    has written yet is covered too.
    """
    readers = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name not in {"open", "read_text", "read_bytes", "readlines",
                            "load", "loads", "derive_max_ordinal"}:
                continue
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                rendered = ast.unparse(arg)
                if "divergence_log_path" in rendered or "DIVERGENCE_LOG_PATH" in rendered:
                    readers.append(f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    assert readers == [], f"the divergence log acquired a reader: {readers}"


def test_b_the_findings_surface_is_read_only_and_carries_no_magnitude():
    """PIN (b) / res.3. No severity, no score, no threshold - §9's bar #5.

    A magnitude here would be a coined threshold at the exact point somebody
    decides whether to act on a finding.
    """
    core = AureaCore()
    surface = core.get_system_status()["divergence"]
    assert set(surface) == {"findings", "count", "log_failures"}

    banned = {"severity", "score", "priority", "weight", "rank", "confidence",
              "threshold", "advice", "recommendation", "action"}
    source = (REPO / DIVERGENCE).read_text(encoding="utf-8").lower()
    for token in banned:
        assert f"{token}:" not in source and f"{token} =" not in source, (
            f"the detector coined a magnitude or an opinion: {token}")


# =====================================================================
# (c) EACH KIND, WITNESSED BY CONSTRUCTION
# =====================================================================

def test_c_epoch_count_ahead_is_detected():
    """PIN (c) / kind 1. **THE R78 CENSUS'S CENTRAL FINDING, AT REST.**

    THE MANUFACTURED STATE: a real mutation, then the durable epoch file loses
    its history while keeping its spend - which is exactly what a crash between
    the spend persist and the record persist leaves behind (Ruling 34 makes the
    spend durable at the moment of spending; R78's ordering law makes losing the
    record the conservative direction).

    THE CAE LEDGER IS CLEARED IN THE SAME EDIT, DELIBERATELY, so this witnesses
    ONE kind: an audit entry left behind by the vanished record would ALSO be an
    honest `AUDIT_WITHOUT_RECORD`, and a witness that fires two kinds cannot
    show which comparator produced which.
    """
    core = AureaCore()
    _mutate(core)
    Path(core.cae.ledger_path).write_text("", encoding="utf-8")
    _rewrite_epoch_state(core, lambda p: p.__setitem__("history", []))

    resumed = AureaCore()

    assert _kinds(resumed) == {DivergenceKind.EPOCH_COUNT_AHEAD.value}, (
        f"expected exactly one kind, got {resumed.divergence_findings}")
    finding = _of_kind(resumed, DivergenceKind.EPOCH_COUNT_AHEAD)[0]
    assert finding["citing_store"] == "sae_epoch"
    assert finding["facts"]["epoch_count"] == 1
    assert finding["facts"]["records_in_epoch"] == 0


def test_c_audit_without_record_is_detected_and_reports_content_presence():
    """PIN (c) / kind 2. The same window seen from the ledger's side.

    THE MANUFACTURED STATE: the record survives (so the spend still matches its
    epoch) but its `cae_id` does not - the audit entry is on disk and nothing
    cites it. Ruling 45 writes the ledger BEFORE the change it audits, so this
    is the honest residue of a crash in that gap.

    **`target_content_present` RIDES AS A FACT, NEVER AS A SUBCLASS** (res.3).
    Here the successor IS in the Codex, so the content arrived and only its
    citation is missing - a different world from the entry whose target never
    landed, and the finding reports which without adjudicating between them.
    """
    core = AureaCore()
    ancestor = _mutate(core)
    _rewrite_epoch_state(
        core, lambda p: p["history"][0].__setitem__("cae_id", None))

    resumed = AureaCore()

    assert _kinds(resumed) == {DivergenceKind.AUDIT_WITHOUT_RECORD.value}, (
        f"expected exactly one kind, got {resumed.divergence_findings}")
    finding = _of_kind(resumed, DivergenceKind.AUDIT_WITHOUT_RECORD)[0]
    assert finding["citing_store"] == "cae"
    assert finding["cited_id"].startswith("CAE-")
    assert finding["facts"]["event"] == "mutate_doctrine"
    assert finding["facts"]["target"] == ancestor
    assert finding["facts"]["target_content_present"] is True


def test_c_unresolved_join_is_detected():
    """PIN (c) / kind 3. Ruling 76's join read as an integrity check.

    THE MANUFACTURED STATE: two claim cycles, then the FIRST claim's ancestry
    line is withheld - the durable scar and echo still name a perception whose
    own CLM line never landed.

    **THE SECOND CLAIM IS NOT PADDING.** Deleting the only line would ALSO drop
    the ledger's floor below the id citing it, firing `REFERENCED_ABOVE_FLOOR`
    honestly and making this witness ambiguous. Keeping a higher line holds the
    floor up so exactly one comparator can speak.
    """
    core = AureaCore()
    first = core.process_input("Honesty is pointless.")["claim_id"]
    core.process_input("The sky is a colour.")

    ledger = Path(core.ancestry.ledger_path)
    kept = [line for line in ledger.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("claim_id") != first]
    assert kept, "the second claim's line must survive to hold the floor up"
    ledger.write_text("\n".join(kept) + "\n", encoding="utf-8")

    resumed = AureaCore()

    assert _kinds(resumed) == {DivergenceKind.UNRESOLVED_JOIN.value}, (
        f"expected exactly one kind, got {resumed.divergence_findings}")
    cited = {f["cited_id"] for f in _of_kind(resumed, DivergenceKind.UNRESOLVED_JOIN)}
    assert cited == {first}
    stores = {f["citing_store"] for f in _of_kind(resumed, DivergenceKind.UNRESOLVED_JOIN)}
    assert stores <= {"scars", "suspensions", "echoes"} and stores


def test_c_referenced_above_floor_is_detected():
    """PIN (c) / kind 4. **THE REBORN-ID HAZARD'S AT-REST SIGNATURE.**

    R78 could not honestly simulate page-cache loss in-process and said so
    rather than faking the mechanism. This is the alternative it named: the
    citation and the floor simply disagree, and no crash needs simulating to
    read that.

    THE MANUFACTURED STATE is built on the CAE side on purpose - a record citing
    an audit id far above what the ledger can account for, with the ledger
    emptied so no uncited entry muddies the witness.
    """
    core = AureaCore()
    _mutate(core)
    Path(core.cae.ledger_path).write_text("", encoding="utf-8")
    _rewrite_epoch_state(
        core, lambda p: p["history"][0].__setitem__("cae_id", "CAE-0099"))

    resumed = AureaCore()

    assert _kinds(resumed) == {DivergenceKind.REFERENCED_ABOVE_FLOOR.value}, (
        f"expected exactly one kind, got {resumed.divergence_findings}")
    finding = _of_kind(resumed, DivergenceKind.REFERENCED_ABOVE_FLOOR)[0]
    assert finding["citing_store"] == "sae_epoch"
    assert finding["cited_id"] == "CAE-0099"
    assert finding["facts"] == {"prefix": "CAE-", "ordinal": 99, "floor": 0}


def test_c_a_detected_finding_reaches_the_durable_report():
    """PIN (c) + (h). The finding is not merely computed - it is WRITTEN."""
    core = AureaCore()
    _mutate(core)
    Path(core.cae.ledger_path).write_text("", encoding="utf-8")
    _rewrite_epoch_state(core, lambda p: p.__setitem__("history", []))

    resumed = AureaCore()
    log = Path(resumed.divergence_log_path)

    assert log.exists(), "a finding was detected and never written down"
    lines = [json.loads(line) for line in
             log.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0]["kind"] == DivergenceKind.EPOCH_COUNT_AHEAD.value
    assert lines[0]["timestamp"]
    assert resumed.divergence_log_failures == []


# =====================================================================
# (d) ERA HONESTY
# =====================================================================

def test_d_legacy_none_joins_yield_zero_findings():
    """PIN (d) / res.3. **A `None` JOIN IS ABSENT, AND ABSENCE IS NEVER A
    FINDING.**

    A scar formed before Ruling 76, a seed scar older than every claim, a CSA
    quarantine with no claim cycle behind it - each carries `None` honestly. A
    detector that read those as divergence would report the ARRIVAL of the join
    as a system-wide fault, and would drown every real finding in era noise on
    the first run.

    Driven through the pure module with hand-built legacy records, which is the
    only way to hold a whole store of them.
    """
    class Legacy:
        def __init__(self, ident):
            self.id = ident
            self.claim_id = None

    findings = detect_divergence(
        scars=[Legacy("Scar-1"), Legacy("Scar-2")],
        suspensions=[Legacy("BS-1")],
        echoes=[Legacy("ECH-0001")],
        claim_ids=[],
        floors={"CLM-": 0, "CAE-": 0},
    )
    assert findings == ()


def test_d_a_record_with_no_claim_attribute_at_all_yields_nothing():
    """PIN (d). A record type that never had the field is the oldest era there
    is, and it must read as absent rather than raising."""
    class Ancient:
        id = "Scar-0"

    assert detect_divergence(scars=[Ancient()], claim_ids=[],
                             floors={"CLM-": 0}) == ()


def test_d_an_underived_floor_reports_nothing():
    """PIN (d) / Ruling 53's sentinel honoured at the READ side.

    `None` means "the file exists and could not be read". Comparing against an
    invented zero would report every id in the tree as reborn - the loudest
    possible false positive, produced by treating unknown as empty.
    """
    class Cited:
        id = "Scar-1"
        claim_id = "CLM-0009"

    assert detect_divergence(scars=[Cited()], claim_ids=["CLM-0009"],
                             floors={"CLM-": None}) == ()


# =====================================================================
# (e) THE CLEAN TREE IS SILENT
# =====================================================================

def test_e_a_clean_construction_finds_nothing_and_writes_nothing():
    """PIN (e) / res.4. **SILENCE IS THE HEALTHY STATE.**

    The file exists only if a finding ever did. A per-construction heartbeat
    line would move every census in the tree and turn the healthy state into
    noise nobody reads - so liveness is proven by the (c) witnesses, never by a
    line saying nothing happened.
    """
    core = AureaCore()
    assert core.divergence_findings == []
    assert core.divergence_log_failures == []
    assert not Path(core.divergence_log_path).exists(), (
        "a clean construction wrote a divergence report")


def test_e_a_real_claim_cycle_stays_silent():
    """PIN (e). The pipeline's own joins resolve, so nothing is reported.

    This is the case that would fire on every claim if the join comparison were
    inverted, which is why it is pinned beside the clean construction rather
    than assumed to follow from it.
    """
    core = AureaCore()
    core.process_input("Honesty is pointless.")

    resumed = AureaCore()
    assert resumed.divergence_findings == []
    assert not Path(resumed.divergence_log_path).exists()


# =====================================================================
# (f) DETERMINISM
# =====================================================================

def test_f_the_same_world_produces_the_same_findings_in_the_same_order():
    """PIN (f) / res.4. The report is APPENDED TO A PERMANENT LOG, so two runs
    over one unchanged world must not produce two different records of it."""
    class Rec:
        def __init__(self, ident, claim):
            self.id = ident
            self.claim_id = claim

    kwargs = dict(
        sae_state={"epoch": 0, "epoch_count": 3,
                   "history": [{"epoch": 0, "cae_id": "CAE-001"}]},
        cae_entries=[{"id": "CAE-002", "event": "mutate_doctrine", "target": "D"}],
        scars=[Rec("Scar-2", "CLM-0009"), Rec("Scar-1", "CLM-0008")],
        echoes=[Rec("ECH-0002", "CLM-0009")],
        claim_ids=[], codex_ids=[], mutation_events=["mutate_doctrine"],
        floors={"CLM-": 1, "CAE-": 5},
    )
    first = detect_divergence(**kwargs)
    second = detect_divergence(**kwargs)

    assert first == second
    assert [f.as_dict() for f in first] == [f.as_dict() for f in second]
    # KIND-MAJOR in declaration order, then (citing_store, cited_id). A stable
    # PRESENTATION and explicitly not a ranking - nothing here believes one kind
    # matters more than another.
    order = [list(DivergenceKind).index(f.kind) for f in first]
    assert order == sorted(order)
    for kind in DivergenceKind:
        group = [f for f in first if f.kind is kind]
        assert group == sorted(group, key=lambda f: (f.citing_store,
                                                     f.cited_id or ""))


def test_f_a_finding_is_frozen_including_its_facts():
    """PIN (f). A finding is a reading taken at one instant.

    Rulings 33/52's shape at the smallest record in the tree: a facts mapping
    editable after the fact could be changed between being reported and being
    read.
    """
    finding = DivergenceFinding(kind=DivergenceKind.UNRESOLVED_JOIN,
                                citing_store="scars", cited_id="CLM-0001",
                                facts={"citing_record_id": "Scar-1"})
    with pytest.raises(Exception):
        finding.citing_store = "echoes"
    with pytest.raises(TypeError):
        finding.facts["citing_record_id"] = "tampered"


# =====================================================================
# (g) NEVER-RAISE AT CONSTRUCTION
# =====================================================================

def test_g_an_unreadable_ledger_records_a_failure_and_the_core_constructs(
        monkeypatch):
    """PIN (g) / res.4. **CRASH RESIDUE MUST NEVER BE FATAL.**

    Ruling 11's valence, pointing the same way it does there: the detector
    OBSERVES a change that already happened and gates nothing, so its own
    failure must not stop AUREA constructing. A crash-consistency instrument
    that makes a crashed system unstartable has inverted its purpose.
    """
    from src.doctrine.cae import CAE

    def boom(self):
        raise OSError("the ledger is unreadable")

    monkeypatch.setattr(CAE, "read_all", boom)

    core = AureaCore()

    assert core.divergence_findings == []
    assert len(core.divergence_log_failures) == 1
    failure = core.divergence_log_failures[0]
    assert failure["stage"] == "detect"
    assert "OSError" in failure["error"]


def test_g_a_failing_report_write_does_not_stop_construction(monkeypatch):
    """PIN (g), the write half. A full disk must not become a refusal."""
    import src.aurea_core as core_module

    def boom(path, line, encoding="utf-8"):
        raise OSError("no space left on device")

    core = AureaCore()
    _mutate(core)
    Path(core.cae.ledger_path).write_text("", encoding="utf-8")
    _rewrite_epoch_state(core, lambda p: p.__setitem__("history", []))

    monkeypatch.setattr(core_module, "durable_append_text", boom)
    resumed = AureaCore()

    assert len(resumed.divergence_findings) == 1, (
        "the finding must still be surfaced in memory")
    assert len(resumed.divergence_log_failures) == 1
    assert resumed.divergence_log_failures[0]["stage"] == "write"


# =====================================================================
# (h) THE WRITE ROUTES THROUGH THE FUNNEL
# =====================================================================

def test_h_the_report_write_routes_through_durable_append_text():
    """PIN (h) / R78's funnel. Its pin (c) already forbids the alternative
    (a raw mode-`'a'` open in `src/`); this asserts the positive."""
    tree = _tree("src/aurea_core.py")
    flush = [n for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef)
             and n.name == "_flush_divergence_finding"]
    assert len(flush) == 1

    called = {getattr(n.func, "attr", None) or getattr(n.func, "id", None)
              for n in ast.walk(flush[0]) if isinstance(n, ast.Call)}
    assert "durable_append_text" in called
    assert "open" not in called
    # The site owns its serialization and its validator - Ruling 78's division
    # of labour with the funnel, which decides nothing about content.
    assert "validate_record_value" in called
    assert "dumps" in called


# =====================================================================
# (i) THE ONE RULED TABLE MOVEMENT
# =====================================================================

def test_i_the_divergence_log_is_registered_in_the_isolation_table():
    """PIN (i) / res.4. **THE ONE RULED AUDIT MOVEMENT, 28 -> 29.**

    Stated in the ruling precisely so that any OTHER movement is a STOP. The
    detector runs at EVERY construction, so an unregistered path here would
    append a real finding to shared forensics on the first run that produced
    one - Ruling 31's contamination class, arriving through a new store.
    """
    from scripts.soak import _injection_table
    class_attrs, init_defaults = _injection_table()
    #
    # ~~assert len(class_attrs) + len(init_defaults) == 29~~
    #
    # MIGRATED 2026-08-13 (M3-A), old text kept verbatim above. **THE SUBJECT OF
    # THIS PIN IS UNCHANGED AND IS ASSERTED BELOW**: the divergence log is still
    # registered, still at its ruled relative path. What moved is the TABLE it
    # counts - M3-A registered the obligation ledger and the episode record, its
    # own two ruled movements (29 -> 31). The total is kept exact rather than
    # relaxed to `>=`, because a `>=` would absorb an UNRULED movement silently,
    # which is the whole thing this count exists to prevent.
    assert len(class_attrs) + len(init_defaults) == 31

    registered = [rel for cls, attr, rel in class_attrs
                  if attr == "DIVERGENCE_LOG_PATH"]
    assert registered == ["logs/divergence.jsonl"]


def test_i_the_suite_fixture_redirects_the_divergence_log():
    """PIN (i). Ruling 31's standing rule: a durable write path is a class
    attribute or an `__init__` default AND is redirected in `conftest.py` in the
    SAME commit. Asserted by OBSERVATION, not by reading the fixture."""
    assert AureaCore.DIVERGENCE_LOG_PATH != "data/runtime/logs/divergence.jsonl", (
        "the divergence log is not redirected under test - a finding would "
        "append to shared forensics")
    assert "data/runtime" not in Path(AureaCore.DIVERGENCE_LOG_PATH).as_posix()


def test_i_the_default_path_still_lives_under_runtime():
    """PIN (i) / Ruling 39: the DEFAULT resolves under `data/runtime/`.

    Read from SOURCE rather than from the class, because under this suite the
    class attribute is the fixture's temp path - reading it would prove the
    fixture works while saying nothing about what ships.
    """
    tree = _tree("src/aurea_core.py")
    literals = [ast.literal_eval(node.value)
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "DIVERGENCE_LOG_PATH"
                        for t in node.targets)]
    assert literals == ["data/runtime/logs/divergence.jsonl"]


# =====================================================================
# (j) THE RUN SITE, AND WHAT IT IS NOT
# =====================================================================

def test_j_the_detector_runs_once_from_the_constructor_and_nowhere_else():
    """PIN (j) / res.4. ONCE, after the loads, before the first input.

    After the loads because there is nothing to compare until each store has
    said what it holds; before the first input because a claim processed first
    would begin writing the very records being compared.

    **AND NOWHERE ELSE**: a re-scan on a tick would make this a periodic
    instrument, which is DECLARED OUT and owned by a later ruling.
    """
    tree = _tree("src/aurea_core.py")
    callers = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if (isinstance(node, ast.Call)
                    and getattr(node.func, "attr", None) == "_run_divergence_detection"):
                callers.append(func.name)
    assert callers == ["__init__"], (
        f"the detector acquired a caller outside construction: {callers}")


def test_j_the_detector_call_is_the_constructors_last_act():
    """PIN (j). Position is the ruling, not an accident of layout."""
    tree = _tree("src/aurea_core.py")
    init = [f for cls in ast.walk(tree) if isinstance(cls, ast.ClassDef)
            and cls.name == "AureaCore"
            for f in cls.body
            if isinstance(f, ast.FunctionDef) and f.name == "__init__"][0]
    last = init.body[-1]
    rendered = ast.unparse(last)
    assert "_run_divergence_detection" in rendered, (
        f"the detector is no longer the constructor's last act: {rendered}")


def test_j_the_detector_writes_to_no_store_it_reads():
    """PIN (j) / res.3. **REPAIR IS FORBIDDEN OUTRIGHT, NOT DEFERRED.**

    Driven rather than scanned: a real divergence is manufactured, the stores
    are read before and after, and nothing about them may move. Backfilling a
    record would fabricate history (Rulings 58/70's class).
    """
    core = AureaCore()
    _mutate(core)
    Path(core.cae.ledger_path).write_text("", encoding="utf-8")
    _rewrite_epoch_state(core, lambda p: p.__setitem__("history", []))

    watched = {name: Path(path).read_bytes() for name, path in {
        "sae_epoch": core.sae.runtime_path,
        "cae": core.cae.ledger_path,
        "doctrines": core.codex.runtime_path,
    }.items() if Path(path).exists()}
    assert watched, "the witness must actually be watching something"

    resumed = AureaCore()
    assert resumed.divergence_findings, "the state must be divergent"

    for name, before in watched.items():
        after = Path({"sae_epoch": resumed.sae.runtime_path,
                      "cae": resumed.cae.ledger_path,
                      "doctrines": resumed.codex.runtime_path}[name]).read_bytes()
        assert after == before, (
            f"the detector wrote to '{name}', a store it reads - repair is "
            f"forbidden outright")
