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
M3-D NOTE (2026-08-14): the loop described above now lives in
`aurea_core._carry_contradiction`, driven by the episode record; SBSRE's
decision path is RETIRED and this file's target - `clamp` /
`compute_loop_limit`, the bound DERIVATION - stands in place, which is why
census sec 4 records invariants 13, 14 and 22 as unmoved. The base case still
fires the Abort Reflex on exhaustion; only the caller moved.

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


def test_sbsre_clamp_magnitudes_smoke_check() -> None:
    """SMOKE CHECK ONLY - this is NOT the guard (Docket M, item 1).

    This test verifies only that the words 'clamp'/'min('/'max(' and the Ruling 4
    magnitudes 1/3/5 appear in the SBSRE source text - a did-you-forget-entirely
    tripwire. Docket K proved it is blind to a disabled bound: replacing
    `min(ceiling, value)` with `max(ceiling, value)` removes the ceiling entirely
    and this test stays green, because the tokens still exist in the file.

    The GUARD is test_sbsre_clamp_binds_at_runtime below, which calls clamp()
    and compute_loop_limit() and asserts on their RETURN VALUES. Do not treat
    this lexical check as evidence the bound binds.
    """
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


def test_sbsre_clamp_binds_at_runtime() -> None:
    """THE GUARD (Docket M, item 1 - closing Docket K's survived mutant).

    Ruling 4's entire termination argument is that `loop_limit` enters the loop
    already bounded to [FLOOR, CEILING] and only ever decreases. Docket K showed
    the previous test never CALLED the bound - the ceiling could be deleted
    (`min` -> `max`) with the suite green. This test executes the bound:

      - clamp() returns CEILING for any value above it, FLOOR for any below it,
        in both directions and at the boundaries;
      - compute_loop_limit() under the pathological input Ruling 4 exists for -
        near-zero reflex_load driving the raw formula toward infinity - still
        returns <= CEILING;
      - corrupt (non-finite) input returns FLOOR, not the ceiling: a system that
        cannot tell how heavy a contradiction is must not grant itself MORE time
        to grind on it.

    All magnitudes referenced are the Ruling 4 canon set (1/3/5) already pinned
    at the top of this file - nothing here is coined.

        ~~"Ruling 4's entire termination argument is that `loop_limit` enters
          the loop already bounded to [FLOOR, CEILING] and only ever
          decreases."~~

    **MIGRATED 2026-08-14 (M3-D retirement), old sentence struck above, every
    ASSERTION BELOW UNCHANGED.** `M3_D_CENSUS.md` sec 4 for this invariant:
    *"RETAINED while SBSRE stands (C3) ... At decision-path retirement:
    Ruling-14 migration, old/new verbatim."*

    THE SUBJECT IS UNMOVED AND SO IS THE TARGET: `clamp` and
    `compute_loop_limit` are the BOUND DERIVATION (census S1) and they survive
    the retirement in place, which is why census sec 4 records invariants 13 and
    22 as UNMOVED too - all three still execute against the same functions.

    WHAT MOVED IS WHERE THE BOUND IS SPENT. There is no `loop_limit` any more:
    the value this test clamps is now declared at `open_episode` and FIXED
    there, and the loop that honors it is the caller's. **The episode-open bind
    - the clamp value actually reaching `open_episode` - is pinned as B1 in
    `tests/test_m3d_episode_path.py::test_b_the_recorded_bound_is_the_clamp_value`**,
    which also re-asserts `FLOOR <= bound <= CEILING` on the recorded value. The
    constitutional twin (the store's `>=` forcing at the bound) is pinned in
    `tests/test_m3a.py`. This invariant keeps the half it can execute from
    source: that the derivation itself cannot be reasoned past.
    """
    path = _first_existing(SBSRE_CANDIDATES)
    if path is None:
        pytest.skip("SBSRE not yet implemented - converts to a live check when it is.")

    from src.reflex.sbsre import CEILING, FLOOR, clamp, compute_loop_limit

    assert FLOOR == EXPECTED_FLOOR and CEILING == EXPECTED_CEILING, (
        "Ruling 4 magnitudes moved - that requires a manifest ruling, not an edit"
    )

    # The bound, exercised in both directions and at its own edges.
    assert clamp(10_000.0) == CEILING, "a huge value must return the CEILING"
    assert clamp(CEILING + 1) == CEILING
    assert clamp(CEILING) == CEILING
    assert clamp(FLOOR) == FLOOR
    assert clamp(FLOOR - 1) == FLOOR, "a below-floor value must return the FLOOR"
    assert clamp(-10_000.0) == FLOOR
    assert clamp(3.0) == 3, "an in-range value passes through unclamped"

    # The pathological case: near-zero reflex load sends the raw formula toward
    # infinity. The clamp is what stands between that and an unbounded grinder.
    runaway = compute_loop_limit(
        scar_weight=1_000_000.0, compass_stability=1.0, reflex_load=1e-9)
    assert runaway <= CEILING, (
        "near-zero reflex_load must NOT grant more than CEILING passes - "
        "the quiet grinder is back")
    assert runaway >= FLOOR

    # Corrupt input gets the FLOOR, not the ceiling (naive clamping returns
    # the ceiling for NaN - that is backwards, and pinned here).
    assert compute_loop_limit(float("nan"), 1.0, 1.0) == FLOOR
    assert compute_loop_limit(1.0, float("inf"), 1.0) == FLOOR


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
