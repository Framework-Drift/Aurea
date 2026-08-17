"""M8-a: `stake-classifier.v1` -- what a disposition would TOUCH, from records.

The hundred-fifth entry: *stake is never estimated, asserted, or model-supplied.*
This module is that sentence in code. It reads recorded touch-facts and returns
the HIGHEST class whose condition holds, carrying the full derivation - which
surfaces were consulted, which conditions held, and the exact record ids each
held condition consulted. **The floor is what makes escalation lawful**, and a
floor that guessed would make it lawless in a way nobody could audit afterwards.

PURE, ON THE ATTENTION POLICY'S EXACT DISCIPLINE
-------------------------------------------------------------------------------
Imports the derived view and NOTHING else from `src/`. No ledger, no path, no
`open`, no `datetime`, no `random`. It writes nothing and has no act to record -
M8-b's routing act carries this derivation, which is why a classification is a
returned value rather than a log line.

NO MAGNITUDES ANYWHERE - the grounding's own bar
-------------------------------------------------------------------------------
Every condition below is PRESENCE or MEMBERSHIP on records: does this id appear
in that recorded relation. **Nothing is counted and compared to a cutoff.** A
target with one recorded dependent and a target with fifty are both S1, because
the ruled question is what a disposition would TOUCH, not how much of it.

THE TWO-ABSENCES CUT, AT A NEW LAYER
-------------------------------------------------------------------------------
A condition that did not hold and a condition NOBODY COULD CHECK are different
facts, and conflating them here would be the worst possible place: an
unconsulted surface would silently read as "no stake" and route a structural
disposition to the cheapest rung. So every `ConditionResult` carries whether its
surfaces were CONSULTED, and `StakeClassification.fully_derivable` says whether
the whole assignment rested on a complete reading.

    **ONE RULED TOUCH-FACT HAS NO RECORD SURFACE AT ALL AND IS DECLARED
    UNDERIVABLE: the kernel-fixed stratum's adjacency (S4's second half).** A
    tree-wide census at `c047c3b` found no `stratum` / `kernel_fixed` surface
    anywhere in `src/`. It contributes NO classifications, it is named on every
    S4 result, and it is pinned AS underivable so the day a surface appears the
    pin reddens and the gap closes deliberately rather than by drift. S4's FIRST
    half - identity commitments - IS derivable (RIL's threads carry by-id
    entries and `ingest_scar` is wired), so the class is producible and the
    ordering entry's STOP condition does not apply.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Mapping, Tuple

from src.executive.derived_view import DerivedView, StakeSubstrate

__all__ = [
    "CLASSIFIER_NAME", "CLASSIFIER_VERSION", "REGISTRATION",
    "StakeClass", "ConditionResult", "StakeClassification", "StakeClassifier",
    "ClassifierIdentityMismatch", "UNDERIVABLE_TOUCH_FACTS",
]


CLASSIFIER_NAME = "stake-classifier.v1"
CLASSIFIER_VERSION = "1"


class ClassifierIdentityMismatch(Exception):
    """Construction named an identity this module does not carry."""


class StakeClass(str, Enum):
    """WHAT A DISPOSITION WOULD TOUCH. CLOSED AT FIVE, coined by the
    hundred-fifth entry in the Action Ladder's own style - each member defined
    by what it touches, never by a number.

    The definitions below are the ordering entry's, VERBATIM.
    """

    #: **S0 PERIPHERAL** (touches only the claim itself: no recorded
    #: dependents, no doctrine linkage, no suspension involvement)
    S0_PERIPHERAL = "s0_peripheral"

    #: **S1 LINKED** (touches other records: recorded dependents or joins --
    #: ancestry children, prediction references, world propositions -- but no
    #: doctrine standing)
    S1_LINKED = "s1_linked"

    #: **S2 DOCTRINAL** (touches doctrine standing: the target links to one or
    #: more doctrines whose profile a disposition could alter)
    S2_DOCTRINAL = "s2_doctrinal"

    #: **S3 STRUCTURAL** (touches the load-bearing architecture: suspension or
    #: carried-contradiction structures, or entrenched doctrine per the
    #: entrenchment records)
    S3_STRUCTURAL = "s3_structural"

    #: **S4 IDENTITY** (touches identity commitments or the kernel-fixed
    #: stratum's adjacency)
    S4_IDENTITY = "s4_identity"


# The ruled touch-facts with NO derivable record surface at `c047c3b`. Named
# rather than silently omitted: a condition nobody can check must not read as a
# condition that did not hold.
UNDERIVABLE_TOUCH_FACTS: Mapping[str, str] = MappingProxyType({
    "kernel_fixed_stratum_adjacency":
        "S4's second half. A tree-wide census found no `stratum` / "
        "`kernel_fixed` record surface anywhere in `src/`, so no id can be "
        "tested against it. An identity-touch record surface is a kernel "
        "question and is not this slice's to invent.",
})


# THE REGISTRATION SLOT - fork 8.1, RULED AND CLOSED at the hundred-fifth entry:
# the Foundry contract on a DETERMINISTIC NON-MODEL INSTRUMENT is a REGISTRATION
# SURFACE, not a qualification gate. A sole deterministic instrument is verified
# by its pins and registered by its contract slot; a QUALIFICATION GATE applies
# when candidates COMPETE for a rung, and a sole instrument has nothing to be
# compared against.
#
# **DECLARED DATA ONLY.** There is no evaluation machinery here and no gate: no
# code path reads this into a branch, and nothing about a classification depends
# on it. The invariants below are DECLARED, and each one is pinned in
# `tests/test_m8a_stake_classifier.py` - the registration says what the
# instrument claims, and the pins are what verify it.
REGISTRATION: Mapping[str, Any] = MappingProxyType({
    "identity": CLASSIFIER_NAME,
    "version": CLASSIFIER_VERSION,
    "kind": "deterministic_non_model_instrument",
    "contract": "registration",
    "declared_invariants": (
        "deterministic: identical inputs yield identical classification and "
        "identical derivation",
        "pure: no store, clock, io or randomness is reachable from this module",
        "closed vocabulary: the five ruled StakeClass members, no sixth",
        "highest-holds: the assignment is the highest class whose touch "
        "condition holds on the records consulted",
        "threshold-free: every condition is presence or membership on records, "
        "never a count compared to a cutoff",
    ),
})


@dataclass(frozen=True)
class ConditionResult:
    """ONE class's touch-condition, evaluated. Carries its own evidence.

    `consulted_record_ids` is the derivation: the exact ids the condition
    matched on. A held condition with an empty evidence tuple would be an
    assertion, which is the thing this whole module exists to refuse.
    """

    stake_class: StakeClass
    held: bool
    #: The record ids this condition matched on, sorted for determinism.
    consulted_record_ids: Tuple[str, ...]
    #: The substrate surfaces this condition needs.
    required_surfaces: Tuple[str, ...]
    #: Which of those the caller actually supplied.
    consulted_surfaces: Tuple[str, ...]
    #: Ruled touch-facts this condition cannot check at all.
    underivable_facts: Tuple[str, ...] = ()

    @property
    def fully_consulted(self) -> bool:
        """Every surface this condition needs was read, and nothing is missing."""
        return (not self.underivable_facts
                and set(self.required_surfaces) <= set(self.consulted_surfaces))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stake_class": self.stake_class.value,
            "held": self.held,
            "consulted_record_ids": list(self.consulted_record_ids),
            "required_surfaces": list(self.required_surfaces),
            "consulted_surfaces": list(self.consulted_surfaces),
            "underivable_facts": list(self.underivable_facts),
            "fully_consulted": self.fully_consulted,
        }


@dataclass(frozen=True)
class StakeClassification:
    """The classification AND its full derivation. M8-b's record embeds this."""

    stake_class: StakeClass
    target_kind: str
    target_id: str
    classifier_name: str
    classifier_version: str
    #: EVERY condition evaluated, in ruled order S1..S4 - including the ones
    #: that did not hold, because "what was checked and did not hold" is what
    #: makes a lower class auditable rather than merely asserted.
    conditions: Tuple[ConditionResult, ...]

    @property
    def fully_derivable(self) -> bool:
        return all(c.fully_consulted for c in self.conditions)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stake_class": self.stake_class.value,
            "target_kind": self.target_kind,
            "target_id": self.target_id,
            "classifier_name": self.classifier_name,
            "classifier_version": self.classifier_version,
            "conditions": [c.as_dict() for c in self.conditions],
            "fully_derivable": self.fully_derivable,
        }


