"""test_m9a_prediction_exposure.py - M9-a: THE COMMITMENT CARRIES ITS EXPOSURE.

Hundred-seventeenth entry (PATH v143), M9_GROUNDING.md section M9-a, heading
line 122: resolution criteria fixed before outcomes exist, in operational
terms; typed dependencies declared at commitment under the ruled six; the
licensing linkage validated to resolve - THE JOINT's substrate.

EVERY PIN HERE IS RED AGAINST `4e1b307`, where `DependencyKind`,
`TypedDependency`, `OperationalCriterion`, the `licensing_goal` field and
`src/external/prediction_census.py` did not exist - the file fails at
collection (ImportError), witnessed in a detached worktree.

THE CENSUS IS THE SUBSTRATE: the referenceable-form set is the union of the
kernel's own two resolver registries (`TargetKind`, `KernelRefKind`) plus the
goal linkage this entry itself rules; the criterion surfaces are the four
whose owners expose a derived, non-mutating, closed-vocabulary state read.
The vocabularies live in the census as DATA and are drift-pinned here against
the owners' enums - the guard lives in the pins, not in an import.
"""

from __future__ import annotations

import ast
import dataclasses
import json
from pathlib import Path

import pytest

from src.external.claim_ancestry import FieldState
from src.external.prediction_census import (CENSUS_CITATION,
                                            CRITERION_SURFACES,
                                            EXCLUDED_CRITERION_SURFACES,
                                            EXCLUDED_FORMS,
                                            REFERENCEABLE_FORMS,
                                            id_matches_form, reference_form)
from src.external.prediction_ledger import (DependencyKind, DependencyLink,
                                            OperationalCriterion,
                                            PredictionCommitment,
                                            PredictionLedger,
                                            PredictionOutcome,
                                            TypedDependency, absent,
                                            declared_none, provided)
from src.filtration.obligation_ledger import ObligationRecordType
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalProvenance, GoalStatus)
from src.worldmodel.standing import WorldStanding

LEDGER_MODULE = Path("src/external/prediction_ledger.py")
CENSUS_MODULE = Path("src/external/prediction_census.py")


# =====================================================================
# FIXTURE HELPERS
# =====================================================================

def _goals(tmp_path) -> GoalLedger:
    ledger = GoalLedger(ledger_path=str(tmp_path / "glc.jsonl"))
    ledger.commit(desired_state="keep the M9-a exposure honest",
                  kind=GoalKind.RESEARCH, level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="m9a-pins")
    return ledger


def _ledger(tmp_path, goals=None) -> PredictionLedger:
    return PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"),
                            goal_ledger=goals)


def _exposure():
    """One valid criterion and one valid typed dependency."""
    criterion = OperationalCriterion(
        surface="prediction_resolution_outcome",
        record_id="PRD-0099",
        confirmed_state="confirmed",
        failed_state="falsified")
    dependency = TypedDependency(kind=DependencyKind.OBSERVATION,
                                 record_form="world_proposition",
                                 record_id="WMP-0001")
    return criterion, dependency


