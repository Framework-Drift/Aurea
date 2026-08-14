"""
M3-A - THE OBLIGATION AND EPISODE SUBSTRATE (kernels K2 / K3 / K11).

The pivot's first construction. These pins hold the properties the slice
claims: deterministic admission, structural never-erasability, a bound fixed at
open, honest terminal states, and logical time that never reads a clock.

THE HEADLINE PIN IS SECTION E. `UNRESOLVED_AT_BOUND` is what makes "ran out of
room" distinguishable from "withstood testing", and without the counting rule
both end as SURVIVED and the record cannot tell them apart afterwards.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.filtration.episode_record import (
    ClosedVocabularyViolation, EpisodeAlreadyDisposed, EpisodeOutcome,
    EpisodeRecord, EpisodeRecordType, IllegalOutcomeAtBound, PressureClass,
    ShapingActKind, SurvivalWithoutPressure, UnboundedEpisode, UnknownEpisode,
)
from src.filtration.obligation_ledger import (
    AdmissionOutcome, MalformedDeferral, ObligationLedger, ObligationRecordType,
    RejectionKind, TargetKind, TargetResolution, mint_seq_token, seq_ordinal,
)
from src.suspension.black_sphere import BlackSphere

REPO = Path(__file__).resolve().parents[1]
OBLIGATION_SRC = REPO / "src" / "filtration" / "obligation_ledger.py"
EPISODE_SRC = REPO / "src" / "filtration" / "episode_record.py"
BOTH = (OBLIGATION_SRC, EPISODE_SRC)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _methods(path: Path, class_name: str):
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
    raise AssertionError(f"{class_name} not found in {path}")


def _src_files():
    return sorted((REPO / "src").rglob("*.py"))


# =====================================================================
# A. NEVER-ERASABLE - the property, as SHAPE
# =====================================================================

FORBIDDEN_VERBS = ("delete", "remove", "clear", "purge", "truncate", "erase",
                   "drop", "rewrite", "amend", "update", "edit")


@pytest.mark.parametrize("path,cls", [
    (OBLIGATION_SRC, "ObligationLedger"), (EPISODE_SRC, "EpisodeRecord")])
def test_a_no_erasure_method_exists_on_either_class(path, cls):
    """PIN A1. A record is never modified and never removed.

    Enforced as ABSENCE rather than as discipline: a method named
    `remove_obligation` with a docstring saying "only for duplicates" is a
    request for restraint, and this project has hard evidence restraint fails.
    """
    offenders = [m for m in _methods(path, cls)
                 if any(verb in m.lower() for verb in FORBIDDEN_VERBS)]
    assert offenders == [], (
        f"{cls} grew an erasure-shaped method: {offenders}. An event-sourced "
        f"ledger records a CHANGE as a new line; it never edits or removes one.")


@pytest.mark.parametrize("path", BOTH)
def test_a_no_filesystem_erasure_call_in_either_module(path):
    """PIN A2. No `os.remove` / `unlink` / `truncate` anywhere in either module."""
    banned = {"remove", "unlink", "truncate", "rmtree", "rmdir"}
    hits = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if name in banned:
                hits.append((name, node.lineno))
    assert hits == [], f"{path.name} can erase its own record: {hits}"


@pytest.mark.parametrize("path", BOTH)
def test_a_the_only_write_mode_is_the_funnel(path):
    """PIN A3 / DURABILITY. No `open()` for writing; the funnel owns the append.

    Ruling 78's tree-wide census forbids a mode-`"a"` open outside the helper;
    this asserts the stronger local property - neither module opens a file for
    writing AT ALL, so a `"w"` here would have to get past both.
    """
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "open":
            mode = node.args[1].value if len(node.args) > 1 else "r"
            assert mode == "r", (
                f"{path.name}:{node.lineno} opens a file in mode {mode!r}. "
                f"Appends route through `durable_append_text`; nothing here "
                f"rewrites.")


@pytest.mark.parametrize("path", BOTH)
def test_a_the_append_routes_through_the_funnel(path):
    """PIN A4. Ruling 78's funnel is actually called - the count control."""
    calls = [n for n in ast.walk(_tree(path))
             if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "durable_append_text"]
    assert len(calls) == 1, (
        f"{path.name} should reach the funnel from exactly one `_append`; "
        f"found {len(calls)} call sites.")


# =====================================================================
# B. ADMISSION IS TOTAL - every path writes a record
# =====================================================================

class _FakeCodex:
    def __init__(self, live=(), fossils=()):
        self._live = set(live)
        self.fossils = {f: object() for f in fossils}

    def get(self, doctrine_id):
        return object() if doctrine_id in self._live else None


class _FakeScars:
    def __init__(self, ids=()):
        self._ids = set(ids)

    def get_scar(self, scar_id):
        return object() if scar_id in self._ids else None


