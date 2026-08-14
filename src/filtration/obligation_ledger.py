"""
obligation_ledger.py - M3-A slice A, kernel K2. THE OBLIGATION LEDGER.

**AN OBLIGATION THAT WAS NOT ADMITTED BEFORE IT WAS WORKED IS NOT AN
OBLIGATION** - Ruling 61's law (a prediction that was not committed before its
outcome is not a prediction) and Ruling 72's (a goal that was not committed
before its pursuit is not a goal), arriving at the thing those two both
presuppose: the standing claim that something is OWED.

WHAT THIS STORES AND WHAT IT DOES NOT
-------------------------------------------------------------------------------
It stores DIRECTION. It moves NOTHING. There is no scheduler, no loop, no
internal caller anywhere in `src/`: every door here is externally invoked, the
Q-family's three-doors pattern verbatim (Rulings 72/73/74). A ledger that
selected its own next obligation would be an executive, and the Executive
domain is M7's, not this pass's.

**IT GRANTS NO AUTHORITY.** Recording that something is owed is not a licence to
do it, and this module imports nothing it could command - no SAE, no Codex
writer, no RACM, no reflex, no expression surface. Ruling 70's enforcement-by-
scope and Ruling 72's QL0-as-structure: a module that cannot reach a thing
cannot be talked into commanding it. The three resolver handles it DOES take are
READ-ONLY and are used for exactly one question - does this target exist.

EVENT-SOURCED, AND NEVER ERASABLE
-------------------------------------------------------------------------------
A status change is a NEW RECORD referencing `obligation_id`. No record is ever
modified in place, and **there is no delete, remove, clear, purge or truncate
method on this class or in this module** - pinned by AST, because a method named
`remove_obligation` with a docstring saying "only for duplicates" is a request
for restraint, and this project has hard evidence restraint fails (CLAUDE.md §3).
The current status of an obligation is DERIVED by folding the stream, never
stored (L3 - Rulings 63/65 both refused a stored derivation, at the projection
and at the topology; this is the same refusal at the status field).

ADMISSION IS TOTAL: EVERY PATH WRITES A RECORD
-------------------------------------------------------------------------------
**An admission that writes nothing is unproducible.** DUPLICATE, MALFORMED and
TARGETLESS each produce a REJECTED record carrying the reason, because a
rejection that leaves no trace is indistinguishable afterwards from a claim
nobody ever made - and the whole value of an obligation ledger is that it can be
consulted later about what was asked. This is Ruling 23's law (unresolved
pressure never leaves silently) at the front door.

**THE DUPLICATE CHECK LOOKS AT OPEN AND DEFERRED ONLY.** A previously REJECTED
record does not block a later admission: the first was refused, so the claim was
never taken up, and refusing it forever on the strength of having refused it once
would make a transient TARGETLESS (a doctrine not yet committed) permanent.

TARGET RESOLUTION IS A READ, AND FINDING THAT OUT COST THE PASS ITS FIRST
REAL DISCOVERY
-------------------------------------------------------------------------------
The obvious implementation of "does this suspension id resolve" is
`suspension_system.retrieve(entry_id)`. **IT IS NOT A READ ON ANY OF THE THREE
SUSPENSION SYSTEMS.** Measured before a line was written:

  * `BlackSphere.retrieve` increments `access_count`, stamps `last_accessed`,
    multiplies `orbit_stability` by 0.99, and calls `save_to_file()`;
  * `CSA.retrieve` does the same and additionally RESETS `dormancy_cycles` to 0
    and may write a `metadata['warning']`;
  * `VeiledThread.retrieve` increments, stamps, and calls `save_to_file()`.

So admitting an obligation that merely NAMES a paradox would have destabilized
its orbit, reset a quarantine's dormancy clock, and written another owner's store
to disk - **this ledger becoming a writer of three stores it does not own, at
the moment of checking whether they contain something** (Ruling 1). The check
here is MEMBERSHIP ONLY, against the base class's public `entries` mapping.
"Reads are free" (CLAUDE.md §2) is what licenses it; `retrieve` is not a read.
**An AST pin forbids this module from naming `retrieve`, `suspend`, `save_to_file`
or any other mutating verb on a resolver.**

Doctrines resolve through `Codex.get` and the fossil map, and scars through
`ScarLogicCore.get_scar` - both snapshot-on-read by Ruling 22, so neither can
hand this module a live record to mutate even by accident. **A FOSSIL RESOLVES**:
an obligation may legitimately bear on a doctrine that has fallen, and refusing
it would make the ledger unable to record what is owed about her own history.

THE THIRD STATE, AND WHY IT IS NOT A FOURTH REJECTION KIND
-------------------------------------------------------------------------------
If no resolver for a target kind was supplied, this ledger **CANNOT SEE** that
structure - and "I could not look" is not "it is not there." Docket H's cut
(`NONE_FOUND` vs `NOT_COUNTABLE`), Ruling 45's `CriterionResult.ABSENT`, and
Ruling 58's three field states are all the same distinction, and it is recorded
here as `TargetResolution.UNCHECKED` on the record rather than as a rejection.
Rejecting would assert a non-existence this module never tested; admitting
silently would claim a resolution it never performed. **The record says which.**

LOGICAL TIME
-------------------------------------------------------------------------------
Every record carries a monotonic `SEQ-` token minted in Ruling 69's pattern:
derived from the FILE at the moment of minting, never a cached counter, raw-text
scanned so an ordinal on a torn line is still seen and never reissued, under the
file's mint lock across derive -> mint -> append.

**WALL CLOCK IS RECORDED AND NEVER READ.** `created_wall` is an observation, kept
because a forensic record that cannot say roughly when is worth less - but no
comparison, no arithmetic, no sort and no branch anywhere in either module reads
it, and that is AST-pinned. Ordering is by `SEQ-` ordinal, always. This is the
carried timestamp-join hazard (Ruling 74 res.4 declined to extend it) answered by
never depending on the clock in the first place.

VOCABULARY COLLISION CENSUS (Ruling 30's discipline, run BEFORE coining)
-------------------------------------------------------------------------------
50 enum classes / 217 distinct member names in `src/` at `965c45b`. **ZERO class
name collisions.** Eight member names already exist in OTHER enums, and they are
recorded here so that no one later derives one sense from another - which is
exactly the defect Ruling 30 spent a whole ruling untangling for "scope":

  * `DEFERRED`  - `racm.Verdict.DEFERRED` (arbitration). **Ruling 73 REFUSED
    this word for the goal arbiter because RACM owns it there.** K2 rules it
    here, so it is used - and it means A STANDING CLAIM SET ASIDE WITH A REASON
    AND A DUE ORDINAL, never an arbitration verdict. Nothing converts between them.
  * `SUSPENDED` - `echonet.Verdict.SUSPENDED` (a COLLAPSE verdict) and
    `session_governor.TetherPhase.SUSPENDED`. `EpisodeOutcome.SUSPENDED` is an
    episode DISPOSITION. Ruling 33 pinned SUSPEND/SUSPENDED disjointness for
    exactly this reason; the same care applies one layer up.
  * `RESOLVED` (`goal_ledger.GoalStatus`) · `UNRESOLVED`
    (`prediction_ledger.PredictionOutcome`) · `REVISED` (`goal_ledger.AdoptionAct`)
    · `DOCTRINE`/`SCAR`/`SUSPENSION` (`tca_core.NodeType`, `ril.IdentityThread`).
    `TargetKind` deliberately mirrors `NodeType`'s referents because they name
    the same structures - **it is NOT derived from it and must not be, or a
    topology vocabulary change would silently move what this ledger can be owed
    about.**

VOCABULARIES ARE GOVERNED CONTENT, NOT KERNEL
-------------------------------------------------------------------------------
The closed sets below are v1. **They evolve through episodes, not through
edits** - v1 exists so the first record is typed rather than free text. Adding a
member is a governance act with a record behind it, the way Ruling 7 kept the
behaviour enum closed and Ruling 58 kept `OriginKind` closed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.utils.atomic_write import durable_append_text
from src.utils.ledger_mint import derive_max_ordinal, mint_lock
from src.utils.record_value import validate_record_value

__all__ = [
    "SEQ_PREFIX",
    "mint_seq_token",
    "seq_ordinal",
    "ObligationRecordType",
    "RejectionKind",
    "TargetKind",
    "TargetResolution",
    "AdmissionOutcome",
    "AdmissionResult",
    "ObligationLedger",
    "ObligationLedgerUnreadable",
    "MalformedDeferral",
]


# =====================================================================
# THE SHARED LOGICAL CLOCK
# =====================================================================
#
# ONE MINT, USED BY BOTH STORES. It lives here rather than in a third module
# because a clock module would own no store and no invariant, and the
# admission test in CLAUDE.md §2 is not one to fail on the pass that writes
# the substrate. `episode_record` imports THIS FUNCTION - not this class - so
# the zero-internal-callers pin (which binds on the CLASSES) stays exact.
#
# THE SEQUENCE IS A PREFIXED TOKEN RATHER THAN A BARE INT, DELIBERATELY.
# `derive_max_ordinal` scans RAW TEXT for an anchored prefix, which is what
# makes a torn line's ordinal visible (Ruling 69 res.2). A bare `"seq": 12`
# would need a second regex over a JSON key - a second definition of a ruled
# pattern, which Ruling 79 refused by name. Reusing the prefix mint costs one
# string and inherits the entire property set.
SEQ_PREFIX = "SEQ-"
_SEQ_TOKEN = re.compile(r"^" + re.escape(SEQ_PREFIX) + r"(\d+)$")


class ObligationLedgerUnreadable(Exception):
    """The ledger exists and cannot be read, so the next ordinal is UNKNOWN.

    Ruling 53's sentinel, whole: this NEVER falls back to a number. Two
    obligations wearing one id are two owed things nobody can tell apart
    afterwards, in an append-only record where nothing can disambiguate them
    later (3a:112).
    """


class MalformedDeferral(Exception):
    """A deferral without BOTH a reason and a due ordinal.

    Setting something aside without saying why, or without saying until when,
    is not deferral - it is dropping it while producing a record that says
    otherwise, which is worse than dropping it silently.
    """


def mint_seq_token(paths: Sequence[Path]) -> str:
    """The next logical-time token across every path given. NEVER cached.

    CALLERS MUST HOLD the mint lock for the path they are about to append to,
    across derive -> mint -> append. Deriving inside the lock and appending
    outside leaves exactly the race Ruling 69 closes.

    UNDERIVED ON ANY PATH IT RAISES, and does not fall back: a file that exists
    and cannot be read is a file whose highest ordinal is unknown, and minting
    over it could reissue a live one.
    """
    highest = 0
    for path in paths:
        seq = derive_max_ordinal(path, SEQ_PREFIX)
        if seq is None:
            raise ObligationLedgerUnreadable(
                f"'{path}' exists and cannot be read, so the next {SEQ_PREFIX} "
                f"ordinal is UNKNOWN. Minting one anyway could stamp two "
                f"records with one moment of logical time.")
        highest = max(highest, seq)
    return f"{SEQ_PREFIX}{highest + 1:06d}"


def seq_ordinal(token: Any) -> Optional[int]:
    """The integer behind a `SEQ-` token, or `None` if it is not one.

    Ordering is by THIS, never by `created_wall`. Returns `None` rather than
    raising or defaulting to 0, because an unparseable token is a record whose
    place in logical time is unknown - and a 0 would silently sort it first.
    """
    if not isinstance(token, str):
        return None
    match = _SEQ_TOKEN.match(token)
    return int(match.group(1)) if match else None


# =====================================================================
# VOCABULARY - v1, GOVERNED CONTENT, closed for now
# =====================================================================

class ObligationRecordType(str, Enum):
    """What KIND of event a line is. A status change is a new line, never an edit."""
    OPEN = "open"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    MERGED = "merged"
    EPISODE_OPENED = "episode_opened"


class RejectionKind(str, Enum):
    """Why admission refused. Every member writes a record."""
    DUPLICATE = "duplicate"
    MALFORMED = "malformed"
    TARGETLESS = "targetless"


class TargetKind(str, Enum):
    """What an obligation can be owed ABOUT.

    Mirrors `tca_core.NodeType`'s referents on purpose and is NOT derived from
    it - see the census in the module docstring.

    **WIDENED BY ONE MEMBER AT M3-D**, by the sixty-eighth manifest entry and
    never by a caller's string: `CLAIM`. GOVERNED CONTENT, exactly as the rest
    of this file's vocabularies are - `_member`'s closed-vocabulary guard is
    untouched, so an unruled fifth member is still unwritable.

    CLAIM is what the collapse path needs: a contradiction is owed about the
    CLAIM that produced it, and until now the vocabulary could only name the
    structures a claim BEARS ON.
    """
    DOCTRINE = "doctrine"
    SCAR = "scar"
    SUSPENSION = "suspension"
    CLAIM = "claim"


class TargetResolution(str, Enum):
    """Whether the target was found, not found, or NEVER LOOKED FOR.

    The third member is Docket H's cut. `UNCHECKED` is not a soft `UNRESOLVED`:
    it records that no resolver for this kind was supplied, so the ledger could
    not see the structure at all.
    """
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    UNCHECKED = "unchecked"


class AdmissionOutcome(str, Enum):
    ADMITTED = "admitted"
    REJECTED = "rejected"


# The fields an admission cannot do without. Absence or emptiness is MALFORMED.
REQUIRED_ADMISSION_FIELDS: Tuple[str, ...] = (
    "source", "target_kind", "target_id", "claim_text",
)

# Statuses that make an obligation STANDING - the set `open_items()` folds to,
# and the set the duplicate check consults.
STANDING_STATUSES = frozenset({
    ObligationRecordType.OPEN, ObligationRecordType.DEFERRED,
})


@dataclass(frozen=True)
class AdmissionResult:
    """What admission did, returned to the caller. The RECORD is the ledger's."""
    outcome: AdmissionOutcome
    obligation_id: str
    seq: str
    rejection_kind: Optional[RejectionKind] = None
    reason: str = ""
    target_resolution: TargetResolution = TargetResolution.UNCHECKED

    @property
    def admitted(self) -> bool:
        return self.outcome is AdmissionOutcome.ADMITTED


