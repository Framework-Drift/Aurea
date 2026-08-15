"""
test_m6_proposition_ledger.py - M6-α: THE WORLD MODEL's FIRST MEMBER.

    **A PROPOSITION CITING EVIDENCE THAT DOES NOT EXIST IS MANUFACTURING TRUTH
    AT ONE REMOVE.**

Grounds heading Phase 6 and the World Model domain paragraph. The domain row was
EMPTY before this pass; this is its first member.

RED-FIRST is a COLLECTION ERROR and is stated as one (Rulings 61/63/70's
precedent): `src/worldmodel/` does not exist at the parent, so every pin here
fails at collection there rather than on an assertion. Unlike M4-α there is no
independent half to witness - the store IS the pass - **so the mutation slate
carries this commit's verification weight**, and the pins below are written to
be forcing rather than merely present.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.doctrine.codex import Codex
from src.external.claim_ancestry import ClaimAncestryLedger, OriginDeclaration
from src.external.prediction_ledger import PredictionLedger, provided
from src.filtration.episode_record import EpisodeRecord
from src.filtration.obligation_ledger import ObligationLedger, TargetKind
from src.filtration.scar_logic_core import ScarLogicCore
from src.worldmodel.proposition_ledger import (KernelRef, KernelRefKind,
                                               PropositionKind,
                                               PropositionLedger,
                                               PropositionLedgerUnreadable,
                                               PropositionRecord,
                                               PropositionSummary,
                                               PropositionView,
                                               UnresolvedReference,
                                               UnverifiableReference)

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
MODULE = SRC / "worldmodel" / "proposition_ledger.py"


def _tree(path: Path = MODULE) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _stub_standing(record: PropositionRecord) -> str:
    """A stand-in derivation for commit 1. M6-β owns the real vocabulary; this
    file's law is only that content never travels without SOMETHING beside it."""
    return "ungrounded" if record.ungrounded else "referenced"


def _kernel(tmp_path):
    """A live kernel with one real record in each store the ledger can cite."""
    claims = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    claim = claims.record(OriginDeclaration())

    scars = ScarLogicCore(runtime_path=str(tmp_path / "scars.json"))
    scar = scars.form_scar(origin="m6", type="structural", weight=1.0,
                           description="a wound the world may cite")

    codex = Codex(runtime_path=str(tmp_path / "doctrines.json"))
    doctrine = next(iter(codex.view()))

    obligations = ObligationLedger(ledger_path=str(tmp_path / "obl.jsonl"),
                                   ancestry_ledger=claims)
    admitted = obligations.admit(source="m6", target_kind=TargetKind.CLAIM,
                                 target_id=claim.claim_id, claim_text="owed")

    episodes = EpisodeRecord(log_path=str(tmp_path / "epi.jsonl"))
    episode = episodes.open_episode([admitted.obligation_id], 3)

    predictions = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    prediction = predictions.commit(expected_result="the bridge holds",
                                    success_criteria=provided("it stands"))

    ledger = PropositionLedger(
        ledger_path=str(tmp_path / "propositions.jsonl"),
        ancestry_ledger=claims, scar_core=scars, codex=codex,
        episode_record=episodes, obligation_ledger=obligations,
        prediction_ledger=predictions)

    return ledger, {
        KernelRefKind.CLAIM: claim.claim_id,
        KernelRefKind.SCAR: scar.id,
        KernelRefKind.DOCTRINE: doctrine,
        KernelRefKind.EPISODE: episode,
        KernelRefKind.OBLIGATION: admitted.obligation_id,
        KernelRefKind.PREDICTION: prediction.prediction_id,
    }


# =====================================================================
# (a) THE REFERENCE DISCIPLINE IS A WRITE LAW
# =====================================================================

