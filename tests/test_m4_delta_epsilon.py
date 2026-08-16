"""
test_m4_delta_epsilon.py - M4-δ (the column-zero law) and M4-ε (the declaration
fields). M4's last slice.

    **δ: EVERY APPEND BEGINS AT COLUMN 0.**
    **ε: WHAT THE CHANNEL DECLARED IS RECORDED ON THE ARRIVAL.**

δ rules the finding M4-α measured and reported: a torn append left bytes with no
trailing newline, so the next append concatenated onto them and the first record
written after a crash was SWALLOWED and unreadable. The mint was safe; the record
was lost. ε closes the one thing M4-γ measured a replay could not reconstruct.

RED-FIRST, BOTH REAL. At `6e818e9` the swallow reproduces on `claim_ancestry`
and `cae` (that is the α finding's own executable proof, which lived in this
suite as a MEASURED pin and has now inverted), and a declared origin replays as
UNDECLARED. Both were watched in a detached worktree there.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts.replay import _origin_for, verify
from src.aurea_core import AureaCore
from src.doctrine.cae import CAE
from src.external.acquisition_ledger import (AcquisitionChannel,
                                             AcquisitionDeclaration,
                                             AcquisitionLedger,
                                             DECLARABLE_FIELDS)
from src.external.claim_ancestry import (ClaimAncestryLedger, FieldState,
                                         OriginDeclaration, OriginKind,
                                         declared_none, provided)
from src.executive.attention_policy import (POLICY_NAME, POLICY_VERSION,
                                            AttentionPolicy)
from src.executive.derived_view import ChairState, DerivedView
from src.executive.inquiry_generator import (GENERATOR_NAME, GENERATOR_VERSION,
                                             CandidatePartition,
                                             DiscrepancyClass, DriftBasis,
                                             InquiryCandidate)
from src.executive.inquiry_log import InquiryLog
from src.executive.selection_log import SelectionLog
from src.external.model_provider import ingest_model_assertion
from src.external.prediction_ledger import PredictionLedger
from src.filtration.episode_record import EpisodeRecord
from src.filtration.obligation_ledger import ObligationLedger, TargetKind
from src.goals.goal_activation import ActivationLayer
from src.goals.goal_arbitration import GoalArbiter
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalProvenance)
from src.utils.atomic_write import _ends_mid_line, durable_append_text
from src.utils.echo_memory import EchoMemory
from src.worldmodel.proposition_ledger import (PropositionKind,
                                               PropositionLedger)

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
FUNNEL = SRC / "utils" / "atomic_write.py"

IDENTITY = "openai/gpt-9/2026-01-15"


# =====================================================================
# THE LEDGER POPULATION - DERIVED FRESH, NEVER INHERITED
# =====================================================================
#
# The handoff named NINE. **THE AST CENSUS FINDS TEN**, and the population is
# derived below rather than copied so the number cannot go stale: every module
# that appends through Ruling 78's funnel AND mints an ordinal is a ledger whose
# records carry ids, which is what makes a swallowed record a LOST RECORD rather
# than a lost line.
#
# `aurea_core.py` is deliberately NOT one, and it is the trap in this census: it
# imports `derive_max_ordinal` (for the divergence detector's FLOOR READ) and it
# appends through the funnel (the structural-violation and divergence logs), but
# those appends mint nothing. Import-plus-append is not a mint.

def _derived_ledger_modules() -> set:
    """Every `src/` module that appends through the funnel AND mints."""
    found = set()
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        appends = any(isinstance(n, ast.Call)
                      and getattr(n.func, "id", None) == "durable_append_text"
                      for n in ast.walk(tree))
        if not appends:
            continue
        # A MINT is an id built from an ordinal, not merely an import of the
        # helper - which is exactly what keeps `aurea_core` out.
        mints = any(
            isinstance(n, ast.JoinedStr)
            and any(isinstance(v, ast.FormattedValue) for v in n.values)
            and "PREFIX" in ast.dump(n)
            for n in ast.walk(tree))
        if mints:
            found.add(path.relative_to(REPO).as_posix())
    return found


def _obligation(path):
    return ObligationLedger(ledger_path=str(path))


def _episode(path):
    return EpisodeRecord(log_path=str(path))


def _arbiter(path):
    ledger = GoalLedger(ledger_path=str(Path(path).with_suffix(".goals")))
    ledger.commit(desired_state="x", kind=GoalKind.RESEARCH,
                  level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="t")
    return GoalArbiter(ledger, log_path=str(path))


def _activation(path):
    """TWO commitments, deliberately: attention is SERIAL PER GOAL (Ruling 74),
    so a second examination must be able to select a DIFFERENT goal for a second
    activation to open at all. Ruling 73-A's ladder rotates, which is what makes
    that work - and this row appends twice, like every other."""
    arbiter = _arbiter(Path(path).with_suffix(".exm"))
    arbiter.ledger.commit(desired_state="y", kind=GoalKind.RESEARCH,
                          level=GoalLevel.PROJECT,
                          provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                          asserter="t")
    return ActivationLayer(arbiter, log_path=str(path))


# (name, build, append-one-record, module, read-back)
LEDGERS = [
    ("cae", lambda p: CAE(ledger_path=str(p)),
     lambda L: L.record(event="e", target="T"),
     "src/doctrine/cae.py", lambda L: L.read_all()),
    ("ancestry", lambda p: ClaimAncestryLedger(ledger_path=str(p)),
     lambda L: L.record(OriginDeclaration(kind=OriginKind.HUMAN)),
     "src/external/claim_ancestry.py", lambda L: L.read_all()),
    ("acquisition", lambda p: AcquisitionLedger(ledger_path=str(p)),
     lambda L: L.record("an arrival", channel=AcquisitionChannel.USER_INPUT),
     "src/external/acquisition_ledger.py", lambda L: L.read_all()),
    ("prediction", lambda p: PredictionLedger(ledger_path=str(p)),
     lambda L: L.commit(expected_result="x", success_criteria=provided("s")),
     "src/external/prediction_ledger.py", lambda L: L.read_all()),
    ("goal", lambda p: GoalLedger(ledger_path=str(p)),
     lambda L: L.commit(desired_state="x", kind=GoalKind.RESEARCH,
                        level=GoalLevel.PROJECT,
                        provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                        asserter="t"),
     "src/goals/goal_ledger.py", lambda L: L.commitments()),
    ("examination", _arbiter, lambda A: A.examine(),
     "src/goals/goal_arbitration.py", lambda A: A.examinations()),
    ("activation", _activation,
     lambda X: X.open_activation(X.arbiter.examine(),
                                 __import__("src.goals.goal_activation",
                                            fromlist=["x"]).BoundKind
                                 .EXAMINATION_BOUND, 1),
     "src/goals/goal_activation.py", lambda X: X.read_all()),
    ("echo", lambda p: EchoMemory(filepath=str(p)),
     lambda M: M.record("a perceived claim"),
     "src/utils/echo_memory.py", lambda M: M.read_all()),
    ("obligation", _obligation,
     lambda L: L.admit(source="s", target_kind=TargetKind.CLAIM,
                       target_id="CLM-0001", claim_text="owed"),
     "src/filtration/obligation_ledger.py", lambda L: L.read_all()),
    ("episode", _episode,
     lambda E: E.open_episode(["OBL-0001"], 3),
     "src/filtration/episode_record.py", lambda E: E.read_all()),
    # M6-α MIGRATION (2026-08-15), Ruling-14 form. NO ASSERTION MOVED - one row
    # added, so every claim in this file now also binds the proposition ledger.
    # **THE STANDING DERIVATION ABOVE FOUND IT WITHOUT BEING TOLD**, which is
    # exactly what the M4 census correction bought: the pin reddened on the new
    # store's first commit rather than covering it by omission.
    #
    # UNGROUNDED, deliberately: a proposition with zero references admits, so
    # this row needs no resolvers and exercises the write path alone.
    ("proposition", lambda p: PropositionLedger(ledger_path=str(p)),
     lambda L: L.record(PropositionKind.STATE, "a world proposition"),
     "src/worldmodel/proposition_ledger.py", lambda L: L.summaries()),
    # M7-b MIGRATION (2026-08-16), Ruling-14 form. NO ASSERTION MOVED - one row
    # added, so every claim in this file now also binds the selection log.
    # **THE STANDING DERIVATION FOUND IT WITHOUT BEING TOLD, a second time**,
    # and its failure message is what ordered this edit: "Add the row - a
    # ledger absent from it makes every claim below TRUE BY OMISSION for that
    # store." That is the whole value of deriving the population instead of
    # listing it.
    #
    # A `NOTHING_ATTENDABLE` selection is the cheapest honest write this store
    # has: it needs no candidates, so the row exercises the mint and the append
    # without constructing a kernel.
    # A kernel with nothing attendable, built directly rather than derived:
    # this row is about the STORE's append discipline, not about the policy.
    ("attention_selection", lambda p: SelectionLog(log_path=str(p)),
     lambda L: L.record(
         AttentionPolicy().select(_EMPTY_VIEW), POLICY_NAME, POLICY_VERSION),
     "src/executive/selection_log.py", lambda L: L.selections()),
    # M7-c MIGRATION (2026-08-16), Ruling-14 form. NO ASSERTION MOVED - one row
    # added, so every claim in this file now also binds the inquiry act log.
    # **THE STANDING DERIVATION FOUND IT WITHOUT BEING TOLD, a third time.**
    #
    # A DRIFT FINDING is the cheapest honest write this store has: it needs no
    # goal, no licence and no admission, so the row exercises the mint and the
    # append without constructing a kernel.
    ("inquiry_act", lambda p: InquiryLog(log_path=str(p)),
     lambda L: L.record(_DRIFT_CANDIDATE, GENERATOR_NAME, GENERATOR_VERSION),
     "src/executive/inquiry_log.py", lambda L: L.inquiries()),
]
_EMPTY_VIEW = DerivedView(
    open_obligations=(), unresolved_predictions=(), committed_goals=(),
    chair=ChairState.UNREGISTERED, verdict_acquisition_id=None, candidates=())

_DRIFT_CANDIDATE = InquiryCandidate(
    discrepancy_class=DiscrepancyClass.HORIZONLESS_COMMITMENT,
    source_record_ids=("PRD-0001",),
    partition=CandidatePartition.DRIFT,
    derivation_depth=1,
    drift_basis=DriftBasis.NO_DERIVABLE_LICENSE,
    horizon_state="absent")

IDS = [row[0] for row in LEDGERS]


def test_the_ledger_population_is_derived_and_matches_this_table():
    """THE CENSUS, STANDING RATHER THAN ONE-TIME - and it CORRECTS the handoff.

    The handoff named a NINE-ledger population; the tree holds TEN. A count
    carried in prose goes stale silently (§4's own lesson, three times over this
    milestone), so the population is re-derived from `src/` on every run and
    compared against the table this file parametrizes over. A ledger added
    without a row here reddens instead of being covered by omission.
    """
    derived = _derived_ledger_modules()
    covered = {row[3] for row in LEDGERS}
    assert derived == covered, (
        f"the funnel-appending, minting population is {sorted(derived)} but "
        f"this file covers {sorted(covered)}. Add the row - a ledger absent "
        f"from it makes every claim below TRUE BY OMISSION for that store.")
    assert len(covered) == 13, (
        "THIRTEEN as of M7-c (the inquiry act log). ~~TWELVE as of M7-b (the "
        "attention selection log).~~ ~~ELEVEN as of M6-α "
        "(the proposition ledger).~~ ~~TEN, not the handoff's "
        "nine~~ - `aurea_core` imports the mint helper for a FLOOR READ and "
        "appends only forensic logs, and the M3-A stores were never in Ruling "
        "69's battery list")


# =====================================================================
# (δ-a) THE BOUNDARY INVARIANT, END TO END, ON EVERY LEDGER
# =====================================================================

@pytest.mark.parametrize("name,build,append,module,read", LEDGERS, ids=IDS)
def test_delta_a_a_record_after_a_torn_append_survives(name, build, append,
                                                       module, read, tmp_path):
    """THE LOAD-BEARING PIN. **RED at `6e818e9`** on every row.

    Write a record, TEAR the next append (bytes with no trailing newline, which
    is what a crash mid-write leaves), then write another. Before δ the third
    write concatenated onto the fragment and was unreadable; now it is its own
    line.

    BOTH HALVES ARE ASSERTED TOGETHER AND THAT IS THE POINT: the new record
    SURVIVES **and** the fragment is STILL REFUSED. A remedy that made the
    fragment parse would be repairing a half-written record into validity, which
    is the one thing this law must never do.
    """
    path = tmp_path / f"{name}.jsonl"
    ledger = build(path)
    append(ledger)
    before = len(read(ledger))

    with open(path, "a", encoding="utf-8") as handle:
        handle.write('{"id": "TORN-0001", "half')          # the crash

    append(ledger)

    after = read(ledger)
    assert len(after) == before + 1, (
        f"{name}: the record written after a torn append was SWALLOWED. M4-δ's "
        f"column-zero law stops that at the funnel, for every ledger at once.")
    assert "TORN-0001" not in path.read_text(encoding="utf-8").splitlines()[-1]

    # THE FRAGMENT IS STILL NOT A RECORD - refused by floor semantics, exactly
    # as the standing torn-line law provides.
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    unparseable = [l for l in lines if not _parses(l)]
    assert len(unparseable) == 1 and "half" in unparseable[0], (
        f"{name}: the torn fragment must remain unparseable - δ repairs the "
        f"BOUNDARY, never the record")


def _parses(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except ValueError:
        return False


# =====================================================================
# (δ-b) THE PREFIX CANNOT FIRE ON A HEALTHY FILE
# =====================================================================

def test_delta_b_healthy_appends_are_byte_identical(tmp_path):
    """**THIS IS WHY THE DIFFERENTIAL FOR THIS PASS IS ZERO**, and it is pinned
    as bytes rather than argued.

    Every routed site writes `json.dumps(...) + "\\n"`, so a healthy file always
    ends at column 0 and the prefix never fires. The bytes on disk are exactly
    what they were before δ.
    """
    lines = ['{"a": 1}\n', '{"b": 2}\n', '{"c": 3}\n']

    through_funnel = tmp_path / "healthy.jsonl"
    for line in lines:
        durable_append_text(through_funnel, line)

    # THE CONTROL IS A RAW `open`, WHICH IS RULING 78's OWN WORDS: "the bytes on
    # disk are identical to what the raw `open` produced". Comparing against a
    # hand-built literal would instead measure the PLATFORM's newline
    # translation - text mode writes CRLF on this one - which δ neither
    # introduces nor changes, and which would make this pin fail for a reason
    # that has nothing to do with the law it guards.
    control = tmp_path / "control.jsonl"
    for line in lines:
        with open(control, "a", encoding="utf-8") as handle:
            handle.write(line)

    assert through_funnel.read_bytes() == control.read_bytes()
    assert through_funnel.read_text(encoding="utf-8") == "".join(lines)


def test_delta_b_an_empty_or_absent_file_takes_no_prefix(tmp_path):
    """A file at column 0 already is at column 0. An absent one likewise.

    A JUSTIFIED EQUIVALENT MUTANT IS ANNOTATED HERE (the house's practice):
    deleting `_ends_mid_line`'s explicit `st_size == 0` guard leaves this pin
    GREEN, and it is genuinely equivalent - MEASURED, not assumed. Without the
    guard an empty file reaches `probe.seek(-1, SEEK_END)`, which raises
    `OSError`, which the fallback catches and answers False; an absent file
    raises from `stat()` and lands in the same place.

    **THE EXPLICIT GUARD IS KEPT ANYWAY**, because equivalence here rests on a
    SEEK ERROR having the right meaning. Correctness that depends on an
    exception firing is the fragile shape this codebase refuses on principle -
    it reads as accidental to the next reader, and it would stop being
    equivalent the day the fallback narrowed.
    """
    absent = tmp_path / "absent.jsonl"
    durable_append_text(absent, '{"first": true}\n')
    assert absent.read_text(encoding="utf-8") == '{"first": true}\n'

    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    durable_append_text(empty, '{"first": true}\n')
    assert empty.read_text(encoding="utf-8") == '{"first": true}\n'


def test_delta_b_the_caller_still_owns_the_format(tmp_path):
    """RES.2 UNWEAKENED. The funnel adds nothing to the CALLER'S CONTENT: a
    single append lands verbatim, newline or no newline."""
    target = tmp_path / "verbatim.log"
    durable_append_text(target, "no trailing newline")
    assert target.read_text(encoding="utf-8") == "no trailing newline"


def test_delta_b_the_probe_reads_bytes_not_decoded_text(tmp_path):
    """A torn multi-byte sequence must not raise on the way in.

    Decoding a file whose tail is half a UTF-8 character would raise on exactly
    the input this predicate exists to recognize, so the probe reads the last
    BYTE. Driven with a real truncated multi-byte tail.
    """
    target = tmp_path / "torn_utf8.jsonl"
    target.write_bytes('{"x": "é'.encode("utf-8")[:-1])      # half a character

    assert _ends_mid_line(target) is True
    durable_append_text(target, '{"y": 2}\n')
    assert path_lines(target)[-1] == '{"y": 2}'


def path_lines(path: Path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def test_delta_b_a_failed_probe_means_no_prefix_never_a_new_refusal(tmp_path,
                                                                    monkeypatch):
    """The probe must NOT become a new failure mode of the funnel.

    This funnel's raise semantics are RULED (Ruling 78): it raises, and each
    site decides. A probe that raised would turn a boundary it could not
    DETERMINE into a refusal for a write the caller could otherwise have made -
    letting a read hiccup gate a claim's perception. The fallback is exactly the
    pre-δ behaviour, so the worst case is bounded by the status quo.
    """
    import builtins

    target = tmp_path / "probe.jsonl"
    target.write_text('{"a": 1}\n', encoding="utf-8")

    real_open = builtins.open

    def failing_open(file, mode="r", *args, **kwargs):
        # THE BYTE PROBE ONLY - the append itself must still work, which is what
        # makes this measure the PROBE's failure rather than the disk's.
        if "b" in str(mode):
            raise OSError("simulated probe failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing_open)
    durable_append_text(target, '{"b": 2}\n')          # must NOT raise
    monkeypatch.undo()

    assert target.read_text(encoding="utf-8") == '{"a": 1}\n{"b": 2}\n'


def test_delta_b_the_law_lives_at_one_site():
    """δ IS A ONE-SITE LAW, and the funnel's totality is what makes that enough.

    Ruling 78's routing census says no mode-`"a"` write exists outside this
    module; re-derived here rather than cited, because the whole force of a
    one-site law is that the site is the only one.
    """
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        if path == FUNNEL:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "open":
                modes = [a.value for a in node.args[1:]
                         if isinstance(a, ast.Constant)]
                modes += [k.value.value for k in node.keywords
                          if k.arg == "mode" and isinstance(k.value, ast.Constant)]
                if any("a" in str(m) for m in modes):
                    offenders.append(f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    assert offenders == [], (
        f"a mode-'a' write outside the funnel at {offenders} - δ would not "
        f"bind there, and Ruling 78's routing census disagrees with itself")


# =====================================================================
# (ε-a) THE DECLARATION IS RECORDED AS DECLARED
# =====================================================================

def test_epsilon_a_the_block_records_exactly_what_was_declared(tmp_path):
    """**RED at `6e818e9`** - there was no block. Read back FROM THE FILE."""
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))

    ingest_model_assertion(
        core.process_input, "The bridge will hold.", IDENTITY,
        basis=provided({"kind": "retrieval"}),
        replication_refs=provided(["run-1"]),
        connecting_assumptions=declared_none())

    entry = json.loads(Path(core.acquisitions.ledger_path)
                       .read_text(encoding="utf-8").splitlines()[0])
    block = entry["declaration"]

    assert block["model_identity"] == IDENTITY
    assert block["basis"] == {"state": "provided", "value": {"kind": "retrieval"}}
    assert block["replication_refs"] == {"state": "provided", "value": ["run-1"]}
    assert block["connecting_assumptions"] == {"state": "declared_none",
                                               "value": None}
    # NOT MENTIONED BY THE CALLER -> ABSENT, RECORDED AS ABSENT. Manufacturing a
    # value because a field existed to hold it is L3's class, and the exact
    # defect Ruling 58 closed one record away from here.
    assert block["defeaters"] == {"state": "absent", "value": None}


def test_epsilon_a_the_identity_is_byte_identical_including_odd_shapes(tmp_path):
    """Ruling 70 res.1 RIDES: recorded AS DECLARED, never verified, never
    normalized, never parsed into parts - now in a second record, unchanged."""
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))
    weird = "  OpenAI / GPT-9 :: build 2026-01-15  \tsnapshot  "

    ingest_model_assertion(core.process_input, "A claim.", weird)

    record = core.acquisitions.read_all()[0]
    assert record.declaration.model_identity == weird


def test_epsilon_a_asserted_by_is_not_a_declarable_field():
    """It IS the model identity, which the block carries in its own field. A
    second, caller-settable copy would let an assertion be filed under someone
    else's name - `model_provider` draws the same line for the same reason."""
    assert "asserted_by" not in DECLARABLE_FIELDS
    assert set(DECLARABLE_FIELDS) == {"basis", "replication_refs",
                                      "connecting_assumptions", "defeaters"}


def test_epsilon_a_an_undeclared_arrival_records_no_block(tmp_path):
    """`None` is a real answer and is recorded as one - no empty block, no
    manufactured identity."""
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))
    core.process_input("a plain claim")

    assert core.acquisitions.read_all()[0].declaration is None
    entry = json.loads(Path(core.acquisitions.ledger_path)
                       .read_text(encoding="utf-8").splitlines()[0])
    assert entry["declaration"] is None


