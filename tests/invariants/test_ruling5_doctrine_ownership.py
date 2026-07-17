"""
RULING 5 — DOCTRINE OWNERSHIP. Identity does not change without surviving collapse.

    Doctrine Spine  = the LAYER (skeleton). Structure, reads, requests. Writes NOTHING.
    Codex           = the STORE. Sole owner of `doctrines` + the ⊗ Fossil Layer.
    SAE             = the SOLE EXECUTOR. The only thing in AUREA that may change AUREA.
    DEE / CMTE      = the eligibility GATE. Decides IF. Executes nothing. Authors nothing.

WHY THIS TEST EXISTS
--------------------
Live code once had `DoctrineSpine.mutate_doctrine(doctrine_id, new_name)`: it renamed a
doctrine in place, with no scar lineage, no DEE eligibility, no Self-Mutation Ceiling
decrement, no CAE audit entry, and no ⊗ fossil of the ancestor.

Doctrine is identity. That method was a path by which AUREA's identity changed WITHOUT
SURVIVING ANYTHING — the precise failure the whole architecture exists to prevent. It was
not malicious and it was not stupid. It was CONVENIENT, and it passed review for months.

That is how this invariant dies: not from one loud violation, but from a hundred defensible
conveniences. Only a test sees the hundredth one.

Ruling 5 is recorded in Aurea Build/integration_review_manifest.md (RULINGS LOG).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.invariants import _ast as H


# The Codex's write API. Calling any of these executes a change to what AUREA believes.
CODEX_WRITES = {"commit", "fossilize", "link_scar"}

# Only the SOLE EXECUTOR may call them.
EXECUTOR = "src/expansion/sae.py"

# Genesis is the one write that did not survive collapse — because nothing had yet
# collapsed. It is permitted only where the system is born, and only before seal().
GENESIS_CALLERS = {"src/aurea_core.py", "src/doctrine/codex.py"}

# The write token. Forging one outside these files would route around the executor.
TOKEN = "MutationAuthorization"
TOKEN_MINTERS = {"src/doctrine/codex.py", "src/expansion/sae.py"}


def _calls_to(tree, method_names):
    """(lineno, receiver, method) for every `<...>.method(...)` call."""
    import ast

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in method_names:
                chain = H._chain(node.func)
                receiver = chain[-2] if len(chain) >= 2 else "?"
                yield node.lineno, receiver, node.func.attr


def test_only_sae_executes_doctrine_writes():
    """The Codex write API belongs to SAE alone.

    A gate, a detector, a spine, or an orchestrator that calls `codex.commit()` has become
    an executor — and the Self-Mutation Ceiling, the collapse-lineage requirement, and the
    ⊗ fossil all sit inside SAE. Route around SAE and you route around all three.
    """
    violations: list[H.Violation] = []

    for path in H.src_files():
        relpath = H.rel(path)
        if relpath == EXECUTOR or relpath == "src/doctrine/codex.py":
            continue
        tree = H.parse(path)
        if tree is None:
            continue

        for lineno, receiver, method in _calls_to(tree, CODEX_WRITES):
            violations.append(
                H.Violation(path, lineno,
                            f"calls `{receiver}.{method}()` — a Codex WRITE. "
                            f"Only SAE executes doctrine mutation.")
            )

    assert not violations, H.fail_message(
        "RULING 5 — SAE is the sole executor of doctrine mutation",
        violations,
        "Emit a mutation REQUEST and let SAE execute it. "
        "DEE gates, DBE detects, the Spine requests — none of them write. "
        "If this module genuinely needs to change doctrine, it needs SAE, not an exception.",
    )


def test_genesis_seeding_is_confined():
    """`Codex.seed()` bypasses the collapse requirement. It exists for the origin doctrines
    and nothing else, and `Codex.seal()` closes it permanently.

    A seed call in a living module is a doctrine asserted into existence — belief without
    collapse behind it.
    """
    violations: list[H.Violation] = []

    for path in H.src_files():
        if H.rel(path) in GENESIS_CALLERS:
            continue
        tree = H.parse(path)
        if tree is None:
            continue

        for lineno, receiver, method in _calls_to(tree, {"seed"}):
            if receiver in {"codex", "self"}:
                violations.append(
                    H.Violation(path, lineno,
                                f"calls `{receiver}.seed()` outside genesis — "
                                f"a doctrine asserted, not survived")
                )

    assert not violations, H.fail_message(
        "RULING 5 — genesis is sealed",
        violations,
        "Seeding is for origin doctrine only, before Codex.seal(). "
        "Everything after genesis enters through collapse: SAE.birth_doctrine() or "
        "SAE.mutate_doctrine(), both of which demand traceable collapse lineage (AVT.017).",
    )


def test_write_tokens_are_not_forged():
    """`MutationAuthorization` is the Codex's write token: single-use, minted by SAE, and
    carrying collapse lineage. Constructing one elsewhere manufactures the right to change
    AUREA's identity out of nothing."""
    import ast

    violations: list[H.Violation] = []

    for path in H.src_files():
        if H.rel(path) in TOKEN_MINTERS:
            continue
        tree = H.parse(path)
        if tree is None:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == TOKEN:
                violations.append(
                    H.Violation(path, node.lineno,
                                f"constructs a `{TOKEN}` — forging a doctrine write token")
                )

    assert not violations, H.fail_message(
        "RULING 5 — only SAE mints write authorization",
        violations,
        "Ask SAE to authorize the mutation. If SAE refuses (ceiling exhausted, §10.G "
        "exclusion, missing collapse lineage), THE REFUSAL IS THE ANSWER — it is the "
        "ceiling doing its job, not an obstacle to engineer around.",
    )


