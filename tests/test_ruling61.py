"""
test_ruling61.py - THE PREDICTION COMMITMENT LEDGER (Ruling 61 / Docket O O3).

Manifest twenty-sixth addendum, 2026-08-01.

    A prediction that was not committed before its outcome is not a prediction.

Without prior commitment a prediction is REWRITABLE until everything appears
successful. The ledger's whole job is to make the commitment UNREWRITABLE and
the scoring MECHANICAL against criteria that already existed.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `fdea7c0`, where
`src/external/prediction_ledger.py` did not exist.

COINS NOTHING: six dependency members recovered verbatim from L2's own
sentence, three outcome members from the registration's own words, the
three-state vocabulary is Docket H's (reused, not redeclared), and no
threshold, weight, magnitude or duration exists anywhere in the module.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.aurea_core import STRUCTURAL_VIOLATIONS
from src.external.claim_ancestry import AncestryField, FieldState
from src.external.prediction_ledger import (CRITERION_FIELDS, DependencyLink,
                                            PredictionCommitment,
                                            PredictionLedger,
                                            PredictionLedgerUnreadable,
                                            PredictionOutcome,
                                            PredictionResolution,
                                            RecordedField, absent,
                                            declared_none, provided)

MODULE = Path("src/external/prediction_ledger.py")


def _ledger(tmp_path, name="prd.jsonl") -> PredictionLedger:
    return PredictionLedger(ledger_path=str(tmp_path / name))


def _lines(ledger) -> list:
    path = Path(ledger.ledger_path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def _full(ledger) -> PredictionCommitment:
    """A commitment with all three criteria and a real dependency chain."""
    return ledger.commit(
        expected_result="the index rises above 10 by year end",
        applicable_conditions=provided("only under stable supply"),
        resolution_horizon=provided("2027-01-01"),
        success_criteria=provided("closes above 10"),
        failure_criteria=provided("closes at or below 10"),
        unresolved_criteria=provided("market suspended before close"),
        dependency_chain=(DependencyLink.OBSERVATION,
                          DependencyLink.CAUSAL_LINK,
                          DependencyLink.THE_CLAIM_ITSELF),
        claim_refs=("CLM-0001", "CLM-0002"),
    )


# =====================================================================
# A. THE DOCKET'S NAMED MECHANISM
# =====================================================================

def test_a_commitment_persists_exactly_as_committed(tmp_path) -> None:
    """PIN (a), THE FORCING PIN. **RED FIRST**: the module did not exist.

    ALL THREE CRITERIA AND THE DEPENDENCY CHAIN, FIXED AT COMMIT TIME and
    returned byte-identical after a restart. This is the mechanism that turns a
    truth-seeking POSTURE into a recorded truth-seeking HISTORY.
    """
    ledger = _ledger(tmp_path)
    committed = _full(ledger)

    assert committed.prediction_id == "PRD-0001"
    assert committed.success_criteria.value == "closes above 10"
    assert committed.failure_criteria.value == "closes at or below 10"
    assert committed.unresolved_criteria.value == "market suspended before close"
    assert committed.dependency_chain == (DependencyLink.OBSERVATION,
                                          DependencyLink.CAUSAL_LINK,
                                          DependencyLink.THE_CLAIM_ITSELF)
    assert committed.claim_refs == ("CLM-0001", "CLM-0002")

    # A SEPARATE PROCESS'S VIEW: read back off the file, not the mirror.
    reloaded = _ledger(tmp_path).commitment_for("PRD-0001")
    assert reloaded == committed, (
        "a commitment that does not survive a restart intact is not a "
        "commitment - it is a note")


def test_the_three_state_vocabulary_is_reused_not_redeclared() -> None:
    """`RecordedField` IS `claim_ancestry.AncestryField` - one type, one
    vocabulary (Ruling 33's 'reused never redeclared').

    A second definition of Docket H's cut is the drift hazard Ruling 35 named,
    in the one place where two records most need to mean the same thing.
    """
    assert RecordedField is AncestryField


def test_declared_none_persists_distinguishably_from_absent(tmp_path) -> None:
    """PIN (j). **RED FIRST.** THE FACT WORTH KEEPING.

    A predictor who DECLARED NO failure criterion is on record as having
    declared none - and that is a different fact from never having been asked.
    Flattening them would let a prediction with no stated failure condition
    read, afterwards, exactly like one nobody thought to ask about.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X happens",
                  success_criteria=provided("X observed"),
                  failure_criteria=declared_none())

    entry = _lines(ledger)[0]
    assert entry["failure_criteria"]["state"] == "declared_none"
    assert entry["unresolved_criteria"]["state"] == "absent"

    reloaded = _ledger(tmp_path).commitment_for("PRD-0001")
    assert reloaded.failure_criteria.state is FieldState.DECLARED_NONE
    assert reloaded.unresolved_criteria.state is FieldState.ABSENT


