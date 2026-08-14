"""
M3-D COMMIT 2 - THE EPISODE PATH (Ruling M3-D-alpha).

`SBSRE.process` is no longer the decision path. The contradiction chamber runs
on the durable obligation + episode record: same three inputs, same
`compute_loop_limit` bound, same overrides, same consequences - and a record
that survives the process instead of dying with it.

THE FOUR PROPERTIES THIS FILE HOLDS:
  * every carried contradiction ADMITS before it is considered;
  * the bound is FIXED AT OPEN and any early stop is RECORDED (census §4's
    subsumption of invariant 21: strictly stronger than shrink-only);
  * the passes are SHAPING ACTS, never pressure, so SURVIVED is unproducible
    here and no weak-pressure farming is possible (K11);
  * exhaustion ends UNRESOLVED_AT_BOUND - a shallow carry stays distinguishable
    from a settled one forever.
"""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.filtration.episode_record import EpisodeOutcome, EpisodeRecordType
from src.filtration.obligation_ledger import ObligationRecordType, TargetKind

REPO = Path(__file__).resolve().parents[1]
CORE_SRC = REPO / "src" / "aurea_core.py"

CONTRADICTION = "Fracture Carried is false."
SCARRING = "Honesty is pointless."


def _irreconcilable(contradiction, cycle):
    return "irreconcilable"


def _episode_of(core, result):
    return result["contradiction"]["episode_id"]


# =====================================================================
# A. ADMISSION PRECEDES CONSIDERATION
# =====================================================================

def test_a_a_carried_contradiction_admits_first():
    """PIN A1. The obligation exists, targets the CLAIM, and the episode is
    opened against it."""
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    block = result["contradiction"]
    assert block["admission"] == "admitted"

    opened = [r for r in core.obligations.read_all()
              if r["record_type"] == ObligationRecordType.OPEN.value]
    assert len(opened) == 1
    assert opened[0]["target_kind"] == TargetKind.CLAIM.value
    assert opened[0]["target_id"] == result["claim_id"]
    assert opened[0]["obligation_id"] == block["obligation_id"]


def test_a_the_episode_names_the_obligation_it_was_opened_against():
    """PIN A2. The join is a RECORDED id, never inferred."""
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    block = result["contradiction"]
    opened = [r for r in core.episodes.read_all()
              if r["record_type"] == EpisodeRecordType.EPISODE_OPENED.value]
    assert len(opened) == 1
    assert opened[0]["episode_id"] == block["episode_id"]
    assert opened[0]["obligation_ids"] == [block["obligation_id"]]


def test_a_the_obligation_leaves_the_standing_set_when_worked():
    """PIN A3. An obligation being worked is not one waiting."""
    core = AureaCore()
    core.process_input(CONTRADICTION)
    assert core.obligations.open_items() == []


def test_a_a_claim_that_never_reaches_the_chamber_admits_nothing():
    """PIN A4 - THE CONTROL. Admission happens at the chamber, not at ingress.

    A claim that passes collapse never enters the contradiction path, so no
    obligation is owed about it.
    """
    core = AureaCore()
    core.process_input("The sky is blue.")
    assert core.obligations.read_all() == ()
    assert core.episodes.read_all() == ()


# =====================================================================
# B. THE BOUND IS FIXED AT OPEN, AND THE PASSES ARE SHAPING ACTS
# =====================================================================

def test_b_the_recorded_bound_is_the_clamp_value():
    """PIN B1 - INVARIANT 14's EPISODE-OPEN BIND.

    `compute_loop_limit` still derives the bound (census §4: invariant 13's
    target is preserved), and the value it returns is what reaches
    `open_episode`. This is the binding the census names.
    """
    from src.reflex.sbsre import CEILING, FLOOR
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    opened = [r for r in core.episodes.read_all()
              if r["record_type"] == EpisodeRecordType.EPISODE_OPENED.value][0]
    assert opened["bound"] == result["contradiction"]["bound"]
    assert FLOOR <= opened["bound"] <= CEILING, (
        "the episode's bound escaped Ruling 4's clamp")


def test_b_the_passes_are_shaping_acts_never_pressure():
    """PIN B2 - K11. Internal re-consideration is not an L12 pressure class.

    Recording it as pressure would let a claim accumulate "survivals" by being
    thought about - weak-pressure farming at the cheapest possible price.
    """
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    episode = _episode_of(core, result)
    kinds = [r["record_type"] for r in core.episodes.read_all()
             if r["episode_id"] == episode]
    assert EpisodeRecordType.PRESSURE_APPLIED.value not in kinds
    assert EpisodeRecordType.PRESSURE_DEBT.value not in kinds
    assert kinds.count(EpisodeRecordType.SHAPING_ACT.value) >= 1
    assert core.episodes.applied_pressure_count(episode) == 0


