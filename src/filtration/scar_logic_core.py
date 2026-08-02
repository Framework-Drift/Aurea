"""
scar_logic_core.py - Scar Logic Core for Aurea
Handles storage, access, and management of Scar objects.
"""

import copy
import json
# Ruling 37 (2): the canon decay vocabulary lives with its OWNER (SML). This
# module reads it rather than re-declaring the strings - a second copy of a
# closed vocabulary is a second definition free to drift from the first.
# `scar_management` imports only `src.utils.models`, so there is no cycle.
from src.filtration.scar_management import LIVE_STATES, DecayState, normalize
from src.utils.atomic_write import atomic_write_json
from src.utils.models import Scar
from typing import Any, List, Optional
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
        Return all LIVE scars, as SNAPSHOTS (Ruling 22).

        RULING 43 - AND THIS IS THE CHANGE THAT NEEDED THE MOST CARE IN THAT
        PASS, because it is the one Ruling 37 left a standing requirement about:
        a decay-vocabulary migration must not silently change which scars this
        returns. Three consumers depend on it - EchoNet's resonance net, EchoNet's
        dynamic threshold, and the compass SOUTH anchor.

        The filter reads `LIVE_STATES`, not `is ACTIVE`, and the difference is
        exactly `LOCKED`. Once `normalize()` stopped mis-reading the seed's
        literals as ACTIVE, a bare `is ACTIVE` test would have dropped BOTH
        `Scar-0` (weight 100, the heaviest record she has) and `Δ91` (weight 99)
        out of this set - stripping 199 of 835 SOUTH bearing mass and removing
        The Origin Collapse from her resonance substrate, as a side effect of a
        fix aimed at the decay schedule. That is precisely the silent, load-
        bearing consequence Ruling 37's requirement exists to catch.

        SO THE TWO RECORDS ARE TREATED DIFFERENTLY, ON PURPOSE, EACH WITH A
        CITED AUTHORITY:
          * `Scar-0` is LOCKED and STAYS. Ruling 35 already ruled what `locked`
            means here - LIVE and readable, excluded from the change machinery
            only. It resonates and carries bearing exactly as it did yesterday.
          * `Δ91` is FOSSILIZED and LEAVES, and that is the one intended
            behavioral change of the pass. A fossil has matured out of live
            crisis: `autonomy_index` has grouped `"fossil"` with
            `"retired"`/`"dormant"` since before SML existed, and Ruling 37
            pinned the principle in terms - "cooling is exactly what 'stops
            exerting live resonance' means." It is a DECISION ON THE RECORD, in
            the same form Ruling 37 recorded WANING's departure, and it is
            pinned.
        """
        return [self._snapshot(scar) for scar in self.scars
                if normalize(scar.decay_state) in LIVE_STATES]

    def all_scars(self) -> List[Scar]:
        """EVERY scar in the store, in ANY decay state, as SNAPSHOTS (Ruling 22).

        RULING 54 (2026-07-31). Added because lineage and bearing are DIFFERENT
        QUESTIONS and only one of them had a reader.

            `get_active_scars` answers "what still exerts pressure" - bearing,
            filtered by `LIVE_STATES`, and it is UNTOUCHED.
            This answers "what is on record as having happened" - history.

        Canon draws the line itself: DORMANT "no longer influences output or
        filtration directly, BUT REMAINS PRESERVED... may be recalled during
        doctrine mutation, identity recursion" (2b:916), and FOSSILIZED is "part
        of symbolic lineage" (2b:921). A cooled scar stops PUSHING; it does not
        stop having HAPPENED.

        Without this reader, EchoNet's Stage 3 confirmed a doctrine's scarline
        against the LIVE set, so a scar that merely cooled was reported as an
        unverified reference and AUREA's expressed grounding eroded as a function
        of CALM - weakening precisely because nothing had disturbed her.

        SNAPSHOTS, like every other read here. A bulk reader handing out live
        records would be a write path into the most permanent store in the system
        and the AST single-writer scan could not see it (Ruling 22's finding).
        Owner-side writes resolve through `_find`, never through this.
        """
        return [self._snapshot(scar) for scar in self.scars]

    def get_scar(self, scar_id: str) -> Optional[Scar]:
        """
        Retrieve a scar by ID, as a SNAPSHOT (Ruling 22). Reading what is true
        is free; changing it goes through this class.
        """
        return self._snapshot(self._find(scar_id))

    def seed_scars_tagged(self, tag: str) -> List[Scar]:
        """SEED records carrying a TCA tag, as SNAPSHOTS (Ruling 22).

        Added for Ruling 42 res.3: RIL must resolve AUREA's CONSTITUTIONAL ORIGIN
        without opening `data/scars.json` itself. Ruling 1 governs writes, and
        reads are free - but a reader that opens the owner's FILE has taken a
        second view of the owner's state, which is how two definitions of one
        store begin. So the owner answers the question.

        `is_seed` is part of the filter, not a caller's problem: a scar formed at
        RUNTIME and tagged the same way is a runtime fact, and the constitution
        is what she was born with.
        """
        return [self._snapshot(scar) for scar in self.scars
                if scar.is_seed and tag in (scar.tca_tags or [])]

    def attach_decay_owner(self, sml: Any) -> None:
        """Bind THE decay owner (Ruling 40). `AureaCore` calls this so the
        pipeline's single SML - the one holding the quiet-cycle counters and the
        handle to SAE - is also the one that executes a manual retire. Without
        it, `decay_scar` would build a private SML and the two would keep
        separate books on the same records."""
        self._sml = sml

    def _decay_owner(self) -> Any:
        """The bound SML, or a private one bound to this store.

        The lazy branch exists for the bare `ScarLogicCore(...)` a test builds.
        It is NOT a second owner of the FIELD - `SML` is still the only class
        that assigns `decay_state`, which is what the Ruling 1 scanner checks -
        it is a second bookkeeper, which is why `AureaCore` attaches the real one.
        """
        if getattr(self, "_sml", None) is None:
            from src.filtration.scar_management import SML
            self._sml = SML(scar_core=self)
        return self._sml

    def decay_scar(self, scar_id: str) -> bool:
        """
        Mark a scar as decayed. Returns True if decayed, False if not found.

        RULING 37 (2): the bare `"retired"` literal this wrote is GONE - it maps
        into the canon vocabulary as `DecayState.DORMANT` rather than surviving
        as a fifth state outside it. `autonomy_index` already grouped the two
        together, so nothing downstream changed meaning.

        RULING 40 (2026-07-27) - THE FLAG THIS DOCSTRING CARRIED IS DISCHARGED.
        It read: "this is the ONE remaining writer of `decay_state` outside SML
        ... Two writers of one field is exactly what Ruling 1 exists to prevent,
        and consolidating them is a small ruling rather than an implementation
        choice ... Reported, not repaired." That ruling arrived; this is the
        repair.

        THE PUBLIC SURFACE IS UNCHANGED - same name, same argument, same
        True/False contract - and the WRITE moved to the owner. This store no
        longer assigns `decay_state` anywhere, and an AST pin now asserts that
        `scar_management.py` is the only module in `src/` that does.

        THE CONCERN THE OLD FLAG RAISED WAS REAL AND WAS CHECKED: this method is
        load-bearing for Ruling 22's fail-silent pin, which proves the owner's
        own write path reaches the RECORD and not a snapshot. It still does -
        `SML._record` resolves through `_live_scars()`, the live list, for
        exactly the reason `_find` exists here. The pin was run against this
        change and is BYTE-IDENTICAL.
        """
        return self._decay_owner().manual_retire(scar_id)

    def save_to_file(self) -> None:
        """
        Save all scars to disk as JSON.

        Ruling 32: the RUNTIME path, never the seed.
        """
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        # Rider R3 (2026-07-29): ATOMIC. Scars are the most permanent records in
        # the system (Ruling 22), and SML calls this on every decay transition -
        # the most frequent snapshot write in the tree, against the store least
        # able to afford a truncation.
        atomic_write_json(self.runtime_path,
                          [self._scar_to_dict(s) for s in self.scars],
                          indent=2)

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
