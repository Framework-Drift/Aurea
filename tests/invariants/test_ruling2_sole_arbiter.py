"""
RULING 2 — SOURCE vs SOLE ARBITER. Authority is one-way.

    Reflex Grid  = REGISTRY. It houses and enumerates reflexes. It routes them.
                   It does NOT decide which one wins.
    RACM         = SOLE ARBITER. Priority, suppression, deferral, lockout.
                   It never originates a reflex.

The same shape governs prompt origination:
    SPS / Nova / EchoCore = originators.   PTE = pure gate; originates nothing.

KNOWN FAILING AS OF 2026-07-11 — THIS IS CORRECT, DO NOT "FIX" THE TEST
-----------------------------------------------------------------------
src/reflex/racm.py is 0 bytes, while src/reflex/reflex_grid.py declares itself
"Central reflex arbitration system", holds `self.arbitration_lock`, and defines
`_arbitrate_reflexes()`. The Grid is currently doing RACM's job.

That is the exact drift this ruling exists to prevent, and it was already in the
codebase before any of these tests were written. The remedy is to MOVE the
arbitration into RACM — not to relax the test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.invariants import _ast as H

RACM_PATH = "src/reflex/racm.py"

# Narrow on purpose. The Grid legitimately STORES a priority value on each
# reflex (registry data) and each reflex legitimately returns its own response
# (e.g. action="suppress"). Neither is arbitration. Arbitration is *choosing
# between competing reflexes* — so we flag only that.
ARBITRATION_NEEDLES = ("arbitrat",)


def _racm_file() -> Path:
    return H.repo_root() / RACM_PATH


def test_racm_exists_as_the_arbiter() -> None:
    """RACM must exist and define the arbiter. An absent arbiter means the
    arbitration is living somewhere it does not belong."""
    path = _racm_file()
    assert path.exists(), H.fail_message(
        ruling="Ruling 2: RACM is the sole reflex arbiter",
        violations=[H.Violation(path, 0, "src/reflex/racm.py does not exist")],
        remedy="Create RACM as the sole arbiter of reflex priority/suppression/deferral.",
    )

    if H.is_empty(path):
        pytest.fail(
            H.fail_message(
                ruling="Ruling 2: RACM is the sole reflex arbiter",
                violations=[H.Violation(path, 0, "racm.py is an empty stub — no arbiter exists")],
                remedy=(
                    "Implement RACM. Move `_arbitrate_reflexes()` and `arbitration_lock` "
                    "out of ReflexGrid and into RACM. The Grid keeps registration, "
                    "enumeration, and routing only."
                ),
            )
        )

    tree = H.parse(path)
    assert tree is not None and H.defines_class(tree, "RACM"), H.fail_message(
        ruling="Ruling 2: RACM is the sole reflex arbiter",
        violations=[H.Violation(path, 0, "racm.py does not define a class named RACM")],
        remedy="Define `class RACM` as the sole arbiter.",
    )


def test_arbitration_lives_only_in_racm() -> None:
    """No module but RACM may define arbitration logic."""
    violations: list[H.Violation] = []

    for path in H.src_files():
        if H.rel(path) == RACM_PATH:
            continue
        tree = H.parse(path)
        if tree is None:
            continue
        for lineno, name in H.find_defs_matching(tree, ARBITRATION_NEEDLES):
            violations.append(
                H.Violation(path, lineno, f"defines arbitration logic: `{name}()`")
            )

    assert not violations, H.fail_message(
        ruling="Ruling 2: RACM is the SOLE arbiter; every other module is a source",
        violations=violations,
        remedy=(
            "Move this arbitration into RACM (src/reflex/racm.py). A source module "
            "may raise/route a reflex; only RACM decides which reflex wins."
        ),
    )
