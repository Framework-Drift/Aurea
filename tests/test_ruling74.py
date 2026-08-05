"""
test_ruling74.py - RULING 74 / DOCKET Q item Q3: THE ACTIVATION LAYER.

    An activation that was not BOUNDED before its attention is not an
    activation.

THE RED-FIRST WATCH IS A COLLECTION ERROR, AND IT IS STATED AS ONE (Rulings
61 / 63 / 70's precedent): `src/goals/goal_activation.py` did not exist at
`e601a3e`, so every pin below fails to IMPORT there rather than failing to
ASSERT. Unlike Ruling 60 there is no independent half to witness. **The mutation
slate carries this pass's verification weight**, and the migrated pins in
`test_ruling72.py` / `test_ruling73.py` / `test_ruling69.py` are the half that
did watch meaningfully - each was written against an earlier state and each
fired when this wiring landed.

WHERE THE REST OF THIS RULING'S PINS LIVE:
  * `tests/test_ruling69.py` - the shared mint's FOURTH consumer inherits the
    whole battery at the `ACT-` prefix (interleave, absent counter, typed
    refusal, torn line, mutex, recovery).
  * `tests/test_ruling72.py` - the goal ledger's consumer set, migrated a
    SECOND time to the ruled three.
  * `tests/test_ruling73.py` - the arbiter's consumer set, migrated from empty
    to the ruled two.
"""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.goals.goal_activation import (ActivationClose, ActivationLayer,
                                       ActivationLogUnreadable, BoundKind,
                                       GoalActivation, StopCondition,
                                       UnboundedActivation,
                                       UnproducibleStopCondition,
                                       UNPRODUCIBLE_STOPS)
from src.goals.goal_arbitration import GoalArbiter, GoalExamination
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalOutcome, GoalProvenance,
                                   UnproducibleGoalKind, declared)

REPO = Path(__file__).resolve().parents[1]
MODULE = "src/goals/goal_activation.py"


def _tree():
    return ast.parse((REPO / MODULE).read_text(encoding="utf-8"))


def _stack(tmp_path, goals=2):
    """A ledger + arbiter + layer over isolated paths, with `goals` standing."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "goals.jsonl"))
    for index in range(goals):
        ledger.commit(desired_state=f"direction {index}",
                      kind=GoalKind.RESEARCH, level=GoalLevel.PROJECT,
                      provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                      asserter="tester",
                      completion_criteria=declared(f"criterion {index}"))
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "exams.jsonl"))
    layer = ActivationLayer(arbiter, log_path=str(tmp_path / "acts.jsonl"))
    return ledger, arbiter, layer


# =====================================================================
# (a) OPEN AND CLOSE ARE SEPARATE APPENDS; STATUS IS DERIVED
# =====================================================================

def test_a_open_and_close_are_two_separate_lines(tmp_path):
    """PIN (a). res.2 - the structural heart, measured ON THE BYTES.

    An in-place update would be indistinguishable, afterwards, from having
    declared the right bound all along.
    """
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 3)

    after_open = Path(layer.log_path).read_text(encoding="utf-8")
    assert len(after_open.strip().splitlines()) == 1

    layer.close_activation(activation.activation_id,
                           StopCondition.CRITERION_EVIDENCE)

    lines = Path(layer.log_path).read_text(
        encoding="utf-8").strip().splitlines()
    assert len(lines) == 2, "close must be a SEPARATE append, never an edit"
    # THE OPEN LINE IS BYTE-IDENTICAL AFTERWARDS.
    assert lines[0] == after_open.strip()
    assert json.loads(lines[0])["kind_of_record"] == "activation"
    assert json.loads(lines[1])["kind_of_record"] == "activation_close"


def test_a_status_is_derived_and_stored_nowhere(tmp_path):
    """PIN (a). L3 - no record carries a status field, and none may."""
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)

    assert layer.is_open(activation.activation_id) is True
    layer.close_activation(activation.activation_id, StopCondition.NO_PROGRESS)
    assert layer.is_open(activation.activation_id) is False

    for record in (GoalActivation, ActivationClose):
        for name in record.__dataclass_fields__:
            assert "status" not in name.lower() and name.lower() != "open", (
                f"{record.__name__}.{name} stores a derived status")
    for line in Path(layer.log_path).read_text(
            encoding="utf-8").strip().splitlines():
        payload = json.loads(line)
        assert not any("status" in key.lower() for key in payload)


def test_a_a_crashed_process_leaves_a_derivably_open_activation(tmp_path):
    """PIN (a). **CRASH HONESTY IS THE DERIVATION WORKING, NOT A REPAIR CASE.**

    A process that dies mid-episode leaves an open line and no close line. A
    FRESH instance - which is what a restarted AUREA has - must read that as
    OPEN, because that is what it was. Nothing detects, reconciles or cleans up.
    """
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.PROGRESS_BOUND, 2)

    # The process dies here. A new one constructs everything afresh.
    _, arbiter2, layer2 = _stack(tmp_path)
    assert layer2.entries == [], "the in-memory mirror must not survive"
    assert layer2.is_open(activation.activation_id) is True
    assert [a.activation_id for a in layer2.open_activations()] == \
        [activation.activation_id]
    reread = layer2.activation_for(activation.activation_id)
    assert reread.bound_kind is BoundKind.PROGRESS_BOUND
    assert reread.bound_magnitude == 2


def test_a_an_unknown_activation_has_no_derivable_status(tmp_path):
    _, _, layer = _stack(tmp_path)
    with pytest.raises(ValueError, match="ACT-9999"):
        layer.is_open("ACT-9999")


# =====================================================================
# (b) THE REFUSALS - res.4 and res.5, each witnessed with its typed raise
# =====================================================================

def test_b_an_unbounded_open_is_refused(tmp_path):
    """PIN (b). **AN UNBOUNDED ACTIVATION IS THE COMPULSION SHAPE QL5
    REFUSES**, so the refusal has its own type."""
    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    with pytest.raises(UnboundedActivation, match="bound_magnitude"):
        layer.open_activation(examination, BoundKind.EXAMINATION_BOUND, None)


@pytest.mark.parametrize("magnitude", [0, -1, -99])
def test_b_a_non_positive_bound_is_refused(tmp_path, magnitude):
    """PIN (b). A bound already met at open, or never met, is not a bound."""
    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    with pytest.raises(UnboundedActivation, match="positive"):
        layer.open_activation(examination, BoundKind.EXAMINATION_BOUND,
                              magnitude)


def test_b_a_boolean_magnitude_is_refused(tmp_path):
    """PIN (b). `bool` is an `int` subclass, so `True` would silently mean
    'one further examination' - a magnitude nobody declared."""
    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    with pytest.raises(UnboundedActivation, match="bool"):
        layer.open_activation(examination, BoundKind.EXAMINATION_BOUND, True)


def test_b_an_unknown_bound_kind_is_refused(tmp_path):
    """PIN (b). The vocabulary is CLOSED; a raw string would let a caller
    invent a bound class."""
    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    with pytest.raises(UnboundedActivation, match="BoundKind"):
        layer.open_activation(examination, "examination_bound", 3)


def test_b_a_second_open_for_one_goal_is_refused(tmp_path):
    """PIN (b). **SERIAL ATTENTION.** Two open episodes against one commitment
    make 'how long has this been attended, and under what bound' unanswerable -
    the one question the log exists to answer."""
    _, arbiter, layer = _stack(tmp_path, goals=1)
    first = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 5)

    with pytest.raises(ValueError, match="already has an open activation"):
        layer.open_activation(arbiter.examine(),
                              BoundKind.EXAMINATION_BOUND, 5)

    # AND IT LIFTS ONCE THE EPISODE CLOSES - the guard is SERIAL, not ONE-SHOT.
    layer.close_activation(first.activation_id, StopCondition.NO_PROGRESS)
    second = layer.open_activation(arbiter.examine(),
                                   BoundKind.EXAMINATION_BOUND, 5)
    assert second.activation_id != first.activation_id
    assert second.goal_id == first.goal_id


def test_b_one_examination_authorizes_at_most_one_activation(tmp_path):
    """PIN (b). Re-using an examination would let ONE selection justify
    unbounded re-entry - the bound defeated not by raising it but by opening
    again. Driven on a CLOSED activation so the serial guard cannot be what
    fires."""
    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    activation = layer.open_activation(
        examination, BoundKind.EXAMINATION_BOUND, 1)
    layer.close_activation(activation.activation_id,
                           StopCondition.BOUND_REACHED)

    with pytest.raises(ValueError, match="already authorized"):
        layer.open_activation(examination, BoundKind.EXAMINATION_BOUND, 1)


def test_b_a_second_close_is_refused(tmp_path):
    """PIN (b). Ruling 61's second-resolution form: an episode ends ONCE."""
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    layer.close_activation(activation.activation_id,
                           StopCondition.BOUND_REACHED)

    with pytest.raises(ValueError, match="already closed"):
        layer.close_activation(activation.activation_id,
                               StopCondition.NO_PROGRESS)
    assert len(Path(layer.log_path).read_text(
        encoding="utf-8").strip().splitlines()) == 2