@pytest.mark.parametrize("kind", list(KernelRefKind), ids=lambda k: k.value)
def test_a_every_kernel_kind_resolves_at_write(kind, tmp_path):
    """THE WRITE LAW, driven on ALL SIX stores against REAL records.

    Each id below was minted by its owner's own door in this test, so a passing
    row means the ledger checked a record that genuinely exists rather than a
    string that happened to look right.
    """
    ledger, ids = _kernel(tmp_path)
    record = ledger.record(
        PropositionKind.STATE, "the world is thus",
        supported_by=[KernelRef(kind=kind, record_id=ids[kind])])

    assert record.wmp_id == "WMP-0001"
    assert record.supported_by[0].record_id == ids[kind]
    assert not record.ungrounded


@pytest.mark.parametrize("kind", list(KernelRefKind), ids=lambda k: k.value)
def test_a_an_unrecorded_reference_is_refused_typed(kind, tmp_path):
    """**THE LOAD-BEARING PIN.** A proposition citing evidence that does not
    exist is manufacturing truth at one remove - refused, on every store.

    AND THE REFUSAL LEAVES NOTHING BEHIND: the pre-flight runs before the mint,
    so no ordinal is spent and no line is written (Ruling 24/46's boundary).
    """
    ledger, _ = _kernel(tmp_path)

    with pytest.raises(UnresolvedReference):
        ledger.record(PropositionKind.STATE, "an unsupported claim",
                      supported_by=[KernelRef(kind=kind,
                                              record_id="NOPE-9999")])

    assert ledger.summaries() == ()
    assert not Path(ledger.ledger_path).exists(), (
        "a refused proposition left a file behind - the pre-flight must run "
        "before the mint AND before the write")
    # ...and the ordinal is unspent: the next real write is still the first.
    assert ledger.record(PropositionKind.STATE, "ok").wmp_id == "WMP-0001"


def test_a_all_three_reference_fields_are_checked(tmp_path):
    """`contradicted_by` and `predicted_by` are not a softer class of citation."""
    ledger, ids = _kernel(tmp_path)
    for field in ("supported_by", "contradicted_by", "predicted_by"):
        with pytest.raises(UnresolvedReference):
            ledger.record(PropositionKind.STATE, "x",
                          **{field: [KernelRef(kind=KernelRefKind.CLAIM,
                                               record_id="CLM-9999")]})


def test_a_an_unverifiable_reference_is_a_DIFFERENT_refusal(tmp_path):
    """RULING 29's LAW: two causes, two types, neither a base class of the other.

    `UnresolvedReference` says the ledger LOOKED and the record is not there.
    `UnverifiableReference` says it COULD NOT LOOK. Collapsing them would be
    Ruling 25's defect one level down - and the second exists because a write
    law that can be skipped by simply not injecting a resolver is the
    "discouraged, not unexecutable" shape.
    """
    blind = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))

    with pytest.raises(UnverifiableReference):
        blind.record(PropositionKind.STATE, "x",
                     supported_by=[KernelRef(kind=KernelRefKind.SCAR,
                                             record_id="Scar-0")])

    assert not issubclass(UnverifiableReference, UnresolvedReference)
    assert not issubclass(UnresolvedReference, UnverifiableReference)


def test_a_a_fossil_doctrine_resolves(tmp_path):
    """M3-A's fossil-resolves rule: a proposition may legitimately cite a
    doctrine that has FALLEN, and refusing it would make the world model unable
    to reference her own history."""
    ledger, _ = _kernel(tmp_path)
    fossils = ledger.codex.fossils
    assert fossils, "the seed carries a founding fossil (Ruling 35)"
    fossil_id = next(iter(fossils))
    assert ledger.codex.get(fossil_id) is None, "it is not live"

    record = ledger.record(
        PropositionKind.EVENT, "the ground fell",
        supported_by=[KernelRef(kind=KernelRefKind.DOCTRINE,
                                record_id=fossil_id)])
    assert record.supported_by[0].record_id == fossil_id


def test_a_ungrounded_admits_and_is_recorded(tmp_path):
    """UNGROUNDED IS A REAL STATE. Refusing it would push callers to fabricate
    references to get a write through - L3's fabrication class at the write
    door, and the ABSENT-is-a-real-answer law applied one domain over."""
    ledger, _ = _kernel(tmp_path)
    record = ledger.record(PropositionKind.UNKNOWN, "something is happening")

    assert record.ungrounded is True
    assert record.references == ()
    assert len(ledger.summaries()) == 1


