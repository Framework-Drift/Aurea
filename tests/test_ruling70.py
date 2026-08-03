"""
test_ruling70.py - THE MODEL-INGRESS ADAPTER (Ruling 70 / Docket O item O6).

Manifest thirty-seventh addendum, 2026-08-02. The docket's last item.

    A model is a SOURCE, not a SENSOR OF TRUTH. What it says is recorded as a
    claim, and a claim answers to collapse like any other claim.

THE RED-FIRST WATCH IS A COLLECTION ERROR, AND IT IS STATED RATHER THAN DRESSED
UP. `src/external/model_provider.py` did not exist at `41ba792`, so every pin
below that imports it fails at COLLECTION there rather than on an assertion -
the same honest situation Rulings 61 and 63 recorded for their own new modules.
Unlike Ruling 60, there is no independent half to witness: the adapter IS the
pass. **THE MUTATION SLATE THEREFORE CARRIES THIS PASS'S VERIFICATION WEIGHT**,
and the pins are written to be forcing rather than merely present.

TWO PINS DO WITNESS SOMETHING AT BASELINE AND ARE MARKED WHERE THEY SIT:
`_claim_tier`'s MODEL_PREDICTION -> PREDICTED derivation and Ruling 60's
"independent"-free vocabulary both PREDATE this ruling. Ruling 70 res.3
converts the first from an assertion into a pin NOW THAT A PRODUCER EXISTS, so
the pin drives it THROUGH the adapter; asserting the derivation directly would
pass for Ruling 63's reason and witness nothing about this one.

COINS NOTHING: no enum member (`MODEL_PREDICTION` has been in O1's closed set
since Ruling 58), no threshold, no score, no magnitude.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.external import source_genealogy as sg
from src.external.claim_ancestry import (ANCESTRY_FIELDS, ClaimAncestryLedger,
                                         FieldState, OriginDeclaration,
                                         OriginKind, declared_none, provided)
from src.external.model_provider import (CALLER_DECLARABLE_FIELDS,
                                         ingest_model_assertion,
                                         model_declaration)
from src.external.prediction_ledger import PredictionLedger
from src.external.record_projection import KnowledgeTier, project

MODULE = Path("src/external/model_provider.py")

IDENTITY = "openai/gpt-9/2026-01-15"
OTHER_IDENTITY = "anthropic/claude-5/2026-05-02"


def _tree() -> ast.Module:
    return ast.parse(MODULE.read_text(encoding="utf-8"))


def _ledger(tmp_path, name="claim_ancestry.jsonl") -> ClaimAncestryLedger:
    return ClaimAncestryLedger(ledger_path=str(tmp_path / name))


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


class _Spy:
    """A `process_input`-shaped collaborator that records what it was handed.

    PIN (h)'s injection, and it is what makes (f) and (g) answerable: the
    verbatim text and the never-called property are facts about what CROSSED
    THE BOUNDARY, and re-deriving them from downstream state would measure
    SPL's strip instead of the adapter's fidelity.
    """

    def __init__(self, ledger=None):
        self.calls = []
        self._ledger = ledger

    def __call__(self, raw_input, *, origin=None):
        claim_id = None
        if self._ledger is not None:
            claim_id = self._ledger.record(origin).claim_id
        self.calls.append({"raw_input": raw_input, "origin": origin,
                           "claim_id": claim_id})
        return {"claim_id": claim_id, "spy": True}


# =====================================================================
# (a) DECLARATION COMPLETENESS
# =====================================================================

def test_a_model_assertion_records_model_prediction_with_every_field(tmp_path):
    """PIN (a), THE FORCING PIN. **RED FIRST** (collection) at `41ba792`.

    Read back FROM THE LEDGER, not from the object handed in: the record is the
    claim this ruling makes, and an in-memory assertion would not witness that
    it survived serialization.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)

    ingest_model_assertion(spy, "The bridge will hold.", IDENTITY)

    entries = _lines(ledger)
    assert len(entries) == 1
    entry = entries[0]

    assert entry["origin_kind"] == "model_prediction", (
        "a model assertion is recorded as MODEL_PREDICTION - the member O1's "
        "closed enum has carried since Ruling 58 precisely so O6 would never "
        "reopen it")

    # EVERY O1 FIELD POPULATED means every field carries an EXPLICIT RECORDED
    # STATE - not that every field carries a value. ABSENT is a real answer.
    for name in ANCESTRY_FIELDS:
        assert entry[name]["state"] in {s.value for s in FieldState}, (
            f"{name} carries no recorded state")

    assert entry["asserted_by"] == {"state": "provided", "value": IDENTITY}, (
        "the declared model identity is recorded BYTE-IDENTICAL - never "
        "verified, never normalized, never parsed into parts")


