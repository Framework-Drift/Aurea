"""
replay.py - M4-γ: REPLAY IS A DERIVATION OVER THE RECORD.

Heading Phase 4: *"state transitions deterministic given prior state plus
recorded acquisitions; nondeterminism confined to acquisition points."* That is
a TESTABLE SENTENCE and this instrument tests it - drive a run whose arrivals are
recorded, re-drive the pipeline FROM THE ACQUISITION LEDGER ALONE, and compare
end-state censuses.

**WHY IT ONLY BECAME ANSWERABLE AFTER M4-β'.** Before the boundary record there
were no recorded acquisitions to be given (M4-α), and before the high-water
envelope three stores minted ids from a wall clock (M4-β'), so two runs of the
same tree differed by construction and a replay could never be identical for
reasons that said nothing about determinism. **After β' no logic path reads a
clock and no id mints from one**, which is why the null result below is a
finding rather than noise.

WHAT IT IS NOT
-------------------------------------------------------------------------------
**NOT A GATE.** It decides no architecture, pins no behaviour, and changes no
`src/` file. It owns no store, holds no path of its own, and reads AUREA only
through the census helpers `soak.py` already uses - ONE implementation, four
callers now (Ruling 67's law: a second copy would be a second definition free to
drift, invisibly, because both would look right alone).

Its results carry ZERO authority, exactly as the soak's and the evaluation
instrument's do.

ISOLATED BY CODE, AUDITED ON ITS OWN FOOTPRINT (Ruling 67)
-------------------------------------------------------------------------------
A fresh temp root per run, every injectable store redirected into it by the
soak's own `isolate()`, and a footprint audit whose RESULT IS A REQUIRED FIELD
of the report. **A run whose audit fails FAILS LOUDLY** - nonzero exit, no
report treated as usable - because a contaminated measurement compared against a
clean one produces a diff that looks like a finding.

THE ONE THING A REPLAY CANNOT RECONSTRUCT, DECLARED RATHER THAN DISCOVERED
-------------------------------------------------------------------------------
An acquisition records the ARRIVAL: payload, channel, correlation. **It does not
record the ancestry DECLARATION** - that is the CLAIM's record (Ruling 58), a
different store, minted after the arrival. So a replay from the acquisition
ledger alone re-drives every arrival faithfully and re-derives every state
transition, but a claim whose channel DECLARED an origin replays as UNDECLARED.

That is not a gap this instrument papers over, and it is not a defect of the
boundary either: it is the two records being about different things. **It is
stated here so nobody later reads an identical census as proof that
declarations round-trip.** For every arrival that declared nothing - which is
every claim the soak, the evaluation corpus and this instrument drive - the
replay is exact.

USAGE
-------------------------------------------------------------------------------
  python -B scripts/replay.py --verify [--out report.json]
      Drive a recorded run, replay it from its own acquisition ledger, compare.
  python -B scripts/replay.py --source <acquisitions.jsonl> [--out report.json]
      Replay an EXISTING recorded ledger and emit the end-state census.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
# UNCONDITIONAL, matching `soak.py` and `differential.py` exactly. A guarded
# `if ... not in sys.path` is an `If` at module level, which Ruling 59's
# import-inertness scanner correctly flags - importing a script must EXECUTE
# NOTHING, and the scanner does not (and should not) reason about which
# statements are harmless. **THE GUARD CAUGHT THIS ONE ON ITS FIRST RUN**, which
# is what it is for. `sys.path.insert` itself is Ruling 59's stated exemption.
sys.path.insert(0, str(REPO))

# ONE ISOLATION, ONE AUDIT, ONE SET OF CENSUS READERS - all imported, never
# copied. `soak.py` owns them; this instrument is their fourth caller.
from scripts.soak import (  # noqa: E402
    SCENARIO_CLAIMS, SoakIsolationError, _acquisition_census, _decay_census,
    _lineage_census, _placement_census, _refuse_if_shared_out,
    _shared_runtime_listing, _suspension_census, footprint_audit, isolate)


class ReplayAuditFailure(Exception):
    """The run's own footprint audit did not pass.

    Ruling 67's law, in its loud form: a measurement that wrote outside its
    sandbox is not a measurement, and reporting it with an annotation would let
    a contaminated run be compared against a clean one.
    """


def census(core: Any) -> Dict[str, Any]:
    """The END-STATE CENSUS - what she holds when the arrivals stop.

    **CLOCK-FREE BY CONSTRUCTION.** Every field is a count, an id, or a derived
    state; no wall field is surfaced. That is what lets the comparison be exact
    rather than normalized - and it is the property M4-β' made available, since
    before it three of these id spaces were minted from `datetime.now()`.
    """
    topology = core.tca.topology
    return {
        "acquisitions": _acquisition_census(core),
        "suspensions": _suspension_census(core),
        "decay": _decay_census(core),
        "lineage": _lineage_census(core),
        "placement": _placement_census(core),
        "echoes": len(core.echo_memory.read_all()),
        "claims": len(core.ancestry.read_all()),
        "scars": len(core.scar_core.all_scars()),
        "doctrines": sorted(core.codex.view()),
        "fossils": sorted(getattr(core.codex, "fossils", {})),
        "topology_nodes": sorted(topology.nodes),
        "topology_edges": sum(len(n.edges) for n in topology.nodes.values()),
        "epoch": {
            "epoch": core.sae.epoch,
            "epoch_count": core.sae.epoch_count,
            "state_quarantined": bool(getattr(core.sae, "state_quarantined", False)),
        },
        "structural_violations": len(getattr(core, "structural_violations", [])),
        "divergence_findings": len(getattr(core, "divergence_findings", [])),
    }


def _drive(core: Any, arrivals: List[Dict[str, Any]]) -> None:
    """Feed arrivals through the PUBLIC DOOR, in recorded order.

    `process_input` is the only entry used - the instrument reimplements no part
    of the pipeline, which is what makes a matching census evidence about AUREA
    rather than about this file.
    """
    for arrival in arrivals:
        core.process_input(arrival["payload"],
                           channel=arrival["channel"],
                           correlation_id=arrival["correlation_id"])


def _arrivals_from(path: Path) -> List[Dict[str, Any]]:
    """Read a recorded acquisition ledger into replayable arrivals.

    Through the store's OWN reader, so era honesty and floor semantics apply
    exactly as they do in the pipeline: a torn or unreadable line contributes
    nothing here for the same reason it contributes nothing there.
    """
    from src.external.acquisition_ledger import AcquisitionLedger
    return [{"payload": r.payload, "channel": r.channel,
             "correlation_id": r.correlation_id}
            for r in AcquisitionLedger(ledger_path=str(path)).read_all()]


def _audited(root: Path, shared_before: List[str]) -> Dict[str, Any]:
    audit = footprint_audit([], root, shared_before, _shared_runtime_listing())
    return audit


def _run_in_sandbox(claims: Optional[List[str]] = None,
                    source: Optional[Path] = None) -> Dict[str, Any]:
    """One isolated run. Either drives `claims` or replays `source`."""
    root = Path(tempfile.mkdtemp(prefix="aurea_replay_"))
    configured = isolate(root)
    shared_before = _shared_runtime_listing()

    from src.aurea_core import AureaCore
    core = AureaCore()

    if source is not None:
        arrivals = _arrivals_from(source)
    else:
        from src.external.acquisition_ledger import AcquisitionChannel
        arrivals = [{"payload": c, "channel": AcquisitionChannel.USER_INPUT,
                     "correlation_id": None} for c in (claims or ())]

    _drive(core, arrivals)

    audit = footprint_audit(configured, root, shared_before,
                            _shared_runtime_listing())
    if not audit["pass"]:
        raise ReplayAuditFailure(
            f"the replay instrument's own footprint audit FAILED: {audit}. A "
            f"contaminated measurement compared against a clean one produces a "
            f"diff that looks like a finding.")

    return {"root": root, "census": census(core), "arrivals": len(arrivals),
            "acquisition_path": Path(core.acquisitions.ledger_path),
            "footprint_audit": audit}


def compare(original: Dict[str, Any], replayed: Dict[str, Any]) -> Dict[str, Any]:
    """Field-by-field. IDENTICAL is the expected result and the milestone's claim."""
    moved = {}
    for key in sorted(set(original) | set(replayed)):
        if original.get(key) != replayed.get(key):
            moved[key] = {"original": original.get(key),
                          "replayed": replayed.get(key)}
    return {"identical": not moved, "moved": moved,
            "fields_compared": len(set(original) | set(replayed))}


