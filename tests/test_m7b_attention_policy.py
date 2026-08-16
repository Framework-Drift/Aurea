"""M7-b: `attention-policy.v1`, the bound loop, and the selection log.

THE TEN BINDING PROPERTIES, in the handoff's own order:
  1. DETERMINISM - identical kernel state, identical selection and basis.
  2. CATEGORY PRECEDENCE - obligation > prediction > goal, each edge witnessed.
  3. WITHIN-CATEGORY ORDERING - due ordinal (including the deferral fold),
     PROVIDED-before-ABSENT horizon standing, commitment order.
  4. TIE-BREAK BY IDENTITY, on a genuine tie.
  5. NOTHING_ATTENDABLE on an empty kernel - RECORDED, not raised.
  6. CENSUS COMPLETENESS - N candidates, N census rows, every non-selection
     carrying the rung that outranked it.
  7. RECONSTRUCTION CONTINUITY - a cold second loop selects the same next item
     with the same basis (Test 6 in miniature, extended to v-b).
  8. THE LOG GRANTS NOTHING - no `src/` logic path reads it.
  9. POLICY PURITY - no file, ledger, clock or stochastic import.
 10. THE FOUNDRY-CONTRACT SLOT - present, and pinned UNEVALUATED.

HANDLE DISCIPLINE, unchanged from M7-a: REAL ledgers where their write APIs are
simple, MINIMAL STUBS where construction machinery is another milestone's
subject. A stub carries only the read methods the derivation names.
"""

import ast
import pathlib

import pytest

from src.executive.attention_policy import (
    CATEGORY_PRECEDENCE,
    FOUNDRY_CONTRACT,
    POLICY_NAME,
    POLICY_VERSION,
    WITHIN_CATEGORY_LADDER,
    AttentionPolicy,
    PolicyIdentityMismatch,
    SelectionBasis,
    SelectionOutcome,
)
from src.executive.derived_view import (
    AttentionCategory,
    ChairState,
    derive,
)
from src.executive.loop import ExecutiveLoop, NoAttentionPolicyBound
from src.executive.selection_log import (
    GateOneReferent,
    SelectionLog,
    SelectionLogUnreadable,
)
from src.external.acquisition_ledger import AcquisitionLedger
from src.external.prediction_ledger import PredictionLedger, provided
from src.filtration.obligation_ledger import ObligationLedger

SRC = pathlib.Path("src")


# ---------------------------------------------------------------------------
# Stubs - only the read methods `derive()` names.
# ---------------------------------------------------------------------------

class _StubGoals:
    def __init__(self, goal_ids=()):
        self._ids = tuple(goal_ids)

    def commitments(self):
        return tuple(_StubGoalCommitment(g) for g in self._ids)


class _StubGoalCommitment:
    def __init__(self, goal_id):
        self.goal_id = goal_id


@pytest.fixture()
def kernel(tmp_path):
    obligations = ObligationLedger(
        ledger_path=str(tmp_path / "obligations.jsonl"))
    predictions = PredictionLedger(
        ledger_path=str(tmp_path / "predictions.jsonl"))
    acquisitions = AcquisitionLedger(
        ledger_path=str(tmp_path / "acquisitions.jsonl"))
    return obligations, predictions, acquisitions


def _loop(kernel, goals=(), tmp_path=None, policy=None):
    obligations, predictions, acquisitions = kernel
    return ExecutiveLoop(
        obligations, predictions, _StubGoals(goals), acquisitions,
        policy=policy if policy is not None else AttentionPolicy(),
        selections=SelectionLog(
            log_path=str(tmp_path / "attention_selections.jsonl")))


# ===========================================================================
# PIN 1 - DETERMINISM
# ===========================================================================

def test_1_identical_state_yields_identical_selection_and_basis(kernel, tmp_path):
    obligations, predictions, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "first")
    obligations.admit("test", "claim", "CLM-0002", "second")
    predictions.commit("a prediction")
    loop = _loop(kernel, goals=("GLC-0001",), tmp_path=tmp_path)

    first, second = loop.select(), loop.select()
    assert first == second
    assert first.selected_record_id == second.selected_record_id
    assert first.deciding_basis is second.deciding_basis


