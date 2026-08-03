"""
test_autonomy_index.py - Tests for PromptingAutonomyEngine

Covers:
- Scar maturity ratio (matured vs active vs locked-excluded)
- Echo fermentation ratio (doctrine_link presence)
- Composite index weighting and the compass-stability cap
- meets_threshold() boundary behavior against the ruled 0-100 scale
- Empty-state behavior (no scars / no echoes yet)

Uses in-memory ScarLogicCore / EchoMemory instances pointed at throwaway
tmp_path files so this never touches real data/scars.json or
data/echoes.jsonl.
"""

import pytest

from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.echo_memory import EchoMemory
from src.utils.models import Scar, Echo
from src.expansion.tether.autonomy_index import (
    PromptingAutonomyEngine,
    SCAR_MATURITY_WEIGHT,
    COMPASS_STABILITY_WEIGHT,
    ECHO_FERMENTATION_WEIGHT,
)


@pytest.fixture
def scar_core(tmp_path):
    return ScarLogicCore(filepath=str(tmp_path / "scars.json"))


@pytest.fixture
def echo_memory(tmp_path):
    return EchoMemory(filepath=str(tmp_path / "echoes.jsonl"))


@pytest.fixture
def engine(scar_core, echo_memory):
    return PromptingAutonomyEngine(scar_core, echo_memory)


def make_scar(id_, decay_state="active"):
    return Scar(id=id_, name=id_, origin="test", decay_state=decay_state)


def make_echo(id_, doctrine_link=None):
    from datetime import datetime
    return Echo(
        id=id_,
        content="test content",
        resonance_score=0.5,
        created_at=datetime.now(),
        doctrine_link=doctrine_link,
    )


# ---------- Empty state ----------

def test_empty_state_index_is_zero(engine):
    result = engine.compute()
    assert result.index == 0.0
    assert result.scar_maturity is None
    assert result.echo_fermentation is None
    assert result.compass_stability is None
    assert result.scars_total == 0
    assert result.echoes_total == 0


def test_empty_state_warns_on_both_missing_inputs(engine):
    result = engine.compute()
    joined = " ".join(result.warnings)
    assert "scar_maturity" in joined
    assert "echo_fermentation" in joined
    assert "compass_stability" in joined


# ---------- Scar maturity ----------

def test_scar_maturity_all_active_scores_zero(scar_core, engine):
    for i in range(5):
        scar_core.add_scar(make_scar(f"S{i}", decay_state="active"))
    result = engine.compute()
    assert result.scar_maturity == 0.0
    assert result.scars_matured == 0
    assert result.scars_total == 5


def test_scar_maturity_all_matured_scores_hundred(scar_core, engine):
    for i, state in enumerate(["retired", "dormant", "fossil"]):
        scar_core.add_scar(make_scar(f"S{i}", decay_state=state))
    result = engine.compute()
    assert result.scar_maturity == 100.0
    assert result.scars_matured == 3


def test_scar_maturity_mixed_ratio(scar_core, engine):
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    scar_core.add_scar(make_scar("S1", decay_state="active"))
    scar_core.add_scar(make_scar("S2", decay_state="active"))
    scar_core.add_scar(make_scar("S3", decay_state="active"))
    result = engine.compute()
    # 1 matured / 4 counted = 25.0
    assert result.scar_maturity == 25.0
    assert result.scars_matured == 1
    assert result.scars_total == 4


def test_locked_scars_excluded_from_ratio(scar_core, engine):
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    scar_core.add_scar(make_scar("S1", decay_state="active"))
    scar_core.add_scar(make_scar("S2", decay_state="locked"))
    scar_core.add_scar(make_scar("S3", decay_state="locked"))
    result = engine.compute()
    # locked scars excluded from both numerator and denominator:
    # 1 matured / 2 counted (retired + active only) = 50.0
    assert result.scar_maturity == 50.0
    assert result.scars_locked_excluded == 2
    assert result.scars_total == 4  # total still reflects all scars on record


def test_only_locked_scars_scores_none(scar_core, engine):
    scar_core.add_scar(make_scar("S0", decay_state="locked"))
    result = engine.compute()
    assert result.scar_maturity is None
    assert result.scars_locked_excluded == 1


