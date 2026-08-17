"""M8-a: `stake-classifier.v1` -- the deterministic floor under escalation.

THE NINE BINDING PROPERTIES, in the specification's order:
  1. Determinism -- identical inputs, identical classification AND derivation.
  2. Each DERIVABLE class witnessed in BOTH directions, on fixtures built
     through the kernel's own doors.
  3. Highest-holds -- a target satisfying S1 and S2 classifies S2.
  4. S0 on the bare claim.
  5. Closed vocabulary -- the sixth member unwritable.
  6. Purity by import-absence; no mutation-surface contact.
  7. No magnitudes -- presence/membership, never counts against thresholds.
  8. Underivable conditions pinned AS underivable, so the gap closes
     deliberately rather than by drift.
  9. All prior executive pin files byte-unmodified.
"""

import ast
import hashlib
import pathlib

import pytest

from src.doctrine.codex import Codex
from src.executive.derived_view import (ChairState, DerivedView,
                                        build_stake_substrate)
from src.executive.stake_classifier import (CLASSIFIER_NAME, CLASSIFIER_VERSION,
                                            REGISTRATION,
                                            UNDERIVABLE_TOUCH_FACTS,
                                            ClassifierIdentityMismatch,
                                            StakeClass, StakeClassifier)
from src.external.claim_ancestry import (ClaimAncestryLedger, OriginDeclaration,
                                         OriginKind, provided)
from src.external.prediction_ledger import PredictionLedger
from src.filtration.scar_logic_core import ScarLogicCore
from src.identity.ril import RIL
from src.suspension.black_sphere import BlackSphere
from src.worldmodel.proposition_ledger import (KernelRef, KernelRefKind,
                                               PropositionKind,
                                               PropositionLedger)

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"


def _view(**handles) -> DerivedView:
    """A view carrying ONLY a stake substrate - the classifier reads nothing else."""
    return DerivedView(
        open_obligations=(), unresolved_predictions=(), committed_goals=(),
        chair=ChairState.UNREGISTERED, verdict_acquisition_id=(),
        candidates=(), stake=build_stake_substrate(**handles))


def _classify(target_id, kind="claim", **handles):
    return StakeClassifier().classify(kind, target_id, _view(**handles))


# ===========================================================================
# PIN 1 - DETERMINISM
# ===========================================================================

def test_1_identical_inputs_yield_identical_classification_and_derivation(
        tmp_path):
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    parent = ancestry.record().claim_id
    ancestry.record(OriginDeclaration(kind=OriginKind.HUMAN,
                                      basis=provided(f"derived from {parent}")))
    first = _classify(parent, ancestry=ancestry)
    second = _classify(parent, ancestry=ancestry)
    assert first == second
    assert first.as_dict() == second.as_dict()


# ===========================================================================
# PIN 2 - EACH DERIVABLE CLASS, BOTH DIRECTIONS
# ===========================================================================

def test_2_s1_holds_on_an_ancestry_child_and_not_without_one(tmp_path):
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    cited = ancestry.record().claim_id
    lonely = ancestry.record().claim_id
    citing = ancestry.record(OriginDeclaration(
        kind=OriginKind.HUMAN, basis=provided(f"follows from {cited}"))).claim_id

    held = _classify(cited, ancestry=ancestry)
    assert held.stake_class is StakeClass.S1_LINKED
    assert citing in held.conditions[0].consulted_record_ids
    # OTHER DIRECTION: a claim nothing cites is not S1.
    assert _classify(lonely, ancestry=ancestry).stake_class is \
        StakeClass.S0_PERIPHERAL


def test_2b_s1_holds_on_a_prediction_reference(tmp_path):
    predictions = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    committed = predictions.commit("about a claim", claim_refs=("CLM-0007",))
    held = _classify("CLM-0007", predictions=predictions)
    assert held.stake_class is StakeClass.S1_LINKED
    assert committed.prediction_id in held.conditions[0].consulted_record_ids
    assert _classify("CLM-0008", predictions=predictions).stake_class is \
        StakeClass.S0_PERIPHERAL


