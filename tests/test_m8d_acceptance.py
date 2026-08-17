"""M8-d: ACCEPTANCE TEST 7, BY EXERCISED CHALLENGE. M8's exit gate.

THE ACCEPTANCE TEST, QUOTED VERBATIM from `AUREA_PIVOT_ARCHITECTURE.md`
**LINE 240** (the handoff cited 236 and told me to re-verify; 236 is Test 3, and
this is what line 240 actually says):

    7. An attention or escalation decision challenged after the fact is fully
       reconstructible: what was considered, under which policy version, from
       which assembled context — and a pressure-selection decision is
       challenged and adjudicated under L12.

THE PIN LIST, MAPPED TO THAT SENTENCE'S CLAUSES:

    "an attention OR escalation      -> pins 2, 3 (both halves rebuilt from
     decision ... fully                  records alone, in a cold scope)
     reconstructible"
    "what was considered"            -> pin 3a (the full candidate census, with
                                        every non-selection's outranking key)
    "under which policy version"     -> pin 3b (policy identity ON the record)
    "from which assembled context"   -> pin 3c (the consulted record ids and
                                        surfaces, embedded)
    "challenged after the fact ...   -> pins 4-8 (the exercised challenge, both
     and adjudicated"                   verdicts, and the refusal)

**THE SECOND CLAUSE IS NOT COVERED BY THIS SLICE, AND THAT IS REPORTED RATHER
THAN GLOSSED.** "a pressure-selection decision is challenged and adjudicated
under L12" names a DIFFERENT subject: `ShapingActKind.PRESSURE_SELECTION` on the
episode record, adjudicated under L12's qualifying-pressure law. This slice's
specification (§1) scopes the challenge surface to ATTENTION and ESCALATION
decisions - `SEL-` and `RTE-` records - and the adjudicator's whole method is
re-derivation of the two pure policies, which have no pressure-selection
counterpart to rerun. So Test 7's first clause is exercised here and its second
is DECLARED OPEN. Claiming Test 7 whole on this pass would be the completeness
defect this file's own §4 records four instances of.
"""

import ast
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

import pytest

from src.doctrine.codex import Codex
from src.executive.act_log_audit import (ADJUDICATION_LOG_SCHEMA,
                                         CHALLENGE_LOG_SCHEMA, FindingKind,
                                         ROUTING_LOG_SCHEMA, audit_act_log)
from src.executive.attention_policy import AttentionPolicy
from src.executive.challenge_log import (AdjudicationLog, AdjudicationVerdict,
                                         ChallengeLog, DefectClass,
                                         UnchallengeableRecord, adjudicate,
                                         file_challenge)
from src.executive.derived_view import (ChairState, DerivedView, RungSubstrate,
                                        _consumed_verdicts,
                                        build_stake_substrate)
from src.executive.escalation_policy import (DELEGATED_COGNITION_ROLE,
                                             EscalationPolicy)
from src.executive.loop import ConsumedVerdict
from src.executive.routing_log import RoutingLog
from src.executive.selection_log import SelectionLog
from src.executive.stake_classifier import StakeClassifier
from src.external.acquisition_ledger import AcquisitionChannel, AcquisitionLedger

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"

TEST_7_FIRST_CLAUSE = (
    "An attention or escalation decision challenged after the fact is fully "
    "reconstructible: what was considered, under which policy version, from "
    "which assembled context")
HEADING = REPO.parent / "Aurea Build" / "AUREA_PIVOT_ARCHITECTURE.md"

THE_VERDICT = ConsumedVerdict(
    role_id=DELEGATED_COGNITION_ROLE, verdict="REFUSED",
    foundry_commit="c1930d6",
    record_path="references/m5-gamma-4-qualification-record.md",
    protocol_sha256s=("1dbdcefb",), failed_surfaces=("Q1",),
    unestablished_surfaces=("Q2",))