def test_b_closing_an_unknown_activation_is_refused(tmp_path):
    _, _, layer = _stack(tmp_path)
    with pytest.raises(ValueError, match="no activation"):
        layer.close_activation("ACT-4242", StopCondition.NO_PROGRESS)


def test_b_authority_denial_is_refused_as_unproducible(tmp_path):
    """PIN (b). res.3 - **VACUOUS BY SUBSTRATE.** No authorization surface
    exists that could deny, so nothing could honestly have produced this stop.

    The member STAYS (Ruling 63's `OBSERVED` precedent) so the vocabulary is
    closed NOW and the barrier lifts BY RULING, and the refusal NAMES its
    reopening condition.
    """
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)

    with pytest.raises(UnproducibleStopCondition,
                       match="authorization surface"):
        layer.close_activation(activation.activation_id,
                               StopCondition.AUTHORITY_DENIAL)
    assert layer.is_open(activation.activation_id) is True
    assert StopCondition.AUTHORITY_DENIAL in UNPRODUCIBLE_STOPS


def test_b_the_vocabulary_refusal_precedes_the_unknown_id_refusal(tmp_path):
    """PIN (b). Ruling 51's form - AN ENGINE FACT PRECEDES A REQUEST FACT.

    That a stop has no substrate is permanently true of the tree; that an id is
    unknown is true of one call. The caller gets the answer that will still be
    true tomorrow.
    """
    _, _, layer = _stack(tmp_path)
    with pytest.raises(UnproducibleStopCondition):
        layer.close_activation("ACT-NOPE", StopCondition.AUTHORITY_DENIAL)


def test_b_a_non_examination_cannot_open_anything(tmp_path):
    """PIN (b) / res.5. **THE TYPE GATE IS THE AUTHORIZATION.** There is no
    path that opens on a bare goal id, because that path would let attention be
    directed by something other than the deterministic selector."""
    _, _, layer = _stack(tmp_path)
    for bad in ("GLC-0001", None, 7, {"selected_goal_id": "GLC-0001"}):
        with pytest.raises(TypeError, match="GoalExamination"):
            layer.open_activation(bad, BoundKind.EXAMINATION_BOUND, 1)
    assert not Path(layer.log_path).exists(), (
        "a refused open created the log file")


def test_b_every_refusal_precedes_the_mint_and_writes_nothing(tmp_path):
    """PIN (b). Ruling 24's pre-flight boundary as Ruling 46 read it: **a
    refused open spends NO ORDINAL, writes NO LINE, creates NO FILE.**

    Asserting only the raise would pass against an implementation that refuses
    after minting - which is exactly the defect Ruling 46 was written about.
    """
    _, arbiter, layer = _stack(tmp_path)
    good = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    assert good.activation_id == "ACT-0001"
    before = Path(layer.log_path).read_bytes()

    examination = arbiter.examine()
    for kind, magnitude, error in (
            (BoundKind.EXAMINATION_BOUND, 0, UnboundedActivation),
            (BoundKind.EXAMINATION_BOUND, None, UnboundedActivation),
            ("nope", 1, UnboundedActivation)):
        with pytest.raises(error):
            layer.open_activation(examination, kind, magnitude)
    assert Path(layer.log_path).read_bytes() == before

    # THE ORDINAL WAS NOT BURNT: the next real open is ACT-0002, not ACT-0005.
    assert layer.open_activation(
        examination, BoundKind.EXAMINATION_BOUND, 1).activation_id == "ACT-0002"


def test_b_the_record_type_itself_refuses_an_unbounded_construction():
    """PIN (b). **RULING 46'S KEPT BACKSTOP, with its own contribution.**

    `_validate_bound` runs in `open_activation` before the mint AND again in
    `__post_init__`. The second is not redundant: the frozen record is what
    reaches disk and what pins read, so a type that can be hand-constructed
    unbounded is a type whose invariant lives in one function's discipline.
    """
    for kind, magnitude in ((BoundKind.EXAMINATION_BOUND, 0),
                            (BoundKind.PROGRESS_BOUND, -3),
                            ("examination_bound", 1),
                            (BoundKind.EXAMINATION_BOUND, True)):
        with pytest.raises(UnboundedActivation):
            GoalActivation(activation_id="ACT-0001", goal_id="GLC-0001",
                           examination_id="EXM-0001", bound_kind=kind,
                           bound_magnitude=magnitude)


