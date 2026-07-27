"""
Rulings 34 + 34-A - epoch continuity and saturation surfacing.

    A process death does not SETTLE a lineage; it INTERRUPTS one.
    An interrupted epoch is not a finished epoch and does not earn a fresh ceiling.

WHAT WAS WRONG. `SAE.__init__` built `epoch=0, epoch_count=0,
touched_lineages=set()` and SAE had no save and no load, so three mutations per
epoch became 3N across N restarts. Worse: `stabilization_event`, the only
legitimate closer, has no caller anywhere in `src/`. **The legitimate reset was
unwired and the illegitimate one worked** - a guard pointed the wrong way.

WHY THE FIX IS NOT "RESET ON A TIMER". Canon 5a:1584 had already ruled the
question thirteen months earlier: a saturated epoch is SURFACED, "rather than
force-closing the epoch, which would re-arm mutation capacity at the exact
moment nothing has been metabolized." So the counter persists, the epoch never
force-closes, and the anti-deadlock rule is what keeps the lock from becoming
durable AND INVISIBLE.

TWO PINS HERE ARE STRUCTURAL AND BOTH ARE SELF-PINNED (Ruling 32's precedent -
each scanner is fed the forbidden shape, so it cannot rot into one that finds
nothing because it looks for nothing):
  - no durable write in `src/` resolves its path from a METHOD-PARAMETER default
    (Ruling 31's sweep extended to its third, never-specified shape);
  - no comparison on the saturation count outside the single surfacing site
    (§9 standing bar #5, sixth application).

THREE PINS READ THE SOURCE RATHER THAN THE LIVE CLASS, DELIBERATELY. The autouse
fixture in `conftest.py` redirects `AureaCore.STATE_PATH`, `SAE.RESTART_LOG_PATH`
and SAE's `runtime_path` default before any test runs, so their PRODUCTION values
are invisible from inside a test. That is the stratum Ruling 32 recorded: an
autouse redirect creates a class of defects only an unfixtured assertion can see,
and here the unfixtured instrument is the source itself.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.doctrine.codex import Codex
from src.expansion.sae import (
    SATURATION_HORIZON,
    SELF_MUTATION_CEILING,
    SAE,
    CeilingExceeded,
    MutationClass,
)
from tests.invariants import _ast as H


# =========================================================================
# HELPERS
# =========================================================================

def _sae(tmp_path, name="epoch.json", **kw):
    """A real SAE over a real, empty, tmp-pathed Codex, with an EXPLICIT epoch
    path so a restart test can point two instances at the same file."""
    return SAE(codex=Codex(filepath=str(tmp_path / "doctrines.json")),
               runtime_path=str(tmp_path / name), **kw)


# The obligations `_spend_full_budget` records. ALL THREE, since Ruling 37 (4).
#
# SUPERSEDED 2026-07-27 (Ruling 37 part 4), old text verbatim because it
# described a real defect that this constant's value used to encode:
#
#   "NOTE the asymmetry and that it is PRE-EXISTING, not introduced here: a
#    bare `authorize()` mints a token and spends a slot but records NO touched
#    lineage - only the three counted-class methods call `_touch`. So the third
#    spend below is invisible to the settle condition. Flagged in the report;
#    deliberately not "fixed" here, because making `authorize` touch would
#    change what closes an epoch."
#
# It DOES change what closes an epoch, and Ruling 37 ruled that change correct:
# a slot spent invisibly to the settle condition is BUDGET WITHOUT DEBT.
# `_touch` now lives in `authorize()`, so the bare-`authorize` spend below
# ("scar-c") records its obligation like every other. The flagged asymmetry is
# closed; the value moved because the RULING moved.
_SPENT_LINEAGES = {"scar-a", "scar-b", "scar-c"}


def _spend_full_budget(sae):
    """Consume the epoch budget across ALL THREE counted classes (T4-01), then
    CLOSE THE CYCLE.

    The closing `advance_cycle` matters: a cycle in which a mutation executed
    resets the stasis clock (executed takes precedence over blocked), so without
    it the first blocked cycle after a spend would be swallowed by the reset and
    every count below would sit one low. In a real pipeline the spend and the
    later blockage are different passes; this makes the helper match that.
    """
    sae.mutate_reflex("R-1", {"threshold": 0.8}, collapse_lineage="scar-a")
    sae.authorize_module_generation("M-1", collapse_lineage="scar-b")
    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-c", target_id="D-1")
    sae.advance_cycle()


def _blocked_cycle(sae, n=1):
    """Drive n symbolic cycles in which a mutation attempt is refused."""
    for _ in range(n):
        with pytest.raises(CeilingExceeded):
            sae.authorize(MutationClass.MUTATE_REFLEX, "scar-x", target_id="R-x")
        sae.advance_cycle()


class _RecordingRACM:
    """Stands in for RACM's route to the RB log. Records the call verbatim."""

    def __init__(self):
        self.calls = []

    def record_saturation_pressure(self, **kwargs):
        self.calls.append(kwargs)
        return f"RB-{len(self.calls)}"


# =========================================================================
# PIN 1 - THE CEILING SURVIVES A RESTART   (Ruling 34, double-armed)
# =========================================================================

