"""
test_rb_durability.py - Ruling 11 (ruled 2026-07-21): RB forensic-log
durability is scope-tiered.

The defect this closes: default autoflush=False kept every forensic entry in
memory only - and the session bearing a cascade is the least likely to survive
to read its own log. The ruled shape:

  - GLOBAL-scope reflex entries flush to disk IMMEDIATELY, best-effort: the
    flush NEVER gates the reflex response - a logging failure must not disable
    a safety suppression.
  - LOCAL entries buffer, bounded; boundaries are cap / drain() / close().
    Overflow FLUSHES, never drops.
  - autoflush=True stays the force-all-immediate override.
  - Cascade is durable because GSR is GLOBAL (Ruling 7 decomposition), not
    because it is named - there is no cascade_meta / action=='cascade' check
    in the flush path.
  - RBSystem stays scope-BLIND (durable is a caller bool; Scope never imports
    into rb_system - racm imports rb_system, it would cycle). The Grid's
    _log_execution is where scope becomes durability.

Every RBSystem here takes an explicit tmp log_path - no real logs/ writes
(the autouse conftest fixture guards the rest of the suite the same way).

DO NOT weaken these tests. They pin an architect ruling.
"""

import json

from src.reflex.rb_system import BehaviorType, RBSystem
from src.reflex.reflex_grid import ReflexGrid


