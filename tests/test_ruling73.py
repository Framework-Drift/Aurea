"""
test_ruling73.py - GOAL ARBITRATION (Ruling 73 / Docket Q item Q2).

Manifest forty-second addendum, 2026-08-03.

    The selector selects and records. It closes nothing, grants nothing,
    and draws nothing.

THE RED-FIRST WATCH IS A COLLECTION ERROR AND IS STATED AS ONE.
`src/goals/goal_arbitration.py` did not exist at `7da13d86`, so every pin
importing it fails at COLLECTION there rather than on an assertion - the honest
situation Rulings 61, 63, 70 and 72 each recorded for their own new modules.
**The mutation slate carries this pass's verification weight.**

=====================================================================
A REPORTED DIVERGENCE, MEASURED RATHER THAN ARGUED - READ THIS FIRST
=====================================================================
The ruling's res.5 keys rung 2 (OLDEST_UNRESOLVED) on the GLC ordinal. **GLC
ordinals are UNIQUE per commitment**, so with two or more candidates rung 2
always yields a unique leader, and rungs 3, 4 and 5 are UNREACHABLE through
`select()`.

That contradicts two of the ruling's own pins:

  * PIN (b) asks for "cases decided at rungs 2, 4, and 5". Only rung 2 (and
    SOLE_CANDIDATE) is reachable, so cases at rungs 4 and 5 cannot be
    constructed through the public surface.
  * PIN (f) asks for ALTERNATION between two roots via least-recently-examined.
    With rung 2 total, `GLC-0001` is selected every time, forever.

**WITNESSED, NOT ARGUED:** six consecutive examinations against the two seed
roots all returned `GLC-0001` at basis `oldest_unresolved`; rung keys measured
directly are `[0,0]` / `[1,2]` / `[0,0]` / `[-1,-1]` / `['GLC-0001','GLC-0002']`
- rung 2 discriminating is what closes the ladder early.

**NOTHING IS IMPROVISED TO PAPER OVER IT.** Repairing it means deciding what
"oldest unresolved" keys on, which is a semantic decision this pass does not
own (§7: the corpus does not specify it and inventing it is barred). So:

  * the rungs' OWN RULES are pinned at UNIT level, where they are correct and
    testable - the never-examined-first rule and the stable-identifier backstop
    both work exactly as ruled;
  * the UNREACHABILITY is pinned as the measured finding, so it cannot be
    forgotten and so the pin reddens the day rung 2's semantics are ruled on;
  * pin (f)'s alternation stands as ONE strict-xfail WITNESS, which is this
    house's own mechanism for a measured, reported, unrepaired defect awaiting
    a named ruling (CLAUDE.md §4). **It turns green the day the ladder is
    corrected, and the suite will say so.**

COINS NOTHING beyond the ruling's own `DecidingBasis` vocabulary and the EXM
prefix: no threshold, no weight, no score anywhere in this module.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.goals.goal_arbitration import (CANDIDATE_STATUSES, LADDER,
                                        DecidingBasis, ExaminationLogUnreadable,
                                        FocusPersistence, GoalArbiter,
                                        GoalExamination, Selection,
                                        _LadderContext,
                                        _rung_least_recently_examined,
                                        _rung_oldest_unresolved,
                                        _rung_review_horizon,
                                        _rung_stable_identifier,
                                        _rung_unmet_dependency)
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalOutcome, GoalProvenance, GoalStatus,
                                   declared, standing, supersession_only)

MODULE = Path("src/goals/goal_arbitration.py")
REPO = Path(__file__).resolve().parents[1]


def _tree() -> ast.Module:
    return ast.parse((REPO / MODULE).read_text(encoding="utf-8"))


def _seeded(tmp_path, name="g"):
    """A ledger with the two seed roots, and an arbiter over a fresh log."""
    ledger = GoalLedger(ledger_path=str(tmp_path / f"{name}.jsonl"))
    ledger.ensure_genesis()
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / f"{name}_exm.jsonl"))
    return ledger, arbiter


def _project(ledger, state, **kw):
    params = dict(desired_state=state, kind=GoalKind.RESEARCH,
                  level=GoalLevel.PROJECT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="tester",
                  completion_criteria=declared("done"))
    params.update(kw)
    return ledger.commit(**params)


def _ctx(arbiter):
    return arbiter._context()


# =====================================================================
# (a) DETERMINISM AND PERMUTATION INVARIANCE - Ruling 71's pins
# =====================================================================

def test_a_identical_state_yields_an_identical_selection(tmp_path):
    """PIN (a). **Ruling 71 at the goal layer.**

    A stochastic selector biases what the system can come to know, invisibly -
    the class BAR §3 exists to bar. Repeated selection over unchanged state
    must be identical in BOTH the choice and its basis.
    """
    _, arbiter = _seeded(tmp_path)
    first = arbiter.select()
    for _ in range(25):
        again = arbiter.select()
        assert again == first, "selection is not deterministic"
        assert again.deciding_basis is first.deciding_basis


def test_a_selection_is_invariant_under_candidate_permutation(tmp_path,
                                                              monkeypatch):
    """PIN (a), the permutation half - and it is FORCED, not assumed.

    The candidate set is sorted before the ladder runs, so input order cannot
    reach the outcome. Driven by feeding the ledger's commitments back in
    REVERSED order: without the sort, a rung that ties would let arrival order
    decide.
    """
    ledger, arbiter = _seeded(tmp_path)
    _project(ledger, "third")
    baseline = arbiter.select()

    real = ledger.commitments

    def reversed_commitments():
        return tuple(reversed(real()))

    monkeypatch.setattr(ledger, "commitments", reversed_commitments)
    permuted = arbiter.select()

    assert permuted == baseline, (
        "candidate arrival order changed the selection - the ladder is not "
        "permutation-invariant")
    assert permuted.candidate_goal_ids == baseline.candidate_goal_ids


def test_a_no_stochastic_machinery_is_imported():
    """PIN (a) as IMPORT-ABSENCE (Ruling 71 res.1).

    Not "does not sample" but CANNOT: the names are not in scope.
    """
    imported = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.update(node.module.split("."))
            for alias in node.names:
                imported.add(alias.name)
    for forbidden in ("random", "secrets", "numpy", "sample", "shuffle",
                      "choice", "randint", "uniform"):
        assert forbidden not in imported, (
            f"stochastic machinery `{forbidden}` is reachable - Ruling 71 bars "
            f"a draw from goal selection")


# =====================================================================
# (b) THE LADDER - order as SHAPE, rungs as BEHAVIOR
# =====================================================================

def test_b_the_ladder_order_is_declared_data_in_the_ruled_order():
    """PIN (b), STRUCTURAL. Ruling 71's declared tie-key order, readable.

    The ladder is declared DATA rather than a chain of branches precisely so
    its order is inspectable - a reordering is then a visible edit to a literal
    rather than a subtle rearrangement of control flow.
    """
    assert [basis for basis, _ in LADDER] == [
        DecidingBasis.UNMET_DEPENDENCY,
        DecidingBasis.OLDEST_UNRESOLVED,
        DecidingBasis.REVIEW_HORIZON,
        DecidingBasis.LEAST_RECENTLY_EXAMINED,
        DecidingBasis.STABLE_IDENTIFIER,
    ]

    # And the SOURCE order matches, so the pin cannot pass against a module
    # that builds the tuple dynamically in some other order at import time.
    # `LADDER` carries a type annotation, so it is an `AnnAssign` (one
    # `.target`) and not an `Assign` (a list of `.targets`) - the first draft
    # of this scan looked only for `Assign` and silently found NOTHING, which
    # is the quietest way for a structural pin to pass while measuring nothing.
    source_order = []
    for node in ast.walk(_tree()):
        target = None
        if isinstance(node, ast.AnnAssign):
            target = node.target
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "LADDER":
            for element in node.value.elts:
                source_order.append(element.elts[0].attr)
    assert source_order, "the LADDER literal was not found - the scan is blind"
    assert source_order == ["UNMET_DEPENDENCY", "OLDEST_UNRESOLVED",
                            "REVIEW_HORIZON", "LEAST_RECENTLY_EXAMINED",
                            "STABLE_IDENTIFIER"]


def test_b_rungs_one_and_three_tie_through_by_substrate(tmp_path):
    """PIN (b), the TIE-THROUGH half. **VACUOUS BY SUBSTRATE, and honest.**

    No dependency field and no review-horizon field exist on any record, so
    these rungs tie ALL candidates - deterministically, which is what makes
    tying honest rather than arbitrary. They are present as SHAPE because
    Ruling 71 declared a five-rung ladder, and a four-rung implementation would
    be a different ladder wearing the ruled one's name.
    """
    ledger, arbiter = _seeded(tmp_path)
    _project(ledger, "third")
    candidates = arbiter.candidates()
    context = _ctx(arbiter)
    assert len(candidates) == 3

    for rung in (_rung_unmet_dependency, _rung_review_horizon):
        keys = {rung(c, context) for c in candidates}
        assert len(keys) == 1, (
            f"{rung.__name__} discriminated; it has no substrate to "
            f"discriminate on")

    # And the fields they would read genuinely do not exist - the pin is about
    # the SUBSTRATE, not about the current bodies.
    fields = set(candidates[0].__dataclass_fields__)
    assert not any("depend" in f for f in fields)
    assert not any("horizon" in f for f in fields)


def test_b_rung_two_decides_and_prefers_the_lowest_ordinal(tmp_path):
    """PIN (b), a case decided at RUNG 2 - the reachable rung."""
    ledger, arbiter = _seeded(tmp_path)
    selection = arbiter.select()
    assert selection.deciding_basis is DecidingBasis.OLDEST_UNRESOLVED
    assert selection.selected_goal_id == "GLC-0001"


def test_b_rung_two_parses_ordinals_with_the_anchored_pattern(tmp_path):
    """PIN (b). Ruling 64's discipline: `GLC-00010` must not read as `GLC-0001`.

    Driven at the rung directly, because the public surface cannot mint an id
    that would expose a slicing bug.
    """
    _, arbiter = _seeded(tmp_path)
    context = _ctx(arbiter)

    class _Fake:
        def __init__(self, goal_id):
            self.goal_id = goal_id

    assert context.ordinal_of("GLC-0001") == 1
    assert context.ordinal_of("GLC-00010") == 10
    assert context.ordinal_of("GLC-0042") == 42
    # An id this module cannot parse sorts LAST rather than being guessed at.
    assert context.ordinal_of("not-an-id") > 10 ** 12
    assert (_rung_oldest_unresolved(_Fake("GLC-0007"), context) == 7)


def test_b_rung_four_sorts_a_never_examined_goal_first(tmp_path):
    """PIN (b) / PIN (f)'s RULE, at unit level - **where it is reachable.**

    *The least recently examined thing is the thing never examined.* The rung's
    own rule is correct and is pinned here; that `select()` cannot currently
    reach it is the reported divergence, pinned separately below.
    """
    ledger, arbiter = _seeded(tmp_path)
    arbiter.examine()                      # GLC-0001 becomes examined
    context = _ctx(arbiter)

    candidates = {c.goal_id: c for c in arbiter.candidates()}
    examined = _rung_least_recently_examined(candidates["GLC-0001"], context)
    never = _rung_least_recently_examined(candidates["GLC-0002"], context)

    assert never < examined, "a never-examined goal must sort FIRST"
    assert never == -1
    assert examined == 1, "the rung reads the EXM ordinal, not a wall clock"


def test_b_rung_five_is_a_total_order_backstop(tmp_path):
    """PIN (b), a case decided at RUNG 5's RULE, at unit level.

    Ids are unique, so this rung can never tie - it is what guarantees the
    ladder always selects rather than handing the question back to its caller,
    which is where nondeterminism gets in.
    """
    ledger, arbiter = _seeded(tmp_path)
    _project(ledger, "third")
    context = _ctx(arbiter)
    candidates = arbiter.candidates()

    keys = [_rung_stable_identifier(c, context) for c in candidates]
    assert len(set(keys)) == len(keys), "the backstop tied - ids are not unique"
    assert keys == sorted(keys)


def test_b_the_recorded_basis_is_the_rung_that_made_the_leader_unique(tmp_path):
    """PIN (b). SOLE_CANDIDATE when the ladder never ran; a rung otherwise."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "solo.jsonl"))
    _project(ledger, "only one")
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "solo_exm.jsonl"))

    selection = arbiter.select()
    assert selection.deciding_basis is DecidingBasis.SOLE_CANDIDATE
    assert selection.candidate_goal_ids == (selection.selected_goal_id,)

    _project(ledger, "a second")
    assert arbiter.select().deciding_basis is DecidingBasis.OLDEST_UNRESOLVED


