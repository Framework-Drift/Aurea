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
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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

    def __init__(self, codex: Codex, cae: Any = None, ceiling: int = SELF_MUTATION_CEILING):
        self.codex = codex
        self.cae = cae                                  # append-only audit lineage
        self.ceiling = ceiling
        self.epoch = 0
        self.epoch_count = 0                            # mutations executed this epoch
        self.history: List[MutationRecord] = []
        self.touched_lineages: set = set()              # what must settle to close the epoch
        # Authorized reflex changes awaiting execution by their owner (the Reflex Grid).
        # SAE authorizes; the owner writes. Ruling 1, same shape as the Codex path.
        self.pending_reflex_changes: List[tuple] = []

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
            raise CeilingExceeded(
                f"Self-Mutation Ceiling reached: {self.epoch_count}/{self.ceiling} in epoch "
                f"{self.epoch} (counted classes: {[c.value for c in MutationClass]}). "
                f"The epoch closes on a STABILIZATION EVENT, not on elapsed time - "
                f"let a touched lineage ferment or an anchor consolidate."
            )

        self.epoch_count += 1
        cae_id = self._audit(mutation_class, target_id, collapse_lineage)

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

        self.touched_lineages.add(collapse_lineage)
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
        self.touched_lineages.add(collapse_lineage)
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
        self.touched_lineages.add(collapse_lineage)
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
        self.touched_lineages.add(collapse_lineage)
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
        """
        VALID = {"scar_fermentation", "anchor_consolidation"}
        if event_type not in VALID:
            return False
        if event_type == "scar_fermentation" and lineage not in self.touched_lineages:
            # Fermentation on a lineage SAE never touched proves nothing about SAE's changes.
            return False

        self.epoch += 1
        self.epoch_count = 0
        self.touched_lineages.clear()
        return True

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

    def status(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "used": self.epoch_count,
            "ceiling": self.ceiling,
            "remaining": max(0, self.ceiling - self.epoch_count),
            "counted_classes": [c.value for c in MutationClass],
            "touched_lineages": sorted(self.touched_lineages),
            "mutations_total": len(self.history),
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
