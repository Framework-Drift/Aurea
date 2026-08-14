"""
racm.py - RACM v2.0: Reflex Arbitration & Collapse Monitor (memory-linked)

Canon: 2b_Collapse_Reflex_Engine.txt, "/// MODULE: RACM v2.0 ///"

AUTHORITY (integration_review Ruling 2, 2026-07-09)
--------------------------------------------------
RACM is the SOLE ARBITER of reflex priority, suppression, deferral, and lockout.
The EchoCore Reflex Grid is the reflex REGISTRY/HOUSING - it enumerates and routes
reflexes; it performs no adjudication of its own.

    Reflexes fire FROM the Grid. Which one wins is decided ONLY here.

Authority is one-way: the arbiter never originates a reflex, and the source never
adjudicates. RACM therefore contains no reflex logic - it never calls .trigger().
It returns a verdict set; the Grid executes it.

DEPENDENCY DIRECTION: reflex_grid -> racm. RACM imports nothing from the Grid at
runtime (that would re-couple arbiter to source and reintroduce the cycle).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Protocol

from src.utils.atomic_write import atomic_write_json
from src.utils.continuity import LoadReport, RestorationOutcome

from src.reflex.rb_system import BehaviorType, RBSystem
# DEPENDENCY DIRECTION: racm -> tcaml. `tcaml.py` imports networkx and the
# stdlib only - nothing from AUREA - so this cannot cycle. TCAML is the LOCK
# OWNER; RACM is a requester holding no lock state of its own (Ruling 2's
# shape, one layer out: the arbiter of reflexes is not the owner of topology).
from src.topology.tcaml import TCAML, LockClass, StaleLockRelease


# =====================================================================
# CANON CONSTANTS (2b - Priority Table, Modifiers, Overflow & Deferral)
# =====================================================================

# Priority Table - Symbolic Reflex Ranking. Rank 1 = most urgent.
CANONICAL_PRIORITY: Dict[str, int] = {
    "GSR": 1,                          # Global Integrity Lock
    "ICA": 2,                          # Internal Collapse Awareness
    "DRPE": 3,                         # Doctrine Re-Pressure Event
    "ANCHOR_COLLAPSE": 4,              # Anchor Collapse Reflex
    "WHISPER": 5,                      # Whisper Reflex  (identity modulation)
    "PSI": 5,                          # PSI Reflex      (same rank, canon pairs them)
    "RLB": 6,                          # Recursive Loop Brake (cycle delay)
    "NOVA_FERMENTATION_THROTTLE": 7,
    "SPS": 8,                          # SPS Prompt Trigger
    "SEP_ACTIVATION_SCANNER": 9,
    "TETHER_PROMPT_THROTTLE": 10,
    "RIL_FRAGMENT_SUPPRESSOR": 11,
}

# COINED (not recovered from corpus): a reflex not in the Priority Table ranks
# below every ranked reflex. The canon table is closed at 11; anything unranked
# is by construction not load-bearing enough to preempt a ranked reflex.
UNRANKED_RANK = 12

# Overflow & Deferral Policy (2b, item #49)
QUEUE_MAX = 11          # policy 3: one slot per reflex type -> depth <= 11 by construction
TTL_CYCLES = 5          # policy 4: 5 symbolic cycles (adopted magnitude, LESL/SESL horizon)
AGING_PER_CYCLE = 1     # policy 4: +1 effective priority per deferred cycle...
AGING_CAP = 2           # ...capped at +2 (existing maximum modifier magnitude)

# Modifiers (2b, Priority Table). Positive = MORE urgent = lower rank number.
MOD_FOSSIL_LINKED = 1       # +1 if SMC references (x) or fossil-linked doctrine
MOD_FAILED_NOVA_LINEAGE = 2 # +2 if echo source matches failed Nova lineage
MOD_LESL_SESL_CLEAN = -1    # -1 if doctrine passed LESL + SESL screening in last 5 cycles

# Exemptions (policy 6)
NEVER_QUEUED = frozenset({"GSR", "RLB"})   # GSR preempts; RLB throttles the queue itself
NEVER_EXPIRES = frozenset({"GSR"})

# Deadlock Detection (Core Function 3): incompatible simultaneous trigger sets.
DEADLOCK_SETS: List[FrozenSet[str]] = [frozenset({"DRPE", "ICA", "GSR"})]

# EscalationLogic (2b)
ESCALATION_REFLEX_COUNT = 3     # reflexes_fired >= 3 ...
ESCALATION_COMPASS_DRIFT = 20.0 # ... and compass_drift > 20 degrees
MUTATION_ABORT_SET = frozenset({"DRPE", "ICA", "WHISPER"})
META_UNSTABLE_STATES = frozenset({"meta-unstable", "repair_cycle"})


class Scope(Enum):
    """A reflex's DURABILITY + BREADTH scope. NOT the lock axis (Ruling 30).

    Two live meanings, both about the REFLEX:
      * DURABILITY (Ruling 11) - `_log_execution` sets
        `durable=(reflex.scope == Scope.GLOBAL)`, so a GLOBAL reflex's RB
        entries flush to disk immediately. UNTOUCHED by Ruling 30.
      * BREADTH (Overflow Policy 2) - a GLOBAL-scope executor affects
        everything, so nothing runs alongside it in the compatibility
        partition.

    IT IS NOT, AND NEVER WAS, THE LOCK AXIS. Until Ruling 30 this value was
    passed to `TCAML.lock_request`, which wants the ACTION's structural class
    (`tcaml.LockClass`). Same two words, different concept: GSR is GLOBAL for
    durability and breadth, and its action - suppression - is not structural.
    That conflation is what disarmed GSR during meta-instability. `LockClass`
    shares neither type nor member names with this enum, so the mistake now
    raises instead of locking the wrong thing.
    """
    LOCAL = "LOCAL"
    GLOBAL = "GLOBAL"


class Verdict(Enum):
    """RACM's decision on one reflex in one cycle. `DEFERRED` is a distinct
    readable state from suppressed/lockout (policy 8) - modules gating on RACM
    state treat deferred reflexes as PENDING, not prohibited."""
    EXECUTE = "execute"
    DEFERRED = "deferred"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"
    LOCK_DENIED = "lock_denied"


class TCAMLPort(Protocol):
    """The only surface RACM needs from the topology layer.

    `lock_request` returns a `LockResponse`, whose `__bool__` is `granted` -
    so `if not grant:` below reads correctly. That is not an accident of the
    dataclass: an always-truthy return would have made RACM read every DENIAL
    as a GRANT, a fail-open on the system-wide integrity lock. It is pinned on
    the TCAML side.
    """
    status: str
    def lock_request(self, action_id: str, lock_class: LockClass,
                     module_id: str) -> Any: ...
    def release(self, action_id: str, module_id: str) -> None: ...


@dataclass
class ReflexClaim:
    """A reflex's CLAIM to execute this cycle. Built by the Grid (the source),
    judged by RACM (the arbiter). Carries no reflex logic - RACM never runs it."""
    reflex_id: str
    pressure_level: float = 0.0
    scope: Scope = Scope.LOCAL
    # RULING 30: the ACTION's structural class - the ONLY thing that may reach
    # `TCAML.lock_request`. Separate from `scope` above by type AND by name,
    # because they are separate concepts that shared a vocabulary.
    #
    # DEFAULT NON_STRUCTURAL, AND NOTHING SETS IT OTHERWISE TODAY. No reflex
    # action is structural: reflexes suppress, defer, cascade, monitor - none
    # of which appear in the corpus's GLOBAL list (expansion, mutation,
    # registration, topology change, doctrine-spine write). This RESTORES the
    # Quint model's own clientele: `ACTORS = {mspInstall, doctrineRemap}`.
    # Reflexes were never modeled as lock clients; the code matched the
    # model's mechanism while feeding it the wrong callers.
    lock_class: LockClass = LockClass.NON_STRUCTURAL
    affected_systems: FrozenSet[str] = frozenset()
    source_module: str = ""
    # Modifier context, supplied by the Grid from SMC / EchoTrace lookups.
    fossil_linked: bool = False
    failed_nova_lineage: bool = False
    lesl_sesl_clean: bool = False
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def base_rank(self) -> int:
        return CANONICAL_PRIORITY.get(self.reflex_id.upper(), UNRANKED_RANK)


class ReasonCode(str, Enum):
    """WHY a claim landed where it did, as a stable machine-readable token.

    OBSERVABILITY ONLY (§8 step 6b). These codes describe decisions RACM was
    ALREADY making; not one of them participates in making a decision. The
    `reason` prose stays exactly as it was - this is a parallel channel, not a
    replacement, because the prose is what a human reads in a forensic log and
    the code is what a query filters on.

    This is NOT a typed-preference algebra over RACM - that is REJECTED (§9).
    Nothing here is compared, ordered, or summed. A ReasonCode never reaches
    `_rank_key`.
    """
    WON_PRIORITY = "won_priority"            # highest effective rank
    COMPATIBLE_PASSENGER = "compatible_passenger"   # LOCAL, disjoint systems
    LOST_CONTENTION = "lost_contention"      # deferred: outranked this cycle
    QUEUE_EXEMPT = "queue_exempt"            # suppressed: may not queue (policy 6)
    TTL_EXHAUSTED = "ttl_exhausted"          # expired out of the deferral queue
    LOCK_DENIED = "lock_denied"              # TCAML refused the GLOBAL lock


@dataclass
class Decision:
    reflex_id: str
    verdict: Verdict
    effective_rank: float
    reason: str = ""
    deferred_cycles: int = 0
    ttl_remaining: int = TTL_CYCLES
    rb_entry_id: Optional[str] = None
    # ---- observability sliver (§8 step 6b, 2026-07-26) -------------------
    # ADDITIVE ONLY. Every field below defaults to empty, no existing field
    # changed meaning, and no verdict differs before or after - pinned by a
    # full before/after verdict dump across nine arbitration scenarios.
    reason_code: Optional[ReasonCode] = None
    # The claims that actually stood in this one's way. Answers "who beat me?"
    # without re-deriving it from rank arithmetic after the fact.
    blocking_claims: List[str] = field(default_factory=list)
    # The specific conditions this claim failed, one string each - the same
    # legibility Ruling 23 required of a refusal, applied to a non-execution.
    failed_conditions: List[str] = field(default_factory=list)


@dataclass
class ArbitrationResult:
    cycle: int
    reflexes_fired: int              # policy 1: TRIGGERED, not executed
    execute: List[ReflexClaim] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    deadlock: bool = False
    escalations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def verdict_for(self, reflex_id: str) -> Optional[Verdict]:
        for d in self.decisions:
            if d.reflex_id == reflex_id:
                return d.verdict
        return None


@dataclass
class _QueuedClaim:
    """One deferral-queue slot. ONE SLOT PER REFLEX TYPE (policy 3) - a
    re-trigger refreshes conditions, it never adds a slot."""
    claim: ReflexClaim
    deferred_cycles: int = 0
    ttl_remaining: int = TTL_CYCLES


class RACM:
    """Reflex Arbitration & Collapse Monitor - the sole arbiter.

    Not a reflex. Not a source. It resolves competing reflex chains, assigns
    symbolic priority, prevents deadlock, and preserves doctrinal integrity
    during collapse.
    """

    STATE_VERSION = 1

    def __init__(self, rb_system: Optional[RBSystem] = None,
                 tcaml: Optional[TCAMLPort] = None,
                 smc: Any = None,
                 runtime_path: str = "data/runtime/racm_queue.json",
                 obligation_ledger: Any = None):
        # Ruling 42 / Ruling 39: an `__init__` DEFAULT under `data/runtime/`,
        # redirected by name in `tests/conftest.py`. SAE's shape.
        self.runtime_path = Path(runtime_path)
        self.rb = rb_system or RBSystem()
        # TCAML Stage 2 (2026-07-26): the lock owner is now ALWAYS present.
        # `tcaml or TCAML()` follows this constructor's own existing idiom
        # (`rb_system or RBSystem()`), and it is what let the build-stage
        # default-grant branch in `_request_lock` be DELETED rather than
        # softened: there is no "TCAML absent" state left to special-case.
        # AureaCore constructs ONE instance and threads it through the Grid so
        # the whole pipeline shares a single lock; a bare RACM() still gets a
        # working one instead of an ungated GLOBAL path.
        self.tcaml: TCAMLPort = tcaml or TCAML()
        self.smc = smc                              # Collapse Context Awareness source
        self.cycle = 0
        self._queue: Dict[str, _QueuedClaim] = {}   # reflex_id -> slot; depth <= QUEUE_MAX
        self.last_result: Optional[ArbitrationResult] = None
        self.echotrace_signatures: List[Dict[str, Any]] = []  # policy 5: expiry is never silent
        # Ruling 29: a release TCAML had already revoked/expired. Recorded
        # rather than raised ONLY because the Grid releases from a `finally`
        # (see release_lock). Empty in a healthy system.
        self.stale_lock_releases: List[Dict[str, Any]] = []
        # A GLOBAL lock RACM still held entering a new cycle - i.e. a release
        # that never ran. See _sweep_own_stale_lock. Empty in a healthy system.
        self.self_lock_sweeps: List[Dict[str, Any]] = []
        # Observability sliver: who executed this cycle, for annotating the
        # claims that did not. Written after grants are final; read by nothing
        # that decides anything.
        self._blocked_by: List[str] = []

        # Ruling 42 taxonomy + best-effort persistence (Ruling 11's shape).
        self.load_report: Optional[LoadReport] = None
        self.persist_failures: List[Dict[str, Any]] = []
        # M3-D §1.3 - THE ADMISSION SEAM. K2's ledger, held as a REQUESTER.
        # `None` is the honest default: a bare RACM admits nothing.
        self.obligation_ledger = obligation_ledger
        # Ruling 11's shape again: an admission failure is RECORDED, never
        # raised, so it can never gate the protective record it accompanies.
        self.admission_failures: List[Dict[str, Any]] = []
        # Ruling 23's word, applied to a boundary rather than a queue cap:
        # UNRESOLVED PRESSURE NEVER LEAVES SILENTLY. A queue that could not be
        # restored is a DECLARED LOSS, recorded here and on the RB channel.
        self.declared_losses: List[Dict[str, Any]] = []

        self.load()

    # -- state legibility (policy 8) --------------------------------------

    @property
    def deferred(self) -> List[str]:
        return list(self._queue.keys())

    def is_deferred(self, reflex_id: str) -> bool:
        return reflex_id in self._queue

    def status(self) -> Dict[str, Any]:
        return {
            "cycle": self.cycle,
            "queue_depth": len(self._queue),
            "queue_max": QUEUE_MAX,
            "deferred": {
                rid: {"deferred_cycles": q.deferred_cycles, "ttl_remaining": q.ttl_remaining}
                for rid, q in self._queue.items()
            },
            "last_cycle_executed": (
                [c.reflex_id for c in self.last_result.execute] if self.last_result else []
            ),
        }

    # =================================================================
    # THE ARBITRATION ENTRY POINT
    # =================================================================

    def arbitrate(self, claims: List[ReflexClaim],
                  context: Optional[Dict[str, Any]] = None) -> ArbitrationResult:
        """Resolve one symbolic cycle's contention. The Grid submits every reflex
        that triggered; RACM returns which ones execute and what happens to the rest.

        Order is canon-fixed:
          1. age the deferral queue (TTL / aging) and expire what timed out
          2. registration is total - queued + new claims form the arbitration set
          3. meta-instability override (TCAML)
          4. rank by effective priority (base rank - modifiers - aging)
          5. deadlock detection
          6. compatibility partition - who else may execute alongside the winner
          7. TCAML two-phase lock for GLOBAL-scope executors
          8. defer / suppress the rest
          9. escalation checks
        """
        self.cycle += 1
        ctx = context or {}
        result = ArbitrationResult(cycle=self.cycle, reflexes_fired=0)

        # 0. RACM NEVER ENTERS A NEW CYCLE STILL HOLDING THE LAST ONE'S LOCK.
        self._sweep_own_stale_lock()

        # 1. Age the queue first, so an expiry this cycle is not silently
        #    overwritten by a same-cycle re-trigger.
        self._age_queue(result)

        # 2. Registration is total (policy 1): reflexes_fired counts TRIGGERED,
        #    not executed. EscalationLogic and ReflexBehaviorLogTrigger both key
        #    off this count.
        arbitration_set = self._merge_with_queue(claims)
        result.reflexes_fired = len(arbitration_set)
        if not arbitration_set:
            self.last_result = result
            self._persist()
            return result

        # 3. Meta-instability override (2b, Rule 3): a GLOBAL grant issued a
        #    moment before instability onset is not treated as still valid.
        if self._meta_unstable():
            for claim in arbitration_set:
                # COINED: GSR is exempt. It is the Global Integrity Lock; suppressing
                # it during meta-instability would disarm the reflex that exists FOR
                # instability. Canon exempts GSR from queueing/expiry but does not
                # state this case explicitly.
                if claim.reflex_id == "GSR":
                    continue
                self._suppress(claim, result, "TCAML meta-instability override")
            arbitration_set = [c for c in arbitration_set if c.reflex_id == "GSR"]
            if not arbitration_set:
                self.last_result = result
                return result

        # 4. Effective ranking. Secondary key: DEFERRED WINS TIES (Ruling 9 pt.3,
        #    canonized 2026-07-20). A claim that already lost a cycle outranks an
        #    equal-ranked fresh claim - older deferrals first among those. This was
        #    previously emergent from _merge_with_queue's queue-first insertion order
        #    + stable sort; the explicit key makes it survive any refactor of that
        #    ordering.
        ranked = sorted(arbitration_set, key=self._rank_key)

        # 5. Deadlock detection (Core Function 3). Detection does not halt
        #    resolution - it escalates alongside it (see canon's worked example,
        #    where GSR still wins the chain).
        fired_ids = {c.reflex_id for c in arbitration_set}
        for dset in DEADLOCK_SETS:
            if dset <= fired_ids:
                result.deadlock = True
                result.escalations.append(
                    f"deadlock: incompatible simultaneous set {sorted(dset)} "
                    f"-> Delay Pathway / CSA"
                )

        # 6. Compatibility partition (policy 2).
        winner = ranked[0]
        executing: List[ReflexClaim] = [winner]
        claimed_systems = set(winner.affected_systems)

        # A GLOBAL-scope executor affects EVERYTHING, so nothing runs alongside
        # it. Set-disjointness alone does not catch that (a GLOBAL reflex's
        # affected-system set does not textually intersect a LOCAL one) - the
        # partition must be scope-gated first. A non-winning GLOBAL claim is
        # likewise never a passenger: its breadth cannot be reconciled with
        # another reflex executing at the same time. It defers.
        #
        # RULING 30 CORRECTED THIS RATIONALE, NOT THIS BEHAVIOR. It used to
        # read "a GLOBAL-scope executor holds a system-wide lock" - which is
        # now false: no reflex claim requests the lock. The partition is
        # correct on BREADTH grounds alone, which is what it always actually
        # measured. This is `Scope`'s THIRD live sense (durability, breadth,
        # and - wrongly - lock class); Ruling 30 removed only the third.
        # Re-keying the partition would change arbitration verdicts, which this
        # pass is explicitly not permitted to do.
        if winner.scope is not Scope.GLOBAL:
            for claim in ranked[1:]:
                compatible = (
                    claim.scope is Scope.LOCAL
                    and not (set(claim.affected_systems) & claimed_systems)
                )
                if compatible:
                    executing.append(claim)
                    claimed_systems |= set(claim.affected_systems)

        # 7. TCAML two-phase lock for STRUCTURAL claims (Rule 2).
        #
        # RULING 30: keyed on the ACTION's structural class, NOT on the
        # reflex's durability/breadth scope. This line used to read
        # `claim.scope is Scope.GLOBAL`, which sent every system-wide
        # SUPPRESSION to the lock - and then Rule 3 denied it during exactly
        # the instability it exists to answer.
        #
        # NO REFLEX SETS `lock_class` TODAY, so in practice this branch does
        # not fire and no reflex claim requests the lock. That is the ruling,
        # not a shortcut: reflexes suppress, defer, cascade and monitor, and
        # none of those is expansion, mutation, registration, topology change
        # or a doctrine-spine write. AWAITING ITS STRUCTURAL CLIENTS - MSP
        # install and doctrine remap, the Quint model's own `ACTORS`. The
        # lifecycle below (grant, Grid release, self-sweep, stale records) is
        # NOT DEAD CODE; it is the contract those clients will arrive into,
        # and it is exercised by tests that declare a structural claim.
        granted: List[ReflexClaim] = []
        for claim in executing:
            if claim.lock_class is LockClass.STRUCTURAL \
                    and not self._request_lock(claim, result):
                continue
            granted.append(claim)
            self._clear_slot(claim.reflex_id)
            result.decisions.append(Decision(
                reflex_id=claim.reflex_id,
                verdict=Verdict.EXECUTE,
                effective_rank=self._effective_rank(claim),
                reason="highest priority" if claim is winner else "compatible (LOCAL, disjoint)",
                reason_code=(ReasonCode.WON_PRIORITY if claim is winner
                             else ReasonCode.COMPATIBLE_PASSENGER),
            ))
        result.execute = granted

        # Observability sliver: WHO stood in the way of everything that did not
        # run this cycle. Computed AFTER `granted` is final and read by nothing
        # in this method - it annotates the outcome, it does not shape it.
        self._blocked_by = [c.reflex_id for c in granted]

        # 8. Everything else: defer (or suppress, if exempt from queueing).
        executed_ids = {c.reflex_id for c in executing}
        for claim in ranked:
            if claim.reflex_id in executed_ids:
                continue
            if claim.reflex_id in NEVER_QUEUED:
                # COINED consequence of policy 6: RLB may not enter the queue it
                # governs, so a non-executing RLB is suppressed-and-logged rather
                # than deferred. (GSR cannot reach this branch - rank 1 always wins.)
                self._suppress(claim, result, "queue-exempt reflex did not execute")
            else:
                self._defer(claim, result)

        # 9. Escalation.
        self._check_escalations(result, fired_ids, ctx)

        self.last_result = result
        # Ruling 42 res.3: the queue and the cycle counter leave this method in
        # step, so they are written in the SAME SNAPSHOT. `deferred_cycles` and
        # `ttl_remaining` are RELATIVE counters - meaningless without the clock
        # they were counted against - and persisting them apart from `cycle`
        # would restore ages measured against a clock that no longer exists.
        self._persist()
        return result

    # =================================================================
    # CONTINUITY (Ruling 42) - deferred pressure survives the boundary
    # =================================================================

    def save(self) -> None:
        """Whole-file snapshot. Ruling 32's minimal semantics VERBATIM.

        WHAT ROUND-TRIPS: `cycle`, and every deferral slot as
        (serialized `ReflexClaim`, `deferred_cycles`, `ttl_remaining`).

        CLOCK COHERENCE IS LOCAL, AND DELIBERATELY SO. The two ages are RELATIVE
        counters and `cycle` is written in the SAME snapshot, so a restored slot's
        age is still measured against the clock it was counted against. No GLOBAL
        symbolic ordinal exists anywhere in this system, and none is invented here
        - inventing one would be a coined magnitude at the boundary between
        arbitration and time.

        REPORTED-NOT-PERSISTED, each for the same reason - they describe the
        CYCLE JUST ENDED, not pressure still owed, and a restored copy would be a
        record of events from a process that no longer exists:
          * `echotrace_signatures` - expiry signatures bound for EchoTrace (unbuilt)
          * `stale_lock_releases`  - Ruling 29 observations of a lock TCAML took
          * `self_lock_sweeps`     - locks swept entering a new cycle
          * `last_result`          - the previous cycle's ArbitrationResult
          * `_blocked_by`          - who executed this cycle, for annotation
        All five are forensic candidates for a later slice, not this pass's scope.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.STATE_VERSION,
            "saved_at": datetime.now().isoformat(),
            "cycle": self.cycle,
            "queue": [
                {
                    "claim": self._claim_to_dict(slot.claim),
                    "deferred_cycles": slot.deferred_cycles,
                    "ttl_remaining": slot.ttl_remaining,
                }
                for slot in self._queue.values()
            ],
        }
        # Rider R3 (2026-07-29): ATOMIC. The deferral queue is pressure AUREA
        # judged and chose to CARRY; losing it to a truncation discharges it
        # silently, which is the defect Ruling 42 closed at the process boundary.
        atomic_write_json(self.runtime_path, payload, indent=2)

    def load(self) -> bool:
        """Runtime state if present, ELSE an empty queue. Returns whether it resumed.

        A RESTORED QUEUE OVER `QUEUE_MAX` IS A REFUSED LOAD, NOT A TRUNCATION.
        Truncation is a silent drain: it would discard real deferred pressure and
        report a healthy queue, which is the one outcome this whole ruling exists
        to prevent. The bound does not move (Ruling 23's shape - a bounded queue
        is how this system refuses to become an overload vector).

        EVERY REFUSAL HERE IS A DECLARED LOSS. Deferred pressure that cannot be
        restored has not been resolved; it has been LOST, and Ruling 23's sentence
        governs - unresolved pressure never leaves silently. The loss lands on
        `declared_losses` AND on the RB channel, which is the durable surface
        every other RACM outcome already uses.
        """
        if not self.runtime_path.exists():
            return False

        try:
            with open(self.runtime_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"expected a JSON object, got {type(data).__name__}")
        except (OSError, ValueError) as exc:
            return self._refuse_queue(f"unreadable arbitration state: {exc!r}", 0)

        version = data.get("version")
        if version != self.STATE_VERSION:
            return self._refuse_queue(
                f"unknown state version {version!r} (this build writes "
                f"{self.STATE_VERSION}); the file was left untouched",
                len(data.get("queue") or []))

        slots = data.get("queue") or []
        if len(slots) > QUEUE_MAX:
            return self._refuse_queue(
                f"restored queue depth {len(slots)} exceeds the canon bound "
                f"{QUEUE_MAX}; truncating would silently drain real deferred "
                f"pressure, so the whole restore is refused", len(slots))

        try:
            restored = {}
            for slot in slots:
                claim = self._claim_from_dict(slot["claim"])
                restored[claim.reflex_id] = _QueuedClaim(
                    claim=claim,
                    deferred_cycles=int(slot.get("deferred_cycles", 0)),
                    ttl_remaining=int(slot.get("ttl_remaining", TTL_CYCLES)),
                )
        except (KeyError, TypeError, ValueError) as exc:
            return self._refuse_queue(
                f"a deferral slot did not reconstruct: {exc!r}", len(slots))

        self._queue = restored
        self.cycle = int(data.get("cycle", 0))
        self.load_report = LoadReport(
            store="racm._queue", outcome=RestorationOutcome.RESTORED,
            path=str(self.runtime_path), resumed=True,
            detail={"cycle": self.cycle, "queue_depth": len(restored),
                    "saved_at": data.get("saved_at")})
        return True

    def _refuse_queue(self, reason: str, lost: int) -> bool:
        """Refuse the file, EMPTY the queue, and DECLARE the loss.

        The file is left BYTE-UNTOUCHED - `_persist` is a no-op for the life of a
        process that refused, because a file overwritten one cycle later was not
        left untouched.
        """
        self._queue = {}
        record = {"event": "deferred_pressure_lost", "reason": reason,
                  "slots_lost": lost, "path": str(self.runtime_path),
                  "at": datetime.now().isoformat()}
        self.declared_losses.append(record)
        self.load_report = LoadReport(
            store="racm._queue", outcome=RestorationOutcome.REFUSED,
            path=str(self.runtime_path), resumed=False, detail=record)
        # The RB channel, because it is the durable surface every other RACM
        # outcome already routes to (Ruling 11) - a loss recorded only in memory
        # would evaporate on the next restart, which is the defect one level up.
        # Best-effort: a logging failure must never make a store unconstructable.
        try:
            self.rb.record(
                reflex_triggered="RACM",
                behavior_type=BehaviorType.EXPIRE,
                trigger_conditions={"restore_refused": reason},
                affected_systems=["all"],
                symbolic_context="deferred pressure lost at a process boundary",
                deferred_cycles=0,
                ttl_remaining=0,
                outcome={"result": "declared loss", "slots_lost": lost},
                durable=True,
            )
        except Exception as exc:                    # pragma: no cover - defensive
            self.persist_failures.append({
                "op": "declare_loss", "error": repr(exc),
                "at": datetime.now().isoformat()})
        return False

    def _persist(self) -> None:
        """BEST-EFFORT save. NEVER RAISES (Ruling 11: the observer never gates the
        observed - a disk problem must not disable arbitration)."""
        if self.load_report is not None \
                and self.load_report.outcome is RestorationOutcome.REFUSED:
            return
        try:
            self.save()
        except (OSError, TypeError, ValueError) as exc:
            self.persist_failures.append({
                "op": "save", "path": str(self.runtime_path), "error": repr(exc),
                "at": datetime.now().isoformat(),
            })

    @staticmethod
    def _claim_to_dict(claim: ReflexClaim) -> Dict[str, Any]:
        """Both scope axes are written by NAME, and they stay separate (Ruling 30).
        `scope` is the durability/breadth axis; `lock_class` is the action's
        structural class. Serializing either as the other would rebuild the exact
        conflation Ruling 30 made unwritable."""
        return {
            "reflex_id": claim.reflex_id,
            "pressure_level": claim.pressure_level,
            "scope": claim.scope.name,
            "lock_class": claim.lock_class.name,
            "affected_systems": sorted(claim.affected_systems),
            "source_module": claim.source_module,
            "fossil_linked": claim.fossil_linked,
            "failed_nova_lineage": claim.failed_nova_lineage,
            "lesl_sesl_clean": claim.lesl_sesl_clean,
            "trigger_conditions": dict(claim.trigger_conditions),
            "metadata": dict(claim.metadata),
        }

    @staticmethod
    def _claim_from_dict(d: Dict[str, Any]) -> ReflexClaim:
        return ReflexClaim(
            reflex_id=d["reflex_id"],
            pressure_level=float(d.get("pressure_level", 0.0)),
            scope=Scope[d.get("scope", Scope.LOCAL.name)],
            lock_class=LockClass[d.get("lock_class", LockClass.NON_STRUCTURAL.name)],
            affected_systems=frozenset(d.get("affected_systems") or ()),
            source_module=d.get("source_module", ""),
            fossil_linked=bool(d.get("fossil_linked", False)),
            failed_nova_lineage=bool(d.get("failed_nova_lineage", False)),
            lesl_sesl_clean=bool(d.get("lesl_sesl_clean", False)),
            trigger_conditions=dict(d.get("trigger_conditions") or {}),
            metadata=dict(d.get("metadata") or {}),
        )

    # =================================================================
    # INTERNALS
    # =================================================================

    def _rank_key(self, claim: ReflexClaim):
        """Arbitration sort key: (effective rank, deferral seniority).

        Primary: effective rank (lower = more urgent). Secondary (Ruling 9 pt.3,
        canonized 2026-07-20): at equal effective rank the DEFERRED claim wins, and
        among deferred claims the one that has waited longest wins. A fresh claim
        carries seniority 0; a queued claim carries -deferred_cycles.
        """
        slot = self._queue.get(claim.reflex_id)
        seniority = -slot.deferred_cycles if slot else 0
        return (self._effective_rank(claim), seniority)

    def _effective_rank(self, claim: ReflexClaim) -> float:
        """Lower = more urgent. Modifiers RAISE priority, so they SUBTRACT rank."""
        boost = 0
        if claim.fossil_linked:
            boost += MOD_FOSSIL_LINKED
        if claim.failed_nova_lineage:
            boost += MOD_FAILED_NOVA_LINEAGE
        if claim.lesl_sesl_clean:
            boost += MOD_LESL_SESL_CLEAN
        # Aging is applied through the standard modifier mechanism (policy 4).
        slot = self._queue.get(claim.reflex_id)
        if slot:
            boost += min(slot.deferred_cycles * AGING_PER_CYCLE, AGING_CAP)
        return claim.base_rank() - boost

    def _merge_with_queue(self, claims: List[ReflexClaim]) -> List[ReflexClaim]:
        """Queued reflexes remain in contention. A re-trigger REFRESHES the slot's
        trigger conditions; it never adds a slot (policy 3)."""
        merged: Dict[str, ReflexClaim] = {}
        for rid, slot in self._queue.items():
            merged[rid] = slot.claim
        for claim in claims:
            if claim.reflex_id in self._queue:
                self._queue[claim.reflex_id].claim = claim   # refresh, do not add
            merged[claim.reflex_id] = claim
        return list(merged.values())

    def _age_queue(self, result: ArbitrationResult) -> None:
        """TTL + aging (policy 4). Expiry is never silent (policy 5)."""
        for rid in list(self._queue.keys()):
            slot = self._queue[rid]
            if rid in NEVER_EXPIRES:
                continue
            slot.deferred_cycles += 1
            slot.ttl_remaining -= 1
            if slot.ttl_remaining <= 0:
                self._expire(slot, result)

    def _expire(self, slot: _QueuedClaim, result: ArbitrationResult) -> None:
        claim = slot.claim
        entry = self.rb.record(
            reflex_triggered=claim.reflex_id,
            behavior_type=BehaviorType.EXPIRE,
            trigger_conditions=claim.trigger_conditions,
            affected_systems=sorted(claim.affected_systems),
            symbolic_context="deferral TTL exhausted",
            deferred_cycles=slot.deferred_cycles,
            ttl_remaining=0,
            outcome={"result": "expired from deferral queue"},
        )
        # Policy 5: trigger context routed to EchoTrace as a pressure signature.
        self.echotrace_signatures.append({
            "reflex_id": claim.reflex_id,
            "cycle": self.cycle,
            "pressure_level": claim.pressure_level,
            "trigger_conditions": claim.trigger_conditions,
        })
        result.decisions.append(Decision(
            reflex_id=claim.reflex_id,
            verdict=Verdict.EXPIRED,
            effective_rank=self._effective_rank(claim),
            reason="TTL exhausted",
            deferred_cycles=slot.deferred_cycles,
            ttl_remaining=0,
            rb_entry_id=entry.id,
            reason_code=ReasonCode.TTL_EXHAUSTED,
            failed_conditions=[f"deferred {slot.deferred_cycles} cycles "
                               f"without winning; TTL {TTL_CYCLES} exhausted"],
        ))
        self._clear_slot(claim.reflex_id)

        # Two consecutive expiries of the same reflex type -> escalate. A
        # legitimate signal under sustained pressure surfaces through the
        # escalation channel built for sustained pressure.
        if self.rb.consecutive_expiries(claim.reflex_id) >= 2:
            result.escalations.append(
                f"sustained pressure: {claim.reflex_id} expired twice consecutively "
                f"-> EscalationLogic"
            )

    def _defer(self, claim: ReflexClaim, result: ArbitrationResult) -> None:
        slot = self._queue.get(claim.reflex_id)
        if slot is None:
            slot = _QueuedClaim(claim=claim, deferred_cycles=0, ttl_remaining=TTL_CYCLES)
            self._queue[claim.reflex_id] = slot
        else:
            slot.claim = claim   # refresh conditions, keep the age

        # Policy 7: GLOBAL-scope grants are NOT held while queued; they are
        # re-requested at execution time (see _request_lock).
        entry = self.rb.record(
            reflex_triggered=claim.reflex_id,
            behavior_type=BehaviorType.DEFER,
            trigger_conditions=claim.trigger_conditions,
            affected_systems=sorted(claim.affected_systems),
            symbolic_context="lost same-cycle contention",
            deferred_cycles=slot.deferred_cycles,
            ttl_remaining=slot.ttl_remaining,
            outcome={"result": "queued"},
        )
        result.decisions.append(Decision(
            reflex_id=claim.reflex_id,
            verdict=Verdict.DEFERRED,
            effective_rank=self._effective_rank(claim),
            reason="lost same-cycle contention",
            deferred_cycles=slot.deferred_cycles,
            ttl_remaining=slot.ttl_remaining,
            rb_entry_id=entry.id,
            reason_code=ReasonCode.LOST_CONTENTION,
            blocking_claims=list(self._blocked_by),
            failed_conditions=self._contention_conditions(claim),
        ))
        assert len(self._queue) <= QUEUE_MAX, "deferral queue exceeded canon bound"

    def _contention_conditions(self, claim: ReflexClaim) -> List[str]:
        """Which specific bar this claim failed. OBSERVABILITY ONLY - derived
        from decisions already made, and read by nothing that decides.

        RULING 30 RESIDUE, corrected 2026-07-26. This used to say a GLOBAL
        claim "needs a system-wide lock it cannot hold while another reflex
        executes". That became FALSE the moment Ruling 30 keyed the lock on
        structural class: a GLOBAL-scope reflex claim requests NO lock. It
        loses at the COMPATIBILITY PARTITION, on breadth - a GLOBAL executor
        affects everything, so it can neither run alongside the winner nor
        carry passengers.

        A stale reason here is worse than no reason. The sliver decides
        nothing, but it is what an operator reads to learn WHY a claim lost,
        and it would have sent them hunting a lock that was never requested.
        """
        conditions: List[str] = []
        if claim.scope is Scope.GLOBAL:
            conditions.append(
                "GLOBAL scope: affects every system, so it cannot run "
                "alongside another executing reflex (compatibility partition)"
            )
        if claim.lock_class is LockClass.STRUCTURAL:
            conditions.append(
                "STRUCTURAL action: requires the TCAML lock, which it cannot "
                "hold while another reflex executes"
            )
        conditions.append(f"effective rank {self._effective_rank(claim):.2f} "
                          f"did not win this cycle")
        return conditions

    def _suppress(self, claim: ReflexClaim, result: ArbitrationResult,
                  reason: str) -> None:
        entry = self.rb.record(
            reflex_triggered=claim.reflex_id,
            behavior_type=BehaviorType.SUPPRESS,
            trigger_conditions=claim.trigger_conditions,
            affected_systems=sorted(claim.affected_systems),
            symbolic_context=reason,
            outcome={"result": "suppressed"},
        )
        result.decisions.append(Decision(
            reflex_id=claim.reflex_id,
            verdict=Verdict.SUPPRESSED,
            effective_rank=self._effective_rank(claim),
            reason=reason,
            rb_entry_id=entry.id,
            reason_code=ReasonCode.QUEUE_EXEMPT,
            blocking_claims=list(self._blocked_by),
            failed_conditions=[f"{claim.reflex_id} is queue-exempt "
                               f"(policy 6) and did not execute"],
        ))
        self._clear_slot(claim.reflex_id)

    def _clear_slot(self, reflex_id: str) -> None:
        self._queue.pop(reflex_id, None)

    def _meta_unstable(self) -> bool:
        return self.tcaml is not None and getattr(self.tcaml, "status", "") in META_UNSTABLE_STATES

    def _request_lock(self, claim: ReflexClaim, result: ArbitrationResult) -> bool:
        """Rule 2: synchronous two-phase handoff, no cached state.

        RULING 30: reached only by a STRUCTURAL claim. A non-structural action
        requires no TCAML check (Rule 1), and no reflex action is structural
        today - see the call site.

        THE BUILD-STAGE DEFAULT-GRANT BRANCH IS GONE (2026-07-26, §8 step 6b).
        It was the ONE place a GLOBAL action escaped the lock model: with TCAML
        absent, GLOBAL scope proceeded ungated and the gap was merely logged.
        `self.tcaml` is now never None (see __init__), so there is no absent
        state to grant around and no branch to re-introduce. If you find
        yourself adding an `if self.tcaml is None` here, you are rebuilding the
        seam - construct a TCAML instead.
        """
        grant = self.tcaml.lock_request(claim.reflex_id, claim.lock_class, "RACM")
        self.rb.record(
            reflex_triggered=claim.reflex_id,
            behavior_type=BehaviorType.LOCK_GRANT if grant else BehaviorType.LOCK_DENY,
            affected_systems=["TCAML"] + sorted(claim.affected_systems),
            symbolic_context="TCAML two-phase lock (GLOBAL scope)",
            outcome={"result": "granted" if grant else "denied",
                     "reason": getattr(grant, "reason", "")},
        )
        if not grant:
            result.decisions.append(Decision(
                reflex_id=claim.reflex_id,
                verdict=Verdict.LOCK_DENIED,
                effective_rank=self._effective_rank(claim),
                reason="TCAML lock denied",
                # Observability sliver: the LOCK's own reason, carried through
                # instead of collapsing to the bare verdict string above.
                reason_code=ReasonCode.LOCK_DENIED,
                failed_conditions=[getattr(grant, "reason", "")],
            ))
            self._clear_slot(claim.reflex_id)
        return bool(grant)

    def _sweep_own_stale_lock(self) -> None:
        """Release a lock RACM is somehow still holding from a previous cycle.

        WHY THIS EXISTS. RACM ACQUIRES the GLOBAL lock inside `arbitrate()`,
        but the natural completion it is held until happens in the GRID, after
        `arbitrate()` has returned. That split means the release depends on a
        DIFFERENT object faithfully executing every claim RACM granted - and
        "correct because the only caller is well-behaved" is a CONVENTION, not
        a boundary. Ruling 22 is the standing lesson on that distinction.

        Two real paths leaked before this existed:
          * `arbitrate()` called WITHOUT the Grid (every direct-RACM test, and
            anything future that arbitrates for itself) - the lock was taken
            and never given back, so the NEXT cycle's GSR was LOCK_DENIED. The
            Global Integrity Lock, disarmed by bookkeeping.
          * Ruling 9's ORPHAN path inside the Grid, which `continue`s past a
            claim whose reflex left the registry - skipping the release.
        The second is now also fixed at its own site (the Grid's per-claim
        `finally`); this sweep is what makes the leak UNEXECUTABLE rather than
        merely fixed in the two places currently known.

        NARROWLY SCOPED ON PURPOSE: it releases ONLY a lock whose holder_module
        is 'RACM'. A genuine multi-cycle holder - an MSP install spanning
        cycles, exactly what the TTL bound exists for - holds under its OWN
        module id and this sweep will not touch it. Broadening that check would
        turn a leak-guard into a lock-breaker.

        Recorded, never silent. Empty in a healthy system.
        """
        holder = self.tcaml.holder
        if holder is None or self.tcaml.holder_module != "RACM":
            return
        self.self_lock_sweeps.append({
            "action_id": holder,
            "held_since": self.tcaml.held_since,
            "cycle": self.cycle,
            "reason": "RACM held a GLOBAL lock into a new arbitration cycle - "
                      "its natural-completion release never ran",
            "at": datetime.now().isoformat(timespec="seconds"),
        })
        self.release_lock(holder)

    def release_lock(self, action_id: str) -> None:
        """Release a GLOBAL lock RACM acquired, at the action's completion.

        RACM is the HOLDER (it requested as module_id 'RACM'), so RACM is the
        only party TCAML accepts a release from. The Grid signals that the
        reflex FINISHED; it does not reach into the lock itself - signalling
        completion is not adjudication, and the lock was never the Grid's.

        `StaleLockRelease` is CAUGHT HERE AND RECORDED, not raised - and this
        is the one place that is correct, for a reason with precedent. The Grid
        calls this from a `finally`, and an exception raised inside a `finally`
        REPLACES the exception already in flight. Raising here would let a
        lock-bookkeeping fact destroy the reflex's own failure - Ruling 11's
        principle exactly: THE OBSERVER NEVER GATES THE OBSERVED. The event
        stays loud and durable on `stale_lock_releases`; it is not swallowed,
        it is REROUTED to a surface that cannot eat a real outcome.

        `LockReleaseViolation` deliberately still PROPAGATES. The Grid releases
        only claims RACM actually acquired, so that exception can only mean a
        genuine bug in this file - and those are supposed to be loud.
        """
        try:
            self.tcaml.release(action_id, "RACM")
        except StaleLockRelease as stale:
            self.stale_lock_releases.append({
                "action_id": action_id,
                "cycle": self.cycle,
                "detail": str(stale),
                "at": datetime.now().isoformat(timespec="seconds"),
            })

    def _check_escalations(self, result: ArbitrationResult,
                           fired_ids: set, ctx: Dict[str, Any]) -> None:
        """EscalationLogic (2b). reflexes_fired counts TRIGGERED reflexes."""
        compass_drift = float(ctx.get("compass_drift", 0.0))

        if (result.reflexes_fired >= ESCALATION_REFLEX_COUNT
                and compass_drift > ESCALATION_COMPASS_DRIFT):
            lineage = self._smc_lineage_match(ctx)
            if lineage:
                result.escalations.append(
                    f"SMC lineage match ({lineage}) under drift {compass_drift}deg "
                    f"-> lock output + reroute to CSA"
                )

        if MUTATION_ABORT_SET <= fired_ids:
            result.escalations.append(
                "DRPE + ICA + Whisper simultaneous -> abort mutation, SPS reroute, ADES log"
            )

        if "GSR" in fired_ids and ctx.get("sep_ready"):
            result.escalations.append(
                "GSR fired with SEP ready -> suspend expansion (Tether downgrade), "
                "increment SEP decay timer"
            )

    def _smc_lineage_match(self, ctx: Dict[str, Any]) -> Optional[str]:
        """Collapse Context Awareness: consult SMC for CAE / (delta) / (x) lineage.
        Falls back to caller-supplied context while SMC is a stub."""
        if self.smc is not None and hasattr(self.smc, "lineage_match"):
            return self.smc.lineage_match(ctx)
        return ctx.get("smc_lineage")

    # -- Ruling 34-A: SAE's anti-deadlock surfacing (canon 5a:1584) --

    def record_saturation_pressure(self, *, epoch: int, blocked_cycles: int,
                                   horizon: int,
                                   unsettled_lineages: List[str]) -> str:
        """Log reflex-class pressure for a saturated symbolic epoch.

        Canon 5a:1584 names THIS module as the logger: when SAE's mutation
        attempts have been blocked by a saturated epoch for more than the
        5-cycle horizon, "RACM logs reflex-class pressure and
        `RLB.divergence_trigger` eligibility is signaled ... rather than
        force-closing the epoch."

        RACM ORIGINATES NOTHING HERE (Ruling 2). SAE sources the condition,
        decides it is due, and asks; this method is the route to the RB log,
        which SAE has no standing to write itself (Ruling 1 - CLAUDE.md §2 lists
        the log's requesters as RACM and the Grid, and that table is not widened
        by this ruling). **It does not arbitrate, does not gate, and returns no
        verdict** - only the entry id, so SAE can record where its own signal
        landed.

        BEHAVIOR TYPE: `SUSPEND`, from the CLOSED enum (Ruling 7 - it stays
        closed; there is no `pressure` member and none is added). SUSPEND is the
        honest fit: the epoch's mutation capacity is HELD, unresolved, carried -
        not denied and not resolved. Ruling 7 set the precedent by decomposing
        GSR's cascade to the same member.

        DURABLE, deliberately. Ruling 11 ties a REFLEX entry's durability to its
        scope; SAE is not a reflex and this entry is scope-less, like RACM's own
        lock events. The caller decides (`record(..., durable=...)`), and this
        caller decides YES: it fires at most once per saturation episode and it
        records that AUREA's capacity to change herself is locked. Losing that to
        a buffer is precisely the durable-and-invisible failure Ruling 34-A names.
        """
        entry = self.rb.record(
            reflex_triggered="SAE",
            behavior_type=BehaviorType.SUSPEND,
            trigger_conditions={
                "condition": "saturated_symbolic_epoch",
                "epoch": epoch,
                "consecutive_blocked_cycles": blocked_cycles,
                "horizon": horizon,
            },
            affected_systems=["SAE", "doctrine", "expansion"],
            symbolic_context=(
                f"anti-deadlock (5a:1584): mutation attempts blocked by a "
                f"saturated epoch for {blocked_cycles} consecutive symbolic "
                f"cycles (horizon {horizon}). The epoch is SURFACED, NOT "
                f"force-closed - re-arming capacity now would re-arm it at the "
                f"exact moment nothing has been metabolized."
            ),
            outcome={
                "result": "surfaced",
                "epoch_force_closed": False,
                "divergence_trigger_eligible": True,
                "unsettled_lineages": unsettled_lineages,
            },
            durable=True,
        )
        # M3-D §1.3 - THE ADMISSION SEAM. ADDITIVE: the RB record above is
        # BYTE-UNCHANGED and is written FIRST, so the forensic entry exists
        # whatever happens next. `divergence_trigger_eligible` stays
        # declared-unread (Ruling 34-A) - nothing here reads or sets it.
        #
        # ONE ADMISSION PER UNSETTLED LINEAGE. A saturated epoch is not one
        # owed thing: it is one owed thing PER lineage SAE touched and could
        # not settle, and collapsing them into a single obligation would lose
        # exactly the fact the epoch is saturated ABOUT.
        self._admit_saturation(epoch, blocked_cycles, horizon, unsettled_lineages)
        return entry.id

    def _admit_saturation(self, epoch: int, blocked_cycles: int, horizon: int,
                          unsettled_lineages: List[str]) -> None:
        """Admit one obligation per unsettled lineage. Best-effort, always.

        RACM is a REQUESTER at K2's door. **THE ADMISSION NEVER GATES THE
        PROTECTIVE RECORD** - the RB entry is already written when this runs,
        and every failure lands on `admission_failures` rather than raising.
        Ruling 11's line: a logging failure must not disable a suppression, and
        an admission failure must not disable the record of a locked ceiling.

        SOURCE IS `"SAE"`: the condition is SAE's, and Ruling 2's one-way
        authority is why the source names the module that SOURCED it rather
        than the arbiter that routed it.
        """
        if self.obligation_ledger is None:
            return
        for lineage in unsettled_lineages or ():
            try:
                self.obligation_ledger.admit(
                    source="SAE",
                    target_kind="doctrine",
                    target_id=lineage,
                    claim_text=(
                        f"saturated symbolic epoch {epoch}: mutation blocked "
                        f"for {blocked_cycles} consecutive cycles past the "
                        f"{horizon}-cycle horizon with lineage '{lineage}' "
                        f"unsettled"),
                )
            except Exception as exc:              # noqa: BLE001 - see docstring
                self.admission_failures.append({
                    "epoch": epoch,
                    "lineage": lineage,
                    "error": f"{type(exc).__name__}: {exc}",
                })

    # -- direct suppression path (2b pseudo: RACM.suppress_reflex(trigger_id)) --

    def suppress_reflex(self, reflex_id: str, reason: str = "external suppression") -> None:
        """Called by the meta-instability override path and by TCAML lock denial.
        Suppression is never silent - Rule 2(d) requires the log entry."""
        self.rb.record(
            reflex_triggered=reflex_id,
            behavior_type=BehaviorType.SUPPRESS,
            symbolic_context=reason,
            outcome={"result": "suppressed"},
        )
        self._clear_slot(reflex_id)