# =====================================================================
# THE REPORTED DIVERGENCE, PINNED AS THE MEASURED FINDING
# =====================================================================

def test_divergence_rung_two_is_total_so_rungs_three_to_five_are_unreachable(
        tmp_path):
    """**THE REPORTED DIVERGENCE, PINNED SO IT CANNOT BE FORGOTTEN.**

    Rung 2 keys on the GLC ordinal, which is unique per commitment, so among
    two or more candidates it always yields a unique leader. Rungs 3, 4 and 5
    are therefore unreachable through `select()` - a DIFFERENT condition from
    rungs 1 and 3's vacancy-by-substrate, and one with a different remedy.

    **THIS PIN REDDENS THE DAY RUNG 2'S SEMANTICS ARE RULED ON**, which is
    exactly when someone needs to notice that the reachable basis set changed.
    """
    ledger, arbiter = _seeded(tmp_path)
    for index in range(4):
        _project(ledger, f"extra {index}")

    context = _ctx(arbiter)
    candidates = arbiter.candidates()
    assert len(candidates) == 6

    keys = [_rung_oldest_unresolved(c, context) for c in candidates]
    assert len(set(keys)) == len(keys), (
        "rung 2 no longer discriminates every candidate - the ladder's "
        "reachability has changed and this ruling's divergence may be resolved")

    # Every multi-candidate selection therefore lands on rung 2.
    bases = set()
    for _ in range(6):
        bases.add(arbiter.examine().deciding_basis)
    assert bases == {DecidingBasis.OLDEST_UNRESOLVED}


