"""
scar_logic_core.py - Scar Logic Core for Aurea
Handles storage, access, and management of Scar objects.
"""

import copy
import json
from src.utils.models import Scar
from typing import List, Optional
from datetime import datetime
from pathlib import Path

class ScarLogicCore:
    """
    Scar Logic Core: Handles all scar memory management.
    """
    # RULING 32 (2026-07-26): THE SEED IS READ-ONLY INPUT.
    # `data/scars.json` is TRACKED and holds D17 "Compassion Weaponization"
    # (weight 84) among AUREA's founding scars. `save_to_file` writes mode "w",
    # so a default-constructed ScarLogicCore that saved OVERWROTE the founding
    # scars wholesale - IDENTITY REPLACEMENT, not the additive pollution
    # Ruling 31 closed. Scars are the most permanent records in this system
    # (Ruling 22); a permanence protected only by nobody happening to call
    # save is not permanence. The seed now has NO WRITER at all.
    #     load -> runtime if present, ELSE seed;  save -> always runtime.
    SEED_PATH = "data/scars.json"                 # TRACKED, READ-ONLY
    RUNTIME_PATH = "data/runtime/scars.json"      # untracked, sole write target

    def __init__(self, filepath: Optional[str] = None,
                 seed_path: Optional[str] = None,
                 runtime_path: Optional[str] = None):
        # `filepath` = explicit single-path isolation (tests). The pipeline
        # calls ScarLogicCore(), reading the seed and writing only runtime.
        if filepath is not None:
            self.seed_path = self.runtime_path = Path(filepath)
        else:
            self.seed_path = Path(seed_path or self.SEED_PATH)
            self.runtime_path = Path(runtime_path or self.RUNTIME_PATH)
        self.scars: List[Scar] = []
        self.load_from_file()  # Load at startup

    def add_scar(self, scar: Scar) -> None:
        """
        Add a new scar to memory (DO NOT auto-save here).
        """
        self.scars.append(scar)

    def form_scar(self, origin: str, type: str = "", weight: float = 0.0,
                  description: str = "", name: Optional[str] = None,
                  linked_doctrines: Optional[List[str]] = None,
                  reflexes: Optional[List[str]] = None,
                  echo_proximity: Optional[List[str]] = None) -> Scar:
        """Execute a scar REQUEST from a collapse-bearing module (Ruling 1).

        SBSRE, ELM, MSSL and the rest do not write the scar store - they ask. This is the
        owner-side execution of that request: the Core mints the ID, constructs the record,
        and files it. One writer, many requesters.

        Without this method the requests were silently DROPPED (callers guard with
        `hasattr(scar_core, "form_scar")`), which is worse than a crash: a collapse that
        left no scar is a contradiction AUREA survived and then forgot.
        """
        scar = Scar(
            id=self._next_scar_id(),
            name=name or (description[:48] if description else origin),
            origin=origin,
            type=type,
            weight=weight,
            description=description,
            linked_doctrines=list(linked_doctrines or []),
            reflexes=list(reflexes or []),
            echo_proximity=list(echo_proximity or []),
        )
        self.add_scar(scar)
        return scar

    def _next_scar_id(self) -> str:
        return f"Scar-\u0394{len(self.scars) + 1}"

    # =================================================================
    # READS - free to every module (Ruling 1 governs writes only)
    #
    # RULING 22 (2026-07-25): reads return DEEP COPIES, not the stored
    # objects. The Codex solved this exact problem with `_snapshot()`; the
    # scar store never received the treatment, so until now the doctrine
    # store had an ownership BOUNDARY while the scar store had only a
    # CONVENTION. A caller could set `.weight`, clear `.linked_doctrines`, or
    # flip `.decay_state` with no owner-controlled operation - and the AST
    # single-writer invariant CANNOT see it, because nothing assigns to
    # `scar_core.scars`. Scars are the most permanent records in the system,
    # and a permanence enforced only by everyone remembering not to touch it
    # is not permanence. Weight and decay belong to SML (Ruling 1); changing
    # what a scar IS goes through its owner, not through a read.
    # =================================================================

    @staticmethod
    def _snapshot(scar: Optional[Scar]) -> Optional[Scar]:
        return copy.deepcopy(scar) if scar is not None else None

    def _find(self, scar_id: str) -> Optional[Scar]:
        """THE LIVE record, for the owner's OWN write paths only.

        Deliberately private and deliberately separate from `get_scar`: the
        public accessor snapshots, so an owner-side method that resolved its
        target through it would mutate a copy and its write would vanish
        SILENTLY - a fail-silent regression, the worst possible outcome of
        Ruling 22. `decay_scar` used to do exactly that. Do not call this
        from outside this class; emit a request instead (Ruling 1).
        """
        for scar in self.scars:
            if scar.id == scar_id:
                return scar
        return None

    def get_active_scars(self) -> List[Scar]:
        """
        Return all active scars, as SNAPSHOTS (Ruling 22).
        """
        return [self._snapshot(scar) for scar in self.scars
                if scar.decay_state == "active"]

    def get_scar(self, scar_id: str) -> Optional[Scar]:
        """
        Retrieve a scar by ID, as a SNAPSHOT (Ruling 22). Reading what is true
        is free; changing it goes through this class.
        """
        return self._snapshot(self._find(scar_id))

    def decay_scar(self, scar_id: str) -> bool:
        """
        Mark a scar as decayed/retired.
        Returns True if decayed, False if not found.
        """
        scar = self._find(scar_id)      # Ruling 22: the owner writes the RECORD
        if scar:
            scar.decay_state = "retired"
            self.save_to_file()
            return True
        return False

    def save_to_file(self) -> None:
        """
        Save all scars to disk as JSON.

        Ruling 32: the RUNTIME path, never the seed.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            json.dump([self._scar_to_dict(s) for s in self.scars], f, default=str, indent=2)

    def load_from_file(self) -> None:
        """
        Load scars from disk: runtime state if present, ELSE the seed (Ruling 32).
        """
        source = (self.runtime_path if self.runtime_path.exists()
                  else self.seed_path)
        if source.exists():
            with open(source, "r", encoding="utf-8") as f:
                scars_data = json.load(f)
                self.scars = [Scar(**self._dict_to_scardata(data)) for data in scars_data]

    def _scar_to_dict(self, scar: Scar) -> dict:
        d = scar.__dict__.copy()
        d["created_at"] = str(d["created_at"])
        if d.get("last_accessed"):
            d["last_accessed"] = str(d["last_accessed"])
        d.setdefault("description", "")
        d.setdefault("echo_proximity", [])
        d.setdefault("reflexes", [])
        d.setdefault("tca_tags", [])
        d.setdefault("is_seed", False)
        return d

    def _dict_to_scardata(self, d: dict) -> dict:
        d = d.copy()
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        if d.get("last_accessed"):
            d["last_accessed"] = datetime.fromisoformat(d["last_accessed"])
        d.setdefault("description", "")
        d.setdefault("echo_proximity", [])
        d.setdefault("reflexes", [])
        d.setdefault("tca_tags", [])
        d.setdefault("is_seed", False)
        return d
