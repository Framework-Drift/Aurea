"""The act-log integrity instrument: forward chaining + the anomaly audit.

Discharges the gap M7-d measured. THE EIGHT BINDING PROPERTIES:

  1. Chain continuity -- N appended records verify end to end.
  2. The well-formed edit is CAUGHT in the chained era, on BOTH logs
     (M7-d's census row one, reversed).
  3. The pre-chain era answers ABSENT -- zero chain findings on a mixed-era log.
  4. Torn line -> TORN finding AND still excluded from replay (both halves).
  5. Ordinal gap and duplicate each -> findings; the reissue setup is visible.
  6. Report-only: a positive changes zero bytes and zero decisions.
  7. Mint compatibility -- the floor, the underived refusal, and every prior
     executive pin.
  8. L10 survives its own integrity instrument: the logs are still not
     constitutive, and M7-d's kill/reconstruction pins still pass whole.
"""

import ast
import json
import pathlib
import subprocess
import sys

import pytest

from src.executive.act_chain import (CHAIN_KEY, GENESIS_CHAIN_SEED, chain_over,
                                     genesis_chain, last_line_bytes)
from src.executive.act_log_audit import (INQUIRY_LOG_SCHEMA,
                                         SELECTION_LOG_SCHEMA, ActLogReport,
                                         FindingKind, LineEra, audit_act_log)
from src.executive.attention_policy import (POLICY_NAME, POLICY_VERSION,
                                            AttentionPolicy)
from src.executive.derived_view import ChairState, DerivedView
from src.executive.inquiry_generator import (GENERATOR_NAME, GENERATOR_VERSION,
                                             CandidatePartition,
                                             DiscrepancyClass, DriftBasis,
                                             InquiryCandidate)
from src.executive.inquiry_log import InquiryLog
from src.executive.selection_log import SelectionLog
from src.utils.ledger_mint import derive_max_ordinal

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"

_EMPTY_VIEW = DerivedView(
    open_obligations=(), unresolved_predictions=(), committed_goals=(),
    chair=ChairState.UNREGISTERED, verdict_acquisition_id=None, candidates=())

_DRIFT = InquiryCandidate(
    discrepancy_class=DiscrepancyClass.HORIZONLESS_COMMITMENT,
    source_record_ids=("PRD-0001",), partition=CandidatePartition.DRIFT,
    derivation_depth=1, drift_basis=DriftBasis.NO_DERIVABLE_LICENSE,
    horizon_state="absent")


def _selection_log(path, n=3):
    log = SelectionLog(log_path=str(path))
    for _ in range(n):
        log.record(AttentionPolicy().select(_EMPTY_VIEW), POLICY_NAME,
                   POLICY_VERSION)
    return log


def _inquiry_log(path, n=3):
    log = InquiryLog(log_path=str(path))
    for _ in range(n):
        log.record(_DRIFT, GENERATOR_NAME, GENERATOR_VERSION)
    return log


def _lines(path):
    return pathlib.Path(path).read_text(encoding="utf-8").splitlines()


def _rewrite(path, lines):
    pathlib.Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


LOGS = [
    ("selection", _selection_log, SELECTION_LOG_SCHEMA, "selected_record_id"),
    ("inquiry", _inquiry_log, INQUIRY_LOG_SCHEMA, "horizon_state"),
]
IDS = [row[0] for row in LOGS]


# ===========================================================================
# PIN 1 - CHAIN CONTINUITY
# ===========================================================================

@pytest.mark.parametrize("name,build,schema,field", LOGS, ids=IDS)
def test_1_appended_records_verify_end_to_end(tmp_path, name, build, schema,
                                              field):
    path = tmp_path / f"{name}.jsonl"
    build(path, n=6)
    report = audit_act_log(path, schema)
    assert report.clean, report.as_dict()
    assert report.lines_read == 6
    assert report.chained_lines == 6 and report.pre_chain_lines == 0


def test_1b_the_first_record_chains_from_the_declared_genesis(tmp_path):
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=1)
    first = json.loads(_lines(path)[0])
    assert first[CHAIN_KEY] == genesis_chain()
    assert genesis_chain() != GENESIS_CHAIN_SEED.decode()


def test_1c_each_chain_is_over_the_previous_lines_raw_bytes(tmp_path):
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=4)
    raw = [line.encode("utf-8") for line in _lines(path)]
    for index in range(1, len(raw)):
        assert json.loads(raw[index])[CHAIN_KEY] == chain_over(raw[index - 1])


def test_1d_last_line_bytes_agrees_with_what_the_verifier_splits(tmp_path):
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=3)
    assert last_line_bytes(path) == _lines(path)[-1].encode("utf-8")
    assert last_line_bytes(tmp_path / "absent.jsonl") is None