def test_1b_selection_is_permutation_invariant(kernel, tmp_path):
    """The candidate ORDER cannot reach the outcome (Ruling 71's property)."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "first")
    obligations.admit("test", "claim", "CLM-0002", "second")
    loop = _loop(kernel, tmp_path=tmp_path)
    forward = loop.select()

    view = loop.observe()
    reversed_view = type(view)(
        open_obligations=view.open_obligations,
        unresolved_predictions=view.unresolved_predictions,
        committed_goals=view.committed_goals,
        chair=view.chair,
        verdict_acquisition_id=view.verdict_acquisition_id,
        candidates=tuple(reversed(view.candidates)))
    assert AttentionPolicy().select(reversed_view).selected_record_id == \
        forward.selected_record_id


# ===========================================================================
# PIN 2 - CATEGORY PRECEDENCE, both edges
# ===========================================================================

def test_2_declared_precedence_is_the_headings_order():
    assert CATEGORY_PRECEDENCE == (AttentionCategory.OBLIGATION,
                                   AttentionCategory.PREDICTION,
                                   AttentionCategory.GOAL)


def test_2a_one_obligation_outranks_any_prediction_and_any_goal(kernel, tmp_path):
    obligations, predictions, _ = kernel
    predictions.commit("a prediction that will not be chosen")
    admitted = obligations.admit("test", "claim", "CLM-0001", "the obligation")
    loop = _loop(kernel, goals=("GLC-0001", "GLC-0002"), tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_category is AttentionCategory.OBLIGATION
    assert selection.selected_record_id == admitted.obligation_id


def test_2b_one_prediction_outranks_any_goal(kernel, tmp_path):
    _, predictions, _ = kernel
    committed = predictions.commit("the prediction")
    loop = _loop(kernel, goals=("GLC-0001", "GLC-0002"), tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_category is AttentionCategory.PREDICTION
    assert selection.selected_record_id == committed.prediction_id


def test_2c_a_resolved_prediction_leaves_the_field_to_goals(kernel, tmp_path):
    """Categories DRAIN - the property that makes persistence a queue, not a trap."""
    from src.external.prediction_ledger import PredictionOutcome
    _, predictions, _ = kernel
    # The criterion must be DECLARED at commit time - Ruling 61 refuses a
    # resolution naming one the commitment never recorded, which is the whole
    # point of fixing criteria before the outcome.
    committed = predictions.commit(
        "resolved before it could be attended",
        success_criteria=provided("it simply resolves"))
    predictions.resolve(committed.prediction_id, PredictionOutcome.CONFIRMED,
                        "success_criteria")
    loop = _loop(kernel, goals=("GLC-0001",), tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_category is AttentionCategory.GOAL


# ===========================================================================
# PIN 3 - WITHIN-CATEGORY ORDERING
# ===========================================================================

def test_3a_obligations_order_by_admission_when_none_is_deferred(kernel, tmp_path):
    obligations, _, _ = kernel
    first = obligations.admit("test", "claim", "CLM-0001", "earlier")
    obligations.admit("test", "claim", "CLM-0002", "later")
    loop = _loop(kernel, tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_record_id == first.obligation_id
    assert selection.deciding_basis is SelectionBasis.DUE_ORDINAL


def test_3b_a_deferral_moves_an_obligation_behind_a_later_arrival(kernel, tmp_path):
    """THE DEFERRAL FOLD. `due_seq` is on a SEPARATE record from `open_items()`.

    Without folding the stream the first-admitted obligation would still be
    selected, because its OPEN record is unchanged by the deferral - which is
    the exact defect this fold exists to close.
    """
    obligations, _, _ = kernel
    first = obligations.admit("test", "claim", "CLM-0001", "deferred far out")
    second = obligations.admit("test", "claim", "CLM-0002", "still standing")
    obligations.defer(first.obligation_id, "waiting on evidence", "SEQ-009999")
    loop = _loop(kernel, tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_record_id == second.obligation_id
    assert selection.deciding_basis is SelectionBasis.DUE_ORDINAL


def test_3c_an_overdue_deferral_outranks_a_recent_arrival(kernel, tmp_path):
    """A due ordinal already PASSED sorts ahead - the other half of 3b."""
    obligations, _, _ = kernel
    first = obligations.admit("test", "claim", "CLM-0001", "will be overdue")
    obligations.admit("test", "claim", "CLM-0002", "arrived later")
    obligations.defer(first.obligation_id, "was parked, now due", "SEQ-000001")
    loop = _loop(kernel, tmp_path=tmp_path)

    assert loop.select().selected_record_id == first.obligation_id


def test_3d_a_recorded_horizon_orders_before_one_with_none(kernel, tmp_path):
    _, predictions, _ = kernel
    bare = predictions.commit("no horizon declared")
    with_horizon = predictions.commit(
        "horizon recorded", resolution_horizon=provided("by the next review"))
    loop = _loop(kernel, tmp_path=tmp_path)

    selection = loop.select()
    assert selection.selected_record_id == with_horizon.prediction_id
    assert selection.deciding_basis is SelectionBasis.HORIZON_STANDING
    # ...and the bare one is later in commitment order, so this is not merely
    # the ordinal rung winning under another name.
    assert bare.prediction_id < with_horizon.prediction_id


def test_3e_declared_none_and_absent_rank_together_but_stay_distinct(kernel,
                                                                    tmp_path):
    """DOCKET H'S CUT SURVIVES THE RANK.

    Both sort behind PROVIDED and tie with each other - ordering them against
    one another would need a reason no ruling supplies - and the census still
    records WHICH each one was.
    """
    from src.external.prediction_ledger import declared_none
    _, predictions, _ = kernel
    none_declared = predictions.commit(
        "declared none", resolution_horizon=declared_none())
    never_asked = predictions.commit("never asked")
    loop = _loop(kernel, tmp_path=tmp_path)

    selection = loop.select()
    # They tie at the horizon rung, so commitment order decides.
    assert selection.deciding_basis is SelectionBasis.COMMITMENT_ORDER
    assert selection.selected_record_id == none_declared.prediction_id

    states = {c.record_id: c.horizon_state for c in selection.census}
    assert states[none_declared.prediction_id] == "declared_none"
    assert states[never_asked.prediction_id] == "absent"


def test_3f_goals_order_by_commitment_order(kernel, tmp_path):
    loop = _loop(kernel, goals=("GLC-0002", "GLC-0001"), tmp_path=tmp_path)
    selection = loop.select()
    assert selection.selected_record_id == "GLC-0001"
    assert selection.deciding_basis is SelectionBasis.COMMITMENT_ORDER


def test_3g_a_sole_candidate_records_category_precedence(kernel, tmp_path):
    """No within-category key ran, and the basis says exactly that."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the only one")
    assert _loop(kernel, tmp_path=tmp_path).select().deciding_basis is \
        SelectionBasis.CATEGORY_PRECEDENCE