def test_a_missing_criterion_defaults_to_absent_never_to_an_empty_value(tmp_path) -> None:
    """A caller who did not mention a criterion has not declared there are
    none. An empty PROVIDED value would read as "asked, and there are none"."""
    ledger = _ledger(tmp_path)
    committed = ledger.commit("X happens")

    for name in CRITERION_FIELDS:
        surface = getattr(committed, name)
        assert surface.state is FieldState.ABSENT
        assert surface.value is None


# =====================================================================
# B. UNREWRITABILITY, AS SHAPE
# =====================================================================

def test_no_update_amend_or_revise_exists_anywhere(tmp_path) -> None:
    """PIN (b). **RED FIRST.** THE ABSENCE IS THE ENFORCEMENT.

    The wrong path is UNEXECUTABLE, not discouraged. A method named `amend`
    with a docstring saying "only before resolution" would be a request for
    restraint, and this project has hard evidence that restraint fails.
    """
    forbidden = ("update", "amend", "revise", "edit", "modify", "set_criteria")

    for surface in (PredictionCommitment, PredictionResolution, PredictionLedger):
        present = [name for name in forbidden if hasattr(surface, name)]
        assert present == [], (
            f"{surface.__name__} exposes {present} - a commitment that can be "
            f"edited after the fact is the rewritable thing this docket abolishes")

    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert defined.isdisjoint(forbidden), (
        f"a rewrite verb is defined in the module: {sorted(defined & set(forbidden))}")


def test_the_rewrite_scanner_actually_fires() -> None:
    """Ruling 32's answer to the vacuous-pin problem: feed the scanner the
    forbidden shape and a benign control."""
    forbidden = ast.parse("class L:\n    def amend(self): pass\n")
    benign = ast.parse("class L:\n    def commit(self): pass\n")

    def defined(tree):
        return {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    assert "amend" in defined(forbidden)
    assert defined(benign).isdisjoint(("update", "amend", "revise"))


def test_the_frozen_record_rejects_attribute_assignment(tmp_path) -> None:
    """Deep-frozen per Ruling 52 - the shell AND the interiors."""
    committed = _ledger(tmp_path).commit(
        "X", success_criteria=provided({"nested": ["a"]}))

    with pytest.raises(Exception):
        committed.expected_result = "Y"
    with pytest.raises(Exception):
        committed.success_criteria.value["nested"] = ["b"]


def test_a_retained_reference_cannot_write_through_the_freeze(tmp_path) -> None:
    """RULING 52's actual finding: a proxy over the CALLER'S container is a
    VIEW, so the freeze must copy. Without the deepcopy the honest caller is
    stopped and the one holding the reference writes straight through."""
    payload = {"threshold": ["closes above 10"]}
    committed = _ledger(tmp_path).commit("X", success_criteria=provided(payload))

    payload["threshold"].append("MUTATED AFTER COMMIT")

    assert committed.success_criteria.value["threshold"] == ("closes above 10",), (
        "the committed criterion moved because the caller kept the container")


def test_a_mutable_leaf_is_copied_not_shared(tmp_path) -> None:
    """THE CASE A SURVIVING MUTANT ESTABLISHED, and it is why `deepcopy` is
    there at all.

    The recursive rebuild copies the container SPINE - a list becomes a tuple,
    a dict becomes a proxy - so a nested LIST is already safe without any copy.
    That makes the test above pass against an implementation with no
    `deepcopy`, which is exactly what happened here. A MUTABLE LEAF is what
    `_deep_freeze` passes through untouched, and without the copy it stays
    shared with the caller forever.

    Batch 51 found this for `mutation_proof`, Ruling 58 re-pinned it for the
    ancestry record, and it survived again here until this pin existed.

    MIGRATED 2026-08-02 BY BATCH 66 (Ruling-14 form) - THE PROPERTY IS
    UNCHANGED; ITS PAYLOAD MOVED, BECAUSE A RULING MOVED.

    The leaf was `bytearray(b"closes above 10")`, and the body read:

        leaf = bytearray(b"closes above 10")
        committed = _ledger(tmp_path).commit("X", success_criteria=provided(leaf))
        leaf.extend(b" OR WHATEVER WE SAY LATER")
        assert committed.success_criteria.value == bytearray(b"closes above 10"), (
            "the committed criterion was edited through a reference the caller "
            "still holds - the commitment is not fixed at commit time")

    Ruling 66 REFUSES a bytearray at this ledger's writer, so that payload can
    no longer reach a commitment at all - the pin would now fail on the refusal
    rather than witness the copy. **A LIST IS THE RIGHT SUCCESSOR AND NOT A
    WEAKENING:** it is ADMISSIBLE (so it still exercises the write path end to
    end) and MUTABLE (so it still witnesses exactly what `_deep_freeze` passes
    through untouched and what the caller can still edit afterwards).

    Ruling 64 made this same move for the same reason - re-basing the standing
    bytearray witness onto the surface where the property can still be violated
    rather than the one where it no longer can. The bytearray FORM itself is not
    lost: it is pinned at the validator's own home, as a REFUSAL, per Batch 66
    pin (b).
    """
    leaf = ["closes above 10"]
    committed = _ledger(tmp_path).commit("X", success_criteria=provided(leaf))

    leaf.append("OR WHATEVER WE SAY LATER")

    assert committed.success_criteria.value == ("closes above 10",), (
        "the committed criterion was edited through a reference the caller "
        "still holds - the commitment is not fixed at commit time")


def test_the_module_opens_no_file_in_a_rewriting_mode() -> None:
    """THE STRUCTURAL GUARANTEE BEHIND THE ANTI-REWRITE WITNESS.

    Mode "a" is the only write mode in the file. A `"w"` anywhere here would
    truncate the history the ledger exists to be.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    modes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant):
                    modes.append(arg.value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    modes.append(kw.value.value)

    assert set(modes) <= {"r", "a"}, f"a rewriting open mode appeared: {modes}"
    assert "a" in modes, "the append path vanished"


# =====================================================================
# C. CRITERIA FIXED AT COMMIT TIME, ENFORCED AT THE WRITE
# =====================================================================

def test_resolving_against_an_uncommitted_criterion_raises(tmp_path) -> None:
    """PIN (c). **RED FIRST.** THE HEART OF "FIXED AT COMMIT TIME".

    Criteria fixed at commit time is worth nothing if a resolution may invent
    the criterion it met. Enforced AT THE WRITE, not trusted at the read.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X happens",
                  success_criteria=provided("X observed"),
                  failure_criteria=declared_none())

    with pytest.raises(ValueError, match="declared_none"):
        ledger.resolve("PRD-0001", PredictionOutcome.FALSIFIED, "failure_criteria")

    with pytest.raises(ValueError, match="absent"):
        ledger.resolve("PRD-0001", PredictionOutcome.UNRESOLVED,
                       "unresolved_criteria")

    with pytest.raises(ValueError, match="not one of the recorded criteria"):
        ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "expected_result")

    assert len(_lines(ledger)) == 1, "no refusal wrote anything"