def test_epsilon_a_there_is_no_channel_gate_and_the_reason_is_a_pinned_case(
        tmp_path):
    """**NOT GATED ON MODEL_EXCHANGE, DELIBERATELY.**

    A human pasting a model's output through the user door is a USER_INPUT
    arrival of a MODEL_PREDICTION assertion - M4-α's own Ruling-30 case, already
    pinned - and a declaration there is honest. Gating on channel would refuse
    the one case this milestone established.
    """
    core = AureaCore(acquisitions=AcquisitionLedger(
        ledger_path=str(tmp_path / "acq.jsonl")))

    core.process_input(
        "A model said the bridge will hold.",
        origin=OriginDeclaration(kind=OriginKind.MODEL_PREDICTION),
        declaration=AcquisitionDeclaration(model_identity=IDENTITY))

    record = core.acquisitions.read_all()[0]
    assert record.channel is AcquisitionChannel.USER_INPUT
    assert record.declaration.model_identity == IDENTITY


def test_epsilon_a_a_raw_dict_is_refused(tmp_path):
    """A caller cannot record a declaration this ledger never typed."""
    ledger = AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl"))
    with pytest.raises(TypeError):
        ledger.record("x", channel=AcquisitionChannel.USER_INPUT,
                      declaration={"model_identity": IDENTITY})


