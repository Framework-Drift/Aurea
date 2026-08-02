"""
source_genealogy.py - RULING 60 / DOCKET O item O2: SOURCE-GENEALOGY ANALYSIS.

    The genealogy of a claim is read from the record,
    and the record cannot certify the world.

Canon: Docket O's own registration - "the ten-thousand-sources-one-origin
problem; LCAE compares model outputs, nothing analyzes source descent";
6b:968 "Consensus Is Not Proof"; L1 applied to counting.

THE PRINCIPLE, AND IT IS THE WHOLE MODULE
------------------------------------------
Ten thousand claims repeating one origin are ONE origin. But this analysis can
only ever see the LEDGER - it cannot see the world. So the instrument reports
what the record SHOWS and REFUSES to certify real-world independence:

    ABSENCE OF RECORDED ANCESTRY YIELDS `UNKNOWN`,
    AND `UNKNOWN` NEVER COUNTS AS CORROBORATION.

A fabricated consensus dies at the counter. An unrecorded one is honestly
uncountable rather than flattered. Those are different outcomes and this module
keeps them different.

WHAT THIS IS
-------------
PURE, READ-ONLY analysis over a `List[ClaimAncestryRecord]`. THE CALLER READS
THE LEDGER (`ClaimAncestryLedger.read_all()`); this module never touches a file,
holds no path, opens nothing, and imports nothing that can write. It is NOT
registered in `STORE_OWNERS` because it stores nothing at all.

NO CONSUMER WIRING EXISTS THIS PASS, deliberately. No verdict path, no HAIL
surface, no routing reads it (O4 owns routing; expression integration is a later
decision). It is an instrument in Docket P's sense - capability plus honesty
guarantees now, consumers when a ruling names one.

WHAT IS DELIBERATELY NOT HERE, each with its owner
----------------------------------------------------
  * CONSUMER WIRING into verdicts or expression - a later ruling; O4 for
    routing.
  * BACKFILLING `claim_id` onto persisted legacy echoes - moving stored bytes,
    which is Ruling 58's own bar.
  * SEMANTIC / FUZZY DESCENT DETECTION - a FUTURE RULING, stated again at
    `MINTED_ID_PATTERN`. Anything subtler than an exact minted id is inference
    wearing a record's clothes.
  * ORIGIN_KIND IN THE PAIRWISE PATH - it is REPORTED in summaries
    (`OriginGroup.recorded_origin_kinds`) and NEVER consulted for standing.
    Two claims sharing a source CLASS share nothing; `human` and `human` is not
    a link, it is a category.
  * TRUST SCORES, and all five standing refusals - restated, refused.

COINS NOTHING: four enum members recovered from the record's own three-state
semantics and the docket's registration language, the id grammar is the ledger's
own, and no threshold, weight or magnitude exists anywhere in this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import (Any, Dict, FrozenSet, Iterable, Iterator, List, Mapping,
                    Optional, Sequence, Set, Tuple)

from src.external.claim_ancestry import ClaimAncestryRecord, FieldState


# =====================================================================
# THE VOCABULARY
# =====================================================================

class GenealogyVerdict(str, Enum):
    """The standing of ONE claim relative to ANOTHER, as the record shows it.

    CLOSED, four members. ADDITIONS REQUIRE A MANIFEST RULING (Ruling 7's
    closed-enum discipline).

    "INDEPENDENT" IS DELIBERATELY NOT A MEMBER, AND THE REFUSAL IS THE RULING'S
    SHARPEST LINE. The ledger records ASSERTIONS ABOUT descent; it cannot see
    the world. Two claims with no recorded link may still share an origin that
    nobody wrote down - so calling them independent would be the analysis
    certifying something it never observed, which is exactly the fabrication
    Ruling 58 exists to stop, relocated one layer up into a verdict.
    `NO_RECORDED_LINK` is the STRONGEST HONEST CLAIM available here, and the
    naming carries the epistemics: it says what was consulted, not what is true.

    A `str` Enum by the shape rule: one vocabulary, no collision partner
    anywhere in the tree.
    """

    # `asserted_by` PROVIDED on both records and EQUAL - one recorded
    # proximate source standing behind both claims.
    SHARED_ASSERTER = "shared_asserter"

    # A recorded reference path exists between the two claims (directed): one
    # cites the other's minted id, possibly through intermediaries.
    RECORDED_DESCENT = "recorded_descent"

    # EVERY consulted surface is a RECORD - PROVIDED or DECLARED_NONE - and
    # neither equality nor any path holds. The record is complete and shows
    # no link. This is NOT independence; see the class docstring.
    NO_RECORDED_LINK = "no_recorded_link"

    # Any consulted surface is ABSENT on either side. The channel said NOTHING
    # there, so the question was never answered and this analysis will not
    # answer it by default.
    UNKNOWN = "unknown"


# THE CONSULTED SURFACES, named ONCE so no second spelling can drift.
#
# WHY THESE THREE AND NOT ALL FIVE - A JUDGMENT CALL, STATED. The ruling defines
# SHARED_ASSERTER off `asserted_by` and RECORDED_DESCENT off `basis` /
# `replication_refs`, and names no other field. `connecting_assumptions` and
# `defeaters` bear on an argument's STRUCTURE and its REBUTTAL, not on its
# descent - so consulting them would let an unrelated absence poison a genealogy
# verdict to UNKNOWN while the descent question was fully answered. Widening
# this tuple is a ruling, not a convenience.
CONSULTED_FIELDS: Tuple[str, ...] = ("asserted_by", "basis", "replication_refs")

# The two surfaces on which a claim can CITE another claim.
DESCENT_FIELDS: Tuple[str, ...] = ("basis", "replication_refs")

# THE LEDGER'S OWN CLOSED GRAMMAR: `CLM-` + digits. Minted by the house
# (`ClaimAncestryLedger.ID_PREFIX` + `{n:04d}`), never by a channel.
#
# EXACT MINTED IDS ONLY. NO semantic matching, NO similarity, NO prose
# interpretation - that would be INFERENCE WEARING A RECORD'S CLOTHES, and this
# module's entire claim on trust is that it reports only what was written down.
# Anything subtler is a FUTURE RULING.
#
# THE DOCKET H SUBSTRING LESSON IS ACKNOWLEDGED AND DISTINGUISHED HERE. That
# scan misfired because it matched OPEN PROSE, where any sentence could contain
# the token. This grammar is CLOSED and house-minted, and matches are compared
# by EXACT STRING EQUALITY against a real record id - so `CLM-0001` does NOT
# match inside `CLM-00010` (the pattern takes the MAXIMAL digit run, Ruling 49's
# `Doctrine-0` / `Doctrine-0.1` lesson), and no numeric normalization happens
# anywhere: `CLM-0001` and `CLM-1` are different strings and stay different.
# The pins carry a NO-MATCH CONTROL so a pattern that has stopped discriminating
# fails there rather than quietly grouping everything.
# RULING 64 res.6 - ANCHORED, AS RULING 60 res.3 ALREADY SAID IN WORDS AND
# THIS PATTERN DID NOT DO. It was `re.compile(r"CLM-\d+")`, so
# `prefixCLM-0001suffix` MATCHED and minted a false descent edge out of a
# substring - THE DOCKET H SUBSTRING LESSON RECURRING INSIDE THE MODULE WHOSE
# OWN RULING CITED IT. Neither the pass nor the drafting lane caught it; an
# external review did.
#
# The boundaries are explicit rather than `\b`: `\b` sits between a word
# character and a non-word character, and `-` is a non-word character, so
# `\bCLM-\d+\b` would still match inside `x-CLM-0001`. These lookarounds
# exclude every identifier character on both sides, which is what "anchored"
# has to mean for a house-minted id embedded in free text.
MINTED_ID_PATTERN = re.compile(r"(?<![0-9A-Za-z_\-])CLM-\d+(?![0-9A-Za-z_\-])")


# =====================================================================
# THE READS - every one of them over recorded facts only
# =====================================================================

def _walk_strings(value: Any) -> Iterator[str]:
    """Every string anywhere inside a recorded field value.

    A PROVIDED value arrives DEEP-FROZEN from `ClaimAncestryRecord` (Ruling 52):
    dicts are `MappingProxyType`, lists are tuples, sets are frozensets. Keys are
    walked as well as values, because `{"CLM-0001": "as cited"}` records a
    reference just as honestly as `["CLM-0001"]` does.

    BOUNDED BY CONSTRUCTION (Ruling 4): the deep freeze rebuilds the container
    graph at record construction, so a cyclic structure could never have reached
    a stored record - the recursion here walks a finite tree.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk_strings(key)
            yield from _walk_strings(item)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from _walk_strings(item)