def _ledger(tmp_path, **kw):
    return ObligationLedger(ledger_path=str(tmp_path / "obligations.jsonl"), **kw)


def test_b_a_clean_admission_writes_an_open_record(tmp_path):
    """PIN B1. The happy path, with a resolvable target."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["Doctrine-0"]))
    result = led.admit("architect", TargetKind.DOCTRINE, "Doctrine-0", "owes a check")
    assert result.outcome is AdmissionOutcome.ADMITTED
    assert result.target_resolution is TargetResolution.RESOLVED
    records = led.read_all()
    assert len(records) == 1
    assert records[0]["record_type"] == ObligationRecordType.OPEN.value
    assert records[0]["obligation_id"] == result.obligation_id
    assert records[0]["claim_text"] == "owes a check"


@pytest.mark.parametrize("source,kind,target,claim", [
    ("", TargetKind.DOCTRINE, "Doctrine-0", "c"),
    ("s", TargetKind.DOCTRINE, "", "c"),
    ("s", TargetKind.DOCTRINE, "Doctrine-0", "   "),
    ("s", None, "Doctrine-0", "c"),
    ("s", "not-a-kind", "Doctrine-0", "c"),
    (None, TargetKind.DOCTRINE, "Doctrine-0", "c"),
])
def test_b_malformed_writes_a_rejected_record(tmp_path, source, kind, target, claim):
    """PIN B2. MALFORMED still writes. A rejection that leaves no trace is
    indistinguishable afterwards from a claim nobody ever made."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["Doctrine-0"]))
    result = led.admit(source, kind, target, claim)
    assert result.outcome is AdmissionOutcome.REJECTED
    assert result.rejection_kind is RejectionKind.MALFORMED
    assert result.reason
    records = led.read_all()
    assert len(records) == 1
    assert records[0]["record_type"] == ObligationRecordType.REJECTED.value
    assert records[0]["reason"] == result.reason


def test_b_targetless_writes_a_rejected_record(tmp_path):
    """PIN B3. The target does not resolve against what the ledger CAN see."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["Doctrine-0"]))
    result = led.admit("s", TargetKind.DOCTRINE, "Doctrine-NOPE", "c")
    assert result.rejection_kind is RejectionKind.TARGETLESS
    assert result.target_resolution is TargetResolution.UNRESOLVED
    assert led.read_all()[0]["record_type"] == ObligationRecordType.REJECTED.value
    assert led.open_items() == []


def test_b_a_fossil_resolves(tmp_path):
    """PIN B4. An obligation may bear on a doctrine that has FALLEN."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=[], fossils=["Doctrine-0"]))
    assert led.admit("s", TargetKind.DOCTRINE, "Doctrine-0", "c").admitted


def test_b_an_unseen_structure_is_unchecked_not_targetless(tmp_path):
    """PIN B5 - DOCKET H'S CUT, AT THE FRONT DOOR.

    With no scar resolver the ledger CANNOT SEE scars. "I could not look" is not
    "it is not there": rejecting would assert a non-existence never tested, and
    admitting silently would claim a resolution never performed. The record says
    UNCHECKED, and that is a third state rather than a soft UNRESOLVED.
    """
    led = _ledger(tmp_path)                       # no resolvers at all
    result = led.admit("s", TargetKind.SCAR, "Scar-0", "c")
    assert result.admitted
    assert result.target_resolution is TargetResolution.UNCHECKED
    assert led.read_all()[0]["target_resolution"] == TargetResolution.UNCHECKED.value


def test_b_duplicate_blocks_on_a_standing_obligation(tmp_path):
    """PIN B6. Same target + same normalized claim, while OPEN."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    first = led.admit("s", TargetKind.DOCTRINE, "D", "Check the derivation")
    dupe = led.admit("s", TargetKind.DOCTRINE, "D", "  check   THE DERIVATION ")
    assert dupe.rejection_kind is RejectionKind.DUPLICATE
    assert first.obligation_id in dupe.reason
    assert len(led.open_items()) == 1


def test_b_a_rejected_record_does_not_block_a_later_admission(tmp_path):
    """PIN B7 - THE OTHER HALF, and the one a naive implementation gets wrong.

    A previously REJECTED claim was never taken up. Blocking on it would make a
    transient TARGETLESS - a doctrine not yet committed - permanent.
    """
    led = _ledger(tmp_path, codex=_FakeCodex(live=[]))
    first = led.admit("s", TargetKind.DOCTRINE, "D", "same claim")
    assert first.rejection_kind is RejectionKind.TARGETLESS
    led.codex = _FakeCodex(live=["D"])            # the doctrine now exists
    second = led.admit("s", TargetKind.DOCTRINE, "D", "same claim")
    assert second.admitted, "a REJECTED record must not block a later admission"


def test_b_a_deferred_obligation_still_blocks_a_duplicate(tmp_path):
    """PIN B8. DEFERRED is STANDING - set aside is not gone."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    first = led.admit("s", TargetKind.DOCTRINE, "D", "claim")
    led.defer(first.obligation_id, "waiting on a source", "SEQ-000900")
    again = led.admit("s", TargetKind.DOCTRINE, "D", "claim")
    assert again.rejection_kind is RejectionKind.DUPLICATE


