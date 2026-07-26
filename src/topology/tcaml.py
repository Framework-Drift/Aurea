"""
tcaml.py - Topological Constellation Anchor & Meta-Layer, Stage 1 (organ only)

Canon: `Pressure_Valve_Coordination___Timing_Risks.txt` ("Arbitration Protocol
v2.0", Rules 1-3), `BUILD_CONTRACT.md` 1/3 (RACM <-> TCAML), Ruling 27.
Formal spec: `docs/formal/tcaml_lock/` - three Quint models + README. Those
models were checked at design time; THIS FILE is held to them, and any place
the Python cannot match the model is a reporting obligation, never something
to paper over (Docket J's standing caveat).

WHAT TCAML IS
-------------
TCAML owns two things nothing else may write: ANCHOR STATE (the constellation's
orientation record - CSE measures drift and ASKS; it never straightens the
needle itself) and the GLOBAL LOCK (the one seat a system-wide mutation must
occupy before it runs). RACM arbitrates which reflex wins; TCAML decides
whether the topology can survive the winner running right now. Those are
different questions with different owners (Ruling 2's shape: the arbiter never
originates, the source never adjudicates).

THE THREE RULES (Arbitration Protocol v2.0, unchanged by Ruling 27)
-------------------------------------------------------------------
Rule 1  LOCAL scope requires NO lock check. There is no check to perform, and
        inventing one would make every local reflex pay for a global hazard.
Rule 2  GLOBAL scope requires a SYNCHRONOUS two-phase handoff: request ->
        grant/deny, decided against live state. NEVER a cached or prior-cycle
        answer. A lock you were granted last cycle is not a lock.
Rule 3  Meta-instability (META_UNSTABLE / REPAIR_CYCLE) locks out GLOBAL
        action - and see below, it REVOKES, it does not merely block.

RULING 27's THREE ADDITIONS
---------------------------
1. BOUNDED HOLD. `TTL = 5` (canon 5-cycle horizon, recovered - not coined). A
   lock held that long is force-expired, because a holder that crashed or
   forgot to release must not be able to freeze GLOBAL action forever. See
   `tick()` for the scheduling half of this, which is the load-bearing half.
2. REVOKE ON ONSET. Transition into META_UNSTABLE or REPAIR_CYCLE clears the
   holder IN THE SAME TRANSITION. Model-checked NECESSARY, not a style
   preference - see `_enter_instability()`.
3. STRUCTURAL TIER. Docket F's graph measures select WHICH health threshold a
   request must clear. They never deny on their own. See `assess_topology()`.

STAGE BOUNDARY (Stage 1 of 2) - THE ORGAN, NOT THE WIRING
----------------------------------------------------------
Following the PSI / Nova precedent: build and pin the organ in isolation
BEFORE wiring it, because a half-wired lock is worse than an unwired one - it
would make GLOBAL actions fail in ways nothing tests yet. Nothing imports this
file into the pipeline. `RACM._request_lock()`'s build-stage default-grant
branch is UNTOUCHED and stays until Stage 2. The honest seams:
  - `RACM._request_lock()`      <- Stage 2 constructs TCAML and passes it in;
                                   that is where the default-grant branch dies
  - `CSE._realign()`            <- already calls `anchor_feedback_update` /
                                   `trigger_anchor_realignment` behind hasattr
                                   guards; both exist here, and realignment is
                                   a RECORDED REQUEST with no corrective
                                   effect (see PARKED, below)
  - `health`                    <- the Constellation Health Index has NO
                                   combination rule in the corpus; see below

THE CONSTELLATION HEALTH INDEX IS DELIBERATELY NOT COMPUTED HERE
-----------------------------------------------------------------
The corpus names five inputs (anchor drift, scar bloom density, fragmentation,
dead-zone index, meta-stability) and gives NO combination rule. A weighted
average would be a coined magnitude at the most safety-critical site in the
organ - the number that decides whether a system-wide mutation may proceed.
That is the Symbolic Heat Index shape, refused twice already (Nova's IV
scores, `echo_resonance`). So `health` is a SETTABLE FIELD with a documented
default of 100 (the model's `init`), awaiting its own ruling. `set_health()`
exists for tests and for whatever eventually owns the computation. Do not
"finish" this by inventing a formula.

PARKED, LEGIBLE, NO EFFECT (Ruling 15's shape)
-----------------------------------------------
`trigger_anchor_realignment` records a REQUEST on `realignment_requests` and
changes no anchor. Realignment means moving an orientation reference, and the
corpus gives no magnitude and no target for that move; coining one would let
TCAML quietly redefine which way "true" points - the single worst thing this
module could do silently. The requests accumulate as real forensics with zero
effect until ruled, exactly as Nova's `scar_requests` do.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx


# =====================================================================
# CONSTANTS
# =====================================================================

# CANON, RECOVERED - not coined. The 5-cycle symbolic horizon (CLAUDE.md 5:
# "5 (symbolic cycle horizon)"), reused as the lock's hold bound. A lock is a
# claim on the present; five cycles is how long the present lasts here.
TTL = 5

# COINED - already REGISTERED in `Aurea Build/COINED_CONSTANTS.md` (the
# architect's file, sibling to this repo) under this module's own section. The
# justifications below are that register's, NOT independent ones invented here:
# two divergent rationales for the same magnitude is how a coined number starts
# drifting. If you change one side, change both, and say so.
#
# Each is a health FLOOR on a 0..100 index. None of them is a formula.
#
# ROUTINE_THRESHOLD (COINED): minimum Health Index a `ROUTINE`-tier GLOBAL
# request must clear. Reuses the project's recurring "elevated attention" 0.4
# band (DEE `PRESSURE_RISING`), rescaled 0-100 for the Health Index. Only the
# RESCALED REUSE is coined, not a fresh number.
ROUTINE_THRESHOLD = 40

# ELEVATED_THRESHOLD (COINED): minimum Health Index an `ELEVATED`-tier request
# must clear - one Docket F flagged as structurally consequential. Reuses the
# recurring "critical" 0.75 band (EchoNet `BASE_THRESHOLD`, DEE
# `PRESSURE_CRITICAL`, RIL `IDENTITY_FRACTURE_PRESSURE`). The SAME gate as
# routine at a stricter bar - never a separate verdict path.
ELEVATED_THRESHOLD = 75

# RECOVERY_THRESHOLD (COINED): health required to leave META_UNSTABLE /
# REPAIR_CYCLE. Same band as ELEVATED_THRESHOLD, DELIBERATELY EQUAL rather than
# lower - no hysteresis band is coined here.
# FLAGGED AS AN OPEN DECISION, not a considered-and-rejected one (Ruling 27,
# open question 2). Canon's 20 deg / 25 deg pair is an existing precedent for a
# hysteresis band if this index is ever observed oscillating across one
# threshold. Nothing in THIS module moves health, so it cannot flap on its own;
# a caller oscillating health across 75 would flap the status.
RECOVERY_THRESHOLD = 75

# The model's `init` health. SPEC-DERIVED (tcaml_lock.qnt: `health' = 100`),
# not coined: it is "full" on a 0..100 index, not a tuned magnitude.
DEFAULT_HEALTH = 100

HEALTH_FLOOR = 0
HEALTH_CEILING = 100

# Float comparison tolerance for betweenness ties. A NUMERIC TOLERANCE, NOT A
# DECISION THRESHOLD - it decides whether two identically-computed centralities
# are the same number, and says nothing about AUREA. That distinction is the
# whole of why Ruling 28 can keep this line while refusing a betweenness
# cutoff: a cutoff would decide something, this only compares floats.
# (Registered as such in COINED_CONSTANTS.md.)
_TIE_TOLERANCE = 1e-9

# Ruling 27's tier-default confirmation (2026-07-26). `tier=None` still
# defaults to ROUTINE - defaulting to ELEVATED would assert structural danger
# NO MEASURE FOUND, which is Nova's G1 failure mode in another organ. The
# default is UPHELD and does not move.
#
# But SBSRE's non-finite rule establishes that THE UNINFORMATIVE CASE IS THE
# CONSERVATIVE CASE, and "no delta supplied" is UNKNOWN impact, not
# MEASURED-BENIGN impact. So the two must never be textually identical in the
# record: an unexamined request says so, in the reason, every time.
#
# Whether a delta-less GLOBAL request should be REFUSED outright is a later
# question, decidable once real callers exist. Today RACM supplies no delta at
# all, so refusing would deny every GLOBAL reflex.
UNEXAMINED_DELTA_NOTE = ("no topology_delta supplied - structural impact "
                         "UNEXAMINED, not cleared")


class Status(str, Enum):
    """TCAML's meta-stability state.

    A `str` Enum ON PURPOSE. `RACM._meta_unstable()` reads
    `getattr(self.tcaml, "status", "")` and tests membership in
    `META_UNSTABLE_STATES = frozenset({"meta-unstable", "repair_cycle"})`.
    These VALUES are that frozenset's members verbatim, and str-subclassing
    makes the membership test succeed on the enum member itself. Change either
    side and RACM stops seeing instability - silently, which is the failure
    mode this whole module exists to prevent. Pinned by test.
    """
    HEALTHY = "healthy"
    META_UNSTABLE = "meta-unstable"
    REPAIR_CYCLE = "repair_cycle"


class Tier(str, Enum):
    """Which health threshold a GLOBAL request must clear.

    Selected by structural evidence (Docket F), never by preference. A tier is
    NOT a verdict: `ELEVATED` means "clear a stricter bar on the same gate",
    not "denied by a second path".
    """
    ROUTINE = "routine"
    ELEVATED = "elevated"


class Scope(str, Enum):
    """Values match `racm.Scope` verbatim - RACM passes `claim.scope.value`."""
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"


META_UNSTABLE_STATUSES = frozenset({Status.META_UNSTABLE, Status.REPAIR_CYCLE})


# =====================================================================
# RULING 29 (2026-07-26) - TWO CAUSALLY OPPOSITE EVENTS, TWO TYPES
# =====================================================================
# Keeping the raise was correct: swallowing it would make a revoked operation
# indistinguishable from a completed one. But ONE type covering BOTH causes is
# Ruling 25's defect one level down - the taxonomy CUTS, and it has to cut here
# too. Deliberately NOT a shared base class, for the reason `aurea_core`'s
# STRUCTURAL_VIOLATIONS note gives: a base class silently widens the set the
# next time someone subclasses it. Two concrete types, both enumerated.

class LockReleaseViolation(Exception):
    """A caller released a GLOBAL lock it NEVER HELD.

    CALLER ERROR - an upstream gate already failed. The caller believes it
    holds a lock it never got, or two modules disagree about who owns a
    system-wide mutation. STRUCTURAL, not an error message (Ruling 25): a
    no-op `return False` would make both faults look like a clean release.

    NOT for a holder whose lock TCAML took away - that is `StaleLockRelease`,
    and the two are causally opposite (this one blames the caller; that one
    absolves it).
    """


class StaleLockRelease(Exception):
    """A caller released a GLOBAL lock TCAML TOOK AWAY FROM IT.

    SYSTEM ACTION - the caller is BLAMELESS. Its lock was revoked by
    meta-instability onset (Rule 3) or force-expired at TTL, and this raise is
    how it finds out. The message always names WHICH of the two happened,
    because "your lock is gone" without a cause just relocates the mystery.

    THIS IS THE ABANDONED-STATE MARKER FOR THE CURRENT ERA, AND ONLY FOR IT.
    Nothing downstream is durable yet, so an interrupted GLOBAL operation
    genuinely just stops, and a typed loud record is the honest whole of what
    happened to it. WHEN A PERSISTENCE CONTRACT LANDS THIS BECOMES A TRIGGER,
    NOT AN ANSWER: an interrupted operation will then need a real abandoned /
    resumable state, and this raise is where that transition begins. Do not
    mistake it for a finished design (Ruling 27, decision point (i)).
    """


# =====================================================================
# VALUE OBJECTS
# =====================================================================

@dataclass
class LockResponse:
    """The answer to ONE `lock_request` call, decided against live state.

    `reason` is not optional and is never empty. Ruling 23's principle: an
    unresolved request never leaves without a record. A bare `False` tells a
    caller it lost without telling anyone WHY, and a denial nobody can explain
    is indistinguishable from a bug in the denier.

    `__bool__` returns `granted`. This is deliberate and load-bearing:
    `RACM._request_lock()` already contains `if not grant:` against whatever
    `lock_request` returns, and a plain dataclass instance is ALWAYS truthy -
    wiring this in without `__bool__` would make RACM read every denial as a
    grant. Defusing it here means Stage 2 changes how RACM CONSTRUCTS TCAML,
    not how it reads a lock answer.
    """
    granted: bool
    action_id: str
    reason: str
    scope: Scope = Scope.GLOBAL
    tier: Optional[Tier] = None
    cycle: int = 0
    # Ruling 27 tier-default CONFIRMATION (2026-07-26). False means no
    # `topology_delta` was supplied, so NO structural measure ran. See
    # UNEXAMINED_DELTA_NOTE - "unknown impact" and "measured benign" are
    # different facts and must never read identically.
    delta_examined: bool = False

    def __bool__(self) -> bool:
        return self.granted


@dataclass
class LockState:
    """A SNAPSHOT of the lock (Ruling 22). Mutating it changes nothing."""
    status: Status
    holder: Optional[str]
    holder_module: Optional[str]
    held_since: Optional[int]
    health: int
    cycle: int


@dataclass
class AnchorState:
    """One anchor's record. TCAML is its sole writer (Ruling 1)."""
    anchor_id: str
    last_reported_drift: float = 0.0
    last_reported_cycle: int = 0
    reports: int = 0
    realignments_requested: int = 0