# ===========================================================================
# PIN 4 - TIE-BREAK BY IDENTITY, on a genuine tie
# ===========================================================================

def test_4_a_genuine_tie_breaks_by_record_identity(kernel, tmp_path):
    """Two goals whose ordinals are EQUAL - only identity can separate them."""
    loop = _loop(kernel, goals=("GLC-0007-beta", "GLC-0007-alpha"),
                 tmp_path=tmp_path)
    selection = loop.select()
    assert selection.deciding_basis is SelectionBasis.RECORD_IDENTITY
    assert selection.selected_record_id == "GLC-0007-alpha"


def test_4b_every_ladder_ends_in_the_identity_backstop():
    for category, ladder in WITHIN_CATEGORY_LADDER.items():
        assert ladder[-1][0] is SelectionBasis.RECORD_IDENTITY, category


# ===========================================================================
# PIN 5 - NOTHING_ATTENDABLE, recorded not raised
# ===========================================================================

def test_5_an_empty_kernel_is_recorded_not_raised(kernel, tmp_path):
    loop = _loop(kernel, tmp_path=tmp_path)
    record = loop.step()

    assert record.outcome is SelectionOutcome.NOTHING_ATTENDABLE
    assert record.selected_record_id is None
    assert record.deciding_basis is None
    assert record.census == ()
    # RECORDED: the line exists, and it says the Executive looked.
    lines = loop.selections.selections()
    assert len(lines) == 1
    assert lines[0]["outcome"] == "nothing_attendable"


def test_5b_a_nothing_attendable_record_cannot_carry_a_selection():
    from src.executive.attention_policy import AttentionSelection
    with pytest.raises(ValueError):
        AttentionSelection(
            outcome=SelectionOutcome.NOTHING_ATTENDABLE,
            selected_category=None, selected_record_id="OBL-0001",
            deciding_basis=None, census=())