def recorded_reference_ids(record: ClaimAncestryRecord) -> FrozenSet[str]:
    """The minted claim ids this record CITES, from PROVIDED surfaces only.

    A DECLARED_NONE or ABSENT surface cites nothing - the first because it said
    so, the second because it said nothing. Neither can produce an edge, and
    they are distinguished elsewhere (that is what `UNKNOWN` is for).

    A record citing ITSELF produces no edge: a self-reference is not descent.
    """
    found: Set[str] = set()
    for name in DESCENT_FIELDS:
        surface = getattr(record, name)
        if surface.state is not FieldState.PROVIDED:
            continue
        for text in _walk_strings(surface.value):
            found.update(MINTED_ID_PATTERN.findall(text))
    found.discard(record.claim_id)
    return frozenset(found)


def shares_recorded_asserter(a: ClaimAncestryRecord,
                             b: ClaimAncestryRecord) -> bool:
    """`asserted_by` PROVIDED on BOTH and equal.

    DECLARED_NONE on both is NOT a shared asserter: two channels that each
    declared "there is no asserter" have recorded an ABSENCE in common, not a
    SOURCE in common. Reading that as a link would manufacture an origin out of
    two statements that no origin exists.
    """
    left, right = a.asserted_by, b.asserted_by
    return (left.state is FieldState.PROVIDED
            and right.state is FieldState.PROVIDED
            and left.value == right.value)


