"""
entrenchment.py - HOW DEEPLY A DOCTRINE IS DUG IN, DERIVED AND NEVER STORED.

Docket I / Ruling 45. Entrenchment is a reading of facts the Codex already holds
- `is_seed`, `scar_links`, `mutation_lineage` - and it is computed on demand,
every time, from those three.

WHY IT IS A FUNCTION AND NOT A FIELD, WHICH IS THE WHOLE POINT
-----------------------------------------------------------------
A stored `entrenchment` attribute would be A SECOND WRITER of something the
Codex already determines. The moment it exists, two things can disagree about how
entrenched a doctrine is: the field, and the facts. And the field would be the
one people read - it is right there on the object - while the facts would be the
one that is true. That is Ruling 1's single-writer argument arriving through a
side door, and Ruling 22's fail-silent shape as the consequence.

    An AST pin asserts that NO attribute named `entrenchment*` is ever ASSIGNED
    anywhere in `src/`. Not discouraged - unwritable (CLAUDE.md section 3).

PRECEDENCE, and it is ORDERED rather than scored
--------------------------------------------------
    SEED            `is_seed` - she was born with it. Nothing outranks this:
                    a seed doctrine that later acquires scars is STILL what she
                    was founded on.
    SCAR_SURVIVED   it carries scar links - something broke and this is what
                    stood afterwards.
    DERIVED         it has a mutation lineage - it descends from something that
                    fell, but nothing has scarred IT.
    PROVISIONAL     none of the above. It is asserted and untested.

NO MAGNITUDE ANYWHERE (section 9 standing bar #5, eighth application). There is
no entrenchment SCORE, no weight, no count-of-scars threshold - the corpus gives
no such magnitude, and a "depth" number would be a coined cutoff at exactly the
place someone would later want to gate mutation on. The classes are DISCRETE
STRUCTURAL FACTS, checkable without a number, which is the same reasoning Ruling
28 used to refuse the betweenness cutoff.

IT REPORTS. IT DOES NOT GATE. Nothing in this pass consults entrenchment to
decide anything, and wiring it into CMTE as a sixth criterion is a ruling, not an
edit.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class EntrenchmentBasis(str, Enum):
    """What a doctrine's standing RESTS ON. Ordered by precedence, closed.

    A `str` Enum by the shape rule: one vocabulary, serialized into reports and
    audit entries, no collision partner.
    """

    SEED = "seed"
    SCAR_SURVIVED = "scar_survived"
    DERIVED = "derived"
    PROVISIONAL = "provisional"


def entrenchment_basis(doctrine: Any) -> EntrenchmentBasis:
    """Classify a doctrine by precedence over the three facts the Codex holds.

    Reads with `getattr` defaults so a partial stand-in (a test double, a
    proposal that is not yet a committed doctrine) classifies rather than
    raising - the absent fact simply does not qualify it, which is the honest
    reading of an absent fact.
    """
    if getattr(doctrine, "is_seed", False):
        return EntrenchmentBasis.SEED
    if getattr(doctrine, "scar_links", None):
        return EntrenchmentBasis.SCAR_SURVIVED
    if getattr(doctrine, "mutation_lineage", None):
        return EntrenchmentBasis.DERIVED
    return EntrenchmentBasis.PROVISIONAL
