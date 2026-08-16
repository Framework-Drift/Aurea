"""M7-c: endogenous inquiry -- the generator, licensing, depth, and the act log.

THE THIRTEEN BINDING PROPERTIES, in the specification's order (1-10 from the
base handoff, 11-13 from the ruling's addendum):

  1. Determinism -- identical kernel yields identical candidates AND partition.
  2. OVERDUE_UNRESOLVED fires on a passed horizon, not on a future one.
  3. HORIZONLESS_COMMITMENT fires by FieldState; DECLARED_NONE and ABSENT both
     captured and kept DISTINCT on the record.
  4. No derivable license -> DRIFT (NO_DERIVABLE_LICENSE), no admission tried.
  5. Depth 2 -> DRIFT (DEPTH_CEILING), witnessed with the loop's OWN admitted
     inquiry as the source.
  6. Kernel-owned dedup -- two cycles, two submissions, second carries the
     kernel's duplicate disposition; zero self-log reads.
  7. No sovereign goals -- no goal-ledger write path anywhere.
  8. The write gates the act, both legs.
  9. v-a and v-b pass BYTE-UNMODIFIED.
 10. No thresholds, no magnitudes, no clock reads.
 11. UNCHECKED refusal, both directions.
 12. Fabrication rejection -- the fires-control for the new member.
 13. The widening is entry-bound -- the guard still refuses beyond the ruled set.
"""

import ast
import hashlib
import pathlib

import pytest

from src.executive.derived_view import DerivedView
from src.executive.inquiry_generator import (
    GENERATOR_NAME,
    GENERATOR_VERSION,
    MAX_DERIVATION_DEPTH,
    CandidatePartition,
    DiscrepancyClass,
    DriftBasis,
    GeneratorIdentityMismatch,
    InquiryGenerator,
    LicenseBasis,
)
from src.executive.inquiry_log import InquiryLog, InquiryLogUnreadable, KernelDisposition
from src.executive.loop import ExecutiveLoop
from src.executive.selection_log import SelectionLog
from src.external.acquisition_ledger import AcquisitionLedger
from src.external.prediction_ledger import (PredictionLedger, declared_none,
                                            provided)
from src.filtration.obligation_ledger import (ObligationLedger, TargetKind,
                                              TargetResolution,
                                              UncheckableTarget)
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalProvenance)

SRC = pathlib.Path("src")


# ---------------------------------------------------------------------------
# Fixtures -- REAL ledgers throughout. Licensing is established the way the
# ruling authorizes: goals committed THROUGH THE LEDGER'S OWN API with their
# linkage fields populated, which is legitimate authorship and what those
# fields exist for. Nothing is fabricated and nothing is monkeypatched.
# ---------------------------------------------------------------------------

@pytest.fixture()
def kernel(tmp_path):
    predictions = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    obligations = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                                   prediction_ledger=predictions)
    goals = GoalLedger(ledger_path=str(tmp_path / "glc.jsonl"))
    acquisitions = AcquisitionLedger(ledger_path=str(tmp_path / "acq.jsonl"))
    return obligations, predictions, goals, acquisitions


def _loop(kernel, tmp_path):
    obligations, predictions, goals, acquisitions = kernel
    return ExecutiveLoop(
        obligations, predictions, goals, acquisitions,
        selections=SelectionLog(log_path=str(tmp_path / "sel.jsonl")),
        inquiries=InquiryLog(log_path=str(tmp_path / "inq.jsonl")))


def _advance_clock(obligations, steps=3):
    """Move the shared SEQ- clock forward with ordinary admissions."""
    for i in range(steps):
        obligations.admit("fixture", TargetKind.DOCTRINE, f"D-{i}", f"tick {i}")


def _goal_citing(goals, *, originating=(), justification=()):
    return goals.commit(
        desired_state="a committed direction", kind=GoalKind.RESEARCH,
        level=GoalLevel.PROJECT, provenance=GoalProvenance.EXTERNAL_PROPOSAL,
        asserter="fixture", originating_record_ids=tuple(originating),
        justification_claim_ids=tuple(justification))