def _has_absent_consulted_surface(a: ClaimAncestryRecord,
                                  b: ClaimAncestryRecord) -> bool:
    """Any consulted surface ABSENT on EITHER side - the UNKNOWN condition.

    DOCKET H'S TWO-ABSENCES CUT DOING LOAD-BEARING WORK IN A VERDICT:
    DECLARED_NONE is a RECORDED NEGATIVE and passes through here (a channel that
    declared "no asserter exists" can still reach NO_RECORDED_LINK on its
    recorded refs); ABSENT POISONS the surface to UNKNOWN. Flattening the two
    would make "nobody asked" read as "asked and none exist" - the
    abstention-becomes-honest-zero defect, at the counter.
    """
    for record in (a, b):
        for name in CONSULTED_FIELDS:
            if getattr(record, name).state is FieldState.ABSENT:
                return True
    return False


def _out_edges(records: Iterable[ClaimAncestryRecord]) -> Dict[str, FrozenSet[str]]:
    """Directed citation edges: `{citing_id: {cited_ids}}`."""
    return {record.claim_id: recorded_reference_ids(record) for record in records}


def _reaches(start: str, target: str,
             out_edges: Mapping[str, FrozenSet[str]]) -> bool:
    """Is `target` reachable from `start` along recorded citations?

    TRANSITIVE CLOSURE WITH A VISITED SET - Ruling 4 DECLARED-BOUNDED: the
    record set is finite and the frontier is monotone (no id is expanded twice),
    so this terminates on any graph, including a cyclic one. A citation cycle is
    possible in principle (two claims citing each other), and the visited set is
    what makes that a finite answer rather than a hang.
    """
    if start == target:
        return False
    visited: Set[str] = {start}
    frontier: List[str] = [start]
    while frontier:
        current = frontier.pop()
        for cited in out_edges.get(current, frozenset()):
            if cited == target:
                return True
            if cited not in visited:
                visited.add(cited)
                frontier.append(cited)
    return False


