"""
atomic_write.py - a durable SNAPSHOT is replaced whole or not at all.

Rider R3 of the mutation-surface audit (2026-07-29).

WHAT THIS FIXES
---------------
Thirteen durable stores wrote their whole-file snapshot the same way:

    with open(self.runtime_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

Mode `"w"` TRUNCATES THE TARGET BEFORE THE FIRST BYTE OF NEW CONTENT IS
WRITTEN. Between that truncation and the last byte, the file on disk is neither
the old state nor the new one - it is a prefix. A process killed in that window
(or a full disk, or a serialization error partway through a large payload)
leaves a JSON document that ends mid-token, and the store that reads it back
next construction gets a `ValueError`.

What happens then is store-specific and none of the outcomes are good. Ruling
42's version-gated loaders REFUSE, which is the honest half - but a refusal
caused by a torn write is a refusal AUREA never earned: the state was real, it
was written down, and the writing destroyed it. `SAE.load` records the corrupt
file and constructs at defaults, which is worse in the direction that matters
most, because defaults mean `epoch_count=0` - **A TORN SNAPSHOT OF THE EPOCH
FILE GRANTS A FRESH MUTATION CEILING**, which is exactly the restart absolution
Ruling 34 exists to forbid, arriving through the persistence layer instead of
through the process boundary.

    Ruling 32 established that runtime state never writes to a TRACKED path.
    Ruling 39 established that it never writes to an UNIGNORED path either.
    This establishes that it never DESTROYS THE PRIOR SNAPSHOT to write the
    next one.

THE SHAPE: temp file in the SAME DIRECTORY, flush, `os.fsync`, `os.replace`.
`os.replace` is atomic on both POSIX and Windows (`MoveFileEx` with
`MOVEFILE_REPLACE_EXISTING`), so a reader at any instant sees either the
complete old file or the complete new one. Same directory is not a style choice
- `os.replace` across filesystems is not atomic and may fail outright, so the
temp file is created beside its destination rather than in a temp dir.

SERIALIZATION HAPPENS BEFORE THE FILE IS TOUCHED, and that is a second real
gain rather than an implementation detail. `json.dump(payload, f)` writes
incrementally, so an unserializable object partway through the payload leaves a
truncated file behind. `json.dumps` raises with the destination byte-identical.

WHY A SHARED HELPER IS NOT A SECOND WRITER (Ruling 1)
------------------------------------------------------
Ruling 42 Slice 1 refused a shared LOADER, in terms: "a shared loader would be
a second writer wearing a helper's shape." That refusal stands and this does not
contradict it, because the two functions are not the same kind of thing.

A loader DECIDES: what version is acceptable, what a dangling reference means,
whether to quarantine or refuse. Those are the owner's decisions about the
owner's store, and a shared implementation of them makes one module the author
of every store's restoration semantics.

This helper decides NOTHING. The owner picks the path, builds the payload, and
chooses the serialization options; what crosses this boundary is bytes and a
destination. It is a filesystem primitive of the same standing as `json.dumps`
or `Path.mkdir`, both of which all thirteen stores already share. There is no
store import here and there must never be one.

WHAT IS DELIBERATELY NOT HERE
-------------------------------
NO `.prev` GENERATIONS. Keeping the previous snapshot beside the new one is a
retention policy - how many, pruned when, read back by whom, and what a reader
does when the current file is refused but a `.prev` parses. Every one of those
is a decision, and a rollback surface for identity stores is emphatically not
one to introduce as a side effect of a durability fix. Deferred, not owed.

NO DIRECTORY FSYNC. On POSIX, guaranteeing the RENAME survives power loss also
requires fsyncing the containing directory. It is not attempted here: this
tree's platform has no directory file descriptor to sync, so the call would be
a platform branch that is a no-op on the machine it runs on. The hazard closed
here is a TORN FILE, which `os.replace` closes on both platforms; surviving
power loss at the block layer is a different and larger claim, and making a
partial version of it look complete is the completeness-claim defect this
codebase has now found seven times.

APPEND-ONLY LOGS ARE EXEMPT, AND THE EXEMPTION IS A DIFFERENT FAILURE CLASS,
not a smaller version of the same one. `CAE`'s ledger, the RB log, the GSR
alerts, SAE's restart records, the structural-violation log and EchoMemory all
open mode `"a"`. A torn APPEND damages exactly the line being written and
leaves every prior line intact - and every one of those readers already handles
it, by FLOOR SEMANTICS: `cae._derive_seq` and `cae.read_all` skip a line that
will not parse, on purpose, because "a forensic log outlives the code that
wrote it." A torn SNAPSHOT destroys the whole prior state. Detectable-and-
droppable versus unrecoverable: routing an append through this helper would
mean reading the entire ledger into memory and rewriting it on every entry,
which converts an append-only record into a whole-file rewrite - turning the
exempt failure class into the dangerous one in the name of fixing it.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Union


def atomic_write_text(path: Union[str, Path], text: str,
                      encoding: str = "utf-8") -> None:
    """Replace `path` with `text`, whole or not at all.

    The destination is never truncated: the content lands in a sibling temp
    file which is flushed and fsynced before `os.replace` swaps it in. On any
    failure the temp file is removed and the original is byte-untouched.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Created in the destination's OWN directory - see the module docstring:
    # `os.replace` is only atomic within a filesystem.
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                    prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            # Both are required and neither is redundant: `flush` moves Python's
            # buffer into the OS, `fsync` moves the OS's buffer onto the device.
            # Replacing an unsynced temp file can publish a name whose contents
            # are still in flight.
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, str(path))
    except BaseException:
        # The prior snapshot is still intact; the only thing to clean up is the
        # partial temp file. `BaseException` because a KeyboardInterrupt mid-write
        # is precisely one of the interruptions this function exists for, and
        # leaving `.tmp` litter behind it would make the next run's directory
        # listing a lie about what state exists.
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_json(path: Union[str, Path], payload: Any,
                      encoding: str = "utf-8", **dump_kwargs: Any) -> None:
    """`json.dump` semantics, atomically. Serializes BEFORE touching the file.

    `dump_kwargs` are passed to `json.dumps` unchanged, so each owner keeps the
    exact serialization options it already used (`indent`). This function
    chooses nothing about the content.

    RULING 66 (2026-08-02) - `allow_nan=False` IS SET HERE, AT THE FUNNEL, AND
    IT IS NOT OVERRIDABLE.

    THE FUNNEL WAS CHOSEN OVER TWELVE CALL SITES DELIBERATELY. Every
    `atomic_write_json` caller in `src/` serializes through this one statement,
    so setting it here makes the guarantee true for all of them at once AND
    keeps it true for the thirteenth caller nobody has written yet. Twelve
    disciplined call sites are twelve chances to forget; one funnel is a
    property. This is the same reasoning that put Ruling 51's guard at
    `authorize()` - the single spend site - rather than on each mutation path.

    IT IS PASSED POSITIONALLY-BEFORE-`**`, SO A CALLER SUPPLYING ITS OWN
    `allow_nan` GETS A `TypeError` FOR A DUPLICATE KEYWORD. That is intended:
    the wrong path is UNEXECUTABLE rather than discouraged (CLAUDE.md §3). A
    `setdefault` would have left an override available, and an override on this
    particular flag is the ability to write `NaN` into a forensic record.

    WHY NaN AND Infinity ARE THE TARGET: `json.dumps` writes them as bare
    non-standard constants that no conforming parser in any other language will
    read. `default=` never sees them - the float serializer handles them first -
    so deleting `default=str` alone would not have closed this, which is
    precisely why the ruling names both halves.
    """
    atomic_write_text(path, json.dumps(payload, allow_nan=False, **dump_kwargs),
                      encoding=encoding)
