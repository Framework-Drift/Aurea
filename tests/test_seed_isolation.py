"""
test_seed_isolation.py - Ruling 32 (2026-07-26). THE SEED IS READ-ONLY INPUT.

`data/doctrines.json` (Doctrine-0.1 "Fracture Carried"), `data/scars.json`
(D17 "Compassion Weaponization", weight 84) and `data/echoes.jsonl` are
TRACKED. Until this ruling each store had ONE `filepath` doing two
incompatible jobs: the seed it reads at construction AND the target of
`save_to_file`, which writes with mode "w".

A default-constructed store that saved therefore REPLACED AUREA's founding
doctrine and scars with whatever happened to be in memory. That is not Ruling
31's hazard - R31 closed APPEND-mode logs where pollution ADDS junk. This is a
WHOLE-FILE OVERWRITE of an identity store: not false pressure, IDENTITY
REPLACEMENT.

Nothing prevented it except that no test happened to call save with default
args. That is CONVENTION. The bar is UNEXECUTABILITY, and the remedy chosen
was not copy-on-first-run (which leaves the seed live in the write path and
guards it with a conditional) but a split that leaves the seed WITH NO WRITER.

MINIMAL SEMANTICS, pinned as such: load -> runtime if present else seed;
save -> always a full snapshot to runtime. No layering, no delta format, no
merge rule.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.doctrine.codex import Codex
from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.echo_memory import EchoMemory
from src.utils.models import Echo


SEEDS = [
    (Codex, "data/doctrines.json"),
    (ScarLogicCore, "data/scars.json"),
    (EchoMemory, "data/echoes.jsonl"),
]


def _mutate_and_save(store):
    """Drive each store's real write path with default construction."""
    if isinstance(store, Codex):
        store.doctrines.clear()          # the destructive case, on purpose
        store.save_to_file()
    elif isinstance(store, ScarLogicCore):
        store.scars.clear()
        store.save_to_file()
    else:
        # RULING 75 MIGRATION (2026-08-05), Ruling-14 form. NO ASSERTION MOVED.
        #     OLD: `store.add_echo(Echo(id="E-test", content="runtime only",
        #                               resonance_score=0.0,
        #                               created_at=datetime(2026, 7, 26)))`
        #     NEW: `store.record("runtime only")`
        # `add_echo` is deleted as shape - the writer owns the mint - so the
        # store's real write path is now reached through `record`. What this
        # helper exists to do is unchanged: DRIVE THE REAL WRITE PATH under
        # default construction, which is what makes the seed pin meaningful.
        store.record("runtime only")


# =====================================================================
# PIN 1 - THE SEED IS NEVER A WRITE TARGET
# =====================================================================

@pytest.mark.parametrize("cls,seed_rel", SEEDS, ids=lambda v: getattr(v, "__name__", v))
def test_default_construction_writes_runtime_and_never_the_seed(cls, seed_rel,
                                                                tmp_path):
    """THE PIN THAT MAKES THE OVERWRITE UNEXECUTABLE.

    Default-construct, mutate DESTRUCTIVELY, save. Then assert BOTH halves,
    because either alone is satisfiable by a broken implementation:

      * the SEED file is BYTE-IDENTICAL - a save that reached it would have
        replaced AUREA's founding doctrine or scars wholesale;
      * the RUNTIME file actually RECEIVED the write - otherwise a store that
        silently stopped persisting would sail through a "seed untouched" test
        and this would be a test of nothing.

    RED if anyone points save back at the seed.
    """
    seed = Path(seed_rel)
    seed_before = seed.read_bytes()

    store = cls()                      # DEFAULT construction - the hazard case
    runtime = store.runtime_path

    assert runtime != seed, "runtime and seed must not be the same file"
    assert str(runtime).startswith(str(tmp_path)), (
        "conftest did not redirect this store's runtime path"
    )

    _mutate_and_save(store)

    assert seed.read_bytes() == seed_before, (
        f"THE SEED WAS OVERWRITTEN at {seed} - this is identity replacement, "
        f"not pollution"
    )
    assert runtime.exists(), "the runtime path received no write"
    assert runtime.read_bytes(), "the runtime file is empty"


def test_the_seed_still_holds_the_founding_records():
    """The seeds are not placeholders. Named here so that a test which
    accidentally empties one fails LOUDLY and specifically, rather than as a
    confusing downstream absence."""
    doctrines = json.loads(Path("data/doctrines.json").read_text(encoding="utf-8"))
    active = doctrines["active"] if isinstance(doctrines, dict) else doctrines
    assert any(d["id"] == "Doctrine-0.1" for d in active), (
        "Doctrine-0.1 'Fracture Carried' is missing from the seed"
    )

    scars = json.loads(Path("data/scars.json").read_text(encoding="utf-8"))
    assert any(s["id"] == "\u039417" for s in scars), (
        "Scar D17 'Compassion Weaponization' is missing from the seed"
    )


# =====================================================================
# PIN 2 - LOAD PRECEDENCE, BOTH DIRECTIONS
# =====================================================================