def _read_lines(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _grid(tmp_path):
    log = tmp_path / "rb.jsonl"
    grid = ReflexGrid(rb_system=RBSystem(log_path=str(log)))
    grid.reflexes["GSR"].alert_callback = lambda message, severity: None
    return grid, log


# ---------------------------------------------------------------------
# (1) GLOBAL is durable NOW: the cascade is on disk before anyone flushes
# ---------------------------------------------------------------------

def test_global_cascade_is_on_disk_immediately_no_manual_flush(tmp_path):
    """sbsre_abort@1.0 drives GSR's cascade branch (the Ruling 7 decomposition).
    GSR is GLOBAL, so the decomposed SUSPEND must be on disk the moment
    record() returns - no drain, no close, no autoflush."""
    grid, log = _grid(tmp_path)

    grid.evaluate_pressure(
        source_module="SBSRE", pressure_type="sbsre_abort",
        pressure_level=1.0, metadata={"thread_id": "SBSRE-0001"})

    lines = _read_lines(log)
    on_disk = [l for l in lines if l.get("reflex_triggered") == "GSR"]
    assert len(on_disk) == 1, "the GLOBAL entry is durable at record() time"
    entry = on_disk[0]
    assert entry["behavior_type"] == "suspend"
    assert entry["cascade_meta"]["decomposed_from"] == "cascade"
    assert entry["scope"] == "GLOBAL", "v1.2 provenance for the durability tier"


def test_cascade_durability_comes_from_scope_not_from_being_named(tmp_path):
    """GSR's ordinary >0.85 suspend band (no cascade anywhere in the response)
    is JUST as durable - same scope, same tier. If a fix ever keys durability
    on action=='cascade' or cascade_meta, this breaks."""
    grid, log = _grid(tmp_path)

    grid.evaluate_pressure(
        source_module="aurea_core", pressure_type="cascade_warning",
        pressure_level=0.9, metadata={})

    on_disk = [l for l in _read_lines(log) if l.get("reflex_triggered") == "GSR"]
    assert len(on_disk) == 1, "ordinary GLOBAL suspend hits disk immediately too"
    assert on_disk[0]["behavior_type"] == "suspend"
    assert "cascade_meta" not in on_disk[0], "not cascade-class - and still durable"


# ---------------------------------------------------------------------
# (2) LOCAL buffers to a boundary - not per-entry flushed, never lost
# ---------------------------------------------------------------------

def test_local_entry_buffers_then_lands_on_boundary_drain(tmp_path):
    """A LOCAL-scope reflex execution (ICA's 0.7-0.9 reroute band - 0.8 stays
    under GSR's 0.85 open gate, so no GLOBAL entry muddies the file) and RACM's
    own bookkeeping entries stay in the buffer - the file holds nothing until
    a boundary."""
    grid, log = _grid(tmp_path)

    responses = grid.evaluate_pressure(
        source_module="RIL", pressure_type="identity_fracture",
        pressure_level=0.8, metadata={})
    assert any(r.reflex_id == "ICA" and r.action == "reroute" for r in responses)

    assert _read_lines(log) == [], "LOCAL entries are not per-entry flushed"
    assert len(grid.rb._buffer) > 0

    flushed = grid.rb.drain()
    assert flushed == len(grid.rb.entries), "the boundary flushes everything held"
    assert grid.rb._buffer == []

    on_disk = _read_lines(log)
    ica = [l for l in on_disk if l.get("reflex_triggered") == "ICA"
           and l.get("behavior_type") == "reroute"]
    assert len(ica) == 1, "the buffered LOCAL entry survived to disk"
    assert ica[0]["scope"] == "LOCAL"


def test_close_is_the_session_boundary(tmp_path):
    rb = RBSystem(log_path=str(tmp_path / "rb.jsonl"))
    rb.record("ICA", BehaviorType.SUPPRESS, symbolic_context="session work")
    assert _read_lines(rb.log_path) == []
    assert rb.close() == 1
    assert len(_read_lines(rb.log_path)) == 1


# ---------------------------------------------------------------------
# (3) the buffer is BOUNDED: cap triggers a full flush, nothing drops
# ---------------------------------------------------------------------

def test_buffer_cap_triggers_flush_nothing_dropped(tmp_path):
    """Fill past LOCAL_BUFFER_CAP. Overflow FLUSHES - the file plus the buffer
    always account for every entry recorded, and the buffer never exceeds cap."""
    rb = RBSystem(log_path=str(tmp_path / "rb.jsonl"))
    cap = RBSystem.LOCAL_BUFFER_CAP
    total = cap + 5

    for i in range(total):
        rb.record("ICA", BehaviorType.SUPPRESS, symbolic_context=f"entry {i}")
        assert len(rb._buffer) < cap, "buffer is bounded - cap flushes it"

    on_disk = _read_lines(rb.log_path)
    assert len(on_disk) == cap, "hitting cap flushed the full buffer"
    assert len(on_disk) + len(rb._buffer) == total, "nothing was dropped"
    assert rb.flush_failures == []

    # And the remainder still lands at the next boundary - no gaps.
    rb.drain()
    ids = [l["id"] for l in _read_lines(rb.log_path)]
    assert ids == [e.id for e in rb.entries], "disk holds every entry, in order"


# ---------------------------------------------------------------------
# (4) a flush failure NEVER raises into the reflex path - and is legible
# ---------------------------------------------------------------------

def test_flush_failure_is_recorded_not_raised_and_entry_is_carried(tmp_path):
    """Break the sink (log path parented under a FILE, so mkdir fails). A
    durable record() must return normally - the suppression it logs must not
    die of a disk error - with the failure on flush_failures and the entry
    CARRIED in the buffer for boundary retry, not dropped."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory")
    rb = RBSystem(log_path=str(blocker / "rb.jsonl"))

    entry = rb.record("GSR", BehaviorType.SUSPEND, durable=True,
                      symbolic_context="cascade under a dead disk")

    assert entry in rb.entries, "record() completed despite the dead sink"
    assert len(rb.flush_failures) == 1, "the failure is legible, exactly once"
    assert "entry_ids" in rb.flush_failures[0]
    assert entry.id in rb.flush_failures[0]["entry_ids"]
    assert entry in rb._buffer, "carried for boundary retry - never dropped"

    # Failed boundary: still no raise, buffer retained.
    assert rb.drain() == 0
    assert entry in rb._buffer

    # Sink recovers: the carried entry finally lands.
    rb.log_path = tmp_path / "recovered.jsonl"
    assert rb.drain() == 1
    assert [l["id"] for l in _read_lines(rb.log_path)] == [entry.id]


def test_flush_failure_does_not_block_the_grid_reflex_path(tmp_path):
    """End-to-end: a cascade cycle with a broken log sink still executes,
    still suppresses. The reflex response is what matters; the log is
    best-effort."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory")
    grid = ReflexGrid(rb_system=RBSystem(log_path=str(blocker / "rb.jsonl")))
    grid.reflexes["GSR"].alert_callback = lambda message, severity: None

    responses = grid.evaluate_pressure(
        source_module="SBSRE", pressure_type="sbsre_abort",
        pressure_level=1.0, metadata={})

    gsr = next(r for r in responses if r.reflex_id == "GSR")
    assert gsr.action == "cascade" and gsr.output_blocked, (
        "the safety suppression fired - logging failure did not disable it")
    assert len(grid.rb.flush_failures) >= 1, "and the failure is on the surface"


# ---------------------------------------------------------------------
# (5) autoflush=True stays the force-all-immediate override
# ---------------------------------------------------------------------

def test_autoflush_forces_local_entries_to_disk_immediately(tmp_path):
    rb = RBSystem(log_path=str(tmp_path / "rb.jsonl"), autoflush=True)
    rb.record("ICA", BehaviorType.SUPPRESS, symbolic_context="forced")
    lines = _read_lines(rb.log_path)
    assert len(lines) == 1, "autoflush overrides the LOCAL buffer tier"
    assert rb._buffer == []