# ===========================================================================
# PIN 1 - DETERMINISM
# ===========================================================================

def test_1_identical_kernel_yields_identical_candidates_and_partition(kernel,
                                                                     tmp_path):
    obligations, predictions, goals, _ = kernel
    p = predictions.commit("overdue", resolution_horizon=provided("SEQ-000001"))
    predictions.commit("bare")
    _advance_clock(obligations)
    _goal_citing(goals, originating=(p.prediction_id,))
    loop = _loop(kernel, tmp_path)

    first, second = loop.generate_inquiries(), loop.generate_inquiries()
    assert first == second
    assert [c.partition for c in first] == [c.partition for c in second]


# ===========================================================================
# PIN 2 - OVERDUE_UNRESOLVED, BOTH DIRECTIONS
# ===========================================================================

def test_2a_a_passed_horizon_fires(kernel, tmp_path):
    obligations, predictions, _, _ = kernel
    p = predictions.commit("overdue", resolution_horizon=provided("SEQ-000001"))
    _advance_clock(obligations)
    classes = {c.discrepancy_class for c in _loop(kernel, tmp_path).generate_inquiries()
               if c.source_record_ids == (p.prediction_id,)}
    assert classes == {DiscrepancyClass.OVERDUE_UNRESOLVED}


def test_2b_a_future_horizon_does_not_fire(kernel, tmp_path):
    obligations, predictions, _, _ = kernel
    p = predictions.commit("future", resolution_horizon=provided("SEQ-999999"))
    _advance_clock(obligations)
    assert [c for c in _loop(kernel, tmp_path).generate_inquiries()
            if c.source_record_ids == (p.prediction_id,)] == []


def test_2c_the_comparison_is_strict_at_the_boundary(kernel, tmp_path):
    """A horizon standing exactly AT the clock has been REACHED, not PASSED."""
    obligations, predictions, _, _ = kernel
    _advance_clock(obligations, steps=2)
    clock = _loop(kernel, tmp_path).observe().inquiry.max_seq_ordinal
    p = predictions.commit("at the boundary",
                           resolution_horizon=provided(f"SEQ-{clock:06d}"))
    assert [c for c in _loop(kernel, tmp_path).generate_inquiries()
            if c.source_record_ids == (p.prediction_id,)] == []


def test_2d_a_resolved_prediction_is_never_a_candidate(kernel, tmp_path):
    from src.external.prediction_ledger import PredictionOutcome
    obligations, predictions, _, _ = kernel
    p = predictions.commit("overdue but settled",
                           resolution_horizon=provided("SEQ-000001"),
                           success_criteria=provided("s"))
    predictions.resolve(p.prediction_id, PredictionOutcome.CONFIRMED,
                        "success_criteria")
    _advance_clock(obligations)
    assert _loop(kernel, tmp_path).generate_inquiries() == ()


def test_2e_an_uncomparable_horizon_yields_nothing_and_is_not_horizonless(
        kernel, tmp_path):
    """RULING 61 res.5: the format is not interpreted, so no class fires.

    A PROVIDED prose horizon is NOT horizonless (one was declared) and cannot
    be shown overdue (nothing comparable was recorded). Inventing a reading of
    the value is exactly what that ruling refuses.
    """
    obligations, predictions, _, _ = kernel
    p = predictions.commit("prose", resolution_horizon=provided("by next review"))
    _advance_clock(obligations)
    assert [c for c in _loop(kernel, tmp_path).generate_inquiries()
            if c.source_record_ids == (p.prediction_id,)] == []


# ===========================================================================
# PIN 3 - HORIZONLESS_COMMITMENT, BY FIELDSTATE, TWO STATES KEPT DISTINCT
# ===========================================================================

