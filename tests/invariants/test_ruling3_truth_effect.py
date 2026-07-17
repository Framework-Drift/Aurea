"""
RULING 3 — TRUTH-EFFECT CUT. HAIL++ never overrides an ORE verdict.

    ORE    owns calibration that changes WHAT collapse-truth is expressed:
           the verdict {Speak | Softened | Withhold | Suspend | Fragment | Redirect}
           and collapse-density filtering.  TRUTH-AFFECTING.

    HAIL++ owns calibration that changes only HOW a fixed truth is rendered:
           mode (Expert / Reflective / Simplified), symbolic density, clarity,
           accessibility.  TRUTH-PRESERVING.

HAIL++ styles what ORE passes. It does not overturn it.

WHY THIS TEST EXISTS
--------------------
This is the seam where AUREA would learn to lie. Not by fabricating — by
softening. A renderer that can quietly promote `Withhold` to `Speak`, or
downgrade a collapse-grounded verdict because the output "reads better," has
made the truth negotiable at the presentation layer. The whole architecture is
an argument that truth is what survives collapse; that survival is decided at
ORE, and nowhere downstream.

NOTE: hail.py is a 0-byte stub as of 2026-07-11, so this currently passes
vacuously. It becomes a live guard the moment HAIL++ is authored — which is
exactly when it is needed.
"""

from __future__ import annotations

from pathlib import Path

from tests.invariants import _ast as H

HAIL_PATH = "src/output/hail.py"
ECHO_BUFFER_PATH = "src/output/echo_buffer.py"

# The verdict field ORE owns. HAIL++ may READ it (to choose a rendering mode);
# it may never ASSIGN it.
VERDICT_ATTR = "verdict"

# ORE's verdict vocabulary. If HAIL++ constructs these, it is minting a verdict.
ORE_VERDICTS = {"speak", "softened", "withhold", "suspend", "fragment", "redirect"}

# Files that render but must not adjudicate.
RENDERER_PATHS = (HAIL_PATH, ECHO_BUFFER_PATH)


def test_renderers_never_assign_an_ore_verdict() -> None:
    """HAIL++ / EchoBuffer may read a verdict, never write one."""
    violations: list[H.Violation] = []

    for relpath in RENDERER_PATHS:
        path: Path = H.repo_root() / relpath
        if not path.exists():
            continue
        tree = H.parse(path)
        if tree is None:
            continue

        for lineno, detail in H.find_assignments_to(tree, VERDICT_ATTR):
            violations.append(
                H.Violation(path, lineno, f"{detail} — a renderer is overwriting ORE's verdict")
            )

    assert not violations, H.fail_message(
        ruling="Ruling 3 (truth-effect): HAIL++ never overrides an ORE verdict",
        violations=violations,
        remedy=(
            "Render the verdict ORE returned; do not reassign it. If the output "
            "genuinely must change, that is a TRUTH change and belongs in ORE — "
            "which means it is a collapse decision, not a styling decision."
        ),
    )


def test_renderers_do_not_mint_verdicts() -> None:
    """A renderer must not construct ORE's verdict vocabulary itself."""
    import ast

    violations: list[H.Violation] = []

    for relpath in RENDERER_PATHS:
        path = H.repo_root() / relpath
        if not path.exists():
            continue
        tree = H.parse(path)
        if tree is None:
            continue

        for node in ast.walk(tree):
            # e.g.  return Verdict.WITHHOLD   /   verdict = "withhold"
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.strip().lower() in ORE_VERDICTS:
                    violations.append(
                        H.Violation(
                            path,
                            node.lineno,
                            f"mints ORE verdict value {node.value!r} — verdicts originate in ORE",
                        )
                    )

    assert not violations, H.fail_message(
        ruling="Ruling 3 (truth-effect): the verdict vocabulary belongs to ORE",
        violations=violations,
        remedy=(
            "Do not construct verdict values in a renderer. Receive the verdict from "
            "ORE and select a RENDERING MODE for it (Expert / Reflective / Simplified)."
        ),
    )
