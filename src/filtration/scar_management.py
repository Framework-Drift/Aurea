"""
scar_management.py - SML: the Scar Maturation Layer. THE DECAY OWNER.

Canon: Lexicon §3 (Scar Decay System) - "fading, dormancy, fossilization, or
purging of scars ... transitions from active to waning to dormant to fossilized
or purged"; Unified:79 - "She does not forget. She decays with reverence."
Ruling: 37 (the stabilization-senders grounding contract) + 37-A (magnitudes).

THE OWNER WAS NAMED IN THE CODE BEFORE THE ORGAN EXISTED. `scar_logic_core.py`
has said "Weight and decay belong to SML (Ruling 1)" since Ruling 22, beside a
zero-byte `scar_management.py`. This is that file.

WHAT FERMENTATION IS, AND WHY IT IS THE SETTLE EVENT
-----------------------------------------------------
A scar under strain can end two ways: it COOLS (decays toward waning/dormant) or
it IGNITES (drifts, escalates, re-enters collapse). Ruling 37 grounds the
distinction:

    A scar linked to an SAE-touched lineage COMPLETES FERMENTATION when the
    decay owner transitions it out of ACTIVE **by decay** - not by
    drift-escalation and not by re-collapse. The mutation's consequences were
    absorbed. The wound cooled.

That is the event `SAE.stabilization_event("scar_fermentation", lineage)` has
been waiting for since the ceiling was built. **Before this file, the ONLY
implemented way to restore mutation budget was to kill the process.**

SML EMITS; SAE NEVER POLLS. Ruling 37 (5) states the reason and it is not
stylistic: SAE owning the settle-detection would make the BUDGET-HOLDER THE
JUDGE OF ITS OWN DEBTS. `sae` is a write-only collaborator here - SML calls one
method on it and reads one field - and an AST pin asserts `sae.py` never imports
or references this module.

THE SCHEDULE - COUNTED QUIET CYCLES, NEVER A WEIGHT FORMULA
------------------------------------------------------------
`SCAR_DECAY_CYCLES = 5` per transition, SEQUENTIAL (Ruling 37-A (A),
pre-registered in COINED_CONSTANTS.md ahead of this code). RECOVERED, not
coined: the seventh reuse of the canon 5-cycle horizon.

    ACTIVE  --5 quiet cycles-->  WANING   <- fermentation COMPLETES here
    WANING  --5 quiet cycles-->  DORMANT

Ten quiet cycles to dormancy - twice the housekeeping rate, zero invented
magnitudes. A wound cools slower than a lock expires because it passes through
MORE STATES on the same clock, which is what the canon state machine is for.

STRICT COMPARISON, the `SATURATION_HORIZON` precedent: the transition fires on
the SIXTH quiet cycle (`count > SCAR_DECAY_CYCLES`), not the fifth.

QUIET IS DEFINED AND CONSECUTIVE: no drift event, no re-collapse, and no new
scar on the same lineage during the cycle. ANY of those RESETS the current
transition's count - fermentation interrupted is fermentation RESTARTED, which
is 34-A's consecutive-means-consecutive applied to cooling.

    SECTION 9 STANDING BAR #5: A SCAR'S WEIGHT REPORTS ITS MAGNITUDE. IT NEVER
    SCHEDULES ITS COOLING. No weight term appears anywhere in this schedule,
    and an AST pin refuses one.

That bar is why decay is counted cycles and not `weight / half_life`: a
weight-driven schedule would make the heaviest scars cool slowest or fastest by
a coined curve nobody ruled, at the site that decides when AUREA may change
herself again.

DECLARED-NOT-FAKED: FOSSILIZED AND PURGED
------------------------------------------
Canon's state machine continues past DORMANT. v1 implements
`active -> waning -> dormant` ONLY. `FOSSILIZED` and `PURGED` are DECLARED
members with NO v1 path, and `transition()` RAISES on either - the ICA
dormant-trigger pattern: named so the vocabulary is complete and an emitter can
arrive without editing this file, refused so no half-implementation invites use.
A pin fails if a path appears without a ruling.

WHAT THIS ORGAN DOES NOT OWN
-----------------------------
The SML/SDS split in the Lexicon is DEFERRED - one organ until two are needed
(the CSA/VeiledThread precedent). Scar WEIGHT is named as SML's in the ownership
table and is NOT touched here: v1 owns the state machine only, because weight
adjustment has no ruled schedule and inventing one is bar #5 again.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from src.utils.models import Scar


# Ruling 37-A (A). RECOVERED, not coined - the canon 5-cycle horizon, SEVENTH
# reuse. Registered in COINED_CONSTANTS.md ahead of this code (the TCAML
# precedent). PER TRANSITION and SEQUENTIAL: five to waning, five more to
# dormant. The comparison it feeds is STRICT - see the module docstring.
SCAR_DECAY_CYCLES = 5


class DecayState(str, Enum):
    """The canon decay vocabulary (Lexicon section 3), closed.

    A `str` Enum, and that is a DELIBERATE DEPARTURE from `ExpressionVerdict` /
    `Countability`, which are pointedly non-`str`. Those are non-`str` because
    TWO vocabularies had to be kept from comparing equal to each other. Here
    there is ONE vocabulary, it is PERSISTED as a JSON string on every scar, and
    four modules outside this one already compare `decay_state` to plain strings
    (`srg`, `symbolic_grouping`, `autonomy_index`, `ore`). A non-`str` enum
    would silently break every one of those comparisons - the fail-silent shape
    - while buying a separation nothing here needs.

    So: the members ARE their canon strings, and a legacy record loaded from
    disk compares equal to the member that matches it.
    """
    ACTIVE = "active"
    WANING = "waning"
    DORMANT = "dormant"
    # DECLARED, UNREACHABLE IN v1. `transition()` raises on either.
    FOSSILIZED = "fossilized"
    PURGED = "purged"


# The v1 state machine. FOSSILIZED / PURGED are absent BY CONSTRUCTION, not by a
# check that could be forgotten.
DECAY_SEQUENCE: Dict[DecayState, DecayState] = {
    DecayState.ACTIVE: DecayState.WANING,
    DecayState.WANING: DecayState.DORMANT,
}

# Transitions canon names and v1 has no ruled path for.
UNREACHABLE_STATES = frozenset({DecayState.FOSSILIZED, DecayState.PURGED})

# RULING 37 (2): `"retired"` maps INTO the canon vocabulary rather than
# surviving as a fifth state.
#
# WHY DORMANT: `autonomy_index.py` already treats the two as THE SAME KIND -
# `MATURED_DECAY_STATES = {"retired", "dormant", "fossil"}`, "survived and
# integrated" rather than "still live crisis" - and its own comment says both
# vocabularies are honored "so this doesn't silently break if the richer state
# set gets wired in later." This is that later. The mapping is therefore
# BEHAVIOURALLY INERT for the one module that reads the distinction, which is
# the strongest evidence available that it is the right reading.
LEGACY_DECAY_ALIASES: Dict[str, DecayState] = {
    "retired": DecayState.DORMANT,
}


class DecayTransitionViolation(Exception):
    """A decay transition canon names but v1 has no ruled path for.

    Raised rather than silently ignored: a state machine that accepts a
    transition it cannot perform is a state machine that has already lied.
    """


def normalize(raw: Any) -> DecayState:
    """Read any stored decay value as a canon state.

    Handles the legacy `"retired"` literal and unrecognised strings alike:
    anything unknown reads as ACTIVE, which is the CONSERVATIVE direction - an
    unclassifiable scar is treated as still live, never as already cooled.
    Cooling a scar nobody can classify would discharge an obligation on a record
    we do not understand.
    """
    if isinstance(raw, DecayState):
        return raw
    text = str(raw or "").strip().lower()
    if text in LEGACY_DECAY_ALIASES:
        return LEGACY_DECAY_ALIASES[text]
    for state in DecayState:
        if state.value == text:
            return state
    return DecayState.ACTIVE


class SML:
    """Scar Maturation Layer - counts quiet cycles, emits settle events.

    Holds NO store of its own: the scars belong to ScarLogicCore and the epoch
    belongs to SAE. What SML owns is the DECISION - when a scar has been quiet
    long enough to have cooled - and the per-scar counters that decision rests
    on.
    """

    def __init__(self, scar_core: Any = None, sae: Any = None):
        self.scar_core = scar_core
        # Write-only collaborator (Ruling 37 (5)): SML calls
        # `stabilization_event` and reads `touched_lineages`; SAE never polls SML.
        self.sae = sae

        # scar id -> consecutive quiet cycles in the CURRENT transition.
        self._quiet: Dict[str, int] = {}
        # Within-cycle disturbance accumulators, settled by `advance_cycle`.
        # The SAE precedent exactly: flags accrue during the pass, the boundary
        # resolves them, and they are NOT persisted.
        self._cycle_drift = False
        self._cycle_disturbed: set = set()

        # Legible, append-only working notes. Not a store.
        self.transitions: List[Dict[str, Any]] = []
        self.settle_events: List[Dict[str, Any]] = []

    # =================================================================
    # DISTURBANCE - anything that makes a cycle NOT quiet
    # =================================================================

    def note_drift_event(self) -> None:
        """A compass drift event. GLOBAL: it resets every scar's count.

        Drift is a system-wide reading, so there is no honest way to scope it to
        some scars and not others. Resetting everything DELAYS cooling, and
        delayed cooling holds the epoch closed - the side canon's anti-deadlock
        clause says to err on.
        """
        self._cycle_drift = True

    def note_disturbance(self, lineages: Iterable[str]) -> None:
        """A re-collapse, or a NEW scar, on these lineages. Scoped."""
        for lineage in lineages:
            if lineage:
                self._cycle_disturbed.add(lineage)

    def note_scar_formed(self, scar: Optional[Scar]) -> None:
        """A new scar disturbs its own lineage and every doctrine it links."""
        if scar is None:
            return
        self.note_disturbance([scar.id, *(scar.linked_doctrines or [])])

    # =================================================================
    # THE CLOCK
    # =================================================================

    def advance_cycle(self) -> List[Dict[str, Any]]:
        """Close the accounting for the symbolic cycle just ended.

        ONE SYMBOLIC CYCLE = ONE `AureaCore.process_input` PASS - driven from
        the SAME site as `tcaml.tick()` and `sae.advance_cycle()`, so the three
        clocks advance together and cannot drift (the ecc330c precedent).

        Returns the transitions performed, for the caller's report.
        """
        performed: List[Dict[str, Any]] = []
        for scar in self._live_scars():
            state = normalize(scar.decay_state)
            if state not in DECAY_SEQUENCE:
                continue                       # DORMANT and beyond do not age

            if self._disturbed(scar):
                # Fermentation interrupted is fermentation RESTARTED.
                self._quiet[scar.id] = 0
                continue

            count = self._quiet.get(scar.id, 0) + 1
            self._quiet[scar.id] = count

            # STRICT, the SATURATION_HORIZON precedent: the SIXTH quiet cycle.
            if count > SCAR_DECAY_CYCLES:
                performed.append(self.transition(scar.id, DECAY_SEQUENCE[state]))

        self._cycle_drift = False
        self._cycle_disturbed = set()
        return performed

    def _disturbed(self, scar: Scar) -> bool:
        if self._cycle_drift:
            return True
        if scar.id in self._cycle_disturbed:
            return True
        return any(d in self._cycle_disturbed for d in (scar.linked_doctrines or []))

    def _live_scars(self) -> List[Scar]:
        """The LIVE records. SML is the decay owner (Ruling 1) and writes them.

        Deliberately NOT `get_active_scars()`: that accessor SNAPSHOTS (Ruling
        22), so an owner-side write through it would vanish silently - the exact
        hazard `_find()` exists for on ScarLogicCore's own write paths - and it
        filters to ACTIVE, so it could never advance a WANING scar to DORMANT.
        """
        if self.scar_core is None:
            return []
        return list(getattr(self.scar_core, "scars", []) or [])

    # =================================================================
    # THE TRANSITION - and the settle event it emits
    # =================================================================

    def manual_retire(self, scar_id: str) -> bool:
        """RULING 40 - THE MANUAL RETIRE, EXECUTED BY THE DECAY OWNER.

        `ScarLogicCore.decay_scar` used to write `decay_state` itself, which made
        TWO writers of one field - the exact shape Ruling 1 exists to prevent, and
        `scar_logic_core.py`'s own comment had flagged it as "Reported, not
        repaired" since Ruling 37. This is the repair: the public surface stays,
        the WRITE moves here.

        THE JUMP PAST WANING IS AUTHORIZED FOR THE MANUAL CASE ONLY. The
        SCHEDULED machine is strictly sequential (`active -> waning -> dormant`,
        five quiet cycles each) because cooling is something a scar DOES over
        time. A manual retire is not cooling - it is an operator statement that
        this record is finished - so it does not walk the cooling path.

        AND IT EMITS NO SETTLE EVENT, WHICH IS THE LOAD-BEARING HALF. Ruling 37
        makes fermentation complete when a scar leaves ACTIVE **by decay**;
        `_emit_fermentation` is reachable only from `ACTIVE -> WANING`, and this
        method goes to DORMANT, so it cannot reach it even by accident. A manual
        retire that restored mutation budget would let an operator action close
        an epoch - restart-absolution (Ruling 34) wearing a different hat.

        Returns False for an unknown id rather than raising: this is the owner's
        `decay_scar` contract, which has always answered "no such scar" with a
        return value.
        """
        if self._record(scar_id) is None:
            return False
        self.transition(scar_id, DecayState.DORMANT, manual=True)
        return True

    def transition(self, scar_id: str, new_state: DecayState,
                   manual: bool = False) -> Dict[str, Any]:
        """Move a scar to a new decay state. SML is the writer.

        RAISES on FOSSILIZED / PURGED: canon names them, v1 has no ruled path,
        and a transition that cannot be performed is refused rather than faked.

        `manual` records WHICH mechanism moved the scar. It changes no gate and
        selects no path - the settle event is decided by the from/to pair, as it
        always was - it makes the two causes distinguishable in the record
        (Ruling 29's shape: one event type covering two causes is a defect).
        """
        if new_state in UNREACHABLE_STATES:
            raise DecayTransitionViolation(
                f"'{new_state.value}' is DECLARED in the canon decay vocabulary "
                f"(Lexicon section 3) and has NO v1 path (Ruling 37 (2): "
                f"active -> waning -> dormant ONLY). Fossilization and purging "
                f"are their own ruling - building a path here would be the "
                f"half-implementation the declaration exists to prevent."
            )

        scar = self._record(scar_id)
        if scar is None:
            raise DecayTransitionViolation(f"no scar '{scar_id}' to transition")

        was = normalize(scar.decay_state)
        scar.decay_state = new_state.value
        self._quiet[scar_id] = 0               # the next transition starts fresh

        record = {"scar_id": scar_id, "from": was.value, "to": new_state.value,
                  "trigger": "manual" if manual else "scheduled",
                  "settled_lineages": []}

        # THE SETTLE EVENT. Only on ACTIVE -> WANING, and only BY DECAY: this
        # method is not reachable from drift-escalation or re-collapse, which is
        # what makes "cooled" distinguishable from "ignited" (Ruling 37 (1)).
        if was is DecayState.ACTIVE and new_state is DecayState.WANING:
            record["settled_lineages"] = self._emit_fermentation(scar)

        self.transitions.append(record)
        self._persist()
        return record

    def _emit_fermentation(self, scar: Scar) -> List[str]:
        """Tell SAE a touched lineage has settled. SML emits; SAE never polls.

        WHICH KEY IS "THE LINEAGE" IS GENUINELY AMBIGUOUS IN THE CODEBASE, and
        this reads BOTH rather than picking one. `sae.touched_lineages` is
        populated from `collapse_lineage`, which every live call site fills with
        a SCAR id (`dee.py` passes `doctrine.scar_links[0]`), while Ruling 37's
        text says a scar settles when its `linked_doctrines` intersect the
        touched set. Reading only one convention would silently never fire under
        the other. Ruling 26's bidirectional-read shape, applied to the same
        two-sided relationship one layer over.

        Whatever MATCHED is what is passed, so `stabilization_event`'s own guard
        (`lineage not in touched_lineages -> False`, Ruling 34 res.3) is
        satisfied by construction rather than by hope.
        """
        if self.sae is None:
            return []
        touched = set(getattr(self.sae, "touched_lineages", set()) or set())
        settled: List[str] = []
        for lineage in [scar.id, *(scar.linked_doctrines or [])]:
            if lineage not in touched or lineage in settled:
                continue
            if self.sae.stabilization_event("scar_fermentation", lineage):
                settled.append(lineage)
                self.settle_events.append({
                    "scar_id": scar.id, "lineage": lineage,
                    "epoch_now": getattr(self.sae, "epoch", None),
                })
        return settled

    def _record(self, scar_id: str) -> Optional[Scar]:
        for scar in self._live_scars():
            if scar.id == scar_id:
                return scar
        return None

    def _persist(self) -> None:
        """Ask the RECORD owner to save. SML decides decay; the store owns the file."""
        saver = getattr(self.scar_core, "save_to_file", None)
        if callable(saver):
            saver()

    def status(self) -> Dict[str, Any]:
        return {
            "tracked": len(self._quiet),
            "horizon": SCAR_DECAY_CYCLES,
            "quiet_counts": dict(self._quiet),
            "transitions": len(self.transitions),
            "settle_events": len(self.settle_events),
        }
