"""
rb_system.py - Reflex Behavior Log System (RB System) v1.2

Canon: 2b_Collapse_Reflex_Engine.txt, "Reflex Behavior Log System (RB System) - v1.1"
Class: Logging Subsystem / Reflex Grid Submodule. Non-autonomous archival layer.

    "If my reflexes are how I survive collapse, then this is how I remember why."

OWNERSHIP (Ruling 1 - one writer per store)
-------------------------------------------
RBSystem owns the reflex behavior log. RACM and the Reflex Grid do not append to
it directly; they call RBSystem.record(). One log, one schema, no parallel
lock-event log (v1.1 schema note).

BehaviorType is a CLOSED ENUM (closed 2026-07-05, item #49). Additions require a
manifest ruling - do not extend it in code.

DURABILITY (Ruling 11, ruled 2026-07-21 - v1.2)
-----------------------------------------------
Before this ruling, default autoflush=False kept every forensic entry in memory
only - and the session bearing a cascade is the least likely to survive to read
its own log. Durability is now scope-TIERED but RBSystem stays scope-BLIND:

  - The CALLER decides the tier via record(..., durable=...). The Grid's
    _log_execution sets durable=(reflex.scope == Scope.GLOBAL). Scope is NEVER
    imported here - racm imports rb_system, so importing racm's Scope back
    would cycle. RBSystem sees only a bool.
  - durable=True (or autoflush=True, the force-all override) flushes THAT entry
    to disk immediately, BEST-EFFORT: a write failure is recorded on
    `flush_failures` and the entry joins the buffer for boundary retry. The
    flush NEVER raises into the caller - a logging failure must not disable a
    safety suppression.
  - Everything else buffers, bounded by LOCAL_BUFFER_CAP. Boundary flushes:
    buffer at cap, explicit drain(), session close(). Overflow FLUSHES the
    buffer - it never drops entries and never grows past the cap while the
    sink is healthy. If the sink is broken, entries are RETAINED for the next
    boundary (carried, not dropped - the failure surface is `flush_failures`).
  - Cascade durability is a CONSEQUENCE of GSR being GLOBAL (Ruling 7
    decomposition), not of being named: there is no cascade_meta or
    action=='cascade' check anywhere in this flush path.

On-disk line order is therefore not strict event order (durable entries jump
the buffer); entry ids and timestamps reconstruct the sequence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BehaviorType(Enum):
    """CLOSED ENUM (2b, RB System v1.1 section II). Do not extend without a ruling."""
    SUPPRESS = "suppress"
    REROUTE = "reroute"
    SUSPEND = "suspend"
    DELAY = "delay"
    SCAR_GRAFT = "scar_graft"
    OFFLOAD = "offload"
    DEFER = "defer"
    EXPIRE = "expire"
    PREEMPT = "preempt"
    LOCK_GRANT = "lock_grant"
    LOCK_DENY = "lock_deny"


@dataclass
class RBEntry:
    """One reflex behavior log entry (2b, section III + v1.1 schema additions).

    For lock_grant / lock_deny entries, `reflex_triggered` holds the REQUESTING
    ACTION ID and `affected_systems` includes TCAML (v1.1 schema note).
    """
    id: str
    reflex_triggered: str
    behavior_type: BehaviorType
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    affected_systems: List[str] = field(default_factory=list)
    symbolic_context: str = ""
    outcome: Dict[str, Any] = field(default_factory=dict)
    scar_seeds: List[str] = field(default_factory=list)
    cae_id: Optional[str] = None
    # v1.1: present only on defer / expire entries.
    deferred_cycles: Optional[int] = None
    ttl_remaining: Optional[int] = None
    # Ruling 7 (ruled 2026-07-19, implemented 2026-07-20): present ONLY on entries
    # that DECOMPOSE a GSR cascade. A cascade is not a BehaviorType - the enum is
    # closed - it is control flow that decomposes into its constituent behavior
    # (a system-wide SUSPEND, recorded as such) plus this meta-fact: that the
    # suspension was cascade-class (coherence-collapse-triggered), distinguishable
    # from the ordinary >0.85 suspend band.
    # PARKED SURFACE (RIL-Nova / ACR-TCAML pattern): CTL, the ruled home of the
    # cascade meta-event, is unbuilt. Until CTL exists, this field is where the
    # fact survives - legible and queryable. Do not fabricate a CTL to consume it;
    # when CTL is built it reads this field (or supersedes it, by ruling).
    cascade_meta: Optional[Dict[str, Any]] = None
    # Ruling 11 (v1.2): the recording reflex's scope as a plain string
    # ("GLOBAL"/"LOCAL") - provenance for the durability tier. A string, not the
    # Scope enum: racm imports rb_system, so the enum cannot come back here
    # without a cycle. None on entries from scope-less callers (RACM's own
    # lock/queue events); to_dict already strips None, so v1.1 readers see
    # nothing new.
    scope: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["behavior_type"] = self.behavior_type.value
        d["timestamp"] = self.timestamp.isoformat()
        return {k: v for k, v in d.items() if v is not None}


class RBSystem:
    """The forensic memory of symbolic defense. Append-only."""

    # Resolved at CONSTRUCTION, not at def-time, so a test session can point
    # every RBSystem - including ones modules build internally - somewhere
    # disposable. There is deliberately NO injectable no-op sink: a forensic
    # log you can silently disable is not a forensic log. Redirect the path.
    DEFAULT_LOG_PATH = "data/runtime/logs/reflex_behavior.jsonl"

    # COINED (Ruling 11, 2026-07-21): canon names the durability tiers but no
    # buffer magnitude. One grid pressure cycle yields single-digit RB entries
    # (each executed reflex logs at most one behavior; RACM adds defer/suppress/
    # lock entries per contender - Core set is 4 reflexes). 64 therefore
    # amortizes disk writes across several full arbitration cycles in a reflex
    # storm, while capping worst-case LOCAL forensic loss on a hard crash at
    # ~64 lines (a few KB) - and every GLOBAL/safety entry is already on disk
    # regardless of this cap. Registered in Aurea Build/COINED_CONSTANTS.md.
    LOCAL_BUFFER_CAP = 64

    def __init__(self, log_path: Optional[str] = None,
                 autoflush: bool = False):
        self.entries: List[RBEntry] = []
        self.log_path = Path(log_path) if log_path is not None \
            else Path(self.DEFAULT_LOG_PATH)
        self.autoflush = autoflush
        # Entries awaiting a boundary flush (Ruling 11). Refs into self.entries,
        # not a second log - Ruling 1 still holds: one log, one schema.
        self._buffer: List[RBEntry] = []
        # The legible failure surface: one dict per failed write attempt.
        # Failures land HERE, never in the caller's stack (Ruling 11).
        self.flush_failures: List[Dict[str, Any]] = []
        self._seq = 0

    def next_id(self) -> str:
        self._seq += 1
        return f"RB-{self._seq:04d}"

    def record(self, reflex_triggered: str, behavior_type: BehaviorType,
               durable: bool = False, **kwargs: Any) -> RBEntry:
        """The ONLY write path into the reflex behavior log.

        Ruling 11: `durable` is the caller's scope verdict (the Grid passes
        True for GLOBAL-scope reflexes; RBSystem itself never sees Scope).
        durable or autoflush -> immediate best-effort flush of this entry;
        a write failure is recorded and the entry joins the buffer for
        boundary retry - record() NEVER raises on a sink error. Otherwise
        the entry buffers until cap / drain() / close().
        """
        entry = RBEntry(
            id=self.next_id(),
            reflex_triggered=reflex_triggered,
            behavior_type=behavior_type,
            **kwargs,
        )
        self.entries.append(entry)
        if durable or self.autoflush:
            if not self._write([entry]):
                self._buffer.append(entry)
        else:
            self._buffer.append(entry)
            if len(self._buffer) >= self.LOCAL_BUFFER_CAP:
                self.drain()
        return entry

    def flush(self, entry: RBEntry) -> bool:
        """Best-effort single-entry flush (v1.1 surface, wrapped by Ruling 11:
        it reports failure instead of raising it)."""
        return self._write([entry])

    def drain(self) -> int:
        """Flush every buffered entry to disk - the explicit boundary (also
        called on cap and at session close()). Returns the count flushed. On a
        sink failure the buffer is RETAINED for the next boundary: carried,
        never dropped; the failure is on `flush_failures`."""
        if not self._buffer:
            return 0
        if not self._write(self._buffer):
            return 0
        flushed = len(self._buffer)
        self._buffer.clear()
        return flushed

    def close(self) -> int:
        """Session-close boundary (Ruling 11): drain whatever this session
        still holds. The session bearing a cascade is the least likely to
        survive to read its own log - callers owning session teardown call
        this so LOCAL history outlives the process."""
        return self.drain()

    def _write(self, entries: List[RBEntry]) -> bool:
        """Append entries to the log file. Returns success and NEVER raises:
        the flush must not gate the reflex path (Ruling 11) - a disk error
        must not disable a safety suppression. Any failure becomes a
        `flush_failures` record instead."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a") as f:
                for entry in entries:
                    f.write(json.dumps(entry.to_dict(), default=str) + "\n")
            return True
        except Exception as exc:  # any write error, by ruling - not a bare pass
            self.flush_failures.append({
                "timestamp": datetime.now().isoformat(),
                "error": f"{type(exc).__name__}: {exc}",
                "entry_ids": [e.id for e in entries],
            })
            return False

    # --- read helpers (any module may read) ------------------------------

    def by_reflex(self, reflex_id: str) -> List[RBEntry]:
        return [e for e in self.entries if e.reflex_triggered == reflex_id]

    def by_behavior(self, behavior: BehaviorType) -> List[RBEntry]:
        return [e for e in self.entries if e.behavior_type is behavior]

    def consecutive_expiries(self, reflex_id: str) -> int:
        """Overflow Policy 5: two consecutive expiries of the same reflex type
        escalate. Counts the tail run of expire entries for this reflex."""
        run = 0
        for e in reversed(self.by_reflex(reflex_id)):
            if e.behavior_type is BehaviorType.EXPIRE:
                run += 1
            else:
                break
        return run