def test_a_the_asserter_is_byte_identical_including_odd_shapes(tmp_path):
    """PIN (a), second half. Recorded AS DECLARED - L1's own move.

    An identity with whitespace, casing and punctuation the adapter might have
    been tempted to tidy. A normalized identity is a DIFFERENT declaration, and
    this module cannot verify identities so it must not appear to have.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    weird = "  OpenAI / GPT-9 :: build 2026-01-15  \tsnapshot  "

    ingest_model_assertion(spy, "A claim.", weird)

    assert _lines(ledger)[0]["asserted_by"]["value"] == weird


def test_a_caller_declared_surfaces_reach_the_record(tmp_path):
    """PIN (a), third half: the four declarable surfaces are carried through.

    Ruling 58's three states, all of them reachable through this adapter -
    otherwise "every field populated" would mean "every field ABSENT", and a
    caller who KNOWS the descent would have no way to record it.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)

    ingest_model_assertion(
        spy, "A claim.", IDENTITY,
        basis=provided({"kind": "retrieval", "corpus": "internal"}),
        replication_refs=provided(["run-1", "run-2"]),
        connecting_assumptions=declared_none(),
        defeaters=provided(["contradicted by CLM-0001"]),
    )

    entry = _lines(ledger)[0]
    assert entry["basis"] == {"state": "provided",
                             "value": {"kind": "retrieval",
                                       "corpus": "internal"}}
    assert entry["replication_refs"]["value"] == ["run-1", "run-2"]
    assert entry["connecting_assumptions"] == {"state": "declared_none",
                                               "value": None}
    assert entry["defeaters"]["value"] == ["contradicted by CLM-0001"]


def test_a_undeclared_surfaces_are_absent_not_invented(tmp_path):
    """PIN (a), the fabrication half - L3's class, at the surface it would
    most naturally re-enter.

    A model plainly HAS a basis in some sense. Manufacturing one because a
    field exists to hold it is exactly the defect Ruling 58 was written to
    close, one docket item later.
    """
    ledger = _ledger(tmp_path)
    ingest_model_assertion(_Spy(ledger), "A claim.", IDENTITY)

    entry = _lines(ledger)[0]
    for name in CALLER_DECLARABLE_FIELDS:
        assert entry[name] == {"state": "absent", "value": None}, (
            f"{name} was never declared and says so - a manufactured value "
            f"here is a fact stored because a field existed to hold it")


@pytest.mark.parametrize("bad", ["a string", 7, None.__class__, ["x"], {"k": 1}])
def test_a_a_bare_declared_surface_is_refused_naming_the_callers_parameter(bad):
    """PIN (a), the backstop - **ADDED AFTER A MUTATION SURVIVOR, and the
    disposition is recorded because the survivor was NOT a plain gap.**

    Deleting the adapter's `AncestryField` check survived every behavioral
    assertion in this file, and the reason is legitimate: `OriginDeclaration`
    OWNS this type contract and refuses a bare value itself, so nothing is
    perceived either way. The mutant is behaviourally equivalent.

    THE GUARD IS KEPT AS A BACKSTOP IN RULING 46'S SHAPE - that ruling kept
    `commit`'s fossil raise after `_preflight` duplicated it, and pinned it
    independently so the backstop is driven rather than assumed. Its distinct
    contribution here is Ruling 66's own sentence: **a refusal that cannot say
    where it refused is half a refusal.** The owner's message names its
    internal field (`OriginDeclaration.basis`); this one names the PARAMETER
    THE CALLER ACTUALLY TYPED (`basis`), which is the vocabulary a caller of
    this adapter is working in.

    So this pin is deliberately a MESSAGE pin. It is the only observable
    difference between the two guards, and asserting anything weaker would be
    asserting the owner's behaviour and calling it this module's.
    """
    with pytest.raises(TypeError) as excinfo:
        model_declaration(IDENTITY, basis=bad)

    message = str(excinfo.value)
    assert message.startswith("basis must be an AncestryField"), (
        "the adapter's own refusal must name the caller's parameter - a "
        "refusal that cannot say where it refused is half a refusal")
    assert "OriginDeclaration" not in message, (
        "this is the ADAPTER's guard, not the owner's, and the pin exists so "
        "the backstop is driven independently rather than satisfied by it")


