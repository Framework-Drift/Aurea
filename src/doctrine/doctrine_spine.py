"""
doctrine_spine.py - Doctrine Spine for Aurea
Stores, retrieves, and mutates doctrines, tracking scar links.
"""

import json
from src.utils.models import Doctrine
from typing import List, Optional
from datetime import datetime
from pathlib import Path

class DoctrineSpine:
    """
    Doctrine Spine: Manages doctrine objects and lineage.
    """
    def __init__(self, filepath: str = "data/doctrines.json"):
        self.filepath = Path(filepath)
        self.doctrines: List[Doctrine] = []
        self.load_from_file()  # Load at startup

    def add_doctrine(self, doctrine: Doctrine) -> None:
        """
        Add a new doctrine to memory (DO NOT auto-save here).
        """
        self.doctrines.append(doctrine)

    def get_doctrine(self, doctrine_id: str) -> Optional[Doctrine]:
        """
        Retrieve a doctrine by ID.
        """
        for doctrine in self.doctrines:
            if doctrine.id == doctrine_id:
                return doctrine
        return None

    def link_scar(self, doctrine_id: str, scar_id: str) -> bool:
        """
        Link a scar to a doctrine by ID and save.
        """
        doctrine = self.get_doctrine(doctrine_id)
        if doctrine and scar_id not in doctrine.scar_links:
            doctrine.scar_links.append(scar_id)
            self.save_to_file()
            return True
        return False

    def mutate_doctrine(self, doctrine_id: str, new_name: str) -> bool:
        """
        Mutate (rename) a doctrine, updating its mutation lineage.
        """
        doctrine = self.get_doctrine(doctrine_id)
        if doctrine:
            doctrine.mutation_lineage.append(doctrine.name)
            doctrine.name = new_name
            doctrine.last_mutated = datetime.now()
            self.save_to_file()
            return True
        return False

    def save_to_file(self) -> None:
        """
        Save all doctrines to disk as JSON.
        """
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([self._doctrine_to_dict(d) for d in self.doctrines], f, default=str, indent=2)

    def load_from_file(self) -> None:
        """
        Load all doctrines from disk, if file exists.
        """
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                docs_data = json.load(f)
                self.doctrines = [Doctrine(**self._dict_to_doctrinedata(data)) for data in docs_data]

    def _doctrine_to_dict(self, doctrine: Doctrine) -> dict:
        d = doctrine.__dict__.copy()
        d["created_at"] = str(d["created_at"])
        if d.get("last_mutated"):
            d["last_mutated"] = str(d["last_mutated"])
        # Ensure new fields are always present
        d.setdefault("description", "")
        d.setdefault("tca_tags", [])
        d.setdefault("is_seed", False)
        return d

    def _dict_to_doctrinedata(self, d: dict) -> dict:
        d = d.copy()
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        if d.get("last_mutated"):
            d["last_mutated"] = datetime.fromisoformat(d["last_mutated"])
        # Patch for missing new fields
        d.setdefault("description", "")
        d.setdefault("tca_tags", [])
        d.setdefault("is_seed", False)
        return d

    def create_doctrine(self, scar, name) -> Doctrine:
        doctrine = Doctrine(
            id=f"Doctrine-{scar.id}",
            name=name,
            mutation_lineage=[],
            scar_links=[scar.id],
            status="active",
            created_at=datetime.now(),
            last_mutated=None
        )
        self.doctrines.append(doctrine)
        # Only call self.save_to_file() during normal runtime, NOT seeding
        return doctrine


     