# ===========================================================================
# PIN 6 - CENSUS COMPLETENESS
# ===========================================================================

def test_6_the_census_names_every_candidate_with_its_outranking_rung(kernel,
                                                                    tmp_path):
    obligations, predictions, _ = kernel
    a = obligations.admit("test", "claim", "CLM-0001", "first")
    b = obligations.admit("test", "claim", "CLM-0002", "second")
    p = predictions.commit("a prediction")
    loop = _loop(kernel, goals=("GLC-0001", "GLC-0002"), tmp_path=tmp_path)

    record = loop.step()
    census = {c.record_id: c for c in record.census}

    # N candidates in, N rows out - 2 obligations + 1 prediction + 2 goals.
    assert len(record.census) == 5
    assert set(census) == {a.obligation_id, b.obligation_id, p.prediction_id,
                           "GLC-0001", "GLC-0002"}

    # The selected one, and ONLY it, carries no outranking rung.
    assert census[a.obligation_id].selected is True
    assert census[a.obligation_id].outranked_at is None
    assert [c.record_id for c in record.census if c.selected] == [a.obligation_id]

    # A LOSING CATEGORY is outranked by precedence and never entered a ladder.
    for record_id in (p.prediction_id, "GLC-0001", "GLC-0002"):
        assert census[record_id].outranked_at is SelectionBasis.CATEGORY_PRECEDENCE

    # A losing candidate INSIDE the winning category names the rung it lost at.
    assert census[b.obligation_id].outranked_at is SelectionBasis.DUE_ORDINAL

    # Every row carries a key, and the names are parallel to the values.
    for row in record.census:
        assert len(row.ordering_key) == len(row.key_names)
        assert row.key_names == tuple(
            basis.value for basis, _ in WITHIN_CATEGORY_LADDER[row.category])


def test_6b_the_census_reaches_the_written_line_intact(kernel, tmp_path):
    """The reason must be ON THE RECORD, not merely in the returned object."""
    obligations, _, _ = kernel
    a = obligations.admit("test", "claim", "CLM-0001", "first")
    b = obligations.admit("test", "claim", "CLM-0002", "second")
    loop = _loop(kernel, tmp_path=tmp_path)
    loop.step()

    written = loop.selections.selections()[0]
    rows = {r["record_id"]: r for r in written["candidate_census"]}
    assert set(rows) == {a.obligation_id, b.obligation_id}
    assert rows[b.obligation_id]["outranked_at"] == "due_ordinal"
    assert rows[a.obligation_id]["outranked_at"] is None
    assert rows[a.obligation_id]["selected"] is True


def test_6c_the_line_carries_the_policy_identity_and_the_gate_one_triple(kernel,
                                                                        tmp_path):
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    loop.step()

    written = loop.selections.selections()[0]
    assert written["policy_name"] == POLICY_NAME
    assert written["policy_version"] == POLICY_VERSION
    # ABSENT IS AN ANSWER: the two Gate-1 fields with no referent say so
    # explicitly rather than being omitted or filled with an empty list.
    assert written["gate_one"] == {
        "pressure_class_applied": GateOneReferent.NOT_APPLICABLE.value,
        "unexercised_defeaters": GateOneReferent.NOT_APPLICABLE.value,
        "rejection_reason": GateOneReferent.IN_CANDIDATE_CENSUS.value,
    }


# ===========================================================================
# PIN 7 - RECONSTRUCTION CONTINUITY (Test 6 in miniature, extended to v-b)
# ===========================================================================

def test_7_a_cold_second_loop_selects_the_same_item_with_the_same_basis(kernel,
                                                                       tmp_path):
    obligations, predictions, acquisitions = kernel
    obligations.admit("test", "claim", "CLM-0001", "first")
    obligations.admit("test", "claim", "CLM-0002", "second")
    predictions.commit("a prediction")
    first_loop = _loop(kernel, goals=("GLC-0001",), tmp_path=tmp_path)
    before = first_loop.select()

    # The first loop is dropped; new handles are built over the SAME files,
    # the way a fresh process would after the first one was killed.
    rebuilt = ExecutiveLoop(
        ObligationLedger(ledger_path=str(obligations.ledger_path)),
        PredictionLedger(ledger_path=str(predictions.ledger_path)),
        _StubGoals(("GLC-0001",)),
        AcquisitionLedger(ledger_path=str(acquisitions.ledger_path)),
        policy=AttentionPolicy(),
        selections=SelectionLog(log_path=str(tmp_path / "second.jsonl")))
    after = rebuilt.select()

    assert before.selected_record_id == after.selected_record_id
    assert before.deciding_basis is after.deciding_basis
    assert before == after


