"""
test_ruling75.py - RULING 75: THE ECHOMEMORY WIRING (the five-pressure ruling).

    An echo that persists nowhere is not a memory of perception.

Five pressures accumulated against one seam and this ruling resolves all five in
one motion: EchoMemory becomes a real sibling ledger, the core persists every
perceived echo, echoes become the FOURTH topology source, the wall-clock id dies
at its source, and Batch 66's reserved schema decision is discharged.

WHERE THE REST OF THIS RULING'S PINS LIVE:
  * `tests/test_ruling69.py` - the shared mint's FIFTH consumer inherits the
    whole battery at the `ECH-` prefix.
  * `tests/test_ruling65.py` - the echo-exclusion pin, REVERSED BY RULING and
    migrated in place; that ruling named this one as its reopening condition.
  * `tests/test_ruling60.py` - Ruling 60's construction-site laws, moved with
    the construction site.
  * `tests/test_autonomy_index.py`, `test_seed_isolation.py`, `test_docket_n.py`,
    `test_ruling58.py`, `test_ruling68.py` - migrations, no assertion moved.

**THE `paradox_void` PREDICTION IS MEASURED HERE AND IT DID NOT HOLD.** See
`test_h_...` below: the measurement is pinned as a FINDING, not repaired.
"""

from __future__ import annotations

import ast
import builtins
import inspect
import json
from datetime import datetime
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.perception.spl import SPL
from src.topology.tca_core import NodeType
from src.utils.echo_memory import EchoLogUnreadable, EchoMemory
from src.utils.models import Echo

REPO = Path(__file__).resolve().parents[1]
MODULE = "src/utils/echo_memory.py"


def _tree(rel=MODULE):
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


def _memory(tmp_path, name="echoes.jsonl"):
    return EchoMemory(filepath=str(tmp_path / name))


# =====================================================================
# (a) THE MINT - the shared helper's FIFTH consumer
# =====================================================================

def test_a_record_mints_file_derived_ech_ids(tmp_path):
    """PIN (a) / res.1. **THE WRITER OWNS THE MINT** (Ruling 69's law)."""
    memory = _memory(tmp_path)
    ids = [memory.record(f"claim {i}").id for i in range(3)]
    assert ids == ["ECH-0001", "ECH-0002", "ECH-0003"]

    # DERIVED FROM THE FILE, not from memory: a second instance over the same
    # path continues the sequence rather than restarting it.
    assert _memory(tmp_path).record("fourth").id == "ECH-0004"


def test_a_legacy_wall_clock_ids_never_collide_with_the_ech_scan(tmp_path):
    """PIN (a) / res.1. **A DIFFERENT NAMESPACE, and it is pinned rather than
    assumed.**

    The store may hold `Echo-20260805175535779367` lines written before this
    ruling. The anchored `ECH-` scan must neither be raised by them (burning
    ordinals) nor reissue over them.
    """
    path = tmp_path / "echoes.jsonl"
    path.write_text(
        json.dumps({"id": "Echo-20260805175535779367", "content": "legacy",
                    "resonance_score": 1.0,
                    "created_at": "2026-08-05 17:55:35.779367",
                    "doctrine_link": None, "claim_id": None}) + "\n",
        encoding="utf-8")

    memory = EchoMemory(filepath=str(path))
    assert memory.record("first ruled echo").id == "ECH-0001", (
        "a wall-clock id raised the ECH floor - different namespaces")
    assert [e.id for e in memory.read_all()] == [
        "Echo-20260805175535779367", "ECH-0001"]