def test_b_survived_is_unproducible_on_this_path():
    """PIN B3 - K11 WORKING, NOT A GAP.

    With zero pressure records the store REFUSES SURVIVED outright, so the
    chamber structurally cannot report that a contradiction withstood testing
    it never applied.
    """
    from src.filtration.episode_record import SurvivalWithoutPressure
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    dispositions = {r["outcome"] for r in core.episodes.read_all()
                    if r["record_type"] == EpisodeRecordType.DISPOSITION.value}
    assert EpisodeOutcome.SURVIVED.value not in dispositions

    # And it is refused STRUCTURALLY, not merely unused: a second episode on
    # the same shape cannot be disposed SURVIVED either.
    episode = core.episodes.open_episode(["OBL-0001"], 3)
    with pytest.raises(SurvivalWithoutPressure):
        core.episodes.disposition(episode, EpisodeOutcome.SURVIVED)


def test_b_one_shaping_act_per_pass():
    """PIN B4. The bound is honored by the caller's own iteration count."""
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    episode = _episode_of(core, result)
    attention = [r for r in core.episodes.read_all()
                 if r["episode_id"] == episode
                 and r["record_type"] == EpisodeRecordType.SHAPING_ACT.value
                 and r["act_kind"] == "attention"]
    assert len(attention) == result["contradiction"]["passes"]
    assert result["contradiction"]["passes"] <= result["contradiction"]["bound"]


# =====================================================================
# C. DISPOSITION MAPPING
# =====================================================================

def test_c_exhaustion_maps_to_unresolved_at_bound():
    """PIN C1 - THE FORCING PIN. A shallow carry stays distinguishable forever.

    The old chamber ended an exhausted thread as ABORT, which read the same as
    a thread a reflex had cut short. UNRESOLVED_AT_BOUND says WHY it stopped.
    """
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    block = result["contradiction"]
    assert block["disposition"] == EpisodeOutcome.UNRESOLVED_AT_BOUND.value
    assert block["exhausted"] is True
    assert block["passes"] == block["bound"], (
        "exhaustion means every declared pass was used")
    assert result["output_path"] == "SBSRE_CARRIED"


def test_c_irreconcilable_maps_to_collapsed_and_requests_a_scar():
    """PIN C2. Ruling 1: the episode REQUESTS, the owner writes."""
    core = AureaCore()
    core._echonet_resolver = _irreconcilable
    result = core.process_input(CONTRADICTION)
    assert result["contradiction"]["disposition"] == EpisodeOutcome.COLLAPSED.value
    assert result["scar_formed"] is not None
    assert result["scar_formed"].claim_id == result["claim_id"], (
        "Ruling 76's join did not survive the rewrite")


def test_c_the_scar_carries_the_raw_origin_pressure():
    """PIN C3 - RULING 76, VERBATIM PASSTHROUGH. `weight` clamps; the raw value
    is unrecoverable from it, which is why it is recorded separately."""
    core = AureaCore()
    core._echonet_resolver = _irreconcilable
    result = core.process_input(SCARRING)
    scar = result["scar_formed"]
    assert scar is not None
    assert scar.origin_pressure is not None


def test_c_a_protective_interrupt_maps_to_suspended():
    """PIN C4. Drift past the anchor-collapse line CUTS the consideration.

    Driven on the REAL method with the REAL arguments a pass produced, rather
    than through `process_input`: past 25 degrees the compass blocks output
    before Step 3b is reached, so the interrupt branch is unreachable from the
    public door. Capturing the arguments and re-driving the chamber is what
    lets the mapping be pinned without faking the objects it consumes.
    """
    core = AureaCore()
    captured = {}
    original = core._carry_contradiction

    def _capture(echo, collapse_result, reading):
        captured.update(echo=echo, collapse_result=collapse_result,
                        reading=reading)
        return original(echo, collapse_result, reading)

    core._carry_contradiction = _capture
    core.process_input(CONTRADICTION)
    assert captured, "the chamber was never reached"

    class _Drifted:
        stability = captured["reading"].stability
        drift = 99.0          # past ANCHOR_COLLAPSE_DEGREES (25.0, canon)

    carried = original(captured["echo"], captured["collapse_result"], _Drifted())
    assert carried["disposition"] is EpisodeOutcome.SUSPENDED
    assert "Anchor Collapse" in carried["record"]["reason"]
    assert carried["record"]["passes"] == 1, (
        "the interrupt did not cut the consideration on its first pass")
    assert carried["csa_entry_id"] is not None, (
        "the partial shape was not held in CSA - an abort-class consequence "
        "was lost in the rewrite")


