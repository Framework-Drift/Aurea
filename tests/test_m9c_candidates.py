"""test_m9c_candidates.py - M9-c: THE PREMIUM SOURCE MADE MECHANICAL.

Hundred-nineteenth entry (PATH v145), M9_GROUNDING.md section M9-c, on L6's
own words: carried contradiction is a GENERATIVE state. The derivation
(`discriminating-candidate-generator.v1`), its acts on the PRA- stream, the
governed bridge (`commit_candidate`), and THE JOINT's first witness.

EVERY PIN HERE IS RED AGAINST `830df2a`, where the generator, the candidate
act kinds, the bridge door and `derived_from` did not exist - the file fails
at collection (ImportError), witnessed in a detached worktree.

THE FIXTURE WORLD IS BUILT THROUGH THE KERNEL'S OWN DOORS (claims through the
ancestry ledger, propositions through the proposition ledger with its real
resolver, the carried contradiction through the Black Sphere's own suspend
with its Ruling-76 claim join), except the mutual contradiction link, which
uses the M6 test suite's own harness shim - `KernelRefKind` cannot name a
proposition, so the tree's ruled detection matches on record_id alone, and
this file drift-pins the generator's mirror of that rule against the ruled
surface itself.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.executive.act_log_audit import (FindingKind,
                                         PREDICTION_ACT_LOG_SCHEMA,
                                         audit_act_log)
from src.executive.candidate_generator import (GENERATOR_NAME,
                                               GENERATOR_VERSION,
                                               REGISTRATION,
                                               CandidateGenerator,
                                               CandidateLicenseBasis,
                                               CandidatePrediction,
                                               DeclineBasis, DraftedLicense)
from src.executive.inquiry_generator import (CandidatePartition, DriftBasis,
                                             LicenseBasis)
from src.executive.loop import ExecutiveLoop
from src.executive.prediction_act_log import PredictionActLog
from src.external.acquisition_ledger import AcquisitionLedger
from src.external.claim_ancestry import (ClaimAncestryLedger,
                                         OriginDeclaration, OriginKind)
from src.external.prediction_ledger import (DependencyKind, FieldState,
                                            OperationalCriterion,
                                            PredictionLedger, TypedDependency)
from src.filtration.obligation_ledger import ObligationLedger
from src.goals.goal_ledger import (GoalKind, GoalLedger, GoalLevel,
                                   GoalProvenance)
from src.suspension.black_sphere import BlackSphere
from src.worldmodel.contradiction_surface import (InconsistencyKind,
                                                  detect_inconsistencies)
from src.worldmodel.proposition_ledger import (KernelRef, KernelRefKind,
                                               PropositionKind,
                                               PropositionLedger)

GENERATOR_MODULE = Path("src/executive/candidate_generator.py")


# =====================================================================
# THE WORLD - built once per test, through the kernel's own doors
# =====================================================================

def _link_mutual(path: Path, first_id: str, second_id: str) -> None:
    """The M6 suite's harness shim, verbatim semantics: each names the other.

    `KernelRefKind` cannot name a proposition, so the ruled detection matches
    on record_id membership in the live set; the shim stores the WMP id under
    a shim kind exactly as `test_m6_worldmodel._link` does.
    """
    lines = [json.loads(l) for l in
             path.read_text(encoding="utf-8").splitlines() if l.strip()]
    for line in lines:
        if line["wmp_id"] == first_id:
            line["contradicted_by"] = [
                {"kind": "claim", "record_id": second_id}]
        if line["wmp_id"] == second_id:
            line["contradicted_by"] = [
                {"kind": "claim", "record_id": first_id}]
    path.write_text("".join(json.dumps(l) + "\n" for l in lines),
                    encoding="utf-8")


class _World:
    def __init__(self, tmp_path, with_goal=True):
        self.ancestry = ClaimAncestryLedger(
            ledger_path=str(tmp_path / "clm.jsonl"))
        self.claim_a = self.ancestry.record(
            OriginDeclaration(kind=OriginKind.HUMAN)).claim_id
        self.claim_b = self.ancestry.record(
            OriginDeclaration(kind=OriginKind.HUMAN)).claim_id

        self.prop_path = tmp_path / "wmp.jsonl"
        propositions = PropositionLedger(
            ledger_path=str(self.prop_path), ancestry_ledger=self.ancestry)
        self.prop_a = propositions.record(
            PropositionKind.STATE, "the state claim A asserts",
            supported_by=[KernelRef(kind=KernelRefKind.CLAIM,
                                    record_id=self.claim_a)]).wmp_id
        self.prop_b = propositions.record(
            PropositionKind.STATE, "the state claim B asserts",
            supported_by=[KernelRef(kind=KernelRefKind.CLAIM,
                                    record_id=self.claim_b)]).wmp_id
        _link_mutual(self.prop_path, self.prop_a, self.prop_b)
        self.propositions = PropositionLedger(
            ledger_path=str(self.prop_path), ancestry_ledger=self.ancestry)

        self.sphere = BlackSphere(filepath=str(tmp_path / "bs.json"))
        self.suspension = self.sphere.suspend(
            "claims A and B cannot both hold", 0.95,
            reason="carried contradiction", paradox_type="contradiction",
            claim_id=self.claim_a)

        self.goals = GoalLedger(ledger_path=str(tmp_path / "glc.jsonl"))
        if with_goal:
            self.goal = self.goals.commit(
                desired_state="keep claim A honest under test",
                kind=GoalKind.VERIFICATION, level=GoalLevel.PROJECT,
                provenance=GoalProvenance.EXTERNAL_PROPOSAL,
                asserter="m9c-pins",
                justification_claim_ids=(self.claim_a,))

        self.predictions = PredictionLedger(
            ledger_path=str(tmp_path / "prd.jsonl"), goal_ledger=self.goals)
        self.obligations = ObligationLedger(
            ledger_path=str(tmp_path / "obl.jsonl"),
            prediction_ledger=self.predictions,
            proposition_ledger=self.propositions,
            ancestry_ledger=self.ancestry)
        self.loop = ExecutiveLoop(
            obligations=self.obligations, predictions=self.predictions,
            goals=self.goals,
            acquisitions=AcquisitionLedger(
                ledger_path=str(tmp_path / "acq.jsonl")),
            prediction_acts=PredictionActLog(
                log_path=str(tmp_path / "pra.jsonl")))

    def derive(self):
        return self.loop.derive_candidates(
            list(self.sphere.entries.values()),
            self.propositions.live_summaries())


# =====================================================================
# PIN 1 - DETERMINISM, TWICE
# =====================================================================

def test_same_records_same_candidates_same_declines_twice(tmp_path) -> None:
    """PIN 1. Two generator instances over one reading agree exactly."""
    world = _World(tmp_path)
    entries = list(world.sphere.entries.values())
    summaries = world.propositions.live_summaries()
    goals = world.goals.commitments()
    first = CandidateGenerator().derive(entries, summaries, goals)
    second = CandidateGenerator().derive(entries, summaries, goals)
    assert first == second
    assert len(first.candidates) == 1 and first.declined == ()


# =====================================================================
# PIN 2 - DERIVE OR DECLINE, BOTH DIRECTIONS, NEVER PADDED
# =====================================================================

def test_the_full_structure_yields_the_candidate(tmp_path) -> None:
    """PIN 2, the derive half - and the draft is exactly the records' own."""
    world = _World(tmp_path)
    [candidate] = world.derive().candidates
    assert candidate.suspension_id == world.suspension.id
    assert (candidate.claim_a, candidate.claim_b) == (world.claim_a,
                                                      world.claim_b)
    assert candidate.criterion.surface == "world_proposition_standing"
    assert candidate.criterion.record_id == world.prop_a
    assert candidate.criterion.confirmed_state == "supported"
    assert candidate.criterion.failed_state == "undercut"
    kinds = [(d.kind, d.record_form, d.record_id)
             for d in candidate.typed_dependencies]
    assert kinds == [
        (DependencyKind.SCOPE, "suspension", world.suspension.id),
        (DependencyKind.MAIN_CLAIM, "claim", world.claim_a),
        (DependencyKind.ASSUMPTION, "claim", world.claim_b),
        (DependencyKind.OBSERVATION, "world_proposition", world.prop_a),
        (DependencyKind.OBSERVATION, "world_proposition", world.prop_b),
    ]
    assert candidate.license.basis is CandidateLicenseBasis.JUSTIFICATION_CLAIM
    assert candidate.license.goal_id == world.goal.goal_id
    assert candidate.license.via_claim == world.claim_a