def test_a_the_mint_and_the_append_happen_inside_the_lock():
    """PIN (a). **DECLARED STRUCTURAL PER RULING 17, WRITTEN AT DRAFTING** -
    the standing form, applied before a survivor could find it.

    Dropping `with mint_lock(...)` survives every behavioural pin, and it has
    to: the lock guards CONCURRENT mints, and every mint re-derives from the
    file, so a single-threaded run cannot tell a held lock from a missing one.
    """
    record = next(n for n in ast.walk(_tree())
                  if isinstance(n, ast.FunctionDef) and n.name == "record")
    guarded = [w for w in ast.walk(record) if isinstance(w, ast.With)
               and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id == "mint_lock"
                       for item in w.items
                       for c in ast.walk(item.context_expr))]
    assert guarded, "`record` does not take the mint lock at all"

    calls = {n.func.attr for n in ast.walk(guarded[0])
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "_next_id" in calls, "the MINT happens outside the lock"
    assert "_append" in calls, "the APPEND happens outside the lock"


def test_a_no_cached_ordinal_exists_before_or_after_minting(tmp_path):
    """PIN (a). Ruling 69 res.1 at the fifth prefix."""
    memory = _memory(tmp_path)
    assert not hasattr(memory, "_seq")
    memory.record("x")
    assert not hasattr(memory, "_seq")


# =====================================================================
# (b) `add_echo` IS ABSENT AS SHAPE
# =====================================================================

def test_b_no_caller_minted_door_exists():
    """PIN (b) / res.1. **DELETED AS SHAPE** (Ruling 65's form): there is no
    path that accepts an identity from outside, so the wall-clock id is
    unwritable rather than merely inadvisable."""
    assert not hasattr(EchoMemory, "add_echo")

    defined = {n.name for n in ast.walk(_tree())
               if isinstance(n, ast.FunctionDef)}
    for name in ("add_echo", "append_echo", "store_echo", "put_echo"):
        assert name not in defined, f"a caller-minted door reappeared: {name}"

    # AND `record` TAKES NO ID. Content is positional; everything else is
    # keyword-only; `id` is not a parameter at all.
    params = inspect.signature(EchoMemory.record).parameters
    assert list(params) == ["self", "content", "claim_id", "doctrine_link",
                            "resonance_score"]
    assert "id" not in params


def test_b_the_absence_scanner_actually_fires():
    """The scanner's own control - Ruling 32's answer to the vacuous pin."""
    defined = {n.name for n in ast.walk(ast.parse(
        "class M:\n    def add_echo(self, echo): pass\n"))
        if isinstance(n, ast.FunctionDef)}
    assert "add_echo" in defined


def test_b_spl_no_longer_constructs_an_echo_or_reads_a_clock():
    """PIN (b) / res.1. **SPL STOPPED MINTING, AND THE ENFORCEMENT IS SCOPE.**

    It does not construct an Echo, and it cannot mint from a clock because it
    no longer imports one.
    """
    tree = _tree("src/perception/spl.py")
    assert not any(isinstance(n, ast.Call) and getattr(n.func, "id", None) == "Echo"
                   for n in ast.walk(tree)), "SPL constructs an Echo again"

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.update(node.module.split("."))
    assert "datetime" not in imported, "SPL can read a clock again"

    assert not hasattr(SPL, "process_input"), (
        "SPL.process_input is back - deletion, not deprecation")
    assert SPL().normalize("  hello  ") == "hello"


# =====================================================================
# (c) THE SCHEMA - Batch 66's reservation, discharged
# =====================================================================

def test_c_round_trip_fidelity_on_the_ruled_schema(tmp_path):
    """PIN (c) / res.2. Every field survives, and `created_at` EXACTLY."""
    memory = _memory(tmp_path)
    written = memory.record("a claim about water",
                            claim_id="CLM-0007",
                            doctrine_link="Doctrine-0",
                            resonance_score=0.25)

    reloaded = EchoMemory(filepath=str(tmp_path / "echoes.jsonl")).read_all()
    assert len(reloaded) == 1
    back = reloaded[0]
    assert back.id == written.id == "ECH-0001"
    assert back.content == "a claim about water"
    assert back.claim_id == "CLM-0007"
    assert back.doctrine_link == "Doctrine-0"
    assert back.resonance_score == 0.25
    assert back.created_at == written.created_at
    assert isinstance(back.created_at, datetime)

    # ON THE BYTES: `created_at` is isoformat, and it is not a `repr`.
    line = json.loads((tmp_path / "echoes.jsonl").read_text(
        encoding="utf-8").strip())
    assert line["created_at"] == written.created_at.isoformat()
    assert "T" in line["created_at"]


def test_c_the_writer_carries_no_default_and_refuses_nan():
    """PIN (c) / res.2. **`default=str` IS DELETED** - Batch 66's one
    load-bearing exemption, discharged by making the conversion explicit.

    `default=` is a COERCION, and Ruling 66's law is REFUSAL NEVER COERCION.
    """
    append = next(n for n in ast.walk(_tree())
                  if isinstance(n, ast.FunctionDef) and n.name == "_append")
    dumps = [n for n in ast.walk(append) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "dumps"]
    assert len(dumps) == 1
    keywords = {k.arg for k in dumps[0].keywords}
    assert "default" not in keywords, "`default=str` is back at the writer"
    assert "allow_nan" in keywords

    # AND AT NO OTHER `json.dumps` IN THE MODULE.
    #
    # **SCANNED BY AST, NOT BY SUBSTRING** - the first draft asserted
    # `"default=str" not in source` and went red on this module's own
    # DOCSTRINGS, which legitimately explain what the exemption was and why it
    # is gone (four occurrences, all prose). Ruling 63's precedent governs:
    # deleting correct documentation to satisfy a noisy guard is how a guard
    # earns its eventual weakening. The instrument was sharpened; the prose
    # stands - and this is that defect class's EIGHTH appearance.
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "dumps":
            assert "default" not in {k.arg for k in node.keywords}, (
                f"`default=` returned at line {node.lineno}")
    # The explanation must survive, or the next pass will not know what was
    # discharged here.
    assert "default=str" in (REPO / MODULE).read_text(encoding="utf-8"), (
        "the record of Batch 66's discharged exemption was deleted")


def test_c_the_writer_gate_refuses_a_non_canonical_value(tmp_path):
    """PIN (c). **THE VALIDATOR AT ITS OWN DOOR** - Ruling 74's lesson, applied
    at drafting.

    Every field is type-clean on the real path, so driving a bytearray through
    `record` would pass for a NEIGHBOURING guard's reason and witness nothing
    about this one. A backstop is pinned where it can still be violated.
    """
    from src.utils.record_value import NonCanonicalRecordValue

    memory = _memory(tmp_path)
    with pytest.raises(NonCanonicalRecordValue, match="echo_entry"):
        memory._append({"id": "ECH-0001", "blob": bytearray(b"nope")})
    assert not (tmp_path / "echoes.jsonl").exists(), (
        "a refused entry created the file - the gate must run BEFORE mkdir")


def test_c_the_writer_gate_runs_before_mkdir_and_open():
    """PIN (c). Batch 66's writer discipline as SHAPE: validate, THEN create."""
    append = next(n for n in ast.walk(_tree())
                  if isinstance(n, ast.FunctionDef) and n.name == "_append")
    order = []
    for node in ast.walk(append):
        if isinstance(node, ast.Call):
            name = (getattr(node.func, "id", None)
                    or getattr(node.func, "attr", None))
    # MIGRATED 2026-08-09 (RULING 78), old text struck below, ASSERTION
    # UNCHANGED IN SUBSTANCE. The gate-before-creation property is exactly
    # what it was; what moved is the CREATION CALL. R78 routed every append
    # in `src/` through `durable_append_text`, so the file-creating call in
    # this method is now that helper rather than a raw `open` - and the
    # helper does the `mkdir` too. Scanning for `open` alone would find
    # nothing and PASS VACUOUSLY, which is the quietest way for a structural
    # pin to survive while measuring nothing.
    #
    #     ~~if name in ("validate_record_value", "mkdir", "open"):~~
            if name in ("validate_record_value", "mkdir", "open",
                        "durable_append_text"):
                order.append((node.lineno, name))
    sequence = [name for _, name in sorted(order)]
    assert sequence.index("validate_record_value") < sequence.index("mkdir")
    assert (sequence.index("validate_record_value")
            < sequence.index("durable_append_text")), (
        "the writer gate must run before the append helper - a gate that\n"
        "runs after the write has already left a line behind")
    assert "open" not in sequence, (
        "RULING 78: this write must route through the append funnel, not a\n"
        "raw open - see the AST census in tests/test_ruling78.py")


def test_c_the_only_write_mode_is_append():
    """PIN (c). Mode `"a"` only - what makes the record unrewritable in fact.

        ~~assert "a" in modes~~

    MIGRATED 2026-08-09 (RULING 78), old assertion struck above. The PROPERTY
    is unchanged and so is its first half: no rewriting mode may appear in this
    module, ever. What moved is where the append LIVES - R78 routed every
    append in `src/` through `durable_append_text`, so this module now holds no
    write-mode `open` at all and `"a" in modes` asserts the presence of a
    mechanism the ruling deliberately removed.

    IT IS REPLACED RATHER THAN DELETED, because its job was to stop the append
    path VANISHING - a module with no write at all would satisfy the
    `<= {"a", "r"}` half perfectly. The successor asserts the same thing about
    the funnel: the append path is still here, it is just named.
    """
    modes = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "open":
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                modes.append(node.args[1].value)
    assert set(modes) <= {"a", "r"}, f"a non-append write mode appeared: {modes}"

    appends = [n for n in ast.walk(_tree())
               if isinstance(n, ast.Call)
               and getattr(n.func, "id", None) == "durable_append_text"]
    assert appends, "the append path vanished"


# =====================================================================
# (d) TOLERANT LOAD - bytes untouched forever
# =====================================================================

def test_d_a_legacy_line_loads_clean_and_its_bytes_are_untouched(tmp_path):
    """PIN (d) / res.2. **THE RECORD KEEPS EVERYTHING; THE OBJECT HOLDS THE
    CURRENT SCHEMA.**

    Ruling 68's forensic law: *"legacy bytes are untouched ... no migration, and
    no reader-side reinterpretation of what a stored value used to mean."* A
    `source` key - deleted from `Echo` by that ruling - is dropped at OBJECT
    construction and never from the file.
    """
    path = tmp_path / "echoes.jsonl"
    legacy = {"id": "Echo-20260801120000000000", "content": "legacy claim",
              "source": "user",                       # DELETED by Ruling 68
              "resonance_score": 1.0,
              "created_at": "2026-08-01 12:00:00.000000",   # `str(datetime)`
              "doctrine_link": None, "claim_id": None}
    raw = json.dumps(legacy) + "\n"
    path.write_text(raw, encoding="utf-8")
    before = path.read_bytes()

    memory = EchoMemory(filepath=str(path))
    loaded = memory.read_all()

    assert len(loaded) == 1
    echo = loaded[0]
    assert echo.id == "Echo-20260801120000000000"
    assert echo.content == "legacy claim"
    assert not hasattr(echo, "source"), "the deleted field reached the object"
    assert echo.created_at == datetime(2026, 8, 1, 12, 0, 0)

    assert path.read_bytes() == before, "a READ rewrote the record"

    # AND A WRITE APPENDS - it never rewrites the legacy line.
    memory.record("a new one")
    assert path.read_bytes().startswith(before), (
        "the legacy line was not preserved verbatim at the head of the file")


def test_d_both_timestamp_forms_parse(tmp_path):
    """PIN (d) / res.2. `fromisoformat` accepts the isoformat this build writes
    AND the space-separated `str(datetime)` the `default=str` era produced -
    verified against both rather than assumed."""
    stamp = datetime(2026, 8, 1, 12, 34, 56, 789012)
    path = tmp_path / "echoes.jsonl"
    with open(path, "a", encoding="utf-8") as handle:
        for index, rendered in enumerate((str(stamp), stamp.isoformat()), 1):
            handle.write(json.dumps({
                "id": f"ECH-{index:04d}", "content": "c",
                "resonance_score": 1.0, "created_at": rendered,
                "doctrine_link": None, "claim_id": None}) + "\n")

    loaded = EchoMemory(filepath=str(path)).read_all()
    assert [e.created_at for e in loaded] == [stamp, stamp]


def test_d_an_unparseable_line_contributes_nothing(tmp_path):
    """PIN (d). Floor semantics - never coerced, never guessed at."""
    path = tmp_path / "echoes.jsonl"
    memory = EchoMemory(filepath=str(path))
    memory.record("real")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("{ not json at all\n")
        handle.write(json.dumps({"id": "ECH-0002", "content": "c",
                                 "resonance_score": 1.0,
                                 "created_at": "not-a-timestamp",
                                 "doctrine_link": None,
                                 "claim_id": None}) + "\n")

    assert [e.id for e in memory.read_all()] == ["ECH-0001"]
    # ...AND THE ORDINAL IS STILL BURNT, never reissued (Ruling 69 res.2).
    assert memory.record("next").id == "ECH-0003"


# =====================================================================
# (e) READS RE-READ THE FILE
# =====================================================================

def test_e_a_second_instances_append_is_visible_to_the_first(tmp_path):
    """PIN (e) / res.3. **THE FILE IS THE LEDGER**, and reads ask it.

    Under the old memory-serving reads the first instance would answer from a
    snapshot taken at construction and never see this.
    """
    first = _memory(tmp_path)
    first.record("from the first")
    second = _memory(tmp_path)
    second.record("from the second")

    assert [e.content for e in first.read_all()] == ["from the first",
                                                     "from the second"]
    assert first.get_echo("ECH-0002").content == "from the second"
    assert len(first.list_echoes()) == 2


def test_e_the_mirror_is_write_only_and_declared(tmp_path):
    """PIN (e) / res.3. `self.echoes` holds what THIS PROCESS appended - it is
    NOT the store, and nothing reads it back into a decision."""
    first = _memory(tmp_path)
    first.record("mine")
    second = _memory(tmp_path)
    second.record("theirs")

    assert [e.content for e in first.echoes] == ["mine"]
    assert [e.content for e in second.echoes] == ["theirs"]
    assert len(first.read_all()) == 2, "the FILE holds both"

    # NO `_load`: a constructor that populated memory would build the stale
    # authority Rulings 63 and 65 each refused.
    assert not hasattr(EchoMemory, "_load")
    assert _memory(tmp_path).echoes == []


def test_e_an_unreadable_log_raises_typed_on_read_and_on_the_mint(tmp_path,
                                                                  monkeypatch):
    """PIN (e) / res.3. **RULING 74'S LESSON, APPLIED AT DRAFTING.**

    Returning `()` would render "I could not look" as "there is nothing there" -
    which at this store reads as a perception having never happened.
    """
    memory = _memory(tmp_path)
    memory.record("recorded before the disk failed")
    target = str(memory.runtime_path)
    real_open = builtins.open

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == target and "r" in mode:
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    for call in (lambda: memory.read_all(),
                 lambda: memory.get_echo("ECH-0001"),
                 lambda: memory.list_echoes(),
                 lambda: memory.record("this must not mint")):
        with pytest.raises(EchoLogUnreadable):
            call()


def test_e_a_missing_log_is_an_empty_history_not_a_failure(tmp_path):
    """PIN (e). Absence is a first run, not a fault."""
    memory = _memory(tmp_path, name="never_written.jsonl")
    assert memory.read_all() == ()
    assert memory.list_echoes() == []
    assert memory.get_echo("ECH-0001") is None
    assert not memory.runtime_path.exists(), "a read created its source"


# =====================================================================
# (f) THE ONE-PER-CYCLE PAIR
# =====================================================================

def test_f_one_ech_line_and_one_clm_line_per_claim_cycle():
    """PIN (f) / res.4. **THE PAIR** - Ruling 68's one-CLM guarantee, extended.

    N claim cycles -> N CLM lines AND N ECH lines. The pair's whole value is
    that the two counts match: a claim perceived is a claim recorded, on both
    surfaces, once.
    """
    core = AureaCore()
    claims = ["Water is wet.", "Truth survives collapse.", "", "   ",
              "Honesty is pointless.", "Fracture Carried is false."]
    for claim in claims:
        core.process_input(claim)

    echoes = core.echo_memory.read_all()
    ancestry = Path(core.ancestry.ledger_path).read_text(
        encoding="utf-8").strip().splitlines()

    assert len(echoes) == len(claims) == len(ancestry)
    assert [e.id for e in echoes] == [f"ECH-{i:04d}"
                                      for i in range(1, len(claims) + 1)]
    # AND THE JOIN IS ONE-TO-ONE, IN ORDER.
    assert [e.claim_id for e in echoes] == [
        json.loads(line)["claim_id"] for line in ancestry]


def test_f_a_suspended_pass_and_a_non_str_arrival_write_neither():
    """PIN (f). Both gates sit ABOVE the perception, so the pair holds at zero
    as well as at N - Rider R2's declaration and Ruling 68's type gate."""
    core = AureaCore()
    core.processing_suspended = True
    core.process_input("this must not be perceived")
    assert core.echo_memory.read_all() == ()
    assert not Path(core.ancestry.ledger_path).exists()

    core.processing_suspended = False
    for bad in (None, 7, ["a"], object()):
        core.process_input(bad)
    assert core.echo_memory.read_all() == ()
    assert not Path(core.ancestry.ledger_path).exists()


# =====================================================================
# (g) THE PROBE IS NOT A PERCEPTION
# =====================================================================

def test_g_the_nova_probe_neither_persists_nor_mints():
    """PIN (g) / res.4. **A PROBE IS NOT A PERCEPTION.**

    The probe re-filters a doctrine's own text to see whether Nova's strain
    survives collapse - an internal question asked of material already on
    record. Persisting it would put a line in the perception lineage for
    something nobody said, and break the pair above.
    """
    source = (REPO / "src/aurea_core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    probe_sites = [n for n in ast.walk(tree)
                   if isinstance(n, ast.Call)
                   and getattr(n.func, "id", None) == "Echo"]
    assert len(probe_sites) == 1, (
        f"expected exactly one direct Echo construction (the probe), found "
        f"{len(probe_sites)}")

    # It is built DIRECTLY, never through the ledger.
    route = next(n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef)
                 and n.name == "_nova_route_collapse")
    calls = {getattr(n.func, "attr", None) for n in ast.walk(route)
             if isinstance(n, ast.Call)}
    assert "record" not in calls, "the probe was routed through the ledger"

    # And exactly ONE site calls `echo_memory.record` in all of `src/`.
    recorders = [f"{n.lineno}" for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "record"
                 and isinstance(n.func.value, ast.Attribute)
                 and n.func.value.attr == "echo_memory"]
    assert len(recorders) == 1, f"echo_memory.record has {len(recorders)} sites"