def test_a_references_are_typed_pairs_not_bare_ids(tmp_path):
    """A bare id would have to be resolved by TRYING every store until one hit -
    guessing, and ambiguous for an id living in two. Scars are `Δ17`/`Scar-0`
    and doctrines are `Doctrine-0`/`AVT.001`; no prefix grammar separates them."""
    ledger, ids = _kernel(tmp_path)
    with pytest.raises(TypeError):
        ledger.record(PropositionKind.STATE, "x",
                      supported_by=[ids[KernelRefKind.CLAIM]])
    with pytest.raises(TypeError):
        KernelRef(kind="claim", record_id="CLM-0001")
    with pytest.raises(TypeError):
        KernelRef(kind=KernelRefKind.CLAIM, record_id="")


# =====================================================================
# (b) CONTENT NEVER TRAVELS WITHOUT STANDING - R64's LAW AS SCHEMA
# =====================================================================

def test_b_no_public_reader_returns_content_without_standing():
    """**R64's LAW MADE UNBUILDABLE.** AST over the ledger's public surface.

    An unlabeled content slot let a FALSIFIED prediction's refuted expectation
    read as standing knowledge with a tier vouching for it. Here, every public
    door that can carry `asserted_content` REQUIRES a `derive` callable, so
    there is no way to ask this store for content and not be handed the standing
    beside it.
    """
    cls = next(n for n in ast.walk(_tree())
               if isinstance(n, ast.ClassDef) and n.name == "PropositionLedger")
    public = [f for f in cls.body
              if isinstance(f, ast.FunctionDef) and not f.name.startswith("_")]
    assert public, "the scanner found no public methods - it is measuring nothing"

    content_carriers = {"propositions", "live", "get"}
    for fn in public:
        args = {a.arg for a in fn.args.args}
        if fn.name in content_carriers:
            assert "derive" in args, (
                f"`{fn.name}` can return content and does not require a "
                f"derivation - R64's reversed-meaning defect is buildable again")
        elif fn.name not in {"record"}:
            # Every other public read must be content-free by RETURN TYPE.
            returns = ast.unparse(fn.returns) if fn.returns else ""
            assert "PropositionRecord" not in returns and "View" not in returns, (
                f"`{fn.name}` returns a content-carrying shape without standing")


def test_b_the_content_carrying_doors_hand_back_both(tmp_path):
    """Behaviourally, not just structurally."""
    ledger, _ = _kernel(tmp_path)
    ledger.record(PropositionKind.STATE, "the bridge stands")

    for view in ledger.propositions(_stub_standing):
        assert isinstance(view, PropositionView)
        assert view.asserted_content == "the bridge stands"
        assert view.standing is not None
    assert ledger.get("WMP-0001", _stub_standing).standing == "ungrounded"


def test_b_the_content_doors_cannot_be_called_without_a_derivation(tmp_path):
    """`derive` has NO DEFAULT, and that absence IS the enforcement."""
    ledger, _ = _kernel(tmp_path)
    ledger.record(PropositionKind.STATE, "x")
    for door in (ledger.propositions, ledger.live):
        with pytest.raises(TypeError):
            door()


def test_b_the_summary_surface_carries_no_content_at_all(tmp_path):
    """**ENFORCEMENT BY SCOPE** (Ruling 33's move), and it is what makes M6-γ's
    record-honest floor structural rather than a promise.

    The contradiction surface reads THIS shape. Because it has no
    `asserted_content`, that surface is STRUCTURALLY INCAPABLE of inferring a
    semantic contradiction from text - v1's limitation is not something anyone
    must remember to respect, it is the only thing the surface can see.
    """
    assert not hasattr(PropositionSummary, "asserted_content")
    fields = {f.name for f in PropositionSummary.__dataclass_fields__.values()}
    assert "asserted_content" not in fields
    assert fields == {"wmp_id", "kind", "supported_by", "contradicted_by",
                      "predicted_by", "supersedes"}

    ledger, _ = _kernel(tmp_path)
    ledger.record(PropositionKind.STATE, "a secret the surface cannot read")
    summary = ledger.summaries()[0]
    assert not hasattr(summary, "asserted_content")
    assert "secret" not in json.dumps(summary.__dict__, default=str)


