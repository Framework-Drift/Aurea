"""
test_sae.py - behavioral coverage for the Self-Authorship Engine (Docket M, item 2).

Docket K found sae.py had ZERO behavioral test coverage: the Self-Mutation
Ceiling could be raised 3 -> 4, and the stabilization-event gate could be fully
inverted (garbage event types closing the epoch, real ones refused), with the
whole suite green. The ceiling is what stands between AUREA and unbounded
self-modification per epoch (Ruling 5 / T4-01); an epoch that closes on the
wrong trigger is a fresh mutation budget granted without anything settling.

These tests drive the real SAE against a real (tmp-pathed) Codex. No mocks in
the authorization path. Magnitudes referenced (ceiling 3) are CANON - nothing
here is coined. DO NOT weaken these tests; red means fix the code.
"""

from datetime import datetime

import pytest

from src.doctrine.codex import Codex
from src.expansion.sae import (SELF_MUTATION_CEILING, SAE, CeilingExceeded,
                               MutationClass)
from src.utils.models import Doctrine


@pytest.fixture
def sae(tmp_path):
    """A real SAE over a real, empty, tmp-pathed Codex (no repo data touched)."""
    return SAE(codex=Codex(filepath=str(tmp_path / "doctrines.json")))


def _spend_full_budget(sae):
    """Consume the whole epoch budget across ALL THREE counted classes (T4-01:
    counting only the two mutate_* calls left module generation uncapped)."""
    sae.mutate_reflex("R-1", {"threshold": 0.8}, collapse_lineage="Δ-a")
    sae.authorize_module_generation("M-1", collapse_lineage="Δ-b")
    sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-c", target_id="D-1")


# =====================================================================
# THE CEILING (canon magnitude 3 - Docket K survivor 1a, now pinned)
# =====================================================================

def test_ceiling_three_authorizations_then_fourth_raises():
    """Three mutation events per symbolic epoch, across the three counted
    classes. The FOURTH raises CeilingExceeded - the refusal IS the answer,
    not an error to retry past."""
    assert SELF_MUTATION_CEILING == 3, (
        "the Self-Mutation Ceiling is CANON magnitude 3 - changing it requires "
        "an architect ruling, not an edit")

    engine = SAE(codex=Codex(filepath="__nonexistent__/never_written.json"))
    _spend_full_budget(engine)
    assert engine.epoch_count == 3

    with pytest.raises(CeilingExceeded):
        engine.mutate_reflex("R-2", {}, collapse_lineage="Δ-d")
    assert engine.epoch_count == 3, "a refused authorization spends nothing"


def test_module_retirement_is_ceiling_exempt(sae):
    """T4-03: retirement removes capacity, it does not run away. A system that
    has spent its budget must still be able to dismantle what is hurting it."""
    _spend_full_budget(sae)
    auth = sae.authorize_module_retirement("M-old", collapse_lineage="Δ-e")
    assert auth is not None
    assert sae.epoch_count == 3, "retirement did not count against the ceiling"


# =====================================================================
# THE STABILIZATION GATE (Docket K survivor 1b, now pinned)
# =====================================================================

def test_wrong_typed_event_does_not_close_the_epoch(sae):
    """Elapsed time is not a stabilization event, and neither is wanting more
    budget. A garbage event type resets NOTHING."""
    _spend_full_budget(sae)
    epoch_before = sae.epoch

    assert sae.stabilization_event("elapsed_time") is False
    assert sae.stabilization_event("please") is False
    assert sae.epoch == epoch_before
    assert sae.epoch_count == 3, "the spent budget did not come back"
    with pytest.raises(CeilingExceeded):
        sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-f", target_id="D-2")


def test_fermentation_on_an_untouched_lineage_does_not_close_the_epoch(sae):
    """Fermentation on a lineage SAE never touched proves nothing about SAE's
    changes - correct type, wrong lineage, no reset."""
    _spend_full_budget(sae)
    epoch_before = sae.epoch

    assert sae.stabilization_event(
        "scar_fermentation", lineage="Δ-never-touched") is False
    assert sae.epoch == epoch_before
    assert sae.epoch_count == 3


def test_fermentation_on_a_touched_lineage_closes_the_epoch(sae):
    """The one legitimate path pinned here: correct type AND a lineage SAE
    actually touched. The epoch advances, the count resets, and the budget is
    live again - because something AUREA changed has SETTLED."""
    _spend_full_budget(sae)
    epoch_before = sae.epoch

    assert sae.stabilization_event("scar_fermentation", lineage="Δ-a") is True
    assert sae.epoch == epoch_before + 1
    assert sae.epoch_count == 0

    # The fresh budget is real: an authorization succeeds again.
    auth = sae.authorize(MutationClass.MUTATE_DOCTRINE, "Δ-g", target_id="D-3")
    assert auth.epoch == epoch_before + 1