def test_3_declared_none_and_absent_both_fire_and_stay_distinct(kernel, tmp_path):
    _, predictions, _, _ = kernel
    none_declared = predictions.commit("declared none",
                                       resolution_horizon=declared_none())
    never_asked = predictions.commit("never asked")
    candidates = {c.source_record_ids[0]: c
                  for c in _loop(kernel, tmp_path).generate_inquiries()}

    for pid in (none_declared.prediction_id, never_asked.prediction_id):
        assert candidates[pid].discrepancy_class is \
            DiscrepancyClass.HORIZONLESS_COMMITMENT
    # DOCKET H'S CUT SURVIVES ONTO THE RECORD: one class, two different facts.
    assert candidates[none_declared.prediction_id].horizon_state == "declared_none"
    assert candidates[never_asked.prediction_id].horizon_state == "absent"


def test_3b_both_states_reach_the_written_line(kernel, tmp_path):
    _, predictions, _, _ = kernel
    a = predictions.commit("declared none", resolution_horizon=declared_none())
    b = predictions.commit("never asked")
    loop = _loop(kernel, tmp_path)
    loop.submit_inquiries()
    written = {r["source_record_ids"][0]: r for r in loop.inquiries.inquiries()}
    assert written[a.prediction_id]["horizon_state"] == "declared_none"
    assert written[b.prediction_id]["horizon_state"] == "absent"


# ===========================================================================
# PIN 4 - NO DERIVABLE LICENSE -> DRIFT, NO ADMISSION ATTEMPTED
# ===========================================================================

def test_4_an_unlicensed_candidate_drifts_and_is_never_submitted(kernel, tmp_path):
    obligations, predictions, goals, _ = kernel
    predictions.commit("bare")
    goals.ensure_genesis()          # the real seed roots: linkage fields EMPTY
    loop = _loop(kernel, tmp_path)

    records = loop.submit_inquiries()
    assert len(records) == 1
    assert records[0].partition is CandidatePartition.DRIFT
    assert records[0].drift_basis is DriftBasis.NO_DERIVABLE_LICENSE
    assert records[0].disposition is KernelDisposition.NOT_SUBMITTED
    assert records[0].ancestor_goal_id is None
    # NO ADMISSION WAS ATTEMPTED - the ledger holds nothing.
    assert obligations.read_all() == ()


def test_4b_the_two_joins_license_and_record_which_one(kernel, tmp_path):
    obligations, predictions, goals, _ = kernel
    direct = predictions.commit("licensed directly")
    g1 = _goal_citing(goals, originating=(direct.prediction_id,))
    loop = _loop(kernel, tmp_path)
    candidate = loop.generate_inquiries()[0]
    assert candidate.partition is CandidatePartition.LICENSED
    assert candidate.ancestor_goal_id == g1.goal_id
    assert candidate.license_basis is LicenseBasis.ORIGINATING_RECORD


def test_4c_the_via_claim_join_licenses_too(kernel, tmp_path):
    _, predictions, goals, _ = kernel
    p = predictions.commit("licensed via a shared claim",
                           claim_refs=("CLM-0007",))
    g = _goal_citing(goals, justification=("CLM-0007",))
    candidate = _loop(kernel, tmp_path).generate_inquiries()[0]
    assert candidate.ancestor_goal_id == g.goal_id
    assert candidate.license_basis is LicenseBasis.JUSTIFICATION_CLAIM


def test_4e_the_join_is_exact_equality_never_containment(kernel, tmp_path):
    """RULING 60's DISCIPLINE - found by a SURVIVING MUTANT.

    A goal citing `PRD-00011` must NOT license `PRD-0001`. Nothing pinned this,
    and a containment test passed every other assertion in the file: the ids
    are prefix-shaped, so `"PRD-0001" in "PRD-00011"` is TRUE and a goal about
    one prediction would silently license inquiries about a DIFFERENT one.
    This is the exact failure Ruling 60 res.3 and Ruling 49 both name -
    `Doctrine-0` grazing `Doctrine-0.1`, at a new pair of ids.
    """
    _, predictions, goals, _ = kernel
    for _ in range(11):
        last = predictions.commit("filler")
    assert last.prediction_id == "PRD-0011"
    # A goal that cites the ELEVENTH prediction only.
    _goal_citing(goals, originating=("PRD-00011", "PRD-0011x"))
    by_id = {c.source_record_ids[0]: c for c in
             _loop(kernel, tmp_path).generate_inquiries()}
    # `PRD-0001` must not be licensed by a citation of `PRD-00011`.
    assert by_id["PRD-0001"].partition is CandidatePartition.DRIFT
    assert by_id["PRD-0001"].drift_basis is DriftBasis.NO_DERIVABLE_LICENSE
    # ...and `PRD-0011` is not licensed by `PRD-0011x` either.
    assert by_id["PRD-0011"].partition is CandidatePartition.DRIFT


