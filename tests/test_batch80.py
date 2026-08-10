"""
test_batch80.py - RULINGS 81 and 82 of the consolidation batch.

RULING 81 - THE NOVA MINT IS CLOSED BY DISPOSITION, and the pin here is what
makes that disposition checkable rather than merely argued. Ruling 69's class
(a cached derivation of a file, trusted over its source) does NOT apply: `_seq`
rides INSIDE the atomic snapshot with the record it numbers, persists at the
moment of minting, and is floor-validated at load. **A counter carried in the
record it numbers, atomic with that record, is not a cached derivation - it is
the record.** What makes that safe is the load-time floor, so the load-time
floor is what gets pinned.

RULING 82 - `provided()` REFUSES THE EMPTY IDENTITY. Ruling 70 flagged it and
declined to decide it; Ruling 64 res.7 had already closed the identical failure
mode for `None`. This is res.7's guard in its other spelling.

WHERE THE REST OF THE BATCH LIVES: Ruling 80's cases are in
`data/eval/seed_cases.jsonl` and are driven by `scripts/evaluate.py` (a corpus,
not a suite file). Ruling 83 produced a CENSUS and a disposition table, which
land in the pass report rather than here - by instruction, and because a census
of what exists today is a reading, not a law.
"""

from __future__ import annotations

import json

import pytest

from src.expansion.nova import (DOCTRINE_AUTHORSHIP_ORIGIN, NovaEngine)
from src.external.claim_ancestry import (AncestryField, ClaimAncestryRecord,
                                         FieldState, OriginDeclaration,
                                         OriginKind, absent, declared_none,
                                         provided)
from src.external.model_provider import model_declaration
from src.external.source_genealogy import shares_recorded_asserter
from src.utils.continuity import RestorationOutcome


# =====================================================================
# RULING 81 - THE LOAD-TIME FLOOR IS THE DISPOSITION'S LOAD-BEARING HALF
# =====================================================================

def test_r81_a_seq_below_the_recorded_floor_resumes_from_the_floor():
    """**THE PIN RULING 81 IS CLOSED ON.** Hand-written, below-floor `seq`.

    THE DISPOSITION'S ARGUMENT IS THAT `_seq` IS NOT A CACHED DERIVATION - it
    rides in the atomic snapshot with the ids it numbers, so it cannot drift
    from them the way `cae._seq` drifted from its ledger. **What stops a
    DAMAGED or HAND-EDITED file from re-issuing a live id is the load-time
    floor**, and an argument that rests on a mechanism is only as good as the
    mechanism, so the mechanism is pinned by construction.

    A file claiming `seq=1` while carrying `NE-0003` is asserting that one id
    was issued when three demonstrably were. The recorded IDS win: they are
    facts on disk, and `seq` is a summary of them.
    """
    nova = NovaEngine()
    for i in range(3):
        nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id=f"D-{i}")
    path = nova.runtime_path

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["seq"] == 3
    recorded = sorted(e["id"] for e in payload["echo_index"])
    assert recorded[-1] == "NE-0003"
    payload["seq"] = 1                      # the file understates what it holds
    path.write_text(json.dumps(payload), encoding="utf-8")

    resumed = NovaEngine()

    assert resumed._seq == 3, (
        "a `seq` below the highest recorded NE- ordinal must resume from the "
        "DERIVED floor - the ids are the record, the counter is a summary")
    assert resumed.load_report.outcome is RestorationOutcome.MIGRATED, (
        "resuming from the derived floor is a DERIVATION, not a clean restore, "
        "and the report must say which")


def test_r81_the_next_mint_after_a_below_floor_load_collides_with_nothing():
    """RULING 81, the consequence half - and the one that actually matters.

    The floor is not interesting as a number; it is interesting because of what
    it prevents. `NE-0002` already names an echo that may have AUTHORED
    (Ruling 13: one echo backs one proposal, EVER), so re-issuing it would put
    two authorships under one id in a record where nothing can afterwards tell
    them apart.
    """
    nova = NovaEngine()
    for i in range(3):
        nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id=f"D-{i}")
    path = nova.runtime_path
    payload = json.loads(path.read_text(encoding="utf-8"))
    before = {e["id"] for e in payload["echo_index"]}
    payload["seq"] = 0                       # the worst case: a reset counter
    path.write_text(json.dumps(payload), encoding="utf-8")

    resumed = NovaEngine()
    minted = resumed.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN,
                           origin_id="D-new")

    assert minted.id == "NE-0004"
    assert minted.id not in before, (
        f"the mint reissued '{minted.id}', which already names a recorded echo")


def test_r81_the_mint_rides_in_the_same_snapshot_as_the_ids_it_numbers():
    """RULING 81's premise, asserted rather than assumed.

    THIS IS THE WHOLE REASON THE RULING 69 CLASS DOES NOT APPLY. `cae._seq` was
    a counter in MEMORY derived once from a file it then stopped consulting;
    this one is a FIELD IN THE FILE, written in the same atomic snapshot as the
    `echo_index` it summarizes. If that ever stops being true - if `seq` moves
    to its own file, or is written on a different path - the disposition needs
    re-taking, and this pin is what says so.
    """
    nova = NovaEngine()
    nova.erupt(origin_kind=DOCTRINE_AUTHORSHIP_ORIGIN, origin_id="D-1")
    payload = json.loads(nova.runtime_path.read_text(encoding="utf-8"))

    assert "seq" in payload and "echo_index" in payload, (
        "the mint and the ids it numbers must ride in ONE snapshot")
    assert payload["seq"] == len(payload["echo_index"]) == 1


