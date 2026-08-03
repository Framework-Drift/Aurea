"""
spl.py - Symbolic Perception Layer for Aurea
Normalizes and classifies all input, producing Echo objects for downstream filtration.
"""

from src.utils.models import Echo
from datetime import datetime
from typing import Optional

class SPL:
    """
    Symbolic Perception Layer for Aurea input.
    """

    def process_input(self, raw_input: str,
                      doctrine_link: Optional[str] = None, *,
                      claim_id: Optional[str] = None) -> Echo:
        """
        Normalize raw input and wrap as an Echo object.
        Args:
            raw_input (str): The unprocessed input.
            doctrine_link (Optional[str]): ID of linked doctrine (if known).
            claim_id (Optional[str]): RULING 60 - the minted claim-ancestry id
                for this claim, KEYWORD-ONLY (mirroring 58's `origin`). The
                caller passes what the ledger RETURNED; `None` is the honest
                default for a standalone call, which mints no record and
                therefore has no id to carry.
        Returns:
            Echo: The normalized input as an Echo object.

        RULING 68 (2026-08-02): the `source` parameter is DELETED, with
        `Echo.source` and the topology tag it fed. It defaulted to `"user"` and
        wrote that into a durable store field, so every claim this layer ever
        normalized was on record as originating from a human. The claim's origin
        is the ancestry ledger, reached from `claim_id` below - and that was
        already true when this parameter still existed, which is exactly why it
        had to go rather than be documented harder.

        RULING 60: `claim_id` IS SET AT CONSTRUCTION, never by post-hoc
        mutation. An echo that acquired its linkage after the fact would have
        existed, however briefly, in a state where it was unattributable - and
        the field would then be a thing done TO the echo rather than a fact
        about how it was built.
        """
        # (Placeholder normalization - can add more logic later)
        cleaned = raw_input.strip()
        echo = Echo(
            id=f"Echo-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=cleaned,
            resonance_score=1.0,  # Placeholder score
            created_at=datetime.now(),
            doctrine_link=doctrine_link,
            claim_id=claim_id,
        )
        return echo

    def classify_intent(self, echo: Echo) -> str:
        """
        Classify input intent (stub for future expansion).
        Args:
            echo (Echo): Input echo object.
        Returns:
            str: Classified intent (e.g., 'question', 'claim', 'command').
        """
        # Placeholder: add NLP or rule-based logic later
        content = echo.content.lower()
        if content.endswith('?'):
            return 'question'
        elif content.startswith('do ') or content.startswith('please '):
            return 'command'
        else:
            return 'claim'