def test_load_falls_back_to_seed_when_no_runtime_exists(tmp_path):
    """No runtime file -> the seed is what she wakes up with."""
    runtime = tmp_path / "absent" / "doctrines.json"
    assert not runtime.exists()

    codex = Codex(runtime_path=str(runtime))

    assert "Doctrine-0.1" in codex.doctrines, (
        "with no runtime state, load must fall back to the seed"
    )


def test_load_prefers_runtime_when_it_exists(tmp_path):
    """Runtime file present -> it WINS. Otherwise every restart would silently
    revert to the founding state and discard everything she survived."""
    runtime = tmp_path / "doctrines.json"
    runtime.write_text(json.dumps({
        "active": [{"id": "Doctrine-RUNTIME", "name": "carried forward",
                    "mutation_lineage": [], "scar_links": [], "status": "active"}],
        "fossils": [],
    }), encoding="utf-8")

    codex = Codex(runtime_path=str(runtime))

    assert "Doctrine-RUNTIME" in codex.doctrines
    assert "Doctrine-0.1" not in codex.doctrines, (
        "runtime state must REPLACE the seed on load, not merge with it - "
        "Ruling 32's semantics are deliberately minimal"
    )


def test_scar_core_load_precedence_both_directions(tmp_path):
    """Same contract, second store."""
    absent = tmp_path / "absent" / "scars.json"
    seeded = ScarLogicCore(runtime_path=str(absent))
    assert any(s.id == "\u039417" for s in seeded.scars)

    runtime = tmp_path / "scars.json"
    runtime.write_text(json.dumps([{
        "id": "\u0394999", "name": "runtime scar", "origin": "test",
        "type": "test", "weight": 1, "description": "",
        "linked_doctrines": [], "reflexes": [], "echo_proximity": [],
        "created_at": "2026-07-26T00:00:00", "decay_state": "active",
    }]), encoding="utf-8")

    carried = ScarLogicCore(runtime_path=str(runtime))
    assert [s.id for s in carried.scars] == ["\u0394999"]


def test_echo_memory_does_not_touch_the_seed_into_existence(tmp_path):
    """`_load` used to `touch()` its file when absent - a WRITE inside a
    loader, and the last place anyone would look for one.

    BOTH paths are pointed at absent files ON PURPOSE. An earlier version of
    this test left the seed at its real location, so `source` resolved to the
    existing seed, the absent-branch never ran, and the test passed for the
    wrong reason - it survived the exact mutation it existed to catch. A
    loader must create NEITHER of its candidate sources.
    """
    absent_runtime = tmp_path / "never" / "echoes.jsonl"
    absent_seed = tmp_path / "no_seed" / "echoes.jsonl"
    real_seed_before = Path("data/echoes.jsonl").read_bytes()

    memory = EchoMemory(seed_path=str(absent_seed),
                        runtime_path=str(absent_runtime))

    assert not absent_runtime.exists(), "the loader created its runtime source"
    assert not absent_seed.exists(), "the loader created its SEED source"
    # RULING 75 MIGRATION (2026-08-05), Ruling-14 form - and it is STRICTLY
    # STRONGER rather than merely adjusted.
    #     OLD: `assert memory.echoes == []`
    #     NEW: `assert memory.read_all() == ()` (the old line KEPT below).
    # `self.echoes` is now the declared WRITE-ONLY per-process mirror, so
    # asserting it is empty at construction became trivially true the moment
    # `_load()` was deleted - a pin passing for a reason unrelated to its
    # subject. `read_all()` asks the FILE, which is the claim this test is
    # actually making: neither absent source was created, and reading finds
    # nothing because there is nothing rather than because nobody looked.
    assert memory.read_all() == ()
    assert memory.echoes == []
    assert Path("data/echoes.jsonl").read_bytes() == real_seed_before


@pytest.mark.parametrize("cls", [Codex, ScarLogicCore, EchoMemory],
                         ids=lambda c: c.__name__)
def test_the_runtime_class_default_is_never_the_seed_default(cls):
    """The class attributes themselves must differ.

    Every test runs under `conftest`, which redirects `runtime_path` - so if
    `RUNTIME_PATH` were changed to equal `SEED_PATH`, no behavioral test in
    this suite could see it, while PRODUCTION would overwrite the seed on the
    first save. The fixture hides exactly the defect the ruling is about.

    So this is asserted at the class level, where the fixture cannot mask it.
    """
    assert cls.RUNTIME_PATH != cls.SEED_PATH, (
        f"{cls.__name__}.RUNTIME_PATH collides with its SEED_PATH - in "
        f"production the first save would overwrite the seed"
    )
    assert cls.RUNTIME_PATH.startswith("data/runtime/"), (
        f"{cls.__name__}.RUNTIME_PATH must sit under the gitignored runtime "
        f"prefix, or a run's state lands in version control"
    )