@dataclass
class TopologyDelta:
    """A PROPOSED change to the TCA graph, plus the graph it changes.

    Carries the before-graph explicitly rather than reaching into
    `TopologicalSpace`: TCAML must be able to assess a change that has not
    happened, and a delta that describes itself is testable in isolation.
    Edges are DIRECTED (mirroring `ConstellationNode.edges`, a mapping from a
    node to its targets); the undirected view is DERIVED where a measure needs
    one, never assumed.
    """
    nodes: Set[str] = field(default_factory=set)
    edges: Set[Tuple[str, str]] = field(default_factory=set)
    added_nodes: Set[str] = field(default_factory=set)
    removed_nodes: Set[str] = field(default_factory=set)
    added_edges: Set[Tuple[str, str]] = field(default_factory=set)
    removed_edges: Set[Tuple[str, str]] = field(default_factory=set)
    protected_anchors: Set[str] = field(default_factory=set)
    scar_nodes: Set[str] = field(default_factory=set)
    description: str = ""

    def before(self) -> "nx.DiGraph":
        g = nx.DiGraph()
        g.add_nodes_from(self.nodes)
        g.add_edges_from(self.edges)
        return g

    def after(self) -> "nx.DiGraph":
        g = self.before()
        g.remove_edges_from([e for e in self.removed_edges if g.has_edge(*e)])
        g.remove_nodes_from([n for n in self.removed_nodes if g.has_node(n)])
        g.add_nodes_from(self.added_nodes)
        g.add_edges_from(self.added_edges)
        return g


