"""
STRUCTURAL GUARDS — the invariants that currently exist only as comments.

WHY THIS FILE EXISTS
--------------------
The modules built on 2026-07-11 carry their guarantees as comments. Several say things like:

    "Do not add a `_loosen`."
    "A gate that fabricates the thing it is gating is not a gate."
    "Corrupt input gets the FLOOR, not the ceiling."

Those are REQUESTS FOR RESTRAINT. And that same session produced hard evidence that
restraint fails — including from the agent enforcing the rules:

  · The scar path was SEVERED by a magic number (`pressure > 0.9`), making COLLAPSE
    structurally unreachable. The whole architecture ran and nothing left a mark on her.
  · The compass would have LOCKED HER OUTPUT PERMANENTLY the moment she first scarred,
    because drift was measured against a frozen birth-vector.
  · SBSRE's scar requests were being silently DROPPED by a `hasattr` guard on a method
    that did not exist.

None of those were caught by reading. All were caught by running.

AUREA's own architectural principle is the answer:

    THE WRONG PATH MUST BE UNEXECUTABLE, NOT MERELY DISCOURAGED.

An agent under task-completion pressure reads intentional non-termination as a hang, an
output lock as a bug, and a gate that refuses to resolve as an unfinished function. It will
"fix" them, confidently and fast. A comment cannot stop that. A failing test can.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.invariants import _ast as H


def _module(*parts: str) -> Path:
    return H.repo_root().joinpath("src", *parts)


def _tree_or_skip(path: Path, why: str):
    if H.is_empty(path):
        pytest.skip(f"{H.rel(path)} is a stub — converts to a live check when authored ({why})")
    return H.parse(path)


# =====================================================================
# SBSRE — the bound must only ever TIGHTEN
# =====================================================================

def test_sbsre_bound_can_only_shrink():
    """Ruling 4's termination proof rests on ONE property: `loop_limit` never increases.

    The loop guard is a non-increasing bound over a strictly increasing counter. That is the
    entire argument for why SBSRE halts. If any code path raises the limit — a `_loosen()`,
    an `+= 1`, a reset — the proof is void and the quiet grinder comes back: a high-scar
    contradiction with a steady compass and an unstrained identity trips NO reflex and
    recurses forever.

    The reflex net catches violence. It does not catch patience.
    """
    sbsre = _module("reflex", "sbsre.py")
    tree = _tree_or_skip(sbsre, "SBSRE loop bound")

    violations: list[H.Violation] = []

    for lineno, name in H.find_defs_matching(tree, ("loosen", "extend_limit", "raise_limit")):
        violations.append(
            H.Violation(sbsre, lineno, f"defines `{name}()` — the bound must only shrink")
        )

    for node in ast.walk(tree):
        # `thread.loop_limit += n`
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Attribute) \
                and node.target.attr == "loop_limit" and isinstance(node.op, ast.Add):
            violations.append(
                H.Violation(sbsre, node.lineno,
                            "INCREASES `loop_limit` (+=) — termination proof void")
            )
        # `x.loop_limit = <expr involving +>`
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Attribute) and tgt.attr == "loop_limit":
                    if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                        violations.append(
                            H.Violation(sbsre, node.lineno,
                                        "assigns an INCREASED `loop_limit` — termination proof void")
                        )

    assert not violations, H.fail_message(
        "RULING 4 — the SBSRE bound is monotonic (may only decrease)",
        violations,
        "PSI may SHORTEN the leash (`_tighten`). Nothing may lengthen it. If a contradiction "
        "needs more cycles than the clamp allows, the correct outcome is the ABORT REFLEX — "
        "halt, store the partial thread in CSA, suppress repeats. Carrying a contradiction "
        "to exhaustion and setting it down IS the designed behavior, not a failure to fix.",
    )


def test_sbsre_clamp_survives_corrupt_input():
    """Non-finite input must return the FLOOR, not the ceiling.

    Naive clamping returns the CEILING for NaN (`min(5, nan)` → 5). That is backwards: if
    AUREA cannot tell how heavy a contradiction is, she must not grant herself MORE time to
    grind on it. The uninformative case is the conservative case.
    """
    sbsre = _module("reflex", "sbsre.py")
    _tree_or_skip(sbsre, "SBSRE clamp")
    source = sbsre.read_text(encoding="utf-8")

    assert "isfinite" in source, H.fail_message(
        "RULING 4 — corrupt input gets the floor, not the ceiling",
        [H.Violation(sbsre, 1,
                     "no non-finite guard (`math.isfinite`) in the loop-limit computation")],
        "NaN/inf inputs must return FLOOR. Without the guard, naive clamping silently grants "
        "the MAXIMUM loop limit precisely when the system understands the contradiction least.",
    )


# =====================================================================
# CSE — the compass holds no private copy of the world
# =====================================================================

def test_compass_holds_no_anchor_store():
    """TCAML owns anchor state (Ruling 1). CSE DERIVES the anchors on every reading.

    A compass with a private cache can drift from the world it is supposed to measure — and
    a compass that lies is worse than no compass. This one cannot disagree with reality
    because it IS reality, read directionally.
    """
    compass = _module("identity", "compass.py")
    tree = _tree_or_skip(compass, "compass anchor state")

    violations: list[H.Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in targets:
                if isinstance(tgt, ast.Attribute) and tgt.attr in {"anchors", "anchor_state"}:
                    violations.append(
                        H.Violation(compass, node.lineno,
                                    f"assigns `self.{tgt.attr}` — CSE is caching anchor state")
                    )

    assert not violations, H.fail_message(
        "RULING 1 — CSE owns no anchor store",
        violations,
        "Derive the anchors from their owners on every read: NORTH from the Codex, SOUTH from "
        "Scar Logic Core, EAST from Nova, WEST from the Black Sphere. Request realignment "
        "through TCAML — never straighten the needle by hand.",
    )


# =====================================================================
# SAE — the ceiling counts THREE classes, and §10.G is not negotiable
# =====================================================================

def test_self_mutation_ceiling_counts_three_classes():
    """T4-01: {mutate_doctrine, mutate_reflex, module_generation}.

    Counting only the two `mutate_*` calls leaves module generation UNCAPPED: AUREA could not
    rewrite her doctrine faster than the ceiling, but could manufacture ORGANS without limit.
    """
    sae = _module("expansion", "sae.py")
    tree = _tree_or_skip(sae, "Self-Mutation Ceiling")

    members: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MutationClass":
            members = [
                t.id
                for stmt in node.body
                if isinstance(stmt, ast.Assign)
                for t in stmt.targets
                if isinstance(t, ast.Name)
            ]

    required = {"MUTATE_DOCTRINE", "MUTATE_REFLEX", "MODULE_GENERATION"}
    missing = required - set(members)

    assert not missing, H.fail_message(
        "T4-01 — the ceiling counts THREE classes",
        [H.Violation(sae, 1, f"MutationClass is missing: {sorted(missing)}")],
        "All three counted classes must decrement the same counter. Module generation is the "
        "one that was originally forgotten — the deepest recursion in the architecture, "
        "uncapped.",
    )


def test_10g_exclusions_present():
    """§10.G: the compass she steers by, the law she cannot revise, the place she puts what
    she cannot hold. Autogenesis may not manufacture a way around these, and neither may any
    mutation path."""
    sae = _module("expansion", "sae.py")
    _tree_or_skip(sae, "§10.G exclusions")
    source = sae.read_text(encoding="utf-8").lower()

    missing = [t for t in ("compass", "truth_law", "black_sphere") if t not in source]

    assert not missing, H.fail_message(
        "§10.G — hard exclusions from self-mutation",
        [H.Violation(sae, 1, f"exclusion targets absent from SAE: {missing}")],
        "SAE must refuse compass anchors, the Internal Truth Law, and the Black Sphere as "
        "mutation targets. These are not hers to revise.",
    )


# =====================================================================
# RB System — the behavior enum is CLOSED
# =====================================================================

def test_rb_behavior_enum_is_closed():
    """The RB `behavior_type` enum was CLOSED by ruling (2026-07-05, item #49).

    Silently adding a member is how a closed enum stops being closed. Extending it is an
    architect ruling, not an implementation detail — which is exactly why `cascade` is still
    an OPEN ITEM rather than a quietly-added member.
    """
    rb = _module("reflex", "rb_system.py")
    tree = _tree_or_skip(rb, "RB behavior enum")

    canon = {
        "SUPPRESS", "REROUTE", "SUSPEND", "DELAY", "SCAR_GRAFT", "OFFLOAD",
        "DEFER", "EXPIRE", "PREEMPT", "LOCK_GRANT", "LOCK_DENY",
    }

    members: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BehaviorType":
            members = {
                t.id
                for stmt in node.body
                if isinstance(stmt, ast.Assign)
                for t in stmt.targets
                if isinstance(t, ast.Name)
            }

    added = members - canon
    removed = canon - members

    violations = []
    if added:
        violations.append(
            H.Violation(rb, 1, f"UNRULED members added to the closed enum: {sorted(added)}")
        )
    if removed:
        violations.append(H.Violation(rb, 1, f"canon members removed: {sorted(removed)}"))

    assert not violations, H.fail_message(
        "RB System — behavior_type is a CLOSED enum",
        violations,
        "Adding a behavior type requires a manifest ruling and a Retired_Content_Archive "
        "entry. `cascade` is a known gap and is deliberately NOT mapped — do not close it "
        "here. Escalate to the architect.",
    )


# =====================================================================
# The orchestrator delegates. It does not decide.
# =====================================================================

def test_orchestrator_does_not_arbitrate_or_execute():
    """`aurea_core` wires the spine. It gates nothing, arbitrates nothing, writes nothing.

    An orchestrator is where 'just this once' logic accumulates, because it can see every
    module and is nobody's canonical owner.
    """
    core = _module("aurea_core.py")
    tree = _tree_or_skip(core, "orchestrator")

    violations: list[H.Violation] = []
    for lineno, name in H.find_defs_matching(tree, ("arbitrat",)):
        violations.append(
            H.Violation(core, lineno, f"defines `{name}()` — arbitration is RACM's")
        )
    for lineno, detail in H.find_store_mutations(tree, "scars"):
        violations.append(
            H.Violation(core, lineno, detail + " — the scar store is Scar Logic Core's")
        )
    for lineno, detail in H.find_store_mutations(tree, "doctrines"):
        violations.append(
            H.Violation(core, lineno, detail + " — the doctrine store is the Codex's")
        )

    assert not violations, H.fail_message(
        "Ruling 1 + Ruling 2 — the orchestrator delegates",
        violations,
        "Call the owner. AureaCore hands pressure to the Grid, contradictions to SBSRE, and "
        "scar pressure to DEE — and lets each of them decide what it is theirs to decide.",
    )
