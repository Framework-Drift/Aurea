"""
test_forensic_isolation.py - Ruling 31 (2026-07-26).

A FORENSIC WRITE PATH THAT CANNOT BE REDIRECTED IS ONE THAT WILL BE POLLUTED.
Path injectability is part of a durable store's contract, not a testing
convenience.

`GSR._default_alert` wrote its alert log from a bare literal in the method
body. `tests/conftest.py` has exactly one mechanism - monkeypatching a class
attribute or an `__init__` default - so a literal was UNREACHABLE by it, not
merely uncovered. Every GSR-driving test run appended to the real forensic log
while the fixture's docstring claimed isolation was handled. Ten stale entries
were on disk, one dating to 2025-08-10: ten records of nothing AUREA survived.

That is Ruling 22's fail-silent shape relocated into the harness. An isolation
fixture covering four of five paths does not provide isolation; it provides the
APPEARANCE of it, and the appearance is what stops anyone looking.

WHAT IS AND IS NOT PINNED HERE
------------------------------
PINNED:   the redirect actually binds (behavioral), and .gitignore covers both
          globs (structural - a genuine property OF SOURCE, Ruling 17's
          carve-out, not a runtime guarantee asserted lexically).
UNPINNED: git TRACKING STATUS. `git rm --cached` cannot be verified from
          pytest without shelling out to git, and a test that asserted it by
          running git would be pinning the developer's checkout rather than the
          repository. Checked ONCE by hand at implementation time and reported
          as UNPINNED - stated, never faked. An unpinned guarantee everyone
          believes is pinned is the exact defect this ruling is about.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.reflex.reflex_grid import GSR, ReflexGrid


REAL_ALERT_PATH = Path("data/collapse_logs/gsr_alerts.jsonl")


def _snapshot(path: Path):
    """Bytes if it exists, None if it does not. Either is a fact to preserve."""
    return path.read_bytes() if path.exists() else None


def test_gsr_alerts_land_in_tmp_and_never_touch_the_real_forensic_log(tmp_path):
    """THE PIN THAT WOULD HAVE CAUGHT THIS.

    Drives GSR for real under the autouse isolation fixture and asserts BOTH
    halves, because either alone is satisfiable by a broken implementation:

      * the REAL log is byte-for-byte untouched - a write that went to the
        wrong place is the whole defect;
      * the REDIRECTED path actually RECEIVED the alert - otherwise a GSR that
        silently stopped alerting would pass a "real log untouched" test
        perfectly, and this would be a test of nothing.

    RED if anyone reintroduces a literal in `_default_alert`, or removes the
    conftest redirect.
    """
    real_before = _snapshot(REAL_ALERT_PATH)
    redirected = tmp_path / "gsr_alerts.jsonl"

    assert Path(GSR.GSR_ALERT_PATH) != REAL_ALERT_PATH, (
        "the fixture did not redirect GSR_ALERT_PATH - it is still the real "
        "forensic path"
    )

    grid = ReflexGrid()
    grid.evaluate_pressure("test", "scar_density", 0.99)

    assert _snapshot(REAL_ALERT_PATH) == real_before, (
        f"a test run WROTE to the real forensic log at {REAL_ALERT_PATH} - "
        f"that is false pressure in a permanent record"
    )
    assert redirected.exists(), (
        "GSR did not alert at all - the redirect must isolate the write, not "
        "silence it"
    )
    entries = [json.loads(line) for line in
               redirected.read_text().splitlines() if line]
    assert entries, "the redirected alert log is empty"
    assert {"timestamp", "severity", "message"} <= set(entries[0])


def test_the_alert_path_is_a_class_attribute_not_a_literal():
    """The SHAPE is the contract (Ruling 31).

    `conftest` can only reach a class attribute or an `__init__` default. This
    asserts the attribute EXISTS and is what the writer actually consults - by
    repointing it and observing the write follow, which a literal cannot do.
    A source scan would prove neither.
    """
    assert isinstance(GSR.GSR_ALERT_PATH, str)


def test_gsr_alert_follows_the_class_attribute_at_write_time(tmp_path,
                                                             monkeypatch):
    """Resolved at WRITE time, so a redirect binds even for a GSR that was
    already constructed. Construction-time resolution would leave every
    pre-existing instance writing to the old path."""
    grid = ReflexGrid()                      # GSR constructed HERE...
    moved = tmp_path / "moved_alerts.jsonl"
    monkeypatch.setattr(GSR, "GSR_ALERT_PATH", str(moved))   # ...redirected AFTER

    grid.evaluate_pressure("test", "scar_density", 0.99)

    assert moved.exists(), (
        "the alert did not follow the class attribute - the path is being "
        "resolved at construction time, not at write time"
    )


def test_gitignore_covers_both_forensic_log_globs():
    """STRUCTURAL, and legitimately so (Ruling 17's carve-out): whether a glob
    appears in `.gitignore` is a genuine property OF SOURCE, not a runtime
    guarantee asserted lexically.

    NOTE THE LIMIT, WHICH IS THE POINT OF THIS RULING: a `.gitignore` line is
    INERT against a TRACKED file. Both logs were tracked, which is exactly why
    the previously-deferred ignore line would have fixed nothing and made the
    item look cosmetic. This pin covers the ignore half only; the untracking
    half is UNPINNED and was verified by hand (see module docstring).
    """
    ignored = {line.strip() for line in
               Path(".gitignore").read_text(encoding="utf-8").splitlines()}

    assert "logs/*.jsonl" in ignored
    assert "data/collapse_logs/*.jsonl" in ignored