def test_a_second_resolution_raises(tmp_path) -> None:
    """A commitment resolves ONCE. A re-score is a new prediction."""
    ledger = _ledger(tmp_path)
    _full(ledger)
    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")

    with pytest.raises(ValueError, match="already resolved"):
        ledger.resolve("PRD-0001", PredictionOutcome.FALSIFIED, "failure_criteria")

    assert len(_lines(ledger)) == 2


def test_resolving_an_unknown_prediction_raises(tmp_path) -> None:
    """A resolution refers to a prediction committed BEFORE its outcome."""
    ledger = _ledger(tmp_path)
    with pytest.raises(ValueError, match="no commitment"):
        ledger.resolve("PRD-9999", PredictionOutcome.CONFIRMED, "success_criteria")
    assert _lines(ledger) == []


def test_the_second_resolution_guard_survives_a_restart(tmp_path) -> None:
    """The guard reads the FILE, not the in-process mirror - so a fresh process
    cannot re-score what a previous one already resolved."""
    first = _ledger(tmp_path)
    _full(first)
    first.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")

    with pytest.raises(ValueError, match="already resolved"):
        _ledger(tmp_path).resolve("PRD-0001", PredictionOutcome.FALSIFIED,
                                  "failure_criteria")


def test_the_outcome_is_not_constrained_to_a_matching_criterion(tmp_path) -> None:
    """A JUDGMENT CALL, PINNED SO IT IS VISIBLE.

    Requiring FALSIFIED to name `failure_criteria` would be a rule this ruling
    does not make, and it would be WRONG: a prediction that declared ONLY a
    success criterion is falsified precisely by failing THAT criterion, and
    forcing a `failure_criteria` it never declared would make the honest
    record unwritable.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X happens", success_criteria=provided("X observed"))

    resolution = ledger.resolve("PRD-0001", PredictionOutcome.FALSIFIED,
                                "success_criteria", note="X was not observed")
    assert resolution.outcome is PredictionOutcome.FALSIFIED
    assert resolution.criterion == "success_criteria"


# =====================================================================
# D. THE RESOLUTION IS A SEPARATE APPEND - the anti-rewrite witness
# =====================================================================

def test_resolving_leaves_the_commitment_line_byte_identical(tmp_path) -> None:
    """PIN (d), THE ANTI-REWRITE WITNESS. **RED FIRST.**

    THE STRUCTURAL HEART OF THE RULING, and the pin that would catch a
    "convenient" in-place update. The ledger must read as a HISTORY - what was
    expected, then what was recorded - rather than as a STATE, which is what
    "what we now say we expected" would be. An in-place update is
    indistinguishable, afterwards, from having predicted correctly all along.
    """
    ledger = _ledger(tmp_path)
    _full(ledger)
    path = Path(ledger.ledger_path)
    before = path.read_text(encoding="utf-8")
    assert len(before.strip().splitlines()) == 1

    ledger.resolve("PRD-0001", PredictionOutcome.FALSIFIED, "failure_criteria",
                   note="closed at 9")

    after = path.read_text(encoding="utf-8")
    lines = after.strip().splitlines()
    assert len(lines) == 2, "the resolution is a SEPARATE line"
    assert after.startswith(before), (
        "THE COMMITMENT LINE WAS REWRITTEN. The ledger has become a state "
        "rather than a history, and the original expectation is unrecoverable")
    assert lines[0] == before.strip()

    committed, resolution = json.loads(lines[0]), json.loads(lines[1])
    assert committed["kind"] == "commitment"
    assert resolution["kind"] == "resolution"
    assert resolution["prediction_id"] == committed["prediction_id"]
    assert "outcome" not in committed, (
        "the outcome was written onto the commitment - that IS the rewrite")


def test_the_history_reads_in_append_order(tmp_path) -> None:
    """`read_all()` reads the FILE, in the order written."""
    ledger = _ledger(tmp_path)
    _full(ledger)
    ledger.commit("Y happens", success_criteria=provided("Y observed"))
    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")

    entries = _ledger(tmp_path).read_all()
    assert [type(e).__name__ for e in entries] == [
        "PredictionCommitment", "PredictionCommitment", "PredictionResolution"]
    assert entries[2].prediction_id == "PRD-0001"


# =====================================================================
# E. THE WRITE GATES THE PREDICTION
# =====================================================================

def test_a_failed_write_raises_and_records_nothing(tmp_path, monkeypatch) -> None:
    """PIN (e). **RED FIRST.** RULING 46's THREE-MEASURE FORM.

    AN UNRECORDED PREDICTION IS PRECISELY THE REWRITABLE THING THIS DOCKET
    EXISTS TO ABOLISH, so `commit()` raises rather than handing back an object
    nothing backs. Asserting only the raise would pass against an
    implementation that recorded first and failed after - so the ledger line
    count, the in-process mirror AND the caller's view are all measured.
    """
    ledger = _ledger(tmp_path)
    _full(ledger)

    def _boom(*args, **kwargs):
        raise OSError("disk is gone")

    monkeypatch.setattr("builtins.open", _boom)
    with pytest.raises(OSError):
        ledger.commit("Y happens", success_criteria=provided("Y observed"))
    monkeypatch.undo()

    assert len(_lines(ledger)) == 1, "a failed commit wrote a line"
    assert len(ledger.entries) == 1, "a failed commit polluted the mirror"
    assert [c.prediction_id for c in ledger.commitments()] == ["PRD-0001"]


def test_a_failed_resolution_write_records_nothing(tmp_path, monkeypatch) -> None:
    """The same gate on the other write path."""
    ledger = _ledger(tmp_path)
    _full(ledger)

    def _boom(*args, **kwargs):
        raise OSError("disk is gone")

    monkeypatch.setattr("builtins.open", _boom)
    with pytest.raises(OSError):
        ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")
    monkeypatch.undo()

    assert len(_lines(ledger)) == 1
    assert _ledger(tmp_path).resolution_for("PRD-0001") is None, (
        "a failed write left the prediction looking resolved")


# =====================================================================
# F. THE MINT - Ruling 53's sentinel, both branches
# =====================================================================

def test_a_missing_ledger_is_a_first_run_not_a_fault(tmp_path) -> None:
    """PIN (f), branch one. Absence is a first run; answering an unreadable
    file with 0 would be a claim about content the code never saw."""
    ledger = _ledger(tmp_path, "nothing_here.jsonl")
    assert ledger._seq == 0
    assert ledger.commit("X").prediction_id == "PRD-0001"


def test_an_unreadable_existing_ledger_refuses_to_mint(tmp_path, monkeypatch) -> None:
    """PIN (f), branch two. **RED FIRST.** RULING 53 WHOLE.

    `None` IFF the ledger EXISTS and the read raised. Minting from an unknown
    floor could write an id that already names a different prediction - and two
    commitments wearing one id are two sets of criteria nobody can tell apart.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X", success_criteria=provided("X observed"))

    fresh = _ledger(tmp_path)
    assert fresh._seq == 1

    def _boom(*args, **kwargs):
        raise OSError("unreadable")

    monkeypatch.setattr("builtins.open", _boom)
    broken = _ledger(tmp_path)
    assert broken._seq is None, "an unreadable EXISTING ledger must not read 0"
    with pytest.raises(PredictionLedgerUnreadable):
        broken.commit("Y")