# ---------------------------------------------------------------------------
# THE WORLD -- real records, real decisions, through real doors.
# ---------------------------------------------------------------------------

def _paths(root):
    return {name: str(root / f"{name}.jsonl") for name in
            ("acq", "rte", "sel", "chl", "adj")}


def _rebuild_view(root):
    """A view from DISK PATHS ALONE. The cold-scope reconstruction.

    Constructed fresh on every call, from paths - never from an object anyone
    held. This is the callable the adjudicator reruns the policies against, and
    it is deliberately the ONLY way it can reach any record.
    """
    p = _paths(root)
    acquisitions = AcquisitionLedger(ledger_path=p["acq"])
    codex = Codex(filepath=str(root / "doctrines.json"))
    return DerivedView(
        open_obligations=(), unresolved_predictions=(), committed_goals=(),
        chair=ChairState.UNREGISTERED, verdict_acquisition_id=None,
        candidates=(), stake=build_stake_substrate(codex=codex),
        rungs=RungSubstrate(consumed_verdicts=_consumed_verdicts(acquisitions)))


@pytest.fixture()
def world(tmp_path):
    shutil.copy(Codex.SEED_PATH, tmp_path / "doctrines.json")
    p = _paths(tmp_path)
    acquisitions = AcquisitionLedger(ledger_path=p["acq"])
    acquisitions.record(THE_VERDICT.payload(),
                        channel=AcquisitionChannel.USER_INPUT)

    view = _rebuild_view(tmp_path)
    stake = StakeClassifier().classify("doctrine", "Doctrine-0.1", view)
    decision = EscalationPolicy().route(stake, view)
    routings = RoutingLog(log_path=p["rte"])
    routing = routings.record(decision, target_kind="doctrine",
                              target_id="Doctrine-0.1")
    # A SECOND routing, deliberately: a forward chain protects a record through
    # its SUCCESSOR, so a one-line log is the declared final-line limitation
    # (pinned in the integrity pass) rather than a test of the mechanism.
    routings.record(decision, target_kind="doctrine", target_id="Doctrine-3")

    selections = SelectionLog(log_path=p["sel"])
    selection = selections.record(AttentionPolicy().select(view),
                                  "attention-policy.v1", "1")

    return {"root": tmp_path, "routings": routings, "selections": selections,
            "challenges": ChallengeLog(log_path=p["chl"]),
            "adjudications": AdjudicationLog(log_path=p["adj"]),
            "routing_id": routing.routing_id,
            "selection_id": selection.selection_id}


def _arm(world, name):
    """A PRIVATE COPY of the world - the tamper arm never touches the live one."""
    dest = world["root"].parent / f"arm_{name}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(world["root"], dest)
    return dest


def _adjudicate(world, challenge_id, root=None, routings=None):
    root = root or world["root"]
    return adjudicate(
        challenge_id, challenges=world["challenges"],
        adjudications=world["adjudications"],
        rebuild_view=lambda: _rebuild_view(root),
        routings=routings or world["routings"],
        selections=world["selections"])


# ===========================================================================
# PIN 1 - WHOSE ACCEPTANCE THIS IS
# ===========================================================================

def test_1_the_acceptance_sentence_is_quoted_verbatim():
    assert TEST_7_FIRST_CLAUSE in __doc__.replace("\n       ", " ").replace(
        "\n     ", " ")


@pytest.mark.skipif(not HEADING.exists(),
                    reason="the heading lives outside this repo "
                           "(CLAUDE.md §1: proceed and report, never halt)")
def test_1b_the_quoted_clause_still_matches_the_heading_on_disk():
    """**THE HANDOFF CITED LINE 236 AND THIS IS WHY IT SAID TO RE-VERIFY.**
    Line 236 is Test 3 (doctrine standing); Test 7 is at line 240."""
    lines = HEADING.read_text(encoding="utf-8").splitlines()
    assert TEST_7_FIRST_CLAUSE in lines[239]
    assert lines[239].startswith("7.")
    assert "pressure-selection" in lines[239]      # the clause declared open


