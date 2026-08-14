"""
M3-C - STANDING PROFILES (heading L6 / L7 / L12).

**THE HEADLINE IS SECTION C**: a profile whose survivals are all
MODEL_ADVERSARIAL fails to authorize an empirical decision, whatever its counts.
Weak-pressure farming made UNPROFITABLE rather than merely detectable - if
argument against a model could accumulate into empirical standing, the cheapest
pressure would be the most rewarding to farm.

Standing is a DERIVATION, never a store: purity is pinned as shape.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.doctrine.standing_profile import (
    DERIVATION_V1_EMPIRICAL_GATE, DERIVATION_V1_INTERPRETIVE_STANDING,
    DERIVATION_VERSION, DERIVATIONS, EPISODE_OUTCOMES, PRESSURE_CLASSES,
    STRONG_PRESSURE_CLASSES, WEAK_PRESSURE_CLASSES, UnknownDerivation,
    authorize, profile,
)
from src.filtration.episode_record import (
    EpisodeOutcome, EpisodeRecord, PressureClass,
)
from src.filtration.obligation_ledger import ObligationLedger, TargetKind

REPO = Path(__file__).resolve().parents[1]
PROFILE_SRC = REPO / "src" / "doctrine" / "standing_profile.py"


def _tree() -> ast.Module:
    return ast.parse(PROFILE_SRC.read_text(encoding="utf-8"))


class _FakeCodex:
    fossils: dict = {}

    def get(self, doctrine_id):
        return object()


def _world(tmp_path):
    led = ObligationLedger(ledger_path=str(tmp_path / "obligations.jsonl"),
                           codex=_FakeCodex())
    log = EpisodeRecord(log_path=str(tmp_path / "episodes.jsonl"))
    return led, log


def _episode_for(led, log, target_id, claim, bound, classes, outcome,
                 defeaters=()):
    """Admit an obligation, open an episode against it, pressure it, dispose."""
    obligation = led.admit("architect", TargetKind.DOCTRINE, target_id, claim)
    episode = log.open_episode([obligation.obligation_id], bound)
    for index, pressure_class in enumerate(classes):
        log.record_pressure(episode, pressure_class, "as recorded",
                            defeaters if index == 0 else ())
    if outcome is not None:
        log.disposition(episode, outcome)
    return obligation.obligation_id, episode


# =====================================================================
# A. PURITY - IT IS A VIEW OR IT IS WRONG
# =====================================================================

def test_a_the_module_imports_nothing_from_src():
    """PIN A1 - R79'S SHAPE. Stdlib-only.

    The purity is what makes "never writes to anything it reads" STRUCTURAL: a
    module that cannot reach a store cannot be talked into repairing one.
    """
    for node in ast.walk(_tree()):
        module = ""
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
        elif isinstance(node, ast.Import):
            module = node.names[0].name
        assert not module.startswith("src"), (
            f"standing_profile imports `{module}` - it is stdlib-only by ruling")


def test_a_no_write_path_of_any_kind_exists():
    """PIN A2 - THE STOP. Any write path appearing here is the defect itself."""
    banned_calls = {"open", "durable_append_text", "atomic_write_text",
                    "atomic_write_json", "write_text", "write_bytes", "mkdir",
                    "dump", "unlink", "remove"}
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            assert name not in banned_calls, (
                f"standing_profile:{node.lineno} calls `{name}` - it is a view")


def test_a_no_persistence_surface_on_the_records():
    """PIN A3. No `as_dict`/`save`/`to_json`: the first thing anyone would do
    with a serializable profile is cache it, and a cached standing is Ruling
    63's stale authority at the layer that decides things."""
    names = [n.name.lower() for n in ast.walk(_tree())
             if isinstance(n, ast.FunctionDef)]
    for verb in ("as_dict", "save", "persist", "to_json", "serialize", "cache",
                 "store", "write"):
        assert not any(verb in n for n in names), f"a `{verb}` surface appeared"


