"""
record_value.py - RULING 66 (2026-08-02): CANONICAL RECORD VALUES, REFUSED AT
THE DOOR.

THE LAW THIS FILE ENFORCES
-------------------------------------------------------------------------------
A record either holds what was presented or refuses it. **There is no third
thing where it silently holds something else.**

A repr-stringified `bytearray` is a FABRICATED RECORD VALUE: the record claims a
string was presented when a bytearray was. That is L3's fabrication class
arriving at the WRITE side, and the answer is Ruling 53's law applied one layer
out - **the ledger refuses what it cannot canonically hold. REFUSAL, NEVER
COERCION.**

WHAT WAS WITNESSED, AND WHY A VALIDATOR RATHER THAN A PATCH
-------------------------------------------------------------------------------
Measured at `0b2072c` (sixty-second entry, finding 4), end to end: ONE bytearray
leaf inside a `DoctrineMutationProof` PASSED `validate_proof` (which checked
class, contradiction core and invariants - never serializability), FOSSILIZED
the ancestor, INSTALLED the successor, SPENT a ceiling slot, wrote a PERMANENT
CAE entry with the leaf silently stringified - and THEN raised `TypeError` at
SAE's own persistence. History was 1 in memory and 0 on disk, so Ruling 47's
reversion had nothing to read while the Codex had already moved; and because the
proof stayed in `history`, `sae.save()` and `AureaCore.save_state()` raised for
the REST OF THE PROCESS. No store was checkpointed again.

The defect was never one writer's. It was that FOUR writers each decided
independently what to do with a value they could not hold, and three of them
chose to invent one. So the answer is ONE shared decision, made once.

THE ADMISSIBLE SET IS CLOSED AND DECLARED AS DATA, NOT PROSE
-------------------------------------------------------------------------------
Leaves: `str`, `bool`, `None`, `int`, FINITE `float`.
Containers: `list`, and `dict` with `str` keys - recursively.

**"OVER SERIALIZED PAYLOADS" IS LOAD-BEARING PRECISION, NOT LOOSENESS, AND THE
ABSENCE OF `tuple` FROM THAT SET IS THE PROOF OF IT.** `DoctrineMutationProof`
holds `scar_lineage` as a TUPLE in memory, and Ruling 52's deep freeze converts
every interior list INTO a tuple - so a validator run over the LIVE object would
refuse every proof AUREA can construct. It is run over `as_dict()` output, where
`_thaw` has already returned lists. Verified on a real proof before this set was
written down rather than assumed from the ruling's wording.

WHY NaN AND Infinity ARE EXCLUDED, AND WHY THAT IS A SEPARATE DEFECT
-------------------------------------------------------------------------------
`json.dumps` writes them as bare `NaN` / `Infinity`, which are INVALID under
strict JSON - any conforming parser in any other language rejects the line. A
forensic log outlives the code that wrote it, so a record only Python can read is
a record with a hidden expiry date. `default=str` never sees these values (the
float serializer handles them first), which is why deleting `default=` alone
would not have closed it and `allow_nan=False` is required at every writer.

PURE. NEVER MUTATES ITS INPUT. NO COERCION PATH EXISTS ANYWHERE IN THIS MODULE -
there is no `sanitize`, no `coerce`, no `to_canonical`, and adding one would
reintroduce the fabrication this file exists to refuse.
"""

from __future__ import annotations

import math
from typing import Any, Tuple

__all__ = [
    "CANONICAL_LEAF_TYPES",
    "CANONICAL_CONTAINER_TYPES",
    "NonCanonicalRecordValue",
    "validate_record_value",
]


# THE CLOSED SET, AS DATA. Declared here so a pin can read the DECLARATION
# rather than re-spelling it - a second hand-written copy in the tests is the
# drift hazard Ruling 47 consolidated `CMTE_FAILURE_LABELS` to avoid.
#
# `bool` is listed explicitly even though it is a subclass of `int`: the set is a
# DECLARATION of what is admissible, and a reader must not have to know Python's
# numeric tower to learn that `True` is allowed.
CANONICAL_LEAF_TYPES: Tuple[type, ...] = (str, bool, int, float, type(None))
CANONICAL_CONTAINER_TYPES: Tuple[type, ...] = (list, dict)


class NonCanonicalRecordValue(TypeError):
    """A value that no record may hold. **THE ONE COINAGE OF RULING 66.**

    Subclasses `TypeError` deliberately: that is exactly what `json.dumps`
    already raises for the same value class, so a caller that was correctly
    handling the boundary failure keeps handling it, and this type only makes
    the report better. It is a NARROWING of an existing failure, not a new one.

    Carries the OFFENDING KEY-PATH, because **a refusal that cannot say where it
    refused is half a refusal** - the witnessed defect hid one bytearray inside a
    nested proof, and "somewhere in this payload" would have sent the next
    investigation back to the same manual bisection this file exists to end.
    """

    def __init__(self, path: str, value: Any) -> None:
        self.path = path
        self.offending_type = type(value).__name__
        detail = ""
        if isinstance(value, float):
            # The one case where the TYPE is admissible and the VALUE is not, so
            # naming only the type would read as a contradiction.
            detail = f" (value {value!r} is not finite)"
        super().__init__(
            f"non-canonical record value at {path}: {self.offending_type}"
            f"{detail}. A record either holds what was presented or refuses it; "
            f"it may not hold something else instead. Admissible leaves are "
            f"str, bool, None, int and finite float; containers are list and "
            f"str-keyed dict."
        )


def _describe(path: str, key: Any) -> str:
    """Extend a key-path. Non-`str` dict keys are rendered with `!r` so the
    refusal names the actual key rather than a coerced rendering of it."""
    if isinstance(key, int):
        return f"{path}[{key}]"
    if isinstance(key, str):
        return f"{path}.{key}" if path else key
    return f"{path}[{key!r}]"


def validate_record_value(payload: Any, *, path: str = "root") -> None:
    """Refuse any value a record cannot canonically hold. RAISES, returns None.

    PURE: reads the payload and nothing else; writes nothing, mutates nothing,
    and returns nothing. It is a GATE, not a transformer - there is deliberately
    no variant that returns a cleaned copy, because the moment one exists some
    caller under deadline will use it and the fabrication is back.

    Depth-first, so the FIRST offender reported is the first encountered in
    document order - deterministic, which matters when a refusal message becomes
    the input to someone's next decision.
    """
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(key, str):
                # A non-str key is refused AT THE KEY, not silently stringified.
                # `json.dumps` would have written `{"1": ...}` for `{1: ...}`,
                # so the record would claim a string key was presented - the
                # same fabrication as the stringified leaf, one level up, and
                # measured as a real divergence at `0b2072c`.
                raise NonCanonicalRecordValue(_describe(path, key), key)
            validate_record_value(value, path=_describe(path, key))
        return

    if isinstance(payload, list):
        for index, value in enumerate(payload):
            validate_record_value(value, path=_describe(path, index))
        return

    # LEAVES. `bool` before `int` is not required here (both are admissible),
    # but the finite check must not be reached by a bool, which `isinstance`
    # ordering already guarantees since `bool` is not a `float`.
    if isinstance(payload, bool) or payload is None:
        return
    if isinstance(payload, int):
        return
    if isinstance(payload, float):
        if not math.isfinite(payload):
            raise NonCanonicalRecordValue(path, payload)
        return
    if isinstance(payload, str):
        return

    raise NonCanonicalRecordValue(path, payload)
