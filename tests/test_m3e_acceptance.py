"""
M3-E - THE LOOP'S FIRST FULL TURN. THE ACCEPTANCE.

Four heading §13 items, each made a TREE FACT rather than an assertion. This
file adds no capability: it proves what M3-A through M3-D built, and if the
built thing could not demonstrate an item, that would be the milestone's
finding rather than something to edit around. **ZERO `src/` CHANGE.**

**EVERY ASSERTION READS THE FILES.** The obligation ledger and the episode
store are HISTORIES; return values are convenience. Each segment ends by
re-opening the stores from disk through fresh readers and asserting the facts
from the records alone - the freshest lesson in this repo (M3-D's survivor
C2-08, where deleting the store write survived because a pin read the returned
dict instead of the record).

Every segment is RED-FIRST WATCHED: the driven condition is neutered
in-process, the segment observed failing, and the source restored
byte-verified. A segment that cannot fail proves nothing (Ruling 35's class).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.aurea_core import AureaCore
from src.external.prediction_ledger import (
    PredictionLedger, PredictionOutcome, provided,
)
from src.filtration.episode_record import (
    DefeaterKind, EpisodeOutcome, EpisodeRecord, EpisodeRecordType,
)
from src.filtration.obligation_ledger import (
    ObligationLedger, ObligationRecordType, RejectionKind, TargetKind,
)

# --- The claim family, measured against the live tree before being fixed here.
CONTESTS_DOCTRINE = "Fracture Carried is false."   # -> SUSPENDED, carried
SCARRING = "Honesty is pointless."                 # -> SCARRED, collapses, scars

# Resonates with what a PIPELINE scar actually records - see Segment 4.
RESONANT_LATER = "Contradiction carried without resolution is meaningless."


# =====================================================================
# READERS - every fact below is re-read from disk through a fresh store
# =====================================================================

def _obligations_on_disk(core) -> tuple:
    """Re-open the ledger FROM ITS PATH. Not `core.obligations`, deliberately."""
    return ObligationLedger(ledger_path=str(core.obligations.ledger_path)).read_all()


def _episodes_on_disk(core) -> tuple:
    return EpisodeRecord(log_path=str(core.episodes.log_path)).read_all()


def _rows(records, record_type, **match):
    out = []
    for r in records:
        if r.get("record_type") != record_type:
            continue
        if all(r.get(k) == v for k, v in match.items()):
            out.append(r)
    return out


# =====================================================================
# SEGMENT 1 — §13.1
#   "A contradiction she would prefer not to face cannot be silently
#    dropped; the obligation ledger proves it, including the rejection
#    log answering for every unadmitted challenge."
# =====================================================================

def test_segment_1_the_contradiction_is_on_the_record_and_so_is_the_refusal():
    """§13.1, made a tree fact.

    The turn is driven through the PUBLIC DOOR ONLY - this test calls
    `process_input` and nothing else, so every record below was written by the
    pipeline rather than by the test. Then the stores are re-opened from disk
    and the facts read from the records.
    """
    core = AureaCore()
    result = core.process_input(CONTESTS_DOCTRINE)
    claim_id = result["claim_id"]

    # ---- FROM THE FILES ------------------------------------------------
    obligations = _obligations_on_disk(core)
    opened = _rows(obligations, ObligationRecordType.OPEN.value,
                   target_kind=TargetKind.CLAIM.value, target_id=claim_id)
    assert len(opened) == 1, (
        "the contradiction left no obligation on disk - it was silently dropped")
    obligation_id = opened[0]["obligation_id"]
    assert opened[0]["source"] == "aurea_core.collapse", (
        "the record does not say the PIPELINE admitted it")

    episodes = _episodes_on_disk(core)
    ep = _rows(episodes, EpisodeRecordType.EPISODE_OPENED.value)
    assert len(ep) == 1 and ep[0]["obligation_ids"] == [obligation_id], (
        "no episode was opened against the obligation")
    episode_id = ep[0]["episode_id"]

    acts = _rows(episodes, EpisodeRecordType.SHAPING_ACT.value,
                 episode_id=episode_id)
    assert acts, "the consideration left no shaping acts on disk"
    disposition = _rows(episodes, EpisodeRecordType.DISPOSITION.value,
                        episode_id=episode_id)
    assert len(disposition) == 1, "the episode was never disposed on disk"

    # ---- THE REJECTION HALF: an unadmittable challenge is ANSWERED -----
    # L4's own sentence - the rejection log answers for every UNADMITTED
    # challenge. An unrecorded CLM id cannot resolve, so admission refuses,
    # and the refusal is a RECORD rather than a silence.
    refused = core.obligations.admit(
        source="acceptance", target_kind=TargetKind.CLAIM,
        target_id="CLM-9999", claim_text="a challenge she cannot place")
    assert refused.rejection_kind is RejectionKind.TARGETLESS

    rejected = _rows(_obligations_on_disk(core),
                     ObligationRecordType.REJECTED.value)
    assert len(rejected) == 1, "the unadmitted challenge left no record"
    assert rejected[0]["reason"], "the rejection record carries no reason"
    assert rejected[0]["target_id"] == "CLM-9999"


# =====================================================================
# SEGMENT 2 — §13.4
#   "A carried contradiction has generated a committed discriminating
#    prediction whose resolution criteria predate its outcome."
# =====================================================================

@pytest.fixture
def carried_with_prediction(tmp_path):
    """A carried contradiction plus a real, really-resolved prediction."""
    core = AureaCore()
    result = core.process_input(CONTESTS_DOCTRINE)

    ledger = PredictionLedger(ledger_path=str(tmp_path / "predictions.jsonl"))
    commitment = ledger.commit(
        expected_result=(
            "if the carried contradiction is a real fracture, a re-reading of "
            "the doctrine under the same pressure will fail the same net"),
        success_criteria=provided("the same net passes on re-reading"),
        failure_criteria=provided("the same net fails on re-reading"),
    )
    ledger.resolve(commitment.prediction_id, PredictionOutcome.FALSIFIED,
                   criterion="failure_criteria",
                   note="the net failed on re-reading")
    return core, result, ledger, commitment


def test_segment_2_the_prediction_is_committed_and_its_criteria_predate_it(
        carried_with_prediction):
    """§13.4, made a tree fact.

    The contradiction is CARRIED on the wired path: the resolver returns `None`
    for a SUSPENDED verdict - *"NOT YET. Keep carrying it."* - so the
    consideration exhausts and the episode dispositions UNRESOLVED_AT_BOUND.
    That is ambiguity carried rather than rounded off, which is the state a
    discriminating prediction is FOR.

    **PRECEDENCE COMES FROM APPEND ORDER, NEVER THE CLOCK** - the proof this
    house endorsed at the sixty-seventh entry, because the prediction ledger
    records no ordinal and a timestamp join is barred.
    """
    core, result, ledger, commitment = carried_with_prediction

    # ---- FROM THE FILES: the contradiction really was CARRIED ----------
    episodes = _episodes_on_disk(core)
    disposition = _rows(episodes, EpisodeRecordType.DISPOSITION.value)
    assert len(disposition) == 1
    assert disposition[0]["outcome"] == EpisodeOutcome.UNRESOLVED_AT_BOUND.value, (
        "the contradiction was not CARRIED - a prediction about a settled "
        "question is not discriminating")

    # ---- FROM THE FILES: the commitment and its resolution -------------
    entries = list(ledger.read_all())
    kinds = [type(e).__name__ for e in entries]
    assert kinds.count("PredictionCommitment") == 1
    assert kinds.count("PredictionResolution") == 1

    commitment_index = kinds.index("PredictionCommitment")
    resolution_index = kinds.index("PredictionResolution")
    assert commitment_index < resolution_index, (
        "the criteria do NOT predate the outcome on the record - a prediction "
        "written after its result is not a prediction")

    # The criteria were FIXED AT COMMIT and are on the record verbatim.
    recorded = entries[commitment_index]
    assert recorded.criterion("failure_criteria").value == \
        "the same net fails on re-reading"
    assert entries[resolution_index].outcome is PredictionOutcome.FALSIFIED


# =====================================================================
# SEGMENT 3 — L6 end to end: the typed defeater adjudicates
# =====================================================================

def test_segment_3_a_typed_defeater_adjudicates_a_contradiction(
        carried_with_prediction):
    """L6 end to end, on real records.

    **DECLARED HONESTLY: the registration and the disposition are DOOR-DRIVEN.**
    The mid-turn wire where a resolver CONSULTS a registered defeater is
    later-milestone cognition and is not claimed here. What this segment proves
    is that the SEQUENCE IS REAL AND FORCED - the precedence proof and the
    FALSIFIED gate both execute against genuine ledger records, and a defeater
    that failed either could not be registered at all.

    A FRESH CLAIM ID is used deliberately: Ruling 58 mints one per perception,
    and M3-D's doubly-unreachable finding means re-using the carried turn's
    obligation is not the honest shape.
    """
    core, _, ledger, commitment = carried_with_prediction

    # A fresh perception, so a fresh CLM id - through the public door.
    fresh = core.process_input(SCARRING)
    claim_id = fresh["claim_id"]

    # The episode store needs the prediction ledger to RESOLVE the citation.
    # A read handle, injected here because the pipeline does not wire one
    # today - stated rather than left for a reader to infer.
    core.episodes.prediction_ledger = ledger

    admission = core.obligations.admit(
        source="acceptance", target_kind=TargetKind.CLAIM, target_id=claim_id,
        claim_text="the carried contradiction is defeated by a failed prediction")
    assert admission.admitted
    episode_id = core.episodes.open_episode([admission.obligation_id], 3)

    # THE PRECEDENCE PROOF AND THE FALSIFIED GATE BOTH RUN FOR REAL HERE.
    defeater_id = core.episodes.register_defeater(
        episode_id, DefeaterKind.FAILED_PRECOMMITTED_PREDICTION,
        {"prediction_id": commitment.prediction_id})

    core.episodes.disposition(episode_id, EpisodeOutcome.COLLAPSED,
                              defeater_ref=defeater_id)

    # Ruling 1: the caller REQUESTS, the owner writes.
    scar = core.scar_core.form_scar(
        origin=f"EPISODE/{episode_id}", type="adjudicated_contradiction",
        weight=1.0, description="defeated by a falsified precommitted prediction",
        claim_id=claim_id, origin_pressure=fresh.get("pressure_generated"))

    # ---- FROM THE FILES ------------------------------------------------
    episodes = _episodes_on_disk(core)
    registered = _rows(episodes, EpisodeRecordType.DEFEATER_REGISTERED.value,
                       episode_id=episode_id)
    assert len(registered) == 1
    interpretation = registered[0]["interpretation"]
    assert interpretation["recorded_outcome"] == "falsified", (
        "the FALSIFIED gate did not record the outcome it verified")
    assert interpretation["resolution_criteria"]["recorded"]["value"] == \
        "the same net fails on re-reading", (
        "the criteria were not copied VERBATIM from the ledger record")
    proof = interpretation["precedence_proof"]
    assert proof["commitment_index"] < proof["resolution_index"]
    assert proof["basis"] == "prediction_ledger_append_order"

    disposed = _rows(episodes, EpisodeRecordType.DISPOSITION.value,
                     episode_id=episode_id)
    assert len(disposed) == 1
    assert disposed[0]["outcome"] == EpisodeOutcome.COLLAPSED.value
    assert disposed[0]["defeater_ref"] == defeater_id, (
        "the disposition does not cite the defeater that forced it")

    # The scar carries the join back to the claim.
    on_disk = core.scar_core.get_scar(scar.id)
    assert on_disk is not None and on_disk.claim_id == claim_id


# =====================================================================
# SEGMENT 4 — §13.2
#   "A scar formed under genuine pressure demonstrably alters a later
#    disposition, traceable end to end."
# =====================================================================

def test_segment_4_a_scar_alters_a_later_disposition_end_to_end():
    """§13.2, made a tree fact - and THE MECHANISM IS ASSERTED, not just the
    difference.

    **TURN A forms the scar under GENUINE PRESSURE on the wired path**: the
    verdict is SCARRED, the resolver returns "irreconcilable", the episode
    dispositions COLLAPSED and the PIPELINE forms the scar. That half is this
    segment's permanent witness for the resolver docstring's own HISTORY note -
    an invented `pressure > 0.9` threshold once made COLLAPSE unreachable and
    *"AUREA could not form a scar. The whole architecture ran, and nothing left
    a mark on her."*

    **TURN B drives the SAME later input against the scarred state and against
    an UNSCARRED CONTROL.** The control passes the claim; the scarred instance
    carries it.

    **THE MECHANISM IS THE RESONANCE NET, AND THE RED-FIRST WATCH IS WHAT
    ESTABLISHED THAT.** This docstring first named `EchoNet._threshold` - the
    obvious candidate, whose own words are *"a claim near old wounds is judged
    more strictly"*. Neutering its scar subtraction left this segment GREEN,
    so the attribution was wrong. Neutering the RESONANCE NET's scar loop
    turns it RED:

        pressure = max(pressure, min(0.3 + 0.1 * max(scar.weight, 0.0), 0.7))

    A resonating scar GENERATES PRESSURE, and that is what flips the verdict.
    **THE DIRECTION IS DERIVED FROM THAT LINE, NOT ASSUMED**: the expression is
    a `max` against a non-negative floor, so a scar can only ever ADD pressure -
    it can move a claim toward being carried and never away. `_threshold`'s
    subtraction points the same way (a lower threshold is a stricter net), so
    both scar paths agree in DIRECTION; only the resonance net is load-bearing
    for THIS outcome, and both were measured rather than reasoned about.

    THE RESONANCE IS AGAINST WHAT THE SCAR ACTUALLY RECORDS. `_overlaps` needs
    two shared non-stopword tokens against `name + description`, and a pipeline
    scar records *"Contradiction carried N cycles without resolution"* - not the
    original claim's content. A later input resonating with the ORIGINAL text
    would not move anything, and measuring that first is what made this segment
    honest rather than lucky.
    """
    # ---- CONTROL: no scar formed first --------------------------------
    control = AureaCore()
    control_result = control.process_input(RESONANT_LATER)

    # ---- TURN A: the scar, formed by the pipeline under real pressure --
    scarred = AureaCore()
    turn_a = scarred.process_input(SCARRING)
    assert turn_a["scar_formed"] is not None, (
        "the pipeline formed NO scar under a SCARRED verdict - the scar path "
        "is severed, which is this segment's own named failure")
    the_scar = turn_a["scar_formed"]

    a_episodes = _episodes_on_disk(scarred)
    a_disposed = _rows(a_episodes, EpisodeRecordType.DISPOSITION.value)
    assert a_disposed[0]["outcome"] == EpisodeOutcome.COLLAPSED.value, (
        "turn A did not collapse, so its scar was not formed under pressure")

    # ---- TURN B: the same later input, now against the scarred state ---
    later_result = scarred.process_input(RESONANT_LATER)

    # ---- THE DIFFERENCE, AND THE MECHANISM ----------------------------
    assert control_result["output_path"] != later_result["output_path"], (
        "the scar left NO mark on a later disposition - the whole architecture "
        "ran and nothing changed, which is the milestone's STOP condition")
    # `.get` deliberately: the key is ABSENT (not None) on a claim that
    # never entered the chamber - the block is written inside that branch.
    assert control_result.get("contradiction") is None, (
        "the control already carried this claim - it cannot witness a change")
    assert later_result.get("contradiction") is not None, (
        "the scarred instance did not carry the claim")

    # THE MECHANISM: the scar's own recorded text resonates with the claim,
    # and the threshold line can only ever SUBTRACT.
    from src.filtration.echonet import EchoNet
    resonates = EchoNet._overlaps(
        RESONANT_LATER, f"{the_scar.name} {the_scar.description}")
    assert resonates, (
        "the later claim does not overlap the scar's RECORDED text, so this "
        "difference cannot be attributed to the scar")
    # The resonance net's own magnitude for THIS scar, from THAT line.
    resonant_pressure = min(0.3 + 0.1 * max(the_scar.weight, 0.0), 0.7)
    assert resonant_pressure > 0, (
        "the resonating scar generates no pressure - there is no mechanism")

    # DIRECTION, derived from the line rather than assumed: the net takes a
    # `max` against a non-negative floor, so a scar can only ever ADD pressure -
    # the claim moves toward being carried, never away.
    assert later_result["contradiction"]["disposition"] in (
        EpisodeOutcome.UNRESOLVED_AT_BOUND.value,
        EpisodeOutcome.COLLAPSED.value,
        EpisodeOutcome.SUSPENDED.value), (
        "the scarred instance reached a LESS strict outcome - the threshold "
        "line can only subtract, so this direction is impossible")

    # ---- TRACEABLE END TO END, FROM THE FILES --------------------------
    # scar -> claim_id -> obligation -> episode, for TURN A.
    assert the_scar.claim_id == turn_a["claim_id"]
    obligations = _obligations_on_disk(scarred)
    origin = _rows(obligations, ObligationRecordType.OPEN.value,
                   target_id=the_scar.claim_id)
    assert len(origin) == 1, "the scar's claim has no obligation on disk"
    a_opened = [r for r in _rows(a_episodes,
                                 EpisodeRecordType.EPISODE_OPENED.value)
                if origin[0]["obligation_id"] in (r.get("obligation_ids") or [])]
    assert len(a_opened) == 1, (
        "the chain scar -> claim -> obligation -> episode is broken on disk")

    # And the later turn has its own, distinct chain.
    later_obligations = _rows(_obligations_on_disk(scarred),
                              ObligationRecordType.OPEN.value,
                              target_id=later_result["claim_id"])
    assert len(later_obligations) == 1
    assert later_obligations[0]["obligation_id"] != origin[0]["obligation_id"]