def test_a_nothing_in_src_consumes_the_profile():
    """PIN A4. Zero internal callers - Ruling 77's property at this layer:
    the measurement must be possible without the measurement becoming a
    standing. Goes RED the day a consumer arrives, which is when it needs a
    ruling."""
    consumers = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if path == PROFILE_SRC:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and "standing_profile" in (
                    node.module or ""):
                consumers.append(path.relative_to(REPO).as_posix())
    assert consumers == [], f"{consumers} consume standing profiles"


def test_a_no_numeric_threshold_anywhere():
    """PIN A5 - §9 bar #5. The gate is keyed on WHAT KIND survived, never how
    much. The only literals in the derivation are 0 and 1 - an emptiness test
    and an existence test, neither of which is a magnitude."""
    literals = {n.value for n in ast.walk(_tree())
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool)}
    assert literals <= {0, 1}, f"a coined magnitude appeared: {sorted(literals)}"


# =====================================================================
# B. THE MIRRORED VOCABULARY IS COMPARED, NOT TRUSTED
# =====================================================================

def test_b_the_pressure_class_mirror_equals_the_real_enum():
    """PIN B1 - THE DRIFT DETECTOR.

    Purity forbids importing `PressureClass` here, so its values are mirrored -
    a second definition, which R79 named as a hazard. The answer is not to
    prevent the duplication but to DETECT it, every run.
    """
    assert set(PRESSURE_CLASSES) == {m.value for m in PressureClass}, (
        "the mirrored pressure-class vocabulary has drifted from the enum")


def test_b_the_outcome_mirror_equals_the_real_enum():
    assert set(EPISODE_OUTCOMES) == {m.value for m in EpisodeOutcome}


def test_b_the_strong_weak_partition_is_total_and_disjoint():
    """PIN B3 - THE ONE THAT MATTERS MOST WHEN THE VOCABULARY GROWS.

    A pressure class added to the enum without being placed on one side would
    land in NEITHER, and a survival under it would authorize nothing while
    looking like coverage. This forces the placement to be a decision.
    """
    strong, weak = set(STRONG_PRESSURE_CLASSES), set(WEAK_PRESSURE_CLASSES)
    assert strong & weak == set(), "a class is both strong and weak"
    assert strong | weak == {m.value for m in PressureClass}, (
        "a pressure class sits on NEITHER side of the strong/weak partition - "
        "place it deliberately; landing in neither is silent non-coverage")


# =====================================================================
# C. THE HEADLINE - MODEL-ONLY PRESSURE FAILS TO AUTHORIZE
# =====================================================================

def test_c_model_adversarial_only_fails_the_empirical_gate(tmp_path):
    """PIN C1 - THE FORCING PIN OF THIS SLICE. **RED FIRST.**

    SIX survivals, every one of them under MODEL_ADVERSARIAL, zero debts. The
    profile is as strong as argument alone can ever make it, and it does not
    authorize - structurally, whatever the counts.
    """
    led, log = _world(tmp_path)
    for index in range(6):
        _episode_for(led, log, "Doctrine-0", f"claim {index}", 5,
                     [PressureClass.MODEL_ADVERSARIAL], EpisodeOutcome.SURVIVED)

    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert standing.survivals_under(WEAK_PRESSURE_CLASSES) == 6
    assert standing.survivals_under(STRONG_PRESSURE_CLASSES) == 0

    result = authorize(standing, "empirical", DERIVATION_V1_EMPIRICAL_GATE)
    assert result.authorized is False
    assert any("strong pressure class" in line for line in result.basis)


def test_c_one_strong_survival_authorizes(tmp_path):
    """PIN C2 - THE CONTROL. Without it the rule is satisfiable by an
    implementation that refuses everything."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert authorize(standing, "empirical",
                     DERIVATION_V1_EMPIRICAL_GATE).authorized is True


@pytest.mark.parametrize("pressure_class", [
    PressureClass.PRECOMMITTED_PREDICTION, PressureClass.PRIMARY_SOURCE,
    PressureClass.REPRODUCED_COUNTEREXAMPLE, PressureClass.FORMAL_DERIVATION])
def test_c_every_strong_class_can_authorize(tmp_path, pressure_class):
    """PIN C3. All four, so none is strong by accident of the test set."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5, [pressure_class],
                 EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert authorize(standing, "empirical",
                     DERIVATION_V1_EMPIRICAL_GATE).authorized is True