def test_7b_recording_a_selection_does_not_change_the_next_one(kernel, tmp_path):
    """The log is not an input: stepping twice selects the same item.

    This is the OTHER face of pin 8. If any recency term ever leaked into the
    policy this pin would redden, and so would pin 7.
    """
    obligations, _, _ = kernel
    a = obligations.admit("test", "claim", "CLM-0001", "first")
    obligations.admit("test", "claim", "CLM-0002", "second")
    loop = _loop(kernel, tmp_path=tmp_path)

    first, second = loop.step(), loop.step()
    assert first.selected_record_id == second.selected_record_id == a.obligation_id
    assert first.selection_id != second.selection_id
    assert len(loop.selections.selections()) == 2


# ===========================================================================
# PIN 8 - THE SELECTION LOG GRANTS NOTHING
# ===========================================================================

def _imports_of(path: pathlib.Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
                names.update(f"{node.module}.{a.name}" for a in node.names)
    return names


def test_8_no_src_module_but_the_loop_imports_the_selection_log():
    """Ruling 72's no-consumer form - RED the day a consumer appears.

    A consumer is exactly when this log needs its own ruling, because reading
    an act log back into a decision is how a derived view acquires state.
    """
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "selection_log.py":
            continue
        if any("selection_log" in name for name in _imports_of(path)):
            consumers.append(str(path).replace("\\", "/"))
    assert consumers == ["src/executive/loop.py"], consumers


def test_8b_the_derived_view_cannot_reach_the_selection_log():
    """L10 AT ITS SHARPEST: no logic path from the log into `derive`."""
    imports = _imports_of(SRC / "executive" / "derived_view.py")
    assert not any("selection_log" in name for name in imports)
    source = (SRC / "executive" / "derived_view.py").read_text(encoding="utf-8")
    for forbidden in ("SelectionLog", "selections(", "AttentionSelection"):
        assert forbidden not in source, forbidden


def test_8c_the_policy_cannot_reach_the_selection_log():
    imports = _imports_of(SRC / "executive" / "attention_policy.py")
    assert not any("selection_log" in name for name in imports)


def test_8d_the_scanner_fires(tmp_path):
    """CONTROL: the import scanner sees a real consumer when one exists."""
    planted = tmp_path / "planted.py"
    planted.write_text(
        "from src.executive.selection_log import SelectionLog\n", encoding="utf-8")
    assert any("selection_log" in name for name in _imports_of(planted))


# ===========================================================================
# PIN 9 - POLICY PURITY (Ruling 71 as import-absence)
# ===========================================================================

FORBIDDEN_IN_POLICY = (
    "random", "secrets", "numpy", "datetime", "time", "pathlib", "os", "json",
    "src.filtration", "src.goals", "src.external", "src.doctrine",
    "src.utils.ledger_mint", "src.utils.atomic_write", "src.executive.loop",
    "src.executive.selection_log",
)


def test_9_the_policy_imports_nothing_it_could_read_draw_or_write_with():
    imports = _imports_of(SRC / "executive" / "attention_policy.py")
    for name in imports:
        for forbidden in FORBIDDEN_IN_POLICY:
            assert not (name == forbidden or name.startswith(forbidden + ".")), \
                f"attention_policy.py imports {name!r}"


def test_9b_the_policy_never_opens_anything_and_holds_no_path():
    source = (SRC / "executive" / "attention_policy.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {node.func.id for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in calls
    assert not any(
        isinstance(node, ast.Attribute) and node.attr in {"read_all", "commitments",
                                                          "open_items", "record"}
        for node in ast.walk(tree))


def _referenced_names(path: pathlib.Path):
    """Every NAME and ATTRIBUTE this module's CODE touches. Prose excluded.

    AST rather than substring, and the reason is this repo's most-repeated
    instrument lesson: the first draft of `test_9c` scanned source text for
    `DecidingBasis` and matched the DOCSTRING that explains why this module
    keeps its own vocabulary separate from that one. **Deleting correct
    documentation to satisfy a noisy guard is how a guard earns its eventual
    weakening** (Ruling 63's precedent), so the scanner was sharpened and the
    prose left standing - the ninth recorded occurrence of that class.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def test_9c_the_policy_never_consults_the_goal_arbiter():
    """Ruling 73's ladder orders WITHIN goals; this orders ACROSS categories."""
    imports = _imports_of(SRC / "executive" / "attention_policy.py")
    assert not any("goal_arbitration" in name for name in imports)
    assert "DecidingBasis" not in _referenced_names(
        SRC / "executive" / "attention_policy.py")


def test_9c_control_the_name_scanner_fires(tmp_path):
    """CONTROL: it catches a real reference and still ignores prose."""
    planted = tmp_path / "planted.py"
    planted.write_text('"""DecidingBasis in prose."""\nx = DecidingBasis\n',
                       encoding="utf-8")
    assert "DecidingBasis" in _referenced_names(planted)
    prose_only = tmp_path / "prose.py"
    prose_only.write_text('"""DecidingBasis in prose only."""\nx = 1\n',
                          encoding="utf-8")
    assert "DecidingBasis" not in _referenced_names(prose_only)


def test_9d_selection_is_a_pure_function_of_the_view(kernel, tmp_path):
    """Running the policy writes NO line - the arbiter's select/examine split."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    for _ in range(5):
        loop.select()
    assert loop.selections.selections() == ()


def test_9e_no_numeric_literal_reaches_a_ladder_key():
    """§9 bar #5: keys are read ordinals and membership ranks, never magnitudes.

    The two literals a rank legitimately needs (`0` and `1` for present/absent
    horizon standing) are DECLARED here rather than tolerated silently, so a
    third one arriving is a visible change.
    """
    source = (SRC / "executive" / "attention_policy.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_key_"):
            found[node.name] = sorted(
                n.value for n in ast.walk(node)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)
                and not isinstance(n.value, bool))
    assert found["_key_horizon_standing"] == [0, 1]
    assert found["_key_due_ordinal"] == []
    assert found["_key_commitment_order"] == []
    assert found["_key_record_identity"] == []


# ===========================================================================
# PIN 10 - THE FOUNDRY-CONTRACT SLOT
# ===========================================================================

def test_10_the_contract_slot_is_present_and_names_fork_8_1():
    assert FOUNDRY_CONTRACT["fork"] == "8.1"
    assert FOUNDRY_CONTRACT["status"] == "DEFERRED"
    assert FOUNDRY_CONTRACT["question"]


def test_10b_the_contract_is_pinned_unevaluated():
    """Filling this in would resolve fork 8.1 BY CONSTRUCTION."""
    assert FOUNDRY_CONTRACT["evaluated"] is False
    assert FOUNDRY_CONTRACT["evaluation_record"] is None


def test_10c_the_contract_is_immutable_and_gates_nothing():
    with pytest.raises(TypeError):
        FOUNDRY_CONTRACT["evaluated"] = True      # type: ignore[index]
    source = (SRC / "executive" / "attention_policy.py").read_text(encoding="utf-8")
    # It is DECLARED and carried - never read into a branch.
    assert "FOUNDRY_CONTRACT[" not in source
    assert "if self.foundry_contract" not in source


# ===========================================================================
# THE BOUND LOOP - identity, refusals, and the write gate
# ===========================================================================

def test_the_unbound_refusal_survives_v_b(kernel, tmp_path):
    """REGRESSION-PINNED: v-b binds a chooser; it does not retire the refusal."""
    obligations, predictions, acquisitions = kernel
    loop = ExecutiveLoop(obligations, predictions, _StubGoals(()), acquisitions,
                         selections=SelectionLog(log_path=str(tmp_path / "l.jsonl")))
    with pytest.raises(NoAttentionPolicyBound):
        loop.step()
    with pytest.raises(NoAttentionPolicyBound):
        loop.select()
    # ...and observation stays available, exactly as in v-a.
    assert loop.observe().chair is ChairState.UNREGISTERED


def test_the_v_a_placeholder_is_gone(kernel, tmp_path):
    """A bound policy no longer no-ops: the `NotImplementedError` is REPLACED."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    record = loop.step()
    assert record.outcome is SelectionOutcome.SELECTED
    # AST, NOT SUBSTRING: the supersession note in `step`'s own docstring names
    # the placeholder it replaced, and that sentence is the history worth
    # keeping. What must be gone is the RAISE, not the word.
    tree = ast.parse((SRC / "executive" / "loop.py").read_text(encoding="utf-8"))
    raised = {node.exc.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)
              and isinstance(node.exc.func, ast.Name)}
    assert "NotImplementedError" not in raised
    # ...and the refusal that must SURVIVE is still raised from this module.
    assert "NoAttentionPolicyBound" in raised


def test_a_mismatched_policy_identity_refuses():
    with pytest.raises(PolicyIdentityMismatch):
        AttentionPolicy(name="attention-policy.v2")
    with pytest.raises(PolicyIdentityMismatch):
        AttentionPolicy(version="2")


def test_a_failed_selection_write_gates_the_selection(kernel, tmp_path,
                                                      monkeypatch):
    """THE WRITE GATES THE ACT - no silent continue, and no line either."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)

    def _boom(*args, **kwargs):
        raise OSError("disk gone")

    monkeypatch.setattr("src.executive.selection_log.durable_append_text", _boom)
    with pytest.raises(OSError):
        loop.step()
    assert loop.selections.entries == []


def test_an_unreadable_log_refuses_typed_rather_than_reading_empty(kernel,
                                                                  tmp_path,
                                                                  monkeypatch):
    """Ruling 53's sentinel, and Ruling 74's finding applied at drafting."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    loop.step()

    real_open = open

    def _refuse(path, *args, **kwargs):
        if str(path).endswith("attention_selections.jsonl"):
            raise OSError("unreadable")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _refuse)
    with pytest.raises(SelectionLogUnreadable):
        loop.selections.selections()


