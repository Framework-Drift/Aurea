"""
test_m4_acquisition.py - M4-alpha: THE ACQUISITION BOUNDARY.

Grounds heading Phase 4 ("every model exchange and tool result permanently
recorded; state transitions deterministic given prior state plus recorded
acquisitions; nondeterminism confined to acquisition points"), Section 4's type
system at the boundary, and the M4 grounding's ruling M4-alpha.

    **AN ARRIVAL THAT WAS NOT RECORDED AT THE BOUNDARY IS NOT AN ARRIVAL.**

THE RED-FIRST WATCH IS PART COLLECTION ERROR AND PART REAL, AND THE SPLIT IS
STATED RATHER THAN DRESSED UP. `src/external/acquisition_ledger.py` does not
exist at `86f5148`, so every pin importing it fails at COLLECTION there - the
honest situation Rulings 61, 63 and 70 each recorded for their own new modules.
**BUT UNLIKE THOSE THREE, THIS PASS HAS AN INDEPENDENT HALF**, because the two
doors are pre-existing: the wire pins below (the arrival record, the ACQ<->CLM
join, the channel declaration, both gates) are written against `AureaCore` and
the model adapter, and they were WATCHED RED IN A DETACHED WORKTREE at `86f5148`
where those surfaces exist and the behaviour does not. That watch is reported in
the pass's own record, per CLAUDE.md section 4.
"""

from __future__ import annotations

import ast
import builtins
import inspect
import json
from pathlib import Path

import pytest

from src.aurea_core import STRUCTURAL_VIOLATIONS, AureaCore
from src.external.acquisition_ledger import (AcquisitionChannel,
                                             AcquisitionIntegrity,
                                             AcquisitionLedger,
                                             AcquisitionLedgerUnreadable,
                                             AcquisitionRecord,
                                             ContentStanding, MethodWarrant,
                                             payload_digest)
from src.external.claim_ancestry import (ClaimAncestryLedger, OriginDeclaration,
                                         OriginKind)
from src.external.model_provider import ingest_model_assertion

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
MODULE = SRC / "external" / "acquisition_ledger.py"

IDENTITY = "openai/gpt-9/2026-01-15"


def _tree(path: Path = MODULE) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _src_files():
    return sorted(SRC.rglob("*.py"))


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def _ledger(tmp_path, name="acquisitions.jsonl") -> AcquisitionLedger:
    return AcquisitionLedger(ledger_path=str(tmp_path / name))


class _UnreadableFor:
    """Make ONE path raise on READ while leaving writes alone.

    Ruling 58's fixture verbatim - the asymmetry is what makes Ruling 53's
    sentinel testable at all, and `derive_max_ordinal` uses `open()` rather than
    `Path.read_text` precisely so this fixture can reach it (Ruling 69).
    """

    def __init__(self, monkeypatch, path):
        self._real = builtins.open
        self._path = str(path)
        self._armed = True
        monkeypatch.setattr(builtins, "open", self._open)

    def _open(self, file, mode="r", *args, **kwargs):
        if self._armed and str(file) == self._path and "r" in mode:
            raise OSError("simulated transient read failure")
        return self._real(file, mode, *args, **kwargs)

    def recover(self):
        self._armed = False


# =====================================================================
# (a) THE ARRIVAL IS RECORDED, AND THE CLAIM CARRIES IT
# =====================================================================

def test_a_a_perceived_arrival_writes_exactly_one_acquisition_line():
    """THE FORCING PIN. RED at `86f5148`: no ledger, no line, no field.

    Read back FROM THE FILE rather than from the returned object - the record is
    the claim M4-alpha makes, and an in-memory assertion would not witness that
    it survived serialization (Ruling 70's pin (a) reasoning).
    """
    core = AureaCore()
    core.process_input("A claim arrives at the boundary.")

    entries = _lines(core.acquisitions)
    assert len(entries) == 1, "one perceived arrival, one acquisition line"
    entry = entries[0]
    assert entry["acquisition_id"] == "ACQ-0001"
    assert entry["channel"] == "user_input"
    assert entry["payload"] == "A claim arrives at the boundary.", (
        "the payload is recorded WHOLE - Phase 4's own word is 'permanently "
        "recorded', and a ledger of digests could replay nothing")
    assert entry["payload_sha256"] == payload_digest(
        "A claim arrives at the boundary.")


def test_a_the_claim_carries_the_arrival_and_the_join_reads_both_ways():
    """The ACQ<->CLM join. RED at `86f5148` (no `acquisition_ref` field).

    The WRITE points one way (the later artifact references the earlier - Ruling
    60's forced direction, because the acquisition is append-only and is
    recorded before the claim id exists). The READ resolves both ways, and that
    is what makes the one-way write sufficient.
    """
    core = AureaCore()
    result = core.process_input("Joined at the boundary.")

    claim = core.ancestry.get(result["claim_id"])
    assert claim is not None
    assert claim.acquisition_ref == "ACQ-0001", (
        "the claim records the arrival that became it")

    # ... and back: from the acquisition to the claim.
    arrival = core.acquisitions.get(claim.acquisition_ref)
    assert arrival is not None
    assert arrival.payload == "Joined at the boundary."
    back = [c for c in core.ancestry.read_all()
            if c.acquisition_ref == arrival.acquisition_id]
    assert [c.claim_id for c in back] == [result["claim_id"]]