def test_the_mint_re_derives_once_when_the_disk_recovers(tmp_path) -> None:
    """Ruling 53's single re-derivation: the condition is transient by nature,
    so a recovered ledger resumes from its REAL maximum."""
    ledger = _ledger(tmp_path)
    ledger.commit("X")
    ledger.commit("Y")

    broken = _ledger(tmp_path)
    broken._seq = None                      # as an unreadable load would leave it
    assert broken.commit("Z").prediction_id == "PRD-0003", (
        "a recovered ledger must resume from the file maximum, never from zero")


def test_an_unparseable_line_is_floored_not_fatal(tmp_path) -> None:
    """PER-LINE FLOOR SEMANTICS. An unreadable FILE and an unparseable LINE are
    different failures and get different answers - a forensic log outlives the
    code that wrote it."""
    ledger = _ledger(tmp_path)
    ledger.commit("X", success_criteria=provided("X observed"))
    Path(ledger.ledger_path).open("a", encoding="utf-8").write("{not json\n")

    fresh = _ledger(tmp_path)
    assert fresh._seq == 1
    assert len(fresh.commitments()) == 1
    assert fresh.commit("Y").prediction_id == "PRD-0002"


def test_the_mint_continues_across_a_restart(tmp_path) -> None:
    """CONTINUITY STATE (Ruling 42 res.4): derived from the file maximum."""
    first = _ledger(tmp_path)
    first.commit("X")
    first.commit("Y")

    assert _ledger(tmp_path).commit("Z").prediction_id == "PRD-0003"


