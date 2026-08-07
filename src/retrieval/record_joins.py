"""
record_joins.py - RULING 76 res.5 (2026-08-05): RETRIEVAL IS THE JOINS READ
THE OTHER WAY.

    A claim id is the thread. Follow it, and you have the records. Anything
    beyond following it is inference wearing retrieval's clothes.

Docket item 9, and it is deliberately the smallest module in this tree that
could answer the question. Ruling 76 added `claim_id` to the scar and
suspension records so the topology could DERIVE its event edges; the same joins
read from the other end are retrieval, and nothing else is needed to make them
so.

**ID JOINS ONLY. THIS IS THE WHOLE CONTRACT AND IT IS PERMANENT.**
-------------------------------------------------------------------------------
No similarity. No ranking. No score. No content matching. No embedding, no
vector, no distance, no threshold, no "top k". A record is returned because its
recorded `claim_id` EQUALS the one asked for, or it is not returned.

**CONTENT-SIMILARITY RETRIEVAL IS FOREVER OUTSIDE THE TRUTH PATH**, per the
BARs, and this module is inside it. The reason is not squeamishness: a
similarity ranker decides which evidence a later stage ever sees, which is a
selection effect, which is an epistemic effect entering by the side door -
Ruling 71's finding at the goal layer, and it binds identically here. A
candidate-generation surface that ranks by similarity may become legitimate in
the Foundry era, OUTSIDE the truth path, THROUGH ITS OWN RULING. It does not
become legitimate by being convenient.

The same reasoning already rejected content-matching as the way to rebuild the
event edges (Ruling 76's grounding): matching a suspension to an echo by their
text is the lexical-similarity defect class, and it is why the JOIN was added
to the record instead.

WHAT THIS MODULE IS NOT
-------------------------------------------------------------------------------
  * NOT A STORE. It owns no file, opens nothing, and writes nothing. Records
    arrive as ALREADY-READ collections from their owners (Ruling 63's shape,
    Ruling 63's reason: a module that opens files can be made to write one).
  * NOT AN AUTHORITY. It imports no SAE, Codex, RACM, reflex, expression or
    goal machinery - nothing a retrieval answer could be used to command
    (Ruling 70's enforcement-by-scope).
  * NOT A CACHE. Every call is computed from what it is handed. There is no
    index, no memo, no stored projection - Ruling 63 refused a cached
    projection and Ruling 65 refused a stored derivation, and a retrieval index
    is both at once.
  * NOT AN INTERPRETER. It reports what the records say. A record with `None`
    is ABSENT, and absence is a real answer (Rulings 58/70) - never a prompt to
    guess.

COINS: nothing. No enum, no threshold, no score, and no field.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence, Tuple

__all__ = ["ClaimRecords", "records_for_claim", "claim_of_scar",
           "claim_of_suspension", "claims_present"]


@dataclass(frozen=True)
class ClaimRecords:
    """Every record carrying one `claim_id`. EPHEMERAL - computed, never stored.

    Frozen, and with NO serialization surface on purpose: a persisted retrieval
    result is a stored derivation, which is the structure Ruling 65 refused at
    the topology and Ruling 63 refused at the projection. Ask again; the records
    are the truth.

    **THE FIELDS ARE RECORDS, NOT RANKINGS.** They arrive in the order their
    owners hold them - append order for the echo log, store order for scars and
    suspensions - and that order carries no meaning beyond "this is how they
    were written". Nothing here sorts by relevance, because nothing here
    computes relevance.
    """

    claim_id: str
    echoes: Tuple[Any, ...] = ()
    scars: Tuple[Any, ...] = ()
    suspensions: Tuple[Any, ...] = ()

    @property
    def is_empty(self) -> bool:
        """True when no record carries this claim id.

        A legitimate answer, not a failure: the id may predate the joins
        (Ruling 76 backfills nothing), or name a claim that produced no scar and
        no suspension - which is the ordinary case for a claim that simply
        resolved.
        """
        return not (self.echoes or self.scars or self.suspensions)


def _matching(records: Optional[Iterable[Any]], claim_id: str) -> Tuple[Any, ...]:
    """Records whose recorded `claim_id` EQUALS `claim_id`.

    EXACT STRING EQUALITY on a house-minted id, and nothing else. No prefix
    match, no normalization, no case folding: Ruling 60 res.3 settled this for
    the ancestry ledger's own ids and the reasoning transfers unchanged -
    `CLM-0001` must never graze `CLM-00010`.

    A record that does not carry the attribute at all is skipped rather than
    raising. This module reads across three different record types written by
    three different owners, and a legacy record simply has nothing to say.
    """
    if records is None:
        return ()
    return tuple(record for record in records
                 if getattr(record, "claim_id", None) == claim_id)


def records_for_claim(claim_id: str, *,
                      echoes: Optional[Iterable[Any]] = None,
                      scars: Optional[Iterable[Any]] = None,
                      suspensions: Optional[Iterable[Any]] = None
                      ) -> ClaimRecords:
    """Every record carrying `claim_id`, across the three record types.

    THE CALLER READS THE STORES AND PASSES WHAT IT READ - this module never
    opens one (see the module docstring). In practice:

        records_for_claim("CLM-0007",
                          echoes=core.echo_memory.read_all(),
                          scars=core.scar_core.all_scars(),
                          suspensions=core.black_sphere.entries.values())

    Any collection may be omitted, and omitting one is not the same as it being
    empty - the result simply carries nothing from a store nobody read. That
    distinction is the caller's to keep; this module does not pretend to know
    which stores exist.

    **THE ECHO SIDE IS ONE-TO-ONE BY RULING 75'S GUARANTEE** (one ECH line per
    claim cycle), so `echoes` will hold at most one record for a real claim id.
    It is returned as a TUPLE anyway rather than a single value: a legacy log
    could hold anything, and a retrieval surface that silently returned the
    "first" of several would be adjudicating by list order (Ruling 64 res.5's
    refused class).
    """
    if not isinstance(claim_id, str) or not claim_id:
        raise ValueError(
            "a claim id is a non-empty recorded string. Retrieval follows a "
            "recorded thread; there is nothing to follow from an absent one.")
    return ClaimRecords(
        claim_id=claim_id,
        echoes=_matching(echoes, claim_id),
        scars=_matching(scars, claim_id),
        suspensions=_matching(suspensions, claim_id),
    )


def claim_of_scar(scar: Any) -> Optional[str]:
    """The claim a scar descends from, or `None`.

    THE OTHER DIRECTION OF THE SAME JOIN, and the one the docket registered as
    "a scar's claim ancestry". It is a single attribute read, and it should stay
    that cheap: the whole point of recording the join at creation is that
    nothing downstream has to reconstruct it.

    `None` is ABSENT and means exactly that - a scar formed before Ruling 76, a
    seed scar older than every claim, or one formed outside `process_input`.
    **It is never a prompt to infer.** With the id in hand a caller reaches the
    ancestry ledger for the origin itself; this module does not, because that
    would make it a reader of a fourth store.
    """
    return getattr(scar, "claim_id", None)


def claim_of_suspension(entry: Any) -> Optional[str]:
    """The claim a suspension descends from, or `None`. The same read.

    Only Black Sphere suspensions from the pipeline carry one today (Ruling 76
    res.1). A CSA quarantine, a Veiled Thread fermentation and every tether
    suspension carry `None`, honestly - they have no claim cycle behind them.
    """
    return getattr(entry, "claim_id", None)


def claims_present(records: Optional[Iterable[Any]]) -> List[str]:
    """The distinct recorded claim ids in a collection, in first-seen order.

    A read over what is there, for a caller that wants to walk the joins rather
    than ask about one it already knows. **Records with no claim id contribute
    NOTHING and are not counted** - this returns the ids that were recorded, and
    a count of absences would be a different question about a different thing.

    FIRST-SEEN ORDER, deduplicated - the order the records were written in, and
    explicitly not a ranking. Deterministic so a caller can rely on it without
    anything here having formed an opinion about importance.
    """
    seen: List[str] = []
    for record in (records or ()):
        claim_id = getattr(record, "claim_id", None)
        if isinstance(claim_id, str) and claim_id and claim_id not in seen:
            seen.append(claim_id)
    return seen