def test_4f_an_unmapped_kernel_rejection_is_never_guessed(kernel, tmp_path):
    """FOUND BY A SURVIVING MUTANT: nothing exercised the unmapped branch.

    If `RejectionKind` ever gains a member without this act gaining one, the
    honest answer is a loud failure - recording the nearest neighbour would put
    a disposition on a permanent record that the kernel never gave.
    """
    from src.executive.loop import UnmappedKernelDisposition

    class _Unknown:
        admitted = False

        class rejection_kind:
            value = "some_future_kind"

    with pytest.raises(UnmappedKernelDisposition):
        ExecutiveLoop._disposition(_Unknown())


def test_4d_nothing_is_synthesized_when_no_join_holds(kernel, tmp_path):
    """A goal EXISTS but cites nothing - the generator must not reach for it."""
    _, predictions, goals, _ = kernel
    predictions.commit("bare")
    _goal_citing(goals)
    candidate = _loop(kernel, tmp_path).generate_inquiries()[0]
    assert candidate.partition is CandidatePartition.DRIFT
    assert candidate.ancestor_goal_id is None


# ===========================================================================
# PIN 5 - DEPTH CEILING, WITH THE LOOP'S OWN ADMITTED INQUIRY AS THE SOURCE
# ===========================================================================

def test_5_an_inquiry_about_our_own_inquiry_hits_the_depth_ceiling(kernel,
                                                                  tmp_path):
    """THE RECURSION DOOR, closed the day the recursion becomes possible.

    Built through the REAL path: the loop admits an inquiry (so the obligation
    carries the generator's name in `source`), and a later prediction records
    that obligation among its refs. A discrepancy on THAT prediction is an
    inquiry about an inquiry.
    """
    obligations, predictions, goals, _ = kernel
    first = predictions.commit("bare, licensed")
    _goal_citing(goals, originating=(first.prediction_id,))
    loop = _loop(kernel, tmp_path)
    submitted = loop.submit_inquiries()
    assert submitted[0].disposition is KernelDisposition.ADMITTED
    our_obligation = submitted[0].obligation_id

    # A prediction committed while working that inquiry, citing it.
    second = predictions.commit("derived from our own inquiry",
                                claim_refs=(our_obligation,))
    _goal_citing(goals, originating=(second.prediction_id,))

    derived = {c.source_record_ids[0]: c for c in loop.generate_inquiries()}
    depth_2 = derived[second.prediction_id]
    assert depth_2.derivation_depth == 2
    assert depth_2.partition is CandidatePartition.DRIFT
    assert depth_2.drift_basis is DriftBasis.DEPTH_CEILING
    # ...and it is DRIFT despite a licence being derivable - the structural bar
    # is tested before the scope bar.
    assert depth_2.ancestor_goal_id is None
    # The depth-1 candidate beside it is unaffected.
    assert derived[first.prediction_id].derivation_depth == 1


def test_5b_an_obligation_from_another_source_is_not_our_own_inquiry(kernel,
                                                                    tmp_path):
    """Depth keys on OUR authorship, not on obligations in general."""
    obligations, predictions, goals, _ = kernel
    foreign = obligations.admit("aurea_core.collapse", TargetKind.DOCTRINE,
                                "D-1", "someone else's obligation")
    p = predictions.commit("cites a foreign obligation",
                           claim_refs=(foreign.obligation_id,))
    _goal_citing(goals, originating=(p.prediction_id,))
    candidate = _loop(kernel, tmp_path).generate_inquiries()[0]
    assert candidate.derivation_depth == 1
    assert candidate.partition is CandidatePartition.LICENSED


