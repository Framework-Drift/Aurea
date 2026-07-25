"""
test_codex.py - behavioral coverage for the Codex write gate (Docket M, item 2).

This file existed EMPTY through Docket K, which found that removing the
`_consumed.add()` in `Codex.commit()` - making the single-use write token
replayable - survived the whole suite. A replayable MutationAuthorization is
a write that slips past the Self-Mutation Ceiling: mint once, write forever.
Single-use is the property that keeps replay off the ceiling (Ruling 5).

One test per `_consumed.add` call site - all four:
    commit() · fossilize() target-present · fossilize() target-absent ·
    link_scar()
Each performs a real write with an SAE-minted token, then replays the SAME
token and asserts CodexWriteViolation. Reuse is attempted across DIFFERENT
write methods where natural - consumption is a property of the token in the
store, not of the method that spent it.

Real SAE, real Codex, tmp paths. DO NOT weaken; red means fix the code.
"""

from datetime import datetime

import pytest

from src.doctrine.codex import Codex, CodexWriteViolation
from src.expansion.sae import SAE, MutationClass
from src.utils.models import Doctrine


@pytest.fixture
def store(tmp_path):
    """(codex, sae) - a real executor over a real, empty, tmp-pathed store."""
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    return codex, SAE(codex=codex)


def _doctrine(doc_id: str) -> Doctrine:
    return Doctrine(id=doc_id, name=doc_id, description="test doctrine",
                    created_at=datetime.now())


def _auth(sae, lineage: str, target: str):
    """A fresh single-use token, minted by the only minter (SAE)."""
    return sae.authorize(MutationClass.MUTATE_DOCTRINE, lineage, target)


# =====================================================================
# Site 1 - commit()
# =====================================================================

def test_commit_consumes_the_token_replay_refused(store):
    codex, sae = store
    auth = _auth(sae, "Δ-1", "D-1")
    codex.commit(_doctrine("D-1"), auth)

    with pytest.raises(CodexWriteViolation):
        codex.commit(_doctrine("D-2"), auth)
    assert codex.get("D-2") is None, "the replayed write must not have landed"


# =====================================================================
# Site 2 - fossilize(), target present
# =====================================================================

def test_fossilize_consumes_the_token_replay_refused(store):
    codex, sae = store
    codex.commit(_doctrine("D-1"), _auth(sae, "Δ-1", "D-1"))

    auth = _auth(sae, "Δ-2", "D-1")
    codex.fossilize("D-1", auth, reason="collapse test")
    assert codex.get_fossil("D-1") is not None

    # Replay across a DIFFERENT write method: consumption is the token's.
    with pytest.raises(CodexWriteViolation):
        codex.commit(_doctrine("D-3"), auth)


# =====================================================================
# Site 3 - fossilize(), target absent (the write is refused-by-absence,
#          but the token is still SPENT - a miss is not a refund)
# =====================================================================

def test_fossilize_on_absent_target_still_consumes_the_token(store):
    codex, sae = store
    auth = _auth(sae, "Δ-1", "NO-SUCH")
    assert codex.fossilize("NO-SUCH", auth, reason="miss") is None

    with pytest.raises(CodexWriteViolation):
        codex.commit(_doctrine("D-1"), auth)


# =====================================================================
# Site 4 - link_scar()
# =====================================================================

def test_link_scar_consumes_the_token_replay_refused(store):
    codex, sae = store
    codex.commit(_doctrine("D-1"), _auth(sae, "Δ-1", "D-1"))

    auth = _auth(sae, "Δ-2", "D-1")
    assert codex.link_scar("D-1", "Δ-9", auth) is True
    assert "Δ-9" in codex.get("D-1").scar_links

    with pytest.raises(CodexWriteViolation):
        codex.link_scar("D-1", "Δ-10", auth)
    assert "Δ-10" not in codex.get("D-1").scar_links


# =====================================================================
# Ruling 18 + Ruling 19 (Option B) - the fallen id is permanently dead,
# and ancestry is carried forward instead of the name.
#
# THIS TEST WAS BLOCKED BY RULING during Docket M: whether revival was
# permitted at all, and whether it reused the id or minted a new one, was
# open with the architect, and no test was allowed to presume the answer.
# Ruling 19 (2026-07-25) settled it - Option B: a new id, the fallen id
# appended to `mutation_lineage`, through the ORDINARY path. No new
# mechanism, no new field, no bypass of commit()'s guard. Unblocked here.
# =====================================================================

def test_a_fossilized_id_can_never_be_recommitted(store):
    """Ruling 18, now PERMANENT under Ruling 19. Docket K proved by execution
    that before this guard a fallen doctrine could be silently revived -
    ACTIVE and FOSSIL simultaneously, durable across reload: an identity that
    came back from the dead with nothing survived behind it."""
    codex, sae = store
    codex.commit(_doctrine("D-1"), _auth(sae, "Δ-1", "D-1"))
    codex.fossilize("D-1", _auth(sae, "Δ-2", "D-1"), reason="collapsed")
    assert codex.get("D-1") is None and codex.get_fossil("D-1") is not None

    with pytest.raises(CodexWriteViolation):
        codex.commit(_doctrine("D-1"), _auth(sae, "Δ-3", "D-1"))

    assert codex.get("D-1") is None, "the fallen id is still dead"
    assert "D-1" not in codex.doctrines, "never active and fossil at once"


def test_a_successor_is_born_under_a_new_id_carrying_the_fossils_lineage(store):
    """RULING 19, OPTION B. What survives a fossilized ancestor is not its
    name - it is its ANCESTRY. The successor is a genuinely new identity, and
    the fallen id is visible in its `mutation_lineage` (the field Docket I's
    register had already earmarked for exactly this: 'supersedes/fossil_of').
    A scar does not erase and re-form identically; it accumulates as new
    structure with visible ancestry, and doctrine is treated the same way."""
    codex, sae = store
    codex.commit(_doctrine("D-1"), _auth(sae, "Δ-1", "D-1"))
    codex.fossilize("D-1", _auth(sae, "Δ-2", "D-1"), reason="collapsed")
    sae.stabilization_event("anchor_consolidation")     # a fresh epoch budget

    successor = _doctrine("D-1::reborn")
    successor.mutation_lineage = ["D-1"]                # the fossil, carried
    codex.commit(successor, _auth(sae, "Δ-3", "D-1::reborn"))

    reborn = codex.get("D-1::reborn")
    assert reborn is not None, "the ordinary birth path admits it"
    assert "D-1" in reborn.mutation_lineage, "the fossil's id is carried forward"
    assert codex.get_fossil("D-1") is not None, "the ancestor stays ⊗-archived"
    assert codex.get("D-1") is None, (
        "and 'came back' stays distinguishable from 'never fell' - the whole "
        "reason Option B was chosen over Option C")
    assert codex.lineage("D-1::reborn") == ["D-1"]