def _full_commit(ledger, goal_ref="GLC-0001"):
    criterion, dependency = _exposure()
    return ledger.commit(
        expected_result="the proposition's standing survives its test",
        applicable_conditions=provided("only under the frozen corpus"),
        resolution_horizon=provided("2027-01-01"),
        success_criteria=provided("standing stays supported"),
        failure_criteria=provided("standing becomes undercut"),
        dependency_chain=(DependencyLink.OBSERVATION,),
        claim_refs=("CLM-0001",),
        operational_criteria=(criterion,),
        typed_dependencies=(
            dependency,
            TypedDependency(kind=DependencyKind.MAIN_CLAIM,
                            record_form="claim", record_id="CLM-0001"),
        ),
        licensing_goal=provided(goal_ref),
    )


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [line for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _refuses_and_writes_nothing(tmp_path, exception, **commit_kwargs):
    """The fires-control FORM for every door refusal: the raise alone is not
    the pin - the pin is that a refused commitment WRITES NOTHING and burns
    nothing, so the next honest commitment still mints PRD-0001."""
    goals = _goals(tmp_path)
    ledger = _ledger(tmp_path, goals)
    with pytest.raises(exception):
        ledger.commit(expected_result="refused at the door", **commit_kwargs)
    assert _lines(ledger) == [], (
        "a refused commitment left a line - the refusal happened after the "
        "append, which is storage of hope")
    committed = ledger.commit(expected_result="the honest one after")
    assert committed.prediction_id == "PRD-0001", (
        "the refusal burnt an ordinal - it spent something before refusing")


# =====================================================================
# PIN 1 - THE VOCABULARY, CLOSED AT THE RULED SIX
# =====================================================================

def test_the_ruled_vocabulary_is_closed_at_the_headings_six() -> None:
    """PIN 1. The six are line 122's own words, and the docstring cites the
    entry - a governed-content vocabulary carries its authorization."""
    assert [(m.name, m.value) for m in DependencyKind] == [
        ("OBSERVATION", "observation"),
        ("CAUSAL_LINK", "causal_link"),
        ("ASSUMPTION", "assumption"),
        ("SCOPE", "scope"),
        ("HORIZON", "horizon"),
        ("MAIN_CLAIM", "main_claim"),
    ]
    assert "Hundred-seventeenth entry (PATH v143)" in DependencyKind.__doc__
    assert "line 122" in DependencyKind.__doc__


def test_an_unruled_seventh_kind_is_unwritable() -> None:
    """PIN 1 + PIN 3a, fires-control. Three doors, all shut: the enum
    refuses an unruled value, a LEGACY member name is not silently a ruled
    one, and a raw string cannot ride into a TypedDependency."""
    with pytest.raises(ValueError):
        DependencyKind("an_unruled_seventh")
    # `domain_validity` is L2's word (DependencyLink) and NOT one of the
    # heading's six - the adversarial confusion this pin exists to catch.
    with pytest.raises(ValueError):
        DependencyKind("domain_validity")
    with pytest.raises(TypeError):
        TypedDependency(kind="observation",  # a raw string, not a member
                        record_form="claim", record_id="CLM-0001")


def test_the_legacy_vocabulary_stands_untouched_beside_it() -> None:
    """PIN 4 (era honesty, vocabulary half). `DependencyLink` is Ruling 61's
    recovered L2 sentence and this entry does not reinterpret it."""
    assert {m.value for m in DependencyLink} == {
        "observation", "causal_link", "auxiliary_assumption", "horizon",
        "domain_validity", "the_claim_itself"}
    assert DependencyKind is not DependencyLink
    assert {m.value for m in DependencyKind} != {m.value for m in DependencyLink}


# =====================================================================
# PIN 2 - THE ROUND-TRIP, BYTE-FAITHFUL, TWICE
# =====================================================================

def test_a_fully_loaded_commitment_round_trips_byte_faithful_twice(tmp_path) -> None:
    """PIN 2. Criteria + typed dependencies + linkage, committed once, and:
    the LINE is exactly the record's own serialization; two INDEPENDENT
    re-reads (fresh instances, the file only) both equal the committed
    object; and the loaded commitment is OPERATIONAL."""
    goals = _goals(tmp_path)
    ledger = _ledger(tmp_path, goals)
    committed = _full_commit(ledger)

    [line] = _lines(ledger)
    assert line == json.dumps(committed.as_dict(), allow_nan=False), (
        "the durable line is not the record's own serialization - "
        "byte-faithfulness is the commitment's whole meaning")

    first = _ledger(tmp_path).commitment_for(committed.prediction_id)
    second = _ledger(tmp_path).commitment_for(committed.prediction_id)
    assert first == committed
    assert second == committed
    assert first == second
    assert first.is_operational() is True
    assert first.licensing_goal.state is FieldState.PROVIDED
    assert first.licensing_goal.value == "GLC-0001"
    assert first.typed_dependencies[0].kind is DependencyKind.OBSERVATION
    assert first.operational_criteria[0].confirmed_state == "confirmed"


# =====================================================================
# PIN 3 - THE REFUSALS, EACH IN FIRES-CONTROL FORM
# =====================================================================

def test_an_uncensused_reference_form_is_refused_at_the_door(tmp_path) -> None:
    """PIN 3b. A form the census does not hold is refused BEFORE the append -
    never stored as hope."""
    with pytest.raises(ValueError):
        TypedDependency(kind=DependencyKind.OBSERVATION,
                        record_form="vibes", record_id="VIB-0001")
    _refuses_and_writes_nothing(
        tmp_path, TypeError,
        # a raw dict cannot impersonate a validated TypedDependency either
        typed_dependencies=({"kind": "observation", "record_form": "vibes",
                             "record_id": "VIB-0001"},))


def test_a_reference_outside_its_forms_mint_shape_is_refused(tmp_path) -> None:
    """PIN 3b, the id half: the form is censused but the id is one the
    owner's mint never issued."""
    for bad in ("CLM-", "CLM-01", "WMP-0001"):  # last: right shape, WRONG form
        with pytest.raises(ValueError):
            TypedDependency(kind=DependencyKind.MAIN_CLAIM,
                            record_form="claim", record_id=bad)
    # formless forms still refuse emptiness
    with pytest.raises(ValueError):
        TypedDependency(kind=DependencyKind.ASSUMPTION,
                        record_form="doctrine", record_id="")


def test_a_criterion_naming_no_censused_surface_is_refused(tmp_path) -> None:
    """PIN 3c. Derive or decline, never invent."""
    with pytest.raises(ValueError):
        OperationalCriterion(surface="model_confidence", record_id="PRD-0001",
                             confirmed_state="high", failed_state="low")
    _refuses_and_writes_nothing(
        tmp_path, TypeError,
        operational_criteria=({"surface": "model_confidence"},))


def test_a_criterion_state_outside_the_surfaces_vocabulary_is_refused() -> None:
    """PIN 3c, the state half: a state the surface can never show is a
    criterion that can never be met."""
    with pytest.raises(ValueError):
        OperationalCriterion(surface="world_proposition_standing",
                             record_id="WMP-0001",
                             confirmed_state="supported",
                             failed_state="confirmed")  # a PREDICTION word
    with pytest.raises(ValueError):
        OperationalCriterion(surface="goal_status", record_id="GLC-0001",
                             confirmed_state="achieved",  # not in the enum
                             failed_state="superseded")


def test_a_criterion_whose_two_states_are_one_state_is_refused() -> None:
    """PIN 3c: one state cannot resolve both ways."""
    with pytest.raises(ValueError):
        OperationalCriterion(surface="obligation_status", record_id="OBL-0001",
                             confirmed_state="merged", failed_state="merged")


def test_a_goal_reference_that_does_not_resolve_is_refused(tmp_path) -> None:
    """PIN 3d. The goal ledger holds GLC-0001 only; GLC-0002 resolves
    nowhere, and a commitment under a goal nobody committed licenses
    nothing. Nothing is written, nothing is burnt."""
    _refuses_and_writes_nothing(tmp_path, ValueError,
                                licensing_goal=provided("GLC-0002"))


def test_a_provided_goal_without_a_resolver_is_refused(tmp_path) -> None:
    """PIN 3d, the UNCHECKED half (ObligationLedger.admit's own rule):
    unvalidatable is not validated."""
    ledger = _ledger(tmp_path, goals=None)
    with pytest.raises(ValueError):
        ledger.commit(expected_result="a goal with nobody to ask",
                      licensing_goal=provided("GLC-0001"))
    assert _lines(ledger) == []


def test_a_malformed_goal_reference_is_refused_before_resolution(tmp_path) -> None:
    """PIN 3d, the form half: an id the goal mint never issued is refused
    on shape alone, resolver present or not."""
    _refuses_and_writes_nothing(tmp_path, ValueError,
                                licensing_goal=provided("GOAL-1"))


def test_the_widened_records_are_frozen_and_the_law_is_append_only(tmp_path) -> None:
    """PIN 3e. No mutation of an existing commitment record: the new fields
    are frozen like every old one, and a later append never rewrites an
    earlier line."""
    goals = _goals(tmp_path)
    ledger = _ledger(tmp_path, goals)
    committed = _full_commit(ledger)
    criterion, dependency = _exposure()

    with pytest.raises(dataclasses.FrozenInstanceError):
        committed.operational_criteria = ()
    with pytest.raises(dataclasses.FrozenInstanceError):
        committed.licensing_goal = absent()
    with pytest.raises(dataclasses.FrozenInstanceError):
        criterion.confirmed_state = "falsified"
    with pytest.raises(dataclasses.FrozenInstanceError):
        dependency.kind = DependencyKind.SCOPE

    first_line = _lines(ledger)[0]
    ledger.commit(expected_result="a second, separate commitment")
    assert _lines(ledger)[0] == first_line, (
        "an append rewrote history - the commitment is no longer a record")
    assert len(_lines(ledger)) == 2


# =====================================================================
# PIN 4 - ERA HONESTY: THE OLD RECORDS ARE CLIENTS, NEVER DEBT
# =====================================================================

def test_a_hand_built_legacy_shaped_line_loads_unchanged(tmp_path) -> None:
    """PIN 4, the strongest form: a line carrying EXACTLY the pre-M9 key set
    (no operational_criteria, no typed_dependencies, no licensing_goal key at
    all) loads as a commitment, keeps every old fact, and reads
    NON-OPERATIONAL with the linkage ABSENT - never asked, the honest state."""
    goals = _goals(tmp_path)
    ledger = _ledger(tmp_path, goals)
    modern = _full_commit(ledger)
    legacy_payload = {
        key: value for key, value in modern.as_dict().items()
        if key not in ("operational_criteria", "typed_dependencies",
                       "licensing_goal")}
    legacy_payload["prediction_id"] = "PRD-7777"
    path = tmp_path / "legacy.jsonl"
    path.write_text(json.dumps(legacy_payload) + "\n", encoding="utf-8")

    loaded = PredictionLedger(ledger_path=str(path)).commitment_for("PRD-7777")
    assert loaded is not None, "the legacy line failed to load - era debt"
    assert loaded.expected_result == modern.expected_result
    assert loaded.claim_refs == modern.claim_refs
    assert loaded.dependency_chain == modern.dependency_chain
    assert loaded.operational_criteria == ()
    assert loaded.typed_dependencies == ()
    assert loaded.licensing_goal.state is FieldState.ABSENT
    assert loaded.is_operational() is False


def test_the_old_commit_shape_still_writes_and_reads_non_operational(tmp_path) -> None:
    """PIN 4: every existing call site's shape - no new argument anywhere -
    commits exactly as before, and the resolution machinery is untouched."""
    ledger = _ledger(tmp_path)  # no goal ledger, exactly like every old caller
    committed = ledger.commit(
        expected_result="the old shape survives",
        success_criteria=provided("it loads"),
        dependency_chain=(DependencyLink.THE_CLAIM_ITSELF,),
        claim_refs=("CLM-0009",))
    reloaded = _ledger(tmp_path).commitment_for(committed.prediction_id)
    assert reloaded == committed
    assert reloaded.is_operational() is False
    assert reloaded.licensing_goal.state is FieldState.ABSENT
    resolution = ledger.resolve(committed.prediction_id,
                                PredictionOutcome.CONFIRMED,
                                "success_criteria")
    assert resolution.outcome is PredictionOutcome.CONFIRMED


def test_declared_none_is_a_different_answer_from_absent(tmp_path) -> None:
    """PIN 4, Docket H's cut on the linkage: a commitment EXPLICITLY under no
    goal is on record as having declared none - a different fact from never
    having been asked, and neither needs a resolver."""
    ledger = _ledger(tmp_path, goals=None)  # no resolver: only PROVIDED needs one
    explicit = ledger.commit(expected_result="explicitly unlicensed",
                             licensing_goal=declared_none())
    silent = ledger.commit(expected_result="nobody asked")
    reread = _ledger(tmp_path)
    assert (reread.commitment_for(explicit.prediction_id)
            .licensing_goal.state is FieldState.DECLARED_NONE)
    assert (reread.commitment_for(silent.prediction_id)
            .licensing_goal.state is FieldState.ABSENT)


def test_a_line_with_an_unruled_exposure_drops_whole_never_partial(tmp_path) -> None:
    """PIN 4 + the DependencyLink precedent one field over: a future line
    carrying an unruled kind or an uncensused surface drops as a WHOLE LINE -
    a partially-loaded exposure would route M9-b's backward walk somewhere
    the predictor never named."""
    goals = _goals(tmp_path)
    ledger = _ledger(tmp_path, goals)
    payload = _full_commit(ledger).as_dict()
    payload["prediction_id"] = "PRD-6666"
    payload["typed_dependencies"] = [
        {"kind": "domain_validity",  # L2's word - unruled HERE
         "record_form": "claim", "record_id": "CLM-0001"}]
    path = tmp_path / "unruled.jsonl"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    assert PredictionLedger(ledger_path=str(path)).commitments() == ()


# =====================================================================
# PIN 5 - DETERMINISTIC EVALUABILITY, WITNESSED IN SHAPE
# =====================================================================

def test_two_independent_reads_of_one_criterion_agree(tmp_path) -> None:
    """PIN 5. The criterion's determinism, NOT the resolution machinery
    (that is M9-b): given the criterion and one kernel state, the clerical
    rule - read the named surface, compare - lands two independent
    evaluators on the same answer, on both arms."""
    ledger = _ledger(tmp_path)
    target = ledger.commit(expected_result="the surface under test",
                           success_criteria=provided("it holds"),
                           failure_criteria=provided("it breaks"))
    ledger.resolve(target.prediction_id, PredictionOutcome.FALSIFIED,
                   "failure_criteria")

    criterion = OperationalCriterion(
        surface="prediction_resolution_outcome",
        record_id=target.prediction_id,
        confirmed_state="confirmed",
        failed_state="falsified")

    def clerical_read(instance: PredictionLedger) -> str:
        # The WHOLE evaluation: read the censused surface, compare. Any
        # third outcome is M9-b's honest UNRESOLVED territory, not ours.
        resolution = instance.resolution_for(criterion.record_id)
        state = resolution.outcome.value if resolution else None
        if state == criterion.confirmed_state:
            return "CONFIRMED"
        if state == criterion.failed_state:
            return "FAILED"
        return "UNREACHED"

    first = clerical_read(_ledger(tmp_path))
    second = clerical_read(_ledger(tmp_path))
    assert first == second == "FAILED"

    flipped = OperationalCriterion(
        surface="prediction_resolution_outcome",
        record_id=target.prediction_id,
        confirmed_state="falsified",   # the same kernel state, read by a
        failed_state="confirmed")      # criterion that names it CONFIRMED
    state = _ledger(tmp_path).resolution_for(flipped.record_id).outcome.value
    assert state == flipped.confirmed_state, (
        "the criterion, not the evaluator, decides which arm a state "
        "resolves - determinism is in the DATA")


# =====================================================================
# PIN 7 - THE CENSUS, COMMITTED AS DATA WITH THE ENTRY'S CITATION
# =====================================================================

def test_the_census_carries_the_entrys_citation_and_is_read_only() -> None:
    """PIN 7. M9-b and M9-c consume a RULED census, not a re-derivation."""
    assert "hundred-seventeenth" in CENSUS_CITATION
    assert "v143" in CENSUS_CITATION
    assert "line 122" in CENSUS_CITATION
    assert set(REFERENCEABLE_FORMS) == {
        "claim", "world_proposition", "prediction", "obligation", "episode",
        "goal", "doctrine", "scar", "suspension"}
    assert set(CRITERION_SURFACES) == {
        "prediction_resolution_outcome", "obligation_status",
        "world_proposition_standing", "goal_status"}
    with pytest.raises(TypeError):
        REFERENCEABLE_FORMS["invented"] = None  # mappingproxy refuses
    with pytest.raises(TypeError):
        CRITERION_SURFACES["invented"] = None


def test_the_censused_vocabularies_equal_the_owners_enums() -> None:
    """PIN 7, THE DRIFT GUARD. The census holds the owners' state
    vocabularies as data; this pin is the reason that is safe - the moment
    any owner's enum moves, this reddens and the census is re-ruled rather
    than silently stale (Ruling 35's second-spelling hazard, answered in the
    pin layer)."""
    assert CRITERION_SURFACES["prediction_resolution_outcome"].states == tuple(
        m.value for m in PredictionOutcome)
    assert CRITERION_SURFACES["obligation_status"].states == tuple(
        m.value for m in ObligationRecordType)
    assert CRITERION_SURFACES["world_proposition_standing"].states == tuple(
        m.value for m in WorldStanding)
    assert CRITERION_SURFACES["goal_status"].states == tuple(
        m.value for m in GoalStatus)


def test_the_censused_id_forms_match_the_owners_mints() -> None:
    """PIN 7: each anchored pattern accepts what the owner's mint issues and
    refuses what it never could; the formless forms are DECLARED formless."""
    accepts = {
        "claim": "CLM-0001", "world_proposition": "WMP-0001",
        "prediction": "PRD-0001", "obligation": "OBL-0001",
        "episode": "EPI-0001", "goal": "GLC-0001",
        "suspension": "VT-1",
    }
    for form_key, good in accepts.items():
        form = reference_form(form_key)
        assert id_matches_form(form, good), (form_key, good)
        assert not id_matches_form(form, "JUNK-1"), form_key
        assert not id_matches_form(form, ""), form_key
    # ordinal growth past the pad is legal (the mint grows, never wraps)
    assert id_matches_form(reference_form("claim"), "CLM-123456")
    assert not id_matches_form(reference_form("claim"), "CLM-001")
    # the formless two: caller-given names, existence is the owner's question
    for formless in ("doctrine", "scar"):
        form = reference_form(formless)
        assert form.id_patterns == ()
    assert id_matches_form(reference_form("doctrine"), "Doctrine-0")
    assert id_matches_form(reference_form("scar"), "Δ17")  # Delta-17
    assert not id_matches_form(reference_form("scar"), "")


def test_the_census_module_is_vocabulary_not_machinery() -> None:
    """PIN 7: the census imports NOTHING from src/, opens nothing, and holds
    no store - `continuity.py`'s precedent, AST-pinned."""
    tree = ast.parse(CENSUS_MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not any(name.startswith("src") for name in imported), (
        f"the census reached into src/: {sorted(imported)}")
    opens = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open"]
    assert opens == [], "the census opened a file - data does not read stores"


def test_the_exclusions_are_declared_with_reasons() -> None:
    """PIN 7, the M8-a form: a surface nobody censused must not read as a
    surface that does not exist. The two import-pin deferrals are named."""
    assert {"doctrine_status", "scar_decay_state",
            "claim_state"} <= set(EXCLUDED_CRITERION_SURFACES)
    for mapping in (EXCLUDED_CRITERION_SURFACES, EXCLUDED_FORMS):
        for key, reason in mapping.items():
            assert isinstance(reason, str) and len(reason) > 40, (
                f"'{key}' is excluded without a reason worth the name")


def test_the_goal_join_is_a_read_surface_and_nothing_more() -> None:
    """PIN 7 + the prior import pin's spirit, extended to the new import: the
    ledger names exactly one thing from the goal module (`GoalLedger`) and
    touches exactly one attribute on it (`commitment_for`, a pure read). A
    second attribute appearing here is a widening that needs its own ruling."""
    tree = ast.parse(LEDGER_MODULE.read_text(encoding="utf-8"))
    from_goal = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and "goal" in (node.module or ""):
            from_goal.update(alias.name for alias in node.names)
    assert from_goal == {"GoalLedger"}
    touched = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Attribute)
                and node.value.attr == "goal_ledger"):
            touched.add(node.attr)
    assert touched == {"commitment_for"}, (
        f"the ledger touches {sorted(touched)} on the goal ledger - the "
        f"ruled join is the one pure read")
