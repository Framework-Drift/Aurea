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

APPEND-ONLY LOGS ARE EXEMPT FROM *THIS* FUNNEL, AND THE EXEMPTION IS A
DIFFERENT FAILURE CLASS, not a smaller version of the same one. `CAE`'s ledger,
the RB log, the GSR alerts, SAE's restart records, the structural-violation log
and EchoMemory all open mode `"a"`. A torn APPEND damages exactly the line being
written and leaves every prior line intact - and every one of those readers
already handles it, by FLOOR SEMANTICS: `cae._derive_seq` and `cae.read_all`
skip a line that will not parse, on purpose, because "a forensic log outlives
the code that wrote it." A torn SNAPSHOT destroys the whole prior state.
Detectable-and-droppable versus unrecoverable: routing an append through
`atomic_write_text` would mean reading the entire ledger into memory and
rewriting it on every entry, which converts an append-only record into a
whole-file rewrite - turning the exempt failure class into the dangerous one in
the name of fixing it.

    ~~That paragraph was the whole of what this module said about appends.~~

RULING 78 (2026-08-09) - SUPERSEDED IN PART, old text kept above verbatim.
**THE ATOMICITY EXEMPTION STANDS EXACTLY AS WRITTEN. WHAT IT NEVER ANSWERED
WAS DURABILITY, AND THE TWO WERE NEVER THE SAME GUARANTEE.** Atomicity asks
whether a reader can see a half-written line; durability asks whether a line
the writer believes it wrote is on the device at all. Every argument above is
about the first, and the second went unaddressed by omission rather than by
decision - so an append returned, the caller treated the record as made, and
the bytes sat in the page cache where a power loss took them.