# ---------------------------------------------------------------------------
# THE TOUCH-CONDITIONS, each derived from a real record surface.
# ---------------------------------------------------------------------------
#
# Each returns the ids it matched on. HELD IS `bool(ids)` AND NOTHING ELSE - no
# count is compared to anything, which is what keeps the classifier
# threshold-free at the one place a magnitude would feel natural.

def _s1_linked(target_id: str, sub: StakeSubstrate) -> Tuple[str, ...]:
    """S1: recorded dependents or joins - ancestry children, prediction
    references, world propositions."""
    hits: List[str] = []
    hits += [citing for citing, cited in sub.claim_citations if cited == target_id]
    hits += [pid for pid, ref in sub.prediction_claim_refs if ref == target_id]
    hits += [wmp for wmp, ref in sub.proposition_refs if ref == target_id]
    return tuple(sorted(set(hits)))


def _s2_doctrinal(target_id: str, sub: StakeSubstrate) -> Tuple[str, ...]:
    """S2: the target links to one or more doctrines whose profile a
    disposition could alter.

    BOTH DIRECTIONS (Ruling 26), because the seed proves they disagree: a
    doctrine target names itself, and a scar target names every doctrine either
    half records for it.
    """
    hits: List[str] = []
    if target_id in sub.live_doctrine_ids:
        hits.append(target_id)
    hits += [doctrine for doctrine, scar in sub.doctrine_scar_links
             if scar == target_id]
    return tuple(sorted(set(hits)))