# ===========================================================================
# PIN 2 - BOTH HALVES REBUILT FROM RECORDS ALONE
# ===========================================================================

def test_2_the_escalation_half_reconstructs_from_records_alone(world):
    written = world["routings"].routings()[0]
    assert written["routing_id"] == world["routing_id"]
    # Rebuilt in a scope holding nothing but paths.
    view = _rebuild_view(world["root"])
    stake = StakeClassifier().classify(written["target_kind"],
                                       written["target_id"], view)
    assert EscalationPolicy().route(stake, view).as_dict() == written["routing"]


def test_2b_the_attention_half_reconstructs_from_records_alone(world):
    written = world["selections"].selections()[0]
    view = _rebuild_view(world["root"])
    selection = AttentionPolicy().select(view)
    assert selection.outcome.value == written["outcome"]
    assert [c.as_dict() for c in selection.census] == written["candidate_census"]


# ===========================================================================
# PIN 3 - THE CHALLENGE-SHAPED QUESTIONS, ANSWERED BY CONSTRUCTION
# ===========================================================================

def test_3a_why_this_and_not_that(world):
    """"What was considered" - the census, with every non-selection's key."""
    routing = world["routings"].routings()[0]
    census = routing["routing"]["stake_derivation"]["conditions"]
    assert len(census) == 4                       # every condition evaluated
    held = [c for c in census if c["held"]]
    assert held and all(c["consulted_record_ids"] for c in held)
    # The rung census says what each rung answered, not merely where it landed.
    rungs = routing["routing"]["rung_census"]
    assert len(rungs) == 2 and all(r["basis"] for r in rungs)


def test_3b_under_what_law(world):
    """"Under which policy version" - the identity is ON the record."""
    routing = world["routings"].routings()[0]
    assert routing["routing"]["policy_name"] == "escalation-policy.v1"
    assert routing["routing"]["policy_version"] == "1"
    selection = world["selections"].selections()[0]
    assert selection["policy_name"] == "attention-policy.v1"
    assert selection["policy_version"] == "1"


def test_3c_on_what_evidence(world):
    """"From which assembled context" - the consulted records, embedded."""
    derivation = world["routings"].routings()[0]["routing"]["stake_derivation"]
    surfaces = {s for c in derivation["conditions"] for s in c["consulted_surfaces"]}
    assert "codex" in surfaces
    ids = {i for c in derivation["conditions"] for i in c["consulted_record_ids"]}
    assert "Doctrine-0.1" in ids


# ===========================================================================
# PIN 4 - DETERMINISM OF ADJUDICATION
# ===========================================================================

def test_4_the_same_challenge_adjudicates_the_same_way_twice(world):
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "the minimum was misapplied", "reviewer",
                           log=world["challenges"], routings=world["routings"])
    first = _adjudicate(world, filed.challenge_id)
    second = _adjudicate(world, filed.challenge_id)
    assert first.verdict is second.verdict
    assert first.divergences == second.divergences
    assert first.legs_run == second.legs_run


# ===========================================================================
# PIN 5 - UPHELD ON A REAL UNMUTATED DECISION
# ===========================================================================

def test_5_a_challenge_against_a_sound_decision_is_UPHELD(world):
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "I say the ruled minimum was misapplied", "reviewer",
                           log=world["challenges"], routings=world["routings"])
    result = _adjudicate(world, filed.challenge_id)
    assert result.verdict is AdjudicationVerdict.UPHELD
    assert result.divergences == ()          # the emptiness IS the verdict
    assert result.legs_run == ("stake_reclassification", "rung_census",
                               "mapping_application")


def test_5b_the_attention_half_is_adjudicable_too(world):
    filed = file_challenge(world["selection_id"], DefectClass.CENSUS_DEFECT,
                           "a candidate was omitted", "reviewer",
                           log=world["challenges"], selections=world["selections"])
    result = _adjudicate(world, filed.challenge_id)
    assert result.verdict is AdjudicationVerdict.UPHELD
    assert result.legs_run == ("candidate_census", "ladder_application")


