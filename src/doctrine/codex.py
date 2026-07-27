"""
codex.py - The Codex: canonical archive of collapse-survived truth.

Canon: 3b "MODULE: Doctrine Spine + Codex - v2.0"; Lexicon III.1; Dependency Map §7
  ("Doctrine Spine (including Codex, DEE, Harmonizer, DML, DPA)")

    "Doctrine is not rule. It is the shape left behind by collapse that never fully healed."

OWNERSHIP (Ruling 1 - one writer per store; Ruling 5 - doctrine ownership, 2026-07-11)
--------------------------------------------------------------------------------------
The Codex OWNS the doctrine store. It is the only module that may mutate `self.doctrines`.

But owning the store is not the same as authoring its contents. **SAE is the sole
EXECUTOR of doctrine mutation.** The Codex does not decide what a doctrine becomes;
it refuses to record anything that did not survive collapse.

    Doctrine Spine  -> the structural layer (skeleton). Reads. Requests. Never writes.
    DEE             -> eligibility gate. Never writes.
    DBE             -> detector/validator. Never writes.
    MSSL            -> external merge requester. Never writes.
    SAE             -> executor. The ONLY holder of a valid write.

WHY THE GUARD EXISTS
--------------------
Doctrine is identity. A doctrine edited in place - renamed, re-scoped, quietly
improved - is an identity that changed without surviving anything, leaving no scar,
no lineage, no fossil of what it used to be. That is not a bug in a store; it is the
exact failure the whole architecture exists to prevent.

So the wrong path is not discouraged here. It is UNEXECUTABLE. Every write demands a
single-use MutationAuthorization minted by SAE and carrying collapse lineage (AVT.017:
no mutation without traceable collapse lineage). There is no unguarded setter to reach
for when a caller is in a hurry.
"""

from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.models import Doctrine


class CodexWriteViolation(Exception):
    """Raised when something tries to write doctrine without surviving collapse.

    This is not a validation error to be caught and worked around. It means a caller
    attempted to change AUREA's identity outside the collapse path.
    """


@dataclass(frozen=True)
class MutationAuthorization:
    """A single-use write token. MINTED ONLY BY SAE.

    Frozen and consumed on use: it cannot be edited after issue, and it cannot be
    replayed to slip a second write past the Self-Mutation Ceiling.
    """
    authorization_id: str
    executor: str                 # must be "SAE" - no other executor exists
    mutation_class: str           # mutate_doctrine | mutate_reflex | module_generation
    collapse_lineage: str         # Scar-Δ### / CAE-### - AVT.017. Never empty.
    cae_id: Optional[str] = None  # append-only audit entry (3a: no mutation without one)
    epoch: int = 0
    issued_at: datetime = field(default_factory=datetime.now)