@dataclass
class TopologyAssessment:
    """`assess_topology`'s full working, kept legible.

    `reasons` holds ONE STRING PER NAMED STRUCTURAL CONDITION that fired. It
    is a list, not a score. Docket F's measures are combined by boolean OR
    over individually-legible conditions and are NEVER summed, weighted, or
    multiplied together - that is the Symbolic Heat Index shape, refused as a
    standing bar. A single number cannot tell you WHICH structure is at risk,
    and "which" is the entire content of a topological assessment.
    """
    tier: Tier
    reasons: List[str] = field(default_factory=list)
    measures: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# DOCKET F - STRUCTURAL TIER SELECTION
# =====================================================================

def _undirected(g: "nx.DiGraph") -> "nx.Graph":
    u = nx.Graph(g.to_undirected())
    u.remove_edges_from(list(nx.selfloop_edges(u)))
    return u


def _core_numbers(g: "nx.Graph") -> Dict[str, int]:
    if g.number_of_nodes() == 0:
        return {}
    return nx.core_number(g)


def _min_scar_to_anchor(g: "nx.Graph", scars: Iterable[str],
                        anchors: Iterable[str]) -> float:
    """Shortest hop count from ANY scar node to ANY protected anchor.

    `inf` when no such path exists. Used ONLY as a before/after comparison -
    see condition 5 in `assess_topology`, which deliberately never asks "is
    this path short?" (that would need a magnitude the corpus does not give).
    """
    best = math.inf
    anchor_set = {a for a in anchors if g.has_node(a)}
    if not anchor_set:
        return best
    for scar in scars:
        if not g.has_node(scar):
            continue
        lengths = nx.single_source_shortest_path_length(g, scar)
        for anchor in anchor_set:
            if anchor in lengths:
                best = min(best, float(lengths[anchor]))
    return best


