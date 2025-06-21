"""
scar_logic_core.py - Scar Logic Core for Aurea
Handles storage, access, and management of Scar objects.
"""

from src.utils.models import Scar
from typing import List, Optional

class ScarLogicCore:
    """
    Scar Logic Core: Handles all scar memory management.
    """
    def __init__(self):
        self.scars: List[Scar] = []

    def add_scar(self, scar: Scar) -> None:
        """
        Add a new scar to memory.
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
            return True
        return False