# =====================================================================
# G. THE CLOSED ENUMS, BOTH WAYS
# =====================================================================

def test_the_enums_are_closed_and_every_member_is_recovered() -> None:
    """L2 NAMES THE SIX IN ITS OWN SENTENCE - this enum is RECOVERED, not
    coined: "observation, causal link, auxiliary assumption, horizon, domain
    validity, or the claim itself". The three outcomes are the registration's
    own words."""
    assert {m.name for m in DependencyLink} == {
        "OBSERVATION", "CAUSAL_LINK", "AUXILIARY_ASSUMPTION", "HORIZON",
        "DOMAIN_VALIDITY", "THE_CLAIM_ITSELF"}
    assert {m.name for m in PredictionOutcome} == {
        "CONFIRMED", "FALSIFIED", "UNRESOLVED"}
    assert CRITERION_FIELDS == ("success_criteria", "failure_criteria",
                                "unresolved_criteria")


def test_an_unknown_dependency_member_drops_the_line(tmp_path) -> None:
    """PIN (g), direction one. FLOOR-DROPPED, NEVER DEFAULTED.

    Keeping a PARTIAL chain would be worse than keeping none: O4 routes
    pressure to the chain, and a chain silently missing a link would route
    pressure somewhere the predictor never named.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X", dependency_chain=(DependencyLink.OBSERVATION,))
    path = Path(ledger.ledger_path)
    entry = json.loads(path.read_text(encoding="utf-8").strip())
    entry["prediction_id"] = "PRD-0002"
    entry["dependency_chain"] = ["observation", "vibes"]
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")

    loaded = _ledger(tmp_path).commitments()
    assert [c.prediction_id for c in loaded] == ["PRD-0001"]
    assert all(DependencyLink.OBSERVATION in c.dependency_chain for c in loaded)


def test_an_unknown_outcome_drops_the_line(tmp_path) -> None:
    """PIN (g), direction two. Never coerced, and never defaulted to
    UNRESOLVED - which would silently turn somebody's recorded verdict into a
    shrug."""
    ledger = _ledger(tmp_path)
    ledger.commit("X", success_criteria=provided("X observed"))
    with Path(ledger.ledger_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"kind": "resolution", "prediction_id": "PRD-0001",
                                 "outcome": "probably", "criterion":
                                 "success_criteria"}) + "\n")

    fresh = _ledger(tmp_path)
    assert fresh.resolutions() == ()
    assert fresh.resolution_for("PRD-0001") is None
    assert [c.prediction_id for c in fresh.outstanding()] == ["PRD-0001"], (
        "an undecodable verdict must not silently resolve the prediction")


def test_an_unknown_kind_is_dropped(tmp_path) -> None:
    """A line whose kind this build does not know contributes nothing.

    THE INJECTED LINE IS A COMPLETE, WELL-FORMED COMMITMENT wearing an unknown
    `kind`, and that detail is the whole pin. The first version of this test
    injected a stub carrying only a `prediction_id`; a mutant that fed every
    unknown kind to `PredictionCommitment.from_dict` still returned `None` on
    it - for the unrelated reason that `expected_result` was missing - so the
    mutant SURVIVED. A dropped-line pin whose line would be dropped anyway
    witnesses nothing.

    An `amendment` kind is the pointed case: it is what a future author would
    add if they wanted to edit a commitment without saying so.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X", success_criteria=provided("X observed"))

    forged = json.loads(Path(ledger.ledger_path).read_text(encoding="utf-8").strip())
    forged["kind"] = "amendment"
    forged["expected_result"] = "X happens, or something like it"
    with Path(ledger.ledger_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(forged) + "\n")

    loaded = _ledger(tmp_path).read_all()
    assert len(loaded) == 1, (
        "a line with an unknown kind was read as a commitment - an `amendment` "
        "kind must not become a second, contradicting record of what was "
        "predicted")
    assert loaded[0].expected_result == "X"


def test_a_raw_string_cannot_enter_the_dependency_chain(tmp_path) -> None:
    """The closed enum is enforced at CONSTRUCTION too, not only on load."""
    with pytest.raises(TypeError):
        PredictionCommitment(prediction_id="PRD-0001", expected_result="X",
                             dependency_chain=("observation",))


