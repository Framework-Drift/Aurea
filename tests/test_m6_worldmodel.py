"""
test_m6_worldmodel.py - M6-β (standing is a derivation) + M6-γ (the
contradiction surface routes into L4) + THE ACCEPTANCE.

    **THE WORLD MODEL HAS NO PRIVATE TRUTH MACHINERY. ITS CONFLICTS STAND IN
    THE SAME COURT AS EVERYTHING ELSE.**

THE ACCEPTANCE IS THE POINT OF THE PASS: a driven world contradiction lands end
to end through EXISTING machinery - two propositions written through the real
doors, mutually contradicted, detected, admitted, episoded, dispositioned - with
**every fact read FROM THE FILES**, and nothing new between M3's loop and M6's
store.

RED-FIRST is a COLLECTION ERROR for the β/γ modules (they do not exist at the
parent), and that is stated rather than dressed up. **THE ACCEPTANCE HAS A REAL
ONE**: neuter the detection and it fails; neuter the write-time reference
resolution and its refusal pin fails. Both were driven and are reported.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.external.claim_ancestry import ClaimAncestryLedger, OriginDeclaration
from src.external.prediction_ledger import (PredictionLedger, PredictionOutcome,
                                            provided)
from src.filtration.episode_record import EpisodeRecord
from src.filtration.obligation_ledger import (ObligationLedger,
                                              ObligationRecordType, TargetKind,
                                              TargetResolution)
from src.filtration.scar_logic_core import ScarLogicCore
from src.filtration.scar_management import LIVE_STATES
from src.worldmodel.contradiction_surface import (Inconsistency,
                                                  InconsistencyKind,
                                                  ROUTING_SOURCE,
                                                  detect_inconsistencies,
                                                  route_inconsistencies)
from src.worldmodel.proposition_ledger import (KernelRef, KernelRefKind,
                                               PropositionKind,
                                               PropositionLedger)
from src.worldmodel.standing import (PREDICTION_CONFIRMED, PREDICTION_FALSIFIED,
                                     PREDICTION_UNRESOLVED, RULE_NAME,
                                     RULE_VERSION, SCAR_LIVE_STATES,
                                     ReferenceState, StandingBasis,
                                     WorldStanding, derive_standing)

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
STANDING = SRC / "worldmodel" / "standing.py"
SURFACE = SRC / "worldmodel" / "contradiction_surface.py"


def _ref(field, kind, record_id, present=True, state=None):
    return ReferenceState(field=field, kind=kind, record_id=record_id,
                          present=present, state=state)


# =====================================================================
# (β-a) THE DERIVATION IS PURE
# =====================================================================

def test_beta_a_the_derivation_is_stdlib_only_and_imports_no_store():
    """R79's shape, its second reuse. **A derivation that could reach the
    kernel could be talked into CHANGING what it is measuring.**"""
    imported = set()
    for node in ast.walk(ast.parse(STANDING.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "src" not in imported, (
        f"the derivation acquired a project import: {sorted(imported)}")
    assert imported <= {"__future__", "dataclasses", "enum", "typing"}


def test_beta_a_the_derivation_touches_no_file_and_persists_nothing():
    source = STANDING.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in {"open", "read_text", "write_text", "mkdir",
                                "durable_append_text", "atomic_write_json",
                                "atomic_write_text"}, f"filesystem work: {name}"
    assert "Path(" not in source
    for banned in ("def save", "def _persist", "self.cache", "lru_cache"):
        assert banned not in source, f"the derivation persists: {banned}"


def test_beta_a_the_mirrored_vocabulary_equals_the_real_enums():
    """M3-C's MOVE: the duplication is DETECTED, not prevented.

    Purity means this module cannot import `PredictionOutcome` or the scar
    `LIVE_STATES`, so their values are mirrored - a second definition, and
    therefore a drift risk. This test is the boundary: a vocabulary change
    reddens here instead of silently diverging.
    """
    assert PREDICTION_CONFIRMED == PredictionOutcome.CONFIRMED.value
    assert PREDICTION_FALSIFIED == PredictionOutcome.FALSIFIED.value
    assert PREDICTION_UNRESOLVED == PredictionOutcome.UNRESOLVED.value
    assert {o.value for o in PredictionOutcome} == {
        PREDICTION_CONFIRMED, PREDICTION_FALSIFIED, PREDICTION_UNRESOLVED}
    assert set(SCAR_LIVE_STATES) == {s.value for s in LIVE_STATES}


def test_beta_a_the_derivation_carries_no_magnitude():
    """Section 9's bar #5, its tenth application. The rule is ORDINAL.

    **SCANNED BY AST OVER CODE, NOT BY SUBSTRING OVER TEXT** - and the first
    draft was the latter, which flagged the word "threshold" inside this
    module's own paragraph explaining that it has none. That is this repo's
    most-repeated instrument defect, and Ruling 63's precedent governs the
    remedy: sharpen the scanner, leave the prose standing.
    """
    tree = ast.parse(STANDING.read_text(encoding="utf-8"))
    banned = {"threshold", "score", "weight", "confidence", "priority", "rank"}
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            for t in targets:
                name = getattr(t, "id", None) or getattr(t, "attr", None)
                if name and name.lower() in banned:
                    offenders.append(f"{name}:{node.lineno}")
        # No float arithmetic anywhere: an ordinal rule needs none.
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            offenders.append(f"float {node.value}:{node.lineno}")
    assert offenders == [], f"the derivation coined a magnitude: {offenders}"

    # The only integer literals are the structural 0/1 of "any" and "none".
    ints = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, int)
            and not isinstance(n.value, bool)}
    assert ints <= {0, 1}, f"the derivation carries a magnitude literal: {ints}"


def test_beta_a_the_rule_is_named_and_versioned():
    """L7: an unnamed combination rule is one nobody can later say was changed."""
    assert RULE_NAME == "m6.standing.v1"
    assert RULE_VERSION == 1
    verdict = derive_standing([])
    assert verdict.rule == RULE_NAME and verdict.rule_version == RULE_VERSION


# =====================================================================
# (β-b) THE READINGS, AND THE COMBINATION
# =====================================================================

def test_beta_b_a_falsified_prediction_supports_nothing():
    """**R64's REVERSED-MEANING DEFECT, REFUSED AT ITS SOURCE.** A refuted
    expectation must never read as standing knowledge."""
    verdict = derive_standing([
        _ref("supported_by", "prediction", "PRD-0001",
             state=PREDICTION_FALSIFIED)])

    assert verdict.standing is WorldStanding.UNGROUNDED, (
        "a proposition whose only citation was falsified is UNSUPPORTED, not "
        "supported - and not opposed either")
    assert verdict.live_support == ()
    assert verdict.discounted == (
        ("PRD-0001", StandingBasis.PREDICTION_FALSIFIED_SUPPORTS_NOTHING.value),)


def test_beta_b_a_confirmed_prediction_supports():
    verdict = derive_standing([
        _ref("supported_by", "prediction", "PRD-0001",
             state=PREDICTION_CONFIRMED)])
    assert verdict.standing is WorldStanding.SUPPORTED
    assert verdict.live_support == ("PRD-0001",)


def test_beta_b_an_unsettled_prediction_supports_nothing_yet():
    verdict = derive_standing([
        _ref("supported_by", "prediction", "PRD-0001", state=None)])
    assert verdict.standing is WorldStanding.UNGROUNDED
    assert StandingBasis.PREDICTION_UNSETTLED in verdict.basis


@pytest.mark.parametrize("state", sorted(SCAR_LIVE_STATES))
def test_beta_b_a_live_scar_in_contradicted_by_weighs_against(state):
    verdict = derive_standing([
        _ref("contradicted_by", "scar", "Scar-0", state=state)])
    assert verdict.standing is WorldStanding.UNDERCUT
    assert verdict.live_contradiction == ("Scar-0",)


def test_beta_b_a_cooled_scar_no_longer_weighs():
    """Ruling 54's cut: what is ON RECORD vs what still BEARS."""
    verdict = derive_standing([
        _ref("contradicted_by", "scar", "Scar-0", state="dormant")])
    assert verdict.standing is WorldStanding.UNGROUNDED
    assert verdict.live_contradiction == ()
    assert ("Scar-0", StandingBasis.SCAR_COOLED.value) in verdict.discounted