def test_a_asserted_by_is_not_caller_declarable():
    """PIN (a), shape. `asserted_by` IS the model identity.

    A caller-supplied override would let a model assertion be filed under
    someone else's name - the impersonation direction of the same fabrication.
    """
    assert "asserted_by" not in CALLER_DECLARABLE_FIELDS
    assert set(CALLER_DECLARABLE_FIELDS) == set(ANCESTRY_FIELDS) - {"asserted_by"}

    import inspect
    params = inspect.signature(model_declaration).parameters
    assert "asserted_by" not in params
    assert "origin_kind" not in params and "kind" not in params, (
        "the origin kind is MODEL_PREDICTION by construction - a caller who "
        "could choose it could file a model assertion as HUMAN")


def test_a_the_declaration_names_model_prediction_by_construction():
    """PIN (a), the kind is not a parameter and not a default that can drift."""
    declaration = model_declaration(IDENTITY)
    assert isinstance(declaration, OriginDeclaration)
    assert declaration.kind is OriginKind.MODEL_PREDICTION
    assert declaration.asserted_by.state is FieldState.PROVIDED
    assert declaration.asserted_by.value == IDENTITY


# =====================================================================
# (b) NO BYPASS - AST HALF
# =====================================================================

FORBIDDEN_IMPORT_ROOTS = {
    # The truth-content path. BAR §1's own list: a model's output may not
    # render a verdict, weight a net, write a doctrine or move the map.
    "echonet", "codex", "tca_core", "tcaml", "sae", "dee", "cae",
    "scar_logic_core", "racm", "reflex_grid", "ore", "hail", "nova",
    # res.5 - the adapter must not auto-commit a prediction.
    "prediction_ledger",
    # res.2 - the model never initiates.
    "urllib", "requests", "socket", "http", "aiohttp", "httpx", "asyncio",
    "subprocess", "ssl",
}


def _code_identifiers() -> set:
    """Every identifier the adapter's CODE names - never its prose.

    AST, NOT SUBSTRING, AND THE CONVERSION IS THE HOUSE'S OWN RULED REMEDY.
    Written lexically, all three scans below failed on this module's
    DOCSTRINGS, which legitimately explain why the adapter does NOT take an
    `AureaCore`, does NOT name a tier, and why Ruling 60's counter never says
    "independent". That is the substring-scanner false positive this project
    has now recorded five times, and its precedent is settled: Ruling 63's pass
    converted two pins from SUBSTRING to AST IMPORT rather than edit the prose,
    because **deleting correct documentation to satisfy a noisy guard is how a
    guard earns its eventual weakening.**

    THE ASSERTIONS ARE UNCHANGED - what moved is what counts as naming
    something. Docstrings and comments are excluded; imports, `Name` ids and
    attribute names are not.
    """
    names = set(_imported_roots())
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _imported_roots() -> set:
    roots = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.update(node.module.split("."))
            for alias in node.names:
                roots.add(alias.name)
    return roots


def test_b_the_adapter_imports_nothing_from_the_truth_content_path():
    """PIN (b), AST half. **THE GATE THIS MODULE STANDS ON.**

    BAR §1 cleared for O6 because the model sits on the CLAIM side of the
    arbitration boundary. An import of the verdict, doctrine, scar or topology
    layer here would retroactively fail that gate - so it is unwritable rather
    than discouraged.
    """
    offenders = sorted(_imported_roots() & FORBIDDEN_IMPORT_ROOTS)
    assert offenders == [], (
        f"the adapter imports {offenders}. A model's output enters as a CLAIM "
        f"and answers to collapse like any other; anything that lets it "
        f"influence a verdict other than by being a claim among claims fails "
        f"the BAR §1 gate Ruling 70 stands on.")


def test_b_the_import_scanner_actually_fires():
    """Ruling 32's answer to the vacuous-pin problem.

    A scanner that has stopped scanning must fail HERE rather than pass
    quietly forever. Fed the forbidden shape and a benign control.
    """
    def roots_of(source):
        found = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.update(alias.name.split("."))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    found.update(node.module.split("."))
                for alias in node.names:
                    found.add(alias.name)
        return found

    forbidden = "import requests\nfrom src.doctrine.codex import Codex\n"
    benign = ("from src.external.claim_ancestry import OriginDeclaration\n"
              "from typing import Optional\n")
    assert roots_of(forbidden) & FORBIDDEN_IMPORT_ROOTS
    assert not (roots_of(benign) & FORBIDDEN_IMPORT_ROOTS)