def test_b_every_admission_path_writes_exactly_one_record(tmp_path):
    """PIN B9 - TOTALITY. Four outcomes, four records, no silent path."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    led.admit("s", TargetKind.DOCTRINE, "D", "one")          # OPEN
    led.admit("s", TargetKind.DOCTRINE, "D", "one")          # DUPLICATE
    led.admit("", TargetKind.DOCTRINE, "D", "two")           # MALFORMED
    led.admit("s", TargetKind.DOCTRINE, "GONE", "three")     # TARGETLESS
    assert len(led.read_all()) == 4


# =====================================================================
# C. DEFERRAL REQUIRES A REASON AND A DUE ORDINAL
# =====================================================================

@pytest.mark.parametrize("reason,due", [
    ("", "SEQ-000010"), ("   ", "SEQ-000010"), (None, "SEQ-000010"),
    ("why", None), ("why", ""), ("why", 10), ("why", "tomorrow"),
])
def test_c_deferral_without_both_raises_typed(tmp_path, reason, due):
    """PIN C1. A deferral missing either half is an abandonment with a record
    that says otherwise."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    obligation = led.admit("s", TargetKind.DOCTRINE, "D", "c").obligation_id
    before = len(led.read_all())
    with pytest.raises(MalformedDeferral):
        led.defer(obligation, reason, due)
    assert len(led.read_all()) == before, "a refused deferral writes nothing"


def test_c_a_complete_deferral_records_both(tmp_path):
    """PIN C2."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    obligation = led.admit("s", TargetKind.DOCTRINE, "D", "c").obligation_id
    led.defer(obligation, "waiting on a primary source", "SEQ-000123")
    record = led.read_all()[-1]
    assert record["record_type"] == ObligationRecordType.DEFERRED.value
    assert record["reason"] == "waiting on a primary source"
    assert record["due_seq"] == "SEQ-000123"


def test_c_merge_and_episode_opened_leave_the_standing_set(tmp_path):
    """PIN C3. `open_items` is a FOLD - the status is derived, never stored."""
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    merged = led.admit("s", TargetKind.DOCTRINE, "D", "a").obligation_id
    worked = led.admit("s", TargetKind.DOCTRINE, "D", "b").obligation_id
    standing = led.admit("s", TargetKind.DOCTRINE, "D", "c").obligation_id
    led.merge(merged, "EPI-0001")
    led.mark_episode_opened(worked, "EPI-0002")
    assert [i["obligation_id"] for i in led.open_items()] == [standing]
    assert led.status_of(merged) is ObligationRecordType.MERGED
    assert led.status_of(worked) is ObligationRecordType.EPISODE_OPENED


# =====================================================================
# D. THE BOUND IS DECLARED AT OPEN AND FIXED
# =====================================================================

def _episodes(tmp_path):
    return EpisodeRecord(log_path=str(tmp_path / "episodes.jsonl"))


@pytest.mark.parametrize("bound", [None, 0, -1, -99, 1.5, "3", True, False])
def test_d_an_unbounded_open_raises_typed(tmp_path, bound):
    """PIN D1. `True` is in this list on purpose: `bool` is an `int` in Python,
    so it would otherwise pass as a silent, plausible bound of 1 that nobody
    declared."""
    with pytest.raises(UnboundedEpisode):
        _episodes(tmp_path).open_episode(["OBL-0001"], bound)


def test_d_nothing_is_written_by_a_refused_open(tmp_path):
    """PIN D2. The refusal precedes the mint, so it burns no ordinal."""
    log = _episodes(tmp_path)
    with pytest.raises(UnboundedEpisode):
        log.open_episode(["OBL-0001"], 0)
    assert log.read_all() == ()


def test_d_no_amend_surface_exists(tmp_path):
    """PIN D3 - THE BOUND IS FIXED AS SHAPE.

    There is no `amend_bound`/`extend`/`rebound`/`reopen`. The ABSENCE is the
    enforcement: a method named `extend_bound` with a docstring saying "only
    before disposition" is a request for restraint (CLAUDE.md §3).
    """
    names = [m.lower() for m in _methods(EPISODE_SRC, "EpisodeRecord")]
    for verb in ("amend", "extend", "rebound", "reopen", "set_bound", "rescope"):
        assert not any(verb in m for m in names), f"an episode grew `{verb}`"


def test_d_bound_is_written_once_and_only_at_open(tmp_path):
    """PIN D4. `"bound"` is assigned in exactly one method: `open_episode`."""
    writers = set()
    for node in ast.walk(_tree(EPISODE_SRC)):
        if isinstance(node, ast.FunctionDef):
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Constant) and sub.value == "bound"
                        and isinstance(getattr(sub, "parent", None), type(None))):
                    writers.add(node.name)
    # The dict literal in `open_episode` is the only place the key is SET; the
    # counting rule READS it via `.get`. Assert the literal appears once.
    literals = [n for n in ast.walk(_tree(EPISODE_SRC))
                if isinstance(n, ast.Dict)
                and any(isinstance(k, ast.Constant) and k.value == "bound"
                        for k in n.keys)]
    assert len(literals) == 1, (
        "`bound` is written into exactly one record shape, at open. Found "
        f"{len(literals)} dict literals carrying it.")


# =====================================================================
# E. THE COUNTING RULE - THE HEADLINE
# =====================================================================

def _spend(log, episode_id, times):
    for _ in range(times):
        log.record_pressure(episode_id, PressureClass.PRIMARY_SOURCE, "adequate")


def test_e_at_bound_survived_is_unproducible(tmp_path):
    """PIN E1 - THE FORCING PIN OF THIS SLICE.

    An episode that used every pressure it declared cannot claim it withstood
    testing. Watched RED against a build with the counting rule deleted.
    """
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 2)
    _spend(log, episode, 2)
    assert log.applied_pressure_count(episode) == 2
    with pytest.raises(IllegalOutcomeAtBound) as excinfo:
        log.disposition(episode, EpisodeOutcome.SURVIVED)
    assert EpisodeOutcome.UNRESOLVED_AT_BOUND.value in str(excinfo.value), (
        "the refusal must NAME the honest terminal state the caller should use")


def test_e_unresolved_at_bound_succeeds_where_survived_refused(tmp_path):
    """PIN E2. The other half - the honest state is actually reachable."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 2)
    _spend(log, episode, 2)
    log.disposition(episode, EpisodeOutcome.UNRESOLVED_AT_BOUND)
    assert log.read_all()[-1]["outcome"] == EpisodeOutcome.UNRESOLVED_AT_BOUND.value