# =====================================================================
# (h) THE FOURTH SOURCE - and the MEASURED prediction
# =====================================================================

def test_h_every_persisted_echo_is_rebuilt_at_restart():
    """PIN (h) / res.5 + res.6. **ECHOES ARE THE FOURTH SOURCE.**"""
    core = AureaCore()
    for claim in ("Water is wet.", "Truth survives collapse.",
                  "Honesty is pointless."):
        core.process_input(claim)

    live = sorted(n for n, v in core.tca.topology.nodes.items()
                  if v.node_type is NodeType.ECHO)
    assert len(live) == 3

    resumed = AureaCore()
    rebuilt = sorted(n for n, v in resumed.tca.topology.nodes.items()
                     if v.node_type is NodeType.ECHO)
    assert rebuilt == live, "a persisted echo did not return to the map"
    assert rebuilt == sorted(e.id for e in resumed.echo_memory.read_all()), (
        "the rebuild is from the RECORD, not from the snapshot")


def test_h_the_rebuild_order_places_echoes_last():
    """PIN (h) / res.5. Scars -> doctrines -> paradoxes -> ECHOES: every
    referent exists before the thing that refers to it. Ruling 57's mechanism
    extended by one loop rather than a new rule."""
    # SCOPED TO `AureaCore.__init__` BY CLASS, not by the first `__init__` the
    # walk happens to reach - `aurea_core.py` defines several classes, and the
    # first draft of this pin silently scanned `SymbolicPressureMonitor` and
    # found nothing, which is the quietest way for a structural pin to pass
    # while measuring the wrong body.
    core_class = next(n for n in ast.walk(_tree("src/aurea_core.py"))
                      if isinstance(n, ast.ClassDef) and n.name == "AureaCore")
    init = next(n for n in core_class.body
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    order = []
    for node in ast.walk(init):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("place_scar", "place_doctrine",
                                  "place_paradox", "place_echo"):
                order.append((node.lineno, node.func.attr))
    assert [name for _, name in sorted(order)] == [
        "place_scar", "place_doctrine", "place_paradox", "place_echo"]


def test_h_there_is_one_echo_placement_path():
    """PIN (h) / res.5. Ruling 65 res.5's lesson: ONE placement path rather than
    two that have to be kept in agreement."""
    tree = _tree("src/aurea_core.py")
    inline = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Attribute)
              and n.func.attr == "add_node"]
    assert inline == [], (
        f"`aurea_core` places a node inline at {inline}; placement belongs to "
        f"the owner's `place_*` methods")

    placements = [n.lineno for n in ast.walk(tree)
                  if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Attribute)
                  and n.func.attr == "place_echo"]
    assert len(placements) == 2, (
        f"expected exactly two `place_echo` call sites (live + rebuild), "
        f"found {len(placements)}")