def test_b_the_identifier_scanner_actually_fires():
    """Ruling 32's answer to the vacuous-pin problem, for the AST scanner that
    THREE pins below now depend on.

    The conversion from substring to AST made those pins quieter; this is what
    stops it having made them EMPTY. A scanner blind to real code must fail
    HERE, and the control proves it still ignores prose.
    """
    def named_in(source):
        found = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Name):
                found.add(node.id)
            elif isinstance(node, ast.Attribute):
                found.add(node.attr)
            elif isinstance(node, ast.arg):
                found.add(node.arg)
        return found

    violating = "core = AureaCore()\nt = KnowledgeTier.PREDICTED\n"
    assert "AureaCore" in named_in(violating)
    assert "KnowledgeTier" in named_in(violating)

    # THE CONTROL: the same tokens, in PROSE. A scanner that flags this one is
    # the substring scanner again, and would force correct documentation out.
    prose = '"""This adapter takes no AureaCore and names no KnowledgeTier."""\n'
    assert "AureaCore" not in named_in(prose)
    assert "KnowledgeTier" not in named_in(prose)


def test_b_the_adapter_holds_no_writer_and_no_path():
    """PIN (b), AST half continued: it owns no store, so it can pollute none.

    No `open`, no `json.dump`/`dumps`, no `atomic_write*`, no `Path` literal.
    This module is not in `STORE_OWNERS` and this is why that is honest rather
    than an omission.
    """
    offenders = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in {"open", "Path"}:
            offenders.append(f"{func.id}:{node.lineno}")
        if isinstance(func, ast.Name) and func.id.startswith("atomic_write"):
            offenders.append(f"{func.id}:{node.lineno}")
        if (isinstance(func, ast.Attribute) and func.attr in {"dump", "dumps",
                                                             "write", "mkdir",
                                                             "write_text"}):
            offenders.append(f"{func.attr}:{node.lineno}")
    assert offenders == [], (
        f"the adapter reaches a write surface at {offenders}. It is PURE "
        f"PLUMBING: it constructs a declaration and hands text to a callable.")


def test_b_the_adapter_holds_no_state():
    """PIN (b) meets res.4: NO TRUST MACHINERY, made structural.

    The module holds no mutable module-level state, so there is nothing for a
    per-model counter, score or weight to accumulate on. Refusing trust
    machinery is not a rule anyone must remember here - there is no surface to
    put it on.
    """
    mutable = []
    for node in _tree().body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            for target in targets:
                if isinstance(target, ast.Name) and isinstance(
                        node.value, (ast.Dict, ast.List, ast.Set)):
                    mutable.append(target.id)
    assert mutable == [], (
        f"module-level mutable state at {mutable} - a per-model tally would "
        f"live exactly there, and res.4 refuses trust machinery outright")

    assert not [n for n in _tree().body if isinstance(n, ast.ClassDef)], (
        "the adapter defines no class: a stateful adapter is where a trust "
        "score, a call count or a model weight would accumulate")


# =====================================================================
# (b) NO BYPASS - BEHAVIORAL HALF
# =====================================================================

def test_b_a_model_claim_produces_the_ordinary_pipeline_artifacts():
    """PIN (b), BEHAVIORAL. **THE XAIG LAW, WITNESSED.**

    External input enters the SAME collapse machinery, not a bypass: one CLM
    line, one echo, a verdict from the nets - exactly what a human assertion
    produces, through exactly the same method.
    """
    core = AureaCore()
    result = ingest_model_assertion(core.process_input,
                                    "Water is wet.", IDENTITY)

    assert result["claim_id"] == "CLM-0001"
    assert len(_lines(core.ancestry)) == 1, "one CLM line per perceived claim"
    assert result["echo"] is not None, "a model claim builds an ordinary echo"
    assert result["collapse_result"] is not None, (
        "the nets ran - a model assertion is filtered like any other claim")
    assert result["errors"] == []
    assert core.structural_violations == [], (
        "an ordinary model ingest fires none of AUREA's guards")