# ===========================================================================
# PIN 2 - THE WELL-FORMED EDIT IS CAUGHT (M7-d's census, reversed)
# ===========================================================================

@pytest.mark.parametrize("name,build,schema,field", LOGS, ids=IDS)
def test_2_a_well_formed_edit_in_the_chained_era_is_caught(tmp_path, name,
                                                           build, schema, field):
    """**M7-d MEASURED THIS ROUND-TRIPPING UNDETECTED. IT NO LONGER DOES.**

    The edit is caught by its SUCCESSOR's chain, which no longer matches the
    altered bytes - which is exactly what forward chaining buys and the reason
    the redundancy had to be laid down by the writer.
    """
    path = tmp_path / f"{name}.jsonl"
    build(path, n=4)
    lines = _lines(path)
    record = json.loads(lines[1])
    record[field] = "FORGED-9999"
    lines[1] = json.dumps(record)
    _rewrite(path, lines)

    report = audit_act_log(path, schema)
    kinds = {f.kind for f in report.findings}
    assert FindingKind.CHAIN_BREAK in kinds
    broken = next(f for f in report.findings
                  if f.kind is FindingKind.CHAIN_BREAK)
    assert broken.line_number == 2          # the successor reveals it
    assert broken.era is LineEra.CHAINED


def test_2b_an_edit_to_the_final_line_is_NOT_caught_and_that_is_declared(
        tmp_path):
    """**AN HONEST LIMITATION OF FORWARD CHAINING, MEASURED AND PINNED.**

    A record is protected by its SUCCESSOR, so the most recent line is
    unprotected until the next one is written. Nothing in this design can close
    that - the redundancy for line N is created when line N+1 is minted - and
    the alternative (a trailing checksum the writer updates in place) would mean
    rewriting a line of an append-only log, which is a far worse trade.

    Pinned so the limitation is a KNOWN state rather than a surprise, and so a
    later mechanism that closes it reddens this pin deliberately.
    """
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=3)
    lines = _lines(path)
    record = json.loads(lines[-1])
    record["selected_record_id"] = "FORGED-LAST"
    lines[-1] = json.dumps(record)
    _rewrite(path, lines)
    assert audit_act_log(path, SELECTION_LOG_SCHEMA).clean is True


# ===========================================================================
# PIN 3 - ERA HONESTY
# ===========================================================================

def _legacy_selection_lines(n=2):
    """Lines in the PRE-CHAIN shape: no chain field, nothing else missing."""
    return [json.dumps({
        "kind_of_record": "attention_selection",
        "selection_id": f"SEL-{i:04d}", "policy_name": POLICY_NAME,
        "policy_version": POLICY_VERSION, "outcome": "nothing_attendable",
        "selected_record_id": None, "selected_category": None,
        "deciding_basis": None, "candidate_census": [], "gate_one": {},
        "recorded_at": ""}) for i in range(1, n + 1)]


def test_3_a_mixed_era_log_is_clean_and_the_eras_are_counted(tmp_path):
    path = tmp_path / "sel.jsonl"
    _rewrite(path, _legacy_selection_lines(2))
    _selection_log(path, n=3)                 # appends chained lines after them
    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    assert report.clean, report.as_dict()
    assert report.pre_chain_lines == 2
    assert report.chained_lines == 3


def test_3b_a_well_formed_edit_in_the_PRE_CHAIN_era_yields_no_chain_finding(
        tmp_path):
    """**ERA HONESTY IS LAW, and this is the pin that makes it cost something.**

    The same edit that is CAUGHT in the chained era is INVISIBLE here, and the
    instrument reports nothing rather than inventing a finding it has no
    evidence for. The pre-chain era is UNVERIFIABLE-BY-CHAIN - a state, not a
    defect - and back-filling hashes would produce a log that looked fully
    verified while its oldest records were certified after the fact by the same
    process that could have altered them.
    """
    path = tmp_path / "sel.jsonl"
    legacy = _legacy_selection_lines(3)
    _rewrite(path, legacy)
    lines = _lines(path)
    record = json.loads(lines[0])
    record["outcome"] = "selected"
    lines[0] = json.dumps(record)
    _rewrite(path, lines)
    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    assert not any(f.kind is FindingKind.CHAIN_BREAK for f in report.findings)
    assert report.chained_lines == 0


