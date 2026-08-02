"""
test_ruling63.py - THE WORLD-STATE PROJECTION (Ruling 63 / Docket O item O5).

Manifest twenty-eighth addendum, 2026-08-01.

    The projection is COMPUTED, never KEPT,
    and it says what KIND of knowing each part of it is.

THE GROUNDING FINDING: the corpus mentions world state ONCE, and there it is
something AUREA RECEIVES and filters - never something she keeps. A projection
that persisted would be the first stored world-model in the architecture,
invented at the layer whose whole job is to refuse exactly that.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `5f50264`, where
`src/external/world_state.py` did not exist.

COINS NOTHING: four tier members verbatim from the registration, the input
shape is O2's, and no threshold, weight, magnitude or duration exists anywhere.
"""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

from src.external.claim_ancestry import (ClaimAncestryRecord, OriginKind,
                                         declared_none, provided)
from src.external.prediction_ledger import (PredictionCommitment,
                                            PredictionLedger,
                                            PredictionOutcome,
                                            PredictionResolution)
from src.external.world_state import (KnowledgeTier, TierAnnotation,
                                      WorldStateComponent,
                                      WorldStateProjection, project)

MODULE = Path("src/external/world_state.py")
HOISTED = Path("src/utils/deep_freeze.py")


def _rec(claim_id: str, kind: OriginKind, **fields) -> ClaimAncestryRecord:
    return ClaimAncestryRecord(claim_id=claim_id, origin_kind=kind, **fields)


def _ledger(tmp_path) -> PredictionLedger:
    return PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))


def _mixed(tmp_path):
    """Ancestry and predictions spanning every producible tier."""
    ancestry = [
        _rec("CLM-0001", OriginKind.HUMAN, asserted_by=provided("Dr X")),
        _rec("CLM-0002", OriginKind.MODEL_PREDICTION,
             asserted_by=provided("engine-A")),
        _rec("CLM-0003", OriginKind.UNDECLARED),
        _rec("CLM-0004", OriginKind.LLM_WRAPPER, asserted_by=declared_none()),
    ]
    ledger = _ledger(tmp_path)
    ledger.commit("A rises", success_criteria=provided("above 10"))
    ledger.commit("B falls", success_criteria=provided("below 5"))
    ledger.commit("C holds", unresolved_criteria=provided("market shut"))
    ledger.resolve("PRD-0002", PredictionOutcome.CONFIRMED, "success_criteria")
    ledger.resolve("PRD-0003", PredictionOutcome.UNRESOLVED, "unresolved_criteria")
    return ancestry, list(ledger.commitments()), list(ledger.resolutions())


# =====================================================================
# A. THE REGISTRATION'S NAMED PROPERTY
# =====================================================================

def test_every_component_is_annotated_and_mixed_inputs_show_mixed_tiers(tmp_path) -> None:
    """PIN (a), THE FORCING PIN. **RED FIRST**: the module did not exist.

    A projection built from mixed inputs shows DIFFERENT tiers on DIFFERENT
    components. That is the whole registered mechanism: the projection does not
    present one undifferentiated picture of what is known, it says what KIND of
    knowing each part of it is.
    """
    projection = project(*_mixed(tmp_path))

    assert isinstance(projection, WorldStateProjection)
    assert len(projection.claims) == 4
    assert len(projection.predictions) == 3

    for component in projection.components():
        assert isinstance(component.annotation, TierAnnotation), (
            "an un-annotated component re-flattens the distinction this docket "
            "exists to preserve")

    tiers = {c.component_id: c.annotation.tier for c in projection.components()}
    assert tiers["CLM-0001"] is KnowledgeTier.REPORTED
    assert tiers["CLM-0002"] is KnowledgeTier.PREDICTED
    assert tiers["CLM-0003"] is None
    assert tiers["CLM-0004"] is KnowledgeTier.REPORTED
    assert tiers["PRD-0001"] is KnowledgeTier.PREDICTED    # unresolved
    assert tiers["PRD-0002"] is KnowledgeTier.INFERRED     # resolved CONFIRMED
    assert tiers["PRD-0003"] is KnowledgeTier.PREDICTED    # resolved UNRESOLVED

    assert len({t for t in tiers.values()}) == 4, (
        "a projection over genuinely mixed inputs must not collapse to one tier")


