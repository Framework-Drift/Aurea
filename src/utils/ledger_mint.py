"""
ledger_mint.py - RULING 69 (2026-08-02): WRITER OWNERSHIP.

**THE MINT DERIVES FROM THE RECORD AT THE MOMENT OF MINTING, because a counter
is a cached derivation and this house has refused that structure twice already.**

WHAT WAS BROKEN
-------------------------------------------------------------------------------
All three append-only ledgers shared one mint shape: `self._seq`, derived LAZILY
ONCE from the file at construction, then incremented IN MEMORY forever after and
never re-synced. Two live instances over one path therefore minted the SAME
ordinals whenever the second derived before the first appended - measured at
`0b2072c` as four lines carrying two distinct ids, on all three ledgers.

**`_seq` WAS A CACHED DERIVATION OF THE FILE TRUSTED OVER ITS SOURCE** - the
exact structure Ruling 63 refused at the projection ("a cached projection is a
stale authority waiting for a trusting reader") and Ruling 65 refused at the
topology (a derivation persisted as a source). This was its THIRD appearance,
one layer down again, at the mint itself. The counter dies; the file answers.

WHY THIS FILE EXISTS RATHER THAN THREE COPIES
-------------------------------------------------------------------------------
Ruling 69 res.5 left the hoist to the pass. It was taken, and the AST
near-identity check (Ruling 63's method, run BEFORE the decision) is the reason:
the three `_derive_seq` bodies differed in exactly two ways - a local variable
name, and the JSON key each parsed (`id` / `claim_id` / `prediction_id`).
**RES.2 DELETES THAT SECOND DIFFERENCE BY CONSTRUCTION**, because the raw scan
parses no JSON at all. Post-fix the three bodies are identical modulo
`ID_PREFIX`, which is a parameter - so keeping three copies would be keeping
three chances to drift on a scan discipline whose anchoring is subtle enough
that Ruling 64 needed a rider to fix an unanchored version of it.

Per Ruling 63's mandate, this helper carries ITS OWN pins
(`tests/test_ruling69.py`): a shared helper guarded only through its consumers is
guarded by accident.

**PREFIXES, WIDTHS AND ERROR TYPES STAY PER-LEDGER** and are deliberately not
here - they are each ruling's own vocabulary (`CAE-`/`:03d`/`LedgerUnreadable`,
`CLM-`/`:04d`/`AncestryLedgerUnreadable`, `PRD-`/`:04d`/
`PredictionLedgerUnreadable`). This module answers one question - *what is the
highest ordinal that has reached disk* - and holds the lock while the caller
acts on the answer.

THE CROSS-PROCESS CONTRACT, DECLARED (res.4)
-------------------------------------------------------------------------------
**ONE AUREA PROCESS PER DATA ROOT.** That is the supported topology, and it is
now STATED rather than assumed - Ruling 42's whole durability model already
depends on it (every store snapshots its own whole file; two processes would
race every save, not merely these mints).

**OS-LEVEL FILE LOCKING IS DECLARED OUT**, so the exclusion is a ruling and not
a gap. `fcntl`/`msvcrt` locking is platform-split, silently degrades on network
filesystems, and would buy protection only for a topology that is not supported
anyway. **REOPENING CONDITION, NAMED: a second writer process ever becoming a
supported topology.** On that day this module is where the lock goes.

The mutex below closes the race that is REAL under the supported topology: two
ledger instances, or two threads, inside ONE process.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Dict, Optional, Union

__all__ = ["derive_max_ordinal", "mint_lock", "ordinal_pattern"]


# One lock per RESOLVED PATH, process-wide.
#
# KEYED BY THE FILE, NOT BY THE CLASS, and that is deliberate: the thing being
# protected is a file's derive -> mint -> append sequence. A per-class registry
# would hand two different ledger classes pointing at one path two different
# locks - which is exactly the shape of bug this ruling exists to close, one
# level up.
_LOCKS: Dict[str, threading.Lock] = {}
_REGISTRY_GUARD = threading.Lock()


def mint_lock(path: Union[str, Path]) -> threading.Lock:
    """The process-wide mutex for one ledger file. Held across derive → mint →
    append, never across anything else.

    `_REGISTRY_GUARD` protects the REGISTRY, not the ledger: without it two
    threads racing the first mint on a new path could each build a `Lock` and
    take a different one - a lock that does not exclude, which is worse than no
    lock because it reads as protection.
    """
    key = str(Path(path).resolve())
    with _REGISTRY_GUARD:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = _LOCKS[key] = threading.Lock()
    return lock


def ordinal_pattern(prefix: str) -> "re.Pattern[str]":
    """The anchored id pattern for a ledger prefix - RULING 64's rider form.

    `(?<![0-9A-Za-z_-])PREFIX\\d+(?![0-9A-Za-z_-])`.

    THE BOUNDARIES ARE NOT DECORATION. Ruling 60 res.3 said "anchored" and the
    code was bare, so `prefixCLM-0001suffix` forged a descent edge; `\\b` is
    INSUFFICIENT because `-` is itself a non-word character. The same reasoning
    binds here for a different consequence: an unanchored scan would read
    `X-CLM-0009` as ordinal 9 and burn eight ids, and a scan that stopped at the
    first digits would read `CLM-00010` as `CLM-0001` and REISSUE a live id.
    """
    return re.compile(
        r"(?<![0-9A-Za-z_\-])" + re.escape(prefix) + r"(\d+)(?![0-9A-Za-z_\-])")


def derive_max_ordinal(path: Union[str, Path], prefix: str) -> Optional[int]:
    """The highest ordinal already on disk for `prefix`, or `None` if UNDERIVED.

    RULING 53'S SENTINEL, WHOLE AND UNCHANGED IN SEMANTICS:
      * a MISSING file is a legitimate `0` - absence is a first run, not a fault;
      * a file that EXISTS and cannot be read is `None` - "what is here is
        unknown", and answering that with `0` is a claim about content the code
        never saw. The caller raises its own typed error; this never invents a
        number.

    **RES.2 - THE SCAN IS OVER RAW TEXT, NOT PARSED RECORDS, AND THAT IS THE
    WHOLE POINT.** Every previous implementation did `json.loads(line).get(key)`,
    so an ordinal on a TORN OR UNPARSEABLE LINE WAS INVISIBLE - and the next mint
    would reissue it. Reading the bytes instead makes the safety property
    structural: **any id that reached disk is seen and never reissued.** The
    burnt-ordinal rule stops being a memory-state discipline (`_seq` advanced
    before the append, so a failed write left a gap) and becomes a fact about
    reading the file honestly - a failed append burns nothing unless bytes
    landed, and if bytes landed the scan sees them.

    PER-LINE FLOOR SEMANTICS SURVIVE AND ARE NOW AUTOMATIC: a line that will not
    parse contributes nothing to the maximum but is no longer INVISIBLE. An
    unreadable FILE and an unparseable LINE remain different failures with
    different answers - the distinction Ruling 53 drew, preserved exactly.

    THE ONE ACCEPTED IMPRECISION, STATED RATHER THAN HIDDEN: a raw scan can
    over-count. A recorded value that happens to contain `CLM-9999` - a claim
    quoting an id, say - raises the floor and BURNS ordinals. That is the
    CONSERVATIVE direction and it is harmless by this house's own standing rule
    (ids need only be unique and increasing; gaps are fine). The opposite error -
    under-counting, which is what parsing produced - REISSUES a live id into an
    append-only record where nothing can ever disambiguate the two (3a:112).
    Given a choice between burning an ordinal and forging one, burn it.

    Read WHOLE rather than line-by-line: a torn final line has no newline, and an
    id spanning the tear is still bytes on disk.

    **`open(...)` RATHER THAN `Path.read_text`, AND THAT IS NOT A STYLE CHOICE.**
    The first draft used `Path.read_text`, which reaches `io.open` and therefore
    slips past every failure-injection fixture in this suite - all three patch
    `builtins.open` (`_UnreadableFor` and its siblings). The suite said so
    immediately: Ruling 53's refusal pins stopped witnessing a refusal. Those
    fixtures encode how this codebase simulates a failing disk, and an
    implementation that quietly escapes them is one whose most important failure
    path is no longer tested. `errors="replace"` keeps a torn line's BYTES
    readable rather than raising mid-scan - a decode error is not an unreadable
    FILE, and treating it as one would refuse a mint over a single bad byte.
    """
    ledger = Path(path)
    if not ledger.exists():
        return 0
    try:
        with open(ledger, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return None

    highest = 0
    for match in ordinal_pattern(prefix).finditer(text):
        highest = max(highest, int(match.group(1)))
    return highest
