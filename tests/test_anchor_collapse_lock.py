"""
test_anchor_collapse_lock.py - Ruling 6: the anchor-collapse output lock is the
CONSEQUENCE of RACM authorizing ACR's suppress, never compass's own drift-past-line flag.

Covers:
- drift past the hard-kill line, ACR uncontested -> RACM authorizes suppress ->
  reading.reflex_responses carries an executed ANCHOR_COLLAPSE output_blocked=True.
- drift past the hard-kill line, ACR outranked and deferred by RACM (a higher-priority,
  overlapping-affected-systems reflex wins instead) -> no executed output_blocked in
  reading.reflex_responses, even though drift crossed the line. The lock follows
  arbitration, not a threshold.
- drift_past_lock_line is a compass-owned DIAGNOSTIC, not a gate: it can be True on a
  reading where nothing executed with output_blocked=True.
- the inverse: drift_past_lock_line can be FALSE (total disorientation drifts 0.0 by
  construction) while output IS locked anyway, because compass_disorientation pressure
  drives GSR to an authorized suppress. The lock tracks arbitration in both directions,
  not the drift diagnostic in either direction.

All four exercise the real ReflexGrid + RACM (no mocking of arbitration) - only the
anchor-derivation seam (_north/_south/_east/_west/_drift) is controlled, which is exactly
the boundary CSE documents itself as owning ("CSE MEASURES drift").
"""

from unittest.mock import patch

import pytest

from src.identity.compass import CompassStabilityEngine, AnchorReading, Direction
from src.reflex.reflex_grid import ReflexGrid


def _present(direction: Direction) -> AnchorReading:
    return AnchorReading(direction=direction, mass=1.0)


def _absent(direction: Direction) -> AnchorReading:
    return AnchorReading(direction=direction, mass=0.0)


def _reading_at_drift(cse: CompassStabilityEngine, drift: float):
    with patch.object(CompassStabilityEngine, '_north', return_value=_present(Direction.NORTH)), \
         patch.object(CompassStabilityEngine, '_south', return_value=_present(Direction.SOUTH)), \
         patch.object(CompassStabilityEngine, '_east', return_value=_present(Direction.EAST)), \
         patch.object(CompassStabilityEngine, '_west', return_value=_present(Direction.WEST)), \
         patch.object(CompassStabilityEngine, '_drift', return_value=drift):
        return cse.read()


@pytest.fixture
def grid():
    return ReflexGrid()


@pytest.fixture
def cse(grid):
    return CompassStabilityEngine(reflex_grid=grid)


def test_hard_kill_drift_authorizes_acr_suppress_and_locks(cse):
    """26 deg is past the 25 deg hard-kill line and uncontested (pressure 0.289 clears
    only ACR's own thresholds, not ICA's 0.7 or GSR's 0.85) - RACM authorizes ACR's
    suppress outright, and that authorized response is what a caller must lock on."""
    reading = _reading_at_drift(cse, 26.0)

    assert reading.drift_past_lock_line is True

    acr = next((r for r in reading.reflex_responses if r.reflex_id == "ANCHOR_COLLAPSE"), None)
    assert acr is not None, "ACR should have executed uncontested at this pressure level"
    assert acr.output_blocked is True
    assert acr.action == "suppress"