def test_beta_b_ungrounded_derives_zero_with_the_reason_named():
    verdict = derive_standing([])
    assert verdict.standing is WorldStanding.UNGROUNDED
    assert verdict.basis == (StandingBasis.NO_REFERENCES,)


def test_beta_b_support_and_contradiction_together_are_contested():
    verdict = derive_standing([
        _ref("supported_by", "claim", "CLM-0001"),
        _ref("contradicted_by", "scar", "Scar-0", state="active")])
    assert verdict.standing is WorldStanding.CONTESTED
    assert verdict.live_support == ("CLM-0001",)
    assert verdict.live_contradiction == ("Scar-0",)


def test_beta_b_the_rule_counts_nothing():
    """ORDINAL, NOT NUMERIC - and this is the pin that says so.

    Three live supports against one live contradiction is CONTESTED exactly as
    one against one. A rule that weighed them would need a coined magnitude at
    the point someone wants a proposition to hold up.
    """
    many = derive_standing([
        _ref("supported_by", "claim", f"CLM-000{i}") for i in range(1, 4)
    ] + [_ref("contradicted_by", "scar", "Scar-0", state="active")])
    one = derive_standing([
        _ref("supported_by", "claim", "CLM-0001"),
        _ref("contradicted_by", "scar", "Scar-0", state="active")])
    assert many.standing is one.standing is WorldStanding.CONTESTED