def test_h_place_echo_creates_no_edges(tmp_path):
    """PIN (h) / res.5. **NO EDGE IS INVENTED AT PLACEMENT** - the inline path
    this replaced created none, and creating one here would be a topology
    change this ruling declares out of scope."""
    place = next(n for n in ast.walk(_tree("src/topology/tca_integration.py"))
                 if isinstance(n, ast.FunctionDef) and n.name == "place_echo")
    calls = {getattr(n.func, "attr", None) for n in ast.walk(place)
             if isinstance(n, ast.Call)}
    assert "create_edge" not in calls

    core = AureaCore()
    echo = core.echo_memory.record("standalone", doctrine_link="Doctrine-0")
    node = core.tca.place_echo(echo)
    assert node.edges == set() or list(node.edges) == [], (
        "place_echo created an edge - including one for `doctrine_link`, which "
        "the inline path never created either")


def test_h_the_paradox_void_center_survives_restart():
    """PIN (h) - **SUPERSEDED 2026-08-05 BY RULING 76. THE TRIPWIRE FIRED WHEN
    THE DEFECT DIED, WHICH IS WHAT IT WAS FOR.**

        ~~test_h_the_paradox_void_prediction_is_measured_and_did_not_hold~~

        THE OLD PIN, KEPT VERBATIM - it demanded that a later pass come here
        and say why, and this docstring is that saying:

            PIN (h) / res.5. **THE MEASUREMENT, PINNED AS A FINDING RATHER
            THAN REPAIRED.**

            Ruling 65's comment PREDICTED IN WRITING that `paradox_void` would
            regain a gravity center once echoes became the fourth source,
            because a paradox node's only edge is the echo->paradox edge. **The
            prediction DID NOT HOLD**, and this pin records why: rebuilding the
            NODES was never the same thing as rebuilding the EDGES.
            `place_echo` creates none - deliberately - so a rebuilt paradox
            node still carries zero edges, `_recalculate_center` scores
            `mass * len(edges)` = 0, and its strict `>` correctly selects
            nothing.

            **A FAILED PREDICTION IS A BOARD FINDING, NOT A PASS REPAIR**
            (res.5). This pin exists so the finding is measured on every run
            rather than remembered, and so that a later pass that "fixes" it
            has to come here and say why.

            assert all(not rebuilt.nodes[p].edges for p in paradoxes)
            assert rebuilt.constellations["paradox_void"].gravity_center is None

    **WHY IT IS NOW THE OPPOSITE, AND WHY THAT IS NOT A WEAKENING.** Ruling 75
    forbade IMPROVISING these edges - inventing relationships the records could
    not support - and that prohibition STANDS. Ruling 76 did not improvise
    them: it added the missing JOINS at the creation sites
    (`SuspensionEntry.claim_id`, `Scar.claim_id`, `Scar.origin_pressure`) so
    the edge is DERIVED from recorded facts, exactly like every other edge in
    this map. **The old pin's own reasoning is what forced the correct fix
    rather than a convenient one.**

    `place_echo` still creates NO edge (that pin above is untouched), and
    Ruling 57 res.3's fallback prohibition is untouched: the center returns
    because the node regains a RECORDED edge, not because anything selects an
    anchor in the absence of one.
    """
    core = AureaCore()
    for claim in ("This statement is false.", "I always lie.",
                  "A is not A.", "Everything I say is a lie and this is true."):
        core.process_input(claim)

    topo = core.tca.topology
    paradoxes = [n for n, v in topo.nodes.items()
                 if v.node_type is NodeType.PARADOX]
    if not paradoxes:
        pytest.skip("no claim in this set suspended into the Black Sphere")

    live_center = topo.constellations["paradox_void"].gravity_center
    assert live_center is not None, "precondition: a live paradox_void center"
    assert any(topo.nodes[p].edges for p in paradoxes), (
        "precondition: the live paradox carries its echo edge")

    resumed = AureaCore()
    rebuilt = resumed.tca.topology
    assert [n for n, v in rebuilt.nodes.items()
            if v.node_type is NodeType.PARADOX] == paradoxes, (
        "the paradox node itself is rebuilt")
    assert all(rebuilt.nodes[p].edges for p in paradoxes), (
        "a rebuilt paradox lost its echo edge - Ruling 76 derives it from "
        "`SuspensionEntry.claim_id`, so this means the join is not surviving "
        "its own persistence boundary (the defect this ruling's first "
        "measurement caught)")
    assert rebuilt.constellations["paradox_void"].gravity_center == live_center, (
        "`paradox_void` lost its center at restart. Ruling 76's whole success "
        "criterion is that it does not - the edge is a DERIVATION now.")