def test_3c_no_historical_line_is_touched_when_the_chain_begins(tmp_path):
    """The chain starts where it starts. Nothing rehashes or annotates."""
    path = tmp_path / "sel.jsonl"
    _rewrite(path, _legacy_selection_lines(2))
    before = pathlib.Path(path).read_bytes()
    _selection_log(path, n=2)
    after = pathlib.Path(path).read_bytes()
    assert after.startswith(before)
    assert CHAIN_KEY not in json.loads(_lines(path)[0])
    # ...and the FIRST chained line chains over the last LEGACY line, not
    # genesis - which is what makes a mixed-era log verifiable from there on.
    assert json.loads(_lines(path)[2])[CHAIN_KEY] == chain_over(
        _lines(path)[1].encode("utf-8"))


# ===========================================================================
# PIN 4 - TORN LINE: REPORTED, AND STILL DROPPED
# ===========================================================================

def test_4_a_torn_line_is_reported_and_still_excluded_from_replay(tmp_path):
    path = tmp_path / "sel.jsonl"
    log = _selection_log(path, n=3)
    lines = _lines(path)
    lines[1] = "{ this is not json"
    _rewrite(path, lines)

    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    torn = [f for f in report.findings if f.kind is FindingKind.TORN_LINE]
    assert len(torn) == 1 and torn[0].line_number == 1
    assert torn[0].record_id is None          # an unparseable line has no id
    # AN UNREADABLE LINE'S ERA IS UNKNOWABLE and is reported as such.
    assert torn[0].era is LineEra.UNDETERMINED
    assert report.pre_chain_lines + report.chained_lines == 2   # not counted
    # THE OTHER HALF: floor semantics still DROP it from replay.
    assert len(log.selections()) == 2


# ===========================================================================
# PIN 5 - ORDINAL ANOMALIES
# ===========================================================================

def test_5_a_duplicate_ordinal_is_reported_and_the_reissue_is_visible(tmp_path):
    """**M7-d's CENSUS ROW THREE.** Two lines wearing one id lower the derived
    mint floor, so the next mint collides. The audit now sees it; the floor is
    measured beside it so the consequence is legible, not merely asserted."""
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=4)
    lines = _lines(path)
    record = json.loads(lines[3])
    record["selection_id"] = "SEL-0002"
    lines[3] = json.dumps(record)
    _rewrite(path, lines)

    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    dupes = [f for f in report.findings
             if f.kind is FindingKind.ORDINAL_DUPLICATE]
    assert len(dupes) == 1 and dupes[0].record_id == "SEL-0002"
    # THE CONSEQUENCE, measured: the floor drops, so `SEL-0004` would reissue.
    assert derive_max_ordinal(path, "SEL-") == 3


def test_5b_an_ordinal_gap_is_reported(tmp_path):
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=4)
    lines = _lines(path)
    del lines[2]
    _rewrite(path, lines)
    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    gaps = [f for f in report.findings if f.kind is FindingKind.ORDINAL_GAP]
    assert len(gaps) == 1


def test_5c_a_schema_violation_is_reported(tmp_path):
    path = tmp_path / "sel.jsonl"
    _selection_log(path, n=2)
    lines = _lines(path)
    record = json.loads(lines[1])
    del record["policy_name"]
    lines[1] = json.dumps(record)
    _rewrite(path, lines)
    report = audit_act_log(path, SELECTION_LOG_SCHEMA)
    violations = [f for f in report.findings
                  if f.kind is FindingKind.SCHEMA_VIOLATION]
    assert len(violations) == 1
    assert "policy_name" in violations[0].detail


def test_5d_the_finding_vocabulary_is_closed_at_five():
    assert [m.value for m in FindingKind] == [
        "torn_line", "ordinal_gap", "ordinal_duplicate", "chain_break",
        "schema_violation"]
    with pytest.raises(ValueError):
        FindingKind("something_else")


# ===========================================================================
# PIN 6 - REPORT ONLY
# ===========================================================================

@pytest.mark.parametrize("name,build,schema,field", LOGS, ids=IDS)
def test_6_a_positive_changes_zero_bytes(tmp_path, name, build, schema, field):
    """RULING 79'S OWN PIN FORM: drive a real tamper, assert byte-unchanged."""
    path = tmp_path / f"{name}.jsonl"
    build(path, n=3)
    lines = _lines(path)
    record = json.loads(lines[1])
    record[field] = "FORGED"
    lines[1] = json.dumps(record)
    _rewrite(path, lines)

    before = pathlib.Path(path).read_bytes()
    report = audit_act_log(path, schema)
    assert not report.clean
    assert pathlib.Path(path).read_bytes() == before