def test_b_one_to_one_holds_across_a_batch():
    """PIN (b): Ruling 68's one-to-one property extended to THIS caller.

    CLM lines written EQUALS echoes built. Ruling 68 made that property true
    rather than careful; a new ingress that broke it would have re-opened the
    orphan class from a second door.
    """
    core = AureaCore()
    texts = ["Water is wet.", "The sky is green.", "Honesty is pointless.",
             "Fracture Carried is false.", "Two plus two is four."]
    echoes = 0
    for index, text in enumerate(texts):
        result = ingest_model_assertion(core.process_input, text,
                                        f"provider/model-{index}")
        if result["echo"] is not None:
            echoes += 1

    assert len(_lines(core.ancestry)) == len(texts) == echoes, (
        "one ledger line per claim PERCEIVED - the adapter mints no line "
        "without an echo and builds no echo without a line")


def test_b_the_adapter_adds_nothing_to_the_result_and_removes_nothing():
    """PIN (b): the result is returned UNMODIFIED.

    A result this layer decorated would be a model-shaped surface on the far
    side of the arbitration boundary - the bypass arriving as an annotation
    rather than as a call.
    """
    sentinel = {"claim_id": "CLM-0009", "spy": True}

    def collaborator(raw_input, *, origin=None):
        return sentinel

    returned = ingest_model_assertion(collaborator, "A claim.", IDENTITY)
    assert returned is sentinel, (
        "the adapter returns exactly what the pipeline returned - same object, "
        "nothing added, nothing removed")


def test_b_the_adapter_calls_process_input_with_origin_keyword_only():
    """PIN (b): it routes through the EXISTING entry point, as ruled.

    `origin` is keyword-only on `process_input` (Ruling 58's shape). A
    positional pass would bind the declaration to nothing and is exactly the
    class of defect Ruling 68 found when `source` was deleted.
    """
    captured = {}

    def collaborator(raw_input, *, origin=None):
        captured["raw_input"] = raw_input
        captured["origin"] = origin
        return {}

    ingest_model_assertion(collaborator, "A claim.", IDENTITY)
    assert isinstance(captured["origin"], OriginDeclaration)
    assert captured["origin"].kind is OriginKind.MODEL_PREDICTION


# =====================================================================
# (c) TIER LANDING - res.3, converted from assertion to pin
# =====================================================================

def test_c_a_model_origin_record_projects_predicted(tmp_path):
    """PIN (c). **RED FIRST** (collection) at `41ba792` - and it is driven
    THROUGH THE PRODUCER on purpose.

    Ruling 63 pre-confirmed the landing needs no new machinery, so a pin that
    hand-built a MODEL_PREDICTION record and projected it would pass at
    baseline FOR RULING 63'S REASON and witness nothing about O6. What is new
    is that a producer exists; the pin therefore starts at the adapter.
    """
    ledger = _ledger(tmp_path)
    ingest_model_assertion(_Spy(ledger), "The bridge will hold.", IDENTITY)

    projection = project(ledger.read_all(), [], [])
    components = projection.components()
    assert len(components) == 1

    annotation = components[0].annotation
    assert annotation.tier is KnowledgeTier.PREDICTED, (
        "a model's output is PREDICTED - it is what a model SAID, and no "
        "sensor observed it")
    assert annotation.basis_record == components[0].component_id
    assert annotation.basis_field == "origin_kind", (
        "the tier carries the RECORDED FIELD that produced it (Ruling 63) - "
        "always a real field, never prose")


def test_c_the_adapter_names_no_tier_at_all():
    """PIN (c), the other direction: NO NEW TIER MACHINERY.

    The tier is DERIVED at read time from the recorded `origin_kind` and is
    never stored (Ruling 63 res.1). An adapter that named a tier would be
    writing epistemic standing at ingress - L3's class, and precisely what the
    standing scanner forbids on the ancestry record.
    """
    named = _code_identifiers()
    for token in ("KnowledgeTier", "PREDICTED", "OBSERVED", "INFERRED",
                  "REPORTED", "TierAnnotation", "tier"):
        assert token not in named, (
            f"the adapter's CODE names `{token}`. Tiers are derived by the "
            f"projection from recorded facts; naming one here would store "
            f"standing at the ingress.")


