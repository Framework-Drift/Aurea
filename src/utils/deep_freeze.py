"""
deep_freeze.py - RULING 52's freeze/thaw pair, hoisted to ONE definition.

    A frozen shell around a mutable interior is the appearance of immutability.

WHY THIS FILE EXISTS, AND WHY IT EXISTS NOW
---------------------------------------------
Ruling 52 established the deep freeze for `DoctrineMutationProof` - the
argument of record behind a doctrine mutation. Ruling 58 needed the identical
behaviour for `ClaimAncestryRecord` and re-implemented it, recording the
judgment call in that file rather than hiding it, and STATING THE RULE FOR THE
NEXT ONE:

    "REPORTED AS A JUDGMENT CALL rather than hidden: this is a SECOND
     definition of one behaviour, which is the drift hazard Ruling 35 named. It
     is accepted for one user; if a THIRD appears, the honest move is to hoist
     one copy into `src/utils/` (the `continuity.py` precedent) rather than
     write a third."

RULING 61 WAS THAT THIRD USER AND DECLINED TO TRIGGER THE RULE - it imported
`claim_ancestry`'s private copy instead, reporting the hoist as OWED rather
than reaching across two out-of-scope files to take it. Ruling 63 is the FOURTH
user, the manifest marked the hoist DUE, and this pass's bar sanctioned the
files. So it is taken here.

THE HOIST WAS VERIFIED MECHANICAL BEFORE IT WAS TAKEN, not assumed: the two
existing definitions were compared by AST with docstrings stripped and are
BYTE-IDENTICAL, and no test imported either one. So this is one behaviour with
one definition now, and no behaviour was reconciled, chosen between, or
changed. Had they differed, the honest move would have been to leave them alone
and report it - reconciling two ruled-on records' freeze semantics is its own
ruling, not a refactor.

IMPORTS NO STORE. Vocabulary and mechanism only - the `continuity.py` /
`atomic_write.py` precedent. A helper that reaches a store is a helper that can
be made to write one.

THE LOCAL NAMES ARE PRESERVED AT EVERY CALL SITE (`deep_freeze as _deep_freeze`),
which is deliberate: it keeps every existing call site and every existing AST
pin that names `_deep_freeze` working unchanged, so the hoist moves a
definition without moving a single line of behaviour.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any


def deep_freeze(value: Any) -> Any:
    """Rebuild a container graph as read-only, all the way down. RULING 52.

    dict -> `MappingProxyType`, list -> tuple, set -> frozenset, recursively.
    Anything else is returned as-is: this converts CONTAINERS, and inventing a
    freeze for arbitrary leaf objects would be inventing structure the record
    does not have.

    EVERY CONTAINER IT RETURNS IS NEW. That is not incidental - it is the half
    that makes the freeze airtight, and the reason the ruling says "a fresh deep
    copy" rather than "a proxy". `MappingProxyType(caller_dict)` is a VIEW: it
    would refuse `record.field["x"] = 1` while leaving `caller_dict["x"] = 1`
    writing straight through to the recorded argument. A freeze that stops the
    honest caller and not the one holding the reference is the appearance of
    immutability, which is what stops anyone looking.

    THE CALLER MUST STILL `copy.deepcopy` FIRST. This function copies the
    container SPINE, so a MUTABLE LEAF - a `bytearray`, say - is returned
    untouched and stays shared with whoever passed it in. That gap has now been
    found by a surviving mutant THREE times (Batch 51 on the proof, Ruling 58 on
    the ancestry record, Ruling 61 on the commitment), which is why every call
    site pairs this with a deepcopy and every one of them pins the leaf case.
    """
    if isinstance(value, MappingProxyType):
        # Already frozen by a previous construction (a record rebuilt from
        # another record's `as_dict`, or a nested value passed twice). Rebuilding
        # is still correct but pointless; returning it avoids a proxy of a proxy.
        return value
    if isinstance(value, dict):
        return MappingProxyType({k: deep_freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(deep_freeze(v) for v in value)
    return value


def thaw(value: Any) -> Any:
    """The inverse of `deep_freeze`, for `as_dict`. RULING 52.

    FOUND BY A PIN, NOT BY DESIGN, and worth recording as the reason this
    function exists. `as_dict` did `dict(self.contradiction_core)` - a SHALLOW
    copy, which was correct while the interiors were plain dicts and became a
    `TypeError: Object of type mappingproxy is not JSON serializable` the moment
    they were frozen one level down. The ruling requires the serialized shape to
    be UNCHANGED, so the freeze has to be invisible at the boundary where the
    record leaves memory for a ledger or a state file.

    Converts back exactly what `deep_freeze` converted and no more:
    `MappingProxyType` -> dict, tuple -> list. A `frozenset` is deliberately left
    alone - a set was never JSON-serializable here either, so thawing one would
    change behaviour for an input that already failed, and choosing an order for
    it would be inventing one.

    USED AT THE SERIALIZATION BOUNDARY ONLY, and nowhere else.
    """
    if isinstance(value, (MappingProxyType, dict)):
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw(v) for v in value]
    return value