def test_missing_edges_decline_with_their_bases_never_padding(tmp_path) -> None:
    """PIN 2, the decline half: three different missing RECORDED edges,
    three bases, and the output is exactly one line per contradiction -
    padding unrepresentable."""
    world = _World(tmp_path)
    # (a) no claim join - the tether's own honest shape (claim_id=None).
    unjoined = world.sphere.suspend("no claim behind this", 0.9)
    # (b) a claim reaching no live proposition.
    orphan_claim = world.ancestry.record(
        OriginDeclaration(kind=OriginKind.HUMAN)).claim_id
    orphaned = world.sphere.suspend("an orphan claim", 0.9,
                                    claim_id=orphan_claim)
    derivation = world.derive()

    assert len(derivation.candidates) == 1
    bases = {d.suspension_id: d.basis for d in derivation.declined}
    assert bases == {
        unjoined.id: DeclineBasis.NO_CLAIM_JOIN,
        orphaned.id: DeclineBasis.CLAIM_REACHES_NO_LIVE_PROPOSITION,
    }
    for decline in derivation.declined:
        assert decline.detail
    accounted = ({c.suspension_id for c in derivation.candidates}
                 | {d.suspension_id for d in derivation.declined})
    assert accounted == set(world.sphere.entries.keys()), (
        "a contradiction left the derivation silently - the one forbidden "
        "outcome")


