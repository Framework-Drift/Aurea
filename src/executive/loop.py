"""M7-a: the Executive loop skeleton. It observes; it cannot yet choose.

Heading Phase 7: observe, inspect, choose attention, act. M7-a builds the
cycle's frame and its observation half. Attention is a POLICY DECISION and the
policy is M7-b's named, versioned object (`attention-policy.v1`); until one is
bound, `step()` REFUSES rather than improvising an ordering -- the wrong path
is unexecutable, not discouraged. A loop that picked "something reasonable"
before its policy existed would be an unexamined judgment installed at the top
of the stack, which is the exact thing the heading's section 5 forbids.

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

from src.executive.derived_view import (
    VERDICT_PAYLOAD_KIND,
    ChairState,
    DerivedView,
    derive,
)


class NoAttentionPolicyBound(Exception):
    """M7-a's fail-closed edge: the cycle exists, the chooser does not yet.

    Raised by `step()` while no attention policy is bound. M7-b binds
    `attention-policy.v1` and retires this refusal for bound loops; the
    exception itself stays, because an unbound loop stays refusable.
    """


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
                 acquisitions: Any, policy: Any = None):
        self.obligations = obligations
        self.predictions = predictions
        self.goals = goals
        self.acquisitions = acquisitions
        # M7-a ships with NO policy. M7-b binds attention-policy.v1.
        self.policy = policy

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

    def step(self) -> DerivedView:
        """One cycle. In v-a: observe, then REFUSE at the choosing edge.

        The observation is returned inside the raise's path never -- the
        refusal happens BEFORE any selection so there is no partial act to
        record. A caller that wants the view without choosing calls
        `observe()`; `step()` is the cycle, and the cycle without a policy is
        unexecutable by construction.
        """
        if self.policy is None:
            raise NoAttentionPolicyBound(
                "the cycle reached its choosing edge with no attention policy "
                "bound. M7-b binds `attention-policy.v1` (obligations by due "
                "date, predictions by resolution date, goals by commitment "
                "order); until then the Executive observes and cannot choose, "
                "because a loop that improvised an ordering would be an "
                "unexamined judgment at the top of the stack.")
        raise NotImplementedError(
            "M7-b: policy-bound stepping is the next slice's ordered work; "
            "this line exists so a bound policy cannot silently no-op today.")