def test_5c_the_ceiling_is_one():
    assert MAX_DERIVATION_DEPTH == 1


# ===========================================================================
# PIN 6 - KERNEL-OWNED DEDUPLICATION
# ===========================================================================

def test_6_two_cycles_submit_twice_and_the_kernel_calls_the_second_a_duplicate(
        kernel, tmp_path):
    """THE EXECUTIVE SUBMITS; THE KERNEL DISPOSITIONS (section 5).

    The generator does not suppress its own repeat - it re-derives the same
    discrepancy and submits again, and the LEDGER's duplicate disposition is
    the answer, recorded as received.
    """
    obligations, predictions, goals, _ = kernel
    p = predictions.commit("bare, licensed")
    _goal_citing(goals, originating=(p.prediction_id,))
    loop = _loop(kernel, tmp_path)

    first = loop.submit_inquiries()
    second = loop.submit_inquiries()

    assert first[0].disposition is KernelDisposition.ADMITTED
    assert second[0].disposition is KernelDisposition.REJECTED_DUPLICATE
    # TWO submissions, TWO act lines - the repeat is recorded, not swallowed.
    assert len(loop.inquiries.inquiries()) == 2
    # The kernel wrote a record for its own rejection too (admission is total).
    kinds = [r.get("record_type") for r in obligations.read_all()]
    assert kinds == ["open", "rejected"]


