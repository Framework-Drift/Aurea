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

RULINGS 46 + 47 - THE DUAL-ENTRY CLAIM ABOVE, FINISHED (2026-07-29)
--------------------------------------------------------------------
"Both doctrine entry paths converge on this single executor" was true of the
CEILING and false of the PRE-FLIGHT. Ruling 24 gave `mutate_doctrine` three
checks before its first write; `birth_doctrine` had NONE, so a birth carrying a
living doctrine's id replaced that belief outright - no collapse, no fossil, no
lineage, no error. Worse than the mutation case it was ruled beside, because a
mutation at least archives what it displaces. `_birth_preflight` closes it, and
`Codex.commit`'s Ruling-18 guard stays where it is as the backstop.

`revert` was the third entry into the doctrine store and the only one that was
not a mutation at all: it hand-rolled its own write token, so the ceiling, the
CAE entry and the settle obligation never applied - and it marked the record
reverted BEFORE attempting a write that could not succeed. **A reversion is a
COUNTER-MUTATION and now takes the ordinary path**, under a NEW id (Rulings
18/19 - restoring content is legitimate, restoring a dead name is revival), with
a real proof, spending a real slot. See `revert` for the full record.

RULING 34 - RESTART IS NOT ABSOLUTION (2026-07-27)
--------------------------------------------------
Until this ruling the ceiling reset on process death. `__init__` built
`epoch=0, epoch_count=0, touched_lineages=set()` and SAE had no save and no
load, so three mutations per epoch became 3N across N restarts. **The only
implemented way to restore mutation budget was to kill the process** - because
`stabilization_event`, the sole legitimate closer, ~~has no caller anywhere in
`src/`~~ *(true when written; SUPERSEDED 2026-07-27 by Ruling 37 - see the
supersession block below)* had no caller anywhere in `src/`. A safety mechanism
whose legitimate reset is unwired and whose illegitimate reset works is not a
partially-built guard; it is a guard pointed the wrong way.

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

SUPERSEDED IN PLACE 2026-07-29 (rider R1) - THE SENDERS ARE BUILT AND WIRED
----------------------------------------------------------------------------
The paragraph below was accurate on 2026-07-27 when Ruling 34-A was written, and
it was made obsolete THE SAME DAY by Ruling 37. It is kept rather than deleted
because it is the record of what was known when the surfacing rule was designed,
and Ruling 34-A's whole argument rests on it: the horizon exists BECAUSE nothing
could close an epoch. Read it as history, not as status.

    ~~`stabilization_event`'s two senders remain UNBUILT - not unwired. Scar
    fermentation and anchor consolidation are mechanisms wanting corpus grounding
    (`scar_logic_core.py` contains zero occurrences of ferment/settle/stabilize/
    consolidate; `compass.py` zero of consolidate; Nova's fermentation is ECHO
    fermentation and DEE's is DOCTRINE fermentation - neither is scar
    fermentation). Until that contract lands, **epochs close never - which canon
    explicitly tolerates and the surfacing rule makes legible.** Do not invent a
    sender.~~

