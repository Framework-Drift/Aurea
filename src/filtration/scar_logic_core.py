"""
scar_logic_core.py - Scar Logic Core for Aurea
Handles storage, access, and management of Scar objects.
"""

import json
from src.utils.models import Scar
from typing import List, Optional
from datetime import datetime
from pathlib import Path

class ScarLogicCore:
    """
    Scar Logic Core: Handles all scar memory management.
    """
    def __init__(self, filepath: str = "data/scars.json"):
        self.filepath = Path(filepath)
        self.scars: List[Scar] = []
        self.load_from_file()  # Load at startup

    def add_scar(self, scar: Scar) -> None:
        """
        Add a new scar to memory (DO NOT auto-save here).
        """
        self.scars.append(scar)

    def get_active_scars(self) -> List[Scar]:
        """
        Return all active scars.
        """
        return [scar for scar in self.scars if scar.decay_state == "active"]

    def get_scar(self, scar_id: str) -> Optional[Scar]:
        """
        Retrieve a scar by ID.
        """
        for scar in self.scars:
            if scar.id == scar_id:
                return scar
        return None

    def decay_scar(self, scar_id: str) -> bool:
        """
        Mark a scar as decayed/retired.
        Returns True if decayed, False if not found.
        """
        scar = self.get_scar(scar_id)
        if scar:
            scar.decay_state = "retired"
            self.save_to_file()
            return True
        return False

    def save_to_file(self) -> None:
        """
        Save all scars to disk as JSON.
        """
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([self._scar_to_dict(s) for s in self.scars], f, default=str, indent=2)

    def load_from_file(self) -> None:
        """
        Load all scars from disk, if file exists.
        """
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
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
