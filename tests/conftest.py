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
  - CSA / VeiledThread / BlackSphere take a `filepath` default argument;
    AureaCore builds them with no args, so the default is what gets used -
    this fixture repoints that default's tail at tmp, preserving capacity.
Tests asserting on disk contents pass an explicit path instead and are
unaffected.

This fixture weakens no assertion in any test. Do not extend it into one that
does.
"""

import pytest

from src.aurea_core import AureaCore
from src.reflex.rb_system import RBSystem
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