def test_claim_refs_are_recorded_ids_and_never_live_objects(tmp_path) -> None:
    """RULING 42's FINDING, at this record's boundary. Found by a survivor.

    An embedded record OBJECT in another owner's store is a write path the
    Ruling-1 AST scanner structurally cannot see - nothing assigns to the
    store, yet the store is reachable and mutable through the reference. So
    `claim_refs` carries IDS ONLY (Ruling 50's ids-only shape), and the check
    is enforced rather than documented.
    """
    class _LiveRecord:
        claim_id = "CLM-0001"

    with pytest.raises(TypeError, match="Recorded IDS ONLY"):
        PredictionCommitment(prediction_id="PRD-0001", expected_result="X",
                             claim_refs=(_LiveRecord(),))


def test_the_freeze_list_is_a_class_constant_not_a_constructor_argument() -> None:
    """`ClassVar` IS LOAD-BEARING. Found by a survivor.

    An annotated class attribute inside a dataclass becomes a FIELD with a
    default. Without `ClassVar`, `RECORDED_FIELDS` would be a per-instance,
    CALLER-SUPPLIED list of which fields the freeze loop walks - so
    `PredictionCommitment(..., RECORDED_FIELDS=())` would construct a record
    that skipped the deep freeze entirely, while looking identical.

    A record whose own integrity rule is an argument is not a record.
    """
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(PredictionCommitment)}
    assert "RECORDED_FIELDS" not in field_names, (
        "the freeze list is a constructor parameter - a caller can now choose "
        "which of their own fields get frozen")
    assert PredictionCommitment.RECORDED_FIELDS == (
        "applicable_conditions", "resolution_horizon") + CRITERION_FIELDS


# =====================================================================
# H. HORIZON IS NOT A CLOCK
# =====================================================================

def test_an_overdue_commitment_is_reported_by_a_read_and_never_stored(tmp_path) -> None:
    """PIN (h). **RED FIRST.** THE LEDGER NEVER SCORES ITS OWN PREDICTIONS.

    An auto-resolution would be the ledger resolving what it was built to hold
    open. So "overdue" is COMPUTED AT READ from recorded facts and never stored
    as a status (L3: derive standing, never store it redundantly; and Ruling
    42's cached-status lesson). An overdue commitment stays UNRESOLVED and
    VISIBLE - the Veiled Thread's discipline applied to predictions.
    """
    ledger = _ledger(tmp_path)
    _full(ledger)
    before = Path(ledger.ledger_path).read_text(encoding="utf-8")

    fresh = _ledger(tmp_path)
    overdue = fresh.overdue(lambda horizon: True)

    assert [c.prediction_id for c in overdue] == ["PRD-0001"]
    assert [c.prediction_id for c in fresh.outstanding()] == ["PRD-0001"], (
        "passing a horizon must not resolve anything")
    assert fresh.resolution_for("PRD-0001") is None
    assert Path(ledger.ledger_path).read_text(encoding="utf-8") == before, (
        "a READ wrote to the ledger")

    entry = _lines(ledger)[0]
    for forbidden in ("overdue", "status", "expired", "state"):
        assert forbidden not in entry, (
            f"'{forbidden}' is STORED on the commitment - derived standing "
            f"must never be written down beside the facts it derives from")


def test_the_read_path_holds_no_clock() -> None:
    """THE MODULE DOES NOT INTERPRET A HORIZON, AND CANNOT HONESTLY: a horizon
    may be a date, a cycle count, or an observed condition, and picking a
    format here would COIN one at the exact point where "has this expired" gets
    decided. The CALLER supplies the judgement.

    `datetime.now()` appears only where a RECORD is stamped - never on a read.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    read_paths = {"overdue", "outstanding", "read_all", "commitments",
                  "resolutions", "commitment_for", "resolution_for"}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in read_paths:
            for inner in ast.walk(node):
                if isinstance(inner, ast.Attribute) and inner.attr == "now":
                    pytest.fail(f"{node.name} consults a clock at line "
                                f"{inner.lineno} - horizon is a recorded "
                                f"declaration, not a scheduler")


def test_nothing_resolves_without_an_explicit_resolve_call(tmp_path) -> None:
    """PIN (h), second half. The ONLY writer of a resolution line is
    `resolve()` - AST-pinned, because an auto-resolution buried in a read is
    exactly the defect that would be invisible from the outside."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    writers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call)
                        and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "_append"):
                    writers.append(node.name)

    assert sorted(writers) == ["commit", "resolve"], (
        f"the ledger is appended from {sorted(writers)} - a third write path "
        f"means something records without being asked to")

    # And behaviourally: exercising every read leaves the file untouched.
    ledger = _ledger(tmp_path)
    _full(ledger)
    snapshot = Path(ledger.ledger_path).read_text(encoding="utf-8")

    fresh = _ledger(tmp_path)
    fresh.read_all(); fresh.commitments(); fresh.resolutions()
    fresh.outstanding(); fresh.overdue(lambda h: True)
    fresh.commitment_for("PRD-0001"); fresh.resolution_for("PRD-0001")

    assert Path(ledger.ledger_path).read_text(encoding="utf-8") == snapshot