# =====================================================================
# (c) THE BOUND, DERIVED - both kinds, on constructed sequences
# =====================================================================

def test_c_examination_bound_counts_only_further_examinations(tmp_path):
    """PIN (c). The AUTHORIZING examination is NOT counted - it is what opened
    the episode, not attention paid during it. Counting it would make a bound
    of N behave as N-1 for every activation ever opened."""
    _, arbiter, layer = _stack(tmp_path, goals=1)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 2)

    assert layer.bound_met(activation) is False, "the authorizer was counted"
    arbiter.examine()
    assert layer.bound_met(activation) is False, "off by one: met at N-1"
    arbiter.examine()
    assert layer.bound_met(activation) is True
    arbiter.examine()
    assert layer.bound_met(activation) is True, "must stay met"


def test_c_examination_bound_ignores_examinations_of_other_goals(tmp_path):
    """PIN (c). The bound is attention paid to THIS goal. With two roots,
    Ruling 73-A's rotation alternates, so half the examinations belong to the
    other commitment and must not count."""
    _, arbiter, layer = _stack(tmp_path, goals=2)
    first = arbiter.examine()
    activation = layer.open_activation(
        first, BoundKind.EXAMINATION_BOUND, 1)

    other = arbiter.examine()
    assert other.selected_goal_id != activation.goal_id
    assert layer.bound_met(activation) is False, (
        "another goal's examination was counted")

    mine = arbiter.examine()
    assert mine.selected_goal_id == activation.goal_id
    assert layer.bound_met(activation) is True


def test_c_progress_bound_consumes_focus_persistence(tmp_path):
    """PIN (c). res.3 registers `focus_persistence` as the substrate, and this
    drives it end to end: K consecutive no-progress examinations meets the
    bound, and evidence landing un-meets it."""
    ledger, arbiter, layer = _stack(tmp_path, goals=1)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.PROGRESS_BOUND, 3)

    assert arbiter.focus_persistence(activation.goal_id).consecutive_selections == 1
    assert layer.bound_met(activation) is False
    arbiter.examine()
    assert layer.bound_met(activation) is False
    arbiter.examine()
    persistence = arbiter.focus_persistence(activation.goal_id)
    assert persistence.consecutive_selections == 3
    assert persistence.progress_recorded is False
    assert layer.bound_met(activation) is True


def test_c_progress_resets_the_progress_bound_to_zero(tmp_path):
    """PIN (c). **PROGRESS RESETS THE ANSWER**, rather than merely failing the
    comparison: a goal that received evidence during its run MOVED, and
    reporting a long unproductive run for it would be false."""
    ledger, arbiter, layer = _stack(tmp_path, goals=1)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.PROGRESS_BOUND, 2)
    arbiter.examine()
    assert layer.bound_met(activation) is True

    ledger.record_evidence(activation.goal_id, note="something moved")
    assert arbiter.focus_persistence(activation.goal_id).progress_recorded is True
    assert layer.bound_met(activation) is False, (
        "a goal that moved still reported an unproductive run")
    assert layer._no_progress_run(activation) == 0


def test_c_an_unmeasurable_bound_reports_false_and_leaves_it_open(tmp_path):
    """PIN (c). The conservative direction is the LEGIBLE one: an activation
    that stays open is on the record and closeable by another stop, whereas one
    reporting its bound met would invite a close nothing supports."""
    _, arbiter, layer = _stack(tmp_path)
    orphan = GoalActivation(activation_id="ACT-0001", goal_id="GLC-0001",
                            examination_id="EXM-NEVER-RECORDED",
                            bound_kind=BoundKind.EXAMINATION_BOUND,
                            bound_magnitude=1)
    arbiter.examine()
    arbiter.examine()
    assert layer._further_examinations(orphan) == 0
    assert layer.bound_met(orphan) is False


def test_c_bound_met_reports_and_closes_nothing(tmp_path):
    """PIN (c). §9's standing bar at the one layer where crossing it would feel
    most natural. A met bound changes NOTHING - a caller records the close."""
    _, arbiter, layer = _stack(tmp_path, goals=1)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    arbiter.examine()

    before = Path(layer.log_path).read_bytes()
    assert layer.bound_met(activation) is True
    assert Path(layer.log_path).read_bytes() == before
    assert layer.is_open(activation.activation_id) is True


def test_c_the_bound_derivation_holds_no_numeric_literal():
    """PIN (c) / res.4 / res.8. **THE MODULE COINS NO THRESHOLD.** The only
    magnitude in the comparison is the one the opener declared and the record
    carries; a literal here would be a coined bound at the exact place attention
    gets its limit."""
    tree = _tree()
    functions = {n.name: n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef)}
    derivations = ("bound_met", "_further_examinations", "_no_progress_run")

    # A THRESHOLD IS A LITERAL ON ONE SIDE OF A COMPARISON, IN THE CODE THAT
    # DECIDES WHETHER A BOUND IS MET. Anything numeric there is a cutoff nobody
    # declared.
    for name in derivations:
        for node in ast.walk(functions[name]):
            if not isinstance(node, ast.Compare):
                continue
            operands = [node.left] + list(node.comparators)
            offenders = [o.value for o in operands
                         if isinstance(o, ast.Constant)
                         and isinstance(o.value, (int, float))
                         and not isinstance(o.value, bool)]
            assert offenders == [], (
                f"{name} compares a numeric literal at line {node.lineno}: "
                f"`{ast.unparse(node)}` - that is a coined threshold")

    # **ONE COMPARISON IS DECLARED OUT, AND IT IS NAMED RATHER THAN SKIPPED**
    # (Batch 66's `_DECLARED_OUT` form). `_validate_bound`'s `bound_magnitude
    # <= 0` is a DOMAIN CHECK on caller-supplied data, not a threshold: it says
    # a non-positive number is not a magnitude at all, which is the refusal that
    # makes an unbounded activation unexecutable. It decides nothing about
    # whether a bound is MET, so it is barred from the derivations above and
    # required here - and the pin asserts it is still present, because deleting
    # it is exactly the mutation res.4 exists to stop.
    positivity = [ast.unparse(n) for n in ast.walk(functions["_validate_bound"])
                  if isinstance(n, ast.Compare)]
    assert "bound_magnitude <= 0" in positivity, (
        "the positivity guard vanished - a non-positive bound is either already "
        "met at open or never met, and neither is a bound")

    # AND THE DERIVATION CARRIES ONLY STRUCTURAL LITERALS: `0` starts an empty
    # tally, `1` steps it. Neither is a magnitude - they are how counting works.
    # A float would be a magnitude in ANY position, so none is allowed.
    for name in derivations:
        literals = [n.value for n in ast.walk(functions[name])
                    if isinstance(n, ast.Constant)
                    and isinstance(n.value, (int, float))
                    and not isinstance(n.value, bool)]
        assert all(value in (0, 1) for value in literals), (
            f"{name} carries a coined magnitude: {literals}")
        assert not any(isinstance(value, float) for value in literals), name


