"""
echo_memory.py - RULING 75 (2026-08-05): THE ECHO BECOMES A RECORD.

    An echo that persists nowhere is not a memory of perception; it is a
    shape the pipeline held for one pass.

THE FIVE PRESSURES THIS FILE CARRIED, and what each becomes
-------------------------------------------------------------------------------
For as long as this module has existed it was CANONICAL AND UNWIRED - "complete
input lineage" in its own docstring, constructed by nothing in the pipeline.
Five separate rulings each hit the same seam and each deferred to the wiring
ruling that is now this one:

  * RULING 65 res.4 excluded echoes from the topology rebuild, because **an Echo
    record persists NOWHERE** - so a restored echo node would assert a holding
    no store holds. That reopening condition is FIRED: echoes are the FOURTH
    SOURCE, and `aurea_core`'s rebuild sequence places them.
  * BATCH 66 declared `default=str` here its ONE load-bearing exemption in all
    of `src/`, RESERVED to this ruling because removing it means CHOOSING the
    echo's serialized form. That schema decision is made below and the exemption
    is DISCHARGED - `default=` is gone.
  * RULING 69 made every ledger derive its mint from the file at the moment of
    minting. This store had NO MINT AT ALL: `spl.py` minted
    `Echo-{datetime.now()...}` and handed the id in. **The wall-clock id dies at
    its source**; the writer owns the mint, and this is the shared helper's
    FIFTH consumer.
  * RULING 60 needed an echo<->claim join that survives a process. It could not:
    nothing persisted the echo.
  * RULING 74 generalized Ruling 53's law from the mint to EVERY derivation over
    the same file. Applied here AT DRAFTING rather than after a battery found
    it - see `read_all`.

WHAT IS DELIBERATELY NOT HERE, each with its owner
-------------------------------------------------------------------------------
  * RETRIEVAL, and any echo-content QUERY surface (search, similarity, recall
    by resonance) -> the scar/retrieval schema enrichment ruling, NEXT after
    this one. `get_echo` and `list_echoes` are the two reads this store has
    always had; **this ruling makes them honest, it does not add a third.**
  * SCHEMA ENRICHMENT beyond serialization -> the same ruling. The fields below
    are exactly the fields `Echo` already had.
  * COMMIT-ORDERING / crash consistency -> carried, unchanged. Note that
    `created_at` REMAINS wall-clock DATA, which belongs to that family: **a
    timestamp is a fact of record; the ID was the defect.** An id orders and
    must be unique, so a clock is the wrong instrument for it; a creation time
    records when something happened, which is what a clock is for.

COINS: the `ECH-` prefix and `EchoLogUnreadable`. No enum, no threshold, no
score, and no field the `Echo` dataclass did not already carry.
"""

from __future__ import annotations

import json
from dataclasses import fields as dataclass_fields
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.models import Echo
from src.utils.atomic_write import durable_append_text
from src.utils.record_value import validate_record_value


class EchoLogUnreadable(Exception):
    """RULING 53'S SENTINEL: the echo log EXISTS and cannot be read.

    Raised at the moment an id would be minted - minting from an unknown floor
    could write an `ECH-` id that already names a different echo, and an
    append-only record cannot later disambiguate two lines wearing one id.

    **AND RAISED AT EVERY READ**, which is Ruling 74's generalization applied
    here at drafting rather than discovered by a battery: every fact this store
    answers comes out of this one file, and `record()` derives from it BEFORE
    it mints. Answering a read from an empty result would be "I could not look"
    reported as "there is nothing there" - and here that would mean a claim's
    perception silently absent from the lineage that is this store's whole job.
    """


# The `Echo` dataclass's own field names, read from the dataclass rather than
# spelled again here. A second spelling is a second thing to keep in step.
_ECHO_FIELDS: Tuple[str, ...] = tuple(f.name for f in dataclass_fields(Echo))


