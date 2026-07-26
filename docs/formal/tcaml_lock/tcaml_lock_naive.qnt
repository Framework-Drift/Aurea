// NAIVE variant of the TCAML lock -- for comparison only.
// Only difference from tcaml_lock.qnt: instabilityOnset does NOT clear an
// existing holder. Tests whether "meta-instability override blocks NEW
// GLOBAL requests" alone (without revoking an in-flight hold) is sufficient
// to satisfy noGrantDuringInstability. It is not -- see the run below.

module tcaml_lock_naive {

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

  // THE VARIANT: onset only blocks future requestGlobal calls (via the
  // status==Healthy guard already on requestGlobal). It does NOT touch
  // holder. This is the "block new grants only" reading of Rule 3.
  action instabilityOnset = {
    nondet s = Set(MetaUnstable, RepairCycle).oneOf()
    all {
      status == Healthy,
      status' = s,
      holder' = holder,
      heldSince' = heldSince,
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

  action step = {
    nondet actor = ACTORS.oneOf()
    nondet tier = Set(Routine, Elevated).oneOf()
    any {
      requestGlobal(actor, tier),
      release(actor),
      ttlExpire,
      instabilityOnset,
      recoverStability,
      healthDrift,
      tick,
    }
  }

  val noGrantDuringInstability = (holder != "") implies (status == Healthy)
}
