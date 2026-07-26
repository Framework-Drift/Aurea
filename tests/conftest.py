"""
conftest.py - suite-wide I/O isolation for persistent stores.

Ruling 11 makes GLOBAL-scope reflex entries flush to disk IMMEDIATELY - which
means any test that drives GSR (cascade decomposition, disorientation lock,
type-gate) would otherwise append real lines to logs/reflex_behavior.jsonl.
A forensic log polluted with test entries is worse than a dirty tree: it is
false pressure in a permanent record.

The same hazard applies to the suspension stores. Once Nova Stage 2b wired the
proposals path, an end-to-end test drives real CSA routing (failed-collapse
decay) and real DEE fermentation (Veiled Thread suspend) - both of which
persist to data/suspension/*.json at construction-default paths. Suspended
state written by a test is the same class of false pressure in a real store.

There is deliberately no injectable no-op sink (a store you can silently
disable is not a store), so isolation is by REDIRECTION into pytest's tmp dir
for every test:
  - RBSystem resolves DEFAULT_LOG_PATH at construction time (class attr).
  - AureaCore resolves STRUCTURAL_LOG_PATH the same way (class attr).
  - GSR resolves GSR_ALERT_PATH at WRITE time (class attr) - see below.
  - CSA / VeiledThread / BlackSphere / TopologicalSpace / TetherProtocol take
    a path default argument; AureaCore builds them with no args, so the
    default is what gets used - this fixture repoints that one named default
    at tmp, leaving every other default intact.
  - Codex / ScarLogicCore / EchoMemory have a SEED path and a RUNTIME path
    (Ruling 32). Only the RUNTIME path is redirected.
Tests asserting on disk contents pass an explicit path instead and are
unaffected.

AS OF RULING 32 THIS FIXTURE COVERS EVERY DURABLE STORE IN THE SYSTEM - the
first time that has been true. Eleven paths: three resolved from class
attributes, eight from `__init__` defaults. If you add a twelfth and do not
add it here, you have reopened the hole Ruling 31 closed.

WHY THE FIFTH PATH ESCAPED FOR SO LONG (Ruling 31, 2026-07-26)
---------------------------------------------------------------
READ THIS BEFORE ADDING A DURABLE STORE. This fixture has exactly ONE
mechanism: monkeypatching a CLASS ATTRIBUTE or an `__init__` DEFAULT. That is
not a stylistic preference - it is the fixture's entire reach.

`GSR._default_alert` wrote `data/collapse_logs/gsr_alerts.jsonl` from a BARE
LITERAL in the method body. A literal is neither of those two shapes, so this
fixture could not reach it BY CONSTRUCTION - the path was not uncovered, it
was UNREACHABLE. Every GSR-driving test run appended to the real forensic log
(10 stale entries were found on disk, one dating to 2025-08-10), while the
fixture's own docstring said isolation was handled.

That is Ruling 22's fail-silent shape relocated into the harness: an isolation
fixture covering four of five paths does not provide isolation, it provides
the APPEARANCE of it, and the appearance is what stops anyone looking. The
defect was invisible from inside the fixture, because a fixture cannot enumerate
the paths it cannot see.

SO: A NEW DURABLE WRITE PATH MUST BE A CLASS ATTRIBUTE OR AN `__init__`
DEFAULT, AND MUST BE REDIRECTED HERE IN THE SAME COMMIT. Path injectability is
part of a durable store's contract, not a testing convenience.

This fixture weakens no assertion in any test. Do not extend it into one that
does.
"""

import inspect

import pytest

from src.aurea_core import AureaCore
from src.doctrine.codex import Codex
from src.expansion.tether.session_governor import TetherProtocol
from src.filtration.scar_logic_core import ScarLogicCore
from src.reflex.rb_system import RBSystem
from src.reflex.reflex_grid import GSR
from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread
from src.topology.tca_core import TopologicalSpace
from src.utils.echo_memory import EchoMemory


@pytest.fixture(autouse=True)
def _persist_to_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(
        RBSystem, "DEFAULT_LOG_PATH",
        str(tmp_path / "reflex_behavior.jsonl"),
    )
    # Ruling 25 (Docket N): structural violations get a durable record too, and
    # a test driving a guard on purpose must not append to the real forensic
    # log. Same shape as RBSystem's - resolved at construction from a class
    # attribute, so redirecting the attribute is the whole isolation.
    monkeypatch.setattr(
        AureaCore, "STRUCTURAL_LOG_PATH",
        str(tmp_path / "structural_violations.jsonl"),
    )
    # Ruling 31 (Docket 6d): the fifth path, and the one this fixture could not
    # reach until it stopped being a literal. GSR resolves it at WRITE time, so
    # this redirect binds even for a GSR the Grid already constructed.
    monkeypatch.setattr(
        GSR, "GSR_ALERT_PATH",
        str(tmp_path / "gsr_alerts.jsonl"),
    )
    # Repoint each remaining store's path default at tmp. Ruling 32 completes
    # this list: with the five below joining the three suspension stores and
    # the three class-attribute paths above, THE FIXTURE NOW COVERS EVERY
    # DURABLE STORE IN THE SYSTEM - the first time that has been true.
    #
    # For Codex / ScarLogicCore / EchoMemory it is the RUNTIME path that moves.
    # The SEED path deliberately does NOT: a test still reads AUREA's real
    # founding doctrine and scars, exactly as the pipeline does, and writes
    # land in tmp. Redirecting the seed too would silently give every test an
    # empty identity store and change what the whole suite is testing.
    for cls, param, fname in (
        (CSA, "filepath", "csa.json"),
        (VeiledThread, "filepath", "veiled_thread.json"),
        (BlackSphere, "filepath", "black_sphere.json"),
        (Codex, "runtime_path", "doctrines.json"),
        (ScarLogicCore, "runtime_path", "scars.json"),
        (EchoMemory, "runtime_path", "echoes.jsonl"),
        (TopologicalSpace, "filepath", "tca_map.json"),
        (TetherProtocol, "telemetry_path", "tether_telemetry.jsonl"),
    ):
        _redirect_default(monkeypatch, cls, param, str(tmp_path / fname))


def _redirect_default(monkeypatch, cls, param: str, value: str) -> None:
    """Repoint ONE named `__init__` default, located BY NAME.

    The older form of this loop assumed the path was the LAST defaulted
    parameter (`defaults[:-1] + (value,)`). That happens to be true for the
    suspension stores and is FALSE for `TetherProtocol`, whose
    `telemetry_path` is followed by three callback parameters - patching the
    last default there would have silently rebound `on_abort` to a string and
    left the telemetry path pointing at the real forensic directory. Found
    while extending the loop, not by a failing test.

    A positional assumption that is true for the cases you happen to have is
    the same class of defect Ruling 31 closed: a mechanism that appears to
    cover a store while structurally missing it. Resolve by name instead.
    """
    spec = inspect.signature(cls.__init__)
    names = [n for n, p in spec.parameters.items()
             if p.default is not inspect.Parameter.empty]
    assert param in names, (
        f"{cls.__name__}.__init__ has no defaulted parameter '{param}' - the "
        f"redirect would silently do nothing"
    )
    defaults = list(cls.__init__.__defaults__ or ())
    assert len(defaults) == len(names), (
        f"{cls.__name__}: keyword-only defaults are not in __defaults__; "
        f"this helper would patch the wrong parameter"
    )
    defaults[names.index(param)] = value
    monkeypatch.setattr(cls.__init__, "__defaults__", tuple(defaults))