def test_b_no_standing_value_is_ever_written_to_the_store(tmp_path):
    """What is STORED is references; what is READ is standing. The gap between
    them is where the honesty lives (M6-β), so a standing on disk would be the
    stale authority the whole design refuses."""
    ledger, ids = _kernel(tmp_path)
    ledger.record(PropositionKind.STATE, "x",
                  supported_by=[KernelRef(kind=KernelRefKind.CLAIM,
                                          record_id=ids[KernelRefKind.CLAIM])])

    entry = json.loads(Path(ledger.ledger_path).read_text(encoding="utf-8"))
    for banned in ("standing", "score", "weight", "confidence", "tier",
                   "strength"):
        assert banned not in entry, f"a derived standing reached the store: {banned}"


# =====================================================================
# (c) SUPERSESSION, AND THE LIVE SET AS A DERIVATION
# =====================================================================

def test_c_a_successor_supersedes_and_the_live_set_is_a_fold(tmp_path):
    ledger, _ = _kernel(tmp_path)
    first = ledger.record(PropositionKind.STATE, "the bridge stands")
    second = ledger.record(PropositionKind.STATE, "the bridge is closed",
                           supersedes=first.wmp_id)

    live = [s.wmp_id for s in ledger.live_summaries()]
    assert live == [second.wmp_id]
    assert len(ledger.summaries()) == 2, "the superseded record is NOT erased"


def test_c_superseding_an_unrecorded_proposition_is_refused(tmp_path):
    ledger, _ = _kernel(tmp_path)
    with pytest.raises(UnresolvedReference):
        ledger.record(PropositionKind.STATE, "x", supersedes="WMP-9999")


def test_c_the_live_set_is_never_stored(tmp_path):
    """L3, and Rulings 63/65's refusal of a stored derivation, at the field
    where a 'current world snapshot' would be most tempting and most wrong."""
    ledger, _ = _kernel(tmp_path)
    ledger.record(PropositionKind.STATE, "a")
    text = Path(ledger.ledger_path).read_text(encoding="utf-8")
    for banned in ("live", "current_world", "snapshot", "is_live"):
        assert f'"{banned}"' not in text

    source = MODULE.read_text(encoding="utf-8")
    assert "self.live" not in source and "self._live" not in source


# =====================================================================
# (d) THE STORE DISCIPLINE
# =====================================================================

def test_d_there_is_no_delete_or_update_family():
    """M3-A's rule verbatim: a method named `amend` with a docstring saying
    "only for corrections" is a request for restraint, and this project has
    hard evidence restraint fails."""
    banned = {"delete", "remove", "clear", "purge", "truncate", "update",
              "amend", "revise", "edit", "rewrite", "drop", "retract"}
    offenders = [n.name for n in ast.walk(_tree())
                 if isinstance(n, ast.FunctionDef)
                 and any(n.name.lstrip("_").startswith(b) for b in banned)]
    assert offenders == [], (
        f"the proposition ledger defines {offenders}. A proposition updates by "
        f"SUPERSESSION - a successor record - never by mutation.")


