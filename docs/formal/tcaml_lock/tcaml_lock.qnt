// TCAML two-phase GLOBAL lock -- Docket J formal model (CORRECTED / proposed)
// Grounds: BUILD_CONTRACT.md "RACM <-> TCAML" interface,
//          Pressure_Valve_Coordination "Arbitration Protocol v2.0" (Rules 1-3),
//          Ruling 27 (this session's TCAML grounding contract).
//
// Models exactly the GLOBAL-scope path. LOCAL actions are out of scope by
// design (Rule 1: no lock check, so nothing to prove).

module tcaml_lock {

  type Status = Healthy | MetaUnstable | RepairCycle
  type Tier   = Routine | Elevated

  pure val TTL = 5                 // canon 5-cycle horizon -- recovered, not coined
  pure val ROUTINE_THRESHOLD = 40  // COINED, pending registration
  pure val ELEVATED_THRESHOLD = 75 // COINED, pending registration
  pure val RECOVERY_THRESHOLD = 75 // COINED, pending registration
  pure val ACTORS = Set("mspInstall", "doctrineRemap")

  var status: Status
  var holder: str          // "" = NoHolder
  var heldSince: int
  var cycle: int
  var health: int          // 0..100 -- TCAML's own live Constellation Health Index

  action init = all {
    status' = Healthy,
    holder' = "",
    heldSince' = 0,
    cycle' = 0,
    health' = 100,
  }

  // Rule 2 -- GLOBAL request. Deny paths leave state unchanged except for
  // being the disjunct that was NOT taken; grant is the only path that
  // moves holder. Docket F's structural tier selects which health
  // threshold this request must clear -- it never denies on its own.
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

  // Safety net for an orphaned lock (holder crashed/never released).
  // TTL reuses the canon 5-cycle horizon -- see COINED_CONSTANTS.md pattern.
  action ttlExpire = all {
    holder != "",
    cycle - heldSince >= TTL,
    holder' = "",
    heldSince' = heldSince,
    status' = status,
    cycle' = cycle,
    health' = health,
  }

  // Rule 3 -- meta-instability override.
  // MODELED INTERPRETATION (the flagged decision point): onset REVOKES any
  // currently-held lock immediately, matching "a grant issued a moment
  // before instability onset is not still valid" read literally.
  // See tcaml_lock_naive.qnt for what happens if it does NOT revoke.
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

  // Models the live feed from CSE (drift) / SML (bloom) / SGF (fragmentation)
  // into TCAML's own Constellation Health Index. Bounded random walk.
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

  // ---- PROPERTIES ----

  // SAFETY (Rule 3): a GLOBAL lock is never held while TCAML is unstable.
  val noGrantDuringInstability = (holder != "") implies (status == Healthy)

  // SAFETY (mutual exclusion, restated): the model has exactly one holder
  // slot by construction -- this makes that structural fact explicit and
  // machine-checked rather than assumed from the data shape.
  val singleHolderWellFormed = (holder == "") or ACTORS.contains(holder)

  // BOUNDED HOLD under random scheduling: the lock does not grow the
  // held-duration without limit. Slack of +3 accounts for the gap between
  // "ttlExpire becomes enabled" and "ttlExpire gets scheduled" under
  // interleaving semantics -- see prose: real bound is TTL + (cycles
  // between RACM arbitration passes), which the build must pin down.
  val boundedHoldUnderScheduling = (holder != "") implies (cycle - heldSince <= TTL + 3)
}