def test_divergence_a_standing_goal_holds_focus_rather_than_rotating(tmp_path):
    """**THE CONSEQUENCE, WITNESSED.** Persistent focus, not rotation.

    Six examinations against the two seed roots all select `GLC-0001`. This is
    what the ladder as ruled produces, and it is recorded here as the measured
    behaviour rather than described as intended behaviour - the liveness
    derivation below is what makes it visible to a future consumer.
    """
    ledger, arbiter = _seeded(tmp_path)
    selected = [arbiter.examine().selected_goal_id for _ in range(6)]

    assert selected == ["GLC-0001"] * 6
    assert arbiter.examinations_for("GLC-0002") == ()


@pytest.mark.xfail(strict=True, reason=(
    "RULING 73 PIN (f), UNWRITABLE AS SPECIFIED - the ONE strict-xfail witness "
    "this pass lands. res.5 keys rung 2 on the unique GLC ordinal, so rung 4 "
    "(least-recently-examined) is unreachable and two roots never alternate. "
    "MEASURED, REPORTED, UNREPAIRED, awaiting a ruling on rung 2's semantics "
    "(CLAUDE.md §4's standing for a witness). It turns GREEN the day the "
    "ladder is corrected, and the suite will say so."))
def test_f_two_roots_alternate_across_examinations(tmp_path):
    """PIN (f) AS THE RULING SPECIFIES IT - the witness.

    A fresh ledger with two roots selects deterministically; the second
    examination selects the OTHER root (least-recently-examined doing its
    work); the third returns to the first. Alternation.
    """
    _, arbiter = _seeded(tmp_path)
    first = arbiter.examine().selected_goal_id
    second = arbiter.examine().selected_goal_id
    third = arbiter.examine().selected_goal_id

    assert first != second, "the second examination must select the OTHER root"
    assert third == first, "the third must return - witnessed as alternation"