def test_a_one_way_citation_declines_as_no_mutual_contradiction(tmp_path) -> None:
    """PIN 2 + the M6 surface's own rule: a one-way `contradicted_by` is a
    stance, not a recorded conflict."""
    world = _World(tmp_path)
    lines = [json.loads(l) for l in
             world.prop_path.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if line["wmp_id"] == world.prop_b:
            line["contradicted_by"] = []          # B no longer names A
    world.prop_path.write_text(
        "".join(json.dumps(l) + "\n" for l in lines), encoding="utf-8")
    world.propositions = PropositionLedger(
        ledger_path=str(world.prop_path), ancestry_ledger=world.ancestry)

    derivation = world.derive()
    assert derivation.candidates == ()
    [decline] = derivation.declined
    assert decline.basis is DeclineBasis.NO_RECORDED_MUTUAL_CONTRADICTION


# =====================================================================
# PIN 3 - VALID BY CONSTRUCTION: UNCOMMITTABLE CANDIDATES UNWRITABLE
# =====================================================================

def test_an_uncommittable_candidate_is_unwritable(tmp_path) -> None:
    """PIN 3. The commitment door's constructors run at candidate time: a
    raw-dict criterion, an invented surface, and an unruled form each refuse
    at the exact layer that would otherwise store hope."""
    good = OperationalCriterion(surface="world_proposition_standing",
                                record_id="WMP-0001",
                                confirmed_state="supported",
                                failed_state="undercut")
    dependency = TypedDependency(kind=DependencyKind.SCOPE,
                                 record_form="suspension", record_id="BS-1")
    with pytest.raises(ValueError):
        OperationalCriterion(surface="vibes_alignment", record_id="WMP-0001",
                             confirmed_state="good", failed_state="bad")
    with pytest.raises(TypeError):
        CandidatePrediction(
            suspension_id="BS-1", claim_a="CLM-0001", claim_b="CLM-0002",
            proposition_a="WMP-0001", proposition_b="WMP-0002",
            statement="s", criterion=good.as_dict(),   # a RAW DICT
            typed_dependencies=(dependency,),
            license=DraftedLicense(
                basis=CandidateLicenseBasis.NO_DERIVABLE_LICENSE))
    with pytest.raises(TypeError):
        CandidatePrediction(
            suspension_id="BS-1", claim_a="CLM-0001", claim_b="CLM-0002",
            proposition_a="WMP-0001", proposition_b="WMP-0002",
            statement="s", criterion=good,
            typed_dependencies=(dependency.as_dict(),),   # a RAW DICT
            license=DraftedLicense(
                basis=CandidateLicenseBasis.NO_DERIVABLE_LICENSE))
    log = PredictionActLog(log_path=str(tmp_path / "pra.jsonl"))
    with pytest.raises(TypeError):
        log.record_candidate({"anything": "raw"})


# =====================================================================
# PIN 4 + PIN 6 - THE BRIDGE, GOVERNED
# =====================================================================

def test_a_candidate_commits_verbatim_through_the_m9a_door(tmp_path) -> None:
    """PIN 4. The commitment's exposure equals the candidate's draft, the
    candidate act is cited, and the whole thing re-reads off the file."""
    world = _World(tmp_path)
    world.derive()
    [act] = [a for a in world.loop.prediction_acts.acts()
             if a["kind_of_record"] == "prediction_candidate_act"]
    committed = world.loop.commit_candidate(act["act_id"])

    reread = PredictionLedger(
        ledger_path=str(world.predictions.ledger_path),
        goal_ledger=world.goals).commitment_for(committed.prediction_id)
    assert reread == committed
    draft = act["candidate"]
    assert reread.expected_result == draft["statement"]
    assert list(reread.claim_refs) == draft["claim_refs"]
    assert [c.as_dict() for c in reread.operational_criteria] == [
        draft["criterion"]]
    assert [d.as_dict() for d in reread.typed_dependencies] == \
        draft["typed_dependencies"]
    assert reread.licensing_goal.state is FieldState.PROVIDED
    assert reread.licensing_goal.value == world.goal.goal_id
    assert reread.derived_from == act["act_id"]
    assert reread.is_operational() is True


def test_the_bridge_refuses_missing_and_declined_candidates(tmp_path) -> None:
    """PIN 4's refusal half + section 2: nothing commits that was not a
    recorded candidate."""
    world = _World(tmp_path)
    world.sphere.suspend("no claim behind this", 0.9)   # will DECLINE
    world.derive()
    with pytest.raises(ValueError):
        world.loop.commit_candidate("PRA-7777")
    [declined_act] = [a for a in world.loop.prediction_acts.acts()
                      if a["kind_of_record"]
                      == "prediction_candidate_declined_act"]
    with pytest.raises(ValueError):
        world.loop.commit_candidate(declined_act["act_id"])


def test_license_honesty_both_ways_and_the_bridge_never_softens(tmp_path) -> None:
    """PIN 6. A license-less candidate is still a candidate; its commitment
    refuses without a supplied goal and succeeds with one, through the M9-a
    door's own validation."""
    world = _World(tmp_path, with_goal=False)
    world.derive()
    [act] = [a for a in world.loop.prediction_acts.acts()
             if a["kind_of_record"] == "prediction_candidate_act"]
    assert act["candidate"]["license"] == {
        "basis": CandidateLicenseBasis.NO_DERIVABLE_LICENSE.value,
        "goal_id": None, "via_claim": None}

    with pytest.raises(ValueError):
        world.loop.commit_candidate(act["act_id"])          # no license at all
    with pytest.raises(ValueError):
        world.loop.commit_candidate(act["act_id"],          # unresolvable goal
                                    licensing_goal="GLC-0042")
    assert world.predictions.commitments() == ()

    supplied = world.goals.commit(
        desired_state="the committer supplies the license",
        kind=GoalKind.VERIFICATION, level=GoalLevel.PROJECT,
        provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="m9c-pins")
    committed = world.loop.commit_candidate(act["act_id"],
                                            licensing_goal=supplied.goal_id)
    assert committed.licensing_goal.value == supplied.goal_id
    assert committed.derived_from == act["act_id"]


# =====================================================================
# PIN 5 - NO AUTO-COMMIT, STRUCTURALLY
# =====================================================================

def test_the_generator_has_no_path_to_any_write() -> None:
    """PIN 5. Import absence and call absence: no ledger class, no `commit`,
    no `admit`, no `record`, no `resolve`, no `open` anywhere in the module."""
    tree = ast.parse(GENERATOR_MODULE.read_text(encoding="utf-8"))
    src_imports = set()
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").startswith("src"):
                src_imports.add(node.module)
            imported_names.update(a.name for a in node.names)
    assert src_imports == {"src.external.prediction_ledger"}, src_imports
    assert "PredictionLedger" not in imported_names
    called = {node.func.attr for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)}
    assert called.isdisjoint(
        {"commit", "admit", "record", "resolve", "suspend", "save_to_file"}), (
        called)
    opens = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open"]
    assert opens == []


