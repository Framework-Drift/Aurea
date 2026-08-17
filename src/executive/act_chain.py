"""Forward hash-chaining for the Executive's act logs. The redundancy.

**THE WELL-FORMED-EDIT CLASS IS UNCATCHABLE WITHOUT REDUNDANCY.** M7-d's tamper
census measured it: a field edited inside a syntactically valid line round-trips
undetected, because nothing anywhere cross-checks a line against anything else.
No amount of care at the read side closes that - there is simply nothing to
compare against. So the redundancy starts here, and it starts FORWARD.

**ERA HONESTY IS LAW, AND IT IS THE HARDER HALF TO HOLD.** Historical lines carry
no chain field and ANSWER ABSENT FOREVER. Nothing rehashes them, annotates them,
or migrates them. The chain begins where it begins, and a verifier reports the
pre-chain era as UNVERIFIABLE-BY-CHAIN - **which is a STATE, not a defect**.
Back-filling would be the worse crime by far: it would produce a log that LOOKS
fully verified while the verification of its oldest records was manufactured
after the fact by the same process that could have altered them.

WHY THE CHAIN IS OVER RAW BYTES, AND WHY IT IS READ FROM DISK
-------------------------------------------------------------------------------
The hash covers THE PREVIOUS LINE'S BYTES AS THEY EXIST ON DISK, read at mint
time under the writer's own lock - Ruling 69's derive-from-file posture, at a
second surface. A cached tail would be exactly the defect Ruling 69 deleted three
times over (a cached derivation of a file, trusted over its source), and here it
would be worse: the cache would certify bytes nobody re-read.

Bytes rather than a re-serialization of the parsed record, because the VERIFIER
has only the file. A chain over a re-serialized object would need every future
reader to reproduce this module's exact serialization to check anything, which
makes the check a property of the code rather than of the record.

    THIS MODULE LIVES BESIDE THE LOGS, NOT IN `src/utils`. Kernel substrate is
    not this order's to touch, and the chain is an Executive act-log concern.

WHAT THIS DOES NOT DO
-------------------------------------------------------------------------------
It detects; it never repairs, and it grants nothing. A chain is redundancy for a
READER of history. **The act logs stay non-constitutive**: no decision path reads
them before or after this change, and M7-d's kill/reconstruction pins are what
hold that line - an integrity mechanism that made the logs load-bearing would
have inverted the design.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

__all__ = ["CHAIN_KEY", "GENESIS_CHAIN_SEED", "genesis_chain", "last_line_bytes",
           "chain_over", "chain_for_next_line", "strip_terminator"]

#: The field every CHAINED-ERA line carries. A line without it is pre-chain, and
#: that absence is read as ABSENT rather than as a missing value.
CHAIN_KEY = "prev_chain"

#: What the FIRST line of an EMPTY log chains from. Declared, named, and in-file
#: so a verifier never has to guess what "no previous line" hashed to.
#:
#: A log that already holds legacy lines does NOT use this: its first chained
#: line chains over the last LEGACY line's bytes, which is what makes a mixed-era
#: log verifiable from the chain's first record onward rather than from nowhere.
GENESIS_CHAIN_SEED = b"aurea:act-log-chain.v1:genesis"


def genesis_chain() -> str:
    return hashlib.sha256(GENESIS_CHAIN_SEED).hexdigest()


def last_line_bytes(path: Path) -> Optional[bytes]:
    """The last non-empty line's RAW BYTES, or `None` for an empty/absent log.

    Trailing newlines are stripped structurally rather than by `rstrip`, and
    blank segments are skipped - M4-δ's column-zero law can legitimately leave a
    newline-prefixed record after a torn write, and a blank segment is not a
    line. A verifier splits the same way, which is what keeps the two sides
    agreeing about what "the previous line" means.

    **THE LINE TERMINATOR IS EXCLUDED, AND THAT WAS FOUND BY MEASUREMENT.** The
    append funnel writes in text mode, so on Windows every line lands as
    `...}\r\n` while on POSIX it lands as `...}\n`. A chain over the terminator
    would be SELF-CONSISTENT (writer and verifier would agree on one machine)
    and still wrong in the way that matters: it would hash a FRAMING ARTIFACT
    rather than the record, so the same history would verify on the machine that
    wrote it and break the moment the file crossed a platform or met any tool
    that normalizes line endings. The terminator is not part of the record, so
    it is not part of what the record's successor attests to.
    """
    if not path.exists():
        return None
    data = path.read_bytes()
    if not data:
        return None
    parts = [strip_terminator(p) for p in data.split(b"\n")]
    while parts and parts[-1] == b"":
        parts.pop()
    return parts[-1] if parts else None


def strip_terminator(line: bytes) -> bytes:
    """Drop a single trailing CR. Named ONCE so writer and verifier cannot
    disagree about where a line ends - two spellings of that boundary is how a
    chain starts reporting breaks that never happened."""
    return line[:-1] if line.endswith(b"\r") else line


def chain_over(previous_line: Optional[bytes]) -> str:
    """The chain value a line carries, given the bytes it follows."""
    if previous_line is None:
        return genesis_chain()
    return hashlib.sha256(previous_line).hexdigest()


def chain_for_next_line(path: Path) -> str:
    """The chain value for the record about to be appended to `path`.

    CALLERS MUST HOLD the log's mint lock across this read and the append. That
    is not an extra discipline: both act logs already hold it across
    derive -> mint -> append, and the chain simply joins the same hold. A chain
    computed outside it could certify a line some other writer had already
    replaced - **a torn chain is worse than no chain**, because it would report
    a break where nothing was tampered with.
    """
    return chain_over(last_line_bytes(path))