# ===========================================================================
# PIN 6 - DEFECT_SUSTAINED, AND TWO INSTRUMENTS ON ONE TRUTH
# ===========================================================================

def test_6_a_tampered_routing_sustains_the_defect_AND_breaks_the_chain(world):
    """**TWO INSTRUMENTS, ONE TRUTH.** The same tampered bytes make the
    integrity instrument report CHAIN_BREAK and the adjudicator report
    DEFECT_SUSTAINED with the field named. Neither knows about the other.

    The defect is built through a REAL tamper path in a PRIVATE COPY - never by
    weakening the decision code to make it wrong, which would prove nothing
    about the records.
    """
    arm = _arm(world, "tamper")
    path = arm / "rte.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    # Forge away the debt - the edit this record most attracts.
    record["routing"]["shortfall"] = None
    record["routing"]["adequate"] = True
    lines[0] = json.dumps(record)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # INSTRUMENT ONE: the chain.
    report = audit_act_log(path, ROUTING_LOG_SCHEMA)
    assert FindingKind.CHAIN_BREAK in {f.kind for f in report.findings}

    # INSTRUMENT TWO: the adjudicator, re-deriving.
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "the shortfall is missing", "reviewer",
                           log=world["challenges"], routings=world["routings"])
    result = _adjudicate(world, filed.challenge_id, root=arm,
                         routings=RoutingLog(log_path=str(path)))
    assert result.verdict is AdjudicationVerdict.DEFECT_SUSTAINED
    fields = {d[0] for d in result.divergences}
    assert "shortfall" in fields and "adequate" in fields
    # THE DIVERGENCE NAMES THE FIELD, not merely that two objects differ.
    for name, recorded, rederived in result.divergences:
        assert recorded != rederived


def test_6b_the_live_world_is_byte_untouched_by_the_tamper_arm(world):
    before = (world["root"] / "rte.jsonl").read_bytes()
    arm = _arm(world, "isolation")
    (arm / "rte.jsonl").write_text("{ corrupted\n", encoding="utf-8")
    assert (world["root"] / "rte.jsonl").read_bytes() == before
    result = audit_act_log(world["root"] / "rte.jsonl", ROUTING_LOG_SCHEMA)
    assert result.clean


# ===========================================================================
# PIN 7 - REFUSED IS NOT VINDICATION
# ===========================================================================

def test_7_an_unresolvable_record_is_REFUSED_never_upheld(world):
    filed = file_challenge(world["routing_id"], DefectClass.BASIS_DEFECT,
                           "the basis is contradicted", "reviewer",
                           log=world["challenges"], routings=world["routings"])

    class _Empty:
        def routings(self):
            return ()

    result = _adjudicate(world, filed.challenge_id, routings=_Empty())
    assert result.verdict is AdjudicationVerdict.REFUSED_UNADJUDICABLE
    assert result.verdict is not AdjudicationVerdict.UPHELD
    assert "NOT VINDICATION" in result.refusal_reason
    assert result.divergences == ()


def test_7b_a_challenge_at_the_door_refuses_a_nonexistent_record(world):
    with pytest.raises(UnchallengeableRecord):
        file_challenge("RTE-9999", DefectClass.MAPPING_DEFECT, "x", "reviewer",
                       log=world["challenges"], routings=world["routings"])
    assert world["challenges"].challenges() == ()


def test_7c_an_unruled_defect_class_is_refused(world):
    with pytest.raises(UnchallengeableRecord):
        file_challenge(world["routing_id"], "vibes_defect", "x", "reviewer",
                       log=world["challenges"], routings=world["routings"])
    assert world["challenges"].challenges() == ()


