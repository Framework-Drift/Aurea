"""
proof_support.py - the ONE shared helper for constructing a mutation proof in
tests. Ruling 45, Part 2.6.

NOT a fixture, and deliberately not. A fixture would arrive implicitly and every
`mutate_doctrine` call would carry a proof without its author having said
anything about it - which is precisely the "implicit default proof" the ruling
made unwritable in `src/`. Recreating it in the harness would hand the discipline
back with one hand after taking it away with the other. So this is a FUNCTION,
imported and CALLED at each site, visible in the diff.

WHY THE DEFAULT `preserved_invariants` IS ALL-ABSENT, AND WHY THAT IS THE HONEST
VALUE RATHER THAN A CONVENIENT ONE
---------------------------------------------------------------------------------
Every caller of this helper drives `SAE.mutate_doctrine` DIRECTLY, which means
CMTE never ran. Not one of the five criteria was evaluated. `ABSENT` is the
truthful record of that, and it is also what makes these proofs valid without
claiming anything false: `validate_proof` requires the invariants to be
REPORTED, not to have PASSED.

A helper that defaulted them to PASS would put "all five criteria satisfied" into
the audit ledger of a test that never consulted a single one - a fabricated
argument in the exact place this docket exists to prevent one.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from src.doctrine.mutation_proof import (
    ContentDelta, CriterionResult, DoctrineMutationProof, all_criteria_absent,
)

# The five CMTE criteria, none of which a direct SAE call evaluates.
#
# RULING 47 (2026-07-29): this was a hand-spelled dict of the same five names -
# the SECOND definition of CMTE's vocabulary, in the harness, exactly the drift
# hazard `CMTE.FAILURE_LABELS` was consolidated to avoid. It now derives from the
# one canonical definition, so a criterion renamed in `mutation_proof.py` cannot
# leave these proofs asserting the old names. The VALUE is unchanged: all five
# ABSENT, because a test driving SAE directly evaluated none of them.
_ALL_ABSENT: Dict[str, CriterionResult] = all_criteria_absent()


def minimal_proof(forced_by: str,
                  scar_lineage: Sequence[str] = (),
                  ancestor_id: str = "",
                  criteria: Optional[Dict[str, CriterionResult]] = None,
                  ) -> DoctrineMutationProof:
    """An honest minimal proof for a test that drives SAE directly.

    `forced_by` is REQUIRED and has no default, mirroring the production
    signature: the caller must say what it is claiming forced this mutation, even
    in a test. "A test drove it" is a real answer; no answer is not.
    """
    return DoctrineMutationProof(
        contradiction_core={
            "triggers": ["test_harness"],
            "pressure": 1.0,
            "strain_source": forced_by,
            "note": ("constructed by tests/proof_support.minimal_proof - this "
                     "mutation was driven directly against SAE, so no CMTE "
                     "evaluation stands behind it"),
        },
        scar_lineage=tuple(scar_lineage),
        echo_provenance=None,
        content_delta=ContentDelta(ancestor_id=ancestor_id) if ancestor_id else None,
        preserved_invariants=dict(criteria or _ALL_ABSENT),
        unresolved_residue=(),
    )
