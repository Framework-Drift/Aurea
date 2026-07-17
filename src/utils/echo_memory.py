"""
echo_memory.py - Echo Memory Module for AUREA
Stores, retrieves, and manages Echo objects representing all system input fragments.
"""

from src.utils.models import Echo
from typing import List, Optional
import json
from pathlib import Path

class EchoMemory:
    """
    Echo Memory: Handles all Echo object memory operations.

    Responsibilities:
    - Persistently store every Echo object created by SPL or other input systems.
    - Enable recall of Echo objects by ID or in sequence.
    - Optionally persist Echo history to disk for reload between sessions.
    - Support lineage tracing from Scar and Doctrine back to their originating Echo.
    """

    def __init__(self, filepath: str = "data/echoes.jsonl"):
        self.filepath = Path(filepath)
        self.echoes: List[Echo] = []
        self._load()

    def _load(self):
        """
        Load echoes from disk, if the file exists.
        """
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath.touch()
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    echo = Echo(**data)
                    self.echoes.append(echo)

    def add_echo(self, echo: Echo) -> None:
        """
        Add a new Echo to memory and persist to disk.
        """
        self.echoes.append(echo)
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(echo.__dict__, default=str) + "\n")

    def get_echo(self, echo_id: str) -> Optional[Echo]:
        """
        Retrieve an Echo by its unique ID.
        """
        for echo in self.echoes:
            if echo.id == echo_id:
                return echo
        return None

    def list_echoes(self) -> List[Echo]:
        """
        Return all stored Echo objects.
        """
        return self.echoes