def test_epsilon_a_a_bare_value_cannot_say_which_of_the_three_answers_it_is():
    with pytest.raises(TypeError):
        AcquisitionDeclaration(model_identity=IDENTITY, basis="a string")
    with pytest.raises(TypeError):
        AcquisitionDeclaration(model_identity=7)


# =====================================================================
# (ε-b) ERA HONESTY, AND THE ROUND TRIP
# =====================================================================

def test_epsilon_b_a_pre_epsilon_line_reads_as_none_and_replays_undeclared(
        tmp_path):
    """THE LEGACY HALF OF γ'S PIN SURVIVES, and it is still true.

    A record written before ε has no block, reads as `None`, and replays as
    UNDECLARED forever. Nothing is backfilled and nothing is inferred - that is
    an honest statement about what was written down at the time.
    """
    path = tmp_path / "legacy_acq.jsonl"
    path.write_text(json.dumps({
        "acquisition_id": "ACQ-0001", "channel": "model_exchange",
        "correlation_id": "ACQ-0001", "payload": "a model said so",
        "payload_sha256": "x" * 64, "integrity": "structural",
        "method_warrant": "none", "warrant_conditions": [],
        "content_standing": "provisional_unvalidated", "recorded_wall": "",
    }) + "\n", encoding="utf-8")

    record = AcquisitionLedger(ledger_path=str(path)).read_all()[0]
    assert record.declaration is None
    assert _origin_for(record.declaration) is None, (
        "a blockless record replays as UNDECLARED - γ's limitation, still true "
        "of the records it was true of")

    before = path.read_bytes()
    AcquisitionLedger(ledger_path=str(path)).read_all()
    assert path.read_bytes() == before, "legacy bytes are never rewritten"