def test_ceiling_survives_teardown_and_reconstruction(tmp_path):
    """SPEND -> TEAR DOWN -> RECONSTRUCT FROM DISK -> STILL REFUSED.

    DOUBLE-ARMED per Ruling 34-A: refused BEFORE the restart and refused AFTER,
    so a build that simply refuses everything cannot pass the second half alone.

    THE TRAP THIS TEST IS WRITTEN AROUND, recorded because the ruling names it:
    against pre-change code this pin "passes TRIVIALLY AND WRONGLY" if written
    loosely. A reconstructed pre-change SAE has `epoch_count == 0`, so the fourth
    mutation SUCCEEDS - but a naive version that reuses one successor id would
    see `MutationPreflightViolation` ("already a LIVE doctrine") and a bare
    `pytest.raises(Exception)` would go green for exactly the opposite reason.
    So: DISTINCT ids, `CeilingExceeded` named EXACTLY, and the restored counter
    asserted directly - three independent ways of refusing to be fooled.
    """
    first = _sae(tmp_path)
    _spend_full_budget(first)
    assert first.epoch_count == SELF_MUTATION_CEILING

    # ARM 1 - refused before the restart.
    with pytest.raises(CeilingExceeded):
        first.authorize(MutationClass.MUTATE_REFLEX, "scar-d", target_id="R-2")

    del first                                    # the process dies

    second = _sae(tmp_path)                      # reconstructed from disk ONLY
    assert second.epoch_count == SELF_MUTATION_CEILING, (
        "the spent budget did not survive reconstruction - this is the restart "
        "bypass: 3 mutations per epoch becomes 3N across N restarts")
    assert second.touched_lineages == _SPENT_LINEAGES, (
        "the OBLIGATION did not survive - `epoch_count` is downstream of the "
        "settle condition, and it is the settle condition that must cross")

    # ARM 2 - refused after the restart, for the ceiling's own reason.
    with pytest.raises(CeilingExceeded):
        second.authorize(MutationClass.MUTATE_REFLEX, "scar-e", target_id="R-3")
    assert second.epoch_count == SELF_MUTATION_CEILING, "a refusal spends nothing"


def test_a_spend_is_durable_before_the_cycle_boundary(tmp_path):
    """DEFECT WATCHED: persisting only at `advance_cycle`.

    FOUND BY THE MUTATION HARNESS, NOT BY DESIGN - and recorded as such. Removing
    `_persist()` from `authorize` initially SURVIVED every other pin here,
    because `mutate_reflex` / `authorize_module_generation` persist via `_touch`
    and the cycle boundary persists again. The uncovered case is a BARE
    `authorize()` - which is exactly how MSP Stage_2 spends a slot - in a process
    that dies mid-pass, after the token is minted and before the pass completes.
    That window restores a spent slot, which is the restart bypass in miniature.

    So: no `advance_cycle` here. The spend must be on disk the moment it happens.
    """
    sae = _sae(tmp_path)
    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-z", target_id="D-9")
    del sae                                      # dies mid-cycle

    resumed = _sae(tmp_path)
    assert resumed.epoch_count == 1, (
        "a minted authorization did not survive a mid-cycle death - the ceiling "
        "is durable only at the next convenient boundary, not at the spend")


def test_a_missing_epoch_file_is_a_first_run_not_a_missing_seed(tmp_path):
    """THERE IS NO SEED EPOCH, and that asymmetry with Codex/ScarLogicCore/
    EchoMemory is deliberate: an epoch is ACCUMULATED, never issued."""
    fresh = _sae(tmp_path, name="never-written.json")
    assert fresh.epoch == 0 and fresh.epoch_count == 0
    assert fresh.touched_lineages == set()
    assert fresh.restart_records == [], "a first run is not a restart"


# =========================================================================
# PIN 2 - CLOSURE CARRIES WHAT DID NOT SETTLE   (Ruling 34 res.2)
# =========================================================================

def test_closure_discharges_what_settled_and_carries_what_did_not(tmp_path):
    """DEFECT WATCHED: `touched_lineages.clear()`.

    A clear lets an epoch closure LAUNDER unsettled obligation - which is
    precisely what restart used to do. The principle that makes restart
    non-absolving makes closure non-absolving: one rule, two boundaries.
    """
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    assert sae.touched_lineages == _SPENT_LINEAGES

    assert sae.stabilization_event("scar_fermentation", lineage="scar-a") is True
    assert sae.epoch == 1 and sae.epoch_count == 0

    assert sae.touched_lineages == {"scar-b", "scar-c"}, (
        "closure erased obligations that never settled - scar-b and scar-c are "
        "still owed and must cross into the next epoch")


def test_the_carry_survives_a_restart_too(tmp_path):
    """The two boundaries compose: carried obligation is also durable."""
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    sae.stabilization_event("scar_fermentation", lineage="scar-a")
    del sae

    resumed = _sae(tmp_path)
    assert resumed.epoch == 1
    assert resumed.touched_lineages == {"scar-b", "scar-c"}


# =========================================================================
# PIN 3 - THE EVIDENCE GUARD IS SYMMETRICAL   (Ruling 34 res.3)
# =========================================================================