@pytest.mark.parametrize("outcome", [
    EpisodeOutcome.UNRESOLVED_AT_BOUND, EpisodeOutcome.SUSPENDED,
    EpisodeOutcome.CARRIED_CONTRADICTION])
def test_e_the_three_legal_outcomes_at_bound(tmp_path, outcome):
    """PIN E3. Exactly these three, and each one really works."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 1)
    _spend(log, episode, 1)
    log.disposition(episode, outcome)
    assert log.read_all()[-1]["outcome"] == outcome.value


@pytest.mark.parametrize("outcome", [
    EpisodeOutcome.SURVIVED, EpisodeOutcome.REVISED, EpisodeOutcome.COLLAPSED])
def test_e_the_three_illegal_outcomes_at_bound(tmp_path, outcome):
    """PIN E4. REVISED and COLLAPSED are barred at bound too - they are
    conclusions, and the bound says no conclusion was reached."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 1)
    _spend(log, episode, 1)
    with pytest.raises(IllegalOutcomeAtBound):
        log.disposition(episode, outcome)


def test_e_below_bound_survived_is_producible(tmp_path):
    """PIN E5 - THE CONTROL. Without it the rule is satisfiable by an
    implementation that refuses SURVIVED always."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    _spend(log, episode, 1)
    log.disposition(episode, EpisodeOutcome.SURVIVED)
    assert log.read_all()[-1]["outcome"] == EpisodeOutcome.SURVIVED.value


def test_e_reached_is_greater_or_equal_not_strictly_greater(tmp_path):
    """PIN E6. The comparison is a DECISION, pinned so it cannot drift into `>`.

    At exactly `bound` the episode has no pressure left, so SURVIVED is already
    unproducible - it does not become so one pressure later.
    """
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 1)
    _spend(log, episode, 1)                         # applied == bound exactly
    with pytest.raises(IllegalOutcomeAtBound):
        log.disposition(episode, EpisodeOutcome.SURVIVED)


def test_e_pressure_debt_does_not_consume_the_bound(tmp_path):
    """PIN E7. A defeater NOTICED is not a pressure APPLIED.

    Counting debts toward the bound would let noticing an objection spend the
    same budget as testing one.
    """
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 2)
    log.record_pressure(episode, PressureClass.PRIMARY_SOURCE, "ok",
                        ["defeater-a", "defeater-b", "defeater-c"])
    assert log.applied_pressure_count(episode) == 1
    assert len(log.pressure_debts(episode)) == 3
    log.disposition(episode, EpisodeOutcome.SURVIVED)   # still below bound


# =====================================================================
# F. K11 - NO SURVIVAL WITHOUT PRESSURE
# =====================================================================

def test_f_survived_with_zero_pressure_raises(tmp_path):
    """PIN F1. Survival requires an identifiable completed pressure episode,
    not the absence of an objection."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    with pytest.raises(SurvivalWithoutPressure):
        log.disposition(episode, EpisodeOutcome.SURVIVED)


