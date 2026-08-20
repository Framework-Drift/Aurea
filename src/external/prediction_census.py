"""prediction_census.py - M9-a: THE RULED CENSUS OF WHAT A COMMITMENT MAY NAME.

Hundred-seventeenth entry (PATH v143), M9_GROUNDING.md section M9-a, on the
heading's line 122:

    "Prediction is the premium evidence channel: resolution criteria fixed
     before outcomes exist, in operational terms, so disposition-time
     interpretation approaches clerical."

VOCABULARY AND DATA, NOT MACHINERY (`continuity.py`'s precedent). This module
imports NOTHING from `src/` and holds no store, no path, no clock: it is the
committed census that M9-b's evaluator and M9-c's candidate derivation consume
as a RULED SURFACE instead of re-deriving - and that the prediction door
validates against, so a reference form nothing can resolve is refused at
commitment rather than stored as hope.

RECOVERED, NOT COINED - the census's own method (the M8-a discipline)
-------------------------------------------------------------------------------
The kernel already answers "what record forms can be resolved" in TWO ruled
places, and this census is their union rather than a new invention:

  * `ObligationLedger._resolve_target` (filtration) resolves the closed
    `TargetKind` six - DOCTRINE, SCAR, SUSPENSION, CLAIM, WORLD_PROPOSITION,
    PREDICTION - each against its owner's own read surface;
  * `PropositionLedger._resolver_for` (worldmodel) resolves the closed
    `KernelRefKind` six - CLAIM, SCAR, DOCTRINE, EPISODE, OBLIGATION,
    PREDICTION.

The union adds GOAL, whose owner surface (`GoalLedger.commitment_for`) exists
and whose referenceability is this entry's own subject: the licensing linkage
is what makes an M7-c license derivable (M9_GROUNDING MOVE ONE).

STATE VOCABULARIES ARE DATA HERE, PINNED EQUAL TO THE OWNERS' ENUMS IN TESTS.
A second live import of each owner would hand the prediction ledger transitive
reach into modules its own prior import pin exists to bar (scar and doctrine
surfaces); a second SPELLING would be Ruling 35's drift hazard. The resolution
is the house's third option: the strings live here as declared data, and a
drift pin in `tests/test_m9a_prediction_exposure.py` fails the moment any
owner's enum moves - the guard lives in the pins, not in an import.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

__all__ = [
    "CENSUS_CITATION", "ReferenceForm", "REFERENCEABLE_FORMS",
    "CriterionSurface", "CRITERION_SURFACES",
    "EXCLUDED_FORMS", "EXCLUDED_CRITERION_SURFACES",
    "reference_form", "criterion_surface", "id_matches_form",
]


CENSUS_CITATION = (
    "hundred-seventeenth entry (PATH v143); M9_GROUNDING.md section M9-a; "
    "heading line 122"
)


@dataclass(frozen=True)
class ReferenceForm:
    """One record form the kernel can resolve, with the owner that resolves it.

    `id_patterns` are anchored regexes over the owner's own mint discipline;
    an EMPTY tuple declares the form FORMLESS - the owner mints no anchored id
    shape (doctrine and scar ids are caller-given names), so the door can
    validate only non-emptiness and the owner's resolver settles existence at
    ITS door, exactly as `ObligationLedger.admit` already does.
    """

    form: str
    id_patterns: Tuple[str, ...]
    owner: str
    resolver_surface: str
    precedent: str


REFERENCEABLE_FORMS: Mapping[str, ReferenceForm] = MappingProxyType({
    "claim": ReferenceForm(
        form="claim",
        id_patterns=(r"^CLM-\d{4,}$",),
        owner="src.external.claim_ancestry.ClaimAncestryLedger",
        resolver_surface="ClaimAncestryLedger.get(claim_id) is not None",
        precedent="TargetKind.CLAIM and KernelRefKind.CLAIM",
    ),
    "world_proposition": ReferenceForm(
        form="world_proposition",
        id_patterns=(r"^WMP-\d{4,}$",),
        owner="src.worldmodel.proposition_ledger.PropositionLedger",
        resolver_surface="PropositionLedger.resolves(wmp_id)",
        precedent="TargetKind.WORLD_PROPOSITION",
    ),
    "prediction": ReferenceForm(
        form="prediction",
        id_patterns=(r"^PRD-\d{4,}$",),
        owner="src.external.prediction_ledger.PredictionLedger",
        resolver_surface="PredictionLedger.commitment_for(prediction_id)",
        precedent="TargetKind.PREDICTION and KernelRefKind.PREDICTION",
    ),
    "obligation": ReferenceForm(
        form="obligation",
        id_patterns=(r"^OBL-\d{4,}$",),
        owner="src.filtration.obligation_ledger.ObligationLedger",
        resolver_surface="ObligationLedger.status_of(obligation_id)",
        precedent="KernelRefKind.OBLIGATION",
    ),
    "episode": ReferenceForm(
        form="episode",
        id_patterns=(r"^EPI-\d{4,}$",),
        owner="src.filtration.episode_record",
        resolver_surface="the episode ledger's by-id read",
        precedent="KernelRefKind.EPISODE",
    ),
    "goal": ReferenceForm(
        form="goal",
        id_patterns=(r"^GLC-\d{4,}$",),
        owner="src.goals.goal_ledger.GoalLedger",
        resolver_surface="GoalLedger.commitment_for(goal_id)",
        precedent=(
            "the M9-a licensing linkage itself - the union's one addition, "
            "added by this entry because a commitment carrying claim_refs and "
            "a resolving goal reference is what makes an M7-c license "
            "derivable (M9_GROUNDING MOVE ONE)"
        ),
    ),
    "doctrine": ReferenceForm(
        form="doctrine",
        id_patterns=(),
        owner="src.doctrine.codex.Codex",
        resolver_surface=(
            "Codex.get(doctrine_id) is not None, or membership in "
            "Codex.fossils - an obligation may bear on a doctrine that has "
            "FALLEN (ObligationLedger._resolve_target's own rule)"
        ),
        precedent="TargetKind.DOCTRINE and KernelRefKind.DOCTRINE",
    ),
    "scar": ReferenceForm(
        form="scar",
        id_patterns=(),
        owner="src.filtration.scar_logic_core.ScarLogicCore",
        resolver_surface="ScarLogicCore.get_scar(scar_id) is not None",
        precedent="TargetKind.SCAR and KernelRefKind.SCAR",
    ),
    "suspension": ReferenceForm(
        form="suspension",
        id_patterns=(r"^VT-.+$", r"^BS-.+$", r"^CSA-.+$"),
        owner=(
            "src.suspension - VeiledThread, BlackSphere, CSA "
            "(three owners, three declared ID_PREFIX constants)"
        ),
        resolver_surface=(
            "membership in a suspension system's public `entries` mapping - "
            "NEVER `retrieve`, which mutates (ObligationLedger's own bar)"
        ),
        precedent="TargetKind.SUSPENSION",
    ),
})


@dataclass(frozen=True)
class CriterionSurface:
    """One kernel record surface a resolution criterion may name.

    `states` is the owner's honest CLOSED vocabulary, held here as declared
    data and drift-pinned against the owner's enum. A criterion names one of
    these surfaces, the record it reads, the state that resolves CONFIRMED and
    the state that resolves FAILED - so M9-b's evaluator reads the surface and
    compares, nothing more.
    """

    surface: str
    reference_form: str
    owner: str
    read_surface: str
    states: Tuple[str, ...]


CRITERION_SURFACES: Mapping[str, CriterionSurface] = MappingProxyType({
    "prediction_resolution_outcome": CriterionSurface(
        surface="prediction_resolution_outcome",
        reference_form="prediction",
        owner="src.external.prediction_ledger",
        read_surface=(
            "PredictionLedger.resolution_for(prediction_id).outcome; a "
            "commitment with no resolution line has not reached any state"
        ),
        states=("confirmed", "falsified", "unresolved"),
    ),
    "obligation_status": CriterionSurface(
        surface="obligation_status",
        reference_form="obligation",
        owner="src.filtration.obligation_ledger",
        read_surface=(
            "ObligationLedger.status_of(obligation_id) - derived by folding "
            "the appends, never stored (L3)"
        ),
        states=("open", "rejected", "deferred", "merged", "episode_opened"),
    ),
    "world_proposition_standing": CriterionSurface(
        surface="world_proposition_standing",
        reference_form="world_proposition",
        owner="src.worldmodel.standing",
        read_surface=(
            "derive_standing over the proposition's recorded references - "
            "derived at read, never stored (L3)"
        ),
        states=("ungrounded", "supported", "contested", "undercut"),
    ),
    "goal_status": CriterionSurface(
        surface="goal_status",
        reference_form="goal",
        owner="src.goals.goal_ledger",
        read_surface=(
            "GoalLedger.derive_status(goal_id) - derived by declared "
            "precedence over the appends, never stored (L3)"
        ),
        states=("committed", "evidence_bearing", "resolved", "superseded"),
    ),
})


# WHAT THE CENSUS EXCLUDED, AND WHY - named rather than silently omitted (the
# M8-a `UNDERIVABLE_TOUCH_FACTS` shape: a surface nobody censused must not
# read as a surface that does not exist).
EXCLUDED_FORMS: Mapping[str, str] = MappingProxyType({
    "cae_entry": (
        "CAE- ids name audit-ledger lines. No ruled resolver precedent names "
        "them as dependency targets - neither TargetKind nor KernelRefKind "
        "carries them - and an audit trail is evidence ABOUT acts, not a "
        "surface a prediction rests on. Excluded until an entry rules "
        "otherwise."
    ),
    "act_records": (
        "Executive act ids (RTE-, SEL-, UTL-, INQ-, CHL-, ADJ-, EXM-, ACT-) "
        "are the Executive's own history. L10: the Executive owns nothing a "
        "kernel commitment may rest on; no ruled resolver names them."
    ),
})

EXCLUDED_CRITERION_SURFACES: Mapping[str, str] = MappingProxyType({
    "doctrine_status": (
        "The owner vocabulary lives in src.doctrine - a surface the "
        "prediction ledger's prior import pin (test_ruling61, L2 pinned "
        "structurally) bars it from reaching, directly or transitively. "
        "Doctrine records stay REFERENCEABLE as dependencies (the resolver "
        "owner settles existence at its own door); a doctrine-status "
        "CRITERION becomes censusable when the entry that owns M9-b's "
        "evaluator imports rules it."
    ),
    "scar_decay_state": (
        "`DecayState` is scar_management's, a module in the prediction "
        "ledger's forbidden import set. Same deferral as doctrine_status, "
        "same reopening condition."
    ),
    "claim_state": (
        "The claim-ancestry ledger records formation facts, append-only, and "
        "exposes NO live state read - a recorded claim always resolves "
        "(ObligationLedger's own rule), so membership is the whole question "
        "and there is no state for a criterion to compare. Claims participate "
        "as dependency REFERENCES, not criterion surfaces."
    ),
    "suspension_state": (
        "`retrieve` mutates the entry on all three suspension systems (the "
        "obligation resolver's own bar), so membership is the only safe read "
        "- and membership alone cannot separate CONFIRMED from FAILED."
    ),
    "episode_state": (
        "No ruled non-mutating by-id state read was censused on the episode "
        "ledger. Referenceable as a dependency; not a criterion surface "
        "until one is."
    ),
})


def reference_form(form_key: str) -> Optional[ReferenceForm]:
    """The censused form, or None - the caller decides what a miss means."""
    return REFERENCEABLE_FORMS.get(form_key)


def criterion_surface(surface_key: str) -> Optional[CriterionSurface]:
    """The censused surface, or None - the caller decides what a miss means."""
    return CRITERION_SURFACES.get(surface_key)


def id_matches_form(form: ReferenceForm, record_id: str) -> bool:
    """Pure form check. A FORMLESS form validates non-emptiness only -
    existence is the resolver owner's question, at its own door."""
    if not isinstance(record_id, str) or not record_id:
        return False
    if not form.id_patterns:
        return True
    return any(re.match(pattern, record_id) for pattern in form.id_patterns)