def test_c_an_outstanding_debt_blocks_the_empirical_gate(tmp_path):
    """PIN C4 - K11. A defeater noticed and never exercised is testing the
    claim did not receive, and it blocks even a strong survival."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED,
                 defeaters=["an unexercised counterexample"])
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert len(standing.outstanding_debts) == 1
    result = authorize(standing, "empirical", DERIVATION_V1_EMPIRICAL_GATE)
    assert result.authorized is False
    assert any("pressure debts" in line for line in result.basis)


def test_c_model_only_does_authorize_interpretive_standing(tmp_path):
    """PIN C5 - THE OTHER HALF, and it is what makes the refusal a CUT rather
    than a blanket. Argumentative survival is real; it grants INTERPRETIVE
    standing only."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.MODEL_ADVERSARIAL], EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert authorize(standing, "interpretive",
                     DERIVATION_V1_INTERPRETIVE_STANDING).authorized is True
    assert authorize(standing, "empirical",
                     DERIVATION_V1_EMPIRICAL_GATE).authorized is False


def test_c_a_non_survival_authorizes_nothing(tmp_path):
    """PIN C6. COLLAPSED is not coverage."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.COLLAPSED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    for derivation in DERIVATIONS:
        assert authorize(standing, "any", derivation).authorized is False


def test_c_the_result_names_its_derivation_and_version(tmp_path):
    """PIN C7 - L7. A compression that cannot be re-derived is not auditable."""
    led, log = _world(tmp_path)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    result = authorize(standing, "empirical", DERIVATION_V1_EMPIRICAL_GATE)
    assert result.derivation == DERIVATION_V1_EMPIRICAL_GATE
    assert result.derivation_version == DERIVATION_VERSION
    assert result.decision_kind == "empirical"
    assert result.basis, "an authorization with no recorded basis is a verdict"


def test_c_an_unknown_derivation_refuses(tmp_path):
    """PIN C8. It does not default - the default anyone reaches for is the
    permissive one."""
    led, log = _world(tmp_path)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    with pytest.raises(UnknownDerivation):
        authorize(standing, "empirical", "vibes_v2")


# =====================================================================
# D. THE FOLD - NEGATIVE SPACE AND DETERMINISM
# =====================================================================

def test_d_the_profile_joins_only_through_recorded_ids(tmp_path):
    """PIN D1. An episode belongs because an id says so, or not at all."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "mine", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    _episode_for(led, log, "Doctrine-9", "theirs", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert len(standing.episode_ids) == 1
    assert standing.survivals_under(STRONG_PRESSURE_CLASSES) == 1


def test_d_negative_space_records_deferred_obligations(tmp_path):
    """PIN D2. Set aside, with the reason and the ordinal - not merely absent."""
    led, log = _world(tmp_path)
    obligation = led.admit("architect", TargetKind.DOCTRINE, "Doctrine-0", "c")
    led.defer(obligation.obligation_id, "awaiting a primary source", "SEQ-000900")
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert standing.negative_space.deferred_obligations == (
        (obligation.obligation_id, "awaiting a primary source", "SEQ-000900"),)