def test_7d_the_defect_vocabulary_is_closed_at_four():
    assert [m.value for m in DefectClass] == [
        "census_defect", "derivation_defect", "mapping_defect", "basis_defect"]
    with pytest.raises(ValueError):
        DefectClass("something_else")


# ===========================================================================
# PIN 8 - GATE-1 REFERENTS ARE REAL ON ADJUDICATIONS
# ===========================================================================

def test_8_the_gate_one_referents_are_real(world):
    filed = file_challenge(world["routing_id"], DefectClass.DERIVATION_DEFECT,
                           "the stake was mis-derived", "reviewer",
                           log=world["challenges"], routings=world["routings"])
    _adjudicate(world, filed.challenge_id)
    gate = world["adjudications"].adjudications()[0]["gate_one"]
    # THE PRESSURE APPLIED IS THE DEFECT CLASS PRESSED.
    assert gate["pressure_class_applied"] == "derivation_defect"
    # THE DEFEATERS NAMED ARE THE LEGS THE RE-DERIVATION RAN.
    assert gate["unexercised_defeaters"] == ["stake_reclassification",
                                             "rung_census", "mapping_application"]
    assert gate["rejection_reason"] == "not_applicable"
    # ...and on a REFUSAL the reason is real rather than not-applicable.
    class _Empty:
        def routings(self):
            return ()
    second = file_challenge(world["routing_id"], DefectClass.BASIS_DEFECT,
                            "y", "reviewer", log=world["challenges"],
                            routings=world["routings"])
    _adjudicate(world, second.challenge_id, routings=_Empty())
    refused = world["adjudications"].adjudications()[1]["gate_one"]
    assert refused["rejection_reason"] != "not_applicable"


# ===========================================================================
# PIN 9 - NOTHING READS ADJUDICATIONS BACK
# ===========================================================================

def test_9_no_src_module_imports_the_challenge_surface():
    consumers = []
    for path in SRC.rglob("*.py"):
        if path.name == "challenge_log.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module \
                    and "challenge_log" in node.module:
                consumers.append(path.relative_to(REPO).as_posix())
    assert consumers == [], consumers


def test_9b_adjudication_changes_nothing_downstream(world):
    """**A DEFECT_SUSTAINED IS A RECORD, NOT A ROLLBACK.**"""
    before = (world["root"] / "rte.jsonl").read_bytes()
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "x", "reviewer", log=world["challenges"],
                           routings=world["routings"])
    _adjudicate(world, filed.challenge_id)
    # The challenged decision stands exactly as it stood.
    assert (world["root"] / "rte.jsonl").read_bytes() == before
    # ...and the re-derivation is unchanged by having been challenged.
    view = _rebuild_view(world["root"])
    stake = StakeClassifier().classify("doctrine", "Doctrine-0.1", view)
    assert EscalationPolicy().route(stake, view).as_dict() == \
        world["routings"].routings()[0]["routing"]