def test_c_no_module_constant_is_a_default_bound():
    """PIN (c). res.4 - there is NO default bound anywhere, so a caller cannot
    open one by omission."""
    signature = inspect.signature(ActivationLayer.open_activation)
    for name in ("bound_kind", "bound_magnitude"):
        assert signature.parameters[name].default is inspect.Parameter.empty, (
            f"{name} acquired a default - a default bound is a magnitude AUREA "
            f"coined for herself")

    module_numbers = [t.id for n in ast.walk(_tree())
                      if isinstance(n, ast.Assign)
                      for t in n.targets
                      if isinstance(t, ast.Name) and t.id.isupper()
                      and isinstance(n.value, ast.Constant)
                      and isinstance(n.value.value, (int, float))]
    assert module_numbers == [], f"module-level magnitudes: {module_numbers}"


# =====================================================================
# (d) DETERMINISM - Ruling 71 layer 2
# =====================================================================

def test_d_the_same_examination_and_state_authorize_identically(tmp_path):
    """PIN (d) / res.5. Same examination + same state -> same outcome, twice.

    There is nothing to PERMUTE - the examination IS the selection - so the
    determinism claim is about the authorization being a function of recorded
    state alone.
    """
    outcomes = []
    for run in range(2):
        root = tmp_path / f"run{run}"
        root.mkdir()
        _, arbiter, layer = _stack(root, goals=3)
        examination = arbiter.examine()
        activation = layer.open_activation(
            examination, BoundKind.EXAMINATION_BOUND, 2)
        outcomes.append((examination.selected_goal_id,
                         examination.deciding_basis,
                         activation.activation_id,
                         activation.goal_id,
                         activation.examination_id,
                         activation.bound_kind,
                         activation.bound_magnitude))
    assert outcomes[0] == outcomes[1], f"authorization diverged: {outcomes}"


def test_d_the_goal_is_read_off_the_examination_never_supplied(tmp_path):
    """PIN (d) / res.5. An activation cannot name a goal the selector did not
    select, because the caller never gets to name one."""
    signature = inspect.signature(ActivationLayer.open_activation)
    assert list(signature.parameters) == [
        "self", "examination", "bound_kind", "bound_magnitude"], (
        "open_activation acquired a parameter - a `goal_id` here would be the "
        "bare-goal door res.5 refuses")

    _, arbiter, layer = _stack(tmp_path)
    examination = arbiter.examine()
    activation = layer.open_activation(
        examination, BoundKind.EXAMINATION_BOUND, 1)
    assert activation.goal_id == examination.selected_goal_id


# =====================================================================
# (e) THE COMPOSITION - QL3's kinds are unproducible UPSTREAM
# =====================================================================

def test_e_no_path_reaches_an_activation_for_a_ql3_kind(tmp_path):
    """PIN (e) / res.5. **THE PROPERTY IS PINNED OVER THE COMPOSITION, NOT AS A
    LOCAL GATE** - a guard for an unreachable case is coined machinery, and it
    would also assert that this layer is what stands between her and world
    agency, which it is not.

    The chain: `GoalLedger._commit` refuses the kind, so no such commitment
    exists; so it is never a candidate, never examined, and never activated.
    """
    ledger, arbiter, layer = _stack(tmp_path, goals=1)

    for kind in (GoalKind.EXTERNAL_TASK, GoalKind.CAPABILITY_ACQUISITION):
        with pytest.raises(UnproducibleGoalKind, match="QL3"):
            ledger.commit(desired_state="act on the world", kind=kind,
                          level=GoalLevel.PROJECT,
                          provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                          asserter="tester")

    # The refusal is upstream, so nothing downstream can ever see one.
    assert all(c.kind not in (GoalKind.EXTERNAL_TASK,
                              GoalKind.CAPABILITY_ACQUISITION)
               for c in ledger.commitments())
    assert all(c.kind is GoalKind.RESEARCH for c in arbiter.candidates())
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    assert ledger.commitment_for(activation.goal_id).kind is GoalKind.RESEARCH


def test_e_this_module_defines_no_ql3_guard_of_its_own():
    """PIN (e). The absence is the ruling: no CODE here names either kind.

    **SCANNED BY AST, NOT BY SUBSTRING - THE SEVENTH OCCURRENCE OF THAT DEFECT,
    caught by this pin going red on its own subject.** The first draft searched
    raw source and matched `open_activation`'s DOCSTRING, which legitimately
    explains why no guard exists. Ruling 63's precedent governs: deleting
    correct documentation to satisfy a noisy guard is how a guard earns its
    eventual weakening. The instrument was sharpened; the prose stands.
    """
    tree = _tree()
    identifiers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            identifiers.add(node.name)
    for word in ("EXTERNAL_TASK", "CAPABILITY_ACQUISITION", "GoalKind"):
        assert word not in identifiers, (
            f"`{word}` entered the activation layer's CODE - res.5 rules that "
            f"a guard for an unreachable case is coined machinery")
    assert "GoalKind" not in _imported_tokens(), "the kind vocabulary is imported"

    # THE PROSE MUST SURVIVE: the module explains why the guard is absent, and
    # that explanation is what stops a later pass adding one.
    assert "EXTERNAL_TASK" in (REPO / MODULE).read_text(encoding="utf-8"), (
        "the explanation of why no QL3 guard exists was deleted to satisfy a "
        "scanner")


def test_e_resolved_and_superseded_goals_leave_the_candidate_set(tmp_path):
    """PIN (e). Candidacy is DERIVED upstream, so a resolved goal cannot be
    activated - checked here because this is the layer that would notice."""
    ledger, arbiter, layer = _stack(tmp_path, goals=2)
    first = arbiter.examine().selected_goal_id
    ledger.resolve(first, GoalOutcome.COMPLETED, "completion_criteria")
    assert first not in [c.goal_id for c in arbiter.candidates()]

    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    assert activation.goal_id != first


# =====================================================================
# (f) THE MINT AT THE FOURTH PREFIX
# =====================================================================