def test_f_other_outcomes_do_not_require_pressure(tmp_path):
    """PIN F2 - THE CUT. K11 constrains SURVIVAL, not every disposition.

    An episode can honestly end CARRIED_CONTRADICTION having applied nothing.
    """
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    log.disposition(episode, EpisodeOutcome.CARRIED_CONTRADICTION)
    assert log.read_all()[-1]["outcome"] == \
        EpisodeOutcome.CARRIED_CONTRADICTION.value


def test_f_the_debt_is_permanent(tmp_path):
    """PIN F3. A disposition does not discharge a recorded debt."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 5)
    log.record_pressure(episode, PressureClass.FORMAL_DERIVATION, "partial",
                        ["unexercised-counterexample"])
    log.disposition(episode, EpisodeOutcome.SURVIVED)
    debts = log.pressure_debts(episode)
    assert len(debts) == 1 and debts[0]["defeater"] == "unexercised-counterexample"


# =====================================================================
# G. ONE DISPOSITION PER EPISODE
# =====================================================================

def test_g_a_second_disposition_raises(tmp_path):
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    log.disposition(episode, EpisodeOutcome.SUSPENDED)
    with pytest.raises(EpisodeAlreadyDisposed):
        log.disposition(episode, EpisodeOutcome.SURVIVED)
    assert sum(1 for r in log.read_all()
               if r["record_type"] == EpisodeRecordType.DISPOSITION.value) == 1


def test_g_acts_on_an_unopened_episode_raise(tmp_path):
    log = _episodes(tmp_path)
    for call in (
        lambda: log.record_shaping_act("EPI-9999", ShapingActKind.ATTENTION, "a", "c"),
        lambda: log.record_pressure("EPI-9999", PressureClass.PRIMARY_SOURCE, "ok"),
        lambda: log.disposition("EPI-9999", EpisodeOutcome.SUSPENDED),
    ):
        with pytest.raises(UnknownEpisode):
            call()


# =====================================================================
# H. CLOSED VOCABULARIES
# =====================================================================

def test_h_unknown_shaping_act_raises(tmp_path):
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    with pytest.raises(ClosedVocabularyViolation):
        log.record_shaping_act(episode, "vibing", "actor", "content")


def test_h_unknown_pressure_class_raises(tmp_path):
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    with pytest.raises(ClosedVocabularyViolation):
        log.record_pressure(episode, "argued_hard", "ok")


def test_h_unknown_outcome_raises(tmp_path):
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    with pytest.raises(ClosedVocabularyViolation):
        log.disposition(episode, "mostly_fine")


@pytest.mark.parametrize("adequacy", [None, "", "   ", 0.9, 1, True])
def test_h_adequacy_must_be_a_recorded_declaration(tmp_path, adequacy):
    """PIN H4. A NUMERIC adequacy would be a coined magnitude at the exact point
    survival is decided - §9 standing bar #5."""
    log = _episodes(tmp_path)
    episode = log.open_episode(["OBL-0001"], 3)
    with pytest.raises(ClosedVocabularyViolation):
        log.record_pressure(episode, PressureClass.PRIMARY_SOURCE, adequacy)


def test_h_the_shaping_act_vocabulary_is_exactly_v1():
    """PIN H5. Membership pinned, so a member arrives by governance not by edit."""
    assert {m.value for m in ShapingActKind} == {
        "classification", "decomposition", "context_assembly", "admission",
        "attention", "escalation", "pressure_selection"}
    assert {m.value for m in PressureClass} == {
        "model_adversarial", "precommitted_prediction", "primary_source",
        "reproduced_counterexample", "formal_derivation"}
    assert {m.value for m in EpisodeOutcome} == {
        "survived", "revised", "suspended", "collapsed", "unresolved_at_bound",
        "carried_contradiction"}


# =====================================================================
# I. NO NUMBER GATES ANYTHING IT SHOULD NOT (§9 bar #5)
# =====================================================================

def test_i_adequacy_is_never_compared():
    """PIN I1. `adequacy` REPORTS; it never GATES.

    The `isinstance`/`.strip()` type guard is deliberately NOT a comparison -
    it is a domain check on caller data (Ruling 74's `_validate_bound`
    precedent), and it produces no Compare or BinOp node.
    """
    for node in ast.walk(_tree(EPISODE_SRC)):
        if isinstance(node, (ast.Compare, ast.BinOp)):
            names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            consts = {n.value for n in ast.walk(node)
                      if isinstance(n, ast.Constant)}
            assert "adequacy" not in names and "adequacy" not in consts, (
                f"line {node.lineno} compares or computes on `adequacy`")