# =====================================================================
# (c) ARBITRATION NEVER CLOSES
# =====================================================================

CLOSING_CALLS = {"resolve", "record_evidence", "commit", "_commit",
                 "ensure_genesis"}


def _closing_calls_in(tree) -> list:
    return [f"{node.func.attr}:{node.lineno}" for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in CLOSING_CALLS]


def test_c_the_module_never_calls_a_closing_operation():
    """PIN (c), AS SHAPE. **Ruling 72's lesson applied IN ADVANCE.**

    Ruling 5's scanner flags `.commit()` on ANY receiver because a scanner that
    had to infer a receiver's type would eventually get it wrong. Ruling 72
    discovered that by having an invariant fire; this module was written so it
    never could. A selector that could close a goal would be able to declare
    its own work finished.
    """
    assert _closing_calls_in(_tree()) == [], (
        "arbitration reached a closing operation; closure is RESOLUTION, a "
        "goal-ledger append, and it is not this module's to perform")


def test_c_the_module_defines_no_method_named_commit():
    """PIN (c). The NAME would be wrong even if the body were harmless."""
    defined = {n.name for n in ast.walk(_tree())
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "commit" not in defined and "_commit" not in defined


def test_c_the_closing_scanner_actually_fires():
    """Ruling 32's answer to the vacuous-pin problem, with a benign control."""
    forbidden = ast.parse("ledger.resolve('G', o, 'c')\nx.commit()\n")
    benign = ast.parse("ledger.commitments()\nledger.derive_status('G')\n")
    assert _closing_calls_in(forbidden)
    assert _closing_calls_in(benign) == []


def test_c_examinations_leave_every_derived_status_unchanged(tmp_path):
    """PIN (c), BEHAVIORAL. **The goal ledger is BYTE-IDENTICAL afterwards.**

    Twelve examinations, three commitments, and not one byte of the ledger
    moves - the strongest available statement that arbitration closes nothing.
    """
    ledger, arbiter = _seeded(tmp_path)
    _project(ledger, "third")

    before_bytes = Path(ledger.ledger_path).read_bytes()
    before_status = {c.goal_id: ledger.derive_status(c.goal_id)
                     for c in ledger.commitments()}

    for _ in range(12):
        arbiter.examine()

    assert Path(ledger.ledger_path).read_bytes() == before_bytes, (
        "the goal ledger changed during arbitration")
    after_status = {c.goal_id: ledger.derive_status(c.goal_id)
                    for c in ledger.commitments()}
    assert after_status == before_status


# =====================================================================
# (d) NAME-DISJOINTNESS - the tree-wide enum census, as a pin
# =====================================================================

def _enum_members_by_file():
    """Every `Enum` subclass member in `src/`, by rglob.

    RGLOB rather than a module list, deliberately (Ruling 70's instrument
    lesson): the census must cover the module nobody has written yet, or it
    reports a disjointness that lapses the moment someone adds a file.
    """
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
    return found


def test_d_the_arbitration_vocabulary_collides_with_no_other_enum():
    """PIN (d). **The census that earned its keep before a line was written.**

    Docket Q's registration described the capability as "focus, hold, or
    defer", and this census found `DEFERRED` live in `racm.Verdict` with
    `_defer` / `is_deferred` / `deferred_cycles` throughout `racm.py`. That
    vocabulary is RACM's. A collision here is a STOP, never an improvised
    rename - two enums sharing a member name is how two senses of one word get
    conflated at a boundary (Ruling 30's exact defect).
    """
    census = _enum_members_by_file()
    ours = {m.name for m in DecidingBasis}

    collisions = {}
    for member in ours:
        owners = [o for o in census.get(member, [])
                  if not o.startswith("src/goals/goal_arbitration.py")]
        if owners:
            collisions[member] = owners
    assert collisions == {}, (
        f"the arbitration vocabulary collides: {collisions}")


def test_d_the_word_defer_appears_nowhere_in_this_module():
    """PIN (d), the specific collision the census caught. **It is RACM's.**

    The registration's "defer" sense here is exclusion at a rung, which
    `deciding_basis` already reports.
    """
    source = (REPO / MODULE).read_text(encoding="utf-8").lower()
    # The module docstring EXPLAINS why the word is absent, so the scan is over
    # code identifiers rather than prose - the substring-scanner lesson.
    identifiers = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            identifiers.add(node.name)
        elif isinstance(node, ast.arg):
            identifiers.add(node.arg)
    assert not any("defer" in name.lower() for name in identifiers), (
        "`defer` entered this module's vocabulary; it is RACM's")


def test_d_the_census_instrument_actually_finds_known_enums():
    """The census's own control - a scan that has stopped scanning must fail
    HERE rather than report a comfortable zero."""
    census = _enum_members_by_file()
    assert "DEFERRED" in census, "the census cannot see racm.Verdict"
    assert any("racm.py" in owner for owner in census["DEFERRED"])
    assert "GLOBAL" in census and "STRUCTURAL" in census
    assert len(census) > 100, f"census implausibly small: {len(census)}"


# =====================================================================
# (e) THE MINT AT THE THIRD PREFIX
# =====================================================================

def test_e_the_mint_uses_the_shared_helper(tmp_path):
    """PIN (e). Ruling 69's helper, IMPORTED - the THIRD consumer."""
    imported = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imported.add(f"{node.module}.{alias.name}")
    assert "src.utils.ledger_mint.derive_max_ordinal" in imported
    assert "src.utils.ledger_mint.mint_lock" in imported
    assert "src.utils.ledger_mint.ordinal_pattern" in imported

    defined = {n.name for n in ast.walk(_tree())
               if isinstance(n, ast.FunctionDef)}
    assert "derive_max_ordinal" not in defined


def test_e_exm_ids_are_file_derived_and_sequential(tmp_path):
    _, arbiter = _seeded(tmp_path)
    ids = [arbiter.examine().examination_id for _ in range(3)]
    assert ids == ["EXM-0001", "EXM-0002", "EXM-0003"]

    fresh = GoalArbiter(arbiter.ledger, log_path=str(arbiter.log_path))
    assert fresh.examine().examination_id == "EXM-0004", (
        "a new instance resumes from the FILE, not from a counter it never had")


def test_e_the_torn_line_property_holds_at_the_exm_prefix(tmp_path):
    """PIN (e). Ruling 69 res.2 at a new prefix: an ordinal on a TORN,
    UNPARSEABLE line is still seen and never reissued."""
    _, arbiter = _seeded(tmp_path)
    arbiter.examine()
    with open(arbiter.log_path, "a", encoding="utf-8") as handle:
        handle.write('{"kind_of_record": "examination", "examination_id": "EXM-0042"')

    assert arbiter.examine().examination_id == "EXM-0043"


def test_e_an_unreadable_existing_log_refuses_typed(tmp_path, monkeypatch):
    """PIN (e). Ruling 53's sentinel - it RAISES rather than minting from an
    unknown floor."""
    import builtins
    _, arbiter = _seeded(tmp_path)
    arbiter.examine()

    real_open = builtins.open
    target = str(arbiter.log_path)

    def failing(file, mode="r", *args, **kwargs):
        if str(file) == target and "r" in mode:
            raise OSError("simulated read failure")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing)
    with pytest.raises(ExaminationLogUnreadable, match="EXM"):
        arbiter._next_id()


