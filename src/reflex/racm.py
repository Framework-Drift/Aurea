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

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Protocol

from src.reflex.rb_system import BehaviorType, RBSystem


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
    """Scope-partitioned lock model. GLOBAL requires a TCAML two-phase lock."""
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
    """The only surface RACM needs from the topology layer."""
    status: str
    def lock_request(self, action_id: str, scope: str, module_id: str) -> bool: ...


@dataclass
class ReflexClaim:
    """A reflex's CLAIM to execute this cycle. Built by the Grid (the source),
    judged by RACM (the arbiter). Carries no reflex logic - RACM never runs it."""
    reflex_id: str
    pressure_level: float = 0.0
    scope: Scope = Scope.LOCAL
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


@dataclass
class Decision:
    reflex_id: str
    verdict: Verdict
    effective_rank: float
    reason: str = ""
    deferred_cycles: int = 0
    ttl_remaining: int = TTL_CYCLES
    rb_entry_id: Optional[str] = None


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

    def __init__(self, rb_system: Optional[RBSystem] = None,
                 tcaml: Optional[TCAMLPort] = None,
                 smc: Any = None):
        self.rb = rb_system or RBSystem()
        self.tcaml = tcaml
        self.smc = smc                              # Collapse Context Awareness source
        self.cycle = 0
        self._queue: Dict[str, _QueuedClaim] = {}   # reflex_id -> slot; depth <= QUEUE_MAX
        self.last_result: Optional[ArbitrationResult] = None
        self.echotrace_signatures: List[Dict[str, Any]] = []  # policy 5: expiry is never silent

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

        # 4. Effective ranking.
        ranked = sorted(arbitration_set, key=lambda c: self._effective_rank(c))

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

        # A GLOBAL-scope executor holds a system-wide lock. NOTHING is disjoint
        # from it, so nothing runs alongside it. Set-disjointness alone does not
        # catch this (a GLOBAL reflex's affected-system set does not textually
        # intersect a LOCAL one) - the partition must be scope-gated first.
        # A non-winning GLOBAL claim is likewise never a passenger: it needs a
        # lock it cannot hold while another reflex is executing. It defers.
        if winner.scope is not Scope.GLOBAL:
            for claim in ranked[1:]:
                compatible = (
                    claim.scope is Scope.LOCAL
                    and not (set(claim.affected_systems) & claimed_systems)
                )
                if compatible:
                    executing.append(claim)
                    claimed_systems |= set(claim.affected_systems)

        # 7. TCAML two-phase lock for GLOBAL-scope executors (Rule 2).
        granted: List[ReflexClaim] = []
        for claim in executing:
            if claim.scope is Scope.GLOBAL and not self._request_lock(claim, result):
                continue
            granted.append(claim)
            self._clear_slot(claim.reflex_id)
            result.decisions.append(Decision(
                reflex_id=claim.reflex_id,
                verdict=Verdict.EXECUTE,
                effective_rank=self._effective_rank(claim),
                reason="highest priority" if claim is winner else "compatible (LOCAL, disjoint)",
            ))
        result.execute = granted

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
        return result

    # =================================================================
    # INTERNALS
    # =================================================================

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
        ))
        assert len(self._queue) <= QUEUE_MAX, "deferral queue exceeded canon bound"

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
        ))
        self._clear_slot(claim.reflex_id)

    def _clear_slot(self, reflex_id: str) -> None:
        self._queue.pop(reflex_id, None)

    def _meta_unstable(self) -> bool:
        return self.tcaml is not None and getattr(self.tcaml, "status", "") in META_UNSTABLE_STATES

    def _request_lock(self, claim: ReflexClaim, result: ArbitrationResult) -> bool:
        """Rule 2: synchronous two-phase handoff, no cached state. LOCAL-scope
        actions require no TCAML check (Rule 1)."""
        if self.tcaml is None:
            # BUILD-STAGE SEAM (not canon): TCAML is not yet wired into the runtime.
            # GLOBAL scope proceeds ungated and the gap is logged, rather than
            # silently denying GSR and disarming the integrity lock. Remove this
            # branch the moment TCAML is constructed - it is the one place a
            # GLOBAL action currently escapes the lock model.
            self.rb.record(
                reflex_triggered=claim.reflex_id,
                behavior_type=BehaviorType.LOCK_GRANT,
                affected_systems=["TCAML"],
                symbolic_context="TCAML absent (build stage) - GLOBAL scope ungated",
                outcome={"result": "granted by default"},
            )
            return True

        grant = self.tcaml.lock_request(claim.reflex_id, claim.scope.value, "RACM")
        self.rb.record(
            reflex_triggered=claim.reflex_id,
            behavior_type=BehaviorType.LOCK_GRANT if grant else BehaviorType.LOCK_DENY,
            affected_systems=["TCAML"] + sorted(claim.affected_systems),
            symbolic_context="TCAML two-phase lock (GLOBAL scope)",
            outcome={"result": "granted" if grant else "denied"},
        )
        if not grant:
            result.decisions.append(Decision(
                reflex_id=claim.reflex_id,
                verdict=Verdict.LOCK_DENIED,
                effective_rank=self._effective_rank(claim),
                reason="TCAML lock denied",
            ))
            self._clear_slot(claim.reflex_id)
        return grant

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