def test_c_observed_and_inferred_remain_unproducible_through_this_path(tmp_path):
    """PIN (c): the two unproducible tiers stay unproducible.

    AUREA observes nothing and adjudicates nothing (Rulings 63/64). A model
    ingress is the most tempting place for either to leak in - the model DID
    something that resembles inference - and it does not.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    for index in range(3):
        ingest_model_assertion(spy, f"Claim {index}.", f"provider/model-{index}")

    tiers = {c.annotation.tier for c in project(ledger.read_all(), [], [])
             .components()}
    assert tiers == {KnowledgeTier.PREDICTED}
    assert KnowledgeTier.OBSERVED not in tiers
    assert KnowledgeTier.INFERRED not in tiers


# =====================================================================
# (d) TWO-MODEL NON-INDEPENDENCE
# =====================================================================

def test_d_two_models_are_two_claims_with_two_asserters(tmp_path):
    """PIN (d), first half. **THE CONSENSUS TRAP, REFUSED.**

    Identical text from two declared models is TWO CLAIMS, not one
    corroborated claim and not one claim with two votes. There is no consensus
    counting anywhere in this path, and res.4 refuses it standing.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    text = "The bridge will hold."

    ingest_model_assertion(spy, text, IDENTITY)
    ingest_model_assertion(spy, text, OTHER_IDENTITY)

    records = ledger.read_all()
    assert [r.claim_id for r in records] == ["CLM-0001", "CLM-0002"]
    assert [r.asserted_by.value for r in records] == [IDENTITY, OTHER_IDENTITY]
    assert not sg.shares_recorded_asserter(records[0], records[1])


def test_d_undeclared_descent_is_unknown_never_corroboration(tmp_path):
    """PIN (d), THE LOAD-BEARING HALF, and it looks like under-reporting.

    With nothing declared about descent, Ruling 60 reads two model claims as
    UNKNOWN - NOT as two corroborating origins. That is res.4's own reasoning:
    **two models sharing training corpora is the shared-ancestry case O2
    exists to keep honest**, and UNKNOWN NEVER COUNTS AS CORROBORATION.

    A future pass that "improves" this to two distinct origins would be
    manufacturing consensus out of two silences.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    for identity in (IDENTITY, OTHER_IDENTITY):
        ingest_model_assertion(spy, "The bridge will hold.", identity)

    records = ledger.read_all()
    assert sg.pairwise_verdict(records[0], records[1], records) is (
        sg.GenealogyVerdict.UNKNOWN)

    summary = sg.corroboration([r.claim_id for r in records], records)
    assert summary.distinct_recorded_origins == 0, (
        "nothing was recorded about descent, so the record shows NO origins - "
        "not two")
    assert summary.unknown_count == 2


def test_d_declared_descent_is_counted_and_still_never_independent(tmp_path):
    """PIN (d), the control. A caller who DECLARES gets a recorded answer.

    Without this half the pin above would pass against an adapter that
    silently discarded every declaration - UNKNOWN for the wrong reason.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    for identity in (IDENTITY, OTHER_IDENTITY):
        ingest_model_assertion(spy, "The bridge will hold.", identity,
                               basis=declared_none(),
                               replication_refs=declared_none())

    records = ledger.read_all()
    assert sg.pairwise_verdict(records[0], records[1], records) is (
        sg.GenealogyVerdict.NO_RECORDED_LINK), (
        "both channels declared no basis and no replication - a RECORDED "
        "NEGATIVE, which is not the same as silence")

    summary = sg.corroboration([r.claim_id for r in records], records)
    assert summary.distinct_recorded_origins == 2
    assert summary.unknown_count == 0


def test_d_independent_is_never_emitted():
    """PIN (d), the vocabulary. **The refusal IS the ruling** (Ruling 60).

    The ledger records ASSERTIONS ABOUT descent and cannot see the world, so
    NO_RECORDED_LINK is the strongest honest claim. Marked as witnessing at
    baseline: this vocabulary predates Ruling 70, and the pin exists because
    the model-ingress path is where "independent sources" would be most
    tempting to claim.
    """
    names = {m.name for m in sg.GenealogyVerdict}
    values = {m.value for m in sg.GenealogyVerdict}
    assert not any("independent" in n.lower() for n in names)
    assert not any("independent" in v.lower() for v in values)
    assert names == {"SHARED_ASSERTER", "RECORDED_DESCENT",
                     "NO_RECORDED_LINK", "UNKNOWN"}

    # THE ADAPTER EMITS NO VERDICT OF ITS OWN. Its CODE names no genealogy
    # member at all, so it cannot report a standing the vocabulary refuses to
    # express. Scanned by AST rather than lexically: this module's prose
    # DISCUSSES the refusal, and a substring scan would forbid documenting the
    # very rule it enforces.
    named = _code_identifiers()
    assert "GenealogyVerdict" not in named
    assert not any("independent" in n.lower() for n in named)
    assert not any("corroborat" in n.lower() for n in named), (
        "the adapter counts nothing - Ruling 60 owns corroboration, and res.4 "
        "refuses cross-model consensus counting standing")