def test_e_the_mint_and_the_append_happen_inside_the_lock():
    """PIN (e), ADDED AFTER A MUTATION SURVIVOR - the same real gap Ruling 72
    found at its own mint, recurring here for the same reason.

    Dropping `with mint_lock(...)` survives every behavioural pin, and it has
    to: the lock guards CONCURRENT mints, and every mint re-derives from the
    file, so a single-threaded run cannot tell a held lock from a missing one.

    **DECLARED STRUCTURAL PER RULING 17**, and it is the right instrument
    rather than a weaker one: the property IS a lexical scope - that the mint
    and the append sit inside the `with` block - so source is where it is true
    or false. A threaded probe would be flaky and could pass by luck.
    """
    examine = next(n for n in ast.walk(_tree())
                   if isinstance(n, ast.FunctionDef) and n.name == "examine")

    guarded = [w for w in ast.walk(examine) if isinstance(w, ast.With)
               and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id == "mint_lock"
                       for item in w.items
                       for c in ast.walk(item.context_expr))]
    assert guarded, "`examine` does not take the mint lock at all"

    calls = {n.func.attr for n in ast.walk(guarded[0])
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "_next_id" in calls, "the MINT happens outside the lock"
    assert "_append" in calls, (
        "the APPEND happens outside the lock - deriving inside it and "
        "appending outside leaves exactly the race Ruling 69 closes")


def test_e_no_cached_ordinal_exists_before_or_after_minting(tmp_path):
    """PIN (e). Ruling 69 res.1: the counter is GONE, not merely unused."""
    _, arbiter = _seeded(tmp_path)
    assert not hasattr(arbiter, "_seq")
    arbiter.examine()
    assert not hasattr(arbiter, "_seq")

    offenders = [n.lineno for n in ast.walk(_tree())
                 if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                 for t in ([n.target] if getattr(n, "target", None) is not None
                           else getattr(n, "targets", []))
                 if isinstance(t, ast.Attribute) and t.attr == "_seq"]
    assert offenders == []


# =====================================================================
# (f) SELECTION ACROSS EXAMINATIONS  (see the xfail witness above)
# =====================================================================

def test_f_a_fresh_state_selects_deterministically(tmp_path):
    """PIN (f), the half that IS writable today."""
    _, first = _seeded(tmp_path, "a")
    _, second = _seeded(tmp_path, "b")
    assert (first.select().selected_goal_id
            == second.select().selected_goal_id == "GLC-0001")


def test_f_hold_is_derivable_across_consecutive_records(tmp_path):
    """res.6: HOLD is re-selection, DERIVABLE by comparing records, never
    stored. There is no HOLD member and no stored flag - the comparison is the
    whole mechanism."""
    _, arbiter = _seeded(tmp_path)
    for _ in range(3):
        arbiter.examine()

    records = arbiter.examinations()
    held = [b.selected_goal_id == a.selected_goal_id
            for a, b in zip(records, records[1:])]
    assert held == [True, True]
    assert not any("hold" in m.name.lower() for m in DecidingBasis)


# =====================================================================
# (g) CANDIDACY BY DERIVATION
# =====================================================================

def test_g_a_resolved_commitment_leaves_the_candidate_set(tmp_path):
    """PIN (g). Out BY DERIVATION - no stored flag is read, and none exists."""
    ledger, arbiter = _seeded(tmp_path)
    goal = _project(ledger, "resolvable")
    assert goal.goal_id in {c.goal_id for c in arbiter.candidates()}

    ledger.resolve(goal.goal_id, GoalOutcome.COMPLETED, "completion_criteria")

    assert ledger.derive_status(goal.goal_id) is GoalStatus.RESOLVED
    assert goal.goal_id not in {c.goal_id for c in arbiter.candidates()}


def test_g_a_superseded_root_leaves_the_candidate_set(tmp_path):
    """PIN (g), the other exclusion - also by derivation."""
    ledger, arbiter = _seeded(tmp_path)
    assert "GLC-0001" in {c.goal_id for c in arbiter.candidates()}

    ledger.commit(desired_state="A revised first root.",
                  kind=GoalKind.RESEARCH, level=GoalLevel.ROOT,
                  provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                  asserter="founder", completion_criteria=standing(),
                  abandonment_criteria=supersession_only(),
                  supersedes_goal_id="GLC-0001")

    assert ledger.derive_status("GLC-0001") is GoalStatus.SUPERSEDED
    assert "GLC-0001" not in {c.goal_id for c in arbiter.candidates()}


def test_g_an_evidence_bearing_commitment_remains_a_candidate(tmp_path):
    """PIN (g). Evidence does not close a goal, so it does not end candidacy."""
    ledger, arbiter = _seeded(tmp_path)
    ledger.record_evidence("GLC-0001", ["CLM-0001"])
    assert ledger.derive_status("GLC-0001") is GoalStatus.EVIDENCE_BEARING
    assert "GLC-0001" in {c.goal_id for c in arbiter.candidates()}
    assert set(CANDIDATE_STATUSES) == {GoalStatus.COMMITTED,
                                       GoalStatus.EVIDENCE_BEARING}


def test_g_candidacy_routes_through_derive_status_only():
    """PIN (g), AST. No status is read except through the ledger's derivation.

    A stored-flag read would be Ruling 63's cached projection and Ruling 65's
    stored derivation, both of which this house has already paid for.
    """
    source = (REPO / MODULE).read_text(encoding="utf-8")
    assert "derive_status" in source
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Attribute) and node.attr in {
                "status", "is_resolved", "is_superseded", "resolved",
                "superseded"}:
            raise AssertionError(
                f"a stored status surface is read at line {node.lineno}")