def test_d_negative_space_records_classes_never_exercised(tmp_path):
    """PIN D3. What was never tried is standing information."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    never = set(standing.negative_space.unexercised_pressure_classes)
    assert PressureClass.PRIMARY_SOURCE.value not in never
    assert PressureClass.MODEL_ADVERSARIAL.value in never
    assert never == set(PRESSURE_CLASSES) - {PressureClass.PRIMARY_SOURCE.value}


def test_d_a_shallow_survival_stays_distinguishable_forever(tmp_path):
    """PIN D4 - M3-A'S COUNTING RULE PAYING OUT.

    An episode that ran out of room is recorded as exhausted WITH its bound, so
    a reader can always tell it from one that withstood testing.
    """
    led, log = _world(tmp_path)
    obligation = led.admit("architect", TargetKind.DOCTRINE, "Doctrine-0", "c")
    episode = log.open_episode([obligation.obligation_id], 2)
    log.record_pressure(episode, PressureClass.MODEL_ADVERSARIAL, "argued")
    log.record_pressure(episode, PressureClass.MODEL_ADVERSARIAL, "argued again")
    log.disposition(episode, EpisodeOutcome.UNRESOLVED_AT_BOUND)

    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert standing.negative_space.exhausted_episodes == ((episode, 2),)
    assert standing.inquiry_depths == ((episode, 2),)
    for derivation in DERIVATIONS:
        assert authorize(standing, "any", derivation).authorized is False, (
            "an exhausted episode authorized something - running out of room "
            "is not survival")


def test_d_one_episode_credits_every_class_it_applied(tmp_path):
    """PIN D5. The disposition is the episode's; each class it applied stands
    behind it."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE, PressureClass.MODEL_ADVERSARIAL],
                 EpisodeOutcome.SURVIVED)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert standing.survivals_under(STRONG_PRESSURE_CLASSES) == 1
    assert standing.survivals_under(WEAK_PRESSURE_CLASSES) == 1


def test_d_the_fold_is_deterministic_and_restart_invariant(tmp_path):
    """PIN D6. Same records, same profile - across instances and processes.

    Restart invariance is not a bonus here: a standing that changed shape after
    a restart would be a standing nobody could cite.
    """
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "a", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED,
                 defeaters=["d1", "d2"])
    _episode_for(led, log, "Doctrine-0", "b", 3,
                 [PressureClass.MODEL_ADVERSARIAL], EpisodeOutcome.REVISED)

    first = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    again = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert first == again, "the fold is not deterministic within a process"

    resumed_led = ObligationLedger(ledger_path=str(tmp_path / "obligations.jsonl"))
    resumed_log = EpisodeRecord(log_path=str(tmp_path / "episodes.jsonl"))
    assert profile(TargetKind.DOCTRINE, "Doctrine-0", resumed_log,
                   resumed_led) == first, "the profile changed across a restart"


def test_d_an_empty_world_profiles_to_nothing(tmp_path):
    """PIN D7. No records is not an error, and it authorizes nothing."""
    led, log = _world(tmp_path)
    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    assert standing.episode_ids == () and standing.obligation_ids == ()
    assert set(standing.negative_space.unexercised_pressure_classes) == \
        set(PRESSURE_CLASSES)
    assert authorize(standing, "empirical",
                     DERIVATION_V1_EMPIRICAL_GATE).authorized is False


def test_d_the_profile_writes_to_nothing_it_reads(tmp_path):
    """PIN D8 - THE STOP, PINNED BEHAVIOURALLY. Bytes before == bytes after."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    obligations = Path(tmp_path / "obligations.jsonl").read_bytes()
    episodes = Path(tmp_path / "episodes.jsonl").read_bytes()

    standing = profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
    authorize(standing, "empirical", DERIVATION_V1_EMPIRICAL_GATE)

    assert Path(tmp_path / "obligations.jsonl").read_bytes() == obligations
    assert Path(tmp_path / "episodes.jsonl").read_bytes() == episodes


def test_d_records_may_arrive_as_a_plain_sequence(tmp_path):
    """PIN D9. O5's shape: already-read records, so a caller may hand a slice
    it read itself. This module opens nothing."""
    led, log = _world(tmp_path)
    _episode_for(led, log, "Doctrine-0", "one", 5,
                 [PressureClass.PRIMARY_SOURCE], EpisodeOutcome.SURVIVED)
    assert profile(TargetKind.DOCTRINE, "Doctrine-0",
                   list(log.read_all()), list(led.read_all())) == \
        profile(TargetKind.DOCTRINE, "Doctrine-0", log, led)