def test_dee_authors_no_doctrine():
    """DEE decides IF a doctrine may change. It must never decide WHAT it becomes.

    The convenient move — and it is genuinely tempting — is to let the gate synthesize a
    new doctrine so it can close its own approval. That would let AUREA's identity change
    with NO AUTHOR BUT THE GATE ITSELF.

    Doctrine content comes from the collapse path: Nova hypotheses, DBE branches, a Spine
    request carrying a proposed form. When nothing supplies one, an eligible mutation must
    FERMENT — not be invented.

        A gate that fabricates the thing it is gating is not a gate.
    """
    import ast

    dee = H.repo_root() / "src" / "doctrine" / "dee.py"
    if H.is_empty(dee):
        pytest.skip("dee.py is a stub — this converts to a live check when it is authored")

    tree = H.parse(dee)
    violations = [
        H.Violation(dee, node.lineno,
                    "constructs a `Doctrine(...)` — DEE is authoring doctrine content")
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "Doctrine"
    ]

    assert not violations, H.fail_message(
        "RULING 5 — the gate authors nothing",
        violations,
        "DEE must receive a proposed form from the collapse path, or ferment. "
        "If no module yet authors doctrine candidates (Nova and DBE are stubs), then "
        "FERMENTING IS THE CORRECT BEHAVIOR — not a gap to fill by having the gate write "
        "its own answer.",
    )


def test_doctrine_spine_holds_no_store():
    """The Spine is the skeleton, not the scribe. It may read, orient, and REQUEST."""
    spine = H.repo_root() / "src" / "doctrine" / "doctrine_spine.py"
    if H.is_empty(spine):
        pytest.skip("doctrine_spine.py is a stub")

    tree = H.parse(spine)
    violations = [
        H.Violation(spine, lineno, detail)
        for lineno, detail in H.find_store_mutations(tree, "doctrines")
    ]
    violations += [
        H.Violation(spine, lineno, f"defines `{name}()` — mutation is SAE's, not the Spine's")
        for lineno, name in H.find_defs_matching(tree, ("mutate_doctrine",))
    ]

    assert not violations, H.fail_message(
        "RULING 5 — the Doctrine Spine writes nothing",
        violations,
        "Use `request_mutation()`. The Spine emits a request; DEE gates it; SAE executes it. "
        "This is exactly the method that was deleted on 2026-07-11 — do not reintroduce it.",
    )