That is not a smaller version of the torn-line problem either. The sharpest
consequence is CROSS-STORE: a minted id escapes into records that ARE fsync'd
(a suspension snapshot, one of Ruling 76's `claim_id` joins), its own ledger
line dies in the cache, the mint's floor re-derives LOWER at restart, and the
id is REBORN naming a different perception while durable joins still point at
it. Ruling 69's letter holds - the line never reached disk - and its intent
does not.

So appends are exempt from the SNAPSHOT funnel and are NOT exempt from
durability: `durable_append_text` below is their funnel, and the argument for
one funnel is the argument `atomic_write_json` already makes for `allow_nan`
- twelve disciplined sites are twelve chances to forget; one funnel is a
property, and it stays true for the thirteenth site nobody has written yet.
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


def durable_append_text(path: Union[str, Path], line: str,
                        encoding: str = "utf-8") -> None:
    """Append `line` to `path` and do not return until it is on the device.

    RULING 78 res.2 (2026-08-09) - THE APPEND FUNNEL. Every mode-`"a"` write in
    `src/` routes through here; the AST pin in `tests/test_ruling78.py` asserts
    there are none left outside this module, so the routing is unexecutable-by-
    omission rather than remembered.

    THE CALLER SUPPLIES THE TRAILING NEWLINE, AND THAT IS THE RULED CHOICE.
    This function writes the bytes it is given and not one more. Appending a
    separator would be choosing something about CONTENT, and the line separator
    is part of a ledger's format, which belongs to the ledger's owner - the same
    boundary `atomic_write_text` draws when it writes `text` verbatim. It also
    keeps every routed site a pure substitution: each one already wrote
    `json.dumps(...) + "\\n"`, so the bytes on disk are identical to what the
    raw `open` produced and only the durability is new.

    M4-δ (2026-08-15) - THE COLUMN-ZERO LAW. **RULING 78 res.2 STANDS EXACTLY AS
    WRITTEN ABOVE, AND THE LINE BETWEEN THEM IS THE WHOLE OF THIS ADDITION.**

    THE DEFECT, MEASURED AT M4-α AND RULED HERE: a torn append leaves bytes with
    NO TRAILING NEWLINE, so the next append concatenated onto them and **the
    first record written after a crash was SWALLOWED into the torn fragment and
    unreadable to every reader.** Its id was minted and its bytes reached disk -
    the MINT was safe (Ruling 69 res.2's raw-text scan) - but the RECORD was
    lost. Reproduced on `claim_ancestry` and `cae`, so it belonged to every
    append-only ledger in the tree rather than to any one of them.

    **WHAT THE FUNNEL NOW OWNS IS THE BOUNDARY, NOT THE FORMAT.** The caller
    still supplies its own trailing newline and this function still appends no
    separator to the caller's content. The prefix below fires ONLY when the
    PREVIOUS write was torn - never after a well-formed one, because a
    well-formed write ended at column 0 by the caller's own trailing newline. So
    it chooses nothing about any record's bytes; it repairs the FILE's boundary,
    which is filesystem integrity of exactly the same standing as the `fsync`
    two lines below it.

    **THE TORN FRAGMENT IS NOT REPAIRED INTO VALIDITY, AND THAT IS THE HALF
    WORTH READING TWICE.** It becomes its OWN line, which every reader still
    refuses by floor semantics exactly as the standing torn-line law provides -
    a half-written record stays a half-written record forever. What changes is
    that it stops taking an innocent record down with it. Nothing is silently
    made valid; one thing is stopped from being silently destroyed.

    WHAT STAYS AT THE SITE, DELIBERATELY: `json.dumps`, `validate_record_value`,
    `allow_nan=False`, id minting, the mint lock, and each writer's error
    discipline. This helper decides NOTHING - it is a filesystem primitive of
    the same standing as `json.dumps` or `Path.mkdir`, and the "not a second
    writer" argument in this module's docstring applies to it unchanged. There
    is no store import here and there must never be one.

    `flush` THEN `fsync`, BOTH REQUIRED AND NEITHER REDUNDANT - `flush` moves
    Python's buffer into the OS, `fsync` moves the OS's buffer onto the device.
    Returning after only the first is what let a recorded line die in the page
    cache while the caller treated the record as made.

    IT RAISES. An `OSError` from the fsync reaches the caller exactly as one
    from the `open` already did, so each site's existing discipline decides what
    that means: the ledgers whose write GATES the thing being recorded (Rulings
    58/61) still refuse, and the best-effort forensic writers still catch and
    land it on their own failure ledgers (Ruling 11 - the observer never gates
    the observed). This function does not choose between those, because the
    choice is the site's and always was.

    `mkdir` here is deliberate belt-and-braces: the routed sites each do their
    own, several of them ordered AFTER a validator on purpose so that a refused
    entry leaves no directory it did not already need. Those orderings are
    untouched; this one exists so the primitive is complete for the site nobody
    has written yet.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding=encoding) as handle:
        # M4-δ: THE BOUNDARY INVARIANT. Every append begins at column 0.
        if _ends_mid_line(path):
            handle.write("\n")
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def _ends_mid_line(path: Path) -> bool:
    """Does `path` exist, hold bytes, and END WITHOUT a newline? (M4-δ)

    True ONLY for a file whose last write was torn. An empty or absent file is
    already at column 0, and a file written by any routed site ends with the
    caller's own trailing newline - so on every healthy path this returns False
    and the append is BYTE-IDENTICAL to what it was before this ruling. That is
    not an aspiration; it is why the differential for this pass is zero.

    **CHECKED IN BYTES, NOT IN DECODED TEXT.** `0x0A` is the last byte of a
    UTF-8 newline regardless of what precedes it, and decoding a file whose tail
    is a torn multi-byte sequence would raise on exactly the input this function
    exists to recognize.

    **A FAILED PROBE MEANS "NO PREFIX", AND THAT IS DELIBERATE RATHER THAN
    DEFENSIVE.** This funnel's raise semantics are RULED (Ruling 78: it raises,
    and each site's own discipline decides what that means - the gating ledgers
    refuse, the forensic writers catch). A probe that raised would make a
    boundary this function could not DETERMINE into a new refusal for a write
    the caller could otherwise have made, which would let a disk hiccup on a
    read gate a claim's perception. Falling back to no-prefix is exactly the
    pre-δ behaviour, so the worst case is bounded by the status quo: the swallow
    this ruling closes, not a new failure.
    """
    try:
        if path.stat().st_size == 0:
            return False
        with open(path, "rb") as probe:
            probe.seek(-1, os.SEEK_END)
            return probe.read(1) != b"\n"
    except OSError:
        return False