def test_c_every_disposition_this_path_can_reach_is_legal():
    """PIN C5. The mapping is verified against the STORE's own checks - a
    disposition the store would refuse is not a mapping, it is a crash."""
    legal = {EpisodeOutcome.REVISED.value, EpisodeOutcome.COLLAPSED.value,
             EpisodeOutcome.SUSPENDED.value,
             EpisodeOutcome.UNRESOLVED_AT_BOUND.value}
    core = AureaCore()
    for claim in (CONTRADICTION, SCARRING, "Truth requires no evidence."):
        result = core.process_input(claim)
        block = result.get("contradiction")
        if block and block["disposition"]:
            assert block["disposition"] in legal


# =====================================================================
# D. THE DUPLICATE BRANCH - MEASURED, AND THE FINDING REPORTED
# =====================================================================

def test_d_repeat_text_is_not_suppressed_and_this_is_the_measured_finding():
    """PIN D1 - **A DECLARED BEHAVIORAL MOVEMENT, LARGER THAN THE HANDOFF'S.**

    SBSRE's `suppressed` set was keyed on a SHA-1 of the contradiction's
    CONTENT, so re-entering the same TEXT was refused. The obligation ledger
    dedupes on (target_kind, target_id, normalized claim) - and `target_id` is
    the CLAIM id, which Ruling 58 mints fresh for every perception. **Two
    identical texts are therefore two different targets, and the DUPLICATE
    branch is unreachable on this path.**

    That is the ruled design (M3-D §2.1 names `target_id=echo.claim_id`), so it
    is implemented as ruled and the consequence is recorded here rather than
    papered over. **NOTHING UNBOUNDED IS RE-OPENED**: each re-entry gets its own
    bounded episode, so Ruling 4's clamp still holds, and every carry now leaves
    a durable record where the old set dropped it silently (Ruling 23's law).
    What is LOST is the don't-re-grind-identical-input optimisation.
    """
    core = AureaCore()
    first = core.process_input(CONTRADICTION)
    second = core.process_input(CONTRADICTION)
    assert first["claim_id"] != second["claim_id"], (
        "claim ids stopped being unique per perception - Ruling 58 moved")
    assert second["contradiction"]["admission"] == "admitted", (
        "the duplicate branch became reachable - re-read this pin's docstring "
        "and the finding it records")
    assert second["contradiction"]["episode_id"] is not None
    rejected = [r for r in core.obligations.read_all()
                if r["record_type"] == ObligationRecordType.REJECTED.value]
    assert rejected == []


def test_d_the_duplicate_branch_still_works_when_it_is_reached():
    """PIN D2. The branch is unreachable through the pipeline, not broken:
    driven directly at the ledger, the rejection record IS the suppression."""
    core = AureaCore()
    first = core.obligations.admit(
        source="aurea_core.collapse", target_kind=TargetKind.CLAIM,
        target_id="CLM-0001", claim_text="same")
    assert first.admitted or first.rejection_kind is not None
    if first.admitted:
        again = core.obligations.admit(
            source="aurea_core.collapse", target_kind=TargetKind.CLAIM,
            target_id="CLM-0001", claim_text="same")
        assert not again.admitted
        assert again.rejection_kind.value == "duplicate"


# =====================================================================
# E. THE CALL SITE AND THE RESULT SURFACE
# =====================================================================

def test_e_sbsre_process_has_no_caller_in_src():
    """PIN E1. The decision path is no longer driven from anywhere."""
    for path in sorted((REPO / "src").rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                target = getattr(node.func, "value", None)
                if (getattr(node.func, "attr", None) == "process"
                        and isinstance(target, ast.Attribute)
                        and target.attr == "sbsre"):
                    raise AssertionError(
                        f"{path}:{node.lineno} still drives SBSRE.process")


def test_e_the_result_key_moved_and_the_old_one_is_gone():
    """PIN E2 - A DECLARED MOVEMENT. `result['sbsre']` -> `result['contradiction']`.

    The census found ZERO logic readers of the old key, so nothing needed
    migrating. The rename is the honest move rather than churn: the block no
    longer describes SBSRE, and a key naming a retired decision path is false
    documentation in the surface consumers read.
    """
    core = AureaCore()
    result = core.process_input(CONTRADICTION)
    assert "contradiction" in result
    assert "sbsre" not in result


def test_e_the_chamber_holds_no_loop_over_a_store_door():
    """PIN E3. The bounded consideration is the CALLER's loop; no episode door
    is driven from a `while` body."""
    tree = ast.parse(CORE_SRC.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    attr = getattr(sub.func, "attr", None)
                    assert attr not in ("open_episode", "disposition", "admit"), (
                        f"line {sub.lineno}: `{attr}` is driven from a loop - "
                        f"an episode is opened once and disposed once")