def test_beta_b_a_reference_whose_record_vanished_counts_for_nothing():
    """DERIVING AT THE CURRENT STATE IS THE POINT. The write law checked at
    write; the kernel has moved since, and the derivation says so."""
    verdict = derive_standing([
        _ref("supported_by", "claim", "CLM-0001", present=False)])
    assert verdict.standing is WorldStanding.UNGROUNDED
    assert ("CLM-0001", StandingBasis.RECORD_STATE_UNKNOWN.value) in verdict.discounted


def test_beta_b_the_verdict_carries_the_facts_that_produced_it():
    """Ruling 45's move: a reader can disagree with a COINED rule only if the
    verdict says what it saw."""
    verdict = derive_standing([
        _ref("supported_by", "prediction", "PRD-0001", state=PREDICTION_CONFIRMED),
        _ref("contradicted_by", "scar", "S-1", state="dormant")])
    payload = verdict.as_dict()
    assert payload["rule"] == RULE_NAME
    assert payload["live_support"] == ["PRD-0001"]
    assert payload["discounted"] == [["S-1", "scar_cooled"]]
    assert payload["basis"] == ["prediction_confirmed_supports", "scar_cooled"]


# =====================================================================
# (γ-a) THE TARGETKIND WIDENING
# =====================================================================

def test_gamma_a_world_proposition_is_the_fifth_member(tmp_path):
    assert TargetKind.WORLD_PROPOSITION.value == "world_proposition"
    assert {m.value for m in TargetKind} == {
        "doctrine", "scar", "suspension", "claim", "world_proposition"}


def test_gamma_a_a_recorded_proposition_always_resolves(tmp_path):
    """The claim-resolves rule's sibling: that ledger never erases, so
    membership is the whole question."""
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    record = props.record(PropositionKind.STATE, "the bridge stands")
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           proposition_ledger=props)

    result = obl.admit(source="t", target_kind=TargetKind.WORLD_PROPOSITION,
                       target_id=record.wmp_id, claim_text="owed about it")
    assert result.admitted
    assert result.target_resolution is TargetResolution.RESOLVED


