"""
echonet.py - EchoNet module for Aurea
Filters input Echo objects for collapse resistance.
"""

from src.utils.models import Echo, Scar
from datetime import datetime
from typing import List

class CollapseResult:
    def __init__(self, passed: bool, tags=None, reason: str = ""):
        self.passed = passed
        self.tags = tags or []
        self.reason = reason

class EchoNet:
    """
    EchoNet: Symbolic filtration engine.
    """

    def filter_claim(self, echo: Echo) -> CollapseResult:
        """
        Filter an Echo for collapse-resistance, returns a CollapseResult object.
        """
        content = echo.content.strip()
        if len(content) < 10:
            return CollapseResult(False, tags=["too_short"], reason="Input too short")
        if content.lower().startswith("ban "):
            return CollapseResult(False, tags=["forbidden"], reason="Forbidden command")
        # Extend here with more rules or nets
        return CollapseResult(True, tags=["base_pass"])

    def collapse_test(self, echo: Echo) -> Scar:
        """
        Attempt to collapse an echo; returns a Scar object if successful.
        Args:
            echo (Echo): The echo to collapse.
        Returns:
            Scar: New scar object representing the collapse event.
        """
        # Placeholder: all passed echoes form a scar with weight based on length
        weight = min(len(echo.content) * 1.5, 100.0)
        scar = Scar(
            id=f"Δ{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            name=f"Scar from {echo.id}",  # <-- ADD THIS LINE (or use something smarter)
            origin=echo.id,
            type="unknown",  # or set from echo/logic if you have it
            weight=weight,
            created_at=datetime.now(),
            decay_state="active",
            linked_doctrines=[echo.doctrine_link] if echo.doctrine_link else [],
            description="Scar auto-generated from echo input.",
            echo_proximity=[echo.id],  # or [] if not relevant
            reflexes=[],
            tca_tags=[],
            is_seed=False
    )
        return scar
