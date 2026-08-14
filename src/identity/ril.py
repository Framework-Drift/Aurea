"""
ril.py - RIL: the Recursive Identity Layer for AUREA.

Canon: identity threads (Origin, Scarline, Doctrine, Nova, Void) are what survives the
collapse loop and accumulates into a continuous self. CLAUDE.md Sec 2 (Ruling 1): RIL is
the SOLE WRITER of `threads`; TCAML and MSSL are REQUESTERS, not owners - they route
through RIL exactly as SBSRE/ELM/MSSL route scar formation through ScarLogicCore.

OWNERSHIP (Ruling 1) - THE ATTRIBUTE NAME IS LOAD-BEARING
-----------------------------------------------------------
`tests/invariants/test_ruling1_single_writer.py` keys STORE_OWNERS["threads"] on the
literal attribute name `threads` on this module. SBSRE already collided with this once -
it had its own `self.threads` (recursion-carrying, unrelated to identity) until the
invariant test caught it; it is now `recursion_threads` (see sbsre.py's own account of
that incident). Do not rename this attribute without updating the test's STORE_OWNERS
entry - and per CLAUDE.md Sec 4, that is not a call this module gets to make alone.

RIL reads freely from every store it touches (Codex, ScarLogicCore, ReflexGrid, CSA,
Black Sphere) - Ruling 1 only governs writes. RIL writes exactly one thing: `self.threads`.
Everything else is routed through the owning module's existing API, as a request.

THE FIVE THREADS
-----------------
    ORIGIN    the birth identity - written ONCE, from the first scar RIL ever ingests
    SCARLINE  every identity-defining scar RIL has ingested, in arrival order
    DOCTRINE  every doctrine mutation RIL has observed (via SAE-executed rulings)
    NOVA      emergent/Nova-sourced identity pulls - Nova is unbuilt, so this thread
              stays empty and HONESTLY reports empty. Same discipline as compass.py's
              EAST anchor: an empty thread is not a bug to paper over with a guess.
    VOID      RIL's own record of identity fractures it has detected - absence, not
              of data, but of continuity: a belief that was identity-anchoring, gone.

FRACTURE: GROUND IT OR ABSTAIN
--------------------------------
"An identity-defining belief fell" is only ever asserted from two OBSERVABLE facts, never
inferred more broadly:
  1. `doctrine.mutation_lineage` - Codex's own record of "what this doctrine used to be" -
     names a fallen ancestor doctrine ID for THIS mutation.
  2. That ancestor ID is already referenced by a scar RIL itself has recorded in ORIGIN or
     SCARLINE (`scar.linked_doctrines`) - i.e. RIL had already anchored identity to it.
If either fact is missing, RIL abstains. It does not widen the check, weight it, or guess
at a "probably identity-relevant" doctrine - an abstaining detector is honest; a guessing
one writes false fracture pressure into a permanent record (see EchoNet's intuition net,
CLAUDE.md Sec 0).

FRACTURE FIRES A REFLEX. IT NEVER LOCKS OUTPUT (Ruling 6 / Ruling 2).
------------------------------------------------------------------------
On a grounded fracture, RIL SOURCES pressure to ICA through the exact same
`reflex_grid.evaluate_pressure(...)` path compass.py already uses for anchor_collapse -
RIL never arbitrates (Ruling 2: source vs sole arbiter) and never touches output directly
(Ruling 6: the lock, if any, is the CONSEQUENCE of RACM authorizing a reflex's
output_blocked - that is aurea_core's job at its own wiring point, not RIL's). RIL reads
the RETURNED `List[ReflexResponse]` from `evaluate_pressure` - never
`reflex_grid.last_arbitration`, which is a shared field, stale across cycles and
clobbered by later, unrelated registrations (the exact hazard Ruling 6 already ruled out
for compass; the same hazard applies to any caller of evaluate_pressure, RIL included).

If RACM does not authorize ICA to act on the fracture pressure (deferred/suppressed),
the fracture does not just vanish: RIL routes it to CSA as a REQUEST
(`self.csa.suspend(...)`), the same pattern SBSRE already uses when its own abort reflex
fires and the partial thread still needs a home. Black Sphere is wired in (RIL's map
session named it as an option) but never auto-selected here: distinguishing a truly
irreducible identity paradox from an ordinary volatile fracture would require paradox
classification data RIL does not have at this layer. Ground it or abstain applies to that
choice too - CSA is the defensible default, Black Sphere is left for a future session
with the missing signal.

CONTINUITY: THE THREADS ARE DURABLE, AND ORIGIN IS CONSTITUTIONAL (Ruling 42)
------------------------------------------------------------------------------
Until Ruling 42 this store was PURELY IN-MEMORY. `threads` was built empty in
`__init__` and never written to disk, so every process death emptied ORIGIN -
and the "written ONCE" guard below, which is correct and untouched, guarded
nothing across a restart. THE FIRST SCAR AFTER A RESTART BECAME HER BIRTH
IDENTITY. A guard whose scope is one process is not a guard on a fact that is
supposed to hold for a lifetime.

So the threads persist (`runtime_path`, under `data/runtime/` per Rulings 32 and
39), with Ruling 32's minimal semantics VERBATIM: load reads runtime if present,
save writes a whole-file snapshot, and there is NO layering, NO delta and NO
merge rule. There is also NO SEED THREAD FILE - identity is ACCUMULATED, never
issued, exactly as SAE's epoch is (Ruling 34).

ENTRIES ARE BY-ID REFERENCES, NOT EMBEDDED RECORDS (Ruling 42 res.2)
----------------------------------------------------------------------
ORIGIN and SCARLINE used to hold the LIVE `Scar` OBJECTS aurea_core handed in -
the same objects living in ScarLogicCore's list. That made an identity thread a
WRITE PATH INTO THE SCAR STORE: anything holding a thread entry could set
`.weight`, clear `.linked_doctrines` or flip `.decay_state`, and the Ruling 1
single-writer scanner cannot see it, because nothing assigns to `scar_core.scars`.
psi.py's own `_live_weight` docstring had already named the hazard in words -
"a held Scar reference is a held write path" - while RIL held one per scar.

Entries are now dicts naming the record and the facts RIL ASSERTED AT INGEST:

    {"record_type": "scar", "record_id": "...", "linked_doctrines": [...], ...}

RIL records that it anchored identity to a scar. It does not carry the scar's
MAGNITUDES: weight and decay belong to SML (Ruling 1, and Ruling 15's
generalization - the owner owns the write INCLUDING its magnitudes), so a weight
copied into an identity thread would be a non-owner carrying an owner's number
into a permanent record. A reader that wants a weight asks the owner.

`_anchored_in_identity` therefore reads BOTH the at-ingest `linked_doctrines`
RIL recorded AND the owner's LIVE record - a union, Ruling 26's bidirectional
shape one layer up. That is not a widening: holding the live object made the old
read live BY ACCIDENT, and asking the owner makes it live BY CONTRACT.

ORIGIN IS CONSTITUTIONAL (Ruling 42 res.3)
--------------------------------------------
When a load leaves ORIGIN empty, RIL ASKS THE SCAR OWNER - never opening a file
itself (Ruling 1) - for the SEED scar tagged `origin`, and requires EXACTLY ONE.
Found: ORIGIN gets its by-ID entry, provenance `constitutional`, and the load
reports `MIGRATED`, because a value derived from facts the file did not carry is
not the same event as a value restored from one.

Zero or several: ORIGIN STAYS EMPTY and a VOID discontinuity entry records that
the constitutional origin was UNRESOLVABLE. Declared, never claimed - the
abstaining-detector discipline this module already applies to fracture, applied
to its own birth.

NO OWNER AT ALL is a THIRD case and NOT a discontinuity: no instrument ran, so
there is nothing to declare unresolvable (Docket H's `NOT_COUNTABLE`-vs-
`NONE_FOUND` cut - two absences that are not the same absence). A bare
`RIL()` keeps the `is_root` semantics it has always had, and persistence then
makes even that assignment permanent.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.atomic_write import atomic_write_json
from src.utils.continuity import LoadReport, RestorationOutcome
from src.utils.models import Scar, Doctrine
from src.doctrine.dee import EligibilityRuling
from src.reflex.reflex_grid import ReflexResponse


class IdentityThread(Enum):
    ORIGIN = "origin"
    SCARLINE = "scarline"
    DOCTRINE = "doctrine"
    NOVA = "nova"
    VOID = "void"


# COINED (not recovered from corpus): a fracture-pressure magnitude past ICA's own 0.7
# threshold (reflex_grid.py's SymbolicReflex default), so the fracture reliably clears
# ICA's gate. Chosen inside ICA's REROUTE band (0.7-0.9), not its suppress band (>0.9) -
# RIL raises the pressure, it does not pick ICA's severity for it. Register in
# Aurea Build/COINED_CONSTANTS.md the next time that file is in scope (this session is
# ril.py-only).
#
# ^ THAT ASK IS DISCHARGED, and the sentence above is kept rather than deleted
#   because it is the record of when the debt was taken on. SUPERSEDED 2026-07-28
#   (Ruling 43 rider): `IDENTITY_FRACTURE_PRESSURE` HAS a full row in
#   `Aurea Build/COINED_CONSTANTS.md`, in the RIL section, stamped
#   `[coined 2026-07-19]` - i.e. it was registered the same day the note asked,
#   and the note has been stale ever since. VERIFIED BY READING THAT FILE THIS
#   PASS, not assumed: an in-file note that asks for something already done reads
#   as an open debt forever, and a false open debt is the same defect as a false
#   completeness claim wearing the opposite sign.
IDENTITY_FRACTURE_PRESSURE = 0.75

# Ruling 42 res.3. The tag the scar owner's SEED records carry to mark AUREA's
# constitutional origin. `data/scars.json` carries exactly one such record
# (`Scar-0`, `tca_tags: ["origin"]`). RECOVERED FROM THE SEED, not coined: this
# is a name that already exists in the tracked corpus, read rather than invented.
#
# TAG, NOT NAME AND NOT ID. A name-match or id-match heuristic ("the one called
# Scar-0") would make the constitution depend on a spelling; the tag is the
# seed's own declaration of what the record IS.
CONSTITUTIONAL_ORIGIN_TAG = "origin"

# The record kinds a thread entry may name. Closed - an entry that names no
# record is not a reference, it is prose.
RECORD_TYPE_SCAR = "scar"
RECORD_TYPE_DISCONTINUITY = "discontinuity"


class RIL:
    """Recursive Identity Layer. Accumulates the five identity threads; sources ICA on
    a grounded fracture; routes what ICA doesn't resolve to CSA as a request. Arbitrates
    nothing, locks nothing, writes nothing but `self.threads`.

    Deliberately no `__bool__`/`__len__`: a freshly-constructed RIL with five empty
    threads is a real, valid RIL - not a falsy one. Defining either would make
    `if ril:` silently lie the moment every thread is still empty.
    """

    STATE_VERSION = 1

    def __init__(self, codex: Any = None, scar_core: Any = None,
                 black_sphere: Any = None, csa: Any = None,
                 reflex_grid: Any = None,
                 runtime_path: str = "data/runtime/ril_threads.json",
                 obligation_ledger: Any = None):
        self.codex = codex               # doctrine content OWNER; RIL is a reader
        self.scar_core = scar_core       # scar OWNER; RIL is a reader, never form_scar
        self.black_sphere = black_sphere  # paradox suspension; RIL routes as a REQUEST
        self.csa = csa                   # volatile-content suspension; RIL REQUESTS
        self.reflex_grid = reflex_grid   # ICA is SOURCED here; RACM arbitrates, not RIL

        # Ruling 42 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` - one of
        # the exactly two shapes `tests/conftest.py` can reach, redirected there BY
        # NAME in the same commit. SAE's `runtime_path` is the template.
        self.runtime_path = Path(runtime_path)

        # SOLE WRITER (Ruling 1). Attribute name is exactly `threads` - load-bearing,
        # see the module docstring's OWNERSHIP section.
        self.threads: Dict[IdentityThread, List[Any]] = {t: [] for t in IdentityThread}

        # Ruling 42 taxonomy. `load_report` is None on a run that restored NOTHING -
        # a first run performs no restoration, so it has nothing to report, and a
        # sixth enum member to say "nothing happened" would make absence an event.
        self.load_report: Optional[LoadReport] = None
        # Entries whose referent the scar owner cannot resolve. HELD, VISIBLE,
        # REPORTED - never silently unlinked, never merged back without a ruling.
        self.quarantined: List[Dict[str, Any]] = []
        # Ruling 11's `flush_failures` shape: the observer never gates the observed.
        self.persist_failures: List[Dict[str, Any]] = []

        # M3-D §1.3 - THE ADMISSION SEAM. K2's ledger, held as a REQUESTER.
        # `None` is the honest default: a bare RIL admits nothing, so
        # constructing one incidentally never writes an obligation.
        self.obligation_ledger = obligation_ledger
        # ADMISSION FAILURES ARE RECORDED, NEVER RAISED (Ruling 11's line, and
        # the reason this surface exists): an identity fracture must fire even
        # if the obligation cannot be written. A recorded failure is not a
        # silent loss; a gated protective reflex is a defect.
        self.admission_failures: List[Dict[str, Any]] = []

        self.load()
        self._restore_constitutional_origin()

    # =================================================================
    # INGESTION - the two live handoffs (aurea_core wiring points, not built here)
    # =================================================================

    def ingest_scar(self, scar: Scar) -> None:
        """Scarline handoff. Called with the `Scar` aurea_core already has in hand at
        its own `result['scar_formed']` point - RIL never calls `form_scar` itself
        (ScarLogicCore is the sole scar-store writer; RIL is a requester like every
        other module, Ruling 1)."""
        is_root = not self.threads[IdentityThread.SCARLINE]
        self.threads[IdentityThread.SCARLINE].append(
            self._scar_entry(scar, provenance="ingest"))

        # ORIGIN is written ONCE. Guarded on ORIGIN's own state, not merely inferred
        # from SCARLINE's emptiness - so a future change to how SCARLINE grows cannot
        # silently reopen the overwrite this guard exists to prevent.
        #
        # RULING 42: THE GUARD IS UNCHANGED AND WAS ALWAYS CORRECT. What changed is
        # that it now guards across process boundaries too - both threads are
        # restored from disk before this runs, so a restart no longer presents a
        # freshly-empty ORIGIN for the next scar to claim.
        if is_root and not self.threads[IdentityThread.ORIGIN]:
            self.threads[IdentityThread.ORIGIN].append(
                self._scar_entry(scar, provenance="ingest"))

        self._persist()

    @staticmethod
    def _scar_entry(scar: Scar, provenance: str) -> Dict[str, Any]:
        """A BY-ID reference plus the facts RIL asserted at ingest (Ruling 42 res.2).

        NO MAGNITUDES. `weight` and `decay_state` are SML's (Ruling 1), and a
        non-owner carrying an owner's number into a permanent record is Ruling 15's
        disguised write. A reader wanting a weight asks the scar owner - which is
        what `psi._live_weight` already did FIRST, before falling back to the
        embedded object this entry replaces.
        """
        return {
            "record_type": RECORD_TYPE_SCAR,
            "record_id": scar.id,
            "linked_doctrines": list(scar.linked_doctrines or []),
            "provenance": provenance,
            "ingested_at": datetime.now().isoformat(),
        }

    def ingest_doctrine_mutation(self, ruling: EligibilityRuling,
                                  doctrine: Doctrine) -> None:
        """Doctrine handoff. Called with the ruling and the post-mutation `Doctrine`
        (`codex.get(ruling.doctrine_id)`) at aurea_core's `ruling.executed_by == 'SAE'`
        point. Always records the mutation on DOCTRINE. Fires ICA only when the
        mutation's fallen ancestor was already identity-anchored - see the module
        docstring's FRACTURE section for exactly what "grounded" means here.
        """
        self.threads[IdentityThread.DOCTRINE].append({
            "doctrine_id": doctrine.id,
            "verdict": ruling.verdict,
            "reason": ruling.reason,
            "mutation_lineage": list(doctrine.mutation_lineage),
        })

        # Fact 1: does this mutation name a fallen ancestor at all?
        ancestor_id = doctrine.mutation_lineage[-1] if doctrine.mutation_lineage else None
        if ancestor_id is None:
            self._persist()
            return  # nothing fell - no ancestor to ground a fracture in. Abstain.

        # Fact 2: was that ancestor already anchored in RIL's own identity threads?
        if not self._anchored_in_identity(ancestor_id):
            self._persist()
            return  # not grounded - RIL never held this doctrine as identity. Abstain.

        # ---- Both facts present: an identity-defining belief fell. ----
        self.threads[IdentityThread.VOID].append({
            "doctrine_id": doctrine.id,
            "fallen_ancestor": ancestor_id,
            "ruling_reason": ruling.reason,
        })
        self._persist()

        responses = self._fire_ica(doctrine, ancestor_id, ruling)
        ica_response = next((r for r in responses if r.reflex_id == "ICA"), None)
        if ica_response is None and self.csa is not None:
            # RACM did not authorize ICA to act on this fracture. The conflict does not
            # just vanish - route it to CSA as a REQUEST, the same pattern SBSRE already
            # uses when its own abort reflex fires and the partial thread needs a home.
            self.csa.suspend(
                content=(f"identity fracture: doctrine {doctrine.id} superseded "
                         f"{ancestor_id}, an ancestor RIL had anchored identity to"),
                pressure=IDENTITY_FRACTURE_PRESSURE,
                reason=(f"ICA not authorized to resolve identity fracture "
                        f"({ruling.reason})"),
            )

    def _anchored_in_identity(self, doctrine_id: str) -> bool:
        """Grounded check: does any scar RIL has already recorded in ORIGIN or SCARLINE
        link to this doctrine ID? Uses `scar.linked_doctrines`, the same field
        aurea_core's own DEE pressure-signal pass reads for scar<->doctrine touch.

        RULING 42: reads a UNION of RIL's at-ingest record and the OWNER'S LIVE one.
        Holding the live `Scar` object used to make this read live BY ACCIDENT - the
        stored object was the store's object, so an owner-side edit showed up here.
        By-ID entries end that accident, so the live half is now obtained the way it
        should always have been: by ASKING THE OWNER. Ruling 26's bidirectional shape
        - a union of two partial views, never either alone.

        No owner (a bare `RIL()`): the at-ingest half stands alone. That is RIL's own
        record of what it anchored, which is the half this module is entitled to.
        """
        for thread in (IdentityThread.ORIGIN, IdentityThread.SCARLINE):
            for entry in self.threads[thread]:
                if doctrine_id in self._entry_links(entry):
                    return True
        return False

    def _entry_links(self, entry: Any) -> List[str]:
        """At-ingest links UNION the owner's current links for the same record."""
        if not isinstance(entry, dict):
            return []
        links = list(entry.get("linked_doctrines") or [])
        record_id = entry.get("record_id")
        live = self._owner_scar(record_id)
        if live is not None:
            links.extend(d for d in (live.linked_doctrines or []) if d not in links)
        return links

    def _owner_scar(self, record_id: Optional[str]) -> Optional[Scar]:
        """Resolve a referenced scar THROUGH ITS OWNER. Reads are free (Ruling 1),
        and `get_scar` snapshots (Ruling 22), so nothing reachable from here is a
        write path back into the scar store."""
        if not record_id or self.scar_core is None:
            return None
        getter = getattr(self.scar_core, "get_scar", None)
        return getter(record_id) if callable(getter) else None

    def _fire_ica(self, doctrine: Doctrine, ancestor_id: str,
                   ruling: EligibilityRuling) -> List[ReflexResponse]:
        """Source ICA the same way compass.py sources ANCHOR_COLLAPSE: through
        evaluate_pressure, reading its RETURN VALUE (never last_arbitration - Ruling 6).
        RIL sources; RACM arbitrates. RIL never calls .trigger() and never inspects or
        sets output_blocked itself."""
        # M3-D §1.3: ADMIT THE OBLIGATION FIRST, then fire. ADDITIVE - the
        # reflex path below is byte-unchanged - and BEST-EFFORT: the admission
        # is wrapped so that NO failure here can stop an identity fracture from
        # reaching the Grid. Ruling 11's line exactly: the observer never gates
        # the observed, and this is a protective response.
        self._admit_fracture(doctrine, ancestor_id, ruling)

        if self.reflex_grid is None:
            return []
        return self.reflex_grid.evaluate_pressure(
            source_module="RIL",
            pressure_type="identity_fracture",
            pressure_level=IDENTITY_FRACTURE_PRESSURE,
            metadata={
                "doctrine_id": doctrine.id,
                "fallen_ancestor": ancestor_id,
                "ruling_reason": ruling.reason,
            },
        )

    def _admit_fracture(self, doctrine: Doctrine, ancestor_id: str,
                        ruling: EligibilityRuling) -> None:
        """Admit the identity fracture as an OBLIGATION. Best-effort, always.

        M3-D §1.3. RIL is a REQUESTER at K2's door exactly as it is at the
        scar owner's: it calls `admit(...)` and never writes the ledger itself.

        **THE ADMISSION NEVER GATES THE REFLEX.** Every failure - no ledger, an
        unwritable file, a refused admission, anything at all - lands on
        `admission_failures` and the fracture fires regardless. An identity
        fracture is a protective response, and Ruling 11's rule about a logging
        failure never disabling a safety suppression binds here in the same
        words. The broad `except` is deliberate and is the ONE place in this
        module where that is correct.

        A REJECTED admission is not a failure and is not recorded here: the
        ledger wrote a REJECTED record, which is the outcome, and duplicate
        suppression of a repeated fracture is the ledger working.
        """
        if self.obligation_ledger is None:
            return
        try:
            self.obligation_ledger.admit(
                source="RIL",
                target_kind="doctrine",
                target_id=doctrine.id,
                claim_text=(
                    f"identity fracture: '{doctrine.id}' descends from fallen "
                    f"ancestor '{ancestor_id}' - {ruling.reason}"),
            )
        except Exception as exc:                      # noqa: BLE001 - see docstring
            self.admission_failures.append({
                "doctrine_id": doctrine.id,
                "ancestor_id": ancestor_id,
                "error": f"{type(exc).__name__}: {exc}",
            })

    # =================================================================
    # INBOUND REQUESTS (SPECULATIVE - no live caller today)
    # =================================================================

    def request_thread_write(self, thread: IdentityThread, entry: Any,
                              requester: str) -> Any:
        """SPECULATIVE. Mirrors ScarLogicCore.form_scar's shape (execute the request,
        return the record) for RIL's documented requesters (CLAUDE.md Sec 2: TCAML,
        MSSL). Neither exists in this repo yet - tcaml.py is a 0-byte stub, and MSSL has
        no file anywhere in the tree - so this method has NO LIVE CALLER as of this
        session. Kept deliberately minimal: no validation, no routing, no fracture
        detection beyond what ingest_doctrine_mutation already does. Do not build this
        out further against an imagined caller; build it out when TCAML or MSSL are
        real and their actual request shape is known.
        """
        self.threads[thread].append(entry)
        self._persist()
        return entry

    # =================================================================
    # CONTINUITY (Ruling 42) - the threads cross the process boundary
    # =================================================================

    def save(self) -> None:
        """Whole-file snapshot to the runtime path.

        RULING 32'S MINIMAL SEMANTICS, VERBATIM: no layering, no delta format, no
        merge rule. A snapshot replaces a snapshot.

        Threads are keyed by the enum's VALUE so the file stays plain JSON and a
        reader needs nothing from this module to understand it.

        DELIBERATELY NO `default=str`. Every entry this module writes is already
        JSON-native (by-ID dicts, ISO strings), so a value that cannot serialize
        means some caller put a live object on a thread - the exact defect res.2
        closes. `default=str` would stringify it and the file would look fine,
        which is the fail-silent shape. It raises instead, and `_persist` records.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.STATE_VERSION,
            "saved_at": datetime.now().isoformat(),
            "threads": {t.value: list(self.threads[t]) for t in IdentityThread},
        }
        # Rider R3 (2026-07-29): ATOMIC. ORIGIN is written ONCE and is her birth
        # identity; a torn write is the one loss this file exists to prevent
        # (Ruling 42: "the first scar after a restart became her birth identity").
        atomic_write_json(self.runtime_path, payload, indent=2)

    def load(self) -> bool:
        """Runtime state if present, ELSE empty threads. Returns whether state resumed.

        THERE IS NO SEED THREAD FILE. Identity is ACCUMULATED, never issued - SAE's
        epoch reasoning (Ruling 34) applied to the store that holds who she is. A
        missing file is a first run.

        REFUSAL LEAVES THE FILE BYTE-UNTOUCHED. An unreadable file or an unknown
        `version` constructs an EMPTY store and records the refusal; it does not
        rewrite, migrate or truncate what it could not read. When AUREA cannot
        prove what a record says, she does not overwrite it with a guess.
        """
        if not self.runtime_path.exists():
            return False

        try:
            with open(self.runtime_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"expected a JSON object, got {type(data).__name__}")
        except (OSError, ValueError) as exc:
            return self._refuse(f"unreadable identity state: {exc!r}")

        version = data.get("version")
        if version != self.STATE_VERSION:
            return self._refuse(
                f"unknown state version {version!r} (this build writes "
                f"{self.STATE_VERSION}); the file was left untouched")

        restored = {t: list(data.get("threads", {}).get(t.value, []) or [])
                    for t in IdentityThread}

        # Referent check, and ONLY where an instrument exists. No scar owner means
        # no lookup ran - which is not the same fact as a lookup that found nothing
        # (Docket H's NOT_COUNTABLE / NONE_FOUND cut), so it quarantines nothing.
        held: List[Dict[str, Any]] = []
        if self.scar_core is not None:
            for thread in (IdentityThread.ORIGIN, IdentityThread.SCARLINE):
                kept = []
                for entry in restored[thread]:
                    if self._referent_missing(entry):
                        held.append({"thread": thread.value, "entry": entry,
                                     "reason": "referenced scar not in the scar store"})
                    else:
                        kept.append(entry)
                restored[thread] = kept

        self.threads = restored
        self.quarantined.extend(held)

        if held:
            self._report(RestorationOutcome.PARTIALLY_RESTORED, resumed=True,
                         detail={"quarantined": len(held),
                                 "quarantined_ids": [h["entry"].get("record_id")
                                                     for h in held]})
        else:
            self._report(RestorationOutcome.RESTORED, resumed=True,
                         detail={"saved_at": data.get("saved_at")})
        return True

    def _referent_missing(self, entry: Any) -> bool:
        """A scar entry naming a record the OWNER cannot resolve."""
        if not isinstance(entry, dict) or entry.get("record_type") != RECORD_TYPE_SCAR:
            return False
        return self._owner_scar(entry.get("record_id")) is None

    def _restore_constitutional_origin(self) -> None:
        """RULING 42 res.3 - ORIGIN IS CONSTITUTIONAL, not merely first-seen.

        Runs only when a load left ORIGIN EMPTY. Asks the scar OWNER (never a file -
        Ruling 1) for the SEED record tagged `origin`, and requires EXACTLY ONE.

        WHY `is_seed` IS PART OF THE FILTER: her constitution is what she was born
        with. A scar formed at RUNTIME and tagged `origin` is a runtime fact, and
        letting one qualify would make the birth identity re-derivable from
        something that happened afterwards - which is the very overwrite this
        ruling exists to make impossible.

        ZERO OR SEVERAL: ORIGIN STAYS EMPTY and a VOID discontinuity entry declares
        the question unresolvable. It does not pick one, and it does not fall back
        to a name or id match: an ambiguous constitution is a fact to record, not a
        tie to break. NO OWNER AT ALL records nothing - no instrument ran.
        """
        if self.threads[IdentityThread.ORIGIN] or self.scar_core is None:
            return

        finder = getattr(self.scar_core, "seed_scars_tagged", None)
        if not callable(finder):
            return
        candidates = list(finder(CONSTITUTIONAL_ORIGIN_TAG) or [])

        if len(candidates) == 1:
            self.threads[IdentityThread.ORIGIN].append(
                self._scar_entry(candidates[0], provenance="constitutional"))
            self._report(
                RestorationOutcome.MIGRATED,
                resumed=self.load_report.resumed if self.load_report else False,
                detail={"origin_provenance": "constitutional",
                        "origin_record_id": candidates[0].id,
                        "derived": "ORIGIN was not carried by the state file and was "
                                   "derived from the scar owner's seed record"})
            self._persist()
            return

        self.threads[IdentityThread.VOID].append({
            "record_type": RECORD_TYPE_DISCONTINUITY,
            "kind": "constitutional_origin_unresolvable",
            "candidate_ids": sorted(getattr(c, "id", "") for c in candidates),
            "reason": (f"expected exactly one seed scar tagged "
                       f"'{CONSTITUTIONAL_ORIGIN_TAG}', found {len(candidates)}"),
            "at": datetime.now().isoformat(),
        })
        self._persist()

    # -- reporting + best-effort write -----------------------------------

    def _report(self, outcome: RestorationOutcome, resumed: bool,
                detail: Optional[Dict[str, Any]] = None) -> None:
        """Record what kind of restoration this was.

        PRECEDENCE, when a load is more than one thing at once: a REFUSAL outranks
        a partial restoration, which outranks a derivation, which outranks a clean
        one. The headline is the most serious fact; the rest survive in `detail`,
        so nothing is lost to the ranking.
        """
        order = {
            RestorationOutcome.RESTORED: 0,
            RestorationOutcome.MIGRATED: 1,
            RestorationOutcome.QUARANTINED: 2,
            RestorationOutcome.PARTIALLY_RESTORED: 2,
            RestorationOutcome.REFUSED: 3,
        }
        merged = dict(self.load_report.detail) if self.load_report else {}
        merged.update(detail or {})
        if self.load_report is not None and order[self.load_report.outcome] > order[outcome]:
            outcome = self.load_report.outcome
        self.load_report = LoadReport(
            store="ril.threads", outcome=outcome, path=str(self.runtime_path),
            resumed=resumed, detail=merged)

    def _refuse(self, reason: str) -> bool:
        self.threads = {t: [] for t in IdentityThread}
        self._report(RestorationOutcome.REFUSED, resumed=False, detail={"reason": reason})
        return False

    def _persist(self) -> None:
        """BEST-EFFORT save. NEVER RAISES.

        Ruling 11's `flush_failures` shape, and the trade-off was accepted at the
        manifest's twenty-eighth entry rather than re-argued here: a disk problem
        must not become a NEW REFUSAL PATH inside the identity layer. A failed save
        lands on `persist_failures`, where it is legible.

        FLAGGED, because it is the same real cost SAE's `_persist` carries: if a
        save fails, this process still holds the correct ORIGIN, but a restart
        would resume from the last successful snapshot.
        """
        if self.load_report is not None \
                and self.load_report.outcome is RestorationOutcome.REFUSED:
            # A refusal left a file we could not read. Do not overwrite it - that
            # is the whole content of "BYTE-UNTOUCHED".
            return
        try:
            self.save()
        except (OSError, TypeError, ValueError) as exc:
            self.persist_failures.append({
                "op": "save", "path": str(self.runtime_path), "error": repr(exc),
                "at": datetime.now().isoformat(),
            })

    # =================================================================
    # READ VIEWS - DEEP SNAPSHOTS ONLY
    # =================================================================

    def identity_conflict(self, doctrine_id: str) -> bool:
        """CMTE criterion 4: does RIL flag this doctrine as contradicting selfhood?

        RULING 45. CMTE has asked `context.get("ril_identity_conflict")` since it
        was written, and NOTHING HAS EVER SUPPLIED THE KEY - `aurea_core`'s
        context builder passes `echo_origin` and nothing else, so criterion 4 has
        passed by absence in every run AUREA has performed. This is the supplier.

        GROUND IT OR ABSTAIN, and this method invents no heuristic beyond what the
        threads already record. The VOID thread is, in this module's own words,
        "RIL's own record of identity fractures it has detected - absence, not of
        data, but of continuity: a belief that was identity-anchoring, gone." A
        doctrine NAMED in one of those records is flagged BY RIL'S OWN RECORD;
        there is nothing to infer.

        So: True iff a VOID FRACTURE entry names this doctrine - either as the
        successor whose arrival fractured identity (`doctrine_id`) or as the
        anchored ancestor that fell (`fallen_ancestor`). Both are facts RIL wrote
        down after grounding them on two observable checks (see the module
        docstring's FRACTURE section); neither is re-derived here.

        WHAT IS DELIBERATELY NOT CONSULTED:
          * DISCONTINUITY entries (`record_type == "discontinuity"`) - those
            record that a question was UNRESOLVABLE (Ruling 42's constitutional
            origin), which is not a fracture and names no doctrine.
          * anything about how RECENT, how HEAVY or how MANY. A count would need
            a threshold, and that threshold would be a coined magnitude at a
            mutation gate (section 9 standing bar #5).

        ABSTAINS BY RETURNING FALSE, and the caller's absent-key path means the
        same thing: no grounds is not a clean bill of health, it is silence. The
        proof records that silence as ABSENT rather than PASS, which is where the
        distinction is kept honest (`CriterionResult`).
        """
        if not doctrine_id:
            return False
        for entry in self.threads[IdentityThread.VOID]:
            if not isinstance(entry, dict):
                continue
            if entry.get("record_type") == RECORD_TYPE_DISCONTINUITY:
                continue
            if doctrine_id in (entry.get("doctrine_id"),
                               entry.get("fallen_ancestor")):
                return True
        return False

    def dominant_thread(self) -> Optional[IdentityThread]:
        """Whichever thread currently carries the most entries. COINED: the corpus
        names the five threads but does not define "dominant" as a magnitude, so this
        uses entry count - the simplest metric that cannot be gamed by content, only by
        volume. Ties favor the earlier-declared thread (ORIGIN first) via
        IdentityThread's own iteration order - `max` keeps the first-seen maximum.

        Returns an enum member, not thread content - enum members are immutable
        singletons, so there is nothing here for a caller to mutate back into
        self.threads. The DEEP SNAPSHOT guarantee is what `thread_state` exists for.
        """
        if not any(self.threads.values()):
            return None
        return max(IdentityThread, key=lambda t: len(self.threads[t]))

    def thread_state(
        self, thread: Optional[IdentityThread] = None
    ) -> Dict[IdentityThread, List[Any]]:
        """Read-only DEEP snapshot of one thread or all five. Mirrors Codex's own
        `_snapshot`/`copy.deepcopy` pattern (codex.py) exactly - a caller mutating
        anything in the returned structure must never be able to reach `self.threads`.

        Always returns a dict keyed by IdentityThread, even for a single thread, so
        callers do not need two different return shapes depending on the argument.
        """
        if thread is not None:
            return {thread: copy.deepcopy(self.threads[thread])}
        return copy.deepcopy(self.threads)