def test_epsilon_b_declarations_round_trip_through_a_replay(tmp_path):
    """**THE HEADLINE, AND THE MIGRATION OF γ'S LIMITATION PIN.**

        ~~OLD (M4-γ): an identical census is NOT proof declarations round-trip,
        because the acquisition does not record the declaration.~~
        NEW (M4-ε): DECLARATIONS ROUND-TRIP, PROVEN - for records carrying the
        block.

    Proven on the ANCESTRY RECORDS rather than on the census, deliberately: a
    census counts, and a count can match while the contents differ. This
    compares what the claim ledger actually holds on both sides.
    """
    source = tmp_path / "acq.jsonl"
    first = AureaCore(
        acquisitions=AcquisitionLedger(ledger_path=str(source)),
        ancestry=ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl")))
    ingest_model_assertion(
        first.process_input, "The bridge will hold.", IDENTITY,
        basis=provided({"kind": "retrieval"}),
        defeaters=declared_none())

    original = first.ancestry.read_all()[0]
    assert original.origin_kind is OriginKind.MODEL_PREDICTION

    # THE REPLAY: a fresh core, driven from the recorded ledger alone.
    replayed_core = AureaCore(
        acquisitions=AcquisitionLedger(ledger_path=str(tmp_path / "acq2.jsonl")),
        ancestry=ClaimAncestryLedger(ledger_path=str(tmp_path / "clm2.jsonl")))
    for arrival in AcquisitionLedger(ledger_path=str(source)).read_all():
        replayed_core.process_input(arrival.payload,
                                    channel=arrival.channel,
                                    correlation_id=arrival.correlation_id,
                                    origin=_origin_for(arrival.declaration),
                                    declaration=arrival.declaration)

    replayed = replayed_core.ancestry.read_all()[0]
    assert replayed.origin_kind is OriginKind.MODEL_PREDICTION, (
        "a declared origin no longer replays as UNDECLARED")
    assert replayed.asserted_by.state is FieldState.PROVIDED
    assert replayed.asserted_by.value == IDENTITY
    assert replayed.basis.as_dict() == original.basis.as_dict()
    assert replayed.defeaters.state is FieldState.DECLARED_NONE
    for name in ("asserted_by", "basis", "replication_refs",
                 "connecting_assumptions", "defeaters"):
        assert (getattr(replayed, name).as_dict()
                == getattr(original, name).as_dict()), f"{name} did not survive"


def test_epsilon_b_the_replay_instrument_is_still_identical_end_to_end():
    """And the whole instrument still reports IDENTICAL - ε adds a field to the
    record without moving the census it was already reproducing."""
    report = verify(claims=["one arrival", "and another"])
    assert report["comparison"]["identical"], report["comparison"]["moved"]


def test_epsilon_b_the_origin_is_rebuilt_through_the_ruled_constructor():
    """AST. `_origin_for` must call `model_declaration`, not hand-roll an
    `OriginDeclaration`.

    A hand-rolled copy would be a second implementation of a ruled constructor,
    free to drift from it invisibly - the defect this house has closed
    repeatedly (Ruling 47's criterion names, Ruling 67's one-audit-two-callers).
    """
    import scripts.replay as replay_mod
    tree = ast.parse(Path(replay_mod.__file__).read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_origin_for")
    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "model_declaration" in called
    assert "OriginDeclaration" not in called


def test_epsilon_b_the_adapter_still_holds_no_writer():
    """RULING 70 PIN (b), UNWEAKENED - re-asserted because ε is the pass that
    gave the adapter a second thing to carry.

    **IT STILL DECLARES RATHER THAN WRITES**: it builds a value and hands it on,
    holding no ledger, opening no file and calling no `record`.
    """
    tree = ast.parse((SRC / "external" / "model_provider.py")
                     .read_text(encoding="utf-8"))
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
    assert offenders == [], f"the adapter reaches a write surface at {offenders}"

    imported = {n.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) for n in node.names}
    assert "AcquisitionLedger" not in imported
    assert {"AcquisitionChannel", "AcquisitionDeclaration"} <= imported, (
        "the adapter imports the VOCABULARY only - Ruling 63's precedent")


def test_epsilon_b_the_two_records_cannot_disagree_about_what_was_declared(
        tmp_path):
    """ONE DECLARATION, TWO PLACES IT IS WRITTEN DOWN, NO SECOND SOURCE OF
    TRUTH. Both are built from the same four caller inputs, so the claim's
    ancestry and the arrival's block must agree field for field."""
    core = AureaCore(
        acquisitions=AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl")),
        ancestry=ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl")))
    ingest_model_assertion(
        core.process_input, "A claim.", IDENTITY,
        basis=provided(["a", "b"]), replication_refs=declared_none())

    block = core.acquisitions.read_all()[0].declaration
    claim = core.ancestry.read_all()[0]

    assert claim.asserted_by.value == block.model_identity
    for name in DECLARABLE_FIELDS:
        assert (getattr(claim, name).as_dict()
                == getattr(block, name).as_dict()), f"{name} disagrees"


def test_delta_b_the_prefix_is_exactly_one_newline_and_the_fragment_is_untouched(
        tmp_path):
    """**FOUND BY A SURVIVING MUTANT.** The fragment's BYTES are preserved.

    A funnel that wrote anything other than a bare newline - a closing brace, a
    padding character, a "recovered" wrapper - would be REPAIRING a half-written
    record into something, which is the one thing this law must never do. The
    torn fragment must survive byte-for-byte as the invalid thing it is.

    Asserted as a byte-level prefix relation rather than by parsing, because
    parsing is what a clever repair would be trying to satisfy.
    """
    target = tmp_path / "torn.jsonl"
    fragment = '{"id": "TORN-0001", "half'
    target.write_text('{"a": 1}\n' + fragment, encoding="utf-8")
    before = target.read_bytes()

    durable_append_text(target, '{"b": 2}\n')

    after = target.read_bytes()
    assert after.startswith(before), (
        "the funnel altered bytes that were already on disk - it may only ADD "
        "a boundary, never touch the fragment")
    # CRLF is normalized because the PLATFORM's text-mode translation is not
    # δ's business - it applied identically before this ruling.
    added = after[len(before):].replace(b"\r\n", b"\n")
    assert added == b'\n{"b": 2}\n', (
        f"the funnel added {added!r} - it may add EXACTLY one newline before "
        f"the caller's bytes and nothing else")


def test_epsilon_b_the_instrument_itself_replays_a_declared_arrival(tmp_path):
    """**FOUND BY A SURVIVING MUTANT**, and it is the gap that mattered most.

    The round-trip pin above hand-drives `process_input`, so deleting the
    origin reconstruction inside the INSTRUMENT left it green - a proof about
    the mechanism that never exercised the thing shipping it. This drives
    `scripts/replay.py`'s own path end to end with a DECLARED arrival.

    It reads `claim_origin_kinds`, which is the census key ε added for exactly
    this: a count of arrivals can match while their declarations are lost, and
    an origin-kind breakdown moves the moment one replays as UNDECLARED.
    """
    from scripts.replay import _run_in_sandbox
    from scripts.soak import isolate

    isolate(tmp_path / "record")
    from src.aurea_core import AureaCore
    core = AureaCore()
    ingest_model_assertion(core.process_input, "The bridge will hold.",
                           IDENTITY, basis=provided({"kind": "retrieval"}))
    recorded = Path(core.acquisitions.ledger_path)
    assert core.ancestry.read_all()[0].origin_kind is OriginKind.MODEL_PREDICTION

    replayed = _run_in_sandbox(source=recorded)
    kinds = replayed["census"]["acquisitions"]["claim_origin_kinds"]
    assert kinds == {"model_prediction": 1}, (
        f"the instrument replayed the declared arrival as {kinds} - the origin "
        f"must be reconstructed from the recorded block, not dropped")
    assert replayed["census"]["acquisitions"]["declarations"] == 1