def test_6b_the_generator_never_reads_its_own_log(kernel, tmp_path):
    """Import- and call-absence. Dedup by self-inspection would be the
    Executive dispositioning, which is the kernel's half of section 5."""
    tree = ast.parse((SRC / "executive" / "inquiry_generator.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, "module", "") or ""
            names = [a.name for a in node.names]
            assert "inquiry_log" not in module
            assert not any("inquiry_log" in n or "InquiryLog" in n for n in names)
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"inquiries", "read_all", "selections"}


def test_6c_the_claim_text_is_derived_so_the_duplicate_check_can_work(kernel,
                                                                     tmp_path):
    """Identical discrepancies produce IDENTICAL text, by construction.

    If the text varied, the kernel's duplicate check would never fire and pin 6
    would be measuring nothing.
    """
    _, predictions, goals, _ = kernel
    p = predictions.commit("bare")
    _goal_citing(goals, originating=(p.prediction_id,))
    loop = _loop(kernel, tmp_path)
    a, b = loop.generate_inquiries()[0], loop.generate_inquiries()[0]
    assert loop._claim_text(a) == loop._claim_text(b)
    assert loop._claim_text(a) == f"horizonless_commitment: {p.prediction_id}"


# ===========================================================================
# PIN 7 - NO SOVEREIGN GOALS
# ===========================================================================

def test_7_no_goal_ledger_write_path_in_either_module():
    for name in ("inquiry_generator.py", "inquiry_log.py"):
        source = (SRC / "executive" / name).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                assert "goal_ledger" not in module, name
            if isinstance(node, ast.Attribute):
                assert node.attr not in {"commit", "_commit", "ensure_genesis",
                                         "resolve", "record_evidence"}, name


def test_7b_the_loop_never_commits_a_goal():
    tree = ast.parse((SRC / "executive" / "loop.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            assert "goal_ledger" not in (getattr(node, "module", "") or "")
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"ensure_genesis", "_commit"}


# ===========================================================================
# PIN 8 - THE WRITE GATES THE ACT, BOTH LEGS
# ===========================================================================

def test_8_a_failed_log_write_gates_the_act(kernel, tmp_path, monkeypatch):
    _, predictions, _, _ = kernel
    predictions.commit("bare")
    loop = _loop(kernel, tmp_path)

    def _boom(*a, **k):
        raise OSError("disk gone")

    monkeypatch.setattr("src.executive.inquiry_log.durable_append_text", _boom)
    with pytest.raises(OSError):
        loop.submit_inquiries()
    assert loop.inquiries.entries == []


def test_8b_an_underived_mint_refuses_and_never_falls_back(kernel, tmp_path,
                                                           monkeypatch):
    _, predictions, _, _ = kernel
    predictions.commit("bare")
    loop = _loop(kernel, tmp_path)
    loop.submit_inquiries()
    monkeypatch.setattr("src.executive.inquiry_log.derive_max_ordinal",
                        lambda *a, **k: None)
    with pytest.raises(InquiryLogUnreadable):
        loop.submit_inquiries()
    assert len(loop.inquiries.inquiries()) == 1


def test_8c_an_unreadable_log_refuses_typed(kernel, tmp_path, monkeypatch):
    _, predictions, _, _ = kernel
    predictions.commit("bare")
    loop = _loop(kernel, tmp_path)
    loop.submit_inquiries()
    real_open = open

    def _refuse(path, *a, **k):
        if str(path).endswith("inq.jsonl"):
            raise OSError("unreadable")
        return real_open(path, *a, **k)

    monkeypatch.setattr("builtins.open", _refuse)
    with pytest.raises(InquiryLogUnreadable):
        loop.inquiries.inquiries()


def test_8d_every_candidate_is_recorded_the_third_outcome_is_unreachable(
        kernel, tmp_path):
    """THE ONE FORBIDDEN OUTCOME: neither admitted nor recorded."""
    obligations, predictions, goals, _ = kernel
    licensed = predictions.commit("licensed")
    _goal_citing(goals, originating=(licensed.prediction_id,))
    predictions.commit("unlicensed")
    loop = _loop(kernel, tmp_path)

    candidates = loop.generate_inquiries()
    records = loop.submit_inquiries()
    assert len(candidates) == len(records) == 2
    assert len(loop.inquiries.inquiries()) == 2
    partitions = {r.partition for r in records}
    assert partitions == {CandidatePartition.LICENSED, CandidatePartition.DRIFT}


# ===========================================================================
# PIN 9 - v-a AND v-b BYTE-UNMODIFIED
# ===========================================================================

# Recorded at M7-c. These files carry the M7-a and M7-b pins, and the
# specification requires them to pass UNMODIFIED - so their bytes are pinned
# rather than their behaviour trusted. A change here is a STOP, not a rebase.
_FROZEN_TEST_FILES = {
    "tests/test_m7a_executive_loop.py":
        "c7867cd28cf7d76d64683024a2c86335ec0f27bc3676e9467ef615523adc58fe",
    "tests/test_m7b_attention_policy.py":
        "5ea92b1f5ef9c278499151705ad2fc1180522665fda9b0e5f0c07544ad8bf700",
}


def test_9_the_v_a_and_v_b_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN_TEST_FILES.items():
        actual = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
        assert actual == expected, (
            f"{path} changed. M7-c's specification requires the v-a and v-b "
            f"pin files to pass BYTE-UNMODIFIED; if a ruling moved one of "
            f"their properties, that is a migration and this hash moves WITH "
            f"the ruling that ordered it - never to make a suite green.")


# ===========================================================================
# PIN 10 - NO THRESHOLDS, NO MAGNITUDES, NO CLOCK READS
# ===========================================================================

FORBIDDEN_IN_GENERATOR = (
    "random", "secrets", "numpy", "datetime", "time", "pathlib", "os", "json",
    "src.filtration", "src.goals", "src.external", "src.doctrine",
    "src.utils", "src.executive.loop", "src.executive.inquiry_log",
)


def test_10_the_generator_imports_nothing_it_could_read_draw_or_time_with():
    tree = ast.parse((SRC / "executive" / "inquiry_generator.py").read_text(
        encoding="utf-8"))
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            seen.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                seen.add(node.module)
    for name in seen:
        for bad in FORBIDDEN_IN_GENERATOR:
            assert not (name == bad or name.startswith(bad + ".")), name


def test_10b_the_only_numeric_literals_are_the_depth_hops():
    """No threshold, no window, no grace period. §9 bar #5 at a new surface.

    The integers this module may hold are the DEPTH HOPS (1 and 2) and nothing
    else - and a depth hop is a count of derivations, not a magnitude selecting
    a behaviour from a range.
    """
    tree = ast.parse((SRC / "executive" / "inquiry_generator.py").read_text(
        encoding="utf-8"))
    # AN INDEX IS NOT A MAGNITUDE, and the distinction is declared rather than
    # absorbed: `direct[0]` selects the first of a sorted list, it does not
    # select a behaviour from a numeric range. The first draft of this pin
    # counted subscripts and flagged `0`, which would have pushed the allowed
    # set wider than the property deserves - so the SCANNER was sharpened and
    # the bound left tight, rather than the reverse.
    indices = {id(n.slice) for n in ast.walk(tree)
               if isinstance(n, ast.Subscript)}
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)
                and not isinstance(n.value, bool) and id(n) not in indices}
    assert literals <= {1, 2}, literals