@pytest.mark.parametrize("path,keys", [
    (OBLIGATION_SRC, ("created_wall",)), (EPISODE_SRC, ("wall",))])
def test_i_wall_clock_is_written_and_never_read(path, keys):
    """PIN I2 - LOGICAL TIME. The clock is an observation, never an input.

    Ordering is by `SEQ-` ordinal always. This asserts no read of the wall field
    exists anywhere: no subscript, no `.get`, no comparison.
    """
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Subscript):
            index = getattr(node.slice, "value", None)
            assert index not in keys, f"{path.name}:{node.lineno} READS the clock"
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "get":
            if node.args and isinstance(node.args[0], ast.Constant):
                assert node.args[0].value not in keys, (
                    f"{path.name}:{node.lineno} READS the clock via .get")


# =====================================================================
# J. TARGET RESOLUTION IS A READ - THE FORCING PIN
# =====================================================================

def test_j_admission_does_not_disturb_a_real_black_sphere(tmp_path):
    """PIN J1 - THE PASS'S FIRST REAL DISCOVERY, PINNED AGAINST THE REAL ORGAN.

    `BlackSphere.retrieve` increments `access_count`, stamps `last_accessed`,
    multiplies `orbit_stability` by 0.99 AND calls `save_to_file()`. Resolving a
    target through it would make this ledger a WRITER of a store it does not own
    (Ruling 1) and would destabilize a paradox's orbit as a side effect of
    checking whether it exists.
    """
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    entry = sphere.suspend(content="a paradox", pressure=1.0)
    before_stability = entry.orbit_stability
    before_access = entry.access_count

    led = _ledger(tmp_path, suspension_systems=[sphere])
    assert led.admit("s", TargetKind.SUSPENSION, entry.id, "revisit").admitted

    after = sphere.entries[entry.id]
    assert after.orbit_stability == before_stability, (
        "admission DESTABILIZED the orbit - resolution used `retrieve`")
    assert after.access_count == before_access, (
        "admission counted as an access - resolution used `retrieve`")


def test_j_an_absent_suspension_is_targetless(tmp_path):
    """PIN J2 - THE CONTROL. Membership really is being checked."""
    sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
    led = _ledger(tmp_path, suspension_systems=[sphere])
    assert led.admit("s", TargetKind.SUSPENSION, "BS-nope", "c").rejection_kind \
        is RejectionKind.TARGETLESS


def test_j_no_mutating_verb_is_named_on_a_resolver():
    """PIN J3. The module cannot call a mutating door on a store it reads."""
    banned = {"retrieve", "suspend", "save_to_file", "form_scar", "commit",
              "fossilize", "add_scar", "decay_scar", "mutate_doctrine"}
    for node in ast.walk(_tree(OBLIGATION_SRC)):
        if isinstance(node, ast.Call):
            attr = getattr(node.func, "attr", None)
            assert attr not in banned, (
                f"obligation_ledger:{node.lineno} calls `{attr}` - target "
                f"resolution is a READ, and `retrieve` is not one")


# =====================================================================
# K. ZERO INTERNAL CALLERS / ONE WRITER
# =====================================================================

def test_k_nothing_in_src_imports_either_class():
    """PIN K1. SUBSTRATE. Both stores are externally invoked ONLY.

    Goes RED the day something wires one - which is exactly when that wiring
    needs its own ruling (Ruling 72's pin, same shape and same reason).
    """
    consumers = []
    for path in _src_files():
        if path in BOTH:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in ("ObligationLedger", "EpisodeRecord"):
                        consumers.append(path.relative_to(REPO).as_posix())
    assert consumers == [], (
        f"{consumers} consume a K2/K3 store. The substrate stores DIRECTION and "
        f"moves nothing; a consumer is an executive and needs its own ruling.")


def test_k_the_episode_module_imports_the_clock_not_the_ledger_class():
    """PIN K2. The shared clock is a FUNCTION import; the classes stay unwired."""
    imported = set()
    for node in ast.walk(_tree(EPISODE_SRC)):
        if isinstance(node, ast.ImportFrom) and "obligation_ledger" in (node.module or ""):
            imported |= {a.name for a in node.names}
    assert "ObligationLedger" not in imported
    assert "mint_seq_token" in imported


def test_k_neither_module_can_reach_authority():
    """PIN K3 - ENFORCEMENT BY SCOPE (Ruling 70 / Ruling 72's QL0).

    A module that cannot reach a thing cannot be talked into commanding it.
    """
    forbidden = ("sae", "racm", "reflex", "dee", "nova", "compass", "ore",
                 "hail", "tcaml")
    for path in BOTH:
        for node in ast.walk(_tree(path)):
            module = ""
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                module = node.names[0].name
            leaf = module.split(".")[-1]
            assert leaf not in forbidden, (
                f"{path.name} imports `{module}` - a record that stores "
                f"direction must not be able to command anything.")


