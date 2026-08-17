"""M8-b: `escalation-policy.v1` -- the cheapest adequate rung, and the debt.

The hundred-fifth entry ruled the whole of this policy's judgment, and it is
carried as DATA rather than as branching logic:

    S0, S1 -> rung 0 adequate;  S2, S3, S4 -> minimum rung 1.

That is the entire policy. `v2` must be a ONE-OBJECT change - swap
`RULED_MINIMUM_RUNG` and nothing else moves - which is only true if no other
module and no other line ever re-decides what a stake class needs. Nothing here
branches on a stake class; the mapping is looked up.

PURE, on the house discipline. Imports the derived view and nothing else from
`src/`: no ledger, no path, no `open`, no `datetime`, no `random`. The policy
decides; the routing ACT records (`routing_log`), which is the select/record
split for a fourth time.

RUNG OCCUPANCY IS DERIVED FROM RECORDS, NEVER HARDWIRED
-------------------------------------------------------------------------------
Rung 0 is occupied BY CONSTRUCTION and says so with its reason: the deterministic
kernel IS the substrate, and a substrate is not a candidate for its own ladder.

Rung 1's occupancy is DERIVED from consumed qualification records for
`ROLE-EXECUTIVE-DELEGATED-COGNITION`. **It is empty today by TWO INDEPENDENT
DERIVATIONS**, and the distinction matters because only the first is a fact about
the world:

  1. The consumed verdict on the record is REFUSED (Foundry `c1930d6`), so the
     derivation reads EMPTY from what was actually decided.
  2. `ConsumedVerdict` REFUSES to construct a non-REFUSED verdict by design
     (M7-a), so no type in this codebase can even build the record that would
     fill the rung.

The pin exercises the DERIVATION PATH rather than the constant: a fixture
acquisition in the qualified shape - raw ledger data, since no `src/` type can
produce one - derives OCCUPIED and the shortfall disappears. **The ladder fills
by RECORDS ALONE, with no code change.** That is the property worth having, and
it is the reason occupancy is not a boolean somebody edits.

THE SHORTFALL IS A FACT, NOT A WARNING
-------------------------------------------------------------------------------
When the ruled minimum rung is unoccupied, the episode routes to the highest
occupied rung BELOW and the shortfall is RECORDED - stake class, ruled minimum,
actual rung, and the unoccupied rung's derivation basis. Never silent, never
softened, never a warning that isn't a record. L12's pressure-debt discipline
applied to routing: **cognition applied below the stake's ruled minimum is
partial pressure, and it is visible forever.**

On the live tree this fires for EVERY S2+ episode from the first commit. That is
the design working. From here on, AUREA's own records say - honestly and
permanently - which of her dispositions were reached below their ruled cognitive
minimum.

NO MAGNITUDES. A rung is an ORDINAL POSITION on a ruled ladder, not a score, and
the mapping is a lookup over a closed vocabulary. Nothing is counted, weighted or
compared to a cutoff.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple

from src.executive.derived_view import DerivedView
from src.executive.stake_classifier import StakeClass, StakeClassification

__all__ = [
    "POLICY_NAME", "POLICY_VERSION", "REGISTRATION", "DELEGATED_COGNITION_ROLE",
    "Rung", "RungOccupancy", "OccupancyBasis", "RungCensusEntry", "Shortfall",
    "RoutingDecision", "EscalationPolicy", "EscalationIdentityMismatch",
    "UnclassifiedRouting", "RULED_MINIMUM_RUNG",
]

POLICY_NAME = "escalation-policy.v1"
POLICY_VERSION = "1"

#: The role whose qualification records fill rung 1. Compared by EXACT EQUALITY:
#: a verdict about any other role must never move this rung, and the payload has
#: carried `role_id` since M7-a so this is a recorded fact, not an assumption.
DELEGATED_COGNITION_ROLE = "ROLE-EXECUTIVE-DELEGATED-COGNITION"

#: The only verdict value that could ever fill a rung. Declared so the
#: derivation's positive case is legible even though no `src/` type can build it.
QUALIFYING_VERDICT = "QUALIFIED"


class EscalationIdentityMismatch(Exception):
    """Construction named an identity this module does not carry.

    Deliberately NOT `attention_policy.PolicyIdentityMismatch`: a census found
    that name live there, and sharing one exception across two policies would
    make a caller's `except` catch a mismatch it never meant to handle.
    """


class UnclassifiedRouting(Exception):
    """Routing was attempted with no stake classification.

    **UNCLASSIFIED IS REFUSED, NOT CHEAP.** Docket H's cut at the routing layer:
    defaulting a missing classification to S0 would route the one episode nobody
    measured to the cheapest rung, and it would do so silently. A stake nobody
    derived is not a low stake.
    """


class Rung(str, Enum):
    """The cognition ladder. RULED at two rungs for v1.

    Further rungs arrive ONLY by ruling, with their roles - the hundred-fifth
    entry's own words. Ordinal position is the DECLARATION ORDER below and is
    read from `RUNG_ORDER`, never from the member's spelling.
    """

    #: Occupied BY CONSTRUCTION. The substrate is not a candidate for its own
    #: ladder: there is nothing to qualify and nobody to compare it against.
    RUNG_0_DETERMINISTIC_KERNEL = "rung_0_deterministic_kernel"
    #: Occupancy DERIVED from consumed qualification records. EMPTY today.
    RUNG_1_DELEGATED_COGNITION = "rung_1_delegated_cognition"


#: Cheapest first. The ladder's order is DATA, so "the highest occupied rung
#: below" is a list operation rather than a comparison anyone re-implements.
RUNG_ORDER: Tuple[Rung, ...] = (
    Rung.RUNG_0_DETERMINISTIC_KERNEL,
    Rung.RUNG_1_DELEGATED_COGNITION,
)


class RungOccupancy(str, Enum):
    OCCUPIED = "occupied"
    EMPTY = "empty"


class OccupancyBasis(str, Enum):
    """WHY a rung is occupied or empty. Every census entry carries one.

    A census that said only "empty" would leave a reader unable to tell a rung
    nobody has qualified for from one whose candidate was REFUSED on the record
    - and the second is a fact with a citation behind it.
    """

    BY_CONSTRUCTION = "by_construction"
    CONSUMED_VERDICT_QUALIFIED = "consumed_verdict_qualified"
    CONSUMED_VERDICT_REFUSED = "consumed_verdict_refused"
    NO_CONSUMED_VERDICT = "no_consumed_verdict"


# =====================================================================
# THE RULED MAPPING - DATA, carrying its citation
# =====================================================================
#
# THE HUNDRED-FIFTH MANIFEST ENTRY, VERBATIM:
#     "THE v1 CHEAPEST-ADEQUATE MAPPING IS RULED: S0 and S1 -> rung 0 adequate;
#      S2, S3, S4 -> minimum rung 1."
#
# Every stake class is present. A mapping with a hole would make an unmapped
# class fall through to whatever a lookup's default happened to be, which is the
# unexamined judgment this whole layer exists to keep out.
RULED_MINIMUM_RUNG: Mapping[StakeClass, Rung] = MappingProxyType({
    StakeClass.S0_PERIPHERAL: Rung.RUNG_0_DETERMINISTIC_KERNEL,
    StakeClass.S1_LINKED: Rung.RUNG_0_DETERMINISTIC_KERNEL,
    StakeClass.S2_DOCTRINAL: Rung.RUNG_1_DELEGATED_COGNITION,
    StakeClass.S3_STRUCTURAL: Rung.RUNG_1_DELEGATED_COGNITION,
    StakeClass.S4_IDENTITY: Rung.RUNG_1_DELEGATED_COGNITION,
})


REGISTRATION: Mapping[str, Any] = MappingProxyType({
    "identity": POLICY_NAME,
    "version": POLICY_VERSION,
    "kind": "deterministic_non_model_instrument",
    "contract": "registration",
    "declared_invariants": (
        "deterministic: identical inputs yield identical routing, census and "
        "shortfall",
        "pure: no store, clock, io or randomness is reachable from this module",
        "ruled mapping: the v1 stake-to-minimum-rung mapping is data carrying "
        "the hundred-fifth entry's citation, total over StakeClass",
        "occupancy derived: rung occupancy is read from records, never "
        "hardwired, and the ladder fills by records alone",
        "shortfall recorded: routing below the ruled minimum records the debt "
        "as a fact, never a warning",
        "threshold-free: a rung is an ordinal position, never a score",
    ),
})


@dataclass(frozen=True)
class RungCensusEntry:
    """ONE rung's occupancy AND the basis it was derived from."""

    rung: Rung
    occupancy: RungOccupancy
    basis: OccupancyBasis
    #: The acquisition id of the consumed verdict this was derived from, where
    #: one exists. THE CITATION - what makes "empty" checkable rather than
    #: asserted.
    citation: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {"rung": self.rung.value, "occupancy": self.occupancy.value,
                "basis": self.basis.value, "citation": self.citation}


