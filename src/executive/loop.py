"""The Executive loop: it observes, it chooses through a BOUND policy, and it
records what it chose.

    ~~M7-a: the Executive loop skeleton. It observes; it cannot yet choose.~~
    ~~M7-a builds the cycle's frame and its observation half. Attention is a
    POLICY DECISION and the policy is M7-b's named, versioned object
    (`attention-policy.v1`); until one is bound, `step()` REFUSES...~~

SUPERSEDED IN PLACE 2026-08-16 (M7-b), old text kept verbatim above because it
is the record of the era it describes -- and because a header still reading
"it cannot yet choose" over a module that chooses is false documentation in the
position a reader trusts most (Docket E's class, and this pass authored it).

Heading Phase 7: observe, inspect, choose attention, act. **THE REFUSAL DID NOT
RETIRE -- IT NARROWED TO ITS TRUE SUBJECT.** An UNBOUND loop still refuses at
`step()`, and always will: what changed is that a policy now EXISTS to bind, not
that improvising became acceptable. A loop that picked "something reasonable"
without one would be an unexamined judgment installed at the top of the stack,
which is exactly what the heading's section 5 forbids, and that is as true today
as it was before `attention-policy.v1` was written.

THE LOOP OWNS NOTHING (L10). It holds duck-typed handles to kernel ledgers and
computes `DerivedView`s. Killing this object and constructing a new one over
the same ledgers loses nothing -- M7-d proves that by destruction; the test
file proves it in miniature by reconstruction-equality.

THE FIRST SUBMISSION (ninety-eighth entry, verbatim order): the Executive's
own registration of the REFUSED verdict as a consumed fact, so the loop knows
its chair is empty from the record and never from hardwiring. The registration
writes ONE acquisition through the kernel's own door. Channel law: the
acquisition ledger's channel vocabulary is CLOSED at two doors and its own
docstring rules this case -- an operator supplying external material through
an input path "is honestly USER_INPUT arrival" of that material's assertion.
The verdict document is Foundry-governed content; its arrival HERE is the
operator invoking this registration. USER_INPUT is the door, the payload
carries what arrived, and no third channel member is invented (a third member
is a manifest act, says the enum, and none is needed).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from src.executive.attention_policy import AttentionSelection
from src.executive.inquiry_generator import (
    GENERATOR_NAME,
    CandidatePartition,
    InquiryCandidate,
    InquiryGenerator,
)
from src.executive.escalation_policy import EscalationPolicy, RoutingDecision
from src.executive.inquiry_log import (
    InquiryLog,
    InquiryRecord,
    KernelDisposition,
)
from src.executive.routing_log import RoutingLog, RoutingRecord
from src.executive.stake_classifier import StakeClassifier
from src.executive.derived_view import (
    VERDICT_PAYLOAD_KIND,
    ChairState,
    DerivedView,
    derive,
)
from src.executive.selection_log import AttentionSelectionRecord, SelectionLog
# THE ONE KERNEL VOCABULARY THIS MODULE NAMES, and it names it because this is
# the submitting act: an obligation is admitted AT a target kind, and the
# hundred-second entry ruled which one a prediction-sourced inquiry wears. The
# import is the enum ONLY - no ledger class, no writer, no path.
from src.filtration.obligation_ledger import TargetKind


class NoAttentionPolicyBound(Exception):
    """M7-a's fail-closed edge: the cycle exists, the chooser does not yet.

    Raised by `step()` and `select()` while no attention policy is bound.

    ~~M7-b binds `attention-policy.v1` and retires this refusal for bound
    loops~~ -- SUPERSEDED 2026-08-16: M7-b landed, and the accurate statement is
    that a BOUND loop never reaches this raise, not that the refusal was
    retired. It is regression-pinned and stays forever, because an unbound loop
    stays refusable.
    """


# The refusal's wording, defined ONCE so the two doors that can reach the
# choosing edge cannot drift into saying different things about one rule.
#
# ~~"...M7-b binds `attention-policy.v1` ...; until then the Executive observes
# and cannot choose..."~~ SUPERSEDED IN PLACE 2026-08-16 (M7-b), old sense kept
# above: that sentence described an era in which no policy EXISTED. One exists
# now, so the honest refusal names what the caller must BIND rather than what a
# future slice must build - a message that still said "until then" would be
# false documentation in the position a reader trusts most, which is Docket E's
# class in an error string.
_UNBOUND_MESSAGE = (
    "the cycle reached its choosing edge with no attention policy bound. Bind "
    "`attention_policy.AttentionPolicy` (attention-policy.v1: obligations by "
    "effective due ordinal, then unresolved predictions by recorded-horizon "
    "standing, then committed goals by commitment order). An unbound loop "
    "observes and cannot choose, because a loop that improvised an ordering "
    "would be an unexamined judgment at the top of the stack."
)


class VerdictAlreadyRegistered(Exception):
    """A second verdict registration without a new gate run is a fabrication.

    The M5 verdict happened once. Registering it twice would mint two boundary
    facts for one event; registering a DIFFERENT verdict requires a new
    qualification run in the Foundry and arrives as its own document with its
    own citations -- and v1 has no path for it by design (M7_GROUNDING
    section 3: the slot fills only by a future package clearing the gate).
    """


class MalformedConsumedVerdict(Exception):
    """The registration payload failed its own closed checks."""


class UnmappedKernelDisposition(Exception):
    """The kernel returned a rejection kind this act cannot record.

    Raised rather than defaulted: the whole value of recording a disposition is
    that it is the kernel's own answer, and a nearest-neighbour guess would put
    a fact on a permanent record that nobody ever gave. It fires only if
    `RejectionKind` gains a member without this map gaining one - which is a
    kernel vocabulary change, and therefore a ruling.
    """


@dataclass(frozen=True)
class ConsumedVerdict:
    """The typed fact the loop registers: M5's verdict, with its citations.

    `verdict` must be exactly "REFUSED" -- not because refusal is assumed
    forever, but because THIS type registers the M5 outcome that exists, and a
    QUALIFIED consumption path does not exist yet anywhere in v1. A different
    future verdict is a different door built under its own ruling.
    """

    role_id: str
    verdict: str
    foundry_commit: str
    record_path: str
    protocol_sha256s: Tuple[str, ...]
    failed_surfaces: Tuple[str, ...]
    unestablished_surfaces: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.verdict != "REFUSED":
            raise MalformedConsumedVerdict(
                f"v1 registers the M5 verdict that exists, which is REFUSED; "
                f"got {self.verdict!r}. A QUALIFIED consumption path arrives "
                f"with the first qualified package, under its own ruling.")
        for name in ("role_id", "foundry_commit", "record_path"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise MalformedConsumedVerdict(
                    f"`{name}` must be a non-empty string; got {value!r}. A "
                    f"citation with a blank field cites nothing.")
        if not self.protocol_sha256s:
            raise MalformedConsumedVerdict(
                "at least one protocol digest is required: the verdict binds "
                "to exact reviewed identities, and a registration without "
                "them would be consuming a verdict about nothing in "
                "particular.")

    def payload(self) -> str:
        """Canonical JSON for the acquisition record. Keys sorted, exact."""
        return json.dumps(
            {
                "kind": VERDICT_PAYLOAD_KIND,
                "role_id": self.role_id,
                "verdict": self.verdict,
                "foundry_commit": self.foundry_commit,
                "record_path": self.record_path,
                "protocol_sha256s": list(self.protocol_sha256s),
                "failed_surfaces": list(self.failed_surfaces),
                "unestablished_surfaces": list(self.unestablished_surfaces),
            },
            sort_keys=True,
            allow_nan=False,
        )


class ExecutiveLoop:
    """The loop, v-a: constructed over kernel handles, owning none of them.

    DUCK-TYPED HANDLES, NEVER IMPORTED (episode_record.py's M3-B precedent):
    `obligations`, `predictions`, `goals` are read handles used only through
    the methods `derive` names. `acquisitions` is the ONE handle with a write
    method this loop may call (`record`), and `register_consumed_verdict` is
    the ONE call site -- the column-zero shape, per funnel law.
    """

    ACTOR = "executive-loop.m7a"

    def __init__(self, obligations: Any, predictions: Any, goals: Any,
                 acquisitions: Any, policy: Any = None,
                 selections: Any = None, generator: Any = None,
                 inquiries: Any = None, classifier: Any = None,
                 escalation: Any = None, routings: Any = None):
        self.obligations = obligations
        self.predictions = predictions
        self.goals = goals
        self.acquisitions = acquisitions
        # ~~M7-a ships with NO policy. M7-b binds attention-policy.v1.~~
        #
        # SUPERSEDED IN PLACE 2026-08-16 (M7-b), old text kept above. A policy
        # may now be bound; an UNBOUND loop still refuses at `step()`, and that
        # refusal is regression-pinned rather than retired. `None` remains the
        # default because binding is the CALLER's act: a loop that supplied its
        # own chooser would be choosing how it chooses.
        self.policy = policy
        # DEFAULT-BY-CONSTRUCTION (Ruling 45's `cae or CAE()`, itself Ruling
        # 27's `tcaml or TCAML()` idiom). This is what lets `step()` carry NO
        # `is None` branch for the log: there is no absent state to write
        # around, so the write-gates-the-selection rule cannot be softened by a
        # caller who simply did not pass one. Constructing a log opens no file
        # and writes nothing - the arbiter and the activation layer are
        # composed the same way and stay silent until a door is opened.
        self.selections = selections or SelectionLog()
        # M7-c, same default-by-construction idiom. **THE GENERATOR IS NOT
        # OPTIONAL THE WAY THE POLICY IS**, and the asymmetry is deliberate:
        # a policy is a CHOICE among possible orderings, so binding one is the
        # caller's act and an unbound loop must refuse. `inquiry-generator.v1`
        # is not a choice - it is the only generation there is, and a loop
        # holding one still generates nothing until a door is opened from
        # outside.
        self.generator = generator or InquiryGenerator()
        self.inquiries = inquiries or InquiryLog()
        # M8-b, same default-by-construction idiom and the same asymmetry as
        # the generator: `stake-classifier.v1` and `escalation-policy.v1` are
        # not CHOICES among possible instruments - each is the only one there
        # is, and both are ruled. A loop holding them still routes nothing
        # until a door is opened from outside.
        self.classifier = classifier or StakeClassifier()
        self.escalation = escalation or EscalationPolicy()
        self.routings = routings or RoutingLog()

    # ------------------------------------------------------------------
    # OBSERVE
    # ------------------------------------------------------------------

    def observe(self) -> DerivedView:
        """One pure observation. No writes; observation is not shaping."""
        return derive(self.obligations, self.predictions, self.goals,
                      self.acquisitions)

    # ------------------------------------------------------------------
    # THE FIRST SUBMISSION
    # ------------------------------------------------------------------

    def register_consumed_verdict(self, verdict: ConsumedVerdict) -> str:
        """Write the ONE acquisition that derives the chair's state.

        Derive-first: if the chair is already registered, a second write is
        REFUSED as fabrication (see `VerdictAlreadyRegistered`). The channel
        is USER_INPUT per the ledger's own docstring precedent -- the module
        docstring carries the reasoning in full.
        """
        view = self.observe()
        if view.chair is not ChairState.UNREGISTERED:
            raise VerdictAlreadyRegistered(
                f"the consumed-verdict record already exists at acquisition "
                f"{view.verdict_acquisition_id!r}; the M5 verdict happened "
                f"once and is registered once.")
        # Import here, at the single call site, so the module-level import
        # set of this package stays free of ledger classes: the loop can be
        # handed fakes everywhere EXCEPT the one door it writes through,
        # where the channel member must be the real closed vocabulary.
        from src.external.acquisition_ledger import AcquisitionChannel
        record = self.acquisitions.record(
            verdict.payload(), channel=AcquisitionChannel.USER_INPUT)
        return str(record.acquisition_id)

    # ------------------------------------------------------------------
    # STEP -- the cycle frame; refuses until a policy is bound
    # ------------------------------------------------------------------

    def select(self) -> AttentionSelection:
        """Observe and choose. PURE - it writes nothing and records nothing.

        Separated from `step` deliberately, and for `GoalArbiter.select`'s
        stated reason: a selection computable without recording one is a
        selection anyone can audit, and it is what makes the determinism and
        reconstruction pins measurable without accumulating a single log line.
        """
        if self.policy is None:
            raise NoAttentionPolicyBound(_UNBOUND_MESSAGE)
        return self.policy.select(self.observe())

    # ------------------------------------------------------------------
    # ENDOGENOUS INQUIRY -- M7-c. A GOVERNED PHASE BESIDE THE CYCLE.
    # ------------------------------------------------------------------
    #
    # **WHY GENERATION IS A SIBLING OF `step()` RATHER THAN A STAGE INSIDE IT --
    # the wiring decision the specification left to this lane, with its
    # reasoning.**
    #
    # (1) THE COHERENCE ARGUMENT, which is the one that actually decides it.
    #     `step()` chooses from the attendable set and returns that choice. If
    #     the same call also ADMITTED obligations, it would mutate the very set
    #     it had just selected from, and the record it returns would describe a
    #     kernel state that no longer holds by the time the caller reads it.
    #     Attention allocation and obligation authorship are different acts on
    #     the same records, and fusing them makes the selection's census
    #     unreproducible from the state the caller can observe afterwards.
    #
    # (2) THE HOUSE SHAPE. `AureaCore` exposes `examine_goals`,
    #     `open_goal_activation` and `close_goal_activation` as
    #     `process_input`'s SIBLINGS, each externally invoked with no internal
    #     caller (Rulings 72/73/74's three-doors pattern). These are the same
    #     shape one layer up.
    #
    # (3) PIN 9 IS SATISFIED BY CONSTRUCTION RATHER THAN BY LUCK. The v-a and
    #     v-b files must pass BYTE-UNMODIFIED; a `step()` that also generated
    #     would have to be argued not to disturb them. This way there is
    #     nothing to argue - `step()` is untouched.
    #
    # NOTHING LOOPS AND NOTHING SCHEDULES. Both verbs below are doors opened
    # from outside, exactly as every Docket Q verb is.

    def generate_inquiries(self) -> Tuple[InquiryCandidate, ...]:
        """Observe and notice. PURE - it writes nothing and submits nothing.

        The select/record split for a third time. A candidate set computable
        without recording one is a candidate set anyone can audit, and it is
        what makes the determinism pin measurable without accumulating log
        lines or admitting obligations.
        """
        return self.generator.generate(self.observe())

    @staticmethod
    def _claim_text(candidate: InquiryCandidate) -> str:
        """The obligation's claim text. DERIVED, never composed as prose.

        **THIS IS LOAD-BEARING FOR KERNEL-OWNED DEDUPLICATION, NOT COSMETIC.**
        The obligation ledger's duplicate check compares the NORMALIZED claim
        text against standing obligations for the same target. A generated
        sentence that varied - by phrasing, by ordering, by anything - would
        make two submissions of the SAME discrepancy read as two different
        claims, and the kernel's duplicate disposition would never fire. So the
        text is a deterministic function of the closed class name and the
        source ids: identical discrepancies produce identical text, by
        construction.

        It is also why no natural language is generated anywhere in this slice.
        """
        return (f"{candidate.discrepancy_class.value}: "
                f"{','.join(candidate.source_record_ids)}")

    @staticmethod
    def _disposition(result: Any) -> KernelDisposition:
        """Map the kernel's OWN answer onto the recorded vocabulary.

        A TRANSLATION, NEVER A JUDGEMENT (section 5: the Executive submits, the
        kernel dispositions). Every branch reads a field the ledger set; nothing
        here decides whether a rejection was fair, and an unrecognised rejection
        kind is NOT coerced into a neighbour - it would mean the kernel's
        vocabulary moved, and answering from a stale map would record a
        disposition the kernel never gave.
        """
        if getattr(result, "admitted", False):
            return KernelDisposition.ADMITTED
        kind = getattr(getattr(result, "rejection_kind", None), "value", None)
        mapped = {
            "duplicate": KernelDisposition.REJECTED_DUPLICATE,
            "targetless": KernelDisposition.REJECTED_TARGETLESS,
            "malformed": KernelDisposition.REJECTED_MALFORMED,
        }.get(kind)
        if mapped is None:
            raise UnmappedKernelDisposition(
                f"the obligation ledger returned rejection kind {kind!r}, which "
                f"this act has no recorded member for. The kernel's vocabulary "
                f"has moved; recording the nearest neighbour would put a "
                f"disposition on a permanent record that the kernel never gave.")
        return mapped

    def submit_inquiries(self) -> Tuple[InquiryRecord, ...]:
        """Generate, submit the licensed, and RECORD EVERY candidate.

        **THE PARTITION IS TOTAL HERE, WHICH IS WHERE IT MATTERS.** Both
        branches write a line; there is no path on which a candidate is neither
        admitted nor recorded. That is the specification's one forbidden
        outcome, and it is closed by the loop over the generator's FULL output
        rather than by a filter anyone must remember not to add.

        A licensed candidate is submitted THROUGH THE KERNEL'S OWN DOOR - the
        existing obligation ledger, no new admission path - and the kernel's
        answer is recorded as received, including a duplicate disposition on a
        repeat. **This act never deduplicates and never reads its own log.**
        """
        records = []
        for candidate in self.generate_inquiries():
            if candidate.partition is CandidatePartition.LICENSED:
                result = self.obligations.admit(
                    GENERATOR_NAME, TargetKind.PREDICTION,
                    candidate.source_record_ids[0], self._claim_text(candidate))
                records.append(self.inquiries.record(
                    candidate, self.generator.name, self.generator.version,
                    disposition=self._disposition(result),
                    obligation_id=getattr(result, "obligation_id", None)))
            else:
                # SURFACED, NEVER PURSUED. No admission is attempted at all -
                # `NOT_SUBMITTED` is a different fact from a submission that
                # was refused, and collapsing them would hide which bar stopped
                # it.
                records.append(self.inquiries.record(
                    candidate, self.generator.name, self.generator.version))
        return tuple(records)

    # ------------------------------------------------------------------
    # ESCALATION ROUTING -- M8-b. A GOVERNED PHASE BESIDE THE CYCLE.
    # ------------------------------------------------------------------
    #
    # **WHY ROUTING RIDES BESIDE `step()` RATHER THAN INSIDE IT** - the wiring
    # decision this specification left to the lane, with its reasoning, and it
    # is the M7-c argument sharpened by one more fact.
    #
    # (1) `step()` RETURNS A SELECTION RECORD AND ROUTING ANSWERS A SELECTION.
    #     Fusing them would make one call produce two acts in two logs, and a
    #     caller who wanted only to see what was selected could not get it
    #     without also committing a routing decision. The select/record split
    #     exists precisely so observation is separable from commitment.
    #
    # (2) NOT EVERY SELECTION IS ROUTED. `step()` legitimately returns
    #     NOTHING_ATTENDABLE, and a fused call would then have to invent a
    #     routing for an episode that does not exist - or branch around it,
    #     which is the same thing wearing a guard.
    #
    # (3) PIN 10 IS SATISFIED BY CONSTRUCTION. All prior executive pin FILES
    #     stay byte-unmodified because `step()` is untouched.
    #
    # Nothing loops and nothing schedules: both verbs below are doors opened
    # from outside, as every Executive verb is.

    def route(self, target_kind: Any, target_id: str) -> RoutingDecision:
        """Classify the stake and apply the ruled mapping. PURE - writes nothing.

        The select/record split for a fourth time: a routing computable without
        recording one is a routing anyone can audit, and it is what makes the
        determinism pins measurable without accumulating log lines.
        """
        view = self.observe()
        stake = self.classifier.classify(target_kind, target_id, view)
        return self.escalation.route(stake, view)

    def route_and_record(self, target_kind: Any, target_id: str,
                         selection_id: Optional[str] = None) -> RoutingRecord:
        """Route, and RECORD the act - including its shortfall where one exists.

        The write GATES the act: a failed log write raises and the routing does
        not stand, so there is no path on which a caller receives a routing
        whose record never landed. An escalation decision nobody can inspect is
        the invisible venue decision L5 abolishes - and a SHORTFALL nobody can
        inspect would be worse, because the whole point of recording the debt is
        that it stays visible forever.
        """
        decision = self.route(target_kind, target_id)
        return self.routings.record(
            decision, target_kind=str(getattr(target_kind, "value", target_kind)),
            target_id=target_id, selection_id=selection_id)

    def step(self) -> AttentionSelectionRecord:
        """ONE CYCLE: observe, select, record, return.

        ~~In v-a: observe, then REFUSE at the choosing edge.~~ SUPERSEDED IN
        PLACE 2026-08-16 (M7-b), old text kept. The v-a `NotImplementedError`
        that stood after this refusal is GONE - it existed so that a bound
        policy could not silently no-op, and a bound policy no longer can,
        because it now does the work. **`NoAttentionPolicyBound` STAYS and still
        fires for an unbound loop**: v-b binds a chooser, it does not retire the
        refusal, and an unbound loop stays refusable forever.

        THE ORDER IS OBSERVE -> SELECT -> RECORD, AND THE RECORD GATES. A failed
        write RAISES and the selection does not stand: `record()` is called
        before this method returns anything, so there is no path on which a
        caller receives an allocation whose record never landed. An attention
        allocation nobody can inspect is the invisible venue decision L5
        abolishes.

        **A `NOTHING_ATTENDABLE` CYCLE RETURNS A RECORD LIKE ANY OTHER.** The
        empty kernel is a real outcome, so it takes the same path, the same
        mint, and the same log line - it is not an error, not a `None`, and not
        a skipped write.
        """
        if self.policy is None:
            raise NoAttentionPolicyBound(_UNBOUND_MESSAGE)
        selection = self.policy.select(self.observe())
        return self.selections.record(
            selection,
            policy_name=self.policy.name,
            policy_version=self.policy.version)