# =====================================================================
# (e) NO AUTO-COMMIT
# =====================================================================

def test_e_the_adapter_does_not_import_the_prediction_ledger():
    """PIN (e), AST half. res.5, pinned as ABSENCE.

    Classifying "is this text a prediction" is INFERENCE the adapter must not
    perform (BAR §2-adjacent). The absence of the import is what makes the
    classification unwritable rather than merely undone.
    """
    roots = _imported_roots()
    assert "prediction_ledger" not in roots
    assert not any("prediction" in r.lower() for r in roots), (
        f"the adapter reaches the prediction ledger via {sorted(roots)}")


def test_e_a_prediction_shaped_claim_commits_nothing_until_the_caller_does(
        tmp_path):
    """PIN (e), BEHAVIORAL. **THE FORCING HALF.**

    The text is unmistakably prediction-shaped. The O3 ledger stays EMPTY
    until the caller commits explicitly - and then it holds exactly one line,
    with the linkage the CALLER chose.
    """
    ancestry = _ledger(tmp_path)
    predictions = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    spy = _Spy(ancestry)

    result = ingest_model_assertion(
        spy, "The bridge will hold until 2030.", IDENTITY)

    assert predictions.commitments() == (), (
        "a prediction-shaped model claim commits NOTHING - the adapter does "
        "not classify text, and an auto-commit would be inference wearing "
        "plumbing's clothes")
    assert not Path(predictions.ledger_path).exists()

    # The caller commits, explicitly, through Ruling 61's existing API.
    predictions.commit(expected_result="The bridge holds until 2030.",
                       claim_refs=(result["claim_id"],))

    committed = predictions.commitments()
    assert len(committed) == 1
    assert committed[0].claim_refs == (result["claim_id"],)


# =====================================================================
# (f) THE str GATE - Ruling 68's door, at the adapter
# =====================================================================

@pytest.mark.parametrize("bad", [None, b"bytes", {"a": 1}, ["a"], 7, 3.5,
                                 object(), bytearray(b"x")])
def test_f_a_non_str_response_is_refused_and_the_pipeline_is_never_called(bad):
    """PIN (f). **RED FIRST** (collection) at `41ba792`.

    Refused at THIS boundary, BEFORE the pipeline: no claim id, no ledger line,
    nothing perceived. A `TypeError` and deliberately not a coined class - a
    violated type contract is the language's own vocabulary, and this is a
    caller's ordinary mistake rather than one of AUREA's guards firing.
    """
    spy = _Spy()
    with pytest.raises(TypeError) as excinfo:
        ingest_model_assertion(spy, bad, IDENTITY)

    assert "response_text must be str" in str(excinfo.value)
    assert spy.calls == [], (
        "THE PIPELINE WAS CALLED. The refusal must precede perception, or the "
        "adapter has re-opened the ancestry-orphan class from a second door.")


def test_f_a_non_str_response_writes_no_ledger_line(tmp_path):
    """PIN (f), the durable half. Nothing was perceived, so nothing is on record.

    Asserting only the raise would pass against an adapter that refused AFTER
    minting - which is exactly the defect Ruling 68 closed one layer down.
    """
    ledger = _ledger(tmp_path)
    spy = _Spy(ledger)
    with pytest.raises(TypeError):
        ingest_model_assertion(spy, None, IDENTITY)

    assert _lines(ledger) == []
    assert not Path(ledger.ledger_path).exists()


@pytest.mark.parametrize("bad", [None, 7, b"x", ["openai"]])
def test_f_a_non_str_identity_is_refused_before_the_pipeline(bad):
    """PIN (f), the identity's own gate.

    res.1 records the DECLARED model identity STRING. A non-string identity
    cannot be carried byte-identical into the record, so the stated contract
    is enforced rather than documented.
    """
    spy = _Spy()
    with pytest.raises(TypeError) as excinfo:
        ingest_model_assertion(spy, "A claim.", bad)

    assert "model_identity must be str" in str(excinfo.value)
    assert spy.calls == []


