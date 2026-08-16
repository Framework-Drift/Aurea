"""The Gate-1 adequacy referents, shared by the Executive's act logs.

BUILD_CONTRACT's disposition-record adequacy names three fields: pressure class
applied, defeaters named-not-exercised, and rejection reason. **AN EXECUTIVE ACT
IS NOT A DISPOSITION** - it allocates attention or asks a question, and
adjudicates nothing - so some of those fields have no referent, and this
vocabulary is how a record says so rather than omitting them.

**HOISTED HERE AT M7-c, AND THE REASON IS A PIN RATHER THAN TIDINESS.** It was
declared in `selection_log` at M7-b, when there was one act log. M7-c adds a
second, and the inquiry log needs the same three answers. The two available
moves were both worse:

  * REDECLARE it in `inquiry_log` - a second definition of one rule, free to
    drift, which is the defect this house has named at `_derive_seq`
    (Ruling 69's hoist), at `deep_freeze` (Ruling 63's owed hoist) and at the
    isolation table (Ruling 67's "one implementation, two callers").
  * IMPORT IT FROM `selection_log` - which turns the ATTENTION log into a
    dependency of the INQUIRY log, and reddens M7-b's no-consumer pin. That pin
    is not incidental: it asserts nothing in `src/` reads the selection log,
    and a module importing it for a vocabulary is a consumer by the scanner's
    only honest definition.

So the vocabulary moves to a module that owns no store, imports nothing, and can
be read by both. `selection_log` re-exports it, so every M7-b import site and
pin is untouched - which is what keeps the v-b test file BYTE-UNMODIFIED.
"""

from __future__ import annotations

from enum import Enum

__all__ = ["GateOneReferent"]


class GateOneReferent(str, Enum):
    """How a Gate-1 adequacy field is answered by a NON-DISPOSITION record.

    Two members, and neither is a value: they say WHERE the answer is, or that
    the question does not apply. A record that silently omitted a Gate-1 field
    would be indistinguishable from one whose author forgot it, and one that
    filled it with an empty list would claim an instrument ran.
    """

    # The field names something this act does not do. Not zero, not empty.
    NOT_APPLICABLE = "not_applicable"
    # The requirement is met, and the per-candidate census is where it is met.
    IN_CANDIDATE_CENSUS = "in_candidate_census"
