"""
cae.py - CAE: the Collapse Audit Engine. THE APPEND-ONLY AUDIT LEDGER.

Canon: 3a - "no doctrine may be mutated, collapsed, or discarded without a CAE
entry" (3a:111); entries are never overwritten and never deleted (3a:112); ids
are `CAE-###` (3a:45); the override protocol routes through CTL *and* CAE
(3a:728).

WHAT THIS FILE IS FIXING, AND IT IS NOT A MISSING FEATURE - IT IS A VOID
--------------------------------------------------------------------------
`SAE._audit` and `DEE._audit` have BOTH cited 3a:111 verbatim in their docstrings
since they were written. Both then read:

    if self.cae is None:
        return None

and `aurea_core` wired NEITHER. There was no `cae.py` anywhere in `src/`. So the
protection canon states in absolute terms was, in every real run AUREA has ever
performed, A DOCSTRING ABOVE A SOFT RETURN - and every `cae_id` on every
authorization, every ruling and every mutation record has been `None` since the
fields were added.

That is CLAUDE.md section 3's governing principle in its purest negative form: a
comment saying "no mutation without an entry" is a REQUEST FOR RESTRAINT. This
module, plus the deletion of both `is None` branches and DEFAULT-BY-CONSTRUCTION
below, is what makes the entry UNAVOIDABLE instead.

DEFAULT-BY-CONSTRUCTION (the Ruling 39 shape)
-----------------------------------------------
`SAE.__init__` and `DEE.__init__` construct their OWN `CAE()` when none is
injected, so there is no "CAE absent" state left to special-case - exactly how
Ruling 27 let RACM delete its build-stage default-grant branch (`self.tcaml =
tcaml or TCAML()`). `aurea_core` injects ONE SHARED instance into both, so the
pipeline has a single ledger with two writers of entries and zero writers of each
other's entries.

    Do NOT reintroduce `if self.cae is None`. Construct a CAE instead.

THE ID IS CONTINUITY STATE (Ruling 42 res.4)
----------------------------------------------
`CAE-###` ids are minted from a counter, and the ledger they land in PERSISTS. A
counter that restarted at zero would remint `CAE-001` over an id that already
names a recorded mutation - Nova's `_seq` defect exactly, in the one store whose
whole purpose is that its records can be cited later. So the next ordinal is
DERIVED on construction as the max over ids already in the file, with FLOOR
semantics: an unparseable line contributes nothing rather than raising, because
this is a floor and a forensic log must stay readable by a build that does not
understand every line in it.

`{n:03d}` matches canon's three-digit examples and GROWS NATURALLY past 999 -
`CAE-1000` is what the format produces, not an overflow. Do not add a wrap.

A FAILED WRITE RAISES, AND THAT IS A DELIBERATE DEPARTURE FROM RULING 11
--------------------------------------------------------------------------
Ruling 11 says the observer never gates the observed: a logging failure must not
disable a safety suppression. THIS LEDGER IS THE OTHER VALENCE. It does not gate
a PROTECTION, it gates a CHANGE - and `dee.py`'s override docstring already
states the rule in terms:

    "If logging is impossible, the override does not happen - the record is not
     a side effect of the override, it is a precondition for it."

Blocking a mutation because it cannot be recorded is the CONSERVATIVE direction:
AUREA does not change what she believes while unable to write down why. So
`record()` lets an OSError propagate. In `mutate_doctrine` that surfaces through
DEE's existing `except Exception` and the doctrine FERMENTS, which is the correct
outcome and not a new one.

FLAGGED, because it is a real cost and not a free one: `authorize()` increments
`epoch_count` BEFORE calling `_audit`, so a CAE write failure spends a ceiling
slot on a mutation that does not happen. That errs conservative - budget lost,
nothing changed - and reordering it would move Ruling 24's spend/refuse boundary,
which is a bigger change than this docket authorized.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CAE:
    """The Collapse Audit Engine. Append-only, disk-persistent, never rewritten.

    Not a store of doctrine and not an arbiter of anything: CAE records that
    something happened and hands back the id by which it can be cited. It refuses
    nothing, decides nothing, and reads nothing back into a decision.
    """

    ID_PREFIX = "CAE-"

    def __init__(self, ledger_path: str = "data/runtime/logs/cae_audit.jsonl"):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` can reach - redirected
        # there BY NAME in the same commit.
        self.ledger_path = Path(ledger_path)
        # In-memory mirror of what this process appended. NOT the ledger: the
        # file is the ledger, and this is a convenience for readers in the same
        # run. Nothing reads it back into a decision.
        self.entries: List[Dict[str, Any]] = []
        self._seq = self._derive_seq()

    # -----------------------------------------------------------------
    # THE MINT - continuity state (Ruling 42 res.4)
    # -----------------------------------------------------------------

    def _derive_seq(self) -> int:
        """The highest `CAE-` ordinal already in the ledger.

        FLOOR SEMANTICS, the Nova `_derive_seq` shape: a line that will not parse
        contributes NOTHING rather than raising. A forensic log outlives the code
        that wrote it, and a build that refuses to start because it met a line it
        does not understand has turned an append-only record into a liability.
        """
        if not self.ledger_path.exists():
            return 0
        highest = 0
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry_id = json.loads(line).get("id", "")
                    except ValueError:
                        continue
                    if isinstance(entry_id, str) and entry_id.startswith(self.ID_PREFIX):
                        tail = entry_id[len(self.ID_PREFIX):]
                        if tail.isdigit():
                            highest = max(highest, int(tail))
        except OSError:
            # Unreadable ledger: the mint cannot be derived, so it does not
            # pretend to have been. Starting at 0 here would remint over real
            # ids, so the read failure surfaces on the next append instead -
            # `record()` raises, and a mutation that cannot be audited does not
            # happen.
            return 0
        return highest

    def _next_id(self) -> str:
        self._seq += 1
        return f"{self.ID_PREFIX}{self._seq:03d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE PATH
    # -----------------------------------------------------------------

    def record(self, event: str, target: str, collapse_lineage: str = "",
               epoch: int = 0, **extra: Any) -> str:
        """Append ONE entry and return its id. The entry is never revisited.

        The signature is the one `SAE._audit` was already calling with
        (`event` / `target` / `collapse_lineage` / `epoch`) - that call site was
        written for this class before this class existed, and it is matched
        rather than redesigned.

        `**extra` carries whatever the caller needs the record to hold - for a
        doctrine mutation that is the `DoctrineMutationProof` as a dict, so the
        argument that forced the change is IN the audit entry rather than beside
        it.

        RAISES on a write failure. See the module docstring: the record is a
        PRECONDITION for the change, not a side effect of it.
        """
        entry = {
            "id": self._next_id(),
            "event": event,
            "target": target,
            "collapse_lineage": collapse_lineage,
            "epoch": epoch,
            "at": datetime.now().isoformat(),
        }
        for key, value in extra.items():
            if key not in entry:            # the six fields above are not overridable
                entry[key] = value

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        self.entries.append(entry)
        return entry["id"]

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they decide nothing
    # -----------------------------------------------------------------

    def read_all(self) -> List[Dict[str, Any]]:
        """Every entry in the ledger, in append order. A forensic read.

        Deliberately reads the FILE rather than `self.entries`: the ledger spans
        processes and the in-memory list does not.
        """
        if not self.ledger_path.exists():
            return []
        out: List[Dict[str, Any]] = []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue            # floor semantics, as in `_derive_seq`
        return out

    def get(self, entry_id: str) -> Optional[Dict[str, Any]]:
        for entry in self.read_all():
            if entry.get("id") == entry_id:
                return entry
        return None