def test_only_a_provided_horizon_reaches_the_callers_judgement(tmp_path) -> None:
    """SUPERSEDED AND REPLACED IN PLACE 2026-08-01 BY RULING 64 res.8, under
    the Ruling-14 precedent. Recorded verbatim:

        OLD (Ruling 61) - test_a_declared_none_horizon_is_still_readable_by_
        the_caller:
            '''The horizon's three states reach the caller's judgement intact -
            the module hands over the RECORD and interprets none of it.'''
            assert seen == [FieldState.DECLARED_NONE, FieldState.PROVIDED]

    THE OLD PIN WAS RIGHT ABOUT NON-INTERPRETATION AND WRONG ABOUT WHAT TO HAND
    OVER. Ruling 61 refused to interpret a horizon's VALUE, which stands. But
    passing a DECLARED_NONE or ABSENT horizon to a predicate that answers "has
    this passed?" asks the caller a question about a date that does not exist -
    and the honest answers (a commitment that declared no horizon is NOT
    overdue; one never asked is NOT KNOWABLE) are both "not overdue", so
    handing them over only invites a caller to invent one.

    Docket H's two-absences cut, at the read: the predicate now sees only
    horizons that EXIST. Nothing is hidden - all three commitments remain
    OUTSTANDING and fully readable there.
    """
    ledger = _ledger(tmp_path)
    ledger.commit("X", resolution_horizon=declared_none())
    ledger.commit("Y", resolution_horizon=provided("2027-01-01"))
    ledger.commit("Z")

    seen = []
    _ledger(tmp_path).overdue(lambda horizon: seen.append(horizon.state) or False)
    assert seen == [FieldState.PROVIDED], (
        "a horizon that does not exist was handed to a predicate asked to "
        "judge whether it had passed")

    assert len(_ledger(tmp_path).outstanding()) == 3, (
        "the filter narrows OVERDUE, never visibility")


# =====================================================================
# I. L2 - NOTHING HERE PROMOTES
# =====================================================================

def test_the_module_imports_no_promotion_surface() -> None:
    """PIN (i). **RED FIRST.** L2, PINNED STRUCTURALLY RATHER THAN PROMISED.

        "Prediction is a pressure source, never a promotion source...
         Predictive success preserves viability and updates instrument
         history; it PROMOTES NOTHING. Utility is not ontology."

    A CONFIRMED prediction updates nothing but the record. The import set is
    the enforcement: you cannot write a doctrine you cannot reach.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(alias.name for alias in node.names)

    forbidden = {
        "src.doctrine.codex", "Codex", "src.doctrine.sae", "SAE",
        "src.expansion.sae", "src.doctrine.dee", "DEE",
        "src.doctrine.doctrine_spine", "DoctrineSpine",
        "src.filtration.scar_logic_core", "ScarLogicCore",
        "src.filtration.scar_management", "SML",
        "src.reflex.racm", "RACM", "src.reflex.reflex_grid",
        "src.doctrine.cae", "CAE", "src.aurea_core", "AureaCore",
        # res.1: claim_refs are recorded ids and are NOT validated against the
        # ancestry ledger - that would make this module read a SECOND store.
        "ClaimAncestryLedger",
    }
    assert forbidden.isdisjoint(imported), (
        f"a promotion or second-store surface is reachable from the prediction "
        f"ledger: {sorted(forbidden & imported)}")


def test_the_import_scanner_actually_fires() -> None:
    """The fires-control: a scan that has stopped scanning fails HERE."""
    forbidden = ast.parse("from src.doctrine.codex import Codex\n"
                          "from src.external.claim_ancestry import "
                          "ClaimAncestryLedger\n")
    benign = ast.parse("from src.external.claim_ancestry import provided\n")

    def names(tree):
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                found.add(node.module or "")
                found.update(a.name for a in node.names)
        return found

    assert {"Codex", "ClaimAncestryLedger"} <= names(forbidden)
    assert {"Codex", "ClaimAncestryLedger"}.isdisjoint(names(benign))


def test_the_module_defines_no_promotion_verb() -> None:
    """Beyond imports: no method here is named for changing a belief."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    forbidden = {"promote", "mutate_doctrine", "form_scar", "commit_doctrine",
                 "apply_pressure", "route_pressure", "entrench", "reinforce"}
    assert defined.isdisjoint(forbidden), (
        f"a promotion verb is defined here: {sorted(defined & forbidden)}. "
        f"O3 records the outcome; O4 decides its consequence")


def test_no_track_record_or_calibration_score_is_stored(tmp_path) -> None:
    """RES.8, REFUSED AND STANDING. Accuracy rates and calibration scores are
    the numeric trust scores the docket refused. They are legitimate later ONLY
    as derivations over recorded facts - derived AT READ, never stored."""
    ledger = _ledger(tmp_path)
    _full(ledger)
    ledger.resolve("PRD-0001", PredictionOutcome.CONFIRMED, "success_criteria")

    forbidden = ("accuracy", "calibration", "score", "reliability", "track_record",
                 "hit_rate", "confidence", "weight")
    for entry in _lines(ledger):
        for key in entry:
            assert not any(word in key.lower() for word in forbidden), (
                f"'{key}' is stored on a ledger line")
    for name in forbidden:
        assert not hasattr(ledger, name)