def test_the_fixture_redirected_every_store_it_claims_to(tmp_path):
    """The fixture's OWN correctness, pinned.

    `_redirect_default` locates the parameter BY NAME because the older
    positional form (`defaults[-1]`) is wrong for any store whose path is not
    the last defaulted parameter - `TetherProtocol.telemetry_path` is followed
    by three callbacks, so the positional form would have bound `on_abort` to
    a path string and left telemetry pointing at the real forensic directory.

    Nothing constructs a TetherProtocol in this suite, so no behavioral test
    can observe that. This inspects the live patched defaults instead, which
    is what the fixture actually produced.
    """
    import inspect

    from src.expansion.tether.session_governor import TetherProtocol
    from src.topology.tca_core import TopologicalSpace

    expected = [
        (Codex, "runtime_path"),
        (ScarLogicCore, "runtime_path"),
        (EchoMemory, "runtime_path"),
        (TopologicalSpace, "filepath"),
        (TetherProtocol, "telemetry_path"),
    ]
    for cls, param in expected:
        bound = inspect.signature(cls.__init__).parameters[param].default
        assert bound is not None and str(tmp_path) in str(bound), (
            f"{cls.__name__}.{param} was not redirected into tmp (got "
            f"{bound!r}) - the fixture patched the wrong parameter"
        )

    # ...and no NON-path default was clobbered in the process.
    for cb in ("on_escalate", "on_suspend", "on_abort"):
        assert inspect.signature(TetherProtocol.__init__).parameters[cb].default is None, (
            f"TetherProtocol.{cb} was overwritten by the redirect - this is "
            f"the positional-assumption defect"
        )


def test_explicit_filepath_collapses_both_paths(tmp_path):
    """The single-path form tests use. It is an EXPLICIT caller choice, and it
    is deliberately not how the pipeline constructs a store - `aurea_core`
    calls `Codex()`, which reads the seed and writes only runtime."""
    one = tmp_path / "isolated.json"
    codex = Codex(filepath=str(one))

    assert codex.seed_path == codex.runtime_path == one
    assert codex.doctrines == {}, "an isolated store must not inherit the seed"


# =====================================================================
# PIN 3 - THE RUNTIME PREFIX IS IGNORED
# =====================================================================

def test_gitignore_covers_the_runtime_prefix():
    """STRUCTURAL, legitimately (Ruling 17's carve-out): whether a glob appears
    in `.gitignore` is a genuine property OF SOURCE.

    Seeds STAY TRACKED - untracking them would be the opposite of this
    ruling's remedy, which is that they have no writer, not that git stops
    watching them."""
    ignored = {line.strip() for line in
               Path(".gitignore").read_text(encoding="utf-8").splitlines()}
    assert "data/runtime/" in ignored

    for _, seed_rel in SEEDS:
        assert seed_rel not in ignored, (
            f"{seed_rel} is a SEED and must remain tracked"
        )


# =====================================================================
# PIN 4 - NO WRITE CALL IN src/ TARGETS A SEED PATH (AST)
# =====================================================================

def test_no_write_call_in_src_targets_a_seed_path():
    """STRUCTURAL/AST, and the same shape as "no module but the owner writes
    this store" (Ruling 1's invariant): a genuine property OF SOURCE.

    Scans every write-mode `open()` in `src/` and refuses any whose target is
    a seed path - whether spelled as a literal, as `self.seed_path`, or as
    `SEED_PATH`. This is what makes the overwrite UNEXECUTABLE rather than
    merely absent: a future author cannot reintroduce it without this failing.
    """
    import ast

    seed_literals = {rel for _, rel in SEEDS}
    seed_attrs = {"seed_path", "SEED_PATH"}
    violations = []

    for path in sorted(Path("src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                continue
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            if not any(m in mode for m in ("w", "a", "x", "+")):
                continue                      # read-only open: seeds may be READ

            target = node.args[0] if node.args else None
            detail = None
            if isinstance(target, ast.Constant) and target.value in seed_literals:
                detail = f"seed literal {target.value!r}"
            elif isinstance(target, ast.Attribute) and target.attr in seed_attrs:
                detail = f"`.{target.attr}`"
            elif isinstance(target, ast.Name) and target.id in seed_attrs:
                detail = f"`{target.id}`"
            if detail:
                violations.append(
                    f"{path.as_posix()}:{node.lineno} opens {detail} in mode "
                    f"{mode!r}"
                )

    assert not violations, (
        "RULING 32 VIOLATED - a write call in src/ targets a SEED path:\n  "
        + "\n  ".join(violations)
        + "\n\n  The seed is READ-ONLY INPUT. Write to the runtime path."
    )


def test_the_ast_pin_would_catch_a_reintroduced_seed_write():
    """The scanner above is only worth its line count if it can actually see
    the defect. Feeds it the exact code Ruling 32 forbids and asserts it is
    flagged - a pin on the pin, because an AST check that silently matches
    nothing is the classic way a structural test becomes decoration.
    """
    import ast

    offending = ast.parse(
        'with open(self.seed_path, "w", encoding="utf-8") as f:\n    pass\n')
    writes = [
        n for n in ast.walk(offending)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "open"
        and isinstance(n.args[0], ast.Attribute)
        and n.args[0].attr == "seed_path"
        and "w" in str(n.args[1].value)
    ]
    assert writes, "the scanner's matching logic does not detect a seed write"
