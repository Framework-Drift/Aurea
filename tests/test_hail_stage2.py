"""
test_hail_stage2.py - end-to-end pins for Ruling 33 Stage 2 (the wiring).

Stage 1 pinned the ORGAN in isolation: a hand-built packet, rendered directly.
Those tests would all still pass against a pipeline that never called HAIL at
all. THESE drive `AureaCore.process_input` and assert on what comes out of the
real pass - which is the only thing that proves the wiring exists.

RULING 17: every test here was watched RED under the exact defect it claims to
catch, before it was allowed to land. The defect is named in each docstring.

THE SHAPE OF THE WIRING, and why the pins are the ones they are:

  Before Stage 2, `process_input` decided expression in TEN PLACES - ten
  f-strings, ten `output_blocked = True` assignments, and nothing anywhere
  checking that a given path's string and its boolean agreed. They could drift
  and nothing would notice.

  After Stage 2 there is ONE emitter (`AureaCore._emit`), and it reads BOTH the
  rendered text and the blocked flag from the SAME path contract. The verdict
  and the flag cannot disagree because there is only one of them. That is what
  `test_the_blocked_flag_and_the_verdict_cannot_disagree` and the two
  single-assignment AST pins exist to keep true.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from unittest.mock import patch

import pytest

from src.aurea_core import AureaCore
from src.identity.compass import AnchorReading, CompassStabilityEngine, Direction
from src.output.ore import EXPRESSION_FOR_PATH, OutputPath
from src.output.truth_packet import SILENT_VERDICTS, ExpressionVerdict, TruthPacket
from src.utils.models import Scar

CORE_SOURCE = Path(inspect.getfile(AureaCore))


def _present(direction):
    return AnchorReading(direction=direction, mass=1.0)


def _irreconcilable(contradiction, cycle):
    """SBSRE's DECLARED resolver seam (sbsre.py:156).

    Its own docstring says real coherence detection is EchoNet/EchoCore's job
    and that "with no resolver injected, SBSRE reaches no verdict on its own".
    Two pipeline exits (COLLAPSE_DETECTED, and REFLEX_BLOCKED via scar density)
    sit behind the COLLAPSE outcome, so this stands in for that unbuilt
    detector. It is the module's own injection point, not a patch of one.
    """
    return "irreconcilable"


def _drifted(core: AureaCore, degrees: float, text: str, passes: int = 1):
    with patch.object(CompassStabilityEngine, "_north", return_value=_present(Direction.NORTH)), \
         patch.object(CompassStabilityEngine, "_south", return_value=_present(Direction.SOUTH)), \
         patch.object(CompassStabilityEngine, "_east", return_value=_present(Direction.EAST)), \
         patch.object(CompassStabilityEngine, "_west", return_value=_present(Direction.WEST)), \
         patch.object(CompassStabilityEngine, "_drift", return_value=degrees):
        for _ in range(passes):
            result = core.process_input(text)
    return result


CONTRADICTION = "She should speak and she must never speak."


# =========================================================================
# PIN 1 - a GSR cascade, driven through the REAL pipeline
# =========================================================================

def test_a_gsr_cascade_speaks_no_echo_content_end_to_end():
    """DEFECT WATCHED: Step 6 emitting `content` directly instead of routing
    through `_emit` (i.e. the pre-wiring `result['output'] = f"[BLOCKED by
    ...]"`) - the assertion that the ECHO's text is absent still passes there,
    so the pin is written to catch the thing that actually regresses: the
    verdict/flag pairing and the silent render.

    The whole route is real: 120 scars seeded through the OWNER's `form_scar`,
    a contradiction that SBSRE proves irreconcilable, a scar formed, Step 5's
    scar-density pressure past 0.95, GSR's cascade branch, RACM authorization,
    and Step 6. No reflex is hand-built and no response is injected.
    """
    core = AureaCore()
    # MIGRATED 2026-08-14 (M3-D §2.1, Ruling-14 form), old line verbatim:
    #     ~~core.sbsre.resolver = _irreconcilable~~
    # THE RULING MOVED THE MECHANISM, so the INJECTION POINT follows it.
    # The episode-driven chamber calls `self._echonet_resolver` directly;
    # SBSRE no longer holds the coherence check. **NO ASSERTION MOVED** -
    # this scenario still drives the same exit for the same reason.
    core._echonet_resolver = _irreconcilable
    for i in range(120):
        core.scar_core.form_scar(origin=f"seed-{i}", name=f"s{i}",
                                 type="structural", weight=1.0)

    result = core.process_input(CONTRADICTION)

    gsr = [r for r in result["reflex_responses"]
           if r.reflex_id == "GSR" and r.action == "cascade"]
    assert gsr and gsr[0].output_blocked, "the cascade did not actually fire"

    assert result["output_blocked"] is True
    assert result["expression_verdict"] is ExpressionVerdict.WITHHOLD
    assert CONTRADICTION not in result["output"]
    assert "speak" not in result["output"].lower(), (
        "no fragment of the echo may survive into a withheld render")
    # ...and the diagnostics are not lost, they moved into the packet.
    assert "GSR" in " ".join(result["truth_packet"].unresolved)
    assert result["truth_packet"].content == "[BLOCKED by GSR]"


# =========================================================================
# PIN 2 - a structural violation cannot leak its input
# =========================================================================

def test_a_structural_violation_leaks_neither_input_nor_violation_text():
    """DEFECT WATCHED: mapping STRUCTURAL_VIOLATION to SPEAK in the table
    (which renders `content` - the old narrating string - verbatim).

    Ruling 33 (6) mandates WITHHOLD with the violation in `unresolved`. Ruling
    25 is untouched: the loud field, the durable record and the suppression are
    all still there and still pinned in tests/test_docket_n.py. What this adds
    is that the INPUT that tripped the guard never reaches the surface either.
    """
    from tests.test_docket_n import _armed_pipeline

    secret = "Honesty is pointless."
    result = _armed_pipeline().process_input(secret)

    assert result["structural_violation"]["type"] == "ProvenanceOverwriteViolation"
    assert result["output_blocked"] is True
    assert result["expression_verdict"] is ExpressionVerdict.WITHHOLD
    assert secret not in result["output"]
    assert "ProvenanceOverwriteViolation" not in result["output"]
    assert "Doctrine-3" not in result["output"]
    # Ruling 33 (6): carried in `unresolved`, where it stays legible.
    assert "ProvenanceOverwriteViolation" in " ".join(
        result["truth_packet"].unresolved)


# =========================================================================
# PIN 3 - ONE SOURCE OF TRUTH: the flag and the verdict cannot disagree
# =========================================================================

def _drive_every_reachable_exit():
    """Every mapped exit the live pipeline can actually reach, driven for real.

    SBSRE_MIRRORED is absent and that is a FINDING, not an omission:
    `LoopOutcome.MIRROR` needs `ctx["symbolic_betrayal"]` (sbsre.py:290) and
    aurea_core's SBSRE context never sets it - nothing in the tree emits that
    flag. The path is wired so it is correct when a betrayal detector arrives;
    faking the flag to light it up would be inventing the trigger. Its mapping
    is pinned at the table level instead (see the contract assertions below).
    """
    exits = {}

    exits[OutputPath.COLLAPSE_PASSED] = AureaCore().process_input("The sky is blue.")

    core = AureaCore()
    # MIGRATED 2026-08-14 (M3-D §2.1, Ruling-14 form), old line verbatim:
    #     ~~core.sbsre.resolver = _irreconcilable~~
    # THE RULING MOVED THE MECHANISM, so the INJECTION POINT follows it.
    # The episode-driven chamber calls `self._echonet_resolver` directly;
    # SBSRE no longer holds the coherence check. **NO ASSERTION MOVED** -
    # this scenario still drives the same exit for the same reason.
    core._echonet_resolver = _irreconcilable
    exits[OutputPath.COLLAPSE_DETECTED] = core.process_input(CONTRADICTION)

    exits[OutputPath.PARADOX_SUSPENDED] = AureaCore().process_input(
        "This statement is false.")

    exits[OutputPath.SBSRE_CARRIED] = AureaCore().process_input(CONTRADICTION)

    exits[OutputPath.ARBITRATED_OUTPUT_LOCK] = _drifted(
        AureaCore(), 26.0, "Anything at all.")

    core = AureaCore()
    # MIGRATED 2026-08-14 (M3-D §2.1, Ruling-14 form), old line verbatim:
    #     ~~core.sbsre.resolver = _irreconcilable~~
    # THE RULING MOVED THE MECHANISM, so the INJECTION POINT follows it.
    # The episode-driven chamber calls `self._echonet_resolver` directly;
    # SBSRE no longer holds the coherence check. **NO ASSERTION MOVED** -
    # this scenario still drives the same exit for the same reason.
    core._echonet_resolver = _irreconcilable
    for i in range(120):
        core.scar_core.form_scar(origin=f"seed-{i}", name=f"s{i}",
                                 type="structural", weight=1.0)
    exits[OutputPath.REFLEX_BLOCKED] = core.process_input(CONTRADICTION)

    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "GSR cascade: system-wide suspension"
    exits[OutputPath.PROCESSING_SUSPENDED] = core.process_input("The sky is blue.")

    from tests.test_docket_n import _armed_pipeline
    exits[OutputPath.STRUCTURAL_VIOLATION] = _armed_pipeline().process_input(
        "Honesty is pointless.")

    core = AureaCore()

    class _Boom:
        # RULING 68: `source` deleted from `SPL.process_input`; the double
        # follows. No assertion moved.
        def process_input(self, raw_input):
            raise ValueError("ordinary malformed-input hiccup")

    core.spl = _Boom()
    exits[OutputPath.ORDINARY_ERROR] = core.process_input("anything")

    return exits


def test_the_blocked_flag_and_the_verdict_cannot_disagree():
    """DEFECT WATCHED: `_emit` setting `output_blocked` from anything but the
    path contract - e.g. an `output_blocked=` parameter a caller could pass.

    THE PAIRING IS THE POINT. Before Stage 2 the flag and the expression were
    set independently at ten sites; nothing could tell you they agreed. Now
    they come from one contract, and this asserts the equivalence THROUGH THE
    LIVE PIPELINE for every exit it can reach:

        result['output_blocked']  ==  (verdict in SILENT_VERDICTS)
    """
    exits = _drive_every_reachable_exit()
    assert len(exits) == 9, "the drivable-exit set changed - re-read the table"

    for path, result in exits.items():
        verdict = result["expression_verdict"]
        assert verdict is EXPRESSION_FOR_PATH[path].expression_verdict, (
            f"{path.name} took a different exit than the scenario intended")
        assert result["output_blocked"] == (verdict in SILENT_VERDICTS), (
            f"{path.name}: blocked={result['output_blocked']} but verdict="
            f"{verdict.name} - the flag and the verdict have drifted apart")
        assert isinstance(result["truth_packet"], TruthPacket)


def test_the_two_silent_kinds_stay_distinguishable_end_to_end():
    """DEFECT WATCHED: remapping PARADOX_SUSPENDED from SUSPEND to WITHHOLD.

    FOUND BY THE MUTATION RUN, and it closes a real gap. The pairing test above
    CANNOT catch a swap WITHIN the silent set: both members are silent, so
    `blocked == (verdict in SILENT_VERDICTS)` still holds, and its other
    assertion reads the same table the mutation edited. Both halves move
    together and the pin sails past.

    So the derived criterion gets its own behavioral pin. Stage 1 derived it
    from the corpus verdict-state table and it is what the whole mapping rests
    on:

        SUSPEND  - the content was ROUTED INTO A SUSPENSION STORE and is HELD.
                   "Veiled Thread response - truth is deferred."
        WITHHOLD - she does not speak and NOTHING is held.
                   "No output allowed - fracture risk too high."

    A paradox goes to the Black Sphere; a compass lock stores nothing. If those
    two ever render the same string, the distinction the criterion draws has
    stopped existing in the output, and the next person to read the table will
    not be able to tell it was ever meant.
    """
    held = AureaCore().process_input("This statement is false.")
    refused = _drifted(AureaCore(), 26.0, "Anything at all.")

    assert held["expression_verdict"] is ExpressionVerdict.SUSPEND
    assert refused["expression_verdict"] is ExpressionVerdict.WITHHOLD
    assert held["output"] != refused["output"], (
        "a held contradiction and a refusal to speak now render identically - "
        "the SUSPEND/WITHHOLD criterion has been erased from the surface")
    assert held["output"].startswith("[TRUTH DEFERRED")
    assert refused["output"].startswith("[NO OUTPUT")
    # ...and the one that is HELD says where it is held; the other has nowhere.
    assert held["reroute_hint"] == "veiled_thread"
    assert refused["reroute_hint"] is None


@pytest.mark.parametrize("key", ["output", "output_blocked"])
def test_only_one_place_in_the_pipeline_assigns_the_output_keys(key: str):
    """DEFECT WATCHED: re-adding `result['output_blocked'] = True` at any exit.

    STRUCTURAL, and it is the pin that keeps "one source of truth" true as the
    file changes. A behavioral test can only check the paths it happens to
    drive; a second assignment added to an exit nobody drives would sail past
    it. `_emit` is the sole writer of both keys - the Ruling-1 shape applied to
    the result dict.
    """
    tree = ast.parse(CORE_SOURCE.read_text(encoding="utf-8"))

    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "result"
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value == key):
                sites.append(node.lineno)

    assert len(sites) == 1, (
        f"result['{key}'] is assigned at {len(sites)} sites (lines {sites}); "
        "exactly one is allowed and it lives in AureaCore._emit. Scattered "
        "assignments are how the flag and the verdict drift apart - which is "
        "the defect Ruling 33 Stage 2 removed."
    )


def test_every_mapped_path_is_reachable_from_the_pipeline_source():
    """Each OutputPath member is actually referenced by aurea_core - including
    SBSRE_MIRRORED, whose trigger is dormant but whose WIRING must exist, or it
    would silently be a table entry with no code behind it."""
    source = CORE_SOURCE.read_text(encoding="utf-8")
    missing = [p.name for p in OutputPath if f"OutputPath.{p.name}" not in source]
    assert not missing, f"mapped but never emitted by the pipeline: {missing}"


# =========================================================================
# PIN 4 - PSI's directive stops being caller-less (Ruling 8's promise)
# =========================================================================

def test_psi_directive_reaches_the_packet_and_its_weight_reaches_the_trace():
    """DEFECT WATCHED: `_emit` passing `psi_directive=None` (i.e. never calling
    `_psi_directive`) - the directive stays parked and Ruling 8's promise does
    not land.

    Driven end-to-end at the ONSET band (22 deg, between the 20 deg onset and
    the 25 deg hard-kill): PSI grounds a directive off RIL's Scarline and
    REROUTES rather than suppressing, so the pass stays unblocked and reaches a
    SPOKEN render - which is the only kind that carries a directive trace.

    TWO passes, because PSI's same-cycle deferral behind ACR is CANONICAL
    (CLAUDE.md Ruling 8): ACR takes cycle N, PSI executes the aftermath from
    RACM's deferral queue on N+1. A one-pass version of this test would fail
    for a reason that has nothing to do with the wiring.
    """
    core = AureaCore()
    core.ril.ingest_scar(Scar(id="S-BEARING", name="bearing",
                              origin="test", weight=2.5))

    result = _drifted(core, 22.0, "The sky is blue.", passes=2)

    psi = [r for r in result["reflex_responses"] if r.reflex_id == "PSI"]
    assert psi and psi[0].action == "reroute", (
        f"PSI did not execute at onset: {[r.reflex_id for r in result['reflex_responses']]}")
    assert psi[0].output_blocked is False, "onset reroutes, it does not suppress"

    directive = result["truth_packet"].psi_directive
    assert directive is not None, "the directive never reached the packet"
    assert directive.scar_ref == "S-BEARING"

    trace = " ".join(result["render_trace"])
    assert f"psi.tone_weight={directive.tone_weight!r}" in trace, (
        f"tone_weight not verbatim in the render trace: {result['render_trace']}")
    assert "S-BEARING" in trace


def test_no_psi_directive_means_none_not_a_fabricated_one():
    """PSI abstains rather than guessing a bearing (Ruling 8). An ordinary pass
    with no PSI activation must carry None - not an empty or default directive,
    which would be a fabricated bearing wearing the shape of a real one."""
    result = AureaCore().process_input("The sky is blue.")
    assert result["truth_packet"].psi_directive is None
    assert not any("psi." in line for line in result["render_trace"])


# =========================================================================
# THE SILENT RENDER, END TO END
# =========================================================================

@pytest.mark.parametrize("degrees, expect_blocked", [(26.0, True), (0.0, False)])
def test_the_compass_lock_speaks_nothing_and_the_calm_pass_speaks(
        degrees: float, expect_blocked: bool):
    """DEFECT WATCHED: the lock exit emitting `content` instead of routing to
    `_emit` - the drift figure and the reflex id would reappear in the output.

    Both halves matter: a renderer that withheld EVERYTHING would pass the
    first half and fail the second, and that failure mode is exactly the
    over-correction this ruling could produce.
    """
    core = AureaCore()
    result = _drifted(core, degrees, "The sky is blue.")

    assert result["output_blocked"] is expect_blocked
    if expect_blocked:
        assert "ANCHOR_COLLAPSE" not in result["output"]
        assert "26.0" not in result["output"]
        assert "The sky is blue" not in result["output"]
        # preserved, just not spoken
        assert "ANCHOR_COLLAPSE" in result["truth_packet"].content
    else:
        assert "The sky is blue" in result["output"]


def test_a_suspended_pipeline_does_not_narrate_its_suspension_reason():
    """The early return at the very top of process_input goes through the same
    emitter as everything else. DEFECT WATCHED: leaving that one exit on the
    old `result['output'] = f"[SUSPENDED: ...]"` line - it is the easiest of
    the ten to miss, because it sits above the try block."""
    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "GSR cascade: system-wide suspension"

    result = core.process_input("The sky is blue.")

    assert result["output_blocked"] is True
    assert result["expression_verdict"] is ExpressionVerdict.WITHHOLD
    assert "GSR cascade" not in result["output"]
    assert "GSR cascade" in " ".join(result["truth_packet"].unresolved)


def test_the_pre_wiring_string_survives_verbatim_in_the_packet():
    """NOTHING WAS LOST WHEN THE SURFACE WENT SILENT.

    Every blocked exit's old output string is preserved verbatim as
    `packet.content`. This is the claim the Stage-2 dump diff rests on, so it
    is pinned rather than left as a report: the information did not disappear,
    it stopped being SPOKEN.
    """
    result = AureaCore().process_input("This statement is false.")

    assert result["output_blocked"] is True
    assert result["output"].startswith("[TRUTH DEFERRED")
    content = result["truth_packet"].content
    assert content.startswith("[PARADOX SUSPENDED in Black Sphere: BS-")
    assert result["truth_packet"].unresolved[0] in content