def test_gamma_a_an_unrecorded_proposition_is_targetless(tmp_path):
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           proposition_ledger=props)
    result = obl.admit(source="t", target_kind=TargetKind.WORLD_PROPOSITION,
                       target_id="WMP-9999", claim_text="x")
    assert not result.admitted
    assert result.target_resolution is TargetResolution.UNRESOLVED


def test_gamma_a_no_resolver_is_unchecked_not_unresolved(tmp_path):
    """Docket H's cut, which M3-A put on this ledger: "I could not look" is not
    "it is not there"."""
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"))
    result = obl.admit(source="t", target_kind=TargetKind.WORLD_PROPOSITION,
                       target_id="WMP-0001", claim_text="x")
    assert result.admitted
    assert result.target_resolution is TargetResolution.UNCHECKED


def test_gamma_a_the_existing_kinds_are_byte_unmoved(tmp_path):
    """The widening adds; it moves nothing. Driven, not read."""
    ancestry = ClaimAncestryLedger(ledger_path=str(tmp_path / "c.jsonl"))
    claim = ancestry.record(OriginDeclaration())
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           ancestry_ledger=ancestry)
    result = obl.admit(source="t", target_kind=TargetKind.CLAIM,
                       target_id=claim.claim_id, claim_text="still works")
    assert result.admitted and result.target_resolution is TargetResolution.RESOLVED


# =====================================================================
# (γ-b) DETECTION IS RECORD-HONEST, AND STRUCTURALLY SO
# =====================================================================

def test_gamma_b_a_declared_contradiction_is_detected(tmp_path):
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    record = props.record(PropositionKind.CONTRADICTION,
                          "the bridge both stands and is closed")

    found = detect_inconsistencies(props.live_summaries())
    assert len(found) == 1
    assert found[0].kind is InconsistencyKind.DECLARED_CONTRADICTION
    assert found[0].target_id == record.wmp_id


def test_gamma_b_a_mutual_contradiction_is_detected_and_names_the_newer(tmp_path):
    path = tmp_path / "p.jsonl"
    props = PropositionLedger(ledger_path=str(path))
    first = props.record(PropositionKind.STATE, "the bridge stands")
    second = props.record(PropositionKind.STATE, "the bridge is closed")
    _link(path, first.wmp_id, second.wmp_id)

    reopened = PropositionLedger(ledger_path=str(path))
    found = [f for f in detect_inconsistencies(reopened.live_summaries())
             if f.kind is InconsistencyKind.MUTUAL_CONTRADICTION]
    assert len(found) == 1
    assert set(found[0].involved) == {first.wmp_id, second.wmp_id}
    assert found[0].target_id == second.wmp_id, (
        "the NEWER proposition is named - it arrived into an existing world")


def test_gamma_b_a_one_way_citation_is_not_an_inconsistency(tmp_path):
    """**A ONE-WAY `contradicted_by` IS AN ORDINARY CITATION**, which is what
    the field is FOR. Treating every one as a conflict would flood L4 with the
    normal case.

    **THE FIRST DRAFT OF THIS PIN WAS VACUOUS AND A SURVIVING MUTANT SAID SO:**
    it built two propositions with NO citation at all, so it asserted that
    nothing is detected where nothing could be. A genuine one-way link is
    constructed here instead - A names B, B does not name A.
    """
    path = tmp_path / "p.jsonl"
    props = PropositionLedger(ledger_path=str(path))
    first = props.record(PropositionKind.STATE, "a")
    second = props.record(PropositionKind.STATE, "b")
    _link_one_way(path, first.wmp_id, second.wmp_id)

    reopened = PropositionLedger(ledger_path=str(path))
    summaries = reopened.live_summaries()
    cited = [s for s in summaries if s.contradicted_by]
    assert len(cited) == 1, "the fixture must build a REAL one-way citation"
    assert cited[0].contradicted_by[0].record_id == second.wmp_id

    assert detect_inconsistencies(summaries) == (), (
        "a one-way citation is a stance, not a declared conflict")