def test_an_underived_mint_refuses_and_never_falls_back(kernel, tmp_path,
                                                        monkeypatch):
    """RULING 53'S SENTINEL AT THE MINT - found by a SURVIVING MUTANT.

    The first slate had no pin here: `selections()` raising was pinned, but the
    MINT falling back to `SEL-0001` on an underived floor survived the whole
    file. That is the more dangerous half - a fallback REISSUES an id that may
    already name a different attention allocation, in an append-only record
    where nothing can afterwards disambiguate two lines wearing one id.

    Driven at `derive_max_ordinal`'s own contract: `None` means the log EXISTS
    and the read raised.
    """
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    loop.step()                       # a real line exists; SEL-0001 is taken

    monkeypatch.setattr("src.executive.selection_log.derive_max_ordinal",
                        lambda *a, **k: None)
    with pytest.raises(SelectionLogUnreadable):
        loop.step()
    # ...and nothing was appended on the refused path.
    assert len(loop.selections.selections()) == 1


def test_a_missing_log_is_a_first_run_not_a_fault(kernel, tmp_path):
    """The sentinel's other half: ABSENCE is a legitimate zero."""
    obligations, _, _ = kernel
    obligations.admit("test", "claim", "CLM-0001", "the one")
    loop = _loop(kernel, tmp_path=tmp_path)
    assert not loop.selections.log_path.exists()
    assert loop.step().selection_id == "SEL-0001"