def test_h_the_event_edges_are_rebuilt_from_recorded_joins():
    """PIN (h) - **SUPERSEDED 2026-08-05 BY RULING 76**, the twin of the pin
    above and superseded for the same reason.

        ~~test_h_runtime_edges_are_not_rebuilt_and_the_loss_is_recorded~~

        THE OLD PIN, KEPT VERBATIM:

            PIN (h) / res.5. The second half of the measurement, and the one
            the first draft of the in-file comment MISSED: there are TWO
            runtime edge sites, not one.

                echo -> paradox   (the PARADOX_SUSPENDED branch)
                echo -> scar      (the scar-formed branch)

            Both record what HAPPENED TO A CLAIM rather than where a node
            belongs, and neither is recoverable from the echo record alone -
            which is exactly why reconstructing them would be inventing
            relationships rather than restoring them.

            assert not (live_echo_edges & rebuilt_edges), (
                "a runtime echo edge was reconstructed at rebuild - res.5
                forbids improvising that, so if it is now intended it needs a
                ruling")

    **THE OLD MESSAGE NAMED ITS OWN SUCCESSOR CONDITION** - *"if it is now
    intended it needs a ruling"* - and Ruling 76 is that ruling. What made the
    reconstruction legitimate is that it stopped being a reconstruction: the
    records now CARRY the join, so the edge is derived rather than remembered.

    The identification of TWO sites survives and is still the point; both are
    now derivable, and both are asserted here.

    **`save_state()` IS REQUIRED HERE AND THE ASYMMETRY IS PRE-EXISTING, NOT
    THIS RULING'S.** The two stores checkpoint differently: `BlackSphere.suspend`
    calls `save_to_file()` eagerly inside itself, while `ScarLogicCore.add_scar`
    says in terms "DO NOT auto-save here" and leaves it to
    `AureaCore.save_state()`. So a restart without a checkpoint loses the SCAR,
    not merely its edge - and the edge is correctly absent because its endpoint
    is. Driving a real checkpoint is the honest restart scenario; the first
    draft of this migration omitted it and the pin caught the difference.
    """
    core = AureaCore()
    for claim in ("This statement is false.", "Honesty is pointless.",
                  "A is not A."):
        core.process_input(claim)
    core.save_state()

    live_edges = {(n, e) for n, v in core.tca.topology.nodes.items()
                  for e in v.edges}
    echo_ids = {n for n, v in core.tca.topology.nodes.items()
                if v.node_type is NodeType.ECHO}
    live_echo_edges = {(a, b) for a, b in live_edges
                       if a in echo_ids or b in echo_ids}
    if not live_echo_edges:
        pytest.skip("this claim set produced no runtime echo edge")

    resumed = AureaCore()
    rebuilt_edges = {(n, e) for n, v in resumed.tca.topology.nodes.items()
                     for e in v.edges}
    assert live_echo_edges <= rebuilt_edges, (
        f"an event edge was NOT rebuilt from its recorded join: "
        f"{sorted(live_echo_edges - rebuilt_edges)}")


