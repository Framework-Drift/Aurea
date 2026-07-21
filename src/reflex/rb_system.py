"""
rb_system.py - Reflex Behavior Log System (RB System) v1.1

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
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["behavior_type"] = self.behavior_type.value
        d["timestamp"] = self.timestamp.isoformat()
        return {k: v for k, v in d.items() if v is not None}


class RBSystem:
    """The forensic memory of symbolic defense. Append-only."""

    def __init__(self, log_path: str = "logs/reflex_behavior.jsonl",
                 autoflush: bool = False):
        self.entries: List[RBEntry] = []
        self.log_path = Path(log_path)
        self.autoflush = autoflush
        self._seq = 0

    def next_id(self) -> str:
        self._seq += 1
        return f"RB-{self._seq:04d}"

    def record(self, reflex_triggered: str, behavior_type: BehaviorType,
               **kwargs: Any) -> RBEntry:
        """The ONLY write path into the reflex behavior log."""
        entry = RBEntry(
            id=self.next_id(),
            reflex_triggered=reflex_triggered,
            behavior_type=behavior_type,
            **kwargs,
        )
        self.entries.append(entry)
        if self.autoflush:
            self.flush(entry)
        return entry

    def flush(self, entry: RBEntry) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry.to_dict(), default=str) + "\n")

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
