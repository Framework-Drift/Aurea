"""
doctrine_spine.py - The Doctrine Spine: the skeletal structure of self.

Canon: 3b "MODULE: Doctrine Spine + Codex - v2.0"; 0_Core:479 ("Doctrines form skeletal
structure of self"); 0_Core:1206 ("[Doctrine Spine] (Codex Layer)"); Dependency Map §7
("Doctrine Spine (including Codex, DEE, Harmonizer, DML, DPA)").

RULING 5 - DOCTRINE OWNERSHIP (2026-07-11)
------------------------------------------
The Spine is the LAYER. The Codex is the STORE inside it. SAE is the EXECUTOR.

    Doctrine Spine  ->  structure, orientation, reading, REQUESTS      (this file)
    Codex           ->  the doctrine store; sole writer of `doctrines` (codex.py)
    DEE / CMTE      ->  eligibility gate                                (dee.py)
    SAE             ->  sole executor of mutation                       (expansion/sae.py)

WHAT WAS REMOVED, AND WHY
-------------------------
This module previously held `self.doctrines` and defined:

    mutate_doctrine(doctrine_id, new_name)  ->  renamed a doctrine in place, appended the
                                                old name to lineage, saved to disk.

That method changed AUREA's identity with no scar behind it, no DEE eligibility, no
ceiling decrement, no CAE audit entry, and no ⊗ fossil of what fell. It is a path by
which a doctrine becomes something else WITHOUT SURVIVING ANYTHING - the precise failure
the whole architecture exists to prevent.

It is gone. Not deprecated, not guarded - gone. The Spine now REQUESTS mutation and lets
the collapse path decide, exactly as DBE and MSSL do under Ruling 1.

    "Doctrine is not rule. It is the shape left behind by collapse that never fully healed."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.doctrine.codex import Codex
from src.utils.models import Doctrine


@dataclass
class MutationRequest:
    """What the Spine emits instead of a write.

    It travels: DoctrineSpine -> DEE (eligibility) -> CMTE -> SAE (execution) -> Codex.
    The Spine can want a doctrine to change. It cannot make it change.
    """
    doctrine_id: str
    proposed_form: Optional[Doctrine]
    collapse_lineage: str            # scar Δ ID. Empty means the request is inert.
    trigger: str                     # DRPE | Scar Bloom Convergence | PSI Identity Clash | ...
    requested_by: str = "DoctrineSpine"
    requested_at: datetime = field(default_factory=datetime.now)
    reason: str = ""


class DoctrineSpine:
    """The doctrinal skeleton: what holds shape under pressure.

    Holds NO store. Every doctrine it speaks about lives in the Codex.
    """

    def __init__(self, codex: Optional[Codex] = None):
        # Explicit None-check, never `codex or Codex()`: an empty Codex must not be
        # replaced by a fresh private one just because it has nothing in it yet.
        self.codex = codex if codex is not None else Codex()
        self.pending_requests: List[MutationRequest] = []

    # =================================================================
    # READS - free (Ruling 1 governs writes only)
    # =================================================================

    @property
    def doctrines(self) -> Dict[str, Doctrine]:
        """Read-only SNAPSHOT of the Codex store.

        Not the store, and not live objects: editing what comes back here changes
        nothing. There is no append target and no field to quietly overwrite. Callers
        that used to mutate through `spine.doctrines` now change nothing at all, which
        is the correct outcome - doctrine changes by surviving collapse, or not at all.
        """
        return self.codex.view()

    def get_doctrine(self, doctrine_id: str) -> Optional[Doctrine]:
        return self.codex.get(doctrine_id)

    def active(self) -> List[Doctrine]:
        return self.codex.active()

    def by_scar(self, scar_id: str) -> List[Doctrine]:
        """Which doctrines were forged by, or are load-bearing on, this scar."""
        return self.codex.by_scar(scar_id)

    def by_status(self, status: str) -> List[Doctrine]:
        return [d for d in self.codex.view().values() if d.status == status]

    def by_tag(self, tag: str) -> List[Doctrine]:
        return [d for d in self.codex.view().values()
                if tag in getattr(d, "tca_tags", [])]

    # =================================================================
    # STRUCTURE - what the Spine is actually FOR
    # =================================================================

    def anchor_zones(self) -> Dict[str, List[str]]:
        """Doctrine anchor zones inform reflex arbitration (0_Core:65).

        The skeleton reports where it is load-bearing. RACM reads this; the Spine does
        not arbitrate with it.
        """
        zones: Dict[str, List[str]] = {}
        for doctrine in self.codex.view().values():
            for scar_id in doctrine.scar_links:
                zones.setdefault(scar_id, []).append(doctrine.id)
        return zones

    def load_bearing(self, min_scars: int = 3) -> List[Doctrine]:
        """Collapse-resistant doctrines override lower-tier filters (0_Core:152).

        Load-bearing = forged by many scars. Threshold 3 is the corpus's standing
        convergence magnitude (Scar Bloom ≥3), not a new number.
        """
        return [d for d in self.codex.view().values()
                if len(d.scar_links) >= min_scars]

    def integrity_scan(self) -> List[Dict[str, Any]]:
        """Doctrine integrity violations flagged and passed to DRPE (0_Core:219).

        Ossification is the failure mode here: a doctrine that has stopped being tested
        is not strong, it is unexamined. The Spine flags; DRPE re-pressures; SAE executes
        whatever survives.
        """
        flags: List[Dict[str, Any]] = []
        for doctrine in self.codex.view().values():
            if not doctrine.scar_links and not doctrine.is_seed:
                flags.append({
                    "doctrine_id": doctrine.id,
                    "violation": "no scar lineage",
                    "route_to": "DRPE",
                    "detail": "doctrine with no collapse behind it - assertion, not survived truth",
                })
            if doctrine.status == "active" and doctrine.last_mutated is None \
                    and not doctrine.is_seed and len(doctrine.mutation_lineage) == 0:
                flags.append({
                    "doctrine_id": doctrine.id,
                    "violation": "never re-pressured",
                    "route_to": "DRPE",
                    "detail": "ossification risk - doctrine has never been re-tested",
                })
        return flags

    # =================================================================
    # REQUESTS - the Spine's only outbound authority
    # =================================================================

    def request_mutation(self, doctrine_id: str, proposed_form: Optional[Doctrine],
                         collapse_lineage: str, trigger: str,
                         reason: str = "") -> MutationRequest:
        """Emit a request. Does NOT mutate anything.

        The request goes to DEE for eligibility and to SAE for execution. If the
        contradiction it rests on was never actually survived, it dies at the gate -
        which is the correct outcome, not a failure of this method.
        """
        request = MutationRequest(
            doctrine_id=doctrine_id,
            proposed_form=proposed_form,
            collapse_lineage=collapse_lineage,
            trigger=trigger,
            reason=reason,
        )
        self.pending_requests.append(request)
        return request

    def drain_requests(self) -> List[MutationRequest]:
        """DEE pulls pending requests. Bounded by construction - the list is emptied."""
        requests, self.pending_requests = self.pending_requests, []
        return requests

    # =================================================================
    # PERSISTENCE - delegated. The Spine does not own the file either.
    # =================================================================

    def save_to_file(self) -> None:
        self.codex.save_to_file()

    def load_from_file(self) -> None:
        self.codex.load_from_file()
