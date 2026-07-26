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

    # RULING 32 (2026-07-26): THE SEED IS READ-ONLY INPUT.
    # `data/echoes.jsonl` is TRACKED. This store APPENDS rather than
    # overwriting, so it is Ruling 31's hazard shape rather than Codex's - but
    # it sits on a tracked path with no redirect, so every run wrote echoes
    # into version control. `_load` also TOUCHED the file into existence, which
    # is a write in its own right and one nobody would look for in a loader.
    #     load -> runtime if present, ELSE seed;  append -> always runtime.
    SEED_PATH = "data/echoes.jsonl"                # TRACKED, READ-ONLY
    RUNTIME_PATH = "data/runtime/echoes.jsonl"     # untracked, sole write target

    def __init__(self, filepath: Optional[str] = None,
                 seed_path: Optional[str] = None,
                 runtime_path: Optional[str] = None):
        # `filepath` = explicit single-path isolation (tests).
        if filepath is not None:
            self.seed_path = self.runtime_path = Path(filepath)
        else:
            self.seed_path = Path(seed_path or self.SEED_PATH)
            self.runtime_path = Path(runtime_path or self.RUNTIME_PATH)
        self.echoes: List[Echo] = []
        self._load()

    def _load(self):
        """
        Load echoes: runtime history if present, ELSE the seed (Ruling 32).

        Deliberately does NOT touch the seed into existence. A loader that
        creates its source is a writer wearing a reader's name, and the seed
        has no writer.
        """
        source = (self.runtime_path if self.runtime_path.exists()
                  else self.seed_path)
        if not source.exists():
            return
        with open(source, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    echo = Echo(**data)
                    self.echoes.append(echo)

    def add_echo(self, echo: Echo) -> None:
        """
        Add a new Echo to memory and persist to disk.

        Ruling 32: appends to the RUNTIME path, never the seed.
        """
        self.echoes.append(echo)
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.runtime_path, "a", encoding="utf-8") as f:
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
