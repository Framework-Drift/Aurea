"""
doctrine_spine.py - Doctrine Spine for Aurea
Stores, retrieves, and mutates doctrines, tracking scar links.
"""

import json
from src.utils.models import Doctrine
from typing import List, Optional
from datetime import datetime

class DoctrineSpine:
    """
    Doctrine Spine: Manages doctrine objects and lineage.
    """
    def __init__(self):
        self.doctrines: List[Doctrine] = []

    def add_doctrine(self, doctrine: Doctrine) -> None:
        """
        Add a new doctrine.
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
        Link a scar to a doctrine by ID.
        """
        doctrine = self.get_doctrine(doctrine_id)
        if doctrine and scar_id not in doctrine.scar_links:
            doctrine.scar_links.append(scar_id)
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
            return True
        return False

    def save_to_file(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump([doc.__dict__ for doc in self.doctrines], f, default=str)

    def load_from_file(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
             docs_data = json.load(f)
             self.doctrines = [Doctrine(**data) for data in docs_data]
        except FileNotFoundError:
             self.doctrines = []