# =====================================================================
# PIN 7 - THE JOINT, WITNESSED: FINDINGS-ONLY BECOMES LICENSED
# =====================================================================

def test_the_joint_one_bridged_commitment_turns_licensing_on(tmp_path) -> None:
    """PIN 7, THE GROUNDING'S MOVE ONE. One kernel, one M7-c generation
    cycle before the bridge and one after: before, every candidate is a
    DRIFT finding for want of a derivable license; after the bridged
    commitment - which carries `claim_refs` and a licensing goal BY
    CONSTRUCTION - the same cycle derives a LICENSED inquiry through the
    justification-claim join. Both states, one test."""
    world = _World(tmp_path)
    # A pre-existing horizonless commitment with NO claim refs: the
    # findings-only era's own shape.
    world.predictions.commit(expected_result="an unlicensed loose end")

    before = world.loop.generate_inquiries()
    assert before, "the fixture must yield at least one discrepancy"
    assert all(c.partition is CandidatePartition.DRIFT for c in before)
    assert all(c.drift_basis is DriftBasis.NO_DERIVABLE_LICENSE
               for c in before)

    world.derive()
    [act] = [a for a in world.loop.prediction_acts.acts()
             if a["kind_of_record"] == "prediction_candidate_act"]
    bridged = world.loop.commit_candidate(act["act_id"])

    after = world.loop.generate_inquiries()
    licensed = [c for c in after
                if c.partition is CandidatePartition.LICENSED]
    assert licensed, "the joint did not close - licensing stayed off"
    assert any(bridged.prediction_id in c.source_record_ids
               for c in licensed)
    assert all(c.license_basis is LicenseBasis.JUSTIFICATION_CLAIM
               for c in licensed)
    assert all(c.ancestor_goal_id == world.goal.goal_id for c in licensed)