def test_anchor_consolidation_on_an_untouched_lineage_does_not_close(tmp_path):
    """DEFECT WATCHED: the `anchor_consolidation` branch closing UNCONDITIONALLY.

    The reasoning written at the `scar_fermentation` guard - fermentation on a
    lineage SAE never touched proves nothing about SAE's changes - applies
    verbatim here and had not been applied. Left as it was, once a sender exists
    it would close epochs with lineages still unsettled and DISCARD the record
    that they were unsettled: the restart bypass reproduced INSIDE a process.
    """
    sae = _sae(tmp_path)
    _spend_full_budget(sae)

    assert sae.stabilization_event(
        "anchor_consolidation", lineage="scar-never-touched") is False
    assert sae.stabilization_event("anchor_consolidation") is False, (
        "a bare anchor consolidation with no lineage at all still closes the epoch")
    assert sae.epoch == 0 and sae.epoch_count == SELF_MUTATION_CEILING

    with pytest.raises(CeilingExceeded):
        sae.authorize(MutationClass.MUTATE_REFLEX, "scar-f", target_id="R-9")


def test_anchor_consolidation_on_a_touched_lineage_does_close(tmp_path):
    """The guard is symmetrical, not disabling: the legitimate path still works."""
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    assert sae.stabilization_event("anchor_consolidation", lineage="scar-b") is True
    assert sae.epoch == 1 and sae.epoch_count == 0
    assert sae.touched_lineages == {"scar-a", "scar-c"}


# =========================================================================
# PINS 5/6/7 - SATURATION   (Ruling 34-A, canon 5a:1584)
# =========================================================================

def test_saturation_surfaces_past_the_horizon_and_the_epoch_stays_saturated(tmp_path):
    """CANON IS STRICT: "more than 5 consecutive symbolic cycles", so the
    SIXTH surfaces, not the fifth.

    DEFECT WATCHED, and it is the one canon names explicitly: force-closing the
    epoch at the horizon. That would "re-arm mutation capacity at the exact
    moment nothing has been metabolized" - the restart bypass returning under
    the counter's own name.
    """
    racm = _RecordingRACM()
    sae = _sae(tmp_path, racm=racm)
    _spend_full_budget(sae)

    _blocked_cycle(sae, SATURATION_HORIZON)
    assert sae.consecutive_blocked_cycles == SATURATION_HORIZON
    assert sae.saturation_surfaced is False, "surfaced AT the horizon, not past it"
    assert racm.calls == []

    _blocked_cycle(sae, 1)                                   # the sixth
    assert sae.consecutive_blocked_cycles == SATURATION_HORIZON + 1
    assert sae.saturation_surfaced is True
    assert sae.divergence_trigger_eligible is True

    # THE EPOCH IS NOT CLOSED. Still saturated, still refusing, count still spent.
    assert sae.epoch == 0
    assert sae.epoch_count == SELF_MUTATION_CEILING
    with pytest.raises(CeilingExceeded):
        sae.authorize(MutationClass.MUTATE_REFLEX, "scar-g", target_id="R-4")

    assert len(racm.calls) == 1, "RACM did not log reflex-class pressure"
    assert racm.calls[0]["horizon"] == SATURATION_HORIZON
    assert racm.calls[0]["blocked_cycles"] == SATURATION_HORIZON + 1


def test_the_surfacing_happens_once_per_episode_not_once_per_cycle(tmp_path):
    """A signal repeated every cycle forever is noise, and noise is how a real
    one stops being read."""
    racm = _RecordingRACM()
    sae = _sae(tmp_path, racm=racm)
    _spend_full_budget(sae)

    _blocked_cycle(sae, SATURATION_HORIZON + 5)
    assert sae.consecutive_blocked_cycles == SATURATION_HORIZON + 5
    assert len(racm.calls) == 1, f"surfaced {len(racm.calls)}x in one episode"
    assert len(sae.saturation_events) == 1


def test_an_interrupted_run_does_not_surface(tmp_path):
    """PIN 7 - blocked, blocked, UNBLOCKED, blocked... CONSECUTIVE means
    consecutive.

    DEFECT WATCHED: a counter that only ever increments. The stasis clock
    measures an unbroken run; a cycle in which a mutation EXECUTED proves she
    was able to change, and that ends the run.
    """
    racm = _RecordingRACM()
    sae = _sae(tmp_path, racm=racm)
    _spend_full_budget(sae)

    _blocked_cycle(sae, 4)
    assert sae.consecutive_blocked_cycles == 4

    # THE INTERRUPTION. Something settled, so the epoch closed and budget came
    # back - and the run of blocked cycles is over by definition.
    assert sae.stabilization_event("scar_fermentation", lineage="scar-a") is True
    assert sae.consecutive_blocked_cycles == 0, "the run was not broken"

    # Saturate again and block another four. Eight blocked cycles have now
    # happened in total - and NINE would be needed to surface if the counter
    # only ever incremented.
    _spend_full_budget(sae)
    _blocked_cycle(sae, 4)

    assert sae.consecutive_blocked_cycles == 4
    assert racm.calls == [], (
        "surfaced on a run that was interrupted - 4 + 4 blocked cycles with a "
        "settled epoch between them is not 8 CONSECUTIVE blocked cycles")