def pairwise_verdict(a: ClaimAncestryRecord, b: ClaimAncestryRecord,
                     records: Sequence[ClaimAncestryRecord] = ()
                     ) -> GenealogyVerdict:
    """The recorded standing of `a` relative to `b`.

    `records` is the CORPUS - it is what makes PATHS visible as opposed to
    direct edges only. `a` and `b` are always included implicitly, so a bare
    two-argument call answers on direct citations alone; pass the ledger to see
    descent through intermediaries.

    ORDER OF ADJUDICATION, AND IT IS DELIBERATE: recorded POSITIVES are decided
    before absences. A claim that shares a recorded asserter with another has a
    recorded link WHETHER OR NOT some other surface went unanswered - reporting
    UNKNOWN there would discard a fact that IS on record, which is the opposite
    of this module's error direction. `UNKNOWN` is what an unanswered question
    yields when NOTHING positive was recorded.

    SHARED_ASSERTER is checked before RECORDED_DESCENT purely for reporting
    determinism; the two are equivalent for grouping (both collapse a pair into
    one origin), so the precedence changes no count.
    """
    if shares_recorded_asserter(a, b):
        return GenealogyVerdict.SHARED_ASSERTER

    pool: Dict[str, ClaimAncestryRecord] = {r.claim_id: r for r in records}
    pool.setdefault(a.claim_id, a)
    pool.setdefault(b.claim_id, b)
    out_edges = _out_edges(pool.values())
    if (_reaches(a.claim_id, b.claim_id, out_edges)
            or _reaches(b.claim_id, a.claim_id, out_edges)):
        return GenealogyVerdict.RECORDED_DESCENT

    if _has_absent_consulted_surface(a, b):
        return GenealogyVerdict.UNKNOWN
    return GenealogyVerdict.NO_RECORDED_LINK


# =====================================================================
# THE COUNTING OPERATION - what the docket registered O2 for
# =====================================================================

@dataclass(frozen=True)
class OriginGroup:
    """One recorded origin: the claims that collapse into it.

    EPHEMERAL - never persisted, never stored, no `as_dict`. Deliberately: a
    serialization surface is how an analysis becomes a store, and this module
    owns nothing.
    """

    claim_ids: Tuple[str, ...]
    # REPORTED, NEVER CONSULTED (res.6). The source CLASSES present in this
    # group, deduped and ordered. Two claims both marked `human` share a
    # category, not an origin - `origin_kind` never reaches
    # `pairwise_verdict`, and a pin holds that line.
    recorded_origin_kinds: Tuple[str, ...]


@dataclass(frozen=True)
class CorroborationSummary:
    """What the RECORD shows about how many origins a set of claims has.

    EPHEMERAL, never persisted. Counts of record only - NO WEIGHTS, NO SCORES,
    NO THRESHOLDS. Nothing in this module compares these numbers to anything;
    they REPORT (standing bar #5).
    """

    # Groups whose genealogy is ON RECORD. Ten thousand claims naming one
    # recorded asserter -> 1.
    distinct_recorded_origins: int
    # Claims whose recorded standing is UNKNOWN. REPORTED SEPARATELY AND NEVER
    # ADDED TO `distinct_recorded_origins` - that addition is the fabrication
    # this whole module exists to refuse. Ten thousand undeclared claims ->
    # distinct 0, unknown 10000.
    unknown_count: int
    groups: Tuple[OriginGroup, ...]
    unknown_claims: Tuple[str, ...]


def _origin_kinds(claim_ids: Iterable[str],
                  pool: Mapping[str, ClaimAncestryRecord]) -> Tuple[str, ...]:
    """Deduped, ordered source classes present. A report, not an input."""
    kinds: List[str] = []
    for claim_id in claim_ids:
        record = pool.get(claim_id)
        if record is not None and record.origin_kind.value not in kinds:
            kinds.append(record.origin_kind.value)
    return tuple(sorted(kinds))


