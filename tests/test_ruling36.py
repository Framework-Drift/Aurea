"""
Ruling 36 - A FOSSIL WITH A LIVE SUCCESSOR IS METABOLISM, NOT COLLAPSE.

    Seed fossils are CONSTITUTION.
    Succeeded fossils are ANCESTRY.
    Only a fall WITHOUT succession is GROUND COLLAPSING.

WHAT THIS RULES. The Ruling 35 pass found `compass._north()` reading every
fossil as a live anchor collapse at pressure 1.0 -> GSR cascade -> total output
block, and narrowed it to exempt SEED fossils under a flag, correctly refusing
to decide the runtime half. Ruling 36 ratifies (A) that narrowing and rules (B)
the half left open.

WHY THE RUNTIME HALF GOES THIS WAY: `collapse -> scar -> doctrine -> identity`
means survived change produces CONTINUITY, and the codebase already encodes
succession - Rulings 18/24's shape is fossil + successor born under a NEW id
carrying the fallen id in `mutation_lineage`. A fossilization that produced a
live successor is the growth loop WORKING. Registering it as anchor collapse
would mean her FIRST SUCCESSFUL EVOLUTION permanently mutes her: the exact
inversion Ruling 34 closed for the ceiling - a guard pointed the wrong way -
reproduced in the compass.

A fossil with NO live successor is different IN KIND: something she stood on
fell and nothing grew in its place. That is what the trigger is for, and it is
RETAINED. **The trigger is AIMED, not narrowed away.**

SUCCESSION IS A RECORDED FACT, never an inferred one - `mutation_lineage` and
nothing else. A guessed succession would let a doctrine that merely RESEMBLES
the fallen one silence a real anchor collapse. Guarded structurally below, and
the guard is itself pinned (Ruling 32's precedent).
"""

from __future__ import annotations

import ast
from datetime import datetime

import pytest

from src.doctrine.codex import Codex
from src.expansion.sae import SAE, MutationClass
from src.identity.compass import CompassStabilityEngine
from src.utils.models import Doctrine
from tests.invariants import _ast as H
from tests.proof_support import minimal_proof


# =========================================================================
# HELPERS - a real Codex, a real SAE, real commits. No mocks in the path.
# =========================================================================

@pytest.fixture
def store(tmp_path):
    codex = Codex(filepath=str(tmp_path / "doctrines.json"))
    return codex, SAE(codex=codex)


def _budget(sae):
    """Restore the epoch budget through the LEGITIMATE path when it runs out.

    THE SELF-MUTATION CEILING IS CANON 3 AND IS NOT RAISED HERE. Several of
    these scenarios need more than three writes (a three-generation chain plus
    a fossilization is four), and there are exactly two ways to get them:
    construct the test SAE with a larger `ceiling=`, or close the epoch the way
    the architecture says an epoch closes. The first is editing the guard to
    fit the test - CLAUDE.md §5's shape even though the constant itself would
    be untouched - so this does the second.

    It works because `birth_doctrine` routes through `_touch`, so "scar-1" is
    genuinely in `touched_lineages` and the stabilization event is a REAL one
    rather than a nudge. Ruling 34's carry then discharges only that lineage.
    """
    if sae.epoch_count >= sae.ceiling:
        assert sae.stabilization_event("scar_fermentation", lineage="scar-1") is True, (
            "the test could not close the epoch through the legitimate path")


def _commit(codex, sae, doctrine_id, lineage=()):
    """Birth a live doctrine carrying an explicit mutation_lineage.

    Uses `birth_doctrine` rather than a bare `authorize` + `codex.commit`: it is
    the real counted-class path, and it records the touched lineage that
    `_budget` later settles against.
    """
    _budget(sae)
    doctrine = Doctrine(id=doctrine_id, name=doctrine_id, scar_links=["scar-1"],
                        mutation_lineage=list(lineage), created_at=datetime.now())
    sae.birth_doctrine(doctrine, "scar-1")
    return doctrine


def _fossilize(codex, sae, doctrine_id):
    _budget(sae)
    codex.fossilize(doctrine_id,
                    sae.authorize(MutationClass.MUTATE_DOCTRINE, "scar-1", doctrine_id),
                    reason="fell")


def _collapsed(codex):
    return CompassStabilityEngine(codex=codex)._north().collapsed


# =========================================================================
# PIN 1 - THE MIGRATED PIN (Ruling-14 precedent: old/new/why verbatim)
# =========================================================================