# =====================================================================
# (i) THE ARBITER HOUSEKEEPING (res.7)
# =====================================================================

def test_i_the_examination_log_raises_typed_when_unreadable(tmp_path,
                                                            monkeypatch):
    """PIN (i) / res.7. The ordered housekeeping: Ruling 74 reported this latent
    shape against Ruling 73's file, and it is closed here."""
    from src.goals.goal_arbitration import (ExaminationLogUnreadable,
                                            GoalArbiter)
    from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                       GoalProvenance)

    ledger = GoalLedger(ledger_path=str(tmp_path / "goals.jsonl"))
    for index in range(2):
        ledger.commit(desired_state=f"d{index}", kind=GoalKind.RESEARCH,
                      level=GoalLevel.PROJECT,
                      provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                      asserter="tester")
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "exams.jsonl"))
    arbiter.examine()

    target = str(arbiter.log_path)
    real_open = builtins.open

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == target and "r" in mode:
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    for call in (lambda: arbiter.examinations(),
                 lambda: arbiter.focus_persistence("GLC-0001"),
                 lambda: arbiter.select(),
                 lambda: arbiter.examine()):
        with pytest.raises(ExaminationLogUnreadable):
            call()


def test_i_selection_happens_inside_the_mint_lock():
    """PIN (i) / res.7. **DECLARED STRUCTURAL PER RULING 17.**

    `select()` used to run OUTSIDE the hold, so two concurrent `examine()` calls
    could each compute a selection before either appended - and both would
    select the SAME goal. Reported as an observation at Ruling 74; closed here.

    The property IS a lexical scope, so source is where it is true or false; a
    threaded probe would be flaky and could pass by luck.
    """
    examine = next(n for n in ast.walk(_tree("src/goals/goal_arbitration.py"))
                   if isinstance(n, ast.FunctionDef) and n.name == "examine")
    guarded = [w for w in ast.walk(examine) if isinstance(w, ast.With)
               and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id == "mint_lock"
                       for item in w.items
                       for c in ast.walk(item.context_expr))]
    assert guarded, "`examine` does not take the mint lock at all"

    inside = {n.func.attr for n in ast.walk(guarded[0])
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    for verb in ("select", "_next_id", "_append"):
        assert verb in inside, (
            f"`{verb}` happens outside the hold - derive through append must "
            f"be one hold (Ruling 69's discipline)")


def test_i_select_is_still_pure_and_publicly_callable(tmp_path):
    """PIN (i) / res.7. What moved is WHERE `examine` calls it, not what it
    does - `select()` writes nothing and stays callable on its own."""
    from src.goals.goal_arbitration import GoalArbiter
    from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                       GoalProvenance)

    ledger = GoalLedger(ledger_path=str(tmp_path / "goals.jsonl"))
    ledger.commit(desired_state="d", kind=GoalKind.RESEARCH,
                  level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="tester")
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "exams.jsonl"))

    assert arbiter.select() is not None
    assert not Path(arbiter.log_path).exists(), "`select` wrote something"


