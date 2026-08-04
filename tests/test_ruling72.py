"""
test_ruling72.py - THE GOAL COMMITMENT LEDGER (Ruling 72 / Docket Q item Q1).

Manifest forty-first addendum, 2026-08-03. Docket Q's first build.

    A goal that was not committed before its pursuit is not a goal.

Ruling 61's law generalized from prediction to INTENTION. The ledger is
SUBSTRATE, not mover: it stores direction; it moves nothing, wires to nothing,
and grants no authority.

THE RED-FIRST WATCH IS A COLLECTION ERROR AND IS STATED AS ONE. `src/goals/`
did not exist at `90e987f0`, so every pin importing it fails at COLLECTION
there rather than on an assertion - the honest situation Rulings 61, 63 and 70
each recorded for their own new modules. There is no independent half to
witness, **so the mutation slate carries this pass's verification weight** and
the pins below are written to be forcing rather than merely present.

WHAT THIS FILE DOES NOT DUPLICATE: Ruling 69's mint battery. The goal ledger
JOINED `tests/test_ruling69.py`'s `LEDGERS` table (a Ruling-14 migration
recorded there), so the interleave, the absent counter, the typed refusal and
the torn-line property bind it through the pins that already own those claims.
Pin (e) here holds only what is GLC-specific.

COINS NOTHING: every enum member is recovered from the ruling's closed lists,
the mint is Ruling 69's shared helper, the three-state criterion shape is
`AncestryField`'s, and no threshold, weight or magnitude exists anywhere.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.goals.goal_ledger import (CRITERION_FIELDS, UNPRODUCIBLE_KINDS,
                                   AdoptionAct, CriterionKind, GoalAdoption,
                                   GoalCommitment, GoalCriterion, GoalEvidence,
                                   GoalKind, GoalLedger, GoalLedgerUnreadable,
                                   GoalLevel, GoalOutcome, GoalProvenance,
                                   GoalResolution, GoalStatus, UnproducibleGoalKind,
                                   declared, standing, supersession_only)

MODULE = Path("src/goals/goal_ledger.py")
SEED = Path("data/goal_roots.json")
REPO = Path(__file__).resolve().parents[1]


def _tree() -> ast.Module:
    return ast.parse((REPO / MODULE).read_text(encoding="utf-8"))


def _ledger(tmp_path, name="goals.jsonl") -> GoalLedger:
    return GoalLedger(ledger_path=str(tmp_path / name))


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def _ordinary(ledger, **kw) -> GoalCommitment:
    """A committable, resolvable goal - the non-root case."""
    params = dict(desired_state="Verify the seam holds.",
                  kind=GoalKind.VERIFICATION,
                  level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="tester",
                  completion_criteria=declared("the seam is verified"))
    params.update(kw)
    return ledger.commit(**params)


# =====================================================================
# (a) THE COMMITMENT IS FROZEN
# =====================================================================

def test_a_no_amend_method_exists_as_shape():
    """PIN (a), SHAPE. **The absence IS the enforcement.**

    A method named `amend` with a docstring saying "only before resolution"
    would be a request for restraint, and this project has hard evidence
    restraint fails. Scanned on the module's own definitions, so the claim is
    about what exists rather than about what anyone remembered not to call.
    """
    forbidden = {"amend", "update", "revise", "edit", "retarget", "rewrite",
                 "modify", "set_status", "reseed", "re_seed"}
    defined = {n.name for n in ast.walk(_tree())
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert not (defined & forbidden), (
        f"a mutation path appeared: {sorted(defined & forbidden)}. A goal that "
        f"can be edited after the fact is what QL1 abolishes.")


@pytest.mark.parametrize("field_name,value", [
    ("desired_state", "something else"),
    ("kind", GoalKind.REPAIR),
    ("level", GoalLevel.ROOT),
    ("asserter", "someone else"),
    ("supersedes_goal_id", "GLC-0009"),
])
def test_a_commitment_field_mutation_raises(tmp_path, field_name, value):
    """PIN (a), RUNTIME. The frozen record refuses the write."""
    commitment = _ordinary(_ledger(tmp_path))
    with pytest.raises(Exception) as excinfo:
        setattr(commitment, field_name, value)
    assert excinfo.type.__name__ in ("FrozenInstanceError", "AttributeError")


def test_a_the_write_mode_is_append_everywhere(tmp_path):
    """PIN (a), the durable half: THERE IS NO WRITE MODE BUT `"a"`.

    That is what makes the commitment unrewritable IN FACT rather than by
    convention - and it is scanned rather than trusted, because a single `"w"`
    anywhere in this file would make the whole ledger a state rather than a
    history.
    """
    modes = []
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open"):
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                modes.append(node.args[1].value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    modes.append(kw.value.value)
    assert modes, "the scanner found no `open` call at all - it has gone blind"
    assert set(modes) <= {"a", "r"}, (
        f"a non-append write mode appeared: {sorted(set(modes))}")


def test_a_the_commitment_line_is_byte_identical_after_everything(tmp_path):
    """PIN (a), THE STRUCTURAL HEART. The commitment line never changes.

    Evidence, a resolution and a supersession all land afterwards; the original
    bytes are untouched. An in-place update would be indistinguishable,
    afterwards, from having wanted the outcome all along.
    """
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger)
    original = Path(ledger.ledger_path).read_text(encoding="utf-8").splitlines()[0]

    ledger.record_evidence(goal.goal_id, ["CLM-0001"])
    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")
    _ordinary(ledger, supersedes_goal_id=goal.goal_id)

    after = Path(ledger.ledger_path).read_text(encoding="utf-8").splitlines()[0]
    assert after == original, "the commitment line was rewritten"


# =====================================================================
# (b) RESOLUTION GUARDS
# =====================================================================

def test_b_resolution_must_name_a_declared_criterion(tmp_path):
    """PIN (b). A resolution may not INVENT the criterion it met."""
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger, completion_criteria=declared("done"),
                     failure_criteria=standing())

    with pytest.raises(ValueError, match="recorded no failure_criteria"):
        ledger.resolve(goal.goal_id, GoalOutcome.FAILED, "failure_criteria")

    with pytest.raises(ValueError, match="is not a criterion"):
        ledger.resolve(goal.goal_id, GoalOutcome.FAILED, "invented_criteria")

    assert ledger.resolution_for(goal.goal_id) is None
    assert len([l for l in _lines(ledger)
                if l["kind_of_record"] == "resolution"]) == 0


def test_b_an_unknown_goal_cannot_be_resolved(tmp_path):
    ledger = _ledger(tmp_path)
    with pytest.raises(ValueError, match="no commitment"):
        ledger.resolve("GLC-9999", GoalOutcome.COMPLETED, "completion_criteria")


def test_b_a_second_resolution_raises(tmp_path):
    """PIN (b). A goal resolves ONCE; a re-score is a new goal (61 res.3)."""
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger)
    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")

    with pytest.raises(ValueError, match="already resolved"):
        ledger.resolve(goal.goal_id, GoalOutcome.FAILED, "completion_criteria")

    assert len([l for l in _lines(ledger)
                if l["kind_of_record"] == "resolution"]) == 1


def test_b_premise_invalidated_is_distinct_from_failed(tmp_path):
    """PIN (b), WITNESSED SEPARATELY as the ruling requires.

    **A goal whose GROUND DISSOLVED did not fail.** The two carry opposite
    lessons - one says the approach was wrong, the other says the question
    stopped existing - and the record keeps them apart rather than flattening
    the second into the first.
    """
    ledger = _ledger(tmp_path)
    failed = _ordinary(ledger, desired_state="A.")
    dissolved = _ordinary(ledger, desired_state="B.")

    ledger.resolve(failed.goal_id, GoalOutcome.FAILED, "completion_criteria")
    ledger.resolve(dissolved.goal_id, GoalOutcome.PREMISE_INVALIDATED,
                   "completion_criteria")

    assert GoalOutcome.PREMISE_INVALIDATED is not GoalOutcome.FAILED
    assert (GoalOutcome.PREMISE_INVALIDATED.value
            != GoalOutcome.FAILED.value)
    assert ledger.resolution_for(failed.goal_id).outcome is GoalOutcome.FAILED
    assert (ledger.resolution_for(dissolved.goal_id).outcome
            is GoalOutcome.PREMISE_INVALIDATED)

    # And they persist as different values, not as one collapsed onto the other.
    outcomes = [l["outcome"] for l in _lines(ledger)
                if l["kind_of_record"] == "resolution"]
    assert outcomes == ["failed", "premise_invalidated"]


def test_b_a_root_is_structurally_unresolvable(tmp_path):
    """PIN (b) meets the root class. **The property falls out of the
    vocabulary rather than being a rule anyone must remember.**

    A root carries STANDING completion, STANDING failure and SUPERSESSION_ONLY
    abandonment, and `resolve` admits only DECLARED criteria - so no criterion
    on a root can be resolved against, and the only status it can reach is
    SUPERSEDED.
    """
    ledger = _ledger(tmp_path)
    roots = ledger.ensure_genesis()

    for root in roots:
        for name in CRITERION_FIELDS:
            with pytest.raises(ValueError, match="recorded no"):
                ledger.resolve(root.goal_id, GoalOutcome.COMPLETED, name)

    assert not [l for l in _lines(ledger) if l["kind_of_record"] == "resolution"]


# =====================================================================
# (c) STATUS IS DERIVED, NEVER STORED
# =====================================================================

def test_c_no_record_carries_a_status_field():
    """PIN (c), AST. L3: a stored status is a second writer of what the
    appends already determine - Ruling 63's cached projection and Ruling 65's
    stored derivation, both already paid for."""
    offenders = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                if stmt.target.id in {"status", "state", "current_status",
                                      "is_resolved", "is_superseded",
                                      "resolved", "superseded"}:
                    offenders.append(f"{node.name}.{stmt.target.id}")
    assert offenders == [], (
        f"a status field is STORED at {offenders}; status is derived at read")


def test_c_no_persisted_line_carries_a_status_key(tmp_path):
    """PIN (c), the durable half - the bytes carry no status either."""
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger)
    ledger.record_evidence(goal.goal_id, ["CLM-1"])
    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")

    for line in _lines(ledger):
        assert "status" not in line
        assert not any(k.endswith("_status") for k in line)


def test_c_status_is_derived_across_the_whole_progression(tmp_path):
    """PIN (c). Every step derived from the appends alone."""
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger)
    assert ledger.derive_status(goal.goal_id) is GoalStatus.COMMITTED

    ledger.record_evidence(goal.goal_id, ["CLM-1"])
    assert ledger.derive_status(goal.goal_id) is GoalStatus.EVIDENCE_BEARING

    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")
    assert ledger.derive_status(goal.goal_id) is GoalStatus.RESOLVED


@pytest.mark.parametrize("outcome", list(GoalOutcome))
def test_c_derivation_witnessed_across_the_outcome_vocabulary(tmp_path, outcome):
    """PIN (c). Every member of the closed outcome vocabulary derives RESOLVED,
    and the outcome itself stays readable beside it."""
    ledger = _ledger(tmp_path, name=f"{outcome.value}.jsonl")
    goal = _ordinary(ledger)
    ledger.resolve(goal.goal_id, outcome, "completion_criteria")

    assert ledger.derive_status(goal.goal_id) is GoalStatus.RESOLVED
    assert ledger.resolution_for(goal.goal_id).outcome is outcome


def test_c_deriving_an_unknown_goal_raises(tmp_path):
    with pytest.raises(ValueError, match="no commitment"):
        _ledger(tmp_path).derive_status("GLC-9999")


# =====================================================================
# (d) UNPRODUCIBLE KINDS AND THE UNPRODUCIBLE ADOPTION
# =====================================================================

@pytest.mark.parametrize("kind", list(UNPRODUCIBLE_KINDS))
def test_d_the_public_surface_refuses_an_unproducible_kind(tmp_path, kind):
    """PIN (d), BEHAVIORAL. **QL3: epistemic commitments before world agency.**

    The member exists so the vocabulary is closed NOW and the barrier lifts by
    ruling - not by an enum edit made in passing. Nothing is written.
    """
    ledger = _ledger(tmp_path)
    with pytest.raises(UnproducibleGoalKind) as excinfo:
        ledger.commit(desired_state="act on the world",
                      kind=kind,
                      level=GoalLevel.PROJECT,
                      provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                      asserter="tester")

    message = str(excinfo.value)
    assert "QL3" in message, "the refusal names the law it enforces"
    assert _lines(ledger) == []
    assert not Path(ledger.ledger_path).exists(), (
        "a refused commitment leaves no file - the guard runs before the write")


def test_d_the_unproducible_kinds_are_exactly_the_two_ruled():
    """PIN (d). The list is the ruling's, and both members remain PRESENT in
    the enum - a closed vocabulary missing a registered member is the enum
    reopening later (Ruling 63's `OBSERVED` precedent)."""
    assert set(UNPRODUCIBLE_KINDS) == {GoalKind.EXTERNAL_TASK,
                                       GoalKind.CAPABILITY_ACQUISITION}
    assert GoalKind.EXTERNAL_TASK in GoalKind
    assert GoalKind.CAPABILITY_ACQUISITION in GoalKind
    assert {k.value for k in GoalKind} == {
        "research", "verification", "repair", "external_task",
        "capability_acquisition"}


def test_d_no_source_path_constructs_an_unproducible_kind():
    """PIN (d), AST no-emitter, across ALL of `src/`.

    Whole-tree rather than module-local on purpose: the claim is that NOTHING
    mints one, and a scan of this module alone would miss the first consumer
    that did it somewhere else.
    """
    offenders = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Attribute)
                    and node.attr in {"EXTERNAL_TASK", "CAPABILITY_ACQUISITION"}
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "GoalKind"):
                # The declaration in UNPRODUCIBLE_KINDS is the REFUSAL LIST, not
                # an emitter - it is what makes them unproducible.
                offenders.append(f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    allowed = {f"src/goals/goal_ledger.py"}
    unexpected = [o for o in offenders if o.rsplit(":", 1)[0] not in allowed]
    assert unexpected == [], (
        f"an unproducible kind is named in live code at {unexpected}")


def test_d_nothing_constructs_a_goal_adoption_anywhere_in_src():
    """PIN (d), THE NO-PRODUCER PIN. **QL6, and it is the point of the docket.**

    Adoption is AUREA's own event: the moment a proposed direction becomes one
    she holds. Her deliberation machinery does not exist, so nothing here is
    entitled to produce that moment - **a founder-written adoption would be the
    laundering QL6 names**, and the record would afterwards be
    indistinguishable from one she actually made.
    """
    offenders = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "GoalAdoption"):
                offenders.append(f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    assert offenders == [], (
        f"a GoalAdoption is constructed at {offenders}. Adoption is hers, and "
        f"the reopening condition is the Q3-era deliberation machinery.")


def test_d_the_ledger_exposes_no_adoption_write_path():
    """PIN (d), behavioral half: no public method appends an adoption, and the
    reader has no adoption branch to make half a producer out of."""
    surface = [n for n in dir(GoalLedger) if not n.startswith("_")]
    assert not any("adopt" in n.lower() for n in surface), (
        f"an adoption surface appeared on the ledger: {surface}")

    source = (REPO / MODULE).read_text(encoding="utf-8")
    assert '"adoption"' not in source.replace(
        '"kind_of_record": "adoption"', ""), (
        "the reader gained an adoption branch; nothing can write one, so "
        "nothing should read one back")


def test_d_the_adoption_type_exists_and_is_complete():
    """PIN (d), the other direction. The TYPE is real - it simply has no
    producer. A type that did not exist would have to be invented under
    pressure on the day adoption lands, which is the worst moment to design it.
    """
    assert {a.value for a in AdoptionAct} == {"adopted", "revised", "refused"}
    record = GoalAdoption(goal_id="GLC-0001", act=AdoptionAct.ADOPTED)
    assert record.as_dict()["kind_of_record"] == "adoption"
    with pytest.raises(Exception):
        record.goal_id = "GLC-0002"


# =====================================================================
# (e) THE MINT - GLC-specific; the shared battery lives in test_ruling69.py
# =====================================================================

def test_e_the_mint_uses_the_shared_helper_not_a_local_copy():
    """PIN (e). Ruling 69's helper, IMPORTED - a second copy would be a second
    chance to drift on a scan discipline subtle enough to have needed a rider
    (Ruling 64) to anchor correctly."""
    imported = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imported.add(f"{node.module}.{alias.name}")
    assert "src.utils.ledger_mint.derive_max_ordinal" in imported
    assert "src.utils.ledger_mint.mint_lock" in imported

    # And no local re-implementation of the scan.
    defined = {n.name for n in ast.walk(_tree())
               if isinstance(n, ast.FunctionDef)}
    assert "derive_max_ordinal" not in defined
    assert "ordinal_pattern" not in defined


def test_e_the_mint_and_the_append_happen_inside_the_lock():
    """PIN (e), ADDED AFTER A MUTATION SURVIVOR - a real gap.

    Dropping `with mint_lock(...)` survived every behavioural pin, and it had
    to: the lock guards CONCURRENT mints, and every mint re-derives from the
    file, so a single-threaded interleave cannot tell a held lock from a
    missing one. Ruling 69's own do-NOT names this exact failure - "hold the
    lock across only part of derive → mint → append".

    **DECLARED STRUCTURAL PER RULING 17, and it is the right instrument rather
    than a weaker one:** the property IS a lexical scope - that the mint and
    the append sit inside the `with` block - so source is where it is true or
    false. A threaded probe would be flaky and could pass by luck, which is
    worse than a pin that reads the scope directly.
    """
    commit_fn = next(n for n in ast.walk(_tree())
                     if isinstance(n, ast.FunctionDef) and n.name == "_commit")

    withs = [n for n in ast.walk(commit_fn) if isinstance(n, ast.With)]
    guarded = [w for w in withs
               if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                      and c.func.id == "mint_lock"
                      for item in w.items
                      for c in ast.walk(item.context_expr))]
    assert guarded, "`_commit` does not take the mint lock at all"

    body = guarded[0]
    calls = {n.func.attr for n in ast.walk(body)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "_next_id" in calls, "the MINT happens outside the lock"
    assert "_append" in calls, (
        "the APPEND happens outside the lock - deriving inside it and "
        "appending outside leaves exactly the race Ruling 69 closes")


def test_e_glc_ids_are_file_derived_and_sequential(tmp_path):
    """PIN (e). Ids come from the FILE, at the moment of minting."""
    ledger = _ledger(tmp_path)
    ids = [_ordinary(ledger, desired_state=f"G{i}.").goal_id for i in range(3)]
    assert ids == ["GLC-0001", "GLC-0002", "GLC-0003"]

    fresh = GoalLedger(ledger_path=str(ledger.ledger_path))
    assert _ordinary(fresh, desired_state="G3.").goal_id == "GLC-0004", (
        "a new instance resumes from the FILE, not from a counter it never had")


def test_e_the_torn_line_property_holds_at_the_glc_prefix(tmp_path):
    """PIN (e). **Ruling 69 res.2 at a new prefix: an ordinal on a TORN,
    UNPARSEABLE line is still seen and never reissued.**

    The planted line is BOTH high-ordinal and unparseable, which is what makes
    it a witness: a mint that parsed JSON would not see it at all.
    """
    ledger = _ledger(tmp_path)
    _ordinary(ledger)
    with open(ledger.ledger_path, "a", encoding="utf-8") as handle:
        handle.write('{"kind_of_record": "commitment", "goal_id": "GLC-0042"')

    minted = _ordinary(ledger, desired_state="after the tear").goal_id
    assert minted == "GLC-0043", (
        f"minted {minted} - an id on a torn line was invisible and would have "
        f"been reissued into an append-only record")


def test_e_an_unreadable_existing_ledger_refuses_typed(tmp_path, monkeypatch):
    """PIN (e). Ruling 53's sentinel: it RAISES rather than minting from an
    unknown floor. It does not fall back to a number - two goals wearing one id
    are two directions nobody can tell apart afterwards."""
    import builtins
    ledger = _ledger(tmp_path)
    _ordinary(ledger)

    real_open = builtins.open
    target = str(ledger.ledger_path)

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == target and "r" in mode:
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    with pytest.raises(GoalLedgerUnreadable, match="GLC"):
        ledger._next_id()


# =====================================================================
# (f) SEED IDEMPOTENCE
# =====================================================================

def test_f_genesis_commits_exactly_two_roots_once(tmp_path):
    """PIN (f), THE FORCING PIN. **Restart is not absolution** (Ruling 34).

    A second genesis against a non-empty ledger commits NOTHING - the ledger
    persists, so a process starting against it has nothing to found.
    """
    ledger = _ledger(tmp_path)
    first = ledger.ensure_genesis()
    assert len(first) == 2

    second = ledger.ensure_genesis()
    assert second == ()

    # And a THIRD, through a fresh instance over the same path - the restart case.
    third = GoalLedger(ledger_path=str(ledger.ledger_path)).ensure_genesis()
    assert third == ()

    commitments = ledger.commitments()
    assert len(commitments) == 2
    assert [c.goal_id for c in commitments] == ["GLC-0001", "GLC-0002"]
    assert len([l for l in _lines(ledger)
                if l["kind_of_record"] == "commitment"]) == 2


def test_f_the_roots_are_byte_identical_to_the_tracked_seed(tmp_path):
    """PIN (f). The committed text is the seed's text, verbatim.

    Read from the SEED DOCUMENT rather than hardcoded here: a copy in the test
    would drift from the tracked wording and the pin would then be checking
    this file against itself.
    """
    seed = json.loads((REPO / SEED).read_text(encoding="utf-8"))
    ledger = _ledger(tmp_path)
    roots = ledger.ensure_genesis()

    assert len(roots) == len(seed["roots"]) == 2
    for committed, declared_root in zip(roots, seed["roots"]):
        assert committed.desired_state == declared_root["desired_state"]
        # And through the FILE, so serialization is witnessed too.
        line = next(l for l in _lines(ledger)
                    if l["goal_id"] == committed.goal_id)
        assert line["desired_state"] == declared_root["desired_state"]


def test_f_the_roots_carry_the_ruled_provenance_and_criteria(tmp_path):
    """PIN (f). EXTERNAL_PROPOSAL / founder / ROOT / STANDING /
    SUPERSESSION_ONLY - res.5's own list.

    **Per QL6 they are PROPOSALS and stay proposals.** A proposed root
    constrains through its law; an adopted root directs through her commitment,
    and nothing here can perform that adoption.
    """
    roots = _ledger(tmp_path).ensure_genesis()
    assert len(roots) == 2
    for root in roots:
        assert root.provenance is GoalProvenance.EXTERNAL_PROPOSAL
        assert root.asserter == "founder"
        assert root.level is GoalLevel.ROOT
        assert root.completion_criteria.kind is CriterionKind.STANDING
        assert root.abandonment_criteria.kind is CriterionKind.SUPERSESSION_ONLY
        assert root.kind not in UNPRODUCIBLE_KINDS


def test_f_genesis_does_not_run_from_the_constructor(tmp_path):
    """PIN (f), the shape half - **a judgment call, pinned so it is visible.**

    No store in this codebase writes from its constructor, and one that did
    would turn every incidental construction into two permanent records.
    Constructing a ledger writes NOTHING; genesis is a deliberate act.
    """
    ledger = _ledger(tmp_path)
    assert not Path(ledger.ledger_path).exists()
    assert ledger.commitments() == ()


def test_f_there_is_no_reseed_path(tmp_path):
    """PIN (f). Genesis is the ONLY way a seed root enters the ledger.

    Scanned for CALLABLES, not for the token: `SEED_PATH` is the Ruling 32 path
    CONSTANT and its presence is required, not suspect. The claim here is that
    no second seeding OPERATION exists - the first draft of this pin matched
    the constant and had to be sharpened to what it actually asserts.
    """
    seeding = [n for n in dir(GoalLedger)
               if not n.startswith("_")
               and callable(getattr(GoalLedger, n))
               and ("seed" in n.lower() or "genesis" in n.lower())]
    assert seeding == ["ensure_genesis"], (
        f"a seeding operation other than genesis appeared: {seeding}")


def test_f_a_seed_declaring_no_roots_raises_rather_than_founding_nothing(tmp_path):
    """PIN (f), ADDED AFTER A MUTATION SURVIVOR - a real gap, not an equivalence.

    Deleting the empty-roots guard survived every other pin here, because no
    test drove a seed document that declared nothing. **A genesis that quietly
    founded an empty ledger would leave her with no roots and no error** - the
    silent-failure class this house refuses everywhere else, at the one moment
    that is supposed to establish what she is for.
    """
    for payload in ({"version": 1, "roots": []}, {"version": 1}):
        seed = tmp_path / f"empty_{len(payload)}.json"
        seed.write_text(json.dumps(payload), encoding="utf-8")
        ledger = GoalLedger(ledger_path=str(tmp_path / f"g{len(payload)}.jsonl"),
                            seed_path=str(seed))
        with pytest.raises(ValueError, match="declares no roots"):
            ledger.ensure_genesis()
        assert ledger.commitments() == ()


def test_f_a_missing_seed_raises_rather_than_founding_nothing(tmp_path):
    """PIN (f), same principle: an absent seed is a broken install, not a
    licence to found an empty ledger."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "g.jsonl"),
                        seed_path=str(tmp_path / "nope.json"))
    with pytest.raises(OSError):
        ledger.ensure_genesis()
    assert ledger.commitments() == ()


def test_f_the_seed_is_never_opened_for_writing():
    """PIN (f) meets Ruling 32: the seed is READ-ONLY INPUT WITH NO WRITER.

    Scanned rather than trusted - Ruling 32's whole finding was that one
    `filepath` served both a read and a `"w"`, and a default-constructed store
    that saved replaced the founding record wholesale.
    """
    source = (REPO / MODULE).read_text(encoding="utf-8")
    assert "seed_path" in source
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open"):
            # Any open() naming the seed must be mode "r".
            names = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
            if "seed_path" in names:
                assert (len(node.args) > 1
                        and isinstance(node.args[1], ast.Constant)
                        and node.args[1].value == "r"), (
                    "the seed is opened in a non-read mode")


# =====================================================================
# (g) ROOT SUPERSESSION
# =====================================================================

def test_g_a_supersession_must_name_an_existing_goal(tmp_path):
    """PIN (g). A supersession naming nothing is a new goal wearing a
    mutation's clothes."""
    ledger = _ledger(tmp_path)
    with pytest.raises(ValueError, match="no commitment"):
        _ordinary(ledger, supersedes_goal_id="GLC-9999")
    assert _lines(ledger) == []


def test_g_supersession_moves_the_predecessor_and_leaves_it_untouched(tmp_path):
    """PIN (g), BOTH HALVES. **Root mutation IS supersession** (res.1).

    The predecessor's derived status becomes SUPERSEDED and its record BYTES
    ARE UNTOUCHED - the successor names the predecessor, never the reverse,
    because editing the predecessor to say it was superseded is the rewrite
    this ledger refuses.
    """
    ledger = _ledger(tmp_path)
    roots = ledger.ensure_genesis()
    rg1 = roots[0]

    before = Path(ledger.ledger_path).read_text(encoding="utf-8").splitlines()[0]
    assert ledger.derive_status(rg1.goal_id) is GoalStatus.COMMITTED

    successor = ledger.commit(
        desired_state="A revised first root.",
        kind=GoalKind.RESEARCH, level=GoalLevel.ROOT,
        provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="founder",
        completion_criteria=standing(),
        abandonment_criteria=supersession_only(),
        supersedes_goal_id=rg1.goal_id)

    assert ledger.derive_status(rg1.goal_id) is GoalStatus.SUPERSEDED
    assert ledger.superseded_by(rg1.goal_id) == successor.goal_id

    after = Path(ledger.ledger_path).read_text(encoding="utf-8").splitlines()[0]
    assert after == before, "the superseded record was edited"

    # The successor wears a NEW id and carries the predecessor by name.
    assert successor.goal_id != rg1.goal_id
    assert successor.supersedes_goal_id == rg1.goal_id


def test_g_a_root_reaches_superseded_without_any_resolution(tmp_path):
    """PIN (g). The root's whole lifecycle, end to end: it cannot resolve, and
    supersession is the only status it can reach."""
    ledger = _ledger(tmp_path)
    rg1 = ledger.ensure_genesis()[0]
    ledger.commit(desired_state="Successor.", kind=GoalKind.RESEARCH,
                  level=GoalLevel.ROOT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="founder", supersedes_goal_id=rg1.goal_id)

    assert ledger.resolution_for(rg1.goal_id) is None
    assert ledger.derive_status(rg1.goal_id) is GoalStatus.SUPERSEDED


# =====================================================================
# (h) QL0 PURITY
# =====================================================================

FORBIDDEN_IMPORT_TOKENS = {
    # A goal grants no authority: the module that stores goals cannot reach
    # anything a goal might wish to command.
    "sae", "codex", "racm", "reflex_grid", "rb_system", "dee", "cae",
    "doctrine_spine", "scar_logic_core", "nova", "tca_core", "tcaml",
    "hail", "ore", "truth_packet", "echonet", "aurea_core", "spl", "ril",
    "black_sphere", "csa", "veiled_thread", "sbsre", "compass",
    # And it never initiates anything.
    "urllib", "requests", "socket", "http", "aiohttp", "httpx", "asyncio",
    "subprocess",
}


def _imported_tokens() -> set:
    tokens = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                tokens.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                tokens.update(node.module.split("."))
            for alias in node.names:
                tokens.add(alias.name)
    return tokens


def test_h_the_ledger_imports_nothing_it_could_command():
    """PIN (h). **QL0 AS STRUCTURE** (res.6) - the enforcement IS the import
    list. Not "does not call" but CANNOT: the names are not in scope.

    Ruling 70's enforcement-by-scope, one docket later.
    """
    offenders = sorted(_imported_tokens() & FORBIDDEN_IMPORT_TOKENS)
    assert offenders == [], (
        f"the goal ledger imports {offenders}. A goal grants no authority, and "
        f"the module that stores goals must not be able to reach the machinery "
        f"a goal might wish to command.")


def test_h_the_import_scanner_actually_fires():
    """Ruling 32's answer to the vacuous-pin problem: fed the forbidden shape
    and a benign control, so a scanner that has stopped scanning fails HERE."""
    def tokens_of(source):
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

    forbidden = ("from src.expansion.sae import SAE\n"
                 "from src.doctrine.codex import Codex\nimport requests\n")
    benign = ("from src.utils.ledger_mint import mint_lock\n"
              "from typing import Optional\n")
    assert tokens_of(forbidden) & FORBIDDEN_IMPORT_TOKENS
    assert not (tokens_of(benign) & FORBIDDEN_IMPORT_TOKENS)


def test_h_the_goal_ledgers_consumer_set_is_exactly_the_ruled_one():
    """PIN (h). **THE LEDGER'S CONSUMERS ARE ENUMERATED, AND EACH IS RULED.**

    RULING 73 MIGRATION (2026-08-03), Ruling-14 form.

        OLD: `assert consumers == []`  ("the ledger participates in NOTHING
             this pass"), with the docstring promising the pin "goes RED the
             day something wires it - which is exactly when that wiring needs
             its own ruling rather than arriving as a convenience."
        NEW: `assert consumers == [the arbiter]`.

    **THE PIN FIRED EXACTLY AS DESIGNED AND THE PROMISE WAS KEPT.** Ruling 73
    wired the first consumer, and it arrived WITH its ruling rather than as a
    convenience: `src/goals/goal_arbitration.py` reads the ledger through an
    injected instance to select a standing commitment, and writes nothing to
    it (Ruling 73 res.1/res.2, pinned in `tests/test_ruling73.py`).

    **NO ASSERTION WAS WEAKENED - IT WAS NARROWED.** The claim is still that
    the consumer set is exactly the ruled one; what changed is that the ruled
    set now has one member instead of none. An unruled second consumer still
    reddens this pin, which is the property worth keeping.
    """
    RULED_CONSUMERS = ["src/goals/goal_arbitration.py"]

    consumers = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "goal_ledger.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "goal_ledger" in node.module or "goals" in node.module.split("."):
                    consumers.append(path.relative_to(REPO).as_posix())
    assert sorted(set(consumers)) == RULED_CONSUMERS, (
        f"the goal ledger's consumer set is {sorted(set(consumers))}, not the "
        f"ruled {RULED_CONSUMERS}. Wiring it is Q2/Q3 work and takes a ruling.")


def test_h_the_ledger_never_calls_commit_on_itself():
    """PIN (h), FOUND BY THE INVARIANT SUITE, recorded here where a Q2 author
    will look.

    `Codex.commit` is the doctrine write API, and Ruling 5's invariant scans
    `src/` for calls to `.commit()` ON ANY RECEIVER - correctly, because a
    scanner that had to tell "commit a goal" from "commit a doctrine" by
    inferring a receiver's type is one that will eventually get it wrong. The
    first draft's `ensure_genesis` called `self.commit(...)` and was the only
    such call in the tree outside SAE; the invariant caught it.

    **THE PUBLIC NAME STAYED** - `commit` is this docket's vocabulary and
    Ruling 61's sibling shape - and the INTERNAL call site moved to `_commit`,
    which is CLAUDE.md §2's rule ("the fix is the name, not the test") applied
    to the name that actually carried the ambiguity. The invariant remains the
    authoritative guard; this pin exists so the reason is legible here too.
    """
    offenders = [n.lineno for n in ast.walk(_tree())
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "commit"
                 and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == "self"]
    assert offenders == [], (
        f"`self.commit()` at lines {offenders} - indistinguishable to Ruling "
        f"5's scanner from a Codex doctrine write. Use `_commit`.")


def test_h_the_ledger_writes_only_its_own_file(tmp_path):
    """PIN (h), the durable half: one ledger file, nothing else on disk."""
    root = tmp_path / "sandbox"
    root.mkdir()
    ledger = GoalLedger(ledger_path=str(root / "logs" / "goals.jsonl"))
    ledger.ensure_genesis()
    _ordinary(ledger, desired_state="another")
    ledger.record_evidence("GLC-0001", ["CLM-1"])

    written = sorted(p.relative_to(root).as_posix()
                     for p in root.rglob("*") if p.is_file())
    assert written == ["logs/goals.jsonl"], f"unexpected writes: {written}"


# =====================================================================
# (i) ABSENCE - QL4 and the standing refusals
# =====================================================================

def test_i_no_record_carries_a_priority_confidence_or_weight_field():
    """PIN (i), AST. **QL4 and the standing refusals, pinned as ABSENCE.**

    There is nowhere to put a scalar standing: no record carries a numeric
    field at all, so a priority could not be added without adding a field -
    which is a visible change rather than a quiet one.
    """
    forbidden = {"priority", "confidence", "weight", "score", "rank",
                 "importance", "urgency", "utility", "value_estimate",
                 "certainty", "probability"}
    offenders = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id.lower()
                if any(word in name for word in forbidden):
                    offenders.append(f"{node.name}.{stmt.target.id}")
    assert offenders == [], (
        f"a scalar standing field appeared at {offenders} - QL4 refuses "
        f"precedence expressed as a coined magnitude")


def test_i_no_record_field_is_numerically_typed():
    """PIN (i), stronger and type-shaped: no `int`/`float` annotation anywhere
    on a record. A number on a goal record is a magnitude waiting for a
    comparison."""
    offenders = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                annotation = ast.unparse(stmt.annotation)
                if ("int" in annotation or "float" in annotation) and \
                        isinstance(stmt.target, ast.Name):
                    offenders.append(f"{node.name}.{stmt.target.id}: {annotation}")
    assert offenders == [], f"a numeric record field appeared at {offenders}"


def test_i_persisted_lines_carry_no_numbers(tmp_path):
    """PIN (i), the durable half - measured on the BYTES, across every record
    type this ledger can write."""
    ledger = _ledger(tmp_path)
    ledger.ensure_genesis()
    goal = _ordinary(ledger, desired_state="ordinary")
    ledger.record_evidence(goal.goal_id, ["CLM-1"])
    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")

    def numbers(value, path=""):
        found = []
        if isinstance(value, bool):
            return found
        if isinstance(value, (int, float)):
            found.append(path)
        elif isinstance(value, dict):
            for key, item in value.items():
                found += numbers(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                found += numbers(item, f"{path}[{index}]")
        return found

    for line in _lines(ledger):
        assert numbers(line) == [], f"a number reached the record: {line}"


# =====================================================================
# (j) EVIDENCE ORDER-INDEPENDENCE
# =====================================================================

def test_j_permuted_evidence_derives_the_same_status(tmp_path):
    """PIN (j). **Evidence contributes only its EXISTENCE**, never a direction
    or a magnitude, so order cannot change what is derived.

    Ruling 64 res.5's no-adjudication-by-list-order, made structural rather
    than promised: there is no tally for an ordering to bias.
    """
    statuses = []
    for order in ([("a", "up"), ("b", "down")], [("b", "down"), ("a", "up")]):
        ledger = _ledger(tmp_path, name=f"{order[0][0]}.jsonl")
        goal = _ordinary(ledger)
        for record_id, note in order:
            ledger.record_evidence(goal.goal_id, [f"CLM-{record_id}"], note)
        statuses.append(ledger.derive_status(goal.goal_id))

    assert statuses == [GoalStatus.EVIDENCE_BEARING,
                        GoalStatus.EVIDENCE_BEARING]


def test_j_contradictory_evidence_settles_nothing(tmp_path):
    """PIN (j). Evidence pointing both ways leaves the goal EVIDENCE_BEARING -
    the ledger records that something bore on the goal and refuses to say which
    way it pointed, because it holds no instrument for that."""
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger)
    ledger.record_evidence(goal.goal_id, ["CLM-1"], "supports")
    ledger.record_evidence(goal.goal_id, ["CLM-2"], "contradicts")

    assert ledger.derive_status(goal.goal_id) is GoalStatus.EVIDENCE_BEARING
    assert len(ledger.evidence_for(goal.goal_id)) == 2


def test_j_evidence_requires_a_committed_goal(tmp_path):
    """Evidence bears on a goal that was committed BEFORE it."""
    with pytest.raises(ValueError, match="no commitment"):
        _ledger(tmp_path).record_evidence("GLC-9999", ["CLM-1"])


# =====================================================================
# RECORD-VALUE CONFORMANCE (res.7 / Batch 66)
# =====================================================================

def test_the_writer_conforms_to_batch_66():
    """res.7. No `default=`, `allow_nan=False`, admissible leaves only.

    `default=str` would silently stringify a non-canonical leaf into a
    permanent record - a record claiming a string was presented when it was
    not (Ruling 66).
    """
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("dumps", "dump")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "json"):
            kwargs = {kw.arg for kw in node.keywords}
            assert "default" not in kwargs, "a `default=` coercion appeared"
            assert "allow_nan" in kwargs, "`allow_nan=False` is missing"