def test_g_the_candidate_filter_is_level_blind():
    """res.4: the ladder is LEVEL-BLIND today - the ledger stores `level` and
    does not police it (Ruling 72), and this module does not read it. Level
    precedence classes are a future arbitration ruling."""
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Attribute):
            assert node.attr != "level", (
                f"the arbiter reads `level` at line {node.lineno}; level-based "
                f"precedence is a future ruling, not this module's")


def test_g_adoption_does_not_gate_candidacy(tmp_path):
    """res.4, STATED AS A RULING RATHER THAN AN OVERSIGHT.

    `GoalAdoption` has no producer path (Ruling 72 res.6), so gating candidacy
    on adoption would ship a selector with a structurally EMPTY domain - a
    vacuous build that passes its tests by never selecting anything. The seed
    roots are unadopted PROPOSALS and they are candidates.
    """
    ledger, arbiter = _seeded(tmp_path)
    assert {c.goal_id for c in arbiter.candidates()} == {"GLC-0001", "GLC-0002"}
    assert arbiter.select() is not None

    # Scanned by AST, not by substring: this module's docstring EXPLAINS why
    # adoption does not gate candidacy and must stay free to say so. A lexical
    # scan flagged that prose - the substring-scanner false positive, whose
    # settled remedy is to sharpen the instrument rather than delete correct
    # documentation (Ruling 63's precedent).
    named = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Name):
            named.add(node.id)
        elif isinstance(node, ast.Attribute):
            named.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                named.add(alias.name)
    assert "GoalAdoption" not in named, (
        "the arbiter's CODE reaches GoalAdoption; adoption does not gate "
        "candidacy and this module has no business reading it")