# =====================================================================
# (j) ISOLATION, AND THE COUNT-AS-DERIVATION INSTRUMENT
# =====================================================================

def test_j_the_echo_store_is_registered_in_both_isolation_tables():
    """PIN (j). EchoMemory was ALREADY redirect-capable in both tables (Ruling
    31/32 shape), so this ruling adds no path - but the core now CONSTRUCTS one,
    which is what makes the existing redirect load-bearing."""
    for rel in ("tests/conftest.py", "scripts/soak.py"):
        source = (REPO / rel).read_text(encoding="utf-8")
        assert "EchoMemory" in source
        assert "echoes.jsonl" in source


def test_j_a_default_constructed_core_keeps_its_echo_store_isolated():
    """PIN (j), the BEHAVIORAL half. The autouse fixture is active here, so a
    core's echo store must not resolve under the repo's `data/runtime/`."""
    core = AureaCore()
    resolved = str(Path(core.echo_memory.runtime_path).resolve())
    assert str((REPO / "data" / "runtime").resolve()) not in resolved, (
        f"the echo store escaped isolation: {resolved}")


def test_j_the_conftest_path_count_is_a_derivation_not_a_claim():
    """PIN (j). **THE COUNT-AS-DERIVATION INSTRUMENT** - the registered smallest
    carried item, taken here because this pass touches `conftest.py`.

    The docstring states a COUNT because Ruling 34 replaced a completeness
    BOAST with one, on the reasoning that *"a count goes visibly stale and a
    boast does not"*. It DID go visibly stale - Ruling 74 found it reading
    TWENTY-TWO against a tree carrying TWENTY-FOUR, two passes behind.

    **WHAT THE DESIGN COULD NOT DO WAS MAKE ANYONE LOOK.** This assertion makes
    the count a DERIVATION: it is now checked against the tables on every run,
    so it cannot silently drift again. One assertion, and it closes the class.
    """
    source = (REPO / "tests/conftest.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    # CLASS-ATTRIBUTE REDIRECTS: `monkeypatch.setattr` calls, EXCLUDING the one
    # inside `_redirect_default`. That call is the MECHANISM which applies each
    # `__init__` default, not a path of its own - counting it would inflate the
    # total by exactly one and make this derivation disagree with the docstring
    # forever. (The first draft did count it, and said 26.)
    helper = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef)
                   and n.name == "_redirect_default"), None)
    inside_helper = {id(n) for n in ast.walk(helper)} if helper else set()
    class_attrs = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and id(n) not in inside_helper
        and getattr(n.func, "attr", None) == "setattr"
        and getattr(getattr(n.func, "value", None), "id", None) == "monkeypatch")
    init_defaults = max(
        (len(n.iter.elts) for n in ast.walk(tree)
         if isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)),
        default=0)
    actual = class_attrs + init_defaults

    # THE LIVE CLAIM ONLY. Ruling 74 corrected this count and KEPT the old text
    # struck (`~~...~~`) as the record, so a scan that takes the first match
    # reads the SUPERSEDED number - which is what the first draft of this pin
    # did, reporting 22 against a docstring that says 25. Struck lines are
    # history and must not be measured.
    live = "\n".join(line for line in source.splitlines()
                     if "~~" not in line)
    words = {"TWENTY-TWO": 22, "TWENTY-THREE": 23, "TWENTY-FOUR": 24,
             "TWENTY-FIVE": 25, "TWENTY-SIX": 26, "TWENTY-SEVEN": 27,
             "TWENTY-EIGHT": 28, "TWENTY-NINE": 29, "THIRTY": 30,
             # M7-b (2026-08-16): the vocabulary needed the next word, and the
             # ruled form is what forced the docstring edit rather than letting
             # the count drift. `THIRTY` cannot shadow `THIRTY-ONE` here - the
             # match requires ` PATHS` immediately after the word.
             "THIRTY-ONE": 31, "THIRTY-TWO": 32,
             "THIRTY-THREE": 33}
    claimed = [value for word, value in words.items()
               if f"THIS FIXTURE COVERS {word} PATHS" in live]
    assert len(claimed) == 1, (
        f"conftest.py must state its coverage count exactly once in the ruled "
        f"form; found {claimed}. The derivation has nothing to check.")
    assert claimed[0] == actual, (
        f"conftest.py's docstring claims {claimed[0]} paths; the tables hold "
        f"{actual} ({class_attrs} class attributes + {init_defaults} __init__ "
        f"defaults). The count went stale again - update the docstring.")


