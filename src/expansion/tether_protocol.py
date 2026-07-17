"""
tether_protocol.py - COMPATIBILITY SHIM (2026-07-08)

This module was split into src/expansion/tether/ - see that package's
__init__.py for the rationale (TetherProtocol's per-session state and
the new Prompting Autonomy Index's cumulative state are incompatible
models and were forced apart rather than bolted together).

This shim exists only so that any code importing the old flat path
(`from src.expansion.tether_protocol import TetherProtocol`) keeps
working without modification. No new code should import from here -
import from src.expansion.tether instead. Delete this shim once a
repo-wide check confirms nothing still references the old path.
"""

from src.expansion.tether.session_governor import (
    TetherProtocol,
    TetherPhase,
    TetherFence,
    TetherBudget,
    TetherPolicy,
    TetherState,
)

__all__ = [
    "TetherProtocol",
    "TetherPhase",
    "TetherFence",
    "TetherBudget",
    "TetherPolicy",
    "TetherState",
]