@dataclass(frozen=True)
class Shortfall:
    """THE DEBT. Cognition applied below the stake's ruled minimum.

    Every field is a recorded fact, and together they are the whole of what a
    later reader needs to judge the disposition: what was at stake, what the
    ruling required, what it actually got, and WHY the required rung was
    unavailable.
    """

    stake_class: StakeClass
    ruled_minimum_rung: Rung
    actual_rung: Rung
    unoccupied_rung_basis: OccupancyBasis
    unoccupied_rung_citation: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stake_class": self.stake_class.value,
            "ruled_minimum_rung": self.ruled_minimum_rung.value,
            "actual_rung": self.actual_rung.value,
            "unoccupied_rung_basis": self.unoccupied_rung_basis.value,
            "unoccupied_rung_citation": self.unoccupied_rung_citation,
        }


@dataclass(frozen=True)
class RoutingDecision:
    """The pure result. RECOMPUTABLE, never stored by this module."""

    stake: StakeClassification
    ruled_minimum_rung: Rung
    routed_rung: Rung
    census: Tuple[RungCensusEntry, ...]
    shortfall: Optional[Shortfall]
    policy_name: str
    policy_version: str

    @property
    def adequate(self) -> bool:
        """True iff the episode reached at least its ruled minimum rung."""
        return self.shortfall is None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "stake_derivation": self.stake.as_dict(),
            "ruled_minimum_rung": self.ruled_minimum_rung.value,
            "routed_rung": self.routed_rung.value,
            "rung_census": [c.as_dict() for c in self.census],
            "shortfall": None if self.shortfall is None
            else self.shortfall.as_dict(),
            "adequate": self.adequate,
        }