def test_2c_s1_holds_on_a_world_proposition_reference(tmp_path):
    """The proposition ledger REFUSES an unverifiable reference (M6), so this
    fixture supplies a real resolver and a real claim - which is what "built
    through the kernel's own doors" means when the door has a guard."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    claim = ancestry.record().claim_id
    props = PropositionLedger(ledger_path=str(tmp_path / "wmp.jsonl"),
                              ancestry_ledger=ancestry)
    record = props.record(
        PropositionKind.STATE, "the bridge stands",
        supported_by=(KernelRef(KernelRefKind.CLAIM, claim),))
    held = _classify(claim, propositions=props)
    assert held.stake_class is StakeClass.S1_LINKED
    assert record.wmp_id in held.conditions[0].consulted_record_ids
    # OTHER DIRECTION: a real claim no proposition references.
    other = ancestry.record().claim_id
    assert _classify(other, propositions=props).stake_class is \
        StakeClass.S0_PERIPHERAL


def test_2d_s2_holds_on_doctrine_linkage_and_not_on_an_unlinked_scar(tmp_path):
    """BOTH DIRECTIONS OF RULING 26, on the REAL SEED - which is where the two
    halves genuinely disagree."""
    codex, scars = Codex(), ScarLogicCore()
    # A seed scar the Codex links to doctrines.
    linked = next(s for s in scars.all_scars()
                  if codex.by_scar(s.id) or getattr(s, "linked_doctrines", None))
    held = _classify(linked.id, kind="scar", codex=codex, scar_core=scars)
    assert held.stake_class in (StakeClass.S2_DOCTRINAL, StakeClass.S3_STRUCTURAL)
    s2 = next(c for c in held.conditions if c.stake_class is StakeClass.S2_DOCTRINAL)
    assert s2.held and s2.consulted_record_ids
    # OTHER DIRECTION: an id no doctrine links to.
    bare = _classify("Δ-NOT-A-SCAR", kind="scar", codex=codex, scar_core=scars)
    assert not next(c for c in bare.conditions
                    if c.stake_class is StakeClass.S2_DOCTRINAL).held


def test_2e_s3_holds_on_a_suspension_and_on_an_entrenched_doctrine(tmp_path):
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    entry = sphere.suspend("a paradox that will not close", 0.9,
                           claim_id="CLM-0021")
    entry_id = getattr(entry, "entry_id", None) or getattr(entry, "id", None)

    held = _classify(entry_id, kind="suspension", suspensions=[sphere])
    assert held.stake_class is StakeClass.S3_STRUCTURAL
    # ...and the CLAIM the suspension was taken for is structural too.
    by_claim = _classify("CLM-0021", suspensions=[sphere])
    assert by_claim.stake_class is StakeClass.S3_STRUCTURAL
    # OTHER DIRECTION.
    assert _classify("CLM-0022", suspensions=[sphere]).stake_class is \
        StakeClass.S0_PERIPHERAL

    # ENTRENCHMENT, the other S3 half, on the real seed.
    codex = Codex()
    seed_doctrine = next(d for d in codex.active() if d.is_seed)
    entrenched = _classify(seed_doctrine.id, kind="doctrine", codex=codex)
    assert entrenched.stake_class is StakeClass.S3_STRUCTURAL


def test_2f_s4_holds_on_an_identity_thread_reference(tmp_path):
    """S4's DERIVABLE half - RIL's threads carry by-id entries (Ruling 42)."""
    scars = ScarLogicCore()
    ril = RIL(runtime_path=str(tmp_path / "ril.json"))
    scar = scars.all_scars()[0]
    ril.ingest_scar(scar)

    held = _classify(scar.id, kind="scar", ril=ril)
    assert held.stake_class is StakeClass.S4_IDENTITY
    assert scar.id in held.conditions[3].consulted_record_ids
    # OTHER DIRECTION: an id RIL never wrote into a thread.
    assert _classify("Δ-NEVER-INGESTED", kind="scar", ril=ril).stake_class is \
        StakeClass.S0_PERIPHERAL


# ===========================================================================
# PIN 3 - HIGHEST-HOLDS
# ===========================================================================

def test_3_a_target_satisfying_s1_and_s2_classifies_s2(tmp_path):
    """The ruled rule, witnessed where it actually decides something."""
    codex, scars = Codex(), ScarLogicCore()
    linked = next(s for s in scars.all_scars() if codex.by_scar(s.id))
    predictions = PredictionLedger(ledger_path=str(tmp_path / "prd.jsonl"))
    predictions.commit("about that scar", claim_refs=(linked.id,))

    result = _classify(linked.id, kind="scar", codex=codex, scar_core=scars,
                       predictions=predictions)
    held = {c.stake_class for c in result.conditions if c.held}
    assert StakeClass.S1_LINKED in held and StakeClass.S2_DOCTRINAL in held
    assert result.stake_class is StakeClass.S2_DOCTRINAL


def test_3b_every_condition_is_evaluated_not_only_the_winner(tmp_path):
    """A classification that recorded only its winner would leave a reader
    unable to tell a checked-and-absent condition from an unchecked one."""
    result = _classify("CLM-0001")
    assert [c.stake_class for c in result.conditions] == [
        StakeClass.S1_LINKED, StakeClass.S2_DOCTRINAL,
        StakeClass.S3_STRUCTURAL, StakeClass.S4_IDENTITY]


# ===========================================================================
# PIN 4 - S0 ON THE BARE CLAIM
# ===========================================================================

def test_4_a_bare_claim_with_every_surface_consulted_is_s0(tmp_path):
    """S0 EARNED, not defaulted: every surface is supplied and each says no."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    bare = ancestry.record().claim_id
    result = _classify(
        bare, ancestry=ancestry,
        predictions=PredictionLedger(ledger_path=str(tmp_path / "p.jsonl")),
        propositions=PropositionLedger(ledger_path=str(tmp_path / "w.jsonl")),
        codex=Codex(), scar_core=ScarLogicCore(),
        suspensions=[BlackSphere(filepath=str(tmp_path / "bs.json"))],
        ril=RIL(runtime_path=str(tmp_path / "ril.json")))
    assert result.stake_class is StakeClass.S0_PERIPHERAL
    assert not any(c.held for c in result.conditions)
    # Every DERIVABLE condition was fully consulted; only S4's declared
    # underivable half keeps the whole classification from being complete.
    assert all(c.fully_consulted for c in result.conditions[:3])
    assert result.fully_derivable is False


