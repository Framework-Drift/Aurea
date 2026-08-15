"""
contradiction_surface.py - M6-γ. A WORLD-MODEL INCONSISTENCY IS A CONFLICT
CANDIDATE ROUTED INTO L4.

    **THE WORLD MODEL HAS NO PRIVATE TRUTH MACHINERY. ITS CONFLICTS STAND IN
    THE SAME COURT AS EVERYTHING ELSE.**

Detected inconsistencies admit a K2 obligation through the EXISTING seam, and
from there the ratified loop owns it: obligation -> episode -> typed disposition.
A world contradiction can end CARRIED, COLLAPSED-with-scar, or
UNRESOLVED_AT_BOUND like any other, because nothing here adjudicates anything.

v1 DETECTION IS RECORD-HONEST, AND THE LIMITATION IS STRUCTURAL RATHER THAN
PROMISED
-------------------------------------------------------------------------------
Two detections, both reading only what the RECORD ITSELF DECLARES:

  (a) any LIVE proposition of kind CONTRADICTION - an explicitly recorded
      inconsistency;
  (b) any PAIR of live propositions joined by MUTUAL `contradicted_by`
      references - each naming the other.

**IT DOES NOT INFER SEMANTIC CONTRADICTION FROM CONTENT, AND IT COULD NOT IF IT
WANTED TO.** This module reads `PropositionSummary`, which carries NO
`asserted_content` at all (M6-α made that a schema fact). So v1's floor is not a
rule anyone must remember to respect - it is the only thing the surface can see.
Semantic detection is COGNITION and arrives with the Executive; naming its owner
is the honest half of declaring a limitation.

    A NOTE ON (b)'s SHAPE. Mutual reference is required rather than one-way,
    deliberately: a one-way `contradicted_by` is a proposition asserting that
    something opposes it, which is an ordinary citation and is what
    `contradicted_by` is FOR. Two propositions each naming the other is the
    record declaring a conflict rather than a stance - and treating every
    one-way citation as an inconsistency would flood L4 with the normal case.

THE ROUTING IS ADDITIVE, BEST-EFFORT, AND GATES NOTHING
-------------------------------------------------------------------------------
`route_inconsistencies` admits obligations and returns what it did. A failure to
admit lands on a legible surface and is RETURNED, never raised into a read path:
Ruling 11's valence - the observer never gates the observed - and detection is
an observation. **No read of the world model can be blocked by the obligation
ledger being unavailable.**

THE OBLIGATION NAMES THE NEWER PROPOSITION, and that is a choice with a reason:
by `WMP-` ordinal, the later record is the one that arrived into an existing
world, so it is the one whose admission is the open question.

PURITY, AND WHAT THIS MODULE IS NOT
-------------------------------------------------------------------------------
Detection is a PURE READ over already-read summaries: no store handle, no path,
no `open`. Routing is the ONLY function that touches an owner, and it touches
exactly one - the obligation ledger's own public `admit`. It writes no store of
its own, owns nothing, and grants nothing.

COINS: `Inconsistency`, `InconsistencyKind`, `RoutingOutcome`. No threshold, no
score, no magnitude.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "InconsistencyKind",
    "Inconsistency",
    "RoutingOutcome",
    "ROUTING_SOURCE",
    "detect_inconsistencies",
    "route_inconsistencies",
]

# The `source` every routed obligation is admitted under - one string, so the
# ledger's own records say which surface asked.
ROUTING_SOURCE = "worldmodel.contradiction_surface"


class InconsistencyKind(str, Enum):
    """WHAT THE RECORD DECLARED. Closed at two, and both are record-honest.

    A third member would mean a new thing the RECORD can say, not a new thing
    this surface can infer - inference is the Executive's.
    """

    DECLARED_CONTRADICTION = "declared_contradiction"   # a CONTRADICTION-kind
    MUTUAL_CONTRADICTION = "mutual_contradiction"       # each names the other


@dataclass(frozen=True)
class Inconsistency:
    """One detected conflict candidate. A REPORT, not a verdict."""

    kind: InconsistencyKind
    target_id: str                       # the proposition the obligation names
    involved: Tuple[str, ...]            # every proposition in the conflict
    claim_text: str


@dataclass(frozen=True)
class RoutingOutcome:
    """What the routing did. Returned, never raised into a read path."""

    admitted: Tuple[str, ...] = ()        # obligation ids
    rejected: Tuple[Tuple[str, str], ...] = ()   # (target_id, reason)
    failures: Tuple[Tuple[str, str], ...] = ()   # (target_id, error)


def _ordinal(wmp_id: str) -> int:
    """The `WMP-` ordinal, for choosing the NEWER proposition.

    An id that does not parse sorts FIRST (`-1`), so it is never chosen as the
    newer one - the conservative direction: an unparseable id is a record whose
    place in the ledger's order is unknown, and guessing it is newer would name
    it in an obligation on the strength of a guess.
    """
    tail = wmp_id.split("-")[-1]
    return int(tail) if tail.isdigit() else -1


def detect_inconsistencies(summaries: Sequence[Any]) -> Tuple[Inconsistency, ...]:
    """Detect conflict candidates in a set of LIVE proposition summaries.

    A PURE READ. The caller supplies `ledger.live_summaries()` - already-read,
    content-free facts - and this returns reports. It touches no store.

    **THE SUMMARIES CARRY NO CONTENT**, so nothing here can read a proposition's
    text even by accident. See the module docstring.
    """
    live_ids = {s.wmp_id for s in summaries}
    found: List[Inconsistency] = []

    # (a) AN EXPLICITLY RECORDED INCONSISTENCY.
    for summary in summaries:
        if getattr(summary.kind, "value", summary.kind) == "contradiction":
            found.append(Inconsistency(
                kind=InconsistencyKind.DECLARED_CONTRADICTION,
                target_id=summary.wmp_id,
                involved=(summary.wmp_id,),
                claim_text=(f"proposition {summary.wmp_id} is recorded as a "
                            f"CONTRADICTION and stands unresolved in the live "
                            f"world model")))

    # (b) MUTUAL CONTRADICTION - each names the other, both live.
    contradicts: Dict[str, set] = {
        s.wmp_id: {r.record_id for r in s.contradicted_by}
        for s in summaries}
    seen = set()
    for wmp_id, targets in contradicts.items():
        for other in sorted(targets):
            if other not in live_ids or wmp_id not in contradicts.get(other, ()):
                continue                      # one-way is an ordinary citation
            pair = tuple(sorted((wmp_id, other)))
            if pair in seen:
                continue
            seen.add(pair)
            # THE NEWER PROPOSITION IS NAMED: it arrived into an existing world,
            # so its admission is the open question.
            newer = max(pair, key=_ordinal)
            found.append(Inconsistency(
                kind=InconsistencyKind.MUTUAL_CONTRADICTION,
                target_id=newer,
                involved=pair,
                claim_text=(f"propositions {pair[0]} and {pair[1]} each record "
                            f"the other as contradicting it, and both are live "
                            f"in the world model")))
    return tuple(found)


def route_inconsistencies(inconsistencies: Sequence[Inconsistency],
                          obligation_ledger: Any) -> RoutingOutcome:
    """Admit a K2 obligation per detected inconsistency. ADDITIVE, BEST-EFFORT.

    THE EXISTING SEAM, UNCHANGED: `admit(source=..., target_kind=..., target_id=
    ..., claim_text=...)`. From there the ratified loop owns it.

    **IT NEVER RAISES INTO A READ PATH.** A failure to admit is recorded on the
    returned outcome, because detection is an OBSERVATION and Ruling 11's rule
    is that the observer never gates the observed - a world-model read must not
    fail because the obligation ledger was unavailable.

    A REJECTED admission is not a failure: the obligation ledger has its own
    rules (a duplicate is refused, and refusing a second obligation for a
    conflict already standing is exactly right), and its refusals are RECORDS.
    """
    from src.filtration.obligation_ledger import TargetKind

    admitted: List[str] = []
    rejected: List[Tuple[str, str]] = []
    failures: List[Tuple[str, str]] = []

    for item in inconsistencies:
        try:
            result = obligation_ledger.admit(
                source=ROUTING_SOURCE,
                target_kind=TargetKind.WORLD_PROPOSITION,
                target_id=item.target_id,
                claim_text=item.claim_text)
        except Exception as exc:                      # best-effort, by ruling
            failures.append((item.target_id, f"{type(exc).__name__}: {exc}"))
            continue
        if result.admitted:
            admitted.append(result.obligation_id)
        else:
            rejected.append((item.target_id, result.reason))

    return RoutingOutcome(admitted=tuple(admitted), rejected=tuple(rejected),
                          failures=tuple(failures))