def test_d_the_only_write_is_the_funnel():
    calls = {n.func.id for n in ast.walk(_tree())
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "durable_append_text" in calls
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "open":
            modes = [a.value for a in node.args[1:] if isinstance(a, ast.Constant)]
            assert modes == ["r"], f"a non-read open at line {node.lineno}"


def test_d_the_wall_clock_is_recorded_and_never_read():
    """M3-A's discipline. Ordering is by ordinal, always."""
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            reads = ([node.left] + list(node.comparators)
                     if isinstance(node, ast.Compare)
                     else [node.test] if isinstance(node, ast.If) else [])
            for read in reads:
                for inner in ast.walk(read):
                    if (isinstance(inner, ast.Attribute)
                            and inner.attr == "recorded_wall"):
                        offenders.append(
                            f"{path.relative_to(REPO).as_posix()}:{inner.lineno}")
    assert offenders == [], f"`recorded_wall` is READ at {offenders}"


def test_d_the_interval_fields_are_event_time_not_wall_clock(tmp_path):
    """They name RECORDED ORDINALS, and the ledger records them as declared.

    Resolving them is a FUTURE RULING (they may name several ordinal spaces),
    and that is stated rather than silently skipped - but nothing may quietly
    fill them from a clock.
    """
    ledger, _ = _kernel(tmp_path)
    record = ledger.record(PropositionKind.TEMPORAL_INTERVAL, "it rained",
                           interval_start="ACQ-0001", interval_end="ACQ-0009")
    assert record.interval_start == "ACQ-0001"

    fn = next(n for n in ast.walk(_tree())
              if isinstance(n, ast.FunctionDef) and n.name == "record")
    for node in ast.walk(fn):
        if isinstance(node, ast.keyword) and node.arg in {"interval_start",
                                                          "interval_end"}:
            assert "now" not in ast.unparse(node.value), (
                "an interval field was filled from a clock")


def test_d_an_unknown_kind_drops_the_line_and_is_never_coerced(tmp_path):
    """Floor semantics. A forensic log outlives the code that wrote it, and
    reading an unknown proposition kind as a known one would put a fact in the
    reader's hands the writer never recorded."""
    path = tmp_path / "p.jsonl"
    good = {"wmp_id": "WMP-0001", "kind": "state", "asserted_content": "a",
            "supported_by": [], "contradicted_by": [], "predicted_by": [],
            "supersedes": None, "interval_start": None, "interval_end": None,
            "recorded_wall": ""}
    future = dict(good, wmp_id="WMP-0002", kind="quantum_superposition")
    path.write_text(json.dumps(good) + "\n" + json.dumps(future) + "\n",
                    encoding="utf-8")

    ledger = PropositionLedger(ledger_path=str(path))
    assert [s.wmp_id for s in ledger.summaries()] == ["WMP-0001"]
    # ...but the dropped line's ordinal is STILL SEEN by the mint (Ruling 69).
    assert ledger.record(PropositionKind.STATE, "next").wmp_id == "WMP-0003"


def test_d_an_unreadable_ledger_refuses_the_mint(tmp_path, monkeypatch):
    """Ruling 53's sentinel: NEVER falls back to a number. Propositions
    supersede each other BY ID, so a collision would make the world's own
    history unreadable."""
    import builtins
    ledger = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    ledger.record(PropositionKind.STATE, "first")

    real_open = builtins.open

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == str(ledger.ledger_path) and "r" in str(mode):
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    with pytest.raises(PropositionLedgerUnreadable):
        ledger.record(PropositionKind.STATE, "second")


def test_d_the_kind_vocabulary_is_the_headings_own_nine():
    """RECOVERED, not invented - and CLOSED. Widened only by manifest entry."""
    assert [k.name for k in PropositionKind] == [
        "ENTITY", "EVENT", "STATE", "RELATION", "CAUSAL_HYPOTHESIS",
        "CONSTRAINT", "UNKNOWN", "CONTRADICTION", "TEMPORAL_INTERVAL"]
    assert {k.name for k in KernelRefKind} == {
        "CLAIM", "SCAR", "DOCTRINE", "EPISODE", "OBLIGATION", "PREDICTION"}


def test_d_a_raw_string_kind_is_refused(tmp_path):
    ledger, _ = _kernel(tmp_path)
    with pytest.raises(TypeError):
        ledger.record("state", "x")


# =====================================================================
# (e) THE RESOLVERS ARE READS, AND THE WRITERS ARE NOBODY
# =====================================================================

def test_e_the_ledger_names_no_mutating_verb_on_a_resolver():
    """THE CENSUS, STANDING RATHER THAN ONE-TIME.

    M3-A's finding is the reason this pin exists: `retrieve` is NOT a read on
    any of the three suspension systems - it stamps the entry and calls
    `save_to_file()`. All six read surfaces this ledger uses were censused as
    READ-ONLY before wiring, and this keeps them that way.
    """
    banned = {"retrieve", "suspend", "save_to_file", "save", "commit", "record",
              "form_scar", "admit", "open_episode", "resolve", "mutate_doctrine"}
    offenders = []
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in banned):
            # `self.record(...)` is this ledger's OWN write door, not a resolver.
            target = ast.unparse(node.func.value)
            if target.startswith("self.") or target == "self":
                if node.func.attr == "record" and target != "self":
                    offenders.append(f"{target}.{node.func.attr}:{node.lineno}")
                continue
            offenders.append(f"{target}.{node.func.attr}:{node.lineno}")
    assert offenders == [], (
        f"the ledger calls a mutating verb on a resolver: {offenders}")