def test_f_the_mint_and_the_append_happen_inside_the_lock():
    """PIN (f). **DECLARED STRUCTURAL PER RULING 17, AND WRITTEN UP FRONT** -
    the seventieth entry's standing form, applied at drafting rather than after
    a survivor (which is how Rulings 72 and 73 each found it).

    Dropping `with mint_lock(...)` survives every behavioural pin, and it has
    to: the lock guards CONCURRENT mints, and every mint re-derives from the
    file, so a single-threaded run cannot tell a held lock from a missing one.
    The property IS a lexical scope, so source is where it is true or false; a
    threaded probe would be flaky and could pass by luck.
    """
    opener = next(n for n in ast.walk(_tree())
                  if isinstance(n, ast.FunctionDef)
                  and n.name == "open_activation")

    guarded = [w for w in ast.walk(opener) if isinstance(w, ast.With)
               and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id == "mint_lock"
                       for item in w.items
                       for c in ast.walk(item.context_expr))]
    assert guarded, "`open_activation` does not take the mint lock at all"

    calls = {n.func.attr for n in ast.walk(guarded[0])
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "_next_id" in calls, "the MINT happens outside the lock"
    assert "_append" in calls, (
        "the APPEND happens outside the lock - deriving inside it and "
        "appending outside leaves exactly the race Ruling 69 closes")


def test_f_no_cached_ordinal_exists_before_or_after_minting(tmp_path):
    """PIN (f). Ruling 69 res.1 at the fourth prefix - the counter is GONE."""
    _, arbiter, layer = _stack(tmp_path)
    assert not hasattr(layer, "_seq")
    layer.open_activation(arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    assert not hasattr(layer, "_seq")


def test_f_an_unreadable_log_refuses_typed_from_every_door(tmp_path, monkeypatch):
    """PIN (f). **FOUND BY THE SHARED BATTERY, NOT BY DESIGN**, and it is the
    pass's sharpest correction.

    `open_activation`'s guards read the log BEFORE the mint, so an unreadable
    log surfaced a bare `OSError` - Ruling 25's shape, a structural refusal
    wearing a disk hiccup's clothes. Returning `()` instead would have been far
    worse: `is_open` would answer TRUE and the serial guard would wave a second
    episode through - **"I could not look" rendered as "there is nothing
    there".**
    """
    import builtins
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    examination = arbiter.examine()
    real_open, target = builtins.open, str(layer.log_path)

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == target and "r" in mode:
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    for call in (lambda: layer.open_activation(
                     examination, BoundKind.EXAMINATION_BOUND, 1),
                 lambda: layer.close_activation(
                     activation.activation_id, StopCondition.NO_PROGRESS),
                 lambda: layer.is_open(activation.activation_id),
                 lambda: layer.read_all()):
        with pytest.raises(ActivationLogUnreadable):
            call()


def test_f_a_missing_log_is_an_empty_history_not_a_failure(tmp_path):
    """PIN (f). `derive_max_ordinal`'s own two-absences distinction, preserved:
    absence is a first run, not a fault."""
    _, _, layer = _stack(tmp_path)
    assert not Path(layer.log_path).exists()
    assert layer.read_all() == ()
    assert layer.activations() == ()
    assert layer.open_activations() == ()
    assert layer.open_activation_for("GLC-0001") is None


def test_f_an_unknown_bound_kind_on_disk_drops_the_line(tmp_path):
    """PIN (f). Floor semantics: a forensic record outlives its writer, and
    reading an unknown bound as a known one would tell a later reader she was
    held to something she was not."""
    _, arbiter, layer = _stack(tmp_path)
    layer.open_activation(arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1)
    with open(layer.log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "kind_of_record": "activation", "activation_id": "ACT-0002",
            "goal_id": "GLC-0001", "examination_id": "EXM-0002",
            "bound_kind": "eternity_bound", "bound_magnitude": 1}) + "\n")
        handle.write("{ not json at all\n")
    assert [a.activation_id for a in layer.activations()] == ["ACT-0001"]
    # ...AND ITS ORDINAL IS STILL BURNT, never reissued (Ruling 69 res.2).
    assert layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 1
    ).activation_id == "ACT-0003"


# =====================================================================
# (g) THE WIRE - doors, opened only from outside
# =====================================================================

_DOORS = ("examine_goals", "open_goal_activation", "close_goal_activation")


def test_g_the_core_composes_the_three_goal_stores(tmp_path):
    core = AureaCore()
    assert isinstance(core.goal_ledger, GoalLedger)
    assert isinstance(core.goal_arbiter, GoalArbiter)
    assert isinstance(core.goal_activation, ActivationLayer)
    assert core.goal_arbiter.ledger is core.goal_ledger
    assert core.goal_activation.arbiter is core.goal_arbiter
    for door in _DOORS:
        assert callable(getattr(core, door))


def test_g_the_doors_work_end_to_end_when_opened_from_outside():
    """PIN (g). The doors are thin delegations that add no policy."""
    core = AureaCore()
    core.goal_ledger.ensure_genesis()

    examination = core.examine_goals()
    assert isinstance(examination, GoalExamination)
    activation = core.open_goal_activation(
        examination, BoundKind.EXAMINATION_BOUND, 2)
    assert activation.goal_id == examination.selected_goal_id
    assert core.goal_activation.is_open(activation.activation_id) is True

    core.close_goal_activation(activation.activation_id,
                               StopCondition.CRITERION_EVIDENCE,
                               ["GLC-0001"])
    assert core.goal_activation.is_open(activation.activation_id) is False


