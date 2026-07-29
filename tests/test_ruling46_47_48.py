"""
test_ruling46_47_48.py - THE MUTATION-SURFACE AUDIT (2026-07-29).

Three defects on the three paths by which doctrine content can change, plus the
three riders landed with them.

    RULING 46  A BIRTH CANNOT SILENTLY REPLACE A LIVING BELIEF.
               Ruling 24 gave `mutate_doctrine` a pre-flight and found, while
               ruling it, that an id collision with a live doctrine "would have
               SILENTLY CLOBBERED it". `birth_doctrine` never got that check, so
               the same defect sat on the other doctrine-entry path in its WORSE
               form: a mutation at least fossilizes what it displaces.

    RULING 47  A REVERSION IS A COUNTER-MUTATION.
               `revert` set `record.reverted = True` FIRST, then hand-rolled a
               write token outside `authorize()` (no ceiling, no CAE entry, no
               settle obligation, no pre-flight), then committed the pre-state
               UNDER THE FOSSILIZED ANCESTOR'S ID - which `Codex.commit` refuses.
               So it was not merely unaudited: it was NON-FUNCTIONAL, and it
               falsified its own record on the way to failing.

    RULING 48  A STRUCTURAL VIOLATION IS NOT BACK-PRESSURE.
               `DEE._approve` caught `Exception`. Two of the things it caught are
               the executor answering the gate ("ceiling spent", "10.G target")
               and fermenting is right. Everything else was a deliberate guard
               being converted into a fermentation reason string, three frames
               below the Ruling 25 taxonomy built to receive it.

RED-WATCHED AT `70ffb51` IN A DETACHED WORKTREE, per Ruling 17 - no lexical
proxy stands in for a runtime guarantee where a runtime witness is available.
The outcome of each watch is recorded in the test that was watched.
"""

import ast
from datetime import datetime

import pytest

from src.aurea_core import AureaCore, STRUCTURAL_VIOLATIONS
from src.doctrine.cae import CAE
from src.doctrine.codex import Codex, CodexWriteViolation
from src.doctrine.dee import DEE, SUSTAIN_CYCLES, _Watched
from src.expansion.nova import FERMENTATION_ELIGIBILITY_CYCLES, FermentationStatus
from src.doctrine.mutation_proof import (
    CMTE_FAILURE_LABELS, CriterionResult, all_criteria_absent,
)
from src.expansion.sae import (
    SAE, CeilingExceeded, MutationPreflightViolation, MutationClass,
    RevertOutcome, RevertRefusal,
)
from src.output.ore import OutputPath
from src.utils.models import Doctrine

from tests.proof_support import minimal_proof


# =====================================================================
# HARNESS
# =====================================================================

def _sae(tmp_path, doctrines=("D-1",), ceiling=3):
    """A Codex + CAE + SAE over isolated paths. No stubs: every pin below drives
    the real `authorize -> _audit -> CAE.record` chain, because the whole subject
    of Ruling 47 is which parts of that chain a reversion skipped."""
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.doctrines.clear()
    for i, doctrine_id in enumerate(doctrines):
        codex.doctrines[doctrine_id] = Doctrine(
            id=doctrine_id, name=f"Original {i}",
            description=f"the belief {doctrine_id} before",
            scar_links=[f"scar-{i}"], tca_tags=[f"tag-{i}"],
            created_at=datetime.now())
    cae = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    sae = SAE(codex=codex, cae=cae, ceiling=ceiling,
              runtime_path=str(tmp_path / "sae.json"))
    return codex, sae, cae


def _mutate(sae, ancestor_id, successor_id, lineage):
    """One real mutation. Returns its authorization id."""
    sae.mutate_doctrine(
        ancestor_id,
        Doctrine(id=successor_id, name="Successor",
                 description="the belief after", created_at=datetime.now()),
        collapse_lineage=lineage, proof=minimal_proof("test_ruling46_47_48"))
    return sae.history[-1].authorization_id


# =====================================================================
# RULING 46 - THE BIRTH PRE-FLIGHT
# =====================================================================

def test_a_birth_over_a_live_id_refuses_and_costs_nothing(tmp_path):
    """THE HEADLINE OF RULING 46, IN ITS FORCING FORM.

    RED AT `70ffb51`, and not by raising differently - BY NOT RAISING AT ALL.
    Watched there: `birth_doctrine` returned the new doctrine, `codex.doctrines`
    held it under the live id, and the belief that was there was GONE - not
    fossilized, not lineaged, not logged. `epoch_count` had gone 0 -> 1 and a
    permanent CAE entry recorded a mutation that had destroyed a doctrine.

    THREE THINGS ARE MEASURED, not one. Asserting only the raise would pass
    against an implementation that refused AFTER spending the slot and writing
    the ledger entry - which is precisely the Ruling 24 boundary this ruling
    extends to the second entry path, and precisely what `Codex.commit`'s
    backstop already did for the fossil case.
    """
    codex, sae, cae = _sae(tmp_path)
    budget_before = sae.epoch_count
    history_before = len(sae.history)
    ledger_before = len(cae.read_all())
    original = codex.get("D-1")

    with pytest.raises(MutationPreflightViolation) as exc:
        sae.birth_doctrine(
            Doctrine(id="D-1", name="Impostor", description="no collapse behind me",
                     created_at=datetime.now()),
            collapse_lineage="scar-0")

    assert "already a LIVE doctrine" in str(exc.value)

    # THE BELIEF IS UNTOUCHED.
    survivor = codex.get("D-1")
    assert survivor.name == original.name
    assert survivor.description == original.description
    assert "D-1" not in codex.fossils, (
        "a refused birth must not fossilize anything either - nothing happened")

    # AND IT COST NOTHING. Pre-spend refusal, per Ruling 24's boundary.
    assert sae.epoch_count == budget_before, (
        "a refused birth must not spend a ceiling slot")
    assert len(sae.history) == history_before
    assert len(cae.read_all()) == ledger_before, (
        "a refused birth must not write a permanent audit entry for a "
        "mutation that did not happen")