def test_an_UNSUCCESSORED_runtime_fossil_is_still_an_anchor_collapse(store):
    """MIGRATED FROM tests/test_ruling35.py. Recorded verbatim, both halves:

    OLD NAME: `test_a_runtime_fossil_IS_still_an_anchor_collapse`
    NEW NAME: `test_an_UNSUCCESSORED_runtime_fossil_is_still_an_anchor_collapse`

    OLD DOCSTRING, verbatim:
        "THE OTHER HALF, AND THE ONE THAT MATTERS MOST.

        DEFECT WATCHED: "fixing" the above by disabling anchor collapse. A
        doctrine that falls UNDER her is exactly the event the compass exists
        to catch, and a narrowing that swallowed it would be far worse than the
        bug it replaced - it would silently remove a safety trigger while
        looking like a bug fix."

    WHY IT MOVED: Ruling 36 ruled the runtime half this pin was holding open,
    so the pin moves WITH its ruling and gains a companion (pin 2 below). It is
    NOT weakened - it is made SPECIFIC. Its warning stays true verbatim, and
    Ruling 36's answer to it is that the trigger is AIMED, not narrowed away:
    every genuinely fallen-and-unreplaced anchor still fires.
    """
    codex, sae = store
    _commit(codex, sae, "D-live")
    _fossilize(codex, sae, "D-live")

    assert "D-live" in codex.fossils
    assert _collapsed(codex) == ["D-live"], (
        "a doctrine fossilized AT RUNTIME with NOTHING grown in its place no "
        "longer registers as an anchor collapse - the ruling aimed the trigger, "
        "it did not remove it")


# =========================================================================
# PIN 2 - THE COMPANION THIS RULING ARMS
# =========================================================================

def test_a_runtime_fossil_whose_successor_lives_is_not_a_collapse(store):
    """DEFECT WATCHED: her first successful evolution muting her permanently.

    This is the case the Ruling 35 pass could not decide. A fossil with a live
    successor is identity change that LEFT ANCESTRY - the growth loop working.
    """
    codex, sae = store
    _commit(codex, sae, "D-old")
    _fossilize(codex, sae, "D-old")
    assert _collapsed(codex) == ["D-old"], "precondition: it fires while unsuccessored"

    _commit(codex, sae, "D-new", lineage=["D-old"])

    assert _collapsed(codex) == [], (
        "a fossil with a LIVE successor still reads as anchor collapse - the "
        "growth loop is being punished for working")


def test_a_successor_that_does_not_name_the_fossil_does_not_silence_it(store):
    """The companion cannot be satisfied by any live doctrine existing.

    DEFECT WATCHED: `if self.codex.doctrines:` - "something is alive, so
    nothing collapsed". Succession is about THIS fossil, not about the store
    being non-empty.
    """
    codex, sae = store
    _commit(codex, sae, "D-old")
    _fossilize(codex, sae, "D-old")
    _commit(codex, sae, "D-unrelated", lineage=["D-someone-else"])

    assert _collapsed(codex) == ["D-old"], (
        "an unrelated live doctrine silenced a real anchor collapse")


def test_a_fossil_cannot_be_succeeded_by_another_fossil(store):
    """DEFECT WATCHED: reading succession out of the FOSSIL map too.

    Then a chain of fossils vouches for each other and a cascade of falls
    registers as nothing at all. Only a LIVE doctrine can succeed.
    """
    codex, sae = store
    _commit(codex, sae, "D-old")
    _commit(codex, sae, "D-mid", lineage=["D-old"])
    _fossilize(codex, sae, "D-old")
    _fossilize(codex, sae, "D-mid")

    assert sorted(_collapsed(codex)) == ["D-mid", "D-old"], (
        "a fossilized successor silenced its fossilized ancestor - fossils "
        "vouching for each other")


def test_a_codex_that_cannot_answer_still_fires_the_trigger():
    """The `getattr` fallback's DIRECTION, pinned.

    DEFECT WATCHED: defaulting to "succeeded" when the codex cannot answer the
    succession question. That silently suppresses a safety trigger on any
    duck-typed or partially-built store. An unanswerable question means she
    does not know that anything grew in its place - so the trigger FIRES.
    """
    class _CodexWithoutSuccession:
        fossils = {"D-gone": Doctrine(id="D-gone", name="gone",
                                      created_at=datetime.now())}

        def get_fossil(self, doctrine_id):
            return self.fossils.get(doctrine_id)

        def view(self):
            return {}

    north = CompassStabilityEngine(codex=_CodexWithoutSuccession())._north()
    assert north.collapsed == ["D-gone"], (
        "a codex that cannot answer the succession question silently "
        "suppressed the anchor-collapse trigger")