def _s3_structural(target_id: str, sub: StakeSubstrate) -> Tuple[str, ...]:
    """S3: suspension or carried-contradiction structures, or entrenched
    doctrine per the entrenchment records."""
    hits: List[str] = []
    if target_id in sub.suspension_ids:
        hits.append(target_id)
    hits += [entry for entry, claim in sub.suspension_claims
             if claim == target_id]
    if target_id in sub.entrenched_doctrine_ids:
        hits.append(target_id)
    return tuple(sorted(set(hits)))


def _s4_identity(target_id: str, sub: StakeSubstrate) -> Tuple[str, ...]:
    """S4: identity commitments (derivable) or the kernel-fixed stratum's
    adjacency (UNDERIVABLE - see `UNDERIVABLE_TOUCH_FACTS`).

    The derivable half asks whether RIL has written this id into any identity
    thread. Those entries are BY-ID (Ruling 42), so this is a membership test on
    a recorded relation and never a reach into another owner's store.
    """
    return tuple(sorted({rid for rid in sub.identity_referenced_ids
                         if rid == target_id}))


# (class, predicate, required surfaces, underivable facts) - DECLARED DATA, in
# ruled order. The ladder below walks it in REVERSE for highest-holds.
_CONDITIONS: Tuple[Tuple[StakeClass, Callable[..., Tuple[str, ...]],
                         Tuple[str, ...], Tuple[str, ...]], ...] = (
    (StakeClass.S1_LINKED, _s1_linked,
     ("claim_ancestry", "prediction_ledger", "proposition_ledger"), ()),
    (StakeClass.S2_DOCTRINAL, _s2_doctrinal, ("codex", "scar_store"), ()),
    (StakeClass.S3_STRUCTURAL, _s3_structural,
     ("suspension_stores", "codex"), ()),
    (StakeClass.S4_IDENTITY, _s4_identity, ("identity_threads",),
     ("kernel_fixed_stratum_adjacency",)),
)


class StakeClassifier:
    """`stake-classifier.v1`. Deterministic, pure, and named in data."""

    def __init__(self, name: str = CLASSIFIER_NAME,
                 version: str = CLASSIFIER_VERSION):
        if name != CLASSIFIER_NAME or version != CLASSIFIER_VERSION:
            raise ClassifierIdentityMismatch(
                f"this module implements {CLASSIFIER_NAME!r} version "
                f"{CLASSIFIER_VERSION!r}; construction named {name!r} version "
                f"{version!r}. A routing record citing a classifier that never "
                f"ran is worse than no record, because it cannot be told from a "
                f"true one.")
        self.name = CLASSIFIER_NAME
        self.version = CLASSIFIER_VERSION
        self.registration = REGISTRATION

    def classify(self, target_kind: Any, target_id: str,
                 view: DerivedView) -> StakeClassification:
        """The HIGHEST class whose condition holds; S0 when none does.

        Every condition is evaluated - not merely the ones above the answer -
        because a classification that only recorded its winner would leave a
        reader unable to tell a checked-and-absent condition from an unchecked
        one, which is the distinction this layer exists to preserve.
        """
        sub = view.stake
        kind = getattr(target_kind, "value", target_kind)
        results = [
            ConditionResult(
                stake_class=stake_class,
                held=bool(predicate(target_id, sub)),
                consulted_record_ids=predicate(target_id, sub),
                required_surfaces=surfaces,
                consulted_surfaces=tuple(
                    s for s in surfaces if s in sub.consulted_surfaces),
                underivable_facts=underivable)
            for stake_class, predicate, surfaces, underivable in _CONDITIONS
        ]

        # HIGHEST-HOLDS: walk the ruled order in reverse and take the first that
        # holds. S0 is the floor, reached only when nothing did.
        assigned = StakeClass.S0_PERIPHERAL
        for result in reversed(results):
            if result.held:
                assigned = result.stake_class
                break

        return StakeClassification(
            stake_class=assigned, target_kind=str(kind), target_id=target_id,
            classifier_name=self.name, classifier_version=self.version,
            conditions=tuple(results))