def test_a_one_acq_line_per_clm_line_across_a_batch():
    """Ruling 68's restored one-to-one sentence, extended one layer out.

    ONE ACQ, ONE CLM, ONE ECH per perceived claim cycle - all three writes sit
    below both gates, so the three counts move together or the property is
    broken. Pinned as a TRIPLE deliberately: two of them agreeing while the
    third drifts is exactly the shape a per-store pin cannot see.
    """
    core = AureaCore()
    claims = ["first", "second", "third", "", "   "]
    for text in claims:
        core.process_input(text)

    assert len(_lines(core.acquisitions)) == len(claims)
    assert len(core.ancestry.read_all()) == len(claims)
    assert len(core.echo_memory.read_all()) == len(claims)

    # STRICTLY INCREASING, and the ordinal IS the arrival index.
    indices = [r.arrival_index for r in core.acquisitions.read_all()]
    assert indices == [1, 2, 3, 4, 5]
    # The payloads are the arrivals, in arrival order, WHOLE.
    assert [r.payload for r in core.acquisitions.read_all()] == claims


# =====================================================================
# (b) BOTH GATES SIT ABOVE THE ACQUISITION WRITE
# =====================================================================

def test_b_a_suspended_pass_records_no_arrival():
    """Rider R2 extended: a mind that is not running does not take up arrivals.

    FORCING: the pass is driven through the real public door with the real
    suspension gate, and the ledger file is measured, not the return value.
    """
    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "test suspension"

    result = core.process_input("This must not reach the boundary record.")

    assert result["claim_id"] is None
    assert _lines(core.acquisitions) == [], (
        "a suspended AUREA refuses at the door and records nothing - the "
        "acquisition ledger is the boundary's CLOCK, and a suspended pass is "
        "not a moment of it")


@pytest.mark.parametrize("arrival", [None, 7, b"bytes", ["list"], {"k": "v"},
                                     bytearray(b"raw"), object()])
def test_b_a_non_str_arrival_records_no_arrival(arrival):
    """Ruling 68's gate, extended: an arrival that is not a claim is not
    perceived, and is not recorded as an arrival either.

    **AND THE SECOND REASON IS THIS LEDGER'S OWN**: recording it would mean
    minting an arrival id for a `bytearray`, whose payload this store cannot
    canonically hold (Ruling 66). The fabrication class one layer out from the
    one Ruling 68 closed.
    """
    core = AureaCore()
    result = core.process_input(arrival)

    assert result["claim_id"] is None
    assert _lines(core.acquisitions) == []
    assert result["errors"], "it is still an ORDINARY rejection, reported"
    assert result.get("structural_violation") is None, (
        "a caller's wrong type is not one of AUREA's guards firing (Docket N)")


def test_b_the_gates_sit_above_the_acquisition_write_as_shape():
    """THE ORDER, AS SHAPE - Ruling 68's own pin form, extended by one write.

    Behaviourally the gates are distinguishable only through the emitted
    packet; structurally the ordering is exact, and a refactor that hoisted the
    acquisition write above either gate would start recording arrivals that
    changed no state - which is what keeps M4-gamma's replay honest.
    """
    src = inspect.getsource(AureaCore.process_input)
    suspension = src.index("if self.processing_suspended:")
    type_gate = src.index("if not isinstance(raw_input, str):")
    acquisition = src.index("self.acquisitions.record(")
    mint = src.index("self.ancestry.record(")
    assert suspension < type_gate < acquisition < mint, (
        "M4-alpha rules the order: suspension gate, type gate, ARRIVAL, then "
        "the claim that carries it")


def test_b_the_acquisition_write_is_outside_the_broad_exception_clause():
    """AST. The write must NOT sit inside `process_input`'s `try:`.

    Inside it an OSError would be flattened into `result['errors']` by the broad
    clause and the caller would read a DEGRADED SUCCESS - a claim perceived with
    no arrival on record, reported as a hiccup. Ruling 58's pin, verbatim
    reasoning, for the write one line above the one it guards.
    """
    tree = ast.parse(inspect.getsource(AureaCore.process_input).lstrip())
    guarded = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for stmt in node.body:
                for inner in ast.walk(stmt):
                    if (isinstance(inner, ast.Call)
                            and isinstance(inner.func, ast.Attribute)
                            and inner.func.attr == "record"
                            and isinstance(inner.func.value, ast.Attribute)
                            and inner.func.value.attr == "acquisitions"):
                        guarded.add(inner.lineno)
    assert guarded == set(), (
        f"the acquisition write is inside a try: at {sorted(guarded)}. It must "
        f"be visible to the CALLER, which means the exception leaves the method")


# =====================================================================
# (c) THE CHANNEL IS THE DOOR'S IDENTITY, NEVER DERIVED FROM THE ORIGIN
# =====================================================================

def test_c_the_model_adapter_declares_model_exchange():
    """The second door. RED at `86f5148` (no channel to declare).

    Driven through the REAL adapter against a REAL core, so the declaration is
    measured where it lands rather than where it is passed.
    """
    core = AureaCore()
    ingest_model_assertion(core.process_input, "The bridge will hold.", IDENTITY)

    entries = _lines(core.acquisitions)
    assert len(entries) == 1
    assert entries[0]["channel"] == "model_exchange", (
        "a model response is a MODEL_EXCHANGE arrival - recording it as "
        "USER_INPUT would be a fabricated channel fact on a durable record")
    assert entries[0]["payload"] == "The bridge will hold."