def test_a_non_canonical_leaf_is_refused_before_the_write(tmp_path):
    """res.7, BEHAVIORAL. The gate runs BEFORE `mkdir` and BEFORE `open`, so a
    refused entry leaves no file, no line, and no directory.

    **REWRITTEN AFTER A MUTATION SURVIVOR, and the survivor was the finding.**
    The first draft passed a `bytearray` in `originating_record_ids`, which
    `_ids()` refuses on TYPE long before the record-value gate is reached - so
    deleting `validate_record_value` entirely left this test GREEN. The pin was
    passing for a neighbouring guard's reason and witnessed nothing about the
    one it named.

    `permitted_scope` is deliberately NOT type-checked at construction, so it
    is the honest route to the writer gate: a value that reaches serialization
    and must be REFUSED there rather than silently stringified into a permanent
    record (Ruling 66).
    """
    ledger = GoalLedger(ledger_path=str(tmp_path / "nested" / "goals.jsonl"))
    with pytest.raises(Exception) as excinfo:
        _ordinary(ledger, permitted_scope=bytearray(b"not canonical"))

    assert "NonCanonicalRecordValue" in type(excinfo.value).__name__ or \
        isinstance(excinfo.value, TypeError), (
        f"the writer gate did not refuse: {excinfo.value!r}")
    assert not Path(ledger.ledger_path).exists(), (
        "the gate must run BEFORE mkdir and open - a refused entry leaves no "
        "file and no directory it did not already need")
    assert not (tmp_path / "nested").exists()