def test_10c_overdue_is_ordinal_versus_ordinal_only(kernel, tmp_path):
    """Both sides of the comparison are RECORDED points on one clock."""
    obligations, predictions, _, _ = kernel
    p = predictions.commit("overdue", resolution_horizon=provided("SEQ-000002"))
    _advance_clock(obligations, steps=1)
    facts = _loop(kernel, tmp_path).observe().inquiry
    # BOTH SIDES ARE RECORDED POINTS: the horizon's own token, and the furthest
    # ordinal the obligation ledger has minted. Neither is a wall-clock read.
    assert facts.predictions[0].horizon_ordinal == 2
    assert facts.max_seq_ordinal == 1
    # 2 > 1, so the horizon has NOT passed and nothing fires - the comparison
    # is the whole mechanism, with no window and no grace period around it.
    assert _loop(kernel, tmp_path).generate_inquiries() == ()


# ===========================================================================
# PIN 11 - THE `UNCHECKED` REFUSAL, BOTH DIRECTIONS
# ===========================================================================

def test_11a_resolver_present_admits_a_checked_target(tmp_path):
    predictions = PredictionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    p = predictions.commit("a real prediction")
    led = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           prediction_ledger=predictions)
    result = led.admit(GENERATOR_NAME, TargetKind.PREDICTION,
                       p.prediction_id, "when does it resolve")
    assert result.admitted
    assert result.target_resolution is TargetResolution.RESOLVED


def test_11b_resolver_absent_refuses_and_writes_nothing(tmp_path):
    """THE TRAP MEASURED AT `e1f8612`, CLOSED. Never a green UNCHECKED write."""
    led = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"))
    with pytest.raises(UncheckableTarget):
        led.admit(GENERATOR_NAME, TargetKind.PREDICTION, "PRD-0001", "x")
    assert led.read_all() == ()
    assert not (tmp_path / "o.jsonl").exists()


def test_11c_the_refusal_is_scoped_to_prediction_targets_only(tmp_path):
    """The other four keep their legitimate UNCHECKED admissions.

    Widening this refusal would break every caller that admits about a
    structure it did not wire a resolver for, which the third state exists to
    record honestly.
    """
    led = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"))
    for kind in (TargetKind.DOCTRINE, TargetKind.SCAR, TargetKind.SUSPENSION,
                 TargetKind.CLAIM, TargetKind.WORLD_PROPOSITION):
        result = led.admit("someone", kind, "X-1", f"about {kind.value}")
        assert result.admitted
        assert result.target_resolution is TargetResolution.UNCHECKED


# ===========================================================================
# PIN 12 - FABRICATION REJECTION (the fires-control for the new member)
# ===========================================================================

def test_12_a_nonexistent_prediction_id_is_rejected_targetless(tmp_path):
    predictions = PredictionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    predictions.commit("a real one")
    led = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           prediction_ledger=predictions)
    result = led.admit(GENERATOR_NAME, TargetKind.PREDICTION, "PRD-9999",
                       "about a prediction that does not exist")
    assert not result.admitted
    assert result.rejection_kind.value == "targetless"
    assert result.target_resolution is TargetResolution.UNRESOLVED
    # ADMISSION IS TOTAL: the refusal still left a record.
    assert [r["record_type"] for r in led.read_all()] == ["rejected"]