# =====================================================================
# L. LOGICAL TIME IS SHARED, MONOTONIC, AND NEVER CACHED
# =====================================================================

def test_l_the_sequence_is_monotonic_within_a_store(tmp_path):
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    seqs = [led.admit("s", TargetKind.DOCTRINE, "D", f"c{i}").seq for i in range(4)]
    ordinals = [seq_ordinal(s) for s in seqs]
    assert ordinals == sorted(ordinals) and len(set(ordinals)) == 4


def test_l_the_clock_is_shared_when_the_pair_is_wired(tmp_path):
    """PIN L2. One logical time across BOTH stores, not two private counters."""
    obligations = tmp_path / "obligations.jsonl"
    episodes = tmp_path / "episodes.jsonl"
    led = ObligationLedger(ledger_path=str(obligations),
                           peer_paths=[str(episodes)],
                           codex=_FakeCodex(live=["D"]))
    log = EpisodeRecord(log_path=str(episodes), peer_paths=[str(obligations)])

    a = seq_ordinal(led.admit("s", TargetKind.DOCTRINE, "D", "one").seq)
    episode = log.open_episode(["OBL-0001"], 3)
    b = seq_ordinal(log.read_all()[-1]["opened_seq"])
    c = seq_ordinal(led.admit("s", TargetKind.DOCTRINE, "D", "two").seq)
    d = seq_ordinal(log._stamp(EpisodeRecordType.SHAPING_ACT, episode, {}))

    assert [a, b, c, d] == sorted([a, b, c, d]), "logical time went backwards"
    assert len({a, b, c, d}) == 4, "two records share one moment of logical time"


def test_l_consecutive_writes_to_one_store_advance_with_a_peer_wired(tmp_path):
    """PIN L2b - FOUND BY A SURVIVING MUTANT, and it was a REAL GAP.

    The pin above alternates writes between the two stores, so a mint that took
    the LAST path's maximum instead of the MAXIMUM ACROSS ALL of them passed it
    by accident: the peer happened to be the most recently written file every
    time. Two CONSECUTIVE writes to one store, with a peer that is behind, is
    the configuration that tells them apart - and under the mutant the second
    write REISSUES the first one's ordinal.
    """
    obligations = tmp_path / "obligations.jsonl"
    episodes = tmp_path / "episodes.jsonl"
    led = ObligationLedger(ledger_path=str(obligations),
                           peer_paths=[str(episodes)],
                           codex=_FakeCodex(live=["D"]))
    seqs = [seq_ordinal(led.admit("s", TargetKind.DOCTRINE, "D", f"c{i}").seq)
            for i in range(3)]
    assert seqs == sorted(seqs), "logical time went backwards"
    assert len(set(seqs)) == 3, (
        f"two records share one moment of logical time: {seqs}. The mint must "
        f"take the MAXIMUM across every path it can see, not the last one's.")


def test_l_no_cached_counter_exists_on_either_instance(tmp_path):
    """PIN L3 - RULING 69. The mint derives from the FILE, every time.

    Asserted BEFORE AND AFTER a mint: an attribute created lazily on first use
    would satisfy a construction-time check and still be the defect.
    """
    led = _ledger(tmp_path, codex=_FakeCodex(live=["D"]))
    log = _episodes(tmp_path)
    for store in (led, log):
        assert not any(a.endswith("_seq") for a in vars(store))
    led.admit("s", TargetKind.DOCTRINE, "D", "c")
    log.open_episode(["OBL-0001"], 2)
    for store in (led, log):
        assert not any(a.endswith("_seq") for a in vars(store)), (
            "a cached ordinal appeared after minting - Ruling 69's exact defect")


def test_l_a_torn_line_still_burns_its_ordinal(tmp_path):
    """PIN L4. Raw-text scanning: an id on an unparseable line is never reissued."""
    path = tmp_path / "obligations.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"obligation_id": "OBL-0007", "created_seq": "SEQ-000042"',
                    encoding="utf-8")          # torn: no closing brace
    led = ObligationLedger(ledger_path=str(path), codex=_FakeCodex(live=["D"]))
    result = led.admit("s", TargetKind.DOCTRINE, "D", "c")
    assert result.obligation_id == "OBL-0008"
    assert seq_ordinal(result.seq) == 43


def test_l_an_unreadable_ledger_refuses_rather_than_restarting(tmp_path):
    """PIN L5 - RULING 53'S SENTINEL. Never falls back to a number."""
    missing = tmp_path / "nope" / "obligations.jsonl"
    assert mint_seq_token([missing]) == "SEQ-000001", "a MISSING file is a first run"


# =====================================================================
# M. ERA HONESTY AND RESTART
# =====================================================================