def test_g_an_empty_field_selects_nothing_and_records_nothing(tmp_path):
    """A legitimate state, not an error - but an examination carries a
    selection, so `examine` refuses and writes no line."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "empty.jsonl"))
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "empty_exm.jsonl"))

    assert arbiter.candidates() == ()
    assert arbiter.select() is None
    with pytest.raises(ValueError, match="no commitment stands"):
        arbiter.examine()
    assert not Path(arbiter.log_path).exists()


# =====================================================================
# (h) LIVENESS - the MEASUREMENT, and it never gates
# =====================================================================

def test_h_the_tally_is_correct_on_a_constructed_sequence(tmp_path):
    """PIN (h). Three consecutive selections, no evidence -> count 3, progress
    False; append evidence -> progress True."""
    ledger, arbiter = _seeded(tmp_path)
    for _ in range(3):
        arbiter.examine()

    measured = arbiter.focus_persistence("GLC-0001")
    assert isinstance(measured, FocusPersistence)
    assert measured.consecutive_selections == 3
    assert measured.progress_recorded is False

    ledger.record_evidence("GLC-0001", ["CLM-0001"], "something moved")
    assert arbiter.focus_persistence("GLC-0001").progress_recorded is True
    assert arbiter.focus_persistence("GLC-0001").consecutive_selections == 3


def test_h_a_never_selected_goal_reports_zero(tmp_path):
    _, arbiter = _seeded(tmp_path)
    arbiter.examine()
    measured = arbiter.focus_persistence("GLC-0002")
    assert measured.consecutive_selections == 0
    assert measured.progress_recorded is False


def test_h_the_run_counts_back_only_while_the_selection_holds(tmp_path):
    """PIN (h). The run is the TRAILING consecutive stretch, not a lifetime
    total - an interruption ends it, which is what makes it a liveness signal
    rather than a popularity count."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "g.jsonl"))
    first = _project(ledger, "first")
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "e.jsonl"))
    arbiter.examine()
    arbiter.examine()

    # Close the leader; the field moves to the next commitment.
    ledger.resolve(first.goal_id, GoalOutcome.COMPLETED, "completion_criteria")
    _project(ledger, "second")
    arbiter.examine()

    assert arbiter.focus_persistence(first.goal_id).consecutive_selections == 0
    assert arbiter.examinations()[-1].selected_goal_id != first.goal_id