# ===========================================================================
# PIN 13 - THE WIDENING IS ENTRY-BOUND
# ===========================================================================

def test_13_the_vocabulary_is_exactly_the_ruled_set():
    assert {m.value for m in TargetKind} == {
        "doctrine", "scar", "suspension", "claim", "world_proposition",
        "prediction"}


def test_13b_a_member_beyond_the_ruled_set_is_still_unwritable(tmp_path):
    """The closed-vocabulary guard is UNTOUCHED - the NEXT widening also has to
    arrive by manifest entry, never by a caller's string."""
    led = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"))
    result = led.admit("someone", "episode", "EPI-0001", "not a member")
    assert not result.admitted
    assert result.rejection_kind.value == "malformed"


# ===========================================================================
# IDENTITY AND SHAPE
# ===========================================================================

def test_generator_identity_is_data():
    assert GENERATOR_NAME == "inquiry-generator.v1"
    with pytest.raises(GeneratorIdentityMismatch):
        InquiryGenerator(name="inquiry-generator.v2")
    with pytest.raises(GeneratorIdentityMismatch):
        InquiryGenerator(version="2")


def test_the_partition_is_exclusive_and_a_record_cannot_contradict_itself():
    from src.executive.inquiry_generator import InquiryCandidate
    with pytest.raises(ValueError):
        InquiryCandidate(
            discrepancy_class=DiscrepancyClass.HORIZONLESS_COMMITMENT,
            source_record_ids=("PRD-0001",),
            partition=CandidatePartition.LICENSED, derivation_depth=1,
            ancestor_goal_id="GLC-0001", license_basis=LicenseBasis.ORIGINATING_RECORD,
            drift_basis=DriftBasis.DEPTH_CEILING)
    with pytest.raises(ValueError):
        InquiryCandidate(
            discrepancy_class=DiscrepancyClass.HORIZONLESS_COMMITMENT,
            source_record_ids=("PRD-0001",),
            partition=CandidatePartition.DRIFT, derivation_depth=1)


def test_generation_is_pure_and_writes_nothing(kernel, tmp_path):
    _, predictions, goals, _ = kernel
    p = predictions.commit("licensed")
    _goal_citing(goals, originating=(p.prediction_id,))
    loop = _loop(kernel, tmp_path)
    for _ in range(5):
        loop.generate_inquiries()
    assert loop.inquiries.inquiries() == ()
    assert loop.obligations.read_all() == ()


def test_the_gate_one_triple_is_answered_on_both_partitions(kernel, tmp_path):
    obligations, predictions, goals, _ = kernel
    licensed = predictions.commit("licensed")
    _goal_citing(goals, originating=(licensed.prediction_id,))
    predictions.commit("unlicensed")
    loop = _loop(kernel, tmp_path)
    loop.submit_inquiries()

    rows = {r["partition"]: r["gate_one"] for r in loop.inquiries.inquiries()}
    assert rows["licensed"] == {
        "pressure_class_applied": "not_applicable",
        "unexercised_defeaters": "not_applicable",
        "rejection_reason": "not_applicable"}
    # A DRIFT finding is disposition-like: the basis IS the rejection reason.
    assert rows["drift"]["rejection_reason"] == "no_derivable_license"


def test_the_inquiry_log_has_no_update_or_delete_surface():
    tree = ast.parse((SRC / "executive" / "inquiry_log.py").read_text(
        encoding="utf-8"))
    methods = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for forbidden in ("update", "amend", "revise", "delete", "remove", "clear",
                      "purge", "truncate", "rewrite"):
        assert forbidden not in methods


def test_nothing_in_src_consumes_the_inquiry_log_but_the_loop():
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "inquiry_log.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module \
                    and "inquiry_log" in node.module:
                consumers.append(path.as_posix().replace("\\", "/"))
    assert sorted(set(consumers)) == ["src/executive/loop.py"], consumers