def test_a_birth_over_a_fossil_id_refuses_before_the_ceiling_not_after(tmp_path):
    """The hoisted backstop. `Codex.commit` ALREADY refused this (Ruling 18) and
    still does - what Ruling 46 changes is WHEN.

    RED AT `70ffb51`: the raise there was `CodexWriteViolation` from inside
    `commit`, AFTER `authorize()` had incremented `epoch_count` and appended a
    CAE entry. A structurally certain refusal cost a mutation from the epoch's
    budget to discover.
    """
    codex, sae, cae = _sae(tmp_path)
    _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")
    assert "D-1" in codex.fossils, "precondition: the ancestor is ⊗-fossilized"

    budget_before = sae.epoch_count
    ledger_before = len(cae.read_all())

    with pytest.raises(MutationPreflightViolation) as exc:
        sae.birth_doctrine(
            Doctrine(id="D-1", name="Risen", created_at=datetime.now()),
            collapse_lineage="scar-0")
    assert "⊗-fossilized" in str(exc.value)

    assert sae.epoch_count == budget_before
    assert len(cae.read_all()) == ledger_before


def test_the_commit_backstop_is_still_there(tmp_path):
    """DEFENCE IN DEPTH IS THE POINT. Ruling 46 does not replace Ruling 18's
    guard, and a future caller reaching `commit` by another route must still be
    refused. Driven at the store, below SAE, so the pre-flight cannot satisfy it.
    """
    codex, sae, _ = _sae(tmp_path)
    _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    auth = sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-0", "probe")
    with pytest.raises(CodexWriteViolation):
        codex.commit(Doctrine(id="D-1", name="Risen", created_at=datetime.now()), auth)


def test_an_ordinary_birth_still_births_and_still_audits(tmp_path):
    """The guard must never fire on the legitimate path - which is what a correct
    guard looks like (Ruling 24's own words)."""
    codex, sae, cae = _sae(tmp_path)
    born = sae.birth_doctrine(
        Doctrine(id="D-new", name="Born", created_at=datetime.now()),
        collapse_lineage="scar-0")

    assert born.id == "D-new"
    assert codex.get("D-new") is not None
    assert "scar-0" in born.scar_links
    assert sae.history[-1].cae_id is not None
    assert any(e["target"] == "D-new" for e in cae.read_all())


# =====================================================================
# RULING 47 - REVERSION AS COUNTER-MUTATION
# =====================================================================

def test_a_reversion_mints_a_new_id_and_the_whole_chain_stays_visible(tmp_path):
    """THE HEADLINE OF RULING 47.

    RED AT `70ffb51`, and it did not fail an assertion - it RAISED
    `CodexWriteViolation` out of `revert` itself, because the old body committed
    `record.pre_state` under the ancestor's own id and that id had just been
    ⊗-fossilized by the mutation being reverted. Reversion was non-functional for
    every doctrine mutation there has ever been.

    ANCESTOR -> SUCCESSOR -> REVERSION, end to end: she can see that she went
    there and came back, which is exactly what Rulings 18/19 forbid her hiding by
    restoring a dead name.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    out = sae.revert(auth)

    assert isinstance(out, RevertOutcome)
    assert out.performed is True
    assert bool(out) is True, "truthiness is `performed`, for callers migrating"

    # A NEW ID. Never the ancestor's (that is the revival Ruling 18 forbids),
    # never the successor's (Ruling 24 (i)).
    assert out.doctrine.id not in ("D-1", "D-1::nova::NE-0001")
    assert out.doctrine.id == "D-1::revert::" + auth

    # THE CONTENT CAME BACK.
    assert out.doctrine.name == "Original 0"
    assert out.doctrine.description == "the belief D-1 before"
    assert "tag-0" in out.doctrine.tca_tags

    # THE SUCCESSOR IS ⊗'d, THE ANCESTOR STAYS DEAD.
    assert sorted(codex.fossils) == ["D-1", "D-1::nova::NE-0001"]
    assert sorted(codex.doctrines) == [out.doctrine.id]

    # THE FULL CHAIN. Pinned rather than assumed - it is produced by
    # `mutate_doctrine`'s existing lineage mechanics, and if those change this
    # reddens instead of the history silently flattening.
    assert out.doctrine.mutation_lineage == ["D-1", "D-1::nova::NE-0001"]
    assert out.reverted_from == "D-1::nova::NE-0001"
    assert out.restored_from == "D-1"


def test_a_reversion_spends_exactly_one_slot_and_writes_one_cae_entry(tmp_path):
    """RED AT `70ffb51` IN BOTH HALVES, and this is the substance of the ruling
    rather than the visible part.

    The old body hand-rolled a `MutationAuthorization` with
    `mutation_class="rollback"`, bypassing `authorize()` completely. So a
    reversion spent NO ceiling slot, wrote NO CAE entry, and recorded NO settle
    obligation - a doctrine write executed with a token SAE minted outside its
    own gate. Ruling 5's executor privilege used to route around Ruling 34's
    budget and canon 3a:111 together.
    """
    codex, sae, cae = _sae(tmp_path, ceiling=99)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    budget_after_mutation = sae.epoch_count
    ledger_after_mutation = len(cae.read_all())

    sae.revert(auth)

    assert sae.epoch_count == budget_after_mutation + 1, (
        "a reversion CHANGES what AUREA believes; that the content was once "
        "hers does not make the change free")
    assert len(cae.read_all()) == ledger_after_mutation + 1, (
        "3a:111 - no doctrine mutated without a CAE entry, reversions included")

    # THE SETTLE OBLIGATION. `authorize` routes every spend through `_touch`,
    # so the slot the reversion spent is visible to the epoch's close condition.
    assert "scar-0" in sae.touched_lineages

    entry = cae.read_all()[-1]
    assert entry["event"] == "mutate_doctrine"
    assert entry["target"] == "D-1::nova::NE-0001", (
        "the reversion mutates the SUCCESSOR - that is the doctrine being changed")
    assert entry["proof"]["contradiction_core"]["reverted_authorization"] == auth


def test_a_refused_reversion_leaves_reverted_False(tmp_path):
    """THE FORCING PIN. Ruling 47's first defect, isolated.

    RED AT `70ffb51`: watched there, `record.reverted` was **True** after the
    call raised. The old body wrote the flag before attempting any work, so a
    caller that swallowed the exception read a history in which the mutation had
    been undone while the Codex still held the successor. A rollback tracker
    whose flag means nothing is worse than no tracker - a forensic record is
    consulted precisely when memory is gone.

    The ceiling is the instrument because it is the one refusal that arrives
    from INSIDE `mutate_doctrine` after the reversion has been fully built:
    everything upstream of it succeeded, so nothing but ordering can save the
    flag.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=3)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")
    # Spend the rest of the epoch on a different counted class.
    sae.authorize_module_generation("mod-x", "scar-0")
    sae.authorize_module_generation("mod-y", "scar-0")
    assert sae.epoch_count == sae.ceiling, "precondition: budget spent"

    live_before = sorted(codex.doctrines)
    fossils_before = sorted(codex.fossils)

    with pytest.raises(CeilingExceeded):
        sae.revert(auth)

    record = next(r for r in sae.history if r.authorization_id == auth)
    assert record.reverted is False, (
        "a reversion that did not happen must not be recorded as having "
        "happened - the flag is written only after the commit returns")

    # And nothing moved in the store either.
    assert sorted(codex.doctrines) == live_before
    assert sorted(codex.fossils) == fossils_before


