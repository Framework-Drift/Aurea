"""
standing.py - M6-β. STANDING IS A DERIVATION, NEVER A FIELD.

    **WHAT IS STORED IS REFERENCES; WHAT IS READ IS STANDING; THE GAP BETWEEN
    THEM IS WHERE THE HONESTY LIVES.**

A proposition's standing derives at READ TIME from the CURRENT states of the
kernel records it cites. A `supported_by` pointing at a prediction that has since
been FALSIFIED supports nothing; a `contradicted_by` naming a live scar weighs as
the scar's own survival history says, not as the proposition wishes. **References
whose records have MOVED since the proposition was written derive at their
CURRENT state, which is the entire point of deriving.**

R79'S SHAPE, DELIBERATELY VERBATIM (via `standing_profile`, its second reuse)
-------------------------------------------------------------------------------
**Stdlib-only, imports NO store, owns no file, opens none.** Inputs arrive as
ALREADY-READ facts, fetched by the CALLER through the real read surfaces. That
purity is what makes "this never writes to anything it reads" STRUCTURAL rather
than promised - and here it does a second job: a derivation that could reach the
kernel could be talked into CHANGING what it is measuring.

Ruling 63 refused a cached projection ("a stale authority waiting for a trusting
reader"); Ruling 65 refused a persisted derivation trusted over its sources. A
STORED standing would be both at once, at the layer where someone wants a world
proposition to hold up.

THE VOCABULARY IS MIRRORED, AND THE MIRROR IS PINNED RATHER THAN TRUSTED
-------------------------------------------------------------------------------
Purity means this module cannot import `PredictionOutcome` or `DecayState` -
they live in modules that open files. Their VALUES are mirrored below as plain
strings, which is a second definition and therefore a drift risk M3-C named by
name. **THE ANSWER IS NOT TO PREVENT THE DUPLICATION BUT TO DETECT IT**:
`tests/test_m6_standing.py` imports both and asserts the mirrors EQUAL the
enums, so a vocabulary change reddens instead of silently diverging.

THE COMBINATION RULE IS COINED, AND IT IS FLAGGED AS SUCH (L7)
-------------------------------------------------------------------------------
The individual readings are RECOVERED - a falsified prediction supporting
nothing is the prediction ledger's own semantics, and a live scar being live is
`LIVE_STATES`. **What is COINED is how they combine into one verdict**, and no
corpus supplies that. So:

  * the rule is NAMED and VERSIONED (`RULE_NAME` / `RULE_VERSION`), because an
    unnamed combination rule is one nobody can later say was changed;
  * it is DELIBERATELY ORDINAL, NOT NUMERIC - there is no score, no weight, no
    threshold anywhere in this module (section 9's standing bar #5, and the only
    literals are the structural 0 and 1 of "any" and "none");
  * every verdict carries the CONTRIBUTING FACTS that produced it, so a reader
    can disagree with the rule without having to guess what it saw.

**NOTHING PROMOTES ON STANDING.** No doctrine changes, no scar forms, no
authority is granted. The derivation reports; L4 adjudicates.

COINS: `WorldStanding`, `StandingBasis`, `StandingVerdict`, the rule name and
its version. No magnitude.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Sequence, Tuple

__all__ = [
    "RULE_NAME",
    "RULE_VERSION",
    "WorldStanding",
    "StandingBasis",
    "StandingVerdict",
    "ReferenceState",
    "derive_standing",
    "PREDICTION_CONFIRMED",
    "PREDICTION_FALSIFIED",
    "PREDICTION_UNRESOLVED",
    "SCAR_LIVE_STATES",
]

# **THE COMBINATION RULE IS COINED (L7).** Named and versioned so a later change
# is a visible event rather than a silent one.
RULE_NAME = "m6.standing.v1"
RULE_VERSION = 1

# ---------------------------------------------------------------------
# MIRRORED VOCABULARY - a second definition, DETECTED rather than prevented
# ---------------------------------------------------------------------
# `prediction_ledger.PredictionOutcome` and `scar_management.LIVE_STATES` live in
# modules that open files, so this pure module cannot import them. The mirrors
# below are pinned EQUAL to the enums by `tests/test_m6_standing.py`, which is
# M3-C's move: a duplicated vocabulary nobody compares is the hazard; one a test
# compares every run is a boundary.
PREDICTION_CONFIRMED = "confirmed"
PREDICTION_FALSIFIED = "falsified"
PREDICTION_UNRESOLVED = "unresolved"
SCAR_LIVE_STATES: Tuple[str, ...] = ("active", "locked")


class WorldStanding(str, Enum):
    """What a proposition's references currently say about it. CLOSED at four.

    ORDINAL, NOT NUMERIC. There is no score behind these and none is derivable
    from them - a reader who wants to know WHY reads `basis` and the contributing
    facts, not a number this module would have had to invent.
    """

    UNGROUNDED = "ungrounded"      # cites nothing; derives nothing
    SUPPORTED = "supported"        # live support, no live contradiction
    CONTESTED = "contested"        # live support AND live contradiction
    UNDERCUT = "undercut"          # live contradiction, no live support


class StandingBasis(str, Enum):
    """WHY a reference counted, or did not. Recorded per reference.

    Each member is a RECOVERED reading of another store's own semantics - what
    is coined is only how they combine (see the module docstring).
    """

    NO_REFERENCES = "no_references"
    PREDICTION_CONFIRMED_SUPPORTS = "prediction_confirmed_supports"
    PREDICTION_FALSIFIED_SUPPORTS_NOTHING = "prediction_falsified_supports_nothing"
    PREDICTION_UNSETTLED = "prediction_unsettled"
    SCAR_LIVE = "scar_live"
    SCAR_COOLED = "scar_cooled"
    RECORD_PRESENT = "record_present"
    RECORD_STATE_UNKNOWN = "record_state_unknown"


@dataclass(frozen=True)
class ReferenceState:
    """One reference's CURRENT state, as the caller read it from the kernel.

    `state` is whatever that store reports today - a prediction outcome, a scar
    decay state, or `None` for a record whose store has no state to report
    (a claim, an obligation, an episode: present or absent, nothing more).

    **THE CALLER FETCHES THIS**, because this module touches no store. That is
    not an inconvenience to route around: it is the reason a derivation cannot
    change what it measures.
    """

    field: str                       # supported_by | contradicted_by | predicted_by
    kind: str                        # the KernelRefKind value
    record_id: str
    present: bool = True
    state: Optional[str] = None


@dataclass(frozen=True)
class StandingVerdict:
    """A derived standing AND the facts that produced it.

    **THE CONTRIBUTING FACTS ARE PART OF THE VERDICT, NOT AN ANNEX** (Ruling
    45's move): a reader can disagree with a coined combination rule only if the
    verdict says what it saw.
    """

    standing: WorldStanding
    rule: str
    rule_version: int
    live_support: Tuple[str, ...] = ()
    live_contradiction: Tuple[str, ...] = ()
    discounted: Tuple[Tuple[str, str], ...] = ()   # (record_id, basis)
    basis: Tuple[StandingBasis, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "standing": self.standing.value,
            "rule": self.rule,
            "rule_version": self.rule_version,
            "live_support": list(self.live_support),
            "live_contradiction": list(self.live_contradiction),
            "discounted": [list(pair) for pair in self.discounted],
            "basis": [b.value for b in self.basis],
        }


def _read_reference(ref: ReferenceState) -> Tuple[bool, StandingBasis]:
    """Does this reference COUNT right now, and on what basis?

    **THE INDIVIDUAL READINGS ARE RECOVERED, NOT COINED.** A falsified
    prediction supporting nothing is the prediction ledger's own semantics; a
    scar being live is `LIVE_STATES`. What this module coins is only the
    combination (see `derive_standing`).
    """
    if not ref.present:
        # A reference whose record is GONE counts for nothing - and this is not
        # the write law failing: the ledger checked at write, and the kernel has
        # moved since. Deriving at the CURRENT state is the whole point.
        return False, StandingBasis.RECORD_STATE_UNKNOWN

    if ref.kind == "prediction":
        if ref.state == PREDICTION_CONFIRMED:
            return True, StandingBasis.PREDICTION_CONFIRMED_SUPPORTS
        if ref.state == PREDICTION_FALSIFIED:
            # **A FALSIFIED PREDICTION SUPPORTS NOTHING.** R64's reversed-meaning
            # defect, refused at its source: a refuted expectation must never
            # read as standing knowledge.
            return False, StandingBasis.PREDICTION_FALSIFIED_SUPPORTS_NOTHING
        return False, StandingBasis.PREDICTION_UNSETTLED

    if ref.kind == "scar":
        if ref.state in SCAR_LIVE_STATES:
            return True, StandingBasis.SCAR_LIVE
        # A cooled scar is PRESERVED but no longer exerts pressure (Ruling 54's
        # cut: what is on record vs what still bears).
        return False, StandingBasis.SCAR_COOLED

    # Claims, doctrines, obligations, episodes: present or absent, nothing more.
    # This module does not invent a state a store does not report.
    return True, StandingBasis.RECORD_PRESENT


def derive_standing(references: Sequence[ReferenceState]) -> StandingVerdict:
    """Derive one proposition's standing from its references' CURRENT states.

    **THE COMBINATION RULE, COINED AND STATED IN FULL:**

        no references at all                -> UNGROUNDED
        live support and live contradiction -> CONTESTED
        live support only                   -> SUPPORTED
        live contradiction only             -> UNDERCUT
        neither (all discounted)            -> UNGROUNDED

    ORDINAL, NOT NUMERIC: it counts NOTHING. Three live supports and one live
    contradiction is CONTESTED exactly as one and one is - because a rule that
    weighed them would need a coined magnitude at the point someone wants a
    proposition to hold up, and section 9's bar #5 has refused that nine times.

    **THE LAST ROW IS THE ONE WORTH READING TWICE.** A proposition whose every
    citation has been falsified or has cooled derives UNGROUNDED, not UNDERCUT:
    it is not opposed, it is unsupported, and those are different facts. The
    discounted references and their bases ride on the verdict so the difference
    is legible rather than inferred.
    """
    if not references:
        return StandingVerdict(
            standing=WorldStanding.UNGROUNDED, rule=RULE_NAME,
            rule_version=RULE_VERSION, basis=(StandingBasis.NO_REFERENCES,))

    support, contra, discounted, bases = [], [], [], []
    for ref in references:
        counts, basis = _read_reference(ref)
        bases.append(basis)
        if not counts:
            discounted.append((ref.record_id, basis.value))
        elif ref.field == "contradicted_by":
            contra.append(ref.record_id)
        else:
            # `supported_by` and `predicted_by` both bear FOR the proposition;
            # a prediction that bears against it is a `contradicted_by`.
            support.append(ref.record_id)

    if support and contra:
        standing = WorldStanding.CONTESTED
    elif support:
        standing = WorldStanding.SUPPORTED
    elif contra:
        standing = WorldStanding.UNDERCUT
    else:
        standing = WorldStanding.UNGROUNDED

    return StandingVerdict(
        standing=standing, rule=RULE_NAME, rule_version=RULE_VERSION,
        live_support=tuple(support), live_contradiction=tuple(contra),
        discounted=tuple(discounted), basis=tuple(bases))