def test_g_no_internal_caller_invokes_any_activation_verb():
    """PIN (g) / res.6. **NOTHING LOOPS - PINNED AS SHAPE.**

    Scanned by AST over ALL of `src/`, excluding the layer itself and the core's
    own three door BODIES (which exist to delegate). A call from anywhere else -
    or from anywhere inside `process_input` - is a scheduler in embryo.
    """
    verbs = {"open_activation", "close_activation", "examine",
             "examine_goals", "open_goal_activation", "close_goal_activation"}
    offenders = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "goal_activation.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        doors = {n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name in _DOORS}
        inside_doors = {id(n) for door in doors for n in ast.walk(door)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if id(node) in inside_doors:
                continue
            name = getattr(node.func, "attr", None)
            if name in verbs:
                offenders.append(
                    f"{path.relative_to(REPO).as_posix()}:{node.lineno} {name}")
    assert offenders == [], (
        f"an activation verb acquired an internal caller: {offenders}. Every "
        f"verb is externally invoked (QL5); an internal one is a scheduler.")


def test_g_the_internal_caller_scanner_actually_fires():
    """The scanner's own control - Ruling 32's answer to the vacuous pin."""
    def offenders_in(source):
        tree = ast.parse(source)
        doors = {n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name in _DOORS}
        inside = {id(n) for door in doors for n in ast.walk(door)}
        return [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and id(n) not in inside
                and getattr(n.func, "attr", None) in
                {"open_activation", "examine_goals"}]

    assert offenders_in(
        "def process_input(self):\n    self.goal_activation.open_activation(x)\n")
    assert not offenders_in(
        "def examine_goals(self):\n    return self.goal_arbiter.examine()\n")
    assert not offenders_in("def f(self):\n    self.spl.process_input(x)\n")


def test_g_the_core_holds_no_scheduler_for_the_goal_layer():
    """PIN (g) / res.6. No loop, no timer, no thread, no async - the machinery
    a scheduler would need is not in the file."""
    source = (REPO / "src/aurea_core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.AsyncFunctionDef, ast.Await)), (
            "async machinery entered the core")
    forbidden = {"threading", "asyncio", "sched", "signal", "timer",
                 "schedule", "apscheduler"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.update(node.module.split("."))
    assert not (imported & forbidden), f"scheduler machinery: {imported & forbidden}"


def test_g_constructing_a_core_writes_no_goal_line(tmp_path):
    """PIN (g). **COMPOSING A LAYER IS NOT INVOKING ONE**, and genesis is NOT
    called from the constructor (Ruling 72's reasoning, first really tested
    here): an incidental `AureaCore()` must not found two permanent roots."""
    core = AureaCore()
    assert not Path(core.goal_ledger.ledger_path).exists()
    assert not Path(core.goal_arbiter.log_path).exists()
    assert not Path(core.goal_activation.log_path).exists()
    assert core.goal_ledger.read_all() == ()
    assert core.goal_activation.read_all() == ()


def test_g_a_full_pipeline_pass_writes_no_goal_line():
    """PIN (g), the BEHAVIORAL half - the soak's claim in miniature.

    `process_input` is the busiest path in the system; if anything were going to
    reach a goal verb by accident it would be here.
    """
    core = AureaCore()
    core.goal_ledger.ensure_genesis()
    before = Path(core.goal_ledger.ledger_path).read_bytes()

    for claim in ("Truth survives collapse.", "Honesty is pointless.",
                  "Fracture Carried is false."):
        core.process_input(claim)

    assert Path(core.goal_ledger.ledger_path).read_bytes() == before
    assert not Path(core.goal_arbiter.log_path).exists()
    assert not Path(core.goal_activation.log_path).exists()
    assert core.goal_activation.activations() == ()


# =====================================================================
# (i) IMPORT ABSENCE, QL4 ABSENCE, AND THE COUNT-NEVER-GATES SCAN
# =====================================================================

FORBIDDEN_IMPORTS = {
    "sae", "SAE", "codex", "Codex", "racm", "RACM", "reflex", "reflex_grid",
    "psi", "PSI", "gsr", "GSR", "hail", "HAIL", "ore", "ORE", "echonet",
    "EchoNet", "tca_core", "tca_integration", "tcaml", "TCAML", "topology",
    "compass", "ril", "RIL", "nova", "NovaEngine", "sbsre", "SBSRE",
    "dee", "DEE", "scar_logic_core", "ScarLogicCore", "black_sphere",
    "random", "secrets", "numpy", "np",
    # THE SEAM VERDICT, as an import-absence pin (res.1).
    "echo_memory", "EchoMemory",
}


def _imported_tokens(rel=MODULE):
    tokens = set()
    for node in ast.walk(ast.parse((REPO / rel).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            for alias in node.names:
                tokens.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                tokens.update(node.module.split("."))
            for alias in node.names:
                tokens.add(alias.name)
    return tokens


def test_i_the_layer_imports_nothing_it_could_command():
    """PIN (i) / res.1. **QL0 AS STRUCTURE** - a goal grants no authority, and
    a bounded episode of attention grants less. Ruling 70's
    enforcement-by-scope, three dockets on."""
    offenders = sorted(_imported_tokens() & FORBIDDEN_IMPORTS)
    assert offenders == [], f"the activation layer imports {offenders}"


def test_i_the_layer_cannot_reach_echo_memory():
    """PIN (i) / res.1. **THE SEAM VERDICT, MADE STRUCTURAL.**

    Five live pressures sit on `EchoMemory`, and an inquiry layer that reached
    for echoes would decide all five in passing, at the moment they were most
    convenient to assume. The wiring ruling owns every one of them; here the
    name is simply not in scope.
    """
    source = (REPO / MODULE).read_text(encoding="utf-8")
    tokens = _imported_tokens()
    assert "echo_memory" not in tokens and "EchoMemory" not in tokens
    tree = _tree()
    identifiers = {getattr(n, "id", None) or getattr(n, "attr", None)
                   for n in ast.walk(tree)
                   if isinstance(n, (ast.Name, ast.Attribute))}
    for word in ("echo_memory", "EchoMemory", "echoes", "retrieve_echo"):
        assert word not in identifiers, f"echo retrieval reached: {word}"
    # The DOCSTRING legitimately explains the absence - the scan is over code.
    assert "EchoMemory" in source, (
        "the seam verdict's explanation was deleted from the docstring")


def test_i_the_import_scanner_actually_fires():
    """Ruling 32's answer to the vacuous-pin problem, and Ruling 70's lesson:
    fed the forbidden shape AND prose, so a scanner that has stopped scanning -
    or one that matches DOCSTRINGS - fails HERE."""
    def tokens_of(source):
        found = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.update(alias.name.split("."))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    found.update(node.module.split("."))
                for alias in node.names:
                    found.add(alias.name)
        return found

    assert tokens_of("from src.expansion.sae import SAE\nimport random\n") \
        & FORBIDDEN_IMPORTS
    assert tokens_of("from src.utils.echo_memory import EchoMemory\n") \
        & FORBIDDEN_IMPORTS
    assert not (tokens_of("from src.utils.ledger_mint import mint_lock\n")
                & FORBIDDEN_IMPORTS)
    # PROSE MUST NOT REGISTER - the substring-scanner defect, sixth occurrence.
    assert not (tokens_of('"""This module never touches EchoMemory or SAE."""')
                & FORBIDDEN_IMPORTS)


def test_i_no_record_carries_a_scalar_standing():
    """PIN (i) / res.8. QL4's absence, shape one of three.

    `bound_magnitude` is DECLARED DATA, not standing - it says how long an
    episode may run, never how much a goal is worth.
    """
    forbidden = {"priority", "confidence", "weight", "score", "rank",
                 "importance", "urgency", "utility", "salience"}
    for record in (GoalActivation, ActivationClose):
        for name in record.__dataclass_fields__:
            assert not any(word in name.lower() for word in forbidden), (
                f"{record.__name__}.{name} is a scalar standing")


def test_i_persisted_lines_carry_exactly_one_number(tmp_path):
    """PIN (i) / res.8. QL4's absence, shape two - measured ON THE BYTES.

    The sibling ledgers pin ZERO numbers; this store legitimately carries the
    DECLARED bound, so the honest pin names it exactly rather than being
    dropped for being inconvenient.
    """
    _, arbiter, layer = _stack(tmp_path)
    activation = layer.open_activation(
        arbiter.examine(), BoundKind.EXAMINATION_BOUND, 4)
    layer.close_activation(activation.activation_id, StopCondition.NO_PROGRESS)

    def numbers(value, path=""):
        found = []
        if isinstance(value, bool):
            return found
        if isinstance(value, (int, float)):
            found.append(path)
        elif isinstance(value, dict):
            for key, item in value.items():
                found += numbers(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                found += numbers(item, f"{path}[{index}]")
        return found

    seen = []
    for line in Path(layer.log_path).read_text(
            encoding="utf-8").strip().splitlines():
        seen += numbers(json.loads(line))
    assert seen == [".bound_magnitude"], f"unexpected numbers on disk: {seen}"


def test_i_the_writer_gate_refuses_a_non_canonical_value(tmp_path):
    """PIN (i), **ADDED AFTER A MUTATION SURVIVOR - THE SAME REAL GAP RULING 72
    FOUND AT ITS OWN WRITER, recurring here for the same reason.**

    Deleting `validate_record_value` from `_append` survived the entire slate,
    because every field is type-checked upstream - `_ids` refuses a non-string,
    the enums refuse a raw value, `_validate_bound` refuses a non-int - so on
    the real paths nothing non-canonical can reach the writer at all.

    **THAT MAKES THE GATE A BACKSTOP, AND A BACKSTOP IS PINNED AT ITS OWN DOOR**
    (Ruling 46's form, where `commit`'s fossil guard was kept after `_preflight`
    duplicated it and pinned independently). Driving it through a real path
    would pass for a NEIGHBOURING guard's reason and witness nothing about this
    one - which is precisely the defect Ruling 72 recorded.

    It earns its place the day a ruling widens what a record carries: the guard
    is already correct rather than remembered.
    """
    from src.utils.record_value import NonCanonicalRecordValue

    _, _, layer = _stack(tmp_path)
    with pytest.raises(NonCanonicalRecordValue, match="activation_entry"):
        layer._append({"kind_of_record": "activation",
                       "evidence_blob": bytearray(b"not canonical")})
    assert not Path(layer.log_path).exists(), (
        "a refused entry created the file - the gate must run BEFORE mkdir "
        "and BEFORE open")


def test_i_the_writer_gate_runs_before_mkdir_and_open():
    """PIN (i). Batch 66's writer discipline as SHAPE: validate, THEN create.
    A gate that runs after `open` has already left a file behind."""
    append = next(n for n in ast.walk(_tree())
                  if isinstance(n, ast.FunctionDef) and n.name == "_append")
    order = []
    for node in ast.walk(append):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr",
                                                             None)
            if name in ("validate_record_value", "mkdir", "open"):
                order.append((node.lineno, name))
    sequence = [name for _, name in sorted(order)]
    assert sequence.index("validate_record_value") < sequence.index("mkdir")
    assert sequence.index("validate_record_value") < sequence.index("open")

    # `allow_nan=False`, and NO `default=` - Ruling 66's second half.
    dumps = [n for n in ast.walk(append) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "dumps"]
    assert len(dumps) == 1
    keywords = {k.arg for k in dumps[0].keywords}
    assert "allow_nan" in keywords, "NaN/Infinity would persist as invalid JSON"
    assert "default" not in keywords, (
        "`default=` silently stringifies a non-canonical leaf into a permanent "
        "record - REFUSAL, NEVER COERCION")


def test_i_no_amend_or_extend_surface_exists():
    """PIN (i) / res.8. QL4's absence, shape three - and QL1's at this layer.

    **THE ABSENCE IS THE ENFORCEMENT.** A method named `extend_bound` with a
    docstring saying "only before the bound is met" would be a request for
    restraint, and this project has hard evidence restraint fails.
    """
    defined = {n.name.lower() for n in ast.walk(_tree())
               if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for word in ("amend", "update", "revise", "retarget", "extend", "rebound",
                 "reopen", "prolong", "renew"):
        assert not any(word in name for name in defined), (
            f"a `{word}` surface appeared; a bound that can be raised once it "
            f"is nearly met is not a bound")


def test_i_the_tally_is_never_compared_to_anything_but_the_declared_bound():
    """PIN (i). **THE COUNT-NEVER-GATES SCAN, EXTENDED TO THIS MODULE**
    (§9 standing bar #5). `focus_persistence`'s tally may be compared to the
    DECLARED bound and to nothing else - a module constant on the other side
    would be AUREA coining her own attention limit."""
    comparisons = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.Compare):
            continue
        rendered = ast.unparse(node)
        if "bound_magnitude" in rendered or "consecutive_selections" in rendered:
            comparisons.append(rendered)
    assert comparisons, "the scan found no bound comparison at all"
    for rendered in comparisons:
        assert "bound_magnitude" in rendered, (
            f"a tally is compared against something other than the declared "
            f"bound: {rendered}")


def test_i_no_stop_condition_is_produced_automatically():
    """PIN (i) / res.3. Nothing DERIVES a stop - a caller records one. A layer
    that closed its own episodes would be a layer that runs."""
    layer_class = next(n for n in ast.walk(_tree())
                       if isinstance(n, ast.ClassDef)
                       and n.name == "ActivationLayer")
    for node in ast.walk(layer_class):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "StopCondition":
                pytest.fail(
                    f"`StopCondition.{node.attr}` is constructed inside the "
                    f"layer - a stop must be the CALLER's recorded act")


# =====================================================================
# (j) ISOLATION, SAME COMMIT
# =====================================================================

def test_j_the_log_path_default_is_under_data_runtime():
    """PIN (j) / Rulings 31 + 39: an `__init__` DEFAULT under `data/runtime/` -
    one of exactly two shapes the isolation fixtures can reach.

    **READ FROM THE SOURCE, NOT FROM THE LIVE SIGNATURE, AND THE FIRST DRAFT
    GOT THAT WRONG IN AN INSTRUCTIVE WAY.** `inspect.signature` here returns the
    fixture's tmp path, because the autouse redirect is active in this very
    test - so the live default proves isolation is working while saying nothing
    about what ships. The SHIPPED default is the thing Ruling 39 rules on.
    """
    tree = ast.parse((REPO / MODULE).read_text(encoding="utf-8"))
    init = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    names = [a.arg for a in init.args.args][-len(init.args.defaults):]
    default = dict(zip(names, init.args.defaults))["log_path"]
    assert isinstance(default, ast.Constant) and isinstance(default.value, str)
    assert default.value.replace("\\", "/").startswith("data/runtime/"), (
        default.value)
    assert default.value.endswith("goal_activations.jsonl")


def test_j_the_activation_log_is_registered_in_both_isolation_tables():
    """PIN (j). Registered in `conftest.py` AND `scripts/soak.py` in the SAME
    COMMIT as the store - Ruling 31's rule. **Both, because the soak's coverage
    self-audit and the suite's fixture are different mechanisms**, and a store
    in one but not the other is isolated in exactly half the places it runs.
    """
    for rel in ("tests/conftest.py", "scripts/soak.py"):
        source = (REPO / rel).read_text(encoding="utf-8")
        assert "ActivationLayer" in source, f"{rel} does not know the layer"
        assert "goal_activations.jsonl" in source, f"{rel} lacks the path"


def test_j_the_fixture_actually_redirects_this_store(tmp_path):
    """PIN (j), the BEHAVIORAL half - the registration is real, not declared.

    The autouse fixture is active in this very test, so a default-constructed
    layer must NOT resolve under the repo's `data/runtime/`.
    """
    layer = ActivationLayer(arbiter=None)
    resolved = str(Path(layer.log_path).resolve())
    assert str((REPO / "data" / "runtime").resolve()) not in resolved, (
        f"the activation log escaped isolation: {resolved}")


# =====================================================================
# (k) THE ENUM CENSUS - the precondition, pinned
# =====================================================================

def _enum_members_by_file():
    """Every `Enum` subclass member in `src/`, by rglob.

    RGLOB rather than a module list (Ruling 70's instrument lesson): the census
    must cover the module nobody has written yet, or it reports a disjointness
    that lapses the moment someone adds a file.
    """
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
    return found


def test_k_the_activation_vocabulary_collides_with_no_other_enum():
    """PIN (k). **THE PRECONDITION, RE-RUN AND PINNED.** A collision is a STOP,
    never an improvised rename - two enums sharing a member name is how two
    senses of one word get conflated at a boundary (Ruling 30's exact defect,
    and Ruling 73's `DEFERRED` near-miss one docket ago)."""
    census = _enum_members_by_file()
    ours = {m.name for m in StopCondition} | {m.name for m in BoundKind}

    collisions = {}
    for member in ours:
        owners = [o for o in census.get(member, [])
                  if not o.startswith("src/goals/goal_activation.py")]
        if owners:
            collisions[member] = owners
    assert collisions == {}, f"the activation vocabulary collides: {collisions}"


def test_k_expired_was_avoided_and_is_still_racms():
    """PIN (k), the specific near-collision the handoff named."""
    census = _enum_members_by_file()
    assert any("racm.py" in owner for owner in census.get("EXPIRED", []))
    assert "EXPIRED" not in {m.name for m in StopCondition}
    assert "EXPIRED" not in {m.name for m in BoundKind}


def test_k_both_vocabularies_are_closed_at_exactly_their_ruled_members():
    """PIN (k), **ADDED AFTER A MUTATION SURVIVOR - A REAL GAP.**

    Adding a `TIME_BOUND` member to `BoundKind` survived the entire slate. res.4
    rules BOTH bound kinds ORDINAL-BASED and wall-clock-free, with **no time
    bound, because the timestamp-join class is CARRIED, not extended** - a time
    bound needs a clock this layer does not own and a join between two stores
    that share no symbolic ordinal, which is the limitation `focus_persistence`
    already declares about itself. That was a ruled property with nothing
    holding it.

    Membership is a MANIFEST DECISION (Ruling 7's discipline): a sixth stop or a
    third bound kind reddens this pin, which is exactly when it needs a ruling
    rather than arriving as a convenience.
    """
    assert [m.name for m in StopCondition] == [
        "BOUND_REACHED", "CRITERION_EVIDENCE", "NO_PROGRESS",
        "CONTRADICTION_ENCOUNTERED", "AUTHORITY_DENIAL"], (
        "QL5's stop set changed - membership is a manifest decision")
    assert [m.name for m in BoundKind] == [
        "EXAMINATION_BOUND", "PROGRESS_BOUND"], (
        "the bound vocabulary changed - a TIME bound is refused by res.4, "
        "because the timestamp-join class is carried and not extended")

    # AND NO MEMBER OF EITHER IS WALL-CLOCK SHAPED.
    for member in list(StopCondition) + list(BoundKind):
        assert not any(word in member.name.lower()
                       for word in ("time", "clock", "deadline", "elapsed",
                                    "duration", "expiry", "expires")), member


def test_k_the_layer_reads_no_clock_for_any_bound():
    """PIN (k). res.4's wall-clock-free half, as SHAPE. `datetime.now()` may
    stamp a record; it may never reach a bound derivation."""
    tree = _tree()
    functions = {n.name: n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef)}
    for name in ("bound_met", "_further_examinations", "_no_progress_run"):
        rendered = ast.unparse(functions[name])
        for word in ("datetime", "now(", "time", "opened_at", "closed_at",
                     "recorded_at"):
            assert word not in rendered, (
                f"{name} reads a clock (`{word}`) - both bounds are ordinal")


def test_k_the_census_instrument_actually_finds_known_enums():
    """The census's own control - a scan that has stopped scanning must fail
    HERE rather than report a comfortable zero."""
    census = _enum_members_by_file()
    assert "DEFERRED" in census and any("racm.py" in o
                                        for o in census["DEFERRED"])
    assert "BOUND_REACHED" in census, "the census cannot see the new module"
    assert any("goal_activation.py" in o for o in census["BOUND_REACHED"])
    assert len(census) > 100, f"census implausibly small: {len(census)}"


# =====================================================================
# res.7 - THE DRIVE PRODUCER IS NOT BUILT, AND THE CONJUNCTION IS RECORDED
# =====================================================================

def test_res7_no_internal_drive_producer_exists_anywhere():
    """res.7 / Ruling 62's conjunction form. **Q3 LANDED AND THE PRODUCER IS
    STILL NOT BUILT** - a drive at this era has nothing honest to produce.

    Reopening is a CONJUNCTION: the activation layer exists (satisfied) AND a
    ruled content source exists (not satisfied).
    """
    offenders = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "goal_ledger.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and node.attr == "INTERNAL_DRIVE":
                offenders.append(
                    f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    assert offenders == [], (
        f"an INTERNAL_DRIVE producer appeared at {offenders}. Q3 satisfies only "
        f"the FIRST half of the reopening conjunction; deriving a desired_state "
        f"from templates fabricates intention.")


def test_res7_the_finding_condition_migrated_and_lost_its_expiry():
    """res.7. The `goal_ledger.py` note said "before Q3", which would now read
    as SATISFIED and quietly license the record it was written to flag."""
    source = (REPO / "src/goals/goal_ledger.py").read_text(encoding="utf-8")
    assert "appearing in the ledger is a FINDING" in source
    assert "SUPERSEDED 2026-08-05 BY RULING 74" in source
    # The old text is KEPT, struck, as the record of what it said.
    assert "~~so its first producer is Q3's drive wiring~~" in source
    assert "REOPENING IS A CONJUNCTION" in source