def test_the_selection_log_has_no_update_or_delete_surface():
    """Append-only as SHAPE: a record of an act is never edited."""
    tree = ast.parse((SRC / "executive" / "selection_log.py").read_text(
        encoding="utf-8"))
    methods = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for forbidden in ("update", "amend", "revise", "delete", "remove", "clear",
                      "purge", "truncate", "rewrite"):
        assert forbidden not in methods


def test_the_log_writes_through_the_durable_funnel_only():
    """Ruling 78: no write mode in this file at all.

    AST OVER `open()` CALLS, not a substring hunt for `"a"`. The first draft
    scanned source text and matched the docstring sentence citing Ruling 78's
    own mode-`"a"` census - and a scanner that forbids a QUOTED RULING in a
    comment would eventually be satisfied by deleting the citation. Same
    instrument lesson as `_referenced_names` above.
    """
    source = (SRC / "executive" / "selection_log.py").read_text(encoding="utf-8")
    assert "durable_append_text" in source
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            modes = [a.value for a in node.args[1:]
                     if isinstance(a, ast.Constant)]
            modes += [k.value.value for k in node.keywords
                      if k.arg == "mode" and isinstance(k.value, ast.Constant)]
            for mode in modes:
                assert set(mode) <= set("rbt"), f"write-mode open({mode!r})"
