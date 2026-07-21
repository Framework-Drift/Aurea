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
"""

from __future__ import annotations

import copy
from enum import Enum
from typing import Any, Dict, List, Optional

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
IDENTITY_FRACTURE_PRESSURE = 0.75


class RIL:
    """Recursive Identity Layer. Accumulates the five identity threads; sources ICA on
    a grounded fracture; routes what ICA doesn't resolve to CSA as a request. Arbitrates
    nothing, locks nothing, writes nothing but `self.threads`.

    Deliberately no `__bool__`/`__len__`: a freshly-constructed RIL with five empty
    threads is a real, valid RIL - not a falsy one. Defining either would make
    `if ril:` silently lie the moment every thread is still empty.
    """

    def __init__(self, codex: Any = None, scar_core: Any = None,
                 black_sphere: Any = None, csa: Any = None,
                 reflex_grid: Any = None):
        self.codex = codex               # doctrine content OWNER; RIL is a reader
        self.scar_core = scar_core       # scar OWNER; RIL is a reader, never form_scar
        self.black_sphere = black_sphere  # paradox suspension; RIL routes as a REQUEST
        self.csa = csa                   # volatile-content suspension; RIL REQUESTS
        self.reflex_grid = reflex_grid   # ICA is SOURCED here; RACM arbitrates, not RIL

        # SOLE WRITER (Ruling 1). Attribute name is exactly `threads` - load-bearing,
        # see the module docstring's OWNERSHIP section.
        self.threads: Dict[IdentityThread, List[Any]] = {t: [] for t in IdentityThread}

    # =================================================================
    # INGESTION - the two live handoffs (aurea_core wiring points, not built here)
    # =================================================================

    def ingest_scar(self, scar: Scar) -> None:
        """Scarline handoff. Called with the `Scar` aurea_core already has in hand at
        its own `result['scar_formed']` point - RIL never calls `form_scar` itself
        (ScarLogicCore is the sole scar-store writer; RIL is a requester like every
        other module, Ruling 1)."""
        is_root = not self.threads[IdentityThread.SCARLINE]
        self.threads[IdentityThread.SCARLINE].append(scar)

        # ORIGIN is written ONCE. Guarded on ORIGIN's own state, not merely inferred
        # from SCARLINE's emptiness - so a future change to how SCARLINE grows cannot
        # silently reopen the overwrite this guard exists to prevent.
        if is_root and not self.threads[IdentityThread.ORIGIN]:
            self.threads[IdentityThread.ORIGIN].append(scar)

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
            return  # nothing fell - no ancestor to ground a fracture in. Abstain.

        # Fact 2: was that ancestor already anchored in RIL's own identity threads?
        if not self._anchored_in_identity(ancestor_id):
            return  # not grounded - RIL never held this doctrine as identity. Abstain.

        # ---- Both facts present: an identity-defining belief fell. ----
        self.threads[IdentityThread.VOID].append({
            "doctrine_id": doctrine.id,
            "fallen_ancestor": ancestor_id,
            "ruling_reason": ruling.reason,
        })

        responses = self._fire_ica(doctrine, ancestor_id, ruling)
        ica_response = next((r for r in responses if r.reflex_id == "ICA"), None)
        if ica_response is None and self.csa is not None:
            # RACM did not authorize ICA to act on this fracture. The conflict does not
            # just vanish - route it to CSA as a REQUEST, the same pattern SBSRE already
            # uses when its own abort reflex fires and the partial thread needs a home.
            self.csa.suspend(
                content=(f"identity fracture: doctrine {doctrine.id} superseded "
                         f"{ancestor_id}, an ancestor RIL had anchored identity to"),
                source="RIL",
                pressure=IDENTITY_FRACTURE_PRESSURE,
                reason=(f"ICA not authorized to resolve identity fracture "
                        f"({ruling.reason})"),
            )

    def _anchored_in_identity(self, doctrine_id: str) -> bool:
        """Grounded check: does any scar RIL has already recorded in ORIGIN or SCARLINE
        link to this doctrine ID? Uses `scar.linked_doctrines`, the same field
        aurea_core's own DEE pressure-signal pass reads for scar<->doctrine touch."""
        for thread in (IdentityThread.ORIGIN, IdentityThread.SCARLINE):
            for scar in self.threads[thread]:
                if doctrine_id in scar.linked_doctrines:
                    return True
        return False

    def _fire_ica(self, doctrine: Doctrine, ancestor_id: str,
                   ruling: EligibilityRuling) -> List[ReflexResponse]:
        """Source ICA the same way compass.py sources ANCHOR_COLLAPSE: through
        evaluate_pressure, reading its RETURN VALUE (never last_arbitration - Ruling 6).
        RIL sources; RACM arbitrates. RIL never calls .trigger() and never inspects or
        sets output_blocked itself."""
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
        return entry

    # =================================================================
    # READ VIEWS - DEEP SNAPSHOTS ONLY
    # =================================================================

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