def _undirected_components(pool: Mapping[str, ClaimAncestryRecord]
                           ) -> Dict[str, int]:
    """Connected components over SHARED_ASSERTER + RECORDED_DESCENT edges.

    UNDIRECTED FOR GROUPING, and that is right: descent is directional, but two
    claims connected by it collapse into ONE origin regardless of which cites
    which. Direction is what `pairwise_verdict` reports; grouping is what
    counting needs.

    Components are computed over the WHOLE POOL, not over the requested subset,
    so two counted claims that both descend from an UNCOUNTED common ancestor
    still collapse into one origin - which is precisely the
    ten-thousand-sources-one-origin case the docket registered.
    """
    parent: Dict[str, str] = {claim_id: claim_id for claim_id in pool}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: str, right: str) -> None:
        a_root, b_root = find(left), find(right)
        if a_root != b_root:
            parent[b_root] = a_root

    # Citation edges. An edge to an id NOT in the pool groups nothing - there is
    # no second claim on this side of it to collapse with.
    for claim_id, record in pool.items():
        for cited in recorded_reference_ids(record):
            if cited in parent:
                union(claim_id, cited)

    # Shared-asserter edges. Compared PAIRWISE rather than bucketed by value: a
    # PROVIDED value may be a `MappingProxyType`, which is UNHASHABLE, so it
    # cannot be a dict key. Bounded by the record count, which is the ledger.
    asserters = [r for r in pool.values()
                 if r.asserted_by.state is FieldState.PROVIDED]
    for index, left in enumerate(asserters):
        for right in asserters[index + 1:]:
            if left.asserted_by.value == right.asserted_by.value:
                union(left.claim_id, right.claim_id)

    return {claim_id: find(claim_id) for claim_id in parent}


def corroboration(claim_ids: Sequence[str],
                  records: Sequence[ClaimAncestryRecord]
                  ) -> CorroborationSummary:
    """Collapse a set of claims into the origins the RECORD actually shows.

    THE RULE, in one line: claims connected by a recorded link collapse into one
    origin-group; a claim with NO recorded link and an UNANSWERED surface is
    UNKNOWN and is counted nowhere near the origin count.

    A requested claim with NO RECORD AT ALL is UNKNOWN - nothing was written
    down about it, which is the purest form of the condition.

    A claim whose consulted surfaces are ALL RECORDS but which links to nothing
    forms its OWN origin group: its genealogy is on record and shows a standalone
    source. That is a real finding and is counted. The claim that merely went
    UNRECORDED is not, and keeping those two apart is the entire point.
    """
    pool: Dict[str, ClaimAncestryRecord] = {r.claim_id: r for r in records}
    requested: Tuple[str, ...] = tuple(dict.fromkeys(claim_ids))
    component_of = _undirected_components(pool)

    grouped: Dict[str, List[str]] = {}
    unknown: List[str] = []

    for claim_id in requested:
        record = pool.get(claim_id)
        if record is None:
            unknown.append(claim_id)
            continue
        root = component_of[claim_id]
        linked = any(other != claim_id and component_of[other] == root
                     for other in pool)
        if not linked and any(getattr(record, name).state is FieldState.ABSENT
                              for name in CONSULTED_FIELDS):
            # No recorded link to anything, and its own record leaves a
            # consulted question unanswered. The record cannot say whether this
            # is a distinct origin, so it does not say.
            unknown.append(claim_id)
            continue
        grouped.setdefault(root, []).append(claim_id)

    groups = tuple(
        OriginGroup(claim_ids=tuple(sorted(members)),
                    recorded_origin_kinds=_origin_kinds(members, pool))
        for _, members in sorted(grouped.items(),
                                 key=lambda item: sorted(item[1])[0]))

    return CorroborationSummary(
        distinct_recorded_origins=len(groups),
        unknown_count=len(unknown),
        groups=groups,
        unknown_claims=tuple(unknown),
    )
