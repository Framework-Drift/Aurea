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

    def process_input(self, raw_input: str, source: str = "user", doctrine_link: Optional[str] = None) -> Echo:
        """
        Normalize raw input and wrap as an Echo object.
        Args:
            raw_input (str): The unprocessed input.
            source (str): Who/what generated the input.
            doctrine_link (Optional[str]): ID of linked doctrine (if known).
        Returns:
            Echo: The normalized input as an Echo object.
        """
        # (Placeholder normalization - can add more logic later)
        cleaned = raw_input.strip()
        echo = Echo(
            id=f"Echo-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=cleaned,
            source=source,
            resonance_score=1.0,  # Placeholder score
            created_at=datetime.now(),
            doctrine_link=doctrine_link
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
