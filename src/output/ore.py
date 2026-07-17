"""
ore.py - Output Resolution Engine for Aurea
Formats and returns system responses (for user or logging).
"""

from src.utils.models import Echo, Scar, Doctrine
from typing import Optional

class ORE:
    """
    Output Resolution Engine: Generates output responses.
    """
    def format_echo(self, echo: Echo) -> str:
        return f"[Echo] {echo.content} (id: {echo.id})"

    def format_scar(self, scar: Scar) -> str:
        return f"[Scar] Origin: {scar.origin}, Weight: {scar.weight}, Status: {scar.decay_state}"

    def format_doctrine(self, doctrine: Doctrine) -> str:
        desc = f"\n    Description: {doctrine.description}" if doctrine.description else ""
        return f"[Doctrine] {doctrine.name} (id: {doctrine.id}) - Linked scars: {doctrine.scar_links}{desc}"