def test_a_cycle_that_both_spent_and_blocked_is_not_a_blocked_cycle(tmp_path):
    """The executed-takes-precedence branch, pinned on its own.

    A cycle that spends the third slot and is then refused a fourth is not a
    cycle in which AUREA could not change - she just had. Documented in
    `advance_cycle` and reachable only in this shape, so it gets its own pin
    rather than riding on a helper's accident.
    """
    sae = _sae(tmp_path)
    sae.mutate_reflex("R-1", {}, collapse_lineage="scar-a")
    sae.authorize_module_generation("M-1", collapse_lineage="scar-b")
    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-c", target_id="D-1")
    with pytest.raises(CeilingExceeded):
        sae.authorize(MutationClass.MUTATE_REFLEX, "scar-d", target_id="R-2")

    sae.advance_cycle()                          # both flags set this cycle
    assert sae.consecutive_blocked_cycles == 0


def test_a_cycle_that_did_not_exercise_sae_changes_nothing(tmp_path):
    """THE JUDGMENT CALL, PINNED SO IT IS VISIBLE RATHER THAN IMPLIED.

    Canon's condition is "mutation ATTEMPTS are blocked". A cycle with no
    attempt is neither blocked nor unblocked, so it leaves the count alone.
    Resetting on silence would make the surfacing unreachable for a system that
    attempts mutation only occasionally - which is exactly the stasis the
    divergence trigger exists for. Incrementing on silence would count cycles in
    which she never tried. Neither; the count holds.
    """
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    _blocked_cycle(sae, 3)

    for _ in range(10):
        sae.advance_cycle()                      # quiet cycles
    assert sae.consecutive_blocked_cycles == 3


def test_many_blocked_attempts_in_one_cycle_are_one_blocked_cycle(tmp_path):
    """The tally is per-CYCLE. Otherwise a single busy cycle would surface."""
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    for _ in range(20):
        with pytest.raises(CeilingExceeded):
            sae.authorize(MutationClass.MUTATE_REFLEX, "scar-i", target_id="R-6")
    sae.advance_cycle()
    assert sae.consecutive_blocked_cycles == 1


def test_restart_mid_saturation_resumes_the_stasis_clock(tmp_path):
    """PIN 6 - DEFECT WATCHED: saturation state left out of the snapshot.

    If the stasis clock reset on restart, the restart bypass would return
    wearing the counter's name: kill the process every five cycles and the
    condition never surfaces.
    """
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    _blocked_cycle(sae, 4)
    assert sae.consecutive_blocked_cycles == 4
    del sae

    racm = _RecordingRACM()
    resumed = _sae(tmp_path, racm=racm)
    assert resumed.consecutive_blocked_cycles == 4, "the stasis clock reset"

    _blocked_cycle(resumed, 2)                   # cycles 5 and 6
    assert resumed.saturation_surfaced is True
    assert len(racm.calls) == 1


def test_a_surfaced_episode_stays_surfaced_across_a_restart(tmp_path):
    """The episode flag persists too, or a restart re-fires the same signal."""
    sae = _sae(tmp_path, racm=_RecordingRACM())
    _spend_full_budget(sae)
    _blocked_cycle(sae, SATURATION_HORIZON + 1)
    assert sae.saturation_surfaced is True
    del sae

    racm = _RecordingRACM()
    resumed = _sae(tmp_path, racm=racm)
    assert resumed.saturation_surfaced is True
    assert resumed.divergence_trigger_eligible is True
    _blocked_cycle(resumed, 3)
    assert racm.calls == [], "a restart re-fired an already-surfaced episode"


def test_closing_the_epoch_clears_the_stasis_signal(tmp_path):
    """Eligibility describes a CURRENT condition. Leaving it set after the
    condition lifted would be a stale status line inside live state."""
    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    _blocked_cycle(sae, SATURATION_HORIZON + 1)
    assert sae.divergence_trigger_eligible is True

    sae.stabilization_event("scar_fermentation", lineage="scar-a")
    assert sae.consecutive_blocked_cycles == 0
    assert sae.saturation_surfaced is False
    assert sae.divergence_trigger_eligible is False


def test_the_eligibility_field_has_no_consumer(tmp_path):
    """RULING 28's SHAPE, PINNED: `divergence_trigger_eligible` is DECLARED and
    READABLE, and RLB (corpus 2b:697 / 2b:745) is UNBUILT.

    DEFECT WATCHED: inventing a reader to make the field "useful". Setting it
    gates nothing. If a real RLB lands, this pin SHOULD fail - and the response
    is to cite the ruling that authorized the consumer, never to delete the pin.
    """
    readers = []
    for path in H.src_files():
        if H.rel(path) == "src/expansion/sae.py":
            continue                    # the owner declares and sets it
        tree = H.parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            # An ATTRIBUTE ACCESS, not a string. RACM's log payload carries the
            # WORD as a dict key while reporting the surfacing - that is the
            # signal being recorded, not a consumer reading the field.
            if isinstance(node, ast.Attribute) and node.attr == "divergence_trigger_eligible":
                readers.append((H.rel(path), node.lineno))
    assert readers == [], f"{readers} now read the eligibility field"


