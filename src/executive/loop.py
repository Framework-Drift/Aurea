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
from src.executive.derived_view import (
    VERDICT_PAYLOAD_KIND,
    ChairState,
    DerivedView,
    derive,
)
from src.executive.selection_log import AttentionSelectionRecord, SelectionLog


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
                 selections: Any = None):
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