# =====================================================================
# PIN 8 - THE ACT SURFACE, HOUSE SHAPE ON THE PRA- STREAM
# =====================================================================

def test_candidate_acts_ride_the_chained_audited_pra_stream(tmp_path) -> None:
    """PIN 8. Candidate and declined acts share the PRA- ordinal stream,
    chain from genesis, audit clean under the frozen schema, and tampering
    reads CHAIN_BREAK."""
    world = _World(tmp_path)
    world.sphere.suspend("no claim behind this", 0.9)
    world.derive()
    log = world.loop.prediction_acts
    acts = log.acts()
    assert [a["kind_of_record"] for a in acts] == [
        "prediction_candidate_act", "prediction_candidate_declined_act"]
    assert [a["act_id"] for a in acts] == ["PRA-0001", "PRA-0002"]
    assert all(a["prediction_id"] is None for a in acts), (
        "no prediction exists at derivation time; the honest value is None")
    report = audit_act_log(log.log_path, PREDICTION_ACT_LOG_SCHEMA)
    assert report.clean, [f.detail for f in report.findings]

    raw = Path(log.log_path).read_bytes()
    Path(log.log_path).write_bytes(
        raw.replace(b"prediction_candidate_act",
                    b"prediction_candidate_ACT", 1))
    tampered = audit_act_log(log.log_path, PREDICTION_ACT_LOG_SCHEMA)
    assert any(f.kind is FindingKind.CHAIN_BREAK for f in tampered.findings)