def test_saturation_surfaces_even_with_no_racm_injected(tmp_path):
    """DEFECT WATCHED: the whole surfacing silently skipped when the log route
    is absent - the fail-silent shape this ruling exists to close."""
    sae = _sae(tmp_path)                         # no racm
    _spend_full_budget(sae)
    _blocked_cycle(sae, SATURATION_HORIZON + 1)

    assert sae.divergence_trigger_eligible is True
    assert len(sae.saturation_events) == 1
    assert "UNROUTED" in sae.saturation_events[0]["rb_entry_id"]


def test_racm_logs_saturation_into_the_real_rb_channel(tmp_path):
    """The route is real, and the CLOSED BehaviorType enum stays closed."""
    from src.reflex.rb_system import BehaviorType, RBSystem
    from src.reflex.racm import RACM

    racm = RACM(rb_system=RBSystem(log_path=str(tmp_path / "rb.jsonl")))
    entry_id = racm.record_saturation_pressure(
        epoch=0, blocked_cycles=6, horizon=5, unsettled_lineages=["scar-a"])

    assert entry_id
    logged = [e for e in racm.rb.entries if e.reflex_triggered == "SAE"]
    assert len(logged) == 1
    assert logged[0].behavior_type is BehaviorType.SUSPEND
    assert logged[0].outcome["epoch_force_closed"] is False


# =========================================================================
# RES.4 - A RESTART IS RECORDED, NEVER A CLOSURE
# =========================================================================

def test_a_restart_is_recorded_with_what_is_actually_known(tmp_path):
    """DEFECT WATCHED: a restart that closes the epoch, or one that leaves no
    trace. Resumed state must never be indistinguishable from continuous state.
    """
    log = tmp_path / "restarts.jsonl"
    SAE.RESTART_LOG_PATH = str(log)              # class attr, resolved at write

    sae = _sae(tmp_path)
    _spend_full_budget(sae)
    epoch_before = sae.epoch
    del sae

    resumed = _sae(tmp_path)
    assert len(resumed.restart_records) == 1
    record = resumed.restart_records[0]

    assert resumed.epoch == epoch_before, "the restart CLOSED the epoch"
    assert record["at_save"]["epoch_count"] == SELF_MUTATION_CEILING
    assert record["at_load"]["epoch_count"] == SELF_MUTATION_CEILING
    assert set(record["at_save"]["unsettled_lineages"]) == _SPENT_LINEAGES

    assert record["duration"] is None, (
        "a wall-clock gap was recorded as duration - an epoch is explicitly NOT "
        "wall-clock time (5a:1572), so that number would look like symbolic "
        "duration and would not be one")

    lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1 and lines[0]["event"] == "sae_restart"


# =========================================================================
# RES.7 / RES.8 - THE STATE FILE
# =========================================================================