def test_c_a_human_pasting_model_output_is_a_user_input_arrival():
    """**THE CHANNEL IS NOT DERIVED FROM `origin_kind`, AND THIS IS THE CASE
    THAT PROVES THE TWO ARE DIFFERENT QUESTIONS.**

    `origin_kind` says WHO ASSERTED; `channel` says WHICH DOOR. A human handing
    a model's output through `process_input` is honestly a USER_INPUT arrival of
    a MODEL_PREDICTION assertion, and a derivation would record the exchange as
    having come through a door it never touched - Ruling 30's defect (two senses
    collapsed into one value) at a new surface.
    """
    core = AureaCore()
    core.process_input(
        "A model said the bridge will hold.",
        origin=OriginDeclaration(kind=OriginKind.MODEL_PREDICTION))

    entry = _lines(core.acquisitions)[0]
    assert entry["channel"] == "user_input", (
        "the DOOR is user input even though the ASSERTER is a model")
    claim = core.ancestry.get(core.ancestry.read_all()[0].claim_id)
    assert claim.origin_kind is OriginKind.MODEL_PREDICTION, (
        "and the ancestry record is untouched by the channel - two vocabularies, "
        "two records, neither derived from the other")


def test_c_the_channel_must_be_a_member_not_a_string(tmp_path):
    """A raw string would let a caller invent a door that does not exist."""
    ledger = _ledger(tmp_path)
    with pytest.raises(TypeError):
        ledger.record("text", channel="user_input")


def test_c_the_channel_vocabulary_is_closed_at_the_censused_two():
    """Two doors were found by census; two members exist.

    A third member would assert a boundary that does not exist - tool results
    are Phase 11's and have no door. Widening is a manifest act (Ruling 7's
    closed-enum discipline), so this is exact rather than a superset check.
    """
    assert {c.name for c in AcquisitionChannel} == {"USER_INPUT",
                                                   "MODEL_EXCHANGE"}


# =====================================================================
# (d) THE CORRELATION IS A RECORDED ID, NEVER A MINTED SECOND ONE
# =====================================================================

def test_d_a_single_arrival_correlates_with_itself(tmp_path):
    ledger = _ledger(tmp_path)
    record = ledger.record("only half", channel=AcquisitionChannel.USER_INPUT)
    assert record.correlation_id == record.acquisition_id


def test_d_two_halves_of_one_exchange_share_one_correlation():
    """The exchange join, BOTH DIRECTIONS. RED at `86f5148`.

    The caller records the REQUEST half (it is the only party that holds it -
    Ruling 70 res.2), then hands the adapter that half's id. The response half
    is recorded by the pipeline door. Two records, one correlation, and
    `correlated()` returns them in append order.
    """
    core = AureaCore()
    request = core.acquisitions.record(
        "Will the bridge hold?", channel=AcquisitionChannel.MODEL_EXCHANGE)

    ingest_model_assertion(core.process_input, "The bridge will hold.",
                           IDENTITY, correlation_id=request.acquisition_id)

    halves = core.acquisitions.correlated(request.acquisition_id)
    assert [h.acquisition_id for h in halves] == ["ACQ-0001", "ACQ-0002"]
    assert [h.payload for h in halves] == ["Will the bridge hold?",
                                           "The bridge will hold."]
    assert {h.channel for h in halves} == {AcquisitionChannel.MODEL_EXCHANGE}
    # And the RESPONSE half is the one that became a claim - the request never
    # entered the pipeline, so it has no CLM.
    refs = {c.acquisition_ref for c in core.ancestry.read_all()}
    assert refs == {"ACQ-0002"}


def test_d_the_correlation_reads_no_clock_and_mints_nothing():
    """AST. **NOTHING IS MINTED FOR A CORRELATION AND NO CLOCK IS READ.**

    A uuid or a timestamp would be a second identity vocabulary at the one
    boundary whose whole purpose is to have exactly one - and M4-beta exists to
    KILL wall-clock minting rather than add to it. A correlation is a function
    of a recorded fact: the `ACQ-` id of the half that opened the exchange.
    """
    banned = {"uuid", "uuid1", "uuid4", "token_hex", "token_urlsafe",
              "monotonic", "perf_counter", "time", "time_ns", "random"}
    offenders = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call):
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", None))
            if name in banned:
                offenders.append(f"{name}:{node.lineno}")
    assert offenders == [], (
        f"the acquisition ledger reaches an id/clock source at {offenders}")


# =====================================================================
# (e) SECTION 4's TRIPLE - CARRIED FROM THE FIRST RECORD, CONSUMED BY NOTHING
# =====================================================================

def test_e_the_first_record_carries_the_whole_triple():
    """Phase 2's law: provenance is first-class from each store's FIRST record.

    It CANNOT be retrofitted - a field added later is `None` for everything that
    came before, forever. So the triple is asserted on record number one.
    """
    core = AureaCore()
    core.process_input("the very first arrival")

    entry = _lines(core.acquisitions)[0]
    assert entry["integrity"] == "structural"
    assert entry["method_warrant"] == "none", (
        "NONE admits with warrant near zero; it does not exclude. Neither door "
        "has a survival history, and inventing one would be L3's class")
    assert entry["warrant_conditions"] == [], (
        "a warrant of NONE has no documented conditions to cite")
    assert entry["content_standing"] == "provisional_unvalidated"