def test_the_ancestor_id_is_never_resurrected_by_a_reversion(tmp_path):
    """Rulings 18/19 hold THROUGH the rollback path. Restoring CONTENT is
    legitimate; restoring a fallen NAME is the revival Option B settled.

    This is also the pin that would have caught the old implementation from the
    other direction: it tried to do exactly this, and `commit` stopped it.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    sae.revert(auth)

    assert "D-1" in codex.fossils
    assert "D-1" not in codex.doctrines
    assert codex.get("D-1") is None, (
        "the fallen id stays permanently dead; only its content returns")


def test_a_stale_successor_refuses_typed(tmp_path):
    """A -> B -> C. Reverting the A -> B mutation is a claim about HISTORY, not a
    change to the present, and it is refused.

    THIS IS WHY `live_successors` WAS THE WRONG INSTRUMENT and a new one was
    added. Witnessed in this exact configuration: `live_successors("D-1")`
    returns `["gen-C"]`, because lineage ACCUMULATES and C carries the whole
    chain (Ruling 36 depends on that and it is not changing). A reversion built
    on it would have found a live doctrine, concluded the mutation was still
    current, and counter-mutated C - silently discarding B -> C. Asserted here so
    the divergence is on the record rather than in a comment.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    first = _mutate(sae, "D-1", "gen-B", "scar-0")
    _mutate(sae, "gen-B", "gen-C", "scar-0")

    assert codex.live_successors("D-1") == ["gen-C"], (
        "Ruling 36's descendant question, unchanged")
    assert codex.direct_successors("D-1") == [], (
        "Ruling 47's immediate-successor question: gen-B is a fossil")
    assert codex.fossil_direct_successors("D-1") == ["gen-B"]

    budget_before = sae.epoch_count
    out = sae.revert(first)

    assert out.performed is False
    assert out.refusal is RevertRefusal.SUCCESSOR_NOT_LIVE
    assert "gen-B" in out.reason
    assert sorted(codex.doctrines) == ["gen-C"], "the present is untouched"
    assert sae.epoch_count == budget_before, "a refusal spends nothing"
    assert sae.revert_refusals[-1]["refusal"] == "successor_not_live", (
        "Ruling 23: unresolved pressure never leaves silently")