# ===========================================================================
# PIN 5 - CLOSED VOCABULARY
# ===========================================================================

def test_5_the_vocabulary_is_exactly_the_five_ruled_members():
    assert [m.value for m in StakeClass] == [
        "s0_peripheral", "s1_linked", "s2_doctrinal", "s3_structural",
        "s4_identity"]
    with pytest.raises(ValueError):
        StakeClass("s5_cosmic")


def test_5b_each_member_carries_the_ruled_definition():
    source = (SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8")
    for phrase in (
            "touches only the claim itself",
            "recorded dependents or joins",
            "touches doctrine standing",
            "touches the load-bearing architecture",
            "touches identity commitments or the kernel-fixed"):
        assert phrase in source, phrase


# ===========================================================================
# PIN 6 - PURITY
# ===========================================================================

FORBIDDEN = ("random", "secrets", "numpy", "datetime", "time", "pathlib", "os",
             "json", "src.filtration", "src.goals", "src.external",
             "src.doctrine", "src.identity", "src.suspension", "src.worldmodel",
             "src.utils", "src.executive.loop", "src.executive.selection_log",
             "src.executive.inquiry_log")


def test_6_the_classifier_imports_nothing_it_could_read_draw_or_write_with():
    tree = ast.parse((SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8"))
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            seen.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            seen.add(node.module)
    for name in seen:
        for bad in FORBIDDEN:
            assert not (name == bad or name.startswith(bad + ".")), name


def test_6b_no_mutation_surface_contact_and_no_write_call():
    tree = ast.parse((SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open"
        if isinstance(node, ast.Attribute):
            assert node.attr not in {
                "record", "commit", "admit", "suspend", "save", "write",
                "save_to_file", "form_scar", "resolve", "_append"}


def test_6c_classification_writes_nothing(tmp_path):
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    claim = ancestry.record().claim_id
    before = (tmp_path / "clm.jsonl").read_bytes()
    for _ in range(5):
        _classify(claim, ancestry=ancestry)
    assert (tmp_path / "clm.jsonl").read_bytes() == before


# ===========================================================================
# PIN 7 - NO MAGNITUDES
# ===========================================================================

def test_7_no_condition_compares_a_count_to_anything():
    """Conditions are presence/membership. `held` is `bool(ids)` and nothing
    else - the one place a magnitude would feel natural is the one place the
    grounding's bar forbids it."""
    tree = ast.parse((SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_s"):
            for inner in ast.walk(node):
                assert not isinstance(inner, ast.Compare) or all(
                    isinstance(op, (ast.Eq, ast.NotEq, ast.In, ast.NotIn))
                    for op in inner.ops), node.name
                assert not (isinstance(inner, ast.Call)
                            and getattr(inner.func, "id", None) == "len"), node.name


def test_7d_the_claim_id_scan_is_anchored_never_a_substring(tmp_path):
    """RULING 64's RIDER at a new surface: `CLM-0001` must not be found inside
    `XCLM-0001`, and the extraction must take the WHOLE ordinal so
    `CLM-00011` never reads as `CLM-0001`."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "clm.jsonl"))
    target = ancestry.record().claim_id                      # CLM-0001
    ancestry.record(OriginDeclaration(
        kind=OriginKind.HUMAN,
        basis=provided(f"see X{target} and {target}1 and {target}x")))
    # Every mention is a NEAR MISS; none of them cites the target.
    assert _classify(target, ancestry=ancestry).stake_class is \
        StakeClass.S0_PERIPHERAL


def test_7e_the_entrenched_basis_set_is_exactly_the_dug_in_pair():
    """DECLARED DATA, pinned: widening this silently raises stake classes.

    SEED and SCAR_SURVIVED are dug in; DERIVED and PROVISIONAL are not - a
    doctrine descending from something fallen, or merely asserted, has not been
    tested into the load-bearing architecture.
    """
    from src.doctrine.entrenchment import EntrenchmentBasis
    from src.executive.derived_view import ENTRENCHED_BASES
    assert ENTRENCHED_BASES == {"seed", "scar_survived"}
    # ...and every member of it is a REAL member of the Codex's vocabulary.
    assert ENTRENCHED_BASES <= {m.value for m in EntrenchmentBasis}


def test_7b_the_module_holds_no_numeric_threshold():
    tree = ast.parse((SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8"))
    indices = {id(n.slice) for n in ast.walk(tree) if isinstance(n, ast.Subscript)}
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool) and id(n) not in indices}
    assert literals == set(), literals


def test_7c_one_dependent_and_many_classify_the_same(tmp_path):
    """The ruled question is WHAT a disposition touches, never HOW MUCH."""
    predictions = PredictionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    predictions.commit("one", claim_refs=("CLM-0001",))
    one = _classify("CLM-0001", predictions=predictions).stake_class
    for _ in range(20):
        predictions.commit("more", claim_refs=("CLM-0001",))
    many = _classify("CLM-0001", predictions=predictions).stake_class
    assert one is many is StakeClass.S1_LINKED


# ===========================================================================
# PIN 8 - THE UNDERIVABLE CONDITION, PINNED AS UNDERIVABLE
# ===========================================================================

def test_8_the_kernel_fixed_stratum_has_no_record_surface(tmp_path):
    """**A REPORTED GAP, PINNED SO IT CLOSES DELIBERATELY.**

    S4's second half - the kernel-fixed stratum's adjacency - has no record
    surface anywhere in `src/`, so no id can be tested against it. It is
    DECLARED rather than silently dropped, and every S4 result names it.

    This pin REDDENS the day a surface appears, which is when the class's
    second half needs building rather than declaring.
    """
    assert "kernel_fixed_stratum_adjacency" in UNDERIVABLE_TOUCH_FACTS
    hits = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in ("kernel_fixed", "fixed_stratum"):
            if token in text and "stake_classifier" not in path.name:
                hits.append(path.as_posix())
    assert hits == [], hits

    result = _classify("CLM-0001", ril=RIL(runtime_path=str(tmp_path / "r.json")))
    s4 = result.conditions[3]
    assert s4.underivable_facts == ("kernel_fixed_stratum_adjacency",)
    # ...so S4 is NEVER "fully consulted", even when its derivable half is read.
    assert s4.fully_consulted is False


def test_8b_an_unconsulted_surface_is_not_an_absence_of_stake(tmp_path):
    """DOCKET H'S CUT AT THE STAKE LAYER, and the worst place to lose it: an
    unconsulted surface must not read as "no stake" and route a structural
    disposition to the cheapest rung."""
    result = _classify("Doctrine-0.1", kind="doctrine")   # no handles at all
    assert result.stake_class is StakeClass.S0_PERIPHERAL
    assert result.fully_derivable is False
    for condition in result.conditions:
        assert condition.consulted_surfaces == ()
        assert condition.fully_consulted is False
    # ...and with the surface supplied, the SAME target is structural.
    assert _classify("Doctrine-0.1", kind="doctrine",
                     codex=Codex()).stake_class is StakeClass.S3_STRUCTURAL


# ===========================================================================
# PIN 9 - PRIOR EXECUTIVE PIN FILES BYTE-UNMODIFIED
# ===========================================================================

_FROZEN = {
    "tests/test_m7a_executive_loop.py":
        "c7867cd28cf7d76d64683024a2c86335ec0f27bc3676e9467ef615523adc58fe",
    "tests/test_m7b_attention_policy.py":
        "5ea92b1f5ef9c278499151705ad2fc1180522665fda9b0e5f0c07544ad8bf700",
    "tests/test_m7c_inquiry.py":
        "6029d504c25fe4d2b1717339f1a74e34bce04d11460a08c587424efcd8227aa6",
}


def test_9_the_prior_executive_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN.items():
        actual = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
        assert actual == expected, path


# ===========================================================================
# IDENTITY AND THE REGISTRATION SLOT
# ===========================================================================

def test_identity_is_data():
    assert CLASSIFIER_NAME == "stake-classifier.v1"
    with pytest.raises(ClassifierIdentityMismatch):
        StakeClassifier(name="stake-classifier.v2")
    with pytest.raises(ClassifierIdentityMismatch):
        StakeClassifier(version="2")


def test_the_registration_slot_is_declared_data_and_gates_nothing():
    """FORK 8.1, RULED: a REGISTRATION surface, not a qualification gate."""
    assert REGISTRATION["identity"] == CLASSIFIER_NAME
    assert REGISTRATION["version"] == CLASSIFIER_VERSION
    assert REGISTRATION["contract"] == "registration"
    assert len(REGISTRATION["declared_invariants"]) == 5
    with pytest.raises(TypeError):
        REGISTRATION["contract"] = "qualification"   # type: ignore[index]
    # DECLARED, never read into a branch.
    source = (SRC / "executive" / "stake_classifier.py").read_text(
        encoding="utf-8")
    assert "if REGISTRATION" not in source
    assert "REGISTRATION[" not in source


def test_a_held_condition_always_carries_its_evidence(tmp_path):
    """A held condition with no evidence would be an assertion, which is the
    thing this module exists to refuse."""
    predictions = PredictionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    predictions.commit("x", claim_refs=("CLM-0001",))
    result = _classify("CLM-0001", predictions=predictions)
    for condition in result.conditions:
        if condition.held:
            assert condition.consulted_record_ids