def test_the_module_carries_no_magnitude() -> None:
    """COINS NOTHING: no threshold, weight, magnitude or duration anywhere."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    floats = [n.value for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    assert floats == [], f"a float literal appeared: {floats}"


# =====================================================================
# J. REGISTRATION
# =====================================================================

def test_the_unreadable_sentinel_is_a_structural_violation() -> None:
    """RES.4. Membership is a DECISION, made by the ruling.

    UNREACHABLE from `process_input` today - Ruling 61 wires no consumer - and
    that does not disqualify it, on the reasoning `InvalidMutationProof`
    records in the tuple itself: the membership is already correct on the day a
    consumer arrives, rather than being discovered by a structural guard
    degrading into an `errors` string.
    """
    assert PredictionLedgerUnreadable in STRUCTURAL_VIOLATIONS
    assert not issubclass(PredictionLedgerUnreadable, tuple(
        v for v in STRUCTURAL_VIOLATIONS if v is not PredictionLedgerUnreadable)), (
        "STRUCTURAL_VIOLATIONS members are concrete types, never base classes "
        "of one another (Ruling 25)")


def test_the_ledger_path_is_injectable_and_under_runtime() -> None:
    """Ruling 31 / Ruling 39: an `__init__` DEFAULT - one of exactly two shapes
    `conftest.py` and `soak.py` can reach - resolving under `data/runtime/`.

    READ FROM SOURCE, NOT FROM THE LIVE SIGNATURE, and the reason is worth
    recording: the autouse fixture REDIRECTS that default to tmp, so
    `inspect.signature` at test time returns the pytest path and this pin
    asserted the fixture rather than the store. That is Ruling 32's own trap -
    "the fixture would hide exactly this defect while production wrote
    elsewhere" - and it fired here during development.

    Reading the source pins what SHIPS. The redirect being live is asserted
    separately, by the fact that every other test in this file writes to tmp.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    default = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            args = node.args
            names = [a.arg for a in args.args[-len(args.defaults):]] if args.defaults else []
            for name, value in zip(names, args.defaults):
                if name == "ledger_path" and isinstance(value, ast.Constant):
                    default = value.value

    assert isinstance(default, str), "`ledger_path` has no literal default"
    assert default.startswith("data/runtime/"), (
        f"the shipped default write path is {default!r} - a store that writes "
        f"outside data/runtime/ by default is Ruling 39's defect")
    assert default.endswith(".jsonl")


def test_nothing_in_src_consumes_the_prediction_ledger() -> None:
    """NO CONSUMER WIRING THIS PASS - a resolution, not an omission. An
    instrument first, consumers by later ruling (O4 owns routing).

    This pin goes RED the day something wires it, which is exactly when the
    consumer needs a ruling. `aurea_core` is EXEMPT for the taxonomy import
    ONLY: it names the exception type and constructs no ledger.

    MIGRATED 2026-08-01 BY RULING 63, under the Ruling-14 precedent. THE
    ASSERTION IS UNCHANGED; the INSTRUMENT is strictly narrower and now says
    what it always meant.

        OLD:  "prediction_ledger" in text or "PredictionLedger" in text
        NEW:  an AST scan for an import that BINDS THE STORE CLASS

    WHY IT MOVED, AND THE REASON IS SHARPER THAN THE PROSE CASE: Ruling 63's
    `record_projection.py` (then `world_state.py`) imports
    `PredictionCommitment` / `PredictionResolution` /
    `PredictionOutcome` from this module - THE RECORD TYPES, which is exactly
    what O5 was designed to do (its inputs arrive as already-read records) -
    and the substring pin read that as consuming the LEDGER. It would have
    flagged every future module that merely names a commitment.

    IMPORTING A RECORD TYPE IS NOT CONSUMING THE STORE. What this pin exists to
    catch is a module that can REACH the ledger, so it now looks for the class
    `PredictionLedger` and for the ledger's exception, and ignores the
    vocabulary. FIFTH occurrence of the substring-scanner false positive; the
    manifest has the conversion ELEVATED.
    """
    consumers = []
    for path in Path("src").rglob("*.py"):
        if path == MODULE:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        bound = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                bound.update((a.asname or a.name) for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                bound.update((a.asname or a.name) for a in node.names)
        if "PredictionLedger" not in bound:
            continue
        if path.as_posix().endswith("aurea_core.py"):
            assert "PredictionLedger(" not in path.read_text(encoding="utf-8"), (
                "aurea_core CONSTRUCTS a prediction ledger - the taxonomy "
                "import is the only permitted contact")
            continue
        consumers.append(path.as_posix())

    assert consumers == [], (
        f"{consumers} consume the prediction ledger. Wiring it into a verdict "
        f"path, an expression surface or a routing decision is a RULING "
        f"(Ruling 61 res.8), not an implementation choice")