def test_6b_the_instrument_has_no_repair_path_and_no_write_mode():
    tree = ast.parse((SRC / "executive" / "act_log_audit.py").read_text(
        encoding="utf-8"))
    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for verb in ("repair", "fix", "rewrite", "quarantine", "heal", "restore",
                 "truncate", "drop", "remove"):
        assert verb not in names
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open"
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"write_text", "write_bytes", "mkdir",
                                     "unlink", "replace"}


def test_6c_nothing_in_src_consumes_the_audit():
    """Ruling 72's no-consumer form: findings are for readers of history."""
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "act_log_audit.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module \
                    and "act_log_audit" in node.module:
                consumers.append(path.as_posix())
    assert consumers == [], consumers


def test_6d_a_tampered_log_still_changes_no_decision(tmp_path):
    """PIN 6's other half, and M7-d pin 7 restated after chaining exists."""
    path = tmp_path / "sel.jsonl"
    log = _selection_log(path, n=3)
    before = [r["selection_id"] for r in log.selections()]
    lines = _lines(path)
    record = json.loads(lines[0])
    record["selected_record_id"] = "FORGED"
    lines[0] = json.dumps(record)
    _rewrite(path, lines)
    audit_act_log(path, SELECTION_LOG_SCHEMA)
    # The audit changed nothing, and the log still reads back the same ids.
    assert [r["selection_id"] for r in SelectionLog(
        log_path=str(path)).selections()] == before


def test_6e_the_report_is_ephemeral_and_owns_no_store():
    tree = ast.parse((SRC / "executive" / "act_log_audit.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ActLogReport":
            methods = {n.name for n in node.body
                       if isinstance(n, ast.FunctionDef)}
            assert "save" not in methods and "persist" not in methods
    assert not hasattr(ActLogReport, "save")


# ===========================================================================
# PIN 7 - MINT COMPATIBILITY
# ===========================================================================

@pytest.mark.parametrize("name,build,schema,field", LOGS, ids=IDS)
def test_7_chaining_does_not_disturb_the_mint(tmp_path, name, build, schema,
                                              field):
    path = tmp_path / f"{name}.jsonl"
    build(path, n=5)
    prefix = schema.id_prefix
    assert derive_max_ordinal(path, prefix) == 5
    ids = [json.loads(line)[schema.id_field] for line in _lines(path)]
    assert ids == [f"{prefix}{i:04d}" for i in range(1, 6)]


@pytest.mark.parametrize("name,build,schema,field", LOGS, ids=IDS)
def test_7b_the_underived_floor_still_refuses(tmp_path, monkeypatch, name,
                                              build, schema, field):
    """Ruling 53's sentinel, unchanged by chaining."""
    path = tmp_path / f"{name}.jsonl"
    log = build(path, n=1)
    module = ("src.executive.selection_log" if name == "selection"
              else "src.executive.inquiry_log")
    monkeypatch.setattr(f"{module}.derive_max_ordinal", lambda *a, **k: None)
    with pytest.raises(Exception):
        build(path, n=1)


def test_7c_a_chain_failure_is_a_write_failure(tmp_path, monkeypatch):
    """The write still GATES the act: an unchainable record does not exist."""
    path = tmp_path / "sel.jsonl"
    log = SelectionLog(log_path=str(path))

    def _boom(*a, **k):
        raise OSError("cannot read the tail")

    monkeypatch.setattr("src.executive.selection_log.chain_for_next_line", _boom)
    with pytest.raises(OSError):
        log.record(AttentionPolicy().select(_EMPTY_VIEW), POLICY_NAME,
                   POLICY_VERSION)
    assert not path.exists()
    assert log.entries == []


# ===========================================================================
# PIN 8 - L10 SURVIVES ITS OWN INTEGRITY INSTRUMENT
# ===========================================================================

def test_8_the_m7d_acceptance_pins_still_pass_whole():
    """**THE STOP-SET PIN.** An integrity mechanism that made the act logs
    load-bearing would have inverted M7-d's whole result. The kill, the
    reconstruction, and the tamper-changes-no-decision arms are run here as a
    unit so that this pass cannot quietly break the thing it is protecting.
    """
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest",
         "tests/test_m7d_acceptance.py", "-q"],
        cwd=str(REPO), capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-3000:]


def test_8b_the_chain_did_not_make_the_logs_constitutive():
    """No decision path reads either log - before or after chaining."""
    view = (SRC / "executive" / "derived_view.py").read_text(encoding="utf-8")
    policy = (SRC / "executive" / "attention_policy.py").read_text(
        encoding="utf-8")
    generator = (SRC / "executive" / "inquiry_generator.py").read_text(
        encoding="utf-8")
    for source in (view, policy, generator):
        assert "selection_log" not in source
        assert "inquiry_log" not in source
        assert CHAIN_KEY not in source
