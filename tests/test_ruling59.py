"""
test_ruling59.py - THE DOCUMENTED SCOPE IS THE ENFORCED SCOPE (Ruling 59).

Manifest twenty-fourth addendum, 2026-08-01.

THE INCIDENT. `tests/conftest.py`'s autouse isolation fixture covers the
`tests/` subtree and ONLY that subtree. A bare `pytest` collected from the repo
root, which pulled in `scripts/` - demo scripts that EXECUTE AUREA AT IMPORT
TIME against real default paths. One such invocation wrote TWELVE files into
shared `data/runtime/`, including the runtime scar store and `sae_epoch.json`,
the Self-Mutation Ceiling's durable state (Rulings 34/51).

    The isolation contract was real and its SCOPE was a CONVENTION. It held
    exactly as long as everyone remembered to type the path.

That is the "discouraged, not unexecutable" shape CLAUDE.md section 3 exists
for - sitting underneath the suite that enforces the rest of the architecture.

THIS FILE IS THE STRUCTURAL ENFORCEMENT'S WITNESS. The `pytest.ini` proxy is
pinned BESIDE a behavioral collection witness, because a proxy plus a witness is
stronger than either alone (CLAUDE.md section 4's own note on Ruling 17).

COINS NOTHING: one config key, twelve deletions, four guards.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
SHARED_RUNTIME = REPO / "data" / "runtime"


# =====================================================================
# A. COLLECTION CANNOT LEAVE THE ISOLATED SUBTREE
# =====================================================================

def test_bare_collection_stays_inside_tests(tmp_path) -> None:
    """PIN 1 - THE BEHAVIORAL WITNESS, in a SUBPROCESS from ROOTDIR.

    **RED FIRST.** Against `97216e4` this produced SEVEN collection ERRORS from
    `scripts/`, and collection aborted before a single real test ran.

    A subprocess is not a convenience here: the running pytest has already
    resolved its own config and collected its own session, so the only honest
    way to ask "what does a bare `pytest` collect" is to run one.
    """
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
        encoding="utf-8", errors="replace")

    assert proc.returncode == 0, (
        f"bare `pytest` does not collect cleanly:\n{proc.stdout[-3000:]}")

    items = [line.strip() for line in proc.stdout.splitlines()
             if "::" in line and not line.startswith(" ")]
    assert items, "the collection produced no items at all"

    outside = [i for i in items if not i.replace("\\", "/").startswith("tests/")]
    assert outside == [], (
        f"{outside[:10]} were collected from OUTSIDE `tests/`. Only that "
        f"subtree is covered by the isolation fixture, so anything else "
        f"executes against real default store paths.")


def test_pytest_ini_pins_testpaths_to_tests() -> None:
    """PIN 2 - THE PROXY, beside the witness above.

    Ruling 17's discipline: a proxy is not a lesser test when the ruling is a
    fact about a FILE, and a proxy plus a runtime witness is stronger than
    either alone. This one fails loudly if someone deletes the key while the
    witness happens to stay green for an unrelated reason.
    """
    ini = REPO / "pytest.ini"
    assert ini.exists(), "pytest.ini is what makes the scope structural"

    body = ini.read_text(encoding="utf-8")
    lines = [l.strip() for l in body.splitlines()
             if l.strip() and not l.strip().startswith("#")]
    assert lines[0] == "[pytest]"
    assert "testpaths = tests" in lines, (
        f"`testpaths = tests` is the whole of res.1; found {lines}")


def test_the_config_stays_minimal() -> None:
    """ONE KEY, NOTHING SPECULATIVE. `addopts`, markers, or a coverage gate are
    each a SEPARATE decision - CI is deliberately minimal (CLAUDE.md section 4)
    and adding one is a ruling, not a convenience."""
    lines = [l.strip() for l in (REPO / "pytest.ini").read_text(encoding="utf-8")
             .splitlines() if l.strip() and not l.strip().startswith("#")]
    assert lines == ["[pytest]", "testpaths = tests"], (
        f"pytest.ini has grown beyond the one ruled key: {lines}")


# =====================================================================
# B. THE DEAD DEMOS ARE GONE
# =====================================================================

def test_no_test_shaped_scripts_remain() -> None:
    """PIN 4. **RED FIRST**: TWELVE `scripts/test_*.py` existed at `97216e4`.

    Deleted rather than renamed: every line of them misdescribes current APIs
    (`spine.add_doctrine`, `Scar(...)` without `name`, `CollapseResult.tags`),
    which is FALSE DOCUMENTATION IN EXECUTABLE FORM - Docket E's class. Git
    preserves all twelve at every commit up to their deletion, so nothing
    forensic is destroyed.
    """
    stragglers = sorted(p.name for p in SCRIPTS.glob("test_*.py"))
    assert stragglers == [], (
        f"{stragglers} are test-shaped files in `scripts/`. They are outside "
        f"the isolation fixture's reach; a test belongs in `tests/`.")


# =====================================================================
# C. IMPORT EXECUTES NOTHING
# =====================================================================

def _script_modules():
    return sorted(p for p in SCRIPTS.glob("*.py") if p.name != "__init__.py")


def test_importing_every_script_writes_nothing(tmp_path) -> None:
    """PIN 3 - THE IMPORT-INERTNESS WITNESS. **RED FIRST** via the demos.

    Runs in a SUBPROCESS so a real import happens (an already-imported module
    would be a no-op in-process), and asserts shared `data/runtime/` is absent
    BEFORE and AFTER. This stays meaningful forever: it is the guard against the
    NEXT script that runs work at module level.
    """
    assert not SHARED_RUNTIME.exists(), (
        "PRECONDITION: shared data/runtime/ must be absent before this test. "
        "Something already polluted it.")

    names = [p.stem for p in _script_modules()]
    program = (
        "import importlib\n"
        f"for name in {names!r}:\n"
        "    importlib.import_module('scripts.' + name)\n"
        "print('imported', len(" + repr(names) + "))\n"
    )
    proc = subprocess.run([sys.executable, "-B", "-c", program],
                          cwd=REPO, capture_output=True, text=True, timeout=600,
                          encoding="utf-8", errors="replace")

    assert proc.returncode == 0, (
        f"importing the scripts failed:\n{proc.stdout}\n{proc.stderr[-2000:]}")
    assert not SHARED_RUNTIME.exists(), (
        f"IMPORTING the scripts created {SHARED_RUNTIME} - a module is doing "
        f"work at import time. Move it under `if __name__ == \"__main__\":`.")


def test_every_script_is_structurally_inert_at_module_level() -> None:
    """The proxy beside that witness, and the one that localizes a failure.

    A module is inert iff its top level holds only the docstring, imports,
    definitions, constants, `sys.path` setup, and a `__main__` guard.

    `sys.path.insert` IS EXEMPT and the exemption is stated rather than
    assumed: the scripts need it BEFORE their `src` imports, it executes no
    AUREA and touches no store, and `scripts/soak.py` - which the ruling
    expects to pass as-is - has exactly that shape.
    """
    def is_guard(node):
        return (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__")

    def is_sys_path(node):
        if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)):
            return False
        func = node.value.func
        return (isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "path"
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "sys")

    offenders = []
    for path in _script_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                                 ast.AsyncFunctionDef, ast.ClassDef, ast.Assign,
                                 ast.AnnAssign)):
                continue
            if is_guard(node) or is_sys_path(node):
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue                                    # docstring
            offenders.append(f"{path.name}:{node.lineno} {type(node).__name__}")

    assert offenders == [], (
        f"{offenders} run at MODULE level. Importing that file executes it - "
        f"which is how a bare `pytest` wrote twelve files into shared "
        f"data/runtime/ (Ruling 59's incident).")


def test_the_inertness_scanner_actually_fires(tmp_path) -> None:
    """Ruling 32's answer to the vacuous-pin problem: feed the scanner the
    forbidden shape and a benign control, so a scan that has stopped scanning
    fails HERE rather than passing quietly forever."""
    offending = tmp_path / "bad.py"
    offending.write_text("import os\nprint('side effect')\n", encoding="utf-8")
    benign = tmp_path / "good.py"
    benign.write_text(
        '"""doc."""\nimport sys\nsys.path.insert(0, ".")\n'
        'def main():\n    print("x")\nif __name__ == "__main__":\n    main()\n',
        encoding="utf-8")

    def offenders_in(path):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        out = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                                 ast.ClassDef, ast.Assign)):
                continue
            if isinstance(node, ast.If):
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and getattr(node.value.func.value, "attr", None) == "path"):
                continue
            out.append(node.lineno)
        return out

    assert offenders_in(offending) == [2], "the scanner must see a bare call"
    assert offenders_in(benign) == [], "and must not flag the legitimate shape"
