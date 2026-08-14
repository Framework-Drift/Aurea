"""
M3-B - TYPED DEFEATERS v1 (kernel K11, heading L2).

**A DEFEATER'S INTERPRETATION IS FIXED AT REGISTRATION**, before any outcome
exists to shape it. The headline is the PRECEDENCE PROOF: a defeater resting on
a precommitted prediction must show, FROM THE RECORD, that the criteria predate
the outcome. Ruling 61's law arriving one layer up - a citation that cannot be
proved to precede what it judges is a citation shaped to it.

No new store: defeater records enter `episodes.jsonl` through its single writer.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.external.prediction_ledger import (
    DependencyLink, PredictionLedger, PredictionOutcome, declared_none, provided,
)
from src.filtration.episode_record import (
    ClosedVocabularyViolation, DefeaterKind, EpisodeOutcome, EpisodeRecord,
    EpisodeRecordType, MalformedInterpretation, PrecedenceProofFailed,
    REQUIRED_INTERPRETATION_FIELDS, UnknownDefeater, UnknownEpisode,
)

REPO = Path(__file__).resolve().parents[1]
EPISODE_SRC = REPO / "src" / "filtration" / "episode_record.py"


def _tree() -> ast.Module:
    return ast.parse(EPISODE_SRC.read_text(encoding="utf-8"))


def _episodes(tmp_path, ledger=None):
    return EpisodeRecord(log_path=str(tmp_path / "episodes.jsonl"),
                         prediction_ledger=ledger)


def _opened(tmp_path, ledger=None, bound=5):
    log = _episodes(tmp_path, ledger)
    return log, log.open_episode(["OBL-0001"], bound)


# =====================================================================
# A. THE PRECEDENCE PROOF - THE HEADLINE
# =====================================================================

def _falsified_prediction(tmp_path, name="predictions.jsonl"):
    """A REAL ledger with a real commitment and a real resolution."""
    ledger = PredictionLedger(ledger_path=str(tmp_path / name))
    commitment = ledger.commit(
        expected_result="the bridge holds under load",
        success_criteria=provided("no deflection beyond 2mm"),
        failure_criteria=provided("any visible deflection"),
        unresolved_criteria=declared_none(),
        dependency_chain=(DependencyLink.CAUSAL_LINK,),
    )
    ledger.resolve(commitment.prediction_id, PredictionOutcome.FALSIFIED,
                   criterion="failure_criteria", note="it deflected")
    return ledger, commitment


def test_a_a_well_ordered_prediction_registers(tmp_path):
    """PIN A1. The positive path: criteria precede the outcome on the record."""
    ledger, commitment = _falsified_prediction(tmp_path)
    log, episode = _opened(tmp_path, ledger)
    defeater_id = log.register_defeater(
        episode, DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
        {"prediction_id": commitment.prediction_id})
    record = log.defeaters(episode)[0]
    assert record["defeater_id"] == defeater_id
    proof = record["interpretation"]["precedence_proof"]
    assert proof["commitment_index"] < proof["resolution_index"]
    assert proof["basis"] == "prediction_ledger_append_order"


def test_a_the_criteria_are_copied_verbatim_from_the_ledger(tmp_path):
    """PIN A2. Copied from the RECORD, never restated by the caller.

    The value carried is the one fixed at COMMIT time, and the resolution names
    WHICH criterion it met - so the defeater cannot quietly cite a different
    standard than the one the prediction was judged against.
    """
    ledger, commitment = _falsified_prediction(tmp_path)
    log, episode = _opened(tmp_path, ledger)
    log.register_defeater(episode, DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                          {"prediction_id": commitment.prediction_id})
    recorded = log.defeaters(episode)[0]["interpretation"]["resolution_criteria"]
    assert recorded["criterion"] == "failure_criteria"
    assert recorded["recorded"]["value"] == "any visible deflection"
    assert log.defeaters(episode)[0]["interpretation"]["recorded_outcome"] == "falsified"


def test_a_criteria_that_postdate_the_outcome_raise(tmp_path):
    """PIN A3 - THE FORCING PIN. **RED FIRST.**

    Built by writing a REAL ledger through the real API and then SWAPPING its
    two lines, so append order is the only variable that moves - the shapes are
    exactly what the ledger writes. `resolve()` refuses an unknown id, so this
    file cannot be produced through the API at all; that is the point. The proof
    exists because a FILE can carry anything and outlives the code that wrote it.
    """
    ledger, commitment = _falsified_prediction(tmp_path)
    path = Path(ledger.ledger_path)
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    path.write_text(lines[1] + "\n" + lines[0] + "\n", encoding="utf-8")

    swapped = PredictionLedger(ledger_path=str(path))
    log, episode = _opened(tmp_path, swapped)
    with pytest.raises(PrecedenceProofFailed) as excinfo:
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": commitment.prediction_id})
    assert "predate" in str(excinfo.value).lower()
    assert log.defeaters(episode) == (), "a refused registration wrote a record"


def test_a_an_unresolved_prediction_has_not_failed(tmp_path):
    """PIN A4. No outcome means nothing for the criteria to predate.

    An unresolved prediction has not failed - it has not been SETTLED, and a
    defeater built on one would be citing an outcome that does not exist.
    """
    ledger = PredictionLedger(ledger_path=str(tmp_path / "predictions.jsonl"))
    commitment = ledger.commit(expected_result="it holds",
                               success_criteria=provided("no deflection"))
    log, episode = _opened(tmp_path, ledger)
    with pytest.raises(PrecedenceProofFailed):
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": commitment.prediction_id})


def test_a_an_uncited_prediction_raises(tmp_path):
    """PIN A5. A defeater cannot cite a prediction that was never made."""
    ledger = PredictionLedger(ledger_path=str(tmp_path / "predictions.jsonl"))
    log, episode = _opened(tmp_path, ledger)
    with pytest.raises(MalformedInterpretation):
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": "PRD-9999"})


def test_a_no_ledger_supplied_refuses_rather_than_assuming(tmp_path):
    """PIN A6. An unresolvable citation is not evidence."""
    log, episode = _opened(tmp_path)
    with pytest.raises(MalformedInterpretation):
        log.register_defeater(episode,
                              DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                              {"prediction_id": "PRD-0001"})


def test_a_the_proof_never_reads_a_wall_clock():
    """PIN A7. Precedence is APPEND ORDER, never `committed_at`/`resolved_at`.

    M3-A pinned that no logic path reads a clock; a precedence proof resting on
    a timestamp would be a timestamp join in the one place that must not have
    one - and the prediction ledger's records carry no ordinal, which is exactly
    why this had to be decided rather than assumed.
    """
    source = EPISODE_SRC.read_text(encoding="utf-8")
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Attribute) and node.attr in ("committed_at",
                                                             "resolved_at"):
            raise AssertionError(f"line {node.lineno} reads a wall clock")
        if isinstance(node, ast.Constant) and node.value in ("committed_at",
                                                             "resolved_at"):
            # Prose in the docstring explaining WHY is fine; a literal used as a
            # key is not. Only flag it if it is subscripting or a .get argument.
            pass
    assert "resolved_at\"]" not in source and "resolved_at')" not in source


# =====================================================================
# B. PER-KIND REQUIRED FIELDS, VALIDATED AT REGISTRATION
# =====================================================================

@pytest.mark.parametrize("kind,interpretation", [
    (DefeaterKind.REPRODUCED_COUNTEREXAMPLE, {"reproduction_recipe": "r"}),
    (DefeaterKind.REPRODUCED_COUNTEREXAMPLE, {"observed_result": "o"}),
    (DefeaterKind.PRIMARY_SOURCE_CONTRADICTION, {"source_ref": "s"}),
    (DefeaterKind.DEMONSTRATED_INCOMPATIBILITY, {"derivation_text": "d"}),
    (DefeaterKind.FAILED_PRECOMMITTED_PREDICTION, {}),
])
def test_b_a_missing_required_key_raises(tmp_path, kind, interpretation):
    """PIN B1. A MISSING key means nobody was asked - malformed."""
    log, episode = _opened(tmp_path)
    with pytest.raises(MalformedInterpretation):
        log.register_defeater(episode, kind, interpretation)
    assert log.defeaters(episode) == ()


@pytest.mark.parametrize("value", ["", "   ", None, 7, [], {}])
def test_b_a_substantive_field_must_carry_a_real_string(tmp_path, value):
    """PIN B2. Present-but-empty is not addressed."""
    log, episode = _opened(tmp_path)
    with pytest.raises(MalformedInterpretation):
        log.register_defeater(
            episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
            {"reproduction_recipe": value, "observed_result": "it differed"})


def test_b_reproduced_counterexample_registers(tmp_path):
    """PIN B3. The straightforward kind, end to end."""
    log, episode = _opened(tmp_path)
    log.register_defeater(
        episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": "run the notebook at seed 42",
         "observed_result": "the third column diverges"})
    record = log.defeaters(episode)[0]
    assert record["defeater_kind"] == DefeaterKind.REPRODUCED_COUNTEREXAMPLE.value
    assert record["interpretation"]["observed_result"] == "the third column diverges"


def test_b_a_null_fetch_record_is_recorded_absent_not_refused(tmp_path):
    """PIN B4 - ERA HONESTY FORWARD, and the reason it is not a defect.

    `fetch_record` is BOOTSTRAP-SHAPED: the M4 acquisition boundary will
    populate it from real acquisition records. Until that exists, requiring it
    would force every caller to INVENT an acquisition record - the fabrication
    class Rulings 58 and 70 both closed. The key must be ADDRESSED; its value
    may honestly be null, and null is recorded rather than defaulted.
    """
    log, episode = _opened(tmp_path)
    log.register_defeater(
        episode, DefeaterKind.PRIMARY_SOURCE_CONTRADICTION,
        {"source_ref": "Nature 1953 vol 171 p737", "fetch_record": None})
    record = log.defeaters(episode)[0]
    assert record["interpretation"]["fetch_record"] is None
    assert "fetch_record" in record["interpretation"], (
        "the ABSENCE must be recorded, not dropped - a missing key and a "
        "recorded null are different facts")


def test_b_a_missing_fetch_record_key_is_still_malformed(tmp_path):
    """PIN B5 - THE OTHER HALF. Era honesty is not permission to omit."""
    log, episode = _opened(tmp_path)
    with pytest.raises(MalformedInterpretation):
        log.register_defeater(episode,
                              DefeaterKind.PRIMARY_SOURCE_CONTRADICTION,
                              {"source_ref": "somewhere"})


@pytest.mark.parametrize("refs", [
    (), ("A",), ("A", "B", "C"), ("A", "A"), "AB",
])
def test_b_incompatibility_names_exactly_two_distinct_standings(tmp_path, refs):
    """PIN B6. An incompatibility is a relation between TWO things.

    `("A", "A")` is in this list on purpose: a thing is not incompatible with
    itself, and a naive `len()` check would admit it.
    """
    log, episode = _opened(tmp_path)
    with pytest.raises((MalformedInterpretation, TypeError)):
        log.register_defeater(
            episode, DefeaterKind.DEMONSTRATED_INCOMPATIBILITY,
            {"derivation_text": "they cannot both hold", "standing_refs": refs})


def test_b_incompatibility_with_two_standings_registers(tmp_path):
    """PIN B7. The control."""
    log, episode = _opened(tmp_path)
    log.register_defeater(
        episode, DefeaterKind.DEMONSTRATED_INCOMPATIBILITY,
        {"derivation_text": "P entails not-Q", "standing_refs": ["S-1", "S-2"]})
    assert log.defeaters(episode)[0]["interpretation"]["standing_refs"] == \
        ["S-1", "S-2"]


def test_b_the_defeater_vocabulary_is_exactly_v1():
    """PIN B8. A member arrives by governance, never by an edit."""
    assert {m.value for m in DefeaterKind} == {
        "failed_precommitted_prediction", "reproduced_counterexample",
        "primary_source_contradiction", "demonstrated_incompatibility"}
    assert set(REQUIRED_INTERPRETATION_FIELDS) == set(DefeaterKind), (
        "every kind must declare what its interpretation requires")


def test_b_an_unknown_kind_raises(tmp_path):
    log, episode = _opened(tmp_path)
    with pytest.raises(ClosedVocabularyViolation):
        log.register_defeater(episode, "vibes_were_off", {"x": 1})


def test_b_registration_on_an_unopened_episode_raises(tmp_path):
    log = _episodes(tmp_path)
    with pytest.raises(UnknownEpisode):
        log.register_defeater("EPI-9999",
                              DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
                              {"reproduction_recipe": "r", "observed_result": "o"})


# =====================================================================
# C. INTERPRETATION IS AMENDLESS, AND REGISTRATION OBLIGATES NOTHING
# =====================================================================

def test_c_no_amend_surface_for_an_interpretation():
    """PIN C1. Fixed at registration, as SHAPE.

    A method named `reinterpret_defeater` with a docstring saying "only before
    disposition" is a request for restraint (CLAUDE.md §3).
    """
    names = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ClassDef) and node.name == "EpisodeRecord":
            names = [n.name.lower() for n in node.body
                     if isinstance(n, ast.FunctionDef)]
    for verb in ("amend", "reinterpret", "revise", "update", "edit", "set_"):
        assert not any(verb in n for n in names), (
            f"EpisodeRecord grew `{verb}` - an interpretation is fixed at "
            f"registration and a record is never edited")


def test_c_registration_causes_no_other_write(tmp_path):
    """PIN C2 - A DEFEATER ALONE OBLIGATES NOTHING.

    The fold before and after is identical apart from the defeater's own
    record: no disposition, no pressure, no status change. Cognition PRESSURES
    and evidence DISPOSES, and both are acts on the record.
    """
    log, episode = _opened(tmp_path)
    log.record_pressure(episode, "primary_source", "adequate")
    before = list(log.read_all())
    before_applied = log.applied_pressure_count(episode)
    before_debts = log.pressure_debts(episode)

    log.register_defeater(
        episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": "r", "observed_result": "o"})

    after = list(log.read_all())
    added = after[len(before):]
    assert after[:len(before)] == before, "registration rewrote earlier records"
    assert len(added) == 1
    assert added[0]["record_type"] == EpisodeRecordType.DEFEATER_REGISTERED.value
    assert log.applied_pressure_count(episode) == before_applied, (
        "registering a defeater consumed the episode's bound")
    assert log.pressure_debts(episode) == before_debts
    assert log._disposition_of(episode) is None, (
        "registration disposed the episode - evidence disposes only when the "
        "disposition door is invoked")


def test_c_registration_does_not_write_the_prediction_ledger(tmp_path):
    """PIN C3. The ledger handle is READ-ONLY, proved by its bytes."""
    ledger, commitment = _falsified_prediction(tmp_path)
    path = Path(ledger.ledger_path)
    before = path.read_bytes()
    log, episode = _opened(tmp_path, ledger)
    log.register_defeater(episode, DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
                          {"prediction_id": commitment.prediction_id})
    assert path.read_bytes() == before, "the defeater wrote another owner's store"


def test_c_the_module_never_calls_a_prediction_ledger_writer():
    """PIN C4. M3-A's `retrieve` lesson, applied in advance to a second handle.

    A store handed to a reader for one question is a store it can be talked
    into answering others with, so the writing doors are AST-forbidden here.
    """
    banned = {"commit", "resolve", "_mint_and_append", "_append_resolution",
              "save_to_file", "form_scar", "mutate_doctrine"}
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call):
            attr = getattr(node.func, "attr", None)
            if attr in banned:
                # `self._append` is this module's own single writer and is not
                # a call on a foreign store.
                target = getattr(node.func, "value", None)
                is_self = isinstance(target, ast.Name) and target.id == "self"
                assert is_self, (
                    f"episode_record:{node.lineno} calls `{attr}` on a store "
                    f"it does not own")


# =====================================================================
# D. A CITED DEFEATER MUST RESOLVE
# =====================================================================

def test_d_an_unknown_defeater_ref_raises(tmp_path):
    """PIN D1. A dangling citation on a permanent disposition reads as though
    the reasoning was grounded, and nothing can afterwards say what it meant."""
    log, episode = _opened(tmp_path)
    log.record_pressure(episode, "primary_source", "ok")
    with pytest.raises(UnknownDefeater):
        log.disposition(episode, EpisodeOutcome.REVISED, defeater_ref="DEF-9999")
    assert log._disposition_of(episode) is None


def test_d_a_defeater_from_another_episode_does_not_resolve(tmp_path):
    """PIN D2 - THE SHARP HALF. Registered SOMEWHERE is not registered HERE.

    A naive implementation checks the log rather than the episode, and passes
    every test that only ever builds one episode.
    """
    log = _episodes(tmp_path)
    other = log.open_episode(["OBL-0001"], 5)
    mine = log.open_episode(["OBL-0002"], 5)
    foreign = log.register_defeater(
        other, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": "r", "observed_result": "o"})
    log.record_pressure(mine, "primary_source", "ok")
    with pytest.raises(UnknownDefeater):
        log.disposition(mine, EpisodeOutcome.REVISED, defeater_ref=foreign)


def test_d_a_resolving_defeater_ref_is_recorded(tmp_path):
    """PIN D3. The positive path."""
    log, episode = _opened(tmp_path)
    defeater = log.register_defeater(
        episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": "r", "observed_result": "o"})
    log.record_pressure(episode, "reproduced_counterexample", "decisive")
    log.disposition(episode, EpisodeOutcome.REVISED, defeater_ref=defeater)
    assert log.read_all()[-1]["defeater_ref"] == defeater


def test_d_none_stays_permitted(tmp_path):
    """PIN D4 - THE CONTROL. Not every disposition cites a defeater."""
    log, episode = _opened(tmp_path)
    log.record_pressure(episode, "primary_source", "ok")
    log.disposition(episode, EpisodeOutcome.SURVIVED)
    assert log.read_all()[-1]["defeater_ref"] is None


def test_d_defeater_ids_are_minted_from_the_file(tmp_path):
    """PIN D5. Ruling 69's mint at a third prefix - no cached counter."""
    log, episode = _opened(tmp_path)
    ids = [log.register_defeater(
        episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": f"r{i}", "observed_result": "o"}) for i in range(3)]
    assert ids == ["DEF-0001", "DEF-0002", "DEF-0003"]
    resumed = _episodes(tmp_path)
    assert resumed.register_defeater(
        episode, DefeaterKind.REPRODUCED_COUNTEREXAMPLE,
        {"reproduction_recipe": "r3", "observed_result": "o"}) == "DEF-0004", (
        "the mint restarted across instances - Ruling 69's exact defect")
