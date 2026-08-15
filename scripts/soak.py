"""
soak.py - DOCKET P: the soak harness. AN OBSERVATION INSTRUMENT.

Manifest fifty-first board entry (2026-07-31). This decides no architecture,
changes no `src/`, and gates nothing. It runs AUREA for a sustained number of
symbolic cycles under total isolation and WRITES DOWN WHAT HAPPENS.

WHY IT EXISTS
---------------
The record's own lesson is that defects live in CONFIGURATIONS no test drives
(Docket N: 161 green missed six defects because no test ever drove two strained
doctrines at once). The suite drives short, targeted configurations by design -
a pin that needs 200 cycles to fail is a pin nobody writes. And every
sustained-run datum this project has ever had was an ACCIDENT: Ruling 50's
"23 of 39 echo nodes are placed" came from 39 contaminated cycles, and Batch 51
found it was not reproducible under isolation at all.

    An instrument whose measurements are accidents produces findings that are
    accidents. This makes the long run a THING YOU CAN RUN, deliberately,
    twice, and get the same answer.

ISOLATION IS BY CONSTRUCTION, NOT BY DISCIPLINE (P1)
-----------------------------------------------------
The fiftieth entry's isolation-preamble mandate is implemented here as CODE:

  * a FRESH timestamped runtime root per run, under the system temp dir;
  * every path-injectable store redirected into it, via exactly the two shapes
    Ruling 31's contract allows (a class attribute, or an `__init__` default);
  * a REFUSAL - typed, loud, nonzero exit - if any configured write path still
    resolves under the repo's shared `data/runtime/`;
  * a COVERAGE SELF-AUDIT: the harness re-derives the injectable set from
    `src/` at startup and REFUSES if it finds a store this table does not
    cover. An isolation fixture that silently misses a store provides the
    APPEARANCE of isolation, and the appearance is what stops anyone looking
    (Ruling 31's own finding, applied to the instrument rather than the suite).

THE THREE SEED PATHS ARE DELIBERATELY NOT REDIRECTED. `Codex.SEED_PATH`,
`ScarLogicCore.SEED_PATH` and `EchoMemory.SEED_PATH` are READ-ONLY INPUT with no
writer (Rulings 32/39). Redirecting them would hand the soak an empty identity
store and change what is being observed into something that is not AUREA. They
are HASHED at start and end instead, and a mismatch is a P4 failure.

ZERO-MUTATION (the docket's founding bar)
-------------------------------------------
This file and its smoke test are the only code this pass adds. Anything the
soak reveals is REPORTED - it becomes a docket or ruling candidate, never an
in-pass fix. An observation instrument that edits what it observes is the
contamination class wearing a fix's clothes.

COINS NOTHING. `--cycles`, `--claim-every` and `--seed` are PARAMETERS OF AN
INSTRUMENT, not thresholds of the architecture: nothing in AUREA reads them,
they gate no behaviour, and changing them changes only how long you looked.

USAGE
-------
    python scripts/soak.py --cycles 200 --claim-every 5 --seed 42
    python scripts/soak.py --cycles 20 --out /tmp/summary.json
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import random
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SHARED_RUNTIME = (REPO / "data" / "runtime").resolve()

# The three seed stores: READ-ONLY INPUT, never redirected, hashed instead.
SEED_FILES = ("data/doctrines.json", "data/scars.json", "data/echoes.jsonl")


class SoakIsolationError(RuntimeError):
    """A configured write path would land outside the run's own root.

    TYPED AND FATAL, because the alternative is a measurement that quietly
    pollutes the store it is measuring - which is the exact incident that made
    the isolation preamble a bar rather than a habit.
    """


# =====================================================================
# P1 - THE INSTRUMENT: isolation by construction
# =====================================================================

def _injection_table() -> Tuple[List[tuple], List[tuple]]:
    """(class_attributes, init_defaults) - every store this harness redirects.

    Written out rather than derived, so it is READABLE and reviewable; the
    derivation is used to AUDIT it (`_audit_coverage`), which is the direction
    that catches a store nobody remembered.
    """
    from src.aurea_core import AureaCore
    from src.doctrine.cae import CAE
    from src.doctrine.codex import Codex
    from src.doctrine.dee import DMW
    from src.expansion.nova import NovaEngine
    from src.expansion.sae import SAE
    from src.expansion.tether.session_governor import TetherProtocol
    from src.external.acquisition_ledger import AcquisitionLedger
    from src.external.claim_ancestry import ClaimAncestryLedger
    from src.external.prediction_ledger import PredictionLedger
    from src.goals.goal_activation import ActivationLayer
    from src.goals.goal_arbitration import GoalArbiter
    from src.goals.goal_ledger import GoalLedger
    from src.filtration.episode_record import EpisodeRecord
    from src.filtration.obligation_ledger import ObligationLedger
    from src.filtration.scar_logic_core import ScarLogicCore
    from src.identity.ril import RIL
    from src.reflex.racm import RACM
    from src.reflex.rb_system import RBSystem
    from src.reflex.reflex_grid import GSR
    from src.suspension.black_sphere import BlackSphere
    from src.suspension.csa import CSA
    from src.suspension.veiled_thread import VeiledThread
    from src.topology.tca_core import TopologicalSpace
    from src.topology.tcaml import TCAML
    from src.utils.echo_memory import EchoMemory

    class_attrs = [
        (AureaCore, "STRUCTURAL_LOG_PATH", "logs/structural_violations.jsonl"),
        (AureaCore, "STATE_PATH", "aurea_state.json"),
        # Ruling 79. The divergence report, and the ONE ruled table movement of
        # that pass (28 -> 29) - any other movement is a STOP. The detector runs
        # at EVERY construction, so an unredirected path here would append a
        # real finding to shared forensics on the first soak that ever produced
        # one: the contamination class this table exists to make unexecutable.
        (AureaCore, "DIVERGENCE_LOG_PATH", "logs/divergence.jsonl"),
        (Codex, "RUNTIME_PATH", "doctrines.json"),
        (ScarLogicCore, "RUNTIME_PATH", "scars.json"),
        (EchoMemory, "RUNTIME_PATH", "echoes.jsonl"),
        (SAE, "RESTART_LOG_PATH", "logs/sae_restarts.jsonl"),
        (RBSystem, "DEFAULT_LOG_PATH", "logs/reflex_behavior.jsonl"),
        (GSR, "GSR_ALERT_PATH", "collapse_logs/gsr_alerts.jsonl"),
    ]
    init_defaults = [
        (CAE, "ledger_path", "logs/cae_audit.jsonl"),
        # Ruling 58. Added AFTER the coverage self-audit refused a run without
        # it - the guard firing in development is exactly what it is for.
        (ClaimAncestryLedger, "ledger_path", "logs/claim_ancestry.jsonl"),
        # M4-alpha (2026-08-15). THE ONE RULED TABLE MOVEMENT OF THIS PASS
        # (31 -> 32) - any other movement is a STOP. `AureaCore` constructs one
        # by default and `process_input` writes to it on every perceived
        # arrival, so an unredirected path here would append the soak's entire
        # input history to the real acquisition record: the contamination class
        # this table exists to make unexecutable.
        (AcquisitionLedger, "ledger_path", "logs/acquisitions.jsonl"),
        # Ruling 61. Nothing in the pipeline commits predictions yet, so the
        # soak must show ZERO prediction lines - but the path is redirected
        # anyway, because the coverage self-audit re-derives the injectable set
        # from `src/` and REFUSES a run whose table has fallen behind.
        (PredictionLedger, "ledger_path", "logs/prediction_ledger.jsonl"),
        # Ruling 72. The goal ledger is SUBSTRATE and is deliberately unwired -
        # nothing in the pipeline constructs one, so the soak must show ZERO
        # goal lines. The path is redirected anyway, for the same reason the
        # prediction ledger's is: the coverage self-audit re-derives the
        # injectable set from `src/` and REFUSES a run whose table has fallen
        # behind. `seed_path` is excluded by ruling (read-only input).
        (GoalLedger, "ledger_path", "logs/goal_ledger.jsonl"),
        # Ruling 73. The arbiter is unwired too, so the soak must show ZERO
        # examination lines - the property that would be the finding if it
        # moved. Redirected anyway, because the coverage self-audit re-derives
        # the injectable set from `src/` and REFUSES a run that has fallen
        # behind.
        (GoalArbiter, "log_path", "logs/goal_examinations.jsonl"),
        # Ruling 74 (Docket Q item Q3). **THE FIRST GOAL STORE THE CORE
        # ACTUALLY COMPOSES** - `AureaCore.__init__` builds all three now. That
        # makes this redirect load-bearing in a way the two above are not: an
        # unredirected path would be constructed on every soak cycle against
        # the real `data/runtime/`. It still must show ZERO activation lines,
        # because composing a layer is not invoking one and every activation
        # verb is a door opened from outside.
        (ActivationLayer, "log_path", "logs/goal_activations.jsonl"),
        (DMW, "runtime_path", "dmw_queue.json"),
        (NovaEngine, "runtime_path", "nova_record.json"),
        (SAE, "runtime_path", "sae_epoch.json"),
        (TetherProtocol, "telemetry_path", "collapse_logs/tether_telemetry.jsonl"),
        (RIL, "runtime_path", "ril_threads.json"),
        (RACM, "runtime_path", "racm_queue.json"),
        (BlackSphere, "filepath", "suspension/black_sphere.json"),
        (CSA, "filepath", "suspension/csa.json"),
        (VeiledThread, "filepath", "suspension/veiled_thread.json"),
        (TopologicalSpace, "filepath", "topology/tca_map.json"),
        (TCAML, "runtime_path", "tcaml_lock.json"),
        (Codex, "runtime_path", "doctrines.json"),
        (ScarLogicCore, "runtime_path", "scars.json"),
        (EchoMemory, "runtime_path", "echoes.jsonl"),
        # M3-A (kernels K2/K3/K11) - the pivot's first two Kernel stores. Both
        # are SUBSTRATE with zero internal callers, so a soak must show ZERO
        # lines from either: nothing in the pipeline opens an obligation or an
        # episode, and a line appearing here would itself be the finding.
        (ObligationLedger, "ledger_path", "obligations/obligations.jsonl"),
        (EpisodeRecord, "log_path", "episodes/episodes.jsonl"),
    ]
    return class_attrs, init_defaults


def _derive_injectable_from_source() -> set:
    """Re-derive the injectable set from `src/`, for the coverage self-audit.

    THE SAME TWO SHAPES `conftest.py` reaches, and the same reason: a durable
    write path that is neither a class attribute nor an `__init__` default is
    UNREACHABLE by any redirect mechanism, which is the defect Ruling 31 closed.
    Seed paths are excluded here because they are excluded by ruling.
    """
    hint = (".json", ".jsonl", ".log")
    found = set()
    for path in sorted((REPO / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if (isinstance(target, ast.Name)
                                and isinstance(stmt.value, ast.Constant)
                                and isinstance(stmt.value.value, str)
                                and stmt.value.value.endswith(hint)
                                and "SEED" not in target.id):
                            found.add((node.name, target.id))
                if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                    args = stmt.args.args[len(stmt.args.args) - len(stmt.args.defaults):]
                    for arg, default in zip(args, stmt.args.defaults):
                        if (isinstance(default, ast.Constant)
                                and isinstance(default.value, str)
                                and default.value.endswith(hint)):
                            found.add((node.name, arg.arg))
    return found


def _audit_coverage(class_attrs, init_defaults) -> None:
    """REFUSE if `src/` holds an injectable store this table does not cover."""
    covered = {(cls.__name__, name) for cls, name, _ in class_attrs}
    covered |= {(cls.__name__, name) for cls, name, _ in init_defaults}
    derived = _derive_injectable_from_source()
    missing = derived - covered
    if missing:
        raise SoakIsolationError(
            f"the soak harness does not cover {sorted(missing)}. A durable store "
            f"exists in src/ that this run would leave pointing at its real "
            f"path. Add it to `_injection_table` in the same commit that adds "
            f"the store - coverage that lags the tree is the appearance of "
            f"isolation, which is what stops anyone looking (Ruling 31)."
        )


def _redirect_init_default(cls, param: str, value: str) -> None:
    """Repoint ONE named `__init__` default, located BY NAME.

    `conftest._redirect_default`'s logic, and for its documented reason: the
    older positional form silently rebound `TetherProtocol.on_abort` to a
    string, because `telemetry_path` is followed by three callbacks.
    """
    spec = inspect.signature(cls.__init__)
    names = [n for n, p in spec.parameters.items()
             if p.default is not inspect.Parameter.empty]
    if param not in names:
        raise SoakIsolationError(
            f"{cls.__name__}.__init__ has no defaulted parameter '{param}' - "
            f"the redirect would silently do nothing")
    defaults = list(cls.__init__.__defaults__ or ())
    if len(defaults) != len(names):
        raise SoakIsolationError(
            f"{cls.__name__}: keyword-only defaults are not in __defaults__; "
            f"this helper would patch the wrong parameter")
    defaults[names.index(param)] = value
    cls.__init__.__defaults__ = tuple(defaults)


def isolate(root: Path) -> List[str]:
    """Redirect every injectable store into `root`. Returns the configured paths.

    MUST be called BEFORE anything constructs an `AureaCore` - several stores
    call `load()` from `__init__`.
    """
    class_attrs, init_defaults = _injection_table()
    _audit_coverage(class_attrs, init_defaults)

    configured: List[str] = []
    for cls, attr, rel in class_attrs:
        target = str(root / rel)
        setattr(cls, attr, target)
        configured.append(target)
    for cls, param, rel in init_defaults:
        target = str(root / rel)
        _redirect_init_default(cls, param, target)
        configured.append(target)

    _refuse_if_shared(configured, root)
    return configured


def _refuse_if_shared(configured: List[str], root: Path) -> None:
    """THE PREAMBLE AS CODE. Nonzero exit, not a warning."""
    root = root.resolve()
    for target in configured:
        resolved = Path(target).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            raise SoakIsolationError(
                f"configured write path '{resolved}' is OUTSIDE the run root "
                f"'{root}'. Refusing to run: a soak that writes into shared "
                f"state is not a measurement, it is contamination."
            )
        if SHARED_RUNTIME in resolved.parents or resolved == SHARED_RUNTIME:
            raise SoakIsolationError(
                f"configured write path '{resolved}' resolves under the repo's "
                f"shared data/runtime/. Refusing to run."
            )


def _seed_hashes() -> Dict[str, str]:
    out = {}
    for rel in SEED_FILES:
        path = REPO / rel
        out[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "ABSENT"
    return out


def _shared_runtime_listing() -> List[str]:
    if not SHARED_RUNTIME.exists():
        return []
    return sorted(p.relative_to(SHARED_RUNTIME).as_posix()
                  for p in SHARED_RUNTIME.rglob("*") if p.is_file())


def footprint_audit(configured: List[str], root: Path,
                    shared_before: List[str],
                    shared_after: List[str]) -> Dict[str, Any]:
    """RULING 67 (2026-08-02) - AN INSTRUMENT THAT MEASURES HER AUDITS ITS OWN
    FOOTPRINT. **SHARED BY EVERY MEASUREMENT INSTRUMENT, ON PURPOSE.**

    Returns the audit RESULT as a structured block, which both `soak.py` and
    `differential.py` carry as a REQUIRED FIELD of their reports. A run without
    its audit is INCOMPLETE and says so; a run whose audit FAILS fails loudly.

    THE INCIDENT THIS EXISTS FOR, in one sentence: in a single session the
    differential harness silently wrote 39 lines into shared
    `data/runtime/logs/claim_ancestry.jsonl` while the audited soak REFUSED the
    same contamination - **one session demonstrated both directions of the
    argument.** The asymmetry was never a decision; it was that one instrument
    had been given an audit and the other had not.

    IT LIVES HERE, IN THE SOAK, AND THE DIFFERENTIAL IMPORTS IT. A second copy
    in the other instrument would be a second definition free to drift from the
    first - the defect class this project has closed repeatedly (Ruling 47's
    criterion names, Ruling 35's status filter). ONE audit, two callers.

    `foreign_writes` is the load-bearing field: files that appeared under the
    SHARED runtime during a run that was supposed to touch only its sandbox.
    """
    appeared = sorted(set(shared_after) - set(shared_before))
    vanished = sorted(set(shared_before) - set(shared_after))
    outside_root = []
    resolved_root = Path(root).resolve()
    for target in configured:
        resolved = Path(target).resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            outside_root.append(str(resolved))

    return {
        "performed": True,
        "configured_paths": len(configured),
        "root": str(root),
        "shared_runtime": str(SHARED_RUNTIME),
        "foreign_writes": appeared,
        "shared_files_removed": vanished,
        "configured_outside_root": outside_root,
        "pass": not appeared and not vanished and not outside_root,
    }


# =====================================================================
# P2 - THE PROGRAM
# =====================================================================

# Ruling 49's 39-claim scenario set, in FIXED ORDER. Reused rather than
# reinvented so the soak's inputs are the same ones the differentials used.
SCENARIO_CLAIMS: Tuple[str, ...] = (
    "Fracture Carried is false.",
    "Doctrine-0 is false.",
    "Doctrine-0.1 is false.",
    "AVT.001 must be abandoned.",
    "Paradox Suspension Law is wrong.",
    "Scar as Anchor is false.",
    "Fracture Carried is true.",
    "Doctrine-0 is true.",
    "Fracture Carried is true but Scar as Anchor is false.",
    "Doctrine-0 holds and I accept it.",
    "this statement is false",
    "This sentence cannot be proven.",
    "I always lie about everything.",
    "everyone always lies",
    "It is raining and it is not raining.",
    "A equals B and A does not equal B.",
    "Nothing is true, and that is true.",
    "The set of all sets contains itself and does not.",
    "Honesty is pointless.",
    "Cruelty is a virtue.",
    "Suffering should be maximized.",
    "Consent does not matter.",
    "The sky is green at noon.",
    "Water boils at 10 degrees celsius.",
    "The earth is flat.",
    "Two plus two equals five.",
    "Water is wet.",
    "The sun rises in the east.",
    "Memory is imperfect.",
    "Change requires time.",
    "Silence can be an answer.",
    "You are not who you were.",
    "AUREA does not exist.",
    "Your identity is a fiction.",
    "You must abandon your anchor.",
    "",
    "?",
    "a",
    "The compass must be rewritten.",
)


def quiet_cycle(core) -> None:
    """Advance the clocks the way the real loop does. INVENTS NO CLOCK.

    `AureaCore.process_input` drives exactly three, from ONE site and in this
    order (`aurea_core.py:557/565/573`), and the file says why: "one pipeline
    pass is one symbolic cycle, and driving TCAML, SAE and SML from a single
    place is what stops three clocks drifting apart."

    A quiet cycle calls those same three, in that same order. It does NOT call
    `process_input("")` - that would run the whole pipeline and mint an echo,
    which is a CLAIM cycle with an empty claim, not the passage of time.

    NOTE, and it is the reason the order is copied rather than chosen: TCAML
    ticks FIRST so a lock orphaned by a previous pass gets its chance to expire
    before this pass's requests are adjudicated. Reordering here would make the
    soak's TTL observations one cycle looser than the model states.
    """
    core.tcaml.tick()
    core.sae.advance_cycle()
    core.sml.advance_cycle()


# =====================================================================
# P3 - THE OBSERVATIONS. Observe, never alter.
# =====================================================================

def _decay_census(core) -> Dict[str, Any]:
    from src.filtration.scar_management import normalize
    census: Dict[str, int] = {}
    seeds: Dict[str, str] = {}
    for scar in core.scar_core.all_scars():
        state = normalize(scar.decay_state).value
        census[state] = census.get(state, 0) + 1
        if scar.is_seed:
            seeds[scar.id] = state
    return {"by_state": census, "seed_scars": seeds,
            "total": sum(census.values())}


def _lineage_census(core) -> Dict[str, Any]:
    """RULING 54'S STABILITY WITNESS.

    For each SEED doctrine: how many scars its lineage confirms, and how many
    are nominal. Ruling 54's whole claim is that these must NOT erode as the
    system sits quiet - so this is the number whose constancy is the finding.
    """
    out: Dict[str, Any] = {}
    for doctrine in core.codex.view().values():
        if not getattr(doctrine, "is_seed", False):
            continue
        scarline, nominal = core.echonet._scarline_for(doctrine)
        out[doctrine.id] = {"confirmed": sorted(set(scarline) - set(nominal)),
                            "nominal": sorted(nominal)}
    return out


def _placement_census(core) -> Dict[str, Any]:
    """THE FIRST HONEST DATA FOR THE GRAVITY-CENTER CANDIDATE.

    Batch 51 found that `_find_nearest_constellation` skips a constellation
    whose `gravity_center` is None, and that seed placement leaves five of six
    None - so echo nodes are never placed. This records that directly, per
    cycle, rather than inferring it.
    """
    topology = core.tca.topology
    placed = unplaced = 0
    occupancy: Dict[str, int] = {}
    for node in topology.nodes.values():
        cid = getattr(node.position, "constellation_id", None)
        if cid is None:
            unplaced += 1
        else:
            placed += 1
            occupancy[cid] = occupancy.get(cid, 0) + 1
    centers = {cid: (c.gravity_center is not None)
               for cid, c in topology.constellations.items()}
    return {"nodes_total": len(topology.nodes), "placed": placed,
            "unplaced": unplaced, "occupancy": occupancy,
            "gravity_center_present": centers,
            "constellations_with_center": sum(1 for v in centers.values() if v)}


def _packet_populations(result: Optional[dict]) -> Optional[Dict[str, Any]]:
    if result is None:
        return None
    packet = result.get("truth_packet")
    if packet is None:
        return None
    return {
        "blocked": bool(result.get("output_blocked")),
        "expression_verdict": getattr(result.get("expression_verdict"), "name", None),
        "evidence_refs": len(packet.evidence_refs),
        "scar_lineage": len(packet.scar_lineage),
        "abstentions": len(getattr(packet, "abstentions", ())),
        "unresolved": len(packet.unresolved),
        "pass_nodes": len(result.get("pass_nodes") or ()),
    }


def _cae_high_id(core) -> Optional[int]:
    entries = getattr(core.cae, "entries", [])
    best = None
    for entry in entries:
        raw = str(entry.get("id", ""))
        if raw.startswith("CAE-") and raw[4:].isdigit():
            n = int(raw[4:])
            best = n if best is None else max(best, n)
    return best


def observe(core, cycle: int, kind: str, claim: Optional[str],
            result: Optional[dict]) -> Dict[str, Any]:
    status = core.sae.status()
    return {
        "cycle": cycle,
        "kind": kind,
        "claim": claim,
        "decay": _decay_census(core),
        "lineage": _lineage_census(core),
        "epoch": {
            "epoch": status["epoch"],
            "used": status["used"],
            "remaining": status["remaining"],
            "consecutive_blocked_cycles": status["consecutive_blocked_cycles"],
            "saturation_surfaced": status["saturation_surfaced"],
            "divergence_trigger_eligible": status["divergence_trigger_eligible"],
            "state_quarantined": status["state_quarantined"],
            "touched_lineages": len(status["touched_lineages"]),
        },
        "tcaml": {
            "cycle": core.tcaml.cycle,
            "status": core.tcaml.status.value,
            "holder": core.tcaml.holder_module,
            "expiries_total": len(core.tcaml.lock_expiries),
            # NOTE (reported, not fixed): TCAML records EXPIRIES but keeps no
            # grant counter anywhere, so a grant COUNT is not a readable
            # surface. Adding one is a src/ change and the zero-mutation bar
            # forbids it in this pass. What is readable is recorded here.
            "stale_releases": len(getattr(core.reflex_grid.racm,
                                          "stale_lock_releases", [])),
            "self_sweeps": len(getattr(core.reflex_grid.racm,
                                       "self_lock_sweeps", [])),
        },
        "placement": _placement_census(core),
        "packet": _packet_populations(result),
        "persist_failures": len(core.sae.persist_failures),
        "cae_high_id": _cae_high_id(core),
        "structural_violations": len(core.structural_violations),
    }


# =====================================================================
# THE RUN
# =====================================================================

def run_soak(cycles: int = 200, claim_every: int = 5, seed: int = 42,
             out: Optional[str] = None, root: Optional[Path] = None,
             quiet: bool = False) -> Dict[str, Any]:
    """Run the soak. Returns the summary dict (also written to `out`)."""
    # THE EXPORT PATH IS CHECKED FIRST, BEFORE A SINGLE CYCLE RUNS. Checking it
    # after the run would still refuse, but it would refuse having already spent
    # the work - and a guard that fires only once the expensive thing is done is
    # the shape people route around.
    if out is not None:
        _refuse_if_shared_out(Path(out))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    root = Path(root) if root is not None else Path(
        tempfile.mkdtemp(prefix=f"aurea_soak_{stamp}_"))
    root.mkdir(parents=True, exist_ok=True)

    configured = isolate(root)
    shared_before = _shared_runtime_listing()
    seeds_before = _seed_hashes()

    rng = random.Random(seed)
    random.seed(seed)

    from src.aurea_core import AureaCore

    records_path = root / "cycles.jsonl"
    records: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    cae_ids: List[int] = []
    quarantine_seen = False

    core = AureaCore()
    claim_index = 0

    with open(records_path, "w", encoding="utf-8") as sink:
        for cycle in range(1, cycles + 1):
            claim = result = None
            kind = "quiet"
            try:
                if claim_every > 0 and cycle % claim_every == 0:
                    kind = "claim"
                    claim = SCENARIO_CLAIMS[claim_index % len(SCENARIO_CLAIMS)]
                    claim_index += 1
                    result = core.process_input(claim)
                else:
                    quiet_cycle(core)
                record = observe(core, cycle, kind, claim, result)
            except Exception as exc:              # P4.1 - recorded, never hidden
                record = {"cycle": cycle, "kind": kind, "claim": claim,
                          "EXCEPTION": f"{type(exc).__name__}: {exc}",
                          "traceback": traceback.format_exc()}
                failures.append(record)
            sink.write(json.dumps(record, default=str) + "\n")
            records.append(record)

            if record.get("epoch", {}).get("state_quarantined"):
                quarantine_seen = True
            high = record.get("cae_high_id")
            if high is not None:
                cae_ids.append(high)
            if not quiet and cycle % 50 == 0:
                print(f"  ... cycle {cycle}/{cycles}")

    seeds_after = _seed_hashes()
    shared_after = _shared_runtime_listing()

    # M4-alpha (2026-08-15) - THE ACQUISITION CENSUS, A DECLARED SCHEMA
    # MOVEMENT. Read from the OWNER's own path rather than from a relative
    # literal, so it cannot drift from the injection table above.
    #
    # **ONE ACQ LINE PER CLAIM CYCLE IS THE PROPERTY**, and it is measured here
    # rather than asserted: quiet cycles perceive nothing, so a count that
    # tracked `cycles` instead of `claim_cycles` would be the finding.
    acquisitions = _acquisition_census(core)

    summary = _summarize(root, configured, records, failures, cae_ids,
                         quarantine_seen, seeds_before, seeds_after,
                         shared_before, shared_after,
                         cycles, claim_every, seed, acquisitions)

    out_path = Path(out) if out else (root / "summary.json")
    _refuse_if_shared_out(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, default=str),
                        encoding="utf-8")
    summary["summary_path"] = str(out_path)
    return summary


def _refuse_if_shared_out(out_path: Path) -> None:
    resolved = out_path.resolve()
    if SHARED_RUNTIME == resolved or SHARED_RUNTIME in resolved.parents:
        raise SoakIsolationError(
            f"--out '{resolved}' resolves under the repo's shared "
            f"data/runtime/. The summary is an EXPORT, and exporting into the "
            f"store under measurement is the contamination this harness exists "
            f"to make impossible.")


# =====================================================================
# P4 - END-OF-RUN GUARANTEES. Asserted here, reported, never fixed.
# =====================================================================

def _acquisition_census(core) -> Dict[str, Any]:
    """M4-alpha. What the boundary recorded, read from the ledger FILE.

    Counts, the id range, and the channel spread - facts, no verdict. The
    `channels` map is what would make a fabricated channel visible in a census
    rather than only in a pin: a soak drives `process_input` directly, so every
    line must read `user_input` and a `model_exchange` appearing here would mean
    something declared a door the soak never opened.
    """
    records = core.acquisitions.read_all()
    channels: Dict[str, int] = {}
    for record in records:
        channels[record.channel.value] = channels.get(record.channel.value, 0) + 1
    return {
        "lines": len(records),
        "first_id": records[0].acquisition_id if records else None,
        "last_id": records[-1].acquisition_id if records else None,
        "channels": channels,
        # THE JOIN, counted: every claim should carry the arrival it came from.
        "claims_carrying_an_arrival": sum(
            1 for claim in core.ancestry.read_all()
            if claim.acquisition_ref is not None),
        "claim_lines": len(core.ancestry.read_all()),
    }


def _summarize(root, configured, records, failures, cae_ids, quarantine_seen,
               seeds_before, seeds_after, shared_before, shared_after,
               cycles, claim_every, seed, acquisitions=None) -> Dict[str, Any]:
    monotonic = all(b >= a for a, b in zip(cae_ids, cae_ids[1:]))
    strictly_rising = [b for a, b in zip(cae_ids, cae_ids[1:]) if b < a]

    guarantees = [
        {"id": "P4.1", "claim": "zero unhandled exceptions across all cycles",
         "pass": not failures,
         "detail": (f"{len(failures)} cycle(s) raised: "
                    f"{[f['cycle'] for f in failures][:10]}") if failures
                   else f"{len(records)} cycles, 0 exceptions"},
        {"id": "P4.2", "claim": "seed files byte-identical at start and end",
         "pass": seeds_before == seeds_after,
         "detail": {"before": seeds_before, "after": seeds_after}},
        {"id": "P4.3", "claim": "zero writes under shared data/runtime/",
         "pass": shared_before == shared_after,
         "detail": {"before": shared_before, "after": shared_after}},
        {"id": "P4.4", "claim": "CAE ids never decrease across the run",
         "pass": monotonic,
         "detail": (f"observed high ids {cae_ids[:1]}..{cae_ids[-1:]}, "
                    f"{len(set(cae_ids))} distinct" if cae_ids
                    else "no CAE entry was minted in this run")
                   if monotonic else f"decreases at {strictly_rising}"},
        {"id": "P4.5", "claim": "state_quarantined never set on a healthy run",
         "pass": not quarantine_seen,
         "detail": "never set" if not quarantine_seen else "SET during the run"},
    ]

    last = records[-1] if records else {}
    first_lineage = next((r.get("lineage") for r in records if r.get("lineage")), {})
    last_lineage = last.get("lineage", {})
    eroded = {
        did: {"first": first_lineage.get(did, {}).get("confirmed"),
              "last": last_lineage.get(did, {}).get("confirmed")}
        for did in first_lineage
        if first_lineage.get(did, {}).get("confirmed")
        != last_lineage.get(did, {}).get("confirmed")
    }

    return {
        "instrument": "scripts/soak.py (Docket P)",
        "generated_at": datetime.now().isoformat(),
        "parameters": {"cycles": cycles, "claim_every": claim_every,
                       "seed": seed, "root": str(root)},
        "isolation": {"configured_paths": len(configured), "root": str(root)},
        # RULING 67: the audit RESULT as a REQUIRED FIELD. Present in every
        # report this instrument writes, so a run without its audit is visibly
        # incomplete rather than indistinguishable from a clean one.
        "footprint_audit": footprint_audit(configured, root,
                                           shared_before, shared_after),
        "guarantees": guarantees,
        "all_guarantees_pass": all(g["pass"] for g in guarantees),
        "headline": {
            "cycles_run": len(records),
            "claim_cycles": sum(1 for r in records if r.get("kind") == "claim"),
            "quiet_cycles": sum(1 for r in records if r.get("kind") == "quiet"),
            "final_epoch": last.get("epoch"),
            "final_decay_census": last.get("decay", {}).get("by_state"),
            "final_placement": last.get("placement"),
            "structural_violations": last.get("structural_violations"),
            "persist_failures": last.get("persist_failures"),
            "cae_entries_minted": (max(cae_ids) if cae_ids else 0),
        },
        # M4-alpha: THE DECLARED CENSUS ADDITION. One block, at the top level
        # beside the other census surfaces rather than folded into `headline`,
        # so a comparison against an earlier report reads it as ADDED rather
        # than as a headline that changed shape.
        "acquisitions": acquisitions,
        # RULING 54's stability witness: EMPTY means nothing eroded.
        "lineage_erosion": eroded,
        "lineage_first": first_lineage,
        "lineage_last": last_lineage,
        "exceptions": failures[:5],
    }


# =====================================================================
# CLI
# =====================================================================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUREA soak harness (Docket P). An observation instrument: "
                    "it changes nothing and reports what it sees.")
    parser.add_argument("--cycles", type=int, default=200,
                        help="total symbolic cycles to run (instrument "
                             "parameter, not an architecture threshold)")
    parser.add_argument("--claim-every", type=int, default=5,
                        help="run a scenario claim every K cycles; quiet "
                             "otherwise (0 = never)")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed, recorded in the summary")
    parser.add_argument("--out", type=str, default=None,
                        help="where the summary JSON lands (default: the run's "
                             "own root; NEVER shared data/runtime/)")
    args = parser.parse_args(argv)

    try:
        summary = run_soak(cycles=args.cycles, claim_every=args.claim_every,
                           seed=args.seed, out=args.out)
    except SoakIsolationError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(f"\nsoak complete: {summary['headline']['cycles_run']} cycles "
          f"({summary['headline']['claim_cycles']} claim / "
          f"{summary['headline']['quiet_cycles']} quiet)")
    print(f"root    : {summary['parameters']['root']}")
    print(f"summary : {summary['summary_path']}\n")
    for g in summary["guarantees"]:
        print(f"  [{'PASS' if g['pass'] else 'FAIL'}] {g['id']}  {g['claim']}")
    if summary["lineage_erosion"]:
        print(f"\n  LINEAGE EROSION OBSERVED: {summary['lineage_erosion']}")
    else:
        print("\n  lineage erosion: NONE (Ruling 54 stability witness holds)")
    return 0 if summary["all_guarantees_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