def test_two_live_direct_successors_are_refused_not_chosen_between(tmp_path):
    """AMBIGUITY IS NOT RESOLVED BY PICKING (Ruling 42's discipline: zero or
    several -> nothing is chosen).

    A doctrine is ⊗-fossilized by the mutation that succeeds it, so it can only
    be mutated once and this state should not exist. The branch is defensive -
    but "should not exist" is what `Codex.fossils` was before Ruling 35, and a
    defensive branch nothing exercises is a branch nobody knows the behaviour of.
    ADDED AFTER A SURVIVING MUTANT (`if len(live) > 1:` -> `if False:` passed the
    whole file): the state is constructed directly in the store, which is the
    only way to reach it and is exactly what makes it worth pinning.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    # A SECOND live doctrine claiming the same immediate ancestor.
    codex.doctrines["D-1::rogue"] = Doctrine(
        id="D-1::rogue", name="Also claims D-1", mutation_lineage=["D-1"],
        created_at=datetime.now())
    assert codex.direct_successors("D-1") == ["D-1::nova::NE-0001", "D-1::rogue"]

    budget_before = sae.epoch_count
    out = sae.revert(auth)

    assert out.performed is False
    assert out.refusal is RevertRefusal.SUCCESSOR_AMBIGUOUS
    assert "does not choose" in out.reason
    assert sae.epoch_count == budget_before
    assert "D-1::nova::NE-0001" in codex.doctrines, "neither was counter-mutated"
    assert "D-1::rogue" in codex.doctrines


def test_reverting_a_birth_returns_a_typed_refusal_naming_the_open_ruling(tmp_path):
    """RED AT `70ffb51`: the old body returned a bare `None` here - and the SAME
    bare `None` for "no such authorization". Two causally unrelated situations,
    one indistinguishable signal, which is Ruling 29's defect inside a return
    value. The `None` is also what let the birth-reversion semantics stay an
    invisible question rather than a declared one.

    v1 IS THE REFUSAL. Un-birthing would ⊗-mark a doctrine that never collapsed,
    and what the Fossil Layer would then be recording is not this ruling's to
    decide.
    """
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    sae.birth_doctrine(Doctrine(id="D-new", name="Born", created_at=datetime.now()),
                       collapse_lineage="scar-0")
    birth_auth = sae.history[-1].authorization_id

    out = sae.revert(birth_auth)

    assert out.performed is False
    assert bool(out) is False
    assert out.refusal is RevertRefusal.BIRTH_NOT_REVERTIBLE
    assert "OPEN RULING" in out.reason
    assert codex.get("D-new") is not None, "nothing was un-born"
    assert "D-new" not in codex.fossils


def test_the_refusal_causes_are_distinguishable_from_each_other(tmp_path):
    """Ruling 29, applied to five causes. The old code answered three of these
    with the same `None`."""
    codex, sae, _ = _sae(tmp_path, ceiling=99)

    absent = sae.revert("AUTH-does-not-exist")
    assert absent.refusal is RevertRefusal.NO_SUCH_RECORD

    reflex = sae.mutate_reflex("R-1", {"tone": "quiet"}, "scar-0")
    not_ours = sae.revert(reflex.authorization_id)
    assert not_ours.refusal is RevertRefusal.NOT_A_DOCTRINE_MUTATION
    assert "Reflex Grid" in not_ours.reason, (
        "Ruling 1: reverting a reflex change is a request to its owner")

    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")
    assert sae.revert(auth).performed is True
    again = sae.revert(auth)
    assert again.refusal is RevertRefusal.NO_SUCH_RECORD, (
        "one authorization, one reversion - the spent record is not found again")

    kinds = {r["refusal"] for r in sae.revert_refusals}
    assert kinds == {"no_such_record", "not_a_doctrine_mutation"}


def test_the_reversion_proof_records_absent_criteria_not_passed_ones(tmp_path):
    """No CMTE gate stood in front of a reversion, and the proof says so.

    Recording PASS here would put "all five criteria satisfied" into the audit
    ledger of a mutation that consulted none of them - Ruling 45's fabricated
    argument, in `src/` rather than in the harness. `all_criteria_absent()` is
    incapable of expressing anything stronger, which is why it is allowed to
    exist where a `preserved_invariants` default is not.
    """
    codex, sae, cae = _sae(tmp_path, ceiling=99)
    auth = _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")
    sae.revert(auth)

    proof = sae.history[-1].proof
    assert proof is not None
    assert set(proof.preserved_invariants) == set(CMTE_FAILURE_LABELS)
    assert all(r is CriterionResult.ABSENT
               for r in proof.preserved_invariants.values())

    # The argument names what it is undoing, and the residue names what the
    # reversion does NOT resolve.
    assert proof.contradiction_core["reverted_authorization"] == auth
    assert proof.contradiction_core["counter_mutating"] == "D-1::nova::NE-0001"
    assert any("does not revert the pressure" in r
               for r in proof.unresolved_residue), (
        "undoing the change does not undo the pressure that forced it")

    # `scar_lineage` comes from the RECORD - nothing coined.
    assert "scar-0" in proof.scar_lineage


def test_the_criterion_names_have_exactly_one_definition():
    """RULING 47's small consolidation. `CMTE.FAILURE_LABELS` was the definition
    and `tests/proof_support.py` hand-spelled a second copy; SAE needed a third.
    They are now one object, so a rename cannot leave two of the three asserting
    the old names."""
    from src.doctrine.dee import CMTE
    assert CMTE.FAILURE_LABELS is CMTE_FAILURE_LABELS
    assert set(all_criteria_absent()) == set(CMTE_FAILURE_LABELS)
    assert len(CMTE_FAILURE_LABELS) == 5, "all five criteria, not a subset"


def test_sae_holds_no_hand_rolled_write_token_outside_authorize(tmp_path):
    """AST. The structural half of Ruling 47, because a docstring saying "route
    through authorize()" is a request for restraint (CLAUDE.md section 3) and the
    old `revert` is proof that the request fails.

    Every `MutationAuthorization(...)` construction in `sae.py` must sit in
    `authorize`, `authorize_module_retirement` (ceiling-EXEMPT by 5b T4-03) or
    `_reissue` (the paired ⊗ write of ONE mutation event). A fourth site is a
    Codex write with a token minted outside SAE's own gate - which is exactly
    what `revert` did.
    """
    source = (Path_of_sae := __import__("src.expansion.sae", fromlist=["x"]).__file__)
    with open(source, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    SANCTIONED = {"authorize", "authorize_module_retirement", "_reissue"}
    offenders = []
    for func in [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        for node in ast.walk(func):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "MutationAuthorization"
                    and func.name not in SANCTIONED):
                offenders.append(f"{func.name}:{node.lineno}")

    assert not offenders, (
        f"MutationAuthorization is constructed outside {sorted(SANCTIONED)} at "
        f"{offenders}. A write token minted outside `authorize()` skips the "
        f"ceiling, the CAE entry and the settle obligation - Ruling 47's defect."
    )


def test_the_ast_scanner_catches_the_pre_ruling_47_code():
    """Ruling 32's answer to the vacuous-pin problem: feed the scanner the exact
    forbidden code and a benign control, so a scan that has stopped scanning
    fails HERE rather than passing quietly forever."""
    FORBIDDEN = '''
class SAE:
    def revert(self, authorization_id):
        auth = MutationAuthorization(
            authorization_id=new_authorization_id(),
            executor=self.EXECUTOR,
            mutation_class="rollback",
            collapse_lineage=record.collapse_lineage,
            epoch=self.epoch,
        )
        return self.codex.commit(record.pre_state, auth)
'''
    BENIGN = '''
class SAE:
    def revert(self, authorization_id):
        return self.mutate_doctrine(successor_id, new_form,
                                    collapse_lineage=lineage, proof=proof)
'''

    def offenders_in(src):
        tree = ast.parse(src)
        found = []
        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            for node in ast.walk(func):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "MutationAuthorization"
                        and func.name not in {"authorize",
                                              "authorize_module_retirement",
                                              "_reissue"}):
                    found.append(func.name)
        return found

    assert offenders_in(FORBIDDEN) == ["revert"], "the scanner must SEE the defect"
    assert offenders_in(BENIGN) == [], "and must not flag the fix"


# =====================================================================
# RULING 48 - THE EXPECTED-REFUSAL PARTITION
# =====================================================================

STRAINED = "Doctrine-3"          # test_docket_n's DOCTRINE_A, and for its reason
THIRD_SCAR = "Δ42"               # a real seed scar (Doctrine-0.1 carries it)


def _armed_with_an_occupied_successor_id():
    """A live `AureaCore` armed with a REAL structural landmine, in the exact
    shape `test_docket_n._armed_pipeline` established for Ruling 25: nothing is
    patched or mocked, and the guard that fires is a deliberate one firing on the
    real path.

    THE LANDMINE: Nova mints its proposal id as `{doctrine_id}::nova::{echo.id}`,
    which is deterministic once the echo exists. So a LIVE doctrine is planted
    under that exact id BEFORE the pass runs. `SAE._preflight`'s third check -
    Ruling 24's "an id collision with a LIVE doctrine would have SILENTLY
    CLOBBERED it" - then fires inside the real `mutate_doctrine`, reached through
    the real `DEE._approve`, during a normal `process_input`.

    `Doctrine-3` IS THE STRAINED DOCTRINE FOR A VERIFIED REASON, recorded in
    `test_docket_n`: of the eight seed doctrines, only its own content SCARS
    through the real EchoNet, so its echo reaches MUTATED organically through
    `_nova_route_collapse` with no verdict mocked. An invented doctrine's
    description does not scar - checked by execution while building this, and its
    echo went DORMANT -> DECAYING and could never author.

    TWO ARRANGED FACTS, both real states rather than inflated magnitudes:

      THE DMW SLOT is seeded at pressure 0.9 / 3 sustained cycles. This is
      `test_docket_n._seed_strain` verbatim - "the one controlled seam, identical
      to test_nova_stage2a/2b's pattern: a real sustained-strain slot in DEE's
      DMW watch."

      A THIRD SCAR LINK is added to `Doctrine-3` (it seeds with two). This is
      what makes DRPAS flag it every pass - canon's Scar Bloom Convergence is
      `>= 3` - and being flagged is what stops `DMW.observe` HALVING the seeded
      slot's pressure below the critical bar each cycle. Three scars is a real
      configuration, not a number invented to clear a threshold: no pressure
      value is touched anywhere, and the halving it avoids is the documented
      reason `test_nova_stage2b` could not drive this gate un-spied.
    """
    core = AureaCore()
    core.codex.doctrines[STRAINED].scar_links.append(THIRD_SCAR)
    core.dee.dmw.queue[STRAINED] = _Watched(
        doctrine_id=STRAINED, pressure=0.9, sustained_cycles=SUSTAIN_CYCLES)

    core._nova_cycle([])
    echo = next(e for e in core.nova.echo_index.values()
                if e.origin_id == STRAINED)
    for _ in range(FERMENTATION_ELIGIBILITY_CYCLES + 3):
        if echo.status is FermentationStatus.MUTATED:
            break
        core._nova_cycle([])
    assert echo.status is FermentationStatus.MUTATED, (
        "precondition: Doctrine-3's own content survived collapse organically")
    assert echo.scar_links, "precondition: G2 requires a scar-linked echo"

    occupied_id = f"{STRAINED}::nova::{echo.id}"
    core.codex.doctrines[occupied_id] = Doctrine(
        id=occupied_id, name="Occupant",
        description="a living belief already using the id Nova is about to mint",
        created_at=datetime.now())
    return core, occupied_id


def _drive_until_mutation_attempt(core):
    """Real passes through `process_input` until the mutation is attempted."""
    results = []
    for _ in range(SUSTAIN_CYCLES + 3):
        results.append(core.process_input("Honesty is pointless.", source="test"))
        if results[-1].get("structural_violation"):
            break
    return results


def test_a_preflight_violation_inside_dee_reaches_the_structural_surface():
    """THE FORCING PIN FOR RULING 48.

    RED AT `70ffb51`: watched there, the identical configuration produced NO
    structural violation. `_approve`'s `except Exception` caught the
    `MutationPreflightViolation`, set `Verdict.FERMENT`, wrote "SAE refused
    execution: ..." into a ruling and suspended the doctrine to the Veiled
    Thread. AUREA answered the input normally. A guard that makes an id collision
    UNEXECUTABLE fired, and the observable result was a doctrine recorded as
    merely unresolved.

    Ruling 25 built this surface - a loud field, suppressed output, a durable
    record - and this clause was what stood in front of it for every mutation.
    """
    core, occupied_id = _armed_with_an_occupied_successor_id()
    results = _drive_until_mutation_attempt(core)

    violated = [r for r in results if r.get("structural_violation")]
    assert violated, (
        "a MutationPreflightViolation raised inside dee.cycle must surface as a "
        "structural violation, not ferment")

    result = violated[-1]
    assert result["structural_violation"]["type"] == "MutationPreflightViolation"
    assert result["expression_verdict"] is not None
    assert result["output_blocked"] is True, (
        "Ruling 25: she does not answer as though nothing happened when her own "
        "guard fired")
    assert core.codex.get(occupied_id).name == "Occupant", (
        "and the occupied doctrine is untouched - the guard fired BEFORE the "
        "write, which is the whole of Ruling 24's pre-flight and the belief this "
        "collision would otherwise have replaced")
    assert occupied_id not in core.codex.fossils


def test_the_structural_violation_is_durably_recorded():
    """The record is the point (Ruling 25): the process does not crash, because
    crashing would destroy it."""
    core, occupied_id = _armed_with_an_occupied_successor_id()
    _drive_until_mutation_attempt(core)

    assert core.structural_violations, "recorded in memory"
    assert any(v["type"] == "MutationPreflightViolation"
               for v in core.structural_violations)


def test_a_spent_ceiling_still_ferments_and_now_records_its_type(tmp_path):
    """THE OTHER HALF, and the half that must NOT change. `CeilingExceeded` is
    the executor answering the gate's question through its own authority, and
    fermenting is exactly right - the doctrine's pressure is real and unresolved.

    What is new is `refusal_type`: `reason` carried the exception's MESSAGE and
    nothing else, so telling a spent ceiling from a 10.G exclusion meant
    substring-matching prose written for a human.
    """
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    codex.doctrines.clear()
    codex.doctrines["D-1"] = Doctrine(
        id="D-1", name="Original", description="strained",
        scar_links=["Δ-1", "Δ-2", "Δ-3"], created_at=datetime.now())
    cae = CAE(ledger_path=str(tmp_path / "cae.jsonl"))
    sae = SAE(codex=codex, cae=cae, ceiling=1,
              runtime_path=str(tmp_path / "sae.json"))
    dee = DEE(codex=codex, sae=sae, cae=cae)

    sae.authorize_module_generation("mod-x", "Δ-1")   # spends the only slot
    assert sae.epoch_count == sae.ceiling

    proposal = Doctrine(id="D-1::nova::NE-0001", name="Successor",
                        created_at=datetime.now())
    rulings = []
    for _ in range(SUSTAIN_CYCLES + 1):
        rulings = dee.cycle(signals={"D-1": {"pressure": 0.95, "drpe": True}},
                            proposals={"D-1": proposal})
        if any(r.refusal_type for r in rulings):
            break

    refused = [r for r in rulings if r.refusal_type]
    assert refused, "the ceiling refusal must still be caught and fermented"
    assert refused[-1].refusal_type == "CeilingExceeded"
    assert refused[-1].verdict.value == "ferment"
    assert refused[-1].executed_by is None
    assert "D-1" in codex.doctrines, "nothing mutated"


def test_the_approve_except_clause_names_exactly_the_closed_pair():
    """AST. The tuple is CLOSED and ENUMERATED on `STRUCTURAL_VIOLATIONS`'s own
    terms - concrete types, never a base class, and a third member is a manifest
    decision. Widening this back to `Exception` is the regression Ruling 48
    exists to prevent, and it is a one-word edit.
    """
    import src.doctrine.dee as dee_mod
    with open(dee_mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    approve = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_approve")
    handlers = [h for n in ast.walk(approve) if isinstance(n, ast.Try)
                for h in n.handlers]
    assert len(handlers) == 1, "_approve has exactly one except clause"

    caught = handlers[0].type
    assert isinstance(caught, ast.Tuple), (
        "the caught type must be an explicit TUPLE of concrete exception types")
    names = sorted(e.id for e in caught.elts if isinstance(e, ast.Name))
    assert names == ["CeilingExceeded", "ExclusionViolation"], (
        f"_approve catches {names}; Ruling 48 rules it to exactly the closed "
        f"pair of EXPECTED executor refusals. Anything else is a structural "
        f"violation and must PROPAGATE to the Ruling 25 taxonomy.")


def test_the_structural_taxonomy_still_carries_the_mutation_guards():
    """The types Ruling 48 lets through must be the ones `process_input` is ready
    to receive. Without this, narrowing the catch would route a guard into
    `errors` instead - Ruling 25's defect reached by a different road."""
    names = {t.__name__ for t in STRUCTURAL_VIOLATIONS}
    for required in ("MutationPreflightViolation", "CodexWriteViolation",
                     "CeilingExceeded", "ExclusionViolation"):
        assert required in names
    for t in STRUCTURAL_VIOLATIONS:
        others = [o for o in STRUCTURAL_VIOLATIONS if o is not t]
        assert not any(issubclass(o, t) for o in others), (
            f"{t.__name__} is a base class of another member - the tuple is "
            f"CLOSED and its members are concrete (Ruling 25)")


