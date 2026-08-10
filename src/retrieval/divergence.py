"""
divergence.py - RULING 79 (2026-08-09): THE DISAGREEMENT IS REPORTED IN HER OWN
VOCABULARY, AND THE REPORT OBLIGATES NOTHING.

    Every store passed its own integrity check. The disagreement was BETWEEN
    them, and nothing in the tree could see it.

Registered by Ruling 78 res.4.iii. R78 made every write durable and ratified the
ordering law, which shrank cross-store divergence to the crash instants between
adjacent durable writes inside ONE event - plus whatever legacy residue already
sits in a long-lived data directory. That residue is readable, well-formed, and
invisible to every per-store check, because each store IS internally consistent.
This module reads the disagreement AT REST.

WHAT A POSITIVE OBLIGATES: A REPORT, AND NOTHING ELSE
-------------------------------------------------------------------------------
Ruled in terms, against both alternatives:

  * **QUARANTINE IS REFUSED.** Ruling 51 quarantines what cannot be
    ADJUDICATED - an unreadable constitution, where the honest answer is "I
    cannot tell what this says." A divergence is the OPPOSITE case: both files
    are readable, both are well-formed, and the surviving prefix state is one
    R78's ordering law ALREADY ADJUDICATED as honest crash residue (a crash may
    lose content against a durably spent budget; it may never hold content
    against an unspent one). Quarantining on it would re-litigate a closed
    ruling at load time.

  * **REFUSAL IS REFUSED.** Crash residue must never be fatal. A detector that
    stopped construction would convert a survived crash into an unsurvivable
    one - the process that came back to tell you what it lost, refusing to come
    back because it lost it.

  * **REPAIR IS FORBIDDEN OUTRIGHT, not deferred.** Backfilling a missing
    record fabricates history: an audit entry minted to match a mutation record,
    or a CLM line written to satisfy a scar's join, is a claim that something
    was recorded at a time when it was not (Rulings 58/70's class). **This
    module never writes to any store it reads**, and it is structurally unable
    to - see below.

WHAT THIS MODULE IS NOT (`record_joins.py`'s law, and for its reasons)
-------------------------------------------------------------------------------
  * **NOT A STORE.** It owns no file, opens none, and holds no path. Records
    arrive as ALREADY-READ collections from their owners (Ruling 63's shape,
    Ruling 63's reason: a module that opens files can be made to write one).
  * **NOT AN AUTHORITY.** It imports no SAE, Codex, CAE, scar, suspension, echo
    or ledger machinery - nothing a finding could be used to command
    (Ruling 70's enforcement-by-scope). The vocabularies it compares against
    (which CAE events are mutation classes, which ids the Codex holds, what each
    ledger's floor is) are PASSED IN by the caller, precisely so that no second
    definition of any of them is authored here.
  * **NOT A JUDGE.** A finding carries the facts read and stops. There is no
    severity, no score, no threshold, no ranking, and no advice field - nothing
    that would let a reader treat one disagreement as more actionable than
    another on this module's say-so.
  * **NOT A CACHE.** Every call is computed from what it is handed.

**STDLIB ONLY, AND THAT IS WHY THE ORDINAL IS PARSED THE WAY IT IS.** The
obvious import here is `ledger_mint.ordinal_pattern`, whose anchored regex
already solves this problem. It is deliberately NOT imported: that module opens
files, and the purity pin is what makes "never writes to any store it reads"
structural rather than promised. Re-declaring its REGEX would be a second
definition of a ruled pattern (the drift hazard this codebase keeps finding), so
neither is done - `_ordinal` instead strips a KNOWN prefix supplied by the
caller and requires the ENTIRE remainder to be digits. That is not a weaker
check than the anchored pattern, it is a stricter one: the pattern scans for an
id embedded in arbitrary text, while this validates a whole recorded field.
`CLM-00010` cannot read as `CLM-0001`, and `X-CLM-0009` matches no prefix at
all.

ERA HONESTY IS LAW
-------------------------------------------------------------------------------
**A `None` join field is ABSENT, and absence is NEVER a finding.** A scar formed
before Ruling 76, a seed scar older than every claim, a CSA quarantine with no
claim cycle behind it - each carries `None` honestly, and a detector that read
those as divergence would report the arrival of the join as a system-wide fault.
Legacy records yield zero findings, forever. That is Rulings 58/70's rule at the
read side, and it is what lets this run at every construction without drowning a
real finding in era noise.

COINS: the module name, the four `DivergenceKind` members, and
`DivergenceFinding`'s field names. No threshold, no score, no severity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import (Any, Iterable, List, Mapping, Optional, Sequence, Tuple)

__all__ = ["DivergenceKind", "DivergenceFinding", "detect_divergence"]


class DivergenceKind(str, Enum):
    """WHAT disagrees. CLOSED at four; a fifth is a manifest ruling.

    A `str` Enum by the shape rule (`RestorationOutcome`'s reasoning): ONE
    vocabulary, serialized into the report line, with no collision partner
    anywhere in the tree - all four names were censused against every enum in
    `src/` before being coined.

    Each member names a disagreement that is detectable FROM ONE SIDE WITHOUT
    GUESSING, which is the property that makes this instrument honest. None of
    them requires knowing what SHOULD have been there - only that two records
    which must agree do not.
    """

    EPOCH_COUNT_AHEAD = "epoch_count_ahead"
    """A durably spent budget exceeds the mutation records of its own epoch.

    The R78 census's central finding, at rest: `sae_epoch.json` is durable at
    the moment of SPENDING (Ruling 34), so a crash between the spend persist and
    the record persist leaves the spend visible and the record gone. The
    conservative direction, by R78's ordering law - and now the visible one.
    """

    AUDIT_WITHOUT_RECORD = "audit_without_record"
    """A CAE mutation entry that no `MutationRecord` cites.

    The ledger is written BEFORE the record it audits (Ruling 45: the record is
    a PRECONDITION for the change), so this is the same window seen from the
    other side. **Whether the target's content is PRESENT rides as a FACT, never
    as a subclass**: content-present means the mutation happened and only its
    record is missing; content-absent means it did not. Two different worlds,
    one finding kind, both facts on the record - because splitting them into two
    kinds would make this module adjudicate which world it is in.
    """

    UNRESOLVED_JOIN = "unresolved_join"
    """A recorded `claim_id` that resolves to no line in the ancestry ledger.

    Ruling 76's joins read as an integrity check. The citing record is durable
    and names a perception whose own CLM line never landed - so the thread
    Ruling 60 follows runs off the end of the record.
    """

    REFERENCED_ABOVE_FLOOR = "referenced_above_floor"
    """A cited id whose ordinal sits above its own ledger's derived floor.

    **THE REBORN-ID HAZARD'S AT-REST SIGNATURE.** R78 could not honestly
    simulate page-cache loss in-process and said so rather than faking the
    mechanism; this is the alternative it named. A durable record cites
    `CLM-0009` while the ancestry ledger's floor derives to 7, so the mint will
    reissue 8 and 9 to different perceptions while this record still points at
    them. Detected without simulating anything: the two numbers simply disagree.
    """


@dataclass(frozen=True)
class DivergenceFinding:
    """One disagreement, and the facts that establish it. EPHEMERAL.

    Frozen, and the facts mapping is frozen with it - a finding is a reading
    taken at one instant, and a mutable one could be edited between being
    reported and being read (Rulings 33/52's shape, applied to the smallest
    record in the tree).

    **NO SEVERITY, NO SCORE, NO ADVICE.** `facts` carries what was READ - two
    numbers, an id, a presence boolean - and never an opinion about what it
    means. §9's standing bar #5 at a new surface: a magnitude here would be a
    coined threshold at the exact point somebody decides whether to act.
    """

    kind: DivergenceKind
    citing_store: str
    cited_id: Optional[str]
    facts: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "facts", MappingProxyType(dict(self.facts)))

    def as_dict(self) -> dict:
        """The report line's payload. Plain types only.

        The caller serializes and validates (Ruling 78's division: the site owns
        its `json.dumps`, its `validate_record_value` and its `allow_nan=False`).
        This hands over canonical values and nothing else.
        """
        return {
            "kind": self.kind.value,
            "citing_store": self.citing_store,
            "cited_id": self.cited_id,
            "facts": dict(self.facts),
        }


def _ordinal(recorded_id: Any, prefix: str) -> Optional[int]:
    """The ordinal of `recorded_id` under `prefix`, or `None` if it is not one.

    WHOLE-FIELD VALIDATION, not a scan - see the module docstring for why this
    does not import `ordinal_pattern`. The entire remainder after the prefix
    must be digits, so a malformed or foreign id yields `None` and contributes
    nothing rather than being partially read.
    """
    if not isinstance(recorded_id, str) or not recorded_id.startswith(prefix):
        return None
    tail = recorded_id[len(prefix):]
    if not tail.isdigit():
        return None
    return int(tail)


def _recorded_claim(record: Any) -> Optional[str]:
    """A record's recorded `claim_id`, or `None`.

    ERA HONESTY AT ITS SINGLE READ POINT. Everything absent - a missing
    attribute, an explicit `None`, an empty string - returns `None` here and is
    dropped by every caller below. Concentrating it in one function is what
    makes "a `None` join is never a finding" checkable rather than distributed
    across four loops.
    """
    value = getattr(record, "claim_id", None)
    if isinstance(value, str) and value:
        return value
    return None


def _record_id(record: Any) -> Optional[str]:
    """The citing record's own id, for the finding to point back at."""
    value = getattr(record, "id", None)
    return value if isinstance(value, str) and value else None


def _epoch_count_ahead(sae_state: Optional[Mapping[str, Any]]
                       ) -> List[DivergenceFinding]:
    """A durably spent budget against records that are not there."""
    if not sae_state:
        return []
    epoch = sae_state.get("epoch")
    spent = sae_state.get("epoch_count")
    if not isinstance(spent, int) or not isinstance(epoch, int):
        return []

    history = sae_state.get("history") or ()
    in_epoch = sum(1 for record in history
                   if isinstance(record, Mapping) and record.get("epoch") == epoch)
    if spent <= in_epoch:
        return []
    return [DivergenceFinding(
        kind=DivergenceKind.EPOCH_COUNT_AHEAD,
        citing_store="sae_epoch",
        cited_id=None,
        facts={"epoch": epoch, "epoch_count": spent,
               "records_in_epoch": in_epoch},
    )]


def _audit_without_record(cae_entries: Sequence[Any],
                          sae_state: Optional[Mapping[str, Any]],
                          mutation_events: frozenset,
                          codex_ids: frozenset) -> List[DivergenceFinding]:
    """A mutation audit entry that no record cites.

    `mutation_events` ARRIVES FROM THE CALLER and is not declared here. The
    vocabulary belongs to `MutationClass`, and a copy of it in this module would
    be a second definition free to drift - silently, because both would look
    right alone. DEE's own audit events (`dee_ferment`, `dee_rejection`, and the
    rest) are correctly outside the set: they audit a DECISION, and no
    `MutationRecord` was ever supposed to cite them.
    """
    if not cae_entries:
        return []
    history = (sae_state or {}).get("history") or ()
    cited = {record.get("cae_id") for record in history
             if isinstance(record, Mapping)}

    findings: List[DivergenceFinding] = []
    for entry in cae_entries:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("event") not in mutation_events:
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or entry_id in cited:
            continue
        target = entry.get("target")
        findings.append(DivergenceFinding(
            kind=DivergenceKind.AUDIT_WITHOUT_RECORD,
            citing_store="cae",
            cited_id=entry_id,
            # A FACT, NEVER A SUBCLASS (res.3). Present means the mutation
            # happened and lost only its record; absent means it did not happen.
            # Both are reported the same way and neither is decided here.
            facts={"event": entry.get("event"), "target": target,
                   "target_content_present": target in codex_ids},
        ))
    return findings


def _unresolved_joins(sources: Sequence[Tuple[str, Iterable[Any]]],
                      claim_ids: frozenset) -> List[DivergenceFinding]:
    """Durable joins whose target line never landed."""
    findings: List[DivergenceFinding] = []
    for store_name, records in sources:
        for record in (records or ()):
            claim_id = _recorded_claim(record)
            if claim_id is None or claim_id in claim_ids:
                continue
            findings.append(DivergenceFinding(
                kind=DivergenceKind.UNRESOLVED_JOIN,
                citing_store=store_name,
                cited_id=claim_id,
                facts={"citing_record_id": _record_id(record)},
            ))
    return findings


def _referenced_above_floor(sources: Sequence[Tuple[str, Iterable[Any]]],
                            sae_state: Optional[Mapping[str, Any]],
                            floors: Mapping[str, Optional[int]],
                            claim_prefix: str,
                            audit_prefix: str) -> List[DivergenceFinding]:
    """Cited ids sitting above the floor their own ledger derives.

    An UNDERIVED floor (`None` - the file exists and could not be read) yields
    NOTHING. Ruling 53's sentinel, honoured at the read side: "what is here is
    unknown" is not the same as "the floor is zero", and comparing against an
    invented number would report every id in the tree as reborn.
    """
    findings: List[DivergenceFinding] = []

    def _check(store_name: str, cited: Any, prefix: str) -> None:
        floor = floors.get(prefix)
        if floor is None:
            return
        ordinal = _ordinal(cited, prefix)
        if ordinal is None or ordinal <= floor:
            return
        findings.append(DivergenceFinding(
            kind=DivergenceKind.REFERENCED_ABOVE_FLOOR,
            citing_store=store_name,
            cited_id=cited,
            facts={"prefix": prefix, "ordinal": ordinal, "floor": floor},
        ))

    for store_name, records in sources:
        for record in (records or ()):
            claim_id = _recorded_claim(record)
            if claim_id is not None:
                _check(store_name, claim_id, claim_prefix)

    for record in ((sae_state or {}).get("history") or ()):
        if isinstance(record, Mapping) and record.get("cae_id"):
            _check("sae_epoch", record.get("cae_id"), audit_prefix)

    return findings


def detect_divergence(*,
                      sae_state: Optional[Mapping[str, Any]] = None,
                      cae_entries: Sequence[Any] = (),
                      scars: Iterable[Any] = (),
                      suspensions: Iterable[Any] = (),
                      echoes: Iterable[Any] = (),
                      claim_ids: Iterable[str] = (),
                      codex_ids: Iterable[str] = (),
                      mutation_events: Iterable[str] = (),
                      floors: Optional[Mapping[str, Optional[int]]] = None,
                      claim_prefix: str = "CLM-",
                      audit_prefix: str = "CAE-",
                      ) -> Tuple[DivergenceFinding, ...]:
    """Every disagreement visible in what was handed over. Reads no file.

    THE CALLER READS THE STORES AND PASSES WHAT IT READ, including the three
    vocabularies this module refuses to author itself: `claim_ids` (the ancestry
    ledger's own lines), `codex_ids` (live plus fossil), and `mutation_events`
    (the `MutationClass` values). `floors` maps a ledger prefix to the ordinal
    `derive_max_ordinal` returned for it - `None` for an underived floor, which
    is honoured as "unknown" rather than as zero.

    **DETERMINISTIC: the same inputs produce the same findings in the same
    order.** The order is KIND-MAJOR in `DivergenceKind` declaration order, then
    by `(citing_store, cited_id)` within a kind, with ties left in the order the
    caller supplied the records. It is a stable presentation and NOT a ranking:
    kind order is the order they were declared, not an order of importance, and
    nothing here believes an `EPOCH_COUNT_AHEAD` matters more than an
    `UNRESOLVED_JOIN`. Determinism is required because the report is appended to
    a permanent log and two runs over one unchanged world must not produce two
    different records of it.
    """
    floors = floors or {}
    claim_id_set = frozenset(c for c in claim_ids if isinstance(c, str))
    codex_id_set = frozenset(c for c in codex_ids if isinstance(c, str))
    event_set = frozenset(e for e in mutation_events if isinstance(e, str))

    # Materialized once: a caller may hand over generators, and three passes
    # over an exhausted one would silently read as an empty store.
    sources: List[Tuple[str, Iterable[Any]]] = [
        ("scars", tuple(scars)),
        ("suspensions", tuple(suspensions)),
        ("echoes", tuple(echoes)),
    ]

    findings: List[DivergenceFinding] = []
    findings.extend(_epoch_count_ahead(sae_state))
    findings.extend(_audit_without_record(tuple(cae_entries), sae_state,
                                          event_set, codex_id_set))
    findings.extend(_unresolved_joins(sources, claim_id_set))
    findings.extend(_referenced_above_floor(sources, sae_state, floors,
                                            claim_prefix, audit_prefix))

    order = {kind: index for index, kind in enumerate(DivergenceKind)}
    findings.sort(key=lambda f: (order[f.kind], f.citing_store,
                                 f.cited_id or ""))
    return tuple(findings)