def test_e_reading_a_reference_leaves_every_kernel_store_byte_identical(tmp_path):
    """**MEASURED, NOT ASSERTED.** The write law reads six stores on every
    proposition; if any of those reads wrote, the world model would be mutating
    the kernel it exists to defer to."""
    ledger, ids = _kernel(tmp_path)
    others = sorted(p for p in tmp_path.iterdir()
                    if p.is_file() and p.name != "propositions.jsonl")
    before = {p.name: p.read_bytes() for p in others}

    for kind, record_id in ids.items():
        ledger.record(PropositionKind.STATE, f"about {kind.value}",
                      supported_by=[KernelRef(kind=kind, record_id=record_id)])

    after = {p.name: p.read_bytes() for p in others}
    assert after == before, (
        f"a resolver WROTE: {sorted(k for k in before if before[k] != after[k])}")


def test_e_nothing_in_src_writes_a_proposition():
    """Ruling 72's no-consumer form. The Executive wires proposition-writing at
    M7; this goes RED the day something does, which is when it needs its ruling."""
    writers = []
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        if rel.endswith("worldmodel/proposition_ledger.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and "proposition_ledger" in (
                    node.module or ""):
                writers.append(f"{rel}:{node.lineno}")
    assert writers == [], (
        f"the proposition ledger acquired a `src/` consumer: {writers}")


def test_e_the_store_is_registered_in_both_isolation_tables():
    """Ruling 31's standing rule, in the SAME commit as the store."""
    from scripts.soak import _injection_table
    _, init_defaults = _injection_table()
    assert any(cls is PropositionLedger and param == "ledger_path"
               for cls, param, _ in init_defaults)

    conftest = (REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert '(PropositionLedger, "ledger_path"' in conftest

    init = next(n for n in ast.walk(_tree())
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    default = init.args.defaults[0]
    assert isinstance(default, ast.Constant)
    assert default.value.startswith("data/runtime/")


def test_e_no_resolver_handle_is_named_after_a_canonical_store():
    """**AN INVARIANT FIRED ON THIS FILE'S FIRST RUN AND IT WAS RIGHT.**

    The first draft named its resolver handles `claims` / `scars` / `episodes` /
    `obligations` / `predictions`, and `self.scars = scars` tripped Ruling 1's
    single-writer scanner, which flags `<anything>.scars = ...` outside
    `scar_logic_core.py`. CLAUDE.md section 2 rules the remedy in terms: **the
    fix is the NAME, not the test.**

    Pinned so the collision cannot come back by a later rename.
    """
    from tests.invariants.test_ruling1_single_writer import STORE_OWNERS

    init = next(n for n in ast.walk(_tree())
                if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    assigned = {t.attr for node in ast.walk(init)
                if isinstance(node, ast.Assign)
                for t in node.targets
                if isinstance(t, ast.Attribute)}
    collisions = assigned & set(STORE_OWNERS)
    assert collisions == set(), (
        f"a handle is named after a canonical store: {sorted(collisions)}. "
        f"Ruling 1's scanner flags every foreign write to those names.")