class EscalationPolicy:
    """`escalation-policy.v1`. Deterministic, pure, named in data."""

    def __init__(self, name: str = POLICY_NAME, version: str = POLICY_VERSION):
        if name != POLICY_NAME or version != POLICY_VERSION:
            raise EscalationIdentityMismatch(
                f"this module implements {POLICY_NAME!r} version "
                f"{POLICY_VERSION!r}; construction named {name!r} version "
                f"{version!r}. A routing record citing a policy that never ran "
                f"cannot be told from a true one.")
        self.name = POLICY_NAME
        self.version = POLICY_VERSION
        self.registration = REGISTRATION

    # -----------------------------------------------------------------
    # OCCUPANCY - derived from records
    # -----------------------------------------------------------------

    @staticmethod
    def census(view: DerivedView) -> Tuple[RungCensusEntry, ...]:
        """Every rung, its occupancy, and the basis. Reads records only.

        Rung 1's derivation takes the LAST consumed verdict for the role, in
        ledger order: the acquisition ledger is append-only, so a later
        qualification supersedes an earlier one by being later, and nothing here
        adjudicates between them. If no verdict for the role exists at all, the
        basis says so - which is a different fact from a REFUSED one, and the
        two must not read alike.
        """
        verdicts = [v for v in view.rungs.consumed_verdicts
                    if v.role_id == DELEGATED_COGNITION_ROLE]
        if not verdicts:
            rung_1 = RungCensusEntry(
                rung=Rung.RUNG_1_DELEGATED_COGNITION,
                occupancy=RungOccupancy.EMPTY,
                basis=OccupancyBasis.NO_CONSUMED_VERDICT)
        else:
            latest = verdicts[-1]
            qualified = latest.verdict == QUALIFYING_VERDICT
            rung_1 = RungCensusEntry(
                rung=Rung.RUNG_1_DELEGATED_COGNITION,
                occupancy=(RungOccupancy.OCCUPIED if qualified
                           else RungOccupancy.EMPTY),
                basis=(OccupancyBasis.CONSUMED_VERDICT_QUALIFIED if qualified
                       else OccupancyBasis.CONSUMED_VERDICT_REFUSED),
                citation=latest.acquisition_id)
        return (
            RungCensusEntry(
                rung=Rung.RUNG_0_DETERMINISTIC_KERNEL,
                occupancy=RungOccupancy.OCCUPIED,
                basis=OccupancyBasis.BY_CONSTRUCTION),
            rung_1,
        )

    # -----------------------------------------------------------------
    # ROUTING - pure, deterministic
    # -----------------------------------------------------------------

    def route(self, stake: Optional[StakeClassification],
              view: DerivedView) -> RoutingDecision:
        """Apply the ruled mapping. Reads; writes nothing.

        REFUSES an absent classification - see `UnclassifiedRouting`.
        """
        if stake is None:
            raise UnclassifiedRouting(
                "routing was attempted with no stake classification. An "
                "unclassified episode is REFUSED, never defaulted to the "
                "cheapest rung: a stake nobody derived is not a low stake.")

        census = self.census(view)
        occupancy = {entry.rung: entry for entry in census}
        minimum = RULED_MINIMUM_RUNG[stake.stake_class]

        if occupancy[minimum].occupancy is RungOccupancy.OCCUPIED:
            return RoutingDecision(
                stake=stake, ruled_minimum_rung=minimum, routed_rung=minimum,
                census=census, shortfall=None, policy_name=self.name,
                policy_version=self.version)

        # THE HIGHEST OCCUPIED RUNG BELOW, read off the ruled order rather than
        # assumed to be rung 0 - the day a third rung is ruled, this needs no
        # edit, and an assumption here would quietly become wrong.
        below = [r for r in RUNG_ORDER[:RUNG_ORDER.index(minimum)]
                 if occupancy[r].occupancy is RungOccupancy.OCCUPIED]
        routed = below[-1]
        unoccupied = occupancy[minimum]
        return RoutingDecision(
            stake=stake, ruled_minimum_rung=minimum, routed_rung=routed,
            census=census,
            shortfall=Shortfall(
                stake_class=stake.stake_class, ruled_minimum_rung=minimum,
                actual_rung=routed,
                unoccupied_rung_basis=unoccupied.basis,
                unoccupied_rung_citation=unoccupied.citation),
            policy_name=self.name, policy_version=self.version)