# =========================================================================
# PIN 3 - THE STANDING HALF (Ruling 36 A: the narrowing is RATIFIED)
# =========================================================================

def test_a_seed_fossil_never_registers():
    """Re-run against the REAL seed. `⊗ Doctrine-0` fell before she ever ran:
    constitution, not an event in her runtime."""
    codex = Codex()
    assert "⊗ Doctrine-0" in codex.fossils, "precondition: Ruling 35's routing"
    assert _collapsed(codex) == [], "the founding fossil reads as a live collapse"


# =========================================================================
# PIN 4 - THE RECOVERY SEQUENCE, AS ONE STORY
# =========================================================================

def test_fossilize_fires_then_succession_clears_it(store):
    """THE READ-TIME PROPERTY, END TO END - the ruling's own resolution text.

    Succession is read AT READ TIME: no caching, no event subscription,
    `_north()` recomputes from current store state on every call. That is what
    makes recovery legible IN THE SAME SURFACE that saw the fall, with zero new
    machinery.

    DEFECT WATCHED: caching the collapse set, or latching it on the
    fossilization event. Either makes the fall permanent and the recovery
    invisible - which is the stale-status-line shape inside a live sensor.
    """
    codex, sae = store
    _commit(codex, sae, "D-ground")

    assert _collapsed(codex) == [], "nothing has fallen yet"

    _fossilize(codex, sae, "D-ground")
    assert _collapsed(codex) == ["D-ground"], "the fall did not register"

    _commit(codex, sae, "D-ground::successor", lineage=["D-ground"])
    assert _collapsed(codex) == [], (
        "the compass did not clear after a successor was committed - the "
        "reading is latched or cached instead of computed at read time")


# =========================================================================
# PIN 5 - THE CHAIN CASE (direct containment is chain-robust)
# =========================================================================

def test_a_middle_generation_fossil_is_covered_by_its_grandchild(store):
    """LINEAGE ACCUMULATES, so DIRECT containment needs no transitive walk.

    `sae.py` builds a successor as
    `list(ancestor.mutation_lineage) + [ancestor.id]`, so a grandchild carries
    the whole chain: A -> B -> C leaves C's lineage == [A, B]. Fossilize B while
    C lives and B still reads as succeeded.

    THIS PIN IS THE WITNESS FOR THAT DATA PROPERTY. If the accumulation ever
    changes to record only the immediate parent, this goes RED - rather than
    the compass silently under-reporting a real collapse.
    """
    codex, sae = store
    _commit(codex, sae, "A")
    _commit(codex, sae, "B", lineage=["A"])
    _commit(codex, sae, "C", lineage=["A", "B"])

    assert codex.live_successors("A") == ["B", "C"]
    assert codex.live_successors("B") == ["C"]

    _fossilize(codex, sae, "B")

    assert _collapsed(codex) == [], (
        "the middle of a three-generation chain registered as collapse while "
        "its grandchild lives - direct containment stopped being chain-robust")
    assert codex.live_successors("B") == ["C"]


def test_lineage_still_accumulates_through_the_real_mutation_path(store):
    """The property above, asserted through SAE rather than hand-built lineage.

    DEFECT WATCHED: this file's helpers setting `mutation_lineage` by hand and
    thereby testing its own fixture instead of the engine.

    RULING 45 (2026-07-28), Ruling-14 precedent. Both calls gained a `proof`:

        OLD: sae.mutate_doctrine("gen-A", Doctrine(...), collapse_lineage="scar-1")
        NEW: the same call, plus `proof=minimal_proof(...)`.

    WHY: `proof` is REQUIRED and has no default - an implicit one would be a
    fabricated argument. NOT A WEAKENING: the assertion is unchanged, and it is
    still asserted THROUGH THE REAL MUTATION PATH, which is this test's whole
    subject. Adding a required argument to that path does not make the path less
    real - if anything the chain now carries its own lineage twice, once in
    `mutation_lineage` and once in each proof.
    """
    codex, sae = store
    _commit(codex, sae, "gen-A")
    sae.mutate_doctrine("gen-A", Doctrine(id="gen-B", name="B", created_at=datetime.now()),
                        collapse_lineage="scar-1",
                        proof=minimal_proof("chain-robustness probe, generation B",
                                            scar_lineage=("scar-1",),
                                            ancestor_id="gen-A"))
    sae.mutate_doctrine("gen-B", Doctrine(id="gen-C", name="C", created_at=datetime.now()),
                        collapse_lineage="scar-1",
                        proof=minimal_proof("chain-robustness probe, generation C",
                                            scar_lineage=("scar-1",),
                                            ancestor_id="gen-B"))

    assert codex.get("gen-C").mutation_lineage == ["gen-A", "gen-B"], (
        "SAE stopped accumulating lineage - direct containment is no longer "
        "chain-robust and the compass check needs a transitive walk")
    assert _collapsed(codex) == [], "a fully succeeded chain registered a collapse"