def test_ids_only_references_refuse_a_live_object(tmp_path):
    """res.1. Recorded references are ID STRINGS ONLY - a live object here
    would be a handle into another owner's store (Ruling 42)."""
    ledger = _ledger(tmp_path)
    with pytest.raises(TypeError, match="ID STRINGS ONLY"):
        _ordinary(ledger, justification_claim_ids=[object()])
    with pytest.raises(TypeError, match="not a single string"):
        _ordinary(ledger, governing_doctrine_ids="Doctrine-0")


def test_references_are_never_validated_against_any_store(tmp_path):
    """res.1. Ruling 61's `claim_refs` semantics VERBATIM: **the join is the
    caller's.**

    A ledger that validated its references would refuse to record a real
    intention because some other file was unavailable.
    """
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger,
                     originating_record_ids=["CLM-9999"],
                     justification_claim_ids=["PRD-9999"],
                     governing_doctrine_ids=["Doctrine-does-not-exist"])
    assert goal.governing_doctrine_ids == ("Doctrine-does-not-exist",)


# =====================================================================
# THE CRITERION VOCABULARY
# =====================================================================

def test_the_two_special_criteria_are_first_class_not_magic_strings():
    """res.1. STANDING and SUPERSESSION_ONLY are ENUM MEMBERS with
    constructors, so they cannot be misspelled into an ordinary criterion."""
    assert {k.value for k in CriterionKind} == {
        "declared", "standing", "supersession_only"}
    assert standing().kind is CriterionKind.STANDING
    assert supersession_only().kind is CriterionKind.SUPERSESSION_ONLY
    assert declared("x").kind is CriterionKind.DECLARED


