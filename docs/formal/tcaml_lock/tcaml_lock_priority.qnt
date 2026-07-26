// TCAML two-phase GLOBAL lock -- PRIORITY variant.
// Identical to tcaml_lock.qnt except: once ttlExpire is enabled, it
// preempts every other GLOBAL-housekeeping action in the same step,
// instead of being merely one nondeterministic option among several.
// This is what turns "bounded, eventually" into "bounded, exactly TTL."

module tcaml_lock_priority {

  type Status = Healthy | MetaUnstable | RepairCycle
  type Tier   = Routine | Elevated

  pure val TTL = 5
  pure val ROUTINE_THRESHOLD = 40
  pure val ELEVATED_THRESHOLD = 75
  pure val RECOVERY_THRESHOLD = 75
  pure val ACTORS = Set("mspInstall", "doctrineRemap")

  var status: Status
  var holder: str
  var heldSince: int
  var cycle: int
  var health: int

  action init = all {
    status' = Healthy,
    holder' = "",
    heldSince' = 0,
    cycle' = 0,
    health' = 100,
  }

  action requestGlobal(actor, tier) = all {
    holder == "",
    status == Healthy,
    tier == Routine implies health >= ROUTINE_THRESHOLD,
    tier == Elevated implies health >= ELEVATED_THRESHOLD,
    holder' = actor,
    heldSince' = cycle,
    status' = status,
    cycle' = cycle,
    health' = health,
  }

  action release(actor) = all {
    holder == actor,
    holder' = "",
    heldSince' = heldSince,
    status' = status,
    cycle' = cycle,
    health' = health,
  }

  action ttlExpire = all {
    holder != "",
    cycle - heldSince >= TTL,
    holder' = "",
    heldSince' = heldSince,
    status' = status,
    cycle' = cycle,
    health' = health,
  }

  action instabilityOnset = {
    nondet s = Set(MetaUnstable, RepairCycle).oneOf()
    all {
      status == Healthy,
      status' = s,
      holder' = "",
      heldSince' = 0,
      cycle' = cycle,
      health' = health,
    }
  }

  action recoverStability = all {
    status != Healthy,
    health >= RECOVERY_THRESHOLD,
    status' = Healthy,
    holder' = holder,
    heldSince' = heldSince,
    cycle' = cycle,
    health' = health,
  }

  action healthDrift = {
    nondet delta = Set(-10, -5, 0, 5, 10).oneOf()
    val nextHealth = health + delta
    val clamped = if (nextHealth < 0) 0 else (if (nextHealth > 100) 100 else nextHealth)
    all {
      health' = clamped,
      status' = status,
      holder' = holder,
      heldSince' = heldSince,
      cycle' = cycle,
    }
  }

  action tick = all {
    cycle' = cycle + 1,
    status' = status,
    holder' = holder,
    heldSince' = heldSince,
    health' = health,
  }

  // THE FIX: ttlExpire preempts everything else once due.
  action step = {
    nondet actor = ACTORS.oneOf()
    nondet tier = Set(Routine, Elevated).oneOf()
    if (holder != "" and cycle - heldSince >= TTL) {
      ttlExpire
    } else {
      any {
        requestGlobal(actor, tier),
        release(actor),
        instabilityOnset,
        recoverStability,
        healthDrift,
        tick,
      }
    }
  }

  val noGrantDuringInstability = (holder != "") implies (status == Healthy)
  val singleHolderWellFormed = (holder == "") or ACTORS.contains(holder)

  // Exact bound now -- zero slack needed, compare to tcaml_lock.qnt's +3.
  val boundedHoldTight = (holder != "") implies (cycle - heldSince <= TTL)
}
