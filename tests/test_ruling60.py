"""
test_ruling60.py - SOURCE-GENEALOGY INDEPENDENCE ANALYSIS (Ruling 60 / O2).

Manifest twenty-fifth addendum, 2026-08-01.

    The genealogy of a claim is read from the record,
    and the record cannot certify the world.

THE DOCKET'S NAMED PROBLEM is the ten-thousand-sources-one-origin case: LCAE
compares model outputs and nothing analyzed source DESCENT. The instrument built
here counts origins from the ledger and REFUSES to certify real-world
independence - absence of recorded ancestry yields UNKNOWN, and UNKNOWN never
counts as corroboration.

EVERY PIN MARKED **RED FIRST** WAS WATCHED FAILING AGAINST `733e417`, where
`src/external/source_genealogy.py` did not exist and `Echo` had no linkage field.

COINS NOTHING: four enum members recovered from the record's own three-state
semantics and the docket's registration language, the id grammar is the ledger's
own, and no threshold, weight or magnitude exists anywhere in the module.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.external.claim_ancestry import (ClaimAncestryLedger,
                                         ClaimAncestryRecord, FieldState,
                                         OriginKind, absent, declared_none,
                                         provided)
from src.external.source_genealogy import (CONSULTED_FIELDS, DESCENT_FIELDS,
                                           MINTED_ID_PATTERN,
                                           CorroborationSummary,
                                           GenealogyVerdict, OriginGroup,
                                           corroboration, pairwise_verdict,
                                           recorded_reference_ids,
                                           shares_recorded_asserter)
from src.perception.spl import SPL
from src.utils.echo_memory import EchoMemory
from src.utils.models import Echo

MODULE = Path("src/external/source_genealogy.py")


def _rec(claim_id: str, kind: OriginKind = OriginKind.UNDECLARED,
         **fields) -> ClaimAncestryRecord:
    """A record with every unnamed field ABSENT - the honest default."""
    return ClaimAncestryRecord(claim_id=claim_id, origin_kind=kind, **fields)


def _recorded(claim_id: str, **fields) -> ClaimAncestryRecord:
    """A record whose consulted surfaces are all RECORDS unless overridden.

    DECLARED_NONE, not ABSENT: this is a channel that was asked and answered
    "there are none", which is what lets a claim reach NO_RECORDED_LINK.
    """
    base = {name: declared_none() for name in CONSULTED_FIELDS}
    base.update(fields)
    return _rec(claim_id, **base)


# =====================================================================
# A. THE DOCKET'S NAMED PROBLEM - the counting operation
# =====================================================================

def test_ten_thousand_claims_one_recorded_asserter_is_one_origin() -> None:
    """PIN (a), THE FORCING PIN. **RED FIRST**: the module did not exist.

    THE DOCKET'S REGISTRATION, EXECUTED: claims that all name one recorded
    asserter collapse into ONE origin, however many of them there are. A
    fabricated consensus dies at the counter.
    """
    records = [_rec(f"CLM-{n:04d}", asserted_by=provided("Reuters"))
               for n in range(1, 11)]

    summary = corroboration([r.claim_id for r in records], records)

    assert summary.distinct_recorded_origins == 1, (
        "ten claims repeating one recorded asserter are ONE origin - counting "
        "them as ten is the fabricated-consensus defect the docket registered")
    assert summary.unknown_count == 0
    assert len(summary.groups) == 1
    assert summary.groups[0].claim_ids == tuple(r.claim_id for r in records)


def test_the_shared_asserter_verdict_is_reached_pairwise() -> None:
    """The pairwise half of the same fact, at the verdict level."""
    a = _rec("CLM-0001", asserted_by=provided("Reuters"))
    b = _rec("CLM-0002", asserted_by=provided("Reuters"))
    c = _rec("CLM-0003", asserted_by=provided("AP"))

    assert pairwise_verdict(a, b, [a, b, c]) is GenealogyVerdict.SHARED_ASSERTER
    assert shares_recorded_asserter(a, b) is True
    assert shares_recorded_asserter(a, c) is False


def test_two_declared_none_asserters_are_not_a_shared_asserter() -> None:
    """A shared ABSENCE is not a shared SOURCE.

    Two channels that each declared "there is no asserter" have recorded an
    absence in common. Reading that as a link would MANUFACTURE AN ORIGIN out
    of two statements that no origin exists - the fabrication direction, in the
    one place it would look like tidiness.
    """
    a = _recorded("CLM-0001")
    b = _recorded("CLM-0002")

    assert shares_recorded_asserter(a, b) is False
    assert pairwise_verdict(a, b, [a, b]) is GenealogyVerdict.NO_RECORDED_LINK
    assert corroboration(["CLM-0001", "CLM-0002"], [a, b]
                         ).distinct_recorded_origins == 2


# =====================================================================
# B. UNKNOWN NEVER CORROBORATES
# =====================================================================

def test_undeclared_claims_are_unknown_and_count_toward_no_origin() -> None:
    """PIN (b). **RED FIRST.** Ten thousand undeclared claims -> distinct 0.

    THE REFUSAL THAT MAKES THE INSTRUMENT HONEST. Claims about which nothing was
    recorded cannot corroborate anything - and are not silently promoted to
    distinct origins just because no link was found between them. Absence of
    recorded ancestry is not evidence of independent ancestry.
    """
    records = [_rec(f"CLM-{n:04d}") for n in range(1, 6)]

    summary = corroboration([r.claim_id for r in records], records)

    assert summary.distinct_recorded_origins == 0, (
        "an unrecorded claim is UNCOUNTABLE, not an independent origin - "
        "counting it would let silence corroborate")
    assert summary.unknown_count == 5
    assert summary.unknown_claims == tuple(r.claim_id for r in records)
    assert summary.groups == ()
    assert pairwise_verdict(records[0], records[1], records) is (
        GenealogyVerdict.UNKNOWN)


def test_unknown_never_increments_distinct_in_a_mixed_set() -> None:
    """The mixed case, which is the one a real ledger produces.

    Unknown claims sit BESIDE the origin count, never inside it.
    """
    linked = [_rec(f"CLM-{n:04d}", asserted_by=provided("Reuters"))
              for n in (1, 2, 3)]
    silent = [_rec("CLM-0008"), _rec("CLM-0009")]
    standalone = _recorded("CLM-0010")
    records = linked + silent + [standalone]

    summary = corroboration([r.claim_id for r in records], records)

    assert summary.distinct_recorded_origins == 2, (
        "one shared-asserter group plus one fully-recorded standalone claim")
    assert summary.unknown_count == 2
    assert summary.unknown_claims == ("CLM-0008", "CLM-0009")
    assert sum(len(g.claim_ids) for g in summary.groups) == 4, (
        "no unknown claim leaked into a group")


def test_a_claim_with_no_record_at_all_is_unknown() -> None:
    """The purest form of the condition: nothing was written down."""
    known = _recorded("CLM-0001")

    summary = corroboration(["CLM-0001", "CLM-9999"], [known])

    assert summary.unknown_claims == ("CLM-9999",)
    assert summary.unknown_count == 1
    assert summary.distinct_recorded_origins == 1


# =====================================================================
# C. THE TWO-ABSENCES CUT, BOTH DIRECTIONS
# =====================================================================

def test_declared_none_reaches_no_recorded_link_while_absent_yields_unknown() -> None:
    """PIN (c). **RED FIRST.** Docket H's cut, load-bearing inside a verdict.

    THE WHOLE DISTINCTION IN ONE TEST. Two records identical except that one
    pair ANSWERED the consulted questions ("there are none") and the other pair
    was never asked. Flattening them would make "nobody asked" read as "asked
    and none exist" - the abstention-becomes-honest-zero defect, at the counter.
    """
    answered_a, answered_b = _recorded("CLM-0001"), _recorded("CLM-0002")
    assert pairwise_verdict(answered_a, answered_b, [answered_a, answered_b]) is (
        GenealogyVerdict.NO_RECORDED_LINK)

    unasked_a, unasked_b = _rec("CLM-0003"), _rec("CLM-0004")
    assert pairwise_verdict(unasked_a, unasked_b, [unasked_a, unasked_b]) is (
        GenealogyVerdict.UNKNOWN)


def test_one_absent_surface_on_either_side_is_enough_for_unknown() -> None:
    """ABSENT POISONS - and it does so from EITHER side, on ANY consulted
    surface. A record is not partially consultable."""
    for surface in CONSULTED_FIELDS:
        complete = _recorded("CLM-0001")
        partial = _recorded("CLM-0002", **{surface: absent()})

        assert pairwise_verdict(complete, partial, [complete, partial]) is (
            GenealogyVerdict.UNKNOWN), f"{surface} ABSENT must poison"
        assert pairwise_verdict(partial, complete, [complete, partial]) is (
            GenealogyVerdict.UNKNOWN), f"{surface} ABSENT, other side first"


def test_the_unconsulted_fields_do_not_poison_a_genealogy_verdict() -> None:
    """THE JUDGMENT CALL, PINNED SO IT IS VISIBLE.

    `connecting_assumptions` and `defeaters` bear on an argument's STRUCTURE and
    its REBUTTAL, not on its descent. Consulting them would let an unrelated
    absence drive a genealogy verdict to UNKNOWN while the descent question was
    fully answered. Widening `CONSULTED_FIELDS` is a ruling, not a convenience.
    """
    assert CONSULTED_FIELDS == ("asserted_by", "basis", "replication_refs")
    assert DESCENT_FIELDS == ("basis", "replication_refs")

    a = _recorded("CLM-0001", connecting_assumptions=absent(), defeaters=absent())
    b = _recorded("CLM-0002", connecting_assumptions=absent(), defeaters=absent())

    assert pairwise_verdict(a, b, [a, b]) is GenealogyVerdict.NO_RECORDED_LINK


# =====================================================================
# D. DESCENT AND TRANSITIVITY
# =====================================================================

def test_a_recorded_citation_is_descent_and_chains_transitively() -> None:
    """PIN (d). **RED FIRST.** A <- B <- C collapses to ONE origin.

    The transitive half is the one that matters for the docket's problem: the
    common ancestor is usually not the claim in front of you.
    """
    a = _recorded("CLM-0001")
    b = _recorded("CLM-0002", basis=provided("derived from CLM-0001"))
    c = _recorded("CLM-0003", replication_refs=provided(["CLM-0002"]))
    records = [a, b, c]

    assert pairwise_verdict(a, b, records) is GenealogyVerdict.RECORDED_DESCENT
    assert pairwise_verdict(a, c, records) is GenealogyVerdict.RECORDED_DESCENT, (
        "descent is a PATH, not only a direct edge")

    summary = corroboration(["CLM-0001", "CLM-0002", "CLM-0003"], records)
    assert summary.distinct_recorded_origins == 1
    assert summary.groups[0].claim_ids == ("CLM-0001", "CLM-0002", "CLM-0003")


def test_descent_groups_through_an_uncounted_common_ancestor() -> None:
    """THE TEN-THOUSAND-SOURCES CASE IN ITS REAL SHAPE.

    Two counted claims that both descend from an ancestor NOT in the counted set
    still collapse into one origin. Grouping runs over the whole corpus for
    exactly this reason - the shared origin is usually not the thing being
    counted.
    """
    ancestor = _recorded("CLM-0001")
    left = _recorded("CLM-0002", basis=provided("CLM-0001"))
    right = _recorded("CLM-0003", basis=provided("CLM-0001"))

    summary = corroboration(["CLM-0002", "CLM-0003"],
                            [ancestor, left, right])

    assert summary.distinct_recorded_origins == 1, (
        "two claims descending from one uncounted ancestor are ONE origin")
    assert summary.groups[0].claim_ids == ("CLM-0002", "CLM-0003")


def test_descent_is_read_from_both_surfaces_and_from_nested_values() -> None:
    """A PROVIDED value may be prose, a list, or a nested structure the channel
    handed in - all of it deep-frozen by the record. Every string inside it is
    read, keys included."""
    assert recorded_reference_ids(
        _recorded("CLM-0009", basis=provided("see CLM-0001"))) == {"CLM-0001"}
    assert recorded_reference_ids(
        _recorded("CLM-0009", replication_refs=provided(["CLM-0002"]))) == {"CLM-0002"}
    assert recorded_reference_ids(
        _recorded("CLM-0009",
                  basis=provided({"cited": ["CLM-0003", "CLM-0004"]}))
    ) == {"CLM-0003", "CLM-0004"}
    assert recorded_reference_ids(
        _recorded("CLM-0009", basis=provided({"CLM-0005": "as cited"}))
    ) == {"CLM-0005"}, "a reference recorded as a KEY is still recorded"


def test_a_self_citation_is_not_descent() -> None:
    """A record naming its own id has not descended from anything."""
    solo = _recorded("CLM-0001", basis=provided("CLM-0001"))
    assert recorded_reference_ids(solo) == frozenset()
    assert corroboration(["CLM-0001"], [solo]).distinct_recorded_origins == 1


def test_only_provided_surfaces_can_cite() -> None:
    """DECLARED_NONE and ABSENT cite nothing - the first because it said so,
    the second because it said nothing. Neither can produce an edge."""
    for state_fields in ({"basis": declared_none()}, {"basis": absent()}):
        assert recorded_reference_ids(
            _recorded("CLM-0009", **state_fields)) == frozenset()


def test_a_citation_cycle_terminates() -> None:
    """Ruling 4: DECLARED-BOUNDED by a visited set, on any graph.

    Two records citing each other is possible in principle, and the visited set
    is what makes that a finite answer rather than a hang.

    THE SECOND HALF WAS ADDED AFTER A SURVIVING MUTANT, and the gap it exposed
    was real rather than equivalent. Deleting the visited set left the FIRST
    assertion green: `a` cites `b` directly, so the walk returns on its first
    hop and never revisits anything. The load-bearing case is a cycle that does
    NOT contain the target - there the frontier refills forever, and only the
    visited set turns that into an answer. A termination pin whose target is
    one hop away is not a termination pin.
    """
    a = _recorded("CLM-0001", basis=provided("CLM-0002"))
    b = _recorded("CLM-0002", basis=provided("CLM-0001"))

    assert pairwise_verdict(a, b, [a, b]) is GenealogyVerdict.RECORDED_DESCENT
    assert corroboration(["CLM-0001", "CLM-0002"], [a, b]
                         ).distinct_recorded_origins == 1

    # The walk must terminate while searching a cycle for a target that is not
    # in it. If the visited set is gone, this does not fail - it HANGS.
    unrelated = _recorded("CLM-0003")
    assert pairwise_verdict(a, unrelated, [a, b, unrelated]) is (
        GenealogyVerdict.NO_RECORDED_LINK)
    assert corroboration(["CLM-0001", "CLM-0003"], [a, b, unrelated]
                         ).distinct_recorded_origins == 2


# =====================================================================
# E. THE NO-MATCH CONTROL - the scanner-fires discipline at birth
# =====================================================================

def test_prose_without_a_minted_id_creates_no_edge() -> None:
    """PIN (e). **RED FIRST.** EXACT MINTED IDS ONLY.

    THE DOCKET H SUBSTRING LESSON, DISTINGUISHED. That scan misfired because it
    matched OPEN PROSE. This grammar is CLOSED and house-minted - so a basis
    that describes descent in words, without citing an id, records NO edge.
    Anything subtler than an exact id is inference wearing a record's clothes,
    and is a FUTURE RULING.
    """
    ancestor = _recorded("CLM-0001")
    prosaic = _recorded(
        "CLM-0002",
        basis=provided("derived from the earlier wire report, obviously"))

    assert recorded_reference_ids(prosaic) == frozenset()
    assert pairwise_verdict(ancestor, prosaic, [ancestor, prosaic]) is (
        GenealogyVerdict.NO_RECORDED_LINK)
    assert corroboration(["CLM-0001", "CLM-0002"], [ancestor, prosaic]
                         ).distinct_recorded_origins == 2


def test_a_minted_id_is_not_matched_by_a_longer_id_that_contains_it() -> None:
    """RULING 49'S LESSON, SCAR-SIDE: `Doctrine-0` is a prefix of
    `Doctrine-0.1`, and `CLM-0001` is a prefix of `CLM-00010`.

    The pattern takes the MAXIMAL digit run and the comparison is EXACT STRING
    EQUALITY, so a longer id never grazes a shorter one. This is the single
    most natural way for this module to start grouping everything with
    everything.
    """
    short = _recorded("CLM-0001")
    longer = _recorded("CLM-0002", basis=provided("CLM-00010"))

    assert recorded_reference_ids(longer) == {"CLM-00010"}
    assert pairwise_verdict(short, longer, [short, longer]) is (
        GenealogyVerdict.NO_RECORDED_LINK)


def test_no_numeric_normalization_happens_anywhere() -> None:
    """`CLM-0001` and `CLM-1` are DIFFERENT STRINGS and stay different.

    Parsing the tail as an integer would silently merge them, which would be a
    grouping decision made by a number format.
    """
    padded = _recorded("CLM-0001")
    unpadded = _recorded("CLM-0002", basis=provided("CLM-1"))

    assert recorded_reference_ids(unpadded) == {"CLM-1"}
    assert pairwise_verdict(padded, unpadded, [padded, unpadded]) is (
        GenealogyVerdict.NO_RECORDED_LINK)


def test_the_id_grammar_agrees_with_the_ledger_that_mints_the_ids(tmp_path) -> None:
    """THE GRAMMAR IS THE LEDGER'S OWN, and this pin is what keeps the two from
    drifting apart while the module stays free of the writer.

    The module deliberately does NOT import `ClaimAncestryLedger` (pin (g)), so
    agreement is asserted against a REALLY MINTED id rather than assumed.
    """
    ledger = ClaimAncestryLedger(ledger_path=str(tmp_path / "cl.jsonl"))
    minted = ledger.record().claim_id

    assert MINTED_ID_PATTERN.findall(f"see {minted} for details") == [minted]
    assert minted.startswith(ClaimAncestryLedger.ID_PREFIX)


# =====================================================================
# F. THE LINKAGE, END TO END
# =====================================================================

def test_the_echo_carries_exactly_the_claim_id_of_its_own_ledger_line() -> None:
    """PIN (f), THE FORCING PIN. **RED FIRST**: `Echo` had no linkage field.

    THE PROPERTY RULING 58 BUILT, WITNESSED END TO END FOR THE FIRST TIME: one
    ledger line per perceived claim, and the echo that claim produced points
    back at it.
    """
    core = AureaCore()

    first = core.process_input("Water is wet.", source="test")
    second = core.process_input("The sky is green.", source="test")

    assert first["echo"].claim_id == first["claim_id"] == "CLM-0001"
    assert second["echo"].claim_id == second["claim_id"] == "CLM-0002"
    assert first["echo"].claim_id != second["echo"].claim_id, (
        "each claim carries ITS OWN ledger line, not the pass before it")


def test_the_linkage_survives_the_echo_store_round_trip(tmp_path) -> None:
    """A join key that does not persist is not a join key."""
    core = AureaCore()
    result = core.process_input("Water is wet.", source="test")

    path = tmp_path / "echo_roundtrip.jsonl"
    EchoMemory(filepath=str(path)).add_echo(result["echo"])
    reloaded = EchoMemory(filepath=str(path)).echoes

    assert len(reloaded) == 1
    assert reloaded[0].claim_id == result["claim_id"]


def test_a_legacy_persisted_echo_without_the_key_loads_as_none() -> None:
    """NEVER SYNTHESIZED. `None` honestly means "predates the record".

    NO BACKFILL of stored echoes - moving persisted bytes is Ruling 58's own
    bar, and a synthesized id would be a fabricated origin link, which is the
    exact defect this docket exists to close.
    """
    legacy = {"id": "Echo-legacy", "content": "x", "source": "user",
              "resonance_score": 1.0, "created_at": "2020-01-01T00:00:00"}

    assert Echo(**legacy).claim_id is None


def test_spl_called_standalone_defaults_to_none() -> None:
    """A standalone call mints no record, so it has no id to carry - and does
    not invent one."""
    assert SPL().process_input("hello").claim_id is None


def test_the_claim_id_is_set_at_construction_and_is_keyword_only() -> None:
    """No post-hoc mutation: an echo that acquired its linkage after the fact
    would have existed, however briefly, unattributable.

    KEYWORD-ONLY mirrors Ruling 58's `origin`, and it is what stops the id
    being passed positionally into `doctrine_link` by a caller counting
    arguments.
    """
    with pytest.raises(TypeError):
        SPL().process_input("hello", "user", None, "CLM-0001")

    echo = SPL().process_input("hello", claim_id="CLM-0007")
    assert echo.claim_id == "CLM-0007"


def test_result_gains_no_new_key() -> None:
    """`result['claim_id']` is Ruling 58's key and remains the only one. The
    linkage rides on the ECHO, not on a second surface."""
    core = AureaCore()
    result = core.process_input("Water is wet.", source="test")

    assert "claim_id" in result
    assert "genealogy" not in result and "source_genealogy" not in result
    assert "ancestry" not in result


# =====================================================================
# G. THE MODULE IS READ-ONLY, AND STORES NO STANDING
# =====================================================================

def test_the_module_holds_no_write_handle_of_any_kind() -> None:
    """PIN (g). **RED FIRST** (no module existed).

    PURE, READ-ONLY ANALYSIS. The caller reads the ledger; this module never
    touches a file, holds no path, and does not import the WRITER. A module
    that could write would be a store, and it is not registered as one.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(alias.name for alias in node.names)

    forbidden = {"json", "pathlib", "Path", "os", "shutil", "io",
                 "ClaimAncestryLedger", "atomic_write"}
    assert forbidden.isdisjoint(imported), (
        f"the analysis imported a write-capable name: "
        f"{sorted(forbidden & imported)}")

    called = {node.func.id for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in called, "a read-only analysis does not open files"


def test_the_write_handle_scanner_actually_fires() -> None:
    """Ruling 32's answer to the vacuous-pin problem: feed the scanner the
    forbidden shapes and a benign control, so a scan that has stopped scanning
    fails HERE rather than passing quietly forever."""
    forbidden = ast.parse("import json\nfrom pathlib import Path\n"
                          "open('x', 'w')\n")
    benign = ast.parse("import re\nfrom enum import Enum\n")

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

    assert {"json", "pathlib", "Path", "open"} <= names(forbidden)
    assert {"json", "pathlib", "Path", "open"}.isdisjoint(names(benign))


def test_the_analysis_stores_no_epistemic_standing() -> None:
    """THE L3 STANDING SCAN, EXTENDED TO THE NEW FILE.

    The tree-wide half already covered this module the moment it was written
    (`tests/test_ruling58.py`); this is the MODULE-SCOPED half, which catches
    the generic tokens that are somebody else's legitimate vocabulary
    elsewhere. A stored tier / reliability / trust would be a second writer of
    what the record already determines.

    THE GENERIC HALF MATCHES WHOLE SNAKE_CASE WORDS, NOT SUBSTRINGS, and that
    is a deliberate sharpening of Ruling 58's instrument. Written as a
    substring scan it flagged `frontier` - which CONTAINS `tier` - inside the
    transitive-closure loop: a correct local variable, reported as stored
    epistemic standing. THIRD OCCURRENCE of the substring-scanner false
    positive in this suite (Batch 51, then Ruling 58's `net_evidence` prose
    match, now this), and the first one where the honest fix was available
    locally. THE INSTRUMENT WAS CHANGED, NOT THE CODE IT SCANS: renaming a
    correct variable to satisfy a noisy guard is how a guard earns the
    weakening it eventually gets. Reported to the architect - the shared
    scanner in `test_ruling58.py` still matches by substring.
    """
    distinctive = ("admissibility", "reliability", "trust_score",
                   "credibility", "epistemic_")
    generic = {"tier", "standing", "score", "weight", "confidence"}

    offenders = []
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for target in targets:
            name = (target.attr if isinstance(target, ast.Attribute)
                    else target.id if isinstance(target, ast.Name) else "")
            if not name:
                continue
            words = set(name.lower().split("_"))
            if (any(token in name.lower() for token in distinctive)
                    or words & generic):
                offenders.append(f"{node.lineno} {name}")

    assert offenders == [], (
        f"epistemic standing is being STORED at {offenders}. The analysis "
        f"reports counts of record only - no weights, no scores, no thresholds")


def test_the_standing_scanner_fires_and_does_not_fire_on_frontier() -> None:
    """The fires-control for the SHARPENED instrument, with the exact false
    positive that forced the sharpening as the benign case.

    Both halves are asserted: a real stored standing is caught, and `frontier`
    is not. A scanner that only ever passes is a comment.
    """
    generic = {"tier", "standing", "score", "weight", "confidence"}
    distinctive = ("admissibility", "reliability", "trust_score",
                   "credibility", "epistemic_")

    def flagged(source):
        out = []
        for node in ast.walk(ast.parse(source)):
            for target in (node.targets if isinstance(node, ast.Assign) else []):
                name = (target.attr if isinstance(target, ast.Attribute)
                        else target.id if isinstance(target, ast.Name) else "")
                if not name:
                    continue
                if (any(t in name.lower() for t in distinctive)
                        or set(name.lower().split("_")) & generic):
                    out.append(name)
        return out

    assert flagged("record.reliability = 0.9\n") == ["reliability"]
    assert flagged("self.origin_tier = 2\n") == ["origin_tier"]
    assert flagged("group.confidence = 1\n") == ["confidence"]
    assert flagged("frontier = [start]\nfrontiers_seen = 0\n") == [], (
        "`frontier` contains `tier` and is NOT stored standing - this is the "
        "false positive the sharpening exists to prevent")


def test_the_module_carries_no_magnitude() -> None:
    """STANDING BAR #5. The counts REPORT; nothing compares them.

    A cutoff here would be a coined threshold at the exact point corroboration
    is decided - "N sources is enough" - which is the judgement this instrument
    exists to hand to a ruling rather than make.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))

    floats = [node.value for node in ast.walk(tree)
              if isinstance(node, ast.Constant) and isinstance(node.value, float)]
    assert floats == [], f"a float literal appeared in the analysis: {floats}"

    counted = {"distinct_recorded_origins", "unknown_count"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for side in [node.left] + list(node.comparators):
                name = (side.attr if isinstance(side, ast.Attribute)
                        else side.id if isinstance(side, ast.Name) else "")
                assert name not in counted, (
                    f"line {node.lineno}: the corroboration counts are being "
                    f"COMPARED. They report, they do not gate")


def test_no_module_in_src_consumes_the_analysis() -> None:
    """NO CONSUMER WIRING THIS PASS, and that is a resolution rather than an
    omission: no verdict path, no HAIL surface, no routing reads it (O4 owns
    routing). This pin goes RED the day one does - which is exactly when the
    consumer needs a ruling."""
    consumers = [path.as_posix() for path in Path("src").rglob("*.py")
                 if path != MODULE
                 and "source_genealogy" in path.read_text(encoding="utf-8")]

    assert consumers == [], (
        f"{consumers} consume the genealogy analysis. Wiring it into a verdict, "
        f"an expression surface or a routing decision is a RULING (Ruling 60 "
        f"res.1 and res.6), not an implementation choice")


# =====================================================================
# H. THE VOCABULARY IS CLOSED, AND ONE MEMBER IS REFUSED
# =====================================================================

def test_the_verdict_enum_is_closed_at_four_and_refuses_independent() -> None:
    """PIN (h), THE REFUSAL PINNED AS SHAPE. **RED FIRST.**

    THE RULING'S SHARPEST LINE. The ledger records ASSERTIONS ABOUT descent; it
    cannot see the world. Two claims with no recorded link may still share an
    origin nobody wrote down - so "INDEPENDENT" would be the analysis
    certifying something it never observed. `NO_RECORDED_LINK` is the strongest
    honest claim available, and the naming carries the epistemics.
    """
    assert {member.name for member in GenealogyVerdict} == {
        "SHARED_ASSERTER", "RECORDED_DESCENT", "NO_RECORDED_LINK", "UNKNOWN"}

    assert not hasattr(GenealogyVerdict, "INDEPENDENT")
    with pytest.raises(ValueError):
        GenealogyVerdict("independent")


def test_origin_kind_is_reported_but_never_consulted_for_standing() -> None:
    """RES.6: two claims sharing a source CLASS share nothing.

    `human` and `human` is a category, not a link. It is REPORTED on the group
    and never reaches the pairwise path - pinned in BOTH directions, because
    the tempting error is symmetric.
    """
    same_kind_a = _recorded("CLM-0001", )
    same_kind_b = _recorded("CLM-0002")
    assert same_kind_a.origin_kind is same_kind_b.origin_kind
    assert pairwise_verdict(same_kind_a, same_kind_b, [same_kind_a, same_kind_b]
                            ) is GenealogyVerdict.NO_RECORDED_LINK, (
        "a shared source CLASS is not a shared source")

    cross_a = _rec("CLM-0003", OriginKind.HUMAN, asserted_by=provided("Reuters"))
    cross_b = _rec("CLM-0004", OriginKind.EXTERNAL_AI,
                   asserted_by=provided("Reuters"))
    assert pairwise_verdict(cross_a, cross_b, [cross_a, cross_b]) is (
        GenealogyVerdict.SHARED_ASSERTER), (
        "differing source classes do not break a recorded shared asserter")

    summary = corroboration(["CLM-0003", "CLM-0004"], [cross_a, cross_b])
    assert summary.groups[0].recorded_origin_kinds == ("external_ai", "human"), (
        "the kinds are REPORTED on the group")


def test_the_summary_is_frozen_and_has_no_serialization_surface() -> None:
    """EPHEMERAL, never persisted. A serialization surface is how an analysis
    becomes a store, and this module owns nothing."""
    summary = corroboration(["CLM-0001"], [_recorded("CLM-0001")])

    assert isinstance(summary, CorroborationSummary)
    with pytest.raises(Exception):
        summary.distinct_recorded_origins = 99
    with pytest.raises(Exception):
        summary.groups[0].claim_ids = ()

    for surface in ("as_dict", "to_dict", "save", "save_to_file"):
        assert not hasattr(summary, surface), (
            f"CorroborationSummary.{surface} would make an ephemeral analysis "
            f"persistable, and a persisted analysis is a store")
    assert not hasattr(OriginGroup, "as_dict")