# =====================================================================
# RIDER R2 - A SUSPENDED CALL IS NOT A SYMBOLIC CYCLE
# =====================================================================

def test_a_suspended_pass_ages_nothing():
    """WITNESSED, NOT ASSERTED: the three clocks are READ before and after.

    HONESTLY REPORTED: this pin is GREEN AT `70ffb51`. The freeze is not new
    behaviour - the suspension gate has always returned before the three
    advances. What was missing was anyone having declared it INTENDED, which is
    the difference between an invariant and an accident nobody has audited. The
    pin's job is forward-looking: moving `tcaml.tick()` / `sae.advance_cycle()` /
    `sml.advance_cycle()` above the gate, or adding a fourth clock below it,
    turns this red.

    The freeze that matters most is SCAR COOLING. Cooling emits
    `scar_fermentation`, which CLOSES AN EPOCH and restores mutation budget
    (Ruling 37). A suspended AUREA accruing quiet cycles would metabolise her way
    to a fresh ceiling while suspended - budget earned by not running, which is
    Ruling 34's restart absolution wearing suspension's clothes.

    ONE OF THE THREE CLOCKS IS EQUIVALENT-TODAY, and it is recorded here rather
    than left for the next reader to rediscover. Hoisting `tcaml.tick()` or
    `sml.advance_cycle()` above the gate turns this test RED (verified by
    mutation). Hoisting `sae.advance_cycle()` does NOT, and the reason is
    structural: a suspended pass never sets `_cycle_blocked` or `_cycle_executed`,
    so `advance_cycle`'s three-case logic finds nothing to close and changes no
    field. The mutant is EQUIVALENT with respect to SAE's state - not a gap in
    this assertion, and it becomes distinguishable the moment SAE's clock gains
    any unconditional per-cycle effect. The call still belongs below the gate, and
    it is the declaration above it in `aurea_core.py` that says so.
    """
    core = AureaCore()
    core.processing_suspended = True
    core.suspension_reason = "R2 freeze witness"

    before = {
        "tcaml_cycle": core.tcaml._cycle,
        "sae_blocked": core.sae.consecutive_blocked_cycles,
        "sae_epoch": core.sae.epoch,
        "sae_epoch_count": core.sae.epoch_count,
        "sae_saturation_surfaced": core.sae.saturation_surfaced,
        "sml_quiet": dict(core.sml._quiet),
        "sml_transitions": len(core.sml.transitions),
        "sml_settled": len(core.sml.settle_events),
    }

    for _ in range(12):
        result = core.process_input("input arriving while she is not running")
        assert result["output_blocked"] is True

    after = {
        "tcaml_cycle": core.tcaml._cycle,
        "sae_blocked": core.sae.consecutive_blocked_cycles,
        "sae_epoch": core.sae.epoch,
        "sae_epoch_count": core.sae.epoch_count,
        "sae_saturation_surfaced": core.sae.saturation_surfaced,
        "sml_quiet": dict(core.sml._quiet),
        "sml_transitions": len(core.sml.transitions),
        "sml_settled": len(core.sml.settle_events),
    }

    assert after == before, (
        f"a mind that is not running does not age its wounds. Twelve suspended "
        f"passes moved: "
        f"{ {k: (before[k], after[k]) for k in before if before[k] != after[k]} }")