# =====================================================================
# RULING 82 - THE EMPTY IDENTITY IS REFUSED
# =====================================================================

@pytest.mark.parametrize("degenerate", ["", " ", "\t", "\n", "   \t \n "])
def test_r82_provided_refuses_empty_and_whitespace_only_strings(degenerate):
    """**RULING 82.** Ruling 64 res.7's guard in its other spelling.

    Whitespace-only is the same defect wearing a character: `" "` is not an
    identity, and two of them collide exactly as two empty strings do.
    """
    with pytest.raises(ValueError) as excinfo:
        provided(degenerate)
    message = str(excinfo.value)
    assert "declared_none()" in message and "absent()" in message, (
        "the refusal must name BOTH honest alternatives, as res.7's does")


def test_r82_a_whitespace_str_subclass_is_refused_too():
    """RULING 82. The guard tests the VALUE, not the exact type.

    A `str` subclass is still a string, and a caller reaching this door with one
    is not thereby exempt - `isinstance` is what makes the guard about what the
    value IS rather than about how it was spelled.
    """
    class Identity(str):
        pass

    with pytest.raises(ValueError):
        provided(Identity("   "))
    assert provided(Identity("real")).value == "real"


def test_r82_the_shared_asserter_defect_is_witnessed_DEAD():
    """RULING 82's actual subject, and the reason the guard is worth having.

    THE DEFECT: two records carrying an empty asserter are both PROVIDED and
    compare EQUAL, so `shares_recorded_asserter` reads TWO EMPTY STRINGS AS ONE
    SHARED SOURCE - manufacturing the corroboration collapse that module exists
    to compute honestly. **The state is now unconstructible**, so the defect is
    dead at the door rather than handled downstream.

    The positive control is the load-bearing half: a REAL shared asserter must
    still collapse, or this pin would pass against a genealogy module that had
    simply stopped working.
    """
    with pytest.raises(ValueError):
        provided("")

    def record(claim_id, asserter):
        return ClaimAncestryRecord.from_declaration(
            claim_id, OriginDeclaration(kind=OriginKind.MODEL_PREDICTION,
                                        asserted_by=asserter))

    # The positive control, and it is the load-bearing half: without it this
    # pin would pass against a genealogy module that had simply stopped
    # collapsing anything at all.
    shared = provided("gpt-fictional-v9")
    assert shares_recorded_asserter(record("CLM-0001", shared),
                                    record("CLM-0002", shared)) is True, (
        "a REAL shared asserter must still read as shared")

    # And two records that DECLARED no asserter still do not share one - the
    # neighbouring rule this guard must not have disturbed.
    assert shares_recorded_asserter(record("CLM-0003", declared_none()),
                                    record("CLM-0004", declared_none())) is False


def test_r82_a_real_value_is_untouched_and_never_stripped():
    """RULING 82. The guard REFUSES a degenerate value; it never REPAIRS one.

    Ruling 70 res.1 records the declared model identity BYTE-IDENTICAL, so a
    value with real content and incidental whitespace passes through EXACTLY as
    given. Stripping it here would silently record an identity the caller did
    not declare - the fabrication class, arriving as a helpful tidy-up.
    """
    field = provided("  gpt-fictional-v9  ")
    assert field.value == "  gpt-fictional-v9  "
    assert field.state is FieldState.PROVIDED


def test_r82_non_string_values_are_untouched():
    """RULING 82 is about STRINGS, and the boundary is deliberate.

    An empty LIST or DICT is a value a channel supplied, and deciding what an
    empty replication list MEANS is a genealogy question this guard has no
    standing to answer. Widening it there would change what a recorded
    declaration means, which is not what this ruling did.
    """
    for value in ([], {}, 0, False, ()):
        field = provided(value)
        assert field.state is FieldState.PROVIDED
        assert field.value == value


def test_r82_absent_and_declared_none_are_untouched():
    """RULING 82 changes what PROVIDED ACCEPTS. It changes nothing about what
    ABSENT or DECLARED_NONE MEAN - Docket H's two-absences cut is unmoved."""
    assert absent().state is FieldState.ABSENT
    assert declared_none().state is FieldState.DECLARED_NONE
    assert absent().value is None and declared_none().value is None
    assert absent() != declared_none()


def test_r82_the_model_door_refuses_an_empty_identity_through_the_vocabulary():
    """RULING 82 res.: the guard lives in `provided()`, NOT in the adapter.

    **AND THE ADAPTER GAINS NO CHECK OF ITS OWN** - a second guard here would
    be a second definition of one rule, free to drift from it. This asserts the
    refusal arrives at the model door WITHOUT `model_provider` having grown a
    guard: the vocabulary refuses, one frame down.
    """
    with pytest.raises(ValueError):
        model_declaration("")
    with pytest.raises(ValueError):
        model_declaration("   ")

    declaration = model_declaration("gpt-fictional-v9")
    assert declaration.asserted_by.value == "gpt-fictional-v9"


def test_r82_the_adapter_did_not_grow_its_own_guard():
    """RULING 82, the structural half of the same point."""
    import ast
    from pathlib import Path

    source = Path("src/external/model_provider.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    func = [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "model_declaration"][0]
    raises = [ast.unparse(n.exc) for n in ast.walk(func)
              if isinstance(n, ast.Raise) and n.exc is not None]

    assert all("TypeError" in r for r in raises), (
        f"model_declaration grew a non-type guard: {raises}. Ruling 82 put the "
        f"empty-identity refusal in the VOCABULARY, and a copy here would be a "
        f"second definition of one rule.")
