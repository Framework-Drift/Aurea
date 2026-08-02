"""
differential.py - THE DIFFERENTIAL HARNESS, as an AUDITED instrument.

RULING 67 (2026-08-02): AN INSTRUMENT THAT MEASURES HER AUDITS ITS OWN
FOOTPRINT.

WHY THIS FILE EXISTS AT ALL
-------------------------------------------------------------------------------
Every differential this project has run was a SCRATCH file, written per pass and
deleted after. That was tolerable while the harness only read - and it stopped
being tolerable the moment one was measured writing.

THE INCIDENT IS THE SPEC. In a single session the differential harness silently
wrote 39 lines into shared `data/runtime/logs/claim_ancestry.jsonl` - one per
claim in the scenario set - while, in that same session, the audited soak
REFUSED exactly that contamination and said so. **One session demonstrated both
directions of the argument.** The asymmetry was never anyone's decision; it was
that one instrument had been given an audit and the other had not.

So the differential becomes an instrument with the same standing as the soak:
isolated by CODE rather than by the author remembering, and audited on its own
footprint, with the audit result a REQUIRED FIELD of its report.

WHAT IT IS NOT
-------------------------------------------------------------------------------
NOT a gate. It decides no architecture, pins no behaviour, and changes no
`src/` file. It runs the scenario set and writes down what every observable
surface did, so two trees can be compared. **A differential that must produce a
particular answer has stopped measuring** - Docket P's bar for the soak, and it
binds here identically.

IT IMPORTS THE SOAK'S ISOLATION MACHINERY RATHER THAN COPYING IT. `isolate`,
`footprint_audit`, `_shared_runtime_listing` and `SCENARIO_CLAIMS` all come from
`scripts/soak.py`. A second copy of an isolation table is a second definition
free to drift from the first, and the drift would be invisible precisely because
both would look right in isolation.

THE WALL-CLOCK NORMALIZATION IS REPORTED, NOT HIDDEN
-------------------------------------------------------------------------------
`Echo` and `CSA` ids are minted from `datetime.now()`, so two runs of the SAME
tree differ by construction. Comparison therefore normalizes any
`<PREFIX>-<12+ digits>` token to a positional placeholder. That is a WORKAROUND
for a carried defect (Echo wall-clock id minting, elevated on THE PATH), not a
property of the system, and it is named here so no future reader mistakes a
normalized diff for a deterministic one. **The identity run exists to prove the
normalization is sufficient**: run a tree against itself first, and if that is
not clean, the harness is not trustworthy and neither is the comparison.

USAGE
-------------------------------------------------------------------------------
    python scripts/differential.py --out before.json
    (check out the other tree)
    python scripts/differential.py --out after.json
    python scripts/differential.py --compare before.json after.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
# UNCONDITIONAL, matching `soak.py` exactly. A guarded `if ... not in sys.path`
# is an `If` at module level, which Ruling 59's import-inertness scanner
# correctly flags - importing a script must EXECUTE NOTHING, and the scanner
# does not (and should not) reason about which statements are harmless.
# `sys.path.insert` itself is Ruling 59's stated exemption: the scripts need it
# before their `src` imports, it executes no AUREA and touches no store.
sys.path.insert(0, str(REPO))

from scripts.soak import (  # noqa: E402
    SCENARIO_CLAIMS, SoakIsolationError, footprint_audit, isolate,
    _refuse_if_shared_out, _seed_hashes, _shared_runtime_listing)

# Wall-clock-minted ids ONLY. A 12-digit floor keeps ordinary minted ids
# (`CAE-001`, `CLM-0001`, `PRD-0001`, `Scar-11`) untouched - those ARE stable and
# normalizing them would hide real movement.
_TIMESTAMP_ID = re.compile(r"\b([A-Za-z]+)-(\d{12,})\b")


# =====================================================================
# CAPTURE
# =====================================================================

def _packet(packet: Any) -> Optional[Dict[str, Any]]:
    if packet is None:
        return None
    return {
        "content": packet.content,
        "collapse_verdict": getattr(packet.collapse_verdict, "name", None),
        "expression_verdict": getattr(packet.expression_verdict, "name", None),
        "scar_lineage": list(packet.scar_lineage),
        "evidence_refs": list(packet.evidence_refs),
        "unresolved": list(packet.unresolved),
        "abstentions": list(getattr(packet, "abstentions", ())),
        "psi_directive": repr(getattr(packet, "psi_directive", None)),
        "tone_weight": repr(getattr(packet, "tone_weight", None)),
    }


def _topology(core) -> Dict[str, Any]:
    topo = core.tca.topology
    return {
        "nodes": sorted(topo.nodes),
        "edges": sorted("|".join(sorted([n, o]))
                        for n, node in topo.nodes.items() for o in node.edges),
        "total_mass": round(topo.total_mass, 6),
        "total_edges": topo.total_edges,
        "centers": {c: k.gravity_center
                    for c, k in sorted(topo.constellations.items())},
        "constellation_mass": {c: round(k.total_mass, 6)
                               for c, k in sorted(topo.constellations.items())},
        "wormholes": {k: list(v) for k, v in sorted(topo.wormholes.items())},
    }


def _claim_row(result: Dict[str, Any]) -> Dict[str, Any]:
    echo = result.get("echo")
    collapse = result.get("collapse_result")
    return {
        "claim_id": result.get("claim_id"),
        "echo_claim_id": getattr(echo, "claim_id", None) if echo else None,
        "echo_source": getattr(echo, "source", None) if echo else None,
        "output": result.get("output"),
        "output_blocked": result.get("output_blocked"),
        "expression_verdict": getattr(result.get("expression_verdict"),
                                      "name", None),
        "pressure_generated": round(result.get("pressure_generated") or 0.0, 6),
        "errors": result.get("errors"),
        "scar_formed": getattr(result.get("scar_formed"), "id", None),
        "pass_nodes": list(result.get("pass_nodes") or ()),
        "render_trace": list(result.get("render_trace") or ()),
        "reroute_hint": result.get("reroute_hint"),
        "truth_packet": _packet(result.get("truth_packet")),
        "structural_violation": result.get("structural_violation"),
        "reflex_responses": len(result.get("reflex_responses") or []),
        "collapse_verdict": getattr(getattr(collapse, "verdict", None),
                                    "name", None),
        "collapse_pressure": round(
            getattr(collapse, "pressure_generated", 0.0) or 0.0, 6),
        "collapse_reason": getattr(collapse, "reason", None),
        "overlay": repr(getattr(collapse, "overlay", None)) if collapse else None,
    }


def run(root: Path) -> Dict[str, Any]:
    """Drive the scenario set inside `root` and capture every surface.

    ISOLATION FIRST, ALWAYS: `isolate()` runs its own coverage self-audit and
    refuses if `src/` holds an injectable store its table does not cover, and it
    MUST run before anything constructs an `AureaCore` (several stores load from
    `__init__`).
    """
    configured = isolate(root)
    seeds_before = _seed_hashes()
    shared_before = _shared_runtime_listing()

    from src.aurea_core import AureaCore

    core = AureaCore()
    claims = [_claim_row(core.process_input(claim)) for claim in SCENARIO_CLAIMS]
    after_claims = _topology(core)
    core.save_state()

    # The restart boundary, captured because it is where a persistence ruling
    # shows up and nowhere else.
    restarted = _topology(AureaCore())

    seeds_after = _seed_hashes()
    shared_after = _shared_runtime_listing()
    audit = footprint_audit(configured, root, shared_before, shared_after)

    return {
        "instrument": "scripts/differential.py (Ruling 67)",
        "generated_at": datetime.now().isoformat(),
        "parameters": {"claims": len(SCENARIO_CLAIMS), "root": str(root)},
        "isolation": {"configured_paths": len(configured), "root": str(root)},
        # RULING 67: REQUIRED FIELD. A report without it is incomplete, and
        # `compare()` refuses to compare reports that lack or fail it.
        "footprint_audit": audit,
        "seeds": {"before": seeds_before, "after": seeds_after,
                  "identical": seeds_before == seeds_after},
        "non_topology": {"claims": claims},
        "topology": {"after_claims": after_claims, "restarted": restarted},
    }


# =====================================================================
# COMPARE
# =====================================================================

def _normalize(payload: Any) -> Any:
    """Replace wall-clock-minted ids with positional placeholders."""
    seen: Dict[str, str] = {}

    def sub(match: "re.Match[str]") -> str:
        token = match.group(0)
        if token not in seen:
            seen[token] = f"<{match.group(1)}#{len(seen)}>"
        return seen[token]

    return json.loads(_TIMESTAMP_ID.sub(
        sub, json.dumps(payload, sort_keys=True, default=str)))


def compare(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """Report movement, split TOPOLOGY vs NON-TOPOLOGY.

    REFUSES a report whose footprint audit is absent or failing (Ruling 67): a
    measurement taken by a contaminating instrument is not evidence, and
    comparing it would launder the contamination into a conclusion.
    """
    for label, report in (("before", before), ("after", after)):
        audit = report.get("footprint_audit")
        if not audit or not audit.get("performed"):
            raise SoakIsolationError(
                f"the '{label}' report carries no footprint audit. A run "
                f"without its audit is INCOMPLETE (Ruling 67) and may not be "
                f"used as evidence.")
        if not audit.get("pass"):
            raise SoakIsolationError(
                f"the '{label}' report's footprint audit FAILED: "
                f"foreign_writes={audit.get('foreign_writes')}. A contaminating "
                f"run is not a measurement.")

    before, after = _normalize(before), _normalize(after)
    rows_b = before["non_topology"]["claims"]
    rows_a = after["non_topology"]["claims"]

    moved: Dict[str, List[int]] = {}
    for index, (b_row, a_row) in enumerate(zip(rows_b, rows_a)):
        for key in b_row:
            if b_row[key] != a_row.get(key):
                moved.setdefault(key, []).append(index)

    topology_moved = {
        section: [k for k in before["topology"][section]
                  if before["topology"][section][k] != after["topology"][section][k]]
        for section in before["topology"]
    }
    return {
        "non_topology_fields_moved": moved,
        "non_topology_zero_movement": not moved,
        "topology_moved": topology_moved,
        "claim_count": {"before": len(rows_b), "after": len(rows_a)},
    }


# =====================================================================
# CLI
# =====================================================================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="write this tree's capture here")
    parser.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    parser.add_argument("--identity", action="store_true",
                        help="run this tree TWICE and compare it to itself")
    args = parser.parse_args(argv)

    if args.compare:
        before = json.loads(Path(args.compare[0]).read_text(encoding="utf-8"))
        after = json.loads(Path(args.compare[1]).read_text(encoding="utf-8"))
        result = compare(before, after)
        print(json.dumps(result, indent=2))
        return 0 if result["non_topology_zero_movement"] else 1

    if args.identity:
        first = run(Path(tempfile.mkdtemp(prefix="aurea_diff_a_")))
        second = run(Path(tempfile.mkdtemp(prefix="aurea_diff_b_")))
        result = compare(first, second)
        clean = result["non_topology_zero_movement"] and not any(
            result["topology_moved"].values())
        print(f"IDENTITY RUN: {'CLEAN' if clean else 'DIRTY'}")
        print(json.dumps(result, indent=2))
        return 0 if clean else 1

    if not args.out:
        parser.error("one of --out, --compare or --identity is required")

    _refuse_if_shared_out(Path(args.out))
    report = run(Path(tempfile.mkdtemp(prefix="aurea_diff_")))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        json.dumps(report, indent=2, default=str, ensure_ascii=False,
                   sort_keys=True), encoding="utf-8")

    audit = report["footprint_audit"]
    print(f"differential complete: {len(SCENARIO_CLAIMS)} claims -> {args.out}")
    print(f"  footprint audit: {'PASS' if audit['pass'] else 'FAIL'} "
          f"({audit['configured_paths']} paths, "
          f"{len(audit['foreign_writes'])} foreign write(s))")
    if not audit["pass"]:
        # RULING 67: audit failure FAILS THE RUN LOUDLY, never silently
        # annotates a report someone will later read as clean.
        raise SoakIsolationError(
            f"footprint audit FAILED: this run wrote into shared state - "
            f"{audit['foreign_writes']}. The measurement is void.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