def _link_one_way(path: Path, citer_id: str, cited_id: str) -> None:
    """`citer` names `cited`; `cited` names nobody. The harness shim's sibling."""
    lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    for line in lines:
        if line["wmp_id"] == citer_id:
            line["contradicted_by"] = [{"kind": "claim", "record_id": cited_id}]
    path.write_text("".join(json.dumps(l) + "\n" for l in lines),
                    encoding="utf-8")


def test_gamma_b_a_superseded_partner_does_not_form_a_live_pair(tmp_path):
    """The other half N11 needed: a mutual pair whose PARTNER has been
    superseded is not a live conflict. Detection reads the live set, and the
    membership check is what enforces it."""
    path = tmp_path / "p.jsonl"
    props = PropositionLedger(ledger_path=str(path))
    first = props.record(PropositionKind.STATE, "a")
    second = props.record(PropositionKind.STATE, "b")
    _link(path, first.wmp_id, second.wmp_id)
    PropositionLedger(ledger_path=str(path)).record(
        PropositionKind.STATE, "b, revised", supersedes=second.wmp_id)

    reopened = PropositionLedger(ledger_path=str(path))
    mutual = [f for f in detect_inconsistencies(reopened.live_summaries())
              if f.kind is InconsistencyKind.MUTUAL_CONTRADICTION]
    assert mutual == [], (
        "the partner is superseded, so the pair is not live - a conflict "
        "between a live proposition and a retired one is not a live conflict")

    # A JUSTIFIED EQUIVALENT MUTANT IS ANNOTATED HERE (the house's practice):
    # deleting `other not in live_ids` from the surface's pair check leaves this
    # pin GREEN, and it is genuinely equivalent - MEASURED, not assumed.
    # `contradicts` is built from the SAME summaries as `live_ids`, so the two
    # share a key set: an `other` outside `live_ids` is also outside
    # `contradicts`, `.get(other, ())` returns empty, and the mutual test skips
    # it anyway. **THE CHECK IS KEPT** because it states the intent at the point
    # a reader looks for it, and it stops being equivalent the moment a caller
    # passes something other than the live set.


def test_gamma_b_the_surface_cannot_read_content_at_all():
    """**ENFORCEMENT BY SCOPE.** v1's record-honest floor is not a rule anyone
    must remember - `PropositionSummary` carries no `asserted_content`, so
    semantic inference is unavailable to this module.

    Semantic detection is COGNITION and arrives with the Executive; naming its
    owner is the honest half of declaring a limitation.
    """
    source = SURFACE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    reads = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Attribute) and n.attr == "asserted_content"]
    assert reads == [], f"the surface reads content at {reads}"
    # ...and it has no way to get one: it holds no ledger and opens nothing.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            # `.get(` on a dict is ordinary; what must not appear is a call to
            # one of the LEDGER's content-carrying doors.
            assert name not in {"open", "propositions", "live", "_get_record",
                                "_records"}, (
                f"the surface reaches a content door: {name}")


def test_gamma_b_detection_is_pure_and_touches_no_store(tmp_path):
    """Detection takes ALREADY-READ summaries. Measured: the file is untouched."""
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    props.record(PropositionKind.CONTRADICTION, "x")
    before = Path(props.ledger_path).read_bytes()

    detect_inconsistencies(props.live_summaries())
    assert Path(props.ledger_path).read_bytes() == before


def test_gamma_b_a_superseded_contradiction_is_not_live(tmp_path):
    """The live set is a fold, and detection reads the LIVE set."""
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    old = props.record(PropositionKind.CONTRADICTION, "resolved since")
    props.record(PropositionKind.STATE, "the resolution", supersedes=old.wmp_id)

    assert detect_inconsistencies(props.live_summaries()) == ()
    assert len(props.summaries()) == 2, "and nothing was erased"


# =====================================================================
# (γ-c) THE ROUTING
# =====================================================================