# =========================================================================
# PIN 6 - SUCCESSION IS A RECORDED FACT, NOT AN INFERRED ONE
# =========================================================================

FORBIDDEN_ATTRS = {"name", "description", "tca_tags"}
FORBIDDEN_CALLS = {"SequenceMatcher", "get_close_matches", "ratio",
                   "startswith", "endswith", "lower", "upper", "find",
                   "difflib", "similarity"}


def find_inference_in_succession(tree: ast.AST, func_name: str) -> list[tuple[int, str]]:
    """Anything in the succession check that is not a lineage lookup.

    A COINED SIMILARITY MEASURE NEEDS ONE OF THREE THINGS: a text attribute to
    compare, a fuzzy-match call, or a numeric cutoff. All three are refused, so
    the check can only ever read the RECORD.
    """
    found = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name != func_name:
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
                found.append((node.lineno, f"reads .{node.attr}"))
            if isinstance(node, ast.Call):
                name = (node.func.attr if isinstance(node.func, ast.Attribute)
                        else getattr(node.func, "id", ""))
                if name in FORBIDDEN_CALLS:
                    found.append((node.lineno, f"calls {name}()"))
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                    and not isinstance(node.value, bool):
                found.append((node.lineno, f"numeric constant {node.value!r}"))
    return found


def test_the_succession_check_reads_the_record_and_nothing_else():
    """SUCCESSION IS A RECORDED FACT.

    DEFECT WATCHED: `if fossil.name in live.name` or a difflib ratio over
    descriptions. A GUESSED succession lets a doctrine that merely RESEMBLES
    the fallen one silence a real anchor collapse - the false-resolution hazard
    EchoNet's abstaining intuition net exists to avoid, applied to a safety
    trigger. It is also §9 bar #5: a similarity score is a coined magnitude.
    """
    tree = H.parse(H.repo_root() / "src/doctrine/codex.py")
    violations = find_inference_in_succession(tree, "live_successors")

    assert not violations, (
        f"`Codex.live_successors` infers succession instead of reading it: "
        f"{violations}. It may read `mutation_lineage` and nothing else - no "
        "name matching, no similarity measure, no coined threshold.")


@pytest.mark.parametrize("body", [
    "def live_successors(self, d):\n    return [x for x in self.doctrines if x.name == d]\n",
    "def live_successors(self, d):\n"
    "    return [x for x in self.doctrines if SequenceMatcher(None, x, d).ratio() > 0.8]\n",
    "def live_successors(self, d):\n    return [x for x in self.doctrines if x.description]\n",
    "def live_successors(self, d):\n    return [x for x in self.doctrines if len(x) > 3]\n",
    "def live_successors(self, d):\n    return [x for x in self.doctrines if d.lower() in x]\n",
])
def test_the_inference_guard_actually_fires(body):
    """The guard is pinned (Ruling 32's precedent).

    It is green today for the honest reason - the check really does only read
    `mutation_lineage` - which is exactly how a scanner that looks for nothing
    hides.
    """
    assert find_inference_in_succession(ast.parse(body), "live_successors"), body


def test_the_inference_guard_passes_the_real_implementation_shape():
    """A guard that flagged the correct code would just get deleted."""
    benign = ("def live_successors(self, doctrine_id):\n"
              "    return sorted(k for k, d in self.doctrines.items()\n"
              "                  if doctrine_id in d.mutation_lineage)\n")
    assert find_inference_in_succession(ast.parse(benign), "live_successors") == []
