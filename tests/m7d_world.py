"""M7-d test support: the populated world, and the fingerprint of a mind.

NOT A TEST MODULE and deliberately not named like one - pytest must not collect
it. It is the CHILD PROGRAM for Acceptance Test 6's executed kill: run as
`python tests/m7d_world.py build <root> <out>` it constructs a world through the
kernel's own doors and EXITS; run as `... fingerprint <root> <out>` it opens a
world cold from disk paths alone and writes down what the Executive derives.

**WHY THIS IS A SEPARATE PROGRAM RATHER THAN A FIXTURE.** The kill has to be
real. A fixture that deleted references and re-constructed objects in the same
interpreter would leave the dead world reachable in principle - module-level
state, caches, the GC's opinion about liveness - and Test 6 would be measuring a
reset. Here the builder is an OS PROCESS that exits: its address space is
reclaimed by the operating system, and the only thing crossing the boundary is
bytes on disk. The parent test never constructs the world at all, so it cannot
smuggle a reference even by accident.

EVERY PATH IS EXPLICIT AND UNDER THE GIVEN ROOT. This program runs OUTSIDE
pytest, so `conftest.py`'s isolation fixture does not reach it. Nothing here may
rely on a default path; `_paths` is the single place they are named, and the
caller asserts the footprint afterwards.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.executive.attention_policy import AttentionPolicy  # noqa: E402
from src.executive.inquiry_log import InquiryLog  # noqa: E402
from src.executive.loop import ConsumedVerdict, ExecutiveLoop  # noqa: E402
from src.executive.selection_log import SelectionLog  # noqa: E402
from src.external.acquisition_ledger import AcquisitionLedger  # noqa: E402
from src.external.prediction_ledger import (PredictionLedger,  # noqa: E402
                                            declared_none, provided)
from src.filtration.obligation_ledger import (ObligationLedger,  # noqa: E402
                                              TargetKind)
from src.goals.goal_ledger import (GoalKind, GoalLedger,  # noqa: E402
                                   GoalLevel, GoalProvenance)

# The claim id both the goal and one prediction will cite - the VIA-CLAIM join.
SHARED_CLAIM = "CLM-0042"


def _paths(root: pathlib.Path) -> dict:
    return {
        "obligations": str(root / "obligations.jsonl"),
        "predictions": str(root / "predictions.jsonl"),
        "goals": str(root / "goals.jsonl"),
        "acquisitions": str(root / "acquisitions.jsonl"),
        "selections": str(root / "selections.jsonl"),
        "inquiries": str(root / "inquiries.jsonl"),
    }


def open_world(root: pathlib.Path) -> ExecutiveLoop:
    """Construct an Executive over a world FROM DISK PATHS ALONE.

    This is the cold-rebuild constructor, and it is the same one `build` uses -
    deliberately. If the rebuild had its own constructor, the test would be
    comparing two code paths rather than one mind across a boundary.
    """
    p = _paths(root)
    predictions = PredictionLedger(ledger_path=p["predictions"])
    return ExecutiveLoop(
        ObligationLedger(ledger_path=p["obligations"],
                         prediction_ledger=predictions),
        predictions,
        GoalLedger(ledger_path=p["goals"]),
        AcquisitionLedger(ledger_path=p["acquisitions"]),
        policy=AttentionPolicy(),
        selections=SelectionLog(log_path=p["selections"]),
        inquiries=InquiryLog(log_path=p["inquiries"]))


def build(root: pathlib.Path) -> dict:
    """Populate a world THROUGH ITS OWN DOORS. Nothing is written by hand.

    Rich enough that every Executive faculty has non-trivial state to lose:
    obligations including a DEFERRED one (so the due-fold has work), predictions
    in all four horizon shapes, goals licensing through BOTH join paths, the
    consumed verdict, a taken attention cycle, and two generation cycles so the
    kernel's own duplicate disposition is on the record.
    """
    root.mkdir(parents=True, exist_ok=True)
    loop = open_world(root)
    obligations, predictions, goals = loop.obligations, loop.predictions, loop.goals

    # (1) PREDICTIONS - all four horizon shapes.
    overdue = predictions.commit("the bridge holds by then",
                                 resolution_horizon=provided("SEQ-000001"))
    future = predictions.commit("settles much later",
                                resolution_horizon=provided("SEQ-999999"))
    bare = predictions.commit("nobody asked for a horizon")
    none_declared = predictions.commit("there is no horizon",
                                       resolution_horizon=declared_none())
    via_claim = predictions.commit("licensed through a shared claim",
                                   claim_refs=(SHARED_CLAIM,))

    # (2) OBLIGATIONS - several standing, one DEFERRED so the due-fold works.
    first = obligations.admit("fixture", TargetKind.DOCTRINE, "Doctrine-0",
                              "the founding doctrine is owed an account")
    second = obligations.admit("fixture", TargetKind.SCAR, "Scar-0",
                               "the origin collapse is owed an account")
    obligations.admit("fixture", TargetKind.CLAIM, SHARED_CLAIM,
                      "this claim is owed an account")
    obligations.defer(first.obligation_id, "waiting on evidence", "SEQ-000900")

    # (3) GOALS - BOTH join paths, committed through the ledger's own API.
    goals.commit(desired_state="keep the overdue prediction honest",
                 kind=GoalKind.RESEARCH, level=GoalLevel.PROJECT,
                 provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="fixture",
                 originating_record_ids=(overdue.prediction_id,
                                         bare.prediction_id))
    goals.commit(desired_state="keep the shared claim honest",
                 kind=GoalKind.VERIFICATION, level=GoalLevel.PROJECT,
                 provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="fixture",
                 justification_claim_ids=(SHARED_CLAIM,))

    # (4) THE CONSUMED VERDICT - the chair learns it is empty from the record.
    loop.register_consumed_verdict(ConsumedVerdict(
        role_id="ROLE-EXECUTIVE-DELEGATED-COGNITION",
        verdict="REFUSED",
        foundry_commit="c1930d6",
        record_path="references/m5-gamma-4-qualification-record.md",
        protocol_sha256s=("1dbdcefb908b1b7341be90e67ad353b4dceef795e9377fe3513"
                          "c1ede2e1874f7",),
        failed_surfaces=("Q1",),
        unestablished_surfaces=("Q2", "Q3")))

    # (5) ONE ATTENTION CYCLE - a selection on the record.
    loop.step()

    # (6) THE FIRST GENERATION CYCLE - licensed admissions and drift findings.
    first_pass = loop.submit_inquiries()

    # (7) A DEPTH-2 SOURCE, BUILT THROUGH THE REAL PATH.
    #
    # **ADDED AFTER A SURVIVING MUTANT.** Without this, the acceptance world
    # exercised no depth accounting at all: deleting the generator's entire
    # depth machinery left every identity pin green, because nothing in the
    # world had a second hop to lose. A faculty with no non-trivial state is a
    # faculty this test was not measuring (§1.A's own requirement).
    #
    # A prediction committed while working one of OUR OWN admitted inquiries,
    # citing that obligation - and licensed, so it would be pursued but for the
    # recursion bar. That is the case where the ceiling has to do real work.
    ours = next(r.obligation_id for r in first_pass
                if r.obligation_id and r.disposition.value == "admitted")
    recursive = predictions.commit("derived while working our own inquiry",
                                   claim_refs=(ours,))
    goals.commit(desired_state="keep the derived prediction honest",
                 kind=GoalKind.RESEARCH, level=GoalLevel.PROJECT,
                 provenance=GoalProvenance.EXTERNAL_PROPOSAL, asserter="fixture",
                 originating_record_ids=(recursive.prediction_id,))

    # (8) THE SECOND GENERATION CYCLE - the KERNEL'S OWN duplicate disposition
    # on the repeats, and the depth-2 candidate refused by the ceiling.
    loop.submit_inquiries()

    return {
        "recursive": recursive.prediction_id,
        "generator_obligation": ours,
        "overdue": overdue.prediction_id, "future": future.prediction_id,
        "bare": bare.prediction_id, "none_declared": none_declared.prediction_id,
        "via_claim": via_claim.prediction_id,
        "deferred_obligation": first.obligation_id,
        "standing_obligation": second.obligation_id,
    }


# ---------------------------------------------------------------------------
# THE FINGERPRINT - what the Executive DERIVES, not what it holds.
# ---------------------------------------------------------------------------
#
# CLOCK-FREE BY CONSTRUCTION. It captures the PURE surfaces - `observe()`,
# `select()`, `generate_inquiries()` - none of which carry a wall-clock field.
# The RECORDED forms do (`recorded_at`), and comparing those would measure the
# clock rather than the mind. This is the same reason M4-γ's replay census is
# clock-free.

def _candidate(c) -> dict:
    return {"category": c.category.value, "record_id": c.record_id,
            "due_ordinal": c.due_ordinal, "horizon_state": c.horizon_state,
            "commitment_ordinal": c.commitment_ordinal}


def _view(view) -> dict:
    inq = view.inquiry
    return {
        "open_obligations": list(view.open_obligations),
        "unresolved_predictions": list(view.unresolved_predictions),
        "committed_goals": list(view.committed_goals),
        "chair": view.chair.value,
        "verdict_acquisition_id": view.verdict_acquisition_id,
        "candidates": [_candidate(c) for c in view.candidates],
        "inquiry_substrate": {
            "predictions": [
                {"prediction_id": p.prediction_id,
                 "horizon_state": p.horizon_state,
                 "horizon_ordinal": p.horizon_ordinal,
                 "claim_refs": list(p.claim_refs)} for p in inq.predictions],
            "goals": [
                {"goal_id": g.goal_id,
                 "originating_record_ids": list(g.originating_record_ids),
                 "justification_claim_ids": list(g.justification_claim_ids)}
                for g in inq.goals],
            "obligations": [
                {"obligation_id": o.obligation_id, "source": o.source,
                 "target_kind": o.target_kind, "target_id": o.target_id}
                for o in inq.obligations],
            "max_seq_ordinal": inq.max_seq_ordinal,
        },
    }


def _selection(sel) -> dict:
    return {
        "outcome": sel.outcome.value,
        "selected_category": (None if sel.selected_category is None
                              else sel.selected_category.value),
        "selected_record_id": sel.selected_record_id,
        "deciding_basis": (None if sel.deciding_basis is None
                           else sel.deciding_basis.value),
        "census": [{"category": c.category.value, "record_id": c.record_id,
                    "ordering_key": list(c.ordering_key),
                    "key_names": list(c.key_names),
                    "outranked_at": (None if c.outranked_at is None
                                     else c.outranked_at.value),
                    "selected": c.selected,
                    "horizon_state": c.horizon_state} for c in sel.census],
    }


def _generation(candidates) -> list:
    return [{"discrepancy_class": c.discrepancy_class.value,
             "source_record_ids": list(c.source_record_ids),
             "partition": c.partition.value,
             "derivation_depth": c.derivation_depth,
             "ancestor_goal_id": c.ancestor_goal_id,
             "license_basis": (None if c.license_basis is None
                               else c.license_basis.value),
             "drift_basis": (None if c.drift_basis is None
                             else c.drift_basis.value),
             "horizon_state": c.horizon_state} for c in candidates]


def fingerprint(root: pathlib.Path) -> dict:
    """Open the world cold and write down what the Executive derives."""
    loop = open_world(root)
    return {"view": _view(loop.observe()),
            "selection": _selection(loop.select()),
            "generation": _generation(loop.generate_inquiries())}


def forward_cycle(root: pathlib.Path) -> dict:
    """One further cycle AFTER a cold rebuild - the forward-continuity probe.

    Returns the ids the rebuilt Executive minted plus the floors it minted them
    over, so the caller can check monotonicity and collision-freedom across the
    process boundary WITHOUT this program deciding anything about them.
    """
    from src.utils.ledger_mint import derive_max_ordinal
    p = _paths(root)
    before = {
        "SEL-": derive_max_ordinal(pathlib.Path(p["selections"]), "SEL-"),
        "INQ-": derive_max_ordinal(pathlib.Path(p["inquiries"]), "INQ-"),
        "OBL-": derive_max_ordinal(pathlib.Path(p["obligations"]), "OBL-"),
        "SEQ-": derive_max_ordinal(pathlib.Path(p["obligations"]), "SEQ-"),
    }
    loop = open_world(root)
    selection = loop.step()
    inquiries = loop.submit_inquiries()
    after = {
        "SEL-": derive_max_ordinal(pathlib.Path(p["selections"]), "SEL-"),
        "INQ-": derive_max_ordinal(pathlib.Path(p["inquiries"]), "INQ-"),
        "OBL-": derive_max_ordinal(pathlib.Path(p["obligations"]), "OBL-"),
        "SEQ-": derive_max_ordinal(pathlib.Path(p["obligations"]), "SEQ-"),
    }
    return {
        "floors_before": before, "floors_after": after,
        "minted_selection_id": selection.selection_id,
        "minted_inquiry_ids": [r.inquiry_id for r in inquiries],
        "selection_ids_on_disk": [r["selection_id"]
                                  for r in loop.selections.selections()],
        "inquiry_ids_on_disk": [r["inquiry_id"]
                                for r in loop.inquiries.inquiries()],
        "dispositions": [r.disposition.value for r in inquiries],
    }


_COMMANDS = {"build": build, "fingerprint": fingerprint,
             "forward": forward_cycle}


def main(argv) -> int:
    command, root, out = argv[1], pathlib.Path(argv[2]), pathlib.Path(argv[3])
    result = _COMMANDS[command](root)
    out.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