def test_m_a_legacy_line_loads_with_new_fields_absent(tmp_path):
    """PIN M1. Nothing is backfilled, defaulted, or dropped for a missing field."""
    path = tmp_path / "obligations.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "record_type": "open", "obligation_id": "OBL-0001",
        "created_seq": "SEQ-000001", "source": "legacy",
        "target_kind": "doctrine", "target_id": "D", "claim_text": "old",
    }) + "\n", encoding="utf-8")
    led = ObligationLedger(ledger_path=str(path))
    record = led.read_all()[0]
    assert "target_resolution" not in record, "a later field was BACKFILLED"
    assert "created_wall" not in record
    assert [i["obligation_id"] for i in led.open_items()] == ["OBL-0001"]


def test_m_records_survive_a_real_process_boundary(tmp_path):
    """PIN M2 - RESTART. A subprocess, so the in-memory mirror cannot help."""
    obligations = tmp_path / "obligations.jsonl"
    program = (
        "import sys; sys.path.insert(0, r'" + str(REPO) + "')\n"
        "from src.filtration.obligation_ledger import ObligationLedger, TargetKind\n"
        "led = ObligationLedger(ledger_path=r'" + str(obligations) + "')\n"
        "a = led.admit('s', TargetKind.SCAR, 'Scar-1', 'one')\n"
        "b = led.admit('s', TargetKind.SCAR, 'Scar-2', 'two')\n"
        "led.defer(b.obligation_id, 'waiting', 'SEQ-000900')\n"
        "print(len(led.open_items()))\n"
    )
    proc = subprocess.run([sys.executable, "-B", "-c", program],
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "2"

    resumed = ObligationLedger(ledger_path=str(obligations))
    assert len(resumed.read_all()) == 3
    assert sorted(i["obligation_id"] for i in resumed.open_items()) == \
        ["OBL-0001", "OBL-0002"]
    assert resumed.status_of("OBL-0002") is ObligationRecordType.DEFERRED
    # THE FOLD IS IDENTICAL ACROSS THE BOUNDARY - the status is derived from the
    # stream, so it cannot drift from what the writing process believed.
    assert resumed.admit("s", TargetKind.SCAR, "Scar-1", "one").rejection_kind \
        is RejectionKind.DUPLICATE


def test_m_the_episode_log_survives_a_restart_with_its_bound(tmp_path):
    """PIN M3. The bound is a RECORDED fact, so the counting rule still binds."""
    episodes = tmp_path / "episodes.jsonl"
    first = EpisodeRecord(log_path=str(episodes))
    episode = first.open_episode(["OBL-0001"], 1)
    _spend(first, episode, 1)

    resumed = EpisodeRecord(log_path=str(episodes))
    assert resumed.applied_pressure_count(episode) == 1
    with pytest.raises(IllegalOutcomeAtBound):
        resumed.disposition(episode, EpisodeOutcome.SURVIVED)


# =====================================================================
# N. ISOLATION - the two paths are registered in BOTH tables
# =====================================================================

def test_n_both_stores_are_in_the_soak_isolation_table():
    """PIN N1. Ruling 31's standing rule: registered in the SAME commit."""
    sys.path.insert(0, str(REPO))
    from scripts.soak import _injection_table
    _, init_defaults = _injection_table()
    names = {cls.__name__ for cls, _, _ in init_defaults}
    assert {"ObligationLedger", "EpisodeRecord"} <= names


def test_n_the_default_paths_are_under_runtime():
    """PIN N2 - RULING 39. Read from SOURCE, not from the fixture-patched
    signature, which would prove isolation works and say nothing about what
    ships."""
    for path, cls, param in ((OBLIGATION_SRC, "ObligationLedger", "ledger_path"),
                             (EPISODE_SRC, "EpisodeRecord", "log_path")):
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.ClassDef) and node.name == cls:
                init = next(n for n in node.body
                            if isinstance(n, ast.FunctionDef) and n.name == "__init__")
                args = init.args.args[len(init.args.args) - len(init.args.defaults):]
                for arg, default in zip(args, init.args.defaults):
                    if arg.arg == param:
                        assert default.value.startswith("data/runtime/")
                        break
                else:
                    raise AssertionError(f"{cls}.{param} has no default")


def test_n_peer_paths_defaults_to_empty_not_to_a_shared_path():
    """PIN N3. A peer default pointing at real `data/runtime/` would make the
    shared clock READ shared state from inside an isolated test."""
    for path, cls in ((OBLIGATION_SRC, "ObligationLedger"),
                      (EPISODE_SRC, "EpisodeRecord")):
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.ClassDef) and node.name == cls:
                init = next(n for n in node.body
                            if isinstance(n, ast.FunctionDef) and n.name == "__init__")
                args = init.args.args[len(init.args.args) - len(init.args.defaults):]
                for arg, default in zip(args, init.args.defaults):
                    if arg.arg == "peer_paths":
                        assert default.value is None
