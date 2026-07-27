"""
continuity.py - THE RESTORATION VOCABULARY (Ruling 42, res.1).

A restart must stop being able to make AUREA forget anything, and EVERY LOAD
MUST SAY OUT LOUD WHAT KIND OF RESTORATION IT PERFORMED. This module is the
second half of that sentence: the shared words in which a load reports itself.

WHY A VOCABULARY AND NOT A LOADER
-----------------------------------
This module imports NO STORE. It is vocabulary, not machinery. Each owner
implements its own `load()` against these words, because Ruling 1 means the
owner owns its own read of its own file - a shared loader would be a second
writer wearing a helper's shape. What is shared is only what a load may SAY.

THE FIVE OUTCOMES, AND THE ONE THING EACH REFUSES TO SAY
----------------------------------------------------------
    RESTORED            a clean round-trip. The file said it; the store holds it.
    MIGRATED            something the FILE DID NOT CARRY was DERIVED from
                        recorded facts elsewhere. Never silent - a derived value
                        is legitimate, but it is not the same event as a
                        restored one, and a store that reported them alike
                        would make its own provenance unreadable.
    PARTIALLY_RESTORED  some records were held out; the rest are live.
    QUARANTINED         a record referencing a MISSING REFERENT is held in a
                        named collection on its owner - visible and reported.
                        NEVER silently unlinked, NEVER merged back without a
                        ruling. An unresolvable reference is not a reason to
                        drop the record; it is a reason to stop trusting the
                        link, and those are different facts.
    REFUSED             the file is left BYTE-UNTOUCHED and the store constructs
                        EMPTY.

                            When AUREA cannot prove a budget is unused,
                            she does not assume it is unused.

                        That sentence is the whole of the refusal rule. An
                        unreadable file, an unknown `version`, or an absent
                        counter the sentence cannot excuse are all the same
                        event: she does not know, so she does not claim.

THERE IS NO `FIRST_RUN` MEMBER, AND THAT IS DELIBERATE
--------------------------------------------------------
A first run performs NO restoration, so it has nothing to report: the owner's
`load_report` stays `None`. Adding a sixth member to say "nothing happened"
would make absence into an event, and this enum is a closed vocabulary ruled at
five (CLAUDE.md section 7 - a closed enum stays closed; a sixth member is the
architect's call, not an implementer's).

    NOTE, because it is genuinely the interesting case: for RIL a first run is
    NOT silent. There is no file, but the CONSTITUTIONAL ORIGIN is derived from
    the scar owner's own seed record, and a derivation the file did not carry is
    exactly `MIGRATED`. Absence of a file and absence of a restoration are two
    different absences.

`str` ENUM - RULED, NOT STYLE
-------------------------------
The shape rule (manifest, thirty-fourth entry): NON-`str` when two vocabularies
must not collide (`ExpressionVerdict` vs `echonet.Verdict`; `LockClass` vs
`racm.Scope`); `str` when ONE vocabulary must survive serialization. This one is
SERIALIZED - into load reports and into SAE-style restart records - and it has
no collision partner anywhere in the tree. So: `str`, and the members are their
own persisted spellings, exactly as `DecayState`'s docstring argues for itself.

QUARANTINE IS LOCAL TO ITS OWNER IN THIS PASS
-----------------------------------------------
UNRULED, and flagged rather than decided: routing quarantined content onward to
CSA (it is, after all, unresolved material that did not survive a boundary) is a
WIRING decision with a real owner question behind it, and it is not this pass's
to make. Quarantine collections stay on the store that holds them, legible and
reported. Do not add a CSA route here without a ruling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class RestorationOutcome(str, Enum):
    """What kind of restoration a load performed. Closed at five - see module docstring."""

    RESTORED = "restored"
    MIGRATED = "migrated"
    PARTIALLY_RESTORED = "partially_restored"
    QUARANTINED = "quarantined"
    REFUSED = "refused"


@dataclass(frozen=True)
class LoadReport:
    """One store's account of one load.

    FROZEN, for the `TruthPacket` reason: what a load reported is a statement
    about an event that has already happened. A caller that could rewrite the
    outcome could make a REFUSED load read as a RESTORED one after the fact,
    which is the single most damaging edit available anywhere in this file.

    `detail` carries whatever the owner needs a reader to know - quarantined
    ids, derivation provenance, the refusal reason. It is deliberately untyped:
    each owner knows its own facts, and a shared schema here would be this
    module reaching into stores it is not allowed to import.
    """

    store: str
    outcome: RestorationOutcome
    path: str = ""
    resumed: bool = False
    detail: Dict[str, Any] = field(default_factory=dict)
    at: str = field(default_factory=lambda: datetime.now().isoformat())

    def as_dict(self) -> Dict[str, Any]:
        return {
            "store": self.store,
            "outcome": self.outcome.value,
            "path": self.path,
            "resumed": self.resumed,
            "detail": dict(self.detail),
            "at": self.at,
        }
