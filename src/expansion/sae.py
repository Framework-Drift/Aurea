"""
sae.py - SAE: the Self-Authorship Engine.

Canon: 5a_Expansion_Engines.txt, Section 10 (AutogenesisTrigger, dual-entry §G,
       Self-Mutation Ceiling §F, hard exclusions §10.G); 5b MSP.

AUTHORITY (Ruling 1 route-through; Ruling 5 doctrine ownership)
---------------------------------------------------------------
SAE is the SOLE EXECUTOR of self-mutation. Everything else in the doctrine path is a
gate or a requester:

    DEE / CMTE  -> eligibility. Decides a mutation MAY happen. Executes nothing (DEE §IX).
    DBE         -> detector/validator. Feeds DEE. Writes nothing.
    MSSL        -> external merge requester. Writes nothing.
    MSP         -> protocol. Owns no mechanics. Calls SAE to AUTHORIZE.
    SAE         -> executes. Mints the only valid Codex write token.

THE CEILING IS THE POINT (§10.F, extended per T4-01)
----------------------------------------------------
3 mutation events per symbolic epoch, across THREE counted classes:

    {mutate_doctrine, mutate_reflex, module-generation authorization}

Counting only the two mutate_* calls would leave module generation uncapped - AUREA
could not rewrite her doctrine faster than the ceiling, but could manufacture organs
without limit. Both doctrine entry paths (CMTE-reactive and AutogenesisTrigger-
voluntary) converge on this single executor, so the cap binds every path BY
CONSTRUCTION rather than by a per-path check.

An epoch does NOT close on a timer. It closes only on a STABILIZATION EVENT - scar
fermentation on an SAE-touched lineage, or anchor consolidation. A system under
sustained pressure does not get a fresh budget just because time passed. It gets a
fresh budget when something it changed has settled.

Retirement is CEILING-EXEMPT: it removes capacity, it does not run away.

RULING 34 - RESTART IS NOT ABSOLUTION (2026-07-27)
--------------------------------------------------
Until this ruling the ceiling reset on process death. `__init__` built
`epoch=0, epoch_count=0, touched_lineages=set()` and SAE had no save and no
load, so three mutations per epoch became 3N across N restarts. **The only
implemented way to restore mutation budget was to kill the process** - because
`stabilization_event`, the sole legitimate closer, has no caller anywhere in
`src/`. A safety mechanism whose legitimate reset is unwired and whose
illegitimate reset works is not a partially-built guard; it is a guard pointed
the wrong way.

    A process death does not SETTLE a lineage; it INTERRUPTS one.
    An interrupted epoch is not a finished epoch and does not earn a fresh ceiling.

So the state is DURABLE (`runtime_path`, under `data/runtime/` per Ruling 32 -
untracked, gitignored, structurally unable to collide with a seed). **THERE IS
NO SEED EPOCH**: a missing file constructs today's defaults, because an epoch is
something AUREA accumulates, never something she is issued with. Ruling 32's
minimal semantics carry over VERBATIM - whole-file snapshot, no layering, no
delta format, no merge rule. This is no more a licence to redesign persistence
than 31 or 32 were.

And closure is subject to the same rule as restart (resolution 2): **closure
DISCHARGES what settled; it never ERASES what did not.** `touched_lineages` is
a CARRY, not a clear. One principle, two boundaries.

RULING 34-A - THE SATURATED EPOCH IS SURFACED, NEVER FORCE-CLOSED
------------------------------------------------------------------
Persisting a counter nothing can legitimately reset looks like it converts the
ceiling from CONTINUOUS to PERMANENT. **Canon had already adjudicated that, and
in the opposite direction**: 5a:1584's anti-deadlock rule says a saturated epoch
is SURFACED - "rather than force-closing the epoch, which would re-arm mutation
capacity at the exact moment nothing has been metabolized." A ceiling that stays
closed while nothing settles is the INTENDED state.

The real hazard is the lock being durable AND INVISIBLE - a mutation-locked
AUREA with no signal, which is Ruling 22's fail-silent shape applied to her own
growth. Hence `advance_cycle` / `_surface_saturation_if_due`:

    THE COUNTER REPORTS. IT DOES NOT GATE.

It gates exactly one thing - the single surfacing site - and it NEVER closes the
epoch. A saturation count that closed the epoch would be a cutoff on a tally
(§9 standing bar #5, sixth application), and it would be the restart bypass
returning under the counter's own name.

`stabilization_event`'s two senders remain UNBUILT - not unwired. Scar
fermentation and anchor consolidation are mechanisms wanting corpus grounding
(`scar_logic_core.py` contains zero occurrences of ferment/settle/stabilize/
consolidate; `compass.py` zero of consolidate; Nova's fermentation is ECHO
fermentation and DEE's is DOCTRINE fermentation - neither is scar fermentation).
Until that contract lands, **epochs close never - which canon explicitly
tolerates and the surfacing rule makes legible.** Do not invent a sender.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.doctrine.codex import (
    Codex,
    CodexWriteViolation,
    MutationAuthorization,
    new_authorization_id,
)
from src.utils.models import Doctrine


# The Self-Mutation Ceiling: 3 events per symbolic epoch.
SELF_MUTATION_CEILING = 3

# The anti-deadlock horizon (Ruling 34-A, from canon 5a:1584, ruled 2026-07-05).
#
# RECOVERED, NOT COINED. The corpus passage names its own magnitude - "more than
# 5 consecutive symbolic cycles (the corpus's standard 5-cycle horizon)" - so
# nothing is invented here. This is the SIXTH reuse of the canon 5-cycle horizon,
# after RACM's TTL_CYCLES, DEE's pressure half-life, Nova's fermentation
# eligibility, TCAML's lock TTL, and the RB ceiling.
#
# NOTE THE COMPARISON THIS FEEDS IS STRICT: canon says "more than 5", so the
# condition surfaces on the SIXTH consecutive blocked cycle, not the fifth.
SATURATION_HORIZON = 5


class MutationClass(Enum):
    """The THREE counted classes (§10.F as extended by T4-01)."""
    MUTATE_DOCTRINE = "mutate_doctrine"
    MUTATE_REFLEX = "mutate_reflex"
    MODULE_GENERATION = "module_generation"


class CeilingExceeded(Exception):
    """The epoch's mutation budget is spent. This is not an error to retry past.

    AUREA has changed herself three times without anything she changed having settled.
    The correct response is to let something stabilize - not to raise the ceiling.
    """


class ExclusionViolation(Exception):
    """An attempt to mutate something 10.G places outside self-mutation entirely."""


class MutationPreflightViolation(Exception):
    """RULING 24 (2026-07-25): a mutation whose successor id cannot be written.

    Raised BEFORE the first write of `mutate_doctrine`, which is the whole
    point: the fossilize/commit pair is two uncoordinated writes, and the only
    honest way to make it atomic is to make the second one incapable of
    failing. Atomicity by PRE-FLIGHT, never by rollback - an "un-fossilize"
    path moves an id from `fossils` back to `doctrines`, which is mechanically
    the revival Ruling 18 forbids and Ruling 19 settled. Building one "for
    rollback only" would create an executable bypass of both. The wrong path
    must be UNEXECUTABLE, not undoable.
    """


# §10.G - hard exclusions. Autogenesis cannot manufacture a way around these, and
# neither can any mutation path. There is no escape hatch around the load-bearing
# absolutes: the compass she steers by, the law she cannot revise, the place she puts
# what she cannot hold.
EXCLUDED_TARGETS = frozenset({
    "compass", "compass_anchor", "anchor",
    "truth_law", "internal_truth_law", "avt",
    "black_sphere",
})


@dataclass
class MutationRecord:
    """A rollback snapshot. Every mutation snapshots its pre-state.

    Reversion restores collapse-bearing memory WITHOUT erasing the scar trace: AUREA
    can undo what she became, but not that she was pressured into becoming it.
    """
    authorization_id: str
    mutation_class: MutationClass
    target_id: str
    collapse_lineage: str
    pre_state: Optional[Doctrine]
    epoch: int
    cae_id: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.now)
    reverted: bool = False


class SAE:
    """Self-Authorship Engine. The only thing in AUREA that may change AUREA."""

    EXECUTOR = "SAE"

    # Ruling 34 res.4 + Ruling 31's path-injectability contract: a durable write
    # path is a CLASS ATTRIBUTE or an `__init__` default - the only two shapes
    # `tests/conftest.py` can reach - and it is resolved at WRITE time so a
    # redirect binds even for an already-constructed SAE.
    RESTART_LOG_PATH = "logs/sae_restarts.jsonl"

    def __init__(self, codex: Codex, cae: Any = None,
                 ceiling: int = SELF_MUTATION_CEILING, racm: Any = None,
                 runtime_path: str = "data/runtime/sae_epoch.json"):
        self.codex = codex
        self.cae = cae                                  # append-only audit lineage
        self.ceiling = ceiling
        # RACM owns the route to the reflex behavior log (CLAUDE.md §2: the RB
        # log's requesters are RACM and the Grid). SAE SOURCES the saturation
        # condition and asks; it never reaches into the log itself. Injected,
        # duck-typed and optional - the PSI/Nova pattern - so this module's
        # import surface does not grow a reflex-stack dependency.
        self.racm = racm
        # Ruling 34 res.1. An `__init__` default, NOT a class attribute, because
        # conftest's `_redirect_default` resolves defaults BY NAME and this is
        # the shape it reaches. There is deliberately NO SEED_PATH counterpart.
        self.runtime_path = Path(runtime_path)

        self.epoch = 0
        self.epoch_count = 0                            # mutations executed this epoch
        self.history: List[MutationRecord] = []
        self.touched_lineages: set = set()              # what must settle to close the epoch

        # --- Ruling 34-A: the stasis clock ---------------------------------
        # Consecutive symbolic cycles containing at least one attempt blocked by
        # a saturated epoch. A TALLY: nothing compares it except the single
        # surfacing site, and it closes nothing (§9 bar #5).
        self.consecutive_blocked_cycles = 0
        self.saturation_surfaced = False       # once per EPISODE, not per cycle
        # DECLARED AND READABLE; NO CONSUMER EXISTS. RLB (corpus 2b:697 v2.0,
        # `divergence_trigger` at 2b:745 - high bloom + LOW drift = stasis) is
        # UNBUILT. Ruling 28's shape: a named instrument is reported honestly,
        # never promoted. Setting this gates nothing. Do not invent a reader.
        self.divergence_trigger_eligible = False
        self.saturation_events: List[Dict[str, Any]] = []

        # Within-cycle accumulators. DELIBERATELY NOT PERSISTED: a restart begins
        # a fresh cycle, and a cycle interrupted halfway is not a cycle that
        # happened. Persisting them would let a partial cycle count as a whole one.
        self._cycle_blocked = False
        self._cycle_executed = False

        # Ruling 11's `flush_failures` shape: persistence is BEST-EFFORT and never
        # raises. A disk problem must not become a new refusal path that blocks
        # mutation - but it must not vanish either, so it lands here.
        self.persist_failures: List[Dict[str, Any]] = []
        self.restart_records: List[Dict[str, Any]] = []

        # Authorized reflex changes awaiting execution by their owner (the Reflex Grid).
        # SAE authorizes; the owner writes. Ruling 1, same shape as the Codex path.
        self.pending_reflex_changes: List[tuple] = []

        # Ruling 34: an SAE resumes what it owed. Construction is the resume point
        # - not `save_state`/`load_state`, which nothing in the pipeline calls, and
        # which would leave a process kill absolving her exactly as before.
        self.load()

    # =================================================================
    # AUTHORIZATION - the gate every counted class passes through
    # =================================================================

    def authorize(self, mutation_class: MutationClass, collapse_lineage: str,
                  target_id: str = "") -> MutationAuthorization:
        """Mint the single-use write token. This is where the ceiling BITES.

        Called directly by MSP Stage_2 for module-generation authorization, and
        internally by mutate_doctrine / mutate_reflex.
        """
        if not collapse_lineage:
            # AVT.017. A mutation with no scar behind it is not self-authorship;
            # it is self-editing, and AUREA does not edit herself.
            raise ExclusionViolation(
                "AVT.017: no self-mutation without traceable collapse lineage."
            )

        self._check_exclusions(target_id)

        if self.epoch_count >= self.ceiling:
            # RULING 34-A: this is where saturation becomes COUNTABLE. Before it,
            # the ceiling raised and counted NOTHING - so a permanently blocked
            # AUREA produced no signal of any kind. The flag is per-CYCLE, not
            # per-attempt: five blocked attempts in one cycle are one blocked
            # cycle. `advance_cycle` does the tallying.
            self._cycle_blocked = True
            raise CeilingExceeded(
                f"Self-Mutation Ceiling reached: {self.epoch_count}/{self.ceiling} in epoch "
                f"{self.epoch} (counted classes: {[c.value for c in MutationClass]}). "
                f"The epoch closes on a STABILIZATION EVENT, not on elapsed time - "
                f"let a touched lineage ferment or an anchor consolidate."
            )

        self.epoch_count += 1
        self._cycle_executed = True
        # RULING 37 (4): EVERY SPENT SLOT CREATES A SETTLE OBLIGATION.
        #
        # `_touch` used to live at the FOUR counted-class call sites, which left
        # a bare `authorize()` - how MSP Stage_2 spends a module-generation slot
        # - spending budget while recording NO obligation. That is BUDGET
        # WITHOUT DEBT: the epoch could close on fermentation of every VISIBLE
        # lineage while an untracked spend rode through, which is
        # restart-absolution's shape relocated from the process boundary to the
        # CLOSURE boundary.
        #
        # The single SPEND site is now the single TOUCH site, so the two cannot
        # drift apart. This CHANGES what closes an epoch - a module-generation
        # spend now creates an obligation on its lineage - and that is the
        # ruling's intent, not a side effect: module generation is a change she
        # must metabolize like any other.
        self._touch(collapse_lineage)
        cae_id = self._audit(mutation_class, target_id, collapse_lineage)
        # Ruling 34: the spend is durable AT THE MOMENT OF SPENDING. Persisting
        # only on an explicit save_state would leave a process kill restoring the
        # budget, which is the bypass this ruling exists to close.
        self._persist()

        return MutationAuthorization(
            authorization_id=new_authorization_id(),
            executor=self.EXECUTOR,
            mutation_class=mutation_class.value,
            collapse_lineage=collapse_lineage,
            cae_id=cae_id,
            epoch=self.epoch,
        )

    def _check_exclusions(self, target_id: str) -> None:
        if any(x in target_id.lower() for x in EXCLUDED_TARGETS):
            raise ExclusionViolation(
                f"§10.G: '{target_id}' is outside self-mutation. Compass anchors, "
                f"Internal Truth Law, and the Black Sphere are not hers to revise."
            )

    def _audit(self, mutation_class: MutationClass, target_id: str,
               lineage: str) -> Optional[str]:
        """3a: no doctrine may be mutated, collapsed, or discarded without a CAE entry."""
        if self.cae is None:
            return None
        return self.cae.record(
            event=mutation_class.value,
            target=target_id,
            collapse_lineage=lineage,
            epoch=self.epoch,
        )

    # =================================================================
    # COUNTED CLASS 1 - DOCTRINE MUTATION
    # =================================================================

    def mutate_doctrine(self, doctrine_id: str, new_form: Doctrine,
                        collapse_lineage: str, reason: str = "re-pressure") -> Doctrine:
        """Execute a doctrine mutation. The ONLY path by which doctrine content changes.

        The ancestor is not overwritten. It is ⊗-marked and archived to the Fossil Layer
        with its scar trace intact, and the new version records what it descends from.
        AUREA does not get to have always believed the new thing.

        RULING 24: the fossilize/commit pair below is TWO uncoordinated writes, and
        _preflight is what makes them effectively atomic - once it passes, nothing
        structural can raise between them. It runs before authorize(), so a refused
        mutation does not also spend a ceiling slot and a CAE entry on a write that
        never happened.
        """
        self._preflight(doctrine_id, new_form)
        auth = self.authorize(MutationClass.MUTATE_DOCTRINE, collapse_lineage, doctrine_id)
        ancestor = self.codex.get(doctrine_id)

        record = MutationRecord(
            authorization_id=auth.authorization_id,
            mutation_class=MutationClass.MUTATE_DOCTRINE,
            target_id=doctrine_id,
            collapse_lineage=collapse_lineage,
            pre_state=ancestor,
            epoch=self.epoch,
            cae_id=auth.cae_id,
        )

        if ancestor is not None:
            new_form.mutation_lineage = list(ancestor.mutation_lineage) + [ancestor.id]
            new_form.scar_links = list(dict.fromkeys(
                list(ancestor.scar_links) + list(new_form.scar_links) + [collapse_lineage]
            ))
            # ⊗ the fallen ancestor. Needs its own token: one authorization, one write.
            fossil_auth = self._reissue(auth)
            self.codex.fossilize(doctrine_id, fossil_auth, reason=reason)

        new_form.last_mutated = datetime.now()
        committed = self.codex.commit(new_form, auth)

        self.history.append(record)
        return committed

    def _preflight(self, doctrine_id: str, new_form: Doctrine) -> None:
        """RULING 24 (2026-07-25): the three checks that must pass BEFORE any write.

        THERE IS DELIBERATELY NO ROLLBACK PATH HERE, and there must never be one.
        An "un-fossilize" that moves an id from `fossils` back to `doctrines` is
        mechanically identical to the revival Ruling 18 forbids and Ruling 19 settled;
        building it "for rollback only" would create an executable bypass of both.
        Atomicity comes from making failure impossible before the first write - not
        from undoing the second.

        (i)  A successor is a NEW identity. Same-id mutation was ALWAYS broken:
             pre-Ruling-18 it left the id in `doctrines` AND `fossils` at once (durable
             across reload - the exact dual presence Ruling 18 was written to forbid);
             post-Ruling-18 fossilize() succeeds and commit() raises, leaving the
             ancestor fossilized with NO successor installed. A loud vanishing is
             better than a silent corruption, and it is still not the destination.
             Nova already mints `{doctrine_id}::nova::{echo.id}`; this makes that
             convention structural. Nothing returns wearing the dead thing's name.
        (ii) A fallen id is permanently dead (Ruling 18, made permanent by Ruling 19).
        (iii) An id collision with a LIVE doctrine would have SILENTLY CLOBBERED it -
             a belief replaced with no collapse, no fossil, no lineage, no audit,
             found while ruling this one.

        Ruling 18's own guard in Codex.commit is untouched and never fires on the
        legitimate path - which is what a correct guard looks like.
        """
        if new_form.id == doctrine_id:
            raise MutationPreflightViolation(
                f"A mutation's successor may not wear its ancestor's id "
                f"('{doctrine_id}'). The ancestor is ⊗-fossilized by this same "
                f"operation, and a fallen id is permanently dead (Rulings 18/19) - "
                f"so this sequence could only ever fossilize the belief and install "
                f"nothing in its place. A successor is a NEW identity carrying the "
                f"ancestor in its mutation_lineage."
            )
        if new_form.id in self.codex.fossils:
            raise MutationPreflightViolation(
                f"'{new_form.id}' is ⊗-fossilized. A successor may not take a fallen "
                f"doctrine's id (Rulings 18/19) - refused HERE, before the ancestor "
                f"is touched, so the mutation fails whole rather than half."
            )
        if new_form.id in self.codex.doctrines:
            raise MutationPreflightViolation(
                f"'{new_form.id}' is already a LIVE doctrine. Committing over it would "
                f"replace a belief with no collapse behind it, no fossil, and no "
                f"lineage - identity change through an id collision. If this doctrine "
                f"is the one meant to evolve, mutate IT; a successor never lands on an "
                f"id someone else is still using."
            )

    def birth_doctrine(self, doctrine: Doctrine, collapse_lineage: str) -> Doctrine:
        """A scar cluster that survived enough pressure to become structure.

        Counted as a doctrine mutation: new doctrine is a change to what AUREA is.
        """
        auth = self.authorize(MutationClass.MUTATE_DOCTRINE, collapse_lineage, doctrine.id)
        if collapse_lineage not in doctrine.scar_links:
            doctrine.scar_links.append(collapse_lineage)
        committed = self.codex.commit(doctrine, auth)

        self.history.append(MutationRecord(
            authorization_id=auth.authorization_id,
            mutation_class=MutationClass.MUTATE_DOCTRINE,
            target_id=doctrine.id,
            collapse_lineage=collapse_lineage,
            pre_state=None,
            epoch=self.epoch,
            cae_id=auth.cae_id,
        ))
        return committed

    # =================================================================
    # COUNTED CLASS 2 - REFLEX MUTATION
    # =================================================================

    def mutate_reflex(self, reflex_id: str, change: Dict[str, Any],
                      collapse_lineage: str) -> MutationRecord:
        """Change how AUREA reacts. Counted identically to doctrine mutation - a reflex
        is doctrine that fires before thought."""
        auth = self.authorize(MutationClass.MUTATE_REFLEX, collapse_lineage, reflex_id)
        record = MutationRecord(
            authorization_id=auth.authorization_id,
            mutation_class=MutationClass.MUTATE_REFLEX,
            target_id=reflex_id,
            collapse_lineage=collapse_lineage,
            pre_state=None,
            epoch=self.epoch,
            cae_id=auth.cae_id,
        )
        self.history.append(record)
        # NOTE: the reflex-side write executes in the Reflex Grid registry, which owns
        # the reflex objects. SAE authorizes; it does not reach into another store.
        # The `change` payload rides with the authorization to that owner.
        self.pending_reflex_changes.append((reflex_id, change, auth))
        return record

    # =================================================================
    # COUNTED CLASS 3 - MODULE GENERATION  (T4-01: the class the ceiling forgot)
    # =================================================================

    def authorize_module_generation(self, candidate_id: str,
                                    collapse_lineage: str) -> MutationAuthorization:
        """MSP Stage_2. AUREA growing a new organ out of a contradiction she survived.

        This is the deepest recursion in the architecture, and until T4-01 it was the
        one that did not decrement the ceiling. It does now.
        """
        auth = self.authorize(MutationClass.MODULE_GENERATION, collapse_lineage, candidate_id)
        self.history.append(MutationRecord(
            authorization_id=auth.authorization_id,
            mutation_class=MutationClass.MODULE_GENERATION,
            target_id=candidate_id,
            collapse_lineage=collapse_lineage,
            pre_state=None,
            epoch=self.epoch,
            cae_id=auth.cae_id,
        ))
        return auth

    def authorize_module_retirement(self, module_id: str,
                                    collapse_lineage: str) -> MutationAuthorization:
        """⊕-module retirement. CEILING-EXEMPT (5b, T4-03): it removes capacity.

        Deliberately does NOT call authorize(). Capping retirement would mean a system
        that has spent its budget cannot dismantle what is hurting it.
        """
        self._check_exclusions(module_id)
        return MutationAuthorization(
            authorization_id=new_authorization_id(),
            executor=self.EXECUTOR,
            mutation_class="module_retirement",
            collapse_lineage=collapse_lineage or "retirement",
            epoch=self.epoch,
        )

    # =================================================================
    # EPOCH + ROLLBACK
    # =================================================================

    def stabilization_event(self, event_type: str, lineage: str = "") -> bool:
        """Close the epoch. ONLY a stabilization event does this.

        Valid: scar fermentation on an SAE-touched lineage, or anchor consolidation.
        Elapsed time is not a stabilization event, and neither is wanting more budget.

        RULING 34 res.3 - THE EVIDENCE GUARD IS NOW SYMMETRICAL. The
        `scar_fermentation` branch was always tight (closed VALID set plus
        "lineage not in touched_lineages -> return False", with the reasoning
        written at the site). `anchor_consolidation` closed the epoch, zeroed the
        counter and cleared `touched_lineages` UNCONDITIONALLY. **The reasoning
        that justifies the first guard applies verbatim to the second and had not
        been applied**: an anchor event unrelated to anything SAE touched proves
        nothing about SAE's changes, and closing on it would be the restart bypass
        reproduced INSIDE a process. So both branches now require the same thing -
        a lineage SAE actually touched - and the guard is hoisted out of the
        per-type branch to make the symmetry structural rather than duplicated.

        CONSEQUENCE, AND IT IS CORRECT: with `touched_lineages` empty, NOTHING can
        close the epoch. That is not a deadlock - with nothing touched there is no
        budget spent and nothing to restore.

        RULING 34 res.2 - CLOSURE DISCHARGES WHAT SETTLED; IT NEVER ERASES WHAT
        DID NOT. `touched_lineages.clear()` is now a CARRY: the settled lineage is
        removed, every unsettled one crosses into the next epoch and must still
        settle there. The principle that makes restart non-absolving makes closure
        non-absolving - one rule, two boundaries.

        BOTH SENDERS ARE UNBUILT (Ruling 34-A). This method has no caller in
        `src/`, and that is a DEFERRED CONTRACT, not an oversight. Do not invent
        a sender to exercise it.
        """
        VALID = {"scar_fermentation", "anchor_consolidation"}
        if event_type not in VALID:
            return False
        if lineage not in self.touched_lineages:
            # Fermentation - or consolidation - on a lineage SAE never touched
            # proves nothing about SAE's changes.
            return False

        self.epoch += 1
        self.epoch_count = 0
        # THE CARRY (res.2). Discharge exactly what settled; everything else is
        # still owed. `clear()` here would let an epoch closure launder unsettled
        # obligation, which is precisely what restart used to do.
        self.touched_lineages.discard(lineage)
        # A closed epoch is a metabolized one: the stasis run is over by
        # definition, so the clock and its episode flag reset together.
        self._reset_saturation()
        self._persist()
        return True

    # =================================================================
    # RULING 34-A - THE STASIS CLOCK
    # =================================================================

    def advance_cycle(self) -> None:
        """Close the accounting for the symbolic cycle just ended; open the next.

        THE CYCLE BOUNDARY, STATED EXPLICITLY BECAUSE CANON DOES NOT DEFINE IT
        FOR SAE: **one symbolic cycle = one `AureaCore.process_input` pass.**
        That is not invented here - it is the boundary the tree already uses
        twice. `process_input` calls `tcaml.tick()` with the comment "One
        pipeline pass = one TCAML cycle", and `RACM.arbitrate` documents itself
        as resolving "one symbolic cycle's contention" while incrementing
        `self.cycle` once per pass. This method is called from the same site as
        `tcaml.tick()`, so all three advance together and cannot drift.

        THE THREE CASES:
          executed   a mutation went through -> RESET. She was able to change,
                     so whatever run of blockage existed is over. Takes
                     PRECEDENCE when a cycle both executed and blocked (spent
                     the third slot, then refused a fourth): the epoch was not
                     saturated when the execution happened.
          blocked    >=1 attempt refused by a saturated epoch -> INCREMENT, once
                     for the cycle however many attempts were refused.
          neither    SAE was not exercised -> NO CHANGE. This is a JUDGMENT CALL
                     and is flagged as one. Canon's condition is "mutation
                     attempts are blocked", so a cycle with no attempt is not
                     evidence the stasis ended; resetting on silence would make
                     the surfacing unreachable for a system that attempts
                     mutation only occasionally - exactly the stasis the
                     divergence trigger exists for. Holding the condition open
                     is the §7 tiebreaker's direction.
        """
        if self._cycle_executed:
            self._reset_saturation()
        elif self._cycle_blocked:
            self.consecutive_blocked_cycles += 1
            self._surface_saturation_if_due()

        self._cycle_blocked = False
        self._cycle_executed = False
        self._persist()

    def _surface_saturation_if_due(self) -> None:
        """THE ONE SITE THAT COMPARES THE SATURATION COUNT (canon 5a:1584).

        The comparison is STRICT - canon says "more than 5 consecutive symbolic
        cycles", so this fires on the SIXTH, not the fifth.

        THE EPOCH IS NOT TOUCHED HERE, AND MUST NEVER BE. Force-closing "would
        re-arm mutation capacity at the exact moment nothing has been
        metabolized" (5a:1584). The condition is SURFACED and the epoch stays
        saturated; the count keeps climbing.

        ONCE PER EPISODE, not once per cycle: a signal repeated every cycle
        forever is noise, and noise is how a real one stops being read.
        """
        if self.consecutive_blocked_cycles <= SATURATION_HORIZON:
            return
        if self.saturation_surfaced:
            return

        self.saturation_surfaced = True
        self.divergence_trigger_eligible = True

        event = {
            "epoch": self.epoch,
            "consecutive_blocked_cycles": self.consecutive_blocked_cycles,
            "horizon": SATURATION_HORIZON,
            "unsettled_lineages": sorted(self.touched_lineages),
            "surfaced_at": datetime.now().isoformat(),
            "rb_entry_id": None,
        }

        # Canon: "RACM logs reflex-class pressure". SAE sources the condition and
        # ASKS; RACM owns the route to the RB log (Ruling 1). With no RACM
        # injected the eligibility field is still set and the event is still
        # recorded HERE - the surfacing is never lost just because the log
        # channel is absent, which would be the fail-silent shape this ruling
        # exists to close.
        if self.racm is not None and hasattr(self.racm, "record_saturation_pressure"):
            event["rb_entry_id"] = self.racm.record_saturation_pressure(
                epoch=self.epoch,
                blocked_cycles=self.consecutive_blocked_cycles,
                horizon=SATURATION_HORIZON,
                unsettled_lineages=sorted(self.touched_lineages),
            )
        else:
            event["rb_entry_id"] = "UNROUTED: no RACM injected"

        self.saturation_events.append(event)

    def _reset_saturation(self) -> None:
        """The stasis run ended. The clock, the episode flag and the eligibility
        signal fall together - eligibility describes a CURRENT condition, and
        leaving it set after the condition lifted would be a stale status line
        inside live state."""
        self.consecutive_blocked_cycles = 0
        self.saturation_surfaced = False
        self.divergence_trigger_eligible = False

    def _touch(self, lineage: str) -> None:
        """Record an obligation and make it durable in the same breath.

        Every one of the four `touched_lineages` write sites routes through here.
        A lineage recorded in memory but not on disk is an obligation a restart
        would launder - which is the entire defect Ruling 34 closes.
        """
        self.touched_lineages.add(lineage)
        self._persist()

    def revert(self, authorization_id: str) -> Optional[Doctrine]:
        """GSR-triggered reversion is a CANDIDATE, never automatic (5a Rollback Tracker).

        Restores the pre-state. Does NOT erase the scar trace or the CAE entry - the
        mutation still happened, and the record that it happened is not revertible.
        """
        for record in self.history:
            if record.authorization_id == authorization_id and not record.reverted:
                record.reverted = True
                if record.pre_state is not None:
                    auth = MutationAuthorization(
                        authorization_id=new_authorization_id(),
                        executor=self.EXECUTOR,
                        mutation_class="rollback",
                        collapse_lineage=record.collapse_lineage,
                        epoch=self.epoch,
                    )
                    return self.codex.commit(record.pre_state, auth)
                return None
        return None

    # =================================================================
    # RULING 34 res.1 - CONTINUITY. There is NO seed epoch.
    # =================================================================

    def save(self) -> None:
        """Whole-file snapshot to the runtime path.

        RULING 32'S MINIMAL SEMANTICS, VERBATIM: no layering, no delta format,
        no merge rule. A snapshot replaces a snapshot.

        WHAT ROUND-TRIPS, exhaustively - `epoch`, `epoch_count`,
        `touched_lineages`, `history` (including each record's `pre_state`
        doctrine, so a rollback survives a restart), and the three saturation
        fields. `saved_at` is written and read back ONLY into the restart record;
        it is metadata about the file, not state. The within-cycle accumulators
        are deliberately absent - see `__init__`.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "saved_at": datetime.now().isoformat(),
            "epoch": self.epoch,
            "epoch_count": self.epoch_count,
            "touched_lineages": sorted(self.touched_lineages),
            "consecutive_blocked_cycles": self.consecutive_blocked_cycles,
            "saturation_surfaced": self.saturation_surfaced,
            "divergence_trigger_eligible": self.divergence_trigger_eligible,
            "history": [self._record_to_dict(r) for r in self.history],
        }
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self) -> bool:
        """Runtime state if present, ELSE today's defaults. Returns whether state
        was resumed.

        THERE IS NO SEED. Codex, ScarLogicCore and EchoMemory each read a tracked
        seed when no runtime file exists (Ruling 32); an epoch has no equivalent,
        because an epoch is something AUREA ACCUMULATES, never something she is
        issued with. A missing file is a first run, not a missing seed.
        """
        if not self.runtime_path.exists():
            return False
        try:
            with open(self.runtime_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as exc:
            # A corrupt epoch file must not make SAE unconstructable - but it must
            # not silently grant a fresh ceiling either. Recorded loudly; state
            # stays at defaults, which is the conservative direction only because
            # a first run and a corrupt file are genuinely indistinguishable here.
            self.persist_failures.append({
                "op": "load", "path": str(self.runtime_path), "error": repr(exc),
                "at": datetime.now().isoformat(),
            })
            return False

        self.epoch = data.get("epoch", 0)
        self.epoch_count = data.get("epoch_count", 0)
        self.touched_lineages = set(data.get("touched_lineages", []))
        self.consecutive_blocked_cycles = data.get("consecutive_blocked_cycles", 0)
        self.saturation_surfaced = data.get("saturation_surfaced", False)
        self.divergence_trigger_eligible = data.get("divergence_trigger_eligible", False)
        self.history = [self._record_from_dict(d) for d in data.get("history", [])]

        self._record_restart(data)
        return True

    def _persist(self) -> None:
        """BEST-EFFORT save. Never raises.

        Ruling 11's `flush_failures` shape exactly: the observer never gates the
        observed. A disk failure must not become a new refusal path that blocks
        mutation - but it must not vanish either, so it lands on
        `persist_failures` where it is legible.

        FLAGGED, because it is a real trade-off and not a free one: if a save
        fails, the in-memory ceiling still binds for this process, but a restart
        would resume from the last successful snapshot and could recover budget
        that was actually spent. The alternative - raising, and thereby refusing
        mutation whenever the disk misbehaves - is a larger behavioral change
        than this ruling authorized. Recorded for the architect.
        """
        try:
            self.save()
        except OSError as exc:
            self.persist_failures.append({
                "op": "save", "path": str(self.runtime_path), "error": repr(exc),
                "at": datetime.now().isoformat(),
            })

    def _record_restart(self, saved: Dict[str, Any]) -> None:
        """RULING 34 res.4 - A RESTART IS RECORDED, NEVER A CLOSURE.

        The record exists so that resumed state is never indistinguishable from
        continuous state. It is FORENSIC and APPEND-ONLY, and it closes nothing.

        DURATION IS NOT RECORDED, AND THAT IS THE HONEST CHOICE. Both timestamps
        are facts and both are written, but no `duration` field is derived from
        them: an epoch is explicitly NOT wall-clock time (5a:1572), so a
        wall-clock gap would be a number that looks like symbolic duration and is
        not. What IS known is recorded - epochs, counts and unsettled lineages at
        save versus at load.

        Best-effort, never raising (Ruling 31's forensic-write shape); the path
        is resolved from the CLASS ATTRIBUTE at write time so a redirect binds.
        """
        record = {
            "event": "sae_restart",
            "saved_at": saved.get("saved_at"),
            "loaded_at": datetime.now().isoformat(),
            "duration": None,
            "duration_note": ("wall-clock elapsed is not symbolic duration; an "
                              "epoch is not wall-clock time (5a:1572)"),
            "at_save": {
                "epoch": saved.get("epoch", 0),
                "epoch_count": saved.get("epoch_count", 0),
                "unsettled_lineages": sorted(saved.get("touched_lineages", [])),
                "consecutive_blocked_cycles": saved.get("consecutive_blocked_cycles", 0),
            },
            "at_load": {
                "epoch": self.epoch,
                "epoch_count": self.epoch_count,
                "unsettled_lineages": sorted(self.touched_lineages),
                "consecutive_blocked_cycles": self.consecutive_blocked_cycles,
            },
            "note": ("a process death does not SETTLE a lineage; it INTERRUPTS "
                     "one. This restart closed no epoch and restored no budget."),
        }
        self.restart_records.append(record)
        try:
            path = Path(self.RESTART_LOG_PATH)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as exc:
            self.persist_failures.append({
                "op": "restart_log", "path": str(self.RESTART_LOG_PATH),
                "error": repr(exc), "at": datetime.now().isoformat(),
            })

    @staticmethod
    def _record_to_dict(record: MutationRecord) -> Dict[str, Any]:
        return {
            "authorization_id": record.authorization_id,
            "mutation_class": record.mutation_class.value,
            "target_id": record.target_id,
            "collapse_lineage": record.collapse_lineage,
            # Codex owns Doctrine serialization; reusing its helper is a READ of
            # someone else's format, never a write to their store.
            "pre_state": (Codex._to_dict(record.pre_state)
                          if record.pre_state is not None else None),
            "epoch": record.epoch,
            "cae_id": record.cae_id,
            "executed_at": record.executed_at.isoformat(),
            "reverted": record.reverted,
        }

    @staticmethod
    def _record_from_dict(d: Dict[str, Any]) -> MutationRecord:
        pre = d.get("pre_state")
        return MutationRecord(
            authorization_id=d["authorization_id"],
            mutation_class=MutationClass(d["mutation_class"]),
            target_id=d["target_id"],
            collapse_lineage=d["collapse_lineage"],
            pre_state=Doctrine(**Codex._from_dict(pre)) if pre is not None else None,
            epoch=d.get("epoch", 0),
            cae_id=d.get("cae_id"),
            executed_at=datetime.fromisoformat(d["executed_at"]),
            reverted=d.get("reverted", False),
        )

    def status(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "used": self.epoch_count,
            "ceiling": self.ceiling,
            "remaining": max(0, self.ceiling - self.epoch_count),
            "counted_classes": [c.value for c in MutationClass],
            "touched_lineages": sorted(self.touched_lineages),
            "mutations_total": len(self.history),
            # Ruling 34-A. REPORTED, never compared here - the only comparison on
            # the count lives in `_surface_saturation_if_due` (§9 bar #5).
            "consecutive_blocked_cycles": self.consecutive_blocked_cycles,
            "saturation_horizon": SATURATION_HORIZON,
            "saturation_surfaced": self.saturation_surfaced,
            "divergence_trigger_eligible": self.divergence_trigger_eligible,
            "restarts_resumed": len(self.restart_records),
        }

    def _reissue(self, auth: MutationAuthorization) -> MutationAuthorization:
        """A second single-use token for the paired ⊗ write of the same mutation event.

        Does NOT re-count against the ceiling: fossilizing the ancestor is part of ONE
        mutation, not a second one. The alternative - one token doing two writes - would
        break single-use, which is the property that keeps replay off the ceiling.
        """
        return MutationAuthorization(
            authorization_id=new_authorization_id(),
            executor=self.EXECUTOR,
            mutation_class=auth.mutation_class,
            collapse_lineage=auth.collapse_lineage,
            cae_id=auth.cae_id,
            epoch=auth.epoch,
        )
