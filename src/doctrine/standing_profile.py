"""
standing_profile.py - M3-C. STANDING IS A DERIVATION, NEVER A STORE.

**WHAT A DOCTRINE'S STANDING IS, IS A FOLD OVER WHAT HAPPENED TO IT** - the
obligations admitted about it, the episodes opened against those obligations,
the pressure actually applied, and the pressure NOTICED AND NOT APPLIED. It is
computed on demand from the records and kept nowhere.

R79'S SHAPE, DELIBERATELY VERBATIM
-------------------------------------------------------------------------------
`src/retrieval/divergence.py` is the precedent and this follows it exactly:
**stdlib-only, imports NO store, owns no file, opens none, and takes
ALREADY-READ records through their owners' own readers.** That purity is what
makes "this never writes to anything it reads" STRUCTURAL rather than promised -
a module that cannot reach a store cannot be talked into repairing one.

Ruling 63 refused a cached projection ("a stale authority waiting for a trusting
reader"); Ruling 65 refused a persisted derivation trusted over its sources.
**A STORED STANDING WOULD BE BOTH AT ONCE**, and at the layer where it would be
consulted precisely when someone wanted a decision to go a particular way. There
is no `save`, no `_persist`, no path, and no funnel import. AST-pinned.

THE VOCABULARY IS MIRRORED, AND THE MIRROR IS PINNED RATHER THAN TRUSTED
-------------------------------------------------------------------------------
Purity means this module cannot import `PressureClass` or `EpisodeOutcome` -
those live in a module that opens files. So their VALUES are mirrored below as
plain strings, which is a second definition and therefore a drift risk that R79
named by name.

**THE ANSWER IS NOT TO PREVENT THE DUPLICATION BUT TO DETECT IT.**
`tests/test_m3c.py` imports both and asserts the mirrors EQUAL the enums, so a
vocabulary change reddens instead of silently diverging - the same move Ruling
33 made for the ORE/HAIL member disjointness ("pinned, not assumed"). A
duplicated vocabulary nobody compares is the hazard; a duplicated vocabulary a
test compares every run is a boundary.

COVERAGE-KEYED AUTHORIZATION - THE POINT OF THE WHOLE SLICE
-------------------------------------------------------------------------------
**A PROFILE WITH MODEL_ADVERSARIAL-ONLY SURVIVALS FAILS TO AUTHORIZE AN
EMPIRICAL DECISION, WHATEVER ITS COUNTS.** Not "is flagged", not "scores lower"
- FAILS, structurally, at a thousand survivals as surely as at one.

That is L2/K11 made unprofitable rather than merely detectable. If argument
against a model could accumulate into empirical standing, the cheapest possible
pressure would be the most rewarding one to farm, and the system would drift
toward believing whatever it could out-argue. **The gate is keyed on WHAT KIND
of pressure was survived, not on how much of it there was** - which is also why
this module contains no threshold, no score, and no weight anywhere (§9 standing
bar #5).

NEGATIVE SPACE IS PART OF THE PROFILE, NOT AN ANNEX
-------------------------------------------------------------------------------
What was NOT done is standing information: obligations DEFERRED (with the reason
and the due ordinal), pressure classes NEVER EXERCISED against this target, and
episodes that ended UNRESOLVED_AT_BOUND with the bounds they faced. **A SHALLOW
SURVIVAL STAYS DISTINGUISHABLE FROM A DEEP ONE FOREVER**, which is M3-A's
counting rule paying out at the layer that reads it.

NOTHING IN `src/` CONSUMES THIS
-------------------------------------------------------------------------------
Zero internal callers, AST-pinned. Consumers arrive in later slices with their
own rulings. This is Ruling 77's property at the standing layer: **the
measurement must be possible without the measurement itself becoming a
standing.**
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "PRESSURE_CLASSES",
    "STRONG_PRESSURE_CLASSES",
    "WEAK_PRESSURE_CLASSES",
    "EPISODE_OUTCOMES",
    "DERIVATION_VERSION",
    "DERIVATION_V1_EMPIRICAL_GATE",
    "DERIVATION_V1_INTERPRETIVE_STANDING",
    "DERIVATIONS",
    "NegativeSpace",
    "StandingProfile",
    "AuthorizationResult",
    "UnknownDerivation",
    "profile",
    "authorize",
]


# =====================================================================
# THE MIRRORED VOCABULARY - GOVERNED CONTENT, equality PINNED in tests
# =====================================================================

_SURVIVED = "survived"
_UNRESOLVED_AT_BOUND = "unresolved_at_bound"

EPISODE_OUTCOMES: Tuple[str, ...] = (
    "survived", "revised", "suspended", "collapsed", "unresolved_at_bound",
    "carried_contradiction",
)

# THE CUT THAT MAKES WEAK-PRESSURE FARMING UNPROFITABLE.
#
# STRONG classes are the ones whose survival can ground an EMPIRICAL claim:
# each one puts the claim in contact with something that is not another
# argument - a precommitment that could have failed, a source, a reproduction,
# a derivation.
STRONG_PRESSURE_CLASSES: Tuple[str, ...] = (
    "precommitted_prediction", "primary_source", "reproduced_counterexample",
    "formal_derivation",
)
# WEAK is argument. It is real pressure and it is recorded as such - it simply
# cannot, alone, authorize a claim about the world.
WEAK_PRESSURE_CLASSES: Tuple[str, ...] = ("model_adversarial",)

# The partition must be TOTAL and DISJOINT. A pressure class added to the
# episode vocabulary without being placed on one side or the other would
# silently land in neither, and a survival under it would authorize nothing
# while looking like coverage. Pinned in tests against the real enum.
PRESSURE_CLASSES: Tuple[str, ...] = tuple(
    sorted(STRONG_PRESSURE_CLASSES + WEAK_PRESSURE_CLASSES))


# =====================================================================
# THE DERIVATIONS - NAMED, VERSIONED, RECORDED (L7)
# =====================================================================

DERIVATION_VERSION = "v1"
DERIVATION_V1_EMPIRICAL_GATE = "empirical_gate"
DERIVATION_V1_INTERPRETIVE_STANDING = "interpretive_standing"
DERIVATIONS: Tuple[str, ...] = (DERIVATION_V1_EMPIRICAL_GATE,
                                DERIVATION_V1_INTERPRETIVE_STANDING)


class UnknownDerivation(Exception):
    """A derivation not in the closed v1 set.

    Every compression must be AUDITABLE (L7), which means it must be NAMED and
    VERSIONED. An unnamed rule applied to a standing decision is a compression
    nobody can later reconstruct - so an unknown name refuses rather than
    falling back to a default, which would silently pick the permissive one.
    """


# =====================================================================
# THE RECORDS - frozen, EPHEMERAL, no serialization surface
# =====================================================================

@dataclass(frozen=True)
class NegativeSpace:
    """WHAT WAS NOT DONE. Standing information, not an annex.

    Every field is sorted, so the same records produce the same value on any
    machine and after any restart.
    """
    # (obligation_id, reason, due_seq) - set aside, and why, and until when.
    deferred_obligations: Tuple[Tuple[str, str, str], ...] = ()
    # Classes never applied against this target at all.
    unexercised_pressure_classes: Tuple[str, ...] = ()
    # (episode_id, bound) for episodes that ran out of room. THE SHALLOW
    # SURVIVAL, kept distinguishable from a deep one forever.
    exhausted_episodes: Tuple[Tuple[str, int], ...] = ()


@dataclass(frozen=True)
class StandingProfile:
    """A computed VIEW over what happened to one target. Never stored.

    DELIBERATELY NO `as_dict`, NO `save`, NO SERIALIZATION SURFACE. A persisted
    analysis is a store (Ruling 60's `CorroborationSummary`, same reason), and
    the first thing anyone would do with a serializable profile is cache it.
    """
    target_kind: str
    target_id: str
    obligation_ids: Tuple[str, ...] = ()
    episode_ids: Tuple[str, ...] = ()
    # ((pressure_class, ((outcome, count), ...)), ...), fully sorted.
    disposition_counts: Tuple[Tuple[str, Tuple[Tuple[str, int], ...]], ...] = ()
    # (episode_id, defeater). K11: debts are never discharged, so every
    # recorded debt is an OUTSTANDING one - that IS the semantics.
    outstanding_debts: Tuple[Tuple[str, str], ...] = ()
    # (episode_id, bound) - the depths of inquiry actually faced.
    inquiry_depths: Tuple[Tuple[str, int], ...] = ()
    negative_space: NegativeSpace = NegativeSpace()

    def survivals_under(self, classes: Tuple[str, ...]) -> int:
        """How many SURVIVED dispositions sit under any of these classes."""
        total = 0
        for pressure_class, outcomes in self.disposition_counts:
            if pressure_class not in classes:
                continue
            for outcome, count in outcomes:
                if outcome == _SURVIVED:
                    total += count
        return total


@dataclass(frozen=True)
class AuthorizationResult:
    """The answer, WITH the rule that produced it.

    `derivation` and `derivation_version` are not decoration: L7 requires every
    compression to be auditable, and an authorization that does not say which
    rule at which version produced it cannot be re-derived later.
    """
    authorized: bool
    decision_kind: str
    derivation: str
    derivation_version: str
    basis: Tuple[str, ...] = ()


# =====================================================================
# THE FOLD
# =====================================================================

def _records(reader: Any) -> Tuple[Dict[str, Any], ...]:
    """Records ALREADY READ, through the owner's own reader.

    This module never opens a file. It accepts either an owner exposing
    `read_all()` or a plain sequence of records, so a caller may hand it a
    slice it read itself - O5's shape, and O5's reason: a module that opens
    files can be made to write one.
    """
    if reader is None:
        return ()
    if hasattr(reader, "read_all"):
        reader = reader.read_all()
    return tuple(r for r in reader if isinstance(r, dict))


def profile(target_kind: Any, target_id: Any, episode_reader: Any = None,
            obligation_reader: Any = None) -> StandingProfile:
    """Fold the event streams into this target's standing. DETERMINISTIC.

    The join is the one the records already carry: obligations name a TARGET,
    episodes name the OBLIGATIONS they were opened against. Nothing is inferred
    and no similarity is computed - an episode belongs to this profile because a
    recorded id says so, or it does not belong.
    """
    target_kind = str(getattr(target_kind, "value", target_kind))
    target_id = str(target_id)

    obligations = _records(obligation_reader)
    episodes = _records(episode_reader)

    # (1) Which obligations bear on this target - from the OPEN records, which
    # are the ones carrying the content.
    mine: Dict[str, Dict[str, Any]] = {}
    for record in obligations:
        if (record.get("record_type") == "open"
                and record.get("target_kind") == target_kind
                and record.get("target_id") == target_id):
            obligation_id = record.get("obligation_id")
            if isinstance(obligation_id, str):
                mine[obligation_id] = record

    # Deferrals are NEGATIVE SPACE: a standing claim set aside, with the reason
    # and the ordinal it was set aside until. LAST deferral per obligation wins,
    # by append order, which is the fold's own rule elsewhere too.
    deferred: Dict[str, Tuple[str, str]] = {}
    for record in obligations:
        obligation_id = record.get("obligation_id")
        if obligation_id in mine and record.get("record_type") == "deferred":
            deferred[obligation_id] = (str(record.get("reason", "")),
                                       str(record.get("due_seq", "")))

    # (2) Which episodes were opened against those obligations.
    opened: Dict[str, Dict[str, Any]] = {}
    for record in episodes:
        if record.get("record_type") != "episode_opened":
            continue
        refs = record.get("obligation_ids") or ()
        if any(ref in mine for ref in refs if isinstance(ref, str)):
            episode_id = record.get("episode_id")
            if isinstance(episode_id, str):
                opened[episode_id] = record

    # (3) Per-episode pressure classes, dispositions and debts.
    classes_by_episode: Dict[str, set] = {eid: set() for eid in opened}
    disposition_by_episode: Dict[str, str] = {}
    debts: List[Tuple[str, str]] = []
    for record in episodes:
        episode_id = record.get("episode_id")
        if episode_id not in opened:
            continue
        kind = record.get("record_type")
        if kind == "pressure_applied":
            pressure_class = record.get("pressure_class")
            if isinstance(pressure_class, str):
                classes_by_episode[episode_id].add(pressure_class)
        elif kind == "pressure_debt":
            defeater = record.get("defeater")
            if isinstance(defeater, str):
                debts.append((episode_id, defeater))
        elif kind == "disposition":
            outcome = record.get("outcome")
            if isinstance(outcome, str):
                disposition_by_episode[episode_id] = outcome

    # (4) Per-class disposition counts. An episode that exercised two classes
    # and ended SURVIVED contributes one SURVIVED to EACH - the disposition is
    # the episode's, and each class it applied stands behind it.
    counts: Dict[str, Dict[str, int]] = {}
    for episode_id, outcome in disposition_by_episode.items():
        for pressure_class in classes_by_episode.get(episode_id, ()):
            counts.setdefault(pressure_class, {})
            counts[pressure_class][outcome] = \
                counts[pressure_class].get(outcome, 0) + 1

    exercised = {c for classes in classes_by_episode.values() for c in classes}
    exhausted = tuple(sorted(
        (eid, int(opened[eid].get("bound", 0)))
        for eid, outcome in disposition_by_episode.items()
        if outcome == _UNRESOLVED_AT_BOUND))

    return StandingProfile(
        target_kind=target_kind,
        target_id=target_id,
        obligation_ids=tuple(sorted(mine)),
        episode_ids=tuple(sorted(opened)),
        disposition_counts=tuple(
            (pressure_class, tuple(sorted(outcomes.items())))
            for pressure_class, outcomes in sorted(counts.items())),
        outstanding_debts=tuple(sorted(debts)),
        inquiry_depths=tuple(sorted(
            (eid, int(record.get("bound", 0))) for eid, record in opened.items())),
        negative_space=NegativeSpace(
            deferred_obligations=tuple(sorted(
                (oid, reason, due) for oid, (reason, due) in deferred.items())),
            unexercised_pressure_classes=tuple(
                sorted(set(PRESSURE_CLASSES) - exercised)),
            exhausted_episodes=exhausted,
        ),
    )


# =====================================================================
# THE AUTHORIZATION
# =====================================================================

def authorize(standing: StandingProfile, decision_kind: Any,
              derivation: Any) -> AuthorizationResult:
    """Apply ONE named, versioned derivation to a profile. RECORDS ITS BASIS.

    This GRANTS nothing on its own - it returns an answer. Nothing in `src/`
    reads it, and a consumer arrives with its own ruling.
    """
    derivation = str(derivation)
    if derivation not in DERIVATIONS:
        raise UnknownDerivation(
            f"'{derivation}' is not a v1 derivation {list(DERIVATIONS)}. Every "
            f"compression must be NAMED and VERSIONED to be auditable (L7); an "
            f"unknown one refuses rather than defaulting, because the default "
            f"anyone reaches for is the permissive one.")

    decision_kind = str(decision_kind)
    strong = standing.survivals_under(STRONG_PRESSURE_CLASSES)
    weak = standing.survivals_under(WEAK_PRESSURE_CLASSES)
    debts = len(standing.outstanding_debts)
    basis: List[str] = [
        f"strong_class_survivals={strong}",
        f"weak_class_survivals={weak}",
        f"outstanding_pressure_debts={debts}",
    ]

    if derivation == DERIVATION_V1_EMPIRICAL_GATE:
        # THE STRUCTURAL REFUSAL. `strong` is a COUNT OF KINDS SURVIVED, not a
        # score: the test is that at least one exists, and no quantity of `weak`
        # can substitute for it. A profile with a thousand MODEL_ADVERSARIAL
        # survivals and no strong one fails here exactly as one with none does.
        if strong < 1:
            basis.append("REFUSED: no survival under a strong pressure class - "
                         "argument alone cannot authorize an empirical claim")
        if debts:
            basis.append("REFUSED: outstanding pressure debts (K11) - a "
                         "defeater noticed and never exercised is testing the "
                         "claim did not receive")
        authorized = strong >= 1 and debts == 0
    else:
        # INTERPRETIVE STANDING. Argumentative survivals count here and here
        # only - that is what "interpretive standing ONLY" means. Debts are
        # REPORTED in the basis and do not gate: an unexercised defeater bears
        # on what the world is like, which is not what this derivation grants.
        authorized = (strong + weak) >= 1
        if not authorized:
            basis.append("REFUSED: no survival under any pressure class")

    return AuthorizationResult(
        authorized=authorized,
        decision_kind=decision_kind,
        derivation=derivation,
        derivation_version=DERIVATION_VERSION,
        basis=tuple(basis),
    )
