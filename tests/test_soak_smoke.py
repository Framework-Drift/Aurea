"""
test_soak_smoke.py - DOCKET P / P5: the instrument cannot rot.

The soak harness is an OBSERVATION INSTRUMENT, and the lesson this repository
keeps relearning is that an instrument nobody checks stops measuring quietly:
Ruling 31's isolation fixture covered four of five paths while its own docstring
claimed completeness, and Ruling 3's invariant passed vacuously against a 0-byte
file for months. So the harness is under test FROM BIRTH.

WHAT THIS ASSERTS, and deliberately not more: that the instrument RUNS, EXPORTS,
ISOLATES, and REFUSES when it should. It does not assert anything about AUREA's
behaviour over a long run - that is the harness's output, and pinning today's
numbers would convert an observation instrument into a regression gate, which is
exactly what Docket P says it must not become.

    A soak that must produce a particular number is no longer measuring.

THE TWO REFUSAL PINS ARE THE LOAD-BEARING ONES. `_refuse_if_shared_out` and
`_audit_coverage` are guards, and a guard that has never been observed to fire
is indistinguishable from a comment (CLAUDE.md section 3). Both are driven here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import soak


# =====================================================================
# THE INSTRUMENT RUNS
# =====================================================================

def test_the_harness_completes_and_exports_a_summary(tmp_path) -> None:
    """Small N, under `tmp_path`. Completion + export, and every P4 guarantee."""
    out = tmp_path / "summary.json"
    summary = soak.run_soak(cycles=5, claim_every=2, seed=1,
                            out=str(out), root=tmp_path / "run", quiet=True)

    assert out.exists(), "the summary is the exported artifact"
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk["headline"]["cycles_run"] == 5

    assert summary["all_guarantees_pass"] is True, (
        f"a healthy short run must satisfy every P4 guarantee; failures: "
        f"{[g for g in summary['guarantees'] if not g['pass']]}")
    assert {g["id"] for g in summary["guarantees"]} == {
        "P4.1", "P4.2", "P4.3", "P4.4", "P4.5"}


def test_the_cycle_records_land_as_jsonl_in_the_runs_own_root(tmp_path) -> None:
    """One JSONL record per cycle, inside the run's root - never beside it."""
    root = tmp_path / "run"
    soak.run_soak(cycles=4, claim_every=2, seed=1, root=root, quiet=True,
                  out=str(tmp_path / "s.json"))

    lines = [l for l in (root / "cycles.jsonl").read_text(encoding="utf-8")
             .splitlines() if l.strip()]
    assert len(lines) == 4
    kinds = [json.loads(l)["kind"] for l in lines]
    assert kinds == ["quiet", "claim", "quiet", "claim"], (
        "the claim/quiet interleave is DETERMINISTIC and follows --claim-every")


def test_a_quiet_cycle_advances_the_three_real_clocks(tmp_path) -> None:
    """P2: a quiet cycle drives the clocks the real loop drives, and INVENTS
    NONE. `process_input` advances TCAML, SAE and SML from one site; a quiet
    cycle advances the same three.

    It must NOT mint an echo - `process_input("")` would be a claim cycle with
    an empty claim, not the passage of time.
    """
    root = tmp_path / "run"
    soak.isolate(root)
    from src.aurea_core import AureaCore

    core = AureaCore()
    before = (core.tcaml.cycle, core.sae.epoch_count,
              len(core.tca.topology.nodes), core.stats["echoes_processed"])
    soak.quiet_cycle(core)
    after = (core.tcaml.cycle, core.sae.epoch_count,
             len(core.tca.topology.nodes), core.stats["echoes_processed"])

    assert after[0] == before[0] + 1, "TCAML advanced one cycle"
    assert after[2] == before[2], "a quiet cycle places NO node"
    assert after[3] == before[3], "a quiet cycle mints NO echo"


# =====================================================================
# THE REFUSALS - the load-bearing half
# =====================================================================

def test_it_refuses_to_export_into_shared_runtime(tmp_path) -> None:
    """THE PREAMBLE AS CODE. Exporting into the store under measurement is the
    contamination this harness exists to make impossible - and the refusal
    happens BEFORE any cycle runs, so it cannot be discovered after the fact."""
    target = soak.SHARED_RUNTIME / "should_never_land.json"
    with pytest.raises(soak.SoakIsolationError) as exc:
        soak.run_soak(cycles=1, out=str(target), root=tmp_path / "run",
                      quiet=True)
    assert "data/runtime" in str(exc.value).replace("\\", "/")
    assert not target.exists()


def test_it_refuses_when_a_store_escapes_the_table(tmp_path, monkeypatch) -> None:
    """THE COVERAGE SELF-AUDIT, FORCED.

    Ruling 31's finding turned on the instrument rather than the code: a fixture
    covering four of five paths provides the APPEARANCE of isolation, and the
    appearance is what stops anyone looking. So the harness re-derives the
    injectable set from `src/` and refuses if its own table has fallen behind.

    Driven by hiding ONE real store (the CAE ledger) from the table.
    """
    real = soak._injection_table

    def crippled():
        class_attrs, init_defaults = real()
        return class_attrs, [t for t in init_defaults if t[1] != "ledger_path"]

    monkeypatch.setattr(soak, "_injection_table", crippled)

    with pytest.raises(soak.SoakIsolationError) as exc:
        soak.isolate(tmp_path / "run")
    assert "CAE" in str(exc.value)
    assert "ledger_path" in str(exc.value)


def test_the_audit_passes_against_the_real_table() -> None:
    """The control for the pin above: with nothing hidden, the audit is SILENT.

    Without this, a `_derive_injectable_from_source` that returned everything
    (or an `_audit_coverage` that always raised) would satisfy the forcing pin
    and tell us nothing.
    """
    class_attrs, init_defaults = soak._injection_table()
    soak._audit_coverage(class_attrs, init_defaults)      # must not raise


def test_the_three_seed_paths_are_never_redirected(tmp_path) -> None:
    """SEED PATHS ARE EXEMPT AND MUST STAY THAT WAY (Rulings 32/39).

    They are read-only input with no writer. Redirecting one would hand the soak
    an EMPTY identity store and silently change what is being observed into
    something that is not AUREA - the opposite remedy, and one that would make
    every subsequent measurement meaningless while looking more isolated.
    """
    from src.doctrine.codex import Codex
    from src.filtration.scar_logic_core import ScarLogicCore
    from src.utils.echo_memory import EchoMemory

    before = (Codex.SEED_PATH, ScarLogicCore.SEED_PATH, EchoMemory.SEED_PATH)
    soak.isolate(tmp_path / "run")
    after = (Codex.SEED_PATH, ScarLogicCore.SEED_PATH, EchoMemory.SEED_PATH)

    assert before == after, "a seed path was redirected - it must never be"
    for path in after:
        assert "data/runtime" not in str(path).replace("\\", "/")

    class_attrs, init_defaults = soak._injection_table()
    named = {n for _, n, _ in class_attrs} | {n for _, n, _ in init_defaults}
    assert not any("SEED" in n for n in named), (
        "no seed path may appear in the injection table")