def _sccs(g: "nx.DiGraph") -> List[Set[str]]:
    return [set(c) for c in nx.strongly_connected_components(g)]


def _betweenness_hubs(g: "nx.Graph") -> Set[str]:
    """The ARGMAX of betweenness centrality - the graph's busiest through-routes.

    Argmax, not a threshold, ON PURPOSE: "betweenness above X" would be a
    COINED magnitude and this module refuses to coin one. Argmax needs no
    magnitude and is deterministic.
    """
    if g.number_of_nodes() == 0:
        return set()
    scores = nx.betweenness_centrality(g)
    top = max(scores.values())
    if top <= _TIE_TOLERANCE:
        return set()
    return {n for n, s in scores.items()
            if math.isclose(s, top, rel_tol=_TIE_TOLERANCE)}


def assess_topology(delta: Optional[TopologyDelta]) -> TopologyAssessment:
    """Select a THRESHOLD TIER from deterministic structural measures.

    RULING 27: these measures NEVER DENY. They choose which health floor the
    request must clear on the SAME gate. A structural measure that could deny
    on its own would be a second, unarbitrated authority over GLOBAL action -
    precisely the shape Ruling 2 forbids.

    NO SCORING FUNCTION. The conditions below are a boolean OR over named
    structural facts, each one individually legible in `reasons`. Nothing is
    summed, weighted, or multiplied (standing bar 5).

    No delta means no structural evidence, and no evidence means the BASE bar.
    Defaulting to ELEVATED instead would be inventing pressure that no measure
    found - Nova's G1 failure mode, in a different organ.
    """
    if delta is None:
        return TopologyAssessment(
            tier=Tier.ROUTINE,
            reasons=["no topology delta supplied - base threshold applies"],
        )

    before_d, after_d = delta.before(), delta.after()
    before_u, after_u = _undirected(before_d), _undirected(after_d)

    articulation = set(nx.articulation_points(before_u))
    bridges = {frozenset(e) for e in nx.bridges(before_u)}
    core_before, core_after = _core_numbers(before_u), _core_numbers(after_u)
    hubs = _betweenness_hubs(before_u)

    reasons: List[str] = []

    # 1. ARTICULATION POINT removed. Its removal disconnects a component: a
    #    region of the constellation stops being reachable from another.
    cut = sorted(delta.removed_nodes & articulation)
    if cut:
        reasons.append(f"removes articulation point(s): {cut}")

    # 2. BRIDGE severed. The only edge holding two regions together.
    severed = sorted(
        f"{a}->{b}" for (a, b) in delta.removed_edges
        if frozenset((a, b)) in bridges
    )
    if severed:
        reasons.append(f"severs bridge edge(s): {severed}")

    # 3. PROTECTED ANCHOR loses k-core depth. An anchor sitting in a shallower
    #    core is held in place by fewer mutual connections than before.
    dropped: List[str] = []
    for anchor in sorted(delta.protected_anchors):
        if anchor not in core_before:
            continue
        if anchor not in core_after:
            dropped.append(f"{anchor}(removed)")
        elif core_after[anchor] < core_before[anchor]:
            dropped.append(f"{anchor}({core_before[anchor]}->{core_after[anchor]})")
    if dropped:
        reasons.append(f"drops protected anchor k-core: {dropped}")

    # 4. SCC SPLIT. A mutually-reachable region stops being mutually reachable
    #    - a cycle of symbolic reinforcement broken open.
    after_index: Dict[str, int] = {}
    for i, comp in enumerate(_sccs(after_d)):
        for n in comp:
            after_index[n] = i
    split: List[str] = []
    for comp in _sccs(before_d):
        if len(comp) < 2:
            continue
        landing = {after_index[n] for n in comp if n in after_index}
        if len(landing) > 1:
            split.append(str(sorted(comp)))
    if split:
        reasons.append(f"splits strongly-connected component(s): {split}")

    # 5. SCAR -> PROTECTED ANCHOR path SHORTENED.
    #    "Opens a new SHORT path" is stated without a length, and a length is
    #    exactly what this module must not coin. So the condition is a strict
    #    DECREASE in the minimum scar-to-anchor distance, which needs no
    #    magnitude at all: a delta that brings a fracture closer to an anchor
    #    than anything before it did is the thing being guarded against,
    #    whatever the absolute number happens to be. `inf -> finite` (a first
    #    path where none existed) is a decrease and is caught.
    d_before = _min_scar_to_anchor(before_u, delta.scar_nodes, delta.protected_anchors)
    d_after = _min_scar_to_anchor(after_u, delta.scar_nodes, delta.protected_anchors)
    if d_after < d_before:
        shown_b = "none" if d_before == math.inf else int(d_before)
        reasons.append(
            f"shortens scar->protected-anchor path ({shown_b} -> {int(d_after)})"
        )

    # RULING 28 (2026-07-26): BETWEENNESS REPORTS, IT NEVER ELEVATES.
    # DIAGNOSTIC / FORENSIC ONLY. It must never become a tier trigger.
    #
    # The four elevating conditions above are each a DISCRETE STRUCTURAL FACT -
    # an articulation point is removed or it isn't, a bridge is severed or it
    # isn't - checkable with NO magnitude at all. Betweenness is CONTINUOUS, so
    # any trigger built on it needs a cutoff, and that cutoff would be a coined
    # magnitude at this organ's most safety-critical decision. Standing bar 5,
    # refused a third time.
    #
    # REOPENING CONDITION (narrow, and neither half is optional): a cutoff
    # RECOVERED from corpus, or one demonstrated by operational correlation
    # against real lock outcomes. NEVER an invented one, however reasonable it
    # looks in isolation - that is precisely how the last three got proposed.
    hub_removed = sorted(delta.removed_nodes & hubs)

    measures = {
        "articulation_points": sorted(articulation),
        "bridges": sorted(sorted(e) for e in bridges),
        "core_before": dict(sorted(core_before.items())),
        "core_after": dict(sorted(core_after.items())),
        "scc_count_before": len(_sccs(before_d)),
        "scc_count_after": len(_sccs(after_d)),
        "min_scar_anchor_before": d_before,
        "min_scar_anchor_after": d_after,
        "betweenness_hubs": sorted(hubs),
        # RULED (28): reported, NEVER tier-selecting. See the note above.
        "betweenness_hubs_removed": hub_removed,
    }

    if reasons:
        return TopologyAssessment(tier=Tier.ELEVATED, reasons=reasons,
                                  measures=measures)
    return TopologyAssessment(
        tier=Tier.ROUTINE,
        reasons=["no structural condition met - base threshold applies"],
        measures=measures,
    )


