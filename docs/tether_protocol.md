# Tether Protocol (Phase‑3 Safeguard)

**Purpose.** The Tether Protocol wraps high‑risk expansion / hypothesis runs with a hard safety tether that:
- Enforces **pressure budgets** (SPB), **time/step fences**, and **output guards**.
- Integrates with **Reflex Grid** (ICA / GSR), **Suspension Archives** (CSA, Veiled Thread, Black Sphere).
- Publishes lightweight **telemetry** for TCAML / TCAMonitor.
- Provides deterministic **enter/exit** semantics and resumable checkpoints.

## Architecture

- **IPL (Interface Protection Layer):** entry/exit gates via `tether.session(...)` context. Prevents unmanaged runs.
- **SPB (Safety Pressure Buffer):** rolling avg/peak pressure tracking via `record_pressure`, budget enforcement.
- **SET (Safety/Ethics Tuner, planned):** future policy hooks tuning `TetherPolicy.reactions` per context/domain.

### States
`INIT → ARMED → ENGAGED → {THROTTLED|SUSPENDED|ESCALATED} → DISENGAGED | ABORTED`

### Fences
- `PRESSURE_BUDGET` (avg) → default action: **throttle**
- `PEAK_PRESSURE` (instant) → **suspend**
- `REFLEX_DENSITY` → **throttle**
- `SUSPENSION_LOAD` (CSA/VT/BS) → **escalate** (nudges GSR)
- `WALL_TIME` / `STEP_COUNT` → **abort**
- `OUTPUT_GUARD` (ORE preflight) → **suspend**

### Telemetry
JSONL at `data/runtime/collapse_logs/tether_telemetry.jsonl`.

## Usage

```python
from src.expansion.tether_protocol import TetherProtocol, TetherBudget, TetherPolicy
from src.aurea_core import AureaCore

core = AureaCore()
tether = TetherProtocol(
    reflex_grid=core.reflex_grid,
    csa=core.csa,
    vt=core.veiled_thread,
    bs=core.black_sphere,
    tca=core.tca,
    ore=core.ore,
    budget=TetherBudget(max_wall_time_s=60, avg_pressure_ceiling=0.6),
    policy=TetherPolicy()
)

with tether.session("nova:demo"):
    while tether.allow_step():
        # ... perform one hypothesis step ...
        step_pressure = 0.4
        tether.record_pressure(step_pressure)
        # Optionally guard a candidate output
        if not tether.guard_output("candidate text"):
            break  # suspended by policy