def test_gamma_c_a_detected_inconsistency_admits_an_obligation(tmp_path):
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    record = props.record(PropositionKind.CONTRADICTION, "an inconsistency")
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           proposition_ledger=props)

    outcome = route_inconsistencies(detect_inconsistencies(props.live_summaries()),
                                    obl)
    assert len(outcome.admitted) == 1
    assert outcome.failures == ()

    entry = obl.read_all()[0]
    assert entry["source"] == ROUTING_SOURCE
    assert entry["target_kind"] == "world_proposition"
    assert entry["target_id"] == record.wmp_id
    assert entry["record_type"] == ObligationRecordType.OPEN.value


def test_gamma_c_routing_never_raises_into_a_read_path(tmp_path):
    """RULING 11's VALENCE: the observer never gates the observed. A world-model
    read must not fail because the obligation ledger was unavailable."""
    class Broken:
        def admit(self, **kwargs):
            raise OSError("the obligation ledger is unavailable")

    item = Inconsistency(kind=InconsistencyKind.DECLARED_CONTRADICTION,
                         target_id="WMP-0001", involved=("WMP-0001",),
                         claim_text="x")
    outcome = route_inconsistencies([item], Broken())
    assert outcome.admitted == ()
    assert len(outcome.failures) == 1
    assert "OSError" in outcome.failures[0][1]


def test_gamma_c_a_duplicate_conflict_is_rejected_not_failed(tmp_path):
    """The obligation ledger's OWN rules apply, and its refusals are RECORDS -
    refusing a second obligation for a conflict already standing is right."""
    props = PropositionLedger(ledger_path=str(tmp_path / "p.jsonl"))
    props.record(PropositionKind.CONTRADICTION, "an inconsistency")
    obl = ObligationLedger(ledger_path=str(tmp_path / "o.jsonl"),
                           proposition_ledger=props)

    found = detect_inconsistencies(props.live_summaries())
    first = route_inconsistencies(found, obl)
    second = route_inconsistencies(found, obl)

    assert len(first.admitted) == 1
    assert second.admitted == () and len(second.rejected) == 1
    assert second.failures == ()


def test_gamma_c_nothing_in_src_calls_the_surface():
    """Ruling 72's no-consumer form: M6 wires no automatic routing. The
    Executive owns that at M7, and this reddens the day it arrives."""
    callers = []
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        if rel.endswith("worldmodel/contradiction_surface.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.ImportFrom)
                    and "contradiction_surface" in (node.module or "")):
                callers.append(f"{rel}:{node.lineno}")
    assert callers == [], f"the surface acquired a `src/` consumer: {callers}"


# =====================================================================
# THE ACCEPTANCE - end to end, through EXISTING machinery
# =====================================================================

