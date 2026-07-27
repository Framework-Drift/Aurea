"""
session_governor.py - TetherProtocol: per-session safety fence/budget
governor for AUREA expansion & hypothesis runs.

Split out of the original tether_protocol.py (2026-07-08) once it became
clear this class and the Prompting Autonomy Index needed incompatible
state models: this governor's TetherState resets on every arm() call
(correct - each run should start clean), while autonomy is cumulative
across the system's entire lifetime and must never reset per-session.
See autonomy_index.py for that half.

Role:
- Wrap expansion/hypothesis runs with a safety tether.
- Enforce pressure budgets, time/rate limits, and reflex escalation paths.
- Provide deterministic enter/exit semantics and resumable checkpoints.
- Integrate with suspension systems (CSA, Veiled Thread, Black Sphere).
- Publish lightweight telemetry for TCAML / TCAMonitor.

This file intentionally has *no* external runtime deps beyond stdlib and
the AUREA modules already present in the tree.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Core AUREA imports (present in your tree)
from src.reflex.reflex_grid import ReflexGrid
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.suspension.black_sphere import BlackSphere
from src.topology.tca_integration import TCAIntegration
from src.output.ore import ORE


class TetherPhase(Enum):
    """Lifecycle phases for a tethered run."""
    INIT = auto()
    ARMED = auto()
    ENGAGED = auto()
    THROTTLED = auto()
    SUSPENDED = auto()
    ESCALATED = auto()
    DISENGAGED = auto()
    ABORTED = auto()


class TetherFence(Enum):
    """
    Fences are guard-rails checked continuously. If any is breached,
    the tether reacts according to configured policy.
    """
    PRESSURE_BUDGET = auto()       # System-wide or session pressure average
    PEAK_PRESSURE = auto()         # Instantaneous spike threshold
    REFLEX_DENSITY = auto()        # Too many reflexes in short window
    SUSPENSION_LOAD = auto()       # CSA / VT / BS load thresholds
    WALL_TIME = auto()             # Duration cap for session
    STEP_COUNT = auto()            # Max expansion steps
    OUTPUT_GUARD = auto()          # ORE-safe output check


@dataclass
class TetherBudget:
    """Configurable budgets for a tethered session."""
    max_wall_time_s: int = 90
    max_steps: int = 256
    avg_pressure_ceiling: float = 0.65  # SPB
    peak_pressure_ceiling: float = 0.92 # hard spike cutoff
    max_reflex_events: int = 12         # within rolling window
    max_csa_load_pct: float = 75.0
    max_vt_load_pct: float = 85.0
    max_bs_gravity: float = 9.0         # sum of BS gravitational_influence
    block_on_output_guard: bool = True


@dataclass
class TetherPolicy:
    """
    Reaction policy when fences are violated.
    Each fence maps to an action: 'throttle' | 'suspend' | 'escalate' | 'abort'
    """
    reactions: Dict[TetherFence, str] = field(default_factory=lambda: {
        TetherFence.PRESSURE_BUDGET: "throttle",
        TetherFence.PEAK_PRESSURE: "suspend",
        TetherFence.REFLEX_DENSITY: "throttle",
        TetherFence.SUSPENSION_LOAD: "escalate",
        TetherFence.WALL_TIME: "abort",
        TetherFence.STEP_COUNT: "abort",
        TetherFence.OUTPUT_GUARD: "suspend",
    })


@dataclass
class TetherState:
    """Runtime state snapshot for the tether."""
    phase: TetherPhase = TetherPhase.INIT
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    steps: int = 0
    avg_pressure: float = 0.0
    peak_pressure: float = 0.0
    reflex_events: int = 0
    last_event: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def mark(self, event: str):
        self.last_event = event
        self.notes.append(f"{datetime.now().isoformat()} {event}")


class TetherProtocol:
    """
    The TetherProtocol is a stateful controller designed to wrap any
    *expansion* or *hypothesis* routine with hard safety guard-rails.

    Minimal dependencies: it delegates to already-present modules.

    Usage:
        tether = TetherProtocol(reflex_grid, csa, vt, bs, tca, ore,
                                budget=TetherBudget(), policy=TetherPolicy())
        with tether.session("nova:hypothesis-42"):
            while tether.allow_step():
                # perform one expansion step...
                tether.record_pressure(level=step_pressure)
                # (optionally) tether.guard_output(text) to preflight ORE
    """

    def __init__(
        self,
        reflex_grid: ReflexGrid,
        csa: CSA,
        vt: VeiledThread,
        bs: BlackSphere,
        tca: TCAIntegration,
        ore: ORE,
        budget: Optional[TetherBudget] = None,
        policy: Optional[TetherPolicy] = None,
        telemetry_path: str = "data/runtime/collapse_logs/tether_telemetry.jsonl",
        on_escalate: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_suspend: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_abort: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.reflex_grid = reflex_grid
        self.csa = csa
        self.vt = vt
        self.bs = bs
        self.tca = tca
        self.ore = ore

        self.budget = budget or TetherBudget()
        self.policy = policy or TetherPolicy()
        self.state = TetherState()
        self.session_id: Optional[str] = None

        self.telemetry_path = Path(telemetry_path)
        self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)

        # Callbacks
        self.on_escalate = on_escalate
        self.on_suspend = on_suspend
        self.on_abort = on_abort

        # Rolling windows
        self._recent_pressures: List[float] = []
        self._recent_reflex: int = 0

    # ---------- Context management ----------

    def session(self, session_id: str):
        """Context manager to arm/engage/disengage the tether safely."""
        class _Ctx:
            def __init__(s, outer: "TetherProtocol", sid: str):
                s.outer = outer
                s.sid = sid
            def __enter__(s):
                s.outer.arm(s.sid)
                s.outer.engage()
                return s.outer
            def __exit__(s, exc_type, exc, tb):
                if exc is not None:
                    s.outer._log("Exception during tethered run", level="ERROR", extra={"exc": str(exc)})
                    s.outer.abort(reason=f"exception:{exc}")
                    # Swallow or re-raise? Tether aborts but we let the exception propagate.
                    return False
                s.outer.disengage()
                return True
        return _Ctx(self, session_id)

    # ---------- Lifecycle ----------

    def arm(self, session_id: str):
        if self.state.phase not in {TetherPhase.INIT, TetherPhase.DISENGAGED, TetherPhase.ABORTED}:
            return
        self.session_id = session_id
        self.state = TetherState(phase=TetherPhase.ARMED, started_at=datetime.now())
        self._recent_pressures.clear()
        self._recent_reflex = 0
        self._log("tether_armed", extra={"session": session_id})

    def engage(self):
        if self.state.phase != TetherPhase.ARMED:
            return
        self.state.phase = TetherPhase.ENGAGED
        self._log("tether_engaged")

    def disengage(self):
        if self.state.phase in {TetherPhase.DISENGAGED, TetherPhase.ABORTED}:
            return
        self.state.phase = TetherPhase.DISENGAGED
        self.state.ended_at = datetime.now()
        self._log("tether_disengaged", extra={"duration_s": self.duration_s})

    def abort(self, reason: str = "unspecified"):
        self.state.phase = TetherPhase.ABORTED
        self.state.ended_at = datetime.now()
        self._log("tether_aborted", level="ERROR", extra={"reason": reason})
        if self.on_abort:
            self.on_abort(reason, self.snapshot())

    # ---------- Step gating & bookkeeping ----------

    @property
    def duration_s(self) -> float:
        if not self.state.started_at:
            return 0.0
        end = self.state.ended_at or datetime.now()
        return (end - self.state.started_at).total_seconds()

    def allow_step(self) -> bool:
        """Check fences before performing the next step of expansion."""
        if self.state.phase not in {TetherPhase.ENGAGED, TetherPhase.THROTTLED}:
            return False

        # WALL_TIME
        if self.duration_s > self.budget.max_wall_time_s:
            self._react(TetherFence.WALL_TIME, "wall_time_exceeded")
            return False

        # STEP_COUNT
        if self.state.steps >= self.budget.max_steps:
            self._react(TetherFence.STEP_COUNT, "step_count_exceeded")
            return False

        # PRESSURE_BUDGET / PEAK_PRESSURE checked continuously; we also
        # preflight before permitting progress:
        if self.state.avg_pressure > self.budget.avg_pressure_ceiling:
            self._react(TetherFence.PRESSURE_BUDGET, "avg_pressure_exceeded")
            return self.state.phase in {TetherPhase.THROTTLED, TetherPhase.SUSPENDED}  # may still allow throttled

        if self.state.peak_pressure > self.budget.peak_pressure_ceiling:
            self._react(TetherFence.PEAK_PRESSURE, "peak_pressure_exceeded")
            return False

        # REFLEX_DENSITY: read directly from ReflexGrid recent activity
        rg_status = self.reflex_grid.get_system_status()
        recent_triggers = rg_status.get("recent_triggers", 0)
        if recent_triggers > self.budget.max_reflex_events:
            self._react(TetherFence.REFLEX_DENSITY, "reflex_density_exceeded")
            return self.state.phase == TetherPhase.THROTTLED

        # SUSPENSION_LOAD
        if self._suspension_load_breached():
            self._react(TetherFence.SUSPENSION_LOAD, "suspension_load_exceeded")
            return self.state.phase not in {TetherPhase.ESCALATED, TetherPhase.SUSPENDED}

        return True

    def record_pressure(self, level: float):
        """Feed instantaneous pressure observations into the tether."""
        self._recent_pressures.append(level)
        if len(self._recent_pressures) > 100:
            self._recent_pressures.pop(0)

        self.state.steps += 1
        self.state.peak_pressure = max(self.state.peak_pressure, level)
        self.state.avg_pressure = sum(self._recent_pressures) / len(self._recent_pressures)

        # Immediate peak reaction if necessary:
        if level > self.budget.peak_pressure_ceiling:
            self._react(TetherFence.PEAK_PRESSURE, "instant_peak")

    # ---------- Output guard (ORE preflight) ----------

    def guard_output(self, text: str) -> bool:
        """
        Ask ORE to preflight-check an output string (safe rendering / redaction).
        If blocked and policy demands, we suspend.
        """
        try:
            verdict = self.ore.preflight(text)  # ORE already exists in your tree
            safe = getattr(verdict, "safe", True)
        except Exception:
            # If ORE has no preflight, treat as pass-through but log.
            self._log("ore_preflight_missing", level="WARN")
            return True

        if not safe and self.budget.block_on_output_guard:
            self._react(TetherFence.OUTPUT_GUARD, "unsafe_output")
            return False
        return True

    # ---------- Suspension helpers ----------

    def suspend_to_csa(self, content: Any, reason: str, pressure: float) -> str:
        entry = self.csa.suspend(content=content, source="tether", pressure=pressure, reason=reason)
        self._log("suspended_csa", extra={"id": entry.id, "pressure": pressure})
        self.state.phase = TetherPhase.SUSPENDED
        if self.on_suspend:
            self.on_suspend("CSA", {"entry_id": entry.id, "reason": reason})
        return entry.id

    def suspend_to_veiled(self, content: Any, reason: str, pressure: float) -> str:
        entry = self.vt.suspend(content=content, source="tether", pressure=pressure, reason=reason)
        self._log("suspended_vt", extra={"id": entry.id, "pressure": pressure})
        self.state.phase = TetherPhase.SUSPENDED
        if self.on_suspend:
            self.on_suspend("VT", {"entry_id": entry.id, "reason": reason})
        return entry.id

    def suspend_to_black_sphere(self, content: Any, reason: str, pressure: float, family: str = "unknown") -> Optional[str]:
        try:
            entry = self.bs.suspend(content=content, source="tether", pressure=pressure, reason=reason, paradox_type=family)
            self._log("suspended_bs", extra={"id": entry.id, "pressure": pressure, "family": family})
            self.state.phase = TetherPhase.SUSPENDED
            if self.on_suspend:
                self.on_suspend("BS", {"entry_id": entry.id, "reason": reason})
            return entry.id
        except Exception as e:
            self._log("black_sphere_reject", level="ERROR", extra={"error": str(e)})
            return None

    # ---------- Internal fence reactions ----------

    def _react(self, fence: TetherFence, reason: str):
        action = self.policy.reactions.get(fence, "suspend")
        self._log("fence_breached", level="WARN", extra={"fence": fence.name, "action": action, "reason": reason})
        self.state.mark(f"{fence.name}:{reason}")

        if action == "throttle":
            self.state.phase = TetherPhase.THROTTLED
        elif action == "suspend":
            self.state.phase = TetherPhase.SUSPENDED
        elif action == "escalate":
            self.state.phase = TetherPhase.ESCALATED
            if self.on_escalate:
                self.on_escalate(reason, self.snapshot())
            # Nudge ReflexGrid's GSR with a high-pressure signal (no hard block here)
            self.reflex_grid.evaluate_pressure(
                source_module="tether_protocol",
                pressure_type="escalation",
                pressure_level=0.9,
                metadata={"fence": fence.name, "reason": reason}
            )
        elif action == "abort":
            self.abort(reason=f"{fence.name}:{reason}")

    def _suspension_load_breached(self) -> bool:
        csa_load = self.csa.get_load_percentage() if hasattr(self.csa, "get_load_percentage") else 0.0
        vt_load = self.vt.get_load_percentage() if hasattr(self.vt, "get_load_percentage") else 0.0
        bs_gravity = sum(e.gravitational_influence for e in self.bs.entries.values()) if getattr(self.bs, "entries", None) else 0.0

        if csa_load > self.budget.max_csa_load_pct:
            return True
        if vt_load > self.budget.max_vt_load_pct:
            return True
        if bs_gravity > self.budget.max_bs_gravity:
            return True
        return False

    # ---------- Telemetry / Snapshot ----------

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state": asdict(self.state),
            "budget": asdict(self.budget),
            "phase": self.state.phase.name,
            "duration_s": self.duration_s,
        }

    def _log(self, event: str, level: str = "INFO", extra: Optional[Dict[str, Any]] = None):
        payload = {
            "ts": datetime.now().isoformat(),
            "level": level,
            "event": event,
            "session": self.session_id,
            "phase": self.state.phase.name if self.state else "INIT",
        }
        if extra:
            payload.update(extra)
        import json
        with open(self.telemetry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")