def test_resuming_continues_the_clocks_it_did_not_skip():
    """The other half of the R2 declaration (marked per Ruling 4: the freeze is
    DECLARED and BOUNDED, not unbounded). Resumption picks up from the ordinal
    each clock held - nothing is skipped and nothing is caught up."""
    core = AureaCore()
    core.process_input("one live pass")
    at_suspend = core.tcaml._cycle

    core.processing_suspended = True
    for _ in range(5):
        core.process_input("suspended")
    assert core.tcaml._cycle == at_suspend, "frozen"

    core.resume_processing()
    core.process_input("one more live pass")
    assert core.tcaml._cycle == at_suspend + 1, (
        "the five suspended passes are not later counted as cycles")


# =====================================================================
# RIDER R3 - ATOMIC SNAPSHOT WRITES
# =====================================================================

def test_no_durable_snapshot_opens_its_final_path_in_write_mode():
    """THE STRUCTURAL SWEEP. RED AT `70ffb51` with THIRTEEN offenders.

    Mode "w" TRUNCATES the destination before the first byte of new content is
    written, so a process killed in that window leaves a JSON prefix - neither
    the old state nor the new one. On `sae_epoch.json` that is not merely lost
    state: `SAE.load` records the corrupt file and constructs AT DEFAULTS, which
    means `epoch_count=0`. A truncating write on that one file was a route to a
    FRESH MUTATION CEILING.

    APPEND-ONLY LOGS ARE EXEMPT and this scan says so by only looking at "w": a
    torn append damages one line and every reader already drops it by floor
    semantics; a torn snapshot destroys everything.
    """
    import pathlib
    src_root = pathlib.Path(__import__("src").__file__).parent
    offenders = []
    for path in sorted(src_root.rglob("*.py")):
        if path.name == "atomic_write.py":
            continue      # the helper itself opens the TEMP file in "w" - the point
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                continue
            modes = [a.value for a in node.args[1:2]
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            modes += [kw.value.value for kw in node.keywords
                      if kw.arg == "mode" and isinstance(kw.value, ast.Constant)]
            if any("w" in m for m in modes):
                offenders.append(f"{path.relative_to(src_root)}:{node.lineno}")

    assert not offenders, (
        f"durable snapshot written with a truncating open() at {offenders}. "
        f"Route it through src/utils/atomic_write.atomic_write_json - a snapshot "
        f"is replaced whole or not at all.")


def test_an_atomic_write_lands_complete_and_leaves_no_temp_behind(tmp_path):
    """The behavioural witness. The structural scan above proves nobody
    truncates; this proves the replacement actually works, and that a FAILED
    write leaves the previous snapshot byte-intact."""
    from src.utils.atomic_write import atomic_write_json, atomic_write_text

    target = tmp_path / "nested" / "state.json"
    atomic_write_json(target, {"epoch": 1, "touched": ["scar-a"]}, indent=2)
    assert target.exists()
    original = target.read_bytes()

    atomic_write_json(target, {"epoch": 2, "touched": ["scar-a", "scar-b"]}, indent=2)
    import json as _json
    assert _json.loads(target.read_text(encoding="utf-8"))["epoch"] == 2
    assert list(target.parent.glob("*.tmp")) == [], "no temp file survives a success"

    # A payload that cannot be serialized: the destination is BYTE-UNTOUCHED,
    # because serialization happens before the file is opened at all. Compared
    # against the bytes actually on disk rather than a re-serialization - the
    # first draft of this assertion compared against `json.dumps(...)` and failed
    # on the platform's text-mode newline translation, which is a property of the
    # ORIGINAL write too (both used text mode, so nothing about it changed) and
    # not the thing under test.
    intact = target.read_bytes()
    with pytest.raises(TypeError):
        atomic_write_json(target, {"unserializable": object()})
    assert target.read_bytes() == intact, (
        "a failed write leaves the previous snapshot byte-identical")
    assert list(target.parent.glob("*.tmp")) == [], "no temp file survives a failure"

    atomic_write_text(target, "plain text")
    assert target.read_text(encoding="utf-8") == "plain text"


def test_a_failure_INSIDE_the_write_cleans_up_and_spares_the_destination(tmp_path):
    """ADDED AFTER A SURVIVING MUTANT (deleting the `os.unlink(tmp_name)` cleanup
    passed the whole file).

    The failure the test above exercises happens in `json.dumps`, BEFORE any temp
    file exists - so it proved the serialize-first property and never reached the
    cleanup path at all. This one fails during the WRITE, which is the only way
    into that `except`. A `.tmp` left behind makes the next directory listing a
    lie about what state exists, and this store's directory is `data/runtime/`,
    which CI asserts is empty.
    """
    from src.utils.atomic_write import atomic_write_text

    target = tmp_path / "state.json"
    atomic_write_text(target, "the previous snapshot")
    intact = target.read_bytes()

    # A lone surrogate cannot be encoded: the failure lands inside `f.write`,
    # after `mkstemp` has already created the sibling file.
    with pytest.raises(UnicodeEncodeError):
        atomic_write_text(target, "\udcff", encoding="ascii")

    assert target.read_bytes() == intact, "the destination never opened"
    assert list(tmp_path.iterdir()) == [target], (
        "a partial temp file must not survive - found "
        f"{[p.name for p in tmp_path.iterdir()]}")


def test_the_write_publishes_by_replace_and_never_opens_the_destination():
    """STRUCTURAL, and DECLARED KNOWN-WEAK - Ruling 17's accounting, stated rather
    than implied.

    The two properties below are what make the write atomic, and NEITHER is
    observable from inside a passing process: a direct write to the destination
    produces byte-identical content, and a missing `fsync` produces byte-identical
    content. Both only differ when the process DIES mid-write, which is not
    something a test in that process can witness. Both mutants survived every
    behavioural assertion in this file, which is the evidence for this test rather
    than the argument against it.

    So this is a source-shaped assertion about a runtime guarantee - the shape
    Ruling 17 audited and called KNOWN-WEAK. It is kept because a proxy plus the
    behavioural witnesses above is stronger than either alone, and because the
    alternative is no coverage of the two lines the whole rider turns on.
    """
    import src.utils.atomic_write as mod
    with open(mod.__file__, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    write_fn = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "atomic_write_text")
    calls = [n for n in ast.walk(write_fn) if isinstance(n, ast.Call)]

    def names(node):
        return (isinstance(node.func, ast.Attribute) and node.func.attr) or None

    assert any(names(c) == "replace" for c in calls), (
        "publication must go through os.replace - a direct write to the "
        "destination truncates it, which is the whole defect")
    assert any(names(c) == "fsync" for c in calls), (
        "the temp file must be fsynced before it is published; replacing an "
        "unsynced file publishes a name whose contents are still in flight")

    # And nothing in this module may open the DESTINATION for writing - only the
    # temp file it created. This is what a "no os.replace, just write it" edit
    # would have to introduce, so it closes the same mutant a second way.
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open"):
            first = node.args[0] if node.args else None
            assert isinstance(first, ast.Name) and first.id == "tmp_name", (
                "open() in atomic_write.py may only target the temp file")


def test_a_real_store_snapshot_round_trips_through_the_atomic_path(tmp_path):
    """End to end on the store with the sharpest reason: SAE's epoch file. The
    slot spent below is durable AT THE MOMENT OF SPENDING (Ruling 34), and it is
    now durable atomically."""
    codex, sae, _ = _sae(tmp_path, ceiling=99)
    _mutate(sae, "D-1", "D-1::nova::NE-0001", "scar-0")

    assert sae.runtime_path.exists()
    assert list(sae.runtime_path.parent.glob("*.tmp")) == []

    resumed = SAE(codex=codex, runtime_path=str(sae.runtime_path))
    assert resumed.epoch_count == sae.epoch_count
    assert resumed.touched_lineages == sae.touched_lineages
    assert len(resumed.history) == len(sae.history)
    assert resumed.history[-1].proof is not None, (
        "the proof round-trips too (Ruling 45's additive key)")
