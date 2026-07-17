"""
_ast.py — shared source-scanning helpers for AUREA's invariant tests.

WHY STATIC ANALYSIS INSTEAD OF IMPORTS
--------------------------------------
Most of src/ is still empty stubs. Import-based tests would error on the stubs
and tell us nothing. But these invariants must hold *continuously* — from now
until the last stub is filled — so they scan source text instead. That works
whether a module is empty or finished, and it catches a violation the moment
someone writes it, anywhere in the tree.

This is the point: a markdown file cannot enforce an invariant. A test can.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator, NamedTuple

MUTATING_METHODS = {"append", "extend", "insert", "remove", "pop", "clear", "update"}


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "src").is_dir():
            return parent
    raise RuntimeError("Could not locate repo root (no src/ found above this file)")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root())).replace("\\", "/")
    except ValueError:
        return str(path)


def src_files() -> Iterator[Path]:
    """Every .py file under src/, skipping caches."""
    for path in sorted((repo_root() / "src").rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def parse(path: Path) -> ast.Module | None:
    """Empty stubs parse to an empty module. Unparseable files return None
    rather than exploding the whole suite."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return None


def is_empty(path: Path) -> bool:
    """True if the module is a stub (no code in it yet)."""
    tree = parse(path)
    return tree is None or not tree.body


class Violation(NamedTuple):
    path: Path
    line: int
    detail: str

    def __str__(self) -> str:
        return f"    {rel(self.path)}:{self.line} — {self.detail}"


def fail_message(ruling: str, violations: list[Violation], remedy: str) -> str:
    return "\n".join(
        [
            "",
            f"INVARIANT VIOLATED — {ruling}",
            "",
            *[str(v) for v in violations],
            "",
            f"  REMEDY: {remedy}",
            "",
            "  DO NOT weaken, skip, or delete this test to make it pass.",
            "  It encodes an architect ruling from the pre-code integration review",
            "  (see Aurea Build/integration_review_manifest.md, RULINGS LOG).",
            "  Fix the code, or escalate to the architect.",
            "",
        ]
    )


# --- detectors ----------------------------------------------------------


def _chain(node: ast.AST) -> list[str]:
    """Flatten a.b.c -> ['a','b','c']; [] for anything else."""
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if not isinstance(cur, ast.Name):
        return []
    parts.append(cur.id)
    return list(reversed(parts))


def find_store_mutations(tree: ast.Module, store_attr: str) -> Iterator[tuple[int, str]]:
    """Any statement that MUTATES the named collection.

    Catches:  x.scars.append(...) | x.scars = [...] | x.scars[0] = ... | del x.scars[0]

    Deliberately does NOT catch reads or iteration — other modules may read a
    store freely. Ruling 1 governs who *writes*.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            c = _chain(node.func)
            if len(c) >= 2 and c[-1] in MUTATING_METHODS and c[-2] == store_attr:
                yield node.lineno, f"mutates `{store_attr}` via .{c[-1]}()"

        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in targets:
                if isinstance(tgt, ast.Attribute) and tgt.attr == store_attr:
                    yield node.lineno, f"rebinds `{store_attr}`"
                if isinstance(tgt, ast.Subscript):
                    c = _chain(tgt.value)
                    if c and c[-1] == store_attr:
                        yield node.lineno, f"item-assigns into `{store_attr}`"

        if isinstance(node, ast.Delete):
            for tgt in node.targets:
                if isinstance(tgt, ast.Subscript):
                    c = _chain(tgt.value)
                    if c and c[-1] == store_attr:
                        yield node.lineno, f"deletes from `{store_attr}`"


def find_defs_matching(tree: ast.Module, needles: tuple[str, ...]) -> Iterator[tuple[int, str]]:
    """(lineno, name) for any function/method whose name contains a needle."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            low = node.name.lower()
            if any(n in low for n in needles):
                yield node.lineno, node.name


def find_assignments_to(tree: ast.Module, attr: str) -> Iterator[tuple[int, str]]:
    """(lineno, detail) for assignments to `<something>.attr` or bare `attr`."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in targets:
                if isinstance(tgt, ast.Attribute) and tgt.attr == attr:
                    yield node.lineno, f"assigns to `.{attr}`"
                if isinstance(tgt, ast.Name) and tgt.id == attr:
                    yield node.lineno, f"assigns to `{attr}`"


def defines_class(tree: ast.Module, name: str) -> bool:
    return any(
        isinstance(n, ast.ClassDef) and n.name == name for n in ast.walk(tree)
    )