@pytest.mark.parametrize("factory", [standing, supersession_only])
def test_a_special_criterion_carries_no_text(factory):
    """They are statements ABOUT the answer, not answers."""
    assert factory().text is None
    with pytest.raises(ValueError, match="carries no text"):
        GoalCriterion(kind=factory().kind, text="smuggled")


def test_a_declared_criterion_requires_its_text():
    """An empty declared criterion is one nobody can resolve against - the
    rewritability this ledger refuses."""
    with pytest.raises(ValueError, match="carries its text"):
        declared("")
    with pytest.raises(ValueError, match="carries its text"):
        GoalCriterion(kind=CriterionKind.DECLARED)


def test_a_missing_criterion_defaults_to_standing_not_to_empty(tmp_path):
    """res.1. The honest reading of a caller who named none: no terminal state
    of that kind was declared, so none can be resolved against."""
    ledger = _ledger(tmp_path)
    goal = ledger.commit(desired_state="x", kind=GoalKind.RESEARCH,
                         level=GoalLevel.PROJECT,
                         provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                         asserter="tester")
    for name in CRITERION_FIELDS:
        assert goal.criterion(name).kind is CriterionKind.STANDING


# =====================================================================
# CLOSED VOCABULARIES AND THE READER
# =====================================================================

def test_the_reader_never_coerces_an_unknown_enum_value(tmp_path):
    """A line carrying a value outside a closed vocabulary contributes NOTHING.

    Silently reading an unknown kind as a known one would put a fact in the
    reader's hands the writer never recorded - and a forensic record outlives
    the code that wrote it.
    """
    ledger = _ledger(tmp_path)
    _ordinary(ledger)
    with open(ledger.ledger_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "kind_of_record": "commitment", "goal_id": "GLC-0500",
            "kind": "world_domination", "level": "root",
            "desired_state": "x", "provenance": "external_proposal",
            "completion_criteria": {"kind": "standing", "text": None},
            "failure_criteria": {"kind": "standing", "text": None},
            "abandonment_criteria": {"kind": "standing", "text": None},
        }) + "\n")

    assert [c.goal_id for c in ledger.commitments()] == ["GLC-0001"]
    assert ledger.commitment_for("GLC-0500") is None