class EchoMemory:
    """Append-only echo ledger. The four siblings' shape, deliberately verbatim.

    THE SHAPE IS COPIED ON PURPOSE. CAE is the append-only store this project
    has ruled on six times (31, 42 res.4, 45, 53, 66, 69) and the ancestry,
    prediction, goal, examination and activation stores each followed it. Every
    one of those rulings applies here for the same reasons, and writing a
    sixth subtly-different durable append-only store would be re-deciding
    settled questions by accident.

    Responsibilities:
      - RECORD every echo the pipeline perceives, minting its identity.
      - Recall an echo by id, or list them in append order.
      - Be the durable lineage a scar or doctrine can be traced back through.
    """

    ID_PREFIX = "ECH-"

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
        # THE WRITE-ONLY PER-PROCESS MIRROR (res.3), and it is DECLARED as one
        # rather than left to be discovered. It holds what THIS PROCESS
        # appended; it is NOT the store, and nothing reads it back into a
        # decision. CAE's reason verbatim, now at its fifth site: the FILE is
        # the ledger, because the ledger spans processes and memory does not.
        #
        # **THERE IS NO `_load()` ANY MORE, AND ITS ABSENCE IS THE POINT.**
        # Reads re-read the file per call (see `read_all`), so a constructor
        # that populated memory would be building the stale authority Ruling 63
        # refused at the projection and Ruling 65 refused at the topology.
        self.echoes: List[Echo] = []

    # -----------------------------------------------------------------
    # THE SOURCE - Ruling 32's runtime-else-seed, in ONE place
    # -----------------------------------------------------------------

    def _source(self) -> Path:
        """The file reads come from: runtime if present, ELSE the seed.

        **THE MINT DERIVES FROM THIS SAME FILE, and that is deliberate.** An id
        is live iff a read could return it, so the floor must be taken over
        exactly what reads see - deriving from the runtime path while reads
        fell back to the seed would let a seeded id be reissued.

        Deliberately does NOT touch anything into existence. A loader that
        creates its source is a writer wearing a reader's name, and the seed has
        no writer.
        """
        return (self.runtime_path if self.runtime_path.exists()
                else self.seed_path)

    # -----------------------------------------------------------------
    # THE MINT - Ruling 69's shared helper, FIFTH consumer
    # -----------------------------------------------------------------

    def _derive_seq(self) -> Optional[int]:
        """The highest `ECH-` ordinal already ON DISK, or `None` if UNDERIVED.

        Ruling 69's whole property set inherits at a new prefix: derived at the
        moment of minting, RAW-TEXT scanned so an ordinal on a torn or
        unparseable line is still seen and never reissued, and Ruling 53's
        sentinel intact - `None` IFF the file EXISTS and the read raised, a
        MISSING file a legitimate `0`.

        **LEGACY `Echo-…` IDS ARE A DIFFERENT NAMESPACE AND CANNOT COLLIDE.**
        The scan is anchored on `ECH-` followed by digits, so a wall-clock id
        like `Echo-20260805175535779367` matches nothing here - neither raising
        the floor nor being reissued. Pinned, not assumed.
        """
        return derive_max_ordinal(self._source(), self.ID_PREFIX)

    def _next_id(self) -> str:
        """Mint the next id, or REFUSE. Callers hold `mint_lock`.

        UNDERIVED, IT RAISES rather than falling back to a number: two echoes
        wearing one id are two perceptions nobody can tell apart, and every scar
        and doctrine that traces its lineage back through this store would land
        on an ambiguous record.
        """
        seq = self._derive_seq()
        if seq is None:
            raise EchoLogUnreadable(
                f"the echo log at '{self._source()}' exists and cannot be "
                f"read, so the next ECH ordinal is UNKNOWN. Minting one anyway "
                f"could write an id that already names a different perception.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # SERIALIZATION - the schema decision Batch 66 reserved (res.2)
    # -----------------------------------------------------------------

    @staticmethod
    def _to_dict(echo: Echo) -> Dict[str, Any]:
        """The echo's serialized form. EXPLICIT, field by field.

        **THIS IS THE DECISION BATCH 66 RESERVED TO THIS RULING.** That batch
        found `default=str` load-bearing here and ONLY here, because this store
        serialized `echo.__dict__` RAW - so `created_at` arrived as a live
        `datetime` and `json.dumps` needed a fallback to stringify it. Every
        other store in `src/` converted through its own `_to_dict` first and
        needed no default at all.

        `default=str` is a COERCION, and Ruling 66's law is REFUSAL NEVER
        COERCION: it silently turns whatever it is handed into that object's
        `repr`, so a field whose type changed would persist as prose and nobody
        would learn of it. Converting explicitly means the ONE field that needs
        it is converted BY NAME, and anything else non-canonical REFUSES at the
        writer gate instead of being stringified into a permanent record.

        `created_at` goes out as `.isoformat()` and comes back through
        `fromisoformat` - a round trip that is exact, and readable by any
        conforming parser in any language rather than only by Python's `repr`.
        """
        return {
            "id": echo.id,
            "content": echo.content,
            "resonance_score": echo.resonance_score,
            "created_at": echo.created_at.isoformat(),
            "doctrine_link": echo.doctrine_link,
            "claim_id": echo.claim_id,
        }

    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> Optional[Echo]:
        """Rebuild an echo from a log line, or `None` if the line is unreadable.

        **TOLERANT CONSTRUCTION, AND THE BYTES ARE UNTOUCHED FOREVER** (res.2).
        A key this build does not know - notably `source`, deleted by Ruling 68
        - is dropped AT OBJECT CONSTRUCTION, never from the file. Ruling 68's
        forensic law governs: *"legacy bytes are untouched: every
        `"source": "user"` already written into a store stays exactly where it
        is. Forensic record - no migration, and no reader-side reinterpretation
        of what a stored value used to mean."*

        So the RECORD keeps everything it was ever given and the OBJECT holds
        the current schema. That is not a compromise between the two: it is the
        only arrangement in which a forensic log can outlive its writer's
        schema, which is the whole reason this house appends rather than
        rewrites.

        `created_at` parses through `fromisoformat`, which accepts BOTH the
        `isoformat()` this build writes and the space-separated `str(datetime)`
        the `default=str` era produced - verified against both forms rather
        than assumed. An unparseable line contributes NOTHING (floor semantics);
        it is never coerced and never guessed at.
        """
        if not isinstance(data, dict):
            return None
        known = {key: value for key, value in data.items()
                 if key in _ECHO_FIELDS}
        stamp = known.get("created_at")
        if isinstance(stamp, str):
            try:
                known["created_at"] = datetime.fromisoformat(stamp)
            except ValueError:
                return None
        try:
            return Echo(**known)
        except (TypeError, ValueError):
            return None

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write, and it targets the RUNTIME path (Ruling 32).

        Batch 66's writer discipline, in full and for the first time at this
        store: the validator runs BEFORE `mkdir` and BEFORE `open`, so a refused
        entry leaves no file and no directory; `allow_nan=False`, because NaN
        and Infinity persist as bare tokens that are INVALID under strict JSON
        and a forensic log outlives the code that wrote it; and there is NO
        `default=`, so a non-canonical leaf REFUSES rather than being silently
        stringified.

            ~~Mode `"a"` is the only write mode in this file.~~

        RULING 78 (2026-08-09) - SUPERSEDED IN PLACE, old text struck above.
        The append moved to `atomic_write.durable_append_text`, so there is
        now no write mode in this file AT ALL. **THE PROPERTY IS UNCHANGED
        AND STRONGER**: the unrewritability is enforced by the funnel plus
        the AST census in `tests/test_ruling78.py`, which forbids a
        mode-`"a"` open anywhere in `src/` outside the helper - so a `"w"`
        here would have to get past a tree-wide scan rather than a reader.
        The atomicity exemption below still stands exactly as written; what
        the move added is DURABILITY, which that exemption never answered.

        DELIBERATELY NOT ATOMIC
        (Rider R3's exemption, CAE's reason verbatim): a torn APPEND damages one
        line, which the floor semantics already drop; a torn SNAPSHOT destroys
        the prior state.
        """
        validate_record_value(payload, path="echo_entry")
        self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
        # RULING 78 res.2: durable at its own write. Bytes identical -
        # the serializer, the validator above and this store's error
        # discipline are unchanged; only the fsync is new.
        durable_append_text(self.runtime_path,
                            json.dumps(payload, allow_nan=False) + "\n")

    def record(self, content: str, *,
               claim_id: Optional[str] = None,
               doctrine_link: Optional[str] = None,
               resonance_score: float = 1.0) -> Echo:
        """Record a perceived echo. **THE WRITER OWNS THE MINT** (Ruling 69).

        **THERE IS NO `add_echo` AND NO CALLER-SUPPLIED ID.** The old door took
        an already-constructed `Echo` whose identity someone else had minted -
        which is how `spl.py` came to stamp `Echo-{datetime.now()...}` on every
        perception AUREA has ever had. A wall-clock id is unique only by luck of
        microsecond spacing, orders by when rather than by what, and is minted
        by a layer that owns no store. **The door is DELETED rather than
        discouraged** (Ruling 65's form): there is no path here that accepts an
        id, so the wrong one is unwritable rather than merely inadvisable.

            ~~`add_echo(self, echo: Echo) -> None`: "Add a new Echo to memory
            and persist to disk. Ruling 32: appends to the RUNTIME path, never
            the seed."~~  DELETED 2026-08-05 BY RULING 75, history kept here
            because the deleted signature IS the record of how the defect
            entered: the store accepted identity from outside.

        `claim_id` IS SET AT CONSTRUCTION, never by post-hoc mutation - Ruling
        60's law, which simply moves here with the construction site. An echo
        that acquired its linkage afterwards would have existed, however
        briefly, in a state where it was unattributable.

        RAISES on write failure, and the echo does not exist. O1's gate applied
        at this store's own reason: an echo the caller holds but no file records
        is exactly the un-persisted perception these five pressures were about.
        """
        with mint_lock(self.runtime_path):
            echo = Echo(
                id=self._next_id(),
                content=content,
                resonance_score=resonance_score,
                created_at=datetime.now(),
                doctrine_link=doctrine_link,
                claim_id=claim_id,
            )
            self._append(self._to_dict(echo))
        self.echoes.append(echo)
        return echo

    # -----------------------------------------------------------------
    # READS - free (Ruling 1), and they re-read the FILE (res.3)
    # -----------------------------------------------------------------

    def read_all(self) -> Tuple[Echo, ...]:
        """Every readable echo, IN APPEND ORDER. The history, as written.

        Reads the FILE rather than `self.echoes`: the log spans processes and
        the in-memory mirror does not. A line that will not parse, or that
        carries a `created_at` no parser accepts, contributes NOTHING - it is
        never coerced.

        **AN UNREADABLE EXISTING LOG RAISES TYPED** - Ruling 74's lesson applied
        at drafting rather than after a battery found it. Returning `()` would
        render "I could not look" as "there is nothing there", and at this store
        that reads as a perception having never happened. A missing file stays a
        legitimate empty history: absence is a first run, not a fault.
        """
        source = self._source()
        if not source.exists():
            return ()
        try:
            handle = open(source, "r", encoding="utf-8")
        except OSError as failure:
            raise EchoLogUnreadable(
                f"the echo log at '{source}' exists and cannot be read, so no "
                f"fact about any perception can be derived from it. Answering "
                f"a read from an empty result would report that a claim was "
                f"never perceived, when the truth is that the record could not "
                f"be opened.") from failure
        out: List[Echo] = []
        with handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                echo = self._from_dict(data)
                if echo is not None:
                    out.append(echo)
        return tuple(out)

    def get_echo(self, echo_id: str) -> Optional[Echo]:
        """Retrieve an echo by its unique id, from the FILE."""
        for echo in self.read_all():
            if echo.id == echo_id:
                return echo
        return None

    def list_echoes(self) -> List[Echo]:
        """Every stored echo, in append order, from the FILE.

        Returns a `list` because that is what this method has always returned
        and callers index it. `read_all()` is the tuple-returning sibling form.
        """
        return list(self.read_all())
