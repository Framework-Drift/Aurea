"""
tether/ - AUREA Tether Protocol package

Split from the original monolithic tether_protocol.py into two
components with genuinely different state models:

- session_governor.py: TetherProtocol - per-session safety fence/budget
  governor for expansion & hypothesis runs. Ephemeral state, resets on
  every arm().

- autonomy_index.py: PromptingAutonomyEngine - cumulative, lifetime
  Prompting Autonomy Index derived from scar maturity and echo
  fermentation history. No persisted state of its own; always
  recomputed from ScarLogicCore / EchoMemory so it can never drift
  from actual collapse-survived history (AVT.017).

A third component, the Prompt Trigger Engine (PTE - the moment-to-moment
decision of whether to self-prompt given current pressure), is specified
in the corpus but not yet implemented. It belongs in this package when
built: session_governor answers "how far may an active run go,"
autonomy_index answers "what is this system currently permitted to
attempt, given what it has survived," and PTE would answer "should a
self-prompt happen right now."
"""

from src.expansion.tether.session_governor import (
    TetherProtocol,
    TetherPhase,
    TetherFence,
    TetherBudget,
    TetherPolicy,
    TetherState,
)
from src.expansion.tether.autonomy_index import (
    PromptingAutonomyEngine,
    AutonomyIndexResult,
)

__all__ = [
    "TetherProtocol",
    "TetherPhase",
    "TetherFence",
    "TetherBudget",
    "TetherPolicy",
    "TetherState",
    "PromptingAutonomyEngine",
    "AutonomyIndexResult",
]