def test_e_each_triple_vocabulary_carries_only_the_producible_member():
    """v1, GOVERNED CONTENT. A second member would be a state this build can
    neither produce nor recognise - coined at the one surface whose honesty the
    whole boundary rests on."""
    assert {m.name for m in AcquisitionIntegrity} == {"STRUCTURAL"}
    assert {m.name for m in MethodWarrant} == {"NONE"}
    assert {m.name for m in ContentStanding} == {"PROVISIONAL_UNVALIDATED"}


def test_e_nothing_in_src_consumes_or_promotes_the_triple():
    """**NOTHING IN M4 CONSUMES OR PROMOTES THESE, AND IT IS STRUCTURAL.**

    Standing moves only under L12 episodes. A comparison, a branch or a
    truthiness read on any of the three anywhere in `src/` would be this layer
    quietly deciding what it exists to merely record - Docket H's
    count-never-gates scan, at a new field set.
    """
    fields = {"integrity", "method_warrant", "content_standing"}
    offenders = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            reads = []
            if isinstance(node, ast.Compare):
                reads = [node.left] + list(node.comparators)
            elif isinstance(node, ast.If):
                reads = [node.test]
            elif isinstance(node, ast.BoolOp):
                reads = list(node.values)
            for read in reads:
                for inner in ast.walk(read):
                    if (isinstance(inner, ast.Attribute)
                            and inner.attr in fields):
                        offenders.append(
                            f"{path.relative_to(REPO).as_posix()}:{inner.lineno}"
                            f" reads .{inner.attr}")
    assert offenders == [], (
        f"the Section 4 triple is CONSUMED at {offenders}. It is written and "
        f"never read - standing moves only under L12 episodes.")


def test_e_the_triple_scanner_actually_fires():
    """A guard never observed to fire is a comment (Docket P's rule)."""
    fed = ast.parse("if record.content_standing == 'x':\n    pass\n")
    hits = [n for n in ast.walk(fed) if isinstance(n, ast.Attribute)
            and n.attr in {"integrity", "method_warrant", "content_standing"}]
    assert hits, "the scanner's own shape no longer matches a real read"


# =====================================================================
# (f) THE STORE DISCIPLINE - append-only, no update family, wall unread
# =====================================================================

def test_f_there_is_no_delete_or_update_family():
    """AST. M3-A's rule verbatim: a method named `amend` with a docstring saying
    "only before resolution" is a request for restraint, and this project has
    hard evidence restraint fails (CLAUDE.md section 3)."""
    banned = {"delete", "remove", "clear", "purge", "truncate", "update",
              "amend", "revise", "edit", "rewrite", "drop"}
    offenders = [n.name for n in ast.walk(_tree())
                 if isinstance(n, ast.FunctionDef)
                 and any(n.name == b or n.name.startswith(b + "_")
                         or n.name.lstrip("_").startswith(b) for b in banned)]
    assert offenders == [], (
        f"the acquisition ledger defines {offenders}. The record of what "
        f"arrived is not editable, and the absence IS the enforcement")