# =====================================================================
# PIN 10 - PURITY, REGISTRATION, AND THE TWO MIRRORS
# =====================================================================

def test_registration_is_data_and_the_identity_holds() -> None:
    assert REGISTRATION["identity"] == GENERATOR_NAME
    assert REGISTRATION["version"] == GENERATOR_VERSION
    assert REGISTRATION["kind"] == "deterministic_non_model_instrument"
    assert REGISTRATION["declared_invariants"]
    with pytest.raises(TypeError):
        REGISTRATION["identity"] = "impostor"


def test_the_license_vocabulary_mirrors_m7c_exactly() -> None:
    """The mirror drift pin (the standing profile's boundary rule)."""
    assert (CandidateLicenseBasis.JUSTIFICATION_CLAIM.value
            == LicenseBasis.JUSTIFICATION_CLAIM.value)
    assert (CandidateLicenseBasis.NO_DERIVABLE_LICENSE.value
            == DriftBasis.NO_DERIVABLE_LICENSE.value)


def test_the_mutual_rule_mirror_equals_the_ruled_surface(tmp_path) -> None:
    """The second mirror drift pin: the generator's pair derivation and the
    M6 surface's MUTUAL detection agree over the same summaries - a mixed
    world with a mutual pair, a one-way citation, and an isolated record."""
    world = _World(tmp_path)
    extra = PropositionLedger(ledger_path=str(world.prop_path),
                              ancestry_ledger=world.ancestry)
    lonely = extra.record(PropositionKind.STATE, "isolated").wmp_id
    one_way_target = extra.record(PropositionKind.STATE, "cited once").wmp_id
    lines = [json.loads(l) for l in
             world.prop_path.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if line["wmp_id"] == lonely:
            line["contradicted_by"] = [
                {"kind": "claim", "record_id": one_way_target}]
    world.prop_path.write_text(
        "".join(json.dumps(l) + "\n" for l in lines), encoding="utf-8")
    summaries = PropositionLedger(
        ledger_path=str(world.prop_path),
        ancestry_ledger=world.ancestry).live_summaries()

    ruled = {tuple(sorted(f.involved))
             for f in detect_inconsistencies(summaries)
             if f.kind is InconsistencyKind.MUTUAL_CONTRADICTION}
    mirrored_map = CandidateGenerator._mutual_pairs(
        {str(s.wmp_id): s for s in summaries})
    mirrored = {tuple(sorted((a, b)))
                for a, partners in mirrored_map.items() for b in partners}
    assert mirrored == ruled == {tuple(sorted((world.prop_a, world.prop_b)))}


def test_derived_from_is_era_honest(tmp_path) -> None:
    """A directly-authored commitment carries an empty acquisition trail, and
    a legacy-shaped line without the key loads the same way."""
    world = _World(tmp_path)
    direct = world.predictions.commit(expected_result="authored directly")
    assert direct.derived_from == ""
    payload = direct.as_dict()
    del payload["derived_from"]
    payload["prediction_id"] = "PRD-7777"
    path = tmp_path / "legacy.jsonl"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    loaded = PredictionLedger(ledger_path=str(path)).commitment_for("PRD-7777")
    assert loaded is not None and loaded.derived_from == ""