WHAT IS TRUE NOW (Rulings 37 + 37-A, landed `168ec0b`; epochs have closed since):

    SCAR FERMENTATION  `SML._emit_fermentation` (`src/filtration/scar_management.py`)
                       calls `stabilization_event("scar_fermentation", lineage)`
                       when a scar cools ACTIVE -> WANING by SCHEDULE. It is
                       reached only from `SML.transition`, and only on that one
                       edge, which is what makes "cooled" distinguishable from
                       "ignited". It emits per matching lineage key, reading BOTH
                       `scar.id` and `scar.linked_doctrines` (Ruling 26's shape),
                       so the guard below is satisfied by construction.
    ANCHOR CONSOLID.   `CompassStabilityEngine` calls
                       `stabilization_event("anchor_consolidation", lineage)` after
                       a full `CONSOLIDATION_WINDOW` of undisturbed orientation,
                       once per episode, for each touched lineage that anchors a
                       recovered direction. OBSERVED, never induced.
    THE DRIVER         `AureaCore.process_input` calls `sml.advance_cycle()` from
                       the same site as `tcaml.tick()` and `sae.advance_cycle()`,
                       so all three clocks advance together.

    "Do not invent a sender" is DISCHARGED, not relaxed: neither sender was
    invented. Both were grounded in corpus before they were built, and SML EMITS
    while SAE never polls - the budget-holder is not the judge of its own debts.

Ruling 34-A's machinery is UNAFFECTED and is not dead code. The horizon still
surfaces a saturated epoch, because an epoch closing is not the same as an epoch
closing IN TIME: a system under sustained pressure can still spend its budget
faster than anything it changed settles. What changed is that the saturated state
is now escapable by metabolism instead of only by restart.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.doctrine.cae import CAE
from src.doctrine.mutation_proof import (
    ContentDelta, DoctrineMutationProof, all_criteria_absent, validate_proof,
)
from src.doctrine.codex import (
    Codex,
    CodexWriteViolation,
    MutationAuthorization,
    new_authorization_id,
)
from src.utils.atomic_write import atomic_write_json, durable_append_text
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


class EpochStateQuarantined(Exception):
    """RULING 51 (2026-07-31): the epoch state could not be ADJUDICATED.

    A corrupt-but-EXISTING state file is not a missing one. `load()`'s existence
    check distinguishes them three lines before the branch that used to call them
    "genuinely indistinguishable", so defaulting on a parse failure was fail-OPEN
    on the Self-Mutation Ceiling: a file whose real contents recorded a spent
    budget granted a fresh one because it could not be read.

    That is Ruling 34's restart absolution arriving through the persistence layer
    rather than the process boundary, and it needed no process death - a single
    torn write would do it.

        AUREA does not resume a constitution she cannot read.
        She reports that she cannot read it, and she does not change herself
        until it is adjudicated.

    This is an INTEGRITY condition, not an operational refusal, which is why it
    is NOT in DEE's expected pair (Ruling 48): `CeilingExceeded` is SAE
    exercising authority the architecture gave it, and fermenting a doctrine on
    that is correct. This says the engine's own state is unestablished. Reading
    it as a judgement about a doctrine would be reading a breach as a decision,
    so it PROPAGATES to the structural surface (Ruling 25's clause).

    THE ONE LEGITIMATE RESET REMAINS, and it is distinguishable by construction:
    DELETING the file is a deliberate human act and stays a first run. Repairing
    it resumes. Neither is available by accident.
    """


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
    # RULING 45. Optional on the RECORD though required on the CALL, and the
    # asymmetry is deliberate: only `mutate_doctrine` carries a proof, while
    # `MutationRecord` also records reflex mutations and module generation. A
    # record loaded from a state file written before this docket carries None,
    # and that absence is A FACT ABOUT ITS ERA - those mutations really were
    # performed without one - not a value to backfill.
    proof: Optional[DoctrineMutationProof] = None
    executed_at: datetime = field(default_factory=datetime.now)
    reverted: bool = False


class RevertRefusal(str, Enum):
    """WHY a reversion did not happen. RULING 47 (2026-07-29).

    A `str` Enum by the shape rule (`CriterionResult`'s reasoning): ONE
    vocabulary, serialized into the refusal record, with no collision partner
    anywhere in the tree.

    FIVE CAUSES, FIVE MEMBERS, on Ruling 29's discipline - a single signal
    covering causally different events is the defect, and the old code returned
    the SAME bare `None` for "no such authorization" (a caller error) and "that
    record is a birth" (a structurally open question). Reading the first as the
    second is how an unruled semantics stays invisible.
    """

    NO_SUCH_RECORD = "no_such_record"                    # caller error, or already reverted
    NOT_A_DOCTRINE_MUTATION = "not_a_doctrine_mutation"  # another owner's store
    BIRTH_NOT_REVERTIBLE = "birth_not_revertible"        # UNRULED - see `revert`
    SUCCESSOR_NOT_LIVE = "successor_not_live"            # the belief already moved on
    SUCCESSOR_NOT_FOUND = "successor_not_found"          # a discontinuity, not a state
    SUCCESSOR_AMBIGUOUS = "successor_ambiguous"          # nothing is picked


@dataclass(frozen=True)
class RevertOutcome:
    """What `SAE.revert` did, or refused to do, and why.

    FROZEN for `DoctrineMutationProof`'s reason: it is a statement about a
    decision already made, and a caller that could rewrite `performed` after the
    fact could make a refused reversion read as a completed one.

    `performed` and `refusal` are mutually exclusive by construction of every
    return site: a performed reversion carries the committed doctrine, a refused
    one carries a member and a sentence.
    """

    performed: bool
    authorization_id: str
    doctrine: Optional[Doctrine] = None
    refusal: Optional[RevertRefusal] = None
    reason: str = ""
    reverted_from: str = ""      # the successor this counter-mutation ⊗-fossilized
    restored_from: str = ""      # the ancestor whose content came back

    def __bool__(self) -> bool:
        """Truthiness IS `performed`.

        Stated explicitly because the old signature returned `Optional[Doctrine]`,
        so a caller migrating from it writes `if sae.revert(...)`. Without this,
        a dataclass instance is always truthy and every refusal would read as a
        success - the `Codex.__bool__` hazard, in the opposite direction.
        """
        return self.performed


class SAE:
    """Self-Authorship Engine. The only thing in AUREA that may change AUREA."""

    EXECUTOR = "SAE"

    # Ruling 34 res.4 + Ruling 31's path-injectability contract: a durable write
    # path is a CLASS ATTRIBUTE or an `__init__` default - the only two shapes
    # `tests/conftest.py` can reach - and it is resolved at WRITE time so a
    # redirect binds even for an already-constructed SAE.
    RESTART_LOG_PATH = "data/runtime/logs/sae_restarts.jsonl"

    def __init__(self, codex: Codex, cae: Any = None,
                 ceiling: int = SELF_MUTATION_CEILING, racm: Any = None,
                 runtime_path: str = "data/runtime/sae_epoch.json"):
        self.codex = codex
        # RULING 45 - DEFAULT BY CONSTRUCTION. `cae or CAE()` follows RACM's
        # `tcaml or TCAML()` idiom (Ruling 27) and it is what let the
        # `if self.cae is None: return None` branch in `_audit` be DELETED rather
        # than softened: there is no "CAE absent" state left to special-case.
        # `aurea_core` injects ONE shared instance into SAE and DEE.
        #
        # Before this, that branch plus an unwired `aurea_core` meant canon
        # 3a:111 - "no doctrine may be mutated, collapsed, or discarded without a
        # CAE entry" - was a docstring above a soft return, and every `cae_id` in
        # every real run was None.
        self.cae = cae or CAE()                         # append-only audit lineage
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
        # Ruling 47: refused reversions, append-only and legible. NOT PERSISTED -
        # these are this process's refusals to act, and nothing changed, so there
        # is no obligation for a restart to resume (contrast `touched_lineages`,
        # which is a debt). A performed reversion IS durable, because it goes
        # through `mutate_doctrine` like every other mutation.
        self.revert_refusals: List[Dict[str, Any]] = []

        # RULING 51: the adjudication flag. Set by `load()` when the state file
        # EXISTS and could not be read, and never cleared within this process -
        # a repaired file is resumed by CONSTRUCTING an SAE, which starts here at
        # False. Sticky for the process, exactly as Ruling 42 made RIL's refusal
        # sticky, and for the same reason: a quarantine that lapses is not one.
        self.state_quarantined = False

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
                  target_id: str = "", **audit_extra: Any) -> MutationAuthorization:
        """Mint the single-use write token. This is where the ceiling BITES.

        Called directly by MSP Stage_2 for module-generation authorization, and
        internally by mutate_doctrine / mutate_reflex.

        `audit_extra` rides into the CAE entry unchanged - `mutate_doctrine`
        passes the `DoctrineMutationProof` through it (Ruling 45).

        RULING 51: THE QUARANTINE GATE IS HERE, AND HERE IS THE POINT.

        This is the SINGLE SPEND SITE - the header's own claim, that "both
        doctrine entry paths converge on this single executor, so the cap binds
        every path BY CONSTRUCTION rather than by a per-path check", is what
        makes one check sufficient for every counted class. A new mutation path
        cannot forget the gate, because a new mutation path must come here to
        spend a slot.

        It is checked FIRST, before the lineage and exclusion checks, because an
        unadjudicated constitution is a fact about the ENGINE and those are facts
        about the REQUEST. There is no point validating the details of a change
        when it is unknown how much budget has already been spent.

        AND IT IS BEFORE THE COUNTER, which is Ruling 24's spend/refuse boundary
        holding: a refusal costs no ceiling slot, no `_touch` obligation and no
        permanent CAE entry. It also leaves `_cycle_blocked` untouched, so
        Ruling 34-A's saturation clock stays quiet - a quarantined epoch is not a
        SATURATED one, and conflating them would report the wrong condition.
        """
        if self.state_quarantined:
            raise EpochStateQuarantined(
                f"the epoch state at '{self.runtime_path}' EXISTS and could not "
                f"be read, so the Self-Mutation Ceiling cannot be established. "
                f"AUREA does not change herself against a constitution she "
                f"cannot adjudicate - defaulting here would grant a fresh budget "
                f"precisely because the record of the spent one was unreadable. "
                f"Repair the file to resume, or delete it to declare a first run; "
                f"both are deliberate acts and neither happens by accident."
            )

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
        cae_id = self._audit(mutation_class, target_id, collapse_lineage, **audit_extra)
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
               lineage: str, **extra: Any) -> str:
        """3a: no doctrine may be mutated, collapsed, or discarded without a CAE entry.

        RULING 45: the `if self.cae is None: return None` branch that used to sit
        here is GONE, and the return type is no longer Optional. The ledger is
        constructed by default (see `__init__`), so there is no absent state to
        return None for - and a None here was the exact shape of the protection
        failing silently while its own docstring cited the canon forbidding it.

        `extra` carries the `DoctrineMutationProof` on a doctrine mutation, so
        the argument that forced the change is IN the audit entry.
        """
        return self.cae.record(
            event=mutation_class.value,
            target=target_id,
            collapse_lineage=lineage,
            epoch=self.epoch,
            **extra,
        )

    # =================================================================
    # COUNTED CLASS 1 - DOCTRINE MUTATION
    # =================================================================

    def mutate_doctrine(self, doctrine_id: str, new_form: Doctrine,
                        collapse_lineage: str, proof: DoctrineMutationProof,
                        reason: str = "re-pressure") -> Doctrine:
        """Execute a doctrine mutation. The ONLY path by which doctrine content changes.

        RULING 45 - `proof` IS REQUIRED AND HAS NO DEFAULT.

        That is the enforcement, and the absence of a default is the whole of it.
        A default proof would be a FABRICATED ARGUMENT: every mutation would
        carry one, so carrying one would mean nothing, and the field would
        document the shape of an argument rather than the fact of one. A
        proof-less call is UNWRITABLE - a `TypeError` at the call site - rather
        than discouraged (CLAUDE.md section 3).

        It is positioned BEFORE `reason` deliberately: `reason` is a sentence for
        a human, `proof` is the argument, and a caller that supplies only the
        sentence should not silently satisfy the signature.

        The ancestor is not overwritten. It is ⊗-marked and archived to the Fossil Layer
        with its scar trace intact, and the new version records what it descends from.
        AUREA does not get to have always believed the new thing.

        RULING 24: the fossilize/commit pair below is TWO uncoordinated writes, and
        _preflight is what makes them effectively atomic - once it passes, nothing
        structural can raise between them. It runs before authorize(), so a refused
        mutation does not also spend a ceiling slot and a CAE entry on a write that
        never happened.
        """
        # Ruling 45: the proof is checked with the OTHER pre-flight refusals, so
        # an unsupportable argument costs no ceiling slot and no CAE entry -
        # Ruling 24's spend/refuse boundary, extended to cover the new parameter.
        validate_proof(proof)
        self._preflight(doctrine_id, new_form)
        auth = self.authorize(MutationClass.MUTATE_DOCTRINE, collapse_lineage,
                              doctrine_id, proof=proof.as_dict())
        ancestor = self.codex.get(doctrine_id)

        record = MutationRecord(
            authorization_id=auth.authorization_id,
            mutation_class=MutationClass.MUTATE_DOCTRINE,
            target_id=doctrine_id,
            collapse_lineage=collapse_lineage,
            pre_state=ancestor,
            epoch=self.epoch,
            cae_id=auth.cae_id,
            proof=proof,
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
        # RULING 47 (2026-07-29) - THE RECORD IS DURABLE AT THE MOMENT OF THE
        # MUTATION, exactly as the SLOT is.
        #
        # Found while pinning this ruling, not by design: `authorize()` persists
        # (twice - `_touch` and the explicit call), and both happen BEFORE this
        # record exists. So `history` reached disk only on the NEXT `_persist`
        # from anywhere, and a process that died in between resumed with the
        # ceiling slot correctly spent and NO RECORD OF WHAT SPENT IT.
        #
        # `save`'s own docstring already claimed the opposite in terms - "history
        # (including each record's `pre_state` doctrine, SO A ROLLBACK SURVIVES A
        # RESTART)" - which was true of the format and false of the timing. The
        # Docket E shape: a docstring describing a protection the code did not
        # have.
        #
        # It matters more now than it did an hour ago. Ruling 47 makes `revert`
        # resolve through `self.history`, so a lost record is a lost
        # revertibility - and `record.reverted` lives here too, which means an
        # unpersisted flag would let the SAME authorization be reverted twice
        # across a restart: two counter-mutations, two spent slots, one
        # authorization. Ruling 13's one-proposal-ever hazard, on this store.
        self._persist()
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

    def _birth_preflight(self, doctrine: Doctrine) -> None:
        """RULING 46 (2026-07-29): the two id-occupancy checks a BIRTH must pass,
        BEFORE `authorize()` - so a refused birth spends no ceiling slot and
        writes no CAE entry for a mutation that never happened (Ruling 24's
        spend/refuse boundary, applied to the second entry path).

        WHY THIS IS NOT `_preflight`, and why reusing it would have been wrong:
        `_preflight`'s FIRST check is `new_form.id == doctrine_id` - a successor
        may not wear its ancestor's id. A birth HAS NO ANCESTOR. Calling
        `_preflight(doctrine.id, doctrine)` would compare the doctrine's id to
        itself and refuse EVERY birth. So the shared checks are stated here with
        birth's own reasoning, and Ruling 24's method is untouched.

        (i)  A LIVE id is occupied. This is the check birth never had, and the
             one that closes the silent clobber: `Codex.commit` assigns into
             `self.doctrines` with no occupancy test, so this was the only place
             it could be caught at all.
        (ii) A FALLEN id is permanently dead (Rulings 18/19). `Codex.commit`
             ALREADY refuses this one, and that guard is DELIBERATELY LEFT IN
             PLACE - it is the backstop, and defence in depth is the point. What
             changes is WHEN the refusal happens: before the ceiling slot is
             spent rather than after. A birth over a fossil id used to cost a
             mutation from the epoch's budget and a permanent CAE entry to
             discover a refusal that was structurally certain.
        """
        # LIVE FIRST - it is the defect being closed here. The two sets are
        # disjoint by construction (`fossilize` deletes from `doctrines`, and the
        # loader routes by status per Ruling 35), so the order changes no verdict;
        # it states which check is load-bearing and which is a hoisted backstop.
        if doctrine.id in self.codex.doctrines:
            raise MutationPreflightViolation(
                f"'{doctrine.id}' is already a LIVE doctrine, so this birth would "
                f"REPLACE it - no collapse behind the replacement, no fossil of "
                f"what stood there, no lineage recording that anything was "
                f"displaced. A mutation at least archives what it supersedes; a "
                f"birth over a living id does not. If this belief is meant to "
                f"evolve, mutate IT; a new doctrine is born under a new name."
            )
        if doctrine.id in self.codex.fossils:
            raise MutationPreflightViolation(
                f"'{doctrine.id}' is ⊗-fossilized. A fallen doctrine does not "
                f"return to active status by being born again - the fallen id is "
                f"permanently dead (Rulings 18/19, Option B). A doctrine that "
                f"resembles a fossil is born under a NEW id carrying the fallen "
                f"one in its mutation_lineage. Refused HERE so it costs no "
                f"ceiling slot; Codex.commit still refuses it as the backstop."
            )

    def birth_doctrine(self, doctrine: Doctrine, collapse_lineage: str) -> Doctrine:
        """A scar cluster that survived enough pressure to become structure.

        Counted as a doctrine mutation: new doctrine is a change to what AUREA is.

        RULING 46 (2026-07-29): THE BIRTH PATH GETS A PRE-FLIGHT TOO.

        Ruling 24 gave `mutate_doctrine` three checks before its first write, and
        the third of them - "an id collision with a LIVE doctrine would have
        SILENTLY CLOBBERED it" - was found while ruling that one. **Birth never
        got it.** `birth_doctrine` went straight to `authorize()` and then
        `codex.commit()`, and `commit` writes `self.doctrines[doctrine.id] = ...`
        unconditionally, so a birth carrying the id of a living belief REPLACED
        that belief: no collapse behind the replacement, no fossil of what was
        there, no lineage recording that anything was displaced, and no error.

        The same defect Ruling 24 called "identity change through an id
        collision" lived on the OTHER doctrine-entry path for the four days
        between the two rulings, and it lived there in its worse form - a
        mutation at least fossilizes what it displaces, and a birth does not
        even do that. The ancestor is not archived; it is GONE.
        """
        self._birth_preflight(doctrine)
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
        self._persist()          # Ruling 47: see `mutate_doctrine` - the record is
        return committed         # durable at the moment of the mutation.

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
        self._persist()          # Ruling 47: see `mutate_doctrine`.
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
        self._persist()          # Ruling 47: see `mutate_doctrine`.
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

        ~~BOTH SENDERS ARE UNBUILT (Ruling 34-A). This method has no caller in
        `src/`, and that is a DEFERRED CONTRACT, not an oversight. Do not invent
        a sender to exercise it.~~

        SUPERSEDED IN PLACE 2026-07-29 (rider R1). The sentence above was true
        when written and stopped being true on 2026-07-27, when Rulings 37 +
        37-A built both senders (`168ec0b`). It is kept because a reader
        arriving at this method needs to know that the caller-less era was real
        and why: until it ended, THE ONLY WAY TO RESTORE MUTATION BUDGET WAS TO
        KILL THE PROCESS, which is Ruling 34's guard-pointed-the-wrong-way in
        one sentence.

        BOTH SENDERS ARE NOW BUILT AND WIRED:
          `scar_fermentation`    <- `SML._emit_fermentation`, on the scheduled
                                    ACTIVE -> WANING edge only. A MANUAL retire
                                    cannot reach it (Ruling 40) - an operator
                                    action must not close an epoch.
          `anchor_consolidation` <- `CompassStabilityEngine`, after an unbroken
                                    consolidation window, once per episode.
        Both are driven from `AureaCore.process_input`. See the module docstring
        for the full supersession record.

        THE GUARD BELOW IS UNCHANGED BY ANY OF THIS, and that matters more now
        that there are real callers than it did when there were none: a sender
        exists, so the closed VALID set and the `touched_lineages` membership
        test are the only things standing between an unrelated settling event
        and a re-armed ceiling.
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

    def revert(self, authorization_id: str) -> RevertOutcome:
        """GSR-triggered reversion is a CANDIDATE, never automatic (5a Rollback Tracker).

        Restores the pre-state's CONTENT. Does NOT erase the scar trace or the CAE
        entry - the mutation still happened, and the record that it happened is not
        revertible.

        RULING 47 (2026-07-29) - A REVERSION IS A COUNTER-MUTATION, AND IT TAKES
        THE SAME PATH AS EVERY OTHER MUTATION.

        WHAT THIS REPLACED, because it is the reason the ruling exists. The old
        body did three things wrong and they compounded:

          1. It set `record.reverted = True` FIRST, before attempting any work.
          2. It hand-rolled a `MutationAuthorization` with `mutation_class=
             "rollback"` - bypassing `authorize()` entirely, and with it the
             Self-Mutation Ceiling, the CAE entry, `_touch`'s settle obligation
             and the Ruling-24 pre-flight. A doctrine write with a token SAE
             minted outside its own gate is Ruling 5's executor privilege used to
             route around Ruling 34's budget.
          3. It committed `record.pre_state` UNDER THE ANCESTOR'S OWN ID - the id
             the very mutation being reverted had ⊗-fossilized. `Codex.commit`
             refuses that outright (Ruling 18), so the call RAISED.

        Put together: **reversion was not merely unaudited, it was
        non-functional, and it falsified its own record on the way to failing.**
        `reverted = True` was already written when `CodexWriteViolation` came
        back out, so a caller that swallowed the exception would read a history in
        which the mutation had been undone while the Codex still held the
        successor. A rollback tracker whose flag means nothing is worse than no
        tracker, because a forensic record is consulted precisely when memory is
        gone.

        WHAT IT DOES NOW. It builds a successor whose CONTENT is the pre-state's
        and whose ID IS NEW, and puts it through `self.mutate_doctrine`. Every
        guarantee of the ordinary path therefore applies with no special case:
        pre-flight, `authorize()` (ceiling + CAE + `_touch` + durable persist),
        ⊗-fossilization of what is being reverted, and a single-use commit token.

        THE NEW ID IS NOT A CONVENIENCE, it is Rulings 18/19 holding. Restoring
        the ancestor's NAME is the revival those rulings forbid; what a reversion
        legitimately restores is the ancestor's CONTENT, born again through the
        ordinary path under a new id carrying the whole chain in
        `mutation_lineage`. Option B, applied to rollback. Reading the lineage of
        a reverted doctrine shows ancestor -> successor -> reversion: she can see
        that she went there and came back, which is exactly what she must not be
        able to hide.

        AND IT SPENDS A CEILING SLOT, which is the half most likely to look like
        an over-correction and is not. A reversion CHANGES WHAT AUREA BELIEVES.
        That the new content was once her content does not make the change free -
        if it did, an unbounded oscillation between two forms would cost nothing,
        and "three mutation events per epoch" would bound only motion in one
        direction. Reverting is metabolism too.

        `record.reverted` is written ONLY after `mutate_doctrine` returns. On any
        raise the flag is untouched and the exception PROPAGATES - a refused
        reversion is not a completed one, and `CeilingExceeded` reaching the
        caller is the ceiling doing its job.
        """
        record = self._revertible(authorization_id)
        if record is None:
            return self._refuse_revert(
                authorization_id, RevertRefusal.NO_SUCH_RECORD,
                f"no unreverted mutation record carries authorization "
                f"'{authorization_id}'.")

        if record.mutation_class is not MutationClass.MUTATE_DOCTRINE:
            # A reflex change or a module-generation authorization. SAE authorized
            # those; it did not execute them, and their stores have other owners
            # (Ruling 1). Reverting one is a REQUEST to that owner, not a doctrine
            # write, and there is no such request path.
            return self._refuse_revert(
                authorization_id, RevertRefusal.NOT_A_DOCTRINE_MUTATION,
                f"'{record.mutation_class.value}' is not executed by SAE - the "
                f"Reflex Grid owns reflex state and MSP owns module generation. "
                f"Reverting one is a request to that owner, and SAE does not "
                f"write another store to undo an authorization it only issued.")

        if record.pre_state is None:
            # A BIRTH. Undoing one means removing a doctrine that has no prior
            # form to return to, and the only mechanism that removes a live
            # doctrine is ⊗-fossilization - which would mark as FALLEN something
            # that never collapsed. Whether a birth can be un-born, and what the
            # Fossil Layer would then be recording, is UNRULED. The refusal is the
            # whole of v1: the ruling declined to invent the semantics, and a
            # silent `None` here (which is what this returned before) is what let
            # the question stay invisible.
            return self._refuse_revert(
                authorization_id, RevertRefusal.BIRTH_NOT_REVERTIBLE,
                f"'{record.target_id}' was BORN by this authorization; there is "
                f"no pre-state to restore. Un-birthing would ⊗-mark a doctrine "
                f"that never collapsed, and what the Fossil Layer would then be "
                f"recording is an OPEN RULING. Refused, recorded, not invented.")

        live = self.codex.direct_successors(record.target_id)
        if len(live) > 1:
            # Should be unreachable: a doctrine is fossilized by the mutation that
            # succeeds it, so it can be mutated once. If two live doctrines claim
            # the same immediate ancestor, something already went wrong upstream -
            # and choosing between them is the one thing not to do (Ruling 42:
            # when the answer is ambiguous, nothing is picked).
            return self._refuse_revert(
                authorization_id, RevertRefusal.SUCCESSOR_AMBIGUOUS,
                f"'{record.target_id}' has {len(live)} live direct successors "
                f"({', '.join(live)}). A doctrine can only be mutated once, so "
                f"this state should not exist; SAE does not choose which of them "
                f"to counter-mutate.")

        if not live:
            fossilized = self.codex.fossil_direct_successors(record.target_id)
            if fossilized:
                # THE BELIEF HAS ALREADY MOVED ON. What this mutation produced was
                # itself superseded, so there is no present state for the
                # reversion to change - only a claim about history, and history is
                # not revertible. Counter-mutating the CURRENT descendant instead
                # would silently discard every mutation since.
                return self._refuse_revert(
                    authorization_id, RevertRefusal.SUCCESSOR_NOT_LIVE,
                    f"what this mutation produced ({', '.join(fossilized)}) has "
                    f"itself been ⊗-fossilized by a later mutation. Reverting now "
                    f"would be a claim about history rather than a change to the "
                    f"present, and undoing it through the current descendant would "
                    f"silently discard everything that happened since.")
            # NEITHER LIVE NOR FOSSILIZED. A THIRD case and not the same absence
            # (Docket H's NONE_FOUND / NOT_COUNTABLE cut): the record describes a
            # mutation whose product no store holds, which is a discontinuity to
            # report rather than a state to reconcile.
            return self._refuse_revert(
                authorization_id, RevertRefusal.SUCCESSOR_NOT_FOUND,
                f"no doctrine in either store records '{record.target_id}' as its "
                f"immediate ancestor, so what this mutation produced cannot be "
                f"identified. Nothing is guessed from names or content.")

        successor_id = live[0]
        successor = self.codex.get(successor_id)
        pre = record.pre_state

        # THE NEW ID. Derived from the ancestor being restored and the exact
        # authorization being undone, in Nova's `::`-segmented convention
        # (`{doctrine_id}::nova::{echo.id}`), which `_preflight`'s docstring calls
        # the structural one. NO COUNTER IS MINTED - Ruling 42 res.4 makes an id
        # counter continuity state that must persist, and there is nothing to
        # persist here: the id is a function of two recorded facts. One
        # authorization can be reverted once (`reverted` guards it), so it is
        # unique by construction - and if it somehow is not, `_preflight` refuses
        # the collision loudly rather than committing over anything.
        new_id = f"{record.target_id}::revert::{record.authorization_id}"

        new_form = Doctrine(
            id=new_id,
            name=pre.name,
            description=pre.description,
            # From the PRE-STATE. `mutate_doctrine` then unions the successor's
            # scars and the collapse lineage over the top, so the reversion
            # carries the scars of everything it passed through - nothing is
            # dropped, because a reversion does not un-happen the scarring.
            scar_links=list(pre.scar_links),
            tca_tags=list(pre.tca_tags),
            created_at=datetime.now(),
        )

        proof = DoctrineMutationProof(
            contradiction_core={
                "triggers": ["rollback"],
                "strain_source": "SAE.revert - rollback of a recorded mutation "
                                 "(5a Rollback Tracker)",
                "reverted_authorization": record.authorization_id,
                "reverted_cae_id": record.cae_id,
                "reverted_epoch": record.epoch,
                "restored_from": record.target_id,
                "counter_mutating": successor_id,
            },
            # FROM THE RECORD. The collapse lineage the original mutation was
            # authorized on, then the pre-state's own scars: every id here was
            # already written down by a real survived collapse. Ordered dedup, the
            # `_approve` shape.
            scar_lineage=tuple(dict.fromkeys(
                [s for s in [record.collapse_lineage, *pre.scar_links] if s]
            )),
            # No echo authored a reversion. `None` is the ordinary case for this
            # field and is not a gap (see `DEE._echo_provenance`).
            echo_provenance=None,
            content_delta=ContentDelta(
                # The doctrine ACTUALLY being mutated is the successor, not the
                # ancestor whose content is coming back. The delta describes THIS
                # mutation.
                ancestor_id=successor_id,
                name_before=successor.name if successor else "",
                name_after=new_form.name,
                description_before=successor.description if successor else "",
                description_after=new_form.description,
            ),
            # NO CMTE GATE STOOD IN FRONT OF THIS. All five ABSENT is the honest
            # record of that, and `all_criteria_absent()` cannot express anything
            # stronger - see `mutation_proof.py`.
            preserved_invariants=all_criteria_absent(),
            # WHAT THE REVERSION DOES NOT RESOLVE, stated rather than left empty.
            # Undoing the change does not undo the pressure that forced it: the
            # contradiction the original mutation was answering is live again.
            unresolved_residue=(
                f"the contradiction that forced {record.authorization_id} is "
                f"unresolved again - reverting the change does not revert the "
                f"pressure",
                f"⊗{successor_id} is fossilized by this reversion and its id "
                f"is permanently dead (Rulings 18/19)",
            ),
        )

        committed = self.mutate_doctrine(
            doctrine_id=successor_id,
            new_form=new_form,
            collapse_lineage=record.collapse_lineage,
            proof=proof,
            reason=f"reversion of {record.authorization_id}",
        )

        # ONLY NOW. Every raise above and inside `mutate_doctrine` leaves this
        # False, which is the defect this ruling closes.
        record.reverted = True
        self._persist()
        return RevertOutcome(
            performed=True,
            authorization_id=authorization_id,
            doctrine=committed,
            reverted_from=successor_id,
            restored_from=record.target_id,
        )

    def _revertible(self, authorization_id: str) -> Optional[MutationRecord]:
        """The one unreverted record carrying this authorization, or None.

        Separated from `revert` so the history is scanned to completion BEFORE
        `mutate_doctrine` appends the reversion's own record to it - iterating a
        list while something inside the loop appends to it is a trap this method
        exists to keep shut.
        """
        for record in self.history:
            if record.authorization_id == authorization_id and not record.reverted:
                return record
        return None

    def _refuse_revert(self, authorization_id: str, kind: "RevertRefusal",
                       detail: str) -> RevertOutcome:
        """Record a refused reversion and return it TYPED.

        RULING 47: the old body returned a bare `None` for two entirely different
        situations - "this record was a birth" and "no such record" - which is
        Ruling 29's defect (one signal covering causally opposite events) inside a
        return value. Each cause now has its own `RevertRefusal` member and its own
        sentence, and the refusal ACCUMULATES rather than evaporating (Ruling 23:
        unresolved pressure never leaves silently).

        NO CAE ENTRY, and the omission is deliberate. Canon 3a:111 requires an
        entry for a doctrine MUTATED, COLLAPSED OR DISCARDED; a refused reversion
        does none of the three - nothing changed. Writing one would pad the audit
        lineage with non-events, and the ledger's value is that every line in it
        is a change. The refusal is recorded where it happened.
        """
        outcome = RevertOutcome(performed=False, authorization_id=authorization_id,
                                refusal=kind, reason=detail)
        self.revert_refusals.append({
            "authorization_id": authorization_id,
            "refusal": kind.value,
            "reason": detail,
            "epoch": self.epoch,
            "at": datetime.now().isoformat(),
        })
        return outcome

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

        RULING 51 - A QUARANTINED ENGINE DOES NOT WRITE. The guard is HERE rather
        than in `_persist`, and that placement is load-bearing: `_persist` is not
        the only caller. `AureaCore.save_state` calls `save()` DIRECTLY, so a
        guard one level up would have left the pipeline's own checkpoint free to
        replace the unreadable file with a default-valued snapshot.

        That is Ruling 42's stickiness in its exact words - "a file overwritten
        one ingest later was not left BYTE-UNTOUCHED" - and it was not
        hypothetical here: `advance_cycle()` calls `_persist()` every symbolic
        cycle, so before this ruling the FIRST cycle after a corrupt load
        destroyed the evidence and replaced it with something that read as a
        clean first run. The fault erased its own record on the next tick.

        Deliberately NOT recorded per call. The condition is already legible in
        two places that do not grow without bound - `state_quarantined`, and the
        `load` entry on `persist_failures` carrying the original exception - and
        an append here would add a line per cycle forever while saying nothing
        the flag does not already say.
        """
        if self.state_quarantined:
            return

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
        # Rider R3 (2026-07-29): ATOMIC. Mode "w" truncated this file before
        # writing a byte, and a torn epoch snapshot reads back as a corrupt file
        # that `load` records and steps past - CONSTRUCTING AT DEFAULTS, which
        # means `epoch_count=0`. A truncating write on this particular file was
        # therefore a route to a fresh mutation ceiling, which is the restart
        # absolution Ruling 34 exists to forbid, arriving through the persistence
        # layer instead of the process boundary.
        atomic_write_json(self.runtime_path, payload, indent=2)

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
            # stays at defaults, ~~which is the conservative direction only because
            # a first run and a corrupt file are genuinely indistinguishable here.~~
            #
            # SUPERSEDED IN PLACE 2026-07-31 (RULING 51), history kept because the
            # struck sentence is the whole reason the defect survived review: IT
            # WAS FALSE WHEN WRITTEN. The two cases are distinguished THREE LINES
            # ABOVE, by `if not self.runtime_path.exists(): return False` - this
            # branch is reached ONLY when the file exists. So defaulting here was
            # never "the conservative direction"; it was fail-OPEN on the
            # Self-Mutation Ceiling, and a torn write was enough to trigger it.
            #
            # Defaults still load IN MEMORY, for OBSERVATION ONLY - `status()`
            # must be able to report the condition, and an engine that cannot say
            # what is wrong with it is Ruling 22's fail-silent shape applied to
            # the guard that exists to make the fault visible. What changes is
            # that those defaults now authorize NOTHING.
            self.state_quarantined = True
            self.persist_failures.append({
                "op": "load", "path": str(self.runtime_path), "error": repr(exc),
                "quarantined": True,
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
            # RULING 78 res.2: durable at its own write. The `except OSError`
            # below is UNCHANGED and now covers the fsync too - a restart record
            # that cannot be written still lands on `persist_failures` rather
            # than raising into the constructor.
            durable_append_text(path, json.dumps(record, allow_nan=False) + "\n")
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
            # Ruling 45: ADDITIVE and OPTIONAL, so `STATE_VERSION` does NOT move.
            # An older file simply has no `proof` key and its records load with
            # `proof=None` - a truthful statement about mutations performed
            # before proofs existed. Bumping the version would REFUSE those files
            # (Ruling 42's version gate is a refusal), which would discard real
            # epoch state to record the absence of a field that was never owed.
            "proof": record.proof.as_dict() if record.proof is not None else None,
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
            proof=DoctrineMutationProof.from_dict(d.get("proof")),
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
            # RULING 51. Quarantine gates CHANGE, not SIGHT - so the condition is
            # reported here, where a caller asking what state the engine is in
            # gets a straight answer. An engine that refused every mutation while
            # reporting a healthy ceiling would be the fail-silent shape wearing
            # the guard's own uniform.
            "state_quarantined": self.state_quarantined,
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