def test_f_the_only_write_mode_is_the_funnel():
    """No `open` in write mode anywhere here: Ruling 78's funnel owns the
    append, and a `"w"` would have to get past the tree-wide AST census."""
    offenders = []
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and getattr(node.func, "id", None)
                == "open"):
            modes = [a.value for a in node.args[1:]
                     if isinstance(a, ast.Constant)]
            modes += [k.value.value for k in node.keywords
                      if k.arg == "mode" and isinstance(k.value, ast.Constant)]
            if any(m != "r" for m in modes) or not modes:
                offenders.append(node.lineno)
    assert offenders == [], f"a non-read open at {offenders}"
    calls = {n.func.id for n in ast.walk(_tree())
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "durable_append_text" in calls, (
        "the append must route through Ruling 78's funnel")


def test_f_the_wall_clock_is_recorded_and_never_read():
    """M3-A's discipline verbatim. `recorded_wall` is an observation; ordering
    is by ordinal, ALWAYS. A comparison here would make the boundary's clock the
    wall clock, which is the thing M4-beta exists to remove from the tree."""
    offenders = []
    for path in _src_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            reads = []
            if isinstance(node, ast.Compare):
                reads = [node.left] + list(node.comparators)
            elif isinstance(node, ast.If):
                reads = [node.test]
            for read in reads:
                for inner in ast.walk(read):
                    if (isinstance(inner, ast.Attribute)
                            and inner.attr == "recorded_wall"):
                        offenders.append(
                            f"{path.relative_to(REPO).as_posix()}:{inner.lineno}")
    assert offenders == [], f"`recorded_wall` is READ at {offenders}"


def test_f_the_arrival_index_is_derived_never_stored():
    """The ordinal IS the arrival index - one clock, not two fields.

    A stored copy would be a derivation free to disagree with the id it copies
    (L3; Rulings 63 and 65 both refused exactly this structure).
    """
    core = AureaCore()
    core.process_input("indexed")
    entry = _lines(core.acquisitions)[0]
    assert "arrival_index" not in entry, (
        "the index is DERIVED from the id at read time, never stored beside it")
    assert core.acquisitions.read_all()[0].arrival_index == 1

    # An id that does not parse has an UNKNOWN place in logical time - `None`
    # rather than 0, because a 0 would silently sort it first.
    odd = AcquisitionRecord(acquisition_id="LEGACY-x",
                            channel=AcquisitionChannel.USER_INPUT,
                            correlation_id="LEGACY-x", payload="p",
                            payload_sha256=payload_digest("p"))
    assert odd.arrival_index is None


def test_f_the_payload_is_recorded_whole_including_shapes_a_writer_might_tidy():
    """Phase 4's word is PERMANENTLY RECORDED. Whitespace, newlines, unicode and
    length all survive - a transformed arrival is a different arrival, and the
    hash beside it is over exactly what was stored."""
    core = AureaCore()
    payloads = ["  leading and trailing  ", "internal\nnewlines\tand\ttabs",
                "unicode: éè — ‘quoted’", "a" * 4000]
    for text in payloads:
        core.process_input(text)

    stored = [r.payload for r in core.acquisitions.read_all()]
    assert stored == payloads
    for record in core.acquisitions.read_all():
        assert record.payload_sha256 == payload_digest(record.payload)


# =====================================================================
# (g) THE REFUSAL - Ruling 53's sentinel, and it GATES
# =====================================================================

def test_g_an_unreadable_ledger_refuses_the_mint(tmp_path, monkeypatch):
    """Ruling 53's sentinel, whole: an existing-but-unreadable ledger leaves the
    mint UNDERIVED, and it REFUSES rather than minting from a floor it never
    saw. The ordinal is the boundary's CLOCK, so a reissued id would be two
    moments of logical time wearing one name."""
    ledger = _ledger(tmp_path)
    ledger.record("first", channel=AcquisitionChannel.USER_INPUT)

    broken = _UnreadableFor(monkeypatch, ledger.ledger_path)
    with pytest.raises(AcquisitionLedgerUnreadable):
        ledger.record("second", channel=AcquisitionChannel.USER_INPUT)

    # TRANSIENT BY NATURE: a recovered ledger resumes from its REAL maximum, by
    # construction rather than by a special case anyone must remember (Ruling 69
    # subsuming Ruling 53's re-derive).
    broken.recover()
    assert ledger.record("second",
                         channel=AcquisitionChannel.USER_INPUT
                         ).acquisition_id == "ACQ-0002"


def test_g_a_missing_ledger_is_a_first_run_not_a_fault(tmp_path):
    ledger = _ledger(tmp_path, name="never_written.jsonl")
    assert ledger.read_all() == []
    assert ledger.record("first", channel=AcquisitionChannel.USER_INPUT
                         ).acquisition_id == "ACQ-0001"


def test_g_the_refusal_gates_perception_and_writes_nothing_downstream(
        monkeypatch):
    """THE WRITE GATES THE ARRIVAL. Measured DOWNSTREAM, not asserted.

    Boundary facts cannot be reconstructed later, so a claim whose arrival
    cannot be recorded produces NO ancestry line, NO echo and NO topology node -
    Ruling 58's gate, one layer out and one line earlier.
    """
    core = AureaCore()
    core.process_input("a first, successful arrival")

    echoes = core.stats["echoes_processed"]
    nodes = len(core.tca.topology.nodes)
    clm = len(core.ancestry.read_all())

    _UnreadableFor(monkeypatch, core.acquisitions.ledger_path)
    with pytest.raises(AcquisitionLedgerUnreadable):
        core.process_input("this must not be perceived")
    monkeypatch.undo()

    assert core.stats["echoes_processed"] == echoes, "NO echo was built"
    assert len(core.tca.topology.nodes) == nodes, "NO node was placed"
    assert len(core.ancestry.read_all()) == clm, "NO ancestry line was appended"


def test_g_the_refusal_is_in_the_structural_taxonomy():
    """Ruling 25's clause: a structural violation is not an error message.

    Concrete, and not a base class of any other member - the tuple is CLOSED
    (Ruling 25) and membership is a DECISION, made here by M4-alpha.
    """
    assert AcquisitionLedgerUnreadable in STRUCTURAL_VIOLATIONS
    for member in STRUCTURAL_VIOLATIONS:
        others = [o for o in STRUCTURAL_VIOLATIONS if o is not member]
        assert not any(issubclass(o, member) for o in others)


def test_g_the_refusal_is_not_in_dees_expected_pair():
    """Ruling 48's partition, checked rather than assumed: a spent ceiling is
    SAE exercising authority; an unreadable boundary is a breach report. It
    PROPAGATES."""
    import src.doctrine.dee as dee_mod
    tree = ast.parse(Path(dee_mod.__file__).read_text(encoding="utf-8"))
    approve = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_approve")
    caught = [e.id for n in ast.walk(approve) if isinstance(n, ast.Try)
              for h in n.handlers if isinstance(h.type, ast.Tuple)
              for e in h.type.elts if isinstance(e, ast.Name)]
    assert "AcquisitionLedgerUnreadable" not in caught


# =====================================================================
# (h) ERA HONESTY - legacy lines, unknown vocabularies, torn lines
# =====================================================================

def test_h_a_legacy_claim_line_without_an_acquisition_ref_reads_none(tmp_path):
    """A claim minted before the boundary existed has no arrival record, and
    saying so is the honest answer. **No backfill and no inference** - Ruling
    68's forensic law, and Ruling 76's `None`-means-legacy verbatim."""
    path = tmp_path / "legacy_claim_ancestry.jsonl"
    path.write_text(json.dumps({
        "claim_id": "CLM-0001", "origin_kind": "human",
        "recorded_at": "2026-01-01T00:00:00",
        "asserted_by": {"state": "absent", "value": None},
        "basis": {"state": "absent", "value": None},
        "replication_refs": {"state": "absent", "value": None},
        "connecting_assumptions": {"state": "absent", "value": None},
        "defeaters": {"state": "absent", "value": None},
    }) + "\n", encoding="utf-8")

    ledger = ClaimAncestryLedger(ledger_path=str(path))
    records = ledger.read_all()
    assert len(records) == 1
    assert records[0].acquisition_ref is None
    # AND THE BYTES ARE NEVER REWRITTEN: a legacy line stays as it was written.
    before = path.read_bytes()
    ledger.read_all()
    assert path.read_bytes() == before


def test_h_an_unknown_vocabulary_member_drops_the_line_and_is_never_coerced(
        tmp_path):
    """A forensic log outlives the code that wrote it. Reading an unknown
    channel as a known one would put a fact in the reader's hands that the
    writer never recorded (Ruling 58's `from_dict`, verbatim reasoning)."""
    path = tmp_path / "acquisitions.jsonl"
    good = {"acquisition_id": "ACQ-0001", "channel": "user_input",
            "correlation_id": "ACQ-0001", "payload": "p",
            "payload_sha256": payload_digest("p"), "integrity": "structural",
            "method_warrant": "none", "warrant_conditions": [],
            "content_standing": "provisional_unvalidated", "recorded_wall": ""}
    future = dict(good, acquisition_id="ACQ-0002", channel="tool_result")
    path.write_text(json.dumps(good) + "\n" + json.dumps(future) + "\n",
                    encoding="utf-8")

    ledger = AcquisitionLedger(ledger_path=str(path))
    assert [r.acquisition_id for r in ledger.read_all()] == ["ACQ-0001"]
    # ...BUT ITS ORDINAL IS STILL SEEN BY THE MINT (Ruling 69 res.2: the scan is
    # over RAW TEXT, so an id on an unreadable line is never reissued).
    assert ledger.record("next", channel=AcquisitionChannel.USER_INPUT
                         ).acquisition_id == "ACQ-0003"


def test_h_a_torn_last_line_contributes_nothing_but_burns_its_ordinal(tmp_path):
    """The standing torn-line property, inherited at the `ACQ-` prefix.

    Given a choice between burning an ordinal and forging one, burn it: a
    duplicate id in an append-only record is unrecoverable by construction
    (3a:112), and gaps are fine.
    """
    path = tmp_path / "acquisitions.jsonl"
    ledger = AcquisitionLedger(ledger_path=str(path))
    ledger.record("first", channel=AcquisitionChannel.USER_INPUT)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write('{"acquisition_id": "ACQ-0002", "channel": "user_i')

    assert [r.acquisition_id for r in ledger.read_all()] == ["ACQ-0001"]
    assert ledger.record("third", channel=AcquisitionChannel.USER_INPUT
                         ).acquisition_id == "ACQ-0003", (
        "the torn line's ordinal reached disk, so it is seen and never reissued")


# =====================================================================
# (i) NO CONSUMER, NO STORE HANDLE IN THE ADAPTER, AND THE ISOLATION ROW
# =====================================================================

def test_i_nothing_in_src_reads_the_acquisition_ledger():
    """Ruling 72's no-consumer form: the ledger is WRITTEN, not yet read by
    cognition. This goes RED the day something consumes it - which is exactly
    when that consumption needs its own ruling.

    The two WRITERS are the doors and are expected; `aurea_core` composes and
    writes, and nothing anywhere reads a record back into a decision.
    """
    readers = []
    for path in _src_files():
        rel = path.relative_to(REPO).as_posix()
        if rel.endswith("external/acquisition_ledger.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"read_all", "get", "correlated"}
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "acquisitions"):
                readers.append(f"{rel}:{node.lineno}")
    assert readers == [], (
        f"the acquisition ledger is READ at {readers}. It is written and not "
        f"yet consumed by cognition; a reader needs its own ruling.")


def test_i_the_adapter_still_holds_no_writer_and_no_path():
    """Ruling 70's pin (b) UNWEAKENED, re-asserted here because M4 is the pass
    that created the temptation to hand this module a ledger.

    **The adapter DECLARES the channel; it does not WRITE the record.** Writing
    the request half here would have meant a store handle and the end of "the
    adapter cannot reach a store it is never handed" - and the narrower reading
    is the truer one, because this module never had the request (res.2).
    """
    tree = _tree(SRC / "external" / "model_provider.py")
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in {"open", "Path",
                                                          "AcquisitionLedger"}:
                offenders.append(f"{func.id}:{node.lineno}")
            if (isinstance(func, ast.Attribute)
                    and func.attr in {"dump", "dumps", "write", "mkdir",
                                      "record"}):
                offenders.append(f"{func.attr}:{node.lineno}")
    assert offenders == [], (
        f"the adapter reaches a write surface at {offenders}")

    imported = {n.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                for n in node.names}
    assert "AcquisitionLedger" not in imported, (
        "the adapter imports the CHANNEL VOCABULARY only - importing a "
        "vocabulary is not consuming a store (Ruling 63's precedent)")
    assert "AcquisitionChannel" in imported


def test_i_the_store_is_registered_in_both_isolation_tables():
    """Ruling 31's standing rule: a durable write path must be a class attribute
    or an `__init__` default AND be redirected in the SAME commit.

    Both tables, because they are separate mechanisms with separate coverage -
    and this store is written on every perceived arrival, so an omission would
    not have been latent.
    """
    from scripts.soak import _injection_table
    _, init_defaults = _injection_table()
    assert any(cls is AcquisitionLedger and param == "ledger_path"
               for cls, param, _ in init_defaults), "absent from the soak table"

    conftest = (REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "(AcquisitionLedger, \"ledger_path\"" in conftest, (
        "absent from the suite's isolation table")

    # AND THE DEFAULT ITSELF RESOLVES UNDER `data/runtime/` (Ruling 39), read
    # from SOURCE rather than from the live signature - under the fixture the
    # live one is a tmp path, which would prove isolation works while saying
    # nothing about what ships.
    tree = _tree()
    init = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                and n.name == "__init__")
    default = init.args.defaults[-1]
    assert isinstance(default, ast.Constant)
    assert default.value.startswith("data/runtime/")


# =====================================================================
# (j) THE CHAOS CASE THAT IS ALPHA'S OWN - heading item 13.5
# =====================================================================
#
# 13.5 asks for an interrupt AT AN ACQUISITION POINT with the divergence
# detector reading CLEAN across the restart. **THIS CASE IS ENTIRELY M4-alpha's
# AND DEPENDS ON NOTHING FROM M4-beta**: it interrupts the boundary record
# itself, not any wall-clock mint. The rest of the chaos family - the replay
# comparison in particular - is beta's and is STOPPED with it; see the pass's
# record for the measured reason.

def test_j_a_torn_acquisition_line_survives_an_unclean_restart(tmp_path):
    """Interrupt at an acquisition point; restart WITHOUT a checkpoint.

    **NO `save_state` IS CALLED ANYWHERE HERE**, deliberately: Ruling 78 made
    every durable write eager precisely so a restart needs no cooperation, and
    calling the checkpoint would test the checkpoint instead of the law.

    The last line is TORN - bytes on disk, unparseable - which is what a crash
    mid-append leaves. Three properties across the boundary:
      1. the readable arrivals survive and the torn one contributes nothing;
      2. THE TORN LINE'S ORDINAL IS STILL BURNED, so the resumed process cannot
         reissue it (Ruling 69 res.2: the scan is over RAW TEXT);
      3. the ancestry join still resolves for every claim that completed.
    """
    acq_path = tmp_path / "acquisitions.jsonl"
    clm_path = tmp_path / "claim_ancestry.jsonl"

    first = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq_path)),
                      ancestry=ClaimAncestryLedger(ledger_path=str(clm_path)))
    for text in ("first arrival", "second arrival"):
        first.process_input(text)
    assert len(_lines(first.acquisitions)) == 2

    # THE INTERRUPT: a third arrival lands half-written and the process dies.
    with open(acq_path, "a", encoding="utf-8") as handle:
        handle.write('{"acquisition_id": "ACQ-0003", "channel": "user_inp')
    del first

    # THE RESTART. A fresh core over the same paths, no checkpoint, no repair.
    resumed = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq_path)),
                        ancestry=ClaimAncestryLedger(ledger_path=str(clm_path)))

    survived = resumed.acquisitions.read_all()
    assert [r.acquisition_id for r in survived] == ["ACQ-0001", "ACQ-0002"], (
        "the torn line contributes nothing (floor semantics) and the readable "
        "arrivals are untouched")

    result = resumed.process_input("after the crash")
    assert result["claim_id"] is not None
    claim = resumed.ancestry.get(result["claim_id"])
    assert claim.acquisition_ref == "ACQ-0004", (
        "ACQ-0003's bytes reached disk, so its ordinal is BURNED and never "
        "reissued - a gap is fine, a forged id is not (Ruling 69 res.2)")

    # ------------------------------------------------------------------
    # THE MEASURED FINDING IS CLOSED - M4-δ, THE COLUMN-ZERO LAW.
    # ------------------------------------------------------------------
    # **THIS PIN'S TRIPWIRE FIRED WHEN THE DEFECT DIED, WHICH IS WHAT IT WAS
    # FOR** (Ruling 75's `paradox_void` form). Its old assertion recorded the
    # swallow as a measured finding and said in its own message: "if this now
    # resolves, the torn-append seam has been ruled on - update this pin and
    # cite the ruling." It has, and this is that update.
    #
    #     OLD (M4-alpha, 2026-08-15):
    #         assert resumed.acquisitions.get("ACQ-0004") is None
    #         ... "the record written immediately after a torn append is
    #             swallowed by it"
    #         resumed.process_input("and the one after that")
    #         assert [...ids...] == ["ACQ-0001", "ACQ-0002", "ACQ-0005"]
    #     NEW (M4-δ):
    #         ACQ-0004 SURVIVES, and the run continues at ACQ-0005.
    #
    # **THE ASSERTION INVERTS BECAUSE THE BEHAVIOUR WAS RULED ON, NOT BECAUSE
    # THE TEST WAS BENT.** `durable_append_text` now begins every append at
    # column 0: if the previous write was torn, one newline goes down first. The
    # torn fragment becomes its OWN line and is STILL REFUSED by floor semantics
    # - nothing is repaired into validity - and it stops taking the next record
    # with it.
    survivor = resumed.acquisitions.get("ACQ-0004")
    assert survivor is not None, (
        "M4-δ: the record written after a torn append SURVIVES - the funnel "
        "opens a new line for it rather than letting the fragment swallow it")
    assert survivor.payload == "after the crash"

    # THE TORN FRAGMENT IS STILL NOT A RECORD, and that is the half that must
    # never be traded for the half above.
    assert resumed.acquisitions.get("ACQ-0003") is None, (
        "the torn fragment is refused exactly as before - M4-δ repairs the "
        "BOUNDARY, never the record")

    resumed.process_input("and the one after that")
    assert [r.acquisition_id for r in resumed.acquisitions.read_all()] == [
        "ACQ-0001", "ACQ-0002", "ACQ-0004", "ACQ-0005"]

    # THE JOIN STILL RESOLVES for every arrival that survived the tear.
    survivors = {r.acquisition_id for r in resumed.acquisitions.read_all()}
    for claim in resumed.ancestry.read_all():
        if claim.acquisition_ref in survivors:
            assert resumed.acquisitions.get(claim.acquisition_ref) is not None