# =====================================================================
# (k) CENSUS AND ABSENCE REGRESSION
# =====================================================================

def test_k_this_ruling_added_no_enum_member():
    """PIN (k) / res.8. **COINS: the `ECH-` prefix and the typed error names.**
    No enum, no threshold, no score - so the census is a REGRESSION check
    rather than a precondition."""
    found = {}
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.ClassDef):
                continue
            if not any("Enum" in ast.unparse(b) for b in node.bases):
                continue
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            found.setdefault(target.id, []).append(
                                f"{path.relative_to(REPO).as_posix()}:{node.name}")
    assert len(found) > 100, f"census implausibly small: {len(found)}"
    # The echo store defines NO enum at all.
    assert not any("echo_memory.py" in owner
                   for owners in found.values() for owner in owners)


def test_k_the_store_carries_no_threshold_and_no_scalar_standing():
    """PIN (k) / res.8. Nothing numeric is coined here."""
    module_numbers = [t.id for n in ast.walk(_tree())
                      if isinstance(n, ast.Assign)
                      for t in n.targets
                      if isinstance(t, ast.Name) and t.id.isupper()
                      and isinstance(n.value, ast.Constant)
                      and isinstance(n.value.value, (int, float))]
    assert module_numbers == [], f"module-level magnitudes: {module_numbers}"

    for node in ast.walk(_tree()):
        if isinstance(node, ast.Compare):
            operands = [node.left] + list(node.comparators)
            offenders = [o.value for o in operands
                         if isinstance(o, ast.Constant)
                         and isinstance(o.value, (int, float))
                         and not isinstance(o.value, bool)]
            assert offenders == [], (
                f"a numeric literal is compared at line {node.lineno}: "
                f"`{ast.unparse(node)}`")


def test_k_no_retrieval_surface_was_added():
    """PIN (k). **DECLARED OUT, and the absence is pinned**: retrieval and any
    echo-content query surface belong to the scar/retrieval enrichment ruling,
    NEXT after this one. `get_echo` and `list_echoes` are the two reads this
    store has always had; this ruling made them honest, it did not add a third.
    """
    public = {n.name for n in ast.walk(_tree())
              if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")}
    assert public == {"record", "read_all", "get_echo", "list_echoes"}, (
        f"the store's public surface changed: {sorted(public)}")
    for word in ("search", "query", "find_", "similar", "recall", "match"):
        assert not any(word in name for name in public), (
            f"a retrieval surface `{word}` appeared; it is the NEXT ruling's")
