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
  - CSA / VeiledThread / BlackSphere take a `filepath` default argument;
    AureaCore builds them with no args, so the default is what gets used -
    this fixture repoints that default's tail at tmp, preserving capacity.
Tests asserting on disk contents pass an explicit path instead and are
unaffected.

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

import pytest

from src.aurea_core import AureaCore
from src.reflex.rb_system import RBSystem
from src.reflex.reflex_grid import GSR
from src.suspension.black_sphere import BlackSphere
from src.suspension.csa import CSA
from src.suspension.veiled_thread import VeiledThread


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
    # Repoint each suspension store's default filepath (the last __init__
    # default) at tmp, keeping the preceding capacity default intact.
    for cls, fname in ((CSA, "csa.json"),
                       (VeiledThread, "veiled_thread.json"),
                       (BlackSphere, "black_sphere.json")):
        defaults = cls.__init__.__defaults__ or ()
        monkeypatch.setattr(
            cls.__init__, "__defaults__",
            defaults[:-1] + (str(tmp_path / fname),),
        )