def test_a_model_prediction_origin_lands_in_the_predicted_tier(tmp_path) -> None:
    """RES.5, AND IT IS ALSO THE CHECK ON O6.

    External world-model engines enter as `origin_kind=MODEL_PREDICTION` and
    reach the PREDICTED tier with NO NEW TIER MACHINERY. If this ever needed a
    fifth member, one of the two rulings would be wrong.
    """
    projection = project([_rec("CLM-0001", OriginKind.MODEL_PREDICTION)], [], [])
    assert projection.claims[0].annotation.tier is KnowledgeTier.PREDICTED


def test_a_settled_prediction_is_inferred_and_an_unsettled_one_is_not(tmp_path) -> None:
    """THE JUDGMENT CALL, PINNED SO IT IS VISIBLE.

    Res.5 names "a component AUREA's own pipeline produced from other
    components -> INFERRED" without naming its producer, and this composition
    has exactly one: a SETTLED prediction was not asserted by any channel and
    is not a claim about the future - it is a fact AUREA's own ledger produced
    by composing a commitment with a resolution.

    Calling it REPORTED was refused because a resolution carries NO
    `origin_kind`, so the attribution would be invented.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("A", success_criteria=provided("x"))
    ledger.commit("B", success_criteria=provided("y"))
    ledger.resolve("PRD-0001", PredictionOutcome.FALSIFIED, "success_criteria")

    projection = project([], list(ledger.commitments()), list(ledger.resolutions()))
    tiers = {c.component_id: c.annotation.tier for c in projection.predictions}

    assert tiers["PRD-0001"] is KnowledgeTier.INFERRED
    assert tiers["PRD-0002"] is KnowledgeTier.PREDICTED


# =====================================================================
# B. NO WRITE, NO STORE
# =====================================================================

def test_the_module_holds_no_write_handle_and_no_path() -> None:
    """PIN (b). **RED FIRST.**

    A MODULE THAT OPENS FILES IS A MODULE THAT CAN BE MADE TO WRITE ONE. The
    inputs arrive as already-read records, so this module needs no path and has
    none - and it does not import either LEDGER, only the record types.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))

    called = {node.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in called

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(a.name for a in node.names)

    forbidden = {"json", "pathlib", "Path", "os", "shutil", "io",
                 "ClaimAncestryLedger", "PredictionLedger", "atomic_write",
                 "src.doctrine.codex", "Codex", "src.filtration.scar_logic_core",
                 "ScarLogicCore", "src.aurea_core", "AureaCore",
                 "src.topology.tca_core", "TopologicalSpace"}
    assert forbidden.isdisjoint(imported), (
        f"the projection reached a store or a write surface: "
        f"{sorted(forbidden & imported)}")

    source = MODULE.read_text(encoding="utf-8")
    for token in ("data/runtime", ".jsonl", ".json", "filepath", "ledger_path",
                  "runtime_path"):
        assert token not in source, f"a path surface appeared: {token!r}"


def test_the_write_scanner_actually_fires() -> None:
    """Ruling 32's answer to the vacuous-pin problem."""
    forbidden = ast.parse("import json\nfrom pathlib import Path\nopen('x','w')\n"
                          "from src.external.prediction_ledger import PredictionLedger\n")
    benign = ast.parse("from src.external.prediction_ledger import "
                       "PredictionCommitment\n")

    def names(tree):
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                found.add(node.module or "")
                found.update(a.name for a in node.names)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                found.add(node.func.id)
        return found

    assert {"json", "Path", "open", "PredictionLedger"} <= names(forbidden)
    assert {"json", "Path", "open", "PredictionLedger"}.isdisjoint(names(benign))


def test_the_projection_is_absent_from_store_owners() -> None:
    """It stores nothing, so registering it would claim coverage that does not
    exist - the completeness-claim defect (CAE's and O2's reason)."""
    registry = Path("tests/invariants/test_ruling1_single_writer.py").read_text(
        encoding="utf-8")
    owners_src = registry.split("STORE_OWNERS", 1)[1].split("}", 1)[0]

    for token in ("world_state", "WorldState", "projection"):
        assert token not in owners_src, (
            f"'{token}' is registered in STORE_OWNERS - the projection owns no "
            f"store, and a registration that guards nothing claims coverage "
            f"that does not exist")


# =====================================================================
# C. NO CACHE - the pin that makes res.1 real
# =====================================================================

def test_successive_calls_carry_nothing_over(tmp_path) -> None:
    """PIN (c), behavioral. **RED FIRST.**

    A CACHED PROJECTION IS A STALE AUTHORITY WAITING FOR A TRUSTING READER.
    Declaring staleness is a discipline; having NO cache makes staleness
    structurally impossible.
    """
    ancestry, commitments, resolutions = _mixed(tmp_path)

    first = project(ancestry, commitments, resolutions)
    second = project([_rec("CLM-9001", OriginKind.HUMAN)], [], [])
    third = project(ancestry, commitments, resolutions)

    assert len(first.claims) == 4 and len(first.predictions) == 3
    assert len(second.claims) == 1 and second.predictions == ()
    assert [c.component_id for c in second.claims] == ["CLM-9001"], (
        "the second call returned components from the first - something is "
        "being carried over")
    assert len(third.claims) == 4, "the third call was served a stale answer"

    assert first is not third, "two calls returned the SAME object - a cache"
    assert first == third, "equal inputs must produce equal projections"


def test_a_changed_input_is_reflected_immediately(tmp_path) -> None:
    """THE MEMOIZATION WITNESS. A projection recomputed from changed records
    must move - a memo keyed on anything would freeze it."""
    ledger = _ledger(tmp_path)
    ledger.commit("A rises", success_criteria=provided("above 10"))

    before = project([], list(ledger.commitments()), list(ledger.resolutions()))
    assert before.predictions[0].annotation.tier is KnowledgeTier.PREDICTED

    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")
    after = project([], list(ledger.commitments()), list(ledger.resolutions()))

    assert after.predictions[0].annotation.tier is KnowledgeTier.INFERRED, (
        "the projection did not follow the record - it was memoized")


def test_the_module_holds_no_mutable_state(tmp_path) -> None:
    """PIN (c), structural. NO module-level mutable state, NO memoization.

    A module-level dict is the shape a cache arrives in, and
    `functools.lru_cache` is the shape it arrives in when nobody wants to write
    the dict.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(a.name for a in node.names)
    assert {"functools", "lru_cache", "cache", "cached_property"}.isdisjoint(
        imported), "a memoization helper was imported"

    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                value = node.value
                assert isinstance(value, ast.Call) and getattr(
                    value.func, "id", "") == "frozenset" or isinstance(
                    value, ast.Constant), (
                    f"module-level mutable state '{target.id}' at line "
                    f"{node.lineno} - a projection that keeps anything between "
                    f"calls is the cache res.1 refuses")

    # No instance ever holds one either: the entry point is a free function.
    assert callable(project) and not hasattr(project, "cache_clear")


# =====================================================================
# D. OBSERVED IS PRESENT AND UNPRODUCIBLE
# =====================================================================

def test_observed_is_never_emitted_by_any_input_combination(tmp_path) -> None:
    """PIN (d). **RED FIRST.** Ruling 50's SOFTENED precedent exactly.

    AUREA OBSERVES NOTHING. ELM is canon's only sensor path and it is unbuilt,
    so every record reaching this projection arrived through a channel that
    ASSERTED rather than a sensor that MEASURED.
    """
    ancestry = [_rec(f"CLM-{n:04d}", kind)
                for n, kind in enumerate(OriginKind, start=1)]
    ledger = _ledger(tmp_path)
    ledger.commit("A", success_criteria=provided("x"))
    ledger.commit("B", success_criteria=provided("y"))
    ledger.commit("C", unresolved_criteria=provided("z"))
    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")
    ledger.resolve("PRD-0002", PredictionOutcome.FALSIFIED, "success_criteria")
    ledger.resolve("PRD-0003", PredictionOutcome.UNRESOLVED, "unresolved_criteria")

    projection = project(ancestry, list(ledger.commitments()),
                         list(ledger.resolutions()))

    assert all(c.annotation.tier is not KnowledgeTier.OBSERVED
               for c in projection.components()), (
        "OBSERVED was emitted. AUREA observes nothing - there is no sensor "
        "path, so this claims a kind of access she does not have")


def test_observed_remains_a_member_and_no_code_path_assigns_it() -> None:
    """THE MEMBER STAYS, and the ban is STRUCTURAL.

    A closed vocabulary missing a registered member is the enum reopening
    later, so OBSERVED is present. But `KnowledgeTier.OBSERVED` must appear
    NOWHERE in the module except its own definition.
    """
    assert KnowledgeTier.OBSERVED.value == "observed"
    assert {m.name for m in KnowledgeTier} == {
        "OBSERVED", "REPORTED", "INFERRED", "PREDICTED"}

    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    loads = [node.lineno for node in ast.walk(tree)
             if isinstance(node, ast.Attribute) and node.attr == "OBSERVED"]
    assert loads == [], (
        f"`KnowledgeTier.OBSERVED` is referenced in code at lines {loads} - no "
        f"code path may emit it until a sensor path exists whose records are "
        f"MEASUREMENTS rather than assertions")


# =====================================================================
# E. UNDECLARED -> None, BOTH DIRECTIONS
# =====================================================================

def test_undeclared_never_becomes_reported(tmp_path) -> None:
    """PIN (e), direction one. **RED FIRST.** THE FABRICATION PIN.

    Ruling 58 exists because `process_input` defaulted a missing origin to
    `"user"` and wrote a human origin into a durable store for every claim the
    system had ever processed. Defaulting UNDECLARED to REPORTED here would
    commit THE IDENTICAL FABRICATION one layer later, on the read side, where
    nothing durable records it and nothing catches it.
    """
    projection = project([_rec("CLM-0001", OriginKind.UNDECLARED)], [], [])
    annotation = projection.claims[0].annotation

    assert annotation.tier is None, (
        "a channel that declared nothing was reported as having declared "
        "something - L3's fabrication class, re-entering at the read side")
    assert annotation.tier is not KnowledgeTier.REPORTED


def test_the_none_tier_is_rendered_never_omitted(tmp_path) -> None:
    """PIN (e), direction two. AN UNDETERMINED COMPONENT IS STILL A COMPONENT.

    Silently dropping it would re-flatten exactly the distinction this docket
    preserves - and would do it invisibly, since a shorter list looks like a
    smaller world rather than a hidden one.
    """
    ancestry = [_rec("CLM-0001", OriginKind.HUMAN),
                _rec("CLM-0002", OriginKind.UNDECLARED),
                _rec("CLM-0003", OriginKind.EXTERNAL_AI)]

    projection = project(ancestry, [], [])

    assert [c.component_id for c in projection.claims] == [
        "CLM-0001", "CLM-0002", "CLM-0003"], (
        "the undetermined component vanished from the projection")
    assert projection.claims[1].annotation.tier is None
    assert projection.claims[1].annotation.basis_field == "origin_kind", (
        "even the undetermined case states its basis")


def test_no_fifth_tier_member_was_coined() -> None:
    """`Optional` plus a stated basis carries the undetermined case, and the
    registered vocabulary stays exactly four."""
    assert len(KnowledgeTier) == 4
    for name in ("UNDETERMINED", "UNKNOWN", "UNDECLARED", "NONE", "ABSENT"):
        assert not hasattr(KnowledgeTier, name), (
            f"a fifth member '{name}' was coined for the undetermined case")


# =====================================================================
# F. THE BASIS IS A RECORDED FIELD REFERENCE
# =====================================================================

def test_every_basis_names_a_field_that_exists_on_a_record(tmp_path) -> None:
    """PIN (f). **RED FIRST.** RULING 45's move: the annotation carries its own
    argument, so a reader can go and check rather than trust.

    The basis is a RECORDED FIELD REFERENCE, never prose invention - so every
    `basis_field` must be a real attribute of a real record type.
    """
    ancestry, commitments, resolutions = _mixed(tmp_path)
    projection = project(ancestry, commitments, resolutions)

    record_fields = (set(ClaimAncestryRecord.__dataclass_fields__)
                     | set(PredictionCommitment.__dataclass_fields__)
                     | set(PredictionResolution.__dataclass_fields__))

    ids = {r.claim_id for r in ancestry} | {c.prediction_id for c in commitments}

    for component in projection.components():
        annotation = component.annotation
        assert annotation.basis_field in record_fields, (
            f"'{annotation.basis_field}' is not a field of any input record - "
            f"a basis must name a recorded fact, not describe one")
        assert annotation.basis_record in ids, (
            f"'{annotation.basis_record}' names no input record")


def test_the_basis_points_at_the_field_that_actually_decided(tmp_path) -> None:
    """Not merely A field - THE field the derivation read."""
    projection = project([_rec("CLM-0001", OriginKind.HUMAN)], [], [])
    assert projection.claims[0].annotation.basis_field == "origin_kind"

    ledger = _ledger(tmp_path)
    ledger.commit("A", success_criteria=provided("x"))
    unresolved = project([], list(ledger.commitments()), [])
    assert unresolved.predictions[0].annotation.basis_field == "expected_result"

    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")
    resolved = project([], list(ledger.commitments()), list(ledger.resolutions()))
    assert resolved.predictions[0].annotation.basis_field == "outcome"


def test_a_raw_string_cannot_enter_a_tier_annotation() -> None:
    """The closed enum is enforced at construction."""
    with pytest.raises(TypeError):
        TierAnnotation(tier="reported", basis_record="CLM-0001",
                       basis_field="origin_kind")


# =====================================================================
# G. THE COMPOSED SET IS CLOSED
# =====================================================================

def test_the_composed_set_accepts_exactly_the_three_record_types(tmp_path) -> None:
    """PIN (g). **RED FIRST.** RES.3, ENFORCED RATHER THAN DOCUMENTED.

    A projection that composes the doctrine spine and the scar store stops
    being a view over external epistemics and becomes THE SOVEREIGN
    WORLD-MODEL THE DOCKET REFUSED BY NAME. The boundary is checkable at the
    input list, so widening is a DELIBERATE EDIT rather than something that
    happens because a caller passed something new and nothing objected.
    """
    from src.utils.models import Doctrine

    doctrine = Doctrine(id="D-1", name="Fracture Carried")

    for args in (([doctrine], [], []),
                 ([], [doctrine], []),
                 ([], [], [doctrine])):
        with pytest.raises(TypeError, match="composed set is CLOSED"):
            project(*args)

    # And the three legitimate types compose without complaint.
    assert project(*_mixed(tmp_path)) is not None


def test_the_signature_names_exactly_the_three_registered_types() -> None:
    """Widening is a deliberate edit, visible in the signature."""
    import inspect
    params = inspect.signature(project).parameters
    assert list(params) == ["ancestry", "commitments", "resolutions"]


# =====================================================================
# H. FROZEN OUTPUT, WITH THE BYTEARRAY LEAF WITNESS
# =====================================================================

def test_the_projection_is_frozen(tmp_path) -> None:
    """PIN (h). Ruling 52 - the shell."""
    projection = project(*_mixed(tmp_path))

    with pytest.raises(Exception):
        projection.claims = ()
    with pytest.raises(Exception):
        projection.claims[0].component_id = "CLM-9999"
    with pytest.raises(Exception):
        projection.claims[0].annotation.tier = KnowledgeTier.OBSERVED


def test_a_mutable_leaf_in_an_input_record_cannot_edit_the_projection() -> None:
    """PIN (h), THE BYTEARRAY LEAF WITNESS - the standing drafting requirement
    from the fifty-eighth entry, applied at its first opportunity.

    NOT A NESTED CONTAINER, and that distinction is the whole reason this pin
    is specified that way: `deep_freeze` REBUILDS containers, so a nested list
    is already copied and would pass against an implementation with no
    `deepcopy` at all. A MUTABLE LEAF is what the freeze passes through
    untouched - it has escaped as a surviving mutant three times now (Batch 51,
    Ruling 58, Ruling 61).

    THE HAZARD IS REAL HERE AND NOT CEREMONIAL: without the copy, the
    projection's `detail` would ALIAS the input record's own leaf, so a caller
    still holding that record could edit a projection AFTER it was returned -
    which is a cache with extra steps, the thing res.1 refuses.
    """
    leaf = bytearray(b"Dr X")
    record = ClaimAncestryRecord(claim_id="CLM-0001",
                                 origin_kind=OriginKind.HUMAN,
                                 asserted_by=provided(leaf))

    projection = project([record], [], [])
    assert projection.claims[0].detail == bytearray(b"Dr X")

    # The record made its own copy at construction (Ruling 58); mutate THAT one,
    # which is what the projection was handed.
    record.asserted_by.value.extend(b" OR WHOEVER WE SAY LATER")

    assert projection.claims[0].detail == bytearray(b"Dr X"), (
        "the returned projection moved when an input record's leaf was edited "
        "- the projection aliases its inputs and is editable after return")


def test_an_unannotated_component_cannot_be_constructed() -> None:
    """The annotation is not optional anywhere."""
    with pytest.raises(TypeError):
        WorldStateComponent(component_id="X", detail="y", annotation=None)


# =====================================================================
# I. NO NUMBERS
# =====================================================================

def test_the_projection_carries_no_number_of_any_kind(tmp_path) -> None:
    """RES.6. A projection is exactly where a summary number would feel
    natural and be false.

    THERE IS DELIBERATELY NO TALLY FIELD EITHER. Counts of record are
    PERMITTED as tallies but not required, and a count PRESENTED BY THE
    PROJECTION is one short step from a count presented as a quality signal.
    A caller who wants to count these tuples can count them, and the counting
    is then visibly theirs.
    """
    projection = project(*_mixed(tmp_path))

    forbidden = ("confidence", "completeness", "coverage", "score", "ratio",
                 "weight", "accuracy", "count", "total", "percent", "tally")
    for surface in (projection, projection.claims[0],
                    projection.claims[0].annotation):
        for name in forbidden:
            assert not hasattr(surface, name), (
                f"{type(surface).__name__}.{name} presents a number")

    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    numbers = [n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant)
               and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)]
    assert numbers == [], f"a numeric literal appeared in the module: {numbers}"


def test_nothing_in_src_consumes_the_projection() -> None:
    """NO CONSUMER WIRING THIS PASS - a resolution, not an omission. An
    instrument first, consumers by later ruling.

    Matched by IMPORT rather than substring (the conversion Ruling 63 applied
    to Ruling 60's pin in the same pass): a prose mention is not a consumer.
    """
    consumers = []
    for path in Path("src").rglob("*.py"):
        if path == MODULE:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = set()
            if isinstance(node, ast.Import):
                names = {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""} | {a.name for a in node.names}
            if any("world_state" in name for name in names):
                consumers.append(f"{path.as_posix()}:{node.lineno}")

    assert consumers == [], (
        f"{consumers} consume the world-state projection. Wiring it into a "
        f"verdict path, an expression surface or a routing decision is a "
        f"RULING (Ruling 63 res.7), not an implementation choice")


# =====================================================================
# J. THE HOIST (owed item, taken this pass)
# =====================================================================

def test_the_freeze_pair_has_exactly_one_definition_in_src() -> None:
    """THE OWED HOIST, TAKEN. `claim_ancestry`'s own docstring set the rule:
    "if a THIRD appears, the honest move is to hoist one copy into
    `src/utils/` rather than write a third".

    Ruling 61 was the third user and declined (importing the private copy);
    Ruling 63 is the fourth, the manifest marked it DUE, and this pass's bar
    sanctioned the files. One behaviour, one definition.
    """
    definitions = []
    for path in Path("src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.FunctionDef)
                    and node.name in ("deep_freeze", "_deep_freeze",
                                      "thaw", "_thaw")):
                definitions.append(f"{path.as_posix()}:{node.name}")

    assert sorted(definitions) == [
        "src/utils/deep_freeze.py:deep_freeze",
        "src/utils/deep_freeze.py:thaw"], (
        f"the freeze pair has more than one definition: {sorted(definitions)}")


def test_the_hoisted_helper_imports_no_store() -> None:
    """Vocabulary and mechanism only - the `continuity.py` / `atomic_write.py`
    precedent. A helper that reaches a store is a helper that can be made to
    write one."""
    tree = ast.parse(HOISTED.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(a.name for a in node.names)

    assert not any(name.startswith("src.") for name in imported), (
        f"the hoisted helper reached into `src/`: {sorted(imported)}")
    assert {"json", "pathlib", "Path", "os"}.isdisjoint(imported)


def test_the_hoisted_helper_has_its_own_behavioural_pins() -> None:
    """ADDED AFTER TWO SURVIVING MUTANTS, and the reason is worth recording.

    Deleting `deep_freeze`'s dict rebuild or its sequence rebuild survived
    `test_ruling63.py` entirely - this file pinned that the helper EXISTS once,
    imports no store, and is bound at both call sites, but never that it
    FREEZES anything. Against the full suite both go red, so the behaviour is
    guarded; the sequence mutant is caught by exactly ONE test in 880.

    A SHARED HELPER THAT IS ONLY GUARDED THROUGH ITS CONSUMERS IS GUARDED BY
    ACCIDENT. Ruling 63 created the shared surface, so the pins belong here
    too - at its home, not scattered across two modules that happen to use it.
    """
    from types import MappingProxyType

    from src.utils.deep_freeze import deep_freeze, thaw

    frozen = deep_freeze({"a": [1, {"b": {2, 3}}]})
    assert isinstance(frozen, MappingProxyType)
    assert isinstance(frozen["a"], tuple)
    assert isinstance(frozen["a"][1]["b"], frozenset), "the rebuild is recursive"

    with pytest.raises(TypeError):
        frozen["a"] = ()

    # EVERY CONTAINER RETURNED IS NEW - the half that makes the freeze airtight.
    # A proxy over the caller's own dict is a VIEW.
    original = {"a": [1]}
    frozen_again = deep_freeze(original)
    original["a"].append(2)
    assert frozen_again["a"] == (1,), (
        "the freeze returned a view over the caller's container")

    # A LEAF IS PASSED THROUGH - documented, and why every call site deepcopies.
    leaf = bytearray(b"x")
    assert deep_freeze(leaf) is leaf

    # `thaw` inverts exactly what `deep_freeze` converted, and no more.
    assert thaw(frozen)["a"][0] == 1
    assert isinstance(thaw(frozen), dict) and isinstance(thaw(frozen)["a"], list)
    assert isinstance(thaw(deep_freeze({"s": {1}}))["s"], frozenset), (
        "a frozenset is deliberately left alone - thawing one would change "
        "behaviour for an input that was never JSON-serializable anyway")


def test_the_hoist_preserved_the_local_names_at_both_call_sites() -> None:
    """The hoist moved a DEFINITION, not a line of behaviour: both former
    owners still bind `_deep_freeze` / `_thaw` locally, so every call site and
    every AST pin naming them is unchanged."""
    from src.doctrine import mutation_proof
    from src.external import claim_ancestry
    from src.utils.deep_freeze import deep_freeze, thaw

    for module in (mutation_proof, claim_ancestry):
        assert module._deep_freeze is deep_freeze
        assert module._thaw is thaw