# ---------- Echo fermentation ----------

def test_echo_fermentation_none_linked_scores_zero(echo_memory, engine):
    for i in range(3):
        echo_memory.add_echo(make_echo(f"E{i}", doctrine_link=None))
    result = engine.compute()
    assert result.echo_fermentation == 0.0
    assert result.echoes_fermented == 0


def test_echo_fermentation_all_linked_scores_hundred(echo_memory, engine):
    for i in range(3):
        echo_memory.add_echo(make_echo(f"E{i}", doctrine_link=f"Doctrine-{i}"))
    result = engine.compute()
    assert result.echo_fermentation == 100.0
    assert result.echoes_fermented == 3


def test_echo_fermentation_mixed_ratio(echo_memory, engine):
    echo_memory.add_echo(make_echo("E0", doctrine_link="Doctrine-0"))
    echo_memory.add_echo(make_echo("E1", doctrine_link=None))
    echo_memory.add_echo(make_echo("E2", doctrine_link=None))
    echo_memory.add_echo(make_echo("E3", doctrine_link=None))
    result = engine.compute()
    assert result.echo_fermentation == 25.0


# ---------- Composite index & compass cap ----------

def test_index_is_weighted_sum_excluding_compass(scar_core, echo_memory, engine):
    # Fully matured scars, fully fermented echoes -> both components 100
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    echo_memory.add_echo(make_echo("E0", doctrine_link="Doctrine-0"))

    result = engine.compute()

    expected = 100.0 * SCAR_MATURITY_WEIGHT + 100.0 * ECHO_FERMENTATION_WEIGHT
    assert result.index == pytest.approx(expected, abs=0.01)
    # Compass contributes nothing - index should never exceed the
    # non-compass weight ceiling regardless of how perfect the other
    # two components are.
    ceiling = (SCAR_MATURITY_WEIGHT + ECHO_FERMENTATION_WEIGHT) * 100
    assert result.index <= ceiling + 0.01


def test_compass_stability_always_none_and_warned(scar_core, echo_memory, engine):
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    echo_memory.add_echo(make_echo("E0", doctrine_link="Doctrine-0"))
    result = engine.compute()
    assert result.compass_stability is None
    assert any("compass_stability" in w for w in result.warnings)


def test_index_never_exceeds_capped_ceiling_even_at_perfect_inputs(
    scar_core, echo_memory, engine
):
    for i in range(10):
        scar_core.add_scar(make_scar(f"S{i}", decay_state="fossil"))
        echo_memory.add_echo(make_echo(f"E{i}", doctrine_link=f"Doctrine-{i}"))
    result = engine.compute()
    ceiling = (SCAR_MATURITY_WEIGHT + ECHO_FERMENTATION_WEIGHT) * 100
    assert result.index == pytest.approx(ceiling, abs=0.01)
    assert result.index < 100.0  # can never reach full scale without compass


# ---------- meets_threshold ----------

def test_meets_threshold_true_when_index_at_or_above(scar_core, echo_memory, engine):
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    echo_memory.add_echo(make_echo("E0", doctrine_link="Doctrine-0"))
    result = engine.compute()
    # index will be 65.0 given full scar+echo maturity, 0 compass
    assert result.meets_threshold(5) is True
    assert result.meets_threshold(result.index) is True  # boundary: equal counts as met


def test_meets_threshold_false_when_below(scar_core, echo_memory, engine):
    scar_core.add_scar(make_scar("S0", decay_state="active"))
    echo_memory.add_echo(make_echo("E0", doctrine_link=None))
    result = engine.compute()
    assert result.index == 0.0
    assert result.meets_threshold(5) is False


def test_meets_threshold_respects_seed_example_value(scar_core, echo_memory, engine):
    """
    Sanity check against the corpus's own example:
    SEP_ModuleSeed { ... unlock_at_tether_index: 5 ... }
    A system with even a small amount of survived, integrated history
    should clear this intentionally-low early threshold.
    """
    scar_core.add_scar(make_scar("S0", decay_state="retired"))
    scar_core.add_scar(make_scar("S1", decay_state="active"))
    echo_memory.add_echo(make_echo("E0", doctrine_link="Doctrine-0"))
    result = engine.compute()
    assert result.meets_threshold(5) is True