def normalize_claim(text: Any) -> str:
    """The duplicate-detection normal form. v1 GOVERNED CONTENT.

    Case-folded, whitespace-collapsed, stripped. Deliberately NOT semantic:
    similarity matching would make admission a judgment about meaning, and a
    judgment about meaning at the front door is a selection effect entering by
    the side door (Ruling 71's finding, binding identically here).
    """
    if not isinstance(text, str):
        return ""
    return " ".join(text.casefold().split())


class ObligationLedger:
    """Append-only obligation ledger. CAE's / O1's / O3's / Q1's shape.

    THE SHAPE IS COPIED ON PURPOSE (Ruling 72's reasoning verbatim): CAE is the
    append-only store this project has ruled on five times, and writing a second
    subtly-different one would be re-deciding settled questions by accident.
    """

    ID_PREFIX = "OBL-"

    def __init__(
        self,
        ledger_path: str = "data/runtime/obligations/obligations.jsonl",
        peer_paths: Optional[Sequence[str]] = None,
        codex: Any = None,
        scar_core: Any = None,
        suspension_systems: Optional[Sequence[Any]] = None,
        ancestry_ledger: Any = None,
    ):
        # Ruling 31 / Ruling 39: an `__init__` DEFAULT under `data/runtime/` -
        # one of exactly two shapes `tests/conftest.py` and `scripts/soak.py`
        # can reach - registered in both in the same commit.
        self.ledger_path = Path(ledger_path)
        # THE SHARED CLOCK'S VISIBLE SET. Own file plus any peer given. See the
        # module docstring: the mint is monotonic over what it can SEE, and
        # wiring the pair is the constructing caller's job - there is no
        # coordinator this pass, by design.
        self.peer_paths: Tuple[Path, ...] = tuple(
            Path(p) for p in (peer_paths or ()))
        # READ-ONLY resolver handles. Any of them may be absent, and absence is
        # recorded as UNCHECKED rather than guessed at.
        self.codex = codex
        self.scar_core = scar_core
        self.suspension_systems: Tuple[Any, ...] = tuple(suspension_systems or ())
        # M3-D §1.2: the claim-ancestry ledger (Rulings 58/60), READ-ONLY.
        # Its read surface was censused before wiring: `read_all` opens mode
        # "r" and `get` folds over it - no mint, no stamp, no write. It obeys
        # this module's standing AST pin exactly as the other three resolvers do.
        self.ancestry_ledger = ancestry_ledger
        # In-memory mirror of what THIS PROCESS appended. NOT the ledger: the
        # file is the ledger. Nothing reads this back into a decision.
        self.entries: List[Dict[str, Any]] = []
        # RULING 69: THERE IS NO `self._seq`.

    # -----------------------------------------------------------------
    # THE MINT
    # -----------------------------------------------------------------

    def _clock_paths(self) -> Tuple[Path, ...]:
        return (self.ledger_path,) + self.peer_paths

    def _next_id(self) -> str:
        """Mint the next `OBL-` id, or REFUSE. Caller holds the mint lock."""
        seq = derive_max_ordinal(self.ledger_path, self.ID_PREFIX)
        if seq is None:
            raise ObligationLedgerUnreadable(
                f"the obligation ledger at '{self.ledger_path}' exists and "
                f"cannot be read, so the next {self.ID_PREFIX} ordinal is "
                f"UNKNOWN. Minting one anyway could write an id that already "
                f"names a different standing obligation.")
        return f"{self.ID_PREFIX}{seq + 1:04d}"

    # -----------------------------------------------------------------
    # THE ONLY WRITE
    # -----------------------------------------------------------------

    def _append(self, payload: Dict[str, Any]) -> None:
        """The ONLY write. Append one line.

        There is no write mode in this file at all: Ruling 78's funnel owns the
        append and the tree-wide AST census forbids a mode-`"a"` open outside
        it, so a `"w"` here would have to get past a scan rather than a reader.

        Ruling 66's writer gate runs BEFORE `mkdir` and BEFORE the append, so a
        refused entry leaves no file, no line and no directory it did not
        already need. `allow_nan=False` is the second half; `default=` is absent
        entirely, so a non-canonical leaf REFUSES rather than being silently
        stringified into a permanent record.
        """
        validate_record_value(payload, path="obligation_entry")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        durable_append_text(self.ledger_path,
                            json.dumps(payload, allow_nan=False) + "\n")
        self.entries.append(payload)

    # -----------------------------------------------------------------
    # TARGET RESOLUTION - READS ONLY
    # -----------------------------------------------------------------

    def _resolve_target(self, target_kind: Any, target_id: Any) -> TargetResolution:
        """Does this target exist? A READ. Never `retrieve`, never a write.

        See the module docstring for why `retrieve` is barred: on all three
        suspension systems it mutates the entry and calls `save_to_file()`.
        """
        if target_kind == TargetKind.DOCTRINE:
            if self.codex is None:
                return TargetResolution.UNCHECKED
            # `Codex.get` is snapshot-on-read; the fossil map is consulted
            # because an obligation may bear on a doctrine that has FALLEN.
            if self.codex.get(target_id) is not None:
                return TargetResolution.RESOLVED
            if target_id in getattr(self.codex, "fossils", {}):
                return TargetResolution.RESOLVED
            return TargetResolution.UNRESOLVED

        if target_kind == TargetKind.SCAR:
            if self.scar_core is None:
                return TargetResolution.UNCHECKED
            # Ruling 22: `get_scar` returns a DEEP COPY, so this cannot hand
            # the ledger a live record even by accident.
            if self.scar_core.get_scar(target_id) is not None:
                return TargetResolution.RESOLVED
            return TargetResolution.UNRESOLVED

        if target_kind == TargetKind.CLAIM:
            if self.ancestry_ledger is None:
                return TargetResolution.UNCHECKED
            # **A RECORDED CLAIM ALWAYS RESOLVES** - the fossil-resolves rule's
            # sibling. Claims are never erased (Ruling 58's ledger is
            # append-only and its records are permanent), so membership is the
            # whole question and there is no "was it retired" to ask.
            #
            # `get` is a pure fold over `read_all`, which opens mode "r". No
            # mutating verb is named here, exactly as `retrieve` is barred for
            # the suspension resolver.
            if self.ancestry_ledger.get(target_id) is not None:
                return TargetResolution.RESOLVED
            return TargetResolution.UNRESOLVED

        if target_kind == TargetKind.SUSPENSION:
            if not self.suspension_systems:
                return TargetResolution.UNCHECKED
            for system in self.suspension_systems:
                # MEMBERSHIP ONLY against the base class's public mapping.
                if target_id in getattr(system, "entries", {}):
                    return TargetResolution.RESOLVED
            return TargetResolution.UNRESOLVED

        return TargetResolution.UNCHECKED

    # -----------------------------------------------------------------
    # THE DOORS - externally invoked, zero internal callers
    # -----------------------------------------------------------------

    def admit(self, source: Any, target_kind: Any, target_id: Any,
              claim_text: Any) -> AdmissionResult:
        """Deterministic K2 admission. EVERY path writes a record."""
        kind_value = (target_kind.value if isinstance(target_kind, TargetKind)
                      else target_kind)

        # (1) MALFORMED - checked first, because a missing target_kind cannot
        # be resolved and a missing claim cannot be compared for duplication.
        supplied = {
            "source": source, "target_kind": kind_value,
            "target_id": target_id, "claim_text": claim_text,
        }
        missing = [name for name in REQUIRED_ADMISSION_FIELDS
                   if not isinstance(supplied[name], str) or not supplied[name].strip()]
        if not missing and kind_value not in {k.value for k in TargetKind}:
            missing = ["target_kind"]
        if missing:
            return self._reject(
                RejectionKind.MALFORMED, supplied,
                f"required field(s) missing, empty or not a string: "
                f"{', '.join(sorted(missing))}",
                TargetResolution.UNCHECKED)

        target_kind = TargetKind(kind_value)

        # (2) DUPLICATE - an OPEN or DEFERRED obligation for the same target
        # and the same normalized claim. A REJECTED one does not block.
        normalized = normalize_claim(claim_text)
        for item in self.open_items():
            if (item.get("target_kind") == target_kind.value
                    and item.get("target_id") == target_id
                    and normalize_claim(item.get("claim_text")) == normalized):
                return self._reject(
                    RejectionKind.DUPLICATE, supplied,
                    f"'{item.get('obligation_id')}' is already standing for the "
                    f"same target and the same normalized claim",
                    TargetResolution.UNCHECKED)

        # (3) TARGETLESS - resolved against what the ledger CAN SEE.
        resolution = self._resolve_target(target_kind, target_id)
        if resolution is TargetResolution.UNRESOLVED:
            return self._reject(
                RejectionKind.TARGETLESS, supplied,
                f"no {target_kind.value} '{target_id}' resolves against the "
                f"standing structures this ledger can see",
                resolution)

        with mint_lock(self.ledger_path):
            obligation_id = self._next_id()
            seq = mint_seq_token(self._clock_paths())
            self._append({
                "record_type": ObligationRecordType.OPEN.value,
                "obligation_id": obligation_id,
                "created_seq": seq,
                # RECORDED AS OBSERVATION, NEVER READ BY LOGIC. AST-pinned.
                "created_wall": datetime.now().isoformat(),
                "source": source,
                "target_kind": target_kind.value,
                "target_id": target_id,
                "claim_text": claim_text,
                "target_resolution": resolution.value,
            })
        return AdmissionResult(AdmissionOutcome.ADMITTED, obligation_id, seq,
                               target_resolution=resolution)

    def _reject(self, kind: RejectionKind, supplied: Dict[str, Any],
                reason: str, resolution: TargetResolution) -> AdmissionResult:
        """Write the REJECTED record. There is no path out of `admit` that skips this."""
        with mint_lock(self.ledger_path):
            obligation_id = self._next_id()
            seq = mint_seq_token(self._clock_paths())
            self._append({
                "record_type": ObligationRecordType.REJECTED.value,
                "obligation_id": obligation_id,
                "created_seq": seq,
                "created_wall": datetime.now().isoformat(),
                # Recorded AS IT ARRIVED - a malformed admission's fields are
                # kept verbatim so the record says what was actually asked.
                "source": supplied.get("source"),
                "target_kind": supplied.get("target_kind"),
                "target_id": supplied.get("target_id"),
                "claim_text": supplied.get("claim_text"),
                "rejection_kind": kind.value,
                "reason": reason,
                "target_resolution": resolution.value,
            })
        return AdmissionResult(AdmissionOutcome.REJECTED, obligation_id, seq,
                               rejection_kind=kind, reason=reason,
                               target_resolution=resolution)

    def defer(self, obligation_id: str, reason: Any, due_seq: Any) -> str:
        """Set a standing obligation aside, WITH a reason and a due ordinal.

        BOTH are required and neither has a default: a deferral missing either
        is not a weaker deferral, it is an abandonment with a record that says
        otherwise.
        """
        if not isinstance(reason, str) or not reason.strip():
            raise MalformedDeferral(
                f"deferring '{obligation_id}' requires a REASON. A standing "
                f"claim set aside for no recorded reason is one nobody can "
                f"later judge the setting-aside of.")
        if seq_ordinal(due_seq) is None:
            raise MalformedDeferral(
                f"deferring '{obligation_id}' requires `due_seq` as a "
                f"'{SEQ_PREFIX}NNNNNN' token; got {due_seq!r}. A deferral with "
                f"no due ordinal is indefinite, and an indefinite deferral is a "
                f"drop.")
        return self._status_record(
            ObligationRecordType.DEFERRED, obligation_id,
            {"reason": reason, "due_seq": due_seq})

    def merge(self, obligation_id: str, episode_id: str) -> str:
        """Record that this obligation was merged into an episode's work."""
        return self._status_record(
            ObligationRecordType.MERGED, obligation_id,
            {"episode_id": episode_id})

    def mark_episode_opened(self, obligation_id: str, episode_id: str) -> str:
        """Record that an episode was opened against this obligation."""
        return self._status_record(
            ObligationRecordType.EPISODE_OPENED, obligation_id,
            {"episode_id": episode_id})

    def _status_record(self, record_type: ObligationRecordType,
                       obligation_id: str, extra: Dict[str, Any]) -> str:
        with mint_lock(self.ledger_path):
            seq = mint_seq_token(self._clock_paths())
            payload = {
                "record_type": record_type.value,
                "obligation_id": obligation_id,
                "created_seq": seq,
                "created_wall": datetime.now().isoformat(),
            }
            payload.update(extra)
            self._append(payload)
        return seq

    # -----------------------------------------------------------------
    # DERIVED READS - a fold over the stream, nothing stored
    # -----------------------------------------------------------------

    def read_all(self) -> Tuple[Dict[str, Any], ...]:
        """Every readable line, IN APPEND ORDER. The history, as written.

        Reads the FILE rather than `self.entries`: the ledger spans processes
        and the in-memory mirror does not. **ERA HONESTY** - a line is returned
        AS IT WAS WRITTEN. A field a later schema added is simply absent from an
        older line; nothing is backfilled, defaulted or filtered out for missing
        it (Ruling 68's forensic law). A line that will not parse contributes
        nothing and is never coerced (floor semantics).
        """
        if not self.ledger_path.exists():
            return ()
        out: List[Dict[str, Any]] = []
        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                if isinstance(data, dict) and "obligation_id" in data:
                    out.append(data)
        return tuple(out)

    def status_of(self, obligation_id: str) -> Optional[ObligationRecordType]:
        """The CURRENT status, DERIVED by folding. Never stored (L3)."""
        status: Optional[ObligationRecordType] = None
        for record in self.read_all():
            if record.get("obligation_id") != obligation_id:
                continue
            try:
                status = ObligationRecordType(record.get("record_type"))
            except ValueError:
                continue
        return status

    def open_items(self) -> List[Dict[str, Any]]:
        """Every obligation whose derived status is STANDING (OPEN or DEFERRED).

        A pure fold: the OPEN record carries the content, later records carry
        the status, and MERGED / EPISODE_OPENED take an obligation out of the
        standing set because it is being worked rather than waiting.
        """
        opened: Dict[str, Dict[str, Any]] = {}
        status: Dict[str, ObligationRecordType] = {}
        for record in self.read_all():
            obligation_id = record.get("obligation_id")
            if not isinstance(obligation_id, str):
                continue
            try:
                record_type = ObligationRecordType(record.get("record_type"))
            except ValueError:
                continue
            if record_type is ObligationRecordType.OPEN:
                opened[obligation_id] = record
            status[obligation_id] = record_type
        return [opened[oid] for oid in opened
                if status.get(oid) in STANDING_STATUSES]