def test_the_provenance_vocabulary_is_closed_and_asserter_is_separate():
    """res.1. **The founder is a NAMED ASSERTER, not an enum member.**

    Making "founder" a provenance member would bake one proposer into the
    vocabulary and lose the distinction between WHERE a proposal came from and
    WHO made it.
    """
    assert {p.value for p in GoalProvenance} == {
        "external_proposal", "internal_drive", "constitutional"}
    assert not any("founder" in p.value for p in GoalProvenance)

    fields = {f for f in GoalCommitment.__dataclass_fields__}
    assert "asserter" in fields and "provenance" in fields


def test_the_asserter_is_recorded_byte_identical(tmp_path):
    """L1 at the goal layer. Recorded AS DECLARED - never verified, never
    normalized; this ledger cannot check that a name is who it says it is."""
    weird = "  Founder / Hubert :: session 2026-08-03  \t"
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger, asserter=weird)
    assert goal.asserter == weird
    assert _lines(ledger)[0]["asserter"] == weird


def test_level_is_stored_but_no_mutation_class_is_enforced(tmp_path):
    """res.1 / DECLARED OUT. **The ledger STORES `level`; it does not enforce a
    mutation class from it.**

    The differential thresholds by level are arbitration/adoption-era work.
    Storing a field is not the same as policing it, and conflating the two is
    how a store quietly becomes a governor.
    """
    ledger = _ledger(tmp_path)
    for level in GoalLevel:
        goal = _ordinary(ledger, level=level, desired_state=f"at {level.value}")
        assert goal.level is level

    source = (REPO / MODULE).read_text(encoding="utf-8")
    tree = _tree()
    comparisons = [n for n in ast.walk(tree)
                   if isinstance(n, ast.Compare)
                   and any(isinstance(c, ast.Attribute)
                           and c.attr in {"ROOT", "EPOCH", "PROJECT", "IMMEDIATE"}
                           for c in ast.walk(n))]
    assert comparisons == [], (
        "the ledger branches on `level` - enforcing a mutation class is "
        "arbitration-era work and is declared OUT of this ruling")


def test_internal_drive_is_permitted_but_has_no_producer_today(tmp_path):
    """res.1's stated distinction: INTERNAL_DRIVE is NOT hard-barred like the
    QL3 kinds - the barrier there is a LAW about world agency, whereas this is
    a mechanism that does not exist yet.

    **Any INTERNAL_DRIVE record appearing before Q3 is a FINDING**, and the
    docstring says so; the ledger does not refuse it.
    """
    ledger = _ledger(tmp_path)
    goal = _ordinary(ledger, provenance=GoalProvenance.INTERNAL_DRIVE)
    assert goal.provenance is GoalProvenance.INTERNAL_DRIVE

    source = (REPO / MODULE).read_text(encoding="utf-8")
    assert "INTERNAL_DRIVE HAS NO LEGITIMATE PRODUCER TODAY" in source