@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_f_empty_and_whitespace_responses_remain_perceived(text):
    """PIN (f), THE CONTROL - Ruling 68's own, carried forward.

    The gate's cause is the TYPE, never emptiness. An adapter that refused
    empty text would be narrowing what counts as a claim, which is a different
    and unruled decision.
    """
    spy = _Spy()
    ingest_model_assertion(spy, text, IDENTITY)
    assert len(spy.calls) == 1
    assert spy.calls[0]["raw_input"] == text


# =====================================================================
# (g) VERBATIM
# =====================================================================

@pytest.mark.parametrize("text", [
    "  leading and trailing  ",
    "internal\nnewlines\tand\ttabs",
    "trailing whitespace   ",
    "unicode: éè — ‘quoted’",
    "a" * 5000,
    "  \n mixed \r\n line endings \n  ",
])
def test_g_the_response_reaches_the_pipeline_byte_identical(text):
    """PIN (g). **RED FIRST** (collection) at `41ba792`.

    Spied AT THE BOUNDARY, deliberately: re-deriving this from downstream
    state would measure SPL's `.strip()` - the pipeline's own business,
    applied to every claim alike - instead of the adapter's fidelity.

    A TRANSFORMED ASSERTION IS A DIFFERENT ASSERTION.
    """
    spy = _Spy()
    ingest_model_assertion(spy, text, IDENTITY)

    assert len(spy.calls) == 1
    handed = spy.calls[0]["raw_input"]
    assert handed == text
    assert handed is text, (
        "the very object was passed through - not a copy, not a rebuild, and "
        "certainly not a cleaned version")


def test_g_the_adapter_holds_no_text_transformation():
    """PIN (g), AST half: there is no transformation to accidentally re-enable.

    No `.strip()`, `.lower()`, `.replace()`, `.format()`, no slicing of the
    response. Declared OUT by res.7 with the reason in-file.
    """
    offenders = []
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"strip", "lstrip", "rstrip", "lower",
                                       "upper", "replace", "title",
                                       "splitlines", "encode", "decode",
                                       "truncate"}):
            offenders.append(f"{node.func.attr}:{node.lineno}")
    assert offenders == [], (
        f"the adapter transforms text at {offenders} - a transformed "
        f"assertion is a different assertion")


# =====================================================================
# (h) INJECTION
# =====================================================================

def test_h_the_adapter_constructs_no_core_and_reaches_for_no_global():
    """PIN (h). The collaborator is INJECTED - Ruling 31's injectability as a
    construction property, and it is what makes (f) and (g) answerable at all.

    THE CALLABLE AND NOT THE CORE, deliberately: given an `AureaCore` this
    module would hold the Codex, the scar store and SAE and be trusted not to
    touch them. Given `core.process_input` it holds a way to perceive a claim
    and NOTHING ELSE - enforcement by SCOPE, Ruling 33's move.
    """
    named = _code_identifiers()
    assert "AureaCore" not in named, (
        "the adapter's CODE names AureaCore. It takes the CALLABLE, so it "
        "cannot reach a store it is never handed. (Scanned by AST: the "
        "docstring explains this choice and must stay free to say so.)")
    assert "aurea_core" not in named

    for node in ast.walk(_tree()):
        assert not (isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal)), (
            "the adapter reaches for shared state")


def test_h_any_process_input_shaped_callable_is_accepted():
    """PIN (h): injection is real, not decorative.

    A plain function stands in for the pipeline, which is what lets the
    verbatim and never-called properties be measured at the boundary rather
    than inferred from downstream state.
    """
    seen = []

    def collaborator(raw_input, *, origin=None):
        seen.append((raw_input, origin.kind))
        return {"routed": True}

    out = ingest_model_assertion(collaborator, "A claim.", IDENTITY)
    assert out == {"routed": True}
    assert seen == [("A claim.", OriginKind.MODEL_PREDICTION)]


def test_h_the_real_core_is_accepted_through_the_same_surface():
    """PIN (h), the control: the injected shape IS the production shape.

    Without this, every behavioral pin above could be measuring a spy the real
    pipeline does not resemble.
    """
    core = AureaCore()
    result = ingest_model_assertion(core.process_input, "Water is wet.",
                                    IDENTITY)
    assert result["claim_id"] == "CLM-0001"
    entry = _lines(core.ancestry)[0]
    assert entry["origin_kind"] == "model_prediction"
    assert entry["asserted_by"]["value"] == IDENTITY