def test_h_the_tally_never_gates(tmp_path):
    """PIN (h). **A count REPORTS; it never GATES** (§9 standing bar #5).

    Docket H's instrument at a new tally: no comparison of either field against
    any literal anywhere in `src/`. Scanned tree-wide, because the day a
    consumer appears is exactly the day this would be added there.
    """
    fields = {"consecutive_selections", "progress_recorded"}
    offenders = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            names = {n.attr for n in ast.walk(node)
                     if isinstance(n, ast.Attribute)}
            names |= {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            if names & fields:
                offenders.append(
                    f"{path.relative_to(REPO).as_posix()}:{node.lineno}")
    assert offenders == [], (
        f"the liveness tally is compared against something at {offenders} - a "
        f"count reports, it never gates; enforcement is Q3's through QL5")


def test_h_no_threshold_literal_lives_beside_the_measurement():
    """PIN (h). The record carries two facts and no cutoff to judge them by."""
    assert set(FocusPersistence.__dataclass_fields__) == {
        "goal_id", "consecutive_selections", "progress_recorded"}


# =====================================================================
# (i) QL0 / §3 ABSENCE
# =====================================================================

FORBIDDEN_IMPORTS = {
    "sae", "codex", "racm", "reflex_grid", "rb_system", "dee", "cae",
    "doctrine_spine", "scar_logic_core", "nova", "tca_core", "tcaml",
    "hail", "ore", "truth_packet", "echonet", "aurea_core", "spl", "ril",
    "black_sphere", "csa", "veiled_thread", "sbsre", "compass", "echo_memory",
    "random", "secrets", "numpy", "urllib", "requests", "socket", "subprocess",
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


def test_i_the_arbiter_imports_nothing_it_could_command():
    """PIN (i). **QL0 AS STRUCTURE** - a goal grants no authority, and
    selection grants less. Ruling 70's enforcement-by-scope, two dockets on."""
    offenders = sorted(_imported_tokens() & FORBIDDEN_IMPORTS)
    assert offenders == [], f"arbitration imports {offenders}"


def test_i_the_import_scanner_actually_fires():
    def tokens_of(source):
        found = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module:
                found.update(node.module.split("."))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    found.update(alias.name.split("."))
        return found

    assert tokens_of("from src.expansion.sae import SAE\nimport random\n") & \
        FORBIDDEN_IMPORTS
    assert not (tokens_of("from src.goals.goal_ledger import GoalStatus\n")
                & FORBIDDEN_IMPORTS)


def test_i_no_simulation_machinery_exists():
    """res.'s DECLARED OUT: **SAE owns simulation** (caution (ii)). Consequence
    modelling of any kind is absent, pinned."""
    defined = {n.name.lower() for n in ast.walk(_tree())
               if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for word in ("simulate", "project_outcome", "forecast", "predict",
                 "model_consequence", "rollout"):
        assert not any(word in name for name in defined), (
            f"simulation machinery `{word}` appeared; SAE owns simulation")


def test_i_the_examination_record_carries_no_scalar_standing():
    """PIN (i). QL4's absence extends to the examination record."""
    forbidden = {"priority", "confidence", "weight", "score", "rank",
                 "importance", "urgency", "utility"}
    for record in (GoalExamination, FocusPersistence, Selection):
        for field_name in record.__dataclass_fields__:
            assert not any(w in field_name.lower() for w in forbidden), (
                f"{record.__name__}.{field_name} is a scalar standing")


def test_i_persisted_lines_carry_no_numbers(tmp_path):
    """PIN (i), the durable half - measured on the BYTES."""
    _, arbiter = _seeded(tmp_path)
    arbiter.examine()

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

    for line in Path(arbiter.log_path).read_text(encoding="utf-8").splitlines():
        assert numbers(json.loads(line)) == []


def test_i_nothing_in_src_consumes_the_arbiter():
    """res.: **the module is unwired and stays unwired this pass.**

    Q3's drive wiring is the consumer, and it is its own ruling. This pin
    reddens the day something imports the arbiter - which is exactly when that
    wiring needs a ruling rather than arriving as a convenience.
    """
    consumers = []
    for path in sorted((REPO / "src").rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "goal_arbitration.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "goal_arbitration" in node.module:
                    consumers.append(path.relative_to(REPO).as_posix())
    assert consumers == [], f"the arbiter acquired a consumer at {consumers}"


# =====================================================================
# WRITER CONFORMANCE AND THE RECORD
# =====================================================================

def test_the_writer_conforms_to_batch_66():
    """No `default=`, `allow_nan=False`, append-only."""
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("dumps", "dump")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "json"):
            kwargs = {kw.arg for kw in node.keywords}
            assert "default" not in kwargs
            assert "allow_nan" in kwargs

    modes = []
    for node in ast.walk(_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open" and len(node.args) > 1
                and isinstance(node.args[1], ast.Constant)):
            modes.append(node.args[1].value)
    assert modes and set(modes) <= {"a", "r"}


def test_a_non_canonical_leaf_is_refused_before_the_write(tmp_path):
    """The validator runs BEFORE `mkdir` and BEFORE `open`."""
    ledger = GoalLedger(ledger_path=str(tmp_path / "g.jsonl"))
    ledger.ensure_genesis()
    arbiter = GoalArbiter(ledger, log_path=str(tmp_path / "deep" / "e.jsonl"))

    with pytest.raises(Exception):
        arbiter._append({"kind_of_record": "examination",
                         "junk": bytearray(b"not canonical")})
    assert not Path(arbiter.log_path).exists()
    assert not (tmp_path / "deep").exists()


def test_the_examination_record_is_frozen(tmp_path):
    _, arbiter = _seeded(tmp_path)
    examination = arbiter.examine()
    with pytest.raises(Exception):
        examination.selected_goal_id = "GLC-0002"


def test_a_selection_outside_its_own_candidate_set_is_refused():
    """A record nobody can recompute is not a record."""
    with pytest.raises(ValueError, match="not among the recorded candidates"):
        GoalExamination(examination_id="EXM-0001",
                        selected_goal_id="GLC-0009",
                        candidate_goal_ids=("GLC-0001",),
                        deciding_basis=DecidingBasis.SOLE_CANDIDATE)


def test_the_reader_never_coerces_an_unknown_basis(tmp_path):
    """A line carrying a basis outside the closed vocabulary contributes
    NOTHING - it is never coerced into a member."""
    _, arbiter = _seeded(tmp_path)
    arbiter.examine()
    with open(arbiter.log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "kind_of_record": "examination", "examination_id": "EXM-0500",
            "selected_goal_id": "GLC-0001",
            "candidate_goal_ids": ["GLC-0001"],
            "deciding_basis": "vibes",
        }) + "\n")

    assert [e.examination_id for e in arbiter.examinations()] == ["EXM-0001"]


def test_the_candidate_ids_are_ids_only():
    """Ruling 42: a live object here would be a handle into another owner's
    store."""
    with pytest.raises(TypeError, match="ID STRINGS ONLY"):
        GoalExamination(examination_id="EXM-0001",
                        selected_goal_id="GLC-0001",
                        candidate_goal_ids=(object(),),
                        deciding_basis=DecidingBasis.SOLE_CANDIDATE)