def compute_tier(topology_delta: Optional[TopologyDelta]) -> Tier:
    """Ruling 27's stated signature. Thin wrapper - the working lives in
    `assess_topology`, whose `reasons` are what make a tier legible."""
    return assess_topology(topology_delta).tier


# =====================================================================
# TCAML
# =====================================================================

class TCAML:
    """Topological Constellation Anchor & Meta-Layer.

    SOLE WRITER of anchor state (`anchor_state`) and of the GLOBAL lock. Every
    other module ASKS. Reads are free and return SNAPSHOTS (Ruling 22): the
    scar store learned the hard way that a permanence enforced only by
    everyone remembering not to touch it is not permanence, and lock state is
    the one field in this system whose staleness is itself a safety property.
    """

    def __init__(self, health: int = DEFAULT_HEALTH) -> None:
        self._status: Status = Status.HEALTHY
        self._holder: Optional[str] = None
        self._holder_module: Optional[str] = None
        self._held_since: Optional[int] = None
        self._health: int = self._clamp(health)
        self._cycle: int = 0

        # The anchor store. TCAML writes it; nothing else may (Ruling 1).
        self.anchor_state: Dict[str, AnchorState] = {}

        # PARKED (Ruling 15's shape): real forensics, zero effect. See the
        # module docstring - realignment has no corpus-given magnitude.
        self.realignment_requests: List[Dict[str, Any]] = []

        # Append-only forensic surfaces. A denial, an expiry and a revocation
        # are all UNRESOLVED PRESSURE leaving the module; none of them leaves
        # silently (Ruling 23).
        self.lock_denials: List[Dict[str, Any]] = []
        self.lock_expiries: List[Dict[str, Any]] = []
        self.lock_revocations: List[Dict[str, Any]] = []

        # The ordered record of what the LAST `tick()` considered, in the
        # order it considered it. Not test scaffolding: the TTL bound below is
        # a claim about ORDER, and an order nothing can observe is an order
        # nobody can hold the module to.
        self.last_tick_trace: List[Dict[str, Any]] = []

    # -----------------------------------------------------------------
    # READS - free to every module, and they are SNAPSHOTS (Ruling 22)
    # -----------------------------------------------------------------

    @property
    def status(self) -> Status:
        """Read-only. `RACM._meta_unstable()` reads this attribute BY NAME;
        the enum's VALUES match `racm.META_UNSTABLE_STATES` verbatim."""
        return self._status

    @property
    def holder(self) -> Optional[str]:
        return self._holder

    @property
    def holder_module(self) -> Optional[str]:
        return self._holder_module

    @property
    def held_since(self) -> Optional[int]:
        return self._held_since

    @property
    def health(self) -> int:
        return self._health

    @property
    def cycle(self) -> int:
        return self._cycle

    def lock_state(self) -> LockState:
        """A SNAPSHOT of the lock. Mutate it freely; it is a copy."""
        return LockState(
            status=self._status,
            holder=self._holder,
            holder_module=self._holder_module,
            held_since=self._held_since,
            health=self._health,
            cycle=self._cycle,
        )

    def get_anchor_state(self) -> Dict[str, AnchorState]:
        """All anchor records, as DEEP COPIES (Ruling 22)."""
        return {k: copy.deepcopy(v) for k, v in self.anchor_state.items()}

    def get_anchor(self, anchor_id: str) -> Optional[AnchorState]:
        """One anchor record, as a DEEP COPY (Ruling 22)."""
        return copy.deepcopy(self._anchor(anchor_id))

    def _anchor(self, anchor_id: str) -> Optional[AnchorState]:
        """THE LIVE record, for TCAML's OWN write paths only.

        Deliberately private and deliberately separate from `get_anchor`,
        which snapshots. An owner-side method resolving its target through the
        public accessor would mutate a copy and its write would vanish
        SILENTLY - the worst outcome of Ruling 22, and the exact regression
        `ScarLogicCore.decay_scar` had. Do not call this from outside; emit a
        request instead (Ruling 1).
        """
        return self.anchor_state.get(anchor_id)

    # -----------------------------------------------------------------
    # RULE 1 / RULE 2 - THE LOCK
    # -----------------------------------------------------------------

    def lock_request(self, action_id: str, scope: str, module_id: str,
                     topology_delta: Optional[TopologyDelta] = None,
                     tier: Optional[Tier] = None) -> LockResponse:
        """Rule 2: a SYNCHRONOUS grant/deny, decided against live state.

        NEVER a cached answer and never a prior cycle's. There is deliberately
        no memoization here and no "you already hold one, carry on" path: the
        response is to THIS call, at THIS cycle, against THIS status and
        health. A lock granted a moment before instability onset is not still
        valid - that is the whole content of Rule 3.

        Nor is expiry checked here. Force-expiry belongs to `tick()` and to
        `tick()` alone: a second expiry path firing on request arrival is
        exactly the competing-schedule shape that `tcaml_lock.qnt` shows
        loosens the bound (see `tick()`).

        `tier` may be passed explicitly, or DERIVED from `topology_delta` via
        Docket F. Supplying both keeps the explicit one - a caller is allowed
        to know something the delta does not encode - and the derived
        assessment is still recorded on a denial, so a disagreement between
        the two is visible rather than lost.
        """
        assessment = (assess_topology(topology_delta)
                      if topology_delta is not None else None)
        effective_tier = tier if tier is not None else (
            assessment.tier if assessment is not None else Tier.ROUTINE
        )
        examined = assessment is not None
        # Ruling 27 confirmation: an UNEXAMINED request never reads like an
        # examined-and-cleared one. See UNEXAMINED_DELTA_NOTE.
        delta_note = "" if examined else f"; {UNEXAMINED_DELTA_NOTE}"

        # RULE 1: LOCAL requires no lock check. No state is touched, health and
        # status are not consulted, and no record is written - there is nothing
        # unresolved about a request that never needed adjudicating.
        if scope == Scope.LOCAL.value or scope is Scope.LOCAL:
            return LockResponse(
                granted=True,
                action_id=action_id,
                reason="LOCAL scope requires no TCAML lock (Rule 1)",
                scope=Scope.LOCAL,
                tier=None,
                cycle=self._cycle,
            )

        threshold = (ELEVATED_THRESHOLD if effective_tier is Tier.ELEVATED
                     else ROUTINE_THRESHOLD)

        # RULE 3 first: instability locks out GLOBAL action outright.
        if self._status is not Status.HEALTHY:
            return self._deny(
                action_id, module_id, effective_tier, assessment, examined,
                f"TCAML meta-unstable ({self._status.value}) - "
                f"GLOBAL action locked out (Rule 3){delta_note}",
            )

        if self._holder is not None:
            return self._deny(
                action_id, module_id, effective_tier, assessment, examined,
                f"GLOBAL lock already held by '{self._holder}' "
                f"(module '{self._holder_module}', since cycle "
                f"{self._held_since}){delta_note}",
            )

        if self._health < threshold:
            return self._deny(
                action_id, module_id, effective_tier, assessment, examined,
                f"health {self._health} below {effective_tier.value} "
                f"threshold {threshold}{delta_note}",
            )

        self._holder = action_id
        self._holder_module = module_id
        self._held_since = self._cycle
        return LockResponse(
            granted=True,
            action_id=action_id,
            reason=(f"granted at cycle {self._cycle}: healthy, unheld, "
                    f"health {self._health} >= {effective_tier.value} "
                    f"threshold {threshold}{delta_note}"),
            scope=Scope.GLOBAL,
            tier=effective_tier,
            cycle=self._cycle,
            delta_examined=examined,
        )

    def _deny(self, action_id: str, module_id: str, tier: Tier,
              assessment: Optional[TopologyAssessment], examined: bool,
              reason: str) -> LockResponse:
        """Ruling 23: unresolved pressure never leaves silently. A denial is a
        request that could not be met, and it lands on a legible surface
        carrying WHICH condition failed."""
        self.lock_denials.append({
            "action_id": action_id,
            "module_id": module_id,
            "cycle": self._cycle,
            "tier": tier.value,
            "status": self._status.value,
            "health": self._health,
            "holder": self._holder,
            "reason": reason,
            "delta_examined": examined,
            "structural_reasons": list(assessment.reasons) if assessment else [],
            "at": datetime.now().isoformat(timespec="seconds"),
        })
        return LockResponse(
            granted=False,
            action_id=action_id,
            reason=reason,
            scope=Scope.GLOBAL,
            tier=tier,
            cycle=self._cycle,
            delta_examined=examined,
        )

    def release(self, action_id: str, module_id: str) -> None:
        """Only the CURRENT holder may release.

        A release from a non-holder RAISES (Ruling 25's discipline: a guard
        whose firing looks like a typo is not enforcement).

        RULING 29 - WHICH raise depends on WHY, and the two causes are
        opposite:

          StaleLockRelease      TCAML TOOK the lock (revoked by instability
                                onset, or force-expired at TTL). SYSTEM
                                action; this caller is BLAMELESS and is being
                                informed of something done TO it. The message
                                names which of the two happened.

          LockReleaseViolation  the caller NEVER HELD it. CALLER error; an
                                upstream gate already failed.

        One type for both would be Ruling 25's defect one level down - a
        forensic record that cannot tell you whether to go fix the caller or
        go look at what destabilised the constellation.
        """
        if (self._holder is not None
                and self._holder == action_id
                and self._holder_module == module_id):
            self._clear_holder()
            return

        stale = self._stale_record(action_id, module_id)
        if stale is not None:
            raise StaleLockRelease(
                f"'{module_id}' released GLOBAL lock for action '{action_id}', "
                f"but TCAML had already {stale['event']} it at cycle "
                f"{stale['cycle']} ({stale['reason']}). The operation was "
                f"INTERRUPTED, not completed - this caller did nothing wrong. "
                f"The lock is now held by {self._describe_holder()}."
            )
        raise LockReleaseViolation(
            f"'{module_id}' released GLOBAL lock for action '{action_id}' "
            f"but never held it. The lock is held by {self._describe_holder()}. "
            f"No revocation or expiry is recorded for that action/module pair."
        )

    def _stale_record(self, action_id: str,
                      module_id: str) -> Optional[Dict[str, Any]]:
        """The revocation/expiry that took THIS caller's lock, if any.

        Matches on the (action_id, module_id) PAIR, not action_id alone. A
        different module releasing someone else's revoked lock never held it
        either - that is caller error, and widening this match would let a
        genuine ownership confusion hide behind a blameless exception type.
        """
        for record in reversed(self.lock_revocations):
            if record["action_id"] == action_id and record["module_id"] == module_id:
                return {"event": "REVOKED", "cycle": record["cycle"],
                        "reason": f"{record['reason']} -> {record['new_status']}"}
        for record in reversed(self.lock_expiries):
            if record["action_id"] == action_id and record["module_id"] == module_id:
                return {"event": "FORCE-EXPIRED", "cycle": record["cycle"],
                        "reason": f"held {record['held_cycles']} cycles, TTL {TTL}"}
        return None

    def _describe_holder(self) -> str:
        if self._holder is None:
            return "NOBODY"
        return f"'{self._holder}' (module '{self._holder_module}')"

    def _clear_holder(self) -> None:
        self._holder = None
        self._holder_module = None
        self._held_since = None

    # -----------------------------------------------------------------
    # CYCLE ADVANCE - THE ORDERING HERE IS LOAD-BEARING
    # -----------------------------------------------------------------

    # The GLOBAL housekeeping pipeline, in the order `tick()` runs it. TTL
    # expiry is FIRST and stays first; see `tick()` for why. A new housekeeping
    # duty joins this tuple deliberately, and BELOW expiry.
    HOUSEKEEPING_ORDER: Tuple[str, ...] = ("ttl_expiry", "stability_recovery")

    def tick(self) -> List[Dict[str, Any]]:
        """Advance one cycle and run GLOBAL housekeeping IN A FIXED ORDER.

        =============================================================
        WHY TTL EXPIRY IS CHECKED FIRST, AND WHY IT MUST STAY FIRST
        =============================================================
        This ordering is a MODEL-CHECKED FINDING, not a style preference. It
        will look like an arbitrary sequence to whoever reads it next, so:

          docs/formal/tcaml_lock/tcaml_lock.qnt
              TTL expiry competes as ONE nondeterministic option among the
              other GLOBAL housekeeping actions. `boundedHoldUnderScheduling`
              holds only with +3 SLACK: the hold duration DRIFTS PAST TTL,
              because "expiry is enabled" and "expiry is scheduled" are not
              the same thing. The bound is empirical, not exact.

          docs/formal/tcaml_lock/tcaml_lock_priority.qnt
              Identical, except expiry PREEMPTS every other GLOBAL
              housekeeping action once due. `boundedHoldTight` then holds with
              ZERO SLACK - the exact `cycle - held_since <= TTL` bound.

        So `TTL = 5` alone bounds nothing tightly. TTL=5 PLUS scheduling
        priority is what makes the stated bound real. Reorder this and the
        constant stays 5 while the guarantee quietly becomes "about 5" - the
        kind of regression that passes review precisely because the number
        was not touched.

        Expiry is also checked AFTER the cycle increments, against the NEW
        cycle. Checking it first would expire one cycle late, for the same
        reason and with the same invisibility.
        """
        self._cycle += 1
        self.last_tick_trace = []

        # STEP 1 of HOUSEKEEPING_ORDER - PREEMPTS everything below it.
        expired = self._expire_if_due()
        self.last_tick_trace.append({"step": "ttl_expiry", "acted": expired})

        # STEP 2 - ordinary GLOBAL housekeeping, strictly after expiry.
        recovered = self._recover_if_able()
        self.last_tick_trace.append({"step": "stability_recovery",
                                     "acted": recovered})

        assert self._hold_within_bound(), (
            "TTL bound violated: a GLOBAL lock is held longer than TTL cycles. "
            "This is `boundedHoldTight` from tcaml_lock_priority.qnt failing at "
            "runtime."
        )
        return list(self.last_tick_trace)

    def _hold_within_bound(self) -> bool:
        """`boundedHoldTight`: holder != none implies cycle - held_since <= TTL."""
        if self._holder is None or self._held_since is None:
            return True
        return (self._cycle - self._held_since) <= TTL

    def _expire_if_due(self) -> bool:
        """Force-expire an orphaned lock at the TTL bound.

        A holder that crashed, or that simply never released, must not be able
        to freeze GLOBAL action forever. Force-expiry is not a punishment and
        not a verdict on the holder - it is what makes the lock a BOUNDED
        claim rather than an open-ended one.
        """
        if self._holder is None or self._held_since is None:
            return False
        held = self._cycle - self._held_since
        if held < TTL:
            return False
        self.lock_expiries.append({
            "action_id": self._holder,
            "module_id": self._holder_module,
            "held_since": self._held_since,
            "cycle": self._cycle,
            "held_cycles": held,
            "reason": f"TTL {TTL} reached - orphaned GLOBAL lock force-expired",
            "at": datetime.now().isoformat(timespec="seconds"),
        })
        self._clear_holder()
        return True

    def _recover_if_able(self) -> bool:
        """Leave META_UNSTABLE / REPAIR_CYCLE once health permits."""
        if self._status is Status.HEALTHY:
            return False
        if self._health < RECOVERY_THRESHOLD:
            return False
        self._status = Status.HEALTHY
        return True

    # -----------------------------------------------------------------
    # RULE 3 - META-INSTABILITY REVOKES
    # -----------------------------------------------------------------

    def enter_meta_unstable(self, reason: str = "meta-instability onset") -> None:
        self._enter_instability(Status.META_UNSTABLE, reason)

    def enter_repair_cycle(self, reason: str = "repair cycle entered") -> None:
        self._enter_instability(Status.REPAIR_CYCLE, reason)

    def _enter_instability(self, status: Status, reason: str) -> None:
        """Onset REVOKES a held lock IN THE SAME TRANSITION.

        =============================================================
        THIS IS THE MODEL-CHECKED HALF OF RULE 3. DO NOT WEAKEN IT.
        =============================================================
        The weaker reading - "instability blocks NEW GLOBAL requests but leaves
        an existing hold alone" - is modelled in
        `docs/formal/tcaml_lock/tcaml_lock_naive.qnt`, and it FAILS
        `noGrantDuringInstability` IN TWO STEPS. The counterexample is in that
        directory's README verbatim:

            [State 1] holder: "doctrineRemap", status: Healthy
            [State 2] holder: "doctrineRemap", status: MetaUnstable
            [violation] noGrantDuringInstability

        A GLOBAL mutation is then in flight DURING the exact state Rule 3
        exists to lock out. Blocking future requests does not help: the
        dangerous operation is already running. If clearing the holder here
        ever looks over-eager, run that file before changing it.

        FLAGGED (Ruling 27, open question 1): this INTERRUPTS an in-flight
        GLOBAL operation. Safe today only because nothing downstream is
        durable. When a persistence contract lands, an interrupted operation
        needs a defined abandoned state, not just disappearance.
        """
        if status is Status.HEALTHY:
            raise ValueError("_enter_instability is not a path back to HEALTHY")
        revoked = self._holder
        if revoked is not None:
            self.lock_revocations.append({
                "action_id": revoked,
                "module_id": self._holder_module,
                "held_since": self._held_since,
                "cycle": self._cycle,
                "new_status": status.value,
                "reason": reason,
                "at": datetime.now().isoformat(timespec="seconds"),
            })
        self._status = status
        self._clear_holder()

    # -----------------------------------------------------------------
    # ANCHOR STATE - TCAML executes; CSE asks (Ruling 1)
    # -----------------------------------------------------------------

    def anchor_feedback_update(self, anchor_id: str, drift_amount: float) -> None:
        """CSE reports measured drift; TCAML records it.

        CSE MEASURES and TCAML OWNS. Nothing is computed from `drift_amount`
        here - it is stored as reported. The moment this method starts
        deriving a correction from that number, TCAML has coined a magnitude
        for realignment, which is the one thing the module docstring forbids.
        """
        record = self._anchor(anchor_id)   # Ruling 22: the owner writes the LIVE record
        if record is None:
            record = AnchorState(anchor_id=anchor_id)
            self.anchor_state[anchor_id] = record
        record.last_reported_drift = float(drift_amount)
        record.last_reported_cycle = self._cycle
        record.reports += 1

    def trigger_anchor_realignment(self, anchor_id: str) -> None:
        """PARKED (Ruling 15's shape): recorded REQUEST, no corrective effect.

        Realignment means moving an orientation reference, and the corpus
        gives neither magnitude nor target for that move. Coining one would
        let TCAML quietly redefine which way "true" points - silently, at the
        exact site CLAUDE.md 3 records as having nearly struck her mute
        once already. The requests accumulate legibly until ruled.
        """
        record = self._anchor(anchor_id)
        if record is None:
            record = AnchorState(anchor_id=anchor_id)
            self.anchor_state[anchor_id] = record
        record.realignments_requested += 1
        self.realignment_requests.append({
            "anchor_id": anchor_id,
            "cycle": self._cycle,
            "last_reported_drift": record.last_reported_drift,
            "state": "PARKED - no realignment magnitude is ruled",
            "at": datetime.now().isoformat(timespec="seconds"),
        })

    # -----------------------------------------------------------------
    # CONSTELLATION HEALTH INDEX - AWAITING ITS OWN RULING
    # -----------------------------------------------------------------

    @staticmethod
    def _clamp(value: int) -> int:
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("health must be finite")
        return int(max(HEALTH_FLOOR, min(HEALTH_CEILING, numeric)))

    def set_health(self, value: int) -> None:
        """Set the Constellation Health Index directly.

        THIS IS NOT A COMPUTATION AND MUST NOT BECOME ONE. The corpus names
        five inputs (anchor drift, scar bloom density, fragmentation,
        dead-zone index, meta-stability) and gives no combination rule. A
        weighted average would be a COINED magnitude at the most
        safety-critical site in this organ - the number deciding whether a
        system-wide mutation may proceed. Stage 1 keeps the field honest and
        settable and leaves the formula to its own ruling.
        """
        self._health = self._clamp(value)