def test_deferred_acr_does_not_lock(cse, grid):
    """80 deg drift emits anchor_collapse at 0.889 - past ACR's hard-kill band AND past
    GSR's 0.85 threshold. GSR is the one canon-OPEN reflex (trigger_types=None,
    Ruling 10 / 2a:583), so it claims the anchor_collapse pressure too; it outranks ACR
    (rank 1, GLOBAL), a GLOBAL winner runs alone, and RACM defers ACR. GSR's response
    in this band is `suspend` with output_blocked=False - so nothing locks.

    [Ruling 10 correction, 2026-07-20: this test previously staged the deferral with
    ICA at 67.5 deg (0.75), relying on the magnitude-only base gate to pull ICA into an
    anchor_collapse cycle - exactly the spillover seam Ruling 10 closed. ICA no longer
    claims anchor_collapse (not in its Lexicon-11 set); the ruled way to outrank ACR on
    its own pressure type is GSR's open gate.]

    The Ruling-6 assertion is unchanged: drift crossing the hard-kill line is necessary
    but NOT sufficient for a lock. Without RACM's authorization, ACR never executes and
    nothing in reflex_responses carries output_blocked - even though the drift-diagnostic
    still correctly reports the line was crossed.
    """
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None
    reading = _reading_at_drift(cse, 80.0)

    assert reading.drift_past_lock_line is True
    acr = next((r for r in reading.reflex_responses if r.reflex_id == "ANCHOR_COLLAPSE"), None)
    assert acr is None, "ACR should have been deferred by RACM, not executed"
    assert not any(r.output_blocked for r in reading.reflex_responses), (
        "no reflex actually authorized to lock output this cycle - the lock must not fire")


def test_drift_past_lock_line_is_diagnostic_not_gate(cse, grid):
    """Same reading as the deferred case: the drift-diagnostic and the arbitrated lock
    are independent signals. A caller that gates on drift_past_lock_line instead of
    reflex_responses reintroduces the inline flag Ruling 6 removed.

    [Ruling 10 correction: drift moved 67.5 -> 80 deg with the deferred-ACR test above
    - the decoupling under test is unchanged, only the reflex that outranks ACR is
    (GSR via its canon-OPEN gate, not magnitude-spilled ICA).]"""
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None
    reading = _reading_at_drift(cse, 80.0)

    assert reading.drift_past_lock_line is True
    locked = any(r.output_blocked for r in reading.reflex_responses)
    assert locked is False, "drift_past_lock_line=True must not, by itself, imply a lock"


def test_total_disorientation_locks_via_gsr_not_drift(cse, grid):
    """No anchors remain in any quadrant: disoriented=True, and the real _drift() (not
    mocked here - only the four anchor accessors are) returns 0.0 for an all-zero vector
    per its own `if not any(vector): return 0.0`. Pre-Ruling-6, the inline flag
    (`drift > OUTPUT_LOCK_DEGREES`) would have stayed False here - she spoke fluently at
    her most disoriented.

    compass_disorientation registers at pressure level 1.0, which clears GSR's 0.85
    threshold through its canon-OPEN gate (trigger_types=None - the one all-domain
    failsafe, Ruling 10 / 2a:583; every other reflex is now type-gated). GSR outranks
    everything (rank 1, GLOBAL) and RACM authorizes its suppress. That authorized
    response is what locks output now - not the drift diagnostic, which is False the
    entire time. This is the exact inversion CLAUDE.md's Ruling-6 row calls out.

    GSR's default alert_callback writes to data/collapse_logs/gsr_alerts.jsonl - swapped
    for a no-op here so this test never touches real data, same discipline
    test_autonomy_index.py already applies to data/scars.json / data/echoes.jsonl.
    """
    grid.reflexes['GSR'].alert_callback = lambda message, severity: None

    with patch.object(CompassStabilityEngine, '_north', return_value=_absent(Direction.NORTH)), \
         patch.object(CompassStabilityEngine, '_south', return_value=_absent(Direction.SOUTH)), \
         patch.object(CompassStabilityEngine, '_east', return_value=_absent(Direction.EAST)), \
         patch.object(CompassStabilityEngine, '_west', return_value=_absent(Direction.WEST)):
        reading = cse.read()

    assert reading.disoriented is True
    assert reading.drift == 0.0
    assert reading.drift_past_lock_line is False, (
        "the old drift-flag would NOT have locked here - that is precisely the bug Ruling "
        "6 fixes")

    gsr = next((r for r in reading.reflex_responses if r.reflex_id == "GSR"), None)
    assert gsr is not None, "GSR should have executed on compass_disorientation pressure"
    assert gsr.output_blocked is True

    assert any(r.output_blocked for r in reading.reflex_responses) is True, (
        "output must be locked by the arbitrated reflex even though drift_past_lock_line "
        "is False - the lock follows RACM's authorization, not the drift diagnostic")