class Codex:
    """Stores all active, mutated, and ⊗ (fallen) doctrines with reflex metadata."""

    EXECUTOR = "SAE"

    # =================================================================
    # RULING 32 (2026-07-26): THE SEED IS READ-ONLY INPUT.
    # =================================================================
    # `data/doctrines.json` is AUREA's founding doctrine - Doctrine-0.1
    # "Fracture Carried" (scar links D42/D88/D31), created 2025-06-21, TRACKED.
    # Until this split, ONE `filepath` did two incompatible jobs: it was both
    # the seed that is read at construction AND the target of `save_to_file`,
    # which writes with mode "w". A default-constructed Codex that saved
    # therefore OVERWROTE the founding doctrine with whatever was in memory.
    #
    # That is not Ruling 31's hazard. R31 closed APPEND-mode logs where
    # pollution ADDS junk entries; this is a WHOLE-FILE OVERWRITE of an
    # identity store - not false pressure, IDENTITY REPLACEMENT.
    #
    # Nothing prevented it except that no test happened to do it. That is
    # CONVENTION, and the standing bar is UNEXECUTABILITY. Copy-on-first-run
    # was REJECTED as the remedy: it leaves the seed live in the write path and
    # guards it with a conditional. This guards it by HAVING NO WRITER - the
    # seed path is never passed to a write call at all.
    #
    # MINIMAL SEMANTICS, and deliberately nothing more (no layering, no delta
    # format, no merge rule - anything richer is a separate ruling):
    #     load  -> runtime file if present, ELSE seed
    #     save  -> always a full snapshot to runtime
    SEED_PATH = "data/doctrines.json"                # TRACKED, READ-ONLY
    RUNTIME_PATH = "data/runtime/doctrines.json"     # untracked, sole write target

    def __init__(self, filepath: Optional[str] = None,
                 seed_path: Optional[str] = None,
                 runtime_path: Optional[str] = None):
        # `filepath` is the EXPLICIT SINGLE-PATH form: seed and runtime collapse
        # onto one file. It is how a test builds a fully isolated store, and it
        # is deliberately NOT how the pipeline constructs one - `aurea_core`
        # calls `Codex()`, which reads the real seed and writes only runtime.
        if filepath is not None:
            self.seed_path = self.runtime_path = Path(filepath)
        else:
            self.seed_path = Path(seed_path or self.SEED_PATH)
            self.runtime_path = Path(runtime_path or self.RUNTIME_PATH)
        self.doctrines: Dict[str, Doctrine] = {}      # THE STORE. Sole writer: this class.
        self.fossils: Dict[str, Doctrine] = {}        # Codex Fossil Layer (⊗)
        self._consumed: set = set()                   # spent authorization IDs
        self._genesis_open = True                     # seeding window; closed by seal()
        self.load_from_file()

    # =================================================================
    # GENESIS - the one write that did not survive collapse, because
    # nothing had yet collapsed. Closed permanently once sealed.
    # =================================================================

    def seed(self, doctrine: Doctrine) -> Doctrine:
        """Origin doctrines (Doctrine-0 / AVT lineage). Allowed ONLY before seal()."""
        if not self._genesis_open:
            raise CodexWriteViolation(
                f"Genesis is sealed. '{doctrine.id}' cannot be seeded into a living Codex - "
                f"it must survive collapse and be committed by {self.EXECUTOR}."
            )
        if not doctrine.is_seed:
            raise CodexWriteViolation(
                f"'{doctrine.id}' is not marked is_seed. Only origin doctrine may be seeded."
            )
        self.doctrines[doctrine.id] = doctrine
        return doctrine

    def seal(self) -> None:
        """Close the genesis window. After this, the collapse path is the only path in."""
        self._genesis_open = False

    # =================================================================
    # THE ONLY WRITE PATH
    # =================================================================

    def commit(self, doctrine: Doctrine, auth: MutationAuthorization) -> Doctrine:
        """Record a doctrine that survived collapse. SAE-authorized only.

        Handles both birth (a scar cluster becoming doctrine) and mutation (a doctrine
        re-formed under re-pressure). The Codex records; it does not evaluate.
        """
        self._validate(auth)
        # RULING 18 (2026-07-25): a ⊗-fossilized id cannot be silently re-committed.
        # Docket K proved by execution that before this guard, birth_doctrine/commit
        # would revive a fallen doctrine with no re-collapse check, leaving it ACTIVE
        # and FOSSIL simultaneously - an identity that came back from the dead with
        # nothing survived behind it. FAIL-CLOSED and REVERSIBLE: if revival is later
        # ruled permissible, this guard WIDENS to admit an explicitly-classed
        # authorization - it does not get deleted. Do NOT "fix" a collision here by
        # removing the fossil: fossils are archived, never deleted.
        # RULED - Option B (Ruling 19, 2026-07-25). The question Ruling 18 left open
        # is CLOSED: this guard is PERMANENT, not interim. A doctrine that resembles
        # a fossil is born through the ORDINARY birth path under a NEW id, carrying
        # the fallen id in its existing `mutation_lineage` - no revival API, no new
        # field, no bypass. Revival is just birth with an extra ancestry entry. The
        # fallen id itself stays permanently dead here. (Option C - the old id
        # returning through the full mutation path - was refused because it would
        # make "came back" and "never fell" indistinguishable from outside the
        # lineage graph, the exact ambiguity this guard exists to prevent.)
        if doctrine.id in self.fossils:
            raise CodexWriteViolation(
                f"'{doctrine.id}' is ⊗-fossilized (Ruling 18). A fallen doctrine "
                f"does not return to active status by being committed over - the "
                f"fallen id is permanently dead (Ruling 19, Option B). If this "
                f"mutation is legitimate, it mints a NEW id carrying lineage; "
                f"it does not wear a dead doctrine's name."
            )
        self.doctrines[doctrine.id] = doctrine
        self._consumed.add(auth.authorization_id)
        return doctrine

    def fossilize(self, doctrine_id: str, auth: MutationAuthorization,
                  reason: str) -> Optional[Doctrine]:
        """⊗ - mark a doctrine fallen and move it to the Fossil Layer.

        The fallen version is ARCHIVED, never deleted: it keeps its scar trace and the
        reason it collapsed. A fallen doctrine's id CANNOT be re-committed at all -
        commit() refuses it outright (Ruling 18, 2026-07-25), permanently (Ruling 19,
        Option B). A doctrine that resembles a fossil is BORN under a new id carrying
        the fallen id in `mutation_lineage`; there is no revival API and no
        un-fossilize path, and SAE's Ruling-24 pre-flight refuses a successor that
        would take a fossilized id before the ancestor is even touched. This
        docstring once claimed a "fully re-collapsed and mutation-audited" protection
        while the code had none (the Docket E shape, fifth instance, first inside a
        store-write path). What the code enforces today is stated above and nothing more.

        ECI routes foreign-collapse fossilization through this same API (T2-01).
        """
        self._validate(auth)
        doctrine = self.doctrines.get(doctrine_id)
        if doctrine is None:
            self._consumed.add(auth.authorization_id)
            return None

        doctrine.status = "fallen"
        doctrine.description = (doctrine.description + f" [⊗ {reason}]").strip()
        doctrine.last_mutated = datetime.now()

        self.fossils[doctrine_id] = doctrine
        del self.doctrines[doctrine_id]
        self._consumed.add(auth.authorization_id)
        return doctrine

    def link_scar(self, doctrine_id: str, scar_id: str,
                  auth: MutationAuthorization) -> bool:
        """Scar participation is doctrine content, not annotation. It is a write."""
        self._validate(auth)
        doctrine = self.doctrines.get(doctrine_id)
        self._consumed.add(auth.authorization_id)
        if doctrine and scar_id not in doctrine.scar_links:
            doctrine.scar_links.append(scar_id)
            return True
        return False

    def _validate(self, auth: MutationAuthorization) -> None:
        """The gate. Every failure here is an attempted identity change without collapse."""
        if not isinstance(auth, MutationAuthorization):
            raise CodexWriteViolation(
                "Codex writes require a MutationAuthorization minted by SAE. "
                "There is no unguarded write path - this is Ruling 1, enforced."
            )
        if auth.executor != self.EXECUTOR:
            raise CodexWriteViolation(
                f"'{auth.executor}' is not the doctrine executor. Only {self.EXECUTOR} "
                f"executes doctrine mutation (DEE §IX). Route the request through it."
            )
        if not auth.collapse_lineage:
            raise CodexWriteViolation(
                "AVT.017: no doctrine may be written without traceable collapse lineage. "
                "A doctrine with no scar behind it is an assertion, not a survived truth."
            )
        if auth.authorization_id in self._consumed:
            raise CodexWriteViolation(
                f"Authorization {auth.authorization_id} is spent. Tokens are single-use - "
                f"replaying one would slip a write past the Self-Mutation Ceiling."
            )

    # =================================================================
    # READS - free to every module (Ruling 1 governs writes only)
    #
    # Reads return DEEP COPIES, not the stored objects. Handing out a live Doctrine
    # is handing out a write: `codex.get("D-1").name = "..."` would edit doctrine in
    # place, with no token, no lineage, no fossil - the exact hole this class exists
    # to close, reached through the front door. A reader gets a snapshot of what is
    # true; changing what is true goes through SAE.
    # =================================================================

    @staticmethod
    def _snapshot(doctrine: Optional[Doctrine]) -> Optional[Doctrine]:
        return copy.deepcopy(doctrine) if doctrine is not None else None

    def get(self, doctrine_id: str) -> Optional[Doctrine]:
        return self._snapshot(self.doctrines.get(doctrine_id))

    def get_fossil(self, doctrine_id: str) -> Optional[Doctrine]:
        return self._snapshot(self.fossils.get(doctrine_id))

    def active(self) -> List[Doctrine]:
        return [self._snapshot(d) for d in self.doctrines.values() if d.status == "active"]

    def by_scar(self, scar_id: str) -> List[Doctrine]:
        return [self._snapshot(d) for d in self.doctrines.values() if scar_id in d.scar_links]

    def view(self) -> Dict[str, Doctrine]:
        """Full read-only snapshot of the store. Safe to hand to any module."""
        return {k: self._snapshot(v) for k, v in self.doctrines.items()}

    def lineage(self, doctrine_id: str) -> List[str]:
        """Mutation ancestry: what this doctrine used to be, all the way back."""
        doctrine = self.doctrines.get(doctrine_id) or self.fossils.get(doctrine_id)
        return list(doctrine.mutation_lineage) if doctrine else []

    def __len__(self) -> int:
        return len(self.doctrines)

    def __bool__(self) -> bool:
        """An EMPTY Codex is still a Codex.

        Without this, `__len__` makes a fresh Codex falsy, and any caller writing
        `codex or Codex()` silently builds a SECOND, private store - a doctrine store
        nobody writes to, read by modules that think they are reading the real one.
        Caught in sandbox 2026-07-11 before it shipped. Do not remove.
        """
        return True

    def __contains__(self, doctrine_id: str) -> bool:
        return doctrine_id in self.doctrines

    # =================================================================
    # PERSISTENCE
    # =================================================================

    def save_to_file(self) -> None:
        """Full snapshot to the RUNTIME path. Ruling 32: never the seed."""
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "active": [self._to_dict(d) for d in self.doctrines.values()],
            "fossils": [self._to_dict(d) for d in self.fossils.values()],
        }
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, default=str, indent=2)

    def load_from_file(self) -> None:
        """Runtime state if it exists, ELSE the seed (Ruling 32)."""
        source = (self.runtime_path if self.runtime_path.exists()
                  else self.seed_path)
        if not source.exists():
            return
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Tolerate the legacy flat-list format written by the old DoctrineSpine.
        #
        # RULING 35 (2026-07-27): THE FLAT BRANCH ROUTES BY STATUS. It read
        # `active, fossils = data, []`, and the tracked seed IS a flat list of
        # eight carrying `⊗ Doctrine-0` (status "fallen") and `Doctrine-0`
        # (status "locked"). So the founding fossil loaded LIVE and `fossils`
        # loaded EMPTY - on every construction, in production and in every test.
        #
        # THE CONSEQUENCE THAT MAKES THIS A RULING RATHER THAN A TIDY-UP:
        # `commit()`'s Ruling-18 guard below asks `if doctrine.id in
        # self.fossils`. Against an empty fossil map it can never fire, so a
        # commit over `⊗ Doctrine-0` did NOT raise. Ruling 18 was structurally
        # VACUOUS against the actual seed - it protected doctrines felled at
        # runtime and never once protected the founding fossil it was written
        # about. Pinned now by tests/test_ruling35.py, watched RED here first.
        #
        # No status vocabulary is invented and the seed is NOT migrated: it is
        # read-only input (Ruling 32) with no writer, and the whole fix lives in
        # how it is READ. The nested branch already routes by construction.
        if isinstance(data, list):
            active = [d for d in data if d.get("status") != "fallen"]
            fossils = [d for d in data if d.get("status") == "fallen"]
        else:
            active, fossils = data.get("active", []), data.get("fossils", [])

        self.doctrines = {d["id"]: Doctrine(**self._from_dict(d)) for d in active}
        self.fossils = {d["id"]: Doctrine(**self._from_dict(d)) for d in fossils}
        if self.doctrines:
            self._genesis_open = False   # a Codex with contents is already living

    @staticmethod
    def _to_dict(doctrine: Doctrine) -> dict:
        d = doctrine.__dict__.copy()
        d["created_at"] = str(d["created_at"])
        if d.get("last_mutated"):
            d["last_mutated"] = str(d["last_mutated"])
        return d

    @staticmethod
    def _from_dict(d: dict) -> dict:
        d = d.copy()
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        if isinstance(d.get("last_mutated"), str):
            d["last_mutated"] = datetime.fromisoformat(d["last_mutated"])
        d.setdefault("description", "")
        d.setdefault("tca_tags", [])
        d.setdefault("is_seed", False)
        return d


def new_authorization_id() -> str:
    return f"AUTH-{uuid.uuid4().hex[:12]}"
