"""
conftest.py - suite-wide I/O isolation for the RB forensic log (Ruling 11).

Ruling 11 makes GLOBAL-scope reflex entries flush to disk IMMEDIATELY - which
means any test that drives GSR (cascade decomposition, disorientation lock,
type-gate) would otherwise append real lines to logs/reflex_behavior.jsonl.
A forensic log polluted with test entries is worse than a dirty tree: it is
false pressure in a permanent record.

There is deliberately no injectable no-op sink in RBSystem (a forensic log you
can silently disable is not a forensic log), so isolation is by REDIRECTION:
RBSystem resolves DEFAULT_LOG_PATH at construction time, and this autouse
fixture points it into pytest's tmp dir for every test. Tests asserting on
disk contents pass an explicit log_path instead and are unaffected.

This fixture weakens no assertion in any test. Do not extend it into one that
does.
"""

import pytest

from src.reflex.rb_system import RBSystem


@pytest.fixture(autouse=True)
def _rb_log_to_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(
        RBSystem, "DEFAULT_LOG_PATH",
        str(tmp_path / "reflex_behavior.jsonl"),
    )