def test_j_the_divergence_detector_reads_clean_across_the_interrupt(tmp_path):
    """13.5's own sentence: the detector reads CLEAN across an unclean restart.

    It runs at EVERY construction (Ruling 79, AST-pinned to `__init__`'s last
    act), so the resumed core below has already run it by the time this asserts.
    A torn boundary line is honest crash residue that Ruling 78's ordering law
    already adjudicated - **not** a cross-store disagreement - so a finding here
    would mean the detector had started reporting the survivable.
    """
    acq_path = tmp_path / "acquisitions.jsonl"
    clm_path = tmp_path / "claim_ancestry.jsonl"

    first = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq_path)),
                      ancestry=ClaimAncestryLedger(ledger_path=str(clm_path)))
    first.process_input("an arrival before the crash")
    assert first.divergence_findings == [], "clean before the interrupt"

    with open(acq_path, "a", encoding="utf-8") as handle:
        handle.write('{"acquisition_id": "ACQ-0002", "chan')
    del first

    resumed = AureaCore(acquisitions=AcquisitionLedger(ledger_path=str(acq_path)),
                        ancestry=ClaimAncestryLedger(ledger_path=str(clm_path)))
    assert resumed.divergence_findings == [], (
        f"the detector reported {resumed.divergence_findings} across an "
        f"unclean restart. Crash residue at the boundary is survivable and "
        f"already adjudicated; a finding here is a REPORT of the normal.")
    assert resumed.divergence_log_failures == []