def test_9c_the_policies_name_nothing_about_challenges():
    for name in ("attention_policy.py", "escalation_policy.py",
                 "stake_classifier.py", "derived_view.py", "loop.py"):
        # AST, NOT SUBSTRING - the tenth recorded occurrence of that defect in
        # this tree. `escalation_policy`'s docstring legitimately says "nothing
        # here adjudicates between them" while explaining the rung census, and
        # deleting correct documentation to satisfy a noisy guard is how a
        # guard earns its eventual weakening (Ruling 63's precedent).
        tree = ast.parse((SRC / "executive" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                assert "challenge_log" not in module, name
                assert not any("challenge_log" in a.name
                               for a in node.names), name
            if isinstance(node, ast.Name):
                assert "adjudicat" not in node.id.lower(), name
            if isinstance(node, ast.Attribute):
                assert "adjudicat" not in node.attr.lower(), name


# ===========================================================================
# PIN 10 - PRIOR PINS, AND THE NEW LOGS
# ===========================================================================

_FROZEN = {
    "tests/test_m7a_executive_loop.py":
        "c7867cd28cf7d76d64683024a2c86335ec0f27bc3676e9467ef615523adc58fe",
    "tests/test_m7b_attention_policy.py":
        "5ea92b1f5ef9c278499151705ad2fc1180522665fda9b0e5f0c07544ad8bf700",
    "tests/test_m7c_inquiry.py":
        "6029d504c25fe4d2b1717339f1a74e34bce04d11460a08c587424efcd8227aa6",
    "tests/test_m7d_acceptance.py":
        "d3ab01833edb5748671bde1a4f8e75fc318d663421ca12afd4e41945cf4073f0",
    "tests/test_m8a_stake_classifier.py":
        "01dd8bdbc7a3ccf9070a56e6fc43163c61ce1b7e7068e12dea584798bb3ae055",
    "tests/test_act_log_integrity.py":
        "f663fd29114848860aa1bb4472d5d7f0ef0a68d48cc53679c44ea2418ff9caa9",
    "tests/test_m8b_escalation.py":
        "dbabe9e752c83e83444fd74f2656588ad0773ce0d6c2d33a392d3bf621bcc8a4",
    "tests/test_m8c_utility.py":
        "215f2ad19615793a9bf1927c62b70b5db2e2127b87134d59670c19998eecd983",
}


def test_10_all_prior_executive_pin_files_are_byte_unmodified():
    for path, expected in _FROZEN.items():
        actual = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
        assert actual == expected, path


def test_10b_the_kill_and_reconstruction_pins_still_pass():
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest",
         "tests/test_m7d_acceptance.py", "-q"],
        cwd=str(REPO), capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout[-3000:]


def test_10c_both_new_logs_chain_from_genesis_and_audit_clean(world):
    from src.executive.act_chain import CHAIN_KEY, genesis_chain
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "x", "reviewer", log=world["challenges"],
                           routings=world["routings"])
    _adjudicate(world, filed.challenge_id)
    for name, schema in (("chl", CHALLENGE_LOG_SCHEMA),
                         ("adj", ADJUDICATION_LOG_SCHEMA)):
        path = world["root"] / f"{name}.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert json.loads(lines[0])[CHAIN_KEY] == genesis_chain()
        report = audit_act_log(path, schema)
        assert report.clean, (name, report.as_dict())
        assert report.pre_chain_lines == 0


def test_10e_an_underived_mint_refuses_on_both_logs(world, monkeypatch):
    """RULING 53'S SENTINEL - **found by a surviving mutant.** Nothing
    exercised the underived floor on either new log, so a fallback to
    `CHL-0001` / `ADJ-0001` survived the whole file. That is the reissue
    hazard: an id that already names a different dispute, in an append-only
    record where nothing can afterwards tell the two apart."""
    from src.executive.challenge_log import (AdjudicationLogUnreadable,
                                             ChallengeLogUnreadable)
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "x", "reviewer", log=world["challenges"],
                           routings=world["routings"])
    monkeypatch.setattr("src.executive.challenge_log.derive_max_ordinal",
                        lambda *a, **k: None)
    with pytest.raises(ChallengeLogUnreadable):
        file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT, "y",
                       "reviewer", log=world["challenges"],
                       routings=world["routings"])
    with pytest.raises(AdjudicationLogUnreadable):
        _adjudicate(world, filed.challenge_id)
    assert len(world["challenges"].challenges()) == 1
    assert world["adjudications"].adjudications() == ()


def test_10d_a_write_failure_gates_the_adjudication(world, monkeypatch):
    filed = file_challenge(world["routing_id"], DefectClass.MAPPING_DEFECT,
                           "x", "reviewer", log=world["challenges"],
                           routings=world["routings"])
    monkeypatch.setattr("src.executive.challenge_log.durable_append_text",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("gone")))
    with pytest.raises(OSError):
        _adjudicate(world, filed.challenge_id)
    assert world["adjudications"].entries == []