def verify(claims: Optional[List[str]] = None) -> Dict[str, Any]:
    """Drive a run, replay it FROM ITS OWN LEDGER, and compare the censuses."""
    claims = list(claims if claims is not None else SCENARIO_CLAIMS)
    first = _run_in_sandbox(claims=claims)
    second = _run_in_sandbox(source=first["acquisition_path"])
    verdict = compare(first["census"], second["census"])
    return {
        "instrument": "scripts/replay.py (M4-γ)",
        "arrivals": {"recorded": first["arrivals"],
                     "replayed": second["arrivals"]},
        # RULING 67: the audit RESULT as a REQUIRED FIELD, for BOTH halves.
        "footprint_audit": first["footprint_audit"],
        "replay_footprint_audit": second["footprint_audit"],
        "comparison": verdict,
        "census": first["census"],
        "replayed_census": second["census"],
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true",
                        help="drive a run, replay it, compare the censuses")
    parser.add_argument("--source", help="replay an existing acquisition ledger")
    parser.add_argument("--out", help="write the report here")
    args = parser.parse_args(argv)

    if not args.verify and not args.source:
        parser.error("one of --verify or --source is required")
    if args.out:
        _refuse_if_shared_out(Path(args.out))

    if args.verify:
        report = verify()
        ok = report["comparison"]["identical"]
        print(f"REPLAY: {'IDENTICAL' if ok else 'DIVERGED'} "
              f"({report['arrivals']['replayed']} arrivals replayed)")
        if not ok:
            print(json.dumps(report["comparison"]["moved"], indent=2,
                             default=str))
    else:
        run = _run_in_sandbox(source=Path(args.source))
        report = {"instrument": "scripts/replay.py (M4-γ)",
                  "arrivals": {"replayed": run["arrivals"]},
                  "footprint_audit": run["footprint_audit"],
                  "census": run["census"]}
        ok = True
        print(f"REPLAY: {run['arrivals']} arrivals replayed")

    print(f"  footprint audit: "
          f"{'PASS' if report['footprint_audit']['pass'] else 'FAIL'} "
          f"({report['footprint_audit']['configured_paths']} paths, "
          f"{len(report['footprint_audit']['foreign_writes'])} foreign write(s))")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            json.dumps(report, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8")
        print(f"  report: {args.out}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