def test_j_the_torn_append_finding_is_not_this_stores_and_the_proof_is_executable():
    """THE FINDING'S SCOPE, MEASURED ON LEDGERS THIS PASS DID NOT TOUCH.

    A claim that a defect is "pre-existing and shared" is worth exactly as much
    as its evidence, so the evidence is here rather than in a sentence: the same
    interrupt is driven against `claim_ancestry` (Ruling 58) and `cae`
    (Ruling 45).

        ~~...and both swallow the record written after the tear. **THIS IS WHY
        THE REMEDY IS A MANIFEST DECISION AND NOT A BUILD LANE'S:** the seam is
        Ruling 78 res.2's caller-supplies-the-newline resolution, and it is
        shared by every append-only ledger in the tree.~~

    **SUPERSEDED 2026-08-15 BY M4-δ, old text kept verbatim - and the shared
    scope this pin established is exactly WHY it was ruled at the funnel rather
    than patched at a site.** The remedy was a manifest decision, it was taken,
    and it landed in ONE place: `durable_append_text` now begins every append at
    column 0. So this pin keeps its subject - the behaviour is shared by every
    append-only ledger - and INVERTS its verdict, because what is shared is now
    the fix.

        OLD:  assert len(ledger.read_all()) == 1   # the post-tear record is lost
        NEW:  assert len(ledger.read_all()) == 2   # ...and it survives
    """
    from src.doctrine.cae import CAE
    import tempfile

    root = Path(tempfile.mkdtemp(prefix="m4_torn_scope_"))
    for build, mint, torn in (
        (lambda p: ClaimAncestryLedger(ledger_path=str(p)),
         lambda L: L.record(OriginDeclaration()), '{"claim_id": "X", "part'),
        (lambda p: CAE(ledger_path=str(p)),
         lambda L: L.record(event="e", target="T"), '{"cae_id": "X", "part'),
    ):
        path = root / f"{id(build)}.jsonl"
        ledger = build(path)
        mint(ledger)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(torn)
        mint(ledger)
        records = ledger.read_all()
        assert len(records) == 2, (
            f"{type(ledger).__name__} SWALLOWED the post-tear record. M4-δ's "
            f"column-zero law is what stops that, at the funnel, for every "
            f"append-only ledger at once - so a failure here means the boundary "
            f"invariant has been removed or routed around.")