def _class_attr_from_source(module_rel: str, cls: str, attr: str) -> str:
    """Read a class attribute's DECLARED value from source.

    The autouse fixture redirects these before any test runs, so the production
    value is unreachable from inside a test - Ruling 32's recorded stratum. The
    source is the only unfixtured instrument.
    """
    tree = ast.parse((H.repo_root() / module_rel).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for t in stmt.targets:
                        if isinstance(t, ast.Name) and t.id == attr:
                            return stmt.value.value
    raise AssertionError(f"{cls}.{attr} not found in {module_rel}")


def test_the_state_path_is_a_class_attribute_under_data_runtime():
    """RES.7. Was a method-parameter default pointing OUTSIDE `data/runtime/`,
    so a real run left an untracked file in the tree - the exact pre-Ruling-31
    condition."""
    declared = _class_attr_from_source("src/aurea_core.py", "AureaCore", "STATE_PATH")
    assert declared.startswith("data/runtime/"), declared


def test_the_sae_epoch_path_defaults_under_data_runtime():
    """RES.1. Ruling 32's prefix: untracked, gitignored, structurally unable to
    collide with a seed."""
    tree = ast.parse((H.repo_root() / "src/expansion/sae.py").read_text(encoding="utf-8"))
    default = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SAE":
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                    names = [a.arg for a in stmt.args.args]
                    offset = len(names) - len(stmt.args.defaults)
                    for i, d in enumerate(stmt.args.defaults):
                        if names[offset + i] == "runtime_path":
                            default = d.value
    assert default is not None, "SAE.__init__ has no `runtime_path` default"
    assert default.startswith("data/runtime/"), default


def test_the_pipeline_advances_the_sae_cycle():
    """THE WIRING, PINNED. DEFECT WATCHED: `advance_cycle` implemented and never
    called - the stasis clock frozen at zero forever, so the anti-deadlock rule
    could never fire and would look implemented.

    One symbolic cycle = one `process_input` pass, driven from the same site as
    `tcaml.tick()`. This drives the REAL pipeline rather than asserting on
    source, so a call that exists but is unreachable still fails.
    """
    core = AureaCore()
    core.sae.consecutive_blocked_cycles = 4      # mid-stasis, nothing surfaced
    core.sae._cycle_blocked = True               # this pass refused a mutation

    core.process_input("a claim that goes through the ordinary path")

    assert core.sae.consecutive_blocked_cycles == 5, (
        "process_input did not advance SAE's symbolic cycle - the stasis clock "
        "is frozen and the anti-deadlock rule can never fire")


def test_the_fixture_actually_redirects_all_three_new_paths():
    """The redirect is pinned by INSPECTING THE LIVE PATCHED VALUES, not by
    reading conftest.

    This pass adds three durable write paths. A missing entry in the redirect
    table breaks nothing loudly - it just quietly writes epoch state and restart
    records into the real tree on every suite run, which is Ruling 31's defect
    reopening. Nothing else here can catch that, because every test in this file
    passes its paths explicitly.
    """
    import inspect

    names = [n for n, p in inspect.signature(SAE.__init__).parameters.items()
             if p.default is not inspect.Parameter.empty]
    live_runtime = str(SAE.__init__.__defaults__[names.index("runtime_path")])

    for label, value in (("SAE.runtime_path", live_runtime),
                         ("SAE.RESTART_LOG_PATH", str(SAE.RESTART_LOG_PATH)),
                         ("AureaCore.STATE_PATH", str(AureaCore.STATE_PATH))):
        norm = value.replace("\\", "/")
        assert not norm.startswith(("data/", "logs/")), (
            f"{label} is NOT redirected by tests/conftest.py - it still points "
            f"at {value!r}, so every suite run writes into the real tree")


def test_save_state_and_load_state_are_symmetric(tmp_path):
    """RES.8. DEFECT WATCHED: `system_status` - a RENDERED REPORT STRING -
    written into the data file and never read back. Docket L's stale-status-line
    shape in its worst possible location: it goes stale against the data beside
    it and nothing ever reads it to notice.
    """
    core = AureaCore()
    core.save_state()
    written = json.loads(Path(core.STATE_PATH).read_text(encoding="utf-8"))

    assert "system_status" not in written, (
        "a rendered status string is living inside the state file again")

    source = (H.repo_root() / "src/aurea_core.py").read_text(encoding="utf-8")
    load_body = source.split("def load_state")[1]
    for key in written:
        if key in {"timestamp", "version"}:
            continue          # metadata ABOUT the file, not state
        assert f"'{key}'" in load_body or f'"{key}"' in load_body, (
            f"save_state writes {key!r} and load_state never reads it back")


# =========================================================================
# PIN 4 (STRUCTURAL) - NO DURABLE WRITE FROM A METHOD-PARAMETER DEFAULT
# =========================================================================

_WRITE_MODES = {"w", "a", "w+", "a+", "wb", "ab", "x", "xb"}
_WRITE_CALLS = {"dump", "write_text", "write_bytes", "mkdir"}


def _looks_like_path(value) -> bool:
    return isinstance(value, str) and (
        "/" in value or value.endswith((".json", ".jsonl", ".txt", ".log")))


def _body_writes(fn: ast.AST) -> bool:
    for n in ast.walk(fn):
        if not isinstance(n, ast.Call):
            continue
        name = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
        if name in _WRITE_CALLS:
            return True
        if name == "open":
            for a in n.args[1:]:
                if isinstance(a, ast.Constant) and a.value in _WRITE_MODES:
                    return True
            for kw in n.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                        and kw.value.value in _WRITE_MODES:
                    return True
    return False


def find_method_default_write_paths(tree: ast.AST) -> list[tuple[int, str]]:
    """Functions that resolve a durable write path from a METHOD-PARAMETER default.

    `__init__` is excluded because an `__init__` default IS one of the two shapes
    `conftest.py` can reach (it patches `cls.__init__.__defaults__` by name). A
    method-parameter default on any OTHER function is reachable by neither
    mechanism, which is Ruling 31's unreachable-by-construction defect.
    """
    found = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name == "__init__":
            continue
        args = fn.args
        pairs = list(zip(args.args[len(args.args) - len(args.defaults):], args.defaults))
        pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
        for arg, default in pairs:
            if (isinstance(default, ast.Constant) and _looks_like_path(default.value)
                    and _body_writes(fn)):
                found.append((fn.lineno, f"{fn.name}({arg.arg}={default.value!r})"))
    return found


def test_no_durable_write_resolves_its_path_from_a_method_parameter_default():
    """Extends Ruling 31's sweep to its THIRD path shape - the one that sweep
    was never specified on.

    `conftest.py` has exactly two mechanisms: monkeypatch a CLASS ATTRIBUTE or an
    `__init__` DEFAULT. A method-parameter default is neither, so such a path is
    not merely uncovered - it is UNREACHABLE BY CONSTRUCTION, and every test run
    writes to the real location while the fixture's docstring claims isolation.
    """
    violations = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, detail in find_method_default_write_paths(tree):
            violations.append(H.Violation(path, lineno, detail))

    assert not violations, (
        "\n".join(str(v) for v in violations) + "\n\n"
        "  A durable write path MUST be a class attribute or an `__init__`\n"
        "  default - the only two shapes tests/conftest.py can reach - and it\n"
        "  MUST be redirected there in the SAME commit (Ruling 31).\n"
    )


RUNTIME_PREFIX = "data/runtime/"


def _pathish(value) -> bool:
    """A path-looking string constant. Prose is EXCLUDED by the space test.

    The first draft of this scanner flagged `EchoNet._LOGIC_UNCOUNTABLE` - a
    paragraph of explanatory prose containing a slash. A scanner that cries wolf
    on documentation gets narrowed by whoever it annoys, so it excludes spaces
    rather than growing an ignore-list.
    """
    return (isinstance(value, str) and " " not in value
            and ("/" in value or value.endswith((".json", ".jsonl", ".log", ".txt"))))


def find_default_paths(tree: ast.AST) -> list[tuple[int, str, str]]:
    """(lineno, name, value) for every class-attribute and `__init__`-default
    path constant - the two shapes `conftest.py` can reach, and therefore the
    two shapes Ruling 39 governs."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant) \
                        and _pathish(stmt.value.value):
                    for t in stmt.targets:
                        if isinstance(t, ast.Name):
                            out.append((stmt.lineno, f"{node.name}.{t.id}",
                                        stmt.value.value))
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            a = node.args
            pairs = list(zip(a.args[len(a.args) - len(a.defaults):], a.defaults))
            pairs += [(x, d) for x, d in zip(a.kwonlyargs, a.kw_defaults) if d]
            for arg, d in pairs:
                if isinstance(d, ast.Constant) and _pathish(d.value):
                    out.append((node.lineno, arg.arg, d.value))
    return out


def test_every_default_write_path_resolves_under_data_runtime():
    """RULING 39 - ISOLATION BY CONSTRUCTION, NOT BY FIXTURE.

    The fixture protects tests; nothing protects scripts, notebooks, or a real
    run - and nothing SHOULD have to. Ruling 32 established that runtime state
    never writes to a TRACKED path; 39 finishes the thought: it never writes to
    an UNIGNORED path either, BY DEFAULT.

    SEED PATHS ARE EXEMPT AND MUST STAY THAT WAY. They are READ-ONLY INPUT
    (Ruling 32) with no writer at all; moving one under `data/runtime/` would be
    the exact opposite remedy, and the exemption is by NAME so it cannot quietly
    widen.
    """
    violations = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, name, value in find_default_paths(tree):
            if name.endswith("SEED_PATH"):
                assert not value.startswith("data/runtime/"), (
                    f"{H.rel(path)}:{lineno} {name} was moved under runtime - "
                    "a seed has NO writer and belongs on its tracked path")
                continue
            if not value.startswith(RUNTIME_PREFIX):
                violations.append(f"{H.rel(path)}:{lineno} {name} = {value!r}")

    assert not violations, (
        "\n".join(violations) + "\n\n"
        "  Every default write path in src/ resolves under `data/runtime/`\n"
        "  (Ruling 39). `data/runtime/` is GITIGNORED, NOT EPHEMERAL -\n"
        "  git-invisibility is not impermanence, and forensic logs keep their\n"
        "  append-only Ruling 31 semantics wherever they live.\n")


@pytest.mark.parametrize("source", [
    "class C:\n    LOG = 'logs/a.jsonl'\n",
    "class C:\n    def __init__(self, p='data/suspension/x.json'):\n        pass\n",
    "class C:\n    ALERTS = 'data/collapse_logs/x.jsonl'\n",
])
def test_the_runtime_prefix_scanner_actually_fires(source):
    """Fed a violation, per the scanner-fires precedent."""
    found = find_default_paths(ast.parse(source))
    assert found and not any(v.startswith(RUNTIME_PREFIX) for _l, _n, v in found)


def test_an_unfixtured_full_pass_leaves_the_tree_clean():
    """RULING 39's BEHAVIORAL HALF, and the one that would have caught the
    original defect.

    Runs a REAL `AureaCore` pass with the autouse fixture's redirects UNDONE -
    which is the whole point: the fixture is what hides this class of defect,
    so the assertion has to step outside it (Ruling 32's recorded stratum).
    `git status --porcelain` empty is the assertion.

    Before Ruling 39 this left `data/suspension/`, `data/topology/` and
    `data/test_results.json` untracked in the tree on every script run, and
    appended to the real forensic logs - the fixture protects tests, and
    nothing protected anything else.

    IT CLEANS UP AFTER ITSELF, and that is not fastidiousness: CI asserts
    `data/runtime/` is EMPTY after the suite, which is what catches a store
    added without a `conftest.py` redirect. This test deliberately writes there
    with the REAL defaults, so it removes exactly the files it created and
    leaves any that were already present.
    """
    import subprocess
    from src.aurea_core import AureaCore

    root = H.repo_root()
    runtime = root / "data" / "runtime"

    def _snapshot():
        return {p for p in runtime.rglob("*") if p.is_file()} if runtime.exists() else set()

    pre_runtime = _snapshot()
    before = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True).stdout

    core = AureaCore()
    core.process_input("A claim that runs the whole pass.")
    core.save_state()

    after = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                           capture_output=True, text=True).stdout

    for created in _snapshot() - pre_runtime:
        created.unlink(missing_ok=True)
    for d in sorted((p for p in runtime.rglob("*") if p.is_dir()),
                    key=lambda p: -len(p.parts)) if runtime.exists() else []:
        if not any(d.iterdir()):
            d.rmdir()
    if runtime.exists() and not pre_runtime and not any(runtime.iterdir()):
        runtime.rmdir()

    assert after == before, (
        "an unfixtured AureaCore pass dirtied the working tree:\n"
        f"{set(after.splitlines()) - set(before.splitlines())}\n"
        "Every default write path must resolve under `data/runtime/` (Ruling 39).")


def test_the_runtime_prefix_scanner_ignores_prose():
    """DEFECT WATCHED: flagging a docstring that happens to contain a slash.

    This is not hypothetical - it fired on `EchoNet._LOGIC_UNCOUNTABLE` during
    the Ruling 39 sweep.
    """
    prose = ("class C:\n"
             "    NOTE = 'logic reads the claim/text: not a path at all'\n")
    assert find_default_paths(ast.parse(prose)) == []


@pytest.mark.parametrize("source", [
    "def save(self, filepath='data/x.json'):\n"
    "    with open(filepath, 'w') as f:\n        f.write('x')\n",
    "def dump_it(self, p='logs/y.jsonl'):\n    json.dump({}, open(p, 'a'))\n",
    "def w(self, path='data/z.json'):\n    Path(path).write_text('x')\n",
    "def kw(self, *, telemetry='logs/t.jsonl'):\n"
    "    with open(telemetry, 'a') as f:\n        f.write('x')\n",
])
def test_the_method_default_scanner_actually_fires(source):
    """The pin above is pinned (Ruling 32's precedent).

    It is green today for the honest reason - the two `save_state`/`load_state`
    sites moved to a class attribute - which is exactly how a broken scanner
    hides.
    """
    assert find_method_default_write_paths(ast.parse(source)), source


def test_the_method_default_scanner_ignores_the_reachable_shapes():
    """`__init__` defaults and class attributes are FINE - the fixture reaches
    both. A scanner that flagged them would be demanding the wrong fix."""
    benign = (
        "class C:\n"
        "    LOG = 'logs/a.jsonl'\n"
        "    def __init__(self, runtime_path='data/runtime/b.json'):\n"
        "        self.p = runtime_path\n"
        "    def save(self):\n"
        "        with open(self.p, 'w') as f:\n            f.write('x')\n"
    )
    assert find_method_default_write_paths(ast.parse(benign)) == []


# =========================================================================
# PIN 8 (STRUCTURAL) - THE SATURATION COUNT REPORTS, IT DOES NOT GATE
# =========================================================================

COUNT_FIELD = "consecutive_blocked_cycles"
SURFACING_SITE = "_surface_saturation_if_due"


def find_saturation_comparisons(tree: ast.AST) -> list[tuple[int, str]]:
    """Every Compare touching the saturation count, tagged with its enclosing
    function. A bin is a cutoff without an operator, so `round`/`min`/`max`/
    `int`/`abs`/`bool` over the count count as comparisons too."""
    found = []

    def touches(node):
        return any((isinstance(n, ast.Attribute) and n.attr == COUNT_FIELD)
                   or (isinstance(n, ast.Name) and n.id == COUNT_FIELD)
                   for n in ast.walk(node))

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare) and touches(node):
                found.append((node.lineno, fn.name))
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in {"round", "min", "max", "int", "abs", "bool"}
                    and any(touches(a) for a in node.args)):
                found.append((node.lineno, fn.name))
    return found


def test_the_saturation_count_is_compared_at_exactly_one_site():
    """§9 STANDING BAR #5, SIXTH APPLICATION. THE COUNTER REPORTS; IT DOES NOT GATE.

    It gates one thing and one thing only - the surfacing. A saturation count
    that closed the epoch would be a cutoff on a tally AND the restart bypass
    returning under the counter's own name, which canon refuses in terms:
    force-closing "would re-arm mutation capacity at the exact moment nothing
    has been metabolized" (5a:1584).
    """
    sites = []
    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, fn in find_saturation_comparisons(tree):
            sites.append((H.rel(path), lineno, fn))

    offenders = [s for s in sites if s[2] != SURFACING_SITE]
    assert not offenders, (
        f"the saturation count is compared outside {SURFACING_SITE}: {offenders}. "
        "It REPORTS. The only decision it may take part in is whether the "
        "condition has been surfaced once."
    )
    assert len(sites) == 1, (
        f"expected exactly one comparison site, found {sites}")


@pytest.mark.parametrize("source", [
    "def f(self):\n    if self.consecutive_blocked_cycles > 5:\n        self.epoch += 1\n",
    "def f(self):\n    tier = min(self.consecutive_blocked_cycles, 3)\n",
    "def f(self):\n    x = self.consecutive_blocked_cycles >= 2\n",
])
def test_the_saturation_comparison_scanner_actually_fires(source):
    """Self-pinned, same reason as every other scanner in this repo."""
    assert find_saturation_comparisons(ast.parse(source))
