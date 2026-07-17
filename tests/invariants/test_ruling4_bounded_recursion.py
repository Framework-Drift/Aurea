"""
RULING 4 — BOUNDED RECURSION. Every recursion entry point terminates.

    SBSRE loop limit:
        clamp( 3 * (scar_weight * compass_stability) / reflex_load , 1 , 5 )
        BASE CASE: on exhaustion, the SBSRE Abort Reflex fires —
                   halt recursion, store the partial thread in CSA, suppress repeats.

    RCF: already bounded in spec — recursion depth 3, Harmonizer intervention beyond.

    Self-Mutation Ceiling: 3 events per symbolic epoch across THREE counted classes —
        {mutate_doctrine, mutate_reflex, MSP module-generation authorization}

WHY THIS TEST EXISTS — AND THE TRAP IN IT
------------------------------------------
Every other guard on SBSRE is reflex-TRIGGERED: ICA on integrity breach, Anchor
Collapse past 25 degrees, CSA on saturation. All of them fire on a spike. So a
high-scar contradiction with a steady compass and an unstrained identity trips
NOTHING — and without a cycle ceiling, it grinds forever. The reflex net catches
violence, not patience. The clamp is what catches patience.

THE TRAP: AUREA is *designed* to hold things open. Suspension, the Veiled Thread,
fermentation — non-termination is CORRECT in those places, and an optimizer will
read it as a hang and "fix" it. So this test does not forbid open-endedness.
It forbids UNDECLARED open-endedness. If a loop is meant to run without resolving,
say so in the code:

    # INVARIANT: this does not resolve. Non-termination here is correct.

Anything unbounded and unmarked is a bug. Anything unbounded and marked is doctrine.
"""

from __future__ import annotations

import ast

import pytest

from tests.invariants import _ast as H

SBSRE_CANDIDATES = ("src/filtration/sbsre.py", "src/reflex/sbsre.py")
SAE_CANDIDATES = ("src/expansion/sae.py", "src/doctrine/sae.py")

# The marker that declares an intentionally unresolved loop.
HELD_OPEN_MARKER = "INVARIANT: this does not resolve"

# Ruling 4 magnitudes (see 2c SBSRE section 7.A).
EXPECTED_BASELINE, EXPECTED_FLOOR, EXPECTED_CEILING = 3, 1, 5

# The three classes the Self-Mutation Ceiling must count (5a section 10.F).
CEILING_CLASSES = ("mutate_doctrine", "mutate_reflex", "module")


def _first_existing(candidates: tuple[str, ...]):
    for relpath in candidates:
        path = H.repo_root() / relpath
        if path.exists() and not H.is_empty(path):
            return path
    return None


def test_no_undeclared_unbounded_loops() -> None:
    """`while True` with no break is fine ONLY if declared as intentionally open."""
    violations: list[H.Violation] = []

    for path in H.src_files():
        tree = H.parse(path)
        if tree is None:
            continue
        source_lines = path.read_text(encoding="utf-8").splitlines()

        for node in ast.walk(tree):
            if not isinstance(node, ast.While):
                continue
            is_while_true = isinstance(node.test, ast.Constant) and node.test.value is True
            if not is_while_true:
                continue

            has_exit = any(
                isinstance(n, (ast.Break, ast.Return, ast.Raise))
                for n in ast.walk(node)
            )
            if has_exit:
                continue

            # Unbounded. Is it *declared* unbounded?
            window = "\n".join(source_lines[max(0, node.lineno - 4) : node.lineno])
            if HELD_OPEN_MARKER in window:
                continue

            violations.append(
                H.Violation(
                    path,
                    node.lineno,
                    "`while True` with no break/return/raise and no held-open declaration",
                )
            )

    assert not violations, H.fail_message(
        ruling="Ruling 4 (bounded recursion): no UNDECLARED unbounded loop",
        violations=violations,
        remedy=(
            "Either bound the loop, or — if it is meant to stay open (suspension, "
            "Veiled Thread, fermentation) — declare it above the loop with:\n"
            f"      # {HELD_OPEN_MARKER}. Non-termination here is correct.\n"
            "  Do not silently terminate a loop AUREA is supposed to hold open."
        ),
    )


def test_sbsre_loop_limit_is_clamped() -> None:
    """SBSRE must clamp its loop limit to [1, 5] with baseline 3."""
    path = _first_existing(SBSRE_CANDIDATES)
    if path is None:
        pytest.skip(
            "SBSRE not yet implemented. When it is, it MUST clamp its loop limit "
            f"to [{EXPECTED_FLOOR}, {EXPECTED_CEILING}] with baseline {EXPECTED_BASELINE}, "
            "and fire the SBSRE Abort Reflex on exhaustion (Ruling 4)."
        )

    source = path.read_text(encoding="utf-8")
    numbers = {EXPECTED_BASELINE, EXPECTED_FLOOR, EXPECTED_CEILING}
    tree = H.parse(path)
    if tree is None:
        pytest.fail(f"Could not parse {H.rel(path)}")

    has_clamp = "clamp" in source.lower() or ("min(" in source and "max(" in source)
    found_numbers = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, int)
    }

    missing = numbers - found_numbers
    problems: list[H.Violation] = []
    if not has_clamp:
        problems.append(H.Violation(path, 0, "no clamp on the SBSRE loop limit"))
    if missing:
        problems.append(
            H.Violation(path, 0, f"missing Ruling 4 magnitudes: {sorted(missing)}")
        )

    assert not problems, H.fail_message(
        ruling="Ruling 4: SBSRE loop limit is clamped and terminating",
        violations=problems,
        remedy=(
            "loop_limit = clamp(3 * (scar_weight * compass_stability) / reflex_load, 1, 5); "
            "on exhaustion, fire the SBSRE Abort Reflex (halt, store partial thread in CSA, "
            "suppress repeats)."
        ),
    )


def test_self_mutation_ceiling_counts_three_classes() -> None:
    """The ceiling must count module-generation, not just the two mutate_* calls."""
    path = _first_existing(SAE_CANDIDATES)
    if path is None:
        pytest.skip(
            "SAE not yet implemented. When it is, the Self-Mutation Ceiling MUST count "
            "THREE classes: {mutate_doctrine, mutate_reflex, MSP module-generation}. "
            "Counting only the two mutate_* calls leaves module-generation uncapped (T4-01)."
        )

    source = path.read_text(encoding="utf-8").lower()
    missing = [c for c in CEILING_CLASSES if c not in source]

    assert not missing, H.fail_message(
        ruling="Ruling 4 / T4-01: Self-Mutation Ceiling counts THREE classes",
        violations=[
            H.Violation(path, 0, f"ceiling does not account for: {missing}")
        ],
        remedy=(
            "SAE owns the counter. Increment it on mutate_doctrine(), mutate_reflex(), "
            "AND MSP module-generation authorization. Retirement is CEILING-EXEMPT "
            "(it removes capacity, it does not run away)."
        ),
    )