def test_acceptance_a_world_contradiction_reaches_a_typed_disposition(tmp_path):
    """**THE PASS'S OWN ACCEPTANCE.** Two propositions written through the real
    doors, mutually contradicted, detected, admitted, episoded, dispositioned.

    **EVERY FACT IS READ FROM THE FILES** - the stores are re-opened at each
    stage rather than trusted in memory, because a loop that only holds together
    in one process has not demonstrated the thing M6 claims: that the world
    model's conflicts stand in the same court as everything else, adjudicated by
    the machinery M3 already built, with NOTHING NEW BETWEEN THEM.
    """
    props_path = tmp_path / "propositions.jsonl"
    obl_path = tmp_path / "obligations.jsonl"
    epi_path = tmp_path / "episodes.jsonl"

    # --- 1. TWO PROPOSITIONS, through the real door, mutually contradicting.
    props = PropositionLedger(ledger_path=str(props_path))
    stands = props.record(PropositionKind.STATE, "the bridge stands")
    closed = props.record(PropositionKind.STATE, "the bridge is closed")
    # Each names the other. Supersession is how this ledger updates, so the
    # mutual link is built by replacing both with successors that cite across.
    a2 = props.record(PropositionKind.STATE, "the bridge stands",
                      supersedes=stands.wmp_id)
    b2 = props.record(PropositionKind.STATE, "the bridge is closed",
                      supersedes=closed.wmp_id)
    _link(props_path, a2.wmp_id, b2.wmp_id)

    # --- 2. DETECTION, from a FRESHLY OPENED ledger.
    reopened = PropositionLedger(ledger_path=str(props_path))
    found = detect_inconsistencies(reopened.live_summaries())
    mutual = [f for f in found if f.kind is InconsistencyKind.MUTUAL_CONTRADICTION]
    assert len(mutual) == 1, f"detection found {found}"
    assert set(mutual[0].involved) == {a2.wmp_id, b2.wmp_id}

    # --- 3. ADMISSION, through the EXISTING seam.
    obl = ObligationLedger(ledger_path=str(obl_path), proposition_ledger=reopened)
    outcome = route_inconsistencies(mutual, obl)
    assert len(outcome.admitted) == 1 and outcome.failures == ()

    admitted = json.loads(obl_path.read_text(encoding="utf-8").splitlines()[0])
    assert admitted["target_kind"] == "world_proposition"
    assert admitted["source"] == ROUTING_SOURCE
    obligation_id = admitted["obligation_id"]

    # --- 4. AN EPISODE, opened against it through M3's own door.
    episodes = EpisodeRecord(log_path=str(epi_path))
    episode_id = episodes.open_episode([obligation_id], 3)
    obl.mark_episode_opened(obligation_id, episode_id)

    # --- 5. A TYPED DISPOSITION, read FROM THE FILE.
    from src.filtration.episode_record import EpisodeOutcome
    episodes.disposition(episode_id, EpisodeOutcome.CARRIED_CONTRADICTION)

    resumed = EpisodeRecord(log_path=str(epi_path))
    lines = [json.loads(l) for l in
             epi_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    dispositions = [l for l in lines if l.get("outcome")]
    assert len(dispositions) == 1
    assert dispositions[0]["episode_id"] == episode_id
    assert dispositions[0]["outcome"] == EpisodeOutcome.CARRIED_CONTRADICTION.value

    # ...and the obligation is out of the standing set, because it is being
    # WORKED rather than waiting - M3-A's own fold, unchanged by M6.
    resumed_obl = ObligationLedger(ledger_path=str(obl_path))
    assert obligation_id not in [i["obligation_id"] for i in resumed_obl.open_items()]

    # --- 6. NOTHING NEW BETWEEN THEM: the world store was never written by the
    # loop, and the loop's stores were never written by the world.
    assert len(reopened.summaries()) == 4, "the propositions are untouched"


def _link(path: Path, a_id: str, b_id: str) -> None:
    """Make two recorded propositions name each other.

    **A HARNESS SHIM, AND IT IS STATED AS ONE.** The ledger has no update family
    by ruling, and v1 has no writer that composes a mutual pair in one act - the
    Executive owns proposition-writing at M7. So the acceptance edits the
    RECORDED LINES to express the mutual citation the detector is specified to
    find. It writes no new record and mints no id; every other step of the
    acceptance runs through the real doors.
    """
    lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    for line in lines:
        if line["wmp_id"] == a_id:
            line["contradicted_by"] = [{"kind": "claim", "record_id": b_id}]
        elif line["wmp_id"] == b_id:
            line["contradicted_by"] = [{"kind": "claim", "record_id": a_id}]
    path.write_text("".join(json.dumps(l) + "\n" for l in lines), encoding="utf-8")


def test_acceptance_the_detection_is_load_bearing(tmp_path):
    """**THE FIRES CONTROL FOR THE ACCEPTANCE** (Ruling 35).

    Neuter the mutual link and the acceptance's detection step finds nothing -
    so the test above is measuring the detector rather than passing because
    something always returns a result.
    """
    props_path = tmp_path / "p.jsonl"
    props = PropositionLedger(ledger_path=str(props_path))
    props.record(PropositionKind.STATE, "the bridge stands")
    props.record(PropositionKind.STATE, "the bridge is closed")

    reopened = PropositionLedger(ledger_path=str(props_path))
    assert detect_inconsistencies(reopened.live_summaries()) == (), (
        "with no mutual citation there is no inconsistency - the acceptance's "
        "detection step is load-bearing")
