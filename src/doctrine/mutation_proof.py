"""
mutation_proof.py - THE ARGUMENT THAT FORCED A MUTATION, carried with it.

Docket I / Ruling 45. A doctrine mutation used to travel as four values -
`doctrine_id`, `new_form`, a SINGLE `collapse_lineage` string, and a `reason`
sentence. Everything that made the change legitimate (which triggers fired, at
what pressure, which scars were behind it, which echo authored it, which of the
five CMTE criteria actually passed and which merely were not contradicted) was
computed in `DEE._approve`, used once, and dropped on the floor.

    A mutation that cannot state its own argument is not self-authorship.
    It is self-editing with a receipt.

PLACEMENT (stated, per the docket): its own module, importing nothing but stdlib
and `models`. It is constructed by DEE, consumed by SAE, and recorded by CAE -
three modules in two packages - so it belongs to none of them. That is
`src/utils/continuity.py`'s precedent exactly: vocabulary, not machinery.

FROZEN, for `TruthPacket`'s reason: a proof is a statement about a decision that
has already been made. A consumer that could rewrite `preserved_invariants` after
the fact could make a mutation that squeaked through look like one that sailed.

HONESTY AT THE FIELD LEVEL - `CriterionResult`
------------------------------------------------
`preserved_invariants` records the five CMTE criteria AS EVALUATED, and a
criterion that passed BY ABSENCE records `ABSENT`, not `PASS`. This is the
distinction Docket H drew between `NONE_FOUND` and `NOT_COUNTABLE`, applied to a
gate instead of a tally: criterion 3 (`echo_resonance`) and criterion 5
(`distortion_detected`) are read with `context.get(...)`, so an unsupplied key
reads as "not contradicted". That is the correct SEMANTICS - DEE's absent-reads-
as-pass is deliberate - but recording it as PASS would claim an instrument ran.
No instrument ran. Two silences are not the same silence.

WHAT IS DELIBERATELY NOT HERE
-------------------------------
`content_delta` is NAME/DESCRIPTION level, and assertion-level decomposition is
EXPLICITLY DEFERRED. `models.Doctrine` has no assertion structure - a doctrine is
an id, a name, a description and some links - so "which assertions changed" has
nothing to decompose. Inventing a parse would be coining structure the store does
not have.

    REOPENING CONDITION: the PySAT experiment tier. When a doctrine carries a
    real assertion structure, `content_delta` grows a field for it and this
    comment comes out. Not before, and not by regex over a description.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class CriterionResult(str, Enum):
    """How a CMTE criterion actually resolved.

    A `str` Enum by the shape rule (the thirty-fourth entry): ONE vocabulary,
    SERIALIZED into CAE entries and SAE's state file, with no collision partner
    anywhere in the tree.
    """

    PASS = "pass"        # an instrument ran and the criterion held
    FAIL = "fail"        # an instrument ran and the criterion did not hold
    ABSENT = "absent"    # NO INSTRUMENT RAN - the key was never supplied


# The five CMTE criteria, canonically named ONCE.
#
# RULING 47 (2026-07-29) MOVED THIS HERE FROM `CMTE.FAILURE_LABELS`, and the move
# is the point rather than a tidy-up. SAE now constructs a proof of its own for a
# reversion (a counter-mutation that no CMTE gate evaluated), so it needs the
# criterion NAMES in order to report them as ABSENT. The two ways to get them
# were both wrong: importing `dee` into `sae.py` inverts the layering, making the
# executor depend on the gate that calls it; and spelling the five names a second
# time in `sae.py` creates a definition free to drift from CMTE's - the defect
# Ruling 35 named ("a second definition drifts") and `tests/proof_support.py`
# already committed once in the harness.
#
# This module is where it belongs on its own stated terms: "constructed by DEE,
# consumed by SAE, and recorded by CAE - three modules in two packages - so it
# belongs to none of them." `CMTE.FAILURE_LABELS` is now an ALIAS of this, so
# there is exactly one definition and every existing reader is byte-identical.
#
# Criterion name -> the FAILURE LABEL `DEE._reject` routes on. Those labels are
# load-bearing: `_reject` branches on `distortion_flagged` and
# `identity_discontinuity` to send a doctrine to Null Threads rather than to
# fermentation.
CMTE_FAILURE_LABELS: Dict[str, str] = {
    "collapse_threshold_reached": "collapse_threshold_not_reached",
    "scar_lineage_present": "no_scar_lineage",
    "echo_resonance_aligned": "echo_resonance_misaligned",
    "identity_continuity_maintained": "identity_discontinuity",
    "no_distortion_flags": "distortion_flagged",
}


def all_criteria_absent() -> Dict[str, "CriterionResult"]:
    """The five criteria reported as UN-EVALUATED. The honest record for any
    mutation path that no CMTE gate stood in front of.

    THIS HELPER CANNOT FABRICATE ANYTHING, and that is why it is allowed to
    exist where a `preserved_invariants` default is not. Its only possible output
    is ABSENT for every criterion - the claim "no instrument ran", which is the
    weakest statement the vocabulary can make. A convenience that produced PASS
    would put "all five criteria satisfied" into the audit ledger of a mutation
    that consulted none of them; this one is incapable of it.
    """
    return {name: CriterionResult.ABSENT for name in CMTE_FAILURE_LABELS}


@dataclass(frozen=True)
class ContentDelta:
    """What actually changed, at the level the store can express.

    See the module docstring: assertion-level decomposition is deferred to the
    PySAT experiment tier, because `Doctrine` has no assertion structure to
    decompose and a regex over prose would be invented structure.
    """

    ancestor_id: str
    name_before: str = ""
    name_after: str = ""
    description_before: str = ""
    description_after: str = ""


@dataclass(frozen=True)
class DoctrineMutationProof:
    """The argument for ONE mutation, carried on the call that performs it."""

    # WHAT FORCED THIS: the triggers that fired, the pressure they carried, and
    # where the strain was observed. Not a summary sentence - the values.
    contradiction_core: Dict[str, Any] = field(default_factory=dict)

    # THE FULL ORDERED DEDUP of both criterion-2 sources: the doctrine's own
    # `scar_links` first, then the proposal's (which Nova populated from the
    # backing echo). This SUPERSEDES the `[0]` truncation `_approve` hands to
    # `collapse_lineage` - that single string survives for AVT.017, but the
    # lineage of record is here, whole.
    scar_lineage: Tuple[str, ...] = ()

    # The echo recorded as AUTHORING the proposal, and the provenance key under
    # which Nova recorded it. None where no proposal authored this mutation -
    # which is the ordinary case and is not a gap.
    echo_provenance: Optional[Dict[str, str]] = None

    content_delta: Optional[ContentDelta] = None

    # The five criteria AS EVALUATED. ABSENT is not PASS - see the docstring.
    preserved_invariants: Dict[str, CriterionResult] = field(default_factory=dict)

    # What this mutation did NOT resolve. MAY BE EMPTY, and the field exists
    # anyway: "nothing was left over" is a claim worth being able to make
    # explicitly, and a field that only appears when non-empty cannot make it.
    unresolved_residue: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        """Plain JSON for the CAE entry and SAE's state file."""
        return {
            "contradiction_core": dict(self.contradiction_core),
            "scar_lineage": list(self.scar_lineage),
            "echo_provenance": dict(self.echo_provenance) if self.echo_provenance else None,
            "content_delta": (
                {
                    "ancestor_id": self.content_delta.ancestor_id,
                    "name_before": self.content_delta.name_before,
                    "name_after": self.content_delta.name_after,
                    "description_before": self.content_delta.description_before,
                    "description_after": self.content_delta.description_after,
                }
                if self.content_delta else None
            ),
            "preserved_invariants": {k: v.value for k, v
                                     in self.preserved_invariants.items()},
            "unresolved_residue": list(self.unresolved_residue),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["DoctrineMutationProof"]:
        """Rebuild from a state file. `None` in, `None` out.

        A record written before this docket carries NO proof, and that absence is
        A FACT ABOUT ITS ERA rather than an error: those mutations really were
        performed without one. It loads as `None` and says so.
        """
        if not data:
            return None
        delta = data.get("content_delta")
        return cls(
            contradiction_core=dict(data.get("contradiction_core") or {}),
            scar_lineage=tuple(data.get("scar_lineage") or ()),
            echo_provenance=(dict(data["echo_provenance"])
                             if data.get("echo_provenance") else None),
            content_delta=(ContentDelta(**delta) if delta else None),
            preserved_invariants={k: CriterionResult(v) for k, v
                                  in (data.get("preserved_invariants") or {}).items()},
            unresolved_residue=tuple(data.get("unresolved_residue") or ()),
        )


class InvalidMutationProof(Exception):
    """A proof that cannot support the mutation it accompanies.

    A STRUCTURAL VIOLATION, not a validation nicety (Ruling 25's discipline): a
    mutation arriving with an empty argument is a mutation with no argument, and
    the whole point of the parameter is that such a call is refused rather than
    completed with a blank receipt.
    """


def validate_proof(proof: Any) -> None:
    """Refuse a proof that carries no argument. RAISES `InvalidMutationProof`.

    MINIMAL AND STRUCTURAL, deliberately. This checks that a proof IS one and
    that it is not vacuous; it does not grade the argument's quality, because
    "is this a good enough reason" is CMTE's five criteria and they already ran.
    Adding a sixth gate here would be exactly the thing Stage 2b's seam comment
    warns against.
    """
    if not isinstance(proof, DoctrineMutationProof):
        raise InvalidMutationProof(
            f"a doctrine mutation requires a DoctrineMutationProof, got "
            f"{type(proof).__name__}. There is no default proof: an implicit one "
            f"would be a fabricated argument, and a mutation with no argument is "
            f"self-editing."
        )
    if not proof.contradiction_core:
        raise InvalidMutationProof(
            "the proof records no contradiction_core - nothing is stated to have "
            "forced this mutation. An empty argument is not an argument."
        )
    if not proof.preserved_invariants:
        raise InvalidMutationProof(
            "the proof records no preserved_invariants - the five CMTE criteria "
            "are not reported as evaluated. A mutation must carry what it "
            "preserved, including which criteria were ABSENT rather than passed."
        )
