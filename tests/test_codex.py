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
